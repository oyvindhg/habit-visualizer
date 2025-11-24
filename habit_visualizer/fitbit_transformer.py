from datetime import datetime
from typing import Any

from habit_visualizer.transformer import Transformer


class FitbitTransformer(Transformer):
    def get_entry_default(self, json_entry: dict[str, Any]) -> float:
        return float(json_entry['value'])

    def _calculate_values(self, original: str, custom_entry_getter=None) -> list[float | None]:
        values = []
        entries = self.json_data[original]
        date_label = 'dateTime'
        if original == 'sleep':
            date_label = 'dateOfSleep'
        entry_number = 0
        for date_time in self.dates:
            current_date = date_time.date()
            value = None

            if entry_number < len(entries):
                entry_date = datetime.strptime(entries[entry_number][date_label],'%Y-%m-%d').date()
                self._validate_year(entry_number, entry_date)
                if current_date == entry_date:
                    if original == 'sleep':
                        sleep_hours = 0
                        while entry_number < len(entries) and current_date == datetime.strptime(entries[entry_number]['dateOfSleep'],'%Y-%m-%d').date():
                            sleep_hours += entries[entry_number]['minutesAsleep'] / 60
                            entry_number += 1
                        value = sleep_hours
                    else:
                        entry_getter = custom_entry_getter or self.get_entry_default
                        value = entry_getter(entries[entry_number])
                        entry_number += 1
                    if value <= 0:
                        value = None

            values.append(value)

        return values
