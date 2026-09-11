"""Execution parity only: synthetic fixtures are never model calibration."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest

import numpy as np

import feature_panel as panel
import feature_panel_bench as bench
import feature_panel_model as model
import feature_panel_parallel as parallel
import feature_panel_run as run
import tune_bench_v2_survivorship as b
from test_feature_panel_bench import pair, CONTRACT


def population_fixture():
    pairs, metadata, sources, witnesses = [], {}, {}, {}
    for number, (name, date) in enumerate((('a', '2026-04-01'), ('b', '2026-04-02'),
            ('c', '2026-05-01'), ('d', '2026-05-02'), ('e', '2026-06-01'),
            ('f', '2026-06-02'), ('g', '2026-07-01'))):
        query = pair(name, date, number*500, number*500+240, number % 2)
        pairs.append(query)
        for leg in query.legs:
            ticker = name+'-'+leg.leg_id
            metadata[ticker] = dict(formation_source='FIRST_BOTH_SIDES_TRADE', bell_source='scheduled')
            sources[ticker] = dict(books=[], minute_features=[], book_observation_epochs=[],
                clock_provenance=dict(bell_publication_epoch=leg.formation), first_two_sided_book_epoch=leg.formation,
                first_source_book_was_two_sided=False)
            witnesses[ticker] = dict(formation_end_epoch=leg.formation, bell_epoch=leg.bell,
                prints=[[float(epoch), float(price), 1, i] for i, (epoch, price)
                        in enumerate(zip(leg.epoch, leg.values[:, 0]))])
    baseline = dict(organ_contract=CONTRACT, matched_step_first=dict(criterion=dict(
        minimum_matched_queries=100, minimum_step_strictly_closer_share=.5)))
    spec = dict(par=100, pair_budget=99, minimum_cent=1, maximum_cent=99)
    sampler = bench.DirectFeatureSampler(metadata, sources, witnesses, CONTRACT, spec['par'])
    return pairs, sampler, baseline, spec


class ParallelTests(unittest.TestCase):
    def test_readonly_shared_arrays_preserve_values_strides_aliases(self):
        source = np.arange(30., dtype=float).reshape(5, 6)
        source[1, 1] = np.nan
        arrays = [source, source, source.T, source[::-1, ::2],
                  np.asfortranarray(source), np.array(3.), np.empty((0, 2)),
                  np.asarray(['a', 'b'], dtype=object)]
        with tempfile.TemporaryDirectory() as directory:
            proof = parallel.write_shared_snapshot(arrays, Path(directory)/'fixture')
            restored = parallel.load_shared_snapshot(proof)
            self.assertIs(restored[0], restored[1])
            for original, actual in zip(arrays, restored):
                np.testing.assert_equal(original, actual)
                self.assertEqual(original.dtype, actual.dtype)
                if not original.dtype.hasobject:
                    self.assertFalse(actual.flags.writeable)
                    if original.size:
                        self.assertEqual(original.strides, actual.strides)
            del restored  # Close mappings before Windows temporary cleanup.
            with Path(proof['arrays']).open('ab') as stream:
                stream.write(b'x')
            with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
                parallel.load_shared_snapshot(proof)

    def test_bounded_futures_keep_original_order(self):
        seen = []
        class Future:
            def __init__(self, owner, value):
                self.owner, self.value = owner, value
            def result(self):
                self.owner.active -= 1
                return self.value
            def cancel(self):
                self.owner.active -= 1
        class Executor:
            active = 0
            maximum = 0
            def submit(self, function, task):
                self.active += 1
                self.maximum = max(self.maximum, self.active)
                seen.append(task)
                return Future(self, function(task))
        executor = Executor()
        values = list(parallel.ordered_bounded_map(executor, lambda x: x*x, range(9), 3))
        self.assertEqual(values, [x*x for x in range(9)])
        self.assertEqual(seen, list(range(9)))
        self.assertEqual(executor.maximum, 3)
        self.assertEqual(executor.active, 0)

    def test_spawn_one_and_two_workers_nonzero_model_match_direct_bytes(self):
        pairs, sampler, baseline, spec = population_fixture()
        fields = tuple(f for f in panel.FIELDS if f.block is not None)
        blocks, registry = tuple(panel.BLOCKS), bench.variant_registry(panel.BLOCKS)
        scales, _ = bench.fit_category_scales(pairs[:4], sampler, fields, CONTRACT)
        kernel = bench.RankedBlockKernel(fields, blocks, scales)
        coefficients = {v.name: np.zeros(len(blocks)) for v in registry}
        for variant in registry:
            for block in variant.blocks:
                coefficients[variant.name][blocks.index(block)] = 0.5
        frozen = bench.FrozenMonthModel('category', '2026-06', pairs[4].formation,
            kernel, coefficients, {})
        serial_channels = parallel.scorer_channels(baseline, [v.name for v in registry])
        expected, diagnostics = [], []
        with tempfile.TemporaryDirectory() as directory:
            serial_dir = Path(directory)/'serial'
            serial_dir.mkdir()
            proof = bench.write_scale_diagnostics(serial_dir, frozen, CONTRACT)
            for stream, cutoff in (('PRIMARY', None), ('STRICT_HOLDOUT', frozen.cutoff)):
                library = pairs if cutoff is None else pairs[:4]
                projector = bench.FeatureProjector(library, sampler, CONTRACT, kernel, batch_size=2)
                for query in pairs[4:6]:
                    result = bench.evaluate_query(query, projector, frozen, registry, serial_channels['all'],
                        pairs, sampler.witnesses, spec, ['2026-06'], stream=stream,
                        frozen_library_cutoff=cutoff, gate_scorer=serial_channels['gates'],
                        filed_gate_scorer=serial_channels['filed'])
                    diagnostic = bench.write_query_diagnostics(serial_dir, query, frozen, sampler, stream, proof)
                    result['receipt_diagnostics'] = diagnostic['path']
                    expected.append(result)
                    diagnostics.append(diagnostic)
            for workers in (1, 2):
                folder = Path(directory)/str(workers)
                folder.mkdir()
                channels = parallel.scorer_channels(baseline, [v.name for v in registry])
                scale = bench.write_scale_diagnostics(folder, frozen, CONTRACT)
                actual, actual_diagnostics = [], []
                with parallel.QueryPool(pairs, sampler, baseline, spec, registry, ['2026-06'], 2, folder, workers) as pool:
                    for stream, cutoff in (('PRIMARY', None), ('STRICT_HOLDOUT', frozen.cutoff)):
                        for complete in pool.evaluate(pairs[4:6], frozen, scale, stream, cutoff, channels):
                            actual.append(complete['result'])
                            actual_diagnostics.append(complete['diagnostic'])
                    private = pool.private
                self.assertFalse(private.exists())
                self.assertEqual(json.dumps(b.clean(expected), sort_keys=True), json.dumps(b.clean(actual), sort_keys=True))
                self.assertEqual(diagnostics, actual_diagnostics)
                for name in channels:
                    self.assertEqual(json.dumps(serial_channels[name].finish(), sort_keys=True),
                                     json.dumps(channels[name].finish(), sort_keys=True))
                for item in diagnostics:
                    self.assertEqual((serial_dir/item['path']).read_bytes(), (folder/item['path']).read_bytes())

    def test_full_run_serial_parallel_identical_months_and_june_holdout(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for workers in (1, 2):
                pairs, sampler, baseline, spec = population_fixture()
                folder = Path(directory)/str(workers)
                bench.run_category(pairs, sampler, baseline, spec, 'category', folder,
                    heldout_months=['2026-06'], batch_size=2, cache_budget_bytes=1_000_000,
                    source_registry={'fixture': 'synthetic'}, workers=workers, progress=lambda _: None)
                paths.append(folder)
            proof = run.compare_runs(*paths)
            self.assertEqual(proof['status'], 'DETERMINISTIC')


if __name__ == '__main__':
    unittest.main()
