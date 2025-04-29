# parsers/rads_parser.py
import logging
from interfaces.base_parser import BaseParser

logger = logging.getLogger(__name__)

class RadsParser(BaseParser):
    def parse(self, raw: dict) -> list[dict]:
        """
        Transforms raw RADS JSON into a list of flat dicts, one per room type.
        """
        if not raw or not raw.get("nid"):
            return []

        nid = raw.get("nid")
        provider_name = raw.get("name")
        svc = raw.get("serviceProvider", {})
        address = svc.get("address")
        city = svc.get("city")
        postcode = svc.get("postcode")
        state = svc.get("state")
        suburb_postcode = f"{city} {postcode}" if city and postcode else None

        rooms = raw.get("ach_room_costs", {}).get("subtypes") or []
        rows = []
        for room in rooms:
            rows.append({
                "nid": nid,
                "provider_name": provider_name,
                "room_type": room.get("productName"),
                "maximumRAD": room.get("maximumRAD"),
                "address": address,
                "suburb_postcode": suburb_postcode,
                "state": state,
            })
        logger.info(f"[RadsParser] Parsed {len(rows)} room record(s) for NID {nid}")
        return rows