import importlib.util
import json
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_spaces_manifest.py"
)
SPEC = importlib.util.spec_from_file_location("window1_spaces_manifest", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_ticker_from_path_handles_gzip_and_plain_csv():
    assert MODULE.ticker_from_path("a/b/TICK.csv.gz") == "TICK"
    assert MODULE.ticker_from_path("TICK.csv") == "TICK"
    assert MODULE.ticker_from_path("TICK.json") == ""


def test_canonical_object_preserves_remote_metadata_without_credentials():
    row = MODULE.canonical_object("ticks", {
        "Path": "T.csv.gz",
        "Size": 12,
        "ModTime": "2026-07-12T00:00:00Z",
        "Hashes": {"MD5": "abc"},
    })
    assert row["path"] == "ticks/T.csv.gz"
    assert row["size_bytes"] == 12
    assert row["content_hashes"] == {"md5": "abc"}
    assert "credential" not in json.dumps(row).lower()
