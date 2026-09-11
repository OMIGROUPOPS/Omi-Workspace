"""Synthetic correctness and denominator tests, never fitted bench parameters."""
import copy
from collections import defaultdict
from dataclasses import FrozenInstanceError, replace
import json
import pickle
import unittest
from unittest.mock import patch

import numpy as np

from feature_panel_scoring import (FeaturePanelScorer, ScoreContract,
                                   effective_sample_size, score_distribution,
                                   weighted_crps, weighted_quantile, prepare_candidate_support,
                                   prepared_quantiles)
from feature_panel_scoring import _Cell, _Matched, _core_metric


def baseline(ess=2, n=3, share=.5):
    return dict(organ_contract=dict(no_call_ess_floor=ess, quantiles=[.1, .25, .5, .75, .9]),
                matched_step_first=dict(criterion=dict(minimum_matched_queries=n,
                    minimum_step_strictly_closer_share=share)))


def forecast(level=30, count=2):
    return dict(values=[level]*count, weights=[1]*count, times=[5]*count,
                families=["GRIND"]*count)


def identity(event, category="ATP_MAIN", side="favorite", receipt=None, month="2026-06", stream="GATES"):
    return dict(category=category, event_id=event, side=side, receipt_id=receipt or event,
                month=month, gate=10, role="FALLER", stream=stream)


def targets(level=30, reachable=28):
    return dict(carried=dict(floor_cents=level, floor_mtb=5, family="GRIND"),
                reachable=dict(floor_cents=reachable, floor_mtb=4,
                               has_future_print=reachable is not None, family="GRIND"))


def legacy_add_receipt(panel, identity, targets, forecasts, *, eligible=True):
    """Pre-worker add_receipt body retained as an independent arithmetic ruler."""
    required = ("category", "event_id", "side", "receipt_id")
    key = tuple(identity[k] for k in required) + (identity.get("stream"),)
    event_key = (identity["category"], identity["event_id"], identity.get("stream"))
    same_event = panel.identity_mode == "all" or event_key == panel.current_event
    if same_event and key in panel.identities:
        raise ValueError("DUPLICATE_RECEIPT_IDENTITY:" + repr(key))
    if panel.identity_mode == "contiguous_event" and event_key in panel.completed_events:
        raise ValueError("NONCONTIGUOUS_EVENT:" + repr(event_key))
    unknown = set(forecasts)-set(panel.variants)
    if unknown:
        raise ValueError("UNREGISTERED_VARIANTS:" + repr(sorted(unknown)))
    scored = {}
    if eligible:
        for target in panel.target_kinds:
            rows, cache = {}, {}
            for variant in panel.variants:
                forecast = forecasts.get(variant)
                cache_key = id(forecast)
                if cache_key not in cache:
                    row = score_distribution(forecast, targets.get(target), panel.contract, target_name=target)
                    if panel.metric_profile == "core":
                        row["metrics"] = {name: value for name, value in row["metrics"].items() if _core_metric(name)}
                    cache[cache_key] = row
                rows[variant] = cache[cache_key]
            scored[target] = rows
    if panel.identity_mode == "contiguous_event" and event_key != panel.current_event:
        if panel.current_event is not None:
            panel.completed_events.add(panel.current_event)
        panel.identities.clear()
        panel.current_event = event_key
    panel.identities.add(key)
    panel.seen_receipts += 1
    if not eligible:
        panel.excluded += 1
        return
    for fields in panel.groupings:
        group = {field: identity.get(field) for field in fields}
        group_key = tuple(group.items())
        entry = panel.groups.setdefault(group_key, {})
        for target, rows in scored.items():
            cells = entry.setdefault(target, dict(variants=defaultdict(_Cell), matched=defaultdict(_Matched),
                                                  common=defaultdict(_Cell), common_n=0))
            for variant, row in rows.items():
                cells["variants"][variant].add(row)
                if variant != panel.baseline:
                    cells["matched"][variant].add(identity["event_id"], row, rows[panel.baseline])
            if all(row["called"] and row["target_floor_available"] for row in rows.values()):
                cells["common_n"] += 1
                if panel.common_variant_metrics:
                    for variant, row in rows.items():
                        cells["common"][variant].add(row)


class DistributionTests(unittest.TestCase):
    def test_crps_matches_quadratic_definition_and_is_scale_invariant(self):
        x = np.array([3., 8., 8., -2.])
        w = np.array([1., 4., 2., 3.])
        p = w/w.sum()
        expected = np.dot(p, abs(x-4)) - .5*np.sum(p[:, None]*p[None, :]*abs(x[:, None]-x[None, :]))
        self.assertAlmostEqual(weighted_crps(x, w, 4), expected)
        self.assertAlmostEqual(weighted_crps(x, w*1e300, 4), expected)
        self.assertEqual(weighted_crps([7], [1], 4), 3)
        self.assertEqual(weighted_crps([7], [1], 7), 0)

    def test_quantile_tie_and_zero_weight(self):
        self.assertEqual(weighted_quantile([40, 10, 30], [1, 0, 1], .5), 30)
        self.assertEqual(weighted_quantile([40, 10, 30], [1, 0, 1], 1), 40)
        self.assertIsNone(weighted_quantile([30], [0], .5))
        with self.assertRaisesRegex(ValueError, "INVALID_WEIGHTS"):
            weighted_quantile([30], [-1], .5)

    def test_baseline_boundaries_and_same_forecast_two_truths(self):
        c = ScoreContract.from_baseline(baseline())
        a = score_distribution(forecast(), targets()["carried"], c)
        b = score_distribution(forecast(), targets()["reachable"], c)
        self.assertEqual(a["quantiles"], b["quantiles"])
        self.assertEqual(a["metrics"]["floor_signed_error_cents"], 0)
        self.assertEqual(b["metrics"]["floor_signed_error_cents"], 2)
        self.assertEqual(b["metrics"]["floor_timing_signed_error_minutes"], 1)
        self.assertEqual(b["metrics"]["floor_band.q25_q75.nominal_calibration_gap"], -.5)
        self.assertFalse(score_distribution(forecast(count=1), targets()["carried"], c)["called"])
        self.assertTrue(a["called"])
        self.assertFalse(score_distribution(forecast(), targets()["carried"],
                                           ScoreContract.from_baseline(baseline(ess=3)))["called"])
        withheld = dict(forecast(), status="UNAVAILABLE_FEATURE_BLOCK")
        self.assertFalse(score_distribution(withheld, targets()["carried"], c)["called"])

    def test_missing_print_target_keeps_reach_zero_without_fake_floor_error(self):
        row = score_distribution(forecast(), targets(reachable=None)["reachable"],
                                 ScoreContract.from_baseline(baseline()))
        self.assertTrue(row["called"])
        self.assertNotIn("floor_absolute_error_cents", row["metrics"])
        self.assertEqual(row["metrics"]["reach.support.observed_rate"], 0)
        self.assertEqual(row["metrics"]["reach.q50.brier"], 1)

    def test_missing_candidates_recompute_ess_and_disclose_removed_mass(self):
        row = score_distribution(dict(values=[30, None, 31], weights=[1, 2, 1]),
                                 targets()["carried"], ScoreContract.from_baseline(baseline()))
        self.assertTrue(row["called"])
        self.assertEqual(row["ess"], 2)
        self.assertEqual(row["candidate_floor_available_weight_share"], .5)
        self.assertAlmostEqual(effective_sample_size([1e300, 1e300]), 2)

    def test_family_zero_probability_is_infinite_without_epsilon(self):
        c = ScoreContract.from_baseline(baseline())
        row = score_distribution(forecast(), dict(floor_cents=30, family="DIP"), c)
        self.assertEqual(row["family"]["log_loss"], "INF")
        self.assertEqual(row["metrics"]["family_accuracy"], 0)
        self.assertEqual(row["metrics"]["family_brier"], 2)

    def test_shared_reach_grid_preserves_receipt_denominator(self):
        target = dict(floor_cents=30, has_future_print=True, reach_levels=[20, 30, 40])
        row = score_distribution(forecast(), target, ScoreContract.from_baseline(baseline()))
        self.assertEqual(row["metrics"]["reach.support.level_count"], 3)
        self.assertEqual(row["metrics"]["reach.support.mean_probability"], 2/3)
        self.assertEqual(row["metrics"]["reach.support.brier"], 0)

    def test_ready_metrics_supports_independent_target_names(self):
        row = dict(ess=2, metrics_by_target={"reachable": {"floor_crps_cents": 3}})
        result = score_distribution(row, targets()["reachable"], ScoreContract.from_baseline(baseline()),
                                    target_name="reachable")
        self.assertEqual(result["metrics"], {"floor_crps_cents": 3})

    def test_prepared_support_exact_equivalence_with_asymmetric_weights(self):
        c = ScoreContract.from_baseline(baseline(ess=1))
        values = np.array([40., 20., np.nan, 30., 30.])
        times = np.array([5., 8., 2., np.nan, 7.])
        families = ["A", "B", "A", "C", "B"]
        support = prepare_candidate_support(values, times, families)
        for weights in ([3., 1., 7., 0., 2.], [0., 4., 0., 3., 1.], [1., 1., 1., 1., 1.]):
            plain = dict(values=values, weights=weights, times=times, families=families)
            cached = dict(support=support, weights=weights)
            target = dict(floor_cents=29, floor_mtb=4, has_future_print=True, family="B",
                          reach_levels=[10, 20, 25, 30, 35, 40, 45])
            self.assertEqual(score_distribution(plain, target, c), score_distribution(cached, target, c))
            quantiles = prepared_quantiles(support, weights, c.quantiles)
            for q in c.quantiles:
                self.assertEqual(quantiles['q'+format(q*100, '.12g')], dict(
                    level_cents=weighted_quantile(values, weights, q),
                    minutes_to_bell=weighted_quantile(times, weights, q)))
        values[0] = 99
        self.assertEqual(support.values[0], 40)
        with self.assertRaises(ValueError):
            support.values[0] = 99


class PanelTests(unittest.TestCase):
    def scorer(self, **kwargs):
        return FeaturePanelScorer(baseline(), ["FIRST", "JOINT", "LOO"], **kwargs)

    def group(self, result, **wanted):
        return next(g for g in result["groups"] if g["group"] == wanted)

    def test_matched_counts_abstention_ties_and_authorization(self):
        panel = self.scorer(groupings=(("category", "side", "gate"),))
        for event, joint in (("a", forecast(30)), ("b", forecast(30)), ("c", forecast(35))):
            panel.add_receipt(identity(event), targets(), {"FIRST": forecast(35), "JOINT": joint, "LOO": forecast()})
        panel.add_receipt(identity("d"), targets(), {"FIRST": forecast(35), "JOINT": forecast(count=1)})
        result = panel.finish()["groups"][0]["targets"]["carried"]
        own = result["all_eligible"]["JOINT"]
        self.assertEqual((own["eligible_receipts"], own["called_receipts"], own["abstained_receipts"]), (4, 3, 1))
        self.assertEqual(own["metrics"]["floor_absolute_error_cents"]["n"], 3)
        matched = result["matched_to_first"]["JOINT"]
        self.assertEqual((matched["n"], matched["strictly_closer"], matched["tied"]), (3, 2, 1))
        self.assertTrue(matched["qualifies"])
        self.assertFalse(matched["engine_authorship_enabled"])
        self.assertEqual(result["all_variant_matched"]["n"], 3)

    def test_no_receipt_inflation_of_filed_query_criterion(self):
        panel = self.scorer(groupings=(("category", "side", "gate"),))
        for receipt in ("1", "2", "3"):
            panel.add_receipt(identity("one_game", receipt=receipt), targets(),
                              {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()})
        matched = panel.finish()["groups"][0]["targets"]["carried"]["matched_to_first"]["JOINT"]
        self.assertTrue(matched["criterion_met_on_matched_receipts"])
        self.assertEqual(matched["distinct_matched_games"], 1)
        self.assertIsNone(matched["qualifies"])

    def test_target_and_metric_denominators_are_separate(self):
        panel = self.scorer(groupings=(("category",),))
        for event, truth in (("a", targets()), ("b", targets(reachable=None))):
            panel.add_receipt(identity(event), truth,
                              {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()})
        result = panel.finish()["groups"][0]["targets"]
        self.assertEqual(result["carried"]["matched_to_first"]["JOINT"]["n"], 2)
        reachable = result["reachable"]
        self.assertEqual(reachable["matched_to_first"]["JOINT"]["n"], 1)
        self.assertEqual(reachable["all_eligible"]["JOINT"]["metrics"]["reach.q50.brier"]["n"], 2)
        self.assertEqual(reachable["all_eligible"]["JOINT"]["target_missing_receipts"], 1)

    def test_main_chall_month_stream_remain_separate_and_inputs_immutable(self):
        panel = self.scorer(groupings=(("category", "month", "stream"),))
        data = {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()}
        original = copy.deepcopy(data)
        for category, month, stream in (("ATP_MAIN", "2026-05", "GATES"),
                ("ATP_MAIN", "2026-06", "GATES"), ("ATP_CHALL", "2026-06", "GATES"),
                ("ATP_MAIN", "2026-06", "ALL_RECEIPTS")):
            panel.add_receipt(identity(category+month, category=category, month=month, stream=stream), targets(), data)
        result = panel.finish()
        self.assertEqual(len(result["groups"]), 4)
        self.assertEqual(data, original)
        self.assertEqual(json.dumps(result, sort_keys=True, allow_nan=False),
                         json.dumps(panel.finish(), sort_keys=True, allow_nan=False))

    def test_duplicates_and_invalid_inputs_fail_before_partial_add(self):
        panel = self.scorer(groupings=(("category",),))
        bad = dict(values=[30], weights=[-1])
        with self.assertRaisesRegex(ValueError, "INVALID_WEIGHTS"):
            panel.add_receipt(identity("a"), targets(), {"FIRST": forecast(), "JOINT": bad})
        self.assertEqual(panel.finish()["seen_receipts"], 0)
        panel.add_receipt(identity("a"), targets(), {"FIRST": forecast()})
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RECEIPT"):
            panel.add_receipt(identity("a"), targets(), {"FIRST": forecast()})
        with self.assertRaisesRegex(ValueError, "CATEGORY_MUST_REMAIN_SEPARATE"):
            self.scorer(groupings=(("month",),))

    def test_r0_event_units_capture_and_missing_runs(self):
        panel = self.scorer()
        result = lambda done, one, capture: dict(rule="R0 CURRENT", completed=done, one_sided=one, captured_cents=capture)
        panel.add_conduct_event(identity("a"), {"FIRST": result(False, True, 0),
                                 "JOINT": result(True, False, 12), "LOO": result(False, False, 0)})
        panel.add_conduct_event(identity("b"), {"FIRST": result(False, False, 0), "JOINT": result(False, True, 0)})
        rows = panel.finish()["r0_conduct"]
        row = next(r for r in rows if r["group"] == dict(category="ATP_MAIN", stream="GATES"))
        joint = row["variants"]["JOINT"]
        self.assertEqual(joint["metrics"]["captured_cents"]["mean"], 6)
        self.assertEqual(joint["metrics"]["captured_cents_completed"]["mean"], 12)
        self.assertEqual(row["variants"]["LOO"]["missing_events"], 1)
        self.assertEqual(row["matched_to_first"]["JOINT"]["completed_delta"]["mean"], .5)
        with self.assertRaisesRegex(ValueError, "CAPTURE_REQUIRES_BOTH"):
            panel.add_conduct_event(identity("c"), {"FIRST": result(False, False, 2)})

    def test_bounded_identities_preserve_scores_and_reject_reappearing_games(self):
        regular = self.scorer(groupings=(("category",),))
        bounded = self.scorer(groupings=(("category",),), identity_mode="contiguous_event")
        for event in ("a", "b", "c"):
            for receipt in ("1", "2"):
                data = {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()}
                for scorer in (regular, bounded):
                    scorer.add_receipt(identity(event, receipt=receipt), targets(), data)
        self.assertEqual(regular.finish(), bounded.finish())
        self.assertEqual(len(regular.identities), 6)
        self.assertEqual(len(bounded.identities), 2)
        with self.assertRaisesRegex(ValueError, "NONCONTIGUOUS_EVENT"):
            bounded.add_receipt(identity("a", receipt="3"), targets(), {})
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RECEIPT"):
            bounded.add_receipt(identity("c", receipt="1"), targets(), {})
        self.assertEqual(bounded.finish()["seen_receipts"], 6)

    def test_common_metrics_can_be_omitted_without_changing_matched_count(self):
        scorer = self.scorer(groupings=(("category",),), common_variant_metrics=False)
        scorer.add_receipt(identity("a"), targets(),
                          {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()})
        result = scorer.finish()["groups"][0]["targets"]["carried"]
        self.assertEqual(result["all_variant_matched"], dict(n=1, metrics_enabled=False, variants={}))
        self.assertEqual(result["matched_to_first"]["JOINT"]["n"], 1)

    def test_bounded_stream_blocks_can_repeat_games_under_distinct_streams(self):
        scorer = self.scorer(groupings=(("category", "stream"),), identity_mode="contiguous_event")
        for stream in ("PRIMARY", "HOLDOUT"):
            for event in ("a", "b"):
                scorer.add_receipt(identity(event, stream=stream), targets(), {"FIRST": forecast()})
        self.assertEqual(scorer.finish()["seen_receipts"], 4)
        with self.assertRaisesRegex(ValueError, "NONCONTIGUOUS_EVENT"):
            scorer.add_receipt(identity("a", stream="PRIMARY", receipt="new"), targets(), {})

    def test_core_profile_preserves_required_metrics_exactly(self):
        full = self.scorer(groupings=(("category",),))
        core = self.scorer(groupings=(("category",),), metric_profile="core")
        for scorer in (full, core):
            scorer.add_receipt(identity("a"), targets(),
                              {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()})
        rows = [s.finish()["groups"][0]["targets"]["reachable"]["all_eligible"]["JOINT"]["metrics"]
                for s in (full, core)]
        for metric in ("floor_crps_cents", "floor_signed_error_cents", "floor_absolute_error_cents",
                       "floor_timing_absolute_error_minutes", "quantiles.q10.signed_error_cents",
                       "floor_band.q25_q75.coverage", "reach.support.brier", "reach.q50.brier", "family_accuracy"):
            self.assertEqual(rows[0][metric], rows[1][metric])
        self.assertLess(len(rows[1]), len(rows[0]))

    def test_exact_payload_identity_reuse_scores_once_without_merging_variants(self):
        cached = self.scorer(groupings=(("category",),), metric_profile="core")
        direct = self.scorer(groupings=(("category",),), metric_profile="core")
        shared = forecast(30)
        duplicate = {"FIRST": shared, "JOINT": shared, "LOO": forecast(35)}
        separate = {key: copy.deepcopy(value) for key, value in duplicate.items()}
        with patch("feature_panel_scoring.score_distribution", wraps=score_distribution) as counter:
            cached.add_receipt(identity("a"), targets(), duplicate)
            self.assertEqual(counter.call_count, 4)  # two distinct payloads, two truths
        direct.add_receipt(identity("a"), targets(), separate)
        self.assertEqual(cached.finish(), direct.finish())

    def test_only_allowlisted_filed_stream_can_publish_qualification(self):
        scorer = self.scorer(groupings=(("category", "side", "gate", "stream"),),
            authorization_streams=("PRIMARY_FILED_SCORABLE_GATES",))
        for stream in ("PRIMARY_GATES", "PRIMARY_FILED_SCORABLE_GATES"):
            for event in ("a", "b", "c"):
                scorer.add_receipt(identity(event, stream=stream), targets(),
                    {"FIRST": forecast(35), "JOINT": forecast(), "LOO": forecast()})
        for row in scorer.finish()["groups"]:
            matched = row["targets"]["carried"]["matched_to_first"]["JOINT"]
            if row["group"]["stream"] == "PRIMARY_GATES":
                self.assertIsNone(matched["qualifies"])
                self.assertFalse(matched["filed_side_gate_scope"])
            else:
                self.assertTrue(matched["qualifies"])

    def test_prepared_parent_application_is_byte_exact_to_legacy_arithmetic(self):
        encoded = lambda panel: json.dumps(panel.finish(), sort_keys=True, allow_nan=False).encode()
        for profile in ("full", "core"):
            for mode in ("all", "contiguous_event"):
                for common in (False, True):
                    options = dict(metric_profile=profile, identity_mode=mode,
                                   common_variant_metrics=common)
                    old, direct, worker, parent = [self.scorer(**options) for _ in range(4)]
                    jobs = []
                    for event in ("a", "b", "c"):
                        for index in range(6):
                            ident = identity(event, receipt=str(index), side="favorite" if index % 2 else "underdog")
                            truth = targets(level=29+index, reachable=None if index == 2 else 27+index)
                            if index == 3:
                                truth["carried"].update(floor_cents=None, floor_mtb=None, family="ABSENT")
                            shared = dict(values=[40., 20., np.nan, 30., 30.], weights=[3., 1., 7., 0., 2.],
                                          times=[5., 8., 2., np.nan, 7.], families=["A", "B", "A", "C", "B"])
                            forecasts = {"FIRST": shared, "JOINT": shared, "LOO": forecast(32+index)}
                            if index == 1:
                                forecasts["LOO"] = dict(ess=3, metrics_by_target={"carried": {
                                    "floor_signed_error_cents": .1, "floor_absolute_error_cents": .1}})
                            elif index == 2:
                                forecasts.pop("LOO")
                            elif index == 4:
                                forecasts["LOO"] = dict(forecast(), status="UNAVAILABLE_FEATURE_BLOCK")
                            jobs.append((ident, truth, forecasts, index != 5))
                    # Preparation can finish out of order and repeats no mutable
                    # scorer state; parent replay alone fixes accumulation order.
                    prepared = [None]*len(jobs)
                    for index in reversed(range(len(jobs))):
                        ident, truth, forecasts, eligible = jobs[index]
                        prepared[index] = pickle.loads(pickle.dumps(worker.prepare_receipt(
                            ident, truth, forecasts, eligible=eligible)))
                    self.assertEqual(worker.finish()["seen_receipts"], 0)
                    self.assertFalse(worker.identities)
                    for (ident, truth, forecasts, eligible), payload in zip(jobs, prepared):
                        legacy_add_receipt(old, ident, truth, forecasts, eligible=eligible)
                        direct.add_receipt(ident, truth, forecasts, eligible=eligible)
                        with patch("feature_panel_scoring.score_distribution", side_effect=AssertionError("parent rescored")):
                            parent.apply_prepared_receipt(payload)
                    self.assertEqual(encoded(old), encoded(direct))
                    self.assertEqual(encoded(old), encoded(parent))
                    self.assertEqual(old.identities, parent.identities)
                    self.assertEqual(old.completed_events, parent.completed_events)

    def test_prepared_payload_is_owned_immutable_and_pickle_preserves_aliases(self):
        worker = self.scorer()
        ident, truth, shared = identity("a"), targets(), forecast()
        expected_identity = dict(ident)
        with patch("feature_panel_scoring.score_distribution", wraps=score_distribution) as counter:
            prepared = worker.prepare_receipt(ident, truth, {"FIRST": shared, "JOINT": shared})
            self.assertEqual(counter.call_count, 4)
        ident["event_id"] = "changed"
        truth["carried"]["floor_cents"] = -100
        shared["values"][0] = -100
        self.assertEqual(prepared.identity, expected_identity)
        self.assertEqual(prepared.scored["carried"]["FIRST"]["metrics"]["floor_signed_error_cents"], 0)
        for payload in (prepared, pickle.loads(pickle.dumps(prepared))):
            self.assertIs(payload.scored["carried"]["FIRST"], payload.scored["carried"]["JOINT"])
            with self.assertRaises(FrozenInstanceError):
                payload.eligible = False
            with self.assertRaisesRegex(TypeError, "IMMUTABLE"):
                payload.identity["event_id"] = "mutated"
            with self.assertRaisesRegex(TypeError, "IMMUTABLE"):
                payload.scored["carried"]["FIRST"]["metrics"].update(floor_signed_error_cents=100)
            with self.assertRaisesRegex(TypeError, "IMMUTABLE"):
                payload.scored.clear()
            with self.assertRaisesRegex(TypeError, "IMMUTABLE"):
                payload.scored["carried"]["FIRST"]["quantiles"]["q50"].pop("level_cents")

    def test_prepared_guards_validate_before_parent_mutation(self):
        options = dict(identity_mode="contiguous_event")
        worker, parent = self.scorer(**options), self.scorer(**options)
        for eligible in (False, True):
            with self.assertRaisesRegex(ValueError, "UNREGISTERED_VARIANTS"):
                worker.prepare_receipt(identity("bad"), targets(), {"OTHER": forecast()}, eligible=eligible)
        with self.assertRaisesRegex(ValueError, "INVALID_WEIGHTS"):
            worker.prepare_receipt(identity("bad"), targets(), {"FIRST": dict(values=[1], weights=[-1])})
        with self.assertRaises(KeyError):
            worker.prepare_receipt({}, targets(), {})
        self.assertEqual(worker.finish()["seen_receipts"], 0)
        payload = worker.prepare_receipt(identity("a"), targets(), {"FIRST": forecast()})
        for invalid, message in (({}, "INVALID_PREPARED_RECEIPT"),
                (replace(payload, configuration=()), "CONFIGURATION_MISMATCH"),
                (replace(payload, scored={}), "MALFORMED_PREPARED_RECEIPT")):
            with self.assertRaisesRegex(ValueError, message):
                parent.apply_prepared_receipt(invalid)
            self.assertEqual(parent.finish()["seen_receipts"], 0)
        wrong_profile = self.scorer(**options, metric_profile="core")
        with self.assertRaisesRegex(ValueError, "CONFIGURATION_MISMATCH"):
            wrong_profile.apply_prepared_receipt(payload)
        parent.apply_prepared_receipt(payload)
        before = copy.deepcopy(parent.finish())
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RECEIPT"):
            parent.apply_prepared_receipt(payload)
        # Original serial guard order wins over an invalid forecast.
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RECEIPT"):
            parent.add_receipt(identity("a"), targets(), {"OTHER": forecast()})
        self.assertEqual(parent.finish(), before)
        parent.apply_prepared_receipt(worker.prepare_receipt(identity("b"), targets(), {}, eligible=False))
        before = copy.deepcopy(parent.finish())
        with self.assertRaisesRegex(ValueError, "NONCONTIGUOUS_EVENT"):
            parent.apply_prepared_receipt(worker.prepare_receipt(identity("a", receipt="new"), targets(), {}))
        self.assertEqual(parent.finish(), before)


if __name__ == "__main__":
    unittest.main()
