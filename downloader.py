import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from habit_visualizer.notion_client import NotionClient


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool to download habit tracker data")
    parser.add_argument('-y', '--year', type=int, default=2024, help="Year to visualize")
    return parser.parse_args()

def run():
    args = parse_arguments()
    year = args.year

    load_dotenv()
    auth_key = os.getenv("NOTION_API_SECRET")
    table_id = os.getenv(f"NOTION_TABLE_{year}_ID")

    json_data = NotionClient(auth_key).get_data(table_id)

    Path(f"data/{year}").mkdir(exist_ok=True)
    with open(f"data/{year}/habit_data.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file)


if __name__ == "__main__":
    run()
