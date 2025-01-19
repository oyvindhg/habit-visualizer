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
NOTION_TABLE_{year}_ID=your_table_id
```

## Run

### Download data
```
python downloader.py -y 2025
```
`-y` specifies the year of the data, defaulting to `2025`

### Visualize data
```
python visualizer.py -y 2025 -c configs/all-properties-2025.json
```
`-y` specifies the year of the data, defaulting to `2025`

`-c` specifies the path to the config file which specifies the properties to be visualized, defaulting to `config.json`
