#!/usr/bin/env python3
"""Fail-closed changed-path checker for the Window-1 two-seat split."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ANALYSIS_ALLOWLIST = (
    "arb-executor/analysis/second_seat/",
    "arb-executor/tests/analysis_second_seat/",
    "arb-executor/docs/research/window1/second_seat/",
    ".claude/window1_second_seat/",
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, encoding="utf-8"
    ).strip()


def changed_paths(repo: Path, base: str) -> list[str]:
    committed = _git(repo, "diff", "--name-only", f"{base}...HEAD").splitlines()
    working = _git(repo, "status", "--porcelain=v1", "-uall").splitlines()
    work_paths = [row[3:] for row in working if len(row) >= 4]
    return sorted(set(filter(None, committed + work_paths)))


def validate_analysis(paths: list[str]) -> list[str]:
    return [
        path
        for path in paths
        if not any(path.startswith(prefix) for prefix in ANALYSIS_ALLOWLIST)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--seat", choices=("analysis", "live"), required=True)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    paths = changed_paths(repo, args.base)
    violations = validate_analysis(paths) if args.seat == "analysis" else []
    print(f"seat={args.seat}")
    print(f"base={args.base}")
    print(f"changed_paths={len(paths)}")
    for path in paths:
        print(f"PATH {path}")
    if violations:
        for path in violations:
            print(f"VIOLATION {path}")
        return 1
    print("boundary=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

