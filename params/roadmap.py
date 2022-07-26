import sys
import typing as t
from dataclasses import dataclass
from itertools import product
from pprint import pprint

import numpy as np
from pydantic import Field, NonNegativeFloat, PositiveInt, validator

from dash_models import DashModel

T = t.TypeVar("T")
MINOR = 1


def remove_duplicates(it: t.Iterable[T]) -> t.Iterator[T]:
    """
    Remove duplicates from an iterator while preserving order.
    """
    assert (
        sys.version_info[MINOR] >= 6
    ), "This function only works in python 3.6+, where dicts are insertion order."
    yield from dict.fromkeys(it)


@dataclass
class YearlyScenario:
    solar_capacity_kw: float
    wind_capacity_kw: float
    storage_capacity_kwh: float
    storage_efficiency: float
    storage_discharge: float

@dataclass
class Scenario:
    """
    Values for a possible futures.

    Each attribute is an array of values from some start year to some end year.

    The years are not included, and it is assumed the arrays are correct.
     This is strictly a typed container.
    """

    # clean energy sources
    solar_capacity_kw: np.ndarray
    wind_capacity_kw: np.ndarray

    # energy storage
    storage_capacity_kwh: np.ndarray
    storage_efficiency: np.ndarray
    storage_discharge: np.ndarray

    def __iter__(self) -> t.Iterator[YearlyScenario]:
        zipped = np.dstack((self.solar_capacity_kw, self.wind_capacity_kw, self.storage_capacity_kwh, self.storage_efficiency, self.storage_discharge))
        zipped = zipped[0]
        print(zipped)
        return map(lambda x: YearlyScenario(*x), zipped)

    @property
    def title(self) -> str:
        """
        Scenario title, for printing and graph labeling.
        :return: Concatenated last values of each attribute.
        """
        return "-".join(
            str(int(param[~0]))
            for param in (
                self.solar_capacity_kw,
                self.wind_capacity_kw,
                self.storage_capacity_kwh,
                self.storage_efficiency,
                self.storage_discharge,
            )
        )

    def __repr__(self):
        return self.title

    def __hash__(self):
        return hash(self.title)

    def __eq__(self, other: "Scenario"):
        return self.title == other.title

class RoadmapParam(DashModel):
    """
    Roadmap parameter, which has a start values
    and range-like attributes for the end value.
    """

    start: NonNegativeFloat = Field(..., title="Start Year Value")
    end_min: NonNegativeFloat = Field(..., title="End Year Minimum Value")
    end_max: NonNegativeFloat = Field(..., title="End Year Maximum Value")
    step: NonNegativeFloat = Field(..., title="Step")

    @validator("end_min")
    def v_end_min(cls, end_min: float, values: dict[str, float]):
        assert end_min >= values["start"], "end_min must be greater or equal to start"
        return end_min

    @validator("end_max")
    def v_end_max(cls, end_max: float, values: dict[str, float]):
        assert (
            end_max >= values["end_min"]
        ), "end_max must be greater or equal to end_min"
        return end_max

    @validator("step")
    def v_step(cls, step: float, values: dict[str, float]):
        assert step <= (
            values["end_min"] - values["start"]
        ), "step must be smaller or equal to end_min - start"
        return step


class Roadmap(DashModel):
    """
    Represents a variety of future scenarios.
    Each parameter is a `RoadmapParameter`, a range of ranges of values.

    A cartesian product of these generates all possible `Scenario`s.
    """

    start_year: PositiveInt = Field(..., title="Start Year")
    end_year: PositiveInt = Field(..., title="End Year")

    # clean energy sources
    solar_capacity_kw: RoadmapParam = Field(..., title="Solar Generation Capacity (KW)")
    wind_capacity_kw: RoadmapParam = Field(..., title="Wind Generation Capacity (KW)")

    # energy storage
    storage_capacity_kwh: RoadmapParam = Field(..., title="Storage Capacity (KWH)")

    # TODO: add constraints for rates.
    storage_efficiency: RoadmapParam = Field(
        ...,
        title="Storage Efficiency (Rate)",
        description="The rate of energy that can be drawn out, from the "
        "input energy",
    )
    storage_discharge: RoadmapParam = Field(
        ...,
        title="Battery Discharge Depth (Rate)",
        description="The minimum rate of energy in the battery",
    )

    _params: tuple[RoadmapParam, ...]

    @validator("end_year")
    def v_end_year(cls, end_year: float, values: dict[str, int | RoadmapParam]):
        assert (
            end_year >= values["start_year"]
        ), "end_year must be greater or equal to start_year"
        return end_year

    def __init__(self, **data):
        super().__init__(**data)

        self._params = (
            self.solar_capacity_kw,
            self.wind_capacity_kw,
            self.storage_capacity_kwh,
            self.storage_efficiency,
            self.storage_discharge,
        )

    def _scenario_from_ends(self, end_values: t.Sequence[int]) -> Scenario:
        """
        Create a scenario from the given end values
        and the years in this Roadmap.

        :param end_values: Value for the end year for each Scenario parameter, ordered.
        :return: A constructed Scenario.
        """
        return Scenario(
            *(
                np.linspace(
                    start=param.start,
                    stop=end_val,
                    num=self.end_year - self.start_year,
                )
                for param, end_val in zip(self._params, end_values)
            )
        )

    @property
    def scenarios(self) -> t.Iterator[Scenario]:
        """
        All possible `Scenario` that can be generated from this `Roadmap`.
        """
        # a range of end values for each parameter
        end_value_ranges = (
            np.arange(param.end_min, param.end_max, param.step) for param in self._params
        )

        # all combinations of end values
        ends = product(*end_value_ranges)

        return remove_duplicates(
            map(
                self._scenario_from_ends,
                ends,
            )
        )


if __name__ == "__main__":

    # mostly copied from google-sheets
    r = Roadmap(
        start_year=2020,
        end_year=2050,
        solar_capacity_kw=RoadmapParam(
            start=4_000, end_min=50_000, end_max=150_000, step=20_000
        ),
        wind_capacity_kw=RoadmapParam(start=80, end_min=250, end_max=3_000, step=100),
        storage_capacity_kwh=RoadmapParam(start=0, end_min=50_000, end_max=400_000, step=50_000),
        storage_efficiency=RoadmapParam(
            start=85,
            end_min=90,
            end_max=95,
            step=5,
        ),
        storage_discharge=RoadmapParam(start=80, end_min=90, end_max=95, step=5),
    )

    pprint(list(r.scenarios))
