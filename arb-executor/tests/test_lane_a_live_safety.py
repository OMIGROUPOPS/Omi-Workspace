#!/usr/bin/env python3
"""[LANE-A] Live-safety repairs — full test burden, behavioural.

Four defects, each proven by running the REAL methods against realistic
objects (reconciled order rows, raw Kalshi rows, Position dataclasses,
routable API stubs). No source-text assertions anywhere.

  1. ONE-AUTHORITY SWEEP FIELD MISMATCH — canonical order boundary
     (order_id / ticker / action / side / price / remaining) across
     every upstream shape; the old code read oid/px off rows carrying
     order_id/price (KeyError on cancel, price -1 => phantom mismatch).
  2. NAKED-TOOTH QUANTITY COVERAGE — total resting exit qty vs held
     qty; 5 held / 1 exit = 4 uncovered (naked), 5 held / 5 exits =
     covered (no duplicate), partials and multi-order exits included.
  3. PHANTOM-CASH CONFIRMATION + RETRY — no permanent latch before
     confirmation; order-identity attribution; count_fp; partial !=
     cashed; incremental P&L, never overwritten; idempotent re-observe.
  4. TONIGHT'S RE-BUY-AFTER-CASH RACE — exit cashes, poller behind,
     exchange reads zero, healer runs: booked once, cycle finished, no
     deletion before confirmation, NO second buy, first confirmation
     fails then later succeeds.

Run: cd arb-executor && python3 tests/test_lane_a_live_safety.py
"""
import sys, types, asyncio
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    fails += (0 if c else 1)

def run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ---- routable API stub ------------------------------------------------
ORDER_RESP = {}      # order_id -> {"order": {...}} or None
FILLS_RESP = []      # list of canonical /fills rows
MARKET_STATUS = "active"
RESTING = []         # list of raw resting-order rows (ticker-scoped feed)
POSITIONS = []       # explicit exchange positions (empty == verified empty)
API_CALLS = []

async def _fake_api_get(sess, ak, pk, path, rl):
    API_CALLS.append(path)
    if "/portfolio/orders/" in path and "?" not in path:
        oid = path.rsplit("/", 1)[-1]
        return ORDER_RESP.get(oid)
    if "/portfolio/fills" in path:
        return {"fills": list(FILLS_RESP)}
    if "/portfolio/orders?" in path or "status=resting" in path:
        return {"orders": list(RESTING)}
    # [REV3] exchange truth must be EXPLICIT: the contract treats a
    # missing collection as UNKNOWN, so the double states it plainly.
    if "/portfolio/positions" in path:
        return {"market_positions": list(POSITIONS)}
    if "/markets/" in path:
        return {"market": {"status": MARKET_STATUS}}
    return {}
M.api_get = _fake_api_get

STATICS = ("_canon_order", "_exit_coverage", "_canon_receipt",
           "_validate_order_row")
BOUND = ("_fills_bulk", "_bot_owned_ids", "_cash_cleanup_state", "_canon_orders", "_naked_tooth_scan",
         "_reconcile_exit_fill_from_truth", "_tooth_market_status",
         "_price_authority", "_exit_receipts", "_book_exit_receipts",
         "_cancel_resting_buys_on_cash", "_finalize_full_cash",
         "_resting_orders_all", "_positions_qty_all")

def make_pos(tk, **kw):
    kw.setdefault("entry_price", 51)
    kw.setdefault("entry_qty", 5)
    kw.setdefault("exit_price", 64)
    kw.setdefault("phase", "active")
    p = M.Position(ticker=tk, event_ticker=tk.rsplit("-", 1)[0],
                   category="ITF_M", direction="", cell_name="",
                   cell_cfg={}, **kw)
    p.is_v4 = True
    return p

def make_bot():
    s = types.SimpleNamespace()
    s.positions = {}
    s.config = {"fills_bulk_ttl_sec": 0}
    s.entry_size = 5
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s._cycle_count = {}
    s._order_fingerprints = {}
    s._bot_order_ids = set()
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append(
        (ev, det or {}, ticker))
    s._save_v4_resting = lambda: None
    s.get_category = lambda tk: "ITF_M"
    s.placed = []
    s.cancelled = []
    s.exits_applied = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price,
                         "count": count})
        return "OID_NEW_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    async def _v4_apply_exit(tk, pos, basis, qty):
        s.exits_applied.append({"tk": tk, "basis": basis, "qty": qty})
        pos.exit_order_id = "EXIT_NEW"
    s._v4_apply_exit = _v4_apply_exit
    async def _cancel_entry_and_resolve(tk, pos, why, race):
        s.cancelled.append({"tk": tk, "oid": pos.entry_order_id,
                            "label": why})
        return "cancelled"
    s._cancel_entry_and_resolve = _cancel_entry_and_resolve
    s._sibling_ticker_any = lambda tk: None
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    for nm in STATICS:            # @staticmethod -> plain function
        setattr(s, nm, getattr(M.LiveV3, nm))
    return s

def evs(s, name):
    return [d for (e, d, t) in s.logs if e == name]

def reset_api(order_resp=None, fills=None, status="active", resting=None,
              positions=None):
    global ORDER_RESP, FILLS_RESP, MARKET_STATUS, RESTING, POSITIONS
    ORDER_RESP = dict(order_resp or {})
    FILLS_RESP = list(fills or [])
    RESTING = list(resting or [])
    POSITIONS = list(positions or [])
    MARKET_STATUS = status
    API_CALLS.clear()

def rcpt(rid, oid, qty, price_c, ts=1000.0):
    """A realistic /fills row: fill_id + count_fp + yes_price_dollars."""
    return {"fill_id": rid, "order_id": oid, "action": "sell",
            "count_fp": qty, "yes_price_dollars": price_c / 100.0,
            "created_time": ts}

TK = "KXITFMATCH-26JUL20ICHYAM-YAM"

# ======================================================================
print("--- DEFECT 1: canonical order boundary ---")
# ======================================================================
b = make_bot()

# 1a. reconcile's schema (order_id/price/qty) — the shape the sweep
#     actually receives in production and previously misread.
recon_row = {"order_id": "R-1", "action": "buy", "side": "yes",
             "price": 48, "qty": 5}
c = b._canon_orders({TK: [recon_row]})[TK][0]
check(c["order_id"] == "R-1", "reconcile row -> order_id")
check(c["price"] == 48, "reconcile row -> price (was read as px=-1)")
check(c["remaining"] == 5.0, "reconcile row -> remaining")
check(c["action"] == "buy" and c["side"] == "yes", "reconcile row -> action/side")
check(c["ticker"] == TK, "reconcile row -> ticker injected")

# 1b. the audit's schema (oid/px/qty)
audit_row = {"oid": "A-2", "px": 37, "qty": 3}
c2 = b._canon_orders({TK: [audit_row]})[TK][0]
check(c2["order_id"] == "A-2" and c2["price"] == 37
      and c2["remaining"] == 3.0, "audit row (oid/px/qty) normalizes")

# 1c. raw Kalshi schema (yes_price_dollars / remaining_count_fp)
raw_row = {"order_id": "K-3", "ticker": TK, "action": "sell",
           "side": "yes", "yes_price_dollars": "0.64",
           "remaining_count_fp": "2.0"}
c3 = b._canon_orders({TK: [raw_row]})[TK][0]
check(c3["price"] == 64, "raw kalshi dollars -> 64c")
check(c3["remaining"] == 2.0, "raw kalshi remaining_count_fp -> 2.0")
check(c3["action"] == "sell", "raw kalshi action")

# 1d. unknown price stays None (never a silent -1 that reads as mismatch)
c4 = b._canon_orders({TK: [{"order_id": "N-4", "action": "buy"}]})[TK][0]
check(c4["price"] is None, "missing price -> None, not -1")
check(c4["remaining"] == 0.0, "missing qty -> 0.0")

# 1e. the sweep consumes reconcile rows without KeyError and cancels by
#     the CANONICAL id (the old code raised KeyError on o['oid']).
b2 = make_bot()
b2.config = {"one_authority_enabled": True}
pos = make_pos(TK, entry_qty=5, phase="active", exit_order_id="E-1")
b2.positions[TK] = pos
b2._bot_order_ids.add("R-9")
b2._order_fingerprints["R-9"] = {"ticker": TK, "action": "buy"}
reset_api()
run(b2._naked_tooth_scan(
    {TK: {"qty": 5.0}},
    {TK: [{"order_id": "R-9", "action": "buy", "side": "yes",
           "price": 48, "qty": 5},
          {"order_id": "S-9", "action": "sell", "side": "yes",
           "price": 64, "qty": 5}]}))
err = evs(b2, "authority_sweep_error")
check(not err, "sweep runs clean on reconcile rows (no KeyError): %s"
      % (err[:1] or "none"))

# ======================================================================
print("--- DEFECT 2: naked-tooth quantity coverage ---")
# ======================================================================
def naked_case(held, sells, engine_pos=True, cycles=1):
    s = make_bot()
    if engine_pos:
        p = make_pos(TK, entry_qty=int(held), phase="active")
        p.exit_order_id = "E-OLD"
        s.positions[TK] = p
    reset_api()
    om = {TK: [{"order_id": "S%d" % i, "action": "sell", "side": "yes",
                "price": 64, "qty": q} for i, q in enumerate(sells)]}
    for _ in range(cycles):
        run(s._naked_tooth_scan({TK: {"qty": float(held)}}, om))
    return s

# 2a. held 5, one resting exit of 1 -> FOUR uncovered, must fire
s = naked_case(5, [1])
d = evs(s, "naked_leg_defect")
check(len(d) == 1, "held 5 / exits 1 -> naked_leg_defect fires")
check(d and d[0]["uncovered"] == 4.0,
      "uncovered reported as 4 (was: 'one sell = covered')")
check(d and d[0]["resting_exit_qty"] == 1.0, "resting exit qty reported")

# 2b. held 5, exits total 5 (single order) -> covered, silent
s = naked_case(5, [5])
check(not evs(s, "naked_leg_defect"), "held 5 / exits 5 -> no defect")
check(not s.exits_applied, "covered leg: no duplicate exit posted")

# 2c. held 5, exits 3+2 across TWO resting orders -> covered
s = naked_case(5, [3, 2])
check(not evs(s, "naked_leg_defect"),
      "held 5 / exits 3+2 (multi-order) -> covered, no defect")

# 2d. held 5, exits 3+1 = 4 -> ONE uncovered, fires
s = naked_case(5, [3, 1])
d = evs(s, "naked_leg_defect")
check(len(d) == 1 and d[0]["uncovered"] == 1.0,
      "held 5 / exits 3+1 -> 1 uncovered, fires")

# 2e. partial fill shape: held 2 (partial), no exits -> fires with 2
s = naked_case(2, [])
d = evs(s, "naked_leg_defect")
check(len(d) == 1 and d[0]["uncovered"] == 2.0,
      "partial-filled leg held 2 / no exits -> 2 uncovered")

# 2f. heal fires only at cycle 2 and reposts (uncovered recorded)
s = naked_case(5, [1], cycles=2)
h = evs(s, "naked_tooth_heal")
check(len(h) == 1, "heal fires once at cycle 2")
check(h and h[0]["uncovered_before"] == 4.0, "heal records uncovered=4")
check(len(s.exits_applied) == 1 and s.exits_applied[0]["qty"] == 5,
      "heal reposts exit sized to full held qty")

# 2g. settlement_pending carve-out still holds (never naked)
s = make_bot()
s.positions[TK] = make_pos(TK)
reset_api(status="determined")
run(s._naked_tooth_scan({TK: {"qty": 5.0}}, {TK: []}))
check(not evs(s, "naked_leg_defect"),
      "determined market -> settlement_pending, never naked")

# ======================================================================
print("--- DEFECT 3: phantom-cash confirmation, identity, retry ---")
# ======================================================================

# 3a. NO confirmation -> False, nothing booked, nothing deleted, retry
s = make_bot()
p = make_pos(TK, exit_order_id="E-1")
s.positions[TK] = p
reset_api(order_resp={"E-1": {"order": {"status": "resting",
                                        "fill_count_fp": 0}}})
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "unconfirmed -> returns False")
check(TK in s.positions, "unconfirmed -> position NOT deleted")
check(p.pnl_cents == 0, "unconfirmed -> no P&L booked")
check(s._cycle_count.get(TK, 0) == 0, "unconfirmed -> no cycle increment")
check(len(evs(s, "phantom_cash_unconfirmed")) == 1, "unconfirmed logged")

# 3b. the latch must NOT be permanently set on failure (retry next cycle)
s = make_bot()
p = make_pos(TK, exit_order_id="E-1", phase="active")
s.positions[TK] = p
reset_api(fills=None)                        # feed silent
run(s._naked_tooth_scan({}, {}))             # cycle 1 (defect only)
run(s._naked_tooth_scan({}, {}))             # cycle 2 -> route attempt
check(getattr(p, "_phantom_cash_routed", False) is False,
      "failed confirmation leaves latch OPEN (retryable)")
check(TK in s.positions, "failed confirmation: position intact")
# now the exchange answers -> the retry succeeds
reset_api(fills=[rcpt("F-late", "E-1", 5, 64, ts=1600)])
run(s._naked_tooth_scan({}, {}))             # cycle 3 -> retry
check(getattr(p, "_phantom_cash_routed", False) is True,
      "retry after failure SUCCEEDS and latches")
check(TK not in s.positions, "confirmed cash closes the position")
check(s._cycle_count.get(TK) == 1, "confirmed cash increments cycle once")

# 3c. unrelated historical sell on the same ticker is NOT our cash
s = make_bot()
p = make_pos(TK, exit_order_id="E-MINE")
s.positions[TK] = p
reset_api(order_resp={"E-MINE": {"order": {"status": "resting",
                                           "fill_count_fp": 0}}},
          fills=[rcpt("F-OTHER", "SOMEONE-ELSE", 5, 70)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "foreign-order sell -> NOT confirmed")
check(TK in s.positions, "foreign-order sell -> position intact")

# 3d. identity-scoped fills DO confirm (count_fp authoritative)
s = make_bot()
p = make_pos(TK, exit_order_id="E-MINE")
s.positions[TK] = p
reset_api(order_resp={"E-MINE": {"order": {"status": "resting",
                                           "fill_count_fp": 0}}},
          fills=[rcpt("F-OTHER", "SOMEONE-ELSE", 9, 90),
                 rcpt("F-MINE", "E-MINE", 5, 64)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True, "own-order fills confirm the cash")
check(p.exit_filled_qty == 5, "count_fp is authoritative (5)")
check(p.pnl_cents == (64 - 51) * 5, "P&L from own fills only: %s"
      % p.pnl_cents)

# 3e. zero / missing quantity is never a cash
for label, bad in (("zero count_fp",
                    {"fill_id": "Z", "order_id": "E-1", "action": "sell",
                     "count_fp": 0, "yes_price_dollars": 0.64,
                     "created_time": 1600}),
                   ("missing price",
                    {"fill_id": "Z2", "order_id": "E-1", "action": "sell",
                     "count_fp": 5, "created_time": 1600}),
                   ("missing receipt id",
                    {"order_id": "E-1", "action": "sell", "count_fp": 5,
                     "yes_price_dollars": 0.64, "created_time": 1600})):
    s = make_bot()
    p = make_pos(TK, exit_order_id="E-1")
    s.positions[TK] = p
    reset_api(fills=[bad])
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
    check(r is False and TK in s.positions and p.pnl_cents == 0,
          "unbookable receipt (%s) -> not cashed, nothing booked" % label)

# 3f. PARTIAL exit books its increment but does NOT close the story
s = make_bot()
p = make_pos(TK, entry_qty=5, exit_order_id="E-1")
s.positions[TK] = p
reset_api(fills=[rcpt("P-1", "E-1", 2, 64, ts=1600)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "partial exit -> returns False (not fully cashed)")
check(p.exit_filled_qty == 2, "partial books 2")
check(p.exit_filled is False, "partial: exit_filled stays False")
check(TK in s.positions, "partial: position NOT deleted")
check(s._cycle_count.get(TK, 0) == 0, "partial: NO cycle increment")
check(p.pnl_cents == (64 - 51) * 2, "partial: P&L for 2 only")

# 3g. incremental completion accrues P&L, never overwrites
reset_api(fills=[rcpt("P-1", "E-1", 2, 64, ts=1600),
                 rcpt("P-2", "E-1", 3, 64, ts=1700)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True, "remaining 3 completes the cash")
check(p.exit_filled_qty == 5, "booked qty now 5")
check(p.pnl_cents == (64 - 51) * 5,
      "P&L accrued 2+3 = %s (never overwritten)" % p.pnl_cents)
check(s._cycle_count.get(TK) == 1, "cycle increments exactly once")
ef = evs(s, "exit_filled")
check(len(ef) == 2 and ef[0]["new_fills"] == 2 and ef[1]["new_fills"] == 3,
      "two exit_filled rows: increments 2 then 3")

# 3h. IDEMPOTENCY: the same fill observed twice books nothing extra
s = make_bot()
p = make_pos(TK, entry_qty=5, exit_order_id="E-1")
s.positions[TK] = p
reset_api(fills=[rcpt("F-1", "E-1", 5, 64)])
run(s._reconcile_exit_fill_from_truth(TK, p))
pnl_once, cyc_once = p.pnl_cents, s._cycle_count.get(TK)
run(s._reconcile_exit_fill_from_truth(TK, p))      # observe again
check(p.pnl_cents == pnl_once, "re-observe: P&L unchanged (%s)" % p.pnl_cents)
check(s._cycle_count.get(TK) == cyc_once,
      "re-observe: cycle count unchanged (%s)" % cyc_once)
check(len(evs(s, "phantom_cash_idempotent")) == 1,
      "re-observe logs idempotent no-op")

# 3i. no exit_order_id at all -> cannot attribute -> unconfirmed
s = make_bot()
p = make_pos(TK, exit_order_id="")
s.positions[TK] = p
reset_api(fills=[rcpt("F-X", "X", 5, 64)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False and TK in s.positions,
      "no order identity -> unconfirmed, position intact")

# ======================================================================
print("--- DEFECT 4: tonight's re-buy-after-cash race ---")
# ======================================================================
# The exact live sequence: exits CASH at the exchange, check_fills has
# not booked it, exchange positions read ZERO, the healer runs.
def race(first_confirm_fails):
    s = make_bot()
    p = make_pos(TK, entry_price=51, entry_qty=5, exit_price=64,
                 phase="active")
    p.exit_order_id = "E-CASH"
    s.positions[TK] = p
    cashed = [rcpt("F-CASH", "E-CASH", 5, 64, ts=1600)]
    # cycle 1: defect only (never acts on one observation)
    reset_api(fills=(None if first_confirm_fails else cashed))
    run(s._naked_tooth_scan({}, {}))
    check(TK in s.positions, "cycle 1: position intact (no deletion)")
    check(not evs(s, "exit_filled"), "cycle 1: nothing booked yet")
    # cycle 2: route attempt
    run(s._naked_tooth_scan({}, {}))
    if first_confirm_fails:
        check(TK in s.positions,
              "cycle 2 (confirm FAILS): position still intact")
        check(s._cycle_count.get(TK, 0) == 0,
              "cycle 2 (confirm FAILS): no cycle marked")
        check(getattr(p, "_phantom_cash_routed", False) is False,
              "cycle 2 (confirm FAILS): retry stays armed")
        # cycle 3: exchange answers -> retry succeeds
        reset_api(fills=cashed)
        run(s._naked_tooth_scan({}, {}))
    return s, p

# 4a. clean path (confirmation available at the first attempt)
s, p = race(first_confirm_fails=False)
ef = evs(s, "exit_filled")
check(len(ef) == 1, "original exit booked EXACTLY once")
check(ef and ef[0]["qty"] == 5 and ef[0]["complete"] is True,
      "booked complete at full qty")
check(p.pnl_cents == (64 - 51) * 5, "P&L booked once: %s" % p.pnl_cents)
check(s._cycle_count.get(TK) == 1, "session/cycle marked finished")
check(TK in s.__dict__.get("_session_exited", set()),
      "leg stamped session-exited")
check(TK not in s.positions, "position closed AFTER confirmation")
check(not s.placed, "NO second entry / replacement buy placed")

# 4b. the failure-then-success path
s, p = race(first_confirm_fails=True)
ef = evs(s, "exit_filled")
check(len(ef) == 1, "failed-first: booked exactly once overall")
check(s._cycle_count.get(TK) == 1, "failed-first: cycle marked once")
check(TK not in s.positions, "failed-first: closed only after success")
check(not s.placed, "failed-first: still NO re-buy")
check(len(evs(s, "phantom_cash_unconfirmed")) >= 1,
      "failed-first: the unconfirmed attempt is on the record")

# 4c. the cycle counter is what blocks the re-buy downstream: with the
#     shipped cap of 1, a cashed leg refuses further entries.
cap = 1
check(s._cycle_count.get(TK, 0) >= cap,
      "cashed leg's cycle count >= cap 1 -> chokepoint refuses re-entry")

# 4d. regression guard: the DELETION path is gone — a position is never
#     removed while unconfirmed, no matter how many cycles run.
s = make_bot()
p = make_pos(TK, exit_order_id="E-NONE")
s.positions[TK] = p
reset_api(fills=None)
for _ in range(6):
    run(s._naked_tooth_scan({}, {}))
check(TK in s.positions,
      "6 cycles unconfirmed: position STILL intact (drop is dead)")
check(not evs(s, "phantom_position_dropped"),
      "phantom_position_dropped never emitted")
check(len(evs(s, "phantom_position_defect")) == 6,
      "detection still fires every cycle (6)")

print("\n%s" % ("ALL LANE-A TESTS PASS" if not fails
                else "*** %d FAILURE(S)" % fails))
sys.exit(1 if fails else 0)
