from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


guard = load(
    "window1_start_guard",
    "arb-executor/analysis/window1_start_guard.py",
)


def test_proxy_is_relabelled_and_earlier_live_by_is_retained():
    row = {
        "event_id": "KXATPMATCH-26JUL12TESTAA",
        "precision_class": "exact",
        "selected_source": guard.TENNIS_EXPLORER_SOURCE,
        "exact_start_utc": "2026-07-12T12:00:00+00:00",
        "candidate_sources": [
            {
                "source": guard.TENNIS_EXPLORER_SOURCE,
                "direction": "exact",
                "timestamp_utc": "2026-07-12T12:00:00+00:00",
                "precedence_rank": 3,
            },
            {
                "source": "causal_live_receipt",
                "direction": "live_by",
                "timestamp_utc": "2026-07-12T11:57:00+00:00",
                "precedence_rank": 4,
            },
        ],
    }
    repaired = guard.repair_v4_row(row)
    assert repaired["precision_class"] == (
        "quantized_late_detection_proxy"
    )
    assert repaired["exact_start_utc"] is None
    assert repaired["proxy_clock_utc"] == (
        "2026-07-12T12:00:00+00:00"
    )
    assert repaired["known_live_by_utc"] == (
        "2026-07-12T11:57:00+00:00"
    )
    assert repaired["one_sided_conflict_law"][
        "proxy_may_never_overwrite_earlier_live_by"
    ] is True


def test_asymmetric_proxy_guard_censors_the_interior():
    row = guard.repair_v4_row({
        "event_id": "KXATPMATCH-26JUL12TESTAA",
        "precision_class": "exact",
        "selected_source": guard.TENNIS_EXPLORER_SOURCE,
        "exact_start_utc": "2026-07-12T12:00:00+00:00",
        "candidate_sources": [],
    })
    clock = guard.parse_utc(row["proxy_clock_utc"])
    assert guard.boundary_verdict(
        row, clock - 900
    )["verdict"] == "strict_window1"
    assert guard.boundary_verdict(
        row, clock - 899
    )["verdict"] == "censored_guard_band"
    assert guard.boundary_verdict(
        row, clock + 599
    )["verdict"] == "censored_guard_band"
    assert guard.boundary_verdict(
        row, clock + 600
    )["verdict"] == "strict_post_start"


def test_named_proxy_conflicts_are_not_positive_capable():
    event_id = sorted(guard.NAMED_PROXY_CENSORS)[0]
    row = guard.repair_v4_row({
        "event_id": event_id,
        "precision_class": "exact",
        "selected_source": guard.TENNIS_EXPLORER_SOURCE,
        "exact_start_utc": "2026-07-15T12:00:00+00:00",
        "candidate_sources": [],
    })
    assert row["positive_window1_provable"] is False
    assert guard.strict_positive_cutoff(row) is None
    assert guard.boundary_verdict(
        row, guard.parse_utc(row["proxy_clock_utc"]) - 3600
    )["verdict"] == "censored_named_proxy_conflict"


def test_official_point_uses_strict_60_second_guard():
    row = {
        "event_id": "KXATPMATCH-26JUL12OFFICIAL",
        "precision_class": "exact",
        "selected_source": "official_milestone",
        "exact_start_utc": "2026-07-12T12:00:00+00:00",
    }
    exact = guard.parse_utc(row["exact_start_utc"])
    assert guard.boundary_verdict(
        row, exact - 60
    )["verdict"] == "strict_window1"
    assert guard.boundary_verdict(
        row, exact - 59
    )["verdict"] == "censored_guard_band"
    assert guard.boundary_verdict(
        row, exact + 60
    )["verdict"] == "strict_post_start"


def test_round2_conflict_law_never_promotes_proxy_to_exact(monkeypatch):
    monkeypatch.syspath_prepend(
        str(ROOT / "arb-executor" / "analysis")
    )
    round2 = load(
        "window1_start_truth_round2",
        "arb-executor/analysis/window1_start_truth_round2.py",
    )
    baseline = {
        "event_id": "KXATPMATCH-26JUL12TESTAA",
        "candidate_sources": [
            {
                "source": "strong_live_by",
                "source_family": "causal",
                "precedence_rank": 2,
                "timestamp_utc": "2026-07-12T11:55:00+00:00",
                "direction": "live_by",
                "precision": "second",
                "timestamp_basis": "exchange",
            },
            {
                "source": "equal_not_live",
                "source_family": "causal",
                "precedence_rank": 3,
                "timestamp_utc": "2026-07-12T12:01:00+00:00",
                "direction": "not_live_through",
                "precision": "second",
                "timestamp_basis": "exchange",
            },
        ],
        "selected_source": "strong_live_by",
        "selected_source_family": "causal",
        "selected_timestamp_precision": "second",
        "interval_contradiction": False,
    }
    crosswalk = {
        "start_utc": "2026-07-12T12:00:00+00:00",
        "selected_te_match_id": "1",
        "event_source_id": "source-event",
        "competitor_source_ids": ["a", "b"],
        "selected_te_page_date": "2026-07-12",
        "milestone_start_date_identity_only": (
            "2026-07-12T10:00:00+00:00"
        ),
        "selected_te_page_sha256": "a" * 64,
    }
    adjudicated, _ = round2.adjudicate_residual(
        baseline, crosswalk
    )
    assert adjudicated["precision_class"] == (
        "quantized_late_detection_proxy"
    )
    assert adjudicated["exact_start_utc"] is None
    assert adjudicated["known_live_by_utc"] == (
        "2026-07-12T11:55:00+00:00"
    )
    assert any(
        conflict["disposition"]
        == "retain_causal_live_by_proxy_never_overwrites"
        for conflict in adjudicated["round2_conflicts"]
    )
