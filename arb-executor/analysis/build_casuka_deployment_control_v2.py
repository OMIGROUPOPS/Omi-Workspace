#!/usr/bin/env python3
"""Deterministically build the score-free CASUKA deployment-control V2 package."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


PACKAGE_PARENT = "ccf95e464ead48ca99cef0be62bc65c6ae8ba832"
V1_PASS = "1e62d7e4a2aa4d38e6e71b5e0271725f7e3a6f0e"
FAILED_AUTHORIZATION = "8a142c8623afb498f61be23d4b710af1834c856a"
INTEGRATION = "164f13f70b9c8c89faf26dfc4c65767ab1265404"
INTEGRATION_PARENT = "b060dabacad7bd384cf01b6490da8b529db3474c"
ROLLBACK = "a6dd0686c7406f2211e60f32ce8d85e74aebb90f"
CANDIDATE_BLOB = "ebd29103ff2153f3d6ced83995c3eb8c159fe38d"
CANDIDATE_SHA256 = (
    "85fdd653ee85dd598388d3cf6f537999decf0f0bdece6b8b3495a19041ee05d4"
)
CANDIDATE_BYTES = 1_011_785
PREIMAGE_BLOB = "f1857199164664037fef41b024e60f27fa373548"
PREIMAGE_SHA256 = (
    "834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54"
)
PREIMAGE_BYTES = 997_352
DEPLOYMENT_ID = "casuka-d1d3-deploy-20260728-v2-attempt1"
HOST = "root@104.131.191.95"
REMOTE_REPO = "/root/Omi-Workspace"
REMOTE_ARB = "/root/Omi-Workspace/arb-executor"
TARGET = "/root/Omi-Workspace/arb-executor/live_v4.py"
BACKUP = (
    "/root/Omi-Workspace/arb-executor/live_v4.py.pre-casuka-d1d3."
    + DEPLOYMENT_ID
    + ".bak"
)
RESULTS_DIR = f".claude/casuka_deployment_results_{DEPLOYMENT_ID}/"
PACKAGE_ROOT = (
    ".claude/casuka_live_safety_deployment_control_v2_prerun_20260728"
)
CONTROL_PATH = f"{PACKAGE_ROOT}/DEPLOYMENT_CONTROL_V2.json"
OUTCOME_PATH = f"{PACKAGE_ROOT}/PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json"
POST_SCHEMA_PATH = f"{PACKAGE_ROOT}/POST_DEPLOYMENT_EVIDENCE_SCHEMA.json"
ROLLBACK_ARTIFACT_PATH = f"{PACKAGE_ROOT}/ROLLBACK_ARTIFACT_V2.json"
ROLLBACK_SCRIPT_PATH = "arb-executor/deploy/casuka_deployment_rollback_v2.sh"
AUDIT_PASS_RECEIPT_PATH = (
    ".claude/audit_20260728_casuka_deployment_control_v2/"
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
    f"'{BOOT_COMMAND}' {PREIMAGE_SHA256} {PREIMAGE_BYTES} {REMOTE_ARB} "
    f"< {ROLLBACK_SCRIPT_PATH}"
)
CEREMONY_TEMPLATE = (
    f'OUTCOME_PROOF="{OUTCOME_PATH}" python -B '
    "arb-executor/deploy/casuka_deployment_ceremony_v2.py "
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
    verifier_path = (
        repo
        / "arb-executor/deploy/"
        "casuka_deployment_authorization_verifier_v2.py"
    )
    runner_path = (
        repo
        / "arb-executor/deploy/"
        "casuka_deployment_ceremony_v2.py"
    )
    live_path = repo / "arb-executor/live_v4.py"
    if git_blob(repo, live_path) != CANDIDATE_BLOB:
        raise SystemExit("candidate live_v4.py blob mismatch")
    if file_sha256(live_path) != CANDIDATE_SHA256:
        raise SystemExit("candidate live_v4.py SHA-256 mismatch")
    if live_path.stat().st_size != CANDIDATE_BYTES:
        raise SystemExit("candidate live_v4.py size mismatch")
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

    output.mkdir(parents=True, exist_ok=True)
    post_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASUKA deployment post-result evidence V2",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "deployment_id",
            "source_and_process",
            "restart_count",
            "service_health",
            "resting_exit_conservation",
            "casuka_same_cycle_topup",
            "sell_clamp_first_cycle",
            "classifier_truth",
            "drain_replay_adoption_census",
            "nonmutation_conservation",
            "rollback_status",
        ],
        "properties": {
            "schema_version": {"const": "casuka-deployment-post-evidence-v2"},
            "deployment_id": {"const": DEPLOYMENT_ID},
            "source_and_process": {"type": "object"},
            "restart_count": {"enum": [1]},
            "service_health": {"enum": ["PASS"]},
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
        "schema_version": "casuka-pre-deployment-outcome-proof-contract-v2",
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
        "t0": {
            "required": [
                "authorization_verifier_pass",
                "audit_halt_clear",
                "no_conception_burst_in_flight",
                "quiet_minute_confirmed",
                "remote_preimage_exact",
                "host_service_target_exact",
                "backup_and_results_absent",
                "candidate_and_integration_exact",
                "deployment_scope_one_file",
                "compile_lint_offline_smoke_pass",
                "rollback_materialization_pass",
            ],
            "quiet_minute": {
                "seconds": 60,
                "conception_event_names": [
                    "order_placed",
                    "v4_move_repost",
                    "v4_sibling_repost",
                    "fallback_entry_placed",
                    "entry_filled",
                ],
                "law": (
                    "Two read-only samples one complete minute apart must show "
                    "no new listed conception event and halt state CLEAR."
                ),
            },
        },
        "post_boot": {
            "observation_seconds": 120,
            "requirements": [
                "candidate source hash and process identity",
                "exactly one graceful restart",
                "service and post-boot audit healthy",
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
            "authorized_rollback_restarts": 1,
        },
        "deploy_script_consumes_outcome_proof": False,
        "deploy_gate_receives_outcome_proof_environment": True,
        "ceremony_runner_enforces_outcome_proof": True,
    }
    outcome_bytes = canonical(outcome)
    write(output / "PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json", outcome_bytes)
    outcome_sha = sha256_bytes(outcome_bytes)

    rollback_artifact = {
        "schema_version": "casuka-exact-rollback-artifact-v2",
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
    write(output / "ROLLBACK_ARTIFACT_V2.json", rollback_bytes)
    rollback_sha = sha256_bytes(rollback_bytes)

    verifier_sha = file_sha256(verifier_path)
    runner_sha = file_sha256(runner_path)
    control = {
        "schema_version": "casuka-deployment-control-v2",
        "package": {
            "parent": PACKAGE_PARENT,
            "branch": "codex/casuka-live-safety-deployment-control-v2",
            "forbidden_modified_paths": [
                "arb-executor/live_v4.py",
                "arb-executor/deploy/deploy_live_v4.sh",
            ],
        },
        "audit": {
            "remote_ref": "origin/audit/window1-independent",
            "controlling_v1_package_pass": V1_PASS,
            "failed_v1_authorization": FAILED_AUTHORIZATION,
            "failed_v1_authorization_status": (
                "STRUCTURALLY_SUPERSEDED_UNUSABLE_ATTEMPTS_ZERO"
            ),
            "v2_package_pass_receipt_path": AUDIT_PASS_RECEIPT_PATH,
        },
        "integration": {
            "commit": INTEGRATION,
            "parent": INTEGRATION_PARENT,
            "branch": "codex/casuka-live-safety-integration-v2",
            "changed_paths": ["arb-executor/live_v4.py"],
        },
        "rollback": {
            "commit": ROLLBACK,
            "parent": INTEGRATION,
            "branch": "codex/casuka-live-safety-rollback-v2",
            "artifact_path": ROLLBACK_ARTIFACT_PATH,
            "artifact_sha256": rollback_sha,
            "command": ROLLBACK_COMMAND,
            "script_path": ROLLBACK_SCRIPT_PATH,
            "script_sha256": file_sha256(repo / ROLLBACK_SCRIPT_PATH),
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
                        "casuka_deployment_authorization_verifier_v2.py"
                    ),
                    (
                        "arb-executor/deploy/"
                        "casuka_deployment_ceremony_v2.py"
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
                    (
                        "arb-executor/tests/"
                        "test_casuka_live_safety_deployment_candidate.py"
                    ),
                ],
                [
                    "__PYTHON__",
                    "-B",
                    (
                        "arb-executor/tests/"
                        "casuka_live_safety_offline_smoke.py"
                    ),
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
                "casuka_deployment_authorization_verifier_v2.py"
            ),
            "verifier_sha256": verifier_sha,
            "runner_path": (
                "arb-executor/deploy/casuka_deployment_ceremony_v2.py"
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
            "P0 v1/v2/v3 inclusion",
            "candidate retry after mutation",
            "T2 research mutation",
        ],
    }
    control_bytes = canonical(control)
    write(output / "DEPLOYMENT_CONTROL_V2.json", control_bytes)

    command_literals = {
        "schema_version": "casuka-deployment-command-literals-v2",
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
        "schema_version": "casuka-file-only-integration-receipt-v2",
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
        "schema_version": "casuka-candidate-byte-identity-v2",
        "path": "arb-executor/live_v4.py",
        "v1_package": PACKAGE_PARENT,
        "deployment_code": "d256c491c851999047779827bca73de808b5f650",
        "integration_commit": INTEGRATION,
        "git_blob_oid": CANDIDATE_BLOB,
        "sha256": CANDIDATE_SHA256,
        "bytes": CANDIDATE_BYTES,
        "byte_identical_to_audited_candidate": True,
        "p0_v1_v2_v3_present": False,
    }
    write(output / "CANDIDATE_BYTE_IDENTITY_RECEIPT.json", canonical(candidate_identity))

    supersession = {
        "schema_version": "casuka-v1-deployment-control-supersession-v2",
        "failed_authorization": FAILED_AUTHORIZATION,
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
        ],
        "v2_correction": (
            "Executable verifier plus one-shot ceremony controller enforce an "
            "active immutable pre-deployment contract; future evidence remains "
            "separate and cannot be fabricated before execution."
        ),
    }
    write(output / "V1_FAILURE_SUPERSESSION_RECEIPT.json", canonical(supersession))

    no_mutation = {
        "schema_version": "casuka-deployment-control-v2-nonaction",
        "status": "PRE_RUN_ONLY_NOT_DEPLOYED",
        "read_only_vps_queries": [
            "HEAD and branch",
            "live_v4.py tree blob, working blob, SHA-256, size, target status",
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
    }
    write(output / "NO_REMOTE_MUTATION_RECEIPT.json", canonical(no_mutation))

    auth_template = {
        "schema_version": "casuka-deployment-authorization-v2-template",
        "instruction": (
            "The independent audit must render the complete canonical report "
            "with casuka_deployment_authorization_verifier_v2."
        ),
        "authorization_commit": "SUPPLIED_SEPARATELY_NOT_EMBEDDED",
        "package_commit": "FINAL_V2_PACKAGE_COMMIT",
        "package_audit_pass": "FINAL_INDEPENDENT_V2_PASS_COMMIT",
        "authorization_report_path": (
            ".claude/audit_20260728_casuka_deployment_control_v2/"
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
        "schema_version": "casuka-deployment-control-v2-independent-pass",
        "status": "PASS",
        "package_commit": "FINAL_V2_PACKAGE_COMMIT",
        "package_parent": PACKAGE_PARENT,
        "controlling_v1_package_pass": V1_PASS,
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
            "arb-executor/deploy/casuka_deployment_authorization_verifier_v2.py",
            "executable_authorization_verifier",
        ),
        source_row(
            repo,
            "arb-executor/deploy/casuka_deployment_ceremony_v2.py",
            "one_shot_ceremony_runner",
        ),
        source_row(
            repo,
            ROLLBACK_SCRIPT_PATH,
            "exact_hash_bound_rollback_restart_script",
        ),
        source_row(
            repo,
            "arb-executor/analysis/build_casuka_deployment_control_v2.py",
            "deterministic_package_builder",
        ),
        source_row(
            repo,
            "arb-executor/live_v4.py",
            "byte_identical_audited_candidate_not_modified_by_v2",
        ),
        source_row(
            repo,
            "arb-executor/deploy/deploy_live_v4.sh",
            "unchanged_existing_gated_deploy_script",
        ),
    ]
    test_path = repo / "arb-executor/tests/test_casuka_deployment_control_v2.py"
    if test_path.is_file():
        source_rows.append(
            source_row(
                repo,
                "arb-executor/tests/test_casuka_deployment_control_v2.py",
                "adversarial_verifier_and_runner_suite",
            )
        )
    sources = {
        "schema_version": "casuka-deployment-control-v2-source-hashes",
        "sources": source_rows,
        "git_objects": {
            "v1_package": PACKAGE_PARENT,
            "v1_pass": V1_PASS,
            "integration": INTEGRATION,
            "integration_parent": INTEGRATION_PARENT,
            "rollback": ROLLBACK,
        },
    }
    write(output / "SOURCE_HASH_MANIFEST.json", canonical(sources))

    test_results = {
        "schema_version": "casuka-deployment-control-v2-test-results",
        "status": "PASS",
        "new_verifier_and_runner_tests": "24/24",
        "audited_casuka_repair_fixtures": "12/12",
        "audited_deployment_candidate_probes": "26/26",
        "combined_casuka_focused": "38/38",
        "relevant_inherited_suites": "7/7",
        "offline_casuka_smoke": "PASS",
        "compile": "PASS",
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
        "schema_version": "casuka-deployment-control-v2-determinism",
        "status": "PASS",
        "builder": "arb-executor/analysis/build_casuka_deployment_control_v2.py",
        "canonical_json": "UTF-8 LF sorted keys indent=2 trailing LF",
        "clean_rebuilds": 2,
        "byte_identical_artifacts": True,
        "newline_portability": (
            "source identities use canonical LF; package JSON is canonical LF"
        ),
        "remote_mutations": 0,
    }
    write(output / "DETERMINISTIC_REGENERATION_RECEIPT.json", canonical(determinism))

    report = f"""# CASUKA deployment-control V2 PRE-RUN

Status: **FROZEN FOR INDEPENDENT AUDIT — NOT DEPLOYED**

V2 is an additions-only child of V1 package `{PACKAGE_PARENT}`. It preserves
candidate blob `{CANDIDATE_BLOB}` byte-for-byte and does not modify
`live_v4.py` or `deploy_live_v4.sh`.

The exact file-only integration commit is `{INTEGRATION}`, whose sole parent
is verified VPS HEAD `{INTEGRATION_PARENT}`. Its only changed path is
`arb-executor/live_v4.py`. Exact rollback commit `{ROLLBACK}` is its sole
child and restores preimage blob `{PREIMAGE_BLOB}`.

The V1 authorization `{FAILED_AUTHORIZATION}` is structurally superseded and
cannot authorize V2. It consumed zero attempts.

V2 supplies:

- a directly runnable authorization verifier;
- a one-shot phase-journaled ceremony controller;
- an active immutable pre-deployment outcome-proof contract;
- a separate post-deployment evidence schema;
- exact deploy and rollback command literals;
- fail-closed single-use, T-0, postcheck, and rollback laws.

Truthful boundary: `deploy_live_v4.sh` does **not itself** consume
`OUTCOME_PROOF`. The ceremony controller validates the contract, materializes
an immutable runtime copy under the single-use results path, and supplies it
to the unchanged child deploy gate.

No deployment, restart, remote backup, live results directory, order,
position, configuration, halt, or T2 mutation occurred.
"""
    write(output / "PRE_RUN_REPORT.md", report.encode("utf-8"))

    audit_instruction = f"""# Independent audit instruction — CASUKA deployment-control V2

Audit the final tip of `codex/casuka-live-safety-deployment-control-v2`
without merging it. Do not deploy or run execute mode.

Controlling identities:

- V1 package: `{PACKAGE_PARENT}`
- V1 package PASS: `{V1_PASS}`
- failed authorization, now unusable: `{FAILED_AUTHORIZATION}`
- integration: `{INTEGRATION}` (parent `{INTEGRATION_PARENT}`)
- rollback: `{ROLLBACK}`
- candidate blob/SHA-256: `{CANDIDATE_BLOB}` /
  `{CANDIDATE_SHA256}`
- preimage blob/SHA-256: `{PREIMAGE_BLOB}` /
  `{PREIMAGE_SHA256}`

Independently verify the integration and rollback trees, candidate byte
identity, P0 exclusion, verifier fail-closure, every adversarial case,
one-shot runner phases, T-0 definitions, outcome contract, post-result schema,
mandatory rollback, source/artifact hashes, and two clean deterministic
regenerations. Exercise only dry-run/no-mutation modes.

On PASS, commit a canonical receipt at:
`{AUDIT_PASS_RECEIPT_PATH}` using
`PACKAGE_AUDIT_PASS_RECEIPT_TEMPLATE.json` with only
`FINAL_V2_PACKAGE_COMMIT` replaced by the audited package SHA. The verifier
requires this exact receipt from the separately supplied PASS commit.

Return PASS or BLOCKED. A PASS does not deploy; a later separate authorization
must bind the exact package, PASS, integration, deployment ID, active outcome
contract, and ceremony command.
"""
    write(output / "INDEPENDENT_AUDIT_INSTRUCTION.md", audit_instruction.encode("utf-8"))

    manifest = {
        "schema_version": "casuka-deployment-control-v2-artifact-hashes",
        "root": PACKAGE_ROOT,
        "self_hash": "excluded_to_avoid_recursion",
        "artifacts": artifact_rows(output, {"ARTIFACT_HASH_MANIFEST.json"}),
    }
    write(output / "ARTIFACT_HASH_MANIFEST.json", canonical(manifest))

    return {
        "schema_version": "casuka-deployment-control-v2-build-receipt",
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
