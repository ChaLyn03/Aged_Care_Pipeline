import logging

import structlog

from aged_care_pipeline.interfaces.base_parser import BaseParser

log = structlog.get_logger(__name__).bind(component="scraper", scraper="rads")

logger = logging.getLogger(__name__)


class RadsParser(BaseParser):
    def parse(self, raw: dict) -> list[dict]:
        if not raw or not raw.get("nid"):
            return []
        nid = raw["nid"]
        provider_name = raw.get("name")
        svc = raw.get("serviceProvider", {})
        address, city, postcode, state = (
            svc.get("address"),
            svc.get("city"),
            svc.get("postcode"),
            svc.get("state"),
        )
        suburb_postcode = f"{city} {postcode}" if city and postcode else None

        rows = []
        for room in raw.get("ach_room_costs", {}).get("subtypes", []):
            rows.append(
                {
                    "nid": nid,
                    "provider_name": provider_name,
                    "room_type": room.get("productName"),
                    "maximumRAD": room.get("maximumRAD"),
                    "address": address,
                    "suburb_postcode": suburb_postcode,
                    "state": state,
                }
            )
        logger.info(f"[RadsParser] Parsed {len(rows)} room record(s) for NID {nid}")
        return rows
