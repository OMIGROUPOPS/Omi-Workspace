#!/usr/bin/env python3
"""Versioned wrapper for unchanged Round-4 score-separated diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path

import window1_round4_diagnostics as diagnostics
import window1_round4_instrument_v2 as r4v2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--streams", type=Path, required=True)
    parser.add_argument("--round3-results-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    original = diagnostics.r4
    diagnostics.r4 = r4v2
    try:
        receipt, calibration, census = diagnostics.build(
            repo=repo,
            events_path=args.events.resolve(),
            cache_root=args.market_cache.resolve(),
            streams_path=args.streams.resolve(),
            round3_results_dir=args.round3_results_dir.resolve(),
            opportunity_path=(
                output / "WINDOW1_OPPORTUNITY_LEDGER_V2.jsonl.gz"
            ),
        )
    finally:
        diagnostics.r4 = original
    receipt["schema_version"] = "window1-round4-diagnostics-v2"
    receipt["V2_policy_overlay"] = r4v2.VERSION
    diagnostics.write_json(
        output / "ROUND4_V2_DIAGNOSTIC_RECEIPT.json", receipt
    )
    diagnostics.write_json(
        output / "CAUSAL_REFERENCE_CALIBRATION_V2.json", calibration
    )
    diagnostics.write_json(
        output / "ORACLE_FALSE_NEGATIVE_CENSUS_V2.json", census
    )
    (
        output / "WINDOW1_OPPORTUNITY_LEDGER_MANIFEST.json"
    ).replace(output / "WINDOW1_OPPORTUNITY_LEDGER_V2_MANIFEST.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
