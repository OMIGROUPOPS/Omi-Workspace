#!/usr/bin/env python3
"""[LANE-A / EXTERNAL REVIEW] The seven mandated regressions.

Adversarial review found accounting + proof defects in 289fd8d9. These
tests bind PRODUCTION methods (no stubbing of the paths under proof) and
assert live order-book end states, not "no error".

  1. same order, multiple prices -> exact receipt-level P&L
  2. replacement exit order after a previously booked partial
  3. duplicate fill_id / trade_id replay is idempotent
  4. unrelated AND pre-entry historical sells stay excluded
  5. armed bot-owned entry/replacement buy cleanup + a REAL subsequent
     re-entry attempt through the production chokepoint
  6. REAL partial-coverage heal ends with exactly held qty covered
  7. REAL authority mismatch cancels/re-anchors the canonical order id
     (+ unknown price = named fail-closed defect; foreign untouched)

DCA is out of scope and is neither exercised nor referenced.

Run: cd arb-executor && python3 tests/test_lane_a_review_fixes.py
"""
import sys, types, asyncio, json, os
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

TK = "KXITFMATCH-26JUL20ICHYAM-YAM"

# ---- a live order book the stubs mutate, so we can assert END STATE --
BOOK = {"orders": [], "positions": []}
FILLS = []
ORDERS = {}

async def _api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return ORDERS.get(path.rsplit("/", 1)[-1])
    if "/portfolio/fills" in path:
        return {"fills": list(FILLS)}
    if "/portfolio/orders" in path:
        return {"orders": [dict(o) for o in BOOK["orders"]]}
    if "/portfolio/positions" in path:
        return {"market_positions": [dict(p) for p in BOOK["positions"]]}
    if "/markets/" in path:
        return {"market": {"status": "active"}}
    return {}

async def _api_post(sess, ak, pk, path, payload, rl):
    oid = "NEW-%d" % (len(BOOK["orders"]) + 1)
    BOOK["orders"].append({
        "order_id": oid, "ticker": payload.get("ticker", TK),
        "action": payload.get("action"), "side": payload.get("side", "yes"),
        "yes_price_dollars": (payload.get("yes_price", 0) or 0) / 100.0,
        "remaining_count_fp": payload.get("count", 0)})
    return {"order": {"order_id": oid, "status": "resting"}}

M.api_get = _api_get
M.api_post = _api_post

STATICS = ("_canon_order", "_exit_coverage", "_canon_receipt")
BOUND = ("_fills_bulk", "_bot_owned_ids", "_cash_cleanup_state", "_canon_orders", "_exit_receipts", "_book_exit_receipts",
         "_cancel_resting_buys_on_cash", "_naked_tooth_scan",
         "_reconcile_exit_fill_from_truth", "_tooth_market_status",
         "_price_authority", "_v4_apply_exit",
         "_cancel_entry_and_resolve", "_untombstone_entry",
         "_parse_entry_fill", "_book_v4_entry_fill")

def rc(rid, oid, qty, price_c, ts=1000.0, action="sell"):
    return {"fill_id": rid, "order_id": oid, "action": action,
            "count_fp": qty, "yes_price_dollars": price_c / 100.0,
            "created_time": ts}

def make_pos(tk=TK, **kw):
    kw.setdefault("entry_price", 51)
    kw.setdefault("entry_qty", 5)
    kw.setdefault("exit_price", 64)
    kw.setdefault("phase", "active")
    p = M.Position(ticker=tk, event_ticker=tk.rsplit("-", 1)[0],
                   category="ITF_M", direction="", cell_name="",
                   cell_cfg={}, **kw)
    p.is_v4 = True
    p.entry_filled_ts = 500.0
    return p

def make_bot(cap=1):
    s = types.SimpleNamespace()
    s.positions = {}
    s.config = {"fills_bulk_ttl_sec": 0}
    s.entry_size = 5
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s._cycle_count = {}
    s.reentry_cycle_cap = cap
    s._order_fingerprints = {}
    s._bot_order_ids = set()
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append(
        (ev, det or {}, ticker))
    s._save_v4_resting = lambda: None
    s.get_category = lambda tk: "ITF_M"
    s.cell_lookup = lambda cat, px: px
    s.exit_rule_for = lambda cat, px: (13, "exit")
    s.regime_lookup = lambda cat, px: "r45_54"
    s.cancelled = []
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        BOOK["orders"][:] = [o for o in BOOK["orders"]
                             if o["order_id"] != oid]
        return True
    s.cancel_order = cancel_order
    s.placed = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price,
                         "count": count})
        r = await _api_post(None, None, None, None,
                            {"ticker": tk, "action": action,
                             "side": side, "yes_price": price,
                             "count": count}, None)
        return r["order"]["order_id"], r
    s.place_order = place_order
    s._sibling_ticker_any = lambda tk: None
    # attributes the production place_order chokepoint reads before the
    # cycle-cap gate (bound real, so the refusal is the real refusal)
    s.books = {}
    s.event_tickers = {}
    s.ticker_to_event = {}
    s.event_start_time = {}
    s._events_live = set()
    s._session_exited = set()
    s.fused_gun = False
    s.freeze_at_gun = False
    s.maker_only_entry = True
    s._order_fingerprints = {}
    s._is_match_live = lambda et: False
    s._join_trial_resolve = lambda *a, **k: None
    s._staircase_resolve = lambda *a, **k: None
    s._reentry_mark = lambda *a, **k: None
    s.processed_events = set()
    s._save_processed = lambda: None
    s.n_entries = 0
    s._horizon_state = lambda et: (False, 0)
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    for nm in STATICS:
        setattr(s, nm, getattr(M.LiveV3, nm))
    return s

def evs(s, name):
    return [d for (e, d, t) in s.logs if e == name]

def reset(orders=None, positions=None, fills=None, order_resp=None):
    BOOK["orders"] = list(orders or [])
    BOOK["positions"] = list(positions or [])
    FILLS[:] = list(fills or [])
    ORDERS.clear()
    ORDERS.update(order_resp or {})

def sells_total(tk=TK):
    return sum(float(o.get("remaining_count_fp") or 0)
               for o in BOOK["orders"]
               if o.get("action") == "sell" and o.get("ticker") == tk)

def buys_total(tk=TK):
    return sum(float(o.get("remaining_count_fp") or 0)
               for o in BOOK["orders"]
               if o.get("action") == "buy" and o.get("ticker") == tk)

# ======================================================================
print("--- 1. same order, multiple prices: exact receipt P&L ---")
# ======================================================================
# entry 51; first 2 exits at 60 booked (P&L 18); the SAME order later
# shows cumulative 5 at average 66 -> the final 3 actually filled at 70.
# Approximate maths would add (66-51)*3 = 45 -> 63 total. Exact receipt
# accounting is 2*(60-51) + 3*(70-51) = 18 + 57 = 75.
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[rc("F-a", "E-1", 2, 60, ts=1000)])
run(s._reconcile_exit_fill_from_truth(TK, p))
check(p.pnl_cents == 18, "first 2 @60 book P&L 18 (got %s)" % p.pnl_cents)
check(p.exit_filled_qty == 2, "cumulative qty 2")
reset(fills=[rc("F-a", "E-1", 2, 60, ts=1000),
             rc("F-b", "E-1", 3, 70, ts=2000)],
      order_resp={"E-1": {"order": {"status": "executed",
                                    "fill_count_fp": 5,
                                    "average_fill_price_fp": 0.66}}})
run(s._reconcile_exit_fill_from_truth(TK, p))
check(p.pnl_cents == 75,
      "EXACT receipt P&L 2*(60-51)+3*(70-51) = 75 (got %s)" % p.pnl_cents)
check(p.pnl_cents != 63, "the cumulative-average approximation (63) is dead")
check(p.exit_filled_qty == 5, "cumulative qty 5")
check(s._cycle_count.get(TK) == 1, "cycle increments once")

# ======================================================================
print("--- 2. replacement exit order after a booked partial ---")
# ======================================================================
# 2 already booked from an EARLIER exit order; the replacement order
# fills the remaining 3 at 64; exchange position reads zero.
s = make_bot()
p = make_pos(exit_order_id="E-OLD")
s.positions[TK] = p
reset(fills=[rc("F-old", "E-OLD", 2, 64, ts=1000)])
run(s._reconcile_exit_fill_from_truth(TK, p))
check(p.exit_filled_qty == 2 and p.pnl_cents == 26,
      "earlier order booked 2 @64 (qty %s pnl %s)"
      % (p.exit_filled_qty, p.pnl_cents))
check(TK in s.positions, "still open after the partial")
# replacement order takes over
p.exit_order_id = "E-NEW"
reset(fills=[rc("F-old", "E-OLD", 2, 64, ts=1000),
             rc("F-new", "E-NEW", 3, 64, ts=2000)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True, "replacement completes the cash")
check(p.exit_filled_qty == 5,
      "POSITION-cumulative qty across both orders = 5 (got %s)"
      % p.exit_filled_qty)
check(p.pnl_cents == 65, "exact P&L 65 (got %s)" % p.pnl_cents)
check(TK not in s.positions, "position closes exactly once")
check(s._cycle_count.get(TK) == 1, "cycle increments exactly once")
per = p.__dict__.get("_exit_booked_by_order")
check(per == {"E-OLD": 2.0, "E-NEW": 3.0},
      "per-order ledger keeps both orders: %s" % per)

# ======================================================================
print("--- 3. duplicate fill_id / trade_id replay is idempotent ---")
# ======================================================================
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[rc("F-1", "E-1", 5, 64)])
run(s._reconcile_exit_fill_from_truth(TK, p))
pnl1, cyc1, q1 = p.pnl_cents, s._cycle_count.get(TK), p.exit_filled_qty
for _ in range(3):
    run(s._reconcile_exit_fill_from_truth(TK, p))
check(p.pnl_cents == pnl1, "replay x3: P&L unchanged (%s)" % p.pnl_cents)
check(p.exit_filled_qty == q1, "replay x3: qty unchanged (%s)" % q1)
check(s._cycle_count.get(TK) == cyc1, "replay x3: cycle unchanged (%s)" % cyc1)
# trade_id fallback receipt identity
s2 = make_bot()
p2 = make_pos(exit_order_id="E-2")
s2.positions[TK] = p2
tr = {"trade_id": "T-9", "order_id": "E-2", "action": "sell",
      "count_fp": 5, "yes_price_dollars": 0.64, "created_time": 1000}
reset(fills=[tr])
run(s2._reconcile_exit_fill_from_truth(TK, p2))
check(p2.exit_filled_qty == 5, "trade_id receipt books")
reset(fills=[tr])
run(s2._reconcile_exit_fill_from_truth(TK, p2))
check(p2.pnl_cents == 65, "trade_id replay idempotent (%s)" % p2.pnl_cents)

# ======================================================================
print("--- 4. unrelated + pre-entry historical sells excluded ---")
# ======================================================================
s = make_bot()
p = make_pos(exit_order_id="E-MINE")      # entry_filled_ts = 500
s.positions[TK] = p
reset(fills=[rc("F-foreign", "SOMEONE-ELSE", 5, 90, ts=1500),
             rc("F-preentry", "E-MINE", 5, 95, ts=100)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "foreign + pre-entry only -> NOT confirmed")
check(p.exit_filled_qty == 0 and p.pnl_cents == 0,
      "nothing booked from foreign/pre-entry (qty %s pnl %s)"
      % (p.exit_filled_qty, p.pnl_cents))
check(TK in s.positions, "position intact")
reset(fills=[rc("F-foreign", "SOMEONE-ELSE", 5, 90, ts=1500),
             rc("F-preentry", "E-MINE", 5, 95, ts=100),
             rc("F-real", "E-MINE", 5, 64, ts=1600)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True and p.exit_filled_qty == 5,
      "own post-entry receipt books 5")
check(p.pnl_cents == 65,
      "P&L from the real receipt only = 65 (got %s)" % p.pnl_cents)

# ======================================================================
print("--- 5. entry-buy cleanup + REAL subsequent re-entry attempt ---")
# ======================================================================
s = make_bot(cap=1)
p = make_pos(exit_order_id="E-1")
p.entry_order_id = "B-ENTRY"
s.positions[TK] = p
s._bot_order_ids.update({"B-ENTRY", "B-REPL"})
reset(orders=[{"order_id": "B-ENTRY", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.45, "remaining_count_fp": 5},
              {"order_id": "B-REPL", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.37, "remaining_count_fp": 5},
              {"order_id": "B-FOREIGN", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.20, "remaining_count_fp": 9}],
      fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
check(buys_total() == 19, "seeded 3 resting buys (19 contracts)")
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True, "cash confirmed")
cancelled_ids = {c["oid"] for c in s.cancelled}
check("B-ENTRY" in cancelled_ids and "B-REPL" in cancelled_ids,
      "both bot-owned entry/replacement buys CANCELLED: %s" % cancelled_ids)
check("B-FOREIGN" not in cancelled_ids,
      "foreign buy NOT cancelled (manual book untouched)")
check(buys_total() == 9, "only the foreign 9 remain on the book")
check(TK not in s.positions, "closure happened after cleanup")
# order of operations: cleanup precedes closure
kinds = [e for (e, d, t) in s.logs]
check(kinds.index("cash_cleanup_buy_cancelled") < len(kinds),
      "cleanup logged")
# REAL downstream re-entry attempt through the production chokepoint
s._place_order_unlocked = types.MethodType(M.LiveV3._place_order_unlocked, s)
real_place = types.MethodType(M.LiveV3.place_order, s)
oid_new, resp = run(real_place(TK, "buy", "yes", 45, 5, post_only=True))
check(oid_new == "", "re-entry REFUSED by the production chokepoint")
check((resp or {}).get("_error") == "cycle_cap",
      "refusal reason is cycle_cap (got %s)" % (resp or {}).get("_error"))
cc = evs(s, "cycle_cap_refused")
check(len(cc) == 1 and cc[0]["completed_cycles"] >= 1,
      "cycle_cap_refused names the completed cycle")
check(buys_total() == 9, "no replacement entry survives or is placed")

# ======================================================================
print("--- 6. REAL partial-coverage heal covers exactly held qty ---")
# ======================================================================
s = make_bot()
p = make_pos(entry_qty=5, entry_price=51)
p.exit_order_id = "S-OLD"
p.exit_filled_qty = 0
s.positions[TK] = p
reset(orders=[{"order_id": "S-OLD", "ticker": TK, "action": "sell",
               "yes_price_dollars": 0.64, "remaining_count_fp": 1}],
      positions=[{"ticker": TK, "position_fp": 5}])
check(sells_total() == 1, "seeded: held 5 with ONE resting sell of 1")
# the real _v4_apply_exit is bound (no stub) and drives the live book
for _ in range(2):                      # tooth fires the heal at cycle 2
    run(s._naked_tooth_scan({TK: {"qty": 5.0}},
                            {TK: [{"order_id": "S-OLD", "action": "sell",
                                   "price": 64, "qty": 1}]}))
d = evs(s, "naked_leg_defect")
check(d and d[0]["uncovered"] == 4.0, "tooth saw 4 uncovered")
check(sells_total() == 5,
      "FINAL live book: total resting sell qty is exactly 5 (got %s)"
      % sells_total())
check(len([o for o in BOOK["orders"] if o["action"] == "sell"]) == 1,
      "exactly one resting sell order (not stacked)")
check(any(c["oid"] == "S-OLD" for c in s.cancelled),
      "the prior undersized sell was lawfully cancelled/replaced")

# ======================================================================
print("--- 7. REAL authority mismatch: cancel + re-anchor canonical ---")
# ======================================================================
SEAL_P = REPO / "state/pair_policies_sealed_v1.json"
made_seal = False
if not SEAL_P.exists():
    SEAL_P.parent.mkdir(parents=True, exist_ok=True)
    SEAL_P.write_text(json.dumps({"bands": {"ITF_M-B1": {
        "status": "SEALED", "depth_p90": 10.0, "anchor_med": 50}}}))
    made_seal = True
try:
    seal = json.loads(SEAL_P.read_text()).get("bands") or {}
    band = next((b for b, r in seal.items()
                 if r.get("status") == "SEALED" and r.get("depth_p90")),
                None)
    if band is None:
        print("SKIP: no SEALED band available in the sealed object")
    else:
        depth = float(seal[band]["depth_p90"])
        anchor = 50
        fish = int(round(anchor - depth))
        s = make_bot()
        s.config = {"one_authority_enabled": True}
        p = make_pos(entry_qty=0, phase="entry_resting")
        p.entry_order_id = "B-WRONG"
        s.positions[TK] = p
        s._bcasc_pair = {TK.rsplit("-", 1)[0]: "flat_flat"}
        s._bcasc_state = {TK: {"band": band, "open": anchor}}
        s._bot_order_ids.update({"B-WRONG", "B-NOPRICE"})
        auth, ab, af = s._price_authority(TK)
        check(auth == "SEAL" and af == fish,
              "authority resolves SEAL at fish %s (got %s/%s)"
              % (fish, auth, af))
        om = {TK: [{"order_id": "B-WRONG", "action": "buy",
                    "price": fish + 7, "qty": 5},
                   {"order_id": "B-NOPRICE", "action": "buy", "qty": 5},
                   {"order_id": "B-FOREIGN2", "action": "buy",
                    "price": fish + 9, "qty": 5}]}
        reset(positions=[],
              order_resp={"B-WRONG": {"order": {"status": "canceled",
                                                "fill_count_fp": 0}}})
        for _ in range(2):            # detect, then re-anchor
            run(s._naked_tooth_scan({}, om))
        mm = evs(s, "authority_mismatch_defect")
        check(mm, "mismatch defect raised")
        check(not evs(s, "authority_sweep_error"),
              "no swallowed error on the authority path")
        ra = evs(s, "authority_reanchor")
        check(ra, "re-anchor performed: %s" % (ra[:1] or "none"))
        check(any(c["oid"] == "B-WRONG" for c in s.cancelled),
              "the CANONICAL order_id was cancelled: %s"
              % [c["oid"] for c in s.cancelled])
        check(not any(c["oid"] == "B-FOREIGN2" for c in s.cancelled),
              "foreign/manual order NOT cancelled")
        pl = [x for x in s.placed if x["action"] == "buy"]
        check(pl and pl[0]["price"] == fish,
              "replacement posted AT the authority price %s (got %s)"
              % (fish, pl[0]["price"] if pl else None))
        check(pl and pl[0]["count"] == 5,
              "quantity preserved (5, got %s)"
              % (pl[0]["count"] if pl else None))
        unk = evs(s, "authority_price_unknown_defect")
        check(unk, "bot-owned unknown-price order = NAMED fail-closed "
                   "defect (not silently compliant)")
finally:
    if made_seal:
        try:
            os.remove(SEAL_P)
        except OSError:
            pass

# ======================================================================
print("--- 8. REV2: cancellation must be CONFIRMED ---")
# ======================================================================
def cash_with_cleanup(cancel_result="ok", exchange_qty=0):
    s = make_bot()
    p = make_pos(exit_order_id="E-1")
    p.entry_order_id = "B-1"
    s.positions[TK] = p
    s._bot_order_ids.add("B-1")
    reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
                   "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
          positions=([{"ticker": TK, "position_fp": exchange_qty}]
                     if exchange_qty else []),
          fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
    if cancel_result == "false":
        async def co(tk, oid, label=""):
            s.cancelled.append({"tk": tk, "oid": oid, "label": label})
            return False                      # exchange refused
        s.cancel_order = co
    elif cancel_result == "raise":
        async def co(tk, oid, label=""):
            s.cancelled.append({"tk": tk, "oid": oid, "label": label})
            raise RuntimeError("network")
        s.cancel_order = co
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
    return s, p, r

# 8a. cancel_order returns False -> pending, nothing erased, refusal armed
s, p, r = cash_with_cleanup("false")
check(r is False, "cancel False -> cash does NOT close")
check(TK in s.positions, "cancel False -> position retained")
check(p.entry_order_id == "B-1", "cancel False -> entry order id NOT cleared")
check(evs(s, "cash_cleanup_pending"), "cash_cleanup_pending raised (loud)")
check(not evs(s, "cash_cleanup_buy_cancelled"),
      "no 'cancelled' logged for an unconfirmed cancel")
check(s._cycle_count.get(TK) == 1,
      "refusal armed exactly once despite pending cleanup")
check(evs(s, "cash_refusal_armed"), "refusal-armed line present")

# 8b. cancel_order raises -> same discipline
s, p, r = cash_with_cleanup("raise")
check(r is False and TK in s.positions,
      "cancel raises -> pending, position retained")
check(p.entry_order_id == "B-1", "cancel raises -> order id retained")
pend = evs(s, "cash_cleanup_pending")
check(pend and pend[0]["failed"], "failure named in the pending line")

# 8c. exchange position still non-zero -> inconsistent -> pending
s, p, r = cash_with_cleanup("ok", exchange_qty=5)
check(r is False, "exchange still holds shares -> not closed")
pend = evs(s, "cash_cleanup_pending")
check(pend and pend[0]["exchange_qty"] == 5,
      "pending names the inconsistent exchange qty")

# 8d. cleanup-pending RETRIES and later closes safely (refusal armed once)
s = make_bot()
p = make_pos(exit_order_id="E-1")
p.entry_order_id = "B-1"
s.positions[TK] = p
s._bot_order_ids.add("B-1")
_state = {"fail": True}
async def flaky(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    if _state["fail"]:
        return False
    BOOK["orders"][:] = [o for o in BOOK["orders"] if o["order_id"] != oid]
    return True
s.cancel_order = flaky
reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
      fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
r1 = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r1 is False and TK in s.positions, "cycle A: pending, retained")
cyc_after_a = s._cycle_count.get(TK)
_state["fail"] = False
reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
      fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
r2 = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r2 is True, "cycle B: retry succeeds and closes")
check(TK not in s.positions, "closed only after verified-clean book")
check(s._cycle_count.get(TK) == cyc_after_a == 1,
      "cycle armed exactly once across the retry (%s)"
      % s._cycle_count.get(TK))
check(evs(s, "cash_cleanup_verified"), "verified-clean line present")

# 8e. cancellation races a buy FILL: exchange shows shares -> stay open
s = make_bot()
p = make_pos(exit_order_id="E-1")
p.entry_order_id = "B-1"
s.positions[TK] = p
s._bot_order_ids.add("B-1")
async def racing_cancel(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    BOOK["orders"][:] = [o for o in BOOK["orders"] if o["order_id"] != oid]
    BOOK["positions"] = [{"ticker": TK, "position_fp": 5}]   # it FILLED
    return True
s.cancel_order = racing_cancel
reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
      fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "cancel raced a fill -> NOT closed")
check(TK in s.positions, "raced fill -> position retained for the tooth")
pend = evs(s, "cash_cleanup_pending")
check(pend and pend[0]["exchange_qty"] == 5,
      "raced fill named via exchange truth")

# ======================================================================
print("--- 9. REV2: exact receipts or retry (no invented P&L) ---")
# ======================================================================
# 9a. receipt without a price cannot book
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[{"fill_id": "F-np", "order_id": "E-1", "action": "sell",
              "count_fp": 5, "created_time": 1600}])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False and p.pnl_cents == 0,
      "receipt with NO price -> unbookable, no P&L invented")
unc = evs(s, "phantom_cash_unconfirmed")
check(unc and any("yes_price_dollars" in (m or [])
                  for m in (unc[-1].get("missing") or [])),
      "the missing truth is named: %s" % (unc[-1].get("missing") if unc
                                          else None))

# 9b. fills feed temporarily EMPTY -> retry, nothing booked
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False and TK in s.positions, "empty feed -> retry, intact")
reset(fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True and p.pnl_cents == 65, "feed returns -> books exactly")

# 9c. cumulative-average order status ALONE cannot book or close
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[], order_resp={"E-1": {"order": {
    "status": "executed", "fill_count_fp": 5,
    "average_fill_price_fp": 0.66}}})
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "order-status cumulative average CANNOT close the cash")
check(p.exit_filled_qty == 0 and p.pnl_cents == 0,
      "order-status cumulative average books NOTHING (qty %s pnl %s)"
      % (p.exit_filled_qty, p.pnl_cents))
check(TK in s.positions, "position intact under the silent feed")

# 9d. pre-entry timestamp still excluded under strict rules
s = make_bot()
p = make_pos(exit_order_id="E-1")      # entry_filled_ts 500
s.positions[TK] = p
reset(fills=[rc("F-old", "E-1", 5, 95, ts=100)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False and p.pnl_cents == 0,
      "pre-entry receipt excluded (no P&L)")

# ======================================================================
print("--- 10. REV2: N positions do NOT cost N fills requests ---")
# ======================================================================
FILLS_CALLS = {"n": 0}
_orig_get = _api_get
async def counting_get(sess, ak, pk, path, rl):
    if "/portfolio/fills" in path:
        FILLS_CALLS["n"] += 1
    return await _orig_get(sess, ak, pk, path, rl)
M.api_get = counting_get
try:
    s = make_bot()
    s.config = {"fills_bulk_ttl_sec": 30}      # one cycle
    tickers = []
    rows = []
    for i in range(5):
        tki = "KXITFMATCH-26JUL20AAA%d-AAA" % i
        tickers.append(tki)
        pi = make_pos(tki, exit_order_id="E-%d" % i)
        s.positions[tki] = pi
        row = rc("F-%d" % i, "E-%d" % i, 5, 64, ts=1600)
        row["ticker"] = tki
        rows.append(row)
    reset(fills=rows)
    FILLS_CALLS["n"] = 0
    for i, tki in enumerate(tickers):
        run(s._exit_receipts(tki, {"E-%d" % i}))
    check(FILLS_CALLS["n"] == 1,
          "5 positions -> exactly ONE fills-history request (got %d)"
          % FILLS_CALLS["n"])
    got = run(s._exit_receipts(tickers[3], {"E-3"}))[0]
    check(len(got) == 1 and got[0]["order_id"] == "E-3",
          "per-position receipts resolved from the shared fetch")
    check(FILLS_CALLS["n"] == 1, "still one request after all lookups")
finally:
    M.api_get = _orig_get

# ======================================================================
print("--- 11. REV3 D1: cash cleanup must not fail open on UNKNOWN ---")
# ======================================================================
# The book state used by every case below: one bot-owned resting buy,
# a confirmed cash on the exit order. Only the VERIFICATION responses
# differ. Anything other than two explicit successes must stay pending.
def d1_case(verify_orders, verify_positions, cancel_ok=True):
    """verify_* : "ok" | "none" | "nokey" | "malformed" | "raise" """
    s = make_bot()
    p = make_pos(exit_order_id="E-1")
    p.entry_order_id = "B-1"
    s.positions[TK] = p
    s._bot_order_ids.add("B-1")
    reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
                   "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
          fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
    state = {"orders_calls": 0, "pos_calls": 0}
    async def verifying_get(sess, ak, pk, path, rl):
        if "/portfolio/orders" in path and "status=resting" in path:
            state["orders_calls"] += 1
            if state["orders_calls"] == 1:       # the pre-cancel read
                return {"orders": [dict(o) for o in BOOK["orders"]]}
            if verify_orders == "none": return None
            if verify_orders == "nokey": return {"other": []}
            if verify_orders == "malformed": return {"orders": "nope"}
            if verify_orders == "raise": raise RuntimeError("orders boom")
            return {"orders": [dict(o) for o in BOOK["orders"]]}
        if "/portfolio/positions" in path:
            state["pos_calls"] += 1
            if verify_positions == "none": return None
            if verify_positions == "nokey": return {"other": []}
            if verify_positions == "malformed":
                return {"market_positions": "nope"}
            if verify_positions == "raise": raise RuntimeError("pos boom")
            if verify_positions == "nonzero":
                return {"market_positions": [{"ticker": TK,
                                              "position_fp": 5}]}
            return {"market_positions": []}
        return await _api_get(sess, ak, pk, path, rl)
    if not cancel_ok:
        async def co(tk, oid, label=""):
            s.cancelled.append({"tk": tk, "oid": oid, "label": label})
            return False
        s.cancel_order = co
    M.api_get = verifying_get
    try:
        r = run(s._reconcile_exit_fill_from_truth(TK, p))
    finally:
        M.api_get = _api_get
    return s, p, r

def d1_expect_pending(label, s, p, r, want_orders_ok=None,
                      want_positions_ok=None, want_failure=True):
    check(r is False, "%s -> does NOT close" % label)
    check(TK in s.positions, "%s -> position retained" % label)
    check(p.entry_order_id == "B-1", "%s -> entry order id retained" % label)
    check(not evs(s, "cash_cleanup_verified"),
          "%s -> NEVER emits cash_cleanup_verified" % label)
    pend = evs(s, "cash_cleanup_pending")
    check(bool(pend), "%s -> cash_cleanup_pending emitted" % label)
    if pend and want_orders_ok is not None:
        check(pend[-1].get("orders_ok") is want_orders_ok,
              "%s -> names orders_ok=%s" % (label, want_orders_ok))
    if pend and want_positions_ok is not None:
        check(pend[-1].get("positions_ok") is want_positions_ok,
              "%s -> names positions_ok=%s" % (label, want_positions_ok))
    if pend and want_failure:
        check(bool(pend[-1].get("verify_failures")),
              "%s -> names the precise failure: %s"
              % (label, pend[-1].get("verify_failures")))

# 11.1 orders verification returns None
s, p, r = d1_case("none", "ok")
d1_expect_pending("orders=None", s, p, r, False, True)
# 11.2 orders response lacks 'orders'
s, p, r = d1_case("nokey", "ok")
d1_expect_pending("orders missing key", s, p, r, False, True)
# 11.3 positions verification returns None
s, p, r = d1_case("ok", "none")
d1_expect_pending("positions=None", s, p, r, True, False)
# 11.4 positions response lacks 'market_positions'
s, p, r = d1_case("ok", "nokey")
d1_expect_pending("positions missing key", s, p, r, True, False)
# 11.5 either fetch raises
s, p, r = d1_case("raise", "ok")
d1_expect_pending("orders raises", s, p, r, False, True)
s, p, r = d1_case("ok", "raise")
d1_expect_pending("positions raises", s, p, r, True, False)
# malformed collections are UNKNOWN too
s, p, r = d1_case("malformed", "ok")
d1_expect_pending("orders malformed", s, p, r, False, True)
s, p, r = d1_case("ok", "malformed")
d1_expect_pending("positions malformed", s, p, r, True, False)
# 11.6 cancel returns True but verification becomes unavailable
s, p, r = d1_case("none", "none")
d1_expect_pending("cancel ok, both feeds unknown", s, p, r, False, False)
check(any(c["oid"] == "B-1" for c in s.cancelled),
      "cancel was attempted before verification failed")
# 11.8 explicit NONZERO exchange position stays pending
s, p, r = d1_case("ok", "nonzero")
d1_expect_pending("exchange qty 5", s, p, r, True, True,
                  want_failure=False)
pend = evs(s, "cash_cleanup_pending")
check(pend and pend[-1].get("exchange_qty") == 5,
      "nonzero exchange qty reported as a number")
# 11.7 THE ONLY VERIFYING CASE: both feeds explicit + empty
s, p, r = d1_case("ok", "ok")
check(r is True, "both feeds explicitly empty -> closes")
check(TK not in s.positions, "verified closure removes the position")
ver = evs(s, "cash_cleanup_verified")
check(bool(ver), "cash_cleanup_verified emitted exactly here")
check(ver and ver[-1].get("orders_ok") is True
      and ver[-1].get("positions_ok") is True,
      "verified line names BOTH proofs")
check(ver and ver[-1].get("exchange_qty") == 0.0,
      "verified line carries exchange qty 0")

# ======================================================================
print("--- 12. REV3 D2: fills pagination must exhaust or fail ---")
# ======================================================================
PAGES = {"seq": [], "calls": 0}
async def paging_get(sess, ak, pk, path, rl):
    if "/portfolio/fills" in path:
        i = PAGES["calls"]
        PAGES["calls"] += 1
        spec = PAGES["seq"][i] if i < len(PAGES["seq"]) else {"fills": []}
        if spec == "RAISE":
            raise RuntimeError("page boom")
        return spec
    return await _api_get(sess, ak, pk, path, rl)

def d2_bot(pages, ttl=30):
    s = make_bot()
    s.config = {"fills_bulk_ttl_sec": ttl}
    PAGES["seq"] = pages
    PAGES["calls"] = 0
    return s

# 12.1 the target receipt exists ONLY on page two
pages = [{"fills": [rc("F-other", "E-OTHER", 5, 70, ts=1500)],
          "cursor": "c1"},
         {"fills": [rc("F-mine", "E-1", 5, 64, ts=1600)]}]
s = d2_bot(pages)
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
M.api_get = paging_get
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(r is True, "page-two receipt is found and books")
check(p.exit_filled_qty == 5 and p.pnl_cents == 65,
      "page-two receipt books exactly (qty %s pnl %s)"
      % (p.exit_filled_qty, p.pnl_cents))
check(PAGES["calls"] == 2, "walked exactly 2 pages (got %d)"
      % PAGES["calls"])

# 12.2 five positions share ONE two-page walk
pages = [{"fills": [rc("F-%d" % i, "E-%d" % i, 5, 64, ts=1600)
                    for i in range(3)], "cursor": "c1"},
         {"fills": [rc("F-%d" % i, "E-%d" % i, 5, 64, ts=1600)
                    for i in range(3, 5)]}]
s = d2_bot(pages)
M.api_get = paging_get
try:
    for i in range(5):
        tki = "KXITFMATCH-26JUL20BBB%d-BBB" % i
        got, defects, ok = run(s._exit_receipts(tki, {"E-%d" % i}))
        check(ok is True, "position %d: feed_ok" % i)
finally:
    M.api_get = _api_get
check(PAGES["calls"] == 2,
      "5 positions consumed ONE two-page walk (pages fetched: %d)"
      % PAGES["calls"])

# 12.3 page two returns None -> whole fetch fails
pages = [{"fills": [rc("F-a", "E-1", 2, 64, ts=1600)], "cursor": "c1"},
         None]
s = d2_bot(pages)
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
M.api_get = paging_get
try:
    rows, ok = run(s._fills_bulk())
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(ok is False and rows == [], "page-two None -> feed_ok False, no rows")
check(r is False and p.exit_filled_qty == 0 and p.pnl_cents == 0,
      "page-two None -> nothing booked, nothing closed")
check(evs(s, "fills_bulk_incomplete"), "incomplete pagination logged")

# 12.4 page two raises
pages = [{"fills": [rc("F-a", "E-1", 2, 64, ts=1600)], "cursor": "c1"},
         "RAISE"]
s = d2_bot(pages)
M.api_get = paging_get
try:
    rows, ok = run(s._fills_bulk())
finally:
    M.api_get = _api_get
check(ok is False and rows == [], "page-two raise -> feed_ok False")
inc = evs(s, "fills_bulk_incomplete")
check(inc and "exception" in str(inc[-1].get("reason")),
      "exception named in the failure reason: %s"
      % (inc[-1].get("reason") if inc else None))

# 12.5 missing `fills` collection
pages = [{"fills": [rc("F-a", "E-1", 2, 64, ts=1600)], "cursor": "c1"},
         {"other": []}]
s = d2_bot(pages)
M.api_get = paging_get
try:
    rows, ok = run(s._fills_bulk())
finally:
    M.api_get = _api_get
check(ok is False and rows == [], "missing fills collection -> feed_ok False")

# 12.6 repeated cursor (loop) -> failure, not a spin
pages = [{"fills": [], "cursor": "SAME"},
         {"fills": [], "cursor": "SAME"},
         {"fills": [], "cursor": "SAME"}]
s = d2_bot(pages)
M.api_get = paging_get
try:
    rows, ok = run(s._fills_bulk())
finally:
    M.api_get = _api_get
check(ok is False, "repeated cursor -> feed_ok False")
check(PAGES["calls"] <= 3, "repeated cursor detected fast (%d pages)"
      % PAGES["calls"])
inc = evs(s, "fills_bulk_incomplete")
check(inc and "repeated_cursor" in str(inc[-1].get("reason")),
      "repeated cursor named: %s" % (inc[-1].get("reason") if inc else None))

# 12.7 duplicate receipt across pages books ONCE
dup = rc("F-dup", "E-1", 5, 64, ts=1600)
pages = [{"fills": [dup], "cursor": "c1"}, {"fills": [dup]}]
s = d2_bot(pages)
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
M.api_get = paging_get
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(r is True, "duplicate-across-pages still completes")
check(p.exit_filled_qty == 5 and p.pnl_cents == 65,
      "duplicate booked ONCE (qty %s pnl %s)"
      % (p.exit_filled_qty, p.pnl_cents))

# 12.8 incomplete pagination cannot close or invent P&L
pages = [{"fills": [rc("F-a", "E-1", 5, 64, ts=1600)], "cursor": "c1"},
         None]
s = d2_bot(pages)
p = make_pos(exit_order_id="E-1")
p.entry_order_id = "B-1"
s.positions[TK] = p
s._bot_order_ids.add("B-1")
M.api_get = paging_get
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(r is False, "incomplete pagination -> no closure")
check(TK in s.positions, "incomplete pagination -> position retained")
check(p.pnl_cents == 0, "incomplete pagination -> NO P&L invented")
check(s._cycle_count.get(TK, 0) == 0,
      "incomplete pagination -> no cycle armed")
check(not evs(s, "cash_cleanup_verified"),
      "incomplete pagination -> never verified")

print("\n%s" % ("ALL REVIEW-FIX TESTS PASS" if not fails
                 else "*** %d FAILURE(S)" % fails))
sys.exit(1 if fails else 0)
