#!/usr/bin/env python3
"""Re-adjudicate frozen historical fills against a frozen start ledger.

This is not candidate scoring.  It changes no placement, cancellation, fill,
quantity, or reference value.  It only classifies already-published exchange
receipts against the independently extracted real-start boundary.
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


VERSION = "window1-start-replay-adjudication-v1"
D = 804
LEGS = 1_608
UTC = dt.timezone.utc


class AdjudicationError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdjudicationError(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise AdjudicationError(
                    f"expected object: {path}:{line_number}"
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
        return None
    return stamp.timestamp()


def adjudicate_leg(
    leg: Mapping[str, Any],
    start: Mapping[str, Any],
) -> dict[str, Any]:
    status = str(leg.get("source_lifecycle_status") or "")
    exact_five = (
        status == "exact_filled_five"
        and leg.get("exact_five_quantity") is True
        and math.isclose(
            float(leg.get("official_fill_quantity") or 0),
            5.0,
            abs_tol=1e-9,
        )
    )
    clocks = leg.get("placement_fill_causality") or {}
    causal_placement = (
        clocks.get("all_filled_orders_have_causal_exchange_clock") is True
    )
    completion = parse_ts(clocks.get("completion_exchange_ts"))
    precision = str(start.get("precision_class") or "")
    exact_start = parse_ts(start.get("exact_start_utc"))
    lower = parse_ts(start.get("not_live_through_utc"))
    live_by = parse_ts(start.get("known_live_by_utc"))
    proven_w1 = False
    proven_post = False
    if (
        status in {"exact_filled_five", "exact_filled_other_quantity"}
        and completion is not None
    ):
        if precision == "exact" and exact_start is not None:
            proven_w1 = bool(
                exact_five and causal_placement and completion < exact_start
            )
            proven_post = completion >= exact_start
        elif precision == "clean_interval":
            proven_w1 = bool(
                exact_five and causal_placement and lower is not None
                and completion <= lower
            )
            proven_post = bool(
                live_by is not None and completion >= live_by
            )
        elif precision in {"live_by_only", "contradictory"}:
            proven_post = bool(
                live_by is not None and completion >= live_by
            )
    if status == "exact_nonfill":
        ruling = "historical_exact_nonfill"
    elif status == "exact_filled_other_quantity":
        ruling = "historical_other_quantity_fill"
    elif proven_w1:
        ruling = "historical_exact_five_window1_fill"
    elif proven_post:
        ruling = "historical_receipt_proven_post_start_fill"
    elif status == "exact_filled_five":
        ruling = "historical_exact_five_timing_censored"
    else:
        ruling = "historical_lifecycle_censored"
    return {
        "schema_version": VERSION,
        "event_id": str(leg["event_id"]),
        "ticker": str(leg["ticker"]),
        "source_lifecycle_status": status,
        "official_fill_quantity": leg.get("official_fill_quantity"),
        "official_fill_vwap_cents": leg.get(
            "official_fill_vwap_cents"
        ),
        "exact_five_quantity": exact_five,
        "ten_contract_overfill": (
            leg.get("ten_contract_overfill") is True
        ),
        "start_precision_class": precision,
        "start_selected_source": start.get("selected_source"),
        "causal_placement_clock": causal_placement,
        "completion_exchange_ts": completion,
        "proven_window1_exact_five": proven_w1,
        "proven_post_start_fill": proven_post,
        "ruling": ruling,
        "schedule_used_to_prove_positive": False,
        "placement_or_fill_modified": False,
    }


def adjudicate(
    starts: list[dict[str, Any]],
    published_legs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if (
        len(starts) != D or len(published_legs) != LEGS
        or len({row["event_id"] for row in starts}) != D
        or len({row["ticker"] for row in published_legs}) != LEGS
    ):
        raise AdjudicationError("immutable denominator changed")
    starts_by_event = {
        str(row["event_id"]): row for row in starts
    }
    legs = [
        adjudicate_leg(row, starts_by_event[str(row["event_id"])])
        for row in published_legs
    ]
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in legs:
        by_event[row["event_id"]].append(row)
    events = []
    for event_id in sorted(by_event):
        rows = by_event[event_id]
        if len(rows) != 2:
            raise AdjudicationError(f"not a dual event: {event_id}")
        historical_dual = all(
            row["exact_five_quantity"] for row in rows
        )
        strict_w1_dual = all(
            row["proven_window1_exact_five"] for row in rows
        )
        combined = (
            sum(float(row["official_fill_vwap_cents"]) for row in rows)
            if historical_dual and all(
                row["official_fill_vwap_cents"] is not None
                for row in rows
            )
            else None
        )
        events.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "start_precision_class": (
                starts_by_event[event_id]["precision_class"]
            ),
            "historical_dual_exact_five": historical_dual,
            "strict_dual_exact_five_window1": strict_w1_dual,
            "contains_receipt_proven_post_start_leg": any(
                row["proven_post_start_fill"] for row in rows
            ),
            "combined_entry_cost_cents": combined,
            "combined_entry_cost_under_par": (
                combined < 100 if combined is not None else None
            ),
            "leg_tickers": [row["ticker"] for row in rows],
        })
    duals = [row for row in events if row["historical_dual_exact_five"]]
    recovered = [
        row for row in duals if row["strict_dual_exact_five_window1"]
    ]
    summary = {
        "schema_version": VERSION,
        "D": D,
        "historical_dual_exact_five_events": len(duals),
        "historical_dual_events_with_receipt_proven_post_start_leg": sum(
            row["contains_receipt_proven_post_start_leg"] for row in duals
        ),
        "newly_recovered_historical_strict_window1_duals": len(recovered),
        "newly_recovered_historical_dual_events": [
            {
                "event_id": row["event_id"],
                "combined_entry_cost_cents": row[
                    "combined_entry_cost_cents"
                ],
                "combined_entry_cost_under_par": row[
                    "combined_entry_cost_under_par"
                ],
            }
            for row in recovered
        ],
        "permanently_post_start_filled_legs": sum(
            row["proven_post_start_fill"] for row in legs
        ),
        "permanently_post_start_fill_events": len({
            row["event_id"] for row in legs
            if row["proven_post_start_fill"]
        }),
        "ruling_counts": dict(Counter(row["ruling"] for row in legs)),
        "ten_contract_overfill_outside_exact_five": sum(
            row["ten_contract_overfill"] for row in legs
        ),
        "placement_cancellation_fill_values_modified": False,
        "candidate_policy_scoring_performed": False,
    }
    if (
        len(duals) != 31
        or summary["ten_contract_overfill_outside_exact_five"] != 1
    ):
        raise AdjudicationError(
            f"historical conservation changed: {summary}"
        )
    return legs, events, summary


def report(summary: Mapping[str, Any]) -> str:
    recovered = summary[
        "newly_recovered_historical_dual_events"
    ]
    recovered_text = (
        "\n".join(
            f"- {row['event_id']}: "
            f"{row['combined_entry_cost_cents']:.2f} cents, "
            f"under par = {row['combined_entry_cost_under_par']}"
            for row in recovered
        )
        if recovered else "- none"
    )
    return f"""# Historical execution re-adjudication against start ledger v3

No placement, cancellation, fill, quantity, or price was changed.

- historical dual exact-five witnesses = {summary['historical_dual_exact_five_events']}
- dual witnesses with a receipt-proven post-start leg = {summary['historical_dual_events_with_receipt_proven_post_start_leg']}
- permanently post-start filled legs = {summary['permanently_post_start_filled_legs']}
- permanently post-start fill events = {summary['permanently_post_start_fill_events']}
- newly recovered strict Window-1 historical duals = {summary['newly_recovered_historical_strict_window1_duals']}
- ten-contract overfill outside exact-five = {summary['ten_contract_overfill_outside_exact_five']}

## Newly recovered historical duals

{recovered_text}

This is historical receipt adjudication only.  It is not a candidate result
and does not test an alternative OS-family policy.
"""


def run(args: argparse.Namespace) -> int:
    starts_path = Path(args.start_ledger).resolve()
    published_path = Path(args.published_leg_ledger).resolve()
    output = Path(args.output).resolve()
    legs, events, summary = adjudicate(
        read_jsonl(starts_path), read_jsonl(published_path)
    )
    summary["inputs"] = {
        "start_ledger": {
            "sha256": sha256_file(starts_path),
            "bytes": starts_path.stat().st_size,
        },
        "published_leg_ledger": {
            "sha256": sha256_file(published_path),
            "bytes": published_path.stat().st_size,
        },
    }
    write_jsonl(output / "HISTORICAL_START_RULINGS_LEGS.jsonl", legs)
    write_jsonl(output / "HISTORICAL_START_RULINGS_EVENTS.jsonl", events)
    write_json(output / "HISTORICAL_START_RULING_SUMMARY.json", summary)
    (output / "HISTORICAL_START_RULING_REPORT.md").write_text(
        report(summary), encoding="utf-8", newline="\n"
    )
    print(compact({
        "historical_duals": summary[
            "historical_dual_exact_five_events"
        ],
        "post_start_duals": summary[
            "historical_dual_events_with_receipt_proven_post_start_leg"
        ],
        "new_window1_duals": summary[
            "newly_recovered_historical_strict_window1_duals"
        ],
    }))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--start-ledger", required=True)
    result.add_argument("--published-leg-ledger", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
