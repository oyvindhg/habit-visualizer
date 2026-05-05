from abc import ABC, abstractmethod

class Client(ABC):

    @abstractmethod
    def download_data(self, data_path: str, year: int) -> None:
        pass