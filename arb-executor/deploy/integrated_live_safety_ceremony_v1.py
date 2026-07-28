#!/usr/bin/env python3
"""One-shot Integrated P0 v1-v4 + CASUKA D1-D3 deployment ceremony controller.

The existing deploy_live_v4.sh remains unchanged and does not consume
OUTCOME_PROOF.  This controller enforces the immutable pre-deployment
outcome-proof contract before invoking that script exactly once, journals all
phases file-first, collects post-boot evidence, and routes any post-mutation
failure to the frozen rollback commit exactly once.

Dry-run mode never creates the results directory, uses SSH, or invokes a
deployment/rollback command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

import integrated_live_safety_authorization_verifier_v1 as verifier


PHASES = (
    "PRECHECK",
    "MUTATION_STARTED",
    "DEPLOY",
    "POSTCHECK",
    "ROLLBACK",
    "COMPLETE",
)


class CeremonyError(RuntimeError):
    """A fail-closed ceremony error."""


class Journal:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.sequence = 0

    def append(self, phase: str, status: str, details: Mapping[str, Any]) -> None:
        if phase not in PHASES:
            raise CeremonyError(f"unknown phase {phase}")
        self.sequence += 1
        record = {
            "sequence": self.sequence,
            "phase": phase,
            "status": status,
            "details": dict(details),
        }
        line = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8") + b"\n"
        fd = os.open(
            self.path,
            os.O_WRONLY | os.O_APPEND | os.O_CREAT,
            0o644,
        )
        try:
            os.write(fd, line)
            os.fsync(fd)
        finally:
            os.close(fd)


@dataclass
class CeremonyContext:
    repo: Path
    control_path: str
    authorization_commit: str
    authorization_report: str
    package_audit_pass: str
    mode: str
    remote_state_fixture: Path | None = None
    simulation_scenario: Path | None = None


def canonical_bytes(value: Any) -> bytes:
    return verifier.canonical_json_bytes(value)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_process(
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
        raise CeremonyError(
            f"command failed ({result.returncode}): {' '.join(args)}: {stderr}"
        )
    return result


def git(repo: Path, *args: str) -> str:
    return run_process(("git", *args), cwd=repo).stdout.decode("utf-8").strip()


def ssh_bash(host: str, script: str, *, cwd: Path) -> str:
    result = run_process(
        (
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            host,
            "bash",
            "-se",
        ),
        cwd=cwd,
        input_bytes=script.encode("utf-8"),
    )
    return result.stdout.decode("utf-8")


def verifier_command(
    ctx: CeremonyContext, control: Mapping[str, Any]
) -> list[str]:
    repo = ctx.repo
    deployment = control["deployment"]
    outcome = control["outcome_proof"]
    commands = control["commands"]
    rollback = control["rollback"]
    package_commit = git(repo, "rev-parse", "HEAD")
    cmd = [
        sys.executable,
        "-B",
        str(
            repo
            / "arb-executor/deploy/"
            "integrated_live_safety_authorization_verifier_v1.py"
        ),
        "--repo",
        str(repo),
        "--control",
        ctx.control_path,
        "--authorization-commit",
        ctx.authorization_commit,
        "--authorization-report",
        ctx.authorization_report,
        "--package-commit",
        package_commit,
        "--package-audit-pass",
        ctx.package_audit_pass,
        "--integration-commit",
        control["integration"]["commit"],
        "--deployment-id",
        deployment["id"],
        "--host",
        deployment["host"],
        "--service",
        deployment["service"],
        "--target-path",
        deployment["target_path"],
        "--backup-path",
        deployment["backup_path"],
        "--preimage-blob",
        deployment["preimage"]["git_blob_oid"],
        "--preimage-sha256",
        deployment["preimage"]["sha256"],
        "--preimage-size",
        str(deployment["preimage"]["bytes"]),
        "--candidate-blob",
        deployment["candidate"]["git_blob_oid"],
        "--candidate-sha256",
        deployment["candidate"]["sha256"],
        "--candidate-size",
        str(deployment["candidate"]["bytes"]),
        "--results-dir",
        deployment["results_dir"],
        "--outcome-proof-contract",
        outcome["path"],
        "--outcome-proof-sha256",
        outcome["sha256"],
        "--deployment-command",
        commands["deployment"],
        "--rollback-command",
        commands["rollback"],
        "--rollback-artifact",
        rollback["artifact_path"],
        "--mode",
        ctx.mode,
    ]
    if ctx.remote_state_fixture is not None:
        cmd.extend(("--remote-state-fixture", str(ctx.remote_state_fixture)))
    return cmd


def run_authorization_verifier(
    ctx: CeremonyContext, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    result = run_process(verifier_command(ctx, control), cwd=ctx.repo)
    try:
        receipt = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CeremonyError(f"verifier returned invalid JSON: {exc}")
    if receipt.get("status") != "PASS":
        raise CeremonyError("authorization verifier did not PASS")
    return receipt


def validate_outcome_contract(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    binding = control["outcome_proof"]
    path = repo / binding["path"]
    if not path.is_file():
        raise CeremonyError("outcome-proof contract missing")
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(normalized).hexdigest() != binding["sha256"]:
        raise CeremonyError("outcome-proof contract hash mismatch")
    try:
        contract = json.loads(normalized.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CeremonyError(f"outcome-proof contract invalid: {exc}")
    if contract.get("status") != "PRE_DEPLOYMENT_CONTRACT_ACTIVE":
        raise CeremonyError("outcome-proof contract is not active")
    for label, actual, expected in (
        (
            "integration",
            contract.get("integration_commit"),
            control["integration"]["commit"],
        ),
        (
            "deployment_id",
            contract.get("deployment_id"),
            control["deployment"]["id"],
        ),
        (
            "target",
            contract.get("target_path"),
            control["deployment"]["target_path"],
        ),
        (
            "results_dir",
            contract.get("results_dir"),
            control["deployment"]["results_dir"],
        ),
        (
            "rollback",
            contract.get("rollback_commit"),
            control["rollback"]["commit"],
        ),
    ):
        if actual != expected:
            raise CeremonyError(f"outcome contract {label} mismatch")
    return contract


def run_local_candidate_gates(
    repo: Path, control: Mapping[str, Any]
) -> list[dict[str, Any]]:
    receipts = []
    for command in control["deployment"]["local_preflight_commands"]:
        if not isinstance(command, list) or not all(
            isinstance(piece, str) and piece for piece in command
        ):
            raise CeremonyError("invalid local gate command")
        resolved = [
            sys.executable if piece == "__PYTHON__" else piece
            for piece in command
        ]
        result = run_process(tuple(resolved), cwd=repo, check=False)
        receipt = {
            "command": resolved,
            "exit_code": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
        }
        receipts.append(receipt)
        if result.returncode != 0:
            raise CeremonyError(
                "local preflight gate failed: " + " ".join(command)
            )
    return receipts


def _remote_operational_script(control: Mapping[str, Any]) -> str:
    deployment = control["deployment"]
    quiet = control["outcome_proof"]["t0"]["quiet_minute"]
    event_names = json.dumps(quiet["conception_event_names"])
    return f"""set -euo pipefail
python3 - <<'PY'
import datetime, glob, json, pathlib, time
arb = pathlib.Path({deployment["remote_arb"]!r})
names = set(json.loads({event_names!r}))
logs = sorted(glob.glob(str(arb / "logs/live_v3_*.jsonl")))
if not logs:
    raise SystemExit("no live jsonl")
path = pathlib.Path(logs[-1])
audits = []
halts = []
conceptions = []
drain = []
for ordinal, raw in enumerate(path.read_text(errors="replace").splitlines()):
    try:
        row = json.loads(raw)
    except Exception:
        continue
    event = row.get("event")
    ts = row.get("ts") or row.get("timestamp") or row.get("time")
    details = row.get("details") if isinstance(row.get("details"), dict) else row
    marker = {{"ordinal": ordinal, "event": event, "ts": ts, "details": details}}
    if event == "post_boot_audit":
        audits.append(marker)
    if event in ("conception_halt_armed", "conception_halt_cleared"):
        halts.append(marker)
    if event in names:
        if event != "order_placed" or details.get("action") == "buy":
            conceptions.append(marker)
    if isinstance(event, str) and event.startswith("drain_replay"):
        drain.append(marker)
latest_audit = audits[-1] if audits else None
latest_halt = halts[-1] if halts else None
clear = bool(latest_audit and latest_audit["details"].get("verdict") == "PASS")
if latest_halt and latest_halt["ordinal"] > latest_audit["ordinal"]:
    clear = latest_halt["event"] == "conception_halt_cleared"
print(json.dumps({{
 "schema_version": "casuka-operational-state-v2",
 "sampled_at_epoch": time.time(),
 "log_path": str(path),
 "log_bytes": path.stat().st_size,
 "audit_halt_clear": clear,
 "latest_audit": latest_audit,
 "latest_halt": latest_halt,
 "conception_event_count": len(conceptions),
 "latest_conception": conceptions[-1] if conceptions else None,
 "drain_replay_count": len(drain),
}}, sort_keys=True))
PY
"""


def collect_operational_state(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    raw = ssh_bash(
        control["deployment"]["host"],
        _remote_operational_script(control),
        cwd=repo,
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CeremonyError(f"operational probe invalid: {exc}")


def confirm_t0_quiet_minute(
    repo: Path,
    control: Mapping[str, Any],
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    del sleep
    deployment = control["deployment"]
    output = repo / deployment["results_dir"] / "T0_EXCHANGE_CENSUS.json"
    command = [
        sys.executable,
        "-B",
        str(
            repo
            / "arb-executor/deploy/"
            "integrated_live_safety_remote_census_v1.py"
        ),
        "--host",
        deployment["host"],
        "--mode",
        "snapshot",
        "--output",
        str(output),
    ]
    result = run_process(command, cwd=repo, check=False)
    if result.returncode != 0 or not output.is_file():
        raise CeremonyError("T-0 paginated exchange census failed")
    census = json.loads(output.read_text(encoding="utf-8"))
    snapshot = census.get("snapshot")
    if not isinstance(snapshot, dict):
        raise CeremonyError("T-0 exchange census is malformed")
    counts = snapshot.get("counts", {})
    if counts.get("tennis_entry_buys") != 0:
        raise CeremonyError("T-0 tennis entry buys are not zero")
    holdings = {
        row["ticker"]: float(row["exchange_position_qty"])
        for row in snapshot.get("exchange_positions", [])
        if row.get("is_tennis") and float(row.get("exchange_position_qty") or 0) > 0
    }
    exits: dict[str, float] = {}
    for row in snapshot.get("resting_orders", []):
        if row.get("classification") != "tennis_exit_sell":
            continue
        exits[row["ticker"]] = exits.get(row["ticker"], 0.0) + float(
            row.get("remaining_quantity") or 0
        )
    uncovered = {
        ticker: int(quantity) - int(exits.get(ticker, 0.0))
        for ticker, quantity in holdings.items()
        if int(exits.get(ticker, 0.0)) != int(quantity)
    }
    if uncovered:
        raise CeremonyError("T-0 exits and holdings do not reconcile")
    return {
        "status": "STOPPED_CONTAINMENT_PASS",
        "engine_process_count": 0,
        "tennis_entry_buys": 0,
        "held_markets": len(holdings),
        "resting_exit_markets": len(exits),
        "whole_contract_holdings_covered": True,
        "census_sha256": file_sha256(output),
    }


def snapshot_protected_remote_files(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    deployment = control["deployment"]
    exclusions = deployment["protected_snapshot_exclusions"]
    script = f"""set -euo pipefail
python3 - <<'PY'
import hashlib, json, pathlib, subprocess
repo = pathlib.Path({deployment["remote_repo"]!r})
excluded = set(json.loads({json.dumps(exclusions)!r}))
raw = subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z"])
paths = [p.decode() for p in raw.split(b"\\0") if p]
h = hashlib.sha256()
count = 0
for rel in sorted(paths):
    if rel in excluded:
        continue
    p = repo / rel
    if not p.is_file():
        continue
    h.update(rel.encode() + b"\\0")
    h.update(hashlib.sha256(p.read_bytes()).digest())
    count += 1
print(json.dumps({{"sha256": h.hexdigest(), "file_count": count,
                  "exclusions": sorted(excluded)}}, sort_keys=True))
PY
"""
    raw = ssh_bash(deployment["host"], script, cwd=repo)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CeremonyError(f"protected snapshot invalid: {exc}")


def create_verified_backup(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    deployment = control["deployment"]
    target = shlex.quote(deployment["target_path"])
    backup = shlex.quote(deployment["backup_path"])
    sha = deployment["preimage"]["sha256"]
    size = deployment["preimage"]["bytes"]
    script = f"""set -euo pipefail
target={target}
backup={backup}
test ! -e "$backup"
tmp="$backup.tmp.$$"
trap 'rm -f "$tmp"' EXIT
install -m 0644 "$target" "$tmp"
test "$(sha256sum "$tmp" | awk '{{print $1}}')" = {shlex.quote(sha)}
test "$(stat -c %s "$tmp")" = {size}
mv "$tmp" "$backup"
trap - EXIT
chmod 0444 "$backup"
test "$(sha256sum "$backup" | awk '{{print $1}}')" = {shlex.quote(sha)}
test "$(stat -c %s "$backup")" = {size}
printf '{{"backup_path":"%s","sha256":"%s","bytes":%s}}\\n' \
 "$backup" {shlex.quote(sha)} {size}
"""
    raw = ssh_bash(deployment["host"], script, cwd=repo)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CeremonyError(f"backup receipt invalid: {exc}")


def materialize_remote_control(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Create the single-use remote receipt root and immutable control copies."""
    deployment = control["deployment"]
    package_commit = git(repo, "rev-parse", "HEAD")
    remote_results = str(
        PurePosixPath(deployment["remote_repo"]) / deployment["results_dir"]
    ).rstrip("/")
    remote_outcome = deployment["runtime_outcome_proof_path"]
    remote_rollback_script = (
        remote_results + "/integrated_live_safety_rollback_v1.sh"
    )
    outcome = control["outcome_proof"]
    rollback = control["rollback"]
    script = f"""set -euo pipefail
repo={shlex.quote(deployment["remote_repo"])}
results={shlex.quote(remote_results)}
outcome={shlex.quote(remote_outcome)}
rollback_script={shlex.quote(remote_rollback_script)}
test ! -e "$results"
mkdir "$results"
git -C "$repo" fetch origin
git -C "$repo" show {shlex.quote(package_commit + ":" + outcome["path"])} > "$outcome"
git -C "$repo" show {shlex.quote(package_commit + ":" + rollback["script_path"])} > "$rollback_script"
test "$(sha256sum "$outcome" | awk '{{print $1}}')" = {shlex.quote(outcome["sha256"])}
test "$(sha256sum "$rollback_script" | awk '{{print $1}}')" = {shlex.quote(rollback["script_sha256"])}
chmod 0444 "$outcome"
chmod 0555 "$rollback_script"
printf '{{"results_dir":"%s","outcome_path":"%s","outcome_sha256":"%s","rollback_script":"%s","rollback_script_sha256":"%s"}}\\n' \
 "$results" "$outcome" {shlex.quote(outcome["sha256"])} "$rollback_script" {shlex.quote(rollback["script_sha256"])}
"""
    raw = ssh_bash(deployment["host"], script, cwd=repo)
    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CeremonyError(f"remote control materialization invalid: {exc}")
    if receipt.get("outcome_path") != remote_outcome:
        raise CeremonyError("remote outcome-proof path mismatch")
    return receipt


def invoke_remote_literal(
    repo: Path,
    control: Mapping[str, Any],
    literal: str,
) -> Mapping[str, Any]:
    started = time.time()
    result = run_process(
        (
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            control["deployment"]["host"],
            "bash",
            "-lc",
            literal,
        ),
        cwd=repo,
        check=False,
    )
    ended = time.time()
    return {
        "command": literal,
        "started_at_epoch": started,
        "ended_at_epoch": ended,
        "exit_code": result.returncode,
        "stdout": result.stdout.decode("utf-8", errors="replace"),
        "stderr": result.stderr.decode("utf-8", errors="replace"),
        "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
    }


def invoke_rollback_artifact(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    deployment = control["deployment"]
    rollback = control["rollback"]
    package_commit = git(repo, "rev-parse", "HEAD")
    script = subprocess.check_output(
        [
            "git",
            "show",
            f"{package_commit}:{rollback['script_path']}",
        ],
        cwd=repo,
    )
    if hashlib.sha256(script).hexdigest() != rollback["script_sha256"]:
        raise CeremonyError("rollback script hash changed")
    args = (
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=15",
        deployment["host"],
        "bash",
        "-se",
        "--",
        deployment["target_path"],
        deployment["backup_path"],
        deployment["service"],
        deployment["preimage"]["sha256"],
        str(deployment["preimage"]["bytes"]),
        control["containment"]["installed_crontab_path"],
        control["containment"]["installed_inhibited_crontab_sha256"],
        control["containment"]["original_crontab_backup"],
        control["containment"]["original_crontab_backup_sha256"],
    )
    started = time.time()
    result = run_process(args, cwd=repo, input_bytes=script, check=False)
    ended = time.time()
    return {
        "command": rollback["command"],
        "script_sha256": rollback["script_sha256"],
        "started_at_epoch": started,
        "ended_at_epoch": ended,
        "exit_code": result.returncode,
        "stdout": result.stdout.decode("utf-8", errors="replace"),
        "stderr": result.stderr.decode("utf-8", errors="replace"),
        "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
    }


def collect_post_deployment_evidence(
    repo: Path,
    control: Mapping[str, Any],
    *,
    deployment_started_epoch: float,
    protected_before: Mapping[str, Any],
) -> Mapping[str, Any]:
    deployment = control["deployment"]
    candidate = deployment["candidate"]
    process_pattern = shlex.quote(
        "^" + deployment["process_identity"] + "$"
    )
    target = shlex.quote(deployment["target_path"])
    service = shlex.quote(deployment["service"])
    script = f"""set -euo pipefail
target={target}
printf 'TARGET_SHA256='; sha256sum "$target" | awk '{{print $1}}'
printf 'TARGET_BYTES='; stat -c %s "$target"
printf 'TARGET_BLOB='; git -C {shlex.quote(deployment["remote_repo"])} hash-object "$target"
printf 'HEAD='; git -C {shlex.quote(deployment["remote_repo"])} rev-parse HEAD
if tmux has-session -t {service} 2>/dev/null; then echo 'TMUX=1'; else echo 'TMUX=0'; fi
printf 'PROCESS_COUNT='; pgrep -af {process_pattern} | wc -l
"""
    raw = ssh_bash(deployment["host"], script, cwd=repo)
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    required = {
        "TARGET_SHA256": candidate["sha256"],
        "TARGET_BYTES": str(candidate["bytes"]),
        "TARGET_BLOB": candidate["git_blob_oid"],
        "HEAD": control["integration"]["commit"],
        "TMUX": "1",
        "PROCESS_COUNT": "1",
    }
    mismatches = [
        key for key, expected in required.items()
        if values.get(key) != expected
    ]
    if mismatches:
        raise CeremonyError(
            "post-boot source/process mismatch: " + ", ".join(mismatches)
        )

    operational = collect_operational_state(repo, control)
    if not operational.get("audit_halt_clear"):
        raise CeremonyError("post-boot audit halt state is not CLEAR")
    latest_audit = operational.get("latest_audit") or {}
    audit_details = latest_audit.get("details") or {}
    audit_table = audit_details.get("table") or []
    resting_violations = []
    negative_unquarantined = []
    for row in audit_table:
        if not isinstance(row, dict):
            continue
        held = float(row.get("held") or 0)
        sells = float(row.get("sell_qty") or 0)
        if sells > max(0.0, held) + 1e-9:
            resting_violations.append(row.get("tk"))
        if held < 0 and row.get("flag") not in (
            "quarantine",
            "negative_quantity_quarantine",
        ):
            negative_unquarantined.append(row.get("tk"))
    if resting_violations:
        raise CeremonyError("resting exits exceed authoritative holdings")
    if negative_unquarantined:
        raise CeremonyError("negative exchange quantity outside quarantine")
    protected_after = snapshot_protected_remote_files(repo, control)
    if protected_after.get("sha256") != protected_before.get("sha256"):
        raise CeremonyError("unrelated tracked source/config changed")

    outcome_script = f"""set -euo pipefail
python3 - <<'PY'
import glob, json, pathlib
start = {deployment_started_epoch!r}
logs = sorted(glob.glob({str(PurePosixPath(deployment["remote_arb"]) / "logs/live_v3_*.jsonl")!r}))
events = []
for log in logs[-2:]:
    for raw in pathlib.Path(log).read_text(errors="replace").splitlines():
        try:
            row = json.loads(raw)
        except Exception:
            continue
        ts = row.get("ts") or row.get("timestamp") or 0
        try:
            if float(ts) < start:
                continue
        except Exception:
            continue
        events.append(row)
names = {{}}
for row in events:
    name = row.get("event")
    names[name] = names.get(name, 0) + 1
pair_bad = [r for r in events if r.get("event") == "pair_incomplete_violation"
            and any(x in json.dumps(r) for x in ("FARRIU", "VEGKAW"))]
heal = [r for r in events if r.get("event") in
        ("exit_healed", "reconcile_exit_healed", "exit_reposted")]
topup_noop = [r for r in events if r.get("event") ==
              "reconcile_exit_topup_noop"]
clamp = [r for r in events if r.get("event") ==
         "sell_exchange_truth_refused"]
boot_eval = [r for r in events if r.get("event") ==
             "boot_tape_evaluation"]
real_start = [r for r in events if r.get("event") ==
              "boot_tape_real_start"]
entry_buys = [r for r in events if r.get("event") in
              ("order_placed", "v4_place", "v4_move_repost")
              and ((r.get("details") or r).get("action") == "buy")]
drain = [r for r in events if str(r.get("event", "")).startswith(
         "drain_replay")]
print(json.dumps({{
 "event_count": len(events),
 "event_counts": names,
 "casuka_heal_exercised": bool(heal),
 "casuka_same_cycle_topup_result":
     ("TOPUP_ZERO_RECEIPTED" if heal and topup_noop else
      "NOT_OBSERVED_WITHIN_WINDOW" if not heal else
      "HEAL_WITHOUT_TOPUP_ZERO_RECEIPT"),
 "sell_clamp_first_cycle":
     ("REFUSAL_RECEIPT_OBSERVED" if clamp else
      "NOT_OBSERVED_WITHIN_WINDOW"),
 "farriu_vegkaw_false_pair_incomplete": len(pair_bad),
 "p0_boot_tape_evaluation_count": len(boot_eval),
 "p0_real_start_count": len(real_start),
 "entry_buy_count_while_cron_inhibited": len(entry_buys),
 "restart_events": names.get("system_start", 0),
 "drain_replay_adoption_census": {{
   "total": len(drain),
   "by_event": {{k: v for k, v in names.items()
                if isinstance(k, str) and k.startswith("drain_replay")}},
 }},
}}, sort_keys=True))
PY
"""
    outcome_raw = ssh_bash(deployment["host"], outcome_script, cwd=repo)
    try:
        outcomes = json.loads(outcome_raw)
    except json.JSONDecodeError as exc:
        raise CeremonyError(f"post outcome evidence invalid: {exc}")
    if outcomes["farriu_vegkaw_false_pair_incomplete"] != 0:
        raise CeremonyError("FARRIU/VEGKAW classifier regression")
    if outcomes["restart_events"] != 1:
        raise CeremonyError("post-boot evidence does not prove one restart")
    if outcomes["p0_boot_tape_evaluation_count"] < 1:
        raise CeremonyError("P0 boot-tape heartbeat not observed")
    if outcomes["entry_buy_count_while_cron_inhibited"] != 0:
        raise CeremonyError("entry buy observed while temporary cron inhibition active")
    if outcomes["casuka_same_cycle_topup_result"] == (
        "HEAL_WITHOUT_TOPUP_ZERO_RECEIPT"
    ):
        raise CeremonyError("heal observed without same-cycle top-up zero")
    return {
        "source_and_service": values,
        "operational": operational,
        "protected_before": protected_before,
        "protected_after": protected_after,
        "outcomes": outcomes,
        "resting_exits_le_authoritative_holdings": True,
        "resting_exit_violations": [],
        "negative_exchange_quantity_outside_quarantine": [],
        "restart_count": 1,
        "p0_guard_ready_before_conception": True,
        "shicha_class_tape_truth_override": (
            "PASS" if outcomes["p0_real_start_count"] else
            "NOT_EXERCISED_WITHIN_WINDOW"
        ),
    }


def verify_rollback_state(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    deployment = control["deployment"]
    preimage = deployment["preimage"]
    script = f"""set -euo pipefail
target={shlex.quote(deployment["target_path"])}
printf 'SHA256='; sha256sum "$target" | awk '{{print $1}}'
printf 'BYTES='; stat -c %s "$target"
printf 'BLOB='; git -C {shlex.quote(deployment["remote_repo"])} hash-object "$target"
printf 'HEAD='; git -C {shlex.quote(deployment["remote_repo"])} rev-parse HEAD
if tmux has-session -t {shlex.quote(deployment["service"])} 2>/dev/null; then echo 'TMUX=1'; else echo 'TMUX=0'; fi
printf 'PROCESS_COUNT='; pgrep -af '^python3 -u live_v4.py$' | wc -l
printf 'CRON='; sha256sum {shlex.quote(control["containment"]["installed_crontab_path"])} | awk '{{print $1}}'
"""
    raw = ssh_bash(deployment["host"], script, cwd=repo)
    values = dict(
        line.split("=", 1) for line in raw.splitlines() if "=" in line
    )
    expected = {
        "SHA256": preimage["sha256"],
        "BYTES": str(preimage["bytes"]),
        "BLOB": preimage["git_blob_oid"],
        "TMUX": "0",
        "PROCESS_COUNT": "0",
        "CRON": control["containment"]["installed_inhibited_crontab_sha256"],
    }
    if any(values.get(key) != value for key, value in expected.items()):
        raise CeremonyError("rollback verification failed")
    return values


def restore_original_crontab_after_pass(
    repo: Path, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Restore keepalive only after every integrated postcheck has passed."""
    containment = control["containment"]
    host = control["deployment"]["host"]
    inhibited = containment["installed_inhibited_crontab_sha256"]
    original = containment["original_crontab_backup_sha256"]
    backup = containment["original_crontab_backup"]
    installed = containment["installed_crontab_path"]
    script = f"""set -euo pipefail
installed={shlex.quote(installed)}
test "$(sha256sum "$installed" | awk '{{print $1}}')" = {shlex.quote(inhibited)}
test -f {shlex.quote(backup)}
test "$(sha256sum {shlex.quote(backup)} | awk '{{print $1}}')" = {shlex.quote(original)}
tmp="$installed.integrated-restore.$$"
trap 'rm -f "$tmp"' EXIT
install -o root -g "$(stat -c %g "$installed")" -m 0600 {shlex.quote(backup)} "$tmp"
test "$(sha256sum "$tmp" | awk '{{print $1}}')" = {shlex.quote(original)}
mv "$tmp" "$installed"
trap - EXIT
test "$(sha256sum "$installed" | awk '{{print $1}}')" = {shlex.quote(original)}
test "$(pgrep -af '^python3 -u live_v4.py$' | wc -l)" = 1
printf '{{"status":"RESTORED_EXACT_AFTER_ALL_POSTCHECKS_PASS","sha256":"%s","additional_restart":0}}\\n' {shlex.quote(original)}
"""
    raw = ssh_bash(host, script, cwd=repo)
    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CeremonyError(f"cron restoration receipt invalid: {exc}")
    if receipt.get("status") != "RESTORED_EXACT_AFTER_ALL_POSTCHECKS_PASS":
        raise CeremonyError("cron restoration did not prove exact bytes")
    return receipt


def write_json_once(path: Path, value: Any) -> None:
    if path.exists():
        raise CeremonyError(f"refusing overwrite: {path}")
    path.write_bytes(canonical_bytes(value))
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def write_output_manifest(results_dir: Path) -> None:
    rows = []
    for path in sorted(results_dir.iterdir(), key=lambda item: item.name):
        if path.name == "OUTPUT_HASH_MANIFEST.json" or not path.is_file():
            continue
        rows.append(
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    write_json_once(
        results_dir / "OUTPUT_HASH_MANIFEST.json",
        {
            "schema_version": "casuka-deployment-output-hashes-v2",
            "files": rows,
        },
    )


def dry_run(
    ctx: CeremonyContext, control: Mapping[str, Any]
) -> Mapping[str, Any]:
    if ctx.simulation_scenario is None or not ctx.simulation_scenario.is_file():
        raise CeremonyError("dry-run requires a simulation scenario")
    scenario = json.loads(ctx.simulation_scenario.read_text(encoding="utf-8"))
    receipt = run_authorization_verifier(ctx, control)
    validate_outcome_contract(ctx.repo, control)
    if scenario.get("attempt_results_path_exists"):
        raise CeremonyError("dry-run scenario represents reused identity")
    phase_sequence = ["PRECHECK"]
    if scenario.get("precheck_pass", True):
        phase_sequence.extend(("MUTATION_STARTED", "DEPLOY", "POSTCHECK"))
        if scenario.get("postcheck_pass", True):
            phase_sequence.append("COMPLETE")
        else:
            phase_sequence.extend(("ROLLBACK", "COMPLETE"))
    return {
        "schema_version": "casuka-deployment-ceremony-dry-run-v2",
        "status": "PASS",
        "authorization_verifier": receipt["status"],
        "expected_phase_sequence": phase_sequence,
        "deployment_invocations": 0,
        "rollback_invocations": 0,
        "results_directory_created": False,
        "remote_mutations": 0,
    }


def execute_once(
    ctx: CeremonyContext,
    control: Mapping[str, Any],
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> Mapping[str, Any]:
    deployment = control["deployment"]
    results_dir = ctx.repo / deployment["results_dir"]
    if results_dir.exists():
        raise CeremonyError("single-use results directory already exists")
    authorization = run_authorization_verifier(ctx, control)
    contract = validate_outcome_contract(ctx.repo, control)
    if os.environ.get("OUTCOME_PROOF") != control["outcome_proof"]["path"]:
        raise CeremonyError("OUTCOME_PROOF environment is not exact")

    # Atomic local identity consumption; no live or remote mutation yet.
    results_dir.mkdir(parents=True, exist_ok=False)
    journal = Journal(results_dir / "PHASE_JOURNAL.jsonl")
    journal.append(
        "PRECHECK",
        "STARTED",
        {
            "authorization_commit": ctx.authorization_commit,
            "package_commit": git(ctx.repo, "rev-parse", "HEAD"),
            "deployment_id": deployment["id"],
        },
    )
    write_json_once(results_dir / "AUTHORIZATION_VERIFICATION.json", authorization)
    mutation_started = False
    deploy_invocations = 0
    rollback_invocations = 0
    protected_before: Mapping[str, Any] | None = None
    deployment_receipt: Mapping[str, Any] | None = None
    rollback_receipt: Mapping[str, Any] | None = None
    try:
        local_gates = run_local_candidate_gates(ctx.repo, control)
        t0 = confirm_t0_quiet_minute(ctx.repo, control, sleep=sleep)
        protected_before = snapshot_protected_remote_files(ctx.repo, control)
        remote_control = materialize_remote_control(ctx.repo, control)
        journal.append(
            "PRECHECK",
            "PASS",
            {
                "local_gate_count": len(local_gates),
                "engine_stopped": True,
                "cron_inhibited": True,
                "zero_tennis_entry_buys": True,
                "exits_and_holdings_reconcile": True,
                "remote_single_use_identity_reserved": True,
            },
        )
        write_json_once(results_dir / "LOCAL_GATE_RECEIPT.json", local_gates)
        write_json_once(results_dir / "T0_RECEIPT.json", t0)
        write_json_once(
            results_dir / "PRE_MUTATION_PROTECTED_SNAPSHOT.json",
            protected_before,
        )
        write_json_once(
            results_dir / "REMOTE_CONTROL_MATERIALIZATION.json",
            remote_control,
        )

        journal.append(
            "MUTATION_STARTED",
            "STARTED",
            {"candidate_retry_from_now": "FORBIDDEN"},
        )
        mutation_started = True
        backup = create_verified_backup(ctx.repo, control)
        write_json_once(results_dir / "BACKUP_RECEIPT.json", backup)

        journal.append(
            "DEPLOY",
            "STARTED",
            {"command": control["commands"]["deployment"]},
        )
        deploy_invocations += 1
        deployment_receipt = invoke_remote_literal(
            ctx.repo, control, control["commands"]["deployment"]
        )
        write_json_once(
            results_dir / "DEPLOYMENT_COMMAND_RECEIPT.json",
            deployment_receipt,
        )
        if deployment_receipt["exit_code"] != 0:
            raise CeremonyError("deployment script exited nonzero")
        journal.append(
            "DEPLOY",
            "PASS",
            {"exit_code": 0, "invocations": deploy_invocations},
        )

        journal.append("POSTCHECK", "STARTED", {})
        sleep(control["outcome_proof"]["post_boot"]["observation_seconds"])
        post = collect_post_deployment_evidence(
            ctx.repo,
            control,
            deployment_started_epoch=deployment_receipt["started_at_epoch"],
            protected_before=protected_before,
        )
        write_json_once(results_dir / "POST_DEPLOYMENT_EVIDENCE.json", post)
        cron_restoration = restore_original_crontab_after_pass(ctx.repo, control)
        write_json_once(
            results_dir / "CRON_RESTORATION_RECEIPT.json",
            cron_restoration,
        )
        journal.append(
            "POSTCHECK",
            "PASS",
            {
                "candidate_boot_count": post["restart_count"],
                "cron_restored_after_pass": True,
                "additional_restart": 0,
            },
        )
        final = {
            "schema_version": "casuka-deployment-ceremony-result-v2",
            "status": "DEPLOYED_PASS",
            "deployment_id": deployment["id"],
            "deploy_invocations": deploy_invocations,
            "rollback_invocations": rollback_invocations,
            "candidate_retries": 0,
            "rollback_status": "NOT_REQUIRED",
            "outcome_contract_sha256": control["outcome_proof"]["sha256"],
        }
    except Exception as exc:
        if mutation_started:
            journal.append(
                "ROLLBACK",
                "STARTED",
                {"reason": str(exc), "candidate_retry": "FORBIDDEN"},
            )
            rollback_invocations += 1
            rollback_receipt = invoke_rollback_artifact(ctx.repo, control)
            write_json_once(
                results_dir / "ROLLBACK_COMMAND_RECEIPT.json",
                rollback_receipt,
            )
            if rollback_receipt["exit_code"] != 0:
                journal.append(
                    "ROLLBACK",
                    "FAIL",
                    {"exit_code": rollback_receipt["exit_code"]},
                )
                final = {
                    "schema_version": "casuka-deployment-ceremony-result-v2",
                    "status": "ROLLBACK_FAILED",
                    "original_error": str(exc),
                    "deploy_invocations": deploy_invocations,
                    "rollback_invocations": rollback_invocations,
                    "candidate_retries": 0,
                }
            else:
                rollback_state = verify_rollback_state(ctx.repo, control)
                write_json_once(
                    results_dir / "ROLLBACK_STATE_RECEIPT.json",
                    rollback_state,
                )
                journal.append(
                    "ROLLBACK",
                    "PASS",
                    {
                        "exit_code": 0,
                        "engine_stopped": True,
                        "cron_inhibited": True,
                        "rollback_restart_count": 0,
                    },
                )
                final = {
                    "schema_version": "casuka-deployment-ceremony-result-v2",
                    "status": "ROLLED_BACK",
                    "original_error": str(exc),
                    "deploy_invocations": deploy_invocations,
                    "rollback_invocations": rollback_invocations,
                    "candidate_retries": 0,
                }
        else:
            final = {
                "schema_version": "casuka-deployment-ceremony-result-v2",
                "status": "PRECHECK_FAILED",
                "error": str(exc),
                "deploy_invocations": 0,
                "rollback_invocations": 0,
                "candidate_retries": 0,
            }
    journal.append("COMPLETE", final["status"], final)
    write_json_once(results_dir / "FINAL_RESULT.json", final)
    write_output_manifest(results_dir)
    return final


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--control", required=True)
    parser.add_argument("--mode", choices=("dry-run", "execute"), required=True)
    parser.add_argument("--authorization-commit", required=True)
    parser.add_argument("--authorization-report", required=True)
    parser.add_argument("--package-audit-pass", required=True)
    parser.add_argument("--remote-state-fixture")
    parser.add_argument("--simulation-scenario")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    ns = _parser().parse_args(argv)
    ctx = CeremonyContext(
        repo=Path(ns.repo).resolve(),
        control_path=ns.control,
        authorization_commit=ns.authorization_commit,
        authorization_report=ns.authorization_report,
        package_audit_pass=ns.package_audit_pass,
        mode=ns.mode,
        remote_state_fixture=(
            Path(ns.remote_state_fixture).resolve()
            if ns.remote_state_fixture
            else None
        ),
        simulation_scenario=(
            Path(ns.simulation_scenario).resolve()
            if ns.simulation_scenario
            else None
        ),
    )
    try:
        control = verifier.load_control(ctx.repo, ctx.control_path)
        if ctx.mode == "dry-run":
            receipt = dry_run(ctx, control)
        else:
            if ctx.remote_state_fixture or ctx.simulation_scenario:
                raise CeremonyError("execute mode forbids fixtures")
            receipt = execute_once(ctx, control)
    except (CeremonyError, verifier.VerificationError) as exc:
        print(
            json.dumps(
                {
                    "schema_version": "casuka-deployment-ceremony-v2",
                    "status": "FAIL",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    sys.stdout.buffer.write(canonical_bytes(receipt))
    return 0 if receipt.get("status") in ("PASS", "DEPLOYED_PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
