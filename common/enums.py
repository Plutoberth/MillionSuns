from enum import Enum, IntEnum


class EmissionType(str, Enum):
    CO2 = "CO2"
    SOx = "SOx"
    NOx = "NOx"
    PMx = "PMx"


class EnergySource(str, Enum):
    SOLAR = "Solar"
    WIND = "Wind"
    GAS = "Gas"
    COAL = "Coal"
    STORAGE = "Storage"


class SimMiscFields(str, Enum):
    BATTERY_STATE = "BATTERY_STATE"
    CURTAILED_ENERGY = "CURTAILED_ENERGY"
    FIXED_STORAGE_CHARGE = "STORAGE_SOLAR_CHARGE"
    STORAGE_GAS_CHARGE = "STORAGE_GAS_CHARGE"
    DEMAND = "DEMAND"
    NET_DEMAND = "NET_DEMAND"

    # the energy that was used to fulfill demand.
    SOLAR_USAGE = "SOLAR_USAGE"
    GAS_USAGE = "GAS_USAGE"


# the energy that was used to fulfill demand; all the fields should sum up to the demand.
SimUsageFields = EnergySource


class ScenarioCostFields(str, Enum):
    RENEWABLE_ENERGY_USAGE_PERCENTAGE = "RENEWABLE_PERCENT"
    COST_SOURCE = "COST_SOURCE"
    COST = "COST"


# the energy sources that pollute
POLLUTING_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.COAL]
# the energy sources that can scale according to demand
VARIABLE_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.STORAGE]
# the energy sources that can't be scaled according to demand
FIXED_ENERGY_SOURCES = [EnergySource.COAL, EnergySource.SOLAR, EnergySource.WIND]
