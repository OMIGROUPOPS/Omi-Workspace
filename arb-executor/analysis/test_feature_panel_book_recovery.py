import unittest
from feature_panel_book_recovery import (visible_depth, snapshot_residual, imbalance,
                                        spike_reversion, DepthDecoder, usable_book, book_invalid_reason)


class BookRecoveryTests(unittest.TestCase):
    def trade(self,**values):
        return dict(direction_authoritative=True,is_block_trade=False,**values)

    def test_top_five_absence_not_zero_beyond_boundary(self):
        levels = [[20,1],[19,2],[18,3],[17,4],[16,5]]
        self.assertIsNone(visible_depth(levels,15,'bid'))
        self.assertEqual(visible_depth(levels,21,'bid'),0)
        self.assertEqual(visible_depth(levels,15,'bid',full=True),0)
        self.assertIsNone(visible_depth([],20,'bid'))

    def test_maker_residual_execution_and_boundary_ambiguity(self):
        previous = [10,[[20,10]],[[22,10]]]
        current = [13,[[20,7]],[[22,12]]]
        rows = snapshot_residual(previous,current,[self.trade(ts=11.5,price=20,size=3,side='no')])
        self.assertEqual(rows,[['bid',20.,0.,3.],['ask',22.,2.,0.]])
        ambiguous = snapshot_residual(previous,current,[self.trade(ts=13,price=20,size=3,side='no')])
        self.assertIsNone(ambiguous[0][2])
        unknown = snapshot_residual(previous,current,[dict(ts=11.5,price=20,size=3,side=None)])
        self.assertIsNone(unknown[0][2])
        future = snapshot_residual(previous,current,[dict(ts=13.5,price=20,size=3,side='no')])
        self.assertEqual(future,snapshot_residual(previous,current,[]))

    def test_fractional_end_boundary_uses_receipt_cutoff_not_snapshot_clock(self):
        previous=[99,[[20,10]],[[21,10]]]
        current=[100,[[20,10]],[[21,7]]]
        row=self.trade(ts=100.5,price=21,size=3,side='yes')
        def ask(rows):
            return next(r for r in rows if r[0]=='ask')
        self.assertEqual(ask(snapshot_residual(previous,current,[row],known_at_epoch=100)),
                         ['ask',21.,-3.,0.])
        self.assertEqual(snapshot_residual(previous,current,[row]),
                         snapshot_residual(previous,current,[]))
        self.assertEqual(ask(snapshot_residual(previous,current,[row],known_at_epoch=100.5)),
                         ['ask',21.,None,None])
        self.assertEqual(ask(snapshot_residual(previous,current,[row],known_at_epoch=120)),
                         ['ask',21.,None,None])
        after_second=self.trade(ts=101,price=21,size=3,side='yes')
        self.assertEqual(snapshot_residual(previous,current,[after_second],known_at_epoch=120),
                         snapshot_residual(previous,current,[],known_at_epoch=120))

    def test_fractional_start_and_end_boundary_no_invented_order(self):
        previous=[99.75,[[20,10]],[[21,10]]]
        current=[100.25,[[20,10]],[[21,7]]]
        for ts in (99.1,99.9,100.1,100.9):
            with self.subTest(ts=ts):
                row=self.trade(ts=ts,price=21,size=3,side='yes')
                values=snapshot_residual(previous,current,[row],known_at_epoch=120)
                self.assertEqual(next(r for r in values if r[0]=='ask'),['ask',21.,None,None])
        future=self.trade(ts=100.9,price=21,size=3,side='yes')
        self.assertEqual(snapshot_residual(previous,current,[future],known_at_epoch=100.25),
                         snapshot_residual(previous,current,[],known_at_epoch=100.25))
        with self.assertRaisesRegex(ValueError,'MAKER_SNAPSHOT_AFTER_RECEIPT_CUTOFF'):
            snapshot_residual(previous,current,[],known_at_epoch=100)

    def test_maker_never_allocates_arithmetic_or_unknown_block_status(self):
        previous = [10,[[20,10]],[[22,10]]]
        current = [13,[[20,7]],[[22,12]]]
        base=dict(ts=11.5,price=20,size=3,side='no')
        for extra in ({},{'direction_authoritative':True},
                      {'is_block_trade':False,'direction_authoritative':False}):
            rows=snapshot_residual(previous,current,[dict(base,**extra)])
            self.assertIsNone(next(r[2] for r in rows if r[0]=='bid' and r[1]==20))
        blocked=dict(base,is_block_trade=True,direction_authoritative=True)
        self.assertEqual(snapshot_residual(previous,current,[blocked]),snapshot_residual(previous,current,[]))

    def test_authoritative_but_unresolved_order_is_missing(self):
        row=self.trade(ts=11.5,price=20,size=3,side='no',interval_ordering_unresolved=True)
        values=snapshot_residual([10,[[20,10]],[[22,10]]],[13,[[20,7]],[[22,12]]],[row])
        self.assertIsNone(next(r[2] for r in values if r[0]=='bid'))

    def test_missing_execution_at_absent_but_visible_level_not_lost(self):
        row=dict(ts=11.5,price=21,size=3,side=None,is_block_trade=False,direction_authoritative=False)
        values=snapshot_residual([10,[[20,10]],[[22,10]]],[13,[[20,7]],[[22,12]]],[row])
        self.assertIsNone(next(r[2] for r in values if r[0]=='bid' and r[1]==21))
        self.assertIsNone(next(r[2] for r in values if r[0]=='ask' and r[1]==21))

    def test_imbalance_zero_or_missing_depth(self):
        self.assertEqual(imbalance([[20,3]],[[22,1]]),.5)
        self.assertIsNone(imbalance([[20,0]],[[22,0]]))
        self.assertIsNone(imbalance([[20,None]],[[22,1]]))

    def test_usable_book_does_not_repair_locked_or_crossed_prices(self):
        self.assertTrue(usable_book([10,[[20,3]],[[22,1]]]))
        for row in ([10,[[20,3]],[[20,1]]],[10,[[81,3]],[[64,1]]],
                    [10,[[39,3]],[[7,1]]]):
            self.assertFalse(usable_book(row))
            self.assertEqual(book_invalid_reason(row),'LOCKED_OR_CROSSED_CAPTURE')
        self.assertFalse(usable_book([10,[[20,3]],[]]))
        self.assertFalse(usable_book(None))

    def test_crossed_endpoint_invalidates_all_maker_residuals(self):
        before=[10,[[81,3]],[[64,1]]]
        after=[13,[[60,2]],[[64,1]]]
        rows=snapshot_residual(before,after,[],full=True)
        self.assertTrue(rows)
        self.assertTrue(all(row[2] is None for row in rows))

    def test_spike_has_no_future_or_preformation_seed(self):
        rows = [[1,80,1],[11,50,1],[12,40,1],[13,45,1],[20,0,1]]
        self.assertEqual(spike_reversion(rows,10,20,5),(-10,.5))
        self.assertEqual(spike_reversion(rows,10,13,5),(-10,0))
        self.assertEqual(spike_reversion(rows,10,12,5),(None,None))

    def snapshot(self,seq=1):
        return dict(t=10.5,m=dict(type='orderbook_snapshot',sid=1,seq=seq,
            msg=dict(market_ticker='LIB-A',yes_dollars_fp=[['.20','10']],no_dollars_fp=[['.78','12']])))

    def delta(self,seq=2,ticker='LIB-A'):
        return dict(t=11.5,m=dict(type='orderbook_delta',sid=1,seq=seq,
            msg=dict(market_ticker=ticker,price_dollars='.20',delta_fp='-2',side='yes')))

    def test_ws_needs_start_and_seed_no_scale_guess(self):
        decoder=DepthDecoder({'LIB-A'})
        self.assertIsNone(decoder.consume(self.snapshot()))
        decoder.consume(dict(ev='recorder_start'))
        self.assertIsNone(decoder.consume(self.delta()))
        state=decoder.consume(self.snapshot(seq=3))
        self.assertEqual(state['bids'],[[20.,10.]])
        self.assertEqual(state['asks'],[[22.,12.]])
        self.assertEqual(decoder.consume(self.delta(seq=4))['bids'],[[20.,8.]])

    def test_gap_on_other_ticker_invalidates_library_depth(self):
        decoder=DepthDecoder({'LIB-A'})
        decoder.consume(dict(ev='recorder_start'))
        decoder.consume(self.snapshot())
        decoder.consume(self.delta(seq=3,ticker='NOT-IN-LIBRARY'))
        self.assertEqual(decoder.invalidated,['LIB-A'])
        self.assertIsNone(decoder.consume(self.delta(seq=4)))
        self.assertEqual(decoder.counters['sequence_gaps'],1)
        self.assertIsNotNone(decoder.consume(self.snapshot(seq=5)))

    def test_deferred_materialization_equals_eager_state(self):
        eager,lazy=DepthDecoder({'LIB-A'}),DepthDecoder({'LIB-A'})
        for row in (dict(ev='recorder_start'),self.snapshot(),self.delta(),self.delta(seq=3)):
            state=eager.consume(row)
            metadata=lazy.consume(row,materialize=False)
            self.assertEqual(eager.invalidated,lazy.invalidated)
            if metadata:
                self.assertEqual(state,lazy.state(**metadata))

    def test_recorder_restart_has_explicit_invalidation(self):
        decoder=DepthDecoder({'LIB-A'})
        decoder.consume(dict(ev='recorder_start'))
        decoder.consume(self.snapshot())
        decoder.consume(dict(ev='recorder_start'))
        self.assertEqual(decoder.invalidated,['LIB-A'])
        self.assertFalse(decoder.state('LIB-A',12,None,None)['valid'])

    def test_explicit_yes_price_capture_no_side_is_not_inverted(self):
        decoder=DepthDecoder({'LIB-A'})
        decoder.consume(dict(ev='recorder_start',use_yes_price=True))
        snap=self.snapshot()
        snap['m']['msg']['no_dollars_fp']=[['.22','12']]
        self.assertEqual(decoder.consume(snap)['asks'],[[22.,12.]])
        delta=self.delta()
        delta['m']['msg'].update(side='no',price_dollars='.22')
        self.assertEqual(decoder.consume(delta)['asks'],[[22.,10.]])
        decoder.consume(dict(ev='recorder_start',use_yes_price=False))
        self.assertEqual(decoder.consume(self.snapshot())['asks'],[[22.,12.]])

    def test_archive_gap_invalidates_until_snapshot_and_unknown_convention_fails(self):
        decoder=DepthDecoder({'LIB-A'})
        decoder.consume(dict(ev='recorder_start'))
        decoder.consume(self.snapshot())
        self.assertEqual(decoder.invalidate_archive(),['LIB-A'])
        self.assertIsNone(decoder.consume(self.delta()))
        self.assertIsNotNone(decoder.consume(self.snapshot(seq=3)))
        decoder.consume(dict(ev='recorder_start',use_yes_price='unknown'))
        self.assertIsNone(decoder.consume(self.snapshot(seq=4)))
        with self.assertRaisesRegex(ValueError,'UNDECLARED_WS_PRICE_CONVENTION'):
            DepthDecoder({'LIB-A'},no_price_convention='guess')

    def test_ws_exclusion_is_exact_and_capture_convention_survives_checkpoint(self):
        from feature_panel_ws_recovery import archive_exclusion,decoder_snapshot,restore_decoder
        excluded=archive_exclusion(dict(name='ws_20260623_08.jsonl.gz',bytes=123))
        self.assertEqual(excluded['status'],'EXCLUDED')
        self.assertEqual(excluded['hour_end_epoch']-excluded['hour_start_epoch'],3600)
        self.assertIsNone(archive_exclusion(dict(name='ws_20260623_09.jsonl.gz',bytes=123)))
        decoder=DepthDecoder({'LIB-A'},no_price_convention='YES')
        decoder.consume(dict(ev='recorder_start'))
        snap=self.snapshot()
        snap['m']['msg']['no_dollars_fp']=[['.22','12']]
        decoder.consume(snap)
        restored=DepthDecoder({'LIB-A'})
        restore_decoder(restored,decoder_snapshot(decoder))
        self.assertEqual(restored.no_price_convention,'YES')
        self.assertEqual(restored.state('LIB-A',11,1,1),decoder.state('LIB-A',11,1,1))


if __name__=='__main__':
    unittest.main()
