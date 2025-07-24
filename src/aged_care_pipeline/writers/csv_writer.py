# writers/csv_writer.py

import csv
import logging
import os

from aged_care_pipeline.config.global_settings import OUTPUT_DIR
from aged_care_pipeline.interfaces.base_writer import BaseWriter

logger = logging.getLogger(__name__)


class CSVWriter(BaseWriter):
    def __init__(self, output_dir: str = None):
        """
        Initialize writer with an output_dir. If not provided, defaults to the global OUTPUT_DIR.
        """
        super().__init__()
        if output_dir is not None:
            self.output_dir = output_dir
        else:
            # Allow runtime override via environment variable
            self.output_dir = os.getenv("OUTPUT_DIR", str(OUTPUT_DIR))

    def write(self, records: list[dict], filename: str) -> None:
        """
        Write a list of dict records to a CSV file at output_dir/filename.
        """
        # Ensure the directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, filename)

        if not records:
            logger.warning(f"[Writer] No records to write for file {path}; skipping")
            return

        logger.info(f"[Writer] Writing {len(records)} records to {path}")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        logger.debug(f"[Writer] Finished writing file {path}")
