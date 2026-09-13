import unittest
from absorption_audit import prepare_book, audit_interval
from feature_panel_book_recovery import book_invalid_reason


class AbsorptionTests(unittest.TestCase):
    def test_fast_book_validation_matches_reference(self):
        for bids, asks in (([[40,10]], [[42,9]]), ([[40,0]], [[42,9]]),
                ([[42,10]], [[42,9]]), ([[43,10]], [[42,9]]),
                ([[40.25,1.5],[39.5,2]], [[42.25,9.5]]),
                ([[None,None],[40,5]], [[42,9]])):
            book=[10,bids,asks]
            self.assertEqual(prepare_book(book)['reason'], book_invalid_reason(book))

    def measure(self, prints=(), before=None, after=None, **kwargs):
        before = before or [10, [[40, 10], [39, 20]], [[42, 10], [43, 20]]]
        after = after or [20, [[40, 10], [39, 20]], [[42, 10], [43, 20]]]
        return {r['side']: r for r in audit_interval(prepare_book(before), prepare_book(after),
            10, 20, prints, formation=kwargs.get('formation', 0), bell=kwargs.get('bell', 30))}

    def trade(self, **changes):
        return dict(dict(ts=15, price=40, size=5, side='no', direction_authoritative=True,
                         is_block_trade=False), **changes)

    def test_best_bid_included_and_not_only_below(self):
        r = self.measure([self.trade()])['bid']
        self.assertEqual(r['status'], 'MEASURED')
        self.assertEqual(r['refill_ratio'], 1)
        self.assertTrue(r['levels'][0]['was_best'])

    def test_best_ask_and_both_consumed_levels(self):
        rows = self.measure([self.trade(side='yes', price=42), self.trade(side='yes', price=43)])
        self.assertEqual(rows['ask']['refill_ratio'], 1)
        self.assertEqual(len(rows['ask']['levels']), 2)

    def test_unconsumed_adds_not_in_numerator(self):
        after = [20, [[40, 10], [39, 1000]], [[42, 10], [43, 20]]]
        self.assertEqual(self.measure([self.trade()], after=after)['bid']['refill_ratio'], 1)

    def test_measured_zero_is_not_missing(self):
        after = [20, [[40, 5], [39, 20]], [[42, 10], [43, 20]]]
        r = self.measure([self.trade()], after=after)['bid']
        self.assertEqual((r['status'], r['refill_ratio']), ('MEASURED', 0))

    def test_no_execution_zero_denominator(self):
        r = self.measure()['bid']
        self.assertEqual(r['status'], 'ZERO_DENOMINATOR')
        self.assertIsNone(r['refill_ratio'])

    def test_unknown_label_and_block_status_fail_closed(self):
        for field in ({'direction_authoritative': False}, {'is_block_trade': None}):
            rows = self.measure([self.trade(**field)])
            self.assertTrue(all(r['status'] == 'UNOBSERVED' for r in rows.values()))

    def test_offbook_excluded(self):
        self.assertEqual(self.measure([self.trade(is_block_trade=True)])['bid']['status'], 'ZERO_DENOMINATOR')

    def test_boundaries_and_fractional_end_second_unknown(self):
        for ts in (10, 10.5, 20, 20.9):
            r = self.measure([self.trade(ts=ts)])['bid']
            self.assertEqual(r['status'], 'UNOBSERVED')
            self.assertIn('BOUNDARY_SECOND_ORDER_UNKNOWN', r['reasons'])

    def test_depth_outside_capture_is_not_zero(self):
        r = self.measure([self.trade(price=38)])['bid']
        self.assertEqual(r['status'], 'UNOBSERVED')
        self.assertIn('CONSUMED_LEVEL_NOT_VISIBLE_AT_BOTH_SNAPSHOTS', r['reasons'])

    def test_preformation_bell_and_crossed(self):
        self.assertEqual(self.measure(formation=11)['bid']['status'], 'UNOBSERVED')
        self.assertEqual(self.measure(bell=21)['bid']['status'], 'UNOBSERVED')
        before = [10, [[44, 10]], [[42, 10]]]
        self.assertIn('LOCKED_OR_CROSSED_CAPTURE', self.measure(before=before)['bid']['reasons'])

    def test_partial_side_not_promoted(self):
        rows = self.measure([self.trade(), self.trade(ts=20, price=39)])
        self.assertEqual(rows['bid']['status'], 'UNOBSERVED')
        self.assertIsNone(rows['bid']['refill_ratio'])

    def test_net_pull_and_identity(self):
        after = [20, [[40, 1], [39, 20]], [[42, 10], [43, 20]]]
        r = self.measure([self.trade()], after=after)['bid']
        self.assertEqual(r['net_pull'], 4)
        self.assertEqual(r['refill_ratio'], 0)
        self.assertEqual(r['levels'][0]['reconciliation_error'], 0)


if __name__ == '__main__':
    unittest.main()
