import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from charts.chart import Chart


def _is_binary(series: pd.Series) -> bool:
    unique = set(series.dropna().unique())
    return unique.issubset({0, 1})


def _get_binary_columns(data: pd.DataFrame) -> list[str]:
    return [habit for habit in data.columns if _is_binary(data[habit])]


def _create_figure(habits: pd.DataFrame, habit: str, display_config: dict, is_mobile: bool) -> go.Figure:
    other_habits = [h for h in habits.columns if h != habit]
    condition_title = display_config[habit]["title"]

    on_days = habits[habits[habit] == 1]
    off_days = habits[habits[habit] == 0]
    on_day_count = len(on_days)
    off_day_count = len(off_days)

    on_day_means = on_days[other_habits].mean()
    off_day_means = off_days[other_habits].mean()
    titles = [display_config[h]["title"] for h in other_habits]

    col_count = 2 if is_mobile else 3
    row_count = math.ceil(len(other_habits) / col_count)

    fig = make_subplots(
        rows=row_count,
        cols=col_count,
        subplot_titles=titles,
        vertical_spacing=min(0.12, 0.8 / row_count),
    )

    for i, other_habit in enumerate(other_habits):
        row = i // col_count + 1
        col = i % col_count + 1
        fig.add_trace(
            go.Bar(
                x=["Yes", "No"],
                y=[on_day_means[other_habit], off_day_means[other_habit]],
                marker_color=["seagreen", "lightcoral"],
                text=[f"{on_day_means[other_habit]:.2f}", f"{off_day_means[other_habit]:.2f}"],
                textposition="outside",
                hovertemplate="<extra></extra>",
                showlegend=False,
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        title=f"Habit averages on '{condition_title}' (yes n={on_day_count}, no n={off_day_count})",
        height=260 * row_count + 80,
        margin=dict(l=40, r=20, t=80, b=40),
    )

    return fig

class ConditionalComparisonChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        selectable = habits[self._selectable(habits, display_config)]
        binary_habits = _get_binary_columns(selectable)
        if not binary_habits:
            st.info("No binary habits available for conditional comparison.")
            return

        selected_habit = st.selectbox(
            "Condition (binary habit)",
            binary_habits,
            format_func=lambda habit: display_config[habit]["title"],
            key="condition_habit",
        )
        is_mobile = st.session_state.get("mobile")
        st.plotly_chart(_create_figure(selectable, selected_habit, display_config, is_mobile), width="stretch")
