"""
----

Interpolation Range
===================

``ABCInterpolatedRange``
-------------------------

Allow an object to provide a value at given year.

- Get an interpolated value using ``.at(year) -> float``.
- Inherits from ``BaseDash``.

``InterpolatedRange``
---------------------

Provides interpolated values in a given year range.

Represented by a ``dbc.AccordionItem``.

----
"""
import typing as t
from abc import abstractmethod
from secrets import token_hex

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output
from pydantic import BaseModel, Field, PositiveInt, validator

from .abc_dash import ABCDash
from .interpo import AnyInterpo, Compound, Constant, InterpoType, Linear
from .utils import to_title

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component


class ABCInterpoRange(ABCDash):
    """
    Allow an object to provide a value at given year.
    """

    @abstractmethod
    def at(self, year: int) -> float:
        """ Get value at given year. """
        ...


class InterpoRange(BaseModel, ABCInterpoRange):
    enabled: bool
    start_year: PositiveInt
    end_year: PositiveInt
    interpo: AnyInterpo

    interpos: dict[InterpoType, AnyInterpo] | None = Field(exclude=True)

    @validator('interpos', always=True)
    def gen_interpos(cls, v: None, values: dict):
        # all possibilities must be generated in advance
        return {
            InterpoType.constant: Constant(type=InterpoType.constant),
            InterpoType.linear: Linear(type=InterpoType.linear),
            InterpoType.compound: Compound(type=InterpoType.compound),
            values['interpo'].type: values['interpo'].copy()
        }

    def at(self, year: int) -> float:
        return self.interpo.at(self.start_year, self.end_year, year)

    def dash(self, app: 'Dash') -> 'Component':
        tok = token_hex(8)
        range_acc_item_id = f'range_acc_item_{tok}'
        enabled_switch_id = f'enabled_switch_{tok}'
        start_year_id = f'start_year_{tok}'
        end_year_id = f'end_year_{tok}'
        interpo_type_id = f'interpo_type_{tok}'
        interpo_args_id = f'interpo_args_{tok}'

        for interpo in self.interpos.values():
            interpo.dash(app)

        @app.callback(
            Output(interpo_args_id, 'children'),
            Input(interpo_type_id, 'value')
        )
        def update_interpo_args(interpo_type: InterpoType):
            self.interpo = self.interpos[interpo_type]
            return self.interpo.dash(app)

        @app.callback(
            Output(range_acc_item_id, 'title'),
            Input(start_year_id, 'value'),
            Input(end_year_id, 'value')
        )
        def update_title(
            start_year: int,
            end_year: int
        ):
            self.start_year = start_year
            self.end_year = end_year

            return f'{start_year} - {end_year}'

        @app.callback(
            Output(range_acc_item_id, 'style'),
            Input(enabled_switch_id, 'value')
        )
        def update_style(
            enabled_switches: list[int]
        ):
            self.enabled = bool(enabled_switches)

            return {} if self.enabled else {'textDecoration': 'line-through'}

        return dbc.AccordionItem(
            id=range_acc_item_id,
            children=[
                dbc.Checklist(
                    id=enabled_switch_id,
                    options=[
                        {'label': 'Enabled', 'value': 1}
                    ],
                    value=[1] if self.enabled else [],
                    switch=True
                ),
                dbc.Label('Start Year'),
                dbc.Input(
                    id=start_year_id,
                    type='number',
                    value=self.start_year,
                    min=0,
                    step=1,
                    size='sm'
                ),
                dbc.Label('End Year'),
                dbc.Input(
                    id=end_year_id,
                    type='number',
                    value=self.end_year,
                    min=0,
                    step=1,
                    size='sm'
                ),
                dbc.Label('Interpolation Type'),
                dbc.Select(
                    id=interpo_type_id,
                    options=[
                        {'label': to_title(interpo), 'value': interpo}
                        for interpo in InterpoType
                    ],
                    value=self.interpo.type
                ),
                dbc.Label('Interpolation Args'),
                dbc.Card(
                    id=interpo_args_id,
                    class_name='p-3',
                    children=self.interpo.dash(app)
                )
            ]
        )
