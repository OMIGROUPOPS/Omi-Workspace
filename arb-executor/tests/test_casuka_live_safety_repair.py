#!/usr/bin/env python3
"""Deterministic CASUKA live-safety regression fixtures.

No network client is created.  The real live_v4 sell chokepoint, exit healer,
reconcile top-up, and pair classifier run against an in-memory exchange whose
GET/POST/DELETE calls are receipt-ordered.
"""
import asyncio
import sys
import types
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M


TK = "KXITFMATCH-26JUL27CASUKA-CAS"
ET = "KXITFMATCH-26JUL27CASUKA"


class ExchangeFixture:
    def __init__(self, held=5, sells=None):
        self.held = float(held)
        self.orders = []
        self.calls = []
        self.next_id = 1
        for oid, qty, price in (sells or []):
            self.orders.append({
                "order_id": oid, "ticker": TK, "action": "sell",
                "side": "yes", "yes_price_dollars": price / 100.0,
                "remaining_count_fp": float(qty)})

    async def get(self, _s, _ak, _pk, path, _rl):
        self.calls.append(("GET", path))
        if "/positions?" in path:
            rows = ([] if self.held == 0 else [{
                "ticker": TK, "position_fp": self.held}])
            return {"market_positions": rows}
        if "/orders?" in path:
            return {"orders": [dict(o) for o in self.orders]}
        return {}

    async def post(self, _s, _ak, _pk, path, payload, _rl):
        self.calls.append(("POST", path, dict(payload)))
        oid = "NEW-%02d" % self.next_id
        self.next_id += 1
        self.orders.append({
            "order_id": oid, "ticker": payload["ticker"],
            "action": "sell" if payload["side"] == "ask" else "buy",
            "side": "yes", "yes_price_dollars": float(payload["price"]),
            "remaining_count_fp": float(payload["count"])})
        return {"order_id": oid, "fill_count": 0,
                "remaining_count": int(payload["count"])}

    async def delete(self, _s, _ak, _pk, path, _rl):
        self.calls.append(("DELETE", path))
        oid = path.rsplit("/", 1)[-1]
        before = len(self.orders)
        self.orders = [o for o in self.orders if o["order_id"] != oid]
        return len(self.orders) != before

    @property
    def resting_sell_qty(self):
        return sum(float(o["remaining_count_fp"]) for o in self.orders
                   if o["action"] == "sell")

    @property
    def sell_posts(self):
        return [c for c in self.calls if c[0] == "POST"
                and c[2]["side"] == "ask"]


BOUND = (
    "_begin_reconcile_exit_intent_cycle",
    "_end_reconcile_exit_intent_cycle",
    "_exit_intent_state",
    "_record_exit_intent_change",
    "_record_exit_intent_reset",
    "_record_exit_intent_post",
    "_authoritative_sell_snapshot",
    "_alert_sell_guard_refusal",
    "_reconcile_exit_topup_from_truth",
    "place_order",
    "_place_order_unlocked",
    "cancel_order",
    "_v4_apply_exit",
    "_pair_invariant_leg_state",
)


def make_bot():
    bot = types.SimpleNamespace()
    bot.session = None
    bot.ak = None
    bot.pk = None
    bot.rl = None
    bot.config = {}
    bot.books = {}
    bot.positions = {}
    bot._bot_order_ids = set()
    bot._bot_order_tickers = set()
    bot.logs = []
    bot._log = lambda event, details=None, ticker="": bot.logs.append(
        (event, details or {}, ticker))
    bot._wall_observe = lambda *_args, **_kwargs: None
    bot.cell_lookup = lambda _cat, _price: "ITF_W:87"
    bot.exit_rule_for = lambda _cat, _price: (11, "exit")
    bot.exit_depth_floor = 0
    for name in BOUND:
        setattr(bot, name, types.MethodType(getattr(M.LiveV3, name), bot))
    return bot


def make_pos(qty=5, exit_order_id=""):
    pos = M.Position(
        ticker=TK, event_ticker=ET, category="ITF_W", direction="",
        cell_name="", cell_cfg={}, entry_price=87, entry_qty=qty,
        phase="active", entry_filled_ts=1.0, is_v4=True,
        exit_price=98, exit_order_id=exit_order_id)
    pos.exit_filled_qty = 0
    return pos


def run(coro):
    return asyncio.run(coro)


class CasukaLiveSafetyTests(unittest.TestCase):
    def setUp(self):
        self.old_get = M.api_get
        self.old_post = M.api_post
        self.old_delete = M.api_delete

    def tearDown(self):
        M.api_get = self.old_get
        M.api_post = self.old_post
        M.api_delete = self.old_delete

    def install(self, exchange):
        M.api_get = exchange.get
        M.api_post = exchange.post
        M.api_delete = exchange.delete

    def test_heal_then_topup_posts_exactly_five_and_topup_zero(self):
        ex = ExchangeFixture(5, [("OLD-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        pos = make_pos(exit_order_id="OLD-2")
        bot.positions[TK] = pos
        bot._begin_reconcile_exit_intent_cycle()
        run(bot._v4_apply_exit(TK, pos, 87, 5))
        run(bot._reconcile_exit_topup_from_truth(TK, 98))
        bot._end_reconcile_exit_intent_cycle()
        self.assertEqual([int(c[2]["count"]) for c in ex.sell_posts], [5])
        self.assertEqual(ex.resting_sell_qty, 5)
        self.assertTrue(any(e == "reconcile_exit_topup_noop"
                            for e, _, _ in bot.logs))

    def test_topup_then_heal_converges_to_same_one_five_lot_exit(self):
        ex = ExchangeFixture(5, [("OLD-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        pos = make_pos(exit_order_id="OLD-2")
        bot.positions[TK] = pos
        bot._begin_reconcile_exit_intent_cycle()
        run(bot._reconcile_exit_topup_from_truth(TK, 98))
        run(bot._v4_apply_exit(TK, pos, 87, 5))
        bot._end_reconcile_exit_intent_cycle()
        self.assertEqual([int(c[2]["count"]) for c in ex.sell_posts], [3, 5])
        self.assertEqual(len(ex.orders), 1)
        self.assertEqual(ex.resting_sell_qty, 5)

    def test_full_cas_partial_then_five_regression_one_exit(self):
        ex = ExchangeFixture(2)
        self.install(ex)
        bot = make_bot()
        pos = make_pos(qty=2)
        bot.positions[TK] = pos
        bot._begin_reconcile_exit_intent_cycle()
        run(bot._v4_apply_exit(TK, pos, 87, 2))
        bot._end_reconcile_exit_intent_cycle()
        self.assertEqual(ex.resting_sell_qty, 2)

        ex.held = 5
        pos.entry_qty = 5
        bot._begin_reconcile_exit_intent_cycle()
        run(bot._v4_apply_exit(TK, pos, 87, 5))
        run(bot._reconcile_exit_topup_from_truth(TK, 98))
        bot._end_reconcile_exit_intent_cycle()
        self.assertEqual(len(ex.orders), 1)
        self.assertEqual(ex.resting_sell_qty, 5)
        self.assertLessEqual(ex.resting_sell_qty, ex.held)

    def test_covered_position_refuses_same_cycle_oversell_before_post(self):
        ex = ExchangeFixture(5, [("FULL-5", 5, 98)])
        self.install(ex)
        bot = make_bot()
        bot._begin_reconcile_exit_intent_cycle()
        oid, resp = run(bot.place_order(TK, "sell", "yes", 98, 3))
        bot._end_reconcile_exit_intent_cycle()
        self.assertEqual(oid, "")
        self.assertEqual(resp["_error"], "sell_exchange_truth_refused")
        self.assertEqual(len(ex.sell_posts), 0)
        self.assertTrue(any(e == "sell_exchange_truth_refused"
                            for e, _, _ in bot.logs))

    def test_proposal_larger_than_uncovered_capacity_is_refused(self):
        ex = ExchangeFixture(5, [("PART-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        oid, resp = run(bot.place_order(TK, "sell", "yes", 98, 5))
        self.assertEqual(oid, "")
        self.assertEqual(resp["available_sell_qty"], 3)
        self.assertEqual(ex.resting_sell_qty, 2)

    def test_sell_guard_reads_position_and_orders_immediately_before_post(self):
        ex = ExchangeFixture(5)
        self.install(ex)
        bot = make_bot()
        oid, _ = run(bot.place_order(TK, "sell", "yes", 98, 5))
        self.assertTrue(oid)
        kinds = [c[0] for c in ex.calls]
        self.assertEqual(kinds[-3:], ["GET", "GET", "POST"])

    def test_sell_guard_exhausts_authoritative_order_pagination(self):
        ex = ExchangeFixture(5)

        async def paged(_s, _ak, _pk, path, _rl):
            ex.calls.append(("GET", path))
            if "/positions?" in path:
                return {"market_positions": [{
                    "ticker": TK, "position_fp": 5}]}
            if "cursor=ORDER-P2" in path:
                return {"orders": [{
                    "order_id": "S-P2", "ticker": TK, "action": "sell",
                    "yes_price_dollars": 0.98,
                    "remaining_count_fp": 3}]}
            return {"orders": [{
                "order_id": "S-P1", "ticker": TK, "action": "sell",
                "yes_price_dollars": 0.98,
                "remaining_count_fp": 2}], "cursor": "ORDER-P2"}

        M.api_get = paged
        M.api_post = ex.post
        M.api_delete = ex.delete
        bot = make_bot()
        oid, resp = run(bot.place_order(TK, "sell", "yes", 98, 1))
        self.assertEqual(oid, "")
        self.assertEqual(resp["effective_resting_sell_qty"], 5)
        self.assertEqual(resp["available_sell_qty"], 0)
        self.assertEqual(len(ex.sell_posts), 0)

    def test_sell_guard_repeated_cursor_fails_closed(self):
        ex = ExchangeFixture(5)

        async def repeated(_s, _ak, _pk, path, _rl):
            ex.calls.append(("GET", path))
            if "/positions?" in path:
                return {"market_positions": [{
                    "ticker": TK, "position_fp": 5}]}
            return {"orders": [{
                "order_id": "S-LOOP", "ticker": TK, "action": "sell",
                "yes_price_dollars": 0.98,
                "remaining_count_fp": 1}], "cursor": "LOOP"}

        M.api_get = repeated
        M.api_post = ex.post
        M.api_delete = ex.delete
        bot = make_bot()
        oid, resp = run(bot.place_order(TK, "sell", "yes", 98, 1))
        self.assertEqual(oid, "")
        self.assertEqual(resp["_error"], "sell_guard_api_fail")
        self.assertEqual(len(ex.sell_posts), 0)

    def test_resting_sell_quantity_never_exceeds_authoritative_holding(self):
        ex = ExchangeFixture(5)
        self.install(ex)
        bot = make_bot()
        for proposed in (2, 3, 1, 5):
            run(bot.place_order(TK, "sell", "yes", 98, proposed))
            self.assertLessEqual(ex.resting_sell_qty, ex.held)
        self.assertEqual(ex.resting_sell_qty, 5)

    def test_settled_or_zero_booked_position_is_not_filled(self):
        bot = make_bot()
        zero = make_pos(qty=0)
        zero.phase = "entry_resting"
        bot.positions[TK] = zero
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {}, None, frozenset()), "absent")
        zero.settled = True
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {}, None, frozenset()), "settled")
        zero.settled = False
        zero.entry_qty = 5
        zero.phase = "active"
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {}, None, frozenset()), "absent")
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {TK: 5}, {}, None, frozenset()), "filled")

    def test_entry_resting_settled_state_cannot_create_pair_incomplete(self):
        bot = make_bot()
        stale = make_pos(qty=0)
        stale.phase = "entry_resting"
        stale.settled = True
        bot.positions[TK] = stale
        state = bot._pair_invariant_leg_state(
            TK, {}, {}, None, frozenset())
        sibling_state = "absent"
        values = {state, sibling_state}
        pair_alarm = bool({"resting", "filled"} & values) and any(
            v == "absent" or v.startswith("fitting_gap") for v in values)
        self.assertEqual(state, "settled")
        self.assertFalse(pair_alarm)

    def test_sell_truth_api_failure_refuses_without_submission(self):
        ex = ExchangeFixture(5)

        async def missing_orders(_s, _ak, _pk, path, _rl):
            ex.calls.append(("GET", path))
            if "/positions?" in path:
                return {"market_positions": [{
                    "ticker": TK, "position_fp": 5}]}
            return None

        M.api_get = missing_orders
        M.api_post = ex.post
        M.api_delete = ex.delete
        bot = make_bot()
        oid, resp = run(bot.place_order(TK, "sell", "yes", 98, 5))
        self.assertEqual(oid, "")
        self.assertEqual(resp["_error"], "sell_guard_api_fail")
        self.assertEqual(len(ex.sell_posts), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
