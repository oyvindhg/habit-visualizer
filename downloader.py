import os
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

    data_path = f"data/raw/{year}"
    Path(data_path).mkdir(parents=True, exist_ok=True)

    match website:
        case 'notion':
            auth_key = os.getenv("NOTION_API_SECRET")
            table_id = os.getenv(f"NOTION_TABLE_{year}_ID")
            client = NotionClient(auth_key, table_id)

        case 'fitbit':
            client_id = os.getenv("FITBIT_CLIENT_ID")
            client_secret = os.getenv("FITBIT_CLIENT_SECRET")
            client = FitbitClient(client_id=client_id, client_secret=client_secret, token_file="fitbit-tokens.json")

        case _:
            raise ValueError(f"Unsupported website: {website}")

    client.download_data(data_path)


if __name__ == "__main__":
    run()
