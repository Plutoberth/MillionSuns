import dataclasses
from typing import TypeAlias


# TODO: Add type aliases for Kw and KwH

@dataclasses.dataclass(frozen=True)
class Scenario:
    year: int
    solar_generation_kw: float
    wind_generation_kw: float
    storage_capacity_kwh: float
    # energyOutputKwH / energyInputKwH
    storage_efficiency: float
    # the maximum discharge from storage. i.e., if this is 0.95, storage will always be at least 0.05 full.
    storage_depth_of_discharge: float


@dataclasses.dataclass(frozen=True)
class RoadmapParameter:
    start: int
    min_final: int
    max_final: int
    interval: int

    def __post_init__(self):
        assert self.start <= self.min_final
        assert self.min_final <= self.max_final


@dataclasses.dataclass(frozen=True)
class Roadmap:
    solar_generation_kw: RoadmapParameter
    wind_generation_kw: RoadmapParameter
    storage_capacity_kwh: RoadmapParameter
    storage_efficiency: RoadmapParameter
    storage_depth_of_discharge: RoadmapParameter
