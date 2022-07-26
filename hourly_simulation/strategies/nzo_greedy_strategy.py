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
    df["net_demand"] = (df["demand"] - df["fixed_gen"]).clip(lower=0)
    df["fixed_over_demand"] = (df["demand"] - df["fixed_gen"]).clip(upper=0) * -1

    # TODO: assuming charging starts at 50%, probably OK

    battery = Battery(storage_capacity_kwh, storage_capacity_kwh * 0.5, storage_charge_rate,
                      storage_efficiency)

    empty_ndarray = np.zeros(len(df), dtype="float")
    variable_gen_profile_np = {k: empty_ndarray.copy() for k in VARIABLE_ENERGY_SOURCES}
    other_output_np = {k: empty_ndarray.copy() for k in [FIXED_CURTAILED, BATTERY_STATE]}
    fixed_energy_usage_ratio = np.ones(len(df), dtype="float")

    # TODO: this can probably be replaced with more broadcasting operations
    for hour in df.itertuples():
        hour_index = hour.Index
        # getting inputs
        net_demand = hour.net_demand
        storage_usage = 0

        if net_demand == 0:
            fixed_over_demand = hour.fixed_over_demand
            fixed_gen = hour.fixed_gen

            storage_fixed_charge = battery.try_charge(fixed_over_demand)
            # because charging is negative production
            storage_usage = -storage_fixed_charge

            fixed_energy_curtailed = fixed_over_demand - storage_fixed_charge
            fixed_used = fixed_gen - fixed_energy_curtailed

            # to avoid div by zero
            if fixed_gen and fixed_used != fixed_gen:
                fixed_energy_usage_ratio[hour_index] = fixed_used / fixed_gen
                other_output_np[FIXED_CURTAILED][hour_index] = fixed_energy_curtailed
        else:
            storage_usage = battery.try_discharge(net_demand)

            if storage_usage != net_demand:
                variable_gen_profile_np[EnergySource.GAS][hour_index] = net_demand - storage_usage

        # setting outputs
        variable_gen_profile_np[EnergySource.STORAGE][hour_index] = storage_usage
        other_output_np[BATTERY_STATE][hour_index] = battery.get_energy_kwh()


    fixed_gen_actual = fixed_production.multiply(fixed_production, axis=0)
    variable_gen_profile = pd.DataFrame(variable_gen_profile_np)

    gen_profile = variable_gen_profile.join(fixed_gen_actual)

    other_output = pd.DataFrame(other_output_np)
    return gen_profile, other_output
