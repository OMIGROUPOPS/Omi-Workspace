import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "analysis"
    / "window1_finalize_source_coverage.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_finalize_source_coverage", SCRIPT
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def test_report_only_depth_byte_correction(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("{}\n" * 804, encoding="utf-8")
    depth = tmp_path / "depth"
    depth.mkdir()
    for index in range(175):
        (depth / f"depth_20260712_{index:03d}.jsonl.gz").write_bytes(
            b"x"
        )
    summary = {
        "D": 804,
        "required_tickers": 1608,
        "event_counts": {
            "both_legs_minimum_instrument": 804,
        },
        "depth_recorder": {
            "file_count": 175,
            "physical_rows": 2_836_510,
        },
        "depth_recorder_receipt_reconciliation": {
            "receipt_claim": {"bytes": 200},
            "frozen_snapshot_observed": {"bytes": 0},
            "not_preserved_in_frozen_snapshot": {"bytes": 200},
        },
    }
    output = module.finalize(
        summary, ledger_path=ledger, depth_dir=depth
    )
    assert output["depth_recorder"]["bytes"] == 175
    assert output[
        "depth_recorder_receipt_reconciliation"
    ]["not_preserved_in_frozen_snapshot"]["bytes"] == 25
    assert "no event" in output["report_only_correction"]
