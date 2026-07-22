#!/usr/bin/env python3
"""Publish an identifier-free aggregate of a private validation run."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


SAFE_FIELDS = (
    "schema_version", "benchmark_version", "gate_pass", "pass_rule",
    "floor_passing_events", "entry_attempts_compared", "orders_compared",
    "failed_attempts_compared", "matched_failed_attempts", "matched_fills",
    "matched_nonfills", "causal_nonplacement_legs",
    "causal_nonplacement_events", "unobserved_decision_legs",
    "decision_contract_errors", "accepted_orders_missing_terminal_receipt",
    "receipt_validation_errors", "counterfactual_replay", "mismatch_count",
    "mismatch_types", "strategy_scoring_permitted",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--mismatches", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    counts = collections.Counter()
    details = collections.Counter()
    with Path(args.mismatches).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise ValueError(
                    f"mismatch row {line_number} is malformed") from exc
            mismatch_type = str(row.get("mismatch_type") or "unknown")
            detail = str(row.get("detail") or "unspecified")
            counts[mismatch_type] += 1
            details[(mismatch_type, detail)] += 1
    if sum(counts.values()) != summary.get("mismatch_count"):
        raise ValueError("summary and mismatch row counts disagree")
    if dict(sorted(counts.items())) != summary.get("mismatch_types"):
        raise ValueError("summary and mismatch type counts disagree")
    public = {key: summary.get(key) for key in SAFE_FIELDS if key in summary}
    public["public_schema_version"] = "window1-validation-sanitized-v2"
    public["mismatch_detail_census"] = [
        {"mismatch_type": key[0], "detail": key[1], "count": count}
        for key, count in sorted(details.items())
    ]
    public["private_identifiers_emitted"] = False
    public["raw_mismatch_rows_emitted"] = False
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(public, indent=2, sort_keys=True) + chr(10),
        encoding="utf-8",
    )
    print(json.dumps({
        "gate_pass": public.get("gate_pass"),
        "mismatch_count": public.get("mismatch_count"),
        "private_identifiers_emitted": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
