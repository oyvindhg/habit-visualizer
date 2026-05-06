import calendar

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
import streamlit as st

from charts.chart import Chart


def _get_colorscale(color_style: str, boundaries: list[float]) -> list:
    n = len(boundaries) - 1
    sample_points = [0.5] if n == 1 else [i / (n - 1) for i in range(n)]
    sampled_colors = pc.sample_colorscale(color_style, sample_points)
    val_min, val_max = boundaries[0], boundaries[-1]
    span = val_max - val_min if val_max > val_min else 1.0

    colorscale = []
    for i in range(n):
        color = sampled_colors[i]
        start = (boundaries[i] - val_min) / span
        end = (boundaries[i + 1] - val_min) / span
        colorscale.append([max(0.0, start), color])
        colorscale.append([min(1.0, end), color])

    return colorscale


def _get_week_number(date: pd.Timestamp) -> int:
    week = date.isocalendar().week
    if date.month == 12 and week == 1:
        return 53
    if date.month == 1 and week >= 52:
        return 0
    return week


def _create_month_separators(df: pd.DataFrame, color: str) -> list[dict]:
    month_ends = df[df.index.is_month_end]
    line = dict(color=color, width=3.5)
    shapes = []
    for month_num, (_, row) in enumerate(month_ends.iterrows()):
        if month_num >= len(month_ends) - 1:
            continue
        week_number = row["week"]
        day_of_week = row["day_of_week"]
        shapes.append(
            # Add upper, right side vertical line
            dict(
                type="line",
                xref="x",
                yref="y",
                x0=week_number + 0.5,
                x1=week_number + 0.5,
                y0=-0.5,
                y1=day_of_week + 0.5,
                line=line
            )
        )
        if day_of_week < 6:
            # Add horizontal line
            shapes.append(
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=week_number - 0.5,
                    x1=week_number + 0.5,
                    y0=day_of_week + 0.5,
                    y1=day_of_week + 0.5,
                    line=line
                )
            )
            # Add lower, left side vertical line
            shapes.append(
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=week_number - 0.5,
                    x1=week_number - 0.5,
                    y0=day_of_week + 0.5,
                    y1=6.5,
                    line=line
                )
            )
    return shapes


def _create_figure(values: pd.Series, year: int, display_config: dict) -> go.Figure:
    all_dates = pd.date_range(f"{year}-01-01", f"{year}-12-31")
    df = pd.DataFrame(index=all_dates)
    df["value"] = values.reindex(all_dates)
    df["day_of_week"] = df.index.dayofweek
    df["week"] = [_get_week_number(d) for d in df.index]
    df["date_str"] = df.index.strftime("%Y-%m-%d")

    grid = df.pivot_table(index="day_of_week", columns="week", values="value", aggfunc="first")
    date_grid = df.pivot_table(index="day_of_week", columns="week", values="date_str", aggfunc="first")

    boundaries = display_config["boundaries"]
    labels = display_config["labels"]
    colorscale = _get_colorscale(display_config["color_style"], boundaries)
    color_ticks = [(boundaries[i] + boundaries[i + 1]) / 2 for i in range(len(boundaries) - 1)]

    hover_template = "%{customdata}<br>Value: %{z}<extra></extra>"

    fig = go.Figure(
        data=go.Heatmap(
            z=grid.values,
            x=grid.columns.tolist(),
            y=list(calendar.day_abbr),
            customdata=date_grid.values,
            colorscale=colorscale,
            zmin=boundaries[0],
            zmax=boundaries[-1],
            xgap=2,
            ygap=2,
            hovertemplate=hover_template,
            colorbar=dict(
                orientation="h",
                tickvals=color_ticks,
                ticktext=labels,
                thickness=12,
                len=0.6,
                y=-0.5
            )
        )
    )

    month_starts = []
    for month_num in range(1, 13):
        first_of_month = pd.Timestamp(year=year, month=month_num, day=1)
        month_starts.append((month_num, _get_week_number(first_of_month)))

    background_color = "rgba(0,0,0,0)"  # transparent
    separator_color = "rgba(0,0,0,1)"  # black

    fig.update_layout(
        title=dict(
            text=display_config["title"],
            x=0.5,
            xanchor="center",
            y=0.95
        ),
        height=380,
        width=1300,
        margin=dict(
            l=70,
            r=30,
            t=80,
            b=100
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=[w + 1 for _, w in month_starts],
            ticktext=[calendar.month_abbr[m] for m, _ in month_starts],
            side="top",
            showgrid=False
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False
        ),
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        shapes=_create_month_separators(df, separator_color)
    )

    return fig


class HeatmapChart(Chart):
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        controls, chart = st.columns([1, 4])
        with controls:
            years = sorted(habits.index.year.unique())
            year = st.selectbox("Year", years, index=len(years) - 1)
            selectable = self._selectable(habits, display_config)
            selected_habit = st.selectbox(
                "Habit",
                selectable,
                format_func=lambda habit: display_config[habit]["title"],
            )

        with chart:
            config = display_config[selected_habit]
            values = habits[habits.index.year == year][selected_habit]
            st.plotly_chart(_create_figure(values, year, config), width="content")
