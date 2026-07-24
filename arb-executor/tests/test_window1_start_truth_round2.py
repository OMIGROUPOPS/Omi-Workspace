#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_start_truth_round2 as round2  # noqa: E402


class StartTruthRound2Tests(unittest.TestCase):
    def baseline(self):
        return {
            "event_id": "E",
            "event_date": "2026-07-12",
            "category": "ATP_MAIN",
            "legs": [
                {"leg": "A", "ticker": "E-A"},
                {"leg": "B", "ticker": "E-B"},
            ],
            "precision_class": "live_by_only",
            "positive_window1_provable": False,
            "exact_start_utc": None,
            "not_live_through_utc": None,
            "known_live_by_utc": "2026-07-12T10:05:00+00:00",
            "start_interval_utc": {
                "lower_inclusive": None,
                "upper_inclusive": "2026-07-12T10:05:00+00:00",
            },
            "selected_source": "public_tape",
            "selected_source_family": "true_tape_regime_interval",
            "selected_timestamp_precision": "minute",
            "conflict_status": "none",
            "interval_contradiction": False,
            "candidate_sources": [{
                "source": "public_tape",
                "source_family": "true_tape_regime_interval",
                "precedence_rank": 7,
                "timestamp_utc": "2026-07-12T10:05:00+00:00",
                "direction": "live_by",
                "precision": "minute",
                "timestamp_basis": "exchange_print_time",
                "evidence": {},
            }],
        }

    def crosswalk(self):
        return {
            "event_id": "E",
            "start_utc": "2026-07-12T10:10:00+00:00",
            "selected_te_match_id": "123",
            "event_source_id": "sr:sport_event:1",
            "competitor_source_ids": [
                "sr:competitor:1", "sr:competitor:2"
            ],
            "selected_te_page_date": "2026-07-12",
            "milestone_start_date_identity_only": (
                "2026-07-12T10:00:00Z"
            ),
            "selected_te_page_sha256": "a" * 64,
        }

    def test_itf_and_wta125_same_city_are_not_same_tournament(self):
        self.assertFalse(round2.tournament_matches(
            "WTA 125K Istanbul", "Istanbul 10 ITF"
        ))
        self.assertTrue(round2.tournament_matches(
            "ATP Challenger Lincoln (NE)", "Lincoln challenger"
        ))

    def test_lower_precedence_tape_conflict_does_not_erase_exact_start(self):
        row, conflicts = round2.adjudicate_residual(
            self.baseline(), self.crosswalk()
        )
        self.assertEqual("exact", row["precision_class"])
        self.assertTrue(row["positive_window1_provable"])
        self.assertEqual(
            "tennisexplorer_historical_result_start_clock",
            row["selected_source"],
        )
        self.assertEqual(1, len(conflicts))
        self.assertEqual(
            "exact_result_start_controls_by_precedence",
            conflicts[0]["disposition"],
        )

    def test_higher_precedence_not_started_conflict_blocks_promotion(self):
        baseline = self.baseline()
        baseline["candidate_sources"].append({
            "source": "milestone_shadow_not_started_observation",
            "source_family": "raw_milestone_shadow",
            "precedence_rank": 2,
            "timestamp_utc": "2026-07-12T10:11:00+00:00",
            "direction": "not_live_through",
            "precision": "subsecond",
            "timestamp_basis": "receipt",
            "evidence": {"status": "not_started"},
        })
        row, conflicts = round2.adjudicate_residual(
            baseline, self.crosswalk()
        )
        self.assertEqual("contradictory", row["precision_class"])
        self.assertFalse(row["positive_window1_provable"])
        self.assertTrue(any(
            conflict["disposition"] == "blocks_promotion"
            for conflict in conflicts
        ))

    def test_preserved_positive_is_not_targeted_or_reinterpreted(self):
        baseline = self.baseline()
        baseline.update({
            "precision_class": "clean_interval",
            "positive_window1_provable": True,
            "not_live_through_utc": "2026-07-12T10:00:00+00:00",
        })
        result = round2.preserve_positive(baseline)
        self.assertEqual("clean_interval", result["precision_class"])
        self.assertTrue(result["positive_window1_provable"])
        self.assertFalse(result["round2_targeted"])


if __name__ == "__main__":
    unittest.main()
