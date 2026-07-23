import importlib.util
import gzip
import json
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_source_coverage.py"
)
SPEC = importlib.util.spec_from_file_location("window1_source_coverage", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_snapshot_requires_a_real_ladder_field():
    assert not MODULE.snapshot_has_ladder({
        "market_ticker": "T-A",
        "market_id": "m",
    })
    assert MODULE.snapshot_has_ladder({
        "market_ticker": "T-A",
        "yes_dollars": [["0.40", "5"]],
    })


def test_epoch_milliseconds_are_normalized_to_seconds():
    assert MODULE.parse_iso(1_783_814_400_049) == 1_783_814_400.049


def test_local_timestamp_is_timezone_labeled():
    value = MODULE.parse_et("2026-07-12 04:00:00 PM")
    assert MODULE.iso_utc(value).startswith("2026-07-12T20:00:00")


def test_gzip_census_skips_a_truncated_terminal_row(tmp_path):
    path = tmp_path / "trades.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write("ts_et,price,count\n")
        handle.write("2026-07-12 04:00:00 PM,44,5\n")
        handle.write("2026-07-12 04:01:00 PM")
    result = MODULE.scan_recorder_csv(path, "trades")
    assert result["available"] is True
    assert result["row_count"] == 2
    assert result["positive_size_observed_at_endpoint"] is True
    assert result["last_local_receipt_ts"].startswith(
        "2026-07-12T20:00:00"
    )
    assert result["parse_error_count"] >= 1


def test_spaces_lsjson_names_are_accepted_without_network_access(tmp_path):
    path = tmp_path / "ticks.lsjson"
    path.write_text(json.dumps([
        {"Path": "nested/KXEVENT-LEG.csv.gz", "Size": 10}
    ]), encoding="utf-8")
    assert MODULE.load_spaces_names(path) == {"KXEVENT-LEG.csv.gz"}
