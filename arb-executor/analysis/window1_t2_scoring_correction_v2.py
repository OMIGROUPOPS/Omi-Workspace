#!/usr/bin/env python3
"""Mechanical T2 scoring-package V2 reconciliations.

This module is score-free.  It reads the frozen T2 target/decision receipts,
validates exact combined-headroom arithmetic, and reduces target-level
authority/d2 provenance without deriving any performance result.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-t2-scoring-correction-v2"
T2_PACKAGE = Path(".claude/window1_t2_causal_divot_prerun_20260727")
OPPORTUNITY_SHARDS = tuple(
    f"SIBLING_X_OPPORTUNITY_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
DECISION_SHARDS = tuple(
    f"TARGET_SELECTION_REJECTED_TARGET_LEDGER_{part:02d}.jsonl.gz"
    for part in range(1, 17)
)
SUPPORT_LEDGER = "CURRENT_EXPOSURE_SUPPORT_DECAY_LEDGER.jsonl.gz"
EXPECTED_SURFACES = 4_576_794
EXPECTED_LAWFUL_TARGETS = 2_996_560
EXPECTED_V1_PRESERVATION_RECEIPTS = 1_172_973
DECISIONS = ("HOLD", "NO_CALL", "PARK", "REPRICE", "PLACE")
D2_SIGNS = ("NEGATIVE", "ZERO", "POSITIVE", "UNKNOWN")


class CorrectionError(RuntimeError):
    """The frozen T2 receipts fail a V2 mechanical reconciliation."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CorrectionError(
                    f"invalid JSON at {path}:{line_number}"
                ) from exc
            if not isinstance(value, dict):
                raise CorrectionError(
                    f"non-object JSON row at {path}:{line_number}"
                )
            yield value


def exact_decimal(value: Any, field: str) -> tuple[Decimal, str]:
    """Return an exact finite Decimal and its frozen JSON number type.

    Floats are converted from their shortest round-trip representation, never
    through ``int`` or binary arithmetic.  Booleans, strings, NaN, and
    infinity fail closed.
    """

    if isinstance(value, bool):
        raise CorrectionError(f"{field} is bool")
    if isinstance(value, int):
        result, raw_type = Decimal(value), "integer"
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise CorrectionError(f"{field} is non-finite")
        result, raw_type = Decimal(repr(value)), "finite_float"
    else:
        raise CorrectionError(
            f"{field} has unsupported type {type(value).__name__}"
        )
    if not result.is_finite():
        raise CorrectionError(f"{field} is non-finite")
    return result, raw_type


def exact_integer(value: Any, field: str) -> tuple[int, str]:
    decimal, raw_type = exact_decimal(value, field)
    integral = decimal.to_integral_value()
    if decimal != integral:
        raise CorrectionError(f"{field} is fractional: {decimal}")
    return int(integral), raw_type


def headroom_values(d1_value: Any, fee_value: Any) -> dict[str, Any]:
    d1, d1_type = exact_decimal(d1_value, "d1_cents")
    fee, fee_type = exact_decimal(fee_value, "fee_cents")
    canonical = int(
        (-d1 - fee).to_integral_value(rounding=ROUND_CEILING)
    ) - 1
    inherited = int(
        (-d1 - fee - Decimal(1)).to_integral_value(
            rounding=ROUND_FLOOR
        )
    )
    return {
        "d1_exact_decimal": str(d1),
        "d1_raw_json_type": d1_type,
        "frozen_fee_exact_decimal": str(fee),
        "frozen_fee_raw_json_type": fee_type,
        "canonical_b2_max_cents": canonical,
        "inherited_floor_expression_b2_max_cents": inherited,
        "formulas_equal": canonical == inherited,
    }


def normalize_d2_sign(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    decimal, _ = exact_decimal(value, "d2_cents")
    if decimal < 0:
        return "NEGATIVE"
    if decimal > 0:
        return "POSITIVE"
    return "ZERO"


def normalize_authority(raw: str) -> str:
    mapping = {
        "NATIVE_MACRO_TARGET": "NATIVE_MACRO",
        "CAUSAL_DIVOT_LATER_RECURRENCE": "CAUSAL_DIVOT",
        "ACTIVE_PARENT_EXPOSURE": "PARENT_EXPOSURE",
        "LIVEAIM_AIM_DEEP_SOURCE_MAPPING": "LIVE_AIM",
        "CURRENT_TRUE_PRINT_REACH_CONTEXT": "MARKET_CONTEXT",
        "CURRENT_EXTERNAL_BID": "MARKET_CONTEXT",
        "BID_PLUS_ONE_FALLBACK_NOT_PREFERRED": "FALLBACK_NOT_PREFERRED",
    }
    return mapping.get(raw, "UNKNOWN")


def surface_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        str(row.get("candidate_id")),
        str(row.get("event_id")),
        str(row.get("leg_id")),
        row.get("timestamp"),
        str(row.get("trigger_receipt")),
    )


def target_identity(target: Mapping[str, Any]) -> tuple[str, int]:
    x, _ = exact_integer(target.get("X_cents"), "target X_cents")
    return str(target.get("source")), x


def _counter_rows(counter: Mapping[tuple[str, ...], int]) -> list[dict[str, Any]]:
    return [
        {
            "raw_target_authority": key[0],
            "normalized_authority_family": key[1],
            "omitted_lawful_d2_sign": key[2],
            "target_count": count,
        }
        for key, count in sorted(counter.items())
    ]


def _support_preservation_keys(
    repo: Path,
) -> tuple[Counter[tuple[Any, ...]], Counter[str], int]:
    keys: Counter[tuple[Any, ...]] = Counter()
    decisions: Counter[str] = Counter()
    row_count = 0
    for row in iter_gzip(repo / T2_PACKAGE / SUPPORT_LEDGER):
        row_count += 1
        if (
            row.get("decision") == "HOLD"
            and row.get("rejection_reason")
            == "NO_NAMED_RECEIPT_BACKED_EVIDENCE_DECAY"
        ):
            key = surface_key(row)
            keys[key] += 1
            decisions["HOLD"] += 1
    return keys, decisions, row_count


def reconcile_target_surfaces(
    repo: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Stream all target surfaces and their one terminal decision.

    Returns the target-surface reconciliation, headroom receipt, and one
    compact provenance row per candidate/event/leg.
    """

    preservation_keys, preservation_decisions, support_rows = (
        _support_preservation_keys(repo)
    )
    surfaces = 0
    child_targets = 0
    lawful_targets = 0
    unlawful_targets = 0
    no_call_surfaces = 0
    available_surfaces = 0
    surface_decisions: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    raw_authorities: Counter[str] = Counter()
    normalized_authorities: Counter[str] = Counter()
    d2_signs: Counter[str] = Counter()
    lawful_by_authority_sign: Counter[tuple[str, str, str]] = Counter()
    unlawful_by_authority_reason: Counter[tuple[str, str]] = Counter()
    selected_targets = 0
    selected_lawful_targets = 0
    selected_unlawful_targets = 0
    surface_decision_mismatches = 0
    preservation_key_overlap = 0
    preservation_overlap_terminal_counts: Counter[str] = Counter()
    preservation_key_missing_from_terminal = set(preservation_keys)
    d1_types: Counter[str] = Counter()
    fee_types: Counter[str] = Counter()
    fee_values: Counter[str] = Counter()
    headroom_target_checks = 0
    headroom_difference_rows: list[dict[str, Any]] = []
    inherited_b2_mismatches: list[dict[str, Any]] = []
    chain: dict[
        tuple[str, str, str],
        dict[str, Any],
    ] = defaultdict(lambda: {
        "surface_count": 0,
        "target_entry_count": 0,
        "lawful_target_entry_count": 0,
        "unlawful_target_entry_count": 0,
        "all_lawful": Counter(),
        "recognized_not_targeted": Counter(),
        "targeted_not_exposed": Counter(),
        "exposed_not_credited": Counter(),
    })

    for opportunity_name, decision_name in zip(
        OPPORTUNITY_SHARDS, DECISION_SHARDS
    ):
        opportunity_path = repo / T2_PACKAGE / opportunity_name
        decision_path = repo / T2_PACKAGE / decision_name
        opportunity_iter = iter_gzip(opportunity_path)
        decision_iter = iter_gzip(decision_path)
        shard_rows = 0
        while True:
            try:
                surface = next(opportunity_iter)
            except StopIteration:
                surface = None
            try:
                decision = next(decision_iter)
            except StopIteration:
                decision = None
            if surface is None or decision is None:
                if surface is not None or decision is not None:
                    raise CorrectionError(
                        f"surface/decision shard length mismatch: "
                        f"{opportunity_name}"
                    )
                break
            shard_rows += 1
            surfaces += 1
            if surface_key(surface) != surface_key(decision):
                surface_decision_mismatches += 1
                raise CorrectionError(
                    "surface and terminal decision identity mismatch"
                )
            status = str(surface.get("status"))
            status_counts[status] += 1
            available_surfaces += int(status == "AVAILABLE")
            no_call_surfaces += int(status != "AVAILABLE")
            terminal = str(decision.get("decision"))
            if terminal not in DECISIONS:
                raise CorrectionError(
                    f"unknown terminal decision: {terminal}"
                )
            surface_decisions[terminal] += 1
            key = surface_key(surface)
            if key in preservation_keys:
                preservation_key_overlap += preservation_keys[key]
                preservation_overlap_terminal_counts[terminal] += (
                    preservation_keys[key]
                )
                preservation_key_missing_from_terminal.discard(key)
            chain_key = (
                str(surface["candidate_id"]),
                str(surface["event_id"]),
                str(surface["leg_id"]),
            )
            aggregate = chain[chain_key]
            aggregate["surface_count"] += 1
            selected = decision.get("selected_target")
            selected_identity = (
                target_identity(selected)
                if isinstance(selected, Mapping) else None
            )
            if selected_identity is not None:
                selected_targets += 1
            targets = surface.get("targets") or []
            if targets:
                surface_headroom = headroom_values(
                    surface.get("d1_cents"), surface.get("fee_cents")
                )
                d1_types[surface_headroom["d1_raw_json_type"]] += 1
                fee_types[
                    surface_headroom["frozen_fee_raw_json_type"]
                ] += 1
                fee_values[
                    surface_headroom["frozen_fee_exact_decimal"]
                ] += 1
                surface_b2, _ = exact_integer(
                    surface.get("b2_max_cents"),
                    "surface b2_max_cents",
                )
                if surface_b2 != surface_headroom[
                    "inherited_floor_expression_b2_max_cents"
                ]:
                    raise CorrectionError(
                        "surface b2_max differs from inherited expression"
                    )
            for target_ordinal, target in enumerate(targets, 1):
                if not isinstance(target, Mapping):
                    raise CorrectionError("target entry is not an object")
                child_targets += 1
                aggregate["target_entry_count"] += 1
                authority = str(target.get("source"))
                family = normalize_authority(authority)
                sign = normalize_d2_sign(target.get("d2_cents"))
                raw_authorities[authority] += 1
                normalized_authorities[family] += 1
                d2_signs[sign] += 1
                lawful = target.get("lawful") is True
                identity = target_identity(target)
                is_selected = identity == selected_identity
                target_d1, _ = exact_decimal(
                    target.get("d1_cents"), "target d1_cents"
                )
                target_fee, _ = exact_decimal(
                    target.get("fee_cents"), "target fee_cents"
                )
                if (
                    target_d1
                    != Decimal(surface_headroom["d1_exact_decimal"])
                    or target_fee
                    != Decimal(
                        surface_headroom["frozen_fee_exact_decimal"]
                    )
                ):
                    raise CorrectionError(
                        "target d1/fee differs from its target surface"
                    )
                target_headroom = surface_headroom
                headroom_target_checks += 1
                target_b2, _ = exact_integer(
                    target.get("b2_max_cents"), "target b2_max_cents"
                )
                if target_b2 != target_headroom[
                    "inherited_floor_expression_b2_max_cents"
                ]:
                    if len(inherited_b2_mismatches) < 1000:
                        inherited_b2_mismatches.append({
                            "candidate_id": surface["candidate_id"],
                            "event_id": surface["event_id"],
                            "leg_id": surface["leg_id"],
                            "timestamp": surface["timestamp"],
                            "trigger_receipt": surface["trigger_receipt"],
                            "target_ordinal": target_ordinal,
                            "target_source": authority,
                            "X_cents": target["X_cents"],
                            "frozen_b2_max_cents": target_b2,
                            **target_headroom,
                        })
                if not target_headroom["formulas_equal"]:
                    headroom_difference_rows.append({
                        "candidate_id": surface["candidate_id"],
                        "event_id": surface["event_id"],
                        "leg_id": surface["leg_id"],
                        "timestamp": surface["timestamp"],
                        "trigger_receipt": surface["trigger_receipt"],
                        "target_ordinal": target_ordinal,
                        "target_source": authority,
                        "X_cents": target["X_cents"],
                        **target_headroom,
                    })
                if lawful:
                    lawful_targets += 1
                    aggregate["lawful_target_entry_count"] += 1
                    provenance_key = (authority, family, sign)
                    aggregate["all_lawful"][provenance_key] += 1
                    lawful_by_authority_sign[provenance_key] += 1
                    if is_selected:
                        selected_lawful_targets += 1
                        if terminal in {"PLACE", "REPRICE", "HOLD"}:
                            aggregate["exposed_not_credited"][
                                provenance_key
                            ] += 1
                        else:
                            aggregate["targeted_not_exposed"][
                                provenance_key
                            ] += 1
                    elif authority == "CAUSAL_DIVOT_LATER_RECURRENCE":
                        aggregate["recognized_not_targeted"][
                            provenance_key
                        ] += 1
                else:
                    unlawful_targets += 1
                    aggregate["unlawful_target_entry_count"] += 1
                    if is_selected:
                        selected_unlawful_targets += 1
                    checks = target.get("checks")
                    if not isinstance(checks, Mapping):
                        raise CorrectionError("unlawful target lacks checks")
                    failed = tuple(
                        sorted(
                            str(name) for name, verdict in checks.items()
                            if verdict is not True
                        )
                    )
                    if not failed:
                        raise CorrectionError(
                            "unlawful target has no rejection reason"
                        )
                    unlawful_by_authority_reason[
                        (authority, "|".join(failed))
                    ] += 1

    if surfaces != EXPECTED_SURFACES:
        raise CorrectionError(
            f"surface count {surfaces} != {EXPECTED_SURFACES}"
        )
    if lawful_targets != EXPECTED_LAWFUL_TARGETS:
        raise CorrectionError(
            f"lawful target count {lawful_targets} != "
            f"{EXPECTED_LAWFUL_TARGETS}"
        )
    if sum(surface_decisions.values()) != surfaces:
        raise CorrectionError("one-terminal-decision conservation failed")
    if surface_decision_mismatches:
        raise CorrectionError("surface/decision mismatches are nonzero")
    if inherited_b2_mismatches:
        raise CorrectionError(
            "frozen b2_max differs from inherited floor expression"
        )
    if len(headroom_difference_rows) > 100_000:
        raise CorrectionError(
            "unexpectedly large headroom formula discrepancy"
        )
    v1_preservation_receipt_sum = (
        surface_decisions["HOLD"] + preservation_decisions["HOLD"]
    )
    if (
        v1_preservation_receipt_sum
        != EXPECTED_V1_PRESERVATION_RECEIPTS
    ):
        raise CorrectionError(
            "V1 parent-preservation typed receipt sum did not reproduce"
        )

    provenance_rows: list[dict[str, Any]] = []
    for (candidate, event_id, leg_id), value in sorted(chain.items()):
        provenance_rows.append({
            "schema_version": VERSION + "-authority-d2-provenance-v1",
            "candidate_id": candidate,
            "event_id": event_id,
            "leg_id": leg_id,
            "target_surface_count": value["surface_count"],
            "target_entry_count": value["target_entry_count"],
            "lawful_target_entry_count": value[
                "lawful_target_entry_count"
            ],
            "unlawful_target_entry_count": value[
                "unlawful_target_entry_count"
            ],
            "lawful_target_provenance": _counter_rows(
                value["all_lawful"]
            ),
            "unused_lawful_target_provenance_by_primary_loss_stage": {
                "RECOGNIZED_NOT_TARGETED": _counter_rows(
                    value["recognized_not_targeted"]
                ),
                "TARGETED_NOT_EXPOSED": _counter_rows(
                    value["targeted_not_exposed"]
                ),
                "EXPOSED_NOT_CREDITED": _counter_rows(
                    value["exposed_not_credited"]
                ),
            },
            "source_surface_receipt_row_count": value["surface_count"],
            "metrics": None,
            "performance": None,
            "scored": False,
        })

    headroom = {
        "schema_version": VERSION + "-headroom-arithmetic-v1",
        "canonical_expression": "ceil(-d1 - frozen_fee) - 1",
        "inherited_expression": "floor(-d1 - frozen_fee - 1)",
        "numeric_validation": (
            "finite exact Decimal from JSON integer or finite float "
            "round-trip representation; bool/string/fractional integer "
            "coercion forbidden"
        ),
        "frozen_fee_raw_json_type_counts": dict(sorted(fee_types.items())),
        "frozen_fee_exact_value_counts": dict(sorted(fee_values.items())),
        "d1_raw_json_type_counts": dict(sorted(d1_types.items())),
        "applicable_sibling_target_count": headroom_target_checks,
        "formula_difference_count": len(headroom_difference_rows),
        "formula_difference_identities": headroom_difference_rows,
        "frozen_b2_max_vs_inherited_expression_mismatch_count": 0,
        "target_change_count": len(headroom_difference_rows),
        "prior_certification_discrepancy": (
            "PRIOR_CERTIFIED_TARGET_BUDGET_FORMULA_DIVERGENCE"
            if headroom_difference_rows else None
        ),
        "package_blocked": bool(headroom_difference_rows),
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    reconciliation = {
        "schema_version": VERSION + "-target-surface-reconciliation-v1",
        "grain_contract": {
            "target_surface": (
                "one candidate/event/sibling-leg/chronological trigger "
                "receipt after a credited first fill"
            ),
            "child_target": (
                "one authority+integer-X candidate nested within a target "
                "surface; multiple child targets share one surface"
            ),
            "terminal_decision": (
                "exactly one HOLD/NO_CALL/PARK/REPRICE/PLACE row per "
                "target surface"
            ),
            "rejected_replacement_preservation_receipt": (
                "a secondary support-decay receipt nested within a matching "
                "terminal HOLD surface; not an additional surface"
            ),
        },
        "target_surface_rows": surfaces,
        "surface_status_counts": dict(sorted(status_counts.items())),
        "available_target_surfaces": available_surfaces,
        "market_evidence_no_call_surfaces": no_call_surfaces,
        "child_target_entries": child_targets,
        "lawful_target_entries": lawful_targets,
        "unlawful_target_entries": unlawful_targets,
        "child_conservation_pass": (
            child_targets == lawful_targets + unlawful_targets
        ),
        "raw_target_authority_counts": dict(
            sorted(raw_authorities.items())
        ),
        "normalized_authority_family_counts": dict(
            sorted(normalized_authorities.items())
        ),
        "d2_sign_counts": dict(sorted(d2_signs.items())),
        "lawful_by_authority_family_d2_sign": [
            {
                "raw_target_authority": key[0],
                "normalized_authority_family": key[1],
                "d2_sign": key[2],
                "count": count,
            }
            for key, count in sorted(lawful_by_authority_sign.items())
        ],
        "unlawful_by_authority_and_rejection_reason": [
            {
                "raw_target_authority": key[0],
                "rejection_reason": key[1],
                "count": count,
            }
            for key, count in sorted(
                unlawful_by_authority_reason.items()
            )
        ],
        "selected_target_entries": selected_targets,
        "selected_lawful_target_entries": selected_lawful_targets,
        "selected_unlawful_target_entries": selected_unlawful_targets,
        "terminal_decision_counts": {
            name: surface_decisions[name] for name in DECISIONS
        },
        "terminal_decision_rows": sum(surface_decisions.values()),
        "one_terminal_decision_per_surface": True,
        "surface_decision_identity_mismatch_count": 0,
        "support_decay_rows": support_rows,
        "non_displacing_parent_exposure": {
            "terminal_HOLD_surface_decisions": (
                surface_decisions["HOLD"]
            ),
            "secondary_rejected_replacement_receipts": (
                preservation_decisions["HOLD"]
            ),
            "secondary_receipts_with_matching_HOLD_surface": (
                preservation_overlap_terminal_counts["HOLD"]
            ),
            "secondary_receipt_matching_terminal_decision_counts": {
                name: preservation_overlap_terminal_counts[name]
                for name in DECISIONS
            },
            "secondary_receipts_with_matching_target_surface": (
                preservation_key_overlap
            ),
            "secondary_receipts_without_matching_target_surface": sum(
                preservation_keys[key]
                for key in preservation_key_missing_from_terminal
            ),
            "secondary_keys_without_matching_target_surface": len(
                preservation_key_missing_from_terminal
            ),
            "V1_reported_typed_receipt_sum": (
                v1_preservation_receipt_sum
            ),
            "V1_reported_value_reproduced": True,
            "unique_secondary_preservation_surface_keys": len(
                preservation_keys
            ),
            "sum_is_not_a_unique_surface_count": True,
        },
        "reported_count_relationship": {
            "target_surfaces": EXPECTED_SURFACES,
            "lawful_targets": EXPECTED_LAWFUL_TARGETS,
            "V1_parent_exposure_preservation_typed_receipts": (
                EXPECTED_V1_PRESERVATION_RECEIPTS
            ),
            "same_denominator": False,
            "arithmetic_difference_claimed": False,
            "relationship": (
                "lawful targets are nested children of surfaces; the V1 "
                "preservation number is terminal HOLD surfaces plus a nested "
                "secondary receipt stream"
            ),
        },
        "unexplained_residue_count": 0,
        "package_blocked": False,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    return reconciliation, headroom, provenance_rows


def partition_loss_attribution(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate already-selected target provenance after scoring.

    This helper does not infer d2 from a fill.  It consumes only target-level
    provenance frozen before execution.
    """

    counts: Counter[tuple[str, str, str, str]] = Counter()
    source_total = 0
    for row in rows:
        stage = str(row["primary_loss_stage"])
        for item in row.get("omitted_lawful_target_provenance") or []:
            sign = str(item["omitted_lawful_d2_sign"])
            if sign not in D2_SIGNS:
                raise CorrectionError(f"unknown omitted d2 sign: {sign}")
            count, _ = exact_integer(item["target_count"], "target_count")
            if count < 0:
                raise CorrectionError("negative target count")
            key = (
                str(item["raw_target_authority"]),
                str(item["normalized_authority_family"]),
                sign,
                stage,
            )
            counts[key] += count
            source_total += count
    partitions = [
        {
            "raw_target_authority": key[0],
            "normalized_authority_family": key[1],
            "omitted_lawful_d2_sign": key[2],
            "primary_loss_stage": key[3],
            "target_count": count,
        }
        for key, count in sorted(counts.items())
    ]
    partition_total = sum(row["target_count"] for row in partitions)
    if partition_total != source_total:
        raise CorrectionError("authority/d2 partition lost target rows")
    return {
        "partitions": partitions,
        "target_level_source_count": source_total,
        "partition_target_count": partition_total,
        "conservation_pass": True,
        "d2_inferred_from_successful_fill": False,
    }
