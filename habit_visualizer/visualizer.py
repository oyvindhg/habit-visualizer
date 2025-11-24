from abc import ABC, abstractmethod
from matplotlib import pyplot as plt

from habit_visualizer.habit_data import HabitData


class Visualizer(ABC):
    def __init__(self):
        self.title_color = "white"
        self.label_color = "lightgray"
        self.background_color = "dimgray"
        self.missing_color = "gray"
        self.fontname = "DejaVu Sans"

    def visualize(self, habit_data: HabitData, color_style: str, output_path: str) -> None:
        self._draw(habit_data, color_style)
        plt.savefig(output_path)
        plt.close()

    @abstractmethod
    def _draw(self, habit_data: HabitData, color_style: str) -> None:
        pass
