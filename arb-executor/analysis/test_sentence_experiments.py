"""Small deterministic fixtures; numbers here are test data, not model rules."""
import unittest
import numpy as np
import sentence_experiments as s


class PassageTests(unittest.TestCase):
    def test_size_and_span_filter(self):
        rows = [[0, 40, 1], [1, 30, 0], [2, 38, 2], [3, 20, 3]]
        np.testing.assert_array_equal(s.positive_tape(rows, 1, 3), [[2, 38]])

    def test_later_only_and_before_bell(self):
        tape = np.array([[10, 20], [11, 31], [12, 30], [20, 1]])
        self.assertEqual(s.first_passage(tape, 10, 20, 30, 1), 8)
        self.assertIsNone(s.first_passage(tape, 12, 20, 29, 1))

    def test_floor_earliest_tie(self):
        tape = np.array([[10, 2], [11, 31], [12, 30], [13, 30], [20, 1]])
        self.assertEqual(s.future_floor(tape, 10, 20, 1), (30, 8))

    def test_no_print_not_zero_error(self):
        self.assertEqual(s.future_floor(np.empty((0, 2)), 0, 10, 1), (None, None))

    def test_majority_nonhits_censor_median(self):
        self.assertIsNone(s.censored_median(np.array([7, np.nan]), np.array([1, 2]), 10, .5))

    def test_exact_half_hits_inverse_cdf(self):
        self.assertEqual(s.censored_median(np.array([7, np.nan]), np.array([1, 1]), 10, .5), 7)

    def test_chronological_median_not_mtb_lower_quantile(self):
        self.assertEqual(s.censored_median(np.array([9, 1]), np.array([1, 1]), 10, .5), 9)

    def test_zero_weight_nonhits_do_not_censor(self):
        self.assertEqual(s.censored_median(np.array([4, np.nan]), np.array([1, 0]), 10, .5), 4)

    def test_scale_invariant(self):
        hits, weights = np.array([9, 4, np.nan]), np.array([1, 2, 1])
        self.assertEqual(s.censored_median(hits, weights, 10, .5),
                         s.censored_median(hits, weights*7, 10, .5))

    def test_ties_do_not_count_as_win(self):
        criterion = dict(minimum_matched_queries=2, minimum_step_strictly_closer_share=.5)
        result = s.win_record([1, 1], [1, 1], criterion)
        self.assertFalse(result["filed_matched_win"])
        self.assertEqual(result["ties"], 2)

    def test_no_finite_deadline_no_matched_mae(self):
        criterion = dict(minimum_matched_queries=2, minimum_step_strictly_closer_share=.5)
        result = s.win_record([None], [5], criterion)
        self.assertEqual(result["n"], 0)
        self.assertIsNone(result["delta_mae"])


class GuardTests(unittest.TestCase):
    def test_pair_cap_reason_and_action_assertion(self):
        spec = dict(minimum_cent=1, maximum_cent=99, pair_budget=99)
        state = dict(status="OK", bid=60, ask=70, floors={"q50": {"level_cents": 60}})
        rows = [dict(epoch=10, sides={"AAA": state, "BBB": state})]
        result = dict(event_id="fixture", fills={}, actions=[], rests_at_bell={"AAA":None,"BBB":None})
        got = s.guard_diagnostics(rows, result, spec)
        self.assertEqual(got["AAA"]["reasons"], {"PAIR_CAP_HOLD":1})
        self.assertEqual(got["AAA"]["postable_receipts"], 1)
        result["actions"] = [dict(epoch=10, leg="AAA", new_cents=60)]
        with self.assertRaises(ValueError): s.guard_diagnostics(rows, result, spec)


class CausalPoolTests(unittest.TestCase):
    def inputs(self):
        from test_conduct_scoreboard_v2 import CausalProjection
        fixture = CausalProjection()
        members = [fixture.pair(f"MEMBER{i}",1000) for i in range(12)]
        query = fixture.pair("QUERY",10000)
        changed = fixture.pair("QUERY",10000,final=5,future_at=560)
        for p in members+[query, changed]:
            for leg in p.legs: leg.family = "DRIFT_UP"
        contract = dict(gates_minutes_to_bell=[8,5,1],minute_seconds=60,role_drift_cents=2,
                        no_call_ess_floor=10,quantiles=[.1,.25,.5,.75,.9])
        tapes = {p.event_id:{leg.leg_id:np.column_stack((leg.epoch,leg.values[:,0])) for leg in p.legs}
                 for p in members+[query]}
        return members,query,changed,contract,tapes

    def test_gate_predictions_do_not_read_query_future(self):
        from conduct_scoreboard_v2 import ReceiptProjector
        members,q,z,contract,tapes = self.inputs()
        reference = ReceiptProjector(members,contract)
        projector = s.GateExperiments(members,contract,tapes)
        a = projector.project(q,reference.project(q,"GATE-SIM"))
        zz = projector.project(z,reference.project(z,"GATE-SIM"))
        for key in ("q","x","ess","family_called"):
            self.assertEqual([r[key] for r in a[0] if r["gate"]>1], [r[key] for r in zz[0] if r["gate"]>1])
        self.assertEqual([r["first_passage_x"] for r in a[1] if r["gate"]>1],
                         [r["first_passage_x"] for r in zz[1] if r["gate"]>1])

    def test_native_shared_equals_gate_shared_at_gates(self):
        from conduct_scoreboard_v2 import ReceiptProjector
        from sentence_shared_pool_native import shared_projection
        members,q,z,contract,tapes = self.inputs()
        reference = ReceiptProjector(members,contract)
        baseline = reference.project(q,"GATE-SIM")
        expected = s.GateExperiments(members,contract,tapes).project(q,baseline)[2]["SHARED_INTERSECTION"]
        actual = shared_projection(q,baseline,members,contract,1)
        self.assertEqual([r["sides"] for r in actual], [r["sides"] for r in expected])

    def test_member_walk_forward_self_and_same_day_exclusions(self):
        members,q,z,contract,tapes = self.inputs()
        from copy import deepcopy
        same_day = deepcopy(members[0]); same_day.date=q.date; same_day.event_id="SAME_DAY"
        future = deepcopy(q); future.event_id="FUTURE"
        found,_ = s.b.initial_pool(q,members+[q,same_day,future])
        self.assertEqual([p.event_id for p in found], [p.event_id for p in members])


if __name__ == "__main__":
    unittest.main()
