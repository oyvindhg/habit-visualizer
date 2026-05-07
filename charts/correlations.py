import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts.chart import Chart


def _create_figure(habits: pd.DataFrame, display_config: dict, is_mobile: bool) -> go.Figure:
    corr = habits.corr()
    labels = [display_config[habit]["title"] for habit in corr.columns]

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=labels,
            y=labels,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            text=[[f"{v:.2f}" if not np.isnan(v) else "" for v in row] for row in corr.values],
            texttemplate="%{text}",
            textfont=dict(size=10),
            hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>",
            colorbar=dict(
                title=dict(text="" if is_mobile else "r"),
                thickness=12,
                orientation="h" if is_mobile else "v",
                y=1.08 if is_mobile else 0.5,
                yanchor="bottom" if is_mobile else "middle",
                len=1.0,
            ),
        )
    )

    fig.update_layout(
        height=400 if is_mobile else 600,
        margin=dict(l=60 if is_mobile else 120, r=20, t=20, b=120),
        xaxis=dict(side="bottom", tickangle=-45 if is_mobile else -30),
        yaxis=dict(autorange="reversed", tickangle=45 if is_mobile else 0)
    )

    return fig


class CorrelationMatrixChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        selectable = self._selectable(habits, display_config)
        selected = st.multiselect(
            "Habits",
            selectable,
            default=selectable[:8],
            format_func=lambda h: display_config[h]["title"],
        )
        if not selected:
            return
        is_mobile = st.session_state.get("mobile")
        st.plotly_chart(_create_figure(habits[selected], display_config, is_mobile), width="stretch")
