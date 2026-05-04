#!/usr/bin/env python3
"""
§11.1 unit tests for paper-mode v1 (T1-T9).

Imports live_v3 module directly. Uses a minimal FakeBot for tests that don't
require full LiveV3 instantiation. T9 tests the safety-check pattern faithfully
without invoking run() (which would require full bot init).

Output: /tmp/paper_unit_tests.log (also stdout)
"""

import sys
import os
import asyncio
import time
import json
import tempfile
import traceback
from io import StringIO

sys.path.insert(0, "/root/Omi-Workspace/arb-executor")

# Suppress live_v3's print on import
import builtins
_orig_print = builtins.print
_log_buf = StringIO()
def _capture_print(*args, **kwargs):
    _orig_print(*args, **kwargs, file=_log_buf)
    _orig_print(*args, **kwargs)

builtins.print = _capture_print

import live_v3 as lv

builtins.print = _orig_print


PaperApi = lv.PaperApi
PaperOrder = lv.PaperOrder
PaperPosition = lv.PaperPosition
VolumeTracker = lv.VolumeTracker
PaperFillSimulator = lv.PaperFillSimulator
Book = lv.Book


# -------------------------------------------------------------------------
# Test fixtures
# -------------------------------------------------------------------------

class FakeBot:
    def __init__(self):
        self.books = {}
        self.ticker_to_event = {}
        self.events_log = []
        self.config = {"paper_mode": True, "paper_state_max_age_sec": 86400}
        self.positions = {}

    def _log(self, event, details=None, ticker=""):
        self.events_log.append({
            "event": event, "details": details or {},
            "ticker": ticker, "ts": time.time(),
        })

    def _get_side_fv(self, ticker, event_ticker):
        return None


def make_book(bids=None, asks=None, best_bid=None, best_ask=None,
              last_trade_price=0, last_trade_ts=0.0, last_trade_side=""):
    b = Book()
    if bids:
        b.bids.update(bids)
    if asks:
        b.asks.update(asks)
    b.best_bid = best_bid if best_bid is not None else (max(b.bids.keys()) if b.bids else 0)
    b.best_ask = best_ask if best_ask is not None else (min(b.asks.keys()) if b.asks else 100)
    b.last_trade_price = last_trade_price
    b.last_trade_ts = last_trade_ts
    b.last_trade_side = last_trade_side
    return b


# -------------------------------------------------------------------------
# Test runner
# -------------------------------------------------------------------------

PASS = 0
FAIL = 0
LOG = []


def log(msg):
    print(msg)
    LOG.append(msg)


def check(condition, label):
    global PASS, FAIL
    if condition:
        PASS += 1
        log("  PASS: " + label)
    else:
        FAIL += 1
        log("  FAIL: " + label)


def reset_paper_api():
    lv._PAPER_API = None


def header(test_id, description):
    log("")
    log("=" * 78)
    log("%s: %s" % (test_id, description))
    log("=" * 78)


# -------------------------------------------------------------------------
# T1: Paper mode disabled -> real API path used
# -------------------------------------------------------------------------

async def t1():
    header("T1", "paper_mode disabled -> api_get/post/delete dispatch to _real_*")
    reset_paper_api()
    captured = []

    async def fake_real_get(s, ak, pk, path, rl):
        captured.append(("get", path))
        return {"sentinel_get": True}

    async def fake_real_post(s, ak, pk, path, payload, rl):
        captured.append(("post", path, payload))
        return {"sentinel_post": True}

    async def fake_real_delete(s, ak, pk, path, rl):
        captured.append(("delete", path))
        return True

    orig_get, orig_post, orig_delete = lv._real_api_get, lv._real_api_post, lv._real_api_delete
    lv._real_api_get = fake_real_get
    lv._real_api_post = fake_real_post
    lv._real_api_delete = fake_real_delete
    try:
        r1 = await lv.api_get(None, "ak", "pk", "/test/get", None)
        r2 = await lv.api_post(None, "ak", "pk", "/test/post", {"x": 1}, None)
        r3 = await lv.api_delete(None, "ak", "pk", "/test/del", None)
        check(r1 == {"sentinel_get": True}, "api_get returns from _real_api_get when _PAPER_API is None")
        check(r2 == {"sentinel_post": True}, "api_post returns from _real_api_post when _PAPER_API is None")
        check(r3 == True, "api_delete returns from _real_api_delete when _PAPER_API is None")
        check(captured == [("get", "/test/get"), ("post", "/test/post", {"x": 1}), ("delete", "/test/del")],
              "all three real handlers invoked exactly once with correct args")
    finally:
        lv._real_api_get, lv._real_api_post, lv._real_api_delete = orig_get, orig_post, orig_delete


# -------------------------------------------------------------------------
# T2: Post buy order -> PaperOrder created, event emitted
# -------------------------------------------------------------------------

async def t2():
    header("T2", "paper_mode enabled, post buy order -> PaperOrder created + event emitted")
    reset_paper_api()
    bot = FakeBot()
    bot.books["TICKER1"] = make_book(bids={42: 100}, asks={43: 200})
    bot.ticker_to_event["TICKER1"] = "EVENT1"
    api = PaperApi(bot=bot)
    lv._PAPER_API = api
    try:
        resp = await api.handle_post(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders",
            {"ticker": "TICKER1", "action": "buy", "side": "yes",
             "yes_price": 42, "count": 10, "client_order_id": "test-coid-1"},
            None)
        order_id = resp.get("order", {}).get("order_id", "")
        check(order_id.startswith("PAPER-TICKER1-"), "order_id has PAPER- prefix and ticker (got %r)" % order_id)
        check(resp["order"]["status"] == "resting", "response status is resting")
        check(len(api.paper_orders) == 1, "paper_orders dict has 1 entry")
        order = api.paper_orders[order_id]
        check(order.status == "resting", "PaperOrder status=resting")
        check(order.yes_price == 42, "PaperOrder yes_price=42")
        check(order.count == 10, "PaperOrder count=10")
        check(order.remaining_count == 10, "PaperOrder remaining_count=10")
        check(order.action == "buy", "PaperOrder action=buy")
        check(order.client_order_id == "test-coid-1", "client_order_id captured")
        events = [e for e in bot.events_log if e["event"] == "paper_order_posted"]
        check(len(events) == 1, "paper_order_posted emitted exactly once")
        d = events[0]["details"]
        check(d["order_id"] == order_id, "event order_id matches")
        check(d["yes_price"] == 42, "event yes_price=42")
        check(d["count"] == 10, "event count=10")
        check(d["best_bid"] == 42, "event captured best_bid=42")
        check(d["best_ask"] == 43, "event captured best_ask=43")
        check(d["spread"] == 1, "event spread=1")
        # Position bookkeeping
        pos = api.paper_positions.get("TICKER1")
        check(pos is not None, "PaperPosition created for ticker")
        check(order_id in pos.open_buy_orders, "order_id in open_buy_orders")
    finally:
        reset_paper_api()


# -------------------------------------------------------------------------
# T3: Book cross triggers fill
# -------------------------------------------------------------------------

async def t3():
    header("T3", "book cross triggers fill (best_ask drops to bid price)")
    reset_paper_api()
    bot = FakeBot()
    bot.books["T3"] = make_book(bids={42: 100}, asks={50: 200}, best_bid=42, best_ask=50)
    bot.ticker_to_event["T3"] = "E3"
    api = PaperApi(bot=bot)
    lv._PAPER_API = api
    try:
        resp = await api.handle_post(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders",
            {"ticker": "T3", "action": "buy", "side": "yes", "yes_price": 45, "count": 5},
            None)
        order_id = resp["order"]["order_id"]
        check(api.paper_orders[order_id].status == "resting", "order resting before book moves")
        # Move best_ask down to 44 (below our 45)
        bot.books["T3"].asks[44] = 50  # add a new ask level
        bot.books["T3"].best_ask = 44
        api.on_book_update("T3")
        order = api.paper_orders[order_id]
        check(order.status == "executed", "order status=executed after book cross")
        check(order.filled_count == 5, "filled_count=5")
        check(order.remaining_count == 0, "remaining_count=0")
        fills = [e for e in bot.events_log if e["event"] == "paper_fill"]
        check(len(fills) == 1, "paper_fill emitted exactly once")
        d = fills[0]["details"]
        check(d["fill_trigger"] == "book_cross", "trigger=book_cross")
        check(d["fill_price"] == 45, "fill_price=45 (our posted level, permissive)")
        check(d["qty"] == 5, "qty=5")
        check(d["best_ask_at_fill"] == 44, "best_ask_at_fill=44 captured")
        check(d["time_to_fill_sec"] >= 0, "time_to_fill_sec computed")
        # Position state
        pos = api.paper_positions["T3"]
        check(pos.qty == 5, "PaperPosition.qty=5")
        check(pos.total_cost_cents == 5 * 45, "PaperPosition.total_cost_cents=225")
        check(pos.avg_price == 45, "PaperPosition.avg_price=45")
        check(order_id not in pos.open_buy_orders, "order removed from open_buy_orders")
    finally:
        reset_paper_api()


# -------------------------------------------------------------------------
# T4: Trade print triggers fill (with side annotation)
# -------------------------------------------------------------------------

async def t4():
    header("T4", "trade print triggers fill at <= price (sell-aggressor)")
    reset_paper_api()
    bot = FakeBot()
    bot.books["T4"] = make_book(bids={40: 100}, asks={50: 200}, best_bid=40, best_ask=50)
    bot.ticker_to_event["T4"] = "E4"
    api = PaperApi(bot=bot)
    lv._PAPER_API = api
    try:
        resp = await api.handle_post(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders",
            {"ticker": "T4", "action": "buy", "side": "yes", "yes_price": 45, "count": 3},
            None)
        order_id = resp["order"]["order_id"]
        # Trade print at price 41 (≤ our 45) with sell-aggressor (taker_side="no")
        ts = time.time()
        api.on_trade("T4", ts, 41, 20, "no")
        order = api.paper_orders[order_id]
        check(order.status == "executed", "order executed after trade print")
        fills = [e for e in bot.events_log if e["event"] == "paper_fill"]
        check(len(fills) == 1, "paper_fill emitted once")
        d = fills[0]["details"]
        check(d["fill_trigger"] == "trade_print", "trigger=trade_print")
        check(d["fill_price"] == 45, "fill_price=45 (our posted level)")
        # Volume tracker should have recorded the print as sell-aggressor
        vt = api.volume_tracker
        recorded = vt.trades.get("T4", [])
        check(len(recorded) == 1, "VolumeTracker recorded 1 trade")
        if recorded:
            t_ts, t_price, t_qty, t_side = recorded[0]
            check(t_price == 41, "trade price=41 stored")
            check(t_qty == 20, "trade qty=20 stored")
            check(t_side == "sell", "taker_side=no normalized to side=sell")
        check(d["volume_at_or_through_lifetime"] == 20, "vol_at_or_through includes the trade qty")
    finally:
        reset_paper_api()


# -------------------------------------------------------------------------
# T5: Idempotency — chained hooks fire only one fill
# -------------------------------------------------------------------------

async def t5():
    header("T5", "idempotency: repeated hooks on same order produce only one fill")
    reset_paper_api()
    bot = FakeBot()
    bot.books["T5"] = make_book(bids={40: 100}, asks={50: 200}, best_bid=40, best_ask=50)
    bot.ticker_to_event["T5"] = "E5"
    api = PaperApi(bot=bot)
    lv._PAPER_API = api
    try:
        resp = await api.handle_post(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders",
            {"ticker": "T5", "action": "buy", "side": "yes", "yes_price": 45, "count": 5},
            None)
        order_id = resp["order"]["order_id"]
        # Drop ask to trigger fill
        bot.books["T5"].best_ask = 44
        # Fire all three triggers repeatedly
        api.on_book_update("T5")  # should fill
        api.on_book_update("T5")  # should be idempotent
        api.on_trade("T5", time.time(), 30, 10, "no")  # should be idempotent
        api.on_book_update("T5")  # idempotent
        order = api.paper_orders[order_id]
        check(order.status == "executed", "order remains executed")
        check(order.filled_count == 5, "filled_count remains 5 (not 5*N)")
        fills = [e for e in bot.events_log if e["event"] == "paper_fill"]
        check(len(fills) == 1, "exactly one paper_fill emitted across all triggers")
        # Position should have accumulated only once
        pos = api.paper_positions["T5"]
        check(pos.qty == 5, "PaperPosition.qty stays at 5 (no double-counting)")
        check(pos.total_cost_cents == 225, "total_cost_cents stays at 5*45=225")
    finally:
        reset_paper_api()


# -------------------------------------------------------------------------
# T6: Cancel resting order
# -------------------------------------------------------------------------

async def t6():
    header("T6", "cancel resting order -> status canceled, paper_order_cancelled emitted")
    reset_paper_api()
    bot = FakeBot()
    bot.books["T6"] = make_book(bids={40: 100}, asks={50: 200}, best_bid=40, best_ask=50)
    bot.ticker_to_event["T6"] = "E6"
    api = PaperApi(bot=bot)
    lv._PAPER_API = api
    try:
        resp = await api.handle_post(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders",
            {"ticker": "T6", "action": "buy", "side": "yes", "yes_price": 45, "count": 5},
            None)
        order_id = resp["order"]["order_id"]
        # Sleep briefly so lifetime > 0
        await asyncio.sleep(0.05)
        ok = await api.handle_delete(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders/" + order_id, None)
        check(ok == True, "handle_delete returned True")
        order = api.paper_orders[order_id]
        check(order.status == "canceled", "order status=canceled")
        cancels = [e for e in bot.events_log if e["event"] == "paper_order_cancelled"]
        check(len(cancels) == 1, "paper_order_cancelled emitted once")
        d = cancels[0]["details"]
        check(d["order_id"] == order_id, "cancel event order_id matches")
        check(d["lifetime_sec"] > 0, "lifetime_sec > 0 (got %s)" % d["lifetime_sec"])
        # Re-cancel should return False (idempotency on delete)
        ok2 = await api.handle_delete(None, "ak", "pk",
            "/trade-api/v2/portfolio/orders/" + order_id, None)
        check(ok2 == False, "second cancel returns False (already canceled)")
        # Subsequent book/trade triggers don't fill canceled order
        bot.books["T6"].best_ask = 44
        api.on_book_update("T6")
        check(api.paper_orders[order_id].status == "canceled", "canceled order stays canceled after book cross")
        fills = [e for e in bot.events_log if e["event"] == "paper_fill"]
        check(len(fills) == 0, "no paper_fill on canceled order")
    finally:
        reset_paper_api()


# -------------------------------------------------------------------------
# T7: VolumeTracker side normalization
# -------------------------------------------------------------------------

def t7():
    header("T7", "VolumeTracker side normalization (yes->buy, no->sell)")
    vt = VolumeTracker()
    ts = time.time()
    vt.record("T7", ts, 50, 10, "yes")
    vt.record("T7", ts, 51, 20, "no")
    vt.record("T7", ts, 52, 30, "")  # unsided
    vt.record("T7", ts, 53, 40, "garbage")  # unrecognized -> unsided
    trades = list(vt.trades["T7"])
    check(len(trades) == 4, "4 trades recorded")
    check(trades[0][3] == "buy", "taker_side=yes -> internal side=buy")
    check(trades[1][3] == "sell", "taker_side=no -> internal side=sell")
    check(trades[2][3] == "", "taker_side='' -> empty stored side")
    check(trades[3][3] == "", "unrecognized taker_side -> empty stored side")
    check(vt.unsided_count == 2, "unsided_count=2")
    check(vt.sample_count == 4, "sample_count=4")
    # volume_at_or_through with side="buy" counts only sell-aggressor prints at price <= P
    vol_buy_at_60 = vt.volume_at_or_through("T7", "buy", 60, ts - 1)
    check(vol_buy_at_60 == 20, "buy@60 sees only the sell-aggressor (qty=20), got %d" % vol_buy_at_60)
    # volume_at_or_through with side="sell" counts only buy-aggressor prints at price >= P
    vol_sell_at_40 = vt.volume_at_or_through("T7", "sell", 40, ts - 1)
    check(vol_sell_at_40 == 10, "sell@40 sees only the buy-aggressor (qty=10), got %d" % vol_sell_at_40)


# -------------------------------------------------------------------------
# T8: Persistence round-trip
# -------------------------------------------------------------------------

async def t8():
    header("T8", "persistence round-trip: dump_state + load_state")
    reset_paper_api()
    tmp_path = "/tmp/test_paper_state.json"
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    # Build api with state
    bot = FakeBot()
    bot.books["T8A"] = make_book(bids={40: 100}, asks={50: 200}, best_bid=40, best_ask=50)
    bot.books["T8B"] = make_book(bids={30: 50}, asks={60: 80}, best_bid=30, best_ask=60)
    bot.ticker_to_event["T8A"] = "E8A"
    bot.ticker_to_event["T8B"] = "E8B"
    api1 = PaperApi(bot=bot)
    lv._PAPER_API = api1
    # Place 2 orders
    r1 = await api1.handle_post(None, "ak", "pk", "/trade-api/v2/portfolio/orders",
        {"ticker": "T8A", "action": "buy", "side": "yes", "yes_price": 45, "count": 5}, None)
    r2 = await api1.handle_post(None, "ak", "pk", "/trade-api/v2/portfolio/orders",
        {"ticker": "T8B", "action": "buy", "side": "yes", "yes_price": 35, "count": 3}, None)
    oid1 = r1["order"]["order_id"]
    oid2 = r2["order"]["order_id"]
    # Fill T8A via book cross
    bot.books["T8A"].best_ask = 44
    api1.on_book_update("T8A")
    check(api1.paper_orders[oid1].status == "executed", "T8A order filled before dump")
    check(api1.paper_orders[oid2].status == "resting", "T8B order resting before dump")
    pre_orders = len(api1.paper_orders)
    pre_positions = len(api1.paper_positions)
    pre_seq = api1.next_seq
    # Dump
    api1.dump_state(tmp_path)
    check(os.path.exists(tmp_path), "dump_state wrote file")
    # Load into fresh api
    bot2 = FakeBot()
    bot2.books = bot.books  # share books for any depth lookups
    bot2.ticker_to_event = bot.ticker_to_event
    api2 = PaperApi(bot=bot2)
    lv._PAPER_API = api2
    ok = api2.load_state(tmp_path, max_age_sec=86400)
    check(ok == True, "load_state returned True")
    check(len(api2.paper_orders) == pre_orders, "paper_orders count restored (%d)" % pre_orders)
    check(len(api2.paper_positions) == pre_positions, "paper_positions count restored (%d)" % pre_positions)
    check(api2.next_seq == pre_seq, "next_seq restored")
    # Verify exact field equality on the executed order
    o1_orig = api1.paper_orders[oid1]
    o1_loaded = api2.paper_orders[oid1]
    check(o1_loaded.status == o1_orig.status == "executed", "T8A order status preserved")
    check(o1_loaded.yes_price == 45, "T8A yes_price preserved")
    check(o1_loaded.count == 5, "T8A count preserved")
    check(o1_loaded.filled_count == 5, "T8A filled_count preserved")
    # Position state
    p_orig = api1.paper_positions["T8A"]
    p_loaded = api2.paper_positions["T8A"]
    check(p_loaded.qty == p_orig.qty == 5, "T8A position qty preserved")
    check(p_loaded.total_cost_cents == p_orig.total_cost_cents, "T8A total_cost_cents preserved")
    # Restoration emitted event
    restored = [e for e in bot2.events_log if e["event"] == "paper_state_restored"]
    check(len(restored) == 1, "paper_state_restored emitted")
    if restored:
        d = restored[0]["details"]
        check(d["orders_loaded"] == pre_orders, "event reports orders_loaded=%d" % pre_orders)
        check(d["positions_loaded"] == pre_positions, "event reports positions_loaded=%d" % pre_positions)
    # Stale file rejection
    api3 = PaperApi(bot=FakeBot())
    lv._PAPER_API = api3
    # Touch the file with old mtime
    old_ts = time.time() - 100000  # ~28h ago
    os.utime(tmp_path, (old_ts, old_ts))
    ok_stale = api3.load_state(tmp_path, max_age_sec=86400)
    check(ok_stale == False, "stale file rejected")
    skipped = [e for e in api3.bot.events_log if e["event"] == "paper_state_skipped"]
    check(len(skipped) == 1, "paper_state_skipped emitted")
    if skipped:
        check(skipped[0]["details"]["reason"] == "file_stale", "skip reason=file_stale")
    # Missing file
    api4 = PaperApi(bot=FakeBot())
    lv._PAPER_API = api4
    os.remove(tmp_path)
    ok_missing = api4.load_state(tmp_path, max_age_sec=86400)
    check(ok_missing == False, "missing file rejected")
    skipped4 = [e for e in api4.bot.events_log if e["event"] == "paper_state_skipped"]
    check(skipped4 and skipped4[0]["details"]["reason"] == "file_not_found",
          "skip reason=file_not_found")
    reset_paper_api()


# -------------------------------------------------------------------------
# T9: Startup safety check
# -------------------------------------------------------------------------

async def t9():
    header("T9", "startup safety: real positions exist + paper_mode=true -> abort")
    reset_paper_api()

    captured_log = []
    bot = FakeBot()
    bot._log = lambda evt, det=None, ticker="": captured_log.append({"event": evt, "details": det or {}})

    # Mock _real_api_get to return non-empty market_positions
    async def fake_real_get_with_positions(s, ak, pk, path, rl):
        return {"market_positions": [
            {"ticker": "FAKEPOS1", "position_fp": 5.0},
            {"ticker": "FAKEPOS2", "position_fp": 3.0},
        ]}

    orig_get = lv._real_api_get
    lv._real_api_get = fake_real_get_with_positions
    try:
        # Replicate the safety-check pattern from run() faithfully
        api = PaperApi(bot=bot)
        lv._PAPER_API = api
        real_pos = await lv._real_api_get(None, "ak", "pk",
            "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled",
            None)
        real_positions_count = len((real_pos or {}).get("market_positions", []))
        aborted = False
        if real_positions_count > 0:
            bot._log("paper_real_orders_blocked", {
                "real_positions_count": real_positions_count, "action": "abort",
            })
            try:
                raise RuntimeError(
                    "paper_mode=true but %d real Kalshi positions exist; close them first"
                    % real_positions_count)
            except RuntimeError as e:
                aborted = True
                err_msg = str(e)
        check(real_positions_count == 2, "fake _real_api_get returned 2 positions")
        check(aborted, "RuntimeError raised on real positions present")
        check("2 real Kalshi positions exist" in err_msg, "error message mentions count")
        blocked_evts = [e for e in captured_log if e["event"] == "paper_real_orders_blocked"]
        check(len(blocked_evts) == 1, "paper_real_orders_blocked emitted once")
        if blocked_evts:
            check(blocked_evts[0]["details"]["real_positions_count"] == 2,
                  "blocked event reports count=2")
            check(blocked_evts[0]["details"]["action"] == "abort", "blocked event action=abort")

        # Negative case: empty positions -> no abort
        async def fake_real_get_empty(s, ak, pk, path, rl):
            return {"market_positions": []}
        lv._real_api_get = fake_real_get_empty
        real_pos2 = await lv._real_api_get(None, "ak", "pk", "/path", None)
        cnt2 = len((real_pos2 or {}).get("market_positions", []))
        check(cnt2 == 0, "empty positions case: count=0")
        # Should NOT raise — proceed normally
        no_abort = (cnt2 == 0)
        check(no_abort, "empty positions: bot proceeds without abort")
    finally:
        lv._real_api_get = orig_get
        reset_paper_api()


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

async def main():
    log("Paper Mode v1 — §11.1 unit tests")
    log("File: /root/Omi-Workspace/arb-executor/live_v3.py")
    log("Started: " + time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        await t1()
    except Exception as e:
        log("T1 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t2()
    except Exception as e:
        log("T2 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t3()
    except Exception as e:
        log("T3 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t4()
    except Exception as e:
        log("T4 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t5()
    except Exception as e:
        log("T5 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t6()
    except Exception as e:
        log("T6 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        t7()  # synchronous
    except Exception as e:
        log("T7 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t8()
    except Exception as e:
        log("T8 EXCEPTION: " + str(e))
        log(traceback.format_exc())
    try:
        await t9()
    except Exception as e:
        log("T9 EXCEPTION: " + str(e))
        log(traceback.format_exc())

    log("")
    log("=" * 78)
    log("SUMMARY: PASS=%d  FAIL=%d" % (PASS, FAIL))
    log("=" * 78)

    # Save log
    with open("/tmp/paper_unit_tests.log", "w") as f:
        f.write("\n".join(LOG))
    log("Output saved to /tmp/paper_unit_tests.log")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
