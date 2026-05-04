import sqlite3, csv
from collections import defaultdict

bias_map = {}
with open("/tmp/per_cell_verification/entry_price_bias_by_cell.csv") as f:
    for r in csv.DictReader(f):
        if int(r["N_late"]) >= 10:
            bias_map[r["cell"]] = float(r["mean_bias_first_vs_late_mid"])

conn = sqlite3.connect("/root/Omi-Workspace/arb-executor/tennis.db")
cur = conn.cursor()
cur.execute("""SELECT category, first_price_winner, max_price_winner, last_price_winner,
                      first_price_loser, max_price_loser
               FROM historical_events
               WHERE total_trades >= 10
                 AND first_price_winner > 0 AND first_price_winner < 100
                 AND first_price_loser > 0 AND first_price_loser < 100""")
rows = cur.fetchall()
conn.close()

cat_to_tier = {"ATP_MAIN":"ATP_MAIN", "ATP_CHALL":"ATP_CHALL",
               "WTA_MAIN":"WTA_MAIN", "WTA_CHALL":"WTA_CHALL"}

QTY = 10

def classify(tier_str, price):
    if tier_str not in cat_to_tier: return None
    tier = cat_to_tier[tier_str]
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

# Build per-cell event lists with corrected entries
cell_events = defaultdict(list)
for cat, fpw, maxw, lastw, fpl, maxl in rows:
    if cat not in cat_to_tier: continue
    for side, fp, max_p, settle in [("winner", fpw, maxw, lastw if lastw else 99), ("loser", fpl, maxl, 1)]:
        raw = classify(cat, fp)
        if not raw: continue
        bias = bias_map.get(raw, 0)
        corrected = fp - bias
        cell = classify(cat, corrected)
        if not cell: continue
        cell_events[cell].append((side, corrected, max_p, settle))

def compute_roi_at_exit(events, exit_c):
    total_cost = 0
    total_pnl = 0
    n_scalp = 0
    for side, entry, max_p, settle in events:
        if entry <= 0 or entry >= 100: continue
        target = min(99, entry + exit_c)
        scalped = max_p is not None and max_p >= target
        cost = entry * QTY / 100
        if scalped:
            pnl = exit_c * QTY / 100
            n_scalp += 1
        elif side == "winner":
            pnl = (settle - entry) * QTY / 100
        else:
            pnl = -(entry - settle) * QTY / 100
        total_cost += cost
        total_pnl += pnl
    roi = total_pnl / total_cost * 100 if total_cost > 0 else 0
    hit_rate = n_scalp / len(events) * 100 if events else 0
    return roi, total_pnl, total_cost, hit_rate

results = []
full_sweep = []
for cell, events in cell_events.items():
    if len(events) < 30: continue

    best_exit = 0
    best_roi = -999
    best_pnl = 0
    best_cost = 0
    best_hit = 0
    for exit_c in range(5, 41):
        roi, pnl, cost, hit = compute_roi_at_exit(events, exit_c)
        full_sweep.append({"cell": cell, "exit_c": exit_c, "roi": round(roi, 2), "hit_rate": round(hit, 1)})
        if roi > best_roi:
            best_roi = roi
            best_exit = exit_c
            best_pnl = pnl
            best_cost = cost
            best_hit = hit

    roi_15, pnl_15, cost_15, hit_15 = compute_roi_at_exit(events, 15)

    results.append({
        "cell": cell, "N": len(events),
        "optimal_exit": best_exit, "optimal_ROI": best_roi, "hit_at_opt": best_hit,
        "ROI_at_15c": roi_15, "hit_at_15c": hit_15,
        "improvement_pp": best_roi - roi_15,
        "pnl_at_optimal": best_pnl, "cost_at_optimal": best_cost,
    })

results.sort(key=lambda x: -x["optimal_ROI"])

print("%-32s %5s %6s %8s %6s %8s %6s %8s" % (
    "cell", "N", "opt_x", "opt_ROI", "hit%", "ROI@15", "hit15", "improv"))
print("-" * 100)
for r in results:
    print("  %-30s %5d %4dc %+7.1f%% %5.0f%% %+7.1f%% %5.0f%% %+6.1fpp" % (
        r["cell"], r["N"], r["optimal_exit"], r["optimal_ROI"], r["hit_at_opt"],
        r["ROI_at_15c"], r["hit_at_15c"], r["improvement_pp"]))

# Save per-cell summary
with open("/tmp/optimal_exits.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=["cell","N","optimal_exit","optimal_ROI","hit_at_opt",
        "ROI_at_15c","hit_at_15c","improvement_pp","pnl_at_optimal","cost_at_optimal"])
    w.writeheader()
    for r in results:
        w.writerow(r)

# Save full sweep grid
with open("/tmp/exit_sweep_grid.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=["cell","exit_c","roi","hit_rate"])
    w.writeheader()
    for r in full_sweep:
        w.writerow(r)

print("\nSaved: /tmp/optimal_exits.csv")
print("Saved: /tmp/exit_sweep_grid.csv")

# Summary stats
print("\n=== SUMMARY ===")
n_at_15 = sum(1 for r in results if r["optimal_exit"] == 15)
print("Cells where 15c is already optimal: %d / %d" % (n_at_15, len(results)))
lower = [r for r in results if r["optimal_exit"] < 15]
higher = [r for r in results if r["optimal_exit"] > 15]
print("Cells that want LOWER exit: %d (avg optimal: %.0fc)" % (len(lower), sum(r["optimal_exit"] for r in lower)/len(lower) if lower else 0))
print("Cells that want HIGHER exit: %d (avg optimal: %.0fc)" % (len(higher), sum(r["optimal_exit"] for r in higher)/len(higher) if higher else 0))

# What would aggregate portfolio ROI be at each cell's optimal vs uniform 15c?
total_pnl_opt = sum(r["pnl_at_optimal"] for r in results)
total_cost_opt = sum(r["cost_at_optimal"] for r in results)
total_pnl_15 = 0
total_cost_15 = 0
for cell, events in cell_events.items():
    if len(events) < 30: continue
    _, p, c, _ = compute_roi_at_exit(events, 15)
    total_pnl_15 += p
    total_cost_15 += c

print("\nPortfolio at uniform 15c: ROI = %.2f%%, PnL = $%.2f" % (total_pnl_15/total_cost_15*100, total_pnl_15))
print("Portfolio at per-cell optimal: ROI = %.2f%%, PnL = $%.2f" % (total_pnl_opt/total_cost_opt*100, total_pnl_opt))
print("Improvement: %+.2fpp ROI, $%+.2f PnL" % (total_pnl_opt/total_cost_opt*100 - total_pnl_15/total_cost_15*100, total_pnl_opt - total_pnl_15))
