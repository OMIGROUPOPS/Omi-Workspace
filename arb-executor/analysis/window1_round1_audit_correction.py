#!/usr/bin/env python3
"""Generate the controlling Round-1 correction without strategy evaluation.

This program reads only the committed Round-1 selected-event ledger and result
summary.  It re-derives the selected metrics and the audited failure census,
marks the four T8/T6-contaminated comparison rows ineligible, and writes a
sanitized correction receipt/report.  It imports no search or execution code.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


VERSION = "window1-round1-audit-correction-v1"
AUDIT_COMMIT = "024f03bb5b1944bae39ad5afef6ee019ef5dc06d"
RESULTS_COMMIT = "f7cd420951f074104dbc602b84137c5eed7455da"
SELECTED_ID = "drift_cohort_orientation__walk__reaim"
CONTAMINATED_IDS = [
    "pair_divot_core__park__hold",
    "pair_divot_core__park__reaim",
    "pair_divot_core__walk__hold",
    "pair_divot_core__walk__reaim",
]
LOT = 5.0


class CorrectionError(RuntimeError):
    """Raised when the immutable Round-1 record does not reproduce."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_epoch(value: str) -> float:
    return dt.datetime.fromisoformat(value).timestamp()


def reproduce_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in rows:
        legs = list(row.get("legs") or [])
        cutoff = row.get("strict_positive_cutoff_utc")
        quantities_ok = (
            len(legs) == 2
            and all(abs(float(leg.get("quantity") or 0) - LOT) < 1e-9
                    for leg in legs)
        )
        completions_ok = False
        if quantities_ok and cutoff:
            cutoff_epoch = iso_epoch(str(cutoff))
            completions_ok = all(
                leg.get("completion_exchange_ts") is not None
                and float(leg["completion_exchange_ts"]) <= cutoff_epoch
                for leg in legs
            )
        complete = bool(quantities_ok and completions_ok)
        deltas = [leg.get("window1_close_delta_cents") for leg in legs]
        have_deltas = (
            len(deltas) == 2 and all(value is not None for value in deltas)
        )
        pc = bool(complete and have_deltas and sum(deltas) < 0)
        s = bool(
            complete
            and row.get("combined_entry_cost_cents") is not None
            and float(row["combined_entry_cost_cents"]) < 100
        )
        ic = bool(
            complete and have_deltas and all(float(value) < 0
                                             for value in deltas)
        )
        expected = {"C": complete, "PC": pc, "S": s, "IC": ic}
        for field, value in expected.items():
            if bool(row.get(field)) != value:
                raise CorrectionError(
                    f"{field} flag mismatch for {row.get('event_id')}"
                )
            totals[field] += int(value)
    return {name: int(totals[name]) for name in ("C", "PC", "S", "IC")}


def failure_decomposition(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    split: Counter[str] = Counter()
    censored: Counter[str] = Counter()
    by_date: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        classification = str(row["classification"])
        if classification == "nonfill":
            statuses = [str(leg.get("status")) for leg in row.get("legs") or []]
            if row.get("feature_coverage_class") == (
                "window_left_after_guarded_start"
            ):
                bucket = "zero_length_window1_opportunity"
            elif statuses.count("filled") == 1:
                bucket = "naked_single_leg_fill"
            elif statuses == ["not_filled", "not_filled"]:
                bucket = "genuine_zero_fill"
            else:
                raise CorrectionError(
                    "unrecognized Round-1 nonfill shape for "
                    f"{row.get('event_id')}: {statuses}"
                )
            split[bucket] += 1
            by_date[str(row["event_date"])][bucket] += 1
        elif classification == "censored":
            statuses = [str(leg.get("status")) for leg in row.get("legs") or []]
            coverage = str(row.get("feature_coverage_class"))
            if coverage == "start_boundary_censored":
                bucket = "start_boundary"
            elif "missing_placement_evidence" in statuses:
                bucket = "missing_feature_or_birth_book"
            else:
                bucket = "queue_ambiguous"
            censored[bucket] += 1
    expected_split = {
        "genuine_zero_fill": 582,
        "naked_single_leg_fill": 84,
        "zero_length_window1_opportunity": 12,
    }
    expected_censored = {
        "start_boundary": 85,
        "missing_feature_or_birth_book": 11,
        "queue_ambiguous": 6,
    }
    if dict(split) != expected_split:
        raise CorrectionError(f"nonfill decomposition changed: {dict(split)}")
    if dict(censored) != expected_censored:
        raise CorrectionError(
            f"censored decomposition changed: {dict(censored)}"
        )
    return {
        "former_nonfill_total": sum(split.values()),
        "corrected": expected_split,
        "censored_total": sum(censored.values()),
        "censored": expected_censored,
        "by_date": {
            date: dict(sorted(values.items()))
            for date, values in sorted(by_date.items())
        },
    }


def os_family_matrix() -> list[dict[str, Any]]:
    """Audit-controlled status of the six nominal Round-1 OS families."""
    return [
        {
            "family_id": "pair_divot_core",
            "loaded": True,
            "available": False,
            "evaluated": True,
            "decision_changing": "unusable",
            "actually_selected": False,
            "evidence": (
                "all four rows struck: T8 price read a T6-derived called_band "
                "through sealed_depth"
            ),
        },
        {
            "family_id": "drift_cohort_orientation",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": True,
            "actually_selected": True,
            "evidence": (
                "selected family; T6 delay, walk, and sibling reaim changed "
                "decisions, while drift/cohort/orientation did not"
            ),
        },
        {
            "family_id": "mirror_deceleration",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": False,
            "actually_selected": False,
            "evidence": (
                "decision-identical to drift_cohort_orientation at every "
                "committed reporting grain"
            ),
        },
        {
            "family_id": "dynamic_recut_atlas",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": True,
            "actually_selected": False,
            "evidence": "recut and atlas defined distinct prices and C=2",
        },
        {
            "family_id": "causal_micro_pressure",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": True,
            "actually_selected": False,
            "evidence": "top-five pressure and causal bookmaker FV changed prices",
        },
        {
            "family_id": "full_chronological_stack",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": True,
            "actually_selected": False,
            "evidence": "distinct combined lawful actuator stack",
        },
    ]


def feature_family_matrix() -> list[dict[str, Any]]:
    """Audit-controlled actuator status of named Round-1 feature families."""
    rows = [
        ("pair_law", True, True, True, True, True,
         "two-leg object and complete-stream law"),
        ("first_fill_sibling_response", True, "partial", True, True, True,
         "selected reaim ablation changed C from 10 to 6"),
        ("sealed_bands", True, "partial", True, False, False,
         "selected ablation identical; pair-family use is struck"),
        ("dual_divot_steering_and_catch", True, "partial", True, True, True,
         "static divot depth changed base price; catch timing was absent"),
        ("drift_recognition", True, "partial", True, False, False,
         "selected ablation identical"),
        ("cohort_steering", True, "partial", True, False, False,
         "selected ablation identical"),
        ("orientation_prior", True, "partial", True, False, False,
         "selected ablation identical"),
        ("walk_park_posture", True, "partial", True, True, True,
         "walk ablation changed selected C from 10 to 9"),
        ("riser_deceleration_mirror_seesaw", True, "partial", False, False,
         False, "coverage flag only; riser actuator lawfully disarmed"),
        ("dynamic_floor_and_recut_cells", True, "partial", True, True, False,
         "recut family distinct; selected family did not select it"),
        ("atlas", True, "partial", True, True, False,
         "recut-atlas family distinct"),
        ("reach", True, "partial", True, False, False,
         "computed and stored only; no pricing/action consumer"),
        ("shape_corpus", True, False, False, False, False,
         "no independent non-AIM causal cell mapping"),
        ("bookmaker_fv", True, "partial", True, True, False,
         "changed causal-micro/full prices where causal"),
        ("pinnacle", False, False, False, False, False,
         "zero causal rows; unavailable and unused"),
        ("causal_bbo", True, "partial", True, True, True,
         "base order expression and queue state"),
        ("top_five_pressure", True, "partial", True, True, False,
         "changed causal-micro/full prices, not selected family"),
        ("true_print_flow", True, True, True, True, True,
         "fill evidence and walk trigger"),
        ("own_order_fingerprints", True, "partial", True, False, False,
         "coverage flag only; contributed volume was not separated"),
        ("real_start_guard", True, "partial", True, True, True,
         "boundary and censoring law, never schedule-as-start"),
        ("raw_ws_full_depth", False, False, False, False, False,
         "no snapshot-ancestry plus sequence-continuous reconstruction"),
    ]
    return [
        {
            "family_id": family,
            "loaded": loaded,
            "available": available,
            "evaluated": evaluated,
            "decision_changing": changing,
            "actually_selected": selected,
            "evidence": evidence,
        }
        for (
            family, loaded, available, evaluated, changing, selected,
            evidence,
        ) in rows
    ]


def render_report(receipt: Mapping[str, Any]) -> str:
    metrics = receipt["selected_metrics"]
    failure = receipt["failure_decomposition"]
    os_rows = receipt["os_family_capability_matrix"]
    feature_rows = receipt["feature_family_capability_matrix"]
    lines = [
        "# Round-1 Window-1 corrected record",
        "",
        f"Status: **controlling correction** to results commit `{RESULTS_COMMIT}`",
        f"under independent audit `{AUDIT_COMMIT}`. No strategy candidate was",
        "rerun and no score was recomputed from a new order stream.",
        "",
        "## Selected result preserved",
        "",
        f"- D = {metrics['D']}",
        f"- C = {metrics['C']}",
        f"- PC = {metrics['PC']}",
        f"- S = {metrics['S']}",
        f"- IC = {metrics['IC']}",
        f"- selected candidate = `{SELECTED_ID}`",
        "",
        "These values independently reproduce from the 804 selected-event rows.",
        "",
        "## Corrected failure census",
        "",
        "The former `nonfill = 678` headline is replaced by:",
        "",
        f"- {failure['corrected']['genuine_zero_fill']} genuine zero-fill events;",
        f"- {failure['corrected']['naked_single_leg_fill']} naked single-leg fills;",
        f"- {failure['corrected']['zero_length_window1_opportunity']} zero-length "
        "Window-1 opportunities.",
        "",
        "The 102 censored events remain separate: 85 start-boundary censored,",
        "11 missing-feature/no-causal-birth-book censored, and 6 queue-ambiguous.",
        "Feature absence is never counted as a nonfill.",
        "",
        "## Scope of the optimistic bound",
        "",
        "The 26 optimistic completions bound only the selected candidate's",
        "counterfactual order stream and, because it was the grid maximum, the",
        "frozen 24-candidate Round-1 grid, including its lawfully allowed",
        "post-start intervals. It is not a market ceiling, a data ceiling, or a",
        "bound on a candidate with different per-leg timing or price expression.",
        "",
        "## T8/T6 lookahead correction",
        "",
        "The following comparison rows are struck from lawful comparison:",
        "",
    ]
    lines.extend(f"- `{candidate}`" for candidate in CONTAMINATED_IDS)
    lines.extend([
        "",
        "They posted at T8 but priced their sealed-depth term with a",
        "`called_band` derived at T6. The selected candidate is unaffected.",
        "No replacement values are asserted without a newly frozen rerun.",
        "",
        "## Nominal OS-family capability",
        "",
        "| family | loaded | available | evaluated | decision-changing | selected |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in os_rows:
        lines.append(
            "| {family_id} | {loaded} | {available} | {evaluated} | "
            "{decision_changing} | {actually_selected} |".format(**row)
        )
    lines.extend([
        "",
        "The six family names therefore did not represent six independently",
        "decision-changing behaviors. Mirror was decision-identical to the",
        "selected drift family; the pair family is ineligible because of lookahead.",
        "",
        "## Feature-family capability",
        "",
        "| family | loaded | available | evaluated | decision-changing | selected |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in feature_rows:
        lines.append(
            "| {family_id} | {loaded} | {available} | {evaluated} | "
            "{decision_changing} | {actually_selected} |".format(**row)
        )
    lines.extend([
        "",
        "Here `decision-changing` means an observed lawful Round-1 grid decision",
        "or result changed through that actuator; `selected` means the selected",
        "candidate actually used it to change at least one eligible decision.",
        "",
        "## Unavailable or non-actuating Round-1 machinery",
        "",
        "- full depth: unavailable; snapshot ancestry and gap-free sequence",
        "  reconstruction were not proved;",
        "- Pinnacle: unavailable (zero causal rows);",
        "- shape corpus: unavailable without an independent non-AIM causal mapping;",
        "- reach and own-order fingerprints: loaded/coverage-evaluated but inert;",
        "- asynchronous per-leg divot timing and exact one-cent non-self walk:",
        "  absent from Round 1 and therefore the central Round-2 repair.",
        "",
        "July 24-26 remains unopened. This correction touched no production, live,",
        "configuration, order, position, settlement, exit, DCA, or Window-2 surface.",
        "",
    ])
    return "\n".join(lines)


def run(repo: Path, output_dir: Path) -> None:
    result_path = (
        repo / ".claude/window1_os_family_results_20260724/"
        "WINDOW1_OS_FAMILY_RESULTS.json"
    )
    ledger_path = (
        repo / ".claude/window1_os_family_results_20260724/"
        "WINDOW1_OS_FAMILY_SELECTED_EVENTS.jsonl"
    )
    results = read_json(result_path)
    rows = read_jsonl(ledger_path)
    if len(rows) != 804 or len({row["event_id"] for row in rows}) != 804:
        raise CorrectionError("D or event identity changed")
    if results.get("selected_policy_id") != SELECTED_ID:
        raise CorrectionError("selected candidate changed")
    metrics = reproduce_metrics(rows)
    expected = {"C": 10, "PC": 9, "S": 9, "IC": 4}
    if metrics != expected:
        raise CorrectionError(f"selected metrics changed: {metrics}")
    classifications = Counter(str(row["classification"]) for row in rows)
    if sum(classifications.values()) != 804:
        raise CorrectionError("classification conservation failed")
    candidate_ids = {
        str(row["policy_id"]) for row in results.get("candidates") or []
    }
    missing = set(CONTAMINATED_IDS) - candidate_ids
    if missing:
        raise CorrectionError(f"contaminated candidates missing: {missing}")
    receipt = {
        "schema_version": VERSION,
        "generated_from": {
            "results_commit": RESULTS_COMMIT,
            "controlling_audit_commit": AUDIT_COMMIT,
            "results_path": str(result_path.relative_to(repo)).replace("\\", "/"),
            "results_sha256": sha256(result_path),
            "selected_ledger_path": str(
                ledger_path.relative_to(repo)
            ).replace("\\", "/"),
            "selected_ledger_sha256": sha256(ledger_path),
        },
        "strategy_search_rerun": False,
        "candidate_scoring_performed": False,
        "D": 804,
        "selected_policy_id": SELECTED_ID,
        "selected_metrics": {"D": 804, **metrics},
        "classification_history": dict(sorted(classifications.items())),
        "failure_decomposition": failure_decomposition(rows),
        "optimistic_completion_bound": {
            "count": 26,
            "scope": (
                "selected candidate and frozen 24-candidate Round-1 grid "
                "counterfactual order streams, including allowed post-start "
                "intervals"
            ),
            "market_ceiling": False,
            "data_ceiling": False,
        },
        "lookahead_correction": {
            "ineligible_candidate_ids": CONTAMINATED_IDS,
            "defect": (
                "T8 order price consumed sealed_depth(called_band) where "
                "called_band used T6 recognition"
            ),
            "selected_candidate_affected": False,
            "replacement_scores_asserted": False,
        },
        "os_family_capability_matrix": os_family_matrix(),
        "feature_family_capability_matrix": feature_family_matrix(),
        "holdout": {
            "dates": ["2026-07-24", "2026-07-25", "2026-07-26"],
            "opened": False,
            "queried": False,
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = output_dir / "ROUND1_CORRECTION_RECEIPT.json"
    report_path = output_dir / "WINDOW1_ROUND1_CORRECTED_REPORT.md"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report_path.write_text(
        render_report(receipt), encoding="utf-8", newline="\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".claude/window1_round1_corrected_20260724"),
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output_dir
    if not output.is_absolute():
        output = repo / output
    run(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
