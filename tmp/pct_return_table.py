#!/usr/bin/env python3
"""Per-cell statistics in percentage return terms. Two sections: current exit, optimal exit."""
import sqlite3, json, csv, os, math
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"

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

OPTIMAL_EXITS = {
    "ATP_CHALL_leader_50-54": 7, "ATP_CHALL_leader_55-59": 17,
    "ATP_CHALL_leader_60-64": 26, "ATP_CHALL_leader_65-69": 17,
    "ATP_CHALL_leader_70-74": 19, "ATP_CHALL_leader_75-79": 7,
    "ATP_CHALL_leader_80-84": 12, "ATP_CHALL_leader_85-89": 6,
    "ATP_CHALL_underdog_10-14": 35, "ATP_CHALL_underdog_15-19": 42,
    "ATP_CHALL_underdog_20-24": 65, "ATP_CHALL_underdog_25-29": 18,
    "ATP_CHALL_underdog_30-34": 7, "ATP_CHALL_underdog_35-39": 33,
    "ATP_CHALL_underdog_40-44": 27, "ATP_CHALL_underdog_45-49": 48,
    "ATP_MAIN_leader_50-54": 40, "ATP_MAIN_leader_55-59": 37,
    "ATP_MAIN_leader_60-64": 26, "ATP_MAIN_leader_70-74": 16,
    "ATP_MAIN_leader_75-79": 14, "ATP_MAIN_underdog_20-24": 25,
    "ATP_MAIN_underdog_25-29": 20, "ATP_MAIN_underdog_30-34": 8,
    "ATP_MAIN_underdog_35-39": 46, "ATP_MAIN_underdog_40-44": 4,
    "ATP_MAIN_underdog_45-49": 10,
    "WTA_CHALL_leader_55-59": 20, "WTA_CHALL_underdog_40-44": 53,
    "WTA_MAIN_leader_50-54": 16, "WTA_MAIN_leader_55-59": 6,
    "WTA_MAIN_leader_60-64": 18, "WTA_MAIN_leader_65-69": 27,
    "WTA_MAIN_leader_70-74": 23, "WTA_MAIN_leader_80-84": 13,
    "WTA_MAIN_leader_85-89": 9,
    "WTA_MAIN_underdog_15-19": 31, "WTA_MAIN_underdog_20-24": 22,
    "WTA_MAIN_underdog_25-29": 17, "WTA_MAIN_underdog_30-34": 8,
    "WTA_MAIN_underdog_35-39": 19, "WTA_MAIN_underdog_40-44": 4,
    "WTA_MAIN_underdog_45-49": 15,
}

SCALP_CAP = 95

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

cat_to_tier = {"ATP_MAIN":"ATP_MAIN","ATP_CHALL":"ATP_CHALL",
               "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}

conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()
cur.execute("""SELECT event_ticker, category, winner, loser,
    first_price_winner, min_price_winner, max_price_winner, last_price_winner,
    first_price_loser, total_trades, first_ts, last_ts,
    min_price_loser, max_price_loser
    FROM historical_events
    WHERE first_ts > '2026-03-20' AND first_ts < '2026-04-18'
    AND total_trades >= 10""")
events = cur.fetchall()
conn.close()

DAYS = 28
QTY = 10

all_entries = defaultdict(list)
for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, min_w, max_w, last_w = ev[4], ev[5], ev[6], ev[7]
    fp_l, min_l, max_l = ev[8], ev[12], ev[13]
    is_scalar = max_w is not None and max_w < 95
    if fp_w and 0 < fp_w < 100:
        c = classify_cell(tier, fp_w)
        if c in ALL_CELLS:
            all_entries[c].append({"side":"winner","entry":fp_w,"max_price":max_w,
                "is_scalar":is_scalar,"settle_price":last_w if last_w else 99})
    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        if c in ALL_CELLS:
            all_entries[c].append({"side":"loser","entry":fp_l,"max_price":max_l,
                "is_scalar":is_scalar,"settle_price":min_l if min_l else 1})

def compute_pct(entries, ec):
    n = len(entries)
    if n < 30: return None
    avg_e = sum(e["entry"] for e in entries) / n
    cost = avg_e * QTY / 100
    if cost == 0: return None
    outcomes_dollar = []
    for e in entries:
        target = min(99, e["entry"] + ec)
        if e["max_price"] is not None and e["max_price"] >= target:
            outcomes_dollar.append(ec * QTY / 100)
        elif e["side"] == "winner" and not e["is_scalar"]:
            outcomes_dollar.append((99 - e["entry"]) * QTY / 100)
        elif e["side"] == "loser" and not e["is_scalar"]:
            outcomes_dollar.append(-(e["entry"] - 1) * QTY / 100)
        else:
            outcomes_dollar.append((e["settle_price"] - e["entry"]) * QTY / 100)
    # Convert to % return on cost basis
    returns_pct = [(o / cost) * 100 for o in outcomes_dollar]
    mean_pct = sum(returns_pct) / n
    var_pct = sum((r - mean_pct) ** 2 for r in returns_pct) / n
    std_pct = var_pct ** 0.5
    se_pct = std_pct / (n ** 0.5)
    ci_lo = mean_pct - 1.96 * se_pct
    ci_hi = mean_pct + 1.96 * se_pct
    daily_entries = n / DAYS / 2
    daily_pct = mean_pct * daily_entries / 100
    return {"avg_e": avg_e, "cost": cost, "n": n, "mean_pct": mean_pct,
            "std_pct": std_pct, "se_pct": se_pct, "ci_lo": ci_lo, "ci_hi": ci_hi,
            "daily_entries": daily_entries, "daily_pct": daily_pct, "ec": ec}

header = ["cell","avg_entry_price","cost_basis_per_fill","N",
          "mean_return_pct","stddev_return_pct","SE_return_pct",
          "ci_lower_pct","ci_upper_pct","daily_entries","daily_pct_return"]

with open(os.path.join(OUT_DIR, "pct_returns_current_exit.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    for cell in sorted(ALL_CELLS.keys()):
        entries = all_entries.get(cell, [])
        ec = ALL_CELLS[cell]
        r = compute_pct(entries, ec)
        if not r: continue
        w.writerow([cell, "%.1f" % r["avg_e"], "%.2f" % r["cost"], r["n"],
                     "%.2f" % r["mean_pct"], "%.2f" % r["std_pct"], "%.2f" % r["se_pct"],
                     "%.2f" % r["ci_lo"], "%.2f" % r["ci_hi"],
                     "%.2f" % r["daily_entries"], "%.4f" % r["daily_pct"]])

with open(os.path.join(OUT_DIR, "pct_returns_optimal_exit.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    for cell in sorted(ALL_CELLS.keys()):
        entries = all_entries.get(cell, [])
        ec = OPTIMAL_EXITS.get(cell, ALL_CELLS[cell])
        avg_e = sum(e["entry"] for e in entries) / len(entries) if entries else 50
        max_s = int(SCALP_CAP - avg_e)
        if ec > max_s: ec = max_s
        if ec < 3: ec = 3
        r = compute_pct(entries, ec)
        if not r: continue
        w.writerow([cell, "%.1f" % r["avg_e"], "%.2f" % r["cost"], r["n"],
                     "%.2f" % r["mean_pct"], "%.2f" % r["std_pct"], "%.2f" % r["se_pct"],
                     "%.2f" % r["ci_lo"], "%.2f" % r["ci_hi"],
                     "%.2f" % r["daily_entries"], "%.4f" % r["daily_pct"]])

print("Written:")
for fn in ["pct_returns_current_exit.csv", "pct_returns_optimal_exit.csv"]:
    sz = os.path.getsize(os.path.join(OUT_DIR, fn))
    print("  %s (%.1f KB)" % (fn, sz / 1024))
