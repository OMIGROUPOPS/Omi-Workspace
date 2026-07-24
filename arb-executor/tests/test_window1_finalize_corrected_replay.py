#!/usr/bin/env python3
"""Tests for corrected-replay publication finalization."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

import window1_finalize_corrected_replay as finalizer  # noqa: E402


class FinalizeCorrectedReplayTests(unittest.TestCase):
    def test_attempt_lineage_matches_kernel_contract(self):
        self.assertEqual(
            "attempt:A",
            finalizer.lineage({
                "trade_id": "",
                "attempt_id": "A",
                "order_id": "O",
            }),
        )
        self.assertEqual(
            "T",
            finalizer.lineage({
                "trade_id": "T",
                "attempt_id": "A",
            }),
        )

    def test_supplement_is_sanitized_and_filters_to_D(self):
        orders = []
        lifecycles = []
        tickers = set()
        for index in range(14):
            ticker = f"T{index}"
            attempt = f"A{index}"
            tickers.add(ticker)
            orders.append({
                "accepted": False,
                "event_id": "E",
                "ticker": ticker,
                "trade_id": "",
                "attempt_id": attempt,
                "order_id": f"PRIVATE-{index}",
                "exchange_created_ts": None,
                "local_logged_ts": 100.0,
                "price_cents": 42,
                "quantity": 5,
            })
            lifecycles.append({
                "event_id": "E",
                "ticker": ticker,
                "lineage": f"attempt:{attempt}",
            })
        rows = finalizer.supplement_failed_decisions(
            orders, lifecycles, tickers
        )
        self.assertEqual(14, len(rows))
        self.assertTrue(all("order_id" not in row for row in rows))
        self.assertTrue(all("attempt_id" not in row for row in rows))
        self.assertTrue(all(
            row["private_identifier_included"] is False for row in rows
        ))


if __name__ == "__main__":
    unittest.main()
