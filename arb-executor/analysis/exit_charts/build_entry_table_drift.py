#!/usr/bin/env python3
"""Drift-informed CANDIDATE entry table — encodes the lifecycle/drift surface read
(place early, shallow, mirror-respecting) into per-cell placement_minute + offset.
This is a CANDIDATE to be validated against the current T47-derived table via the
timing-aware per-match walk (drift_table_validate.py). NOT auto-deployed.

Drift read it encodes (from premarket_lifecycle_surface_midanchor_*.csv):
  - The catchable dip/drift is an EARLY-window phenomenon: fill_reach + deepen_frac
    decay monotonically T-240 -> T-2; the last ~30 min the price firms. So place
    EARLY (rest the shallow bid where the dip is most catchable).
  - Favorites drift UP, underdogs drift DOWN, mids oscillate — but in ALL bands the
    catch is early. So placement_minute = the earliest tbin where the cell's
    occ_N-weighted fill_reach >= 0.90 (clamped [60,240]).
  - Offset stays SHALLOW (1-3c), NOT f x D argmax: the deepest d in {1,2,3} whose
    early fill_reach at dbucket=-d still clears 0.80 (a bid that reliably fills),
    capped at 3. Deliberately shallow even on the cells T47 made deep (7-18c
    throughput) — the drift hypothesis is that shallow-early beats deep.

Output schema matches entry_table_percell.csv (drop-in): category,c,regime,
placement_minute,bid_offset_cents,expected_fill_rate,expected_net_roi_pct,fill_src.
Run: cd arb-executor && python3 analysis/exit_charts/build_entry_table_drift.py
"""
import os, csv
import pandas as pd, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POL = os.path.join(ROOT, "docs", "policy")
EC = os.path.join(ROOT, "analysis", "exit_charts")
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
PLACEMENT_DOMAIN = [60, 90, 120, 180, 240]   # the bot's placement_minute domain (<=240 cap)
FILL_PLACE = 0.90    # place at the earliest tbin whose occ-wt fill_reach clears this
FILL_OFFSET = 0.80   # offset = deepest shallow d whose early fill_reach clears this
OFFSET_CAP = 3       # shallow, anti-argmax


def regime_of(c):
    for hi, nm in [(15, "r05_14"), (25, "r15_24"), (35, "r25_34"), (45, "r35_44"),
                   (55, "r45_54"), (65, "r55_64"), (75, "r65_74"), (85, "r75_84"),
                   (100, "r85_94")]:
        if c < hi:
            return nm


def clamp_placement(tb):
    # map a surface tbin to the nearest placement_minute in the bot's domain (round up to catch early)
    for p in PLACEMENT_DOMAIN:
        if tb <= p:
            return p
    return 240


reg = pd.read_csv(os.path.join(POL, "per_regime_offsets_v2.csv"))
ROI = {(r.category, r.anchor_regime): float(r.expected_net_roi_pct) for r in reg.itertuples()}

rows = []
for cat in CATS:
    surf = pd.read_csv(os.path.join(EC, "premarket_lifecycle_surface_midanchor_%s.csv" % cat))
    for c in range(5, 95):
        cs = surf[surf.c == c]
        rg = regime_of(c)
        if cs.empty:
            # no surface data for this cell -> conservative default: place early, shallow 2c
            rows.append({"category": cat, "c": c, "regime": rg, "placement_minute": 240,
                         "bid_offset_cents": 2, "expected_fill_rate": 0.0,
                         "expected_net_roi_pct": round(ROI.get((cat, rg), 0.0), 4),
                         "fill_src": "default_nodata"})
            continue
        # occ_N-weighted fill_reach per tbin (collapse dbuckets)
        def occ_wt_fill(g):
            w = g.occ_N.to_numpy(float); s = g.fill_reach.to_numpy(float)
            m = np.isfinite(s) & (w > 0)
            return (s[m] * w[m]).sum() / w[m].sum() if w[m].sum() > 0 else np.nan
        per_tb = cs.groupby("tbin").apply(occ_wt_fill)
        # placement = earliest (largest) tbin clearing FILL_PLACE; else the tbin with max fill
        early = per_tb[per_tb >= FILL_PLACE]
        place_tb = int(early.index.max()) if len(early) else int(per_tb.idxmax())
        placement = clamp_placement(place_tb)
        # offset = deepest shallow d in {1..CAP} with early fill_reach(dbucket=-d) >= FILL_OFFSET
        # early window = tbins >= 120 (the T-240..T-120 high-catch band), occ-wt over them
        early_rows = cs[cs.tbin >= 120]
        if early_rows.empty:
            early_rows = cs
        offset = 1
        for d in range(1, OFFSET_CAP + 1):
            dd = early_rows[early_rows.dbucket == -d]
            if dd.empty:
                continue
            w = dd.occ_N.to_numpy(float); s = dd.fill_reach.to_numpy(float)
            mm = np.isfinite(s) & (w > 0)
            fr = (s[mm] * w[mm]).sum() / w[mm].sum() if w[mm].sum() > 0 else 0.0
            if fr >= FILL_OFFSET:
                offset = d
        # expected fill at chosen (placement, -offset)
        sel = cs[(cs.tbin == place_tb) & (cs.dbucket == -offset)]
        ef = float(sel.fill_reach.mean()) if len(sel) else float(per_tb.get(place_tb, np.nan))
        rows.append({"category": cat, "c": c, "regime": rg, "placement_minute": placement,
                     "bid_offset_cents": offset,
                     "expected_fill_rate": round(ef if np.isfinite(ef) else 0.0, 4),
                     "expected_net_roi_pct": round(ROI.get((cat, rg), 0.0), 4),
                     "fill_src": "drift_surface"})

out = os.path.join(POL, "entry_table_drift_candidate.csv")
fields = ["category", "c", "regime", "placement_minute", "bid_offset_cents",
          "expected_fill_rate", "expected_net_roi_pct", "fill_src"]
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print("wrote", out, "(%d rows)" % len(rows))
import collections
po = collections.Counter((r["placement_minute"]) for r in rows)
of = collections.Counter((r["bid_offset_cents"]) for r in rows)
print("placement_minute dist:", dict(sorted(po.items())))
print("offset dist:", dict(sorted(of.items())))
# contrast vs current per-cell table
cur = pd.read_csv(os.path.join(POL, "entry_table_percell.csv"))
print("CURRENT placement dist:", dict(sorted(collections.Counter(cur.placement_minute).items())))
print("CURRENT offset dist:   ", dict(sorted(collections.Counter(cur.bid_offset_cents).items())))
