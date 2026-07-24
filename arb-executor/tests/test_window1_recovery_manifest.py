#!/usr/bin/env python3
"""Tests for the local-only Window-1 recovery manifest."""

from __future__ import annotations

import sys
import unittest
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_recovery_manifest as recovery  # noqa: E402


ARTIFACTS = REPO / ".claude" / "window1_20260721"


class RecoveryManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = recovery.build(
            recovery.load_jsonl(
                ARTIFACTS / "corrected_event_ledger.jsonl"),
            recovery.load_jsonl(
                ARTIFACTS
                / "POLICY_MISMATCH_RECLASSIFICATION.sanitized.jsonl"),
            recovery.load_jsonl(
                ARTIFACTS / "CAUSAL_DECISIONS.sanitized.jsonl"),
            recovery.load_json(
                ARTIFACTS
                / "CORRECTED_VALIDATION_SUMMARY.sanitized.json"),
        )

    def test_exact_1054_mismatch_census(self):
        rows = self.result["mismatches"]
        self.assertEqual(1054, len(rows))
        self.assertEqual(1054, len({row["mismatch_id"] for row in rows}))
        self.assertEqual(
            recovery.EXPECTED_MISMATCHES,
            dict(Counter(row["mismatch_class"] for row in rows)),
        )

    def test_exact_recovery_status_census(self):
        self.assertEqual(
            {"possible": 3, "uncertain": 1051, "impossible": 0},
            self.result["summary"]["recovery_status_counts"],
        )

    def test_every_mismatch_has_the_recovery_contract(self):
        required = {
            "event",
            "market_ticker",
            "leg",
            "order_or_attempt_identity",
            "causal_timestamp",
            "mismatch_class",
            "expected_evidence",
            "evidence_actually_present",
            "source_needed",
            "recovery_status",
        }
        for row in self.result["mismatches"]:
            self.assertTrue(required.issubset(row), row["mismatch_id"])
            self.assertIn(
                row["recovery_status"], {"possible", "uncertain", "impossible"})
            self.assertTrue(row["expected_evidence"], row["mismatch_id"])
            self.assertTrue(row["evidence_actually_present"], row["mismatch_id"])

    def test_private_identity_is_not_emitted(self):
        rows = self.result["mismatches"]
        self.assertTrue(all(
            row["order_or_attempt_identity"]["available"] is False
            for row in rows))
        self.assertEqual(
            0,
            self.result["summary"]["identity_coverage"]
            ["raw_order_or_attempt_id_emitted"],
        )

    def test_policy_overlap_reconciles_by_leg(self):
        summary = self.result["summary"]
        self.assertEqual(351, summary["policy_event_total"])
        self.assertEqual(643, summary["policy_missing_leg_total"])
        self.assertEqual(308, summary["causal_decision_leg_total"])
        self.assertEqual(335, summary["unobserved_decision_leg_total"])
        mapping = summary["policy_reconciliation"]["mapping_defect"]
        self.assertEqual({
            "events": 47,
            "missing_legs": 52,
            "causal_decision_legs": 50,
            "unobserved_legs": 2,
        }, mapping)

    def test_terminal_receipt_allocation_stays_unclaimed(self):
        self.assertEqual(703, len(self.result["terminal_receipts"]))
        allocation = self.result["summary"][
            "terminal_receipt_source_allocation"]
        self.assertEqual(703, allocation[
            "unallocated_pending_private_identity_join"])
        self.assertEqual(0, allocation["confirmed_no_surviving_source"])

    def test_mapping_defect_report_has_named_tokroz_exhibit(self):
        rows = self.result["mapping_defects"]
        self.assertEqual(47, len(rows))
        tokroz = next(
            row for row in rows
            if row["event_id"]
            == "KXATPCHALLENGERMATCH-26JUL12TOKROZ")
        self.assertEqual(2, tokroz["unobserved_leg_count"])
        self.assertEqual(
            [False, True],
            sorted(state["order_placed_log_evidence"]
                   for state in tokroz["leg_states"]),
        )

    def test_micmay_is_post_sample_and_not_mapped(self):
        micmay = self.result["micmay"]
        self.assertFalse(micmay["inside_D"])
        self.assertFalse(micmay["present_in_corrected_event_ledger"])
        self.assertFalse(micmay["present_in_policy_reclassification"])
        self.assertEqual(
            "not established from local July 12-20 artifacts",
            micmay["participant_mapping_status"],
        )

    def test_human_mapping_report_names_every_mapping_event(self):
        report = (
            REPO / "arb-executor" / "docs" / "research" / "window1"
            / "MAPPING_DEFECT_REPORT.md"
        ).read_text(encoding="utf-8")
        for row in self.result["mapping_defects"]:
            self.assertIn(row["event_id"], report)

    def test_artifact_hash_receipt_matches_bytes(self):
        manifest = json.loads((
            ARTIFACTS / "EVIDENCE_RECOVERY_ARTIFACT_MANIFEST.json"
        ).read_text(encoding="utf-8"))
        for section in ("inputs", "outputs"):
            for item in manifest[section]:
                path = ARTIFACTS / item["path"]
                relative = path.relative_to(REPO).as_posix()
                blob = subprocess.check_output(
                    ["git", "show", f"HEAD:{relative}"],
                    cwd=REPO,
                )
                digest = hashlib.sha256(blob).hexdigest()
                self.assertEqual(item["sha256"], digest, item["path"])
                if "bytes" in item:
                    self.assertEqual(item["bytes"], len(blob), item["path"])

    def test_committed_jsonl_outputs_equal_the_builder(self):
        self.assertEqual(
            self.result["mismatches"],
            recovery.load_jsonl(
                ARTIFACTS / "MISMATCH_RECOVERY_LEDGER.sanitized.jsonl"),
        )
        self.assertEqual(
            self.result["terminal_receipts"],
            recovery.load_jsonl(
                ARTIFACTS
                / "TERMINAL_RECEIPT_RECOVERY_MANIFEST.sanitized.jsonl"),
        )
        self.assertEqual(
            self.result["mapping_defects"],
            recovery.load_jsonl(
                ARTIFACTS / "MAPPING_DEFECTS.sanitized.jsonl"),
        )


if __name__ == "__main__":
    unittest.main()
