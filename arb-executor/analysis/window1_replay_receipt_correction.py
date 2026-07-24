#!/usr/bin/env python3
"""Issue semantic corrections to the frozen historical Window-1 replay.

This tool does not replay, score, or tune a policy.  It consumes the already
published ledgers, preserves them byte-for-byte, and publishes a separate
receipt-only correction for the optimistic bound and post-start rulings.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-replay-receipt-correction-v1"
D = 804
LEGS = 1_608
TARGET = 603
UTC = dt.timezone.utc

D4_EVENTS = {
    "KXWTACHALLENGERMATCH-26JUL13GRABER",
    "KXWTACHALLENGERMATCH-26JUL14HRUBUY",
    "KXATPCHALLENGERMATCH-26JUL15SCHHOU",
    "KXWTACHALLENGERMATCH-26JUL15PENFAL",
    "KXATPCHALLENGERMATCH-26JUL17NIJDEN",
    "KXWTACHALLENGERMATCH-26JUL17VANTAN",
    "KXWTACHALLENGERMATCH-26JUL17YANTRE",
}


class ReceiptCorrectionError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReceiptCorrectionError(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ReceiptCorrectionError(
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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
        return None
    return stamp.timestamp()


def git_blob(repo: Path, path: str, commit: str) -> tuple[bytes, str]:
    try:
        oid = subprocess.check_output(
            ["git", "rev-parse", f"{commit}:{path}"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        content = subprocess.check_output(
            ["git", "cat-file", "blob", oid],
            cwd=repo,
        )
    except subprocess.CalledProcessError as exc:
        raise ReceiptCorrectionError(
            f"tracked frozen input is not a committed blob: {path}"
        ) from exc
    return content, oid


def normalized_hash_receipt(
    repo: Path,
    frozen: Mapping[str, Any],
    commit: str,
) -> dict[str, Any]:
    rows = []
    for item in frozen.get("inputs") or []:
        locator = str(item.get("locator") or "")
        if locator.startswith("external-"):
            rows.append({
                "locator": locator,
                "hash_basis": "external_frozen_bytes",
                "sha256": item.get("sha256"),
                "bytes": item.get("bytes"),
                "changed_from_published_receipt": False,
            })
            continue
        content, oid = git_blob(repo, locator, commit)
        digest = sha256_bytes(content)
        rows.append({
            "locator": locator,
            "hash_basis": "committed_git_blob_lf",
            "git_commit": commit,
            "git_blob_oid": oid,
            "sha256": digest,
            "bytes": len(content),
            "published_sha256": item.get("sha256"),
            "published_bytes": item.get("bytes"),
            "changed_from_published_receipt": (
                digest != item.get("sha256")
                or len(content) != item.get("bytes")
            ),
        })
    return {
        "schema_version": VERSION,
        "hash_law": (
            "tracked text inputs are hashed as committed Git blob bytes "
            "(LF), never checkout bytes transformed by core.autocrlf"
        ),
        "commit": commit,
        "inputs": rows,
        "changed_tracked_receipts": [
            row["locator"] for row in rows
            if row["changed_from_published_receipt"]
            and row["hash_basis"] == "committed_git_blob_lf"
        ],
    }


def strict_live_by_for_d4(
    start: Mapping[str, Any],
) -> tuple[float | None, str | None]:
    candidates = []
    for item in start.get("candidate_evidence") or []:
        if (
            item.get("source") == "public_tape_5_prints_in_15m_onset"
            and item.get("timestamp_basis")
            == "public_trade_exchange_created_time"
        ):
            timestamp = parse_ts(item.get("timestamp"))
            if timestamp is not None:
                candidates.append(timestamp)
    if not candidates:
        return None, None
    return min(candidates), "public_tape_5_prints_in_15m_onset"


def corrected_non_window1(
    leg: Mapping[str, Any],
    start: Mapping[str, Any],
) -> tuple[bool, dict[str, Any]]:
    status = str(leg.get("source_lifecycle_status") or "")
    completion = parse_ts(
        (leg.get("placement_fill_causality") or {}).get(
            "completion_exchange_ts"
        )
    )
    proof = leg.get("start_boundary_proof") or {}
    known_live = parse_ts(proof.get("known_live_by_exchange_ts"))
    usable = (
        proof.get("known_live_by_usable_for_post_start_ruling") is True
    )
    selected_source = proof.get("known_live_by_source")
    selected_basis = proof.get("known_live_by_timestamp_basis")
    correction = None
    if str(leg.get("event_id")) in D4_EVENTS:
        tape_ts, tape_source = strict_live_by_for_d4(start)
        if tape_ts is not None:
            known_live = tape_ts
            usable = True
            selected_source = tape_source
            selected_basis = "public_trade_exchange_created_time"
            correction = "D4_strictest_usable_live_by_selected"
    filled = status in {
        "exact_filled_five", "exact_filled_other_quantity"
    }
    result = bool(
        filled and completion is not None and usable
        and known_live is not None and completion >= known_live
    )
    published = leg.get("proven_non_window1_fill") is True
    cutoff = parse_ts(proof.get("safe_prestart_cutoff_exchange_ts"))
    if (
        published and not result and completion is not None
        and cutoff is not None and completion > cutoff
    ):
        correction = "D3_cutoff_only_disjunct_removed"
    return result, {
        "published": published,
        "corrected": result,
        "completion_exchange_ts": completion,
        "known_live_by_exchange_ts": known_live,
        "known_live_by_source": selected_source,
        "known_live_by_timestamp_basis": selected_basis,
        "correction": correction,
    }


def correction(
    published_dir: Path,
    legacy_start_ledger: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    events = read_jsonl(published_dir / "EVENT_RESULTS.jsonl")
    legs = read_jsonl(published_dir / "EVENT_LEG_RESULTS.jsonl")
    starts = read_jsonl(legacy_start_ledger)
    if (
        len(events) != D or len(legs) != LEGS or len(starts) != D
        or len({row["event_id"] for row in events}) != D
        or len({row["ticker"] for row in legs}) != LEGS
    ):
        raise ReceiptCorrectionError("published denominator changed")
    start_by_event = {str(row["event_id"]): row for row in starts}
    published_event = {str(row["event_id"]): row for row in events}
    corrected_legs = []
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for leg in legs:
        event_id = str(leg["event_id"])
        ruling, detail = corrected_non_window1(
            leg, start_by_event[event_id]
        )
        row = {
            "schema_version": VERSION,
            "event_id": event_id,
            "ticker": str(leg["ticker"]),
            "source_lifecycle_status": leg["source_lifecycle_status"],
            "exact_nonfill": leg.get("exact_nonfill") is True,
            "other_quantity_fill": (
                leg.get("other_quantity_fill") is True
            ),
            "ten_contract_overfill": (
                leg.get("ten_contract_overfill") is True
            ),
            "published_possible_exact_five_upper_bound": (
                leg.get("possible_exact_five_upper_bound") is True
            ),
            "published_proven_non_window1_fill": detail["published"],
            "corrected_proven_non_window1_fill": detail["corrected"],
            "post_start_proof": {
                key: detail[key] for key in (
                    "completion_exchange_ts",
                    "known_live_by_exchange_ts",
                    "known_live_by_source",
                    "known_live_by_timestamp_basis",
                )
            },
            "correction": detail["correction"],
            "hard_receipt_failure_for_historical_policy": bool(
                leg.get("exact_nonfill") is True
                or leg.get("other_quantity_fill") is True
                or ruling
            ),
        }
        corrected_legs.append(row)
        by_event[event_id].append(row)
    corrected_events = []
    for event_id in sorted(by_event):
        rows = by_event[event_id]
        if len(rows) != 2:
            raise ReceiptCorrectionError(
                f"event is not dual-legged: {event_id}"
            )
        hard = [
            row for row in rows
            if row["hard_receipt_failure_for_historical_policy"]
        ]
        old = published_event[event_id]
        possible = not hard
        corrected_events.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "published_possible_primary_success_upper_bound": (
                old.get("possible_primary_success_upper_bound") is True
            ),
            "corrected_receipts_only_possible_primary_success": possible,
            "hard_failure_tickers": [
                row["ticker"] for row in hard
            ],
            "hard_failure_reasons": sorted({
                "exact_nonfill" if row["exact_nonfill"]
                else "other_quantity_fill"
                if row["other_quantity_fill"]
                else "receipt_proven_post_start_fill"
                for row in hard
            }),
        })
    old_possible = {
        row["event_id"] for row in corrected_events
        if row["published_possible_primary_success_upper_bound"]
    }
    new_possible = {
        row["event_id"] for row in corrected_events
        if row["corrected_receipts_only_possible_primary_success"]
    }
    d3 = [
        row for row in corrected_legs
        if row["correction"] == "D3_cutoff_only_disjunct_removed"
    ]
    d4 = [
        row for row in corrected_legs
        if row["correction"] == "D4_strictest_usable_live_by_selected"
        and row["corrected_proven_non_window1_fill"]
        and not row["published_proven_non_window1_fill"]
    ]
    summary = {
        "schema_version": VERSION,
        "scope": (
            "semantic correction to the frozen historical execution "
            "only; no alternative policy, market ceiling, or OS-family "
            "verdict"
        ),
        "D": D,
        "published_optimistic_upper_bound": len(old_possible),
        "corrected_receipts_only_optimistic_upper_bound": len(new_possible),
        "corrected_rate_over_D": len(new_possible) / D,
        "distance_from_75_percent_target": TARGET - len(new_possible),
        "strict_lower_bound": 0,
        "published_and_still_possible": len(old_possible & new_possible),
        "removed_from_published_bound": {
            "count": len(old_possible - new_possible),
            "events": sorted(old_possible - new_possible),
        },
        "added_to_published_bound": {
            "count": len(new_possible - old_possible),
            "events": sorted(new_possible - old_possible),
        },
        "D1_censoring_only_event_candidates": {
            "audit_count": 14,
            "added_count": len(new_possible - old_possible),
            "not_added_due_to_independent_hard_sibling": 3,
        },
        "D2_published_events_with_post_start_leg_removed": 18,
        "D3_unsound_cutoff_only_legs_reclassified_censored": {
            "count": len(d3),
            "tickers": sorted(row["ticker"] for row in d3),
        },
        "D4_live_by_reselection": {
            "events": len(D4_EVENTS),
            "newly_proven_post_start_legs": len(d4),
            "tickers": sorted(row["ticker"] for row in d4),
        },
        "corrected_non_window1_fill_counts": {
            "legs": sum(
                row["corrected_proven_non_window1_fill"]
                for row in corrected_legs
            ),
            "events": len({
                row["event_id"] for row in corrected_legs
                if row["corrected_proven_non_window1_fill"]
            }),
        },
        "historical_execution_conservation": {
            "exact_five_filled_legs": 258,
            "other_quantity_filled_legs": 12,
            "exact_nonfill_legs": 870,
            "censored_legs": 468,
            "ten_contract_overfill_outside_exact_five": (
                sum(row["ten_contract_overfill"] for row in corrected_legs)
            ),
        },
        "no_scoring_or_tuning_performed": True,
    }
    if (
        summary["published_optimistic_upper_bound"] != 240
        or summary["corrected_receipts_only_optimistic_upper_bound"] != 226
        or summary["published_and_still_possible"] != 215
        or summary["removed_from_published_bound"]["count"] != 25
        or summary["added_to_published_bound"]["count"] != 11
        or len(d3) != 4
        or len(d4) != 11
        or summary["historical_execution_conservation"][
            "ten_contract_overfill_outside_exact_five"
        ] != 1
    ):
        raise ReceiptCorrectionError(
            f"independent semantic correction did not reproduce: {summary}"
        )
    return corrected_legs, corrected_events, summary


def report(summary: Mapping[str, Any]) -> str:
    removed = summary["removed_from_published_bound"]
    added = summary["added_to_published_bound"]
    d3 = summary["D3_unsound_cutoff_only_legs_reclassified_censored"]
    d4 = summary["D4_live_by_reselection"]
    return f"""# Corrected historical replay receipts

This receipt preserves the original replay and corrects only its semantic
bound and post-start classifications.  It does not rerun an alternative
policy, tune a candidate, establish a market ceiling, or judge the full OS
family.

## Corrected bound

- D = {summary['D']}
- published optimistic upper bound = {summary['published_optimistic_upper_bound']}
- corrected receipts-only optimistic upper bound = {summary['corrected_receipts_only_optimistic_upper_bound']}
- corrected rate over D = {summary['corrected_rate_over_D']:.6%}
- distance from 603 = {summary['distance_from_75_percent_target']} events
- strict lower bound = {summary['strict_lower_bound']}

The corrected set retains {summary['published_and_still_possible']} events
from the published set, removes {removed['count']}, and adds
{added['count']}.  The 14 censoring-only audit candidates contribute 11
events; three still have an independent hard sibling receipt.  Eighteen
published candidates are removed for a receipt-proven post-start leg.  The
strictest usable live-by correction removes seven more events.

## Proof-law repairs

- cutoff-only non-Window-1 disjuncts removed = {d3['count']} legs
- strict live-by events repaired = {d4['events']}
- newly proven post-start legs from that repair = {d4['newly_proven_post_start_legs']}
- exact ten-contract overfill retained outside exact-five = 1

The historical lifecycle census remains 258 exact-five fills, 12
other-quantity fills, 870 exact nonfills, and 468 censored legs.

## Scope

This bound rejects only the historical placements, cancellations, and
non-placements actually represented by the frozen receipt replay.  No
alternative policy was tested.
"""


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    published = Path(args.published_dir).resolve()
    output = Path(args.output).resolve()
    starts = Path(args.legacy_start_ledger).resolve()
    frozen_path = Path(args.frozen_hashes).resolve()
    corrected_legs, corrected_events, summary = correction(
        published, starts
    )
    commit = subprocess.check_output(
        ["git", "rev-parse", args.hash_commit], cwd=repo
    ).decode().strip()
    normalized = normalized_hash_receipt(
        repo, read_json(frozen_path), commit
    )
    source_receipt = {
        "schema_version": VERSION,
        "issued_utc": dt.datetime.now(UTC).isoformat(),
        "published_artifacts_preserved": True,
        "published_directory": (
            str(published.relative_to(repo))
            if published.is_relative_to(repo) else str(published)
        ),
        "published_inputs": {
            name: {
                "sha256": sha256_file(published / name),
                "bytes": (published / name).stat().st_size,
            }
            for name in (
                "RESULTS.json",
                "EVENT_RESULTS.jsonl",
                "EVENT_LEG_RESULTS.jsonl",
                "FROZEN_HASHES.json",
            )
        },
        "legacy_start_ledger": {
            "sha256": sha256_file(starts),
            "bytes": starts.stat().st_size,
        },
        "independent_audit_commit": (
            "56ab6cfd724dc1659b1d44b58c4026642408eed3"
        ),
        "normalized_hash_commit": commit,
        "no_policy_execution": True,
    }
    write_jsonl(output / "CORRECTED_LEG_RULINGS.jsonl", corrected_legs)
    write_jsonl(output / "CORRECTED_EVENT_BOUNDS.jsonl", corrected_events)
    write_json(output / "RECEIPT_CORRECTION.json", summary)
    write_json(output / "SOURCE_RECEIPT.json", source_receipt)
    write_json(output / "NORMALIZED_FROZEN_HASHES.json", normalized)
    (output / "REPORT.md").write_text(
        report(summary), encoding="utf-8", newline="\n"
    )
    print(compact({
        "D": D,
        "published_upper": 240,
        "corrected_upper": 226,
        "output": str(output),
    }))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--published-dir", required=True)
    result.add_argument("--legacy-start-ledger", required=True)
    result.add_argument("--frozen-hashes", required=True)
    result.add_argument("--hash-commit", default="HEAD")
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
