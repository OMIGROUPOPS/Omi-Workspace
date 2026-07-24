#!/usr/bin/env python3
"""Freeze and package the Round-2 start ledger for independent review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "window1-start-truth-round2-freeze-v1"
EXPECTED_D = 804
EXPECTED_POSITIVE = 718
EXPECTED_EXACT = 687
EXPECTED_CLEAN = 31
EXPECTED_NEW_EXACT = 453
EXPECTED_STRICT_DUALS = 7
BASE_COMMIT = "224417da642a9f378a0d83f76edffe9890cb4a6f"


class FinalizeError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizeError(f"expected object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
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


def count_jsonl(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(bool(line.strip()) for line in handle)


def report(results: dict[str, Any]) -> str:
    witnesses = "\n".join(
        f"- {row['event_id']}: {row['combined_entry_cost_cents']:.0f} "
        f"cents; under par = {row['combined_entry_cost_under_par']}"
        for row in results["historical_witnesses"][
            "strict_window1_dual_events"
        ]
    )
    precision = results["start_gate"]["precision_counts"]
    return f"""# Window-1 Start-Truth Recovery Round 2 — frozen review package

## Start gate — PASS

- D = {results['D']}
- exact starts = {precision['exact']}
- clean causal intervals = {precision['clean_interval']}
- positive-capable population = {results['start_gate']['positive_capable_population']}
- timing-blocked population = {results['start_gate']['timing_blocked_population']}
- required = {results['start_gate']['required']}
- margin = {results['start_gate']['margin']}
- newly recovered exact starts = {results['start_gate']['newly_recovered_exact']}
- higher-precedence conflicts blocked = {results['start_gate']['higher_precedence_conflicts_blocked']}

The frozen 234 exact starts and 31 clean intervals from V3 remain intact.
Round 2 targeted only the prior 539-event residual.  The new provider clocks
required an exact two-player, tournament-class/name, date, match-ID, and
completed-result crosswalk.  Thirty-eight WTA-125/ITF same-city collisions
were rejected.  Eleven otherwise valid clocks remain contradictory because
a higher-precedence raw milestone receipt said `not_started` at or after the
result clock.

## Historical witness re-adjudication

- historical dual exact-five witnesses = {results['historical_witnesses']['historical_dual_exact_five_events']}
- strict Window-1 dual witnesses under the frozen V4 ledger = {results['historical_witnesses']['strict_window1_duals']}
- dual witnesses with a receipt-proven post-start leg = {results['historical_witnesses']['receipt_proven_post_start_duals']}
- exact-five filled legs conserved = {results['historical_witnesses']['lifecycle_conservation']['exact_five_filled_legs']}
- other-quantity filled legs conserved = {results['historical_witnesses']['lifecycle_conservation']['other_quantity_filled_legs']}
- exact nonfills conserved = {results['historical_witnesses']['lifecycle_conservation']['exact_nonfills']}
- legitimately censored legs conserved = {results['historical_witnesses']['lifecycle_conservation']['lifecycle_censored_legs']}
- ten-contract overfill outside exact-five = {results['historical_witnesses']['ten_contract_overfill_outside_exact_five']}

{witnesses}

This re-adjudication changes no placement, cancellation, fill, quantity, or
price.  It is not candidate scoring and tests no alternative policy.

## Stop condition

The start gate passed, so the immutable ledger and receipts are frozen here
for independent review.  The six-family/24-policy development runner remains
unchanged and unscored.  No holdout was opened.  No production, `live_v4`,
configuration, order, position, Window 2, exit, settlement, or DCA surface
was modified.
"""


def run(args: argparse.Namespace) -> int:
    output = Path(args.output).resolve()
    repo = Path(args.repo).resolve()
    preflight_path = Path(args.preflight).resolve()
    acquisition_path = Path(args.acquisition_manifest).resolve()
    summary_path = output / "REAL_START_SUMMARY_V4.json"
    ledger_path = output / "REAL_START_LEDGER_V4.jsonl"
    crosswalk_path = output / "START_CROSSWALK_V4.jsonl"
    conflict_path = output / "START_CONFLICT_LEDGER_V4.jsonl"
    evidence_path = output / "START_EVENT_EVIDENCE_V4.jsonl"
    source_path = output / "START_SOURCE_EXHAUSTION_V4.json"
    historical_path = output / "HISTORICAL_START_RULING_SUMMARY.json"
    summary = read_json(summary_path)
    historical = read_json(historical_path)
    precision = summary["precision_counts"]
    if not (
        summary["D"] == EXPECTED_D
        and summary["positive_capable_population"] == EXPECTED_POSITIVE
        and precision["exact"] == EXPECTED_EXACT
        and precision["clean_interval"] == EXPECTED_CLEAN
        and summary["newly_recovered_exact"] == EXPECTED_NEW_EXACT
        and summary["start_gate_pass"] is True
        and historical["newly_recovered_historical_strict_window1_duals"]
        == EXPECTED_STRICT_DUALS
        and historical["historical_dual_exact_five_events"] == 31
        and historical["ten_contract_overfill_outside_exact_five"] == 1
    ):
        raise FinalizeError("Round-2 frozen expectations changed")
    if not (
        count_jsonl(ledger_path) == EXPECTED_D
        and count_jsonl(evidence_path) == EXPECTED_D
        and count_jsonl(crosswalk_path) == 539
        and historical["candidate_policy_scoring_performed"] is False
    ):
        raise FinalizeError("artifact denominator or scoring law changed")
    preflight = read_json(preflight_path)
    if not (
        preflight["family_count"] == 6
        and preflight["policy_count"] == 24
        and preflight["candidate_scoring_performed"] is False
        and preflight["candidate_results_opened"] is False
        and preflight["holdout_opened"] is False
    ):
        raise FinalizeError("development preflight is no longer frozen")
    rulings = historical["ruling_counts"]
    exact_five_filled = sum(
        rulings.get(key, 0) for key in [
            "historical_exact_five_window1_fill",
            "historical_receipt_proven_post_start_fill",
            "historical_exact_five_timing_censored",
        ]
    )
    if not (
        exact_five_filled == 258
        and rulings["historical_other_quantity_fill"] == 12
        and rulings["historical_exact_nonfill"] == 870
        and rulings["historical_lifecycle_censored"] == 468
        and sum(rulings.values()) == 1608
    ):
        raise FinalizeError("historical lifecycle conservation changed")
    code_paths = [
        repo / "arb-executor/analysis/window1_start_truth_round2_acquire.py",
        repo / "arb-executor/analysis/window1_start_truth_round2.py",
        repo / "arb-executor/analysis/window1_start_replay_adjudication.py",
        repo / "arb-executor/analysis/window1_start_truth_round2_finalize.py",
        repo / "arb-executor/tests/test_window1_start_truth_round2.py",
    ]
    freeze = {
        "schema_version": VERSION,
        "source_base_commit": BASE_COMMIT,
        "branch": "codex/window1-definition",
        "D": EXPECTED_D,
        "ledger": {
            "path": "REAL_START_LEDGER_V4.jsonl",
            "bytes": ledger_path.stat().st_size,
            "rows": count_jsonl(ledger_path),
            "sha256": sha256_file(ledger_path),
        },
        "start_gate": {
            "required": 603,
            "positive_capable_population": EXPECTED_POSITIVE,
            "pass": True,
        },
        "inputs": {
            "baseline_v3_ledger_sha256": summary["baseline"][
                "ledger_sha256"
            ],
            "acquisition_manifest_sha256": sha256_file(acquisition_path),
            "preflight_sha256": sha256_file(preflight_path),
            "crosswalk_sha256": sha256_file(crosswalk_path),
            "source_inventory_sha256": sha256_file(source_path),
            "published_lifecycle_ledger_sha256": historical["inputs"][
                "published_leg_ledger"
            ]["sha256"],
        },
        "code_sha256": {
            str(path.relative_to(repo)).replace("\\", "/"): sha256_file(path)
            for path in code_paths
        },
        "blindness": summary["extraction_law"],
        "development_runner": {
            "family_count": 6,
            "policy_count": 24,
            "candidate_scoring_performed": False,
            "candidate_results_opened": False,
            "holdout_opened": False,
        },
        "private_raw_responses_committed": False,
    }
    freeze_path = output / "START_LEDGER_FREEZE_V4.json"
    write_json(freeze_path, freeze)
    results = {
        "schema_version": VERSION,
        "D": EXPECTED_D,
        "source_base_commit": BASE_COMMIT,
        "start_gate": {
            "precision_counts": precision,
            "positive_capable_population": EXPECTED_POSITIVE,
            "timing_blocked_population": (
                summary["timing_blocked_population"]
            ),
            "required": 603,
            "margin": summary["start_gate_margin"],
            "newly_recovered_exact": EXPECTED_NEW_EXACT,
            "higher_precedence_conflicts_blocked": summary[
                "higher_precedence_conflict_blocked"
            ],
            "pass": True,
        },
        "historical_witnesses": {
            "historical_dual_exact_five_events": historical[
                "historical_dual_exact_five_events"
            ],
            "strict_window1_duals": historical[
                "newly_recovered_historical_strict_window1_duals"
            ],
            "receipt_proven_post_start_duals": historical[
                "historical_dual_events_with_receipt_proven_post_start_leg"
            ],
            "strict_window1_dual_events": historical[
                "newly_recovered_historical_dual_events"
            ],
            "lifecycle_conservation": {
                "legs": 1608,
                "exact_five_filled_legs": exact_five_filled,
                "strict_window1_exact_five_legs": rulings[
                    "historical_exact_five_window1_fill"
                ],
                "receipt_proven_post_start_filled_legs": rulings[
                    "historical_receipt_proven_post_start_fill"
                ],
                "timing_censored_exact_five_legs": rulings[
                    "historical_exact_five_timing_censored"
                ],
                "other_quantity_filled_legs": rulings[
                    "historical_other_quantity_fill"
                ],
                "exact_nonfills": rulings[
                    "historical_exact_nonfill"
                ],
                "lifecycle_censored_legs": rulings[
                    "historical_lifecycle_censored"
                ],
            },
            "ten_contract_overfill_outside_exact_five": historical[
                "ten_contract_overfill_outside_exact_five"
            ],
        },
        "frozen_runner": freeze["development_runner"],
        "candidate_scoring_run": False,
        "tuning_run": False,
        "holdout_opened": False,
        "production_modified": False,
    }
    results_path = output / "FINAL_RESULTS.json"
    report_path = output / "FINAL_REPORT.md"
    write_json(results_path, results)
    report_path.write_text(
        report(results), encoding="utf-8", newline="\n"
    )
    artifact_paths = sorted(
        path for path in output.iterdir()
        if path.is_file() and path.name != "ARTIFACT_MANIFEST.json"
    )
    manifest = {
        "schema_version": (
            "window1-start-truth-round2-artifact-manifest-v1"
        ),
        "D": EXPECTED_D,
        "artifact_count": len(artifact_paths),
        "artifacts": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in artifact_paths
        },
        "manifest_self_hash_excluded": True,
        "private_raw_responses_committed": False,
        "candidate_scoring_performed": False,
        "holdout_opened": False,
    }
    write_json(output / "ARTIFACT_MANIFEST.json", manifest)
    print(json.dumps({
        "D": EXPECTED_D,
        "positive": EXPECTED_POSITIVE,
        "start_gate_pass": True,
        "strict_historical_duals": EXPECTED_STRICT_DUALS,
        "ledger_sha256": freeze["ledger"]["sha256"],
        "artifact_count": manifest["artifact_count"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--output", required=True)
    result.add_argument("--preflight", required=True)
    result.add_argument("--acquisition-manifest", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
