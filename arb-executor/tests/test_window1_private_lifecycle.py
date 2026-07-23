#!/usr/bin/env python3
"""Tests for the read-only private Window-1 lifecycle instrument."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "arb-executor" / "analysis" / "window1_private_lifecycle.py")
SPEC = importlib.util.spec_from_file_location(
    "window1_private_lifecycle", MODULE_PATH)
LIFE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(LIFE)


def source_order(**updates):
    row = {
        "order_id": "order-redacted",
        "client_order_id": "client-redacted",
        "event_id": "KXATPMATCH-26JUL12ABCCDE",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "leg": "ABC",
        "action": "buy",
        "side": "yes",
        "purpose": "entry",
        "quantity": 5,
        "price_cents": 42,
        "exchange_created_ts": 100.0,
        "evaluation_end_exchange_ts": 200.0,
    }
    row.update(updates)
    return row


def slot(order=None):
    order = order or source_order()
    return {
        "order_id": order["order_id"],
        "client_order_id": order["client_order_id"],
        "event_id": order["event_id"],
        "ticker": order["ticker"],
        "leg": order["leg"],
        "source_order": order,
    }


def api_order(**updates):
    row = {
        "order_id": "order-redacted",
        "client_order_id": "client-redacted",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "action": "buy",
        "side": "yes",
        "outcome_side": "yes",
        "status": "canceled",
        "yes_price_dollars": "0.4200",
        "no_price_dollars": "0.5800",
        "fill_count_fp": "0.00",
        "remaining_count_fp": "5.00",
        "initial_count_fp": "5.00",
        "created_time": "1970-01-01T00:01:40Z",
        "last_update_time": "1970-01-01T00:03:00Z",
    }
    row.update(updates)
    return row


def api_fill(**updates):
    row = {
        "fill_id": "fill-redacted",
        "trade_id": "trade-redacted",
        "order_id": "order-redacted",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "action": "buy",
        "side": "yes",
        "outcome_side": "yes",
        "yes_price_dollars": "0.4200",
        "no_price_dollars": "0.5800",
        "count_fp": "5.00",
        "created_time": "1970-01-01T00:02:00Z",
    }
    row.update(updates)
    return row


class LifecycleTests(unittest.TestCase):
    def test_only_get_paths_are_defined(self):
        self.assertEqual("GET", LIFE.ALLOWED_METHOD)
        text = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn(".post(", text)
        self.assertNotIn(".delete(", text)
        self.assertNotIn(".put(", text)
        self.assertNotIn(".patch(", text)

    def test_query_path_is_v2_and_deterministic(self):
        self.assertEqual(
            "/trade-api/v2/portfolio/fills?limit=1000&order_id=x",
            LIFE.query_path(
                "/trade-api/v2/portfolio/fills",
                {"limit": 1000, "order_id": "x"}),
        )
        with self.assertRaises(LIFE.LifecycleError):
            LIFE.query_path("/not-allowed", {})

    def test_strict_canceled_nonfill(self):
        got = LIFE.classify_slot(
            slot(), {"order-redacted": [api_order()]}, {})
        self.assertEqual(
            "valid_nonfill_cancellation_rejection_recovered",
            got["final_class"],
        )
        self.assertTrue(got["terminal_receipt_recovered"])
        self.assertFalse(got["fill_receipt_recovered"])

    def test_strict_executed_fill(self):
        order = api_order(
            status="executed", fill_count_fp="5.00",
            remaining_count_fp="0.00")
        got = LIFE.classify_slot(
            slot(), {"order-redacted": [order]},
            {"order-redacted": [api_fill()]})
        self.assertEqual("exact_fill_receipt_recovered", got["final_class"])
        self.assertTrue(got["fill_receipt_recovered"])
        self.assertEqual(5.0, got["normalized_fills"][0]["quantity"])

    def test_client_identity_mismatch_is_ambiguous(self):
        got = LIFE.classify_slot(
            slot(),
            {"order-redacted": [api_order(client_order_id="wrong")]},
            {},
        )
        self.assertEqual("ambiguous", got["final_class"])
        self.assertIn("client_order_id_mismatch", got["reason_codes"])

    def test_api_recovers_missing_source_side_and_exchange_clock(self):
        source = source_order(side=None, exchange_created_ts=None)
        got = LIFE.classify_slot(
            slot(source), {"order-redacted": [api_order()]}, {})
        self.assertEqual(
            "valid_nonfill_cancellation_rejection_recovered",
            got["final_class"],
        )

    def test_evaluation_edge_uses_frozen_validation_law(self):
        source = source_order(evaluation_end_exchange_ts=None)
        enriched, counts = LIFE.enrich_evaluation_edges(
            [source],
            [{
                "event_id": source["event_id"],
                "actual_start_verified": False,
                "scheduled_start_exchange_ts": 200,
            }],
        )
        self.assertEqual(3800.0, enriched[0]["evaluation_end_exchange_ts"])
        self.assertEqual(1, counts["scheduled_start_plus_60m_corridor"])

    def test_absent_is_source_exhausted_not_a_fill(self):
        got = LIFE.classify_slot(slot(), {}, {})
        self.assertEqual(
            "still_absent_after_complete_source_exhaustion",
            got["final_class"],
        )
        self.assertFalse(got["terminal_receipt_recovered"])

    def test_sanitized_rows_drop_private_ids(self):
        result = LIFE.classify_slot(slot(), {}, {})
        rows = LIFE.sanitized_slot_rows([result])
        payload = json.dumps(rows)
        self.assertNotIn("order-redacted", payload)
        self.assertNotIn("client-redacted", payload)
        self.assertEqual(
            "KXATPMATCH-26JUL12ABCCDE", rows[0]["event_id"])

    def test_validation_sanitizer_drops_order_attempt_fill_ids(self):
        rows = LIFE.sanitize_validation_rows([{
            "mismatch_type": "fill_receipt",
            "event_id": "E1",
            "ticker": "T1",
            "leg": "A",
            "order_id": "private-order",
            "fill_id": "private-fill",
            "detail": "receipt mismatch",
        }])
        payload = json.dumps(rows)
        self.assertNotIn("private-order", payload)
        self.assertNotIn("private-fill", payload)

    def test_identity_free_failed_attempts_are_never_collapsed(self):
        attempts = [
            {"accepted": False, "ticker": "T-A", "order_id": None},
            {"accepted": False, "ticker": "T-B", "order_id": None},
        ]
        got = LIFE.apply_order_replacements(attempts, {})
        self.assertEqual(["T-A", "T-B"], [row["ticker"] for row in got])

    def test_raw_writer_is_immutable_after_close(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.jsonl"
            writer = LIFE.RawPageWriter(path)
            writer.append({"response": {"orders": []}})
            writer.close()
            mode = path.stat().st_mode & 0o777
            self.assertTrue(mode & 0o400)
            self.assertFalse(mode & 0o222)


class CommittedSanitizedResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = ROOT / ".claude" / "window1_20260721"
        cls.export = json.loads((
            cls.artifacts
            / "PRIVATE_LIFECYCLE_EXPORT_MANIFEST.sanitized.json"
        ).read_text(encoding="utf-8"))
        cls.join = json.loads((
            cls.artifacts
            / "PRIVATE_LIFECYCLE_JOIN_SUMMARY.sanitized.json"
        ).read_text(encoding="utf-8"))
        cls.validation = json.loads((
            cls.artifacts
            / "PRIVATE_LIFECYCLE_VALIDATION_RESULT.sanitized.json"
        ).read_text(encoding="utf-8"))
        cls.artifact_manifest = json.loads((
            cls.artifacts
            / "PRIVATE_LIFECYCLE_ARTIFACT_MANIFEST.json"
        ).read_text(encoding="utf-8"))
        cls.slots = LIFE.read_jsonl(
            cls.artifacts
            / "PRIVATE_LIFECYCLE_SLOT_RESULTS.sanitized.jsonl")
        cls.unresolved = LIFE.read_jsonl(
            cls.artifacts
            / "PRIVATE_LIFECYCLE_UNRESOLVED.sanitized.jsonl")

    def test_export_pagination_and_source_exhaustion_are_complete(self):
        proof = self.export["pagination_proof"]
        self.assertTrue(self.export["complete"])
        self.assertEqual(785, proof["pagination_queries"])
        self.assertEqual(785, proof["pagination_complete_empty_cursor"])
        self.assertEqual(0, proof["cursor_cycles"])
        self.assertEqual(0, proof["request_errors"])
        self.assertEqual({"404": 703},
                         self.export["direct_order_http_status_counts"])

    def test_all_703_slots_remain_absent_without_inference(self):
        self.assertEqual(703, len(self.slots))
        self.assertEqual(
            {"still_absent_after_complete_source_exhaustion"},
            {row["final_class"] for row in self.slots},
        )
        self.assertEqual(0, self.join["exact_terminal_receipt_recovered"])
        self.assertEqual(0, self.join["exact_fill_receipt_recovered"])
        self.assertEqual(0, self.join["ambiguous"])

    def test_validation_before_after_is_identical_and_gate_stays_closed(self):
        self.assertEqual(804, self.validation["D"])
        self.assertEqual(
            self.validation["before"]["mismatch_count"],
            self.validation["after"]["mismatch_count"],
        )
        self.assertEqual(
            self.validation["before"]["mismatch_types"],
            self.validation["after"]["mismatch_types"],
        )
        self.assertFalse(self.validation["after"]["gate_pass"])
        self.assertFalse(self.validation["strategy_scoring_permitted"])
        self.assertEqual(1054, len(self.unresolved))

    def test_sanitized_artifacts_have_no_private_identity_keys_or_micmay(self):
        forbidden = {
            "order_id", "client_order_id", "fill_id", "trade_id",
            "attempt_id", "attempt_receipt_id", "account_id",
        }
        for row in [*self.slots, *self.unresolved]:
            self.assertTrue(forbidden.isdisjoint(row))
        payload = json.dumps({
            "export": self.export,
            "join": self.join,
            "validation": self.validation,
            "slots": self.slots,
            "unresolved": self.unresolved,
        })
        self.assertNotIn(
            "KXATPCHALLENGERMATCH-26JUL21MICMAY", payload)

    def test_committed_sanitized_artifact_hashes_are_exact(self):
        for item in self.artifact_manifest["sanitized_artifacts"]:
            path = self.artifacts / item["path"]
            payload = path.read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            if digest != item["sha256"]:
                payload = payload.replace(b"\r\n", b"\n")
                digest = hashlib.sha256(payload).hexdigest()
            self.assertEqual(item["bytes"], len(payload))
            self.assertEqual(item["sha256"], digest)


if __name__ == "__main__":
    unittest.main()
