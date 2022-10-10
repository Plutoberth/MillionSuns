import pandas as pd
import numpy as np

from .battery import Battery
from common import EnergySource, VARIABLE_ENERGY_SOURCES, SimOutFields, FIXED_ENERGY_SOURCES, SimUsageFields

__all__ = [
    "nzo_strategy"
]


def nzo_strategy(demand: pd.Series,
                 fixed_production: pd.DataFrame,
                 storage_capacity_kwh: float,
                 storage_efficiency: float,
                 storage_charge_rate: float,
                 ) -> pd.DataFrame:
    sums_df = pd.DataFrame()
    sums_df["demand"] = demand
    sums_df["fixed_gen"] = fixed_production.sum(axis=1)
    sums_df["net_demand"] = (sums_df["demand"] - sums_df["fixed_gen"]).clip(lower=0)
    sums_df["fixed_over_demand"] = (sums_df["fixed_gen"] - sums_df["demand"]).clip(lower=0)

    out_misc, variable_gen = nzo_strategy_sim(demand, sums_df, storage_capacity_kwh, storage_efficiency,
                                              storage_charge_rate)
    res = postprocess(out_misc, variable_gen, sums_df, fixed_production)
    return res


def nzo_strategy_sim(demand: pd.Series,
                     sums_df: pd.DataFrame,
                     storage_capacity_kwh: float,
                     storage_efficiency: float,
                     storage_charge_rate: float,
                     ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    :param demand: A series of demand values, in KwH, for every hour in the year.
    :param storage_capacity_kwh: the battery capacity, in KwH.

    :return: pd.DataFrame[EnergySource, float] of variable energy sources, and another dataframe
             of misc values like battery state.

    Strategy Goals:
    1. Use the least gas energy possible.
    TODO: 2. Minimize the peak gas energy used, to minimize installed capacity.

    Strategy:
    If fixed sources fulfill demand:
        Charge storage using the remaining energy from fixed sources.
    Otherwise:
        Discharge as much as possible, and if that isn't enough, fulfill demand using gas.

    TODO: If the battery is not full, and we're below the average net demand, charge using gas.

    TODO: If we're above the average net demand, discharge according to a ratio that minimizes peak gas usage.
          For example, choose to discharge only 10MwH for two hours and then use 10MwH of gas on each hour,
          instead of discharging 20MwH on the first hour and then using 20MwH of gas on the next hour.
    """

    battery = Battery(storage_capacity_kwh, 0, storage_charge_rate,
                      storage_efficiency)

    zero_ndarray = np.zeros(len(sums_df), dtype="float")
    variable_gen_np = {k: zero_ndarray.copy() for k in VARIABLE_ENERGY_SOURCES}

    out_np = {k: zero_ndarray.copy() for k in SimOutFields}
    out_np[SimOutFields.DEMAND] = demand.to_numpy()
    out_np[SimOutFields.NET_DEMAND] = sums_df["net_demand"].to_numpy()

    for hour in sums_df.itertuples():
        hour_index = hour.Index
        net_demand = hour.net_demand

        if net_demand == 0:
            fixed_over_demand = hour.fixed_over_demand
            assert fixed_over_demand >= 0

            storage_fixed_charge = battery.try_charge(fixed_over_demand)
            assert storage_fixed_charge >= 0

            # TODO: this needs to be split among fixed energy sources, for when we integrate wind
            out_np[SimOutFields.FIXED_STORAGE_CHARGE][hour_index] = storage_fixed_charge
        else:
            storage_discharge = battery.try_discharge(net_demand)
            variable_gen_np[SimUsageFields.STORAGE][hour_index] = storage_discharge

            net_after_storage = net_demand - storage_discharge

            if net_after_storage != 0:
                variable_gen_np[SimUsageFields.GAS][hour_index] = net_after_storage

        out_np[SimOutFields.BATTERY_STATE][hour_index] = battery.get_energy_kwh()

    out = pd.DataFrame(out_np)
    variable_gen = pd.DataFrame(variable_gen_np)

    return out, variable_gen


def postprocess(out: pd.DataFrame, variable_gen: pd.DataFrame, df: pd.DataFrame, fixed_production: pd.DataFrame):
    """
    Receives the result of the simulation, and performs the required bookkeeping to decide what is used for
    storage, what is curatiled, etc.
    """
    out[SimOutFields.CURTAILED_ENERGY] = df["fixed_over_demand"] \
                                         - out[SimOutFields.FIXED_STORAGE_CHARGE]

    zero_ndarray = np.zeros(len(df), dtype="float")

    fixed_waste_rate = out[SimOutFields.CURTAILED_ENERGY] / df["fixed_gen"]
    fixed_waste_rate.replace([np.inf, -np.inf], 0, inplace=True)

    fixed_storage_rate = out[SimOutFields.FIXED_STORAGE_CHARGE] / \
                         df["fixed_gen"]
    fixed_storage_rate.replace([np.inf, -np.inf], 0, inplace=True)

    fixed_demand_rate = 1 - fixed_waste_rate - fixed_storage_rate

    # TODO: fix this when wind is added
    zeroes_added = pd.DataFrame({
        EnergySource.WIND: zero_ndarray,
    }
    )

    # TODO: don't scale coal here; it'll reduce varopex which is inaccurate
    fixed_gen_actual = fixed_production.multiply(fixed_demand_rate, axis=0)

    variable_gen_profile = pd.DataFrame(variable_gen)
    all_gen_profile = variable_gen_profile.join(fixed_gen_actual)
    out_df = all_gen_profile.join(out).join(zeroes_added)

    return out_df
