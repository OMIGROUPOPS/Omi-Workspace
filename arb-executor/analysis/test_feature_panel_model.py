"""Tests for isolated feature-panel likelihood; no real data or engine import."""
import unittest

import numpy as np

import feature_panel_model as model


class FeaturePanelModelTests(unittest.TestCase):
    def test_rank_ties_and_missing(self):
        scale = model.EmpiricalRankScale.fit([1, 2, 2, 3, None, float("nan")])
        self.assertEqual(scale.rank(2), .5)
        self.assertEqual(scale.rank(0), 0)
        self.assertEqual(scale.rank(4), 1)
        self.assertIsNone(scale.rank(None))
        self.assertIsNone(model.EmpiricalRankScale.fit([]).rank(3))

    def test_feature_blocks_missing_are_neutral_and_reported(self):
        features = [model.FeatureSpec("flow", "numeric"), model.FeatureSpec("source", "categorical")]
        scales = model.fit_rank_scales([{"flow": 1}, {"flow": 2}, {"flow": 3}], features)
        result = model.block_likelihoods({"flow": 2, "source": "a"},
            [{"flow": 2, "source": "a"}, {"flow": 3}, {"source": "b"}, {}],
            {"block": features}, scales)
        np.testing.assert_array_equal(result["comparable_feature_counts"].ravel(), [2, 1, 1, 0])
        np.testing.assert_allclose(result["support_fraction"].ravel(), [1, .5, .5, 0])
        np.testing.assert_allclose(result["block_log_k"].ravel(), [0, -np.log1p(1/3), -np.log(2), 0])
        self.assertEqual(result["member_count"], 4)

    def test_duplicate_feature_rejected(self):
        feature = model.FeatureSpec("x", "categorical")
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            model.block_likelihoods({"x": "a"}, [{"x": "a"}], {"b": [feature, feature]}, {})

    def test_zero_beta_is_bit_identical_first(self):
        base = np.array([.1, .3, 0, np.nextafter(.5, 1)])
        result = model.joint_weights(base, np.array([[-1, -2], [-3, -4], [-5, -6], [0, -8]]), [0, 0])
        self.assertEqual(result.tobytes(), base.tobytes())
        self.assertFalse(np.shares_memory(result, base))

    def test_crps_tied_atoms_against_pairwise_definition(self):
        levels = np.array([2, 2, 5, 8.])
        base = np.array([1, 3, 2, 4.])
        logs = np.array([[-.1, -.9], [-.2, -.3], [-.7, -.1], [-.8, -.6]])
        beta = np.array([.3, .7])
        score, _ = model.crps_and_gradient(levels, base, logs, 4., beta)
        p = model.joint_weights(base, logs, beta)
        p /= p.sum()
        expected = p @ abs(levels-4) - np.sum(p[:, None]*p[None, :]*abs(levels[:, None]-levels[None, :]))/2
        self.assertAlmostEqual(score, expected, places=13)

    def test_analytic_gradient(self):
        levels = np.array([2, 2, 5, 8.])
        base = np.array([1, 3, 2, 4.])
        logs = np.array([[-.1, -.9], [-.2, -.3], [-.7, -.1], [-.8, -.6]])
        beta = np.array([.3, .7])
        _, gradient = model.crps_and_gradient(levels, base, logs, 4., beta)
        h = 1e-5  # finite-difference test tolerance, not a model parameter
        differences = []
        for column in range(len(beta)):
            plus, minus = beta.copy(), beta.copy()
            plus[column] += h
            minus[column] -= h
            a = model.crps_and_gradient(levels, base, logs, 4., plus)[0]
            b = model.crps_and_gradient(levels, base, logs, 4., minus)[0]
            differences.append((a-b)/(2*h))
        np.testing.assert_allclose(gradient, differences, rtol=1e-7, atol=1e-9)

    def test_temporal_filter_excludes_future_self_day_and_heldout(self):
        query = dict(event_id="query", category="cat", date="2026-07-02", formation=100.)
        records = [dict(event_id="earlier", category="cat", date="2026-05-10", bell=10., x=2.),
                   dict(event_id="heldout", category="cat", date="2026-06-10", bell=20., x=999.),
                   dict(event_id="future", category="cat", date="2026-07-03", bell=110., x=-999.),
                   dict(event_id="query", category="cat", date="2026-07-02", bell=5., x=9999.),
                   dict(event_id="same-day", category="cat", date="2026-07-02", bell=50., x=9999.),
                   dict(event_id="other", category="other", date="2026-05-02", bell=1., x=9999.)]
        selected, exclusions = model.select_training_records(records, query, heldout_months=["2026-06"])
        self.assertEqual([r["event_id"] for r in selected], ["earlier"])
        self.assertEqual(sum(exclusions.values()), 5)
        scale = model.fit_rank_scales(selected, [model.FeatureSpec("x", "numeric")])["x"]
        self.assertEqual(scale.sorted_values.tolist(), [2.])
        # Mutating query-future/held-out values cannot change learned ranks.
        for row in records[1:]:
            row["x"] = -1e200
        again, _ = model.select_training_records(records, query, heldout_months=["2026-06"])
        changed = model.fit_rank_scales(again, [model.FeatureSpec("x", "numeric")])["x"]
        np.testing.assert_array_equal(scale.sorted_values, changed.sorted_values)

    def test_fit_improves_crps_and_is_deterministic(self):
        samples = [dict(candidate_levels=[0., 1.], base_weights=[1., 1.],
                        block_log_k=[[0.], [-1.]], actual=0., gameid="earlier")]
        fitted = model.fit_joint_model(samples, ["flow"])
        again = model.fit_joint_model(samples, ["flow"])
        self.assertEqual(fitted.report, again.report)
        self.assertGreater(fitted.beta[0], 0)
        self.assertLess(fitted.report["fitted_crps"], fitted.report["first_crps"])
        self.assertFalse(fitted.report["global_optimum_claimed"])

    def test_game_weighting_not_receipt_count_weighting(self):
        sample = dict(candidate_levels=[0., 1.], base_weights=[1., 1.], block_log_k=[[0.], [-1.]])
        a = dict(sample, actual=0., gameid="a")
        b = dict(sample, actual=1., gameid="b")
        balanced = model.fit_joint_model([a, b], ["flow"])
        duplicated = model.fit_joint_model([a, a, a, b], ["flow"])
        np.testing.assert_array_equal(balanced.beta, duplicated.beta)
        self.assertEqual(balanced.report["fitted_crps"], duplicated.report["fitted_crps"])

    def test_untrained_returns_first(self):
        fitted = model.fit_joint_model([], ["flow"])
        self.assertEqual(fitted.report["status"], "UNTRAINED_FIRST_CONTROL")
        base = np.array([.3, .7])
        self.assertEqual(fitted.predict(base, [[-1.], [-2.]])["weights"].tobytes(), base.tobytes())

    def test_validation_preserves_equal_game_normalization(self):
        sample = dict(candidate_levels=[0., 1.], base_weights=[1., 1.], block_log_k=[[0.], [-1.]])
        a = dict(sample, actual=0., gameid="a")
        b = dict(sample, actual=3., gameid="b")
        once = model.evaluate_joint_model([a, b], [.2])
        repeated = model.evaluate_joint_model([a, a, a, b], [.2])
        self.assertEqual(once["crps"], repeated["crps"])
        self.assertEqual(once["per_game_crps"], repeated["per_game_crps"])

    def test_unused_future_fields_cannot_change_likelihood(self):
        query, member = {"x": 2., "future": 99.}, {"x": 3., "future": -99.}
        specs = [model.FeatureSpec("x", "numeric")]
        scales = model.fit_rank_scales([{"x": 1.}, {"x": 2.}, {"x": 3.}], specs)
        before = model.block_likelihoods(query, [member], {"x": specs}, scales)["block_log_k"]
        query["future"], member["future"] = -1e200, 1e200
        after = model.block_likelihoods(query, [member], {"x": specs}, scales)["block_log_k"]
        np.testing.assert_array_equal(before, after)

    def test_missing_neutral_allows_all_original_members(self):
        base = np.array([1., 2., 3.])
        result = model.joint_weights(base, np.zeros((3, 2)), [4., 9.])
        np.testing.assert_allclose(result/result.sum(), base/base.sum())
        self.assertEqual(np.count_nonzero(result), len(base))


if __name__ == "__main__":
    unittest.main()
