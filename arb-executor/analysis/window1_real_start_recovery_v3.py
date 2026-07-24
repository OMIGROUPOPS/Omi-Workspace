#!/usr/bin/env python3
"""Recover a policy-blind immutable real-start ledger for Window-1 D=804.

Extraction consumes only event identity, schedule, and causal start sources.
It never reads placements, fills, policy decisions, or candidate outcomes.
Historical execution is adjudicated by a separate tool after this ledger is
frozen.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-real-start-ledger-v3"
D = 804
UTC = dt.timezone.utc
PUBLIC_EXACT_STATUSES = {"P", "live", "ended"}
SHADOW_EXACT_STATUSES = {"P", "live", "ended", "interrupted"}

PRECEDENCE = [
    "exact_official_provider_match_start",
    "raw_milestone_shadow",
    "tennis_db_start_or_live_score",
    "live_v3_live_v4_historical_log",
    "mapped_score_onset_interval",
    "event_resolved_exchange_lifecycle",
    "true_tape_regime_interval",
    "schedule_last_resort_bound",
]


class StartRecoveryError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StartRecoveryError(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise StartRecoveryError(
                    f"expected object: {path}:{line_number}"
                )
            rows.append(value)
    return rows


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
            handle.write(compact(row) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_ts(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        if result > 10_000_000_000:
            result /= 1000
        return result if math.isfinite(result) else None
    try:
        stamp = dt.datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError:
        return None
    if stamp.tzinfo is None:
        # The retained tennis.db collector writes local ET without a zone.
        stamp = stamp.replace(tzinfo=dt.timezone(dt.timedelta(hours=-4)))
    return stamp.timestamp()


def iso_utc(value: float | None) -> str | None:
    return (
        dt.datetime.fromtimestamp(value, UTC).isoformat()
        if value is not None else None
    )


def source_family(source: str) -> tuple[str, int]:
    lowered = source.casefold()
    if source == "official_provider_match_start":
        return PRECEDENCE[0], 1
    if "milestone_shadow" in lowered:
        return PRECEDENCE[1], 2
    if "observed_starts" in lowered or "tennis_db" in lowered:
        return PRECEDENCE[2], 3
    if (
        "engine_regime" in lowered
        or "gun_" in lowered
        or "live_v3" in lowered
        or "live_v4" in lowered
    ):
        return PRECEDENCE[3], 4
    if (
        "scoreboard" in lowered
        or "score_onset" in lowered
        or "schedule_feed_live_transition" in lowered
    ):
        return PRECEDENCE[4], 5
    if (
        "exchange_milestone" in lowered
        or "market_lifecycle" in lowered
        or "exchange_transition" in lowered
    ):
        return PRECEDENCE[5], 6
    if "tape" in lowered or "print" in lowered:
        return PRECEDENCE[6], 7
    return PRECEDENCE[7], 8


def candidate(
    *,
    source: str,
    timestamp: float,
    direction: str,
    basis: str,
    precision: str,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    family, rank = source_family(source)
    return {
        "source": source,
        "source_family": family,
        "precedence_rank": rank,
        "timestamp_utc": iso_utc(timestamp),
        "direction": direction,
        "precision": precision,
        "timestamp_basis": basis,
        "evidence": dict(evidence),
    }


def public_candidates(
    normalized: Path,
    manifest_path: Path,
    required: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    manifest = read_json(manifest_path)
    normalized_hash = sha256_file(normalized)
    pagination = manifest.get("pagination") or {}
    scope = manifest.get("scope") or {}
    artifacts = manifest.get("artifacts") or {}
    if not (
        scope.get("D") == D
        and scope.get("event_queries") == D
        and pagination.get("all_terminal_cursors_empty") is True
        and pagination.get("failed_event_count") == 0
        and artifacts.get("normalized_sha256") == normalized_hash
    ):
        raise StartRecoveryError("public milestone completeness gate failed")
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    counts: Counter[str] = Counter()
    exact = 0
    not_live = 0
    for row in read_jsonl(normalized):
        event_id = str(row.get("event_id") or "")
        if event_id not in required:
            raise StartRecoveryError(
                f"public milestone outside D: {event_id}"
            )
        status = str(row.get("status") or "")
        counts[status or "<missing>"] += 1
        start = parse_ts(row.get("start_utc"))
        updated = parse_ts(row.get("last_updated_utc"))
        evidence = {
            "status": status or None,
            "last_updated_utc": row.get("last_updated_utc"),
            "milestone_identity_sha256": row.get(
                "milestone_identity_sha256"
            ),
            "source_identity_sha256": row.get(
                "source_identity_sha256"
            ),
            "historical_freshness_rule_applied": False,
        }
        if start is not None and status in PUBLIC_EXACT_STATUSES:
            output[event_id].append(candidate(
                source="official_provider_match_start",
                timestamp=start,
                direction="exact",
                basis="official_provider_start_timestamp",
                precision="second",
                evidence={
                    **evidence,
                    "adjudication": (
                        "provider in-play/ended status makes start_utc a "
                        "historical match-start fact; deployed six-hour "
                        "freshness is not a historical reconstruction law"
                    ),
                },
            ))
            exact += 1
        elif (
            start is not None and updated is not None
            and status in {"not_started", "SCH"}
            and start - 12 * 3600 <= updated <= start + 6 * 3600
        ):
            output[event_id].append(candidate(
                source="official_provider_not_started_observation",
                timestamp=updated,
                direction="not_live_through",
                basis="official_provider_update_timestamp",
                precision="second",
                evidence=evidence,
            ))
            not_live += 1
    return output, {
        "normalized_sha256": normalized_hash,
        "manifest_sha256": sha256_file(manifest_path),
        "rows": sum(counts.values()),
        "status_counts": dict(counts),
        "accepted_exact": exact,
        "accepted_not_live": not_live,
        "pagination_complete": True,
    }


def shadow_candidates(
    path: Path,
    required: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    counts: Counter[str] = Counter()
    physical = 0
    relevant = 0
    exact = 0
    not_live = 0
    errors = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            physical += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                continue
            event_id = str(row.get("event") or "")
            if event_id not in required:
                continue
            relevant += 1
            status = str(row.get("ms_status") or "")
            counts[status or "<missing>"] += 1
            start = parse_ts(row.get("ms_start_ep") or row.get("ms_start"))
            receipt = parse_ts(row.get("ts"))
            source_id = str(row.get("source_id") or "")
            evidence = {
                "status": status or None,
                "receipt_utc": iso_utc(receipt),
                "source_identity_sha256": (
                    hashlib.sha256(source_id.encode()).hexdigest()
                    if source_id else None
                ),
                "historical_freshness_rule_applied": False,
            }
            if start is not None and status in SHADOW_EXACT_STATUSES:
                output[event_id].append(candidate(
                    source="milestone_shadow_official_start",
                    timestamp=start,
                    direction="exact",
                    basis="official_provider_start_timestamp",
                    precision="second",
                    evidence=evidence,
                ))
                exact += 1
            elif (
                start is not None and receipt is not None
                and status in {"not_started", "SCH"}
                and start - 12 * 3600 <= receipt <= start + 6 * 3600
            ):
                output[event_id].append(candidate(
                    source="milestone_shadow_not_started_observation",
                    timestamp=receipt,
                    direction="not_live_through",
                    basis="local_shadow_receipt_utc",
                    precision="subsecond",
                    evidence=evidence,
                ))
                not_live += 1
    return output, {
        "sha256": sha256_file(path),
        "physical_rows": physical,
        "parse_errors": errors,
        "required_rows": relevant,
        "required_events": len(output),
        "status_counts": dict(counts),
        "accepted_exact": exact,
        "accepted_not_live": not_live,
    }


def legacy_candidates(
    prior: Mapping[str, Any],
) -> list[dict[str, Any]]:
    output = []
    for raw in prior.get("candidate_evidence") or []:
        source = str(raw.get("source") or "")
        if (
            source.startswith("public_milestone_")
            or "milestone_shadow" in source
            or raw.get("bound_direction") == "rejected"
        ):
            continue
        timestamp = parse_ts(raw.get("timestamp"))
        direction = str(raw.get("bound_direction") or "")
        if not direction:
            direction = (
                "exact" if raw.get("exact_point") is True
                else "live_by"
            )
        if timestamp is None or direction not in {
            "exact", "not_live_through", "live_by"
        }:
            continue
        basis = str(raw.get("timestamp_basis") or "")
        precision = (
            "subsecond" if abs(timestamp - round(timestamp)) > 1e-6
            else "second"
        )
        evidence = dict(raw.get("evidence") or {})
        output.append(candidate(
            source=source,
            timestamp=timestamp,
            direction=direction,
            basis=basis,
            precision=precision,
            evidence=evidence,
        ))
    return output


def deduplicate(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output = {}
    for row in rows:
        key = (
            row.get("source"),
            row.get("timestamp_utc"),
            row.get("direction"),
            row.get("timestamp_basis"),
        )
        output[key] = dict(row)
    return sorted(
        output.values(),
        key=lambda row: (
            int(row["precedence_rank"]),
            str(row["timestamp_utc"]),
            str(row["source"]),
        ),
    )


def select_event(
    event: Mapping[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    exact = [
        row for row in candidates if row["direction"] == "exact"
    ]
    lower = [
        row for row in candidates
        if row["direction"] == "not_live_through"
    ]
    upper = [
        row for row in candidates if row["direction"] == "live_by"
    ]
    selected_exact = None
    if exact:
        best_rank = min(int(row["precedence_rank"]) for row in exact)
        best = [
            row for row in exact
            if int(row["precedence_rank"]) == best_rank
        ]
        selected_exact = min(best, key=lambda row: row["timestamp_utc"])
    selected_lower = (
        max(lower, key=lambda row: row["timestamp_utc"])
        if lower else None
    )
    selected_upper = (
        min(upper, key=lambda row: row["timestamp_utc"])
        if upper else None
    )
    exact_ts = parse_ts(
        selected_exact["timestamp_utc"] if selected_exact else None
    )
    lower_ts = parse_ts(
        selected_lower["timestamp_utc"] if selected_lower else None
    )
    upper_ts = parse_ts(
        selected_upper["timestamp_utc"] if selected_upper else None
    )
    exact_values = sorted({
        parse_ts(row["timestamp_utc"]) for row in exact
        if parse_ts(row["timestamp_utc"]) is not None
    })
    authoritative_exact = [
        row for row in exact if int(row["precedence_rank"]) == 1
    ]
    authoritative_values = sorted({
        parse_ts(row["timestamp_utc"]) for row in authoritative_exact
        if parse_ts(row["timestamp_utc"]) is not None
    })
    exact_conflict = bool(
        authoritative_values
        and authoritative_values[-1] - authoritative_values[0] > 1
    )
    interval_contradiction = bool(
        lower_ts is not None and upper_ts is not None
        and lower_ts >= upper_ts
    )
    if selected_exact is not None and not exact_conflict:
        precision_class = "exact"
        positive = True
        conflict_status = (
            "lower_authority_exact_disagreement"
            if exact_values
            and (
                min(exact_values) < exact_ts - 60
                or max(exact_values) > exact_ts + 60
            )
            else "none"
        )
    elif lower_ts is not None and upper_ts is not None:
        if interval_contradiction:
            precision_class = "contradictory"
            positive = False
            conflict_status = "causal_interval_contradiction"
        else:
            precision_class = "clean_interval"
            positive = True
            conflict_status = "none"
    elif upper_ts is not None:
        precision_class = "live_by_only"
        positive = False
        conflict_status = "none"
    elif event.get("scheduled_start_exchange_ts"):
        precision_class = "schedule_only"
        positive = False
        conflict_status = "none"
    else:
        precision_class = "unresolved"
        positive = False
        conflict_status = "none"
    selected_source = (
        selected_exact or selected_upper or selected_lower
    )
    return {
        "schema_version": VERSION,
        "event_id": str(event["event_id"]),
        "event_date": str(event["event_date"]),
        "category": str(event["category"]),
        "legs": event["legs"],
        "precision_class": precision_class,
        "positive_window1_provable": positive,
        "exact_start_utc": (
            iso_utc(exact_ts)
            if precision_class == "exact" else None
        ),
        "not_live_through_utc": iso_utc(lower_ts),
        "known_live_by_utc": iso_utc(
            exact_ts if precision_class == "exact" else upper_ts
        ),
        "start_interval_utc": {
            "lower_inclusive": iso_utc(lower_ts),
            "upper_inclusive": iso_utc(
                exact_ts if precision_class == "exact" else upper_ts
            ),
        },
        "schedule_bound_utc": event.get(
            "scheduled_start_exchange_ts"
        ),
        "schedule_source": event.get("schedule_source"),
        "schedule_can_prove_positive": False,
        "selected_source": (
            selected_source.get("source") if selected_source else None
        ),
        "selected_source_family": (
            selected_source.get("source_family")
            if selected_source else PRECEDENCE[-1]
        ),
        "selected_timestamp_precision": (
            selected_source.get("precision")
            if selected_source else None
        ),
        "conflict_status": conflict_status,
        "authoritative_exact_conflict": exact_conflict,
        "interval_contradiction": interval_contradiction,
        "candidate_sources": candidates,
        "policy_outcomes_examined_during_extraction": False,
    }


def build(
    events: list[dict[str, Any]],
    prior_starts: list[dict[str, Any]],
    public: dict[str, list[dict[str, Any]]],
    shadow: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if (
        len(events) != D or len(prior_starts) != D
        or len({row["event_id"] for row in events}) != D
        or len({row["event_id"] for row in prior_starts}) != D
    ):
        raise StartRecoveryError("immutable D changed")
    prior_by_event = {
        str(row["event_id"]): row for row in prior_starts
    }
    output = []
    for event in sorted(events, key=lambda row: row["event_id"]):
        event_id = str(event["event_id"])
        candidates = deduplicate([
            *public.get(event_id, []),
            *shadow.get(event_id, []),
            *legacy_candidates(prior_by_event[event_id]),
        ])
        output.append(select_event(event, candidates))
    return output


def summarize(
    rows: list[dict[str, Any]],
    source_receipts: Mapping[str, Any],
    ledger_hash: str,
) -> dict[str, Any]:
    counts = Counter(row["precision_class"] for row in rows)
    positive = sum(row["positive_window1_provable"] for row in rows)
    source_counts = Counter(
        row["selected_source"] or "schedule_or_unresolved"
        for row in rows
    )
    blocked = {
        "live_by_only": counts["live_by_only"],
        "contradictory": counts["contradictory"],
        "schedule_only": counts["schedule_only"],
        "unresolved": counts["unresolved"],
    }
    result = {
        "schema_version": VERSION,
        "D": D,
        "start_gate_required": 603,
        "start_gate_pass": positive >= 603,
        "exact_starts": counts["exact"],
        "clean_intervals": counts["clean_interval"],
        "live_by_only": counts["live_by_only"],
        "contradictory": counts["contradictory"],
        "schedule_only": counts["schedule_only"],
        "unresolved": counts["unresolved"],
        "provable_positive_population": positive,
        "timing_blocked_population": D - positive,
        "timing_blocked_by_precision": blocked,
        "missing_from_start_gate": max(0, 603 - positive),
        "selected_source_counts": dict(source_counts),
        "precedence": PRECEDENCE,
        "source_receipts": dict(source_receipts),
        "ledger_sha256": ledger_hash,
        "extraction_law": {
            "policy_outcomes_examined": False,
            "schedule_can_prove_positive": False,
            "live_by_promoted_to_exact": False,
            "missing_source_invents_timestamp": False,
            "official_historical_six_hour_freshness_rule": (
                "not applied to in-play/ended provider match-start facts"
            ),
        },
        "evidence_blocker": {
            "additional_exact_or_clean_boundaries_required": max(
                0, 603 - positive
            ),
            "events_without_a_positive_capable_boundary": D - positive,
            "blocked_precision_classes": blocked,
            "required_missing_source_kind": (
                "an event-resolved official exact start, or both a "
                "causal not-live-through lower bound and causal live-by "
                "upper bound forming a noncontradictory interval"
            ),
        },
    }
    if (
        sum(counts.values()) != D
        or sum(blocked.values()) != D - positive
    ):
        raise StartRecoveryError("start class denominator changed")
    return result


def report(summary: Mapping[str, Any]) -> str:
    verdict = "PASS" if summary["start_gate_pass"] else "FAIL"
    return f"""# Window-1 official-start recovery

This ledger was extracted without reading policy decisions, placements,
fills, or candidate outcomes.  Schedule is retained only as a last-resort
bound and never proves a positive Window-1 fill.

## Start gate — {verdict}

- exact starts = {summary['exact_starts']}
- clean causal intervals = {summary['clean_intervals']}
- live-by-only = {summary['live_by_only']}
- contradictory = {summary['contradictory']}
- schedule-only = {summary['schedule_only']}
- unresolved = {summary['unresolved']}
- positive-Window-1-provable population = {summary['provable_positive_population']}
- timing-blocked population = {summary['timing_blocked_population']}
- required = {summary['start_gate_required']}
- missing from gate = {summary['missing_from_start_gate']}

Historical public-provider rows carrying an in-play or ended status now use
their provider `start_utc` as the historical match-start fact.  The deployed
six-hour freshness corridor is not applied to historical reconstruction.
Live-by observations and scheduled times remain one-sided bounds.

The gate can pass only with {summary['missing_from_start_gate']} additional
event-resolved exact starts or noncontradictory causal intervals.  The
currently blocked population is {summary['live_by_only']} live-by-only,
{summary['contradictory']} contradictory, {summary['schedule_only']}
schedule-only, and {summary['unresolved']} unresolved events.
"""


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    prior_path = Path(args.prior_start_ledger).resolve()
    public_path = Path(args.public_milestones).resolve()
    manifest_path = Path(args.public_manifest).resolve()
    shadow_path = Path(args.milestone_shadow).resolve()
    output = Path(args.output).resolve()
    events = read_jsonl(events_path)
    required = {str(row["event_id"]) for row in events}
    public, public_receipt = public_candidates(
        public_path, manifest_path, required
    )
    shadow, shadow_receipt = shadow_candidates(shadow_path, required)
    rows = build(
        events, read_jsonl(prior_path), public, shadow
    )
    ledger_path = output / "REAL_START_LEDGER_V3.jsonl"
    write_jsonl(ledger_path, rows)
    source_receipts = {
        "events": {
            "sha256": sha256_file(events_path),
            "bytes": events_path.stat().st_size,
        },
        "prior_policy_blind_source_ledger": {
            "sha256": sha256_file(prior_path),
            "bytes": prior_path.stat().st_size,
        },
        "public_milestones": public_receipt,
        "raw_milestone_shadow": shadow_receipt,
    }
    summary = summarize(rows, source_receipts, sha256_file(ledger_path))
    write_json(output / "REAL_START_SUMMARY_V3.json", summary)
    (output / "REAL_START_REPORT_V3.md").write_text(
        report(summary), encoding="utf-8", newline="\n"
    )
    print(compact({
        "D": D,
        "exact": summary["exact_starts"],
        "clean": summary["clean_intervals"],
        "provable": summary["provable_positive_population"],
        "gate_pass": summary["start_gate_pass"],
    }))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--prior-start-ledger", required=True)
    result.add_argument("--public-milestones", required=True)
    result.add_argument("--public-manifest", required=True)
    result.add_argument("--milestone-shadow", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
