#!/usr/bin/env python3
"""Materialize the exact hash-bound 342-tape sealed exam input bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tarfile


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--declaration", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    declaration = json.loads(Path(args.declaration).read_text(encoding="utf-8"))
    legs = [leg for event in declaration["events"] for leg in event["legs"]]
    if len(legs) != 342:
        raise RuntimeError("sealed tape denominator is not 342")
    output = Path(args.output).resolve()
    if output.exists():
        raise RuntimeError("sealed tape bundle already exists")
    with tarfile.open(output, "w") as bundle:
        for leg in sorted(legs, key=lambda row: row["ticker"]):
            source = Path(leg["remote_path"])
            if not source.is_file():
                raise RuntimeError(f"sealed tape absent: {source}")
            got = sha256_file(source)
            if got != leg["sha256"]:
                raise RuntimeError(f"sealed tape hash mismatch: {source}")
            bundle.add(source, arcname=source.name, recursive=False)
    print(json.dumps({
        "files": len(legs),
        "bytes": os.path.getsize(output),
        "sha256": sha256_file(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
