import pandas as pd
from ..predict import predict_demand, predict_solar_production
from ..parameters import simulation_params
from objects.df import DemandDf

growth_per_year = 1.03


def test_predict_demand_simple():
    source = 1215.5
    target = source * (growth_per_year ** 9)
    pd_df = pd.DataFrame({
        "HourOfYear": [1, 2],
        "2021": [1236.0, source]
    })
    demand = DemandDf(pd_df)
    predicted = predict_demand(demand, growth_per_year, 2030)
    assert predicted.df[DemandDf.Demand][1] == target


def test_predict_demand_multiple():
    source = 1215.5
    target = source * (growth_per_year ** 9)
    target2 = target * growth_per_year

    pd_df = pd.DataFrame({
        "HourOfYear": [1, 2],
        "2021": [1236.0, source]
    })

    demand = DemandDf(pd_df)
    predicted = predict_demand(demand, growth_per_year, 2030)
    predicted2 = predict_demand(predicted, growth_per_year, 2031)

    assert predicted.df[DemandDf.Demand][1] == target
    assert predicted2.df[DemandDf.Demand][1] == target2


# TODO: add tests for solar production
