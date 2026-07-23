#!/usr/bin/env python3
"""Tests for the read-only Window-1 live/historical tier reconciler."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "arb-executor" / "analysis" / "window1_tier_reconcile.py")
SPEC = importlib.util.spec_from_file_location(
    "window1_tier_reconcile", MODULE_PATH)
TIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(TIER)


def sample(**updates):
    value = {
        "sample_id": "target-001",
        "is_target": True,
        "strata": ["successful_cancel"],
        "event_id": "KXATPMATCH-26JUL12ABCCDE",
        "ticker": "KXATPMATCH-26JUL12ABCCDE-ABC",
        "order_id": "order-1",
        "client_order_id": "client-1",
        "raw_post_201_body_proof": False,
        "raw_cancel_body_proof": False,
        "normalized_successful_placement_receipt": True,
    }
    value.update(updates)
    return value


class ReadOnlyContractTests(unittest.TestCase):
    def test_network_surface_is_get_only(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(
                    node.func, ast.Attribute):
                calls.append(node.func.attr)
        for forbidden in ("post", "put", "patch", "delete"):
            self.assertNotIn(forbidden, calls)
        self.assertEqual("GET", TIER.METHOD)

    def test_query_path_rejects_non_v2_and_encodes_filters(self):
        self.assertEqual(
            "/trade-api/v2/portfolio/orders?ticker=A%2FB&limit=1000",
            TIER.query_path(
                "/trade-api/v2/portfolio/orders",
                {"ticker": "A/B", "limit": 1000, "cursor": ""},
            ),
        )
        with self.assertRaises(TIER.TierError):
            TIER.query_path("/portfolio/orders", {})

    def test_strata_are_nonexclusive(self):
        evidence = {
            "placements": [{"details": {"response_status": "filled"}}],
            "cancellations": [{"details": {"success": False}}],
            "orphan_readoptions": [{"details": {}}],
        }
        self.assertEqual(
            [
                "cancel_failure",
                "cancel_failure_attempt",
                "immediate_fill",
                "orphan_readopted",
            ],
            TIER.strata_for({}, evidence),
        )

    def test_transient_cancel_failure_is_not_terminal_failure(self):
        evidence = {
            "placements": [],
            "cancellations": [
                {"details": {"success": False}},
                {"details": {"success": True}},
            ],
            "orphan_readoptions": [],
        }
        self.assertEqual(
            ["cancel_failure_attempt", "successful_cancel"],
            TIER.strata_for({}, evidence),
        )


class ClassificationTests(unittest.TestCase):
    def classify(self, row=None, live=None, historical=None, fills=None):
        return TIER.classify_sample(
            row or sample(),
            live or [],
            historical or [],
            fills or [],
            [],
        )

    def test_exact_live_precedes_other_evidence(self):
        got = self.classify(live=[{"order_id": "order-1"}])
        self.assertEqual(
            "A_exchange_created_found_live", got["classification"])

    def test_exact_historical_is_decisive(self):
        got = self.classify(historical=[{"order_id": "order-1"}])
        self.assertEqual(
            "B_exchange_created_found_historical", got["classification"])

    def test_both_partitions_are_contradictory(self):
        row = {"order_id": "order-1"}
        got = self.classify(live=[row], historical=[row])
        self.assertEqual(
            "E_contradictory_or_unknown", got["classification"])

    def test_preserved_raw_201_without_retrieval_is_c(self):
        got = self.classify(sample(raw_post_201_body_proof=True))
        self.assertEqual(
            "C_raw_201_subsequently_unretrievable",
            got["classification"],
        )

    def test_normalized_receipt_without_raw_body_is_d(self):
        got = self.classify()
        self.assertEqual(
            "D_log_only_acknowledgement_raw_body_absent",
            got["classification"],
        )


class PaginationTests(unittest.TestCase):
    class StubClient:
        paged = TIER.ReadOnlyClient.paged

        def __init__(self, replies):
            self.replies = iter(replies)
            self.pagination_queries = 0
            self.pagination_completed = 0
            self.cursor_cycles = 0
            self.paths = []

        def get(self, path, label, allow_404=False):
            self.paths.append((path, label, allow_404))
            return next(self.replies)

    def test_cursor_chain_reaches_empty_cursor(self):
        client = self.StubClient([
            (200, {"orders": [{"order_id": "1"}], "cursor": "next"}),
            (200, {"orders": [{"order_id": "2"}], "cursor": ""}),
        ])
        rows = client.paged(
            "/trade-api/v2/historical/orders",
            {"ticker": "T", "limit": 1000},
            "orders",
            "history",
        )
        self.assertEqual(["1", "2"], [row["order_id"] for row in rows])
        self.assertEqual(1, client.pagination_completed)
        self.assertIn("cursor=next", client.paths[1][0])

    def test_allowed_historical_404_is_complete_empty_query(self):
        client = self.StubClient([(404, {"error": {}})])
        rows = client.paged(
            "/trade-api/v2/historical/fills",
            {"ticker": "T", "limit": 1000},
            "fills",
            "history",
            allow_404_empty=True,
        )
        self.assertEqual([], rows)
        self.assertEqual(1, client.pagination_completed)
        self.assertTrue(client.paths[0][2])

    def test_cursor_cycle_fails_closed(self):
        client = self.StubClient([
            (200, {"orders": [], "cursor": "repeat"}),
            (200, {"orders": [], "cursor": "repeat"}),
        ])
        with self.assertRaises(TIER.TierError):
            client.paged(
                "/trade-api/v2/historical/orders",
                {"ticker": "T"}, "orders", "history")
        self.assertEqual(1, client.cursor_cycles)


class DedupTests(unittest.TestCase):
    def test_identical_overlap_is_counted(self):
        rows, duplicates = TIER.dedup([
            {"order_id": "1", "status": "canceled"},
            {"order_id": "1", "status": "canceled"},
        ], ("order_id",))
        self.assertEqual(1, len(rows))
        self.assertEqual(1, duplicates)

    def test_conflicting_overlap_fails_closed(self):
        with self.assertRaises(TIER.TierError):
            TIER.dedup([
                {"order_id": "1", "status": "resting"},
                {"order_id": "1", "status": "canceled"},
            ], ("order_id",))


if __name__ == "__main__":
    unittest.main()
