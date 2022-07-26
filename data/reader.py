import pandas as pd
import os

from objects.df import DemandSeries

DATA_DIR = "./data/raw/"
SOLAR_CSV = os.path.join(DATA_DIR, "national_solar_production.csv")
DEMAND_JSON = os.path.join(DATA_DIR, "demand_2018.json")

def normalize(series):
    max_value = series.max()
    min_value = series.min()
    return (series - min_value) / (max_value - min_value)

def get_normalized_solar_prod_ratio() -> pd.Series:
    solar_prod = pd.read_csv(SOLAR_CSV)["SolarProduction"]
    return normalize(solar_prod)

def read_2018_demand() -> DemandSeries:
    demand = pd.read_json(DEMAND_JSON)[0]
    return DemandSeries(2018, demand)