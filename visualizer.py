import json
import argparse
from pathlib import Path
from habit_visualizer.heatmap_visualizer import create_heatmap
from habit_visualizer.habit_data_transformer import HabitDataTransformer
from habit_visualizer.custom_entry_getters import get_rich_text_time_as_hours

def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for visualizing daily habits from a Notion table in heatmaps")
    parser.add_argument('-c', '--config', type=str, default="config.json", help="Path to JSON config file")
    parser.add_argument('-y', '--year', type=int, default=2024, help="Year to visualize")
    return parser.parse_args()


def get_custom_function_map():
    return {"get_rich_text_time_as_hours": get_rich_text_time_as_hours}


def run():
    args = parse_arguments()
    config_path = args.config
    year = args.year

    custom_function_map = get_custom_function_map()

    Path("data/{year}").mkdir(exist_ok=True)
    with open(f"data/{year}/habit_data.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)

    habit_data_transformer = HabitDataTransformer(json_data)
    
    with open(config_path, 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    Path(f"output/{year}").mkdir(exist_ok=True)
    for config in configs:
        property_name = config["property"]
        title = config["title"]
        labels = config["labels"]
        boundaries = config["boundaries"]
        color_style = config["color_style"]
        custom_function_name = config["custom_function"]
        if not custom_function_name:
            custom_entry_getter = None
        else:
            custom_entry_getter = custom_function_map[custom_function_name]
            
        habit_data = habit_data_transformer.validate_and_transform(
            property_name=property_name,
            title=title,
            labels=labels,
            boundaries=boundaries,
            custom_entry_getter=custom_entry_getter
        )

        create_heatmap(habit_data, color_style, f"output/{year}/{property_name}.png")

if __name__ == "__main__":
    run()
