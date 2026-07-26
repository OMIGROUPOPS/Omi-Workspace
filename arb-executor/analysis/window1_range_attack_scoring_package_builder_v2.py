#!/usr/bin/env python3
"""Build the unexecuted Window-1 Range-Attack scoring package V2."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from window1_range_attack_guarded_fill_adapter_v2 import (
    UNIQUE_LEDGER_SCHEMA,
    exact_integer,
)
from window1_range_attack_reference_adapter_v1 import (
    guarded_cutoff,
    parse_timestamp,
)


IMPLEMENTATION_PARENT = "f774d9060acc70efd4a80d48bfa7d4c6b1b9daf1"
CONTROLLING_AUDIT = "3811a772aea381767a763af90320a1af91475816"
STRICT_ASK_INSTRUMENT = "d413f23125d5931a56077c70f475d8815ffe36c0"
STRICT_ASK_AUDIT_REPORT_PATH = (
    ".claude/audit_20260726_window1_range_attack_v2_strict_ask/"
    "AUDIT_REPORT.md"
)
AUDIT_REPORT_PATH = (
    ".claude/audit_20260726_window1_range_attack_scoring_package/"
    "AUDIT_REPORT.md"
)
AUDIT_NUMERIC_PATH = (
    ".claude/audit_20260726_window1_range_attack_scoring_package/"
    "ADVERSARIAL_GATE_NUMERIC_RECEIPT.json"
)
PACKAGE_REL = (
    ".claude/window1_range_attack_scoring_package_v2_prerun_20260726"
)
EXECUTION_ID = (
    "w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2"
)
RESULTS_DIRECTORY = f".claude/window1_range_attack_results_{EXECUTION_ID}"
CANDIDATES = [
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
]
DEVELOPMENT_DATES = [
    f"2026-07-{day:02d}" for day in range(12, 21)
]
SEALED_DATES = [
    f"2026-07-{day:02d}" for day in range(24, 27)
]
RAW_FILL_REL = (
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/"
    "PRICE_FILLABILITY_RECEIPTS.jsonl.gz"
)
STREAM_RELS = [
    (
        ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/"
        f"UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    )
    for part in range(1, 5)
]
START_LEDGER_REL = (
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
DATA_MANIFEST_REL = (
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_DATA_BINDING_MANIFEST.json"
)
GUARD_REL = (
    ".claude/window1_round2_final_prerun_20260724/"
    "GUARDED_CUTOFF_PROVENANCE.json"
)
CANDIDATE_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_CANDIDATES_V2_STRICT_ASK.json"
)
METRIC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_OS_FAMILY_METRIC_CONTRACT_V1.json"
)
CONTRACT_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_SCORER_CONTRACT_V2.json"
)
NORMALIZED_PRINTS_REL = "../OMI-Window1-private/fit-local/prints.jsonl"
PUBLIC_TAPE_MANIFEST_REL = (
    "../OMI-Window1-private/fit-local/"
    "PUBLIC_TAPE_MANIFEST.sanitized.json"
)
EVENT_LEDGER_REL = "../OMI-Window1-private/joined/events.jsonl"
CACHE_REL = "../OMI-Window1-private/fit-local/guarded-cache-v3"
SOURCE_PATHS = [
    "arb-executor/analysis/window1_range_attack_guarded_fill_adapter_v2.py",
    "arb-executor/analysis/window1_range_attack_reference_adapter_v2.py",
    "arb-executor/analysis/window1_range_attack_scorer_v2.py",
    "arb-executor/analysis/window1_range_attack_scoring_runner_v2.py",
    "arb-executor/analysis/window1_range_attack_scoring_package_builder_v2.py",
    "arb-executor/analysis/window1_range_attack_scoring_package_freeze_v2.py",
    CONTRACT_REL,
    "arb-executor/tests/test_window1_range_attack_scoring_package_v2.py",
]
FROZEN_INPUT_PATHS = [
    CANDIDATE_REL,
    METRIC_REL,
    RAW_FILL_REL,
    *STREAM_RELS,
    START_LEDGER_REL,
    DATA_MANIFEST_REL,
    GUARD_REL,
    "arb-executor/analysis/window1_public_tape_export.py",
    "arb-executor/analysis/window1_guarded_cache_materializer.py",
    (
        ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/"
        "WINDOW1_RANGE_ATTACK_V2_PRE_RUN_MANIFEST.json"
    ),
    (
        ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/"
        "ARTIFACT_HASH_MANIFEST.json"
    ),
]
TEXT_SUFFIXES = {
    ".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml",
}


class PackageBuildError(RuntimeError):
    """Raised when a frozen receipt or construction invariant fails."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def canonical_text_bytes(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def identity_bytes(path: Path, raw: bytes | None = None) -> bytes:
    value = path.read_bytes() if raw is None else raw
    return canonical_text_bytes(value) if path.suffix.lower() in TEXT_SUFFIXES else value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path, *, canonical_text: bool = False) -> str:
    if canonical_text:
        return sha256_bytes(canonical_text_bytes(path.read_bytes()))
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_oid(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args], cwd=repo, check=False,
        capture_output=True, text=True,
    )
    if process.returncode:
        raise PackageBuildError(
            f"git {' '.join(args)} failed: {process.stderr.strip()}"
        )
    return process.stdout.strip()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_gzip_jsonl(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value))


def deterministic_gzip_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    raw = "".join(compact(row) + "\n" for row in rows).encode("utf-8")
    target = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=target, mtime=0
    ) as handle:
        handle.write(raw)
    return target.getvalue()


def source_row(
    repo: Path,
    relative: str,
    *,
    newline_probe: str = "native",
) -> dict[str, Any]:
    path = (repo / relative).resolve()
    if not path.is_file():
        raise PackageBuildError(f"missing source: {relative}")
    raw = path.read_bytes()
    is_text = path.suffix.lower() in TEXT_SUFFIXES
    if is_text and newline_probe == "lf":
        raw = canonical_text_bytes(raw)
    elif is_text and newline_probe == "crlf":
        raw = canonical_text_bytes(raw).replace(b"\n", b"\r\n")
    identity = identity_bytes(path, raw)
    return {
        "path": relative,
        "identity_bytes": len(identity),
        "sha256": sha256_bytes(identity),
        "git_blob_oid": git_blob_oid(identity),
        "hash_basis": "canonical_lf_text" if is_text else "exact_binary",
    }


def audit_blob(repo: Path, relative: str) -> dict[str, Any]:
    oid = git(repo, "rev-parse", f"{CONTROLLING_AUDIT}:{relative}")
    process = subprocess.run(
        ["git", "cat-file", "blob", oid], cwd=repo,
        check=True, capture_output=True,
    )
    raw = process.stdout
    return {
        "audit_commit": CONTROLLING_AUDIT,
        "path": relative,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "git_blob_oid": oid,
    }


def commit_blob(
    repo: Path,
    commit: str,
    relative: str,
) -> dict[str, Any]:
    oid = git(repo, "rev-parse", f"{commit}:{relative}")
    process = subprocess.run(
        ["git", "cat-file", "blob", oid], cwd=repo,
        check=True, capture_output=True,
    )
    raw = process.stdout
    return {
        "commit": commit,
        "path": relative,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "git_blob_oid": oid,
    }


def _load_policy_selectors(repo: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    selectors: dict[tuple[str, str, str], dict[str, Any]] = {}
    stream_count = 0
    for relative in STREAM_RELS:
        with gzip.open(repo / relative, "rt", encoding="utf-8") as handle:
            for line in handle:
                wrapper = json.loads(line)
                stream_count += 1
                candidate = str(wrapper["candidate_id"])
                event_id = str(wrapper["event_id"])
                states = wrapper["stream"].get(
                    "causal_policy_fill_state_by_leg"
                ) or {}
                for leg_id, state in states.items():
                    if not isinstance(state, Mapping):
                        continue
                    receipt = state.get("simulated_fill_receipt")
                    interval = state.get("simulated_fill_order_interval_id")
                    if not receipt or not interval:
                        continue
                    key = (candidate, event_id, str(leg_id))
                    selectors[key] = {
                        "candidate_id": candidate,
                        "event_id": event_id,
                        "leg_id": str(leg_id),
                        "simulated_fill_order_interval_id": str(interval),
                        "simulated_fill_receipt": str(receipt),
                        "simulated_fill_price": state.get(
                            "simulated_fill_price"
                        ),
                        "simulated_fill_ts": state.get("simulated_fill_ts"),
                        "source_stream_path": relative,
                        "source_order_stream_sha256": wrapper["stream"].get(
                            "order_stream_sha256"
                        ),
                    }
    if stream_count != 1608:
        raise PackageBuildError("policy selector source is not 1,608 streams")
    return selectors


def _unique_fill_ledger(
    repo: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fillable = [
        row for row in read_gzip_jsonl(repo / RAW_FILL_REL)
        if row.get("FILLABLE_AT_X") is True
    ]
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in fillable:
        grouped[(
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        )].append(row)
    selectors = _load_policy_selectors(repo)
    output: list[dict[str, Any]] = []
    duplicate_receipts: list[dict[str, Any]] = []
    singleton_terminal_selector_supersessions: list[dict[str, Any]] = []
    removed = 0
    for key in sorted(grouped):
        rows = grouped[key]
        selector = selectors.get(key)
        if len(rows) == 1:
            selected = rows[0]
            basis = "SINGLETON_GUARDED_RECEIPT"
            selector_matches = bool(
                selector
                and selector["simulated_fill_order_interval_id"]
                == selected["order_interval_id"]
                and selector["simulated_fill_receipt"]
                == selected["FILLABLE_AT_X_evidence"]["receipt"]
            )
            if selector and not selector_matches:
                singleton_terminal_selector_supersessions.append({
                    "candidate_id": key[0],
                    "event_id": key[1],
                    "leg_id": key[2],
                    "guarded_interval_id": selected["order_interval_id"],
                    "guarded_evidence_receipt": selected[
                        "FILLABLE_AT_X_evidence"
                    ]["receipt"],
                    "terminal_policy_interval_id": selector[
                        "simulated_fill_order_interval_id"
                    ],
                    "terminal_policy_evidence_receipt": selector[
                        "simulated_fill_receipt"
                    ],
                    "treatment": (
                        "singleton guarded receipt is already unique; "
                        "later non-guarded policy supersession is not a "
                        "runtime scoring source"
                    ),
                })
        else:
            if selector is None:
                raise PackageBuildError(
                    f"duplicate guarded key lacks policy selector: {key}"
                )
            matches = [
                row for row in rows
                if (
                    row["order_interval_id"]
                    == selector["simulated_fill_order_interval_id"]
                    and row["FILLABLE_AT_X_evidence"]["receipt"]
                    == selector["simulated_fill_receipt"]
                    and row["target_price_cents"]
                    == selector["simulated_fill_price"]
                    and abs(
                        float(row["FILLABLE_AT_X_evidence"]["ts"])
                        - float(selector["simulated_fill_ts"])
                    ) <= 1e-6
                )
            ]
            if len(matches) != 1:
                raise PackageBuildError(
                    f"policy selector did not resolve duplicate key: {key}"
                )
            selected = matches[0]
            basis = "POLICY_SELECTED_INTERVAL_AND_EVIDENCE_IDENTITY"
            removed += len(rows) - 1
            duplicate_receipts.append({
                "candidate_id": key[0],
                "event_id": key[1],
                "leg_id": key[2],
                "raw_guarded_rows": [
                    {
                        "order_interval_id": row["order_interval_id"],
                        "target_price_cents": row["target_price_cents"],
                        "evidence_receipt": row[
                            "FILLABLE_AT_X_evidence"
                        ]["receipt"],
                        "evidence_timestamp": row[
                            "FILLABLE_AT_X_evidence"
                        ]["ts"],
                    }
                    for row in rows
                ],
                "selected_order_interval_id": selected["order_interval_id"],
                "selected_target_price_cents": selected["target_price_cents"],
                "selected_evidence_receipt": selected[
                    "FILLABLE_AT_X_evidence"
                ]["receipt"],
                "selection_basis": basis,
                "selector_source_stream": selector["source_stream_path"],
                "selector_order_stream_sha256": selector[
                    "source_order_stream_sha256"
                ],
                "removed_excess_rows": len(rows) - 1,
            })
        selector_payload = {
            "selection_basis": basis,
            "candidate_id": key[0],
            "event_id": key[1],
            "leg_id": key[2],
            "selected_order_interval_id": selected["order_interval_id"],
            "selected_evidence_receipt": selected[
                "FILLABLE_AT_X_evidence"
            ]["receipt"],
            "raw_guarded_group_size": len(rows),
            "raw_guarded_source_sha256": sha256_file(repo / RAW_FILL_REL),
        }
        if selector is not None:
            selector_payload["policy_selector"] = selector
        selector_payload["selector_receipt_sha256"] = canonical_sha256(
            selector_payload
        )
        frozen = dict(selected)
        frozen["schema_version"] = UNIQUE_LEDGER_SCHEMA
        frozen["unique_selection_receipt"] = selector_payload
        output.append(frozen)
    evidence = Counter(
        str(row["FILLABLE_AT_X_evidence_type"]) for row in output
    )
    candidates = Counter(str(row["candidate_id"]) for row in output)
    if (
        len(fillable) != 995
        or len(output) != 991
        or removed != 4
        or candidates != Counter({CANDIDATES[0]: 501, CANDIDATES[1]: 490})
        or evidence != Counter({
            "PRICE_REACHED": 965,
            "STRICT_ASK_CERTAIN_FILL": 26,
        })
    ):
        raise PackageBuildError("unique guarded-fill census changed")
    if len({(
        row["candidate_id"], row["event_id"], row["leg_id"]
    ) for row in output}) != 991:
        raise PackageBuildError("unique ledger still contains duplicate legs")
    expected = {
        (CANDIDATES[0], "KXWTACHALLENGERMATCH-26JUL20LANRAD", "RAD"):
            ("0005", 80),
        (CANDIDATES[1], "KXWTACHALLENGERMATCH-26JUL20LANRAD", "RAD"):
            ("0005", 80),
        (CANDIDATES[1], "KXATPCHALLENGERMATCH-26JUL19BOHBOU", "BOH"):
            ("0007", 3),
    }
    observed = {
        (row["candidate_id"], row["event_id"], row["leg_id"]): (
            str(row["order_interval_id"]).rsplit("|", 1)[-1],
            row["target_price_cents"],
        )
        for row in output
    }
    if any(observed.get(key) != value for key, value in expected.items()):
        raise PackageBuildError("known duplicate resolution changed")
    receipt = {
        "schema_version": "window1-range-attack-unique-fill-derivation-v2",
        "raw_guarded_fillable_rows": 995,
        "raw_candidate_event_leg_keys": 991,
        "frozen_unique_ledger_rows": 991,
        "removed_excess_interval_rows": 4,
        "candidate_counts": dict(sorted(candidates.items())),
        "evidence_type_counts": dict(sorted(evidence.items())),
        "maximum_rows_per_candidate_event_leg": 1,
        "duplicate_groups": duplicate_receipts,
        "singleton_terminal_selector_supersessions":
            singleton_terminal_selector_supersessions,
        "runtime_reads_raw_policy_streams": False,
        "runtime_reads_raw_interval_fillability_receipts": False,
        "quantity_price_timestamp_boundary_and_evidence_authority":
            "guarded receipt only",
        "selector_authority":
            "interval and evidence identity only during package construction",
        "metrics": None,
        "scored": False,
    }
    return output, receipt


def _eligible_prints(
    rows: Iterable[Mapping[str, Any]],
    *,
    ticker: str,
    t8_floor: float,
    cutoff: float,
) -> list[dict[str, Any]]:
    dedup: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("ticker") or ticker) != ticker:
            continue
        receipt = str(row.get("trade_id") or row.get("receipt_id") or "")
        if not receipt:
            raise PackageBuildError("cache print lacks receipt identity")
        size = row.get("size")
        if (
            isinstance(size, bool)
            or not isinstance(size, (int, float))
            or not math.isfinite(float(size))
            or float(size) <= 0
        ):
            continue
        if (
            row.get("synthetic_transition") is True
            or row.get("self_evidence") is True
            or row.get("own_order") is True
        ):
            continue
        price = exact_integer(
            row.get("price"), "reference print price",
            minimum=1, maximum=99,
        )
        ts = parse_timestamp(row.get("ts"), "reference print timestamp")
        if not (t8_floor <= ts <= cutoff):
            continue
        normalized = {
            "receipt": receipt,
            "ts": ts,
            "price": price,
            "size": float(size),
        }
        prior = dedup.get(receipt)
        if prior is not None and prior != normalized:
            raise PackageBuildError("conflicting cache print receipt")
        dedup[receipt] = normalized
    return list(dedup.values())


def _reference_tie_census(repo: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    events = read_jsonl(repo / EVENT_LEDGER_REL)
    starts = {
        str(row["event_id"]): row
        for row in read_jsonl(repo / START_LEDGER_REL)
    }
    ties: list[dict[str, Any]] = []
    wanted_receipts: set[str] = set()
    positive_boundary_legs_checked = 0
    reference_eligible_legs = 0
    for event in events:
        event_id = str(event["event_id"])
        cutoff = guarded_cutoff(starts[event_id])
        if cutoff["status"] != "positive":
            continue
        scheduled = parse_timestamp(
            event.get("scheduled_start_exchange_ts"), "scheduled start"
        )
        t8_floor = scheduled - 8 * 60 * 60
        with gzip.open(
            repo / CACHE_REL / f"{event_id}.json.gz",
            "rt", encoding="utf-8",
        ) as handle:
            cache = json.load(handle)
        cache_legs = {
            str(row["ticker"]): row for row in cache.get("legs") or []
        }
        for leg in event["legs"]:
            ticker = str(leg["ticker"])
            leg_id = str(leg.get("leg_id") or leg.get("leg"))
            cached_prints = cache_legs[ticker].get("prints") or []
            if cached_prints:
                positive_boundary_legs_checked += 1
            eligible = _eligible_prints(
                cached_prints,
                ticker=ticker,
                t8_floor=t8_floor,
                cutoff=float(cutoff["cutoff_ts"]),
            )
            if not eligible:
                continue
            reference_eligible_legs += 1
            latest_ts = max(row["ts"] for row in eligible)
            latest = [
                row for row in eligible
                if row["ts"] == latest_ts
            ]
            if len(latest) < 2:
                continue
            prices = sorted({row["price"] for row in latest})
            receipts = sorted(row["receipt"] for row in latest)
            wanted_receipts.update(receipts)
            ties.append({
                "event_id": event_id,
                "event_date": str(event["event_date"]),
                "category": str(event.get("category") or ""),
                "leg_id": leg_id,
                "ticker": ticker,
                "latest_timestamp": latest_ts,
                "supporting_receipts": [
                    {
                        "receipt": row["receipt"],
                        "price_cents": row["price"],
                        "size": row["size"],
                    }
                    for row in sorted(
                        latest, key=lambda row: row["receipt"]
                    )
                ],
                "receipt_count": len(latest),
                "distinct_prices": prices,
                "same_price": len(prices) == 1,
                "authoritative_exchange_sequence_present": False,
                "final_reference_available": len(prices) == 1,
                "final_reference_price_cents":
                    prices[0] if len(prices) == 1 else None,
                "final_reason": (
                    None if len(prices) == 1 else
                    "ambiguous_latest_timestamp_multiple_prices_"
                    "no_authoritative_sequence"
                ),
            })
    differing = sum(not row["same_price"] for row in ties)
    if len(ties) != 272 or differing != 64:
        raise PackageBuildError(
            "latest-timestamp tie census changed: "
            f"ties={len(ties)} differing={differing} "
            f"checked={positive_boundary_legs_checked} "
            f"eligible={reference_eligible_legs}"
        )

    normalized_ordinals: dict[str, int] = {}
    normalized_keys: set[str] = set()
    normalized_path = (repo / NORMALIZED_PRINTS_REL).resolve()
    with normalized_path.open("r", encoding="utf-8") as handle:
        for ordinal, line in enumerate(handle, 1):
            row = json.loads(line)
            receipt = str(row.get("trade_id") or row.get("receipt_id") or "")
            if receipt in wanted_receipts:
                normalized_ordinals[receipt] = ordinal
                normalized_keys.update(str(key) for key in row)
    if set(normalized_ordinals) != wanted_receipts:
        raise PackageBuildError("tie receipt missing from normalized source")
    sequence_like = sorted(
        key for key in normalized_keys
        if key.lower() in {
            "sequence", "sequence_number", "trade_sequence",
            "exchange_sequence", "source_sequence",
        }
    )
    for tie in ties:
        for row in tie["supporting_receipts"]:
            row["normalized_source_row_ordinal"] = normalized_ordinals[
                row["receipt"]
            ]
            row["normalized_source_row_ordinal_authoritative"] = False
    public_manifest = read_json(repo / PUBLIC_TAPE_MANIFEST_REL)
    census = {
        "schema_version": "window1-range-attack-reference-tie-census-v2",
        "positive_boundary_legs_checked": positive_boundary_legs_checked,
        "reference_eligible_legs": reference_eligible_legs,
        "latest_timestamp_multi_receipt_ties": len(ties),
        "controlling_audit_reported_ties": 271,
        "source_reproduction_delta_from_audit": 1,
        "same_price_ties_reference_available": sum(
            row["same_price"] for row in ties
        ),
        "differing_price_ties_reference_unavailable": sum(
            not row["same_price"] for row in ties
        ),
        "authoritative_sequence_mappings_found": 0,
        "fallback_law": {
            "same_timestamp_same_price":
                "available at shared price with every supporting receipt",
            "same_timestamp_differing_prices":
                "unavailable: ambiguous_latest_timestamp_multiple_prices_"
                "no_authoritative_sequence",
        },
        "ties": ties,
        "metrics": None,
        "scored": False,
    }
    trace = {
        "schema_version": "window1-range-attack-reference-source-trace-v2",
        "normalized_source": {
            "path": NORMALIZED_PRINTS_REL,
            "bytes": normalized_path.stat().st_size,
            "sha256": sha256_file(normalized_path),
            "manifest_sha256": public_manifest["artifacts"][
                "normalized_true_prints"
            ]["sha256"],
            "canonical_rows": public_manifest["records"][
                "canonical_true_print_rows"
            ],
            "exchange_clock": public_manifest["contract"][
                "exchange_clock"
            ],
            "identity": public_manifest["contract"][
                "true_print_identity"
            ],
            "fields_observed_on_tie_rows": sorted(normalized_keys),
            "authoritative_sequence_fields_observed": sequence_like,
        },
        "raw_source": {
            "endpoint": public_manifest["endpoint"],
            "raw_ticker_file_count": public_manifest["artifacts"][
                "raw_ticker_file_count"
            ],
            "raw_hash_set_sha256": public_manifest["artifacts"][
                "raw_hash_set_sha256"
            ],
            "exchange_sequence_bound": False,
        },
        "normalization_path": {
            "exporter": source_row(
                repo,
                "arb-executor/analysis/window1_public_tape_export.py",
            ),
            "cache_materializer": source_row(
                repo,
                "arb-executor/analysis/window1_guarded_cache_materializer.py",
            ),
            "finding": (
                "exported rows bind created_time and trade_id but no "
                "authoritative exchange sequence; cache materialization "
                "orders equal timestamps by trade_id, which is not lawful "
                "reference precedence"
            ),
            "normalized_source_row_ordinal_is_authoritative": False,
            "receipt_uuid_ordering_allowed": False,
        },
        "tie_receipts_traced": len(wanted_receipts),
        "authoritative_ordering_result": "NOT_AVAILABLE",
        "metrics": None,
        "scored": False,
    }
    return census, trace


def _event_leg_identities(repo: Path) -> list[dict[str, Any]]:
    rows = []
    for boundary in read_jsonl(repo / START_LEDGER_REL):
        for leg in boundary.get("legs") or []:
            rows.append({
                "event_id": str(boundary["event_id"]),
                "event_date": str(boundary["event_date"]),
                "category": str(boundary["category"]),
                "leg_id": str(leg["leg"]),
                "ticker": str(leg["ticker"]),
            })
    rows.sort(key=lambda row: (
        row["event_id"], row["leg_id"], row["ticker"]
    ))
    if (
        len(rows) != 1608
        or len({(row["event_id"], row["leg_id"]) for row in rows}) != 1608
        or len({row["event_id"] for row in rows}) != 804
    ):
        raise PackageBuildError("D/leg identity conservation failed")
    return rows


def build(
    repo: Path,
    output: Path,
    *,
    newline_probe: str = "native",
) -> list[str]:
    if output.exists() and any(output.iterdir()):
        raise PackageBuildError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    head = git(repo, "rev-parse", "HEAD")
    if head != IMPLEMENTATION_PARENT and git(
        repo, "rev-parse", "HEAD^"
    ) != IMPLEMENTATION_PARENT:
        raise PackageBuildError(
            "builder must run from parent or its sole additions-only child"
        )
    spec = read_json(repo / CANDIDATE_REL)
    if spec.get("candidate_ids") != CANDIDATES:
        raise PackageBuildError("frozen candidate identity/order changed")
    if spec.get("D") != 804:
        raise PackageBuildError("D=804 changed")
    metric = read_json(repo / METRIC_REL)
    if metric.get("D") != 804 or metric.get("target_count") != 603:
        raise PackageBuildError("metric contract changed")
    git(repo, "cat-file", "-e", f"{STRICT_ASK_INSTRUMENT}^{{commit}}")

    unique_rows, unique_receipt = _unique_fill_ledger(repo)
    unique_bytes = deterministic_gzip_jsonl(unique_rows)
    (output / "UNIQUE_GUARDED_FILL_LEDGER.jsonl.gz").write_bytes(
        unique_bytes
    )
    unique_receipt["unique_ledger"] = {
        "path": f"{PACKAGE_REL}/UNIQUE_GUARDED_FILL_LEDGER.jsonl.gz",
        "bytes": len(unique_bytes),
        "sha256": sha256_bytes(unique_bytes),
        "git_blob_oid": git_blob_oid(unique_bytes),
    }
    write_json(output / "UNIQUE_GUARDED_FILL_DERIVATION_RECEIPT.json",
               unique_receipt)

    tie_census, trace = _reference_tie_census(repo)
    write_json(output / "REFERENCE_LATEST_TIMESTAMP_TIE_CENSUS.json",
               tie_census)
    write_json(output / "REFERENCE_SOURCE_ORDER_TRACE.json", trace)

    identities = _event_leg_identities(repo)
    identity_receipt = {
        "schema_version": "window1-range-attack-event-leg-identities-v2",
        "D": 804,
        "leg_identities": 1608,
        "development_dates": DEVELOPMENT_DATES,
        "sealed_holdout_dates": SEALED_DATES,
        "rows": identities,
        "rows_canonical_sha256": canonical_sha256(identities),
    }
    write_json(output / "FROZEN_EVENT_LEG_IDENTITIES.json", identity_receipt)

    data_manifest = read_json(repo / DATA_MANIFEST_REL)
    cache = data_manifest["input_records"]["per_leg_market_streams"]
    event_input = data_manifest["input_records"]["immutable_event_ledger"]
    cache_files = cache["event_file_receipts"]
    write_json(output / "GUARDED_CACHE_V3_HASH_SET.json", {
        "schema_version": "window1-guarded-cache-v3-hash-set-v2",
        "cache_version": cache["cache_version"],
        "cache_key": cache["cache_key"],
        "aggregate_sha256": cache["content_sha256"],
        "bytes": cache["bytes"],
        "event_count": 804,
        "ticker_count": 1608,
        "date_range": cache["date_range"],
        "holdout_dates_present": cache["holdout_dates_present"],
        "event_files": cache_files,
        "event_files_canonical_sha256": canonical_sha256(cache_files),
    })

    gate = {
        "schema_version": "window1-range-attack-execution-gate-v2",
        "execution_authorized_now": False,
        "future_independent_PASS_audit_required": True,
        "future_report_must_bind": [
            "exact package commit SHA",
            "execution ID",
            "input-bundle SHA-256",
            "frozen command template",
        ],
        "authorization_commit_verification": (
            "supplied separately; report blob read from exact commit"
        ),
        "audit_report_self_sha_reference_required": False,
        "execution_id": EXECUTION_ID,
        "results_directory": RESULTS_DIRECTORY,
        "one_attempt_only": True,
        "retry_or_resume_allowed": False,
        "command_template": (
            "python -B arb-executor/analysis/"
            "window1_range_attack_scoring_runner_v2.py --repo . --package "
            f"{PACKAGE_REL}/SCORING_INPUT_MANIFEST.json --mode execute "
            "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
            "--authorization-report <AUDIT_REPORT_PATH>"
        ),
        "real_execution_invoked": False,
    }
    write_json(output / "EXECUTION_AUTHORIZATION_GATE.json", gate)

    expected = {
        "schema_version": "window1-range-attack-expected-output-schema-v2",
        "candidate_event_rows": 1608,
        "candidate_order": CANDIDATES,
        "reference_fields_added": [
            "reference_supporting_receipts",
            "reference_latest_timestamp_tie_count",
            "reference_latest_timestamp_distinct_prices",
            "reference_authoritative_sequence_available",
        ],
        "ranking_or_selection_allowed": False,
    }
    write_json(output / "EXPECTED_OUTPUT_SCHEMA.json", expected)

    audit_rows = [
        audit_blob(repo, AUDIT_REPORT_PATH),
        audit_blob(repo, AUDIT_NUMERIC_PATH),
    ]
    committed = [
        source_row(repo, relative, newline_probe=newline_probe)
        for relative in SOURCE_PATHS + FROZEN_INPUT_PATHS
    ]
    private_inputs = [
        {
            "role": "immutable_event_ledger",
            "path": EVENT_LEDGER_REL,
            "bytes": event_input["bytes"],
            "sha256": event_input["content_sha256"],
            "events": 804,
            "tickers": 1608,
            "date_range": event_input["date_range"],
            "holdout_dates_present": 0,
        },
        {
            "role": "guarded_cache_v3_directory",
            "path": CACHE_REL,
            "bytes": cache["bytes"],
            "sha256": cache["content_sha256"],
            "events": 804,
            "tickers": 1608,
            "date_range": cache["date_range"],
            "holdout_dates_present": 0,
            "per_file_hash_set": (
                f"{PACKAGE_REL}/GUARDED_CACHE_V3_HASH_SET.json"
            ),
        },
    ]
    source_manifest = {
        "schema_version": "window1-range-attack-source-hash-manifest-v2",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_audit": CONTROLLING_AUDIT,
        "strict_ask_instrument": STRICT_ASK_INSTRUMENT,
        "audit_artifacts": audit_rows,
        "strict_ask_pass_addendum": commit_blob(
            repo, STRICT_ASK_INSTRUMENT, STRICT_ASK_AUDIT_REPORT_PATH
        ),
        "committed_inputs": committed,
        "private_runtime_inputs": private_inputs,
        "construction_only_inputs": {
            "raw_fillability_receipts": source_row(repo, RAW_FILL_REL),
            "policy_stream_shards": [
                source_row(repo, relative) for relative in STREAM_RELS
            ],
            "normalized_true_print_source": {
                "path": NORMALIZED_PRINTS_REL,
                "bytes": (repo / NORMALIZED_PRINTS_REL).resolve().stat().st_size,
                "sha256": sha256_file(
                    (repo / NORMALIZED_PRINTS_REL).resolve()
                ),
                "runtime_role": False,
            },
        },
        "unique_runtime_fill_ledger": unique_receipt["unique_ledger"],
        "newline_identity_law": (
            "canonical LF bytes for committed text; exact bytes for binary"
        ),
        "holdout_inputs": 0,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)

    roles = {
        "scorer_contract": CONTRACT_REL,
        "candidate_definitions": CANDIDATE_REL,
        "metric_contract": METRIC_REL,
        "unique_guarded_fill_ledger": (
            f"{PACKAGE_REL}/UNIQUE_GUARDED_FILL_LEDGER.jsonl.gz"
        ),
        "start_ledger": START_LEDGER_REL,
        "data_binding_manifest": DATA_MANIFEST_REL,
        "event_ledger": EVENT_LEDGER_REL,
        "guarded_cache_directory": CACHE_REL,
        "event_leg_identities": (
            f"{PACKAGE_REL}/FROZEN_EVENT_LEG_IDENTITIES.json"
        ),
        "guarded_cache_hash_set": (
            f"{PACKAGE_REL}/GUARDED_CACHE_V3_HASH_SET.json"
        ),
        "unique_fill_derivation_receipt": (
            f"{PACKAGE_REL}/UNIQUE_GUARDED_FILL_DERIVATION_RECEIPT.json"
        ),
        "reference_tie_census": (
            f"{PACKAGE_REL}/REFERENCE_LATEST_TIMESTAMP_TIE_CENSUS.json"
        ),
        "reference_source_trace": (
            f"{PACKAGE_REL}/REFERENCE_SOURCE_ORDER_TRACE.json"
        ),
        "expected_output_schema": (
            f"{PACKAGE_REL}/EXPECTED_OUTPUT_SCHEMA.json"
        ),
        "authorization_gate": (
            f"{PACKAGE_REL}/EXECUTION_AUTHORIZATION_GATE.json"
        ),
        "source_hash_manifest": (
            f"{PACKAGE_REL}/SOURCE_HASH_MANIFEST.json"
        ),
    }
    bundle = {
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_audit": CONTROLLING_AUDIT,
        "strict_ask_instrument": STRICT_ASK_INSTRUMENT,
        "candidate_ids": CANDIDATES,
        "D": 804,
        "leg_identities": 1608,
        "unique_fill_rows": 991,
        "unique_fill_ledger_sha256": sha256_bytes(unique_bytes),
        "reference_ties": 272,
        "reference_ambiguous_differing_price_ties": 64,
        "development_dates": DEVELOPMENT_DATES,
        "sealed_holdout_dates": SEALED_DATES,
        "roles": roles,
        "committed_source_receipts": committed,
        "private_source_receipts": private_inputs,
        "event_leg_identities_sha256": identity_receipt[
            "rows_canonical_sha256"
        ],
        "guarded_cache_event_hash_set_sha256": canonical_sha256(cache_files),
    }
    package = {
        "schema_version": "window1-range-attack-scoring-input-manifest-v2",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_audit": CONTROLLING_AUDIT,
        "strict_ask_instrument": STRICT_ASK_INSTRUMENT,
        "candidate_ids": CANDIDATES,
        "D": 804,
        "target_PC": 603,
        "execution_id": EXECUTION_ID,
        "results_directory": RESULTS_DIRECTORY,
        "roles": roles,
        "input_bundle_payload": bundle,
        "input_bundle_sha256": canonical_sha256(bundle),
        "future_independent_pass_required": True,
        "execution_authorized_now": False,
        "forbidden_runtime_roles": [
            "raw PRICE_FILLABILITY_RECEIPTS",
            "causal_policy_fill_state_by_leg",
            "candidate order streams",
            "raw strict_ask_certain_fill actions",
            "raw post-cutoff policy actions",
        ],
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", package)

    no_execution = {
        "schema_version": "window1-range-attack-no-execution-v2",
        "execution_id": EXECUTION_ID,
        "real_population_scorer_invocations": 0,
        "results_directory_exists": (repo / RESULTS_DIRECTORY).exists(),
        "C": None, "PC": None, "S": None, "IC": None,
        "performance": None,
        "ranking_or_selection": None,
        "holdout_access": False,
        "live_or_production_access": False,
    }
    if no_execution["results_directory_exists"]:
        raise PackageBuildError("new execution results directory exists")
    write_json(output / "NO_EXECUTION_NO_METRICS_RECEIPT.json", no_execution)

    report = f"""# Window-1 Range-Attack scoring package V2 PRE-RUN

This additions-only package corrects the four findings at
`{CONTROLLING_AUDIT}` without changing candidates, strategy, fill law,
metric law, D=804, or the passed strict-ask instrument.

## Frozen corrections

- Exact integer validation rejects truncation of quantity and cent prices.
- Runtime consumes 991 unique guarded fills: 501 macro-hold and 490
  macro-micro; 965 are print-backed and 26 strict-ask-backed.
- The three duplicate keys are resolved only by frozen policy interval and
  evidence identity during package construction. Runtime cannot read policy
  streams or raw interval receipts.
- The frozen source reproduces 272 latest-timestamp multi-receipt ties (one
  more same-price tie than the audit headline); 208 share one price and retain
  all supporting receipts. The 64 differing-price ties are unavailable because
  no authoritative exchange sequence survives normalization.
- Future audit authorization supplies the audit commit separately; the report
  at that exact commit binds package commit, execution ID, bundle, and command
  template without impossible self-reference.
- Committed text identities use canonical LF bytes, so LF and CRLF checkouts
  produce the same package.

All C/PC/S/IC and performance values remain null. No development scorer,
benchmark, holdout, live, or production surface was invoked.
"""
    (output / "PRE_RUN_REPORT.md").write_bytes(
        canonical_text_bytes(report.encode("utf-8"))
    )
    return sorted(path.name for path in output.iterdir() if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--newline-probe", choices=("native", "lf", "crlf"),
        default="native",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output.resolve()
        if args.output.is_absolute()
        else (repo / args.output).resolve()
    )
    files = build(repo, output, newline_probe=args.newline_probe)
    print(compact({"files": files, "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
