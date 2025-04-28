# interfaces/base_scraper.py

from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, nid: int) -> dict | None:
        """Fetch raw JSON for a given NID."""
        ...
