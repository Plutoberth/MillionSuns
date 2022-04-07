import pandas as pd
# todo: add units

# prediction
GROWTH_PER_YEAR = 1.28

# Batteries
BATTERY_EFFICIENCY = 0.89   # %
BATTERY_DEPTH = 0.8         # %
BATTERY_OPEX = 15.6         # ILS / kW / year
BATTERY_CAPEX = 1004        # ILS per Kw

# Electricity
ELECTRICITY_COST_PATH = '../data/electricity_cost.csv'
ELECTRICITY_COST = pd.read_csv(ELECTRICITY_COST_PATH)   # ILS per Kw

# Solar Panels
SOLAR_OPEX = 70.4       # ILS / kW / year
SOLAR_CAPEX = 3300      # ILS per Kw
SOLAR_PANEL_AREA_DUNAM = 1.0/1000.0     # meter^2
SOLAR_KWH_PER_DUNAM = 1000.0/10.0       # KVH/DUNAM


# future constants
MAXIMUM_SELLING = 1
BATTERY_LIFETIME = 0
SOLAR_LIFETIME = 0
