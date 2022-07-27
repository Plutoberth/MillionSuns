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


# the energy sources that pollute
POLLUTING_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.COAL]
# the energy sources that can scale according to demand
VARIABLE_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.STORAGE]
