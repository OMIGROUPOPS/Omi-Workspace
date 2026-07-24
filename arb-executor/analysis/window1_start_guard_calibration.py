#!/usr/bin/env python3
"""Derive the frozen asymmetric TE proxy guard from official starts."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import window1_start_truth_round2 as round2


VERSION = "window1-start-guard-calibration-v1"


class CalibrationError(RuntimeError):
    """A calibration input or frozen empirical invariant failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_directory(path: Path, pattern: str) -> dict[str, Any]:
    rows = []
    for item in sorted(path.glob(pattern), key=lambda value: value.name):
        rows.append({
            "name": item.name,
            "bytes": item.stat().st_size,
            "sha256": sha256_file(item),
        })
    digest = hashlib.sha256(
        json.dumps(
            rows, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    return {"files": len(rows), "hash_set_sha256": digest}


def derive(
    baseline_path: Path,
    milestone_raw_dir: Path,
    te_results_dir: Path,
) -> dict[str, Any]:
    baseline = round2.read_jsonl(baseline_path)
    te_matches, te_receipt = round2.parse_te_pages(te_results_dir)
    by_title: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for match in te_matches:
        by_title[tuple(match["title_pair"])].append(match)

    official = {
        str(row["event_id"]): row for row in baseline
        if row.get("precision_class") == "exact"
    }
    differences: list[tuple[str, float]] = []
    for event_id, row in sorted(official.items()):
        path = milestone_raw_dir / f"{event_id}.json.gz"
        if not path.is_file():
            continue
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            raw = json.load(handle)
        milestones = [
            value
            for page in raw.get("pages") or []
            for value in (page.get("response") or {}).get(
                "milestones"
            ) or []
        ]
        if not milestones:
            continue
        milestone = milestones[0]
        start_date = milestone.get("start_date")
        tournament = (milestone.get("details") or {}).get(
            "tournament_name"
        )
        candidates = [
            match
            for match in by_title.get(
                round2.title_pair(milestone.get("title")), []
            )
            if match["completed_result"]
            and match["start_utc"] is not None
            and round2.tournament_matches(
                tournament, match["tournament"]
            )
            and round2.date_distance(
                match["page_date"], start_date
            ) is not None
            and round2.date_distance(
                match["page_date"], start_date
            ) <= 2
        ]
        if len(candidates) != 1:
            continue
        official_ts = round2.parse_ts(row.get("exact_start_utc"))
        if official_ts is None:
            raise CalibrationError(
                f"official exact row lacks timestamp: {event_id}"
            )
        differences.append(
            (event_id, float(candidates[0]["start_utc"] - official_ts))
        )

    values = [value for _, value in differences]
    if len(official) != 234 or len(values) != 222:
        raise CalibrationError(
            "official/comparable calibration population changed: "
            f"{len(official)}/{len(values)}"
        )
    median = float(statistics.median(values))
    if median != 300.0:
        raise CalibrationError(f"calibration median changed: {median}")

    # The central calibrated set is the empirically reported 15-minute
    # absolute band (207/222).  Its signed extrema mechanically yield the
    # asymmetric interval: proxy-900s through proxy+600s.
    central = [value for value in values if abs(value) <= 900]
    positive_guard = max(central)
    negative_guard = abs(min(central))
    if (
        len(central) != 207
        or positive_guard != 900.0
        or negative_guard != 600.0
    ):
        raise CalibrationError(
            "derived asymmetric guard changed: "
            f"{len(central)}/{positive_guard}/{negative_guard}"
        )

    return {
        "schema_version": VERSION,
        "purpose": (
            "policy_blind_start_semantics_calibration_before_scoring"
        ),
        "difference_definition": (
            "tennisexplorer_proxy_clock_minus_official_start_seconds"
        ),
        "official_start_population": len(official),
        "comparable_unique_crosswalks": len(values),
        "median_seconds": median,
        "five_minute_grid_proxy_rows": 453,
        "signed_counts": {
            "negative": sum(value < 0 for value in values),
            "zero": sum(abs(value) <= 1 for value in values),
            "positive": sum(value > 0 for value in values),
        },
        "absolute_15m_central_band": {
            "count": len(central),
            "rate": len(central) / len(values),
            "long_tail_count": len(values) - len(central),
            "long_tail_rate": (len(values) - len(central)) / len(values),
        },
        "derived_guard": {
            "guard_id": "te-calibration-central-93pct-asymmetric-v1",
            "actual_start_interval": (
                "[proxy_clock-900s, proxy_clock+600s]"
            ),
            "positive_guard_seconds": positive_guard,
            "negative_guard_seconds": negative_guard,
            "strict_window1_law": (
                "completion_exchange_ts <= proxy_clock-900s"
            ),
            "strict_post_start_law": (
                "completion_exchange_ts >= proxy_clock+600s"
            ),
            "inside_band_law": "censored",
        },
        "calibration_outliers_abs_over_15m": [
            {"event_id": event_id, "difference_seconds": value}
            for event_id, value in differences if abs(value) > 900
        ],
        "input_receipts": {
            "baseline_v3_ledger": {
                "bytes": baseline_path.stat().st_size,
                "sha256": sha256_file(baseline_path),
            },
            "official_milestone_pages": hash_directory(
                milestone_raw_dir, "*.json.gz"
            ),
            "tennisexplorer_pages": hash_directory(
                te_results_dir, "results-*.html.gz"
            ),
            "tennisexplorer_parser_receipt": te_receipt,
        },
        "blindness": {
            "candidate_results_read": False,
            "placements_read": False,
            "fills_read": False,
            "prices_read": False,
            "deltas_read": False,
            "holdout_read": False,
        },
    }


def run(args: argparse.Namespace) -> int:
    output = Path(args.output).resolve()
    if output.exists():
        raise CalibrationError(f"refusing to overwrite: {output}")
    value = derive(
        Path(args.baseline_v3_ledger).resolve(),
        Path(args.official_milestone_raw_dir).resolve(),
        Path(args.tennisexplorer_results_dir).resolve(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(output),
        "guard": value["derived_guard"],
        "blindness": value["blindness"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--baseline-v3-ledger", required=True)
    result.add_argument("--official-milestone-raw-dir", required=True)
    result.add_argument("--tennisexplorer-results-dir", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
