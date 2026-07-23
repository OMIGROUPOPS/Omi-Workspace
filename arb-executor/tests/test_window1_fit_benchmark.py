import importlib.util
import gzip
import hashlib
import json
import sqlite3
from pathlib import Path

PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_fit_benchmark.py"
)
SPEC = importlib.util.spec_from_file_location("window1_fit_benchmark", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def snapshot(ts=100.0, bid=40, ask=42, bid_size=10):
    return {
        "ts": ts,
        "bids": [(bid, bid_size), (bid - 1, 20)],
        "asks": [(ask, 12), (ask + 1, 30)],
        "best_bid": bid,
        "best_ask": ask,
    }


def test_same_price_queue_is_bounded_not_automatic_fill():
    actions = [{"ts": 100, "price": 40, "queue_ahead": 10}]
    prints = [{
        "ts": 110,
        "price": 40,
        "size": 5,
        "taker_side": "no",
    }]
    lower = MODULE.simulate_actions(actions, prints, 120, "lower")
    upper = MODULE.simulate_actions(actions, prints, 120, "upper")
    assert lower["status"] == "not_filled"
    assert upper["status"] == "filled"


def test_trade_through_is_exact_in_both_queue_bounds():
    actions = [{"ts": 100, "price": 40, "queue_ahead": 1000}]
    prints = [{
        "ts": 110,
        "price": 39,
        "size": 1,
        "taker_side": "no",
    }]
    assert MODULE.simulate_actions(
        actions, prints, 120, "lower"
    )["status"] == "filled"
    assert MODULE.simulate_actions(
        actions, prints, 120, "upper"
    )["status"] == "filled"


def test_yes_taker_does_not_fill_resting_yes_bid():
    actions = [{"ts": 100, "price": 40, "queue_ahead": 0}]
    prints = [{
        "ts": 110,
        "price": 40,
        "size": 100,
        "taker_side": "yes",
    }]
    assert MODULE.simulate_actions(
        actions, prints, 120, "upper"
    )["status"] == "not_filled"


def test_zero_size_never_fills():
    actions = [{"ts": 100, "price": 40, "queue_ahead": 0}]
    prints = [{
        "ts": 110,
        "price": 39,
        "size": 0,
        "taker_side": "no",
    }]
    assert MODULE.simulate_actions(
        actions, prints, 120, "upper"
    )["quantity"] == 0


def test_reference_is_last_positive_true_print_inside_window():
    prints = [
        {"ts": 90, "price": 30, "size": 1},
        {"ts": 110, "price": 31, "size": 2},
        {"ts": 115, "price": 99, "size": 0},
        {"ts": 120, "price": 32, "size": 1},
        {"ts": 130, "price": 33, "size": 1},
    ]
    assert MODULE.w1_reference(prints, 100, 120) == 32


def test_selection_prioritizes_negative_pair_capture():
    rows = [
        {
            "candidate_id": "high-completion",
            "raw": {
                "NC": 10, "C": 50, "IC": 8, "PC": 40, "censored": 2
            },
        },
        {
            "candidate_id": "negative-capture",
            "raw": {
                "NC": 11, "C": 20, "IC": 7, "PC": 18, "censored": 3
            },
        },
    ]
    assert MODULE.select_candidate(rows)["candidate_id"] == "negative-capture"


def test_instrument_stages_hold_boundary_and_mechanics_fixed():
    selected = {
        "boundary_id": "b",
        "window": {"left_edge_hours_before_schedule": 4},
    }
    template = {
        "policy_id": "causal_stack_simultaneous_reaim",
        "placement_rule": "causal_stack",
        "sequence_rule": "simultaneous",
        "first_fill_response": "reaim_depth_support",
    }
    rows = MODULE.instrument_stage_candidates(selected, template)
    assert [row["instrument_stage"] for row in rows] == [
        "bbo_prints_baseline",
        "top5_pressure_enhancement",
        "limited_top20_pressure_enhancement",
        "full_causal_stack",
    ]
    assert {row["boundary_id"] for row in rows} == {"b"}
    assert rows[0]["policy"]["placement_rule"] == (
        rows[-1]["policy"]["placement_rule"]
    )
    assert {row["policy"]["first_fill_response"] for row in rows} == {
        "reaim_touch"
    }
    assert rows[1]["policy"]["use_top20_pressure"] is False


def test_corridor_cache_only_collapses_when_another_right_edge_exists():
    candidate = {
        "window": {"schedule_only_corridor_minutes": 45}
    }
    assert MODULE.corridor_cache_discriminator(
        candidate, {
            "safe_prestart_cutoff_utc": "2026-07-12T12:00:00Z",
            "contradiction": False,
        }
    ) is None
    assert MODULE.corridor_cache_discriminator(
        candidate, {
            "known_live_by_utc": "2026-07-12T12:05:00Z",
        }
    ) is None
    assert MODULE.corridor_cache_discriminator(
        candidate, {}
    ) == 45


def test_sibling_book_is_mapped_into_one_economic_direction():
    own = snapshot(bid=40, ask=42)
    sibling = snapshot(bid=57, ask=59)
    result = MODULE.complement_normalized_features(own, sibling)
    assert result["implied_yes_bid_from_sibling_ask"] == 41
    assert result["implied_yes_ask_from_sibling_bid"] == 43
    assert result["normalized_economic_best_bid"] == 41
    assert result["normalized_economic_best_ask"] == 42


def test_top5_loader_uses_the_row_last_trade_field(tmp_path):
    path = tmp_path / "T-A.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(
            "ts_et,ticker,bid_1,bid_1_sz,ask_1,ask_1_sz,last_trade\n"
        )
        handle.write(
            "2026-07-12 04:00:00 PM,T-A,40,10,42,12,41\n"
        )
    earliest = MODULE.parse_top5_et_fast(
        "2026-07-12 03:59:00 PM", {}
    )
    latest = MODULE.parse_top5_et_fast(
        "2026-07-12 04:01:00 PM", {}
    )
    rows = MODULE.load_top5(path, "T-A", earliest, latest)
    assert len(rows) == 1
    assert rows[0]["last_trade"] == 41


def test_top5_loader_discards_only_a_partial_terminal_row(tmp_path):
    path = tmp_path / "T-A.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(
            "ts_et,ticker,bid_1,bid_1_sz,ask_1,ask_1_sz,last_trade\n"
        )
        handle.write(
            "2026-07-12 04:00:00 PM,T-A,40,10,42,12,41\n"
        )
        handle.write("2026-07-12 04:01:00 PM")
    earliest = MODULE.parse_top5_et_fast(
        "2026-07-12 03:59:00 PM", {}
    )
    latest = MODULE.parse_top5_et_fast(
        "2026-07-12 04:02:00 PM", {}
    )
    rows = MODULE.load_top5(path, "T-A", earliest, latest)
    assert len(rows) == 1


def test_top5_loader_recovers_complete_row_after_rotation_prefix(tmp_path):
    path = tmp_path / "T-A.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(
            "ts_et,ticker,bid_1,bid_1_sz,ask_1,ask_1_sz,last_trade\n"
        )
        handle.write(
            "2026-07-12 04:00:00 PM,T-A,40,10,42"
            "2026-07-12 04:01:00 PM,T-A,41,11,43,13,42\n"
        )
        handle.write(
            "2026-07-12 04:02:00 PM,T-A,42,12,44,14,43\n"
        )
    earliest = MODULE.parse_top5_et_fast(
        "2026-07-12 03:59:00 PM", {}
    )
    latest = MODULE.parse_top5_et_fast(
        "2026-07-12 04:03:00 PM", {}
    )
    rows = MODULE.load_top5(path, "T-A", earliest, latest)
    assert [row["best_bid"] for row in rows] == [41, 42]
    assert [row["last_trade"] for row in rows] == [42, 43]


def test_top5_loader_rejects_malformed_interior_row(tmp_path):
    path = tmp_path / "T-A.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(
            "ts_et,ticker,bid_1,bid_1_sz,ask_1,ask_1_sz,last_trade\n"
        )
        handle.write("not,a,complete,row\n")
        handle.write(
            "2026-07-12 04:02:00 PM,T-A,42,12,44,14,43\n"
        )
    earliest = MODULE.parse_top5_et_fast(
        "2026-07-12 03:59:00 PM", {}
    )
    latest = MODULE.parse_top5_et_fast(
        "2026-07-12 04:03:00 PM", {}
    )
    try:
        MODULE.load_top5(path, "T-A", earliest, latest)
    except MODULE.FitError as exc:
        assert "malformed premarket row" in str(exc)
    else:
        raise AssertionError("interior malformed row was accepted")


def test_print_archive_indexes_contiguous_tickers_and_loads_bounds(tmp_path):
    path = tmp_path / "prints.jsonl"
    rows = [
        {
            "exchange_ts": "2026-07-12T12:00:00Z",
            "price_cents": 40,
            "size": 5,
            "taker_side": "no",
            "ticker": "EVENT-A",
            "trade_id": "trade-a1",
            "true_print": True,
        },
        {
            "exchange_ts": "2026-07-12T13:00:00Z",
            "price_cents": 41,
            "size": 2,
            "taker_side": "yes",
            "ticker": "EVENT-A",
            "trade_id": "trade-a2",
            "true_print": True,
        },
        {
            "exchange_ts": "2026-07-12T12:30:00Z",
            "price_cents": 60,
            "size": 3,
            "taker_side": "no",
            "ticker": "EVENT-B",
            "trade_id": "trade-b1",
            "true_print": True,
        },
    ]
    raw = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode()
    path.write_bytes(raw)
    archive = MODULE.PrintArchive(
        path, hashlib.sha256(raw).hexdigest()
    )
    earliest = MODULE.parse_utc(
        "2026-07-12T12:30:00Z", "earliest"
    )
    latest = MODULE.parse_utc(
        "2026-07-12T14:00:00Z", "latest"
    )
    loaded = archive.load("EVENT-A", earliest, latest)
    assert [row["trade_id"] for row in loaded] == ["trade-a2"]
    assert archive.ranges["EVENT-A"][2] == 2
    assert archive.ranges["EVENT-B"][2] == 1


def test_print_archive_rejects_noncontiguous_ticker_groups(tmp_path):
    path = tmp_path / "prints.jsonl"
    rows = []
    for index, ticker in enumerate(("EVENT-A", "EVENT-B", "EVENT-A")):
        rows.append({
            "exchange_ts": f"2026-07-12T12:0{index}:00Z",
            "price_cents": 40,
            "size": 1,
            "taker_side": "no",
            "ticker": ticker,
            "trade_id": f"trade-{index}",
            "true_print": True,
        })
    raw = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode()
    path.write_bytes(raw)
    try:
        MODULE.PrintArchive(path, hashlib.sha256(raw).hexdigest())
    except MODULE.FitError as exc:
        assert "not ticker-contiguous" in str(exc)
    else:
        raise AssertionError("noncontiguous archive was accepted")


def test_macro_book_context_maps_the_literal_participant_not_role():
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE players (kalshi_code TEXT, name TEXT);
        CREATE TABLE book_prices (
            event_ticker TEXT, book_key TEXT,
            player1_name TEXT, player2_name TEXT,
            book_p1_fv_cents REAL, book_p2_fv_cents REAL,
            polled_at TEXT
        );
        INSERT INTO players VALUES ('MAY', 'Aidan Mayo');
        INSERT INTO book_prices VALUES (
            'EVENT', 'pinnacle', 'Alex Michelsen', 'Aidan Mayo',
            70, 30, '2026-07-20 12:00:00'
        );
        """
    )
    timestamp = MODULE.ET.localize(
        __import__("datetime").datetime(2026, 7, 20, 12, 1)
    ).timestamp() if hasattr(MODULE.ET, "localize") else (
        __import__("datetime").datetime(
            2026, 7, 20, 12, 1, tzinfo=MODULE.ET
        ).timestamp()
    )
    result = MODULE.macro_book_context(
        connection, "EVENT", "EVENT-MAY", timestamp, 60
    )
    assert result["bookmaker_available"] is True
    assert result["book_blend_cents"] == 30
    assert result["book_market_divergence_cents"] == -30


def test_macro_book_context_fails_closed_when_participant_is_unresolved():
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE players (kalshi_code TEXT, name TEXT);
        CREATE TABLE book_prices (
            event_ticker TEXT, book_key TEXT,
            player1_name TEXT, player2_name TEXT,
            book_p1_fv_cents REAL, book_p2_fv_cents REAL,
            polled_at TEXT
        );
        INSERT INTO book_prices VALUES (
            'EVENT', 'pinnacle', 'Alpha Person', 'Beta Person',
            70, 30, '2026-07-20 12:00:00'
        );
        """
    )
    timestamp = __import__("datetime").datetime(
        2026, 7, 20, 12, 1, tzinfo=MODULE.ET
    ).timestamp()
    result = MODULE.macro_book_context(
        connection, "EVENT", "EVENT-ZZZ", timestamp, 60
    )
    assert result["bookmaker_available"] is False
    assert result["book_blend_cents"] is None
