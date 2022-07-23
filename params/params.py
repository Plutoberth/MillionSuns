"""
----

Model parameters
================

``Params``
----------

All parameters of the model.

This is not completely generalized,
in the sense that new parameters need to be added manually.

----
"""

from pydantic import Field, PositiveInt

from dash_models import DashEditorPage
from .interpolated_param import InterpolatedParam


class EnergySourceEmissions(DashEditorPage):
    CO2: PositiveInt = Field(title="CO2 emissions (g/KW)")
    SOX: PositiveInt = Field(title="SOX emissions (g/KW)")
    NOX: PositiveInt = Field(title="NOX emissions (g/KW)")
    PMx: PositiveInt = Field(title="PMx emissions (g/KW)")

    def __init__(self, **data):
        super().__init__(**data)


class EnergySourceCosts(DashEditorPage):
    capex: InterpolatedParam = Field(
        InterpolatedParam(),
        title='Capex (ILS/kw)'
    )

    opex: InterpolatedParam = Field(
        InterpolatedParam(),
        title='Opex (ILS/kw/year)'
    )

    lifetime: InterpolatedParam = Field(
        InterpolatedParam(),
        title="Lifetime (years)"
    )

    def __init__(self, **data):
        super().__init__(**data)


class GeneralParams(DashEditorPage):
    start_year: PositiveInt = 2020
    end_year: PositiveInt = 2050

    solar_prod_hours: PositiveInt = Field(
        1700,
        title="Average Yearly Solar Production Hours"

    )

    wind_prod_hours: PositiveInt = Field(
        3014,
        title="Average Yearly Wind Production Hours"
    )

    interest: PositiveInt = Field(
        3,
        title="Interest (%)"
    )

    population: InterpolatedParam = Field(
        InterpolatedParam(),
        title='Population (Mill)'
    )

    def __init__(self, **data):
        super().__init__(**data)

        for name, attr in data.items():
            if isinstance(attr, InterpolatedParam):
                attr._start_year = self.start_year
