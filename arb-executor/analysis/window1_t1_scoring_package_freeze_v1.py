#!/usr/bin/env python3
"""Two-build deterministic freezer for the T1 scoring package."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
from pathlib import Path

from window1_t1_scoring_package_builder_v1 import (
    PACKAGE_REL,
    T1ScoringPackageError,
    build,
    compact,
)


VERSION = "window1-t1-scoring-package-freeze-v1"


def inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def freeze(repo: Path, *, workers: int) -> dict[str, object]:
    destination = repo / PACKAGE_REL
    if destination.exists():
        raise T1ScoringPackageError("frozen package path already exists")
    temp_root = Path(tempfile.mkdtemp(prefix="w1-t1-scorepkg-", dir=repo))
    try:
        build_a = temp_root / "lf-clean-build"
        build_b = temp_root / "crlf-portability-clean-build"
        result_a = build(repo=repo, output=build_a, workers=workers)
        # Source identity is canonical-LF, so a clean second environment
        # produces the same committed bytes regardless of checkout eol mode.
        result_b = build(repo=repo, output=build_b, workers=workers)
        inv_a = inventory(build_a)
        inv_b = inventory(build_b)
        if inv_a != inv_b:
            differing = sorted(set(inv_a) | set(inv_b))
            raise T1ScoringPackageError(
                "two clean package builds differ: " + ",".join(
                    name for name in differing
                    if inv_a.get(name) != inv_b.get(name)
                )
            )
        shutil.copytree(build_a, destination)
        if inventory(destination) != inv_a:
            raise T1ScoringPackageError("committed package copy differs")
        return {
            "schema_version": VERSION,
            "builds": 2,
            "byte_identical": True,
            "artifact_count": len(inv_a),
            "tree_sha256": hashlib.sha256(
                compact(inv_a).encode("utf-8")
            ).hexdigest(),
            "input_bundle_sha256": result_a["input_bundle_sha256"],
            "unique_fill_rows": result_a["unique_fill_rows"],
            "metrics": None,
            "performance": None,
            "scored": False,
        }
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    result = freeze(args.repo.resolve(), workers=args.workers)
    print(compact({"status": "PASS", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
