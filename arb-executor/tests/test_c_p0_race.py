#!/usr/bin/env python3
"""[C-P0-RACE] Cancel/fill race fix — full test burden.

Covers: the three resolve branches (full-fill race / partial+cancel-success /
partial+cancel-failure / clean cancel / ambiguous), booking idempotency on
order_id, helper-level concurrency (Plex Gate 3), T2 byte-identical no-race
semantics at the swapped sites, T4 adversarial (cap arithmetic, full-fill
equivalence), T5 live-evidence regression (the 2026-06-11 AUGFUC scenario:
adopted/raced 69c Auger-Aliassime leg + resting 29-31c Fucsovics sibling ->
cap violation detected, sibling cancelled, never an exposed pair), and
STEP 5/6 adoption booking + completion_booking_adoption V5 contexts.

Run: cd arb-executor && python3 tests/test_c_p0_race.py
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
    return asyncio.new_event_loop().run_until_complete(coro)

# ---- routable api_get stub --------------------------------------------------
# POLL_QUEUE: list of responses for successive get-order polls (None = API failure).
POLL_QUEUE = []
async def _fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return POLL_QUEUE.pop(0) if POLL_QUEUE else None
    if "orders?ticker=" in path or "status=resting" in path:
        return {"orders": []}
    if "/portfolio/fills" in path:
        return {"fills": []}
    return {}
M.api_get = _fake_api_get

def order_resp(filled, status="executed", avg=None):
    o = {"fill_count_fp": filled, "status": status}
    if avg is not None:
        o["average_fill_price_fp"] = avg
    return {"order": o}

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
                                 last_trade_price=0, last_trade_ts=0.0)

def make_pos(tk, et="EV", cat="ATP_MAIN", **kw):
    return M.Position(ticker=tk, event_ticker=et, category=cat,
                      direction="", cell_name="", cell_cfg={}, **kw)

BOUND = ("_sibling_ticker", "_paired_basis_ok", "_cancel_sibling_if_paired_over_cap",
         "_cancel_entry_and_resolve", "_parse_entry_fill", "_book_v4_entry_fill",
         "_v4_apply_exit", "_untombstone_entry", "_is_match_live",
         "_resting_cancel_reason", "_v4_manage_resting", "_v4_manage_resting_inner",
         "_v4_reconcile_naked", "_fill_is_taker", "_completion_fill_guards")

def make_bot(cancel_ok=True, completion=False, band=(29, "exit")):
    s = types.SimpleNamespace()
    s.completion_reprice = completion
    s.completion_disabled = False
    s.completion_cells = {}
    s._window_open = {}
    s.positions = {}
    s.books = {}
    s.event_tickers = {}
    s.ticker_to_event = {}
    s.event_start_time = {}
    s.inflight_orders = set()
    s._mgmt_inflight = set()
    s._booking_inflight = set()
    s._events_live = set()
    s._trade_times = {}
    s.entry_size = 5
    s.n_entries = 0
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.processed_events = set()
    s._save_processed = lambda: None
    s._save_v4_resting = lambda: None
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: band
    s.exit_depth_floor = 0
    s.cancel_on_marketable = True
    s.cancel_marketable_buffer = 1
    s.v4_fallback_sec = 1200
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []
    s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price, "count": count})
        return "OID_NEW_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return s.cancel_ok
    s.cancel_ok = cancel_ok
    s.cancel_order = cancel_order
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

def events(s, name):
    return [d for (e, d, t) in s.logs if e == name]

# ============================================================================
# SECTION 1 — _cancel_entry_and_resolve three branches (STEP 3 / T3)
# ============================================================================
print("--- resolve branches ---")

# 1a. FULL-FILL RACE: cancel fails, poll shows full fill -> booked
s = make_bot(cancel_ok=False)
p = make_pos("T-A", entry_price=69, entry_order_id="OID1", phase="entry_resting", is_v4=True)
s.positions["T-A"] = p
POLL_QUEUE[:] = [order_resp(5, "executed", 0.69)]
res = run(s._cancel_entry_and_resolve("T-A", p, "v4_cancel_bid_marketable_stale", "manage_cancel_race"))
check(res == "booked", "full-fill race -> 'booked'")
check(p.entry_qty == 5 and p.phase == "active", "raced fill state booked (qty 5, active)")
check(len(events(s, "entry_filled")) == 1 and events(s, "entry_filled")[0]["source"] == "manage_cancel_race",
      "entry_filled emitted with race source")
check(len(events(s, "cancel_fill_race")) == 1, "cancel_fill_race evidence event emitted")
check(s.placed and s.placed[0]["action"] == "sell" and s.placed[0]["price"] == 98 and s.placed[0]["count"] == 5,
      "exit posted at min(69+29,cap)=98 sized to fill")

# 1b. PARTIAL FILL + CANCEL SUCCESS -> books the filled qty
s = make_bot(cancel_ok=True)
p = make_pos("T-B", entry_price=40, entry_order_id="OID2", phase="entry_resting", is_v4=True)
s.positions["T-B"] = p
POLL_QUEUE[:] = [order_resp(2, "canceled", 0.40)]
res = run(s._cancel_entry_and_resolve("T-B", p, "x", "y"))
check(res == "booked" and p.entry_qty == 2 and p.phase == "active",
      "partial+cancel-success -> books filled qty 2")
check(s.placed and s.placed[0]["count"] == 2, "exit sized to partial qty 2")

# 1c. PARTIAL FILL + CANCEL FAILURE -> books the filled qty
s = make_bot(cancel_ok=False)
p = make_pos("T-C", entry_price=40, entry_order_id="OID3", phase="entry_resting", is_v4=True)
s.positions["T-C"] = p
POLL_QUEUE[:] = [order_resp(3, "executed", 0.40)]
res = run(s._cancel_entry_and_resolve("T-C", p, "x", "y"))
check(res == "booked" and p.entry_qty == 3, "partial+cancel-failure -> books filled qty 3")

# 1d. CLEAN CANCEL, NO FILL -> 'cancelled' (caller deletes per existing discipline)
s = make_bot(cancel_ok=True)
p = make_pos("T-D", entry_price=40, entry_order_id="OID4", phase="entry_resting", is_v4=True)
s.positions["T-D"] = p
POLL_QUEUE[:] = [order_resp(0, "canceled")]
res = run(s._cancel_entry_and_resolve("T-D", p, "x", "y"))
check(res == "cancelled" and p.entry_qty == 0 and p.phase == "entry_resting",
      "clean cancel -> 'cancelled', position untouched (caller's discipline)")
check(not events(s, "entry_filled"), "no entry_filled on clean cancel")

# 1e. AMBIGUOUS: poll fails twice -> 'unresolved', NEVER delete
s = make_bot(cancel_ok=False)
p = make_pos("T-E", entry_price=40, entry_order_id="OID5", phase="entry_resting", is_v4=True)
s.positions["T-E"] = p
POLL_QUEUE[:] = [None, None]
res = run(s._cancel_entry_and_resolve("T-E", p, "x", "y"))
check(res == "unresolved" and "T-E" in s.positions and p.entry_order_id == "OID5",
      "ambiguous -> 'unresolved', position + order_id kept for retry")
check(len(events(s, "cancel_resolve_unresolved")) == 1, "unresolved evidence event emitted")

# 1f. no order id -> 'cancelled' passthrough
s = make_bot()
p = make_pos("T-F", entry_price=40, entry_order_id="", phase="entry_resting", is_v4=True)
res = run(s._cancel_entry_and_resolve("T-F", p, "x", "y"))
check(res == "cancelled" and not s.cancelled, "no order_id -> 'cancelled' without exchange call")

# ============================================================================
# SECTION 2 — _book_v4_entry_fill idempotency + concurrency (STEP 2 / Gate 3)
# ============================================================================
print("--- booking idempotency / concurrency ---")

# 2a. double booking attempt: second call same order+count no-ops
s = make_bot()
p = make_pos("T-G", entry_price=50, entry_order_id="OIDG", phase="entry_resting", is_v4=True)
s.positions["T-G"] = p
r1 = run(s._book_v4_entry_fill("T-G", p, 5, 50, "executed"))
r2 = run(s._book_v4_entry_fill("T-G", p, 5, 50, "executed"))
check(r1 is True and r2 is False, "idempotent: second booking of same order/count no-ops")
check(s.n_entries == 1 and len(events(s, "entry_filled")) == 1, "n_entries and entry_filled counted once")

# 2b. incremental partial booking: 2 then 5 books new_fills 3, exit re-sized
s = make_bot()
p = make_pos("T-H", entry_price=50, entry_order_id="OIDH", phase="entry_resting", is_v4=True)
s.positions["T-H"] = p
run(s._book_v4_entry_fill("T-H", p, 2, 50, "executed"))
run(s._book_v4_entry_fill("T-H", p, 5, 50, "executed"))
efs = events(s, "entry_filled")
check(len(efs) == 2 and efs[1]["new_fills"] == 3 and p.entry_qty == 5,
      "incremental booking: 2 then +3, qty 5")
check(s.n_entries == 1, "n_entries counts first fill only")
check(s.placed[-1]["count"] == 5, "exit re-sized to total filled qty")

# 2c. CONCURRENT booking attempts: exactly one books (inflight guard on the tail)
s = make_bot()
p = make_pos("T-I", entry_price=50, entry_order_id="OIDI", phase="entry_resting", is_v4=True)
s.positions["T-I"] = p
tail_entered = []
async def slow_exit(tk, pos, fp, q):
    tail_entered.append(tk)
    await asyncio.sleep(0.05)   # hold the awaited tail open
s._v4_apply_exit = slow_exit
async def concurrent():
    return await asyncio.gather(
        s._book_v4_entry_fill("T-I", p, 5, 50, "executed"),
        s._book_v4_entry_fill("T-I", p, 5, 50, "executed"))
r = run(concurrent())
check(sorted(r) == [False, True], "concurrent booking: exactly one books, other no-ops")
check(len(tail_entered) == 1 and s.n_entries == 1 and len(events(s, "entry_filled")) == 1,
      "awaited tail entered exactly once (per-order_id guard)")
check(not s._booking_inflight, "inflight guard released after booking")

# 2d. check->write segment is await-free (Gate-3 citation, asserted structurally)
import inspect, re as _re
src = inspect.getsource(M.LiveV3._book_v4_entry_fill)
seg = src.split("await-free check->write segment")[1].split("---- awaited tail")[0]
check("await " not in seg, "no await between idempotency check and state writes (cited segment)")

# ============================================================================
# SECTION 3 — T2 byte-identical NO-RACE behavior at swapped sites
# ============================================================================
print("--- T2 no-race byte-identical ---")

# 3a. manage-path marketable-stale clean cancel: same event + deletion as pre-fix
s = make_bot(cancel_ok=True)
p = make_pos("T-J", et="EVJ", entry_price=69, entry_order_id="OIDJ",
             phase="entry_resting", is_v4=True, target_price=69, entry_mode="resting_maker")
p.match_start_ts = time.time() + 99999
s.positions["T-J"] = p
s.processed_events = {"EVJ"}
POLL_QUEUE[:] = [order_resp(0, "canceled")]
run(s._v4_manage_resting_inner("T-J", p, book(69, 70), time.time()))
vc = events(s, "v4_resting_cancel")
check(len(vc) == 1 and vc[0]["reason"] == "bid_marketable_stale"
      and vc[0]["spread"] == 1 and vc[0]["bid"] == 69 and vc[0]["ask"] == 70
      and vc[0]["target_bid"] == 69,
      "no-race marketable cancel: v4_resting_cancel fields identical")
check("T-J" not in s.positions and "EVJ" not in s.processed_events,
      "no-race: position deleted + untombstoned exactly as pre-fix")
check(s.cancelled and s.cancelled[0]["label"] == "v4_cancel_bid_marketable_stale",
      "no-race: cancel label unchanged")

# 3b. T50 clean cancel byte-identical fields (also covered by test_t50_paired_basis)
s = make_bot(cancel_ok=True)
ET2 = "EV2"; s.event_tickers = {ET2: {"L1", "SB"}}
l1 = make_pos("L1", et=ET2, entry_price=75, entry_qty=5, phase="active",
              entry_order_id="L1O", is_v4=True)
sb = make_pos("SB", et=ET2, entry_price=37, entry_qty=0, phase="entry_resting",
              entry_order_id="SBO", is_v4=True)
s.positions = {"L1": l1, "SB": sb}
POLL_QUEUE[:] = [order_resp(0, "canceled")]
run(s._cancel_sibling_if_paired_over_cap("L1", ET2, 75))
pbc = events(s, "paired_basis_cancel")
check(len(pbc) == 1 and pbc[0]["combined"] == 112 and pbc[0]["cap"] == M.V4_PAIRED_BASIS_CAP
      and sb.entry_order_id == "", "no-race T50: paired_basis_cancel fields + oid clear identical")

# ============================================================================
# SECTION 4 — T4 adversarial
# ============================================================================
print("--- T4 adversarial ---")

# 4a. cap arithmetic preserved: under-cap pair -> NO cancel, NO resolve call
s = make_bot()
s.event_tickers = {ET2: {"L1", "SB"}}
l1 = make_pos("L1", et=ET2, entry_price=40, entry_qty=5, phase="active", entry_order_id="L1O", is_v4=True)
sb = make_pos("SB", et=ET2, entry_price=45, entry_qty=0, phase="entry_resting", entry_order_id="SBO", is_v4=True)
s.positions = {"L1": l1, "SB": sb}
run(s._cancel_sibling_if_paired_over_cap("L1", ET2, 40))
check(not s.cancelled and sb.entry_order_id == "SBO", "under-cap (85<=99): no cancel, sibling untouched")

# 4b. T50 race: BOTH legs filled -> sibling fill BOOKED, pair held, loud event, no deletion
s = make_bot(cancel_ok=False)
s.event_tickers = {ET2: {"L1", "SB"}}
l1 = make_pos("L1", et=ET2, entry_price=75, entry_qty=5, phase="active", entry_order_id="L1O", is_v4=True)
sb = make_pos("SB", et=ET2, entry_price=37, entry_qty=0, phase="entry_resting", entry_order_id="SBO", is_v4=True)
s.positions = {"L1": l1, "SB": sb}
POLL_QUEUE[:] = [order_resp(5, "executed", 0.37)]
run(s._cancel_sibling_if_paired_over_cap("L1", ET2, 75))
check(sb.entry_qty == 5 and sb.phase == "active" and "SB" in s.positions,
      "T50 race: sibling fill booked, position kept (pair locked = reality)")
check(len(events(s, "paired_basis_filled_race")) == 1, "paired_basis_filled_race emitted")
check(any(pl["tk"] == "SB" and pl["action"] == "sell" for pl in s.placed),
      "booked raced sibling got its exit posted")

# 4c. full-fill equivalence: race-booked end-state == poll-booked end-state
def snapshot(pos):
    return (pos.entry_qty, pos.phase, pos.strategy, pos.exit_price, pos.entry_filled_ts > 0)
s1 = make_bot()
pa = make_pos("T-K", entry_price=69, entry_order_id="K1", phase="entry_resting", is_v4=True)
s1.positions["T-K"] = pa
run(s1._book_v4_entry_fill("T-K", pa, 5, 69, "executed"))           # check_fills path
s2 = make_bot(cancel_ok=False)
pb = make_pos("T-K2", entry_price=69, entry_order_id="K2", phase="entry_resting", is_v4=True)
s2.positions["T-K2"] = pb
POLL_QUEUE[:] = [order_resp(5, "executed", 0.69)]
run(s2._cancel_entry_and_resolve("T-K2", pb, "x", "y"))             # race path
check(snapshot(pa) == snapshot(pb), "full-fill semantics: race-booked == poll-booked end-state")
check(s1.placed[0]["price"] == s2.placed[0]["price"] == 98, "identical exit price both paths")

# ============================================================================
# SECTION 5 — T5 LIVE-EVIDENCE REGRESSION (AUGFUC 2026-06-11)
# ============================================================================
print("--- T5 live-evidence: AUGFUC ---")

AUG_ET = "KXATPMATCH-26JUN11AUGFUC"; AUG = AUG_ET + "-AUG"; FUC = AUG_ET + "-FUC"

# 5a. manage-path race (what actually happened at 05:42:10 ET, now fixed):
# AUG bid 69c raced by a fill; sibling FUC resting 31c; cap 69+31=100>99.
s = make_bot(cancel_ok=False)
s.event_tickers = {AUG_ET: {AUG, FUC}}
aug = make_pos(AUG, et=AUG_ET, entry_price=69, entry_order_id="AUG_OID",
               phase="entry_resting", is_v4=True, target_price=69, entry_mode="resting_maker")
aug.match_start_ts = time.time() + 99999
fuc = make_pos(FUC, et=AUG_ET, entry_price=31, entry_order_id="FUC_OID",
               phase="entry_resting", is_v4=True, target_price=31, entry_mode="resting_maker")
s.positions = {AUG: aug, FUC: fuc}
s.processed_events = {AUG_ET}
POLL_QUEUE[:] = [order_resp(5, "executed", 0.69),   # AUG resolve poll -> filled
                 order_resp(0, "canceled")]          # FUC T50 resolve poll -> clean cancel
run(s._v4_manage_resting_inner(AUG, aug, book(69, 70), time.time()))
check(aug.entry_qty == 5 and aug.phase == "active" and AUG in s.positions,
      "AUG raced fill BOOKED (pre-fix: deleted + orphaned to reconcile)")
check(any(pl["tk"] == AUG and pl["action"] == "sell" and pl["price"] == 98 for pl in s.placed),
      "AUG exit posted at 98 (69+29 band) at booking time, not 36s later via reconcile")
check(FUC not in s.positions and any(c["tk"] == FUC for c in s.cancelled),
      "FUC sibling CANCELLED by T50 on booking (cap 100>99) -- the 96-minute hole closed")
check(len(events(s, "paired_basis_cancel")) == 1, "paired_basis_cancel emitted for FUC")
# Pre-fix-identical: the T50 sibling cancel untombstones the EVENT (the unfilled
# leg is freed; over-cap re-placement stays blocked by _paired_basis_ok).
check(AUG_ET not in s.processed_events,
      "sibling cancel untombstones event (pre-fix-identical; placement guard still caps)")

# 5b. adoption variant (STEP 5): position already exchange-side, bot adopts naked.
s = make_bot(completion=True)
s.event_tickers = {AUG_ET: {AUG, FUC}}
fuc = make_pos(FUC, et=AUG_ET, entry_price=31, entry_order_id="FUC_OID",
               phase="entry_resting", is_v4=True, entry_mode="resting_maker")
s.positions = {FUC: fuc}
POLL_QUEUE[:] = [order_resp(0, "canceled")]          # FUC T50 resolve -> clean cancel
run(s._v4_reconcile_naked(AUG, AUG_ET, "ATP_MAIN", 69, {"qty": 5},
                          context="steady_state_reconcile"))
aug2 = s.positions.get(AUG)
check(aug2 is not None and aug2.entry_qty == 5 and aug2.phase == "active",
      "adoption: naked position booked through _book_v4_entry_fill")
ef = events(s, "entry_filled")
check(ef and ef[0]["source"] == "reconcile_adoption", "adoption: entry_filled source=reconcile_adoption")
check(FUC not in s.positions and any(c["tk"] == FUC for c in s.cancelled),
      "adoption: T50 cap check runs -- over-cap sibling cancelled (never the exposed pair)")
cba = events(s, "completion_booking_adoption")
check(len(cba) == 1 and cba[0]["context"] == "steady_state_reconcile",
      "V5: completion_booking_adoption emitted, steady-state context (the alert case)")

# 5c. V5 boot context + flag-off behavior
s = make_bot(completion=True)
run(s._v4_reconcile_naked("TKX", "EVX", "ATP_MAIN", 50, {"qty": 5}, context="boot_reconcile"))
cba = events(s, "completion_booking_adoption")
check(len(cba) == 1 and cba[0]["context"] == "boot_reconcile", "V5: boot_reconcile context")
s = make_bot(completion=False)
run(s._v4_reconcile_naked("TKY", "EVY", "ATP_MAIN", 50, {"qty": 5}))
check(not events(s, "completion_booking_adoption") and events(s, "entry_filled"),
      "flag OFF: no V5 event, adoption still books + T50")

# 5d. adoption hold-rule: routes through hold-aware exit application (no sell posted)
s = make_bot(band=(None, "hold"))
run(s._v4_reconcile_naked("TKH", "EVH", "ATP_MAIN", 50, {"qty": 5}))
ph = s.positions["TKH"]
check(ph.strategy == "hold" and not any(pl["action"] == "sell" for pl in s.placed)
      and events(s, "hold_to_settle"), "adoption hold-cell: hold-aware, no exit posted")

# 5e. adoption link branch unchanged: existing resting sell -> link, no booking
s = make_bot()
async def _fake_api_get_sells(sess, ak, pk, path, rl):
    if "status=resting" in path:
        return {"orders": [{"action": "sell", "order_id": "SELL1", "yes_price_dollars": "0.80"}]}
    return {}
M.api_get = _fake_api_get_sells
run(s._v4_reconcile_naked("TKL", "EVL", "ATP_MAIN", 50, {"qty": 5}))
M.api_get = _fake_api_get
pl_ = s.positions["TKL"]
check(pl_.exit_order_id == "SELL1" and pl_.exit_price == 80 and not events(s, "entry_filled")
      and events(s, "reconcile_v4_exit_found"),
      "adoption link branch: existing sell linked, NO booking, no exit churn")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
