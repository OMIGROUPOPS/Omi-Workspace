"""Per-category validation pass (frugal, row-group streaming) for the full per-minute universe.
Reports: distinct matches/sides + 2:1 check, time window, no-trade fraction (price_high NaN %),
and per-cell sides:matches inflation (the c<=50 double-count the match-weighted gate must kill).
Run on the VPS where the full parquet lives. Memory-frugal: streams row groups, only 5 columns.
"""
import argparse, datetime as dt
from collections import defaultdict
import pyarrow.parquet as pq
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
ap.add_argument("--category", required=True)
args = ap.parse_args()

pf = pq.ParquetFile(args.input)
ev, tk = set(), set()
ev_sides = defaultdict(set)
tmin, tmax = 10**12, 0
n_rows = 0
n_price_nan = 0
ev_at = defaultdict(set)   # cell -> set(events)
tk_at = defaultdict(set)   # cell -> set(tickers)

for i in range(pf.num_row_groups):
    t = pf.read_row_group(i, columns=["category", "event_ticker", "ticker",
                                       "minute_ts", "yes_bid_close", "price_high"]).to_pydict()
    for cat, e, k, ts, yb, ph in zip(t["category"], t["event_ticker"], t["ticker"],
                                     t["minute_ts"], t["yes_bid_close"], t["price_high"]):
        if cat != args.category:
            continue
        n_rows += 1
        ev.add(e); tk.add(k); ev_sides[e].add(k)
        if ts < tmin: tmin = ts
        if ts > tmax: tmax = ts
        if ph is None or (isinstance(ph, float) and ph != ph):
            n_price_nan += 1
        if yb is not None:
            c = round(yb * 100)
            if 5 <= c <= 94:
                ev_at[c].add(e); tk_at[c].add(k)

sides = [len(v) for v in ev_sides.values()]
print(f"=== {args.category} ===")
print(f"rows={n_rows:,}  matches(event)={len(ev)}  sides(ticker)={len(tk)}  "
      f"sides/match mean={np.mean(sides):.2f}  matches!=2sides={sum(1 for s in sides if s!=2)}")
print(f"window {dt.date.fromtimestamp(tmin)} -> {dt.date.fromtimestamp(tmax)}")
print(f"no-trade fraction (price_high NaN): {n_price_nan/n_rows*100:.1f}%  "
      f"({n_rows-n_price_nan:,} real prints of {n_rows:,} minutes)")
print("cell : matches sides infl(sides/matches)")
for c in [5, 10, 20, 30, 40, 48, 50, 52, 60, 70, 80, 90, 94]:
    m, s = len(ev_at.get(c, ())), len(tk_at.get(c, ()))
    print(f"  {c:3d} : {m:5d} {s:5d}  {s/m if m else 0:.2f}")
allm = sum(len(v) for v in ev_at.values()); alls = sum(len(v) for v in tk_at.values())
mid = [c for c in ev_at if 41 <= c <= 60]
midm = sum(len(ev_at[c]) for c in mid); mids = sum(len(tk_at[c]) for c in mid)
print(f"avg infl all cells {alls/allm:.3f}  | mid-cells(41-60) infl {mids/midm if midm else 0:.3f}")
