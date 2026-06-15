#!/usr/bin/env python3
"""[C-EXIT-SEAL] exit-surface smoothness gate -- reproducible, in-repo (Plex).

Expands any candidate exit surface (the 4 {cat}_adaptive_exit_bands.parquet
files in live_v4._load_exit_table schema) to per-1c-cell bands and emits, per
category: maxDelta / medDelta (adjacent exit cells), jumps > 5c, HOLD count,
and every structural step (adjacent delta > 1c) BY NAME (cell pair + values).

PASS BAR (= the gated_optima surface's own actuals): max adjacent delta <= 1
outside named structural steps, ZERO jumps > 5c, ZERO HOLD cells. Any
candidate replacement surface must clear this gate before a config flip.

Usage: python3 analysis/exit_surface_smoothness.py <surface_dir> [<surface_dir2> ...]
       (dirs relative to arb-executor/ or absolute)
"""
import sys, statistics
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CATS = ("atp_main", "wta_main", "atp_chall", "wta_chall")
JUMP_BAR = 5

# THE NAMED STRUCTURAL STEPS (the locked gated_optima surface's own actuals,
# 2026-06-12 seal): every adjacent delta > 1c lives in ATP_MAIN; the deep-
# favorite regime turnover at 55->56 is the single >5c step. A candidate
# surface may carry steps ONLY at these named cells; any new step >1c or any
# step >5c outside this list fails the gate.
NAMED_STEPS = set()  # C-ATPMAIN-RESEAL 2026-06-15: all 14 atp_main named
# steps removed -- the full-universe ATP_MAIN surface is smooth (maxD=1,
# steps>1c=0); no structural-step exception is needed for any category.

def expand(fp):
    """parquet -> {cell: X|'HOLD'} over the table's own domain."""
    import pyarrow.parquet as pq
    t = pq.read_table(fp).to_pandas()
    cells = {}
    for _, r in t.iterrows():
        lo, hi = int(r["price_low"]), int(r["price_high"])
        raw = str(r["band_exit_X"]).strip()
        val = "HOLD" if raw.upper() == "HOLD" else int(round(float(raw)))
        for c in range(lo, hi + 1):
            cells[c] = val
    return cells

def assess(cells):
    ks = sorted(cells)
    holds = [c for c in ks if cells[c] == "HOLD"]
    deltas = []        # (cell_a, cell_b, delta) over adjacent EXIT cells
    prev = None
    for c in ks:
        if cells[c] == "HOLD":
            prev = None
            continue
        if prev is not None and c == prev[0] + 1:
            deltas.append((prev[0], c, abs(cells[c] - prev[1])))
        prev = (c, cells[c])
    dvals = [d for _, _, d in deltas] or [0]
    steps = [(a, b, d, cells[a], cells[b]) for a, b, d in deltas if d > 1]
    jumps = [s for s in steps if s[2] > JUMP_BAR]
    return {
        "cells": len(ks), "holds": len(holds), "hold_cells": holds,
        "max_delta": max(dvals), "med_delta": statistics.median(dvals),
        "steps_gt1": steps, "jumps_gt5": jumps,
    }

def run(surface_dir):
    d = Path(surface_dir)
    if not d.is_absolute():
        d = BASE / d
    print("\n=== SURFACE: %s ===" % d)
    all_pass = True
    for cat in CATS:
        fp = d / ("%s_adaptive_exit_bands.parquet" % cat)
        if not fp.exists():
            print("  %-10s MISSING FILE" % cat.upper())
            all_pass = False
            continue
        a = assess(expand(fp))
        unnamed = [s for s in a["steps_gt1"]
                   if (cat, s[0], s[1]) not in NAMED_STEPS]
        ok = a["holds"] == 0 and not unnamed
        all_pass &= ok
        print("  %-10s %s  cells=%d  maxD=%d medD=%g  steps>1c=%d  jumps>%dc=%d  HOLDs=%d" % (
            cat.upper(), "PASS" if ok else "FAIL", a["cells"], a["max_delta"],
            a["med_delta"], len(a["steps_gt1"]), JUMP_BAR, len(a["jumps_gt5"]),
            a["holds"]))
        for s in a["steps_gt1"]:
            named = (cat, s[0], s[1]) in NAMED_STEPS
            print("      structural step: cell %d(X=%s) -> %d(X=%s)  delta %d%s" % (
                s[0], s[3], s[1], s[4], s[2],
                "  [NAMED]" if named else "  << UNNAMED FAIL"))
        if a["holds"]:
            print("      HOLD cells: %s" % a["hold_cells"][:20])
    print("  SURFACE VERDICT: %s" % ("PASS" if all_pass else "FAIL"))
    return all_pass

if __name__ == "__main__":
    dirs = sys.argv[1:] or ["data/durable/exit_surface_gated_optima/",
                            "data/durable/spike_volatility_map/"]
    for sd in dirs:
        run(sd)
