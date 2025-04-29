# utils/limiter.py

import os
import logging

logger = logging.getLogger(__name__)

def apply_limit(iterable: list[int]) -> list[int]:
    """
    Look at the LIMIT env var on each call.
    If it's a positive integer, slice the iterable to that length.
    Otherwise return the full list.
    """
    limit_str = os.getenv("LIMIT", "").strip()
    if limit_str.isdigit():
        limit = int(limit_str)
        logger.info(f"[Limiter] Applying LIMIT={limit} to {len(iterable)} items")
        return iterable[:limit]
    else:
        logger.debug("[Limiter] No LIMIT set, processing all items")
        return iterable
