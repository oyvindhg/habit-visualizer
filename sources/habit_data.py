from dataclasses import dataclass
import pandas as pd


@dataclass
class HabitData:
    title: str
    year: int
    boundaries: list[int]
    labels: list[str]
    data: pd.DataFrame
