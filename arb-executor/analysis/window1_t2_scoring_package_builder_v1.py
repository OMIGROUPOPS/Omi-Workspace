#!/usr/bin/env python3
"""Build the score-free Window-1 T2 scoring-package PRE-RUN.

Construction is allowed to read the frozen T2 overlays and guarded
development inputs only to freeze unique runtime facts.  It never imports or
invokes a scorer.  Runtime scoring cannot reread raw candidate streams.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_t1_scoring_package_builder_v1 as t1pkg
import window1_t2_causal_divot_instrument as t2


VERSION = "window1-t2-scoring-package-builder-v1"
IMPLEMENTATION_PARENT = "87ac9382c23b586f536cf457883c507ebf366ba3"
CONTROLLING_T2_PASS = "8743939745e25f090d69dfd4d56906a93671f331"
AUDITED_SCORER_COMMIT = "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
PACKAGE_REL = ".claude/window1_t2_scoring_package_prerun_20260728"
T2_PACKAGE_REL = ".claude/window1_t2_causal_divot_prerun_20260727"
BASELINE_REL = (
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
)
PRIOR_SCORING_REL = (
    ".claude/window1_range_attack_scoring_package_v2_prerun_20260726"
)
EVENTS_REL = "../OMI-Window1-private/joined/events.jsonl"
CACHE_REL = "../OMI-Window1-private/fit-local/guarded-cache-v3"
START_REL = (
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
SPEC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_CAUSAL_DIVOT_CANDIDATES_V1.json"
)
CONTRACT_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_FRONTIER_REGRET_CONTRACT_V1.json"
)
ADAPTER_REL = "arb-executor/analysis/window1_t2_scoring_adapter_v1.py"
SCORER_REL = (
    "arb-executor/analysis/window1_t2_frontier_regret_scorer_v1.py"
)
RUNNER_REL = "arb-executor/analysis/window1_t2_scoring_runner_v1.py"
BUILDER_REL = (
    "arb-executor/analysis/window1_t2_scoring_package_builder_v1.py"
)
FREEZER_REL = (
    "arb-executor/analysis/window1_t2_scoring_package_freeze_v1.py"
)
TEST_REL = "arb-executor/tests/test_window1_t2_scoring_package_v1.py"
AUDIT_REPORT_REL = (
    ".claude/audit_20260728_window1_t2_causal_divot_prerun/"
    "AUDIT_REPORT.md"
)
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v1"
)
RESULTS_REL = f".claude/window1_t2_results_{EXECUTION_ID}"
MANIFEST_REL = f"{PACKAGE_REL}/SCORING_INPUT_MANIFEST.json"
COMMAND_TEMPLATE = (
    f"python -B {RUNNER_REL} --repo . --package {MANIFEST_REL} "
    "--mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
D_REQUIRED = 804
LOT = 5
FIT_DATES = frozenset(f"2026-07-{day:02d}" for day in range(12, 18))
POST_FIT_DATES = frozenset(f"2026-07-{day:02d}" for day in range(18, 21))
DEV_DATES = FIT_DATES | POST_FIT_DATES
SEALED_DATES = frozenset(f"2026-07-{day:02d}" for day in range(24, 27))
CANDIDATES = t2.CANDIDATES
BASE_CANDIDATES = t2.BASE_CANDIDATES
CONTROL_CANDIDATES = frozenset(
    candidate for candidate in CANDIDATES
    if candidate.endswith("__fixed_admission_parent_control")
)
OVERLAY_FILES = tuple(
    f"{T2_PACKAGE_REL}/UNSCORED_T2_CANDIDATE_EVENT_OVERLAYS_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
BASE_STREAM_FILES = tuple(
    f"{BASELINE_REL}/UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
RANGE_LADDER_FILES = tuple(
    f"{BASELINE_REL}/WINDOW1_PRICE_RANGE_LADDER_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
AUDITED_FILES = (
    "arb-executor/analysis/window1_range_attack_scorer_v2.py",
    "arb-executor/analysis/window1_range_attack_reference_adapter_v2.py",
    "arb-executor/analysis/window1_range_attack_guarded_fill_adapter_v2.py",
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_SCORER_CONTRACT_V2.json",
)
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}


class T2PackageError(RuntimeError):
    """A frozen input, chronology, oracle, or conservation gate failed."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def canonical_text(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def identity_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return canonical_text(raw) if path.suffix.lower() in TEXT_SUFFIXES else raw


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
        raise T2PackageError(
            f"git {' '.join(args)} failed: "
            + process.stderr.decode(errors="replace").strip()
        )
    return process.stdout.decode("utf-8", errors="strict").strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value))


def gzip_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as gz:
        with io.TextIOWrapper(gz, encoding="utf-8", newline="\n") as text:
            for row in rows:
                text.write(compact(row) + "\n")
    return buffer.getvalue()


def jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(compact(row) + "\n" for row in rows).encode("utf-8")


def exact_int(
    value: Any,
    field: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool):
        raise T2PackageError(f"{field} is boolean")
    if isinstance(value, int):
        result = value
    elif isinstance(value, float) and math.isfinite(value) and value.is_integer():
        result = int(value)
    else:
        raise T2PackageError(f"{field} is not exact integer")
    if minimum is not None and result < minimum:
        raise T2PackageError(f"{field} below {minimum}")
    if maximum is not None and result > maximum:
        raise T2PackageError(f"{field} above {maximum}")
    return result


def source_row(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = (repo / relative).resolve()
    raw = identity_bytes(path)
    try:
        oid = git(repo, "rev-parse", f"HEAD:{relative}")
    except T2PackageError:
        oid = git_blob_oid(raw)
    return {
        "path": relative,
        "role": role,
        "hash_basis": (
            "canonical_lf_text"
            if path.suffix.lower() in TEXT_SUFFIXES else "exact_binary"
        ),
        "identity_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_oid": oid,
    }


def binary_source_row(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = repo / relative
    return {
        "path": relative,
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "git_blob_oid": git(repo, "rev-parse", f"HEAD:{relative}"),
    }


def audit_blob(repo: Path) -> dict[str, Any]:
    process = subprocess.run(
        ["git", "show", f"{CONTROLLING_T2_PASS}:{AUDIT_REPORT_REL}"],
        cwd=repo, capture_output=True, check=False,
    )
    if process.returncode:
        raise T2PackageError("controlling T2 audit report is missing")
    raw = process.stdout
    return {
        "audit_commit": CONTROLLING_T2_PASS,
        "path": AUDIT_REPORT_REL,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_oid": git(
            repo, "rev-parse", f"{CONTROLLING_T2_PASS}:{AUDIT_REPORT_REL}"
        ),
    }


def _candidate_parent(candidate: str) -> str:
    return BASE_CANDIDATES[0 if "__macro_hold__" in candidate else 1]


def _load_events(
    repo: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[tuple[str, str], str],
]:
    events, boundaries, tickers = t1pkg._event_and_boundary_inputs(repo)
    dates = Counter(str(row["event_date"]) for row in events)
    if set(dates) != DEV_DATES or sum(dates.values()) != D_REQUIRED:
        raise T2PackageError("development population changed")
    if sum(dates[date] for date in FIT_DATES) != 525:
        raise T2PackageError("fit slice changed")
    if sum(dates[date] for date in POST_FIT_DATES) != 279:
        raise T2PackageError("post-fit slice changed")
    if any(str(row["event_date"]) in SEALED_DATES for row in events):
        raise T2PackageError("sealed holdout entered event ledger")
    return events, boundaries, tickers


def _load_overlays(
    repo: Path,
) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], str],
    dict[str, str],
]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    shards: dict[tuple[str, str], str] = {}
    hashes: dict[str, str] = {}
    for relative in OVERLAY_FILES:
        hashes[relative] = sha256_file(repo / relative)
        for row in iter_gzip(repo / relative):
            if (
                row.get("scored") is not False
                or row.get("metrics") is not None
                or row.get("performance") is not None
                or any(row.get(field) is not None for field in ("C", "PC", "IC", "S"))
            ):
                raise T2PackageError("performance entered T2 overlay")
            key = (str(row["candidate_id"]), str(row["event_id"]))
            if key in rows:
                raise T2PackageError("duplicate T2 candidate/event overlay")
            rows[key] = row
            shards[key] = relative
    if len(rows) != len(CANDIDATES) * D_REQUIRED:
        raise T2PackageError("T2 overlay count differs from 6,432")
    return rows, shards, hashes


def _load_baselines(
    repo: Path,
) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], str],
    dict[str, str],
]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    shards: dict[tuple[str, str], str] = {}
    hashes: dict[str, str] = {}
    for relative in BASE_STREAM_FILES:
        hashes[relative] = sha256_file(repo / relative)
        for envelope in iter_gzip(repo / relative):
            key = (str(envelope["candidate_id"]), str(envelope["event_id"]))
            if key in rows:
                raise T2PackageError("duplicate baseline stream")
            rows[key] = envelope
            shards[key] = relative
    if len(rows) != len(BASE_CANDIDATES) * D_REQUIRED:
        raise T2PackageError("baseline stream identity set changed")
    return rows, shards, hashes


def _materialized(
    candidate: str,
    event_id: str,
    overlays: Mapping[tuple[str, str], Mapping[str, Any]],
    overlay_shards: Mapping[tuple[str, str], str],
    overlay_hashes: Mapping[str, str],
    baselines: Mapping[tuple[str, str], Mapping[str, Any]],
    baseline_shards: Mapping[tuple[str, str], str],
    baseline_hashes: Mapping[str, str],
) -> dict[str, Any]:
    if candidate in CONTROL_CANDIDATES:
        parent = _candidate_parent(candidate)
        envelope = baselines[(parent, event_id)]
        stream = envelope["stream"]
        relative = baseline_shards[(parent, event_id)]
        return {
            "candidate_id": candidate,
            "base_candidate_id": parent,
            "event_id": event_id,
            "event_date": envelope["event_date"],
            "category": envelope["category"],
            "pair_state": stream["pair_state"],
            "fills": stream.get("causal_policy_fill_state_by_leg") or {},
            "intervals": stream["order_intervals_by_leg"],
            "evidence_census": stream.get("evidence_census_by_leg") or [],
            "source_path": relative,
            "source_shard_sha256": baseline_hashes[relative],
            "source_stream_sha256": canonical_sha256(envelope),
            "source_kind": "fixed_admission_parent_control",
        }
    overlay = overlays[(candidate, event_id)]
    relative = overlay_shards[(candidate, event_id)]
    base_stream = baselines[
        (str(overlay["base_candidate_id"]), event_id)
    ]["stream"]
    return {
        "candidate_id": candidate,
        "base_candidate_id": overlay["base_candidate_id"],
        "event_id": event_id,
        "event_date": overlay["event_date"],
        "category": overlay["category"],
        "pair_state": overlay["pair_state"],
        "fills": overlay.get("causal_policy_fill_state_by_leg") or {},
        "intervals": overlay.get("order_intervals_by_leg") or {},
        "evidence_census": (
            base_stream.get("evidence_census_by_leg") or []
        ),
        "source_path": relative,
        "source_shard_sha256": overlay_hashes[relative],
        "source_stream_sha256": canonical_sha256(overlay),
        "source_kind": "T2_overlay",
    }


def _derive_unique_fills(
    repo: Path,
    events: list[dict[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
    tickers: Mapping[tuple[str, str], str],
    records: Mapping[tuple[str, str], Mapping[str, Any]],
    *,
    workers: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    event_map = {str(row["event_id"]): row for row in events}
    admitted = []
    requests: dict[str, set[tuple[str, str, str, str, str]]] = defaultdict(set)
    raw = Counter()
    excluded = Counter()
    for (candidate, event_id), record in records.items():
        boundary = boundaries[event_id]
        cutoff = (
            float(boundary["guarded_cutoff_ts"])
            if boundary.get("positive_window1_provable") is True else None
        )
        for leg_id, fill in record["fills"].items():
            if not fill or fill.get("simulated_fill_ts") is None:
                continue
            raw[candidate] += 1
            fill_ts = float(fill["simulated_fill_ts"])
            if cutoff is None or fill_ts > cutoff + 1e-6:
                excluded[candidate] += 1
                continue
            intervals = record["intervals"].get(leg_id) or []
            interval = next(
                (
                    row for row in intervals
                    if row["order_interval_id"]
                    == fill["simulated_fill_order_interval_id"]
                ),
                None,
            )
            if interval is None:
                raise T2PackageError("fill interval identity missing")
            evidence_type = str(fill["simulated_fill_evidence_type"])
            if evidence_type not in {
                "PRICE_REACHED", "STRICT_ASK_CERTAIN_FILL"
            }:
                raise T2PackageError("unsupported T2 fill evidence")
            fill_receipt = str(fill["simulated_fill_receipt"])
            book_receipt = str(fill["simulated_fill_book_receipt"])
            action_book = str(interval.get("book_receipt") or "")
            if not action_book:
                raise T2PackageError("fill interval lacks action BBO receipt")
            requests[event_id].add((
                str(leg_id), evidence_type, fill_receipt,
                book_receipt, action_book,
            ))
            admitted.append((record, str(leg_id), fill, interval, boundary))
    evidence = t1pkg._collect_evidence(
        repo, events, requests, workers=workers
    )
    rows: list[dict[str, Any]] = []
    by_candidate = Counter()
    by_type = Counter()
    positive_d2 = Counter()
    for record, leg_id, fill, interval, boundary in admitted:
        candidate = str(record["candidate_id"])
        event_id = str(record["event_id"])
        event = event_map[event_id]
        fill_receipt = str(fill["simulated_fill_receipt"])
        book_receipt = str(fill["simulated_fill_book_receipt"])
        action_book = str(interval["book_receipt"])
        support = evidence[
            (event_id, leg_id, fill_receipt, book_receipt, action_book)
        ]
        evidence_type = str(fill["simulated_fill_evidence_type"])
        x = exact_int(fill["simulated_fill_price"], "fill X", 1, 99)
        quantity = exact_int(
            fill["simulated_accounting_quantity"], "quantity", LOT, LOT
        )
        fill_ts = float(fill["simulated_fill_ts"])
        if evidence_type == "PRICE_REACHED":
            if (
                support["print_timestamp"] != fill_ts
                or support["print_price_cents"] > x
                or support["print_size"] <= 0
            ):
                raise T2PackageError("print fill evidence mismatch")
        elif (
            support["book_timestamp"] != fill_ts
            or support["external_ask_cents"] is None
            or support["external_ask_cents"] >= x
        ):
            raise T2PackageError("strict-ask fill evidence mismatch")
        opened = float(interval["opened_ts"])
        if fill_ts < opened - 1e-6 or fill_receipt == action_book:
            raise T2PackageError("fill chronology or self-trigger violated")
        pair = record["pair_state"]
        first_leg = pair.get("first_filled_leg")
        first_ts = pair.get("first_fill_ts")
        d1 = (
            exact_int(pair.get("causal_d1_cents"), "d1")
            if first_leg is not None else None
        )
        fee = exact_int(pair.get("fee_cents"), "fee")
        if fee != 0:
            raise T2PackageError("fee treatment changed")
        role = "first_leg" if leg_id == first_leg else "sibling"
        b2_max = math.floor(-d1 - fee - 1) if d1 is not None else None
        d2 = None
        strict = None
        if role == "sibling":
            if first_ts is None or fill_ts <= float(first_ts):
                raise T2PackageError("sibling fill is not strictly later")
            bid = support.get("action_external_bid_cents")
            if bid is None:
                raise T2PackageError("sibling fill lacks action BBO")
            d2 = x - exact_int(bid, "action bid", 1, 99)
            strict = d1 + d2 + fee < 0
            if d2 > 0 and (not strict or d2 > int(b2_max)):
                raise T2PackageError(
                    "positive-d2 sibling fill violates combined headroom"
                )
            if d2 > 0:
                positive_d2[candidate] += 1
        selector = {
            "candidate_id": candidate,
            "event_id": event_id,
            "leg_id": leg_id,
            "interval_id": fill["simulated_fill_order_interval_id"],
            "fill_receipt": fill_receipt,
            "fill_timestamp": fill_ts,
            "fill_price_cents": x,
            "boundary_source_record_sha256": boundary[
                "source_record_sha256"
            ],
            "source_stream_sha256": record["source_stream_sha256"],
        }
        selector_hash = canonical_sha256(selector)
        rows.append({
            "schema_version": "window1-t2-unique-credited-fill-v1",
            "candidate_id": candidate,
            "base_candidate_id": record["base_candidate_id"],
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
            "action_authority": str(interval.get("authority") or "INHERITED"),
            "action_timestamp": opened,
            "action_trigger_receipt": action_book,
            "evidence_timestamp": fill_ts,
            "evaluated_right_ts": float(boundary["guarded_cutoff_ts"]),
            "boundary": boundary,
            "fill_role": role,
            "first_filled_leg": first_leg,
            "first_fill_timestamp": first_ts,
            "realized_first_leg_d1_cents": d1,
            "b2_max_cents": b2_max,
            "sibling_d2_cents": d2,
            "fee_cents": fee,
            "strict_combined_budget_passed": strict,
            "self_trigger_fill": False,
            "selection_basis": (
                "frozen_T2_fill_fact_then_V5_guard_admission"
            ),
            "causal_fill_identity": selector_hash,
            "selector_receipt_sha256": selector_hash,
            "source_stream_sha256": record["source_stream_sha256"],
            "source_stream_path": record["source_path"],
            "source_stream_shard_sha256": record["source_shard_sha256"],
            "metrics": None,
            "performance": None,
            "scored": False,
        })
        by_candidate[candidate] += 1
        by_type[(candidate, evidence_type)] += 1
    rows.sort(key=lambda row: (
        CANDIDATES.index(str(row["candidate_id"])),
        str(row["event_id"]), str(row["leg_id"]),
    ))
    keys = [
        (row["candidate_id"], row["event_id"], row["leg_id"])
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise T2PackageError("T2 unique-fill ledger is not unique")
    receipt = {
        "schema_version": VERSION + "-unique-fill-derivation-v1",
        "source_candidate_event_streams": len(records),
        "candidate_rows": [
            {
                "candidate_id": candidate,
                "raw_fill_facts": raw[candidate],
                "lawful_unique_fill_rows": by_candidate[candidate],
                "excluded_post_right_or_unprovable": excluded[candidate],
                "PRICE_REACHED": by_type[(candidate, "PRICE_REACHED")],
                "STRICT_ASK_CERTAIN_FILL": by_type[
                    (candidate, "STRICT_ASK_CERTAIN_FILL")
                ],
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
        "duplicate_credit": 0,
        "conflicting_fill_rows": 0,
        "same_receipt_action_fill": 0,
        "post_right_fill": 0,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    return rows, receipt


def _floor_ledgers(
    repo: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    legs: list[dict[str, Any]] = []
    ladder_sources: dict[tuple[str, str], tuple[str, str]] = {}
    for relative in RANGE_LADDER_FILES:
        shard_hash = sha256_file(repo / relative)
        for row in iter_gzip(repo / relative):
            event_id = str(row["event_id"])
            leg_id = str(row["leg_id"])
            key = (event_id, leg_id)
            if key in ladder_sources:
                raise T2PackageError("duplicate range-ladder leg")
            ladder_sources[key] = (relative, shard_hash)
            boundary = row["boundary"]
            positive = (
                row.get("positive_range_outcomes_provable") is True
                and boundary.get("positive_window1_provable") is True
            )
            price_rows = sorted(
                row["integer_cent_price_rows"],
                key=lambda item: int(item["price_cents"]),
            )
            touch = next(
                (
                    item for item in price_rows
                    if item.get("first_true_print_at_or_below")
                ),
                None,
            ) if positive else None
            print_capacity = next(
                (
                    item for item in price_rows
                    if float(item.get("executed_share_volume_at") or 0)
                    + float(item.get("executed_share_volume_below") or 0)
                    >= LOT
                    and item.get("first_true_print_at_or_below")
                ),
                None,
            ) if positive else None
            strict_ask = next(
                (
                    item for item in price_rows
                    if item.get("first_ask_strictly_below")
                ),
                None,
            ) if positive else None
            proven_candidates = [
                ("CUMULATIVE_TRUE_PRINT_CAPACITY", print_capacity),
                ("STRICT_ASK_CERTAIN_FILL", strict_ask),
            ]
            proven_candidates = [
                (kind, item) for kind, item in proven_candidates
                if item is not None
            ]
            proven_kind = None
            proven = None
            if proven_candidates:
                minimum = min(
                    int(item["price_cents"])
                    for _, item in proven_candidates
                )
                kinds = [
                    kind for kind, item in proven_candidates
                    if int(item["price_cents"]) == minimum
                ]
                proven_kind = "+".join(sorted(kinds))
                proven = next(
                    item for _, item in proven_candidates
                    if int(item["price_cents"]) == minimum
                )
            if proven is not None:
                status = "PROVEN_FIVE_CONTRACT_FLOOR"
            elif touch is not None:
                status = "PRICE_SEEN_CAPACITY_UNPROVED"
            else:
                status = "EVIDENCE_CENSORED"
            source_path, source_hash = ladder_sources[key]
            legs.append({
                "schema_version": VERSION + "-oracle-leg-floor-v1",
                "event_id": event_id,
                "event_date": str(row["event_date"]),
                "category": str(row["category"]),
                "leg_id": leg_id,
                "ticker": str(row["ticker"]),
                "D_member": True,
                "boundary": boundary,
                "policy_left_ts": row["policy_left_ts"],
                "guarded_right_ts": row["range_right_ts"],
                "floor_status": status,
                "tape_touch_floor_cents": (
                    int(touch["price_cents"]) if touch else None
                ),
                "tape_touch_first_receipt": (
                    touch["first_true_print_at_or_below"] if touch else None
                ),
                "tape_touch_last_receipt": (
                    touch["last_true_print_at_or_below"] if touch else None
                ),
                "five_contract_proven_floor_cents": (
                    int(proven["price_cents"]) if proven else None
                ),
                "five_contract_proof_type": proven_kind,
                "five_contract_print_volume_at_or_better": (
                    float(proven.get("executed_share_volume_at") or 0)
                    + float(proven.get("executed_share_volume_below") or 0)
                    if proven else None
                ),
                "five_contract_print_first_receipt": (
                    proven.get("first_true_print_at_or_below")
                    if proven else None
                ),
                "five_contract_print_last_receipt": (
                    proven.get("last_true_print_at_or_below")
                    if proven else None
                ),
                "five_contract_strict_ask_receipt": (
                    proven.get("first_ask_strictly_below")
                    if proven and "STRICT_ASK" in str(proven_kind) else None
                ),
                "source_range_ladder_path": source_path,
                "source_range_ladder_sha256": source_hash,
                "full_tape_oracle_only": True,
                "policy_reachable": False,
                "carried_last_trade_used": False,
                "constructed_midpoint_used": False,
                "reference_status": "EVALUATION_PENDING",
                "reference_relative_delta_cents": None,
                "metrics": None,
                "performance": None,
                "scored": False,
            })
    legs.sort(key=lambda row: (row["event_id"], row["leg_id"]))
    if len(legs) != 1608:
        raise T2PackageError("oracle leg floor count differs from 1,608")
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in legs:
        by_event[str(row["event_id"])].append(row)
    pairs = []
    for event_id, pair_legs in sorted(by_event.items()):
        if len(pair_legs) != 2:
            raise T2PackageError("pair floor does not have two legs")
        touch_prices = [row["tape_touch_floor_cents"] for row in pair_legs]
        proven_prices = [
            row["five_contract_proven_floor_cents"] for row in pair_legs
        ]
        pairs.append({
            "schema_version": VERSION + "-oracle-pair-floor-v1",
            "event_id": event_id,
            "event_date": pair_legs[0]["event_date"],
            "category": pair_legs[0]["category"],
            "D_member": True,
            "legs": [
                {
                    "leg_id": row["leg_id"],
                    "tape_touch_floor_cents": row["tape_touch_floor_cents"],
                    "tape_touch_receipt": row[
                        "tape_touch_first_receipt"
                    ],
                    "five_contract_proven_floor_cents": row[
                        "five_contract_proven_floor_cents"
                    ],
                    "five_contract_proof_type": row[
                        "five_contract_proof_type"
                    ],
                    "floor_status": row["floor_status"],
                }
                for row in pair_legs
            ],
            "combined_tape_touch_floor_cents": (
                sum(int(value) for value in touch_prices)
                if all(value is not None for value in touch_prices) else None
            ),
            "combined_five_contract_proven_floor_cents": (
                sum(int(value) for value in proven_prices)
                if all(value is not None for value in proven_prices) else None
            ),
            "proven_pair_floor": all(
                row["floor_status"] == "PROVEN_FIVE_CONTRACT_FLOOR"
                for row in pair_legs
            ),
            "asynchronous_leg_timestamps_allowed": True,
            "reference_relative_tape_touch_delta_cents": None,
            "reference_relative_proven_delta_cents": None,
            "full_tape_oracle_only": True,
            "policy_reachable": False,
            "metrics": None,
            "performance": None,
            "scored": False,
        })
    if len(pairs) != D_REQUIRED:
        raise T2PackageError("oracle pair floor count differs from D=804")
    status = Counter(row["floor_status"] for row in legs)
    census = {
        "schema_version": VERSION + "-floor-coverage-census-v1",
        "leg_rows": len(legs),
        "pair_rows": len(pairs),
        "leg_status_counts": dict(sorted(status.items())),
        "tape_touch_leg_coverage": sum(
            row["tape_touch_floor_cents"] is not None for row in legs
        ),
        "five_contract_proven_leg_coverage": sum(
            row["five_contract_proven_floor_cents"] is not None
            for row in legs
        ),
        "tape_touch_pair_coverage": sum(
            row["combined_tape_touch_floor_cents"] is not None
            for row in pairs
        ),
        "five_contract_proven_pair_coverage": sum(
            row["proven_pair_floor"] for row in pairs
        ),
        "candidate_completion_at_any_price": None,
        "full_tape_opportunity_coverage_at_any_price": {
            "proven_pair_events": sum(row["proven_pair_floor"] for row in pairs),
            "D": D_REQUIRED,
            "benchmark_not_candidate_capture_claim": True,
        },
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "performance": None,
        "scored": False,
    }
    return legs, pairs, census


def _regret_input_rows(
    records: Mapping[tuple[str, str], Mapping[str, Any]],
    floor_rows: list[Mapping[str, Any]],
    unique_fills: list[Mapping[str, Any]],
    repo: Path,
) -> list[dict[str, Any]]:
    floors = {
        (str(row["event_id"]), str(row["leg_id"])): row
        for row in floor_rows
    }
    fills = {
        (str(row["candidate_id"]), str(row["event_id"]), str(row["leg_id"])): row
        for row in unique_fills
    }
    divots: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "recognized_prices": [],
            "recognition_receipts": [],
            "action_count": 0,
            "fill_evidence_count": 0,
        }
    )
    chronology_rel = (
        f"{T2_PACKAGE_REL}/"
        "DIVOT_RECOGNITION_ACTION_EVIDENCE_CHRONOLOGY.jsonl.gz"
    )
    for row in iter_gzip(repo / chronology_rel):
        key = (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        )
        item = divots[key]
        stage = str(row["chronology_stage"])
        if stage == "RECOGNITION":
            item["recognized_prices"].append(
                exact_int(row["recognized_X_cents"], "divot X", 1, 99)
            )
            item["recognition_receipts"].append(
                str(row["recognition_receipt"])
            )
        elif stage == "ACTION":
            item["action_count"] += 1
        elif stage == "FILL_EVIDENCE":
            item["fill_evidence_count"] += 1
    output = []
    for (candidate, event_id), record in sorted(
        records.items(),
        key=lambda item: (
            CANDIDATES.index(item[0][0]), item[0][1]
        ),
    ):
        pair = record["pair_state"]
        first_ts = pair.get("first_fill_ts")
        first_leg = pair.get("first_filled_leg")
        leg_ids = sorted({
            *record["intervals"].keys(),
            *record["fills"].keys(),
            *[
                leg for event, leg in floors
                if event == event_id
            ],
        })
        if len(leg_ids) != 2:
            raise T2PackageError("regret input lost event leg identity")
        for leg_id in leg_ids:
            intervals = list(record["intervals"].get(leg_id) or [])
            relevant = [
                row for row in intervals
                if (
                    first_ts is None
                    or leg_id == first_leg
                    or float(row["opened_ts"]) > float(first_ts)
                )
            ]
            recognized = divots[(candidate, event_id, leg_id)]
            selected_prices = [
                exact_int(
                    row.get("raw_target_cents", row["limit_price_cents"]),
                    "raw target", 1, 99,
                )
                for row in relevant
            ]
            exposed_prices = [
                exact_int(row["limit_price_cents"], "exposed price", 1, 99)
                for row in relevant
            ]
            floor = floors[(event_id, leg_id)]
            fill = fills.get((candidate, event_id, leg_id))
            census = next(
                (
                    row for row in record["evidence_census"]
                    if str(row.get("leg_id")) == leg_id
                ),
                {},
            )
            action_authorities = Counter(
                str(row.get("authority") or "INHERITED")
                for row in relevant
            )
            output.append({
                "schema_version": VERSION + "-regret-chain-input-v1",
                "candidate_id": candidate,
                "base_candidate_id": record["base_candidate_id"],
                "event_id": event_id,
                "event_date": record["event_date"],
                "category": record["category"],
                "leg_id": leg_id,
                "macro_micro_family": (
                    "macro_micro"
                    if "__macro_micro__" in candidate else "macro_hold"
                ),
                "native_regime": (
                    census.get("discovery_page_key")
                    or "NO_CALL_UNAVAILABLE"
                ),
                "orientation": "HASH_BOUND_UNCONSUMED",
                "first_filled_leg": first_leg,
                "first_fill_timestamp": first_ts,
                "full_tape_tape_touch_floor_cents": floor[
                    "tape_touch_floor_cents"
                ],
                "full_tape_five_contract_proven_floor_cents": floor[
                    "five_contract_proven_floor_cents"
                ],
                "full_tape_floor_status": floor["floor_status"],
                "best_recognized_opportunity_cents": (
                    min(recognized["recognized_prices"])
                    if recognized["recognized_prices"] else None
                ),
                "recognized_opportunity_count": len(
                    recognized["recognized_prices"]
                ),
                "recognition_receipts": sorted(
                    set(recognized["recognition_receipts"])
                ),
                "best_selected_target_cents": (
                    min(selected_prices) if selected_prices else None
                ),
                "selected_target_count": len(selected_prices),
                "best_exposed_price_cents": (
                    min(exposed_prices) if exposed_prices else None
                ),
                "exposure_interval_count": len(relevant),
                "exposure_authority_counts": dict(
                    sorted(action_authorities.items())
                ),
                "credited_fill_price_cents": (
                    fill["fill_price_cents"] if fill else None
                ),
                "credited_fill_identity": (
                    fill["causal_fill_identity"] if fill else None
                ),
                "divot_later_action_count": recognized["action_count"],
                "divot_still_later_fill_evidence_count": recognized[
                    "fill_evidence_count"
                ],
                "primary_loss_stage": None,
                "execution_proof_regret_cents": None,
                "signed_tape_touch_gap_cents": None,
                "recognition_gap_cents": None,
                "target_selection_gap_cents": None,
                "exposure_gap_cents": None,
                "execution_gap_cents": None,
                "oracle_unreachable_from_policy": True,
                "metrics": None,
                "performance": None,
                "scored": False,
            })
    if len(output) != len(CANDIDATES) * D_REQUIRED * 2:
        raise T2PackageError("regret input rows differ from 12,864")
    return output


def _audited_identity(repo: Path) -> dict[str, Any]:
    rows = []
    for relative in AUDITED_FILES:
        current = identity_bytes(repo / relative)
        prior = subprocess.run(
            ["git", "show", f"{AUDITED_SCORER_COMMIT}:{relative}"],
            cwd=repo, capture_output=True, check=False,
        )
        if prior.returncode:
            raise T2PackageError(f"audited source missing: {relative}")
        audited = canonical_text(prior.stdout)
        if current != audited:
            raise T2PackageError(
                f"settled metric/reference mechanics changed: {relative}"
            )
        rows.append({
            "path": relative,
            "audited_commit": AUDITED_SCORER_COMMIT,
            "sha256": hashlib.sha256(current).hexdigest(),
            "git_blob_oid": git_blob_oid(current),
            "byte_identical": True,
        })
    return {
        "schema_version": VERSION + "-settled-law-identity-v1",
        "audited_commit": AUDITED_SCORER_COMMIT,
        "files": rows,
        "all_byte_identical": True,
        "metric_reference_or_exact_integer_law_changed": False,
    }


def _artifact_rows(output: Path) -> list[dict[str, Any]]:
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
        raise T2PackageError("output directory already exists")
    head = git(repo, "rev-parse", "HEAD")
    if head != IMPLEMENTATION_PARENT and git(repo, "rev-parse", "HEAD^") != IMPLEMENTATION_PARENT:
        raise T2PackageError("builder is not on T2 parent or its sole child")
    output.mkdir(parents=True)
    events, boundaries, tickers = _load_events(repo)
    overlays, overlay_shards, overlay_hashes = _load_overlays(repo)
    baselines, baseline_shards, baseline_hashes = _load_baselines(repo)
    event_ids = [str(row["event_id"]) for row in events]
    records = {
        (candidate, event_id): _materialized(
            candidate, event_id,
            overlays, overlay_shards, overlay_hashes,
            baselines, baseline_shards, baseline_hashes,
        )
        for candidate in CANDIDATES for event_id in event_ids
    }
    if len(records) != 6432:
        raise T2PackageError("candidate-event stream count changed")
    fills, fill_receipt = _derive_unique_fills(
        repo, events, boundaries, tickers, records, workers=workers
    )
    leg_floors, pair_floors, floor_census = _floor_ledgers(repo)
    regret_inputs = _regret_input_rows(records, leg_floors, fills, repo)

    (output / "T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(fills)
    )
    write_json(
        output / "T2_UNIQUE_CREDITED_FILL_DERIVATION_RECEIPT.json",
        fill_receipt,
    )
    (output / "TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(leg_floors)
    )
    tape_floor_rows = [
        {
            "schema_version": VERSION + "-tape-touch-floor-v1",
            "event_id": row["event_id"],
            "event_date": row["event_date"],
            "category": row["category"],
            "leg_id": row["leg_id"],
            "ticker": row["ticker"],
            "tape_touch_floor_cents": row["tape_touch_floor_cents"],
            "tape_touch_first_receipt": row["tape_touch_first_receipt"],
            "tape_touch_last_receipt": row["tape_touch_last_receipt"],
            "guarded_right_ts": row["guarded_right_ts"],
            "price_seen": row["tape_touch_floor_cents"] is not None,
            "carried_last_trade_used": False,
            "constructed_midpoint_used": False,
            "oracle_unreachable_from_policy": True,
            "metrics": None,
            "performance": None,
            "scored": False,
        }
        for row in leg_floors
    ]
    proven_floor_rows = [
        {
            "schema_version": VERSION + "-five-contract-proven-floor-v1",
            "event_id": row["event_id"],
            "event_date": row["event_date"],
            "category": row["category"],
            "leg_id": row["leg_id"],
            "ticker": row["ticker"],
            "five_contract_proven_floor_cents": row[
                "five_contract_proven_floor_cents"
            ],
            "five_contract_proof_type": row[
                "five_contract_proof_type"
            ],
            "five_contract_print_first_receipt": row[
                "five_contract_print_first_receipt"
            ],
            "five_contract_print_last_receipt": row[
                "five_contract_print_last_receipt"
            ],
            "five_contract_print_volume_at_or_better": row[
                "five_contract_print_volume_at_or_better"
            ],
            "five_contract_strict_ask_receipt": row[
                "five_contract_strict_ask_receipt"
            ],
            "floor_status": row["floor_status"],
            "guarded_right_ts": row["guarded_right_ts"],
            "oracle_unreachable_from_policy": True,
            "metrics": None,
            "performance": None,
            "scored": False,
        }
        for row in leg_floors
    ]
    (output / "TAPE_TOUCH_FLOOR_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(tape_floor_rows)
    )
    (output / "FIVE_CONTRACT_PROVEN_FLOOR_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(proven_floor_rows)
    )
    (output / "ASYNCHRONOUS_PAIR_FLOOR_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(pair_floors)
    )
    write_json(output / "FLOOR_COVERAGE_CENSUS.json", floor_census)
    (output / "T2_REGRET_CHAIN_INPUT_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(regret_inputs)
    )

    fit_rows = [
        {
            "event_id": str(event["event_id"]),
            "event_date": str(event["event_date"]),
            "category": str(event["category"]),
            "slice": (
                "fit" if str(event["event_date"]) in FIT_DATES else "post_fit"
            ),
            "D_member": True,
        }
        for event in events
    ]
    write_json(output / "FIT_POSTFIT_BOUNDARY_LEDGER.json", {
        "schema_version": VERSION + "-fit-postfit-v1",
        "fit_dates": sorted(FIT_DATES),
        "post_fit_dates": sorted(POST_FIT_DATES),
        "fit_D": sum(row["slice"] == "fit" for row in fit_rows),
        "post_fit_D": sum(row["slice"] == "post_fit" for row in fit_rows),
        "aggregate_D": len(fit_rows),
        "rows": fit_rows,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    identities = read_json(
        repo / PRIOR_SCORING_REL / "FROZEN_EVENT_LEG_IDENTITIES.json"
    )
    if identities.get("D") != 804 or identities.get("leg_identities") != 1608:
        raise T2PackageError("event-leg identity ledger changed")
    write_json(output / "FROZEN_EVENT_LEG_IDENTITIES.json", identities)
    (output / "IMMUTABLE_EVENT_LEDGER.jsonl").write_bytes(
        jsonl_bytes(events)
    )
    (output / "GUARDED_BOUNDARY_LEDGER.jsonl").write_bytes(
        jsonl_bytes(
            boundaries[str(event["event_id"])] for event in events
        )
    )
    spec = read_json(repo / SPEC_REL)
    if tuple(spec["candidate_ids"]) != CANDIDATES:
        raise T2PackageError("T2 candidate allowlist changed")
    write_json(output / "FROZEN_T2_CANDIDATE_SPEC.json", spec)
    mechanism = read_json(repo / T2_PACKAGE_REL / "MECHANISM_STATUS_TABLE.json")
    statuses = Counter(row["status"] for row in mechanism["mechanisms"])
    if statuses != Counter({
        "BOUND": 12, "PROXIED": 10, "ABSENT": 4, "RETRACTED": 8,
    }):
        raise T2PackageError("mechanism status manifest changed")
    claim_fences = {
        "schema_version": VERSION + "-claim-fences-v1",
        "mechanism_manifest_unchanged": mechanism,
        "status_totals": dict(sorted(statuses.items())),
        "required_result_fences": [
            "orientation is hash-bound but unconsumed",
            "volume, pressure and last trade are stored evidence, not candidate gates",
            "drift/band/recut/LIBRARY surfaces are not consumed",
            "depth claims are limited to bound top five",
            "Pinnacle and authoritative bookmaker/FV are absent",
            "historical divot tables are replaced by the bound native causal print-divot mechanism",
            "results describe these eight T2 candidate families, not the complete OS or a market ceiling",
        ],
        "template_omission_is_fatal": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "CLAIM_FENCE_MANIFEST.json", claim_fences)
    decision_binding = {
        "schema_version": VERSION + "-decision-attribution-binding-v1",
        "frozen_T2_counts": {
            "later_divot_actions": 140,
            "still_later_fill_evidence": 81,
            "PARK_exits": 6963,
            "recognized_divots": 166644,
            "later_recurrences": 176435,
            "positive_d2_targets_exposed": 54,
        },
        "authority_families": [
            "parent HOLD/non-displacement",
            "evidence-decay replacement",
            "PARK combined-budget or maker-law invalidation",
            "causal-divot recognition",
            "later recurrence",
            "target selection",
            "PLACE",
            "REPRICE",
            "exposure persistence",
            "fill evidence",
            "macro-target authority",
            "causal-pair-headroom authority",
            "LIVE-AIM authority",
        ],
        "market_absent_from_policy_inaction_forbidden": True,
        "source_receipts": [
            binary_source_row(
                repo,
                f"{T2_PACKAGE_REL}/"
                "DIVOT_RECOGNITION_ACTION_EVIDENCE_CHRONOLOGY.jsonl.gz",
                "divot_action_fill_chronology",
            ),
            binary_source_row(
                repo,
                f"{T2_PACKAGE_REL}/"
                "PARENT_EXPOSURE_PRESERVATION_REPLACEMENT_CENSUS.json",
                "preservation_replacement_park_census",
            ),
            binary_source_row(
                repo, f"{T2_PACKAGE_REL}/PRE_RUN_MANIFEST.json",
                "T2_count_manifest",
            ),
        ],
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "DECISION_LAYER_ATTRIBUTION_BINDING.json", decision_binding)
    settled = _audited_identity(repo)
    write_json(output / "SETTLED_SCORING_LAW_IDENTITY_RECEIPT.json", settled)
    audit = audit_blob(repo)
    write_json(output / "T2_INSTRUMENT_AUDIT_BINDING.json", {
        "schema_version": VERSION + "-instrument-audit-binding-v1",
        "T2_prerun": IMPLEMENTATION_PARENT,
        "T2_parent": "d710ba0606084f67625e255e87ebad1cd016bf6a",
        "independent_PASS": CONTROLLING_T2_PASS,
        "audit_report": audit,
        "candidate_ids": list(CANDIDATES),
        "candidate_switch_hashes": {
            candidate: canonical_sha256(spec["switch_matrix"][candidate])
            for candidate in CANDIDATES
        },
        "candidate_target_action_fill_exposure_changed": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    })

    cache_hashes = read_json(
        repo / PRIOR_SCORING_REL / "GUARDED_CACHE_V3_HASH_SET.json"
    )
    write_json(output / "GUARDED_CACHE_V3_HASH_SET.json", cache_hashes)
    source_inputs = [
        source_row(repo, relative, role)
        for relative, role in (
            (ADAPTER_REL, "T2 exact-integer guarded-fill adapter"),
            (SCORER_REL, "frontier and regret scorer wrapper"),
            (RUNNER_REL, "stdout-safe deterministic runner"),
            (BUILDER_REL, "score-free package builder"),
            (FREEZER_REL, "two-build deterministic freezer"),
            (TEST_REL, "synthetic and invariant tests"),
            (CONTRACT_REL, "frontier and oracle contract"),
            (SPEC_REL, "frozen T2 candidate specification"),
        )
    ]
    source_inputs.extend(
        source_row(repo, relative, "byte-identical settled scoring law")
        for relative in AUDITED_FILES
    )
    frozen_binary_inputs = [
        binary_source_row(repo, relative, "T2 candidate overlay")
        for relative in OVERLAY_FILES
    ] + [
        binary_source_row(repo, relative, "fixed-admission baseline stream")
        for relative in BASE_STREAM_FILES
    ] + [
        binary_source_row(repo, relative, "frozen Window1 range ladder")
        for relative in RANGE_LADDER_FILES
    ]
    for relative, role in (
        (
            f"{T2_PACKAGE_REL}/"
            "DIVOT_RECOGNITION_ACTION_EVIDENCE_CHRONOLOGY.jsonl.gz",
            "frozen divot chronology",
        ),
        (
            f"{T2_PACKAGE_REL}/MECHANISM_STATUS_TABLE.json",
            "audited mechanism manifest",
        ),
        (
            f"{T2_PACKAGE_REL}/PRE_RUN_MANIFEST.json",
            "T2 PRE-RUN conservation manifest",
        ),
        (
            f"{T2_PACKAGE_REL}/"
            "PARENT_EXPOSURE_PRESERVATION_REPLACEMENT_CENSUS.json",
            "T2 exposure and PARK census",
        ),
    ):
        frozen_binary_inputs.append(binary_source_row(repo, relative, role))
    private = read_json(
        repo / ".claude/window1_t1_scoring_package_prerun_20260727"
        / "SOURCE_HASH_MANIFEST.json"
    )["private_runtime_inputs"]
    source_manifest = {
        "schema_version": VERSION + "-source-hashes-v1",
        "committed_inputs": source_inputs,
        "frozen_binary_inputs": frozen_binary_inputs,
        "private_runtime_inputs": private,
        "T2_unique_fill_ledger": {
            "path": f"{PACKAGE_REL}/T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz",
            "bytes": (
                output / "T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
            ).stat().st_size,
            "sha256": sha256_file(
                output / "T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
            ),
        },
        "oracle_leg_floor_ledger": {
            "path": f"{PACKAGE_REL}/TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz",
            "bytes": (
                output / "TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz"
            ).stat().st_size,
            "sha256": sha256_file(
                output / "TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz"
            ),
        },
        "tape_touch_floor_ledger": {
            "path": f"{PACKAGE_REL}/TAPE_TOUCH_FLOOR_LEDGER.jsonl.gz",
            "bytes": (
                output / "TAPE_TOUCH_FLOOR_LEDGER.jsonl.gz"
            ).stat().st_size,
            "sha256": sha256_file(
                output / "TAPE_TOUCH_FLOOR_LEDGER.jsonl.gz"
            ),
        },
        "five_contract_proven_floor_ledger": {
            "path": (
                f"{PACKAGE_REL}/FIVE_CONTRACT_PROVEN_FLOOR_LEDGER.jsonl.gz"
            ),
            "bytes": (
                output / "FIVE_CONTRACT_PROVEN_FLOOR_LEDGER.jsonl.gz"
            ).stat().st_size,
            "sha256": sha256_file(
                output / "FIVE_CONTRACT_PROVEN_FLOOR_LEDGER.jsonl.gz"
            ),
        },
        "holdout_paths_or_hashes": [],
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)

    expected_schema = {
        "schema_version": VERSION + "-expected-output-v1",
        "candidate_order": list(CANDIDATES),
        "candidate_count": 8,
        "D_per_candidate": 804,
        "slices": {
            "aggregate": 804, "fit": 525, "post_fit": 279,
        },
        "frontier_tiers": ["LE_93", "LE_95", "LE_97", "LT_100", "ANY_PRICE"],
        "tier_fields": [
            "C", "C_over_D", "PC", "PC_over_D",
            "both_legs_negative",
            "leg1_negative_leg2_nonnegative",
            "leg1_nonnegative_leg2_negative",
            "both_legs_nonnegative",
            "reference_missing_completions", "S", "S_over_D",
            "IC", "IC_over_D", "PC_but_not_IC",
            "PC_but_not_IC_leg1_negative_leg2_nonnegative",
            "PC_but_not_IC_leg1_nonnegative_leg2_negative",
            "PC_shortfall_from_603",
        ],
        "regret_dimensions": [
            "candidate", "slice", "category", "native_regime",
            "orientation", "macro_micro_family", "primary_loss_stage",
        ],
        "primary_loss_stages": read_json(repo / CONTRACT_REL)[
            "primary_loss_stages"
        ],
        "claim_fences": claim_fences["required_result_fences"],
        "ranking_or_selection": None,
    }
    write_json(output / "EXPECTED_OUTPUT_SCHEMA.json", expected_schema)
    write_json(output / "EXECUTION_AUTHORIZATION_TEMPLATE.json", {
        "schema_version": VERSION + "-authorization-template-v1",
        "future_authorization_commit_supplied_separately": True,
        "future_report_must_bind": [
            "exact_package_commit", "exact_execution_id",
            "full_input_bundle_sha256", "exact_command_template_literal",
        ],
        "self_referential_authorization_SHA_required": False,
        "clean_worktree_required": True,
        "local_remote_equality_required": True,
        "new_results_directory_required": RESULTS_REL,
        "single_attempt_no_retry": True,
        "command_template_literal": COMMAND_TEMPLATE,
        "authorized": False,
    })
    write_json(output / "NULL_METRIC_NO_EXECUTION_RECEIPT.json", {
        "schema_version": VERSION + "-no-execution-v1",
        "candidate_metrics": {
            candidate: {
                "C": None, "PC": None, "IC": None, "S": None,
                "frontier": None, "regret": None, "performance": None,
            }
            for candidate in CANDIDATES
        },
        "real_population_scorer_invocations": 0,
        "results_directory_exists": False,
        "ranking_or_selection": None,
        "holdout_access": False,
        "live_or_production_access": False,
        "scored": False,
    })
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "allowed_inputs": "July 12-20 development only",
        "sealed_dates": sorted(SEALED_DATES),
        "holdout_access": False,
        "live_access": False,
        "production_access": False,
        "network_calls": 0,
        "orders_positions_exits_window2_settlement_DCA_access": False,
        "results_directory_created": False,
    })
    input_payload = {
        "T2_prerun": IMPLEMENTATION_PARENT,
        "T2_PASS": CONTROLLING_T2_PASS,
        "candidate_ids": list(CANDIDATES),
        "candidate_event_stream_count": len(records),
        "event_count": D_REQUIRED,
        "leg_identity_count": 1608,
        "unique_fill_ledger_sha256": source_manifest[
            "T2_unique_fill_ledger"
        ]["sha256"],
        "oracle_leg_floor_ledger_sha256": source_manifest[
            "oracle_leg_floor_ledger"
        ]["sha256"],
        "tape_touch_floor_ledger_sha256": source_manifest[
            "tape_touch_floor_ledger"
        ]["sha256"],
        "five_contract_proven_floor_ledger_sha256": source_manifest[
            "five_contract_proven_floor_ledger"
        ]["sha256"],
        "immutable_event_ledger_sha256": sha256_file(
            output / "IMMUTABLE_EVENT_LEDGER.jsonl"
        ),
        "guarded_boundary_ledger_sha256": sha256_file(
            output / "GUARDED_BOUNDARY_LEDGER.jsonl"
        ),
        "source_manifest_sha256": sha256_file(
            output / "SOURCE_HASH_MANIFEST.json"
        ),
        "contract_sha256": source_row(
            repo, CONTRACT_REL, "contract"
        )["sha256"],
        "claim_fence_manifest_sha256": sha256_file(
            output / "CLAIM_FENCE_MANIFEST.json"
        ),
        "fit_D": 525,
        "post_fit_D": 279,
        "fee_cents": 0,
        "holdout_dates": [],
    }
    package = {
        "schema_version": "window1-t2-scoring-input-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_T2_PASS": CONTROLLING_T2_PASS,
        "audited_scorer_commit": AUDITED_SCORER_COMMIT,
        "execution_id": EXECUTION_ID,
        "results_directory": RESULTS_REL,
        "candidate_ids": list(CANDIDATES),
        "candidate_count": 8,
        "D": 804,
        "fit_D": 525,
        "post_fit_D": 279,
        "command_template_literal": COMMAND_TEMPLATE,
        "input_bundle_payload": input_payload,
        "input_bundle_sha256": canonical_sha256(input_payload),
        "roles": {
            "event_ledger": (
                f"{PACKAGE_REL}/IMMUTABLE_EVENT_LEDGER.jsonl"
            ),
            "start_ledger": (
                f"{PACKAGE_REL}/GUARDED_BOUNDARY_LEDGER.jsonl"
            ),
            "guarded_cache_directory": CACHE_REL,
            "guarded_cache_hash_set": (
                f"{PACKAGE_REL}/GUARDED_CACHE_V3_HASH_SET.json"
            ),
            "unique_T2_fill_ledger": (
                f"{PACKAGE_REL}/T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
            ),
            "oracle_leg_floor_ledger": (
                f"{PACKAGE_REL}/TAPE_AND_FIVE_CONTRACT_FLOOR_LEDGER.jsonl.gz"
            ),
            "tape_touch_floor_ledger": (
                f"{PACKAGE_REL}/TAPE_TOUCH_FLOOR_LEDGER.jsonl.gz"
            ),
            "five_contract_proven_floor_ledger": (
                f"{PACKAGE_REL}/FIVE_CONTRACT_PROVEN_FLOOR_LEDGER.jsonl.gz"
            ),
            "oracle_pair_floor_ledger": (
                f"{PACKAGE_REL}/ASYNCHRONOUS_PAIR_FLOOR_LEDGER.jsonl.gz"
            ),
            "regret_chain_input_ledger": (
                f"{PACKAGE_REL}/T2_REGRET_CHAIN_INPUT_LEDGER.jsonl.gz"
            ),
            "fit_postfit_ledger": (
                f"{PACKAGE_REL}/FIT_POSTFIT_BOUNDARY_LEDGER.json"
            ),
            "event_leg_identities": (
                f"{PACKAGE_REL}/FROZEN_EVENT_LEG_IDENTITIES.json"
            ),
            "candidate_specification": (
                f"{PACKAGE_REL}/FROZEN_T2_CANDIDATE_SPEC.json"
            ),
            "claim_fence_manifest": (
                f"{PACKAGE_REL}/CLAIM_FENCE_MANIFEST.json"
            ),
            "source_hash_manifest": (
                f"{PACKAGE_REL}/SOURCE_HASH_MANIFEST.json"
            ),
            "expected_output_schema": (
                f"{PACKAGE_REL}/EXPECTED_OUTPUT_SCHEMA.json"
            ),
        },
        "future_independent_PASS_required": True,
        "authorization": None,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "performance": None,
        "scored": False,
        "ranking_or_selection": None,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", package)
    report = f"""# Window-1 T2 scoring-package PRE-RUN

Score-free package for exactly eight frozen T2 candidates and D=804.
The completion frontier is cumulative at <=93, <=95, <=97, <100, and
any-price, reported separately for aggregate 804, fit 525, and post-fit 279.
The ex-post tape/proven floors are unreachable from policy code.

Input bundle SHA-256: `{package['input_bundle_sha256']}`

All C/PC/IC/S, frontier, regret, and performance fields are null.  No scorer
was invoked, no results directory was created, and July 24-26 remains sealed.
No ranking or selection is authorized.

## Claim fences

""" + "\n".join(
        f"- {value}" for value in claim_fences["required_result_fences"]
    ) + "\n"
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    write_json(output / "INDEPENDENT_AUDIT_INSTRUCTION.json", {
        "schema_version": VERSION + "-audit-instruction-v1",
        "instruction": (
            "Audit this package without executing the scorer. Reproduce the "
            "unique-fill and two oracle floors, all fit/post-fit boundaries, "
            "exact tier endpoints, regret stage conservation, claim fences, "
            "hashes, two clean builds, and every synthetic/inherited test. "
            "A PASS authorizes nothing; return a separate PASS commit/report."
        ),
        "audit_branch": "audit/window1-independent",
        "merge_package_before_audit": False,
        "execute_or_score": False,
    })
    write_json(output / "DETERMINISTIC_PACKAGE_REGENERATION_RECEIPT.json", {
        "schema_version": VERSION + "-determinism-v1",
        "clean_builds_required": 2,
        "canonical_json": "UTF-8 LF sorted keys indent=2 trailing LF",
        "deterministic_gzip": "filename empty; mtime=0; canonical JSONL",
        "byte_identical": True,
        "verified_during_freeze": True,
        "metrics": None,
        "performance": None,
        "scored": False,
    })
    artifact_rows = _artifact_rows(output)
    write_json(output / "PACKAGE_ARTIFACT_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "artifacts": artifact_rows,
        "artifact_count": len(artifact_rows),
    })
    return {
        "schema_version": VERSION + "-build-receipt-v1",
        "output": str(output),
        "candidate_count": len(CANDIDATES),
        "candidate_event_streams": len(records),
        "unique_fill_rows": len(fills),
        "floor_leg_rows": len(leg_floors),
        "floor_pair_rows": len(pair_floors),
        "input_bundle_sha256": package["input_bundle_sha256"],
        "artifact_count": len(artifact_rows),
        "real_scorer_invocations": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (repo / args.output_dir).resolve()
    )
    print(json.dumps(
        build(repo=repo, output=output, workers=args.workers),
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
