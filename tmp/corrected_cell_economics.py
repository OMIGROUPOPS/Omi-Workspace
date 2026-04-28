#!/usr/bin/env python3
"""
Corrected Per-Cell Economics — Decomposed scalp rates with proper payoff paths.

Key correction: Scalp WR is separated into winner-side (Sw) and loser-side (Sl).
Winner-side scalp ≈ 100% but COSTS upside (scalp profit < settlement profit).
Loser-side scalp is the variable that determines cell viability.

EV per entry = w × [Sw × exit_c + (1-Sw) × (99-E)]
             + (1-w-s) × [Sl × exit_c + (1-Sl) × -(E-1)]
             + s × scalar_pnl

Where:
  w = P(side wins settlement)
  s = P(scalar: retirement/walkover, settle mid-range)
  Sw = P(scalp fires | win path) — price hits exit target on way to 99
  Sl = P(scalp fires | loss path) — price hits exit target despite losing
  E = entry price, exit_c = exit target in cents above entry
"""

import sqlite3, json, csv, os, math, random
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/corrected_analysis"
os.makedirs(OUT_DIR, exist_ok=True)

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

# Load data
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
QTY = 10  # contracts per fill

# Build per-cell entries with full decomposition
cell_entries = defaultdict(list)

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue

    fp_w, min_w, max_w, last_w = ev[4], ev[5], ev[6], ev[7]
    fp_l = ev[8]
    min_l, max_l = ev[12], ev[13]

    # Detect scalar (retirement/walkover): winner doesn't reach 99
    is_scalar = max_w is not None and max_w < 95

    # Winner side entry
    if fp_w and 0 < fp_w < 100:
        c = classify_cell(tier, fp_w)
        if c in ALL_CELLS:
            exit_c = ALL_CELLS[c]
            target = min(99, fp_w + exit_c)
            scalped = max_w is not None and max_w >= target
            cell_entries[c].append({
                "side": "winner", "entry": fp_w, "exit_c": exit_c,
                "target": target, "scalped": scalped,
                "max_price": max_w, "is_scalar": is_scalar,
                "settle_price": last_w if last_w else 99,
                "evt": evt,
            })

    # Loser side entry
    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        if c in ALL_CELLS:
            exit_c = ALL_CELLS[c]
            target = min(99, fp_l + exit_c)
            scalped = max_l is not None and max_l >= target
            cell_entries[c].append({
                "side": "loser", "entry": fp_l, "exit_c": exit_c,
                "target": target, "scalped": scalped,
                "max_price": max_l, "is_scalar": is_scalar,
                "settle_price": min_l if min_l else 1,
                "evt": evt,
            })

# =====================================================================
# TASK 1: Decomposed scalp rates
# =====================================================================
print("=" * 80)
print("=== TASK 1: PER-CELL DECOMPOSED SCALP RATES ===")
print("=" * 80)
print()

task1 = {}
print("| Cell | Status | Exit | N | N_win | N_lose | N_scalar | Sw (win scalp%) | Sl (lose scalp%) | Blended (old) |")
print("|---|---|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    entries = cell_entries.get(cell, [])
    if not entries: continue
    n = len(entries)
    exit_c = ALL_CELLS[cell]
    is_active = cell in active_cells

    winners = [e for e in entries if e["side"] == "winner" and not e["is_scalar"]]
    losers = [e for e in entries if e["side"] == "loser" and not e["is_scalar"]]
    scalars = [e for e in entries if e["is_scalar"]]

    n_w, n_l, n_s = len(winners), len(losers), len(scalars)
    w_scalp = sum(1 for e in winners if e["scalped"])
    l_scalp = sum(1 for e in losers if e["scalped"])
    total_scalp = w_scalp + l_scalp + sum(1 for e in scalars if e["scalped"])

    Sw = w_scalp / n_w if n_w else 0
    Sl = l_scalp / n_l if n_l else 0
    blended = total_scalp / n if n else 0

    avg_entry = sum(e["entry"] for e in entries) / n

    task1[cell] = {
        "n": n, "n_w": n_w, "n_l": n_l, "n_s": n_s,
        "Sw": Sw, "Sl": Sl, "blended": blended,
        "avg_entry": avg_entry, "exit_c": exit_c,
        "is_active": is_active, "entries": entries,
        "w": n_w / (n_w + n_l) if (n_w + n_l) else 0,
        "s_rate": n_s / n if n else 0,
    }

    flag = "" if n >= 30 else "*"
    print("| %s | %s | +%d | %d%s | %d | %d | %d | %.0f%% | %.0f%% | %.0f%% |" % (
        cell, "ON" if is_active else "off", exit_c, n, flag,
        n_w, n_l, n_s, Sw*100, Sl*100, blended*100))

# =====================================================================
# TASK 2: Per-cell true expected $ per event
# =====================================================================
print()
print("=" * 80)
print("=== TASK 2: PER-CELL TRUE EXPECTED $ PER EVENT ===")
print("=" * 80)
print()

print("| Cell | w | Sw | Sl | scalp$ | win_settle$ | loss_settle$ | EV$/event | Daily fires | Daily$ |")
print("|---|---|---|---|---|---|---|---|---|---|")

task2 = {}
for cell in sorted(ALL_CELLS.keys()):
    t = task1.get(cell)
    if not t or t["n"] < 10: continue

    E = t["avg_entry"]
    exit_c = t["exit_c"]
    w = t["w"]
    s = t["s_rate"]
    Sw = t["Sw"]
    Sl = t["Sl"]

    scalp_profit = exit_c * QTY / 100  # $ per scalp
    win_settle = (99 - E) * QTY / 100  # $ if side wins, no scalp
    loss_settle = -(E - 1) * QTY / 100  # $ if side loses, no scalp

    # Scalar outcome: approximate as break-even (settle at mid-price)
    # In reality, retirements settle at last traded price
    scalar_entries = [e for e in t["entries"] if e["is_scalar"]]
    if scalar_entries:
        scalar_pnl = sum((e["settle_price"] - e["entry"]) * QTY / 100 for e in scalar_entries) / len(scalar_entries)
    else:
        scalar_pnl = 0

    # EV per event
    ev_win = w * (Sw * scalp_profit + (1 - Sw) * win_settle)
    ev_lose = (1 - w - s) * (Sl * scalp_profit + (1 - Sl) * loss_settle)
    ev_scalar = s * scalar_pnl
    ev_total = ev_win + ev_lose + ev_scalar

    daily_fires = t["n"] / DAYS / 2
    daily_dollar = daily_fires * ev_total

    task2[cell] = {
        "w": w, "Sw": Sw, "Sl": Sl, "s": s,
        "scalp_profit": scalp_profit, "win_settle": win_settle,
        "loss_settle": loss_settle, "scalar_pnl": scalar_pnl,
        "ev_total": ev_total, "daily_fires": daily_fires,
        "daily_dollar": daily_dollar, "avg_entry": E, "exit_c": exit_c,
        "n": t["n"], "is_active": t["is_active"],
    }

    flag = "*" if t["n"] < 30 else ""
    print("| %s | %.2f | %.0f%% | %.0f%% | $%.2f | $%.2f | $%.2f | $%+.2f | %.1f | $%+.2f |" % (
        cell, w, Sw*100, Sl*100, scalp_profit, win_settle, loss_settle,
        ev_total, daily_fires, daily_dollar))


# =====================================================================
# TASK 3: Per-cell ROI on capital deployed
# =====================================================================
print()
print("=" * 80)
print("=== TASK 3: PER-CELL ROI ON CAPITAL DEPLOYED ===")
print("=" * 80)
print()

print("| Cell | Status | Avg cost basis | Expected $ | ROI % | Confidence |")
print("|---|---|---|---|---|---|")

for cell in sorted(task2.keys()):
    t = task2[cell]
    cost_basis = t["avg_entry"] * QTY / 100  # $ per entry
    roi = t["ev_total"] / cost_basis * 100 if cost_basis else 0
    conf = "HIGH" if t["n"] >= 50 else "MEDIUM" if t["n"] >= 30 else "LOW"
    print("| %s | %s | $%.2f | $%+.3f | %+.1f%% | %s |" % (
        cell, "ON" if t["is_active"] else "off", cost_basis,
        t["ev_total"], roi, conf))

# =====================================================================
# TASK 4: Variance and Sharpe per cell
# =====================================================================
print()
print("=" * 80)
print("=== TASK 4: VARIANCE AND SHARPE PER CELL ===")
print("=" * 80)
print()

print("| Cell | EV$/event | StdDev | Sharpe | 95% CI low | 95% CI high |")
print("|---|---|---|---|---|---|")

task4 = {}
for cell in sorted(ALL_CELLS.keys()):
    t1 = task1.get(cell)
    t2 = task2.get(cell)
    if not t1 or not t2 or t1["n"] < 10: continue

    # Compute per-event $ outcomes
    outcomes = []
    for e in t1["entries"]:
        exit_c = e["exit_c"]
        entry = e["entry"]
        if e["scalped"]:
            pnl = exit_c * QTY / 100
        elif e["side"] == "winner" and not e["is_scalar"]:
            pnl = (99 - entry) * QTY / 100
        elif e["side"] == "loser" and not e["is_scalar"]:
            pnl = -(entry - 1) * QTY / 100
        else:  # scalar
            pnl = (e["settle_price"] - entry) * QTY / 100
        outcomes.append(pnl)

    mean = sum(outcomes) / len(outcomes)
    variance = sum((x - mean) ** 2 for x in outcomes) / len(outcomes)
    std = variance ** 0.5
    sharpe = mean / std if std > 0 else 0
    n = len(outcomes)
    ci_half = 1.96 * std / (n ** 0.5) if n > 0 else 0

    task4[cell] = {"mean": mean, "std": std, "sharpe": sharpe,
                    "ci_low": mean - ci_half, "ci_high": mean + ci_half,
                    "outcomes": outcomes}

    print("| %s | $%+.3f | $%.3f | %.2f | $%+.3f | $%+.3f |" % (
        cell, mean, std, sharpe, mean - ci_half, mean + ci_half))


# =====================================================================
# TASK 5: Compare corrected to original
# =====================================================================
print()
print("=" * 80)
print("=== TASK 5: CORRECTED VS ORIGINAL ===")
print("=" * 80)
print()

# Load original scorecard
orig = {}
orig_file = "/tmp/harmonized_analysis/task4_harmonized_scorecard.csv"
if os.path.exists(orig_file):
    with open(orig_file) as f:
        for row in csv.DictReader(f):
            orig[row["cell"]] = {
                "blended_scalp": float(row["scalp_WR_pct"]),
                "roi": float(row["ROI_pct"]),
                "dollar": float(row["dollar_per_fill"]),
            }

print("| Cell | Old scalp% | Old ROI | Sw | Sl | Corrected EV$ | Corrected ROI | ROI delta | Status flip? |")
print("|---|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    t1 = task1.get(cell)
    t2 = task2.get(cell)
    o = orig.get(cell)
    if not t1 or not t2: continue
    if t1["n"] < 10: continue

    cost_basis = t2["avg_entry"] * QTY / 100
    corrected_roi = t2["ev_total"] / cost_basis * 100 if cost_basis else 0

    old_scalp = o["blended_scalp"] if o else 0
    old_roi = o["roi"] if o else 0
    old_dollar = o["dollar"] if o else 0

    delta = corrected_roi - old_roi

    # Status flip check
    if old_roi > 0 and corrected_roi <= 0:
        flip = "POS->NEG"
    elif old_roi <= 0 and corrected_roi > 0:
        flip = "NEG->POS"
    elif old_roi > 0 and corrected_roi > 0 and abs(delta) > 10:
        flip = "WEAKENED" if delta < 0 else "STRENGTHENED"
    else:
        flip = "-"

    flag = "*" if t1["n"] < 30 else ""
    print("| %s | %.0f%% | %+.1f%% | %.0f%% | %.0f%% | $%+.3f | %+.1f%% | %+.1f%% | %s |" % (
        cell, old_scalp, old_roi, t1["Sw"]*100, t1["Sl"]*100,
        t2["ev_total"], corrected_roi, delta, flip))


# =====================================================================
# TASK 6: Portfolio-level corrected projection
# =====================================================================
print()
print("=" * 80)
print("=== TASK 6: PORTFOLIO-LEVEL CORRECTED PROJECTION ===")
print("=" * 80)
print()

# Active cells only
active_daily = 0
active_outcomes = {}
for cell in sorted(ALL_CELLS.keys()):
    t2 = task2.get(cell)
    t4 = task4.get(cell)
    if not t2 or not t4 or not t2["is_active"]: continue
    active_daily += t2["daily_dollar"]
    active_outcomes[cell] = t4["outcomes"]

print("Daily expected $ (active cells, corrected): $%.2f" % active_daily)
print()

# Monte Carlo with corrected outcomes
random.seed(42)
sim_daily = []
for _ in range(10000):
    day = 0
    for cell, outcomes in active_outcomes.items():
        t2 = task2[cell]
        fires = max(1, int(round(t2["daily_fires"])))
        for _ in range(fires):
            day += random.choice(outcomes)
    sim_daily.append(day)

sim_daily.sort()
ns = len(sim_daily)
avg = sum(sim_daily) / ns
std = (sum((x - avg)**2 for x in sim_daily) / ns) ** 0.5
sharpe = avg / std if std else 0

print("=== Monte Carlo (10K sims, corrected payoffs) ===")
print("  Mean daily PnL:    $%.2f" % avg)
print("  Std dev:           $%.2f" % std)
print("  Sharpe (daily):    %.2f" % sharpe)
print("  P5 (worst day):    $%.2f" % sim_daily[ns // 20])
print("  P25:               $%.2f" % sim_daily[ns // 4])
print("  Median:            $%.2f" % sim_daily[ns // 2])
print("  P75:               $%.2f" % sim_daily[3 * ns // 4])
print("  P95 (best day):    $%.2f" % sim_daily[19 * ns // 20])
print()

# Compare to original
print("=== COMPARISON TO ORIGINAL PROJECTIONS ===")
print("  Original daily expected:  $35.77")
print("  Corrected daily expected: $%.2f" % active_daily)
print("  Original MC mean:         $-2.57")
print("  Corrected MC mean:        $%.2f" % avg)
print("  Original MC Sharpe:       -0.15")
print("  Corrected MC Sharpe:      %.2f" % sharpe)


# =====================================================================
# TASK 7: Paired cell joint economics
# =====================================================================
print()
print("=" * 80)
print("=== TASK 7: PAIRED CELL JOINT ECONOMICS ===")
print("=" * 80)
print()

# For each event, find if both sides are in active cells
pair_results = defaultdict(lambda: {"events": []})

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, max_w, fp_l, max_l = ev[4], ev[6], ev[8], ev[13]
    if not fp_w or not fp_l or fp_w <= 0 or fp_l <= 0: continue

    cw = classify_cell(tier, fp_w)
    cl = classify_cell(tier, fp_l)
    if cw not in ALL_CELLS or cl not in ALL_CELLS: continue

    ew, el = ALL_CELLS[cw], ALL_CELLS[cl]
    tw = min(99, fp_w + ew)
    tl = min(99, fp_l + el)
    sw = max_w is not None and max_w >= tw
    sl = max_l is not None and max_l >= tl

    # Winner side PnL
    if sw:
        pnl_w = ew * QTY / 100
    else:
        pnl_w = (99 - fp_w) * QTY / 100

    # Loser side PnL
    if sl:
        pnl_l = el * QTY / 100
    else:
        pnl_l = -(fp_l - 1) * QTY / 100

    pk = tuple(sorted([cw, cl]))
    pair_results[pk]["events"].append({
        "pnl_w": pnl_w, "pnl_l": pnl_l, "joint": pnl_w + pnl_l,
        "sw": sw, "sl": sl, "cap_w": fp_w * QTY / 100, "cap_l": fp_l * QTY / 100,
    })

print("| Pair | N | P(both scalp) | P(w only) | P(l only) | P(neither) | Joint EV$ | Joint Sharpe | Solo sum$ |")
print("|---|---|---|---|---|---|---|---|---|")

for pair in sorted(pair_results.keys()):
    evts = pair_results[pair]["events"]
    n = len(evts)
    if n < 5: continue

    both = sum(1 for e in evts if e["sw"] and e["sl"])
    w_only = sum(1 for e in evts if e["sw"] and not e["sl"])
    l_only = sum(1 for e in evts if not e["sw"] and e["sl"])
    neither = sum(1 for e in evts if not e["sw"] and not e["sl"])

    joints = [e["joint"] for e in evts]
    j_mean = sum(joints) / n
    j_std = (sum((x - j_mean)**2 for x in joints) / n) ** 0.5
    j_sharpe = j_mean / j_std if j_std else 0

    # Solo expected $ (sum of individual cell EVs)
    t2_a = task2.get(pair[0], {})
    t2_b = task2.get(pair[1], {})
    solo_sum = t2_a.get("ev_total", 0) + t2_b.get("ev_total", 0)

    print("| %s / %s | %d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | $%+.2f | %.2f | $%+.2f |" % (
        pair[0], pair[1], n,
        both/n*100, w_only/n*100, l_only/n*100, neither/n*100,
        j_mean, j_sharpe, solo_sum))


# =====================================================================
# TASK 8: Per-cell corrected recommendations
# =====================================================================
print()
print("=" * 80)
print("=== TASK 8: PER-CELL CORRECTED RECOMMENDATIONS ===")
print("=" * 80)
print()

print("| Cell | Status | N | Corrected ROI | Sl (lose-side scalp) | EV$/event | Rec | Reason |")
print("|---|---|---|---|---|---|---|---|")

for cell in sorted(ALL_CELLS.keys()):
    t1 = task1.get(cell)
    t2 = task2.get(cell)
    t4 = task4.get(cell)
    if not t1 or not t2: continue

    n = t1["n"]
    is_active = t1["is_active"]
    cost_basis = t2["avg_entry"] * QTY / 100
    roi = t2["ev_total"] / cost_basis * 100 if cost_basis else 0
    Sl = t1["Sl"]
    ev = t2["ev_total"]

    ci_low = t4["ci_low"] if t4 else 0
    ci_high = t4["ci_high"] if t4 else 0

    if n < 15:
        rec, reason = "INVESTIGATE", "N=%d too low for confidence" % n
    elif is_active:
        if roi > 0 and ci_low > -0.05:
            rec, reason = "KEEP", "ROI %+.1f%%, CI includes positive" % roi
        elif roi > 0 and ci_low <= -0.05:
            rec, reason = "KEEP-WATCH", "ROI %+.1f%% but CI includes negative ($%.3f)" % (roi, ci_low)
        elif roi <= 0 and roi > -5:
            rec, reason = "RETUNE", "ROI %+.1f%%, Sl=%.0f%% — try different exit" % (roi, Sl*100)
        else:
            rec, reason = "DISABLE", "ROI %+.1f%% — corrected math shows negative EV" % roi
    else:
        if roi > 3 and n >= 30 and ci_low > 0:
            rec, reason = "RE-ENABLE", "ROI %+.1f%%, CI fully positive" % roi
        elif roi > 0 and n >= 20:
            rec, reason = "RE-ENABLE", "ROI %+.1f%%, N=%d" % (roi, n)
        else:
            rec, reason = "STAY-OFF", "ROI %+.1f%%" % roi

    flag = "*" if n < 30 else ""
    print("| %s | %s | %d%s | %+.1f%% | %.0f%% | $%+.3f | %s | %s |" % (
        cell, "ON" if is_active else "off", n, flag, roi, Sl*100, ev, rec, reason))


# =====================================================================
# WRITE CSVs
# =====================================================================
print()
print("=" * 80)
print("Writing CSVs...")

# Task 1-2-3 combined scorecard
with open(os.path.join(OUT_DIR, "corrected_scorecard.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","status","exit_c","N","N_win","N_lose","N_scalar",
                "avg_entry","w","Sw","Sl","blended_scalp",
                "scalp_profit","win_settle","loss_settle",
                "EV_per_event","cost_basis","ROI_pct",
                "daily_fires","daily_dollar",
                "std_dev","sharpe","ci_low","ci_high",
                "recommendation","reason"])
    for cell in sorted(ALL_CELLS.keys()):
        t1 = task1.get(cell)
        t2 = task2.get(cell)
        t4 = task4.get(cell)
        if not t1 or not t2: continue
        cost = t2["avg_entry"] * QTY / 100
        roi = t2["ev_total"] / cost * 100 if cost else 0

        # Recommendation (same logic as above)
        n = t1["n"]
        is_active = t1["is_active"]
        Sl = t1["Sl"]
        ci_low = t4["ci_low"] if t4 else 0
        if n < 15: rec = "INVESTIGATE"
        elif is_active:
            if roi > 0 and ci_low > -0.05: rec = "KEEP"
            elif roi > 0: rec = "KEEP-WATCH"
            elif roi > -5: rec = "RETUNE"
            else: rec = "DISABLE"
        else:
            if roi > 3 and n >= 30 and ci_low > 0: rec = "RE-ENABLE"
            elif roi > 0 and n >= 20: rec = "RE-ENABLE"
            else: rec = "STAY-OFF"

        w.writerow([cell, "ACTIVE" if is_active else "disabled", t1["exit_c"],
                     t1["n"], t1["n_w"], t1["n_l"], t1["n_s"],
                     "%.1f" % t2["avg_entry"], "%.3f" % t2["w"],
                     "%.3f" % t1["Sw"], "%.3f" % t1["Sl"], "%.3f" % t1["blended"],
                     "%.3f" % t2["scalp_profit"], "%.3f" % t2["win_settle"],
                     "%.3f" % t2["loss_settle"],
                     "%.4f" % t2["ev_total"], "%.3f" % cost, "%.1f" % roi,
                     "%.2f" % t2["daily_fires"], "%.3f" % t2["daily_dollar"],
                     "%.3f" % (t4["std"] if t4 else 0),
                     "%.3f" % (t4["sharpe"] if t4 else 0),
                     "%.4f" % (t4["ci_low"] if t4 else 0),
                     "%.4f" % (t4["ci_high"] if t4 else 0),
                     rec, ""])

# Monte Carlo runs
with open(os.path.join(OUT_DIR, "corrected_monte_carlo.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sim_id", "daily_pnl_dollars"])
    for i, pnl in enumerate(sim_daily):
        w.writerow([i, "%.2f" % pnl])

# Comparison table
with open(os.path.join(OUT_DIR, "corrected_vs_original.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["cell","old_blended_scalp","old_ROI","Sw","Sl","corrected_EV",
                  "corrected_ROI","ROI_delta","status_flip"])
    for cell in sorted(ALL_CELLS.keys()):
        t1 = task1.get(cell)
        t2 = task2.get(cell)
        o = orig.get(cell)
        if not t1 or not t2: continue
        cost = t2["avg_entry"] * QTY / 100
        croi = t2["ev_total"] / cost * 100 if cost else 0
        oroi = o["roi"] if o else 0
        delta = croi - oroi
        if oroi > 0 and croi <= 0: flip = "POS->NEG"
        elif oroi <= 0 and croi > 0: flip = "NEG->POS"
        else: flip = "-"
        wr.writerow([cell, "%.1f" % (o["blended_scalp"] if o else 0),
                      "%.1f" % oroi, "%.1f" % (t1["Sw"]*100), "%.1f" % (t1["Sl"]*100),
                      "%.4f" % t2["ev_total"], "%.1f" % croi, "%.1f" % delta, flip])

print("CSVs written to %s/" % OUT_DIR)
for fn in sorted(os.listdir(OUT_DIR)):
    print("  %s (%.1f KB)" % (fn, os.path.getsize(os.path.join(OUT_DIR, fn))/1024))

print()
print("=" * 80)
print("CORRECTED ANALYSIS COMPLETE")
print("=" * 80)
