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
from abc import ABC, abstractmethod

import numpy as np
import numpy_financial as npf

from .base_dash_model import DashModel, DashSelect

__all__ = 'InterpoSelect',


class ABCInterpo(ABC):
    @abstractmethod
    def at(
        self,
        start_year: int,
        end_year: int,
        target_year: int
    ) -> float:
        """ Get the value at a certain year. """
        ...


class BaseInterpo(DashModel, ABCInterpo):
    type: t.Literal['constant', 'linear', 'compound']

    def at(
        self,
        start_year: int,
        end_year: int,
        target_year: int
    ) -> float:
        """ Get the value at a certain year. """
        ...


class Constant(BaseInterpo):
    """
    The value is constant for the entire range.
    """
    type: t.Literal['constant', 'linear', 'compound'] = 'constant'

    value: float = 0

    def at(
        self,
        start_year: int,
        end_year: int,
        target_year: int
    ) -> float:
        return self.value


class Linear(BaseInterpo):
    """
    The value is linearly interpolated between two given values.
    """
    type: t.Literal['constant', 'linear', 'compound'] = 'linear'

    start_value: float = 0
    end_value: float = 0

    def at(
        self,
        start_year: int,
        end_year: int,
        target_year: int
    ) -> float:
        return np.interp(
            x=target_year,
            xp=(start_year, end_year),
            fp=(self.start_value, self.end_value)
        )


class Compound(BaseInterpo):
    """
    The value is compounded from a given value at a given rate.
    """
    type: t.Literal['constant', 'linear', 'compound'] = 'compound'

    start_value: float = 0
    rate: float = 0

    def at(
        self,
        start_year: int,
        end_year: int,
        target_year: int
    ) -> float:
        # pv=-start_value because fv is for debt.
        # i.e. with (rate=0.5, nper=1, pmt=0): pv=-10 -> 15, pv=10 -> 5
        return npf.fv(
            rate=self.rate,
            nper=target_year - start_year,
            pmt=0,  # :)
            pv=-self.start_value
        )


class InterpoSelect(DashSelect[t.Union[Constant, Linear, Compound]]):
    _constant: Constant = Constant()
    _linear: Linear = Linear()
    _compound: Compound = Compound()
