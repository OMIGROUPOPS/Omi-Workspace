import sqlite3, csv, random
from collections import defaultdict
from statistics import mean
from math import sqrt

random.seed(42)

# Load bias corrections
bias_map = {}
with open("/tmp/per_cell_verification/entry_price_bias_by_cell.csv") as f:
    for r in csv.DictReader(f):
        n_late = int(r["N_late"])
        if n_late >= 10:
            bias_map[r["cell"]] = float(r["mean_bias_first_vs_late_mid"])

# Load historical events
conn = sqlite3.connect("/root/Omi-Workspace/arb-executor/tennis.db")
cur = conn.cursor()
cur.execute("""SELECT category, first_price_winner, max_price_winner, last_price_winner,
                      first_price_loser, max_price_loser
               FROM historical_events
               WHERE first_ts > ? AND first_ts < ? AND total_trades >= 10
                 AND first_price_winner > 0 AND first_price_winner < 100
                 AND first_price_loser > 0 AND first_price_loser < 100""",
            ("2026-01-01", "2026-04-30"))
rows = cur.fetchall()
conn.close()

cat_to_tier = {"ATP_MAIN":"ATP_MAIN", "ATP_CHALL":"ATP_CHALL",
               "WTA_MAIN":"WTA_MAIN", "WTA_CHALL":"WTA_CHALL"}
EXIT_C = 15
QTY = 10

def classify(tier_str, price):
    if tier_str not in cat_to_tier: return None
    tier = cat_to_tier[tier_str]
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

# Build per-cell event lists
cell_events = defaultdict(list)

for cat, fpw, maxw, lastw, fpl, maxl in rows:
    if cat not in cat_to_tier: continue
    # Winner side
    raw_cell_w = classify(cat, fpw)
    if raw_cell_w:
        bias_w = bias_map.get(raw_cell_w, 0)
        corrected_fp_w = fpw - bias_w
        corrected_cell_w = classify(cat, corrected_fp_w)
        if corrected_cell_w:
            cell_events[corrected_cell_w].append({
                "side": "winner", "entry": corrected_fp_w, "max_price": maxw, "last_price": lastw or 99
            })
    # Loser side
    raw_cell_l = classify(cat, fpl)
    if raw_cell_l:
        bias_l = bias_map.get(raw_cell_l, 0)
        corrected_fp_l = fpl - bias_l
        corrected_cell_l = classify(cat, corrected_fp_l)
        if corrected_cell_l:
            cell_events[corrected_cell_l].append({
                "side": "loser", "entry": corrected_fp_l, "max_price": maxl, "last_price": None
            })

# SCALPER_EDGE cells from rebuilt scorecard
scalper_edge_cells = [
    "ATP_CHALL_underdog_10-14", "WTA_MAIN_underdog_15-19", "ATP_CHALL_underdog_15-19",
    "ATP_CHALL_underdog_20-24", "ATP_MAIN_underdog_20-24", "ATP_CHALL_underdog_25-29",
    "WTA_MAIN_underdog_25-29", "ATP_CHALL_underdog_30-34", "WTA_MAIN_underdog_30-34",
    "ATP_CHALL_leader_60-64", "ATP_CHALL_underdog_35-39", "ATP_CHALL_underdog_40-44",
    "WTA_MAIN_underdog_40-44", "WTA_MAIN_underdog_35-39", "ATP_CHALL_leader_55-59"
]

N_BOOT = 1000

def compute_ev_from_events(events):
    if not events:
        return None
    w_events = [e for e in events if e["side"] == "winner"]
    l_events = [e for e in events if e["side"] == "loser"]
    n_w = len(w_events)
    n_l = len(l_events)
    n_total = n_w + n_l
    if n_total < 10:
        return None

    # Compute Sw and Sl
    w_scalp = sum(1 for e in w_events if e["max_price"] is not None and e["max_price"] >= min(99, e["entry"] + EXIT_C))
    l_scalp = sum(1 for e in l_events if e["max_price"] is not None and e["max_price"] >= min(99, e["entry"] + EXIT_C))
    Sw = w_scalp / n_w if n_w > 0 else 0
    Sl = l_scalp / n_l if n_l > 0 else 0

    # Per-event PnL
    pnls = []
    for e in w_events:
        scalp_pnl = EXIT_C * QTY / 100
        settle_pnl = (99 - e["entry"]) * QTY / 100
        pnls.append(Sw * scalp_pnl + (1 - Sw) * settle_pnl)
    for e in l_events:
        scalp_pnl = EXIT_C * QTY / 100
        settle_pnl = -(e["entry"] - 1) * QTY / 100
        pnls.append(Sl * scalp_pnl + (1 - Sl) * settle_pnl)

    total_pnl = sum(pnls)
    total_cost = sum(e["entry"] * QTY / 100 for e in events)
    roi = total_pnl / total_cost * 100 if total_cost > 0 else 0
    avg_pnl = mean(pnls)
    return {"roi": roi, "avg_pnl": avg_pnl, "n": n_total, "Sw": Sw, "Sl": Sl, "total_pnl": total_pnl}

print("Bootstrap CI (N=%d iterations) for %d SCALPER_EDGE cells" % (N_BOOT, len(scalper_edge_cells)))
print("=" * 120)
print("%-30s %5s %8s %8s %8s %8s %8s %8s %8s %5s" % (
    "Cell", "N", "Point", "Boot_m", "Boot_s", "CI_2.5%", "CI_97.5%", "Anal_lo", "Anal_hi", "Match"))
print("-" * 120)

results = []
for cell in scalper_edge_cells:
    events = cell_events.get(cell, [])
    if len(events) < 20:
        print("%-30s SKIP (N=%d)" % (cell, len(events)))
        continue

    # Point estimate
    point = compute_ev_from_events(events)

    # Bootstrap
    boot_rois = []
    for _ in range(N_BOOT):
        sample = random.choices(events, k=len(events))
        result = compute_ev_from_events(sample)
        if result:
            boot_rois.append(result["roi"])

    boot_rois.sort()
    boot_mean = mean(boot_rois)
    boot_std = sqrt(sum((x - boot_mean)**2 for x in boot_rois) / (len(boot_rois) - 1))
    ci_lo = boot_rois[int(0.025 * len(boot_rois))]
    ci_hi = boot_rois[int(0.975 * len(boot_rois))]

    # Analytical CI from scorecard
    anal_lo = None
    anal_hi = None
    with open("/tmp/rebuilt_scorecard.csv") as f:
        for r in csv.DictReader(f):
            if r["cell"] == cell:
                anal_lo = float(r["ci_low"]) * 100
                anal_hi = float(r["ci_high"]) * 100
                break

    if anal_lo is None:
        anal_lo = 0
        anal_hi = 0

    match = "YES" if (ci_lo > 0 and anal_lo > 0) or (ci_lo <= 0 and anal_lo <= 0) else "NO"

    print("%-30s %5d %+7.1f%% %+7.1f%% %6.1f%% %+7.1f%% %+7.1f%% %+7.1f%% %+7.1f%% %5s" % (
        cell, point["n"], point["roi"], boot_mean, boot_std, ci_lo, ci_hi, anal_lo, anal_hi, match))

    results.append({
        "cell": cell, "N": point["n"], "point_roi": round(point["roi"], 2),
        "boot_mean": round(boot_mean, 2), "boot_std": round(boot_std, 2),
        "boot_ci_lo": round(ci_lo, 2), "boot_ci_hi": round(ci_hi, 2),
        "anal_ci_lo": round(anal_lo, 2), "anal_ci_hi": round(anal_hi, 2),
        "ci_match": match, "Sw": round(point["Sw"], 3), "Sl": round(point["Sl"], 3)
    })

print("\n" + "=" * 120)
all_above_zero = sum(1 for r in results if r["boot_ci_lo"] > 0)
print("\nCells with bootstrap CI entirely above zero: %d / %d" % (all_above_zero, len(results)))
mismatches = [r for r in results if r["ci_match"] == "NO"]
if mismatches:
    print("\nCI MISMATCHES (analytical vs bootstrap disagree on sign):")
    for r in mismatches:
        print("  %s: boot=[%+.1f%%, %+.1f%%] anal=[%+.1f%%, %+.1f%%]" % (
            r["cell"], r["boot_ci_lo"], r["boot_ci_hi"], r["anal_ci_lo"], r["anal_ci_hi"]))
else:
    print("All analytical CIs confirmed by bootstrap - no mismatches.")

# Portfolio bootstrap
print("\n\nPORTFOLIO BOOTSTRAP (all %d SCALPER_EDGE cells combined):" % len(results))
all_events = []
for cell in scalper_edge_cells:
    all_events.extend(cell_events.get(cell, []))

port_boots = []
for _ in range(N_BOOT):
    sample = random.choices(all_events, k=len(all_events))
    r = compute_ev_from_events(sample)
    if r:
        port_boots.append(r["total_pnl"])

port_boots.sort()
port_mean = mean(port_boots)
port_std = sqrt(sum((x - port_mean)**2 for x in port_boots) / (len(port_boots) - 1))
port_lo = port_boots[int(0.025 * len(port_boots))]
port_hi = port_boots[int(0.975 * len(port_boots))]
n_days = 99  # Jan-Apr ~99 trading days
print("  Total events: %d over ~%d days" % (len(all_events), n_days))
print("  Portfolio PnL: $%.2f [95%% CI: $%.2f to $%.2f]" % (port_mean, port_lo, port_hi))
print("  Per-day PnL:   $%.2f/day [95%% CI: $%.2f to $%.2f]" % (port_mean/n_days, port_lo/n_days, port_hi/n_days))

# Save CSV
with open("/tmp/bootstrap_ci_results.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=["cell","N","point_roi","boot_mean","boot_std",
        "boot_ci_lo","boot_ci_hi","anal_ci_lo","anal_ci_hi","ci_match","Sw","Sl"])
    w.writeheader()
    for r in results:
        w.writerow(r)
print("\nSaved: /tmp/bootstrap_ci_results.csv")
