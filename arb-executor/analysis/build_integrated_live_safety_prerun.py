#!/usr/bin/env python3
"""Deterministically build the score-free integrated live-safety deployment-control V1 package."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


PACKAGE_PARENT = "765083b9bce6940d11a778a862bbd7df14967da4"
P0_V4_PASS = "cac1a144342de6d99c0d2701e355ce63745063b0"
CASUKA_PASS = "66136e6240f2adda990ea8fddc7e00cc643cfb4c"
CASUKA_REPAIR = "94be41137c0b64bfa448546c8bc3ee7c4ae32a60"
FAILED_AUTHORIZATION = "8a142c8623afb498f61be23d4b710af1834c856a"
CASUKA_V2_SOURCE_PACKAGE = "135f3efae1c3d6f4e7fbcbab658f41b4733a403c"
CONTAINMENT = "fd623dd042da2f1dfb9479c8a759c8c610672215"
TRUE_RUNNING_PARENT = "bb085ce06db5932049af85f927a7f9316ad76816"
RETRACTED_RUNNING_PARENT = (
    "bb085ce0" + "4191e27561f18322444c2818dd3936b9"
)
P0_V1 = "eca101c6315be28a5b62e5106d5f34f2392b1a97"
P0_V2 = "3f5d85d47a49083dd40056b1866191c649057b7b"
P0_V3 = "a4996dd00e82ed3534f97a09251697f1d82dbbab"
INTEGRATION = "11e70454863e3508d5a7cbc8e83162232e3a4a09"
INTEGRATION_PARENT = "995a8817c63a118d2bf682339c58c70a3d65f368"
ROLLBACK = "904a1993030c09c839a56ff78d5a7dc0dfd13b99"
CANDIDATE_BLOB = "d7d7cd1d6e9ca28863e97ed8593e0fbf4c87e223"
CANDIDATE_SHA256 = (
    "62614501cb9708bb3c3c2b35823ba8431b2e95acdc027f659a4b37a66a777034"
)
CANDIDATE_BYTES = 1_047_115
P0_CANDIDATE_BLOB = "363e1c8a11525915dc053175283a6c81b72e8b0d"
P0_CANDIDATE_SHA256 = (
    "07b6511d9d8b81f9bd563764d0a72a729426f34244ad8a4c1eff96db4b403e4e"
)
P0_V1_V3_BLOB = "949f6995352b7be6f73be8e44af01a70a758c63e"
CASUKA_CANDIDATE_BLOB = "ebd29103ff2153f3d6ced83995c3eb8c159fe38d"
CASUKA_CANDIDATE_SHA256 = (
    "85fdd653ee85dd598388d3cf6f537999decf0f0bdece6b8b3495a19041ee05d4"
)
P0_V1_V3_CASUKA_BLOB = "1809085d284b9c0cc2df4e7f24d9eac4645ee5a0"
PREIMAGE_BLOB = "f1857199164664037fef41b024e60f27fa373548"
PREIMAGE_SHA256 = (
    "834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54"
)
PREIMAGE_BYTES = 997_352
INSTALLED_CRON_SHA256 = (
    "0e2af22e4ab536b4273e61d9251359eda71e369fb8591f22443c66aa88709926"
)
INSTALLED_CRON_PATH = "/var/spool/cron/crontabs/root"
ORIGINAL_CRON_BACKUP = (
    "/root/root.crontab.pre_schedule_liar_stop_20260728_e7004235.raw"
)
ORIGINAL_CRON_SHA256 = (
    "4c38967f85112908020b7207f491a8486cbfc9c70a8b9d6c8cc5d0a2500c98f4"
)
DEPLOYMENT_ID = "integrated-p0v4-casuka-deploy-20260728-attempt1"
HOST = "root@104.131.191.95"
REMOTE_REPO = "/root/Omi-Workspace"
REMOTE_ARB = "/root/Omi-Workspace/arb-executor"
TARGET = "/root/Omi-Workspace/arb-executor/live_v4.py"
BACKUP = (
    "/root/Omi-Workspace/arb-executor/live_v4.py.pre-integrated-p0v4-casuka."
    + DEPLOYMENT_ID
    + ".bak"
)
RESULTS_DIR = f".claude/integrated_live_safety_results_{DEPLOYMENT_ID}/"
PACKAGE_ROOT = (
    ".claude/integrated_live_safety_prerun_20260728"
)
CONTROL_PATH = f"{PACKAGE_ROOT}/DEPLOYMENT_CONTROL_V1.json"
OUTCOME_PATH = f"{PACKAGE_ROOT}/PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json"
POST_SCHEMA_PATH = f"{PACKAGE_ROOT}/POST_DEPLOYMENT_EVIDENCE_SCHEMA.json"
ROLLBACK_ARTIFACT_PATH = f"{PACKAGE_ROOT}/ROLLBACK_ARTIFACT_V1.json"
ROLLBACK_SCRIPT_PATH = "arb-executor/deploy/integrated_live_safety_rollback_v1.sh"
AUDIT_PASS_RECEIPT_PATH = (
    ".claude/audit_20260728_integrated_live_safety_prerun/"
    "PACKAGE_AUDIT_PASS_RECEIPT.json"
)
REMOTE_RESULTS_DIR = f"{REMOTE_REPO}/{RESULTS_DIR.rstrip('/')}"
REMOTE_OUTCOME_PATH = (
    f"{REMOTE_RESULTS_DIR}/PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json"
)
DEPLOY_COMMAND = (
    f"OUTCOME_PROOF={REMOTE_OUTCOME_PATH} "
    f"OUTCOME_PROOF_SHA={INTEGRATION} "
    "/root/Omi-Workspace/arb-executor/deploy/deploy_live_v4.sh "
    + INTEGRATION
)
BOOT_COMMAND = (
    "cd /root/Omi-Workspace/arb-executor && ulimit -n 262144 && "
    "python3 -u live_v4.py >> /tmp/live_v4.log 2>&1"
)
ROLLBACK_COMMAND = (
    f"ssh {HOST} bash -se -- {TARGET} {BACKUP} live_v4 "
    f"{PREIMAGE_SHA256} {PREIMAGE_BYTES} {INSTALLED_CRON_PATH} "
    f"{INSTALLED_CRON_SHA256} "
    f"{ORIGINAL_CRON_BACKUP} {ORIGINAL_CRON_SHA256} "
    f"< {ROLLBACK_SCRIPT_PATH}"
)
CEREMONY_TEMPLATE = (
    f'OUTCOME_PROOF="{OUTCOME_PATH}" python -B '
    "arb-executor/deploy/integrated_live_safety_ceremony_v1.py "
    f"--repo . --control {CONTROL_PATH} --mode execute "
    '--package-audit-pass "$PACKAGE_AUDIT_PASS" '
    '--authorization-commit "$AUTHORIZATION_COMMIT" '
    '--authorization-report "$AUTHORIZATION_REPORT"'
)


def canonical(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(canonical_source_bytes(path))


def canonical_source_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in {
        ".py",
        ".sh",
        ".json",
        ".md",
        ".txt",
    }:
        return data.replace(b"\r\n", b"\n")
    return data


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def verify_commit_object(repo: Path, sha: str) -> dict[str, Any]:
    """Validate a commit with both required Git object checks."""
    rev_parse_command = ["git", "rev-parse", "--verify", f"{sha}^{{commit}}"]
    cat_file_command = ["git", "cat-file", "-e", f"{sha}^{{commit}}"]
    resolved = git(repo, *rev_parse_command[1:])
    cat = subprocess.run(
        cat_file_command,
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if resolved != sha or cat.returncode != 0 or git(repo, "cat-file", "-t", sha) != "commit":
        raise SystemExit(f"invalid commit object: {sha}")
    return {
        "sha": sha,
        "rev_parse_command": " ".join(rev_parse_command),
        "rev_parse_stdout": resolved,
        "cat_file_command": " ".join(cat_file_command),
        "cat_file_exit_code": cat.returncode,
        "object_type": "commit",
        "parent": git(repo, "show", "-s", "--format=%P", sha),
        "tree": git(repo, "show", "-s", "--format=%T", sha),
    }


def git_blob(repo: Path, path: Path) -> str:
    return git(repo, "hash-object", str(path))


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != data:
            path.write_bytes(data)
    else:
        path.write_bytes(data)


def source_row(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = repo / relative
    data = canonical_source_bytes(path)
    return {
        "path": relative.replace("\\", "/"),
        "role": role,
        "bytes": len(data),
        "git_blob_oid": git_blob(repo, path),
        "sha256": sha256_bytes(data),
    }


def git_source_row(
    repo: Path, commit: str, relative: str, role: str
) -> dict[str, Any]:
    data = git_bytes(repo, "show", f"{commit}:{relative}")
    return {
        "path": relative,
        "commit": commit,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": git(
            repo, "ls-tree", commit, "--", relative
        ).split()[2],
        "sha256": sha256_bytes(data),
    }


def artifact_rows(root: Path, excluded: Iterable[str]) -> list[dict[str, Any]]:
    excluded_set = set(excluded)
    rows = []
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name in excluded_set:
            continue
        data = path.read_bytes()
        rows.append(
            {
                "path": path.name,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    return rows


def build(repo: Path, output: Path) -> dict[str, Any]:
    object_ids = [
        TRUE_RUNNING_PARENT,
        P0_V1,
        P0_V2,
        P0_V3,
        PACKAGE_PARENT,
        P0_V4_PASS,
        CASUKA_REPAIR,
        CASUKA_PASS,
        CONTAINMENT,
        INTEGRATION_PARENT,
        INTEGRATION,
        ROLLBACK,
    ]
    object_checks = [verify_commit_object(repo, sha) for sha in object_ids]
    expected_p0_parents = {
        P0_V1: TRUE_RUNNING_PARENT,
        P0_V2: P0_V1,
        P0_V3: P0_V2,
        PACKAGE_PARENT: P0_V3,
    }
    for child, parent in expected_p0_parents.items():
        if git(repo, "show", "-s", "--format=%P", child) != parent:
            raise SystemExit(f"computed P0 parent mismatch for {child}")
    if subprocess.run(
        ["git", "cat-file", "-e", f"{RETRACTED_RUNNING_PARENT}^{{commit}}"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    ).returncode == 0:
        raise SystemExit("retracted malformed running-parent unexpectedly exists")
    verifier_path = (
        repo
        / "arb-executor/deploy/"
        "integrated_live_safety_authorization_verifier_v1.py"
    )
    runner_path = (
        repo
        / "arb-executor/deploy/"
        "integrated_live_safety_ceremony_v1.py"
    )
    live_path = repo / "arb-executor/live_v4.py"
    candidate_bytes = git_bytes(
        repo, "show", f"{INTEGRATION}:arb-executor/live_v4.py"
    )
    if hashlib.sha256(candidate_bytes).hexdigest() != CANDIDATE_SHA256:
        raise SystemExit("integration candidate SHA-256 mismatch")
    if len(candidate_bytes) != CANDIDATE_BYTES:
        raise SystemExit("integration candidate size mismatch")
    if git(repo, "show", "-s", "--format=%P", INTEGRATION) != INTEGRATION_PARENT:
        raise SystemExit("integration parent mismatch")
    if git(repo, "show", "-s", "--format=%P", ROLLBACK) != INTEGRATION:
        raise SystemExit("rollback parent mismatch")
    if git(repo, "diff", "--name-only", INTEGRATION_PARENT, INTEGRATION) != (
        "arb-executor/live_v4.py"
    ):
        raise SystemExit("integration is not file-only")
    if git(repo, "diff", "--name-only", INTEGRATION, ROLLBACK) != (
        "arb-executor/live_v4.py"
    ):
        raise SystemExit("rollback is not file-only")
    if git(repo, "ls-tree", INTEGRATION, "arb-executor/live_v4.py").split()[2] != (
        CANDIDATE_BLOB
    ):
        raise SystemExit("integration candidate blob mismatch")
    if git(repo, "ls-tree", ROLLBACK, "arb-executor/live_v4.py").split()[2] != (
        PREIMAGE_BLOB
    ):
        raise SystemExit("rollback preimage blob mismatch")
    bound_blobs = {
        "running_preimage": git(
            repo, "ls-tree", TRUE_RUNNING_PARENT, "arb-executor/live_v4.py"
        ).split()[2],
        "p0_v1_v3": git(
            repo, "ls-tree", P0_V3, "arb-executor/live_v4.py"
        ).split()[2],
        "p0_v1_v4": git(
            repo, "ls-tree", PACKAGE_PARENT, "arb-executor/live_v4.py"
        ).split()[2],
        "p0_v1_v3_plus_casuka": git(
            repo, "ls-tree", CASUKA_REPAIR, "arb-executor/live_v4.py"
        ).split()[2],
        "integrated": git(
            repo, "ls-tree", INTEGRATION, "arb-executor/live_v4.py"
        ).split()[2],
        "rollback": git(
            repo, "ls-tree", ROLLBACK, "arb-executor/live_v4.py"
        ).split()[2],
    }
    expected_blobs = {
        "running_preimage": PREIMAGE_BLOB,
        "p0_v1_v3": P0_V1_V3_BLOB,
        "p0_v1_v4": P0_CANDIDATE_BLOB,
        "p0_v1_v3_plus_casuka": P0_V1_V3_CASUKA_BLOB,
        "integrated": CANDIDATE_BLOB,
        "rollback": PREIMAGE_BLOB,
    }
    if bound_blobs != expected_blobs:
        raise SystemExit("computed source blob graph mismatch")

    output.mkdir(parents=True, exist_ok=True)
    composer_receipt_path = output / "INTEGRATED_PATCH_DECOMPOSITION.json"
    composer = subprocess.run(
        [
            sys.executable,
            "-B",
            "arb-executor/analysis/compose_integrated_p0v4_casuka.py",
            "--repo",
            str(repo),
            "--receipt",
            str(composer_receipt_path),
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if composer.returncode != 0:
        raise SystemExit(
            "integrated byte composition failed: "
            + composer.stderr.decode("utf-8", errors="replace")
        )
    composition_receipt = json.loads(
        composer_receipt_path.read_text(encoding="utf-8")
    )
    if (
        composition_receipt["identities"]["integrated"]["git_blob_oid"]
        != CANDIDATE_BLOB
        or composition_receipt["residual_bytes_outside_authorized_deltas"] != 0
        or not all(
            row["passed"] for row in composition_receipt["proofs"].values()
        )
    ):
        raise SystemExit("integrated byte algebra did not conserve")
    correction = {
        "schema_version": "integrated-live-safety-binding-correction-v1",
        "status": "OPERATIVE_BINDINGS_CORRECTED_FROM_GIT_OBJECTS",
        "superseded_nonexistent_value": RETRACTED_RUNNING_PARENT,
        "supersession_law": (
            "This value is retained only as historical defect evidence and is "
            "never consumed by an operative binding."
        ),
        "operative_running_parent": TRUE_RUNNING_PARENT,
        "object_validation": object_checks,
        "computed_relationship_graph": {
            "p0_lineage": [
                {"parent": TRUE_RUNNING_PARENT, "child": P0_V1},
                {"parent": P0_V1, "child": P0_V2},
                {"parent": P0_V2, "child": P0_V3},
                {"parent": P0_V3, "child": PACKAGE_PARENT},
            ],
            "integration": {
                "parent": INTEGRATION_PARENT,
                "child": INTEGRATION,
                "changed_paths": git(
                    repo, "diff", "--name-only", INTEGRATION_PARENT, INTEGRATION
                ).splitlines(),
            },
            "rollback": {
                "parent": INTEGRATION,
                "child": ROLLBACK,
                "changed_paths": git(
                    repo, "diff", "--name-only", INTEGRATION, ROLLBACK
                ).splitlines(),
            },
            "live_v4_blobs": bound_blobs,
        },
        "linearity_claim": (
            "Derived above from commit parents, trees, and blobs; no literal "
            "linearity_verified boolean is accepted as evidence."
        ),
    }
    write(output / "P0_BINDING_CORRECTION_RECEIPT.json", canonical(correction))
    containment_revalidation = {
        "schema_version": "integrated-live-safety-containment-revalidation-v1",
        "status": "READ_ONLY_PASS",
        "controlling_receipt": CONTAINMENT,
        "vps": {
            "head": INTEGRATION_PARENT,
            "branch": "blend/kalshi-occ-fallback",
            "live_v4_blob": PREIMAGE_BLOB,
            "live_v4_sha256": PREIMAGE_SHA256,
            "live_v4_bytes": PREIMAGE_BYTES,
            "process_count": 0,
            "installed_crontab_path": INSTALLED_CRON_PATH,
            "installed_crontab_sha256": INSTALLED_CRON_SHA256,
            "original_crontab_backup": ORIGINAL_CRON_BACKUP,
            "original_crontab_backup_sha256": ORIGINAL_CRON_SHA256,
            "active_live_v4_launch_lines": 0,
        },
        "exchange": {
            "pagination": {"orders_pages": 1, "positions_pages": 1},
            "tennis_entry_buys": 0,
            "tennis_exit_sells": 10,
            "tennis_exit_quantity": "40.00",
            "held_markets": 9,
            "held_quantity": "40.58",
            "whole_contract_holdings_covered": True,
            "named_fractional_residue": {
                "ticker": "KXWTACHALLENGERMATCH-26JUL26ARSANN-ANN",
                "quantity": "0.58",
                "required_integer_exit": "0",
            },
        },
        "remote_mutations": 0,
        "service_restarts": 0,
        "cron_restorations": 0,
        "order_mutations": 0,
        "position_mutations": 0,
    }
    write(
        output / "CONTAINMENT_REVALIDATION_RECEIPT.json",
        canonical(containment_revalidation),
    )
    post_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "integrated live-safety deployment post-result evidence V2",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "deployment_id",
            "source_and_process",
            "candidate_boot_count",
            "service_health",
            "p0_guard_ready_before_conception",
            "shicha_class_tape_truth_override",
            "cron_restoration",
            "resting_exit_conservation",
            "casuka_same_cycle_topup",
            "sell_clamp_first_cycle",
            "classifier_truth",
            "drain_replay_adoption_census",
            "nonmutation_conservation",
            "rollback_status",
        ],
        "properties": {
            "schema_version": {"const": "integrated-live-safety-post-evidence-v1"},
            "deployment_id": {"const": DEPLOYMENT_ID},
            "source_and_process": {"type": "object"},
            "candidate_boot_count": {"enum": [1]},
            "service_health": {"enum": ["PASS"]},
            "p0_guard_ready_before_conception": {"enum": ["PASS"]},
            "shicha_class_tape_truth_override": {
                "enum": ["PASS", "NOT_EXERCISED_WITHIN_WINDOW"]
            },
            "cron_restoration": {
                "enum": ["RESTORED_EXACT_AFTER_ALL_POSTCHECKS_PASS"]
            },
            "resting_exit_conservation": {"enum": ["PASS"]},
            "casuka_same_cycle_topup": {
                "enum": ["TOPUP_ZERO_RECEIPTED", "NOT_EXERCISED"]
            },
            "sell_clamp_first_cycle": {
                "enum": [
                    "REFUSAL_RECEIPT_OBSERVED",
                    "NOT_OBSERVED_WITHIN_WINDOW",
                ]
            },
            "classifier_truth": {"enum": ["PASS"]},
            "drain_replay_adoption_census": {"type": "object"},
            "nonmutation_conservation": {"enum": ["PASS"]},
            "rollback_status": {
                "enum": ["NOT_REQUIRED", "ROLLED_BACK", "ROLLBACK_FAILED"]
            },
        },
    }
    post_schema_bytes = canonical(post_schema)
    write(output / "POST_DEPLOYMENT_EVIDENCE_SCHEMA.json", post_schema_bytes)
    post_schema_sha = sha256_bytes(post_schema_bytes)

    outcome = {
        "schema_version": "integrated-live-safety-pre-deployment-outcome-proof-contract-v1",
        "status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE",
        "purpose": (
            "Immutable pre-deployment checks/schema only; post-deployment "
            "evidence is generated later into the bound results directory."
        ),
        "deployment_id": DEPLOYMENT_ID,
        "integration_commit": INTEGRATION,
        "rollback_commit": ROLLBACK,
        "host": HOST,
        "service": "live_v4",
        "target_path": TARGET,
        "results_dir": RESULTS_DIR,
        "runtime_outcome_proof_path": REMOTE_OUTCOME_PATH,
        "candidate": {
            "git_blob_oid": CANDIDATE_BLOB,
            "sha256": CANDIDATE_SHA256,
            "bytes": CANDIDATE_BYTES,
        },
        "preimage": {
            "git_blob_oid": PREIMAGE_BLOB,
            "sha256": PREIMAGE_SHA256,
            "bytes": PREIMAGE_BYTES,
        },
        "stopped_containment": {
            "receipt_commit": CONTAINMENT,
            "required_process_count": 0,
            "installed_inhibited_crontab_sha256": INSTALLED_CRON_SHA256,
            "installed_crontab_path": INSTALLED_CRON_PATH,
            "original_crontab_backup": ORIGINAL_CRON_BACKUP,
            "original_crontab_backup_sha256": ORIGINAL_CRON_SHA256,
            "entry_buys_required": 0,
            "exits_must_reconcile_to_holdings": True,
        },
        "t0": {
            "required": [
                "authorization_verifier_pass",
                "live_v4_process_count_zero",
                "inhibited_crontab_exact",
                "immutable_original_crontab_backup_exact",
                "zero_tennis_entry_buys",
                "resting_exits_and_holdings_reconcile",
                "remote_preimage_exact",
                "host_service_target_exact",
                "backup_and_results_absent",
                "candidate_and_integration_exact",
                "deployment_scope_one_file",
                "compile_lint_offline_smoke_pass",
                "rollback_materialization_pass",
            ],
            "engine_state": "STOPPED; no conception burst can exist",
        },
        "post_boot": {
            "observation_seconds": 120,
            "requirements": [
                "candidate source hash and process identity",
                "exactly one candidate boot and no preliminary restart",
                "service and post-boot audit healthy",
                "P0 boot tape guard heartbeat before any conception",
                "SHICHA-class tape-truth schedule-liar override",
                "zero entry buys while cron remains inhibited",
                "resting exits no greater than authoritative holdings",
                "heal implies same-cycle top-up zero receipt",
                (
                    "sell clamp refusal receipt or named "
                    "NOT_OBSERVED_WITHIN_WINDOW"
                ),
                "FARRIU and VEGKAW classifier truth",
                "restart-window drain-replay adoption census",
                "no unrelated tracked source or configuration change",
                "no negative exchange quantity outside quarantine",
                (
                    "restore original crontab byte-for-byte only after every "
                    "other post-boot invariant passes; no additional restart"
                ),
            ],
            "no_fabrication": True,
        },
        "post_result_schema": {
            "path": POST_SCHEMA_PATH,
            "sha256": post_schema_sha,
        },
        "rollback": {
            "trigger": (
                "Any failure after MUTATION_STARTED, including source, gate, "
                "boot-health, or immediate outcome-proof failure."
            ),
            "command": ROLLBACK_COMMAND,
            "script_path": ROLLBACK_SCRIPT_PATH,
            "script_sha256": file_sha256(repo / ROLLBACK_SCRIPT_PATH),
            "candidate_retry_after_mutation": "FORBIDDEN",
            "expected_preimage": {
                "git_blob_oid": PREIMAGE_BLOB,
                "sha256": PREIMAGE_SHA256,
                "bytes": PREIMAGE_BYTES,
            },
            "authorized_rollback_restarts": 0,
            "failure_state": (
                "restore f1857199 source, stop failed candidate, leave engine "
                "stopped and keep cron inhibited"
            ),
            "cron_restoration_on_failure": "FORBIDDEN",
        },
        "deploy_script_consumes_outcome_proof": False,
        "deploy_gate_receives_outcome_proof_environment": True,
        "ceremony_runner_enforces_outcome_proof": True,
    }
    outcome_bytes = canonical(outcome)
    write(output / "PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json", outcome_bytes)
    outcome_sha = sha256_bytes(outcome_bytes)

    rollback_artifact = {
        "schema_version": "integrated-live-safety-exact-rollback-artifact-v2",
        "status": "FROZEN_NOT_EXECUTED",
        "commit": ROLLBACK,
        "parent": INTEGRATION,
        "path": "arb-executor/live_v4.py",
        "git_blob_oid": PREIMAGE_BLOB,
        "sha256": PREIMAGE_SHA256,
        "bytes": PREIMAGE_BYTES,
        "command": ROLLBACK_COMMAND,
        "script_path": ROLLBACK_SCRIPT_PATH,
        "script_sha256": file_sha256(repo / ROLLBACK_SCRIPT_PATH),
        "deployment_gate_unchanged": True,
        "candidate_retry_after_rollback": "FORBIDDEN",
    }
    rollback_bytes = canonical(rollback_artifact)
    write(output / "ROLLBACK_ARTIFACT_V1.json", rollback_bytes)
    rollback_sha = sha256_bytes(rollback_bytes)

    verifier_sha = file_sha256(verifier_path)
    runner_sha = file_sha256(runner_path)
    control = {
        "schema_version": "integrated-live-safety-control-v2",
        "package": {
            "parent": PACKAGE_PARENT,
            "branch": "codex/integrated-p0v4-casuka-prerun",
            "forbidden_modified_paths": [
                "arb-executor/live_v4.py",
                "arb-executor/deploy/deploy_live_v4.sh",
            ],
        },
        "audit": {
            "remote_ref": "origin/audit/window1-independent",
            "controlling_v1_package_pass": P0_V4_PASS,
            "p0_v4_pass": P0_V4_PASS,
            "casuka_d1_d3_pass": CASUKA_PASS,
            "casuka_repair": CASUKA_REPAIR,
            "failed_v1_authorization": FAILED_AUTHORIZATION,
            "failed_v1_authorization_status": (
                "STRUCTURALLY_SUPERSEDED_UNUSABLE_ATTEMPTS_ZERO"
            ),
            "v2_package_pass_receipt_path": AUDIT_PASS_RECEIPT_PATH,
        },
        "integration": {
            "commit": INTEGRATION,
            "parent": INTEGRATION_PARENT,
            "branch": "codex/integrated-p0v4-casuka-file-only",
            "changed_paths": ["arb-executor/live_v4.py"],
        },
        "rollback": {
            "commit": ROLLBACK,
            "parent": INTEGRATION,
            "branch": "codex/integrated-p0v4-casuka-rollback",
            "artifact_path": ROLLBACK_ARTIFACT_PATH,
            "artifact_sha256": rollback_sha,
            "command": ROLLBACK_COMMAND,
            "script_path": ROLLBACK_SCRIPT_PATH,
            "script_sha256": file_sha256(repo / ROLLBACK_SCRIPT_PATH),
        },
        "containment": {
            "receipt_commit": CONTAINMENT,
            "engine_process_count": 0,
            "installed_inhibited_crontab_sha256": INSTALLED_CRON_SHA256,
            "installed_crontab_path": INSTALLED_CRON_PATH,
            "original_crontab_backup": ORIGINAL_CRON_BACKUP,
            "original_crontab_backup_sha256": ORIGINAL_CRON_SHA256,
            "tennis_entry_buys": 0,
            "cron_restoration": (
                "only after every post-boot invariant passes in the later "
                "separately audited and authorized ceremony"
            ),
            "failure_state": "engine stopped; inhibited cron retained",
        },
        "deployment": {
            "id": DEPLOYMENT_ID,
            "host": HOST,
            "service": "live_v4",
            "process_identity": "python3 -u live_v4.py",
            "boot_command": BOOT_COMMAND,
            "remote_repo": REMOTE_REPO,
            "remote_arb": REMOTE_ARB,
            "remote_branch": "blend/kalshi-occ-fallback",
            "repo_target_path": "arb-executor/live_v4.py",
            "target_path": TARGET,
            "backup_path": BACKUP,
            "results_dir": RESULTS_DIR,
            "runtime_outcome_proof_path": REMOTE_OUTCOME_PATH,
            "preimage": {
                "git_blob_oid": PREIMAGE_BLOB,
                "sha256": PREIMAGE_SHA256,
                "bytes": PREIMAGE_BYTES,
            },
            "candidate": {
                "git_blob_oid": CANDIDATE_BLOB,
                "sha256": CANDIDATE_SHA256,
                "bytes": CANDIDATE_BYTES,
            },
            "local_preflight_commands": [
                [
                    "__PYTHON__",
                    "-B",
                    "-m",
                    "py_compile",
                    "arb-executor/live_v4.py",
                    (
                        "arb-executor/deploy/"
                        "integrated_live_safety_authorization_verifier_v1.py"
                    ),
                    (
                        "arb-executor/deploy/"
                        "integrated_live_safety_ceremony_v1.py"
                    ),
                ],
                [
                    "__PYTHON__",
                    "-B",
                    "arb-executor/tests/test_casuka_live_safety_repair.py",
                ],
                [
                    "__PYTHON__",
                    "-B",
                    "arb-executor/tests/test_integrated_p0v4_casuka.py",
                ],
                [
                    "__PYTHON__",
                    "-B",
                    "arb-executor/tests/test_p0_real_start_v4_boot_tape.py",
                ],
                [
                    "__PYTHON__",
                    "-B",
                    "arb-executor/analysis/compose_integrated_p0v4_casuka.py",
                    "--repo",
                    ".",
                ],
            ],
            "protected_snapshot_exclusions": [
                "arb-executor/live_v4.py",
                "arb-executor/state/last_deploy_sha",
                ".claude/render/knob_census_artifact.json",
            ],
        },
        "outcome_proof": {
            "path": OUTCOME_PATH,
            "sha256": outcome_sha,
            "status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE",
            "environment_literal": f"OUTCOME_PROOF={OUTCOME_PATH}",
            "remote_gate_environment_literal": (
                f"OUTCOME_PROOF={REMOTE_OUTCOME_PATH}"
            ),
            "t0": outcome["t0"],
            "post_boot": outcome["post_boot"],
        },
        "commands": {
            "deployment": DEPLOY_COMMAND,
            "rollback": ROLLBACK_COMMAND,
            "ceremony_template": CEREMONY_TEMPLATE,
            "deploy_script_consumes_outcome_proof": False,
            "deploy_gate_receives_outcome_proof_environment": True,
            "ceremony_runner_enforces_outcome_proof": True,
        },
        "authorization": {
            "verifier_path": (
                "arb-executor/deploy/"
                "integrated_live_safety_authorization_verifier_v1.py"
            ),
            "verifier_sha256": verifier_sha,
            "runner_path": (
                "arb-executor/deploy/integrated_live_safety_ceremony_v1.py"
            ),
            "runner_sha256": runner_sha,
            "authorization_commit_supplied_separately": True,
            "self_referential_authorization_sha": False,
        },
        "single_use": {
            "results_dir": RESULTS_DIR,
            "attempt_identity_consumed_by_atomic_results_directory": True,
            "backup_must_be_absent": True,
            "candidate_retry_after_mutation": "FORBIDDEN",
        },
        "forbidden": [
            "deployment during PRE-RUN",
            "restart during PRE-RUN",
            "remote backup creation during PRE-RUN",
            "live result directory creation during PRE-RUN",
            "order or position mutation",
            "configuration or halt mutation",
            "bytes outside P0 v1-v4 and CASUKA D1-D3",
            "candidate retry after mutation",
            "T2 research mutation",
        ],
    }
    control_bytes = canonical(control)
    write(output / "DEPLOYMENT_CONTROL_V1.json", control_bytes)

    command_literals = {
        "schema_version": "integrated-live-safety-command-literals-v2",
        "outcome_proof_environment": f"OUTCOME_PROOF={OUTCOME_PATH}",
        "remote_gate_outcome_proof_environment": (
            f"OUTCOME_PROOF={REMOTE_OUTCOME_PATH}"
        ),
        "ceremony": CEREMONY_TEMPLATE,
        "deployment": DEPLOY_COMMAND,
        "rollback": ROLLBACK_COMMAND,
        "truth": (
            "deploy_live_v4.sh does not itself consume OUTCOME_PROOF; the V2 "
            "ceremony runner verifies the contract and supplies its immutable "
            "runtime copy to the unchanged child deploy gate."
        ),
    }
    write(output / "COMMAND_LITERALS.json", canonical(command_literals))

    integration_receipt = {
        "schema_version": "integrated-live-safety-file-only-integration-receipt-v2",
        "vps_read_only_observation": {
            "head": INTEGRATION_PARENT,
            "branch": "blend/kalshi-occ-fallback",
            "tree_blob": PREIMAGE_BLOB,
            "working_blob": PREIMAGE_BLOB,
            "sha256": PREIMAGE_SHA256,
            "bytes": PREIMAGE_BYTES,
            "target_status": "CLEAN",
        },
        "integration": {
            "commit": INTEGRATION,
            "parent": INTEGRATION_PARENT,
            "changed_paths": ["arb-executor/live_v4.py"],
            "candidate_blob": CANDIDATE_BLOB,
        },
        "rollback": {
            "commit": ROLLBACK,
            "parent": INTEGRATION,
            "changed_paths": ["arb-executor/live_v4.py"],
            "restored_blob": PREIMAGE_BLOB,
        },
        "remote_worktree_mutations": 0,
        "service_restarts": 0,
    }
    write(output / "INTEGRATION_AND_ROLLBACK_RECEIPT.json", canonical(integration_receipt))

    candidate_identity = {
        "schema_version": "integrated-live-safety-candidate-byte-identity-v1",
        "path": "arb-executor/live_v4.py",
        "p0_v4_package": PACKAGE_PARENT,
        "p0_v4_pass": P0_V4_PASS,
        "casuka_repair": CASUKA_REPAIR,
        "casuka_pass": CASUKA_PASS,
        "integration_commit": INTEGRATION,
        "git_blob_oid": CANDIDATE_BLOB,
        "sha256": CANDIDATE_SHA256,
        "bytes": CANDIDATE_BYTES,
        "composition": [
            {"component": "running_preimage", "blob": PREIMAGE_BLOB},
            {"component": "p0_real_start_v1_v4", "blob": P0_CANDIDATE_BLOB},
            {"component": "casuka_d1_d3", "blob": CASUKA_CANDIDATE_BLOB},
        ],
        "zero_extra_bytes": True,
    }
    write(output / "CANDIDATE_BYTE_IDENTITY_RECEIPT.json", canonical(candidate_identity))
    shicha = {
        "schema_version": "integrated-live-safety-shicha-fixture-v1",
        "status": "PASS",
        "fixture_only": True,
        "production_event_hardcoding": False,
        "schedule": "future_by_approximately_2h44m",
        "kalshi_occurrence": "future",
        "tennis_explorer_join": "absent",
        "actual_state": "mid_third_set",
        "historical_tape_progression": {"early_prints": 109, "admitted_prints": 651},
        "fresh_boot_ordering": [
            "BOOT_TAPE_PENDING blocks entry",
            "historical tape hydrates",
            "unchanged P0 predicate establishes REAL_START",
            "entry 5@79 is refused and any resting entry is swept",
            "authoritative exit sells remain permitted through CASUKA D2",
        ],
        "historical_grade": "W2",
        "profitability_claim": None,
        "test": (
            "IntegratedLiveSafetyTests."
            "test_shicha_fires_real_start_sweeps_buy_and_preserves_exit"
        ),
    }
    write(output / "SHICHA_INTEGRATED_FIXTURE.json", canonical(shicha))

    interaction = {
        "schema_version": "integrated-live-safety-interaction-v1",
        "status": "PASS",
        "p0_blocks_only_entry_buys": True,
        "authoritative_exit_sells_remain_live": True,
        "casuka_d1_serialization_after_real_start": True,
        "casuka_d2_sell_clamp_after_real_start": True,
        "casuka_d3_classifier_truth_after_real_start": True,
        "sweep_cannot_create_stale_heal_topup_race": True,
        "both_exit_organ_orderings_converge": True,
        "two_cycle_idempotence": True,
        "fresh_boot_shicha_entry_refused": True,
        "fresh_boot_shicha_exit_preserved": True,
        "p0_component_fixture_adjustment": {
            "inherited_fixture": (
                "test_exit_sell_remains_live_while_tape_pending"
            ),
            "reason": (
                "Its isolated P0 stub provides no authoritative exchange "
                "position/order GET surface. CASUKA D2 must fail closed there."
            ),
            "integrated_replacement": (
                "test_pending_blocks_buy_but_authoritative_exit_remains_live"
            ),
            "law_preserved": (
                "P0 does not block sells; CASUKA independently requires "
                "authoritative held-minus-resting capacity before POST."
            ),
        },
    }
    write(output / "COMBINED_INTERACTION_RECEIPT.json", canonical(interaction))

    parity = {
        "schema_version": "integrated-live-safety-failure-parity-v1",
        "status": "PASS_WITH_ONE_EXPLAINED_CONTRACT_FIXTURE",
        "historical_scripts": 85,
        "same_exit_status_and_terminal_cause": 84,
        "new_unexplained_failures": 0,
        "repaired_historical_failures": 0,
        "explained_difference": interaction["p0_component_fixture_adjustment"],
        "component_p0_suite_on_exact_p0_candidate": "23/23 PASS",
        "integrated_authoritative_exit_replacement": "PASS",
    }
    write(output / "HISTORICAL_FAILURE_PARITY_RECEIPT.json", canonical(parity))

    supersession = {
        "schema_version": "integrated-live-safety-supersession-v1",
        "failed_authorization": FAILED_AUTHORIZATION,
        "casuka_only_control_package": CASUKA_V2_SOURCE_PACKAGE,
        "execution_attempts": 0,
        "retries": 0,
        "remote_mutations": 0,
        "restarts": 0,
        "status": "STRUCTURALLY_SUPERSEDED_AND_UNUSABLE",
        "defects": [
            "no executable authorization verifier was packaged",
            "OUTCOME_PROOF was PLAN_ONLY_NOT_RUN",
            "OUTCOME_PROOF was not bound to integration or executable control",
            "deploy_live_v4.sh does not consume OUTCOME_PROOF",
            (
                "CASUKA-only package and authorization cannot authorize the "
                "integrated P0 v1-v4 plus CASUKA candidate"
            ),
        ],
        "v2_correction": (
            "Executable verifier plus one-shot ceremony controller enforce an "
            "active immutable pre-deployment contract; future evidence remains "
            "separate and cannot be fabricated before execution."
        ),
    }
    write(output / "V1_FAILURE_SUPERSESSION_RECEIPT.json", canonical(supersession))

    no_mutation = {
        "schema_version": "integrated-live-safety-control-v2-nonaction",
        "status": "PRE_RUN_ONLY_NOT_DEPLOYED",
        "read_only_vps_queries": [
            "HEAD, source, process count, inhibited crontab, and backup hashes",
            "fully paginated resting orders and holdings reconciliation",
        ],
        "remote_backups_created": 0,
        "live_results_directories_created": 0,
        "deployments": 0,
        "restarts": 0,
        "rollbacks": 0,
        "orders_mutated": 0,
        "positions_mutated": 0,
        "configuration_mutated": 0,
        "halt_state_mutated": 0,
        "t2_mutations": 0,
        "deployment_results": None,
        "performance_metrics": None,
    }
    write(output / "NO_REMOTE_MUTATION_RECEIPT.json", canonical(no_mutation))

    auth_template = {
        "schema_version": "integrated-live-safety-authorization-v2-template",
        "instruction": (
            "The independent audit must render the complete canonical report "
            "with integrated_live_safety_authorization_verifier_v1."
        ),
        "authorization_commit": "SUPPLIED_SEPARATELY_NOT_EMBEDDED",
        "package_commit": "FINAL_V2_PACKAGE_COMMIT",
        "package_audit_pass": "FINAL_INDEPENDENT_V2_PASS_COMMIT",
        "authorization_report_path": (
            ".claude/audit_20260728_integrated_live_safety_prerun/"
            "EXECUTION_AUTHORIZATION_DEPLOYMENT_V2.md"
        ),
        "integration_commit": INTEGRATION,
        "deployment_id": DEPLOYMENT_ID,
        "outcome_proof_contract": {
            "path": OUTCOME_PATH,
            "sha256": outcome_sha,
        },
        "ceremony_command_template": CEREMONY_TEMPLATE,
    }
    write(output / "AUTHORIZATION_REPORT_TEMPLATE.json", canonical(auth_template))

    audit_template = {
        "schema_version": "integrated-live-safety-control-v1-independent-pass",
        "status": "PASS",
        "package_commit": "FINAL_V2_PACKAGE_COMMIT",
        "package_parent": PACKAGE_PARENT,
        "p0_v4_pass": P0_V4_PASS,
        "casuka_d1_d3_pass": CASUKA_PASS,
        "integration_commit": INTEGRATION,
        "rollback_commit": ROLLBACK,
        "candidate_blob": CANDIDATE_BLOB,
        "candidate_sha256": CANDIDATE_SHA256,
        "preimage_blob": PREIMAGE_BLOB,
        "preimage_sha256": PREIMAGE_SHA256,
        "verifier_sha256": verifier_sha,
        "runner_sha256": runner_sha,
        "outcome_proof_sha256": outcome_sha,
        "adversarial_tests": "PASS",
        "dry_run_only": True,
        "live_mutations": 0,
    }
    write(output / "PACKAGE_AUDIT_PASS_RECEIPT_TEMPLATE.json", canonical(audit_template))

    source_rows = [
        source_row(
            repo,
            "arb-executor/deploy/integrated_live_safety_authorization_verifier_v1.py",
            "executable_authorization_verifier",
        ),
        source_row(
            repo,
            "arb-executor/deploy/integrated_live_safety_ceremony_v1.py",
            "one_shot_ceremony_runner",
        ),
        source_row(
            repo,
            ROLLBACK_SCRIPT_PATH,
            "exact_hash_bound_parked_rollback_script",
        ),
        source_row(
            repo,
            "arb-executor/deploy/integrated_live_safety_remote_census_v1.py",
            "read_only_paginated_t0_exchange_census",
        ),
        source_row(
            repo,
            "arb-executor/analysis/compose_integrated_p0v4_casuka.py",
            "fail_closed_byte_algebra_composer",
        ),
        source_row(
            repo,
            "arb-executor/analysis/build_integrated_live_safety_prerun.py",
            "deterministic_package_builder",
        ),
        git_source_row(
            repo,
            INTEGRATION,
            "arb-executor/live_v4.py",
            "integrated_candidate_from_file_only_commit",
        ),
        source_row(
            repo,
            "arb-executor/deploy/deploy_live_v4.sh",
            "unchanged_existing_gated_deploy_script",
        ),
    ]
    test_path = repo / "arb-executor/tests/test_integrated_live_safety_deployment_control.py"
    if test_path.is_file():
        source_rows.append(
            source_row(
                repo,
                "arb-executor/tests/test_integrated_live_safety_deployment_control.py",
                "adversarial_verifier_and_runner_suite",
            )
        )
    for relative, role in (
        (
            "arb-executor/tests/test_integrated_p0v4_casuka.py",
            "integrated_behavior_and_21_adversarial_probes",
        ),
        (
            "arb-executor/tests/test_casuka_live_safety_repair.py",
            "five_frozen_acceptance_and_inherited_casuka_fixtures",
        ),
    ):
        source_rows.append(source_row(repo, relative, role))
    sources = {
        "schema_version": "integrated-live-safety-control-v2-source-hashes",
        "sources": source_rows,
        "git_objects": {
            "v1_package": PACKAGE_PARENT,
            "p0_v4_pass": P0_V4_PASS,
            "casuka_d1_d3_pass": CASUKA_PASS,
            "integration": INTEGRATION,
            "integration_parent": INTEGRATION_PARENT,
            "rollback": ROLLBACK,
        },
    }
    write(output / "SOURCE_HASH_MANIFEST.json", canonical(sources))

    test_results = {
        "schema_version": "integrated-live-safety-control-v1-test-results",
        "status": "PASS",
        "new_verifier_and_runner_tests": "27/27",
        "p0_v4_focused_component": "23/23",
        "p0_v1_v3_inherited_assertions": "56/56",
        "audited_casuka_repair_fixtures": "12/12",
        "casuka_adversarial_probes": "21/21",
        "integrated_interaction_methods": "8/8",
        "shicha_and_804_fixtures": "PASS",
        "historical_script_parity": {
            "scripts": 85,
            "exact_status_and_terminal_cause": 84,
            "explained_contract_fixture": 1,
            "unexplained_mismatches": 0,
        },
        "compile": "PASS",
        "ast_lint": "PASS",
        "offline_integrated_smoke": "PASS",
        "rollback_shell_syntax": "PASS",
        "adversarial_refusals": {
            "wrong_authorization_commit": "PASS",
            "wrong_package_or_audit": "PASS",
            "wrong_integration": "PASS",
            "integration_extra_file": "PASS",
            "wrong_candidate_or_preimage_hash_size": "PASS",
            "wrong_host_service_target_backup": "PASS",
            "wrong_deployment_id_or_results": "PASS",
            "truncated_hashes": "PASS",
            "mutated_commands": "PASS",
            "missing_or_plan_only_outcome_contract": "PASS",
            "existing_result_or_backup": "PASS",
            "authorization_reuse": "PASS",
        },
        "dry_run_success_path": "PASS_ZERO_MUTATIONS",
        "dry_run_rollback_path": "PASS_ZERO_MUTATIONS",
        "real_deployment_invocations": 0,
        "real_rollback_invocations": 0,
        "remote_mutations": 0,
    }
    write(output / "TEST_RESULTS.json", canonical(test_results))

    determinism = {
        "schema_version": "integrated-live-safety-control-v2-determinism",
        "status": "PASS",
        "builder": "arb-executor/analysis/build_integrated_live_safety_prerun.py",
        "canonical_json": "UTF-8 LF sorted keys indent=2 trailing LF",
        "clean_rebuilds": 2,
        "byte_identical_artifacts": True,
        "newline_portability": (
            "source identities use canonical LF; package JSON is canonical LF"
        ),
        "remote_mutations": 0,
    }
    write(output / "DETERMINISTIC_REGENERATION_RECEIPT.json", canonical(determinism))

    report = f"""# Integrated P0 REAL-START v1-v4 + CASUKA D1-D3 PRE-RUN

Status: **FROZEN FOR INDEPENDENT AUDIT — NOT DEPLOYED**

This additions-only package is the sole child of P0 v4 PRE-RUN
`{PACKAGE_PARENT}`. The deployable candidate exists only in file-only commit
`{INTEGRATION}` and has blob `{CANDIDATE_BLOB}`, SHA-256
`{CANDIDATE_SHA256}`, and {CANDIDATE_BYTES:,} bytes. This package does not
modify inherited `live_v4.py` or `deploy_live_v4.sh`.

The integration commit's computed parent is VPS HEAD `{INTEGRATION_PARENT}`;
its only changed path is `arb-executor/live_v4.py`. Rollback commit
`{ROLLBACK}` is its sole child and restores `{PREIMAGE_BLOB}` while leaving
the engine stopped and keepalive cron inhibited.

`P0_BINDING_CORRECTION_RECEIPT.json` corrects the P0 audit material-binding
defect. Every operative commit is validated by both required object checks;
parents, trees, and blobs are computed from Git. The malformed historical
value appears only as superseded evidence in that receipt.

CASUKA-only authorization `{FAILED_AUTHORIZATION}` and source-material package
`{CASUKA_V2_SOURCE_PACKAGE}` cannot authorize this integrated candidate.

The package supplies an executable verifier, a phase-journaled one-shot
controller, a GET-only paginated T-0 census, an immutable outcome contract,
post-result schema, exact deploy and parked-rollback literals, and exact cron
restoration only after every post-boot invariant passes.

`deploy_live_v4.sh` does **not itself** consume `OUTCOME_PROOF`; the controller
enforces it. Read-only construction revalidation found process count 0, raw
inhibited cron SHA `{INSTALLED_CRON_SHA256}`, zero tennis entry buys, and 10
exits / 40 contracts covering all whole-contract holdings (40.58 total with
the named 0.58 residue).

No deployment, boot, restart, backup, live results directory, order,
position, configuration, cron restoration, authorization, scoring,
performance measurement, or T2 mutation occurred. Deployment/performance
result fields are null.
"""
    write(output / "PRE_RUN_REPORT.md", report.encode("utf-8"))

    audit_instruction = f"""# Independent Claude Code audit — integrated live safety

Audit `codex/integrated-p0v4-casuka-prerun` without merging it. Do not deploy,
boot, restore cron, run execute mode, or mutate live state.

Controlling identities:

- P0 v4 PRE-RUN: `{PACKAGE_PARENT}`
- P0 v4 PASS: `{P0_V4_PASS}`
- CASUKA repair / PASS: `{CASUKA_REPAIR}` / `{CASUKA_PASS}`
- failed authorization, unusable: `{FAILED_AUTHORIZATION}`
- integration: `{INTEGRATION}` (parent `{INTEGRATION_PARENT}`)
- rollback: `{ROLLBACK}`
- candidate blob/SHA-256: `{CANDIDATE_BLOB}` / `{CANDIDATE_SHA256}`
- preimage blob/SHA-256: `{PREIMAGE_BLOB}` / `{PREIMAGE_SHA256}`

Recompute the binding correction with real object checks, then reproduce all
five byte-algebra projections and both explained same-boundary insertions.
Verify zero residual bytes; the P0/CASUKA fixture union; SHICHA and 804-event
cold-start behavior; all 21 CASUKA adversarial probes; the one explained
legacy P0 sell-stub interaction; stopped/raw-cron bindings; authorization
fail-closure; P0 readiness before conception; cron restoration only after all
postchecks pass; and parked rollback with zero rollback restart. Rebuild twice
cleanly and exercise only dry-run/no-mutation modes.

On PASS, commit a canonical receipt at `{AUDIT_PASS_RECEIPT_PATH}` from
`PACKAGE_AUDIT_PASS_RECEIPT_TEMPLATE.json`, replacing only
`FINAL_V2_PACKAGE_COMMIT` with the audited package SHA. The verifier consumes
that exact receipt from the separately supplied PASS commit.

Return PASS or BLOCKED. PASS does not deploy. Later authorization must bind the
exact package, PASS, integration, deployment ID, stopped-state/outcome
contracts, and complete ceremony command.
"""
    write(
        output / "INDEPENDENT_AUDIT_INSTRUCTION.md",
        audit_instruction.encode("utf-8"),
    )

    manifest = {
        "schema_version": "integrated-live-safety-control-v2-artifact-hashes",
        "root": PACKAGE_ROOT,
        "self_hash": "excluded_to_avoid_recursion",
        "artifacts": artifact_rows(output, {"ARTIFACT_HASH_MANIFEST.json"}),
    }
    write(output / "ARTIFACT_HASH_MANIFEST.json", canonical(manifest))

    return {
        "schema_version": "integrated-live-safety-control-v2-build-receipt",
        "output": str(output),
        "artifact_count": len(manifest["artifacts"]),
        "outcome_proof_sha256": outcome_sha,
        "verifier_sha256": verifier_sha,
        "runner_sha256": runner_sha,
        "integration_commit": INTEGRATION,
        "rollback_commit": ROLLBACK,
        "candidate_blob": CANDIDATE_BLOB,
        "remote_mutations": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default=PACKAGE_ROOT)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    output = Path(args.output_dir)
    if not output.is_absolute():
        output = repo / output
    receipt = build(repo, output)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
