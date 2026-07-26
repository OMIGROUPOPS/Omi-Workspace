from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_range_attack_guarded_fill_adapter_v1 import (  # noqa: E402
    GuardedFillError,
    adapt_fillability_rows,
)
from window1_range_attack_reference_adapter_v1 import (  # noqa: E402
    Window1CloseReference,
    derive_window1_close_reference,
)
from window1_range_attack_scorer_v1 import (  # noqa: E402
    aggregate_candidate,
    score_event,
)


CANDIDATE = "w1_range_attack__macro_hold__combined_headroom"
EVENT = {
    "event_id": "KXTEST-26JUL12AB",
    "event_date": "2026-07-12",
    "category": "ATP_MAIN",
    "scheduled_start_exchange_ts": 20_000.0,
    "legs": [
        {"leg": "A", "ticker": "KXTEST-26JUL12AB-A"},
        {"leg": "B", "ticker": "KXTEST-26JUL12AB-B"},
    ],
}


def boundary(*, positive: bool = True) -> dict:
    return {
        "schema_version": "window1-real-start-ledger-v5-guarded",
        "event_id": EVENT["event_id"],
        "start_source_class": "official_exact",
        "positive_window1_provable": positive,
        "guard_censor_reason": None if positive else "fixture_censor",
        "exact_start_utc": 20_000.0,
        "guard_band": {
            "guard_id": "official-point-strict-60s-v1",
            "positive_guard_seconds": 60,
        },
    }


def fill_row(
    leg: str,
    *,
    evidence_type: str = "PRICE_REACHED",
    target: int = 50,
    evidence_ts: float = 19_000.0,
) -> dict:
    is_print = evidence_type == "PRICE_REACHED"
    evidence = (
        {
            "receipt": f"print-{leg}",
            "ts": evidence_ts,
            "price": target,
            "size": 0.25,
        }
        if is_print
        else {
            "receipt": f"book-{leg}",
            "ts": evidence_ts,
            "target_price_cents": target,
            "external_ask_price_cents": target - 1,
        }
    )
    return {
        "candidate_id": CANDIDATE,
        "event_id": EVENT["event_id"],
        "event_date": EVENT["event_date"],
        "category": EVENT["category"],
        "leg_id": leg,
        "ticker": f"KXTEST-26JUL12AB-{leg}",
        "order_interval_id": f"{CANDIDATE}|fixture|{leg}|0001",
        "opened_ts": 18_000.0,
        "evaluated_right_ts": 19_940.0,
        "target_price_cents": target,
        "boundary": {
            "event_id": EVENT["event_id"],
            "start_source_class": "official_exact",
            "positive_window1_provable": True,
            "schedule_can_prove_positive": False,
            "guarded_cutoff_ts": 19_940.0,
            "guard_id": "official-point-strict-60s-v1",
            "guard_seconds": 60,
        },
        "FILLABLE_AT_X": True,
        "FILLABLE_AT_X_evidence_type": evidence_type,
        "FILLABLE_AT_X_evidence": evidence,
        "PRICE_REACHED": is_print,
        "STRICT_ASK_CERTAIN_FILL": not is_print,
        "primary_price_fillability_assigns_five": True,
        "accounting_quantity_if_later_scored": 5,
        "accounting_fill_price_if_later_scored": target,
        "metrics": None,
        "scored": False,
    }


def expected_legs() -> dict:
    return {
        (EVENT["event_id"], "A"): "KXTEST-26JUL12AB-A",
        (EVENT["event_id"], "B"): "KXTEST-26JUL12AB-B",
    }


def adapted(rows: list[dict]) -> dict:
    values = adapt_fillability_rows(
        rows,
        expected_candidates=frozenset({CANDIDATE}),
        expected_legs=expected_legs(),
    )
    return {
        leg: values[(CANDIDATE, EVENT["event_id"], leg)]
        for leg in ("A", "B")
        if (CANDIDATE, EVENT["event_id"], leg) in values
    }


def reference(leg: str, close: int | None) -> Window1CloseReference:
    return Window1CloseReference(
        event_id=EVENT["event_id"],
        event_date=EVENT["event_date"],
        leg_id=leg,
        ticker=f"KXTEST-26JUL12AB-{leg}",
        available=close is not None,
        window1_close_cents=close,
        reference_ts=19_900.0 if close is not None else None,
        reference_receipt=f"ref-{leg}" if close is not None else None,
        reference_source="synthetic_true_print_fixture",
        t8_floor_ts=-8_800.0,
        guarded_cutoff_ts=19_940.0,
        boundary_source_class="official_exact",
        boundary_guard_id="official-point-strict-60s-v1",
        reason=None if close is not None else "missing_fixture_reference",
    )


def scored(
    prices: tuple[int, int],
    closes: tuple[int | None, int | None],
    *,
    fill_legs: tuple[str, ...] = ("A", "B"),
) -> dict:
    rows = [
        fill_row(leg, target=prices[0 if leg == "A" else 1])
        for leg in fill_legs
    ]
    return score_event(
        candidate_id=CANDIDATE,
        event=EVENT,
        boundary=boundary(),
        fills_by_leg=adapted(rows),
        references_by_leg={
            "A": reference("A", closes[0]),
            "B": reference("B", closes[1]),
        },
    )


def test_01_both_negative_is_pc_and_ic() -> None:
    row = scored((40, 45), (42, 48))
    assert row["C"] and row["PC"] and row["IC"]


def test_02_positive_leg_financed_by_negative_sibling_is_pc_not_ic() -> None:
    row = scored((60, 40), (55, 47))
    assert row["individual_deltas_cents"] == [5, -7]
    assert row["PC"] is True and row["IC"] is False


def test_03_combined_delta_exactly_zero_is_not_pc() -> None:
    row = scored((50, 50), (49, 51))
    assert row["combined_delta_cents"] == 0 and row["PC"] is False


def test_04_combined_cost_99_is_s() -> None:
    assert scored((49, 50), (50, 51))["S"] is True


def test_05_combined_cost_100_is_not_s() -> None:
    assert scored((50, 50), (51, 51))["S"] is False


def test_06_s_can_be_true_while_pc_false() -> None:
    row = scored((49, 50), (48, 49))
    assert row["S"] is True and row["PC"] is False


def test_07_pc_can_be_true_while_s_false() -> None:
    row = scored((60, 50), (70, 51))
    assert row["PC"] is True and row["S"] is False


def test_08_missing_reference_keeps_c_but_blocks_pc_and_ic() -> None:
    row = scored((40, 45), (42, None))
    assert row["C"] is True
    assert row["PC"] is False and row["IC"] is False
    assert row["classification"] == "completed_reference_missing"


def test_09_missing_fill_is_naked_single_and_not_c() -> None:
    row = scored((40, 45), (42, 48), fill_legs=("A",))
    assert row["C"] is False and row["classification"] == "naked_single"


def test_10_guarded_strict_ask_credits_exactly_five_at_x() -> None:
    fill = adapted([
        fill_row("A", evidence_type="STRICT_ASK_CERTAIN_FILL", target=61)
    ])["A"]
    assert fill.accounting_quantity == 5
    assert fill.accounting_fill_price_cents == 61


def test_11_guarded_print_credits_regardless_of_subfive_size() -> None:
    fill = adapted([fill_row("A", target=52)])["A"]
    assert fill.accounting_quantity == 5
    assert fill.evidence_type == "PRICE_REACHED"


def test_12_exact_ask_touch_does_not_credit() -> None:
    row = fill_row("A", evidence_type="STRICT_ASK_CERTAIN_FILL")
    row.update({
        "FILLABLE_AT_X": False,
        "FILLABLE_AT_X_evidence_type": None,
        "FILLABLE_AT_X_evidence": None,
        "STRICT_ASK_CERTAIN_FILL": False,
        "EXACT_TOUCH": True,
        "primary_price_fillability_assigns_five": False,
        "accounting_quantity_if_later_scored": 0,
        "accounting_fill_price_if_later_scored": None,
    })
    assert adapted([row]) == {}


def test_13_after_right_strict_ask_is_rejected() -> None:
    row = fill_row(
        "A", evidence_type="STRICT_ASK_CERTAIN_FILL",
        evidence_ts=19_941.0,
    )
    with pytest.raises(GuardedFillError, match="after evaluated right"):
        adapted([row])


def test_14_boundary_unprovable_strict_ask_is_rejected() -> None:
    row = fill_row("A", evidence_type="STRICT_ASK_CERTAIN_FILL")
    row["boundary"]["positive_window1_provable"] = False
    with pytest.raises(GuardedFillError, match="unprovable"):
        adapted([row])


def test_15_raw_causal_fill_state_is_rejected() -> None:
    row = fill_row("A")
    row["causal_policy_fill_state_by_leg"] = {"A": "filled"}
    with pytest.raises(GuardedFillError, match="raw causal-state"):
        adapted([row])


def test_16_duplicate_fill_evidence_cannot_inflate_quantity() -> None:
    with pytest.raises(GuardedFillError, match="multiple eligible intervals"):
        adapt_fillability_rows(
            [fill_row("A"), fill_row("A")],
            expected_candidates=frozenset({CANDIDATE}),
            expected_legs=expected_legs(),
        )


def test_17_holdout_date_fails_closed() -> None:
    row = fill_row("A")
    row["event_date"] = "2026-07-24"
    with pytest.raises(GuardedFillError, match="holdout"):
        adapted([row])


def test_18_d_remains_804_for_censored_events() -> None:
    template = scored((40, 45), (42, 48))
    rows = []
    for index in range(804):
        row = copy.deepcopy(template)
        row["event_id"] = f"fixture-{index:04d}"
        row["classification"] = "censored_boundary"
        row["C"] = row["PC"] = row["S"] = row["IC"] = False
        rows.append(row)
    summary = aggregate_candidate(CANDIDATE, rows)
    assert summary["raw_integers_before_percentages"]["D"] == 804
    assert summary["classification_conservation"]["total"] == 804


def test_19_pc_never_requires_both_individual_deltas_negative() -> None:
    row = scored((60, 40), (55, 47))
    assert row["PC"] and not row["IC"]


def test_20_pc_never_aliases_s() -> None:
    left = scored((60, 50), (70, 51))
    right = scored((49, 50), (48, 49))
    assert (left["PC"], left["S"]) == (True, False)
    assert (right["PC"], right["S"]) == (False, True)


def test_reference_adapter_uses_t8_floor_and_guarded_cutoff() -> None:
    value = derive_window1_close_reference(
        event=EVENT,
        leg=EVENT["legs"][0],
        boundary=boundary(),
        true_prints=[
            {"trade_id": "too-early", "ts": -9_000, "price": 10, "size": 1},
            {"trade_id": "valid", "ts": 19_930, "price": 44, "size": 1},
            {"trade_id": "future", "ts": 19_950, "price": 99, "size": 1},
        ],
    )
    assert value.window1_close_cents == 44
    assert value.reference_receipt == "valid"


def test_reference_adapter_never_uses_schedule_as_close() -> None:
    value = derive_window1_close_reference(
        event=EVENT,
        leg=EVENT["legs"][0],
        boundary=boundary(),
        true_prints=[],
    )
    assert value.available is False
    assert value.window1_close_cents is None
