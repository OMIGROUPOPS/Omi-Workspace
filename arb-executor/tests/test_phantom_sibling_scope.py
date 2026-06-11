#!/usr/bin/env python3
"""[C-BID-SURVIVAL DIFF-1] phantom-sibling scoping of the paired-basis guard.

KESMAR both-legs-live semantics unchanged; the Collarini 2026-06-11 12:41:19
frame (own 69c + phantom sibling ask 33c = 102 with ZERO sibling exposure,
sibling anchor-dead) now SURVIVES the T-20 evaluation; revival runs the guard
on real prices (over-cap -> decline placement, never retro-cancel the held
leg); the dead/engageable transition is evidence-monotone (no thrash).
Run: cd arb-executor && python3 tests/test_phantom_sibling_scope.py
"""
import sys, types, time, asyncio
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

def run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def book(bid, ask, lt_price=0, lt_age=1e9):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
        updated=time.time(), last_trade_price=lt_price,
        last_trade_ts=(time.time() - lt_age) if lt_price else 0.0)

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="ATP_CHALL",
                   direction="", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

BOUND = ("_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
         "_resting_cancel_reason", "_is_match_live", "_taker_spread_ok",
         "_fallback_order", "_reprice_target", "_completion_buffer_exempt",
         "_v4_manage_resting", "_v4_manage_resting_inner",
         "_cancel_entry_and_resolve", "_parse_entry_fill", "_book_v4_entry_fill",
         "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap", "_untombstone_entry")

def make_bot():
    s = types.SimpleNamespace()
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s._save_v4_resting = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0
    s.cancel_on_marketable = True; s.cancel_marketable_buffer = 1
    s.v4_fallback_sec = 1200
    s.fallback_maker_clamp = True; s.maker_only_entry = True
    s.completion_reprice = False; s.completion_disabled = False
    s.entry_table = {}
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: (10, "exit")
    s.exit_depth_floor = 0
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []; s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price,
                         "count": count, "post_only": post_only})
        return "OID_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

async def fake_api_get_clean(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return {"order": {"status": "canceled", "fill_count_fp": 0}}
    return {"orders": []}
M.api_get = fake_api_get_clean

def events(s, name): return [d for (e, d, t) in s.logs if e == name]

ET = "EV"; A = "EV-AAA"; Z = "EV-ZZZ"

# ---- 1. KESMAR both-legs-live UNCHANGED ----
s = make_bot(); s.event_tickers = {ET: {A, Z}}
s.positions = {Z: mk(Z, ET, entry_price=75, entry_order_id="z1", phase="entry_resting")}
s.books = {A: book(35, 38, lt_price=36, lt_age=60), Z: book(73, 76, lt_price=75, lt_age=60)}
check(s._paired_basis_ok(A, ET, 37) is False, "KESMAR: sibling RESTING@75 + this@37 = 112 -> refuse (unchanged)")
s.positions = {Z: mk(Z, ET, entry_price=45, entry_order_id="z1", phase="entry_resting")}
check(s._paired_basis_ok(A, ET, 40) is True, "KESMAR: 85<=99 -> allow (unchanged)")

# ---- 2. ENGAGEABLE sibling, no position: ask substitution still applies ----
s = make_bot(); s.event_tickers = {ET: {A, Z}}
s.books = {A: book(35, 38), Z: book(73, 76, lt_price=75, lt_age=300)}   # fresh print
check(s._paired_basis_ok(A, ET, 37) is False and len(events(s, "paired_basis_skip")) == 1,
      "engageable sibling (fresh print): phantom ask math unchanged -> refuse 113")

# ---- 3. DEAD sibling (Collarini frame): single-sided hold, guard passes ----
s = make_bot(); s.event_tickers = {ET: {A, Z}}
s.books = {A: book(68, 70, lt_price=69, lt_age=60), Z: book(31, 33, lt_price=32, lt_age=2400)}  # sibling print 40min old
check(s._paired_basis_ok(A, ET, 69) is True, "dead sibling (print>1800s): guard passes (69 single-sided)")
ssh_ = events(s, "single_sided_hold")
check(len(ssh_) == 1 and ssh_[0]["reason"] == "sibling_dead_no_position_no_fresh_print",
      "single_sided_hold NAMED with reason")
# dead sibling, no book at all
s.books.pop(Z)
check(s._paired_basis_ok(A, ET, 69) is True and len(events(s, "single_sided_hold")) == 2,
      "dead sibling (no book): named hold, passes")

# ---- 4. T-20 evaluation: Collarini bid SURVIVES (re-posts ask-1 fallback_maker, not killed) ----
s = make_bot(); s.event_tickers = {ET: {A, Z}}
now = time.time()
col = mk(A, ET, entry_price=66, entry_order_id="col1", phase="entry_resting", is_v4=True,
         target_price=66, entry_mode="resting_maker", match_start_ts=now + 1140)  # T-19
s.positions = {A: col}
s.books = {A: book(68, 70, lt_price=69, lt_age=60), Z: book(31, 33, lt_price=32, lt_age=2400)}
run(s._v4_manage_resting_inner(A, col, s.books[A], now))
check(not any(c["label"] == "paired_basis_no_fallback" for c in s.cancelled),
      "T-20 eval, dead sibling: NO paired_basis_no_fallback kill (old code killed here)")
check(any(p["tk"] == A and p["post_only"] for p in s.placed) and col.entry_order_id.startswith("OID_"),
      "bid SURVIVES as ask-1 maker re-post (fallback_maker) -- replace, not silence")
check(col.entry_mode == "fallback_maker", "leg continues as fallback_maker")

# ---- 5. REVIVAL: fresh print arrives -> guard runs on REAL prices ----
s = make_bot(); s.event_tickers = {ET: {A, Z}}
held = mk(A, ET, entry_price=69, entry_qty=5, phase="active", is_v4=True)
s.positions = {A: held}
s.books = {A: book(68, 70), Z: book(31, 33, lt_price=32, lt_age=120)}   # revived
# entering Z at 32 vs held A cost 69: combined 101 > 99 -> refuse, named
s.logs.clear()
ok = s._paired_basis_ok(Z, ET, 32)
check(ok is False and len(events(s, "paired_basis_skip")) == 1,
      "revival over-cap: placement DECLINED (named paired_basis_skip)")
check(not s.cancelled, "revival over-cap: held leg NEVER retroactively cancelled")
ok2 = s._paired_basis_ok(Z, ET, 29)
check(ok2 is True, "revival under-cap (29+69=98): placement allowed on real prices")

# ---- 6. Transition non-thrash: monotone in evidence ----
s = make_bot()
s.books = {Z: book(31, 33, lt_price=32, lt_age=1799)}
check(s._sibling_engageable(Z) is True, "age 1799s -> engageable")
s.books = {Z: book(31, 33, lt_price=32, lt_age=1801)}
check(s._sibling_engageable(Z) is False, "age 1801s -> dead (boundary at the 1800s anchor constant)")
r1 = s._sibling_engageable(Z); r2 = s._sibling_engageable(Z)
check(r1 == r2 is False, "same evidence -> same answer (no thrash within a cycle)")
s.books[Z].last_trade_ts = time.time() - 10   # new print = added evidence
check(s._sibling_engageable(Z) is True, "new print -> engageable (monotone in evidence)")
# resting sibling bid = engageable regardless of prints
s.books = {Z: book(31, 33)}
s.positions = {Z: mk(Z, "EV", entry_price=31, entry_order_id="z9", phase="entry_resting")}
check(s._sibling_engageable(Z) is True, "live resting sibling bid -> engageable")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
