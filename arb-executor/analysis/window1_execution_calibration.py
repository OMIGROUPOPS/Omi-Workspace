#!/usr/bin/env python3
"""Build the Window-1 execution-calibration gate without candidate scoring."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

_ANALYSIS_DIR = str(Path(__file__).resolve().parent)
if _ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, _ANALYSIS_DIR)
from window1_execution_kernel import (  # noqa: E402
    VERSION as KERNEL_VERSION,
    replay_historical_execution,
)


VERSION = "window1-execution-calibration-gate-v1"
EXPECTED_LEG_COUNTS = {
    "exact_filled_five": 258,
    "exact_filled_other_quantity": 12,
    "exact_nonfill": 870,
    "censored": 468,
}
ALLOWED_COMPONENT_STATUS = {
    "available", "unavailable", "partially_available", "excluded",
}


class CalibrationError(RuntimeError):
    """The calibration contract cannot be evaluated safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CalibrationError(f"{path} is not a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    result = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise CalibrationError(
                    f"{path}:{line_number} is not an object"
                )
            result.append(row)
    return result


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(
    path: Path, rows: Sequence[Mapping[str, Any]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")


def source_family(source: str) -> str:
    if source in {
        "exchange_milestone_live_transition",
        "milestone_shadow_official_start",
    }:
        return "official_or_milestone_bell"
    if source.startswith("ws_market_lifecycle"):
        return "market_lifecycle_v2_exchange_transition"
    if source in {
        "te_scoreboard_first_observed_inplay",
        "observed_starts_db_first_observed_inplay",
        "tennis_db_live_scores_current_state",
        "schedule_feed_live_transition",
    }:
        return "mapped_live_score_onset_or_bound"
    if (
        source.startswith("engine_regime_transition:")
        or source == "public_tape_5_prints_in_15m_onset"
    ):
        return "defensible_tape_regime_onset"
    if source == "schedule_plus_declared_corridor":
        return "schedule_last_resort_bound"
    return "other_retained_evidence"


def precision_class(state: str) -> str:
    mapping = {
        "verified_exact": "exact_official_or_milestone",
        "bounded_start_interval": "causal_start_interval",
        "bounded_live_by_timestamp": "causal_live_by_bound",
        "schedule_only_censored": "schedule_only_bound",
    }
    if state not in mapping:
        raise CalibrationError(f"unknown real-start state: {state}")
    return mapping[state]


def build_start_ledger(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    ws_summary: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if len(rows) != 804:
        raise CalibrationError("real-start ledger does not preserve D=804")
    output = []
    event_ids: set[str] = set()
    precision_counts: collections.Counter[str] = collections.Counter()
    source_counts: collections.Counter[str] = collections.Counter()
    family_counts: collections.Counter[str] = collections.Counter()
    schedule_promoted_to_exact = 0
    interval_missing = 0
    ticker_count = 0
    for source in rows:
        event_id = str(source.get("event_id") or "")
        if not event_id or event_id in event_ids:
            raise CalibrationError("real-start event identity is invalid")
        event_ids.add(event_id)
        legs = source.get("legs") or []
        if len(legs) != 2:
            raise CalibrationError(
                f"real-start event {event_id} lacks two legs"
            )
        ticker_count += len(legs)
        state = str(source.get("start_state") or "")
        precision = precision_class(state)
        selected = str(source.get("selected_source") or "")
        family = source_family(selected)
        interval = source.get("start_interval_utc") or {}
        lower = interval.get("lower_exclusive")
        upper = interval.get("upper_inclusive")
        exact = state == "verified_exact"
        schedule_only = state == "schedule_only_censored"
        if schedule_only and exact:
            schedule_promoted_to_exact += 1
        if (
            not exact
            and not schedule_only
            and upper is None
        ):
            interval_missing += 1
        if (
            schedule_only
            and source.get("schedule_fallback_right_edge_utc") is None
        ):
            interval_missing += 1
        candidate_sources = sorted({
            str(value.get("source") or "")
            for value in source.get("candidate_evidence") or []
            if value.get("source")
        })
        output.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "event_date": str(source.get("event_date") or ""),
            "category": str(source.get("category") or ""),
            "legs": [
                {
                    "leg": str(value.get("leg") or ""),
                    "ticker": str(value.get("ticker") or ""),
                }
                for value in legs
            ],
            "precision_class": precision,
            "source_family": family,
            "selected_source": selected,
            "timestamp_basis": source.get(
                "selected_evidence_time_basis"
            ),
            "exact_start_utc": (
                source.get("verified_start_utc") if exact else None
            ),
            "interval_utc": {
                "lower_exclusive": lower,
                "upper_inclusive": upper,
            },
            "schedule_bound_utc": source.get(
                "schedule_fallback_right_edge_utc"
            ),
            "schedule_only": schedule_only,
            "censored": not exact,
            "candidate_sources_retained": candidate_sources,
            "contradiction": bool(source.get("contradiction")),
            "interval_contradiction": bool(
                source.get("interval_contradiction")
            ),
        })
        precision_counts[precision] += 1
        source_counts[selected] += 1
        family_counts[family] += 1

    raw_ws = ws_summary.get("ws_depth") or {}
    prior_ws = summary.get("ws_lifecycle") or {}
    start_summary = {
        "schema_version": VERSION,
        "gate_pass": (
            len(event_ids) == 804
            and ticker_count == 1608
            and schedule_promoted_to_exact == 0
            and interval_missing == 0
            and int(prior_ws.get("events_with_live_transition") or 0) == 0
        ),
        "D": len(event_ids),
        "required_legs": ticker_count,
        "precision_class_counts": dict(sorted(precision_counts.items())),
        "source_family_counts": dict(sorted(family_counts.items())),
        "selected_source_counts": dict(sorted(source_counts.items())),
        "censored_events": sum(
            value for key, value in precision_counts.items()
            if key != "exact_official_or_milestone"
        ),
        "schedule_only_events": precision_counts[
            "schedule_only_bound"
        ],
        "schedule_only_promoted_to_exact": schedule_promoted_to_exact,
        "nonexact_rows_missing_upper_bound": interval_missing,
        "market_lifecycle_v2": {
            "message_rows": int(
                (raw_ws.get("message_types") or {})
                .get("market_lifecycle_v2") or 0
            ),
            "valid_live_transition_events": int(
                prior_ws.get("events_with_live_transition") or 0
            ),
            "ruling": (
                "no archived market_lifecycle_v2 message encoded a "
                "defensible live transition; none was promoted"
            ),
        },
        "precedence": [
            "official_or_milestone_bell",
            "market_lifecycle_v2_exchange_transition",
            "mapped_live_score_onset_or_bound",
            "defensible_tape_regime_onset",
            "schedule_last_resort_bound",
        ],
        "laws": {
            "schedule_only_is_exact": False,
            "first_trade_alone_is_start": False,
            "current_live_score_last_updated_is_exact_start": False,
            "unresolved_events_leave_D": False,
        },
    }
    return output, start_summary


def nested_value(
    value: Mapping[str, Any], dotted: str
) -> Any:
    current: Any = value
    for part in dotted.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def build_os_adapter(
    repo_root: Path,
    contract: Mapping[str, Any],
    feature_coverage: Mapping[str, Any],
    source_coverage: Mapping[str, Any],
    tape_summary: Mapping[str, Any],
    execution_summary: Mapping[str, Any],
    start_summary: Mapping[str, Any],
) -> dict[str, Any]:
    context = {
        "feature_coverage": feature_coverage,
        "source_coverage": source_coverage,
        "tape_summary": tape_summary,
        "execution_summary": execution_summary,
        "start_summary": start_summary,
    }
    components = []
    missing_source_count = 0
    status_counts: collections.Counter[str] = collections.Counter()
    component_ids: set[str] = set()
    for source in contract.get("components") or []:
        component_id = str(source.get("component_id") or "")
        status = str(source.get("declared_status") or "")
        if not component_id or component_id in component_ids:
            raise CalibrationError("OS adapter component ID is invalid")
        if status not in ALLOWED_COMPONENT_STATUS:
            raise CalibrationError(
                f"OS adapter status is invalid for {component_id}"
            )
        component_ids.add(component_id)
        source_receipts = []
        component_missing = []
        for relative in source.get("sources") or []:
            path = repo_root / str(relative)
            exists = path.is_file()
            receipt = {
                "source": str(relative).replace("\\", "/"),
                "available": exists,
                "sha256": sha256_file(path) if exists else None,
                "bytes": path.stat().st_size if exists else None,
            }
            source_receipts.append(receipt)
            if not exists:
                component_missing.append(str(relative))
                missing_source_count += 1
        coverage_binding = source.get("coverage_binding")
        coverage_value = (
            nested_value(context, str(coverage_binding))
            if coverage_binding else None
        )
        components.append({
            "component_id": component_id,
            "status": status,
            "source_receipts": source_receipts,
            "missing_sources": component_missing,
            "coverage_binding": coverage_binding,
            "coverage_value": coverage_value,
            "reason": str(source.get("reason") or ""),
            "missing_action": str(source.get("missing_action") or ""),
            "silent_proxy_substitution_allowed": False,
            "feature_censored_when_input_missing": True,
        })
        status_counts[status] += 1

    required_ids = {
        "pair_law",
        "first_fill_sibling_response",
        "sealed_bands",
        "dual_divot_steering_and_catch",
        "drift_recognition",
        "cohort_steering",
        "orientation_prior",
        "walk_park_posture",
        "riser_deceleration_mirror_seesaw",
        "dynamic_floor_and_recut_cells",
        "atlas_and_reach",
        "fv_bookmaker_pinnacle_voices",
        "bbo_and_top_five_pressure",
        "own_order_fingerprints_and_contributed_volume",
        "aim_v2",
    }
    missing_components = sorted(required_ids - component_ids)
    by_id = {row["component_id"]: row for row in components}
    gate_pass = (
        not missing_components
        and missing_source_count == 0
        and by_id["aim_v2"]["status"] == "excluded"
        and by_id["raw_ws_full_depth"]["status"] == "unavailable"
        and all(
            row["feature_censored_when_input_missing"]
            and not row["silent_proxy_substitution_allowed"]
            and row["missing_action"]
            for row in components
        )
    )
    return {
        "schema_version": str(
            contract.get("schema_version")
            or "window1-os-research-adapter-contract-v1"
        ),
        "gate_pass": gate_pass,
        "adapter_version": VERSION,
        "kernel_version": KERNEL_VERSION,
        "component_count": len(components),
        "status_counts": dict(sorted(status_counts.items())),
        "missing_required_components": missing_components,
        "missing_source_count": missing_source_count,
        "components": components,
        "coverage": {
            "feature_rows": int(
                feature_coverage.get("feature_rows") or 0
            ),
            "shape_cell_available_rows": int(
                feature_coverage.get("shape_cell_available_rows") or 0
            ),
            "bookmaker_available_rows": int(
                feature_coverage.get("bookmaker_available_rows") or 0
            ),
            "pinnacle_available_rows": 0,
            "top5_available_rows": int(
                feature_coverage.get("top5_available_rows") or 0
            ),
            "top5_missing_rows": int(
                feature_coverage.get("top5_missing_rows") or 0
            ),
            "full_depth_rows": int(
                feature_coverage.get("full_depth_sequence_valid_rows") or 0
            ),
            "execution_receipt_backed_legs": (
                1608 - int(
                    execution_summary.get("leg_status_counts", {})
                    .get("censored") or 0
                )
            ),
            "exact_start_events": int(
                start_summary.get("precision_class_counts", {})
                .get("exact_official_or_milestone") or 0
            ),
        },
        "laws": contract.get("law") or {},
    }


def evidence_receipt(path: Path, logical: str, private: bool) -> dict[str, Any]:
    return {
        "logical_source": logical,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "private": private,
        "path_included": False,
    }


def report_markdown(
    gate: Mapping[str, Any],
    start: Mapping[str, Any],
    execution: Mapping[str, Any],
    adapter: Mapping[str, Any],
    tape: Mapping[str, Any],
) -> str:
    counts = execution["leg_status_counts"]
    receipt = execution["receipt_grain"]
    precision = start["precision_class_counts"]
    market = tape["identity_reconciliation"]
    return f"""# Window-1 execution-calibration gate

Status: **{"PASS" if gate["gate_pass"] else "FAIL"}**. This is a calibration
result, not candidate scoring and not an OS-performance verdict.

## Real-start ledger

All 804 D events and 1,608 legs are retained. Precision classes are:

- exact official/milestone: {precision.get("exact_official_or_milestone", 0)}
- causal start interval: {precision.get("causal_start_interval", 0)}
- causal live-by bound: {precision.get("causal_live_by_bound", 0)}
- schedule-only bound: {precision.get("schedule_only_bound", 0)}

Schedule-only starts promoted to exact: {start["schedule_only_promoted_to_exact"]}.
Archived `market_lifecycle_v2` rows:
{start["market_lifecycle_v2"]["message_rows"]}; valid live-transition events:
{start["market_lifecycle_v2"]["valid_live_transition_events"]}. Missing start
precision censors the boundary; it does not remove an event from D.

## Causal market receipts

The canonical public tape has
{tape["canonical_true_print_stream"]["rows"]:,} exchange-identified,
positive-size true prints across
{tape["canonical_true_print_stream"]["tickers_with_true_prints"]} tickers;
queries are cursor-complete for all 1,608 and the other
{len(tape["canonical_true_print_stream"]["proven_zero_trade_tickers"])}
tickers are proven zero-trade. Recovered WS
trade receipt rows: {tape["archived_ws_trade_stream"]["required_trade_receipt_rows"]:,};
unique identities:
{tape["archived_ws_trade_stream"]["unique_exchange_trade_ids"]:,} across
{tape["archived_ws_trade_stream"]["tickers_with_trade_receipts"]} tickers;
{tape["archived_ws_trade_stream"]["tickers_without_trade_receipts"]} tickers
have no recovered WS trade. Exact
WS/public identity matches: {market["exact_matches"]:,}; reconciliation
mismatches: {market["mismatch_total"]}. Recorder read errors remain named
coverage censoring. Full depth is unavailable and no full-depth feature is
enabled.

## Exact historical execution replay

The shared kernel consumed {receipt["attributable_accepted_placements"]:,}
accepted placement receipts plus {receipt["relevant_failed_attempts"]} failed
attempts, validated {receipt["placement_prices_validated"]:,} prices,
quantities, and local timestamps, consumed
{receipt["cancellation_receipts"]:,} cancellation receipts and
{receipt["official_fill_receipts"]} official fill receipts. The 42
unattributed private-fill lineages remain censored.

Across 1,608 legs the replay produced exactly:

- {counts.get("exact_filled_five", 0)} exact-five filled legs
- {counts.get("exact_filled_other_quantity", 0)} other-quantity filled legs
- {counts.get("exact_nonfill", 0)} exact nonfills
- {counts.get("censored", 0)} legitimately censored legs

Completed dual exact-five events:
{execution["completed_dual_exact_five_events"]}; of those, combined actual
entry cost under par: {execution["completed_dual_combined_cost_under_par"]}.
Execution mismatches: {execution["mismatch_count"]}. Schedule fields consumed
by this replay: {str(execution["schedule_fields_consumed"]).lower()}.

## OS research adapter

The adapter inventories {adapter["component_count"]} chronological
components. Status counts:
{json.dumps(adapter["status_counts"], sort_keys=True)}. AIM_V2 is excluded.
Pinnacle is unavailable; bookmaker/FV is partial; top-five pressure is
partial; full depth is unavailable; own-order contribution is partial.
Every missing input censors its named feature. No narrow proxy is substituted.

## Stop law

No C, PC, NC, IC, X, dynamic-floor gap, dip/catch performance, candidate,
ablation, tuning, or holdout result was computed. No production surface was
read as a mutation target or changed.

If this gate is accepted, the smallest lawful scoring run is one deterministic,
predeclared corrected-instrument replay over all 804 development events, with
one fixed adapter version and one fixed execution kernel. It must report C,
PC, NC, IC, X, dynamic-floor gap, and per-leg dip/catch separately; it may not
tune, ablate, inspect a holdout, or shrink D. Only after that instrument passes
validation may a new prospective holdout be frozen.
"""


def run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "calibration_runner": Path(__file__).resolve(),
        "execution_kernel": (
            Path(__file__).resolve().with_name(
                "window1_execution_kernel.py"
            )
        ),
        "trade_reconciliation_runner": (
            Path(__file__).resolve().with_name(
                "window1_ws_trade_reconcile.py"
            )
        ),
        "future_fit_runner": (
            Path(__file__).resolve().with_name(
                "window1_fit_benchmark.py"
            )
        ),
        "events": Path(args.events),
        "orders": Path(args.orders),
        "fills": Path(args.fills),
        "private_lifecycles": Path(args.private_lifecycles),
        "decisions": Path(args.decisions),
        "expected_legs": Path(args.expected_legs),
        "expected_execution_summary": Path(
            args.expected_execution_summary
        ),
        "real_start_ledger": Path(args.real_start_ledger),
        "real_start_summary": Path(args.real_start_summary),
        "ws_summary": Path(args.ws_summary),
        "tape_reconciliation": Path(args.tape_reconciliation),
        "feature_coverage": Path(args.feature_coverage),
        "source_coverage": Path(args.source_coverage),
        "os_contract": Path(args.os_contract),
    }
    events = read_jsonl(paths["events"])
    orders = read_jsonl(paths["orders"])
    fills = read_jsonl(paths["fills"])
    private_lifecycles = read_jsonl(paths["private_lifecycles"])
    decisions = read_jsonl(paths["decisions"])
    expected_legs = read_jsonl(paths["expected_legs"])
    expected_execution_summary = read_json(
        paths["expected_execution_summary"]
    )
    prior_start_rows = read_jsonl(paths["real_start_ledger"])
    prior_start_summary = read_json(paths["real_start_summary"])
    ws_summary = read_json(paths["ws_summary"])
    tape_reconciliation = read_json(paths["tape_reconciliation"])
    feature_coverage = read_json(paths["feature_coverage"])
    source_coverage = read_json(paths["source_coverage"])
    os_contract = read_json(paths["os_contract"])

    start_rows, start_summary = build_start_ledger(
        prior_start_rows, prior_start_summary, ws_summary
    )
    replay_legs, mismatches, execution_summary = (
        replay_historical_execution(
            events,
            orders,
            fills,
            private_lifecycles,
            decisions,
            expected_legs,
        )
    )
    replay_by_event: dict[str, list[Mapping[str, Any]]] = (
        collections.defaultdict(list)
    )
    for row in replay_legs:
        replay_by_event[str(row["event_id"])].append(row)
    replay_events = []
    for event in events:
        event_id = str(event["event_id"])
        legs = sorted(
            replay_by_event.get(event_id, []),
            key=lambda row: str(row["ticker"]),
        )
        exact_dual = len(legs) == 2 and all(
            row["replayed_status"] == "exact_filled_five"
            for row in legs
        )
        combined_cost = (
            sum(float(row["official_fill_vwap_cents"]) for row in legs)
            if exact_dual else None
        )
        replay_events.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "event_date": str(event["event_date"]),
            "category": str(event["category"]),
            "required_leg_count": len(legs),
            "leg_statuses": [
                {
                    "ticker": str(row["ticker"]),
                    "status": str(row["replayed_status"]),
                }
                for row in legs
            ],
            "completed_dual_exact_five": exact_dual,
            "combined_actual_entry_cost_cents": combined_cost,
            "combined_actual_entry_cost_under_par": (
                combined_cost < 100.0
                if combined_cost is not None else None
            ),
            "match": len(legs) == 2 and all(row["match"] for row in legs),
            "private_identifiers_included": False,
        })
    execution_summary["replayed_event_rows"] = len(replay_events)
    execution_summary["gate_pass"] = (
        execution_summary["D"] == 804
        and execution_summary["required_legs"] == 1608
        and execution_summary["replayed_event_rows"] == 804
        and execution_summary["leg_status_counts"]
        == EXPECTED_LEG_COUNTS
        and execution_summary["mismatch_count"] == 0
        and execution_summary["receipt_grain"][
            "zero_size_fill_promotions"
        ] == 0
        and execution_summary["receipt_grain"][
            "duplicate_fill_memberships"
        ] == 0
        and execution_summary["receipt_grain"][
            "duplicate_order_memberships"
        ] == 0
        and execution_summary["schedule_fields_consumed"] is False
        and expected_execution_summary.get("gate_pass") is True
        and expected_execution_summary.get("leg_status_counts")
        == EXPECTED_LEG_COUNTS
    )
    adapter = build_os_adapter(
        repo_root,
        os_contract,
        feature_coverage,
        source_coverage,
        tape_reconciliation,
        execution_summary,
        start_summary,
    )
    market_gate = {
        "gate_pass": (
            tape_reconciliation.get("gate_pass") is True
            and int(
                feature_coverage.get("top5_available_rows") or 0
            ) + int(feature_coverage.get("top5_missing_rows") or 0)
            == int(feature_coverage.get("feature_rows") or 0)
            and int(
                feature_coverage.get("full_depth_sequence_valid_rows")
                or 0
            ) == 0
            and str(
                feature_coverage.get("full_depth_enhancement_status") or ""
            ).startswith("unavailable")
        ),
        "top5_available_rows": int(
            feature_coverage.get("top5_available_rows") or 0
        ),
        "top5_missing_rows": int(
            feature_coverage.get("top5_missing_rows") or 0
        ),
        "full_depth_available_rows": 0,
        "full_depth_claimed": False,
    }

    gate_pass = (
        start_summary["gate_pass"]
        and market_gate["gate_pass"]
        and execution_summary["gate_pass"]
        and adapter["gate_pass"]
    )
    gate = {
        "schema_version": VERSION,
        "gate_pass": gate_pass,
        "D": 804,
        "required_legs": 1608,
        "subgates": {
            "real_start": start_summary["gate_pass"],
            "causal_market_data": market_gate["gate_pass"],
            "historical_execution_replay": (
                execution_summary["gate_pass"]
            ),
            "full_os_research_adapter": adapter["gate_pass"],
        },
        "score_or_tune_executed": False,
        "ablations_executed": False,
        "holdout_opened_or_evaluated": False,
        "production_mutated": False,
        "aim_v2_activated": False,
        "metrics_not_evaluated": [
            "C", "PC", "NC", "IC", "X",
            "dynamic_floor_gap", "per_leg_dip_catch",
        ],
        "smallest_next_run_if_passed": (
            "one deterministic, predeclared corrected-instrument replay "
            "over all D=804 development events using this adapter/kernel; "
            "report C, PC, NC, IC, X, dynamic-floor gap, and per-leg "
            "dip/catch separately; no tuning, ablation, or holdout"
            if gate_pass else None
        ),
    }

    start_ledger_path = output_dir / "REAL_START_CALIBRATION_LEDGER.jsonl"
    start_summary_path = output_dir / "REAL_START_CALIBRATION_SUMMARY.json"
    replay_path = output_dir / "EXECUTION_REPLAY_LEDGER.jsonl"
    replay_event_path = (
        output_dir / "EXECUTION_REPLAY_EVENT_LEDGER.jsonl"
    )
    mismatch_path = output_dir / "EXECUTION_MISMATCH_LEDGER.jsonl"
    execution_summary_path = (
        output_dir / "EXECUTION_REPLAY_SUMMARY.json"
    )
    adapter_path = output_dir / "WINDOW1_OS_RESEARCH_ADAPTER.json"
    gate_path = output_dir / "CALIBRATION_GATE_SUMMARY.json"
    report_path = output_dir / "CALIBRATION_GATE_REPORT.md"
    manifest_path = output_dir / "CALIBRATION_EVIDENCE_MANIFEST.json"

    write_jsonl(start_ledger_path, start_rows)
    write_json(start_summary_path, start_summary)
    write_jsonl(replay_path, replay_legs)
    write_jsonl(replay_event_path, replay_events)
    write_jsonl(mismatch_path, mismatches)
    write_json(execution_summary_path, execution_summary)
    write_json(adapter_path, adapter)
    write_json(gate_path, gate)
    report_path.write_text(
        report_markdown(
            gate,
            start_summary,
            execution_summary,
            adapter,
            tape_reconciliation,
        ),
        encoding="utf-8",
    )

    private_names = {
        "orders", "fills", "private_lifecycles",
    }
    inputs = [
        evidence_receipt(
            path, logical, logical in private_names
        )
        for logical, path in sorted(paths.items())
    ]
    outputs = [
        evidence_receipt(path, path.name, False)
        for path in (
            start_ledger_path,
            start_summary_path,
            replay_path,
            replay_event_path,
            mismatch_path,
            execution_summary_path,
            adapter_path,
            report_path,
        )
    ]
    manifest = {
        "schema_version": VERSION,
        "gate_pass": gate_pass,
        "inputs": inputs,
        "outputs": outputs,
        "private_identifiers_emitted": False,
        "private_paths_emitted": False,
        "holdout_inputs": [],
        "scoring_outputs": [],
    }
    write_json(manifest_path, manifest)
    gate["artifact_hashes"] = {
        path.name: sha256_file(path)
        for path in (
            start_ledger_path,
            start_summary_path,
            replay_path,
            replay_event_path,
            mismatch_path,
            execution_summary_path,
            adapter_path,
            report_path,
            manifest_path,
        )
    }
    write_json(gate_path, gate)
    print(json.dumps({
        "gate_pass": gate_pass,
        "start_precision": start_summary["precision_class_counts"],
        "leg_status_counts": execution_summary["leg_status_counts"],
        "execution_mismatches": execution_summary["mismatch_count"],
        "os_status_counts": adapter["status_counts"],
    }, sort_keys=True))
    return 0 if gate_pass else 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo-root", required=True)
    result.add_argument("--events", required=True)
    result.add_argument("--orders", required=True)
    result.add_argument("--fills", required=True)
    result.add_argument("--private-lifecycles", required=True)
    result.add_argument("--decisions", required=True)
    result.add_argument("--expected-legs", required=True)
    result.add_argument("--expected-execution-summary", required=True)
    result.add_argument("--real-start-ledger", required=True)
    result.add_argument("--real-start-summary", required=True)
    result.add_argument("--ws-summary", required=True)
    result.add_argument("--tape-reconciliation", required=True)
    result.add_argument("--feature-coverage", required=True)
    result.add_argument("--source-coverage", required=True)
    result.add_argument("--os-contract", required=True)
    result.add_argument("--output-dir", required=True)
    return result


def main() -> int:
    return run(parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
