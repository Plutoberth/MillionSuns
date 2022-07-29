from __future__ import annotations
from numpy_financial import pmt, npv
from dataclasses import dataclass
from functools import cached_property
from params.params import AllParams
from enums import EnergySource, EmissionType, POLLUTING_ENERGY_SOURCES
from units import kWh, ILS
from units.units import ILS_per_kW, ILS_per_kWh

@dataclass
class YearlySimulationProductionResults:
    installed_gas_kw: float
    installed_solar_kw: float
    installed_wind_kw: float
    installed_coal_kw: float
    installed_storage_kwh: float

    used_gas_kwh: kWh
    used_coal_kwh: kWh

    @property
    def emitting_used(self) -> kWh:
        return self.used_gas_kwh + self.used_coal_kwh

    def get(self, source_type: EnergySource):
        return {
            EnergySource.GAS: self.installed_gas_kw,
            # EnergySource.COAL: self.installed_coal_kw,
            EnergySource.SOLAR: self.installed_solar_kw,
            EnergySource.STORAGE: self.installed_storage_kwh,
            EnergySource.WIND: self.installed_wind_kw,
        }[source_type]


@dataclass(frozen=True)
class YearlyCost:
    capex: float = 0
    opex: float = 0
    variable_opex: ILS_per_kWh = 0

    @cached_property
    def total(self):
        return self.capex + self.opex + self.variable_opex


def running_npv(rate, last_npv, new_cash_flow, num_years):
    return last_npv + new_cash_flow / ((rate + 1) ** num_years)


def calculate_emissions_cost(year_data: YearlySimulationProductionResults, year: int, params: AllParams) -> ILS:
    # TODO: use the emissions module instead of calculating emissions here
    emissions_cost = ILS()
    for source in POLLUTING_ENERGY_SOURCES:
        source_emissions_params = params.emissions.get(source)

        for emission_type in EmissionType:
            # TODO: quadruple check all of the units here
            emission_kwh_coeff = source_emissions_params.get(emission_type)
            # TODO: what is emitting_used? could we be calculating twice because it's duped for gas and coal?
            kwh_used = year_data.emitting_used
            emission_costs = params.emissions_costs.get(emission_type).at(year)
            # TODO: triple check this formula
            emissions_cost += emission_kwh_coeff * kwh_used * emission_costs
    return emissions_cost


def calculate_costs(yearly_capacities: list[YearlySimulationProductionResults], params: AllParams):
    year_costs = []
    year_npvs = []

    year_costs = [
        {energy_source: YearlyCost(0, 0) for energy_source in EnergySource}
    ]

    year_npvs = [{energy_source: 0 for energy_source in EnergySource}]

    start_year = params.general.start_year
    end_year = params.general.end_year

    # Intentionally starting from 1 rather than 0 to calculate diffs between years
    # TODO: yes interpolation is nice but where is the year range? 20 as placeholder
    for year in range(start_year + 1, end_year):
        year_idx = year - start_year

        current_year_costs = {}
        current_year_npvs = {}

        for energy_source in EnergySource:
            source_params = params.costs.get(energy_source)
            source_capacity = yearly_capacities[year_idx].get(energy_source)

            new_capacity = source_capacity - yearly_capacities[year_idx - 1].get(energy_source)

            new_capex = -1 * pmt(
                params.general.wacc_rate,
                source_params.lifetime.at(year),
                new_capacity,
            )

            # Original model adds comulative capex to current non-comulative opex...
            new_opex = source_params.opex.at(year) * source_capacity

            # TODO: double check
            # new_variable_opex = source_params.variable_opex.at(year)
            # TODO: get used capacity and multiply here
            new_variable_opex = 0

            current_year_costs[energy_source] = YearlyCost(
                capex=new_capex, opex=new_opex, variable_opex=new_variable_opex
            )

            current_year_npvs[energy_source] = running_npv(
                params.general.interest_rate,
                year_npvs[year_idx - 1][energy_source],
                current_year_costs[
                    energy_source
                ].total,  # original passes running total
                year_idx,
            )

        # This is a number while other entries in current_year_costs are YearlyCosts's.
        # TODO: this does not spark joy. make this spark joy.
        current_year_costs["externalities"] = calculate_emissions_cost(yearly_capacities[year_idx], year, params)

        year_costs.append(current_year_costs)
        year_npvs.append(current_year_npvs)

    return year_costs, year_npvs
