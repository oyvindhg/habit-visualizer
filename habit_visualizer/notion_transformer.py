import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Any

from habit_visualizer.transformer import Transformer


class NotionTransformer(Transformer):
    def __init__(self, json_data: dict[str, Any], year: int):
        self.json_data = json_data
        self._validate_json()
        self.year = year

    def _validate_json(self):
        if len(self.json_data) == 0:
            raise ValueError("Habit data is empty")
        
    def _validate_year(self, entry_number: int, entry_date: date):
        if self.year != entry_date.year:
            raise ValueError(
                f"Year {entry_date.year} in entry number {entry_number} is not equal to the set year {self.year}")

    def get_entry_default(self, json_entry: dict[str, Any], name: str, data_type: str) -> int:
        return json_entry['properties'][name][data_type]

    def transform(self, original: str, path: str, custom_entry_getter=None) -> None:
        full_year_date_times = pd.date_range(f"{self.year}-01-01", f"{self.year}-12-31")
        data = []
        main_name = original.split('-')[0]
        data_type = self.json_data[0]['properties'][main_name]['type']
        entry_number = 0
        for date_time in full_year_date_times:
            current_date = date_time.date()

            if entry_number < len(self.json_data):
                entry_date = datetime.strptime(self.json_data[entry_number]['properties']['Date']['date']['start'], '%Y-%m-%d').date()
                self._validate_year(entry_number, entry_date)
                if current_date == entry_date:
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
