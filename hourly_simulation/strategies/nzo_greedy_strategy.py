from enum import Enum

import pandas as pd
import numpy as np
from pandas import DataFrame

from .battery import Battery
from enums import EnergySource, VARIABLE_ENERGY_SOURCES

__all__ = [
    "BATTERY_STATE",
    "FIXED_CURTAILED",
    "nzo_strategy"
]


BATTERY_STATE = "battery_state"
FIXED_CURTAILED = "fixed_curtailed"


def nzo_strategy(demand: pd.Series,
                 fixed_production: pd.DataFrame,
                 storage_capacity_kwh: float,
                 storage_efficiency: float,
                 storage_charge_rate: float,
                 ) -> tuple[DataFrame, DataFrame]:
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
    # TODO: this can be less ugly
    df["net_demand"] = (df["demand"] - df["fixed_gen"]).apply(lambda x: max(0, x))
    df["fixed_over_demand"] = (df["demand"] - df["fixed_gen"]).apply(lambda x: min(0, x) * -1)

    # TODO: assuming charging starts at 50%, probably OK

    battery = Battery(storage_capacity_kwh, storage_capacity_kwh * 0.5, storage_charge_rate,
                      storage_efficiency)

    fixed_gen_actual = fixed_production.copy()

    empty_ndarray = np.empty(len(df), dtype="float")
    variable_gen_profile_np = {k: empty_ndarray.copy() for k in VARIABLE_ENERGY_SOURCES}
    other_output_np = {k: empty_ndarray.copy() for k in [FIXED_CURTAILED, BATTERY_STATE]}

    # TODO: this can probably be replaced with more broadcasting operations
    for hour in df.itertuples():
        hour_index = hour.Index
        # getting inputs
        net_demand = hour.net_demand
        gas_prod = 0
        fixed_energy_curtailed = 0
        fixed_used = hour.fixed_gen
        storage_usage = 0

        if net_demand == 0:
            fixed_over_demand = hour.fixed_over_demand
            storage_fixed_charge = battery.try_charge(fixed_over_demand)

            fixed_energy_curtailed = fixed_over_demand - storage_fixed_charge
            fixed_used -= fixed_energy_curtailed

        else:
            storage_usage = battery.try_discharge(net_demand)

            if storage_usage != net_demand:
                gas_prod += net_demand - storage_usage

        # to avoid div by zero
        if hour.fixed_gen:
            fixed_gen_actual.loc[hour_index] *= fixed_used / hour.fixed_gen
        # setting outputs
        variable_gen_profile_np[EnergySource.GAS][hour_index] = gas_prod
        variable_gen_profile_np[EnergySource.STORAGE][hour_index] = storage_usage
        other_output_np[FIXED_CURTAILED][hour_index] = fixed_energy_curtailed
        other_output_np[BATTERY_STATE][hour_index] = battery.get_energy_kwh()

    variable_gen_profile = pd.DataFrame(variable_gen_profile_np)
    gen_profile = variable_gen_profile.join(fixed_gen_actual)

    other_output = pd.DataFrame(other_output_np)
    return gen_profile, other_output
