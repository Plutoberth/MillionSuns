"""
----

Model parameters
================

``Params``
----------

All parameters of the model.

Each ``InterpolatedParam`` is a known attribute for editor completion,
from which a ``params: list[InterpolatedParam]`` is generated for iteration.

As such, this is not completely generalized,
in the sense that new parameters need to be added manually.

----
"""

from pydantic import PositiveInt

from .base_dash_model import DashEditorPage
from .interpolated_param import InterpolatedParam


class Params(DashEditorPage):
    start_year: PositiveInt
    end_year: PositiveInt

    population: InterpolatedParam
    # solar_panel_price: InterpolatedParam

    _params: dict[str, InterpolatedParam]

    def __init__(self, **data):
        super().__init__(**data)

        for name, attr in data.items():
            if isinstance(attr, InterpolatedParam):
                attr._start_year = self.start_year
                self._params[name] = attr
