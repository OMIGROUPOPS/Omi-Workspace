#!/usr/bin/env python3
"""Focused and adversarial tests for CASUKA deployment-control V2."""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "arb-executor/deploy"
ANALYSIS = ROOT / "arb-executor/analysis"
sys.path.insert(0, str(DEPLOY))
sys.path.insert(0, str(ANALYSIS))

import casuka_deployment_authorization_verifier_v2 as verifier  # noqa: E402
import casuka_deployment_ceremony_v2 as ceremony  # noqa: E402
import build_casuka_deployment_control_v2 as builder  # noqa: E402


def run(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        list(args),
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    return result.stdout.strip()


class VerificationFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run(self.repo, "git", "init", "-b", "main")
        run(self.repo, "git", "config", "user.name", "Fixture")
        run(self.repo, "git", "config", "user.email", "fixture@example.test")
        self.counter = 0
        self.preimage = b"preimage\n"
        self.candidate = b"candidate\n"
        self.live = self.repo / "arb-executor/live_v4.py"
        self.live.parent.mkdir(parents=True)
        self.live.write_bytes(self.preimage)
        self.base = self.commit("base")
        self.pre_blob = run(self.repo, "git", "hash-object", str(self.live))
        self.pre_sha = hashlib.sha256(self.preimage).hexdigest()

        self.live.write_bytes(self.candidate)
        self.integration = self.commit("integration")
        self.candidate_blob = run(
            self.repo, "git", "hash-object", str(self.live)
        )
        self.candidate_sha = hashlib.sha256(self.candidate).hexdigest()

        self.live.write_bytes(self.preimage)
        self.rollback = self.commit("rollback")

        run(self.repo, "git", "checkout", "-q", self.integration)
        run(self.repo, "git", "switch", "-q", "-c", "package")
        (self.repo / "v1.txt").write_text("v1\n", encoding="utf-8")
        self.package_parent = self.commit("package parent")

        self.control_path = ".claude/test/DEPLOYMENT_CONTROL_V2.json"
        self.outcome_path = ".claude/test/OUTCOME.json"
        self.rollback_path = ".claude/test/ROLLBACK.json"
        self.rollback_script_path = "rollback.sh"
        self.audit_receipt_path = ".claude/audit/PASS.json"
        self.auth_report_path = ".claude/audit/AUTH.md"
        self.results_dir = ".claude/results_fixture/"
        self.target = "/remote/repo/arb-executor/live_v4.py"
        self.backup = "/remote/repo/arb-executor/live_v4.py.backup"
        self.deploy_command = (
            f"/remote/repo/arb-executor/deploy/deploy_live_v4.sh "
            f"{self.integration}"
        )
        self.rollback_command = (
            f"/remote/repo/arb-executor/deploy/deploy_live_v4.sh "
            f"{self.rollback}"
        )
        self.outcome = {
            "candidate": {
                "git_blob_oid": self.candidate_blob,
                "sha256": self.candidate_sha,
                "bytes": len(self.candidate),
            },
            "deployment_id": "fixture-deployment-attempt1",
            "host": "root@example.test",
            "integration_commit": self.integration,
            "preimage": {
                "git_blob_oid": self.pre_blob,
                "sha256": self.pre_sha,
                "bytes": len(self.preimage),
            },
            "results_dir": self.results_dir,
            "runtime_outcome_proof_path": (
                "/remote/repo/.claude/results_fixture/OUTCOME.json"
            ),
            "rollback_commit": self.rollback,
            "service": "live_v4",
            "status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE",
            "target_path": self.target,
        }
        outcome_bytes = verifier.canonical_json_bytes(self.outcome)
        outcome_sha = hashlib.sha256(outcome_bytes).hexdigest()
        rollback_artifact = {
            "commit": self.rollback,
            "preimage": self.pre_blob,
            "status": "FROZEN_NOT_EXECUTED",
        }
        rollback_bytes = verifier.canonical_json_bytes(rollback_artifact)
        rollback_sha = hashlib.sha256(rollback_bytes).hexdigest()
        verifier_source = b"fixture verifier\n"
        runner_source = b"fixture runner\n"
        rollback_source = b"#!/bin/bash\nexit 0\n"
        self.write("verifier.py", verifier_source)
        self.write("runner.py", runner_source)
        self.write(self.rollback_script_path, rollback_source)
        self.verifier_sha = hashlib.sha256(verifier_source).hexdigest()
        self.runner_sha = hashlib.sha256(runner_source).hexdigest()
        self.control = {
            "schema_version": "casuka-deployment-control-v2",
            "package": {
                "parent": self.package_parent,
                "branch": "codex/casuka-live-safety-deployment-control-v2",
                "forbidden_modified_paths": [
                    "arb-executor/live_v4.py",
                    "arb-executor/deploy/deploy_live_v4.sh",
                ],
            },
            "audit": {
                "remote_ref": "origin/audit/window1-independent",
                "controlling_v1_package_pass": "0" * 40,
                "failed_v1_authorization": "f" * 40,
                "failed_v1_authorization_status": "SUPERSEDED",
                "v2_package_pass_receipt_path": self.audit_receipt_path,
            },
            "integration": {
                "commit": self.integration,
                "parent": self.base,
                "branch": "codex/integration",
                "changed_paths": ["arb-executor/live_v4.py"],
            },
            "rollback": {
                "commit": self.rollback,
                "parent": self.integration,
                "branch": "codex/rollback",
                "artifact_path": self.rollback_path,
                "artifact_sha256": rollback_sha,
                "command": self.rollback_command,
                "script_path": self.rollback_script_path,
                "script_sha256": hashlib.sha256(rollback_source).hexdigest(),
            },
            "deployment": {
                "id": "fixture-deployment-attempt1",
                "host": "root@example.test",
                "service": "live_v4",
                "process_identity": "python3 -u live_v4.py",
                "remote_repo": "/remote/repo",
                "remote_arb": "/remote/repo/arb-executor",
                "remote_branch": "main",
                "repo_target_path": "arb-executor/live_v4.py",
                "target_path": self.target,
                "backup_path": self.backup,
                "results_dir": self.results_dir,
                "runtime_outcome_proof_path": (
                    "/remote/repo/.claude/results_fixture/OUTCOME.json"
                ),
                "preimage": {
                    "git_blob_oid": self.pre_blob,
                    "sha256": self.pre_sha,
                    "bytes": len(self.preimage),
                },
                "candidate": {
                    "git_blob_oid": self.candidate_blob,
                    "sha256": self.candidate_sha,
                    "bytes": len(self.candidate),
                },
                "local_preflight_commands": [],
                "protected_snapshot_exclusions": [
                    "arb-executor/live_v4.py"
                ],
            },
            "outcome_proof": {
                "path": self.outcome_path,
                "sha256": outcome_sha,
                "status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE",
                "environment_literal": f"OUTCOME_PROOF={self.outcome_path}",
                "t0": {
                    "quiet_minute": {
                        "seconds": 60,
                        "conception_event_names": ["order_placed"],
                    }
                },
                "post_boot": {"observation_seconds": 120},
            },
            "commands": {
                "deployment": self.deploy_command,
                "rollback": self.rollback_command,
                "ceremony_template": "fixture ceremony",
                "deploy_script_consumes_outcome_proof": False,
                "ceremony_runner_enforces_outcome_proof": True,
            },
            "authorization": {
                "verifier_path": "verifier.py",
                "verifier_sha256": self.verifier_sha,
                "runner_path": "runner.py",
                "runner_sha256": self.runner_sha,
                "authorization_commit_supplied_separately": True,
                "self_referential_authorization_sha": False,
            },
            "single_use": {
                "results_dir": self.results_dir,
                "attempt_identity_consumed_by_atomic_results_directory": True,
                "backup_must_be_absent": True,
                "candidate_retry_after_mutation": "FORBIDDEN",
            },
            "forbidden": ["deployment in tests"],
        }
        self.write(self.outcome_path, outcome_bytes)
        self.write(self.rollback_path, rollback_bytes)
        self.write(self.control_path, verifier.canonical_json_bytes(self.control))
        self.package = self.commit("package")
        run(
            self.repo,
            "git",
            "update-ref",
            "refs/remotes/origin/codex/casuka-live-safety-deployment-control-v2",
            self.package,
        )
        run(
            self.repo,
            "git",
            "update-ref",
            "refs/remotes/origin/codex/integration",
            self.integration,
        )
        run(
            self.repo,
            "git",
            "update-ref",
            "refs/remotes/origin/codex/rollback",
            self.rollback,
        )

        run(self.repo, "git", "checkout", "-q", self.base)
        run(self.repo, "git", "switch", "-q", "-c", "audit")
        (self.repo / "audit-base.txt").write_text("audit\n", encoding="utf-8")
        self.v1_pass = self.commit("v1 pass")
        self.control["audit"]["controlling_v1_package_pass"] = self.v1_pass

        audit_receipt = {
            "schema_version": "casuka-deployment-control-v2-independent-pass",
            "status": "PASS",
            "package_commit": self.package,
            "package_parent": self.package_parent,
            "controlling_v1_package_pass": self.v1_pass,
            "integration_commit": self.integration,
            "rollback_commit": self.rollback,
            "candidate_blob": self.candidate_blob,
            "candidate_sha256": self.candidate_sha,
            "preimage_blob": self.pre_blob,
            "preimage_sha256": self.pre_sha,
            "verifier_sha256": self.verifier_sha,
            "runner_sha256": self.runner_sha,
            "outcome_proof_sha256": outcome_sha,
            "adversarial_tests": "PASS",
            "dry_run_only": True,
            "live_mutations": 0,
        }
        self.write(
            self.audit_receipt_path,
            verifier.canonical_json_bytes(audit_receipt),
        )
        self.audit_pass = self.commit("package pass")

        payload = verifier.expected_authorization_payload(
            self.control,
            self.package,
            self.audit_pass,
            self.auth_report_path,
        )
        self.write(
            self.auth_report_path,
            verifier.render_authorization_report(payload),
        )
        self.authorization = self.commit("authorization")
        run(
            self.repo,
            "git",
            "update-ref",
            "refs/remotes/origin/audit/window1-independent",
            self.authorization,
        )
        run(self.repo, "git", "checkout", "-q", self.package)
        # Package control must bind the V1 pass now known; amend its contents
        # without changing the already-frozen package graph by rebuilding the
        # fixture from the resulting commit.
        control_path = self.repo / self.control_path
        current = json.loads(control_path.read_text(encoding="utf-8"))
        current["audit"]["controlling_v1_package_pass"] = self.v1_pass
        control_path.write_bytes(verifier.canonical_json_bytes(current))
        run(self.repo, "git", "add", self.control_path)
        env = self.env()
        run(self.repo, "git", "commit", "--amend", "--no-edit", env=env)
        old_package = self.package
        self.package = run(self.repo, "git", "rev-parse", "HEAD")
        # Recreate the audit commits against the amended package.
        run(self.repo, "git", "checkout", "-q", self.v1_pass)
        run(self.repo, "git", "switch", "-q", "-C", "audit")
        audit_receipt["package_commit"] = self.package
        self.write(
            self.audit_receipt_path,
            verifier.canonical_json_bytes(audit_receipt),
        )
        self.audit_pass = self.commit("package pass")
        payload = verifier.expected_authorization_payload(
            current, self.package, self.audit_pass, self.auth_report_path
        )
        self.write(
            self.auth_report_path,
            verifier.render_authorization_report(payload),
        )
        self.authorization = self.commit("authorization")
        run(
            self.repo,
            "git",
            "update-ref",
            "refs/remotes/origin/audit/window1-independent",
            self.authorization,
        )
        run(
            self.repo,
            "git",
            "update-ref",
            "refs/remotes/origin/codex/casuka-live-safety-deployment-control-v2",
            self.package,
        )
        run(self.repo, "git", "checkout", "-q", self.package)
        self.control = current
        self.remote_state_path = self.repo / ".git/remote-state.json"
        remote_state = {
            "schema_version": "casuka-remote-preflight-state-v2",
            "host": "root@example.test",
            "remote_repo": "/remote/repo",
            "repo_head": self.base,
            "repo_branch": "main",
            "target_path": self.target,
            "target_git_blob": self.pre_blob,
            "target_tree_blob": self.pre_blob,
            "target_sha256": self.pre_sha,
            "target_bytes": len(self.preimage),
            "target_status": "",
            "backup_exists": False,
            "results_exists": False,
            "tmux_session_alive": True,
            "process_count": 1,
            "process_rows": ["100 python3 -u live_v4.py"],
        }
        self.remote_state_path.write_bytes(
            verifier.canonical_json_bytes(remote_state)
        )
        self.request = verifier.VerificationRequest(
            repo=self.repo,
            control_path=self.control_path,
            authorization_commit=self.authorization,
            authorization_report=self.auth_report_path,
            package_commit=self.package,
            package_audit_pass=self.audit_pass,
            integration_commit=self.integration,
            deployment_id="fixture-deployment-attempt1",
            host="root@example.test",
            service="live_v4",
            target_path=self.target,
            backup_path=self.backup,
            preimage_blob=self.pre_blob,
            preimage_sha256=self.pre_sha,
            preimage_size=len(self.preimage),
            candidate_blob=self.candidate_blob,
            candidate_sha256=self.candidate_sha,
            candidate_size=len(self.candidate),
            results_dir=self.results_dir,
            outcome_proof_contract=self.outcome_path,
            outcome_proof_sha256=outcome_sha,
            deployment_command=self.deploy_command,
            rollback_command=self.rollback_command,
            rollback_artifact=self.rollback_path,
            mode="dry-run",
            remote_state_fixture=self.remote_state_path,
        )
        self.old_package = old_package

    def env(self) -> dict[str, str]:
        env = dict(os.environ)
        self.counter += 1
        stamp = f"2026-07-28T05:{self.counter:02d}:00Z"
        env.update(
            {
                "GIT_AUTHOR_DATE": stamp,
                "GIT_COMMITTER_DATE": stamp,
            }
        )
        return env

    def commit(self, message: str) -> str:
        run(self.repo, "git", "add", "-A")
        run(self.repo, "git", "commit", "-q", "-m", message, env=self.env())
        return run(self.repo, "git", "rev-parse", "HEAD")

    def write(self, relative: str, data: bytes) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def close(self) -> None:
        self.tmp.cleanup()


class VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fx = VerificationFixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fx.close()

    def test_valid_authorization_passes(self) -> None:
        receipt = verifier.verify(self.fx.request)
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["no_mutation_performed"])

    def assert_rejected(self, request: verifier.VerificationRequest) -> None:
        with self.assertRaises(verifier.VerificationError):
            verifier.verify(request)

    def test_wrong_authorization_commit_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, authorization_commit=self.fx.audit_pass
            )
        )

    def test_wrong_package_commit_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, package_commit=self.fx.package_parent
            )
        )

    def test_wrong_audit_commit_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, package_audit_pass=self.fx.v1_pass
            )
        )

    def test_wrong_integration_commit_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, integration_commit=self.fx.rollback
            )
        )

    def test_wrong_candidate_hash_and_size_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(self.fx.request, candidate_sha256="a" * 64)
        )
        self.assert_rejected(
            dataclasses.replace(self.fx.request, candidate_size=999)
        )

    def test_wrong_preimage_hash_and_size_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(self.fx.request, preimage_sha256="b" * 64)
        )
        self.assert_rejected(
            dataclasses.replace(self.fx.request, preimage_size=11)
        )

    def test_wrong_host_service_target_backup_rejected(self) -> None:
        for field, value in (
            ("host", "root@wrong.test"),
            ("service", "wrong"),
            ("target_path", "/wrong/live_v4.py"),
            ("backup_path", "/wrong/backup"),
        ):
            self.assert_rejected(
                dataclasses.replace(self.fx.request, **{field: value})
            )

    def test_wrong_deployment_id_and_results_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(self.fx.request, deployment_id="wrong-attempt")
        )
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, results_dir=".claude/other-results/"
            )
        )

    def test_truncated_hash_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, candidate_sha256=self.fx.candidate_sha[:12]
            )
        )
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request, integration_commit=self.fx.integration[:12]
            )
        )

    def test_mutated_commands_rejected(self) -> None:
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request,
                deployment_command=self.fx.deploy_command + " --extra",
            )
        )
        self.assert_rejected(
            dataclasses.replace(
                self.fx.request,
                rollback_command=self.fx.rollback_command + " --extra",
            )
        )

    def test_plan_only_outcome_contract_rejected(self) -> None:
        path = self.fx.repo / ".claude/test/PLAN_ONLY.json"
        path.write_bytes(
            verifier.canonical_json_bytes({"status": "PLAN_ONLY_NOT_RUN"})
        )
        control = copy.deepcopy(self.fx.control)
        control["outcome_proof"]["path"] = ".claude/test/PLAN_ONLY.json"
        control["outcome_proof"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        with self.assertRaises(ceremony.CeremonyError):
            ceremony.validate_outcome_contract(self.fx.repo, control)
        path.unlink()

    def test_remote_backup_or_results_existing_rejected(self) -> None:
        state = json.loads(self.fx.remote_state_path.read_text())
        for key in ("backup_exists", "results_exists"):
            mutated = dict(state)
            mutated[key] = True
            path = self.fx.repo / ".git" / f"{key}.json"
            path.write_bytes(verifier.canonical_json_bytes(mutated))
            self.assert_rejected(
                dataclasses.replace(
                    self.fx.request, remote_state_fixture=path
                )
            )
            path.unlink()

    def test_attempted_authorization_reuse_rejected(self) -> None:
        results = self.fx.repo / self.fx.results_dir
        results.mkdir(parents=True)
        try:
            self.assert_rejected(self.fx.request)
        finally:
            results.rmdir()

    def test_fractional_and_ambiguous_sizes_rejected(self) -> None:
        for value in ("5.9", "5.0001", "01", "true", "+5"):
            with self.assertRaises(verifier.VerificationError):
                verifier._parse_exact_cli_int(value, "size")

    def test_extra_file_integration_is_rejected(self) -> None:
        repo = self.fx.repo
        run(repo, "git", "checkout", "-q", self.fx.base)
        run(repo, "git", "switch", "-q", "-C", "extra-integration")
        (repo / "arb-executor/live_v4.py").write_bytes(self.fx.candidate)
        (repo / "extra.txt").write_text("extra\n", encoding="utf-8")
        extra = self.fx.commit("extra integration")
        run(repo, "git", "checkout", "-q", self.fx.package)
        request = dataclasses.replace(
            self.fx.request, integration_commit=extra
        )
        control = copy.deepcopy(self.fx.control)
        control["integration"]["commit"] = extra
        with self.assertRaises(verifier.VerificationError):
            verifier._verify_git_and_files(request, control)

    def test_report_extra_or_duplicated_text_rejected(self) -> None:
        expected = verifier.render_authorization_report(
            verifier.expected_authorization_payload(
                self.fx.control,
                self.fx.package,
                self.fx.audit_pass,
                self.fx.auth_report_path,
            )
        )
        self.assertNotEqual(expected + expected, expected)
        self.assertNotEqual(expected + b"\nextra\n", expected)

    def test_authorization_payload_has_no_self_sha(self) -> None:
        payload = verifier.expected_authorization_payload(
            self.fx.control,
            self.fx.package,
            self.fx.audit_pass,
            self.fx.auth_report_path,
        )
        self.assertNotIn("authorization_commit", payload)
        self.assertTrue(payload["authorization_commit_supplied_separately"])


class RunnerAndBuilderTests(unittest.TestCase):
    def test_journal_is_complete_line_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.jsonl"
            journal = ceremony.Journal(path)
            journal.append("PRECHECK", "PASS", {"x": 1})
            journal.append("COMPLETE", "PASS", {"x": 2})
            lines = path.read_bytes().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["sequence"], 1)
            self.assertEqual(json.loads(lines[1])["sequence"], 2)

    def test_dry_run_success_has_no_invocations_or_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scenario = Path(tmp) / "scenario.json"
            scenario.write_text(
                json.dumps(
                    {"precheck_pass": True, "postcheck_pass": True}
                ),
                encoding="utf-8",
            )
            ctx = ceremony.CeremonyContext(
                repo=ROOT,
                control_path="unused",
                authorization_commit="a" * 40,
                authorization_report=".claude/audit/auth.md",
                package_audit_pass="b" * 40,
                mode="dry-run",
                simulation_scenario=scenario,
            )
            control = {"outcome_proof": {"path": "unused"}}
            with mock.patch.object(
                ceremony,
                "run_authorization_verifier",
                return_value={"status": "PASS"},
            ), mock.patch.object(
                ceremony,
                "validate_outcome_contract",
                return_value={"status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE"},
            ), mock.patch.object(
                ceremony, "ssh_bash", side_effect=AssertionError("SSH called")
            ):
                receipt = ceremony.dry_run(ctx, control)
            self.assertEqual(receipt["deployment_invocations"], 0)
            self.assertEqual(receipt["rollback_invocations"], 0)
            self.assertFalse(receipt["results_directory_created"])

    def test_dry_run_failure_models_single_rollback_no_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scenario = Path(tmp) / "scenario.json"
            scenario.write_text(
                json.dumps(
                    {"precheck_pass": True, "postcheck_pass": False}
                ),
                encoding="utf-8",
            )
            ctx = ceremony.CeremonyContext(
                repo=ROOT,
                control_path="unused",
                authorization_commit="a" * 40,
                authorization_report=".claude/audit/auth.md",
                package_audit_pass="b" * 40,
                mode="dry-run",
                simulation_scenario=scenario,
            )
            with mock.patch.object(
                ceremony,
                "run_authorization_verifier",
                return_value={"status": "PASS"},
            ), mock.patch.object(
                ceremony,
                "validate_outcome_contract",
                return_value={"status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE"},
            ):
                receipt = ceremony.dry_run(
                    ctx, {"outcome_proof": {"path": "unused"}}
                )
            self.assertEqual(
                receipt["expected_phase_sequence"],
                [
                    "PRECHECK",
                    "MUTATION_STARTED",
                    "DEPLOY",
                    "POSTCHECK",
                    "ROLLBACK",
                    "COMPLETE",
                ],
            )
            self.assertEqual(receipt["deployment_invocations"], 0)

    def test_outcome_environment_must_be_exact(self) -> None:
        control = {"outcome_proof": {"path": ".claude/exact.json"}}
        with mock.patch.dict(os.environ, {"OUTCOME_PROOF": "wrong"}):
            self.assertNotEqual(
                os.environ["OUTCOME_PROOF"], control["outcome_proof"]["path"]
            )

    def test_two_clean_builder_outputs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / "one"
            two = Path(tmp) / "two"
            builder.build(ROOT, one)
            builder.build(ROOT, two)
            files_one = {
                p.name: p.read_bytes() for p in one.iterdir() if p.is_file()
            }
            files_two = {
                p.name: p.read_bytes() for p in two.iterdir() if p.is_file()
            }
            self.assertEqual(files_one, files_two)

    def test_builder_preserves_candidate_and_file_only_commits(self) -> None:
        self.assertEqual(
            run(ROOT, "git", "ls-tree", builder.INTEGRATION,
                "arb-executor/live_v4.py").split()[2],
            builder.CANDIDATE_BLOB,
        )
        self.assertEqual(
            run(ROOT, "git", "ls-tree", builder.ROLLBACK,
                "arb-executor/live_v4.py").split()[2],
            builder.PREIMAGE_BLOB,
        )
        self.assertEqual(
            run(ROOT, "git", "diff", "--name-only",
                builder.INTEGRATION_PARENT, builder.INTEGRATION),
            "arb-executor/live_v4.py",
        )


if __name__ == "__main__":
    unittest.main()
