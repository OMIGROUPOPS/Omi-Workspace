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

PART B -- WS producer/consumer split (this commit):
  7.   Producer (ws_reader) enqueues frames fast (<1ms/msg) and loses none.
  8.   Worker drains + dispatches correctly: snapshot->book+route, trade->tape,
       market_lifecycle_v2->settlement dispatch (Bug 4 preserved).
  9.   No message loss under burst (every enqueued frame dispatched exactly once).
  10.  Loop NOT starved under burst: a concurrent 50ms probe stays well under the
       1.5s starvation threshold while the worker drains a 300-frame flood.
  11.  Paired-leg placement still works end-to-end through the worker path.

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


async def test_producer_speed_and_no_loss():
    bot = _new_bot()
    et = "KXATPMATCH-26MAY25TSTCCC"
    leader_tk, under_tk = et + "-AAA", et + "-BBB"
    frames = []
    for _ in range(150):
        frames.append(_snapshot_frame(leader_tk, 60, 61))
        frames.append(_snapshot_frame(under_tk, 39, 41))  # 300 frames total
    bot._ws_queue = asyncio.Queue(maxsize=5000)
    bot.ws = FakeWS(frames)
    bot.ws_connected = True

    t0 = time.monotonic()
    reader = asyncio.create_task(bot.ws_reader())
    while bot._ws_queue.qsize() < len(frames):
        await asyncio.sleep(0.001)
    elapsed = time.monotonic() - t0
    reader.cancel()
    try:
        await reader
    except asyncio.CancelledError:
        pass
    per_msg_ms = elapsed / len(frames) * 1000.0
    assert bot._ws_queue.qsize() == len(frames), "producer lost frames"
    assert per_msg_ms < 1.0, "producer too slow: %.3f ms/msg" % per_msg_ms
    print("[7]   PASS  producer enqueued %d frames, %.4f ms/msg, 0 lost"
          % (len(frames), per_msg_ms))


async def test_worker_dispatch_and_burst_lag():
    bot = _new_bot()
    api = live_v4._PAPER_API
    now = time.time()
    start_ts = now + 2 * 3600
    et = "KXATPMATCH-26MAY25TSTDDD"
    leader_tk, under_tk = et + "-AAA", et + "-BBB"
    _inject_event(bot, et, leader_tk, under_tk, now, start_ts)
    bot._ws_queue = asyncio.Queue(maxsize=5000)

    # Instrument dispatch: count every message the worker handles (no-loss check),
    # and stub the Bug-4 settlement hop so we verify dispatch routing without net.
    dispatched = {"n": 0, "lifecycle": 0}
    orig_dispatch = bot._dispatch_ws_message
    async def _counting_dispatch(raw):
        dispatched["n"] += 1
        await orig_dispatch(raw)
    bot._dispatch_ws_message = _counting_dispatch
    lifecycle_hits = []
    async def _fake_settlement(tk, ts):
        lifecycle_hits.append(tk)
    bot._handle_ws_settlement = _fake_settlement

    # Build a burst: 300 BBO snapshots (flood) + 1 trade + 1 lifecycle.
    burst = []
    for _ in range(150):
        burst.append(_snapshot_frame(leader_tk, 60, 61))
        burst.append(_snapshot_frame(under_tk, 39, 41))
    burst.append(_trade_frame(leader_tk, 60, 7))
    burst.append(_lifecycle_frame(leader_tk))
    for raw in burst:
        bot._ws_queue.put_nowait(raw)
    total = len(burst)

    # Concurrent loop-lag probe: 50ms sleeps, record the worst overshoot while the
    # worker drains. If the worker monopolized the loop, the probe would stall.
    max_lag = {"v": 0.0}
    async def _probe():
        for _ in range(40):  # ~2s of probing
            t0 = time.monotonic()
            await asyncio.sleep(0.05)
            lag = (time.monotonic() - t0) - 0.05
            if lag > max_lag["v"]:
                max_lag["v"] = lag
    worker = asyncio.create_task(bot._ws_worker())
    probe = asyncio.create_task(_probe())
    # Wait for the queue to drain.
    while bot._ws_queue.qsize() > 0:
        await asyncio.sleep(0.005)
    await asyncio.sleep(0.05)  # let the final task_done/yield settle
    await probe
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        pass

    assert dispatched["n"] == total, "message loss: dispatched %d of %d" % (dispatched["n"], total)
    assert leader_tk in bot.positions and under_tk in bot.positions, "worker path must place both legs"
    buys = [o for o in api.paper_orders.values() if o.action == "buy"]
    assert len(buys) == 2, "expected 2 buys via worker path, got %d" % len(buys)
    book = bot.books[leader_tk]
    assert book.last_trade_price == 60, "trade-tape not applied via worker"
    assert lifecycle_hits == [leader_tk], "Bug-4 lifecycle dispatch broken: %r" % lifecycle_hits
    assert max_lag["v"] < 1.5, "LOOP STARVED under burst: max probe lag %.3fs" % max_lag["v"]
    print("[8]   PASS  worker dispatched snapshot/trade/lifecycle correctly (Bug 4 intact)")
    print("[9]   PASS  no message loss under burst (%d/%d dispatched)" % (dispatched["n"], total))
    print("[10]  PASS  loop NOT starved under 302-frame burst: max probe lag %.1f ms (<1500)"
          % (max_lag["v"] * 1000.0))
    print("[11]  PASS  paired-leg placement intact through worker path (%d buys)" % len(buys))


async def main():
    await test_on_bbo_update_routing()
    await test_producer_speed_and_no_loss()
    await test_worker_dispatch_and_burst_lag()
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
