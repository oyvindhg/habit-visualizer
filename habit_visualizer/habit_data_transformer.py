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

    def validate_and_transform(self, property_name: str, category_count: int, category_labels: list[str], category_limits: list[int]) -> HabitData:
        full_year_date_times = pd.date_range(f"{self.year}-01-01", f"{self.year}-12-31")
        data = []
        data_type = self.json_data[0]['properties'][property_name]['type']
        entry_number = 0
        for date_time in full_year_date_times:
            date = date_time.date()

            if entry_number < len(self.json_data):
                self._validate_entry(entry_number)
                entry_date = datetime.strptime(self.json_data[entry_number]['properties']['Date']['date']['start'], '%Y-%m-%d').date()
                if date == entry_date:
                    data_entry = self.json_data[entry_number]['properties'][property_name][data_type]
                    data.append(data_entry)
                    entry_number += 1
                else:
                    print(f"date: {date}, ed: {entry_date}")
                    data.append(None)
            else:
                data.append(None)

        return HabitData(
            title=property_name,
            year=self.year,
            category_count=category_count,
            category_labels=category_labels,
            category_limits=category_limits,
            data=np.array([np.nan if num is None else num for num in data], dtype='float')
        )
