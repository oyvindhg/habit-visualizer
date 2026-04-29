import json
import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from habit_visualizer.fitbit_transformer import FitbitTransformer
from habit_visualizer.notion_transformer import NotionTransformer
from habit_visualizer.transformer import Transformer
from habit_visualizer.custom_entry_getters import get_rich_text_time_as_hours, get_from_multiselect


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for transforming raw json data to habits.csv")
    parser.add_argument('-c', '--config', type=str, default="sources.json", help="Path to JSON config file")
    parser.add_argument('-y', '--year', type=int, default=2025, help="Year")
    return parser.parse_args()


def get_custom_function_map():
    return {
        "get_rich_text_time_as_hours": get_rich_text_time_as_hours,
        "get_from_multiselect": get_from_multiselect
    }

def get_transformer(source: str, property_name: str, raw_data_path: Path, year: int) -> Transformer:
    match source:
        case "notion":
            with open(raw_data_path / "notion_data.json", "r", encoding="utf-8") as file:
                return NotionTransformer(json.load(file), year)
        case "fitbit":
            with open(raw_data_path / f"fitbit_{property_name}.json", "r", encoding="utf-8") as file:
                return FitbitTransformer(json.load(file), year)
        case _:
            raise ValueError(f"{source} is not a valid source")


def run():
    args = parse_arguments()
    config_path = args.config
    year = args.year
    load_dotenv()

    custom_function_map = get_custom_function_map()

    data_dir = Path(os.getenv("DATA_DIR")).expanduser()
    raw_data_path = data_dir / f"raw/{year}"

    with open(config_path, 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    series_map = {}
    for config in configs:
        property_name = config["property"]
        original = config["original"]
        source = config["source"]
        custom_function_name = config["custom_function"]

        custom_entry_getter = custom_function_map[custom_function_name] if custom_function_name else None

        transformer = get_transformer(source, property_name, raw_data_path, year)
        series_map[property_name] = transformer.to_series(original, custom_entry_getter)

    new_data = pd.DataFrame(series_map)
    new_data.index.name = "date"

    habits_path = data_dir / "habits.csv"
    if habits_path.exists():
        existing = pd.read_csv(habits_path, parse_dates=["date"], index_col="date")
        existing_without_year = existing[existing.index.year != year]
        combined = pd.concat([existing_without_year, new_data]).sort_index()
    else:
        combined = new_data

    combined.to_csv(habits_path)
    print(f"Transformed and stored file at {habits_path}")


if __name__ == "__main__":
    run()
