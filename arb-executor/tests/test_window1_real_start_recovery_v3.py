#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_real_start_recovery_v3 as recovery  # noqa: E402
import window1_start_replay_adjudication as adjudication  # noqa: E402


class RealStartRecoveryV3Tests(unittest.TestCase):
    def test_legacy_self_fill_start_candidate_is_excluded(self):
        rows = recovery.legacy_candidates({
            "candidate_evidence": [{
                "source": "engine_regime_transition:self_fill",
                "timestamp": "2026-07-12T12:00:00+00:00",
                "bound_direction": "live_by",
                "timestamp_basis": "local_engine_receipt_utc",
            }]
        })
        self.assertEqual([], rows)

    def event(self):
        return {
            "event_id": "E",
            "event_date": "2026-07-12",
            "category": "ATP_MAIN",
            "scheduled_start_exchange_ts": "2026-07-12T12:00:00Z",
            "schedule_source": "catalog",
            "legs": [
                {"leg": "A", "ticker": "E-A"},
                {"leg": "B", "ticker": "E-B"},
            ],
        }

    def test_stale_historical_live_row_is_exact_not_freshness_rejected(self):
        row = recovery.candidate(
            source="official_provider_match_start",
            timestamp=recovery.parse_ts("2026-07-12T10:00:00Z"),
            direction="exact",
            basis="official_provider_start_timestamp",
            precision="second",
            evidence={
                "status": "live",
                "historical_freshness_rule_applied": False,
            },
        )
        selected = recovery.select_event(self.event(), [row])
        self.assertEqual("exact", selected["precision_class"])
        self.assertTrue(selected["positive_window1_provable"])
        self.assertFalse(selected["schedule_can_prove_positive"])

    def test_live_by_never_becomes_exact(self):
        row = recovery.candidate(
            source="public_tape_5_prints_in_15m_onset",
            timestamp=recovery.parse_ts("2026-07-12T10:00:00Z"),
            direction="live_by",
            basis="public_trade_exchange_created_time",
            precision="second",
            evidence={},
        )
        selected = recovery.select_event(self.event(), [row])
        self.assertEqual("live_by_only", selected["precision_class"])
        self.assertFalse(selected["positive_window1_provable"])
        self.assertIsNone(selected["exact_start_utc"])

    def test_clean_interval_and_contradiction_remain_distinct(self):
        lower = recovery.candidate(
            source="milestone_shadow_not_started_observation",
            timestamp=100.0,
            direction="not_live_through",
            basis="local_shadow_receipt_utc",
            precision="subsecond",
            evidence={},
        )
        upper = recovery.candidate(
            source="public_tape_5_prints_in_15m_onset",
            timestamp=200.0,
            direction="live_by",
            basis="public_trade_exchange_created_time",
            precision="second",
            evidence={},
        )
        clean = recovery.select_event(self.event(), [lower, upper])
        self.assertEqual("clean_interval", clean["precision_class"])
        self.assertTrue(clean["positive_window1_provable"])
        contradiction = recovery.select_event(
            self.event(),
            [{**lower, "timestamp_utc": recovery.iso_utc(300.0)}, upper],
        )
        self.assertEqual(
            "contradictory", contradiction["precision_class"]
        )
        self.assertFalse(contradiction["positive_window1_provable"])

    def test_schedule_only_cannot_prove_a_positive(self):
        selected = recovery.select_event(self.event(), [])
        self.assertEqual("schedule_only", selected["precision_class"])
        self.assertFalse(selected["positive_window1_provable"])


class StartAdjudicationTests(unittest.TestCase):
    def test_exact_five_requires_causal_placement_and_prestart_completion(self):
        leg = {
            "event_id": "E",
            "ticker": "E-A",
            "source_lifecycle_status": "exact_filled_five",
            "exact_five_quantity": True,
            "official_fill_quantity": 5,
            "official_fill_vwap_cents": 40,
            "ten_contract_overfill": False,
            "placement_fill_causality": {
                "all_filled_orders_have_causal_exchange_clock": True,
                "completion_exchange_ts": 100.0,
            },
        }
        start = {
            "precision_class": "exact",
            "exact_start_utc": 200.0,
            "selected_source": "official",
        }
        result = adjudication.adjudicate_leg(leg, start)
        self.assertTrue(result["proven_window1_exact_five"])
        start["exact_start_utc"] = 50.0
        result = adjudication.adjudicate_leg(leg, start)
        self.assertFalse(result["proven_window1_exact_five"])
        self.assertTrue(result["proven_post_start_fill"])

    def test_ten_contract_fill_never_becomes_exact_five(self):
        leg = {
            "event_id": "E",
            "ticker": "E-A",
            "source_lifecycle_status": "exact_filled_other_quantity",
            "exact_five_quantity": False,
            "official_fill_quantity": 10,
            "official_fill_vwap_cents": 40,
            "ten_contract_overfill": True,
            "placement_fill_causality": {
                "all_filled_orders_have_causal_exchange_clock": True,
                "completion_exchange_ts": 100.0,
            },
        }
        start = {
            "precision_class": "exact",
            "exact_start_utc": 200.0,
            "selected_source": "official",
        }
        result = adjudication.adjudicate_leg(leg, start)
        self.assertFalse(result["exact_five_quantity"])
        self.assertFalse(result["proven_window1_exact_five"])
        self.assertEqual(
            "historical_other_quantity_fill", result["ruling"]
        )


if __name__ == "__main__":
    unittest.main()
