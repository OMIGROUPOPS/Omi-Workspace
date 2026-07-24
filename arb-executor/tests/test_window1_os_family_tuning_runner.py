#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_os_family_tuning_runner as runner  # noqa: E402


DOCS = REPO / "arb-executor" / "docs" / "research" / "window1"


class OSFamilyTuningPreflightTests(unittest.TestCase):
    def contracts(self):
        return (
            runner.read_json(
                DOCS / "WINDOW1_OS_FAMILY_CANDIDATES_V1.json"
            ),
            runner.read_json(
                DOCS / "WINDOW1_OS_FAMILY_ADAPTER_V1.json"
            ),
            runner.read_json(
                DOCS / "WINDOW1_OS_FAMILY_FEATURE_ALLOWLIST_V1.json"
            ),
            runner.read_json(
                DOCS / "WINDOW1_OS_FAMILY_METRIC_CONTRACT_V1.json"
            ),
            runner.read_json(
                DOCS
                / "WINDOW1_OS_FAMILY_PROSPECTIVE_HOLDOUT_V1.json"
            ),
        )

    def test_contracts_bind_24_exact_policy_ids(self):
        result = runner.validate_contracts(*self.contracts())
        self.assertEqual(24, result["policy_count"])
        self.assertEqual(6, result["family_count"])
        self.assertEqual(
            [],
            self.contracts()[0]["parameter_ranges"][
                "free_numeric_parameters"
            ],
        )
        self.assertFalse(
            result["silent_proxy_substitution_allowed"]
        )
        self.assertTrue(result["aim_v2_excluded"])

    def test_unknown_policy_is_refused(self):
        spec, adapter, features, metric, holdout = self.contracts()
        spec["permitted_policy_ids"].append("proxy")
        with self.assertRaises(runner.TuningPreflightError):
            runner.validate_contracts(
                spec, adapter, features, metric, holdout
            )

    def test_missing_feature_censors_only_feature(self):
        spec, adapter, features, metric, holdout = self.contracts()
        self.assertFalse(spec["missing_feature_censors_entire_event"])
        self.assertEqual(
            "disable_feature_only",
            adapter["laws"]["missing_feature"],
        )
        self.assertIn(
            "disable the named feature",
            features["missing_feature_law"],
        )
        runner.validate_contracts(
            spec, adapter, features, metric, holdout
        )

    def test_start_gate_fails_before_scoring_below_603(self):
        with self.assertRaises(runner.StartGateFailed):
            runner.enforce_start_gate({
                "D": 804,
                "provable_positive_population": 265,
                "start_gate_pass": False,
            })

    def test_start_gate_passes_at_603(self):
        receipt = runner.enforce_start_gate({
            "D": 804,
            "provable_positive_population": 603,
            "start_gate_pass": True,
        })
        self.assertTrue(receipt["pass"])


if __name__ == "__main__":
    unittest.main()
