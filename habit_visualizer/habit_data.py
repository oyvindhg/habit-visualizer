from dataclasses import dataclass
import numpy as np

@dataclass
class HabitData:
    title: str
    year: int
    category_count: int
    category_limits: list[int]
    category_labels: list[str]
    data: np.ndarray
