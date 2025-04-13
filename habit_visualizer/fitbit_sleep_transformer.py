import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any

from habit_visualizer.transformer import Transformer


class FitbitSleepTransformer(Transformer):
    def __init__(self, json_data: dict[str, Any]):
        self.json_data = json_data
        self._validate_json()
        self.year = datetime.strptime(json_data['sleep'][0]['dateOfSleep'], '%Y-%m-%d').year

    def _validate_json(self):
        if len(self.json_data) == 0:
            raise ValueError("Habit data is empty")

    def _validate_entry(self, entry_number: int):
        entry_year = datetime.strptime(self.json_data['sleep'][entry_number]['dateOfSleep'],'%Y-%m-%d').year
        if self.year != entry_year:
            raise ValueError(
                f"Year {entry_year} in entry number {entry_number} is not equal to the first recorded year {self.year}")

    def transform(self, original: str, path: str, custom_entry_getter=None) -> None:
        full_year_date_times = pd.date_range(f"{self.year}-01-01", f"{self.year}-12-31")
        data = []
        sleep_entries = self.json_data['sleep']
        entry_number = 0
        for date_time in full_year_date_times:
            date = date_time.date()

            if entry_number < len(sleep_entries):
                self._validate_entry(entry_number)
                entry_date = datetime.strptime(sleep_entries[entry_number]['dateOfSleep'],'%Y-%m-%d').date()

                if date == entry_date:
                    sleep_hours = sleep_entries[entry_number]['minutesAsleep'] / 60
                    data.append(sleep_hours)
                    entry_number += 1

                    while entry_number < len(sleep_entries) and date == datetime.strptime(sleep_entries[entry_number]['dateOfSleep'],'%Y-%m-%d').date():
                        sleep_hours = sleep_entries[entry_number]['minutesAsleep'] / 60
                        data[-1] += sleep_hours
                        entry_number += 1
                else:
                    data.append(None)
            else:
                data.append(None)

        np_data = np.array([np.nan if num is None else num for num in data], dtype='float')

        np.savetxt(path, np_data, delimiter="\t")
