#!/usr/bin/env python3
"""Offline interaction and adversarial probes for P0 v4 + CASUKA D1-D3.

No network client, live account, service, cron, order, or position surface is
reachable.  The exact production methods run against frozen in-memory APIs.
"""

import asyncio
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

EXEC = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
REPO = EXEC.parent
INTEGRATION = "11e70454863e3508d5a7cbc8e83162232e3a4a09"
_CANDIDATE_TEMP = tempfile.TemporaryDirectory(
    prefix="integrated-live-safety-candidate-"
)
_CANDIDATE_ROOT = Path(_CANDIDATE_TEMP.name)
_CANDIDATE_BYTES = subprocess.check_output(
    [
        "git",
        "show",
        f"{INTEGRATION}:arb-executor/live_v4.py",
    ],
    cwd=REPO,
)
(_CANDIDATE_ROOT / "live_v4.py").write_bytes(_CANDIDATE_BYTES)
sys.path[:0] = [str(_CANDIDATE_ROOT), str(TESTS), str(EXEC)]

import live_v4 as M
import test_casuka_live_safety_repair as C
import test_p0_real_start_v4_boot_tape as P


class IntegratedLiveSafetyTests(unittest.IsolatedAsyncioTestCase):
    async def test_pending_blocks_buy_but_authoritative_exit_remains_live(self):
        now = time.time()
        bot = P.make_bot(now=now)
        exchange = C.ExchangeFixture(held=5)
        with patch.object(M, "api_get", exchange.get), \
                patch.object(M, "api_post", exchange.post), \
                patch.object(M, "api_delete", exchange.delete):
            buy_oid, buy_result = await bot._place_order_unlocked(
                P.SHI, "buy", "yes", 79, 5, post_only=True)
            sell_oid, _sell_result = await bot._place_order_unlocked(
                P.SHI, "sell", "yes", 98, 5, post_only=True)
        self.assertEqual("", buy_oid)
        self.assertEqual(
            "post_start_entry_refused", buy_result.get("_error"))
        self.assertTrue(sell_oid)
        self.assertEqual(1, len(exchange.sell_posts))

    async def test_shicha_fires_real_start_sweeps_buy_and_preserves_exit(self):
        now = time.time()
        bot = P.make_bot(now=now)
        rows = {
            P.SHI: P.trades(P.SHI, 651, now, price=79),
            P.CHA: [],
        }
        receipt = await P.hydrate_with(bot, P.TapeAPI(rows), now)
        self.assertTrue(receipt["predicate_result"])
        self.assertEqual(
            M.P0_BOOT_TAPE_REAL_START,
            bot._boot_tape_state[P.SHICHA]["state"])
        exchange = C.ExchangeFixture(held=5)
        with patch.object(M, "api_get", exchange.get), \
                patch.object(M, "api_post", exchange.post), \
                patch.object(M, "api_delete", exchange.delete):
            oid, _ = await bot._place_order_unlocked(
                P.SHI, "sell", "yes", 98, 5, post_only=True)
        self.assertTrue(oid)
        self.assertEqual(5, exchange.resting_sell_qty)

    async def test_stale_entry_intent_cannot_cross_real_start_or_sell_guard(self):
        now = time.time()
        bot = P.make_bot(now=now)
        bot._p0v4_transition(
            P.SHICHA, M.P0_BOOT_TAPE_INSUFFICIENT, "complete", {})
        posts = []

        async def get_and_fire(_s, _ak, _pk, path, _rl):
            bot._p0v4_mark_real_start(
                P.SHICHA, "simultaneous_gun", {"fixture": True})
            return {
                "market_positions": [],
                "orders": [],
            }

        async def forbidden_post(*args):
            posts.append(args)
            return {"order_id": "FORBIDDEN"}

        with patch.object(M, "api_get", get_and_fire), \
                patch.object(M, "api_post", forbidden_post):
            oid, result = await bot._place_order_unlocked(
                P.SHI, "buy", "yes", 79, 5, post_only=True)
        self.assertEqual("", oid)
        self.assertEqual("p0v4_pre_post_refused", result.get("_error"))
        self.assertEqual([], posts)

    async def test_804_pending_events_are_independently_fail_closed(self):
        bot = P.make_bot()
        bot._boot_tape_state.clear()
        for i in range(804):
            event = "KXITFMATCH-26JUL28E%04d" % i
            ticker = event + "-A"
            bot.event_tickers[event] = {ticker}
            bot._p0v4_register_entry_market(event, ticker, 1000 + i)
        self.assertEqual(804, len(bot._boot_tape_state))
        self.assertTrue(all(
            bot._p0v4_entry_authority_gate(event)
            == (True, "boot_tape_not_ready")
            for event in bot._boot_tape_state))


class IntegratedCasukaAdversarialProbes(unittest.TestCase):
    """Twenty-one named probes matching the independent CASUKA audit matrix."""

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

    def test_d1_four_serialization_probes(self):
        # P1 heal -> top-up; P2 top-up -> heal.
        for ordering in ("heal_topup", "topup_heal"):
            with self.subTest(probe=ordering):
                ex = C.ExchangeFixture(5, [("OLD-2", 2, 98)])
                self.install(ex)
                bot = C.make_bot()
                pos = C.make_pos(exit_order_id="OLD-2")
                bot.positions[C.TK] = pos
                bot._begin_reconcile_exit_intent_cycle()
                if ordering == "heal_topup":
                    C.run(bot._v4_apply_exit(C.TK, pos, 87, 5))
                    C.run(bot._reconcile_exit_topup_from_truth(C.TK, 98))
                else:
                    C.run(bot._reconcile_exit_topup_from_truth(C.TK, 98))
                    C.run(bot._v4_apply_exit(C.TK, pos, 87, 5))
                bot._end_reconcile_exit_intent_cycle()
                self.assertEqual(5, ex.resting_sell_qty)
                self.assertEqual(1, len(ex.orders))
        # P3 two-cycle idempotence; P4 resting never exceeds held.
        ex = C.ExchangeFixture(5)
        self.install(ex)
        bot = C.make_bot()
        pos = C.make_pos()
        bot.positions[C.TK] = pos
        for _ in range(2):
            bot._begin_reconcile_exit_intent_cycle()
            C.run(bot._v4_apply_exit(C.TK, pos, 87, 5))
            C.run(bot._reconcile_exit_topup_from_truth(C.TK, 98))
            bot._end_reconcile_exit_intent_cycle()
            self.assertLessEqual(ex.resting_sell_qty, ex.held)
        self.assertEqual(5, ex.resting_sell_qty)

    def test_d2_nine_sell_clamp_probes(self):
        # P5 oversell, P6 exact, P7 fully covered.
        cases = [
            ("oversell", 5, [], 6, False),
            ("exact", 5, [], 5, True),
            ("covered", 5, [("FULL", 5, 98)], 1, False),
            ("zero", 5, [], 0, False),       # P8
            ("negative", 5, [], -1, False),  # P8 companion
            ("zero_position", 0, [], 1, False),  # P10
        ]
        for name, held, sells, proposed, allowed in cases:
            with self.subTest(probe=name):
                ex = C.ExchangeFixture(held, sells)
                self.install(ex)
                bot = C.make_bot()
                oid, _ = C.run(
                    bot.place_order(C.TK, "sell", "yes", 98, proposed))
                self.assertEqual(bool(oid), allowed)
                self.assertLessEqual(ex.resting_sell_qty, ex.held)
        # P9 fractional holding never rounds up.
        ex = C.ExchangeFixture(5.58, [("FIVE", 5, 98)])
        self.install(ex)
        bot = C.make_bot()
        oid, _ = C.run(bot.place_order(C.TK, "sell", "yes", 98, 1))
        self.assertEqual("", oid)
        # P11 unavailable API and P13 refusal receipt/alert path.
        ex = C.ExchangeFixture(5)

        async def unavailable(*_args):
            return None

        M.api_get = unavailable
        M.api_post = ex.post
        bot = C.make_bot()
        oid, result = C.run(
            bot.place_order(C.TK, "sell", "yes", 98, 5))
        self.assertEqual("", oid)
        self.assertEqual("sell_guard_api_fail", result["_error"])
        # P12 buy path never enters the sell clamp.
        bot = P.make_bot()
        bot._p0v4_transition(
            P.SHICHA, M.P0_BOOT_TAPE_INSUFFICIENT, "complete", {})
        sell_guard_calls = []

        async def forbidden_sell_guard(*_args):
            sell_guard_calls.append(True)
            raise AssertionError("buy entered sell guard")

        bot._authoritative_sell_snapshot = forbidden_sell_guard
        _oid, result = C.run(
            bot._place_order_unlocked(
                P.SHI, "buy", "yes", 79, 5, post_only=True))
        self.assertEqual([], sell_guard_calls)
        self.assertNotIn(
            result.get("_error"),
            {"sell_guard_api_fail", "sell_exchange_truth_refused"})

    def test_d2_pagination_and_repeated_cursor_probes(self):
        # P20 full order pagination; P21 repeated cursor fails closed.
        ex = C.ExchangeFixture(5)

        async def paged(_s, _ak, _pk, path, _rl):
            if "/positions?" in path:
                return {"market_positions": [{
                    "ticker": C.TK, "position_fp": 5}]}
            if "cursor=ORDER-P2" in path:
                return {"orders": [{
                    "order_id": "S-P2", "ticker": C.TK,
                    "action": "sell", "yes_price_dollars": 0.98,
                    "remaining_count_fp": 3}]}
            return {"orders": [{
                "order_id": "S-P1", "ticker": C.TK,
                "action": "sell", "yes_price_dollars": 0.98,
                "remaining_count_fp": 2}],
                "cursor": "ORDER-P2"}

        M.api_get = paged
        M.api_post = ex.post
        M.api_delete = ex.delete
        bot = C.make_bot()
        oid, result = C.run(
            bot.place_order(C.TK, "sell", "yes", 98, 1))
        self.assertEqual("", oid)
        self.assertEqual(0, result["available_sell_qty"])

        async def repeated(_s, _ak, _pk, path, _rl):
            if "/positions?" in path:
                return {"market_positions": [{
                    "ticker": C.TK, "position_fp": 5}]}
            return {"orders": [{
                "order_id": "S-LOOP", "ticker": C.TK,
                "action": "sell", "yes_price_dollars": 0.98,
                "remaining_count_fp": 1}], "cursor": "LOOP"}

        M.api_get = repeated
        bot = C.make_bot()
        oid, result = C.run(
            bot.place_order(C.TK, "sell", "yes", 98, 1))
        self.assertEqual("", oid)
        self.assertEqual("sell_guard_api_fail", result["_error"])

    def test_d3_six_classifier_probes(self):
        bot = C.make_bot()
        pos = C.make_pos(qty=0)
        pos.phase = "entry_resting"
        bot.positions[C.TK] = pos
        # P14 zero booked, P15 genuine resting.
        self.assertEqual(
            "absent", bot._pair_invariant_leg_state(
                C.TK, {}, {}, None, frozenset()))
        self.assertEqual(
            "resting", bot._pair_invariant_leg_state(
                C.TK, {}, {C.TK: 5}, None, frozenset()))
        # P16 settled.
        pos.settled = True
        self.assertEqual(
            "settled", bot._pair_invariant_leg_state(
                C.TK, {}, {}, None, frozenset()))
        # P17 stale booked with no holding; P18 genuine fill.
        pos.settled = False
        pos.phase = "active"
        pos.entry_qty = 5
        self.assertEqual(
            "absent", bot._pair_invariant_leg_state(
                C.TK, {}, {}, None, frozenset()))
        self.assertEqual(
            "filled", bot._pair_invariant_leg_state(
                C.TK, {C.TK: 5}, {}, None, frozenset()))
        # P19 fitting-gap naming remains intact.
        self.assertEqual(
            "fitting_gap:GAP",
            bot._pair_invariant_leg_state(
                C.TK, {}, {}, ("GAP",), frozenset({"GAP"})))


if __name__ == "__main__":
    unittest.main(verbosity=2)
