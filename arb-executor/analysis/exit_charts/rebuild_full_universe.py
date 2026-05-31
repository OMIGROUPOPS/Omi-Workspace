"""
rebuild_full_universe.py — re-run all three producers on the FULL per-minute universe.

The probe (39 games) pinned the right SHAPE and the right GATE (match-weighted). This turns
"correct surface" into "deployable numbers" by re-running at full N. Everything is parametrised
on --input; this is just the one-command orchestrator carrying every correction forward:
  - settlement-blind, TRADED-price reach (max forward price_high; bid instruments stay banned)
  - sand-pooled sample (k±3 grain-mass overlap weights)
  - MATCH-weighted gate + expected-return deploy surface, per-cell match-N shown

PREREQUISITE — the full universe must exist and --input must point at it. It is NOT in the git
clone (only the 39-game probe is). Build it first where the g9 source tape lives (the VPS,
/root/Omi-Workspace/...): `python arb-executor/data/scripts/build_per_minute_universe.py` (phase 3),
then point --input at the resulting per_minute_universe parquet dir/glob.

Usage:
    python rebuild_full_universe.py --input /path/to/full/per_minute_universe/'*phase3*.parquet'
    python rebuild_full_universe.py --input /root/Omi-Workspace/arb-executor/data/durable/per_minute_universe
"""
from __future__ import annotations
import argparse
import os

import chart_common as cc
import build_chart_sand_overlap as bso
import build_chart_mirror_outlook as bmo
import build_chart_pooled_gauge as bpg

HERE = os.path.dirname(__file__)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="full per-minute universe (file/dir/glob)")
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--kmax", type=int, default=3)
    ap.add_argument("--reach-floor", type=float, default=0.85)
    ap.add_argument("--suffix", default="_full", help="output filename suffix")
    args = ap.parse_args()

    df = cc.load_universe(args.input, args.category)
    n_tk, n_ev = df.ticker.nunique(), df.event_ticker.nunique()
    print(f"FULL UNIVERSE: {len(df):,} rows · {n_tk} tickers · {n_ev} events · category={args.category}")
    s = args.suffix

    # 1) sand / overlap (pooling foundation)
    sand = bso.build(df, os.path.join(HERE, f"chart_sand_overlap{s}.html"), args.category)
    print("SAND:", sand)

    # 2) mirror / outlook
    mirror = bmo.build(df, os.path.join(HERE, f"chart_mirror_outlook{s}.html"), args.category)
    print("MIRROR:", {k: mirror[k] for k in ("micro_event", "probe_level_sum") if k in mirror})

    # 3) pooled gauge — MATCH-weighted canonical deploy gate
    raw, pooled, opt, pooled_N, Nraw = bpg.build(
        df, os.path.join(HERE, f"chart_pooled_gauge{s}.html"),
        args.category, args.kmax, args.reach_floor, gate_basis="match")
    opt.to_csv(os.path.join(HERE, f"deploy_gated_optima{s}.csv"), index=False)
    pooled.to_csv(os.path.join(HERE, f"pooled_gauge_blocks{s}.csv"), index=False)

    # 4) pyramid (geometry / opportunity space)
    psummary, _, _ = bpg_pyramid(df, args, s)
    print("PYRAMID:", psummary)

    # flag-back: per-cell match-N at full N (which firmed up vs stayed thin) + shape check
    thin = opt[opt.match_N < bpg.THIN_MATCH_N]
    print(f"\nMATCH-N at full universe: range [{int(opt.match_N.min())}, {int(opt.match_N.max())}] · "
          f"thin (<{bpg.THIN_MATCH_N}): {len(thin)}/{len(opt)} cells"
          + (": " + ", ".join(f"c{int(r.c)}({int(r.match_N)})" for r in thin.itertuples()) if len(thin) else ""))
    # shape check: is the match-gated fold monotone (deeper X at lower cost)?
    o = opt.sort_values("c")
    mono_viol = int((o.X.diff() > 2).sum())  # upward jumps in X as c rises (fold should fall)
    print(f"fold monotonicity: {mono_viol} upward X-jumps>2 as c rises (0 = clean fold)")
    print(f"\noutputs written with suffix '{s}'. Compare against probe to confirm shape holds.")


def bpg_pyramid(df, args, s):
    import build_chart_pyramid as bp
    return bp.build(df, os.path.join(HERE, f"chart_pyramid{s}.html"), args.category)


if __name__ == "__main__":
    main()
