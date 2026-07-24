#!/usr/bin/env python3
"""Mechanical preflight for development-only Window-1 OS-family tuning.

The start gate is evaluated before any market tape, candidate result, or
outcome input can be opened.  This lane intentionally exposes only contract
validation and freeze construction while the gate is below 603.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping


VERSION = "window1-os-family-tuning-preflight-v1"
D = 804
START_GATE = 603
UTC = dt.timezone.utc
PROHIBITED_AIM_SHA = (
    "6183ddec56eaab2ad48432aa7c802ea6265e608fa26cdd960"
    "aa1dde866824356"
)
REQUIRED_EXCLUSIONS = {
    "aim_v2",
    "pinnacle",
    "unproven_reconstructed_full_depth",
    "future_information",
    "window2",
    "exits",
    "settlement",
    "dca",
    "narrow_walk_law_proxy_substitution",
    "post_result_feature_or_parameter",
}


class TuningPreflightError(RuntimeError):
    pass


class StartGateFailed(TuningPreflightError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TuningPreflightError(f"expected object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_policy_ids(spec: Mapping[str, Any]) -> list[str]:
    output = []
    posture_suffix = {
        "park_at_own_divot": "park",
        "bounded_walk_with_nonself_chain": "walk",
    }
    response_suffix = {
        "hold_sibling_at_own_divot": "hold",
        "reaim_sibling_to_its_own_divot": "reaim",
    }
    generation = spec.get("candidate_generation") or {}
    for family in spec.get("families") or []:
        family_id = str(family.get("family_id") or "")
        for posture in generation.get("posture_values") or []:
            for response in (
                generation.get("first_fill_response_values") or []
            ):
                if posture not in posture_suffix:
                    raise TuningPreflightError(
                        f"unknown posture: {posture}"
                    )
                if response not in response_suffix:
                    raise TuningPreflightError(
                        f"unknown first-fill response: {response}"
                    )
                output.append(
                    f"{family_id}__{posture_suffix[posture]}"
                    f"__{response_suffix[response]}"
                )
    return output


def validate_contracts(
    candidate_spec: Mapping[str, Any],
    adapter: Mapping[str, Any],
    feature_allowlist: Mapping[str, Any],
    metric: Mapping[str, Any],
    holdout: Mapping[str, Any],
) -> dict[str, Any]:
    period = candidate_spec.get("development_period") or {}
    if period != {
        "start": "2026-07-12",
        "end": "2026-07-20",
        "D": D,
        "role": "development_only",
    }:
        raise TuningPreflightError("development period changed")
    expected = expected_policy_ids(candidate_spec)
    declared = candidate_spec.get("permitted_policy_ids") or []
    if declared != expected or len(declared) != 24:
        raise TuningPreflightError("policy allowlist is not exact")
    if set(candidate_spec.get("hard_exclusions") or []) != REQUIRED_EXCLUSIONS:
        raise TuningPreflightError("hard exclusions changed")
    ranges = candidate_spec.get("parameter_ranges") or {}
    generation = candidate_spec.get("candidate_generation") or {}
    if (
        ranges.get("free_numeric_parameters") != []
        or ranges.get("posture") != generation.get("posture_values")
        or ranges.get("first_fill_sibling_response")
        != generation.get("first_fill_response_values")
        or "no interpolation" not in str(ranges.get("numeric_values"))
    ):
        raise TuningPreflightError("parameter ranges changed")
    if PROHIBITED_AIM_SHA not in set(
        candidate_spec.get("prohibited_input_sha256") or []
    ):
        raise TuningPreflightError("AIM_V2 SHA is not prohibited")
    if (
        candidate_spec.get("missing_feature_censors_entire_event") is not False
        or candidate_spec.get("missing_feature_law")
        != "disable_only_that_feature_at_that_timestamp"
    ):
        raise TuningPreflightError("missing-feature law changed")
    laws = adapter.get("laws") or {}
    if (
        laws.get("silent_proxy_substitution_allowed") is not False
        or laws.get("missing_feature") != "disable_feature_only"
        or laws.get("schedule_can_prove_positive") is not False
        or laws.get("aim_v2") != "excluded"
    ):
        raise TuningPreflightError("adapter causal laws changed")
    allowed = set(feature_allowlist.get("allowed") or [])
    required_components = {
        component
        for family in candidate_spec.get("families") or []
        for component in family.get("required_components") or []
    }
    if not required_components.issubset(allowed):
        raise TuningPreflightError(
            "candidate requires a non-allowlisted feature"
        )
    if feature_allowlist.get("proxy_substitution_allowed") is not False:
        raise TuningPreflightError("proxy substitution became executable")
    if (
        metric.get("D") != D or metric.get("target_count") != START_GATE
        or metric.get("censored_event_counts_as_success") is not False
        or metric.get("conflation_allowed") is not False
    ):
        raise TuningPreflightError("metric contract changed")
    existing = holdout.get("existing_july_24_26_baseline_holdout") or {}
    if (
        existing.get("preserved") is not True
        or existing.get("opened") is not False
        or existing.get("automatically_reused") is not False
        or holdout.get("current_holdout_dates") != []
    ):
        raise TuningPreflightError("holdout declaration changed")
    return {
        "schema_version": VERSION,
        "contract_validation": "pass",
        "policy_count": len(declared),
        "family_count": len(candidate_spec.get("families") or []),
        "aim_v2_excluded": True,
        "pinnacle_excluded": True,
        "full_depth_excluded": True,
        "silent_proxy_substitution_allowed": False,
        "development_dates": ["2026-07-12", "2026-07-20"],
        "holdout_opened": False,
    }


def enforce_start_gate(summary: Mapping[str, Any]) -> dict[str, Any]:
    if summary.get("D") != D:
        raise TuningPreflightError("start ledger D changed")
    provable = int(summary.get("provable_positive_population") or 0)
    declared_pass = summary.get("start_gate_pass") is True
    actual_pass = provable >= START_GATE
    if declared_pass != actual_pass:
        raise TuningPreflightError("start gate receipt is inconsistent")
    receipt = {
        "required": START_GATE,
        "provable_positive_population": provable,
        "missing": max(0, START_GATE - provable),
        "pass": actual_pass,
    }
    if not actual_pass:
        raise StartGateFailed(compact(receipt))
    return receipt


def committed_blob_receipt(
    repo: Path,
    path: Path,
    commit: str,
) -> dict[str, Any]:
    relative = path.resolve().relative_to(repo).as_posix()
    try:
        oid = subprocess.check_output(
            ["git", "rev-parse", f"{commit}:{relative}"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        content = subprocess.check_output(
            ["git", "cat-file", "blob", oid], cwd=repo
        )
    except subprocess.CalledProcessError as exc:
        raise TuningPreflightError(
            f"freeze input is not committed: {relative}"
        ) from exc
    return {
        "path": relative,
        "git_blob_oid": oid,
        "sha256": hashlib.sha256(content).hexdigest(),
        "bytes": len(content),
        "hash_basis": "committed_git_blob_lf",
    }


def freeze_receipt(
    repo: Path,
    paths: Mapping[str, Path],
    commit: str,
) -> dict[str, Any]:
    resolved_commit = subprocess.check_output(
        ["git", "rev-parse", commit], cwd=repo
    ).decode().strip()
    inputs = {
        name: committed_blob_receipt(
            repo, path, resolved_commit
        )
        for name, path in paths.items()
    }
    return {
        "schema_version": VERSION,
        "frozen_at_utc": dt.datetime.now(UTC).isoformat(),
        "code_commit": resolved_commit,
        "hash_basis": "committed_git_blob_lf",
        "inputs": inputs,
        "candidate_spec_hash": inputs["candidate_spec"]["sha256"],
        "adapter_hash": inputs["adapter"]["sha256"],
        "causal_feature_allowlist_hash": inputs[
            "feature_allowlist"
        ]["sha256"],
        "fill_kernel_hash": inputs["fill_kernel"]["sha256"],
        "metric_contract_hash": inputs["metric_contract"]["sha256"],
        "prospective_holdout_declaration_hash": inputs[
            "prospective_holdout"
        ]["sha256"],
        "development_dates": ["2026-07-12", "2026-07-20"],
        "candidate_results_opened": False,
        "holdout_opened": False,
    }


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = {
        "candidate_spec": Path(args.candidate_spec).resolve(),
        "adapter": Path(args.adapter).resolve(),
        "feature_allowlist": Path(args.feature_allowlist).resolve(),
        "fill_kernel": Path(args.fill_kernel).resolve(),
        "metric_contract": Path(args.metric_contract).resolve(),
        "prospective_holdout": Path(
            args.prospective_holdout
        ).resolve(),
        "runner": Path(__file__).resolve(),
    }
    validation = validate_contracts(
        read_json(paths["candidate_spec"]),
        read_json(paths["adapter"]),
        read_json(paths["feature_allowlist"]),
        read_json(paths["metric_contract"]),
        read_json(paths["prospective_holdout"]),
    )
    freeze = freeze_receipt(repo, paths, args.hash_commit)
    start_summary_path = Path(args.start_summary).resolve()
    summary = read_json(start_summary_path)
    freeze["start_evidence"] = {
        "summary_sha256": sha256_file(start_summary_path),
        "ledger_sha256": summary.get("ledger_sha256"),
        "schema_version": summary.get("schema_version"),
        "policy_outcomes_examined_during_extraction": (
            (summary.get("extraction_law") or {}).get(
                "policy_outcomes_examined"
            )
        ),
    }
    try:
        gate = enforce_start_gate(summary)
    except StartGateFailed as exc:
        gate = json.loads(str(exc))
        result = {
            **validation,
            "start_gate": gate,
            "candidate_scoring_performed": False,
            "candidate_results_opened": False,
            "stop_reason": "start_gate_below_603",
            "freeze": freeze,
        }
        write_json(Path(args.output).resolve(), result)
        print(compact(result["start_gate"]))
        return 3
    result = {
        **validation,
        "start_gate": gate,
        "candidate_scoring_performed": False,
        "candidate_results_opened": False,
        "stop_reason": (
            "preflight_only; scoring backend may now be invoked by the "
            "separate development executor"
        ),
        "freeze": freeze,
    }
    write_json(Path(args.output).resolve(), result)
    print(compact(result["start_gate"]))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--candidate-spec", required=True)
    result.add_argument("--adapter", required=True)
    result.add_argument("--feature-allowlist", required=True)
    result.add_argument("--fill-kernel", required=True)
    result.add_argument("--metric-contract", required=True)
    result.add_argument("--prospective-holdout", required=True)
    result.add_argument("--start-summary", required=True)
    result.add_argument("--hash-commit", default="HEAD")
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
