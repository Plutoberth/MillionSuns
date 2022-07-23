"""
----

Model parameters
================
Defines classes for the user-facing parameters of the model.

----
"""

from pydantic import Field, PositiveFloat, PositiveInt

from dash_models import DashEditorPage
from .interpolated_param import InterpolatedParam


class EmissionsPricing(DashEditorPage):
    """
    Pricing for an emissions tax, aka a carbon tax
    """

    CO2: InterpolatedParam = Field(InterpolatedParam(), title="CO2 Pricing (ILS/ton)")
    SOX: InterpolatedParam = Field(InterpolatedParam(), title="SOX Pricing (ILS/ton)")
    NOX: InterpolatedParam = Field(InterpolatedParam(), title="NOX Pricing (ILS/ton)")
    PMx: InterpolatedParam = Field(InterpolatedParam(), title="PMx Pricing (ILS/ton)")


class EnergySourceEmissions(DashEditorPage):
    """
    The emissions created by an energy sources. Relevant to coal and gas.
    """

    CO2: PositiveInt = Field(title="CO2 emissions (g/KW)")
    SOX: PositiveInt = Field(title="SOX emissions (g/KW)")
    NOX: PositiveInt = Field(title="NOX emissions (g/KW)")
    PMx: PositiveInt = Field(title="PMx emissions (g/KW)")


class EnergySourceCosts(DashEditorPage):
    """
    The costs associated with an energy source
    """

    capex: InterpolatedParam = Field(
        InterpolatedParam(),
        title="Capex (ILS/kw)",
        description="Initial construction expense",
    )

    opex: InterpolatedParam = Field(
        InterpolatedParam(),
        title="Opex (ILS/kw/year)",
        description="Electricity generation expenses",
    )

    lifetime: InterpolatedParam = Field(
        InterpolatedParam(),
        title="Lifetime (years)",
        description="The lifetime of the facility",
    )


class StorageParams(DashEditorPage):
    charge_rate: PositiveFloat = Field(
        0.25,
        title="Battery Charge Rate (Proportion)",
        description="The maximum proportion of the battery that can be charged or "
        "discharged every hour",
    )

    minimum_charge: PositiveFloat = Field(
        0.05,
        title="Minimum Charge (Proportion)",
        description="The minimum charge that must be kept in the battery at all "
        "times, as a margin",
    )

    efficiency: PositiveFloat = Field(
        0.87,
        title="Efficiency (Proportion)",
        description="The proportion of energy that is kept in the battery, from the "
        "input energy",
    )


class GeneralParams(DashEditorPage):
    start_year: PositiveInt = 2020
    end_year: PositiveInt = 2050

    solar_prod_hours: PositiveInt = Field(
        1700, title="Average Yearly Solar Production Hours"
    )

    wind_prod_hours: PositiveInt = Field(
        3014, title="Average Yearly Wind Production Hours"
    )

    interest_pct: PositiveInt = Field(3, title="Interest (%)")

    usage_growth_rate: float = Field(
        1.028,
        title="Electricity Demand Growth Rate YoY",
        description="The rate of electricity demand growth from the previous year",
    )

    coal_must_run: InterpolatedParam = Field(
        InterpolatedParam, title="Coal Must-Run (KW)"
    )

    def __init__(self, **data):
        super().__init__(**data)

        for name, attr in data.items():
            if isinstance(attr, InterpolatedParam):
                attr._start_year = self.start_year
