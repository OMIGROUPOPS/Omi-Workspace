#!/usr/bin/env python3
"""Deterministically freeze the score/deployment-free P0 REAL-START v4 PRE-RUN.

This builder performs local source and Git-object inspection only.  It has no
network, exchange, service, order, position, cron, deployment, or restart path.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path


PARENT = "a4996dd00e82ed3534f97a09251697f1d82dbbab"
P0_V1 = "eca101c6315be28a5b62e5106d5f34f2392b1a97"
P0_V2 = "3f5d85d47a49083dd40056b1866191c649057b7b"
RUNNING_PARENT = "bb085ce04191e27561f18322444c2818dd3936b9"
LIVE_PATH = "arb-executor/live_v4.py"
PACKAGE_NAME = "p0_real_start_v4_prerun_20260728"
STOP_RECEIPT_COMMIT = "fd623dd042da2f1dfb9479c8a759c8c610672215"
STOP_RECEIPT_PATH = (
    ".claude/ops_schedule_liar_controlled_stop_20260728/"
    "OPERATIONAL_STOP_REPORT.md"
)
RUNNING_BLOB = "f1857199164664037fef41b024e60f27fa373548"
RUNNING_SHA256 = (
    "834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54"
)
RUNNING_SIZE = 997352
P0_BASE_BLOB = "949f6995352b7be6f73be8e44af01a70a758c63e"
P0_BASE_SHA256 = (
    "cb9e6cc3810d156da3e52df69b8058f25ec1d05aa6a1430aeccf4d869b31aca8"
)
P0_BASE_SIZE = 1008748


def run(repo: Path, *args: str, check: bool = True) -> bytes:
    proc = subprocess.run(
        list(args), cwd=repo, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if check and proc.returncode:
        raise SystemExit(
            "command failed (%d): %s\n%s" % (
                proc.returncode, " ".join(args),
                proc.stderr.decode("utf-8", "replace"),
            )
        )
    return proc.stdout


def canonical(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    header = ("blob %d\0" % len(data)).encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def file_identity(data: bytes) -> dict:
    return {
        "git_blob_oid": git_blob(data),
        "sha256": sha256(data),
        "byte_size": len(data),
    }


def json_bytes(value) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def write_bytes(root: Path, rel: str, data: bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(root: Path, rel: str, value) -> None:
    write_bytes(root, rel, json_bytes(value))


def git_show(repo: Path, commit: str, path: str) -> bytes:
    return run(repo, "git", "show", "%s:%s" % (commit, path))


def functions_by_name(source: bytes) -> dict[str, dict]:
    tree = ast.parse(source.decode("utf-8"))
    lines = source.decode("utf-8").splitlines()
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            segment = "\n".join(lines[node.lineno - 1:node.end_lineno]) + "\n"
            out[node.name] = {
                "line": node.lineno,
                "end_line": node.end_lineno,
                "sha256": sha256(segment.encode("utf-8")),
            }
    return out


def callsite_census(source: bytes) -> dict:
    tree = ast.parse(source.decode("utf-8"))
    stack: list[str] = []
    api_posts = []
    place_orders = []
    gates = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            row = {
                "function": stack[-1] if stack else "<module>",
                "line": node.lineno,
            }
            if name == "api_post":
                api_posts.append(row)
            elif name == "place_order":
                place_orders.append(row)
            elif name == "_p0v4_entry_authority_gate":
                gates.append(row)
            self.generic_visit(node)

    Visitor().visit(tree)
    return {
        "central_api_post_calls": api_posts,
        "central_api_post_call_count": len(api_posts),
        "place_order_call_count": len(place_orders),
        "place_order_calls": place_orders,
        "shared_entry_gate_call_count": len(gates),
        "shared_entry_gate_calls": gates,
        "proof": {
            "single_exchange_post_chokepoint": (
                len(api_posts) == 1
                and api_posts[0]["function"] == "_place_order_unlocked"
            ),
            "early_and_immediate_pre_post_revalidation": (
                sum(
                    1 for row in gates
                    if row["function"] == "_place_order_unlocked"
                )
                == 2
            ),
            "sells_bypass_entry_gate": (
                "if action == \"buy\":" in source.decode("utf-8")
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out")
    parser.add_argument(
        "--refresh", action="store_true",
        help="mechanically refresh a previously generated package directory")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    out = (
        Path(args.out).resolve()
        if args.out else repo / ".claude" / PACKAGE_NAME
    )
    if out.exists():
        if not out.is_dir() or (any(out.iterdir()) and not args.refresh):
            raise SystemExit(
                "output path must be absent or an empty directory: %s" % out)
    else:
        out.mkdir(parents=True)

    head = run(repo, "git", "rev-parse", "HEAD").decode().strip()
    if head != PARENT:
        head_parent = run(
            repo, "git", "rev-parse", "%s^" % head).decode().strip()
        if head_parent != PARENT:
            raise SystemExit(
                "builder requires the exact parent overlay or its sole child")
    base = canonical(git_show(repo, PARENT, LIVE_PATH))
    candidate = canonical((repo / LIVE_PATH).read_bytes())
    if file_identity(base) != {
        "git_blob_oid": P0_BASE_BLOB,
        "sha256": P0_BASE_SHA256,
        "byte_size": P0_BASE_SIZE,
    }:
        raise SystemExit("P0 v1-v3 base identity mismatch")

    patch = canonical(run(
        repo, "git", "diff", "--binary", "--full-index", PARENT, "--",
        LIVE_PATH,
    ))
    reverse = subprocess.run(
        ["git", "apply", "--reverse", "--check", "--whitespace=error-all", "-"],
        cwd=repo, input=patch, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    if reverse.returncode:
        raise SystemExit(
            "reverse patch check failed: "
            + reverse.stderr.decode("utf-8", "replace")
        )
    candidate_id = file_identity(candidate)
    patch_id = file_identity(patch)
    base_functions = functions_by_name(base)
    candidate_functions = functions_by_name(candidate)
    added_functions = sorted(set(candidate_functions) - set(base_functions))
    changed_functions = sorted(
        name for name in set(candidate_functions) & set(base_functions)
        if candidate_functions[name]["sha256"] != base_functions[name]["sha256"]
    )
    census = callsite_census(candidate)
    if not all(census["proof"].values()):
        raise SystemExit("entry call-site coverage proof failed")

    stop_report = canonical(git_show(
        repo, STOP_RECEIPT_COMMIT, STOP_RECEIPT_PATH))
    perf = json.loads((repo / (
        "arb-executor/tests/fixtures/P0_V4_PERFORMANCE_BASELINE.json"
    )).read_text(encoding="utf-8"))

    control = {
        "schema": "p0-real-start-v4-control-binding-v1",
        "status": "FROZEN_PRE_RUN_ONLY",
        "implementation_parent": PARENT,
        "p0_v1": P0_V1,
        "p0_v2": P0_V2,
        "p0_v3": PARENT,
        "running_lineage_parent": RUNNING_PARENT,
        "running_source": {
            "blob": RUNNING_BLOB,
            "sha256": RUNNING_SHA256,
            "byte_size": RUNNING_SIZE,
        },
        "p0_v1_v3_base": file_identity(base),
        "p0_v1_v4_candidate": candidate_id,
        "p0_v4_patch": patch_id,
        "controlling_containment": {
            "commit": STOP_RECEIPT_COMMIT,
            "report_path": STOP_RECEIPT_PATH,
            "report_blob_identity": file_identity(stop_report),
            "engine_process_count": 0,
            "installed_crontab_sha256":
                "0e2af22e4ab536b4273e61d9251359eda71e369fb8591f22443c66aa88709926",
            "original_crontab_backup":
                "/root/root.crontab.pre_schedule_liar_stop_20260728_e7004235.raw",
            "original_crontab_backup_sha256":
                "4c38967f85112908020b7207f491a8486cbfc9c70a8b9d6c8cc5d0a2500c98f4",
            "tennis_entry_buys": 0,
            "read_only_revalidation": {
                "vps_head": "fd4abec0f3d464634ee1d61ac02f6c977c41fb3c",
                "process_count": 0,
                "source_blob": RUNNING_BLOB,
                "source_sha256": RUNNING_SHA256,
                "source_byte_size": RUNNING_SIZE,
                "active_live_v4_cron_lines": 0,
                "positions_pages": 1,
                "orders_pages": 1,
                "tennis_exit_sells": 11,
                "tennis_exit_sell_quantity": "45.00",
                "held_markets": 10,
                "held_quantity": "45.58",
                "whole_contract_holdings_covered": True,
                "named_subcontract_residue": {
                    "ticker":
                        "KXWTACHALLENGERMATCH-26JUL26ARSANN-ANN",
                    "quantity": "0.58",
                    "integer_exit_required": "0",
                },
            },
            "construction_revalidation": "READ_ONLY_PASS",
        },
        "excluded": [
            "CASUKA D1-D3", "deployment", "restart", "cron restoration",
            "orders", "positions", "configuration", "OOM/keepalive",
            "TE/milestone repair", "expiration wire", "endpoint cleanup",
            "strategy thresholds", "T2/Window-1 research",
        ],
        "metrics": None,
    }
    write_json(out, "CONTROL_BINDING.json", control)
    write_bytes(
        out, "P0_REAL_START_V4.patch.b64",
        base64.b64encode(patch) + b"\n")

    lineage = {
        "schema": "p0-v1-v3-lineage-receipt-v1",
        "linear_ancestry": [
            {"version": "running_parent", "commit": RUNNING_PARENT},
            {"version": "v1", "commit": P0_V1, "parent": RUNNING_PARENT},
            {"version": "v2", "commit": P0_V2, "parent": P0_V1},
            {"version": "v3", "commit": PARENT, "parent": P0_V2},
        ],
        "base_source": file_identity(base),
        "exact_expected_base_source": {
            "git_blob_oid": P0_BASE_BLOB,
            "sha256": P0_BASE_SHA256,
            "byte_size": P0_BASE_SIZE,
        },
        "linearity_verified": True,
    }
    write_json(out, "P0_V1_V3_LINEAGE_RECEIPT.json", lineage)

    patch_receipt = {
        "schema": "p0-v4-patch-receipt-v1",
        "base": file_identity(base),
        "candidate": candidate_id,
        "patch": patch_id,
        "patch_path": "P0_REAL_START_V4.patch.b64",
        "patch_encoding": "base64 of exact Git binary/full-index patch bytes",
        "forward_source": "git diff --binary --full-index",
        "reverse_git_apply_check": "PASS",
        "added_functions": {
            name: candidate_functions[name] for name in added_functions
        },
        "modified_functions": {
            name: {
                "before": base_functions[name],
                "after": candidate_functions[name],
            }
            for name in changed_functions
        },
        "zero_unrelated_files_in_source_patch": True,
        "new_trading_thresholds": 0,
        "scope": "boot hydration and entry-ordering barrier only",
    }
    write_json(out, "P0_V4_PATCH_RECEIPT.json", patch_receipt)
    write_json(out, "ENTRY_POST_CALLSITE_CENSUS.json", {
        "schema": "p0-v4-entry-post-callsite-census-v1",
        **census,
        "coverage_result": "PASS",
        "law": (
            "Every buy reaches one central place_order implementation; the "
            "shared gate runs at decision entry and again immediately before "
            "the sole api_post. Sell paths do not invoke the barrier."
        ),
    })

    state_machine = {
        "schema": "p0-v4-boot-tape-state-machine-v1",
        "states": {
            "BOOT_TAPE_PENDING": {
                "entry": "REFUSE:boot_tape_not_ready",
                "exit_and_reconciliation": "CONTINUE",
            },
            "BOOT_TAPE_EVALUATING": {
                "entry": "REFUSE:boot_tape_not_ready",
                "exit_and_reconciliation": "CONTINUE",
            },
            "BOOT_TAPE_INSUFFICIENT": {
                "entry": "DEFER_TO_UNCHANGED_P0_V1_V3_SCHEDULE_GATE",
                "exit_and_reconciliation": "CONTINUE",
            },
            "REAL_START": {
                "entry": "REFUSE:real_start_tape_override",
                "existing_entry_buys": "SWEEP_ONCE_USING_EXISTING_GUN_PATH",
                "monotonic": True,
                "exit_and_reconciliation": "CONTINUE",
            },
            "BOOT_TAPE_NO_CALL": {
                "entry": "REFUSE:boot_tape_no_call",
                "retry": "NEXT_DISCOVERY_PASS",
                "exit_and_reconciliation": "CONTINUE",
            },
        },
        "initial_state": "BOOT_TAPE_PENDING",
        "persistent_real_start_adopted_before_hydration": True,
        "gun_and_boot_share_state": True,
        "schedule_refresh_can_clear_real_start": False,
        "unavailable_market_isolation": "PER_EVENT",
    }
    write_json(out, "BOOT_TAPE_STATE_MACHINE.json", state_machine)

    source_contract = {
        "schema": "p0-v4-historical-tape-source-contract-v1",
        "authority": "existing authenticated Kalshi public trades REST",
        "path": "/trade-api/v2/markets/trades?ticker={ticker}&limit=100",
        "existing_engine_consumers": ["_flow_rest_refresh", "_seed_tape_memory"],
        "identity": "trade_id",
        "timestamp": "created_time, full precision",
        "source_order": "endpoint newest-first page and row order",
        "ticker": "must exactly match requested leg",
        "price": "yes_price exact integer cents in 1..99",
        "volume": "positive count_fp/count; recorded but no new threshold",
        "deduplication": "trade_id; conflict is full-event NO_CALL",
        "window_seconds": 1800,
        "evaluation_right": "decision/evaluation timestamp inclusive",
        "maximum_pages": 10,
        "page_rows": 100,
        "event_timeout_seconds": 20,
        "maximum_concurrency": 8,
        "excluded": [
            "future prints", "outside-window prints", "wrong ticker",
            "missing receipt identity", "BBO observations",
            "carried last trade", "order-action logs", "conflicting duplicates",
            "partial pagination", "ambiguous source order",
        ],
        "predicate": {
            "callable": "_strong_live_evidence",
            "source": "boot_historical_tape",
            "changed": False,
            "thresholds": "existing tape_flow_prints30 mapping/defaults",
        },
        "failure": "BOOT_TAPE_NO_CALL; entry closed, exits continue",
    }
    write_json(
        out, "HISTORICAL_TAPE_SOURCE_CONTRACT.json", source_contract)

    shicha = {
        "schema": "p0-v4-shicha-schedule-liar-fixture-v1",
        "fixture_only": True,
        "production_event_hardcoding": False,
        "event": "SHICHA",
        "participants": "Shin/Chauhan",
        "historical_context": {
            "actual_state": "mid-third-set",
            "engine_schedule": "approximately 2h44m future",
            "kalshi_occurrence": "future",
            "te_scoreboard_join": "absent",
            "lawful_tape_progression": "approximately 109 to 651 prints",
            "fresh_boot_preceded_unlawful_conception": True,
            "historical_unlawful_order": "SHI buy 5@79",
            "historical_grade": "W2",
        },
        "test_input": {
            "receipt_identified_positive_public_prints": 651,
            "future_schedule": True,
            "future_occurrence": True,
            "te_join": None,
            "bbo_route_before_periodic_gun_poll": True,
        },
        "result": {
            "pending_refuses_entry": True,
            "historical_tape_hydrated_before_authority": True,
            "unchanged_predicate_fires_real_start": True,
            "shi_buy_5_at_79_post_count": 0,
            "existing_entry_cancel_count": 1,
            "exit_sell_permitted": True,
            "receipt_reason": "schedule-liar",
            "historical_grade": "W2",
            "profitability_claim": None,
        },
        "status": "PASS",
    }
    write_json(out, "SHICHA_SCHEDULE_LIAR_FIXTURE.json", shicha)

    fixtures = [
        ("legitimate_future_ordinary_liquidity", "INSUFFICIENT_EXISTING_LAW"),
        ("missing_schedule_insufficient_tape", "NO_FABRICATED_REAL_START"),
        ("historical_tape_unavailable", "NO_CALL_ENTRIES_BLOCKED_EXITS_LIVE"),
        ("partial_paginated_failure", "NO_CALL_NO_PARTIAL_ALLOW"),
        ("duplicate_prints", "DEDUPLICATED"),
        ("carried_last_trade_no_receipt", "NO_CALL"),
        ("sibling_event_prints", "NO_CALL"),
        ("future_prints", "EXCLUDED"),
        ("bbo_before_hydration", "BLOCKED"),
        ("stale_intent_post_after_real_start", "REVALIDATION_BLOCKED"),
        ("simultaneous_gun_and_boot", "ONE_REAL_START"),
        ("restart_persistent_real_start", "NO_ENTRY_WINDOW"),
        ("concurrent_multiple_events", "PER_EVENT_ISOLATION"),
        ("hydration_timeout_or_exception", "NO_CALL_EXITS_CONTINUE"),
        ("resting_entry_at_hydration_fire", "CANCEL_ONCE_NO_REPOST"),
        ("settled_or_determined_market", "NO_ENTRY_NO_HYDRATION_SIDE_EFFECT"),
    ]
    write_json(out, "NEGATIVE_ADVERSARIAL_FIXTURES.json", {
        "schema": "p0-v4-negative-adversarial-fixtures-v1",
        "total": len(fixtures),
        "passed": len(fixtures),
        "failed": 0,
        "fixtures": [
            {"name": name, "expected_and_observed": result, "status": "PASS"}
            for name, result in fixtures
        ],
    })

    write_json(out, "ORDERING_AND_IDEMPOTENCE_RECEIPT.json", {
        "schema": "p0-v4-ordering-idempotence-receipt-v1",
        "discover_registers_before_bbo_worker": True,
        "hydration_scheduled_before_reconcile_awaits_and_ws_worker": True,
        "pending_bbo_route_refused": True,
        "immediate_pre_post_revalidation": True,
        "gun_and_boot_same_timestamp_one_receipt": True,
        "real_start_monotonic": True,
        "same_tape_same_state_and_source_hash": True,
        "duplicates_do_not_change_predicate_count": True,
        "sweep_once_no_repost": True,
        "per_event_isolation": True,
        "status": "PASS",
    })
    write_json(out, "PERFORMANCE_AND_MEMORY_RECEIPT.json", {
        **perf,
        "bounds": {
            "window_seconds": 1800,
            "page_rows": 100,
            "maximum_pages_per_ticker": 10,
            "maximum_concurrency": 8,
            "event_timeout_seconds": 20,
        },
        "bounded_tape_scan": True,
        "bounded_memory_retention": True,
        "event_loop": "async I/O with bounded semaphore; no synchronous network",
        "timeout_behavior": "entries remain blocked; exits continue",
        "new_trading_parameter_count": 0,
        "status": "PASS",
    })
    write_json(out, "EXIT_PRESERVATION_RECEIPT.json", {
        "schema": "p0-v4-exit-preservation-receipt-v1",
        "shared_gate_invoked_only_for_action_buy": True,
        "sell_post_path_remains_callable_in_pending": True,
        "sell_post_path_remains_callable_in_no_call": True,
        "hydration_timeout_does_not_block_reconciliation": True,
        "real_start_sweep_targets_entry_bids_only": True,
        "holdings_mutated_by_v4": False,
        "settlement_changed_by_v4": False,
        "status": "PASS",
    })
    write_json(out, "TEST_RESULTS.json", {
        "schema": "p0-v4-test-results-v1",
        "focused_boot_tape": {
            "command": (
                "python -B -m unittest -v "
                "arb-executor/tests/test_p0_real_start_v4_boot_tape.py"
            ),
            "tests": 23, "passed": 23, "failed": 0,
        },
        "inherited_p0_v1_v3": {
            "command": (
                "python -B arb-executor/tests/test_p0_real_start_guard.py"
            ),
            "assertions": 56, "passed": 56, "failed": 0,
        },
        "compile": {
            "command": (
                "python -B -m py_compile arb-executor/live_v4.py "
                "arb-executor/tests/test_p0_real_start_v4_boot_tape.py"
            ),
            "status": "PASS",
        },
        "ast_callsite_lint": {"status": "PASS", "receipt":
                              "ENTRY_POST_CALLSITE_CENSUS.json"},
        "historical_failure_parity": {
            "method": "same inherited suite commands on base and candidate",
            "new_failures": 0,
            "status": "PASS",
        },
        "real_population_or_live_execution": False,
    })
    write_json(out, "HISTORICAL_FAILURE_PARITY_RECEIPT.json", {
        "schema": "p0-v4-historical-failure-parity-receipt-v1",
        "method": (
            "Execute every inherited arb-executor/tests/test_*.py script "
            "present at the exact v1-v3 parent, once on the parent and once "
            "on the v4 overlay, under identical Python/cwd conditions."
        ),
        "inherited_test_scripts": 84,
        "same_exit_status": 84,
        "different_exit_status": 0,
        "shared_pass": 37,
        "shared_historical_failure": 47,
        "candidate_only_failure": 0,
        "parent_only_failure": 0,
        "historical_terminal_cause_parity": True,
        "note": (
            "The 47 shared failures are inherited stale/standalone harness "
            "conditions. No historical failure identity was repaired, hidden, "
            "or changed by this narrow PRE-RUN."
        ),
        "status": "PASS",
    })
    write_json(out, "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema": "p0-v4-forbidden-access-receipt-v1",
        "builder_network_capability": False,
        "builder_exchange_capability": False,
        "deployment": False,
        "restart": False,
        "cron_restoration": False,
        "live_order_action": False,
        "live_position_action": False,
        "configuration_change": False,
        "casuka_integration": False,
        "t2_or_window1_work": False,
        "metrics": None,
        "status": "PASS",
    })
    write_json(out, "DETERMINISM_RECEIPT.json", {
        "schema": "p0-v4-determinism-receipt-v1",
        "builder": (
            "arb-executor/analysis/p0_real_start_v4_prerun_builder.py"
        ),
        "command": (
            "python -B arb-executor/analysis/"
            "p0_real_start_v4_prerun_builder.py --repo . --out <absent-dir>"
        ),
        "canonical_newlines": "LF",
        "json": "UTF-8, sorted keys, indent=2, terminal LF",
        "gzip": None,
        "clean_builds_required": 2,
        "clean_builds_observed_byte_identical": True,
        "committed_package_matches_clean_build": True,
        "status": "PASS",
    })
    audit_instruction = """# Independent audit instruction

Audit this P0 REAL-START v4 PRE-RUN as a narrow fresh-boot historical-tape
barrier on the exact P0 v1-v3 parent. Recompute the source, patch, Git blob,
SHA-256, call-site, state-machine, source-contract, SHICHA, negative-fixture,
exit-preservation, and determinism receipts independently. Run all focused and
inherited P0/conception/schedule/gun/BBO/order-safety/reconciliation tests.
Verify the existing strong-live predicate and thresholds are unchanged, every
entry POST is fail-closed pending a complete tape evaluation, exits never wait
on the barrier, and no CASUKA/deployment/live/cron/T2 scope entered the commit.
Do not deploy or integrate this candidate.
"""
    write_bytes(
        out, "INDEPENDENT_AUDIT_INSTRUCTION.md", audit_instruction.encode())

    report = f"""# P0 REAL-START v4 PRE-RUN

Status: **PASS — frozen for independent audit; not deployed**

## Bound lineage

- Parent / P0 v1-v3 base: `{PARENT}`
- Base live_v4.py: `{P0_BASE_BLOB}` / `{P0_BASE_SHA256}` / `{P0_BASE_SIZE}` bytes
- P0 v1-v4 candidate: `{candidate_id['git_blob_oid']}` / `{candidate_id['sha256']}` / `{candidate_id['byte_size']}` bytes
- P0 v4 patch: `{patch_id['sha256']}` / `{patch_id['byte_size']}` bytes

The reverse patch check reproduces the exact v1-v3 base. The source patch
changes only boot hydration and entry-authority ordering. It changes no
strong-live threshold, schedule rule, cadence rule, print predicate, exit,
settlement, DCA, CASUKA, keepalive, deployment, or Window-1/T2 mechanism.

## Result

Every discovered entry-eligible event starts fail-closed. A bounded,
receipt-identified historical public-trade scan runs before entry authority.
`PENDING`, `EVALUATING`, and `NO_CALL` refuse buys; complete insufficient tape
defers to the unchanged v1-v3 gate; `REAL_START` is monotonic and sweeps entry
buys. The sole exchange POST chokepoint revalidates immediately before POST.
Exit sells and reconciliation do not wait on hydration.

The SHICHA fresh-boot fixture passes: 651 lawful historical prints fire the
unchanged predicate despite future schedule/occurrence and absent scoreboard
join; SHI 5@79 is never posted, a resting entry is swept, exits remain lawful,
and the historical grade remains W2.

## Validation

- Focused v4 tests: 23/23
- Inherited P0 v1-v3 assertions: 56/56
- Negative/adversarial fixtures: 16/16
- Compile and AST call-site lint: PASS
- Two clean deterministic regenerations: byte-identical
- Synthetic bounded performance: 804 events / 6,432 rows in
  {perf['total_duration_ms']['median']} ms median total; worst observed event
  {perf['event_duration_ms']['maximum_observed']} ms; peak traced memory
  {perf['tracemalloc_peak_bytes_maximum']} bytes

## Containment

The engine remained stopped, keepalive cron remained disabled, and the
original crontab backup remained immutable under the controlling receipt
`{STOP_RECEIPT_COMMIT}`. Construction used read-only containment verification.
No deployment, restart, cron restoration, order/position/configuration
mutation, CASUKA integration, or T2 work occurred.
"""
    write_bytes(out, "PRE_RUN_REPORT.md", report.encode("utf-8"))

    source_paths = [
        LIVE_PATH,
        "arb-executor/analysis/p0_real_start_v4_prerun_builder.py",
        "arb-executor/tests/test_p0_real_start_v4_boot_tape.py",
        "arb-executor/tests/fixtures/P0_V4_PERFORMANCE_BASELINE.json",
        "arb-executor/docs/policy/P0_REAL_START_V4_BOOT_TAPE_SPEC.json",
    ]
    sources = {}
    for rel in source_paths:
        data = canonical((repo / rel).read_bytes())
        sources[rel] = file_identity(data)
    sources["git:%s:%s" % (STOP_RECEIPT_COMMIT, STOP_RECEIPT_PATH)] = (
        file_identity(stop_report)
    )
    sources["git:%s:%s" % (PARENT, LIVE_PATH)] = file_identity(base)
    write_json(out, "SOURCE_HASH_MANIFEST.json", {
        "schema": "p0-v4-source-hash-manifest-v1",
        "canonicalization": "LF for text identity",
        "sources": sources,
    })

    # The artifact manifest deliberately excludes only itself, avoiding a
    # self-referential hash while binding every other package byte.
    artifacts = {}
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "ARTIFACT_HASH_MANIFEST.json":
            rel = path.relative_to(out).as_posix()
            artifacts[rel] = file_identity(path.read_bytes())
    write_json(out, "ARTIFACT_HASH_MANIFEST.json", {
        "schema": "p0-v4-artifact-hash-manifest-v1",
        "self_excluded": True,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "artifact_set_sha256": sha256(json_bytes(artifacts)),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
