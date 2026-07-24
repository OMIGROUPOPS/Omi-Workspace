#!/usr/bin/env python3
"""Tests for the mechanically bound corrected Window-1 replay."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_corrected_replay as corrected  # noqa: E402


class CorrectedReplayTests(unittest.TestCase):
    def setUp(self):
        self.start = {
            "event_id": "E",
            "precision_class": "exact_official_or_milestone",
            "exact_start_utc": 200.0,
            "interval_contradiction": False,
            "interval_utc": {
                "lower_exclusive": None,
                "upper_inclusive": 200.0,
            },
            "selected_source": "official",
            "timestamp_basis": "exchange",
        }
        self.base = {
            "event_id": "E",
            "event_date": "2026-07-12",
            "category": "ITF_M",
            "ticker": "T",
            "replayed_status": "exact_filled_five",
            "official_fill_vwap_cents": 60.0,
            "causal_nonplacement_receipt_count": 0,
            "possible_exact_five_upper_bound": True,
        }
        self.lifecycle = {
            "event_id": "E",
            "ticker": "T",
            "lineage": "L",
            "status": "exact_filled_five",
            "accepted_order_ids": ["O"],
            "official_fill_ids": ["F"],
            "cancellation_evidence": {},
            "first_fill_exchange_ts": 150.0,
        }
        self.indexes = {
            "order_by_id": {
                "O": {
                    "accepted": True,
                    "event_id": "E",
                    "ticker": "T",
                    "order_id": "O",
                    "trade_id": "L",
                    "exchange_created_ts": 100.0,
                    "local_logged_ts": 99.0,
                    "price_cents": 60,
                    "quantity": 5,
                    "window_receipt": {
                        "phase": "W1",
                    },
                }
            },
            "failed_by_key": {},
            "fill_by_id": {
                "F": {
                    "fill_id": "F",
                    "order_id": "O",
                    "ticker": "T",
                    "action": "buy",
                    "quantity": 5.0,
                    "price_cents": 60.0,
                    "exchange_ts": 150.0,
                }
            },
            "lifecycle_by_ticker": {
                "T": [self.lifecycle],
            },
            "decisions_by_ticker": {},
        }
        self.reference = {
            "reference_cents": 70,
            "reference_exchange_ts": 190.0,
            "reference_trade_id_retained": False,
            "reference_identity_source": "exchange_trade_id",
            "observed_min_cents_through_cutoff": 55,
        }

    def build(self):
        return corrected.build_leg_receipt_detail(
            self.base,
            self.start,
            [self.lifecycle],
            self.indexes,
            self.reference,
            None,
            {"ITF_M": {"70": {"edge_p50": 8}}},
        )[0]

    def test_exact_clocked_fill_is_positive_and_measured(self):
        row = self.build()
        self.assertTrue(row["proven_window1_exact_five"])
        self.assertEqual(-10.0, row["individual_leg_delta_cents"])
        self.assertEqual(
            -2.0, row["dynamic_floor_leg"]["dip_catch_gap_cents"]
        )
        self.assertTrue(
            row["dynamic_floor_leg"]["at_or_below_fitted_target"]
        )

    def test_missing_exchange_placement_clock_censors_positive(self):
        self.indexes["order_by_id"]["O"]["exchange_created_ts"] = None
        row = self.build()
        self.assertFalse(row["proven_window1_exact_five"])
        self.assertIsNone(row["individual_leg_delta_cents"])
        self.assertIn(
            "filled_order_missing_exchange_placement_clock",
            row["placement_fill_causality"]["issues"],
        )

    def test_fill_after_causal_boundary_is_proven_non_window1(self):
        self.indexes["fill_by_id"]["F"]["exchange_ts"] = 210.0
        row = self.build()
        self.assertFalse(row["proven_window1_exact_five"])
        self.assertTrue(row["proven_non_window1_fill"])

    def test_ten_contract_overfill_never_counts_exact_five(self):
        self.base["replayed_status"] = "exact_filled_other_quantity"
        self.base["official_fill_vwap_cents"] = 60.0
        self.indexes["fill_by_id"]["F"]["quantity"] = 10.0
        row = self.build()
        self.assertTrue(row["ten_contract_overfill"])
        self.assertFalse(row["exact_five_quantity"])
        self.assertFalse(row["proven_window1_exact_five"])

    def test_schedule_only_never_proves_positive_or_negative(self):
        proof = corrected.start_proof({
            "precision_class": "schedule_only_bound",
            "exact_start_utc": None,
            "interval_contradiction": False,
            "interval_utc": {
                "lower_exclusive": None,
                "upper_inclusive": None,
            },
            "selected_source": "schedule_plus_declared_corridor",
            "timestamp_basis": "schedule",
        })
        self.assertFalse(proof["positive_window1_capable"])
        self.assertIsNone(proof["safe_prestart_cutoff_exchange_ts"])
        self.assertIsNone(proof["known_live_by_exchange_ts"])
        self.assertFalse(proof["schedule_used_for_classification"])

    def test_contradictory_interval_cannot_prove_positive(self):
        proof = corrected.start_proof({
            "precision_class": "causal_start_interval",
            "exact_start_utc": None,
            "interval_contradiction": True,
            "interval_utc": {
                "lower_exclusive": 300.0,
                "upper_inclusive": 200.0,
            },
            "selected_source": "tape",
            "timestamp_basis": "exchange",
        })
        self.assertFalse(proof["positive_window1_capable"])
        self.assertIsNone(proof["safe_prestart_cutoff_exchange_ts"])
        self.assertEqual(200.0, proof["known_live_by_exchange_ts"])

    def test_local_live_by_receipt_cannot_prove_post_start(self):
        proof = corrected.start_proof({
            "start_state": "bounded_live_by_timestamp",
            "verified_start_utc": None,
            "interval_contradiction": False,
            "start_interval_utc": {
                "lower_exclusive": None,
                "upper_inclusive": 200.0,
            },
            "known_live_by_utc": 200.0,
            "known_live_by_source": "engine_regime_transition",
            "known_live_by_time_basis": "local_engine_receipt_utc",
            "selected_source": "engine_regime_transition",
        })
        self.assertFalse(
            proof["known_live_by_usable_for_post_start_ruling"]
        )

    def test_policy_binding_refuses_proxy_and_unknown_component(self):
        candidate = {
            "policy": {
                "policy_id": "park_touch_simultaneous_hold",
                "simplified_proxy_allowed": False,
            },
            "aim_v2": {
                "status": "excluded",
                "shape_prior_consumed": False,
            },
        }
        allowlist = {
            "allowed_policy_ids": ["park_touch_simultaneous_hold"],
            "forbidden_policy_ids": [],
            "allowed_execution_components": ["pair_law"],
            "forbidden_execution_components": ["aim_v2"],
            "prohibited_input_sha256": [],
        }
        adapter = {
            "adapter_id": "chronological-window1-os-receipt-adapter-v1",
            "laws": {
                "silent_proxy_substitution_allowed": False,
            },
            "metric_executable_components": ["pair_law"],
            "feature_coverage_components": [],
        }
        with self.assertRaises(corrected.ReplayError):
            corrected.bind_policy(candidate, allowlist, adapter)
        candidate["policy"]["policy_id"] = "actual"
        allowlist["allowed_policy_ids"] = ["actual"]
        adapter["feature_coverage_components"] = ["unknown"]
        with self.assertRaises(corrected.ReplayError):
            corrected.bind_policy(candidate, allowlist, adapter)

    def test_committed_binding_excludes_aim_prior(self):
        candidate = corrected.read_json(
            REPO / "arb-executor" / "docs" / "research" / "window1"
            / "WINDOW1_CORRECTED_CANDIDATE.json"
        )
        allowlist = corrected.read_json(
            REPO / "arb-executor" / "docs" / "research" / "window1"
            / "WINDOW1_POLICY_ALLOWLIST.json"
        )
        adapter = corrected.read_json(
            REPO / "arb-executor" / "docs" / "research" / "window1"
            / "WINDOW1_OS_EXECUTION_ADAPTER.json"
        )
        corrected.bind_policy(candidate, allowlist, adapter)
        self.assertFalse(candidate["aim_v2"]["shape_prior_consumed"])
        self.assertEqual("excluded", candidate["aim_v2"]["status"])

    def test_committed_start_decomposition_and_positive_clock_basis(self):
        starts = corrected.read_jsonl(
            REPO / ".claude" / "window1_20260721"
            / "REAL_START_LEDGER.jsonl"
        )
        self.assertEqual(
            corrected.EXPECTED_START_DECOMPOSITION,
            corrected.start_decomposition(starts),
        )
        positive = [
            corrected.start_proof(row) for row in starts
            if corrected.start_proof(row)["positive_window1_capable"]
        ]
        self.assertEqual(76, len(positive))
        self.assertTrue(all(
            row["safe_prestart_cutoff_timestamp_basis"]
            == "official_provider_start_timestamp"
            for row in positive
        ))


if __name__ == "__main__":
    unittest.main()
