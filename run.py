import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from habit_visualizer.notion_client import NotionClient
from habit_visualizer.visualizer import create_heatmap
from habit_visualizer.habit_data_transformer import HabitDataTransformer
from habit_visualizer.custom_entry_getters import get_rich_text_time_as_hours

def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for visualizing daily habits from a Notion table in heatmaps")

    parser.add_argument('-c', '--config', type=str, default="config.json", help="Path to JSON config file")
    parser.add_argument('--no-fetch', action='store_true', help="Use local JSON data instead of connecting to Notion API")

    return parser.parse_args()

def run():
    args = parse_arguments()
    config_path = args.config
    no_fetch = args.no_fetch

    with open(config_path, 'r', encoding="utf-8") as config_file:
        config = json.load(config_file)

    property_name = config["property"]
    labels = config["labels"]
    boundaries = config["boundaries"]
    color_style = config["color_style"]  # 'YlOrBr'  # 'PuBu'
    custom_entry_getter = get_rich_text_time_as_hours
    # custom_entry_getter = None

    load_dotenv()
    auth_key = os.getenv("NOTION_API_SECRET")
    table_id = os.getenv("NOTION_TABLE_ID")

    if no_fetch:
        with open("data/habit_data.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)
    else:
        json_data = NotionClient(auth_key).get_data(table_id)
        Path("data").mkdir(exist_ok=True)
        with open("data/habit_data.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file)
        
    habit_data = HabitDataTransformer(json_data).validate_and_transform(
        property_name=property_name,
        labels=labels,
        boundaries=boundaries,
        custom_entry_getter=custom_entry_getter
    )

    create_heatmap(habit_data, color_style, f"data/{property_name}.png")

if __name__ == "__main__":
    run()
