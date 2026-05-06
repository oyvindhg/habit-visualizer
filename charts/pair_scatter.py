import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts.chart import Chart


def _create_figure(data: pd.DataFrame, x_col: str, y_col: str, display_config: dict) -> go.Figure:
    pair = data[[x_col, y_col]].dropna()
    x_title = display_config[x_col]["title"]
    y_title = display_config[y_col]["title"]

    counts = pair.groupby([x_col, y_col]).size().reset_index(name="count")
    max_count = counts["count"].max()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=counts[x_col],
            y=counts[y_col],
            mode="markers",
            marker=dict(
                size=counts["count"],
                sizemode="area",
                sizeref=2.0 * max_count / (50 ** 2),
                sizemin=4,
                color="steelblue",
            ),
            customdata=counts["count"],
            name="Days",
            hovertemplate=f"{x_title}: %{{x}}<br>{y_title}: %{{y}}<br>Days: %{{customdata}}<extra></extra>",
        )
    )

    can_fit = len(pair) >= 2 and pair[x_col].nunique() >= 2
    if can_fit:
        a, b = np.polyfit(pair[x_col], pair[y_col], 1)
        x = np.array([pair[x_col].min(), pair[x_col].max()])
        fig.add_trace(
            go.Scatter(
                x=x,
                y=a * x + b,
                mode="lines",
                line=dict(color="firebrick", dash="dash"),
                name=f"Trend (r={pair[x_col].corr(pair[y_col]):.2f}, n={len(pair)})",
            )
        )

    fig.update_layout(
        height=500,
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode="closest",
        margin=dict(l=60, r=20, t=40, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1, x=0),
    )

    return fig


class PairScatterChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        selectable = self._selectable(habits, display_config)
        habit_titles = lambda habit: display_config[habit]["title"]
        default_y = next(
            (habit for habit, cfg in display_config.items() if cfg.get("default_y") and habit in selectable),
            None
        )

        col_x, col_y = st.columns(2)
        with col_y:
            y_index = selectable.index(default_y) if default_y in selectable else 0
            y_habit = st.selectbox(
                "Y axis",
                selectable,
                index=y_index,
                format_func=habit_titles,
                key="y_habit"
            )
        with col_x:
            x_options = [h for h in selectable if h != y_habit]
            x_habit = st.selectbox(
                "X axis",
                x_options,
                format_func=habit_titles,
                key="x_habit"
            )

        st.plotly_chart(_create_figure(habits, x_habit, y_habit, display_config), width="stretch")
