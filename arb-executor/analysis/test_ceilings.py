"""Small synthetic fixtures, not pool or conduct tuning parameters."""
from copy import deepcopy
import math
import unittest
import ceilings as x
from test_conduct_scoreboard import SPEC, receipt, state


class OracleTests(unittest.TestCase):
    def test_strict_future_positive_size_before_bell(self):
        rows = [receipt(100, state(50)), receipt(200, state(50))]
        tapes = {"A":[[100, 1, 1], [101, 2, 0], [150, 30, 1], [200, 25, 1], [1000, 1, 1]], "B":[]}
        out, counts = x.oracle_forecasts(rows, tapes, 0, 1000)
        self.assertEqual(x.q50(out[0]["sides"]["A"]), 25)
        self.assertIsNone(x.q50(out[1]["sides"]["A"]))
        self.assertIsNone(x.q50(out[0]["sides"]["B"]))
        self.assertEqual(counts["oracle_available"], 1)

    def test_only_q_changes_and_input_untouched(self):
        rows = [receipt(100, state(50, status="INSUFFICIENT_EVIDENCE"))]
        rows[0]["sides"]["A"]["floors"]["q50"]["minutes_to_bell"] = 4
        before = deepcopy(rows)
        out, _ = x.oracle_forecasts(rows, {"A":[[200, 30, 1]], "B":[]}, 0, 1000)
        self.assertEqual(rows, before)
        for leg in ("A", "B"):
            out[0]["sides"][leg]["floors"]["q50"]["level_cents"] = x.q50(before[0]["sides"][leg])
        self.assertEqual(out, before)

    def test_fence_is_not_promoted_by_oracle(self):
        rows = [receipt(100, state(50, status="INSUFFICIENT_EVIDENCE"))]
        tapes = {"A":[[200, 30, 1, 1]], "B":[]}
        out, _ = x.oracle_forecasts(rows, tapes, 0, 1000)
        result = x.c.simulate_conduct("fixture", ["A","B"], out, tapes, 0, 1000, dict(SPEC, positive_size_fills=True), 0)
        self.assertNotIn("A", result["fills"])

    def test_suffix_min_matches_brute_force(self):
        rows = [receipt(t, state(50)) for t in (0, 1, 2, 3, 4, 5)]
        tapes = {"A":[[1, 50, 1], [1, 40, 1], [2, 1, 0], [3, 35, 1], [4, 40, 1]], "B":[]}
        out, _ = x.oracle_forecasts(rows, tapes, 0, 5)
        for old, new in zip(rows, out):
            eligible = [p[1] for p in tapes["A"] if old["epoch"] < p[0] < 5 and p[2] > 0]
            self.assertEqual(x.q50(new["sides"]["A"]), min(eligible) if eligible else None)


class BudgetTests(unittest.TestCase):
    def test_release_cap_keeps_negative_capture(self):
        rows = [receipt(100, state(60), state(50))]
        tapes = {"A":[[200, 59, 1, 1]], "B":[[201, 49, 1, 2]]}
        normal = x.c.simulate_conduct("fixture", ["A","B"], rows, tapes, 0, 1000, SPEC, 0)
        unsafe = x.c.simulate_conduct("fixture", ["A","B"], rows, tapes, 0, 1000, dict(SPEC, pair_budget=math.inf), 0)
        self.assertFalse(normal["completed"])
        self.assertEqual(unsafe["captured_cents"], -10)
        audit = x.commitment_audit(unsafe, ["A","B"], SPEC["pair_budget"], SPEC["par"])
        self.assertTrue(audit["completed_above_par"])
        self.assertEqual(audit["maximum_filled_plus_rest_cents"], 110)

    def test_pair_actions_are_atomic(self):
        result = dict(fills={}, completed=False, pair_sum=None, actions=[
            dict(epoch=1, leg="A", new_cents=40), dict(epoch=1, leg="B", new_cents=59),
            dict(epoch=2, leg="A", new_cents=59), dict(epoch=2, leg="B", new_cents=40)])
        audit = x.commitment_audit(result, ["A","B"], 99, 100)
        self.assertEqual(audit["maximum_filled_plus_rest_cents"], 99)
        self.assertFalse(audit["ever_above_par"])


class OrderTests(unittest.TestCase):
    def result(self, rows, a, b):
        tapes = {"A":[[t,p,1,i] for i,(t,p) in enumerate(a)], "B":[[t,p,1,i] for i,(t,p) in enumerate(b)]}
        return x.c.simulate_conduct("fixture", ["A","B"], rows, tapes, 0, 1000, SPEC, 0)

    def test_same_timestamp_receipt_not_used_for_fill_q(self):
        rows = [receipt(100, state(50)), receipt(200, state(30))]
        result = self.result(rows, [(200,49)], [(201,39)])
        record = x.fill_order(result, rows, ["A","B"], SPEC, 60)
        self.assertEqual(record["receipt_epoch"], 100)
        self.assertEqual(record["fills"][0]["current_q"], 50)
        self.assertEqual(record["underdog_cap_headroom_cents"], 9)

    def test_current_q_and_placement_q_are_separate(self):
        rows = [receipt(100, state(50)), receipt(150, state(45, ask=40))]
        rows[1]["sides"]["A"]["bid"] = 40  # Locked book holds old rest.
        result = self.result(rows, [(200,49)], [])
        record = x.fill_order(result, rows, ["A","B"], SPEC, 60)
        self.assertEqual(record["fills"][0]["premium_to_current_q"], 5)
        self.assertEqual(record["fills"][0]["premium_to_placement_q"], 0)

    def test_dog_first_uses_favourite_rest_commitment(self):
        rows = [receipt(100, state(50))]
        result = self.result(rows, [], [(200,39)])
        record = x.fill_order(result, rows, ["A","B"], SPEC, 60)
        self.assertEqual(record["first_side"], "underdog")
        self.assertEqual(record["favourite_commitment_source"], "RESTING")
        self.assertEqual(record["underdog_effective_cap_cents"], 49)

    def test_simultaneous_not_lexical_first(self):
        rows = [receipt(100, state(50))]
        result = self.result(rows, [(200,49)], [(200,39)])
        record = x.fill_order(result, rows, ["A","B"], SPEC, 60)
        self.assertEqual(record["first_side"], "SAME_TIMESTAMP")
        self.assertTrue(all(f["first"] for f in record["fills"]))

    def test_missing_q_remains_missing(self):
        rows = [receipt(100, state(50)), receipt(150, state(50))]
        rows[1]["sides"]["B"]["floors"] = {}
        rows[1]["sides"]["B"]["status"] = "INSUFFICIENT_EVIDENCE"
        result = self.result(rows, [(200,49)], [])
        record = x.fill_order(result, rows, ["A","B"], SPEC, 60)
        self.assertIsNone(record["underdog_cap_headroom_cents"])

    def test_empty_distribution_does_not_impute_zero(self):
        record = x.distribution([None, float("nan")], [.1,.25,.5,.75,.9])
        self.assertEqual(record["n"], 0)
        self.assertEqual(record["missing"], 2)
        self.assertIsNone(record["mean"])


if __name__ == "__main__":
    unittest.main()
