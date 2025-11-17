from dataclasses import dataclass
import json
import os
import time
from datetime import datetime
from urllib.parse import urlencode
import base64

import requests

from habit_visualizer.client import Client


@dataclass
class FitbitClientSettings:
    redirect_url: str = "https://example.com"
    auth_base_url: str = "https://www.fitbit.com/oauth2/authorize"
    token_url: str = "https://api.fitbit.com/oauth2/token"
    scope: str = "activity heartrate location nutrition social weight sleep profile"
    base_url: str = "https://api.fitbit.com/1.2/user/-"

class FitbitClient(Client):
    def __init__(self, client_id: str, client_secret: str, token_file: str):
        self.settings = FitbitClientSettings
        self.client_id = client_id
        self.credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        if os.path.exists(token_file):
            self.access_token = self._load_token(token_file)
        else:
            self.access_token = self._authorize(token_file)
        
    def _authorize(self, token_file: str):
        redirect_url = self.settings.redirect_url
        auth_base_url = self.settings.auth_base_url
        auth_settings = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_url,
            "scope": self.settings.scope
        }
        auth_url = f"{auth_base_url}?{urlencode(auth_settings)}"
        print(f"Authentication url: {auth_url}")
        authorization_code = input("Login to Fitbit with the above URL, and paste the authorization code from the redirection URL:")

        token_url = self.settings.token_url
        headers = {
            "Authorization": f"Basic {self.credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth_body = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": self.client_id,
            "redirect_uri": redirect_url
        }

        response = requests.post(token_url, headers=headers, data=auth_body, timeout=30)

        response.raise_for_status()
        tokens = response.json()
        self._save_tokens(tokens=tokens, token_file = token_file)
        return tokens["access_token"]

    def _save_tokens(self, tokens: str, token_file: str):
        with open(token_file, "w", encoding="utf-8") as file:
            json.dump(tokens, file)
    
    def _refresh_tokens(self, refresh_token, token_file: str) -> str:
        print("Refreshing Fitbit token...")

        headers = {
            "Authorization": f"Basic {self.credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id
        }

        response = requests.post(self.settings.token_url, headers=headers, data=refresh_data, timeout=30)
        response.raise_for_status()

        tokens = response.json()

        self._save_tokens(tokens=tokens, token_file=token_file)
        print("Token refreshed")
        return tokens["access_token"]

    def _load_token(self, token_file: str) -> str:
        file_modified_time = os.path.getmtime(token_file)
        with open(token_file, "r", encoding="utf-8") as file:
            tokens = json.load(file)
        
        if time.time() > file_modified_time + tokens["expires_in"]:
            return self._refresh_tokens(refresh_token = tokens["refresh_token"], token_file=token_file)
        return tokens["access_token"]

    def download_data(self, data_path: str, year: int) -> None:
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        # Weight data
        label = "weight"
        url = f"{self.settings.base_url}/body/{label}/date/{year}-01-01/{year}-12-31.json"
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
        with open(f"{data_path}/fitbit_{label}.json", "w", encoding="utf-8") as file:
            json.dump(data, file)

        # Step count data
        label = "steps"
        url = f"{self.settings.base_url}/activities/{label}/date/{year}-01-01/{year}-12-31.json"
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
        with open(f"{data_path}/fitbit_{label}.json", "w", encoding="utf-8") as file:
            json.dump(data, file)

        # Sleep data
        label = "sleep"
        full_year_sleep_data = []
        for quarter in [1, 2, 3, 4]:
            match quarter:
                case 1:
                    dates = f"{year}-01-01/{year}-03-31"
                case 2:
                    dates = f"{year}-04-01/{year}-06-30"
                case 3:
                    dates = f"{year}-07-01/{year}-09-30"
                case _:
                    dates = f"{year}-10-01/{year}-12-31"
            url = f"{self.settings.base_url}/{label}/date/{dates}.json"
            response = requests.get(url, headers=headers, timeout=30)
            quarter_sleep_data = response.json()
            quarter_sleep_entries = quarter_sleep_data.get(f"{label}", [])
            quarter_sleep_entries.sort(key=lambda x: datetime.fromisoformat(x["dateOfSleep"]))
            full_year_sleep_data.extend(quarter_sleep_entries)
        fitbit_sleep_data = {f"{label}": full_year_sleep_data}
        with open(f"{data_path}/fitbit_{label}.json", "w", encoding="utf-8") as file:
            json.dump(fitbit_sleep_data, file)
