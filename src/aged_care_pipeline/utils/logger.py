# utils/logger.py

import logging
import os


def setup_logger():
    # 1) Read from environment, or default to INFO
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # 2) Force-reconfigure the root logger on every run
    #    (requires Python ≥3.8)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
