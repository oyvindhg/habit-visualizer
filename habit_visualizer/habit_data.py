from dataclasses import dataclass
import numpy as np

@dataclass
class HabitData:
    title: str
    year: int
    boundaries: list[int]
    labels: list[str]
    data: np.ndarray
