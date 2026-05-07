import json
import argparse
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sources.fitbit_transformer import FitbitTransformer
from sources.notion_transformer import NotionTransformer
from sources.transformer import Transformer
from sources.custom_entry_getters import get_rich_text_time_as_hours, get_from_multiselect, get_as_bool


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for transforming raw json data to habits.csv")
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year, help="Year")
    return parser.parse_args()


def get_custom_function_map():
    return {
        "get_rich_text_time_as_hours": get_rich_text_time_as_hours,
        "get_from_multiselect": get_from_multiselect,
        "get_as_bool": get_as_bool
    }

def get_transformer(source: str, property_name: str, raw_data_path: Path, year: int) -> Transformer:
    match source:
        case "notion":
            with open(raw_data_path / f"notion-data-{year}.json", "r", encoding="utf-8") as file:
                return NotionTransformer(json.load(file), year)
        case "fitbit":
            with open(raw_data_path / f"fitbit-{property_name}-{year}.json", "r", encoding="utf-8") as file:
                return FitbitTransformer(json.load(file), year)
        case _:
            raise ValueError(f"{source} is not a valid source")


def run():
    args = parse_arguments()
    year = args.year
    load_dotenv()

    custom_function_map = get_custom_function_map()

    data_dir = Path(os.getenv("DATA_DIR")).expanduser()
    raw_data_path = data_dir / "raw"

    with open(data_dir / "sources.example.json", 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    series_map = {}
    for config in configs:
        if year < config.get("from", 0) or year > config.get("to", 9999):
            continue

        property_name = config["property"]
        original = config["original"]
        source = config["source"]
        custom_function_name = config.get("custom_function", None)

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
