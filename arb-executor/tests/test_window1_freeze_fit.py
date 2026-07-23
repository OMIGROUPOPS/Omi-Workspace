import datetime as dt
import importlib.util
from contextlib import contextmanager
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_freeze_fit.py"
)
SPEC = importlib.util.spec_from_file_location("window1_freeze_fit", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


@contextmanager
def raises(error_type, text):
    try:
        yield
    except error_type as exc:
        assert text in str(exc)
    else:
        raise AssertionError(f"expected {error_type.__name__}")


def fit_fixture():
    return {
        "status": "fit_complete",
        "selected_candidate_id": "c1",
        "selected_result": {
            "candidate_id": "c1",
            "boundary_id": "b1",
            "window": {"left": 1, "right": 2},
            "policy": {"policy_id": "p1"},
            "raw": {
                "D": 804, "C": 1, "PC": 1, "NC": 1, "IC": 1
            },
            "percentages": {},
            "bounds": {},
        },
        "inputs": {"events": "abc"},
        "selection_rule": ["maximize NC"],
        "metric_definitions": {"NC": "negative pair delta"},
    }


def test_holdout_is_first_three_dates_strictly_after_freeze_utc_date():
    stamp = dt.datetime(2026, 7, 23, 23, 59, tzinfo=dt.timezone.utc)
    receipt = MODULE.build_receipt(
        fit_fixture(),
        freeze_timestamp=stamp,
        fit_summary_sha256="fit",
        denominator_sha256="ledger",
    )
    assert receipt["forward_holdout"]["dates"] == [
        "2026-07-24", "2026-07-25", "2026-07-26"
    ]


def test_freeze_rejects_changed_denominator():
    fit = fit_fixture()
    fit["selected_result"]["raw"]["D"] = 803
    with raises(MODULE.FreezeError, "D=804"):
        MODULE.build_receipt(
            fit,
            freeze_timestamp=dt.datetime.now(dt.timezone.utc),
            fit_summary_sha256="fit",
            denominator_sha256="ledger",
        )
