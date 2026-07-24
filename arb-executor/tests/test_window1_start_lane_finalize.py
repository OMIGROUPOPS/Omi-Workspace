#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_start_lane_finalize as finalizer  # noqa: E402


class StartLaneFinalizeTests(unittest.TestCase):
    def test_gate_failed_result_never_claims_strategy_verdict(self):
        result = finalizer.assemble(
            {
                "D": 804,
                "exact_starts": 234,
                "clean_intervals": 31,
                "live_by_only": 450,
                "contradictory": 26,
                "schedule_only": 63,
                "unresolved": 0,
                "provable_positive_population": 265,
                "missing_from_start_gate": 338,
                "start_gate_pass": False,
                "ledger_sha256": "start",
                "evidence_blocker": {},
            },
            {
                "D": 804,
                "historical_dual_exact_five_events": 31,
                "historical_dual_events_with_receipt_proven_post_start_leg": 26,
                "permanently_post_start_filled_legs": 108,
                "permanently_post_start_fill_events": 95,
                "newly_recovered_historical_strict_window1_duals": 0,
                "ten_contract_overfill_outside_exact_five": 1,
                "ruling_counts": {},
            },
            {
                "D": 804,
                "published_optimistic_upper_bound": 240,
                "corrected_receipts_only_optimistic_upper_bound": 226,
                "corrected_rate_over_D": 226 / 804,
                "distance_from_75_percent_target": 377,
                "strict_lower_bound": 0,
            },
            {
                "contract_validation": "pass",
                "family_count": 6,
                "policy_count": 24,
                "aim_v2_excluded": True,
                "candidate_scoring_performed": False,
                "candidate_results_opened": False,
                "stop_reason": "start_gate_below_603",
                "start_gate": {"pass": False},
                "freeze": {
                    "candidate_spec_hash": "candidate",
                    "policy_allowlist_hash": "policies",
                    "parameter_ranges_hash": "ranges",
                    "fixed_parameter_surface_hashes": {},
                    "adapter_hash": "adapter",
                    "causal_feature_allowlist_hash": "features",
                    "fill_kernel_hash": "kernel",
                    "metric_contract_hash": "metric",
                    "prospective_holdout_declaration_hash": "holdout",
                    "code_commit": "commit",
                },
            },
        )
        self.assertFalse(
            result["verdict_law"]["strategy_75_percent_verdict_issued"]
        )
        self.assertFalse(
            result["development_candidate_preflight"][
                "candidate_scoring_performed"
            ]
        )


if __name__ == "__main__":
    unittest.main()
