# utils/limiter.py

from config.global_settings import LIMIT

def apply_limit(iterable: list[int]) -> list[int]:
    return iterable if LIMIT is None else iterable[:LIMIT]
