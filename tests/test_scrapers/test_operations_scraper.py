import importlib
import json
from pathlib import Path

from requests.models import Response

import aged_care_pipeline.scrapers.operations_scraper as op_scraper
from aged_care_pipeline.config.global_settings import OPERATIONS_BASE_URL


class DummyResponse(Response):
    """A minimal Response object that behaves like requests.get output."""

    def __init__(self, data, status=200):
        super().__init__()
        self._content = json.dumps(data).encode()
        self.status_code = status


def test_scrape_saves_raw(tmp_path, monkeypatch):
    """OperationsScraper.scrape should write the raw JSON to RAW_DIR."""
    nid = 12345
    sample = {"nid": nid, "foo": "bar"}

    # Patch safe_get so we do **not** hit the network
    def fake_get(url, headers):
        assert url == OPERATIONS_BASE_URL.format(nid)
        return DummyResponse(sample)

    monkeypatch.setattr(op_scraper, "safe_get", fake_get, raising=True)

    # Point RAW_DIR at the pytest tmp directory *and* reload the module so the
    # constant inside operations_scraper picks up the new value.
    monkeypatch.setenv("RAW_DIR", str(tmp_path))
    importlib.reload(op_scraper)

    scraper = op_scraper.OperationsScraper()
    result = scraper.scrape(nid)
    assert result == sample

    # The scraper creates <RAW_DIR>/<nid>.json  — search recursively to find it
    saved_files = list(Path(tmp_path).rglob("*.json"))
    assert len(saved_files) == 1
    saved = json.loads(saved_files[0].read_bytes())
    assert saved == sample
