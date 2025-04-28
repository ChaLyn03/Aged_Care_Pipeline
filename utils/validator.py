# utils/validator.py

def has_key(d: dict, key: str) -> bool:
    return key in d and d[key] is not None
