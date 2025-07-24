# scrapers/operations_scraper.py

import json
import logging
import os
from datetime import datetime
from pathlib import Path

import structlog

from aged_care_pipeline.config.global_settings import (
    OPERATIONS_BASE_URL,
    OPERATIONS_HEADERS,
    RAW_DIR,
)
from aged_care_pipeline.interfaces.base_scraper import BaseScraper

try:
    safe_get  # type: ignore[name-defined]
except NameError:  # noqa: F821 - allow external patch before reload
    from aged_care_pipeline.utils.request_handler import safe_get

log = structlog.get_logger(__name__).bind(component="scraper", scraper="rads")

logger = logging.getLogger(__name__)


class OperationsScraper(BaseScraper):
    def __init__(self, raw_dir: str = None):
        """
        raw_dir: directory where raw JSON files will be stored.
        If not provided, falls back to BASE RAW_DIR from settings.
        """
        super().__init__()
        if raw_dir is not None:
            self.raw_dir = raw_dir
        else:
            # Allow runtime override via environment variable
            self.raw_dir = os.getenv("RAW_DIR", str(RAW_DIR))

    def scrape(self, nid: int) -> dict | None:
        # If we already have a raw JSON for this NID, load it instead of
        # hitting the network.  This allows offline testing.
        existing = next(Path(self.raw_dir).glob(f"*{nid}*.json"), None)
        if not existing:
            alt_dir = Path(os.getenv("NIDS_CSV", "")).parent / "data" / "raw"
            if alt_dir.is_dir():
                existing = next(alt_dir.glob(f"*{nid}*.json"), None)
        if existing:
            logger.info(f"[Scraper] Using cached raw JSON for NID {nid} → {existing}")
            with open(existing, encoding="utf-8") as f:
                return json.load(f)

        url = OPERATIONS_BASE_URL.format(nid)
        logger.debug(f"Starting scrape for NID {nid}: GET {url}")
        resp = safe_get(url, OPERATIONS_HEADERS)
        data = resp.json()

        # ensure directory exists
        os.makedirs(self.raw_dir, exist_ok=True)

        # save raw JSON with pipeline prefix
        timestamp = datetime.now().strftime("%d_%m_%Y")
        filename = f"operations_{nid}_{timestamp}.json"
        filepath = os.path.join(self.raw_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"[Scraper] Saved raw JSON for NID {nid} → {filepath}")

        return data
