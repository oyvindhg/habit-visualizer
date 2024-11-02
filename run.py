import os
import json
from pathlib import Path
from dotenv import load_dotenv
from habit_visualizer.notion_client import NotionClient
from habit_visualizer.visualizer import create_heatmap
from habit_visualizer.habit_data_transformer import HabitDataTransformer

def run():
    client = "json"
    property_name = "Drinks"
    category_count = 5
    category_labels = ["0", "1-2", "3-5", "6+"]
    category_limits = [0, 0.5, 2.5, 5.5, 6]
    color_style = 'YlOrBr'  # PuBu

    load_dotenv()
    auth_key = os.getenv("NOTION_API_SECRET")
    table_id = os.getenv("NOTION_TABLE_ID")

    match client:
        case "notion":
            json_data = NotionClient(auth_key).get_data(table_id)
            Path("data").mkdir(exist_ok=True)
            with open("data/habit_data.json", "w", encoding="utf-8") as file:
                json.dump(json_data, file)
        case "json":
            with open("data/habit_data.json", "r", encoding="utf-8") as file:
                json_data = json.load(file)
    
    habit_data_transformer = HabitDataTransformer(json_data)
    habit_data = habit_data_transformer.validate_and_transform(
        property_name, 
        category_count=category_count, 
        category_labels=category_labels,
        category_limits=category_limits
    )
    create_heatmap(habit_data, color_style, f"data/{property_name}.png")

if __name__ == "__main__":
    run()
