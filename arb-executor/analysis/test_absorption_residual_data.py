import copy
import unittest
import numpy as np
from absorption_residual_data import FirstAtlas, corrected_refill
from conduct_scoreboard_v2 import ReceiptProjector
from tune_bench_v2_survivorship import Leg, Pair


def pair(event, date, base, formation):
    epochs = formation+np.arange(5)*60
    legs = []
    for side, prices in enumerate(([base,base-1,base-2,base+1,base], [100-base,101-base,102-base,99-base,100-base])):
        values = np.column_stack((prices,np.array(prices)-1,np.array(prices)+1)).astype(float)
        leg = Leg(str(side),float(prices[0]),float(formation),float(formation+300),epochs,values,
            np.arange(5,dtype=float),epochs,np.minimum.accumulate(prices),None,
            postformation_open=float(prices[0]),count_epoch=epochs,print_count_cum=np.arange(5)+1)
        legs.append(leg)
    return Pair(event,'TEST',date,tuple(legs),float(formation),'TICK')


class DataTests(unittest.TestCase):
    def test_cached_first_matches_reference_atlas_exactly(self):
        members = [pair('m'+str(i),'prior'+str(i),60+i,1000+i*400) for i in range(12)]
        query = pair('query','later',63,10000)
        contract = dict(gates_minutes_to_bell=[4,3,2,1],minute_seconds=60,role_drift_cents=2,
                        no_call_ess_floor=1,quantiles=[.1,.25,.5,.75,.9])
        original = ReceiptProjector(members,contract).project(query,'GATE-SIM')
        cache = FirstAtlas(members,contract)
        new = cache.project(query)
        again = cache.project(query)
        self.assertEqual(new,again)
        for row in new:
            ref=next(r for r in original if r['source_gate_minutes']==row['gate'])['sides'][row['leg']]
            self.assertEqual(row['role'],ref['role'])
            self.assertEqual(row['member_count'],ref['member_count'])
            self.assertEqual(row['ess'],ref['ess'])
            self.assertEqual(row['q'],ref.get('floors',{}).get('q50',{}).get('level_cents'))

    def proof(self):
        return dict(interval=[10,12],reason=None,per_level=[dict(side='bid',yes_price_cents=58,
            start_displayed_contracts=10,end_displayed_contracts=12,on_book_executed_contracts=4,net_displayed_residual=6)])

    def test_best_consumed_level_included(self):
        result=corrected_refill(self.proof(),'bid',13,0,20)
        self.assertEqual(result['status'],'MEASURED')
        self.assertEqual(result['value'],1.5)

    def test_same_end_second_not_yet_known(self):
        self.assertEqual(corrected_refill(self.proof(),'bid',12,0,20)['status'],'UNOBSERVED')

    def test_zero_denominator_is_not_zero_refill(self):
        result=corrected_refill(self.proof(),'ask',13,0,20)
        self.assertEqual(result['status'],'ZERO_DENOMINATOR')
        self.assertIsNone(result['value'])

    def test_ambiguous_any_potential_consumed_level_invalidates_side(self):
        proof=self.proof()
        proof['per_level'].append(dict(side='bid',on_book_executed_contracts=None))
        self.assertEqual(corrected_refill(proof,'bid',13,0,20)['status'],'UNOBSERVED')

    def test_unconsumed_offscreen_does_not_invalidate_consumed_domain(self):
        proof=self.proof()
        proof['per_level'].append(dict(side='bid',on_book_executed_contracts=0))
        self.assertEqual(corrected_refill(proof,'bid',13,0,20)['status'],'MEASURED')


if __name__=='__main__':
    unittest.main()
