import dataclasses
from typing import TypeAlias

# TODO: Improve types with pydantic
# TODO: Add type aliases for stuff like Kw and KwH

@dataclasses.dataclass(frozen=True)
class Scenario:
    year: int
    solarGenerationKw: int
    windGenerationKw: int
    storageCapacityKwH: int
    # energyOutputKwH / energyInputKwH
    storageEfficiency: float
    # the maximum discharge from storage. i.e., if this is 0.95, storage will always be at least 0.05 full.
    storageDepthOfDischarge: float

@dataclasses.dataclass(frozen=True)
class RoadmapParameter:
    start: int
    minFinal: int
    maxFinal: int
    interval: int

    def __post_init__(self):
        assert self.start <= self.minFinal
        assert self.minFinal <= self.maxFinal

# TODO: replace with types from itay raveh's work

@dataclasses.dataclass(frozen=True)
class Roadmap:
    solarGenerationKw: RoadmapParameter
    windGenerationKw: RoadmapParameter
    storageEnergyKwH: RoadmapParameter
    storageEfficiency: RoadmapParameter
    storageDepthOfDischarge: RoadmapParameter

