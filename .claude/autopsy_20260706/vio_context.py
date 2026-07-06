#!/usr/bin/env python3
"""Extract per-violation event context from the session log (local).
For each session violation (ts>=BOOT) pull every bot event for that ticker (and its sibling)
in a +/- window around the violation, so the function-call chain is provable from log lines."""
import json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
BOOT = 1783309839.0
SESS = "vps/session_since_boot.jsonl"
VALID = "vps/live_validation.jsonl"

def hm(e): return datetime.fromtimestamp(e, ET).strftime("%H:%M:%S") if e else "?"

vio = []
seen = set()
for line in open(VALID, encoding="utf-8"):
    try: o = json.loads(line)
    except: continue
    if o.get("type") == "violation" and (o.get("ts") or 0) >= BOOT:
        if o.get("key") in seen: continue
        seen.add(o.get("key")); vio.append(o)
print(f"session violations: {len(vio)}", file=sys.stderr)

# index session log by ticker and by event(prefix)
by_tk = defaultdict(list)
for line in open(SESS, encoding="utf-8"):
    try: o = json.loads(line)
    except: continue
    tk = o.get("ticker") or ""
    ev_field = o.get("details", {}).get("event") or ""
    key = tk or ev_field
    if not key: continue
    by_tk[key].append(o)
    if tk:
        by_tk[tk.rsplit("-", 1)[0]].append(o)

INTERESTING = {"order_placed","order_cancelled","order_canceled","v4_place","v4_move_repost",
               "join_queue","leg2_reshuffle_reaim","entry_filled","staircase_hold_place",
               "window_open_set","reaim_sibling_arrival","v4_repost_hold_same_price",
               "completion_booking_adoption","reconcile_v4_adopted","sibling_repost_placed",
               "premarket_walk_capped","match_live_detected","order_error","complete_cross_skip",
               "completion_no_attempt","v4_exit_posted","exit_filled","scalp_filled"}

out = []
for v in vio:
    tk = v.get("ticker") or v.get("event") or ""
    ev = tk if tk.count("-") == 1 else tk.rsplit("-", 1)[0]
    t = v["ts"]
    ctx = []
    pool = by_tk.get(ev, [])
    seen_ids = set()
    for o in pool:
        ts = o.get("ts_epoch", 0)
        if not (t - 2400 <= ts <= t + 300): continue
        if o.get("event") not in INTERESTING: continue
        oid = id(o)
        if oid in seen_ids: continue
        seen_ids.add(oid)
        ctx.append({"t": hm(ts), "ts": ts, "event": o["event"], "tk": (o.get("ticker") or "")[-14:],
                    "d": o.get("details", {})})
    ctx.sort(key=lambda x: x["ts"])
    out.append({"vio": {"cls": v["cls"], "t": hm(t), "ts": t, "tk": tk, "price": v.get("price"),
                        "conception": v.get("conception_cell"), "ceiling": v.get("ceiling"),
                        "ref": v.get("ref_source"), "detail": v.get("detail")},
                "context": ctx})

json.dump(out, open("vio_contexts.json", "w"), indent=1)
print(f"wrote vio_contexts.json: {len(out)} violations", file=sys.stderr)

# quick per-class digest
from collections import Counter
cls = Counter(v["vio"]["cls"] for v in out)
print(dict(cls))
for v in out[:3]:
    print("\n===", v["vio"]["detail"], "@", v["vio"]["t"])
    for c in v["context"][-14:]:
        dd = {k: c["d"].get(k) for k in ("price","action","reference_source","ref_source","aim","target",
              "conception_cell","reason","qty","fill_price","best_bid","best_ask","new_target","cap") if c["d"].get(k) is not None}
        print(f"  {c['t']} {c['event']:26s} {c['tk']:14s} {dd}")
