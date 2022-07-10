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

import inspect

from pydantic import PrivateAttr

from .base_dash_model import DashModel
from .interpo_range import ABCInterpoRange, InterpoRange


class InterpolatedParam(DashModel, ABCInterpoRange):
    ranges: InterpoRange

    _ranges: list[InterpoRange] = PrivateAttr()
    _start_year: int = PrivateAttr(0)

    def __init__(self, **data):
        super().__init__(**data)

        self._ranges = [
            member[1] for member in inspect.getmembers(
                self,
                predicate=lambda attr: isinstance(attr, InterpoRange)
            )
        ]

    def at(self, year: int) -> float:
        return sum(
            ([r for _ in range(r.end_year - r.start_year)] for r in
             sorted(self._ranges, key=lambda r: r.start_year)
             if r.enabled),
            start=[]
        )[year - self._start_year].at(year)
