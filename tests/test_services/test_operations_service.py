import pandas as pd
import pytest
from services.operations_service import OperationsService

# A minimal dummy that mirrors the structure your parser expects
def make_dummy_raw(nid):
    return {
        "nid": nid,
        "ratings": {"compliance": [{"rating": 5}]},
        "operationsData": {
            "agedCareHomes": {
                "occupancy": {"value": {"value": "91-100%"}},
                "residents": {
                    "lastYear":     {"value": "20-39"},
                    "newResidents": {"value": "20-39"},
                    "ceasedResidents":{"value": "20-39"}
                }
            },
            "financialReport": {
                "annual": {
                    "income": {
                        "items": {
                            "governmentFunding": {
                                "value": {"value": 324.98}
                            }
                        }
                    }
                }
            }
        }
    }

class DummyScraper:
    def scrape(self, nid):
        # return a minimal raw JSON for each NID
        return make_dummy_raw(nid)

class DummyParser:
    def parse(self, raw):
        # flatten only nid and compliance rating
        return [{"nid": raw["nid"], "rating_compliance": raw["ratings"]["compliance"][0]["rating"]}]

class DummyWriter:
    def __init__(self):
        self.written = None

    def write(self, records, filename):
        self.written = (records, filename)

def test_operations_service_runs(monkeypatch, tmp_path):
    # Create a tiny NIDs CSV
    df = pd.DataFrame({"nid": [101, 202]})
    nids_csv = tmp_path / "nids.csv"
    df.to_csv(nids_csv, index=False)

    # Point the service at our test CSV
    monkeypatch.setenv("NIDS_CSV", str(nids_csv))

    svc = OperationsService()
    svc.scraper = DummyScraper()
    svc.parser  = DummyParser()
    dummy_writer = DummyWriter()
    svc.writer  = dummy_writer

    svc.run()

    # Assert writer was called with two records
    records, filename = dummy_writer.written
    assert len(records) == 2
    # Filenames should start with "operations_"
    assert filename.startswith("operations_")
    # Spot check content
    assert records[0] == {"nid": 101, "rating_compliance": 5}
    assert records[1] == {"nid": 202, "rating_compliance": 5}
