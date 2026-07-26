#!/usr/bin/env python3
"""Compare two fresh score-free regenerations byte for byte."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import window1_round4_macromicro_prerun_builder as builder


class VerifyError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--regenerated", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    names = sorted(builder.OUTPUT_FILENAMES.values())
    rows = []
    for name in names:
        left, right = args.reference / name, args.regenerated / name
        if not left.is_file() or not right.is_file():
            raise VerifyError(f"missing deterministic artifact: {name}")
        left_hash, right_hash = sha256(left), sha256(right)
        if left_hash != right_hash or left.stat().st_size != right.stat().st_size:
            raise VerifyError(f"regeneration mismatch: {name}")
        rows.append({
            "path": name,
            "bytes": left.stat().st_size,
            "reference_sha256": left_hash,
            "regenerated_sha256": right_hash,
            "byte_identical": True,
        })
    args.receipt.write_text(json.dumps({
        "schema_version": "round4-macromicro-regeneration-v1",
        "artifact_count": len(rows),
        "all_byte_identical": True,
        "artifacts": rows,
        "scorer_invocation_count": 0,
        "metrics": None,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
