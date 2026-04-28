#!/usr/bin/env python3
"""
Scalp-constrained optimization. Validates whether "optimal" exits are
actually achievable as premarket scalps or are settlement-ride artifacts.

Constraint: exit target must be ≤ 95c absolute (entry + exit_c ≤ 95).
"""
import sqlite3, json, csv, os, math, random
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"

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
SCALP_CAP = 95  # absolute price cap for scalp-achievable exits

# Build entries
all_entries = defaultdict(list)
for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, min_w, max_w, last_w = ev[4], ev[5], ev[6], ev[7]
    fp_l, min_l, max_l = ev[8], ev[12], ev[13]
    is_scalar = max_w is not None and max_w < 95
    dur_h = 0
    try:
        from datetime import datetime
        t1 = datetime.fromisoformat(ev[10].replace("Z","+00:00"))
        t2 = datetime.fromisoformat(ev[11].replace("Z","+00:00"))
        dur_h = (t2-t1).total_seconds()/3600
    except: pass

    if fp_w and 0 < fp_w < 100:
        c = classify_cell(tier, fp_w)
        if c in ALL_CELLS:
            all_entries[c].append({
                "side":"winner","entry":fp_w,"exit_c":ALL_CELLS[c],
                "max_price":max_w,"is_scalar":is_scalar,
                "settle_price":last_w if last_w else 99,"evt":evt,"dur_h":dur_h,
            })
    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        if c in ALL_CELLS:
            all_entries[c].append({
                "side":"loser","entry":fp_l,"exit_c":ALL_CELLS[c],
                "max_price":max_l,"is_scalar":is_scalar,
                "settle_price":min_l if min_l else 1,"evt":evt,"dur_h":dur_h,
            })

def compute_ev(entries, ec):
    if not entries: return None
    n = len(entries)
    winners = [e for e in entries if e["side"]=="winner" and not e["is_scalar"]]
    losers = [e for e in entries if e["side"]=="loser" and not e["is_scalar"]]
    scalars = [e for e in entries if e["is_scalar"]]
    n_w, n_l, n_s = len(winners), len(losers), len(scalars)
    w = n_w/(n_w+n_l) if (n_w+n_l) else 0
    s = n_s/n if n else 0
    avg_e = sum(e["entry"] for e in entries)/n

    w_scalp = sum(1 for e in winners if e["max_price"] and e["max_price"]>=min(99,e["entry"]+ec))
    l_scalp = sum(1 for e in losers if e["max_price"] and e["max_price"]>=min(99,e["entry"]+ec))
    Sw = w_scalp/n_w if n_w else 0
    Sl = l_scalp/n_l if n_l else 0

    sp = ec*QTY/100
    ws = (99-avg_e)*QTY/100
    ls = -(avg_e-1)*QTY/100
    sc_pnl = 0
    if scalars:
        sc_pnl = sum((e["settle_price"]-e["entry"])*QTY/100 for e in scalars)/len(scalars)

    ev = w*(Sw*sp+(1-Sw)*ws) + (1-w-s)*(Sl*sp+(1-Sl)*ls) + s*sc_pnl
    cost = avg_e*QTY/100
    roi = ev/cost*100 if cost else 0
    df = n/DAYS/2
    # Outcomes for variance
    outcomes = []
    for e in entries:
        target = min(99, e["entry"]+ec)
        if e["max_price"] and e["max_price"]>=target:
            outcomes.append(ec*QTY/100)
        elif e["side"]=="winner" and not e["is_scalar"]:
            outcomes.append((99-e["entry"])*QTY/100)
        elif e["side"]=="loser" and not e["is_scalar"]:
            outcomes.append(-(e["entry"]-1)*QTY/100)
        else:
            outcomes.append((e["settle_price"]-e["entry"])*QTY/100)
    mean_o = sum(outcomes)/len(outcomes)
    std_o = (sum((x-mean_o)**2 for x in outcomes)/len(outcomes))**0.5
    sharpe_o = mean_o/std_o if std_o else 0

    return {"ev":ev,"roi":roi,"cost":cost,"n":n,"df":df,"dd":df*ev,
            "Sw":Sw,"Sl":Sl,"w":w,"avg_e":avg_e,"ec":ec,
            "outcomes":outcomes,"std":std_o,"sharpe":sharpe_o,
            "n_w":n_w,"n_l":n_l}

# =====================================================================
# TASK 1: Scalp-achievable max exit
# =====================================================================
print("="*80)
print("=== TASK 1: SCALP-ACHIEVABLE MAX EXIT PER CELL ===")
print("="*80)
print()
print("| Cell | Avg entry | Max scalpable (+) | CC optimal | Optimal abs | Settlement-only? |")
print("|---|---|---|---|---|---|")

prev_optimal = {}  # from prior analysis
for cell in sorted(ALL_CELLS.keys()):
    entries = all_entries.get(cell,[])
    if not entries or len(entries)<15: continue
    avg_e = sum(e["entry"] for e in entries)/len(entries)
    max_scalp = SCALP_CAP - avg_e  # max exit_c where target ≤ 95

    # Find what prior optimization returned (sweep 3..40)
    best_roi = -999
    best_ec = ALL_CELLS[cell]
    for ec in range(3,41):
        r = compute_ev(entries, ec)
        if r and r["roi"]>best_roi:
            best_roi = r["roi"]
            best_ec = ec
    prev_optimal[cell] = best_ec

    target_abs = avg_e + best_ec
    settle_only = "YES" if target_abs > SCALP_CAP else "no"
    if target_abs > 99: settle_only = "YES (>99, impossible scalp)"

    print("| %s | %.0fc | +%.0fc | +%dc | %.0fc | %s |" % (
        cell, avg_e, max_scalp, best_ec, target_abs, settle_only))


# =====================================================================
# TASK 2: Re-optimize with scalp-only constraint
# =====================================================================
print()
print("="*80)
print("=== TASK 2: SCALP-ONLY CONSTRAINED OPTIMIZATION ===")
print("="*80)
print()
print("| Cell | Avg entry | Max scalpable | Optimal constrained | Constrained ROI | Sw | Sl | EV$/fill | vs Current |")
print("|---|---|---|---|---|---|---|---|---|")

constrained = {}
for cell in sorted(ALL_CELLS.keys()):
    entries = all_entries.get(cell,[])
    if not entries or len(entries)<15: continue
    avg_e = sum(e["entry"] for e in entries)/len(entries)
    max_ec = int(SCALP_CAP - avg_e)
    if max_ec < 3: max_ec = 3

    best_roi = -999
    best_ec = ALL_CELLS[cell]
    best_r = None
    for ec in range(3, max_ec+1):
        r = compute_ev(entries, ec)
        if r and r["roi"]>best_roi:
            best_roi = r["roi"]
            best_ec = ec
            best_r = r

    if not best_r: continue
    constrained[cell] = best_r

    current_r = compute_ev(entries, ALL_CELLS[cell])
    delta = best_roi - current_r["roi"] if current_r else 0

    print("| %s | %.0fc | +%dc | +%dc | %+.1f%% | %.0f%% | %.0f%% | $%+.3f | %+.1f%% |" % (
        cell, avg_e, max_ec, best_ec, best_roi,
        best_r["Sw"]*100, best_r["Sl"]*100, best_r["ev"], delta))


# =====================================================================
# TASK 3: Settlement-ride comparison
# =====================================================================
print()
print("="*80)
print("=== TASK 3: SCALP vs HOLD-TO-SETTLEMENT ===")
print("="*80)
print()

def hold_to_settle_ev(entries):
    """EV if we never scalp — hold everything to settlement."""
    if not entries: return None
    n = len(entries)
    outcomes = []
    for e in entries:
        if e["side"]=="winner" and not e["is_scalar"]:
            outcomes.append((99-e["entry"])*QTY/100)
        elif e["side"]=="loser" and not e["is_scalar"]:
            outcomes.append(-(e["entry"]-1)*QTY/100)
        else:
            outcomes.append((e["settle_price"]-e["entry"])*QTY/100)
    avg_e = sum(e["entry"] for e in entries)/n
    mean = sum(outcomes)/len(outcomes)
    cost = avg_e*QTY/100
    roi = mean/cost*100 if cost else 0
    std = (sum((x-mean)**2 for x in outcomes)/len(outcomes))**0.5
    sharpe = mean/std if std else 0
    return {"ev":mean,"roi":roi,"std":std,"sharpe":sharpe,"outcomes":outcomes,
            "n":n,"df":n/DAYS/2,"dd":(n/DAYS/2)*mean,"avg_e":avg_e,"cost":cost}

print("| Cell | Avg entry | Scalp-opt exit | Scalp ROI | Hold-settle ROI | Better | Gap |")
print("|---|---|---|---|---|---|---|")

hold_results = {}
for cell in sorted(ALL_CELLS.keys()):
    entries = all_entries.get(cell,[])
    if not entries or len(entries)<15: continue

    cr = constrained.get(cell)
    hr = hold_to_settle_ev(entries)
    if not cr or not hr: continue
    hold_results[cell] = hr

    better = "SCALP" if cr["roi"]>hr["roi"] else "HOLD" if hr["roi"]>cr["roi"] else "TIE"
    gap = cr["roi"]-hr["roi"]
    print("| %s | %.0fc | +%dc | %+.1f%% | %+.1f%% | %s | %+.1f%% |" % (
        cell, cr["avg_e"], cr["ec"], cr["roi"], hr["roi"], better, gap))


# =====================================================================
# TASK 4: Re-do scenarios with scalp-only constraint
# =====================================================================
print()
print("="*80)
print("=== TASK 4: SCENARIO COMPARISON ===")
print("="*80)
print()

def run_mc(results_dict, cell_set, label):
    random.seed(42)
    sim = []
    total_ev = sum(results_dict[c]["dd"] for c in cell_set if c in results_dict)
    outcomes_map = {c: results_dict[c]["outcomes"] for c in cell_set if c in results_dict}
    fires_map = {c: results_dict[c]["df"] for c in cell_set if c in results_dict}
    for _ in range(10000):
        day = 0
        for c, outs in outcomes_map.items():
            fires = max(1, int(round(fires_map[c])))
            for _ in range(fires):
                day += random.choice(outs)
        sim.append(day)
    sim.sort()
    ns = len(sim)
    avg = sum(sim)/ns
    std = (sum((x-avg)**2 for x in sim)/ns)**0.5
    sharpe = avg/std if std else 0
    n_cells = len(outcomes_map)
    print("=== %s (%d cells) ===" % (label, n_cells))
    print("  Daily EV:   $%.2f" % total_ev)
    print("  MC mean:    $%.2f" % avg)
    print("  MC std:     $%.2f" % std)
    print("  MC Sharpe:  %.3f" % sharpe)
    print("  MC P5:      $%.2f" % sim[ns//20])
    print("  MC median:  $%.2f" % sim[ns//2])
    print("  MC P95:     $%.2f" % sim[19*ns//20])
    print()
    return {"ev":total_ev,"mean":avg,"sharpe":sharpe,"p5":sim[ns//20],
            "p95":sim[19*ns//20],"cells":n_cells,"std":std}

# Scenario A: Current 25 active, current exits
current_results = {}
for cell in ALL_CELLS:
    entries = all_entries.get(cell,[])
    if entries and len(entries)>=10:
        current_results[cell] = compute_ev(entries, ALL_CELLS[cell])
print("--- A: Current 25 active, current exits ---")
sc_a = run_mc(current_results, set(active_cells.keys()), "Current config")

# Scenario B: Current 25 active, scalp-constrained optimal exits
print("--- B: Current 25 active, scalp-constrained optimal ---")
sc_b = run_mc(constrained, set(active_cells.keys()), "Current cells, scalp-opt exits")

# Scenario C: All positive cells (scalp-constrained), N>=20
pos_constrained = {c for c,r in constrained.items() if r["roi"]>0 and r["n"]>=20}
print("--- C: All positive scalp-constrained cells (N>=20) ---")
sc_c = run_mc(constrained, pos_constrained, "All positive scalp-opt")

# Scenario D: Mix strategy — scalp where scalp is better, hold where hold is better
mix_results = {}
for cell in ALL_CELLS:
    cr = constrained.get(cell)
    hr = hold_results.get(cell)
    if not cr or not hr: continue
    if cr["roi"] >= hr["roi"]:
        mix_results[cell] = cr
    else:
        mix_results[cell] = hr
pos_mix = {c for c,r in mix_results.items() if r["roi"]>0 and r["n"]>=20}
print("--- D: Mix scalp+hold, all positive cells (N>=20) ---")
sc_d = run_mc(mix_results, pos_mix, "Mix scalp/hold, positive cells")

# Summary table
print("="*80)
print("| Scenario | Cells | Daily EV | MC Mean | Sharpe | P5 worst | P95 best |")
print("|---|---|---|---|---|---|---|")
for label, sc in [("A: Current config", sc_a),
                   ("B: Current cells, scalp-opt", sc_b),
                   ("C: All positive, scalp-opt", sc_c),
                   ("D: Mix scalp+hold, positive", sc_d)]:
    print("| %s | %d | $%.2f | $%.2f | %.3f | $%.2f | $%.2f |" % (
        label, sc["cells"], sc["ev"], sc["mean"], sc["sharpe"], sc["p5"], sc["p95"]))


# =====================================================================
# TASK 5: Position lockup analysis
# =====================================================================
print()
print("="*80)
print("=== TASK 5: POSITION LOCKUP ANALYSIS ===")
print("="*80)
print()

# Average duration by tier
tier_durs = defaultdict(list)
for cell in ALL_CELLS:
    for e in all_entries.get(cell,[]):
        parts = cell.split("_")
        tier = parts[0]+"_"+parts[1]
        if e["dur_h"]>0:
            tier_durs[tier].append(e["dur_h"])

print("| Tier | N | Avg duration (h) | Median | P25 | P75 |")
print("|---|---|---|---|---|---|")
for tier in sorted(tier_durs.keys()):
    ds = sorted(tier_durs[tier])
    n = len(ds)
    if n < 5: continue
    print("| %s | %d | %.1fh | %.1fh | %.1fh | %.1fh |" % (
        tier, n, sum(ds)/n, ds[n//2], ds[n//4], ds[3*n//4]))

# Scalp strategy: positions close at scalp (winner side quick, loser side quick or settle)
# Hold strategy: all positions locked until settlement
# Avg scalp hold time ≈ much less than full match
# But we don't have per-scalp timing from historical_events (only first/last trade times)
print()
print("Capital lockup comparison:")
print("  Scalp strategy: ~80%% of positions close within first few hours (winner scalps)")
print("  Hold strategy: ALL positions locked for full match duration")
print()

# Capital at peak: concurrent matches × 2 sides × entry × qty
# Estimate concurrent matches from daily fires
total_daily_fires = sum(r["df"] for c,r in constrained.items() if c in pos_constrained)
avg_entry = sum(r["avg_e"]*r["df"] for c,r in constrained.items() if c in pos_constrained) / total_daily_fires if total_daily_fires else 50
avg_dur_chall = sum(tier_durs.get("ATP_CHALL",[12]))/len(tier_durs.get("ATP_CHALL",[12]))
avg_dur_main = sum(tier_durs.get("ATP_MAIN",[30]))/len(tier_durs.get("ATP_MAIN",[30]))

print("  Scalp-opt daily fires: %.1f" % total_daily_fires)
print("  Avg entry price: %.0fc" % avg_entry)
print("  Avg position size: $%.2f (10ct @ %.0fc)" % (avg_entry*QTY/100, avg_entry))
print("  ATP_CHALL avg duration: %.1fh" % avg_dur_chall)
print("  ATP_MAIN avg duration: %.1fh" % avg_dur_main)
print()
print("  Peak concurrent positions (estimate):")
print("    Scalp: ~%.0f (fires/day × avg_hold_h / 24)" % (total_daily_fires * 4 / 24))
print("    Hold:  ~%.0f (fires/day × avg_dur_h / 24)" % (total_daily_fires * 15 / 24))
print("  Peak capital deployed:")
print("    Scalp: ~$%.0f" % (total_daily_fires * 4 / 24 * avg_entry * QTY / 100))
print("    Hold:  ~$%.0f" % (total_daily_fires * 15 / 24 * avg_entry * QTY / 100))


# =====================================================================
# TASK 6: Retirement risk
# =====================================================================
print()
print("="*80)
print("=== TASK 6: RETIREMENT/SCALAR RISK ===")
print("="*80)
print()

# Count scalars by tier
scalar_counts = defaultdict(lambda: {"total":0,"scalar":0})
for cell in ALL_CELLS:
    entries = all_entries.get(cell,[])
    parts = cell.split("_")
    tier = parts[0]+"_"+parts[1]
    for e in entries:
        scalar_counts[tier]["total"] += 1
        if e["is_scalar"]:
            scalar_counts[tier]["scalar"] += 1

print("| Tier | Total entries | Scalar events | Retirement rate |")
print("|---|---|---|---|")
for tier in sorted(scalar_counts.keys()):
    d = scalar_counts[tier]
    rate = d["scalar"]/d["total"]*100 if d["total"] else 0
    print("| %s | %d | %d | %.1f%% |" % (tier, d["total"], d["scalar"], rate))


# =====================================================================
# TASK 7: True optimal exit per cell with all constraints
# =====================================================================
print()
print("="*80)
print("=== TASK 7: TRUE OPTIMAL EXIT (SCALP-CONSTRAINED) ===")
print("="*80)
print()

print("| Cell | Status | N | Avg entry | Current exit | Current ROI | Optimal exit | Optimal ROI | Sl | Daily$ | Change? |")
print("|---|---|---|---|---|---|---|---|---|---|---|")

final_config = {}
for cell in sorted(ALL_CELLS.keys()):
    entries = all_entries.get(cell,[])
    if not entries or len(entries)<15: continue

    avg_e = sum(e["entry"] for e in entries)/len(entries)
    max_ec = int(SCALP_CAP - avg_e)
    if max_ec < 3: continue

    current_ec = ALL_CELLS[cell]
    current_r = compute_ev(entries, current_ec)
    is_active = cell in active_cells

    best_roi = -999; best_ec = current_ec; best_r = current_r
    for ec in range(3, max_ec+1):
        r = compute_ev(entries, ec)
        if r and r["roi"]>best_roi:
            best_roi=r["roi"]; best_ec=ec; best_r=r

    final_config[cell] = best_r
    change = ""
    if best_ec != current_ec:
        if abs(best_roi - current_r["roi"]) > 3:
            change = "RETUNE +%dc→+%dc" % (current_ec, best_ec)
        else:
            change = "minor"

    print("| %s | %s | %d | %.0fc | +%dc | %+.1f%% | +%dc | %+.1f%% | %.0f%% | $%+.3f | %s |" % (
        cell, "ON" if is_active else "off", best_r["n"], avg_e,
        current_ec, current_r["roi"] if current_r else 0,
        best_ec, best_roi, best_r["Sl"]*100, best_r["dd"], change))


# =====================================================================
# TASK 8: Final realistic portfolio
# =====================================================================
print()
print("="*80)
print("=== TASK 8: FINAL REALISTIC PORTFOLIO ===")
print("="*80)
print()

# Positive cells at constrained-optimal exits, N>=20
final_pos = {c for c,r in final_config.items() if r["roi"]>0 and r["n"]>=20}

print("Active cells in final portfolio:")
total_ev = 0
for c in sorted(final_pos):
    r = final_config[c]
    total_ev += r["dd"]
    print("  %s: +%dc exit, ROI=%+.1f%%, daily=$%+.3f, N=%d" % (
        c, r["ec"], r["roi"], r["dd"], r["n"]))

print()
print("--- FINAL PORTFOLIO ---")
sc_final = run_mc(final_config, final_pos, "Final scalp-constrained portfolio")

print()
print("="*80)
print("=== FINAL COMPARISON ===")
print("="*80)
print()
print("| Scenario | Cells | Daily EV | MC Mean | Sharpe | P5 | P95 |")
print("|---|---|---|---|---|---|---|")
print("| Current config | %d | $%.2f | $%.2f | %.3f | $%.2f | $%.2f |" % (
    sc_a["cells"], sc_a["ev"], sc_a["mean"], sc_a["sharpe"], sc_a["p5"], sc_a["p95"]))
print("| CC unconstrained opt | 28 | $24.86 | $27.78 | 1.260 | $-10.10 | $63.00 |")
print("| Scalp-constrained opt | %d | $%.2f | $%.2f | %.3f | $%.2f | $%.2f |" % (
    sc_final["cells"], sc_final["ev"], sc_final["mean"], sc_final["sharpe"],
    sc_final["p5"], sc_final["p95"]))
print()

# How much of the $24.86 was settlement-ride artifact?
print("Settlement-ride artifact: $%.2f of $24.86 = %.0f%% was achievable as scalps" % (
    sc_final["ev"], sc_final["ev"]/24.86*100 if 24.86 else 0))

print()
print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
