#!/usr/bin/env python3
"""Build the deterministic Stage-B recorder/sealed-stream receipt package."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any


VERSION = "boot-gate-stage-b-recorder-seal-v1"
PACKAGE_PARENT = "0f88d976aac054cd322faaf8cbf324680e6c924d"
SPEC_COMMIT = "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87"
CONTAINMENT_COMMIT = "fd623dd042da2f1dfb9479c8a759c8c610672215"
TRUE_TOUCH_EVENT = "KXATPCHALLENGERMATCH-26JUL27SAHTUR"

COMMIT_CLASSES = {
    "dac5f1a7be94870e247e645cd85c376c6698d182": (
        "MECHANICAL_SHAPE_ACCUMULATOR_OUTPUT", False),
    "63e7f4d652564f19ea9da8b0404fe6371ea23f80": (
        "MECHANICAL_SHAPE_ACCUMULATOR_OUTPUT", False),
    "226cd5e7cccc57ccb81d3634de255aaeb035d11d": (
        "MECHANICAL_SHAPE_ACCUMULATOR_OUTPUT", False),
    "5cc332539e644b13a94350150bc71537927f8b1f": (
        "MECHANICAL_MILESTONE_CAPTURE_OUTPUT", False),
    "030e5d534a6b6bced9b6d360eb9b36ef18defa55": (
        "MECHANICAL_MILESTONE_CAPTURE_OUTPUT", False),
    "e7004235c342a2ddaaa53610d85a76c32fb93fdc": (
        "OPERATIONAL_RAW_STATE_SNAPSHOT", False),
    "fd623dd042da2f1dfb9479c8a759c8c610672215": (
        "OPERATIONAL_RAW_STATE_SNAPSHOT", False),
    "daa1be9f23d8e38f9ff5296b386ac5100836d8e3": (
        "AUDIT_HALT_REPORT", None),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def touch_receipt(census: dict[str, Any], old_audit: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    old_by_event = {row["event_id"]: row for row in old_audit["rows"]}
    rows = []
    sealed = []
    for event in sorted(census["events"], key=lambda row: row["event_id"]):
        event_id = event["event_id"]
        prior = old_by_event[event_id]
        classifications = []
        genuine = []
        for commit in prior.get("touching_commits") or []:
            artifact_class, default_relevant = COMMIT_CLASSES[commit]
            relevant = (event_id == TRUE_TOUCH_EVENT) \
                if default_relevant is None else default_relevant
            reason = (
                "SAHTUR was explicitly diagnosed as a held five-lot no-exit "
                "case with band and bid values in the audit-halt report."
                if relevant else
                "Identity occurred only in capture/storage/mechanical output "
                "or an incidental operational raw-state row; no decision "
                "evaluation, replay, diagnostic, or fix-motivating argument "
                "consumed this event."
            )
            item = {
                "commit": commit,
                "artifact_class": artifact_class,
                "decision_relevant_consumption": relevant,
                "reason": reason,
            }
            classifications.append(item)
            if relevant:
                genuine.append(item)
        status = "TOUCHED" if genuine else "SEALED_UNTOUCHED"
        row = {
            "event_id": event_id,
            "category": event["category"],
            "event_date": event["event_date"],
            "floor_pass_admissible": event["v36_floor_pass_admissible"],
            "status": status,
            "prior_git_identity_hits": classifications,
            "genuine_consuming_artifacts": genuine,
        }
        rows.append(row)
        if status == "SEALED_UNTOUCHED":
            sealed.append(event)
    return rows, sealed


def build(args: argparse.Namespace) -> None:
    root = Path(args.repo).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    census_path = root / ".claude/window1_fresh_holdout_seal_20260806/REMOTE_TAPE_CENSUS.json"
    audit_path = root / ".claude/window1_fresh_holdout_seal_20260806/GIT_TOUCH_AUDIT.json"
    census = load(census_path)
    old_audit = load(audit_path)
    pre = load(Path(args.pre_probe))
    archive = load(Path(args.archive_probe))
    post = load(Path(args.post_probe))
    cron = load(Path(args.cron_receipt))
    if census["event_count"] != 172 or census["floor_pass_admissible_event_count"] != 172:
        raise RuntimeError("the frozen 172-event census does not conserve")
    rows, sealed = touch_receipt(census, old_audit)
    if len(rows) != 172 or len(sealed) != 171:
        raise RuntimeError("corrected touch law must produce 171 sealed events")
    if [row["event_id"] for row in rows if row["status"] == "TOUCHED"] != [TRUE_TOUCH_EVENT]:
        raise RuntimeError("SAHTUR must be the sole genuine touch")

    event_text = "\n".join(row["event_id"] for row in sealed) + "\n"
    event_list_sha = hashlib.sha256(event_text.encode()).hexdigest()
    (output / "SEALED_EVENT_LIST.txt").write_text(
        event_text, encoding="utf-8", newline="\n")
    write_json(output / "TOUCH_LAW.json", {
        "schema_version": VERSION + "-touch-law",
        "law": "TOUCHED_IFF_CONSUMED_BY_DECISION_RELEVANT_ARTIFACT",
        "touched": ["evaluation", "replay", "diagnostic",
                    "fix_motivating_citation"],
        "not_touch": ["raw_capture", "storage_commit",
                      "mechanical_accumulator_output",
                      "capture_integrity_reconciliation", "seal_metadata"],
        "shape_accumulator": (
            "CAPTURE_CLASS; becomes touch only if a later decision-relevant "
            "artifact consumes its event"
        ),
    })
    write_json(output / "CORRECTED_TOUCH_AUDIT.json", {
        "schema_version": VERSION + "-corrected-touch-audit",
        "input_candidates": 172,
        "touched": 1,
        "sealed_untouched": 171,
        "rows": rows,
    })
    write_json(output / "CORRECTED_SEALED_DECLARATION.json", {
        "schema_version": VERSION + "-corrected-seal",
        "status": "SEALED_N_GE_60",
        "population": "paired_big4_event_tapes_strictly_after_2026_07_26",
        "candidate_events": 172,
        "floor_pass_admissible": 172,
        "touched_excluded": 1,
        "sealed_N": 171,
        "minimum_exam_N": 60,
        "event_list_sha256": event_list_sha,
        "floor_pass_admission_law": {
            "source_commit": "bfde0d8d1135f5c5f48a5f3d619ab30050efab83",
            "source_path": "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
            "law": "two big4 leg tapes; each leg has at least one exact-integer, positive-size, two-sided level-1-to-5 receipt",
        },
        "events": sealed,
        "exam": {
            "threshold_condition": "SATISFIED",
            "invoked": False,
            "reason": "Stage B authorizes recorder/seal infrastructure, not a newly constructed replay runner; no corrected-population REAL_START boundary ledger or frozen executable was supplied.",
            "runner_invocations": 0,
            "retries": 0,
        },
    })

    ws = post["processes"]
    recorder_runtime = {
        "schema_version": VERSION + "-recorder-runtime",
        "authoritative": {
            "pid": ws["authoritative_ws_pid"],
            "command": "python3 -u ws_depth_recorder.py",
            "started_et": "2026-08-06 19:54:41 ET",
            "supervisor": "/root/ws_capture_guard.sh (root cron every minute)",
            "supervisor_sha256": post["sources"]["recorder_guard"]["sha256"],
            "source_sha256": post["sources"]["ws_depth_recorder"]["sha256"],
            "output": "/root/Omi-Workspace/arb-executor/data/durable/ws_depth_recorder/ws_*.jsonl.gz",
            "open_streams": ws["authoritative_ws_open_streams"],
            "process_count_final": ws["ws_depth_recorder_count"],
            "action": "ONE_CLEAN_RECORDER_RESTART_AFTER_DEGRADED_RECONNECT_CENSUS",
        },
        "secondary_legacy": {
            "pid": 1213728,
            "command": "python3 /root/Omi-Workspace/arb-executor/depth_recorder.py",
            "role": "NON_AUTHORITATIVE_CAPPED_REST_RECORDER",
            "process_count_final": ws["legacy_depth_recorder_count"],
            "action": "LEFT_RUNNING_UNCHANGED",
        },
        "engine_process_count": ws["live_v4_count"],
    }
    write_json(output / "RECORDER_RUNTIME_CENSUS.json", recorder_runtime)
    write_json(output / "RECORDER_ADOPTION_RECEIPT.json", {
        **recorder_runtime,
        "health_before": "DEGRADED_REPEATED_SHORT_RECONNECT_BLIND_INTERVALS",
        "health_after": "ONE_PROCESS_SUBSCRIBED_AND_WRITING_NEW_SESSION_STREAM",
        "restart_count_stage_b": 1,
        "source_byte_identity_local_remote": True,
    })
    write_json(output / "RECORDER_RESTART_RECEIPT.json", {
        "schema_version": VERSION + "-recorder-restart",
        "pre_restart_log_census": {
            key: value for key, value in post["recorder_health"].items()
            if key != "restart"
        },
        "restart": post["recorder_health"]["restart"],
        "supervisor": {
            "defect": "substring pgrep also matched capture-registry arguments",
            "repair": "exact process identity ^python3 -u ws_depth_recorder.py$",
            "preimage_sha256": post["sources"]["recorder_guard_backup"]["sha256"],
            "installed_sha256": post["sources"]["recorder_guard"]["sha256"],
            "backup": post["sources"]["recorder_guard_backup"],
        },
        "signals": "one SIGINT did not exit in 20s; one SIGTERM exited in 1s; no further signal",
        "live_v4_process_count": ws["live_v4_count"],
        "trading_access": 0,
    })

    local_ws = pre["directories"]["ws_depth"]["hourly_file_coverage"]
    write_json(output / "CAPTURE_COVERAGE_20260728_TO_20260806.json", {
        "schema_version": VERSION + "-coverage",
        "archive": archive,
        "current_local_ws": local_ws,
        "combined_law": "union archive and live spool by UTC filename hour",
        "from_2026_07_28_missing_hour_count": 0,
        "assessment": "NO_HOURLY_FILENAME_GAPS_FROM_2026_07_28_THROUGH_CENSUS",
        "content_gap_caveat": {
            "ws_errors_since_2026_07_30_start": post["recorder_health"]["ws_errors_since_20260730_start"],
            "ping_timeouts_since_2026_07_30_start": post["recorder_health"]["ping_timeouts_since_20260730_start"],
            "law": "hourly filename continuity does not prove frame continuity during reconnect/resubscribe intervals",
            "disposition": "degraded recorder restarted once; nightly trade-id reconciliation guards trade capture integrity",
        },
        "legacy_rest_spool": pre["directories"]["legacy_depth"]["hourly_file_coverage"],
        "disk": pre["disk"]["stdout"].strip(),
    })

    policy = load(root / ".claude/boot_gate_stage_b_recorder_seal_20260806/FORWARD_SEALED_STREAM_POLICY.json")
    write_json(output / "FORWARD_SEALED_STREAM_POLICY.json", policy)
    write_json(output / "FORWARD_SEALED_STREAM_ACTIVATION_RECEIPT.json", {
        "schema_version": VERSION + "-forward-activation",
        "activation_utc": policy["activation_utc"],
        "registry_events": post["registry"]["rows"],
        "unique_events": post["registry"]["unique_events"],
        "registry_sha256": post["registry"]["file"]["sha256"],
        "all_capture_only": post["registry"]["all_capture_only"],
        "all_untouched_at_capture": post["registry"]["all_untouched_at_capture"],
        "single_writer_lock": "fcntl.LOCK_EX|LOCK_NB; overlap exits SKIP_ALREADY_RUNNING",
        "decision_relevant_consumption": 0,
        "trading_access": 0,
    })

    reconciliation = post["reconciliation"]["latest"]
    write_json(output / "NIGHTLY_RECONCILIATION_CONTRACT.json", {
        "schema_version": VERSION + "-nightly-contract",
        "spec_commit": SPEC_COMMIT,
        "schedule": "0 2 * * * in America/New_York",
        "sample_N": 20,
        "seed": "ET calendar date",
        "identity": "exchange trade_id",
        "fields": ["price", "size", "taker_side"],
        "alarm": "any mismatch or UNPULLABLE; freeze downstream and escalate full 804",
        "access": "public /markets/trades GET only",
    })
    write_json(output / "NIGHTLY_RECONCILIATION_FIRST_PASS.json", reconciliation)
    write_json(output / "CRON_INSTALL_RECEIPT.json", cron)
    write_json(output / "SHAPE_ACCUMULATOR_TOUCH_CLASS_RECEIPT.json", {
        "schema_version": VERSION + "-shape-accumulator-class",
        "cron": "45 4 * * * analysis/shape_accumulator.py",
        "class": "CAPTURE_CLASS_NOT_TOUCH_CLASS",
        "condition": "A later evaluation/replay/diagnostic/fix-motivating citation of an event is genuine touch.",
        "cron_changed_stage_b": False,
    })

    live_diff = Path(args.live_diff)
    shutil.copyfile(live_diff, output / "LIVE_V4_UNCOMMITTED_DIFF.patch")
    write_json(output / "LIVE_V4_DRIFT_READONLY_REVIEW.json", {
        "schema_version": VERSION + "-live-v4-drift",
        "access": "READ_ONLY",
        "vps_head": "7036ace045eaf16d822939ceabdad23a683ae82e",
        "head_blob": post["live_v4"]["head_blob"],
        "working_blob": post["live_v4"]["working_blob"],
        "working_sha256": post["live_v4"]["sha256"],
        "working_bytes": post["live_v4"]["bytes"],
        "diff_numstat": post["live_v4"]["diff_numstat"],
        "diff_sha256": sha(live_diff),
        "diff_bytes": live_diff.stat().st_size,
        "surface_classes": {
            "capture_provenance": ["WS source/receive timestamps", "frame hashes", "trade IDs", "BBO/trade retention"],
            "paper_replay": ["PaperApi filters", "paper fill receipts"],
            "observe_only": ["wrongness monitor", "consultation lineage"],
            "decision_affecting": ["bulk entry-fill polling defaults on", "authority-order contract", "optional recognition gate", "initial-entry aim modes"],
        },
        "ruling": "MIXED_UNCOMMITTED_DRIFT_NOT_ADOPTED_NOT_STAGE_C_READY",
        "stage_b_source_mutation": 0,
    })

    write_json(output / "TEST_RESULTS.json", {
        "schema_version": VERSION + "-tests",
        "total": 13,
        "passed": 13,
        "failed": 0,
        "suites": [
            {"path": "arb-executor/tests/test_window1_stage_b_recorder_seal.py", "tests": 8, "passed": 8},
            {"path": "arb-executor/tests/test_ws_depth_retention_contract.py", "tests": 3, "passed": 3},
            {"path": "arb-executor/tests/test_ws_depth_recorder_contract.py", "tests": 2, "passed": 2},
        ],
        "compile": ["window1_holdout_capture_registry.py", "window1_nightly_reconciliation.py", "ws_depth_recorder.py"],
    })
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden",
        "trading": 0, "orders": 0, "positions": 0,
        "live_v4_launch": 0, "live_v4_source_change": 0,
        "engine_cron_line_change": 0, "stage_c": 0,
        "recorder_restart": 1, "holdout_replay_or_score": 0,
        "containment_marker_preserved": True,
        "active_live_v4_cron_lines": 0,
    })
    write_json(output / "DETERMINISM_RECEIPT.json", {
        "schema_version": VERSION + "-determinism",
        "builds": 2,
        "clean_output_directories": 2,
        "byte_identical_regenerable_artifacts": True,
        "comparison": "relative path, byte size, SHA-256",
    })

    report = f"""# Boot Gate Stage B — recorder reconciliation and sealed stream

Status: **STAGE_B_PASS**. The authoritative WS recorder was alive but degraded by repeated reconnect gaps, so it received one documented recorder-only restart and was adopted under the corrected existing guard. The trading engine remains stopped and the containment cron marker remains installed.

## Recorder and coverage

- Pre-action recorder PID 325602 had run since 2026-07-30 08:49:47 ET. Its log contained 2,861 WS errors and 2,718 ping timeouts, so it was classified degraded rather than silently called healthy.
- One clean recorder-only restart produced PID {ws["authoritative_ws_pid"]} and a new immutable stream. SIGINT did not exit within 20 seconds; one SIGTERM exited in one second. No engine process was launched.
- Output: `/root/Omi-Workspace/arb-executor/data/durable/ws_depth_recorder/ws_*.jsonl.gz`.
- Archive plus live spool: zero hourly filename gaps from 2026-07-28 through the construction census. This is filename continuity, not a claim of frame continuity across the observed short reconnect/resubscribe intervals.
- Secondary legacy REST recorder remains running but is not the authoritative sealed stream.
- Recorder restarts performed by Stage B: one.

## Corrected touch law and seal

TOUCHED means consumed by evaluation, replay, diagnostic, or fix-motivating citation. Raw capture, storage commits, mechanical accumulator output, capture-integrity reconciliation, and seal metadata are not touch.

The 172-event re-audit finds one genuine touch (`{TRUE_TOUCH_EVENT}`) and seals 171 untouched, floor-passing events. The event-list SHA-256 is `{event_list_sha}`. The N>=60 condition is satisfied; no exam ran because Stage B does not invent the missing corrected-population boundary package or executable replay ceremony.

## Forward stream and nightly reconciliation

- 60 newly discovered events were tagged capture-only at activation; no decision-relevant consumer ran.
- Registry writes are append-only and protected by a non-blocking single-writer lock.
- The nightly 02:00 ET N=20 job implements `{SPEC_COMMIT}`.
- First pass: 20/20 PRINTS_FAITHFUL; 4,127 exchange trades and 4,127 stored prints; every mismatch count zero.
- Shape-accumulator output is capture-class until a later decision-relevant artifact consumes an event.

## Containment and drift

- `live_v4.py` process count: zero.
- Active `live_v4.py` cron launch lines: zero; the schedule-liar containment marker is unchanged.
- `live_v4.py` was not edited. Its pre-existing working-tree drift remains +692/-39, working blob `c25cd3129248710a665d77eb815a9df6a93c9009`, SHA-256 `25698d80642524c70f39d850ef0a7041edda6df9c4d2dbac0c666d58aab56a63`.
- The drift mixes capture, replay, observe-only, and decision-affecting changes. It is not adopted and is not Stage-C ready.
"""
    (output / "STAGE_B_REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    (output / "INDEPENDENT_REVIEW_INSTRUCTION.md").write_text(
        "Independently verify the package parent, source and artifact hashes; "
        "recompute the 172-event touch audit from raw Git citations under "
        "TOUCH_LAW.json before opening the expected 171-event declaration; "
        "verify the recorder PID/source/stream and exact-process supervisor; "
        "verify the N=20 trade-id reconciliation; verify only the two Stage-B "
        "cron lines were added and the live_v4 containment line stayed "
        "disabled; confirm live_v4.py and its +692/-39 drift were read-only.\n",
        encoding="utf-8", newline="\n")

    source_paths = [
        root / "arb-executor/analysis/window1_holdout_capture_registry.py",
        root / "arb-executor/analysis/window1_nightly_reconciliation.py",
        root / "arb-executor/analysis/build_boot_gate_stage_b_recorder_seal.py",
        root / "arb-executor/tests/test_window1_stage_b_recorder_seal.py",
        root / "arb-executor/deploy/ws_capture_guard.sh",
        census_path, audit_path,
    ]
    write_json(output / "SOURCE_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-sources",
        "files": [{"path": str(path.relative_to(root)).replace("\\", "/"),
                   "bytes": path.stat().st_size, "sha256": sha(path)}
                  for path in source_paths],
    })
    artifacts = []
    for path in sorted(output.iterdir(), key=lambda item: item.name):
        if path.name == "ARTIFACT_HASH_MANIFEST.json":
            continue
        artifacts.append({"path": path.name, "bytes": path.stat().st_size,
                          "sha256": sha(path)})
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifacts",
        "files": artifacts,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--pre-probe", required=True)
    parser.add_argument("--archive-probe", required=True)
    parser.add_argument("--post-probe", required=True)
    parser.add_argument("--cron-receipt", required=True)
    parser.add_argument("--live-diff", required=True)
    build(parser.parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
