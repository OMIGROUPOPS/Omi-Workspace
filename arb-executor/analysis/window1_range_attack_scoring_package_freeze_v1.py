#!/usr/bin/env python3
"""Freeze two byte-identical builds of the Range-Attack scoring package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ANALYSIS_DIR = Path(__file__).resolve().parent
import sys
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

from window1_range_attack_scoring_package_builder_v1 import (  # noqa: E402
    IMPLEMENTATION_PARENT,
    build,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob(repo: Path, path: Path) -> str:
    process = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def inventory(directory: Path) -> dict[str, dict[str, Any]]:
    return {
        path.name: {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


def freeze(repo: Path, output: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="w1ra-score-freeze-a-") as a_raw, \
            tempfile.TemporaryDirectory(prefix="w1ra-score-freeze-b-") as b_raw:
        a = Path(a_raw)
        b = Path(b_raw)
        build(repo, a)
        build(repo, b)
        first = inventory(a)
        second = inventory(b)
        if first != second:
            raise RuntimeError("fresh scoring-package builds differ")
        output.mkdir(parents=True, exist_ok=True)
        permitted_existing = set(first) | {
            "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json",
            "PACKAGE_ARTIFACT_MANIFEST.json",
        }
        unexpected = {
            path.name for path in output.iterdir()
            if path.name not in permitted_existing
        }
        if unexpected:
            raise RuntimeError(
                "refusing unexpected existing package files: "
                + ",".join(sorted(unexpected))
            )
        for path in sorted(a.iterdir()):
            shutil.copyfile(path, output / path.name)
    receipt = {
        "schema_version": (
            "window1-range-attack-scoring-package-regeneration-v1"
        ),
        "implementation_parent": IMPLEMENTATION_PARENT,
        "build_command": (
            "python -B arb-executor/analysis/"
            "window1_range_attack_scoring_package_freeze_v1.py "
            "--repo . --output-dir "
            ".claude/window1_range_attack_scoring_package_prerun_20260726"
        ),
        "fresh_builds_compared": 2,
        "core_file_count": len(first),
        "first_build": first,
        "second_build": second,
        "byte_identical": True,
        "scorer_invoked": False,
        "real_population_scored": False,
        "metrics": {"C": None, "PC": None, "S": None, "IC": None},
    }
    write_json(output / "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json", receipt)
    rows = []
    for path in sorted(output.iterdir()):
        if path.name == "PACKAGE_ARTIFACT_MANIFEST.json":
            continue
        rows.append({
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "git_blob_oid": git_blob(repo, path),
        })
    artifact_manifest = {
        "schema_version": (
            "window1-range-attack-scoring-package-artifacts-v1"
        ),
        "implementation_parent": IMPLEMENTATION_PARENT,
        "artifact_count_excluding_manifest": len(rows),
        "artifacts": rows,
        "all_performance_metrics_null": True,
        "scorer_invoked": False,
    }
    write_json(output / "PACKAGE_ARTIFACT_MANIFEST.json", artifact_manifest)
    return {
        "core_files": len(first),
        "total_files": len(list(output.iterdir())),
        "byte_identical": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (repo / args.output_dir).resolve()
    )
    result = freeze(repo, output)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
