from enum import Enum

import pandas as pd

from objects.df import EnergySeries
from dataclasses import dataclass

"""
Plan:
Receive a list

It probably makes sense to have an object for 
Have an object that specifies 
"""


class EnergySourceType(Enum):
    SOLAR = "SOLAR"
    WIND = "WIND"
    GAS = "GAS"
    COAL = "COAL"


@dataclass(frozen=True)
class StrategyParams:
    # The C-value of the battery. Max charge/discharge rate per hour.
    BATTERY_CHARGE_RATE: float = 0.25
    # (battery output energy) / (battery input energy)
    BATTERY_EFFICIENCY: float = 0.87
    # TODO: the fraction of the battery's capacity that can be used - probably unimportant
    # and can be computed before sending to `nzo_strategy`.


def nzo_strategy(demand: EnergySeries,
                 fixed_production: pd.DataFrame,
                 storage_capacity_kwh: float,
                 params: StrategyParams,
                 ):
    """
    :param demand: A series of demand values, in KwH, for every hour in the year.
    :param fixed_production: A pd.DataFrame[EnergySourceType, EnergySeries]
    :param storage_capacity_kwh: the battery capacity, in KwH.
    :param variable_source: the "free" variable in the equation.

    net demand = demand after subtracting fixed sources

    Strategy Goals:
    1. Use the least gas energy possible.
    2. TODO Later: Flatten the peak usage of gas energy, to reduce the maximum needed installed capacity.

    Charging:
    1. Charge using remaining energy from fixed sources
    2. If the battery is not full, and we're below the average net demand, charge using gas (#TODO: how much?)

    Discharging:
    If we're above the average net demand, discharge according to a ratio that minimizes peak gas usage.
    For example, choose to discharge only 10MwH for two hours and then use 10MwH of gas on each hour,
    instead of discharging 20MwH on the first hour and then using 20MwH of gas on the next hour.
    """

    df = pd.DataFrame()
    df["demand"] = demand
    df["fixed_gen"] = fixed_production.sum(axis=1)
    # TODO: this can surely be less ugly
    df["net_demand"] = (df["demand"] - df["fixed_gen"]).apply(lambda x: max(0, x))
    df["fixed_over_demand"] = (df["demand"] - df["fixed_gen"]).apply(lambda x: min(0, x) * -1)
    df["day"] = df.apply(lambda row: row.name // 24, axis=1)
    df["hour_in_day"] = df.apply(lambda row: row.name % 24, axis=1)

    # TODO: assuming charging starts at 50%, probably ok?
    storage_state_kwh = 0.5 * storage_capacity_kwh
    # TODO: this can probably be replaced with groupby and broadcasting operations
    for _, day in df.groupby("day"):
        assert len(day) == 24
        total_demand = day["demand"].sum()
        average_demand = total_demand / len(day["demand"])
        total_net = day["net_demand"].sum()
        average_net = total_net / len(day["net_demand"])
        # TODO: this can surely be less ugly
        over_avg_demand_sum = day[day["demand"] > average_demand]["demand"].apply(lambda x: x - average_demand).sum()
        over_avg_net_sum = day[day["net_demand"] > average_net]["net_demand"].apply(lambda x: x - average_net).sum()

        # TODO: don't we only need to reduce the net demand, and not the total demand?
        #       we don't care about high demand, only high demand that requires gas usage...
        storage_peak_demand_reduction_ratio = min(1, storage_capacity_kwh / over_avg_demand_sum)
        # after clearing the
        storage_after_clearing_avg_demand = storage_capacity_kwh - over_avg_demand_sum
        storage_peak_net_demand_reduction_ratio = min(1,
                                                      storage_after_clearing_avg_demand / (over_avg_net_sum - over_avg_demand_sum))
        # TODO: add this
        # storage_net_demand_reduction_ratio

        # fixed_over_gen = min(0, -1 * total_unmet)
        # expected_storage_with_fixed_charging = min(storage_capacity_kwh, storage_state_kwh + fixed_over_gen)

        def get_amount_left_to_charge(curr):
            return (storage_capacity_kwh - curr) / params.BATTERY_EFFICIENCY

        # TODO: eliminate this or use itertuples
        for index, hour in df.iterrows():
            net_demand_over_avg_daily = max(0, hour["net_demand"] - average_net)
            demand_over_avg_daily = max(0, hour["demand"] - average_demand)


            # first charge with fixed sources
            storage_fixed_charge = min(hour["fixed_over_demand"],
                                       get_amount_left_to_charge(storage_state_kwh))
            storage_state_kwh += storage_fixed_charge * params.BATTERY_EFFICIENCY

            # todo: what the heck is leftToChargeFromGas - is it needed?
            storage_gas_charge = min(

                net_demand_over_avg_daily,
                get_amount_left_to_charge(storage_state_kwh),
            )

            storage_state_kwh += storage_gas_charge * params.BATTERY_EFFICIENCY

            # now calculate how much we want to discharge the batteries
            # TODO: this forumula isn't complete. complete it.
            storage_discharge = min(
                storage_peak_demand_reduction_ratio * demand_over_avg_daily +
                storage_peak_net_demand_reduction_ratio * net_demand_over_avg_daily,
                # TODO: add day.storagePeakDemandReduction formula
                hour["net_demand"],
                storage_state_kwh,
                storage_capacity_kwh * params.BATTERY_CHARGE_RATE
            )

            # TODO: handle cases where storageDischarge and storageCharge happen in the same hour

            storage_state_kwh -= storage_discharge

            gas_gen = hour["net_demand"] - storage_discharge + storage_gas_charge
            print(gas_gen, storage_state_kwh, storage_discharge)
            assert gas_gen >= 0

            # TODO: add calculations for the rest of the statistic values - curtailed energy, fixed usage, gas usage, etc
            # TODO: record storage state at end
            # curtailed_energy = hour["fixed_over_demand"] - storage_fixed_charge
            #
            # if curtailed_energy > 0:
            #     # if we curtailed energy we could've charged less using gas
            #     assert gas_gen == 0
            #
            # fixed_used = hour
