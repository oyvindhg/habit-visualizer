import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Any

from habit_visualizer.transformer import Transformer


class FitbitTransformer(Transformer):
    def __init__(self, json_data: dict[str, Any], year: int):
        self.json_data = json_data
        self._validate_json()
        self.year = year

    def _validate_json(self):
        if len(self.json_data) == 0:
            raise ValueError("Habit data is empty")

    def _validate_date(self, entry_number: int, entry_date: date):
        if self.year != entry_date.year:
            raise ValueError(f"Year {entry_date.year} in entry number {entry_number} is not equal to the set year {self.year}")

    def get_entry_default(self, json_entry: dict[str, Any]) -> float:
        return float(json_entry['value'])

    def transform(self, original: str, path: str, custom_entry_getter=None) -> None:
        full_year_date_times = pd.date_range(f"{self.year}-01-01", f"{self.year}-12-31")
        data = []
        entries = self.json_data[original]
        date_label = 'dateTime'
        if original == 'sleep':
            date_label = 'dateOfSleep'
        entry_number = 0
        for date_time in full_year_date_times:
            current_date = date_time.date()

            if entry_number < len(entries):
                entry_date = datetime.strptime(entries[entry_number][date_label],'%Y-%m-%d').date()
                self._validate_date(entry_number, entry_date)
                if current_date == entry_date:
                    if original == 'sleep':
                        sleep_hours = 0
                        while entry_number < len(entries) and current_date == datetime.strptime(entries[entry_number]['dateOfSleep'],'%Y-%m-%d').date():
                            sleep_hours += entries[entry_number]['minutesAsleep'] / 60
                            entry_number += 1
                        data_entry = sleep_hours
                    else:
                        entry_getter = custom_entry_getter or self.get_entry_default
                        data_entry = entry_getter(entries[entry_number])
                        entry_number += 1
                    if data_entry > 0:
                        data.append(data_entry)
                    else:
                        data.append(None)
                else:
                    data.append(None)
            else:
                data.append(None)

        np_data = np.array([np.nan if num is None else num for num in data], dtype='float')

        np.savetxt(path, np_data, delimiter="\t")
