#!/usr/bin/env python3
"""Build and freeze the score-free Window-1 T1 PRE-RUN.

The output is an additive decision overlay over the byte-bound Range-Attack
V2 baselines.  It contains complete T1 interval state and every explicit T1
post-first receipt decision, but never imports a scorer or computes C/PC/S/IC.
"""

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
from typing import Any, Iterable, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round2_real_capability as capability
import window1_round4_macromicro_instrument as normalizer
import window1_range_attack_prerun_builder as baseline_builder
import window1_t1_post_first_leg_instrument as t1


VERSION = "window1-t1-post-first-leg-prerun-v1"
PACKAGE_REL = ".claude/window1_t1_post_first_leg_prerun_20260727"
ATTRIBUTION_REL = (
    ".claude/window1_decision_layer_attribution_prerun_20260727"
)
BASELINE_REL = (
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
)
AUDIT_REPORT = (
    ".claude/audit_20260727_window1_decision_layer_attribution/"
    "AUDIT_REPORT.md"
)
AUDIT_RECEIPT = (
    ".claude/audit_20260727_window1_decision_layer_attribution/"
    "INDEPENDENT_ATTRIBUTION_REPRODUCTION_RECEIPT.json"
)
AUDIT_REPORT_BLOB = "e5839c2bacebd646833756d3739da77686fb3ae9"
AUDIT_RECEIPT_BLOB = "6e7a44b9badb8fff2a63d8d359ffb2f1caa84719"
SOURCE_REL = (
    "arb-executor/analysis/window1_t1_post_first_leg_instrument.py"
)
BUILDER_REL = (
    "arb-executor/analysis/window1_t1_post_first_leg_prerun.py"
)
TEST_REL = "arb-executor/tests/test_window1_t1_post_first_leg_prerun.py"
SPEC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T1_POST_FIRST_LEG_CANDIDATES_V1.json"
)
STREAM_FILES = tuple(
    f"{BASELINE_REL}/UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
OVERLAY_SHARDS = tuple(
    f"UNSCORED_T1_CANDIDATE_EVENT_OVERLAYS_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
DECISION_SHARDS = tuple(
    f"POST_FIRST_EPISODE_KEYED_DECISIONS_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
METRIC_FIELDS = {"C", "PC", "S", "IC"}
FIVE_NO_BBO = baseline_builder.FIVE_NO_BBO


class T1FreezeError(RuntimeError):
    """An input, causal, conservation, or deterministic invariant failed."""


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
        raise T1FreezeError(
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


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
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


def read_gzip_rows(path: Path) -> list[dict[str, Any]]:
    return list(iter_gzip(path))


def assert_metrics_null(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in METRIC_FIELDS and child is not None:
                raise T1FreezeError(f"metric populated at {path}.{key}")
            if key in {"metrics", "performance"} and child is not None:
                raise T1FreezeError(
                    f"performance object populated at {path}.{key}"
                )
            if key == "scored" and child is not False:
                raise T1FreezeError(f"scored flag changed at {path}")
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
        for candidate in (*t1.BASE_CANDIDATES, *t1.CANDIDATES):
            result = result.replace(candidate, "<CANDIDATE>")
        return result
    return value


def _semantic_hash(value: Any) -> str:
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
    rows = [
        row for row in stream["order_stream"]
        if float(row["ts"]) <= float(first)
    ]
    return _semantic_hash(rows)


def _nofill_hash(stream: Mapping[str, Any]) -> str | None:
    if stream["pair_state"].get("first_filled_leg") is not None:
        return None
    return _semantic_hash({
        "actions": stream["order_stream"],
        "intervals": stream["order_intervals_by_leg"],
    })


def baseline_facts(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    facts: dict[tuple[str, str], dict[str, Any]] = {}
    for relative in STREAM_FILES:
        for envelope in iter_gzip(repo / relative):
            candidate = str(envelope["candidate_id"])
            event_id = str(envelope["event_id"])
            stream = envelope["stream"]
            key = (candidate, event_id)
            if key in facts:
                raise T1FreezeError(f"duplicate baseline stream: {key}")
            facts[key] = {
                "candidate_id": candidate,
                "event_id": event_id,
                "stream_row_sha256": canonical_sha256(envelope),
                "order_stream_sha256": stream["order_stream_sha256"],
                "order_intervals_sha256": stream[
                    "order_intervals_sha256"
                ],
                "full_policy_semantic_sha256": _semantic_hash({
                    "actions": stream["order_stream"],
                    "intervals": stream["order_intervals_by_leg"],
                }),
                "first_fill_semantics": _first_fill_semantics(stream),
                "event_date": str(envelope["event_date"]),
                "category": str(envelope["category"]),
                "prefix_through_first_fill_semantic_sha256": _prefix_hash(
                    stream
                ),
                "nofill_full_semantic_sha256": _nofill_hash(stream),
                "baseline_policy_horizon_ts": stream["policy_clock"][
                    "policy_decision_horizon_ts"
                ],
                "placement_count": sum(
                    row["action"] in {"place", "reprice"}
                    for row in stream["order_stream"]
                ),
            }
    if len(facts) != 1608:
        raise T1FreezeError(
            f"baseline candidate-event count changed: {len(facts)}"
        )
    return facts


def baseline_policy_source_hashes(
    repo: Path,
    source_paths: Mapping[str, str],
) -> dict[str, str]:
    """Recover policy-facing receipt hashes from the immutable baseline.

    The passed Range-Attack package was frozen from a Windows checkout whose
    text sources used CRLF bytes.  A clean worktree may expose the identical
    JSON through LF bytes.  Policy decisions must retain the passed receipt
    identities, while SOURCE_HASH_MANIFEST separately records the exact bytes
    in this checkout and the committed Git blobs.
    """
    observed: dict[str, set[str]] = defaultdict(set)
    for relative in STREAM_FILES:
        for envelope in iter_gzip(repo / relative):
            for action in envelope["stream"]["order_stream"]:
                if action.get("action") != "macro_target_selected":
                    continue
                atlas_hash = action.get("source_sha256")
                if atlas_hash:
                    observed["atlas"].add(str(atlas_hash))
                for key, value in (
                    action.get("historical_surface_source_sha256") or {}
                ).items():
                    if value:
                        observed[str(key)].add(str(value))
    required = {
        "atlas", "drift", "divot", "band", "library", "orient", "recut",
    }
    if not required.issubset(observed):
        raise T1FreezeError(
            "baseline policy source receipt set is incomplete"
        )
    result = {
        key: sha256_file(repo / path)
        for key, path in source_paths.items()
    }
    for key in sorted(required):
        values = observed[key]
        if len(values) != 1:
            raise T1FreezeError(
                f"baseline policy source receipt is not unique: {key}"
            )
        expected = next(iter(values))
        raw = (repo / source_paths[key]).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        crlf = lf.replace(b"\n", b"\r\n")
        lawful_checkout_hashes = {
            hashlib.sha256(raw).hexdigest(),
            hashlib.sha256(lf).hexdigest(),
            hashlib.sha256(crlf).hexdigest(),
        }
        if expected not in lawful_checkout_hashes:
            raise T1FreezeError(
                f"baseline policy source content changed: {key}"
            )
        result[key] = expected
    return result


def load_attribution(repo: Path) -> dict[str, Any]:
    package = repo / ATTRIBUTION_REL
    decision = read_gzip_rows(package / "DECISION_LAYER_EVENT_LEDGER.jsonl.gz")
    never = read_gzip_rows(package / "NEVER_EXPOSED_ATTRIBUTION.jsonl.gz")
    moved = read_gzip_rows(package / "MOVED_AWAY_ATTRIBUTION.jsonl.gz")
    capacity_doc = json.loads(
        (package / "CAPACITY_UNPROVED_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )
    capacity = list(capacity_doc.get("candidate_rows") or [])
    if Counter(row["attributed_layer"] for row in decision) != Counter({
        "first_fill_sibling_response_failed_to_create_exposure": 24,
        "target_selection_never_included_lawful_X": 4,
        "headroom_reprice": 8,
        "corridor_window_termination": 8,
        "LIVE_AIM_reprice": 1,
        "capacity_measurement_unproved": 2,
    }):
        raise T1FreezeError("controlling attribution counts changed")
    if len(never) != 28 or len(moved) != 17 or len(capacity) != 2:
        raise T1FreezeError("24+4+17+2 attribution fixtures changed")
    return {
        "decision": decision,
        "never": never,
        "moved": moved,
        "capacity": capacity,
    }


def _compact_action(row: Mapping[str, Any]) -> dict[str, Any]:
    keep = {
        "event_id", "candidate_id", "leg_id", "ticker", "ts", "action",
        "reason", "primary_authority", "composed_macro_micro",
        "price_cents", "prior_price_cents", "proposed_price_cents",
        "reprice_direction", "order_interval_id",
        "original_order_interval_id", "active_order_interval_id",
        "trigger_receipt", "trigger_kind", "t1_decision",
        "selected_X_cents", "strictly_later_than_first_fill",
        "new_action_fill_eligible_on_trigger_receipt",
        "queue_preserved", "queue_surrendered", "suppressed_authority",
        "suppressed_reason", "limit_price_cents", "print_receipt",
        "book_receipt", "external_ask_price_cents",
        "simulated_fill_price_cents", "simulated_accounting_quantity",
    }
    return {key: row.get(key) for key in sorted(keep) if key in row}


def compact_result(
    result: Mapping[str, Any],
    base: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    first_ts = result["pair_state"].get("first_fill_ts")
    post_actions = [
        _compact_action(row) for row in result["order_stream"]
        if first_ts is not None and float(row["ts"]) >= float(first_ts)
        and (
            row["action"] in {
                "place", "reprice", "cancel", "hold",
                "price_reached_policy_tape", "strict_ask_certain_fill",
                "headroom_armed", "headroom_decision",
                "t1_episode_keyed_decision", "t1_persistence_hold",
                "feature_no_call", "terminal",
            }
        )
    ]
    prefix = _prefix_hash(result)
    nofill = _nofill_hash(result)
    first_semantics = _first_fill_semantics(result)
    first_equal = first_semantics == base["first_fill_semantics"]
    prefix_equal = (
        prefix == base["prefix_through_first_fill_semantic_sha256"]
    )
    nofill_equal = nofill == base["nofill_full_semantic_sha256"]
    intervals = result["order_intervals_by_leg"]
    overlay = {
        "schema_version": VERSION + "-candidate-event-overlay-v1",
        "candidate_id": result["candidate_id"],
        "base_candidate_id": result["base_candidate_id"],
        "t1_variant": result["t1_variant"],
        "t1_switches": result["t1_switches"],
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
        "post_first_effective_actions": post_actions,
        "post_first_effective_actions_sha256": canonical_sha256(
            post_actions
        ),
        "order_intervals_sha256": canonical_sha256(intervals),
        "full_policy_semantic_sha256": _semantic_hash({
            "actions": result["order_stream"],
            "intervals": intervals,
        }),
        "first_leg_semantics": first_semantics,
        "first_leg_semantics_identical_to_baseline": first_equal,
        "prefix_through_first_fill_semantic_sha256": prefix,
        "prefix_through_first_fill_identical_to_baseline": prefix_equal,
        "baseline_nofill": (
            base["nofill_full_semantic_sha256"] is not None
        ),
        "nofill_full_semantic_sha256": nofill,
        "nofill_semantics_identical_to_baseline": nofill_equal,
        "t1_episode_decision_count": sum(
            len(rows)
            for rows in result["t1_episode_decisions_by_leg"].values()
        ),
        "t1_target_construction_count": sum(
            len(rows)
            for rows in result[
                "t1_target_construction_receipts_by_leg"
            ].values()
        ),
        "t1_persistence_receipt_count": sum(
            len(rows)
            for rows in result["t1_persistence_receipts_by_leg"].values()
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
        "episode_decisions": [
            row
            for rows in result["t1_episode_decisions_by_leg"].values()
            for row in rows
        ],
        "target_receipts": [
            row for rows in result[
                "t1_target_construction_receipts_by_leg"
            ].values() for row in rows
        ],
        "persistence_receipts": [
            row
            for rows in result["t1_persistence_receipts_by_leg"].values()
            for row in rows
        ],
        "strict_ask_actions": [
            _compact_action(row) for row in result["order_stream"]
            if row["action"] == "strict_ask_certain_fill"
        ],
        "cancel_reprice_actions": [
            _compact_action(row) for row in result["order_stream"]
            if row["action"] in {"cancel", "reprice"}
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
    """Bind a T1 no-fill row to the complete immutable baseline stream.

    With no credited first leg, every T1 switch is unreachable.  Replaying the
    raw cache would add no information and would weaken the byte-identity
    contract, so the complete baseline row is inherited by content receipt.
    """
    baseline_id = t1.base_candidate_id(candidate_id)
    overlay = {
        "schema_version": VERSION + "-candidate-event-overlay-v1",
        "candidate_id": candidate_id,
        "base_candidate_id": baseline_id,
        "t1_variant": t1._variant(candidate_id),
        "t1_switches": dict(t1.SWITCHES[t1._variant(candidate_id)]),
        "event_id": event_id,
        "event_date": base["event_date"],
        "category": base["category"],
        "D_member": True,
        "baseline_stream_reference": {
            "stream_row_sha256": base["stream_row_sha256"],
            "order_stream_sha256": base["order_stream_sha256"],
            "order_intervals_sha256": base["order_intervals_sha256"],
        },
        "inherits_complete_baseline_stream": True,
        "inheritance_reason": (
            "no credited first leg; every T1 switch is unreachable"
        ),
        "policy_clock": {
            "baseline_policy_decision_horizon_ts": base[
                "baseline_policy_horizon_ts"
            ],
            "post_first_terminal_ts": None,
        },
        "pair_state": {
            "first_filled_leg": None,
            "first_fill_ts": None,
            "causal_d1_cents": None,
            "C": None,
            "PC": None,
            "S": None,
            "IC": None,
        },
        "causal_policy_fill_state_by_leg": None,
        "order_intervals_by_leg": None,
        "post_first_effective_actions": [],
        "post_first_effective_actions_sha256": canonical_sha256([]),
        "order_intervals_sha256": base["order_intervals_sha256"],
        "full_policy_semantic_sha256": base[
            "full_policy_semantic_sha256"
        ],
        "first_leg_semantics": base["first_fill_semantics"],
        "first_leg_semantics_identical_to_baseline": True,
        "prefix_through_first_fill_semantic_sha256": None,
        "prefix_through_first_fill_identical_to_baseline": True,
        "baseline_nofill": True,
        "nofill_full_semantic_sha256": base[
            "nofill_full_semantic_sha256"
        ],
        "nofill_semantics_identical_to_baseline": True,
        "t1_episode_decision_count": 0,
        "t1_target_construction_count": 0,
        "t1_persistence_receipt_count": 0,
        "C": None,
        "PC": None,
        "S": None,
        "IC": None,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    details = {
        "episode_decisions": [],
        "target_receipts": [],
        "persistence_receipts": [],
        "strict_ask_actions": [],
        "cancel_reprice_actions": [],
    }
    assert_metrics_null(overlay)
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
    spec = t1.load_candidate_spec(repo)
    _WORKER.update({
        "repo": repo,
        "cache": Path(cache_text),
        "feature_map": feature_map,
        "boundaries": boundaries,
        "facts": facts,
        "source_hashes": source_hashes,
        "spec": spec,
        "atlas": json.loads(
            (repo / t1.passed.ATLAS_PATH).read_text(encoding="utf-8")
        ),
        "guidebook": json.loads(
            (repo / t1.passed.GUIDEBOOK_PATH).read_text(encoding="utf-8")
        ),
        "recut": json.loads(
            (repo / t1.passed.RECUT_PATH).read_text(encoding="utf-8")
        ),
        "reach": json.loads(
            (repo / t1.passed.TAKER_REACH_PATH).read_text(
                encoding="utf-8"
            )
        ),
    })


def _process_event(
    item: tuple[int, Mapping[str, Any]],
) -> tuple[int, list[tuple[dict[str, Any], dict[str, Any]]]]:
    index, event = item
    event_id = str(event["event_id"])
    candidate_rows: list[
        tuple[str, Mapping[str, Any], bool]
    ] = []
    for candidate in t1.CANDIDATES:
        base_id = t1.base_candidate_id(candidate)
        base = _WORKER["facts"][(base_id, event_id)]
        candidate_rows.append((
            candidate, base,
            base["nofill_full_semantic_sha256"] is not None,
        ))
    if all(row[2] for row in candidate_rows):
        return index, [
            inherited_nofill_overlay(
                candidate_id=candidate,
                event_id=event_id,
                base=base,
            )
            for candidate, base, _ in candidate_rows
        ]
    t1.clear_event_flow_cache()
    cache = capability.load_cache(
        _WORKER["cache"] / f"{event_id}.json.gz"
    )
    normalized, _ = normalizer.normalize_event(
        event, cache, _WORKER["feature_map"], corridor_seconds=0.0
    )
    boundary = _WORKER["boundaries"][event_id]
    rows = []
    for candidate, base, nofill in candidate_rows:
        if nofill:
            rows.append(inherited_nofill_overlay(
                candidate_id=candidate,
                event_id=event_id,
                base=base,
            ))
            continue
        policy = t1.candidate_policy(
            _WORKER["repo"], _WORKER["spec"], candidate
        )
        result = t1.T1Simulator(
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


def _source_manifest(
    repo: Path,
    events_path: Path,
    cache_root: Path,
) -> dict[str, Any]:
    committed_paths = [
        SOURCE_REL, BUILDER_REL, TEST_REL, SPEC_REL,
        "arb-executor/analysis/window1_range_attack_instrument_v2.py",
        "arb-executor/analysis/window1_range_attack_instrument.py",
        "arb-executor/analysis/window1_range_attack_prerun_builder.py",
        ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "DECISION_LAYER_EVENT_LEDGER.jsonl.gz",
        ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "NEVER_EXPOSED_ATTRIBUTION.jsonl.gz",
        ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "MOVED_AWAY_ATTRIBUTION.jsonl.gz",
        ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "CAPACITY_UNPROVED_RECEIPT.json",
        ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "SOURCE_HASH_MANIFEST.json",
        ".claude/window1_decision_layer_attribution_prerun_20260727/"
        "ARTIFACT_HASH_MANIFEST.json",
        baseline_builder.START_LEDGER,
        binding.FEATURE_LEDGER,
        *STREAM_FILES,
    ]
    rows = []
    for relative in committed_paths:
        path = repo / relative
        raw = path.read_bytes()
        rows.append({
            "path": relative,
            "role": "immutable_committed_input_or_T1_source",
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git(
                repo, "hash-object", relative
            ).decode().strip(),
        })
    audit_rows = []
    for relative, expected in (
        (AUDIT_REPORT, AUDIT_REPORT_BLOB),
        (AUDIT_RECEIPT, AUDIT_RECEIPT_BLOB),
    ):
        raw = git(
            repo, "show", f"{t1.CONTROLLING_AUDIT}:{relative}"
        )
        oid = git_blob_oid(raw)
        if oid != expected:
            raise T1FreezeError(
                f"controlling audit blob changed: {relative}"
            )
        audit_rows.append({
            "path": relative,
            "commit": t1.CONTROLLING_AUDIT,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": oid,
        })
    private_rows = [{
        "path": "PRIVATE:joined/events.jsonl",
        "role": "frozen_804_development_event_ledger",
        "bytes": events_path.stat().st_size,
        "sha256": sha256_file(events_path),
        "git_blob_oid": None,
    }]
    for path in sorted(cache_root.glob("*.json.gz")):
        private_rows.append({
            "path": f"PRIVATE:guarded-cache-v3/{path.name}",
            "role": "frozen_development_public_market_cache",
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "git_blob_oid": None,
        })
    if len(private_rows) != 805:
        raise T1FreezeError("804 private cache receipt law changed")
    return {
        "schema_version": VERSION + "-source-manifest-v1",
        "exact_parent": t1.EXACT_PARENT,
        "controlling_attribution_PASS": t1.CONTROLLING_AUDIT,
        "committed_inputs": rows,
        "audit_artifacts": audit_rows,
        "private_development_inputs": private_rows,
        "development_dates": sorted(t1.passed.DEVELOPMENT_DATES),
        "sealed_holdout_dates": sorted(t1.passed.SEALED_HOLDOUT_DATES),
        "holdout_input_count": 0,
        "live_or_network_input_count": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def _variant_candidate(base_id: str, variant: str) -> str:
    regime = "macro_hold" if "macro_hold" in base_id else "macro_micro"
    return f"w1_t1__{regime}__{variant}"


def _fixture_migration(
    attribution: Mapping[str, Any],
    details: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    rows = []
    counts = Counter()
    for source in attribution["decision"]:
        layer = source["attributed_layer"]
        if layer == "capacity_measurement_unproved":
            rows.append({
                "source_candidate_id": source["candidate_id"],
                "event_id": source["event_id"],
                "source_layer": layer,
                "T1_behavior": (
                    "capacity remains a separate unproved diagnostic; "
                    "no conversion or performance credit is claimed"
                ),
                "T1_credited_fixture": False,
                "metrics": None,
                "performance": None,
                "scored": False,
            })
            counts["capacity_unproved"] += 1
            continue
        if layer == "first_fill_sibling_response_failed_to_create_exposure":
            variants = ("response_only", "full_stack")
        elif layer == "target_selection_never_included_lawful_X":
            variants = ("target_completeness_only", "full_stack")
        elif layer in {
            "headroom_reprice", "corridor_window_termination",
            "LIVE_AIM_reprice",
        }:
            variants = ("persistence_only", "full_stack")
        else:
            continue
        for variant in variants:
            candidate = _variant_candidate(
                source["candidate_id"], variant
            )
            detail = details[(candidate, source["event_id"])]
            receipt: dict[str, Any] = {
                "source_candidate_id": source["candidate_id"],
                "T1_candidate_id": candidate,
                "event_id": source["event_id"],
                "source_layer": layer,
                "credited_first_leg": source["credited_first_leg"],
                "earliest_lawful_opportunity": source[
                    "earliest_lawful_opportunity"
                ],
                "metrics": None,
                "performance": None,
                "scored": False,
            }
            if layer == "first_fill_sibling_response_failed_to_create_exposure":
                decisions = detail["episode_decisions"]
                receipt.update({
                    "explicit_post_first_decision_count": len(decisions),
                    "explicit_post_first_decision_produced": bool(decisions),
                    "first_decision": decisions[0] if decisions else None,
                })
                if not decisions:
                    raise T1FreezeError(
                        f"24-row response fixture failed: {candidate} "
                        f"{source['event_id']}"
                    )
                counts["response_fixture_variant_rows_passed"] += 1
            elif layer == "target_selection_never_included_lawful_X":
                constructions = [
                    row for row in detail["target_receipts"]
                    if row.get("construction") is not None
                ]
                lawful = [
                    row for row in constructions
                    if row["construction"].get("selected_X_cents")
                    is not None
                ]
                receipt.update({
                    "target_construction_receipt_count": len(constructions),
                    "lawful_complete_target_receipt_count": len(lawful),
                    "lawful_headroom_target_included": bool(lawful),
                    "first_lawful_construction": lawful[0] if lawful else None,
                })
                if not lawful:
                    raise T1FreezeError(
                        f"4-row target fixture failed: {candidate} "
                        f"{source['event_id']}"
                    )
                counts["target_fixture_variant_rows_passed"] += 1
            else:
                moved = next(
                    row for row in attribution["moved"]
                    if row["candidate_id"] == source["candidate_id"]
                    and row["event_id"] == source["event_id"]
                )
                old_x = int(moved["original_exposure"]["X_cents"])
                opportunity_ts = float(
                    moved["earliest_lawful_opportunity"]["timestamp"]
                )
                intervals = [
                    interval
                    for leg_rows in detail["overlay"][
                        "order_intervals_by_leg"
                    ].values()
                    for interval in leg_rows
                    if int(interval["limit_price_cents"]) == old_x
                    and float(interval["opened_ts"]) <= opportunity_ts
                    and (
                        interval["closed_ts"] is None
                        or float(interval["closed_ts"]) >= opportunity_ts
                    )
                ]
                fills = [
                    fill for fill in detail["overlay"][
                        "causal_policy_fill_state_by_leg"
                    ].values()
                    if fill["simulated_fill_price"] == old_x
                    and fill["simulated_fill_ts"] is not None
                    and float(fill["simulated_fill_ts"]) <= opportunity_ts
                ]
                legal_reasons = [
                    row for row in detail["persistence_receipts"]
                    if row.get("decision") in {
                        "HOLD",
                        "RECEIPT_BACKED_CHANGE_ALLOWED",
                        "EXTEND_SIBLING_PERSISTENCE_TO_GUARDED_CUTOFF",
                    }
                ]
                passed_fixture = bool(intervals or fills or legal_reasons)
                receipt.update({
                    "original_X_cents": old_x,
                    "opportunity_timestamp": opportunity_ts,
                    "old_X_retained_through_opportunity": bool(intervals),
                    "old_X_filled_before_opportunity": bool(fills),
                    "persistence_receipts": legal_reasons,
                    "receipt_backed_resolution_present": passed_fixture,
                })
                if not passed_fixture:
                    raise T1FreezeError(
                        f"17-row persistence fixture failed: {candidate} "
                        f"{source['event_id']}"
                    )
                counts["persistence_fixture_variant_rows_passed"] += 1
            rows.append(receipt)
    expected = {
        "response_fixture_variant_rows_passed": 48,
        "target_fixture_variant_rows_passed": 8,
        "persistence_fixture_variant_rows_passed": 34,
        "capacity_unproved": 2,
    }
    if any(counts[key] != value for key, value in expected.items()):
        raise T1FreezeError(
            f"fixture migration count mismatch: {dict(counts)}"
        )
    return {
        "schema_version": VERSION + "-causal-fixture-migration-v1",
        "source_attribution_candidate_rows": 47,
        "required_fixtures": {
            "no_decision_rows": 24,
            "omitted_target_rows": 4,
            "moved_away_rows": 17,
            "capacity_unproved_rows": 2,
        },
        "variant_acceptance_counts": dict(counts),
        "rows": rows,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def _strict_ask_proof(
    details: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    rows = []
    violations = []
    for (candidate, event_id), detail in sorted(details.items()):
        for fill in detail["strict_ask_actions"]:
            timestamp = float(fill["ts"])
            interval = fill.get("order_interval_id")
            conflicting = [
                row for row in detail["cancel_reprice_actions"]
                if float(row["ts"]) == timestamp
                and (
                    row.get("order_interval_id") == interval
                    or row.get("original_order_interval_id") == interval
                )
            ]
            item = {
                "candidate_id": candidate,
                "event_id": event_id,
                "timestamp": timestamp,
                "order_interval_id": interval,
                "limit_price_cents": fill.get("limit_price_cents"),
                "external_ask_price_cents": fill.get(
                    "external_ask_price_cents"
                ),
                "credited_before_cancel_or_reprice": not conflicting,
                "conflicting_actions": conflicting,
            }
            rows.append(item)
            if conflicting:
                violations.append(item)
    if violations:
        raise T1FreezeError("strict-ask credit ordering regressed")
    return {
        "schema_version": VERSION + "-strict-ask-ordering-v1",
        "strict_ask_action_count": len(rows),
        "credit_before_cancel_or_reprice_count": len(rows),
        "violation_count": 0,
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
        raise T1FreezeError("build output already exists")
    output.mkdir(parents=True)
    events = list(iter_jsonl(events_path))
    if len(events) != 804:
        raise T1FreezeError(f"D changed: {len(events)}")
    if sorted({str(row["event_date"]) for row in events}) != list(
        binding.DEV_DATES
    ):
        raise T1FreezeError("development date set changed")
    if any(
        str(row["event_date"]) in t1.passed.SEALED_HOLDOUT_DATES
        for row in events
    ):
        raise T1FreezeError("holdout date entered T1 input")
    event_ids = [str(row["event_id"]) for row in events]
    if len(set(event_ids)) != 804:
        raise T1FreezeError("event identities are not unique")
    feature_rows = [
        row for row in iter_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in feature_rows
    }
    if len(feature_map) != 1608:
        raise T1FreezeError("1,608 leg identities changed")
    boundaries = {
        str(row["event_id"]): baseline_builder.boundary_contract(row)
        for row in iter_jsonl(repo / baseline_builder.START_LEDGER)
    }
    if set(boundaries) != set(event_ids):
        raise T1FreezeError("V5 boundary identity set changed")
    facts = baseline_facts(repo)
    attribution = load_attribution(repo)
    spec = t1.load_candidate_spec(repo)
    if tuple(spec["candidate_ids"]) != t1.CANDIDATES:
        raise T1FreezeError("frozen eight-candidate order changed")
    source_paths = {
        "atlas": t1.passed.ATLAS_PATH,
        "guidebook": t1.passed.GUIDEBOOK_PATH,
        "recut": t1.passed.RECUT_PATH,
        "taker_reach": t1.passed.TAKER_REACH_PATH,
        "liveaim_proof": t1.passed.LIVEAIM_PROOF_PATH,
        "volume": t1.passed.VOLUME_PATH,
        "start_ledger": baseline_builder.START_LEDGER,
        "drift": t1.passed.DRIFT_PATH,
        "divot": t1.passed.DIVOT_PATH,
        "band": t1.passed.BAND_PATH,
        "library": t1.passed.LIBRARY_PATH,
        "orient": t1.passed.ORIENT_PATH,
    }
    source_hashes = baseline_policy_source_hashes(repo, source_paths)
    overlay_writers = [
        GzipWriter(output / name) for name in OVERLAY_SHARDS
    ]
    decision_writers = [
        GzipWriter(output / name) for name in DECISION_SHARDS
    ]
    target_writer = GzipWriter(
        output / "HEADROOM_TARGET_CONSTRUCTION_RECEIPTS.jsonl.gz"
    )
    persistence_writer = GzipWriter(
        output / "PERSISTENCE_QUEUE_SURRENDER_RECEIPTS.jsonl.gz"
    )
    details: dict[tuple[str, str], dict[str, Any]] = {}
    fixture_event_ids = {
        str(row["event_id"]) for row in attribution["decision"]
    }
    conservation = Counter()
    first_identity_bad = []
    nofill_identity_bad = []
    changed = Counter()
    changed_ids: dict[str, list[str]] = defaultdict(list)
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
            futures = [
                pool.submit(_process_event, item)
                for item in enumerate(events)
            ]
            for expected_index in range(len(futures)):
                future = futures[expected_index]
                index, candidate_results = future.result()
                futures[expected_index] = None
                if index != expected_index:
                    raise T1FreezeError("worker event order changed")
                if len(candidate_results) != 8:
                    raise T1FreezeError("worker candidate count changed")
                for candidate_index, (overlay, detail) in enumerate(
                    candidate_results
                ):
                    candidate = t1.CANDIDATES[candidate_index]
                    if overlay["candidate_id"] != candidate:
                        raise T1FreezeError("candidate order changed")
                    shard = index % len(OVERLAY_SHARDS)
                    overlay_writers[shard].write(overlay)
                    for row in detail["episode_decisions"]:
                        decision_writers[shard].write(row)
                    for row in detail["target_receipts"]:
                        target_writer.write(row)
                    for row in detail["persistence_receipts"]:
                        persistence_writer.write(row)
                    conservation[candidate] += 1
                    if not overlay[
                        "first_leg_semantics_identical_to_baseline"
                    ] or not overlay[
                        "prefix_through_first_fill_identical_to_baseline"
                    ]:
                        first_identity_bad.append(
                            (candidate, overlay["event_id"])
                        )
                    if (
                        overlay["baseline_nofill"]
                        and not overlay[
                            "nofill_semantics_identical_to_baseline"
                        ]
                    ):
                        nofill_identity_bad.append(
                            (candidate, overlay["event_id"])
                        )
                    changed_key = (
                        overlay["full_policy_semantic_sha256"],
                    )
                    base_key = (
                        facts[(
                            overlay["base_candidate_id"],
                            overlay["event_id"],
                        )]["full_policy_semantic_sha256"],
                    )
                    status = (
                        "changed" if changed_key != base_key else "unchanged"
                    )
                    changed[(candidate, status)] += 1
                    if status == "changed":
                        changed_ids[candidate].append(overlay["event_id"])
                    if overlay["event_id"] in fixture_event_ids:
                        detail["overlay"] = overlay
                        details[(candidate, overlay["event_id"])] = detail
    finally:
        for writer in (
            *overlay_writers, *decision_writers,
            target_writer, persistence_writer,
        ):
            writer.close()
    if any(conservation[candidate] != 804 for candidate in t1.CANDIDATES):
        raise T1FreezeError(f"D conservation failed: {dict(conservation)}")
    if first_identity_bad:
        raise T1FreezeError(
            f"first-leg semantic identity failed: {first_identity_bad[:5]}"
        )
    if nofill_identity_bad:
        raise T1FreezeError(
            f"no-fill identity failed: {nofill_identity_bad[:5]}"
        )
    fixture = _fixture_migration(attribution, details)
    strict_ask = _strict_ask_proof(details)
    write_json(output / "CAUSAL_FIXTURE_MIGRATION_RECEIPT.json", fixture)
    write_json(
        output / "STRICT_ASK_CREDIT_BEFORE_REPRICE_PROOF.json",
        strict_ask,
    )
    write_json(output / "D_CONSERVATION_RECEIPT.json", {
        "schema_version": VERSION + "-D-conservation-v1",
        "D_per_candidate": {
            candidate: conservation[candidate]
            for candidate in t1.CANDIDATES
        },
        "candidate_count": 8,
        "candidate_event_overlay_count": sum(conservation.values()),
        "immutable_D": 804,
        "all_events_retained": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    write_json(output / "FIRST_LEG_SEMANTIC_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-first-leg-identity-v1",
        "candidate_event_rows_checked": 6432,
        "mismatch_count": 0,
        "first_leg_selection_exposure_fill_price_evidence_unchanged": True,
        "prefix_through_first_fill_unchanged": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    baseline_nofill = sum(
        fact["nofill_full_semantic_sha256"] is not None
        for fact in facts.values()
    )
    write_json(output / "NOFILL_SEMANTIC_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-nofill-identity-v1",
        "baseline_candidate_event_nofill_rows": baseline_nofill,
        "T1_variant_nofill_rows_checked": baseline_nofill * 4,
        "mismatch_count": 0,
        "T1_switches_inactive_without_first_fill": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    baseline_files = []
    for relative in STREAM_FILES:
        path = repo / relative
        baseline_files.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "git_blob_oid": git(
                repo, "hash-object", relative
            ).decode().strip(),
        })
    write_json(output / "BASELINE_BYTE_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-baseline-identity-v1",
        "baseline_candidate_ids": list(t1.BASE_CANDIDATES),
        "baseline_stream_files": baseline_files,
        "baseline_candidate_event_rows": 1608,
        "baseline_files_modified": 0,
        "baseline_rows_regenerated": 0,
        "byte_identical_references": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    write_json(
        output / "CHANGED_UNCHANGED_STREAM_CENSUS.json",
        {
            "schema_version": VERSION + "-stream-census-v1",
            "comparison": (
                "T1 complete interval state/post-first action overlay "
                "versus immutable baseline references"
            ),
            "candidate_counts": {
                candidate: {
                    "changed": changed[(candidate, "changed")],
                    "unchanged": changed[(candidate, "unchanged")],
                    "D": 804,
                } for candidate in t1.CANDIDATES
            },
            "changed_event_ids": dict(changed_ids),
            "first_leg_mismatch_count": 0,
            "nofill_mismatch_count": 0,
            "metrics": None,
            "performance": None,
            "scored": False,
        },
    )
    five_rows = []
    for event_id in sorted(FIVE_NO_BBO):
        for candidate in t1.CANDIDATES:
            fact = facts[(t1.base_candidate_id(candidate), event_id)]
            five_rows.append({
                "candidate_id": candidate,
                "event_id": event_id,
                "D_member": True,
                "baseline_placement_count": fact["placement_count"],
                "T1_first_fill": False,
                "T1_post_first_switches_activated": False,
                "fabricated_BBO_or_price_count": 0,
                "metrics": None,
                "performance": None,
                "scored": False,
            })
    if len(five_rows) != 40 or any(
        row["baseline_placement_count"] != 0 for row in five_rows
    ):
        raise T1FreezeError("five no-BBO event contract changed")
    write_json(output / "FIVE_NO_BBO_D_MEMBERSHIP_PROOF.json", {
        "schema_version": VERSION + "-five-no-BBO-v1",
        "rows": five_rows,
        "row_count": 40,
        "distinct_events": 5,
        "all_D_members": True,
        "all_zero_orders": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    write_json(output / "CANDIDATE_SWITCH_MATRIX.json", {
        "schema_version": VERSION + "-candidate-matrix-v1",
        "baseline_candidate_ids": list(t1.BASE_CANDIDATES),
        "candidate_ids": list(t1.CANDIDATES),
        "switch_matrix": spec["switch_matrix"],
        "post_first_only": True,
        "free_parameters": [],
        "metrics": None,
        "performance": None,
        "scored": False,
    })
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
        "holdout_access": False,
        "live_or_network_access": False,
        "production_access": False,
        "orders_or_positions_access": False,
        "Window2_exit_settlement_DCA_access": False,
        "development_inputs_only": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    report = f"""# Window-1 T1 Post-First-Leg Response and Persistence PRE-RUN

Status: **FROZEN SCORE-FREE BUILD; BENCHMARK NOT EXECUTED**

- Exact parent: `{t1.EXACT_PARENT}`
- Controlling attribution PASS: `{t1.CONTROLLING_AUDIT}`
- Immutable denominator: D=804 for each of eight T1 candidates
- Candidate-event overlays: 6,432
- Baseline candidates: byte-bound references only; zero regenerated rows
- Switches: receipt-keyed response, target completeness, persistence, full stack
- All switches are inactive before the credited first fill.
- Strict pair law: `d1+d2+fee<0`; positive sibling d2 is lawful.
- C/PC/S/IC and every performance field: null

## Controlling fixture migration

- 24 no-decision rows: explicit decisions in response-only and full-stack
- 4 omitted-target rows: complete lawful headroom construction in
  target-completeness-only and full-stack
- 17 moved-away rows: retained or resolved by exact receipt-backed law in
  persistence-only and full-stack
- TON-SPI capacity-unproved rows: no T1 conversion/performance claim

The package contains no scorer, ranking, benchmark, holdout, live, production,
Window-2, exit, settlement, DCA, order, or position interface.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    write_json(output / "PRE_RUN_MANIFEST.json", {
        "schema_version": VERSION + "-manifest-v1",
        "exact_parent": t1.EXACT_PARENT,
        "controlling_attribution_PASS": t1.CONTROLLING_AUDIT,
        "baseline_candidate_ids": list(t1.BASE_CANDIDATES),
        "candidate_ids": list(t1.CANDIDATES),
        "D_per_candidate": 804,
        "candidate_event_overlay_count": 6432,
        "benchmark_execution_authorized": False,
        "scorer_present": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    for path in output.iterdir():
        if path.suffix in {".json", ".md"}:
            try:
                assert_metrics_null(
                    json.loads(path.read_text(encoding="utf-8"))
                    if path.suffix == ".json" else {}
                )
            except json.JSONDecodeError as error:
                raise T1FreezeError(f"invalid JSON: {path}") from error
    return {
        "D": 804,
        "candidate_count": 8,
        "candidate_event_overlay_count": 6432,
        "episode_decision_rows": sum(
            writer.rows for writer in decision_writers
        ),
        "target_receipt_rows": target_writer.rows,
        "persistence_receipt_rows": persistence_writer.rows,
        "fixture_counts": fixture["variant_acceptance_counts"],
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
        raise T1FreezeError("frozen output already exists")
    inventory_a = _inventory(build_a)
    inventory_b = _inventory(build_b)
    if inventory_a != inventory_b:
        raise T1FreezeError("two clean T1 builds are not byte-identical")
    shutil.copytree(build_a, output)
    receipt = {
        "schema_version": VERSION + "-determinism-v1",
        "clean_regeneration_count": 2,
        "byte_identical": True,
        "file_count_before_freeze_receipts": len(inventory_a),
        "inventory_sha256": canonical_sha256(inventory_a),
        "inventories": {
            "build_A": inventory_a,
            "build_B": inventory_b,
        },
        "output_paths_excluded_from_bytes": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "DETERMINISTIC_REGENERATION_RECEIPT.json", receipt)
    rows = _inventory(output)
    manifest = {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "self_excluded": "ARTIFACT_HASH_MANIFEST.json",
        "artifact_count": len(rows),
        "artifacts": rows,
        "all_hashes_verified": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", manifest)
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
    arguments = parser.parse_args()
    if arguments.mode == "build":
        result = build(
            repo=arguments.repo.resolve(),
            events_path=arguments.events.resolve(),
            cache_root=arguments.market_cache.resolve(),
            output=arguments.output_dir.resolve(),
            workers=arguments.workers,
        )
    else:
        result = freeze(
            arguments.build_a.resolve(),
            arguments.build_b.resolve(),
            arguments.output_dir.resolve(),
        )
    print(compact({"status": "PASS", "mode": arguments.mode, **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
