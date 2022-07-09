import csv
from collections import namedtuple
from typing import Dict, Iterable, Tuple

import pandas as pd

from objects.df import CostElectricityDf
from hourly_simulation.shift_day_in_year import shift_day_of_year

# Non changing Params
PARAMS_PATH = "data/parameters.csv"


def mw_to_kw(value_str, unit, as_mw):
    value = float(value_str)

    if not as_mw:
        if "/mw" in unit.lower():
            value = value / 1000
        elif "mw" in unit.lower():
            value = value * 1000
    return value


def process_simulation_params(lines: Iterable[Tuple[str, str, str]], with_units, as_mw) -> Dict:
    params = {}

    for row in lines:
        if with_units:
            params[row[0].strip()] = (mw_to_kw(row[1], row[2], as_mw), row[2])
        else:
            params[row[0].strip()] = mw_to_kw(row[1], row[2], as_mw)

    return params


def get_simulation_parameters(csv_path, with_units=False, as_mw=False) -> Dict:
    """
    Retrieves the parameters from csv_path as dictionary

    :param csv_path: str path of parameters_backup.csv file
    :param with_units: boolean should return the units (third column) as well?
    :param as_mw: whether to return as Mw or not
    :return: if with_units: dictionary(str -> float). else: dictionary(str -> (float, str))
    """
    with open(csv_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        return process_simulation_params(reader, with_units, as_mw)


__simulation_params_dict = get_simulation_parameters(PARAMS_PATH)
Params = namedtuple('Params', __simulation_params_dict.keys())
simulation_params = Params(**__simulation_params_dict)

# Electricity

ELECTRICITY_COST_PATH = 'data/electricity_cost_gaussian.csv'
ELECTRICITY_COST_BINARY_PATH = 'data/shifted_electricity_cost_binary.csv'
ELECTRICITY_SELLING_INCOME_PATH = 'data/electricity_sell_gaussian.csv'
ELECTRICITY_COST = CostElectricityDf(pd.read_csv(ELECTRICITY_COST_PATH, index_col=0))
ELECTRICITY_COST.df[ELECTRICITY_COST.Cost] = shift_day_of_year(ELECTRICITY_COST.df[ELECTRICITY_COST.Cost],
                                                               ELECTRICITY_COST.YearOfCost)
ELECTRICITY_SELLING_INCOME = CostElectricityDf(pd.read_csv(ELECTRICITY_SELLING_INCOME_PATH, index_col=0))  # ILS per Kw
ELECTRICITY_SELLING_INCOME.df[ELECTRICITY_SELLING_INCOME.Cost] = shift_day_of_year(
    ELECTRICITY_SELLING_INCOME.df[ELECTRICITY_SELLING_INCOME.Cost], ELECTRICITY_SELLING_INCOME.YearOfCost)
BINARY_SELLING_COST = CostElectricityDf(pd.read_csv(ELECTRICITY_COST_BINARY_PATH, index_col=0))
BINARY_SELLING_COST.df[BINARY_SELLING_COST.Cost] = shift_day_of_year(BINARY_SELLING_COST.df[BINARY_SELLING_COST.Cost],
                                                                     BINARY_SELLING_COST.YearOfCost)
