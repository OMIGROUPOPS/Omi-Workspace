#!/usr/bin/env python3
"""
Challenge 1: Verify exit_cents are EV-optimal.
Challenge 2: Leader/underdog mirror consistency.
"""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v3.json"
DAYS = 28
CONTRACTS = 10

config = json.load(open(CONFIG_PATH))

# Load facts
facts = []
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        facts.append(r)

def load_max_bounce(ticker):
    path = os.path.join(TICKS_DIR, "%s.csv" % ticker)
    if not os.path.exists(path):
        return None
    mids = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                mids.append(float(row[3]))
    return max(mids) - mids[0] if mids else None

def get_cell_name(cat, side, mid):
    bucket = int(mid / 5) * 5
    return "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)

# Group matches by cell
cell_matches = defaultdict(list)
for r in facts:
    cat = r["category"]
    side = r["side"]
    entry_mid = float(r["entry_mid"])
    max_bounce = float(r["max_bounce_from_entry"])
    result = r["match_result"]
    cell = get_cell_name(cat, side, entry_mid)
    cell_matches[cell].append({
        "ticker": r["ticker_id"], "entry_mid": entry_mid,
        "max_bounce": max_bounce, "result": result,
        "category": cat, "side": side,
    })

# ============================================================
print("=" * 90)
print("CHALLENGE 1: EXIT_CENTS EV OPTIMIZATION")
print("=" * 90)

underdog_cells = [
    "ATP_MAIN_underdog_20-24", "ATP_MAIN_underdog_25-29",
    "ATP_MAIN_underdog_30-34", "ATP_MAIN_underdog_35-39",
    "ATP_MAIN_underdog_40-44",
    "WTA_MAIN_underdog_15-19", "WTA_MAIN_underdog_20-24",
    "WTA_MAIN_underdog_25-29", "WTA_MAIN_underdog_30-34",
    "WTA_MAIN_underdog_35-39", "WTA_MAIN_underdog_40-44",
]

exit_range = list(range(5, 65, 5))

for cell in underdog_cells:
    matches = cell_matches.get(cell, [])
    if len(matches) < 3:
        continue

    current_cfg = config["active_cells"].get(cell, {})
    current_exit = current_cfg.get("exit_cents", 0)
    n = len(matches)
    avg_entry = sum(m["entry_mid"] for m in matches) / n

    print("\n--- %s (N=%d, avg_entry=%.0fc, current_exit=+%dc) ---" % (cell, n, avg_entry, current_exit))
    print("%-8s %5s %7s %7s %10s %10s %s" % (
        "EXIT", "HITS", "HIT%", "EV/TR", "TOT_PNL", "$/DAY@10", "NOTE"))

    best_ev = -999
    best_ev_exit = 0
    best_pnl = -999999
    best_pnl_exit = 0

    for ex in exit_range:
        hits = sum(1 for m in matches if m["max_bounce"] >= ex)
        hit_rate = hits / n
        # EV per trade: P(hit) * exit_cents - P(miss) * entry_mid
        # When exit hits: gain = exit_cents
        # When exit misses: settle at 99.5 (win) or 0.5 (loss)
        # Need to compute actual PnL for misses
        total_pnl = 0
        for m in matches:
            if m["max_bounce"] >= ex:
                total_pnl += ex  # exit hit
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - m["entry_mid"])  # hold to settlement

        ev_per_trade = total_pnl / n
        dpd = total_pnl * CONTRACTS / 100.0 / DAYS

        note = ""
        if ex == current_exit:
            note = " <<<< CURRENT"

        if ev_per_trade > best_ev:
            best_ev = ev_per_trade
            best_ev_exit = ex
        if total_pnl > best_pnl:
            best_pnl = total_pnl
            best_pnl_exit = ex

        print("+%-6dc %4d  %5.0f%% %+6.1fc %+9.0fc  $%+7.2f%s" % (
            ex, hits, 100*hit_rate, ev_per_trade, total_pnl, dpd, note))

    print()
    if best_ev_exit != current_exit or best_pnl_exit != current_exit:
        print("  BEST EV/trade: +%dc (%.1fc/trade)" % (best_ev_exit, best_ev))
        print("  BEST total PNL: +%dc (%.0fc total)" % (best_pnl_exit, best_pnl))
        if best_ev_exit != best_pnl_exit:
            print("  *** EV and PNL disagree: EV prefers +%dc, PNL prefers +%dc" % (best_ev_exit, best_pnl_exit))
        if current_exit != best_ev_exit and current_exit != best_pnl_exit:
            print("  *** CURRENT +%dc is NEITHER EV-optimal NOR PNL-optimal" % current_exit)
        elif current_exit == best_pnl_exit and current_exit != best_ev_exit:
            print("  Current optimizes for TOTAL PNL, not per-trade EV")
        elif current_exit == best_ev_exit:
            print("  Current IS EV-optimal")
    else:
        print("  Current +%dc is optimal on both metrics" % current_exit)

# ============================================================
print("\n\n" + "=" * 90)
print("CHALLENGE 2: LEADER/UNDERDOG MIRROR CONSISTENCY")
print("=" * 90)

disabled_cells = config["disabled_cells"]

# For each disabled leader cell, find the mirror underdog cell
print("\n%-30s %4s %-30s %4s %s" % ("DISABLED LEADER", "N", "MIRROR UNDERDOG", "N", "UNDERDOG STATUS"))

for dc in sorted(disabled_cells):
    if "leader" not in dc:
        continue
    parts = dc.split("_")
    cat = "_".join(parts[:2])
    lo_hi = parts[-1]
    lo = int(lo_hi.split("-")[0])
    hi = int(lo_hi.split("-")[1])

    # Mirror: leader 65-69 -> underdog 30-34 (100 - 69 = 31, 100 - 65 = 35)
    u_lo = 100 - hi - 1
    u_hi = 100 - lo - 1
    # Snap to 5c buckets
    u_bucket_lo = int(u_lo / 5) * 5
    u_bucket_hi = u_bucket_lo + 4
    mirror_cell = "%s_underdog_%d-%d" % (cat, u_bucket_lo, u_bucket_hi)

    leader_n = len(cell_matches.get(dc, []))
    mirror_n = len(cell_matches.get(mirror_cell, []))
    mirror_cfg = config["active_cells"].get(mirror_cell)
    mirror_status = "ACTIVE +%dc" % mirror_cfg["exit_cents"] if mirror_cfg else "NOT CONFIGURED"

    print("%-30s %4d %-30s %4d %s" % (dc, leader_n, mirror_cell, mirror_n, mirror_status))

# Now scan disabled leader cells for any profitable exit
print("\n" + "-" * 90)
print("SCANNING DISABLED LEADER CELLS FOR PROFITABLE EXITS")
print("-" * 90)

for dc in sorted(disabled_cells):
    if "leader" not in dc:
        continue
    matches = cell_matches.get(dc, [])
    if len(matches) < 3:
        print("\n%s: N=%d (too few, skip)" % (dc, len(matches)))
        continue

    n = len(matches)
    avg_entry = sum(m["entry_mid"] for m in matches) / n
    win_rate = sum(1 for m in matches if m["result"] == "win") / n

    print("\n%s: N=%d, avg_entry=%.0fc, win_rate=%.0f%%" % (dc, n, avg_entry, 100*win_rate))
    print("%-8s %5s %7s %10s %10s" % ("EXIT", "HITS", "HIT%", "TOT_PNL", "$/DAY@10"))

    any_positive = False
    best_dpd = -999
    best_exit = 0

    for ex in range(5, 45, 5):
        total_pnl = 0
        hits = 0
        for m in matches:
            if m["max_bounce"] >= ex:
                total_pnl += ex
                hits += 1
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - m["entry_mid"])

        hit_rate = hits / n
        dpd = total_pnl * CONTRACTS / 100.0 / DAYS

        if dpd > best_dpd:
            best_dpd = dpd
            best_exit = ex
        if dpd > 0:
            any_positive = True

        print("+%-6dc %4d  %5.0f%% %+9.0fc  $%+7.2f%s" % (
            ex, hits, 100*hit_rate, total_pnl, dpd,
            " <<<" if dpd > 0 else ""))

    if any_positive:
        print("  >>> CANDIDATE FOR RE-ACTIVATION at +%dc ($%.2f/day)" % (best_exit, best_dpd))
    else:
        print("  No profitable exit found. Stay disabled.")

# Summary
print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)
print("\nChallenge 1: Are current exits EV-optimal?")
suboptimal = []
for cell in underdog_cells:
    matches = cell_matches.get(cell, [])
    if len(matches) < 3:
        continue
    current_exit = config["active_cells"].get(cell, {}).get("exit_cents", 0)
    if current_exit == 0:
        continue
    n = len(matches)
    # Find best EV exit
    best_ev = -999
    best_exit = 0
    for ex in exit_range:
        total_pnl = 0
        for m in matches:
            if m["max_bounce"] >= ex:
                total_pnl += ex
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - m["entry_mid"])
        ev = total_pnl / n
        if ev > best_ev:
            best_ev = ev
            best_exit = ex
    if best_exit != current_exit:
        current_ev_total = 0
        for m in matches:
            if m["max_bounce"] >= current_exit:
                current_ev_total += current_exit
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                current_ev_total += (settle - m["entry_mid"])
        current_ev = current_ev_total / n
        delta = best_ev - current_ev
        suboptimal.append((cell, current_exit, best_exit, current_ev, best_ev, delta, n))

if suboptimal:
    print("\nSuboptimal cells (current != EV-best):")
    print("%-35s %6s %6s %8s %8s %8s %4s" % ("CELL", "CUR", "BEST", "CUR_EV", "BEST_EV", "DELTA", "N"))
    for cell, cur, best, cur_ev, best_ev, delta, n in sorted(suboptimal, key=lambda x: -x[5]):
        print("%-35s +%3dc +%3dc %+7.1fc %+7.1fc %+7.1fc %4d" % (
            cell, cur, best, cur_ev, best_ev, delta, n))
else:
    print("All cells are EV-optimal at current exits.")

print("\nDONE")
