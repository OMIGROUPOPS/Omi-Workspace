"""Small synthetic orchestration proofs; no population data or engine run."""
from types import SimpleNamespace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import feature_panel_bench as bench
import feature_panel_model as model
import feature_panel_scoring as scoring
import tune_bench_v2_survivorship as b


def pair(event, date, formation, bell, offset=0):
    epochs = np.asarray([formation, formation+60, bell-30.], dtype=float)
    legs = []
    for name, prices in (("favorite", [60+offset, 58+offset, 62+offset]),
                          ("underdog", [40-offset, 42-offset, 38-offset])):
        prices = np.asarray(prices, dtype=float)
        legs.append(b.Leg(name, prices[0], formation, bell, epochs.copy(),
            np.column_stack((prices, prices-1, prices+1)), np.arange(len(epochs), dtype=float)+1,
            epochs.copy(), np.minimum.accumulate(prices), None,
            postformation_open=prices[0], count_epoch=epochs.copy(),
            print_count_cum=np.arange(len(epochs))+1))
    return b.Pair(event, "category", date, tuple(legs), formation, "TICK")


CONTRACT = dict(minute_seconds=60, gates_minutes_to_bell=[3, 1], role_drift_cents=2,
                no_call_ess_floor=1, quantiles=[.1, .25, .5, .75, .9], sleeper_category_quantile=.1)


class Sampler:
    def sample(self, pair, gates):
        values = np.empty((len(gates), len(pair.legs), 2))
        for side, leg in enumerate(pair.legs):
            values[:, side, 0] = leg.sample(pair.bell-np.asarray(gates)*60)[:, 0]
            values[:, side, 1] = 1
        return values


def kernel():
    fields = (SimpleNamespace(name="value", kind="numeric", block="price"),
              SimpleNamespace(name="source", kind="categorical", block="source"))
    scales = {"value": model.EmpiricalRankScale.fit([30, 40, 50, 60, 70])}
    return bench.RankedBlockKernel(fields, ("price", "source"), scales)


class FeaturePanelBenchTests(unittest.TestCase):
    def test_registry_six_cumulative_six_leaveout(self):
        blocks = tuple("abcdef")
        variants = bench.variant_registry(blocks)
        self.assertEqual(len(variants), 13)
        self.assertEqual(variants[0].name, "FIRST")
        self.assertEqual(variants[6].blocks, blocks)
        for variant in variants[7:]:
            self.assertEqual(len(variant.blocks), 5)

    def test_vectorized_kernel_matches_scalar_helper_with_missing(self):
        k = kernel()
        query = np.asarray([[60., 1.], [40., np.nan]])
        members = np.asarray([[[50., 1.], [40., 1.]], [[np.nan, 2.], [30., np.nan]],
                              [[np.nan, np.nan], [np.nan, np.nan]]])
        logs, support = k.compare_ranked(k.rank(query), k.rank(members))
        specs = {"price": [model.FeatureSpec("f.value", "numeric"), model.FeatureSpec("d.value", "numeric")],
                 "source": [model.FeatureSpec("f.source", "categorical"), model.FeatureSpec("d.source", "categorical")]}
        def flatten(values):
            return {name+"."+feature: values[side, column] for side, name in enumerate(("f", "d"))
                    for column, feature in enumerate(("value", "source"))}
        scales = {"f.value": k.scales["value"], "d.value": k.scales["value"]}
        reference = model.block_likelihoods(flatten(query), [flatten(m) for m in members], specs, scales)
        np.testing.assert_allclose(logs, reference["block_log_k"], rtol=0, atol=0)
        np.testing.assert_array_equal(support, reference["support_fraction"])

    def test_direct_sampler_uses_values_only_with_identical_model_matrix(self):
        from test_feature_panel import panel_fixture
        query, metadata, sources, witnesses, contract = panel_fixture()
        sampler = bench.DirectFeatureSampler(metadata, sources, witnesses, contract, 100)
        gates = np.asarray([4., 3., 2., 1.])
        full = bench.panel.build_pair_panel(query, metadata, sources, witnesses, contract, 100,
            sampler.codebooks, evaluation_gates=gates)["values"]
        with patch.object(bench.panel, "filed_spread_bands", side_effect=AssertionError("diagnostic route used")):
            sampled = sampler.sample(query, gates)
        np.testing.assert_equal(sampled, full)

    def test_first_projection_and_emitter_match_reference(self):
        members = [pair("member-a", "2026-04-01", 0, 240), pair("member-b", "2026-04-02", 250, 490, 1)]
        query = pair("query", "2026-05-01", 1000, 1240)
        k = kernel()
        projection = bench.FeatureProjector(members, Sampler(), CONTRACT, k, batch_size=2)
        registry = bench.variant_registry(k.blocks)
        frozen = bench.FrozenMonthModel("category", "2026-05", 1000, k,
            {v.name: np.zeros(len(k.blocks)) for v in registry}, {})
        receipts = list(projection.receipts(query))
        self.assertTrue(receipts)
        for receipt in receipts:
            forecasts, emitted = bench.emit_variants(query, receipt, frozen, registry, CONTRACT)
            for leg in query.legs:
                expected = receipt.baseline["sides"][leg.leg_id]
                first = emitted["FIRST"]["sides"][leg.leg_id]
                self.assertEqual(first.get("floors"), expected.get("floors"))
                self.assertEqual(first["member_count"], expected["member_count"])
                self.assertEqual(first["ess"], expected["ess"])

    def test_query_future_values_do_not_change_existing_prefix_forecast(self):
        members = [pair("member", "2026-04-01", 0, 240)]
        query = pair("query", "2026-05-01", 1000, 1240)
        before = next(bench.FeatureProjector(members, Sampler(), CONTRACT, kernel(), batch_size=1).receipts(query))
        changed = pair("query", "2026-05-01", 1000, 1240)
        for leg in changed.legs:
            leg.values[-1] += 10_000  # after the first receipt, deliberately impossible sentinel
        after = next(bench.FeatureProjector(members, Sampler(), CONTRACT, kernel(), batch_size=1).receipts(changed))
        np.testing.assert_array_equal(before.levels, after.levels)
        np.testing.assert_array_equal(before.block_log_k, after.block_log_k)
        self.assertEqual(before.baseline, after.baseline)

    def test_month_plan_never_fits_heldout_future_or_unresolved(self):
        def meta(event, month, formation, bell):
            return SimpleNamespace(event_id=event, category="category", date=month+"-01",
                                   formation=formation, bell=bell)
        population = [meta("apr", "2026-04", 0, 10), meta("may", "2026-05", 20, 30),
                      meta("unresolved-may", "2026-05", 40, 120), meta("june", "2026-06", 50, 60),
                      meta("july", "2026-07", 100, 130)]
        plan = bench.outer_month_plan(population, "category", "2026-07", ["2026-06"])
        self.assertEqual([p.event_id for p in plan["training"]], ["apr", "may"])
        may = next(f for f in plan["inner"] if f["month"] == "2026-05")
        self.assertEqual([p.event_id for p in may["training"]], ["apr"])
        self.assertEqual([p.event_id for p in may["validation"]], ["may"])
        self.assertTrue(may["partial_resolved_validation"])
        self.assertEqual(plan["cutoff"], 100)

    def test_positive_target_strictly_later_and_earliest_tie(self):
        rows = [[5, 40, 1, 1], [6, 30, 0, 2], [7, 35, 1, 3], [8, 35, 2, 4], [10, 1, 1, 5]]
        target = bench.PositivePrintTarget(rows, 0, 10, 1)
        self.assertEqual(target.at(5), dict(floor_cents=35., floor_mtb=3., has_future_print=True))
        self.assertEqual(target.at(7), dict(floor_cents=35., floor_mtb=2., has_future_print=True))
        self.assertFalse(target.at(8)["has_future_print"])

    def test_training_cache_budget_aborts_without_truncating(self):
        member = pair("member", "2026-04-01", 0, 240)
        query = pair("query", "2026-05-01", 1000, 1240)
        projector = bench.FeatureProjector([member], Sampler(), CONTRACT, kernel(), batch_size=2)
        with self.assertRaisesRegex(MemoryError, "no query dropped"):
            bench.collect_training_samples([query], projector, cache_budget_bytes=0)

    def test_causal_training_ranks_ignore_self_future_and_june(self):
        earlier = pair("earlier", "2026-04-01", 0, 240)
        heldout = pair("heldout", "2026-06-01", 250, 490)
        query = pair("query", "2026-07-01", 1000, 1240)
        future = pair("future", "2026-07-02", 1300, 1540)
        population = [earlier, heldout, query, future]
        k = kernel()
        cache = bench.CausalRankCache(population, Sampler(), k.fields, k.blocks, CONTRACT, ["2026-06"])
        before = cache.kernel_for(query).scales["value"].sorted_values.copy()
        for changed in (heldout, query, future):
            for leg in changed.legs:
                leg.values[:] += 100_000
            changed.__dict__.pop("_cache", None)
        after = bench.CausalRankCache(population, Sampler(), k.fields, k.blocks, CONTRACT,
                                      ["2026-06"]).kernel_for(query).scales["value"].sorted_values
        np.testing.assert_array_equal(before, after)
        proof = cache.receipt()["days"][0]
        self.assertEqual(proof["prior_event_ids"], ["earlier"])

    def test_evaluate_small_query_preserves_r0_and_two_targets(self):
        members = [pair("member-a", "2026-04-01", 0, 240), pair("member-b", "2026-04-02", 250, 490, 1)]
        query = pair("query", "2026-05-01", 1000, 1240)
        k = kernel()
        registry = bench.variant_registry(k.blocks)
        frozen = bench.FrozenMonthModel("category", "2026-05", 1000, k,
            {v.name: np.zeros(len(k.blocks)) for v in registry}, {})
        baseline = dict(organ_contract=CONTRACT, matched_step_first=dict(criterion=dict(
            minimum_matched_queries=100, minimum_step_strictly_closer_share=.5)))
        scorer = scoring.FeaturePanelScorer(baseline, [v.name for v in registry],
            groupings=(("category", "stream", "side"),))
        tapes = {}
        for leg in query.legs:
            rows = [[float(t), float(p), 1, i] for i, (t, p) in enumerate(zip(leg.epoch, leg.values[:, 0]))]
            tapes[query.event_id+"-"+leg.leg_id] = dict(formation_end_epoch=leg.formation,
                bell_epoch=leg.bell, prints=rows)
        result = bench.evaluate_query(query,
            bench.FeatureProjector(members, Sampler(), CONTRACT, k, batch_size=2),
            frozen, registry, scorer, members+[query], tapes,
            dict(par=100, pair_budget=99, minimum_cent=1, maximum_cent=99), ["2026-06"], stream="TEST")
        first = result["conduct"]["FIRST"]
        for row in result["conduct"].values():
            self.assertEqual(row, first)
        self.assertGreater(scorer.finish()["seen_receipts"], 0)

    def test_no_inner_training_means_zero_not_invented_coefficients(self):
        population = [pair("earlier", "2026-04-01", 0, 240), pair("query", "2026-05-01", 1000, 1240)]
        k = kernel()
        plan = bench.outer_month_plan(population, "category", "2026-05", ["2026-06"])
        registry = bench.variant_registry(k.blocks)
        fitted = bench.fit_outer_month(plan, population, Sampler(), k.fields, k.blocks, registry, CONTRACT,
            heldout_months=["2026-06"], batch_size=2, cache_budget_bytes=1_000_000)
        for coefficients in fitted.coefficients.values():
            np.testing.assert_array_equal(coefficients, np.zeros(len(k.blocks)))
        for choice in fitted.receipt["model_class_choices"].values():
            self.assertEqual(choice["selected"], "FIRST_ZERO")
            self.assertEqual(choice["reason"], "NO_USABLE_INNER_VALIDATION")

    def test_raw_ranks_and_exact_scales_are_persisted_deterministically(self):
        query = pair("query", "2026-05-01", 1000, 1240)
        k = kernel()
        frozen = bench.FrozenMonthModel("category", "2026-05", 900, k, {}, {})
        raw = np.asarray([[[50., 1.], [np.nan, 1.]], [[60., 1.], [40., 1.]]])
        data = dict(values=raw, epochs=np.array([1060, 1180]), gates=np.array([3, 1]), is_gate=np.array([True, True]),
            diagnostic_arrays={leg.leg_id: {"spread_band": np.array([0., 1.])} for leg in query.legs},
            coverage={leg.leg_id: dict(receipts=2, fields={}) for leg in query.legs}, diagnostics=[])
        sampler = SimpleNamespace(metadata={}, sources={}, witnesses={}, contract=CONTRACT, par=100, codebooks={})
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory)/"a", Path(directory)/"b"
            first.mkdir(); second.mkdir()
            proofs = []
            for folder in (first, second):
                scales = bench.write_scale_diagnostics(folder, frozen, CONTRACT)
                with patch.object(bench.panel, "build_pair_panel", return_value=data):
                    result = bench.write_query_diagnostics(folder, query, frozen, sampler, "PRIMARY", scales)
                proofs.append(result)
                with np.load(folder/result["path"], allow_pickle=False) as arrays:
                    np.testing.assert_array_equal(arrays["raw_value"], raw)
                    np.testing.assert_array_equal(arrays["empirical_rank"], k.rank(raw))
                self.assertEqual(result["scale_cutoff"], 900)
                self.assertEqual(result["month"], "2026-05")
            self.assertEqual(proofs[0], proofs[1])

    def test_coverage_scores_do_not_authorize(self):
        row = dict(qualifies=True, filed_side_gate_scope=True, criterion_met_on_matched_receipts=True)
        payload = dict(groups=[dict(targets=dict(carried=dict(matched_to_first=dict(variant=row))))])
        result = bench.disable_unfiled_authorization(payload)
        self.assertIsNone(result["groups"][0]["targets"]["carried"]["matched_to_first"]["variant"]["qualifies"])
        self.assertFalse(row["filed_side_gate_scope"])
        self.assertTrue(row["criterion_met_on_matched_receipts"])


if __name__ == "__main__":
    unittest.main()
