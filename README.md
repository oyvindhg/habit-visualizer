# Habit Visualizer

A visualization tool for Fitbit data and habit tracking in Notion


## Requirements
- Python (built with 3.10)
- Notion account with a database tracking daily habits

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
python download.py -y 2025 -s fitbit
```
`-y` specifies the year of the data, defaulting to `2025`

`-s` specifies the source to download data from, defaulting to `notion`. Only `notion` and `fitbit` are valid options.

### Transform data
```
python transform.py -y 2025 -c configs/all-properties-2025.json
```
`-y` specifies the year of the data, defaulting to `2025`

`-c` specifies the path to the config file which specifies the properties to be transformed, defaulting to `config.json`


### Visualize data
```
python visualize.py -y 2025 -c configs/all-properties-2025.json
```
`-y` specifies the year of the data, defaulting to `2025`

`-c` specifies the path to the config file which specifies the properties to be visualized, defaulting to `config.json`

#### Example

Running the visualizing tool will produce a heatmap of all habits as specified in the config file. The following example is showing a daily overview of whether I studied Japanese or not in 2024.

<img src="https://github.com/user-attachments/assets/b291f9dc-f6fb-4848-8c6e-9ef3a3cf047f" alt="Japanese study habit" width="100" />
