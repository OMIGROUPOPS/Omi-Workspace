#!/usr/bin/env python3
"""[C-GUIDEBOOK-AIM v1, 07-13] THE GUIDEBOOK — the discovery-to-aim wire.

LINEAGE (C45): composes three ratified fitted surfaces, invents nothing:
  M1  .claude/seqfloor_20260708/recut_cells.json — per cat x price-cell W1
      dip-depth DISTRIBUTION below current (edge_p25/p50/p75 = the depth
      reached in ~75/50/25 percent of historical window-1s), dip timing
      (t_deep_p50, minutes before start), dip-first share. RATIFIED
      (RULING_DYNAMIC_S_CELL_AIM: dynamic S + cell-keyed aim).
  Mfr .claude/fillredo_20260709/aggregate.json — fill-regime grid: per cat x
      price-zone x volume-state x stance (JOIN/S1/S2/T1) fill_pct + ttf.
  M2  docs/policy/aim_table.json — the static organ this replaces at cutover
      (deleted, not disabled, per the migration doctrine).
The THREE-PRICE RANGE SHAPE axis is a NAMED v2 gap: M1's axes are cat x
price-cell; the shape cross requires a corpus recut (registry note).

THE DOCTRINE FLIP (Part 2, named): the placement objective changes from
GET FILLED to GET PAID — the aim is the depth this market class actually
offers (edge_p50: offered in half of historical W1s; edge_p75 = the deep
tier), never the market's current edge; a bid that cannot clear the yield
arithmetic at an achievable depth is a NAMED NO-BID, not a shallower bid.
Fewer, deeper, on purpose. The discount is the asset."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent
RECUT = WS / ".claude/seqfloor_20260708/recut_cells.json"
FILLREDO = WS / ".claude/fillredo_20260709/aggregate.json"
OUT = WS / ".claude/guidebook/GUIDEBOOK_V1.json"

MIN_N = 8          # thin page -> REFUSE loudly, never a guess
YIELD_BAR = 0.08   # the operator's bar: yield on capital wagered

def zone_of(px):
    px = int(px)
    if px < 25:
        return "01-24"
    if px < 50:
        return "25-49"
    if px < 75:
        return "50-74"
    return "75-99"

def build():
    recut = json.loads(RECUT.read_text(encoding="utf-8"))
    fr = json.loads(FILLREDO.read_text(encoding="utf-8"))
    gb = {"meta": {
        "built": "2026-07-13",
        "lineage": ["M1 seqfloor recut_cells (depth distribution + timing; "
                    "RULING_DYNAMIC_S_CELL_AIM)",
                    "fillredo_20260709 aggregate (fill-regime grid)",
                    "supersedes M2 aim_table.json at cutover (deleted, not disabled)"],
        "axes": "category x price_cell (three-price range shape = NAMED v2 gap)",
        "aim_semantics": "aim_depth_cents BELOW current price at discovery; "
                         "achievability = share of historical W1s reaching it",
        "min_n": MIN_N, "yield_bar": YIELD_BAR}, "pages": {}}
    for cat, cells in recut.items():
        for px_cell, v in cells.items():
            n = v.get("n", 0)
            page = {"n": n}
            if n < MIN_N:
                page["verdict"] = "REFUSE_THIN"
            else:
                page.update({
                    "depth_p50_of_w1s": v.get("edge_p50"),   # reached 50% of W1s
                    "depth_p75_of_w1s": v.get("edge_p25"),   # reached ~75%
                    "depth_p25_of_w1s": v.get("edge_p75"),   # the deep tier
                    "dip_t_med_min": v.get("t_deep_p50"),
                    "dip_first_pct": v.get("dip_first_pct"),
                    "verdict": "AIM"})
                zone = zone_of(px_cell)
                grid = (fr.get("per_cat", {}).get(cat, {}) or {}).get("grid", {})
                page["fill_regime"] = {
                    k.split("|", 1)[1]: {"fill_pct": g.get("fill_pct"),
                                         "ttf_med_min": g.get("ttf_med_min")}
                    for k, g in grid.items() if k.startswith(zone + "|")}
            gb["pages"]["%s|%s" % (cat, px_cell)] = page
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(gb, indent=1), encoding="utf-8")
    aims = sum(1 for p in gb["pages"].values() if p.get("verdict") == "AIM")
    thin = sum(1 for p in gb["pages"].values() if p.get("verdict") == "REFUSE_THIN")
    print("GUIDEBOOK_V1: %d pages (%d AIM, %d REFUSE_THIN) -> %s" %
          (len(gb["pages"]), aims, thin, OUT))
    return gb

if __name__ == "__main__":
    build()
