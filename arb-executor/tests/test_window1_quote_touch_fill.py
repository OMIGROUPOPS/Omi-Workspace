from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace


EXECUTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXECUTOR / "analysis"))

from window1_live_v4_replay import (  # noqa: E402
    PRINT_ONLY_FILL_MODEL,
    ReplayFillSimulator,
)
from window1_quote_reachability_census import (  # noqa: E402
    price_for_model,
    quote_floor,
)


class FakeClock:
    def __init__(self, now=0.0):
        self.now = float(now)

    def time(self):
        return self.now


class FakeNativeFillSimulator:
    def __init__(self, api):
        self.api = api

    def try_fill(self, order, fill_price, fill_ts, trigger):
        order.status = "executed"
        order.fill = (fill_price, fill_ts, trigger)

    def evaluate_trade_print(self, ticker, ts, price):
        for order in self.api.paper_orders.values():
            if (
                order.ticker == ticker
                and order.status == "resting"
                and order.action == "buy"
                and price <= order.yes_price
            ):
                self.try_fill(
                    order, order.yes_price, ts, "trade_print"
                )


def fake_api(*, ask=70, limit=69):
    order = SimpleNamespace(
        order_id="O1",
        ticker="T",
        status="resting",
        action="buy",
        yes_price=limit,
    )
    api = SimpleNamespace(
        paper_orders={"O1": order},
        bot=SimpleNamespace(
            books={"T": SimpleNamespace(best_bid=68, best_ask=ask)}
        ),
    )
    return api, order


def fake_module(clock):
    return SimpleNamespace(
        time=clock,
        PaperFillSimulator=FakeNativeFillSimulator,
    )


def test_print_only_ignores_quote_but_accepts_print():
    clock = FakeClock()
    api, order = fake_api(ask=68, limit=69)
    simulator = ReplayFillSimulator(
        fake_module(clock), api, PRINT_ONLY_FILL_MODEL
    )

    simulator.evaluate_book_cross("T")
    assert order.status == "resting"

    simulator.evaluate_trade_print("T", 7.0, 69)
    assert order.fill == (69, 7.0, "trade_print")


def test_quote_dwell_fills_at_threshold_not_first_touch():
    clock = FakeClock()
    api, order = fake_api(ask=68, limit=69)
    simulator = ReplayFillSimulator(
        fake_module(clock),
        api,
        "QUOTE_TOUCH_OR_PRINT_DWELL_10_V1",
    )

    simulator.evaluate_book_cross("T")
    assert simulator.next_due_ts() == 10.0
    simulator.evaluate_due(9.999)
    assert order.status == "resting"
    simulator.evaluate_due(10.0)
    assert order.fill == (
        69,
        10.0,
        "book_cross_dwell_10s",
    )


def test_quote_dwell_resets_when_ask_leaves_limit():
    clock = FakeClock()
    api, order = fake_api(ask=68, limit=69)
    simulator = ReplayFillSimulator(
        fake_module(clock),
        api,
        "QUOTE_TOUCH_OR_PRINT_DWELL_30_V1",
    )

    simulator.evaluate_book_cross("T")
    clock.now = 20.0
    api.bot.books["T"].best_ask = 70
    simulator.evaluate_book_cross("T")
    assert simulator.next_due_ts() is None

    clock.now = 25.0
    api.bot.books["T"].best_ask = 69
    simulator.evaluate_book_cross("T")
    assert simulator.next_due_ts() == 55.0
    assert order.status == "resting"


def test_newly_posted_cross_starts_dwell_at_post_decision_time():
    clock = FakeClock(now=12.5)
    api, order = fake_api(ask=68, limit=69)
    simulator = ReplayFillSimulator(
        fake_module(clock),
        api,
        "QUOTE_TOUCH_OR_PRINT_DWELL_10_V1",
    )

    simulator.begin_dwell_for_newly_posted_orders()

    assert simulator.next_due_ts() == 22.5
    simulator.evaluate_due(22.5)
    assert order.fill == (
        69,
        22.5,
        "book_cross_dwell_10s",
    )


def test_quote_floor_can_span_multiple_asks_below_limit():
    states = [
        {
            "ts": 0.0,
            "end_ts": 5.0,
            "duration_seconds": 5.0,
            "ask": 70,
        },
        {
            "ts": 5.0,
            "end_ts": 25.0,
            "duration_seconds": 20.0,
            "ask": 68,
        },
        {
            "ts": 25.0,
            "end_ts": 45.0,
            "duration_seconds": 20.0,
            "ask": 69,
        },
        {
            "ts": 45.0,
            "end_ts": 80.0,
            "duration_seconds": 35.0,
            "ask": 75,
        },
    ]

    assert quote_floor(
        states, 10
    )["resting_bid_limit_cents"] == 68
    assert quote_floor(
        states, 30
    )["resting_bid_limit_cents"] == 69
    assert quote_floor(
        states, 60
    )["resting_bid_limit_cents"] == 75


def test_maker_union_uses_better_of_print_and_sustained_quote():
    leg = {
        "print_only_floor": {"price_cents": 70},
        "quote_touch_floors": {
            "10": {"resting_bid_limit_cents": 68},
            "300": {"resting_bid_limit_cents": 72},
        },
    }

    assert price_for_model(leg, "quote_only_10") == 68
    assert price_for_model(leg, "quote_or_print_10") == 68
    assert price_for_model(leg, "quote_only_300") == 72
    assert price_for_model(leg, "quote_or_print_300") == 70
