# utils/logger.py
import logging
import os

def setup_logger():
    lvl_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, lvl_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # suppress overly-verbose libraries if you like
    logging.getLogger("requests").setLevel(logging.WARNING)
