# Habit Visualizer

A visualization tool for habit tracking in Notion


## Requirements
- Python (built with 3.10)
- Notion account

## Setup
Setup a virtual environment:

```
python -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```
python -m pip install -r requirements.txt
```

Set the Notion API secret and the database table ID as environment variables, or in a `.env` file on the project root level:

```
NOTION_API_SECRET=your_api_secret
NOTION_TABLE_ID=your_table_id
```

## Run

Run the visualizer:
```
python run.py
```
