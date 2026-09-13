import unittest
from unittest.mock import patch
from decimal import Decimal
from feature_panel_public_trades import canonical_trade, PublicTrades
from feature_panel_taker_recovery import (
    arithmetic_aggressor, preceding_book, unique_identity_matches, net_maker_residual,
    authoritative_direction, same_second_quote_change,
)
from feature_panel_inventory_extract import recover, reusable_checkpoint, write_gzip, atomic_json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import hashlib
import sqlite3


class RecoveryTests(unittest.TestCase):
    def test_arithmetic_boundaries(self):
        self.assertEqual(arithmetic_aggressor('0.9', '0.8', '0.9')['side'], 'yes')
        self.assertEqual(arithmetic_aggressor('0.8', '0.8', '0.9')['side'], 'no')
        self.assertIsNone(arithmetic_aggressor('0.85', '0.8', '0.9')['side'])
        for bid, ask in ((None, 1), (1, 1), (2, 1)):
            self.assertEqual(arithmetic_aggressor(1, bid, ask)['status'], 'AMBIGUOUS')

    def test_same_second_book_is_never_used(self):
        books = [{'epoch': 10}, {'epoch': 11}]
        self.assertIs(preceding_book(books, [10, 11], 11.9), books[0])
        self.assertIsNone(preceding_book(books, [10, 11], 10.9))

    def test_unique_id_and_duplicate_page(self):
        row = dict(ticker='FIXTURE-A', ts=10.1, price='0.8', size='2.00')
        api = dict(row, trade_id='id', taker_side='yes')
        result = unique_identity_matches([row], [api, api])[0]
        self.assertEqual(result['trade_id'], 'id')
        self.assertIsNone(unique_identity_matches([row, row], [api])[0]['trade_id'])
        self.assertIsNone(unique_identity_matches([row], [api, dict(api, trade_id='other')])[0]['trade_id'])
        self.assertIsNone(unique_identity_matches([row], [api, dict(api, taker_side='no')])[0]['trade_id'])

    def test_near_time_or_price_not_matched(self):
        row = dict(ticker='FIXTURE-A', ts=10, price='0.8', size='2')
        self.assertIsNone(unique_identity_matches([row], [dict(row, ts=11, trade_id='x', taker_side='yes')])[0]['trade_id'])
        self.assertIsNone(unique_identity_matches([row], [dict(row, price='0.8000001', trade_id='x', taker_side='yes')])[0]['trade_id'])

    def test_maker_execution_sign_and_missing(self):
        self.assertEqual(net_maker_residual(10, 7, 3), Decimal(0))
        self.assertEqual(net_maker_residual(10, 12, 3), Decimal(5))
        self.assertEqual(net_maker_residual(10, 5, 3), Decimal(-2))
        self.assertIsNone(net_maker_residual(10, None, 3))
        self.assertIsNone(net_maker_residual(10, 7, None))

    def test_conflicting_id_cannot_make_a_second_id_unique(self):
        row = dict(ticker='FIXTURE-A', ts=10, price=20, size=1)
        a = dict(row, trade_id='a', taker_side='yes')
        b = dict(row, trade_id='b', taker_side='yes')
        self.assertIsNone(unique_identity_matches([row], [a, dict(a,taker_side='no'),b])[0]['trade_id'])

    def test_api_units_and_direction(self):
        row = dict(ticker='FIXTURE-A', created_time='2026-04-20T00:00:00.125Z',
                   trade_id='id', yes_price_dollars='0.7200', count_fp='61.17',
                   taker_outcome_side='yes', taker_book_side='bid', taker_side='yes')
        value = canonical_trade(row)
        self.assertEqual(Decimal(value['price']), Decimal('72'))
        self.assertEqual(Decimal(value['size']), Decimal('61.17'))
        conflicted = canonical_trade(dict(row,taker_book_side='ask'))
        self.assertIsNone(conflicted['taker_side'])
        self.assertEqual(conflicted['direction_status'], 'CONFLICTING_API_DIRECTION')

    def test_paginated_api_is_exact_and_includes_last_fractional_second(self):
        api = PublicTrades.__new__(PublicTrades)
        api.split, api.page_limit = 100, 1000
        source = dict(ticker='FIXTURE-A',ts=10.5,price=20,size=1)
        raw = dict(ticker='FIXTURE-A', created_time='1970-01-01T00:00:10.5Z',
                   trade_id='one',yes_price_dollars='.20',count_fp='1',taker_side='yes')
        replies = [({'trades':[raw],'cursor':'next'}, {'fetched_at':'recorded'}),
                   ({'trades':[dict(raw,ticker='OTHER')],'cursor':''}, {'fetched_at':'recorded'})]
        with patch.object(api,'get',side_effect=replies) as fetch:
            rows,proof = api.matching([source])
        self.assertEqual(len(rows),1)
        self.assertEqual(len(proof),2)
        self.assertEqual(fetch.call_args_list[0].args[1]['max_ts'],11)
        self.assertEqual(fetch.call_args_list[1].args[1]['cursor'],'next')

    def api(self, **changes):
        row = dict(ticker='FIXTURE-A',ts=10.5,price=20,size=1,trade_id='id',
            taker_side='yes',taker_outcome_side='yes',taker_book_side='bid',
            is_block_trade=False,direction_status='CANONICAL_API_DIRECTION',fetched_at='recorded')
        return dict(row, **changes)

    def test_explicit_id_can_resolve_identical_keys_but_wrong_id_cannot_fallback(self):
        source = dict(ticker='FIXTURE-A',ts=10.5,price=20,size=1,trade_id='id')
        rows = [self.api(), self.api(trade_id='second')]
        self.assertEqual(unique_identity_matches([source,dict(source,trade_id='second')],rows)[0]['status'],'EXACT_TRADE_ID')
        self.assertIsNone(unique_identity_matches([dict(source,trade_id='missing')],rows)[0]['trade_id'])

    def test_onbook_canonical_api_is_the_only_authority(self):
        source = dict(ticker='FIXTURE-A',ts=10.5,price=20,size=1)
        match = unique_identity_matches([source],[self.api()])[0]
        self.assertTrue(authoritative_direction(match)['direction_authoritative'])
        for changed in (dict(is_block_trade=True),dict(is_block_trade=None),
                        dict(direction_status='CANONICAL_API_DIRECTION_ABSENT'),
                        dict(direction_status='CONFLICTING_API_DIRECTION'),dict(taker_side=None)):
            decision=authoritative_direction(dict(match,**changed))
            self.assertFalse(decision['direction_authoritative'])
            self.assertIsNone(decision['side'])

    def test_block_flag_conflicts_fail_identity_closed(self):
        source=dict(ticker='FIXTURE-A',ts=10.5,price=20,size=1)
        match=unique_identity_matches([source],[self.api(),self.api(is_block_trade=True)])[0]
        self.assertEqual(match['status'],'UNRESOLVED_IDENTITY')

    def test_unlabeled_or_block_candidate_cannot_make_other_id_unique(self):
        source=dict(ticker='FIXTURE-A',ts=10.5,price=20,size=1)
        for other in (self.api(trade_id='other',taker_side=None),self.api(trade_id='other',is_block_trade=True)):
            self.assertIsNone(unique_identity_matches([source],[self.api(),other])[0]['trade_id'])

    def test_legacy_only_is_not_canonical_api_direction(self):
        raw=dict(ticker='FIXTURE-A',created_time='2026-04-20T00:00:00Z',trade_id='id',
            yes_price_dollars='.20',count_fp='1',taker_side='yes',is_block_trade=False)
        parsed=canonical_trade(raw)
        self.assertIsNone(parsed['taker_side'])
        self.assertEqual(parsed['legacy_taker_side'],'yes')
        self.assertIs(parsed['is_block_trade'],False)
        self.assertEqual(canonical_trade(dict(raw,taker_book_side='ask',taker_side='no'))['taker_side'],'no')

    def test_same_second_flag_is_delayed_and_top_specific(self):
        old=dict(bids=[[19,1]],asks=[[20,1]])
        sizes=dict(bids=[[19,2]],asks=[[20,3]])
        moved=dict(bids=[[20,1]],asks=[[21,1]])
        self.assertFalse(same_second_quote_change([old,sizes],[9,10],10.2)['top_quote_changed_in_print_second'])
        result=same_second_quote_change([old,moved],[9,10],10.2)
        self.assertTrue(result['top_quote_changed_in_print_second'])
        self.assertEqual(result['top_quote_change_available_epoch'],11)
        self.assertIsNone(same_second_quote_change([old],[10],10.2)['top_quote_changed_in_print_second'])

    def test_recovery_fetches_even_unambiguous_arithmetic_and_never_uses_it_as_flow(self):
        row=dict(ticker='FIXTURE-A',rowid=1,ts=10.5,price=20,size=1,taker_side='no')
        leg=dict(event_id='FIXTURE',category='ATP_MAIN',leg_id='A',ticker='FIXTURE-A',formation_end_epoch=9,bell_epoch=20)
        book=dict(source_epoch=9,bids=[[19,1]],asks=[[20,1]])
        panel=dict(books=[book],checks={},excluded_unverified_objects=[],source_manifest=[],book_observation_epochs=[9])
        def extraction(connection,leg,cutter,client):
            core.attach_takers([row],None)
            return panel,dict(positive_prints=[row])
        flow_rows=[]
        core=SimpleNamespace(book_from_source=lambda *a,**k: None,attach_takers=lambda *a,**k:[dict(row)],
            extract_leg=extraction,minute_features=lambda leg,rows,books:flow_rows.extend(rows) or [])
        api=SimpleNamespace(matching=lambda rows:([],[]))
        with patch.object(api,'matching',wraps=api.matching) as lookup:
            result=recover(core,None,leg,None,api)
        lookup.assert_called_once()
        taker=result['takers'][0]
        self.assertEqual(taker['arithmetic_side'],'yes')
        self.assertIsNone(taker['side'])
        self.assertFalse(taker['direction_authoritative'])
        self.assertIsNone(flow_rows[0]['taker_side'])
        self.assertEqual(result['counts']['label_coverage:arithmetic-only'],1)
        # API overrides disagreeing original and arithmetic; block excluded from
        # new flow only, while the original positive witness count is unchanged.
        api.matching=lambda rows:([self.api(taker_side='no',taker_outcome_side='no',taker_book_side='ask')],[])
        self.assertEqual(recover(core,None,leg,None,api)['takers'][0]['side'],'no')
        api.matching=lambda rows:([self.api(is_block_trade=True)],[])
        flow_rows.clear()
        result=recover(core,None,leg,None,api)
        self.assertEqual(result['counts']['positive_prints'],1)
        self.assertEqual(result['counts']['offbook_excluded'],1)
        self.assertEqual(flow_rows,[])

    def test_reuse_checks_hash_span_and_input_binding(self):
        leg=dict(event_id='FIXTURE',category='ATP_MAIN',leg_id='A',ticker='FIXTURE-A',formation_end_epoch=9,bell_epoch=20)
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory); (folder/'parts').mkdir()
            key=hashlib.sha256(leg['ticker'].encode()).hexdigest()
            target=folder/'parts'/(key+'.json.gz')
            info=write_gzip(target,dict(leg,books=[],takers=[]))
            marker=folder/'parts'/(key+'.ready.json')
            atomic_json(marker,dict(ticker=leg['ticker'],binding=dict(inputs={'pin':'value'}),file=info))
            self.assertEqual(reusable_checkpoint(folder,leg,{'pin':'value'})['ticker'],leg['ticker'])
            with self.assertRaisesRegex(ValueError,'INPUT_BINDING'):
                reusable_checkpoint(folder,leg,{'pin':'wrong'})
            with self.assertRaisesRegex(ValueError,'SPAN'):
                reusable_checkpoint(folder,dict(leg,bell_epoch=21),{'pin':'value'})
            target.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'HASH'):
                reusable_checkpoint(folder,leg,{'pin':'value'})

    def test_reuse_reads_sealed_rows_not_original_objects_and_preserves_ids(self):
        leg=dict(event_id='FIXTURE',category='ATP_MAIN',leg_id='A',ticker='FIXTURE-A',formation_end_epoch=9,bell_epoch=20)
        connection=sqlite3.connect(':memory:'); connection.row_factory=sqlite3.Row
        connection.execute('CREATE TABLE prints (rowid INTEGER,event TEXT,ticker TEXT,ts REAL,price REAL,size REAL,src_role TEXT)')
        connection.execute('INSERT INTO prints VALUES (1,?,?,?,?,?,?)',('FIXTURE','FIXTURE-A',10.5,20,1,'LIBRARY'))
        reused=dict(leg,books=[[9,[[19,1]],[[20,1]]]],
            takers=[dict(rowid=1,observed_side='no',trade_id='id')],
            excluded_unverified_objects=[],source_manifest=[],checks={})
        core=SimpleNamespace(verify_library=lambda leg,rows:dict(accepted_count=len(rows)),
            minute_features=lambda leg,rows,books:[])
        api=SimpleNamespace(matching=lambda rows:([self.api()],[]))
        with patch.object(api,'matching',wraps=api.matching) as fetch:
            result=recover(core,connection,leg,None,api,reused=reused)
        self.assertEqual(fetch.call_args.args[0][0]['trade_id'],'id')
        self.assertEqual(result['takers'][0]['api_identity_status'],'EXACT_TRADE_ID')
        self.assertTrue(result['takers'][0]['direction_authoritative'])
        self.assertIsNone(result['book_observation_epochs'])
        with self.assertRaisesRegex(ValueError,'ROWIDS'):
            recover(core,connection,leg,None,api,reused=dict(reused,takers=[]))
        connection.close()


if __name__ == '__main__':
    unittest.main()
