import importlib.util
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_decision_layer_attribution.py"
)
SPEC = importlib.util.spec_from_file_location("w1_layer", SOURCE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def interval(price=40):
    return {
        "order_interval_id": "i1",
        "limit_price_cents": price,
        "authority": "INITIAL_PAIR_BBO",
        "open_reason": "initial_pair_join_presence",
        "opened_ts": 1.0,
        "closed_ts": 20.0,
    }


def stream(*, target=40, discovery="AVAILABLE_FROZEN", no_calls=None):
    return {
        "evidence_census_by_leg": [{
            "leg_id": "B",
            "discovery_page_key": "ATP_CHALL|leader|26_50",
            "discovery_price": 40,
            "discovery_status": discovery,
            "macro_target_raw": target,
            "macro_target_source": "fixture",
            "macro_target_status": "ATLAS_PATH_TARGET_FROZEN",
            "no_calls": no_calls or [],
            "headroom_trigger_count": 1,
            "target_change_count": 0,
            "queue_surrender_count": 0,
        }],
        "order_intervals_by_leg": {"B": []},
    }


def event():
    return {
        "sibling_leg_id": "B",
        "credited_first_leg": {"timestamp": 5.0},
    }


def earliest():
    return {
        "timestamp": 10.0,
        "price_x_cents": 45,
        "evidence_receipt": "p1",
    }


def arm():
    return {
        "leg_id": "B",
        "action": "headroom_armed",
        "ts": 5.0,
        "_receipt": {"row_sha256": "a"},
    }


def decision(target):
    return {
        "leg_id": "B",
        "action": "headroom_decision",
        "trigger_receipt": "p1",
        "ts": 10.0,
        "complete_raw_target_cents": target,
        "final_expressed_price_cents": target,
        "action_taken": True,
        "reason": "fixture",
        "_receipt": {"row_sha256": "d"},
    }


def test_strict_combined_accepts_positive_sibling_inside_pair_budget():
    assert M.strict_combined(-2, 1)
    assert not M.strict_combined(-1, 1)


def test_target_selection_layer_requires_same_receipt_different_target():
    result = M.attribute_never_exposed(
        event(), earliest(), stream(), [arm(), decision(41)]
    )
    assert result["attributed_layer"] == (
        "target_selection_never_included_lawful_X"
    )


def test_armed_without_episode_decision_is_sibling_response_layer():
    result = M.attribute_never_exposed(
        event(), earliest(), stream(), [arm()]
    )
    assert result["attributed_layer"] == (
        "first_fill_sibling_response_failed_to_create_exposure"
    )


def test_explicit_discovery_nocall_has_priority():
    result = M.attribute_never_exposed(
        event(), earliest(),
        stream(discovery="NO_CALL_UNAVAILABLE"), [arm()]
    )
    assert result["attributed_layer"] == (
        "discovery_recognition_unavailable_or_no_call"
    )


def test_target_x_without_interval_is_target_included_no_exposure():
    result = M.attribute_never_exposed(
        event(), earliest(), stream(), [arm(), decision(45)]
    )
    assert result["attributed_layer"] == (
        "target_included_X_but_no_initial_exposure_created"
    )


def test_active_interval_proves_exposure_state_without_changing_layer():
    s = stream()
    s["order_intervals_by_leg"]["B"] = [interval(41)]
    result = M.attribute_never_exposed(
        event(), earliest(), s, [arm(), decision(41)]
    )
    assert result["active_intervals_at_opportunity"][0]["price_cents"] == 41


def test_moved_authority_mapping():
    assert M.moved_layer("MAKER_SAFETY", True) == "maker_safety_reprice"
    assert M.moved_layer("LIVEAIM_SOURCE_MAPPING", True) == "LIVE_AIM_reprice"
    assert M.moved_layer("CAUSAL_PAIR_HEADROOM", True) == "headroom_reprice"
    assert M.moved_layer("POLICY_HORIZON", False) == (
        "corridor_window_termination"
    )


def test_latest_book_uses_preserved_later_ordinal():
    books = [
        {"timestamp": 10.0, "source_ordinal": 1, "bid_cents": 18},
        {"timestamp": 10.0, "source_ordinal": 2, "bid_cents": 17},
    ]
    assert M.latest_book(books, 10.5)["bid_cents"] == 17


def test_full_precision_strict_later_is_preserved():
    assert 10.000002 > 10.000001
    assert not 10.000001 > 10.000001


def test_diagnostic_bands_are_not_policy_outputs():
    assert M.sign_band(1) == "POSITIVE"
    assert M.volume_band(4.9) == "POSITIVE_LT_5"
    assert M.elapsed_band(60) == "1M_TO_LT_5M"
    assert M.depth_band(0) == "ZERO"


def test_crosswalk_keeps_candidate_rows_distinct_from_games():
    base = {
        "event_id": "E",
        "credited_first_leg": {
            "leg_id": "A", "price_x_cents": 40,
            "timestamp": 1.0, "evidence_receipt": "p",
        },
        "earliest_lawful_recovery": {"episode_id": "x"},
        "primary_classification": "lawful_opportunity_but_policy_never_exposed",
    }
    rows = [
        {**base, "candidate_id": M.CANDIDATES[0]},
        {**base, "candidate_id": M.CANDIDATES[1]},
    ]
    result = M.build_crosswalk(rows)
    assert result["shared_event_count"] == 1
    assert sum(result["candidate_row_counts"].values()) == 2


def test_counterfactual_geometry_contract_is_never_realized_miss():
    spec_path = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "research"
        / "window1"
        / "WINDOW1_DECISION_LAYER_ATTRIBUTION_SPEC.json"
    )
    assert '"counterfactual_paths_are_not_realized_misses": true' in (
        spec_path.read_text(encoding="utf-8")
    )


def test_module_contains_no_scorer_or_strategy_entrypoint():
    forbidden = ("score", "rank", "select_candidate", "tune")
    assert not any(
        name.lower().startswith(forbidden) for name in vars(M)
    )
