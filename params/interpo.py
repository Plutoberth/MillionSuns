"""
----

Interpolation
=============

``InterpoType``
---------------

String Enum of interpolation types.


``ABCInterpo`` children
------------------------

Given value interpolated in a given year range.

- Access values using ``.at(year) -> float``.
- Inherits from``BaseDash``.

``AnyInterpo``
---------------

Union of all interpolation types,
to abstract additions and removals.

----
"""

import typing as t
from abc import abstractmethod
from enum import Enum
from secrets import token_hex

import dash_bootstrap_components as dbc
import numpy as np
import numpy_financial as npf
from dash import Input, Output, html
from pydantic import BaseModel

from .abc_dash import ABCDash

if t.TYPE_CHECKING:
    from dash import Dash
    from dash.development.base_component import Component

__all__ = 'InterpoType', 'Constant', 'Linear', 'Compound', 'AnyInterpo'


class InterpoType(str, Enum):
    """
    Enum of interpolation types.
    """
    constant = 'constant'
    linear = 'linear'
    compound = 'compound'


class ABCInterpo(ABCDash):
    type: InterpoType

    @abstractmethod
    def at(
        self,
        start_year: PositiveInt,
        end_year: PositiveInt,
        target_year: PositiveInt
    ) -> float:
        """ Get the value at a certain year. """
        ...

    class Config:
        use_enum_values = True


class Constant(BaseModel, ABCInterpo):
    """
    The value is constant for the entire range.
    """
    type: InterpoType = InterpoType.constant
    value: float = 0

    def at(
        self,
        start_year: PositiveInt,
        end_year: PositiveInt,
        target_year: PositiveInt
    ) -> float:
        return self.value

    def dash(self, app: 'Dash') -> 'Component':
        tok = token_hex(8)
        input_id = f'input_{tok}'

        @app.callback(
            Output(input_id, 'name'),
            Input(input_id, 'value'),
        )
        def update_value(value: float):
            self.value = value
            return value

        return html.Div(
            [
                dbc.Label('Value'),
                dbc.Input(
                    id=input_id,
                    type='number',
                    inputmode='numeric',
                    step=.01,
                    size='sm',
                    value=self.value
                )
            ]
        )


class Linear(BaseModel, ABCInterpo):
    """
    The value is linearly interpolated between two given values.
    """
    type: InterpoType = InterpoType.linear
    start_value: float = 0
    end_value: float = 0

    def at(
        self,
        start_year: PositiveInt,
        end_year: PositiveInt,
        target_year: PositiveInt
    ) -> float:
        return np.interp(
            x=target_year,
            xp=(start_year, end_year),
            fp=(self.start_value, self.end_value)
        )

    def dash(self, app: 'Dash') -> 'Component':
        tok = token_hex(8)
        start_input_id = f'start_input_{tok}'
        end_input_id = f'end_input_{tok}'

        @app.callback(
            Output(start_input_id, 'name'),
            Input(start_input_id, 'value')
        )
        def update_start_value(value: float):
            self.start_value = value
            return value

        @app.callback(
            Output(end_input_id, 'name'),
            Input(end_input_id, 'value')
        )
        def update_end_value(value: float):
            self.end_value = value
            return value

        return html.Div(
            [
                dbc.Label('Start Value'),
                dbc.Input(
                    id=start_input_id,
                    type='number',
                    step=0.01,
                    size='sm',
                    value=self.start_value
                ),
                dbc.Label('End Value'),
                dbc.Input(
                    id=end_input_id,
                    type='number',
                    step=0.01,
                    size='sm',
                    value=self.end_value
                )
            ]
        )


class Compound(BaseModel, ABCInterpo):
    """
    The value is compounded from a given value at a given rate.
    """
    type: InterpoType = InterpoType.compound
    start_value: float = 0
    rate: float = 0

    def at(
        self,
        start_year: PositiveInt,
        end_year: PositiveInt,
        target_year: PositiveInt
    ) -> float:
        # pv=-start_value because fv is for debt.
        # i.e. with (rate=0.5, nper=1, pmt=0): pv=-10 -> 15, pv=10 -> 5
        return npf.fv(
            rate=self.rate,
            nper=target_year - start_year,
            pmt=0,  # :)
            pv=-self.start_value
        )

    def dash(self, app: 'Dash') -> 'Component':
        tok = token_hex(8)
        start_input_id = f'start_input_{tok}'
        rate_input_id = f'rate_input_{tok}'

        @app.callback(
            Output(start_input_id, 'name'),
            Input(start_input_id, 'value')
        )
        def update_start_value(value: float):
            self.start_value = value
            return value

        @app.callback(
            Output(rate_input_id, 'name'),
            Input(rate_input_id, 'value')
        )
        def update_rate_value(value: float):
            self.rate = value
            return value

        return html.Div(
            [
                dbc.Label('Start Value'),
                dbc.Input(
                    id=start_input_id,
                    type='number',
                    step=0.01,
                    size='sm',
                    value=self.start_value
                ),
                dbc.Label('Rate'),
                dbc.Input(
                    id=rate_input_id,
                    type='number',
                    step=0.01,
                    min=0,
                    max=1,
                    size='sm',
                    value=self.rate
                )
            ]
        )


AnyInterpo = Constant | Linear | Compound
