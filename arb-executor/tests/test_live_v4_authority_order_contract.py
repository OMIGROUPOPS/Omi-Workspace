#!/usr/bin/env python3

from __future__ import annotations

import ast
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LIVE_V4 = REPO / "arb-executor" / "live_v4.py"


def function_source(name: str) -> str:
    source = LIVE_V4.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    return ast.get_source_segment(source, node) or ""


class AuthorityOrderContractTests(unittest.TestCase):
    def test_reconcile_and_authority_use_the_same_order_fields(self):
        reconcile = function_source("reconcile")
        authority = function_source("_naked_tooth_scan")

        self.assertIn('"order_id": o.get("order_id", "")', reconcile)
        self.assertIn('"price": price_cents', reconcile)
        self.assertIn(
            'self.config.get(\n                "authority_order_contract_v2", True)',
            authority,
        )
        self.assertIn('lambda row: row.get("order_id")', authority)
        self.assertIn('lambda row: row.get("price")', authority)
        self.assertIn('else (lambda row: row.get("oid"))', authority)
        self.assertIn('else (lambda row: row.get("px"))', authority)

    def test_only_safe_repaired_contracts_are_enabled_in_deploy_config(self):
        cascade = function_source("_band_cascade_pass")
        anchor = function_source("_v4_entry_anchor")
        route = function_source("_route_event")
        config = __import__("json").loads(
            (REPO / "arb-executor" / "config" / "deploy_v5_live.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertIn(
            'self.config.get("recognition_before_place", False)', cascade
        )
        self.assertIn(
            'self.config.get("recognition_before_place", False)', route
        )
        self.assertIn(
            'self.config.get("contention_drop_enforced", False)', route
        )
        self.assertIn('"selector") == "DROP"', route)
        self.assertIn(
            'self.config.get("cohort_steer_riser", False)', anchor
        )
        self.assertTrue(config["atlas_clock_contract_v2"])
        self.assertTrue(config["authority_order_contract_v2"])
        self.assertFalse(config["contention_drop_enforced"])
        self.assertFalse(config["pair_class_steer_enabled"])
        self.assertFalse(config["entry_table_prior_enabled"])
        self.assertFalse(config["one_authority_enabled"])
        self.assertTrue(config["bulk_fill_poll_enabled"])

    def test_fill_receipt_poll_precedes_per_order_status_poll(self):
        check = function_source("check_fills")
        bulk = function_source("_poll_entry_fills_bulk")

        self.assertLess(
            check.index("await self._poll_entry_fills_bulk()"),
            check.index('"/trade-api/v2/portfolio/orders/%s"'),
        )
        self.assertIn("/trade-api/v2/portfolio/fills?limit=1000", bulk)
        self.assertIn("oid not in tracked", bulk)
        self.assertIn("await self._book_v4_entry_fill(", bulk)

    def test_old_atlas_axis_is_refused_by_default(self):
        dossier = function_source("_entry_dossier")

        self.assertIn('"atlas_clock_contract_v2", True', dossier)
        self.assertIn('"REFUSED_AXIS_MISMATCH"', dossier)
        self.assertIn('"path_tminus_actual_bell"', dossier)


if __name__ == "__main__":
    unittest.main()
