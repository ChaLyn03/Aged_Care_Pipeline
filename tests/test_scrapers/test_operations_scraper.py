# tests/test_scrapers/test_operations_scraper.py
import os
import json
import pytest
import requests
from requests.models import Response

from scrapers.operations_scraper import OperationsScraper
from config.global_settings import BASE_URL, RAW_DIR

class DummyResponse(Response):
    def __init__(self, data, status=200):
        super().__init__()
        self._content = json.dumps(data).encode()
        self.status_code = status

def test_scrape_saves_raw(tmp_path, monkeypatch):
    nid = 12345
    sample = {"nid": nid, "foo": "bar"}

    # Monkey-patch safe_get to return our dummy response
    def fake_get(url, headers):
        assert url == BASE_URL.format(nid)
        return DummyResponse(sample)
    monkeypatch.setattr("scrapers.operations_scraper.safe_get", fake_get)

    # Redirect RAW_DIR to our tmp
    monkeypatch.setenv("RAW_DIR", str(tmp_path))
    os.makedirs(str(tmp_path), exist_ok=True)

    scraper = OperationsScraper()
    result = scraper.scrape(nid)
    assert result == sample

    # Check file was written
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    saved = json.loads(files[0].read_bytes())
    assert saved == sample
