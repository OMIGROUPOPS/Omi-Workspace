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
        self.assertIn('o.get("order_id")', authority)
        self.assertIn('o.get("price")', authority)
        self.assertNotIn('o.get("oid")', authority)
        self.assertNotIn('o.get("px")', authority)
        self.assertNotIn('o["oid"]', authority)
        self.assertNotIn('o["px"]', authority)

    def test_counterfactual_decision_dials_are_default_off(self):
        cascade = function_source("_band_cascade_pass")
        anchor = function_source("_v4_entry_anchor")
        route = function_source("_route_event")

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


if __name__ == "__main__":
    unittest.main()
