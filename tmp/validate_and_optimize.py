#!/usr/bin/env python3
"""
Validate corrected analysis and explore optimal portfolio configuration.
Tasks 1-9: Sl verification, exit retune, portfolio optimization.
"""
import sqlite3, json, csv, os, math, random
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/corrected_analysis"

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

# =====================================================================
# TASK 1: Verify Sl for ATP_CHALL_leader_70-74
# =====================================================================
print("=" * 80)
print("=== TASK 1: Sl VERIFICATION — ATP_CHALL_leader_70-74 ===")
print("=" * 80)
print()

exit_c_7074 = ALL_CELLS.get("ATP_CHALL_leader_70-74", 25)
print("Cell: ATP_CHALL_leader_70-74, exit_cents=%d" % exit_c_7074)
print()
print("| # | Event | Side | Entry | Target | max_price | Reached? | Gap |")
print("|---|---|---|---|---|---|---|---|")

loser_count = 0
loser_reached = 0
for ev in events:
    evt, cat = ev[0], ev[1]
    if cat != "ATP_CHALL": continue
    fp_l, max_l, min_l = ev[8], ev[13], ev[12]
    if not fp_l or fp_l <= 0: continue
    cell = classify_cell("ATP_CHALL", fp_l)
    if cell != "ATP_CHALL_leader_70-74": continue
    # This is a loser-side entry
    target = min(99, fp_l + exit_c_7074)
    reached = max_l is not None and max_l >= target
    gap = (max_l - target) if max_l else -999
    loser_count += 1
    if reached: loser_reached += 1
    print("| %d | %s | loser | %.0fc | %.0fc | %.0fc | %s | %+.0fc |" % (
        loser_count, evt[-20:], fp_l, target, max_l if max_l else 0,
        "YES" if reached else "NO", gap))

print()
print("Loser entries: %d, Reached exit: %d, Sl = %.0f%%" % (
    loser_count, loser_reached, loser_reached/loser_count*100 if loser_count else 0))
print()

# TASK 2: Methodology check
print("=" * 80)
print("=== TASK 2: SCALP CHECK METHODOLOGY ===")
print("=" * 80)
print()
print("Corrected script checks: max_price >= min(99, entry + exit_cents)")
print()
print("For winner side: max_price_winner = highest yes_price trade on winner ticker")
print("  → always 99c (settlement). Sw = 100% correct.")
print()
print("For loser side: max_price_loser = highest yes_price trade on loser ticker")
print("  → This is the highest price ANYONE traded at on that side.")
print("  → A trade at price X means a buyer paid X cents for YES contracts.")
print("  → Our resting sell at target would fill if a buyer pays >= target.")
print("  → This is the correct check for maker sell fills.")
print()
print("HOWEVER: max_price_loser is from the FULL trade tape including")
print("very early trades (market open) and very late trades (settlement).")
print("The FIRST price on the loser side might be the max if the market")
print("opened at a high price and declined to settlement at 1c.")
print()
print("For our strategy: we enter DURING the match lifecycle.")
print("If max_price_loser occurred BEFORE our entry, the scalp opportunity")
print("was already gone. We need max_price AFTER entry.")
print()
print("This is only a problem if max_price == first_price on the loser side")
print("(meaning the price only went down from entry).")
print()

# Check: for each loser entry, did max_price == first_price?
fp_eq_max_count = 0
fp_gt_max_count = 0  # shouldn't happen
max_after_entry = 0
for ev in events:
    evt, cat = ev[0], ev[1]
    if cat != "ATP_CHALL": continue
    fp_l, max_l = ev[8], ev[13]
    if not fp_l or fp_l <= 0: continue
    cell = classify_cell("ATP_CHALL", fp_l)
    if cell != "ATP_CHALL_leader_70-74": continue
    if max_l == fp_l:
        fp_eq_max_count += 1
    elif max_l and max_l > fp_l:
        max_after_entry += 1

print("For ATP_CHALL_leader_70-74 loser entries:")
print("  max_l == fp_l (no upward bounce): %d" % fp_eq_max_count)
print("  max_l > fp_l (bounced above entry): %d" % max_after_entry)
print()

# =====================================================================
# TASK 3: Per-cell daily fire rates
# =====================================================================
print("=" * 80)
print("=== TASK 3: PER-CELL DAILY FIRE RATES ===")
print("=" * 80)
print()

# Build entries with per-exit-c computation for retune testing
def compute_cell_ev(entries, exit_c_override=None):
    """Compute EV for a list of entries at a given exit target."""
    if not entries:
        return {"ev": 0, "n": 0, "Sw": 0, "Sl": 0, "w": 0}

    n = len(entries)
    winners = [e for e in entries if e["side"] == "winner" and not e["is_scalar"]]
    losers = [e for e in entries if e["side"] == "loser" and not e["is_scalar"]]
    scalars = [e for e in entries if e["is_scalar"]]

    n_w, n_l, n_s = len(winners), len(losers), len(scalars)
    w = n_w / (n_w + n_l) if (n_w + n_l) else 0
    s = n_s / n if n else 0

    ec = exit_c_override if exit_c_override is not None else entries[0]["exit_c"]
    avg_entry = sum(e["entry"] for e in entries) / n

    # Recompute scalp rates at this exit target
    w_scalp = sum(1 for e in winners if e["max_price"] and e["max_price"] >= min(99, e["entry"] + ec))
    l_scalp = sum(1 for e in losers if e["max_price"] and e["max_price"] >= min(99, e["entry"] + ec))

    Sw = w_scalp / n_w if n_w else 0
    Sl = l_scalp / n_l if n_l else 0

    scalp_profit = ec * QTY / 100
    win_settle = (99 - avg_entry) * QTY / 100
    loss_settle = -(avg_entry - 1) * QTY / 100

    scalar_pnl = 0
    if scalars:
        scalar_pnl = sum((e["settle_price"] - e["entry"]) * QTY / 100 for e in scalars) / len(scalars)

    ev = w * (Sw * scalp_profit + (1 - Sw) * win_settle) \
       + (1 - w - s) * (Sl * scalp_profit + (1 - Sl) * loss_settle) \
       + s * scalar_pnl

    cost = avg_entry * QTY / 100
    roi = ev / cost * 100 if cost else 0

    return {"ev": ev, "n": n, "Sw": Sw, "Sl": Sl, "w": w, "roi": roi,
            "avg_entry": avg_entry, "cost": cost, "exit_c": ec,
            "daily_fires": n / DAYS / 2, "daily_dollar": (n / DAYS / 2) * ev}

# Build all entries
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
            all_entries[c].append({
                "side": "winner", "entry": fp_w, "exit_c": ALL_CELLS[c],
                "max_price": max_w, "is_scalar": is_scalar,
                "settle_price": last_w if last_w else 99, "evt": evt,
            })
    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        if c in ALL_CELLS:
            all_entries[c].append({
                "side": "loser", "entry": fp_l, "exit_c": ALL_CELLS[c],
                "max_price": max_l, "is_scalar": is_scalar,
                "settle_price": min_l if min_l else 1, "evt": evt,
            })

print("| Cell | Status | N | Daily fires | EV$/fill | Daily $ | Cost basis | ROI% |")
print("|---|---|---|---|---|---|---|---|")

cell_results = {}
total_daily = 0
for cell in sorted(ALL_CELLS.keys()):
    entries = all_entries.get(cell, [])
    if not entries: continue
    r = compute_cell_ev(entries)
    cell_results[cell] = r
    is_active = cell in active_cells
    if is_active:
        total_daily += r["daily_dollar"]
    flag = "*" if r["n"] < 30 else ""
    print("| %s | %s | %d%s | %.2f | $%+.3f | $%+.3f | $%.2f | %+.1f%% |" % (
        cell, "ON" if is_active else "off", r["n"], flag,
        r["daily_fires"], r["ev"], r["daily_dollar"], r["cost"], r["roi"]))

print()
print("Total daily $ (active cells): $%.2f" % total_daily)


# =====================================================================
# TASK 4: Portfolio with negative cells removed
# =====================================================================
print()
print("=" * 80)
print("=== TASK 4: PORTFOLIO — NEGATIVES REMOVED ===")
print("=" * 80)
print()

# Cells to disable (currently active but negative on corrected math)
neg_active = [c for c, r in cell_results.items()
              if c in active_cells and r["roi"] < 0 and r["n"] >= 15]

print("Cells to disable (active + negative ROI + N>=15):")
for c in sorted(neg_active):
    r = cell_results[c]
    print("  %s: ROI=%+.1f%%, daily=$%+.3f" % (c, r["roi"], r["daily_dollar"]))

def run_mc(cell_set, cell_results_dict, label):
    """Run Monte Carlo for a set of cells."""
    # Build per-event outcomes for each cell
    outcomes = {}
    daily_ev = 0
    for cell in cell_set:
        r = cell_results_dict.get(cell)
        if not r: continue
        entries = all_entries.get(cell, [])
        cell_outcomes = []
        ec = r["exit_c"]
        for e in entries:
            target = min(99, e["entry"] + ec)
            if e["max_price"] and e["max_price"] >= target:
                pnl = ec * QTY / 100
            elif e["side"] == "winner" and not e["is_scalar"]:
                pnl = (99 - e["entry"]) * QTY / 100
            elif e["side"] == "loser" and not e["is_scalar"]:
                pnl = -(e["entry"] - 1) * QTY / 100
            else:
                pnl = (e["settle_price"] - e["entry"]) * QTY / 100
            cell_outcomes.append(pnl)
        if cell_outcomes:
            outcomes[cell] = cell_outcomes
            daily_ev += r["daily_dollar"]

    random.seed(42)
    sim = []
    for _ in range(10000):
        day = 0
        for cell, outs in outcomes.items():
            r = cell_results_dict[cell]
            fires = max(1, int(round(r["daily_fires"])))
            for _ in range(fires):
                day += random.choice(outs)
        sim.append(day)

    sim.sort()
    ns = len(sim)
    avg = sum(sim) / ns
    std = (sum((x - avg)**2 for x in sim) / ns) ** 0.5
    sharpe = avg / std if std else 0

    print("=== %s (%d cells) ===" % (label, len(outcomes)))
    print("  Daily expected $: $%.2f" % daily_ev)
    print("  MC mean:          $%.2f" % avg)
    print("  MC std:           $%.2f" % std)
    print("  MC Sharpe:        %.3f" % sharpe)
    print("  MC P5 worst:      $%.2f" % sim[ns//20])
    print("  MC P25:           $%.2f" % sim[ns//4])
    print("  MC median:        $%.2f" % sim[ns//2])
    print("  MC P75:           $%.2f" % sim[3*ns//4])
    print("  MC P95 best:      $%.2f" % sim[19*ns//20])
    print()
    return {"daily_ev": daily_ev, "mc_mean": avg, "sharpe": sharpe,
            "p5": sim[ns//20], "p95": sim[19*ns//20], "cells": len(outcomes)}

# Current 25 active cells
current_active = set(active_cells.keys())
print("--- SCENARIO A: Current 25 active cells ---")
sc_a = run_mc(current_active, cell_results, "Current 25 active")

# After removing negatives
trimmed = current_active - set(neg_active)
print("--- SCENARIO B: After removing %d negative cells (%d remain) ---" % (
    len(neg_active), len(trimmed)))
sc_b = run_mc(trimmed, cell_results, "Trimmed (negatives removed)")


# =====================================================================
# TASK 5: Aggressive subset
# =====================================================================
print("=" * 80)
print("=== TASK 5: AGGRESSIVE SUBSET ===")
print("=" * 80)
print()

# Only cells with corrected ROI > 3% and N >= 20
aggressive = set()
for cell, r in cell_results.items():
    if r["roi"] > 3 and r["n"] >= 20:
        aggressive.add(cell)
        print("  %s: ROI=%+.1f%%, N=%d, daily=$%+.3f" % (cell, r["roi"], r["n"], r["daily_dollar"]))

print()
print("--- SCENARIO C: Aggressive subset (%d cells with ROI>3%%, N>=20) ---" % len(aggressive))
sc_c = run_mc(aggressive, cell_results, "Aggressive (ROI>3%, N>=20)")


# =====================================================================
# TASK 6: ATP_CHALL_leader_60-64 re-enable impact
# =====================================================================
print("=" * 80)
print("=== TASK 6: RE-ENABLE ATP_CHALL_leader_60-64 IMPACT ===")
print("=" * 80)
print()

r6064 = cell_results.get("ATP_CHALL_leader_60-64")
if r6064:
    print("ATP_CHALL_leader_60-64 at current exit +%dc:" % r6064["exit_c"])
    print("  N=%d, Daily fires=%.2f" % (r6064["n"], r6064["daily_fires"]))
    print("  Sw=%.0f%%, Sl=%.0f%%, w=%.0f%%" % (r6064["Sw"]*100, r6064["Sl"]*100, r6064["w"]*100))
    print("  EV/fill=$%+.3f, ROI=%+.1f%%" % (r6064["ev"], r6064["roi"]))
    print("  Daily $ contribution: $%+.3f" % r6064["daily_dollar"])
    print()

# Trimmed + 60-64
with_6064 = trimmed | {"ATP_CHALL_leader_60-64"}
print("--- SCENARIO D: Trimmed + ATP_CHALL_leader_60-64 ---")
sc_d = run_mc(with_6064, cell_results, "Trimmed + leader_60-64")


# =====================================================================
# TASK 7: Exit retune for negative cells
# =====================================================================
print("=" * 80)
print("=== TASK 7: EXIT RETUNE FOR NEGATIVE/MARGINAL CELLS ===")
print("=" * 80)
print()

retune_cells = [
    "ATP_CHALL_leader_50-54",    # -3.1% at +15
    "ATP_CHALL_leader_85-89",    # -0.5% at +7
    "ATP_CHALL_underdog_35-39",  # -2.0% at +11
    "ATP_CHALL_underdog_45-49",  # -5.1% at +13
    "ATP_MAIN_underdog_30-34",   # -0.6% at +15
    "ATP_MAIN_underdog_45-49",   # -4.6% at +4
    # Also test marginally positive cells for improvement
    "ATP_CHALL_leader_65-69",    # +1.1% at +30
    "ATP_CHALL_leader_75-79",    # +0.5% at +10
    "ATP_CHALL_leader_80-84",    # +1.4% at +15
    "ATP_MAIN_leader_70-74",     # +1.1% at +17
]

print("| Cell | Current exit | Current ROI | Best exit | Best ROI | Best Sl | Best EV$ | Delta |")
print("|---|---|---|---|---|---|---|---|")

best_exits = {}
for cell in retune_cells:
    entries = all_entries.get(cell, [])
    if not entries: continue

    current_ec = ALL_CELLS[cell]
    current_r = compute_cell_ev(entries, current_ec)

    best_roi = current_r["roi"]
    best_ec = current_ec
    best_r = current_r

    # Test exits from 3 to 40 in steps of 1
    for test_ec in range(3, 41):
        r = compute_cell_ev(entries, test_ec)
        if r["roi"] > best_roi:
            best_roi = r["roi"]
            best_ec = test_ec
            best_r = r

    delta = best_roi - current_r["roi"]
    best_exits[cell] = {"exit_c": best_ec, "roi": best_roi, "ev": best_r["ev"],
                         "Sl": best_r["Sl"], "result": best_r}

    improved = "***" if best_ec != current_ec and delta > 2 else ""
    print("| %s | +%dc | %+.1f%% | +%dc | %+.1f%% | %.0f%% | $%+.3f | %+.1f%% %s|" % (
        cell, current_ec, current_r["roi"],
        best_ec, best_roi, best_r["Sl"]*100, best_r["ev"], delta, improved))

# Also test ALL active cells for optimal exit
print()
print("=== Full exit optimization (ALL cells) ===")
print("| Cell | Current exit | Current ROI | Optimal exit | Optimal ROI | Delta |")
print("|---|---|---|---|---|---|")

optimal_results = {}
for cell in sorted(ALL_CELLS.keys()):
    entries = all_entries.get(cell, [])
    if not entries or len(entries) < 15: continue

    current_ec = ALL_CELLS[cell]
    current_r = compute_cell_ev(entries, current_ec)

    best_roi = -999
    best_ec = current_ec
    best_r = current_r

    for test_ec in range(3, 41):
        r = compute_cell_ev(entries, test_ec)
        if r["roi"] > best_roi:
            best_roi = r["roi"]
            best_ec = test_ec
            best_r = r

    optimal_results[cell] = best_r
    delta = best_roi - current_r["roi"]
    flag = "***" if delta > 3 else ""
    print("| %s | +%dc | %+.1f%% | +%dc | %+.1f%% | %+.1f%% %s|" % (
        cell, current_ec, current_r["roi"], best_ec, best_roi, delta, flag))


# =====================================================================
# TASK 8: Optimized portfolio
# =====================================================================
print()
print("=" * 80)
print("=== TASK 8: OPTIMIZED PORTFOLIO ===")
print("=" * 80)
print()

# Build optimal portfolio:
# - Keep cells with optimal ROI > 0 and N >= 20
# - Use optimal exit for each
optimal_cells = set()
for cell, r in optimal_results.items():
    if r["roi"] > 0 and r["n"] >= 20:
        optimal_cells.add(cell)
        print("  %s: +%dc exit, ROI=%+.1f%%, N=%d, daily=$%+.3f" % (
            cell, r["exit_c"], r["roi"], r["n"], r["daily_dollar"]))

print()
print("--- SCENARIO E: Optimized portfolio (%d cells at optimal exits) ---" % len(optimal_cells))
sc_e = run_mc(optimal_cells, optimal_results, "Optimized (all cells at best exit)")


# =====================================================================
# COMPARISON TABLE
# =====================================================================
print("=" * 80)
print("=== SCENARIO COMPARISON ===")
print("=" * 80)
print()
print("| Scenario | Cells | Daily EV$ | MC Mean | Sharpe | P5 worst | P95 best |")
print("|---|---|---|---|---|---|---|")
for label, sc in [("A: Current 25 active", sc_a),
                   ("B: Trim negatives", sc_b),
                   ("C: Aggressive (ROI>3%)", sc_c),
                   ("D: Trimmed + 60-64", sc_d),
                   ("E: All cells optimal exit", sc_e)]:
    print("| %s | %d | $%.2f | $%.2f | %.3f | $%.2f | $%.2f |" % (
        label, sc["cells"], sc["daily_ev"], sc["mc_mean"],
        sc["sharpe"], sc["p5"], sc["p95"]))

print()
print("=" * 80)
print("OPTIMIZATION COMPLETE")
print("=" * 80)
