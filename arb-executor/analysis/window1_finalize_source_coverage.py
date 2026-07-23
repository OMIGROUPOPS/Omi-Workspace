#!/usr/bin/env python3
"""Finalize a completed source census without rescanning immutable evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "window1-source-coverage-finalizer-v1"


class FinalizeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def count_jsonl(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(bool(line.strip()) for line in handle)


def finalize(
    summary: dict[str, Any],
    *,
    ledger_path: Path,
    depth_dir: Path,
) -> dict[str, Any]:
    if (
        summary.get("D") != 804
        or summary.get("required_tickers") != 1608
        or summary.get("event_counts", {}).get(
            "both_legs_minimum_instrument"
        ) != 804
    ):
        raise FinalizeError("source coverage gate/grain is not complete")
    if count_jsonl(ledger_path) != 804:
        raise FinalizeError("source coverage ledger is not 804 rows")
    files = sorted(depth_dir.glob("depth_202607*.jsonl.gz"))
    depth = summary.get("depth_recorder") or {}
    if (
        len(files) != depth.get("file_count")
        or depth.get("physical_rows") != 2_836_510
    ):
        raise FinalizeError("frozen depth snapshot grain changed")
    observed_bytes = sum(path.stat().st_size for path in files)
    receipt = summary.get(
        "depth_recorder_receipt_reconciliation"
    ) or {}
    claim = receipt.get("receipt_claim") or {}
    claimed_bytes = int(claim.get("bytes") or 0)
    if claimed_bytes <= observed_bytes:
        raise FinalizeError("depth receipt no longer exceeds snapshot")
    depth["bytes"] = observed_bytes
    receipt["frozen_snapshot_observed"]["bytes"] = observed_bytes
    receipt["not_preserved_in_frozen_snapshot"]["bytes"] = (
        claimed_bytes - observed_bytes
    )
    output = dict(summary)
    output.update({
        "coverage_finalizer_version": VERSION,
        "depth_recorder": depth,
        "depth_recorder_receipt_reconciliation": receipt,
        "artifacts": {
            "source_coverage_ledger_sha256": sha256_file(ledger_path),
        },
        "report_only_correction": (
            "adds compressed byte totals omitted by the completed scanner; "
            "no event, ticker, row, availability, or source ruling changed"
        ),
    })
    return output


def run(args: argparse.Namespace) -> int:
    summary_path = Path(args.summary).resolve()
    ledger_path = Path(args.ledger).resolve()
    output_path = Path(args.output).resolve()
    if output_path.exists():
        raise FinalizeError("refusing to overwrite final coverage receipt")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    output = finalize(
        summary,
        ledger_path=ledger_path,
        depth_dir=Path(args.depth_recorder_dir).resolve(),
    )
    output["artifacts"]["raw_scan_summary_sha256"] = sha256_file(
        summary_path
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "D": output["D"],
        "minimum_instrument_events": output["event_counts"][
            "both_legs_minimum_instrument"
        ],
        "depth_snapshot_bytes": output["depth_recorder"]["bytes"],
        "ledger_sha256": output["artifacts"][
            "source_coverage_ledger_sha256"
        ],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--summary", required=True)
    result.add_argument("--ledger", required=True)
    result.add_argument("--depth-recorder-dir", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
