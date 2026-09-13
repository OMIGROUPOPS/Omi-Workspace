import unittest
from feature_panel_inventory_features import previous_receipt,receipt_features,maker_summary,ADDED_BLOCKS


class InventoryFeaturesTests(unittest.TestCase):
    def test_previous_receipt_is_not_previous_gate(self):
        self.assertEqual(previous_receipt([1,2,9,10],[1,5,10],10,1),9)
        self.assertIsNone(previous_receipt([1,2],[1,5],1,1))

    def test_queue_same_q_and_no_future_book_or_print(self):
        args=dict(epoch=120,previous_epoch=90,seconds_per_minute=60,formation=0,
            books=[[80,[[20,10]],[[22,10]]],[110,[[20,7]],[[23,10]]],[130,[[20,99]],[[24,10]]]],
            book_epochs=[80,110,130],first_q=20,bid=20,ask=23,previous_bid=20,previous_ask=22,
            prints=[[61,50,1],[70,40,1],[80,45,1],[120,0,1]])
        rows,proof=receipt_features(**args)
        self.assertEqual(rows['displayed_depth_at_first_q'],7)
        self.assertEqual(rows['queue_decay_per_minute'],6)
        self.assertEqual(rows['spread_rate_per_minute'],2)
        self.assertEqual(rows['completed_minute_largest_move'],-10)
        self.assertEqual(rows['completed_minute_retraced_share'],.5)
        self.assertEqual(len(ADDED_BLOCKS),5)

    def test_no_fitted_reference_or_empty_queue_invention(self):
        rows,_=receipt_features(epoch=100,previous_epoch=None,seconds_per_minute=60,formation=0,
            books=[],book_epochs=[],first_q=None,bid=None,ask=None,previous_bid=None,previous_ask=None,prints=[])
        self.assertIsNone(rows['displayed_depth_at_first_q'])
        self.assertIsNone(rows['queue_decay_per_minute'])

    def test_refill_ratio_and_zero_denominator(self):
        before=[10,[[20,10],[19,10]],[[22,10],[23,10]]]
        after=[13,[[20,10],[19,12]],[[22,10],[23,12]]]
        rows,proof=maker_summary(before,after,[dict(ts=11,price=19,size=2,side='no',
            direction_authoritative=True,is_block_trade=False)],reference_price=21)
        self.assertEqual(rows['maker_refill_below_bid'],2)
        self.assertIsNone(rows['maker_refill_above_ask'])
        self.assertEqual(rows['maker_bid_net_adds'],4)
        level=next(r for r in proof['per_level'] if r['side']=='bid' and r['yes_price_cents']==19)
        self.assertEqual(level['distance_from_price_cents'],-2)
        self.assertEqual(level['start_displayed_contracts'],10)
        self.assertEqual(level['end_displayed_contracts'],12)
        self.assertEqual(level['on_book_executed_contracts'],2)
        self.assertEqual(level['net_displayed_residual'],4)

    def test_unresolved_execution_invalidates_visible_side_summary(self):
        before=[10,[[20,10],[19,10]],[[22,10],[23,10]]]
        after=[13,[[20,10],[19,12]],[[22,10],[23,12]]]
        rows,proof=maker_summary(before,after,[dict(ts=11,price=19,size=2,side='no')])
        self.assertIsNone(rows['maker_bid_net_adds'])
        self.assertIsNone(rows['maker_refill_below_bid'])
        level=next(r for r in proof['per_level'] if r['side']=='bid' and r['yes_price_cents']==19)
        self.assertEqual(level['status'],'STORE_SILENT')
        self.assertIsNone(level['distance_from_price_cents'])
        self.assertIn('UNRESOLVED_EXECUTION',level['missing_reason'])

    def test_crossed_maker_interval_keeps_raw_and_has_no_aggregate(self):
        before=[10,[[81,10]],[[64,12]]]
        after=[13,[[60,10]],[[64,12]]]
        rows,proof=maker_summary(before,after,[],full=True,reference_price=62)
        self.assertTrue(all(value is None for value in rows.values()))
        self.assertEqual(proof['reason'],'LOCKED_OR_CROSSED_CAPTURE')
        self.assertEqual(proof['raw_previous_snapshot'],before)
        self.assertEqual(proof['raw_current_snapshot'],after)
        self.assertTrue(proof['per_level'])
        self.assertTrue(all(r['status']=='STORE_SILENT' and r['missing_reason']=='LOCKED_OR_CROSSED_CAPTURE'
                            and r['net_displayed_residual'] is None for r in proof['per_level']))

    def test_receipt_features_passes_known_clock_to_snapshot_interval(self):
        before=[99,[[20,10]],[[21,10]]]
        after=[100,[[20,10]],[[21,7]]]
        args=dict(previous_epoch=98,seconds_per_minute=60,formation=0,
            books=[before,after],book_epochs=[99,100],first_q=20,bid=20,ask=21,
            previous_bid=20,previous_ask=21,prints=[],maker_previous=before,maker_current=after,
            attributed_prints=[dict(ts=100.5,price=21,size=3,side='yes',
                direction_authoritative=True,is_block_trade=False)])
        at_snapshot,proof=receipt_features(epoch=100,**args)
        self.assertEqual(at_snapshot['maker_ask_net_pulls'],3)
        self.assertEqual(proof['maker']['known_at_receipt_epoch'],100)
        later,proof=receipt_features(epoch=120,**args)
        self.assertIsNone(later['maker_ask_net_pulls'])
        self.assertEqual(proof['maker']['known_at_receipt_epoch'],120)
        level=next(r for r in proof['maker']['per_level'] if r['side']=='ask')
        self.assertEqual(level['status'],'STORE_SILENT')
        self.assertIn('INTERVAL_ORDER',level['missing_reason'])

    def test_new_imbalance_and_queue_fail_closed_but_keep_usable_current_state(self):
        args=dict(epoch=120,previous_epoch=90,seconds_per_minute=60,formation=0,
            books=[[80,[[81,10]],[[64,12]]],[110,[[60,8]],[[64,12]]]],
            book_epochs=[80,110],first_q=60,bid=60,ask=64,previous_bid=81,previous_ask=64,prints=[])
        rows,proof=receipt_features(**args)
        self.assertEqual(rows['book_imbalance_top'],-.2)
        self.assertIsNone(rows['book_imbalance_top_change'])
        self.assertIsNone(rows['book_imbalance_five_change'])
        self.assertEqual(rows['displayed_depth_at_first_q'],8)
        self.assertIsNone(rows['queue_decay_per_minute'])
        self.assertEqual(proof['previous_book_invalid_reason'],'LOCKED_OR_CROSSED_CAPTURE')
        args['books'][1]=[110,[[64,8]],[[64,12]]]
        rows,proof=receipt_features(**args)
        for name in ('book_imbalance_top','book_imbalance_five','book_imbalance_top_change',
                     'book_imbalance_five_change','displayed_depth_at_first_q','queue_decay_per_minute'):
            self.assertIsNone(rows[name])
        self.assertEqual(proof['current_book_invalid_reason'],'LOCKED_OR_CROSSED_CAPTURE')


if __name__=='__main__':
    unittest.main()
