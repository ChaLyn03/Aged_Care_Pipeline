# src/aged_care_pipeline/interfaces/base_scraper.py

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, nid: int) -> dict | None:
        """Fetch raw JSON for a given NID."""
        ...

    def bulk(self, nids: list[int]) -> None:
        """
        Default bulk‐scrape: iterate scrape() over each NID.
        """
        for nid in nids:
            self.scrape(nid)
