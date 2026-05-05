import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from sources.client import Client
from sources.fitbit_client import FitbitClient
from sources.notion_client import NotionClient


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool to download habit tracker data")
    parser.add_argument('-y', '--year', type=int, default=2025, help="Year to visualize")
    parser.add_argument('-w', '--website', choices=['notion', 'fitbit'], default='notion',
                        help="Which website to download from")
    return parser.parse_args()


def get_client(website: str, year: str) -> Client:
    match website:
        case 'notion':
            auth_key = os.getenv("NOTION_API_SECRET")
            table_id = os.getenv(f"NOTION_TABLE_{year}_ID")
            return NotionClient(auth_key, table_id)

        case 'fitbit':
            client_id = os.getenv("FITBIT_CLIENT_ID")
            client_secret = os.getenv("FITBIT_CLIENT_SECRET")
            token_file = str(Path(os.getenv("FITBIT_TOKEN_PATH")).expanduser())
            return FitbitClient(client_id=client_id, client_secret=client_secret, token_file=token_file)

        case _:
            raise ValueError(f"Unsupported website: {website}")


def run():
    args = parse_arguments()
    year = args.year
    website = args.website
    load_dotenv()

    data_dir = Path(os.getenv("DATA_DIR")).expanduser()
    raw_data_path = str(data_dir / f"raw/{year}")
    Path(raw_data_path).mkdir(parents=True, exist_ok=True)

    client = get_client(website, year)
    client.download_data(raw_data_path, year)
    print(f"Downloaded to {raw_data_path}")


if __name__ == "__main__":
    run()
