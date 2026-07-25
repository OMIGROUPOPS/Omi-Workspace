#!/usr/bin/env python3
"""Validate and freeze the amended additions-only Round-4 PRE-RUN V2."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_round2_data_binding as binding
import window1_round4_instrument_v2 as r4v2


PARENT = "4f65344672430adc51fe0a5a7e8c9279b2b354ed"
AUDIT = "84cdf87a12f3b0c4986ba3133c84711bce4e74c7"
AMENDMENT = "abe543e33bf40cf6cca14e046c40904d2de5e878"
OUTPUT_REL = ".claude/window1_round4_prerun_v2_20260725"
NAMED_EVENTS = {
    "KXATPCHALLENGERMATCH-26JUL19KRUCAS",
    "KXATPCHALLENGERMATCH-26JUL20CREMAT",
    "KXWTAMATCH-26JUL13TAUTOM",
    "KXWTAMATCH-26JUL14PUTJEA",
    "KXWTAMATCH-26JUL20KUDKOR",
}
CODE = [
    "arb-executor/analysis/window1_round4_instrument_v2.py",
    "arb-executor/analysis/window1_round4_prerun_builder_v2.py",
    "arb-executor/analysis/window1_round4_diagnostics_v2.py",
    "arb-executor/analysis/window1_round4_freeze_v2.py",
    "arb-executor/docs/research/window1/WINDOW1_ROUND4_CANDIDATES_V2.json",
    "arb-executor/tests/test_window1_round4_v2.py",
]
BASE_ARTIFACTS = [
    "FROZEN_CANDIDATE_EVENT_STREAMS_V2.jsonl.gz",
    "ROUND4_V1_V2_STREAM_IDENTITY_RECEIPT.json",
    "ROUND4_V2_REAL_CAPABILITY.json",
    "ROUND4_V2_CANDIDATE_ORDER_DIFFERENCES.jsonl",
    "ROUND4_V2_HEADROOM_DECISION_RECEIPTS.jsonl.gz",
    "WINDOW1_OPPORTUNITY_LEDGER_V2_01.jsonl.gz",
    "WINDOW1_OPPORTUNITY_LEDGER_V2_02.jsonl.gz",
    "WINDOW1_OPPORTUNITY_LEDGER_V2_MANIFEST.json",
    "ROUND4_V2_DIAGNOSTIC_RECEIPT.json",
    "CAUSAL_REFERENCE_CALIBRATION_V2.json",
    "ORACLE_FALSE_NEGATIVE_CENSUS_V2.json",
]


class FreezeError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def blob(repo: Path, path: Path) -> str:
    relative = str(path.relative_to(repo)).replace("\\", "/")
    return subprocess.check_output(
        [
            "git", "-C", str(repo), "hash-object", "--path", relative,
            str(path),
        ],
        text=True,
    ).strip()


def receipt(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise FreezeError(f"missing artifact: {relative}")
    return {
        "path": relative.replace("\\", "/"),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "git_blob_oid": blob(repo, path),
    }


def write_gzip(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as zipped:
            with io.TextIOWrapper(
                zipped, encoding="utf-8", newline="\n"
            ) as handle:
                for row in rows:
                    handle.write(compact(row) + "\n")


def stream_validation(output: Path) -> tuple[list[dict[str, Any]], Any]:
    receipts = []
    counts: Counter[str] = Counter()
    event_ids = set()
    changed_proof = []
    with gzip.open(
        output / "FROZEN_CANDIDATE_EVENT_STREAMS_V2.jsonl.gz",
        "rt",
        encoding="utf-8",
    ) as handle:
        for ordinal, line in enumerate(handle, start=1):
            wrapper = json.loads(line)
            stream = wrapper["stream"]
            if stream["metrics"] is not None or stream["scored"] is not False:
                raise FreezeError("performance metric found")
            candidate = str(wrapper["candidate_id"])
            event_id = str(wrapper["event_id"])
            counts[candidate] += 1
            event_ids.add(event_id)
            actions = stream["order_stream"]
            if any(
                row["action"] == "feature_censor"
                and "causal_role" in (row.get("missing_features") or [])
                for row in actions
            ):
                raise FreezeError("causal_role censor remains")
            if event_id in NAMED_EVENTS:
                proof = {
                    "candidate_id": candidate,
                    "event_id": event_id,
                    "event_terminal": stream["event_terminal"],
                    "causal_role_NO_CALL_count": sum(
                        row["action"] == "feature_no_call"
                        and row["reason"] == r4v2.CAUSAL_ROLE_NO_CALL
                        for row in actions
                    ),
                    "market_evidence_NO_CALL_count": sum(
                        row["action"] == "feature_no_call"
                        and row["reason"] == r4v2.MARKET_EVIDENCE_NO_CALL
                        for row in actions
                    ),
                    "placement_count": sum(
                        row["action"] == "place" for row in actions
                    ),
                    "D_membership_continues": True,
                    "metrics": None,
                }
                changed_proof.append(proof)
            encoded = compact(wrapper).encode("utf-8")
            receipts.append({
                "ordinal": ordinal,
                "candidate_id": candidate,
                "event_id": event_id,
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "bytes": len(encoded),
                "stream_sha256": stream["stream_sha256"],
                "metrics": None,
                "scored": False,
            })
    if len(receipts) != 1608 or len(event_ids) != 804:
        raise FreezeError("stream conservation failed")
    if set(counts.values()) != {804} or len(counts) != 2:
        raise FreezeError("per-candidate D changed")
    if len(changed_proof) != 10 or any(
        row["event_terminal"] == "censored_feature"
        or row["causal_role_NO_CALL_count"] != 2
        or row["market_evidence_NO_CALL_count"] != 2
        or row["placement_count"] != 0
        for row in changed_proof
    ):
        raise FreezeError("amended five-event proof failed")
    return receipts, changed_proof


def headroom_validation(output: Path) -> dict[str, Any]:
    total = violations = accepted = b2_max_mismatches = 0
    with gzip.open(
        output / "ROUND4_V2_HEADROOM_DECISION_RECEIPTS.jsonl.gz",
        "rt",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            row = json.loads(line)
            total += 1
            if row["action"] != "headroom_decision":
                continue
            b1, b2, fee = (
                row.get("b1_cents"),
                row.get("b2_cents"),
                row.get("fee_cents"),
            )
            if b1 is not None and fee is not None:
                expected_max = math.floor(
                    -float(b1) - float(fee) - 1.0
                )
                if (
                    row.get("b2_max_cents") is not None
                    and int(row["b2_max_cents"]) != expected_max
                ):
                    b2_max_mismatches += 1
            if (
                row.get("action_taken") is not True
                or b1 is None or b2 is None or fee is None
            ):
                continue
            actual = float(b1) + float(b2) + float(fee) < 0
            violations += int(
                not actual
                or row.get("strict_combined_guard") is not True
                or (
                    row.get("b2_max_cents") is not None
                    and float(b2) > float(row["b2_max_cents"])
                )
            )
            accepted += 1
    if violations or b2_max_mismatches:
        raise FreezeError("headroom arithmetic changed")
    return {
        "receipt_count": total,
        "accepted_action_count": accepted,
        "arithmetic_violation_count": 0,
        "b2_max_mismatch_count": 0,
        "strict_law": "b1+b2+fee<0",
        "metrics": None,
    }


def audit_blob(repo: Path, commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", f"{commit}:{path}"],
        text=True,
    ).strip()


def build(repo: Path, output: Path) -> None:
    if subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip() != PARENT:
        raise FreezeError("wrong exact parent")
    spec = r4v2.load_candidate_spec(repo)
    capability = read_json(output / "ROUND4_V2_REAL_CAPABILITY.json")
    identity = read_json(
        output / "ROUND4_V1_V2_STREAM_IDENTITY_RECEIPT.json"
    )
    diagnostic = read_json(output / "ROUND4_V2_DIAGNOSTIC_RECEIPT.json")
    if (
        capability["D"] != 804
        or capability["candidate_event_stream_count"] != 1608
        or identity["byte_identical_to_V1_count"] != 1598
        or identity["changed_from_V1_count"] != 10
        or diagnostic["all_stream_metrics_null"] is not True
    ):
        raise FreezeError("V2 frozen population invariant failed")
    if any(
        row["eligible_event_count"] != 804
        or row["censored_event_count"] != 0
        for row in capability["candidate_summaries"]
    ):
        raise FreezeError("actionable D=804 failed")

    streams, changed_proof = stream_validation(output)
    write_gzip(output / "ROUND4_V2_STREAM_RECEIPTS.jsonl.gz", streams)
    headroom = headroom_validation(output)
    write_json(
        output / "ROUND4_V2_HEADROOM_INVARIANT_RECEIPT.json", headroom
    )
    write_json(output / "ROUND4_V2_FIVE_EVENT_PROOF.json", {
        "schema_version": "window1-round4-v2-five-event-proof-v1",
        "rows": changed_proof,
        "row_count": 10,
        "all_non_censored": True,
        "all_zero_placement": True,
        "all_D_membership_continues": True,
        "metrics": None,
    })
    write_json(output / "ROUND4_V1_SUPERSESSION_RECEIPT.json", {
        "schema_version": "window1-round4-v1-supersession-v2",
        "V1_prerun_retracted_from_execution": PARENT,
        "historical_V1_files_preserved": True,
        "reasons": [
            "causal_role was an unlawful terminal event censor",
            "two inert 100-cent fields were ambiguous stale surface",
        ],
        "V2_execution_binding_required": True,
        "candidate_ids_changed": False,
        "fill_or_headroom_law_changed": False,
        "benchmark_execution_authorized": False,
    })

    v1_source = read_json(
        repo
        / ".claude/window1_round4_prerun_20260725/"
        "ROUND4_SOURCE_BINDING_AVAILABILITY.json"
    )
    source = {
        **v1_source,
        "schema_version": "window1-round4-source-availability-v2",
        "V1_source_receipts_inherited_byte_identically": True,
        "causal_role_absence": r4v2.CAUSAL_ROLE_NO_CALL,
        "market_evidence_absence": r4v2.MARKET_EVIDENCE_NO_CALL,
        "print_as_BBO_substitution": False,
        "fabricated_price_allowed": False,
        "holdout_opened": False,
    }
    write_json(
        output / "ROUND4_V2_SOURCE_BINDING_AVAILABILITY.json", source
    )

    code_receipts = [
        receipt(repo, path, "V2 code/spec/test") for path in CODE
    ]
    generated = [
        *BASE_ARTIFACTS,
        "ROUND4_V2_STREAM_RECEIPTS.jsonl.gz",
        "ROUND4_V2_HEADROOM_INVARIANT_RECEIPT.json",
        "ROUND4_V2_FIVE_EVENT_PROOF.json",
        "ROUND4_V1_SUPERSESSION_RECEIPT.json",
        "ROUND4_V2_SOURCE_BINDING_AVAILABILITY.json",
    ]
    artifact_receipts = [
        receipt(repo, f"{OUTPUT_REL}/{name}", "V2 PRE-RUN artifact")
        for name in generated
    ]
    execution = {
        "schema_version": "window1-round4-v2-execution-inventory-v1",
        "bind_V2_only": True,
        "candidate_ids_in_frozen_order": spec["candidate_ids"],
        "D": 804,
        "target_PC": 603,
        "candidate_event_stream_count": 1608,
        "required_V2_inputs": [
            row for row in [*code_receipts, *artifact_receipts]
            if (
                "CANDIDATES_V2" in row["path"]
                or "instrument_v2" in row["path"]
                or "FROZEN_CANDIDATE_EVENT_STREAMS_V2" in row["path"]
                or "SOURCE_BINDING" in row["path"]
                or "STREAM_RECEIPTS" in row["path"]
            )
        ],
        "frozen_source_receipts": v1_source["git_source_receipts"],
        "execution_id": None,
        "execution_command": None,
        "benchmark_execution_authorized": False,
        "scorer_invocation_count": 0,
    }
    write_json(
        output / "ROUND4_V2_EXECUTION_PACKAGE_INVENTORY.json", execution
    )
    generated.append("ROUND4_V2_EXECUTION_PACKAGE_INVENTORY.json")

    amendment_path = (
        ".claude/audit_20260725_round4_prerun/ITEM5_AMENDMENT.md"
    )
    manifest = {
        "schema_version": "window1-round4-prerun-freeze-v2",
        "exact_parent": PARENT,
        "original_audit": AUDIT,
        "controlling_item5_amendment": AMENDMENT,
        "controlling_item5_amendment_blob_oid": audit_blob(
            repo, AMENDMENT, amendment_path
        ),
        "D": 804,
        "candidate_count": 2,
        "candidate_event_stream_count": 1608,
        "leg_identity_count": 1608,
        "development_dates": list(binding.DEV_DATES),
        "sealed_holdout_dates": [
            "2026-07-24", "2026-07-25", "2026-07-26"
        ],
        "candidate_ids": spec["candidate_ids"],
        "actionable_event_count_by_candidate": {
            row["candidate_id"]: row["eligible_event_count"]
            for row in capability["candidate_summaries"]
        },
        "candidate_distinctness_event_count": capability[
            "candidate_summaries"
        ][0]["events_distinct_from_other_candidate"],
        "byte_identical_to_V1_stream_count": 1598,
        "changed_from_V1_stream_count": 10,
        "five_event_proof": changed_proof,
        "retired_100_fields_present": False,
        "primary_fill_law_changed": False,
        "headroom_law_changed": False,
        "headroom_validation": headroom,
        "all_metrics_null": True,
        "C_PC_S_IC_populated": False,
        "code_receipts": code_receipts,
        "artifact_receipts": artifact_receipts,
        "benchmark_execution_authorized": False,
        "scorer_invocation_count": 0,
        "ranking_tuning_or_ablation": False,
        "holdout_opened": False,
        "live_or_production_access": False,
    }
    write_json(output / "ROUND4_V2_PRE_RUN_MANIFEST.json", manifest)
    generated.append("ROUND4_V2_PRE_RUN_MANIFEST.json")

    report = f"""# Window-1 Round-4 PRE-RUN V2

This additions-only V2 supersedes `{PARENT}` for future execution binding and
implements only Item 5 amendment `{AMENDMENT}` plus the original audit's stale
100-field removal.

- D=804 and actionable=804 for both unchanged candidate IDs.
- 1,598 candidate-event streams are byte-identical to V1.
- Exactly ten streams change: five named events times two candidates.
- Every changed stream has two causal-role NO_CALLs, two market-evidence
  NO_CALLs, zero placements, a non-censored event terminal, and continued D
  membership.
- No price is fabricated and no executed print substitutes for BBO authority.
- Candidate order-distinctness remains {capability['candidate_summaries'][0]['events_distinct_from_other_candidate']} real events.
- Both inert 100-cent fields are absent; S and IC remain diagnostics only.
- Primary cumulative print-volume fills and strict `b1+b2+fee<0` headroom are
  unchanged; the receipt scan has zero arithmetic violations.
- All C/PC/S/IC fields remain null. No scorer, benchmark, tuning, ranking,
  holdout, live, or production action occurred.

The V2 execution inventory contains no execution ID or command and authorizes
no benchmark.
"""
    (output / "ROUND4_V2_PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    generated.append("ROUND4_V2_PRE_RUN_REPORT.md")

    final_receipts = [
        receipt(repo, f"{OUTPUT_REL}/{name}", "V2 PRE-RUN artifact")
        for name in generated
    ]
    write_json(output / "ROUND4_V2_ARTIFACT_MANIFEST.json", {
        "schema_version": "window1-round4-v2-artifact-manifest-v1",
        "exact_parent": PARENT,
        "controlling_amendment": AMENDMENT,
        "artifacts": final_receipts,
        "code": code_receipts,
        "frozen_source_receipts": v1_source["git_source_receipts"],
        "all_metrics_null": True,
        "scorer_invocations": 0,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    build(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
