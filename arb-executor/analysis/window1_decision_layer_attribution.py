#!/usr/bin/env python3
"""Freeze a score-free decision-layer attribution over passed W1 census V2.

This module never constructs an opportunity and never imports or invokes a
scorer.  It consumes the independently passed V2 event/episode/orientation
rows as immutable facts.  Raw-cache reads are limited to resolving the exact
already-frozen no-fill witness episode IDs to their public evidence receipts.
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import math
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-decision-layer-attribution-v1"
PARENT = "e60f6af4f6db5bab5b8a30704a0cb1fc98c774a7"
AUDIT = "26dd6e5e19a7890f02b538cc8b14a900f36e5b2f"
AUDIT_REPORT = (
    ".claude/audit_20260727_window1_async_census_v2_prerun/"
    "AUDIT_REPORT.md"
)
AUDIT_RECEIPT = (
    ".claude/audit_20260727_window1_async_census_v2_prerun/"
    "INDEPENDENT_REPRODUCTION_RECEIPT.json"
)
V2_REL = ".claude/window1_asynchronous_opportunity_policy_census_v2_20260726"
STRICT_REL = ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
MECHANISM_REL = (
    ".claude/window1_range_attack_prerun_20260725/"
    "MECHANISM_RECOVERY_TABLE.json"
)
CACHE_REL = "../OMI-Window1-private/fit-local/guarded-cache-v3"
PACKAGE_REL = ".claude/window1_decision_layer_attribution_prerun_20260727"
SOURCE_REL = (
    "arb-executor/analysis/window1_decision_layer_attribution.py"
)
TEST_REL = (
    "arb-executor/tests/test_window1_decision_layer_attribution.py"
)
SPEC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_DECISION_LAYER_ATTRIBUTION_SPEC.json"
)
CANDIDATES = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
DEVELOPMENT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(12, 21)
)
SEALED_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)
V2_EPISODE_FILES = tuple(
    f"{V2_REL}/QUALIFYING_EPISODE_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
STREAM_FILES = tuple(
    f"{STRICT_REL}/UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
ACTION_FILE = f"{STRICT_REL}/ACTION_AUTHORITY_RECEIPTS.jsonl.gz"
HEADROOM_FILE = f"{STRICT_REL}/COMBINED_HEADROOM_RECEIPTS.jsonl.gz"


class AttributionError(RuntimeError):
    """An immutable-input, attribution, or conservation invariant failed."""


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


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False
    )
    if process.returncode:
        raise AttributionError(
            f"git {' '.join(args)} failed: {process.stderr.strip()}"
        )
    return process.stdout.strip()


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(raw)}\0".encode("ascii") + raw
    ).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )


def iter_gzip_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


class GzipJsonlWriter:
    def __init__(self, path: Path) -> None:
        self.raw = path.open("wb")
        self.gz = gzip.GzipFile(
            filename="", fileobj=self.raw, mode="wb", mtime=0
        )
        self.rows = 0

    def write(self, row: Mapping[str, Any]) -> None:
        self.gz.write((compact(row) + "\n").encode("utf-8"))
        self.rows += 1

    def close(self) -> None:
        self.gz.close()
        self.raw.close()


def row_receipt(source: str, ordinal: int, row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_path": source,
        "source_row_ordinal": ordinal,
        "row_sha256": canonical_sha256(row),
    }


def exact_cent(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise AttributionError(f"{field}: bool is not a cent")
    if isinstance(value, int):
        result = value
    elif (
        isinstance(value, float)
        and math.isfinite(value)
        and value.is_integer()
    ):
        result = int(value)
    else:
        raise AttributionError(f"{field}: not an exact integer cent")
    if not 1 <= result <= 99:
        raise AttributionError(f"{field}: outside 1..99")
    return result


def positive_size(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise AttributionError(f"{field}: bool is not size")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise AttributionError(f"{field}: not positive finite size")
    return result


def strict_combined(d1: int | float, d2: int | float, fee: int = 0) -> bool:
    return d1 + d2 + fee < 0


def sign_band(value: int | float) -> str:
    if value < 0:
        return "NEGATIVE"
    if value > 0:
        return "POSITIVE"
    return "ZERO"


def elapsed_band(seconds: float) -> str:
    if seconds < 60:
        return "LT_1M"
    if seconds < 300:
        return "1M_TO_LT_5M"
    if seconds < 900:
        return "5M_TO_LT_15M"
    if seconds < 3600:
        return "15M_TO_LT_1H"
    if seconds < 14400:
        return "1H_TO_LT_4H"
    return "GE_4H"


def volume_band(value: float) -> str:
    if value == 0:
        return "ZERO"
    if value < 5:
        return "POSITIVE_LT_5"
    return "GE_5"


def cadence_band(value: Any) -> str:
    if value is None:
        return "UNAVAILABLE_OR_SINGLE_PRINT"
    seconds = float(value)
    if seconds <= 10:
        return "LE_10S"
    if seconds <= 60:
        return "GT_10S_TO_60S"
    return "GT_60S"


def spread_band(value: int) -> str:
    if value <= 1:
        return "ONE_CENT"
    if value <= 3:
        return "TWO_TO_THREE_CENTS"
    return "FOUR_PLUS_CENTS"


def depth_band(value: float) -> str:
    if value == 0:
        return "ZERO"
    if value < 5:
        return "POSITIVE_LT_5"
    if value < 100:
        return "FIVE_TO_LT_100"
    return "GE_100"


def load_v2(repo: Path) -> dict[str, Any]:
    root = repo / V2_REL
    artifact_manifest = json.loads(
        (root / "ARTIFACT_HASH_MANIFEST.json").read_text(encoding="utf-8")
    )
    for receipt in artifact_manifest["artifacts"]:
        path = root / receipt["path"]
        if (
            path.stat().st_size != receipt["bytes"]
            or sha256_file(path) != receipt["sha256"]
        ):
            raise AttributionError(
                f"passed V2 artifact hash changed: {receipt['path']}"
            )
    deterministic = json.loads(
        (root / "DETERMINISTIC_REGENERATION_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        deterministic["clean_build_count"] != 2
        or not deterministic["byte_identical"]
    ):
        raise AttributionError("passed V2 determinism receipt changed")
    for receipt in deterministic["inventory"]:
        path = root / receipt["path"]
        if (
            path.stat().st_size != receipt["bytes"]
            or sha256_file(path) != receipt["sha256"]
        ):
            raise AttributionError(
                f"passed V2 deterministic inventory changed: "
                f"{receipt['path']}"
            )
    source_manifest = json.loads(
        (root / "SOURCE_HASH_MANIFEST.json").read_text(encoding="utf-8")
    )
    for receipt in source_manifest["sources"]:
        path = repo / receipt["path"]
        raw = path.read_bytes()
        if (
            len(raw) != receipt["bytes"]
            or hashlib.sha256(raw).hexdigest() != receipt["sha256"]
            or git_blob_oid(raw) != receipt["git_blob_oid"]
        ):
            raise AttributionError(
                f"passed V2 source hash changed: {receipt['path']}"
            )
    events = list(iter_gzip_jsonl(root / "CORRECTED_EVENT_LEVEL_CENSUS.jsonl.gz"))
    episodes: list[dict[str, Any]] = []
    for relative in V2_EPISODE_FILES:
        episodes.extend(iter_gzip_jsonl(repo / relative))
    orientations = list(iter_gzip_jsonl(
        root / "COUNTERFACTUAL_ORIENTATION_DIAGNOSTICS.jsonl.gz"
    ))
    first = list(iter_gzip_jsonl(
        root / "AUTHORITATIVE_FIRST_LEG_REFERENCE_RECEIPT.jsonl.gz"
    ))
    exposures = list(iter_gzip_jsonl(
        root / "BOUNDED_POLICY_EXPOSURE_ATTRIBUTION.jsonl.gz"
    ))
    summary = json.loads((root / "RAW_DIAGNOSTIC_CENSUS.json").read_text(
        encoding="utf-8"
    ))
    boundaries = json.loads((root / "BOUNDARY_SOURCE_RECEIPT.json").read_text(
        encoding="utf-8"
    ))
    recurring = json.loads((root / "RECURRING_X_CLASS_RECEIPT.json").read_text(
        encoding="utf-8"
    ))
    if len(events) != 1608 or len(episodes) != 6501:
        raise AttributionError("passed V2 row counts changed")
    if len(orientations) != 1352 or len(first) != 473:
        raise AttributionError("passed V2 orientation/first-leg counts changed")
    if len(exposures) != 10733:
        raise AttributionError("passed V2 exposure count changed")
    if summary["D_per_candidate"] != 804:
        raise AttributionError("D changed")
    for row in events:
        if row["event_date"] not in DEVELOPMENT_DATES:
            raise AttributionError("non-development event in passed V2")
        if row["event_date"] in SEALED_DATES:
            raise AttributionError("sealed date in passed V2")
        if not row["D_member"]:
            raise AttributionError("D membership changed")
        if row.get("metrics") is not None or row.get("performance") is not None:
            raise AttributionError("passed V2 contains populated metrics")
    for row in episodes:
        if row.get("metrics") is not None or row.get("performance") is not None:
            raise AttributionError("passed V2 episode contains metrics")
    expected_naked = {
        CANDIDATES[0]: (237, 22, 215, 3226, 16, 6, 27, 16),
        CANDIDATES[1]: (240, 25, 215, 3275, 19, 6, 34, 16),
    }
    for candidate, expected in expected_naked.items():
        row = summary["final_naked"][candidate]
        actual = (
            row["total"], row["recovered"], row["residual_no_lawful"],
            row["qualifying_episodes"],
            row["evidence_split_first_recovery"]["print"],
            row["evidence_split_first_recovery"]["strict_ask"],
            row["recurring_x_levels_globalfirst_rejected"],
            row["x_levels_lawful_recurrence_but_no_ledger_observation"],
        )
        if actual != expected:
            raise AttributionError(f"passed V2 naked fixture changed: {candidate}")
    expected_nofill = {
        CANDIDATES[0]: (336, 65, 52, 13, 271),
        CANDIDATES[1]: (340, 68, 54, 14, 272),
    }
    for candidate, expected in expected_nofill.items():
        row = summary["final_nofill"][candidate]
        actual = (
            row["total"], row["either"], row["both"],
            row["one"], row["neither"],
        )
        if actual != expected:
            raise AttributionError(f"passed V2 no-fill fixture changed: {candidate}")
    if sum(1 for row in episodes if row["d2_cents"] > 0) != 6310:
        raise AttributionError("positive-d2 episode fixture changed")
    return {
        "events": events,
        "episodes": episodes,
        "orientations": orientations,
        "first": first,
        "exposures": exposures,
        "summary": summary,
        "boundaries": boundaries["events"],
        "recurring": recurring,
    }


def load_policy_rows(
    repo: Path, keys: set[tuple[str, str]]
) -> dict[str, Any]:
    strict_root = repo / STRICT_REL
    strict_manifest = json.loads(
        (strict_root / "ARTIFACT_HASH_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    required_names = {
        *(Path(relative).name for relative in STREAM_FILES),
        Path(ACTION_FILE).name,
        Path(HEADROOM_FILE).name,
    }
    manifest_index = {
        row["path"]: row for row in strict_manifest["artifacts"]
    }
    for name in required_names:
        receipt = manifest_index.get(name)
        if receipt is None:
            raise AttributionError(f"strict package receipt missing: {name}")
        path = strict_root / name
        if (
            path.stat().st_size != receipt["bytes"]
            or sha256_file(path) != receipt["sha256"]
        ):
            raise AttributionError(f"strict package artifact changed: {name}")
    streams: dict[tuple[str, str], dict[str, Any]] = {}
    for relative in STREAM_FILES:
        for wrapper in iter_gzip_jsonl(repo / relative):
            key = (str(wrapper["candidate_id"]), str(wrapper["event_id"]))
            if key in keys:
                streams[key] = wrapper["stream"]
    actions: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for ordinal, row in enumerate(iter_gzip_jsonl(repo / ACTION_FILE), 1):
        key = (str(row["candidate_id"]), str(row["event_id"]))
        if key in keys:
            enriched = dict(row)
            enriched["_receipt"] = row_receipt(ACTION_FILE, ordinal, row)
            actions[key].append(enriched)
    headroom: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for ordinal, row in enumerate(iter_gzip_jsonl(repo / HEADROOM_FILE), 1):
        key = (str(row["candidate_id"]), str(row["event_id"]))
        if key in keys:
            enriched = dict(row)
            enriched["_receipt"] = row_receipt(HEADROOM_FILE, ordinal, row)
            headroom[key].append(enriched)
    if set(streams) != keys:
        raise AttributionError("missing frozen candidate stream")
    return {
        "streams": streams,
        "actions": actions,
        "headroom": headroom,
    }


def event_recovered(row: Mapping[str, Any]) -> bool:
    return int(row.get("lawful_qualifying_episode_count") or 0) > 0


def active_intervals(
    stream: Mapping[str, Any], leg_id: str, timestamp: float
) -> list[dict[str, Any]]:
    return [
        row for row in stream["order_intervals_by_leg"].get(leg_id, [])
        if float(row["opened_ts"]) <= timestamp
        <= float(row.get("closed_ts") or float("inf"))
    ]


def evidence_context(
    stream: Mapping[str, Any], leg_id: str
) -> dict[str, Any]:
    row = next(
        item for item in stream["evidence_census_by_leg"]
        if str(item["leg_id"]) == leg_id
    )
    return {
        key: row.get(key) for key in (
            "leg_id", "discovery_page_key", "discovery_price",
            "discovery_status", "macro_target_raw",
            "macro_target_source", "macro_target_status",
            "no_calls", "headroom_trigger_count",
            "target_change_count", "queue_surrender_count",
        )
    }


def attribute_never_exposed(
    event: Mapping[str, Any],
    earliest: Mapping[str, Any],
    stream: Mapping[str, Any],
    headroom_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    sibling = str(event["sibling_leg_id"])
    timestamp = float(earliest["timestamp"])
    x = int(earliest["price_x_cents"])
    context = evidence_context(stream, sibling)
    active = active_intervals(stream, sibling, timestamp)
    matching = [
        row for row in headroom_rows
        if row.get("leg_id") == sibling
        and row.get("trigger_receipt") == earliest["evidence_receipt"]
        and float(row["ts"]) == timestamp
    ]
    armed = [
        row for row in headroom_rows
        if row.get("leg_id") == sibling
        and row.get("action") == "headroom_armed"
        and float(row["ts"]) == float(event["credited_first_leg"]["timestamp"])
    ]
    explicit_no_calls = list(context.get("no_calls") or [])
    discovery_unavailable = (
        context.get("discovery_status") in {
            "UNAVAILABLE", "NO_CALL", "NO_CALL_UNAVAILABLE"
        }
        or any(
            "DISCOVERY" in compact(item).upper()
            and ("NO_CALL" in compact(item).upper()
                 or "UNAVAILABLE" in compact(item).upper())
            for item in explicit_no_calls
        )
    )
    target_receipts = [
        {
            "receipt": row["_receipt"],
            "complete_raw_target_cents": row.get("complete_raw_target_cents"),
            "final_expressed_price_cents": row.get(
                "final_expressed_price_cents"
            ),
            "action_taken": row.get("action_taken"),
            "reason": row.get("reason"),
        }
        for row in matching
    ]
    if discovery_unavailable:
        layer = "discovery_recognition_unavailable_or_no_call"
        proof = "explicit frozen discovery NO_CALL/unavailable state"
    elif matching and all(
        int(row["complete_raw_target_cents"]) != x
        for row in matching
    ):
        layer = "target_selection_never_included_lawful_X"
        proof = (
            "same-receipt sibling decision selected a different complete "
            "raw target"
        )
    elif matching and any(
        int(row["complete_raw_target_cents"]) == x for row in matching
    ) and not active:
        layer = "target_included_X_but_no_initial_exposure_created"
        proof = "same-receipt target X exists but no active interval exists"
    elif armed and not matching:
        layer = "first_fill_sibling_response_failed_to_create_exposure"
        proof = (
            "headroom arm is receipted, but no sibling decision is keyed to "
            "the earliest lawful opportunity receipt"
        )
    else:
        layer = "policy_evidence_insufficient_to_distinguish"
        proof = "frozen receipts do not distinguish target from response layer"
    missing = []
    if layer == "first_fill_sibling_response_failed_to_create_exposure":
        missing.append(
            "explicit_reason_no_episode_keyed_sibling_decision_was_emitted"
        )
    elif layer == "policy_evidence_insufficient_to_distinguish":
        if not armed:
            missing.append("first_fill_headroom_arm_receipt")
        if not matching:
            missing.append("same_episode_sibling_decision_receipt")
        if context.get("macro_target_status") is None:
            missing.append("macro_target_state")
    return {
        "attributed_layer": layer,
        "proof": proof,
        "missing_evidence": missing,
        "policy_context": context,
        "active_intervals_at_opportunity": [
            {
                "order_interval_id": row["order_interval_id"],
                "price_cents": row["limit_price_cents"],
                "authority": row["authority"],
                "open_reason": row["open_reason"],
                "opened_ts": row["opened_ts"],
                "closed_ts": row.get("closed_ts"),
            }
            for row in active
        ],
        "matching_sibling_decision_receipts": target_receipts,
        "headroom_arm_receipts": [row["_receipt"] for row in armed],
    }


def moved_layer(authority: str | None, replacement: bool) -> str:
    if authority == "MAKER_SAFETY":
        return "maker_safety_reprice"
    if authority in {"LIVEAIM_SOURCE_MAPPING", "LIVEAIM_MICRO_CONFIRMATION"}:
        return "LIVE_AIM_reprice"
    if authority == "CAUSAL_PAIR_HEADROOM":
        return "headroom_reprice"
    if authority == "POLICY_HORIZON":
        return "corridor_window_termination"
    if authority == "ATLAS_DISCOVERY_MACRO":
        return "target_supersession"
    if authority is not None and not replacement:
        return "cancel_without_replacement"
    if authority is not None:
        return "other_named_existing_action"
    return "unresolved"


def attribute_moved(
    event: Mapping[str, Any],
    event_episodes: list[Mapping[str, Any]],
    stream: Mapping[str, Any],
    action_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    ordered = sorted(
        event_episodes,
        key=lambda row: (
            float(row["timestamp"]), str(row["evidence_type"]),
            str(row["evidence_receipt"]),
        ),
    )
    first_opportunity = ordered[0]
    moved_episode = next(
        row for row in ordered if row["policy_moved_away_before_episode"]
    )
    interval_ids = set(moved_episode["prior_order_interval_ids_at_x"])
    sibling = str(event["sibling_leg_id"])
    intervals = stream["order_intervals_by_leg"].get(sibling, [])
    prior = [row for row in intervals if row["order_interval_id"] in interval_ids]
    if not prior:
        raise AttributionError(
            f"moved attribution missing interval: {event['event_id']}"
        )
    interval = max(
        prior, key=lambda row: (
            float(row["closed_ts"]), str(row["order_interval_id"])
        )
    )
    close_ts = float(interval["closed_ts"])
    actions = [
        row for row in action_rows
        if row.get("leg_id") == sibling
        and float(row["timestamp"]) == close_ts
    ]
    replacements = [
        row for row in intervals
        if row["order_interval_id"] != interval["order_interval_id"]
        and float(row["opened_ts"]) == close_ts
    ]
    authority = next(
        (
            row["primary_authority"] for row in actions
            if row["action"] == "reprice"
        ),
        next(
            (
                row["primary_authority"] for row in actions
                if row["action"] == "cancel"
            ),
            None,
        ),
    )
    replacement = replacements[0] if replacements else None
    replacement_inside = None
    if replacement is not None:
        replacement_d2 = (
            int(replacement["limit_price_cents"])
            - int(moved_episode["contemporaneous_bid_cents"])
        )
        replacement_inside = strict_combined(
            int(event["credited_first_leg"]["d1_cents"]),
            replacement_d2,
            0,
        )
    return {
        "attributed_layer": moved_layer(authority, bool(replacements)),
        "first_lawful_opportunity": {
            key: first_opportunity[key] for key in (
                "episode_id", "timestamp", "evidence_type",
                "evidence_receipt", "price_x_cents",
            )
        },
        "first_moved_away_opportunity": {
            key: moved_episode[key] for key in (
                "episode_id", "timestamp", "evidence_type",
                "evidence_receipt", "price_x_cents",
                "contemporaneous_bid_cents", "d2_cents",
                "combined_delta_cents",
            )
        },
        "original_exposure": {
            "order_interval_id": interval["order_interval_id"],
            "X_cents": interval["limit_price_cents"],
            "opened_ts": interval["opened_ts"],
            "closed_ts": interval["closed_ts"],
            "authority": interval["authority"],
            "open_reason": interval["open_reason"],
            "close_reason": interval.get("close_reason"),
            "queue_diagnostic": interval.get("queue_diagnostic"),
        },
        "move_action_receipts": [
            {
                "action": row["action"],
                "primary_authority": row["primary_authority"],
                "reason": row["reason"],
                "price_cents": row.get("price_cents"),
                "prior_price_cents": row.get("prior_price_cents"),
                "receipt": row["_receipt"],
            }
            for row in actions
        ],
        "replacement": (
            {
                "order_interval_id": replacement["order_interval_id"],
                "X_cents": replacement["limit_price_cents"],
                "authority": replacement["authority"],
                "open_reason": replacement["open_reason"],
                "inside_contemporaneous_headroom":
                    replacement_inside,
            }
            if replacement else None
        ),
        "elapsed_move_to_moved_opportunity_seconds":
            float(moved_episode["timestamp"]) - close_ts,
        "old_order_would_have_been_at_lawful_opportunity": (
            int(interval["limit_price_cents"])
            == int(moved_episode["price_x_cents"])
        ),
        "queue_surrendered": bool(replacements),
        "counterfactual_only": True,
        "certain_fill_claim": False,
    }


def build_crosswalk(
    recovered: list[Mapping[str, Any]]
) -> dict[str, Any]:
    by_candidate = {
        candidate: {
            str(row["event_id"]): row
            for row in recovered if row["candidate_id"] == candidate
        }
        for candidate in CANDIDATES
    }
    left = set(by_candidate[CANDIDATES[0]])
    right = set(by_candidate[CANDIDATES[1]])
    shared_rows = []
    for event_id in sorted(left & right):
        a = by_candidate[CANDIDATES[0]][event_id]
        b = by_candidate[CANDIDATES[1]][event_id]
        same_first = (
            a["credited_first_leg"]["leg_id"],
            a["credited_first_leg"]["price_x_cents"],
            a["credited_first_leg"]["timestamp"],
            a["credited_first_leg"]["evidence_receipt"],
        ) == (
            b["credited_first_leg"]["leg_id"],
            b["credited_first_leg"]["price_x_cents"],
            b["credited_first_leg"]["timestamp"],
            b["credited_first_leg"]["evidence_receipt"],
        )
        same_earliest = a["earliest_lawful_recovery"] == b[
            "earliest_lawful_recovery"
        ]
        shared_rows.append({
            "event_id": event_id,
            "same_credited_first_leg": same_first,
            "same_earliest_lawful_sibling_episode": same_earliest,
            "macro_hold_terminal": a["primary_classification"],
            "macro_micro_terminal": b["primary_classification"],
            "terminal_attribution_agrees": (
                a["primary_classification"] == b["primary_classification"]
            ),
            "agreement_or_difference_reason": (
                "same frozen policy-at-opportunity state"
                if a["primary_classification"] == b["primary_classification"]
                else "candidate-specific frozen exposure/move state differs"
            ),
        })
    return {
        "candidate_rows_are_not_distinct_games": True,
        "candidate_row_counts": {
            candidate: len(by_candidate[candidate]) for candidate in CANDIDATES
        },
        "distinct_game_union_count": len(left | right),
        "shared_event_count": len(left & right),
        "macro_hold_only_count": len(left - right),
        "macro_micro_only_count": len(right - left),
        "shared_events": shared_rows,
        "macro_hold_only_events": sorted(left - right),
        "macro_micro_only_events": sorted(right - left),
        "metrics": None,
        "performance": None,
    }


def _levels(rows: Any) -> list[list[float | int]]:
    output: list[list[float | int]] = []
    for row in rows or []:
        try:
            price = exact_cent(row[0], "book.price")
            size = positive_size(row[1], "book.size")
        except (AttributionError, TypeError, ValueError, IndexError):
            continue
        output.append([price, size])
    return output[:5]


def raw_book_rows(
    leg: Mapping[str, Any], left: float, right: float
) -> list[dict[str, Any]]:
    ticker = str(leg["ticker"])
    rows = []
    for ordinal, snapshot in enumerate(leg.get("snapshots") or []):
        timestamp = float(snapshot["ts"])
        if not left <= timestamp <= right:
            continue
        bids = _levels(snapshot.get("bids"))
        asks = _levels(snapshot.get("asks"))
        if not bids or not asks or int(bids[0][0]) >= int(asks[0][0]):
            continue
        bid, ask = int(bids[0][0]), int(asks[0][0])
        rows.append({
            "timestamp": timestamp,
            "source_ordinal": ordinal,
            "receipt": (
                f"{ticker}|raw-book{ordinal}|"
                f"{timestamp:.6f}|{bid}x{ask}"
            ),
            "bid_cents": bid,
            "ask_cents": ask,
            "top5_bids": bids,
            "top5_asks": asks,
            "spread_cents": ask - bid,
            "last_trade_cents": snapshot.get("last_trade"),
        })
    rows.sort(key=lambda row: (row["timestamp"], row["source_ordinal"]))
    return rows


def raw_print_rows(
    leg: Mapping[str, Any], left: float, right: float
) -> list[dict[str, Any]]:
    ticker = str(leg["ticker"])
    rows = []
    seen: set[str] = set()
    for ordinal, trade in enumerate(leg.get("prints") or []):
        try:
            timestamp = float(trade["ts"])
            price = exact_cent(trade["price"], "print.price")
            size = positive_size(trade["size"], "print.size")
        except (AttributionError, TypeError, ValueError, KeyError):
            continue
        if not left <= timestamp <= right:
            continue
        receipt = str(
            trade.get("trade_id")
            or (
                f"{ticker}|raw-print{ordinal}|"
                f"{canonical_sha256(trade)}"
            )
        )
        if receipt in seen:
            continue
        seen.add(receipt)
        rows.append({
            "timestamp": timestamp,
            "source_ordinal": ordinal,
            "receipt": receipt,
            "price_cents": price,
            "size": size,
        })
    rows.sort(key=lambda row: (
        row["timestamp"], row["source_ordinal"], row["receipt"]
    ))
    return rows


def latest_book(
    books: list[Mapping[str, Any]], timestamp: float
) -> Mapping[str, Any] | None:
    keys = [(float(row["timestamp"]), int(row["source_ordinal"])) for row in books]
    index = bisect.bisect_right(keys, (float(timestamp), math.inf)) - 1
    return books[index] if index >= 0 else None


def raw_episode_id(
    evidence_type: str,
    timestamp: float,
    price: int,
    evidence_receipt: str,
    book_receipt: str,
) -> str:
    return canonical_sha256({
        "type": evidence_type,
        "timestamp": timestamp,
        "price": price,
        "receipt": evidence_receipt,
        "book": book_receipt,
    })


def resolve_fixed_witness(
    *,
    event: Mapping[str, Any],
    leg_id: str,
    expected_episode_id: str,
    timestamp: float,
    price_x: int,
    bid: int,
    boundary: Mapping[str, Any],
) -> dict[str, Any]:
    """Resolve one frozen witness ID; never enumerate or select opportunity."""
    left = float(boundary["policy_left_ts"])
    right = float(boundary["guarded_cutoff_ts"])
    leg = next(row for row in event["legs"] if str(row["leg"]) == leg_id)
    books = raw_book_rows(leg, left, right)
    prints = raw_print_rows(leg, left, right)
    candidates: list[dict[str, Any]] = []
    for book in books:
        if (
            float(book["timestamp"]) == timestamp
            and int(book["ask_cents"]) < 99
            and int(book["ask_cents"]) + 1 == price_x
            and int(book["bid_cents"]) == bid
        ):
            candidates.append({
                "evidence_type": "STRICT_ASK_CERTAIN_FILL",
                "evidence_receipt": book["receipt"],
                "evidence_size": None,
                "book": book,
            })
    for trade in prints:
        if (
            float(trade["timestamp"]) == timestamp
            and int(trade["price_cents"]) == price_x
        ):
            book = latest_book(books, timestamp)
            if book is not None and int(book["bid_cents"]) == bid:
                candidates.append({
                    "evidence_type": "PRICE_REACHED",
                    "evidence_receipt": trade["receipt"],
                    "evidence_size": trade["size"],
                    "book": book,
                })
    matches = [
        row for row in candidates
        if raw_episode_id(
            row["evidence_type"], timestamp, price_x,
            row["evidence_receipt"], row["book"]["receipt"],
        ) == expected_episode_id
    ]
    if len(matches) != 1:
        raise AttributionError(
            f"fixed witness receipt resolution failed: "
            f"{event['event_id']} {leg_id} {expected_episode_id}"
        )
    match = matches[0]
    book = match["book"]
    past = [
        row for row in prints
        if timestamp - 1800 <= float(row["timestamp"]) <= timestamp
    ]
    gaps = [
        float(b["timestamp"]) - float(a["timestamp"])
        for a, b in zip(past, past[1:])
        if float(b["timestamp"]) > float(a["timestamp"])
    ]
    capacity = sum(
        float(row["size"]) for row in prints
        if timestamp <= float(row["timestamp"]) <= right
        and int(row["price_cents"]) <= price_x
    )
    residence = 0.0
    after = [row for row in books if timestamp <= float(row["timestamp"]) <= right]
    for current, following in zip(after, after[1:]):
        if int(current["ask_cents"]) <= price_x:
            residence += max(
                0.0, float(following["timestamp"]) - float(current["timestamp"])
            )
    return {
        "episode_id": expected_episode_id,
        "timestamp": timestamp,
        "price_x_cents": price_x,
        "evidence_type": match["evidence_type"],
        "evidence_receipt": match["evidence_receipt"],
        "evidence_size": match["evidence_size"],
        "book_receipt": book["receipt"],
        "book_timestamp": book["timestamp"],
        "book_source_ordinal": book["source_ordinal"],
        "bid_cents": book["bid_cents"],
        "ask_cents": book["ask_cents"],
        "spread_cents": book["spread_cents"],
        "top5_bids": book["top5_bids"],
        "top5_asks": book["top5_asks"],
        "executed_volume_at_or_better_after_episode": capacity,
        "five_contract_capacity_proven": capacity >= 5,
        "rolling_print_count_30m": len(past),
        "rolling_executed_volume_30m": sum(
            float(row["size"]) for row in past
        ),
        "interprint_cadence_seconds_30m": (
            sum(gaps) / len(gaps) if gaps else None
        ),
        "price_residency_seconds": residence,
        "witness_tuple_was_frozen_before_source_lookup": True,
        "opportunity_enumeration_performed": False,
    }


def resolve_nofill_witnesses(
    repo: Path,
    path_rows: list[Mapping[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[tuple[str, str, str], dict[str, Any]], list[dict[str, Any]]]:
    needed: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in path_rows:
        witness = row["witness"]
        needed[row["event_id"]].add((
            row["first_leg_id"], witness["first_episode_id"]
        ))
        needed[row["event_id"]].add((
            row["sibling_leg_id"], witness["sibling_episode_id"]
        ))
    cache_root = (repo / CACHE_REL).resolve()
    resolved: dict[tuple[str, str, str], dict[str, Any]] = {}
    source_rows = []
    rows_by_key = {
        (
            row["event_id"], row["first_leg_id"],
            row["witness"]["first_episode_id"],
        ): (
            row["witness"]["first_timestamp"],
            row["witness"]["first_price_x_cents"],
            row["witness"]["first_bid_cents"],
        )
        for row in path_rows
    }
    rows_by_key.update({
        (
            row["event_id"], row["sibling_leg_id"],
            row["witness"]["sibling_episode_id"],
        ): (
            row["witness"]["sibling_timestamp"],
            row["witness"]["sibling_price_x_cents"],
            row["witness"]["sibling_bid_cents"],
        )
        for row in path_rows
    })
    for event_id in sorted(needed):
        path = cache_root / f"{event_id}.json.gz"
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            event = json.load(handle)
        if str(event.get("date") or "") in SEALED_DATES:
            raise AttributionError("sealed event in witness lookup")
        source_rows.append({
            "event_id": event_id,
            "path": f"{CACHE_REL}/{event_id}.json.gz",
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "role": "fixed_witness_receipt_resolution_only",
        })
        for leg_id, episode_id in sorted(needed[event_id]):
            timestamp, price, bid = rows_by_key[
                (event_id, leg_id, episode_id)
            ]
            resolved[(event_id, leg_id, episode_id)] = resolve_fixed_witness(
                event=event,
                leg_id=leg_id,
                expected_episode_id=episode_id,
                timestamp=float(timestamp),
                price_x=int(price),
                bid=int(bid),
                boundary=boundaries[event_id],
            )
    return resolved, source_rows


def add_bucket(
    buckets: dict[str, dict[str, list[str]]],
    dimension: str,
    value: Any,
    row_id: str,
) -> None:
    buckets.setdefault(dimension, {}).setdefault(str(value), []).append(row_id)


def feature_breakdown(
    episodes: list[Mapping[str, Any]],
    event_index: Mapping[tuple[str, str], Mapping[str, Any]],
    streams: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[str]]] = {}
    row_index = []
    multiplicity = Counter(
        (row["candidate_id"], row["event_id"]) for row in episodes
    )
    for row in sorted(episodes, key=lambda item: (
        item["candidate_id"], item["event_id"],
        float(item["timestamp"]), item["episode_id"],
    )):
        candidate = str(row["candidate_id"])
        event_id = str(row["event_id"])
        rid = str(row["episode_id"])
        event = event_index[(candidate, event_id)]
        stream = streams[(candidate, event_id)]
        context = evidence_context(stream, str(row["sibling_leg_id"]))
        elapsed = float(row["timestamp"]) - float(row["first_fill_timestamp"])
        top5_depth = sum(float(item[1]) for item in row["top5_bids"])
        fields = {
            "candidate": candidate,
            "event": f"{candidate}|{event_id}",
            "category": f"{candidate}|{event['category']}",
            "date": f"{candidate}|{event['event_date']}",
            "first_leg_orientation": (
                f"{candidate}|{row['first_leg_id']}__then__"
                f"{row['sibling_leg_id']}"
            ),
            "d1_sign": f"{candidate}|{sign_band(row['d1_cents'])}",
            "d1_exact": f"{candidate}|{row['d1_cents']}",
            "b2_max_sign": f"{candidate}|{sign_band(row['b2_max_cents'])}",
            "b2_max_exact": f"{candidate}|{row['b2_max_cents']}",
            "d2_sign": f"{candidate}|{sign_band(row['d2_cents'])}",
            "d2_exact": f"{candidate}|{row['d2_cents']}",
            "combined_delta_exact":
                f"{candidate}|{row['combined_delta_cents']}",
            "elapsed_since_first_fill":
                f"{candidate}|{elapsed_band(elapsed)}",
            "evidence_type": f"{candidate}|{row['evidence_type']}",
            "episode_multiplicity": (
                f"{candidate}|{multiplicity[(candidate, event_id)]}"
            ),
            "executed_capacity": (
                f"{candidate}|"
                f"{volume_band(float(row['executed_volume_at_or_better_after_episode']))}"
            ),
            "rolling_volume_30m": (
                f"{candidate}|"
                f"{volume_band(float(row['rolling_executed_volume_30m']))}"
            ),
            "cadence_30m": (
                f"{candidate}|"
                f"{cadence_band(row['interprint_cadence_seconds_30m'])}"
            ),
            "spread": f"{candidate}|{spread_band(int(row['spread_cents']))}",
            "top5_bid_depth": f"{candidate}|{depth_band(top5_depth)}",
            "depth_at_or_ahead_X": (
                f"{candidate}|"
                f"{depth_band(float(row['displayed_depth_at_or_ahead_of_x']))}"
            ),
            "macro_regime": (
                f"{candidate}|{context.get('macro_target_status')}"
            ),
            "historical_cell": (
                f"{candidate}|{context.get('discovery_page_key')}"
            ),
        }
        for dimension, value in fields.items():
            add_bucket(buckets, dimension, value, rid)
        row_index.append({
            "episode_row_id": rid,
            "candidate_id": candidate,
            "event_id": event_id,
            "event_date": event["event_date"],
            "category": event["category"],
            "evidence_receipt": row["evidence_receipt"],
            "book_receipt": row["contemporaneous_book_receipt"],
        })
    cross_tabs = {}
    event_by_episode_id = {
        row["episode_row_id"]: row["event_id"] for row in row_index
    }
    for dimension, values in sorted(buckets.items()):
        cross_tabs[dimension] = [
            {
                "bucket": bucket,
                "candidate_episode_rows": len(ids),
                "distinct_games": len({
                    event_by_episode_id[rid] for rid in ids
                }),
                "episode_row_ids": sorted(ids),
            }
            for bucket, ids in sorted(values.items())
        ]
        if sum(row["candidate_episode_rows"] for row in cross_tabs[dimension]) != 6501:
            raise AttributionError(f"episode cross-tab does not conserve: {dimension}")
    positive = [row for row in episodes if row["d2_cents"] > 0]
    return {
        "candidate_episode_rows": len(episodes),
        "episode_rows_are_not_event_counts": True,
        "positive_d2_inside_combined_headroom": {
            "candidate_episode_rows": len(positive),
            "by_candidate": dict(Counter(
                row["candidate_id"] for row in positive
            )),
            "episode_row_ids": sorted(row["episode_id"] for row in positive),
        },
        "diagnostic_band_definitions": {
            "elapsed": [
                "LT_1M", "1M_TO_LT_5M", "5M_TO_LT_15M",
                "15M_TO_LT_1H", "1H_TO_LT_4H", "GE_4H",
            ],
            "volume": ["ZERO", "POSITIVE_LT_5", "GE_5"],
            "cadence": [
                "UNAVAILABLE_OR_SINGLE_PRINT", "LE_10S",
                "GT_10S_TO_60S", "GT_60S",
            ],
            "spread": [
                "ONE_CENT", "TWO_TO_THREE_CENTS", "FOUR_PLUS_CENTS"
            ],
            "depth": [
                "ZERO", "POSITIVE_LT_5", "FIVE_TO_LT_100", "GE_100"
            ],
            "not_policy_parameters": True,
        },
        "episode_receipt_index": row_index,
        "cross_tabs": cross_tabs,
        "metrics": None,
        "performance": None,
    }


def mechanism_matrix(
    decision_rows: list[Mapping[str, Any]],
    mechanism_table: Mapping[str, Any],
) -> dict[str, Any]:
    lookup = {
        row["mechanism"]: {
            "classification": row["classification"],
            "decision_effect": row["decision_effect"],
        }
        for row in mechanism_table["rows"]
    }
    mapping = {
        "target_selection_never_included_lawful_X": [
            "Trendpath_ATLAS_native_discovery_path",
            "nonself_external_BBO_and_top5_chain",
            "pair_combined_headroom",
        ],
        "first_fill_sibling_response_failed_to_create_exposure": [
            "pair_combined_headroom",
            "receipt_identified_positive_public_true_print",
        ],
        "target_included_X_but_no_initial_exposure_created": [
            "nonself_external_BBO_and_top5_chain",
            "pair_combined_headroom",
        ],
        "discovery_recognition_unavailable_or_no_call": [
            "drift_surfaces_v1", "band_map_v1", "divot_tables_v1",
        ],
        "policy_evidence_insufficient_to_distinguish": [
            "carried_last_trade",
        ],
        "maker_safety_reprice": ["external_ask_maker_safety"],
        "LIVE_AIM_reprice": ["LIVE_AIM_source_mapping"],
        "headroom_reprice": ["pair_combined_headroom"],
        "corridor_window_termination": ["timestamped_schedule_policy_clock"],
        "target_supersession": ["Trendpath_ATLAS_native_discovery_path"],
        "cancel_without_replacement": ["nonself_external_BBO_and_top5_chain"],
        "other_named_existing_action": ["nonself_external_BBO_and_top5_chain"],
        "unresolved": ["carried_last_trade"],
        "capacity_measurement_unproved": [
            "executed_share_volume_and_cadence",
            "taker_reach_probability",
            "full_depth_beyond_bound_top5",
            "nonself_external_BBO_and_top5_chain",
        ],
    }
    rows = []
    for layer in sorted({row["attributed_layer"] for row in decision_rows}):
        affected = [
            row for row in decision_rows if row["attributed_layer"] == layer
        ]
        mechanisms = []
        for name in mapping[layer]:
            if name not in lookup:
                raise AttributionError(f"mechanism missing from table: {name}")
            mechanisms.append({"mechanism": name, **lookup[name]})
        event_sets = defaultdict(set)
        for row in affected:
            event_sets[row["candidate_id"]].add(row["event_id"])
        overlap = (
            len(event_sets[CANDIDATES[0]] & event_sets[CANDIDATES[1]])
            if len(event_sets) else 0
        )
        rows.append({
            "decision_layer": layer,
            "proven_affected_candidate_rows": len(affected),
            "distinct_games": len({row["event_id"] for row in affected}),
            "qualifying_episodes": sum(
                int(row["lawful_qualifying_episode_count"]) for row in affected
            ),
            "candidate_overlap_distinct_games": overlap,
            "candidate_event_row_ids": sorted(
                f"{row['candidate_id']}|{row['event_id']}"
                for row in affected
            ),
            "mechanisms": mechanisms,
            "exact_evidence_sources": sorted({
                source for row in affected
                for source in row["exact_evidence_sources"]
            }),
            "what_is_proven": sorted({
                row["proof"] for row in affected
            }),
            "what_remains_unresolved": sorted({
                item for row in affected for item in row["missing_evidence"]
            }),
        })
    return {
        "mechanism_classification_totals":
            mechanism_table["classification_totals"],
        "proxy_never_promoted_to_BOUND": True,
        "rows": rows,
        "metrics": None,
        "performance": None,
    }


def source_manifest(
    repo: Path, raw_sources: list[Mapping[str, Any]]
) -> dict[str, Any]:
    inputs = [
        SOURCE_REL, TEST_REL, SPEC_REL,
        f"{V2_REL}/CORRECTED_EVENT_LEVEL_CENSUS.jsonl.gz",
        *V2_EPISODE_FILES,
        f"{V2_REL}/AUTHORITATIVE_FIRST_LEG_REFERENCE_RECEIPT.jsonl.gz",
        f"{V2_REL}/BOUNDED_POLICY_EXPOSURE_ATTRIBUTION.jsonl.gz",
        f"{V2_REL}/COUNTERFACTUAL_ORIENTATION_DIAGNOSTICS.jsonl.gz",
        f"{V2_REL}/BOUNDARY_SOURCE_RECEIPT.json",
        f"{V2_REL}/RECURRING_X_CLASS_RECEIPT.json",
        f"{V2_REL}/RAW_DIAGNOSTIC_CENSUS.json",
        f"{V2_REL}/SOURCE_HASH_MANIFEST.json",
        f"{V2_REL}/ARTIFACT_HASH_MANIFEST.json",
        *STREAM_FILES, ACTION_FILE, HEADROOM_FILE, MECHANISM_REL,
    ]
    rows = []
    for relative in inputs:
        path = repo / relative
        raw = path.read_bytes()
        rows.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git_blob_oid(raw),
        })
    audit_rows = []
    for relative in (AUDIT_REPORT, AUDIT_RECEIPT):
        raw = subprocess.check_output(
            ["git", "show", f"{AUDIT}:{relative}"], cwd=repo
        )
        audit_rows.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git(repo, "rev-parse", f"{AUDIT}:{relative}"),
        })
    return {
        "schema_version": VERSION + "-source-manifest-v1",
        "implementation_parent": PARENT,
        "controlling_independent_PASS": AUDIT,
        "passed_V2_package": V2_REL,
        "immutable_inputs": rows,
        "audit_artifacts": audit_rows,
        "targeted_private_source_receipts": raw_sources,
        "raw_source_role": (
            "resolve exact already-frozen no-fill witness IDs only; "
            "no opportunity construction or selection"
        ),
        "sealed_dates": sorted(SEALED_DATES),
        "metrics": None,
        "performance": None,
    }


def inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def finalize_artifacts(output: Path) -> None:
    rows = inventory(output)
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "artifact_count_before_manifest": len(rows),
        "artifacts": rows,
        "metrics": None,
        "performance": None,
    })


def build(repo: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise AttributionError(f"refusing existing output: {output}")
    if git(repo, "rev-parse", "HEAD") != PARENT:
        raise AttributionError("builder requires exact implementation parent")
    if git(repo, "rev-parse", "origin/codex/window1-definition") != PARENT:
        raise AttributionError("remote Codex tip changed")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", AUDIT,
         "origin/audit/window1-independent"],
        cwd=repo, check=False,
    ).returncode:
        raise AttributionError("controlling PASS not on fetched audit branch")
    output.mkdir(parents=True)

    v2 = load_v2(repo)
    events = v2["events"]
    episodes = v2["episodes"]
    recovered = [row for row in events if event_recovered(row)]
    if len(recovered) != 47:
        raise AttributionError("recovered candidate-row count changed")
    event_index = {
        (row["candidate_id"], row["event_id"]): row for row in events
    }
    episode_index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in episodes:
        episode_index[(row["candidate_id"], row["event_id"])].append(row)
    path_orientations = [
        row for row in v2["orientations"] if row["path_exists"]
    ]
    policy_keys = {
        (row["candidate_id"], row["event_id"]) for row in recovered
    } | {
        (row["candidate_id"], row["event_id"]) for row in path_orientations
    }
    policy = load_policy_rows(repo, policy_keys)

    crosswalk = build_crosswalk(recovered)
    write_json(output / "SHARED_UNIQUE_EVENT_CROSSWALK.json", crosswalk)
    episode_breakdown = feature_breakdown(
        episodes, event_index, policy["streams"]
    )
    write_json(output / "EPISODE_FEATURE_BREAKDOWN.json", episode_breakdown)

    decision_writer = GzipJsonlWriter(
        output / "DECISION_LAYER_EVENT_LEDGER.jsonl.gz"
    )
    never_writer = GzipJsonlWriter(
        output / "NEVER_EXPOSED_ATTRIBUTION.jsonl.gz"
    )
    moved_writer = GzipJsonlWriter(
        output / "MOVED_AWAY_ATTRIBUTION.jsonl.gz"
    )
    decision_rows = []
    capacity_rows = []
    for event in sorted(recovered, key=lambda row: (
        row["candidate_id"], row["event_id"]
    )):
        key = (event["candidate_id"], event["event_id"])
        event_episodes = episode_index[key]
        earliest = min(
            event_episodes,
            key=lambda row: (
                float(row["timestamp"]), str(row["evidence_type"]),
                str(row["evidence_receipt"]),
            ),
        )
        base = {
            "schema_version": VERSION + "-decision-event-v1",
            "candidate_id": event["candidate_id"],
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "category": event["category"],
            "credited_first_leg": event["credited_first_leg"],
            "sibling_leg_id": event["sibling_leg_id"],
            "earliest_lawful_opportunity": {
                key_name: earliest[key_name] for key_name in (
                    "episode_id", "timestamp", "evidence_type",
                    "evidence_receipt", "price_x_cents",
                    "contemporaneous_book_receipt",
                    "contemporaneous_bid_cents", "d2_cents",
                    "combined_delta_cents",
                )
            },
            "lawful_qualifying_episode_count":
                event["lawful_qualifying_episode_count"],
            "terminal_policy_attribution": event["primary_classification"],
            "metrics": None,
            "performance": None,
            "scored": False,
        }
        if event["primary_classification"] == (
            "lawful_opportunity_but_policy_never_exposed"
        ):
            detail = attribute_never_exposed(
                event, earliest, policy["streams"][key],
                policy["headroom"][key],
            )
            exact_sources = [
                f"{V2_REL}/CORRECTED_EVENT_LEVEL_CENSUS.jsonl.gz",
                *V2_EPISODE_FILES,
                *STREAM_FILES,
                HEADROOM_FILE,
            ]
            proof = detail["proof"]
            missing = detail["missing_evidence"]
            out = {**base, **detail}
            never_writer.write(out)
        elif event["primary_classification"] == "policy_moved_away":
            detail = attribute_moved(
                event, event_episodes, policy["streams"][key],
                policy["actions"][key],
            )
            exact_sources = [
                f"{V2_REL}/CORRECTED_EVENT_LEVEL_CENSUS.jsonl.gz",
                *V2_EPISODE_FILES,
                *STREAM_FILES,
                ACTION_FILE,
            ]
            proof = (
                "closed interval and same-timestamp frozen action receipt "
                f"identify {detail['attributed_layer']}"
            )
            missing = [] if detail["attributed_layer"] != "unresolved" else [
                "same_timestamp_action_authority"
            ]
            out = {**base, **detail, "proof": proof, "missing_evidence": missing}
            moved_writer.write(out)
        elif event["primary_classification"] == (
            "price_reached_but_five_contract_capacity_unproved"
        ):
            rows = sorted(event_episodes, key=lambda row: (
                float(row["timestamp"]), str(row["episode_id"])
            ))
            detail = {
                "attributed_layer": "capacity_measurement_unproved",
                "proof": (
                    "price evidence exists while every retained episode's "
                    "chronological executed capacity remains below five"
                ),
                "missing_evidence": [
                    "five_contract_chronological_executed_capacity"
                ],
            }
            capacity = {
                **base,
                **detail,
                "episodes": [
                    {
                        key_name: row[key_name] for key_name in (
                            "episode_id", "timestamp", "evidence_type",
                            "evidence_receipt", "price_x_cents",
                            "executed_volume_at_or_better_after_episode",
                            "five_contract_capacity_proven",
                            "contemporaneous_book_receipt",
                            "contemporaneous_bid_cents",
                            "contemporaneous_ask_cents", "spread_cents",
                            "top5_bids", "top5_asks",
                            "displayed_depth_at_or_ahead_of_x",
                            "rolling_print_count_30m",
                            "rolling_executed_volume_30m",
                            "interprint_cadence_seconds_30m",
                        )
                    } | {
                        "missing_capacity_contracts": max(
                            0.0,
                            5.0 - float(
                                row[
                                    "executed_volume_at_or_better_after_episode"
                                ]
                            ),
                        )
                    }
                    for row in rows
                ],
                "price_reach_is_not_erased": True,
                "policy_absence_class": False,
            }
            capacity_rows.append(capacity)
            exact_sources = [
                f"{V2_REL}/CORRECTED_EVENT_LEVEL_CENSUS.jsonl.gz",
                *V2_EPISODE_FILES,
            ]
            proof = detail["proof"]
            missing = detail["missing_evidence"]
            out = capacity
        else:
            raise AttributionError("unknown recovered terminal class")
        decision = {
            **base,
            "attributed_layer": out["attributed_layer"],
            "proof": proof,
            "missing_evidence": missing,
            "exact_evidence_sources": exact_sources,
        }
        decision_writer.write(decision)
        decision_rows.append(decision)
    for writer in (decision_writer, never_writer, moved_writer):
        writer.close()
    write_json(output / "CAPACITY_UNPROVED_RECEIPT.json", {
        "candidate_rows": capacity_rows,
        "candidate_row_count": len(capacity_rows),
        "distinct_games": len({row["event_id"] for row in capacity_rows}),
        "price_reach_and_capacity_separate": True,
        "policy_absence_conflation": False,
        "metrics": None,
        "performance": None,
    })

    resolved, raw_sources = resolve_nofill_witnesses(
        repo, path_orientations, v2["boundaries"]
    )
    nofill_sets = {
        candidate: {
            row["event_id"] for row in path_orientations
            if row["candidate_id"] == candidate
        }
        for candidate in CANDIDATES
    }
    geometry_writer = GzipJsonlWriter(
        output / "NOFILL_COUNTERFACTUAL_GEOMETRY.jsonl.gz"
    )
    path_by_event: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in sorted(path_orientations, key=lambda item: (
        item["candidate_id"], item["event_id"], item["orientation_id"]
    )):
        witness = row["witness"]
        first_detail = resolved[(
            row["event_id"], row["first_leg_id"],
            witness["first_episode_id"],
        )]
        sibling_detail = resolved[(
            row["event_id"], row["sibling_leg_id"],
            witness["sibling_episode_id"],
        )]
        stream = policy["streams"][(row["candidate_id"], row["event_id"])]
        out = {
            "schema_version": VERSION + "-nofill-orientation-v1",
            "row_type": "orientation_diagnostic",
            "candidate_id": row["candidate_id"],
            "event_id": row["event_id"],
            "event_date": event_index[(
                row["candidate_id"], row["event_id"]
            )]["event_date"],
            "category": event_index[(
                row["candidate_id"], row["event_id"]
            )]["category"],
            "orientation_id": row["orientation_id"],
            "first_leg_id": row["first_leg_id"],
            "sibling_leg_id": row["sibling_leg_id"],
            "witness": witness,
            "first_episode_receipt": first_detail,
            "sibling_episode_receipt": sibling_detail,
            "first_macro_context": evidence_context(
                stream, row["first_leg_id"]
            ),
            "sibling_macro_context": evidence_context(
                stream, row["sibling_leg_id"]
            ),
            "elapsed_gap_seconds": (
                float(witness["sibling_timestamp"])
                - float(witness["first_timestamp"])
            ),
            "counterfactual": True,
            "realized_policy_miss_claim": False,
            "metrics": None,
            "performance": None,
        }
        geometry_writer.write(out)
        path_by_event[(row["candidate_id"], row["event_id"])].append(
            row["orientation_id"]
        )
    for candidate in CANDIDATES:
        other = CANDIDATES[1] if candidate == CANDIDATES[0] else CANDIDATES[0]
        for event_id in sorted(nofill_sets[candidate]):
            ids = sorted(path_by_event[(candidate, event_id)])
            geometry_writer.write({
                "schema_version": VERSION + "-nofill-event-union-v1",
                "row_type": "candidate_event_union",
                "candidate_id": candidate,
                "event_id": event_id,
                "event_date": event_index[(candidate, event_id)]["event_date"],
                "category": event_index[(candidate, event_id)]["category"],
                "orientation_count": len(ids),
                "orientation_ids": ids,
                "shared_or_unique": (
                    "SHARED" if event_id in nofill_sets[other]
                    else "CANDIDATE_UNIQUE"
                ),
                "counterfactual": True,
                "realized_policy_miss_claim": False,
                "metrics": None,
                "performance": None,
            })
    geometry_writer.close()

    mechanism_table = json.loads((repo / MECHANISM_REL).read_text(
        encoding="utf-8"
    ))
    matrix = mechanism_matrix(decision_rows, mechanism_table)
    write_json(output / "MECHANISM_STATUS_DECISION_MATRIX.json", matrix)

    layer_counts = Counter(row["attributed_layer"] for row in decision_rows)
    terminal_counts = Counter(
        row["terminal_policy_attribution"] for row in decision_rows
    )
    candidate_terminal = {
        candidate: Counter(
            row["terminal_policy_attribution"] for row in decision_rows
            if row["candidate_id"] == candidate
        )
        for candidate in CANDIDATES
    }
    nofill_shared = nofill_sets[CANDIDATES[0]] & nofill_sets[CANDIDATES[1]]
    conservation = {
        "D_per_candidate": 804,
        "recovered_candidate_rows": len(decision_rows),
        "recovered_distinct_games": len({
            row["event_id"] for row in decision_rows
        }),
        "terminal_attribution": dict(terminal_counts),
        "decision_layers": dict(layer_counts),
        "terminal_candidate_event_row_ids": {
            terminal: sorted(
                f"{row['candidate_id']}|{row['event_id']}"
                for row in decision_rows
                if row["terminal_policy_attribution"] == terminal
            )
            for terminal in sorted(terminal_counts)
        },
        "decision_layer_candidate_event_row_ids": {
            layer: sorted(
                f"{row['candidate_id']}|{row['event_id']}"
                for row in decision_rows
                if row["attributed_layer"] == layer
            )
            for layer in sorted(layer_counts)
        },
        "candidate_terminal_conservation": {
            candidate: dict(candidate_terminal[candidate])
            for candidate in CANDIDATES
        },
        "required_equalities": {
            "47_equals_28_plus_17_plus_2": (
                len(decision_rows) == 47
                and terminal_counts[
                    "lawful_opportunity_but_policy_never_exposed"
                ] == 28
                and terminal_counts["policy_moved_away"] == 17
                and terminal_counts[
                    "price_reached_but_five_contract_capacity_unproved"
                ] == 2
            ),
            "macro_hold_22_equals_14_plus_7_plus_1": (
                sum(candidate_terminal[CANDIDATES[0]].values()) == 22
                and sorted(candidate_terminal[CANDIDATES[0]].values())
                == [1, 7, 14]
            ),
            "macro_micro_25_equals_14_plus_10_plus_1": (
                sum(candidate_terminal[CANDIDATES[1]].values()) == 25
                and sorted(candidate_terminal[CANDIDATES[1]].values())
                == [1, 10, 14]
            ),
            "episodes_3226_plus_3275_equals_6501": (
                Counter(row["candidate_id"] for row in episodes)
                == Counter({CANDIDATES[0]: 3226, CANDIDATES[1]: 3275})
            ),
            "positive_d2_equals_6310": (
                len(episode_breakdown[
                    "positive_d2_inside_combined_headroom"
                ]["episode_row_ids"]) == 6310
            ),
            "nofill_unions_65_and_68": (
                len(nofill_sets[CANDIDATES[0]]) == 65
                and len(nofill_sets[CANDIDATES[1]]) == 68
            ),
        },
        "episode_candidate_rows": 6501,
        "positive_d2_candidate_episode_rows": 6310,
        "nofill": {
            "candidate_event_union_counts": {
                candidate: len(nofill_sets[candidate])
                for candidate in CANDIDATES
            },
            "shared_distinct_games": len(nofill_shared),
            "shared_event_ids": sorted(nofill_shared),
            "macro_hold_only_distinct_games":
                len(nofill_sets[CANDIDATES[0]] - nofill_shared),
            "macro_hold_only_event_ids":
                sorted(nofill_sets[CANDIDATES[0]] - nofill_shared),
            "macro_micro_only_distinct_games":
                len(nofill_sets[CANDIDATES[1]] - nofill_shared),
            "macro_micro_only_event_ids":
                sorted(nofill_sets[CANDIDATES[1]] - nofill_shared),
            "candidate_event_union_ids": {
                candidate: sorted(nofill_sets[candidate])
                for candidate in CANDIDATES
            },
            "orientation_path_rows": Counter(
                row["candidate_id"] for row in path_orientations
            ),
            "both_one_neither": {
                candidate: {
                    key: v2["summary"]["final_nofill"][candidate][key]
                    for key in ("both", "one", "neither")
                }
                for candidate in CANDIDATES
            },
        },
        "recurring_X": {
            "ledger_rejected": [
                v2["summary"]["final_naked"][candidate][
                    "recurring_x_levels_globalfirst_rejected"
                ] for candidate in CANDIDATES
            ],
            "raw_absent_from_ledger": [
                v2["summary"]["final_naked"][candidate][
                    "x_levels_lawful_recurrence_but_no_ledger_observation"
                ] for candidate in CANDIDATES
            ],
        },
        "all_required_equalities_pass": True,
        "candidate_rows_distinct_from_games": True,
        "episodes_distinct_from_events": True,
        "metrics": None,
        "performance": None,
    }
    if not all(conservation["required_equalities"].values()):
        raise AttributionError("operator conservation failed")
    write_json(output / "CONSERVATION_RECEIPT.json", conservation)
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "scorer_imported": False,
        "scorer_invoked": False,
        "benchmark_executed": False,
        "strategy_or_candidate_changed": False,
        "parameter_proposed_or_tuned": False,
        "ranking_or_selection": False,
        "opportunity_rescanned_or_redefined": False,
        "raw_access_limited_to_fixed_witness_receipt_resolution": True,
        "holdout_accessed": False,
        "live_or_production_accessed": False,
        "orders_positions_window2_exits_settlement_DCA_accessed": False,
        "metrics": None,
        "performance": None,
    })
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest(
        repo, raw_sources
    ))
    report = f"""# Window-1 decision-layer attribution PRE-RUN

This additions-only package diagnoses the independently passed asynchronous
opportunity census V2. It neither constructs opportunities nor scores,
changes, ranks, or tunes a policy.

- Parent: `{PARENT}`
- Controlling independent PASS: `{AUDIT}`
- D: 804 per candidate
- Recovered candidate rows: {len(decision_rows)} across {conservation['recovered_distinct_games']} distinct games
- Shared recovered games: {crosswalk['shared_event_count']}
- Macro-hold only recovered games: {crosswalk['macro_hold_only_count']}
- Macro-micro only recovered games: {crosswalk['macro_micro_only_count']}
- Never exposed / moved away / capacity unproved: 28 / 17 / 2
- Decision-layer counts: `{compact(dict(layer_counts))}`
- Qualifying episodes: 3,226 / 3,275 = 6,501
- Positive-d2 candidate episodes inside strict combined headroom: 6,310
- No-fill counterfactual event unions: 65 / 68
- No-fill shared / hold-only / micro-only games: {len(nofill_shared)} / {len(nofill_sets[CANDIDATES[0]] - nofill_shared)} / {len(nofill_sets[CANDIDATES[1]] - nofill_shared)}
- All benchmark/performance metrics: null

Candidate rows, distinct games, episodes, price reach, capacity, policy
exposure, and counterfactual paths remain separate throughout.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    return {
        "decision_layer_counts": dict(layer_counts),
        "crosswalk": {
            key: crosswalk[key] for key in (
                "shared_event_count", "macro_hold_only_count",
                "macro_micro_only_count", "distinct_game_union_count",
            )
        },
        "conservation": conservation["required_equalities"],
        "episode_rows": 6501,
        "positive_d2_rows": 6310,
        "nofill_shared_games": len(nofill_shared),
        "metrics": None,
        "performance": None,
    }


def freeze(repo: Path) -> dict[str, Any]:
    target = repo / PACKAGE_REL
    if target.exists():
        raise AttributionError(f"refusing existing package: {target}")
    with tempfile.TemporaryDirectory(prefix="w1-layer-a-") as left_name:
        with tempfile.TemporaryDirectory(prefix="w1-layer-b-") as right_name:
            left = Path(left_name) / "package"
            right = Path(right_name) / "package"
            build(repo, left)
            finalize_artifacts(left)
            build(repo, right)
            finalize_artifacts(right)
            left_inventory = inventory(left)
            right_inventory = inventory(right)
            if left_inventory != right_inventory:
                raise AttributionError("clean regeneration mismatch")
            shutil.copytree(left, target)
    receipt = {
        "schema_version": VERSION + "-determinism-v1",
        "clean_build_count": 2,
        "byte_identical": True,
        "inventory": inventory(target),
        "metrics": None,
        "performance": None,
    }
    write_json(target / "DETERMINISTIC_REGENERATION_RECEIPT.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument(
        "--mode", required=True, choices=("validate-only", "freeze")
    )
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.mode == "freeze":
        result = freeze(repo)
    else:
        with tempfile.TemporaryDirectory(prefix="w1-layer-validate-") as name:
            output = Path(name) / "package"
            result = build(repo, output)
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
