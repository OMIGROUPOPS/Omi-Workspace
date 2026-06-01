#!/usr/bin/env python3
"""DRAFT (do not deploy without review): rebuild the 4 exit-band parquets from
the VALIDATED deploy_gated_optima per-cell surface (locked exit-charts output).

Output schema matches live_v4.py::_load_exit_table, which reads only
price_low / price_high / band_exit_X. We emit ONE ROW PER 1c CELL
(price_low == price_high == c), band_exit_X = int(round(X)). The gated-optima
surface is all-exit (no HOLD), so every cell is an exit cell.

Writes to --out_dir; never touches the deployed dir or deploy_v5_live.json.
"""
import argparse
import pandas as pd
from pathlib import Path

# category -> validated CSV filename (unsuffixed file is the ATP_MAIN surface)
CAT_FILES = {
    "WTA_CHALL": "deploy_gated_optima_WTA_CHALL.csv",
    "ATP_CHALL": "deploy_gated_optima_ATP_CHALL.csv",
    "WTA_MAIN":  "deploy_gated_optima_WTA_MAIN.csv",
    "ATP_MAIN":  "deploy_gated_optima.csv",
}

def build(in_dir, out_dir):
    in_dir, out_dir = Path(in_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for cat, fn in CAT_FILES.items():
        v = pd.read_csv(in_dir / fn)
        rows = [{"price_low": int(round(float(r["c"]))),
                 "price_high": int(round(float(r["c"]))),
                 "n_constituent_cells": 1,
                 "band_exit_X": str(int(round(float(r["X"]))))}
                for _, r in v.iterrows()]
        df = pd.DataFrame(rows).sort_values("price_low").reset_index(drop=True)
        fp = out_dir / ("%s_adaptive_exit_bands.parquet" % cat.lower())
        df.to_parquet(fp, index=False)
        xs = df["band_exit_X"].astype(int)
        print("wrote %-40s cells=%d  X=%d..%d  mean=%.1f"
              % (fp.name, len(df), xs.min(), xs.max(), xs.mean()))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", default="analysis/exit_charts")
    ap.add_argument("--out_dir", required=True)
    a = ap.parse_args()
    build(a.in_dir, a.out_dir)
