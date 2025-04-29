# utils/request_handler.py

import requests

from aged_care_pipeline.utils.retry import retry


@retry(times=3, delay=1)
def safe_get(url: str, headers: dict) -> requests.Response:
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp
