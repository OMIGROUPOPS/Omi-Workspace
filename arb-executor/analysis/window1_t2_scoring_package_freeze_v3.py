#!/usr/bin/env python3
"""Two-clean-build freezer for the score-free T2 package V3."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from window1_t2_scoring_package_builder_v3 import build


VERSION = "window1-t2-scoring-package-freeze-v3"


class FreezeError(RuntimeError):
    """The two V3 builds were not byte-identical."""


def manifest(
    root: Path,
    *,
    exclude_determinism: bool = False,
) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not (
            exclude_determinism
            and path.name == "DETERMINISTIC_REGENERATION_RECEIPT.json"
        )
    }


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")).hexdigest()


def freeze(*, repo: Path, output: Path) -> dict[str, object]:
    if output.exists():
        raise FreezeError("frozen V3 output already exists")
    with tempfile.TemporaryDirectory(
        prefix="w1-t2-scorepkg-v3-a-"
    ) as a_text, tempfile.TemporaryDirectory(
        prefix="w1-t2-scorepkg-v3-b-"
    ) as b_text:
        a = Path(a_text) / "package"
        b = Path(b_text) / "package"
        receipt_a = build(repo=repo, output=a)
        receipt_b = build(repo=repo, output=b)
        hashes_a = manifest(a)
        hashes_b = manifest(b)
        if hashes_a != hashes_b:
            mismatch = [
                path for path in sorted(set(hashes_a) | set(hashes_b))
                if hashes_a.get(path) != hashes_b.get(path)
            ]
            raise FreezeError(
                "clean V3 builds differ: " + ",".join(mismatch[:20])
            )
        shutil.copytree(a, output)
    build_regenerable = {
        path: digest for path, digest in hashes_a.items()
        if path != "DETERMINISTIC_REGENERATION_RECEIPT.json"
    }
    frozen_regenerable = manifest(output, exclude_determinism=True)
    if frozen_regenerable != build_regenerable:
        raise FreezeError("frozen V3 differs from clean builds")
    identity = canonical_sha256(build_regenerable)
    receipt = {
        "schema_version": VERSION + "-receipt-v1",
        "clean_build_count": 2,
        "clean_build_A_artifact_set_sha256": identity,
        "clean_build_B_artifact_set_sha256": identity,
        "frozen_regenerable_artifact_set_sha256": identity,
        "regenerable_file_count": len(build_regenerable),
        "A_equals_B": True,
        "A_equals_frozen": True,
        "real_scorer_invocations": 0,
        "results_directory_created": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "performance": None,
        "ranking": None,
        "selection": None,
        "scored": False,
    }
    (output / "DETERMINISTIC_REGENERATION_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "schema_version": VERSION + "-receipt-v1",
        "clean_build_A": receipt_a,
        "clean_build_B": receipt_b,
        "A_equals_B": True,
        "A_equals_frozen": True,
        "regenerable_artifact_set_sha256": identity,
        "file_count": len(manifest(output)),
        "real_scorer_invocations": 0,
        "output": str(output),
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
    print(json.dumps(freeze(repo=repo, output=output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
