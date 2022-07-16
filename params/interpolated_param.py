"""
----

Model parameter
===============

``InterpolatedParam``
---------

A parameter in the model which provides a value by year.

A list of ``InterpoRanges`` is used to allow complex interpolations.

Represented by a ``dbc.Accordion`` of the ranges.

Inherits from ``BaseInterpoRange``.

----
"""

from dash_models import DashList
from .interpo_range import ABCInterpoRange, InterpoRange


class InterpolatedParam(DashList[InterpoRange], ABCInterpoRange):
    _start_year: int = 0

    def at(self, year: int) -> float:
        return sum(
            ([r for _ in range(r.end_year - r.start_year)] for r in
             sorted(self, key=lambda r: r.start_year)),
            start=[]
        )[year - self._start_year].at(year)
