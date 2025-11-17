import json
from dataclasses import dataclass
import requests

from habit_visualizer.client import Client


@dataclass
class NotionClientSettings:
    base_url: str = "https://api.notion.com"
    version: str = "2022-06-28"


class NotionClient(Client):
    def __init__(self, auth_key: str, table_id: str):
        self.settings = NotionClientSettings
        self.auth_key = auth_key
        self.table_id = table_id

    def download_data(self, data_path: str, year: int) -> None:
        path = "/v1/databases/" + self.table_id + "/query"
        url = self.settings.base_url + path

        headers = {
            "Authorization": f"Bearer {self.auth_key}",
            "Notion-Version": self.settings.version,
            "Accept": "application/json"
        }

        body = {
            "sorts": [
                {
                    "property": "Date",
                    "direction": "ascending"
                }
            ]
        }

        data = []
        cursor = None

        while True:
            if cursor:
                body["start_cursor"] = cursor

            response = requests.post(url, headers=headers, json=body, timeout=30)
            response.raise_for_status()

            page_data = response.json()

            data.extend(page_data["results"])
            cursor = page_data.get("next_cursor")

            if not cursor:
                break

        with open(f"{data_path}/notion_data.json", "w", encoding="utf-8") as file:
            json.dump(data, file)
