from typing import Any
from dataclasses import dataclass
import requests

@dataclass
class NotionClientSettings:
    base_url: str = "https://api.notion.com"
    version: str = "2022-06-28"


class NotionClient:
    def __init__(self, auth_key: str):
        self.settings = NotionClientSettings
        self.auth_key = auth_key

    def get_data(self, table_id: str) -> dict[str, Any]:
        path = "/v1/databases/" + table_id + "/query"
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

            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()

            page_data = response.json()

            data.extend(page_data["results"])
            cursor = page_data.get("next_cursor")

            if not cursor:
                break

        return data
