import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from charts.conditional import ConditionalComparisonChart
from charts.correlations import CorrelationMatrixChart
from charts.heatmap import HeatmapChart
from charts.pair_scatter import PairScatterChart
from charts.time_series import TimeSeriesChart
from charts.weekday import DayOfWeekChart


@st.cache_data
def load_habits(data_dir: Path) -> pd.DataFrame:
    return pd.read_csv(data_dir / "habits.csv", parse_dates=["date"], index_col="date")


@st.cache_data
def load_display_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return {c["property"]: c for c in json.load(f)}


def get_display_options(data_dir: Path) -> dict[str, Path]:
    displays_dir = data_dir / "displays"
    if not displays_dir.exists():
        st.error(f"No `displays/` directory found in `{data_dir}`. Create it and add at least one display config JSON file.")
        st.stop()
    options = {p.stem: p for p in sorted(displays_dir.glob("*.json"))}
    if not options:
        st.error(f"No JSON files found in `{displays_dir}`. Add at least one display config JSON file.")
        st.stop()
    return options


def run() -> None:
    st.set_page_config(page_title="Habit Visualizer", layout="wide")

    load_dotenv()
    data_dir = Path(os.getenv("DATA_DIR")).expanduser()
    habits = load_habits(data_dir)

    title, toggle = st.columns([6, 1])
    with title:
        st.title("Habit Visualizer")
    with toggle:
        st.toggle("Mobile view", key="mobile")

    display_options = get_display_options(data_dir)
    selected = st.sidebar.selectbox("View", list(display_options.keys()))
    display_config = load_display_config(display_options[selected])
    heatmap_tab, timeseries_tab, correlations_tab, patterns_tab = st.tabs(
        [
            "Heatmap",
            "Time series",
            "Correlations",
            "Patterns"
        ]
    )

    with heatmap_tab:
        HeatmapChart().render(habits, display_config)

    with timeseries_tab:
        TimeSeriesChart().render(habits, display_config)

    with correlations_tab:
        CorrelationMatrixChart("Correlation Matrix").render(habits, display_config)
        PairScatterChart("Pair Scatter").render(habits, display_config)

    with patterns_tab:
        DayOfWeekChart("Day of Week").render(habits, display_config)
        ConditionalComparisonChart("Conditional Comparison").render(habits, display_config)


if __name__ == "__main__":
    run()
