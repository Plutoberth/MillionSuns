"""
----

Interpolations
==============

Interpolate a value between two years.

Interface
---------

All interpolations implement ``.at(start_year, end_year, target_year)``,
which will return the value at the target year according to the set attributes.

``InterpoSelect``
-----------------
A ``DashSelect`` for selecting and populating one of the provided interpolations.

Interpolations
--------------

- **Constant**: Always return ``value``.
- **Linear**: Linear interpolation between ``start_value`` and ``end_value``.
- **Compound**: Compound ``start_value`` by ``rate`` *percent* per year.

----
"""

import typing as t
from abc import ABC, abstractmethod

import numpy as np
import numpy_financial as npf
from pydantic import Field, StrictFloat

from dash_models import DashSelect, DashSelectable

__all__ = 'InterpoSelect', 'Constant', 'Linear', 'Compound'


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


class BaseInterpo(DashSelectable, ABCInterpo):
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
    type: t.Literal['constant'] = 'constant'

    value: StrictFloat = 0.

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
    type: t.Literal['linear'] = 'linear'

    start_value: StrictFloat = 0.
    end_value: StrictFloat = 0.

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
    type: t.Literal['compound'] = 'compound'

    start_value: StrictFloat = 0.
    rate: StrictFloat = Field(0., title='Rate (%)')

    def at(
        self,
        start_year: int,
        end_year: int,
        target_year: int
    ) -> float:
        # pv=-start_value because fv is for debt.
        # i.e. with (rate=0.5, nper=1, pmt=0): pv=-10 -> 15, pv=10 -> 5
        return npf.fv(
            rate=self.rate / 100,
            nper=target_year - start_year,
            pmt=0,  # :)
            pv=-self.start_value
        )


class InterpoSelect(DashSelect[t.Union[Constant, Linear, Compound]]):
    _constant: Constant
    _linear: Linear
    _compound: Compound
