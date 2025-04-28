# tests/test_parsers/test_operations_parser.py

import pytest
from parsers.operations_parser import OperationsParser
from parsers.field_paths import get_path, FIELD_PATHS

def make_dummy():
    return {
        "nid": 1,
        "ratings": {"compliance": [{"rating": 4}]},
        "operationsData": {
            "agedCareHomes": {
                "occupancy": {
                    "value": {"value": "91-100%"},
                    "median": {"value": "81-90%"}
                },
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
                                "total": {"value": 324.98},
                                "value": {"value": 324.98}
                            }
                        },
                        "total": {"value": {"value": 425.43}}
                    },
                    "expenses": {
                        "items": {
                            "careNursing": {
                                "total": {"value": 232.13},
                                "subitems": {
                                    "registeredNurses": {"value": {"value": 71.33}}
                                }
                            }
                        },
                        "total": {"value": {"value": 386.95}}
                    },
                    "reportingPeriod": {"value": {"reportingPeriod": "2023-24"}},
                    "dailyPerResident": {"value": {"value": 38.47}}
                },
                "quarterly": {
                    "wages": {
                        "achTotal": {
                            "total": {"value": 243.51},
                            "value": {"value": 243.51}
                        }
                    }
                }
            }
        }
    }

def test_parse_minimal_dummy():
    raw = make_dummy()
    parser = OperationsParser()
    rows = parser.parse(raw)

    assert len(rows) == 1
    row = rows[0]
    # every key from FIELD_PATHS should be present
    for col in FIELD_PATHS:
        assert col in row

    assert row["nid"] == 1
    assert row["agedCareHomes_occupancy_value"] == "91-100%"
    assert pytest.approx(row["governmentFunding_value"], rel=1e-3) == 324.98
