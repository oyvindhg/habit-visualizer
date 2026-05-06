import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from charts.correlations import CorrelationMatrixChart
from charts.heatmap import HeatmapChart
from charts.pair_scatter import PairScatterChart
from charts.time_series import TimeSeriesChart


@st.cache_data
def load_habits() -> pd.DataFrame:
    data_dir = Path(os.getenv("DATA_DIR")).expanduser()
    return pd.read_csv(data_dir / "habits.csv", parse_dates=["date"], index_col="date")


@st.cache_data
def load_display_config() -> dict:
    with open("display.json", "r", encoding="utf-8") as f:
        return {c["property"]: c for c in json.load(f)}


def run() -> None:
    st.set_page_config(page_title="Habit Visualizer", layout="wide")

    load_dotenv()
    habits = load_habits()
    display_config = load_display_config()

    st.title("Habit Visualizer")

    heatmap_tab, timeseries_tab, correlations_tab = st.tabs(
        [
            "Heatmap",
            "Time series",
            "Correlations"
        ]
    )

    with heatmap_tab:
        HeatmapChart().render(habits, display_config)

    with timeseries_tab:
        TimeSeriesChart().render(habits, display_config)

    with correlations_tab:
        CorrelationMatrixChart("Correlation Matrix").render(habits, display_config)
        PairScatterChart("Pair Scatter").render(habits, display_config)


if __name__ == "__main__":
    run()
