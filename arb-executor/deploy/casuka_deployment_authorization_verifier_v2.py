#!/usr/bin/env python3
"""Fail-closed authorization verifier for the CASUKA D1-D3 ceremony.

This verifier deliberately does not deploy.  It binds a separately committed
authorization report to an already-frozen package, integration commit,
rollback commit, outcome-proof contract, paths, hashes, and command literals.
Execute mode also performs read-only remote preflight probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DEPLOYMENT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{7,127}$")
REPORT_TITLE = "# CASUKA D1-D3 DEPLOYMENT AUTHORIZATION V2\n\n"
REPORT_EXPLANATION = (
    "This canonical report authorizes one ceremony. The authorization commit "
    "is supplied separately and is intentionally absent from the payload.\n\n"
)
REPORT_OPEN = "```json\n"
REPORT_CLOSE = "```\n"


class VerificationError(RuntimeError):
    """A fail-closed authorization or integrity failure."""


@dataclass(frozen=True)
class VerificationRequest:
    repo: Path
    control_path: str
    authorization_commit: str
    authorization_report: str
    package_commit: str
    package_audit_pass: str
    integration_commit: str
    deployment_id: str
    host: str
    service: str
    target_path: str
    backup_path: str
    preimage_blob: str
    preimage_sha256: str
    preimage_size: int
    candidate_blob: str
    candidate_sha256: str
    candidate_size: int
    results_dir: str
    outcome_proof_contract: str
    outcome_proof_sha256: str
    deployment_command: str
    rollback_command: str
    rollback_artifact: str
    mode: str
    remote_state_fixture: Path | None = None


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def render_authorization_report(payload: Mapping[str, Any]) -> bytes:
    return (
        REPORT_TITLE.encode("utf-8")
        + REPORT_EXPLANATION.encode("utf-8")
        + REPORT_OPEN.encode("utf-8")
        + canonical_json_bytes(payload)
        + REPORT_CLOSE.encode("utf-8")
    )


def _strict_keys(
    value: Mapping[str, Any], expected: set[str], label: str
) -> None:
    actual = set(value)
    if actual != expected:
        raise VerificationError(
            f"{label} keys mismatch: missing={sorted(expected - actual)} "
            f"extra={sorted(actual - expected)}"
        )


def _strict_int(
    value: Any, label: str, *, minimum: int = 0, maximum: int | None = None
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VerificationError(f"{label} must be an exact integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise VerificationError(f"{label} outside frozen range")
    return value


def _strict_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise VerificationError(f"{label} must be nonempty exact text")
    if "\x00" in value or "\r" in value:
        raise VerificationError(f"{label} contains forbidden bytes")
    return value


def _sha1(value: Any, label: str) -> str:
    text = _strict_text(value, label)
    if not SHA1_RE.fullmatch(text):
        raise VerificationError(f"{label} must be a complete lowercase SHA-1")
    return text


def _sha256(value: Any, label: str) -> str:
    text = _strict_text(value, label)
    if not SHA256_RE.fullmatch(text):
        raise VerificationError(
            f"{label} must be a complete lowercase SHA-256"
        )
    return text


def _repo_relative_path(value: Any, label: str, *, directory: bool = False) -> str:
    text = _strict_text(value, label).replace("\\", "/")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise VerificationError(f"{label} must be a normalized repo path")
    if directory and not text.endswith("/"):
        raise VerificationError(f"{label} must end with /")
    if not directory and text.endswith("/"):
        raise VerificationError(f"{label} must name a file")
    return text


def _absolute_posix_path(value: Any, label: str) -> str:
    text = _strict_text(value, label)
    path = PurePosixPath(text)
    if not path.is_absolute() or ".." in path.parts:
        raise VerificationError(f"{label} must be a normalized absolute path")
    return text


def _run(
    args: Sequence[str],
    *,
    cwd: Path,
    input_bytes: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        list(args),
        cwd=str(cwd),
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise VerificationError(
            f"command failed ({result.returncode}): {' '.join(args)}: {stderr}"
        )
    return result


def _git(repo: Path, *args: str) -> str:
    return _run(("git", *args), cwd=repo).stdout.decode("utf-8").strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    return _run(("git", *args), cwd=repo).stdout


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_commit(repo: Path, commit: str, label: str) -> None:
    _sha1(commit, label)
    resolved = _git(repo, "rev-parse", f"{commit}^{{commit}}")
    if resolved != commit:
        raise VerificationError(f"{label} does not resolve exactly")


def _commit_parent(repo: Path, commit: str) -> str:
    parents = _git(repo, "show", "-s", "--format=%P", commit).split()
    if len(parents) != 1:
        raise VerificationError(f"{commit} must have exactly one parent")
    return parents[0]


def _tree_blob(repo: Path, commit: str, path: str) -> str:
    fields = _git(repo, "ls-tree", commit, "--", path).split()
    if len(fields) < 3:
        raise VerificationError(f"missing tree path {commit}:{path}")
    return fields[2]


def _diff_names(repo: Path, parent: str, child: str) -> list[str]:
    raw = _git(repo, "diff", "--name-only", parent, child)
    return [line for line in raw.splitlines() if line]


def _load_json_bytes(data: bytes, label: str) -> Mapping[str, Any]:
    normalized = data.replace(b"\r\n", b"\n")
    try:
        value = json.loads(normalized.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"{label} is not canonical UTF-8 JSON: {exc}")
    if not isinstance(value, dict):
        raise VerificationError(f"{label} must be a JSON object")
    if canonical_json_bytes(value) != normalized:
        raise VerificationError(f"{label} must use canonical package encoding")
    return value


def load_control(repo: Path, control_path: str) -> Mapping[str, Any]:
    relative = _repo_relative_path(control_path, "control_path")
    path = repo / relative
    if not path.is_file():
        raise VerificationError("control file missing")
    control = _load_json_bytes(path.read_bytes(), "control")
    required = {
        "schema_version",
        "package",
        "audit",
        "integration",
        "rollback",
        "deployment",
        "outcome_proof",
        "commands",
        "authorization",
        "single_use",
        "forbidden",
    }
    _strict_keys(control, required, "control")
    if control["schema_version"] != "casuka-deployment-control-v2":
        raise VerificationError("unsupported control schema")
    return control


def expected_authorization_payload(
    control: Mapping[str, Any],
    package_commit: str,
    package_audit_pass: str,
    authorization_report: str,
) -> dict[str, Any]:
    audit = control["audit"]
    integration = control["integration"]
    rollback = control["rollback"]
    deployment = control["deployment"]
    proof = control["outcome_proof"]
    commands = control["commands"]
    return {
        "schema_version": "casuka-deployment-authorization-v2",
        "authorization_state": "AUTHORIZED_ONCE",
        "authorization_commit_supplied_separately": True,
        "authorization_report_path": authorization_report,
        "package_commit": package_commit,
        "package_audit_pass": package_audit_pass,
        "controlling_v1_package_pass": audit["controlling_v1_package_pass"],
        "integration_commit": integration["commit"],
        "rollback_commit": rollback["commit"],
        "deployment_id": deployment["id"],
        "host": deployment["host"],
        "service": deployment["service"],
        "target_path": deployment["target_path"],
        "backup_path": deployment["backup_path"],
        "preimage": deployment["preimage"],
        "candidate": deployment["candidate"],
        "results_dir": deployment["results_dir"],
        "outcome_proof_contract": {
            "path": proof["path"],
            "sha256": proof["sha256"],
            "status": proof["status"],
        },
        "deployment_command": commands["deployment"],
        "rollback_command": commands["rollback"],
        "ceremony_command_template": commands["ceremony_template"],
        "failed_v1_authorization_superseded": audit[
            "failed_v1_authorization"
        ],
        "candidate_retry_after_mutation": "FORBIDDEN",
    }


def _verify_control_values(
    request: VerificationRequest, control: Mapping[str, Any]
) -> None:
    package = control["package"]
    audit = control["audit"]
    integration = control["integration"]
    rollback = control["rollback"]
    deployment = control["deployment"]
    proof = control["outcome_proof"]
    commands = control["commands"]
    single_use = control["single_use"]

    expected_pairs = {
        "integration_commit": (
            request.integration_commit,
            integration["commit"],
        ),
        "deployment_id": (request.deployment_id, deployment["id"]),
        "host": (request.host, deployment["host"]),
        "service": (request.service, deployment["service"]),
        "target_path": (request.target_path, deployment["target_path"]),
        "backup_path": (request.backup_path, deployment["backup_path"]),
        "preimage_blob": (
            request.preimage_blob,
            deployment["preimage"]["git_blob_oid"],
        ),
        "preimage_sha256": (
            request.preimage_sha256,
            deployment["preimage"]["sha256"],
        ),
        "preimage_size": (
            request.preimage_size,
            deployment["preimage"]["bytes"],
        ),
        "candidate_blob": (
            request.candidate_blob,
            deployment["candidate"]["git_blob_oid"],
        ),
        "candidate_sha256": (
            request.candidate_sha256,
            deployment["candidate"]["sha256"],
        ),
        "candidate_size": (
            request.candidate_size,
            deployment["candidate"]["bytes"],
        ),
        "results_dir": (request.results_dir, deployment["results_dir"]),
        "outcome_proof_contract": (
            request.outcome_proof_contract,
            proof["path"],
        ),
        "outcome_proof_sha256": (
            request.outcome_proof_sha256,
            proof["sha256"],
        ),
        "deployment_command": (
            request.deployment_command,
            commands["deployment"],
        ),
        "rollback_command": (
            request.rollback_command,
            commands["rollback"],
        ),
        "rollback_artifact": (
            request.rollback_artifact,
            rollback["artifact_path"],
        ),
    }
    mismatches = [
        label for label, (actual, expected) in expected_pairs.items()
        if actual != expected
    ]
    if mismatches:
        raise VerificationError(
            "runtime bindings differ from control: " + ", ".join(mismatches)
        )

    _sha1(request.package_commit, "package_commit")
    _sha1(request.package_audit_pass, "package_audit_pass")
    _sha1(request.integration_commit, "integration_commit")
    _sha1(request.authorization_commit, "authorization_commit")
    _sha1(request.preimage_blob, "preimage_blob")
    _sha1(request.candidate_blob, "candidate_blob")
    _sha256(request.preimage_sha256, "preimage_sha256")
    _sha256(request.candidate_sha256, "candidate_sha256")
    _sha256(request.outcome_proof_sha256, "outcome_proof_sha256")
    _strict_int(request.preimage_size, "preimage_size", minimum=1)
    _strict_int(request.candidate_size, "candidate_size", minimum=1)
    if not DEPLOYMENT_ID_RE.fullmatch(request.deployment_id):
        raise VerificationError("deployment_id has invalid syntax")
    _absolute_posix_path(request.target_path, "target_path")
    _absolute_posix_path(request.backup_path, "backup_path")
    _repo_relative_path(request.results_dir, "results_dir", directory=True)
    _repo_relative_path(
        request.outcome_proof_contract, "outcome_proof_contract"
    )
    _repo_relative_path(request.rollback_artifact, "rollback_artifact")
    if request.results_dir != single_use["results_dir"]:
        raise VerificationError("single-use results directory mismatch")
    if package["branch"] != "codex/casuka-live-safety-deployment-control-v2":
        raise VerificationError("unexpected package branch")


def _verify_git_and_files(
    request: VerificationRequest, control: Mapping[str, Any]
) -> dict[str, Any]:
    repo = request.repo
    package = control["package"]
    audit = control["audit"]
    integration = control["integration"]
    rollback = control["rollback"]
    deployment = control["deployment"]
    proof = control["outcome_proof"]
    commands = control["commands"]

    for label, commit in (
        ("authorization_commit", request.authorization_commit),
        ("package_commit", request.package_commit),
        ("package_audit_pass", request.package_audit_pass),
        ("controlling_v1_package_pass", audit["controlling_v1_package_pass"]),
        ("integration_commit", request.integration_commit),
        ("integration_parent", integration["parent"]),
        ("rollback_commit", rollback["commit"]),
    ):
        _require_commit(repo, commit, label)

    if _commit_parent(repo, request.package_commit) != package["parent"]:
        raise VerificationError("package commit is not the sole V1 child")
    if _commit_parent(repo, request.authorization_commit) != (
        request.package_audit_pass
    ):
        raise VerificationError(
            "authorization commit must be the sole child of the supplied PASS"
        )
    if _commit_parent(repo, request.integration_commit) != integration["parent"]:
        raise VerificationError("integration parent mismatch")
    if _commit_parent(repo, rollback["commit"]) != request.integration_commit:
        raise VerificationError("rollback parent mismatch")

    audit_receipt_path = _repo_relative_path(
        audit["v2_package_pass_receipt_path"],
        "v2_package_pass_receipt_path",
    )
    audit_receipt_bytes = _git_bytes(
        repo, "show", f"{request.package_audit_pass}:{audit_receipt_path}"
    )
    audit_receipt = _load_json_bytes(
        audit_receipt_bytes, "V2 package audit PASS receipt"
    )
    expected_audit_receipt = {
        "schema_version": "casuka-deployment-control-v2-independent-pass",
        "status": "PASS",
        "package_commit": request.package_commit,
        "package_parent": package["parent"],
        "controlling_v1_package_pass": audit["controlling_v1_package_pass"],
        "integration_commit": request.integration_commit,
        "rollback_commit": rollback["commit"],
        "candidate_blob": request.candidate_blob,
        "candidate_sha256": request.candidate_sha256,
        "preimage_blob": request.preimage_blob,
        "preimage_sha256": request.preimage_sha256,
        "verifier_sha256": control["authorization"]["verifier_sha256"],
        "runner_sha256": control["authorization"]["runner_sha256"],
        "outcome_proof_sha256": request.outcome_proof_sha256,
        "adversarial_tests": "PASS",
        "dry_run_only": True,
        "live_mutations": 0,
    }
    if audit_receipt != expected_audit_receipt:
        raise VerificationError("V2 package audit PASS receipt mismatch")

    if _diff_names(repo, integration["parent"], request.integration_commit) != [
        deployment["repo_target_path"]
    ]:
        raise VerificationError("integration diff is not exactly one file")
    if _diff_names(repo, request.integration_commit, rollback["commit"]) != [
        deployment["repo_target_path"]
    ]:
        raise VerificationError("rollback diff is not exactly one file")

    if (
        _tree_blob(repo, integration["parent"], deployment["repo_target_path"])
        != request.preimage_blob
    ):
        raise VerificationError("integration parent preimage blob mismatch")
    if (
        _tree_blob(repo, request.integration_commit, deployment["repo_target_path"])
        != request.candidate_blob
    ):
        raise VerificationError("integration candidate blob mismatch")
    if (
        _tree_blob(repo, rollback["commit"], deployment["repo_target_path"])
        != request.preimage_blob
    ):
        raise VerificationError("rollback does not restore preimage blob")
    if (
        _tree_blob(repo, request.package_commit, deployment["repo_target_path"])
        != request.candidate_blob
    ):
        raise VerificationError("package candidate blob mismatch")
    candidate_bytes = _git_bytes(repo, "cat-file", "blob", request.candidate_blob)
    if len(candidate_bytes) != request.candidate_size:
        raise VerificationError("candidate Git object size mismatch")
    if hashlib.sha256(candidate_bytes).hexdigest() != request.candidate_sha256:
        raise VerificationError("candidate Git object SHA-256 mismatch")
    preimage_bytes = _git_bytes(repo, "cat-file", "blob", request.preimage_blob)
    if len(preimage_bytes) != request.preimage_size:
        raise VerificationError("preimage Git object size mismatch")
    if hashlib.sha256(preimage_bytes).hexdigest() != request.preimage_sha256:
        raise VerificationError("preimage Git object SHA-256 mismatch")

    for label, path, expected_hash in (
        (
            "authorization verifier",
            control["authorization"]["verifier_path"],
            control["authorization"]["verifier_sha256"],
        ),
        (
            "ceremony runner",
            control["authorization"]["runner_path"],
            control["authorization"]["runner_sha256"],
        ),
    ):
        source_bytes = _git_bytes(
            repo, "show", f"{request.package_commit}:{path}"
        )
        if hashlib.sha256(source_bytes).hexdigest() != expected_hash:
            raise VerificationError(f"{label} source hash mismatch")

    outcome_path = repo / request.outcome_proof_contract
    if not outcome_path.is_file():
        raise VerificationError("pre-deployment outcome-proof contract missing")
    outcome_bytes = _git_bytes(
        repo,
        "show",
        f"{request.package_commit}:{request.outcome_proof_contract}",
    )
    if hashlib.sha256(outcome_bytes).hexdigest() != request.outcome_proof_sha256:
        raise VerificationError("outcome-proof contract hash mismatch")
    outcome = _load_json_bytes(outcome_bytes, "outcome contract")
    if outcome.get("status") != "PRE_DEPLOYMENT_CONTRACT_ACTIVE":
        raise VerificationError("outcome-proof contract is missing or PLAN_ONLY")
    if outcome.get("integration_commit") != request.integration_commit:
        raise VerificationError("outcome contract integration mismatch")
    if outcome.get("deployment_id") != request.deployment_id:
        raise VerificationError("outcome contract deployment ID mismatch")
    outcome_bindings = {
        "host": request.host,
        "service": request.service,
        "target_path": request.target_path,
        "results_dir": request.results_dir,
        "rollback_commit": rollback["commit"],
        "candidate": deployment["candidate"],
        "preimage": deployment["preimage"],
        "runtime_outcome_proof_path": deployment[
            "runtime_outcome_proof_path"
        ],
    }
    if any(outcome.get(key) != value for key, value in outcome_bindings.items()):
        raise VerificationError("outcome contract frozen binding mismatch")

    rollback_path = repo / request.rollback_artifact
    if not rollback_path.is_file():
        raise VerificationError("rollback artifact missing")
    rollback_bytes = _git_bytes(
        repo, "show", f"{request.package_commit}:{request.rollback_artifact}"
    )
    if hashlib.sha256(rollback_bytes).hexdigest() != rollback["artifact_sha256"]:
        raise VerificationError("rollback artifact hash mismatch")
    if rollback["command"] != request.rollback_command:
        raise VerificationError("rollback command mismatch")
    rollback_script = _git_bytes(
        repo,
        "show",
        f"{request.package_commit}:{rollback['script_path']}",
    )
    if hashlib.sha256(rollback_script).hexdigest() != rollback["script_sha256"]:
        raise VerificationError("rollback script hash mismatch")
    if commands["deployment"] != request.deployment_command:
        raise VerificationError("deployment command mismatch")

    package_ref = f"origin/{package['branch']}"
    if _git(repo, "rev-parse", package_ref) != request.package_commit:
        raise VerificationError("local/remote package equality failed")
    if _git(repo, "rev-parse", f"origin/{integration['branch']}") != (
        request.integration_commit
    ):
        raise VerificationError("integration branch equality failed")
    if _git(repo, "rev-parse", f"origin/{rollback['branch']}") != (
        rollback["commit"]
    ):
        raise VerificationError("rollback branch equality failed")
    audit_ref = audit["remote_ref"]
    for label, commit in (
        ("authorization", request.authorization_commit),
        ("package audit", request.package_audit_pass),
        ("V1 package audit", audit["controlling_v1_package_pass"]),
    ):
        result = _run(
            ("git", "merge-base", "--is-ancestor", commit, audit_ref),
            cwd=repo,
            check=False,
        )
        if result.returncode != 0:
            raise VerificationError(f"{label} commit not on audit ref")

    report_path = _repo_relative_path(
        request.authorization_report, "authorization_report"
    )
    report_bytes = _git_bytes(
        repo, "show", f"{request.authorization_commit}:{report_path}"
    )
    payload = expected_authorization_payload(
        control,
        request.package_commit,
        request.package_audit_pass,
        report_path,
    )
    if "authorization_commit" in payload:
        raise VerificationError("self-referential authorization payload")
    expected_report = render_authorization_report(payload)
    if report_bytes != expected_report:
        raise VerificationError(
            "authorization report is not the complete canonical V2 text"
        )

    current_head = _git(repo, "rev-parse", "HEAD")
    if current_head != request.package_commit:
        raise VerificationError("worktree HEAD is not the package commit")
    if _git(repo, "status", "--porcelain=v1"):
        raise VerificationError("relevant package worktree is not clean")

    package_changed = _diff_names(repo, package["parent"], request.package_commit)
    if any(path in package["forbidden_modified_paths"] for path in package_changed):
        raise VerificationError("V2 package modified an inherited frozen path")
    name_status = _git(
        repo, "diff", "--name-status", package["parent"], request.package_commit
    ).splitlines()
    if any(not line.startswith("A\t") for line in name_status):
        raise VerificationError("V2 package must be additions-only")

    return {
        "authorization_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        "package_changed_paths": package_changed,
        "integration_parent": integration["parent"],
        "integration_commit": request.integration_commit,
        "rollback_commit": rollback["commit"],
        "candidate_blob": request.candidate_blob,
        "preimage_blob": request.preimage_blob,
    }


def _read_remote_state_fixture(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        raise VerificationError("remote-state fixture missing")
    return _load_json_bytes(path.read_bytes(), "remote-state fixture")


def probe_remote_state(
    request: VerificationRequest, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Read-only remote probe. No backup, result path, or state is created."""
    if request.mode == "dry-run":
        if request.remote_state_fixture is None:
            raise VerificationError("dry-run requires a remote-state fixture")
        return _read_remote_state_fixture(request.remote_state_fixture)
    if request.mode != "execute":
        raise VerificationError("unsupported verifier mode")
    if request.remote_state_fixture is not None:
        raise VerificationError("execute mode forbids remote-state fixtures")

    deployment = control["deployment"]
    remote_repo = deployment["remote_repo"]
    remote_results = str(PurePosixPath(remote_repo) / request.results_dir)
    script = r"""
import hashlib, json, os, pathlib, re, subprocess, sys
repo, target, backup, results, service, process = sys.argv[1:]
def run(*args):
    return subprocess.check_output(args, text=True).strip()
p = pathlib.Path(target)
h = hashlib.sha256(p.read_bytes()).hexdigest()
status = run("git", "-C", repo, "status", "--porcelain=v1", "--",
             os.path.relpath(target, repo))
tree = run("git", "-C", repo, "ls-tree", "HEAD",
           os.path.relpath(target, repo)).split()
tmux = subprocess.run(["tmux", "has-session", "-t", service],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode == 0
pg = subprocess.run(["pgrep", "-af", "^" + re.escape(process) + "$"], text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
rows = [line for line in pg.stdout.splitlines()
        if line.strip() and "pgrep -af" not in line]
print(json.dumps({
  "schema_version": "casuka-remote-preflight-state-v2",
  "host": sys.argv[0] if False else "",
  "repo_head": run("git", "-C", repo, "rev-parse", "HEAD"),
  "repo_branch": run("git", "-C", repo, "rev-parse", "--abbrev-ref", "HEAD"),
  "target_path": target,
  "target_git_blob": run("git", "-C", repo, "hash-object", target),
  "target_tree_blob": tree[2] if len(tree) >= 3 else "",
  "target_sha256": h,
  "target_bytes": p.stat().st_size,
  "target_status": status,
  "backup_exists": pathlib.Path(backup).exists(),
  "results_exists": pathlib.Path(results).exists(),
  "tmux_session_alive": tmux,
  "process_count": len(rows),
  "process_rows": rows,
}, sort_keys=True))
"""
    result = _run(
        (
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            request.host,
            "python3",
            "-c",
            script,
            remote_repo := deployment["remote_repo"],
            request.target_path,
            request.backup_path,
            remote_results,
            request.service,
            deployment["process_identity"],
        ),
        cwd=request.repo,
    )
    try:
        state = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"remote probe returned invalid JSON: {exc}")
    state["host"] = request.host
    state["remote_repo"] = remote_repo
    return state


def _verify_remote_state(
    request: VerificationRequest,
    control: Mapping[str, Any],
    state: Mapping[str, Any],
) -> dict[str, Any]:
    deployment = control["deployment"]
    expected = {
        "schema_version": "casuka-remote-preflight-state-v2",
        "host": request.host,
        "remote_repo": deployment["remote_repo"],
        "repo_head": control["integration"]["parent"],
        "repo_branch": deployment["remote_branch"],
        "target_path": request.target_path,
        "target_git_blob": request.preimage_blob,
        "target_tree_blob": request.preimage_blob,
        "target_sha256": request.preimage_sha256,
        "target_bytes": request.preimage_size,
        "target_status": "",
        "backup_exists": False,
        "results_exists": False,
        "tmux_session_alive": True,
        "process_count": 1,
    }
    mismatches = [
        key for key, value in expected.items() if state.get(key) != value
    ]
    if mismatches:
        raise VerificationError(
            "remote preflight mismatch: " + ", ".join(sorted(mismatches))
        )
    rows = state.get("process_rows")
    if not isinstance(rows, list) or len(rows) != 1:
        raise VerificationError("remote process identity is ambiguous")
    if deployment["process_identity"] not in rows[0]:
        raise VerificationError("remote process identity mismatch")
    local_results = request.repo / request.results_dir
    if local_results.exists():
        raise VerificationError("local results path already exists")
    return {
        "remote_head": state["repo_head"],
        "remote_target_blob": state["target_git_blob"],
        "remote_target_sha256": state["target_sha256"],
        "backup_absent": True,
        "results_absent": True,
        "single_use_identity_available": True,
    }


def verify(request: VerificationRequest) -> dict[str, Any]:
    repo = request.repo.resolve()
    if not (repo / ".git").exists() and not _run(
        ("git", "rev-parse", "--git-dir"), cwd=repo, check=False
    ).returncode == 0:
        raise VerificationError("repo is not a Git worktree")
    control = load_control(repo, request.control_path)
    _verify_control_values(request, control)
    git_receipt = _verify_git_and_files(request, control)
    remote_state = probe_remote_state(request, control)
    remote_receipt = _verify_remote_state(request, control, remote_state)
    return {
        "schema_version": "casuka-deployment-authorization-verification-v2",
        "status": "PASS",
        "mode": request.mode,
        "authorization_commit": request.authorization_commit,
        "authorization_report": request.authorization_report,
        "package_commit": request.package_commit,
        "deployment_id": request.deployment_id,
        "git": git_receipt,
        "remote": remote_receipt,
        "no_mutation_performed": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--control", required=True)
    parser.add_argument("--authorization-commit", required=True)
    parser.add_argument("--authorization-report", required=True)
    parser.add_argument("--package-commit", required=True)
    parser.add_argument("--package-audit-pass", required=True)
    parser.add_argument("--integration-commit", required=True)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--backup-path", required=True)
    parser.add_argument("--preimage-blob", required=True)
    parser.add_argument("--preimage-sha256", required=True)
    parser.add_argument("--preimage-size", required=True)
    parser.add_argument("--candidate-blob", required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--candidate-size", required=True)
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--outcome-proof-contract", required=True)
    parser.add_argument("--outcome-proof-sha256", required=True)
    parser.add_argument("--deployment-command", required=True)
    parser.add_argument("--rollback-command", required=True)
    parser.add_argument("--rollback-artifact", required=True)
    parser.add_argument("--mode", choices=("dry-run", "execute"), required=True)
    parser.add_argument("--remote-state-fixture")
    parser.add_argument("--receipt-out")
    return parser


def _parse_exact_cli_int(value: str, label: str) -> int:
    if not re.fullmatch(r"(0|[1-9][0-9]*)", value):
        raise VerificationError(f"{label} must be exact decimal integer text")
    return _strict_int(int(value), label, minimum=1)


def request_from_namespace(ns: argparse.Namespace) -> VerificationRequest:
    return VerificationRequest(
        repo=Path(ns.repo),
        control_path=ns.control,
        authorization_commit=ns.authorization_commit,
        authorization_report=ns.authorization_report,
        package_commit=ns.package_commit,
        package_audit_pass=ns.package_audit_pass,
        integration_commit=ns.integration_commit,
        deployment_id=ns.deployment_id,
        host=ns.host,
        service=ns.service,
        target_path=ns.target_path,
        backup_path=ns.backup_path,
        preimage_blob=ns.preimage_blob,
        preimage_sha256=ns.preimage_sha256,
        preimage_size=_parse_exact_cli_int(ns.preimage_size, "preimage_size"),
        candidate_blob=ns.candidate_blob,
        candidate_sha256=ns.candidate_sha256,
        candidate_size=_parse_exact_cli_int(ns.candidate_size, "candidate_size"),
        results_dir=ns.results_dir,
        outcome_proof_contract=ns.outcome_proof_contract,
        outcome_proof_sha256=ns.outcome_proof_sha256,
        deployment_command=ns.deployment_command,
        rollback_command=ns.rollback_command,
        rollback_artifact=ns.rollback_artifact,
        mode=ns.mode,
        remote_state_fixture=(
            Path(ns.remote_state_fixture) if ns.remote_state_fixture else None
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    ns = _parser().parse_args(argv)
    try:
        receipt = verify(request_from_namespace(ns))
    except VerificationError as exc:
        print(
            json.dumps(
                {
                    "schema_version": (
                        "casuka-deployment-authorization-verification-v2"
                    ),
                    "status": "FAIL",
                    "error": str(exc),
                    "no_mutation_performed": True,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    output = canonical_json_bytes(receipt)
    if ns.receipt_out:
        path = Path(ns.receipt_out)
        if path.exists():
            print("receipt path already exists", file=sys.stderr)
            return 2
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(output)
    sys.stdout.buffer.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
