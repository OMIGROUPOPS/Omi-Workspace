import importlib.util
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis" / "window1_execution_kernel.py"
SPEC = importlib.util.spec_from_file_location(
    "window1_execution_kernel", MODULE_PATH
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_counterfactual_kernel_never_promotes_zero_size():
    actions = [{"ts": 100, "price": 40, "queue_ahead": 0}]
    prints = [{
        "ts": 110,
        "price": 39,
        "size": 0,
        "taker_side": "no",
    }]
    result = M.simulate_candidate_actions(
        actions, prints, 120, "upper"
    )
    assert result["quantity"] == 0
    assert result["status"] == "not_filled"


def test_historical_receipts_reproduce_fill_and_nonfill():
    events = [{
        "event_id": "E",
        "event_date": "2026-07-12",
        "category": "ATP_MAIN",
        "legs": [
            {"leg": "A", "ticker": "E-A"},
            {"leg": "B", "ticker": "E-B"},
        ],
    }]
    orders = [
        {
            "event_id": "E",
            "ticker": "E-A",
            "trade_id": "TA",
            "order_id": "OA",
            "accepted": True,
            "action": "buy",
            "price_cents": 40,
            "quantity": 5,
            "local_logged_ts": 100,
            "exchange_created_ts": 101,
        },
        {
            "event_id": "E",
            "ticker": "E-B",
            "trade_id": "TB",
            "order_id": "OB",
            "accepted": True,
            "action": "buy",
            "price_cents": 60,
            "quantity": 5,
            "local_logged_ts": 100,
            "exchange_status": "canceled",
            "exchange_fill_count": 0,
        },
    ]
    fills = [{
        "fill_id": "FA",
        "trade_id": "PFA",
        "order_id": "OA",
        "ticker": "E-A",
        "action": "buy",
        "side": "yes",
        "yes_price_dollars": "0.4000",
        "no_price_dollars": "0.6000",
        "count_fp": "5.00",
        "created_time": "2026-07-12T00:01:50Z",
    }]
    lifecycles = [
        {
            "event_id": "E",
            "ticker": "E-A",
            "lineage": "TA",
            "status": "exact_filled_five",
            "accepted_order_ids": ["OA"],
            "failed_attempts": 0,
            "official_fill_ids": ["FA"],
            "official_fill_quantity": 5,
            "official_fill_vwap_cents": 40,
            "first_fill_exchange_ts": 1783814510,
            "completion_exchange_ts": 1783814510,
            "cancellation_evidence": {},
            "censor_reasons": [],
        },
        {
            "event_id": "E",
            "ticker": "E-B",
            "lineage": "TB",
            "status": "exact_nonfill",
            "accepted_order_ids": ["OB"],
            "failed_attempts": 0,
            "official_fill_ids": [],
            "official_fill_quantity": 0,
            "official_fill_vwap_cents": None,
            "first_fill_exchange_ts": None,
            "completion_exchange_ts": None,
            "closure_receipts": [{
                "order_id": "OB",
                "closed": True,
                "reason": "official_zero_fill_terminal",
            }],
            "cancellation_evidence": {},
            "censor_reasons": [],
        },
    ]
    expected = [
        {
            "ticker": "E-A",
            "status": "exact_filled_five",
            "official_fill_quantity": 5,
            "official_fill_vwap_cents": 40,
        },
        {
            "ticker": "E-B",
            "status": "exact_nonfill",
            "official_fill_quantity": 0,
            "official_fill_vwap_cents": None,
        },
    ]
    legs, mismatches, summary = M.replay_historical_execution(
        events, orders, fills, lifecycles, [], expected
    )
    assert not mismatches
    assert len(legs) == 2
    assert summary["leg_status_counts"] == {
        "exact_filled_five": 1,
        "exact_nonfill": 1,
    }
    assert summary["schedule_fields_consumed"] is False


def test_private_fill_requires_positive_size():
    row = {
        "fill_id": "F",
        "order_id": "O",
        "ticker": "E-A",
        "action": "buy",
        "side": "yes",
        "yes_price_dollars": "0.4",
        "count_fp": "0",
        "created_time": "2026-07-12T00:00:00Z",
    }
    try:
        M.canonical_private_fill(row)
    except M.ExecutionKernelError as exc:
        assert "promoted" in str(exc)
    else:
        raise AssertionError("zero-size private fill was accepted")
