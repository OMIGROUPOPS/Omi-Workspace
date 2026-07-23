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


def test_ws_delta_fast_timestamp_and_nonempty_ladder_law():
    line = (
        b'{"m":{"type":"orderbook_delta","msg":{'
        b'"market_ticker":"EVENT-A","ts_ms":1780000000123,'
        b'"delta_fp":"1.00"},"seq":2,"sid":1}}'
    )
    assert MODULE.ws_timestamp_from_line(line) == 1780000000.123
    assert MODULE.snapshot_has_ladder({"yes": [], "no": []}) is False
    assert MODULE.snapshot_has_ladder(
        {"yes": [["0.4000", "5.00"]], "no": []}
    ) is True


def test_precomputed_ws_receipt_must_bind_exact_ledger(tmp_path):
    required = {"EVENT-A", "EVENT-B"}
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("\n".join(
        json.dumps({
            "schema_version": "test",
            "ticker": ticker,
            "available": True,
            "full_depth_usable": False,
        }, sort_keys=True)
        for ticker in sorted(required)
    ) + "\n", encoding="utf-8")
    summary = tmp_path / "summary.json"
    receipt = {
        "D": 804,
        "required_tickers": 2,
        "ledger_sha256": MODULE.sha256_file(ledger),
        "ws_depth": {
            "file_count": 215,
            "all_objects_exact": True,
            "required_ticker_count": 2,
        },
    }
    summary.write_text(
        json.dumps(receipt), encoding="utf-8"
    )
    output, metadata = MODULE.load_precomputed_ws_depth(
        ledger, summary, required
    )
    assert set(output) == required
    assert metadata["scan_reused"] is True

    ledger.write_text(
        ledger.read_text(encoding="utf-8") + " ",
        encoding="utf-8",
    )
    try:
        MODULE.load_precomputed_ws_depth(
            ledger, summary, required
        )
    except MODULE.CoverageError as exc:
        assert "hash disagrees" in str(exc)
    else:
        raise AssertionError("tampered WS ledger was accepted")


def test_public_tape_manifest_proves_complete_zero_trade(tmp_path):
    prints = tmp_path / "prints.jsonl"
    prints.write_text("", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "immutable_denominator": {
            "D": 804,
            "required_leg_tickers": 2,
        },
        "pagination": {
            "ticker_queries": 2,
            "failed_ticker_count": 0,
            "all_terminal_cursors_empty": True,
        },
        "artifacts": {
            "normalized_true_prints": {
                "sha256": MODULE.sha256_file(prints),
            }
        },
        "coverage": {
            "tickers_with_zero_trades": ["EVENT-A"],
        },
    }), encoding="utf-8")
    zero, receipt = MODULE.validate_public_tape_manifest(
        manifest, prints, {"EVENT-A", "EVENT-B"}
    )
    assert zero == {"EVENT-A"}
    assert receipt["complete_ticker_queries"] == 2


def test_depth_receipt_difference_is_named_not_reconstructed(tmp_path):
    receipt = tmp_path / "source_inventory.json"
    receipt.write_text(json.dumps({
        "census_date_utc": "2026-07-22",
        "sources": {
            "depth_recorder": {
                "development_files": 189,
                "development_rows": 3_079_608,
                "development_bytes": 435_950_289,
                "coverage_by_utc_date": {
                    "2026-07-12": {"files": 13, "rows": 221_814}
                },
            }
        },
    }), encoding="utf-8")
    result = MODULE.reconcile_depth_inventory_receipt(
        receipt, {
            "file_count": 175,
            "physical_rows": 2_836_510,
            "bytes": 400_549_093,
        }
    )
    assert result["not_preserved_in_frozen_snapshot"] == {
        "files": 14,
        "rows": 243_098,
        "bytes": 35_401_196,
    }
    assert "cannot be reconstructed" in result["classification"]
