import importlib.util
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis" / "window1_execution_calibration.py"
SPEC = importlib.util.spec_from_file_location(
    "window1_execution_calibration", MODULE_PATH
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_start_calibration_keeps_schedule_as_censored_bound():
    rows = []
    states = [
        ("verified_exact", "exchange_milestone_live_transition"),
        ("bounded_start_interval", "tennis_db_live_scores_current_state"),
        (
            "bounded_live_by_timestamp",
            "public_tape_5_prints_in_15m_onset",
        ),
        ("schedule_only_censored", "schedule_plus_declared_corridor"),
    ]
    for index in range(804):
        state, source = states[index % len(states)]
        exact = state == "verified_exact"
        rows.append({
            "event_id": f"E{index:04d}",
            "event_date": "2026-07-12",
            "category": "ATP_MAIN",
            "legs": [
                {"leg": "A", "ticker": f"E{index:04d}-A"},
                {"leg": "B", "ticker": f"E{index:04d}-B"},
            ],
            "start_state": state,
            "selected_source": source,
            "selected_evidence_time_basis": "exchange",
            "verified_start_utc": (
                "2026-07-12T12:00:00Z" if exact else None
            ),
            "start_interval_utc": {
                "lower_exclusive": (
                    "2026-07-12T11:59:00Z"
                    if state == "bounded_start_interval" else None
                ),
                "upper_inclusive": (
                    None if (
                        exact or state == "schedule_only_censored"
                    ) else "2026-07-12T12:00:00Z"
                ),
            },
            "schedule_fallback_right_edge_utc": (
                "2026-07-12T13:00:00Z"
            ),
            "candidate_evidence": [],
        })
    summary = {
        "ws_lifecycle": {"events_with_live_transition": 0}
    }
    ws = {
        "ws_depth": {
            "message_types": {"market_lifecycle_v2": 123}
        }
    }
    ledger, result = M.build_start_ledger(rows, summary, ws)
    schedule = [
        row for row in ledger if row["schedule_only"]
    ]
    assert len(ledger) == 804
    assert len(schedule) == 201
    assert all(row["censored"] for row in schedule)
    assert all(row["exact_start_utc"] is None for row in schedule)
    assert result["gate_pass"] is True
    assert result["schedule_only_promoted_to_exact"] == 0


def test_source_family_precedence_names_are_stable():
    assert M.source_family(
        "exchange_milestone_live_transition"
    ) == "official_or_milestone_bell"
    assert M.source_family(
        "tennis_db_live_scores_current_state"
    ) == "mapped_live_score_onset_or_bound"
    assert M.source_family(
        "engine_regime_transition:tape_flow"
    ) == "defensible_tape_regime_onset"
    assert M.source_family(
        "schedule_plus_declared_corridor"
    ) == "schedule_last_resort_bound"
