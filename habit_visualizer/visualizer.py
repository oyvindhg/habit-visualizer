import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from habit_visualizer.habit_data import HabitData


def create_heatmap(habit_data: HabitData, color_style: str, output_path: str):
    dates = pd.date_range(f"{habit_data.year}-01-01", f"{habit_data.year}-12-31")
    df = pd.DataFrame({"date": dates, "value": habit_data.data})
    
    df["day_of_week"] = df["date"].dt.dayofweek

    # Some days can be counted in 'week 1' of the next year, so we change those to week 53 of the current year
    df["week"] = df["date"].apply(lambda x: x.isocalendar().week if x.month != 12 or x.isocalendar().week != 1 else 53)

    plt.figure(figsize=(5,20))
    plt.title(f"{habit_data.title} in {habit_data.year}", pad=30)

    # Draw separation lines between months
    month_end_dates = df[df["date"].dt.is_month_end]
    for i, (_, row) in enumerate(month_end_dates.iterrows()):
        if i < len(month_end_dates) - 1:
            week = row["week"]
            day_of_week = row["day_of_week"]
            plt.plot([-0.5, day_of_week + 0.5], [week - 0.5, week - 0.5], color="black", linewidth=3)
            plt.plot([day_of_week + 0.5, 6.5], [week - 1.5, week - 1.5], color="black", linewidth=3)
            plt.plot([day_of_week + 0.5, day_of_week + 0.5], [week - 1.5, week - 0.5], color="black", linewidth=3)

    # Remove border around the plot
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["left"].set_visible(False)
    plt.gca().spines["bottom"].set_visible(False)

    # Configure axis ticks
    plt.xticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    plt.gca().xaxis.tick_top()
    month_starts = df[df["date"].dt.is_month_start]
    month_weeks = month_starts.groupby(month_starts["date"].dt.month).apply(
        lambda x: x["week"].iloc[0] + (1 if x["date"].dt.weekday.iloc[0] != 0 else 0)
    )
    plt.yticks(month_weeks, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    plt.tick_params(axis='both', which='both', length=0)

    # Find calendar start and end offsets and create heatmap
    start_day_of_week = df["day_of_week"].iloc[0]
    end_day_of_week = df["day_of_week"].iloc[-1]
    first_week_empty = [np.nan] * start_day_of_week
    last_week_empty = [np.nan] * (6 - end_day_of_week)

    weekly_data = (
        df.groupby("week")["value"]
        .apply(lambda x: first_week_empty + list(x) if x.name == df["week"].iloc[0] else (list(x) + last_week_empty if x.name == df["week"].iloc[-1] else list(x)))
        .apply(lambda x: x[:7] if len(x) > 7 else x)
    )

    plot_data = pd.DataFrame(weekly_data.tolist())

    # Define heatmap colors and color labels
    colormap = plt.cm.get_cmap(color_style, habit_data.category_count)
    colormap.set_bad(color='white')
    boundaries = habit_data.category_limits
    norm = mcolors.BoundaryNorm(boundaries, colormap.N, clip=True)
    plt.imshow(plot_data, cmap=colormap, norm=norm, aspect="auto")

    color_ticks = [(boundaries[i] + boundaries[i+1]) / 2 for i in range(len(boundaries) - 1)]
    colorbar = plt.colorbar(ticks=color_ticks, shrink=0.2, aspect=10)
    colorbar.ax.set_yticklabels(habit_data.category_labels)
    colorbar.ax.tick_params(axis='y', length=0)

    plt.savefig(output_path)
