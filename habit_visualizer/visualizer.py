from abc import ABC

class Visualizer(ABC):
    def __init__(self):
        self.title_color = "white"
        self.label_color = "lightgray"
        self.background_color = "dimgray"
        self.missing_color = "gray"
        self.fontname = "DejaVu Sans"