"""
----

Model parameter
===============

``InterpolatedParam``
---------------------

Represents a list of ``InterpoRange``s.

Provides a `.at(year) method which will call the matching method on the appropriate
``InterpoRange``

----
"""

from dash_models import DashList
from .interpo_range import ABCInterpoRange, InterpoRange
from typing import Generic, TypeVar, cast

T = TypeVar('T')

class InterpolatedParam(DashList[InterpoRange], ABCInterpoRange, Generic[T]):
    _start_year: int = 0
    _end_year: int = 0

    def __init__(self, **data):
        super().__init__(**data)

        # get the lowest start year out of all InterpoRanges
        if self.__root__:
            list_start_years = [r.start_year for r in self.__root__]
            list_end_years = [r.end_year for r in self.__root__]
            # TODO: will those be changed if the interpolatedparam is modified on runtime?
            self._start_year = min(list_start_years)
            self._end_year = max(list_end_years)

            for idx in range(len(self.__root__) - 1):
                curr, next = self.__root__[idx], self.__root__[idx+1]
                if curr.end_year != next.start_year:
                    raise Exception("all years within the range must be within exactly one InterpoRange")


    def at(self, year: int) -> T:
        if not self._start_year <= year < self._end_year:
            raise Exception(f"requested year not in range [{self._start_year}, {self._end_year})")

        list_of_interpos = sum(
            (
                [r for _ in range(r.end_year - r.start_year)]
                for r in sorted(self.__root__, key=lambda r: r.start_year)
            ),
            start=[],
        )
        interpo = list_of_interpos[year - self._start_year]
        # TODO: make this less ugly :)
        return cast(T, interpo.at(year))
