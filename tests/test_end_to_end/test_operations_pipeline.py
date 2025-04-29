# tests/test_end_to_end/test_full_pipeline.py
import subprocess
import sys
from pathlib import Path

def test_full_pipeline(tmp_path, monkeypatch):
    # point NIDS_CSV to our one-item file
    nids_csv = tmp_path / "nids.csv"
    nids_csv.write_text("nid\n12345\n")
    monkeypatch.setenv("NIDS_CSV", str(nids_csv))

    # pre-create raw JSON to skip HTTP
    raw = tmp_path / "data/raw/12345_20250101.json"
    raw.parent.mkdir(parents=True)
    raw.write_text('{"nid":12345,"ratings":{"compliance":[{"rating":3}]}}')

    # run main.py and ensure exit code 0
    result = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
    assert result.returncode == 0

    # check output file exists
    out = Path("data/processed").glob("operations_*.csv")
    assert any(out)
