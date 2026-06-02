#!/usr/bin/env python3
"""T58 — per-cell premarket maker-entry table (the deployable entry table).

Expands the T47 net-optimal SHALLOW per-regime offsets (per_regime_offsets_v2.csv,
the offsets the committed per-match walk validated as ~+3pp mirror-respecting) to
all 90 cost-basis cells [5,94] per category, attaching each cell's own sand-pooled
match-weighted fill-reach from the committed dip surface (premarket_dip_surface_*.csv,
column reach_dip_pooled_match at depth D == the cell's offset).

The OFFSET is the cell's regime net-optimal SHALLOW value (1-3c for most regimes;
the handful of 7-18c cells are the deep-underdog throughput cells per atlas doctrine)
— NOT a per-cell f x D argmax. The argmax was the +8pp error the per-match walk
corrected (entry_lift_permatch.py): deeper bids add no exit upside under the fixed
atlas exit, only raise the miss rate, and the cell-average double-counts the mirror.
Per-cell granularity here only lets the live bot key entry on the EXACT cell of its
running-mid anchor rather than the coarse 10c regime band; the offset stays shallow
and mirror-respecting.

Source (both committed): docs/policy/per_regime_offsets_v2.csv (T47) +
analysis/exit_charts/premarket_dip_surface_{cat}.csv. Output:
docs/policy/entry_table_percell.csv (360 rows = 4 cat x 90 cells).
Run: cd arb-executor && python3 analysis/exit_charts/build_entry_table_percell.py
"""
import os, csv
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POL = os.path.join(ROOT, "docs", "policy")
EC = os.path.join(ROOT, "analysis", "exit_charts")
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]


def regime_of(c):
    for hi, nm in [(15, "r05_14"), (25, "r15_24"), (35, "r25_34"), (45, "r35_44"),
                   (55, "r45_54"), (65, "r55_64"), (75, "r65_74"), (85, "r75_84"),
                   (100, "r85_94")]:
        if c < hi:
            return nm


reg = pd.read_csv(os.path.join(POL, "per_regime_offsets_v2.csv"))
R = {(r.category, r.anchor_regime): r for r in reg.itertuples()}

rows = []
for cat in CATS:
    dip = pd.read_csv(os.path.join(EC, "premarket_dip_surface_%s.csv" % cat))
    reach = {(int(r.c), int(r.D)): float(r.reach_dip_pooled_match) for r in dip.itertuples()}
    for c in range(5, 95):
        rg = regime_of(c)
        rr = R[(cat, rg)]
        offset = int(rr.bid_offset_cents)
        placement = int(rr.placement_minute)
        roi = float(rr.expected_net_roi_pct)
        # per-cell fill-reach = dip-surface reach at this cell's offset depth;
        # fall back to the regime's expected fill where the cell/depth is absent.
        fill = reach.get((c, offset))
        fill_src = "percell_dip" if fill is not None else "regime"
        if fill is None:
            fill = float(rr.expected_fill_rate)
        rows.append({"category": cat, "c": c, "regime": rg,
                     "placement_minute": placement, "bid_offset_cents": offset,
                     "expected_fill_rate": round(fill, 4),
                     "expected_net_roi_pct": round(roi, 4), "fill_src": fill_src})

out = os.path.join(POL, "entry_table_percell.csv")
fields = ["category", "c", "regime", "placement_minute", "bid_offset_cents",
          "expected_fill_rate", "expected_net_roi_pct", "fill_src"]
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print("wrote", out, "(%d rows)" % len(rows))
import collections
off = collections.Counter(r["bid_offset_cents"] for r in rows)
print("offset distribution (cents -> n_cells):", dict(sorted(off.items())))
shallow = sum(v for k, v in off.items() if k <= 3)
print("shallow (<=3c): %d / %d cells (%.0f%%)" % (shallow, len(rows), 100.0 * shallow / len(rows)))
percell_fill = sum(1 for r in rows if r["fill_src"] == "percell_dip")
print("per-cell fill-reach attached: %d / %d cells" % (percell_fill, len(rows)))
