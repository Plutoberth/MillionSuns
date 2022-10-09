from enum import Enum, IntEnum


class EmissionType(Enum):
    CO2 = "CO2"
    SOx = "SOx"
    NOx = "NOx"
    PMx = "PMx"


class EnergySource(Enum):
    SOLAR = "Solar"
    WIND = "Wind"
    GAS = "Gas"
    COAL = "Coal"
    STORAGE = "Storage"


class SimHourField(Enum):
    BATTERY_STATE = "BATTERY_STATE"
    CURTAILED_ENERGY = "CURTAILED_ENERGY"
    STORAGE_SOLAR_CHARGE = "STORAGE_SOLAR_CHARGE"
    STORAGE_GAS_CHARGE = "STORAGE_GAS_CHARGE"
    DEMAND = "DEMAND"
    NET_DEMAND = "NET_DEMAND"

    # the actual energy that was used to fulfill demand.
    # all generation, including solar and demand supply, but not including curtailed energy
    SOLAR_USAGE = "SOLAR_USAGE"
    GAS_USAGE = "GAS_USAGE"


class ScenarioCostFields(Enum):
    RENEWABLE_ENERGY_USAGE_PERCENTAGE = "RENEWABLE_PERCENT"
    COST_SOURCE = "COST_SOURCE"
    COST = "COST"


# the energy sources that pollute
POLLUTING_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.COAL]
# the energy sources that can scale according to demand
VARIABLE_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.STORAGE]
