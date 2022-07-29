import copy
import pandas as pd

from common import DemandSeries


def predict_solar_production(
    normalised_production: pd.Series,
    solar_panel_generation_kw: float,
) -> pd.Series:
    """
    Get Solar Production Profile as pd.DataFrame.

    :param normalised_production: normalised solar hourly production ratios (0<=n<=1)
    :param solar_panel_generation_kw: float max power of solar panels built [KW]
    :param params: namedtuple simulation params
    :return: pd.Series: yearly production of solar panels, in KwH
    """
    assert normalised_production.max() <= 1 and normalised_production.min() >= 0, "normalized production values not in range"
    # TODO: improve this to track degradation over the years properly? Should make a big difference during the years when solar production is ramped up.
    # average_production_ratio = (
    #     1 + (1 - params.PV_DEGRADATION) ** params.FACILITY_LIFE_SPAN
    # ) / 2
    average_production_ratio = 1
    generation_with_ratio = solar_panel_generation_kw * average_production_ratio
    adjusted_prod = normalised_production * generation_with_ratio
    return adjusted_prod


def predict_demand(
    hourly_demand: DemandSeries, yoy_growth_proportion: float, simulated_year: int
) -> DemandSeries:
    """
    Predict the growth in demand in a given year with exponential growth with GROWTH_PER_YEAR

    :param yoy_growth_proportion: float: the Year-over-Year growth proportion. Like 1.03
    :param hourly_demand: DemandSeries of pd.DataFrame(columns=['HourOfYear', '$[Year]'])
    :param simulated_year: int year of the wanted output
    :return: DemandSeries of new pd.DataFrame(columns=['HourOfYear', 'Demand']) of the wanted year with extrapolation
    and the year of demand
    """
    assert simulated_year >= hourly_demand.year

    expected_demand = copy.deepcopy(hourly_demand)
    expected_demand.series *= yoy_growth_proportion ** (
        simulated_year - expected_demand.year
    )
    expected_demand.year = simulated_year
    return expected_demand
