import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
from habit_visualizer.habit_data import HabitData

class HeatmapVisualizer:
    def visualize(self, habit_data: HabitData, color_style: str, output_path: str):
        title_color = "white"
        label_color = "lightgray"
        background_color = "dimgray"
        missing_color = "gray"
        fontname = "DejaVu Sans"

        dates = pd.date_range(f"{habit_data.year}-01-01", f"{habit_data.year}-12-31")
        df = pd.DataFrame({"date": dates, "value": habit_data.data})

        df["day_of_week"] = df["date"].dt.dayofweek

        # Some days can be counted in 'week 1' of the next year, so we change those to week 53 of the current year
        df["week"] = df["date"].apply(lambda x: x.isocalendar().week if x.month != 12 or x.isocalendar().week != 1 else 53)

        scaler = 0.5
        fig = plt.figure(figsize=(7 * scaler, 30 * scaler))
        fig.patch.set_facecolor(background_color)
        plt.subplots_adjust(top=0.91, bottom=-0.1, left=0.25, right=0.76)
        ax = plt.gca()
        ax.text(0.5, 1.07, f"{habit_data.year}", transform=ax.transAxes, fontsize=10, fontname=fontname, color=title_color, ha='center')
        ax.text(0.5, 1.05, f"{habit_data.title.upper()}", transform=ax.transAxes, fontsize=12, fontname=fontname, color=title_color, weight='bold', ha='center')

        # Draw separation lines between months
        month_end_dates = df[df["date"].dt.is_month_end]
        linewidth = 5
        for i, (_, row) in enumerate(month_end_dates.iterrows()):
            if i < len(month_end_dates) - 1:
                week = row["week"]
                day_of_week = row["day_of_week"]
                plt.plot([-0.5, day_of_week + 0.5], [week - 0.5, week - 0.5], color=background_color, linewidth=linewidth)
                plt.plot([day_of_week + 0.5, 6.5], [week - 1.5, week - 1.5], color=background_color, linewidth=linewidth)
                if day_of_week < 6:
                    plt.plot([day_of_week + 0.5, day_of_week + 0.5], [week - 1.5, week - 0.5], color=background_color, linewidth=linewidth)

        # Remove border around the plot
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False)
        plt.gca().spines["left"].set_visible(False)
        plt.gca().spines["bottom"].set_visible(False)

        # Configure axis ticks
        plt.xticks(range(7), ["M", "T", "W", "T", "F", "S", "S"], fontname=fontname, color=label_color, weight='bold')
        plt.gca().xaxis.tick_top()
        month_starts = df[df["date"].dt.is_month_start]
        month_weeks = month_starts.groupby(month_starts["date"].dt.month).apply(
            lambda x: x["week"].iloc[0] + (1 if x["date"].dt.weekday.iloc[0] != 0 else 0)
        )
        plt.yticks(month_weeks, ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], fontname=fontname, color=label_color, weight='bold')
        plt.tick_params(axis='both', which='both', length=0)

        # Find calendar start and end offsets and create heatmap
        start_day_of_week = df["day_of_week"].iloc[0]
        end_day_of_week = df["day_of_week"].iloc[-1]
        first_week_empty = [-999] * start_day_of_week
        last_week_empty = [-999] * (6 - end_day_of_week)

        weekly_data = (
            df.groupby("week")["value"]
            .apply(lambda x: first_week_empty + list(x) if x.name == df["week"].iloc[0] else (list(x) + last_week_empty if x.name == df["week"].iloc[-1] else list(x)))
            .apply(lambda x: x[:7] if len(x) > 7 else x)
        )

        plot_data = pd.DataFrame(weekly_data.tolist())

        # Define heatmap colors and color labels
        boundaries = habit_data.boundaries
        colormap = plt.cm.get_cmap(color_style, len(boundaries))
        colormap.set_bad(color=missing_color)
        colormap.set_under(color=background_color)
        norm = mcolors.BoundaryNorm(boundaries, colormap.N, clip=False)
        plt.imshow(plot_data, cmap=colormap, norm=norm, aspect="auto")

        color_ticks = [(boundaries[i] + boundaries[i+1]) / 2 for i in range(len(boundaries) - 1)]
        colorbar = plt.colorbar(orientation="horizontal", ticks=color_ticks, pad=0.02)
        colorbar.ax.set_xticklabels(habit_data.labels, fontname=fontname, color=label_color)
        colorbar.ax.tick_params(axis='both', which='both', length=0)
        colorbar.outline.set_visible(False)

        plt.savefig(output_path)
