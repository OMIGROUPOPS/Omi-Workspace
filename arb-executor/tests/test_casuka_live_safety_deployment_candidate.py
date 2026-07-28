#!/usr/bin/env python3
"""Deployment-candidate parity and adversarial probes for CASUKA D1-D3.

Everything here is offline.  The exchange is the receipt-ordered in-memory
fixture from the independently audited repair tests.
"""
import ast
import asyncio
import copy
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import live_v4 as M
from test_casuka_live_safety_repair import (
    ExchangeFixture,
    ET,
    TK,
    make_bot,
    make_pos,
    run,
)


AUDITED_REPAIR = "94be41137c0b64bfa448546c8bc3ee7c4ae32a60"
RUNNING_PARENT = "bb085ce06db5932049af85f927a7f9316ad76816"
P0_V2 = "3f5d85d47a49083dd40056b1866191c649057b7b"
P0_V3 = "a4996dd00e82ed3534f97a09251697f1d82dbbab"


def git_source(commit):
    return subprocess.check_output(
        ["git", "show", "%s:arb-executor/live_v4.py" % commit],
        cwd=REPO, text=True, encoding="utf-8")


def class_methods(source):
    tree = ast.parse(source)
    cls = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "LiveV3")
    return {
        node.name: node
        for node in cls.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def normalized(node):
    return ast.dump(node, annotate_fields=True, include_attributes=False)


def call_names(node):
    names = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Attribute):
            names.append(func.attr)
        elif isinstance(func, ast.Name):
            names.append(func.id)
    return names


def casuka_place_order_blocks(node):
    """Return only the two D2 statement blocks from _place_order_unlocked."""
    candidates = []
    for stmt in ast.walk(node):
        if not isinstance(stmt, ast.If):
            continue
        names = set(call_names(stmt))
        if ("_authoritative_sell_snapshot" in names
                or "_record_exit_intent_post" in names):
            candidates.append(stmt)
    # ast.walk(parent_if) includes calls from nested if statements.  Keep the
    # narrowest matching statement so the enclosing response branch is not
    # accidentally treated as part of D2.
    found = []
    for stmt in candidates:
        nested = {
            id(child) for child in ast.walk(stmt)
            if child is not stmt and isinstance(child, ast.If)
            and ("_authoritative_sell_snapshot" in set(call_names(child))
                 or "_record_exit_intent_post" in set(call_names(child)))
        }
        if not nested:
            found.append(stmt)
    return sorted(normalized(stmt) for stmt in found)


class AuditorProbeParityTests(unittest.TestCase):
    """The 21 independently named D1/D2/D3 probes, one test per probe."""

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

    # D1: four probes.
    def test_d1_heal_then_topup_one_five_lot_topup_zero(self):
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

    def test_d1_topup_then_heal_converges(self):
        ex = ExchangeFixture(5, [("OLD-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        pos = make_pos(exit_order_id="OLD-2")
        bot.positions[TK] = pos
        bot._begin_reconcile_exit_intent_cycle()
        run(bot._reconcile_exit_topup_from_truth(TK, 98))
        run(bot._v4_apply_exit(TK, pos, 87, 5))
        bot._end_reconcile_exit_intent_cycle()
        self.assertEqual(len(ex.orders), 1)
        self.assertEqual(ex.resting_sell_qty, 5)

    def test_d1_two_cycle_idempotent(self):
        ex = ExchangeFixture(5, [("OLD-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        pos = make_pos(exit_order_id="OLD-2")
        bot.positions[TK] = pos
        for _ in range(2):
            bot._begin_reconcile_exit_intent_cycle()
            run(bot._v4_apply_exit(TK, pos, 87, 5))
            run(bot._reconcile_exit_topup_from_truth(TK, 98))
            bot._end_reconcile_exit_intent_cycle()
            self.assertEqual(len(ex.orders), 1)
            self.assertEqual(ex.resting_sell_qty, 5)

    def test_d1_conservation_resting_never_exceeds_held(self):
        ex = ExchangeFixture(5)
        self.install(ex)
        bot = make_bot()
        for proposed in (2, 3, 1, 5):
            run(bot.place_order(TK, "sell", "yes", 98, proposed))
            self.assertLessEqual(ex.resting_sell_qty, ex.held)

    # D2: nine probes.
    def test_d2_oversell_refused_in_full_pre_post(self):
        ex = ExchangeFixture(5, [("PART-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 5))
        self.assertEqual(oid, "")
        self.assertEqual(response["_error"], "sell_exchange_truth_refused")
        self.assertEqual(len(ex.sell_posts), 0)

    def test_d2_exact_available_allowed(self):
        ex = ExchangeFixture(5, [("PART-2", 2, 98)])
        self.install(ex)
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 3))
        self.assertTrue(oid)
        self.assertNotIn("_error", response)
        self.assertEqual(ex.resting_sell_qty, 5)

    def test_d2_covered_refuses(self):
        ex = ExchangeFixture(5, [("FULL-5", 5, 98)])
        self.install(ex)
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 1))
        self.assertEqual(oid, "")
        self.assertEqual(response["available_sell_qty"], 0)

    def test_d2_zero_and_negative_refused(self):
        for count in (0, -1):
            ex = ExchangeFixture(5)
            self.install(ex)
            bot = make_bot()
            oid, response = run(
                bot.place_order(TK, "sell", "yes", 98, count))
            self.assertEqual(oid, "")
            self.assertEqual(response["reason"], "nonpositive_sell_quantity")
            self.assertEqual(len(ex.sell_posts), 0)

    def test_d2_fractional_never_rounds_up(self):
        ex = ExchangeFixture(4.5)
        self.install(ex)
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 5))
        self.assertEqual(oid, "")
        self.assertEqual(response["available_sell_qty"], 4.5)
        self.assertEqual(len(ex.sell_posts), 0)

    def test_d2_zero_position_refused(self):
        ex = ExchangeFixture(0)
        self.install(ex)
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 1))
        self.assertEqual(oid, "")
        self.assertEqual(response["exchange_position_qty"], 0)

    def test_d2_api_unavailable_fails_closed(self):
        ex = ExchangeFixture(5)

        async def missing(_s, _ak, _pk, path, _rl):
            ex.calls.append(("GET", path))
            return None

        M.api_get = missing
        M.api_post = ex.post
        M.api_delete = ex.delete
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 5))
        self.assertEqual(oid, "")
        self.assertEqual(response["_error"], "sell_guard_api_fail")
        self.assertEqual(len(ex.sell_posts), 0)

    def test_d2_buy_path_ungated(self):
        ex = ExchangeFixture(0)
        self.install(ex)
        bot = make_bot()
        bot.config["sizing"] = {"entry_contracts": 5}
        # Deliberate taker form bypasses unrelated maker-band/horizon policy;
        # the assertion here is solely that D2 adds no exchange-truth GET to
        # any buy.
        oid, response = run(
            bot.place_order(TK, "buy", "yes", 2, 5, post_only=False))
        self.assertTrue(oid)
        self.assertNotIn("_error", response)
        # Existing buy-side exchange-truth checks remain intact; D2 neither
        # refuses the buy nor emits a sell-guard receipt.
        self.assertTrue(any(c[0] == "POST" for c in ex.calls))
        self.assertFalse(any(
            event.startswith("sell_") for event, _, _ in bot.logs))

    def test_d2_refusal_receipted_and_alert_wired(self):
        ex = ExchangeFixture(5, [("FULL-5", 5, 98)])
        self.install(ex)
        bot = make_bot()
        oid, _ = run(bot.place_order(TK, "sell", "yes", 98, 1))
        self.assertEqual(oid, "")
        events = [event for event, _, _ in bot.logs]
        self.assertIn("sell_exchange_truth_refused", events)

    def test_d2_position_pagination_is_exhausted(self):
        ex = ExchangeFixture(0)

        async def paged(_s, _ak, _pk, path, _rl):
            ex.calls.append(("GET", path))
            if "/positions?" in path:
                if "cursor=POS-P2" in path:
                    return {"market_positions": [{
                        "ticker": TK, "position_fp": 3}]}
                return {"market_positions": [{
                    "ticker": TK, "position_fp": 2}], "cursor": "POS-P2"}
            return {"orders": []}

        M.api_get = paged
        M.api_post = ex.post
        M.api_delete = ex.delete
        bot = make_bot()
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 6))
        self.assertEqual(oid, "")
        self.assertEqual(response["exchange_position_qty"], 5)
        self.assertEqual(len(ex.sell_posts), 0)

    def test_d2_order_pagination_is_exhausted(self):
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
        oid, response = run(bot.place_order(TK, "sell", "yes", 98, 1))
        self.assertEqual(oid, "")
        self.assertEqual(response["effective_resting_sell_qty"], 5)
        self.assertEqual(len(ex.sell_posts), 0)

    # D3: six probes.
    def test_d3_zero_booked_entry_resting_absent(self):
        bot = make_bot()
        pos = make_pos(qty=0)
        pos.phase = "entry_resting"
        bot.positions[TK] = pos
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {}, None, frozenset()), "absent")

    def test_d3_resting_is_resting(self):
        bot = make_bot()
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {TK: [{"order_id": "B"}]}, None, frozenset()),
            "resting")

    def test_d3_settled_is_settled(self):
        bot = make_bot()
        pos = make_pos(qty=5)
        pos.settled = True
        bot.positions[TK] = pos
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {TK: 5}, {}, None, frozenset()), "settled")

    def test_d3_stale_booked_without_holding_absent(self):
        bot = make_bot()
        bot.positions[TK] = make_pos(qty=5)
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {}, None, frozenset()), "absent")

    def test_d3_genuine_booked_and_unsettled_is_filled(self):
        bot = make_bot()
        bot.positions[TK] = make_pos(qty=5)
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {TK: 5}, {}, None, frozenset()), "filled")

    def test_d3_fitting_gap_preserved(self):
        bot = make_bot()
        refusal = ("missing_top5", "receipt")
        self.assertEqual(bot._pair_invariant_leg_state(
            TK, {}, {}, refusal, frozenset({"missing_top5"})),
            "fitting_gap:missing_top5")


class DeploymentEquivalenceTests(unittest.TestCase):
    def test_all_standalone_casuka_methods_ast_identical_to_audited_repair(self):
        candidate = class_methods(
            (REPO / "arb-executor" / "live_v4.py").read_text(
                encoding="utf-8"))
        audited = class_methods(git_source(AUDITED_REPAIR))
        names = (
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
            "cancel_order",
            "_v4_apply_exit",
            "_pair_invariant_leg_state",
            "_post_boot_book_audit",
            "reconcile",
        )
        for name in names:
            self.assertEqual(normalized(candidate[name]),
                             normalized(audited[name]), name)

    def test_d2_blocks_inside_place_order_are_ast_identical(self):
        candidate = class_methods(
            (REPO / "arb-executor" / "live_v4.py").read_text(
                encoding="utf-8"))
        audited = class_methods(git_source(AUDITED_REPAIR))
        self.assertEqual(
            casuka_place_order_blocks(candidate["_place_order_unlocked"]),
            casuka_place_order_blocks(audited["_place_order_unlocked"]))
        self.assertEqual(
            len(casuka_place_order_blocks(
                candidate["_place_order_unlocked"])), 2)

    def test_p0_guard_surfaces_remain_running_parent_ast(self):
        candidate = class_methods(
            (REPO / "arb-executor" / "live_v4.py").read_text(
                encoding="utf-8"))
        parent = class_methods(git_source(RUNNING_PARENT))
        names = (
            "__init__",
            "_entry_start_gate",
            "_gun_stamp",
            "_gun_sweep_entry_bids",
            "_start_gate_cancel_resting",
            "_strong_live_evidence",
            "_v4_manage_resting",
            "_v4_manage_resting_inner",
            "discover_markets",
            "run",
            "validate_resting_buys",
        )
        for name in names:
            if name in parent or name in candidate:
                self.assertEqual(
                    normalized(candidate[name]) if name in candidate else None,
                    normalized(parent[name]) if name in parent else None,
                    name)

    def test_p0_v2_v3_function_deltas_are_not_present(self):
        parent = class_methods(git_source(RUNNING_PARENT))
        candidate = class_methods(
            (REPO / "arb-executor" / "live_v4.py").read_text(
                encoding="utf-8"))
        v3 = class_methods(git_source(P0_V3))
        changed_by_p0 = {
            name for name in set(parent) | set(v3)
            if (normalized(parent[name]) if name in parent else None)
            != (normalized(v3[name]) if name in v3 else None)
        }
        self.assertTrue({
            "_gun_sweep_entry_bids", "_start_gate_cancel_resting",
            "_v4_manage_resting", "validate_resting_buys"} <= changed_by_p0)
        for name in changed_by_p0 - {"_place_order_unlocked"}:
            self.assertEqual(
                normalized(candidate[name]) if name in candidate else None,
                normalized(parent[name]) if name in parent else None,
                name)

    def test_farriu_and_vegkaw_classifier_regressions(self):
        bot = make_bot()
        for ticker in (
                "KXWTAMATCH-26JUL27FARRIU-FAR",
                "KXITFMATCH-26JUL27VEGKAW-VEG"):
            stale = make_pos(qty=0)
            stale.ticker = ticker
            stale.phase = "entry_resting"
            stale.settled = True
            bot.positions[ticker] = stale
            self.assertEqual(bot._pair_invariant_leg_state(
                ticker, {}, {}, None, frozenset()), "settled")


if __name__ == "__main__":
    unittest.main(verbosity=2)
