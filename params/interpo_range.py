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
from abc import ABC, abstractmethod

from pydantic import PositiveInt

from .base_dash_model import DashModel
from .interpo import InterpoSelect


class ABCInterpoRange(ABC):
    """
    Allow an object to provide a value at given year.
    """

    @abstractmethod
    def at(self, year: int) -> float:
        """ Get value at given year. """
        ...


class InterpoRange(DashModel, ABCInterpoRange):
    enabled: bool
    start_year: PositiveInt
    end_year: PositiveInt
    interpo: InterpoSelect

    def at(self, year: int) -> float:
        return self.interpo.selected.at(self.start_year, self.end_year, year)
