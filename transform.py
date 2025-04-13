import json
import argparse
from datetime import datetime
from pathlib import Path

from habit_visualizer.fitbit_sleep_transformer import FitbitSleepTransformer
from habit_visualizer.notion_transformer import NotionTransformer
from habit_visualizer.custom_entry_getters import get_rich_text_time_as_hours, get_from_multiselect

def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for transforming raw json data to tsv")
    parser.add_argument('-c', '--config', type=str, default="config.json", help="Path to JSON config file")
    parser.add_argument('-y', '--year', type=int, default=2025, help="Year")
    return parser.parse_args()


def get_custom_function_map():
    return {
        "get_rich_text_time_as_hours": get_rich_text_time_as_hours,
        "get_from_multiselect": get_from_multiselect
        }


def run():
    args = parse_arguments()
    config_path = args.config
    year = args.year

    custom_function_map = get_custom_function_map()

    raw_data_path = f"data/raw/{year}"
    Path(raw_data_path).mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    with open(f"{raw_data_path}/notion_data.json", "r", encoding="utf-8") as file:
        notion_data = json.load(file)
        notion_transformer = NotionTransformer(notion_data)

    fitbit_sleep_entries = []
    for quarter in ["q1", "q2", "q3", "q4"]:
        with open(f"{raw_data_path}/fitbit_sleep_{quarter}.json", "r", encoding="utf-8") as file:
            sleep_data = json.load(file)
            sleep_entries = sleep_data.get("sleep", [])
            fitbit_sleep_entries.extend(sleep_entries)
    fitbit_sleep_entries.sort(key=lambda x: datetime.fromisoformat(x["dateOfSleep"]))
    print(fitbit_sleep_entries)
    fitbit_sleep_data = {"sleep": fitbit_sleep_entries}
    fitbit_sleep_transformer = FitbitSleepTransformer(fitbit_sleep_data)

    processed_data_path = f"data/processed/{year}"
    Path(processed_data_path).mkdir(parents=True, exist_ok=True)
    for config in configs:
        property_name = config["property"]
        source = config["source"]
        original = config["original"]
        custom_function_name = config["custom_function"]
        if not custom_function_name:
            custom_entry_getter = None
        else:
            custom_entry_getter = custom_function_map[custom_function_name]

        match source:
            case "notion": transformer = notion_transformer
            case "fitbit": transformer = fitbit_sleep_transformer
            case _: raise ValueError(f"{source} is not a valid source")

        file_path = f"{processed_data_path}/{property_name}.tsv"

        transformer.transform(
            original=original,
            path=file_path,
            custom_entry_getter=custom_entry_getter
        )

if __name__ == "__main__":
    run()
