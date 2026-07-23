import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "analysis" / "window1_boundary_validation.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_boundary_validation", SCRIPT
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def life(status, completion=None):
    return {
        "event_id": "E",
        "ticker": "T",
        "status": status,
        "completion_exchange_ts": completion,
        "first_fill_exchange_ts": completion,
        "official_fill_quantity": 5,
        "official_fill_vwap_cents": 40,
    }


def start(state, exact=None, bound=None, safe=None):
    return {
        "start_state": state,
        "verified_start_utc": exact,
        "known_live_by_utc": bound,
        "safe_prestart_cutoff_utc": safe or exact,
        "boundary_censored": state != "verified_exact",
    }


def test_exact_prestart_fill():
    row = module.classify_leg(
        life("exact_filled_five", "2026-07-12T10:00:00Z"),
        start("verified_exact", "2026-07-12T11:00:00Z"),
        module.parse_epoch("2026-07-12T09:00:00Z"),
    )
    assert row["proven_window1_fill_five"] is True


def test_fill_before_one_sided_bound_is_censored():
    row = module.classify_leg(
        life("exact_filled_five", "2026-07-12T10:00:00Z"),
        start(
            "bounded_live_by_timestamp", None,
            "2026-07-12T11:00:00Z",
        ),
        module.parse_epoch("2026-07-12T09:00:00Z"),
    )
    assert row["window1_ruling"] == "censored_start_boundary"


def test_fill_before_not_live_through_bound_is_proven_prestart():
    row = module.classify_leg(
        life("exact_filled_five", "2026-07-12T10:00:00Z"),
        start(
            "bounded_start_interval", None,
            "2026-07-12T11:00:00Z",
            "2026-07-12T10:30:00Z",
        ),
        module.parse_epoch("2026-07-12T09:00:00Z"),
    )
    assert row["proven_window1_fill_five"] is True


def test_all_time_nonfill_is_window1_nonfill_without_exact_start():
    row = module.classify_leg(
        life("exact_nonfill"),
        start("schedule_only_censored"),
        module.parse_epoch("2026-07-12T09:00:00Z"),
    )
    assert row["window1_ruling"] == "exact_window1_nonfill"
    assert row["possible_window1_fill_five"] is False


def test_fill_before_left_edge_is_not_window1_inventory():
    row = module.classify_leg(
        life("exact_filled_five", "2026-07-12T08:00:00Z"),
        start("verified_exact", "2026-07-12T11:00:00Z"),
        module.parse_epoch("2026-07-12T09:00:00Z"),
    )
    assert (
        row["window1_ruling"]
        == "exact_pre_window_inventory_not_window1"
    )
    assert row["possible_window1_fill_five"] is False
