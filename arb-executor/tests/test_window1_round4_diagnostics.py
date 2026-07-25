from __future__ import annotations

import ast
import gzip
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round4_diagnostics as diagnostics  # noqa: E402


OUTPUT = ROOT / ".claude/window1_round4_prerun_20260725"


def test_primary_opportunity_uses_print_volume_not_estimated_queue():
    intervals = [{
        "start_ts": 10,
        "end_ts": 20,
        "price_cents": 40,
        "queue_ahead": 2,
    }]
    prints = [
        {
            "timestamp": 11,
            "price_cents": 40,
            "size": 6,
            "taker_side": "no",
            "receipt_identity": "one",
        },
        {
            "timestamp": 12,
            "price_cents": 40,
            "size": 1,
            "taker_side": "no",
            "receipt_identity": "two",
        },
    ]
    proof = diagnostics._proved_five_opportunities(
        intervals, prints[:1], 20
    )
    assert len(proof) == 1
    assert proof[0]["proved_at_ts"] == 11
    assert proof[0]["estimated_queue_applied_to_primary"] is False
    facts = diagnostics._execution_reach_facts(
        intervals, prints[:1], 20
    )
    assert facts["primary_exact_five_proved"] is True
    assert facts["primary_print_volume_class"] == (
        "at_least_five_qualifying_contracts_exact_five_primary_fill"
    )
    assert facts["queue_sensitivity_diagnostic_only"][
        "any_five_after_estimated_queue"
    ] is False
    assert facts["queue_sensitivity_diagnostic_only"][
        "primary_result_altered"
    ] is False


def test_qualifying_volume_below_five_remains_partial():
    intervals = [{
        "start_ts": 10,
        "end_ts": 20,
        "price_cents": 40,
        "queue_ahead": 0,
    }]
    prints = [
        {
            "timestamp": 11,
            "price_cents": 40,
            "size": 2,
            "taker_side": "no",
            "receipt_identity": "one",
        },
        {
            "timestamp": 12,
            "price_cents": 39,
            "size": 2,
            "taker_side": "no",
            "receipt_identity": "two",
        },
    ]
    assert diagnostics._proved_five_opportunities(
        intervals, prints, 20
    ) == []
    facts = diagnostics._execution_reach_facts(
        intervals, prints, 20
    )
    assert facts["price_reached"] is True
    assert facts["maximum_primary_qualifying_executed_volume"] == 4
    assert facts["five_qualifying_contracts_reached"] is False
    assert facts["primary_print_volume_class"] == (
        "qualifying_volume_below_five_before_cutoff"
    )


def test_primary_volume_accumulates_across_successive_order_intervals():
    intervals = [
        {
            "start_ts": 10,
            "end_ts": 12,
            "price_cents": 40,
            "queue_ahead": 100,
        },
        {
            "start_ts": 12,
            "end_ts": 20,
            "price_cents": 41,
            "queue_ahead": 200,
        },
    ]
    prints = [
        {
            "timestamp": 11,
            "price_cents": 40,
            "size": 2,
            "taker_side": "no",
            "receipt_identity": "one",
        },
        {
            "timestamp": 13,
            "price_cents": 41,
            "size": 3,
            "taker_side": "no",
            "receipt_identity": "two",
        },
    ]
    proof = diagnostics._proved_five_opportunities(
        intervals, prints, 20
    )
    assert len(proof) == 1
    assert proof[0]["proved_at_ts"] == 13
    assert proof[0]["cumulative_qualifying_executed_volume"] == 5
    facts = diagnostics._execution_reach_facts(
        intervals, prints, 20
    )
    assert facts["total_primary_qualifying_executed_volume"] == 5
    assert facts["primary_exact_five_proved"] is True
    assert facts["queue_sensitivity_diagnostic_only"][
        "total_volume_after_estimated_queue"
    ] == 0


def test_post_cutoff_print_cannot_prove_window1_opportunity():
    intervals = [{
        "start_ts": 10,
        "end_ts": 30,
        "price_cents": 40,
        "queue_ahead": 0,
    }]
    prints = [{
        "timestamp": 21,
        "price_cents": 40,
        "size": 10,
        "taker_side": "no",
        "receipt_identity": "late",
    }]
    assert diagnostics._proved_five_opportunities(
        intervals, prints, 20
    ) == []
    facts = diagnostics._execution_reach_facts(
        intervals, prints, 20
    )
    assert facts["primary_print_volume_class"] == (
        "no_qualifying_executed_volume_at_order_price"
    )


def test_pair_opportunity_uses_separate_volume_proofs_not_realized_fills():
    legs = [
        {
            "leg_id": "A",
            "lawful_five_contract_opportunity_proofs": [{
                "proved_at_ts": 11,
                "order_price_cents": 40,
                "receipt_identity": "a",
            }],
            "oracle_diagnostic_only": {
                "window1_close_reference_cents": 45,
            },
        },
        {
            "leg_id": "B",
            "lawful_five_contract_opportunity_proofs": [{
                "proved_at_ts": 19,
                "order_price_cents": 51,
                "receipt_identity": "b",
            }],
            "oracle_diagnostic_only": {
                "window1_close_reference_cents": 50,
            },
        },
    ]
    value = diagnostics._pair_opportunity_summary(legs)
    assert value["two_separate_lawful_five_contract_times"] is True
    assert (
        value[
            "separately_timed_prices_combined_ex_post_"
            "delta_strictly_negative"
        ]
        is True
    )
    assert value["best_separately_timed_pair_witness"][
        "combined_ex_post_delta_cents"
    ] == -4
    assert value["unreachable_from_policy"] is True


def test_calibration_is_descriptive_and_never_tunes():
    rows = [
        {
            "candidate_id": "a",
            "tournament_class": "ATP_MAIN",
            "start_source_class": "official_exact",
            "macro_band": "ATP_MAIN-B1",
            "causal_b_i_cents": -2,
            "ex_post_d_i_cents": 1,
        },
        {
            "candidate_id": "a",
            "tournament_class": "ATP_MAIN",
            "start_source_class": "official_exact",
            "macro_band": "ATP_MAIN-B1",
            "causal_b_i_cents": 1,
            "ex_post_d_i_cents": -1,
        },
    ]
    value = diagnostics._calibration_summary(rows)
    assert value["policy_threshold_tuned_from_calibration"] is False
    assert value["overall"]["false_positive_proxy_count"] == 1
    assert value["overall"]["false_negative_proxy_count"] == 1


def test_policy_source_does_not_import_diagnostic_module():
    source = (
        ROOT / "arb-executor/analysis/window1_round4_instrument.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any("diagnostic" in name for name in names)


def test_real_freeze_conserves_804_and_never_populates_metrics():
    manifest = json.loads(
        (OUTPUT / "ROUND4_PRE_RUN_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    receipt = json.loads(
        (OUTPUT / "ROUND4_DIAGNOSTIC_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )
    capability = json.loads(
        (OUTPUT / "ROUND4_REAL_CAPABILITY.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["development_scope"]["D"] == 804
    assert manifest["development_scope"]["candidate_count"] == 2
    assert capability["candidate_event_stream_count"] == 1608
    assert receipt["event_rows"] == 804
    assert receipt["all_stream_metrics_null"] is True
    assert manifest["candidate_scoring_performed"] is False
    assert manifest["C_PC_S_IC_populated"] is False
    with gzip.open(
        OUTPUT / "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz",
        "rt",
        encoding="utf-8",
    ) as handle:
        rows = 0
        for line in handle:
            stream = json.loads(line)["stream"]
            assert stream["scored"] is False
            assert stream["metrics"] is None
            rows += 1
    assert rows == 1608


def test_opportunity_ledger_has_804_rows_and_null_final_metrics():
    rows = 0
    manifest = json.loads(
        (OUTPUT / "WINDOW1_OPPORTUNITY_LEDGER_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(manifest["ordered_shards"]) == 2
    for shard in manifest["ordered_shards"]:
        with gzip.open(
            ROOT / shard["path"], "rt", encoding="utf-8"
        ) as handle:
            shard_rows = 0
            for line in handle:
                row = json.loads(line)
                assert row["benchmark_metrics"] is None
                assert row["scored"] is False
                assert len(row["candidate_entries"]) == 2
                for entry in row["candidate_entries"].values():
                    pair = entry["pair_diagnostic"]
                    assert pair["final_C"] is None
                    assert pair["final_PC"] is None
                    assert pair["final_S"] is None
                    assert pair["final_IC"] is None
                    assert pair["metrics"] is None
                rows += 1
                shard_rows += 1
            assert shard_rows == shard["row_count"] == 402
    assert rows == 804


def test_round3_control_census_matches_supplied_headroom_counts():
    value = json.loads(
        (OUTPUT / "ORACLE_FALSE_NEGATIVE_CENSUS.json").read_text(
            encoding="utf-8"
        )
    )
    assert value["supplied_selected_candidate_counts_reproduced"] is True
    expected = value["supplied_count_comparison"]["expected"]
    actual = value["supplied_count_comparison"]["actual"]
    assert actual == expected
    assert actual == {
        "allowance_at_least_1": 75,
        "allowance_at_least_2": 68,
        "allowance_at_least_3": 59,
        "allowance_at_least_5": 40,
        "allowance_median": 4,
        "filled_leg_ex_post_d1_negative_count": 92,
        "later_logged_strict_price_reach": 12,
        "naked_single_count": 278,
        "post_cutoff_sibling_fills": 53,
    }
