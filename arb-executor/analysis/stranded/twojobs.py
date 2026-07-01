import json, glob, gzip, csv, os, collections
from datetime import datetime

LOG = "logs/live_v3_20260619.jsonl"

# ---- gather fills + placements per event ----
fills = {}      # ticker -> (ts_epoch, fill_price, cat, cell, play_type)
placed = collections.defaultdict(set)   # event -> set(legs placed)
filledlegs = collections.defaultdict(dict)  # event -> {leg: fill_price}
for L in open(LOG):
    try: d = json.loads(L)
    except: continue
    e = d.get("event"); det = d.get("details", {}); tk = d.get("ticker", "")
    if e == "order_placed" and det.get("action") == "buy":
        m = tk.rsplit("-", 1)
        if len(m) == 2: placed[m[0]].add(m[1])
    if e == "entry_filled":
        m = tk.rsplit("-", 1)
        if len(m) == 2:
            fills[tk] = (d.get("ts_epoch", 0), det.get("fill_price"), det.get("cell"), det.get("play_type"))
            filledlegs[m[0]][m[1]] = det.get("fill_price")

# ---- JOB 1: pairing rate ----
both = [ev for ev, legs in filledlegs.items() if len(legs) == 2]
single = [ev for ev, legs in filledlegs.items() if len(legs) == 1 and len(placed.get(ev, set())) == 2]
print("=== JOB 1: PAIRING RATE (today) ===")
tot = len(both) + len(single)
print("  both-legs filled: %d | single-leg (other placed, missed): %d | fill-both rate = %.0f%%" % (
    len(both), len(single), 100*len(both)/tot if tot else 0))
print("  single-leg misses (which leg floated):")
for ev in single[:15]:
    leg = list(filledlegs[ev].keys())[0]; missed = (placed[ev] - set(filledlegs[ev].keys()))
    sh = ev.replace("KXATPMATCH-26JUN19","").replace("KXWTAMATCH-26JUN19","").replace("KXWTACHALLENGERMATCH-26JUN19","wc:").replace("KXATPCHALLENGERMATCH-26JUN19","ac:")
    print("    %-14s held %s@%s  missed %s" % (sh, leg, filledlegs[ev][leg], ",".join(missed)))

# ---- JOB 2: entry vs FV (reconstructed from depth recorder) ----
# FV anchor = mid at last depth tick before the leg's first sustained >=8c move from premarket baseline
want = set(fills.keys())
ser = collections.defaultdict(list)
for f in glob.glob("data/durable/depth_recorder/depth_20260619_*.jsonl*"):
    op = gzip.open if f.endswith(".gz") else open
    try:
        with op(f, "rt") as fh:
            for L in fh:
                if not any(t in L for t in want): continue
                try: d = json.loads(L)
                except: continue
                tk = d.get("ticker")
                if tk in want and d.get("bid") is not None and d.get("ask") is not None:
                    m = re.search(r"(\d\d):(\d\d):(\d\d)", d["ts"]) if False else None
                    ser[tk].append((d["ts_epoch"], (d["bid"]+d["ask"])/2.0))
    except: pass
import re
for tk in ser: ser[tk].sort()

def fv_anchor(tk, fill_ep):
    rows = ser.get(tk, [])
    if len(rows) < 6: return None
    pre = [m for ep, m in rows if ep <= fill_ep]
    if len(pre) < 3: pre = [m for _, m in rows[:20]]
    base = sorted(pre)[len(pre)//2]
    for i, (ep, m) in enumerate(rows):
        if ep < fill_ep: continue
        if abs(m - base) >= 8:
            nxt = [mm for _, mm in rows[i:i+6]]
            if sum(1 for mm in nxt if abs(mm-base) >= 6) >= 3:
                return rows[i-1][1] if i > 0 else m
    return None

print("\n=== JOB 2: ENTRY vs FV-at-burst (reconstructed, all anchorable fills) ===")
rows_out = []
for tk, (ep, fp, cell, pt) in fills.items():
    if fp is None: continue
    fv = fv_anchor(tk, ep)
    if fv is None: continue
    delta = fp - fv
    ev = tk.rsplit("-", 1)[0]
    paired = len(filledlegs.get(ev, {})) == 2
    rows_out.append({"tk": tk, "fp": fp, "fv": fv, "delta": delta, "paired": paired, "cell": cell})

def avg(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return sum(xs)/len(xs) if xs else float("nan")
print("  anchorable fills: %d" % len(rows_out))
print("  mean entry-FV = %+.2fc (positive = filled ABOVE FV / no edge)" % avg([r["delta"] for r in rows_out]))
print("  PAIRED legs:  mean %+.2fc (n=%d)" % (avg([r["delta"] for r in rows_out if r["paired"]]), sum(1 for r in rows_out if r["paired"])))
print("  SOLO legs:    mean %+.2fc (n=%d)" % (avg([r["delta"] for r in rows_out if not r["paired"]]), sum(1 for r in rows_out if not r["paired"])))
print("  CHEAP fill<40: mean %+.2fc (n=%d) | FAVE fill>60: mean %+.2fc (n=%d) | MID: mean %+.2fc (n=%d)" % (
    avg([r["delta"] for r in rows_out if r["fp"]<40]), sum(1 for r in rows_out if r["fp"]<40),
    avg([r["delta"] for r in rows_out if r["fp"]>60]), sum(1 for r in rows_out if r["fp"]>60),
    avg([r["delta"] for r in rows_out if 40<=r["fp"]<=60]), sum(1 for r in rows_out if 40<=r["fp"]<=60)))
ds = sorted(r["delta"] for r in rows_out)
if ds:
    print("  distribution: p10=%+.0f p50=%+.0f p90=%+.0f | above-FV: %.0f%%  discount: %.0f%%" % (
        ds[len(ds)//10], ds[len(ds)//2], ds[9*len(ds)//10],
        100*sum(1 for d in ds if d>=1)/len(ds), 100*sum(1 for d in ds if d<=-1)/len(ds)))
