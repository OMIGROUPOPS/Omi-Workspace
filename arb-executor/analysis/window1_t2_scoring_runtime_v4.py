#!/usr/bin/env python3
"""Shared V4 real-input preparation and crash-honest scorer accounting.

Both no-score preflight and future execute mode consume
``iter_prepared_scorer_calls``.  The exact ``score_kwargs`` mapping yielded by
that function carries the full raw V5 boundary row.  The normalized boundary
is retained only as a separately named cross-check and can never be selected
as the inherited scorer boundary.
"""

from __future__ import annotations

import gzip
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping

from window1_range_attack_prerun_builder import boundary_contract
from window1_range_attack_reference_adapter_v1 import guarded_cutoff
from window1_range_attack_scoring_runner_v1 import (
    _event_legs,
    read_json,
    read_jsonl,
    resolve_role,
)
from window1_t2_reference_boundary_v3 import (
    RAW_V5_SHA256,
    adapt_frozen_reference_rows,
    canonical_sha256,
)
from window1_t2_scoring_adapter_v1 import adapt_t2_unique_fill_rows


VERSION = "window1-t2-scoring-runtime-v4"
D_REQUIRED = 804
EXPECTED_LEGS = 1608
EXPECTED_CALLS = 6432
EXPECTED_CHAINS = 12864
EXPECTED_AUTHORITY_D2 = 4170


class RuntimePreparationError(RuntimeError):
    """A prepared V4 scorer argument left the frozen contract."""


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _same(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is bool and type(right) is bool and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return (
            math.isfinite(float(left))
            and math.isfinite(float(right))
            and abs(float(left) - float(right)) <= 1e-6
        )
    return left == right


def _expected_cutoff_from_normalized(
    normalized: Mapping[str, Any],
) -> dict[str, Any]:
    status = (
        "positive"
        if normalized.get("positive_window1_provable") is True
        else (
            "contradictory"
            if normalized.get("start_source_class") == "contradictory"
            else "censored"
        )
    )
    return {
        "event_id": normalized.get("event_id"),
        "status": status,
        "source_class": normalized.get("start_source_class"),
        "cutoff_ts": normalized.get("guarded_cutoff_ts"),
        "guard_id": (
            normalized.get("guard_id") if status == "positive" else None
        ),
        "guard_seconds": (
            normalized.get("guard_seconds") if status == "positive" else None
        ),
    }


def validate_boundary_pair(
    raw: Mapping[str, Any],
    normalized: Mapping[str, Any],
) -> dict[str, Any]:
    """Prove raw V5 and its lossy cutoff contract agree field by field."""
    event_id = str(raw.get("event_id") or "")
    if not event_id or str(normalized.get("event_id") or "") != event_id:
        raise RuntimePreparationError("raw/normalized event identity mismatch")
    independently_normalized = boundary_contract(raw)
    if independently_normalized != dict(normalized):
        changed = [
            key for key in sorted(
                set(independently_normalized) | set(normalized)
            )
            if not _same(
                independently_normalized.get(key), normalized.get(key)
            )
        ]
        raise RuntimePreparationError(
            f"boundary contract mismatch {event_id}: {','.join(changed)}"
        )
    cutoff = guarded_cutoff(raw)
    expected = _expected_cutoff_from_normalized(normalized)
    actual = {
        "event_id": cutoff.get("event_id"),
        "status": cutoff.get("status"),
        "source_class": cutoff.get("source_class"),
        "cutoff_ts": cutoff.get("cutoff_ts"),
        "guard_id": cutoff.get("guard_id"),
        "guard_seconds": cutoff.get("guard_seconds"),
    }
    changed = [
        key for key in expected
        if not _same(expected.get(key), actual.get(key))
    ]
    if changed:
        raise RuntimePreparationError(
            f"guarded cutoff mismatch {event_id}: {','.join(changed)}"
        )
    return cutoff


@dataclass(frozen=True)
class PreparedScorerCall:
    candidate_id: str
    parent_candidate_id: str
    candidate_ordinal: int
    event_ordinal: int
    event_id: str
    event_date: str
    event: Mapping[str, Any]
    raw_v5_boundary: Mapping[str, Any]
    normalized_boundary_contract: Mapping[str, Any]
    cutoff: Mapping[str, Any]
    fills_by_leg: Mapping[str, Any]
    references_by_leg: Mapping[str, Any]
    floors_by_leg: Mapping[str, Mapping[str, Any]]
    regret_chains_by_leg: Mapping[str, Mapping[str, Any]]
    authority_d2_by_leg: Mapping[str, Mapping[str, Any]]

    @property
    def score_kwargs(self) -> dict[str, Any]:
        """The exact mapping passed to ``score_t2_event`` in execute mode."""
        return {
            "candidate_id": self.candidate_id,
            "parent_candidate_id": self.parent_candidate_id,
            "event": self.event,
            "boundary": self.raw_v5_boundary,
            "fills_by_leg": self.fills_by_leg,
            "references_by_leg": self.references_by_leg,
        }

    def seam_receipt(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "event_id": self.event_id,
            "candidate_ordinal": self.candidate_ordinal,
            "event_ordinal": self.event_ordinal,
            "scorer_boundary_role": "full_raw_V5_boundary",
            "raw_boundary_schema": self.raw_v5_boundary.get("schema_version"),
            "raw_boundary_source_sha256": canonical_sha256(
                self.raw_v5_boundary
            ),
            "normalized_boundary_source_sha256": (
                self.normalized_boundary_contract.get(
                    "source_record_sha256"
                )
            ),
            "raw_and_normalized_are_distinct_objects": (
                self.raw_v5_boundary is not self.normalized_boundary_contract
            ),
            "guarded_cutoff_status": self.cutoff["status"],
            "guarded_cutoff_ts": self.cutoff.get("cutoff_ts"),
            "fill_leg_count": len(self.fills_by_leg),
            "reference_leg_count": len(self.references_by_leg),
            "floor_leg_count": len(self.floors_by_leg),
            "regret_chain_leg_count": len(self.regret_chains_by_leg),
        }


def _load_runtime_inputs(
    repo: Path,
    roles: Mapping[str, str],
    candidate_ids: tuple[str, ...],
) -> dict[str, Any]:
    events = read_jsonl(resolve_role(repo, roles["event_ledger"]))
    if len(events) != D_REQUIRED:
        raise RuntimePreparationError("D changed from 804")
    expected_legs = _event_legs(events)
    if len(expected_legs) != EXPECTED_LEGS:
        raise RuntimePreparationError("event-leg population changed")
    raw_rows = read_jsonl(resolve_role(repo, roles["raw_v5_boundary_ledger"]))
    normalized_rows = read_jsonl(
        resolve_role(repo, roles["normalized_boundary_ledger"])
    )
    raw = {str(row["event_id"]): row for row in raw_rows}
    normalized = {
        str(row["event_id"]): row for row in normalized_rows
    }
    event_ids = {str(event["event_id"]) for event in events}
    if (
        len(raw) != D_REQUIRED
        or len(normalized) != D_REQUIRED
        or set(raw) != event_ids
        or set(normalized) != event_ids
    ):
        raise RuntimePreparationError("boundary event sets do not conserve")
    cutoffs = {
        event_id: validate_boundary_pair(raw[event_id], normalized[event_id])
        for event_id in sorted(event_ids)
    }

    reference_rows = list(iter_gzip(resolve_role(
        repo, roles["frozen_reference_ledger"]
    )))
    for row in reference_rows:
        event_id = str(row["event_id"])
        if (
            row.get("raw_v5_boundary_ledger_sha256") != RAW_V5_SHA256
            or row.get("raw_v5_boundary_source_sha256")
            != canonical_sha256(raw[event_id])
        ):
            raise RuntimePreparationError(
                "frozen reference/raw V5 binding changed"
            )
    references = adapt_frozen_reference_rows(
        reference_rows,
        expected_legs=expected_legs,
        normalized_boundaries=normalized,
    )
    fills = adapt_t2_unique_fill_rows(
        iter_gzip(resolve_role(repo, roles["unique_T2_fill_ledger"])),
        expected_candidates=frozenset(candidate_ids),
        expected_legs=expected_legs,
    )
    floors = {
        (str(row["event_id"]), str(row["leg_id"])): row
        for row in iter_gzip(resolve_role(
            repo, roles["oracle_leg_floor_ledger"]
        ))
    }
    chains = {
        (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        ): row
        for row in iter_gzip(resolve_role(
            repo, roles["regret_chain_input_ledger"]
        ))
    }
    authority = {
        (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        ): row
        for row in iter_gzip(resolve_role(
            repo, roles["target_authority_d2_provenance_ledger"]
        ))
    }
    expected_candidate_legs = {
        (candidate, event_id, leg_id)
        for candidate in candidate_ids
        for event_id, leg_id in expected_legs
    }
    if (
        len(references) != EXPECTED_LEGS
        or set(references) != set(expected_legs)
        or len(floors) != EXPECTED_LEGS
        or set(floors) != set(expected_legs)
        or len(chains) != EXPECTED_CHAINS
        or set(chains) != expected_candidate_legs
        or len(authority) != EXPECTED_AUTHORITY_D2
        or not set(authority).issubset(expected_candidate_legs)
    ):
        raise RuntimePreparationError("runtime joins do not conserve")
    fit_post = read_json(resolve_role(repo, roles["fit_postfit_ledger"]))
    if (
        len(fit_post.get("rows") or []) != 804
        or sum(
            row["slice"] == "fit" for row in fit_post["rows"]
        ) != 525
        or sum(
            row["slice"] == "post_fit" for row in fit_post["rows"]
        ) != 279
    ):
        raise RuntimePreparationError("fit/post-fit membership changed")
    return {
        "events": events,
        "expected_legs": expected_legs,
        "raw": raw,
        "normalized": normalized,
        "cutoffs": cutoffs,
        "references": references,
        "fills": fills,
        "floors": floors,
        "chains": chains,
        "authority": authority,
    }


def iter_prepared_scorer_calls(
    *,
    repo: Path,
    roles: Mapping[str, str],
    candidate_ids: tuple[str, ...],
    candidate_to_parent: Mapping[str, str],
) -> Iterator[PreparedScorerCall]:
    """Yield the exact 6,432 future scorer argument objects."""
    state = _load_runtime_inputs(repo, roles, candidate_ids)
    for candidate_ordinal, candidate in enumerate(candidate_ids, 1):
        parent = candidate_to_parent.get(candidate)
        if not parent:
            raise RuntimePreparationError("candidate lacks parent identity")
        for event_ordinal, event in enumerate(state["events"], 1):
            event_id = str(event["event_id"])
            leg_ids = [
                str(leg.get("leg_id") or leg.get("leg"))
                for leg in event["legs"]
            ]
            fills = {
                leg_id: state["fills"][(candidate, event_id, leg_id)]
                for leg_id in leg_ids
                if (candidate, event_id, leg_id) in state["fills"]
            }
            references = {
                leg_id: state["references"][(event_id, leg_id)]
                for leg_id in leg_ids
            }
            floors = {
                leg_id: state["floors"][(event_id, leg_id)]
                for leg_id in leg_ids
            }
            chains = {
                leg_id: state["chains"][(candidate, event_id, leg_id)]
                for leg_id in leg_ids
            }
            authority = {
                leg_id: state["authority"][(candidate, event_id, leg_id)]
                for leg_id in leg_ids
                if (candidate, event_id, leg_id) in state["authority"]
            }
            yield PreparedScorerCall(
                candidate_id=candidate,
                parent_candidate_id=parent,
                candidate_ordinal=candidate_ordinal,
                event_ordinal=event_ordinal,
                event_id=event_id,
                event_date=str(event["event_date"]),
                event=event,
                raw_v5_boundary=state["raw"][event_id],
                normalized_boundary_contract=state["normalized"][event_id],
                cutoff=state["cutoffs"][event_id],
                fills_by_leg=fills,
                references_by_leg=references,
                floors_by_leg=floors,
                regret_chains_by_leg=chains,
                authority_d2_by_leg=authority,
            )


def no_score_seam_probe(
    *,
    repo: Path,
    roles: Mapping[str, str],
    candidate_ids: tuple[str, ...],
    candidate_to_parent: Mapping[str, str],
    results_directory: str,
) -> dict[str, Any]:
    """Iterate every exact scorer input without importing/invoking a scorer."""
    calls = 0
    first_receipts = []
    statuses: dict[str, int] = {}
    fill_rows = 0
    reference_legs = 0
    floor_legs = 0
    chain_legs = 0
    authority_legs = 0
    for prepared in iter_prepared_scorer_calls(
        repo=repo,
        roles=roles,
        candidate_ids=candidate_ids,
        candidate_to_parent=candidate_to_parent,
    ):
        calls += 1
        kwargs = prepared.score_kwargs
        if kwargs["boundary"] is not prepared.raw_v5_boundary:
            raise RuntimePreparationError(
                "prepared scorer boundary is not raw V5"
            )
        if kwargs["boundary"] is prepared.normalized_boundary_contract:
            raise RuntimePreparationError(
                "normalized boundary selected for scorer"
            )
        cutoff = guarded_cutoff(kwargs["boundary"])
        if cutoff != dict(prepared.cutoff):
            raise RuntimePreparationError("prepared cutoff changed")
        if (
            cutoff["status"] == "positive"
            and not isinstance(kwargs["boundary"].get("guard_band"), Mapping)
        ):
            raise RuntimePreparationError(
                "positive prepared boundary lacks guard band"
            )
        statuses[cutoff["status"]] = statuses.get(cutoff["status"], 0) + 1
        fill_rows += len(prepared.fills_by_leg)
        reference_legs += len(prepared.references_by_leg)
        floor_legs += len(prepared.floors_by_leg)
        chain_legs += len(prepared.regret_chains_by_leg)
        authority_legs += len(prepared.authority_d2_by_leg)
        if prepared.event_id == "KXATPCHALLENGERMATCH-26JUL12ALVVAN":
            first_receipts.append(prepared.seam_receipt())
    if calls != EXPECTED_CALLS or len(first_receipts) != len(candidate_ids):
        raise RuntimePreparationError("prepared call conservation failed")
    result_path = resolve_role(repo, results_directory)
    if result_path.exists():
        raise RuntimePreparationError("V4 results directory exists")
    return {
        "schema_version": VERSION + "-no-score-seam-probe-v1",
        "prepared_scorer_calls": calls,
        "candidate_count": len(candidate_ids),
        "event_count_per_candidate": D_REQUIRED,
        "prepared_boundary_role": "full_raw_V5_boundary",
        "normalized_boundary_selected_count": 0,
        "full_raw_V5_boundary_count": calls,
        "guarded_cutoff_success_count": calls,
        "guarded_cutoff_status_counts": dict(sorted(statuses.items())),
        "fill_bindings_across_calls": fill_rows,
        "reference_leg_bindings_across_calls": reference_legs,
        "floor_leg_bindings_across_calls": floor_legs,
        "regret_chain_leg_bindings_across_calls": chain_legs,
        "authority_d2_leg_bindings_across_calls": authority_legs,
        "first_V2_V3_failure_event_receipts": first_receipts,
        "first_failure_event_reached_with_raw_row": True,
        "scorer_imported": False,
        "scorer_call_attempts": 0,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "results_directory_created": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "performance": None,
        "ranking": None,
        "selection": None,
        "gate_pass": True,
    }


@dataclass
class ScoreAccounting:
    scorer_call_attempts: int = 0
    completed_event_rows: int = 0
    completed_candidates: int = 0
    active_candidate_id: str | None = None
    active_event_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def invoke_prepared_score(
    *,
    prepared: PreparedScorerCall,
    scorer: Callable[..., Mapping[str, Any]],
    accounting: ScoreAccounting,
    persist: Callable[[ScoreAccounting], None],
) -> Mapping[str, Any]:
    """Persist an attempt before entry; count completion only after return."""
    accounting.scorer_call_attempts += 1
    accounting.active_candidate_id = prepared.candidate_id
    accounting.active_event_id = prepared.event_id
    persist(accounting)
    row = scorer(**prepared.score_kwargs)
    accounting.completed_event_rows += 1
    persist(accounting)
    return row


def mark_candidate_completed(
    accounting: ScoreAccounting,
    persist: Callable[[ScoreAccounting], None],
) -> None:
    accounting.completed_candidates += 1
    accounting.active_candidate_id = None
    accounting.active_event_id = None
    persist(accounting)
