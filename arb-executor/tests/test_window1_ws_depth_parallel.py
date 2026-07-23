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
