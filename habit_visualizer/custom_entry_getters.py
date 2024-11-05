from typing import Any


def get_rich_text_time_as_hours(json_entry: dict[str, Any], property_name: str, data_type: str) -> int:
    text_array = json_entry['properties'][property_name][data_type]
    if text_array:
        time_duration = text_array[0]['text']['content']
        hours, minutes = time_duration.split(':')
        return int(hours) + int(minutes) / 60
    return None
