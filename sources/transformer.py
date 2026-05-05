from abc import ABC, abstractmethod
from datetime import date
from typing import Any

import pandas as pd


class Transformer(ABC):
    def __init__(self, json_data: dict[str, Any], year: int):
        self.json_data = json_data
        self._validate_json()
        self.year = year
        self.dates = pd.date_range(f"{self.year}-01-01", f"{self.year}-12-31")

    def _validate_year(self, entry_number: int, entry_date: date):
        if self.year != entry_date.year:
            raise ValueError(
                f"Year {entry_date.year} in entry number {entry_number} is not equal to the set year {self.year}")

    def _validate_json(self):
        if len(self.json_data) == 0:
            raise ValueError("Habit data is empty")

    def to_series(self, original: str, custom_entry_getter) -> pd.Series:
        values = self._calculate_values(original, custom_entry_getter)
        return pd.Series(values, index=self.dates)

    @abstractmethod
    def _calculate_values(self, original: str, custom_entry_getter=None) -> list[float | None]:
        pass
