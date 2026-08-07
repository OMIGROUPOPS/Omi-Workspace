import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
sys.path.insert(0, str(ANALYSIS))
SPEC = importlib.util.spec_from_file_location(
    "window1_sealed_print_repull", ANALYSIS / "window1_sealed_print_repull.py"
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(M)


def test_load_population_enforces_exact_sealed_denominators(tmp_path):
    events = []
    ids = []
    for index in range(171):
        event_id = f"E{index:03d}"
        ids.append(event_id)
        events.append({
            "event_id": event_id,
            "legs": [{"ticker": event_id + "-A"}, {"ticker": event_id + "-B"}],
        })
    event_list = ("\n".join(ids) + "\n").encode()
    list_path = tmp_path / "list.txt"
    declaration = tmp_path / "declaration.json"
    list_path.write_bytes(event_list)
    declaration.write_text(json.dumps({"events": events}), encoding="utf-8")
    prior = M.SEALED_LIST_SHA256
    M.SEALED_LIST_SHA256 = hashlib.sha256(event_list).hexdigest()
    try:
        loaded, tickers, mapping, got = M.load_population(declaration, list_path)
    finally:
        M.SEALED_LIST_SHA256 = prior
    assert len(loaded) == 171
    assert len(tickers) == 342
    assert mapping["E000-A"] == "E000"
    assert got == event_list


def test_nightly_shape_preserves_identity_size_side_and_exchange_clock():
    row = {
        "trade_id": "T",
        "ticker": "E-A",
        "exchange_ts": "2026-08-01T12:00:00.123000Z",
        "price_cents": 42,
        "size": 5.0,
        "taker_side": "no",
    }
    got = M.nightly_shape(row)
    assert got["trade_id"] == "T"
    assert got["price"] == 42
    assert got["size"] == "5"
    assert got["side"] == "no"
    assert got["ts"] == 1785585600.123
