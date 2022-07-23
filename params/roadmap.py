import sys
import typing as t
from dataclasses import dataclass
from itertools import product
from pprint import pprint

import numpy as np
from pydantic import Field, NonNegativeInt, PositiveInt, validator

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
class Scenario:
    # clean energy sources
    solar_gen_kw: np.ndarray
    wind_gen_kw: np.ndarray

    # energy storage
    storage_cap_kwh: np.ndarray
    storage_efficiency_p: np.ndarray
    storage_discharge_p: np.ndarray

    @property
    def title(self) -> str:
        return "-".join(
            str(int(param[~0]))
            for param in (
                self.solar_gen_kw,
                self.wind_gen_kw,
                self.solar_gen_kw,
                self.storage_efficiency_p,
                self.storage_discharge_p,
            )
        )

    def __repr__(self):
        return self.title

    def __hash__(self):
        return hash(self.title)

    def __eq__(self, other: "Scenario"):
        return self.title == other.title


class RoadmapParam(DashModel):
    start: NonNegativeInt = Field(..., title="Start Year Value")
    end_min: NonNegativeInt = Field(..., title="End Year Minimum Value")
    end_max: NonNegativeInt = Field(..., title="End Year Maximum Value")
    step: NonNegativeInt = Field(..., title="Step")

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
    start_year: PositiveInt = Field(..., title="Start Year")
    end_year: PositiveInt = Field(..., title="End Year")

    # clean energy sources
    solar_gen_kw: RoadmapParam = Field(..., title="Solar Generation Capacity (KW)")
    wind_gen_kw: RoadmapParam = Field(..., title="Wind Generation Capacity (KW)")

    # energy storage
    storage_cap_kwh: RoadmapParam = Field(..., title="Storage Capacity (KWH)")
    storage_efficiency_p: RoadmapParam = Field(
        ...,
        title="Storage Efficiency (%)",
        description="For every KWH entered, how mush is able to be drawn out.",
    )
    storage_discharge_p: RoadmapParam = Field(
        ...,
        title="Solar Discharge Depth (%)",
        description="How much of the battery's capacity can be drawn out at once.",
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
            self.solar_gen_kw,
            self.wind_gen_kw,
            self.solar_gen_kw,
            self.storage_efficiency_p,
            self.storage_discharge_p,
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
        # a range of end values for each parameter
        end_value_ranges = (
            range(param.end_min, param.end_max, param.step) for param in self._params
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
        solar_gen_kw=RoadmapParam(
            start=4_000, end_min=50_000, end_max=150_000, step=20_000
        ),
        wind_gen_kw=RoadmapParam(start=80, end_min=250, end_max=3_000, step=100),
        storage_cap_kwh=RoadmapParam(
            start=0, end_min=50_000, end_max=400_000, step=50_000
        ),
        storage_efficiency_p=RoadmapParam(
            start=85,
            end_min=90,
            end_max=95,
            step=5,
        ),
        storage_discharge_p=RoadmapParam(start=80, end_min=90, end_max=95, step=5),
    )

    pprint(list(r.scenarios))
