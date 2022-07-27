from enum import IntEnum

class EmissionType(IntEnum):
    CO2 = 0
    SOx = 1
    NOx = 2
    PMx = 3

class EnergySource(IntEnum):
    SOLAR = 0
    WIND = 1
    GAS = 2
    COAL = 3
    STORAGE = 4

class SimHourField(IntEnum):
    BATTERY_STATE = 0
    CURTAILED_ENERGY = 1
    STORAGE_SOLAR_CHARGE = 2
    STORAGE_GAS_CHARGE = 3
    DEMAND = 4
    NET_DEMAND = 5

    # the actual energy that was used to fulfill demand.
    # all generation, including solar and demand supply, but not including curtailed energy
    SOLAR_USAGE = 6
    GAS_USAGE = 7



# the energy sources that pollute
POLLUTING_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.COAL]
# the energy sources that can scale according to demand
VARIABLE_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.STORAGE]
