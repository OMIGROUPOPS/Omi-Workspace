import importlib.util
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module():
    path = ROOT / "te_live.py"
    spec = importlib.util.spec_from_file_location("te_live_identity", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source():
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE kalshi_price_snapshots (
        polled_at TEXT, ticker TEXT, event_ticker TEXT)""")
    return conn


def test_two_codes_resolve_one_full_event_and_are_banked():
    module = _module()
    source = _source()
    source.executemany(
        "INSERT INTO kalshi_price_snapshots VALUES (?,?,?)",
        [
            ("2026-07-30 01:00:00", "EVENT-ALV", "EVENT"),
            ("2026-07-30 01:00:00", "EVENT-VAN", "EVENT"),
        ],
    )
    target = sqlite3.connect(":memory:")
    module._init_observed_start_event_table(target.cursor())

    inserted = module._bank_full_event_start(
        target.cursor(), source.cursor(), "te1", "Alv", "Van",
        "ALV", "VAN", "2026-07-30 01:01:00", "abc",
    )

    assert inserted == 1
    row = target.execute(
        "SELECT kalshi_event_ticker, kalshi_market_tickers_json "
        "FROM observed_start_events"
    ).fetchone()
    assert row[0] == "EVENT"
    assert row[1] == '["EVENT-ALV","EVENT-VAN"]'


def test_one_code_or_ambiguous_pair_never_guesses():
    module = _module()
    source = _source()
    source.executemany(
        "INSERT INTO kalshi_price_snapshots VALUES (?,?,?)",
        [
            ("2026-07-30 01:00:00", "E1-ALV", "E1"),
            ("2026-07-30 01:00:00", "E1-VAN", "E1"),
            ("2026-07-30 01:00:00", "E2-ALV", "E2"),
            ("2026-07-30 01:00:00", "E2-VAN", "E2"),
        ],
    )

    assert module._resolve_full_event_identity(
        source.cursor(), "ALV", None
    ) is None
    assert module._resolve_full_event_identity(
        source.cursor(), "ALV", "VAN"
    ) is None
