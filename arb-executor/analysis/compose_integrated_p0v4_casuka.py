#!/usr/bin/env python3
"""Byte-compose the independently frozen P0 v1-v4 and CASUKA D1-D3 deltas.

The composition is line-preserving and fail-closed.  It permits only
disjoint base-line edits plus the two independently known same-boundary
insertions (imports and the buy/sell pre-POST guards).  No fuzzy patching,
three-way merge, or hand resolution is used.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
from pathlib import Path


LIVE = "arb-executor/live_v4.py"
RUNNING_COMMIT = "bb085ce06db5932049af85f927a7f9316ad76816"
RUNNING_BLOB = "f1857199164664037fef41b024e60f27fa373548"
P0_V3_COMMIT = "a4996dd00e82ed3534f97a09251697f1d82dbbab"
P0_V3_BLOB = "949f6995352b7be6f73be8e44af01a70a758c63e"
P0_V4_COMMIT = "765083b9bce6940d11a778a862bbd7df14967da4"
P0_V4_BLOB = "363e1c8a11525915dc053175283a6c81b72e8b0d"
CASUKA_REPAIR_COMMIT = "94be41137c0b64bfa448546c8bc3ee7c4ae32a60"
CASUKA_REPAIR_BLOB = "1809085d284b9c0cc2df4e7f24d9eac4645ee5a0"
CASUKA_ONLY_BLOB = "ebd29103ff2153f3d6ced83995c3eb8c159fe38d"


def run(repo: Path, *args: str) -> bytes:
    p = subprocess.run(
        list(args), cwd=repo, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if p.returncode:
        raise RuntimeError(
            "%s failed (%d): %s" % (
                " ".join(args), p.returncode,
                p.stderr.decode("utf-8", "replace"),
            )
        )
    return p.stdout


def blob(repo: Path, oid: str) -> bytes:
    if run(repo, "git", "cat-file", "-t", oid).strip() != b"blob":
        raise RuntimeError("%s is not a blob" % oid)
    return run(repo, "git", "cat-file", "blob", oid)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(
        ("blob %d\0" % len(data)).encode("ascii") + data
    ).hexdigest()


def identity(data: bytes) -> dict:
    return {
        "git_blob_oid": git_blob(data),
        "sha256": sha256(data),
        "byte_size": len(data),
    }


def opcodes(base: bytes, changed: bytes) -> list[dict]:
    left = base.splitlines(keepends=True)
    right = changed.splitlines(keepends=True)
    out = []
    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        out.append({
            "tag": tag,
            "base_start": i1,
            "base_end": i2,
            "old": b"".join(left[i1:i2]),
            "new": b"".join(right[j1:j2]),
        })
    return out


def overlaps(left: list[dict], right: list[dict]) -> list[dict]:
    rows = []
    for li, a in enumerate(left):
        for ri, b in enumerate(right):
            span = max(a["base_start"], b["base_start"]) < min(
                a["base_end"], b["base_end"])
            same_insert = (
                a["base_start"] == a["base_end"]
                and b["base_start"] == b["base_end"]
                and a["base_start"] == b["base_start"]
            )
            insertion_inside = (
                a["base_start"] == a["base_end"]
                and b["base_start"] <= a["base_start"] <= b["base_end"]
            ) or (
                b["base_start"] == b["base_end"]
                and a["base_start"] <= b["base_start"] <= a["base_end"]
            )
            if span or same_insert or insertion_inside:
                rows.append({
                    "left_index": li,
                    "right_index": ri,
                    "same_boundary_insertions": same_insert,
                    "left_base_span": [
                        a["base_start"], a["base_end"]],
                    "right_base_span": [
                        b["base_start"], b["base_end"]],
                    "left_new_sha256": sha256(a["new"]),
                    "right_new_sha256": sha256(b["new"]),
                    "left_new_text": a["new"].decode("utf-8"),
                    "right_new_text": b["new"].decode("utf-8"),
                })
    return rows


def _render_projection(
        base: bytes, lops: list[dict], rops: list[dict],
        include_left: bool, include_right: bool) -> bytes:
    base_lines = base.splitlines(keepends=True)
    events = []
    for order, name, ops, enabled in (
            (0, "P0", lops, include_left),
            (1, "CASUKA", rops, include_right)):
        if not enabled:
            continue
        for index, op in enumerate(ops):
            events.append((
                op["base_start"],
                0 if op["base_start"] == op["base_end"] else 1,
                order, index, name, op,
            ))
    events.sort(key=lambda row: row[:4])
    cursor = 0
    output = []
    for start, kind, _order, _index, _name, op in events:
        if kind == 0:
            if start < cursor:
                raise RuntimeError("insertion fell inside consumed base span")
            if start > cursor:
                output.extend(base_lines[cursor:start])
                cursor = start
            output.extend(op["new"].splitlines(keepends=True))
            continue
        if start < cursor:
            raise RuntimeError("overlapping replacement; merge forbidden")
        output.extend(base_lines[cursor:start])
        output.extend(op["new"].splitlines(keepends=True))
        cursor = op["base_end"]
    output.extend(base_lines[cursor:])
    return b"".join(output)


def compose(
        base: bytes, left: bytes, right: bytes
) -> tuple[bytes, dict, dict[str, bytes]]:
    """Union independent edits; left insertion precedes right at same boundary."""
    lops = opcodes(base, left)
    rops = opcodes(base, right)
    ov = overlaps(lops, rops)
    if any(not row["same_boundary_insertions"] for row in ov):
        raise RuntimeError("non-insertion patch overlap; manual merge forbidden")
    if len(ov) != 2:
        raise RuntimeError(
            "expected exactly two explained same-boundary insertions, got %d"
            % len(ov)
        )
    texts = {
        (row["left_new_text"], row["right_new_text"]) for row in ov
    }
    import_overlap = any(
        "import hashlib" in left_text and "import functools" in right_text
        for left_text, right_text in texts
    )
    post_overlap = any(
        "P0 REAL-START v4" in left_text
        and "CASUKA LIVE-SAFETY D2" in right_text
        and 'if action == "buy"' in left_text
        and 'if action == "sell"' in right_text
        for left_text, right_text in texts
    )
    if not import_overlap or not post_overlap:
        raise RuntimeError("the two overlaps are not the frozen explained pair")

    projections = {
        "both": _render_projection(base, lops, rops, True, True),
        "left_only": _render_projection(base, lops, rops, True, False),
        "right_only": _render_projection(base, lops, rops, False, True),
        "neither": _render_projection(base, lops, rops, False, False),
    }
    result = projections["both"]
    return result, {
        "left_opcode_count": len(lops),
        "right_opcode_count": len(rops),
        "overlap_count": len(ov),
        "overlaps": ov,
        "manual_merge_or_fuzzy_resolution": False,
    }, projections


def verify(repo: Path) -> tuple[bytes, dict]:
    running = blob(repo, RUNNING_BLOB)
    p0 = blob(repo, P0_V4_BLOB)
    casuka_only = blob(repo, CASUKA_ONLY_BLOB)
    p0_v3 = blob(repo, P0_V3_BLOB)
    casuka_repair = blob(repo, CASUKA_REPAIR_BLOB)

    integrated_from_running, overlap_running, running_projections = compose(
        running, p0, casuka_only)
    integrated_from_v3, overlap_v3, v3_projections = compose(
        p0_v3, p0, casuka_repair)
    if integrated_from_running != integrated_from_v3:
        raise RuntimeError("running-base and v3-base compositions differ")
    algebra = {
        "integrated_minus_casuka_equals_p0_v1_v4":
            running_projections["left_only"] == p0,
        "integrated_minus_all_p0_equals_casuka_only":
            running_projections["right_only"] == casuka_only,
        "integrated_minus_p0_v4_equals_p0_v1_v3_plus_casuka":
            v3_projections["right_only"] == casuka_repair,
        "integrated_minus_casuka_and_p0_v4_equals_p0_v1_v3":
            v3_projections["neither"] == p0_v3,
        "integrated_minus_all_authorized_deltas_equals_running":
            running_projections["neither"] == running,
    }
    if not all(algebra.values()):
        raise RuntimeError("one or more algebraic projections failed")

    receipt = {
        "schema": "integrated-p0v4-casuka-byte-composition-v1",
        "identities": {
            "running_preimage": identity(running),
            "p0_v1_v4": identity(p0),
            "casuka_only": identity(casuka_only),
            "p0_v1_v3": identity(p0_v3),
            "p0_v1_v3_plus_casuka": identity(casuka_repair),
            "integrated": identity(integrated_from_running),
        },
        "running_base_composition": overlap_running,
        "p0_v3_base_composition": overlap_v3,
        "proofs": {
            key: {
                "passed": passed,
                "result_identity": identity({
                    "integrated_minus_casuka_equals_p0_v1_v4":
                        running_projections["left_only"],
                    "integrated_minus_all_p0_equals_casuka_only":
                        running_projections["right_only"],
                    "integrated_minus_p0_v4_equals_p0_v1_v3_plus_casuka":
                        v3_projections["right_only"],
                    "integrated_minus_casuka_and_p0_v4_equals_p0_v1_v3":
                        v3_projections["neither"],
                    "integrated_minus_all_authorized_deltas_equals_running":
                        running_projections["neither"],
                }[key]),
            }
            for key, passed in algebra.items()
        },
        "residual_bytes_outside_authorized_deltas": 0,
        "manual_merge_or_fuzzy_resolution": False,
    }
    return integrated_from_running, receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    integrated, receipt = verify(repo)
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = repo / output
        if output.exists():
            current = output.read_bytes()
            if git_blob(current) not in (P0_V4_BLOB, git_blob(integrated)):
                raise SystemExit("refusing to overwrite an unexpected source")
        output.write_bytes(integrated)
    if args.receipt:
        target = Path(args.receipt)
        if not target.is_absolute():
            target = repo / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n")
    print(json.dumps(
        receipt["identities"]["integrated"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
