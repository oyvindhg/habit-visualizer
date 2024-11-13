import os
import json
from pathlib import Path
from dotenv import load_dotenv
from habit_visualizer.notion_client import NotionClient


def run():
    load_dotenv()
    auth_key = os.getenv("NOTION_API_SECRET")
    table_id = os.getenv("NOTION_TABLE_ID")

    json_data = NotionClient(auth_key).get_data(table_id)

    Path("data").mkdir(exist_ok=True)
    with open("data/habit_data.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file)


if __name__ == "__main__":
    run()