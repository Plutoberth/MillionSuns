from enum import Enum


class EnergySource(Enum):
    SOLAR = "SOLAR"
    WIND = "WIND"
    GAS = "GAS"
    COAL = "COAL"
    STORAGE = "STORAGE"


VARIABLE_ENERGY_SOURCES = [EnergySource.GAS, EnergySource.STORAGE]
