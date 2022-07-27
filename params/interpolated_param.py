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


class InterpolatedParam(DashList[InterpoRange], ABCInterpoRange):
    _start_year: int = 0

    def __init__(self, **data):
        super().__init__(**data)

        # get the lowest start year out of all InterpoRanges
        if self.__root__:
            lowest = min(*[r.start_year for r in self.__root__])
            self._start_year = lowest


    def at(self, year: int) -> float:
        assert year >= self._start_year
        return sum(
            (
                [r for _ in range(r.end_year - r.start_year)]
                for r in sorted(self.__root__, key=lambda r: r.start_year)
            ),
            start=[],
        )[year - self._start_year].at(year)
