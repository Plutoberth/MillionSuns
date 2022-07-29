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
from units import kg_per_kWh, ILS_per_kg, ILS_per_kW, ILS_per_kWh, kW

# TODO: validate that all InterpolatedParams start at the correct start year, and end at the correct end year.

class EmissionsPricing(DashModel):
    """
    Pricing for an emissions tax, aka a carbon tax
    """

    CO2: InterpolatedParam[ILS_per_kg] = Field(
        InterpolatedParam[ILS_per_kg](), title="CO2 Pricing (ILS/kg)"
    )
    SOx: InterpolatedParam[ILS_per_kg] = Field(
        InterpolatedParam[ILS_per_kg](),
        title="SOx Pricing (ILS/kg)",
        description="Sulfur Oxides",
    )
    NOx: InterpolatedParam[ILS_per_kg] = Field(
        InterpolatedParam[ILS_per_kg](),
        title="NOx Pricing (ILS/kg)",
        description="Nitrogen Oxides",
    )
    PMx: InterpolatedParam[ILS_per_kg] = Field(
        InterpolatedParam[ILS_per_kg](),
        title="PMx Pricing (ILS/kg)",
        description="Particulate Matter",
    )

    def get(self, emission_type: EmissionType) -> InterpolatedParam[ILS_per_kg]:
        return {
            EmissionType.CO2: self.CO2,
            EmissionType.SOx: self.SOx,
            EmissionType.NOx: self.SOx,
            EmissionType.PMx: self.PMx,
        }[emission_type]


class EnergySourceEmissions(DashModel):
    """
    The emissions created by an energy sources. Relevant to coal and gas.
    """

    CO2: kg_per_kWh = Field(0, title="CO2 emissions (kg/kWh)")
    SOx: kg_per_kWh = Field(
        0, title="SOx emissions (kg/kWh)", description="Sulfur Oxides"
    )
    NOx: kg_per_kWh = Field(
        0, title="NOx emissions (kg/kWh)", description="Nitrogen Oxides"
    )
    PMx: kg_per_kWh = Field(
        0, title="PMx emissions (kg/kWh)", description="Particulate Matter"
    )

    def get(self, emission: EmissionType) -> kg_per_kWh:
        return {
            EmissionType.CO2: self.CO2,
            EmissionType.SOx: self.SOx,
            EmissionType.NOx: self.NOx,
            EmissionType.PMx: self.PMx,
        }[emission]


class EnergySourceCosts(DashModel):
    """
    The costs associated with an energy source
    """

    capex: InterpolatedParam[ILS_per_kW] = Field(
        InterpolatedParam[ILS_per_kW] (),
        title="Capex (ILS/kw)",
        description="Initial construction expense",
    )

    opex: InterpolatedParam[ILS_per_kW] = Field(
        InterpolatedParam[ILS_per_kW](),
        title="Constant Opex (ILS/kw/year)",
        description="Maintenance expenses",
    )

    variable_opex: InterpolatedParam[ILS_per_kWh] = Field(
        InterpolatedParam[ILS_per_kWh](),
        title="Variable Opex (ILS/kwh)",
        descripton="Variable generation expenses",
    )

    lifetime: InterpolatedParam[NonNegativeInt] = Field(
        InterpolatedParam[NonNegativeInt](),
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
            # EnergySource.COAL: self.coal,
            EnergySource.STORAGE: self.storage,
        }[source_type]


class AllEmissions(DashModel):
    gas: EnergySourceEmissions = Field(EnergySourceEmissions(), title="Gas")
    coal: EnergySourceEmissions = Field(EnergySourceEmissions(), title="Coal")

    def get(self, source_type: EnergySource) -> EnergySourceEmissions:
        return {# EnergySource.COAL: self.coal,
                EnergySource.GAS: self.gas}[source_type]


class GeneralParams(DashModel):
    start_year: PositiveInt = 2020
    end_year: PositiveInt = 2050

    # TODO: add a better explanation here and better defaults
    wacc_rate: PositiveFloat = Field(1.03, title="Weighted Average Cost of Capital (Rate)")
    interest_rate: PositiveFloat = Field(1.03, title="Interest (Rate)", description="The yearly interest rate (like 1.03).")

    demand_growth_rate: float = Field(
        1.028,
        title="Electricity Demand Growth Rate YoY",
        description="The rate of electricity demand growth from the previous year",
    )

    coal_must_run: InterpolatedParam[kW] = Field(
        InterpolatedParam[kW](), title="Coal Must-Run (KW)"
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
