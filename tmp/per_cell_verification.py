#!/usr/bin/env python3
"""
Per-cell verification with raw data exposure.
Produces 7 CSVs for commit+push.
"""
import sqlite3, json, csv, os, math, random, glob
from collections import defaultdict
from datetime import datetime, timezone, timedelta

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"
os.makedirs(OUT_DIR, exist_ok=True)
ET = timezone(timedelta(hours=-4))

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

# Scalp-constrained optimal exits from prior analysis
OPTIMAL_EXITS = {
    "ATP_CHALL_leader_50-54": 7, "ATP_CHALL_leader_55-59": 17,
    "ATP_CHALL_leader_60-64": 26, "ATP_CHALL_leader_65-69": 17,
    "ATP_CHALL_leader_70-74": 19, "ATP_CHALL_leader_75-79": 7,
    "ATP_CHALL_leader_80-84": 12, "ATP_CHALL_leader_85-89": 6,
    "ATP_CHALL_underdog_10-14": 35, "ATP_CHALL_underdog_15-19": 42,
    "ATP_CHALL_underdog_20-24": 65, "ATP_CHALL_underdog_25-29": 18,
    "ATP_CHALL_underdog_30-34": 7, "ATP_CHALL_underdog_35-39": 33,
    "ATP_CHALL_underdog_40-44": 27, "ATP_CHALL_underdog_45-49": 48,
    "ATP_MAIN_leader_50-54": 40, "ATP_MAIN_leader_55-59": 37,
    "ATP_MAIN_leader_60-64": 26, "ATP_MAIN_leader_70-74": 16,
    "ATP_MAIN_leader_75-79": 14, "ATP_MAIN_underdog_20-24": 25,
    "ATP_MAIN_underdog_25-29": 20, "ATP_MAIN_underdog_30-34": 8,
    "ATP_MAIN_underdog_35-39": 46, "ATP_MAIN_underdog_40-44": 4,
    "ATP_MAIN_underdog_45-49": 10,
    "WTA_CHALL_leader_55-59": 20, "WTA_CHALL_underdog_40-44": 53,
    "WTA_MAIN_leader_50-54": 16, "WTA_MAIN_leader_55-59": 6,
    "WTA_MAIN_leader_60-64": 18, "WTA_MAIN_leader_65-69": 27,
    "WTA_MAIN_leader_70-74": 23, "WTA_MAIN_leader_80-84": 17,
    "WTA_MAIN_leader_85-89": 14,
    "WTA_MAIN_underdog_15-19": 31, "WTA_MAIN_underdog_20-24": 22,
    "WTA_MAIN_underdog_25-29": 17, "WTA_MAIN_underdog_30-34": 8,
    "WTA_MAIN_underdog_35-39": 19, "WTA_MAIN_underdog_40-44": 4,
    "WTA_MAIN_underdog_45-49": 15,
}

SCALP_CAP = 95

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

def inverse_cell(cell):
    parts = cell.split("_")
    tier = parts[0] + "_" + parts[1]
    direction = parts[2]
    bucket = parts[3]
    lo, hi = int(bucket.split("-")[0]), int(bucket.split("-")[1])
    inv_mid = 100 - (lo + hi) / 2.0
    inv_dir = "underdog" if direction == "leader" else "leader"
    inv_bs = int(inv_mid // 5) * 5
    return "%s_%s_%d-%d" % (tier, inv_dir, inv_bs, inv_bs + 4)

cat_to_tier = {"ATP_MAIN":"ATP_MAIN","ATP_CHALL":"ATP_CHALL",
               "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}

# Load historical events
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
print("Loaded %d events" % len(events))

DAYS = 28
QTY = 10

# Build entries
all_entries = defaultdict(list)
event_sides = defaultdict(list)  # event_ticker -> [(cell, side, entry, ...)]

for ev in events:
    evt, cat = ev[0], ev[1]
    tier = cat_to_tier.get(cat)
    if not tier: continue
    fp_w, min_w, max_w, last_w = ev[4], ev[5], ev[6], ev[7]
    fp_l, min_l, max_l = ev[8], ev[12], ev[13]
    is_scalar = max_w is not None and max_w < 95
    dur_h = 0
    try:
        t1 = datetime.fromisoformat(ev[10].replace("Z","+00:00"))
        t2 = datetime.fromisoformat(ev[11].replace("Z","+00:00"))
        dur_h = (t2-t1).total_seconds()/3600
    except: pass

    if fp_w and 0 < fp_w < 100:
        c = classify_cell(tier, fp_w)
        if c in ALL_CELLS:
            e = {"side":"winner","entry":fp_w,"max_price":max_w,"is_scalar":is_scalar,
                 "settle_price":last_w if last_w else 99,"evt":evt,"dur_h":dur_h,
                 "first_ts":ev[10],"last_ts":ev[11]}
            all_entries[c].append(e)
            event_sides[evt].append((c, "winner", fp_w, max_w))

    if fp_l and 0 < fp_l < 100:
        c = classify_cell(tier, fp_l)
        if c in ALL_CELLS:
            e = {"side":"loser","entry":fp_l,"max_price":max_l,"is_scalar":is_scalar,
                 "settle_price":min_l if min_l else 1,"evt":evt,"dur_h":dur_h,
                 "first_ts":ev[10],"last_ts":ev[11]}
            all_entries[c].append(e)
            event_sides[evt].append((c, "loser", fp_l, max_l))

def compute_ev_full(entries, ec):
    if not entries: return None
    n = len(entries)
    outcomes = []
    scalp_count = 0
    for e in entries:
        target = min(99, e["entry"]+ec)
        scalped = e["max_price"] is not None and e["max_price"] >= target
        if scalped:
            outcomes.append(ec*QTY/100)
            scalp_count += 1
        elif e["side"]=="winner" and not e["is_scalar"]:
            outcomes.append((99-e["entry"])*QTY/100)
        elif e["side"]=="loser" and not e["is_scalar"]:
            outcomes.append(-(e["entry"]-1)*QTY/100)
        else:
            outcomes.append((e["settle_price"]-e["entry"])*QTY/100)

    mean = sum(outcomes)/n
    std = (sum((x-mean)**2 for x in outcomes)/n)**0.5
    ci = 1.96*std/(n**0.5) if n > 1 else 999
    avg_e = sum(e["entry"] for e in entries)/n
    cost = avg_e*QTY/100
    roi = mean/cost*100 if cost else 0
    sr = scalp_count/n*100
    df = n/DAYS/2
    return {"ev":mean,"std":std,"ci_lo":mean-ci,"ci_hi":mean+ci,"roi":roi,
            "cost":cost,"sr":sr,"n":n,"df":df,"dd":df*mean,"avg_e":avg_e,
            "ec":ec,"outcomes":outcomes,"scalp_count":scalp_count}

# Load live logs
log_files = sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl")))
live_fills = []
live_exits = []
live_settlements = []
for logf in log_files[-7:]:
    with open(logf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except: continue
            ev = d.get("event","")
            det = d.get("details",{})
            if ev == "entry_filled":
                live_fills.append({"ticker":d.get("ticker",""),"ts":d.get("ts",""),
                    "fill_price":det.get("fill_price",0),"qty":det.get("qty",0),
                    "cell":det.get("cell","")})
            elif ev in ("exit_filled","scalp_filled"):
                live_exits.append({"ticker":d.get("ticker",""),"ts":d.get("ts",""),
                    "exit_price":det.get("exit_price",0),"entry_price":det.get("entry_price",0),
                    "pnl_cents":det.get("pnl_cents",det.get("profit_cents",0))})
            elif ev == "settled":
                live_settlements.append({"ticker":d.get("ticker",""),"ts":d.get("ts",""),
                    "result":det.get("settle",""),"entry_price":det.get("entry_price",0),
                    "pnl_cents":det.get("pnl_cents",0),"pnl_dollars":det.get("pnl_dollars",0)})

ticker_to_cell = {f["ticker"]:f["cell"] for f in live_fills if f["cell"]}
print("Live data: %d fills, %d exits, %d settlements" % (len(live_fills),len(live_exits),len(live_settlements)))

# Determine cells to include: all active + all flagged for re-enable
include_cells = set(active_cells.keys())
for cell, r in [(c, compute_ev_full(all_entries.get(c,[]), OPTIMAL_EXITS.get(c, ALL_CELLS.get(c,10))))
                 for c in ALL_CELLS]:
    if r and r["roi"] > 0 and r["n"] >= 15:
        include_cells.add(cell)

# =====================================================================
# TASK 1: Per-cell raw economics
# =====================================================================
print("Writing Task 1...")
with open(os.path.join(OUT_DIR, "task1_raw_economics.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","avg_entry","current_exit","optimal_exit","N","daily_entry_rate",
                "current_scalp_rate_pct","current_ev_per_entry","current_daily_dollar",
                "optimal_scalp_rate_pct","optimal_ev_per_entry","optimal_daily_dollar",
                "direction","inverse_cell","inverse_status",
                "optimal_ci_lower","optimal_ci_upper","confidence_flag"])
    for cell in sorted(include_cells):
        entries = all_entries.get(cell,[])
        if not entries: continue
        cur_ec = ALL_CELLS.get(cell, 10)
        opt_ec = OPTIMAL_EXITS.get(cell, cur_ec)
        avg_e = sum(e["entry"] for e in entries)/len(entries)
        max_scalp = int(SCALP_CAP - avg_e)
        if opt_ec > max_scalp: opt_ec = max_scalp
        if opt_ec < 3: opt_ec = 3

        r_cur = compute_ev_full(entries, cur_ec)
        r_opt = compute_ev_full(entries, opt_ec)
        if not r_cur or not r_opt: continue

        direction = "leader" if "leader" in cell else "underdog"
        inv = inverse_cell(cell)
        inv_status = "ACTIVE" if inv in active_cells else ("disabled" if inv in ALL_CELLS else "no_config")
        conf = "HIGH" if r_opt["n"]>=50 and r_opt["ci_lo"]>0 else "MED" if r_opt["n"]>=20 and r_opt["ci_lo"]>-0.2 else "LOW"

        w.writerow([cell, "%.1f"%avg_e, cur_ec, opt_ec, r_opt["n"], "%.2f"%r_opt["df"],
                     "%.1f"%r_cur["sr"], "%.4f"%r_cur["ev"], "%.4f"%r_cur["dd"],
                     "%.1f"%r_opt["sr"], "%.4f"%r_opt["ev"], "%.4f"%r_opt["dd"],
                     direction, inv, inv_status,
                     "%.4f"%r_opt["ci_lo"], "%.4f"%r_opt["ci_hi"], conf])

# =====================================================================
# TASK 2: Scalp timing distribution
# =====================================================================
print("Writing Task 2...")
# We don't have per-scalp timing from historical_events (only first_ts/last_ts)
# We CAN estimate: if a scalp fires, it fires when max_price is reached
# But we don't know WHEN max_price was reached in the trade tape
# We'll note this limitation and use duration as proxy

with open(os.path.join(OUT_DIR, "task2_scalp_timing.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","optimal_exit","N_total","N_scalps","N_winner_scalps","N_loser_scalps",
                "pct_winner_scalps","pct_loser_scalps",
                "avg_match_duration_h","median_duration_h",
                "NOTE_timing_within_match_not_available_from_trade_tape"])
    for cell in sorted(include_cells):
        entries = all_entries.get(cell,[])
        if not entries: continue
        opt_ec = OPTIMAL_EXITS.get(cell, ALL_CELLS.get(cell,10))
        avg_e = sum(e["entry"] for e in entries)/len(entries)
        max_s = int(SCALP_CAP - avg_e)
        if opt_ec > max_s: opt_ec = max_s

        n = len(entries)
        w_scalps = sum(1 for e in entries if e["side"]=="winner" and not e["is_scalar"]
                       and e["max_price"] and e["max_price"]>=min(99,e["entry"]+opt_ec))
        l_scalps = sum(1 for e in entries if e["side"]=="loser" and not e["is_scalar"]
                       and e["max_price"] and e["max_price"]>=min(99,e["entry"]+opt_ec))
        total_scalps = w_scalps + l_scalps
        durs = sorted([e["dur_h"] for e in entries if e["dur_h"]>0])
        avg_dur = sum(durs)/len(durs) if durs else 0
        med_dur = durs[len(durs)//2] if durs else 0

        w.writerow([cell, opt_ec, n, total_scalps, w_scalps, l_scalps,
                     "%.1f"%(w_scalps/n*100) if n else 0,
                     "%.1f"%(l_scalps/n*100) if n else 0,
                     "%.1f"%avg_dur, "%.1f"%med_dur,
                     "historical_events has first/last trade time only, not per-scalp timing"])

# =====================================================================
# TASK 3: Live behavior vs corrected projection
# =====================================================================
print("Writing Task 3...")
# Aggregate live data per cell (deduplicate by ticker)
live_cell_data = defaultdict(lambda: {"fills":0,"scalps":0,"settle_w":0,"settle_l":0,
    "pnl_cents":0,"fill_prices":[],"capital":0})

seen_tickers_exit = set()
seen_tickers_settle = set()

for fl in live_fills:
    c = fl["cell"]
    if c:
        live_cell_data[c]["fills"] += 1
        live_cell_data[c]["fill_prices"].append(fl["fill_price"])
        live_cell_data[c]["capital"] += fl["fill_price"] * fl["qty"]

for ex in live_exits:
    tk = ex["ticker"]
    if tk in seen_tickers_exit: continue
    seen_tickers_exit.add(tk)
    c = ticker_to_cell.get(tk,"")
    if c:
        live_cell_data[c]["scalps"] += 1
        live_cell_data[c]["pnl_cents"] += ex.get("pnl_cents",0)

for st in live_settlements:
    tk = st["ticker"]
    if tk in seen_tickers_settle: continue
    seen_tickers_settle.add(tk)
    c = ticker_to_cell.get(tk,"")
    if c:
        if st["result"]=="WIN": live_cell_data[c]["settle_w"] += 1
        else: live_cell_data[c]["settle_l"] += 1
        live_cell_data[c]["pnl_cents"] += st.get("pnl_cents",0)

with open(os.path.join(OUT_DIR, "task3_live_vs_projection.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","live_entries","live_scalps","live_settle_w","live_settle_l",
                "live_scalp_rate_pct","live_avg_fill_price","live_pnl_cents","live_pnl_dollars",
                "live_daily_dollar","projected_daily_dollar_current_exit",
                "discrepancy","days_of_data"])
    for cell in sorted(include_cells):
        ld = live_cell_data.get(cell)
        entries = all_entries.get(cell,[])
        cur_ec = ALL_CELLS.get(cell,10)
        r_cur = compute_ev_full(entries, cur_ec) if entries else None

        if ld and ld["fills"]>0:
            avg_fp = sum(ld["fill_prices"])/len(ld["fill_prices"])
            live_sr = ld["scalps"]/(ld["scalps"]+ld["settle_w"]+ld["settle_l"])*100 if (ld["scalps"]+ld["settle_w"]+ld["settle_l"])>0 else 0
            live_pnl_d = ld["pnl_cents"]/100
            live_daily = live_pnl_d / 7  # 7 days of data
            proj_daily = r_cur["dd"] if r_cur else 0
            disc = live_daily - proj_daily
            w.writerow([cell, ld["fills"], ld["scalps"], ld["settle_w"], ld["settle_l"],
                         "%.1f"%live_sr, "%.1f"%avg_fp, ld["pnl_cents"], "%.2f"%live_pnl_d,
                         "%.3f"%live_daily, "%.3f"%proj_daily, "%.3f"%disc, 7])
        else:
            w.writerow([cell, 0,0,0,0,"","","","","","%.3f"%(r_cur["dd"] if r_cur else 0),"","7"])

# =====================================================================
# TASK 4: Capital and duration profile
# =====================================================================
print("Writing Task 4...")
with open(os.path.join(OUT_DIR, "task4_capital_duration.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","avg_entry","position_size_contracts","capital_per_fill",
                "optimal_exit","avg_duration_h","median_duration_h","p90_duration_h",
                "capital_hours_per_fill","daily_fires","daily_capital_hours"])
    for cell in sorted(include_cells):
        entries = all_entries.get(cell,[])
        if not entries: continue
        avg_e = sum(e["entry"] for e in entries)/len(entries)
        opt_ec = OPTIMAL_EXITS.get(cell, ALL_CELLS.get(cell,10))
        cap = avg_e * QTY / 100
        durs = sorted([e["dur_h"] for e in entries if e["dur_h"]>0])
        if not durs: durs = [12]
        avg_dur = sum(durs)/len(durs)
        med_dur = durs[len(durs)//2]
        p90_dur = durs[int(len(durs)*0.9)]
        cap_hours = cap * avg_dur
        df = len(entries)/DAYS/2
        w.writerow([cell, "%.1f"%avg_e, QTY, "%.2f"%cap, opt_ec,
                     "%.1f"%avg_dur, "%.1f"%med_dur, "%.1f"%p90_dur,
                     "%.1f"%cap_hours, "%.2f"%df, "%.1f"%(df*cap_hours)])

# =====================================================================
# TASK 5: Inverse-side context
# =====================================================================
print("Writing Task 5...")
with open(os.path.join(OUT_DIR, "task5_inverse_pairs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell_A","cell_A_status","cell_B_inverse","cell_B_status",
                "N_events_both_filled","pair_completion_rate_pct",
                "joint_pnl_when_paired","joint_variance",
                "solo_A_ev","solo_B_ev"])

    done_pairs = set()
    for cell_a in sorted(include_cells):
        cell_b = inverse_cell(cell_a)
        pk = tuple(sorted([cell_a, cell_b]))
        if pk in done_pairs: continue
        done_pairs.add(pk)

        a_status = "ACTIVE" if cell_a in active_cells else ("disabled" if cell_a in ALL_CELLS else "no_config")
        b_status = "ACTIVE" if cell_b in active_cells else ("disabled" if cell_b in ALL_CELLS else "no_config")

        # Find events where both sides filled into these cells
        joint_pnls = []
        a_only = []
        b_only = []
        for evt, sides in event_sides.items():
            a_side = [s for s in sides if s[0]==cell_a]
            b_side = [s for s in sides if s[0]==cell_b]
            if a_side and b_side:
                # Both filled
                a_ec = OPTIMAL_EXITS.get(cell_a, ALL_CELLS.get(cell_a,10))
                b_ec = OPTIMAL_EXITS.get(cell_b, ALL_CELLS.get(cell_b,10))
                a_entry, a_max = a_side[0][2], a_side[0][3]
                b_entry, b_max = b_side[0][2], b_side[0][3]
                a_tgt = min(99, a_entry+a_ec)
                b_tgt = min(99, b_entry+b_ec)
                a_scalped = a_max and a_max >= a_tgt
                b_scalped = b_max and b_max >= b_tgt
                a_pnl = a_ec*QTY/100 if a_scalped else ((99-a_entry)*QTY/100 if a_side[0][1]=="winner" else -(a_entry-1)*QTY/100)
                b_pnl = b_ec*QTY/100 if b_scalped else ((99-b_entry)*QTY/100 if b_side[0][1]=="winner" else -(b_entry-1)*QTY/100)
                joint_pnls.append(a_pnl + b_pnl)
            elif a_side:
                a_ec = OPTIMAL_EXITS.get(cell_a, ALL_CELLS.get(cell_a,10))
                a_entry, a_max = a_side[0][2], a_side[0][3]
                a_tgt = min(99, a_entry+a_ec)
                a_scalped = a_max and a_max >= a_tgt
                pnl = a_ec*QTY/100 if a_scalped else ((99-a_entry)*QTY/100 if a_side[0][1]=="winner" else -(a_entry-1)*QTY/100)
                a_only.append(pnl)
            elif b_side:
                b_ec = OPTIMAL_EXITS.get(cell_b, ALL_CELLS.get(cell_b,10))
                b_entry, b_max = b_side[0][2], b_side[0][3]
                b_tgt = min(99, b_entry+b_ec)
                b_scalped = b_max and b_max >= b_tgt
                pnl = b_ec*QTY/100 if b_scalped else ((99-b_entry)*QTY/100 if b_side[0][1]=="winner" else -(b_entry-1)*QTY/100)
                b_only.append(pnl)

        n_joint = len(joint_pnls)
        total_a = n_joint + len(a_only)
        total_b = n_joint + len(b_only)
        pair_rate = n_joint/max(total_a,total_b,1)*100

        j_mean = sum(joint_pnls)/n_joint if joint_pnls else 0
        j_var = sum((x-j_mean)**2 for x in joint_pnls)/n_joint if n_joint>1 else 0

        r_a = compute_ev_full(all_entries.get(cell_a,[]), OPTIMAL_EXITS.get(cell_a,ALL_CELLS.get(cell_a,10)))
        r_b = compute_ev_full(all_entries.get(cell_b,[]), OPTIMAL_EXITS.get(cell_b,ALL_CELLS.get(cell_b,10)))

        w.writerow([cell_a, a_status, cell_b, b_status,
                     n_joint, "%.1f"%pair_rate,
                     "%.3f"%j_mean if joint_pnls else "",
                     "%.3f"%j_var if joint_pnls else "",
                     "%.3f"%r_a["ev"] if r_a else "",
                     "%.3f"%r_b["ev"] if r_b else ""])

# =====================================================================
# TASK 6: Confidence-tiered breakdown
# =====================================================================
print("Writing Task 6...")
with open(os.path.join(OUT_DIR, "task6_confidence_tiers.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","confidence","N","optimal_exit","optimal_roi_pct",
                "optimal_ev_per_fill","optimal_daily_dollar",
                "ci_lower","ci_upper","current_exit","current_roi_also_positive"])

    tiers = {"HIGH":{"cells":0,"dd":0},"MED":{"cells":0,"dd":0},"LOW":{"cells":0,"dd":0}}

    for cell in sorted(include_cells):
        entries = all_entries.get(cell,[])
        if not entries: continue
        opt_ec = OPTIMAL_EXITS.get(cell, ALL_CELLS.get(cell,10))
        avg_e = sum(e["entry"] for e in entries)/len(entries)
        max_s = int(SCALP_CAP - avg_e)
        if opt_ec > max_s: opt_ec = max_s
        if opt_ec < 3: opt_ec = 3

        r_opt = compute_ev_full(entries, opt_ec)
        r_cur = compute_ev_full(entries, ALL_CELLS.get(cell,10))
        if not r_opt: continue

        cur_also_pos = r_cur["roi"]>0 if r_cur else False

        if r_opt["n"]>=50 and r_opt["ci_lo"]>0 and cur_also_pos:
            conf = "HIGH"
        elif r_opt["n"]>=20 and r_opt["ci_lo"]>-0.20:
            conf = "MED"
        else:
            conf = "LOW"

        tiers[conf]["cells"] += 1
        if r_opt["roi"]>0:
            tiers[conf]["dd"] += r_opt["dd"]

        w.writerow([cell, conf, r_opt["n"], opt_ec, "%.1f"%r_opt["roi"],
                     "%.4f"%r_opt["ev"], "%.4f"%r_opt["dd"],
                     "%.4f"%r_opt["ci_lo"], "%.4f"%r_opt["ci_hi"],
                     ALL_CELLS.get(cell,10), "YES" if cur_also_pos else "no"])

    # Append summary rows
    w.writerow([])
    w.writerow(["SUMMARY","","","","","","","","","",""])
    total_dd = sum(t["dd"] for t in tiers.values())
    for tier in ["HIGH","MED","LOW"]:
        pct = tiers[tier]["dd"]/total_dd*100 if total_dd else 0
        w.writerow(["TIER_%s"%tier, "", tiers[tier]["cells"], "", "",
                     "", "%.3f"%tiers[tier]["dd"], "", "", "",
                     "%.0f%% of total"%pct])

# =====================================================================
# TASK 7: Three-scenario re-projection per cell
# =====================================================================
print("Writing Task 7...")
with open(os.path.join(OUT_DIR, "task7_three_scenarios.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","current_exit","scenario_A_daily_dollar","optimal_exit",
                "scenario_B_daily_dollar","modest_exit","scenario_C_daily_dollar"])

    totals = {"A":0,"B":0,"C":0}
    for cell in sorted(include_cells):
        entries = all_entries.get(cell,[])
        if not entries: continue
        cur_ec = ALL_CELLS.get(cell,10)
        opt_ec = OPTIMAL_EXITS.get(cell, cur_ec)
        avg_e = sum(e["entry"] for e in entries)/len(entries)
        max_s = int(SCALP_CAP - avg_e)
        if opt_ec > max_s: opt_ec = max_s

        # Modest: current + 5c, capped at max_scalpable
        mod_ec = min(cur_ec + 5, max_s)
        if mod_ec < 3: mod_ec = 3

        r_a = compute_ev_full(entries, cur_ec)
        r_b = compute_ev_full(entries, opt_ec)
        r_c = compute_ev_full(entries, mod_ec)

        dd_a = r_a["dd"] if r_a and r_a["roi"]>0 else 0
        dd_b = r_b["dd"] if r_b and r_b["roi"]>0 else 0
        dd_c = r_c["dd"] if r_c and r_c["roi"]>0 else 0

        # Only count positive cells
        if r_a and r_a["roi"]>0: totals["A"] += dd_a
        if r_b and r_b["roi"]>0: totals["B"] += dd_b
        if r_c and r_c["roi"]>0: totals["C"] += dd_c

        w.writerow([cell, cur_ec, "%.4f"%dd_a if r_a else "",
                     opt_ec, "%.4f"%dd_b if r_b else "",
                     mod_ec, "%.4f"%dd_c if r_c else ""])

    w.writerow([])
    w.writerow(["TOTAL","","%.3f"%totals["A"],"","%.3f"%totals["B"],"","%.3f"%totals["C"]])

print()
print("=" * 60)
print("Files written to %s/:" % OUT_DIR)
for fn in sorted(os.listdir(OUT_DIR)):
    print("  %s (%.1f KB)" % (fn, os.path.getsize(os.path.join(OUT_DIR, fn))/1024))
print("=" * 60)
