from ..graph_utils import year_marks


def conv(lst):
    return {k: str(k) for k in lst}


def test_year_marks_on_step():
    start, end = 2020, 2050
    assert year_marks(start, end, step=5) == conv([2020, 2025, 2030, 2035, 2040, 2045, 2050])


def test_year_marks_end_not_on_step():
    start, end = 2020, 2049
    assert year_marks(start, end, step=10) == conv([2020, 2030, 2040, 2049])


def test_year_marks_both_not_on_step():
    start, end = 2017, 2051
    assert year_marks(start, end, step=10) == conv([2017, 2020, 2030, 2040, 2050, 2051])
