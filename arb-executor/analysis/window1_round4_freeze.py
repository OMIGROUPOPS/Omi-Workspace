#!/usr/bin/env python3
"""Freeze Round-4 PRE-RUN manifests after score-free stream generation."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round4_instrument as r4


VERSION = "window1-round4-prerun-freeze-v1"
ANCESTRY = {
    "round3_prerun": "14e0e846e8922da98f656aef1f43d2c48da96ee7",
    "round3_package": "6daab089d1e6c11bd75a684b4e8609e815fec8f4",
    "round3_result_parent_and_control": (
        "754415bb81a328d671cd327f216d1753802442b1"
    ),
    "round3_results_audit": (
        "25735d9c9d9775a122da2a067962f45312aa62dc"
    ),
}


class FreezeError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_oid(repo: Path, path: Path) -> str:
    relative = str(path.relative_to(repo)).replace("\\", "/")
    return subprocess.check_output(
        [
            "git",
            "-C",
            str(repo),
            "hash-object",
            "--path",
            relative,
            str(path),
        ],
        text=True,
    ).strip()


def receipt(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise FreezeError(f"required freeze input absent: {relative}")
    return {
        "path": relative.replace("\\", "/"),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "git_blob_oid": git_blob_oid(repo, path),
        "availability": "available",
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_gzip_jsonl(
    path: Path, rows: Sequence[Mapping[str, Any]],
) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as zipped:
            with io.TextIOWrapper(
                zipped, encoding="utf-8", newline="\n"
            ) as handle:
                for row in rows:
                    handle.write(compact(row) + "\n")


def _stream_receipts(
    streams_path: Path,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    rows = []
    candidates = []
    events = []
    with gzip.open(streams_path, "rt", encoding="utf-8") as handle:
        for ordinal, line in enumerate(handle, start=1):
            wrapper = json.loads(line)
            encoded = compact(wrapper).encode("utf-8")
            candidate = str(wrapper["candidate_id"])
            event_id = str(wrapper["event_id"])
            rows.append({
                "ordinal": ordinal,
                "candidate_id": candidate,
                "event_id": event_id,
                "path": (
                    ".claude/window1_round4_prerun_20260725/"
                    "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
                    f"#L{ordinal}"
                ),
                "role": "frozen_score_free_candidate_event_stream",
                "bytes": len(encoded),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "stream_sha256": wrapper["stream"]["stream_sha256"],
                "scored": wrapper["stream"]["scored"],
                "metrics": wrapper["stream"]["metrics"],
            })
            candidates.append(candidate)
            events.append(event_id)
    return rows, candidates, events


def build(repo: Path, output: Path) -> None:
    capability = read_json(output / "ROUND4_REAL_CAPABILITY.json")
    diagnostics = read_json(output / "ROUND4_DIAGNOSTIC_RECEIPT.json")
    calibration = read_json(
        output / "CAUSAL_REFERENCE_CALIBRATION.json"
    )
    census = read_json(output / "ORACLE_FALSE_NEGATIVE_CENSUS.json")
    spec = r4.load_candidate_spec(repo)
    round3_bundle = read_json(
        repo
        / ".claude/window1_round3_execution_package_20260725/"
        "SCORING_INPUT_BUNDLE.json"
    )
    private_data_receipts = {
        "external_inputs": round3_bundle["external_inputs"],
        "market_cache_aggregate": round3_bundle[
            "market_cache_aggregate"
        ],
        "market_cache_files": round3_bundle["market_cache_files"],
        "frozen_event_leg_identities": round3_bundle[
            "frozen_event_leg_identities"
        ],
        "frozen_event_leg_identities_sha256": round3_bundle[
            "frozen_event_leg_identities_sha256"
        ],
        "source": (
            ".claude/window1_round3_execution_package_20260725/"
            "SCORING_INPUT_BUNDLE.json"
        ),
        "raw_private_data_committed": False,
    }
    streams_path = output / "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
    stream_rows, stream_candidates, stream_events = _stream_receipts(
        streams_path
    )
    expected_candidates = list(spec["candidate_ids"])
    if len(stream_rows) != 1608:
        raise FreezeError("Round-4 must freeze 1,608 candidate-event streams")
    if stream_candidates != expected_candidates * 804:
        # Streams are event-major, so the manifest order repeats per event.
        expected_order = [
            candidate
            for _ in range(804)
            for candidate in expected_candidates
        ]
        if stream_candidates != expected_order:
            raise FreezeError("candidate stream ordering changed")
    if any(
        row["scored"] is not False or row["metrics"] is not None
        for row in stream_rows
    ):
        raise FreezeError("performance result found in PRE-RUN stream")
    if len(set(stream_events)) != 804:
        raise FreezeError("D=804 stream event identities not conserved")

    stream_receipt_path = (
        output / "ROUND4_STREAM_RECEIPTS.jsonl.gz"
    )
    write_gzip_jsonl(stream_receipt_path, stream_rows)

    new_code = [
        (
            "arb-executor/analysis/window1_round4_instrument.py",
            "Round-4 policy instrument",
        ),
        (
            "arb-executor/analysis/window1_round4_prerun_builder.py",
            "score-free real-input stream builder",
        ),
        (
            "arb-executor/analysis/window1_round4_diagnostics.py",
            "oracle-separated diagnostic builder",
        ),
        (
            "arb-executor/analysis/window1_round4_freeze.py",
            "PRE-RUN manifest freezer",
        ),
        (
            "arb-executor/docs/research/window1/"
            "WINDOW1_ROUND4_CANDIDATES_V1.json",
            "exact two-candidate policy specification",
        ),
        (
            "arb-executor/tests/test_window1_round4_instrument.py",
            "focused causal actuator fixtures",
        ),
        (
            "arb-executor/tests/test_window1_round4_diagnostics.py",
            "oracle-separation and opportunity-ledger fixtures",
        ),
    ]
    frozen_inputs = [
        (
            ".claude/window1_start_guard_corrected_20260724/"
            "REAL_START_LEDGER_V5.jsonl",
            "frozen start-boundary ledger and guarded cutoffs",
        ),
        (
            ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl",
            "frozen 1,608-leg feature availability ledger",
        ),
        (
            ".claude/entrysurface_20260717/band_map_v1.json",
            "frozen macro birth-band map",
        ),
        (
            ".claude/entrysurface_20260717/divot_tables_v1.json",
            "frozen divot surfaces",
        ),
        (
            ".claude/entrysurface_20260717/drift_surfaces_v1.json",
            "frozen 12,170-leg drift/reach surfaces",
        ),
        (
            ".claude/seqfloor_20260708/recut_cells.json",
            "frozen dynamic recut cells",
        ),
        (
            ".claude/master_20260709/cohort.json",
            "frozen cohort n>=30 surfaces",
        ),
        (
            ".claude/trendpath/ORIENT_V1.json",
            "frozen orientation surface",
        ),
        (
            ".claude/trendpath/ATLAS_V1.json",
            "source-proved G9 atlas reach surface",
        ),
        (
            "arb-executor/analysis/window1_round2_scorer.py",
            "unchanged frozen scorer reserved for later authorization",
        ),
        (
            "arb-executor/docs/research/window1/"
            "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json",
            "unchanged D/C/PC/S/IC metric contract",
        ),
        (
            "arb-executor/docs/research/window1/"
            "WINDOW1_ROUND2_SCORER_CONTRACT_V1.json",
            "unchanged scorer contract",
        ),
    ]
    source_receipts = [
        receipt(repo, path, role) for path, role in frozen_inputs
    ]
    code_receipts = [
        receipt(repo, path, role) for path, role in new_code
    ]

    availability = {
        "schema_version": "window1-round4-source-availability-v1",
        "primary_fill_contract": spec["primary_fill_contract"],
        "git_source_receipts": source_receipts,
        "private_data_receipt_binding": {
            "inherited_round3_bundle": receipt(
                repo,
                ".claude/window1_round3_execution_package_20260725/"
                "SCORING_INPUT_BUNDLE.json",
                "audited private-input receipt authority",
            ),
            "external_inputs": private_data_receipts[
                "external_inputs"
            ],
            "market_cache_aggregate": private_data_receipts[
                "market_cache_aggregate"
            ],
            "market_cache_file_count": len(
                private_data_receipts["market_cache_files"]
            ),
            "market_cache_file_receipts_sha256": hashlib.sha256(
                compact(
                    private_data_receipts["market_cache_files"]
                ).encode("utf-8")
            ).hexdigest(),
            "event_leg_identity_count": len(
                private_data_receipts["frozen_event_leg_identities"]
            ),
            "event_leg_identities_sha256": private_data_receipts[
                "frozen_event_leg_identities_sha256"
            ],
            "raw_private_data_committed": False,
        },
        "available_and_bound": [
            {
                "family": "independent pair presence",
                "source": "frozen public BBO snapshots",
                "policy_effect": "independent per-leg maker order",
            },
            {
                "family": "true-print microdivot and recut",
                "source": "receipt-identifiable positive-size public prints",
                "policy_effect": "evidence-triggered recut only",
            },
            {
                "family": "chronological drift and fitted reach",
                "source": (
                    ".claude/entrysurface_20260717/"
                    "drift_surfaces_v1.json"
                ),
                "policy_effect": "lawful depth/posture; never skip",
            },
            {
                "family": "G9 atlas reach",
                "source": ".claude/trendpath/ATLAS_V1.json",
                "policy_effect": "p50 depth and advisory t_deep",
            },
            {
                "family": "orientation",
                "source": ".claude/trendpath/ORIENT_V1.json",
                "policy_effect": (
                    "latent posture; movement only on later print"
                ),
            },
            {
                "family": "cohort steering",
                "source": ".claude/master_20260709/cohort.json",
                "availability_law": (
                    "CALL only n>=30; otherwise NO_CALL and continue"
                ),
            },
            {
                "family": "BBO/top-five pressure",
                "source": "bound guarded-cache book receipts",
                "availability_law": (
                    "top-five used only where causal and present"
                ),
            },
            {
                "family": "own-order subtraction",
                "source": "frozen own-order fingerprints",
                "policy_effect": (
                    "subtract contributed volume; never self-confirm"
                ),
            },
            {
                "family": "displayed queue observation",
                "source": "bound causal BBO/top-five snapshots",
                "policy_effect": (
                    "placement input and sensitivity diagnostic only; "
                    "never changes primary qualifying-print fill"
                ),
            },
        ],
        "unavailable_not_proxied": [
            "sealed dual-divot pair policy",
            "Pinnacle",
            "bookmaker/FV",
            "proved full depth (top-five is not full depth)",
            "lawful independent shape mapping",
            "timestamped schedule revisions beyond bound schedule receipt",
        ],
        "optional_NO_CALL_suppresses_presence": False,
        "holdout_opened": False,
    }
    write_json(output / "ROUND4_SOURCE_BINDING_AVAILABILITY.json", availability)

    artifact_paths = [
        (
            ".claude/window1_round4_prerun_20260725/"
            "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz",
            "1,608 score-free candidate-event streams",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_STREAM_RECEIPTS.jsonl.gz",
            "per-stream immutable receipts",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_REAL_CAPABILITY.json",
            "real-input capability and distinctness proof",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_CANDIDATE_ORDER_DIFFERENCES.jsonl",
            "real-event candidate order differences",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_HEADROOM_DECISION_RECEIPTS.jsonl.gz",
            "causal headroom decision receipts",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "WINDOW1_OPPORTUNITY_LEDGER_01.jsonl.gz",
            "804-event score-separated opportunity ledger shard 1/2",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "WINDOW1_OPPORTUNITY_LEDGER_02.jsonl.gz",
            "804-event score-separated opportunity ledger shard 2/2",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "WINDOW1_OPPORTUNITY_LEDGER_MANIFEST.json",
            "ordered 804-event opportunity-ledger shard manifest",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "CAUSAL_REFERENCE_CALIBRATION.json",
            "causal b_i versus ex-post d_i diagnostic",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ORACLE_FALSE_NEGATIVE_CENSUS.json",
            "independent Round-3 eight-candidate oracle census",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_DIAGNOSTIC_RECEIPT.json",
            "oracle-separation and D conservation receipt",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_SOURCE_BINDING_AVAILABILITY.json",
            "source binding and unavailable-family disclosure",
        ),
    ]
    artifact_receipts = [
        receipt(repo, path, role) for path, role in artifact_paths
    ]

    execution_required_roles = {
        "1,608 score-free candidate-event streams",
        "per-stream immutable receipts",
        "source binding and unavailable-family disclosure",
    }
    execution_required_artifacts = [
        row for row in artifact_receipts
        if row["role"] in execution_required_roles
    ]
    diagnostic_audit_artifacts = [
        row for row in artifact_receipts
        if row["role"] not in execution_required_roles
    ]
    execution_inventory = {
        "schema_version": "window1-round4-later-execution-inventory-v1",
        "purpose": (
            "exact inventory for a separately authorized deterministic "
            "Round-4 package; this PRE-RUN is not an execution package"
        ),
        "candidate_ids_in_frozen_order": list(spec["candidate_ids"]),
        "D": 804,
        "target_PC": 603,
        "candidate_event_stream_count": 1608,
        "required_scoring_inputs": [
            *source_receipts,
            *execution_required_artifacts,
            receipt(
                repo,
                "arb-executor/docs/research/window1/"
                "WINDOW1_ROUND4_CANDIDATES_V1.json",
                "frozen two-candidate definition",
            ),
        ],
        "diagnostic_audit_artifacts_not_policy_or_scorer_inputs": (
            diagnostic_audit_artifacts
        ),
        "private_data_receipts_inherited_byte_identically": (
            private_data_receipts
        ),
        "diagnostic_oracle_inputs_reachable_from_policy": False,
        "diagnostic_oracle_inputs_reachable_from_scorer": False,
        "future_package_must_add": [
            "new never-used execution ID",
            "stdout-safe deterministic two-candidate grid runner",
            "exact one-run command",
            "absent execution-ID-specific result directory",
            "expected progress and output inventories",
            "hard one-attempt/no-retry/no-resume execution law",
        ],
        "execution_id": None,
        "execution_command": None,
        "benchmark_execution_authorized": False,
        "one_attempt_execution_discipline_preserved": True,
        "scorer_invocation_count": 0,
        "candidate_scoring_performed": False,
    }
    write_json(
        output / "ROUND4_EXECUTION_PACKAGE_INVENTORY.json",
        execution_inventory,
    )
    artifact_receipts.extend([
        receipt(
            repo,
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_EXECUTION_PACKAGE_INVENTORY.json",
            "later execution package inventory",
        )
    ])

    manifest = {
        "schema_version": VERSION,
        "ancestry": ANCESTRY,
        "development_scope": {
            "D": 804,
            "leg_identities": 1608,
            "candidate_count": 2,
            "candidate_event_streams": 1608,
            "dates": list(binding.DEV_DATES),
            "sealed_holdout_dates": [
                "2026-07-24", "2026-07-25", "2026-07-26"
            ],
            "target_PC": 603,
        },
        "candidate_ids_in_frozen_order": list(spec["candidate_ids"]),
        "metric_law": {
            "C": (
                "both legs exactly five inside lawful guarded Window 1"
            ),
            "PC": "C and combined Window-1-close delta strictly < 0",
            "S": "C and combined entry cost strictly < 100; diagnostic",
            "IC": (
                "C and both individual deltas strictly < 0; diagnostic"
            ),
            "S_gates_policy": False,
            "IC_gates_policy": False,
        },
        "headroom_law": spec["headroom_contract"],
        "primary_fill_law": spec["primary_fill_contract"],
        "guard_law_unchanged": {
            "official_exact_seconds": 60,
            "proxy_seconds": 900,
            "raw_realized_start_is_cutoff": False,
            "schedule_only_positive_allowed": False,
        },
        "source_receipts": source_receipts,
        "private_data_receipts": private_data_receipts,
        "code_receipts": code_receipts,
        "artifact_receipts": artifact_receipts,
        "stream_receipt_count": len(stream_rows),
        "stream_receipts_path": (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_STREAM_RECEIPTS.jsonl.gz"
        ),
        "stream_receipts_sha256": sha256_path(stream_receipt_path),
        "real_input_capability": capability,
        "diagnostic_separation": diagnostics,
        "calibration_threshold_tuned": calibration[
            "policy_threshold_tuned_from_calibration"
        ],
        "round3_census_reproduced": census[
            "supplied_selected_candidate_counts_reproduced"
        ],
        "benchmark_execution_authorized": False,
        "benchmark_execution_command": None,
        "candidate_scoring_performed": False,
        "performance_metrics_computed": False,
        "C_PC_S_IC_populated": False,
        "ranking_or_selection_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
    }
    write_json(output / "ROUND4_PRE_RUN_MANIFEST.json", manifest)

    final_paths = [
        *artifact_paths,
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_EXECUTION_PACKAGE_INVENTORY.json",
            "later execution inventory",
        ),
        (
            ".claude/window1_round4_prerun_20260725/"
            "ROUND4_PRE_RUN_MANIFEST.json",
            "authoritative Round-4 PRE-RUN manifest",
        ),
    ]
    artifact_manifest = {
        "schema_version": "window1-round4-artifact-manifest-v1",
        "artifacts": [
            receipt(repo, path, role) for path, role in final_paths
        ],
        "code": code_receipts,
        "frozen_inputs": source_receipts,
        "benchmark_execution_authorized": False,
        "scorer_invocations": 0,
    }
    write_json(
        output / "ROUND4_ARTIFACT_MANIFEST.json",
        artifact_manifest,
    )

    candidates = capability["candidate_summaries"]
    report = f"""# Window-1 Round-4 PRE-RUN

## Outcome

Round 4 is frozen as an implementation-only, score-free PRE-RUN on the
immutable July 12-20 D=804 development population. The audited Round-3 result
at `{ANCESTRY['round3_result_parent_and_control']}` remains the control and was
not rerun.

No benchmark, scorer, ranking, tuning, ablation, holdout query, or live /
production action occurred. Every one of the 1,608 candidate-event streams
has `scored=false` and `metrics=null`.

## Bound ancestry and metric contract

- Round-3 PRE-RUN: `{ANCESTRY['round3_prerun']}`
- Authorized Round-3 package: `{ANCESTRY['round3_package']}`
- Audited Round-3 result/control: `{ANCESTRY['round3_result_parent_and_control']}`
- Independent results audit: `{ANCESTRY['round3_results_audit']}`

`D=804` is immutable and the primary target remains `PC>=603`. `C` requires
both legs to fill exactly five inside their lawful guarded Window 1. `PC`
requires `C` and a strictly negative combined Window-1-close delta. `S`
(combined entry cost below 100) and `IC` (both individual deltas negative)
remain separate diagnostics and never gate policy. The official/exact guard
remains 60 seconds and the proxy guard remains 900 seconds; schedule-only
evidence cannot prove a positive completion.

## Frozen candidates

1. `{spec['candidate_ids'][0]}`
2. `{spec['candidate_ids'][1]}`

The pair-presence candidate isolates the causal headroom ladder. The full
drift-stack candidate uses the identical actuator and adds only source-bound
chronological drift, recognition, orientation, reach/atlas, cohort, BBO /
top-five, divot, recut, queue, and own-volume-subtraction mechanics. Macro
NO_CALL never suppresses pair presence; no clock-only repricing exists.

## Real-input capability

| Candidate | eligible | censored | both legs present | decisions | headroom actions | positive prints |
|---|---:|---:|---:|---:|---:|---:|
| `{candidates[0]['candidate_id']}` | {candidates[0]['eligible_event_count']} | {candidates[0]['censored_event_count']} | {candidates[0]['both_legs_present_event_count']} | {candidates[0]['order_decision_count']} | {candidates[0]['headroom_order_change_count']} | {candidates[0]['positive_size_print_count_consumed']} |
| `{candidates[1]['candidate_id']}` | {candidates[1]['eligible_event_count']} | {candidates[1]['censored_event_count']} | {candidates[1]['both_legs_present_event_count']} | {candidates[1]['order_decision_count']} | {candidates[1]['headroom_order_change_count']} | {candidates[1]['positive_size_print_count_consumed']} |

The two aggregate order-decision hashes differ on
`{candidates[0]['events_distinct_from_other_candidate']}` real D=804 events,
and the committed difference ledger supplies event-level witnesses. These
are capability and distinctness facts, not performance results.

## Actuator law

Any positive partial fill arms the sibling without creating a budget. The
first leg to reach exactly five freezes its VWAP and contemporaneous
own-subtracted external bid `R1`, giving `b1 = VWAP - R1`. With `F=0`, each
strictly later receipt-identified sibling print may improve at most one cent
and only while `b1 + b2 + F < 0`; integer `b2_max = -b1 - F - 1`.
Maker, positive-price, lawful-band, and exact-quantity guards remain
explicit. Queue surrender from order movement is logged, but estimated queue
never gates the primary fill. Combined cost/S and individual-delta/IC never
gate the actuator.

## Primary fill law

Exact five is the simulated order quantity. Each active order accumulates
chronological receipt-identified positive-size non-self executed volume at
its limit or better, across as many prints as necessary, until its remaining
quantity reaches zero. Displayed depth, full/top-five depth, one-print size,
strict trade-through, and estimated or unknown queue clearance are not fill
gates. Queue observations remain available for placement and a separately
labeled sensitivity diagnostic, but never alter or censor the primary fill.

## Oracle separation

`CAUSAL_REFERENCE_CALIBRATION.json`, the 804-event opportunity ledger, and
`ORACLE_FALSE_NEGATIVE_CENSUS.json` are diagnostic-only. Policy code imports
none of them. The opportunity ledger carries final C/PC/S/IC as null and
marks its ex-post columns as unreachable from policy. No threshold was tuned
from calibration. The independent Round-3 control census reproduces the
supplied 278 naked singles, 92 negative filled legs, allowance counts
75/68/59/40 at >=1/>=2/>=3/>=5 cents, 4-cent median allowance, 12 later
strict price reaches, and 53 post-cutoff sibling fills.

## Unavailable

The sealed dual-divot pair policy, Pinnacle, bookmaker/FV, proved full depth,
lawful independent shape mapping, and unbound schedule revisions remain
unavailable and unproxied.

## Stop condition

`ROUND4_EXECUTION_PACKAGE_INVENTORY.json` lists the exact inputs a later,
separately authorized package must bind. This PRE-RUN contains no execution
ID or executable benchmark command and authorizes no scoring.
"""
    (output / "ROUND4_PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    artifact_manifest["artifacts"].append(receipt(
        repo,
        ".claude/window1_round4_prerun_20260725/"
        "ROUND4_PRE_RUN_REPORT.md",
        "human-readable Round-4 PRE-RUN report",
    ))
    write_json(
        output / "ROUND4_ARTIFACT_MANIFEST.json",
        artifact_manifest,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze Round-4 PRE-RUN manifests."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir
        if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    build(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
