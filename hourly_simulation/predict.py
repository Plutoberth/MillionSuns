import copy

from objects.df import DemandDf, ProductionDf
from hourly_simulation.parameters import Params


def predict_solar_production(
    normalised_production: ProductionDf,
    solar_panel_generation_kw: float,
    params: Params,
) -> ProductionDf:
    """
    Get Solar Production Profile as pd.DataFrame.

    :param normalised_production: ProductionDf normalised solar hourly production pd.DataFrame(columns=['HourOfYear',
        'SolarProduction'])
    :param solar_panel_generation_kw: float max power of solar panels built [KW]
    :param params: namedtuple simulation params
    :return: ProductionDf total production of solar panels pd.DataFrame(columns=['HourOfYear', 'SolarProduction'])
    """
    total_production = copy.deepcopy(normalised_production)
    # TODO: improve this to track degradation over the years properly? Should make a big difference during the years when solar production is ramped up.
    average_production_ratio = (
        1 + (1 - params.PV_DEGRADATION) ** params.FACILITY_LIFE_SPAN
    ) / 2
    total_production.df[total_production.SolarProduction] *= (
        average_production_ratio * solar_panel_generation_kw
    )  # production in Kw
    return total_production


def predict_demand(
    hourly_demand: DemandDf, params: Params, simulated_year: int
) -> DemandDf:
    """
    Predict the growth in demand in a given year with exponential growth with GROWTH_PER_YEAR

    :param params: namedtuple Params: simulation params
    :param hourly_demand: DemandDf of pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param simulated_year: int year of the wanted output
    :return: DemandDf of new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    and the year of demand
    """
    assert simulated_year >= hourly_demand.year

    expected_demand = copy.deepcopy(hourly_demand)
    expected_demand.df[expected_demand.Demand] *= params.GROWTH_PER_YEAR ** (
        simulated_year - expected_demand.year
    )
    expected_demand.year = simulated_year
    return expected_demand
