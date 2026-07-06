#!/usr/bin/env python3
"""RISER LIVE VERDICT — today's session (12:15 boot -> now), the disarm rule's own bars
measured on the live tape. Bars (SCOREBOARD_20260706.md, pre-registered 07-05):
 (a) riser fill-discount vs best-bid-at-post: median >= +2c CHALL/ITF (disarm if < 1c)
 (b) retention >= 60% of riser posts fill (vs 91% baseline at depth 0)
 (e) erosion: fills above first-posted price < 25%"""
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
SESS = "vps/sess2.jsonl"
hm = lambda e: datetime.fromtimestamp(e, ET).strftime("%H:%M")

posts = defaultdict(list)         # tk -> [(ts, px)]
vplace = defaultdict(list)        # tk -> [(ts, book_bid)]
fills = {}                        # tk -> (ts, px)
cat_of = {}
for line in open(SESS, encoding="utf-8"):
    try: o = json.loads(line)
    except: continue
    e, tk, d, ts = o.get("event"), o.get("ticker") or "", o.get("details", {}), o.get("ts_epoch", 0)
    if e == "order_placed" and d.get("action") == "buy" and tk and d.get("price") is not None:
        posts[tk].append((ts, d["price"]))
    elif e == "v4_place" and tk:
        if d.get("book_bid") is not None: vplace[tk].append((ts, d["book_bid"]))
        if d.get("cat"): cat_of[tk] = d["cat"]
    elif e == "entry_filled" and tk and tk not in fills:
        fills[tk] = (ts, d.get("fill_price"))

def med(v):
    v = sorted(x for x in v if x is not None); return v[len(v)//2] if v else None

# riser = first post >= 50 (role fallback convention), CHALL/ITF only per bar (a)
rows = []
posted_risers = 0
for tk, ps in posts.items():
    ps.sort()
    first_px = ps[0][1]
    if first_px < 50: continue
    c = cat_of.get(tk, "")
    if c not in ("ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"): continue
    posted_risers += 1
    f = fills.get(tk)
    if not f or f[1] is None: continue
    bb = [b for t, b in sorted(vplace.get(tk, [])) if t <= f[0]]
    disc = (bb[-1] - f[1]) if bb else None
    rows.append({"tk": tk[-16:], "cat": c, "fill": f[1], "t": hm(f[0]),
                 "first_post": first_px, "eroded": f[1] > first_px, "disc": disc})

n = len(rows)
disc = med([r["disc"] for r in rows])
ero = sum(1 for r in rows if r["eroded"])
ret = n / max(1, posted_risers)
print(f"LIVE SESSION 12:15->{datetime.now(ET).strftime('%H:%M')} ET | riser posts (>=50 first-post, CHALL/ITF): {posted_risers} | filled: {n} (retention {ret:.0%})")
print(f"(a) fill-discount vs best-bid-at-post: median {disc}c (n={sum(1 for r in rows if r['disc'] is not None)}) — bar >=+2, disarm <1")
print(f"(e) erosion: {ero}/{n} = {100*ero//max(1,n)}% — bar <25%")
print(f"(b) retention {ret:.0%} — bar >=60%")
for r in rows: print("   ", r)
