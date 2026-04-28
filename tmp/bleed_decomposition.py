#!/usr/bin/env python3
"""Decompose the -$228.80 bleed by cell: which cells caused it?"""
import json, csv, os, glob, subprocess
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"
ET = timezone(timedelta(hours=-4))
QTY = 10

apr26 = datetime(2026,4,26,13,31,tzinfo=ET).timestamp()

# Load fills + outcomes
fills = []
exits_map = {}
settle_map = {}
for lf in sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl"))):
    with open(lf) as f:
        for line in f:
            try: d = json.loads(line.strip())
            except: continue
            ev = d.get("event","")
            det = d.get("details",{})
            tk = d.get("ticker","")
            if ev == "entry_filled":
                ep = d.get("ts_epoch",0)
                if ep == 0:
                    try:
                        ts = d.get("ts","").replace(" ET","").strip()
                        dt = datetime.strptime(ts, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET)
                        ep = dt.timestamp()
                    except: pass
                fills.append({"ticker":tk,"epoch":ep,"cell":det.get("cell",""),
                    "fp":det.get("fill_price",0)})
            elif ev in ("exit_filled","scalp_filled") and tk not in exits_map:
                exits_map[tk] = det.get("pnl_cents",det.get("profit_cents",0))
            elif ev == "settled" and tk not in settle_map:
                settle_map[tk] = det.get("pnl_cents",0)

def pnl(tk):
    if tk in exits_map: return exits_map[tk] * QTY / 100
    if tk in settle_map: return settle_map[tk] * QTY / 100
    return 0

# Cells disabled in the retune (present in bleed config, absent in recovery config)
bleed_raw = subprocess.check_output(
    ["git","show","f79697f4:arb-executor/config/deploy_v4.json"],
    cwd="/root/Omi-Workspace",stderr=subprocess.DEVNULL).decode()
bleed_cfg = json.loads(bleed_raw)
bleed_active = set(bleed_cfg.get("active_cells",{}).keys())

recov_raw = subprocess.check_output(
    ["git","show","af2507c6:arb-executor/config/deploy_v4.json"],
    cwd="/root/Omi-Workspace",stderr=subprocess.DEVNULL).decode()
recov_cfg = json.loads(recov_raw)
recov_active = set(recov_cfg.get("active_cells",{}).keys())

disabled_cells = bleed_active - recov_active
kept_cells = bleed_active & recov_active

# Bleed period fills
bleed_fills = [f for f in fills if f["epoch"] > 0 and f["epoch"] < apr26]
after_fills = [f for f in fills if f["epoch"] >= apr26]

# Per-cell bleed decomposition
cell_bleed = defaultdict(lambda: {"n":0,"cost":0,"pnl":0,"fps":[]})
for f in bleed_fills:
    c = f["cell"]
    p = pnl(f["ticker"])
    cost = f["fp"] * QTY / 100
    cell_bleed[c]["n"] += 1
    cell_bleed[c]["cost"] += cost
    cell_bleed[c]["pnl"] += p
    cell_bleed[c]["fps"].append(f["fp"])

total_bleed = sum(d["pnl"] for d in cell_bleed.values())

# Part 1: Disabled cells contribution to bleed
with open(os.path.join(OUT_DIR, "bleed_decomposition.csv"), "w", newline="") as fout:
    w = csv.writer(fout)
    w.writerow(["section","cell","status_change","N_bleed","cost_basis","realized_pnl",
                "roi_pct","pct_of_total_bleed","pre_exit","post_exit"])

    # All cells sorted by contribution to bleed
    for c in sorted(cell_bleed.keys(), key=lambda x: cell_bleed[x]["pnl"]):
        d = cell_bleed[c]
        if d["n"] == 0: continue
        roi = d["pnl"] / d["cost"] * 100 if d["cost"] else 0
        pct = d["pnl"] / total_bleed * 100 if total_bleed else 0

        if c in disabled_cells:
            status = "DISABLED"
        elif c in kept_cells:
            status = "KEPT"
        else:
            status = "ADDED_LATER"

        pre_ec = bleed_cfg.get("active_cells",{}).get(c,{}).get("exit_cents","OFF")
        post_ec = recov_cfg.get("active_cells",{}).get(c,{}).get("exit_cents","OFF")

        w.writerow(["ALL_CELLS", c, status, d["n"], "%.2f"%d["cost"], "%.2f"%d["pnl"],
                     "%.1f"%roi, "%.1f"%pct, pre_ec, post_ec])

    # Summary rows
    disabled_pnl = sum(cell_bleed[c]["pnl"] for c in disabled_cells if c in cell_bleed)
    disabled_n = sum(cell_bleed[c]["n"] for c in disabled_cells if c in cell_bleed)
    kept_pnl = sum(cell_bleed[c]["pnl"] for c in kept_cells if c in cell_bleed)
    kept_n = sum(cell_bleed[c]["n"] for c in kept_cells if c in cell_bleed)

    w.writerow([])
    w.writerow(["SUMMARY","DISABLED_CELLS","",disabled_n,"","%.2f"%disabled_pnl,
                "","%.1f"%(disabled_pnl/total_bleed*100 if total_bleed else 0),"",""])
    w.writerow(["SUMMARY","KEPT_CELLS","",kept_n,"","%.2f"%kept_pnl,
                "","%.1f"%(kept_pnl/total_bleed*100 if total_bleed else 0),"",""])
    w.writerow(["SUMMARY","TOTAL","",disabled_n+kept_n,"","%.2f"%total_bleed,"","100.0","",""])

# Part 2: Retuned cells before/after
    w.writerow([])
    w.writerow(["RETUNED_CELLS","cell","","N_before","","pnl_before","roi_before",
                "N_after","pnl_after","roi_after"])

    # For cells that stayed active but had exit changed
    retuned = {}
    for c in kept_cells:
        pre_ec = bleed_cfg["active_cells"].get(c,{}).get("exit_cents",0)
        post_ec = recov_cfg["active_cells"].get(c,{}).get("exit_cents",0)
        if pre_ec != post_ec:
            retuned[c] = {"pre":pre_ec,"post":post_ec}

    cell_after = defaultdict(lambda: {"n":0,"cost":0,"pnl":0})
    for f in after_fills:
        c = f["cell"]
        p = pnl(f["ticker"])
        cost = f["fp"] * QTY / 100
        cell_after[c]["n"] += 1
        cell_after[c]["cost"] += cost
        cell_after[c]["pnl"] += p

    for c in sorted(retuned.keys()):
        b = cell_bleed.get(c, {"n":0,"cost":0,"pnl":0})
        a = cell_after.get(c, {"n":0,"cost":0,"pnl":0})
        b_roi = b["pnl"]/b["cost"]*100 if b["cost"] else 0
        a_roi = a["pnl"]/a["cost"]*100 if a["cost"] else 0
        w.writerow(["RETUNED", c, "%d->%d"%(retuned[c]["pre"],retuned[c]["post"]),
                     b["n"], "%.2f"%b["cost"], "%.2f"%b["pnl"], "%.1f"%b_roi,
                     a["n"], "%.2f"%a["pnl"], "%.1f"%a_roi])

# Print summary
print("=== BLEED DECOMPOSITION ===\n")
print("Total bleed: $%.2f from %d fills\n" % (total_bleed, sum(d["n"] for d in cell_bleed.values())))
print("| Cell | Status | N | PnL | ROI% | %% of bleed |")
print("|---|---|---|---|---|---|")
for c in sorted(cell_bleed.keys(), key=lambda x: cell_bleed[x]["pnl"]):
    d = cell_bleed[c]
    if d["n"] == 0: continue
    status = "DISABLED" if c in disabled_cells else "KEPT"
    roi = d["pnl"]/d["cost"]*100 if d["cost"] else 0
    pct = d["pnl"]/total_bleed*100 if total_bleed else 0
    print("| %s | %s | %d | $%+.2f | %+.0f%% | %.0f%% |" % (c, status, d["n"], d["pnl"], roi, pct))

print("\nDisabled cells total: $%.2f (%.0f%% of bleed)" % (disabled_pnl, disabled_pnl/total_bleed*100 if total_bleed else 0))
print("Kept cells total: $%.2f (%.0f%% of bleed)" % (kept_pnl, kept_pnl/total_bleed*100 if total_bleed else 0))

print("\n=== RETUNED CELLS (before/after) ===\n")
print("| Cell | Exit change | Before N | Before PnL | After N | After PnL |")
print("|---|---|---|---|---|---|")
for c in sorted(retuned.keys()):
    b = cell_bleed.get(c, {"n":0,"pnl":0})
    a = cell_after.get(c, {"n":0,"pnl":0})
    print("| %s | %d->%d | %d | $%+.2f | %d | $%+.2f |" % (
        c, retuned[c]["pre"], retuned[c]["post"], b["n"], b["pnl"], a["n"], a["pnl"]))

print("\nWritten: bleed_decomposition.csv")
