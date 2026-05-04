import sqlite3, csv, random
from collections import defaultdict

random.seed(42)

bias_map = {}
with open("/tmp/per_cell_verification/entry_price_bias_by_cell.csv") as f:
    for r in csv.DictReader(f):
        if int(r["N_late"]) >= 10:
            bias_map[r["cell"]] = float(r["mean_bias_first_vs_late_mid"])

conn = sqlite3.connect("/root/Omi-Workspace/arb-executor/tennis.db")
cur = conn.cursor()
cur.execute("""SELECT category, first_price_winner, max_price_winner, last_price_winner,
                      first_price_loser, max_price_loser, first_ts
               FROM historical_events
               WHERE total_trades >= 10
                 AND first_price_winner > 0 AND first_price_winner < 100
                 AND first_price_loser > 0 AND first_price_loser < 100""")
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
for cat, fpw, maxw, lastw, fpl, maxl, ts in rows:
    if cat not in cat_to_tier: continue
    day = ts[:10]

    for side, fp, max_p, settle in [("winner", fpw, maxw, lastw if lastw else 99), ("loser", fpl, maxl, 1)]:
        raw = classify(cat, fp)
        if not raw: continue
        bias = bias_map.get(raw, 0)
        corrected = fp - bias
        cell = classify(cat, corrected)
        if not cell: continue
        cell_events[cell].append((side, corrected, max_p, settle, day))

def event_pnl(side, entry, max_p, settle):
    target = min(99, entry + EXIT_C)
    scalped = max_p is not None and max_p >= target
    if scalped:
        return EXIT_C * QTY / 100
    elif side == "winner":
        return (settle - entry) * QTY / 100
    else:
        return -(entry - settle) * QTY / 100

def compute_roi(events):
    if not events: return 0
    total_cost = sum(e[1] * QTY / 100 for e in events)
    total_pnl = sum(event_pnl(e[0], e[1], e[2], e[3]) for e in events)
    return total_pnl / total_cost * 100 if total_cost > 0 else 0

target_cells = [
    # SCALPER_NEGATIVE
    "ATP_CHALL_leader_65-69", "WTA_MAIN_leader_65-69", "ATP_MAIN_leader_60-64",
    "ATP_MAIN_leader_70-74", "WTA_MAIN_leader_70-74", "WTA_MAIN_leader_60-64",
    # SETTLEMENT_RIDE_CONTAMINATED
    "ATP_CHALL_leader_80-84", "ATP_CHALL_leader_85-89", "WTA_MAIN_leader_85-89",
]

print("Bootstrap CI for SCALPER_NEGATIVE + SETTLEMENT_RIDE_CONTAMINATED cells")
print("=" * 95)
print("%-32s %-5s %-8s %-8s %-8s %-8s %s" % ("cell", "N", "point", "boot_m", "2.5%", "97.5%", "verdict"))
print("-" * 95)

portfolio_events = []
results = []
for cell in target_cells:
    events = cell_events.get(cell, [])
    if len(events) < 10:
        print("  %-30s N=%-3d insufficient" % (cell, len(events)))
        continue

    point = compute_roi(events)

    bootstrap_rois = []
    for _ in range(1000):
        sample = [random.choice(events) for _ in range(len(events))]
        bootstrap_rois.append(compute_roi(sample))

    bootstrap_rois.sort()
    boot_mean = sum(bootstrap_rois) / len(bootstrap_rois)
    p025 = bootstrap_rois[25]
    p975 = bootstrap_rois[974]

    if p975 < 0:
        verdict = "CONFIRMED BLEED"
    elif p025 > 0:
        verdict = "CONFIRMED +EV"
    else:
        verdict = "UNCERTAIN (crosses zero)"

    portfolio_events.extend(events)
    results.append({"cell": cell, "n": len(events), "point": point, "boot_mean": boot_mean, "lo": p025, "hi": p975, "verdict": verdict})

    print("  %-30s %-5d %+7.1f%% %+7.1f%% %+7.1f%% %+7.1f%% %s" % (cell, len(events), point, boot_mean, p025, p975, verdict))

# Summary
print()
confirmed_bleed = sum(1 for r in results if "BLEED" in r["verdict"])
uncertain = sum(1 for r in results if "UNCERTAIN" in r["verdict"])
confirmed_pos = sum(1 for r in results if "+EV" in r["verdict"])
print("Confirmed bleed (CI entirely < 0): %d" % confirmed_bleed)
print("Uncertain (CI crosses zero):       %d" % uncertain)
print("Confirmed +EV (CI entirely > 0):   %d" % confirmed_pos)

# Portfolio economics
days = set()
total_cost = 0
total_pnl = 0
for e in portfolio_events:
    days.add(e[4])
    total_cost += e[1] * QTY / 100
    total_pnl += event_pnl(e[0], e[1], e[2], e[3])

print()
print("=== PORTFOLIO (9 BLEED-candidate cells) ===")
print("Total events: %d" % len(portfolio_events))
print("Distinct active days: %d" % len(days))
print("Total cost basis: $%.2f" % total_cost)
print("Total P&L: $%+.2f" % total_pnl)
print("Aggregate ROI: %+.2f%%" % (total_pnl/total_cost*100))
print("Avg cost cycled per active day: $%.2f" % (total_cost/len(days)))
print("Avg P&L per active day: $%+.2f" % (total_pnl/len(days)))
print("Daily ROI on capital cycled: %+.2f%%" % ((total_pnl/len(days))/(total_cost/len(days))*100))

# Portfolio bootstrap
print()
print("=== PORTFOLIO BOOTSTRAP ===")
port_boots = []
for _ in range(1000):
    sample = [random.choice(portfolio_events) for _ in range(len(portfolio_events))]
    total_c = sum(e[1] * QTY / 100 for e in sample)
    total_p = sum(event_pnl(e[0], e[1], e[2], e[3]) for e in sample)
    port_boots.append(total_p / total_c * 100 if total_c > 0 else 0)
port_boots.sort()
print("Portfolio ROI 95%% CI: [%+.2f%%, %+.2f%%]" % (port_boots[25], port_boots[974]))
print("Portfolio PnL 95%% CI: [$%+.2f, $%+.2f]" % (port_boots[25]*total_cost/100, port_boots[974]*total_cost/100))
