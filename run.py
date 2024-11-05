import os
import json
from pathlib import Path
from dotenv import load_dotenv
from habit_visualizer.notion_client import NotionClient
from habit_visualizer.visualizer import create_heatmap
from habit_visualizer.habit_data_transformer import HabitDataTransformer
from habit_visualizer.custom_entry_getters import get_rich_text_time_as_hours

def run():
    client = "json"
    property_name = "Sleep"
    category_count = 5
    category_labels = ["0-5", "5-6", "6-7", "7-8", "8+"]
    # category_labels = ["No", "Yes"]
    category_limits = [0, 5, 6, 7, 8, 9]
    # category_limits = [0, 0.5, 1]
    color_style = 'RdYlGn' # 'YlOrBr'  # 'PuBu'
    custom_entry_getter = get_rich_text_time_as_hours
    # custom_entry_getter = None

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
        category_limits=category_limits,
        custom_entry_getter=custom_entry_getter
    )
    create_heatmap(habit_data, color_style, f"data/{property_name}.png")

if __name__ == "__main__":
    run()
