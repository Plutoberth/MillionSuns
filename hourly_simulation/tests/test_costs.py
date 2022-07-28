from ..costs import calculate_costs, YearlySimulationProductionResults, npv
from enums import EnergySource
from params import AllParams
from data.defaults import DEFAULT_PARAMS


def test_get_costs():
    yearly_capacities = [
        YearlySimulationProductionResults(100, 100, 10, 100, 100, 95, 100),
        YearlySimulationProductionResults(90, 120, 25, 100, 100, 65, 100),
        YearlySimulationProductionResults(80, 140, 45, 100, 100, 55, 100),
        YearlySimulationProductionResults(70, 160, 60, 100, 100, 45, 100),
    ]

    params = AllParams(**DEFAULT_PARAMS)

    year_costs, year_npvs = calculate_costs(yearly_capacities, params)
    years = range(len(yearly_capacities))
    for source in EnergySource:
        print(
            "{} should be roughly equivalent to {}".format(
                year_npvs[years[-1]][source],
                npv(
                    params.general.interest_rate,
                    [year_costs[year][source].total for year in years],
                ),
            )
        )
