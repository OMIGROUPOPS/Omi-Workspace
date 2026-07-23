#!/usr/bin/env python3
"""Verify local/recovered recorder objects against the immutable Spaces map.

The verifier is offline and read-only.  It emits public-safe object hashes and
logical source classes, never raw paths or credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "window1-spaces-materialization-v1"


class VerificationError(RuntimeError):
    """A source-materialization contract failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest(path: Path, prefix: str) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise VerificationError(
                    f"non-object manifest row {line_number}"
                )
            if row.get("prefix") == prefix:
                rows.append(row)
    tickers = [str(row.get("ticker") or "") for row in rows]
    if not rows or any(not ticker for ticker in tickers):
        raise VerificationError(f"empty/invalid prefix selection: {prefix}")
    if len(set(tickers)) != len(tickers):
        raise VerificationError(f"duplicate ticker in prefix: {prefix}")
    return sorted(rows, key=lambda row: str(row["ticker"]))


def choose(
    ticker: str, primary: Path, recovered: Path,
) -> tuple[Path | None, str]:
    for root, logical in (
        (primary, "production_local_read_only"),
        (recovered, "spaces_recovered_private"),
    ):
        for suffix in (".csv.gz", ".csv"):
            path = root / (ticker + suffix)
            if path.is_file():
                return path, logical
    return None, "missing"


def run(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest).resolve()
    primary = Path(args.primary_dir).resolve()
    recovered = Path(args.recovered_dir).resolve()
    ledger_path = Path(args.ledger_output).resolve()
    summary_path = Path(args.summary_output).resolve()
    rows = read_manifest(manifest, args.prefix)
    ledger = []
    for index, row in enumerate(rows, 1):
        ticker = str(row["ticker"])
        path, logical = choose(ticker, primary, recovered)
        expected_md5 = str(
            (row.get("content_hashes") or {}).get("md5") or ""
        ).lower()
        expected_size = int(row.get("size_bytes") or -1)
        if path is None:
            actual_size = None
            actual_md5 = None
            state = "missing"
        else:
            actual_size = path.stat().st_size
            actual_md5 = md5_file(path)
            state = (
                "exact_spaces_object"
                if expected_md5
                and actual_md5 == expected_md5
                and actual_size == expected_size
                else "content_mismatch"
            )
        ledger.append({
            "schema_version": VERSION,
            "prefix": args.prefix,
            "event_id": row.get("event_id"),
            "ticker": ticker,
            "logical_materialization": logical,
            "spaces_path": row.get("path"),
            "expected_size_bytes": expected_size,
            "actual_size_bytes": actual_size,
            "expected_md5": expected_md5 or None,
            "actual_md5": actual_md5,
            "state": state,
        })
        if index % 100 == 0 or index == len(rows):
            print(f"verified={index}/{len(rows)}", flush=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in ledger:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    counts: dict[str, int] = {}
    locations: dict[str, int] = {}
    for row in ledger:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
        key = str(row["logical_materialization"])
        locations[key] = locations.get(key, 0) + 1
    summary = {
        "schema_version": VERSION,
        "prefix": args.prefix,
        "object_count": len(ledger),
        "states": dict(sorted(counts.items())),
        "logical_materializations": dict(sorted(locations.items())),
        "all_exact": counts == {"exact_spaces_object": len(ledger)},
        "input_manifest_sha256": sha256_file(manifest),
        "output_ledger_sha256": sha256_file(ledger_path),
        "privacy": {
            "raw_absolute_paths_emitted": False,
            "credentials_or_account_data_emitted": False,
        },
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["all_exact"] else 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--manifest", required=True)
    result.add_argument("--prefix", default="ticks")
    result.add_argument("--primary-dir", required=True)
    result.add_argument("--recovered-dir", required=True)
    result.add_argument("--ledger-output", required=True)
    result.add_argument("--summary-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
