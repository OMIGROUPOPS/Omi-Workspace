"""Synthetic algorithm tests: fixtures are not fitted conduct parameters."""
import copy
import unittest
import numpy as np
from test_conduct_scoreboard import SPEC, state, receipt
from conduct_scoreboard import simulate_conduct
from conduct_scoreboard_v2 import choose_joint, ReceiptProjector
import tune_bench_v2_survivorship as b


class JointAndSafety(unittest.TestCase):
    def joint(self, outcomes):
        r = receipt(100, state(50), state(40))
        r["joint"] = dict(status="OK", ess=20, member_count=20, outcomes=outcomes)
        return r

    def test_joint_dependence_not_product_of_marginals(self):
        r = self.joint([[40, 50, 1], [50, 40, 1]])
        pick = choose_joint(r, ["A", "B"], {}, {}, {"A":None,"B":None}, SPEC)
        self.assertEqual(pick["probability_both_reach"], .5)
        self.assertEqual(pick["expected_pair_discount"], 5)
        self.assertEqual(pick["levels"], {"A":40,"B":50})

    def test_joint_maximizes_objective_not_probability(self):
        r = self.joint([[40, 40, 3], [45, 45, 1]])
        pick = choose_joint(r, ["A", "B"], {}, {}, {"A":None,"B":None}, SPEC)
        self.assertEqual(pick["levels"], {"A":40,"B":40})
        self.assertEqual(pick["expected_pair_discount"], 15)

    def test_post_only_and_named_memory_filter_candidates(self):
        r = self.joint([[40,40,1],[50,40,1],[55,40,1]])
        r["sides"]["A"]["ask"] = 55
        pick = choose_joint(r,["A","B"],{}, {"A":50},{"A":None,"B":None},SPEC)
        self.assertEqual(pick["levels"], {"A":50,"B":40})

    def test_joint_filled_price_stays_fixed(self):
        r = self.joint([[40,40,1],[50,45,1]])
        pick = choose_joint(r,["A","B"],{"A":{"cents":48}}, {},{"A":None,"B":None},SPEC)
        self.assertEqual(pick["levels"]["A"],48)
        self.assertEqual(pick["probability_both_reach"], .5)

    def test_joint_no_call_and_pair_cap(self):
        r = self.joint([[60,50,20]])
        pick = choose_joint(r,["A","B"],{}, {},{"A":None,"B":None},SPEC)
        self.assertEqual(pick["levels"],{})
        r["joint"]["status"] = "INSUFFICIENT_EVIDENCE"
        self.assertEqual(choose_joint(r,["A","B"],{}, {},{"A":None,"B":None},SPEC)["status"], "INSUFFICIENT_EVIDENCE")

    def test_r6_protects_climber_too(self):
        rows = [receipt(100,state(50,"CLIMBER")), receipt(200,state(40,"CLIMBER"))]
        tapes = {"A":[[201,49,1,0]],"B":[]}
        a = simulate_conduct("FIXTURE",["A","B"],rows,tapes,0,1000,dict(SPEC,positive_size_fills=True),2)
        z = simulate_conduct("FIXTURE",["A","B"],rows,tapes,0,1000,dict(SPEC,positive_size_fills=True),6)
        self.assertNotIn("A",a["fills"])
        self.assertEqual(z["fills"]["A"]["cents"],50)

    def test_r5_rest_fills_only_positive_later_print(self):
        rows = [self.joint([[40,40,20]])]
        tapes = {"A":[[100,39,1,0],[101,39,0,1],[102,39,1,2]],"B":[[103,39,1,3]]}
        z = simulate_conduct("FIXTURE",["A","B"],rows,tapes,0,1000,dict(SPEC,positive_size_fills=True),5)
        self.assertEqual(z["fills"]["A"]["epoch"],102)
        self.assertEqual(z["captured_cents"],20)

    def test_ask_only_veto_then_postability_rearm(self):
        first = receipt(100,state(50,ask=49))
        second = receipt(200,state(50,ask=55))
        second["ask_only_book_tick"] = True
        third = receipt(300,state(40,ask=60))
        third["ask_only_book_tick"] = True
        z = simulate_conduct("FIXTURE",["A","B"],[first,second,third],{"A":[[301,49,1,0]],"B":[]},0,1000,SPEC,0)
        self.assertEqual(z["fills"]["A"]["cents"],50)
        self.assertEqual(z["fills"]["A"]["placed_epoch"],200)


class CausalProjection(unittest.TestCase):
    def pair(self, event, start, final=50, future_at=540):
        legs = []
        for name,prices in (("A",[60,61,final]),("B",[40,39,45])):
            times = np.array([start,start+180,start+future_at],dtype=float)
            prices = np.array(prices,dtype=float)
            leg = b.Leg(name,prices[0],start,start+600,times,
                        np.column_stack((prices,prices-1,prices+1)),np.array([1,2,3]),
                        times,np.minimum.accumulate(prices),None,
                        postformation_open=prices[0],count_epoch=times,print_count_cum=np.array([1,2,3]))
            legs.append(leg)
        return b.Pair(event,"TEST",event,tuple(legs),start,"TICK")

    def test_future_query_values_and_timestamps_cannot_change_earlier_predictions(self):
        members = [self.pair(f"MEMBER{i}",1000) for i in range(12)]
        query = self.pair("QUERY",10000)
        changed = self.pair("QUERY",10000,final=5,future_at=560)
        c = dict(gates_minutes_to_bell=[8,5,1],minute_seconds=60,role_drift_cents=2,
                 no_call_ess_floor=10,quantiles=[.1,.25,.5,.75,.9])
        p = ReceiptProjector(members,c,batch_size=2)
        a = p.project(query,"RECEIPT-SIM")
        z = p.project(changed,"RECEIPT-SIM")
        self.assertEqual([r for r in a if r["epoch"]<10540], [r for r in z if r["epoch"]<10540])
        self.assertTrue(any(r["epoch"]==10180 for r in a))
        self.assertTrue(any(r["epoch"]==10120 for r in a))
        self.assertEqual(len(p.project(query,"GATE-SIM")),3)

    def test_batch_size_changes_neither_grid_nor_forecasts(self):
        members = [self.pair(f"MEMBER{i}",1000) for i in range(12)]
        query = self.pair("QUERY",10000)
        c = dict(gates_minutes_to_bell=[8,5,1],minute_seconds=60,role_drift_cents=2,
                 no_call_ess_floor=10,quantiles=[.1,.25,.5,.75,.9])
        self.assertEqual(ReceiptProjector(members,c,1).project(query,"RECEIPT-SIM"),
                         ReceiptProjector(members,c,256).project(query,"RECEIPT-SIM"))


if __name__ == "__main__":
    unittest.main()
