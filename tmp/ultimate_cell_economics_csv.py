#!/usr/bin/env python3
"""
Ultimate Per-Cell Economics — CSV output for all 12 tasks.
Writes individual CSV files per task to tmp/harmonized_analysis/
"""

import sqlite3, json, csv, os, glob, sys, random
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/harmonized_analysis"
os.makedirs(OUT_DIR, exist_ok=True)
ET = timezone(timedelta(hours=-4))

# === LOAD CONFIG ===
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
    direction = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, direction, bs, bs + 4)

cat_to_tier = {"ATP_MAIN": "ATP_MAIN", "ATP_CHALL": "ATP_CHALL",
               "WTA_MAIN": "WTA_MAIN", "WTA_CHALL": "WTA_CHALL"}

# === LOAD HISTORICAL EVENTS ===
conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()
cur.execute("""SELECT event_ticker, category, winner, loser,
    first_price_winner, min_price_winner, max_price_winner,
    first_price_loser, min_price_loser, max_price_loser,
    total_trades, first_ts, last_ts
    FROM historical_events
    WHERE first_ts > '2026-03-20' AND first_ts < '2026-04-18'
    AND total_trades >= 10""")
events = cur.fetchall()
print("Loaded %d historical events" % len(events))

# === BUILD PER-CELL DATA ===
cell_data = defaultdict(lambda: {"entries": []})
DAYS = 28

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, min_w, max_w = ev[4], ev[5], ev[6]
    fp_l, min_l, max_l = ev[7], ev[8], ev[9]
    try:
        t1 = datetime.fromisoformat(ev[11].replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(ev[12].replace("Z", "+00:00"))
        dur_h = (t2 - t1).total_seconds() / 3600
    except:
        dur_h = 0

    if fp_w and 0 < fp_w < 100:
        c = classify_cell(tier, fp_w)
        if c in ALL_CELLS:
            cell_data[c]["entries"].append((fp_w, True, max_w, min_w, evt, dur_h, cat))
    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        if c in ALL_CELLS:
            cell_data[c]["entries"].append((fp_l, False, max_l, min_l, evt, dur_h, cat))

# === LOAD DCA RESULTS ===
dca_results = {}
dca_file = "/tmp/validation5/per_cell_dca_summary.csv"
if os.path.exists(dca_file):
    with open(dca_file) as f:
        for row in csv.DictReader(f):
            cell = row["cell"]
            trigger = int(row["trigger"])
            combo = row["combo"]
            roi = float(row["cell_roi_delta_pct"])
            fires = int(row["dca_fires"])
            total = int(row["total"])
            key = (cell, combo)
            if key not in dca_results or roi > dca_results[key]["roi"]:
                dca_results[key] = {"roi": roi, "trigger": trigger, "fires": fires, "total": total,
                                     "win_rate": float(row["win_rate_pct"]), "fire_rate": float(row["fire_rate_pct"])}

# === LOAD LIVE LOGS ===
log_files = sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl")))
live_fills = []
live_exits = []
live_settlements = []
live_skips = defaultdict(int)
live_cell_matches = []
live_orders = []

for logf in log_files[-7:]:
    with open(logf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except:
                continue
            ev = d.get("event", "")
            det = d.get("details", {})
            if ev == "entry_filled":
                live_fills.append({"ticker": d.get("ticker",""), "ts": d.get("ts",""),
                    "fill_price": det.get("fill_price",0), "qty": det.get("qty",0),
                    "cell": det.get("cell",""), "direction": det.get("direction",""),
                    "play_type": det.get("play_type",""), "anchor_source": det.get("anchor_source","")})
            elif ev == "exit_filled":
                live_exits.append({"ticker": d.get("ticker",""), "ts": d.get("ts",""),
                    "exit_price": det.get("exit_price",0), "entry_price": det.get("entry_price",0),
                    "pnl_cents": det.get("pnl_cents",0), "pnl_dollars": det.get("pnl_dollars",0),
                    "type": "exit"})
            elif ev == "scalp_filled":
                live_exits.append({"ticker": d.get("ticker",""), "ts": d.get("ts",""),
                    "exit_price": det.get("exit_price",0), "entry_price": det.get("entry_price",0),
                    "pnl_cents": det.get("profit_cents",0), "type": "scalp",
                    "hours_before": det.get("hours_before_commence",0)})
            elif ev == "settled":
                live_settlements.append({"ticker": d.get("ticker",""), "ts": d.get("ts",""),
                    "result": det.get("settle",""), "settle_price": det.get("settle_price",0),
                    "entry_price": det.get("entry_price",0), "pnl_cents": det.get("pnl_cents",0),
                    "pnl_dollars": det.get("pnl_dollars",0)})
            elif ev == "skipped":
                live_skips[det.get("reason","unknown")] += 1
            elif ev == "cell_match":
                live_cell_matches.append({"ticker": d.get("ticker",""), "ts": d.get("ts",""),
                    "cell": det.get("cell",""), "direction": det.get("direction",""),
                    "scenario": det.get("scenario",""), "anchor_source": det.get("anchor_source",""),
                    "anchor_value": det.get("anchor_value",0), "delta": det.get("delta",0),
                    "event": det.get("event","")})
            elif ev == "order_placed":
                live_orders.append({"ticker": d.get("ticker",""), "ts": d.get("ts",""),
                    "price": det.get("price",0), "count": det.get("count",0),
                    "action": det.get("action",""), "status": det.get("response_status","")})

ticker_to_cell = {f["ticker"]: f["cell"] for f in live_fills if f["cell"]}
print("Live data: %d fills, %d exits, %d settlements, %d cell_matches" % (
    len(live_fills), len(live_exits), len(live_settlements), len(live_cell_matches)))

# =====================================================================
# TASK 1: Per-cell baseline economics CSV
# =====================================================================
print("Writing Task 1...")
with open(os.path.join(OUT_DIR, "task1_baseline_economics.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","status","exit_cents","N","avg_entry","TWP","mispricing_cents",
                "scalp_WR_pct","ROI_pct","dollar_per_fill","daily_fires","daily_dollar",
                "win_count","loss_count","avg_duration_h","confidence"])
    for cell in sorted(ALL_CELLS.keys()):
        entries = cell_data.get(cell, {}).get("entries", [])
        if not entries: continue
        n = len(entries)
        if n < 15: continue
        exit_c = ALL_CELLS[cell]
        is_active = cell in active_cells
        avg_e = sum(e[0] for e in entries) / n
        wins = sum(1 for e in entries if e[1])
        twp = wins / n
        mp = twp * 100 - avg_e
        scalps = sum(1 for ep,won,mx,mn,evt,dur,cat in entries if mx and mx >= min(99, ep+exit_c))
        sr = scalps / n * 100
        ev = (sr/100)*exit_c + (1-sr/100)*(twp*(99-avg_e) - (1-twp)*(avg_e-1))
        roi = ev / avg_e * 100
        dpf = ev * 10 / 100
        daily_f = n / DAYS / 2
        daily_d = daily_f * dpf
        avg_dur = sum(e[5] for e in entries) / n
        conf = "HIGH" if n >= 50 else "MEDIUM" if n >= 30 else "LOW"
        w.writerow([cell, "ACTIVE" if is_active else "disabled", exit_c, n,
                     "%.1f" % avg_e, "%.3f" % twp, "%.1f" % mp,
                     "%.1f" % sr, "%.1f" % roi, "%.2f" % dpf,
                     "%.2f" % daily_f, "%.2f" % daily_d,
                     wins, n-wins, "%.1f" % avg_dur, conf])

# =====================================================================
# TASK 2: Paired economics CSV
# =====================================================================
print("Writing Task 2...")
pair_data = defaultdict(lambda: {"matches": 0, "both_active": 0, "pnls": []})
for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, min_w, max_w = ev[4], ev[5], ev[6]
    fp_l, min_l, max_l = ev[7], ev[8], ev[9]
    if not fp_w or not fp_l or fp_w<=0 or fp_l<=0: continue
    cw = classify_cell(tier, fp_w)
    cl = classify_cell(tier, fp_l)
    if cw not in ALL_CELLS or cl not in ALL_CELLS: continue
    ew, el = ALL_CELLS[cw], ALL_CELLS[cl]
    tw = min(99, fp_w+ew)
    tl = min(99, fp_l+el)
    pnl_w = ew*10 if max_w and max_w>=tw else (99-fp_w)*10
    pnl_l = el*10 if max_l and max_l>=tl else -(fp_l-1)*10
    cap = (fp_w+fp_l)*10
    pk = tuple(sorted([cw, cl]))
    pair_data[pk]["matches"] += 1
    pair_data[pk]["both_active"] += (1 if cw in active_cells and cl in active_cells else 0)
    pair_data[pk]["pnls"].append((pnl_w+pnl_l, cap, pnl_w, pnl_l))

with open(os.path.join(OUT_DIR, "task2_paired_economics.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell_A","cell_B","N_matches","both_active","avg_joint_pnl_cents",
                "joint_ROI_pct","avg_capital_cents","avg_winner_pnl","avg_loser_pnl"])
    for pair in sorted(pair_data.keys()):
        d = pair_data[pair]
        n = d["matches"]
        if n < 3: continue
        ps = d["pnls"]
        ajp = sum(p[0] for p in ps)/n
        ac = sum(p[1] for p in ps)/n
        aw = sum(p[2] for p in ps)/n
        al = sum(p[3] for p in ps)/n
        roi = ajp/ac*100 if ac else 0
        w.writerow([pair[0], pair[1], n, d["both_active"],
                     "%.1f" % ajp, "%.1f" % roi, "%.0f" % ac, "%.0f" % aw, "%.0f" % al])

# =====================================================================
# TASK 3: Entry timing CSV
# =====================================================================
print("Writing Task 3...")
with open(os.path.join(OUT_DIR, "task3_entry_timing.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N","avg_duration_h","median_duration_h",
                "pct_lt2h","pct_2_6h","pct_6_12h","pct_gt12h"])
    for cell in sorted(ALL_CELLS.keys()):
        entries = cell_data.get(cell, {}).get("entries", [])
        if len(entries) < 10: continue
        n = len(entries)
        durs = sorted([e[5] for e in entries])
        w.writerow([cell, n, "%.1f" % (sum(durs)/n), "%.1f" % durs[n//2],
                     "%.1f" % (sum(1 for d in durs if d<2)/n*100),
                     "%.1f" % (sum(1 for d in durs if 2<=d<6)/n*100),
                     "%.1f" % (sum(1 for d in durs if 6<=d<12)/n*100),
                     "%.1f" % (sum(1 for d in durs if d>=12)/n*100)])

# =====================================================================
# TASK 4: Harmonized scorecard CSV
# =====================================================================
print("Writing Task 4...")
with open(os.path.join(OUT_DIR, "task4_harmonized_scorecard.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","status","N","avg_entry","TWP","mispricing","scalp_WR_pct","exit_cents",
                "ROI_pct","dollar_per_fill","daily_fires","daily_dollar",
                "dca_A_roi","dca_A_trigger","dca_A_fire_rate","dca_A_win_rate",
                "dca_B_roi","dca_B_trigger","dca_B_fire_rate","dca_B_win_rate",
                "avg_duration_h","win_count","loss_count","confidence","recommendation"])
    for cell in sorted(ALL_CELLS.keys()):
        entries = cell_data.get(cell, {}).get("entries", [])
        if not entries: continue
        n = len(entries)
        exit_c = ALL_CELLS[cell]
        is_active = cell in active_cells
        avg_e = sum(e[0] for e in entries) / n
        wins = sum(1 for e in entries if e[1])
        twp = wins / n
        mp = twp*100 - avg_e
        scalps = sum(1 for ep,won,mx,mn,evt,dur,cat in entries if mx and mx >= min(99,ep+exit_c))
        sr = scalps / n * 100
        ev = (sr/100)*exit_c + (1-sr/100)*(twp*(99-avg_e) - (1-twp)*(avg_e-1))
        roi = ev / avg_e * 100
        dpf = ev * 10 / 100
        daily_f = n / DAYS / 2
        avg_dur = sum(e[5] for e in entries) / n
        conf = "HIGH" if n >= 50 else "MEDIUM" if n >= 30 else "LOW"

        da = dca_results.get((cell, "A"), {"roi":0,"trigger":0,"fire_rate":0,"win_rate":0})
        db = dca_results.get((cell, "B"), {"roi":0,"trigger":0,"fire_rate":0,"win_rate":0})

        if is_active:
            rec = "KEEP" if roi > 0 else "RETUNE" if roi > -5 else "DISABLE"
        else:
            rec = "RE-ENABLE" if mp > 0 and roi > 5 and n >= 30 else "RE-ENABLE" if mp > 0 and roi > 0 and n >= 20 else "STAY-OFF"

        w.writerow([cell, "ACTIVE" if is_active else "disabled", n, "%.1f"%avg_e,
                     "%.3f"%twp, "%.1f"%mp, "%.1f"%sr, exit_c, "%.1f"%roi, "%.2f"%dpf,
                     "%.2f"%daily_f, "%.2f"%(daily_f*dpf),
                     "%.1f"%da["roi"], da["trigger"], "%.1f"%da.get("fire_rate",0), "%.1f"%da.get("win_rate",0),
                     "%.1f"%db["roi"], db["trigger"], "%.1f"%db.get("fire_rate",0), "%.1f"%db.get("win_rate",0),
                     "%.1f"%avg_dur, wins, n-wins, conf, rec])

# =====================================================================
# TASK 5: Cross-tabulation by tier
# =====================================================================
print("Writing Task 5...")
with open(os.path.join(OUT_DIR, "task5_cross_tabulation.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","tier","N","TWP","scalp_WR_pct","avg_entry","ROI_pct"])
    for cell in sorted(ALL_CELLS.keys()):
        entries = cell_data.get(cell, {}).get("entries", [])
        if len(entries) < 10: continue
        # Group by category
        by_cat = defaultdict(list)
        for ep,won,mx,mn,evt,dur,cat in entries:
            by_cat[cat].append((ep,won,mx,mn))
        for cat in sorted(by_cat.keys()):
            es = by_cat[cat]
            n = len(es)
            if n < 3: continue
            exit_c = ALL_CELLS[cell]
            avg_e = sum(e[0] for e in es)/n
            wins = sum(1 for e in es if e[1])
            twp = wins/n
            scalps = sum(1 for ep,won,mx,mn in es if mx and mx>=min(99,ep+exit_c))
            sr = scalps/n*100
            ev = (sr/100)*exit_c + (1-sr/100)*(twp*(99-avg_e)-(1-twp)*(avg_e-1))
            roi = ev/avg_e*100 if avg_e else 0
            w.writerow([cell, cat, n, "%.3f"%twp, "%.1f"%sr, "%.1f"%avg_e, "%.1f"%roi])

# =====================================================================
# TASK 6: Live vs sweep CSV (raw data, known double-counting bug)
# =====================================================================
print("Writing Task 6...")
live_cell_pnl = defaultdict(lambda: {"fills":0,"scalps":0,"settle_w":0,"settle_l":0,
    "pnl_cents":0,"capital":0,"fill_prices":[]})
for f in live_fills:
    c = f["cell"]
    if c:
        live_cell_pnl[c]["fills"] += 1
        live_cell_pnl[c]["capital"] += f["fill_price"] * f["qty"]
        live_cell_pnl[c]["fill_prices"].append(f["fill_price"])

for e in live_exits:
    c = ticker_to_cell.get(e["ticker"],"")
    if c:
        live_cell_pnl[c]["scalps"] += 1
        live_cell_pnl[c]["pnl_cents"] += e.get("pnl_cents",0)

# NOTE: settlement PnL is per-contract not per-position — known bug
for s in live_settlements:
    c = ticker_to_cell.get(s["ticker"],"")
    if c:
        if s["result"] == "WIN": live_cell_pnl[c]["settle_w"] += 1
        else: live_cell_pnl[c]["settle_l"] += 1
        live_cell_pnl[c]["pnl_cents"] += s.get("pnl_cents",0)

with open(os.path.join(OUT_DIR, "task6_live_vs_sweep.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","live_fills","live_scalps","settle_wins","settle_losses",
                "live_pnl_cents_RAW_BUGGY","live_capital","sweep_ROI_pct",
                "NOTE_settlement_is_per_contract_not_per_position"])
    for cell in sorted(live_cell_pnl.keys()):
        d = live_cell_pnl[cell]
        entries = cell_data.get(cell, {}).get("entries", [])
        n = len(entries)
        exit_c = ALL_CELLS.get(cell, 0)
        if n > 0:
            avg_e = sum(e[0] for e in entries)/n
            wins = sum(1 for e in entries if e[1])
            twp = wins/n
            scalps = sum(1 for ep,won,mx,mn,evt,dur,cat in entries if mx and mx>=min(99,ep+exit_c))
            sr = scalps/n*100
            ev = (sr/100)*exit_c + (1-sr/100)*(twp*(99-avg_e)-(1-twp)*(avg_e-1))
            sweep_roi = ev/avg_e*100 if avg_e else 0
        else:
            sweep_roi = 0
        w.writerow([cell, d["fills"], d["scalps"], d["settle_w"], d["settle_l"],
                     d["pnl_cents"], d["capital"], "%.1f"%sweep_roi,
                     "BUGGY: settlements logged per-contract not per-position"])

# =====================================================================
# TASK 7: P&L attribution — deduplicated by unique ticker
# =====================================================================
print("Writing Task 7...")
# Deduplicate settlements by unique ticker (take first occurrence)
seen_tickers = set()
deduped_settlements = []
for s in live_settlements:
    tk = s["ticker"]
    if tk not in seen_tickers:
        seen_tickers.add(tk)
        deduped_settlements.append(s)

# Deduplicate scalps similarly
seen_scalp_tickers = set()
deduped_exits = []
for e in live_exits:
    tk = e["ticker"]
    if tk not in seen_scalp_tickers:
        seen_scalp_tickers.add(tk)
        deduped_exits.append(e)

with open(os.path.join(OUT_DIR, "task7_pnl_attribution.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","cell","type","entry_price","exit_price","result","pnl_cents","pnl_dollars","ts"])
    for s in deduped_settlements:
        c = ticker_to_cell.get(s["ticker"], "?")
        w.writerow([s["ticker"], c, "settlement", s["entry_price"], s["settle_price"],
                     s["result"], s["pnl_cents"], s.get("pnl_dollars",0), s["ts"]])
    for e in deduped_exits:
        c = ticker_to_cell.get(e["ticker"], "?")
        w.writerow([e["ticker"], c, e.get("type","exit"), e.get("entry_price",0),
                     e.get("exit_price",0), "SCALP", e.get("pnl_cents",0), "", e.get("ts","")])

# Summary by cell
with open(os.path.join(OUT_DIR, "task7_pnl_by_cell.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","settle_wins","settle_losses","scalps","total_pnl_cents","total_pnl_dollars"])
    cell_pnl = defaultdict(lambda: {"sw":0,"sl":0,"sc":0,"pnl":0})
    for s in deduped_settlements:
        c = ticker_to_cell.get(s["ticker"], "?")
        if s["result"] == "WIN": cell_pnl[c]["sw"] += 1
        else: cell_pnl[c]["sl"] += 1
        cell_pnl[c]["pnl"] += s.get("pnl_cents",0)
    for e in deduped_exits:
        c = ticker_to_cell.get(e["ticker"], "?")
        cell_pnl[c]["sc"] += 1
        cell_pnl[c]["pnl"] += e.get("pnl_cents",0)
    for c in sorted(cell_pnl.keys()):
        d = cell_pnl[c]
        w.writerow([c, d["sw"], d["sl"], d["sc"], d["pnl"], "%.2f"%(d["pnl"]/100)])

# =====================================================================
# TASK 8: Skip rate per cell
# =====================================================================
print("Writing Task 8...")
with open(os.path.join(OUT_DIR, "task8_skip_rates.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["reason","count"])
    for reason, count in sorted(live_skips.items(), key=lambda x: -x[1]):
        w.writerow([reason, count])

cell_match_counts = defaultdict(int)
cell_fill_counts = defaultdict(int)
cell_order_counts = defaultdict(int)
for cm in live_cell_matches:
    cell_match_counts[cm["cell"]] += 1
for f in live_fills:
    cell_fill_counts[f["cell"]] += 1

with open(os.path.join(OUT_DIR, "task8_fill_funnel.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","cell_matches","fills","fill_rate_pct"])
    for cell in sorted(set(list(cell_match_counts.keys()) + list(cell_fill_counts.keys()))):
        m = cell_match_counts.get(cell, 0)
        fl = cell_fill_counts.get(cell, 0)
        w.writerow([cell, m, fl, "%.1f"%(fl/m*100) if m else "0"])

# =====================================================================
# TASK 9: Anchor health
# =====================================================================
print("Writing Task 9...")
with open(os.path.join(OUT_DIR, "task9_anchor_health.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["anchor_source","count","pct"])
    total = len(live_cell_matches)
    src_counts = defaultdict(int)
    for cm in live_cell_matches:
        src_counts[cm["anchor_source"] or "BLANK"] += 1
    for src, cnt in sorted(src_counts.items(), key=lambda x: -x[1]):
        w.writerow([src, cnt, "%.1f"%(cnt/total*100) if total else 0])

# Per-fill anchor data
with open(os.path.join(OUT_DIR, "task9_per_fill_anchor.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","cell","fill_price","anchor_source","play_type","ts"])
    for fl in live_fills:
        w.writerow([fl["ticker"], fl["cell"], fl["fill_price"],
                     fl.get("anchor_source",""), fl["play_type"], fl["ts"]])

# =====================================================================
# TASK 10: True opportunity space
# =====================================================================
print("Writing Task 10...")
# Pre-compute per-cell stats for mispricing check
cell_stats = {}
for cell in ALL_CELLS:
    entries = cell_data.get(cell, {}).get("entries", [])
    if not entries: continue
    n = len(entries)
    avg_e = sum(e[0] for e in entries)/n
    wins = sum(1 for e in entries if e[1])
    twp = wins/n
    mp = twp*100 - avg_e
    cell_stats[cell] = {"twp": twp, "mp": mp, "n": n, "avg_e": avg_e}

with open(os.path.join(OUT_DIR, "task10_opportunity_space.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N","avg_entry","TWP","mispricing","has_positive_mispricing",
                "dollar_per_opportunity","daily_opportunities"])
    for cell in sorted(ALL_CELLS.keys()):
        cs = cell_stats.get(cell)
        if not cs: continue
        entries = cell_data[cell]["entries"]
        n = cs["n"]
        exit_c = ALL_CELLS[cell]
        avg_e = cs["avg_e"]
        twp = cs["twp"]
        mp = cs["mp"]
        scalps = sum(1 for ep,won,mx,mn,evt,dur,cat in entries if mx and mx>=min(99,ep+exit_c))
        sr = scalps/n*100
        ev = (sr/100)*exit_c + (1-sr/100)*(twp*(99-avg_e)-(1-twp)*(avg_e-1))
        dpf = ev*10/100
        w.writerow([cell, n, "%.1f"%avg_e, "%.3f"%twp, "%.1f"%mp,
                     "YES" if mp > 0 else "no", "%.2f"%dpf, "%.2f"%(n/DAYS/2)])

# =====================================================================
# TASK 11: Recommendations
# =====================================================================
print("Writing Task 11...")
with open(os.path.join(OUT_DIR, "task11_recommendations.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","status","N","TWP","mispricing","scalp_WR","ROI_pct","recommendation","reason"])
    for cell in sorted(ALL_CELLS.keys()):
        entries = cell_data.get(cell, {}).get("entries", [])
        if not entries: continue
        n = len(entries)
        exit_c = ALL_CELLS[cell]
        is_active = cell in active_cells
        avg_e = sum(e[0] for e in entries)/n
        wins = sum(1 for e in entries if e[1])
        twp = wins/n
        mp = twp*100-avg_e
        scalps = sum(1 for ep,won,mx,mn,evt,dur,cat in entries if mx and mx>=min(99,ep+exit_c))
        sr = scalps/n*100
        ev = (sr/100)*exit_c+(1-sr/100)*(twp*(99-avg_e)-(1-twp)*(avg_e-1))
        roi = ev/avg_e*100 if avg_e else 0

        if is_active:
            if n < 15: rec,why = "INVESTIGATE","N=%d too low"%n
            elif roi > 5 and mp > 0: rec,why = "KEEP","positive ROI+mispricing"
            elif roi > 0: rec,why = "KEEP","positive ROI (%.0f%%)"%roi
            elif roi > -5: rec,why = "RETUNE","marginally negative ROI"
            else: rec,why = "DISABLE","negative ROI (%.0f%%)"%roi
        else:
            if mp > 3 and roi > 5 and n >= 30: rec,why = "RE-ENABLE","+%.1fc mp, +%.0f%% ROI"%(mp,roi)
            elif mp > 0 and roi > 0 and n >= 20: rec,why = "RE-ENABLE","positive mp+ROI"
            else: rec,why = "STAY-OFF","mp=%.1fc, ROI=%.0f%%"%(mp,roi)

        w.writerow([cell, "ACTIVE" if is_active else "disabled", n,
                     "%.3f"%twp, "%.1f"%mp, "%.1f"%sr, "%.1f"%roi, rec, why])

# =====================================================================
# TASK 12: Monte Carlo simulation — full output
# =====================================================================
print("Writing Task 12...")
# Build per-cell PnL distributions for active cells
cell_pnl_dists = {}
for cell in ALL_CELLS:
    if cell not in active_cells: continue
    entries = cell_data.get(cell, {}).get("entries", [])
    if not entries: continue
    exit_c = ALL_CELLS[cell]
    pnls = []
    for ep,won,mx,mn,evt,dur,cat in entries:
        target = min(99, ep+exit_c)
        if mx and mx >= target:
            pnls.append(exit_c * 10 / 100)
        elif won:
            pnls.append((99-ep) * 10 / 100)
        else:
            pnls.append(-(ep-1) * 10 / 100)
    if pnls:
        cell_pnl_dists[cell] = pnls

random.seed(42)
sim_daily = []
for i in range(10000):
    day_pnl = 0
    for cell, pnls in cell_pnl_dists.items():
        fires = max(1, len(pnls) // (DAYS*2))
        for _ in range(fires):
            day_pnl += random.choice(pnls)
    sim_daily.append(day_pnl)

with open(os.path.join(OUT_DIR, "task12_monte_carlo_runs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sim_id","daily_pnl_dollars"])
    for i, pnl in enumerate(sim_daily):
        w.writerow([i, "%.2f" % pnl])

sim_daily.sort()
ns = len(sim_daily)
with open(os.path.join(OUT_DIR, "task12_monte_carlo_summary.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric","value"])
    avg = sum(sim_daily)/ns
    std = (sum((x-avg)**2 for x in sim_daily)/ns)**0.5
    w.writerow(["mean_daily_pnl", "%.2f"%avg])
    w.writerow(["std_dev", "%.2f"%std])
    w.writerow(["sharpe_daily", "%.3f"%(avg/std if std else 0)])
    w.writerow(["p5_worst", "%.2f"%sim_daily[ns//20]])
    w.writerow(["p10", "%.2f"%sim_daily[ns//10]])
    w.writerow(["p25", "%.2f"%sim_daily[ns//4]])
    w.writerow(["median", "%.2f"%sim_daily[ns//2]])
    w.writerow(["p75", "%.2f"%sim_daily[3*ns//4]])
    w.writerow(["p90", "%.2f"%sim_daily[9*ns//10]])
    w.writerow(["p95_best", "%.2f"%sim_daily[19*ns//20]])
    w.writerow(["n_simulations", ns])
    w.writerow(["n_active_cells", len(cell_pnl_dists)])
    w.writerow(["historical_events", len(events)])
    w.writerow(["date_range", "2026-03-20 to 2026-04-17"])

# === METHODOLOGY ===
with open(os.path.join(OUT_DIR, "methodology.txt"), "w") as f:
    f.write("Ultimate Cell Economics Analysis — Methodology\n")
    f.write("=" * 60 + "\n\n")
    f.write("Data Sources:\n")
    f.write("  1. historical_events: %d events, Mar 20 - Apr 17, 2026\n" % len(events))
    f.write("  2. DCA v3 results: /tmp/validation5/per_cell_dca_summary.csv\n")
    f.write("     (515M BBO rows, inline state machine, time-ordered)\n")
    f.write("  3. Live bot logs: %d files (last 7 days)\n" % len(log_files[-7:]))
    f.write("     %d fills, %d exits, %d settlements\n" % (len(live_fills), len(live_exits), len(live_settlements)))
    f.write("  4. deploy_v4.json: %d active + %d disabled cells\n" % (len(active_cells), len(DISABLED_EXITS)))
    f.write("\nCell Classification:\n")
    f.write("  tier × direction × 5c price bucket\n")
    f.write("  Entry price = first_price from historical_events\n")
    f.write("  TWP = fraction of entries in that cell that won settlement\n")
    f.write("  Mispricing = TWP*100 - avg_entry_price (in cents)\n")
    f.write("\nScalp WR Calculation:\n")
    f.write("  Scalp = max_price >= entry + exit_cents at any point during match lifecycle\n")
    f.write("  This includes in-play price movement (exit orders stay resting)\n")
    f.write("\nROI Calculation:\n")
    f.write("  EV/fill = scalp_rate * exit_c + (1-scalp_rate) * (TWP*(99-entry) - (1-TWP)*(entry-1))\n")
    f.write("  ROI = EV/fill / entry * 100\n")
    f.write("  $/fill = EV/fill * 10_contracts / 100_cents_per_dollar\n")
    f.write("\nKnown Issues:\n")
    f.write("  - Task 6: Settlement PnL is per-contract not per-position (double-counted)\n")
    f.write("  - Live log ticker→cell mapping fails for some older entries (shows '?')\n")
    f.write("  - 32%% of cell matches have blank anchor_source in logs\n")
    f.write("  - Monte Carlo uses uniform sampling from historical distribution\n")
    f.write("    (doesn't model serial correlation or regime changes)\n")
    f.write("\nRun at: %s\n" % datetime.now(ET).strftime("%Y-%m-%d %I:%M %p ET"))

conn.close()
print("\nAll CSVs written to %s/" % OUT_DIR)
print("Files:")
for fn in sorted(os.listdir(OUT_DIR)):
    sz = os.path.getsize(os.path.join(OUT_DIR, fn))
    print("  %s (%.1f KB)" % (fn, sz/1024))
