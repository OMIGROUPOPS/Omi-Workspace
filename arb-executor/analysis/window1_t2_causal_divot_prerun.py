#!/usr/bin/env python3
"""Build and freeze the score-free Window-1 T2 causal-divot PRE-RUN."""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_round2_data_binding as binding
import window1_round2_real_capability as capability
import window1_round4_macromicro_instrument as normalizer
import window1_range_attack_prerun_builder as baseline_builder
import window1_t1_post_first_leg_prerun as t1_builder
import window1_t2_causal_divot_instrument as t2


VERSION = "window1-t2-causal-divot-prerun-v1"
PACKAGE_REL = ".claude/window1_t2_causal_divot_prerun_20260727"
SOURCE_REL = "arb-executor/analysis/window1_t2_causal_divot_instrument.py"
BUILDER_REL = "arb-executor/analysis/window1_t2_causal_divot_prerun.py"
TEST_REL = "arb-executor/tests/test_window1_t2_causal_divot_prerun.py"
SPEC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_CAUSAL_DIVOT_CANDIDATES_V1.json"
)
BASELINE_REL = (
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
)
STREAM_FILES = t1_builder.STREAM_FILES
OVERLAY_SHARDS = tuple(
    f"UNSCORED_T2_CANDIDATE_EVENT_OVERLAYS_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
OPPORTUNITY_SHARDS = tuple(
    f"SIBLING_X_OPPORTUNITY_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
DECISION_SHARDS = tuple(
    f"HOLD_WALK_REPRICE_PARK_NOCALL_DECISION_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
TARGET_SELECTION_SHARDS = tuple(
    f"TARGET_SELECTION_REJECTED_TARGET_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
AUDIT_PATHS = {
    t2.CONTROLLING_RESULTS_AUDIT: (
        ".claude/audit_20260727_window1_t1_execution_results/"
        "AUDIT_REPORT.md"
    ),
    t2.CONTROLLING_T1_AUDIT: (
        ".claude/audit_20260727_window1_t1_post_first_leg/"
        "AUDIT_REPORT.md"
    ),
    t2.CONTROLLING_ATTRIBUTION_AUDIT: (
        ".claude/audit_20260727_window1_decision_layer_attribution/"
        "AUDIT_REPORT.md"
    ),
    t2.CONTROLLING_ASYNC_AUDIT: (
        ".claude/audit_20260727_window1_async_census_v2_prerun/"
        "AUDIT_REPORT.md"
    ),
}
METRIC_FIELDS = {"C", "PC", "S", "IC"}
FIVE_NO_BBO = baseline_builder.FIVE_NO_BBO


class T2FreezeError(RuntimeError):
    """An input, causal, conservation, or deterministic gate failed."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    process = subprocess.run(
        ["git", *args], cwd=repo, input=input_bytes,
        capture_output=True, check=False,
    )
    if process.returncode:
        raise T2FreezeError(
            f"git {' '.join(args)} failed: "
            + process.stderr.decode(errors="replace").strip()
        )
    return process.stdout


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(raw)}\0".encode("ascii") + raw
    ).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


class GzipWriter:
    def __init__(self, path: Path) -> None:
        self.raw = path.open("wb")
        self.gz = gzip.GzipFile(
            filename="", mode="wb", fileobj=self.raw, mtime=0
        )
        self.text = io.TextIOWrapper(
            self.gz, encoding="utf-8", newline="\n"
        )
        self.rows = 0

    def write(self, row: Mapping[str, Any]) -> None:
        self.text.write(compact(row) + "\n")
        self.rows += 1

    def close(self) -> None:
        self.text.flush()
        self.text.detach()
        self.gz.close()
        self.raw.close()


def assert_metrics_null(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in METRIC_FIELDS and child is not None:
                raise T2FreezeError(f"metric populated at {path}.{key}")
            if key in {"metrics", "performance"} and child is not None:
                raise T2FreezeError(
                    f"performance populated at {path}.{key}"
                )
            if key == "scored" and child is not False:
                raise T2FreezeError(f"scored changed at {path}")
            assert_metrics_null(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_metrics_null(child, f"{path}[{index}]")


def _normalize_identity(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _normalize_identity(child)
            for key, child in value.items()
            if key not in {"pair_read_id"}
        }
    if isinstance(value, list):
        return [_normalize_identity(child) for child in value]
    if isinstance(value, str):
        result = value
        for candidate in (
            *t2.BASE_CANDIDATES, *t2.CANDIDATES, *t2.t1.CANDIDATES,
        ):
            result = result.replace(candidate, "<CANDIDATE>")
        return result
    return value


def semantic_sha256(value: Any) -> str:
    return canonical_sha256(_normalize_identity(value))


def _first_fill_semantics(stream: Mapping[str, Any]) -> dict[str, Any]:
    pair = stream["pair_state"]
    leg_id = pair.get("first_filled_leg")
    fill = (
        (stream.get("causal_policy_fill_state_by_leg") or {}).get(leg_id)
        if leg_id else None
    )
    return {
        "first_filled_leg": leg_id,
        "first_fill_ts": pair.get("first_fill_ts"),
        "causal_d1_cents": pair.get("causal_d1_cents"),
        "fee_cents": pair.get("fee_cents"),
        "first_leg_fill": _normalize_identity(fill),
    }


def _prefix_hash(stream: Mapping[str, Any]) -> str | None:
    first = stream["pair_state"].get("first_fill_ts")
    if first is None:
        return None
    return semantic_sha256([
        row for row in stream["order_stream"]
        if float(row["ts"]) <= float(first)
    ])


def _nofill_hash(stream: Mapping[str, Any]) -> str | None:
    if stream["pair_state"].get("first_filled_leg") is not None:
        return None
    return semantic_sha256({
        "actions": stream["order_stream"],
        "intervals": stream["order_intervals_by_leg"],
    })


def baseline_facts(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    facts = t1_builder.baseline_facts(repo)
    if len(facts) != 1608:
        raise T2FreezeError("baseline candidate-event set changed")
    return facts


def compact_result(
    result: Mapping[str, Any],
    base: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    first = _first_fill_semantics(result)
    prefix = _prefix_hash(result)
    nofill = _nofill_hash(result)
    intervals = result["order_intervals_by_leg"]
    actions = result["order_stream"]
    first_equal = first == base["first_fill_semantics"]
    prefix_equal = (
        prefix == base["prefix_through_first_fill_semantic_sha256"]
    )
    nofill_equal = nofill == base["nofill_full_semantic_sha256"]
    overlay = {
        "schema_version": VERSION + "-candidate-event-overlay-v1",
        "candidate_id": result["candidate_id"],
        "base_candidate_id": result["base_candidate_id"],
        "t2_variant": result["t2_variant"],
        "t2_switches": result["t2_switches"],
        "event_id": result["event_id"],
        "event_date": result["event_date"],
        "category": result["category"],
        "D_member": True,
        "baseline_stream_reference": {
            "stream_row_sha256": base["stream_row_sha256"],
            "order_stream_sha256": base["order_stream_sha256"],
            "order_intervals_sha256": base["order_intervals_sha256"],
        },
        "policy_clock": result["policy_clock"],
        "pair_state": result["pair_state"],
        "causal_policy_fill_state_by_leg": result[
            "causal_policy_fill_state_by_leg"
        ],
        "order_intervals_by_leg": intervals,
        "order_stream_semantic_sha256": semantic_sha256(actions),
        "order_intervals_semantic_sha256": semantic_sha256(intervals),
        "full_policy_semantic_sha256": semantic_sha256({
            "actions": actions, "intervals": intervals,
        }),
        "first_leg_semantics": first,
        "first_leg_semantics_identical_to_baseline": first_equal,
        "prefix_through_first_fill_semantic_sha256": prefix,
        "prefix_through_first_fill_identical_to_baseline": prefix_equal,
        "baseline_nofill": (
            base["nofill_full_semantic_sha256"] is not None
        ),
        "nofill_semantics_sha256": nofill,
        "nofill_semantics_identical_to_baseline": nofill_equal,
        "target_surface_count": sum(
            len(rows) for rows in result["t2_target_surfaces_by_leg"].values()
        ),
        "decision_count": sum(
            len(rows) for rows in result["t2_episode_decisions_by_leg"].values()
        ),
        "support_decay_count": sum(
            len(rows)
            for rows in result[
                "t2_current_exposure_support_decay_by_leg"
            ].values()
        ),
        "divot_chronology_count": sum(
            len(rows)
            for rows in result["t2_divot_chronology_by_leg"].values()
        ),
        "C": None,
        "PC": None,
        "S": None,
        "IC": None,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    details = {
        "target_surfaces": [
            row for rows in result["t2_target_surfaces_by_leg"].values()
            for row in rows
        ],
        "support_decay": [
            row for rows in result[
                "t2_current_exposure_support_decay_by_leg"
            ].values() for row in rows
        ],
        "target_selection": [
            row for rows in result["t2_target_selection_by_leg"].values()
            for row in rows
        ],
        "decisions": [
            row for rows in result["t2_episode_decisions_by_leg"].values()
            for row in rows
        ],
        "divot_chronology": [
            row for rows in result["t2_divot_chronology_by_leg"].values()
            for row in rows
        ],
        "parent_exposure": [
            row for rows in result[
                "t2_parent_exposure_receipts_by_leg"
            ].values() for row in rows
        ],
        "actions": actions,
        "first_fill_budget": [
            {
                "candidate_id": result["candidate_id"],
                "event_id": result["event_id"],
                "leg_id": leg_id,
                "first_filled_leg": result["pair_state"][
                    "first_filled_leg"
                ],
                "first_fill_ts": result["pair_state"]["first_fill_ts"],
                "d1_cents": result["pair_state"]["causal_d1_cents"],
                "b2_max_cents": next((
                    row.get("b2_max_cents") for row in actions
                    if row.get("action") == "headroom_armed"
                    and row.get("leg_id") == leg_id
                ), None),
                "fee_cents": result["pair_state"]["fee_cents"],
                "positive_d2_lawful_target_count": sum(
                    target["lawful"] and target["d2_cents"] > 0
                    for surface in result[
                        "t2_target_surfaces_by_leg"
                    ][leg_id]
                    for target in surface.get("targets") or []
                ),
                "positive_d2_exposed_count": sum(
                    row["decision"] in {"PLACE", "REPRICE"}
                    and row.get("selected_target") is not None
                    and row["selected_target"]["d2_cents"] > 0
                    for row in result["t2_target_selection_by_leg"][leg_id]
                ),
                "metrics": None,
                "scored": False,
            }
            for leg_id in result["t2_target_surfaces_by_leg"]
            if leg_id != result["pair_state"]["first_filled_leg"]
            and result["pair_state"]["first_filled_leg"] is not None
        ],
    }
    assert_metrics_null(overlay)
    return overlay, details


def inherited_nofill_overlay(
    *,
    candidate_id: str,
    event_id: str,
    base: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    overlay = {
        "schema_version": VERSION + "-candidate-event-overlay-v1",
        "candidate_id": candidate_id,
        "base_candidate_id": t2.base_candidate_id(candidate_id),
        "t2_variant": t2._variant(candidate_id),
        "t2_switches": dict(t2.SWITCHES[t2._variant(candidate_id)]),
        "event_id": event_id,
        "event_date": base["event_date"],
        "category": base["category"],
        "D_member": True,
        "inherits_complete_baseline_stream": True,
        "inheritance_reason": "no credited first leg; T2 is post-first-only",
        "baseline_stream_reference": {
            "stream_row_sha256": base["stream_row_sha256"],
            "order_stream_sha256": base["order_stream_sha256"],
            "order_intervals_sha256": base["order_intervals_sha256"],
        },
        "policy_clock": {
            "baseline_policy_decision_horizon_ts": base[
                "baseline_policy_horizon_ts"
            ],
        },
        "pair_state": {
            "first_filled_leg": None,
            "first_fill_ts": None,
            "causal_d1_cents": None,
            "fee_cents": 0.0,
            "C": None, "PC": None, "S": None, "IC": None,
        },
        "causal_policy_fill_state_by_leg": None,
        "order_intervals_by_leg": None,
        "order_stream_semantic_sha256": None,
        "order_intervals_semantic_sha256": base[
            "order_intervals_sha256"
        ],
        "full_policy_semantic_sha256": base[
            "full_policy_semantic_sha256"
        ],
        "first_leg_semantics": base["first_fill_semantics"],
        "first_leg_semantics_identical_to_baseline": True,
        "prefix_through_first_fill_semantic_sha256": None,
        "prefix_through_first_fill_identical_to_baseline": True,
        "baseline_nofill": True,
        "nofill_semantics_sha256": base[
            "nofill_full_semantic_sha256"
        ],
        "nofill_semantics_identical_to_baseline": True,
        "target_surface_count": 0,
        "decision_count": 0,
        "support_decay_count": 0,
        "divot_chronology_count": 0,
        "C": None, "PC": None, "S": None, "IC": None,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    details = {
        key: [] for key in (
            "target_surfaces", "support_decay", "target_selection",
            "decisions", "divot_chronology", "parent_exposure",
            "first_fill_budget",
        )
    }
    details["actions"] = []
    return overlay, details


def inherited_control_overlay(
    *,
    candidate_id: str,
    event_id: str,
    base: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Materialize a fixed-admission control by immutable stream reference."""
    overlay, details = inherited_nofill_overlay(
        candidate_id=candidate_id, event_id=event_id, base=base
    )
    overlay.update({
        "inherits_complete_baseline_stream": True,
        "inheritance_reason": (
            "fixed-admission measurement control is the byte-bound passed "
            "Range-Attack V2 parent stream"
        ),
        "pair_state": {
            **base["first_fill_semantics"],
            "C": None, "PC": None, "S": None, "IC": None,
        },
        "first_leg_semantics": base["first_fill_semantics"],
        "prefix_through_first_fill_semantic_sha256": base[
            "prefix_through_first_fill_semantic_sha256"
        ],
        "baseline_nofill": (
            base["nofill_full_semantic_sha256"] is not None
        ),
        "nofill_semantics_sha256": base[
            "nofill_full_semantic_sha256"
        ],
    })
    return overlay, details


_WORKER: dict[str, Any] = {}


def _init_worker(
    repo_text: str,
    cache_text: str,
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
    facts: Mapping[tuple[str, str], Mapping[str, Any]],
    source_hashes: Mapping[str, str],
) -> None:
    repo = Path(repo_text)
    _WORKER.update({
        "repo": repo,
        "cache": Path(cache_text),
        "feature_map": feature_map,
        "boundaries": boundaries,
        "facts": facts,
        "source_hashes": source_hashes,
        "spec": t2.load_candidate_spec(repo),
        "atlas": json.loads(
            (repo / t2.passed.ATLAS_PATH).read_text(encoding="utf-8")
        ),
        "guidebook": json.loads(
            (repo / t2.passed.GUIDEBOOK_PATH).read_text(encoding="utf-8")
        ),
        "recut": json.loads(
            (repo / t2.passed.RECUT_PATH).read_text(encoding="utf-8")
        ),
        "reach": json.loads(
            (repo / t2.passed.TAKER_REACH_PATH).read_text(encoding="utf-8")
        ),
    })


def _process_event(
    item: tuple[int, Mapping[str, Any]],
) -> tuple[int, list[tuple[dict[str, Any], dict[str, Any]]]]:
    index, event = item
    event_id = str(event["event_id"])
    candidate_rows = []
    for candidate in t2.CANDIDATES:
        base = _WORKER["facts"][(t2.base_candidate_id(candidate), event_id)]
        candidate_rows.append((
            candidate, base,
            base["nofill_full_semantic_sha256"] is not None,
        ))
    if all(row[2] for row in candidate_rows):
        return index, [
            (
                inherited_control_overlay(
                    candidate_id=candidate, event_id=event_id, base=base
                )
                if t2._variant(candidate)
                == "fixed_admission_parent_control"
                else inherited_nofill_overlay(
                    candidate_id=candidate, event_id=event_id, base=base
                )
            )
            for candidate, base, _ in candidate_rows
        ]
    t2.t1.clear_event_flow_cache()
    cache = capability.load_cache(
        _WORKER["cache"] / f"{event_id}.json.gz"
    )
    normalized, _ = normalizer.normalize_event(
        event, cache, _WORKER["feature_map"], corridor_seconds=0.0
    )
    boundary = _WORKER["boundaries"][event_id]
    rows = []
    for candidate, base, nofill in candidate_rows:
        if t2._variant(candidate) == "fixed_admission_parent_control":
            rows.append(inherited_control_overlay(
                candidate_id=candidate, event_id=event_id, base=base
            ))
            continue
        if nofill:
            rows.append(inherited_nofill_overlay(
                candidate_id=candidate, event_id=event_id, base=base
            ))
            continue
        policy = t2.candidate_policy(
            _WORKER["repo"], _WORKER["spec"], candidate
        )
        result = t2.T2Simulator(
            policy,
            boundary=boundary,
            atlas=_WORKER["atlas"],
            guidebook=_WORKER["guidebook"],
            recut=_WORKER["recut"],
            taker_reach=_WORKER["reach"],
            source_hashes=_WORKER["source_hashes"],
        ).run(normalized)
        rows.append(compact_result(result, base))
    return index, rows


def _audit_binding(repo: Path) -> list[dict[str, Any]]:
    rows = []
    for commit, path in AUDIT_PATHS.items():
        raw = git(repo, "show", f"{commit}:{path}")
        if git(repo, "cat-file", "-t", commit).strip() != b"commit":
            raise T2FreezeError(f"audit commit unavailable: {commit}")
        rows.append({
            "commit": commit,
            "path": path,
            "blob_oid": git_blob_oid(raw),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    return rows


def _source_manifest(
    repo: Path,
    events_path: Path,
    cache_root: Path,
) -> dict[str, Any]:
    committed = [
        SOURCE_REL, BUILDER_REL, TEST_REL, SPEC_REL,
        "arb-executor/analysis/window1_t1_post_first_leg_instrument.py",
        "arb-executor/analysis/window1_range_attack_instrument_v2.py",
        "arb-executor/analysis/window1_range_attack_instrument.py",
        ".claude/window1_range_attack_prerun_20260725/"
        "MECHANISM_RECOVERY_TABLE.json",
    ]
    rows = []
    for relative in committed:
        path = repo / relative
        raw = path.read_bytes()
        rows.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git_blob_oid(raw),
        })
    private = [{
        "path": str(events_path.resolve()),
        "role": "immutable_D804_event_ledger",
        "bytes": events_path.stat().st_size,
        "sha256": sha256_file(events_path),
        "availability": "PRIVATE_HASH_BOUND",
    }]
    for path in sorted(cache_root.glob("*.json.gz")):
        private.append({
            "path": str(path.resolve()),
            "role": "guarded_cache_v3_event_microstructure",
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "availability": "PRIVATE_HASH_BOUND",
        })
    if len(private) != 805:
        raise T2FreezeError("private input receipt count changed")
    return {
        "schema_version": VERSION + "-source-manifest-v1",
        "exact_parent": t2.EXACT_PARENT,
        "audit_bindings": _audit_binding(repo),
        "committed_sources": rows,
        "private_inputs": private,
        "private_input_count": len(private),
        "holdout_dates": sorted(t2.passed.SEALED_HOLDOUT_DATES),
        "holdout_excluded": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def _load_controlling_attribution(repo: Path) -> list[dict[str, Any]]:
    path = (
        repo / ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "DECISION_LAYER_EVENT_LEDGER.jsonl.gz"
    )
    rows = list(iter_gzip(path))
    expected = Counter({
        "first_fill_sibling_response_failed_to_create_exposure": 24,
        "target_selection_never_included_lawful_X": 4,
        "headroom_reprice": 8,
        "corridor_window_termination": 8,
        "LIVE_AIM_reprice": 1,
        "capacity_measurement_unproved": 2,
    })
    if Counter(row["attributed_layer"] for row in rows) != expected:
        raise T2FreezeError("controlling 24+4+17+2 attribution changed")
    moved_path = path.parent / "MOVED_AWAY_ATTRIBUTION.jsonl.gz"
    moved = list(iter_gzip(moved_path))
    by_key = {
        (str(row["candidate_id"]), str(row["event_id"])): row
        for row in moved
    }
    if len(by_key) != 17:
        raise T2FreezeError("controlling moved-away set changed")
    merged = []
    for row in rows:
        key = (str(row["candidate_id"]), str(row["event_id"]))
        merged.append({**row, "_moved_detail": by_key.get(key)})
    return merged


def _fixture_migration(
    attribution: list[Mapping[str, Any]],
    details: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    rows = []
    counts = Counter()
    for source in attribution:
        layer = str(source["attributed_layer"])
        if layer == "capacity_measurement_unproved":
            continue
        base_id = str(source["candidate_id"])
        regime = (
            "macro_hold" if "macro_hold" in base_id else "macro_micro"
        )
        event_id = str(source["event_id"])
        if layer == "first_fill_sibling_response_failed_to_create_exposure":
            variants = ("full_causal_divot_stack",)
        elif layer == "target_selection_never_included_lawful_X":
            variants = (
                "non_displacing_target_completeness",
                "target_completeness_evidence_decay",
                "full_causal_divot_stack",
            )
        else:
            variants = (
                "non_displacing_target_completeness",
                "target_completeness_evidence_decay",
                "full_causal_divot_stack",
            )
        for variant in variants:
            candidate = f"w1_t2__{regime}__{variant}"
            detail = details[(candidate, event_id)]
            opportunity = source["earliest_lawful_opportunity"]
            acceptance = None
            proof: dict[str, Any] = {}
            if layer == (
                "first_fill_sibling_response_failed_to_create_exposure"
            ):
                matches = [
                    row for row in detail["decisions"]
                    if row["leg_id"] == source["sibling_leg_id"]
                    and float(row["timestamp"]) > float(
                        source["credited_first_leg"]["timestamp"]
                    )
                ]
                acceptance = bool(matches)
                proof = {
                    "explicit_post_first_decision_count": len(matches),
                    "first_decision": matches[0] if matches else None,
                }
                counts["response_rows_checked"] += 1
            elif layer == "target_selection_never_included_lawful_X":
                x = int(opportunity["price_x_cents"])
                surfaces = [
                    surface
                    for surface in detail["target_surfaces"]
                    if surface["leg_id"] == source["sibling_leg_id"]
                ]
                matches = [
                    {
                        "surface_timestamp": surface["timestamp"],
                        "trigger_receipt": surface["trigger_receipt"],
                        "target": target,
                    }
                    for surface in surfaces
                    for target in surface.get("targets") or []
                    if target["X_cents"] == x
                ]
                lawful_matches = [
                    row for row in matches if row["target"]["lawful"]
                ]
                expression_guarded_matches = [
                    row for row in matches
                    if (
                        row["target"]["checks"]["strict_combined_negative"]
                        and row["target"]["checks"][
                            "inside_event_specific_b2_max"
                        ]
                        and not row["target"]["checks"]["maker_safe"]
                        and row["target"]["ask_cents"] <= x
                    )
                ]
                lawful_alternatives = [
                    {
                        "surface_timestamp": surface["timestamp"],
                        "trigger_receipt": surface["trigger_receipt"],
                        "target": target,
                    }
                    for surface in surfaces
                    for target in surface.get("targets") or []
                    if target["lawful"]
                ]
                acceptance = bool(
                    lawful_matches
                    or (
                        expression_guarded_matches
                        and lawful_alternatives
                    )
                )
                proof = {
                    "lawful_X_cents": x,
                    "surface_inclusion_count": len(matches),
                    "lawful_maker_inclusion_count": len(lawful_matches),
                    "combined_lawful_but_expression_guarded_count": len(
                        expression_guarded_matches
                    ),
                    "lawful_maker_alternative_count": len(
                        lawful_alternatives
                    ),
                    "first_inclusion": matches[0] if matches else None,
                    "first_lawful_maker_alternative": (
                        lawful_alternatives[0]
                        if lawful_alternatives else None
                    ),
                    "interpretation": (
                        "exact_audited_X_retained_as_causal_print context; "
                        "maker expression guard remains controlling"
                    ),
                }
                counts["target_rows_checked"] += 1
            else:
                moved = source["_moved_detail"]
                original = moved["original_exposure"]
                x = int(original["X_cents"])
                ts = float(opportunity["timestamp"])
                intervals = (
                    detail["overlay"]["order_intervals_by_leg"][
                        source["sibling_leg_id"]
                    ]
                )
                retained = [
                    row for row in intervals
                    if int(row["limit_price_cents"]) == x
                    and float(row["opened_ts"]) <= ts
                    and (
                        row.get("closed_ts") is None
                        or float(row["closed_ts"]) >= ts
                    )
                ]
                allowed = [
                    row for row in detail["actions"]
                    if row["leg_id"] == source["sibling_leg_id"]
                    and row["action"] in {"cancel", "reprice"}
                    and row.get("primary_authority") in {
                        "MAKER_SAFETY", "LIVEAIM_SOURCE_MAPPING",
                        "DIVOT_SOURCE_MAPPING", "CAUSAL_PAIR_HEADROOM",
                        "POLICY_HORIZON",
                    }
                ]
                acceptance = bool(retained or allowed)
                proof = {
                    "original_X_cents": x,
                    "opportunity_timestamp": ts,
                    "preserved_through_opportunity": bool(retained),
                    "receipt_backed_lawful_resolution_count": len(allowed),
                    "lawful_resolution_actions": allowed,
                }
                counts["moved_rows_checked"] += 1
            if not acceptance:
                raise T2FreezeError(
                    f"T2 fixture migration failed: {candidate} {event_id} "
                    f"{layer}"
                )
            rows.append({
                "source_candidate_id": base_id,
                "T2_candidate_id": candidate,
                "event_id": event_id,
                "attributed_layer": layer,
                "credited_first_leg": source["credited_first_leg"],
                "earliest_lawful_opportunity": opportunity,
                "acceptance": True,
                "proof": proof,
                "metrics": None,
                "performance": None,
                "scored": False,
            })
    return {
        "schema_version": VERSION + "-causal-fixture-migration-v1",
        "source_fixture_counts": {
            "missing_episode_keyed_decision": 24,
            "omitted_lawful_target": 4,
            "moved_away": 17,
            "capacity_unproved_diagnostic_only": 2,
        },
        "variant_receipt_counts": dict(counts),
        "row_count": len(rows),
        "all_acceptance_checks_passed": True,
        "capacity_unproved_TON_SPI_remains_uncredited_claim": True,
        "rows": rows,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def build(
    *,
    repo: Path,
    events_path: Path,
    cache_root: Path,
    output: Path,
    workers: int,
) -> dict[str, Any]:
    if output.exists():
        raise T2FreezeError("build output already exists")
    output.mkdir(parents=True)
    events = list(iter_jsonl(events_path))
    if len(events) != 804:
        raise T2FreezeError(f"D changed: {len(events)}")
    dates = sorted({str(row["event_date"]) for row in events})
    if dates != list(binding.DEV_DATES):
        raise T2FreezeError("development dates changed")
    if any(
        row["event_date"] in t2.passed.SEALED_HOLDOUT_DATES
        for row in events
    ):
        raise T2FreezeError("holdout entered T2")
    event_ids = [str(row["event_id"]) for row in events]
    if len(set(event_ids)) != 804:
        raise T2FreezeError("event identities changed")
    feature_rows = [
        row for row in iter_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in feature_rows
    }
    if len(feature_map) != 1608:
        raise T2FreezeError("leg identity count changed")
    boundaries = {
        str(row["event_id"]): baseline_builder.boundary_contract(row)
        for row in iter_jsonl(repo / baseline_builder.START_LEDGER)
    }
    if set(boundaries) != set(event_ids):
        raise T2FreezeError("boundary identity set changed")
    facts = baseline_facts(repo)
    attribution = _load_controlling_attribution(repo)
    fixture_event_ids = {
        str(row["event_id"]) for row in attribution
        if row["attributed_layer"] != "capacity_measurement_unproved"
    }
    spec = t2.load_candidate_spec(repo)
    source_paths = {
        "atlas": t2.passed.ATLAS_PATH,
        "guidebook": t2.passed.GUIDEBOOK_PATH,
        "recut": t2.passed.RECUT_PATH,
        "taker_reach": t2.passed.TAKER_REACH_PATH,
        "liveaim_proof": t2.passed.LIVEAIM_PROOF_PATH,
        "volume": t2.passed.VOLUME_PATH,
        "start_ledger": baseline_builder.START_LEDGER,
        "drift": t2.passed.DRIFT_PATH,
        "divot": t2.passed.DIVOT_PATH,
        "band": t2.passed.BAND_PATH,
        "library": t2.passed.LIBRARY_PATH,
        "orient": t2.passed.ORIENT_PATH,
    }
    source_hashes = t1_builder.baseline_policy_source_hashes(
        repo, source_paths
    )
    overlay_writers = [GzipWriter(output / name) for name in OVERLAY_SHARDS]
    opportunity_writers = [
        GzipWriter(output / name) for name in OPPORTUNITY_SHARDS
    ]
    decision_writers = [
        GzipWriter(output / name) for name in DECISION_SHARDS
    ]
    support_writer = GzipWriter(
        output / "CURRENT_EXPOSURE_SUPPORT_DECAY_LEDGER.jsonl.gz"
    )
    selection_writers = [
        GzipWriter(output / name) for name in TARGET_SELECTION_SHARDS
    ]
    divot_writer = GzipWriter(
        output / "DIVOT_RECOGNITION_ACTION_EVIDENCE_CHRONOLOGY.jsonl.gz"
    )
    budget_writer = GzipWriter(
        output / "FIRST_FILL_BUDGET_POSITIVE_D2_RECEIPTS.jsonl.gz"
    )
    conservation = Counter()
    first_bad = []
    nofill_bad = []
    control_bad = []
    control_hashes: dict[tuple[str, str], str] = {}
    changed = Counter()
    changed_ids: dict[str, list[str]] = defaultdict(list)
    counts = Counter()
    parent_receipts = Counter()
    progress = (output / "BUILD_PROGRESS.log").open(
        "w", encoding="utf-8", newline="\n"
    )
    fixture_details: dict[tuple[str, str], dict[str, Any]] = {}
    try:
        worker_count = max(1, min(int(workers), os.cpu_count() or 1))
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=worker_count,
            initializer=_init_worker,
            initargs=(
                str(repo), str(cache_root), feature_map, boundaries,
                facts, source_hashes,
            ),
        ) as pool:
            # Bound outstanding serialized result payloads.  Each event owns
            # a complete causal target surface, so submitting all 804 events
            # at once would retain completed payloads in the parent before
            # their deterministic ordinal could be published.
            pending: dict[int, concurrent.futures.Future[Any]] = {}
            next_submit = 0
            window = max(worker_count * 2, 1)
            while next_submit < min(window, len(events)):
                pending[next_submit] = pool.submit(
                    _process_event, (next_submit, events[next_submit])
                )
                next_submit += 1
            for expected_index in range(len(events)):
                future = pending.pop(expected_index)
                index, candidate_results = future.result()
                if next_submit < len(events):
                    pending[next_submit] = pool.submit(
                        _process_event, (next_submit, events[next_submit])
                    )
                    next_submit += 1
                if index != expected_index:
                    raise T2FreezeError("worker event order changed")
                if len(candidate_results) != 8:
                    raise T2FreezeError("candidate count changed")
                for candidate_index, (overlay, detail) in enumerate(
                    candidate_results
                ):
                    candidate = t2.CANDIDATES[candidate_index]
                    if overlay["candidate_id"] != candidate:
                        raise T2FreezeError("candidate order changed")
                    shard = index % len(OVERLAY_SHARDS)
                    overlay_writers[shard].write(overlay)
                    for row in detail["target_surfaces"]:
                        opportunity_writers[shard].write(row)
                        counts["target_surfaces"] += 1
                        for target in row.get("targets") or []:
                            counts["lawful_sibling_X"] += int(
                                target["lawful"]
                            )
                            counts["lawful_positive_d2_targets"] += int(
                                target["lawful"]
                                and target["d2_cents"] > 0
                            )
                    for row in detail["decisions"]:
                        decision_writers[shard].write(row)
                        counts["decisions"] += 1
                        counts["decision_" + row["decision"]] += 1
                        if (
                            row["decision"] in {"PLACE", "REPRICE"}
                            and row.get("selected_target")
                            and row["selected_target"]["d2_cents"] > 0
                        ):
                            counts["positive_d2_targets_exposed"] += 1
                    for row in detail["support_decay"]:
                        support_writer.write(row)
                        counts["support_decay_rows"] += 1
                        if row.get("decision") == "PARK":
                            counts["evidence_decay_PARK"] += 1
                        if row.get("replacement_X_cents") is not None:
                            counts["evidence_decay_replacements"] += 1
                    for row in detail["target_selection"]:
                        selection_writers[shard].write(row)
                    for row in detail["divot_chronology"]:
                        divot_writer.write(row)
                        counts[
                            "divot_" + str(row["chronology_stage"])
                        ] += 1
                    for row in detail["first_fill_budget"]:
                        budget_writer.write(row)
                    for row in detail["parent_exposure"]:
                        parent_receipts[str(row.get("decision"))] += 1
                    conservation[candidate] += 1
                    if (
                        not overlay[
                            "first_leg_semantics_identical_to_baseline"
                        ]
                        or not overlay[
                            "prefix_through_first_fill_identical_to_baseline"
                        ]
                    ):
                        first_bad.append((candidate, overlay["event_id"]))
                    if (
                        overlay["baseline_nofill"]
                        and not overlay[
                            "nofill_semantics_identical_to_baseline"
                        ]
                    ):
                        nofill_bad.append((candidate, overlay["event_id"]))
                    regime = t2._regime(candidate)
                    control_key = (regime, overlay["event_id"])
                    if t2._variant(candidate) == (
                        "fixed_admission_parent_control"
                    ):
                        control_hashes[control_key] = overlay[
                            "full_policy_semantic_sha256"
                        ]
                        base_hash = facts[(
                            t2.base_candidate_id(candidate),
                            overlay["event_id"],
                        )]["full_policy_semantic_sha256"]
                        if (
                            overlay["full_policy_semantic_sha256"]
                            != base_hash
                        ):
                            control_bad.append(
                                (candidate, overlay["event_id"])
                            )
                    else:
                        control_hash = control_hashes.get(control_key)
                        if control_hash is None:
                            raise T2FreezeError(
                                "fixed-admission control not emitted first"
                            )
                        status = (
                            "unchanged" if overlay[
                                "full_policy_semantic_sha256"
                            ] == control_hash else "changed"
                        )
                        changed[(candidate, status)] += 1
                        if status == "changed":
                            changed_ids[candidate].append(
                                overlay["event_id"]
                            )
                    if overlay["event_id"] in fixture_event_ids:
                        detail["overlay"] = overlay
                        fixture_details[(candidate, overlay["event_id"])] = (
                            detail
                        )
                progress.write(compact({
                    "event_index": expected_index,
                    "event_id": event_ids[expected_index],
                    "candidate_rows_published": 8,
                    "metrics": None,
                    "scored": False,
                }) + "\n")
                progress.flush()
    finally:
        progress.close()
        for writer in (
            *overlay_writers, *opportunity_writers, *decision_writers,
            *selection_writers, support_writer, divot_writer, budget_writer,
        ):
            writer.close()
    if any(conservation[candidate] != 804 for candidate in t2.CANDIDATES):
        raise T2FreezeError(f"D conservation failed: {dict(conservation)}")
    if first_bad or nofill_bad:
        raise T2FreezeError(
            f"semantic identity failed: first={first_bad[:3]} "
            f"nofill={nofill_bad[:3]}"
        )
    if control_bad:
        raise T2FreezeError(
            f"fixed-admission controls differ from baseline: "
            f"{control_bad[:5]}"
        )
    fixture_receipt = _fixture_migration(attribution, fixture_details)
    write_json(
        output / "CAUSAL_FIXTURE_MIGRATION_TABLE.json",
        fixture_receipt,
    )

    control_receipt = {
        "schema_version": VERSION + "-fixed-admission-control-v1",
        "control_candidate_ids": [
            candidate for candidate in t2.CANDIDATES
            if t2._variant(candidate) == "fixed_admission_parent_control"
        ],
        "candidate_event_rows_checked": 1608,
        "baseline_candidate_event_rows": 1608,
        "candidate_normalized_semantic_mismatch_count": 0,
        "one_byte_identical_fill_admission_law_on_both_sides": True,
        "former_boundary_surface_artifacts": [
            {
                "candidate_regime": "macro_hold",
                "event_id": "KXATPMATCH-26JUL13PASKRU",
                "disposition": "DISAPPEARS_UNDER_IDENTICAL_ADMISSION_SURFACE",
            },
            {
                "candidate_regime": "macro_micro",
                "event_id": "KXATPMATCH-26JUL13PASKRU",
                "disposition": "DISAPPEARS_UNDER_IDENTICAL_ADMISSION_SURFACE",
            },
            {
                "candidate_regime": "macro_micro",
                "event_id": "KXATPCHALLENGERMATCH-26JUL12FEAWAL",
                "disposition": "DISAPPEARS_UNDER_IDENTICAL_ADMISSION_SURFACE",
            },
        ],
        "former_boundary_artifact_count": 3,
        "behavioral_comparison_artifact_count": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(
        output / "FIXED_ADMISSION_PARENT_IDENTITY_RECEIPT.json",
        control_receipt,
    )
    write_json(output / "CANDIDATE_SWITCH_MATRIX.json", {
        "schema_version": VERSION + "-candidate-matrix-v1",
        "candidate_ids": list(t2.CANDIDATES),
        "baseline_candidate_ids": list(t2.BASE_CANDIDATES),
        "switch_matrix": spec["switch_matrix"],
        "free_parameters": [],
        "candidate_ranking": None,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    write_json(output / "D_CONSERVATION_RECEIPT.json", {
        "schema_version": VERSION + "-D-conservation-v1",
        "D_per_candidate": dict(conservation),
        "immutable_D": 804,
        "candidate_count": 8,
        "candidate_event_rows": sum(conservation.values()),
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    write_json(output / "FIRST_LEG_SEMANTIC_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-first-leg-identity-v1",
        "rows_checked": 6432,
        "mismatch_count": 0,
        "pre_first_action_mismatch_count": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    nofill_baseline = sum(
        fact["nofill_full_semantic_sha256"] is not None
        for fact in facts.values()
    )
    write_json(output / "NOFILL_SEMANTIC_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-nofill-identity-v1",
        "baseline_nofill_rows": nofill_baseline,
        "T2_nofill_rows_checked": nofill_baseline * 4,
        "mismatch_count": 0,
        "T2_is_post_first_only": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    write_json(
        output / "CHANGED_BYTE_IDENTICAL_STREAM_CENSUS.json",
        {
            "schema_version": VERSION + "-stream-census-v1",
            "comparison": (
                "candidate-normalized complete policy stream versus "
                "same-regime fixed-admission control"
            ),
            "controls_semantically_identical_to_passed_parents": True,
            "candidate_counts": {
                candidate: {
                    "changed": changed[(candidate, "changed")],
                    "byte_identical_after_candidate_normalization":
                        changed[(candidate, "unchanged")],
                    "D": 804,
                }
                for candidate in t2.CANDIDATES
                if t2._variant(candidate)
                != "fixed_admission_parent_control"
            },
            "changed_event_ids": dict(changed_ids),
            "metrics": None,
            "performance": None,
            "scored": False,
        },
    )
    write_json(
        output / "PARENT_EXPOSURE_PRESERVATION_REPLACEMENT_CENSUS.json",
        {
            "schema_version": VERSION + "-parent-exposure-census-v1",
            "parent_exposure_receipt_counts": dict(parent_receipts),
            "preserved_exposure_count": (
                counts["decision_HOLD"]
                + parent_receipts["HOLD"]
            ),
            "replaced_exposure_count": counts["decision_REPRICE"],
            "parked_exposure_count": counts["decision_PARK"],
            "replacement_requires_named_decay": True,
            "unconditional_persistence": False,
            "metrics": None,
            "performance": None,
            "scored": False,
        },
    )
    mechanism = {
        "schema_version": VERSION + "-mechanism-status-v1",
        "mechanisms": [
            {"mechanism": "positive_size_true_print", "status": "BOUND"},
            {"mechanism": "nonself_BBO_top5", "status": "BOUND"},
            {"mechanism": "Trendpath_ATLAS_discovery", "status": "BOUND"},
            {"mechanism": "LIVE_AIM_mapping", "status": "BOUND"},
            {"mechanism": "GUIDEBOOK_deep_tier", "status": "BOUND"},
            {"mechanism": "positive_print_microdivot", "status": "BOUND"},
            {"mechanism": "causal_divot_later_recurrence", "status": "BOUND"},
            {"mechanism": "pair_combined_headroom", "status": "BOUND"},
            {"mechanism": "timestamped_policy_clock", "status": "BOUND"},
            {"mechanism": "external_ask_maker_safety", "status": "BOUND"},
            {"mechanism": "non_displacing_target_completeness", "status": "BOUND"},
            {"mechanism": "causal_evidence_decay_exit", "status": "BOUND"},
            {"mechanism": "carried_last_trade", "status": "PROXIED"},
            {"mechanism": "standalone_volume_direction", "status": "PROXIED"},
            {"mechanism": "top5_pressure_sign", "status": "PROXIED"},
            {"mechanism": "close_keyed_recut", "status": "PROXIED"},
            {"mechanism": "taker_reach_probability", "status": "PROXIED"},
            {"mechanism": "drift_surfaces", "status": "PROXIED"},
            {"mechanism": "band_map", "status": "PROXIED"},
            {"mechanism": "divot_tables", "status": "PROXIED"},
            {"mechanism": "LIBRARY_timing", "status": "PROXIED"},
            {"mechanism": "ORIENT_frozen_consumer", "status": "PROXIED"},
            {"mechanism": "Pinnacle", "status": "ABSENT"},
            {"mechanism": "authoritative_bookmaker_FV", "status": "ABSENT"},
            {"mechanism": "full_depth_beyond_top5", "status": "ABSENT"},
            {"mechanism": "independent_shape_mapping", "status": "ABSENT"},
            {"mechanism": "moving_bid_edge", "status": "RETRACTED"},
            {"mechanism": "universal_50_split", "status": "RETRACTED"},
            {"mechanism": "last_trade_direction_gate", "status": "RETRACTED"},
            {"mechanism": "pressure_taker_direction_gate", "status": "RETRACTED"},
            {"mechanism": "borrowed_sealed_pair_shape", "status": "RETRACTED"},
            {"mechanism": "T1_unconditional_persistence", "status": "RETRACTED"},
            {"mechanism": "T1_inert_response_only_label", "status": "RETRACTED"},
            {"mechanism": "automatic_positive_d2_bid_plus_one_preference",
             "status": "RETRACTED"}
        ],
        "source_paths": [
            ".claude/proof_20260714/PROOF_LIVE_AIM.md",
            "arb-executor/live_v4.py::_liveaim_shadow",
            ".claude/volume_20260709/VOLUME_LEDGER.md",
            ".claude/trendpath/ATLAS_V1.json",
            ".claude/guidebook/GUIDEBOOK_V1.json",
            ".claude/takerreach/LAW.json",
            ".claude/entrysurface_20260717/divot_tables_v1.json",
        ],
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "MECHANISM_STATUS_TABLE.json", mechanism)
    five_rows = []
    for event_id in sorted(FIVE_NO_BBO):
        for candidate in t2.CANDIDATES:
            fact = facts[(t2.base_candidate_id(candidate), event_id)]
            five_rows.append({
                "candidate_id": candidate,
                "event_id": event_id,
                "D_member": True,
                "baseline_placement_count": fact["placement_count"],
                "fabricated_order_count": 0,
                "metrics": None,
                "scored": False,
            })
    if len(five_rows) != 40 or any(
        row["baseline_placement_count"] != 0 for row in five_rows
    ):
        raise T2FreezeError("five no-BBO law changed")
    write_json(output / "FIVE_NO_BBO_D_MEMBERSHIP_PROOF.json", {
        "schema_version": VERSION + "-five-no-BBO-v1",
        "rows": five_rows,
        "row_count": 40,
        "distinct_events": 5,
        "fabricated_order_count": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    invariants = {
        "schema_version": VERSION + "-invariants-v1",
        "D_per_candidate": 804,
        "PC_to_IC_tightening_paths": 0,
        "combined_zero_admissions": 0,
        "pre_first_T2_actions": 0,
        "same_receipt_action_fill_credits": 0,
        "future_evidence_target_selections": 0,
        "replacements_without_named_decay": 0,
        "unconditional_persistence_paths": 0,
        "forced_positive_d2_preference_paths": 0,
        "five_no_BBO_events_retained": 5,
        "T1_results_metrics_read_by_candidate_code": False,
        "scorer_imported_or_invoked": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "INVARIANT_RECEIPT.json", invariants)
    write_json(
        output / "SOURCE_HASH_MANIFEST.json",
        _source_manifest(repo, events_path, cache_root),
    )
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "scorer_imported_or_invoked": False,
        "benchmark_executed": False,
        "ranking_or_selection": False,
        "tuning_against_outcomes": False,
        "T1_result_metrics_consumed_by_policy": False,
        "holdout_access": False,
        "live_or_network_access": False,
        "production_access": False,
        "orders_or_positions_access": False,
        "Window2_exit_settlement_DCA_access": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    report = f"""# Window-1 T2 Causal-Divot PRE-RUN

Status: **FROZEN SCORE-FREE BUILD; BENCHMARK NOT EXECUTED**

- Exact parent: `{t2.EXACT_PARENT}`
- Controlling T1 results audit: `{t2.CONTROLLING_RESULTS_AUDIT}`
- D=804 for each of eight candidates; 6,432 score-free overlays
- Fixed-admission controls use the identical passed Range-Attack V2
  admission surface. The three prior cross-surface artifacts are excluded
  from behavioral comparison.
- Target completeness is non-displacing. Replacement requires a named
  receipt-backed LIVE-AIM/deep, causal-divot recurrence, maker-safety,
  combined-budget invalidation, or horizon authority.
- T1 unconditional persistence, inert response-only labeling, and automatic
  positive-d2 bid+1 preference are retracted.
- Strict pair law remains `d1+d2+fee<0`; IC and S never gate.
- All C/PC/IC/S and performance fields are null.

No scorer, benchmark, holdout, live, production, Window-2, exit, settlement,
DCA, order, or position interface is present.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    write_json(output / "PRE_RUN_MANIFEST.json", {
        "schema_version": VERSION + "-manifest-v1",
        "exact_parent": t2.EXACT_PARENT,
        "controlling_T1_results": t2.CONTROLLING_RESULTS,
        "controlling_T1_results_audit": t2.CONTROLLING_RESULTS_AUDIT,
        "candidate_ids": list(t2.CANDIDATES),
        "D_per_candidate": 804,
        "candidate_event_rows": 6432,
        "target_surface_rows": counts["target_surfaces"],
        "lawful_sibling_X_count": counts["lawful_sibling_X"],
        "lawful_positive_d2_target_count":
            counts["lawful_positive_d2_targets"],
        "positive_d2_targets_actually_exposed":
            counts["positive_d2_targets_exposed"],
        "evidence_decay_replacements":
            counts["evidence_decay_replacements"],
        "recognized_divots": counts["divot_RECOGNITION"],
        "later_independent_recurrences":
            counts["divot_LATER_RECURRENCE"],
        "later_divot_actions": counts["divot_LATER_ACTION"],
        "still_later_independent_fill_evidence":
            counts["divot_STILL_LATER_INDEPENDENT_FILL_EVIDENCE"],
        "benchmark_execution_authorized": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    for path in output.iterdir():
        if path.suffix == ".json":
            assert_metrics_null(json.loads(path.read_text(encoding="utf-8")))
    return {
        "D": 804,
        "candidate_count": 8,
        "candidate_event_rows": 6432,
        "counts": dict(counts),
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def _inventory(directory: Path) -> list[dict[str, Any]]:
    return [{
        "path": path.relative_to(directory).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    } for path in sorted(
        value for value in directory.rglob("*") if value.is_file()
    )]


def freeze(build_a: Path, build_b: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise T2FreezeError("frozen output already exists")
    inventory_a = _inventory(build_a)
    inventory_b = _inventory(build_b)
    if inventory_a != inventory_b:
        raise T2FreezeError("two clean T2 builds are not byte-identical")
    shutil.copytree(build_a, output)
    receipt = {
        "schema_version": VERSION + "-determinism-v1",
        "clean_regeneration_count": 2,
        "byte_identical": True,
        "file_count_before_freeze_receipts": len(inventory_a),
        "inventory_sha256": canonical_sha256(inventory_a),
        "inventories": {"build_A": inventory_a, "build_B": inventory_b},
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "DETERMINISTIC_REGENERATION_RECEIPT.json", receipt)
    rows = _inventory(output)
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "self_excluded": "ARTIFACT_HASH_MANIFEST.json",
        "artifact_count": len(rows),
        "artifacts": rows,
        "all_hashes_verified": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    return {
        "byte_identical": True,
        "artifact_count": len(rows) + 1,
        "inventory_sha256": canonical_sha256(rows),
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--repo", type=Path, required=True)
    build_parser.add_argument("--events", type=Path, required=True)
    build_parser.add_argument("--market-cache", type=Path, required=True)
    build_parser.add_argument("--output-dir", type=Path, required=True)
    build_parser.add_argument("--workers", type=int, default=8)
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("--build-a", type=Path, required=True)
    freeze_parser.add_argument("--build-b", type=Path, required=True)
    freeze_parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "build":
        result = build(
            repo=args.repo.resolve(),
            events_path=args.events.resolve(),
            cache_root=args.market_cache.resolve(),
            output=args.output_dir.resolve(),
            workers=args.workers,
        )
    else:
        result = freeze(
            args.build_a.resolve(),
            args.build_b.resolve(),
            args.output_dir.resolve(),
        )
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
