# writers/csv_writer.py

import os
import csv
from config.global_settings import OUTPUT_DIR
from interfaces.base_writer import BaseWriter

class CSVWriter(BaseWriter):
    def write(self, records: list[dict], filename: str) -> None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, filename)
        if not records:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
