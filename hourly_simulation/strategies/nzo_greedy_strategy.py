import pandas as pd
import numpy as np

from .battery import Battery
from common import EnergySource, VARIABLE_ENERGY_SOURCES, SimMiscFields

__all__ = [
    "nzo_strategy"
]


def nzo_strategy(demand: pd.Series,
                 fixed_production: pd.DataFrame,
                 storage_capacity_kwh: float,
                 storage_efficiency: float,
                 storage_charge_rate: float,
                 ) -> pd.DataFrame:
    """
    :param demand: A series of demand values, in KwH, for every hour in the year.
    :param fixed_production: A pd.DataFrame[EnergySourceType, float]
    :param storage_capacity_kwh: the battery capacity, in KwH.
    :param variable_source: the "free" variable in the equation.

    :return: pd.DataFrame[EnergySourceType, float] of energy sources throughout the day, and another dataframe
             of other values.

    net demand = demand after subtracting fixed sources

    Strategy Goals:
    1. Use the least gas energy possible.

    Charging:
    1. Charge using remaining energy from fixed sources
    TODO: 2. If the battery is not full, and we're below the average net demand, charge using gas

    Discharging:
    Discharge as much as possible to meet demand.

    TODO: If we're above the average net demand, discharge according to a ratio that minimizes peak gas usage.
          For example, choose to discharge only 10MwH for two hours and then use 10MwH of gas on each hour,
          instead of discharging 20MwH on the first hour and then using 20MwH of gas on the next hour.
    """

    df = pd.DataFrame()
    df["demand"] = demand
    df["fixed_gen"] = fixed_production.sum(axis=1)
    df["net_demand"] = (df["demand"] - df["fixed_gen"]).clip(lower=0)
    df["fixed_over_demand"] = (df["demand"] - df["fixed_gen"]).clip(upper=0) * -1

    # TODO: assuming charging starts at 50%, probably OK

    battery = Battery(storage_capacity_kwh, storage_capacity_kwh * 0.5, storage_charge_rate,
                      storage_efficiency)

    zero_ndarray = np.zeros(len(df), dtype="float")
    variable_gen_profile_np = {k: zero_ndarray.copy() for k in VARIABLE_ENERGY_SOURCES}

    other_output_np = {k: zero_ndarray.copy() for k in SimMiscFields}
    other_output_np[SimMiscFields.DEMAND] = demand.to_numpy()
    other_output_np[SimMiscFields.NET_DEMAND] = df["net_demand"].to_numpy()

    fixed_energy_usage_ratio = np.ones(len(df), dtype="float")

    solar_prod_np = fixed_production[EnergySource.SOLAR].to_numpy()

    # TODO: this can probably be replaced with more broadcasting operations
    for hour in df.itertuples():
        hour_index = hour.Index
        # getting inputs
        demand = hour.demand
        net_demand = hour.net_demand
        fixed_gen = hour.fixed_gen

        if net_demand == 0:
            fixed_over_demand = hour.fixed_over_demand
            assert fixed_over_demand >= 0

            storage_fixed_charge = battery.try_charge(fixed_over_demand)
            assert storage_fixed_charge >= 0

            fixed_energy_curtailed = fixed_over_demand - storage_fixed_charge
            fixed_used = fixed_gen - fixed_energy_curtailed

            # TODO: this needs to be split among fixed energy sources, for when we integrate wind
            other_output_np[SimMiscFields.STORAGE_SOLAR_CHARGE][hour_index] = storage_fixed_charge

            # to avoid div by zero
            if fixed_gen and fixed_used != fixed_gen:
                fixed_energy_usage_ratio[hour_index] = fixed_used / fixed_gen
                other_output_np[SimMiscFields.CURTAILED_ENERGY][hour_index] = fixed_energy_curtailed
        else:
            storage_discharge = battery.try_discharge(net_demand)
            variable_gen_profile_np[EnergySource.STORAGE][hour_index] = storage_discharge

            if storage_discharge != net_demand:
                variable_gen_profile_np[EnergySource.GAS][hour_index] = net_demand - storage_discharge

        # setting outputs
        other_output_np[SimMiscFields.BATTERY_STATE][hour_index] = battery.get_energy_kwh()
        other_output_np[SimMiscFields.SOLAR_USAGE][hour_index] = min(
            demand,
            solar_prod_np[hour_index] * fixed_energy_usage_ratio[hour_index]
        )


    # TODO: this needs to be changed to reflect actual gas usage when we use gas for storage
    other_output_np[SimMiscFields.GAS_USAGE] = variable_gen_profile_np[EnergySource.GAS].copy()

    fixed_gen_actual = fixed_production.multiply(fixed_energy_usage_ratio, axis=0)
    variable_gen_profile = pd.DataFrame(variable_gen_profile_np)

    gen_profile = variable_gen_profile.join(fixed_gen_actual)

    other_output = pd.DataFrame(other_output_np)

    # TODO: fix this when wind is added
    zeroes_added = pd.DataFrame({
        EnergySource.WIND: zero_ndarray,
        }
    )

    out_df = gen_profile.join(other_output).join(zeroes_added)

    return out_df
