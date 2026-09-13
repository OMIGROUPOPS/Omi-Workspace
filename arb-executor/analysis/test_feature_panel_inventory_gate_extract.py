import unittest
from unittest.mock import patch
from feature_panel_inventory_gate_extract import pair_identity, build_states, side_state


def leg(name, prices):
    return dict(event_id='KXATP-26MAY01AAABBB',category='ATP_MAIN',ticker='KXATP-26MAY01AAABBB-'+name,
        leg_id=name,formation_end_epoch=0,bell_epoch=180,anchor_cents=prices[0],
        path=[dict(ts=t,last_cents=p,bid_cents=p-1,ask_cents=p+1) for t,p in zip([0,61,90,120],prices)])


class GateExtractTests(unittest.TestCase):
    def test_orientation_and_original_receipt_clock(self):
        a,z=leg('AAA',[60,61,62,63]),leg('BBB',[40,39,38,37])
        identity,error=pair_identity([z,a],{a['ticker']:0,z['ticker']:0})
        self.assertIsNone(error)
        self.assertEqual([r['leg_id'] for r in identity['rows']],['AAA','BBB'])
        rec={r['ticker']:dict(books=[],book_observation_epochs=[]) for r in [a,z]}
        rows=build_states(identity,rec,{a['ticker']:[],z['ticker']:[]},[4,2,1],60)
        self.assertEqual(rows['states'][0]['sides']['AAA']['reason'],'BEFORE_FIRST_PAIR_OBSERVATION')
        self.assertEqual(rows['states'][2]['sides']['AAA']['previous_receipt_epoch'],90)

    def test_actual_refresh_not_last_change_and_authoritative_flow(self):
        a,z=leg('AAA',[60,61,62,63]),leg('BBB',[40,39,38,37])
        pair_identity([a,z],{a['ticker']:0,z['ticker']:0})
        recovery=dict(books=[[80,[[60,10]],[[62,10]]],[110,[[60,12]],[[62,10]]]],
            book_observation_epochs=[80,100,110,119])
        prints=[dict(ts=70,price=60,size=4,side='yes',direction_authoritative=True,is_block_trade=False),
                dict(ts=75,price=60,size=100,side='no',direction_authoritative=True,is_block_trade=True)]
        result=side_state(a,recovery,prints,120,90,60)
        self.assertEqual(result['maker']['interval'],[110,119])
        self.assertEqual(result['features']['taker_flow'],4)
        prints.append(dict(ts=85,price=60,size=2,side=None,arithmetic_side='no',
                           direction_authoritative=False,is_block_trade=None))
        result=side_state(a,recovery,prints,120,90,60)
        self.assertIsNone(result['features']['taker_flow'])

    def test_future_prints_do_not_change_gate(self):
        a,z=leg('AAA',[60,61,62,63]),leg('BBB',[40,39,38,37])
        pair_identity([a,z],{a['ticker']:0,z['ticker']:0})
        recovery=dict(books=[],book_observation_epochs=[])
        before=side_state(a,recovery,[],120,90,60)
        after=side_state(a,recovery,[dict(ts=121,price=1,size=999,side='no',
            direction_authoritative=True,is_block_trade=False)],120,90,60)
        self.assertEqual(before,after)

    def test_known_fractional_snapshot_boundary_is_not_a_maker_pull(self):
        a,z=leg('AAA',[60,61,62,63]),leg('BBB',[40,39,38,37])
        pair_identity([a,z],{a['ticker']:0,z['ticker']:0})
        recovery=dict(books=[[99,[[60,10]],[[62,10]]],[100,[[60,10]],[[62,7]]]],
            book_observation_epochs=[99,100])
        prints=[dict(ts=100.5,price=62,size=3,side='yes',
            direction_authoritative=True,is_block_trade=False)]
        at_snapshot=side_state(a,recovery,prints,100,90,60)
        no_future=side_state(a,recovery,[],100,90,60)
        self.assertEqual(at_snapshot,no_future)
        later=side_state(a,recovery,prints,120,90,60)
        affected=next(row for row in later['maker']['per_level']
            if row['side']=='ask' and row['yes_price_cents']==62)
        self.assertEqual(affected['status'],'STORE_SILENT')
        self.assertIsNone(affected['net_displayed_residual'])
        self.assertIsNone(later['features']['maker_ask_net_pulls'])


if __name__=='__main__':
    unittest.main()
