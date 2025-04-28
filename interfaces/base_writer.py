# interfaces/base_writer.py

from abc import ABC, abstractmethod

class BaseWriter(ABC):
    @abstractmethod
    def write(self, records: list[dict], filename: str) -> None:
        """Persist parsed records to storage (CSV, DB, etc.)."""
        ...
