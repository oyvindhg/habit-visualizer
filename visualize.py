import json
import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from habit_visualizer.habit_data import HabitData
from habit_visualizer.heatmap_visualizer import HeatmapVisualizer


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool for visualizing daily habits from a Notion table in heatmaps")
    parser.add_argument('-c', '--config', type=str, default="display.json", help="Path to JSON config file")
    parser.add_argument('-y', '--year', type=int, default=2025, help="Year to visualize")
    return parser.parse_args()


def run():
    args = parse_arguments()
    config_path = args.config
    year = args.year
    load_dotenv()

    data_dir = Path(os.getenv("DATA_DIR")).expanduser()

    with open(config_path, 'r', encoding="utf-8") as config_file:
        configs = json.load(config_file)

    all_data = pd.read_csv(data_dir / "habits.csv", parse_dates=["date"], index_col="date")
    year_data = all_data[all_data.index.year == year]

    output_directory = data_dir / f"output/{year}"
    output_directory.mkdir(parents=True, exist_ok=True)

    visualizer = HeatmapVisualizer()

    for config in configs:
        property_name = config["property"]
        title = config["title"]
        labels = config["labels"]
        boundaries = config["boundaries"]
        color_style = config["color_style"]

        data = year_data[[property_name]].rename(columns={property_name: "value"})

        habit_data = HabitData(
            title=title,
            year=year,
            boundaries=boundaries,
            labels=labels,
            data=data
        )

        visualizer.visualize(habit_data, color_style, str(output_directory / f"{property_name}_heatmap.png"))


if __name__ == "__main__":
    run()
