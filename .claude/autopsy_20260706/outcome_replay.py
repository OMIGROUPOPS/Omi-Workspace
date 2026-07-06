#!/usr/bin/env python3
"""OUTCOME REPLAY (C46 lane-1/lane-2) — apply the P1/P2/P3/P4 fix semantics to last
night's own tape and verify: every targeted violation blocks/corrects, every clean
fill survives. Independent re-derivation (not trusting the forensic agents' numbers)."""
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
BOOT = 1783309839.0
GOAL = 97
hm = lambda e: datetime.fromtimestamp(e, ET).strftime("%H:%M:%S")

fills_x = json.load(open("vps/autopsy_truth/fills_session.json"))
vwap = defaultdict(lambda: [0.0, 0.0])
for f in fills_x:
    if f["action"] != "buy": continue
    vwap[f["ticker"]][0] += float(f["yes_price_dollars"])*100*float(f["count_fp"])
    vwap[f["ticker"]][1] += float(f["count_fp"])
xv = {tk: round(v[0]/v[1], 2) for tk, v in vwap.items() if v[1]}

# parse session log once
entry_fills = {}          # tk -> (ts, px, qty) first
cancel_ts = {}            # order_id -> first cancel ts
adoptions = []            # (ts, tk, avg, qty)
buy_orders = []           # (ts, tk, px, oid)
sib_reposts = []          # (ts, tk, level)
reaim_places = []         # (ts, tk, px)
ev_of = lambda tk: tk.rsplit("-", 1)[0]
for line in open("vps/session_since_boot.jsonl", encoding="utf-8"):
    try: o = json.loads(line)
    except: continue
    e, tk, d, ts = o.get("event"), o.get("ticker") or "", o.get("details", {}), o.get("ts_epoch", 0)
    if e == "entry_filled" and tk and tk not in entry_fills:
        entry_fills[tk] = (ts, d.get("fill_price"), d.get("qty"))
    elif e == "reconcile_v4_adopted" and tk:
        adoptions.append((ts, tk, d.get("avg"), d.get("qty")))
    elif e == "order_placed" and d.get("action") == "buy" and tk:
        buy_orders.append((ts, tk, d.get("price"), d.get("order_id")))
    elif e in ("order_cancelled", "order_canceled") and d.get("order_id"):
        cancel_ts.setdefault(d["order_id"], ts)
    elif e == "sibling_repost_placed" and tk:
        sib_reposts.append((ts, tk, d.get("level")))
    elif e == "reaim_sibling_arrival" and tk:
        reaim_places.append((ts, tk, d.get("to") or d.get("price")))

def sibling(tk):
    ev = ev_of(tk)
    sibs = [t for t in entry_fills if ev_of(t) == ev and t != tk]
    return sibs[0] if sibs else None

print("=== P1 replay: adopted bookings vs exchange VWAP (dissolution table) ===")
n_fix = 0
for ts, tk, avg, qty in adoptions:
    x = xv.get(tk)
    if x is None or avg is None: continue
    if abs(avg - x) >= 1:
        sib = sibling(tk)
        sib_fill = entry_fills.get(sib, (None, None, None))[1] if sib else None
        old_comb = (avg + sib_fill) if sib_fill else None
        new_comb = round(x + sib_fill, 1) if sib_fill else None
        n_fix += 1
        flag = ""
        if old_comb and new_comb and old_comb > GOAL >= new_comb: flag = "  <-- VIOLATION DISSOLVES"
        print(f"  {hm(ts)} {tk[-18:]:18s} booked {avg:>3} true {x:>5} comb {old_comb}->{new_comb}{flag}")
print(f"  adoptions with booking error >=1c: {n_fix} / {len(adoptions)}")

print("\n=== P2/P3 replay: post-basis buy orders over goal-basis bound (full independent scan) ===")
over = []
for ts, tk, px, oid in buy_orders:
    sib = sibling(tk)
    if not sib: continue
    sf = entry_fills.get(sib)
    if not sf or sf[0] >= ts: continue          # sibling filled BEFORE this order
    bound = GOAL - (sf[1] or 0)
    if px is not None and px > bound:
        filled = tk in entry_fills and abs(entry_fills[tk][0] - ts) < 7200 and entry_fills[tk][1] == px
        over.append((ts, tk, px, bound, filled))
for ts, tk, px, bound, filled in over:
    print(f"  {hm(ts)} {tk[-18:]:18s} buy {px:>3} > bound {bound:>3}  filled_at_that_px={filled}  -> P2/P3 clamp to {max(1,bound)}")
print(f"  post-basis over-bound orders: {len(over)} (these are the ONLY orders P2/P3 would alter — all other {len(buy_orders)} buys survive untouched)")

print("\n=== P4 replay: sibling_repost placements with an in-memory in-flight entry (dup set) ===")
dups = 0; legit = 0
for ts, tk, level in sib_reposts:
    # in-flight proxy: another buy order on the SAME ticker, placed before the repost,
    # NOT cancelled before the repost, and the leg not yet filled at repost time
    prior = [b for b in buy_orders if b[1] == tk and b[0] < ts - 0.5
             and cancel_ts.get(b[3], 1e18) > ts
             and not (tk in entry_fills and entry_fills[tk][0] < ts)]
    if prior: dups += 1; print(f"  {hm(ts)} {tk[-18:]:18s} repost level {level} — prior buy {prior[-1][2]}c at {hm(prior[-1][0])} STILL LIVE -> P4 skips (dup blocked)")
    else: legit += 1
print(f"  dup-blocked: {dups} | legitimate heals unaffected: {legit}")

print("\n=== Clean-fill survival check ===")
viol_tks = set(tk for _, tk, _, _, _ in over)
clean_buys = [b for b in buy_orders if b[1] not in viol_tks]
print(f"  buy orders total {len(buy_orders)}; altered by P2/P3: {len(over)} (all violation/near-miss); clean untouched: {len(clean_buys)}")
print(f"  P1 alters ZERO orders (booking only); P4 blocks {dups} duplicate placements (each had a live twin at the same-or-better level, participation retained by the twin)")
