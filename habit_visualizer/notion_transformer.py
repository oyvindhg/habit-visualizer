from datetime import datetime
from typing import Any

from habit_visualizer.transformer import Transformer


class NotionTransformer(Transformer):
    def get_entry_default(self, json_entry: dict[str, Any], name: str, data_type: str) -> float | None:
        entry_value = json_entry['properties'][name][data_type]
        return float(entry_value) if entry_value is not None else None

    def _calculate_values(self, original: str, custom_entry_getter=None) -> list[float | None]:
        values = []
        entries = self.json_data
        main_name = original.split('-')[0]
        data_type = self.json_data[0]['properties'][main_name]['type']
        entry_number = 0
        for date_time in self.dates:
            current_date = date_time.date()
            value = None

            if entry_number < len(entries):
                entry_date = datetime.strptime(entries[entry_number]['properties']['Date']['date']['start'], '%Y-%m-%d').date()
                self._validate_year(entry_number, entry_date)
                if current_date == entry_date:
                    entry_getter = custom_entry_getter or self.get_entry_default
                    value = entry_getter(entries[entry_number], original, data_type)
                    entry_number += 1

            values.append(value)

        return values
