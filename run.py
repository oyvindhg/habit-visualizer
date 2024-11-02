from habit_visualizer.notion_client import NotionClient
from habit_visualizer.visualizer import plot
from dotenv import load_dotenv
import os
import json
from pathlib import Path

def run():
    client = "json"

    load_dotenv()
    auth_key = os.getenv("NOTION_API_SECRET")
    table_id = os.getenv("NOTION_TABLE_ID")

    match client:
        case "notion":
            data = NotionClient(auth_key).get_data(table_id)
            Path("data").mkdir(exist_ok=True)
            with open("data/habit_data.json", "w") as file:
                json.dump(data, file)
        case "json":
            with open("data/habit_data.json", "r") as file:
                data = json.load(file)
    
    plot_output_path = "data/plot.png"
    plot(plot_output_path)

if __name__ == "__main__":
    run()
