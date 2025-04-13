import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any
from habit_visualizer.habit_data import HabitData


class HabitDataTransformer:
    def __init__(self, json_data: dict[str, Any]):
        self.json_data = json_data
        self._validate_json()
        self.year = datetime.strptime(json_data[0]['properties']['Date']['date']['start'], '%Y-%m-%d').year

    def _validate_json(self):
        if len(self.json_data) == 0:
            raise ValueError("Habit data is empty")
        
    def _validate_entry(self, entry_number: int):
        entry_year = datetime.strptime(self.json_data[entry_number]['properties']['Date']['date']['start'], '%Y-%m-%d').year
        if self.year != entry_year:
            raise ValueError(f"Year {entry_year} in entry number {entry_number} is not equal to the first recorded year {self.year}")

    def get_entry_default(self, json_entry: dict[str, Any], property_name: str, data_type: str) -> int:
        return json_entry['properties'][property_name][data_type]

    def transform(self, property_name: str, original: str, path: str, custom_entry_getter=None) -> None:
        full_year_date_times = pd.date_range(f"{self.year}-01-01", f"{self.year}-12-31")
        data = []
        main_name = original.split('-')[0]
        data_type = self.json_data[0]['properties'][main_name]['type']
        entry_number = 0
        for date_time in full_year_date_times:
            date = date_time.date()

            if entry_number < len(self.json_data):
                self._validate_entry(entry_number)
                entry_date = datetime.strptime(self.json_data[entry_number]['properties']['Date']['date']['start'], '%Y-%m-%d').date()
                if date == entry_date:
                    entry_getter = custom_entry_getter or self.get_entry_default
                    data_entry = entry_getter(self.json_data[entry_number], original, data_type)
                    data.append(data_entry)
                    entry_number += 1
                else:
                    data.append(None)
            else:
                data.append(None)

        np_data = np.array([np.nan if num is None else num for num in data], dtype='float')

        np.savetxt(path, np_data, delimiter="\t")
