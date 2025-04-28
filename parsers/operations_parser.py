# parsers/operations_parser.py

from interfaces.base_parser import BaseParser
from utils.limiter import apply_limit

# reuse your get_path and FIELD_PATHS
from .field_paths import get_path, FIELD_PATHS

class OperationsParser(BaseParser):
    def parse(self, raw: dict) -> list[dict]:
        if not raw or not get_path(raw, ["nid"]):
            return []
        row = {col: get_path(raw, path) for col, path in FIELD_PATHS.items()}
        return [row]
