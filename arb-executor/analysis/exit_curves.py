#!/usr/bin/env python3
"""Full 1c-granularity exit curves with bounce vs settlement classification."""
import csv, os
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
DAYS = 28; CT = 10

facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (r["category"], r["side"], bucket, bucket + 4)
        facts_by_cell[cell].append({
            "ticker": r["ticker_id"], "entry_mid": entry,
            "max_bounce": float(r["max_bounce_from_entry"]),
            "result": r["match_result"],
        })

def load_ticks(ticker):
    path = os.path.join(TICKS_DIR, "%s.csv" % ticker)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                rows.append((int(row[0]), float(row[3])))
    return rows

# Pre-load ticks for target cells
target_cells = [
    "ATP_CHALL_underdog_40-44",
    "ATP_MAIN_underdog_35-39",
    "WTA_MAIN_underdog_35-39",
    "WTA_MAIN_underdog_40-44",
    "ATP_MAIN_leader_60-64",
    "ATP_CHALL_leader_65-69",
]

cell_ticks = {}
for cell in target_cells:
    cell_ticks[cell] = []
    for m in facts_by_cell.get(cell, []):
        ticks = load_ticks(m["ticker"])
        if ticks:
            cell_ticks[cell].append((m, ticks))
    print("Loaded %s: %d/%d matches with ticks" % (cell, len(cell_ticks[cell]), len(facts_by_cell.get(cell, []))))

def classify_hit(ticks, entry, exit_cents):
    """Returns (hit, category) where category is 'A:bounce' or 'B:settle' or None."""
    target = entry + exit_cents
    n = len(ticks)
    hit_idx = None
    for i, (ts, mid) in enumerate(ticks):
        if mid >= target:
            hit_idx = i
            break
    if hit_idx is None:
        return False, None
    position_pct = hit_idx / n
    remaining = ticks[hit_idx:]
    min_after = min(mid for _, mid in remaining)
    retreat = ticks[hit_idx][1] - min_after
    if position_pct > 0.90 and retreat < 5:
        return True, "B"
    elif retreat > 5:
        return True, "A"
    elif position_pct > 0.85:
        return True, "B"
    else:
        return True, "A"

def scan_cell(cell_name, current_exit, lo=10, hi=51):
    matches_ticks = cell_ticks.get(cell_name, [])
    n = len(matches_ticks)
    if n == 0:
        return
    avg_entry = sum(m["entry_mid"] for m, _ in matches_ticks) / n

    print("\n" + "=" * 95)
    print("%s (N=%d, avg_entry=%.0fc, current=+%dc)" % (cell_name, n, avg_entry, current_exit))
    print("=" * 95)
    print("%-5s %5s %7s %7s %7s %7s %7s %s" % (
        "EXIT", "HIT%", "GEN%", "SET%", "EV_c", "$/DAY", "MISS$", "NOTES"))
    print("-" * 95)

    best_dpd = -999
    best_exit = 0
    plateau_start = None
    plateau_end = None
    prev_dpd = None
    results = []

    for ex in range(lo, hi):
        hits_a = 0; hits_b = 0; total_pnl = 0
        for m, ticks in matches_ticks:
            entry = m["entry_mid"]
            hit, cat = classify_hit(ticks, entry, ex)
            if hit:
                total_pnl += ex * CT
                if cat == "A":
                    hits_a += 1
                else:
                    hits_b += 1
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - entry) * CT

        total_hits = hits_a + hits_b
        hit_rate = total_hits / n
        gen_pct = hits_a / total_hits if total_hits else 0
        set_pct = hits_b / total_hits if total_hits else 0
        ev_cents = total_pnl / n / CT
        dpd = ev_cents * CT / 100.0 * n / DAYS

        # Miss P&L
        miss_count = n - total_hits
        miss_pnl = 0
        if miss_count > 0:
            for m, ticks in matches_ticks:
                hit, _ = classify_hit(ticks, m["entry_mid"], ex)
                if not hit:
                    settle = 99.5 if m["result"] == "win" else 0.5
                    miss_pnl += (settle - m["entry_mid"]) * CT / 100.0
            miss_avg = miss_pnl / miss_count
        else:
            miss_avg = 0

        notes = ""
        if ex == current_exit:
            notes = " <<<CURRENT"
        if dpd > best_dpd:
            best_dpd = dpd
            best_exit = ex

        results.append((ex, hit_rate, gen_pct, set_pct, ev_cents, dpd, miss_avg))

        print("+%3dc %4.0f%% %5.0f%%A %5.0f%%B %+5.1fc $%+5.2f $%+5.2f%s" % (
            ex, 100*hit_rate, 100*gen_pct, 100*set_pct, ev_cents, dpd, miss_avg, notes))

    # Find cliff and plateau
    print()
    print("  GLOBAL OPTIMUM: +%dc at $%.2f/day" % (best_exit, best_dpd))

    # Plateau detection: exits within $0.10 of peak
    plateau = [r for r in results if r[5] >= best_dpd - 0.10]
    if len(plateau) > 3:
        print("  PLATEAU: +%dc to +%dc (all within $0.10 of peak)" % (
            plateau[0][0], plateau[-1][0]))
        print("  Width: %dc — ROBUST pick" % (plateau[-1][0] - plateau[0][0]))
    else:
        print("  NO PLATEAU — peak is narrow/fragile")

    # Cliff detection: biggest single-step drop in hit rate
    max_cliff = 0; cliff_at = 0
    for i in range(1, len(results)):
        drop = results[i-1][1] - results[i][1]
        if drop > max_cliff:
            max_cliff = drop
            cliff_at = results[i][0]
    if max_cliff > 0.05:
        print("  CLIFF: hit rate drops %.0f%% at +%dc" % (100*max_cliff, cliff_at))

    # Local maxima
    local_max = []
    for i in range(1, len(results)-1):
        if results[i][5] > results[i-1][5] and results[i][5] > results[i+1][5]:
            if results[i][5] > 0:
                local_max.append((results[i][0], results[i][5]))
    if len(local_max) > 1:
        print("  LOCAL MAXIMA: %s" % ", ".join("+%dc($%.2f)" % (e, d) for e, d in local_max))

for cell, current in [
    ("ATP_CHALL_underdog_40-44", 45),
    ("ATP_MAIN_underdog_35-39", 31),
    ("WTA_MAIN_underdog_35-39", 27),
    ("WTA_MAIN_underdog_40-44", 49),
    ("ATP_MAIN_leader_60-64", 35),
    ("ATP_CHALL_leader_65-69", 24),
]:
    scan_cell(cell, current)

print("\nDONE")
