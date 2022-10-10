import pandas as pd


def month_marks():
    # year hardly matters, except leap years
    _year = 2020

    result = {}
    for month in range(12):
        timestamp = pd.Timestamp(_year, month + 1, 1)
        day = timestamp.dayofyear
        result[day] = "|"
        result[day + 15] = timestamp.month_name()
    result[pd.Timestamp(_year, 12, 31).dayofyear - 1] = "|"
    return result


def year_marks(minimum, maximum):
    marked_years = filter(lambda x: x % 10 == 0, range(minimum, maximum + 1))
    marked_years = list(marked_years)

    # ensure end and start year are present
    if maximum != marked_years[-1]:
        marked_years.append(maximum)

    if minimum != marked_years[0]:
        marked_years.append(minimum)

    return {y: str(y) for y in marked_years}
