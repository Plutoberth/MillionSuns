"""
----

Model parameter
===============

``Param``
---------

A parameter in the model which provides a value by year.

A list of ``InterpoRanges`` is used to allow complex interpolations.

Represented by a ``dbc.Accordion`` of the ranges.

Inherits from ``BaseInterpoRange``.

----
"""
import typing as t
from secrets import token_hex

import dash_bootstrap_components as dbc
from dash import Dash
from pydantic import BaseModel, PositiveInt, conlist

from .interpo_range import ABCInterpoRange, InterpoRange

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


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
