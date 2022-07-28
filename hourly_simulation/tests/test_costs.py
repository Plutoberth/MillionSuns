from ..costs import calculate_costs, YearlySimulationProductionResults, npv
from enums import EnergySource
from params import AllParams


def test_get_costs():
    yearly_capacities = [
        YearlySimulationProductionResults(100, 100, 100, 100, 100, 100, 100),
        YearlySimulationProductionResults(100, 100, 100, 100, 100, 100, 100),
        YearlySimulationProductionResults(100, 100, 100, 100, 100, 100, 100),
        YearlySimulationProductionResults(100, 100, 100, 100, 100, 100, 100),
    ]

    params = AllParams()

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
