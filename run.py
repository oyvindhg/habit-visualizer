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


def get_custom_function_map():
    return {"get_rich_text_time_as_hours": get_rich_text_time_as_hours}


def run():
    args = parse_arguments()
    config_path = args.config
    no_fetch = args.no_fetch

    load_dotenv()
    auth_key = os.getenv("NOTION_API_SECRET")
    table_id = os.getenv("NOTION_TABLE_ID")

    custom_function_map = get_custom_function_map()

    Path("data").mkdir(exist_ok=True)
    if no_fetch:
        with open("data/habit_data.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)
    else:
        json_data = NotionClient(auth_key).get_data(table_id)
        with open("data/habit_data.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file)

    habit_data_transformer = HabitDataTransformer(json_data)
    
    with open(config_path, 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    Path("output").mkdir(exist_ok=True)
    for config in configs:
        property_name = config["property"]
        labels = config["labels"]
        boundaries = config["boundaries"]
        color_style = config["color_style"]  # 'YlOrBr'  # 'PuBu'
        custom_function_name = config["custom_function"]
        if not custom_function_name:
            custom_entry_getter = None
        else:
            custom_entry_getter = custom_function_map[custom_function_name]
            
        habit_data = habit_data_transformer.validate_and_transform(
            property_name=property_name,
            labels=labels,
            boundaries=boundaries,
            custom_entry_getter=custom_entry_getter
        )

        create_heatmap(habit_data, color_style, f"output/{property_name}.png")

if __name__ == "__main__":
    run()
