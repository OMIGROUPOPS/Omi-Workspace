import gzip
import importlib.util
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis" / "window1_ws_trade_reconcile.py"
SPEC = importlib.util.spec_from_file_location(
    "window1_ws_trade_reconcile", MODULE_PATH
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_ws_trade_parser_retains_exchange_identity_and_clock(tmp_path):
    path = tmp_path / "ws_20260712_00.jsonl.gz"
    row = {
        "t": 1783814467.007,
        "m": {
            "type": "trade",
            "seq": 1,
            "sid": 2,
            "msg": {
                "trade_id": "T",
                "market_ticker": "E-A",
                "yes_price_dollars": "0.9000",
                "no_price_dollars": "0.1000",
                "count_fp": "0.11",
                "ts": 1783814466,
                "ts_ms": 1783814466990,
            },
        },
    }
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    result = M.scan_ws_file((str(path), frozenset({"E-A"})))
    assert result["required_trade_rows"] == 1
    assert result["parse_errors"] == 0
    assert result["rows"] == [
        ("T", "E-A", 1783814466990, 90, "0.11", path.name)
    ]


def test_decimal_and_timestamp_normalization():
    assert M.decimal_text("5.00") == "5"
    assert M.price_cents("0.4200") == 42
    assert M.epoch_ms("2026-07-12T00:00:00.049114Z") == 1783814400049


def test_proven_zero_trade_tickers_do_not_fail_complete_tape():
    assert M.reconciliation_gate_pass(
        mismatch_total=0,
        public_tickers_with_prints=1606,
        proven_zero_trade_ticker_count=2,
        union_rows=4_836_462,
        public_rows=4_836_462,
    )
    assert not M.reconciliation_gate_pass(
        mismatch_total=0,
        public_tickers_with_prints=1605,
        proven_zero_trade_ticker_count=2,
        union_rows=4_836_462,
        public_rows=4_836_462,
    )
