#!/usr/bin/env python3
"""Publish the corrected V5 start ledger and historical witness rulings."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from window1_start_guard import (
    NAMED_PROXY_CENSORS,
    PROXY_GUARD_ID,
    PROXY_NEGATIVE_GUARD_SECONDS,
    PROXY_POSITIVE_GUARD_SECONDS,
    StartGuardError,
    boundary_verdict,
    is_te_proxy,
    repair_v4_row,
)


VERSION = "window1-start-guard-repair-v1"
D_REQUIRED = 804
EXPECTED_SOURCE_PARTITION = {
    "start_clock": 687,
    "clean_interval": 31,
    "contradictory": 14,
    "schedule_only": 20,
    "live_by_only": 52,
}
POST_TO_STRICT_REVERSALS = [
    "KXATPMATCH-26JUL14TOPUGO",
    "KXATPMATCH-26JUL17COLVAC",
    "KXWTACHALLENGERMATCH-26JUL13GRABER",
    "KXATPCHALLENGERMATCH-26JUL13YEVCAM",
]


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StartGuardError(f"object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise StartGuardError(
                    f"object required: {path}:{line_number}"
                )
            rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(
    path: Path, rows: Iterable[Mapping[str, Any]]
) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def source_partition(rows: Iterable[Mapping[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        precision = str(row.get("precision_class") or "")
        if is_te_proxy(row) or precision == "exact":
            counts["start_clock"] += 1
        elif precision in {
            "clean_interval", "contradictory",
            "schedule_only", "live_by_only",
        }:
            counts[precision] += 1
        else:
            raise StartGuardError(
                "unrecognized precision class: "
                f"{row.get('event_id')}={precision}"
            )
    return counts


def witness_rows(
    repaired_by_event: Mapping[str, Mapping[str, Any]],
    historical_events: list[dict[str, Any]],
    historical_legs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    legs_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in historical_legs:
        legs_by_event[str(row.get("event_id") or "")].append(row)
    output = []
    for event in historical_events:
        if event.get("strict_dual_exact_five_window1") is not True:
            continue
        event_id = str(event["event_id"])
        start = repaired_by_event[event_id]
        legs = [
            row for row in legs_by_event[event_id]
            if row.get("exact_five_quantity") is True
        ]
        if len(legs) != 2:
            raise StartGuardError(
                f"claimed dual lacks two exact-five legs: {event_id}"
            )
        strict_60 = [
            boundary_verdict(
                start, float(row["completion_exchange_ts"]),
                proxy_guard_override_seconds=60,
            )
            for row in legs
        ]
        frozen = [
            boundary_verdict(
                start, float(row["completion_exchange_ts"])
            )
            for row in legs
        ]
        output.append({
            "event_id": event_id,
            "combined_entry_cost_cents": float(
                event["combined_entry_cost_cents"]
            ),
            "combined_entry_cost_under_par": bool(
                event["combined_entry_cost_under_par"]
            ),
            "strict_60_second_guard": {
                "dual_strict_window1": all(
                    row["verdict"] == "strict_window1"
                    for row in strict_60
                ),
                "leg_verdicts": strict_60,
            },
            "frozen_asymmetric_proxy_guard": {
                "guard_id": PROXY_GUARD_ID,
                "dual_strict_window1": all(
                    row["verdict"] == "strict_window1"
                    for row in frozen
                ),
                "leg_verdicts": frozen,
            },
        })
    return sorted(output, key=lambda row: row["event_id"])


def markdown(summary: Mapping[str, Any]) -> str:
    witnesses = summary["historical_witnesses"]["rows"]
    lines = [
        "# Corrected Window-1 start ledger and witness adjudication",
        "",
        "Independent-review provenance: "
        "`origin/audit/window1-independent` at "
        "`9919de9462f3df4a0bd33239b7e8f648b71e20fb`, artifact "
        "`START_LEDGER_V4_CROSS_REVIEW.md`.",
        "",
        "## Frozen source conservation",
        "",
        "- D = 804",
        "- start-clock rows = 687 (234 official exact + 453 "
        "five-minute-quantized late-detection proxies)",
        "- clean causal intervals = 31",
        "- contradictory = 14",
        "- schedule-only = 20",
        "- live-by-only = 52",
        f"- positive-capable after 13 named evidence censors = "
        f"{summary['positive_capable_after_named_censors']} "
        "(the pre-correction population gate was 718)",
        "",
        "## Boundary law",
        "",
        "- official point and clean-interval boundaries use a strict "
        "60-second guard;",
        "- TE proxy strict W1 requires completion at or before "
        "proxy−900 seconds;",
        "- TE proxy strict post-start requires completion at or after "
        "proxy+600 seconds;",
        "- the interior is censored; the 13 named conflicts are censored;",
        "- schedule is never a start, and a retained causal live-by bound "
        "is never overwritten by the rank-3 proxy.",
        "",
        "## Seven historical witnesses",
        "",
        "| event | cost | 60s guard | frozen −900/+600 guard |",
        "|---|---:|---|---|",
    ]
    for row in witnesses:
        lines.append(
            f"| {row['event_id']} | "
            f"{row['combined_entry_cost_cents']:.0f} | "
            f"{'strict' if row['strict_60_second_guard']['dual_strict_window1'] else 'censored'} | "
            f"{'strict' if row['frozen_asymmetric_proxy_guard']['dual_strict_window1'] else 'censored'} |"
        )
    counts = summary["historical_witnesses"]
    lines.extend([
        "",
        "Recomputed result: under the explicitly requested strict "
        f"60-second witness guard, {counts['strict_60_count']} are strict "
        f"and {counts['strict_60_under_par_count']} are under par. Under "
        f"the frozen calibrated development guard, "
        f"{counts['frozen_guard_strict_count']} are strict and "
        f"{counts['frozen_guard_under_par_count']} are under par.",
        "",
        "The record also discloses all four prior post→strict reversals "
        "(TOPUGO, COLVAC, GRABER, YEVCAM), the permanently unavailable "
        "historical-leg shrink from 106 to 82, and the W1-leg expansion "
        "from 45 to 146. These are semantic changes, not performance.",
        "",
        "No candidate result, placement, fill beyond the already-published "
        "historical witness ledger, delta, or holdout evidence was read to "
        "derive this law.",
        "",
    ])
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    if output.exists() and any(output.iterdir()):
        raise StartGuardError(f"refusing to overwrite: {output}")
    output.mkdir(parents=True, exist_ok=True)

    v4_path = Path(args.v4_ledger).resolve()
    calibration_path = Path(args.calibration).resolve()
    historical_event_path = Path(args.historical_events).resolve()
    historical_leg_path = Path(args.historical_legs).resolve()
    v4 = read_jsonl(v4_path)
    if len(v4) != D_REQUIRED:
        raise StartGuardError(f"D changed: {len(v4)}")
    if dict(source_partition(v4)) != EXPECTED_SOURCE_PARTITION:
        raise StartGuardError(
            f"V4 conservation changed: {dict(source_partition(v4))}"
        )
    calibration = read_json(calibration_path)
    guard = calibration.get("derived_guard") or {}
    if (
        guard.get("positive_guard_seconds")
        != PROXY_POSITIVE_GUARD_SECONDS
        or guard.get("negative_guard_seconds")
        != PROXY_NEGATIVE_GUARD_SECONDS
        or calibration.get("comparable_unique_crosswalks") != 222
    ):
        raise StartGuardError("calibration/guard binding failed")

    repaired = [repair_v4_row(row) for row in v4]
    repaired_by_event = {
        str(row["event_id"]): row for row in repaired
    }
    if len(repaired_by_event) != D_REQUIRED:
        raise StartGuardError("duplicate/missing repaired event ids")
    partition = dict(source_partition(repaired))
    if partition != EXPECTED_SOURCE_PARTITION:
        raise StartGuardError(
            f"repaired conservation changed: {partition}"
        )
    proxy_count = sum(is_te_proxy(row) for row in repaired)
    official_count = sum(
        row.get("start_source_class") == "official_exact"
        for row in repaired
    )
    if proxy_count != 453 or official_count != 234:
        raise StartGuardError(
            f"clock decomposition changed: {official_count}/{proxy_count}"
        )
    named_present = set(NAMED_PROXY_CENSORS) & set(repaired_by_event)
    if named_present != set(NAMED_PROXY_CENSORS):
        raise StartGuardError(
            "named proxy censor event set is incomplete"
        )

    historical_events = read_jsonl(historical_event_path)
    historical_legs = read_jsonl(historical_leg_path)
    witnesses = witness_rows(
        repaired_by_event, historical_events, historical_legs
    )
    strict_60 = [
        row for row in witnesses
        if row["strict_60_second_guard"]["dual_strict_window1"]
    ]
    frozen = [
        row for row in witnesses
        if row["frozen_asymmetric_proxy_guard"]["dual_strict_window1"]
    ]
    if len(witnesses) != 7 or len(strict_60) != 5:
        raise StartGuardError(
            f"witness recomputation changed: {len(witnesses)}/"
            f"{len(strict_60)}"
        )
    if sum(row["combined_entry_cost_under_par"] for row in strict_60) != 3:
        raise StartGuardError("60-second under-par witness count changed")

    summary = {
        "schema_version": VERSION,
        "D": D_REQUIRED,
        "source_conservation": partition,
        "start_clock_decomposition": {
            "official_exact": official_count,
            "quantized_late_detection_proxy": proxy_count,
        },
        "population_gate_positive_capable_before_named_censors": 718,
        "named_evidence_censors": dict(sorted(NAMED_PROXY_CENSORS.items())),
        "positive_capable_after_named_censors": 718 - len(
            NAMED_PROXY_CENSORS
        ),
        "guard": guard,
        "one_sided_conflict_law": {
            "law_id": "retain-stronger-causal-bounds-v1",
            "proxy_never_exact": True,
            "proxy_never_overwrites_earlier_live_by": True,
            "only_strictly_higher_rank_not_live_may_block": True,
            "ties_never_promote_proxy_to_exact": True,
        },
        "historical_witnesses": {
            "claimed_population": len(witnesses),
            "strict_60_count": len(strict_60),
            "strict_60_under_par_count": sum(
                row["combined_entry_cost_under_par"]
                for row in strict_60
            ),
            "frozen_guard_strict_count": len(frozen),
            "frozen_guard_under_par_count": sum(
                row["combined_entry_cost_under_par"]
                for row in frozen
            ),
            "rows": witnesses,
        },
        "mandatory_disclosures": {
            "post_to_strict_reversals": POST_TO_STRICT_REVERSALS,
            "permanently_unavailable_legs_before": 106,
            "permanently_unavailable_legs_after": 82,
            "window1_legs_before": 45,
            "window1_legs_after": 146,
        },
        "provenance": {
            "independent_audit_branch": (
                "origin/audit/window1-independent"
            ),
            "independent_audit_commit": (
                "9919de9462f3df4a0bd33239b7e8f648b71e20fb"
            ),
            "independent_artifact": (
                "START_LEDGER_V4_CROSS_REVIEW.md"
            ),
            "v4_ledger_sha256": sha256_file(v4_path),
            "calibration_sha256": sha256_file(calibration_path),
            "historical_events_sha256": sha256_file(
                historical_event_path
            ),
            "historical_legs_sha256": sha256_file(historical_leg_path),
        },
        "blindness": {
            "candidate_scoring_run": False,
            "candidate_results_opened": False,
            "holdout_opened": False,
        },
    }

    ledger_path = output / "REAL_START_LEDGER_V5.jsonl"
    summary_path = output / "REAL_START_SUMMARY_V5.json"
    witness_path = output / "HISTORICAL_WITNESSES_GUARDED.json"
    report_path = output / "START_LEDGER_V5_CORRECTION_REPORT.md"
    write_jsonl(ledger_path, repaired)
    write_json(summary_path, summary)
    write_json(witness_path, summary["historical_witnesses"])
    report_path.write_text(markdown(summary), encoding="utf-8")
    manifest = {
        "schema_version": VERSION + "-manifest",
        "D": D_REQUIRED,
        "candidate_scoring_run": False,
        "holdout_opened": False,
        "artifacts": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in (
                ledger_path, summary_path, witness_path, report_path
            )
        },
    }
    write_json(output / "ARTIFACT_MANIFEST.json", manifest)
    print(json.dumps({
        "D": D_REQUIRED,
        "partition": partition,
        "positive_capable": summary[
            "positive_capable_after_named_censors"
        ],
        "strict_60": len(strict_60),
        "strict_60_under_par": 3,
        "frozen_guard_strict": len(frozen),
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--v4-ledger", required=True)
    result.add_argument("--calibration", required=True)
    result.add_argument("--historical-events", required=True)
    result.add_argument("--historical-legs", required=True)
    result.add_argument("--output-dir", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
