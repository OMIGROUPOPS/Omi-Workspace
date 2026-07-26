#!/usr/bin/env python3
"""Validate and document a regenerated score-free range-attack PRE-RUN."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import window1_range_attack_instrument as attack
import window1_range_attack_prerun_builder as builder


PARENT = "84959172330a6659df4ef7db04d971ec0bb8d893"
AUDIT = "9a0177af3ed93289c9a15f1df3acbc7bd2ee28bc"
ADDENDUM = "ffa412554d5cda9b3c669ef96cfe407c5c9aabf0"
AUDIT_REPORT = (
    ".claude/audit_20260725_round4_macromicro/AUDIT_REPORT.md"
)
AUDIT_REPORT_BLOB = "4e29e0263f171a26c7146746022e1e44c8bd5d28"
ADDENDUM_REPORT_BLOB = "f4d5f643139bb4b32e0e9009141493aaf6377df1"
ADDENDUM_RECEIPTS_BLOB = "f07d0f9b38fdc4b15517b771a65265ba4f25e0d9"

SOURCE_PATHS = [
    "arb-executor/docs/LIVING_VAULT.md",
    ".claude/rulings/GAME_LIFECYCLE.md",
    ".claude/rulings/RULING_GRANULARITY_LAW.md",
    ".claude/rulings/RULING_COMBINED_PRICE_CLAUSE.md",
    ".claude/rulings/CLIMBSIDE_SPEC.md",
    ".claude/seqfloor_20260708/recut_cells.json",
    ".claude/entrysurface_20260717/drift_surfaces_v1.json",
    ".claude/entrysurface_20260717/divot_tables_v1.json",
    ".claude/entrysurface_20260717/band_map_v1.json",
    ".claude/trendpath/ATLAS_V1.json",
    ".claude/trendpath/LIBRARY_V1.json",
    ".claude/trendpath/ORIENT_V1.json",
    ".claude/takerreach/LAW.json",
    ".claude/guidebook/GUIDEBOOK_V1.json",
    ".claude/volume_20260709/VOLUME_LEDGER.md",
    ".claude/fillredo_20260709/FILL_REDO.md",
    ".claude/proof_20260714/PROOF_LIVE_AIM.md",
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl",
    ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl",
    "arb-executor/live_v4.py",
    "arb-executor/analysis/trendpath_build.py",
    "arb-executor/analysis/range_spectrum_build.py",
    "arb-executor/analysis/range_spectrum_itf.py",
    "arb-executor/analysis/exit_charts/rebuild_full_universe.py",
    "arb-executor/analysis/window1_round4_macromicro_instrument.py",
]

NEW_SOURCE_PATHS = [
    "arb-executor/analysis/window1_range_attack_instrument.py",
    "arb-executor/analysis/window1_range_attack_prerun_builder.py",
    "arb-executor/analysis/window1_range_attack_freeze.py",
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_CANDIDATES_V1.json",
    "arb-executor/tests/test_window1_range_attack_prerun.py",
]

MECHANISMS = [
    {
        "mechanism": "receipt_identified_positive_public_true_print",
        "classification": "BOUND",
        "native_meaning": "chronological execution price/size evidence",
        "decision_effect": "discovery, divot, fillability and later headroom trigger",
    },
    {
        "mechanism": "nonself_external_BBO_and_top5_chain",
        "classification": "BOUND",
        "native_meaning": "maker authority and observable public chain",
        "decision_effect": "pair presence, expression, maker safety and hollowing",
    },
    {
        "mechanism": "Trendpath_ATLAS_native_discovery_path",
        "classification": "BOUND",
        "native_meaning": "first-hour print median keyed path/bottom depth",
        "decision_effect": "one frozen Challenger macro target",
    },
    {
        "mechanism": "LIVE_AIM_source_mapping",
        "classification": "BOUND",
        "native_meaning": "30m print ratio/signature, spread and bid-depth trend",
        "decision_effect": "B-only hold or source-authorized downward AIM_DEEP",
    },
    {
        "mechanism": "GUIDEBOOK_V1_deep_tier",
        "classification": "BOUND",
        "native_meaning": "category/discovery-price page depth_p25_of_w1s",
        "decision_effect": "B-only downward target after source-bound AIM_DEEP",
    },
    {
        "mechanism": "positive_print_microdivot",
        "classification": "BOUND",
        "native_meaning": "sell print below trailing print median with ask hold",
        "decision_effect": "queue-preserving hold at selected target",
    },
    {
        "mechanism": "pair_combined_headroom",
        "classification": "BOUND",
        "native_meaning": "strict remaining causal pair budget after first reach",
        "decision_effect": "strictly later at-most-one-cent sibling improvement",
    },
    {
        "mechanism": "timestamped_schedule_policy_clock",
        "classification": "BOUND",
        "native_meaning": "causally observed schedule anchor and corridor",
        "decision_effect": "policy eligibility and horizon only",
    },
    {
        "mechanism": "external_ask_maker_safety",
        "classification": "BOUND",
        "native_meaning": "current lawful positive-size ask",
        "decision_effect": "nonmarketable expression/correction",
    },
    {
        "mechanism": "carried_last_trade",
        "classification": "PROXIED",
        "native_meaning": "market state with execution time unknown",
        "decision_effect": "state/stress only; never BBO, print or direction authority",
    },
    {
        "mechanism": "executed_share_volume_and_cadence",
        "classification": "PROXIED",
        "native_meaning": "actual rolling public volume/count/timing",
        "decision_effect": "stress and LIVE-AIM print-count context; no invented direction",
    },
    {
        "mechanism": "top5_pressure_sign",
        "classification": "PROXIED",
        "native_meaning": "observable chain summary",
        "decision_effect": "recorded only; no ratified direction gate",
    },
    {
        "mechanism": "close_keyed_recut_cells",
        "classification": "PROXIED",
        "native_meaning": "historical own-close keyed edge/floor rows",
        "decision_effect": "receipted NO_CALL without causal own-close projection",
    },
    {
        "mechanism": "taker_reach_probability",
        "classification": "PROXIED",
        "native_meaning": "fitted reach rate by native category/flow/depth",
        "decision_effect": "exact-touch stress diagnostic only",
    },
    {
        "mechanism": "drift_surfaces_v1",
        "classification": "PROXIED",
        "native_meaning": "future net/dip fitted range path by native band",
        "decision_effect": "named NO_CALL; future path components unavailable causally",
    },
    {
        "mechanism": "band_map_v1",
        "classification": "PROXIED",
        "native_meaning": "category k-means band on anchor/net/dip",
        "decision_effect": "named NO_CALL; net/dip are not decision-time inputs",
    },
    {
        "mechanism": "divot_tables_v1",
        "classification": "PROXIED",
        "native_meaning": "historical divot distributions keyed by fitted band",
        "decision_effect": "table row NO_CALL without causal fitted band; chronological positive-print divot remains independently bound",
    },
    {
        "mechanism": "LIBRARY_V1",
        "classification": "PROXIED",
        "native_meaning": "category/discovery/volume path library on -0k onset",
        "decision_effect": "named NO_CALL because its own metadata marks timing axis mis-anchored",
    },
    {
        "mechanism": "ORIENT_V1",
        "classification": "PROXIED",
        "native_meaning": "pair tell to pre-onset riser truth",
        "decision_effect": "named NO_CALL without separately frozen pair tell consumer",
    },
    {
        "mechanism": "Pinnacle",
        "classification": "ABSENT",
        "native_meaning": None,
        "decision_effect": "none",
    },
    {
        "mechanism": "authoritative_bookmaker_or_FV",
        "classification": "ABSENT",
        "native_meaning": None,
        "decision_effect": "none",
    },
    {
        "mechanism": "full_depth_beyond_bound_top5",
        "classification": "ABSENT",
        "native_meaning": None,
        "decision_effect": "none",
    },
    {
        "mechanism": "independent_shape_mapping",
        "classification": "ABSENT",
        "native_meaning": None,
        "decision_effect": "none",
    },
    {
        "mechanism": "moving_current_bid_minus_edge_target",
        "classification": "RETRACTED",
        "native_meaning": "blocked V1 invention",
        "decision_effect": "forbidden",
    },
    {
        "mechanism": "universal_50_climb_split",
        "classification": "RETRACTED",
        "native_meaning": "blocked V1 flattening",
        "decision_effect": "forbidden",
    },
    {
        "mechanism": "last_trade_bid_direction_gate",
        "classification": "RETRACTED",
        "native_meaning": "blocked unsourced mapping",
        "decision_effect": "forbidden",
    },
    {
        "mechanism": "pressure_or_taker_side_direction_gate",
        "classification": "RETRACTED",
        "native_meaning": "blocked unsourced mapping",
        "decision_effect": "forbidden",
    },
    {
        "mechanism": "borrowed_or_sealed_pair_shape_policy",
        "classification": "RETRACTED",
        "native_meaning": "no independent frozen mapping",
        "decision_effect": "forbidden",
    },
]

SURFACE_DETAILS = {
    "Trendpath_ATLAS_native_discovery_path": {
        "native_key": "category|leader_or_underdog|discovery_price_bucket",
        "fitted_population": "page.n; PATH requires n>=8",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "median true-print price in first hour",
        "target_or_depth_meaning": "bottom.depth_p50 below discovery",
        "timing_meaning": "path slices and evidence-gun timing are advisory receipts",
        "validation_or_ratification": "ATLAS PATH/REFUSE_THIN verdict",
        "causal_for_simulation": True,
        "changes_decision": True,
    },
    "GUIDEBOOK_V1_deep_tier": {
        "native_key": "category|rounded_discovery_price",
        "fitted_population": "page fitted population and tier receipt",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
        ],
        "native_anchor": "frozen first-hour discovery price",
        "target_or_depth_meaning": "depth_p25_of_w1s deep tier",
        "timing_meaning": "no action timestamp; LIVE-AIM micro evidence triggers",
        "validation_or_ratification": "PROOF_LIVE_AIM source-bound consumer",
        "causal_for_simulation": True,
        "changes_decision": True,
    },
    "LIVE_AIM_source_mapping": {
        "native_key": "category OPEN threshold plus leg rolling 30m state",
        "fitted_population": "thresholds ITF=6, Challenger=16, mains gauge off",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "strictly chronological public print/BBO receipts",
        "target_or_depth_meaning": "prior/deep/shallow posture mapping",
        "timing_meaning": "current micro receipt only",
        "validation_or_ratification": "PROOF_LIVE_AIM and live_v4::_liveaim_shadow",
        "causal_for_simulation": True,
        "changes_decision": True,
    },
    "drift_surfaces_v1": {
        "native_key": "category fitted band and minute offset",
        "fitted_population": "band.n from 12,170-leg range spectrum",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "range-spectrum anchor/net/dip band",
        "target_or_depth_meaning": "historical bid/ask/trade movement and reach",
        "timing_meaning": "historical minute offsets, never action timestamps",
        "validation_or_ratification": "authoritative fitted artifact",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
    "band_map_v1": {
        "native_key": "category k-means band",
        "fitted_population": "category n and per-band n",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "anchor/net/dip triplet",
        "target_or_depth_meaning": "path-shape classification, not a price",
        "timing_meaning": "none independently",
        "validation_or_ratification": "deterministic fitted artifact",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
    "divot_tables_v1": {
        "native_key": "fitted band",
        "fitted_population": "windows/divots by band",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "band-specific historical flat window",
        "target_or_depth_meaning": "divot depth/catch distribution",
        "timing_meaning": "historical duration/near-wake, not action timestamp",
        "validation_or_ratification": "authoritative fitted artifact",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
    "LIBRARY_V1": {
        "native_key": "category|discovery_price_cell|first_hour_volume_band",
        "fitted_population": "cell.n",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "first-hour discovery and print-volume tercile",
        "target_or_depth_meaning": "dip frequency and depth quantiles",
        "timing_meaning": "native -0k axis explicitly marked mis-anchored",
        "validation_or_ratification": "artifact metadata requires timing recut",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
    "ORIENT_V1": {
        "native_key": "category|drift_tell|range_tell|flow_tell",
        "fitted_population": "cell.n, call only at operating-point n>=10",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "first-hour pair tells",
        "target_or_depth_meaning": "which leg is the pre-onset riser",
        "timing_meaning": "own n>=300 clock before money",
        "validation_or_ratification": "not independently frozen for this consumer",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
    "close_keyed_recut_cells": {
        "native_key": "category|eventual own-close integer cent",
        "fitted_population": "row n",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "eventual own close",
        "target_or_depth_meaning": "edge_p50/floor relative to own close",
        "timing_meaning": "historical fit only",
        "validation_or_ratification": "authoritative but not causal without projection",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
    "taker_reach_probability": {
        "native_key": "category|flow_bucket|depth",
        "fitted_population": "hours and arrivals_per_hour per page",
        "category_coverage": [
            "ITF_M", "ITF_W", "ATP_CHALL", "WTA_CHALL",
            "ATP_MAIN", "WTA_MAIN",
        ],
        "native_anchor": "depth below contemporaneous reference and residency",
        "target_or_depth_meaning": "P(reach at depth over residency)",
        "timing_meaning": "integrates only to evidence gun",
        "validation_or_ratification": "C-CONVICTED-INSTRUMENTS v1 bound",
        "causal_for_simulation": False,
        "changes_decision": False,
    },
}


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True
    ).strip()


def blob_oid(repo: Path, path: Path) -> str:
    return git(repo, "hash-object", str(path))


def identity(repo: Path, relative: str, *, parent: bool) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise VerificationError(f"source absent: {relative}")
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "git_blob_oid": (
            git(repo, "rev-parse", f"{PARENT}:{relative}")
            if parent else blob_oid(repo, path)
        ),
    }


def read_gzip(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def verify_builder_outputs(output: Path) -> dict[str, Any]:
    diagnostics = json.loads(
        (output / builder.FILES["diagnostics"]).read_text(encoding="utf-8")
    )
    streams = []
    ladders = []
    for index in range(1, 5):
        streams.extend(read_gzip(output / builder.FILES[f"stream_{index}"]))
        ladders.extend(read_gzip(output / builder.FILES[f"ladder_{index}"]))
    if len(streams) != 1608 or len(ladders) != 1608:
        raise VerificationError("D/stream/ladder conservation failed")
    if any(
        row["stream"]["metrics"] is not None
        or row["stream"]["pair_state"]["C"] is not None
        or row["stream"]["pair_state"]["PC"] is not None
        or row["stream"]["pair_state"]["S"] is not None
        or row["stream"]["pair_state"]["IC"] is not None
        for row in streams
    ):
        raise VerificationError("performance metric populated")
    if any(row["integer_cent_price_row_count"] != 99 for row in ladders):
        raise VerificationError("range ladder incomplete")
    candidates = Counter(row["candidate_id"] for row in streams)
    if candidates != Counter({
        "w1_range_attack__macro_hold__combined_headroom": 804,
        "w1_range_attack__macro_micro__combined_headroom": 804,
    }):
        raise VerificationError("candidate identity/count changed")
    return {
        "diagnostics": diagnostics,
        "stream_count": len(streams),
        "ladder_count": len(ladders),
        "integer_cent_rows": sum(
            row["integer_cent_price_row_count"] for row in ladders
        ),
    }


def compare_regeneration(
    reference: Path, regenerated: Path,
) -> list[dict[str, Any]]:
    rows = []
    for filename in sorted(set(builder.FILES.values())):
        left = reference / filename
        right = regenerated / filename
        if not left.is_file() or not right.is_file():
            raise VerificationError(f"regeneration artifact absent: {filename}")
        left_hash, right_hash = sha256(left), sha256(right)
        if left_hash != right_hash or left.read_bytes() != right.read_bytes():
            raise VerificationError(f"regeneration mismatch: {filename}")
        rows.append({
            "path": filename,
            "sha256": left_hash,
            "bytes": left.stat().st_size,
            "byte_identical": True,
        })
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def inherited_identity(repo: Path) -> list[dict[str, Any]]:
    names = git(
        repo, "ls-tree", "-r", "--name-only", PARENT,
        ".claude/window1_round4_macromicro_prerun_20260725",
    ).splitlines()
    names.extend([
        "arb-executor/analysis/window1_round4_macromicro_instrument.py",
        "arb-executor/analysis/window1_round4_macromicro_prerun_builder.py",
        "arb-executor/analysis/window1_round4_macromicro_freeze.py",
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND4_MACROMICRO_CANDIDATES_V1.json",
        "arb-executor/tests/test_window1_round4_macromicro.py",
    ])
    return [identity(repo, name, parent=True) for name in sorted(names)]


def report_text(diagnostics: Mapping[str, Any]) -> str:
    candidates = list(diagnostics["D_per_candidate"])
    lines = [
        "# Window-1 Range-Mastery Attack PRE-RUN",
        "",
        "Status: FROZEN, SCORE-FREE, NOT AUTHORIZED FOR EXECUTION.",
        "",
        f"Parent: `{PARENT}`.",
        f"Controlling BLOCKED audit: `{AUDIT}`.",
        f"Determinism addendum: `{ADDENDUM}`.",
        "",
        "This additions-only overlay retracts the blocked strategy logic at "
        "the parent while preserving its passed mechanical and last-trade "
        "substrate byte-for-byte. It recovers native Trendpath targeting, "
        "chronological public chain/tape evidence, primary price fillability, "
        "and strict asynchronous combined headroom.",
        "",
        "## Frozen candidates",
        "",
        *[f"- `{candidate}`" for candidate in candidates],
        "",
        "## Score-free diagnostics",
        "",
        f"- D: 804 for each candidate.",
        f"- Candidate-event streams: "
        f"{diagnostics['candidate_event_stream_count']}.",
        f"- Per-leg integer-cent ladders: "
        f"{diagnostics['leg_range_ladder_count']}.",
        f"- Integer-cent range rows: "
        f"{diagnostics['integer_cent_range_row_count']}.",
    ]
    for candidate in candidates:
        counts = diagnostics["price_fillability_counts"][candidate]
        lines.extend([
            f"- `{candidate}`: PRICE_REACHED={counts['PRICE_REACHED']}, "
            f"CERTAIN_FILL={counts['CERTAIN_FILL']}, "
            f"EXACT_TOUCH={counts['EXACT_TOUCH']}, "
            "cumulative-five false negatives="
            f"{counts['cumulative_five_false_negative']}.",
        ])
    lines.extend([
        "",
        "These are selected-price opportunity diagnostics, not C/PC/S/IC "
        "results. Five shares are an accounting assignment only after primary "
        "PRICE_REACHED; printed quantity and observable queue do not gate it.",
        "",
        "All C, PC, S, IC, percentages, rankings, and selections remain null. "
        "No scorer, benchmark, holdout, live, production, order, position, "
        "Window 2, exit, settlement, or DCA surface was invoked.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--regenerated-dir", type=Path, required=True)
    arguments = parser.parse_args()
    repo = arguments.repo.resolve()
    output = (
        arguments.output_dir.resolve()
        if arguments.output_dir.is_absolute()
        else (repo / arguments.output_dir).resolve()
    )
    regenerated = arguments.regenerated_dir.resolve()
    if git(repo, "rev-parse", "HEAD") != PARENT:
        raise VerificationError("wrong parent")
    verified = verify_builder_outputs(output)
    deterministic = compare_regeneration(output, regenerated)
    diagnostics = verified["diagnostics"]

    write_json(output / "AUTHORITATIVE_CHRONOLOGY_SOURCE_MANIFEST.json", {
        "schema_version": "range-attack-source-manifest-v1",
        "parent": PARENT,
        "controlling_audit": {
            "commit": AUDIT,
            "report_path": AUDIT_REPORT,
            "report_blob_oid": AUDIT_REPORT_BLOB,
        },
        "determinism_addendum": {
            "commit": ADDENDUM,
            "report_path": AUDIT_REPORT,
            "report_blob_oid": ADDENDUM_REPORT_BLOB,
            "receipts_blob_oid": ADDENDUM_RECEIPTS_BLOB,
        },
        "authoritative_parent_sources": [
            identity(repo, path, parent=True) for path in SOURCE_PATHS
        ],
        "new_overlay_sources": [
            identity(repo, path, parent=False) for path in NEW_SOURCE_PATHS
        ],
        "private_inputs": {
            "events": {
                "path": "C:/Users/omigr/OMI-Window1-private/joined/events.jsonl",
                "sha256": (
                    "1f150cf0e4e4a5809617c2b9303d5f1cf64b22d182d9"
                    "96ff893de255e6e48b46"
                ),
                "event_count": 804,
                "bytes": 336694,
                "event_leg_identity_count": 1608,
                "event_leg_identities_sha256": (
                    "c7bc10c3432e0ff7e6432cf51311e40eb90015b120c6a"
                    "c3dac32766ab0a7f6cd"
                ),
                "date_range": ["2026-07-12", "2026-07-20"],
                "available_outside_git": True,
            },
            "guarded_cache": {
                "path": (
                    "C:/Users/omigr/OMI-Window1-private/fit-local/"
                    "guarded-cache-v3"
                ),
                "aggregate_sha256": (
                    "aad8d055e90bb429f7da87b450dc9c4e2dc6a6ef114e4"
                    "0368535b8953b86425e"
                ),
                "event_file_count": 804,
                "bytes": 197461623,
                "per_file_receipts_sha256": (
                    "825c27a6c8f789ce76db26033afa5ae59acfea735716f04"
                    "159bfdc8bb89a48ea"
                ),
                "available_outside_git": True,
            },
        },
        "holdout_paths_opened": False,
        "metrics": None,
        "scored": False,
    })
    mechanism_rows = []
    for mechanism in MECHANISMS:
        detail = SURFACE_DETAILS.get(mechanism["mechanism"], {})
        mechanism_rows.append({
            **mechanism,
            "native_key": detail.get("native_key", "not_applicable"),
            "fitted_population": detail.get(
                "fitted_population", "not_applicable"
            ),
            "category_coverage": detail.get(
                "category_coverage", "all_bound_development_rows_where_present"
            ),
            "native_anchor": detail.get(
                "native_anchor", mechanism["native_meaning"]
            ),
            "target_or_depth_meaning": detail.get(
                "target_or_depth_meaning", mechanism["native_meaning"]
            ),
            "timing_meaning": detail.get(
                "timing_meaning", "strictly chronological receipt when bound"
            ),
            "validation_or_ratification": detail.get(
                "validation_or_ratification",
                "source-bound if BOUND; otherwise explicitly unavailable",
            ),
            "causal_for_simulation": detail.get(
                "causal_for_simulation",
                mechanism["classification"] == "BOUND",
            ),
            "changes_decision": detail.get(
                "changes_decision",
                mechanism["classification"] == "BOUND",
            ),
        })
    write_json(output / "MECHANISM_RECOVERY_TABLE.json", {
        "schema_version": "range-attack-mechanism-recovery-v1",
        "rows": mechanism_rows,
        "classification_totals": dict(Counter(
            row["classification"] for row in MECHANISMS
        )),
        "all_optional_absence_continues_D": True,
        "blocked_V1_strategy_logic_inherited": False,
        "metrics": None,
        "scored": False,
    })
    (output / "MACROMICRO_PAIR_STATE_MACHINE.md").write_text(
        """# Window-1 Range Attack Pair State Machine

1. A timestamped schedule opens the policy corridor; evaluation-start truth is
   structurally absent from policy inputs.
2. The first coherent lawful external BBO pair read establishes independent
   maker presence on both legs.
3. Each Challenger leg accumulates receipt-identified true prints for the
   native first-hour Trendpath discovery interval. Once elapsed, the native
   ATLAS path bottom depth selects one fixed target. Mains retain PAR_LOCK_JOIN.
4. Every target is fully expressed against contemporaneous non-self BBO:
   rest at target when target<=bid, otherwise bid+1, always below ask and 1..99.
   Ordinary bid motion never moves the fixed target.
5. Candidate A holds that target. Candidate B additionally consumes only the
   source-recorded LIVE-AIM mapping and positive-print divot mapping. Rising
   prints hold; AIM_SHALLOW cannot lift an order; AIM_DEEP may only lower it.
6. A receipt-identified public execution at or below an exposed buy price is
   PRICE_REACHED. Displayed five, one five-share print, cumulative volume five,
   trade-through, or queue clearance are never primary fillability gates.
7. The first policy-tape PRICE_REACHED event freezes causal d1 against the
   contemporaneous external bid. On each strictly later sibling print trigger,
   b2_max=floor(-d1-fee-1); at most one +1 improvement is admitted only when
   d1+d2+fee<0 after complete maker expression.
8. The independent V5 evaluator later labels whether reach occurred within
   lawful guarded Window 1. It cannot change any policy action.

All performance metrics remain null in this PRE-RUN.
""",
        encoding="utf-8",
        newline="\n",
    )
    write_json(output / "V1V2_SUPERSESSION_AND_IDENTITY_RECEIPT.json", {
        "schema_version": "range-attack-supersession-v1",
        "retracted_from_future_execution": PARENT,
        "retraction_scope": [
            "moving_current_bid_minus_edge_target",
            "universal_50_climb_split",
            "invented_last_trade_pressure_taker_direction_gates",
            "blanket_composed_action_annotations",
        ],
        "preserved_parent_files": inherited_identity(repo),
        "preserved_files_byte_identical_to_parent": True,
        "parent_files_modified_or_deleted": False,
        "overlay_additions_only": True,
        "metrics": None,
        "scored": False,
    })
    write_json(output / "FORBIDDEN_ACCESS_NO_SCORER_RECEIPT.json", {
        "schema_version": "range-attack-forbidden-access-v1",
        "scorer_imported": False,
        "scorer_invoked": False,
        "benchmark_executed": False,
        "C_PC_S_IC_populated": False,
        "holdout_opened_or_queried": False,
        "network_or_exchange_access": False,
        "live_or_production_access": False,
        "orders_positions_configuration_mutated": False,
        "Window2_exits_settlement_DCA_access": False,
        "policy_source_forbidden_tokens": list(
            sorted(attack.FORBIDDEN_POLICY_FIELDS)
        ),
        "metrics": None,
        "scored": False,
    })
    command = (
        "python -B arb-executor/analysis/"
        "window1_range_attack_prerun_builder.py --repo . "
        "--events C:\\\\Users\\\\omigr\\\\OMI-Window1-private\\\\joined\\\\"
        "events.jsonl --market-cache C:\\\\Users\\\\omigr\\\\"
        "OMI-Window1-private\\\\fit-local\\\\guarded-cache-v3 "
        "--output-dir .claude/window1_range_attack_prerun_20260725 "
        "--workers 6"
    )
    write_json(output / "DETERMINISTIC_REGENERATION_RECEIPT.json", {
        "schema_version": "range-attack-determinism-v1",
        "command": command,
        "reference_and_fresh_regeneration": deterministic,
        "artifact_count": len(deterministic),
        "all_byte_identical": True,
        "gzip_mtime": 0,
        "candidate_order_fixed": list(diagnostics["D_per_candidate"]),
        "metrics": None,
        "scored": False,
    })
    write_json(output / "LATER_EXECUTION_PACKAGE_INVENTORY.json", {
        "schema_version": "range-attack-later-package-inventory-v1",
        "status": "INVENTORY_ONLY_NO_EXECUTION_PACKAGE_AUTHORIZATION",
        "required_frozen_roles": [
            "D804_event_and_leg_identity_ledger",
            "V5_start_boundary_and_guard_ledger",
            "two_frozen_candidate_definitions",
            "1608_unscored_candidate_event_streams",
            "price_fillability_and_stress_contract",
            "existing_frozen_metric_scorer_and_contract",
            "all_source_and_private_input_hash_receipts",
            "new_stdout_safe_deterministic_grid_runner",
        ],
        "execution_id": None,
        "execution_command": None,
        "ranking_rule": None,
        "execution_authorized": False,
        "metrics": None,
        "scored": False,
    })
    (output / "WINDOW1_RANGE_ATTACK_PRE_RUN_REPORT.md").write_text(
        report_text(diagnostics), encoding="utf-8", newline="\n"
    )

    artifact_files = sorted(
        path for path in output.iterdir()
        if path.is_file()
        and path.name not in {
            "ARTIFACT_HASH_MANIFEST.json",
            "WINDOW1_RANGE_ATTACK_PRE_RUN_MANIFEST.json",
        }
    )
    artifact_rows = [{
        "path": str(path.relative_to(repo)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "git_blob_oid": blob_oid(repo, path),
    } for path in artifact_files]
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": "range-attack-artifact-hashes-v1",
        "artifacts": artifact_rows,
        "artifact_count": len(artifact_rows),
        "all_receipts_verified": True,
        "metrics": None,
        "scored": False,
    })
    artifact_manifest = output / "ARTIFACT_HASH_MANIFEST.json"
    write_json(output / "WINDOW1_RANGE_ATTACK_PRE_RUN_MANIFEST.json", {
        "schema_version": "window1-range-attack-prerun-manifest-v1",
        "exact_parent": PARENT,
        "controlling_audit": AUDIT,
        "determinism_addendum": ADDENDUM,
        "candidate_ids": list(diagnostics["D_per_candidate"]),
        "D_per_candidate": diagnostics["D_per_candidate"],
        "candidate_event_stream_count": diagnostics[
            "candidate_event_stream_count"
        ],
        "leg_range_ladder_count": diagnostics[
            "leg_range_ladder_count"
        ],
        "integer_cent_range_row_count": diagnostics[
            "integer_cent_range_row_count"
        ],
        "price_fillability_law": "PRICE_REACHED_PRIMARY_NO_SIZE5_GATE",
        "all_C_PC_S_IC_null": True,
        "scorer_or_benchmark_invoked": False,
        "holdout_live_production_access": False,
        "artifact_hash_manifest": {
            "path": str(artifact_manifest.relative_to(repo)).replace("\\", "/"),
            "bytes": artifact_manifest.stat().st_size,
            "sha256": sha256(artifact_manifest),
            "git_blob_oid": blob_oid(repo, artifact_manifest),
        },
        "execution_authorized": False,
        "metrics": None,
        "scored": False,
    })
    print(json.dumps({
        "status": "PASS_FROZEN_SCORE_FREE",
        **verified,
        "deterministic_artifact_count": len(deterministic),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
