#!/usr/bin/env python3
"""Re-run only the frozen N=20 public-print reconciliation.

This diagnostic consumes the completed canonical ledger and raw-independent
nightly endpoint method.  It never invokes a policy or emits a score row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import window1_nightly_reconciliation as nightly
import window1_v47_exam_print_repull as repull


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population-declaration", required=True)
    parser.add_argument("--event-list", required=True)
    parser.add_argument("--boundary-ledger", required=True)
    parser.add_argument("--prints", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-size", type=int, default=20)
    args = parser.parse_args()
    events, _, _, list_bytes = repull.load_population(Path(args.population_declaration), Path(args.event_list))
    event_list_hash = hashlib.sha256(list_bytes).hexdigest()
    sample = nightly.deterministic_sample(events, "V47-SEALED-EXAM-" + event_list_hash, args.sample_size)
    boundaries = {row["event_id"]: row for row in repull.read_jsonl(Path(args.boundary_ledger))}
    if set(boundaries) != {event["event_id"] for event in events}:
        raise RuntimeError("boundary/event population mismatch")
    right_by_ticker = {
        leg["ticker"]: float(boundaries[event["event_id"]]["right_edge_epoch"])
        for event in events for leg in event["legs"]
    }
    sample_tickers = {leg["ticker"] for event in sample for leg in event["legs"]}
    by_ticker = {ticker: {} for ticker in sample_tickers}
    with Path(args.prints).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("ticker") in by_ticker:
                identity = row["trade_id"]
                if identity in by_ticker[row["ticker"]] and by_ticker[row["ticker"]][identity] != row:
                    raise RuntimeError(f"conflicting canonical sample duplicate {identity}")
                by_ticker[row["ticker"]][identity] = row
    result = repull.reconcile(sample, by_ticker, right_by_ticker, event_list_hash, args.sample_size)
    receipt = {
        "schema_version": "window1-v47-sealed-exam-print-reconciliation-focused-v1",
        "policy_invocations": 0,
        "score_rows": 0,
        "population_event_list_sha256": event_list_hash,
        "boundary_ledger_sha256": repull.sha_file(Path(args.boundary_ledger)),
        "canonical_prints_sha256": repull.sha_file(Path(args.prints)),
        "canonical_prints_bytes": Path(args.prints).stat().st_size,
        "canonical_prints_rows": sum(1 for _ in Path(args.prints).open("rb")),
        "sample_tickers": len(sample_tickers),
        "nightly_method_spot_reconciliation": result,
    }
    Path(args.output).write_bytes(canonical(receipt))
    print(json.dumps({"pass": result["pass"], "verdicts": result["verdicts"], "totals": result["totals"]}, sort_keys=True))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
