from __future__ import annotations

import ast
from pathlib import Path
import time
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "live_v4.py"


def _method():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    live = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "LiveV3"
    )
    method = next(
        node for node in live.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_set_skip_no_trade_state"
    )
    module = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"time": time}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace["_set_skip_no_trade_state"]


SET_STATE = _method()


def _bot():
    bot = SimpleNamespace(_skip_no_trade_state={}, _records=[])
    bot._log = lambda name, details=None, ticker="": bot._records.append(
        (name, details or {}, ticker)
    )
    bot._set_skip_no_trade_state = lambda tk, active, details=None: SET_STATE(
        bot, tk, active, details
    )
    return bot


def test_repeated_no_trade_observations_are_one_state():
    bot = _bot()
    ticker = "KXTEST-AAA"

    assert bot._set_skip_no_trade_state(
        ticker, True, {"last_trade_age_sec": 999.0}
    )
    assert not bot._set_skip_no_trade_state(
        ticker, True, {"last_trade_age_sec": 1000.0}
    )
    assert not bot._set_skip_no_trade_state(
        ticker, True, {"last_trade_age_sec": 1001.0}
    )

    assert len(bot._records) == 1
    assert bot._records[0][0] == "skip_no_trade_state"
    assert bot._records[0][1]["transition"] == "enter"
    assert bot._skip_no_trade_state[ticker]["observations"] == 3

    assert bot._set_skip_no_trade_state(
        ticker, False, {"resolved_by": "fresh_anchor"}
    )
    assert len(bot._records) == 2
    assert bot._records[1][1]["transition"] == "exit"
    assert bot._records[1][1]["observations"] == 3
    assert ticker not in bot._skip_no_trade_state


def test_inactive_state_does_not_emit_an_exit():
    bot = _bot()
    assert not bot._set_skip_no_trade_state(
        "KXTEST-BBB", False, {"resolved_by": "fresh_anchor"}
    )
    assert bot._records == []
