#!/usr/bin/env python3
"""Freeze the mechanically bound one-shot corrected Window-1 replay."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "arb-executor" / "analysis"))

from window1_corrected_replay import (  # noqa: E402
    frozen_logical_paths,
    read_json,
    sha256_file,
    write_json,
)


VERSION = "window1-corrected-freeze-v1"
CALIBRATION_MANIFEST = (
    REPO / ".claude" / "window1_calibration_20260723"
    / "CALIBRATION_EVIDENCE_MANIFEST.json"
)
EXTRA_INPUTS = [
    "corrected_replay_runner",
    "corrected_candidate",
    "policy_allowlist",
    "execution_adapter",
    "metric_contract",
    "calibration_adapter",
    "feature_matrix",
    "public_true_print_tape",
    "recut_cells",
    "micmay_forensic",
    "micmay_manifest",
    "independent_cross_review",
]


class FreezeError(RuntimeError):
    pass


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def git_status() -> str:
    return subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=REPO, text=True
    )


def sanitized_locator(path: Path, private: bool) -> str:
    if private:
        return f"external-private:{path.name}"
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return f"external-evidence:{path.name}"


def runtime_paths(args: argparse.Namespace) -> dict[str, Path]:
    return {
        name: Path(value).resolve()
        for name, value in vars(args).items()
        if name not in {"output", "code_sha"} and value is not None
    }


def run(args: argparse.Namespace) -> int:
    output = Path(args.output).resolve()
    if output.exists():
        raise FreezeError("freeze output already exists")
    if git_status():
        raise FreezeError(
            "working tree must be clean before the code SHA is frozen"
        )
    code_sha = args.code_sha or git_head()
    if code_sha != git_head():
        raise FreezeError("code SHA must equal current HEAD at freeze time")
    runtime = runtime_paths(args)
    logical_paths = frozen_logical_paths(runtime)
    calibration = read_json(CALIBRATION_MANIFEST)
    base = calibration.get("inputs") or []
    if len(base) != 18:
        raise FreezeError(
            f"calibration input count moved from 18 to {len(base)}"
        )
    inputs: list[dict[str, Any]] = []
    for expected in base:
        logical = str(expected["logical_source"])
        path = logical_paths.get(logical)
        if path is None or not path.is_file():
            raise FreezeError(f"missing calibration input: {logical}")
        actual = sha256_file(path)
        if actual != expected["sha256"]:
            raise FreezeError(
                f"calibration input hash moved: {logical}: {actual}"
            )
        private = bool(expected.get("private"))
        inputs.append({
            "logical_source": logical,
            "sha256": actual,
            "bytes": path.stat().st_size,
            "private": private,
            "locator": sanitized_locator(path, private),
            "calibration_gate_input": True,
        })
    private_extra = {
        "public_true_print_tape",
    }
    for logical in EXTRA_INPUTS:
        path = logical_paths[logical]
        if not path.is_file():
            raise FreezeError(f"missing corrected input: {logical}")
        private = logical in private_extra
        inputs.append({
            "logical_source": logical,
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "private": private,
            "locator": sanitized_locator(path, private),
            "calibration_gate_input": False,
        })
    if any(
        "holdout" in str(item).lower()
        for item in inputs
    ):
        raise FreezeError("holdout input refused")
    candidate = read_json(runtime["candidate"])
    allowlist = read_json(runtime["allowlist"])
    adapter = read_json(runtime["adapter"])
    metric = read_json(runtime["metric_contract"])
    if candidate.get("holdout_inputs") != []:
        raise FreezeError("candidate has holdout inputs")
    if allowlist.get("proxy_substitution_allowed") is not False:
        raise FreezeError("allowlist permits proxy substitution")
    if (adapter.get("laws") or {}).get("aim_v2") != "excluded":
        raise FreezeError("adapter does not exclude AIM_V2")
    if metric.get("D") != 804:
        raise FreezeError("metric denominator changed")
    by_logical = {
        item["logical_source"]: item for item in inputs
    }
    receipt = {
        "schema_version": VERSION,
        "frozen": True,
        "code_sha": code_sha,
        "adapter_id": adapter["adapter_id"],
        "adapter_sha256": by_logical["execution_adapter"]["sha256"],
        "policy_allowlist": {
            "sha256": by_logical["policy_allowlist"]["sha256"],
            "allowed_policy_ids": allowlist["allowed_policy_ids"],
            "allowed_execution_components": (
                allowlist["allowed_execution_components"]
            ),
            "forbidden_policy_ids": allowlist["forbidden_policy_ids"],
            "forbidden_execution_components": (
                allowlist["forbidden_execution_components"]
            ),
        },
        "candidate_spec_sha256": by_logical[
            "corrected_candidate"
        ]["sha256"],
        "metric_contract_sha256": by_logical[
            "metric_contract"
        ]["sha256"],
        "causal_clock_source_hashes": {
            "private_orders": by_logical["orders"]["sha256"],
            "private_fills": by_logical["fills"]["sha256"],
            "private_lifecycles": by_logical[
                "private_lifecycles"
            ]["sha256"],
            "causal_nonplacements": by_logical["decisions"]["sha256"],
            "real_start_ledger": by_logical[
                "real_start_ledger"
            ]["sha256"],
        },
        "calibration_gate_input_count": 18,
        "total_input_count": len(inputs),
        "inputs": inputs,
        "prohibited_input_sha256": (
            allowlist["prohibited_input_sha256"]
        ),
        "aim_v2_consumed": False,
        "proxy_substitution_allowed": False,
        "D": 804,
        "development_dates_utc_inclusive": [
            "2026-07-12",
            "2026-07-20",
        ],
        "execution_limit": 1,
        "holdout_inputs": [],
        "window2_exit_settlement_dca_inputs": False,
    }
    write_json(output, receipt)
    print(json.dumps({
        "frozen": True,
        "code_sha": code_sha,
        "calibration_gate_input_count": 18,
        "total_input_count": len(inputs),
        "candidate_spec_sha256": receipt["candidate_spec_sha256"],
        "adapter_sha256": receipt["adapter_sha256"],
        "metric_contract_sha256": receipt["metric_contract_sha256"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    private = Path.home() / "OMI-Window1-private" / "calibration-v1"
    fit_local = Path.home() / "OMI-Window1-private" / "fit-local"
    documents = REPO / "arb-executor" / "docs" / "research" / "window1"
    calibration = REPO / ".claude" / "window1_calibration_20260723"
    fit = REPO / ".claude" / "window1_20260721"
    result = argparse.ArgumentParser()
    result.add_argument("--output", required=True)
    result.add_argument("--code-sha")
    result.add_argument(
        "--candidate",
        default=documents / "WINDOW1_CORRECTED_CANDIDATE.json",
    )
    result.add_argument(
        "--allowlist",
        default=documents / "WINDOW1_POLICY_ALLOWLIST.json",
    )
    result.add_argument(
        "--adapter",
        default=documents / "WINDOW1_OS_EXECUTION_ADAPTER.json",
    )
    result.add_argument(
        "--metric-contract",
        default=documents / "WINDOW1_CORRECTED_METRIC_CONTRACT.json",
    )
    result.add_argument(
        "--calibration-adapter",
        default=calibration / "WINDOW1_OS_RESEARCH_ADAPTER.json",
    )
    result.add_argument(
        "--events", default=private / "events.jsonl"
    )
    result.add_argument(
        "--expected-legs",
        default=fit / "EVENT_LEG_LIFECYCLE_LEDGER.jsonl",
    )
    result.add_argument(
        "--starts",
        default=fit / "REAL_START_LEDGER.jsonl",
    )
    result.add_argument(
        "--orders", default=private / "orders.private.jsonl"
    )
    result.add_argument(
        "--fills", default=private / "api_fills.private.jsonl"
    )
    result.add_argument(
        "--lifecycles", default=private / "lifecycle.private.jsonl"
    )
    result.add_argument(
        "--decisions", default=fit / "CAUSAL_DECISIONS.sanitized.jsonl"
    )
    result.add_argument(
        "--feature-matrix", default=fit / "WINDOW1_FEATURE_MATRIX.jsonl"
    )
    result.add_argument(
        "--recut-cells",
        default=REPO / ".claude" / "seqfloor_20260708"
        / "recut_cells.json",
    )
    result.add_argument(
        "--public-prints", default=fit_local / "prints.jsonl"
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
