from abc import ABC, abstractmethod

class Transformer(ABC):

    @abstractmethod
    def transform(self, original: str, path: str, custom_entry_getter=None) -> None:
        pass
