import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts.chart import Chart


def _create_figure(habits: pd.DataFrame, display_config: dict) -> go.Figure:
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
            colorbar=dict(title="r", thickness=12)
        )
    )

    fig.update_layout(
        height=600,
        margin=dict(l=120, r=20, t=20, b=120),
        xaxis=dict(side="bottom", tickangle=-30),
        yaxis=dict(autorange="reversed")
    )

    return fig


class CorrelationMatrixChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        selectable = self._selectable(habits, display_config)
        st.plotly_chart(_create_figure(habits[selectable], display_config), width="stretch")
