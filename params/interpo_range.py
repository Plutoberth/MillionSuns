"""
----

Interpolation Range
===================

``InterpoRange``
----------------

Provides interpolated values in a given year range.

----
"""
from abc import ABC, abstractmethod

from pydantic import PositiveInt

from dash_models import DashListable
from .interpo import InterpoSelect, Constant


class ABCInterpoRange(ABC):
    """
    Allow an object to provide a value at given year.
    """

    @abstractmethod
    def at(self, year: int) -> float:
        """Get value at given year."""
        ...


class InterpoRange(DashListable, ABCInterpoRange):
    # arbitrary defaults
    start_year: PositiveInt = 1
    end_year: PositiveInt = 2
    interpo: InterpoSelect = Constant()

    @property
    def title(self) -> str:
        return f"{self.start_year}-{self.end_year} ({self.interpo.selected})"

    def at(self, year: int) -> float:
        return self.interpo.__root__.at(self.start_year, self.end_year, year)
