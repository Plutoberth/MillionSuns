import copy
from typing import Callable

import numpy_financial as npf

from objects.df import ElectricityUseDf
from hourly_simulation.parameters import Params, ELECTRICITY_COST, ELECTRICITY_SELLING_INCOME
from hourly_simulation.predict import predict_demand, predict_solar_production


def calculate_cost(electricity_use: ElectricityUseDf, params: Params, battery_capacity: float,
                   solar_panel_power_kw: float,
                   return_description=False):  # -> Optional[float, Tuple[float, Tuple[Any]]]:
    """
    Calculates the cost of  electricity_use

    :param params: namedtuple simulation params
    :param solar_panel_power_kw: int power of panel Kwh
    :param battery_capacity: float capacity of batteries in Kwh
    :param electricity_use: pd.DataFrame(columns=['HourOfYear', 'GasUsage', 'SolarUsage', 'StoredUsage', 'SolarStored',
        'SolarLost'])
    :return: float cost of the given electricity usage
    """
    # find relevant hours
    hours_paid_in_year = ELECTRICITY_COST.df[ELECTRICITY_COST.HourOfYear] == electricity_use.df[
        electricity_use.HourOfYear]
    # extract gas buying price per hour
    gas_cost_per_hour = ELECTRICITY_COST.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    # extract gas selling price cost per hour
    selling_income_per_hour = ELECTRICITY_SELLING_INCOME.df.loc[hours_paid_in_year, ELECTRICITY_COST.Cost]
    # calculate gas usage price
    gas_usage_cost = electricity_use.df[electricity_use.GasUsage].to_numpy().dot(gas_cost_per_hour.to_numpy())
    # calculate gas stored price
    gas_stored_cost = electricity_use.df[electricity_use.GasStored].to_numpy().dot(gas_cost_per_hour.to_numpy())
    total_gas_cost = gas_usage_cost + gas_stored_cost / params.BATTERY_EFFICIENCY
    # calculate solar selling income
    immediate_selling_income = electricity_use.df[electricity_use.SolarSold].to_numpy().dot(
        selling_income_per_hour.to_numpy())
    # calculate stored selling income
    battery_selling_income = electricity_use.df[electricity_use.StoredSold].to_numpy().dot(
        selling_income_per_hour.to_numpy())
    total_selling_income = immediate_selling_income + battery_selling_income
    # calculate PV opex and capex
    total_solar_opex = solar_panel_power_kw * params.PV_OPEX
    total_solar_capex = solar_panel_power_kw * params.PV_CAPEX / params.FACILITY_LIFE_SPAN
    # calculate batteries opex and capex
    total_battery_opex = battery_capacity * params.BATTERY_OPEX
    total_battery_capex = battery_capacity * params.BATTERY_CAPEX / params.FACILITY_LIFE_SPAN
    # sum opex and capex
    total_init_capex = total_battery_capex + total_solar_capex
    total_opex = total_solar_opex + total_battery_opex
    # battery_replacement_cost
    future_battery_capex = params.BATTERY_ADDED_FOR_REPLACEMENT * battery_capacity * params.BATTERY_FUTURE_CAPEX / params.FACILITY_LIFE_SPAN
    # capital expenses due to loans
    total_loan = total_init_capex * params.FACILITY_LIFE_SPAN * params.LOAN_SIZE
    capital_expenses = (-1 * npf.pmt(rate=params.LOAN_INTEREST_RATE, nper=params.LOAN_LENGTH,
                                     pv=total_loan) * params.LOAN_LENGTH - total_loan) / params.FACILITY_LIFE_SPAN
    # entrepreneur profit
    total_equity = total_init_capex * params.FACILITY_LIFE_SPAN * (1 - params.LOAN_SIZE)
    entrepreneur_profit = (-1 * npf.pmt(rate=params.ENTREPRENEUR_PROFIT, nper=params.FACILITY_LIFE_SPAN,
                                        pv=total_equity) * params.FACILITY_LIFE_SPAN - total_equity) / params.FACILITY_LIFE_SPAN
    # sum the cost
    total_cost = total_gas_cost + total_init_capex + total_opex + future_battery_capex - total_selling_income + \
                 capital_expenses + entrepreneur_profit
    if return_description:
        return total_cost, ((total_cost, total_gas_cost, total_solar_capex, total_battery_capex,
                             future_battery_capex, total_solar_opex, total_battery_opex,
                             capital_expenses, entrepreneur_profit, total_selling_income,))
    return total_cost
