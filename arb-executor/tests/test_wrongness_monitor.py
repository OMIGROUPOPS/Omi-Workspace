import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wrongness_monitor import VerdictMonitor, audit_surface_consult


def _codes(alarms):
    return {alarm.code for alarm in alarms}


def test_surface_key_mismatch_and_thin_row_alarm_together():
    alarms = audit_surface_consult(
        "ATLAS_V1:ATP_MAIN|leader|51_75",
        {
            "price_source": "first_hour_median",
            "timestamp_semantics": "discovery_hour",
        },
        {
            "price_source": "fresh_last_trade",
            "timestamp_semantics": "exact_consultation_time",
        },
        fitted_n=8,
    )
    assert _codes(alarms) == {
        "FIT_CONSULT_KEY_MISMATCH",
        "FITTED_ROW_THIN",
    }


def test_missing_fit_contract_is_blocking():
    alarms = audit_surface_consult(
        "legacy_table", None,
        {"price_source": "fresh_last_trade"},
        fitted_n=100,
    )
    assert _codes(alarms) == {"FIT_CONTRACT_MISSING"}


def test_drop_followed_by_post_is_an_ignored_verdict():
    monitor = VerdictMonitor()
    assert not monitor.record(
        "d1", "TICKER", "DROP", expected_effect="REFUSE"
    )
    alarms = monitor.observe(
        "d1", effect="POST", actual_price=42, order_id="o1"
    )
    assert _codes(alarms) == {"VERDICT_IGNORED"}


def test_wrong_authorized_price_alarms():
    monitor = VerdictMonitor()
    monitor.record(
        "d2", "TICKER", "AUTHORIZED", expected_effect="POST",
        expected_price=37,
    )
    alarms = monitor.observe(
        "d2", effect="POST", actual_price=48, order_id="o2"
    )
    assert _codes(alarms) == {"AUTHORIZED_PRICE_IGNORED"}


def test_unresolved_verdict_alarms():
    monitor = VerdictMonitor()
    monitor.record("d3", "TICKER", "DROP", expected_effect="REFUSE")
    assert _codes(monitor.unresolved()) == {"VERDICT_WITHOUT_EFFECT"}
