#!/usr/bin/env python3
"""Freeze two newline-portable builds of scoring package V2."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from window1_range_attack_scoring_package_builder_v2 import (
    IMPLEMENTATION_PARENT,
    PACKAGE_REL,
    build,
    canonical_text_bytes,
    git_blob_oid,
)

TEXT_SUFFIXES = {
    ".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml",
}

class FreezeError(RuntimeError):
    """Raised when deterministic package freezing fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.iterdir())
        if path.is_file()
    ]


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        (
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
            + "\n"
        ).encode("utf-8")
    )


def freeze(repo: Path) -> dict[str, Any]:
    target = repo / PACKAGE_REL
    if target.exists():
        raise FreezeError("V2 package target already exists")
    with tempfile.TemporaryDirectory(prefix="w1-range-score-v2-") as tmp:
        temp = Path(tmp)
        lf = temp / "lf"
        crlf = temp / "crlf"
        build(repo, lf, newline_probe="lf")
        build(repo, crlf, newline_probe="crlf")
        left = inventory(lf)
        right = inventory(crlf)
        if left != right:
            raise FreezeError("LF and CRLF clean builds differ")
        shutil.copytree(lf, target)
    portability = {
        "schema_version":
            "window1-range-attack-newline-portability-receipt-v2",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "clean_builds": 2,
        "checkout_forms": ["LF", "CRLF"],
        "canonical_text_identity": "LF",
        "binary_identity": "exact bytes",
        "artifact_inventories_byte_identical": True,
        "artifact_count_before_freeze_receipts": len(left),
        "artifact_inventory": left,
        "metrics": None,
        "scored": False,
    }
    write_json(target / "NEWLINE_PORTABILITY_RECEIPT.json", portability)
    regeneration = {
        "schema_version":
            "window1-range-attack-deterministic-package-regeneration-v2",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "builds_compared": 2,
        "fresh_output_directories": True,
        "LF_CRLF_byte_identical": True,
        "real_population_scorer_invocations": 0,
        "results_directories_created": 0,
        "performance_metrics": {
            "C": None, "PC": None, "S": None, "IC": None
        },
        "gate_pass": True,
    }
    write_json(
        target / "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json",
        regeneration,
    )
    artifacts = []
    for path in sorted(target.iterdir()):
        if not path.is_file() or path.name == "PACKAGE_ARTIFACT_MANIFEST.json":
            continue
        raw = path.read_bytes()
        is_text = path.suffix.lower() in TEXT_SUFFIXES
        identity = canonical_text_bytes(raw) if is_text else raw
        artifacts.append({
            "path": f"{PACKAGE_REL}/{path.name}",
            "identity_bytes": len(identity),
            "sha256": hashlib.sha256(identity).hexdigest(),
            "git_blob_oid": git_blob_oid(identity),
            "hash_basis": "canonical_lf_text" if is_text else "exact_binary",
        })
    manifest = {
        "schema_version": "window1-range-attack-package-artifacts-v2",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "metrics": None,
        "scored": False,
    }
    write_json(target / "PACKAGE_ARTIFACT_MANIFEST.json", manifest)
    return {
        "target": str(target),
        "artifact_count": len(artifacts) + 1,
        "LF_CRLF_byte_identical": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args.repo.resolve())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
