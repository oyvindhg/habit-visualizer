import calendar

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts.chart import Chart


def _create_figure(habits: pd.DataFrame, habit: str, display_config: dict) -> go.Figure:
    title = display_config[habit]["title"]

    series = habits[habit].dropna()
    df = pd.DataFrame()
    df["value"] = series
    df["day_of_week"] = series.index.dayofweek

    means = df.groupby("day_of_week")["value"].mean().reindex(range(7))
    counts = df.groupby("day_of_week")["value"].count().reindex(range(7), fill_value=0)

    fig = go.Figure(
        data=go.Bar(
            x=list(calendar.day_abbr),
            y=means.values,
            text=[f"n={c}" for c in counts.values],
            textposition="inside",
            insidetextanchor="start",
            marker_color="steelblue",
            hovertemplate="%{x}<br>Avg: %{y:.2f}<br>%{text}<extra></extra>",
        )
    )

    overall = series.mean()
    fig.add_hline(
        y=overall,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Overall avg ({overall:.2f})",
        annotation_position="top right",
    )

    fig.update_layout(
        title=f"{title} by day of week",
        yaxis_title="Average",
        height=400,
        margin=dict(l=60, r=20, t=60, b=40),
    )

    return fig


class DayOfWeekChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        selectable = self._selectable(habits, display_config)
        selected_habit = st.selectbox(
            "Habit",
            selectable,
            format_func=lambda habit: display_config[habit]["title"],
            key="weekday_habit",
        )
        st.plotly_chart(_create_figure(habits, selected_habit, display_config), width="stretch")
