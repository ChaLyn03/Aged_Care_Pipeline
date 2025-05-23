# parsers/operations_parser.py

import logging

import structlog

from aged_care_pipeline.interfaces.base_parser import BaseParser

from .operations_field_paths import FIELD_PATHS, get_path

log = structlog.get_logger(__name__).bind(component="scraper", scraper="rads")


logger = logging.getLogger(__name__)


class OperationsParser(BaseParser):
    def parse(self, raw: dict) -> list[dict]:
        nid = get_path(raw, ["nid"])
        if not raw or not nid:
            logger.warning("[Parser] Empty or invalid raw data; skipping parse")
            return []

        logger.debug(f"[Parser] Parsing data for NID {nid}")
        row = {col: get_path(raw, path) for col, path in FIELD_PATHS.items()}
        logger.info(f"[Parser] Parsed {len(row)} fields for NID {nid}")
        return [row]
