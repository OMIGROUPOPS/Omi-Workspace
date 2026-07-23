import importlib.util
import gzip
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
