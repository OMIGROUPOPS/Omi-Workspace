#!/usr/bin/env python3
"""Write the immutable fit/policy/reference receipt before forward holdout."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


FREEZE_VERSION = "window1-fit-freeze-v1"


class FreezeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FreezeError(f"JSON object required: {path}")
    return value


def next_three_dates(timestamp: dt.datetime) -> list[str]:
    if timestamp.tzinfo is None:
        raise FreezeError("freeze timestamp must be timezone-aware")
    day = timestamp.astimezone(dt.timezone.utc).date()
    return [
        (day + dt.timedelta(days=offset)).isoformat()
        for offset in (1, 2, 3)
    ]


def build_receipt(
    fit: dict[str, Any],
    *,
    freeze_timestamp: dt.datetime,
    fit_summary_sha256: str,
    denominator_sha256: str,
) -> dict[str, Any]:
    if fit.get("status") != "fit_complete":
        raise FreezeError("fit result is not complete")
    selected = fit.get("selected_result")
    if not isinstance(selected, dict):
        raise FreezeError("fit result lacks selected_result")
    if selected.get("candidate_id") != fit.get("selected_candidate_id"):
        raise FreezeError("selected candidate identity mismatch")
    raw = selected.get("raw") or {}
    if raw.get("D") != 804:
        raise FreezeError("fit denominator is not immutable D=804")
    dates = next_three_dates(freeze_timestamp)
    return {
        "freeze_version": FREEZE_VERSION,
        "frozen_at_utc": freeze_timestamp.astimezone(
            dt.timezone.utc
        ).isoformat(),
        "fit_period": {
            "start": "2026-07-12",
            "end": "2026-07-20",
            "role": "inspected_development_and_backwalk_history",
        },
        "development_D": 804,
        "development_ledger_sha256": denominator_sha256,
        "fit_summary_sha256": fit_summary_sha256,
        "source_hashes": fit.get("inputs"),
        "selection_rule": fit.get("selection_rule"),
        "selected_candidate_id": selected["candidate_id"],
        "selected_boundary_id": selected["boundary_id"],
        "selected_window_definition": selected["window"],
        "selected_policy_definition": selected["policy"],
        "metric_definitions": fit.get("metric_definitions"),
        "reference_definition": {
            "name": "own_window1_close_true_print",
            "leg_delta": (
                "entry VWAP minus the leg's final positive-size, "
                "exchange-trade-identified public true print at or before the "
                "frozen Window-1 right edge"
            ),
            "pair_delta": "sum of the two individual leg deltas",
            "combined_cost": (
                "sum of two five-contract entry VWAPs; compared separately "
                "with strict par 100"
            ),
            "later_close_exit_settlement_inputs": False,
        },
        "fit_result_raw": raw,
        "fit_result_percentages": selected.get("percentages"),
        "fit_result_bounds": selected.get("bounds"),
        "forward_holdout": {
            "selection_rule": (
                "first three complete UTC dates strictly after the UTC "
                "date containing this fit freeze"
            ),
            "dates": dates,
            "evaluation_count_allowed": 1,
            "viewed": False,
            "dates_may_not_be_extended_or_replaced_after_viewing": True,
            "minimum_complete_after_utc": (
                dt.datetime.fromisoformat(dates[-1])
                .replace(tzinfo=dt.timezone.utc)
                + dt.timedelta(days=1)
            ).isoformat(),
        },
        "window2_exit_settlement_dca_used": False,
    }


def run(args: argparse.Namespace) -> int:
    fit_path = Path(args.fit_summary).resolve()
    ledger_path = Path(args.event_ledger).resolve()
    output_path = Path(args.output).resolve()
    if output_path.exists():
        raise FreezeError("freeze receipt already exists; refusing overwrite")
    timestamp = (
        dt.datetime.fromisoformat(args.freeze_timestamp.replace("Z", "+00:00"))
        if args.freeze_timestamp
        else dt.datetime.now(dt.timezone.utc)
    )
    receipt = build_receipt(
        load_object(fit_path),
        freeze_timestamp=timestamp,
        fit_summary_sha256=sha256_file(fit_path),
        denominator_sha256=sha256_file(ledger_path),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "selected_candidate_id": receipt["selected_candidate_id"],
        "holdout_dates": receipt["forward_holdout"]["dates"],
        "output": str(output_path),
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--fit-summary", required=True)
    result.add_argument("--event-ledger", required=True)
    result.add_argument("--output", required=True)
    result.add_argument("--freeze-timestamp")
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
