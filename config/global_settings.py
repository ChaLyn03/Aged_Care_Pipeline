# config/global_settings.py

# If LIMIT is None → full scrape; otherwise slice NIDs for testing
LIMIT = None

# Base API settings
BASE_URL = (
    "https://www.myagedcare.gov.au/api/v1/find-a-provider/"
    "details/{}?search=search-by-name&searchType=agedCareHomes"
)
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.myagedcare.gov.au/find-a-provider/aged-care-homes/",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "OperationsBot/1.0 (+https://yourdomain.com)"
}

# Local paths
NIDS_CSV = "data/references/NIDs_Only.csv"
OUTPUT_DIR = "data/processed"
RAW_DIR = "data/raw"
LOG_DIR = "data/logs"
