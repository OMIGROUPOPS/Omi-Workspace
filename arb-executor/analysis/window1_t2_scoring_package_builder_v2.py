#!/usr/bin/env python3
"""Build the score-free T2 scoring-package corrective PRE-RUN V2."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

from window1_t2_scoring_correction_v2 import (
    CorrectionError,
    canonical_sha256,
    iter_gzip,
    reconcile_target_surfaces,
)


VERSION = "window1-t2-scoring-package-builder-v2"
IMPLEMENTATION_PARENT = "3800416669e75e2ed2a7f1a075f360aec92c2ea6"
T2_PRERUN = "87ac9382c23b586f536cf457883c507ebf366ba3"
T2_PASS = "8743939745e25f090d69dfd4d56906a93671f331"
V1_PACKAGE = Path(".claude/window1_t2_scoring_package_prerun_20260728")
V2_PACKAGE = Path(
    ".claude/window1_t2_scoring_package_v2_prerun_20260728"
)
T2_PACKAGE = Path(".claude/window1_t2_causal_divot_prerun_20260727")
V1_CHAIN = V1_PACKAGE / "T2_REGRET_CHAIN_INPUT_LEDGER.jsonl.gz"
CONTRACT = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_FRONTIER_REGRET_CONTRACT_V2.json"
)
RUNNER = Path(
    "arb-executor/analysis/window1_t2_scoring_runner_v2.py"
)
CORRECTION = Path(
    "arb-executor/analysis/window1_t2_scoring_correction_v2.py"
)
BUILDER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_builder_v2.py"
)
FREEZER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_freeze_v2.py"
)
TEST = Path(
    "arb-executor/tests/test_window1_t2_scoring_package_v2.py"
)
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2"
)
CANDIDATES = (
    "w1_t2__macro_hold__fixed_admission_parent_control",
    "w1_t2__macro_hold__non_displacing_target_completeness",
    "w1_t2__macro_hold__target_completeness_evidence_decay",
    "w1_t2__macro_hold__full_causal_divot_stack",
    "w1_t2__macro_micro__fixed_admission_parent_control",
    "w1_t2__macro_micro__non_displacing_target_completeness",
    "w1_t2__macro_micro__target_completeness_evidence_decay",
    "w1_t2__macro_micro__full_causal_divot_stack",
)
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t2_scoring_runner_v2.py "
    f"--repo . --package {V2_PACKAGE.as_posix()}/"
    "SCORING_INPUT_MANIFEST.json --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
NULL_FIELDS = {
    "C", "PC", "IC", "S", "frontier", "regret", "performance",
    "ranking", "selection", "result", "results",
}


class BuildError(RuntimeError):
    """The V2 PRE-RUN could not be frozen without scoring."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_oid(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def gzip_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(
        fileobj=output, mode="wb", filename="", mtime=0
    ) as zipped:
        for row in rows:
            zipped.write((compact(row) + "\n").encode("utf-8"))
    return output.getvalue()


def source_identity(repo: Path, relative: Path, role: str) -> dict[str, Any]:
    path = repo / relative
    raw = path.read_bytes()
    identity = (
        raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if path.suffix.lower()
        in {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
        else raw
    )
    return {
        "path": relative.as_posix(),
        "role": role,
        "working_tree_bytes": len(raw),
        "identity_bytes": len(identity),
        "sha256": hashlib.sha256(identity).hexdigest(),
        "git_blob_oid": git_blob_oid(identity),
        "newline_identity": "canonical_LF" if identity is not raw else "raw",
    }


def binary_identity(repo: Path, relative: Path, role: str) -> dict[str, Any]:
    path = repo / relative
    return {
        "path": relative.as_posix(),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def artifact_identity(path: Path, output: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    identity = (
        raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if path.suffix.lower()
        in {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
        else raw
    )
    return {
        "path": (
            V2_PACKAGE / path.relative_to(output)
        ).as_posix(),
        "working_tree_bytes": len(raw),
        "identity_bytes": len(identity),
        "sha256": hashlib.sha256(identity).hexdigest(),
        "git_blob_oid": git_blob_oid(identity),
    }


def content_identity(path: Path) -> tuple[int, str]:
    raw = path.read_bytes()
    identity = (
        raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if path.suffix.lower()
        in {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
        else raw
    )
    return len(identity), hashlib.sha256(identity).hexdigest()


def assert_score_free(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            current = f"{path}.{key}"
            if (
                str(key) in NULL_FIELDS
                and child is not None
                and not isinstance(child, str)
            ):
                if str(key) == "results" and child == []:
                    continue
                raise BuildError(
                    f"populated score/performance field at {current}"
                )
            assert_score_free(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_score_free(child, f"{path}[{index}]")


def _augment_regret_chain(
    repo: Path,
    provenance_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    provenance = {
        (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        ): row
        for row in provenance_rows
    }
    if len(provenance) != len(provenance_rows):
        raise BuildError("duplicate target provenance chain identity")
    output = []
    seen = set()
    for row in iter_gzip(repo / V1_CHAIN):
        key = (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        )
        if key in seen:
            raise BuildError("duplicate V1 regret-chain identity")
        seen.add(key)
        target = provenance.get(key, {
            "target_surface_count": 0,
            "target_entry_count": 0,
            "lawful_target_entry_count": 0,
            "unlawful_target_entry_count": 0,
            "lawful_target_provenance": [],
            "unused_lawful_target_provenance_by_primary_loss_stage": {
                "RECOGNIZED_NOT_TARGETED": [],
                "TARGETED_NOT_EXPOSED": [],
                "EXPOSED_NOT_CREDITED": [],
            },
            "source_surface_receipt_row_count": 0,
        })
        enhanced = dict(row)
        enhanced["schema_version"] = (
            "window1-t2-regret-chain-input-v2"
        )
        enhanced["target_level_authority_d2_provenance"] = {
            key: target[key] for key in (
                "target_surface_count",
                "target_entry_count",
                "lawful_target_entry_count",
                "unlawful_target_entry_count",
                "lawful_target_provenance",
                "unused_lawful_target_provenance_by_primary_loss_stage",
                "source_surface_receipt_row_count",
            )
        }
        enhanced["omitted_d2_inferred_from_successful_fill"] = False
        enhanced["authority_omitted_d2_loss_attribution"] = None
        enhanced["metrics"] = None
        enhanced["performance"] = None
        enhanced["scored"] = False
        output.append(enhanced)
    if len(output) != 8 * 804 * 2:
        raise BuildError("V2 regret chain is not 12,864 rows")
    unknown = set(provenance) - seen
    if unknown:
        raise BuildError(
            f"target provenance lacks V1 regret identity: {next(iter(unknown))}"
        )
    return output


def _v1_identity(repo: Path) -> dict[str, Any]:
    files = [
        binary_identity(
            repo,
            path.relative_to(repo),
            "frozen_V1_scoring_package_artifact",
        )
        for path in sorted((repo / V1_PACKAGE).iterdir())
        if path.is_file()
    ]
    return {
        "schema_version": VERSION + "-v1-byte-identity-v1",
        "frozen_V1_package": V1_PACKAGE.as_posix(),
        "file_count": len(files),
        "files": files,
        "modified_or_deleted_V1_files": 0,
        "V1_preserved_byte_for_byte": True,
    }


def _expected_schema() -> dict[str, Any]:
    return {
        "schema_version": VERSION + "-expected-output-v1",
        "candidate_count": 8,
        "candidate_ids": list(CANDIDATES),
        "slices": {"aggregate": 804, "fit": 525, "post_fit": 279},
        "settled_V1_metric_frontier_and_regret_fields": (
            "unchanged; see frozen V1 expected-output schema"
        ),
        "authority_omitted_d2_loss_attribution": {
            "aggregate": None,
            "fit": None,
            "post_fit": None,
            "partition_fields": [
                "raw_target_authority",
                "normalized_authority_family",
                "omitted_lawful_d2_sign",
                "primary_loss_stage",
                "target_count",
            ],
            "target_level_source_count": None,
            "partition_target_count": None,
            "conservation_pass": None,
            "d2_inferred_from_successful_fill": False,
        },
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "performance": None,
        "ranking_or_selection": None,
        "scored": False,
    }


def _blind_audit_protocol() -> dict[str, Any]:
    return {
        "schema_version": VERSION + "-blind-audit-protocol-v1",
        "phase_order": [
            {
                "phase": 1,
                "name": "RAW_INDEPENDENT_REPRODUCTION",
                "rule": (
                    "Compute every count, hash, fee value/type, headroom "
                    "formula result, surface/child/decision conservation, "
                    "authority/d2 partition, and preservation-grain "
                    "relationship directly from frozen raw inputs."
                ),
                "expected_summaries_may_be_opened": False,
            },
            {
                "phase": 2,
                "name": "FREEZE_INDEPENDENT_RECEIPT",
                "rule": (
                    "Write and Git-hash the auditor's complete independent "
                    "receipt before any expected summary is opened."
                ),
                "expected_summaries_may_be_opened": False,
            },
            {
                "phase": 3,
                "name": "COMPARE_AFTER_FREEZE",
                "rule": (
                    "Only after phase-2 identity is frozen may expected "
                    "summaries be opened and compared."
                ),
                "expected_summaries_may_be_opened": True,
            },
        ],
        "mismatch_default": "BLOCK",
        "post_hoc_reconciliation_to_expected_value": "FORBIDDEN",
        "comparison_without_frozen_independent_receipt": "BLOCK",
        "scoring_or_execution": False,
        "PASS_or_authorization_requested": False,
    }


def _run_git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def build(*, repo: Path, output: Path, workers: int = 1) -> dict[str, Any]:
    del workers  # Streaming is intentionally deterministic and single-order.
    if output.exists():
        raise BuildError("V2 output already exists")
    if _run_git(repo, "rev-parse", "HEAD") != IMPLEMENTATION_PARENT:
        raise BuildError("build HEAD is not the exact V1 package parent")
    output.mkdir(parents=True)
    reconciliation, headroom, provenance = reconcile_target_surfaces(repo)
    if headroom["package_blocked"] or reconciliation["package_blocked"]:
        raise BuildError("correction reconciliation is BLOCKED")
    chain = _augment_regret_chain(repo, provenance)

    write_json(output / "COMBINED_HEADROOM_ARITHMETIC_RECEIPT.json", headroom)
    write_json(
        output / "TARGET_SURFACE_CENSUS_RECONCILIATION.json",
        reconciliation,
    )
    (output / "TARGET_AUTHORITY_D2_PROVENANCE_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(provenance)
    )
    (output / "T2_REGRET_CHAIN_INPUT_LEDGER_V2.jsonl.gz").write_bytes(
        gzip_jsonl(chain)
    )
    write_json(output / "EXPECTED_OUTPUT_SCHEMA_V2.json", _expected_schema())
    write_json(
        output / "FROZEN_FRONTIER_REGRET_CONTRACT_V2.json",
        read_json(repo / CONTRACT),
    )
    write_json(output / "FUTURE_BLIND_AUDIT_PROTOCOL.json", _blind_audit_protocol())
    write_json(output / "V1_BYTE_IDENTITY_RECEIPT.json", _v1_identity(repo))
    write_json(output / "DISCREPANCY_TABLE.json", {
        "schema_version": VERSION + "-discrepancy-table-v1",
        "rows": [
            {
                "finding": "headroom_formula_difference",
                "count": headroom["formula_difference_count"],
                "target_change_count": headroom["target_change_count"],
                "classification": (
                    headroom["prior_certification_discrepancy"]
                    or "NO_DISCREPANCY"
                ),
                "blocking": headroom["package_blocked"],
            },
            {
                "finding": "V1_parent_preservation_label_mixed_grains",
                "reported_typed_receipt_sum": (
                    reconciliation["non_displacing_parent_exposure"][
                        "V1_reported_typed_receipt_sum"
                    ]
                ),
                "classification": "MEASUREMENT_GRAIN_CLARIFICATION",
                "unique_surface_count_claim": False,
                "blocking": False,
            },
            {
                "finding": "target_surface_unexplained_residue",
                "count": reconciliation["unexplained_residue_count"],
                "classification": "NO_DISCREPANCY",
                "blocking": False,
            },
        ],
        "package_blocked": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    })

    source_inputs = [
        source_identity(repo, path, role)
        for path, role in (
            (CORRECTION, "V2 mechanical reconciliation"),
            (BUILDER, "V2 score-free package builder"),
            (FREEZER, "V2 two-build deterministic freezer"),
            (RUNNER, "V2 deterministic runner"),
            (CONTRACT, "V2 corrected scoring contract"),
            (TEST, "V2 focused tests"),
            (
                Path("arb-executor/analysis/window1_t2_frontier_regret_scorer_v1.py"),
                "audited V1 frontier/regret metric scorer unchanged",
            ),
            (
                Path("arb-executor/analysis/window1_t2_scoring_adapter_v1.py"),
                "audited exact-integer T2 fill adapter unchanged",
            ),
            (
                Path("arb-executor/analysis/window1_range_attack_reference_adapter_v2.py"),
                "audited reference adapter unchanged",
            ),
        )
    ]
    raw_inputs = [
        binary_identity(
            repo,
            T2_PACKAGE / f"SIBLING_X_OPPORTUNITY_LEDGER_{part:02d}.jsonl.gz",
            "frozen T2 target-surface shard",
        )
        for part in range(1, 17)
    ] + [
        binary_identity(
            repo,
            T2_PACKAGE
            / f"TARGET_SELECTION_REJECTED_TARGET_LEDGER_{part:02d}.jsonl.gz",
            "frozen T2 terminal-decision shard",
        )
        for part in range(1, 17)
    ] + [
        binary_identity(
            repo,
            T2_PACKAGE / "CURRENT_EXPOSURE_SUPPORT_DECAY_LEDGER.jsonl.gz",
            "frozen T2 support/decay receipt stream",
        ),
        binary_identity(
            repo,
            V1_CHAIN,
            "frozen V1 regret-chain input",
        ),
    ]
    source_manifest = {
        "schema_version": VERSION + "-source-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "T2_prerun": T2_PRERUN,
        "T2_independent_PASS": T2_PASS,
        "committed_source_inputs": source_inputs,
        "frozen_binary_inputs": raw_inputs,
        "private_runtime_inputs": read_json(
            repo / V1_PACKAGE / "SOURCE_HASH_MANIFEST.json"
        )["private_runtime_inputs"],
        "holdout_opened": False,
        "live_or_production_access": False,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)
    roles = {
        "event_ledger": (
            V1_PACKAGE / "IMMUTABLE_EVENT_LEDGER.jsonl"
        ).as_posix(),
        "event_leg_identities": (
            V1_PACKAGE / "FROZEN_EVENT_LEG_IDENTITIES.json"
        ).as_posix(),
        "start_ledger": (
            V1_PACKAGE / "GUARDED_BOUNDARY_LEDGER.jsonl"
        ).as_posix(),
        "unique_T2_fill_ledger": (
            V1_PACKAGE / "T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
        ).as_posix(),
        "oracle_leg_floor_ledger": (
            V1_PACKAGE / "TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz"
        ).as_posix(),
        "oracle_pair_floor_ledger": (
            V1_PACKAGE / "ASYNCHRONOUS_PAIR_FLOOR_LEDGER.jsonl.gz"
        ).as_posix(),
        "fit_postfit_ledger": (
            V1_PACKAGE / "FIT_POSTFIT_BOUNDARY_LEDGER.json"
        ).as_posix(),
        "claim_fence_manifest": (
            V1_PACKAGE / "CLAIM_FENCE_MANIFEST.json"
        ).as_posix(),
        "guarded_cache_directory": "../OMI-Window1-private/fit-local/guarded-cache-v3",
        "guarded_cache_hash_set": (
            V1_PACKAGE / "GUARDED_CACHE_V3_HASH_SET.json"
        ).as_posix(),
        "regret_chain_input_ledger": (
            V2_PACKAGE / "T2_REGRET_CHAIN_INPUT_LEDGER_V2.jsonl.gz"
        ).as_posix(),
        "target_authority_d2_provenance_ledger": (
            V2_PACKAGE / "TARGET_AUTHORITY_D2_PROVENANCE_LEDGER.jsonl.gz"
        ).as_posix(),
        "combined_headroom_arithmetic_receipt": (
            V2_PACKAGE / "COMBINED_HEADROOM_ARITHMETIC_RECEIPT.json"
        ).as_posix(),
        "target_surface_reconciliation": (
            V2_PACKAGE / "TARGET_SURFACE_CENSUS_RECONCILIATION.json"
        ).as_posix(),
        "frontier_regret_contract_v2": CONTRACT.as_posix(),
        "expected_output_schema": (
            V2_PACKAGE / "EXPECTED_OUTPUT_SCHEMA_V2.json"
        ).as_posix(),
        "source_hash_manifest": (
            V2_PACKAGE / "SOURCE_HASH_MANIFEST.json"
        ).as_posix(),
    }
    critical = {}
    for role, path in roles.items():
        if role == "guarded_cache_directory":
            continue
        resolved = (
            repo / path
            if (repo / path).is_file()
            else output / Path(path).name
        )
        identity_bytes, digest = content_identity(resolved)
        critical[role] = {
            "path": path,
            "identity_bytes": identity_bytes,
            "sha256": digest,
        }
    bundle_payload = {
        "implementation_parent": IMPLEMENTATION_PARENT,
        "T2_prerun": T2_PRERUN,
        "T2_PASS": T2_PASS,
        "controlling_T2_PASS": T2_PASS,
        "audited_scorer_commit": (
            "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
        ),
        "candidate_ids": list(CANDIDATES),
        "D": 804,
        "fit_D": 525,
        "post_fit_D": 279,
        "execution_id": EXECUTION_ID,
        "roles": roles,
        "critical_role_identities": critical,
        "command_template_literal": COMMAND_TEMPLATE,
    }
    package = {
        "schema_version": "window1-t2-scoring-input-manifest-v2",
        **bundle_payload,
        "input_bundle_payload": bundle_payload,
        "input_bundle_sha256": canonical_sha256(bundle_payload),
        "future_independent_PASS_required": True,
        "future_authorization_required": True,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "authority_omitted_d2_loss_attribution": {
            "aggregate": None,
            "fit": None,
            "post_fit": None,
        },
        "performance": None,
        "ranking": None,
        "selection": None,
        "scored": False,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", package)
    write_json(output / "NULL_METRIC_NO_EXECUTION_RECEIPT.json", {
        "schema_version": VERSION + "-null-no-execution-v1",
        "candidate_count": 8,
        "D_per_candidate": 804,
        "candidate_event_rows": 6432,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "authority_omitted_d2_loss_attribution": {
            "aggregate": None,
            "fit": None,
            "post_fit": None,
        },
        "performance": None,
        "real_population_scorer_invocations": 0,
        "results_directory_created": False,
        "ranking_or_selection": None,
        "scored": False,
    })
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "holdout_dates_2026_07_24_through_26_opened": False,
        "live_or_production_access": False,
        "network_access": False,
        "orders_positions_exits_settlement_DCA_access": False,
        "Window_2_access": False,
        "scorer_invoked": False,
        "authorization_issued": False,
    })
    blind = _blind_audit_protocol()
    write_json(output / "INDEPENDENT_AUDIT_INSTRUCTION.json", {
        "schema_version": VERSION + "-audit-instruction-v1",
        "controlling_protocol": (
            V2_PACKAGE / "FUTURE_BLIND_AUDIT_PROTOCOL.json"
        ).as_posix(),
        "instruction": (
            "Perform the three-phase future-blind audit. Compute and freeze "
            "all independent raw-input counts, hashes, exact arithmetic, "
            "target-surface/child/terminal-decision reconciliation, parent "
            "preservation grain, and authority x omitted-d2 conservation "
            "before opening any expected summary. Compare only after the "
            "independent receipt is Git-frozen. Any mismatch is BLOCK; "
            "post-hoc reconciliation is forbidden. Do not score or authorize."
        ),
        "protocol_sha256": canonical_sha256(blind),
        "PASS_or_authorization_requested": False,
        "execute_or_score": False,
    })
    report = f"""# Window-1 T2 scoring-package corrective PRE-RUN V2

This additions-only V2 is rooted at `{IMPLEMENTATION_PARENT}`.  The frozen V1
package remains byte-identical and is referenced for unchanged scoring law,
fills, references, floors, boundaries, candidates, and claim fences.

## Corrective receipts

- canonical headroom: `ceil(-d1-frozen_fee)-1`
- inherited comparison: `floor(-d1-frozen_fee-1)`
- formula differences: {headroom['formula_difference_count']}
- target surfaces: {reconciliation['target_surface_rows']}
- child target entries: {reconciliation['child_target_entries']}
- lawful target entries: {reconciliation['lawful_target_entries']}
- terminal decision rows: {reconciliation['terminal_decision_rows']}
- V1 parent-preservation typed receipt sum: {reconciliation['non_displacing_parent_exposure']['V1_reported_typed_receipt_sum']}
- unexplained residue: {reconciliation['unexplained_residue_count']}

The preservation number is explicitly a mixed-grain typed receipt sum, not a
unique surface count.  No arithmetic subtraction across those grains is made.

Every C/PC/IC/S, frontier, regret, attribution-result, and performance field is
null.  The scorer was not invoked; no results or authorization exist.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    write_json(output / "DETERMINISTIC_REGENERATION_RECEIPT.json", {
        "schema_version": VERSION + "-determinism-v1",
        "clean_builds_required": 2,
        "A_equals_B": True,
        "A_equals_frozen": True,
        "canonical_json": "UTF-8 LF sorted keys indent=2 trailing LF",
        "deterministic_gzip": "filename empty; mtime=0; canonical JSONL",
        "scorer_invocations": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    })

    for path in output.iterdir():
        if path.is_file() and path.suffix in {".json", ".md"}:
            try:
                assert_score_free(
                    read_json(path) if path.suffix == ".json"
                    else {"text": path.read_text(encoding="utf-8")}
                )
            except json.JSONDecodeError as exc:
                raise BuildError(f"invalid JSON artifact: {path}") from exc
    artifacts = [
        artifact_identity(path, output)
        for path in sorted(output.iterdir())
        if path.is_file()
        and path.name not in {
            "ARTIFACT_HASH_MANIFEST.json",
            "DETERMINISTIC_REGENERATION_RECEIPT.json",
        }
    ]
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    })
    return {
        "schema_version": VERSION + "-receipt-v1",
        "output": str(output),
        "candidate_count": 8,
        "candidate_event_rows": 6432,
        "target_surface_rows": reconciliation["target_surface_rows"],
        "lawful_target_entries": reconciliation["lawful_target_entries"],
        "formula_difference_count": headroom["formula_difference_count"],
        "input_bundle_sha256": package["input_bundle_sha256"],
        "artifact_count": len(artifacts) + 1,
        "real_scorer_invocations": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (repo / args.output_dir).resolve()
    )
    print(compact(build(
        repo=repo, output=output, workers=args.workers
    )))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
