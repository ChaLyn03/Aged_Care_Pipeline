import pandas as pd


# All imports that depend on environment variables happen *inside* the test
# so that monkeypatching works.
def make_dummy_raw(nid):
    return {
        "nid": nid,
        "ratings": {"compliance": [{"rating": 5}]},
        "operationsData": {
            "agedCareHomes": {
                "occupancy": {"value": {"value": "91-100%"}},
                "residents": {
                    "lastYear": {"value": "20-39"},
                    "newResidents": {"value": "20-39"},
                    "ceasedResidents": {"value": "20-39"},
                },
            },
            "financialReport": {
                "annual": {
                    "income": {
                        "items": {"governmentFunding": {"total": {"value": 324.98}}}
                    }
                }
            },
        },
    }


class DummyScraper:
    def scrape(self, nid):
        return make_dummy_raw(nid)


class DummyParser:
    def parse(self, raw):
        return [
            {
                "nid": raw["nid"],
                "rating_compliance": raw["ratings"]["compliance"][0]["rating"],
            }
        ]


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

    # Environment variables **before** we import the service module
    monkeypatch.setenv("NIDS_CSV", str(nids_csv))

    # Import after env-vars so constants pick up the patched paths
    from aged_care_pipeline.services.operations_service import OperationsService

    svc = OperationsService()
    svc.scraper = DummyScraper()
    svc.parser = DummyParser()
    dummy_writer = DummyWriter()
    svc.writer = dummy_writer

    svc.run()

    records, filename = dummy_writer.written
    assert len(records) == 2
    assert filename.startswith("operations_")
    assert records == [
        {"nid": 101, "rating_compliance": 5},
        {"nid": 202, "rating_compliance": 5},
    ]
