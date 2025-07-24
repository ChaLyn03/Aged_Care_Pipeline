# scrapers/operations_scraper.py

import glob
import json
import logging
import os
from datetime import datetime

import structlog

from aged_care_pipeline.config.global_settings import (
    OPERATIONS_BASE_URL,
    OPERATIONS_HEADERS,
    RAW_DIR,
)
from aged_care_pipeline.interfaces.base_scraper import BaseScraper

try:  # allow monkeypatching safe_get before reload without overwriting
    safe_get  # type: ignore  # noqa: F401 - reference for NameError check
except NameError:  # pragma: no cover - executed on first import
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
        env_raw = os.getenv("RAW_DIR")
        self.raw_dir = raw_dir if raw_dir is not None else env_raw or RAW_DIR

    def scrape(self, nid: int) -> dict | None:
        pattern = os.path.join(self.raw_dir, f"*{nid}*.json")
        existing = glob.glob(pattern)
        if existing:
            path = existing[0]
            logger.info(f"[Scraper] Loading cached JSON for NID {nid} from {path}")
            with open(path, "r", encoding="utf-8") as f:
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
