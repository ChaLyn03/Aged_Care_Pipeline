import pytest

from aged_care_pipeline.parsers.operations.operations_field_paths import FIELD_PATHS
from aged_care_pipeline.parsers.operations.operations_parser import OperationsParser


def make_dummy():
    """Return the smallest JSON blob that touches every path we care about."""
    return {
        "nid": 1,
        "ratings": {"compliance": [{"rating": 4}]},
        "operationsData": {
            "agedCareHomes": {
                "occupancy": {
                    "value": {"value": "91-100%"},
                    "median": {"value": "81-90%"},
                },
                "residents": {
                    "lastYear": {"value": "20-39"},
                    "newResidents": {"value": "20-39"},
                    "ceasedResidents": {"value": "20-39"},
                },
            },
            "financialReport": {
                "annual": {
                    "income": {
                        "items": {
                            "governmentFunding": {
                                "total": {"value": 324.98},
                            }
                        },
                        "total": {"value": {"value": 425.43}},
                    },
                    "expenses": {
                        "items": {
                            "careNursing": {
                                "total": {"value": 232.13},
                                "subitems": {
                                    "registeredNurses": {"value": {"value": 71.33}}
                                },
                            }
                        },
                        "total": {"value": {"value": 386.95}},
                    },
                    "reportingPeriod": {"value": {"reportingPeriod": "2023-24"}},
                    "dailyPerResident": {"value": {"value": 38.47}},
                },
                "quarterly": {
                    "wages": {
                        "achTotal": {
                            "total": {"value": 243.51},
                            "value": {"value": 243.51},
                        }
                    }
                },
            },
        },
    }


def test_parse_minimal_dummy():
    raw = make_dummy()
    parser = OperationsParser()
    rows = parser.parse(raw)

    assert len(rows) == 1
    row = rows[0]

    # Every column declared in FIELD_PATHS should be present in the output row
    missing = [c for c in FIELD_PATHS if c not in row]
    assert not missing, f"parser missed columns: {missing}"

    assert row["nid"] == 1
    assert row["agedCareHomes_occupancy_value"] == "91-100%"

    # Naming in the live parser is “governmentFunding_total_value”
    assert pytest.approx(row["governmentFunding_total_value"], rel=1e-3) == 324.98
