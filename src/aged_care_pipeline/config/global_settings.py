# config/global_settings.py
import os

# Local paths
NIDS_CSV = "data/refs/NIDs_Only.csv"
RAW_DIR = "data/raw"
INTERIM_DIR = "data/interim"
OUTPUT_DIR = "data/processed"
LOG_DIR = "data/logs"

# BOperations pipeline settings
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

# RADS pipeline settings
RADS_NIDS_CSV = os.path.join("data", "refs", "ProviderDirectory.csv")
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
RADS_RAW_DIR = os.path.join(RAW_DIR, "rads")
RADS_INTERIM_DIR = os.path.join(INTERIM_DIR, "rads")
