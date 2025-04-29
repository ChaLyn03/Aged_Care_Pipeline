# src/aged_care_pipeline/__main__.py

"""Package entry-point: python -m aged_care_pipeline …"""

import os

from aged_care_pipeline.logging_config import init_logging
from aged_care_pipeline.scrapers.rads_scraper import run_scraper

from .cli import main


def cli() -> None:
    """Entry-point for console_scripts and direct invocation."""
    # configure logging before any work
    init_logging(
        level=os.getenv("LOG_LEVEL", "INFO"),
        json_output=bool(os.getenv("LOG_JSON", "0")),
    )

    # pull the NID from an environment variable
    nid = os.getenv("RADS_NID")
    if not nid:
        raise RuntimeError("Please set the RADS_NID environment variable")

    # run the scraper
    run_scraper(nid)


if __name__ == "__main__":
    main()
