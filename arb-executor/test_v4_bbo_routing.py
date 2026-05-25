#!/usr/bin/env python3
"""Local verification harness for the event-driven routing restructure.

Instantiates LiveV3 in paper mode (no network: placement + guards route through
PaperApi), injects a synthetic paired event with fresh books inside the
placement window, and drives on_bbo_update end-to-end. Asserts:

  1. on_bbo_update places v4 bids on BOTH legs (paired-leg independence).
  2. The paper order + Position are created with correct v4 fields.
  3. The periodic backstop sweep (routing_tick) does NOT double-place an
     already-positioned event.
  4. The per-event reentrancy guard short-circuits a concurrent route.
  5. on_bbo_update swallows routing errors (no exception escapes into the WS
     reader / reconnect path).
  6. on_bbo_update on an untracked ticker is a graceful no-op.

Run: python test_v4_bbo_routing.py   (exit 0 = all pass)
"""
import asyncio
import time
import live_v4
from live_v4 import LiveV3, Book


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


def _inject_event(bot, et, leader_tk, under_tk, cat_prefix, now, start_ts):
    """Wire one synthetic paired event into bot state (no discovery/network)."""
    for tk in (leader_tk, under_tk):
        bot.ticker_to_event[tk] = et
        bot.event_tickers[et].add(tk)
        bot.ticker_category[tk] = bot.get_category(tk)
    bot.event_start_time[et] = start_ts
    # Leader: bid 60 / ask 61 (>50). Underdog: bid 39 / ask 41 (<50).
    bot.books[leader_tk] = _mk_book(60, 61, now)
    bot.books[under_tk] = _mk_book(39, 41, now)


async def main():
    bot = LiveV3()
    assert live_v4._PAPER_API is not None, "expected paper_mode=true from deploy_v5.json"
    bot.session = None  # paper path never touches the session
    api = live_v4._PAPER_API

    now = time.time()
    start_ts = now + 2 * 3600  # T-2h: inside T-4h window, past T-20m, past buffer
    et = "KXATPMATCH-26MAY25TSTAAA"
    leader_tk = et + "-AAA"
    under_tk = et + "-BBB"
    _inject_event(bot, et, leader_tk, under_tk, "KXATPMATCH", now, start_ts)

    # --- 1/2: drive on_bbo_update for the leader -> routes the whole event ---
    await bot.on_bbo_update(leader_tk)

    assert leader_tk in bot.positions, "leader leg should have a Position"
    assert under_tk in bot.positions, "underdog leg should have a Position (paired)"
    lp = bot.positions[leader_tk]
    assert lp.is_v4 is True, "position must be flagged v4"
    assert lp.entry_mode in ("marketable_taker", "resting_maker"), lp.entry_mode
    assert lp.regime_at_posting == "r55_64", lp.regime_at_posting
    assert lp.entry_order_id, "entry order id must be set"
    buys = [o for o in api.paper_orders.values() if o.action == "buy"]
    assert len(buys) == 2, "expected 2 paper buy orders (one per leg), got %d" % len(buys)
    assert et not in bot._event_routing, "routing guard must be released after route"
    print("[1/2] PASS  legs=%s mode=%s regime=%s buys=%d"
          % (sorted(p[-3:] for p in (leader_tk, under_tk)),
             lp.entry_mode, lp.regime_at_posting, len(buys)))

    # --- 3: backstop sweep must NOT double-place an already-positioned event ---
    orders_before = len(api.paper_orders)
    await bot.routing_tick()
    assert len(api.paper_orders) == orders_before, \
        "backstop sweep double-placed: %d -> %d" % (orders_before, len(api.paper_orders))
    print("[3]   PASS  backstop sweep placed 0 new orders (no double-place)")

    # --- 4: reentrancy guard short-circuits a concurrent route ---
    et2 = "KXWTAMATCH-26MAY25TSTBBB"
    l2, u2 = et2 + "-CCC", et2 + "-DDD"
    _inject_event(bot, et2, l2, u2, "KXWTAMATCH", now, start_ts)
    bot._event_routing.add(et2)  # simulate an in-flight route
    await bot._route_event(et2, bot.event_tickers[et2], time.time())
    assert l2 not in bot.positions and u2 not in bot.positions, \
        "guard failed: routed while et2 already in _event_routing"
    bot._event_routing.discard(et2)
    print("[4]   PASS  reentrancy guard blocked concurrent route of same event")

    # --- 5: routing error is swallowed, never escapes on_bbo_update ---
    orig = bot._route_event
    async def _boom(*a, **k):
        raise RuntimeError("synthetic routing failure")
    bot._route_event = _boom
    try:
        await bot.on_bbo_update(l2)  # must NOT raise
    except Exception as e:
        raise AssertionError("on_bbo_update leaked an exception: %r" % e)
    finally:
        bot._route_event = orig
    print("[5]   PASS  on_bbo_update swallowed routing error (no reconnect trigger)")

    # --- 6: untracked ticker is a graceful no-op ---
    await bot.on_bbo_update("KXNOPE-DOESNOTEXIST-ZZZ")
    print("[6]   PASS  untracked ticker handled gracefully")

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
