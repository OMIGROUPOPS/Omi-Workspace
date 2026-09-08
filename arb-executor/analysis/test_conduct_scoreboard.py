"""Synthetic fill-law tests; fixture prices are not conduct tuning parameters."""
import copy
import gzip
import json
import os
from pathlib import Path
import unittest
from conduct_scoreboard import simulate_conduct, summarize

SPEC = dict(minimum_cent=1, maximum_cent=99, pair_budget=99, par=100)


def state(q, role="FALLER", low=38, ask=70, status="OK"):
    return dict(role=role, seen_true_trade_low=low, bid=ask-1, ask=ask, last=ask,
                status=status, floors={"q50": {"level_cents": q}, "q25": {"level_cents": q-2}})


def receipt(t, a, b=None):
    return dict(epoch=t, source_gate_minutes=(1000-t)/60, sides={"A": a, "B": b or state(40)})


class FillLaw(unittest.TestCase):
    def run_rule(self, receipts, a=(), b=(), rule=0):
        tapes = {"A": [[t, p, 1, i, "test"] for i, (t, p) in enumerate(a)],
                 "B": [[t, p, 1, i, "test"] for i, (t, p) in enumerate(b)]}
        return simulate_conduct("FIXTURE", ["A", "B"], receipts, tapes, 0, 1000, SPEC, rule)

    def test_strictly_later_and_bid_price_not_trade_price(self):
        r = self.run_rule([receipt(100, state(50))], [(100, 45), (101, 48)], [(102, 39)])
        self.assertEqual(r["fills"]["A"]["epoch"], 101)
        self.assertEqual(r["fills"]["A"]["cents"], 50)
        self.assertEqual(r["captured_cents"], 10)

    def test_old_order_sees_gate_print_before_reprice(self):
        r = self.run_rule([receipt(100, state(50)), receipt(200, state(40))], [(200, 49)])
        self.assertEqual(r["fills"]["A"]["cents"], 50)

    def test_reprice_retires_old_order_and_records_step_off(self):
        r = self.run_rule([receipt(100, state(50)), receipt(200, state(40))], [(201, 49)])
        self.assertNotIn("A", r["fills"])
        self.assertTrue(r["stepped_off"])

    def test_cancel_retires_rest(self):
        r = self.run_rule([receipt(100, state(50)), receipt(200, state(50, ask=49))], [(201, 45)])
        self.assertNotIn("A", r["fills"])
        self.assertEqual(r["actions"][-1]["action"], "PULL")

    def test_bell_print_excluded_and_one_side_uncredited(self):
        r = self.run_rule([receipt(100, state(50))], [(1000, 45)], [(900, 39)])
        self.assertTrue(r["one_sided"])
        self.assertEqual(r["captured_cents"], 0)

    def test_pair_cap_reverts_both_targets(self):
        r = self.run_rule([receipt(100, state(60), state(50))], [(200, 1)], [(200, 1)])
        self.assertEqual(r["actions"], [])
        self.assertEqual(r["fills"], {})

    def test_insufficient_holds_but_cannot_place(self):
        no = state(50, status="INSUFFICIENT_EVIDENCE")
        self.assertNotIn("A", self.run_rule([receipt(100, no)], [(200, 45)])["fills"])
        yes = self.run_rule([receipt(100, state(50)), receipt(150, no)], [(200, 45)])
        self.assertEqual(yes["fills"]["A"]["cents"], 50)

    def test_r1_anchor_bound_once_not_future_low(self):
        r = self.run_rule([receipt(100, state(50, "CLIMBER", low=45)),
                           receipt(200, state(40, "FALLER", low=35))], [(300, 44)], rule=1)
        self.assertEqual(r["fills"]["A"]["cents"], 45)
        self.assertEqual(r["climber_bindings"]["A"]["epoch"], 100)

    def test_r2_protects_posted_faller_level(self):
        r = self.run_rule([receipt(100, state(50)), receipt(200, state(40))], [(201, 49)], rule=2)
        self.assertEqual(r["fills"]["A"]["cents"], 50)
        self.assertFalse(r["stepped_off"])

    def test_r2_climber_is_current(self):
        r = self.run_rule([receipt(100, state(50, "CLIMBER")), receipt(200, state(40, "CLIMBER"))], [(201, 49)], rule=2)
        self.assertNotIn("A", r["fills"])

    def test_r4_faller_uses_q25(self):
        r = self.run_rule([receipt(100, state(50))], [(101, 47)], rule=4)
        self.assertEqual(r["fills"]["A"]["cents"], 48)

    def test_named_level_survives_safety_cancel(self):
        r = self.run_rule([receipt(100, state(50)), receipt(200, state(50, ask=49)),
                           receipt(300, state(40))], [(301, 49)], rule=2)
        self.assertEqual(r["fills"]["A"]["cents"], 50)

    def test_reprice_cannot_get_same_instant_trade(self):
        r = self.run_rule([receipt(100, state(40)), receipt(200, state(50))], [(200, 49)])
        self.assertNotIn("A", r["fills"])

    def test_v2_zero_unknown_and_negative_sizes_are_not_witnesses(self):
        tapes = {"A": [[101, 45, 0, 1], [102, 45, None, 2], [103, 45, -1, 3],
                       [104, 45, 1, 4]], "B": []}
        r = simulate_conduct("FIXTURE", ["A", "B"], [receipt(100, state(50))], tapes,
                             0, 1000, dict(SPEC, positive_size_fills=True), 0)
        self.assertEqual(r["fills"]["A"]["epoch"], 104)

    def test_v2_zero_size_cannot_witness_stepping_off(self):
        tapes = {"A": [[201, 49, 0, 1]], "B": []}
        r = simulate_conduct("FIXTURE", ["A", "B"], [receipt(100, state(50)), receipt(200, state(40))],
                             tapes, 0, 1000, dict(SPEC, positive_size_fills=True), 0)
        self.assertFalse(r["stepped_off"])


@unittest.skipUnless(os.environ.get("CONDUCT_PRINTS"), "Set CONDUCT_PRINTS for the private-data integration audit")
class RecordedFillAudit(unittest.TestCase):
    def test_every_query_fill_is_first_reachable_print_in_a_live_order_interval(self):
        import numpy as np
        inputs = {}
        with gzip.open(os.environ["CONDUCT_PRINTS"], "rt") as stream:
            for line in stream:
                row = json.loads(line)
                inputs[row["ticker"]] = np.asarray([p[:4] for p in row["prints"]], dtype=float)
        output = Path(__file__).with_name("conduct_scoreboard") / "ATP_MAIN" / "CONDUCT_SCOREBOARD.json"
        scoreboard = json.loads(output.read_text(encoding="utf-8"))
        for rule, rows in scoreboard["queries"].items():
            self.assertEqual(len(rows), scoreboard["summary"][rule]["eligible"])
            for row in rows:
                self.assertFalse(row["safety_violations"])
                for leg in row["rests_at_bell"]:
                    tape = inputs[row["event_id"]+"-"+leg]
                    actions = [a for a in row["actions"] if a["leg"] == leg]
                    expected = None
                    for i, action in enumerate(actions):
                        if action["new_cents"] is None: continue
                        start = np.searchsorted(tape[:, 0], action["epoch"], side="right")
                        stop = (np.searchsorted(tape[:, 0], actions[i+1]["epoch"], side="right")
                                if i+1 < len(actions) else len(tape))
                        interval = tape[start:stop]
                        reachable = np.flatnonzero((interval[:, 0] >= row["formation_epoch"])
                            & (interval[:, 0] < row["bell_epoch"]) & (interval[:, 1] <= action["new_cents"]))
                        if len(reachable):
                            first = interval[reachable[0]]
                            expected = (first[0], action["new_cents"], first[1], int(first[3]))
                            break
                    got = row["fills"].get(leg)
                    actual = (got["epoch"], got["cents"], got["print_cents"], got["print_rowid"]) if got else None
                    self.assertEqual(actual, expected, (rule, row["event_id"], leg))


if __name__ == "__main__":
    unittest.main()
