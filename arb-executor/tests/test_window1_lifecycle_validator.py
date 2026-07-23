import importlib.util
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "analysis" / "window1_lifecycle_validator.py"
SPEC = importlib.util.spec_from_file_location(
    "window1_lifecycle_validator", MODULE_PATH)
M = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def order(order_id, trade_id="T-1", status=None, fill_count=None,
          quantity=5, accepted=True):
    return {
        "event_id": "KXEVENT",
        "ticker": "KXEVENT-LEG",
        "trade_id": trade_id,
        "order_id": order_id,
        "accepted": accepted,
        "quantity": quantity,
        "exchange_initial_count": quantity,
        "exchange_status": status,
        "exchange_fill_count": fill_count,
        "local_logged_ts": 100.0,
    }


def fill(order_id, quantity=5, price=42, timestamp=110):
    return {
        "fill_id": f"F-{order_id}",
        "order_id": order_id,
        "ticker": "KXEVENT-LEG",
        "action": "buy",
        "quantity": quantity,
        "price_cents": price,
        "exchange_ts": timestamp,
    }


def logs(cancellations=None, entry_fills=None, settlements=None):
    return M.LogEvidence(
        {}, cancellations or {}, entry_fills or {}, settlements or {},
        0, 0, 0)


def classify(orders, fills_by_order=None, evidence=None, unmatched=None):
    row, mismatches = M.classify_lifecycle(
        ("KXEVENT", "KXEVENT-LEG", "T-1"),
        orders,
        fills_by_order or {},
        evidence or logs(),
        unmatched or {},
        200.0,
    )
    return row, mismatches


def test_reposts_collapse_to_one_lineage():
    rows = [order("O-1"), order("O-2")]
    grouped = {}
    for row in rows:
        grouped.setdefault(M.lifecycle_key(row), []).append(row)
    assert len(grouped) == 1
    assert len(next(iter(grouped.values()))) == 2


def test_fill_truth_comes_from_private_fills_and_requires_exact_five():
    rows = [order("O-1", status="executed", fill_count="5")]
    result, mismatches = classify(rows, {"O-1": [fill("O-1")]})
    assert result["status"] == "exact_filled_five"
    assert result["official_fill_quantity"] == 5
    assert not mismatches

    result, _ = classify(
        rows, {"O-1": [fill("O-1", quantity=4)]})
    assert result["status"] == "exact_filled_other_quantity"


def test_zero_fill_requires_exact_closure():
    rows = [order("O-1")]
    result, _ = classify(rows, evidence=logs({
        "O-1": [{"success": True, "label": "v4_move_repost"}],
    }))
    assert result["status"] == "exact_nonfill"

    result, _ = classify(rows)
    assert result["status"] == "censored"
    assert "accepted_order_not_exactly_closed" in result["censor_reasons"]


def test_official_zero_fill_terminal_is_nonfill():
    rows = [order("O-1", status="canceled", fill_count="0")]
    result, mismatches = classify(rows)
    assert result["status"] == "exact_nonfill"
    assert not mismatches


def test_unmatched_position_increase_censors_nonfill():
    rows = [order("O-1", status="canceled", fill_count="0")]
    result, _ = classify(
        rows,
        unmatched={"KXEVENT-LEG": [fill("OTHER", timestamp=120)]},
    )
    assert result["status"] == "censored"
    assert "unmatched_position_increase_proxy" in result["censor_reasons"]


def test_engine_fill_without_private_fill_is_mismatch_and_censored():
    rows = [order("O-1", status="canceled", fill_count="0")]
    result, mismatches = classify(
        rows,
        evidence=logs(entry_fills={
            "T-1": [{
                "qty": 5,
                "new_fills": 5,
                "fill_price_cents": 42,
            }],
        }),
    )
    assert result["status"] == "censored"
    assert mismatches[0]["mismatch_type"] == "entry_fill_without_private_fill"


def test_exchange_initial_quantity_repairs_corrupt_local_quantity():
    row = order("O-1", quantity=4)
    row["quantity"] = 4.19
    assert M.official_order_quantity(row) == 4


def test_unmapped_private_fill_requires_exact_order_id_placement():
    fills = [fill("O-NEW")]
    placement = {
        "O-NEW": [{
            "order_id": "O-NEW",
            "client_order_id": "C-NEW",
            "trade_id": "T-NEW",
            "ticker": "KXEVENT-LEG",
            "action": "buy",
            "side": "yes",
            "price_cents": 42,
            "quantity": 5,
            "local_logged_ts": 100,
        }],
    }
    evidence = M.LogEvidence(placement, {}, {}, {}, 0, 0, 0)
    recovered, mismatches = M.recover_unmapped_fill_orders(
        fills, set(), {"KXEVENT": {}}, evidence)
    assert len(recovered) == 1
    assert recovered[0]["trade_id"] == "T-NEW"
    assert not mismatches


def test_leg_status_keeps_censoring_in_denominator():
    event = {
        "event_id": "KXEVENT",
        "event_date": "2026-07-12",
        "category": "ATP_MAIN",
    }
    row = M.leg_row(event, "KXEVENT-LEG", [], [])
    assert row["status"] == "censored"
    assert row["possible_five_contract_upper_bound"] is True
    assert "required_leg_decision_unobserved" in row["censor_reasons"]
