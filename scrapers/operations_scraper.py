# scrapers/operations_scraper.py

import os
import json
import logging
from datetime import datetime
from utils.request_handler import safe_get
from config.global_settings import OPERATIONS_BASE_URL, OPERATIONS_HEADERS, RAW_DIR
from interfaces.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class OperationsScraper(BaseScraper):
    def __init__(self, raw_dir: str = None):
        """
        raw_dir: directory where raw JSON files will be stored.
        If not provided, falls back to BASE RAW_DIR from settings.
        """
        super().__init__()
        self.raw_dir = raw_dir if raw_dir is not None else RAW_DIR

    def scrape(self, nid: int) -> dict | None:
        url = OPERATIONS_BASE_URL.format(nid)
        logger.debug(f"Starting scrape for NID {nid}: GET {url}")
        resp = safe_get(url, OPERATIONS_HEADERS)
        data = resp.json()

        # ensure directory exists
        os.makedirs(self.raw_dir, exist_ok=True)

        # save raw JSON with pipeline prefix
        timestamp = datetime.now().strftime('%d_%m_%Y')
        filename = f"operations_{nid}_{timestamp}.json"
        filepath = os.path.join(self.raw_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"[Scraper] Saved raw JSON for NID {nid} → {filepath}")

        return data
