# Habit Visualizer

A visualization tool for Fitbit data and habit tracking in Notion


## Requirements
- Python `3.13`
- Notion account with a database tracking daily habits
- Fitbit account

## Setup

### Python setup
Setup a virtual environment:

```
python -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```
python -m pip install -r requirements.txt
```

### Notion setup
The Notion database needs a field called `Date` which is of the `Date` type. The other fields are specified in a config file when running the visualization tool.

Setup a Notion integration and get the API secrets and database ID as explained in [https://developers.notion.com/docs/create-a-notion-integration](https://developers.notion.com/docs/create-a-notion-integration).

Set the API secret and the database ID as environment variables, or in a `.env` file on the project root level:

```
NOTION_API_SECRET=your_api_secret
NOTION_TABLE_{year}_ID=your_database_id
```

### Fitbit setup
Register a new application at [https://dev.fitbit.com/apps/new](https://dev.fitbit.com/apps/new). The application needs to be of "Server" type.

After creating the application, copy the `OAuth 2.0 Client ID` and `Client Secret` as environment variables, or into a `.env` file on the project root level:

```
FITBIT_CLIENT_ID=your_oath_2.0_client_id
FITBIT_CLIENT_SECRET=your_client_secret
```


## Run

### Download data
```
python download.py -y 2024 -w fitbit
```
`-y` specifies the year of the data, defaulting to the current year

`-w` specifies the website to download data from, defaulting to `notion`. Only `notion` and `fitbit` are valid options.

### Transform data
```
python transform.py -y 2025 -c configs/my-source-config.json
```
`-y` specifies the year of the data, defaulting to the current year

Note that a `sources.json` file must be present in the `DATA_DIR` directory.

### Visualize data
```
streamlit run visualize.py
```

Note that a directory `DATA_DIR/displays` must exist with at least one `*.json` display config file inside.
