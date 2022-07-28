from ..costs import calculate_costs, YearlySimulationProductionResults, npv
from enums import EnergySource
from params import AllParams
from data.defaults import DEFAULT_PARAMS

EPSILON = 0.1

def test_get_costs():
    yearly_capacities = [
        YearlySimulationProductionResults(100, 100, 10, 100, 100, 95, 100),
        YearlySimulationProductionResults(90, 120, 25, 100, 100, 65, 100),
        YearlySimulationProductionResults(80, 140, 45, 100, 100, 55, 100),
        YearlySimulationProductionResults(70, 160, 60, 100, 100, 45, 100),
    ]

    params = AllParams(**DEFAULT_PARAMS)
    # Adjust end_year due to size of list
    params.general.end_year = params.general.start_year + len(yearly_capacities)

    year_costs, year_npvs = calculate_costs(yearly_capacities, params)
    years = range(len(yearly_capacities))
    for source in EnergySource:
        result_npv = year_npvs[years[-1]][source]
        calculated_npv = npv(
                    params.general.interest_rate,
                    [year_costs[year][source].total for year in years],
                )

        diff = abs(calculated_npv - result_npv)
        assert diff < EPSILON
