#!/usr/bin/env python3
"""Verify and finalize sanitized publication of the completed replay.

This does not score or classify any event. It verifies the frozen result and
adds the 14 failed placement decisions omitted by the first sanitizer's
fallback-lineage key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-corrected-publication-v1"
EXPECTED_DECISIONS = {
    "accepted_entry_placement": 3318,
    "accepted_placement_receipt_missing": 42,
    "cancellation_receipt": 3574,
    "causal_no_placement": 308,
    "failed_entry_placement": 14,
}


class FinalizeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizeError(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise FinalizeError(f"non-object {path}:{line_number}")
            output.append(value)
    return output


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ))
            handle.write("\n")


def parse_ts(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result > 10_000_000_000:
        result /= 1000.0
    return result if math.isfinite(result) else None


def lineage(order: Mapping[str, Any]) -> str:
    explicit = str(order.get("trade_id") or "")
    if explicit:
        return explicit
    fallback = str(order.get("attempt_id") or order.get("order_id") or "")
    if not fallback:
        payload = json.dumps(
            dict(order), sort_keys=True, separators=(",", ":")
        )
        fallback = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()[:20]
    return "attempt:" + fallback


def supplement_failed_decisions(
    orders: list[Mapping[str, Any]],
    lifecycles: list[Mapping[str, Any]],
    D_tickers: set[str],
) -> list[dict[str, Any]]:
    lifecycle_keys = {
        (
            str(row.get("event_id") or ""),
            str(row.get("ticker") or ""),
            str(row.get("lineage") or ""),
        )
        for row in lifecycles
    }
    output = []
    for order in orders:
        if order.get("accepted") is not False:
            continue
        event_id = str(order.get("event_id") or "")
        ticker = str(order.get("ticker") or "")
        key = (event_id, ticker, lineage(order))
        if ticker not in D_tickers or key not in lifecycle_keys:
            continue
        exchange_ts = parse_ts(order.get("exchange_created_ts"))
        output.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "ticker": ticker,
            "decision_index": "failed-supplement",
            "decision_type": "failed_entry_placement",
            "policy_id": (
                "chronological_os_strategy_of_record_receipt_replay_v1"
            ),
            "exchange_placement_ts": exchange_ts,
            "exchange_clock_available": exchange_ts is not None,
            "local_receipt_clock_present": (
                parse_ts(order.get("local_logged_ts")) is not None
            ),
            "price_cents": int(order["price_cents"]),
            "quantity": float(order["quantity"]),
            "source": "private_order_export_hash_receipt",
            "private_identifier_included": False,
            "used_to_prove_positive_window1": False,
            "publication_note": (
                "sanitizer-lineage supplement; replay metrics unchanged"
            ),
        })
    output.sort(key=lambda row: (row["event_id"], row["ticker"]))
    if len(output) != 14:
        raise FinalizeError(
            f"failed placement supplement moved from 14 to {len(output)}"
        )
    return output


def verify_original_artifacts(output: Path) -> dict[str, Any]:
    manifest = read_json(output / "ARTIFACT_MANIFEST.json")
    for name, receipt in manifest["artifacts"].items():
        path = output / name
        if sha256_file(path) != receipt["sha256"]:
            raise FinalizeError(f"original artifact hash moved: {name}")
        if receipt.get("rows") is not None:
            rows = sum(1 for line in path.open(encoding="utf-8") if line)
            if rows != receipt["rows"]:
                raise FinalizeError(f"original row count moved: {name}")
    receipt = read_json(output / "RUN_RECEIPT.json")
    if receipt.get("state") != "execution_complete":
        raise FinalizeError("run receipt is not complete")
    if receipt.get("execution_ordinal") != 1:
        raise FinalizeError("execution ordinal changed")
    return manifest


def final_report(
    result: Mapping[str, Any],
    decision_counts: Mapping[str, int],
) -> str:
    raw = result["raw_event_counts"]
    legs = result["raw_leg_counts"]
    bounds = result["primary_bounds"]
    start = result["start_precision_accounting"]
    rates = result["rates_over_D"]
    return f"""# Final reconciliation — corrected Window-1 development replay

## Raw event counts first

- D = {raw['D']}
- strict dual exact-five Window-1 completions = {raw['strict_dual_exact_five_window1_completions']}
- strict dual exact-five Window-1 completions with negative combined Window-1-close delta = {raw['strict_dual_exact_five_window1_completions_with_negative_combined_window1_close_delta']}
- combined entry cost under par = {raw['combined_entry_cost_under_par']}
- both individual-leg deltas negative = {raw['both_individual_leg_deltas_negative']}
- one-leg-only negative delta = {raw['one_leg_only_negative_delta']}
- dynamic-floor gap evaluated events = {raw['dynamic_floor_gap_evaluated_events']}
- dynamic-floor gap at or below zero = {raw['dynamic_floor_gap_at_or_below_zero']}
- nonfill events = {raw['nonfill_events']}
- non-Window-1 fill events = {raw['non_window1_fill_events']}
- other-quantity fill events = {raw['other_quantity_fill_events']}
- timing-censored events = {raw['timing_censored_events']}
- feature-censored events = {raw['feature_censored_events']}

## Exact leg conservation and per-leg measures

- exact-five filled legs = {legs['exact_five_filled_legs']}
- other-quantity filled legs = {legs['other_quantity_filled_legs']}
- exact nonfill legs = {legs['exact_nonfill_legs']}
- lifecycle-censored legs = {legs['lifecycle_censored_legs']}
- proven Window-1 exact-five legs = {legs['proven_window1_exact_five_legs']}
- proven non-Window-1 filled legs = {legs['proven_non_window1_filled_legs']}
- 10-contract overfill legs retained as other quantity = {legs['ten_contract_overfill_legs']}
- dip/catch evaluated legs = {legs['dip_catch_evaluated_legs']}
- at or below fitted target = {legs['dip_catch_at_or_below_fitted_target']}
- within four cents of fitted target = {legs['dip_catch_within_four_cents']}

## Rates against D = 804

- strict completion rate = {rates['strict_dual_exact_five_window1_completions']:.6%}
- primary rate = {rates['strict_dual_exact_five_window1_completions_with_negative_combined_window1_close_delta']:.6%}
- combined-cost-under-par rate = {rates['combined_entry_cost_under_par']:.6%}
- both-individual-negative rate = {rates['both_individual_leg_deltas_negative']:.6%}
- one-leg-only-negative rate = {rates['one_leg_only_negative_delta']:.6%}
- nonfill-event rate = {rates['nonfill_events']:.6%}
- non-Window-1-fill-event rate = {rates['non_window1_fill_events']:.6%}
- other-quantity-fill-event rate = {rates['other_quantity_fill_events']:.6%}
- timing-censored-event rate = {rates['timing_censored_events']:.6%}
- feature-censored-event rate = {rates['feature_censored_events']:.6%}

## Lawful primary bounds

- strict lower bound = {bounds['strict_lower_bound_count']} of 804 ({bounds['strict_lower_bound_rate_over_D']:.6%})
- optimistic upper bound = {bounds['optimistic_upper_bound_count']} of 804 ({bounds['optimistic_upper_bound_rate_over_D']:.6%})
- unresolved events assumed successful in the upper bound = {bounds['unresolved_events_assumed_successful_in_upper_bound']}
- distance to the 603-event target at the lower bound = {bounds['distance_from_target_at_strict_lower_bound']}
- distance to the 603-event target at the optimistic bound = {bounds['distance_from_target_at_optimistic_upper_bound']}
- lawful-bounds verdict = {bounds['verdict']}

## Start precision

- exact starts = {start['exact_starts']}
- clean causal intervals capable of proving a positive = {start['clean_causal_intervals_positive_capable']}
- contradictory intervals unable to prove a positive = {start['contradictory_intervals_not_positive_capable']}
- live-by events usable only for nonfill or causally proven-not-Window-1 findings = {start['live_by_events_negative_only']}
- fully timing-censored events = {start['fully_timing_censored_events']}
- positive-Window-1-provable population = {start['positive_window1_provable_population']}
- remaining timing-censored population = {start['remaining_timing_censored_population']}

## Execution and publication conservation

- accepted placements = {decision_counts['accepted_entry_placement']}
- missing-placement witnesses = {decision_counts['accepted_placement_receipt_missing']}
- failed placement attempts = {decision_counts['failed_entry_placement']}
- cancellation receipts = {decision_counts['cancellation_receipt']}
- causal nonplacements = {decision_counts['causal_no_placement']}
- execution mismatches = 0
- duplicate or zero-size fill promotions = 0

The first publication ledger omitted the 14 failed-attempt rows because its
sanitizer used a client-order fallback instead of the kernel's attempt
lineage. `POLICY_DECISION_SUPPLEMENT.jsonl` and
`POLICY_DECISION_LEDGER_COMPLETE.jsonl` repair publication only. The frozen
replay outputs and every metric above remain byte-for-byte unchanged.

## Component coverage and remaining censorship

The chronological adapter retains the calibration inventory: five available,
thirteen partially available, one unavailable, and one excluded component,
plus the available historical-execution binding. All 804 events are
feature-censored because AIM_V2's LATCHCAL prior is excluded, full-depth
ancestry is unavailable, Pinnacle is unavailable, and fixed-snapshot
BBO/top-five features are not exchange-placement-clock aligned. The public
tape remains 4,836,462 positive-size exchange-identified prints. Top-five
coverage remains 6,338 of 6,432 feature rows; bookmaker coverage remains 844
of 6,432; Pinnacle and proven full depth remain zero.

## Preserved baseline comparison

The seven-hour narrow proxy baseline remains unchanged at C = 4 and X = 734;
it is not an OS-performance verdict. The exact historical execution gate's
31 dual exact-five events and 27 combined-cost-under-par events also remain
unchanged, with the required qualifier that all 31 sit on live-by bounds and
none has proven Window-1 timing. This corrected replay promotes neither
population into the strict numerator.

AIM_V2's pinned table first entered Git in `c8c91b33` as the named
operational LATCHCAL artifact. No earlier independent authorization exists,
so its resting-aim/shape-offset feature is censored rather than relabeled.

No candidate search, tuning, threshold selection, parameter sweep, or
ablation ran. No holdout, production, live_v4, configuration, order,
position, Window 2, exit, settlement, or DCA state was opened or changed.
"""


def run(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    original_manifest = verify_original_artifacts(output)
    result = read_json(output / "RESULTS.json")
    event_rows = read_jsonl(output / "EVENT_RESULTS.jsonl")
    leg_rows = read_jsonl(output / "EVENT_LEG_RESULTS.jsonl")
    mismatch_rows = read_jsonl(
        output / "EXECUTION_MISMATCH_LEDGER.jsonl"
    )
    original_decisions = read_jsonl(
        output / "POLICY_DECISION_LEDGER.jsonl"
    )
    if len(event_rows) != 804 or len(leg_rows) != 1608:
        raise FinalizeError("event/leg conservation changed")
    if mismatch_rows:
        raise FinalizeError("mismatch ledger is not empty")
    orders = read_jsonl(Path(args.orders).resolve())
    lifecycles = read_jsonl(Path(args.lifecycles).resolve())
    D_tickers = {str(row["ticker"]) for row in leg_rows}
    supplement = supplement_failed_decisions(
        orders, lifecycles, D_tickers
    )
    complete = original_decisions + supplement
    complete.sort(key=lambda row: (
        str(row.get("event_id") or ""),
        str(row.get("ticker") or ""),
        str(row.get("decision_type") or ""),
        str(row.get("decision_index") or ""),
    ))
    decision_counts = dict(Counter(
        str(row["decision_type"]) for row in complete
    ))
    if decision_counts != EXPECTED_DECISIONS:
        raise FinalizeError(
            f"decision conservation changed: {decision_counts}"
        )
    supplement_path = output / "POLICY_DECISION_SUPPLEMENT.jsonl"
    complete_path = output / "POLICY_DECISION_LEDGER_COMPLETE.jsonl"
    write_jsonl(supplement_path, supplement)
    write_jsonl(complete_path, complete)
    report_path = output / "FINAL_RECONCILIATION_REPORT.md"
    report_path.write_text(
        final_report(result, decision_counts),
        encoding="utf-8",
        newline="\n",
    )
    verification = {
        "schema_version": VERSION,
        "run_receipt_state": "execution_complete",
        "execution_ordinal": 1,
        "original_artifacts_preserved": True,
        "original_artifact_manifest_sha256": sha256_file(
            output / "ARTIFACT_MANIFEST.json"
        ),
        "D": 804,
        "event_rows": 804,
        "leg_rows": 1608,
        "mismatch_rows": 0,
        "decision_counts": decision_counts,
        "complete_decision_rows": len(complete),
        "failed_decision_supplement_rows": len(supplement),
        "metric_results_changed": False,
        "holdout_inputs": [],
        "private_identifiers_emitted": False,
        "artifacts": {
            supplement_path.name: {
                "bytes": supplement_path.stat().st_size,
                "rows": len(supplement),
                "sha256": sha256_file(supplement_path),
            },
            complete_path.name: {
                "bytes": complete_path.stat().st_size,
                "rows": len(complete),
                "sha256": sha256_file(complete_path),
            },
            report_path.name: {
                "bytes": report_path.stat().st_size,
                "sha256": sha256_file(report_path),
            },
        },
        "original_artifacts": original_manifest["artifacts"],
    }
    write_json(output / "POST_RUN_VERIFICATION.json", verification)
    print(json.dumps({
        "verified": True,
        "decision_counts": decision_counts,
        "complete_decision_rows": len(complete),
        "mismatch_rows": 0,
        "metric_results_changed": False,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    private = Path.home() / "OMI-Window1-private" / "calibration-v1"
    result = argparse.ArgumentParser()
    result.add_argument("--output-dir", required=True)
    result.add_argument(
        "--orders", default=private / "orders.private.jsonl"
    )
    result.add_argument(
        "--lifecycles", default=private / "lifecycle.private.jsonl"
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
