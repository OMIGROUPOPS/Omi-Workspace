#!/usr/bin/env python3
"""Two-build deterministic freezer for the T2 scoring PRE-RUN."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from window1_t2_scoring_package_builder_v1 import build


VERSION = "window1-t2-scoring-package-freeze-v1"


class FreezeError(RuntimeError):
    """The two clean score-free builds did not reproduce exactly."""


def manifest(
    root: Path,
    *,
    exclude_determinism_receipt: bool = False,
) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not (
            exclude_determinism_receipt
            and path.name == "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json"
        )
    }


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def freeze(
    *,
    repo: Path,
    output: Path,
    workers: int,
) -> dict[str, object]:
    if output.exists():
        raise FreezeError("frozen output already exists")
    with tempfile.TemporaryDirectory(prefix="w1-t2-scorepkg-a-") as a_text, \
            tempfile.TemporaryDirectory(prefix="w1-t2-scorepkg-b-") as b_text:
        a = Path(a_text) / "package"
        b = Path(b_text) / "package"
        receipt_a = build(repo=repo, output=a, workers=workers)
        receipt_b = build(repo=repo, output=b, workers=workers)
        hashes_a = manifest(a)
        hashes_b = manifest(b)
        if hashes_a != hashes_b:
            changed = sorted(set(hashes_a) | set(hashes_b))
            mismatches = [
                path for path in changed
                if hashes_a.get(path) != hashes_b.get(path)
            ]
            raise FreezeError(
                "clean builds differ: " + ",".join(mismatches[:20])
            )
        shutil.copytree(a, output)
    frozen_regenerable = manifest(
        output, exclude_determinism_receipt=True
    )
    build_regenerable = {
        path: digest for path, digest in hashes_a.items()
        if path != "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json"
    }
    if frozen_regenerable != build_regenerable:
        raise FreezeError("frozen package differs from clean builds")
    artifact_set_sha256 = canonical_sha256(build_regenerable)
    determinism_receipt = {
        "schema_version": VERSION + "-receipt-v1",
        "clean_build_count": 2,
        "clean_build_A_artifact_set_sha256": artifact_set_sha256,
        "clean_build_B_artifact_set_sha256": artifact_set_sha256,
        "frozen_regenerable_artifact_set_sha256": artifact_set_sha256,
        "regenerable_file_count": len(build_regenerable),
        "A_equals_B": True,
        "A_equals_frozen": True,
        "canonical_json": "UTF-8 LF sorted keys indent=2 trailing LF",
        "deterministic_gzip": "filename empty; mtime=0; canonical JSONL",
        "real_scorer_invocations": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    (output / "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json").write_text(
        json.dumps(determinism_receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    frozen = manifest(output)
    return {
        "schema_version": VERSION + "-receipt-v1",
        "clean_build_A": receipt_a,
        "clean_build_B": receipt_b,
        "file_count": len(frozen),
        "regenerable_artifact_set_sha256": artifact_set_sha256,
        "A_equals_B": True,
        "A_equals_frozen": True,
        "real_scorer_invocations": 0,
        "output": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (repo / args.output_dir).resolve()
    )
    print(json.dumps(
        freeze(repo=repo, output=output, workers=args.workers),
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
