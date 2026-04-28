#!/usr/bin/env python3
"""
Framework analysis: ROI in %, CI, exit granularity, cell groupings, variable isolation.
"""
import sqlite3, json, csv, os, glob, subprocess, math
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"
ET = timezone(timedelta(hours=-4))
QTY = 10

# Load config
with open(os.path.join(BASE_DIR, "config/deploy_v4.json")) as f:
    cfg = json.load(f)
active_cells = cfg.get("active_cells", {})
ALL_CELLS = {}
for cell, params in active_cells.items():
    ALL_CELLS[cell] = params.get("exit_cents", 0)
DISABLED_EXITS = {
    "ATP_MAIN_underdog_40-44": 9, "ATP_CHALL_underdog_30-34": 15,
    "ATP_MAIN_leader_75-79": 14, "ATP_CHALL_underdog_25-29": 21,
    "ATP_MAIN_underdog_35-39": 12, "ATP_CHALL_leader_60-64": 6,
    "ATP_MAIN_leader_60-64": 15, "ATP_MAIN_underdog_25-29": 22,
    "ATP_CHALL_underdog_15-19": 31, "WTA_MAIN_leader_55-59": 10,
    "WTA_MAIN_underdog_40-44": 5, "WTA_MAIN_underdog_30-34": 16,
    "WTA_MAIN_underdog_35-39": 11, "ATP_MAIN_leader_55-59": 13,
    "ATP_MAIN_underdog_20-24": 25, "WTA_MAIN_leader_60-64": 8,
    "WTA_MAIN_underdog_15-19": 31, "WTA_MAIN_underdog_20-24": 22,
}
for cell, exit_c in DISABLED_EXITS.items():
    ALL_CELLS[cell] = exit_c

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

def get_tier(tk):
    if "KXATPMATCH" in tk and "CHALL" not in tk: return "ATP_MAIN"
    if "KXWTAMATCH" in tk and "CHALL" not in tk: return "WTA_MAIN"
    if "KXATPCHALL" in tk: return "ATP_CHALL"
    if "KXWTACHALL" in tk: return "WTA_CHALL"
    return None

cat_to_tier = {"ATP_MAIN":"ATP_MAIN","ATP_CHALL":"ATP_CHALL",
               "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}
SCALP_CAP = 95

# Load historical events
conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()
cur.execute("""SELECT event_ticker, category, first_price_winner, min_price_winner,
    max_price_winner, last_price_winner, first_price_loser,
    min_price_loser, max_price_loser
    FROM historical_events
    WHERE first_ts > '2026-03-20' AND first_ts < '2026-04-18'
    AND total_trades >= 10""")
events = cur.fetchall()
conn.close()

hist_entries = defaultdict(list)
for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, min_w, max_w, last_w = ev[2], ev[3], ev[4], ev[5]
    fp_l, min_l, max_l = ev[6], ev[7], ev[8]
    is_scalar = max_w is not None and max_w < 95
    if fp_w and 0 < fp_w < 100:
        c = classify_cell(tier, fp_w)
        hist_entries[c].append({"entry":fp_w,"max_price":max_w,"side":"winner",
            "is_scalar":is_scalar,"settle":last_w or 99})
    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        hist_entries[c].append({"entry":fp_l,"max_price":max_l,"side":"loser",
            "is_scalar":is_scalar,"settle":min_l or 1})

# Load live fills
apr26 = datetime(2026,4,26,13,31,tzinfo=ET).timestamp()
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
                    "fp":det.get("fill_price",0),"tier":get_tier(tk) or ""})
            elif ev in ("exit_filled","scalp_filled") and tk not in exits_map:
                exits_map[tk] = det.get("pnl_cents",det.get("profit_cents",0))
            elif ev == "settled" and tk not in settle_map:
                settle_map[tk] = det.get("pnl_cents",0)

def get_pnl_dollars(tk):
    if tk in exits_map: return exits_map[tk] * QTY / 100
    if tk in settle_map: return settle_map[tk] * QTY / 100
    return 0

def compute_roi_ci(pnl_pcts):
    n = len(pnl_pcts)
    if n < 2: return 0, 0, 0, 0, False
    mean = sum(pnl_pcts) / n
    std = (sum((x-mean)**2 for x in pnl_pcts) / n) ** 0.5
    se = std / (n**0.5)
    ci_lo = mean - 1.96 * se
    ci_hi = mean + 1.96 * se
    sig = ci_lo > 0 or ci_hi < 0  # CI doesn't include 0
    return mean, std, ci_lo, ci_hi, sig

# =====================================================================
# PART A: Post-retune per-cell economics (Apr 26 PM - Apr 28)
# =====================================================================
post_fills = [f for f in fills if f["epoch"] >= apr26]
print("=== PART A: POST-RETUNE ECONOMICS (%d fills) ===" % len(post_fills))

with open(os.path.join(OUT_DIR, "post_retune_economics.csv"), "w", newline="") as fout:
    w = csv.writer(fout)
    w.writerow(["cell","N","avg_fill_price","cost_basis_total","realized_pnl",
                "realized_roi_pct","ci_lower_pct","ci_upper_pct","significant"])

    cell_post = defaultdict(lambda: {"n":0,"pnl":0,"fps":[],"pnl_pcts":[]})
    for f in post_fills:
        cell = classify_cell(f["tier"], f["fp"]) if f["tier"] else f["cell"]
        pnl = get_pnl_dollars(f["ticker"])
        cost = f["fp"] * QTY / 100
        pnl_pct = pnl / cost * 100 if cost else 0
        cell_post[cell]["n"] += 1
        cell_post[cell]["pnl"] += pnl
        cell_post[cell]["fps"].append(f["fp"])
        cell_post[cell]["pnl_pcts"].append(pnl_pct)

    for cell in sorted(cell_post.keys()):
        d = cell_post[cell]
        n = d["n"]
        avg_fp = sum(d["fps"]) / n
        cost_total = sum(fp * QTY / 100 for fp in d["fps"])
        roi = d["pnl"] / cost_total * 100 if cost_total else 0
        mean, std, ci_lo, ci_hi, sig = compute_roi_ci(d["pnl_pcts"])
        w.writerow([cell, n, "%.1f"%avg_fp, "%.2f"%cost_total, "%.2f"%d["pnl"],
                     "%.1f"%roi, "%.1f"%ci_lo, "%.1f"%ci_hi,
                     "YES" if sig else "NO"])

# =====================================================================
# PART B: Exit increment granularity for leader_70-74
# =====================================================================
print("\n=== PART B: EXIT SWEEP leader_70-74 (1c granularity) ===")

entries_7074 = hist_entries.get("ATP_CHALL_leader_70-74", [])
max_exit = int(SCALP_CAP - 72)  # ~23

with open(os.path.join(OUT_DIR, "exit_sweep_leader_70_74.csv"), "w", newline="") as fout:
    w = csv.writer(fout)
    w.writerow(["exit_cents","scalp_rate_pct","mean_roi_pct","ci_lower","ci_upper","N"])

    for ec in range(3, max_exit + 1):
        pnl_pcts = []
        scalps = 0
        for e in entries_7074:
            target = min(99, e["entry"] + ec)
            cost = e["entry"] * QTY / 100
            if e["max_price"] and e["max_price"] >= target:
                pnl = ec * QTY / 100
                scalps += 1
            elif e["side"] == "winner" and not e["is_scalar"]:
                pnl = (99 - e["entry"]) * QTY / 100
            elif e["side"] == "loser" and not e["is_scalar"]:
                pnl = -(e["entry"] - 1) * QTY / 100
            else:
                pnl = (e["settle"] - e["entry"]) * QTY / 100
            pnl_pcts.append(pnl / cost * 100 if cost else 0)

        n = len(pnl_pcts)
        sr = scalps / n * 100 if n else 0
        mean, std, ci_lo, ci_hi, sig = compute_roi_ci(pnl_pcts)
        w.writerow([ec, "%.1f"%sr, "%.1f"%mean, "%.1f"%ci_lo, "%.1f"%ci_hi, n])

# =====================================================================
# PART C: Alternative cell groupings
# =====================================================================
print("\n=== PART C: ALTERNATIVE CELL GROUPINGS ===")

groupings = {
    "ATP_CHALL_leader_60-79": ["ATP_CHALL_leader_60-64","ATP_CHALL_leader_65-69",
                                "ATP_CHALL_leader_70-74","ATP_CHALL_leader_75-79"],
    "ATP_CHALL_leader_50-69": ["ATP_CHALL_leader_50-54","ATP_CHALL_leader_55-59",
                                "ATP_CHALL_leader_60-64","ATP_CHALL_leader_65-69"],
    "ATP_CHALL_leader_70-89": ["ATP_CHALL_leader_70-74","ATP_CHALL_leader_75-79",
                                "ATP_CHALL_leader_80-84","ATP_CHALL_leader_85-89"],
    "ALL_ATP_CHALL_leaders": [c for c in hist_entries if "ATP_CHALL_leader" in c],
    "ALL_ATP_MAIN_leaders": [c for c in hist_entries if "ATP_MAIN_leader" in c],
    "ALL_CHALL_underdogs": [c for c in hist_entries if "CHALL" in c and "underdog" in c],
}

with open(os.path.join(OUT_DIR, "cell_groupings.csv"), "w", newline="") as fout:
    w = csv.writer(fout)
    w.writerow(["grouping","N","optimal_exit_1c","optimal_roi_pct","ci_lower","ci_upper",
                "sum_subcell_roi_pct","grouping_vs_subcell"])

    for gname, subcells in sorted(groupings.items()):
        # Combine entries from all sub-cells
        combined = []
        for sc in subcells:
            combined.extend(hist_entries.get(sc, []))
        if len(combined) < 30:
            w.writerow([gname, len(combined), "", "", "", "", "", "N<30"])
            continue

        # Find optimal exit at 1c granularity
        avg_e = sum(e["entry"] for e in combined) / len(combined)
        max_ec = int(SCALP_CAP - avg_e)
        best_roi = -999
        best_ec = 10
        for ec in range(3, min(max_ec + 1, 50)):
            pnl_pcts = []
            for e in combined:
                target = min(99, e["entry"] + ec)
                cost = e["entry"] * QTY / 100
                if e["max_price"] and e["max_price"] >= target:
                    pnl = ec * QTY / 100
                elif e["side"] == "winner" and not e["is_scalar"]:
                    pnl = (99 - e["entry"]) * QTY / 100
                elif e["side"] == "loser" and not e["is_scalar"]:
                    pnl = -(e["entry"] - 1) * QTY / 100
                else:
                    pnl = (e["settle"] - e["entry"]) * QTY / 100
                pnl_pcts.append(pnl / cost * 100 if cost else 0)
            mean, _, _, _, _ = compute_roi_ci(pnl_pcts)
            if mean > best_roi:
                best_roi = mean
                best_ec = ec

        # Compute stats at best exit
        pnl_pcts = []
        for e in combined:
            target = min(99, e["entry"] + best_ec)
            cost = e["entry"] * QTY / 100
            if e["max_price"] and e["max_price"] >= target:
                pnl = best_ec * QTY / 100
            elif e["side"] == "winner" and not e["is_scalar"]:
                pnl = (99 - e["entry"]) * QTY / 100
            elif e["side"] == "loser" and not e["is_scalar"]:
                pnl = -(e["entry"] - 1) * QTY / 100
            else:
                pnl = (e["settle"] - e["entry"]) * QTY / 100
            pnl_pcts.append(pnl / cost * 100 if cost else 0)

        mean, std, ci_lo, ci_hi, sig = compute_roi_ci(pnl_pcts)

        # Sum of sub-cell optimal ROIs
        subcell_sum = 0
        for sc in subcells:
            sc_entries = hist_entries.get(sc, [])
            if len(sc_entries) < 10: continue
            sc_avg_e = sum(e["entry"] for e in sc_entries) / len(sc_entries)
            sc_max_ec = int(SCALP_CAP - sc_avg_e)
            sc_best = -999
            for ec in range(3, min(sc_max_ec + 1, 50)):
                pp = []
                for e in sc_entries:
                    t = min(99, e["entry"] + ec)
                    c = e["entry"] * QTY / 100
                    if e["max_price"] and e["max_price"] >= t:
                        p = ec * QTY / 100
                    elif e["side"] == "winner" and not e["is_scalar"]:
                        p = (99 - e["entry"]) * QTY / 100
                    elif e["side"] == "loser" and not e["is_scalar"]:
                        p = -(e["entry"] - 1) * QTY / 100
                    else:
                        p = (e["settle"] - e["entry"]) * QTY / 100
                    pp.append(p / c * 100 if c else 0)
                m = sum(pp)/len(pp) if pp else 0
                if m > sc_best: sc_best = m
            if sc_best > -999:
                subcell_sum += sc_best

        verdict = "GROUP_BETTER" if mean > subcell_sum / max(len(subcells),1) else "SUBCELL_BETTER"

        w.writerow([gname, len(combined), best_ec, "%.1f"%mean, "%.1f"%ci_lo, "%.1f"%ci_hi,
                     "%.1f"%(subcell_sum/max(len(subcells),1)), verdict])

# =====================================================================
# PART D: Variable isolation — what changed between bleed and recovery
# =====================================================================
print("\n=== PART D: VARIABLE ISOLATION ===")

# Compare config at two points:
# Bleed: f79697f4 (Apr 24 00:15) — the config that produced -$116/day
# Recovery: af2507c6 (Apr 26 14:35) — the config that produced +$66/day

with open(os.path.join(OUT_DIR, "variable_isolation.csv"), "w", newline="") as fout:
    w = csv.writer(fout)
    w.writerow(["variable","bleed_period_value","recovery_period_value","changed"])

    bleed_hash = "f79697f4"
    recov_hash = "af2507c6"

    try:
        bleed_raw = subprocess.check_output(
            ["git","show","%s:arb-executor/config/deploy_v4.json" % bleed_hash],
            cwd="/root/Omi-Workspace",stderr=subprocess.DEVNULL).decode()
        bleed_cfg = json.loads(bleed_raw)

        recov_raw = subprocess.check_output(
            ["git","show","%s:arb-executor/config/deploy_v4.json" % recov_hash],
            cwd="/root/Omi-Workspace",stderr=subprocess.DEVNULL).decode()
        recov_cfg = json.loads(recov_raw)

        # Count active cells
        b_active = set(bleed_cfg.get("active_cells",{}).keys())
        r_active = set(recov_cfg.get("active_cells",{}).keys())
        w.writerow(["active_cell_count", len(b_active), len(r_active), len(b_active)!=len(r_active)])
        w.writerow(["cells_added", "", ", ".join(sorted(r_active - b_active)), len(r_active-b_active)>0])
        w.writerow(["cells_removed", "", ", ".join(sorted(b_active - r_active)), len(b_active-r_active)>0])

        # Exit cents changes
        changed_exits = []
        for c in sorted(b_active & r_active):
            be = bleed_cfg["active_cells"][c].get("exit_cents",0)
            re = recov_cfg["active_cells"][c].get("exit_cents",0)
            if be != re:
                changed_exits.append("%s: %d->%d" % (c, be, re))
        w.writerow(["exit_cents_changed", len(changed_exits), "; ".join(changed_exits), len(changed_exits)>0])

        # Sizing
        b_sz = bleed_cfg.get("sizing",{})
        r_sz = recov_cfg.get("sizing",{})
        w.writerow(["entry_contracts", b_sz.get("entry_contracts","?"), r_sz.get("entry_contracts","?"),
                     b_sz != r_sz])

        # Other config keys
        for key in set(list(bleed_cfg.keys()) + list(recov_cfg.keys())):
            if key in ("active_cells","disabled_cells","sizing"): continue
            bv = bleed_cfg.get(key, "ABSENT")
            rv = recov_cfg.get(key, "ABSENT")
            if bv != rv:
                w.writerow([key, str(bv)[:80], str(rv)[:80], True])

    except Exception as e:
        w.writerow(["error", str(e), "", ""])

    # Code changes between bleed and recovery
    try:
        code_changes = subprocess.check_output(
            ["git","log","--oneline","%s..%s" % (bleed_hash, recov_hash),
             "--","arb-executor/live_v3.py","arb-executor/intelligence.py"],
            cwd="/root/Omi-Workspace",stderr=subprocess.DEVNULL).decode().strip()
        for line in code_changes.split("\n"):
            if line.strip():
                w.writerow(["code_change", line.strip()[:80], "", True])
    except:
        pass

    # Tournament context (from kalshi_price_snapshots)
    w.writerow(["tournament_context", "not available from config", "would need schedule data", "UNKNOWN"])
    w.writerow(["market_hours", "24/7 automated", "24/7 automated", False])

print("\nWritten CSVs to %s/" % OUT_DIR)
for fn in ["post_retune_economics.csv","exit_sweep_leader_70_74.csv",
           "cell_groupings.csv","variable_isolation.csv"]:
    p = os.path.join(OUT_DIR, fn)
    if os.path.exists(p):
        print("  %s (%.1f KB)" % (fn, os.path.getsize(p)/1024))
