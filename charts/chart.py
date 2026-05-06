from abc import ABC, abstractmethod

import pandas as pd
import streamlit as st


class Chart(ABC):
    def __init__(self, title: str = None):
        self.title = title

    def render(self, habits: pd.DataFrame, display_config: dict) -> None:
        if self.title:
            st.subheader(self.title)

        self._plot(habits, display_config)

    def _selectable(self, habits: pd.DataFrame, display_config: dict) -> list[str]:
        return [h for h in habits.columns if h in display_config]

    @abstractmethod
    def _plot(self, habits: pd.DataFrame, display_config: dict) -> None:
        pass
