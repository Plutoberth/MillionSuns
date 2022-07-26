import pandas as pd

from enums import EnergySource, EmissionType, POLLUTING_ENERGY_SOURCES
from params.params import AllEmissions, EnergySourceEmissions


def calculate_source_emissions(
    usage_kwh: float, emissions_coefficients: EnergySourceEmissions
) -> pd.Series:
    dct = {}

    for emission in EmissionType:
        dct[emission] = usage_kwh * emissions_coefficients.get(emission)

    return pd.Series(dct)


def calculate_emissions(
    source_production: pd.Series, all_emissions: AllEmissions
) -> pd.DataFrame:
    """
    :param source_production: a series where the index is an EnergySource and the value is the generation.
    """
    values = []
    for source, gen in source_production.iteritems():
        if source in POLLUTING_ENERGY_SOURCES:
            coeffs = all_emissions.get(source)
            result_emissions = calculate_source_emissions(gen, coeffs)
            values.append((source, result_emissions))
    return pd.DataFrame(values)
