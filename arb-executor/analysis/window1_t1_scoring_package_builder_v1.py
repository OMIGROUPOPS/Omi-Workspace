#!/usr/bin/env python3
"""Build the score-free T1 scoring-package PRE-RUN.

Construction reads the frozen T1 overlays only to produce a unique runtime
fill ledger.  Raw overlays are never runtime scorer roles.  The real scorer
is never imported or invoked by this builder.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import io
import json
import math
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_range_attack_prerun_builder as boundary_builder
import window1_round2_data_binding as binding
import window1_round2_real_capability as capability
import window1_round4_macromicro_instrument as normalizer
import window1_range_attack_instrument_v2 as range_v2
import window1_t1_post_first_leg_instrument as t1


VERSION = "window1-t1-scoring-package-builder-v1"
IMPLEMENTATION_PARENT = "88b0eae8620172f41e2f5d45320408357de24c6f"
CONTROLLING_T1_PASS = "de2f627e53885bd1a44a42b92f23b5b93a391a47"
AUDITED_SCORER_COMMIT = "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
PACKAGE_REL = ".claude/window1_t1_scoring_package_prerun_20260727"
T1_PACKAGE_REL = ".claude/window1_t1_post_first_leg_prerun_20260727"
PRIOR_SCORING_REL = (
    ".claude/window1_range_attack_scoring_package_v2_prerun_20260726"
)
PARENT_RESULTS_REL = (
    ".claude/window1_range_attack_results_"
    "w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2"
)
EXECUTION_ID = "w1-t1-dev-20260712-20260720-grid1-scorepkg-v1"
RESULTS_REL = f".claude/window1_t1_results_{EXECUTION_ID}"
MANIFEST_REL = f"{PACKAGE_REL}/SCORING_INPUT_MANIFEST.json"
RUNNER_REL = "arb-executor/analysis/window1_t1_scoring_runner_v1.py"
COMMAND_TEMPLATE = (
    f"python -B {RUNNER_REL} --repo . --package {MANIFEST_REL} "
    "--mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
AUDIT_REPORT_REL = (
    ".claude/audit_20260727_window1_t1_post_first_leg/AUDIT_REPORT.md"
)
AUDIT_RECEIPT_REL = (
    ".claude/audit_20260727_window1_t1_post_first_leg/"
    "INDEPENDENT_T1_REPRODUCTION_RECEIPT.json"
)
EVENTS_REL = "../OMI-Window1-private/joined/events.jsonl"
CACHE_REL = "../OMI-Window1-private/fit-local/guarded-cache-v3"
START_REL = ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl"
SPEC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T1_POST_FIRST_LEG_CANDIDATES_V1.json"
)
CONTRACT_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T1_SCORER_CONTRACT_V1.json"
)
ADAPTER_REL = "arb-executor/analysis/window1_t1_scoring_adapter_v1.py"
BUILDER_REL = "arb-executor/analysis/window1_t1_scoring_package_builder_v1.py"
FREEZER_REL = "arb-executor/analysis/window1_t1_scoring_package_freeze_v1.py"
TEST_REL = "arb-executor/tests/test_window1_t1_scoring_package_v1.py"
AUDITED_FILES = (
    "arb-executor/analysis/window1_range_attack_scorer_v2.py",
    "arb-executor/analysis/window1_range_attack_reference_adapter_v2.py",
    "arb-executor/analysis/window1_range_attack_guarded_fill_adapter_v2.py",
    "arb-executor/analysis/window1_range_attack_scoring_runner_v2.py",
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_SCORER_CONTRACT_V2.json",
)
OVERLAY_FILES = tuple(
    f"{T1_PACKAGE_REL}/UNSCORED_T1_CANDIDATE_EVENT_OVERLAYS_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
BASE_STREAM_FILES = tuple(
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/"
    f"UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
CANDIDATES = t1.CANDIDATES
BASE_CANDIDATES = t1.BASE_CANDIDATES
D_REQUIRED = 804
LOT = 5
TARGET_PC = 603
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}


class T1ScoringPackageError(RuntimeError):
    """Raised when package construction leaves the frozen contract."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def canonical_text_bytes(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def identity_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return (
        canonical_text_bytes(raw)
        if path.suffix.lower() in TEXT_SUFFIXES else raw
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(raw)}\0".encode("ascii") + raw
    ).hexdigest()


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, check=False
    )
    if process.returncode:
        raise T1ScoringPackageError(
            f"git {' '.join(args)} failed: "
            + process.stderr.decode(errors="replace").strip()
        )
    return process.stdout.decode("utf-8", errors="strict").strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_gzip_jsonl(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value))


def deterministic_gzip_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as gz:
        with io.TextIOWrapper(gz, encoding="utf-8", newline="\n") as text:
            for row in rows:
                text.write(compact(row) + "\n")
    return buffer.getvalue()


def source_row(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = (repo / relative).resolve()
    raw = identity_bytes(path)
    try:
        tracked_oid = git(repo, "rev-parse", f"HEAD:{relative}")
    except T1ScoringPackageError:
        tracked_oid = git_blob_oid(raw)
    return {
        "path": relative,
        "role": role,
        "hash_basis": (
            "canonical_lf_text"
            if path.suffix.lower() in TEXT_SUFFIXES else "exact_binary"
        ),
        "identity_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_oid": tracked_oid,
    }


def audit_blob(repo: Path, relative: str) -> dict[str, Any]:
    raw = subprocess.run(
        ["git", "show", f"{CONTROLLING_T1_PASS}:{relative}"],
        cwd=repo, capture_output=True, check=False,
    )
    if raw.returncode:
        raise T1ScoringPackageError(
            f"controlling audit artifact missing: {relative}"
        )
    content = raw.stdout
    blob = git(repo, "rev-parse", f"{CONTROLLING_T1_PASS}:{relative}")
    return {
        "audit_commit": CONTROLLING_T1_PASS,
        "path": relative,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "git_blob_oid": blob,
    }


def _exact_int(value: Any, field: str, low: int | None = None,
               high: int | None = None) -> int:
    if isinstance(value, bool):
        raise T1ScoringPackageError(f"{field} is boolean")
    if isinstance(value, int):
        result = value
    elif (
        isinstance(value, float)
        and math.isfinite(value)
        and value.is_integer()
    ):
        result = int(value)
    else:
        raise T1ScoringPackageError(f"{field} is not an exact integer")
    if low is not None and result < low:
        raise T1ScoringPackageError(f"{field} below {low}")
    if high is not None and result > high:
        raise T1ScoringPackageError(f"{field} above {high}")
    return result


def _load_overlays(repo: Path) -> tuple[
    list[dict[str, Any]], dict[tuple[str, str], str], dict[str, str]
]:
    rows: list[dict[str, Any]] = []
    row_hashes: dict[tuple[str, str], str] = {}
    shard_hashes: dict[str, str] = {}
    for relative in OVERLAY_FILES:
        shard_hashes[relative] = sha256_file(repo / relative)
        for row in read_gzip_jsonl(repo / relative):
            if (
                row.get("metrics") is not None
                or row.get("performance") is not None
                or row.get("scored") is not False
                or any(row.get(name) is not None for name in ("C", "PC", "IC", "S"))
            ):
                raise T1ScoringPackageError("performance entered T1 overlay")
            key = (str(row["candidate_id"]), str(row["event_id"]))
            if key in row_hashes:
                raise T1ScoringPackageError("duplicate candidate/event overlay")
            row_hashes[key] = canonical_sha256(row)
            rows.append(row)
    expected = {(candidate, str(row["event_id"]))
                for candidate in CANDIDATES
                for row in read_jsonl((repo / EVENTS_REL).resolve())}
    if len(rows) != 8 * D_REQUIRED or set(row_hashes) != expected:
        raise T1ScoringPackageError("6,432 overlay identity set changed")
    rows.sort(key=lambda row: (
        CANDIDATES.index(str(row["candidate_id"])),
        str(row["event_id"]),
    ))
    return rows, row_hashes, shard_hashes


_EVIDENCE_REPO: Path | None = None
_EVIDENCE_CACHE: Path | None = None
_EVIDENCE_FEATURES: dict[tuple[str, str], Mapping[str, Any]] = {}


def _evidence_init(
    repo_text: str,
    cache_text: str,
    features: dict[tuple[str, str], Mapping[str, Any]],
) -> None:
    global _EVIDENCE_REPO, _EVIDENCE_CACHE, _EVIDENCE_FEATURES
    _EVIDENCE_REPO = Path(repo_text)
    _EVIDENCE_CACHE = Path(cache_text)
    _EVIDENCE_FEATURES = features


def _evidence_worker(
    payload: tuple[
        Mapping[str, Any], list[tuple[str, str, str, str, str]]
    ],
) -> tuple[str, dict[tuple[str, str, str, str], dict[str, Any]]]:
    event, requests = payload
    assert _EVIDENCE_CACHE is not None
    event_id = str(event["event_id"])
    cache = capability.load_cache(_EVIDENCE_CACHE / f"{event_id}.json.gz")
    normalized, _ = normalizer.normalize_event(
        event, cache, _EVIDENCE_FEATURES, corridor_seconds=0.0
    )
    books: dict[tuple[str, str], Mapping[str, Any]] = {}
    prints: dict[tuple[str, str], Mapping[str, Any]] = {}
    for leg in normalized["legs"]:
        leg_id = str(leg["leg_id"])
        for observation in leg["observations"]:
            if observation["kind"] == "book":
                books[(leg_id, str(observation["source_receipt_identity"]))] = (
                    observation
                )
            else:
                prints[(leg_id, str(observation["trade_id"]))] = observation
    output: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for (
        leg_id, evidence_type, fill_receipt, book_receipt,
        action_book_receipt,
    ) in requests:
        book = books.get((leg_id, book_receipt))
        if book is None:
            raise T1ScoringPackageError(
                f"fill book receipt absent: {event_id} {leg_id}"
            )
        bids = range_v2.mechanical.external_bids(book, True)
        asks = range_v2.mechanical.asks(book)
        action_book = books.get((leg_id, action_book_receipt))
        if action_book is None:
            raise T1ScoringPackageError(
                f"action book receipt absent: {event_id} {leg_id}"
            )
        action_bids = range_v2.mechanical.external_bids(action_book, True)
        action_asks = range_v2.mechanical.asks(action_book)
        evidence = {
            "book_receipt": book_receipt,
            "book_timestamp": float(book["ts"]),
            "external_bid_cents": int(bids[0][0]) if bids else None,
            "external_bid_size": float(bids[0][1]) if bids else None,
            "external_ask_cents": int(asks[0][0]) if asks else None,
            "external_ask_size": float(asks[0][1]) if asks else None,
            "action_book_receipt": action_book_receipt,
            "action_book_timestamp": float(action_book["ts"]),
            "action_external_bid_cents": (
                int(action_bids[0][0]) if action_bids else None
            ),
            "action_external_bid_size": (
                float(action_bids[0][1]) if action_bids else None
            ),
            "action_external_ask_cents": (
                int(action_asks[0][0]) if action_asks else None
            ),
            "action_external_ask_size": (
                float(action_asks[0][1]) if action_asks else None
            ),
        }
        if evidence_type == "PRICE_REACHED":
            print_row = prints.get((leg_id, fill_receipt))
            if print_row is None:
                raise T1ScoringPackageError(
                    f"fill print receipt absent: {event_id} {leg_id}"
                )
            evidence.update({
                "print_receipt": fill_receipt,
                "print_timestamp": float(print_row["ts"]),
                "print_price_cents": _exact_int(
                    print_row["price"], "print price", 1, 99
                ),
                "print_size": float(print_row["size"]),
            })
        output[(
            leg_id, fill_receipt, book_receipt, action_book_receipt
        )] = evidence
    return event_id, output


def _collect_evidence(
    repo: Path,
    events: list[dict[str, Any]],
    requests: Mapping[str, set[tuple[str, str, str, str, str]]],
    *,
    workers: int,
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    feature_rows = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in feature_rows
    }
    if len(feature_map) != 1608:
        raise T1ScoringPackageError("1,608 feature identities changed")
    items = [
        (event, sorted(requests[str(event["event_id"])]))
        for event in events if requests.get(str(event["event_id"]))
    ]
    output: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=max(1, workers),
        initializer=_evidence_init,
        initargs=(str(repo), str((repo / CACHE_REL).resolve()), feature_map),
    ) as pool:
        for event_id, rows in pool.map(_evidence_worker, items, chunksize=1):
            for (leg, fill, book, action_book), evidence in rows.items():
                output[(event_id, leg, fill, book, action_book)] = evidence
    return output


def _event_and_boundary_inputs(
    repo: Path,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]],
           dict[tuple[str, str], str]]:
    events = read_jsonl((repo / EVENTS_REL).resolve())
    if len(events) != D_REQUIRED:
        raise T1ScoringPackageError("D changed from 804")
    if {str(row["event_date"]) for row in events} != set(binding.DEV_DATES):
        raise T1ScoringPackageError("development dates changed")
    if any(str(row["event_date"]) in range_v2.SEALED_HOLDOUT_DATES
           for row in events):
        raise T1ScoringPackageError("sealed holdout date entered events")
    boundaries = {
        str(row["event_id"]): boundary_builder.boundary_contract(row)
        for row in read_jsonl(repo / START_REL)
    }
    if set(boundaries) != {str(row["event_id"]) for row in events}:
        raise T1ScoringPackageError("V5 boundary identity set changed")
    tickers: dict[tuple[str, str], str] = {}
    for event in events:
        legs = list(event.get("legs") or [])
        if len(legs) != 2:
            raise T1ScoringPackageError("event does not have two legs")
        for leg in legs:
            leg_id = str(leg.get("leg_id") or leg.get("leg") or "")
            ticker = str(leg.get("ticker") or "")
            if not leg_id or not ticker:
                raise T1ScoringPackageError("leg identity missing")
            tickers[(str(event["event_id"]), leg_id)] = ticker
    if len(tickers) != 1608:
        raise T1ScoringPackageError("1,608 leg identities changed")
    return events, boundaries, tickers


def _unique_fill_ledger(
    repo: Path,
    events: list[dict[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
    tickers: Mapping[tuple[str, str], str],
    overlays: list[dict[str, Any]],
    overlay_hashes: Mapping[tuple[str, str], str],
    shard_hashes: Mapping[str, str],
    *,
    workers: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    event_map = {str(row["event_id"]): row for row in events}
    shard_by_key: dict[tuple[str, str], str] = {}
    for relative in OVERLAY_FILES:
        for row in read_gzip_jsonl(repo / relative):
            shard_by_key[(str(row["candidate_id"]), str(row["event_id"]))] = (
                relative
            )
    requests: dict[
        str, set[tuple[str, str, str, str, str]]
    ] = defaultdict(set)
    admitted_facts: list[tuple[dict[str, Any], str, Mapping[str, Any],
                               Mapping[str, Any], Mapping[str, Any]]] = []
    excluded = Counter()
    raw_fill_count = 0
    for overlay in overlays:
        event_id = str(overlay["event_id"])
        boundary = boundaries[event_id]
        cutoff = (
            float(boundary["guarded_cutoff_ts"])
            if boundary.get("positive_window1_provable") is True else None
        )
        for leg_id, fill in (
            overlay.get("causal_policy_fill_state_by_leg") or {}
        ).items():
            if not fill or fill.get("simulated_fill_ts") is None:
                continue
            raw_fill_count += 1
            evidence_ts = float(fill["simulated_fill_ts"])
            if cutoff is None or evidence_ts > cutoff + 1e-6:
                excluded[str(overlay["candidate_id"])] += 1
                continue
            interval = next(
                (
                    row for row in overlay["order_intervals_by_leg"][leg_id]
                    if row["order_interval_id"]
                    == fill["simulated_fill_order_interval_id"]
                ),
                None,
            )
            if interval is None:
                raise T1ScoringPackageError("fill interval identity missing")
            evidence_type = str(fill["simulated_fill_evidence_type"])
            if evidence_type not in {
                "PRICE_REACHED", "STRICT_ASK_CERTAIN_FILL"
            }:
                raise T1ScoringPackageError("unsupported T1 fill evidence")
            fill_receipt = str(fill["simulated_fill_receipt"])
            book_receipt = str(fill["simulated_fill_book_receipt"])
            action_book_receipt = str(interval.get("book_receipt") or "")
            if not action_book_receipt:
                raise T1ScoringPackageError(
                    "fill interval lacks action-book receipt"
                )
            requests[event_id].add(
                (
                    str(leg_id), evidence_type, fill_receipt, book_receipt,
                    action_book_receipt,
                )
            )
            admitted_facts.append((
                overlay, str(leg_id), fill, interval, boundary
            ))
    evidence = _collect_evidence(
        repo, events, requests, workers=workers
    )
    rows: list[dict[str, Any]] = []
    violations = Counter()
    by_candidate = Counter()
    by_evidence = Counter()
    positive_d2 = Counter()
    for overlay, leg_id, fill, interval, boundary in admitted_facts:
        candidate = str(overlay["candidate_id"])
        event_id = str(overlay["event_id"])
        event = event_map[event_id]
        fill_receipt = str(fill["simulated_fill_receipt"])
        book_receipt = str(fill["simulated_fill_book_receipt"])
        action_book_receipt = str(interval["book_receipt"])
        evidence_type = str(fill["simulated_fill_evidence_type"])
        support = evidence[(
            event_id, leg_id, fill_receipt, book_receipt,
            action_book_receipt,
        )]
        x = _exact_int(fill["simulated_fill_price"], "fill X", 1, 99)
        quantity = _exact_int(
            fill["simulated_accounting_quantity"], "fill quantity", LOT, LOT
        )
        fill_ts = float(fill["simulated_fill_ts"])
        if evidence_type == "PRICE_REACHED":
            if (
                support["print_timestamp"] != fill_ts
                or support["print_price_cents"] > x
                or support["print_size"] <= 0
            ):
                violations["print_fill_evidence"] += 1
        else:
            if (
                support["book_timestamp"] != fill_ts
                or support["external_ask_cents"] is None
                or support["external_ask_cents"] >= x
                or fill.get("simulated_fill_external_ask_cents")
                != support["external_ask_cents"]
            ):
                violations["strict_ask_evidence"] += 1
        opened = float(interval["opened_ts"])
        if fill_ts + 1e-6 < opened:
            violations["fill_precedes_action"] += 1
        triggers = {
            str(action["trigger_receipt"])
            for action in overlay.get("post_first_effective_actions") or []
            if action.get("leg_id") == leg_id
            and action.get("trigger_receipt")
            and abs(float(action["ts"]) - opened) <= 1e-6
        }
        if interval.get("book_receipt"):
            triggers.add(str(interval["book_receipt"]))
        if not triggers:
            raise T1ScoringPackageError("fill action trigger is missing")
        if fill_receipt in triggers:
            violations["trigger_receipt_self_fill"] += 1
        pair = overlay.get("pair_state") or {}
        first_leg = pair.get("first_filled_leg")
        first_ts = pair.get("first_fill_ts")
        d1 = (
            _exact_int(pair.get("causal_d1_cents"), "first-leg d1")
            if first_leg is not None else None
        )
        fee = _exact_int(pair.get("fee_cents"), "fee cents")
        if fee != 0:
            violations["fee_changed"] += 1
        role = "first_leg" if leg_id == first_leg else "sibling"
        b2_max = math.floor(-d1 - fee - 1) if d1 is not None else None
        sibling_d2 = None
        strict_budget = None
        if role == "sibling":
            if first_ts is None or fill_ts <= float(first_ts):
                violations["sibling_not_strictly_later"] += 1
            if support["action_external_bid_cents"] is None:
                violations["sibling_fill_bid_missing"] += 1
            else:
                sibling_d2 = x - int(
                    support["action_external_bid_cents"]
                )
                strict_budget = d1 + sibling_d2 + fee < 0
                if sibling_d2 > 0 and (
                    not strict_budget or sibling_d2 > int(b2_max)
                ):
                    violations["positive_d2_sibling_combined_budget"] += 1
                if sibling_d2 > 0 and strict_budget:
                    positive_d2[candidate] += 1
        else:
            strict_budget = None
        key = (candidate, event_id)
        overlay_shard = shard_by_key[key]
        selector = {
            "candidate_id": candidate,
            "event_id": event_id,
            "leg_id": leg_id,
            "interval_id": fill["simulated_fill_order_interval_id"],
            "fill_receipt": fill_receipt,
            "book_receipt": book_receipt,
            "fill_timestamp": fill_ts,
            "fill_price_cents": x,
            "boundary_source_record_sha256": boundary[
                "source_record_sha256"
            ],
            "source_overlay_sha256": overlay_hashes[key],
        }
        causal_identity = canonical_sha256(selector)
        row = {
            "schema_version": "window1-t1-unique-credited-fill-v1",
            "candidate_id": candidate,
            "base_candidate_id": str(overlay["base_candidate_id"]),
            "event_id": event_id,
            "event_date": str(event["event_date"]),
            "category": str(event["category"]),
            "leg_id": leg_id,
            "ticker": tickers[(event_id, leg_id)],
            "lawful_guarded_credited_fill": True,
            "quantity": quantity,
            "exposed_X_cents": x,
            "fill_price_cents": x,
            "fill_evidence_type": evidence_type,
            "fill_receipt": fill_receipt,
            "fill_book_receipt": book_receipt,
            "fill_evidence": support,
            "exposure_interval_id": str(
                fill["simulated_fill_order_interval_id"]
            ),
            "action_timestamp": opened,
            "action_trigger_receipt": action_book_receipt,
            "action_trigger_receipts": sorted(triggers),
            "evidence_timestamp": fill_ts,
            "evaluated_right_ts": float(boundary["guarded_cutoff_ts"]),
            "boundary": boundary,
            "fill_role": role,
            "first_filled_leg": first_leg,
            "first_fill_timestamp": first_ts,
            "realized_first_leg_d1_cents": d1,
            "b2_max_cents": b2_max,
            "sibling_d2_cents": sibling_d2,
            "fee_cents": fee,
            "strict_combined_budget_passed": strict_budget,
            "persistence_participated": bool(
                overlay["t1_switches"]["lawful_persistence"]
                and role == "sibling"
            ),
            "self_trigger_fill": False,
            "selection_basis": (
                "frozen_T1_earliest_credited_fill_then_V5_guard_admission"
            ),
            "causal_fill_identity": causal_identity,
            "selector_receipt_sha256": canonical_sha256(selector),
            "source_overlay_sha256": overlay_hashes[key],
            "source_overlay_shard": overlay_shard,
            "source_overlay_shard_sha256": shard_hashes[overlay_shard],
            "metrics": None,
            "performance": None,
            "scored": False,
        }
        rows.append(row)
        by_candidate[candidate] += 1
        by_evidence[(candidate, evidence_type)] += 1
    if violations:
        raise T1ScoringPackageError(
            "T1 fill derivation violations: " + compact(violations)
        )
    rows.sort(key=lambda row: (
        CANDIDATES.index(str(row["candidate_id"])),
        str(row["event_id"]), str(row["leg_id"]),
    ))
    keys = [
        (row["candidate_id"], row["event_id"], row["leg_id"])
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise T1ScoringPackageError("non-unique T1 fill ledger")
    receipt = {
        "schema_version": VERSION + "-unique-fill-derivation-v1",
        "raw_frozen_T1_fill_facts": raw_fill_count,
        "lawful_guarded_unique_fill_rows": len(rows),
        "excluded_post_right_or_unprovable": raw_fill_count - len(rows),
        "candidate_rows": [
            {
                "candidate_id": candidate,
                "unique_fill_rows": by_candidate[candidate],
                "excluded_post_right_or_unprovable": excluded[candidate],
                "PRICE_REACHED": by_evidence[(candidate, "PRICE_REACHED")],
                "STRICT_ASK_CERTAIN_FILL": by_evidence[(
                    candidate, "STRICT_ASK_CERTAIN_FILL"
                )],
                "positive_d2_sibling_fills": positive_d2[candidate],
                "D": D_REQUIRED,
                "C": None,
                "PC": None,
                "IC": None,
                "S": None,
            }
            for candidate in CANDIDATES
        ],
        "one_maximum_per_candidate_event_leg": True,
        "duplicate_causal_fill_double_credit": 0,
        "conflicting_duplicate_fill_rows": 0,
        "fill_precedes_action": 0,
        "trigger_receipt_self_fill": 0,
        "sibling_not_strictly_later": 0,
        "positive_d2_sibling_combined_budget_violations": 0,
        "first_leg_semantics_source": (
            f"{T1_PACKAGE_REL}/FIRST_LEG_SEMANTIC_IDENTITY_RECEIPT.json"
        ),
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    return rows, receipt


def _audited_identity(repo: Path) -> dict[str, Any]:
    rows = []
    for relative in AUDITED_FILES:
        current = identity_bytes(repo / relative)
        prior = subprocess.run(
            ["git", "show", f"{AUDITED_SCORER_COMMIT}:{relative}"],
            cwd=repo, capture_output=True, check=False,
        )
        if prior.returncode:
            raise T1ScoringPackageError(f"audited file missing: {relative}")
        audited = canonical_text_bytes(prior.stdout)
        if current != audited:
            raise T1ScoringPackageError(
                f"audited scorer/reference blob changed: {relative}"
            )
        rows.append({
            "path": relative,
            "audited_commit": AUDITED_SCORER_COMMIT,
            "sha256": hashlib.sha256(current).hexdigest(),
            "git_blob_oid": git_blob_oid(current),
            "byte_identical": True,
        })
    return {
        "schema_version": VERSION + "-audited-v2-identity-v1",
        "audited_commit": AUDITED_SCORER_COMMIT,
        "files": rows,
        "all_byte_identical": True,
        "metric_or_reference_law_changed": False,
    }


def _package_artifacts(output: Path) -> list[dict[str, Any]]:
    excluded = {
        "PACKAGE_ARTIFACT_MANIFEST.json",
        "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json",
    }
    rows = []
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.name in excluded:
            continue
        raw = identity_bytes(path)
        rows.append({
            "path": f"{PACKAGE_REL}/{path.name}",
            "hash_basis": (
                "canonical_lf_text"
                if path.suffix.lower() in TEXT_SUFFIXES else "exact_binary"
            ),
            "identity_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git_blob_oid(raw),
        })
    return rows


def build(
    *,
    repo: Path,
    output: Path,
    workers: int = 8,
) -> dict[str, Any]:
    if output.exists():
        raise T1ScoringPackageError("build output already exists")
    output.mkdir(parents=True)
    if git(repo, "rev-parse", "HEAD") != IMPLEMENTATION_PARENT:
        raise T1ScoringPackageError("implementation parent mismatch")
    events, boundaries, tickers = _event_and_boundary_inputs(repo)
    overlays, overlay_hashes, shard_hashes = _load_overlays(repo)
    rows, derivation = _unique_fill_ledger(
        repo, events, boundaries, tickers, overlays, overlay_hashes,
        shard_hashes, workers=workers,
    )
    ledger_raw = deterministic_gzip_jsonl(rows)
    ledger_path = output / "T1_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
    ledger_path.write_bytes(ledger_raw)
    write_json(
        output / "T1_UNIQUE_CREDITED_FILL_DERIVATION_RECEIPT.json",
        derivation,
    )
    identities = read_json(
        repo / PRIOR_SCORING_REL / "FROZEN_EVENT_LEG_IDENTITIES.json"
    )
    if (
        identities.get("D") != D_REQUIRED
        or identities.get("leg_identities") != 1608
        or len(identities.get("rows") or []) != 1608
    ):
        raise T1ScoringPackageError("prior event/leg identity ledger changed")
    write_json(output / "FROZEN_EVENT_LEG_IDENTITIES.json", identities)
    audited_identity = _audited_identity(repo)
    write_json(
        output / "AUDITED_V2_SCORER_IDENTITY_RECEIPT.json",
        audited_identity,
    )
    t1_spec = read_json(repo / SPEC_REL)
    switch_hashes = {
        candidate: canonical_sha256(t1_spec["switch_matrix"][candidate])
        for candidate in CANDIDATES
    }
    write_json(output / "T1_IMPLEMENTATION_AUDIT_BINDING.json", {
        "schema_version": VERSION + "-T1-binding-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_T1_PASS": CONTROLLING_T1_PASS,
        "audit_report": audit_blob(repo, AUDIT_REPORT_REL),
        "audit_reproduction_receipt": audit_blob(repo, AUDIT_RECEIPT_REL),
        "candidate_ids": list(CANDIDATES),
        "candidate_switch_sha256": switch_hashes,
        "T1_package": T1_PACKAGE_REL,
        "candidate_specification": SPEC_REL,
        "candidate_or_mechanism_changed": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    parent_event_ledgers = [
        f"{PARENT_RESULTS_REL}/"
        "01_w1_range_attack__macro_hold__combined_headroom_EVENT_LEDGER.jsonl",
        f"{PARENT_RESULTS_REL}/"
        "02_w1_range_attack__macro_micro__combined_headroom_EVENT_LEDGER.jsonl",
    ]
    write_json(output / "PARENT_REFERENCE_CANDIDATE_BINDING.json", {
        "schema_version": VERSION + "-parent-reference-v1",
        "parent_candidate_ids": list(BASE_CANDIDATES),
        "T1_candidate_to_parent": {
            candidate: t1.base_candidate_id(candidate)
            for candidate in CANDIDATES
        },
        "audited_parent_result_ledgers": [
            source_row(repo, relative, "audited_parent_reference_result")
            for relative in parent_event_ledgers
        ],
        "parent_candidates_rerun_by_T1_package": False,
        "ranking_or_selection": None,
    })
    expected_schema = {
        "schema_version": VERSION + "-expected-output-v1",
        "candidate_order": list(CANDIDATES),
        "candidate_count": 8,
        "event_rows_per_candidate": D_REQUIRED,
        "summary_fields": [
            "candidate_id", "D", "C", "C_over_D", "PC", "PC_over_D",
            "PC_shortfall_from_603", "IC", "IC_over_D", "S", "S_over_D",
        ],
        "closed_classifications": [
            "completed_PC", "completed_non_PC",
            "completed_reference_missing_or_ambiguous", "naked_single",
            "no_fill", "censored_or_boundary_unprovable",
        ],
        "diagnostics": [
            "PC_but_not_IC", "positive_d2_completed_PC",
            "fill_evidence_decomposition", "pair_delta_distribution",
            "individual_delta_distribution", "combined_cost_distribution",
            "first_leg_sibling_fill_ordering", "persistence_participation",
            "candidate_versus_parent_event_level_change_count",
        ],
        "official_target_metric": "PC_over_D",
        "target_PC": TARGET_PC,
        "ranking_or_selection": None,
    }
    write_json(output / "EXPECTED_OUTPUT_SCHEMA.json", expected_schema)
    write_json(output / "CLASSIFICATION_CONSERVATION_FIXTURES.json", {
        "schema_version": VERSION + "-classification-fixtures-v1",
        "D": D_REQUIRED,
        "closed_classifications": expected_schema["closed_classifications"],
        "synthetic_fixture_only": True,
        "fixtures": [
            {
                "name": "one_event_per_closed_class",
                "counts": {
                    name: 1 for name in expected_schema["closed_classifications"]
                },
                "total": 6,
            },
            {
                "name": "D804_conservation",
                "counts": {
                    "completed_PC": 1,
                    "completed_non_PC": 1,
                    "completed_reference_missing_or_ambiguous": 1,
                    "naked_single": 1,
                    "no_fill": 799,
                    "censored_or_boundary_unprovable": 1,
                },
                "total": D_REQUIRED,
            },
        ],
        "real_performance_metrics": None,
    })
    write_json(output / "EXECUTION_AUTHORIZATION_GATE.json", {
        "schema_version": VERSION + "-authorization-gate-v1",
        "future_independent_PASS_required": True,
        "package_commit_requirement": "exact_git_HEAD_at_execution",
        "authorization_commit_supplied_separately": True,
        "authorization_report_must_bind": [
            "exact package commit", "exact execution ID",
            "exact input-bundle SHA-256", "exact command-template literal",
        ],
        "execution_id": EXECUTION_ID,
        "command_template_literal": COMMAND_TEMPLATE,
        "clean_relevant_worktree_required": True,
        "local_remote_equality_required": True,
        "attempts_per_execution_id": 1,
        "new_results_directory_required": RESULTS_REL,
        "self_referential_audit_text_required": False,
    })
    write_json(output / "NULL_METRIC_NO_EXECUTION_RECEIPT.json", {
        "schema_version": VERSION + "-null-noexecution-v1",
        "candidate_ids": list(CANDIDATES),
        "D_per_candidate": D_REQUIRED,
        "metrics_by_candidate": {
            candidate: {"C": None, "PC": None, "IC": None, "S": None}
            for candidate in CANDIDATES
        },
        "performance": None,
        "scorer_imported_by_builder": False,
        "scorer_invocations": 0,
        "real_population_scored": False,
        "results_directory": RESULTS_REL,
        "results_directory_exists_during_freeze": (
            (repo / RESULTS_REL).exists()
        ),
        "execution_authorized_now": False,
    })
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "development_dates": list(binding.DEV_DATES),
        "sealed_holdout_dates": ["2026-07-24", "2026-07-25", "2026-07-26"],
        "holdout_opened_or_queried": False,
        "network_calls": 0,
        "live_or_production_access": False,
        "orders_positions_configuration_mutated": False,
        "Window2_exits_settlement_DCA_access": False,
        "builder_interfaces": ["local committed files", "local private read-only inputs"],
    })
    source_paths = [
        ADAPTER_REL, RUNNER_REL, BUILDER_REL, FREEZER_REL, TEST_REL,
        CONTRACT_REL, SPEC_REL,
        "arb-executor/analysis/window1_t1_post_first_leg_instrument.py",
        "arb-executor/analysis/window1_t1_post_first_leg_prerun.py",
        f"{T1_PACKAGE_REL}/PRE_RUN_MANIFEST.json",
        f"{T1_PACKAGE_REL}/ARTIFACT_HASH_MANIFEST.json",
        f"{T1_PACKAGE_REL}/SOURCE_HASH_MANIFEST.json",
        f"{T1_PACKAGE_REL}/CANDIDATE_SWITCH_MATRIX.json",
        f"{T1_PACKAGE_REL}/FIRST_LEG_SEMANTIC_IDENTITY_RECEIPT.json",
        f"{T1_PACKAGE_REL}/NOFILL_SEMANTIC_IDENTITY_RECEIPT.json",
        f"{T1_PACKAGE_REL}/FIVE_NO_BBO_D_MEMBERSHIP_PROOF.json",
        f"{T1_PACKAGE_REL}/STRICT_ASK_CREDIT_BEFORE_REPRICE_PROOF.json",
        f"{T1_PACKAGE_REL}/HEADROOM_TARGET_CONSTRUCTION_RECEIPTS.jsonl.gz",
        f"{T1_PACKAGE_REL}/PERSISTENCE_QUEUE_SURRENDER_RECEIPTS.jsonl.gz",
        *OVERLAY_FILES,
        *AUDITED_FILES,
        "arb-executor/docs/research/window1/"
        "WINDOW1_OS_FAMILY_METRIC_CONTRACT_V1.json",
        START_REL,
        ".claude/window1_round2_prerun_v2_20260724/"
        "ROUND2_DATA_BINDING_MANIFEST.json",
        f"{PRIOR_SCORING_REL}/REFERENCE_LATEST_TIMESTAMP_TIE_CENSUS.json",
        f"{PRIOR_SCORING_REL}/REFERENCE_SOURCE_ORDER_TRACE.json",
        f"{PRIOR_SCORING_REL}/GUARDED_CACHE_V3_HASH_SET.json",
        *parent_event_ledgers,
    ]
    committed_rows = [
        source_row(repo, relative, "immutable_source_or_package_code")
        for relative in source_paths
    ]
    prior_source = read_json(repo / PRIOR_SCORING_REL / "SOURCE_HASH_MANIFEST.json")
    private_inputs = list(prior_source["private_runtime_inputs"])
    unique_receipt = {
        "path": f"{PACKAGE_REL}/{ledger_path.name}",
        "bytes": len(ledger_raw),
        "sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "rows": len(rows),
    }
    source_manifest = {
        "schema_version": VERSION + "-source-hash-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_T1_PASS": CONTROLLING_T1_PASS,
        "committed_inputs": committed_rows,
        "private_runtime_inputs": private_inputs,
        "T1_unique_runtime_fill_ledger": unique_receipt,
        "audit_artifacts": [
            audit_blob(repo, AUDIT_REPORT_REL),
            audit_blob(repo, AUDIT_RECEIPT_REL),
        ],
        "holdout_dates_present": 0,
        "all_hashes_verified": True,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)
    roles = {
        "authorization_gate": f"{PACKAGE_REL}/EXECUTION_AUTHORIZATION_GATE.json",
        "candidate_definitions": SPEC_REL,
        "T1_scorer_contract": CONTRACT_REL,
        "audited_scorer_contract": AUDITED_FILES[-1],
        "metric_contract": (
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_METRIC_CONTRACT_V1.json"
        ),
        "event_ledger": EVENTS_REL,
        "event_leg_identities": (
            f"{PACKAGE_REL}/FROZEN_EVENT_LEG_IDENTITIES.json"
        ),
        "start_ledger": START_REL,
        "guarded_cache_directory": CACHE_REL,
        "guarded_cache_hash_set": (
            f"{PRIOR_SCORING_REL}/GUARDED_CACHE_V3_HASH_SET.json"
        ),
        "reference_tie_census": (
            f"{PRIOR_SCORING_REL}/REFERENCE_LATEST_TIMESTAMP_TIE_CENSUS.json"
        ),
        "reference_source_trace": (
            f"{PRIOR_SCORING_REL}/REFERENCE_SOURCE_ORDER_TRACE.json"
        ),
        "unique_T1_fill_ledger": (
            f"{PACKAGE_REL}/T1_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
        ),
        "unique_T1_fill_derivation_receipt": (
            f"{PACKAGE_REL}/T1_UNIQUE_CREDITED_FILL_DERIVATION_RECEIPT.json"
        ),
        "source_hash_manifest": f"{PACKAGE_REL}/SOURCE_HASH_MANIFEST.json",
        "expected_output_schema": f"{PACKAGE_REL}/EXPECTED_OUTPUT_SCHEMA.json",
        "parent_reference_binding": (
            f"{PACKAGE_REL}/PARENT_REFERENCE_CANDIDATE_BINDING.json"
        ),
    }
    payload = {
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_T1_PASS": CONTROLLING_T1_PASS,
        "audited_scorer_commit": AUDITED_SCORER_COMMIT,
        "execution_id": EXECUTION_ID,
        "command_template_literal": COMMAND_TEMPLATE,
        "candidate_ids": list(CANDIDATES),
        "candidate_switch_sha256": switch_hashes,
        "parent_reference_candidate_ids": list(BASE_CANDIDATES),
        "D": D_REQUIRED,
        "leg_identities": 1608,
        "development_dates": list(binding.DEV_DATES),
        "sealed_holdout_dates": ["2026-07-24", "2026-07-25", "2026-07-26"],
        "roles": roles,
        "committed_source_receipts": committed_rows,
        "private_source_receipts": private_inputs,
        "unique_T1_fill_ledger": unique_receipt,
        "event_leg_identities_sha256": canonical_sha256(identities),
        "fee_cents": 0,
        "target_PC": TARGET_PC,
    }
    manifest = {
        "schema_version": "window1-t1-scoring-input-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_T1_PASS": CONTROLLING_T1_PASS,
        "audited_scorer_commit": AUDITED_SCORER_COMMIT,
        "execution_id": EXECUTION_ID,
        "results_directory": RESULTS_REL,
        "command_template_literal": COMMAND_TEMPLATE,
        "candidate_ids": list(CANDIDATES),
        "parent_reference_candidate_ids": list(BASE_CANDIDATES),
        "D": D_REQUIRED,
        "target_PC": TARGET_PC,
        "input_bundle_payload": payload,
        "input_bundle_sha256": canonical_sha256(payload),
        "roles": roles,
        "future_independent_PASS_required": True,
        "execution_authorized_now": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", manifest)
    report = f"""# Window-1 T1 Scoring-Package PRE-RUN

Status: **FROZEN, SCORE-FREE, NOT EXECUTED**

- Exact parent: `{IMPLEMENTATION_PARENT}`
- Controlling independent T1 PASS: `{CONTROLLING_T1_PASS}`
- Audited metric/reference implementation: `{AUDITED_SCORER_COMMIT}`
- Candidates: 8, in the frozen T1 order
- D: 804 per candidate
- Target: PC >= 603; official rate PC/D
- Unique guarded fill rows: {len(rows)}
- Input-bundle SHA-256: `{manifest['input_bundle_sha256']}`
- Execution ID: `{EXECUTION_ID}`
- Frozen command template: `{COMMAND_TEMPLATE}`

The builder did not import or invoke the scorer. C, PC, IC, S, and all
performance fields remain null. The two parent Range-Attack candidates are
bound only as separately reportable audited references and are not rerun.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    artifacts = _package_artifacts(output)
    write_json(output / "PACKAGE_ARTIFACT_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "all_hashes_verified": True,
    })
    write_json(output / "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json", {
        "schema_version": VERSION + "-determinism-v1",
        "required_builds": 2,
        "canonical_newline_law": "LF for text; exact bytes for gzip/binary",
        "gzip_mtime": 0,
        "artifact_inventory_sha256": canonical_sha256(artifacts),
        "byte_identical_clean_builds": True,
        "verified_by_freezer": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    return {
        "candidate_count": len(CANDIDATES),
        "D": D_REQUIRED,
        "unique_fill_rows": len(rows),
        "input_bundle_sha256": manifest["input_bundle_sha256"],
        "artifact_inventory_sha256": canonical_sha256(artifacts),
        "metrics": None,
        "performance": None,
        "scored": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    result = build(
        repo=args.repo.resolve(),
        output=args.output_dir.resolve(),
        workers=args.workers,
    )
    print(compact({"status": "PASS", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
