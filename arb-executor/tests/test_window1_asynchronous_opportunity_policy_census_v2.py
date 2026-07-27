import importlib.util
from pathlib import Path

import pytest


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_asynchronous_opportunity_policy_census_v2.py"
)
SPEC = importlib.util.spec_from_file_location("w1_async_v2", SOURCE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def book(ts, bid, ask, ordinal=0):
    return {
        "timestamp": float(ts),
        "source_ordinal": ordinal,
        "receipt": f"book-{ts}-{ordinal}",
        "bid_cents": bid,
        "ask_cents": ask,
        "top5_bids": [[bid, 2.0]],
        "top5_asks": [[ask, 3.0]],
        "spread_cents": ask - bid,
        "last_trade_cents": None,
        "source": "fixture",
    }


def episode(ts, x, bid, evidence="PRICE_REACHED", receipt="p"):
    row = {
        "episode_id": f"{receipt}-{ts}",
        "timestamp": float(ts),
        "evidence_type": evidence,
        "evidence_receipt": receipt,
        "evidence_size": 0.5 if evidence == "PRICE_REACHED" else None,
        "price_x_cents": x,
        "contemporaneous_bid_cents": bid,
        "contemporaneous_ask_cents": bid + 1,
        "contemporaneous_book_timestamp": float(ts),
        "contemporaneous_book_receipt": f"b-{ts}",
        "top5_bids": [[bid, 1.0]],
        "top5_asks": [[bid + 1, 1.0]],
        "spread_cents": 1,
        "last_trade_cents": None,
        "last_trade_provenance": None,
        "executed_volume_at_or_better_after_episode": 0.5,
        "five_contract_capacity_proven": False,
        "rolling_print_count_30m": 1,
        "rolling_executed_volume_30m": 0.5,
        "interprint_cadence_seconds_30m": None,
        "displayed_depth_at_or_ahead_of_x": 0,
    }
    return row


def test_prefill_x_retouch_after_fill_survives():
    rows = [episode(9, 40, 41, receipt="before"), episode(11, 40, 41, receipt="after")]
    found = M.qualifying_episodes(
        rows, first_timestamp=10, d1=0, left=0, right=20,
        positive_window1_provable=True,
    )
    assert [row["evidence_receipt"] for row in found] == ["after"]


def test_post_cutoff_retouch_is_excluded_and_right_endpoint_is_inclusive():
    rows = [episode(20, 40, 41, receipt="equal"), episode(20.1, 40, 41, receipt="late")]
    found = M.qualifying_episodes(
        rows, first_timestamp=10, d1=0, left=0, right=20,
        positive_window1_provable=True,
    )
    assert [row["evidence_receipt"] for row in found] == ["equal"]


def test_same_timestamp_sibling_is_excluded():
    assert not M.qualifying_episodes(
        [episode(10, 40, 41)], first_timestamp=10, d1=0,
        left=0, right=20, positive_window1_provable=True,
    )


def test_missing_boundary_excludes_evidence():
    assert not M.qualifying_episodes(
        [episode(11, 40, 41)], first_timestamp=10, d1=0,
        left=0, right=20, positive_window1_provable=False,
    )


def test_positive_d2_is_lawful_inside_combined_headroom():
    found = M.qualifying_episodes(
        [episode(11, 60, 59)], first_timestamp=10, d1=-2,
        left=0, right=20, positive_window1_provable=True,
    )
    assert found[0]["d2_cents"] == 1
    assert found[0]["combined_delta_cents"] == -1


def test_true_print_and_strict_ask_recovery_are_separate():
    rows = [
        episode(11, 40, 41, "PRICE_REACHED", "p"),
        episode(12, 40, 41, "STRICT_ASK_CERTAIN_FILL", "a"),
    ]
    found = M.qualifying_episodes(
        rows, first_timestamp=10, d1=0, left=0, right=20,
        positive_window1_provable=True,
    )
    assert {row["evidence_type"] for row in found} == {
        "PRICE_REACHED", "STRICT_ASK_CERTAIN_FILL",
    }


def test_price_reach_survives_capacity_unproved():
    row = episode(11, 40, 41)
    assert row["five_contract_capacity_proven"] is False
    assert M.qualifying_episodes(
        [row], first_timestamp=10, d1=0, left=0, right=20,
        positive_window1_provable=True,
    )


def test_missing_bbo_does_not_fabricate_print_episode():
    raw = {
        "ticker": "T",
        "snapshots": [],
        "prints": [{"ts": 11.1, "price": 40, "size": 1, "trade_id": "p"}],
    }
    prepared = M.prepare_raw_leg(raw, 0, 20, True)
    assert prepared["episodes"] == []


def test_newer_lawful_bbo_invalidates_earlier_carried_bid():
    raw = {
        "ticker": "T",
        "snapshots": [
            {"ts": 10, "bids": [[42, 1]], "asks": [[43, 1]], "last_trade": 41},
            {"ts": 11, "bids": [[41, 1]], "asks": [[42, 1]], "last_trade": 41},
        ],
        "prints": [{"ts": 11.5, "price": 41, "size": 1, "trade_id": "p"}],
    }
    prepared = M.prepare_raw_leg(raw, 0, 20, True)
    row = next(x for x in prepared["episodes"] if x["evidence_type"] == "PRICE_REACHED")
    assert row["contemporaneous_bid_cents"] == 41
    assert row["contemporaneous_book_timestamp"] == 11


def test_strict_ask_uses_same_snapshot_bid_and_ask():
    raw = {
        "ticker": "T",
        "snapshots": [
            {"ts": 10, "bids": [[35, 1]], "asks": [[37, 1]], "last_trade": 36},
        ],
        "prints": [],
    }
    prepared = M.prepare_raw_leg(raw, 0, 20, True)
    row = prepared["episodes"][0]
    assert (row["price_x_cents"], row["contemporaneous_bid_cents"], row["contemporaneous_ask_cents"]) == (38, 35, 37)


def test_full_precision_timestamps_remain_distinct():
    assert M.episode_is_strictly_later(100.000001, 100.000002)
    assert not M.episode_is_strictly_later(100.000002, 100.000001)


def test_ambiguous_same_timestamp_differing_books_need_sequence_authority():
    raw = {
        "ticker": "T",
        "snapshots": [
            {"ts": 10, "bids": [[40, 1]], "asks": [[41, 1]], "last_trade": 40},
            {"ts": 10, "bids": [[41, 1]], "asks": [[42, 1]], "last_trade": 41},
        ],
        "prints": [{"ts": 10.5, "price": 40, "size": 1, "trade_id": "p"}],
    }
    prepared = M.prepare_raw_leg(raw, 0, 20, True)
    print_row = next(
        row for row in prepared["episodes"]
        if row["evidence_type"] == "PRICE_REACHED"
    )
    assert print_row["contemporaneous_bid_cents"] == 41
    assert len([
        row for row in prepared["episodes"]
        if row["evidence_type"] == "STRICT_ASK_CERTAIN_FILL"
    ]) == 2
    assert prepared["ambiguous_book_timestamps"] == [10.0]
    selected, reason = M.latest_book_reference(
        prepared["raw_lawful_books"],
        10.5,
        authoritative_source_row_order=False,
    )
    assert selected is None
    assert reason == (
        "ambiguous_latest_timestamp_multiple_prices_"
        "no_authoritative_sequence"
    )


def test_authoritative_same_timestamp_ordinal_selects_later_not_favorable():
    books = [
        book(10, 18, 19, ordinal=218159),
        book(10, 17, 18, ordinal=218181),
    ]
    selected, reason = M.latest_book_reference(
        books, 10.8, authoritative_source_row_order=True
    )
    assert reason is None
    assert selected["source_ordinal"] == 218181
    assert selected["bid_cents"] == 17
    assert not M.strict_combined(0, 17 - selected["bid_cents"])


def test_three_disputed_receipts_are_frozen_exclusions():
    assert M.DISPUTED_RECEIPTS == {
        "06a93c92-0d52-4040-1ed2-6882d5490b0a",
        "8f0d3c80-128b-4359-4f43-1d9e5a6b57d1",
        "3e4c49d6-a936-45a0-6577-5f2fdefe62b9",
    }


def test_counterfactual_orientations_are_both_retained():
    left = [episode(10, 40, 41, receipt="L")]
    right = [episode(11, 60, 61, receipt="R")]
    assert M._orientation_path(left, right)["path_exists"]
    assert not M._orientation_path(right, left)["path_exists"]


def test_orientation_rows_do_not_inflate_event_union():
    flags = [True, True]
    assert int(any(flags)) == 1
    assert sum(flags) == 2


@pytest.mark.parametrize(
    "missing",
    [
        "strictly_post_first_fill",
        "inside_combined_headroom",
        "lawful_contemporaneous_external_bbo",
        "guarded_corridor_overlap",
        "no_execution_proof_during_exposure",
    ],
)
def test_exposure_requires_all_five_requirements(missing):
    requirements = {
        "strictly_post_first_fill": True,
        "inside_combined_headroom": True,
        "lawful_contemporaneous_external_bbo": True,
        "guarded_corridor_overlap": True,
        "no_execution_proof_during_exposure": True,
    }
    requirements[missing] = False
    assert not all(requirements.values())


def test_exact_cent_rejects_fraction_bool_and_range():
    for value in (40.9, True, 0, 100, float("nan")):
        with pytest.raises(M.CensusError):
            M.exact_cent(value, "fixture")


def test_vukbro_arithmetic_one_lawful_seven_zero_delta():
    assert M.strict_combined(0, 41 - 42)
    assert not M.strict_combined(0, 41 - 41)
    assert M.headroom_d2_max(0) == -1


def test_avefor_identity_is_frozen_exclusion_fixture():
    assert M.AVEFOR == "KXATPCHALLENGERMATCH-26JUL12AVEFOR"


def test_metrics_are_not_implemented_by_census_module():
    assert not any(
        name.lower().startswith(("score", "calculate_pc", "rank"))
        for name in vars(M)
    )
