#!/usr/bin/env python3
"""Local verification harness for the event-driven routing + WS producer/consumer
restructure. Paper mode, no network (placement + guards route through PaperApi).

PART A -- on_bbo_update routing (d437137c restructure):
  1/2. on_bbo_update places v4 bids on BOTH legs (paired-leg independence) with
       correct v4 fields.
  3.   Periodic backstop sweep (routing_tick) does NOT double-place.
  4.   Per-event reentrancy guard short-circuits a concurrent route.
  5.   on_bbo_update swallows routing errors (no escape into the reader/reconnect).
  6.   on_bbo_update on an untracked ticker is a graceful no-op.

PART B -- WS coalescing split (this commit):
  7.   Coalescing: 1000 BBO frames over 5 tickers -> AT MOST 5 on_bbo_update
       calls (one per ticker, last-value-wins); no bounded queue, no blocking.
  8.   Trades and lifecycle (Bug 4) are NOT coalesced/dropped under a mixed
       flood; BBO is coalesced. Lifecycle reaches the settlement dispatch.
  9.   ws_reader ingest is non-blocking (no await on a full queue) -- a flood is
       absorbed without backpressure on recv.
  10.  Loop NOT starved under a 1000+ frame burst through the real ws_reader:
       a concurrent 50ms probe stays <100ms while the worker drains.
  11.  Paired-leg placement still works end-to-end through the coalesced path.

Run: python test_v4_bbo_routing.py   (exit 0 = all pass)
"""
import asyncio
import json
import time
import live_v4
from live_v4 import LiveV3, Book


# ---------------------------------------------------------------------------
def _mk_book(bid, ask, now):
    b = Book()
    b.bids = {bid: 500}
    b.asks = {ask: 500}
    b.best_bid = bid
    b.best_ask = ask
    b.updated = now
    b.last_trade_price = (bid + ask) // 2
    b.last_trade_ts = now
    return b


def _snapshot_frame(tk, bid, ask):
    """Raw WS snapshot frame that apply_snapshot rebuilds into bid/ask."""
    return json.dumps({"type": "orderbook_snapshot", "msg": {
        "market_ticker": tk,
        "yes": [[bid / 100.0, 500]],
        "no": [[(100 - ask) / 100.0, 500]],
    }})


def _trade_frame(tk, price, count):
    return json.dumps({"type": "trade", "msg": {
        "market_ticker": tk, "yes_price": price, "count": count, "taker_side": "yes"}})


def _lifecycle_frame(tk):
    return json.dumps({"type": "market_lifecycle_v2", "msg": {
        "event_type": "settled", "market_ticker": tk, "settled_ts": time.time()}})


def _new_bot():
    bot = LiveV3()
    assert live_v4._PAPER_API is not None, "expected paper_mode=true from deploy_v5.json"
    bot.session = None  # paper path never touches the session
    return bot


def _inject_event(bot, et, leader_tk, under_tk, now, start_ts):
    for tk in (leader_tk, under_tk):
        bot.ticker_to_event[tk] = et
        bot.event_tickers[et].add(tk)
        bot.ticker_category[tk] = bot.get_category(tk)
    bot.event_start_time[et] = start_ts
    bot.books[leader_tk] = _mk_book(60, 61, now)
    bot.books[under_tk] = _mk_book(39, 41, now)


class FakeWS:
    def __init__(self, frames):
        self._frames = list(frames)
        self.recv_count = 0
    async def recv(self):
        if self._frames:
            self.recv_count += 1
            return self._frames.pop(0)
        await asyncio.sleep(3600)  # idle once drained; the test cancels the task


# ---------------------------------------------------------------------------
async def test_on_bbo_update_routing():
    bot = _new_bot()
    api = live_v4._PAPER_API
    now = time.time()
    start_ts = now + 2 * 3600  # T-2h: in T-4h window, past T-20m, past buffer
    et = "KXATPMATCH-26MAY25TSTAAA"
    leader_tk, under_tk = et + "-AAA", et + "-BBB"
    _inject_event(bot, et, leader_tk, under_tk, now, start_ts)

    await bot.on_bbo_update(leader_tk)
    assert leader_tk in bot.positions and under_tk in bot.positions, "both legs must place"
    lp = bot.positions[leader_tk]
    assert lp.is_v4 and lp.entry_mode in ("marketable_taker", "resting_maker")
    assert lp.regime_at_posting == "r55_64" and lp.entry_order_id
    buys = [o for o in api.paper_orders.values() if o.action == "buy"]
    assert len(buys) == 2, "expected 2 paper buy orders, got %d" % len(buys)
    assert et not in bot._event_routing, "routing guard must release after route"
    print("[1/2] PASS  paired placement mode=%s regime=%s buys=%d"
          % (lp.entry_mode, lp.regime_at_posting, len(buys)))

    orders_before = len(api.paper_orders)
    await bot.routing_tick()
    assert len(api.paper_orders) == orders_before, "backstop sweep double-placed"
    print("[3]   PASS  backstop sweep placed 0 new orders")

    et2 = "KXWTAMATCH-26MAY25TSTBBB"
    l2, u2 = et2 + "-CCC", et2 + "-DDD"
    _inject_event(bot, et2, l2, u2, now, start_ts)
    bot._event_routing.add(et2)
    await bot._route_event(et2, bot.event_tickers[et2], time.time())
    assert l2 not in bot.positions and u2 not in bot.positions, "reentrancy guard failed"
    bot._event_routing.discard(et2)
    print("[4]   PASS  reentrancy guard blocked concurrent route")

    orig = bot._route_event
    async def _boom(*a, **k):
        raise RuntimeError("synthetic routing failure")
    bot._route_event = _boom
    try:
        await bot.on_bbo_update(l2)  # must NOT raise
    finally:
        bot._route_event = orig
    print("[5]   PASS  on_bbo_update swallowed routing error")

    await bot.on_bbo_update("KXNOPE-DOESNOTEXIST-ZZZ")
    print("[6]   PASS  untracked ticker handled gracefully")


async def test_coalescing_and_trade_lifecycle():
    bot = _new_bot()
    api = live_v4._PAPER_API
    bot._bbo_event = asyncio.Event()
    now = time.time()
    start_ts = now + 2 * 3600
    et = "KXATPMATCH-26MAY25TSTCCC"
    leader_tk, under_tk = et + "-AAA", et + "-BBB"
    _inject_event(bot, et, leader_tk, under_tk, now, start_ts)
    # 3 standalone tickers (no event) -> on_bbo_update entered but early-returns.
    extra = ["KXATPMATCH-26MAY25TSTCCC-EEE", "KXWTAMATCH-26MAY25TSTCCC-FFF",
             "KXATPCHALLENGERMATCH-26MAY25TSTCCC-GGG"]
    five = [leader_tk, under_tk] + extra

    # Count on_bbo_update entries (coalescing assertion).
    routed = {"n": 0}
    orig_obu = bot.on_bbo_update
    async def _counting_obu(tk):
        routed["n"] += 1
        await orig_obu(tk)
    bot.on_bbo_update = _counting_obu
    # Stub the Bug-4 REST hop (public-data call) so lifecycle dispatch is offline.
    lifecycle_hits = []
    async def _fake_settlement(tk, ts):
        lifecycle_hits.append(tk)
    bot._handle_ws_settlement = _fake_settlement

    # Ingest 1000 BBO frames cycling the 5 tickers + 40 trades + 5 lifecycle.
    n_bbo = 1000
    for i in range(n_bbo):
        tk = five[i % 5]
        bid, ask = (60, 61) if tk == leader_tk else (39, 41) if tk == under_tk else (50, 52)
        bot._ingest_ws_frame(_snapshot_frame(tk, bid, ask))
    n_trades = 40
    for i in range(n_trades):
        bot._ingest_ws_frame(_trade_frame(leader_tk, 60, 3))
    n_life = 5
    for i in range(n_life):
        bot._ingest_ws_frame(_lifecycle_frame(et + "-LIFE%d" % i))

    # 9: ingest never blocked -> all BBO collapsed to a 5-ticker dirty set.
    assert len(bot._bbo_dirty) == 5, "expected 5 dirty tickers, got %d" % len(bot._bbo_dirty)
    # Trades applied in-order (not coalesced): VolumeTracker saw every print.
    assert api.volume_tracker.sample_count == n_trades, \
        "trade loss: VolumeTracker saw %d of %d" % (api.volume_tracker.sample_count, n_trades)
    # Lifecycle dispatched for every settled event (Bug 4 not dropped).
    await asyncio.sleep(0)  # let the create_task lifecycle coroutines run
    assert len(lifecycle_hits) == n_life, \
        "lifecycle loss: %d of %d dispatched" % (len(lifecycle_hits), n_life)
    print("[9]   PASS  ingest non-blocking; %d BBO frames coalesced to %d dirty tickers"
          % (n_bbo, len(bot._bbo_dirty)))
    print("[8]   PASS  trades not coalesced (%d/%d), lifecycle not dropped (%d/%d, Bug 4 intact)"
          % (api.volume_tracker.sample_count, n_trades, len(lifecycle_hits), n_life))

    # 7: drain the worker once -> AT MOST 5 on_bbo_update calls for 1000 frames.
    worker = asyncio.create_task(bot._ws_worker())
    while bot._bbo_dirty:
        await asyncio.sleep(0.005)
    await asyncio.sleep(0.02)
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        pass
    assert routed["n"] == 5, "coalescing failed: %d on_bbo_update calls for 1000 frames" % routed["n"]
    # 11: paired-leg placement happened on the latest state via the coalesced path.
    assert leader_tk in bot.positions and under_tk in bot.positions, "paired placement missing"
    buys = [o for o in api.paper_orders.values() if o.action == "buy"]
    assert len(buys) == 2, "expected 2 buys, got %d" % len(buys)
    print("[7]   PASS  1000 BBO frames -> %d on_bbo_update calls (coalesced, <=5)" % routed["n"])
    print("[11]  PASS  paired-leg placement intact through coalesced path (%d buys)" % len(buys))


async def test_loop_not_starved_under_burst():
    bot = _new_bot()
    bot._bbo_event = asyncio.Event()
    now = time.time()
    start_ts = now + 2 * 3600
    et = "KXATPMATCH-26MAY25TSTDDD"
    leader_tk, under_tk = et + "-AAA", et + "-BBB"
    _inject_event(bot, et, leader_tk, under_tk, now, start_ts)

    # 1200-frame flood through the REAL ws_reader (recv yields per frame via
    # wait_for) + the worker draining concurrently + a 50ms loop-lag probe.
    frames = []
    for _ in range(600):
        frames.append(_snapshot_frame(leader_tk, 60, 61))
        frames.append(_snapshot_frame(under_tk, 39, 41))
    bot.ws = FakeWS(frames)
    bot.ws_connected = True

    max_lag = {"v": 0.0}
    async def _probe():
        for _ in range(40):  # ~2s
            t0 = time.monotonic()
            await asyncio.sleep(0.05)
            lag = (time.monotonic() - t0) - 0.05
            if lag > max_lag["v"]:
                max_lag["v"] = lag
    reader = asyncio.create_task(bot.ws_reader())
    worker = asyncio.create_task(bot._ws_worker())
    probe = asyncio.create_task(_probe())
    while bot.ws.recv_count < len(frames):
        await asyncio.sleep(0.005)
    await asyncio.sleep(0.1)
    await probe
    for t in (reader, worker):
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass

    assert leader_tk in bot.positions and under_tk in bot.positions, "placement missing under burst"
    assert max_lag["v"] < 0.1, "LOOP STARVED: max probe lag %.1f ms (>=100)" % (max_lag["v"] * 1000.0)
    print("[10]  PASS  loop NOT starved under 1200-frame burst: max probe lag %.1f ms (<100)"
          % (max_lag["v"] * 1000.0))


async def test_settlement_dedup():
    """FIX 1: 50 settled-lifecycle events for one ticker -> exactly 1 handler
    spawn (in-flight guard); a settled ticker -> 0 spawns; a repeat within the
    cooldown -> 0 spawns."""
    from live_v4 import PaperPosition
    bot = _new_bot()
    api = live_v4._PAPER_API
    bot._bbo_event = asyncio.Event()

    state = {"cur": 0, "max": 0, "runs": []}
    async def _probe_settlement(tk, ts):
        state["cur"] += 1
        state["max"] = max(state["max"], state["cur"])
        state["runs"].append(tk)
        await asyncio.sleep(0.02)
        state["cur"] -= 1
    bot._handle_ws_settlement = _probe_settlement

    tk = "KXATPMATCH-26MAY25TSTEEE-AAA"
    for _ in range(50):
        bot._ingest_ws_frame(_lifecycle_frame(tk))  # synchronous spawns
    assert bot._inflight_settlements == {tk}, "in-flight guard not set: %r" % bot._inflight_settlements
    await asyncio.sleep(0.05)  # let the single task run + release
    assert state["runs"].count(tk) == 1, "expected 1 spawn for 50 events, got %d" % state["runs"].count(tk)
    assert state["max"] == 1, "concurrent handlers for one ticker: %d" % state["max"]
    assert tk not in bot._inflight_settlements, "in-flight guard not released"
    print("[12]  PASS  50 settled events -> 1 handler spawn, max concurrency 1")

    # Repeat within cooldown -> still skipped.
    for _ in range(10):
        bot._ingest_ws_frame(_lifecycle_frame(tk))
    await asyncio.sleep(0.03)
    assert state["runs"].count(tk) == 1, "cooldown failed: re-spawned within %ds" % live_v4.SETTLEMENT_RETRY_COOLDOWN
    print("[13]  PASS  re-emit within cooldown -> 0 re-spawn")

    # Already-settled ticker -> 0 spawns.
    tk2 = "KXATPMATCH-26MAY25TSTEEE-BBB"
    api.paper_positions[tk2] = PaperPosition(ticker=tk2, settled=True)
    bot._ingest_ws_frame(_lifecycle_frame(tk2))
    await asyncio.sleep(0.02)
    assert tk2 not in state["runs"], "settled-guard failed: spawned for already-settled ticker"
    print("[14]  PASS  settled ticker -> 0 handler spawn (Bug 4 idempotency upheld)")


async def _probe_max_lag(seconds, step=0.05):
    """Run a loop-lag probe for `seconds`; return the worst overshoot."""
    worst = 0.0
    n = int(seconds / step)
    for _ in range(n):
        t0 = time.monotonic()
        await asyncio.sleep(step)
        lag = (time.monotonic() - t0) - step
        if lag > worst:
            worst = lag
    return worst


async def test_schedule_parse_offload():
    """FIX 2: a heavy schedule parse runs in an executor; the loop stays
    responsive (probe lag <100ms) instead of blocking on the parse."""
    bot = _new_bot()
    def _spin():
        t0 = time.monotonic()
        while time.monotonic() - t0 < 0.3:  # 300ms pure-CPU stand-in for the parse
            pass
        return {"schedule": {"x": 1}, "fetched_epoch": time.time(), "fetched_et": "test"}, None
    bot._read_schedule_file = _spin

    probe = asyncio.create_task(_probe_max_lag(0.6))
    await bot._load_schedule_async()
    worst = await probe
    assert bot.schedule == {"x": 1}, "schedule not applied after offloaded parse"
    assert worst < 0.1, "loop starved during schedule parse: max lag %.1f ms" % (worst * 1000.0)
    print("[15]  PASS  schedule parse offloaded; loop lag %.1f ms during 300ms parse (<100)"
          % (worst * 1000.0))


async def test_discovery_chunking():
    """FIX 3: discovery yields periodically so the per-market sync work
    (schedule match + sqlite) can't block the loop (probe lag <100ms)."""
    bot = _new_bot()
    orig_api_get = live_v4.api_get
    async def _fake_api_get(s, ak, pk, path, rl):
        if "series_ticker" in path and "cursor" not in path:
            markets = [{"ticker": "KXATPMATCH-26MAY25EV%03d-AAA" % i,
                        "event_ticker": "KXATPMATCH-26MAY25EV%03d" % i,
                        "volume_fp": "100", "yes_sub_title": "A", "no_sub_title": "B"}
                       for i in range(200)]
            return {"markets": markets, "cursor": ""}
        return {"markets": [], "cursor": ""}
    def _heavy_match(et):
        t0 = time.monotonic()
        while time.monotonic() - t0 < 0.002:  # 2ms CPU per new event
            pass
        return None, None
    live_v4.api_get = _fake_api_get
    bot._match_event_to_schedule = _heavy_match
    bot._commence_time_from_book_prices = lambda et: None
    try:
        probe = asyncio.create_task(_probe_max_lag(0.8))
        tickers = await bot.discover_markets()
        worst = await probe
    finally:
        live_v4.api_get = orig_api_get
    assert tickers, "discovery returned no tickers"
    assert worst < 0.1, "loop starved during discovery: max lag %.1f ms" % (worst * 1000.0)
    print("[16]  PASS  discovery chunked; loop lag %.1f ms over %d markets w/ 2ms-each match (<100)"
          % (worst * 1000.0, len(tickers)))


async def test_schedule_rematch_offload():
    """This commit: the post-reload schedule re-match (the ~2198-entry fuzzy
    scan, a single multi-second call that cannot be chunked) is offloaded to a
    thread; the loop stays responsive (probe lag <100ms) across ~10 heavy
    matches, mirroring a reload cycle."""
    bot = _new_bot()
    bot.event_player_names = {}
    def _heavy_match(event_ticker, schedule, player_names):
        t0 = time.monotonic()
        while time.monotonic() - t0 < 0.08:  # 80ms pure-CPU stand-in per match
            pass
        return None, None, [("schedule_unmatched", {"event": event_ticker})]
    bot._match_event_pure = _heavy_match

    probe = asyncio.create_task(_probe_max_lag(1.2))
    for i in range(10):  # ~800ms of matching, offloaded
        await bot._match_event_to_schedule_async("KXATPMATCH-26MAY25EV%03d" % i)
    worst = await probe
    assert worst < 0.1, "loop starved during re-match: max lag %.1f ms" % (worst * 1000.0)
    print("[17]  PASS  schedule re-match offloaded; loop lag %.1f ms over 10x80ms matches (<100)"
          % (worst * 1000.0))


async def test_rematch_parity():
    """The offloaded async match returns the same (result, method) and emits the
    same logs as the sync path -- offload must not change matching behavior."""
    bot = _new_bot()
    bot.schedule = {"AAABBB": {"start_time": "2026-05-25T16:00:00Z",
                               "p1": "X", "p2": "Y", "category": "ATP_MAIN"}}
    bot.event_player_names = {}
    et = "KXATPMATCH-26MAY25AAABBB"
    logged = []
    orig_log = bot._log
    bot._log = lambda ev, det=None, ticker="": logged.append(ev)
    r_sync, m_sync = bot._match_event_to_schedule(et)
    r_async, m_async = await bot._match_event_to_schedule_async(et)
    bot._log = orig_log
    assert m_sync == m_async == "direct_6char", "method mismatch: %r vs %r" % (m_sync, m_async)
    assert r_sync == r_async and r_async is not None, "result mismatch"
    assert logged.count("schedule_match") == 2, "expected 2 schedule_match logs, got %r" % logged
    print("[18]  PASS  async re-match parity: same result/method/logs as sync (direct_6char)")


async def main():
    await test_on_bbo_update_routing()
    await test_coalescing_and_trade_lifecycle()
    await test_loop_not_starved_under_burst()
    await test_settlement_dedup()
    await test_schedule_parse_offload()
    await test_discovery_chunking()
    await test_schedule_rematch_offload()
    await test_rematch_parity()
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
