#!/usr/bin/env python3
"""One-shot corrected Window-1 development replay.

This instrument reproduces the chronological OS strategy of record from
actual historical placement, fill, cancel, and causal nonplacement receipts.
It does not create counterfactual orders and cannot fall back to the earlier
walk/touch proxy grid.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

from window1_execution_kernel import (  # noqa: E402
    canonical_private_fill,
    replay_historical_execution,
)


VERSION = "window1-corrected-os-replay-v1"
D = 804
LEGS = 1608
LOT = 5.0
PAR = 100.0
TARGET_COUNT = 603
EXPECTED_START_DECOMPOSITION = {
    "exact_starts": 29,
    "clean_causal_intervals_positive_capable": 47,
    "contradictory_intervals_not_positive_capable": 32,
    "live_by_events_negative_only": 625,
    "fully_timing_censored_events": 71,
    "positive_window1_provable_population": 76,
    "remaining_timing_censored_population": 728,
}
EXPECTED_EXECUTION_COUNTS = {
    "exact_filled_five": 258,
    "exact_filled_other_quantity": 12,
    "exact_nonfill": 870,
    "censored": 468,
}
PROHIBITED_PROXY_POLICIES = {
    "park_touch_simultaneous_hold",
    "walk_law_simultaneous_hold",
    "walk_law_firstfill_reaim_touch",
    "causal_stack_simultaneous_reaim",
}


class ReplayError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReplayError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ReplayError(
                    f"expected JSON object: {path}:{line_number}"
                )
            output.append(value)
    return output


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ))
            handle.write("\n")


def parse_ts(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        if result > 10_000_000_000:
            result /= 1000.0
        return result if math.isfinite(result) else None
    try:
        stamp = dt.datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.timestamp()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        text=True,
    ).strip()


def verify_frozen_inputs(
    freeze: Mapping[str, Any],
    logical_paths: Mapping[str, Path],
) -> None:
    if freeze.get("schema_version") != "window1-corrected-freeze-v1":
        raise ReplayError("unknown or missing corrected freeze")
    if freeze.get("frozen") is not True:
        raise ReplayError("freeze receipt is not frozen")
    if freeze.get("holdout_inputs") != []:
        raise ReplayError("freeze receipt includes a holdout input")
    for item in freeze.get("inputs") or []:
        logical = str(item.get("logical_source") or "")
        path = logical_paths.get(logical)
        if path is None:
            raise ReplayError(f"unresolved frozen input: {logical}")
        if "holdout" in logical.lower() or "holdout" in str(path).lower():
            raise ReplayError("holdout path refused")
        if not path.is_file():
            raise ReplayError(f"missing frozen input: {logical}")
        actual = sha256_file(path)
        if actual != item.get("sha256"):
            raise ReplayError(
                f"frozen input hash mismatch: {logical}: {actual}"
            )
    code_sha = str(freeze.get("code_sha") or "")
    if len(code_sha) != 40:
        raise ReplayError("invalid frozen code SHA")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", code_sha, git_head()],
        cwd=REPO,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ReplayError("frozen code SHA is not an ancestor of HEAD")


def bind_policy(
    candidate: Mapping[str, Any],
    allowlist: Mapping[str, Any],
    adapter: Mapping[str, Any],
) -> None:
    policy_id = str(
        (candidate.get("policy") or {}).get("policy_id") or ""
    )
    allowed_policies = set(allowlist.get("allowed_policy_ids") or [])
    if policy_id not in allowed_policies:
        raise ReplayError(f"policy is not allowlisted: {policy_id}")
    if policy_id in PROHIBITED_PROXY_POLICIES:
        raise ReplayError("simplified proxy policy refused")
    if policy_id in set(allowlist.get("forbidden_policy_ids") or []):
        raise ReplayError("forbidden policy refused")
    if (candidate.get("policy") or {}).get(
        "simplified_proxy_allowed"
    ) is not False:
        raise ReplayError("candidate does not mechanically forbid proxying")
    if adapter.get("adapter_id") != (
        "chronological-window1-os-receipt-adapter-v1"
    ):
        raise ReplayError("unexpected OS adapter version")
    if (adapter.get("laws") or {}).get(
        "silent_proxy_substitution_allowed"
    ) is not False:
        raise ReplayError("adapter permits silent proxy substitution")
    allowed_components = set(
        allowlist.get("allowed_execution_components") or []
    )
    declared_components = set(
        adapter.get("metric_executable_components") or []
    ) | set(adapter.get("feature_coverage_components") or [])
    candidate_components = set(
        candidate.get("required_execution_components") or []
    ) | set(candidate.get("feature_coverage_components") or [])
    if candidate_components != declared_components:
        raise ReplayError(
            "candidate and adapter component bindings differ"
        )
    unknown = declared_components - allowed_components
    if unknown:
        raise ReplayError(
            f"adapter component is not allowlisted: {sorted(unknown)}"
        )
    if "aim_v2" in declared_components:
        raise ReplayError("AIM_V2 component is executable")
    prohibited_hashes = set(
        allowlist.get("prohibited_input_sha256") or []
    )
    serialized_candidate = json.dumps(candidate, sort_keys=True)
    serialized_adapter = json.dumps(adapter, sort_keys=True)
    for digest in prohibited_hashes:
        if digest in serialized_adapter:
            raise ReplayError("prohibited prior is bound by adapter")
        aim = candidate.get("aim_v2") or {}
        if (
            digest in serialized_candidate
            and not (
                aim.get("status") == "excluded"
                and aim.get("shape_prior_consumed") is False
                and aim.get("excluded_sha256") == digest
            )
        ):
            raise ReplayError("prohibited prior is bound by candidate")


def start_proof(row: Mapping[str, Any]) -> dict[str, Any]:
    state = str(row.get("start_state") or "")
    precision = str(row.get("precision_class") or "")
    if state:
        precision = {
            "verified_exact": "exact_official_or_milestone",
            "bounded_start_interval": "causal_start_interval",
            "bounded_live_by_timestamp": "causal_live_by_bound",
            "schedule_only_censored": "schedule_only_bound",
        }.get(state, "")
    exact = parse_ts(
        row.get("verified_start_utc") or row.get("exact_start_utc")
    )
    interval = (
        row.get("start_interval_utc") or row.get("interval_utc") or {}
    )
    lower = parse_ts(interval.get("lower_exclusive"))
    upper = parse_ts(interval.get("upper_inclusive"))
    contradictory = row.get("interval_contradiction") is True
    if precision == "exact_official_or_milestone":
        positive_capable = exact is not None
        cutoff = parse_ts(row.get("safe_prestart_cutoff_utc")) or exact
        cutoff_source = str(
            row.get("selected_source") or ""
        )
        cutoff_basis = str(
            row.get("safe_prestart_cutoff_time_basis")
            or row.get("verified_start_time_basis")
            or row.get("timestamp_basis") or ""
        )
        cutoff_inclusive = row.get(
            "safe_prestart_cutoff_inclusive"
        ) is not False
        if cutoff is not None and not cutoff_inclusive:
            cutoff = math.nextafter(cutoff, -math.inf)
        positive_class = "exact_start"
        known_live_by = (
            parse_ts(row.get("known_live_by_utc")) or exact
        )
    elif precision == "causal_start_interval" and not contradictory:
        cutoff = (
            parse_ts(row.get("safe_prestart_cutoff_utc")) or lower
        )
        positive_capable = cutoff is not None and upper is not None
        cutoff_source = str(
            row.get("not_live_through_source") or ""
        )
        cutoff_basis = str(
            row.get("safe_prestart_cutoff_time_basis")
            or row.get("not_live_through_time_basis")
            or ""
        )
        cutoff_inclusive = row.get(
            "safe_prestart_cutoff_inclusive"
        ) is not False
        if cutoff is not None and not cutoff_inclusive:
            cutoff = math.nextafter(cutoff, -math.inf)
        positive_class = "clean_causal_interval"
        known_live_by = (
            parse_ts(row.get("known_live_by_utc")) or upper
        )
    elif precision == "causal_start_interval":
        positive_capable = False
        cutoff = None
        cutoff_source = ""
        cutoff_basis = ""
        cutoff_inclusive = False
        positive_class = "contradictory_interval"
        known_live_by = (
            parse_ts(row.get("known_live_by_utc")) or upper
        )
    elif precision == "causal_live_by_bound":
        positive_capable = False
        cutoff = None
        cutoff_source = ""
        cutoff_basis = ""
        cutoff_inclusive = False
        positive_class = "live_by_negative_only"
        known_live_by = (
            parse_ts(row.get("known_live_by_utc")) or upper
        )
    elif precision == "schedule_only_bound":
        positive_capable = False
        cutoff = None
        cutoff_source = ""
        cutoff_basis = ""
        cutoff_inclusive = False
        positive_class = "fully_timing_censored"
        known_live_by = None
    else:
        raise ReplayError(f"unknown start precision: {precision}")
    known_live_basis = (
        str(
            row.get("known_live_by_time_basis")
            or row.get("timestamp_basis") or ""
        )
        if known_live_by is not None else None
    )
    known_live_usable = bool(
        known_live_by is not None
        and known_live_basis in {
            "official_provider_start_timestamp",
            "public_trade_exchange_created_time",
            "exchange_transition_timestamp",
        }
    )
    return {
        "precision_class": precision,
        "positive_precision_class": positive_class,
        "positive_window1_capable": positive_capable,
        "safe_prestart_cutoff_exchange_ts": cutoff,
        "safe_prestart_cutoff_source": (
            cutoff_source
            if cutoff is not None else None
        ),
        "safe_prestart_cutoff_timestamp_basis": (
            cutoff_basis
            if cutoff is not None else None
        ),
        "safe_prestart_cutoff_inclusive": cutoff_inclusive,
        "known_live_by_exchange_ts": known_live_by,
        "known_live_by_source": (
            str(
                row.get("known_live_by_source")
                or row.get("selected_source") or ""
            )
            if known_live_by is not None else None
        ),
        "known_live_by_timestamp_basis": known_live_basis,
        "known_live_by_usable_for_post_start_ruling": (
            known_live_usable
        ),
        "schedule_used_for_classification": False,
        "local_receipt_used_for_classification": False,
        "timing_censored_for_positive": not positive_capable,
    }


def start_decomposition(
    starts: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    def precision_for(row: Mapping[str, Any]) -> str:
        if row.get("precision_class"):
            return str(row["precision_class"])
        return {
            "verified_exact": "exact_official_or_milestone",
            "bounded_start_interval": "causal_start_interval",
            "bounded_live_by_timestamp": "causal_live_by_bound",
            "schedule_only_censored": "schedule_only_bound",
        }.get(str(row.get("start_state") or ""), "")

    precision = Counter(precision_for(row) for row in starts)
    intervals = [
        row for row in starts
        if precision_for(row) == "causal_start_interval"
    ]
    clean = sum(
        row.get("interval_contradiction") is not True for row in intervals
    )
    contradictory = len(intervals) - clean
    result = {
        "exact_starts": precision["exact_official_or_milestone"],
        "clean_causal_intervals_positive_capable": clean,
        "contradictory_intervals_not_positive_capable": contradictory,
        "live_by_events_negative_only": precision[
            "causal_live_by_bound"
        ],
        "fully_timing_censored_events": precision[
            "schedule_only_bound"
        ],
        "positive_window1_provable_population": (
            precision["exact_official_or_milestone"] + clean
        ),
        "remaining_timing_censored_population": (
            len(starts)
            - precision["exact_official_or_milestone"]
            - clean
        ),
    }
    if result != EXPECTED_START_DECOMPOSITION:
        raise ReplayError(f"start decomposition changed: {result}")
    return result


def load_true_print_references(
    path: Path,
    cutoff_by_ticker: Mapping[str, float],
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    references: dict[str, dict[str, Any]] = {}
    seen_ids: set[str] = set()
    rows = 0
    positive_rows = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            rows += 1
            row = json.loads(line)
            trade_id = str(row.get("trade_id") or "")
            ticker = str(row.get("ticker") or "")
            timestamp = parse_ts(row.get("exchange_ts"))
            try:
                price = int(row.get("price_cents"))
                size = float(row.get("size"))
            except (TypeError, ValueError) as exc:
                raise ReplayError(
                    f"invalid true-print row {line_number}"
                ) from exc
            if (
                not trade_id or trade_id in seen_ids
                or not ticker or timestamp is None
                or row.get("true_print") is not True
                or not 1 <= price <= 99 or size <= 0
            ):
                raise ReplayError(
                    f"noncanonical true-print row {line_number}"
                )
            seen_ids.add(trade_id)
            positive_rows += 1
            cutoff = cutoff_by_ticker.get(ticker)
            if cutoff is None or timestamp > cutoff:
                continue
            prior = references.get(ticker)
            key = (timestamp, trade_id)
            if prior is None:
                references[ticker] = {
                    "reference_cents": price,
                    "reference_exchange_ts": timestamp,
                    "reference_trade_id_retained": False,
                    "reference_identity_source": "exchange_trade_id",
                    "observed_min_cents_through_cutoff": price,
                    "_key": key,
                }
            else:
                prior["observed_min_cents_through_cutoff"] = min(
                    int(prior["observed_min_cents_through_cutoff"]), price
                )
                if key > prior["_key"]:
                    prior.update({
                        "reference_cents": price,
                        "reference_exchange_ts": timestamp,
                        "_key": key,
                    })
    for value in references.values():
        value.pop("_key", None)
    return references, {
        "rows": rows,
        "positive_size_rows": positive_rows,
        "distinct_exchange_trade_ids": len(seen_ids),
        "referenced_tickers": len(references),
    }


def aggregate_feature_sources(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("ticker") or "")].append(row)
    output: dict[str, dict[str, Any]] = {}
    for ticker, values in grouped.items():
        top5 = sum(row.get("top5_available") is True for row in values)
        bookmaker = sum(
            row.get("bookmaker_available") is True for row in values
        )
        output[ticker] = {
            "feature_row_count": len(values),
            "bbo_top5": {
                "status": "partially_available" if top5 else "unavailable",
                "available_rows": top5,
                "source": "premarket_ticks_top5",
                "decision_clock_aligned": False,
                "consumed_for_policy": False,
            },
            "bookmaker": {
                "status": (
                    "partially_available" if bookmaker else "unavailable"
                ),
                "available_rows": bookmaker,
                "source": "macro_projection.db causal projection",
                "consumed_for_policy": False,
            },
            "pinnacle": {
                "status": "unavailable",
                "available_rows": 0,
                "consumed_for_policy": False,
            },
            "shape_prior": {
                "status": "excluded",
                "available_rows": 0,
                "source": None,
                "reason": "AIM_V2-only lineage",
                "consumed_for_policy": False,
            },
            "raw_full_depth": {
                "status": "unavailable",
                "available_rows": 0,
                "reason": "no proven gap-free snapshot ancestry",
                "consumed_for_policy": False,
            },
        }
    return output


def frozen_logical_paths(runtime: Mapping[str, Path]) -> dict[str, Path]:
    fit = REPO / ".claude" / "window1_20260721"
    calibration = REPO / ".claude" / "window1_calibration_20260723"
    documents = REPO / "arb-executor" / "docs" / "research" / "window1"
    analysis = REPO / "arb-executor" / "analysis"
    return {
        "calibration_runner": (
            analysis / "window1_execution_calibration.py"
        ),
        "decisions": runtime["decisions"],
        "events": runtime["events"],
        "execution_kernel": analysis / "window1_execution_kernel.py",
        "expected_execution_summary": (
            fit / "LIFECYCLE_VALIDATION_SUMMARY.json"
        ),
        "expected_legs": runtime["expected_legs"],
        "feature_coverage": fit / "WINDOW1_FEATURE_COVERAGE.json",
        "fills": runtime["fills"],
        "future_fit_runner": analysis / "window1_fit_benchmark.py",
        "orders": runtime["orders"],
        "os_contract": (
            documents / "WINDOW1_OS_ADAPTER_CONTRACT.json"
        ),
        "private_lifecycles": runtime["lifecycles"],
        "real_start_ledger": runtime["starts"],
        "real_start_summary": fit / "REAL_START_SUMMARY.json",
        "source_coverage": fit / "SOURCE_COVERAGE_SUMMARY.json",
        "tape_reconciliation": (
            calibration / "CAUSAL_TAPE_RECONCILIATION.json"
        ),
        "trade_reconciliation_runner": (
            analysis / "window1_ws_trade_reconcile.py"
        ),
        "ws_summary": fit / "WS_DEPTH_COVERAGE_SUMMARY.json",
        "corrected_replay_runner": Path(__file__).resolve(),
        "corrected_candidate": runtime["candidate"],
        "policy_allowlist": runtime["allowlist"],
        "execution_adapter": runtime["adapter"],
        "metric_contract": runtime["metric_contract"],
        "calibration_adapter": runtime["calibration_adapter"],
        "feature_matrix": runtime["feature_matrix"],
        "public_true_print_tape": runtime["public_prints"],
        "recut_cells": runtime["recut_cells"],
        "micmay_forensic": (
            fit / "POST_SAMPLE_MICMAY_FORENSIC.json"
        ),
        "micmay_manifest": (
            fit / "EVIDENCE_RECOVERY_ARTIFACT_MANIFEST.json"
        ),
        "independent_cross_review": (
            documents / "independent-audit"
            / "CALIBRATION_GATE_CROSS_REVIEW.md"
        ),
    }


def order_lineage(row: Mapping[str, Any]) -> str:
    value = row.get("trade_id") or row.get("client_order_id")
    return str(value or "")


def build_receipt_indexes(
    orders: Sequence[Mapping[str, Any]],
    fills: Sequence[Mapping[str, Any]],
    lifecycles: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    order_by_id = {
        str(row.get("order_id")): row
        for row in orders
        if row.get("accepted") is True and row.get("order_id")
    }
    failed_by_key: dict[
        tuple[str, str, str], list[Mapping[str, Any]]
    ] = defaultdict(list)
    for row in orders:
        if row.get("accepted") is False:
            failed_by_key[(
                str(row.get("event_id") or ""),
                str(row.get("ticker") or ""),
                order_lineage(row),
            )].append(row)
    fill_by_id: dict[str, dict[str, Any]] = {}
    for row in fills:
        value = canonical_private_fill(row)
        fill_id = str(value["fill_id"])
        if fill_id in fill_by_id and fill_by_id[fill_id] != value:
            raise ReplayError("conflicting private fill identity")
        fill_by_id[fill_id] = value
    lifecycle_by_ticker: dict[str, list[Mapping[str, Any]]] = (
        defaultdict(list)
    )
    for row in lifecycles:
        lifecycle_by_ticker[str(row.get("ticker") or "")].append(row)
    decisions_by_ticker: dict[str, list[Mapping[str, Any]]] = (
        defaultdict(list)
    )
    for row in decisions:
        decisions_by_ticker[str(row.get("ticker") or "")].append(row)
    return {
        "order_by_id": order_by_id,
        "failed_by_key": failed_by_key,
        "fill_by_id": fill_by_id,
        "lifecycle_by_ticker": lifecycle_by_ticker,
        "decisions_by_ticker": decisions_by_ticker,
    }


def sanitized_policy_decisions(
    event_id: str,
    ticker: str,
    lifecycles: Sequence[Mapping[str, Any]],
    indexes: Mapping[str, Any],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    order_by_id = indexes["order_by_id"]
    failed_by_key = indexes["failed_by_key"]
    decisions_by_ticker = indexes["decisions_by_ticker"]
    for lifecycle in lifecycles:
        lineage = str(lifecycle.get("lineage") or "")
        for order_id in lifecycle.get("accepted_order_ids") or []:
            order = order_by_id.get(str(order_id))
            if order is None:
                output.append({
                    "decision_type": "accepted_placement_receipt_missing",
                    "policy_id": (
                        "chronological_os_strategy_of_record_"
                        "receipt_replay_v1"
                    ),
                    "exchange_placement_ts": None,
                    "exchange_clock_available": False,
                    "local_receipt_clock_present": False,
                    "price_cents": None,
                    "quantity": None,
                    "source": "private_order_export_hash_receipt",
                    "private_identifier_included": False,
                    "used_to_prove_positive_window1": False,
                })
                continue
            exchange_ts = parse_ts(order.get("exchange_created_ts"))
            phase = (
                (order.get("window_receipt") or {}).get("phase")
                if isinstance(order.get("window_receipt"), dict) else None
            )
            output.append({
                "decision_type": "accepted_entry_placement",
                "policy_id": (
                    "chronological_os_strategy_of_record_receipt_replay_v1"
                ),
                "exchange_placement_ts": exchange_ts,
                "exchange_clock_available": exchange_ts is not None,
                "local_receipt_clock_present": (
                    parse_ts(order.get("local_logged_ts")) is not None
                ),
                "price_cents": int(order.get("price_cents")),
                "quantity": float(order.get("quantity")),
                "historical_window_label": phase,
                "historical_window_label_used_for_metric": False,
                "source": "private_order_export_hash_receipt",
                "private_identifier_included": False,
                "used_to_prove_positive_window1": exchange_ts is not None,
            })
        key = (event_id, ticker, lineage)
        for order in failed_by_key.get(key, []):
            output.append({
                "decision_type": "failed_entry_placement",
                "policy_id": (
                    "chronological_os_strategy_of_record_receipt_replay_v1"
                ),
                "exchange_placement_ts": parse_ts(
                    order.get("exchange_created_ts")
                ),
                "exchange_clock_available": (
                    parse_ts(order.get("exchange_created_ts")) is not None
                ),
                "local_receipt_clock_present": (
                    parse_ts(order.get("local_logged_ts")) is not None
                ),
                "price_cents": int(order.get("price_cents")),
                "quantity": float(order.get("quantity")),
                "source": "private_order_export_hash_receipt",
                "private_identifier_included": False,
                "used_to_prove_positive_window1": False,
            })
        for receipts in (
            lifecycle.get("cancellation_evidence") or {}
        ).values():
            for receipt in receipts:
                output.append({
                    "decision_type": "cancellation_receipt",
                    "policy_id": (
                        "chronological_os_strategy_of_record_"
                        "receipt_replay_v1"
                    ),
                    "exchange_placement_ts": None,
                    "exchange_clock_available": False,
                    "local_receipt_clock_present": (
                        parse_ts(receipt.get("local_logged_ts")) is not None
                    ),
                    "success": receipt.get("success") is True,
                    "reason": str(receipt.get("label") or ""),
                    "source": "private_lifecycle_cancellation_receipt",
                    "private_identifier_included": False,
                    "used_to_prove_positive_window1": False,
                })
    for row in decisions_by_ticker.get(ticker, []):
        output.append({
            "decision_type": "causal_no_placement",
            "policy_id": (
                "chronological_os_strategy_of_record_receipt_replay_v1"
            ),
            "exchange_placement_ts": parse_ts(row.get("exchange_ts")),
            "exchange_clock_available": (
                parse_ts(row.get("exchange_ts")) is not None
            ),
            "local_receipt_clock_present": (
                parse_ts(row.get("local_logged_ts")) is not None
            ),
            "reason": str(row.get("reason") or ""),
            "source": str(row.get("source") or ""),
            "private_identifier_included": False,
            "used_to_prove_positive_window1": False,
        })
    return output


def build_leg_receipt_detail(
    base: Mapping[str, Any],
    start: Mapping[str, Any],
    lifecycles: Sequence[Mapping[str, Any]],
    indexes: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
    feature_source: Mapping[str, Any] | None,
    recut_cells: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ticker = str(base["ticker"])
    event_id = str(base["event_id"])
    status = str(base["replayed_status"])
    fill_by_id = indexes["fill_by_id"]
    order_by_id = indexes["order_by_id"]
    attributable_fills: list[dict[str, Any]] = []
    unattributed_fill_count = 0
    accepted_ids: set[str] = set()
    cancel_count = 0
    successful_cancel_count = 0
    first_fill_sibling_feature_partial = False
    for lifecycle in lifecycles:
        is_unattributed = (
            lifecycle.get("status")
            == "censored_unattributed_private_fill"
        )
        ids = {
            str(value)
            for value in lifecycle.get("accepted_order_ids") or []
        }
        accepted_ids.update(ids)
        for receipts in (
            lifecycle.get("cancellation_evidence") or {}
        ).values():
            cancel_count += len(receipts)
            successful_cancel_count += sum(
                receipt.get("success") is True for receipt in receipts
            )
        if (
            lifecycle.get("first_fill_exchange_ts") not in (None, "")
            and ids
        ):
            first_fill_sibling_feature_partial = True
        for fill_id in lifecycle.get("official_fill_ids") or []:
            fill = fill_by_id.get(str(fill_id))
            if fill is None:
                raise ReplayError("private lifecycle fill receipt disappeared")
            if is_unattributed:
                unattributed_fill_count += 1
            else:
                attributable_fills.append(fill)
    attributable_fills.sort(
        key=lambda value: (value["exchange_ts"], value["fill_id"])
    )
    fill_quantity = sum(
        float(value["quantity"]) for value in attributable_fills
    )
    cumulative = 0.0
    completion_ts = None
    for fill in attributable_fills:
        cumulative += float(fill["quantity"])
        if cumulative >= LOT - 1e-9:
            completion_ts = float(fill["exchange_ts"])
            break
    first_fill_ts = (
        float(attributable_fills[0]["exchange_ts"])
        if attributable_fills else None
    )
    placement_clock_count = 0
    placement_causality_count = 0
    filled_order_count = 0
    filled_order_ids: set[str] = set()
    causal_clock_issues: list[str] = []
    for fill in attributable_fills:
        order_id = str(fill["order_id"])
        filled_order_ids.add(order_id)
        order = order_by_id.get(order_id)
        if order is None:
            causal_clock_issues.append(
                "filled_order_missing_private_placement_receipt"
            )
            continue
        placement_ts = parse_ts(order.get("exchange_created_ts"))
        if placement_ts is None:
            causal_clock_issues.append(
                "filled_order_missing_exchange_placement_clock"
            )
            continue
        placement_clock_count += 1
        if placement_ts <= float(fill["exchange_ts"]):
            placement_causality_count += 1
        else:
            causal_clock_issues.append(
                "fill_exchange_clock_precedes_placement_exchange_clock"
            )
    filled_order_count = len(filled_order_ids)
    fill_receipt_count = len(attributable_fills)
    all_filled_orders_clocked = bool(attributable_fills) and all(
        (
            order_by_id.get(str(fill["order_id"])) is not None
            and parse_ts(
                order_by_id[str(fill["order_id"])].get(
                    "exchange_created_ts"
                )
            ) is not None
            and parse_ts(
                order_by_id[str(fill["order_id"])].get(
                    "exchange_created_ts"
                )
            ) <= float(fill["exchange_ts"])
        )
        for fill in attributable_fills
    )
    proof = start_proof(start)
    cutoff = proof["safe_prestart_cutoff_exchange_ts"]
    known_live_by = proof["known_live_by_exchange_ts"]
    exact_five = status == "exact_filled_five" and math.isclose(
        fill_quantity, LOT, abs_tol=1e-9
    )
    proven_window1 = bool(
        exact_five
        and all_filled_orders_clocked
        and first_fill_ts is not None
        and completion_ts is not None
        and cutoff is not None
        and completion_ts <= cutoff
    )
    proven_non_window1 = bool(
        status in {"exact_filled_five", "exact_filled_other_quantity"}
        and completion_ts is not None
        and (
            (
                proof["known_live_by_usable_for_post_start_ruling"]
                and known_live_by is not None
                and completion_ts >= known_live_by
            )
            or (cutoff is not None and completion_ts > cutoff)
        )
    )
    if status == "exact_nonfill":
        ruling = "exact_nonfill"
    elif status == "exact_filled_other_quantity":
        ruling = "other_quantity_fill"
    elif proven_window1:
        ruling = "proven_exact_five_window1_fill"
    elif proven_non_window1:
        ruling = "proven_non_window1_fill"
    elif status == "exact_filled_five":
        ruling = "exact_five_fill_timing_or_placement_censored"
    else:
        ruling = "lifecycle_censored"
    reference_cents = (
        int(reference["reference_cents"]) if reference else None
    )
    vwap = (
        float(base["official_fill_vwap_cents"])
        if base.get("official_fill_vwap_cents") is not None else None
    )
    delta = (
        vwap - reference_cents
        if proven_window1 and vwap is not None
        and reference_cents is not None else None
    )
    recut = None
    fitted_target = None
    dip_catch_gap = None
    category = str(base["category"])
    if proven_window1 and reference_cents is not None:
        recut = (
            (recut_cells.get(category) or {}).get(str(reference_cents))
        )
        if recut is not None and vwap is not None:
            fitted_target = (
                reference_cents - float(recut["edge_p50"])
            )
            dip_catch_gap = vwap - fitted_target
    features = dict(feature_source or {
        "feature_row_count": 0,
        "bbo_top5": {"status": "unavailable"},
        "bookmaker": {"status": "unavailable"},
        "pinnacle": {"status": "unavailable"},
        "shape_prior": {"status": "excluded"},
        "raw_full_depth": {"status": "unavailable"},
    })
    feature_censors = [
        "aim_v2_shape_prior_excluded",
        "raw_full_depth_unavailable",
        "pinnacle_unavailable",
        "policy_decision_feature_vector_not_exchange_clock_aligned",
    ]
    if (features.get("bbo_top5") or {}).get("status") == "unavailable":
        feature_censors.append("bbo_top5_unavailable")
    if (features.get("bookmaker") or {}).get("status") == "unavailable":
        feature_censors.append("bookmaker_unavailable")
    policy_decisions = sanitized_policy_decisions(
        event_id, ticker, lifecycles, indexes
    )
    row = {
        "schema_version": VERSION,
        "event_id": event_id,
        "event_date": str(base["event_date"]),
        "category": category,
        "ticker": ticker,
        "policy_id": (
            "chronological_os_strategy_of_record_receipt_replay_v1"
        ),
        "source_lifecycle_status": status,
        "official_fill_quantity": fill_quantity,
        "official_fill_vwap_cents": vwap,
        "exact_five_quantity": exact_five,
        "other_quantity_fill": status == "exact_filled_other_quantity",
        "ten_contract_overfill": (
            status == "exact_filled_other_quantity"
            and math.isclose(fill_quantity, 10.0, abs_tol=1e-9)
        ),
        "exact_nonfill": status == "exact_nonfill",
        "window1_ruling": ruling,
        "proven_window1_exact_five": proven_window1,
        "proven_non_window1_fill": proven_non_window1,
        "start_boundary_proof": proof,
        "placement_fill_causality": {
            "accepted_placement_receipt_count": len(accepted_ids),
            "filled_order_count": filled_order_count,
            "fill_receipt_count": fill_receipt_count,
            "fill_exchange_clock_count": fill_receipt_count,
            "filled_order_exchange_placement_clock_count": (
                placement_clock_count
            ),
            "placement_precedes_fill_count": placement_causality_count,
            "all_filled_orders_have_causal_exchange_clock": (
                all_filled_orders_clocked
            ),
            "first_fill_exchange_ts": first_fill_ts,
            "completion_exchange_ts": completion_ts,
            "local_receipt_used_for_positive": False,
            "schedule_used_for_positive_or_post_start": False,
            "issues": sorted(set(causal_clock_issues)),
        },
        "nonfill_causality": {
            "causal_nonplacement_receipt_count": int(
                base.get("causal_nonplacement_receipt_count") or 0
            ),
            "cancellation_receipt_count": cancel_count,
            "successful_cancellation_receipt_count": (
                successful_cancel_count
            ),
        },
        "window1_close_reference": (
            dict(reference) if reference else None
        ),
        "individual_leg_delta_cents": delta,
        "dynamic_floor_leg": {
            "recut_cell_available": recut is not None,
            "edge_p50_cents": (
                float(recut["edge_p50"]) if recut is not None else None
            ),
            "fitted_target_cents": fitted_target,
            "dip_catch_gap_cents": dip_catch_gap,
            "at_or_below_fitted_target": (
                dip_catch_gap <= 0 if dip_catch_gap is not None else None
            ),
            "within_four_cents_of_fitted_target": (
                dip_catch_gap <= 4 if dip_catch_gap is not None else None
            ),
        },
        "first_fill_sibling_response": {
            "status": (
                "partially_available"
                if first_fill_sibling_feature_partial else "unavailable"
            ),
            "source": "private lifecycle and cancellation receipts",
            "consumed_for_policy": False,
        },
        "feature_sources": features,
        "feature_censors": feature_censors,
        "feature_censored": bool(feature_censors),
        "policy_decision_count": len(policy_decisions),
        "unattributed_private_fill_receipt_count": (
            unattributed_fill_count
        ),
        "possible_exact_five_upper_bound": bool(
            base.get("possible_exact_five_upper_bound")
        ),
        "private_identifiers_included": False,
    }
    decision_rows = [
        {
            "schema_version": VERSION,
            "event_id": event_id,
            "ticker": ticker,
            "decision_index": index,
            **decision,
        }
        for index, decision in enumerate(policy_decisions)
    ]
    return row, decision_rows


def evaluate_events(
    starts: Sequence[Mapping[str, Any]],
    legs: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start_by_event = {
        str(row["event_id"]): row for row in starts
    }
    by_event: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in legs:
        by_event[str(row["event_id"])].append(row)
    event_rows: list[dict[str, Any]] = []
    for event_id in sorted(start_by_event):
        leg_rows = sorted(
            by_event[event_id], key=lambda value: str(value["ticker"])
        )
        if len(leg_rows) != 2:
            raise ReplayError(f"event leg count changed: {event_id}")
        strict_c = all(
            row["proven_window1_exact_five"] for row in leg_rows
        )
        costs = [
            row["official_fill_vwap_cents"] for row in leg_rows
        ]
        combined = (
            sum(float(value) for value in costs)
            if strict_c and all(value is not None for value in costs)
            else None
        )
        deltas = [
            row["individual_leg_delta_cents"] for row in leg_rows
        ]
        reference_complete = strict_c and all(
            value is not None for value in deltas
        )
        combined_delta = (
            sum(float(value) for value in deltas)
            if reference_complete else None
        )
        primary = bool(
            strict_c and combined_delta is not None
            and combined_delta < 0
        )
        cost_under_par = bool(
            strict_c and combined is not None and combined < PAR
        )
        both_negative = bool(
            reference_complete and all(float(value) < 0 for value in deltas)
        )
        one_leg_negative = bool(
            reference_complete
            and sum(float(value) < 0 for value in deltas) == 1
        )
        dynamic_parts = [
            row["dynamic_floor_leg"] for row in leg_rows
        ]
        dynamic_floor = (
            sum(float(value["fitted_target_cents"])
                for value in dynamic_parts)
            if strict_c and all(
                value["fitted_target_cents"] is not None
                for value in dynamic_parts
            ) else None
        )
        possible_pair = all(
            row["possible_exact_five_upper_bound"] for row in leg_rows
        )
        primary_resolved = bool(
            primary
            or (
                strict_c and combined_delta is not None
                and combined_delta >= 0
            )
            or not possible_pair
        )
        proof = start_proof(start_by_event[event_id])
        row = {
            "schema_version": VERSION,
            "event_id": event_id,
            "event_date": str(leg_rows[0]["event_date"]),
            "category": str(leg_rows[0]["category"]),
            "D_member": True,
            "strict_dual_exact_five_window1_completion": strict_c,
            "primary_negative_combined_window1_close_delta": primary,
            "combined_entry_cost_under_par": cost_under_par,
            "both_individual_leg_deltas_negative": both_negative,
            "one_leg_only_negative_delta": one_leg_negative,
            "combined_entry_cost_cents": combined,
            "combined_window1_close_delta_cents": combined_delta,
            "dynamic_floor_cents": dynamic_floor,
            "dynamic_floor_gap_cents": (
                combined - dynamic_floor
                if combined is not None and dynamic_floor is not None
                else None
            ),
            "has_exact_nonfill_leg": any(
                value["exact_nonfill"] for value in leg_rows
            ),
            "has_proven_non_window1_fill_leg": any(
                value["proven_non_window1_fill"] for value in leg_rows
            ),
            "has_other_quantity_fill_leg": any(
                value["other_quantity_fill"] for value in leg_rows
            ),
            "timing_censored_event": (
                proof["timing_censored_for_positive"]
            ),
            "feature_censored_event": any(
                value["feature_censored"] for value in leg_rows
            ),
            "possible_primary_success_upper_bound": (
                primary or (possible_pair and not primary_resolved)
            ),
            "primary_ruling_resolved": primary_resolved,
            "leg_tickers": [
                str(value["ticker"]) for value in leg_rows
            ],
        }
        event_rows.append(row)
    raw = {
        "D": D,
        "strict_dual_exact_five_window1_completions": sum(
            row["strict_dual_exact_five_window1_completion"]
            for row in event_rows
        ),
        "strict_dual_exact_five_window1_completions_with_negative_combined_window1_close_delta": sum(
            row["primary_negative_combined_window1_close_delta"]
            for row in event_rows
        ),
        "combined_entry_cost_under_par": sum(
            row["combined_entry_cost_under_par"] for row in event_rows
        ),
        "both_individual_leg_deltas_negative": sum(
            row["both_individual_leg_deltas_negative"]
            for row in event_rows
        ),
        "one_leg_only_negative_delta": sum(
            row["one_leg_only_negative_delta"] for row in event_rows
        ),
        "dynamic_floor_gap_evaluated_events": sum(
            row["dynamic_floor_gap_cents"] is not None
            for row in event_rows
        ),
        "dynamic_floor_gap_at_or_below_zero": sum(
            row["dynamic_floor_gap_cents"] is not None
            and row["dynamic_floor_gap_cents"] <= 0
            for row in event_rows
        ),
        "nonfill_events": sum(
            row["has_exact_nonfill_leg"] for row in event_rows
        ),
        "non_window1_fill_events": sum(
            row["has_proven_non_window1_fill_leg"]
            for row in event_rows
        ),
        "other_quantity_fill_events": sum(
            row["has_other_quantity_fill_leg"] for row in event_rows
        ),
        "timing_censored_events": sum(
            row["timing_censored_event"] for row in event_rows
        ),
        "feature_censored_events": sum(
            row["feature_censored_event"] for row in event_rows
        ),
    }
    dip_rows = [
        row for row in legs
        if row["dynamic_floor_leg"]["dip_catch_gap_cents"] is not None
    ]
    leg_raw = {
        "required_legs": LEGS,
        "exact_five_filled_legs": sum(
            row["source_lifecycle_status"] == "exact_filled_five"
            for row in legs
        ),
        "other_quantity_filled_legs": sum(
            row["source_lifecycle_status"]
            == "exact_filled_other_quantity" for row in legs
        ),
        "exact_nonfill_legs": sum(
            row["source_lifecycle_status"] == "exact_nonfill"
            for row in legs
        ),
        "lifecycle_censored_legs": sum(
            row["source_lifecycle_status"] == "censored"
            for row in legs
        ),
        "proven_window1_exact_five_legs": sum(
            row["proven_window1_exact_five"] for row in legs
        ),
        "proven_non_window1_filled_legs": sum(
            row["proven_non_window1_fill"] for row in legs
        ),
        "ten_contract_overfill_legs": sum(
            row["ten_contract_overfill"] for row in legs
        ),
        "dip_catch_evaluated_legs": len(dip_rows),
        "dip_catch_at_or_below_fitted_target": sum(
            row["dynamic_floor_leg"]["at_or_below_fitted_target"]
            is True for row in dip_rows
        ),
        "dip_catch_within_four_cents": sum(
            row["dynamic_floor_leg"][
                "within_four_cents_of_fitted_target"
            ] is True for row in dip_rows
        ),
    }
    primary_lower = raw[
        "strict_dual_exact_five_window1_completions_with_negative_combined_window1_close_delta"
    ]
    primary_upper = sum(
        row["possible_primary_success_upper_bound"] for row in event_rows
    )
    if primary_lower >= TARGET_COUNT:
        verdict = "target_proven_passed"
    elif primary_upper < TARGET_COUNT:
        verdict = "target_proven_failed"
    else:
        verdict = "target_not_decidable_with_current_evidence"
    bounds = {
        "strict_lower_bound_count": primary_lower,
        "strict_lower_bound_rate_over_D": primary_lower / D,
        "optimistic_upper_bound_count": primary_upper,
        "optimistic_upper_bound_rate_over_D": primary_upper / D,
        "unresolved_events_assumed_successful_in_upper_bound": (
            primary_upper - primary_lower
        ),
        "target_count": TARGET_COUNT,
        "distance_from_target_at_strict_lower_bound": (
            TARGET_COUNT - primary_lower
        ),
        "distance_from_target_at_optimistic_upper_bound": (
            TARGET_COUNT - primary_upper
        ),
        "verdict": verdict,
    }
    rates = {
        key: value / D
        for key, value in raw.items()
        if key != "D" and isinstance(value, int)
    }
    return event_rows, {
        "raw_event_counts": raw,
        "raw_leg_counts": leg_raw,
        "rates_over_D": rates,
        "primary_bounds": bounds,
    }


def component_coverage(
    calibration_adapter: Mapping[str, Any],
    legs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    components = []
    for component in calibration_adapter.get("components") or []:
        row = {
            "component_id": component["component_id"],
            "calibration_status": component["status"],
            "replay_status": component["status"],
            "consumed_for_policy": False,
            "consumed_for_metric": False,
            "source_receipts": component.get("source_receipts") or [],
            "reason": component.get("reason"),
        }
        component_id = row["component_id"]
        if component_id in {
            "pair_law", "true_print_tape", "real_start",
            "own_order_fingerprints_and_contributed_volume",
        }:
            row["consumed_for_metric"] = True
        if component_id == "dynamic_floor_and_recut_cells":
            row["consumed_for_metric"] = True
        if component_id == "dual_divot_steering_and_catch":
            row["consumed_for_metric"] = True
        if component_id == "aim_v2":
            row.update({
                "replay_status": "excluded",
                "consumed_for_policy": False,
                "consumed_for_metric": False,
                "reason": "AIM_V2-only prior lineage; excluded",
            })
        if component_id == "shape_corpus":
            row.update({
                "replay_status": "partially_available",
                "consumed_for_policy": False,
                "reason": (
                    "generic corpus retained, but frozen per-row shape "
                    "fields depend on excluded AIM_V2 prior"
                ),
            })
        components.append(row)
    components.append({
        "component_id": "historical_execution",
        "calibration_status": "available",
        "replay_status": "available",
        "consumed_for_policy": True,
        "consumed_for_metric": True,
        "source_receipts": [
            "private orders hash",
            "private fills hash",
            "private lifecycles hash",
            "causal nonplacement ledger hash",
        ],
        "reason": "actual chronological OS placement/fill/nonfill receipts",
    })
    return {
        "schema_version": VERSION,
        "component_count": len(components),
        "components": components,
        "event_feature_censored_count": sum(
            row["feature_censored_event"] for row in []
        ),
        "leg_feature_censored_count": sum(
            row["feature_censored"] for row in legs
        ),
        "aim_v2_consumed": False,
        "full_depth_consumed": False,
        "proxy_substitution_used": False,
    }


def markdown_report(summary: Mapping[str, Any]) -> str:
    raw = summary["raw_event_counts"]
    legs = summary["raw_leg_counts"]
    bounds = summary["primary_bounds"]
    start = summary["start_precision_accounting"]
    lines = [
        "# Corrected Window-1 deterministic development replay",
        "",
        "## Raw counts first",
        "",
        f"- D = {raw['D']}",
        (
            "- strict dual exact-five Window-1 completions = "
            f"{raw['strict_dual_exact_five_window1_completions']}"
        ),
        (
            "- strict dual exact-five Window-1 completions with negative "
            "combined Window-1-close delta = "
            f"{raw['strict_dual_exact_five_window1_completions_with_negative_combined_window1_close_delta']}"
        ),
        (
            "- combined entry cost under par = "
            f"{raw['combined_entry_cost_under_par']}"
        ),
        (
            "- both individual-leg deltas negative = "
            f"{raw['both_individual_leg_deltas_negative']}"
        ),
        (
            "- one-leg-only negative delta = "
            f"{raw['one_leg_only_negative_delta']}"
        ),
        (
            "- dynamic-floor gap evaluated events = "
            f"{raw['dynamic_floor_gap_evaluated_events']}"
        ),
        (
            "- dynamic-floor gap at or below zero = "
            f"{raw['dynamic_floor_gap_at_or_below_zero']}"
        ),
        (
            "- per-leg dip/catch evaluated = "
            f"{legs['dip_catch_evaluated_legs']}"
        ),
        (
            "- per-leg at or below fitted target = "
            f"{legs['dip_catch_at_or_below_fitted_target']}"
        ),
        (
            "- per-leg within four cents of fitted target = "
            f"{legs['dip_catch_within_four_cents']}"
        ),
        f"- nonfill events = {raw['nonfill_events']}",
        (
            "- non-Window-1 fill events = "
            f"{raw['non_window1_fill_events']}"
        ),
        (
            "- other-quantity fill events = "
            f"{raw['other_quantity_fill_events']}"
        ),
        (
            "- timing-censored events = "
            f"{raw['timing_censored_events']}"
        ),
        (
            "- feature-censored events = "
            f"{raw['feature_censored_events']}"
        ),
        "",
        "## Start precision",
        "",
        f"- exact starts = {start['exact_starts']}",
        (
            "- clean causal intervals capable of proving a positive = "
            f"{start['clean_causal_intervals_positive_capable']}"
        ),
        (
            "- contradictory intervals unable to prove a positive = "
            f"{start['contradictory_intervals_not_positive_capable']}"
        ),
        (
            "- live-by events usable only for nonfill or proven-not-"
            f"Window-1 = {start['live_by_events_negative_only']}"
        ),
        (
            "- fully timing-censored events = "
            f"{start['fully_timing_censored_events']}"
        ),
        (
            "- positive-Window-1-provable population = "
            f"{start['positive_window1_provable_population']}"
        ),
        (
            "- remaining timing-censored population = "
            f"{start['remaining_timing_censored_population']}"
        ),
        "",
        "## Primary bounds against D = 804",
        "",
        (
            "- strict lower bound = "
            f"{bounds['strict_lower_bound_count']} "
            f"({bounds['strict_lower_bound_rate_over_D']:.6%})"
        ),
        (
            "- optimistic upper bound = "
            f"{bounds['optimistic_upper_bound_count']} "
            f"({bounds['optimistic_upper_bound_rate_over_D']:.6%})"
        ),
        (
            "- distance from the 75% target at the strict lower bound = "
            f"{bounds['distance_from_target_at_strict_lower_bound']} events"
        ),
        (
            "- distance from the 75% target at the optimistic upper bound = "
            f"{bounds['distance_from_target_at_optimistic_upper_bound']} events"
        ),
        f"- lawful-bounds verdict = {bounds['verdict']}",
        "",
        "Every rate in `RESULTS.json` is also printed against D = 804. "
        "Censored events remain in D and are not observed successes.",
        "",
        "## Causality and contamination",
        "",
        "Positive Window-1 classifications require an exchange placement "
        "clock for every filled order, exchange fill/completion clocks, and "
        "an exact or clean-interval safe pre-start cutoff. Schedule values, "
        "local receipt clocks, missing completion clocks, and hardcoded "
        "defaults prove neither a positive nor a post-start ruling.",
        "",
        "AIM_V2 and its byte-identical LATCHCAL prior are excluded. The "
        "independent recut-cell surface is consumed only for dynamic-floor "
        "and dip/catch reporting. No walk-law or touch proxy is executable.",
        "",
        "The historical 10-contract overfill remains an other-quantity "
        "fill and never counts toward exact-five completion.",
        "",
        "No holdout, Window 2, exit, settlement, DCA, production, live_v4, "
        "configuration, order, or position input was consumed or changed.",
        "",
    ]
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    if output.exists():
        raise ReplayError(
            "one-shot output directory already exists; replay refused"
        )
    paths = {
        name: Path(value).resolve()
        for name, value in vars(args).items()
        if name not in {"output_dir", "execute_frozen_replay"}
        and value is not None
    }
    freeze = read_json(paths["freeze"])
    logical_paths = frozen_logical_paths(paths)
    verify_frozen_inputs(freeze, logical_paths)
    candidate = read_json(paths["candidate"])
    allowlist = read_json(paths["allowlist"])
    adapter = read_json(paths["adapter"])
    bind_policy(candidate, allowlist, adapter)
    if args.execute_frozen_replay != (
        "EXECUTE-ONE-CORRECTED-804-DEVELOPMENT-REPLAY"
    ):
        raise ReplayError("explicit one-shot execution token missing")
    output.mkdir(parents=True)
    write_json(output / "RUN_RECEIPT.json", {
        "schema_version": VERSION,
        "state": "execution_started",
        "execution_ordinal": 1,
        "candidate_spec_sha256": sha256_file(paths["candidate"]),
        "freeze_sha256": sha256_file(paths["freeze"]),
        "code_sha": freeze["code_sha"],
        "D": D,
        "holdout_inputs": [],
    })

    events = read_jsonl(paths["events"])
    expected_legs = read_jsonl(paths["expected_legs"])
    starts = read_jsonl(paths["starts"])
    orders = read_jsonl(paths["orders"])
    fills = read_jsonl(paths["fills"])
    lifecycles = read_jsonl(paths["lifecycles"])
    decisions = read_jsonl(paths["decisions"])
    feature_matrix = read_jsonl(paths["feature_matrix"])
    recut_cells = read_json(paths["recut_cells"])
    if len(events) != D or len(starts) != D or len(expected_legs) != LEGS:
        raise ReplayError("immutable D/leg denominator changed")
    start_counts = start_decomposition(starts)
    replay_legs, kernel_mismatches, kernel_stats = (
        replay_historical_execution(
            events, orders, fills, lifecycles, decisions, expected_legs
        )
    )
    if kernel_mismatches:
        write_jsonl(
            output / "EXECUTION_MISMATCH_LEDGER.jsonl",
            kernel_mismatches,
        )
        raise ReplayError("historical execution mismatch; scoring refused")
    actual_status = dict(Counter(
        row["replayed_status"] for row in replay_legs
    ))
    if actual_status != EXPECTED_EXECUTION_COUNTS:
        raise ReplayError(
            f"execution status conservation changed: {actual_status}"
        )
    by_expected = {
        str(row["ticker"]): row for row in expected_legs
    }
    for row in replay_legs:
        expected = by_expected[str(row["ticker"])]
        row["possible_exact_five_upper_bound"] = bool(
            expected.get("possible_five_contract_upper_bound")
            or row["replayed_status"] == "exact_filled_five"
        )
    start_by_event = {
        str(row["event_id"]): row for row in starts
    }
    cutoff_by_ticker: dict[str, float] = {}
    for start in starts:
        proof = start_proof(start)
        cutoff = proof["safe_prestart_cutoff_exchange_ts"]
        if cutoff is not None:
            for leg in start.get("legs") or []:
                cutoff_by_ticker[str(leg["ticker"])] = cutoff
    references, tape_stats = load_true_print_references(
        paths["public_prints"], cutoff_by_ticker
    )
    if (
        tape_stats["rows"] != 4_836_462
        or tape_stats["positive_size_rows"] != 4_836_462
        or tape_stats["distinct_exchange_trade_ids"] != 4_836_462
    ):
        raise ReplayError(f"true-print conservation changed: {tape_stats}")
    features_by_ticker = aggregate_feature_sources(feature_matrix)
    indexes = build_receipt_indexes(
        orders, fills, lifecycles, decisions
    )
    lifecycle_by_ticker = indexes["lifecycle_by_ticker"]
    leg_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    additional_mismatches: list[dict[str, Any]] = []
    for base in sorted(replay_legs, key=lambda value: value["ticker"]):
        ticker = str(base["ticker"])
        leg, leg_decisions = build_leg_receipt_detail(
            base,
            start_by_event[str(base["event_id"])],
            lifecycle_by_ticker.get(ticker, []),
            indexes,
            references.get(ticker),
            features_by_ticker.get(ticker),
            recut_cells,
        )
        issues = leg["placement_fill_causality"]["issues"]
        if "fill_exchange_clock_precedes_placement_exchange_clock" in issues:
            additional_mismatches.append({
                "event_id": leg["event_id"],
                "ticker": ticker,
                "mismatch_type": (
                    "fill_exchange_clock_precedes_placement_exchange_clock"
                ),
            })
        leg_rows.append(leg)
        decision_rows.extend(leg_decisions)
    if additional_mismatches:
        write_jsonl(
            output / "EXECUTION_MISMATCH_LEDGER.jsonl",
            additional_mismatches,
        )
        raise ReplayError("causal clock mismatch; result publication refused")
    event_rows, metric_summary = evaluate_events(starts, leg_rows)
    coverage = component_coverage(
        read_json(paths["calibration_adapter"]), leg_rows
    )
    coverage["event_feature_censored_count"] = sum(
        row["feature_censored_event"] for row in event_rows
    )
    summary = {
        "schema_version": VERSION,
        "run_status": "complete",
        "execution_ordinal": 1,
        "candidate_id": candidate["candidate_id"],
        "D": D,
        **metric_summary,
        "start_precision_accounting": start_counts,
        "execution_reproduction": {
            "gate_pass": True,
            "leg_status_counts": actual_status,
            "mismatch_count": 0,
            "kernel_version": kernel_stats["kernel_version"],
            "historical_dual_exact_five_events": kernel_stats[
                "completed_dual_exact_five_events"
            ],
            "historical_dual_window1_timing_proven": False,
            "ten_contract_overfill_retained_as_other_quantity": (
                metric_summary["raw_leg_counts"][
                    "ten_contract_overfill_legs"
                ]
            ),
        },
        "causal_tape": tape_stats,
        "causal_clock_laws": {
            "private_exchange_fill_timestamps_consumed": True,
            "private_exchange_placement_timestamps_consumed": True,
            "schedule_used_for_positive_or_post_start": False,
            "local_receipt_used_for_positive_or_post_start": False,
            "missing_completion_default_used": False,
        },
        "instrument_binding": {
            "code_sha": freeze["code_sha"],
            "adapter_sha256": sha256_file(paths["adapter"]),
            "policy_allowlist_sha256": sha256_file(paths["allowlist"]),
            "candidate_spec_sha256": sha256_file(paths["candidate"]),
            "metric_contract_sha256": sha256_file(
                paths["metric_contract"]
            ),
            "freeze_sha256": sha256_file(paths["freeze"]),
            "proxy_substitution_used": False,
            "aim_v2_consumed": False,
        },
        "scope_assertions": {
            "development_dates_only": ["2026-07-12", "2026-07-20"],
            "holdout_inputs": [],
            "candidate_search": False,
            "parameter_sweep": False,
            "ablation": False,
            "threshold_optimization": False,
            "window2_exit_settlement_dca": False,
            "production_mutation": False,
        },
    }
    write_jsonl(output / "EVENT_LEG_RESULTS.jsonl", leg_rows)
    write_jsonl(output / "EVENT_RESULTS.jsonl", event_rows)
    write_jsonl(output / "POLICY_DECISION_LEDGER.jsonl", decision_rows)
    write_jsonl(output / "EXECUTION_MISMATCH_LEDGER.jsonl", [])
    write_json(output / "COMPONENT_COVERAGE.json", coverage)
    write_json(output / "RESULTS.json", summary)
    (output / "REPORT.md").write_text(
        markdown_report(summary), encoding="utf-8", newline="\n"
    )
    frozen_copy = {
        **freeze,
        "freeze_receipt_sha256": sha256_file(paths["freeze"]),
    }
    write_json(output / "FROZEN_HASHES.json", frozen_copy)
    artifacts = {}
    for path in sorted(output.iterdir()):
        if path.name in {"ARTIFACT_MANIFEST.json", "RUN_RECEIPT.json"}:
            continue
        artifacts[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "rows": (
                sum(1 for _ in path.open(encoding="utf-8"))
                if path.suffix == ".jsonl" else None
            ),
        }
    write_json(output / "ARTIFACT_MANIFEST.json", {
        "schema_version": VERSION,
        "D": D,
        "artifacts": artifacts,
        "private_identifiers_emitted": False,
        "holdout_inputs": [],
    })
    write_json(output / "RUN_RECEIPT.json", {
        "schema_version": VERSION,
        "state": "execution_complete",
        "execution_ordinal": 1,
        "candidate_spec_sha256": sha256_file(paths["candidate"]),
        "freeze_sha256": sha256_file(paths["freeze"]),
        "results_sha256": sha256_file(output / "RESULTS.json"),
        "artifact_manifest_sha256": sha256_file(
            output / "ARTIFACT_MANIFEST.json"
        ),
        "code_sha": freeze["code_sha"],
        "D": D,
        "holdout_inputs": [],
    })
    print(json.dumps({
        "run_status": "complete",
        "raw_event_counts": summary["raw_event_counts"],
        "raw_leg_counts": summary["raw_leg_counts"],
        "primary_bounds": summary["primary_bounds"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    private = Path.home() / "OMI-Window1-private" / "calibration-v1"
    fit_local = (
        Path.home() / "OMI-Window1-private" / "fit-local"
    )
    documents = REPO / "arb-executor" / "docs" / "research" / "window1"
    calibration = REPO / ".claude" / "window1_calibration_20260723"
    fit = REPO / ".claude" / "window1_20260721"
    result = argparse.ArgumentParser()
    result.add_argument("--freeze", required=True)
    result.add_argument(
        "--candidate",
        default=documents / "WINDOW1_CORRECTED_CANDIDATE.json",
    )
    result.add_argument(
        "--allowlist",
        default=documents / "WINDOW1_POLICY_ALLOWLIST.json",
    )
    result.add_argument(
        "--adapter",
        default=documents / "WINDOW1_OS_EXECUTION_ADAPTER.json",
    )
    result.add_argument(
        "--metric-contract",
        default=documents / "WINDOW1_CORRECTED_METRIC_CONTRACT.json",
    )
    result.add_argument(
        "--calibration-adapter",
        default=calibration / "WINDOW1_OS_RESEARCH_ADAPTER.json",
    )
    result.add_argument(
        "--events", default=fit / "corrected_event_ledger.jsonl"
    )
    result.add_argument(
        "--expected-legs",
        default=fit / "EVENT_LEG_LIFECYCLE_LEDGER.jsonl",
    )
    result.add_argument(
        "--starts", default=fit / "REAL_START_LEDGER.jsonl"
    )
    result.add_argument(
        "--orders", default=private / "orders.private.jsonl"
    )
    result.add_argument(
        "--fills", default=private / "api_fills.private.jsonl"
    )
    result.add_argument(
        "--lifecycles", default=private / "lifecycle.private.jsonl"
    )
    result.add_argument(
        "--decisions", default=fit / "CAUSAL_DECISIONS.sanitized.jsonl"
    )
    result.add_argument(
        "--feature-matrix", default=fit / "WINDOW1_FEATURE_MATRIX.jsonl"
    )
    result.add_argument(
        "--recut-cells",
        default=REPO / ".claude" / "seqfloor_20260708"
        / "recut_cells.json",
    )
    result.add_argument(
        "--public-prints", default=fit_local / "prints.jsonl"
    )
    result.add_argument("--output-dir", required=True)
    result.add_argument("--execute-frozen-replay", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
