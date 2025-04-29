# ── src/aged_care_pipeline/config/global_settings.py ───────────────────────
"""
All paths in one place.

• reference CSVs (bundled in the wheel)     →  aged_care_pipeline/data/refs/
• every output file (raw / interim / csv)   →  <repo>/data/…
  unless the user overrides    $AGED_CARE_DATA_ROOT
"""
from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path

# ── 1. reference data that ships inside the package ────────────────────────
REFS_DIR = files("aged_care_pipeline").joinpath("refs")

NIDS_CSV = REFS_DIR / "NIDs_Only.csv"
RADS_NIDS_CSV = REFS_DIR / "ProviderDirectory.csv"


# ── 2. where *outputs* should live  ────────────────────────────────────────
def _default_data_root() -> Path:
    """
    Find the project's root-level data directory.
    Walk up from this file until we find a folder containing 'pyproject.toml'
    (the project root). Then return <root>/data if it exists.
    Otherwise, fall back to any ancestor 'data' directory, or CWD/data.
    """
    here = Path(__file__).resolve()
    # first look for project root by pyproject.toml
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file():
            candidate = parent / "data"
            if candidate.is_dir():
                return candidate
            break
    # next, look for any ancestor 'data' folder
    for parent in here.parents:
        candidate = parent / "data"
        if candidate.is_dir():
            return candidate
    # fallback
    return Path.cwd() / "data"


DATA_ROOT = Path(os.getenv("AGED_CARE_DATA_ROOT", _default_data_root())).resolve()

RAW_DIR = DATA_ROOT / "raw"
INTERIM_DIR = DATA_ROOT / "interim"
OUTPUT_DIR = DATA_ROOT / "processed"
LOG_DIR = DATA_ROOT / "logs"

# convenient per-pipeline dirs (used by the scrapers & CLI)
OPERATIONS_RAW_DIR = RAW_DIR / "operations"
OPERATIONS_INTERIM_DIR = INTERIM_DIR / "operations"

RADS_RAW_DIR = RAW_DIR / "rads"
RADS_INTERIM_DIR = INTERIM_DIR / "rads"


# ── 3. the rest (URLs, headers) stays as-is ────────────────────────────────
OPERATIONS_BASE_URL = (
    "https://www.myagedcare.gov.au/api/v1/find-a-provider/"
    "details/{}?search=search-by-name&searchType=agedCareHomes"
)
OPERATIONS_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.myagedcare.gov.au/find-a-provider/aged-care-homes/",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "OperationsBot/1.0 (+https://yourdomain.com)",
}

RADS_BASE_URL = (
    "https://www.myagedcare.gov.au/api/v1/find-a-provider/"
    "details/{}?search=search-by-name&searchType=companyName"
    "&start=0&rows=20&sort=titleAsc"
)
RADS_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.myagedcare.gov.au/find-a-provider/",
}
