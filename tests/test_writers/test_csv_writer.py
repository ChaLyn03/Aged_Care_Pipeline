import csv
import importlib
from pathlib import Path

import aged_care_pipeline.writers.csv_writer as csv_writer


def test_csv_write(tmp_path, monkeypatch):
    """CSVWriter should honour OUTPUT_DIR at runtime."""
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

    # Reload so csv_writer picks up the new OUTPUT_DIR constant
    importlib.reload(csv_writer)

    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    writer = csv_writer.CSVWriter()
    writer.write(data, "test.csv")

    out_file = Path(tmp_path) / "test.csv"
    assert out_file.exists()

    with out_file.open() as f:
        rows = list(csv.DictReader(f))
    assert rows == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
