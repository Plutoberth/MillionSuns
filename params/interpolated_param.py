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


class Param(BaseModel, ABCInterpoRange):
    unit: str
    ranges: conlist(InterpoRange, min_items=5, max_items=5)
    start_year: PositiveInt
    end_year: PositiveInt

    def at(self, year: int) -> float:
        return sum(
            ([r for _ in range(r.end_year - r.start_year)] for r in
             sorted(self.ranges, key=lambda r: r.start_year)
             if r.enabled),
            start=[]
        )[year - self.start_year].at(year)

    def dash(self, app: 'Dash') -> 'Component':
        tok = token_hex(8)
        ranges_acc_id = f'ranges_acc_{tok}'

        return dbc.Accordion(
            id=ranges_acc_id,
            always_open=True,
            start_collapsed=True,
            children=[_range.dash(app) for _range in self.ranges]
        )
