"""Clock/lineage tests; fixtures are not model constants or population data."""
import unittest
import copy
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import feature_panel as f
import tune_bench_v2_survivorship as b


def panel_fixture():
    epochs = np.array([0., 59., 60., 119., 120., 179., 240.])
    legs, metadata, sources, witnesses = [], {}, {}, {}
    for name, last in (("F", [60, 59, 58, 59, 58, 61, 62]), ("D", [40, 41, 42, 41, 42, 39, 38])):
        last = np.asarray(last, dtype=float)
        leg = b.Leg(name, last[0], 0, 300, epochs.copy(), np.column_stack((last, last-1, last+1)),
            np.arange(len(epochs), dtype=float), epochs.copy(), np.minimum.accumulate(last), None,
            postformation_open=last[0], count_epoch=epochs.copy(), print_count_cum=np.arange(len(epochs))+1)
        legs.append(leg)
        ticker = "fixture-"+name
        metadata[ticker] = dict(formation_source="FIRST_BOTH_SIDES_TRADE", bell_source="scheduled", cadence_s=999)
        sources[ticker] = dict(first_two_sided_book_epoch=10, first_source_book_was_two_sided=True,
            clock_provenance=dict(bell_publication_epoch=5), book_observation_epochs=[10, 59, 120, 200],
            books=[dict(available_epoch=t, bid_depth_5=bid, ask_depth_5=ask) for t, bid, ask in
                   ((10, 6, 4), (120, 0, 0), (200, 3, 7))],
            minute_features=[dict(available_epoch=t, taker_flow_contracts=flow, taker_yes_contracts=abs(flow),
                taker_no_contracts=0, distinct_print_prices=2, intertrade_gap_std_seconds=3)
                for t, flow in ((60, 2), (120, -3), (180, 1))],
            oi_columns=["available_epoch", "open_interest_at_minute_end", "open_interest_ffill", "open_interest_delta_from_prior_minute"],
            oi=[[60, 12, 12, None], [120, 13, 13, 1]], odds_poll_epochs=[20, 250])
        witnesses[ticker] = dict(formation_end_epoch=0, prints=[[10, 50, 1, 1], [20, 49, 2, 2],
            [59, 48, 1, 3], [61, 47, 0, 4], [150, 46, 1, 5]])
    pair = b.Pair("fixture", "ATP_MAIN", "2026-05-01", tuple(legs), 10, "TICK")
    contract = dict(minute_seconds=60, gates_minutes_to_bell=[4, 2, 1])
    return pair, metadata, sources, witnesses, contract


class CausalPanelTests(unittest.TestCase):
    def test_asof_future_append_cannot_change_prefix(self):
        expected = f.asof([10, 20], [1, 2], [0, 10, 19, 20])
        actual = f.asof([10, 20, 30], [1, 2, -999], [0, 10, 19, 20])
        np.testing.assert_equal(expected, actual)
        self.assertTrue(np.isnan(actual[0]))

    def test_minute_boundary_excludes_boundary_tick(self):
        leg = SimpleNamespace(formation=0, epoch=np.array([0, 59, 60, 119, 120]),
                              values=np.array([[1, 2, 3], [2, 4, 6], [90, 90, 90],
                                               [4, 8, 12], [99, 99, 99]], dtype=float))
        result = f.completed_closes(leg, [120, 121, 179], 60)
        np.testing.assert_array_equal(result, [[2, 4, 6]]*3)

    def test_prefix_cadence_does_not_use_future_print(self):
        tape = [[10, 50, 1, 1], [20, 49, 1, 2], [59, 48, 1, 3], [61, 47, 0, 4]]
        before = f.prefix_print_features(tape, [9, 10, 20, 60], 0, 60)
        after = f.prefix_print_features(tape+[[500, 1, 100, 5]], [9, 10, 20, 60], 0, 60)
        for x, y in zip(before, after):
            np.testing.assert_equal(x, y)
        self.assertTrue(np.isnan(before[0][1]))
        self.assertEqual(before[0][2], 10)
        self.assertEqual(before[1][-1], 1)
        self.assertEqual(before[2][-1], 1)

    def test_missing_source_is_missing_not_zero(self):
        self.assertTrue(np.isnan(f.source_column([], "x", [1, 2])).all())
        np.testing.assert_equal(f.source_column([dict(available_epoch=2, x=None)], "x", [1, 2]), [np.nan,np.nan])

    def test_registry_accounts_for_all_requested_groups(self):
        self.assertEqual(set(f.BLOCKS), {x.block for x in f.FIELDS if x.block})
        self.assertEqual(len(f.FIELD_NAMES), len(set(f.FIELD_NAMES)))
        self.assertNotIn("cadence_class", f.MODEL_FIELDS)
        self.assertNotIn("spread_band", f.MODEL_FIELDS)
        self.assertNotIn("ws_depth_available", f.MODEL_FIELDS)
        self.assertNotIn("odds_available", f.MODEL_FIELDS)
        self.assertNotIn("cadence_s", f.MODEL_FIELDS)

    def test_supplemental_is_not_silently_dropped(self):
        sources = {"x": dict(oi_columns=["available_epoch", "open_interest_at_minute_end", "open_interest_ffill", "open_interest_delta_from_prior_minute"],
                             oi=[[60, 12, 12, None], [120, 13, 13, 1]], odds_poll_epochs=[70])}
        f.prepare_sources(sources, {})
        np.testing.assert_equal(f.source_column(sources["x"]["open_interest"], "open_interest", [59,60,120]), [np.nan,12,13])
        np.testing.assert_array_equal(sources["x"]["odds_snapshot_epochs"], [70])

    def test_empty_book_depth_sentinel_is_missing(self):
        sources = {"x": dict(books=[dict(available_epoch=1, bid_depth_5=0, ask_depth_5=0, depth_ratio=.5),
                                         dict(available_epoch=2, bid_depth_5=6, ask_depth_5=4, depth_ratio=.6)])}
        f.prepare_sources(sources, {})
        np.testing.assert_equal(f.source_column(sources["x"]["books"], "depth_ratio", [1,2]), [np.nan,.6])

    def test_spread_bands_reuse_filed_helper_and_preserve_missing(self):
        codes, labels = f.filed_spread_bands([40,40,40,41,np.nan], [41,44,48,40,42], 100)
        self.assertEqual(tuple(labels), ("tight", "medium", "wide"))
        np.testing.assert_equal(codes, [0,1,2,np.nan,np.nan])

    def test_unextracted_odds_are_unknown_not_zero(self):
        source = {"x": dict(odds_poll_epochs=[], odds_status="NOT_EXTRACTED")}
        f.prepare_sources(source, {})
        self.assertIsNone(source["x"]["odds_snapshot_epochs"])

    def test_missing_witness_payload_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "MISSING_POSITIVE_PRINT_WITNESS_PAYLOAD"):
            f.prepare_sources({}, {"x": dict(ticker="x", formation_end_epoch=0)})

    def test_positive_minute_endpoint_cache_is_exact_and_reused(self):
        rows = [[10, 50, 1, 1], [20, 49, 1, 2], [59, 48, 1, 3], [61, 47, 0, 4], [121, 46, 1, 5]]
        prepared = f.prepare_print_prefix(rows, 0)
        endpoints = f.positive_minute_endpoints(prepared, 60)
        np.testing.assert_array_equal(endpoints, [60, 180])
        expected = f.prefix_print_features(rows, [9, 10, 20, 60, 180], 0, 60)
        with patch.object(f.np, "unique", side_effect=AssertionError("cached endpoint index rebuilt")):
            actual = f.prefix_print_features(rows, [9, 10, 20, 60, 180], 0, 60, prepared)
        for x, y in zip(expected, actual):
            np.testing.assert_equal(x, y)
        self.assertIs(f.positive_minute_endpoints(prepared, 60), endpoints)
        np.testing.assert_array_equal(f.positive_minute_endpoints(prepared, 120), [120, 240])

    def test_source_array_caches_are_prepared_once(self):
        _, _, sources, witnesses, contract = panel_fixture()
        f.prepare_sources(sources, witnesses, minute_seconds=contract["minute_seconds"])
        book = sources["fixture-F"]["book_observation_epochs"]
        odds = sources["fixture-F"]["odds_snapshot_epochs"]
        minute = witnesses["fixture-F"]["_prefix"]["positive_minute_endpoints_by_seconds"][60]
        f.prepare_sources(sources, witnesses, minute_seconds=contract["minute_seconds"])
        self.assertIs(sources["fixture-F"]["book_observation_epochs"], book)
        self.assertIs(sources["fixture-F"]["odds_snapshot_epochs"], odds)
        self.assertIs(witnesses["fixture-F"]["_prefix"]["positive_minute_endpoints_by_seconds"][60], minute)

    def test_values_only_matches_full_before_and_after_prepare(self):
        pair, metadata, sources, witnesses, contract = panel_fixture()
        codebooks = f.categorical_codes(metadata)
        gates = np.array([5., 4., 3., 2., 1.])
        # The source conversion was already part of the original production path.
        f.prepare_sources(sources, witnesses, minute_seconds=contract["minute_seconds"])
        full = f.build_pair_panel(pair, metadata, sources, witnesses, contract, 100, codebooks,
            evaluation_gates=gates)
        with patch.object(f, "filed_spread_bands", side_effect=AssertionError("unused diagnostics computed")):
            values = f.build_pair_panel(pair, metadata, sources, witnesses, contract, 100, codebooks,
                evaluation_gates=gates, values_only=True)
        np.testing.assert_equal(values, full["values"])
        self.assertTrue(np.isnan(values[0]).all())  # Before both first prints.
        self.assertTrue(np.isnan(values[:, :, f.FEATURE_INDEX["depth_ratio"]]).any())

    def test_cached_values_only_future_sentinel_invariance(self):
        pair, metadata, sources, witnesses, contract = panel_fixture()
        changed_sources, changed_witnesses = copy.deepcopy(sources), copy.deepcopy(witnesses)
        for source in changed_sources.values():
            source["books"].append(dict(available_epoch=260, bid_depth_5=999, ask_depth_5=1))
            source["minute_features"].append(dict(available_epoch=260, taker_flow_contracts=999))
            source["book_observation_epochs"].append(260)
            source["odds_poll_epochs"].append(260)
        for witness in changed_witnesses.values():
            witness["prints"].append([260, 1, 999, 99])
        codebooks = f.categorical_codes(metadata)
        f.prepare_sources(sources, witnesses, minute_seconds=contract["minute_seconds"])
        f.prepare_sources(changed_sources, changed_witnesses, minute_seconds=contract["minute_seconds"])
        before = f.build_pair_panel(pair, metadata, sources, witnesses, contract, 100, codebooks,
            evaluation_gates=[4., 3., 2., 1.], values_only=True)
        after = f.build_pair_panel(pair, metadata, changed_sources, changed_witnesses, contract, 100, codebooks,
            evaluation_gates=[4., 3., 2., 1.], values_only=True)
        np.testing.assert_equal(before, after)


if __name__ == "__main__":
    unittest.main()
