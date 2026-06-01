#!/usr/bin/env python3
"""DRAFT test: load the staging exit table with the REAL live_v4 loader and
assert exit_rule_for(cat, price) returns the validated X for sample cells in
all 4 categories. Uses the actual bot methods (no reimplementation) bound to a
minimal stub so we test the real code path, not a copy."""
import types
import pandas as pd
from pathlib import Path
import live_v4 as L

STAGING = "data/durable/exit_surface_gated_optima"
TRUTH = {  # category -> validated CSV (already on VPS /tmp for this draft run)
    "WTA_CHALL": "/tmp/deploy_gated_optima_WTA_CHALL.csv",
    "ATP_CHALL": "/tmp/deploy_gated_optima_ATP_CHALL.csv",
    "WTA_MAIN":  "/tmp/deploy_gated_optima_WTA_MAIN.csv",
    "ATP_MAIN":  "/tmp/deploy_gated_optima.csv",
}
SAMPLES = [5, 25, 37, 44, 52, 60, 75, 94]

# minimal stub carrying the methods exit_rule_for / _load_exit_table need
s = types.SimpleNamespace(config={"exit_table_dir": STAGING}, exit_table={})
s._log = lambda *a, **k: None
s.cell_lookup = types.MethodType(L.LiveV3.cell_lookup, s)
L.LiveV3._load_exit_table(s)   # REAL loader populates s.exit_table

fails = 0
for cat, csv in TRUTH.items():
    truth = pd.read_csv(csv)
    tmap = {int(round(r.c)): int(round(r.X)) for r in truth.itertuples()}
    for c in SAMPLES:
        band_x, rule = L.LiveV3.exit_rule_for(s, cat, c)   # REAL exit_rule_for
        exp = tmap[c]
        ok = (band_x == exp and rule == "exit")
        fails += (not ok)
        print("  %-9s cell %2d -> exit_rule_for X=%-3s rule=%-4s | validated X=%-3d  %s"
              % (cat, c, band_x, rule, exp, "OK" if ok else "*** MISMATCH ***"))
print("\nRESULT: %d/%d assertions passed%s"
      % (len(TRUTH)*len(SAMPLES) - fails, len(TRUTH)*len(SAMPLES),
         "  ALL PASS" if fails == 0 else "  <-- FAILURES"))
