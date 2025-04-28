# interfaces/base_parser.py

from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw: dict) -> list[dict]:
        """Turn raw JSON into a list of flat records."""
        ...
