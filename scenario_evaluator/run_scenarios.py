from dataclasses import dataclass

import numpy as np
import pandas as pd
from common import EnergySource

from params.roadmap import Scenario, YearlyScenario
from params.params import AllParams
from common import DemandSeries
from hourly_simulation.predict import predict_demand, predict_solar_production
from hourly_simulation.strategies import nzo_greedy_strategy
import data


def run_scenario(scenario: Scenario, params: AllParams) -> list[pd.DataFrame]:
    original_demand = data.read_2018_demand()
    solar_prod_ratio = data.get_normalized_solar_prod_ratio()
    return run_scenario_ex(original_demand, solar_prod_ratio, scenario, params)


# TODO: might be cool to check in the simulation whether we reached the edges of the Roadmap iterator
#       in the optimal scenario. Could help us find an optimum because if the best value is at the edge, better
#       values might be lying beyond.
# TODO: add a progress bar?
def run_scenario_ex(
        original_demand: DemandSeries,
        solar_prod_ratio: pd.Series,
        scenario: Scenario,
        params: AllParams,
) -> list[pd.DataFrame]:
    scenario_iter = iter(scenario)
    year_and_scenario = zip(
        range(params.general.start_year, params.general.end_year), scenario_iter
    )

    results: list[pd.DataFrame] = []

    for year, yearly_scenario in year_and_scenario:
        results.append(run_scenario_year(year, yearly_scenario, original_demand, solar_prod_ratio, params))

    return results


def run_scenario_year(
        year: int,
        yearly_scenario: YearlyScenario,
        original_demand: DemandSeries,
        solar_prod_ratio: pd.Series,
        params: AllParams
):
    demand_scaled = predict_demand(
        original_demand, params.general.demand_growth_rate, year
    )

    solar_production = predict_solar_production(
        solar_prod_ratio, yearly_scenario.solar_capacity_kw
    )

    coal_prod = np.full(len(solar_production), params.general.coal_must_run.at(year))

    fixed_production = pd.DataFrame({
        EnergySource.SOLAR: solar_production,
        EnergySource.COAL: coal_prod
    })

    storage_efficiency = yearly_scenario.storage_efficiency
    storage_capacity = yearly_scenario.storage_capacity_kwh
    scaled_capacity = storage_capacity * (1 - yearly_scenario.storage_min_energy_rate)

    result = nzo_greedy_strategy.nzo_strategy(
        demand_scaled.series,
        fixed_production,
        scaled_capacity,
        storage_efficiency,
        params.general.charge_rate,
    )

    return result
