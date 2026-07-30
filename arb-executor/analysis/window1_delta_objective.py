#!/usr/bin/env python3
"""Re-cut the full-lawful Window-1 opportunity set on close-relative delta.

This is intentionally separate from the pair-cost ladder.  PC is a completed
pair whose accounting fills have negative combined delta to the two frozen
Window-1 closes.  This module measures the tape ceiling for that objective
using the already-built full-lawful touch oracle and the frozen scorer close
contract.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


FULL_LAWFUL = (
    ".claude/window1_t2_iteration_history/"
    "WINDOW1_FULL_LAWFUL_CEILING.json"
)
CONTROL_LEDGER = (
    ".claude/"
    "window1_t2_results_w1-t2-dev-20260712-20260720-"
    "frontier-regret-grid1-scorepkg-v5/"
    "01_w1_t2__macro_hold__fixed_admission_parent_control_"
    "EVENT_LEDGER.jsonl"
)
DEFAULT_OUTPUT = (
    ".claude/window1_live_v4_replay/delta_objective_20260729"
)
SELECTED_CATEGORIES = (
    "ATP_CHALL",
    "ATP_MAIN",
    "WTA_CHALL",
    "WTA_MAIN",
)
SELECTED_EVENT_IDS = (
    "KXATPCHALLENGERMATCH-26JUL19HURBIG",
    "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
    "KXATPMATCH-26JUL12LAJVAN",
    "KXWTACHALLENGERMATCH-26JUL16BRAVED",
    "KXWTAMATCH-26JUL20KORJIM",
)


class DeltaError(RuntimeError):
    """The delta analysis contract did not reconcile."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise DeltaError(f"object required: {path}:{line_number}")
            rows.append(value)
    return rows


def floor_by_leg(
    floor: Mapping[str, Any] | None,
    *,
    sequential: bool,
) -> dict[str, int] | None:
    if not floor:
        return None
    if sequential:
        return {
            str(floor["first_leg_id"]): int(floor["first_target_cents"]),
            str(floor["second_leg_id"]): int(floor["second_target_cents"]),
        }
    touches = floor.get("touches") or {}
    if len(touches) != 2:
        return None
    return {
        str(leg_id): int(row["price_cents"])
        for leg_id, row in touches.items()
    }


def ladder(values: Iterable[int]) -> dict[str, int]:
    rows = list(values)
    thresholds = (1, 2, 3, 5, 10, 15, 20)
    return {
        **{
            f"combined_delta_le_minus_{threshold}_count": sum(
                value <= -threshold for value in rows
            )
            for threshold in thresholds
        },
        "combined_delta_zero_count": sum(value == 0 for value in rows),
        "combined_delta_positive_count": sum(value > 0 for value in rows),
        "available_count": len(rows),
    }


def measure(
    events: Iterable[Mapping[str, Any]],
    references: Mapping[str, Mapping[str, Any]],
    *,
    floor_key: str,
    sequential: bool,
) -> list[dict[str, Any]]:
    output = []
    for event in events:
        if (
            not event.get("positive_guarded_boundary")
            or event.get("zero_length_selected_window")
        ):
            continue
        event_id = str(event["event_id"])
        reference = references.get(event_id)
        floor = floor_by_leg(event.get(floor_key), sequential=sequential)
        if reference is None or floor is None:
            continue
        closes = {
            str(leg["leg_id"]): int(leg["window1_close_cents"])
            for leg in reference.get("legs") or []
            if (
                leg.get("available")
                and isinstance(leg.get("window1_close_cents"), int)
            )
        }
        if set(closes) != set(floor):
            continue
        deltas = {
            leg_id: int(floor[leg_id]) - int(closes[leg_id])
            for leg_id in sorted(floor)
        }
        combined = sum(deltas.values())
        output.append({
            "event_id": event_id,
            "event_date": event["event_date"],
            "category": event["category"],
            "start_evidence": event["source_group"],
            "selected_left_ts": event["selected_left_ts"],
            "evaluator_right_ts": event["evaluator_right_ts"],
            "close_cents_by_leg": closes,
            "reachable_price_cents_by_leg": floor,
            "delta_cents_by_leg": deltas,
            "combined_delta_cents": combined,
            "both_legs_negative_delta": all(
                value < 0 for value in deltas.values()
            ),
            "negative_combined_delta": combined < 0,
        })
    return output


def choose_five(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_event = {row["event_id"]: row for row in rows}
    selected = []
    for event_id in SELECTED_EVENT_IDS:
        row = by_event.get(event_id)
        if row is None:
            raise DeltaError(f"selected event unavailable: {event_id}")
        if not (
            row["negative_combined_delta"]
            and row["both_legs_negative_delta"]
            and row["start_evidence"] == "observed_official_exact"
        ):
            raise DeltaError(f"selected event fails delta law: {event_id}")
        selected.append(row)
    if set(row["category"] for row in selected) != set(
        SELECTED_CATEGORIES
    ):
        raise DeltaError("selected sample does not span all categories")
    return selected


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "authoritative_close_and_two_leg_touch_available_count": len(rows),
        "both_legs_reachable_below_own_close_count": sum(
            row["both_legs_negative_delta"] for row in rows
        ),
        "negative_combined_delta_count": sum(
            row["negative_combined_delta"] for row in rows
        ),
        "delta_ladder": ladder(
            row["combined_delta_cents"] for row in rows
        ),
        "by_category": {
            category: {
                "available_count": sum(
                    row["category"] == category for row in rows
                ),
                "both_legs_negative_count": sum(
                    row["category"] == category
                    and row["both_legs_negative_delta"]
                    for row in rows
                ),
                "combined_negative_count": sum(
                    row["category"] == category
                    and row["negative_combined_delta"]
                    for row in rows
                ),
            }
            for category in SELECTED_CATEGORIES
        },
    }


def render_ladder(result: Mapping[str, Any]) -> str:
    independent = result["independent_touch"]
    sequential = result["strict_sequential_touch"]
    ladder_rows = []
    for threshold in (1, 2, 3, 5, 10, 15, 20):
        key = f"combined_delta_le_minus_{threshold}_count"
        ladder_rows.append(
            f"| ≤ −{threshold}¢ | "
            f"{independent['delta_ladder'][key]} | "
            f"{sequential['delta_ladder'][key]} |"
        )
    category_rows = [
        (
            f"| {category} | {values['available_count']} | "
            f"{values['both_legs_negative_count']} | "
            f"{values['combined_negative_count']} |"
        )
        for category, values in sequential["by_category"].items()
    ]
    unavailable = result["population"] - sequential[
        "authoritative_close_and_two_leg_touch_available_count"
    ]
    return "\n".join([
        "# Window-1 close-relative delta ladder",
        "",
        (
            "**This is not the cost-under-par ladder.** Delta is "
            "`reachable price − authoritative Window-1 close`, per leg. "
            "Combined delta is the sum of the two leg deltas. The frozen "
            "PC scorer uses this close-relative quantity and a zero-cent "
            "frozen fee."
        ),
        "",
        (
            "Fill model: resting order, later true-price touch fills; no "
            "depth proof and no five-contract capacity gate."
        ),
        "",
        "## Headline",
        "",
        (
            f"- **{sequential['both_legs_reachable_below_own_close_count']} "
            "of 804** had both legs reachable strictly below their own "
            "authoritative Window-1 close."
        ),
        (
            f"- **{sequential['negative_combined_delta_count']} of 804** "
            "had negative combined reachable delta."
        ),
        (
            f"- The comparison is defined for **"
            f"{sequential['authoritative_close_and_two_leg_touch_available_count']} "
            f"of 804**. The other **{unavailable}** are not assigned a "
            "synthetic close or opportunity."
        ),
        "",
        "## Ladder",
        "",
        "| combined reachable delta | independent touch | strict sequential touch |",
        "|---|---:|---:|",
        *ladder_rows,
        (
            f"| exactly 0¢ | "
            f"{independent['delta_ladder']['combined_delta_zero_count']} | "
            f"{sequential['delta_ladder']['combined_delta_zero_count']} |"
        ),
        "",
        (
            "The two columns are equal here. Both leg orderings were tested "
            "by the strict oracle; sequencing did not change the attainable "
            "close-relative minima in this population."
        ),
        "",
        "## By category",
        "",
        "| category | defined | both legs < close | combined delta < 0 |",
        "|---|---:|---:|---:|",
        *category_rows,
        "",
        "## Denominator",
        "",
        (
            "There are 693 games with a measurable nonzero guarded Window 1. "
            "Of those, 680 have a two-leg touch floor. A further 58 do not "
            "have an authoritative two-leg close under the scorer's "
            "latest-timestamp tie law, leaving 622 defined delta comparisons. "
            "The other 111 games have no lawful nonzero evaluator window."
        ),
        "",
    ])


def render_alvvan(row: Mapping[str, Any]) -> str:
    return "\n".join([
        "# ALVVAN — close-relative delta correction",
        "",
        (
            "**Sealed was the better value authority, but neither authority "
            "completed the pair.** Comparing aims to the tape low answered "
            "reachability; it did not answer Window-1 value."
        ),
        "",
        "| leg | Window-1 close | legacy aim | legacy delta | sealed aim | sealed delta |",
        "|---|---:|---:|---:|---:|---:|",
        "| VAN | 22¢ | 22¢ | 0¢ | 16¢ | −6¢ |",
        "| ALV | 78¢ | 74¢ | −4¢ | 70¢ | −8¢ |",
        "| pair | 100¢ | 96¢ | **−4¢** | 86¢ | **−14¢** |",
        "",
        "What filled:",
        "",
        (
            "- Before the field repair, legacy VAN 22 filled and legacy ALV "
            "74 missed. One leg is not a PC pair."
        ),
        (
            "- With the field repair, the OS canceled legacy 22/74 and "
            "reposted sealed 16/70 before the tape touched VAN 22. Neither "
            "sealed leg filled."
        ),
        (
            "- With field repair plus wait-for-recognition, the orders were "
            "born directly at sealed 16/70. Again, neither filled."
        ),
        "",
        (
            "Therefore the aimed deltas were legacy **−4¢** and sealed "
            "**−14¢**, but achieved combined delta is undefined for both "
            "because neither completed. PC remains false. The correct "
            "conclusion is: **sealed selected substantially more Window-1 "
            "value and sacrificed all reach on this game.**"
        ),
        "",
        (
            "Tape context: the full lawful lows were VAN 22 and ALV 78, the "
            "same as their authoritative closes here. Legacy could reach only "
            "VAN; sealed could reach neither."
        ),
        "",
    ])


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    output = (repo / args.output).resolve()
    full = json.loads(
        (repo / FULL_LAWFUL).read_text(encoding="utf-8")
    )
    control = read_jsonl((repo / CONTROL_LEDGER).resolve())
    if len(full["events"]) != 804 or len(control) != 804:
        raise DeltaError("expected 804 full-lawful and reference rows")
    references = {str(row["event_id"]): row for row in control}
    independent_rows = measure(
        full["events"],
        references,
        floor_key="independent_touch_floor",
        sequential=False,
    )
    sequential_rows = measure(
        full["events"],
        references,
        floor_key="strict_sequential_touch_floor",
        sequential=True,
    )
    if {
        row["event_id"] for row in independent_rows
    } != {
        row["event_id"] for row in sequential_rows
    }:
        raise DeltaError("independent/sequential delta populations differ")
    selected = choose_five(sequential_rows)
    result = {
        "schema_version": "window1-close-relative-delta-v1",
        "objective": {
            "leg_delta": (
                "reachable_price_cents - authoritative_window1_close_cents"
            ),
            "combined_delta": "sum(two leg deltas)",
            "PC": (
                "completed pair and combined_delta_cents < 0; "
                "frozen fee_cents = 0"
            ),
            "separate_from_pair_cost_under_par": True,
        },
        "population": 804,
        "full_lawful_boundary_census": full["boundary_census"],
        "independent_touch": summary(independent_rows),
        "strict_sequential_touch": summary(sequential_rows),
        "strict_sequential_event_rows": sequential_rows,
        "selected_five": selected,
        "selection_law": (
            "negative combined delta; both legs individually negative; "
            "nonzero full lawful window; observed official exact start; "
            "all four categories represented; both live authorities emitted "
            "a comparable aim on both legs under field repair plus "
            "recognition-before-place"
        ),
        "pre_screen_exclusions": [
            {
                "event_id": "KXATPCHALLENGERMATCH-26JUL12DEGEE",
                "reason": (
                    "recognition-before-place emitted no two-leg authority "
                    "decision; retained as a failed trace, not used for the "
                    "requested authority-depth comparison"
                ),
            },
            {
                "event_id": "KXATPMATCH-26JUL12DROBLO",
                "reason": (
                    "sealed authority emitted no aims; retained as a failed "
                    "trace, not used for the requested legacy-versus-sealed "
                    "comparison"
                ),
            },
        ],
        "start_evidence_counts_selected": dict(Counter(
            row["start_evidence"] for row in selected
        )),
    }
    alvvan = next(
        row for row in sequential_rows
        if row["event_id"]
        == "KXATPCHALLENGERMATCH-26JUL12ALVVAN"
    )
    alvvan_result = {
        "event_id": alvvan["event_id"],
        "window1_close_cents": {"VAN": 22, "ALV": 78},
        "legacy": {
            "aim_cents": {"VAN": 22, "ALV": 74},
            "aim_delta_cents": {"VAN": 0, "ALV": -4},
            "combined_aim_delta_cents": -4,
            "pre_field_repair_fills": {"VAN": 22, "ALV": None},
            "completed_pair": False,
            "achieved_combined_delta_cents": None,
            "PC": False,
        },
        "sealed": {
            "aim_cents": {"VAN": 16, "ALV": 70},
            "aim_delta_cents": {"VAN": -6, "ALV": -8},
            "combined_aim_delta_cents": -14,
            "field_repaired_fills": {"VAN": None, "ALV": None},
            "wait_for_recognition_fills": {"VAN": None, "ALV": None},
            "completed_pair": False,
            "achieved_combined_delta_cents": None,
            "PC": False,
        },
        "full_lawful_tape_low_cents": {"VAN": 22, "ALV": 78},
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "WINDOW1_DELTA_LADDER.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "WINDOW1_DELTA_LADDER.md").write_text(
        render_ladder(result),
        encoding="utf-8",
        newline="\n",
    )
    (output / "ALVVAN_DELTA_RECUT.json").write_text(
        json.dumps(alvvan_result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "ALVVAN_DELTA_RECUT.md").write_text(
        render_alvvan(alvvan_result),
        encoding="utf-8",
        newline="\n",
    )
    (output / "FIVE_GAME_SELECTION.json").write_text(
        json.dumps({
            "selection_law": result["selection_law"],
            "games": selected,
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "independent_touch": result["independent_touch"],
        "strict_sequential_touch": result["strict_sequential_touch"],
        "selected": [
            row["event_id"] for row in selected
        ],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--output", default=DEFAULT_OUTPUT)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
