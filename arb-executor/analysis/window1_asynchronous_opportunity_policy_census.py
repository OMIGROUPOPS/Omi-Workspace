#!/usr/bin/env python3
"""Score-free asynchronous Window-1 opportunity-vs-policy census.

This module reconciles frozen Range-Attack V2 market evidence, policy
exposure, and credited-fill facts.  It does not import or invoke a scorer and
does not construct policy actions or candidate parameters.
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import io
import json
import math
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping


VERSION = "window1-asynchronous-opportunity-policy-census-v1"
PARENT = "53eaf2b5b10b82b86b71b651bb720028a6ee7979"
CONTROLLING_AUDIT = "e6aab4698015a2c45e6e9a607c7a0c994e756d8f"
STRICT_ASK_IMPLEMENTATION = "851346343eecbff64bd836992876592784874c86"
STRICT_ASK_PASS = "5579b93774267779ae916eb9cb46766de66a9efe"
STRICT_ASK_DETERMINISM = "d413f23125d5931a56077c70f475d8815ffe36c0"
PACKAGE_REL = (
    ".claude/window1_asynchronous_opportunity_policy_census_20260726"
)
STRICT_REL = ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
RESULT_REL = (
    ".claude/window1_range_attack_results_"
    "w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2"
)
CACHE_REL = "../OMI-Window1-private/fit-local/guarded-cache-v3"
DATA_MANIFEST_REL = (
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_DATA_BINDING_MANIFEST.json"
)
MECHANISM_REL = (
    ".claude/window1_range_attack_prerun_20260725/"
    "MECHANISM_RECOVERY_TABLE.json"
)
AUDIT_REPORT_REL = (
    ".claude/audit_20260726_window1_range_attack_execution_results/"
    "AUDIT_REPORT.md"
)
AUDIT_RECEIPTS_REL = (
    ".claude/audit_20260726_window1_range_attack_execution_results/"
    "AUDIT_RECEIPTS.json"
)
CANDIDATES = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
RESULT_LEDGER_BY_CANDIDATE = {
    CANDIDATES[0]: (
        f"{RESULT_REL}/"
        "01_w1_range_attack__macro_hold__combined_headroom_EVENT_LEDGER.jsonl"
    ),
    CANDIDATES[1]: (
        f"{RESULT_REL}/"
        "02_w1_range_attack__macro_micro__combined_headroom_EVENT_LEDGER.jsonl"
    ),
}
LADDER_RELS = tuple(
    f"{STRICT_REL}/WINDOW1_PRICE_RANGE_LADDER_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
STREAM_RELS = tuple(
    f"{STRICT_REL}/UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
ACTION_REL = f"{STRICT_REL}/ACTION_AUTHORITY_RECEIPTS.jsonl.gz"
HEADROOM_REL = f"{STRICT_REL}/COMBINED_HEADROOM_RECEIPTS.jsonl.gz"
FILLABILITY_REL = f"{STRICT_REL}/PRICE_FILLABILITY_RECEIPTS.jsonl.gz"
DEPTH_REL = f"{STRICT_REL}/DEPTH_VOLUME_STRESS_RECEIPTS.jsonl.gz"
PAIR_REL = f"{STRICT_REL}/PAIRWISE_ASYNCHRONOUS_OPPORTUNITY_LEDGER.jsonl.gz"
TERMINAL_CLASSES = (
    "completed_by_policy",
    "lawful_in_budget_opportunity_policy_never_exposed",
    "policy_exposed_execution_or_strict_ask_proved_not_credited",
    "policy_exposed_without_execution_proof",
    "price_reached_five_contract_capacity_unproved",
    "evidence_unavailable",
    "no_lawful_in_budget_later_sibling_opportunity_observed",
)
TERMINAL_PRIORITY = {
    "completed_by_policy": 0,
    "policy_exposed_execution_or_strict_ask_proved_not_credited": 1,
    "price_reached_five_contract_capacity_unproved": 2,
    "lawful_in_budget_opportunity_policy_never_exposed": 3,
    "policy_exposed_without_execution_proof": 4,
    "evidence_unavailable": 5,
    "no_lawful_in_budget_later_sibling_opportunity_observed": 6,
}
DEVELOPMENT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(12, 21)
)
SEALED_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt"}
SOURCE_RELS = (
    "arb-executor/analysis/window1_asynchronous_opportunity_policy_census.py",
    "arb-executor/tests/test_window1_asynchronous_opportunity_policy_census.py",
    MECHANISM_REL,
    *LADDER_RELS,
    *STREAM_RELS,
    ACTION_REL,
    HEADROOM_REL,
    FILLABILITY_REL,
    DEPTH_REL,
    PAIR_REL,
    *RESULT_LEDGER_BY_CANDIDATE.values(),
    DATA_MANIFEST_REL,
    f"{STRICT_REL}/ARTIFACT_HASH_MANIFEST.json",
    f"{STRICT_REL}/WINDOW1_RANGE_ATTACK_V2_PRE_RUN_MANIFEST.json",
)


class CensusError(RuntimeError):
    """Raised when a frozen census invariant fails."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def canonical_text_bytes(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(raw)}\0".encode("ascii") + raw
    ).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_row(repo: Path, relative: str) -> dict[str, Any]:
    path = (repo / relative).resolve()
    if not path.is_file():
        raise CensusError(f"missing frozen source: {relative}")
    raw = path.read_bytes()
    is_text = path.suffix.lower() in TEXT_SUFFIXES
    identity = canonical_text_bytes(raw) if is_text else raw
    return {
        "path": relative,
        "identity_bytes": len(identity),
        "sha256": hashlib.sha256(identity).hexdigest(),
        "git_blob_oid": git_blob_oid(identity),
        "hash_basis": "canonical_lf_text" if is_text else "exact_binary",
    }


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args], cwd=repo, text=True,
        capture_output=True, check=False,
    )
    if process.returncode:
        raise CensusError(
            f"git {' '.join(args)} failed: {process.stderr.strip()}"
        )
    return process.stdout.strip()


def commit_blob(
    repo: Path,
    commit: str,
    relative: str,
) -> dict[str, Any]:
    oid = git(repo, "rev-parse", f"{commit}:{relative}")
    process = subprocess.run(
        ["git", "cat-file", "blob", oid], cwd=repo,
        capture_output=True, check=True,
    )
    raw = process.stdout
    return {
        "commit": commit,
        "path": relative,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_oid": oid,
    }


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def iter_gzip_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        (
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
            + "\n"
        ).encode("utf-8")
    )


class DeterministicGzipJsonlWriter:
    def __init__(self, path: Path) -> None:
        self._raw = path.open("wb")
        self._gzip = gzip.GzipFile(
            filename="", mode="wb", fileobj=self._raw, mtime=0
        )
        self.rows = 0

    def write(self, row: Mapping[str, Any]) -> None:
        self._gzip.write((compact(row) + "\n").encode("utf-8"))
        self.rows += 1

    def close(self) -> None:
        self._gzip.close()
        self._raw.close()


def exact_cent(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise CensusError(f"{field} is boolean")
    if isinstance(value, int):
        result = value
    elif isinstance(value, float) and math.isfinite(value) and value.is_integer():
        result = int(value)
    else:
        raise CensusError(f"{field} is not an exact integer cent")
    if not 1 <= result <= 99:
        raise CensusError(f"{field} is outside 1..99")
    return result


def positive_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) <= 0
    ):
        raise CensusError(f"{field} is not finite and positive")
    return float(value)


def headroom_d2_max(d1: float, fee: float = 0.0) -> int:
    return int(math.floor(-float(d1) - float(fee) - 1.0))


def strict_combined_budget(d1: float, d2: float, fee: float = 0.0) -> bool:
    return float(d1) + float(d2) + float(fee) < 0.0


def strictly_later(first_ts: float, sibling_ts: float) -> bool:
    return float(sibling_ts) > float(first_ts)


def first_lawful_observation(row: Mapping[str, Any]) -> dict[str, Any] | None:
    """Return earliest evidence; strict ask wins an exact timestamp tie."""
    choices: list[tuple[float, int, str, Mapping[str, Any]]] = []
    ask = row.get("first_ask_strictly_below")
    if isinstance(ask, Mapping):
        choices.append((float(ask["ts"]), 0, "STRICT_ASK_CERTAIN_FILL", ask))
    trade = row.get("first_true_print_at_or_below")
    if isinstance(trade, Mapping):
        choices.append((float(trade["ts"]), 1, "PRICE_AT_X", trade))
    if not choices:
        return None
    ts, _, evidence_type, evidence = min(choices)
    return {
        "evidence_type": evidence_type,
        "timestamp": ts,
        "receipt": str(evidence["receipt"]),
        "price_cents": (
            exact_cent(evidence["price"], "true-print price")
            if evidence_type == "PRICE_AT_X" else None
        ),
        "executed_size": (
            positive_number(evidence["size"], "true-print size")
            if evidence_type == "PRICE_AT_X" else None
        ),
    }


def orientation_ids(legs: Iterable[str]) -> tuple[tuple[str, str], ...]:
    values = tuple(str(value) for value in legs)
    if len(values) != 2 or len(set(values)) != 2:
        raise CensusError("orientation fixture must contain two distinct legs")
    return ((values[0], values[1]), (values[1], values[0]))


def volume_band(value: float) -> str:
    if value <= 0:
        return "ZERO"
    if value < 5:
        return "POSITIVE_LT5"
    if value < 25:
        return "FIVE_TO_LT25"
    return "GE25"


def cadence_band(count: int, cadence: float | None) -> str:
    if count <= 0:
        return "NO_PRINT"
    if count == 1 or cadence is None:
        return "ONE_PRINT"
    if cadence < 60:
        return "FAST_LT60S"
    if cadence < 300:
        return "MEDIUM_60_TO_LT300S"
    return "SLOW_GE300S"


def depth_band(value: float | None) -> str:
    if value is None:
        return "UNAVAILABLE"
    if value < 5:
        return "LT5"
    if value < 50:
        return "FIVE_TO_LT50"
    return "GE50"


def spread_band(value: int | None) -> str:
    if value is None:
        return "UNAVAILABLE"
    if value <= 1:
        return "ONE_OR_LESS"
    if value <= 3:
        return "TWO_TO_THREE"
    return "FOUR_PLUS"


def elapsed_band(value: float | None) -> str:
    if value is None:
        return "NO_LATER_OPPORTUNITY"
    if value < 60:
        return "LT1M"
    if value < 300:
        return "ONE_TO_LT5M"
    if value < 900:
        return "FIVE_TO_LT15M"
    if value < 1800:
        return "FIFTEEN_TO_LT30M"
    if value < 3600:
        return "THIRTY_TO_LT60M"
    return "GE60M"


def _latest_before(
    rows: list[Mapping[str, Any]],
    timestamp: float,
    field: str,
) -> Mapping[str, Any] | None:
    if not rows:
        return None
    positions = [float(row[field]) for row in rows]
    index = bisect.bisect_right(positions, float(timestamp)) - 1
    return rows[index] if index >= 0 else None


def _book_context(
    snapshots: list[Mapping[str, Any]],
    prints: list[Mapping[str, Any]],
    timestamp: float,
    target: int,
) -> dict[str, Any]:
    snapshot = _latest_before(snapshots, timestamp, "ts")
    prior_prints = [
        row for row in prints
        if float(row["ts"]) <= float(timestamp) and float(row["size"]) > 0
    ]
    if snapshot is None:
        return {
            "available": False,
            "reason": "market_evidence_unavailable_no_lawful_BBO",
            "timestamp": timestamp,
            "nonself_best_bid_cents": None,
            "nonself_best_ask_cents": None,
            "spread_cents": None,
            "top5_bids": [],
            "top5_asks": [],
            "displayed_depth_at_or_ahead_of_X": None,
            "last_trade_cents": None,
            "last_trade_execution_at": None,
            "last_trade_provenance": None,
        }
    bids = [
        [exact_cent(row[0], "bid price"), positive_number(row[1], "bid size")]
        for row in snapshot.get("bids") or []
        if float(row[1]) > 0
    ][:5]
    asks = [
        [exact_cent(row[0], "ask price"), positive_number(row[1], "ask size")]
        for row in snapshot.get("asks") or []
        if float(row[1]) > 0
    ][:5]
    bid = bids[0][0] if bids else None
    ask = asks[0][0] if asks else None
    last_trade_raw = snapshot.get("last_trade")
    last_trade = (
        exact_cent(last_trade_raw, "last trade")
        if isinstance(last_trade_raw, (int, float))
        and not isinstance(last_trade_raw, bool)
        and float(last_trade_raw) > 0
        else None
    )
    matching_print = next(
        (
            row for row in reversed(prior_prints)
            if last_trade is not None and int(row["price"]) == last_trade
        ),
        None,
    )
    return {
        "available": bool(bids and asks),
        "reason": None if bids and asks else
            "market_evidence_unavailable_no_lawful_BBO",
        "timestamp": float(snapshot["ts"]),
        "source": str(snapshot.get("source") or ""),
        "nonself_best_bid_cents": bid,
        "nonself_best_ask_cents": ask,
        "spread_cents": ask - bid if ask is not None and bid is not None else None,
        "top5_bids": bids,
        "top5_asks": asks,
        "displayed_depth_at_or_ahead_of_X": (
            sum(size for price, size in bids if price >= target)
            if bids else None
        ),
        "last_trade_cents": last_trade,
        "last_trade_execution_at": (
            float(matching_print["ts"]) if matching_print is not None else None
        ),
        "last_trade_provenance": (
            "VERIFIED_PRINT_TIMESTAMP"
            if matching_print is not None else
            "CARRIED_EXECUTION_TIME_UNKNOWN" if last_trade is not None
            else None
        ),
    }


def _rolling_flow(
    prints: list[Mapping[str, Any]],
    timestamp: float,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for minutes in (5, 15, 30):
        left = timestamp - minutes * 60
        rows = [
            row for row in prints
            if left <= float(row["ts"]) <= timestamp
            and float(row["size"]) > 0
        ]
        output[f"print_count_{minutes}m"] = len(rows)
        output[f"executed_volume_{minutes}m"] = sum(
            float(row["size"]) for row in rows
        )
    trailing = [
        row for row in prints
        if timestamp - 1800 <= float(row["ts"]) <= timestamp
        and float(row["size"]) > 0
    ]
    if len(trailing) >= 2:
        intervals = [
            float(right["ts"]) - float(left["ts"])
            for left, right in zip(trailing, trailing[1:])
            if float(right["ts"]) > float(left["ts"])
        ]
        output["inter_print_cadence_seconds_30m"] = (
            sum(intervals) / len(intervals) if intervals else None
        )
        first = int(trailing[0]["price"])
        last = int(trailing[-1]["price"])
        output["trailing_price_signature_30m"] = (
            "rising" if last > first else "falling" if last < first else "flat"
        )
    else:
        output["inter_print_cadence_seconds_30m"] = None
        output["trailing_price_signature_30m"] = "flat"
    return output


def classify_orientation(
    *,
    boundary_available: bool,
    d1_available: bool,
    completed_by_policy: bool,
    later_opportunities: list[Mapping[str, Any]],
    potential_exposures_without_evidence: int,
) -> tuple[str, str]:
    """Apply one documented evidence-first terminal classification."""
    if completed_by_policy:
        return "completed_by_policy", "both_guarded_policy_fills_temporally_match"
    if not boundary_available or not d1_available:
        return "evidence_unavailable", "boundary_or_causal_BBO_unavailable"
    exposed_proved = [
        row for row in later_opportunities
        if row["policy_exposed_at_X"] and not row["policy_credited_fill"]
    ]
    if exposed_proved:
        return (
            "policy_exposed_execution_or_strict_ask_proved_not_credited",
            "policy_was_resting_at_lawful_evidence_but_credit_absent",
        )
    if later_opportunities:
        capacity_unproved = [
            row for row in later_opportunities
            if row["price_reached"]
            and not row["strict_ask_certain_fill"]
            and not row["five_contract_capacity_proven"]
        ]
        if len(capacity_unproved) == len(later_opportunities):
            return (
                "price_reached_five_contract_capacity_unproved",
                "price_reach_preserved_capacity_remains_unproved",
            )
        moved = any(
            row["policy_moved_away_before_observation"]
            for row in later_opportunities
        )
        return (
            "lawful_in_budget_opportunity_policy_never_exposed",
            "policy_moved_away_before_observation"
            if moved else "policy_never_exposed_at_lawful_X",
        )
    if potential_exposures_without_evidence:
        return (
            "policy_exposed_without_execution_proof",
            "policy_exposure_observed_without_print_or_strict_ask_proof",
        )
    return (
        "no_lawful_in_budget_later_sibling_opportunity_observed",
        "no_strictly_later_in_budget_price_or_strict_ask_observation",
    )


def _load_stream_summaries(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for relative in STREAM_RELS:
        for wrapper in iter_gzip_jsonl(repo / relative):
            stream = wrapper["stream"]
            key = (str(wrapper["candidate_id"]), str(wrapper["event_id"]))
            evidence = {
                str(row["leg_id"]): row
                for row in stream.get("evidence_census_by_leg") or []
            }
            output[key] = {
                "category": str(wrapper["category"]),
                "event_date": str(wrapper["event_date"]),
                "intervals_by_leg": {
                    str(leg): list(rows)
                    for leg, rows in (
                        stream.get("order_intervals_by_leg") or {}
                    ).items()
                },
                "evidence_by_leg": evidence,
            }
    if len(output) != 1608:
        raise CensusError("frozen candidate streams do not conserve 1,608")
    return output


def _load_actions(
    repo: Path,
) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    output: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in iter_gzip_jsonl(repo / ACTION_REL):
        causal = row.get("causal_state") or {}
        flow = causal.get("flow") or {}
        macro = causal.get("macro") or {}
        output[(
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        )].append({
            "timestamp": float(row["timestamp"]),
            "action": str(row["action"]),
            "price_cents": row.get("price_cents"),
            "prior_price_cents": row.get("prior_price_cents"),
            "primary_authority": str(row.get("primary_authority") or ""),
            "reason": str(row.get("reason") or ""),
            "composed_macro_micro": bool(row.get("composed_macro_micro")),
            "book_receipt": causal.get("book_receipt"),
            "nonself_best_bid_cents": causal.get("nonself_best_bid_cents"),
            "nonself_best_ask_cents": causal.get("nonself_best_ask_cents"),
            "last_trade_cents": causal.get("last_trade_cents"),
            "flow": {
                "verdict": flow.get("verdict"),
                "flow_bucket": flow.get("flow_bucket"),
                "flow_ratio": flow.get("flow_ratio"),
                "unique_positive_print_count_30m":
                    flow.get("unique_positive_print_count_30m"),
                "executed_share_volume_30m":
                    flow.get("executed_share_volume_30m"),
                "inter_print_cadence_seconds":
                    flow.get("inter_print_cadence_seconds"),
                "verified_print_trailing_signature":
                    flow.get("verified_print_trailing_signature"),
                "spread_cents": flow.get("spread_cents"),
                "bid_depth_within_three_cents":
                    flow.get("bid_depth_within_three_cents"),
                "depth_trend": flow.get("depth_trend"),
            },
            "macro": {
                "status": macro.get("status"),
                "page_key": macro.get("page_key"),
                "target_raw_cents": macro.get("target_raw_cents"),
                "target_source": macro.get("target_source"),
            },
        })
    for rows in output.values():
        rows.sort(key=lambda row: (
            row["timestamp"], row["action"], str(row["price_cents"])
        ))
    return output


def _load_results(repo: Path) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str, str], dict[str, Any]],
]:
    events: dict[tuple[str, str], dict[str, Any]] = {}
    legs: dict[tuple[str, str, str], dict[str, Any]] = {}
    for candidate, relative in RESULT_LEDGER_BY_CANDIDATE.items():
        rows = read_jsonl(repo / relative)
        if len(rows) != 804:
            raise CensusError("latest result ledger is not D=804")
        for row in rows:
            if str(row["candidate_id"]) != candidate:
                raise CensusError("result candidate identity mismatch")
            event_id = str(row["event_id"])
            events[(candidate, event_id)] = {
                "classification": str(row["classification"]),
                "event_date": str(row["event_date"]),
                "category": str(row["category"]),
                "boundary_status": str(row["boundary_status"]),
            }
            for leg in row["legs"]:
                legs[(candidate, event_id, str(leg["leg_id"]))] = {
                    "policy_credited_fill": bool(leg["fillable"]),
                    "fill_price_cents": leg.get("accounting_fill_price_cents"),
                    "fill_timestamp": leg.get("evidence_timestamp"),
                    "fill_receipt": leg.get("evidence_receipt"),
                    "fill_evidence_type": leg.get("evidence_type"),
                }
    if len(events) != 1608 or len(legs) != 3216:
        raise CensusError("latest result identities do not conserve")
    return events, legs


def _policy_fact(
    *,
    candidate: str,
    event_id: str,
    leg_id: str,
    x_fact: Mapping[str, Any],
    stream: Mapping[str, Any],
    actions: list[Mapping[str, Any]],
    result_leg: Mapping[str, Any],
) -> dict[str, Any]:
    price = int(x_fact["price_cents"])
    observation_ts = x_fact.get("first_observation_timestamp")
    intervals = [
        row for row in stream["intervals_by_leg"].get(leg_id, [])
        if int(row["limit_price_cents"]) == price
    ]
    active = []
    if observation_ts is not None:
        active = [
            row for row in intervals
            if float(row["opened_ts"]) <= float(observation_ts)
            <= float(row.get("closed_ts") or float("inf"))
        ]
    moved = bool(
        observation_ts is not None
        and intervals
        and not active
        and any(
            float(row.get("closed_ts") or float("inf"))
            < float(observation_ts) for row in intervals
        )
    )
    action = (
        _latest_before(actions, float(observation_ts), "timestamp")
        if observation_ts is not None else None
    )
    evidence = stream["evidence_by_leg"].get(leg_id) or {}
    credited = bool(
        result_leg["policy_credited_fill"]
        and result_leg["fill_price_cents"] == price
    )
    micro_class = (
        "BOUND"
        if candidate == CANDIDATES[1]
        else "PROXIED_NOT_CONSUMED_BY_CANDIDATE"
    )
    return {
        "schema_version": VERSION + "-candidate-policy-at-x-v1",
        "candidate_id": candidate,
        "event_id": event_id,
        "event_date": str(x_fact["event_date"]),
        "category": str(x_fact["category"]),
        "orientation_id": f"{leg_id}__then__{x_fact['sibling_leg_id']}",
        "leg_id": leg_id,
        "ticker": str(x_fact["ticker"]),
        "price_cents": price,
        "x_evidence_id": str(x_fact["x_evidence_id"]),
        "policy_exposed_at_X": bool(active),
        "policy_ever_exposed_X": bool(intervals),
        "policy_moved_away_before_observation": moved,
        "active_order_interval_ids": sorted(
            str(row["order_interval_id"]) for row in active
        ),
        "all_order_interval_ids_at_X": sorted(
            str(row["order_interval_id"]) for row in intervals
        ),
        "policy_credited_fill": credited,
        "policy_credit_receipt": (
            result_leg["fill_receipt"] if credited else None
        ),
        "policy_credit_timestamp": (
            result_leg["fill_timestamp"] if credited else None
        ),
        "policy_credit_evidence_type": (
            result_leg["fill_evidence_type"] if credited else None
        ),
        "current_policy_action": (
            {
                "action": action["action"],
                "price_cents": action["price_cents"],
                "prior_price_cents": action["prior_price_cents"],
                "primary_authority": action["primary_authority"],
                "reason": action["reason"],
                "timestamp": action["timestamp"],
                "book_receipt": action["book_receipt"],
            } if action is not None else None
        ),
        "macro_category_cell_range_regime": {
            "discovery_page_key": evidence.get("discovery_page_key"),
            "discovery_status": evidence.get("discovery_status"),
            "macro_target_raw": evidence.get("macro_target_raw"),
            "macro_target_source": evidence.get("macro_target_source"),
            "macro_target_status": evidence.get("macro_target_status"),
        },
        "micro_LIVE_AIM_state": {
            "classification": micro_class,
            "state": action["flow"] if action is not None else None,
            "last_trade_state_is_PROXIED": True,
            "top5_pressure_sign_is_PROXIED": True,
            "sibling_flow_is_PROXIED": True,
        },
        "D_member": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def _build_x_fact(
    *,
    ladder: Mapping[str, Any],
    price_row: Mapping[str, Any],
    sibling_leg_id: str,
    prepared_prints: list[Mapping[str, Any]],
    prepared_snapshots: list[Mapping[str, Any]],
) -> dict[str, Any]:
    event_id = str(ladder["event_id"])
    leg_id = str(ladder["leg_id"])
    price = exact_cent(price_row["price_cents"], "ladder price")
    observation = first_lawful_observation(price_row)
    prints = prepared_prints
    snapshots = prepared_snapshots
    observation_ts = observation["timestamp"] if observation else None
    context = (
        _book_context(snapshots, prints, observation_ts, price)
        if observation_ts is not None else {
            "available": False,
            "reason": "no_PRICE_AT_X_or_STRICT_ASK_observation",
            "timestamp": None,
            "nonself_best_bid_cents": None,
            "nonself_best_ask_cents": None,
            "spread_cents": None,
            "top5_bids": [],
            "top5_asks": [],
            "displayed_depth_at_or_ahead_of_X": None,
            "last_trade_cents": None,
            "last_trade_execution_at": None,
            "last_trade_provenance": None,
        }
    )
    after_volume = (
        sum(
            float(row["size"]) for row in prints
            if observation_ts <= float(row["ts"])
            <= float(ladder["range_right_ts"])
            and int(row["price"]) <= price
        )
        if observation_ts is not None else 0.0
    )
    flow = (
        _rolling_flow(prints, observation_ts)
        if observation_ts is not None else {
            "print_count_5m": 0,
            "executed_volume_5m": 0.0,
            "print_count_15m": 0,
            "executed_volume_15m": 0.0,
            "print_count_30m": 0,
            "executed_volume_30m": 0.0,
            "inter_print_cadence_seconds_30m": None,
            "trailing_price_signature_30m": "flat",
        }
    )
    price_reached = isinstance(
        price_row.get("first_true_print_at_or_below"), Mapping
    )
    strict_ask = isinstance(
        price_row.get("first_ask_strictly_below"), Mapping
    )
    evidence_id = canonical_sha256({
        "event_id": event_id,
        "leg_id": leg_id,
        "price_cents": price,
        "first_observation": observation,
    })
    return {
        "schema_version": VERSION + "-x-evidence-v1",
        "x_evidence_id": evidence_id,
        "event_id": event_id,
        "event_date": str(ladder["event_date"]),
        "category": str(ladder["category"]),
        "leg_id": leg_id,
        "sibling_leg_id": sibling_leg_id,
        "ticker": str(ladder["ticker"]),
        "price_cents": price,
        "boundary": ladder["boundary"],
        "policy_left_ts": float(ladder["policy_left_ts"]),
        "window1_right_ts": float(ladder["range_right_ts"]),
        "price_reached": price_reached,
        "price_reached_receipt": price_row.get(
            "first_true_print_at_or_below"
        ),
        "strict_ask_certain_fill": strict_ask,
        "strict_ask_receipt": price_row.get("first_ask_strictly_below"),
        "first_observation_type": (
            observation["evidence_type"] if observation else None
        ),
        "first_observation_timestamp": observation_ts,
        "first_observation_receipt": (
            observation["receipt"] if observation else None
        ),
        "first_observation_true_print_price_cents": (
            observation["price_cents"] if observation else None
        ),
        "first_observation_executed_size": (
            observation["executed_size"] if observation else None
        ),
        "executed_volume_at_or_better_through_window1": (
            float(price_row["executed_share_volume_at"])
            + float(price_row["executed_share_volume_below"])
        ),
        "executed_volume_at_or_better_after_first_observation":
            after_volume,
        "five_contract_capacity_proven": after_volume >= 5.0,
        "capacity_law": (
            "chronological positive executed volume at_or_below_X "
            "from first observation through guarded Window1 >=5"
        ),
        "price_reach_survives_capacity_unproved": (
            price_reached and after_volume < 5.0
        ),
        "book_and_chain_at_first_observation": context,
        "displayed_BBO_top5_depth": {
            "nonself_best_bid_cents":
                context["nonself_best_bid_cents"],
            "nonself_best_ask_cents":
                context["nonself_best_ask_cents"],
            "spread_cents": context["spread_cents"],
            "top5_bids": context["top5_bids"],
            "top5_asks": context["top5_asks"],
            "depth_at_or_ahead_of_X":
                context["displayed_depth_at_or_ahead_of_X"],
            "depth_is_primary_price_reach_gate": False,
        },
        "last_traded_state": {
            "last_trade_cents": context["last_trade_cents"],
            "last_trade_execution_at": context["last_trade_execution_at"],
            "last_trade_provenance": context["last_trade_provenance"],
            "last_trade_is_BBO_authority": False,
            "last_trade_is_fill_volume": False,
        },
        "rolling_executed_volume_and_cadence": flow,
        "price_residency": {
            "ask_at_or_below_X_seconds":
                float(price_row["ask_residency_at_or_below_seconds"]),
            "first_true_print_ts": (
                price_row["first_true_print_at_or_below"]["ts"]
                if price_reached else None
            ),
            "last_true_print_ts": (
                price_row["last_true_print_at_or_below"]["ts"]
                if price_row.get("last_true_print_at_or_below") else None
            ),
        },
        "executed_volume_band": volume_band(after_volume),
        "cadence_band": cadence_band(
            int(flow["print_count_30m"]),
            flow["inter_print_cadence_seconds_30m"],
        ),
        "displayed_depth_band": depth_band(
            context["displayed_depth_at_or_ahead_of_X"]
        ),
        "spread_band": spread_band(context["spread_cents"]),
        "true_print_and_BBO_are_distinct_authorities": True,
        "D_member": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def _writers(
    output: Path,
    prefix: str,
) -> list[DeterministicGzipJsonlWriter]:
    return [
        DeterministicGzipJsonlWriter(
            output / f"{prefix}_{part:02d}.jsonl.gz"
        )
        for part in range(1, 5)
    ]


def _close_writers(
    writers: Iterable[DeterministicGzipJsonlWriter],
) -> None:
    for writer in writers:
        writer.close()


def _add_breakdown(
    table: MutableMapping[tuple[Any, ...], Counter],
    key: tuple[Any, ...],
    row: Mapping[str, Any],
) -> None:
    counter = table[key]
    counter["rows"] += 1
    counter[f"terminal::{row['terminal_classification']}"] += 1
    counter["price_reached"] += int(bool(row["later_price_reached_count"]))
    counter["capacity_proven"] += int(
        bool(row["later_capacity_proven_count"])
    )
    counter["policy_exposed"] += int(
        bool(row["later_policy_exposed_count"])
    )
    counter["policy_credited"] += int(
        bool(row["later_policy_credited_count"])
    )


def _breakdown_rows(
    table: Mapping[tuple[Any, ...], Counter],
    fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    output = []
    for key in sorted(table, key=lambda value: tuple(str(x) for x in value)):
        counter = table[key]
        output.append({
            **dict(zip(fields, key)),
            "row_count": counter["rows"],
            "price_reached_rows": counter["price_reached"],
            "capacity_proven_rows": counter["capacity_proven"],
            "policy_exposed_rows": counter["policy_exposed"],
            "policy_credited_rows": counter["policy_credited"],
            "terminal_classifications": {
                name: counter[f"terminal::{name}"]
                for name in TERMINAL_CLASSES
            },
        })
    return output


def build(repo: Path, output: Path) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise CensusError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    head = git(repo, "rev-parse", "HEAD")
    if head != PARENT and git(repo, "rev-parse", "HEAD^") != PARENT:
        raise CensusError("census must build from parent or its sole child")
    if git(repo, "rev-parse", "origin/codex/window1-definition") != PARENT:
        if head == PARENT:
            raise CensusError("remote branch is not the required parent")
    for commit in (
        CONTROLLING_AUDIT,
        STRICT_ASK_IMPLEMENTATION,
        STRICT_ASK_PASS,
        STRICT_ASK_DETERMINISM,
    ):
        git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    mechanism = read_json(repo / MECHANISM_REL)
    if mechanism["classification_totals"] != {
        "ABSENT": 4, "BOUND": 9, "PROXIED": 10, "RETRACTED": 5
    }:
        raise CensusError("mechanism recovery table changed")
    streams = _load_stream_summaries(repo)
    actions = _load_actions(repo)
    result_events, result_legs = _load_results(repo)

    ladder_by_event: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for relative in LADDER_RELS:
        for row in iter_gzip_jsonl(repo / relative):
            event_date = str(row["event_date"])
            if event_date in SEALED_DATES or event_date not in DEVELOPMENT_DATES:
                raise CensusError("outside development date in range ladder")
            ladder_by_event[str(row["event_id"])][str(row["leg_id"])] = row
    if len(ladder_by_event) != 804 or sum(
        len(value) for value in ladder_by_event.values()
    ) != 1608:
        raise CensusError("range ladders do not conserve D/legs")

    x_writers = _writers(output, "FROZEN_X_EVIDENCE_LEDGER")
    policy_writers = _writers(output, "CANDIDATE_POLICY_AT_X_LEDGER")
    x_index: dict[tuple[str, str, int], dict[str, Any]] = {}
    policy_index: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    evidence_counts = Counter()
    policy_counts: dict[str, Counter] = {
        candidate: Counter() for candidate in CANDIDATES
    }
    for event_ordinal, event_id in enumerate(sorted(ladder_by_event)):
        shard = min(3, event_ordinal // 201)
        ladders = ladder_by_event[event_id]
        leg_ids = sorted(ladders)
        if len(leg_ids) != 2:
            raise CensusError("event lacks exactly two ladder legs")
        with gzip.open(
            repo / CACHE_REL / f"{event_id}.json.gz",
            "rt", encoding="utf-8",
        ) as handle:
            cache = json.load(handle)
        cache_legs = {
            str(row["leg"]): row for row in cache.get("legs") or []
        }
        for leg_id, sibling_id in orientation_ids(leg_ids):
            ladder = ladders[leg_id]
            cache_leg = cache_legs.get(leg_id)
            if not isinstance(cache_leg, Mapping):
                raise CensusError("guarded cache leg missing")
            prepared_prints = [
                row for row in cache_leg.get("prints") or []
                if float(row.get("size") or 0) > 0
                and float(ladder["policy_left_ts"]) <= float(row["ts"])
                <= float(ladder["range_right_ts"])
            ]
            prepared_prints.sort(key=lambda row: (
                float(row["ts"]), str(row.get("trade_id") or "")
            ))
            prepared_snapshots = [
                row for row in cache_leg.get("snapshots") or []
                if float(ladder["policy_left_ts"]) <= float(row["ts"])
                <= float(ladder["range_right_ts"])
            ]
            prepared_snapshots.sort(key=lambda row: float(row["ts"]))
            if len(ladder["integer_cent_price_rows"]) != 99:
                raise CensusError("frozen integer-cent ladder changed")
            for price_row in ladder["integer_cent_price_rows"]:
                x_fact = _build_x_fact(
                    ladder=ladder,
                    price_row=price_row,
                    sibling_leg_id=sibling_id,
                    prepared_prints=prepared_prints,
                    prepared_snapshots=prepared_snapshots,
                )
                x_writers[shard].write(x_fact)
                price = int(x_fact["price_cents"])
                x_index[(event_id, leg_id, price)] = {
                    "x_evidence_id": x_fact["x_evidence_id"],
                    "event_id": event_id,
                    "event_date": x_fact["event_date"],
                    "category": x_fact["category"],
                    "leg_id": leg_id,
                    "sibling_leg_id": sibling_id,
                    "ticker": x_fact["ticker"],
                    "price_cents": price,
                    "boundary_available": bool(
                        x_fact["boundary"].get("positive_window1_provable")
                    ),
                    "has_observation":
                        x_fact["first_observation_timestamp"] is not None,
                    "first_observation_timestamp":
                        x_fact["first_observation_timestamp"],
                    "first_observation_receipt":
                        x_fact["first_observation_receipt"],
                    "first_observation_type":
                        x_fact["first_observation_type"],
                    "price_reached": x_fact["price_reached"],
                    "strict_ask_certain_fill":
                        x_fact["strict_ask_certain_fill"],
                    "five_contract_capacity_proven":
                        x_fact["five_contract_capacity_proven"],
                    "executed_volume":
                        x_fact[
                            "executed_volume_at_or_better_after_first_observation"
                        ],
                    "bid": x_fact["displayed_BBO_top5_depth"][
                        "nonself_best_bid_cents"
                    ],
                    "ask": x_fact["displayed_BBO_top5_depth"][
                        "nonself_best_ask_cents"
                    ],
                    "spread": x_fact["displayed_BBO_top5_depth"][
                        "spread_cents"
                    ],
                    "volume_band": x_fact["executed_volume_band"],
                    "cadence_band": x_fact["cadence_band"],
                    "depth_band": x_fact["displayed_depth_band"],
                    "spread_band": x_fact["spread_band"],
                }
                evidence_counts["rows"] += 1
                evidence_counts["price_reached"] += int(x_fact["price_reached"])
                evidence_counts["strict_ask"] += int(
                    x_fact["strict_ask_certain_fill"]
                )
                evidence_counts["capacity_proven"] += int(
                    x_fact["five_contract_capacity_proven"]
                )
                evidence_counts["price_reached_capacity_unproved"] += int(
                    x_fact["price_reach_survives_capacity_unproved"]
                )
                for candidate in CANDIDATES:
                    stream = streams[(candidate, event_id)]
                    policy = _policy_fact(
                        candidate=candidate,
                        event_id=event_id,
                        leg_id=leg_id,
                        x_fact=x_fact,
                        stream=stream,
                        actions=actions.get(
                            (candidate, event_id, leg_id), []
                        ),
                        result_leg=result_legs[
                            (candidate, event_id, leg_id)
                        ],
                    )
                    policy_writers[shard].write(policy)
                    policy_index[(candidate, event_id, leg_id, price)] = {
                        "policy_exposed_at_X":
                            policy["policy_exposed_at_X"],
                        "policy_ever_exposed_X":
                            policy["policy_ever_exposed_X"],
                        "policy_moved_away_before_observation":
                            policy[
                                "policy_moved_away_before_observation"
                            ],
                        "policy_credited_fill":
                            policy["policy_credited_fill"],
                        "policy_credit_timestamp":
                            policy["policy_credit_timestamp"],
                        "macro_regime":
                            policy["macro_category_cell_range_regime"][
                                "discovery_page_key"
                            ] or "NO_CALL",
                        "action_state": (
                            policy["current_policy_action"]["action"]
                            if policy["current_policy_action"] else "NO_ACTION"
                        ),
                    }
                    policy_counts[candidate]["rows"] += 1
                    policy_counts[candidate]["exposed"] += int(
                        policy["policy_exposed_at_X"]
                    )
                    policy_counts[candidate]["ever_exposed"] += int(
                        policy["policy_ever_exposed_X"]
                    )
                    policy_counts[candidate]["credited"] += int(
                        policy["policy_credited_fill"]
                    )
    _close_writers(x_writers)
    _close_writers(policy_writers)
    if evidence_counts["rows"] != 1608 * 99:
        raise CensusError("X evidence ledger does not conserve 1,608x99")
    if any(
        value["rows"] != 1608 * 99
        for value in policy_counts.values()
    ):
        raise CensusError("candidate policy X ledgers do not conserve")

    orientation_writers = _writers(
        output, "ASYNCHRONOUS_ORIENTATION_X_CENSUS"
    )
    summary_writers = _writers(
        output, "ASYNCHRONOUS_ORIENTATION_EVENT_SUMMARY"
    )
    orientation_counts: dict[str, Counter] = {
        candidate: Counter() for candidate in CANDIDATES
    }
    event_summary_counts: dict[str, Counter] = {
        candidate: Counter() for candidate in CANDIDATES
    }
    decisive: dict[str, Counter] = {
        candidate: Counter() for candidate in CANDIDATES
    }
    breakdowns: dict[str, defaultdict[tuple[Any, ...], Counter]] = {
        name: defaultdict(Counter)
        for name in (
            "candidate", "date", "category", "macro_regime",
            "orientation", "elapsed", "volume_cadence",
            "depth_spread", "policy_action_state",
        )
    }
    event_summaries: list[dict[str, Any]] = []
    for event_ordinal, event_id in enumerate(sorted(ladder_by_event)):
        shard = min(3, event_ordinal // 201)
        leg_ids = sorted(ladder_by_event[event_id])
        for candidate in CANDIDATES:
            result = result_events[(candidate, event_id)]
            for first_leg, sibling_leg in orientation_ids(leg_ids):
                first_facts = [
                    x_index[(event_id, first_leg, price)]
                    for price in range(1, 100)
                    if x_index[(event_id, first_leg, price)]["has_observation"]
                ]
                detail_rows: list[dict[str, Any]] = []
                for first in first_facts:
                    first_price = int(first["price_cents"])
                    first_policy = policy_index[
                        (candidate, event_id, first_leg, first_price)
                    ]
                    bid = first["bid"]
                    d1 = first_price - int(bid) if bid is not None else None
                    maximum = headroom_d2_max(d1, 0.0) if d1 is not None else None
                    later: list[dict[str, Any]] = []
                    if d1 is not None:
                        for sibling_price in range(1, 100):
                            fact = x_index[
                                (event_id, sibling_leg, sibling_price)
                            ]
                            if (
                                not fact["has_observation"]
                                or not strictly_later(
                                    float(first["first_observation_timestamp"]),
                                    float(fact["first_observation_timestamp"]),
                                )
                                or fact["bid"] is None
                            ):
                                continue
                            d2 = sibling_price - int(fact["bid"])
                            if (
                                d2 <= maximum
                                and strict_combined_budget(d1, d2, 0.0)
                            ):
                                policy = policy_index[
                                    (
                                        candidate, event_id,
                                        sibling_leg, sibling_price,
                                    )
                                ]
                                later.append({
                                    "x_evidence_id": fact["x_evidence_id"],
                                    "price_cents": sibling_price,
                                    "first_observation_timestamp":
                                        fact["first_observation_timestamp"],
                                    "first_observation_receipt":
                                        fact["first_observation_receipt"],
                                    "first_observation_type":
                                        fact["first_observation_type"],
                                    "d2_cents": d2,
                                    "price_reached": fact["price_reached"],
                                    "strict_ask_certain_fill":
                                        fact["strict_ask_certain_fill"],
                                    "five_contract_capacity_proven":
                                        fact[
                                            "five_contract_capacity_proven"
                                        ],
                                    "policy_exposed_at_X":
                                        policy["policy_exposed_at_X"],
                                    "policy_ever_exposed_X":
                                        policy["policy_ever_exposed_X"],
                                    "policy_moved_away_before_observation":
                                        policy[
                                            "policy_moved_away_before_observation"
                                        ],
                                    "policy_credited_fill":
                                        policy["policy_credited_fill"],
                                    "executed_volume_at_or_better":
                                        fact["executed_volume"],
                                    "nonself_best_bid_cents": fact["bid"],
                                    "nonself_best_ask_cents": fact["ask"],
                                    "spread_cents": fact["spread"],
                                    "executed_volume_band":
                                        fact["volume_band"],
                                    "cadence_band": fact["cadence_band"],
                                    "displayed_depth_band":
                                        fact["depth_band"],
                                    "spread_band": fact["spread_band"],
                                    "policy_action_state":
                                        policy["action_state"],
                                })
                    first_credit = result_legs[
                        (candidate, event_id, first_leg)
                    ]
                    sibling_credit = result_legs[
                        (candidate, event_id, sibling_leg)
                    ]
                    completed = bool(
                        first_credit["policy_credited_fill"]
                        and sibling_credit["policy_credited_fill"]
                        and first_credit["fill_price_cents"] == first_price
                        and first_credit["fill_timestamp"] is not None
                        and sibling_credit["fill_timestamp"] is not None
                        and strictly_later(
                            float(first_credit["fill_timestamp"]),
                            float(sibling_credit["fill_timestamp"]),
                        )
                    )
                    potential_without_evidence = 0
                    if d1 is not None:
                        for sibling_price in range(1, 100):
                            fact = x_index[
                                (event_id, sibling_leg, sibling_price)
                            ]
                            policy = policy_index[
                                (
                                    candidate, event_id,
                                    sibling_leg, sibling_price,
                                )
                            ]
                            if (
                                not fact["has_observation"]
                                and policy["policy_ever_exposed_X"]
                            ):
                                potential_without_evidence += 1
                    terminal, reason = classify_orientation(
                        boundary_available=bool(first["boundary_available"]),
                        d1_available=d1 is not None,
                        completed_by_policy=completed,
                        later_opportunities=later,
                        potential_exposures_without_evidence=
                            potential_without_evidence,
                    )
                    earliest = min(
                        later,
                        key=lambda row: (
                            row["first_observation_timestamp"],
                            row["price_cents"],
                        ),
                        default=None,
                    )
                    detail = {
                        "schema_version":
                            VERSION + "-orientation-x-census-v1",
                        "candidate_id": candidate,
                        "event_id": event_id,
                        "event_date": result["event_date"],
                        "category": result["category"],
                        "orientation_id":
                            f"{first_leg}__then__{sibling_leg}",
                        "first_leg_id": first_leg,
                        "sibling_leg_id": sibling_leg,
                        "first_leg_X_cents": first_price,
                        "first_leg_x_evidence_id":
                            first["x_evidence_id"],
                        "first_leg_opportunity_timestamp":
                            first["first_observation_timestamp"],
                        "first_leg_opportunity_receipt":
                            first["first_observation_receipt"],
                        "first_leg_opportunity_type":
                            first["first_observation_type"],
                        "first_leg_external_bid_cents": bid,
                        "causal_d1_cents": d1,
                        "frozen_fee_cents": 0,
                        "d2_max_cents": maximum,
                        "strictly_later_sibling_evidence_required": True,
                        "same_timestamp_sibling_evidence_accepted": False,
                        "later_in_budget_opportunity_count": len(later),
                        "later_in_budget_opportunity_ids": [
                            row["x_evidence_id"] for row in later
                        ],
                        "later_in_budget_prices_cents": [
                            row["price_cents"] for row in later
                        ],
                        "later_in_budget_opportunities": later,
                        "later_price_reached_count": sum(
                            row["price_reached"] for row in later
                        ),
                        "later_strict_ask_count": sum(
                            row["strict_ask_certain_fill"] for row in later
                        ),
                        "later_capacity_proven_count": sum(
                            row["five_contract_capacity_proven"]
                            for row in later
                        ),
                        "later_policy_exposed_count": sum(
                            row["policy_exposed_at_X"] for row in later
                        ),
                        "later_policy_credited_count": sum(
                            row["policy_credited_fill"] for row in later
                        ),
                        "potential_policy_exposures_without_evidence":
                            potential_without_evidence,
                        "first_policy_exposed_at_X":
                            first_policy["policy_exposed_at_X"],
                        "first_policy_credited_fill":
                            first_policy["policy_credited_fill"],
                        "macro_category_cell_range_regime":
                            first_policy["macro_regime"],
                        "earliest_later_opportunity": earliest,
                        "elapsed_after_first_seconds": (
                            float(earliest["first_observation_timestamp"])
                            - float(first["first_observation_timestamp"])
                            if earliest else None
                        ),
                        "elapsed_band": elapsed_band(
                            (
                                float(earliest[
                                    "first_observation_timestamp"
                                ])
                                - float(first[
                                    "first_observation_timestamp"
                                ])
                            ) if earliest else None
                        ),
                        "terminal_classification": terminal,
                        "terminal_reason": reason,
                        "latest_policy_result_classification":
                            result["classification"],
                        "PC_is_combined_negative_and_IC_is_not_a_gate": True,
                        "D_member": True,
                        "metrics": None,
                        "performance": None,
                        "scored": False,
                    }
                    orientation_writers[shard].write(detail)
                    detail_rows.append(detail)
                    orientation_counts[candidate]["rows"] += 1
                    orientation_counts[candidate][terminal] += 1
                    _add_breakdown(
                        breakdowns["candidate"], (candidate,), detail
                    )
                    _add_breakdown(
                        breakdowns["date"],
                        (candidate, result["event_date"]), detail,
                    )
                    _add_breakdown(
                        breakdowns["category"],
                        (candidate, result["category"]), detail,
                    )
                    _add_breakdown(
                        breakdowns["macro_regime"],
                        (
                            candidate,
                            detail["macro_category_cell_range_regime"],
                        ),
                        detail,
                    )
                    _add_breakdown(
                        breakdowns["orientation"],
                        (
                            candidate,
                            detail["orientation_id"],
                        ),
                        detail,
                    )
                    _add_breakdown(
                        breakdowns["elapsed"],
                        (candidate, detail["elapsed_band"]), detail,
                    )
                    _add_breakdown(
                        breakdowns["volume_cadence"],
                        (
                            candidate,
                            earliest["executed_volume_band"]
                            if earliest else "NO_LATER_OPPORTUNITY",
                            earliest["cadence_band"]
                            if earliest else "NO_LATER_OPPORTUNITY",
                        ),
                        detail,
                    )
                    _add_breakdown(
                        breakdowns["depth_spread"],
                        (
                            candidate,
                            earliest["displayed_depth_band"]
                            if earliest else "NO_LATER_OPPORTUNITY",
                            earliest["spread_band"]
                            if earliest else "NO_LATER_OPPORTUNITY",
                        ),
                        detail,
                    )
                    _add_breakdown(
                        breakdowns["policy_action_state"],
                        (
                            candidate,
                            earliest["policy_action_state"]
                            if earliest else "NO_LATER_OPPORTUNITY",
                        ),
                        detail,
                    )
                if detail_rows:
                    selected_terminal = min(
                        (
                            row["terminal_classification"]
                            for row in detail_rows
                        ),
                        key=lambda name: TERMINAL_PRIORITY[name],
                    )
                    witnesses = [
                        row for row in detail_rows
                        if row["terminal_classification"] == selected_terminal
                    ]
                    reason = Counter(
                        row["terminal_reason"] for row in witnesses
                    ).most_common(1)[0][0]
                else:
                    positive = bool(
                        ladder_by_event[event_id][first_leg]["boundary"].get(
                            "positive_window1_provable"
                        )
                    )
                    selected_terminal = (
                        "no_lawful_in_budget_later_sibling_opportunity_observed"
                        if positive else "evidence_unavailable"
                    )
                    reason = (
                        "no_first_leg_price_or_strict_ask_opportunity"
                        if positive else "boundary_not_positive_provable"
                    )
                    witnesses = []
                summary = {
                    "schema_version":
                        VERSION + "-orientation-event-summary-v1",
                    "candidate_id": candidate,
                    "event_id": event_id,
                    "event_date": result["event_date"],
                    "category": result["category"],
                    "orientation_id": f"{first_leg}__then__{sibling_leg}",
                    "first_leg_id": first_leg,
                    "sibling_leg_id": sibling_leg,
                    "first_leg_opportunity_X_count": len(detail_rows),
                    "terminal_classification": selected_terminal,
                    "terminal_reason": reason,
                    "terminal_witness_first_X_cents": [
                        row["first_leg_X_cents"] for row in witnesses
                    ],
                    "terminal_witness_orientation_X_receipts": [
                        canonical_sha256({
                            "candidate": candidate,
                            "event": event_id,
                            "orientation": row["orientation_id"],
                            "first_X": row["first_leg_X_cents"],
                            "evidence": row["first_leg_x_evidence_id"],
                        })
                        for row in witnesses
                    ],
                    "latest_policy_result_classification":
                        result["classification"],
                    "D_member": True,
                    "metrics": None,
                    "performance": None,
                    "scored": False,
                }
                summary_writers[shard].write(summary)
                event_summaries.append(summary)
                event_summary_counts[candidate]["rows"] += 1
                event_summary_counts[candidate][selected_terminal] += 1
                if result["classification"] in {"naked_single", "no_fill"}:
                    prevention = {
                        "completed_by_policy": "completed_by_policy",
                        "lawful_in_budget_opportunity_policy_never_exposed":
                            (
                                "moved_away"
                                if reason
                                == "policy_moved_away_before_observation"
                                else "no_exposure"
                            ),
                        "policy_exposed_execution_or_strict_ask_proved_not_credited":
                            "execution_proved_but_uncredited",
                        "policy_exposed_without_execution_proof":
                            "policy_exposed_without_execution_proof",
                        "price_reached_five_contract_capacity_unproved":
                            "capacity_unproved",
                        "evidence_unavailable": "evidence_absent",
                        "no_lawful_in_budget_later_sibling_opportunity_observed":
                            "genuinely_no_observed_later_opportunity",
                    }[selected_terminal]
                    decisive[candidate][(
                        result["classification"],
                        summary["orientation_id"],
                        prevention,
                    )] += 1
    _close_writers(orientation_writers)
    _close_writers(summary_writers)
    if any(
        value["rows"] != 1608 for value in event_summary_counts.values()
    ):
        raise CensusError("both orientations are not retained for D=804")

    decisive_rows = []
    for candidate in CANDIDATES:
        for (result_class, orientation, prevention), count in sorted(
            decisive[candidate].items()
        ):
            decisive_rows.append({
                "candidate_id": candidate,
                "latest_policy_result_classification": result_class,
                "first_leg_orientation": orientation,
                "prevention": prevention,
                "event_orientation_count": count,
            })
    write_json(output / "DECISIVE_NAKED_SINGLE_NO_CREDIT_TABLE.json", {
        "schema_version": VERSION + "-decisive-table-v1",
        "scope": ["naked_single", "no_fill"],
        "orientations_retained_per_event": 2,
        "rows": decisive_rows,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    breakdown_output = {
        "schema_version": VERSION + "-breakdowns-v1",
        "by_candidate": _breakdown_rows(
            breakdowns["candidate"], ("candidate_id",)
        ),
        "by_date": _breakdown_rows(
            breakdowns["date"], ("candidate_id", "event_date")
        ),
        "by_category": _breakdown_rows(
            breakdowns["category"], ("candidate_id", "category")
        ),
        "by_category_native_cell_range_regime": _breakdown_rows(
            breakdowns["macro_regime"],
            ("candidate_id", "macro_regime"),
        ),
        "by_first_leg_orientation": _breakdown_rows(
            breakdowns["orientation"],
            ("candidate_id", "orientation_id"),
        ),
        "by_elapsed_time_after_first_opportunity": _breakdown_rows(
            breakdowns["elapsed"],
            ("candidate_id", "elapsed_band"),
        ),
        "by_executed_volume_cadence_band": _breakdown_rows(
            breakdowns["volume_cadence"],
            ("candidate_id", "executed_volume_band", "cadence_band"),
        ),
        "by_displayed_depth_spread_band": _breakdown_rows(
            breakdowns["depth_spread"],
            ("candidate_id", "displayed_depth_band", "spread_band"),
        ),
        "by_policy_action_state": _breakdown_rows(
            breakdowns["policy_action_state"],
            ("candidate_id", "policy_action_state"),
        ),
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "BREAKDOWN_TABLES.json", breakdown_output)
    raw = {
        "schema_version": VERSION + "-raw-diagnostic-census-v1",
        "immutable_population_events_per_candidate": 804,
        "candidate_count": 2,
        "leg_identities": 1608,
        "integer_cent_levels_per_leg": 99,
        "x_evidence": dict(sorted(evidence_counts.items())),
        "candidate_policy_at_x": {
            candidate: dict(sorted(policy_counts[candidate].items()))
            for candidate in CANDIDATES
        },
        "orientation_x": {
            candidate: dict(sorted(orientation_counts[candidate].items()))
            for candidate in CANDIDATES
        },
        "orientation_event_summaries": {
            candidate: dict(
                sorted(event_summary_counts[candidate].items())
            )
            for candidate in CANDIDATES
        },
        "simultaneous_pair_evidence_required": False,
        "individual_negative_gate": False,
        "cumulative_five_gate_on_price_reach": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "RAW_DIAGNOSTIC_CENSUS.json", raw)
    conservation = {
        "schema_version": VERSION + "-conservation-v1",
        "immutable_population_events_per_candidate": 804,
        "candidate_rows": [
            {
                "candidate_id": candidate,
                "unique_event_identities": len({
                    row["event_id"] for row in event_summaries
                    if row["candidate_id"] == candidate
                }),
                "orientation_event_rows":
                    event_summary_counts[candidate]["rows"],
                "required_orientation_event_rows": 1608,
                "both_orientations_retained": (
                    event_summary_counts[candidate]["rows"] == 1608
                ),
                "terminal_classification_total": sum(
                    event_summary_counts[candidate][name]
                    for name in TERMINAL_CLASSES
                ),
            }
            for candidate in CANDIDATES
        ],
        "D_membership_changed": False,
        "benchmark_metrics_computed": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "CONSERVATION_PROOF.json", conservation)

    source_manifest = {
        "schema_version": VERSION + "-source-hash-manifest-v1",
        "implementation_parent": PARENT,
        "controlling_audit": commit_blob(
            repo, CONTROLLING_AUDIT, AUDIT_REPORT_REL
        ),
        "controlling_audit_receipts": commit_blob(
            repo, CONTROLLING_AUDIT, AUDIT_RECEIPTS_REL
        ),
        "strict_ask_lineage": {
            "implementation": STRICT_ASK_IMPLEMENTATION,
            "independent_PASS": STRICT_ASK_PASS,
            "determinism_addendum": STRICT_ASK_DETERMINISM,
        },
        "committed_sources": [
            source_row(repo, relative) for relative in SOURCE_RELS
        ],
        "private_development_cache": {
            "path": CACHE_REL,
            "receipt_source": DATA_MANIFEST_REL,
            "events": 804,
            "tickers": 1608,
            "holdout_dates_present": 0,
            "runtime_network_access": False,
        },
        "holdout_inputs": 0,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)
    no_access = {
        "schema_version": VERSION + "-forbidden-access-v1",
        "scorer_imports": 0,
        "scorer_invocations": 0,
        "benchmark_executions": 0,
        "candidate_ids_added": 0,
        "strategy_parameters_added": 0,
        "policy_actions_created": 0,
        "holdout_access": False,
        "live_access": False,
        "production_access": False,
        "network_calls": 0,
        "Window2_access": False,
        "exit_settlement_DCA_access": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "FORBIDDEN_ACCESS_NO_SCORER_RECEIPT.json", no_access)
    report = f"""# Window-1 asynchronous opportunity-vs-policy census

This score-free additions-only census reconciles the frozen Range-Attack V2
integer-cent ladders, public print/BBO evidence, policy intervals, guarded
credited fills, asynchronous headroom, and audited result classifications.

It retains both first-leg orientations and separates price reach, strict-ask
certain evidence, five-contract capacity proof, policy exposure, and policy
credit.  A price reached on sub-five executed volume remains price reached.
Positive sibling delta is lawful whenever the strict combined budget permits.

The immutable population remains 804 events per candidate.  Every benchmark
metric and performance field is null.  No scorer, benchmark, tuning, ranking,
holdout, live, production, Window 2, exit, settlement, or DCA surface ran.

Controlling result audit: `{CONTROLLING_AUDIT}`.
"""
    (output / "CENSUS_REPORT.md").write_bytes(report.encode("utf-8"))
    return {
        "schema_version": VERSION + "-build-receipt-v1",
        "output": str(output),
        "files": sorted(
            path.name for path in output.iterdir() if path.is_file()
        ),
        "raw_diagnostic_sha256": canonical_sha256(raw),
        "decisive_rows": len(decisive_rows),
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.iterdir())
        if path.is_file()
    ]


def freeze(repo: Path) -> dict[str, Any]:
    target = repo / PACKAGE_REL
    if target.exists():
        raise CensusError("frozen census target already exists")
    with tempfile.TemporaryDirectory(
        prefix="w1-async-opportunity-census-"
    ) as temp_value:
        temp = Path(temp_value)
        first = temp / "build_a"
        second = temp / "build_b"
        build(repo, first)
        build(repo, second)
        first_inventory = inventory(first)
        second_inventory = inventory(second)
        if first_inventory != second_inventory:
            raise CensusError("fresh deterministic builds differ")
        shutil.copytree(first, target)
    regeneration = {
        "schema_version": VERSION + "-deterministic-regeneration-v1",
        "fresh_builds": 2,
        "byte_identical": True,
        "artifact_inventory": first_inventory,
        "scorer_imports": 0,
        "scorer_invocations": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(target / "DETERMINISTIC_REGENERATION_RECEIPT.json",
               regeneration)
    artifacts = []
    for path in sorted(target.iterdir()):
        if not path.is_file() or path.name == "ARTIFACT_HASH_MANIFEST.json":
            continue
        raw = path.read_bytes()
        artifacts.append({
            "path": f"{PACKAGE_REL}/{path.name}",
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git_blob_oid(raw),
        })
    artifact_manifest = {
        "schema_version": VERSION + "-artifact-hash-manifest-v1",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(target / "ARTIFACT_HASH_MANIFEST.json", artifact_manifest)
    return {
        "target": str(target),
        "artifact_count": len(artifacts) + 1,
        "deterministic_regeneration": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--mode", choices=("build", "freeze"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.mode == "freeze":
        if args.output is not None:
            raise CensusError("--output is forbidden in freeze mode")
        result = freeze(repo)
    else:
        if args.output is None:
            raise CensusError("--output is required in build mode")
        output = (
            args.output.resolve()
            if args.output.is_absolute()
            else (repo / args.output).resolve()
        )
        result = build(repo, output)
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
