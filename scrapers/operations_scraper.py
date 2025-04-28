# scrapers/operations_scraper.py

import os
import json
from datetime import datetime
from utils.request_handler import safe_get
from config.global_settings import BASE_URL, HEADERS, RAW_DIR

from interfaces.base_scraper import BaseScraper

class OperationsScraper(BaseScraper):
    def scrape(self, nid: int) -> dict | None:
        url = BASE_URL.format(nid)
        resp = safe_get(url, HEADERS)
        data = resp.json()
        # save raw for audit
        os.makedirs(RAW_DIR, exist_ok=True)
        fname = os.path.join(RAW_DIR, f"{nid}_{datetime.now():%Y%m%d}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
