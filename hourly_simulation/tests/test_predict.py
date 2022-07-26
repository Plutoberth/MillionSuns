import pandas as pd
from ..predict import predict_demand, predict_solar_production
from objects.df import DemandSeries

growth_per_year = 1.03


def test_predict_demand_simple():
    source = 1215.5
    target = source * (growth_per_year ** 9)
    series = pd.Series([1236.0, source])
    demand = DemandSeries(2021, series)
    predicted = predict_demand(demand, growth_per_year, 2030)
    assert predicted.series[1] == target


def test_predict_demand_multiple():
    source = 1215.5
    target = source * (growth_per_year ** 9)
    target2 = target * growth_per_year

    series = pd.Series([1236.0, source])
    demand = DemandSeries(2021, series)
    predicted = predict_demand(demand, growth_per_year, 2030)
    predicted2 = predict_demand(predicted, growth_per_year, 2031)

    assert predicted.series[1] == target
    assert predicted2.series[1] == target2


# TODO: add tests for solar production
