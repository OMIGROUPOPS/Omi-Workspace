#!/usr/bin/env python3
"""Offline smoke replay of the frozen CASUKA causal sequence.

No network object is created.  This runs the production D1-D3 methods against
the receipt-ordered in-memory exchange used by the audited fixtures.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import test_casuka_live_safety_repair as T


def replay():
    exchange = T.ExchangeFixture(2)
    old_get, old_post, old_delete = (
        T.M.api_get, T.M.api_post, T.M.api_delete)
    try:
        T.M.api_get = exchange.get
        T.M.api_post = exchange.post
        T.M.api_delete = exchange.delete
        bot = T.make_bot()
        pos = T.make_pos(qty=2)
        bot.positions[T.TK] = pos

        # Partial state: two held and exactly one two-lot resting exit.
        bot._begin_reconcile_exit_intent_cycle()
        T.run(bot._v4_apply_exit(T.TK, pos, 87, 2))
        bot._end_reconcile_exit_intent_cycle()
        partial_qty = exchange.resting_sell_qty

        # Full booking: the healer replaces the old two-lot with one five-lot;
        # the later top-up organ re-reads exchange truth and posts zero.
        exchange.held = 5
        pos.entry_qty = 5
        bot._begin_reconcile_exit_intent_cycle()
        T.run(bot._v4_apply_exit(T.TK, pos, 87, 5))
        T.run(bot._reconcile_exit_topup_from_truth(T.TK, 98))
        bot._end_reconcile_exit_intent_cycle()

        classifier = {}
        for ticker in (
                "KXWTAMATCH-26JUL27FARRIU-FAR",
                "KXITFMATCH-26JUL27VEGKAW-VEG"):
            stale = T.make_pos(qty=0)
            stale.ticker = ticker
            stale.phase = "entry_resting"
            stale.settled = True
            bot.positions[ticker] = stale
            classifier[ticker] = bot._pair_invariant_leg_state(
                ticker, {}, {}, None, frozenset())

        result = {
            "schema_version": "casuka-live-safety-offline-smoke-v1",
            "network_access": False,
            "partial_resting_sell_qty": partial_qty,
            "authoritative_held_qty": exchange.held,
            "final_resting_sell_qty": exchange.resting_sell_qty,
            "final_resting_sell_orders": len(exchange.orders),
            "sell_post_counts": [
                int(call[2]["count"]) for call in exchange.sell_posts],
            "same_cycle_topup_noop": any(
                event == "reconcile_exit_topup_noop"
                for event, _, _ in bot.logs),
            "resting_never_exceeds_held":
                exchange.resting_sell_qty <= exchange.held,
            "classifier_regressions": classifier,
        }
        expected = {
            "partial_resting_sell_qty": 2,
            "authoritative_held_qty": 5,
            "final_resting_sell_qty": 5,
            "final_resting_sell_orders": 1,
            "sell_post_counts": [2, 5],
            "same_cycle_topup_noop": True,
            "resting_never_exceeds_held": True,
        }
        for key, value in expected.items():
            if result[key] != value:
                raise AssertionError(
                    "%s: expected %r got %r" % (key, value, result[key]))
        if set(classifier.values()) != {"settled"}:
            raise AssertionError("classifier regression: %r" % classifier)
        return result
    finally:
        T.M.api_get = old_get
        T.M.api_post = old_post
        T.M.api_delete = old_delete


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True, separators=(",", ":")))
