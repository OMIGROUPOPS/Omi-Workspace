#!/usr/bin/env python3
"""[READ-ONLY] Night-1 rollups: Metric A session-scoped, combined distribution,
riser/faller FV split, fv_observe accumulation, repriceable counter."""
import json
from collections import defaultdict

BOOT = 1783215168.0   # aba83af 21:32:48 ET Jul 4
END = 1783262384.0    # 733341f restart 10:39:44 ET Jul 5
LOG = "logs/live_v3_20260704.jsonl"

fills, latch, wopen, emfb = {}, {}, {}, {}
for l in open(LOG, encoding="utf-8", errors="replace"):
    if '"event"' not in l:
        continue
    try:
        o = json.loads(l)
    except Exception:
        continue
    ts = o["ts_epoch"]
    e, tk, d = o["event"], o.get("ticker") or "", o.get("details", {})
    if e == "window_open_set" and tk and tk not in wopen:
        wopen[tk] = d.get("price")
    if ts < BOOT or ts > END:
        continue
    if e == "entry_filled" and tk and tk not in fills:
        fills[tk] = {"ts": ts, "fill": d.get("fill_price"), "dir": d.get("direction"),
                     "play": d.get("play_type"), "emfb": d.get("entry_minus_fv_burst")}
    elif e == "match_live_detected" and d.get("event"):
        latch.setdefault(d["event"], ts)
    elif e == "fv_burst_anchor" and tk:
        emfb[tk] = d.get("entry_minus_fv_burst")

# Metric A session
viol = []
for tk, f in fills.items():
    ev = tk.rsplit("-", 1)[0]
    if ev in latch and f["ts"] > latch[ev] + 300:
        viol.append((tk, round((f["ts"] - latch[ev]) / 60, 1), f["fill"], f["play"]))
print(f"METRIC A (session {len(fills)} fills, {len(latch)} latches): {len(viol)} past latch+300s")
for v in viol:
    print("   ", v)

# combined distribution
ev_f = defaultdict(list)
for tk, f in fills.items():
    ev_f[tk.rsplit("-", 1)[0]].append(f["fill"] or 0)
combos = [sum(v[:2]) for v in ev_f.values() if len(v) >= 2]
b = {"<=97": 0, "98-100": 0, ">100": 0}
for c in combos:
    b["<=97" if c <= 97 else ("98-100" if c <= 100 else ">100")] += 1
print(f"\nCOMBINED distribution (n={len(combos)} pairs): {b}")
print("  exactly 97:", sum(1 for c in combos if c == 97), "| <=95:", sum(1 for c in combos if c <= 95))

# riser/faller FV split (session fills with emfb)
r, fa = [], []
for tk, f in fills.items():
    e0 = f["emfb"] if f["emfb"] is not None else emfb.get(tk)
    if e0 is None:
        continue
    (fa if ((f["dir"] == "underdog") or ((f["fill"] or 50) < 50)) else r).append(e0)
import statistics as st
for name, xs in (("riser", r), ("faller", fa)):
    if xs:
        print(f"\nFV split {name}: N={len(xs)} mean_emfb={st.mean(xs):+.1f}c "
              f"(neg=under FV=good) under-FV {sum(1 for x in xs if x < 0)}/{len(xs)} "
              f"({100*sum(1 for x in xs if x < 0)/len(xs):.0f}%)")

# fv_observe riser accumulation (all logs last 7)
import glob
n = 0
for lp in sorted(glob.glob("logs/live_v3_*.jsonl"))[-7:]:
    for l in open(lp, encoding="utf-8", errors="replace"):
        if "fv_burst_anchor" not in l or '"event"' not in l:
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        if (o["details"].get("entry_price") or 0) >= 50 and o["details"].get("fv_mid") is not None:
            n += 1
print(f"\nfv_observe riser accumulation: {n} / ~100 gate")

# repriceable counter from monitor jsonl
t = f0 = 0
try:
    for l in open("/root/Omi-Workspace/.claude/live_20260705/live_validation.jsonl",
                  encoding="utf-8", errors="replace"):
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("type") == "bid_grade":
            if o.get("repriceable"):
                t += 1
            else:
                f0 += 1
except Exception:
    pass
print(f"repriceable counter (cumulative bid_grades): true {t} / false {f0}")
