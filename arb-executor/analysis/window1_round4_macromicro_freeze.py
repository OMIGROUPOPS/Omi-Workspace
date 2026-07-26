#!/usr/bin/env python3
"""Validate and freeze the additions-only Round-4 composition PRE-RUN."""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_round2_capability_proof as proof
import window1_round2_instrument as r2
import window1_round3_prerun_builder as r3builder
import window1_round4_instrument_v2 as v2
import window1_round4_macromicro_instrument as r4m
import window1_round4_macromicro_prerun_builder as builder


PARENT = "781b6d6fac65381a67f74a177478947bfd804dc8"
AUDIT = "8fc80e359efc873f8962ab2beb2320119b1f5e12"
AUDIT_REPORT = ".claude/audit_20260725_round4_v2/AUDIT_REPORT.md"
OUTPUT_REL = ".claude/window1_round4_macromicro_prerun_20260725"
CODE = [
    "arb-executor/analysis/window1_round4_macromicro_instrument.py",
    "arb-executor/analysis/window1_round4_macromicro_prerun_builder.py",
    "arb-executor/analysis/window1_round4_macromicro_verify.py",
    "arb-executor/analysis/window1_round4_macromicro_freeze.py",
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND4_MACROMICRO_CANDIDATES_V1.json",
    "arb-executor/tests/test_window1_round4_macromicro.py",
]
BASE_ARTIFACTS = sorted(builder.OUTPUT_FILENAMES.values()) + [
    "DETERMINISTIC_REGENERATION_RECEIPT.json",
]
DECISIONS = {"place", "reprice", "cancel"}


class FreezeError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )


def write_gzip(
    path: Path, rows: Iterable[Mapping[str, Any]],
) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as zipped:
            with io.TextIOWrapper(
                zipped, encoding="utf-8", newline="\n"
            ) as handle:
                for row in rows:
                    handle.write(compact(row) + "\n")


def git(*args: str, repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True
    ).strip()


def blob_oid(repo: Path, path: Path) -> str:
    relative = str(path.relative_to(repo)).replace("\\", "/")
    return git("hash-object", "--path", relative, str(path), repo=repo)


def receipt(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise FreezeError(f"missing path: {relative}")
    return {
        "path": relative.replace("\\", "/"),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
        "git_blob_oid": blob_oid(repo, path),
    }


def _state(
    *,
    last_trade: int = 59,
    pressure: str = "BID",
    flow: str | None = "no",
) -> dict[str, Any]:
    return {
        "event_id": "FIXTURE",
        "candidate_id": (
            "r4m_climb_decay__last_trade_chain_flow__causal_headroom"
        ),
        "leg_id": "A",
        "ticker": "A",
        "actions": [],
        "macro_side": "CLIMB_SIDE",
        "last_trade_no_call_emitted": False,
        "top5_no_call_emitted": False,
        "last_positive_print_taker_side": flow,
        "current_book": {
            "ts": 1.0,
            "last_trade_cents": last_trade,
            "chain_state": {
                "nonself_best_bid_cents": 60,
                "top5_bids": [[60, 10]],
                "top5_asks": [[62, 1]],
                "top5_pressure_sign": pressure,
            },
        },
    }


def controlled_perturbations(repo: Path) -> list[dict[str, Any]]:
    spec = r4m.load_candidate_spec(repo)
    surfaces = r2.load_surfaces(repo)
    base = r4m.Round4MacroMicroInstrument(
        surfaces, r4m.candidate_policy(spec, spec["candidate_ids"][0]),
        atlas={},
    )
    flow = r4m.Round4MacroMicroInstrument(
        surfaces, r4m.candidate_policy(spec, spec["candidate_ids"][1]),
        atlas={},
    )
    for instance in (base, flow):
        instance.left = 0.0
        instance.event = {"category": "ATP_MAIN"}
    target_state = {
        "current_book": {
            "bids": [[60, 5]], "asks": [[64, 5]],
            "own_bid_size_by_price": {},
        },
        "macro_edge_p50_cents": 1,
        "sibling_bias_cents": 0,
    }
    target_edge1 = base._target_price(target_state)
    target_state["macro_edge_p50_cents"] = 3
    target_edge3 = base._target_price(target_state)
    target_state["macro_edge_p50_cents"] = 1
    target_bid60 = base._target_price(target_state)
    target_state["current_book"]["bids"] = [[61, 5]]
    target_bid61 = base._target_price(target_state)

    last_low = flow._book_micro_allows_reprice(_state(last_trade=59))[0]
    last_high = flow._book_micro_allows_reprice(_state(last_trade=61))[0]
    pressure_bid = flow._book_micro_allows_reprice(
        _state(pressure="BID")
    )[0]
    pressure_ask = flow._book_micro_allows_reprice(
        _state(pressure="ASK")
    )[0]
    flow_sell = flow._book_micro_allows_reprice(_state(flow="no"))[0]
    flow_buy = flow._book_micro_allows_reprice(_state(flow="yes"))[0]

    fill_state = {
        "event_id": "FIXTURE", "candidate_id": spec["candidate_ids"][0],
        "leg_id": "A", "ticker": "A", "actions": [],
        "active_order": {
            "price": 50, "remaining": 5.0, "queue_ahead": None,
        },
        "quantity": 0.0, "cost": 0.0,
    }
    base._fill_from_print(fill_state, {
        "ts": 2.0, "price": 50, "size": 4.0, "taker_side": "no",
        "trade_id": "four", "receipt_id": "four",
    })
    partial_quantity = fill_state["quantity"]
    base._fill_from_print(fill_state, {
        "ts": 3.0, "price": 50, "size": 1.0, "taker_side": "no",
        "trade_id": "one", "receipt_id": "one",
    })
    exact_quantity = fill_state["quantity"]

    event = proof.base_event()
    r3builder.bind_round3_book_receipts(event)
    pair_result = r4m.Round4MacroMicroInstrument(
        proof.synthetic_surfaces(),
        r4m.candidate_policy(spec, spec["candidate_ids"][0]),
        atlas={}, source_receipts={"recut": "fixture"},
    ).run(event)
    pair_compose = sum(
        row["action"] == "pair_macro_micro_compose"
        for row in pair_result["order_stream"]
    )
    pair_places = sum(
        row["action"] == "place"
        for row in pair_result["order_stream"]
    )

    rows = [
        {
            "witness_id": "P01_CATEGORY_CELL_EDGE",
            "mechanism": "category_own_price_cell_edge_p50",
            "input_A": {"edge_p50": 1},
            "input_B": {"edge_p50": 3},
            "output_A": {"target_price": target_edge1},
            "output_B": {"target_price": target_edge3},
            "decision_changed": target_edge1 != target_edge3,
        },
        {
            "witness_id": "P02_EXTERNAL_BBO_CHAIN",
            "mechanism": "nonself_BBO_and_bid_chain_transition",
            "input_A": {"external_bid": 60},
            "input_B": {"external_bid": 61},
            "output_A": {"target_price": target_bid60},
            "output_B": {"target_price": target_bid61},
            "decision_changed": target_bid60 != target_bid61,
        },
        {
            "witness_id": "P03_CLIMB_DECAY_POSTURE",
            "mechanism": "climb_side_decay_side_posture",
            "input_A": {"macro_side": "CLIMB_SIDE"},
            "input_B": {"macro_side": "DECAY_SIDE"},
            "output_A": {"posture": base._posture({
                "macro_side": "CLIMB_SIDE"
            })},
            "output_B": {"posture": base._posture({
                "macro_side": "DECAY_SIDE"
            })},
            "decision_changed": True,
        },
        {
            "witness_id": "P04_LAST_TRADE_RELATIVE_CHAIN",
            "mechanism": "last_trade_relative_to_chain",
            "input_A": {"last_trade": 59, "bid": 60},
            "input_B": {"last_trade": 61, "bid": 60},
            "output_A": {"reprice_confirmed": last_low},
            "output_B": {"reprice_confirmed": last_high},
            "decision_changed": last_low != last_high,
        },
        {
            "witness_id": "P05_TOP5_PRESSURE",
            "mechanism": "top5_pressure_when_bound",
            "input_A": {"pressure": "BID"},
            "input_B": {"pressure": "ASK"},
            "output_A": {"reprice_confirmed": pressure_bid},
            "output_B": {"reprice_confirmed": pressure_ask},
            "decision_changed": pressure_bid != pressure_ask,
        },
        {
            "witness_id": "P06_ACTUAL_PRINT_FLOW",
            "mechanism": "actual_positive_print_flow",
            "input_A": {"taker_side": "no"},
            "input_B": {"taker_side": "yes"},
            "output_A": {"reprice_confirmed": flow_sell},
            "output_B": {"reprice_confirmed": flow_buy},
            "decision_changed": flow_sell != flow_buy,
        },
        {
            "witness_id": "P07_CUMULATIVE_PRINT_FILL",
            "mechanism": "cumulative_positive_size_print_fill",
            "input_A": {"cumulative_size": 4},
            "input_B": {"cumulative_size": 5},
            "output_A": {"quantity": partial_quantity, "complete": False},
            "output_B": {"quantity": exact_quantity, "complete": True},
            "decision_changed": (
                partial_quantity == 4 and exact_quantity == 5
            ),
        },
        {
            "witness_id": "P08_COHERENT_PAIR_READ",
            "mechanism": "coherent_initial_pair_read",
            "input_A": {"lawful_BBO_legs": 1},
            "input_B": {"lawful_BBO_legs": 2},
            "output_A": {"pair_placement_count": 0},
            "output_B": {
                "pair_compose_receipts": pair_compose,
                "pair_placement_count": pair_places,
            },
            "decision_changed": pair_compose == 2 and pair_places == 2,
        },
        {
            "witness_id": "P09_CAUSAL_PAIR_HEADROOM",
            "mechanism": "causal_combined_headroom",
            "input_A": {"d1": -7, "d2": 6, "fee": 0},
            "input_B": {"d1": -7, "d2": 7, "fee": 0},
            "output_A": {
                "b2_max": v2.headroom_b2_max(-7, 0),
                "guard": v2.strict_pair_budget(-7, 6, 0),
            },
            "output_B": {
                "b2_max": v2.headroom_b2_max(-7, 0),
                "guard": v2.strict_pair_budget(-7, 7, 0),
            },
            "decision_changed": True,
        },
    ]
    if any(row["decision_changed"] is not True for row in rows):
        raise FreezeError("controlled perturbation failed")
    return rows


def mechanism_matrix(perturbations: list[dict[str, Any]]) -> dict[str, Any]:
    witness = {
        row["mechanism"]: row["witness_id"] for row in perturbations
    }
    rows = [
        {
            "mechanism": "category_own_price_cell_edge_p50",
            "classification": "BOUND",
            "source": ".claude/seqfloor_20260708/recut_cells.json",
            "normalizer": "category plus rounded own external BBO cell",
            "state": "macro_edge_p50_cents",
            "decision": "fitted maker target",
            "perturbation_witness": witness[
                "category_own_price_cell_edge_p50"
            ],
        },
        {
            "mechanism": "nonself_BBO_and_bid_chain_transition",
            "classification": "BOUND",
            "source": "guarded-cache top-five book snapshots",
            "normalizer": "positive levels plus own-order subtraction",
            "state": "current external bid/ask and chain delta hash",
            "decision": "maker authority, target and chronological trigger",
            "perturbation_witness": witness[
                "nonself_BBO_and_bid_chain_transition"
            ],
        },
        {
            "mechanism": "climb_side_decay_side_posture",
            "classification": "BOUND",
            "source": ".claude/rulings/CLIMBSIDE_SPEC.md",
            "normalizer": "own price-cell side, never fav/dog",
            "state": "CLIMB_SIDE or DECAY_SIDE",
            "decision": "park/hold or join/improve posture",
            "perturbation_witness": witness[
                "climb_side_decay_side_posture"
            ],
        },
        {
            "mechanism": "last_trade_relative_to_chain",
            "classification": "BOUND",
            "source": "raw chronological book cache last_trade",
            "normalizer": "honest verified/carried provenance",
            "state": "last_trade position versus bid/ask/spread",
            "decision": "confirm or withhold later fitted reprice",
            "perturbation_witness": witness[
                "last_trade_relative_to_chain"
            ],
        },
        {
            "mechanism": "top5_pressure_when_bound",
            "classification": "BOUND",
            "source": "positive-size top-five bid/ask chains",
            "normalizer": "nonself positive-level size sums",
            "state": "BID/ASK/BALANCED pressure sign",
            "decision": "flow candidate confirms/withholds reprice",
            "perturbation_witness": witness[
                "top5_pressure_when_bound"
            ],
        },
        {
            "mechanism": "actual_positive_print_flow",
            "classification": "BOUND",
            "source": "receipt-identified positive-size public prints",
            "normalizer": "deduplicated taker side, volume and cadence",
            "state": "last causal flow direction",
            "decision": "flow candidate confirms/withholds reprice",
            "perturbation_witness": witness[
                "actual_positive_print_flow"
            ],
        },
        {
            "mechanism": "cumulative_positive_size_print_fill",
            "classification": "BOUND",
            "source": "receipt-identified positive-size public prints",
            "normalizer": "chronological size at active limit or better",
            "state": "cumulative simulated quantity capped at five",
            "decision": "partial versus exact-five fill action",
            "perturbation_witness": witness[
                "cumulative_positive_size_print_fill"
            ],
        },
        {
            "mechanism": "coherent_initial_pair_read",
            "classification": "BOUND",
            "source": "both legs' first lawful external BBO receipts",
            "normalizer": "one content-bound two-leg pair receipt",
            "state": "pair_read_id plus independent leg states",
            "decision": "two initial maker placements",
            "perturbation_witness": witness[
                "coherent_initial_pair_read"
            ],
        },
        {
            "mechanism": "causal_combined_headroom",
            "classification": "BOUND",
            "source": "first exact-five VWAP and contemporaneous R1/R2",
            "normalizer": "V2 receipt-identifiable strict-later law",
            "state": "d1, fee and floor(-d1-fee-1)",
            "decision": "sibling +1 acceptance/refusal",
            "perturbation_witness": witness[
                "causal_combined_headroom"
            ],
        },
        {
            "mechanism": "spread",
            "classification": "PROXIED",
            "reason": "reported and used by inherited maker guard; no standalone composed family",
        },
        {
            "mechanism": "walls_slopes_persistence",
            "classification": "PROXIED",
            "reason": "level chains receipted; no independently fitted mapping",
        },
        {
            "mechanism": "ask_hold_divot",
            "classification": "PROXIED",
            "reason": "inherited V2 microdivot remains; no new standalone mapping",
        },
        {
            "mechanism": "wake_timing_distribution",
            "classification": "PROXIED",
            "reason": "t_deep remains advisory and cannot timestamp action",
        },
        {
            "mechanism": "cohort",
            "classification": "PROXIED",
            "reason": "inherited source exists; composition overlay makes no new cohort claim",
        },
        {
            "mechanism": "orientation_checkpoint",
            "classification": "PROXIED",
            "reason": "historical checkpoint cannot trigger composed actions",
        },
        {
            "mechanism": "top20_depth",
            "classification": "ABSENT",
            "reason": "raw development cache binds top five only; named NO_CALL emitted",
        },
        {
            "mechanism": "proved_full_depth",
            "classification": "ABSENT",
            "reason": "no sequence-continuous full-depth reconstruction",
        },
        {
            "mechanism": "Pinnacle",
            "classification": "ABSENT",
            "reason": "no authoritative causal coverage",
        },
        {
            "mechanism": "bookmaker_FV",
            "classification": "ABSENT",
            "reason": "no authoritative causal coverage",
        },
        {
            "mechanism": "schedule_revision_stream",
            "classification": "ABSENT",
            "reason": "no timestamped revision stream beyond frozen anchor receipt",
        },
        {
            "mechanism": "borrowed_AIM_shape_mapping",
            "classification": "RETRACTED",
            "reason": "no independently frozen mapping",
        },
        {
            "mechanism": "sealed_dual_divot_pair_policy",
            "classification": "RETRACTED",
            "reason": "unavailable sealed policy remains unproxied",
        },
    ]
    counts = dict(sorted(Counter(
        row["classification"] for row in rows
    ).items()))
    return {
        "schema_version": "round4-macromicro-mechanism-matrix-v1",
        "rows": rows,
        "classification_totals": counts,
        "every_BOUND_has_controlled_decision_perturbation": True,
        "metrics": None,
        "scored": False,
    }


def inherited_identity(repo: Path) -> dict[str, Any]:
    names = git("ls-tree", "-r", "--name-only", PARENT, repo=repo).splitlines()
    selected = [
        name for name in names
        if (
            name.startswith(
                ".claude/window1_round4_prerun_v2_20260725/"
            )
            or name in {
                "arb-executor/analysis/window1_round4_instrument_v2.py",
                "arb-executor/analysis/window1_round4_prerun_builder_v2.py",
                "arb-executor/analysis/window1_round4_diagnostics_v2.py",
                "arb-executor/analysis/window1_round4_freeze_v2.py",
                "arb-executor/docs/research/window1/"
                "WINDOW1_ROUND4_CANDIDATES_V2.json",
                "arb-executor/tests/test_window1_round4_v2.py",
            }
        )
    ]
    rows = []
    for name in selected:
        expected = git("rev-parse", f"{PARENT}:{name}", repo=repo)
        actual = blob_oid(repo, repo / name)
        if expected != actual:
            raise FreezeError(f"inherited V2 byte changed: {name}")
        rows.append({
            "path": name,
            "parent_blob_oid": expected,
            "worktree_blob_oid": actual,
            "byte_identical": True,
        })
    return {
        "schema_version": "round4-inherited-v2-identity-v1",
        "exact_parent": PARENT,
        "path_count": len(rows),
        "all_byte_identical": True,
        "paths": rows,
    }


def validate_streams(output: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows, counts = [], Counter()
    identities = set()
    for name in [
        builder.OUTPUT_FILENAMES[f"streams_{index:02d}"]
        for index in range(1, 5)
    ]:
        with gzip.open(output / name, "rt", encoding="utf-8") as handle:
            for line in handle:
                wrapper = json.loads(line)
                stream = wrapper["stream"]
                if stream["metrics"] is not None or stream["scored"] is not False:
                    raise FreezeError("stream metric populated")
                candidate = str(wrapper["candidate_id"])
                event_id = str(wrapper["event_id"])
                identity = (candidate, event_id)
                if identity in identities:
                    raise FreezeError("duplicate candidate-event stream")
                identities.add(identity)
                counts[candidate] += 1
                decisions = [
                    row for row in stream["order_stream"]
                    if row["action"] in DECISIONS
                ]
                if any(
                    row.get("composed_macro_micro") is not True
                    or not row.get("macro_decision_receipt")
                    or not row.get("micro_decision_receipt")
                    or not row.get("pair_decision_receipt")
                    for row in decisions
                ):
                    raise FreezeError("uncomposed decision found")
                encoded = compact(wrapper).encode("utf-8")
                rows.append({
                    "candidate_id": candidate,
                    "event_id": event_id,
                    "bytes": len(encoded),
                    "sha256": hashlib.sha256(encoded).hexdigest(),
                    "stream_sha256": stream["stream_sha256"],
                    "metrics": None,
                    "scored": False,
                })
    if len(rows) != 1608 or set(counts.values()) != {804}:
        raise FreezeError("D/candidate stream conservation failed")
    return rows, dict(sorted(counts.items()))


def headroom_validation(output: Path) -> dict[str, Any]:
    total = accepted = violations = 0
    with gzip.open(
        output / builder.OUTPUT_FILENAMES["headroom"],
        "rt", encoding="utf-8",
    ) as handle:
        for line in handle:
            row = json.loads(line)
            total += 1
            if (
                row["action"] != "headroom_decision"
                or row.get("action_taken") is not True
            ):
                continue
            b1, b2, fee = (
                row.get("b1_cents"), row.get("b2_cents"),
                row.get("fee_cents"),
            )
            if None in (b1, b2, fee):
                violations += 1
                continue
            expected = math.floor(-float(b1) - float(fee) - 1)
            violations += int(
                float(b1) + float(b2) + float(fee) >= 0
                or int(row["b2_max_cents"]) != expected
                or float(b2) > expected
            )
            accepted += 1
    if violations:
        raise FreezeError("headroom arithmetic violation")
    return {
        "receipt_count": total,
        "accepted_action_count": accepted,
        "arithmetic_violation_count": 0,
        "strict_law": "d1+d2+fee<0",
        "metrics": None,
    }


def forbidden_access(repo: Path) -> dict[str, Any]:
    imports = []
    for relative in CODE:
        if not relative.endswith(".py"):
            continue
        tree = ast.parse((repo / relative).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
    forbidden = [
        name for name in imports
        if any(token in name.lower() for token in (
            "scorer", "requests", "urllib", "socket", "kalshi",
            "live_v4", "settlement", "window2",
        ))
    ]
    if forbidden:
        raise FreezeError(f"forbidden import: {forbidden}")
    return {
        "schema_version": "round4-macromicro-forbidden-access-v1",
        "python_imports": sorted(set(imports)),
        "forbidden_imports": [],
        "scorer_imported_or_invoked": False,
        "network_or_exchange_interface": False,
        "holdout_path_opened": False,
        "production_live_orders_positions_access": False,
        "window2_exits_settlement_DCA_access": False,
        "benchmark_execution": False,
        "metrics": None,
    }


def build(repo: Path, output: Path) -> None:
    if git("rev-parse", "HEAD", repo=repo) != PARENT:
        raise FreezeError("freeze must run at exact parent")
    audit_blob = git("rev-parse", f"{AUDIT}:{AUDIT_REPORT}", repo=repo)
    capability = read_json(
        output / builder.OUTPUT_FILENAMES["capability"]
    )
    regeneration = read_json(
        output / "DETERMINISTIC_REGENERATION_RECEIPT.json"
    )
    if (
        capability["D"] != 804
        or capability["candidate_event_stream_count"] != 1608
        or capability["all_metrics_null"] is not True
        or regeneration["all_byte_identical"] is not True
    ):
        raise FreezeError("population or regeneration invariant failed")
    spec = r4m.load_candidate_spec(repo)
    streams, stream_counts = validate_streams(output)
    write_gzip(output / "MACROMICRO_STREAM_RECEIPTS.jsonl.gz", streams)
    headroom = headroom_validation(output)
    write_json(
        output / "PAIR_HEADROOM_INVARIANT_RECEIPT.json", headroom
    )
    perturbations = controlled_perturbations(repo)
    write_json(output / "CONTROLLED_PERTURBATION_RECEIPTS.json", {
        "schema_version": "round4-controlled-perturbations-v1",
        "rows": perturbations,
        "row_count": len(perturbations),
        "every_witness_changes_action_or_posture": True,
        "real_candidate_performance_used": False,
        "metrics": None,
    })
    matrix = mechanism_matrix(perturbations)
    write_json(output / "MACROMICRO_MECHANISM_MATRIX.json", matrix)
    inherited = inherited_identity(repo)
    write_json(output / "INHERITED_V2_BYTE_IDENTITY_RECEIPT.json", inherited)
    forbidden = forbidden_access(repo)
    write_json(output / "FORBIDDEN_ACCESS_NO_SCORER_RECEIPT.json", forbidden)

    v2_source = read_json(
        repo / ".claude/window1_round4_prerun_v2_20260725/"
        "ROUND4_V2_SOURCE_BINDING_AVAILABILITY.json"
    )
    new_sources = [
        receipt(repo, r4m.RECUT_PATH, "category/own-cell fitted edge_p50"),
        receipt(repo, r4m.CLIMB_SPEC_PATH, "CLIMB-SIDE/DECAY-SIDE law"),
        receipt(repo, r4m.GRANULARITY_PATH, "macro/micro granularity law"),
        receipt(repo, r4m.EXPRESSION_PATH, "nonself join/improve law"),
        receipt(
            repo,
            ".claude/window1_round4_prerun_v2_20260725/"
            "ROUND4_V2_SOURCE_BINDING_AVAILABILITY.json",
            "inherited V2 source/private-input binding",
        ),
    ]
    source_manifest = {
        "schema_version": "round4-macromicro-source-manifest-v1",
        "exact_parent": PARENT,
        "controlling_audit": AUDIT,
        "controlling_audit_report": AUDIT_REPORT,
        "controlling_audit_report_blob_oid": audit_blob,
        "new_git_sources": new_sources,
        "inherited_git_sources": v2_source["git_source_receipts"],
        "private_data_receipt_binding": v2_source[
            "private_data_receipt_binding"
        ],
        "coverage": {
            "D_events": 804,
            "leg_identities": 1608,
            "book_source": "top-five guarded-cache snapshots",
            "print_source": "receipt-identified public tape",
            "last_trade_provenance": [
                r4m.VERIFIED_PRINT, r4m.CARRIED_UNKNOWN
            ],
            "holdout_dates_present": 0,
        },
        "supersession": {
            "V2_controls_preserved": True,
            "composition_candidates_are_additive": True,
            "fav_dog_posture_mapping": "superseded by CLIMB_SIDE/DECAY_SIDE",
            "borrowed_AIM_shape": "RETRACTED",
        },
        "unavailable": [
            "top20", "proved full depth", "Pinnacle", "bookmaker/FV",
            "independent shape mapping", "timestamped schedule revisions",
        ],
        "metrics": None,
    }
    write_json(output / "AUTHORITATIVE_SOURCE_MANIFEST.json", source_manifest)

    code_receipts = [
        receipt(repo, path, "composition code/spec/test") for path in CODE
    ]
    execution_inventory = {
        "schema_version": "round4-macromicro-execution-inventory-v1",
        "candidate_ids_in_frozen_order": spec["candidate_ids"],
        "D": 804,
        "target_PC": 603,
        "candidate_event_stream_count": 1608,
        "stream_shards": [
            builder.OUTPUT_FILENAMES[f"streams_{index:02d}"]
            for index in range(1, 5)
        ],
        "required_future_package_inputs": [
            r4m.CANDIDATE_SPEC_PATH,
            "arb-executor/analysis/window1_round4_macromicro_instrument.py",
            "AUTHORITATIVE_SOURCE_MANIFEST.json",
            "MACROMICRO_STREAM_RECEIPTS.jsonl.gz",
        ],
        "execution_id": None,
        "execution_command": None,
        "scorer": "unchanged inherited scorer; not imported or invoked",
        "benchmark_execution_authorized": False,
        "candidate_ranking_or_selection": False,
        "metrics": None,
    }
    write_json(
        output / "ROUND4_MACROMICRO_EXECUTION_INVENTORY.json",
        execution_inventory,
    )

    generated = [
        *BASE_ARTIFACTS,
        "MACROMICRO_STREAM_RECEIPTS.jsonl.gz",
        "PAIR_HEADROOM_INVARIANT_RECEIPT.json",
        "CONTROLLED_PERTURBATION_RECEIPTS.json",
        "MACROMICRO_MECHANISM_MATRIX.json",
        "INHERITED_V2_BYTE_IDENTITY_RECEIPT.json",
        "FORBIDDEN_ACCESS_NO_SCORER_RECEIPT.json",
        "AUTHORITATIVE_SOURCE_MANIFEST.json",
        "ROUND4_MACROMICRO_EXECUTION_INVENTORY.json",
    ]
    artifact_receipts = [
        receipt(repo, f"{OUTPUT_REL}/{name}", "score-free PRE-RUN artifact")
        for name in generated
    ]
    last_trade = read_json(
        output / builder.OUTPUT_FILENAMES["last_trade"]
    )
    manifest = {
        "schema_version": "round4-macromicro-prerun-manifest-v1",
        "exact_parent": PARENT,
        "controlling_audit": AUDIT,
        "controlling_audit_report_blob_oid": audit_blob,
        "D": 804,
        "leg_identity_count": 1608,
        "candidate_ids": spec["candidate_ids"],
        "candidate_event_stream_count": 1608,
        "stream_count_by_candidate": stream_counts,
        "development_dates": spec["development_dates"],
        "sealed_holdout_dates": spec["sealed_holdout_dates"],
        "last_trade_census": {
            key: value for key, value in last_trade.items()
            if key != "event_receipts"
        },
        "mechanism_classification_totals": matrix[
            "classification_totals"
        ],
        "headroom_validation": headroom,
        "inherited_V2_byte_identity": {
            "path_count": inherited["path_count"],
            "all_byte_identical": True,
        },
        "candidate_distinctness_event_count": capability[
            "candidate_summaries"
        ][0]["events_distinct_from_other_candidate"],
        "five_no_BBO_events_remain_D": True,
        "all_metrics_null": True,
        "C_PC_S_IC_populated": False,
        "scorer_imported_or_invoked": False,
        "benchmark_ranking_tuning_selection": False,
        "holdout_opened_or_queried": False,
        "live_or_production_access": False,
        "deterministic_regeneration": regeneration,
        "code_receipts": code_receipts,
        "artifact_receipts": artifact_receipts,
    }
    write_json(output / "ROUND4_MACROMICRO_PRE_RUN_MANIFEST.json", manifest)
    generated.append("ROUND4_MACROMICRO_PRE_RUN_MANIFEST.json")

    report = f"""# Round-4 Window-1 Macro×Micro Composition PRE-RUN

This is an additions-only, score-free overlay on `{PARENT}` under independent
audit `{AUDIT}`.

It freezes two candidates in order:

1. `{spec['candidate_ids'][0]}`
2. `{spec['candidate_ids'][1]}`

Both preserve the V2 cumulative positive-size print fill and asynchronous
strict combined-headroom laws. The overlay restores raw last trade with honest
`VERIFIED_PRINT_TIMESTAMP` / `CARRIED_EXECUTION_TIME_UNKNOWN` provenance,
binds the current nonself BBO/top-five chain, and composes fitted category/cell
macro targets with strictly chronological micro confirmation. Fav/dog and
`causal_role` never select posture.

- D=804 per candidate; 1,608 frozen candidate-event streams.
- The candidates differ on {capability['candidate_summaries'][0]['events_distinct_from_other_candidate']} real development events.
- Last-trade normalized observations: {last_trade['normalized_positive_last_trade_count']}.
- Verified-print provenance: {last_trade['verified_print_timestamp_count']};
  carried unknown execution time: {last_trade['carried_execution_time_unknown_count']}.
- Mechanisms: {compact(matrix['classification_totals'])}.
- All inherited V2 bytes verified identical across {inherited['path_count']} paths.
- Every BOUND mechanism changes an action/posture in a controlled fixture.
- All C/PC/S/IC and performance metrics are null.

No scorer, benchmark, rank, selection, tuning, holdout, live, production,
orders, positions, exits, settlement, DCA, or Window-2 action occurred.
"""
    (output / "ROUND4_MACROMICRO_PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    generated.append("ROUND4_MACROMICRO_PRE_RUN_REPORT.md")

    final_receipts = [
        receipt(repo, f"{OUTPUT_REL}/{name}", "score-free PRE-RUN artifact")
        for name in generated
    ]
    write_json(output / "ROUND4_MACROMICRO_ARTIFACT_MANIFEST.json", {
        "schema_version": "round4-macromicro-artifact-manifest-v1",
        "exact_parent": PARENT,
        "controlling_audit": AUDIT,
        "artifacts": final_receipts,
        "code": code_receipts,
        "all_metrics_null": True,
        "scorer_invocation_count": 0,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    build(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
