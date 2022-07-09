import pandas as pd
from ..parameters import process_simulation_params


def test_process_simulation_params():
    csv = [("GROWTH_PER_YEAR", "1.028", "ratio"),
           ("TEST_GEN_PRICE", "3500", "ILS/Mw"),
           ("TEST_CO2_PER_KW", "2000.1234", "CO2/Kw"),
           ("TEST_GEN", "15", "Mw")]
    r = process_simulation_params(csv, with_units=False, as_mw=False)

    assert r["GROWTH_PER_YEAR"] == 1.028
    assert r["TEST_GEN_PRICE"] == 3.5
    assert r["TEST_CO2_PER_KW"] == 2000.1234
    assert r["TEST_GEN"] == 15000.0

# TODO: add a test with units

