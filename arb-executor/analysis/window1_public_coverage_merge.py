#!/usr/bin/env python3
"""Merge a completed public-tape export into a prior source coverage census."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "window1_source_coverage", HERE / "window1_source_coverage.py"
)
coverage = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(coverage)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                output.append(json.loads(line))
    return output


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(args: argparse.Namespace) -> int:
    base_ledger_path = Path(args.base_ledger).resolve()
    base_summary_path = Path(args.base_summary).resolve()
    public_path = Path(args.public_prints).resolve()
    ledger = read_jsonl(base_ledger_path)
    if len(ledger) != coverage.D:
        raise coverage.CoverageError(
            f"immutable D changed in base ledger: {len(ledger)}"
        )
    public = coverage.load_public_print_coverage(public_path)
    required_tickers = {
        leg["ticker"] for event in ledger for leg in event["legs"]
    }
    for event in ledger:
        for leg in event["legs"]:
            ticker = leg["ticker"]
            source = public.get(
                ticker, {"available": False, "row_count": 0}
            )
            leg["sources"]["exchange_trade_identified_public_tape"] = source
            true_print = source.get("positive_size_rows", 0) > 0
            top5 = leg["sources"].get("premarket_ticks_top5") or {}
            polled = leg["sources"].get("tennis_db_bbo") or {}
            bbo = (
                top5.get("valid_bbo_observed_at_endpoint") is True
                or (top5.get("valid_bbo_rows") or 0) > 0
                or polled.get("valid_bbo_rows", 0) > 0
            )
            leg["minimum_bbo_plus_print_instrument_available"] = (
                bbo and true_print
            )
            failures = [
                value for value in leg.get("join_failures", [])
                if value != (
                    "no_positive_size_exchange_timestamped_true_print"
                )
                and value != "no_causal_bbo_source_joined"
            ]
            if not bbo:
                failures.append("no_causal_bbo_source_joined")
            if not true_print:
                failures.append(
                    "no_positive_size_exchange_timestamped_true_print"
                )
            leg["join_failures"] = failures
        event["both_legs_minimum_instrument_available"] = all(
            leg["minimum_bbo_plus_print_instrument_available"]
            for leg in event["legs"]
        )
    output = Path(args.ledger_output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in ledger:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    summary = json.loads(base_summary_path.read_text(encoding="utf-8"))
    summary["event_counts"] = {
        "both_legs_minimum_instrument": sum(
            row["both_legs_minimum_instrument_available"] for row in ledger
        ),
        "any_leg_missing_minimum_instrument": sum(
            not row["both_legs_minimum_instrument_available"]
            for row in ledger
        ),
    }
    summary["ticker_counts"][
        "exchange_trade_identified_public_print_available"
    ] = len(required_tickers & set(public))
    summary["public_tape"] = {
        "normalized_sha256": sha256_file(public_path),
        "required_ticker_count": len(required_tickers),
        "required_tickers_with_positive_size_prints": sum(
            (public.get(ticker) or {}).get("positive_size_rows", 0) > 0
            for ticker in required_tickers
        ),
        "public_trade_identity_available": True,
        "private_order_or_fill_receipt_required": False,
        "timestamp_semantics": "exchange_created_time",
    }
    summary["coverage_ledger_sha256"] = sha256_file(output)
    Path(args.summary_output).resolve().write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "D": len(ledger),
        "public_tickers": len(required_tickers & set(public)),
        "event_counts": summary["event_counts"],
        "ledger_sha256": summary["coverage_ledger_sha256"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--base-ledger", required=True)
    result.add_argument("--base-summary", required=True)
    result.add_argument("--public-prints", required=True)
    result.add_argument("--ledger-output", required=True)
    result.add_argument("--summary-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
