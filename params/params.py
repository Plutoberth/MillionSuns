"""
----

Model parameters
================

``Params``
----------

All parameters of the model.

Each ``Param`` is a known attribute for editor completion,
from which a ``params: list[Param]`` is generated for iteration.

As such, this is not completely generalized,
in the sense that new parameters need to be added manually.

----
"""
import typing as t

import dash_bootstrap_components as dbc
from pydantic import Field, PositiveInt, validator

from .base_dash import BaseDash
from .param import Param
from .utils import to_title

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


class Params(BaseDash):
    start_year: PositiveInt
    end_year: PositiveInt

    population: Param
    solar_panel_price: Param

    params: list[tuple[str, Param]] | None = Field(exclude=True)

    @validator(
        'population',
        'solar_panel_price',
        pre=True
    )
    def inject_years(cls, param: dict, values: dict) -> Param:
        return Param(
            **param,
            start_year=values['start_year'],
            end_year=values['end_year']
        )

    @validator('params', always=True)
    def gen_params(cls, v: None, values: dict):
        return [
            (name, attr)
            for name, attr in values.items()
            if isinstance(attr, Param)
        ]

    def dash(self, app: 'Dash') -> 'Component':
        return dbc.Accordion(
            always_open=True,
            start_collapsed=True,
            children=[
                dbc.AccordionItem(
                    title=f'{to_title(name)} ({param.unit})',
                    children=param.dash(app)
                ) for name, param in self.params
            ]
        )
