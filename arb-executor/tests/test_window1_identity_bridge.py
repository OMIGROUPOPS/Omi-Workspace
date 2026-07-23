#!/usr/bin/env python3
"""Tests for the offline Window-1 identity bridge."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "arb-executor" / "analysis" / "window1_identity_bridge.py")
SPEC = importlib.util.spec_from_file_location(
    "window1_identity_bridge", MODULE_PATH)
BRIDGE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BRIDGE)


def source(**updates):
    value = {
        "order_id": "11111111-1111-4111-8111-111111111111",
        "client_order_id": "client-1",
        "trade_id": "attempt-1",
        "event_id": "KXATPMATCH-26JUL12ABCCDE",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "action": "buy",
        "side": None,
        "price_cents": 42,
        "quantity": 5,
        "local_logged_ts": 1_000.0,
    }
    value.update(updates)
    return value


def log(**updates):
    value = {
        "order_id": "11111111-1111-4111-8111-111111111111",
        "client_order_id": "client-1",
        "internal_trade_id": "attempt-1",
        "event_id": "KXATPMATCH-26JUL12ABCCDE",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "action": "buy",
        "side": "yes",
        "price_cents": 42,
        "quantity": 5,
        "local_logged_ts": 1_000.0,
        "response_status": 201,
    }
    value.update(updates)
    return value


def api(**updates):
    value = {
        "order_id": "22222222-2222-4222-8222-222222222222",
        "client_order_id": "client-2",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "action": "buy",
        "outcome_side": "yes",
        "yes_price_dollars": "0.4200",
        "no_price_dollars": "0.5800",
        "initial_count_fp": "5.00",
        "created_time": "1970-01-01T00:16:35Z",
        "status": "canceled",
    }
    value.update(updates)
    return value


class OfflineContractTests(unittest.TestCase):
    def test_source_has_no_network_imports(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        forbidden = {"requests", "httpx", "socket", "urllib.request"}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        self.assertTrue(forbidden.isdisjoint(imported))

    def test_uuid_canonicalization_is_diagnostic(self):
        exact = "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"
        loose = "{aaaaaaaaaaaa4aaa8aaaaaaaaaaaaaaa}"
        self.assertEqual(
            BRIDGE.canonical_identifier(exact),
            BRIDGE.canonical_identifier(loose),
        )
        self.assertNotEqual(exact, loose)

    def test_composite_uses_independent_log_side(self):
        got = BRIDGE.source_composite(source(), log())
        self.assertEqual(
            (
                "KXATPMATCH-26JUL12ABCCDE-ABC",
                "yes",
                "buy",
                42,
                "5",
            ),
            got,
        )

    def test_causal_composite_requires_nonnegative_bounded_lag(self):
        order = api()
        index = {BRIDGE.api_composite(order): [order]}
        compatible, incompatible = BRIDGE.causal_composite_candidates(
            source(), log(), index, 60.0)
        self.assertEqual(1, len(compatible))
        self.assertEqual([], incompatible)
        compatible, incompatible = BRIDGE.causal_composite_candidates(
            source(), log(local_logged_ts=900), index, 60.0)
        self.assertEqual([], compatible)
        self.assertEqual(1, len(incompatible))

    def test_strict_candidate_detects_each_semantic_family(self):
        candidate = api(
            ticker="KXATPMATCH-26JUL12ABCCDE-WRONG",
            action="sell",
            outcome_side="no",
            no_price_dollars="0.4100",
            initial_count_fp="4.00",
            created_time="1970-01-01T00:10:00Z",
        )
        failures = BRIDGE.strict_candidate_failures(
            source(), log(), candidate, 60.0)
        self.assertIn("ticker_or_participant_mapping_mismatch", failures)
        self.assertIn(
            "side_or_action_canonicalization_mismatch", failures)
        self.assertIn(
            "cents_dollars_or_count_count_fp_mismatch", failures)
        self.assertIn("timestamp_or_timezone_mismatch", failures)

    def test_order_placed_response_acceptance_supports_order_states(self):
        self.assertTrue(BRIDGE.response_accepted(201))
        self.assertTrue(BRIDGE.response_accepted("200 OK"))
        self.assertTrue(BRIDGE.response_accepted("resting"))
        self.assertTrue(BRIDGE.response_accepted("filled"))
        self.assertFalse(BRIDGE.response_accepted(404))
        self.assertFalse(BRIDGE.response_accepted(None))

    def test_endpoint_classes_do_not_emit_identity(self):
        self.assertEqual(
            "current_order_exact_id",
            BRIDGE.endpoint_class(
                "/trade-api/v2/portfolio/orders/private-id"),
        )
        self.assertEqual(
            "current_fills_collection",
            BRIDGE.endpoint_class(
                "/trade-api/v2/portfolio/fills?order_id=private-id"),
        )

    def test_target_rebuild_rejects_duplicate_mismatch_identity(self):
        order = source()
        mismatches = [{
            "mismatch_type": "accepted_order_missing_receipt",
            "order_id": order["order_id"],
        } for _ in range(BRIDGE.EXPECTED_SLOTS)]
        with self.assertRaises(BRIDGE.BridgeError):
            BRIDGE.build_target_slots(mismatches, [order])


class RawExportAuditTests(unittest.TestCase):
    def test_cursor_chain_and_filters_are_recomputed(self):
        pages = [
            {
                "method": "GET",
                "path": (
                    "/trade-api/v2/portfolio/orders?"
                    "limit=1000&min_ts=1&max_ts=2"),
                "label": "orders:page-0001",
                "http_status": 429,
                "retry_attempt": 0,
                "response": {"error": "rate limited"},
            },
            {
                "method": "GET",
                "path": (
                    "/trade-api/v2/portfolio/orders?"
                    "limit=1000&min_ts=1&max_ts=2"),
                "label": "orders:page-0001",
                "http_status": 200,
                "retry_attempt": 1,
                "response": {
                    "orders": [api()],
                    "cursor": "cursor-private",
                },
            },
            {
                "method": "GET",
                "path": (
                    "/trade-api/v2/portfolio/orders?"
                    "limit=1000&min_ts=1&max_ts=2&"
                    "cursor=cursor-private"),
                "label": "orders:page-0002",
                "http_status": 200,
                "response": {"orders": [], "cursor": ""},
            },
        ]
        audit = BRIDGE.audit_raw_pages(
            pages,
            [api()],
            [],
            {"pagination_proof": {
                "pagination_queries": 1,
                "pagination_complete_empty_cursor": 1,
                "cursor_cycles": 0,
                "request_errors": 0,
            }},
        )
        self.assertEqual([], audit["pagination"]["errors"])
        self.assertEqual(
            1, audit["pagination"]["groups_ending_empty_cursor"])
        self.assertEqual(
            {"canceled": 1}, audit["status_coverage"])
        self.assertEqual(1, audit["records"]["retry_attempt_rows"])
        payload = json.dumps(audit)
        self.assertNotIn("cursor-private", payload)
        self.assertNotIn("private-id", payload)


class CommittedIdentityBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = ROOT / ".claude" / "window1_20260721"
        cls.summary = json.loads((
            cls.artifacts / "IDENTITY_BRIDGE_SUMMARY.sanitized.json"
        ).read_text(encoding="utf-8"))
        cls.audit = json.loads((
            cls.artifacts / "IDENTITY_BRIDGE_EXPORT_AUDIT.sanitized.json"
        ).read_text(encoding="utf-8"))
        cls.proofs = json.loads((
            cls.artifacts / "IDENTITY_BRIDGE_PROOFS.sanitized.json"
        ).read_text(encoding="utf-8"))
        cls.manifest = json.loads((
            cls.artifacts / "IDENTITY_BRIDGE_ARTIFACT_MANIFEST.json"
        ).read_text(encoding="utf-8"))
        cls.rows = [
            json.loads(line) for line in (
                cls.artifacts / "IDENTITY_BRIDGE.sanitized.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]

    def test_all_703_slots_are_enumerated_without_private_values(self):
        self.assertEqual(703, len(self.rows))
        self.assertEqual(703, self.summary["target_slots"])
        self.assertTrue(all(
            row["private_identifiers_emitted"] is False
            for row in self.rows
        ))
        payload = json.dumps(self.rows)
        self.assertNotIn(
            "KXATPCHALLENGERMATCH-26JUL21MICMAY", payload)
        self.assertIsNone(re.search(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}\b",
            payload,
        ))
        self.assertIsNone(re.search(r"\bT-\d{8}-\d{4}\b", payload))
        self.assertNotIn("/root/", payload)
        self.assertNotIn("/mnt/", payload)

    def test_all_accepted_placements_are_log_corroborated(self):
        self.assertEqual(
            {"exchange_accepted_response_corroborated": 703},
            self.summary["accepted_order_evidence_counts"],
        )
        self.assertEqual(
            {"filled": 1, "resting": 702},
            self.summary["slot_log_response_status_counts"],
        )

    def test_no_identity_tier_changes_validation(self):
        self.assertEqual(0, self.summary["matched_slots"])
        self.assertEqual(703, self.summary["unresolved_slots"])
        self.assertEqual(
            {
                "tier1_exact_exchange_order_id": 0,
                "tier2_exact_client_order_id": 0,
                "tier3_unique_corroborated_composite": 0,
                "unresolved": 703,
            },
            self.summary["join_tier_counts"],
        )
        self.assertFalse(self.summary["validation_rerun_required"])
        self.assertFalse(self.summary["validation_rerun_performed"])
        self.assertEqual(
            703,
            self.summary["failure_class_counts"][
                "exchange_id_present_but_absent_from_api"],
        )
        self.assertEqual(
            46,
            self.summary["failure_class_counts"][
                "timestamp_or_timezone_mismatch"],
        )

    def test_export_cursor_and_retry_audit_is_complete(self):
        raw = self.audit["raw_export_audit"]
        self.assertEqual([], raw["pagination"]["errors"])
        self.assertEqual(785, raw["pagination"]["groups"])
        self.assertEqual(
            785, raw["pagination"]["groups_ending_empty_cursor"])
        self.assertEqual(26, raw["records"]["retry_attempt_rows"])
        self.assertEqual(
            703,
            raw["endpoint_logical_query_counts"][
                "current_order_exact_id"],
        )

    def test_committed_artifact_hashes_are_exact(self):
        for item in self.manifest["sanitized_artifacts"]:
            payload = (self.artifacts / item["path"]).read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            if digest != item["sha256"]:
                payload = payload.replace(b"\r\n", b"\n")
                digest = hashlib.sha256(payload).hexdigest()
            self.assertEqual(item["bytes"], len(payload))
            self.assertEqual(item["sha256"], digest)
        source_path = ROOT / self.manifest["source_code"]["path"]
        source_payload = source_path.read_bytes()
        source_digest = hashlib.sha256(source_payload).hexdigest()
        if source_digest != self.manifest["source_code"]["sha256"]:
            source_digest = hashlib.sha256(
                source_payload.replace(b"\r\n", b"\n")).hexdigest()
        self.assertEqual(
            self.manifest["source_code"]["sha256"],
            source_digest,
        )


if __name__ == "__main__":
    unittest.main()
