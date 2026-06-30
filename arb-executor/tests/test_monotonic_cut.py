"""[C-MONOTONIC-CUT] unit tests: decoupled gun predicate + monotonic-faller decision + shadow-only default.
Run: python3 -m pytest tests/test_monotonic_cut.py -q   (or python3 tests/test_monotonic_cut.py)"""
import asyncio
import live_v4 as M


class FakeSelf:
    _gun_detected_for_cut = M.LiveV3._gun_detected_for_cut
    _monotonic_cut_eval = M.LiveV3._monotonic_cut_eval

    def __init__(self, active=False):
        self.event_tickers = {}
        self._trade_times = {}
        self._trade_prices = {}
        self.monotonic_cut_enabled = True
        self.monotonic_cut_active = active
        self.logs = []
        self.placed = []
        self.cancelled = []

    def _log(self, ev, d, ticker=None):
        self.logs.append((ev, d))

    async def cancel_order(self, tk, oid, label=""):
        self.cancelled.append((tk, oid, label))

    async def place_order(self, tk, action, side, price, count, post_only=True):
        self.placed.append((tk, action, side, price, count))
        return ("oid-cut", {})


def _pos(fill=70):
    p = M.Position(ticker="EV-A", event_ticker="EV", category="ATP_MAIN",
                   direction="leader", cell_name="c", cell_cfg={})
    p.is_v4 = True
    p.entry_filled_ts = 1.0
    p.entry_price = fill
    p.entry_qty = 5
    p.phase = "active"
    return p


def test_constants_decoupled():
    # INVARIANT 2: the CUT gun must NOT equal the cancel gun.
    assert M.CUT_GUN_BURST == 5 and M.CUT_GUN_BURST != M.LIVE_TRADE_BURST
    assert M.CUT_GUN_K == 2
    assert M.CUT_N_SEC == 1800 and M.CUT_X_CENTS == 10


def test_gun_predicate(monkeypatch=None):
    now = 1_000_000.0
    orig = M.time.time
    M.time.time = lambda: now
    try:
        f = FakeSelf()
        f.event_tickers = {"EV": {"EV-A"}}
        # 5 prints in window0 [now-60,now), 5 in window1 [now-120,now-60) -> fires
        f._trade_times = {"EV-A": [now - 30] * 5 + [now - 90] * 5}
        assert f._gun_detected_for_cut("EV") is True
        # 4 in window0 -> below CUT_GUN_BURST -> no fire
        f._trade_times = {"EV-A": [now - 30] * 4 + [now - 90] * 5}
        assert f._gun_detected_for_cut("EV") is False
    finally:
        M.time.time = orig


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_monotonic_fires_shadow_only():
    now = [1_000_000.0]
    orig = M.time.time
    M.time.time = lambda: now[0]
    try:
        f = FakeSelf(active=False)              # SHADOW
        f.event_tickers = {"EV": {"EV-A"}}
        f._trade_times = {"EV-A": [now[0] - 30] * 5 + [now[0] - 90] * 5}
        p = _pos(fill=70)
        # tick 1: gun latches, no decision yet
        _run(f._monotonic_cut_eval("EV-A", p))
        assert p.cut_gun_ts == now[0] and not p.cut_evaluated
        # post-gun tape: fell to 60 (<=70-10) and NEVER printed above 70 -> monotonic faller
        f._trade_prices = {"EV-A": [(now[0] + 60, 66), (now[0] + 120, 60)]}
        now[0] += M.CUT_N_SEC + 1                # advance past gun+30min
        _run(f._monotonic_cut_eval("EV-A", p))
        evs = [e for e, _ in f.logs]
        assert "monotonic_cut_would_fire" in evs
        assert p.cut_dipped and not p.cut_wobble and p.cut_fired
        assert f.placed == [] and f.cancelled == []   # SHADOW: no flatten
    finally:
        M.time.time = orig


def test_wobble_blocks_fire():
    now = [1_000_000.0]
    orig = M.time.time
    M.time.time = lambda: now[0]
    try:
        f = FakeSelf(active=True)               # even ACTIVE, wobble must block
        f.event_tickers = {"EV": {"EV-A"}}
        f._trade_times = {"EV-A": [now[0] - 30] * 5 + [now[0] - 90] * 5}
        p = _pos(fill=70)
        _run(f._monotonic_cut_eval("EV-A", p))   # gun
        # printed ABOVE fill (84) then dipped -> ERHROD-class, NOT monotonic -> must NOT fire
        f._trade_prices = {"EV-A": [(now[0] + 30, 84), (now[0] + 120, 60)]}
        now[0] += M.CUT_N_SEC + 1
        _run(f._monotonic_cut_eval("EV-A", p))
        evs = [e for e, _ in f.logs]
        assert "monotonic_cut_no_fire" in evs and "monotonic_cut_would_fire" not in evs
        assert p.cut_wobble and not p.cut_fired
        assert f.placed == []                    # no flatten on a wobbler
    finally:
        M.time.time = orig


def test_active_flattens():
    now = [1_000_000.0]
    orig = M.time.time
    M.time.time = lambda: now[0]
    try:
        f = FakeSelf(active=True)               # ACTIVE
        f.event_tickers = {"EV": {"EV-A"}}
        f._trade_times = {"EV-A": [now[0] - 30] * 5 + [now[0] - 90] * 5}
        p = _pos(fill=70)
        p.exit_order_id = "band-exit-oid"
        _run(f._monotonic_cut_eval("EV-A", p))
        f._trade_prices = {"EV-A": [(now[0] + 60, 60)]}   # monotonic faller to 60
        now[0] += M.CUT_N_SEC + 1
        _run(f._monotonic_cut_eval("EV-A", p))
        assert f.cancelled == [("EV-A", "band-exit-oid", "monotonic_cut_flatten")]
        assert f.placed == [("EV-A", "sell", "yes", 60, 5)]   # flatten at fill-10 = 60, open qty 5
    finally:
        M.time.time = orig


if __name__ == "__main__":
    test_constants_decoupled()
    test_gun_predicate()
    test_monotonic_fires_shadow_only()
    test_wobble_blocks_fire()
    test_active_flattens()
    print("ALL 5 PASS")
