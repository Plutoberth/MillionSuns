from enum import Enum


class EnergySource(Enum):
    SOLAR = "SOLAR"
    WIND = "WIND"
    GAS = "GAS"
    COAL = "COAL"
    STORAGE = "STORAGE"


# the energy sources that pollute
POLLUTING_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.COAL]
# the energy sources that can scale according to demand
VARIABLE_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.STORAGE]
