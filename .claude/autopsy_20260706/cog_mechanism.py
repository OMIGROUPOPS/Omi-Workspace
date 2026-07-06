#!/usr/bin/env python3
"""combined_over_goal mechanism classifier — per violation event, from log lines.
For each event: leg1/leg2 fills (ts, px), bound = 97 - leg1_px, then the leg2 story:
what was leg2 resting at when leg1 filled, did reaim_on_sibling_arrival fire, was the
fill adopted via reconcile (cancel-fill race), was it same-tick with leg1."""
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
BOOT = 1783309839.0
def hm(e): return datetime.fromtimestamp(e, ET).strftime("%H:%M:%S") if e else "?"

vio = []
seen = set()
for line in open("vps/live_validation.jsonl", encoding="utf-8"):
    try: o = json.loads(line)
    except: continue
    if o.get("type") == "violation" and (o.get("ts") or 0) >= BOOT and o.get("cls") == "combined_over_goal":
        if o.get("key") in seen: continue
        seen.add(o.get("key")); vio.append(o)

EVENTS = {"entry_filled","order_placed","order_cancelled","reaim_sibling_arrival",
          "leg2_reshuffle_reaim","reconcile_v4_adopted","completion_booking_adoption",
          "v4_move_repost","v4_place","cancel_fill_race","cancel_resolve_unresolved",
          "sibling_repost_placed","entry_cancel_partial"}
by_ev = defaultdict(list)
for line in open("vps/session_since_boot.jsonl", encoding="utf-8"):
    try: o = json.loads(line)
    except: continue
    if o.get("event") not in EVENTS: continue
    tk = o.get("ticker") or ""
    if not tk: continue
    by_ev[tk.rsplit("-", 1)[0]].append(o)

out = []
for v in vio:
    evt = v.get("ticker") or v.get("event") or ""
    ev = evt if evt.count("-") == 1 else evt.rsplit("-", 1)[0]
    pool = sorted(by_ev.get(ev, []), key=lambda o: o.get("ts_epoch", 0))
    fills_seq = [o for o in pool if o["event"] == "entry_filled"]
    if len(fills_seq) < 2:
        out.append({"ev": ev, "detail": v.get("detail"), "note": f"only {len(fills_seq)} entry_filled in log", "n_fills": len(fills_seq)})
        continue
    # take the two fills straddling the violation ts (the pair the monitor graded)
    vt = v["ts"]
    prior = [o for o in fills_seq if o["ts_epoch"] <= vt + 5]
    l2 = prior[-1]; l1 = prior[-2] if len(prior) >= 2 else fills_seq[0]
    l1tk, l2tk = l1["ticker"], l2["ticker"]
    l1px = l1["details"].get("fill_price"); l2px = l2["details"].get("fill_price")
    l1ts, l2ts = l1["ts_epoch"], l2["ts_epoch"]
    bound = 97 - (l1px or 0)
    gap_s = round(l2ts - l1ts, 1)
    # leg2 resting order at the moment leg1 filled: last order_placed buy on l2tk before l1ts
    l2_orders = [o for o in pool if o["ticker"] == l2tk and o["event"] == "order_placed"
                 and o["details"].get("action") == "buy" and o["ts_epoch"] <= l1ts]
    resting_at_l1 = l2_orders[-1]["details"].get("price") if l2_orders else None
    # was leg2 fill adopted (reconcile) — adoption events within 3s of l2 fill
    adopted = any(o["event"] in ("reconcile_v4_adopted","completion_booking_adoption")
                  and o["ticker"] == l2tk and abs(o["ts_epoch"] - l2ts) < 3 for o in pool)
    race = any(o["event"] == "cancel_fill_race" and o["ticker"] == l2tk
               and abs(o["ts_epoch"] - l2ts) < 60 for o in pool)
    # reaim attempts on l2 between l1 fill and l2 fill
    reaims = [o for o in pool if o["ticker"] == l2tk and o["ts_epoch"] > l1ts and o["ts_epoch"] < l2ts
              and o["event"] in ("reaim_sibling_arrival","leg2_reshuffle_reaim","v4_move_repost","order_placed","order_cancelled")]
    reaim_summary = []
    for o in reaims[-8:]:
        d = o["details"]
        reaim_summary.append(f"{hm(o['ts_epoch'])} {o['event']}"
                             + (f" px={d.get('price')}" if d.get("price") is not None else "")
                             + (f" tgt={d.get('new_target')}" if d.get("new_target") is not None else "")
                             + (f" act={d.get('action')}" if d.get("action") else ""))
    # post-l1 orders above bound?
    post_l1_orders = [o for o in pool if o["ticker"] == l2tk and o["event"] == "order_placed"
                      and o["details"].get("action") == "buy" and l1ts < o["ts_epoch"] <= l2ts]
    post_l1_px = [o["details"].get("price") for o in post_l1_orders]
    mech = ("SAME_TICK_RACE" if gap_s <= 2 else
            "ADOPTED_CANCEL_FILL_RACE" if adopted or race else
            "REPOSTED_ABOVE_BOUND_POST_L1" if any((p or 0) > bound for p in post_l1_px) else
            "RESTING_ABOVE_BOUND_NEVER_REAIMED" if (resting_at_l1 or 0) > bound and not reaims else
            "REAIM_TOO_SLOW_OR_INSUFFICIENT")
    out.append({"ev": ev.replace("KX",""), "detail": v.get("detail"), "t": hm(vt),
                "l1": f"{l1tk[-8:]} {l1px}c @{hm(l1ts)}", "l2": f"{l2tk[-8:]} {l2px}c @{hm(l2ts)}",
                "gap_s": gap_s, "bound": bound, "l2_over_bound": (l2px or 0) - bound,
                "l2_resting_at_l1": resting_at_l1, "adopted": adopted, "cancel_fill_race": race,
                "post_l1_orders": post_l1_px, "reaims_between": reaim_summary, "mech": mech})

json.dump(out, open("cog_mechanisms.json", "w"), indent=1)
from collections import Counter
print(Counter(o.get("mech","NO_PAIR") for o in out))
for o in out:
    if "mech" not in o:
        print("NOPAIR", o["ev"], o["note"]); continue
    print(f"[{o['mech']:32s}] {o['ev']:34s} {o['t']} gap={o['gap_s']:>7}s bound={o['bound']} "
          f"l2_over={o['l2_over_bound']:+d} resting_at_l1={o['l2_resting_at_l1']} adopted={o['adopted']}")
    print(f"    l1={o['l1']}  l2={o['l2']}  post_l1_orders={o['post_l1_orders']}")
    for r in o["reaims_between"][-4:]:
        print(f"      {r}")
