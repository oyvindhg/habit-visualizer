import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from charts.chart import Chart


def _create_figure(data: pd.DataFrame, display_config: dict) -> go.Figure:
    n = len(data.columns)
    titles = [display_config[habit]["title"] for habit in data.columns]

    fig = make_subplots(
        rows=n,
        cols=1,
        shared_xaxes=True,
        subplot_titles=titles,
        vertical_spacing=0.04
    )

    for row, habit in enumerate(data.columns, start=1):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[habit],
                mode="lines+markers",
                name=habit,
                marker=dict(size=4)
            ),
            row=row,
            col=1
        )

    fig.update_layout(
        height=max(220 * n, 400),
        showlegend=False,
        hovermode="x unified",
        margin=dict(l=40, r=20, t=40, b=40),
    )

    return fig


class TimeSeriesChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        controls, chart = st.columns([1, 4])
        with controls:
            min_date = habits.index.min().date()
            max_date = habits.index.max().date()
            date_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            selectable = self._selectable(habits, display_config)
            selected = st.multiselect(
                "Habits",
                options=selectable,
                default=selectable[:2],
            )
            aggregation = st.radio(
                "Aggregation",
                [
                    "Daily",
                    "7-day rolling average",
                    "30-day rolling average",
                    "Monthly average",
                    "Monthly sum"
                ]
            )

        with chart:
            if len(date_range) != 2 or not selected:
                st.info("Pick a date range and at least one habit.")
                return

            start, end = date_range
            window = habits.loc[str(start):str(end), selected]
            match aggregation:
                case "7-day rolling average":
                    window = window.rolling(window=7, min_periods=1).mean()
                case "30-day rolling average":
                    window = window.rolling(window=30, min_periods=1).mean()
                case "Monthly average":
                    window = window.resample("MS").mean()
                case "Monthly sum":
                    window = window.resample("MS").sum()

            st.plotly_chart(_create_figure(window, display_config), width="stretch")
