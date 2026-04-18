#!/usr/bin/env python3
"""
Multi-strategy backtest: single-exit vs tight-exit vs scalp re-entry.
Uses full tick data from match_ticks_full/.
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

facts = []
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        facts.append(r)

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

def get_cell_name(cat, side, mid):
    bucket = int(mid / 5) * 5
    return "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)

def sim_strategy_a(ticks, entry_mid, result, exit_cents):
    """Single entry, EV-optimal exit, hold to settlement if not hit."""
    target = entry_mid + exit_cents
    for ts, mid in ticks:
        if mid >= target:
            return exit_cents
    settle = 99.5 if result == "win" else 0.5
    return settle - entry_mid

def sim_strategy_b(ticks, entry_mid, result, exit_cents):
    """Single entry, tight exit, hold to settlement if not hit."""
    return sim_strategy_a(ticks, entry_mid, result, exit_cents)

def sim_strategy_c(ticks, entry_mid, result, exit_cents, max_entries=3, cooldown_sec=300):
    """Tight exit + re-entry on dip. Max N entries, cooldown between."""
    total_pnl = 0
    entries = 0
    in_position = True
    current_entry = entry_mid
    target = current_entry + exit_cents
    last_exit_ts = -cooldown_sec
    last_exit_idx = 0

    for i, (ts, mid) in enumerate(ticks):
        if in_position:
            if mid >= target:
                total_pnl += exit_cents
                in_position = False
                entries += 1
                last_exit_ts = ts
                last_exit_idx = i
                if entries >= max_entries:
                    break
        else:
            if ts - last_exit_ts >= cooldown_sec and abs(mid - entry_mid) <= 2 and 1 < mid < 99:
                current_entry = mid
                target = current_entry + exit_cents
                in_position = True

    if in_position:
        settle = 99.5 if result == "win" else 0.5
        total_pnl += settle - current_entry

    return total_pnl, max(entries, 1)

# Group matches by cell
cell_matches = defaultdict(list)
for r in facts:
    cat = r["category"]
    side = r["side"]
    entry_mid = float(r["entry_mid"])
    cell = get_cell_name(cat, side, entry_mid)
    cell_matches[cell].append(r)

# Underdog cells to test
underdog_cells = sorted([c for c in config["active_cells"] if "underdog" in c])

print("=" * 100)
print("MULTI-STRATEGY BACKTEST")
print("=" * 100)

for cell in underdog_cells:
    matches = cell_matches.get(cell, [])
    if len(matches) < 5:
        continue

    cell_cfg = config["active_cells"].get(cell, {})
    ev_exit = cell_cfg.get("exit_cents", 0)
    if ev_exit == 0:
        continue

    n = len(matches)
    avg_entry = sum(float(m["entry_mid"]) for m in matches) / n

    # Load all ticks
    match_ticks = []
    for m in matches:
        ticks = load_ticks(m["ticker_id"])
        if ticks:
            match_ticks.append((m, ticks))
    if not match_ticks:
        continue

    n_loaded = len(match_ticks)

    print("\n--- %s (N=%d loaded, avg_entry=%.0fc, EV-exit=+%dc) ---" % (cell, n_loaded, avg_entry, ev_exit))

    # Strategy A: single entry, EV-optimal exit
    a_pnls = []
    for m, ticks in match_ticks:
        pnl = sim_strategy_a(ticks, float(m["entry_mid"]), m["match_result"], ev_exit)
        a_pnls.append(pnl)

    # Strategy B: tight exits at +8, +10, +12
    b_results = {}
    for tight in [8, 10, 12]:
        pnls = []
        for m, ticks in match_ticks:
            pnl = sim_strategy_b(ticks, float(m["entry_mid"]), m["match_result"], tight)
            pnls.append(pnl)
        b_results[tight] = pnls

    # Strategy C: tight exit + re-entry at +10c
    c_pnls = []
    c_trades = []
    for m, ticks in match_ticks:
        pnl, trades = sim_strategy_c(ticks, float(m["entry_mid"]), m["match_result"], 10, max_entries=3, cooldown_sec=300)
        c_pnls.append(pnl)
        c_trades.append(trades)

    # Strategy D: both-sides scalp (only for 40-60c cells)
    d_applicable = 40 <= avg_entry <= 60
    d_pnls = []
    d_trades = []
    if d_applicable:
        for m, ticks in match_ticks:
            entry = float(m["entry_mid"])
            other_entry = 100 - entry
            pnl1, tr1 = sim_strategy_c(ticks, entry, m["match_result"], 10, max_entries=3, cooldown_sec=300)
            # Flip ticks for other side: other_mid = 100 - mid
            other_ticks = [(ts, 100 - mid) for ts, mid in ticks]
            other_result = "loss" if m["match_result"] == "win" else "win"
            pnl2, tr2 = sim_strategy_c(other_ticks, other_entry, other_result, 10, max_entries=3, cooldown_sec=300)
            d_pnls.append(pnl1 + pnl2)
            d_trades.append(tr1 + tr2)

    def report(label, pnls, trades_list=None):
        n = len(pnls)
        total = sum(pnls)
        ev = total / n
        dpd = total * CONTRACTS / 100.0 / DAYS
        wins = sum(1 for p in pnls if p > 0)
        wr = 100 * wins / n
        variance = sum((p - ev)**2 for p in pnls) / n
        std = math.sqrt(variance)
        avg_trades = sum(trades_list) / n if trades_list else 1.0
        print("  %-22s EV=%+6.1fc  $/d@10=$%+6.2f  WR=%4.0f%%  std=%.0fc  tr/match=%.1f" % (
            label, ev, dpd, wr, std, avg_trades))

    report("A: EV-opt +%dc" % ev_exit, a_pnls)
    for tight in [8, 10, 12]:
        report("B: tight +%dc" % tight, b_results[tight])
    report("C: scalp +10c (re-entry)", c_pnls, c_trades)
    if d_applicable:
        report("D: both-sides +10c", d_pnls, d_trades)

    # Count oscillations
    osc_counts = []
    for m, ticks in match_ticks:
        entry = float(m["entry_mid"])
        crossings = 0
        above = ticks[0][1] > entry + 10 if ticks else False
        for ts, mid in ticks:
            now_above = mid > entry + 10
            if now_above != above:
                crossings += 1
                above = now_above
        osc_counts.append(crossings)
    avg_osc = sum(osc_counts) / len(osc_counts)
    print("  Oscillations (crosses entry+10c): avg=%.1f  max=%d" % (avg_osc, max(osc_counts)))

# Summary: which cells benefit most from Strategy C
print("\n" + "=" * 100)
print("STRATEGY C UPLIFT SUMMARY (scalp +10c re-entry vs EV-optimal single-exit)")
print("=" * 100)
print("%-35s %8s %8s %8s %s" % ("CELL", "A $/d", "C $/d", "UPLIFT", "VERDICT"))

for cell in underdog_cells:
    matches = cell_matches.get(cell, [])
    if len(matches) < 5:
        continue
    cell_cfg = config["active_cells"].get(cell, {})
    ev_exit = cell_cfg.get("exit_cents", 0)
    if ev_exit == 0:
        continue

    match_ticks = [(m, load_ticks(m["ticker_id"])) for m in matches]
    match_ticks = [(m, t) for m, t in match_ticks if t]
    if not match_ticks:
        continue

    a_total = sum(sim_strategy_a(t, float(m["entry_mid"]), m["match_result"], ev_exit) for m, t in match_ticks)
    c_total = sum(sim_strategy_c(t, float(m["entry_mid"]), m["match_result"], 10, 3, 300)[0] for m, t in match_ticks)

    a_dpd = a_total * CONTRACTS / 100.0 / DAYS
    c_dpd = c_total * CONTRACTS / 100.0 / DAYS
    uplift = c_dpd - a_dpd
    verdict = "C WINS" if uplift > 0.05 else ("TIE" if abs(uplift) < 0.05 else "A WINS")
    print("%-35s $%+6.2f $%+6.2f $%+6.2f %s" % (cell, a_dpd, c_dpd, uplift, verdict))

print("\nDONE")
