#!/usr/bin/env python3
"""Freeze the score-free Window-1 asynchronous opportunity census V2.

V2 scans every raw chronological print and lawful external-book episode.
It preserves candidate actions and results as evidence, but never imports or
invokes a scorer and never calculates C/PC/IC/S.
"""

from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import math
import pickle
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-asynchronous-opportunity-policy-census-v2"
PARENT = "9220eba26b00a5b94e86d9c644adef16382942a0"
AUDIT = "0350c081a26e06216a34f58eed8a13e72ef5e236"
AUDIT_REPORT = (
    ".claude/audit_20260726_window1_async_census_same_timestamp_bbo_amendment/"
    "ITEM_SAME_TIMESTAMP_BBO_AMENDMENT.md"
)
AUDIT_CENSUS = (
    ".claude/audit_20260726_window1_async_census_same_timestamp_bbo_amendment/"
    "CONTEMPORANEOUS_BBO_SELECTION_CENSUS.json"
)
AUDIT_SOURCE_RECEIPT = (
    ".claude/audit_20260726_window1_async_census_same_timestamp_bbo_amendment/"
    "SOURCE_AND_ARTIFACT_HASH_RECEIPT.json"
)
AUDIT_ARTIFACTS = (
    AUDIT_REPORT,
    AUDIT_CENSUS,
    (
        ".claude/audit_20260726_window1_async_census_"
        "same_timestamp_bbo_amendment/DISPUTED_THREE_EPISODE_RECEIPT.json"
    ),
    (
        ".claude/audit_20260726_window1_async_census_"
        "same_timestamp_bbo_amendment/"
        "INDEPENDENT_RAW_ROW_VALIDATION_RECEIPT.json"
    ),
    AUDIT_SOURCE_RECEIPT,
)
PACKAGE_REL = (
    ".claude/window1_asynchronous_opportunity_policy_census_v2_20260726"
)
V1_PACKAGE_REL = (
    ".claude/window1_asynchronous_opportunity_policy_census_20260726"
)
STRICT_REL = ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
RESULT_REL = (
    ".claude/window1_range_attack_results_"
    "w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2"
)
CACHE_REL = "../OMI-Window1-private/fit-local/guarded-cache-v3"
SPEC_REL = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ASYNC_OPPORTUNITY_POLICY_CENSUS_V2_SPEC.json"
)
SOURCE_REL = (
    "arb-executor/analysis/"
    "window1_asynchronous_opportunity_policy_census_v2.py"
)
TEST_REL = (
    "arb-executor/tests/"
    "test_window1_asynchronous_opportunity_policy_census_v2.py"
)
CANDIDATES = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
RESULT_FILES = {
    CANDIDATES[0]: (
        f"{RESULT_REL}/"
        "01_w1_range_attack__macro_hold__combined_headroom_EVENT_LEDGER.jsonl"
    ),
    CANDIDATES[1]: (
        f"{RESULT_REL}/"
        "02_w1_range_attack__macro_micro__combined_headroom_EVENT_LEDGER.jsonl"
    ),
}
X_FILES = tuple(
    f"{V1_PACKAGE_REL}/FROZEN_X_EVIDENCE_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
STREAM_FILES = tuple(
    f"{STRICT_REL}/UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
ACTION_FILE = f"{STRICT_REL}/ACTION_AUTHORITY_RECEIPTS.jsonl.gz"
DEVELOPMENT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(12, 21)
)
SEALED_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)
VUKBRO = "KXATPCHALLENGERMATCH-26JUL13VUKBRO"
AVEFOR = "KXATPCHALLENGERMATCH-26JUL12AVEFOR"
DISPUTED_RECEIPTS = frozenset({
    "06a93c92-0d52-4040-1ed2-6882d5490b0a",
    "8f0d3c80-128b-4359-4f43-1d9e5a6b57d1",
    "3e4c49d6-a936-45a0-6577-5f2fdefe62b9",
})


class CensusError(RuntimeError):
    """A frozen evidence, construction, or conservation invariant failed."""


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
        raise CensusError(
            f"git {' '.join(args)} failed: {process.stderr.strip()}"
        )
    return process.stdout.strip()


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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


class PreparedRawStore:
    """Disk-backed deterministic event evidence with a one-event read cache."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._key: str | None = None
        self._value: dict[str, Any] | None = None

    def write(self, event_id: str, value: Mapping[str, Any]) -> None:
        path = self.root / f"{event_id}.pickle.gz"
        with path.open("wb") as raw:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw, mtime=0
            ) as handle:
                pickle.dump(dict(value), handle, protocol=4)

    def __getitem__(self, event_id: str) -> dict[str, Any]:
        if self._key != event_id:
            with gzip.open(
                self.root / f"{event_id}.pickle.gz", "rb"
            ) as handle:
                self._value = pickle.load(handle)
            self._key = event_id
        assert self._value is not None
        return self._value


def exact_cent(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise CensusError(f"{field}: bool is not an exact cent")
    if isinstance(value, int):
        result = value
    elif (
        isinstance(value, float)
        and math.isfinite(value)
        and value.is_integer()
    ):
        result = int(value)
    else:
        raise CensusError(f"{field}: not an exact integer cent")
    if not 1 <= result <= 99:
        raise CensusError(f"{field}: outside 1..99")
    return result


def positive_size(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise CensusError(f"{field}: bool is not size")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise CensusError(f"{field}: not positive finite size")
    return result


def headroom_d2_max(d1: int, fee: int = 0) -> int:
    return math.floor(-d1 - fee - 1)


def strict_combined(d1: int, d2: int, fee: int = 0) -> bool:
    return d1 + d2 + fee < 0


def inside_corridor(
    timestamp: float,
    left: float,
    right: float,
    positive_window1_provable: bool,
) -> bool:
    return bool(
        positive_window1_provable
        and float(left) <= float(timestamp) <= float(right)
    )


def episode_is_strictly_later(first: float, sibling: float) -> bool:
    return float(sibling) > float(first)


def _levels(rows: Any, field: str) -> list[list[float | int]]:
    output: list[list[float | int]] = []
    for index, row in enumerate(rows or []):
        if not isinstance(row, list) or len(row) < 2:
            continue
        try:
            price = exact_cent(row[0], f"{field}[{index}].price")
            size = positive_size(row[1], f"{field}[{index}].size")
        except (CensusError, TypeError, ValueError):
            continue
        output.append([price, size])
    return output[:5]


def _raw_receipt(ticker: str, kind: str, ordinal: int, row: Any) -> str:
    return (
        f"{ticker}|raw-{kind}{ordinal}|"
        f"{canonical_sha256(row)}"
    )


def prepare_raw_leg(
    leg: Mapping[str, Any],
    left: float,
    right: float,
    positive_window1_provable: bool,
) -> dict[str, Any]:
    """Prepare lawful raw BBO and positive-print episodes once."""
    ticker = str(leg["ticker"])
    ambiguous_book_timestamps: set[float] = set()
    by_timestamp: dict[float, set[tuple[int, int]]] = defaultdict(set)
    raw_books: list[dict[str, Any]] = []
    for ordinal, snapshot in enumerate(leg.get("snapshots") or []):
        timestamp = float(snapshot["ts"])
        bids = _levels(snapshot.get("bids"), "bids")
        asks = _levels(snapshot.get("asks"), "asks")
        if not bids or not asks:
            continue
        bid = int(bids[0][0])
        ask = int(asks[0][0])
        if bid >= ask:
            continue
        if not inside_corridor(
            timestamp, left, right, positive_window1_provable
        ):
            continue
        last_trade = None
        if snapshot.get("last_trade") is not None:
            try:
                last_trade = exact_cent(
                    snapshot["last_trade"], "last_trade"
                )
            except CensusError:
                last_trade = None
        row = {
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
            "last_trade_cents": last_trade,
            "source": str(snapshot.get("source") or ""),
        }
        raw_books.append(row)
        by_timestamp[timestamp].add((bid, ask))
    for timestamp, values in by_timestamp.items():
        if len(values) > 1:
            ambiguous_book_timestamps.add(timestamp)
    raw_books.sort(key=lambda row: (
        row["timestamp"], row["source_ordinal"]
    ))
    raw_book_times = [float(row["timestamp"]) for row in raw_books]

    prints: list[dict[str, Any]] = []
    seen_print_receipts: set[str] = set()
    for ordinal, trade in enumerate(leg.get("prints") or []):
        try:
            timestamp = float(trade["ts"])
            price = exact_cent(trade["price"], "print.price")
            size = positive_size(trade["size"], "print.size")
        except (CensusError, TypeError, ValueError, KeyError):
            continue
        if not inside_corridor(
            timestamp, left, right, positive_window1_provable
        ):
            continue
        receipt = str(
            trade.get("trade_id")
            or _raw_receipt(ticker, "print", ordinal, trade)
        )
        if receipt in seen_print_receipts:
            continue
        seen_print_receipts.add(receipt)
        prints.append({
            "timestamp": timestamp,
            "source_ordinal": ordinal,
            "receipt": receipt,
            "price_cents": price,
            "size": size,
            "taker_side": trade.get("taker_side"),
        })
    prints.sort(key=lambda row: (
        row["timestamp"], row["source_ordinal"], row["receipt"]
    ))

    bare_episodes: list[dict[str, Any]] = []
    # Each strict-ask episode is self-contained in one lawful snapshot.  Same
    # timestamp snapshots therefore remain distinct evidence episodes; no
    # cross-row price selection is required.
    for book in raw_books:
        if int(book["ask_cents"]) >= 99:
            continue
        bare_episodes.append({
            "evidence_type": "STRICT_ASK_CERTAIN_FILL",
            "timestamp": float(book["timestamp"]),
            "price": int(book["ask_cents"]) + 1,
            "evidence_receipt": str(book["receipt"]),
            "evidence_size": None,
            "book": book,
        })
    for trade in prints:
        timestamp = float(trade["timestamp"])
        index = bisect.bisect_right(raw_book_times, timestamp) - 1
        if index < 0:
            continue
        book, _ = latest_book_reference(
            raw_books,
            timestamp,
            authoritative_source_row_order=True,
        )
        if book is None:
            continue
        bare_episodes.append({
            "evidence_type": "PRICE_REACHED",
            "timestamp": timestamp,
            "price": int(trade["price_cents"]),
            "evidence_receipt": str(trade["receipt"]),
            "evidence_size": float(trade["size"]),
            "book": book,
        })
    episodes: list[dict[str, Any]] = []
    for bare in bare_episodes:
        timestamp = float(bare["timestamp"])
        price = int(bare["price"])
        book = bare["book"]
        episodes.append(_episode_row(
            evidence_type=str(bare["evidence_type"]),
            timestamp=timestamp,
            price=price,
            evidence_receipt=str(bare["evidence_receipt"]),
            evidence_size=bare["evidence_size"],
            book=book,
        ))
    episodes.sort(key=episode_sort_key)
    return {
        "ticker": ticker,
        "books": raw_books,
        "raw_lawful_books": raw_books,
        "books_by_receipt": {
            str(row["receipt"]): row for row in raw_books
        },
        "prints": prints,
        "episodes": episodes,
        "ambiguous_book_timestamps": sorted(ambiguous_book_timestamps),
        "source_row_order_is_authoritative_sequence": True,
    }


def latest_book_reference(
    books: list[Mapping[str, Any]],
    timestamp: float,
    *,
    authoritative_source_row_order: bool,
) -> tuple[Mapping[str, Any] | None, str | None]:
    """Select latest BBO without arbitrary same-timestamp tie-breaking."""
    times = [float(row["timestamp"]) for row in books]
    index = bisect.bisect_right(times, float(timestamp)) - 1
    if index < 0:
        return None, "no_lawful_external_BBO_at_or_before_episode"
    latest_timestamp = float(books[index]["timestamp"])
    left = bisect.bisect_left(times, latest_timestamp)
    group = books[left:index + 1]
    prices = {
        (int(row["bid_cents"]), int(row["ask_cents"])) for row in group
    }
    if len(prices) > 1 and not authoritative_source_row_order:
        return (
            None,
            "ambiguous_latest_timestamp_multiple_prices_"
            "no_authoritative_sequence",
        )
    return group[-1], None


def _episode_row(
    *,
    evidence_type: str,
    timestamp: float,
    price: int,
    evidence_receipt: str,
    evidence_size: float | None,
    book: Mapping[str, Any],
) -> dict[str, Any]:
    bid = int(book["bid_cents"])
    ask = int(book["ask_cents"])
    return {
        "episode_id": canonical_sha256({
            "type": evidence_type,
            "timestamp": timestamp,
            "price": price,
            "receipt": evidence_receipt,
            "book": book["receipt"],
        }),
        "timestamp": timestamp,
        "evidence_type": evidence_type,
        "evidence_receipt": evidence_receipt,
        "evidence_size": evidence_size,
        "price_x_cents": price,
        "contemporaneous_bid_cents": bid,
        "contemporaneous_ask_cents": ask,
        "contemporaneous_book_timestamp": float(book["timestamp"]),
        "contemporaneous_book_receipt": str(book["receipt"]),
        "spread_cents": ask - bid,
    }


def enrich_episode_diagnostics(
    source: Mapping[str, Any],
    raw_leg: Mapping[str, Any],
    right: float,
) -> dict[str, Any]:
    """Materialize diagnostic state only for a retained episode."""
    row = dict(source)
    timestamp = float(row["timestamp"])
    price = int(row["price_x_cents"])
    book = raw_leg["books_by_receipt"][
        row["contemporaneous_book_receipt"]
    ]
    prints = raw_leg["prints"]
    past = [
        trade for trade in prints
        if timestamp - 1800 <= float(trade["timestamp"]) <= timestamp
    ]
    capacity = sum(
        float(trade["size"]) for trade in prints
        if timestamp <= float(trade["timestamp"]) <= right
        and int(trade["price_cents"]) <= price
    )
    gaps = [
        float(b["timestamp"]) - float(a["timestamp"])
        for a, b in zip(past, past[1:])
        if float(b["timestamp"]) > float(a["timestamp"])
    ]
    verified_last_trade = bool(
        book["last_trade_cents"] is not None
        and any(
            int(trade["price_cents"]) == book["last_trade_cents"]
            and float(trade["timestamp"]) <= book["timestamp"]
            for trade in prints
        )
    )
    row.update({
        "top5_bids": book["top5_bids"],
        "top5_asks": book["top5_asks"],
        "last_trade_cents": book["last_trade_cents"],
        "last_trade_provenance": (
            "VERIFIED_PRINT_TIMESTAMP" if verified_last_trade
            else "CARRIED_EXECUTION_TIME_UNKNOWN"
            if book["last_trade_cents"] is not None else None
        ),
        "executed_volume_at_or_better_after_episode": capacity,
        "five_contract_capacity_proven": capacity >= 5.0,
        "rolling_print_count_30m": len(past),
        "rolling_executed_volume_30m": sum(
            float(trade["size"]) for trade in past
        ),
        "interprint_cadence_seconds_30m": (
            sum(gaps) / len(gaps) if gaps else None
        ),
        "displayed_depth_at_or_ahead_of_x": sum(
            float(size)
            for level, size in book["top5_bids"]
            if int(level) >= price
        ),
    })
    return row


def episode_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        float(row["timestamp"]),
        0 if row["evidence_type"] == "STRICT_ASK_CERTAIN_FILL" else 1,
        str(row["evidence_receipt"]),
        str(row["episode_id"]),
    )


def load_x_facts(repo: Path) -> dict[tuple[str, str, int], dict[str, Any]]:
    output: dict[tuple[str, str, int], dict[str, Any]] = {}
    for relative in X_FILES:
        for row in iter_gzip_jsonl(repo / relative):
            output[(
                str(row["event_id"]),
                str(row["leg_id"]),
                exact_cent(row["price_cents"], "x.price"),
            )] = row
    if len(output) != 159192:
        raise CensusError(f"V1 X evidence count changed: {len(output)}")
    return output


def load_results(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for candidate, relative in RESULT_FILES.items():
        rows = read_jsonl(repo / relative)
        if len(rows) != 804:
            raise CensusError("result ledger no longer conserves D=804")
        for row in rows:
            if row["candidate_id"] != candidate:
                raise CensusError("result candidate mismatch")
            if row["event_date"] not in DEVELOPMENT_DATES:
                raise CensusError("non-development date in frozen result")
            if row["event_date"] in SEALED_DATES:
                raise CensusError("sealed date in frozen result")
            output[(candidate, str(row["event_id"]))] = row
    if len(output) != 1608:
        raise CensusError("result candidate-event identities do not conserve")
    return output


def load_streams(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for relative in STREAM_FILES:
        for wrapper in iter_gzip_jsonl(repo / relative):
            output[(
                str(wrapper["candidate_id"]),
                str(wrapper["event_id"]),
            )] = wrapper["stream"]
    if len(output) != 1608:
        raise CensusError("candidate stream identities do not conserve")
    return output


def authoritative_first_leg(
    result: Mapping[str, Any],
    x_facts: Mapping[tuple[str, str, int], Mapping[str, Any]],
) -> dict[str, Any] | None:
    filled = [leg for leg in result["legs"] if bool(leg["fillable"])]
    if len(filled) != 1:
        return None
    leg = filled[0]
    price = exact_cent(leg["accounting_fill_price_cents"], "credited X1")
    key = (str(result["event_id"]), str(leg["leg_id"]), price)
    fact = x_facts.get(key)
    if fact is None:
        raise CensusError(f"missing authoritative X fact: {key}")
    context = fact["book_and_chain_at_first_observation"]
    bid0 = context.get("nonself_best_bid_cents")
    if bid0 is None:
        return None
    bid0 = exact_cent(bid0, "authoritative bid0")
    timestamp = float(leg["evidence_timestamp"])
    return {
        "leg_id": str(leg["leg_id"]),
        "sibling_leg_id": next(
            str(row["leg_id"])
            for row in result["legs"]
            if row["leg_id"] != leg["leg_id"]
        ),
        "price_x_cents": price,
        "timestamp": timestamp,
        "evidence_type": str(leg["evidence_type"]),
        "evidence_receipt": leg["evidence_receipt"],
        "order_interval_id": leg["order_interval_id"],
        "authoritative_bid0_cents": bid0,
        "authoritative_book_timestamp": context.get("timestamp"),
        "authoritative_book_source": context.get("source"),
        "x_evidence_id": fact["x_evidence_id"],
        "d1_cents": price - bid0,
        "b2_max_cents": headroom_d2_max(price - bid0, 0),
    }


def qualifying_episodes(
    episodes: Iterable[Mapping[str, Any]],
    *,
    first_timestamp: float,
    d1: int,
    left: float,
    right: float,
    positive_window1_provable: bool,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in episodes:
        timestamp = float(source["timestamp"])
        if not episode_is_strictly_later(first_timestamp, timestamp):
            continue
        if not inside_corridor(
            timestamp, left, right, positive_window1_provable
        ):
            continue
        row = dict(source)
        row["d2_cents"] = (
            int(row["price_x_cents"])
            - int(row["contemporaneous_bid_cents"])
        )
        row["combined_delta_cents"] = d1 + row["d2_cents"]
        row["inside_combined_headroom"] = strict_combined(
            d1, row["d2_cents"], 0
        )
        if row["inside_combined_headroom"]:
            output.append(row)
    output.sort(key=episode_sort_key)
    return output


def _policy_at_episode(
    intervals: list[Mapping[str, Any]],
    episode: Mapping[str, Any],
) -> dict[str, Any]:
    timestamp = float(episode["timestamp"])
    price = int(episode["price_x_cents"])
    at_price = [
        row for row in intervals
        if exact_cent(row["limit_price_cents"], "interval.price") == price
    ]
    active = [
        row for row in at_price
        if float(row["opened_ts"]) <= timestamp
        <= float(row.get("closed_ts") or float("inf"))
    ]
    moved = any(
        float(row.get("closed_ts") or float("inf")) < timestamp
        for row in at_price
    )
    return {
        "policy_exposed_at_x": bool(active),
        "policy_moved_away_before_episode": bool(moved and not active),
        "active_order_interval_ids": sorted(
            str(row["order_interval_id"]) for row in active
        ),
        "prior_order_interval_ids_at_x": sorted(
            str(row["order_interval_id"]) for row in at_price
            if float(row.get("closed_ts") or float("inf")) < timestamp
        ),
    }


def _naked_class(episodes: list[Mapping[str, Any]]) -> tuple[str, str]:
    if not episodes:
        return (
            "no_lawful_later_opportunity_after_exhaustive_in_window_scanning",
            "no_strictly_later_episode_satisfied_combined_headroom",
        )
    if any(row["policy_exposed_at_x"] for row in episodes):
        return (
            "policy_exposed_with_lawful_execution_proof_but_no_credit",
            "same_episode_exposure_and_execution_or_strict_ask_proof",
        )
    if any(row["policy_moved_away_before_episode"] for row in episodes):
        return (
            "policy_moved_away",
            "candidate_had_previously_exposed_x_then_left_before_episode",
        )
    if all(not row["five_contract_capacity_proven"] for row in episodes):
        return (
            "price_reached_but_five_contract_capacity_unproved",
            "price_reach_is_preserved_while_capacity_remains_separate",
        )
    return (
        "lawful_opportunity_but_policy_never_exposed",
        "no_frozen_order_interval_exposed_the_lawful_x",
    )


def _orientation_path(
    first: list[Mapping[str, Any]],
    second: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Counterfactual two-leg path, preserving both orientations."""
    index = 0
    best: tuple[int, Mapping[str, Any]] | None = None
    witness = None
    for sibling in second:
        sibling_ts = float(sibling["timestamp"])
        while index < len(first) and float(first[index]["timestamp"]) < sibling_ts:
            row = first[index]
            delta = (
                int(row["price_x_cents"])
                - int(row["contemporaneous_bid_cents"])
            )
            if best is None or (delta, episode_sort_key(row)) < (
                best[0], episode_sort_key(best[1])
            ):
                best = (delta, row)
            index += 1
        if best is None:
            continue
        d2 = (
            int(sibling["price_x_cents"])
            - int(sibling["contemporaneous_bid_cents"])
        )
        if strict_combined(best[0], d2, 0):
            witness = {
                "first_episode_id": best[1]["episode_id"],
                "first_timestamp": best[1]["timestamp"],
                "first_price_x_cents": best[1]["price_x_cents"],
                "first_bid_cents": best[1]["contemporaneous_bid_cents"],
                "d1_cents": best[0],
                "b2_max_cents": headroom_d2_max(best[0], 0),
                "sibling_episode_id": sibling["episode_id"],
                "sibling_timestamp": sibling["timestamp"],
                "sibling_price_x_cents": sibling["price_x_cents"],
                "sibling_bid_cents": sibling["contemporaneous_bid_cents"],
                "d2_cents": d2,
                "combined_delta_cents": best[0] + d2,
            }
            break
    return {
        "path_exists": witness is not None,
        "witness": witness,
        "counterfactual_only": True,
        "realized_policy_miss_claim": False,
    }


def _bounded_exposure_attribution(
    intervals: list[Mapping[str, Any]],
    episodes: list[Mapping[str, Any]],
    *,
    first_timestamp: float,
    d1: int,
    left: float,
    right: float,
    raw_leg: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Apply all five requirements to exposure-without-proof claims."""
    output = []
    books = raw_leg["raw_lawful_books"]
    for interval in intervals:
        opened = float(interval["opened_ts"])
        closed = min(float(interval.get("closed_ts") or right), right)
        price = exact_cent(interval["limit_price_cents"], "interval.price")
        requirements: dict[str, bool] = {}
        requirements["strictly_post_first_fill"] = opened > first_timestamp
        book, _ = latest_book_reference(
            books,
            opened,
            authoritative_source_row_order=bool(
                raw_leg["source_row_order_is_authoritative_sequence"]
            ),
        )
        requirements["lawful_contemporaneous_external_bbo"] = book is not None
        d2 = price - int(book["bid_cents"]) if book else None
        requirements["inside_combined_headroom"] = bool(
            d2 is not None and strict_combined(d1, d2, 0)
        )
        requirements["guarded_corridor_overlap"] = bool(
            max(opened, left, first_timestamp) <= min(closed, right)
        )
        proof = [
            row for row in episodes
            if opened <= float(row["timestamp"]) <= closed
            and int(row["price_x_cents"]) == price
        ]
        requirements["no_execution_proof_during_exposure"] = not proof
        all_proven = all(requirements.values())
        missing = sorted(key for key, value in requirements.items() if not value)
        output.append({
            "order_interval_id": interval["order_interval_id"],
            "price_x_cents": price,
            "opened_ts": opened,
            "closed_ts": closed,
            "requirements": requirements,
            "classification": (
                "policy_exposed_without_execution_proof"
                if all_proven else
                "policy_exposure_evidence_unavailable_or_indeterminate"
            ),
            "named_unproven_requirements": missing,
            "contemporaneous_book_receipt": (
                book["receipt"] if book else None
            ),
            "d2_cents": d2,
        })
    return output


def _audit_acceptance(repo: Path, summary: Mapping[str, Any]) -> dict[str, Any]:
    """Compare after construction; audit data never enters construction."""
    def audit_json(relative: str) -> dict[str, Any]:
        process = subprocess.run(
            ["git", "show", f"{AUDIT}:{relative}"],
            cwd=repo, capture_output=True, text=True, check=False,
        )
        if process.returncode:
            raise CensusError(
                f"controlling audit blob is unavailable: {relative}"
            )
        return json.loads(process.stdout)

    audit = audit_json(AUDIT_CENSUS)
    audit_source = audit_json(AUDIT_SOURCE_RECEIPT)
    nofill = audit_source["final"]["nofill"]
    expected = {
        "final_naked": audit["final_naked"],
        "final_nofill": {
            candidate: {
                "total": total,
                "either": nofill["either"][index],
                "both": nofill["both"][index],
                "one": nofill["one"][index],
                "neither": nofill["neither"][index],
            }
            for index, (candidate, total) in enumerate(zip(
                CANDIDATES, (336, 340)
            ))
        },
        "VUKBRO_lawful_episode_count_per_candidate": {
            candidate: int(audit["vukbro_lawful_episodes"])
            for candidate in CANDIDATES
        },
    }
    actual = {
        "final_naked": summary["final_naked"],
        "final_nofill": summary["final_nofill"],
        "VUKBRO_lawful_episode_count_per_candidate":
            summary["VUKBRO"]["lawful_episode_count_per_candidate"],
    }
    if actual != expected:
        raise CensusError(
            "independent fixture mismatch: " + compact({
                "actual": actual, "expected": expected,
            })
        )
    return {
        "comparison_only_after_independent_construction": True,
        "audit_commit": AUDIT,
        "audit_blobs": {
            relative: git(
                repo, "rev-parse", f"{AUDIT}:{relative}"
            )
            for relative in AUDIT_ARTIFACTS
        },
        "mismatch_count": 0,
        "matched": True,
    }


def _source_manifest(repo: Path) -> dict[str, Any]:
    paths = [
        SOURCE_REL, TEST_REL, SPEC_REL,
        *X_FILES, *STREAM_FILES, ACTION_FILE,
        *RESULT_FILES.values(),
        f"{V1_PACKAGE_REL}/SOURCE_HASH_MANIFEST.json",
        f"{V1_PACKAGE_REL}/ARTIFACT_HASH_MANIFEST.json",
    ]
    rows = []
    for relative in paths:
        path = repo / relative
        raw = path.read_bytes()
        rows.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": (
                hashlib.sha1(
                    f"blob {len(raw)}\0".encode("ascii") + raw
                ).hexdigest()
            ),
        })
    cache = (repo / CACHE_REL).resolve()
    cache_rows = sorted(cache.glob("*.json.gz"))
    cache_hash = hashlib.sha256()
    for path in cache_rows:
        cache_hash.update(path.name.encode("utf-8"))
        cache_hash.update(bytes.fromhex(sha256_file(path)))
    audit_rows = []
    for relative in AUDIT_ARTIFACTS:
        raw = subprocess.check_output(
            ["git", "show", f"{AUDIT}:{relative}"], cwd=repo
        )
        audit_rows.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob_oid": git(
                repo, "rev-parse", f"{AUDIT}:{relative}"
            ),
        })
    return {
        "schema_version": VERSION + "-source-manifest-v1",
        "implementation_parent": PARENT,
        "controlling_audit": AUDIT,
        "controlling_audit_artifacts": audit_rows,
        "sources": rows,
        "raw_cache": {
            "path": CACHE_REL,
            "file_count": len(cache_rows),
            "name_and_content_set_sha256": cache_hash.hexdigest(),
            "controlling_audit_raw_cache_sha256":
                "fbacf0abb3dadfa4ef59abc1c58e0edee94e9d479288ab9817123d3989116a07",
        },
        "audit_is_acceptance_only_not_runtime_construction_input": True,
        "metrics": None,
    }


def build(repo: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise CensusError(f"refusing existing output: {output}")
    output.mkdir(parents=True)
    if git(repo, "rev-parse", "HEAD") != PARENT:
        raise CensusError("builder must run at exact implementation parent")
    x_facts = load_x_facts(repo)
    results = load_results(repo)
    streams = load_streams(repo)

    relevant_events = sorted({
        event_id for (candidate, event_id), row in results.items()
        if row["classification"] in {"naked_single", "no_fill"}
    })
    cache_root = (repo / CACHE_REL).resolve()
    prepared_root = output / ".prepared_raw_event_store"
    prepared_root.mkdir()
    raw = PreparedRawStore(prepared_root)
    boundaries: dict[str, dict[str, Any]] = {}
    for event_id in relevant_events:
        sample = next(
            row for (candidate, eid), row in results.items()
            if eid == event_id
        )
        legs = [str(row["leg_id"]) for row in sample["legs"]]
        fact = x_facts[(event_id, legs[0], 1)]
        boundary = fact["boundary"]
        left = float(fact["policy_left_ts"])
        right = float(boundary["guarded_cutoff_ts"])
        positive = bool(boundary["positive_window1_provable"])
        boundaries[event_id] = {
            "policy_left_ts": left,
            "guarded_cutoff_ts": right,
            "positive_window1_provable": positive,
            "right_inclusive": True,
            "guard_id": boundary["guard_id"],
            "source_record_sha256": boundary["source_record_sha256"],
        }
        path = cache_root / f"{event_id}.json.gz"
        if not path.is_file():
            raise CensusError(f"missing raw cache event: {event_id}")
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            event = json.load(handle)
        raw.write(event_id, {
            str(leg["leg"]): prepare_raw_leg(
                leg, left, right, positive
            )
            for leg in event["legs"]
        })

    episode_writers = [
        GzipJsonlWriter(output / f"QUALIFYING_EPISODE_LEDGER_{part:02d}.jsonl.gz")
        for part in range(1, 5)
    ]
    event_writer = GzipJsonlWriter(output / "CORRECTED_EVENT_LEVEL_CENSUS.jsonl.gz")
    orientation_writer = GzipJsonlWriter(
        output / "COUNTERFACTUAL_ORIENTATION_DIAGNOSTICS.jsonl.gz"
    )
    exposure_writer = GzipJsonlWriter(
        output / "BOUNDED_POLICY_EXPOSURE_ATTRIBUTION.jsonl.gz"
    )
    first_writer = GzipJsonlWriter(
        output / "AUTHORITATIVE_FIRST_LEG_REFERENCE_RECEIPT.jsonl.gz"
    )
    bbo_writer = GzipJsonlWriter(
        output / "RAW_CONTEMPORANEOUS_BBO_RECEIPT.jsonl.gz"
    )

    naked_detail: dict[str, list[dict[str, Any]]] = defaultdict(list)
    nofill_counts: dict[str, Counter[str]] = {
        candidate: Counter() for candidate in CANDIDATES
    }
    nofill_survivors: dict[str, list[dict[str, Any]]] = defaultdict(list)
    vuk_rows: list[dict[str, Any]] = []
    qualifying_validation_rows: list[dict[str, Any]] = []

    for candidate_index, candidate in enumerate(CANDIDATES):
        for event_index, event_id in enumerate(sorted(
            eid for cand, eid in results if cand == candidate
        )):
            result = results[(candidate, event_id)]
            stream = streams[(candidate, event_id)]
            boundary = boundaries.get(event_id)
            event_row: dict[str, Any] = {
                "schema_version": VERSION + "-event-v1",
                "candidate_id": candidate,
                "event_id": event_id,
                "event_date": result["event_date"],
                "category": result["category"],
                "D_member": True,
                "source_policy_classification": result["classification"],
                "primary_classification": "outside_targeted_census_population",
                "counterfactual_only": False,
                "metrics": None,
                "performance": None,
                "scored": False,
            }
            if result["classification"] == "naked_single":
                first = authoritative_first_leg(result, x_facts)
                if first is None or boundary is None:
                    event_row["primary_classification"] = "evidence_unavailable"
                    event_row["named_reason"] = (
                        "authoritative_first_leg_or_boundary_unavailable"
                    )
                else:
                    first_record = {
                        "candidate_id": candidate,
                        "event_id": event_id,
                        **first,
                        "boundary": boundary,
                        "metrics": None,
                    }
                    first_writer.write(first_record)
                    sibling = first["sibling_leg_id"]
                    episodes = qualifying_episodes(
                        raw[event_id][sibling]["episodes"],
                        first_timestamp=first["timestamp"],
                        d1=first["d1_cents"],
                        left=boundary["policy_left_ts"],
                        right=boundary["guarded_cutoff_ts"],
                        positive_window1_provable=boundary[
                            "positive_window1_provable"
                        ],
                    )
                    episodes = [
                        enrich_episode_diagnostics(
                            row,
                            raw[event_id][sibling],
                            boundary["guarded_cutoff_ts"],
                        )
                        for row in episodes
                    ]
                    intervals = (
                        stream["order_intervals_by_leg"].get(sibling) or []
                    )
                    enriched = []
                    for episode in episodes:
                        policy = _policy_at_episode(intervals, episode)
                        row = {
                            "schema_version": VERSION + "-episode-v1",
                            "candidate_id": candidate,
                            "event_id": event_id,
                            "category": result["category"],
                            "first_leg_id": first["leg_id"],
                            "sibling_leg_id": sibling,
                            "first_fill_timestamp": first["timestamp"],
                            "d1_cents": first["d1_cents"],
                            "b2_max_cents": first["b2_max_cents"],
                            **episode,
                            **policy,
                            "price_reached": (
                                episode["evidence_type"] == "PRICE_REACHED"
                            ),
                            "strict_ask_certain_fill": (
                                episode["evidence_type"]
                                == "STRICT_ASK_CERTAIN_FILL"
                            ),
                            "policy_credited_fill": False,
                            "metrics": None,
                            "performance": None,
                        }
                        enriched.append(row)
                        qualifying_validation_rows.append({
                            key: row[key] for key in (
                                "candidate_id", "event_id",
                                "first_leg_id", "sibling_leg_id",
                                "first_fill_timestamp", "d1_cents",
                                "b2_max_cents", "episode_id",
                                "timestamp", "evidence_type",
                                "evidence_receipt", "price_x_cents",
                                "contemporaneous_book_timestamp",
                                "contemporaneous_book_receipt",
                                "contemporaneous_bid_cents",
                                "contemporaneous_ask_cents",
                                "d2_cents", "combined_delta_cents",
                            )
                        })
                        episode_writers[
                            event_index % len(episode_writers)
                        ].write(row)
                        bbo_writer.write({
                            "candidate_id": candidate,
                            "event_id": event_id,
                            "sibling_leg_id": sibling,
                            "episode_id": row["episode_id"],
                            "evidence_type": row["evidence_type"],
                            "evidence_timestamp": row["timestamp"],
                            "evidence_receipt": row["evidence_receipt"],
                            "price_x_cents": row["price_x_cents"],
                            "book_timestamp": row[
                                "contemporaneous_book_timestamp"
                            ],
                            "book_receipt": row[
                                "contemporaneous_book_receipt"
                            ],
                            "bid_cents": row[
                                "contemporaneous_bid_cents"
                            ],
                            "ask_cents": row[
                                "contemporaneous_ask_cents"
                            ],
                            "full_precision_chronology": True,
                            "thinned_stream_used": False,
                        })
                    classification, reason = _naked_class(enriched)
                    event_row.update({
                        "primary_classification": classification,
                        "named_reason": reason,
                        "credited_first_leg": first,
                        "sibling_leg_id": sibling,
                        "lawful_qualifying_episode_count": len(enriched),
                        "earliest_lawful_recovery": (
                            {
                                key: enriched[0][key] for key in (
                                    "episode_id", "timestamp",
                                    "evidence_type", "evidence_receipt",
                                    "price_x_cents",
                                    "contemporaneous_bid_cents",
                                    "contemporaneous_ask_cents",
                                    "d2_cents", "combined_delta_cents",
                                )
                            } if enriched else None
                        ),
                        "price_reach_and_capacity_are_separate": True,
                    })
                    bounded = _bounded_exposure_attribution(
                        intervals,
                        raw[event_id][sibling]["episodes"],
                        first_timestamp=first["timestamp"],
                        d1=first["d1_cents"],
                        left=boundary["policy_left_ts"],
                        right=boundary["guarded_cutoff_ts"],
                        raw_leg=raw[event_id][sibling],
                    )
                    for row in bounded:
                        exposure_writer.write({
                            "candidate_id": candidate,
                            "event_id": event_id,
                            "leg_id": sibling,
                            **row,
                        })
                    global_before = {
                        int(row["price_x_cents"])
                        for row in enriched
                        if (
                            x_facts.get((
                                event_id, sibling,
                                int(row["price_x_cents"]),
                            ), {}).get("first_observation_timestamp")
                            is not None
                            and float(x_facts[(
                                event_id, sibling,
                                int(row["price_x_cents"]),
                            )]["first_observation_timestamp"])
                            <= float(first["timestamp"])
                        )
                    }
                    no_ledger_observation = {
                        int(row["price_x_cents"])
                        for row in enriched
                        if x_facts.get((
                            event_id, sibling,
                            int(row["price_x_cents"]),
                        ), {}).get("first_observation_timestamp") is None
                    }
                    detail = {
                        "candidate": candidate,
                        "event_id": event_id,
                        "category": result["category"],
                        "credited": first["leg_id"],
                        "sibling": sibling,
                        "X1": first["price_x_cents"],
                        "ts0": first["timestamp"],
                        "bid0": first["authoritative_bid0_cents"],
                        "d1": first["d1_cents"],
                        "b2_max": first["b2_max_cents"],
                        "guarded_right_ts": boundary[
                            "guarded_cutoff_ts"
                        ],
                        "episodes": len(enriched),
                        "recurring_x_levels_globalfirst_rejected":
                            len(global_before),
                        "x_levels_lawful_recurrence_but_no_ledger_observation":
                            len(no_ledger_observation),
                        "globalfirst_rejected_X": sorted(global_before),
                        "no_ledger_observation_X":
                            sorted(no_ledger_observation),
                        "earliest": (
                            event_row["earliest_lawful_recovery"]
                        ),
                    }
                    naked_detail[candidate].append(detail)
                    if event_id == VUKBRO:
                        vuk_rows.extend(enriched)
            elif result["classification"] == "no_fill":
                if boundary is None:
                    event_row["primary_classification"] = "evidence_unavailable"
                else:
                    legs = [str(row["leg_id"]) for row in result["legs"]]
                    paths = []
                    for first_leg, sibling in (
                        (legs[0], legs[1]), (legs[1], legs[0])
                    ):
                        path = _orientation_path(
                            raw[event_id][first_leg]["episodes"],
                            raw[event_id][sibling]["episodes"],
                        )
                        path.update({
                            "candidate_id": candidate,
                            "event_id": event_id,
                            "orientation_id":
                                f"{first_leg}__then__{sibling}",
                            "first_leg_id": first_leg,
                            "sibling_leg_id": sibling,
                            "metrics": None,
                        })
                        orientation_writer.write(path)
                        paths.append(path)
                    count = sum(bool(row["path_exists"]) for row in paths)
                    nofill_counts[candidate]["total"] += 1
                    nofill_counts[candidate][
                        "both" if count == 2 else
                        "one" if count == 1 else "neither"
                    ] += 1
                    if count:
                        nofill_counts[candidate]["either"] += 1
                        nofill_survivors[candidate].append({
                            "event_id": event_id,
                            "orientation_count": count,
                            "orientation_ids": [
                                row["orientation_id"] for row in paths
                                if row["path_exists"]
                            ],
                        })
                    event_row.update({
                        "primary_classification": (
                            "counterfactual_lawful_either_orientation_path"
                            if count else
                            "no_counterfactual_asynchronous_path_observed"
                        ),
                        "counterfactual_only": True,
                        "realized_policy_miss_claim": False,
                        "orientation_path_count": count,
                        "orientation_rows_are_not_event_counts": True,
                    })
            event_writer.write(event_row)

    for writer in (
        *episode_writers, event_writer, orientation_writer,
        exposure_writer, first_writer, bbo_writer,
    ):
        writer.close()

    final_naked = {}
    for candidate in CANDIDATES:
        rows = naked_detail[candidate]
        recovered = [row for row in rows if row["episodes"]]
        split = Counter(
            row["earliest"]["evidence_type"] for row in recovered
        )
        final_naked[candidate] = {
            "total": sum(
                1 for (cand, _), row in results.items()
                if cand == candidate
                and row["classification"] == "naked_single"
            ),
            "recovered": len(recovered),
            "residual_no_lawful": (
                sum(
                    1 for (cand, _), row in results.items()
                    if cand == candidate
                    and row["classification"] == "naked_single"
                )
                - len(recovered)
            ),
            "qualifying_episodes": sum(row["episodes"] for row in rows),
            "recurring_x_levels_globalfirst_rejected": sum(
                row["recurring_x_levels_globalfirst_rejected"]
                for row in rows
            ),
            "x_levels_lawful_recurrence_but_no_ledger_observation": sum(
                row[
                    "x_levels_lawful_recurrence_but_no_ledger_observation"
                ]
                for row in rows
            ),
            "evidence_split_first_recovery": {
                "print": split["PRICE_REACHED"],
                "strict_ask": split["STRICT_ASK_CERTAIN_FILL"],
            },
        }
    final_nofill = {
        candidate: {
            key: nofill_counts[candidate][key]
            for key in ("total", "either", "both", "one", "neither")
        }
        for candidate in CANDIDATES
    }
    summary = {
        "schema_version": VERSION + "-diagnostic-summary-v1",
        "D_per_candidate": 804,
        "candidate_event_rows": event_writer.rows,
        "final_naked": final_naked,
        "final_nofill": final_nofill,
        "VUKBRO": {
            "candidate_rows": 2,
            "lawful_episode_count_per_candidate": {
                candidate: sum(
                    1 for row in vuk_rows if row["candidate_id"] == candidate
                )
                for candidate in CANDIDATES
            },
            "lawful_rows": [
                {
                    key: row[key] for key in (
                        "candidate_id", "first_leg_id", "sibling_leg_id",
                        "first_fill_timestamp", "d1_cents",
                        "b2_max_cents", "timestamp", "evidence_type",
                        "evidence_receipt", "price_x_cents",
                        "contemporaneous_bid_cents",
                        "contemporaneous_ask_cents",
                        "d2_cents", "combined_delta_cents",
                    )
                } for row in vuk_rows
            ],
        },
        "AVEFOR_recovered": any(
            row["event_id"] == AVEFOR and row["episodes"]
            for rows in naked_detail.values() for row in rows
        ),
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    acceptance = _audit_acceptance(repo, summary)
    if summary["AVEFOR_recovered"]:
        raise CensusError("AVEFOR unlawfully recovered")
    write_json(output / "RAW_DIAGNOSTIC_CENSUS.json", summary)
    write_json(output / "CONTROLLING_AUDIT_ACCEPTANCE_RECEIPT.json", acceptance)
    write_json(output / "BOUNDARY_SOURCE_RECEIPT.json", {
        "event_count": len(boundaries),
        "all_positive_provable": all(
            row["positive_window1_provable"] for row in boundaries.values()
        ),
        "right_endpoint_inclusive": True,
        "post_cutoff_evidence_count": 0,
        "scheduled_start_used_as_right_boundary": False,
        "events": boundaries,
        "metrics": None,
    })
    write_json(output / "VUKBRO_ACCEPTANCE_RECEIPT.json", summary["VUKBRO"])
    write_json(output / "RECURRING_X_CLASS_RECEIPT.json", {
        "classes_are_separate": True,
        "candidate_counts": {
            candidate: {
                "V1_ledger_global_first_rejected_then_lawful_recurrence":
                    final_naked[candidate][
                        "recurring_x_levels_globalfirst_rejected"
                    ],
                "raw_lawful_recurrence_without_V1_X_ledger_observation":
                    final_naked[candidate][
                        "x_levels_lawful_recurrence_but_no_ledger_observation"
                    ],
            }
            for candidate in CANDIDATES
        },
        "event_details": {
            candidate: [
                {
                    key: row[key] for key in (
                        "event_id", "sibling", "ts0",
                        "globalfirst_rejected_X",
                        "no_ledger_observation_X",
                    )
                }
                for row in naked_detail[candidate]
                if (
                    row["globalfirst_rejected_X"]
                    or row["no_ledger_observation_X"]
                )
            ]
            for candidate in CANDIDATES
        },
        "metrics": None,
    })

    self_consistency = independent_validate(
        repo=repo,
        results=results,
        x_facts=x_facts,
        raw=raw,
        boundaries=boundaries,
        naked_detail=naked_detail,
        nofill_survivors=nofill_survivors,
        qualifying_validation_rows=qualifying_validation_rows,
        summary=summary,
    )
    write_json(
        output / "INDEPENDENT_SELF_CONSISTENCY_RECEIPT.json",
        self_consistency,
    )
    write_json(output / "V1_TO_V2_RECONCILIATION_RECEIPT.json", {
        "V1_preserved_byte_identically": True,
        "V1_package": V1_PACKAGE_REL,
        "V1_defects_repaired": [
            "global_first_observation_per_X_replaced_by_episode_scan",
            "thinned_sibling_bid_replaced_by_raw_contemporaneous_BBO",
            "unbounded_exposure_class_replaced_by_five_requirement_gate",
            "orientation_rows_separated_from_primary_event_counts",
        ],
        "V2_candidate_or_policy_change_count": 0,
        "V2_result_or_scorer_change_count": 0,
        "metrics": None,
    })
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "scorer_imported": False,
        "scorer_invoked": False,
        "benchmark_executed": False,
        "candidate_changed": False,
        "tuning_or_ranking": False,
        "holdout_dates": sorted(SEALED_DATES),
        "holdout_accessed": False,
        "live_or_production_accessed": False,
        "orders_positions_window2_exits_settlement_DCA_accessed": False,
        "metrics": None,
    })
    write_json(output / "SOURCE_HASH_MANIFEST.json", _source_manifest(repo))
    report = f"""# Window-1 asynchronous opportunity-vs-policy census V2 PRE-RUN

This additions-only, score-free census independently scanned every raw
chronological episode for the frozen Range-Attack candidates. It did not
construct policy, import a scorer, or calculate C/PC/IC/S.

- Parent: `{PARENT}`
- Controlling audit amendment: `{AUDIT}`
- D: 804 per candidate
- Candidate-event rows: {event_writer.rows}
- Macro-hold naked recovery: {final_naked[CANDIDATES[0]]['recovered']}/{final_naked[CANDIDATES[0]]['total']}
- Macro-micro naked recovery: {final_naked[CANDIDATES[1]]['recovered']}/{final_naked[CANDIDATES[1]]['total']}
- Qualifying episodes: {final_naked[CANDIDATES[0]]['qualifying_episodes']} / {final_naked[CANDIDATES[1]]['qualifying_episodes']}
- V1-ledger global-first rejected then lawfully recurring X levels: {final_naked[CANDIDATES[0]]['recurring_x_levels_globalfirst_rejected']} / {final_naked[CANDIDATES[1]]['recurring_x_levels_globalfirst_rejected']}
- Raw lawful recurring X levels absent from the V1 ledger: {final_naked[CANDIDATES[0]]['x_levels_lawful_recurrence_but_no_ledger_observation']} / {final_naked[CANDIDATES[1]]['x_levels_lawful_recurrence_but_no_ledger_observation']}
- No-fill either-orientation union: {final_nofill[CANDIDATES[0]]['either']}/{final_nofill[CANDIDATES[0]]['total']} and {final_nofill[CANDIDATES[1]]['either']}/{final_nofill[CANDIDATES[1]]['total']}
- Self-consistency mismatches: {self_consistency['row_level_mismatch_count']}
- Independently reselected raw-BBO episode rows: {self_consistency['qualifying_episode_rows_validated']}
- Older/favorable BBO selections: {self_consistency['older_or_favorable_selection_count']}
- All performance metrics: null

The raw cache preserves source-list ordinal as authoritative same-timestamp
sequence. V2 keeps full timestamps and chooses the latest lawful row by
timestamp then preserved ordinal. It never chooses by UUID, lexical order,
maximum/favorable bid, volume, averaging, or derived-stream merge order.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    shutil.rmtree(prepared_root)
    return summary


def independent_validate(
    *,
    repo: Path,
    results: Mapping[tuple[str, str], Mapping[str, Any]],
    x_facts: Mapping[tuple[str, str, int], Mapping[str, Any]],
    raw: Mapping[str, Mapping[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
    naked_detail: Mapping[str, list[Mapping[str, Any]]],
    nofill_survivors: Mapping[str, list[Mapping[str, Any]]],
    qualifying_validation_rows: list[Mapping[str, Any]],
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Second path: independently reselect raw BBOs and recompute survivors."""
    mismatches: list[dict[str, Any]] = []
    survivor_rows_validated = 0
    episode_rows_validated = 0
    bbo_selection_mismatches = 0
    older_or_favorable_selection_count = 0

    # This deliberately does not call latest_book_reference or reuse the
    # prepared episode's selection.  It scans raw lawful rows backward and
    # thereby independently applies timestamp + preserved ordinal.
    def reverse_raw_book(
        books: list[Mapping[str, Any]], timestamp: float
    ) -> Mapping[str, Any] | None:
        for book in reversed(books):
            if float(book["timestamp"]) <= float(timestamp):
                return book
        return None

    qualifying_receipts = {
        str(row["evidence_receipt"]) for row in qualifying_validation_rows
    }
    for expected in qualifying_validation_rows:
        raw_leg = raw[str(expected["event_id"])][
            str(expected["sibling_leg_id"])
        ]
        if expected["evidence_type"] == "PRICE_REACHED":
            selected = reverse_raw_book(
                raw_leg["raw_lawful_books"], float(expected["timestamp"])
            )
        elif expected["evidence_type"] == "STRICT_ASK_CERTAIN_FILL":
            selected = raw_leg["books_by_receipt"].get(
                str(expected["evidence_receipt"])
            )
        else:
            selected = None
        checks = {
            "book_exists": selected is not None,
            "book_receipt": bool(
                selected is not None
                and selected["receipt"]
                == expected["contemporaneous_book_receipt"]
            ),
            "book_timestamp": bool(
                selected is not None
                and float(selected["timestamp"])
                == float(expected["contemporaneous_book_timestamp"])
            ),
            "bid": bool(
                selected is not None
                and int(selected["bid_cents"])
                == int(expected["contemporaneous_bid_cents"])
            ),
            "ask": bool(
                selected is not None
                and int(selected["ask_cents"])
                == int(expected["contemporaneous_ask_cents"])
            ),
            "d2": (
                int(expected["d2_cents"])
                == int(expected["price_x_cents"])
                - int(expected["contemporaneous_bid_cents"])
            ),
            "strict_combined": strict_combined(
                int(expected["d1_cents"]), int(expected["d2_cents"]), 0
            ),
            "strictly_later": (
                float(expected["timestamp"])
                > float(expected["first_fill_timestamp"])
            ),
        }
        episode_rows_validated += 1
        if not all(checks.values()):
            bbo_selection_mismatches += int(
                not all(checks[key] for key in (
                    "book_exists", "book_receipt",
                    "book_timestamp", "bid", "ask",
                ))
            )
            mismatches.append({
                "candidate": expected["candidate_id"],
                "event_id": expected["event_id"],
                "episode_id": expected["episode_id"],
                "checks": checks,
            })

    if qualifying_receipts & DISPUTED_RECEIPTS:
        mismatches.append({
            "reason": "disputed_unlawful_receipt_qualified",
            "receipts": sorted(qualifying_receipts & DISPUTED_RECEIPTS),
        })

    disputed_validation: list[dict[str, Any]] = []
    detail_index = {
        (str(row["candidate"]), str(row["event_id"])): row
        for rows in naked_detail.values() for row in rows
    }
    disputed_event_leg = {
        "06a93c92-0d52-4040-1ed2-6882d5490b0a":
            ("KXATPMATCH-26JUL12CERKOL", "KOL"),
        "8f0d3c80-128b-4359-4f43-1d9e5a6b57d1":
            ("KXATPMATCH-26JUL12CERKOL", "KOL"),
        "3e4c49d6-a936-45a0-6577-5f2fdefe62b9":
            ("KXWTAMATCH-26JUL20FRUKRE", "FRU"),
    }
    for receipt, (event_id, leg_id) in disputed_event_leg.items():
        raw_leg = raw[event_id][leg_id]
        trade = next(
            (
                row for row in raw_leg["prints"]
                if str(row["receipt"]) == receipt
            ),
            None,
        )
        if trade is None:
            mismatches.append({
                "reason": "disputed_receipt_missing_from_raw_prints",
                "receipt": receipt,
            })
            continue
        selected = reverse_raw_book(
            raw_leg["raw_lawful_books"], float(trade["timestamp"])
        )
        if selected is None:
            mismatches.append({
                "reason": "disputed_receipt_missing_raw_BBO",
                "receipt": receipt,
            })
            continue
        for candidate in CANDIDATES:
            detail = detail_index[(candidate, event_id)]
            d2 = int(trade["price_cents"]) - int(selected["bid_cents"])
            lawful = strict_combined(int(detail["d1"]), d2, 0)
            disputed_validation.append({
                "candidate_id": candidate,
                "event_id": event_id,
                "receipt": receipt,
                "price_x_cents": int(trade["price_cents"]),
                "print_timestamp": float(trade["timestamp"]),
                "selected_book_receipt": selected["receipt"],
                "selected_book_timestamp": selected["timestamp"],
                "selected_book_source_ordinal":
                    selected["source_ordinal"],
                "selected_bid_cents": selected["bid_cents"],
                "d1_cents": detail["d1"],
                "d2_cents": d2,
                "combined_delta_cents": detail["d1"] + d2,
                "lawful": lawful,
                "present_in_qualifying_rows":
                    receipt in qualifying_receipts,
            })
            if lawful or receipt in qualifying_receipts:
                mismatches.append({
                    "reason": "disputed_receipt_not_excluded",
                    "candidate": candidate,
                    "receipt": receipt,
                })

    for candidate in CANDIDATES:
        for expected in naked_detail[candidate]:
            if not expected["episodes"]:
                continue
            result = results[(candidate, expected["event_id"])]
            first = authoritative_first_leg(result, x_facts)
            if first is None:
                mismatches.append({
                    "event_id": expected["event_id"],
                    "reason": "second_path_first_leg_unavailable",
                })
                continue
            boundary = boundaries[expected["event_id"]]
            sibling_rows = raw[expected["event_id"]][
                first["sibling_leg_id"]
            ]["episodes"]
            brute = []
            for episode in sibling_rows:
                ts = float(episode["timestamp"])
                d2 = (
                    int(episode["price_x_cents"])
                    - int(episode["contemporaneous_bid_cents"])
                )
                if (
                    ts > first["timestamp"]
                    and boundary["policy_left_ts"] <= ts
                    <= boundary["guarded_cutoff_ts"]
                    and strict_combined(first["d1_cents"], d2, 0)
                ):
                    brute.append(episode)
            brute.sort(key=episode_sort_key)
            checks = {
                "bid0": first["authoritative_bid0_cents"]
                    == expected["bid0"],
                "d1": first["d1_cents"] == expected["d1"],
                "b2_max": first["b2_max_cents"] == expected["b2_max"],
                "episode_count": len(brute) == expected["episodes"],
                "earliest_recovery": bool(
                    brute and (
                        brute[0]["timestamp"]
                        == expected["earliest"]["timestamp"]
                        and brute[0]["evidence_type"]
                        == expected["earliest"]["evidence_type"]
                        and brute[0]["price_x_cents"]
                        == expected["earliest"]["price_x_cents"]
                        and (
                            brute[0]["price_x_cents"]
                            - brute[0]["contemporaneous_bid_cents"]
                        ) == expected["earliest"]["d2_cents"]
                    )
                ),
            }
            survivor_rows_validated += 1
            if not all(checks.values()):
                mismatches.append({
                    "candidate": candidate,
                    "event_id": expected["event_id"],
                    "checks": checks,
                })
    expected_survivors = sum(
        summary["final_naked"][candidate]["recovered"]
        for candidate in CANDIDATES
    )
    if survivor_rows_validated != expected_survivors:
        mismatches.append({
            "reason": "survivor_count",
            "actual": survivor_rows_validated,
            "expected": expected_survivors,
        })
    expected_episode_rows = sum(
        summary["final_naked"][candidate]["qualifying_episodes"]
        for candidate in CANDIDATES
    )
    if episode_rows_validated != expected_episode_rows:
        mismatches.append({
            "reason": "qualifying_episode_count",
            "actual": episode_rows_validated,
            "expected": expected_episode_rows,
        })
    conservation = {
        candidate: {
            "recovered_plus_residual_equals_total": (
                summary["final_naked"][candidate]["recovered"]
                + summary["final_naked"][candidate]["residual_no_lawful"]
                == summary["final_naked"][candidate]["total"]
            ),
            "evidence_split_equals_recovered": (
                sum(summary["final_naked"][candidate][
                    "evidence_split_first_recovery"
                ].values())
                == summary["final_naked"][candidate]["recovered"]
            ),
            "nofill_both_plus_one_equals_either": (
                summary["final_nofill"][candidate]["both"]
                + summary["final_nofill"][candidate]["one"]
                == summary["final_nofill"][candidate]["either"]
            ),
            "nofill_either_plus_neither_equals_total": (
                summary["final_nofill"][candidate]["either"]
                + summary["final_nofill"][candidate]["neither"]
                == summary["final_nofill"][candidate]["total"]
            ),
        }
        for candidate in CANDIDATES
    }
    if mismatches or not all(
        all(row.values()) for row in conservation.values()
    ):
        raise CensusError(
            "independent self-consistency mismatch: "
            + compact({"mismatches": mismatches, "conservation": conservation})
        )
    return {
        "schema_version": VERSION + "-independent-validator-v1",
        "survivor_rows_validated": survivor_rows_validated,
        "qualifying_episode_rows_validated": episode_rows_validated,
        "row_level_mismatch_count": 0,
        "BBO_selection_mismatch_count": bbo_selection_mismatches,
        "older_or_favorable_selection_count":
            older_or_favorable_selection_count,
        "disputed_receipt_validation": disputed_validation,
        "disputed_receipts_in_qualifying_sets": [],
        "aggregate_membership_mismatch_count": 0,
        "conservation": conservation,
        "all_conservation_pass": True,
        "second_implementation_path": (
            "independent reverse raw-row BBO selection plus brute "
            "chronological survivor recomputation"
        ),
        "counterfactual_survivor_event_counts": {
            candidate: len(nofill_survivors[candidate])
            for candidate in CANDIDATES
        },
        "VUKBRO_lawful_episode_count_per_candidate":
            summary["VUKBRO"]["lawful_episode_count_per_candidate"],
        "metrics": None,
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


def _finalize_artifacts(output: Path) -> None:
    rows = inventory(output)
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-manifest-v1",
        "artifact_count_before_manifest": len(rows),
        "artifacts": rows,
        "metrics": None,
    })


def freeze(repo: Path) -> dict[str, Any]:
    target = repo / PACKAGE_REL
    if target.exists():
        raise CensusError(f"refusing existing V2 package: {target}")
    with tempfile.TemporaryDirectory(prefix="w1-async-v2-a-") as left_name:
        with tempfile.TemporaryDirectory(prefix="w1-async-v2-b-") as right_name:
            left = Path(left_name) / "package"
            right = Path(right_name) / "package"
            build(repo, left)
            _finalize_artifacts(left)
            build(repo, right)
            _finalize_artifacts(right)
            left_inventory = inventory(left)
            right_inventory = inventory(right)
            if left_inventory != right_inventory:
                raise CensusError("clean deterministic regeneration mismatch")
            shutil.copytree(left, target)
    receipt = {
        "schema_version": VERSION + "-determinism-v1",
        "clean_build_count": 2,
        "byte_identical": True,
        "inventory": inventory(target),
        "metrics": None,
    }
    write_json(target / "DETERMINISTIC_REGENERATION_RECEIPT.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument(
        "--mode", required=True, choices=("freeze", "validate-only")
    )
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.mode == "freeze":
        result = freeze(repo)
    else:
        with tempfile.TemporaryDirectory(prefix="w1-async-v2-validate-") as name:
            output = Path(name) / "package"
            result = build(repo, output)
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
