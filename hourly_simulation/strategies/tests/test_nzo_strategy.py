from ..nzo_greedy_strategy import nzo_strategy, EnergySource
import pandas as pd

# Everything is in units of KW
MEGA = 1000

STORAGE_EFFICIENCY = 0.87
STORAGE_CHARGE_RATE = 0.25

def test_nzo_strategy():
    storage_capacity_kwh = 5


    demand = pd.Series([1, 2, 2.5, 3, 4, 5, 7, 9, 11, 12, 12, 11, 9, 9, 9, 7, 6, 5, 4, 3, 2, 2, 2, 1, 1, 2, 2.5, 3, 4, 5, 7, 9, 11, 12, 12, 11, 9, 9, 9, 7, 6, 5, 4, 3, 2, 2, 2, 1])
    solar_prod = pd.Series([0, 0, 0, 0, 0, 2, 5, 9, 17, 19, 15, 10, 7, 5, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 9, 17, 19, 15, 10, 7, 5, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    fixed_prod = pd.DataFrame({EnergySource.SOLAR: solar_prod})
    profile, others = nzo_strategy(demand, fixed_prod, storage_capacity_kwh, STORAGE_EFFICIENCY, STORAGE_CHARGE_RATE)
    print("\n\n")
    print(profile)
    print(others)
