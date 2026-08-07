#!/usr/bin/env python3
"""Focused, offline checks for the missing-exit-cell fail-loud repair."""

import inspect
import json
import sys
import types
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M  # noqa: E402


def bot(exit_table):
    state = types.SimpleNamespace()
    state.exit_table = exit_table
    state._log_write_errors = 0
    state.logs = []
    state._log = lambda event, details=None, ticker="": state.logs.append(
        (event, details or {}, ticker)
    )
    state.cell_lookup = lambda category, price: int(price)
    state.exit_rule_for = types.MethodType(M.LiveV3.exit_rule_for, state)
    return state


def critical(state):
    return [details for event, details, _ in state.logs
            if event == "CRITICAL_exit_cell_missing"]


def borrowed(state):
    return [details for event, details, _ in state.logs
            if event == "exit_cell_nearest_borrowed"]


def test_exact_cell_has_no_alarm():
    state = bot({"ATP_MAIN": {20: (7, "exit")}})
    assert state.exit_rule_for("ATP_MAIN", 20) == (7, "exit")
    assert state.logs == []


def test_missing_cell_alarms_and_borrows_nearest():
    state = bot({"ATP_MAIN": {10: (3, "exit"), 14: (8, "exit")}})
    assert state.exit_rule_for("ATP_MAIN", 13) == (8, "exit")
    assert len(critical(state)) == 1
    assert len(borrowed(state)) == 1
    assert critical(state)[0]["nearest_cell"] == 14
    assert critical(state)[0]["distance_cents"] == 1
    assert borrowed(state)[0]["borrowed_band_x"] == 8


def test_equal_distance_tie_borrows_lower_cell():
    state = bot({"WTA_MAIN": {10: (4, "exit"), 12: (6, "exit")}})
    assert state.exit_rule_for("WTA_MAIN", 11) == (4, "exit")
    assert critical(state)[0]["tie_break"] == "MIN_ABSOLUTE_DISTANCE_THEN_LOWER_CELL"


def test_itf_uses_existing_challenger_borrow_surface():
    state = bot({"ATP_CHALL": {30: (9, "exit"), 32: (11, "exit")}})
    assert state.exit_rule_for("ITF_M", 31) == (9, "exit")
    assert critical(state)[0]["requested_category"] == "ITF_M"
    assert critical(state)[0]["borrowed_category"] == "ATP_CHALL"


def test_missing_category_alarms_then_raises():
    state = bot({})
    try:
        state.exit_rule_for("ATP_MAIN", 20)
    except RuntimeError as exc:
        assert "no same-category borrow surface" in str(exc)
    else:
        raise AssertionError("missing category did not fail loud")
    assert len(critical(state)) == 1
    assert borrowed(state) == []


def test_silent_fifteen_cent_constant_is_absent():
    source = inspect.getsource(M.LiveV3.exit_rule_for)
    assert 'return (15, "exit")' not in source
    assert "CRITICAL_exit_cell_missing" in source
    assert "exit_cell_nearest_borrowed" in source


if __name__ == "__main__":
    failures = []
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            try:
                value()
                print("PASS", name)
            except Exception as exc:  # pragma: no cover - standalone receipt
                failures.append((name, repr(exc)))
                print("FAIL", name, repr(exc))
    print(json.dumps({"tests": 6, "failures": failures}, sort_keys=True))
    raise SystemExit(1 if failures else 0)
