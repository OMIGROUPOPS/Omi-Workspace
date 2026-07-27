#!/usr/bin/env python3
"""Synthetic and frozen-package tests for the T1 scoring PRE-RUN."""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import window1_t1_scoring_adapter_v1 as adapter
import window1_t1_scoring_package_builder_v1 as builder
import window1_t1_scoring_runner_v1 as runner
from window1_range_attack_reference_adapter_v2 import (
    Window1CloseReferenceV2,
)
from window1_range_attack_scoring_runner_v2 import (
    canonical_text_bytes,
    verify_authorization_report_text,
)
from window1_range_attack_scoring_runner_v1 import RunnerError


CANDIDATE = adapter_source_candidate = (
    "w1_t1__macro_hold__response_only"
)
PARENT = "w1_range_attack__macro_hold__combined_headroom"
EVENT_ID = "KXATPCHALLENGERMATCH-26JUL12SYNTH"
EVENT_DATE = "2026-07-12"
LEGS = {"AAA": "TICKER-AAA", "BBB": "TICKER-BBB"}


def boundary() -> dict:
    return {
        "event_id": EVENT_ID,
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "exact_start_utc": "2026-07-12T12:00:00+00:00",
        "guard_band": {
            "guard_id": "official-point-strict-60s-v1",
            "positive_guard_seconds": 60,
        },
    }


def ledger_boundary() -> dict:
    return {
        "event_id": EVENT_ID,
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "guard_seconds": 60,
        "guarded_cutoff_ts": 1783857540.0,
        "guard_id": "official-point-strict-60s-v1",
        "schedule_can_prove_positive": False,
        "source_record_sha256": "a" * 64,
    }


def unique_row(
    *,
    leg: str = "AAA",
    price: object = 40,
    quantity: object = 5,
    evidence_type: str = "PRICE_REACHED",
    evidence_ts: float = 1783857002.0,
    action_ts: float = 1783857001.0,
    fill_role: str = "first_leg",
    d1: object = -2,
    d2: object | None = None,
    b2_max: object = 1,
    strict: bool | None = None,
) -> dict:
    receipt = "print-1" if evidence_type == "PRICE_REACHED" else "book-1"
    evidence = {
        "book_receipt": "book-1",
        "book_timestamp": evidence_ts,
        "external_bid_cents": (
            int(price) - int(d2)
            if fill_role == "sibling" and d2 is not None
            else 42
        ),
        "external_bid_size": 10.0,
        "external_ask_cents": 41 if evidence_type == "PRICE_REACHED" else 39,
        "external_ask_size": 10.0,
        "action_book_receipt": "trigger-1",
        "action_book_timestamp": action_ts,
        "action_external_bid_cents": (
            int(price) - int(d2)
            if fill_role == "sibling" and d2 is not None
            else 42
        ),
        "action_external_bid_size": 10.0,
        "action_external_ask_cents": 50,
        "action_external_ask_size": 10.0,
    }
    if evidence_type == "PRICE_REACHED":
        evidence.update({
            "print_receipt": receipt,
            "print_timestamp": evidence_ts,
            "print_price_cents": price,
            "print_size": 0.25,
        })
    return {
        "schema_version": adapter.SCHEMA,
        "candidate_id": CANDIDATE,
        "base_candidate_id": PARENT,
        "event_id": EVENT_ID,
        "event_date": EVENT_DATE,
        "category": "ATP_MAIN",
        "leg_id": leg,
        "ticker": LEGS[leg],
        "lawful_guarded_credited_fill": True,
        "quantity": quantity,
        "exposed_X_cents": price,
        "fill_price_cents": price,
        "fill_evidence_type": evidence_type,
        "fill_receipt": receipt,
        "fill_book_receipt": "book-1",
        "fill_evidence": evidence,
        "exposure_interval_id": f"interval-{leg}",
        "action_timestamp": action_ts,
        "action_trigger_receipt": "trigger-1",
        "action_trigger_receipts": ["trigger-1"],
        "evidence_timestamp": evidence_ts,
        "evaluated_right_ts": 1783857540.0,
        "boundary": ledger_boundary(),
        "fill_role": fill_role,
        "first_filled_leg": "AAA",
        "first_fill_timestamp": (
            1783857002.0 if fill_role == "first_leg" else 1783857000.0
        ),
        "realized_first_leg_d1_cents": d1,
        "b2_max_cents": b2_max,
        "sibling_d2_cents": d2,
        "fee_cents": 0,
        "strict_combined_budget_passed": strict,
        "persistence_participated": False,
        "self_trigger_fill": False,
        "selection_basis": "synthetic_contract_fixture",
        "causal_fill_identity": hashlib.sha256(
            f"{leg}-{receipt}".encode()
        ).hexdigest(),
        "selector_receipt_sha256": "b" * 64,
        "source_overlay_sha256": "c" * 64,
        "source_overlay_shard_sha256": "d" * 64,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def adapt(row: dict) -> adapter.T1CreditedFill:
    return adapter.adapt_t1_unique_fill_row(
        row,
        expected_candidates={CANDIDATE},
        candidate_to_parent={CANDIDATE: PARENT},
        expected_legs={(EVENT_ID, leg): ticker for leg, ticker in LEGS.items()},
    )


def reference(leg: str, price: int | None) -> Window1CloseReferenceV2:
    available = price is not None
    return Window1CloseReferenceV2(
        event_id=EVENT_ID,
        event_date=EVENT_DATE,
        leg_id=leg,
        ticker=LEGS[leg],
        available=available,
        window1_close_cents=price,
        reference_ts=1783857530.0 if available else None,
        reference_receipt=f"reference-{leg}" if available else None,
        reference_supporting_receipts=(
            (f"reference-{leg}",) if available else ()
        ),
        reference_source="synthetic_true_print_fixture",
        t8_floor_ts=1783828800.0,
        guarded_cutoff_ts=1783857540.0,
        boundary_source_class="official_exact",
        boundary_guard_id="official-point-strict-60s-v1",
        reason=None if available else "window1_close_reference_missing",
        latest_timestamp_tie_count=1 if available else 0,
        latest_timestamp_distinct_prices=(price,) if available else (),
        authoritative_sequence_available=False,
    )


def event() -> dict:
    return {
        "event_id": EVENT_ID,
        "event_date": EVENT_DATE,
        "category": "ATP_MAIN",
        "scheduled_start_exchange_ts": 1783857600.0,
        "legs": [
            {"leg_id": leg, "ticker": ticker}
            for leg, ticker in LEGS.items()
        ],
    }


class ExactFillAdapterTests(unittest.TestCase):
    def test_exact_five_integer_and_fractional_rejections(self) -> None:
        self.assertEqual(adapt(unique_row()).accounting_quantity, 5)
        for bad in (True, 5.9, 5.0001, float("nan"), float("inf"), 4, 6):
            row = unique_row(quantity=bad)
            with self.assertRaises(adapter.T1ScoringAdapterError):
                adapt(row)

    def test_fractional_and_out_of_range_prices_rejected(self) -> None:
        for bad in (True, 40.9, 0, 100, float("nan"), float("inf")):
            with self.assertRaises(adapter.T1ScoringAdapterError):
                adapt(unique_row(price=bad))

    def test_positive_fractional_print_size_is_lawful(self) -> None:
        row = unique_row()
        row["fill_evidence"]["print_size"] = 0.01
        self.assertEqual(adapt(row).evidence_type, "PRICE_REACHED")

    def test_print_and_strict_ask_credit(self) -> None:
        self.assertEqual(adapt(unique_row()).evidence_type, "PRICE_REACHED")
        strict = unique_row(evidence_type="STRICT_ASK_CERTAIN_FILL")
        self.assertEqual(
            adapt(strict).accounting_fill_price_cents, 40
        )

    def test_ask_equal_x_does_not_credit(self) -> None:
        row = unique_row(evidence_type="STRICT_ASK_CERTAIN_FILL")
        row["fill_evidence"]["external_ask_cents"] = 40
        with self.assertRaises(adapter.T1ScoringAdapterError):
            adapt(row)

    def test_action_and_trigger_chronology(self) -> None:
        with self.assertRaises(adapter.T1ScoringAdapterError):
            adapt(unique_row(action_ts=1783857003.0))
        row = unique_row()
        row["action_trigger_receipts"] = ["trigger-1", "print-1"]
        with self.assertRaises(adapter.T1ScoringAdapterError):
            adapt(row)

    def test_positive_d2_inside_combined_headroom(self) -> None:
        row = unique_row(
            leg="BBB", fill_role="sibling", d1=-3, d2=1,
            b2_max=2, strict=True, evidence_ts=1783857004.0,
        )
        fill = adapt(row)
        self.assertEqual(fill.sibling_d2_cents, 1)
        self.assertTrue(fill.strict_combined_budget_passed)

    def test_same_timestamp_sibling_not_later_rejected(self) -> None:
        row = unique_row(
            leg="BBB", fill_role="sibling", d1=-3, d2=1,
            b2_max=2, strict=True, evidence_ts=1783857000.0,
        )
        with self.assertRaises(adapter.T1ScoringAdapterError):
            adapt(row)

    def test_duplicate_and_conflicting_fill_fail_closed(self) -> None:
        row = unique_row()
        kwargs = {
            "expected_candidates": {CANDIDATE},
            "candidate_to_parent": {CANDIDATE: PARENT},
            "expected_legs": {
                (EVENT_ID, leg): ticker for leg, ticker in LEGS.items()
            },
        }
        with self.assertRaises(adapter.T1ScoringAdapterError):
            adapter.adapt_t1_unique_fill_rows([row, copy.deepcopy(row)], **kwargs)
        conflict = copy.deepcopy(row)
        conflict["fill_price_cents"] = 39
        conflict["exposed_X_cents"] = 39
        conflict["fill_evidence"]["print_price_cents"] = 39
        conflict["causal_fill_identity"] = "e" * 64
        with self.assertRaises(adapter.T1ScoringAdapterError):
            adapter.adapt_t1_unique_fill_rows([row, conflict], **kwargs)


class MetricLawTests(unittest.TestCase):
    def score(
        self, prices: tuple[int, int], closes: tuple[int | None, int | None]
    ) -> dict:
        first = adapt(unique_row(leg="AAA", price=prices[0], d1=-2))
        second_row = unique_row(
            leg="BBB", price=prices[1], fill_role="sibling",
            d1=-2, d2=1, b2_max=1, strict=True,
            evidence_ts=1783857004.0,
        )
        second_row["fill_evidence"]["print_price_cents"] = prices[1]
        second = adapt(second_row)
        return adapter.score_t1_event(
            candidate_id=CANDIDATE,
            parent_candidate_id=PARENT,
            event=event(),
            boundary=boundary(),
            fills_by_leg={"AAA": first, "BBB": second},
            references_by_leg={
                "AAA": reference("AAA", closes[0]),
                "BBB": reference("BBB", closes[1]),
            },
        )

    def test_combined_negative_pc_and_pc_without_ic(self) -> None:
        both_negative = self.score((40, 40), (42, 42))
        self.assertTrue(both_negative["PC"])
        self.assertTrue(both_negative["IC"])
        financed = self.score((40, 45), (44, 44))
        self.assertTrue(financed["PC"])
        self.assertFalse(financed["IC"])

    def test_combined_zero_not_pc(self) -> None:
        row = self.score((40, 40), (41, 39))
        self.assertEqual(row["combined_delta_cents"], 0)
        self.assertFalse(row["PC"])

    def test_S_99_100_and_independence(self) -> None:
        s_true_pc_false = self.score((49, 50), (49, 50))
        self.assertTrue(s_true_pc_false["S"])
        self.assertFalse(s_true_pc_false["PC"])
        s_false_pc_true = self.score((50, 50), (51, 51))
        self.assertFalse(s_false_pc_true["S"])
        self.assertTrue(s_false_pc_true["PC"])

    def test_reference_missing_preserves_C_and_S(self) -> None:
        row = self.score((40, 40), (42, None))
        self.assertTrue(row["C"])
        self.assertTrue(row["S"])
        self.assertIsNone(row["PC"])
        self.assertIsNone(row["IC"])
        self.assertEqual(
            row["classification"],
            "completed_reference_missing_or_ambiguous",
        )

    def test_missing_fill_is_naked_single(self) -> None:
        first = adapt(unique_row(leg="AAA"))
        row = adapter.score_t1_event(
            candidate_id=CANDIDATE,
            parent_candidate_id=PARENT,
            event=event(),
            boundary=boundary(),
            fills_by_leg={"AAA": first},
            references_by_leg={
                "AAA": reference("AAA", 42),
                "BBB": reference("BBB", 42),
            },
        )
        self.assertFalse(row["C"])
        self.assertEqual(row["classification"], "naked_single")

    def test_six_class_conservation(self) -> None:
        rows = []
        classes = list(adapter.CLASSIFICATIONS)
        for index in range(adapter.D_REQUIRED):
            classification = classes[index] if index < len(classes) else "no_fill"
            rows.append({
                "candidate_id": CANDIDATE,
                "event_id": f"E{index:04d}",
                "classification": classification,
                "C": classification.startswith("completed_"),
                "PC": classification == "completed_PC",
                "IC": False,
                "S": classification.startswith("completed_"),
                "combined_entry_cost_cents": 80 if classification.startswith("completed_") else None,
                "combined_delta_cents": -1 if classification == "completed_PC" else None,
                "individual_deltas_cents": [-1, 0] if classification == "completed_PC" else None,
                "event_date": EVENT_DATE,
                "category": "ATP_MAIN",
                "boundary_source_class": "official_exact",
                "legs": [
                    {"evidence_type": "PRICE_REACHED", "t1_sibling_d2_cents": None,
                     "t1_persistence_participated": False},
                    {"evidence_type": "PRICE_REACHED", "t1_sibling_d2_cents": None,
                     "t1_persistence_participated": False},
                ],
            })
        summary = adapter.aggregate_t1_candidate(
            candidate_id=CANDIDATE,
            parent_candidate_id=PARENT,
            rows=rows,
        )
        self.assertEqual(summary["D"], 804)
        self.assertEqual(
            summary["classification_conservation"]["total"], 804
        )


class PackageContractTests(unittest.TestCase):
    def test_candidate_set_and_null_contract(self) -> None:
        spec = json.loads((ROOT / builder.SPEC_REL).read_text())
        self.assertEqual(tuple(spec["candidate_ids"]), builder.CANDIDATES)
        contract = json.loads((ROOT / builder.CONTRACT_REL).read_text())
        self.assertEqual(contract["population"]["D"], 804)
        self.assertIsNone(contract["metrics"])
        self.assertIsNone(contract["performance"])
        self.assertFalse(contract["scored"])

    def test_authorization_is_finite_and_non_self_referential(self) -> None:
        report = (
            "PASS\npackage\nexecution\nbundle\n" + runner.COMMAND_TEMPLATE
        )
        verify_authorization_report_text(
            report,
            package_commit="package",
            execution_id="execution",
            bundle_sha256="bundle",
            command_template=runner.COMMAND_TEMPLATE,
        )
        for wrong in ("package", "execution", "bundle"):
            with self.assertRaises(RunnerError):
                verify_authorization_report_text(
                    report.replace(wrong, "WRONG"),
                    package_commit="package",
                    execution_id="execution",
                    bundle_sha256="bundle",
                    command_template=runner.COMMAND_TEMPLATE,
                )

    def test_lf_crlf_identity_is_portable(self) -> None:
        lf = b"one\ntwo\n"
        crlf = b"one\r\ntwo\r\n"
        self.assertEqual(
            hashlib.sha256(canonical_text_bytes(lf)).hexdigest(),
            hashlib.sha256(canonical_text_bytes(crlf)).hexdigest(),
        )

    def test_builder_does_not_import_or_invoke_scorer(self) -> None:
        text = (ROOT / builder.BUILDER_REL).read_text()
        imports = [
            line for line in text.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        ]
        self.assertFalse(any(
            "window1_range_attack_scorer" in line for line in imports
        ))
        self.assertNotIn("score_event(", text)
        self.assertNotIn("aggregate_candidate(", text)

    def test_frozen_package_when_present(self) -> None:
        package_dir = ROOT / builder.PACKAGE_REL
        if not package_dir.exists():
            self.skipTest("package is generated after focused source tests")
        manifest = json.loads(
            (package_dir / "SCORING_INPUT_MANIFEST.json").read_text()
        )
        self.assertEqual(manifest["D"], 804)
        self.assertEqual(tuple(manifest["candidate_ids"]), runner.CANDIDATE_IDS)
        self.assertIsNone(manifest["metrics"])
        self.assertIsNone(manifest["performance"])
        self.assertFalse(manifest["scored"])
        self.assertFalse((ROOT / runner.RESULTS_DIRECTORY).exists())
        receipt = json.loads(
            (package_dir / "T1_UNIQUE_CREDITED_FILL_DERIVATION_RECEIPT.json").read_text()
        )
        self.assertEqual(len(receipt["candidate_rows"]), 8)
        with gzip.open(
            package_dir / "T1_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz", "rt"
        ) as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        self.assertEqual(
            len(rows), receipt["lawful_guarded_unique_fill_rows"]
        )
        self.assertEqual(
            len({
                (row["candidate_id"], row["event_id"], row["leg_id"])
                for row in rows
            }),
            len(rows),
        )


if __name__ == "__main__":
    unittest.main()
