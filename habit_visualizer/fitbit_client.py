from dataclasses import dataclass
import json
import os
import time
from urllib.parse import urlencode
import base64

import requests

@dataclass
class FitbitClientSettings:
    redirect_url: str = "https://example.com"
    auth_base_url: str = "https://www.fitbit.com/oauth2/authorize"
    token_url: str = "https://api.fitbit.com/oauth2/token"
    scope: str = "activity heartrate location nutrition social weight sleep profile"

class FitbitClient:
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
        return tokens["access_token"]

    def _load_token(self, token_file: str) -> str:
        file_modified_time = os.path.getmtime(token_file)
        with open(token_file, "r", encoding="utf-8") as file:
            tokens = json.load(file)
        
        if time.time() > file_modified_time + tokens["expires_in"]:
            print("TOKEN EXPIRED - REFRESH")  # TODO: Test that this works
            return self._refresh_tokens(refresh_token = tokens["refresh_token"], token_file=token_file)
        return tokens["access_token"]
        

    def download_data(self, data_path: str) -> None:

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        for quarter in range(1, 5):

            match quarter:
                case 1:
                    dates = "2025-01-01/2025-03-31"
                case 2:
                    dates = "2025-04-01/2025-06-30"
                case 3:
                    dates = "2025-07-01/2025-09-30"
                case _:
                    dates = "2025-10-01/2025-12-31"

            url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{dates}.json"

            response = requests.get(url, headers=headers, timeout=30)
            data = response.json()

            with open(f"{data_path}/fitbit_sleep_q{quarter}.json", "w", encoding="utf-8") as file:
                json.dump(data, file)
