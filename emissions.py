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
    usage_profile: pd.DataFrame, all_emissions: AllEmissions
) -> pd.DataFrame:
    """
    :param usage_profile: the usage profile for the year. Columns are energy sources, rows are
                          every hour in the year, and the values are the generation for that source in that hour.
    """
    values = []
    for column in usage_profile:
        if column in POLLUTING_ENERGY_SOURCES:
            total_usage = usage_profile[column].sum()
            coeffs = all_emissions.get(column)
            result_emissions = calculate_source_emissions(total_usage, coeffs)
            values.append((column, result_emissions))
    return pd.DataFrame(values)
