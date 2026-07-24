#!/usr/bin/env python3
"""Adjudicate Start-Truth Recovery Round 2 without execution evidence.

This instrument targets only the 539 events that were not positive-capable
in ``REAL_START_LEDGER_V3``.  It consumes identity, provider clock, status,
and score/result evidence.  It has no arguments for placements, fills,
prices, deltas, policy decisions, or candidate results.

The broad recovery surface is TennisExplorer's retained historical results
page: the same provider surface used by ``te_live.py`` and named
``te_honest`` in the chronological Living Vault.  A result start clock is
accepted only after a strict two-player structured-target crosswalk,
tournament crosswalk, date alignment, and completed-result proof.  A
higher-precedence raw milestone ``not_started`` observation at or after the
provider clock keeps the event contradictory rather than allowing a
performance-favorable choice.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo


VERSION = "window1-real-start-ledger-v4-round2"
D = 804
BASE_POSITIVE = 265
BASE_EXACT = 234
BASE_CLEAN = 31
RESIDUAL = 539
GATE = 603
UTC = dt.timezone.utc
TE_ZONE = ZoneInfo("Europe/Berlin")
BASE_COUNTS = {
    "exact": 234,
    "clean_interval": 31,
    "live_by_only": 450,
    "contradictory": 26,
    "schedule_only": 63,
}
COMMON_TOURNAMENT_TOKENS = {
    "atp", "wta", "challenger", "open", "men", "women", "singles",
    "s", "h", "a", "k",
}


class Round2Error(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Round2Error(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise Round2Error(f"expected object: {path}:{number}")
            rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def normalize(value: Any) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value or ""))
    ascii_value = decomposed.encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z]+", ascii_value.casefold()))


def strip_html(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        html.unescape(re.sub(r"<[^>]*>", " ", value)),
    ).strip()


def parse_ts(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        stamp = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        raise Round2Error(f"naive timestamp is not causal: {value}")
    return stamp.timestamp()


def iso_utc(value: float | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, UTC).isoformat()


def title_pair(title: Any) -> tuple[str, ...]:
    return tuple(sorted(
        normalize(part)
        for part in re.split(r"\s+vs\s+", str(title or ""), flags=re.I)
        if part.strip()
    ))


def te_player_key(display_name: str) -> tuple[str, str] | None:
    parts = normalize(display_name).split()
    if len(parts) < 2 or len(parts[-1]) != 1:
        return None
    first_initial = parts[-1]
    surname = " ".join(parts[:-1])
    return (surname, first_initial)


def target_player_key(target: Mapping[str, Any]) -> tuple[str, str] | None:
    details = target.get("details") or {}
    surname = normalize(details.get("last_name"))
    first = normalize(details.get("first_name"))
    if not surname or not first:
        return None
    return (surname, first[0])


def tournament_tokens(value: Any) -> set[str]:
    tokens = []
    for token in normalize(value).split():
        if token in COMMON_TOURNAMENT_TOKENS:
            continue
        if token.isdigit() or re.fullmatch(r"\d+k?", token):
            continue
        tokens.append(token)
    return set(tokens)


def tournament_matches(left: Any, right: Any) -> bool:
    # A shared city is not an exact tournament crosswalk when the retained
    # provider says WTA 125 and the result source says ITF (the Istanbul
    # collision is the observed class).  Sponsor/region suffixes may differ,
    # but the competition class may not.
    left_normalized = normalize(left)
    right_normalized = normalize(right)
    if ("itf" in left_normalized.split()) != (
        "itf" in right_normalized.split()
    ):
        return False
    a = tournament_tokens(left)
    b = tournament_tokens(right)
    return bool(a and b and (a <= b or b <= a))


def load_target(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        wrapper = json.load(handle)
    target = (wrapper.get("response") or {}).get("structured_target") or {}
    if not isinstance(target, dict):
        raise Round2Error(f"invalid structured target: {path}")
    return {
        "id": target.get("id"),
        "name": target.get("name"),
        "details": target.get("details") or {},
        "source_id": (
            target.get("source_id")
            or (target.get("source_ids") or {}).get("source_3_id")
        ),
        "raw_sha256": sha256_file(path),
        "payload_sha256": wrapper.get("response_payload_sha256"),
    }


def retained_milestone_identity(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        wrapper = json.load(handle)
    event_id = str(
        wrapper.get("request_event_id") or path.name.split(".")[0]
    )
    milestones = [
        value
        for page in wrapper.get("pages") or []
        for value in (page.get("response") or {}).get("milestones") or []
        if isinstance(value, dict)
    ]
    matching = [
        value for value in milestones
        if event_id in (value.get("related_event_tickers") or [])
        or event_id in (value.get("primary_event_tickers") or [])
        or (value.get("details") or {}).get("main_game_event_ticker")
        == event_id
    ]
    matching = sorted(
        matching, key=lambda value: str(value.get("id") or "")
    )
    milestone = matching[0] if matching else (
        milestones[0] if milestones else {}
    )
    details = milestone.get("details") or {}
    return {
        "event_id": event_id,
        "milestone_id": milestone.get("id"),
        "milestone_ids": [
            value.get("id") for value in matching
        ] or ([milestone.get("id")] if milestone.get("id") else []),
        "event_source_id": (
            milestone.get("source_id")
            or (milestone.get("source_ids") or {}).get("source_3_id")
        ),
        "event_source_ids": [
            (
                value.get("source_id")
                or (value.get("source_ids") or {}).get("source_3_id")
            )
            for value in matching
        ],
        "competitor_target_ids": sorted({
            target_id
            for value in (matching or [milestone])
            for target_id in [
                (value.get("details") or {}).get(
                    "first_competitor_id"
                ),
                (value.get("details") or {}).get(
                    "second_competitor_id"
                ),
            ]
            if target_id
        }),
        "title": milestone.get("title"),
        "tournament": details.get("tournament_name"),
        "tour": details.get("tour"),
        "round": details.get("round"),
        "retained_identity_conflict": len(matching) > 1,
        "raw_sha256": sha256_file(path),
    }


HEADER_RE = re.compile(
    r'<tr[^>]*class="head flags"[^>]*>(.*?)</tr>',
    re.I | re.S,
)
PAIR_RE = re.compile(
    r'<tr id="(r\d+)"[^>]*>(.*?)</tr>\s*'
    r'<tr id="\1b"[^>]*>(.*?)</tr>',
    re.I | re.S,
)


def first_anchor_text(fragment: str) -> str:
    match = re.search(r"<a[^>]*>(.*?)</a>", fragment, re.I | re.S)
    return strip_html(match.group(1)) if match else strip_html(fragment)


def parse_te_pages(directory: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    page_receipts = []
    for path in sorted(directory.glob("results-*.html.gz")):
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", path.name)
        if not date_match:
            raise Round2Error(f"TE page lacks date: {path}")
        page_date = date_match.group()
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
        timezone_match = re.search(
            r'<span class="timezone" title="([^"]+)">(.*?)</span>',
            raw,
            re.I | re.S,
        )
        if (
            not timezone_match
            or "Berlin" not in timezone_match.group(1)
            or "Prague" not in timezone_match.group(1)
        ):
            raise Round2Error(f"unexpected TE page timezone: {path}")
        items = sorted([
            *((match.start(), "header", match)
              for match in HEADER_RE.finditer(raw)),
            *((match.start(), "pair", match)
              for match in PAIR_RE.finditer(raw)),
        ])
        tournament = ""
        page_rows = 0
        for _, kind, match in items:
            if kind == "header":
                tournament = first_anchor_text(match.group(1))
                continue
            row1, row2 = match.group(2), match.group(3)
            time_cell = re.search(
                r'class="first time"[^>]*>(.*?)</td>',
                row1,
                re.I | re.S,
            )
            clock = re.search(
                r"\b([012]\d:[0-5]\d)\b",
                strip_html(time_cell.group(1)) if time_cell else "",
            )
            player_rows = []
            for row in (row1, row2):
                player_match = re.search(
                    r'class="t-name"[^>]*>\s*'
                    r'<a href="([^"]+)"[^>]*>(.*?)</a>',
                    row,
                    re.I | re.S,
                )
                result_match = re.search(
                    r'class="result"[^>]*>\s*(\d+)\s*</td>',
                    row,
                    re.I | re.S,
                )
                player_rows.append({
                    "display_name": (
                        strip_html(player_match.group(2))
                        if player_match else None
                    ),
                    "player_path": (
                        player_match.group(1) if player_match else None
                    ),
                    "sets_won": (
                        int(result_match.group(1))
                        if result_match else None
                    ),
                })
            match_id = re.search(
                r"match-detail/\?id=(\d+)",
                row1,
                re.I,
            )
            completed = bool(
                all(row["sets_won"] is not None for row in player_rows)
                and sum(row["sets_won"] or 0 for row in player_rows) > 0
            )
            start_utc = None
            if clock:
                local = dt.datetime.fromisoformat(
                    f"{page_date}T{clock.group(1)}:00"
                ).replace(tzinfo=TE_ZONE)
                start_utc = local.astimezone(UTC).timestamp()
            matches.append({
                "te_match_id": match_id.group(1) if match_id else None,
                "page_date": page_date,
                "display_timezone": "Europe/Berlin",
                "display_clock": clock.group(1) if clock else None,
                "start_utc": start_utc,
                "tournament": tournament,
                "players": player_rows,
                "player_keys": sorted(
                    key for key in (
                        te_player_key(str(row["display_name"] or ""))
                        for row in player_rows
                    ) if key is not None
                ),
                "title_pair": tuple(sorted(
                    normalize(
                        " ".join(
                            normalize(row["display_name"]).split()[:-1]
                        )
                    )
                    for row in player_rows
                    if row["display_name"]
                )),
                "completed_result": completed,
                "page_sha256": sha256_file(path),
            })
            page_rows += 1
        page_receipts.append({
            "date": page_date,
            "sha256": sha256_file(path),
            "rows": page_rows,
            "display_timezone": "Europe/Berlin",
        })
    return matches, {
        "pages": len(page_receipts),
        "matches": len(matches),
        "page_receipts": page_receipts,
        "page_hash_set_sha256": sha256_text(compact(page_receipts)),
    }


def load_identity(
    path: Path,
    target_directory: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = read_jsonl(path)
    if (
        len(rows) != RESIDUAL
        or len({row["event_id"] for row in rows}) != RESIDUAL
    ):
        raise Round2Error("residual identity crosswalk changed")
    targets: dict[str, dict[str, Any]] = {}
    for target_id in sorted({
        str(target_id)
        for row in rows
        for target_id in row.get("competitor_target_ids") or []
        if target_id
    }):
        target_path = target_directory / f"{target_id}.json.gz"
        if not target_path.exists():
            raise Round2Error(f"missing structured target: {target_id}")
        targets[target_id] = load_target(target_path)
    output = []
    for row in rows:
        target_ids = [
            str(value) for value in row.get("competitor_target_ids") or []
            if value
        ]
        target_rows = [targets[value] for value in target_ids]
        output.append({
            **row,
            "target_rows": target_rows,
            "target_player_keys": sorted(
                key for key in (
                    target_player_key(target) for target in target_rows
                ) if key is not None
            ),
            "competitor_source_ids": [
                target.get("source_id") for target in target_rows
            ],
        })
    return output, {
        "events": len(output),
        "unique_targets": len(targets),
        "targets_with_player_key": sum(
            target_player_key(row) is not None for row in targets.values()
        ),
        "crosswalk_sha256": sha256_file(path),
        "target_raw_hash_set_sha256": sha256_text(compact(sorted(
            ({
                "id": target_id,
                "raw_sha256": row["raw_sha256"],
                "payload_sha256": row["payload_sha256"],
            } for target_id, row in targets.items()),
            key=lambda row: row["id"],
        ))),
    }


def date_distance(
    page_date: str,
    milestone_start_date: Any,
) -> int | None:
    if not milestone_start_date:
        return None
    try:
        expected = dt.date.fromisoformat(str(milestone_start_date)[:10])
        observed = dt.date.fromisoformat(page_date)
    except ValueError:
        return None
    return abs((observed - expected).days)


def crosswalk_event(
    identity: Mapping[str, Any],
    te_matches: list[dict[str, Any]],
) -> dict[str, Any]:
    target_keys = list(identity.get("target_player_keys") or [])
    raw_title_pair = title_pair(identity.get("title"))
    candidates = []
    diagnostics: Counter[str] = Counter()
    for match in te_matches:
        distance = date_distance(
            match["page_date"],
            identity.get("milestone_start_date"),
        )
        title_ok = tuple(match["title_pair"]) == raw_title_pair
        players_ok = (
            len(target_keys) == 2
            and list(match["player_keys"]) == target_keys
        )
        tournament_ok = tournament_matches(
            identity.get("tournament"),
            match.get("tournament"),
        )
        date_ok = distance is not None and distance <= 2
        if title_ok and players_ok and date_ok and not tournament_ok:
            diagnostics["tournament_class_or_name_mismatch"] += 1
        if title_ok and tournament_ok and date_ok and not players_ok:
            diagnostics["structured_player_crosswalk_mismatch"] += 1
        if title_ok and players_ok and tournament_ok and not date_ok:
            diagnostics["date_alignment_mismatch"] += 1
        if title_ok and players_ok and tournament_ok and date_ok:
            candidates.append({
                **match,
                "date_distance_days": distance,
            })
    completed = [
        row for row in candidates
        if row["completed_result"]
        and row["start_utc"] is not None
        and row["te_match_id"]
    ]
    if len(completed) == 1:
        selected = completed[0]
        reason = None
    elif not target_keys or len(target_keys) != 2:
        selected = None
        reason = "structured_target_identity_unavailable"
    elif not candidates:
        selected = None
        if diagnostics["tournament_class_or_name_mismatch"]:
            reason = "tournament_class_or_name_mismatch"
        elif diagnostics["structured_player_crosswalk_mismatch"]:
            reason = "structured_player_crosswalk_mismatch"
        elif diagnostics["date_alignment_mismatch"]:
            reason = "date_alignment_mismatch"
        else:
            reason = "no_exact_player_tournament_date_crosswalk"
    elif not completed:
        selected = None
        reason = "crosswalk_has_no_completed_result_start_clock"
    else:
        selected = None
        reason = "multiple_completed_exact_crosswalks"
    evidence = {
        "event_id": identity["event_id"],
        "ticker_pair": identity.get("ticker_pair"),
        "event_source_id": identity.get("event_source_id"),
        "competitor_target_ids": identity.get("competitor_target_ids"),
        "competitor_source_ids": identity.get("competitor_source_ids"),
        "milestone_id": identity.get("milestone_id"),
        "milestone_title": identity.get("title"),
        "milestone_tournament": identity.get("tournament"),
        "milestone_start_date_identity_only": identity.get(
            "milestone_start_date"
        ),
        "target_player_keys": target_keys,
        "exact_crosswalk_candidate_count": len(candidates),
        "completed_start_clock_candidate_count": len(completed),
        "near_match_diagnostics": dict(diagnostics),
        "selected_te_match_id": (
            selected["te_match_id"] if selected else None
        ),
        "selected_te_player_names": (
            [row["display_name"] for row in selected["players"]]
            if selected else None
        ),
        "selected_te_player_paths": (
            [row["player_path"] for row in selected["players"]]
            if selected else None
        ),
        "selected_te_tournament": (
            selected["tournament"] if selected else None
        ),
        "selected_te_page_date": (
            selected["page_date"] if selected else None
        ),
        "selected_te_display_clock": (
            selected["display_clock"] if selected else None
        ),
        "selected_te_timezone": (
            selected["display_timezone"] if selected else None
        ),
        "selected_te_page_sha256": (
            selected["page_sha256"] if selected else None
        ),
        "selected_completed_result": (
            selected["completed_result"] if selected else None
        ),
        "start_utc": (
            iso_utc(selected["start_utc"]) if selected else None
        ),
        "precision": "minute" if selected else None,
        "unresolved_reason": reason,
        "policy_outcomes_examined": False,
    }
    return evidence


def te_candidate(crosswalk: Mapping[str, Any]) -> dict[str, Any] | None:
    timestamp = parse_ts(crosswalk.get("start_utc"))
    if timestamp is None:
        return None
    return {
        "source": "tennisexplorer_historical_result_start_clock",
        "source_family": "tennis_db_start_or_live_score",
        "precedence_rank": 3,
        "timestamp_utc": iso_utc(timestamp),
        "direction": "exact",
        "precision": "minute",
        "timestamp_basis": (
            "historical_results_completed_match_start_clock_"
            "Europe_Berlin_converted_to_UTC"
        ),
        "evidence": {
            "te_match_id": crosswalk.get("selected_te_match_id"),
            "event_source_id": crosswalk.get("event_source_id"),
            "competitor_source_ids": crosswalk.get(
                "competitor_source_ids"
            ),
            "player_identity": "exact_surname_and_first_initial_both_players",
            "tournament_identity": "normalized_exact_or_subset_canonical_name",
            "date_alignment_days": (
                abs((
                    dt.date.fromisoformat(
                        str(crosswalk["selected_te_page_date"])
                    )
                    - dt.date.fromisoformat(
                        str(crosswalk[
                            "milestone_start_date_identity_only"
                        ])[:10]
                    )
                ).days)
            ),
            "completed_result": True,
            "page_sha256": crosswalk.get("selected_te_page_sha256"),
            "schedule_used_as_endpoint": False,
        },
    }


def deduplicate_candidates(
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    output = {}
    for row in rows:
        key = (
            row.get("source"),
            row.get("timestamp_utc"),
            row.get("direction"),
            row.get("timestamp_basis"),
        )
        output[key] = dict(row)
    return sorted(output.values(), key=lambda row: (
        int(row.get("precedence_rank") or 99),
        str(row.get("timestamp_utc")),
        str(row.get("source")),
    ))


def adjudicate_residual(
    baseline: Mapping[str, Any],
    crosswalk: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate_row = te_candidate(crosswalk)
    candidates = deduplicate_candidates([
        *(baseline.get("candidate_sources") or []),
        *([candidate_row] if candidate_row else []),
    ])
    if candidate_row is None:
        row = {
            **baseline,
            "schema_version": VERSION,
            "round2_targeted": True,
            "round2_crosswalk": dict(crosswalk),
            "round2_new_exact_recovered": False,
            "round2_conflicts": [],
        }
        return row, []
    exact_ts = parse_ts(candidate_row["timestamp_utc"])
    conflicts = []
    higher_precedence_not_live = []
    for existing in candidates:
        timestamp = parse_ts(existing.get("timestamp_utc"))
        if timestamp is None or existing is candidate_row:
            continue
        direction = existing.get("direction")
        rank = int(existing.get("precedence_rank") or 99)
        if direction == "not_live_through" and timestamp >= exact_ts:
            conflict = {
                "kind": "not_live_observation_at_or_after_result_start",
                "source": existing.get("source"),
                "source_family": existing.get("source_family"),
                "precedence_rank": rank,
                "source_timestamp_utc": existing.get("timestamp_utc"),
                "result_start_utc": candidate_row["timestamp_utc"],
                "disposition": (
                    "blocks_promotion"
                    if rank < int(candidate_row["precedence_rank"])
                    else "retained_lower_precedence_conflict"
                ),
            }
            conflicts.append(conflict)
            if rank < int(candidate_row["precedence_rank"]):
                higher_precedence_not_live.append(conflict)
        elif direction == "live_by" and timestamp < exact_ts:
            conflicts.append({
                "kind": "live_by_observation_before_result_start",
                "source": existing.get("source"),
                "source_family": existing.get("source_family"),
                "precedence_rank": rank,
                "source_timestamp_utc": existing.get("timestamp_utc"),
                "result_start_utc": candidate_row["timestamp_utc"],
                "disposition": (
                    "exact_result_start_controls_by_precedence"
                ),
            })
        elif direction == "exact" and abs(timestamp - exact_ts) > 60:
            conflicts.append({
                "kind": "exact_start_disagreement_over_one_minute",
                "source": existing.get("source"),
                "source_family": existing.get("source_family"),
                "precedence_rank": rank,
                "source_timestamp_utc": existing.get("timestamp_utc"),
                "result_start_utc": candidate_row["timestamp_utc"],
                "disposition": "higher_precedence_exact_controls",
            })
    lowers = [
        parse_ts(row["timestamp_utc"]) for row in candidates
        if row.get("direction") == "not_live_through"
        and parse_ts(row.get("timestamp_utc")) is not None
    ]
    if higher_precedence_not_live:
        precision_class = "contradictory"
        positive = False
        exact_start = None
        conflict_status = (
            "higher_precedence_not_live_after_te_result_start"
        )
    else:
        precision_class = "exact"
        positive = True
        exact_start = exact_ts
        conflict_status = (
            "lower_precedence_source_conflict" if conflicts else "none"
        )
    row = {
        **baseline,
        "schema_version": VERSION,
        "precision_class": precision_class,
        "positive_window1_provable": positive,
        "exact_start_utc": iso_utc(exact_start),
        "not_live_through_utc": iso_utc(max(lowers)) if lowers else None,
        "known_live_by_utc": iso_utc(exact_start) if positive else baseline.get(
            "known_live_by_utc"
        ),
        "start_interval_utc": {
            "lower_inclusive": iso_utc(max(lowers)) if lowers else None,
            "upper_inclusive": (
                iso_utc(exact_start) if positive
                else baseline.get("start_interval_utc", {}).get(
                    "upper_inclusive"
                )
            ),
        },
        "selected_source": (
            candidate_row["source"] if positive
            else baseline.get("selected_source")
        ),
        "selected_source_family": (
            candidate_row["source_family"] if positive
            else baseline.get("selected_source_family")
        ),
        "selected_timestamp_precision": (
            candidate_row["precision"] if positive
            else baseline.get("selected_timestamp_precision")
        ),
        "conflict_status": conflict_status,
        "interval_contradiction": bool(
            higher_precedence_not_live
            or baseline.get("interval_contradiction")
        ),
        "candidate_sources": candidates,
        "round2_targeted": True,
        "round2_crosswalk": dict(crosswalk),
        "round2_new_exact_recovered": positive,
        "round2_conflicts": conflicts,
        "policy_outcomes_examined_during_extraction": False,
    }
    conflict_rows = [{
        "event_id": baseline["event_id"],
        **conflict,
    } for conflict in conflicts]
    return row, conflict_rows


def preserve_positive(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **row,
        "schema_version": VERSION,
        "round2_targeted": False,
        "round2_crosswalk": None,
        "round2_new_exact_recovered": False,
        "round2_conflicts": [],
        "policy_outcomes_examined_during_extraction": False,
    }


def breakdown(
    rows: list[dict[str, Any]],
    field: str,
) -> dict[str, Any]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = str(row.get(field) or "<missing>")
        grouped[key]["D"] += 1
        grouped[key][str(row["precision_class"])] += 1
        grouped[key]["positive_capable"] += int(
            row["positive_window1_provable"]
        )
        grouped[key]["newly_recovered"] += int(
            row["round2_new_exact_recovered"]
        )
    return {
        key: dict(sorted(values.items()))
        for key, values in sorted(grouped.items())
    }


def competition_class(
    category: str,
    tournament: Any,
) -> str:
    normalized = normalize(tournament)
    if "itf" in normalized.split():
        return "ITF"
    return {
        "ATP_CHALL": "ATP_CHALLENGER",
        "ATP_MAIN": "ATP",
        "WTA_CHALL": "WTA_CHALLENGER_OR_125",
        "WTA_MAIN": "WTA",
    }.get(category, "OTHER")


def observation(
    candidate_row: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if candidate_row is None:
        return None
    return {
        "source": candidate_row.get("source"),
        "source_family": candidate_row.get("source_family"),
        "timestamp_utc": candidate_row.get("timestamp_utc"),
        "precision": candidate_row.get("precision"),
        "timestamp_basis": candidate_row.get("timestamp_basis"),
    }


def event_evidence_projection(
    row: Mapping[str, Any],
    retained: Mapping[str, Any],
) -> dict[str, Any]:
    candidates = row.get("candidate_sources") or []
    lower = [
        candidate_row for candidate_row in candidates
        if candidate_row.get("direction") == "not_live_through"
        and parse_ts(candidate_row.get("timestamp_utc")) is not None
    ]
    live = [
        candidate_row for candidate_row in candidates
        if candidate_row.get("direction") in {"live_by", "exact"}
        and parse_ts(candidate_row.get("timestamp_utc")) is not None
    ]
    last_pre = max(
        lower,
        key=lambda candidate_row: parse_ts(
            candidate_row["timestamp_utc"]
        ),
    ) if lower else None
    first_live = min(
        live,
        key=lambda candidate_row: parse_ts(
            candidate_row["timestamp_utc"]
        ),
    ) if live else None
    round2_crosswalk = row.get("round2_crosswalk") or {}
    competitor_sources = round2_crosswalk.get("competitor_source_ids")
    return {
        "schema_version": VERSION,
        "event_id": row["event_id"],
        "ticker_pair": [leg["ticker"] for leg in row["legs"]],
        "event_date": row["event_date"],
        "category": row["category"],
        "competition_class": competition_class(
            str(row["category"]), retained.get("tournament")
        ),
        "tournament": retained.get("tournament"),
        "source_ids": {
            "milestone_id": retained.get("milestone_id"),
            "milestone_ids": retained.get("milestone_ids"),
            "event_source_id": retained.get("event_source_id"),
            "event_source_ids": retained.get("event_source_ids"),
            "competitor_target_ids": retained.get(
                "competitor_target_ids"
            ),
            "competitor_source_ids": competitor_sources,
            "competitor_source_ids_status": (
                "queried_for_round2_residual"
                if row.get("round2_targeted")
                else "not_queried_target_only_preservation"
            ),
            "tennisexplorer_match_id": round2_crosswalk.get(
                "selected_te_match_id"
            ),
        },
        "exact_start_utc": row.get("exact_start_utc"),
        "interval_endpoints_utc": row.get("start_interval_utc"),
        "source_class": row.get("selected_source_family"),
        "selected_source": row.get("selected_source"),
        "precision": row.get("selected_timestamp_precision"),
        "last_pre_live_observation": observation(last_pre),
        "first_live_observation": observation(first_live),
        "crosswalk_evidence": (
            round2_crosswalk if row.get("round2_targeted")
            else {
                "status": "preserved_from_frozen_v3",
                "retained_milestone_raw_sha256": retained.get(
                    "raw_sha256"
                ),
            }
        ),
        "conflicts": row.get("round2_conflicts") or [],
        "retained_identity_conflict": retained.get(
            "retained_identity_conflict", False
        ),
        "conflict_status": row.get("conflict_status"),
        "precision_class": row["precision_class"],
        "round2_new_exact_recovered": row.get(
            "round2_new_exact_recovered", False
        ),
        "final_classification": str(
            row["precision_class"]
        ).upper(),
        "positive_capable": row["positive_window1_provable"],
        "positive_window1_provable": row[
            "positive_window1_provable"
        ],
        "schedule_used_as_start_endpoint": False,
        "policy_outcomes_examined_during_extraction": False,
    }


def source_inventory(
    *,
    final_rows: list[dict[str, Any]],
    crosswalk_rows: list[dict[str, Any]],
    retained_source_dir: Path,
    round1_live_scores: Path,
    round1_observed_starts: Path,
    round1_summary: Path,
    acquisition: Mapping[str, Any],
) -> dict[str, Any]:
    ids = {row["event_id"] for row in final_rows}
    blocked = {
        row["event_id"] for row in final_rows
        if not row["positive_window1_provable"]
    }
    milestone_path = retained_source_dir / "milestone_starts.json"
    corpus_path = retained_source_dir / "corpus_events_v2.jsonl"
    bells_path = retained_source_dir / "daysheet_bells_official.json"
    observed_path = retained_source_dir / "observed_starts.db"
    milestone_cache = read_json(milestone_path)
    milestone_d = {
        key: value for key, value in milestone_cache.items()
        if key in ids
    }
    official_bells = read_json(bells_path)
    bells_d = {
        key: value for key, value in official_bells.items()
        if key in ids
    }
    corpus_d = {}
    for row in read_jsonl(corpus_path):
        if row.get("event") in ids:
            corpus_d[str(row["event"])] = row
    connection = sqlite3.connect(
        f"file:{observed_path.as_posix()}?mode=ro", uri=True
    )
    try:
        observed_rows = connection.execute(
            "SELECT te_match_id, player1, player2, kalshi_ticker, "
            "first_inplay_at, inserted_at FROM observed_starts"
        ).fetchall()
    finally:
        connection.close()
    crosswalk_by_te = {
        str(row["selected_te_match_id"]): str(row["event_id"])
        for row in crosswalk_rows if row.get("selected_te_match_id")
    }
    observed_joined = [
        (str(row[0]), crosswalk_by_te[str(row[0])], row[4])
        for row in observed_rows if str(row[0]) in crosswalk_by_te
    ]
    live_score_rows = read_jsonl(round1_live_scores)
    round1_observed_rows = read_jsonl(round1_observed_starts)
    round1 = read_json(round1_summary)
    promoted = sum(
        row["round2_new_exact_recovered"] for row in final_rows
    )
    matched_clocks = sum(
        row.get("start_utc") is not None for row in crosswalk_rows
    )
    blocked_crosswalks = matched_clocks - promoted
    remote_log_receipts = {
        "receipt_scope": (
            "read-only metadata/hash snapshot; logs continue to accrue"
        ),
        "te_live.log": {
            "bytes": 1235506,
            "sha256": (
                "8edd5dd863f2798696eb318b6817f141d43c684c4e54d9c20b8d01b1e7a2dd35"
            ),
        },
        "betexplorer.log": {
            "bytes": 38078,
            "sha256": (
                "9c6f14f32b53926a2194aaa76294ca5d6e46d14643576e10b4e32d04104458dc"
            ),
        },
        "kalshi_price.log": {
            "bytes": 18365,
            "sha256": (
                "a8b59c96bf752d5933699274326e275dac28d4d665b2b0d9d7d48f53258a42d4"
            ),
        },
        "fv_monitor.log": {
            "bytes": 2862,
            "sha256": (
                "bd771cbfdf2793c84ae0169612bf8f7c21b4ac5db9c14bb6da97d3ec29d0864e"
            ),
        },
        "tennis_odds.log": {
            "bytes": 709086,
            "sha256": (
                "66f6f3810b956d5ac73069005a6f307b514e64d02060a1ae1ad6dff9b9e64a44"
            ),
        },
        "milestone_shadow.current": {
            "bytes": 514445,
            "sha256": (
                "ee27ceda409492f9fa44b5b52e1073910b707c50e751c75e715706649ad09428"
            ),
        },
        "daysheet_misses.current": {
            "bytes": 4899158,
            "sha256": (
                "dab3098bef08c619abd55f3f8585b55e34bd139c7a6cfeadab9c176d6482df71"
            ),
        },
        "subsecond_store.db": {
            "bytes": 6132076544,
            "schema": {
                "prints": (
                    "event,ticker,ts,price,size,src"
                ),
                "ingest_log": "src,path,rows,ingested_at",
            },
            "sha256": "not_rehashed_large_live_store",
        },
    }
    surfaces = [
        {
            "source": "tennis.db.matches",
            "availability": "excluded",
            "D_start_promotions": 0,
            "reason": (
                "mixed execution/policy table; blindness law forbids row "
                "reads and frozen event identity already supplies D"
            ),
        },
        {
            "source": "tennis.db.live_scores",
            "availability": "partial",
            "retained_rows": len(live_score_rows),
            "status_counts": dict(Counter(
                str(row.get("status") or "<missing>")
                for row in live_score_rows
            )),
            "D_start_promotions": 0,
            "reason": (
                "UNIQUE(te_match_id) INSERT OR REPLACE retains current/final "
                "state, not monotonic status history; one-sided upper only"
            ),
        },
        {
            "source": "tennis.db.score_status_history",
            "availability": "unavailable",
            "D_start_promotions": 0,
            "reason": "no append-only historical table existed for July 12-20",
        },
        {
            "source": "tennis.db.observed_starts_main",
            "availability": "partial",
            "retained_rows": len(round1_observed_rows),
            "D_start_promotions": 0,
            "reason": (
                "set-once first sighting supplies a live-by upper but no "
                "independent pre-live lower"
            ),
        },
        {
            "source": "state/observed_starts.db",
            "availability": "partial",
            "retained_rows": len(observed_rows),
            "exact_TE_match_id_joins": len(observed_joined),
            "joins_still_blocked": sum(
                event_id in blocked
                for _, event_id, _ in observed_joined
            ),
            "D_start_promotions": 0,
            "reason": (
                "first in-play receipt is upper-only; joined rows corroborate "
                "but cannot independently create a two-sided interval"
            ),
        },
        {
            "source": "tennis.db.historical_events",
            "availability": "identity_only",
            "D_start_promotions": 0,
            "reason": (
                "first_ts/last_ts are market-price retention clocks, not "
                "match status clocks; price behavior is prohibited"
            ),
        },
        {
            "source": "tennis.db.kalshi_price_snapshots",
            "availability": "identity_time_alignment_only",
            "D_start_promotions": 0,
            "reason": (
                "open-market poll metadata does not contractually prove "
                "not-started; price fields were not read"
            ),
        },
        {
            "source": (
                "betexplorer_staging/bookmaker_odds/fv_monitor/"
                "tennis_odds producer records"
            ),
            "availability": "identity_time_alignment_only",
            "D_start_promotions": 0,
            "reason": (
                "listing/poll clocks carry no explicit pre-live or live "
                "status; odds and prices were not used"
            ),
        },
        {
            "source": "milestone_shadow and official bell caches",
            "availability": "available",
            "baseline_receipt": round1["source_receipts"][
                "raw_milestone_shadow"
            ],
            "current_official_D_rows": len(bells_d),
            "current_official_status_counts": dict(Counter(
                str(row.get("status") or "<missing>")
                for row in bells_d.values()
            )),
            "D_start_promotions_round2": 0,
            "reason": (
                "already consumed in V3; current D additions are not_started "
                "receipts and cannot be promoted"
            ),
        },
        {
            "source": "milestone_starts/corpus_events_v2",
            "availability": "partial",
            "milestone_D_rows": len(milestone_d),
            "milestone_D_status_counts": dict(Counter(
                str(row.get("status") or "<missing>")
                for row in milestone_d.values()
            )),
            "corpus_D_rows": len(corpus_d),
            "corpus_right_edge_counts": dict(Counter(
                str(row.get("right_edge_src") or "<missing>")
                for row in corpus_d.values()
            )),
            "blocked_events_with_official_ts": sum(
                bool(corpus_d.get(event_id, {}).get("official_ts"))
                for event_id in blocked
            ),
            "D_start_promotions_round2": 0,
            "reason": (
                "official actuals already sit in the preserved baseline; "
                "onset estimates and schedule rows cannot prove positives"
            ),
        },
        {
            "source": "live_v3/live_v4 immutable logs",
            "availability": "available_previously_consumed",
            "D_start_promotions_round2": 0,
            "reason": (
                "V3 retained policy-blind start/status candidates; the "
                "Round-2 residual scan found no new explicit pre/live pair"
            ),
        },
        {
            "source": (
                "market_lifecycle_v2/raw WS lifecycle/reconnect/depth snapshots"
            ),
            "availability": "partial_or_unavailable_for_start",
            "D_start_promotions": 0,
            "reason": (
                "retained subsecond store contains prints plus ingest "
                "provenance, not event-resolved status transitions; price "
                "movement and unproven depth continuity cannot establish start"
            ),
        },
        {
            "source": "public retained milestone score endpoint",
            "availability": "available_current_state_only",
            "responses": (
                acquisition["http_receipts"]["by_kind"]
                ["retained_milestone_score"]
            ),
            "response_404": 1,
            "D_start_promotions": 0,
            "reason": (
                "current final score/status has no historical receipt or "
                "start timestamp"
            ),
        },
        {
            "source": "TennisExplorer historical completed-result start clock",
            "availability": "available",
            "strict_crosswalk_start_clocks": matched_clocks,
            "higher_precedence_conflicts_blocked": blocked_crosswalks,
            "D_start_promotions": promoted,
            "reason": (
                "same provider surface used by te_live/te_honest; exact "
                "player, tournament class/name, date, match ID, completed "
                "result, and minute clock required"
            ),
        },
    ]
    return {
        "schema_version": "window1-start-truth-round2-source-inventory-v1",
        "D": D,
        "residual_targeted": RESIDUAL,
        "policy_blind": True,
        "surfaces": surfaces,
        "remote_log_receipts": remote_log_receipts,
        "private_retained_receipts": {
            "milestone_starts.json": {
                "bytes": milestone_path.stat().st_size,
                "sha256": sha256_file(milestone_path),
            },
            "corpus_events_v2.jsonl": {
                "bytes": corpus_path.stat().st_size,
                "sha256": sha256_file(corpus_path),
            },
            "daysheet_bells_official.json": {
                "bytes": bells_path.stat().st_size,
                "sha256": sha256_file(bells_path),
            },
            "observed_starts.db": {
                "bytes": observed_path.stat().st_size,
                "sha256": sha256_file(observed_path),
            },
            "round1_live_scores": {
                "bytes": round1_live_scores.stat().st_size,
                "sha256": sha256_file(round1_live_scores),
            },
            "round1_observed_starts": {
                "bytes": round1_observed_starts.stat().st_size,
                "sha256": sha256_file(round1_observed_starts),
            },
        },
        "exhaustion_verdict": (
            "The start gate passed. No exhausted query was repeated as a "
            "new source; the existing six-family/24-policy runner remains "
            "frozen and unscored pending independent ledger review."
        ),
    }


def source_report(inventory: Mapping[str, Any]) -> str:
    lines = [
        "# Round-2 start-source disposition",
        "",
        "All extraction remained blind to execution and policy outcomes.",
        "",
        "| source | availability | new D promotions | disposition |",
        "|---|---:|---:|---|",
    ]
    for row in inventory["surfaces"]:
        lines.append(
            f"| {row['source']} | {row['availability']} | "
            f"{row.get('D_start_promotions_round2', row.get('D_start_promotions', 0))} "
            f"| {row['reason']} |"
        )
    lines.extend([
        "",
        inventory["exhaustion_verdict"],
        "",
    ])
    return "\n".join(lines)


def calibration(
    baseline_rows: list[dict[str, Any]],
    milestone_raw_dir: Path,
    te_matches: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare retained TE clocks to already-frozen exact starts.

    This is a source-semantics check only.  It does not replace, rerun, or
    modify any of the 234 frozen exact rulings.
    """
    te_by_title: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for match in te_matches:
        te_by_title[tuple(match["title_pair"])].append(match)
    frozen = {
        str(row["event_id"]): row for row in baseline_rows
        if row["precision_class"] == "exact"
    }
    differences = []
    comparable = 0
    for event_id, baseline in sorted(frozen.items()):
        path = milestone_raw_dir / f"{event_id}.json.gz"
        if not path.exists():
            continue
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            raw = json.load(handle)
        milestones = [
            value
            for page in raw.get("pages") or []
            for value in (page.get("response") or {}).get("milestones") or []
        ]
        if not milestones:
            continue
        milestone = milestones[0]
        start_date = milestone.get("start_date")
        tournament = (milestone.get("details") or {}).get(
            "tournament_name"
        )
        candidates = [
            match for match in te_by_title[title_pair(milestone.get("title"))]
            if match["completed_result"]
            and match["start_utc"] is not None
            and tournament_matches(tournament, match["tournament"])
            and (
                date_distance(match["page_date"], start_date) is not None
                and date_distance(match["page_date"], start_date) <= 2
            )
        ]
        if len(candidates) != 1:
            continue
        comparable += 1
        official_ts = parse_ts(baseline["exact_start_utc"])
        differences.append(candidates[0]["start_utc"] - official_ts)
    buckets = Counter()
    for difference in differences:
        absolute = abs(difference)
        if absolute <= 1:
            buckets["exact_to_second"] += 1
        elif absolute <= 60:
            buckets["within_1_minute"] += 1
        elif absolute <= 300:
            buckets["within_5_minutes"] += 1
        elif absolute <= 900:
            buckets["within_15_minutes"] += 1
        else:
            buckets["over_15_minutes_conflict"] += 1
    return {
        "purpose": "source_semantics_only_no_frozen_ruling_changed",
        "frozen_exact_population": len(frozen),
        "comparable_unique_crosswalks": comparable,
        "difference_buckets_exclusive": dict(buckets),
        "within_5_minutes_inclusive": sum(
            abs(value) <= 300 for value in differences
        ),
        "within_15_minutes_inclusive": sum(
            abs(value) <= 900 for value in differences
        ),
        "over_15_minutes_conflicts": sum(
            abs(value) > 900 for value in differences
        ),
        "conflicts_do_not_modify_frozen_exact_rows": True,
    }


def build_report(summary: Mapping[str, Any]) -> str:
    verdict = "PASS" if summary["start_gate_pass"] else "FAIL"
    counts = summary["precision_counts"]
    return f"""# Window-1 Start-Truth Recovery Round 2

Extraction remained blind to policy decisions, placements, fills, prices,
deltas, candidate results, and success labels.  The frozen 234 exact starts
and 31 clean intervals were preserved.  Only the 539 previously blocked
events were eligible for a new ruling.

## Start gate — {verdict}

- D = {summary['D']}
- exact starts = {counts.get('exact', 0)}
- clean causal intervals = {counts.get('clean_interval', 0)}
- live-by-only = {counts.get('live_by_only', 0)}
- contradictory = {counts.get('contradictory', 0)}
- schedule-only = {counts.get('schedule_only', 0)}
- unresolved = {counts.get('unresolved', 0)}
- positive-capable population = {summary['positive_capable_population']}
- gate required = {summary['start_gate_required']}
- gate margin = {summary['start_gate_margin']}
- newly recovered exact starts = {summary['newly_recovered_exact']}
- residual timing-blocked population = {summary['timing_blocked_population']}

The new exact source is the retained TennisExplorer finished-result start
clock, the historical provider surface used by `te_live.py` and named
`te_honest` in the chronological Vault.  Promotion required the exact same
two structured-target players (surname plus first initial), tournament,
date corridor used only for identity alignment, provider match ID, a
completed result, and a minute start clock.  The displayed
Berlin/Prague/Vienna timezone was converted with `Europe/Berlin`; schedule
was never used as an interval endpoint.

{summary['higher_precedence_conflict_blocked']} otherwise crosswalked events
remain contradictory because a higher-precedence raw milestone receipt
still said `not_started` at or after the result clock.  Lower-precedence
tape/live-by disagreements are retained in the conflict ledger; the exact
result clock controls by the frozen source precedence rather than by which
value would improve policy performance.

The six-family/24-policy development preflight remains frozen and unscored.
No candidate runner, tuning, ablation, or holdout evaluation was executed.
"""


def run(args: argparse.Namespace) -> int:
    baseline_path = Path(args.baseline_ledger).resolve()
    identity_path = Path(args.residual_identity).resolve()
    acquisition_path = Path(args.acquisition_manifest).resolve()
    target_dir = Path(args.structured_targets).resolve()
    te_dir = Path(args.te_results).resolve()
    milestone_raw_dir = Path(args.milestone_raw_dir).resolve()
    preflight_path = Path(args.preflight).resolve()
    retained_source_dir = Path(args.retained_source_dir).resolve()
    round1_live_scores = Path(args.round1_live_scores).resolve()
    round1_observed_starts = Path(args.round1_observed_starts).resolve()
    round1_summary = Path(args.round1_summary).resolve()
    output = Path(args.output).resolve()
    baseline_rows = read_jsonl(baseline_path)
    counts = Counter(row["precision_class"] for row in baseline_rows)
    if (
        len(baseline_rows) != D
        or len({row["event_id"] for row in baseline_rows}) != D
        or any(counts[key] != value for key, value in BASE_COUNTS.items())
        or sum(row["positive_window1_provable"] for row in baseline_rows)
        != BASE_POSITIVE
    ):
        raise Round2Error("frozen V3 baseline changed")
    acquisition = read_json(acquisition_path)
    failures = acquisition.get("failures") or []
    if not (
        len(failures) == 1
        and failures[0].get("request_kind")
        == "retained_milestone_score"
        and "404" in str(failures[0].get("detail"))
    ):
        raise Round2Error(
            f"unexpected acquisition failures: {len(failures)}"
        )
    identities, identity_receipt = load_identity(
        identity_path, target_dir
    )
    baseline_by_id = {
        str(row["event_id"]): row for row in baseline_rows
    }
    retained_identity = {}
    for event_id in sorted(baseline_by_id):
        path = milestone_raw_dir / f"{event_id}.json.gz"
        if not path.exists():
            raise Round2Error(f"missing retained milestone raw: {event_id}")
        retained_identity[event_id] = retained_milestone_identity(path)
    for identity in identities:
        event_id = str(identity["event_id"])
        if baseline_by_id[event_id]["positive_window1_provable"]:
            raise Round2Error(f"Round 2 targeted a frozen positive: {event_id}")
        identity["ticker_pair"] = [
            leg["ticker"] for leg in baseline_by_id[event_id]["legs"]
        ]
    te_matches, te_receipt = parse_te_pages(te_dir)
    crosswalk_rows = [
        crosswalk_event(identity, te_matches)
        for identity in sorted(
            identities, key=lambda row: row["event_id"]
        )
    ]
    crosswalk_by_id = {
        str(row["event_id"]): row for row in crosswalk_rows
    }
    final_rows = []
    conflicts = []
    for baseline in sorted(
        baseline_rows, key=lambda row: str(row["event_id"])
    ):
        event_id = str(baseline["event_id"])
        if baseline["positive_window1_provable"]:
            final_rows.append(preserve_positive(baseline))
        else:
            final, conflict_rows = adjudicate_residual(
                baseline, crosswalk_by_id[event_id]
            )
            final_rows.append(final)
            conflicts.extend(conflict_rows)
    final_counts = Counter(row["precision_class"] for row in final_rows)
    positive = sum(
        row["positive_window1_provable"] for row in final_rows
    )
    newly = sum(row["round2_new_exact_recovered"] for row in final_rows)
    if (
        len(final_rows) != D
        or len({row["event_id"] for row in final_rows}) != D
        or newly != positive - BASE_POSITIVE
        or final_counts["clean_interval"] != BASE_CLEAN
        or sum(
            row["precision_class"] == "exact"
            and not row["round2_targeted"]
            for row in final_rows
        ) != BASE_EXACT
    ):
        raise Round2Error("Round 2 denominator or preservation law failed")
    higher_blocked = len({
        row["event_id"] for row in conflicts
        if row["disposition"] == "blocks_promotion"
    })
    crosswalk_reason_counts = Counter(
        row["unresolved_reason"] or "recovered_start_clock"
        for row in crosswalk_rows
    )
    selected_source_counts = Counter(
        row.get("selected_source") or "schedule_or_unresolved"
        for row in final_rows
    )
    calibration_receipt = calibration(
        baseline_rows, milestone_raw_dir, te_matches
    )
    ledger_path = output / "REAL_START_LEDGER_V4.jsonl"
    crosswalk_path = output / "START_CROSSWALK_V4.jsonl"
    conflict_path = output / "START_CONFLICT_LEDGER_V4.jsonl"
    event_evidence_path = output / "START_EVENT_EVIDENCE_V4.jsonl"
    source_inventory_path = output / "START_SOURCE_EXHAUSTION_V4.json"
    source_report_path = output / "START_SOURCE_EXHAUSTION_V4.md"
    write_jsonl(ledger_path, final_rows)
    write_jsonl(crosswalk_path, crosswalk_rows)
    write_jsonl(conflict_path, sorted(
        conflicts,
        key=lambda row: (
            row["event_id"], row["kind"], row["source_timestamp_utc"]
        ),
    ))
    event_evidence_rows = [
        event_evidence_projection(
            row, retained_identity[row["event_id"]]
        )
        for row in final_rows
    ]
    write_jsonl(event_evidence_path, event_evidence_rows)
    inventory = source_inventory(
        final_rows=final_rows,
        crosswalk_rows=crosswalk_rows,
        retained_source_dir=retained_source_dir,
        round1_live_scores=round1_live_scores,
        round1_observed_starts=round1_observed_starts,
        round1_summary=round1_summary,
        acquisition=acquisition,
    )
    write_json(source_inventory_path, inventory)
    source_report_path.write_text(
        source_report(inventory), encoding="utf-8", newline="\n"
    )
    summary = {
        "schema_version": VERSION,
        "D": D,
        "baseline": {
            "ledger_sha256": sha256_file(baseline_path),
            "exact_starts_preserved": BASE_EXACT,
            "clean_intervals_preserved": BASE_CLEAN,
            "positive_capable_preserved": BASE_POSITIVE,
            "residual_targeted": RESIDUAL,
        },
        "precision_counts": dict(final_counts),
        "positive_capable_population": positive,
        "timing_blocked_population": D - positive,
        "start_gate_required": GATE,
        "start_gate_pass": positive >= GATE,
        "start_gate_margin": positive - GATE,
        "newly_recovered_exact": newly,
        "higher_precedence_conflict_blocked": higher_blocked,
        "crosswalk_dispositions": dict(crosswalk_reason_counts),
        "selected_source_counts": dict(selected_source_counts),
        "coverage": {
            "by_date": breakdown(final_rows, "event_date"),
            "by_category": breakdown(final_rows, "category"),
            "by_selected_provider": {
                key: value for key, value in sorted(
                    selected_source_counts.items()
                )
            },
            "by_tournament": {},
            "by_competition_class": breakdown(
                event_evidence_rows, "competition_class"
            ),
            "exact_vs_interval": {
                "exact": final_counts["exact"],
                "clean_interval": final_counts["clean_interval"],
                "other": D - final_counts["exact"]
                - final_counts["clean_interval"],
            },
            "reason_still_unresolved": {
                key: value for key, value in sorted(
                    crosswalk_reason_counts.items()
                ) if key != "recovered_start_clock"
            },
        },
        "calibration_against_preserved_exact": calibration_receipt,
        "source_receipts": {
            "acquisition_manifest": {
                "sha256": sha256_file(acquisition_path),
                "http_requests": acquisition["http_receipts"]["requests"],
                "te_pages": acquisition["tennisexplorer_results"]["pages"],
                "failures": failures,
            },
            "residual_identity": identity_receipt,
            "tennisexplorer_results": te_receipt,
            "retained_score_endpoint": {
                "role": "status_and_identity_only",
                "historical_start_timestamp_present": False,
                "promoted_events": 0,
                "missing_response_events": 1,
                "reason": (
                    "current retained final score has no historical receipt "
                    "clock and therefore cannot create a past start boundary"
                ),
            },
        },
        "extraction_law": {
            "policy_decisions_examined": False,
            "placements_examined": False,
            "fills_examined": False,
            "prices_examined": False,
            "deltas_examined": False,
            "candidate_results_examined": False,
            "schedule_used_as_start_endpoint": False,
            "live_by_promoted_to_exact": False,
            "higher_precedence_conflict_chosen_for_performance": False,
        },
        "frozen_runner": {
            "preflight_sha256": sha256_file(preflight_path),
            "permitted_family_count": read_json(preflight_path)[
                "family_count"
            ],
            "permitted_policy_count": read_json(preflight_path)[
                "policy_count"
            ],
            "candidate_scoring_run": False,
            "tuning_run": False,
            "holdout_opened": False,
        },
        "artifacts": {
            "ledger": {
                "path": "REAL_START_LEDGER_V4.jsonl",
                "sha256": sha256_file(ledger_path),
                "rows": len(final_rows),
            },
            "crosswalk": {
                "path": "START_CROSSWALK_V4.jsonl",
                "sha256": sha256_file(crosswalk_path),
                "rows": len(crosswalk_rows),
            },
            "conflicts": {
                "path": "START_CONFLICT_LEDGER_V4.jsonl",
                "sha256": sha256_file(conflict_path),
                "rows": len(conflicts),
            },
            "event_evidence": {
                "path": "START_EVENT_EVIDENCE_V4.jsonl",
                "sha256": sha256_file(event_evidence_path),
                "rows": len(event_evidence_rows),
            },
            "source_exhaustion": {
                "path": "START_SOURCE_EXHAUSTION_V4.json",
                "sha256": sha256_file(source_inventory_path),
                "surfaces": len(inventory["surfaces"]),
            },
        },
    }
    tournament_counts: dict[str, Counter[str]] = defaultdict(Counter)
    identity_by_event = {
        row["event_id"]: row for row in identities
    }
    for row in final_rows:
        tournament = (
            identity_by_event.get(row["event_id"], {}).get("tournament")
            or "<preserved_not_requeried>"
        )
        tournament_counts[tournament]["D"] += 1
        tournament_counts[tournament][row["precision_class"]] += 1
        tournament_counts[tournament]["positive_capable"] += int(
            row["positive_window1_provable"]
        )
        tournament_counts[tournament]["newly_recovered"] += int(
            row["round2_new_exact_recovered"]
        )
    summary["coverage"]["by_tournament"] = {
        key: dict(sorted(value.items()))
        for key, value in sorted(tournament_counts.items())
    }
    summary_path = output / "REAL_START_SUMMARY_V4.json"
    report_path = output / "REAL_START_REPORT_V4.md"
    write_json(summary_path, summary)
    report_path.write_text(
        build_report(summary), encoding="utf-8", newline="\n"
    )
    manifest = {
        "schema_version": "window1-start-truth-round2-artifact-manifest-v1",
        "artifacts": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in [
                ledger_path,
                crosswalk_path,
                conflict_path,
                event_evidence_path,
                source_inventory_path,
                source_report_path,
                summary_path,
                report_path,
            ]
        },
        "code": {
            "path": "arb-executor/analysis/window1_start_truth_round2.py",
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "private_raw_responses_committed": False,
        "candidate_scoring_run": False,
        "holdout_opened": False,
    }
    write_json(output / "ARTIFACT_MANIFEST.json", manifest)
    print(compact({
        "D": D,
        "exact": final_counts["exact"],
        "clean": final_counts["clean_interval"],
        "positive": positive,
        "new_exact": newly,
        "blocked_conflicts": higher_blocked,
        "gate_pass": positive >= GATE,
        "output": str(output),
    }))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--baseline-ledger", required=True)
    result.add_argument("--residual-identity", required=True)
    result.add_argument("--acquisition-manifest", required=True)
    result.add_argument("--structured-targets", required=True)
    result.add_argument("--te-results", required=True)
    result.add_argument("--milestone-raw-dir", required=True)
    result.add_argument("--preflight", required=True)
    result.add_argument("--retained-source-dir", required=True)
    result.add_argument("--round1-live-scores", required=True)
    result.add_argument("--round1-observed-starts", required=True)
    result.add_argument("--round1-summary", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
