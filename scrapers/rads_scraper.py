# scrapers/rads_scraper.py

import os
import json
import logging
from datetime import datetime
import requests
from config.global_settings import RADS_BASE_URL, RADS_HEADERS, RADS_RAW_DIR
from interfaces.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class RadsScraper(BaseScraper):
    def __init__(self, raw_dir: str = None):
        """
        raw_dir: directory where raw JSON files will be stored.
        If not provided, falls back to the global RADS_RAW_DIR.
        """
        super().__init__()
        self.raw_dir = raw_dir if raw_dir is not None else RADS_RAW_DIR

    def scrape(self, nid: str) -> dict | None:
        """
        Fetch provider details for the given NID and write raw JSON to disk.
        """
        url = RADS_BASE_URL.format(nid)
        logger.debug(f"Fetching RADS NID {nid}: GET {url}")
        resp = requests.get(url, headers=RADS_HEADERS)
        resp.raise_for_status()
        data = resp.json()

        # ensure directory exists
        os.makedirs(self.raw_dir, exist_ok=True)

        # save raw JSON with pipeline prefix and date
        timestamp = datetime.now().strftime('%d_%m_%Y')
        filename = f"rads_{nid}_{timestamp}.json"
        filepath = os.path.join(self.raw_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"[RadsScraper] Saved raw JSON for NID {nid} → {filepath}")
        return data
