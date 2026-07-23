import importlib.util
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_ws_depth_parallel.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_ws_depth_parallel", PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def worker_result(name, first, last, *, started=False, ladder=False):
    return {
        "file": name,
        "expected_name": name,
        "bytes": 1,
        "md5": "x",
        "exact_object": True,
        "physical_rows": 1,
        "parse_errors": 0,
        "corrupt_error_class": None,
        "message_types": {"orderbook_delta": 1},
        "segments": [{
            "started_by_recorder": started,
            "first_by_sid": {1: first},
            "last_by_sid": {1: last},
            "gap_count": 0,
        }],
        "tickers": {
            "EVENT-A": {
                **MODULE.new_ticker_stats(),
                "delta_rows": 1,
                "segments": [0],
                "full_snapshot_segments": [0] if ladder else [],
                "full_snapshot_rows": 1 if ladder else 0,
            }
        },
    }


def test_cross_file_sequence_gap_invalidates_full_depth_epoch():
    rows = [
        worker_result("a", 1, 2, started=True, ladder=True),
        worker_result("b", 4, 5, ladder=True),
    ]
    output, summary = MODULE.merge_results(rows, {"EVENT-A"})
    assert summary["epoch_count"] == 1
    assert summary["epoch_gap_count"] == 1
    assert output["EVENT-A"]["full_depth_usable"] is False


def test_recorder_start_creates_a_new_complete_epoch():
    rows = [
        worker_result("a", 1, 2, started=False),
        worker_result("b", 9, 10, started=True, ladder=True),
    ]
    output, summary = MODULE.merge_results(rows, {"EVENT-A"})
    assert summary["epoch_count"] == 2
    assert summary["complete_start_epochs"] == 1
    assert output["EVENT-A"]["full_depth_usable"] is True


def test_required_ticker_without_ws_rows_is_explicitly_unavailable():
    rows = [
        worker_result("a", 1, 2, started=True, ladder=True),
    ]
    output, summary = MODULE.merge_results(
        rows, {"EVENT-A", "EVENT-B"}
    )
    assert set(output) == {"EVENT-A", "EVENT-B"}
    assert output["EVENT-B"]["available"] is False
    assert output["EVENT-B"]["full_depth_usable"] is False
    assert summary["required_ticker_count"] == 2


def test_fast_scalar_extractors_preserve_ws_values():
    line = (
        b'{"m":{"type":"orderbook_delta","sid":1,"seq":7,'
        b'"msg":{"market_ticker":"EVENT-A",'
        b'"ts":"2026-07-12T03:59:59.999234Z",'
        b'"ts_ms":1783828799999}}}'
    )
    assert MODULE.fast_quoted(
        line, b'"type":"', MODULE.TYPE_PATTERN
    ) == b"orderbook_delta"
    assert MODULE.fast_uint(
        line, b'"seq":', MODULE.SEQUENCE_PATTERN
    ) == 7
    assert MODULE.timestamp_from_line(line) == 1783828799.999
