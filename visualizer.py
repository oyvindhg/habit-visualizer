import json
import argparse
from pathlib import Path

import numpy as np

from habit_visualizer.habit_data import HabitData
from habit_visualizer.heatmap_visualizer import create_heatmap

def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for visualizing daily habits from a Notion table in heatmaps")
    parser.add_argument('-c', '--config', type=str, default="config.json", help="Path to JSON config file")
    parser.add_argument('-y', '--year', type=int, default=2025, help="Year to visualize")
    return parser.parse_args()


def run():
    args = parse_arguments()
    config_path = args.config
    year = args.year

    processed_data_path = f"data/processed/{year}"
    Path(processed_data_path).mkdir(parents=True, exist_ok=True)

    with open(config_path, 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    output_directory = f"output/{year}"

    Path(output_directory).mkdir(parents=True, exist_ok=True)
    for config in configs:
        property_name = config["property"]
        title = config["title"]
        labels = config["labels"]
        boundaries = config["boundaries"]
        color_style = config["color_style"]

        filepath = f"{processed_data_path}/{property_name}.tsv"

        data = np.loadtxt(filepath, delimiter='\t')

        habit_data = HabitData(
            title=title,
            year=year,
            boundaries=boundaries,
            labels=labels,
            data=data
        )

        output_file = f"{output_directory}/{property_name}.png"

        create_heatmap(habit_data, color_style, output_file)

if __name__ == "__main__":
    run()
