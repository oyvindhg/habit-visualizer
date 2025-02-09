import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from habit_visualizer.fitbit_client import FitbitClient
from habit_visualizer.notion_client import NotionClient


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool to download habit tracker data")
    parser.add_argument('-y', '--year', type=int, default=2025, help="Year to visualize")
    parser.add_argument('-w', '--website', choices=['notion', 'fitbit'], default='notion', help="Which website to download from")
    return parser.parse_args()


def run():
    args = parse_arguments()
    year = args.year
    website = args.website
    load_dotenv()

    match website:
        case 'notion':
            auth_key = os.getenv("NOTION_API_SECRET")
            table_id = os.getenv(f"NOTION_TABLE_{year}_ID")
            data = NotionClient(auth_key).get_data(table_id)
        case 'fitbit':
            client_id = os.getenv("FITBIT_CLIENT_ID")
            client_secret = os.getenv("FITBIT_CLIENT_SECRET")
            data = FitbitClient(client_id=client_id, client_secret=client_secret, token_file="fitbit-tokens.json").get_data()
    
    Path(f"data/{year}").mkdir(exist_ok=True)
    with open(f"data/{year}/{website}_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file)


if __name__ == "__main__":
    run()
