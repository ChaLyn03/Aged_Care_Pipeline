# tests/test_writers/test_csv_writer.py
import csv
import os

import pytest
from writers.csv_writer import CSVWriter
from config.global_settings import OUTPUT_DIR

def test_csv_write(tmp_path, monkeypatch):
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

    writer = CSVWriter()
    writer.write(data, "test.csv")

    out = tmp_path / "test.csv"
    assert out.exists()

    # read back
    with open(out) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 2
    assert rows[0]["a"] == "1"
    assert rows[1]["b"] == "4"
