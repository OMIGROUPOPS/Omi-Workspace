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
    cnt = payload.get("count", 0)
    BOOK["orders"].append({
        "order_id": oid, "ticker": payload.get("ticker", TK),
        "action": payload.get("action"), "side": payload.get("side", "yes"),
        "yes_price_dollars": (payload.get("yes_price", 0) or 0) / 100.0,
        "remaining_count_fp": cnt})
    # a posted order is GET-reconcilable: fill_count 0, remaining=count,
    # zero receipts -> reconciles as clean resting cover next cycle
    ORDERS[oid] = {"order": {"order_id": oid, "status": "resting",
                             "fill_count_fp": 0, "remaining_count_fp": cnt}}
    return {"order": {"order_id": oid, "status": "resting"}}

M.api_get = _api_get
M.api_post = _api_post

STATICS = ("_canon_order", "_exit_coverage", "_canon_receipt",
           "_validate_order_row")
BOUND = ("_fills_bulk", "_bot_owned_ids", "_cash_cleanup_state", "_canon_orders", "_exit_receipts", "_book_exit_receipts",
         "_entry_start_gate", "_strong_live_evidence",
         "_cancel_resting_buys_on_cash", "_finalize_full_cash",
         "_quarantine_reconcile", "_quarantine_poll",
         "_quarantine_ensure_coverage", "_quarantine_accrue",
         "_resolve_protective_oid",
         "_quarantine_covered", "_quarantine_admitted_qty",
         "_quarantine_open_qty", "_quarantine_snapshot",
         "_bot_owned_ids",
         "_resting_orders_all", "_positions_qty_all", "_naked_tooth_scan",
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
    s.unmatched_holdings = {}
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
    s.event_start_time = {TK.rsplit("-", 1)[0]: 9_999_999_999}
    s._events_live = set()
    s._start_conflict = set()
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

# ======================================================================
print("--- 13. REV4 B2: status=executed cannot override exact receipts ---")
# ======================================================================
# The phantom path proves the accounting rule directly (the exit-poll
# path shares the identical _book_exit_receipts completion logic).
# 13.4  status=executed, order fill_count=5, exact receipts=2 -> books 2
s = make_bot()
p = make_pos(entry_qty=5, exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[rc("R1", "E-1", 2, 64, ts=1600)],
      order_resp={"E-1": {"order": {"status": "executed",
                                    "fill_count_fp": 5,
                                    "average_fill_price_fp": 0.64}}})
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is False, "executed+2-receipts -> NOT complete (books partial)")
check(p.exit_filled_qty == 2, "exactly 2 booked (got %s)" % p.exit_filled_qty)
check(p.pnl_cents == (64 - 51) * 2, "P&L for 2 only (got %s)" % p.pnl_cents)
check(TK in s.positions, "position remains open on partial receipts")
check(s._cycle_count.get(TK, 0) == 0, "partial -> no cycle increment")
check(p.exit_filled is not True, "partial -> exit_filled not terminal")

# 13.5  the remaining 3 receipts arrive later -> completes once
reset(fills=[rc("R1", "E-1", 2, 64, ts=1600),
             rc("R2", "E-1", 3, 64, ts=1700)])
r = run(s._reconcile_exit_fill_from_truth(TK, p))
check(r is True, "remaining 3 receipts complete the cash")
check(p.exit_filled_qty == 5, "cumulative 5")
check(p.pnl_cents == (64 - 51) * 5, "cumulative P&L 65 (got %s)" % p.pnl_cents)
check(s._cycle_count.get(TK) == 1, "completes once, cycle +1")
check(TK not in s.positions, "closed exactly once")

# ======================================================================
print("--- 14. REV4 B1: exit-poll + phantom share ONE finalizer ---")
# ======================================================================
# 14.9  [REV5 CORRECTION] the Round-4 14.9 claim ("both entry points
#       proved") was FALSE — it invoked only _reconcile_exit_fill_from_truth
#       (the phantom path) and never the production check_fills exit poll.
#       The real two-path spy lives in Section 15 and drives check_fills
#       itself; nothing here claims a proof it did not perform.

# 14.1  cancellation returns False -> pending & retryable (no close)
def poll_bot_with_book(cancel_ok=True, buys=None, ex_positions=None,
                       verify_ok=True):
    s = make_bot()
    p = make_pos(exit_order_id="E-1")
    p.entry_order_id = "B-1"
    s.positions[TK] = p
    for b in (buys or []):
        s._bot_order_ids.add(b["order_id"])
    def build():
        reset(orders=list(buys or []),
              positions=(ex_positions if ex_positions is not None else []),
              fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
    build()
    st = {}
    async def vget(sess, ak, pk, path, rl):
        if "/portfolio/orders" in path and "status=resting" in path:
            if not verify_ok:
                return None
            return {"orders": [dict(o) for o in BOOK["orders"]]}
        if "/portfolio/positions" in path:
            return {"market_positions": list(BOOK["positions"])}
        return await _api_get(sess, ak, pk, path, rl)
    if not cancel_ok:
        async def co(tk, oid, label=""):
            s.cancelled.append({"tk": tk, "oid": oid, "label": label})
            return False
        s.cancel_order = co
    M.api_get = vget
    try:
        r = run(s._reconcile_exit_fill_from_truth(TK, p))
    finally:
        M.api_get = _api_get
    return s, p, r

buys = [{"order_id": "B-1", "ticker": TK, "action": "buy",
         "yes_price_dollars": 0.45, "remaining_count_fp": 5}]
s, p, r = poll_bot_with_book(cancel_ok=False, buys=buys)
check(r is False, "cancel False -> pending, no close")
check(TK in s.positions, "cancel False -> position retained")
check(p.entry_order_id == "B-1", "cancel False -> entry id retained")
check(p.exit_filled is not True,
      "cancel False -> exit_filled NOT set (retry re-enters)")
check(s._cycle_count.get(TK) == 1, "refusal armed once even while pending")

# 14.2  same position later verifies clean -> closes once, cycle stays 1
async def good_cancel(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    BOOK["orders"][:] = [o for o in BOOK["orders"] if o["order_id"] != oid]
    return True
s.cancel_order = good_cancel
async def vget2(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": [dict(o) for o in BOOK["orders"]]}
    if "/portfolio/positions" in path:
        return {"market_positions": []}
    return await _api_get(sess, ak, pk, path, rl)
M.api_get = vget2
try:
    r2 = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(r2 is True, "verified-clean retry closes")
check(TK not in s.positions, "closed after verification")
check(s._cycle_count.get(TK) == 1, "cycle incremented exactly once overall")

# 14.3 & 14.10  foreign buy untouched, every bot-owned buy cancelled
buys = [{"order_id": "B-1", "ticker": TK, "action": "buy",
         "yes_price_dollars": 0.45, "remaining_count_fp": 5},
        {"order_id": "B-2", "ticker": TK, "action": "buy",
         "yes_price_dollars": 0.40, "remaining_count_fp": 5},
        {"order_id": "FOREIGN", "ticker": TK, "action": "buy",
         "yes_price_dollars": 0.20, "remaining_count_fp": 9}]
s = make_bot()
p = make_pos(exit_order_id="E-1")
p.entry_order_id = "B-1"
s.positions[TK] = p
s._bot_order_ids.update({"B-1", "B-2"})
reset(orders=list(buys), positions=[],
      fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
async def cancel_del(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    BOOK["orders"][:] = [o for o in BOOK["orders"] if o["order_id"] != oid]
    return True
s.cancel_order = cancel_del
async def vget3(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": [dict(o) for o in BOOK["orders"]]}
    if "/portfolio/positions" in path:
        return {"market_positions": []}
    return await _api_get(sess, ak, pk, path, rl)
M.api_get = vget3
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
cids = {c["oid"] for c in s.cancelled}
check("B-1" in cids and "B-2" in cids, "every bot-owned buy cancelled")
check("FOREIGN" not in cids, "foreign buy NEVER cancelled")
check(r is True, "closes once foreign-safe cleanup verified")
check(all(o["order_id"] == "FOREIGN" for o in BOOK["orders"]),
      "only the foreign order remains on the book")

# 14.6  bot-owned buy on ORDERS PAGE TWO -> refused until cancelled+absent
PAGES2 = {"seq": [], "calls": 0}
s = make_bot()
p = make_pos(exit_order_id="E-1")
p.entry_order_id = "B-2"
s.positions[TK] = p
s._bot_order_ids.add("B-2")
def orders_two_pages(include_b2):
    pg1 = {"orders": [{"order_id": "FOREIGN", "action": "buy",
                       "remaining_count_fp": 9}], "cursor": "oc1"}
    pg2 = {"orders": ([{"order_id": "B-2", "action": "buy",
                        "remaining_count_fp": 5}] if include_b2 else [])}
    return [pg1, pg2]
state6 = {"pages": orders_two_pages(True), "book_has_b2": True}
async def vget6(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        import re
        m = re.search(r"cursor=([^&]+)", path)
        idx = 0 if not m else 1
        return state6["pages"][idx]
    if "/portfolio/positions" in path:
        return {"market_positions": []}
    if "/portfolio/fills" in path:
        return {"fills": [rc("F-1", "E-1", 5, 64, ts=1600)]}
    return await _api_get(sess, ak, pk, path, rl)
async def cancel6(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    if oid == "B-2":
        state6["pages"] = orders_two_pages(False)  # now absent on refetch
    return True
s.cancel_order = cancel6
M.api_get = vget6
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(any(c["oid"] == "B-2" for c in s.cancelled),
      "page-two bot buy was discovered and cancelled")
check(r is True, "closes only after page-two buy verified absent")
check(TK not in s.positions, "closed once page-two buy gone")

# 14.7  orders page two None -> UNKNOWN -> no closure
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
async def vget7(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        return ({"orders": [], "cursor": "oc1"} if "cursor" not in path
                else None)
    if "/portfolio/positions" in path:
        return {"market_positions": []}
    if "/portfolio/fills" in path:
        return {"fills": [rc("F-1", "E-1", 5, 64, ts=1600)]}
    return await _api_get(sess, ak, pk, path, rl)
M.api_get = vget7
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(r is False, "orders page-two None -> no closure")
check(TK in s.positions, "orders page-two None -> position retained")
pend = evs(s, "cash_cleanup_pending")
check(bool(pend), "pending emitted for truncated orders read")

# 14.8  malformed order row -> UNKNOWN -> no closure
for label, badrow in (
        ("no order_id", {"action": "buy", "remaining_count_fp": 5}),
        ("bad action", {"order_id": "X", "action": "weird",
                        "remaining_count_fp": 5}),
        ("nonnumeric remaining", {"order_id": "X", "action": "buy",
                                  "remaining_count_fp": "NaNish"})):
    s = make_bot()
    p = make_pos(exit_order_id="E-1")
    s.positions[TK] = p
    async def vget8(sess, ak, pk, path, rl, _bad=badrow):
        if "/portfolio/orders" in path and "status=resting" in path:
            return {"orders": [_bad]}
        if "/portfolio/positions" in path:
            return {"market_positions": []}
        if "/portfolio/fills" in path:
            return {"fills": [rc("F-1", "E-1", 5, 64, ts=1600)]}
        return await _api_get(sess, ak, pk, path, rl)
    M.api_get = vget8
    try:
        r = run(s._reconcile_exit_fill_from_truth(TK, p))
    finally:
        M.api_get = _api_get
    check(r is False, "malformed order row (%s) -> no closure" % label)
    check(TK in s.positions, "malformed (%s) -> position retained" % label)

# validator unit checks (a malformed row never silently becomes zero)
V = M.LiveV3._validate_order_row
check(V({"action": "buy", "remaining_count_fp": 5}) is None,
      "validator: missing order_id -> None")
check(V({"order_id": "X", "action": "nope",
         "remaining_count_fp": 5}) is None,
      "validator: bad action -> None")
check(V({"order_id": "X", "action": "buy",
         "remaining_count_fp": "x"}) is None,
      "validator: nonnumeric remaining -> None")
check(V({"order_id": "X", "action": "buy",
         "remaining_count_fp": -1}) is None,
      "validator: negative remaining -> None")
_okrow = V({"order_id": "X", "action": "buy", "remaining_count_fp": 5})
check(_okrow == {"order_id": "X", "action": "buy", "remaining": 5.0},
      "validator: well-formed row canonicalizes")

# ======================================================================
print("--- 15. REV5: REAL check_fills exit-poll path (B1/B2/B3) ---")
# ======================================================================
# These tests invoke the PRODUCTION LiveV3.check_fills itself for an
# active v4 position, so the exit-poll cash path is exercised end to end
# (not the phantom reconciliation).
CF_BOUND = ("check_fills", "_finalize_full_cash",
            "_cancel_resting_buys_on_cash", "_cash_cleanup_state",
            "_resting_orders_all", "_positions_qty_all",
            "_exit_receipts", "_book_exit_receipts", "_fills_bulk",
            "_canon_orders", "_bot_owned_ids")
CF_STATIC = ("_canon_order", "_canon_receipt", "_validate_order_row",
             "_exit_coverage")

def make_poll_bot(cap=1):
    s = make_bot(cap)
    s.config = {"fills_bulk_ttl_sec": 0, "completion_live_enabled": False}
    s.monotonic_cut_enabled = False
    s.n_exits = 0
    s.premarket_bids_ride_live = False
    s.event_start_time = {}
    s._completion_shadow = lambda tk, pos, now: None
    async def _mce(tk, pos):
        return None
    s._monotonic_cut_eval = _mce
    for nm in CF_BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    for nm in CF_STATIC:
        setattr(s, nm, getattr(M.LiveV3, nm))
    return s

def active_exit_pos(entry_qty=5, entry_price=51, exit_price=64,
                    exit_order_id="E-1"):
    p = make_pos(entry_qty=entry_qty, entry_price=entry_price,
                 exit_price=exit_price, exit_order_id=exit_order_id)
    p.phase = "active"
    p.exit_filled = False
    p.exit_filled_qty = 0
    p.match_start_ts = 1.0          # skip entry-buffer path
    p.dca_qty = 0
    p.dca_order_id = ""
    p.dca_filled = False
    p.play_type = ""
    return p

# 15.1  normal full receipt exit + verified cleanup (source=exit_poll,
#       cycle becomes exactly 1, session-exited set, closes after verify)
srcs_seen = []
_orig_fin = M.LiveV3._finalize_full_cash
async def fin_spy(self, tk, pos, source="cash"):
    srcs_seen.append(source)
    return await _orig_fin(self, tk, pos, source)
M.LiveV3._finalize_full_cash = fin_spy
try:
    s = make_poll_bot()
    p = active_exit_pos()
    s.positions[TK] = p
    reset(orders=[], positions=[],
          fills=[rc("F-1", "E-1", 5, 64, ts=1600)],
          order_resp={"E-1": {"order": {"status": "executed",
                                        "fill_count_fp": 5}}})
    run(s.check_fills())
    check("exit_poll" in srcs_seen,
          "check_fills invoked the finalizer with source=exit_poll")
    check(p.exit_filled_qty == 5 and p.pnl_cents == 65,
          "exact receipts booked (qty %s pnl %s)"
          % (p.exit_filled_qty, p.pnl_cents))
    check(s._cycle_count.get(TK) == 1,
          "cycle armed exactly ONCE via check_fills (got %s) — the "
          "pre-seed suppression is gone" % s._cycle_count.get(TK))
    check(TK in s.__dict__.get("_session_exited", set()),
          "session-exited set by the finalizer")
    check(TK not in s.positions, "position closed after verified cleanup")
    check(s.n_exits == 1, "n_exits incremented once")

    # 15.2  cancellation fails on cycle one; cycle two has NO new receipts;
    #       the finalizer nevertheless RETRIES via check_fills and closes.
    s = make_poll_bot()
    p = active_exit_pos()
    p.entry_order_id = "B-1"
    s.positions[TK] = p
    s._bot_order_ids.add("B-1")
    fail_state = {"cancel": False, "positions": [{"ticker": TK,
                                                  "position_fp": 0}]}
    async def cf_get(sess, ak, pk, path, rl):
        if "/portfolio/orders/E-1" in path:
            return {"order": {"status": "executed", "fill_count_fp": 5}}
        if "/portfolio/orders" in path and "status=resting" in path:
            return {"orders": [dict(o) for o in BOOK["orders"]]}
        if "/portfolio/positions" in path:
            return {"market_positions": list(fail_state["positions"])}
        if "/portfolio/fills" in path:
            return {"fills": [rc("F-1", "E-1", 5, 64, ts=1600)]}
        return await _api_get(sess, ak, pk, path, rl)
    async def cf_cancel(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        if not fail_state["cancel"]:
            return False                    # cycle-one cancellation fails
        BOOK["orders"][:] = [o for o in BOOK["orders"]
                             if o["order_id"] != oid]
        return True
    s.cancel_order = cf_cancel
    reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
                   "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
          positions=[])
    M.api_get = cf_get
    try:
        run(s.check_fills())              # cycle 1: books, cancel FAILS
        check(TK in s.positions, "cycle1: position retained (cancel fail)")
        check(p.entry_order_id == "B-1", "cycle1: entry order id retained")
        check(p.exit_filled is not True, "cycle1: exit_filled NOT set")
        check(s._cycle_count.get(TK) == 1, "cycle1: refusal already armed")
        check(getattr(p, "_cash_cleanup_pending", False) is True,
              "cycle1: cash_cleanup_pending flag set")
        pnl1, cyc1, book1 = p.pnl_cents, s._cycle_count.get(TK), p.exit_filled_qty
        # cycle 2: NO new receipts (E-1 already booked); cancellation now ok
        fail_state["cancel"] = True
        run(s.check_fills())
        check(TK not in s.positions,
              "cycle2: finalizer RETRIED with no new receipts and CLOSED")
        check(s._cycle_count.get(TK) == 1,
              "cycle2: cycle NOT double-incremented (got %s)"
              % s._cycle_count.get(TK))
        check(p.pnl_cents == pnl1 == 65,
              "cycle2: P&L unchanged/exactly-once (got %s)" % p.pnl_cents)
        check(p.exit_filled_qty == book1 == 5,
              "cycle2: receipts not rebooked (qty %s)" % p.exit_filled_qty)
    finally:
        M.api_get = _api_get

    # 15.3  partial exact receipts via check_fills: no session mutation,
    #       no cycle increment, no closure.
    s = make_poll_bot()
    p = active_exit_pos(entry_qty=5)
    s.positions[TK] = p
    reset(fills=[rc("R1", "E-1", 2, 64, ts=1600)],
          order_resp={"E-1": {"order": {"status": "executed",
                                        "fill_count_fp": 5}}})
    run(s.check_fills())
    check(p.exit_filled_qty == 2, "partial books exactly 2 (got %s)"
          % p.exit_filled_qty)
    check(p.pnl_cents == (64 - 51) * 2, "partial P&L for 2 only")
    check(TK in s.positions, "partial: position open")
    check(s._cycle_count.get(TK, 0) == 0,
          "partial: NO cycle increment (got %s)" % s._cycle_count.get(TK, 0))
    check(TK not in s.__dict__.get("_session_exited", set()),
          "partial: session-exited NOT mutated")
    check(p.exit_filled is not True, "partial: exit_filled not terminal")
finally:
    M.LiveV3._finalize_full_cash = _orig_fin

# 15.4  the phantom path invokes the SAME finalizer -> both literal
#       sources present after the real entry points ran.
srcs2 = []
async def fin_spy2(self, tk, pos, source="cash"):
    srcs2.append(source)
    return await _orig_fin(self, tk, pos, source)
M.LiveV3._finalize_full_cash = fin_spy2
try:
    # real exit-poll entry
    s = make_poll_bot()
    p = active_exit_pos()
    s.positions[TK] = p
    reset(positions=[], fills=[rc("F-1", "E-1", 5, 64, ts=1600)],
          order_resp={"E-1": {"order": {"status": "executed",
                                        "fill_count_fp": 5}}})
    run(s.check_fills())
    # real phantom entry
    s2 = make_bot()
    for nm in ("_finalize_full_cash", "_cancel_resting_buys_on_cash",
               "_cash_cleanup_state", "_resting_orders_all",
               "_positions_qty_all", "_exit_receipts",
               "_book_exit_receipts", "_reconcile_exit_fill_from_truth",
               "_bot_owned_ids"):
        setattr(s2, nm, types.MethodType(getattr(M.LiveV3, nm), s2))
    for nm in ("_canon_order", "_canon_receipt", "_validate_order_row"):
        setattr(s2, nm, getattr(M.LiveV3, nm))
    s2.config = {"fills_bulk_ttl_sec": 0}
    p2 = make_pos(exit_order_id="E-1")
    s2.positions[TK] = p2
    reset(positions=[], fills=[rc("F-2", "E-1", 5, 64, ts=1600)])
    run(s2._reconcile_exit_fill_from_truth(TK, p2))
finally:
    M.LiveV3._finalize_full_cash = _orig_fin
check("exit_poll" in srcs2 and "phantom" in srcs2,
      "BOTH literal sources present after real entry points: %s"
      % sorted(set(srcs2)))

# ======================================================================
print("--- 16. REV5 B4: verified-zero is ACTUAL zero ---")
# ======================================================================
def d4_qty_case(ex_positions):
    s = make_bot()
    p = make_pos(exit_order_id="E-1")
    p.entry_order_id = "B-1"
    s.positions[TK] = p
    s._bot_order_ids.add("B-1")
    reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
                   "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
          positions=ex_positions, fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
    async def dget(sess, ak, pk, path, rl):
        if "/portfolio/orders" in path and "status=resting" in path:
            return {"orders": [dict(o) for o in BOOK["orders"]]}
        if "/portfolio/positions" in path:
            return {"market_positions": list(BOOK["positions"])}
        if "/portfolio/fills" in path:
            return {"fills": list(FILLS)}
        return await _api_get(sess, ak, pk, path, rl)
    async def dcancel(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        BOOK["orders"][:] = [o for o in BOOK["orders"]
                             if o["order_id"] != oid]
        return True
    s.cancel_order = dcancel
    M.api_get = dget
    try:
        r = run(s._reconcile_exit_fill_from_truth(TK, p))
    finally:
        M.api_get = _api_get
    return s, p, r

# 16.1  +0.5-equivalent fractional holding -> NOT zero -> no closure
s, p, r = d4_qty_case([{"ticker": TK, "position_fp": 0.5}])
check(r is False, "+0.5 exchange qty -> NOT verified zero -> no close")
check(TK in s.positions, "+0.5 -> position retained")
# 16.2  -5 negative holding -> NOT zero -> no closure
s, p, r = d4_qty_case([{"ticker": TK, "position_fp": -5}])
check(r is False, "-5 exchange qty -> NOT verified zero -> no close")
check(TK in s.positions, "-5 -> position retained")
# 16.3  true zero -> verifies and closes
s, p, r = d4_qty_case([{"ticker": TK, "position_fp": 0}])
check(r is True, "0.0 exchange qty -> verified zero -> closes")
check(TK not in s.positions, "true zero -> closed")
# 16.4  UNKNOWN positions (missing collection) -> no closure
s = make_bot()
p = make_pos(exit_order_id="E-1")
s.positions[TK] = p
reset(fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
async def uget(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": []}
    if "/portfolio/positions" in path:
        return {"nope": []}                 # missing market_positions
    if "/portfolio/fills" in path:
        return {"fills": list(FILLS)}
    return await _api_get(sess, ak, pk, path, rl)
M.api_get = uget
try:
    r = run(s._reconcile_exit_fill_from_truth(TK, p))
finally:
    M.api_get = _api_get
check(r is False and TK in s.positions,
      "UNKNOWN positions -> fail closed, retained")

# ======================================================================
print("--- 17. REV5 RACE: bot buy fills during cash-cancel race ---")
# ======================================================================
# A fully-cashed position; a bot-owned resting buy is cancelled but the
# fill RACES it — the exchange ends holding 5 NEW contracts on TK.
s = make_poll_bot()
p = active_exit_pos(entry_qty=5, entry_price=51)
p.entry_order_id = "B-RACE"
s.positions[TK] = p
s._bot_order_ids.add("B-RACE")
reset(orders=[{"order_id": "B-RACE", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.30, "remaining_count_fp": 5},
              {"order_id": "FOREIGN", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.10, "remaining_count_fp": 9}],
      positions=[],
      fills=[rc("F-1", "E-1", 5, 64, ts=1600)])
async def race_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/E-1" in path:
        return {"order": {"status": "executed", "fill_count_fp": 5}}
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": [dict(o) for o in BOOK["orders"]]}
    if "/portfolio/positions" in path:
        return {"market_positions": list(BOOK["positions"])}
    if "/portfolio/fills" in path:
        return {"fills": list(FILLS)}
    return await _api_get(sess, ak, pk, path, rl)
async def race_cancel(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    # B-RACE cancellation races a FILL: the order leaves the book AND the
    # exchange now holds 5 new contracts on the ticker.
    if oid == "B-RACE":
        BOOK["orders"][:] = [o for o in BOOK["orders"]
                             if o["order_id"] != "B-RACE"]
        BOOK["positions"] = [{"ticker": TK, "position_fp": 5}]
    return True
s.cancel_order = race_cancel
M.api_get = race_get
try:
    run(s.check_fills())
finally:
    M.api_get = _api_get
# SAFE MINIMUM (proven): fail closed, never erase, refusal armed once,
# foreign untouched, the raced holding named explicitly.
check(TK in s.positions,
      "raced fill -> position NOT closed/erased (retained)")
check(s._cycle_count.get(TK) == 1,
      "raced fill -> refusal armed exactly once (got %s)"
      % s._cycle_count.get(TK))
cids = {c["oid"] for c in s.cancelled}
check("FOREIGN" not in cids, "raced fill -> foreign order NEVER cancelled")
check(any(o["order_id"] == "FOREIGN" for o in BOOK["orders"]),
      "raced fill -> foreign order remains on the book")
raced = evs(s, "cash_cleanup_raced_holding")
check(bool(raced), "raced holding is NAMED explicitly (cash_cleanup_raced_holding)")
check(raced and raced[-1].get("exchange_qty") == 5,
      "raced holding names the exact new quantity (5)")
pend = evs(s, "cash_cleanup_pending")
check(bool(pend), "raced fill -> cash_cleanup_pending (fail closed)")

# ======================================================================
print("--- 18. REV6 QUARANTINE: cash-cancel-race (operator law C) ---")
# ======================================================================
def rcb(rid, oid, qty, price_c, ts=1500.0):
    return {"fill_id": rid, "order_id": oid, "action": "buy",
            "count_fp": qty, "yes_price_dollars": price_c / 100.0,
            "created_time": ts}

def race_env(buy_receipt=True, foreign=True, buy_qty=5, buy_price=30,
             ex_qty=5, buy_ts=1700):
    """Full-cash of a 5-lot; a bot-owned B-RACE buy fills during the
    cancellation race so the exchange ends holding `ex_qty` on TK."""
    s = make_poll_bot()
    p = active_exit_pos(entry_qty=5, entry_price=51, exit_price=64)
    p.entry_order_id = "B-RACE"
    s.positions[TK] = p
    s._bot_order_ids.add("B-RACE")
    orders = [{"order_id": "B-RACE", "ticker": TK, "action": "buy",
               "yes_price_dollars": buy_price / 100.0,
               "remaining_count_fp": 5}]
    if foreign:
        orders.append({"order_id": "FOREIGN", "ticker": TK,
                       "action": "buy", "yes_price_dollars": 0.10,
                       "remaining_count_fp": 9})
    fills = [rc("S-1", "E-1", 5, 64, ts=1600)]     # the exit cash (sell)
    if buy_receipt:
        fills.append(rcb("BUYRC", "B-RACE", buy_qty, buy_price, ts=buy_ts))
    reset(orders=orders, positions=[], fills=fills)
    async def rget(sess, ak, pk, path, rl):
        if "/portfolio/orders/E-1" in path:
            return {"order": {"status": "executed", "fill_count_fp": 5}}
        if "/portfolio/orders" in path and "status=resting" in path:
            return {"orders": [dict(o) for o in BOOK["orders"]]}
        if "/portfolio/positions" in path:
            return {"market_positions": list(BOOK["positions"])}
        if "/portfolio/fills" in path:
            return {"fills": list(FILLS)}
        return await _api_get(sess, ak, pk, path, rl)
    async def rcancel(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        if oid == "B-RACE":
            BOOK["orders"][:] = [o for o in BOOK["orders"]
                                 if o["order_id"] != "B-RACE"]
            BOOK["positions"] = [{"ticker": TK, "position_fp": ex_qty}]
        return True
    s.cancel_order = rcancel
    return s, p, rget

# ---- Regression A: normal cash unchanged (re-assert via a fresh poll) --
s = make_poll_bot()
p = active_exit_pos()
s.positions[TK] = p
reset(orders=[], positions=[],
      fills=[rc("F-A", "E-1", 5, 64, ts=1600)],
      order_resp={"E-1": {"order": {"status": "executed",
                                    "fill_count_fp": 5}}})
run(s.check_fills())
check(TK not in s.positions and s._cycle_count.get(TK) == 1
      and p.pnl_cents == 65,
      "A: normal cash closes once, cycle 1, P&L 65, no quarantine")
check(not s.unmatched_holdings.get(TK), "A: no quarantine on a clean cash")

# ---- Regression B: cancellation-race buy -------------------------------
# Coverage is BOOK-confirmed: cycle 1 admits + posts protective (pending,
# old Position retained); cycle 2 finds it resting and closes the old cycle.
s, p, rget = race_env()
M.api_get = rget
try:
    run(s.check_fills())               # cycle 1: admit + post protective
    check(TK in s.positions,
          "B cycle1: old Position PENDING until coverage book-confirmed")
    check(getattr(p, "_cash_cleanup_pending", False) is True,
          "B cycle1: cleanup pending")
    check(len(s.unmatched_holdings.get(TK) or []) == 1,
          "B cycle1: raced buy quarantined")
    run(s.check_fills())               # cycle 2: coverage confirmed -> close
finally:
    M.api_get = _api_get
check(p.pnl_cents == 65, "B: completed-cycle P&L UNCHANGED (65)")
check(p.exit_filled_qty == 5 and p.entry_qty == 5 and p.entry_price == 51,
      "B: old receipt ledgers unchanged (qty %s basis %s)"
      % (p.exit_filled_qty, p.entry_price))
check(s._cycle_count.get(TK) == 1, "B: cycle count remains 1")
check(TK not in s.positions, "B: old Position closed AFTER coverage confirmed")
q = s.unmatched_holdings.get(TK) or []
check(len(q) == 1, "B: exactly ONE quarantine record")
check(q and q[0]["buy_receipt_id"] == "BUYRC"
      and q[0]["qty"] == 5.0 and q[0]["price"] == 30,
      "B: raced buy stored once from its ACTUAL basis (30)")
sells = [x for x in s.placed if x["action"] == "sell"]
check(any(x["count"] == 5 and x["price"] == 43 for x in sells),
      "B: quarantine protective sell = 5 @ (30+13)=43 (raced basis)")
check(q and q[0]["protective_exit_target"] == 43,
      "B: protective exit target from raced basis, not old (64)")
buys = [x for x in s.placed if x["action"] == "buy"]
check(not buys, "B: NO conception/re-buy placed")
check("FOREIGN" not in {c["oid"] for c in s.cancelled}
      and any(o["order_id"] == "FOREIGN" for o in BOOK["orders"]),
      "B: foreign order untouched and still resting")

# ---- Regression C: repeated reconcile/tooth cycles are idempotent ------
s, p, rget = race_env()
M.api_get = rget
try:
    run(s.check_fills())               # admit + protective exit
    sells1 = len([x for x in s.placed if x["action"] == "sell"])
    recs1 = len(s.unmatched_holdings.get(TK) or [])
    # run the REAL naked tooth twice more against the raced holding
    # drive the tooth with NO resting-sell coverage so the naked
    # condition is real; the quarantine guard must DEFER (never heal the
    # completed Position against the old basis).
    async def cget(sess, ak, pk, path, rl):
        if "/portfolio/markets/" in path or "/markets/" in path:
            return {"market": {"status": "active"}}
        return await _api_get(sess, ak, pk, path, rl)
    M.api_get = cget
    for _ in range(3):
        run(s._naked_tooth_scan({TK: {"qty": 5.0}}, {TK: []}))
finally:
    M.api_get = _api_get
check(len(s.unmatched_holdings.get(TK) or []) == recs1 == 1,
      "C: no duplicate quarantine record across cycles")
check(len([x for x in s.placed if x["action"] == "sell"]) == sells1,
      "C: no duplicate protective sell")
check(not evs(s, "naked_tooth_heal"),
      "C: naked tooth NEVER healed the old Position (no old-basis exit)")
check(bool(evs(s, "naked_tooth_quarantine_protected")),
      "C: tooth verified/held quarantine-owned coverage (not silent)")

# ---- Regression D: restart persists + restores quarantine --------------
import tempfile, os as _os
tf = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
tf.close()
_orig_path = M.V4_RESTING_FILE
M.V4_RESTING_FILE = tf.name
try:
    s1 = make_poll_bot()
    s1._window_open = {}
    s1.completion_reprice = False
    s1.pair_governor_scoot = False
    s1.unmatched_holdings = {TK: [dict(s.unmatched_holdings[TK][0])]}
    for nm in ("_save_v4_resting",):
        setattr(s1, nm, types.MethodType(getattr(M.LiveV3, nm), s1))
    s1._save_v4_resting()
    check(_os.path.getsize(tf.name) > 0, "D: state persisted to disk")
    # fresh engine restores
    s2 = make_poll_bot()
    s2._window_open = {}
    s2.unmatched_holdings = {}
    for nm in ("_load_v4_resting",):
        setattr(s2, nm, types.MethodType(getattr(M.LiveV3, nm), s2))
    s2._load_v4_resting()
    r2 = s2.unmatched_holdings.get(TK) or []
    check(len(r2) == 1 and r2[0]["buy_receipt_id"] == "BUYRC"
          and r2[0]["qty"] == 5.0 and r2[0]["price"] == 30
          and r2[0]["protective_exit_target"] == 43,
          "D: quarantine restored intact (basis + protective coverage)")
    # the restored engine's tooth defers (coverage/refusal survive)
    run(s2._naked_tooth_scan({TK: {"qty": 5.0}},
                             {TK: [{"order_id": "PX", "action": "sell",
                                    "price": 43, "remaining_count_fp": 5}]}))
    check(not evs(s2, "naked_tooth_heal"),
          "D: restored engine does NOT re-heal against old basis")
    check(not [x for x in s2.placed if x["action"] == "buy"],
          "D: restored engine places no re-conception")
finally:
    M.V4_RESTING_FILE = _orig_path
    try:
        _os.remove(tf.name)
    except OSError:
        pass

# ---- Regression E: protective exit partial then full (quarantine P&L) ---
s, p, rget = race_env()
M.api_get = rget
try:
    run(s.check_fills())               # admit + protective sell @43
    rec = s.unmatched_holdings[TK][0]
    px_oid = rec["protective_exit_order_id"]
    old_pnl = p.pnl_cents
    # partial protective fill: 2 @ 45. The order GET is RECONCILED — it
    # reports fill_count 2 / remaining 3, matching the 2 exact receipts, so
    # coverage is booked 2 + reconciled resting 3 = 5 (covered, NOT resolved).
    reset(orders=[], positions=[{"ticker": TK, "position_fp": 5}],
          fills=[{"fill_id": "PX1", "order_id": px_oid, "action": "sell",
                  "count_fp": 2, "yes_price_dollars": 0.45,
                  "created_time": 1700}],
          order_resp={px_oid: {"order": {"status": "resting",
                                         "fill_count_fp": 2,
                                         "remaining_count_fp": 3}}})
    async def eget(sess, ak, pk, path, rl):
        if "/portfolio/fills" in path:
            return {"fills": list(FILLS)}
        return await _api_get(sess, ak, pk, path, rl)
    M.api_get = eget
    run(s._quarantine_poll())
    check(rec["exit_booked_qty"] == 2 and rec["status"] == "quarantined",
          "E: partial protective fill books 2 into quarantine (unresolved)")
    check(rec["exit_pnl_cents"] == (45 - 30) * 2,
          "E: quarantine P&L uses the RACED basis 30 (got %s)"
          % rec["exit_pnl_cents"])
    check(p.pnl_cents == old_pnl == 65,
          "E: completed-cycle P&L still UNCHANGED (65)")
    # remaining 3 @ 45; the protective order GET is now TERMINAL (executed,
    # fill_count 5) and reconciles exactly against the 5 receipts -> the
    # ONLY path to resolution: booked == qty, zero live cover, oid terminal.
    reset(fills=[{"fill_id": "PX1", "order_id": px_oid, "action": "sell",
                  "count_fp": 2, "yes_price_dollars": 0.45,
                  "created_time": 1700},
                 {"fill_id": "PX2", "order_id": px_oid, "action": "sell",
                  "count_fp": 3, "yes_price_dollars": 0.45,
                  "created_time": 1800}],
          order_resp={px_oid: {"order": {"status": "executed",
                                         "fill_count_fp": 5,
                                         "remaining_count_fp": 0}}})
    run(s._quarantine_poll())
    check(rec["exit_booked_qty"] == 5 and rec["status"] == "resolved",
          "E: full fill + oid GET terminal (fill_count==receipts) -> resolved")
    check(rec["exit_pnl_cents"] == (45 - 30) * 5, "E: cumulative quarantine P&L")
    check(TK in s.unmatched_holdings, "E: resolved record REMAINS for audit")
    # idempotent re-poll
    run(s._quarantine_poll())
    check(rec["exit_pnl_cents"] == (45 - 30) * 5,
          "E: re-poll idempotent (no double booking)")
finally:
    M.api_get = _api_get

# ---- Regression F: ambiguous/missing buy receipt -> UNKNOWN ------------
s, p, rget = race_env(buy_receipt=False)   # no buy receipt in the feed
M.api_get = rget
try:
    run(s.check_fills())
finally:
    M.api_get = _api_get
check(TK in s.positions, "F: no buy receipt -> old position NOT closed/erased")
check(not s.unmatched_holdings.get(TK),
      "F: no fabricated quarantine record without receipts")
check(not [x for x in s.placed if x["action"] == "sell"
           and x["price"] == 43],
      "F: no fabricated protective sell / basis")
check(bool(evs(s, "quarantine_unknown")), "F: loud UNKNOWN emitted")
check("FOREIGN" not in {c["oid"] for c in s.cancelled},
      "F: foreign untouched under UNKNOWN")
check(bool(evs(s, "cash_cleanup_pending")), "F: fail closed (pending)")

# receipts that do not reconcile to exchange qty -> UNKNOWN
s, p, rget = race_env(buy_qty=2, ex_qty=5)   # receipt 2 but exchange 5
M.api_get = rget
try:
    run(s.check_fills())
finally:
    M.api_get = _api_get
check(not s.unmatched_holdings.get(TK) and TK in s.positions,
      "F: receipts under exchange qty -> UNKNOWN, no admission")

# ---- Regression G: old exit-order GET unavailable during retry ---------
s = make_poll_bot()
p = active_exit_pos()
p.entry_order_id = "B-1"
s.positions[TK] = p
s._bot_order_ids.add("B-1")
gstate = {"cancel": False}
async def gget(sess, ak, pk, path, rl):
    if "/portfolio/orders/E-1" in path:
        # cycle 1 returns the executed order; cycle 2 the order is GONE
        return (None if gstate["cancel"] else
                {"order": {"status": "executed", "fill_count_fp": 5}})
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": [dict(o) for o in BOOK["orders"]]}
    if "/portfolio/positions" in path:
        return {"market_positions": []}
    if "/portfolio/fills" in path:
        return {"fills": [rc("F-G", "E-1", 5, 64, ts=1600)]}
    return await _api_get(sess, ak, pk, path, rl)
async def gcancel(tk, oid, label=""):
    s.cancelled.append({"tk": tk, "oid": oid, "label": label})
    if gstate["cancel"]:
        BOOK["orders"][:] = [o for o in BOOK["orders"] if o["order_id"] != oid]
        return True
    return False
s.cancel_order = gcancel
reset(orders=[{"order_id": "B-1", "ticker": TK, "action": "buy",
               "yes_price_dollars": 0.45, "remaining_count_fp": 5}],
      positions=[])
M.api_get = gget
try:
    run(s.check_fills())          # cycle 1: books, cancel FAILS -> pending
    check(TK in s.positions and getattr(p, "_cash_cleanup_pending", False),
          "G: cycle 1 pending, position retained")
    pnl1, cyc1, book1 = p.pnl_cents, s._cycle_count.get(TK), p.exit_filled_qty
    # cycle 2: the OLD exit-order GET now returns None (404); cancel ok
    gstate["cancel"] = True
    run(s.check_fills())
    check(TK not in s.positions,
          "G: retry CLOSED even though the exit-order GET returned None")
    check(s._cycle_count.get(TK) == cyc1 == 1,
          "G: no cycle duplication (got %s)" % s._cycle_count.get(TK))
    check(p.pnl_cents == pnl1 == 65, "G: no P&L duplication")
    check(p.exit_filled_qty == book1 == 5, "G: no receipt re-booking")
    check(s.n_exits == 1, "G: no n_exits duplication")
finally:
    M.api_get = _api_get

# ======================================================================
print("--- 19. REV6.1 CAUSAL attribution (strictly post-cash) ---")
# ======================================================================
def causal_case(buy_ts, term_ts=1600.0, order_id="B-RACE",
                in_attempt=True, ex_qty=5, buy_qty=5):
    s = make_bot()
    p = make_pos(entry_qty=5, entry_price=51, exit_price=64,
                 exit_order_id="E-1")
    p.exit_filled_qty = 5
    if term_ts is not None:
        p._terminal_cash_ts = term_ts
    p._cancel_attempted_buy_ids = {order_id} if in_attempt else set()
    s.positions[TK] = p
    s._bot_order_ids.add(order_id)
    fills = []
    if buy_ts is not None:
        fills.append({"fill_id": "BR", "order_id": order_id,
                      "action": "buy", "count_fp": buy_qty,
                      "yes_price_dollars": 0.30, "created_time": buy_ts})
    reset(orders=[], positions=[{"ticker": TK, "position_fp": ex_qty}],
          fills=fills)
    async def cg(sess, ak, pk, path, rl):
        if "/portfolio/orders" in path and "status=resting" in path:
            return {"orders": []}
        if "/portfolio/fills" in path:
            return {"fills": list(FILLS)}
        return await _api_get(sess, ak, pk, path, rl)
    M.api_get = cg
    try:
        v = run(s._quarantine_reconcile(TK, p, ex_qty))
    finally:
        M.api_get = _api_get
    return s, p, v

# 19.1 exit@1600, buy@1700 -> admitted
s, p, v = causal_case(1700)
check(v in ("explained", "pending"), "19.1 buy@1700 (post-cash) admitted")
check(len(s.unmatched_holdings.get(TK) or []) == 1, "19.1 one record")
# 19.2 buy@1500 -> pre-cash rejected
s, p, v = causal_case(1500)
check(v == "unknown", "19.2 buy@1500 (pre-cash) -> UNKNOWN")
check(not s.unmatched_holdings.get(TK), "19.2 no admission")
check(bool(evs(s, "quarantine_unknown")), "19.2 loud UNKNOWN")
# 19.3 buy@1600 (equal resolution) -> ambiguous UNKNOWN
s, p, v = causal_case(1600)
check(v == "unknown", "19.3 buy@1600 (== terminal cash) -> UNKNOWN")
check(not s.unmatched_holdings.get(TK), "19.3 no admission at equal ts")
# 19.4 missing buy timestamp -> UNKNOWN
s = make_bot()
p = make_pos(entry_qty=5, exit_order_id="E-1")
p.exit_filled_qty = 5
p._terminal_cash_ts = 1600.0
p._cancel_attempted_buy_ids = {"B-RACE"}
s.positions[TK] = p
s._bot_order_ids.add("B-RACE")
reset(orders=[], positions=[{"ticker": TK, "position_fp": 5}],
      fills=[{"fill_id": "BR", "order_id": "B-RACE", "action": "buy",
              "count_fp": 5, "yes_price_dollars": 0.30}])  # no ts
async def cg4(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": []}
    if "/portfolio/fills" in path:
        return {"fills": list(FILLS)}
    return await _api_get(sess, ak, pk, path, rl)
M.api_get = cg4
try:
    v = run(s._quarantine_reconcile(TK, p, 5))
finally:
    M.api_get = _api_get
check(v == "unknown" and not s.unmatched_holdings.get(TK),
      "19.4 missing buy ts -> UNKNOWN, no admission")
# 19.5 no terminal-cash ts -> UNKNOWN (causality cannot be established)
s, p, v = causal_case(1700, term_ts=None)
check(v == "unknown", "19.5 no terminal_cash_ts -> UNKNOWN")
# 19.6 old original-entry receipt (pre-cash, entry order) -> not admitted
s, p, v = causal_case(1400, order_id="B-1", in_attempt=False)
check(v == "unknown" and not s.unmatched_holdings.get(TK),
      "19.6 original-entry receipt -> not admitted")

# ======================================================================
print("--- 20. REV6.2 coverage verified, open-qty, repost ---")
# ======================================================================
def qbot_with_rec(booked=0.0, protective_ids=None, status="quarantined"):
    s = make_bot()
    s.unmatched_holdings = {TK: [{
        "ticker": TK, "buy_receipt_id": "BR", "buy_order_id": "B-RACE",
        "qty": 5.0, "price": 30, "exchange_ts": 1700.0,
        "terminal_cash_ts": 1600.0, "local_ts": 0.0,
        "source": "cash_cancel_race", "status": status,
        "protective_order_ids": list(protective_ids or []),
        "protective_exit_order_id": (protective_ids or [""])[-1]
        if protective_ids else "",
        "protective_exit_target": 43, "exit_receipt_ids": [],
        "exit_booked_qty": booked, "exit_pnl_cents": 0.0,
        "operator_state": "operator_pending"}]}
    return s

def set_resting(sells):
    BOOK["orders"] = [dict(o, ticker=TK, action="sell") for o in sells]

# 20a  _quarantine_open_qty = admitted - booked, excludes resolved
s = qbot_with_rec(booked=2.0)
check(s._quarantine_open_qty(TK) == 3.0,
      "20a open-qty = admitted 5 - booked 2 = 3 (got %s)"
      % s._quarantine_open_qty(TK))
s2 = qbot_with_rec(booked=5.0, status="resolved")
check(s2._quarantine_open_qty(TK) == 0.0, "20a resolved excluded")

# 20b  placement initially FAILS, next cycle succeeds, confirmed after
#      the posted order is GET-reconciled (fill_count==receipts) next cycle
s = qbot_with_rec()                # no protective ids yet
reset(orders=[], positions=[], fills=[], order_resp={})
place_state = {"fail": True}
async def pfail(tk, action, side, price, count, post_only=True):
    s.placed.append({"tk": tk, "action": action, "price": price,
                     "count": count})
    if place_state["fail"]:
        return "", {"_error": "post_only_cross"}
    r = await _api_post(None, None, None, None,
                        {"ticker": tk, "action": action, "side": side,
                         "yes_price": price, "count": count}, None)
    return r["order"]["order_id"], r
s.place_order = pfail
run(s._quarantine_ensure_coverage(TK))
check(not s.unmatched_holdings[TK][0].get("_resting_confirmed"),
      "20b placement failed -> not confirmed, retained")
check(bool(evs(s, "quarantine_protective_place_failed")),
      "20b failed placement is loud")
place_state["fail"] = False
run(s._quarantine_ensure_coverage(TK))          # posts (awaits reconcile)
check(s.unmatched_holdings[TK][0].get("_resting_confirmed") is False,
      "20b successful post AWAITS reconciliation (not ack-confirmed)")
check(len([x for x in s.placed if x["action"] == "sell"
           and x["count"] == 5]) == 2,
      "20b two attempts total (1 fail + 1 success), no over-post")
run(s._quarantine_ensure_coverage(TK))          # GET-reconciles -> confirmed
check(s.unmatched_holdings[TK][0].get("_resting_confirmed") is True,
      "20b next cycle reconciles the posted order -> CONFIRMED")
# 20c confirmed protective exit remains -> no duplicate
run(s._quarantine_ensure_coverage(TK))
check(len([x for x in s.placed if x["action"] == "sell"
           and x["count"] == 5]) == 2,
      "20c confirmed exit remains -> NO duplicate posted")

# 20d protective exit ABSENT + UNKNOWN exact status -> NO blind replacement
s = qbot_with_rec(protective_ids=["OLD-PX"])
reset(orders=[], positions=[], fills=[], order_resp={})   # GET(OLD-PX)->None
run(s._quarantine_ensure_coverage(TK))
reps = [x for x in s.placed if x["action"] == "sell"]
check(len(reps) == 0,
      "20d absent + UNKNOWN status -> NO blind replacement (absence != cancel)")
check(bool(evs(s, "quarantine_coverage_unknown")), "20d loud UNKNOWN alert")
check(s.unmatched_holdings[TK][0].get("_resting_confirmed") is False,
      "20d fail closed (not confirmed)")

# 20d2 absent + CONFIRMED cancellation + complete zero-fill census ->
#      exactly one replacement of the exact remainder
s = qbot_with_rec(protective_ids=["OLD-PX"])
reset(orders=[], positions=[], fills=[],
      order_resp={"OLD-PX": {"order": {"status": "canceled",
                                       "fill_count_fp": 0,
                                       "remaining_count_fp": 0}}})
run(s._quarantine_ensure_coverage(TK))
reps = [x for x in s.placed if x["action"] == "sell"]
check(len(reps) == 1 and reps[0]["count"] == 5 and reps[0]["price"] == 43,
      "20d2 confirmed cancel + complete census -> one replacement of 5 @ 43")

# 20e reconciled partial resting cover -> repost exactly the uncovered
s = qbot_with_rec(protective_ids=["PX-A"])
reset(orders=[], positions=[], fills=[],
      order_resp={"PX-A": {"order": {"status": "resting",
                                     "fill_count_fp": 0,
                                     "remaining_count_fp": 3}}})   # 3 of 5
run(s._quarantine_ensure_coverage(TK))
reps = [x for x in s.placed if x["action"] == "sell"]
check(len(reps) == 1 and reps[0]["count"] == 2,
      "20e reconciled partial cover 3 -> repost exactly the uncovered 2")

# 20f resting order with a PARTIAL-FILL LAG (fill_count 3, remaining 2) but
#     its receipts have NOT arrived -> reconciliation MISMATCH -> UNKNOWN,
#     NO repost (posting the "missing" 3 would oversell: 3+2+3 > 5). This is
#     the exact Blocker-1 oversell race.
s = qbot_with_rec(protective_ids=["PX-A"])
reset(orders=[], positions=[], fills=[],
      order_resp={"PX-A": {"order": {"status": "resting",
                                     "fill_count_fp": 3,
                                     "remaining_count_fp": 2}}})   # receipts 0
run(s._quarantine_ensure_coverage(TK))
check(not [x for x in s.placed if x["action"] == "sell"],
      "20f resting fill_count 3 but receipts 0 -> MISMATCH UNKNOWN, no repost")
check(bool(evs(s, "quarantine_coverage_unknown")), "20f loud UNKNOWN alert")
check(s.unmatched_holdings[TK][0].get("_resting_confirmed") is False,
      "20f fail closed (not confirmed)")

# 20g REAL naked-tooth cadence: held 5, no protective sell in the book ->
#     quarantine-specific protection, NOT old-Position heal, NOT silent.
s = make_poll_bot()
p = active_exit_pos()
p.exit_filled_qty = 5
p.entry_qty = 5
s.positions[TK] = p              # old completed position still present
s.unmatched_holdings = {TK: [{
    "ticker": TK, "buy_receipt_id": "BR", "buy_order_id": "B-RACE",
    "qty": 5.0, "price": 30, "exchange_ts": 1700.0,
    "terminal_cash_ts": 1600.0, "local_ts": 0.0,
    "source": "cash_cancel_race", "status": "quarantined",
    "protective_order_ids": [], "protective_exit_order_id": "",
    "protective_exit_target": 43, "exit_receipt_ids": [],
    "exit_booked_qty": 0.0, "exit_pnl_cents": 0.0,
    "operator_state": "operator_pending"}]}
async def tg(sess, ak, pk, path, rl):
    if "/portfolio/orders" in path and "status=resting" in path:
        return {"orders": [dict(o) for o in BOOK["orders"]]}
    if "/markets/" in path:
        return {"market": {"status": "active"}}
    return await _api_get(sess, ak, pk, path, rl)
set_resting([])
M.api_get = tg
try:
    for _ in range(2):
        run(s._naked_tooth_scan({TK: {"qty": 5.0}}, {TK: []}))
finally:
    M.api_get = _api_get
check(not evs(s, "naked_tooth_heal"),
      "20g tooth NEVER healed the old Position")
check(bool(evs(s, "naked_tooth_quarantine_protected")),
      "20g tooth logged quarantine protection (not silent defer)")
check(bool(evs(s, "quarantine_protective_posted")),
      "20g quarantine-specific protective exit was posted from raced basis")
check(p.entry_price == 51 and p.entry_qty == 5,
      "20g completed Position untouched (basis 51)")

# ======================================================================
print("--- 21. REV6.3 restart quarantine refuses new buys ---")
# ======================================================================
import tempfile as _tf, os as _o2
_f = _tf.NamedTemporaryFile(delete=False, suffix=".json")
_f.close()
_op = M.V4_RESTING_FILE
M.V4_RESTING_FILE = _f.name
try:
    s1 = make_poll_bot()
    s1._window_open = {}
    s1.completion_reprice = False
    s1.pair_governor_scoot = False
    s1.unmatched_holdings = {TK: [{
        "ticker": TK, "buy_receipt_id": "BR", "buy_order_id": "B-RACE",
        "qty": 5.0, "price": 30, "status": "quarantined",
        "protective_order_ids": ["PX"], "protective_exit_order_id": "PX",
        "protective_exit_target": 43, "exit_booked_qty": 0.0,
        "exit_pnl_cents": 0.0, "operator_state": "operator_pending"}]}
    setattr(s1, "_save_v4_resting",
            types.MethodType(M.LiveV3._save_v4_resting, s1))
    s1._save_v4_resting()
    # fresh engine restores, then a REAL buy placement is attempted
    s2 = make_poll_bot()
    s2._window_open = {}
    s2.unmatched_holdings = {}
    for nm in ("_load_v4_resting", "place_order", "_place_order_unlocked"):
        setattr(s2, nm, types.MethodType(getattr(M.LiveV3, nm), s2))
    s2.books = {}
    s2.event_tickers = {}
    s2.ticker_to_event = {}
    s2.event_start_time = {TK.rsplit("-", 1)[0]: 9_999_999_999}
    s2._events_live = set()
    s2._start_conflict = set()
    s2.fused_gun = False
    s2.freeze_at_gun = False
    s2.maker_only_entry = True
    s2._is_match_live = lambda et: False
    s2._horizon_state = lambda et: (False, 0)
    s2._load_v4_resting()
    check(s2.unmatched_holdings.get(TK), "21 quarantine restored")
    oid, resp = run(s2.place_order(TK, "buy", "yes", 45, 5, post_only=True))
    check(oid == "", "21 restored quarantine REFUSES a new post-only buy")
    check((resp or {}).get("_error") == "quarantine_buy_refused",
          "21 refusal reason is quarantine_buy_refused (got %s)"
          % (resp or {}).get("_error"))
    check(bool([d for (e, d, t) in s2.logs
                if e == "quarantine_buy_refused"]),
          "21 quarantine_buy_refused emitted")
    check(TK not in s2.positions, "21 no Position created")
    check(s2._cycle_count.get(TK, 0) == 0, "21 no cycle increment")
finally:
    M.V4_RESTING_FILE = _op
    try:
        _o2.remove(_f.name)
    except OSError:
        pass

# ======================================================================
print("--- 22. REV6.1.1.2 D1: GET-reconciled coverage + hard invariant ---")
# ======================================================================
# EVERY protective order is GET-reconciled: its fill_count_fp must equal
# the exact per-oid receipt sum before its resting remainder counts as
# cover. Any mismatch/malformed/incomplete/unavailable => UNKNOWN (no
# repost). booked + confirmed resting cover may never exceed the holding
# (a breach is a NAMED halt). The resting book's remaining is never
# trusted on its own.
def qbot(qty=5.0, booked=0.0, protective_ids=None, price=30, target=43,
         operator_state="operator_pending"):
    s = make_bot()
    s.unmatched_holdings = {TK: [{
        "ticker": TK, "buy_receipt_id": "BR", "buy_order_id": "B-RACE",
        "qty": qty, "price": price, "status": "quarantined",
        "protective_order_ids": list(protective_ids or []),
        "protective_exit_order_id": (protective_ids or [""])[-1]
        if protective_ids else "", "protective_exit_target": target,
        "exit_receipt_ids": [], "exit_booked_qty": booked,
        "exit_pnl_cents": 0.0, "operator_state": operator_state,
        "_await_oids": []}]}
    return s

def qr(s):
    return s.unmatched_holdings[TK][0]

def nsells(s):
    return len([x for x in s.placed if x["action"] == "sell"])

def ordr(status, fill, remaining):
    return {"order": {"status": status, "fill_count_fp": fill,
                      "remaining_count_fp": remaining}}

# 22.0  initial post: empty book -> post full open once, reconcile-confirm
#       on the next cycle (the posted order GETs as resting fill_count 0)
s = qbot()
reset(orders=[], positions=[], fills=[], order_resp={})
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 1 and s.placed[0]["count"] == 5,
      "22.0 initial protective post = full open once")
check(qr(s).get("_resting_confirmed") is False, "22.0 bare post not yet confirmed")
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 1, "22.0 posted order reconciles -> NO duplicate")
check(qr(s).get("_resting_confirmed") is True, "22.0 reconcile-confirmed next cycle")

# ---- Regression A: active resting, fill_count 3 / remaining 2, receipts
#      temporarily zero -> reconciliation MISMATCH -> UNKNOWN, no repost ----
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 3, 2)})
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 0,
      "A: resting fill_count 3 but receipts 0 -> UNKNOWN, no repost")
check(len(evs(s, "quarantine_coverage_unknown")) == 1, "A: loud UNKNOWN")
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 0 and len(evs(s, "quarantine_coverage_unknown")) == 2,
      "A: persists every cycle, still no repost")

# ---- Regression B: same case AFTER exact receipts for 3 arrive ->
#      booked 3 + reconciled resting 2, no repost, confirmed ----
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[],
      fills=[rc("R3", "PX", 3, 43, ts=1600)],
      order_resp={"PX": ordr("resting", 3, 2)})
run(s._quarantine_ensure_coverage(TK))
check(abs(float(qr(s).get("exit_booked_qty")) - 3) < 1e-6, "B: booked 3 from receipts")
check(nsells(s) == 0, "B: booked 3 + reconciled resting 2 = 5 -> no repost")
check(qr(s).get("_resting_confirmed") is True, "B: confirmed once reconciled")

# ---- Regression C: executed fill_count 5 but receipt sum 0 (or 2) ->
#      UNKNOWN, no repost ----
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("executed", 5, 0)})
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 0, "C: executed fill_count 5 vs receipts 0 -> UNKNOWN, no repost")
check(bool(evs(s, "quarantine_coverage_unknown")), "C: loud UNKNOWN")
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[],
      fills=[rc("R2", "PX", 2, 43, ts=1600)],
      order_resp={"PX": ordr("executed", 5, 0)})
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 0, "C: executed fill_count 5 vs receipts 2 -> UNKNOWN, no repost")

# ---- Regression D: canceled fill_count 3 with receipt sum 3 ->
#      book 3, repost exactly 2 once ----
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[],
      fills=[rc("R3", "PX", 3, 43, ts=1600)],
      order_resp={"PX": ordr("canceled", 3, 0)})
run(s._quarantine_ensure_coverage(TK))
check(abs(float(qr(s).get("exit_booked_qty")) - 3) < 1e-6, "D: booked the reconciled 3")
check(nsells(s) == 1 and s.placed[-1]["count"] == 2,
      "D: canceled 3 reconciled -> repost exactly the remaining 2 once")
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 1, "D: remainder reposted only once")

# ---- Regression E: malformed receipt belonging to the oid -> UNKNOWN ----
s = qbot(protective_ids=["PX"])
# a fill for PX with NO price field -> canonicalizes to a malformed receipt
reset(orders=[], positions=[],
      fills=[{"fill_id": "FM", "order_id": "PX", "action": "sell",
              "count_fp": 3, "created_time": 1600}],
      order_resp={"PX": ordr("canceled", 3, 0)})
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 0, "E: malformed receipt for the oid -> UNKNOWN, no repost")
check(bool(evs(s, "quarantine_coverage_unknown")), "E: loud UNKNOWN")

# ---- Regression F: resting coverage 6 against holding 5 ->
#      NAMED invariant breach, not covered ----
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 0, 6)})
run(s._quarantine_ensure_coverage(TK))
check(bool(evs(s, "quarantine_oversell_invariant_breach")),
      "F: resting cover 6 > holding 5 -> NAMED invariant breach")
check(nsells(s) == 0, "F: breach -> no new order")
check(qr(s).get("_resting_confirmed") is False, "F: breach -> NOT covered")
check(qr(s).get("operator_state") == "operator_pending", "F: operator_pending armed")

# ---- Regression G: booked 3 + resting 3 against holding 5 -> breach ----
s = qbot(protective_ids=["PX-EX", "PX-RS"])
reset(orders=[], positions=[],
      fills=[rc("R3", "PX-EX", 3, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 3, 0),
                  "PX-RS": ordr("resting", 0, 3)})
run(s._quarantine_ensure_coverage(TK))
check(abs(float(qr(s).get("exit_booked_qty")) - 3) < 1e-6, "G: booked the executed 3")
check(bool(evs(s, "quarantine_oversell_invariant_breach")),
      "G: booked 3 + resting 3 = 6 > holding 5 -> NAMED invariant breach")
check(nsells(s) == 0, "G: breach -> no new order")

# ---- Regression H: multiple oids; ONE UNKNOWN blocks ALL reposting ----
s = qbot(protective_ids=["PX-OK", "PX-UNK"])
reset(orders=[], positions=[], fills=[],
      order_resp={"PX-OK": ordr("resting", 0, 2)})   # PX-UNK GET -> None
run(s._quarantine_ensure_coverage(TK))
check(nsells(s) == 0,
      "H: one UNKNOWN protective order blocks ALL reposting for the record")
check(bool(evs(s, "quarantine_coverage_unknown")), "H: loud UNKNOWN")
check(qr(s).get("_resting_confirmed") is False, "H: not confirmed while any UNKNOWN")

# ---- Regression I: restart preserves UNKNOWN and breach state ----
# UNKNOWN preserved
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 3, 2)})
run(s._quarantine_ensure_coverage(TK))
s2 = qbot()
s2.unmatched_holdings = {TK: [
    {**x, "protective_order_ids": list(x.get("protective_order_ids") or [])}
    for x in s.unmatched_holdings[TK]]}
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 3, 2)})
run(s2._quarantine_ensure_coverage(TK))
check(nsells(s2) == 0 and bool(evs(s2, "quarantine_coverage_unknown")),
      "I: restart preserves UNKNOWN -> still no repost, still alerts")
check(qr(s2).get("operator_state") == "operator_pending",
      "I: operator_pending armed across restart (UNKNOWN)")
# breach preserved
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 0, 6)})
run(s._quarantine_ensure_coverage(TK))
s2 = qbot()
s2.unmatched_holdings = {TK: [
    {**x, "protective_order_ids": list(x.get("protective_order_ids") or [])}
    for x in s.unmatched_holdings[TK]]}
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 0, 6)})
run(s2._quarantine_ensure_coverage(TK))
check(bool(evs(s2, "quarantine_oversell_invariant_breach")) and nsells(s2) == 0,
      "I: restart preserves invariant breach -> named breach, no order")

# 22.6  the old-Position closure exception still requires reconciled
#       coverage (a bare ack cannot close the old cycle)
s, p, rget = race_env()
M.api_get = rget
try:
    run(s.check_fills())               # cycle 1: admit + post (pending)
    check(TK in s.positions,
          "22.6 old Position CANNOT close on an unreconciled post (pending)")
finally:
    M.api_get = _api_get

# ======================================================================
print("--- 23. REV6.1.1 D2: terminal-cash counts legacy ONCE ---")
# ======================================================================
def tc_bot():
    s = make_bot()
    for nm in ("_book_exit_receipts",):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

# 23.1  legacy 4 absorbed @1500; final new 1 @1600 completes -> terminal 1600
s = tc_bot()
p = make_pos(entry_qty=5, entry_price=51, exit_price=64)
p.exit_filled_qty = 4          # legacy already booked
receipts = [{"receipt_id": "H4", "order_id": "E-OLD", "action": "sell",
             "qty": 4.0, "price": 60.0, "ts": 1500.0, "missing": []},
            {"receipt_id": "N1", "order_id": "E-NEW", "action": "sell",
             "qty": 1.0, "price": 62.0, "ts": 1600.0, "missing": []}]
newq, newpnl, complete = s._book_exit_receipts(TK, p, receipts, source="t")
check(complete is True, "23.1 completion reached")
check(getattr(p, "_terminal_cash_ts", None) == 1600.0,
      "23.1 terminal_cash_ts = 1600 (NOT 1500) -> got %s"
      % getattr(p, "_terminal_cash_ts", None))
check(p.exit_filled_qty == 5, "23.1 no double-count (exit qty 5, not 9)")
# a buy at 1550 is therefore PRE-cash -> rejected
s2, p2, v2 = causal_case(1550, term_ts=p._terminal_cash_ts)
check(v2 == "unknown", "23.1 buy@1550 rejected as pre-cash (terminal 1600)")

# 23.2  clean non-legacy completion still stamps the crossing receipt
s = tc_bot()
p = make_pos(entry_qty=5, entry_price=51, exit_price=64)
p.exit_filled_qty = 0
receipts = [{"receipt_id": "A2", "order_id": "E-1", "action": "sell",
             "qty": 2.0, "price": 63.0, "ts": 1590.0, "missing": []},
            {"receipt_id": "B3", "order_id": "E-1", "action": "sell",
             "qty": 3.0, "price": 64.0, "ts": 1610.0, "missing": []}]
newq, newpnl, complete = s._book_exit_receipts(TK, p, receipts, source="t")
check(complete is True and getattr(p, "_terminal_cash_ts", None) == 1610.0,
      "23.2 non-legacy: terminal ts = the receipt that crossed entry_qty (1610)")

# ======================================================================
print("--- 24. REV6.1.1 D3: operator_pending blocks regardless of status ---")
# ======================================================================
def guard_bot(operator_state, protective_status):
    s = make_poll_bot()
    for nm in ("place_order", "_place_order_unlocked"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    s.books = {}
    s.event_tickers = {}
    s.ticker_to_event = {}
    s.event_start_time = {TK.rsplit("-", 1)[0]: 9_999_999_999}
    s._events_live = set()
    s._start_conflict = set()
    s.fused_gun = False
    s.freeze_at_gun = False
    s.maker_only_entry = True
    s._is_match_live = lambda et: False
    s._horizon_state = lambda et: (False, 0)
    s._pursuit_armed = lambda tk: False
    s.reentry_cycle_cap = 1
    s._cycle_count = {}
    s.unmatched_holdings = {TK: [{
        "ticker": TK, "buy_receipt_id": "BR", "qty": 5.0, "price": 30,
        "status": protective_status, "operator_state": operator_state,
        "protective_order_ids": ["PX"], "exit_booked_qty": 5.0}]}
    return s

# 24.1  unresolved + operator_pending -> refused
s = guard_bot("operator_pending", "quarantined")
oid, resp = run(s.place_order(TK, "buy", "yes", 45, 5, post_only=True))
check(oid == "" and (resp or {}).get("_error") == "quarantine_buy_refused",
      "24.1 unresolved + operator_pending -> refused")
# 24.2  RESOLVED protective exit + operator_pending -> STILL refused
s = guard_bot("operator_pending", "resolved")
oid, resp = run(s.place_order(TK, "buy", "yes", 45, 5, post_only=True))
check(oid == "" and (resp or {}).get("_error") == "quarantine_buy_refused",
      "24.2 resolved protective + operator_pending -> STILL refused")
# 24.3  explicitly operator_reconciled -> this guard no longer refuses
s = guard_bot("operator_reconciled", "resolved")
try:
    oid, resp = run(s.place_order(TK, "buy", "yes", 45, 5, post_only=True))
    _err = (resp or {}).get("_error")
except Exception:
    _err = "downstream_raised"     # a later, unrelated gate — not ours
check(_err != "quarantine_buy_refused"
      and not [d for (e, d, t) in s.logs if e == "quarantine_buy_refused"],
      "24.3 operator_reconciled -> quarantine guard released (no refusal)")

# ======================================================================
print("--- 25. REV6.1.1.3 D4: resolution ONLY through full reconciliation ---")
# ======================================================================
# Booking never resolves. A record resolves ONLY when booked == qty AND
# reconciled resting cover == 0 AND every protective oid is reconciled
# terminal. Oversell / UNKNOWN / mismatch can never resolve silently.
def malformed_fill(oid, qty, ts=1600):
    # a relevant receipt with NO price field -> canonicalizes to malformed
    return {"fill_id": "M-%s" % oid, "order_id": oid, "action": "sell",
            "count_fp": qty, "created_time": ts}

# 25.A booked 5 + reconciled resting cover 1 (qty 5) -> NAMED breach,
#      unresolved, NOT covered
s = qbot(protective_ids=["PX-EX", "PX-RS"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0),
                  "PX-RS": ordr("resting", 0, 1)})
run(s._quarantine_ensure_coverage(TK))
check(bool(evs(s, "quarantine_oversell_invariant_breach")),
      "25.A booked 5 + resting 1 -> NAMED breach")
check(qr(s).get("status") != "resolved", "25.A UNRESOLVED")
check(qr(s).get("_resting_confirmed") is False and nsells(s) == 0,
      "25.A not covered, no new order")

# 25.B booked 5 + a second protective oid UNKNOWN -> UNKNOWN, unresolved
s = qbot(protective_ids=["PX-EX", "PX-UNK"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0)})   # PX-UNK GET -> None
run(s._quarantine_ensure_coverage(TK))
check(bool(evs(s, "quarantine_coverage_unknown")), "25.B UNKNOWN alert")
check(qr(s).get("status") != "resolved",
      "25.B booked 5 but a second oid UNKNOWN -> UNRESOLVED (no silent close)")

# 25.C booked 5 + a malformed relevant receipt -> UNKNOWN, unresolved
s = qbot(protective_ids=["PX-EX"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600),
             malformed_fill("PX-EX", 1)],
      order_resp={"PX-EX": ordr("executed", 5, 0)})
run(s._quarantine_ensure_coverage(TK))
check(bool(evs(s, "quarantine_coverage_unknown")), "25.C UNKNOWN alert")
check(qr(s).get("status") != "resolved",
      "25.C malformed relevant receipt -> UNRESOLVED (census gate first)")

# 25.D booked receipts total 6 (qty 5) -> NAMED breach, unresolved
s = qbot(protective_ids=["PX-EX"])
reset(orders=[], positions=[],
      fills=[rc("R6", "PX-EX", 6, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 6, 0)})
run(s._quarantine_ensure_coverage(TK))
check(abs(float(qr(s).get("exit_booked_qty")) - 6) < 1e-6, "25.D booked 6")
check(bool(evs(s, "quarantine_oversell_invariant_breach")),
      "25.D booked 6 > holding 5 -> NAMED breach")
check(qr(s).get("status") != "resolved", "25.D UNRESOLVED")

# 25.E booked 5 + every oid exact terminal + zero cover -> RESOLVED
s = qbot(protective_ids=["PX-EX"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0)})
run(s._quarantine_ensure_coverage(TK))
check(qr(s).get("status") == "resolved",
      "25.E booked 5 + oid terminal (fill_count==receipts) + zero cover -> resolved")
check(bool(evs(s, "quarantine_exit_resolved")), "25.E named resolution event")

# 25.F old Position cannot close while the quarantine is breach/UNKNOWN
#     (_quarantine_covered gates the old-cycle closure; it must be False)
s = qbot(protective_ids=["PX-EX", "PX-RS"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0),
                  "PX-RS": ordr("resting", 0, 1)})        # breach
run(s._quarantine_ensure_coverage(TK))
check(s._quarantine_covered(TK) is False,
      "25.F breach -> _quarantine_covered False (old Position cannot close)")
s = qbot(protective_ids=["PX-EX", "PX-UNK"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0)})       # UNKNOWN
run(s._quarantine_ensure_coverage(TK))
check(s._quarantine_covered(TK) is False,
      "25.F UNKNOWN -> _quarantine_covered False (old Position cannot close)")

# 25.G after a breach: repeated polls AND restart keep checking + alerting
s = qbot(protective_ids=["PX-EX", "PX-RS"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0),
                  "PX-RS": ordr("resting", 0, 1)})
run(s._quarantine_ensure_coverage(TK))
run(s._quarantine_ensure_coverage(TK))
check(len(evs(s, "quarantine_oversell_invariant_breach")) == 2,
      "25.G breach re-alerts every cycle (no premature resolution silences it)")
s2 = qbot()
s2.unmatched_holdings = {TK: [
    {**x, "protective_order_ids": list(x.get("protective_order_ids") or [])}
    for x in s.unmatched_holdings[TK]]}
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0),
                  "PX-RS": ordr("resting", 0, 1)})
run(s2._quarantine_ensure_coverage(TK))
check(qr(s2).get("status") != "resolved"
      and bool(evs(s2, "quarantine_oversell_invariant_breach")),
      "25.G restart preserves the breach -> still unresolved, still alerts")

# 25.H negative fill_count or negative remaining -> UNKNOWN
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", -1, 2)})
run(s._quarantine_ensure_coverage(TK))
check(bool(evs(s, "quarantine_coverage_unknown")) and nsells(s) == 0,
      "25.H negative fill_count -> UNKNOWN, no repost")
s = qbot(protective_ids=["PX"])
reset(orders=[], positions=[], fills=[], order_resp={"PX": ordr("resting", 0, -2)})
run(s._quarantine_ensure_coverage(TK))
check(bool(evs(s, "quarantine_coverage_unknown")) and nsells(s) == 0,
      "25.H negative remaining -> UNKNOWN, no repost")

# 25.I exact terminal resolution is idempotent
s = qbot(protective_ids=["PX-EX"])
reset(orders=[], positions=[],
      fills=[rc("R5", "PX-EX", 5, 43, ts=1600)],
      order_resp={"PX-EX": ordr("executed", 5, 0)})
run(s._quarantine_ensure_coverage(TK))
check(qr(s).get("status") == "resolved", "25.I first pass resolves")
pnl0 = qr(s).get("exit_pnl_cents")
n0 = len(evs(s, "quarantine_exit_resolved"))
run(s._quarantine_ensure_coverage(TK))
run(s._quarantine_ensure_coverage(TK))
check(qr(s).get("status") == "resolved"
      and qr(s).get("exit_pnl_cents") == pnl0
      and len(evs(s, "quarantine_exit_resolved")) == n0 and nsells(s) == 0,
      "25.I resolved record is idempotent (no re-book, no re-resolve, no post)")

print("\n%s" % ("ALL REVIEW-FIX TESTS PASS" if not fails
                 else "*** %d FAILURE(S)" % fails))
sys.exit(1 if fails else 0)
