#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_replay_receipt_correction as correction  # noqa: E402


class ReplayReceiptCorrectionTests(unittest.TestCase):
    def test_published_bound_corrects_to_226_without_replay(self):
        legs, events, summary = correction.correction(
            REPO / ".claude" / "window1_corrected_20260723",
            REPO / ".claude" / "window1_20260721"
            / "REAL_START_LEDGER.jsonl",
        )
        self.assertEqual(1_608, len(legs))
        self.assertEqual(804, len(events))
        self.assertEqual(240, summary["published_optimistic_upper_bound"])
        self.assertEqual(
            226,
            summary["corrected_receipts_only_optimistic_upper_bound"],
        )
        self.assertEqual(
            25, summary["removed_from_published_bound"]["count"]
        )
        self.assertEqual(
            11, summary["added_to_published_bound"]["count"]
        )
        self.assertTrue(summary["no_scoring_or_tuning_performed"])

    def test_four_cutoff_only_disjuncts_become_censored(self):
        legs, _, summary = correction.correction(
            REPO / ".claude" / "window1_corrected_20260723",
            REPO / ".claude" / "window1_20260721"
            / "REAL_START_LEDGER.jsonl",
        )
        changed = [
            row for row in legs
            if row["correction"] == "D3_cutoff_only_disjunct_removed"
        ]
        self.assertEqual(4, len(changed))
        self.assertTrue(all(
            row["published_proven_non_window1_fill"]
            and not row["corrected_proven_non_window1_fill"]
            for row in changed
        ))
        self.assertEqual(
            4,
            summary[
                "D3_unsound_cutoff_only_legs_reclassified_censored"
            ]["count"],
        )

    def test_strict_live_by_reselection_proves_11_legs(self):
        legs, _, summary = correction.correction(
            REPO / ".claude" / "window1_corrected_20260723",
            REPO / ".claude" / "window1_20260721"
            / "REAL_START_LEDGER.jsonl",
        )
        changed = [
            row for row in legs
            if row["correction"]
            == "D4_strictest_usable_live_by_selected"
            and row["corrected_proven_non_window1_fill"]
            and not row["published_proven_non_window1_fill"]
        ]
        self.assertEqual(11, len(changed))
        self.assertEqual(
            7, summary["D4_live_by_reselection"]["events"]
        )

    def test_ten_contract_overfill_stays_outside_exact_five(self):
        legs, _, _ = correction.correction(
            REPO / ".claude" / "window1_corrected_20260723",
            REPO / ".claude" / "window1_20260721"
            / "REAL_START_LEDGER.jsonl",
        )
        overfill = [row for row in legs if row["ten_contract_overfill"]]
        self.assertEqual(1, len(overfill))
        self.assertTrue(overfill[0]["other_quantity_fill"])
        self.assertTrue(
            overfill[0]["hard_receipt_failure_for_historical_policy"]
        )


if __name__ == "__main__":
    unittest.main()
