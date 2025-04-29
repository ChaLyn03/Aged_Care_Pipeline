# parsers/field_paths.py


def get_path(d, path, default=None):
    for key in path:
        if isinstance(key, int) and isinstance(d, list):
            d = d[key] if key < len(d) else default
        elif isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d


FIELD_PATHS = {
    "nid": ["nid"],
    # …
    "rating_compliance": ["ratings", "compliance", 0, "rating"],
}
