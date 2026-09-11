"""Execution-storage parity; synthetic fixtures are not model calibration."""
import copy
import gc
import pickle
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

import conduct_scoreboard as conduct
import feature_panel as panel
import feature_panel_bench as bench
import feature_panel_execution as execution
import feature_panel_parallel as parallel
from test_conduct_scoreboard import receipt, state, SPEC
from test_feature_panel import panel_fixture
from test_feature_panel_bench import pair, kernel, Sampler, CONTRACT


class CompactPrintTests(unittest.TestCase):
    def assert_exact(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        if isinstance(expected, np.ndarray):
            self.assertEqual(actual.dtype, expected.dtype)
            self.assertEqual(actual.shape, expected.shape)
            self.assertEqual(actual.tobytes(), expected.tobytes())
        elif isinstance(expected, dict):
            self.assertEqual(actual.keys(), expected.keys())
            for key in expected:
                self.assert_exact(actual[key], expected[key])
        elif isinstance(expected, (list, tuple)):
            self.assertEqual(len(actual), len(expected))
            for left, right in zip(actual, expected):
                self.assert_exact(left, right)
        elif isinstance(expected, float):
            self.assertEqual(struct.pack("d", actual), struct.pack("d", expected))
        else:
            self.assertEqual(actual, expected)

    def numeric_fixture(self):
        payload_nan = struct.unpack("d", struct.pack("Q", 0x7ff8000000000042))[0]
        return [[1.25, -0.0, 2, (1 << 53)+1, "feed"],
                [1, 1.0, (1 << 64)-1, -(1 << 63), None],
                (float("inf"), -float("inf"), payload_nan, True, "feed"),
                [False, 4, .125, 0], [3.5, 99, 1.5, 6, ""],
                [1, 2, 3, 4, "second-feed"]]

    def test_rows_indices_slices_values_types_and_float_bits(self):
        original = self.numeric_fixture()
        compact = execution.CompactPrintRows(original)
        self.assertEqual(len(compact), len(original))
        self.assert_exact(list(compact), original)
        for index in range(-len(original), len(original)):
            self.assert_exact(compact[index], original[index])
        for index in (slice(None), slice(None, None, -1), slice(1, 5, 2),
                      slice(-5, -1), slice(100), slice(3, 2), slice(None, None, -2)):
            self.assert_exact(compact[index], original[index])
        self.assert_exact(compact[np.int64(0)], original[0])
        self.assertEqual(compact._sources, ("feed", "", "second-feed"))
        for index in (len(original), -len(original)-1):
            with self.assertRaises(IndexError):
                compact[index]
        with self.assertRaises(TypeError):
            compact[1.5]
        with self.assertRaises(ValueError):
            compact[::0]
        self.assertEqual(list(execution.CompactPrintRows([])), [])

    def test_immutable_and_independent_from_input_rows(self):
        original = [[1, 2., 3, 4, "feed"]]
        compact = execution.CompactPrintRows(original)
        original[0][0] = 8
        compact[0][0] = 9
        self.assertEqual(compact[0], [1, 2., 3, 4, "feed"])
        with self.assertRaises(AttributeError):
            compact._sources = ()
        with self.assertRaises(AttributeError):
            del compact._sources
        with self.assertRaises(TypeError):
            compact[0] = [1, 2., 3, 4, "feed"]
        for name in ("_bits", "_kinds", "_source_ids", "_tuple_rows"):
            array = getattr(compact, name)
            self.assertFalse(array.dtype.hasobject)
            self.assertFalse(array.flags.writeable)
            with self.assertRaises(ValueError):
                array.flat[0] = 0

    def test_unsupported_payloads_fail_instead_of_coercing(self):
        for value in (None, "2", complex(2), np.float64(2), np.int64(2)):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(TypeError, "UNSUPPORTED_PRINT_NUMERIC_TYPE"):
                    execution.CompactPrintRows([[1, value, 3, 4]])
        for value in (1 << 64, -(1 << 63)-1):
            with self.assertRaisesRegex(ValueError, "PRINT_INTEGER_OUT_OF_64_BIT_RANGE"):
                execution.CompactPrintRows([[1, 2, 3, value]])
        for row in ([1, 2, 3], [1, 2, 3, 4, "feed", 6], np.arange(4)):
            with self.assertRaisesRegex(ValueError, "UNSUPPORTED_PRINT_ROW_SHAPE"):
                execution.CompactPrintRows([row])
        with self.assertRaisesRegex(TypeError, "UNSUPPORTED_PRINT_SOURCE_TYPE"):
            execution.CompactPrintRows([[1, 2, 3, 4, 5]])

    def test_pickle_and_readonly_snapshot_roundtrip_preserve_aliases(self):
        compact = execution.CompactPrintRows(self.numeric_fixture())
        restored = pickle.loads(pickle.dumps(compact, protocol=pickle.HIGHEST_PROTOCOL))
        self.assert_exact(list(restored), self.numeric_fixture())
        self.assertFalse(restored._bits.flags.writeable)
        with tempfile.TemporaryDirectory() as directory:
            proof = parallel.write_shared_snapshot([compact, compact], Path(directory)/"compact")
            restored = parallel.load_shared_snapshot(proof)
            self.assertIs(restored[0], restored[1])
            self.assert_exact(list(restored[0]), self.numeric_fixture())
            self.assertFalse(restored[0]._bits.flags.writeable)
            self.assertIsInstance(restored[0]._bits.base, np.memmap)
            del restored
            gc.collect()

    def test_snapshot_object_payload_stays_small_when_row_count_grows(self):
        count = 10000
        original = [[float(i)+.25, 42., 1, (1 << 53)+i, "feed"] for i in range(count)]
        compact = execution.CompactPrintRows(original)
        with tempfile.TemporaryDirectory() as directory:
            ordinary = parallel.write_shared_snapshot(original, Path(directory)/"ordinary")
            packed = parallel.write_shared_snapshot(compact, Path(directory)/"compact")
            self.assertLess(Path(packed["data"]).stat().st_size, 2000)
            self.assertGreater(Path(ordinary["data"]).stat().st_size,
                               Path(packed["data"]).stat().st_size*100)
            self.assertEqual(Path(packed["arrays"]).stat().st_size, count*41)

    def test_copy_preserves_aliases_metadata_and_prepared_cache_identity(self):
        rows = [[1, 2., 3, 4, "feed"]]
        prefix = {"epochs": np.asarray([1.])}
        record = dict(prints=rows, positive_prints=rows, _prefix=prefix,
                      formation_end_epoch=0, extra={"nested": True})
        sampler = SimpleNamespace(sources={"source": record}, witnesses={"witness": record},
            metadata={"source": {"all": "fields"}, "witness": {}, "irrelevant": {}},
            codebooks={"source": {"global": 99}}, unknown_attribute="retained")
        compact = execution.compact_sampler_copy(sampler)
        self.assertIsNot(compact, sampler)
        self.assertIsNot(compact.sources, sampler.sources)
        self.assertIsNot(compact.witnesses, sampler.witnesses)
        copied = compact.witnesses["witness"]
        self.assertIsNot(copied, record)
        self.assertIs(compact.sources["source"], copied)
        self.assertIs(copied["prints"], copied["positive_prints"])
        self.assertIs(copied["_prefix"], prefix)
        self.assertIs(copied["extra"], record["extra"])
        self.assertEqual(compact.metadata, {"source": {"all": "fields"}, "witness": {}})
        self.assertIn("irrelevant", sampler.metadata)
        self.assertIs(compact.codebooks, sampler.codebooks)
        self.assertEqual(compact.unknown_attribute, sampler.unknown_attribute)
        self.assertIs(record["prints"], rows)
        again = execution.compact_sampler_copy(compact)
        self.assertIs(again.witnesses["witness"]["prints"], copied["prints"])

    def test_copy_keeps_distinct_payloads_and_missing_or_null_fields(self):
        first, second = [[1, 2, 3, 4]], [[4, 3, 2, 1]]
        witnesses = {"both": dict(prints=first, positive_prints=second),
                     "missing": {}, "null": dict(prints=None)}
        sampler = SimpleNamespace(sources={}, witnesses=witnesses, metadata={})
        compact = execution.compact_sampler_copy(sampler)
        self.assertEqual(compact.witnesses["both"]["prints"][:], first)
        self.assertEqual(compact.witnesses["both"]["positive_prints"][:], second)
        self.assertEqual(compact.witnesses["missing"], {})
        self.assertIsNone(compact.witnesses["null"]["prints"])

    def test_raw_source_payloads_retained_until_prepared(self):
        source = dict(oi=[[60, 12, 12, None]], odds_poll_epochs=[50],
            oi_columns=["available_epoch", "open_interest_at_minute_end", "open_interest_ffill",
                        "open_interest_delta_from_prior_minute"], odds_status="NOT_EXTRACTED")
        sampler = SimpleNamespace(sources={"x": source}, witnesses={}, metadata={})
        self.assertEqual(execution.compact_sampler_copy(sampler).sources, sampler.sources)
        panel.prepare_sources(sampler.sources, {})
        compact = execution.compact_sampler_copy(sampler)
        self.assertNotIn("oi", compact.sources["x"])
        self.assertNotIn("odds_poll_epochs", compact.sources["x"])
        self.assertIn("oi", source)
        self.assertIn("odds_poll_epochs", source)
        self.assertIsNone(compact.sources["x"]["odds_snapshot_epochs"])
        self.assertEqual(compact.sources["x"]["oi_columns"], source["oi_columns"])

    def test_direct_sampler_full_diagnostics_and_global_codebooks_match(self):
        query, metadata, sources, witnesses, contract = panel_fixture()
        metadata["unrelated"] = dict(formation_source="AAA_GLOBAL", bell_source="AAA_GLOBAL")
        for witness in witnesses.values():
            witness["positive_prints"] = witness["prints"]
        sampler = bench.DirectFeatureSampler(metadata, sources, witnesses, contract, 100)
        gates = np.asarray([5., 4., 3., 2., 1.])
        expected = sampler.sample(query, gates)
        full = panel.build_pair_panel(query, metadata, sources, witnesses, contract, 100,
                                      sampler.codebooks, evaluation_gates=gates)
        compact = execution.compact_sampler_copy(sampler)
        self.assertIs(compact.codebooks, sampler.codebooks)
        self.assertIn("AAA_GLOBAL", compact.codebooks["formation_source"])
        self.assertNotIn("unrelated", compact.metadata)
        self.assert_exact(compact.sample(query, gates), expected)
        self.assert_exact(panel.build_pair_panel(query, compact.metadata, compact.sources,
            compact.witnesses, contract, 100, compact.codebooks, evaluation_gates=gates), full)
        for key, source in compact.sources.items():
            self.assertNotIn("oi", source)
            self.assertNotIn("odds_poll_epochs", source)
            self.assertEqual(source.keys(), sources[key].keys()-{"oi", "odds_poll_epochs"})
            self.assertIs(source["open_interest"], sources[key]["open_interest"])
            self.assertIs(source["odds_snapshot_epochs"], sources[key]["odds_snapshot_epochs"])
        panel.prepare_sources(compact.sources, compact.witnesses, minute_seconds=60)
        self.assert_exact(compact.sample(query, gates), expected)
        with tempfile.TemporaryDirectory() as directory:
            proof = parallel.write_shared_snapshot(compact, Path(directory)/"sampler")
            restored = parallel.load_shared_snapshot(proof)
            self.assert_exact(restored.sample(query, gates), expected)
            self.assert_exact(panel.build_pair_panel(query, restored.metadata, restored.sources,
                restored.witnesses, contract, 100, restored.codebooks, evaluation_gates=gates), full)
            self.assertIs(restored.witnesses["fixture-F"]["prints"],
                          restored.witnesses["fixture-F"]["positive_prints"])
            del restored
            gc.collect()

    def test_positive_targets_and_conduct_outputs_remain_exact(self):
        tapes = {"A": [[100, 45., 1, (1 << 60)+1, "feed"],
                        [101, 48., 0, (1 << 60)+2, "feed"],
                        [102., 48, 2., (1 << 60)+4, None],
                        [102., 47, 3, (1 << 60)+3, "feed"],
                        [1000, 1, 1, (1 << 60)+5]],
                 "B": [[102, 39, 1, 9, "feed"]]}
        compact = {key: execution.CompactPrintRows(rows) for key, rows in tapes.items()}
        forecasts = [receipt(100, state(50)), receipt(200, state(40))]
        spec = dict(SPEC, positive_size_fills=True)
        expected = conduct.simulate_conduct("FIXTURE", ["A", "B"], copy.deepcopy(forecasts),
                                            tapes, 0, 1000, spec, 0)
        actual = conduct.simulate_conduct("FIXTURE", ["A", "B"], copy.deepcopy(forecasts),
                                          compact, 0, 1000, spec, 0)
        self.assert_exact(actual, expected)
        self.assertEqual(actual["fills"]["A"]["print_rowid"], (1 << 60)+3)
        original_target = bench.PositivePrintTarget(tapes["A"], 0, 1000, 60)
        compact_target = bench.PositivePrintTarget(compact["A"], 0, 1000, 60)
        for epoch in (0, 100, 101, 102, 999):
            self.assert_exact(compact_target.at(epoch), original_target.at(epoch))

    def test_emitter_only_aliases_conduct_rows_with_identical_writers(self):
        members = [pair("member", "2026-04-01", 0, 240)]
        query = pair("query", "2026-05-01", 1000, 1240)
        ranked = kernel()
        registry = bench.variant_registry(ranked.blocks)
        coefficients = {variant.name: np.zeros(len(ranked.blocks)) for variant in registry}
        for variant in registry[-2:]:
            coefficients[variant.name][:] = .5
        frozen = bench.FrozenMonthModel("category", "2026-05", 1000, ranked, coefficients, {})
        candidate = next(bench.FeatureProjector(members, Sampler(), CONTRACT, ranked, batch_size=1).receipts(query))
        forecasts, rows = bench.emit_variants(query, candidate, frozen, registry, CONTRACT)
        first = rows["FIRST"]
        for variant in registry[:-2]:
            self.assertIs(rows[variant.name], first)
            for leg in query.legs:
                self.assertIs(forecasts[variant.name][leg.leg_id], forecasts["FIRST"][leg.leg_id])
                self.assertEqual(rows[variant.name]["sides"][leg.leg_id]["writer"], "POOL_FIRST_TICK")
        self.assertIsNot(rows[registry[-1].name], rows[registry[-2].name])
        for variant in registry[-2:]:
            for leg in query.legs:
                self.assertEqual(rows[variant.name]["sides"][leg.leg_id]["writer"], "FEATURE_PANEL:"+variant.name)


if __name__ == "__main__":
    unittest.main()
