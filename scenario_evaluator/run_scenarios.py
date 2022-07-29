from dataclasses import dataclass

import pandas as pd
from common import EnergySource

from params.roadmap import Scenario
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
        demand_scaled = predict_demand(
            original_demand, params.general.demand_growth_rate, year
        )
        solar_production = predict_solar_production(
            solar_prod_ratio, yearly_scenario.solar_capacity_kw
        )
        fixed_production = pd.DataFrame({EnergySource.SOLAR: solar_production})
        storage_efficiency = yearly_scenario.storage_efficiency
        # TODO: this is unused, we should probably integrate it later
        # stroage_discharge = yearly_scenario.storage_discharge

        result = nzo_greedy_strategy.nzo_strategy(
            demand_scaled.series,
            fixed_production,
            yearly_scenario.storage_capacity_kwh,
            storage_efficiency,
            params.general.charge_rate,
        )

        results.append(result)

    return results



