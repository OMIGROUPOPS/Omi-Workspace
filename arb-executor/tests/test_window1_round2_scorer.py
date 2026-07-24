from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_scorer as scorer  # noqa: E402


CANDIDATE = "r2_async_pair__park_join__hold"


def event_fixture(
    *,
    event_id: str = "FIXTURE-SCORE",
    event_date: str = "2026-07-12",
    ticker_prefix: str = "FIXTURE",
) -> dict:
    return {
        "event_id": event_id,
        "event_date": event_date,
        "legs": [
            {"leg_id": "A", "ticker": f"{ticker_prefix}-A"},
            {"leg_id": "B", "ticker": f"{ticker_prefix}-B"},
        ],
    }


def official_boundary(
    event_id: str = "FIXTURE-SCORE",
    exact_start: float = 1700.0,
) -> dict:
    return {
        "schema_version": "window1-real-start-ledger-v5-guarded",
        "event_id": event_id,
        "start_source_class": "official_exact",
        "selected_source": "fixture_official_provider",
        "selected_source_family": "exact_official_provider_match_start",
        "positive_window1_provable": True,
        "exact_start_utc": exact_start,
        "guard_band": {
            "guard_id": "official-point-strict-60s-v1",
            "positive_guard_seconds": 60,
            "negative_guard_seconds": 60,
        },
    }


def proxy_boundary(
    event_id: str = "FIXTURE-SCORE",
    proxy_clock: float = 2500.0,
) -> dict:
    return {
        "schema_version": "window1-real-start-ledger-v5-guarded",
        "event_id": event_id,
        "start_source_class": "quantized_late_detection_proxy",
        "selected_source": "fixture_quantized_proxy",
        "selected_source_family": "tennis_db_start_or_live_score",
        "positive_window1_provable": True,
        "proxy_clock_utc": proxy_clock,
        "guard_band": {
            "guard_id": "te-calibration-central-93pct-asymmetric-v1",
            "positive_guard_seconds": 900,
            "negative_guard_seconds": 600,
            "strict_window1_completion_lte_utc": proxy_clock - 900,
        },
    }


def fill(
    leg_id: str,
    ticker: str,
    timestamp: float,
    price: float,
    *,
    quantity: float = 5.0,
    receipt_id: str | None = None,
) -> tuple[dict, dict]:
    identity = receipt_id or f"PRINT-{leg_id}"
    action = {
        "event_id": "FIXTURE-SCORE",
        "candidate_id": CANDIDATE,
        "leg_id": leg_id,
        "ticker": ticker,
        "ts": timestamp,
        "action": "fill_observed",
        "reason": "public_nonself_true_print",
        "order_price_cents": price,
        "print_price_cents": price,
        "fill_quantity": quantity,
        "cumulative_quantity": quantity,
        "complete": quantity >= 5,
        "trade_id": identity,
    }
    evidence = {
        "event_id": "FIXTURE-SCORE",
        "ticker": ticker,
        "ts": timestamp,
        "price": price,
        "size": quantity,
        "trade_id": identity,
        "receipt_id": identity,
        "source": "normalized_public_true_print",
        "size_verified": True,
        "synthetic_transition": False,
    }
    return action, evidence


def policy_fixture(
    event: dict,
    *,
    a_ts: float = 1500,
    b_ts: float = 1500,
    a_price: float = 40,
    b_price: float = 55,
    a_quantity: float = 5,
    b_quantity: float = 5,
) -> tuple[dict, list[dict]]:
    a_action, a_evidence = fill(
        "A", event["legs"][0]["ticker"], a_ts, a_price,
        quantity=a_quantity,
    )
    b_action, b_evidence = fill(
        "B", event["legs"][1]["ticker"], b_ts, b_price,
        quantity=b_quantity,
    )
    for row in (a_action, b_action, a_evidence, b_evidence):
        row["event_id"] = event["event_id"]
    actions = [a_action, b_action]
    actions.sort(key=lambda row: (row["ts"], row["leg_id"]))
    result = {
        "schema_version": "fixture-score-free-stream",
        "instrument_version": "window1-round2-causal-instrument-v3",
        "candidate_id": CANDIDATE,
        "event_id": event["event_id"],
        "event_date": event["event_date"],
        "policy_clock": {
            "policy_activation_ts": 1000.0,
        },
        "evaluation_truth_present": False,
        "event_terminal": "complete_counterfactual_stream",
        "leg_streams": {
            "A": [a_action],
            "B": [b_action],
        },
        "order_stream": actions,
        "scored": False,
        "metrics": None,
        "holdout_queried": False,
        "stream_sha256": scorer.canonical_sha256(actions),
    }
    return result, [a_evidence, b_evidence]


def references(event: dict, a_close: float = 45, b_close: float = 60) -> dict:
    return {
        event["legs"][0]["ticker"]: {
            "available": True,
            "window1_close_cents": a_close,
        },
        event["legs"][1]["ticker"]: {
            "available": True,
            "window1_close_cents": b_close,
        },
    }


def features(**overrides) -> dict:
    value = {
        "censored": False,
        "censor_reasons": [],
        "feature_unavailable": [],
        "cohort_NO_CALL_count": 0,
        "reaim_NO_CALL_count": 0,
    }
    value.update(overrides)
    return value


def scored_event(
    *,
    event: dict | None = None,
    boundary: dict | None = None,
    policy: dict | None = None,
    evidence: list[dict] | None = None,
    refs: dict | None = None,
    feature: dict | None = None,
) -> dict:
    event = event or event_fixture()
    if policy is None or evidence is None:
        policy, evidence = policy_fixture(event)
    return scorer.score_event(
        event,
        policy,
        evidence,
        boundary or official_boundary(event["event_id"]),
        refs or references(event),
        feature or features(),
        CANDIDATE,
    )


def test_exact_dual_five_before_guarded_cutoff_is_C():
    row = scored_event()
    assert row["classification"] == "exact_five"
    assert row["C"] is True
    assert row["PC"] is True
    assert row["S"] is True
    assert row["IC"] is True


def test_one_leg_after_guarded_cutoff_is_not_C():
    event = event_fixture()
    policy, evidence = policy_fixture(event, b_ts=1650)
    row = scored_event(event=event, policy=policy, evidence=evidence)
    assert row["C"] is False
    assert row["classification"] == "naked_single_leg"


def test_official_and_proxy_use_their_frozen_guards():
    official = scorer.strict_cutoff(official_boundary())
    proxy = scorer.strict_cutoff(proxy_boundary())
    assert official["boundary_timestamp"] == 1640
    assert official["guard_seconds"] == 60
    assert proxy["boundary_timestamp"] == 1600
    assert proxy["guard_seconds"] == 900
    assert proxy["direction"] == "anchor_minus_positive_guard"


def test_raw_realized_start_cannot_bypass_guarded_cutoff():
    boundary = official_boundary()
    boundary["evaluation_real_start_ts"] = 9999
    with pytest.raises(scorer.ScoringError, match="raw realized"):
        scored_event(boundary=boundary)


def test_schedule_only_row_cannot_become_positive():
    boundary = {
        "schema_version": "window1-real-start-ledger-v5-guarded",
        "event_id": "FIXTURE-SCORE",
        "start_source_class": "schedule_only",
        "selected_source": "exchange_schedule",
        "selected_source_family": "schedule",
        "schedule_source": "timestamped_exchange_catalog",
        "positive_window1_provable": False,
        "exact_start_utc": 9999,
    }
    row = scored_event(boundary=boundary)
    assert row["classification"] == "censored"
    assert row["C"] is False


def test_exact_combined_delta_zero_is_not_PC():
    event = event_fixture()
    row = scored_event(
        event=event, refs=references(event, 40, 55)
    )
    assert row["combined_window1_close_delta_cents"] == 0
    assert row["PC"] is False


def test_combined_cost_exactly_100_is_not_S():
    event = event_fixture()
    policy, evidence = policy_fixture(
        event, a_price=45, b_price=55
    )
    row = scored_event(
        event=event, policy=policy, evidence=evidence,
        refs=references(event, 50, 60),
    )
    assert row["combined_entry_cost_cents"] == 100
    assert row["S"] is False


def test_one_individual_delta_zero_is_not_IC():
    event = event_fixture()
    row = scored_event(
        event=event, refs=references(event, 40, 60)
    )
    assert row["individual_leg_window1_close_delta_cents"] == [0, -5]
    assert row["IC"] is False


@pytest.mark.parametrize(
    ("a_quantity", "b_quantity", "expected"),
    [(2, 5, "partial"), (6, 5, "other_quantity")],
)
def test_partial_or_other_quantity_is_not_C(
    a_quantity, b_quantity, expected,
):
    event = event_fixture()
    policy, evidence = policy_fixture(
        event, a_quantity=a_quantity, b_quantity=b_quantity
    )
    row = scored_event(
        event=event, policy=policy, evidence=evidence
    )
    assert row["classification"] == expected
    assert row["C"] is False


def test_naked_single_stays_separately_classified():
    event = event_fixture()
    policy, evidence = policy_fixture(event)
    policy["order_stream"] = [policy["order_stream"][0]]
    policy["leg_streams"]["B"] = []
    policy["stream_sha256"] = scorer.canonical_sha256(
        policy["order_stream"]
    )
    row = scored_event(
        event=event, policy=policy, evidence=[evidence[0]]
    )
    assert row["classification"] == "naked_single_leg"
    assert row["C"] is False


def test_NO_CALL_continues_and_is_not_nonfill_or_censor():
    row = scored_event(feature=features(cohort_NO_CALL_count=2))
    assert row["classification"] == "exact_five"
    assert row["C"] is True
    assert row["cohort_NO_CALL_count"] == 2


def test_missing_feature_remains_censored_unavailable():
    row = scored_event(feature=features(
        censored=True,
        censor_reasons=["top5"],
        feature_unavailable=["top5"],
    ))
    assert row["classification"] == "censored"
    assert row["C"] is False
    assert "top5" in row["feature_unavailable"]


def test_duplicate_receipt_cannot_inflate_quantity():
    event = event_fixture()
    policy, evidence = policy_fixture(event)
    duplicate = copy.deepcopy(policy["order_stream"][0])
    duplicate["fill_quantity"] = 1
    policy["order_stream"].append(duplicate)
    policy["leg_streams"]["A"].append(duplicate)
    policy["stream_sha256"] = scorer.canonical_sha256(
        policy["order_stream"]
    )
    with pytest.raises(scorer.ScoringError, match="duplicate fill"):
        scored_event(event=event, policy=policy, evidence=evidence)


def frozen_contract() -> dict:
    source_receipts = {
        name: f"frozen-{name}" for name in scorer.SECTION_NAMES
    }
    return {
        "schema_version": "window1-round2-scorer-contract-v1",
        "scorer_version": scorer.VERSION,
        "D": 804,
        "target_PC": 603,
        "lot_per_leg": 5,
        "development_dates": scorer.DEVELOPMENT_DATES,
        "sealed_holdout_dates": scorer.SEALED_HOLDOUT_DATES,
        "candidate_ids": [CANDIDATE],
        "metric_definitions": {
            "C": "fixture-bound exact law",
            "PC": "fixture-bound strict law",
            "S": "fixture-bound strict law",
            "IC": "fixture-bound strict law",
        },
        "freeze_lineage": {
            "instrument": "frozen-instrument",
            "candidate_spec": "frozen-candidates",
            "metric_contract": "frozen-metrics",
            "data_binding": "frozen-data",
            "scorer_source": "frozen-scorer",
        },
        "frozen_source_receipts": source_receipts,
    }


def population_bundle() -> tuple[dict, dict]:
    contract = frozen_contract()
    ledger = []
    streams = {}
    evidence = {}
    boundaries = {}
    refs = {}
    feature_rows = {}
    for index in range(804):
        event_id = f"FIXTURE-E{index:03d}"
        date = scorer.DEVELOPMENT_DATES[
            index % len(scorer.DEVELOPMENT_DATES)
        ]
        event = event_fixture(
            event_id=event_id,
            event_date=date,
            ticker_prefix=f"FIXTURE-{index:03d}",
        )
        ledger.append(event)
        order_stream: list[dict] = []
        streams[event_id] = {
            "candidate_id": CANDIDATE,
            "event_id": event_id,
            "event_date": date,
            "policy_clock": {"policy_activation_ts": 1000},
            "evaluation_truth_present": False,
            "leg_streams": {"A": [], "B": []},
            "order_stream": order_stream,
            "scored": False,
            "metrics": None,
            "holdout_queried": False,
            "stream_sha256": scorer.canonical_sha256(order_stream),
        }
        evidence[event_id] = []
        boundaries[event_id] = official_boundary(event_id, 2000)
        refs[event_id] = {}
        feature_rows[event_id] = features()
    sections = {
        "event_ledger": ledger,
        "candidate_order_streams": streams,
        "fill_evidence": evidence,
        "start_boundaries": boundaries,
        "references": refs,
        "feature_classifications": feature_rows,
        "data_binding_manifest": {
            "D": 804,
            "leg_identities": 1608,
            "binding_bundle_sha256": contract[
                "freeze_lineage"
            ]["data_binding"],
            "holdout_dates_present_in_any_input": 0,
            "holdout_queried": False,
        },
    }
    identities = sorted(
        (
            {
                "event_id": event["event_id"],
                "event_date": event["event_date"],
                "leg_id": scorer._leg_identity(leg),
                "ticker": leg["ticker"],
            }
            for event in ledger for leg in event["legs"]
        ),
        key=lambda row: (
            row["event_id"], row["leg_id"], row["ticker"]
        ),
    )
    candidate_stream_receipts = {
        CANDIDATE: {
            event_id: row["stream_sha256"]
            for event_id, row in streams.items()
        }
    }
    contract["frozen_event_leg_identities"] = identities
    contract["frozen_event_leg_identities_sha256"] = (
        scorer.canonical_sha256(identities)
    )
    contract["candidate_stream_receipts"] = (
        candidate_stream_receipts
    )
    contract["candidate_stream_receipts_sha256"] = (
        scorer.canonical_sha256(candidate_stream_receipts)
    )
    receipts = {
        name: {
            "canonical_sha256": scorer.canonical_sha256(value),
            "source_sha256": contract["frozen_source_receipts"][name],
        }
        for name, value in sections.items()
    }
    return {
        "candidate_id": CANDIDATE,
        "freeze_lineage": copy.deepcopy(contract["freeze_lineage"]),
        "source_receipts": copy.deepcopy(
            contract["frozen_source_receipts"]
        ),
        "sections": sections,
        "section_receipts": receipts,
    }, contract


def test_changed_input_hash_hard_fails():
    bundle, contract = population_bundle()
    bundle["sections"]["feature_classifications"][
        "FIXTURE-E000"
    ]["cohort_NO_CALL_count"] = 1
    with pytest.raises(scorer.ScoringError, match="changed input hash"):
        scorer.score_population(bundle, contract)


def test_changed_candidate_stream_outside_frozen_receipt_hard_fails():
    bundle, contract = population_bundle()
    stream = bundle["sections"]["candidate_order_streams"][
        "FIXTURE-E000"
    ]
    stream["order_stream"].append({
        "event_id": "FIXTURE-E000",
        "leg_id": "A",
        "ticker": "FIXTURE-000-A",
        "ts": 1001,
        "action": "sibling_hold",
        "reason": "fixture_mutation",
    })
    stream["stream_sha256"] = scorer.canonical_sha256(
        stream["order_stream"]
    )
    section = bundle["sections"]["candidate_order_streams"]
    bundle["section_receipts"]["candidate_order_streams"][
        "canonical_sha256"
    ] = scorer.canonical_sha256(section)
    with pytest.raises(
        scorer.ScoringError, match="outside frozen receipts"
    ):
        scorer.score_population(bundle, contract)


@pytest.mark.parametrize("date", ["2026-07-24", "2026-07-23"])
def test_holdout_or_nondevelopment_date_hard_fails(date):
    event = event_fixture(event_date=date)
    policy, evidence = policy_fixture(event)
    with pytest.raises(
        scorer.ScoringError, match="holdout|non-development"
    ):
        scored_event(event=event, policy=policy, evidence=evidence)


def test_metric_totals_conserve_to_D804():
    bundle, contract = population_bundle()
    result = scorer.score_population(bundle, contract)
    raw = result["raw_integer_metrics_before_percentages"]
    census = [
        raw[name] for name in (
            "exact_five",
            "partial",
            "other_quantity",
            "genuine_nonfill",
            "naked_single_leg",
            "zero_length_window",
            "contradictory",
            "censored",
        )
    ]
    assert sum(census) == 804
    assert raw["D"] == 804
    assert raw["genuine_nonfill"] == 804
    assert result["census_conserves_to_D"] is True


def test_scorer_is_byte_identical_on_same_synthetic_contract():
    bundle, contract = population_bundle()
    first = scorer.score_population(bundle, contract)
    second = scorer.score_population(
        copy.deepcopy(bundle), copy.deepcopy(contract)
    )
    assert json.dumps(first, sort_keys=True) == json.dumps(
        second, sort_keys=True
    )
    assert first["result_sha256"] == second["result_sha256"]
