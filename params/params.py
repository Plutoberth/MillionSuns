"""
----

Model parameters
================
Defines classes for the user-facing parameters of the model.

----
"""

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from dash_models import DashEditorPage
from dash_models.model import DashModel
from .interpolated_param import InterpolatedParam
from enums import EmissionType, EnergySource

# TODO: validate that all InterpolatedParams start at the correct start year, and end at the correct end year.

class EmissionsPricing(DashModel):
    """
    Pricing for an emissions tax, aka a carbon tax
    """

    CO2: InterpolatedParam = Field(InterpolatedParam(), title="CO2 Pricing (ILS/ton)")
    SOx: InterpolatedParam = Field(
        InterpolatedParam(), title="SOx Pricing (ILS/ton)", description="Sulfur Oxides"
    )
    NOx: InterpolatedParam = Field(
        InterpolatedParam(),
        title="NOx Pricing (ILS/ton)",
        description="Nitrogen Oxides",
    )
    PMx: InterpolatedParam = Field(
        InterpolatedParam(),
        title="PMx Pricing (ILS/ton)",
        description="Particulate Matter",
    )


class EnergySourceEmissions(DashModel):
    """
    The emissions created by an energy sources. Relevant to coal and gas.
    """

    CO2: NonNegativeInt = Field(0, title="CO2 emissions (g/KW)")
    SOx: NonNegativeInt = Field(
        0, title="SOx emissions (g/KW)", description="Sulfur Oxides"
    )
    NOx: NonNegativeInt = Field(
        0, title="NOx emissions (g/KW)", description="Nitrogen Oxides"
    )
    PMx: NonNegativeInt = Field(
        0, title="PMx emissions (g/KW)", description="Particulate Matter"
    )

    def get(self, emission: EmissionType) -> NonNegativeInt:
        return {
            EmissionType.CO2: self.CO2,
            EmissionType.SOx: self.SOx,
            EmissionType.NOx: self.NOx,
            EmissionType.PMx: self.PMx
        }[emission]

class EnergySourceCosts(DashModel):
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
        title="Constant Opex (ILS/kw/year)",
        description="Maintenance expenses",
    )

    variable_opex: InterpolatedParam = Field(
        InterpolatedParam(),
        title="Variable Opex (ILS/kwh)",
        descripton="Variable generation expenses",
    )

    lifetime: InterpolatedParam = Field(
        InterpolatedParam(),
        title="Lifetime (years)",
        description="The lifetime of the facility",
    )


class AllSourceCosts(DashModel):
    # TODO: make this generic over a list of energy sources
    solar: EnergySourceCosts = Field(EnergySourceCosts(), title="Solar")
    wind: EnergySourceCosts = Field(EnergySourceCosts(), title="Wind")
    gas: EnergySourceCosts = Field(EnergySourceCosts(), title="Gas")
    coal: EnergySourceCosts = Field(EnergySourceCosts(), title="Coal")
    storage: EnergySourceCosts = Field(EnergySourceCosts(), title="Storage")

    def get(self, source_type: EnergySource) -> EnergySourceCosts:
        return {
            EnergySource.SOLAR: self.solar,
            EnergySource.WIND: self.wind,
            EnergySource.GAS: self.gas,
            EnergySource.COAL: self.coal,
            EnergySource.STORAGE: self.storage
        }[source_type]


class AllEmissions(DashModel):
    gas: EnergySourceEmissions = Field(EnergySourceEmissions(), title="Gas")
    coal: EnergySourceEmissions = Field(EnergySourceEmissions(), title="Coal")

    def get(self, source_type: EnergySource) -> EnergySourceEmissions:
        return {
            EnergySource.COAL: self.coal,
            EnergySource.GAS: self.gas
        }[source_type]


class GeneralParams(DashModel):
    start_year: PositiveInt = 2020
    end_year: PositiveInt = 2050

    solar_prod_hours: PositiveInt = Field(
        1700, title="Average Yearly Solar Production Hours"
    )

    wind_prod_hours: PositiveInt = Field(
        3014, title="Average Yearly Wind Production Hours"
    )

    interest_pct: PositiveInt = Field(3, title="Interest (%)")

    demand_growth_rate: float = Field(
        1.028,
        title="Electricity Demand Growth Rate YoY",
        description="The rate of electricity demand growth from the previous year",
    )

    coal_must_run: InterpolatedParam = Field(
        InterpolatedParam(), title="Coal Must-Run (KW)"
    )

    charge_rate: PositiveFloat = Field(
        0.25,
        title="Battery Charge Rate (Proportion)",
        description="The maximum proportion of the battery that can be charged or "
        "discharged every hour",
    )


class AllParams(DashEditorPage):
    general: GeneralParams = Field(GeneralParams(), title="General Parameters")
    costs: AllSourceCosts = Field(AllSourceCosts(), title="Energy Source Costs")
    emissions_costs: EmissionsPricing = Field(
        EmissionsPricing(), title="EmissionsCosts (Carbon Tax)"
    )
    emissions: AllEmissions = Field(AllEmissions(), title="Energy Source Emissions")
