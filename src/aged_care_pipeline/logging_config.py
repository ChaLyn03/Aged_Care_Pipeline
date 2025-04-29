# src/aged_care_pipeline/logging_config.py
import logging
import sys
from typing import Literal

import structlog


def init_logging(
    *,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    json_output: bool = False,
) -> None:
    """
    Initialise application-wide structured logging.

    Call once, as early as possible (before other modules import logging).
    """
    # 1️⃣  Point the stdlib logger at stdout so docker/ecs/cloud-init grabs it.
    logging.basicConfig(
        format="%(message)s",  # structlog will render the final line
        stream=sys.stdout,
        level=getattr(logging, level),
    )

    # 2️⃣  Define how each event is transformed ➜ rendered.
    common_processors = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    render = (
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=common_processors + [render],
        # wrap stdlib Logger objects so third-party libs keep working
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        cache_logger_on_first_use=True,  # perf
    )
