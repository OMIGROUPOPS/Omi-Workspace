from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_os_family_search as search  # noqa: E402


def configure_surfaces():
    search._SURFACES = {
        "band_map": {
            "cats": {
                "ATP_MAIN": {
                    "bands": [
                        {
                            "band": "ATP_MAIN-B1",
                            "direction": "flat",
                            "anchor_med": 25,
                        },
                        {
                            "band": "ATP_MAIN-B2",
                            "direction": "flat",
                            "anchor_med": 75,
                        },
                    ]
                }
            }
        },
        "divot": {
            "bands": {
                "ATP_MAIN-B1": {
                    "depth_p50": 3,
                    "depth_p90": 7,
                }
            }
        },
        "sealed": {
            "bands": {
                "ATP_MAIN-B1": {
                    "status": "SEALED",
                    "depth": 5,
                }
            }
        },
        "drift": {"recognition": {}},
        "cohort": {"rows": []},
        "orient": {"cats": {}},
        "recut": {"ATP_MAIN": {"25": {"edge_p50": 4}}},
        "atlas": {"pages": {}},
        "reach": {"law": {}},
        "allowed_features": [],
    }


def test_default_band_and_surface_depths_are_deterministic():
    configure_surfaces()
    assert search.default_flat_band("ATP_MAIN", 24) == "ATP_MAIN-B1"
    assert search.divot_depth("ATP_MAIN-B1", "p50") == 3
    assert search.divot_depth("ATP_MAIN-B1", "p90") == 7
    assert search.sealed_depth("ATP_MAIN-B1") == 5
    assert search.recut_depth("ATP_MAIN", 25) == 4


def test_family_price_uses_own_divot_and_never_falls_back_to_touch():
    configure_surfaces()
    policy = {
        "os_family": "pair_divot_core",
        "ablations": [],
    }
    feature = {
        "_os": {
            "depths": {
                "divot_core": 3,
                "sealed_band": 5,
            }
        }
    }
    snapshot = {"best_bid": 40, "best_ask": 43}
    assert search.family_price(
        policy, {}, feature, snapshot
    ) == 35
    feature["_os"]["depths"] = {}
    assert search.family_price(
        policy, {}, feature, snapshot
    ) is None


def test_pressure_feature_is_disabled_without_causal_coverage():
    configure_surfaces()
    policy = {
        "os_family": "causal_micro_pressure",
        "ablations": [],
    }
    snapshot = {"best_bid": 40, "best_ask": 43}
    feature = {
        "_os": {
            "depths": {"divot_core": 3},
            "pressure_ratio": None,
        }
    }
    assert search.family_price(
        policy, {}, feature, snapshot
    ) == 37
    feature["_os"]["pressure_ratio"] = 2.0
    assert search.family_price(
        policy, {}, feature, snapshot
    ) == 36
    policy["ablations"] = ["without_top_five_pressure"]
    assert search.family_price(
        policy, {}, feature, snapshot
    ) == 37


def test_candidate_allowlist_expands_to_exact_24_in_declared_order():
    spec = {
        "permitted_policy_ids": [
            f"{family}__{posture}__{response}"
            for family in (
                "pair_divot_core",
                "drift_cohort_orientation",
                "mirror_deceleration",
                "dynamic_recut_atlas",
                "causal_micro_pressure",
                "full_chronological_stack",
            )
            for posture in ("park", "walk")
            for response in ("hold", "reaim")
        ]
    }
    policies = search.candidate_policies(spec)
    assert len(policies) == 24
    assert policies[0]["policy_id"] == "pair_divot_core__park__hold"
    assert policies[-1]["policy_id"] == (
        "full_chronological_stack__walk__reaim"
    )
    assert sum(
        policy["placement_rule"] == "walk_law"
        for policy in policies
    ) == 12


def test_metric_names_follow_corrected_contract():
    policy = {
        "policy_id": "p",
        "os_family": "pair_divot_core",
        "posture": "park",
        "first_fill_sibling_response_id": "hold",
        "ablations": [],
    }
    base = {
        "policy_id": "p",
        "event_date": "2026-07-12",
        "tournament_class": "ATP_MAIN",
        "start_source_class": "official_exact",
        "feature_coverage_class": "available_1_of_16",
        "strict_positive_cutoff_utc": "2026-07-12T12:00:00+00:00",
        "classification": "nonfill",
        "C": False,
        "PC": False,
        "S": False,
        "IC": False,
        "combined_entry_cost_cents": None,
        "combined_window1_close_delta_cents": None,
        "optimistic_queue_complete": False,
        "available_feature_family_count": 1,
        "legs": [],
    }
    rows = [dict(base) for _ in range(804)]
    summary = search.summarize_candidate(policy, rows)
    assert summary["raw"]["D"] == 804
    assert summary["raw"]["PC"] == 0
    assert summary["raw"]["S"] == 0
    assert summary["raw"]["nonfill"] == 804
    assert summary["distance_from_target"]["raw_shortfall"] == 603
