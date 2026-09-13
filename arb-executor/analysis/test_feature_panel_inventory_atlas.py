"""Eleven-block adapter, causal queue/freeze and unchanged-FIRST proofs."""
from __future__ import annotations
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import feature_panel as panel
import feature_panel_atlas as atlas
import feature_panel_bench as bench
import feature_panel_inventory_atlas as inventory
import feature_panel_run as launcher
from feature_panel_execution import compact_sampler_copy
from test_feature_panel_bench import pair, CONTRACT
from test_feature_panel_parallel import population_fixture


def inputs_fixture(pairs):
    rows = []
    for p in pairs:
        states = []
        for gate in CONTRACT['gates_minutes_to_bell']:
            epoch = p.bell-gate*CONTRACT['minute_seconds']
            states.append(dict(minutes_to_bell=gate, sides={leg.leg_id:dict(epoch=epoch,
                previous_receipt_epoch=epoch-30,
                features={name:None for name in inventory.INPUT_FIELDS},
                book_current=[epoch, [[40,8],[39,4]], [[41,7],[42,5]]],
                book_previous=[epoch-30, [[40,12],[39,4]], [[41,7],[42,5]]]) for leg in p.legs}))
        rows.append(dict(event_id=p.event_id, category=p.category, span_sha256=atlas.span_hash(p), states=states))
    receipt = dict(schema='FEATURE_INVENTORY_GATE_INPUTS_V2', status='VERIFIED', complete=True,
        library_sha256='fixture', gates_minutes_to_bell=CONTRACT['gates_minutes_to_bell'],
        output=dict(rows=len(rows)))
    return inventory.GateInputs(rows, receipt, CONTRACT, 'fixture')


class InventoryAtlasTests(unittest.TestCase):
    def test_registry_is_exactly_eleven_and_twenty_three_variants(self):
        previous = panel.FIELDS
        with inventory.registry_adapter():
            self.assertEqual(len(panel.BLOCKS),11)
            variants = [dict(name=v.name, blocks=list(v.blocks)) for v in bench.variant_registry(panel.BLOCKS)]
            self.assertEqual(len(variants),23)
            self.assertEqual(inventory.required_variants(dict(fields=panel.field_registry(), variants=variants)), variants)
        self.assertIs(panel.FIELDS, previous)

    def test_exact_gate_and_span_and_missing_are_fail_closed(self):
        p=pair('query','2026-05-01',1000,1240)
        inputs=inputs_fixture([p])
        inputs.at(p,3)
        with self.assertRaisesRegex(ValueError,'NON_ATLAS'):
            inputs.at(p,np.nextafter(3.,4.))
        changed=pair('query','2026-05-01',1000,1241)
        with self.assertRaisesRegex(ValueError,'SPAN_MISMATCH'):
            inputs.at(changed,3)
        with self.assertRaisesRegex(ValueError,'PAIR_MISSING'):
            inputs.at(pair('other','2026-05-01',1000,1240),3)
        inputs.rows['query'][1][inventory.exact_gate(3)]['sides']['favorite']['book_current'][0]+=1
        with self.assertRaisesRegex(ValueError,'FUTURE_BOOK'):
            inputs.at(p,3)

    def test_queue_uses_same_current_reference_level_at_both_clocks(self):
        p=pair('query','2026-05-01',1000,1240)
        row=inputs_fixture([p]).at(p,3)['sides']['favorite']
        values=inventory.queue_values(row,40,60)
        self.assertEqual(values,dict(displayed_depth_at_first_q=8.,queue_decay_per_minute=8.))
        self.assertIsNone(inventory.queue_values(row,None,60)['displayed_depth_at_first_q'])
        self.assertIsNone(inventory.queue_values(row,38,60)['displayed_depth_at_first_q'])

    def test_invalid_new_queue_book_fails_closed_without_touching_base_features(self):
        p=pair('query','2026-05-01',1000,1240)
        row=inputs_fixture([p]).at(p,3)['sides']['favorite']
        row['book_current'][2]=[[40,7]]  # locked at the reference bid
        self.assertEqual(inventory.queue_values(row,40,60),
            dict(displayed_depth_at_first_q=None,queue_decay_per_minute=None))
        row=inputs_fixture([p]).at(p,3)['sides']['favorite']
        row['book_previous'][2]=[[39,7]]  # crossed prior snapshot only
        self.assertEqual(inventory.queue_values(row,40,60),
            dict(displayed_depth_at_first_q=8.,queue_decay_per_minute=None))
        row['book_current'][2]=[]
        self.assertIsNone(inventory.queue_values(row,40,60)['displayed_depth_at_first_q'])

    def test_first_reference_is_causal_and_strict_holdout_matches_bound_library(self):
        members=[pair('earlier','2026-04-01',0,240),pair('later','2026-06-02',2000,2240)]
        query=pair('query','2026-06-01',1000,1240)
        reference=inventory.FirstQueueReference(CONTRACT)
        full=reference.levels(query,3,members)
        prior=reference.levels(query,3,members[:1])
        self.assertEqual(full,prior)  # future member cannot enter FIRST
        for leg in members[-1].legs:
            leg.values[:]+=10000  # sentinel in the excluded future pair
        altered=inventory.FirstQueueReference(CONTRACT).levels(query,3,members)
        self.assertEqual(full,altered)

    def test_flow_missing_never_uses_old_flow_and_queue_cache_is_freeze_bound(self):
        pairs,old,baseline,spec=population_fixture()
        inputs=inputs_fixture(pairs)
        with inventory.registry_adapter():
            sampler=inventory.sampler_type(inputs,'source',1024*1024)(old.metadata,old.sources,old.witnesses,CONTRACT,100)
            sampler.all_pairs=pairs
            calls=[]
            def project(reference,query,mode):
                calls.append(len(reference.pairs))
                q=40 if len(reference.pairs)==len(pairs) else 39
                return [dict(source_gate_minutes=gate,sides={leg.leg_id:dict(floors=dict(q50=dict(level_cents=q)))
                    for leg in query.legs}) for gate in CONTRACT['gates_minutes_to_bell']]
            with patch.object(bench.cv2.ReceiptProjector,'project',project):
                raw=sampler.sample(pairs[-1],[3])
                with sampler.use_library(pairs[:2]):
                    frozen=sampler.sample(pairs[-1],[3])
                again=sampler.sample(pairs[-1],[3])
            np.testing.assert_equal(raw,again)
            self.assertEqual(calls,[7,2])
            self.assertEqual(raw[0,0,panel.FEATURE_INDEX['displayed_depth_at_first_q']],8)
            self.assertEqual(frozen[0,0,panel.FEATURE_INDEX['displayed_depth_at_first_q']],4)
            for name in inventory.FLOW_FIELDS+('pressure_x_bid_response','sell_pressure_x_replenishment'):
                self.assertTrue(np.isnan(raw[0,0,panel.FEATURE_INDEX[name]]))
            self.assertEqual(sampler.state_cache.hits,1)

    def test_adapter_small_population_two_passes_and_first_unchanged(self):
        pairs,_,baseline,spec=population_fixture()
        inputs=inputs_fixture(pairs)
        with tempfile.TemporaryDirectory() as directory:
            for name in ('one','two'):
                with inventory.adapter(inputs,'fixture'),atlas.adapter('fixture',1024*1024):
                    pairs,sampler,baseline,spec=population_fixture()
                    sampler=compact_sampler_copy(sampler)
                    receipt,board=bench.run_category(pairs,sampler,baseline,spec,'category',Path(directory)/name,
                        heldout_months=('2026-06',),batch_size=2,cache_budget_bytes=8*1024*1024,
                        source_registry={'fixture':'synthetic'},progress=lambda row:None)
                    self.assertEqual(len(receipt['variants']),23)
                    self.assertEqual(receipt['eligible_games'],7)
                    self.assertGreater(sampler.state_cache.hits,0)
                    self.assertGreater(len(sampler.reference.bindings),1)
            launcher.compare_runs(Path(directory)/'one',Path(directory)/'two')
            # A v1 atlas on the same sources must retain exact FIRST outputs.
            with atlas.adapter('fixture',1024*1024):
                pairs,sampler,baseline,spec=population_fixture()
                _,prior=bench.run_category(pairs,sampler,baseline,spec,'category',Path(directory)/'prior',
                    heldout_months=('2026-06',),batch_size=2,cache_budget_bytes=8*1024*1024,
                    source_registry={'fixture':'synthetic'},progress=lambda row:None)
            for section in ('gates','all_receipts','filed_scorable_gates'):
                first=lambda obj:[{name:target['all_eligible']['FIRST'] for name,target in row['targets'].items()}
                                  for row in obj[section]['groups']]
                self.assertEqual(first(board),first(prior))


if __name__=='__main__':
    unittest.main()
