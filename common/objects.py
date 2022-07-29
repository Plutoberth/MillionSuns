from dataclasses import dataclass
import pandas as pd

@dataclass
class DemandSeries:
    year: int
    series: pd.Series
