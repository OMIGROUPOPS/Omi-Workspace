import sqlite3, csv
from collections import defaultdict
from statistics import mean
from math import sqrt

bias_map = {}
with open("/tmp/per_cell_verification/entry_price_bias_by_cell.csv") as f:
    for r in csv.DictReader(f):
        n_late = int(r["N_late"])
        if n_late >= 10:
            bias_map[r["cell"]] = float(r["mean_bias_first_vs_late_mid"])

print("Loaded bias corrections for %d cells" % len(bias_map))

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
print("Loaded %d events from historical_events Jan-Apr" % len(rows))

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

cell_data = defaultdict(lambda: {
    "w_n":0, "w_scalp":0, "w_entries":[], "w_settle_prices":[],
    "l_n":0, "l_scalp":0, "l_entries":[]
})

for cat, fpw, maxw, lastw, fpl, maxl in rows:
    if cat not in cat_to_tier: continue
    raw_cell_w = classify(cat, fpw)
    if raw_cell_w:
        bias_w = bias_map.get(raw_cell_w, 0)
        corrected_fp_w = fpw - bias_w
        corrected_cell_w = classify(cat, corrected_fp_w)
        if corrected_cell_w:
            target = min(99, corrected_fp_w + EXIT_C)
            scalp = maxw is not None and maxw >= target
            cell_data[corrected_cell_w]["w_n"] += 1
            if scalp: cell_data[corrected_cell_w]["w_scalp"] += 1
            cell_data[corrected_cell_w]["w_entries"].append(corrected_fp_w)
            cell_data[corrected_cell_w]["w_settle_prices"].append(lastw or 99)
    raw_cell_l = classify(cat, fpl)
    if raw_cell_l:
        bias_l = bias_map.get(raw_cell_l, 0)
        corrected_fp_l = fpl - bias_l
        corrected_cell_l = classify(cat, corrected_fp_l)
        if corrected_cell_l:
            target = min(99, corrected_fp_l + EXIT_C)
            scalp = maxl is not None and maxl >= target
            cell_data[corrected_cell_l]["l_n"] += 1
            if scalp: cell_data[corrected_cell_l]["l_scalp"] += 1
            cell_data[corrected_cell_l]["l_entries"].append(corrected_fp_l)

results = []
for cell, d in cell_data.items():
    n_total = d["w_n"] + d["l_n"]
    if n_total < 20: continue
    avg_entry_w = mean(d["w_entries"]) if d["w_entries"] else 0
    avg_entry_l = mean(d["l_entries"]) if d["l_entries"] else 0
    avg_entry = (avg_entry_w * d["w_n"] + avg_entry_l * d["l_n"]) / n_total
    Sw = d["w_scalp"]/d["w_n"] if d["w_n"] else 0
    Sl = d["l_scalp"]/d["l_n"] if d["l_n"] else 0
    TWP = d["w_n"]/n_total
    distance_from_50 = abs(avg_entry - 50)
    target = min(99, avg_entry + EXIT_C)
    proximity = 99 - target

    scalp_p = EXIT_C * QTY / 100
    win_settle = (99 - avg_entry) * QTY / 100
    loss_settle = -(avg_entry - 1) * QTY / 100
    p1 = TWP * Sw * scalp_p
    p2 = TWP * (1-Sw) * win_settle
    p3 = (1-TWP) * Sl * scalp_p
    p4 = (1-TWP) * (1-Sl) * loss_settle
    total_ev = p1 + p2 + p3 + p4
    cost = avg_entry * QTY / 100
    decomp_roi = total_ev / cost * 100 if cost > 0 else 0

    per_event_pnls = []
    for entry in d["w_entries"]:
        sv = EXIT_C * QTY / 100
        wv = (99 - entry) * QTY / 100
        per_event_pnls.append(Sw * sv + (1-Sw) * wv)
    for entry in d["l_entries"]:
        sv = EXIT_C * QTY / 100
        lv = -(entry - 1) * QTY / 100
        per_event_pnls.append(Sl * sv + (1-Sl) * lv)
    if len(per_event_pnls) > 1:
        m = mean(per_event_pnls)
        v = sum((x-m)**2 for x in per_event_pnls) / (len(per_event_pnls) - 1)
        sd = sqrt(v)
        se = sd / sqrt(len(per_event_pnls))
        ci_low = (m - 1.96*se) / cost if cost > 0 else 0
        ci_high = (m + 1.96*se) / cost if cost > 0 else 0
    else:
        ci_low = ci_high = 0

    bias_used = bias_map.get(cell, 0)
    is_uncal = cell not in bias_map

    results.append({
        "cell":cell, "N":n_total, "N_winner":d["w_n"], "N_loser":d["l_n"],
        "avg_entry":"%.1f"%avg_entry, "bias_correction":"%.1f"%bias_used,
        "distance_from_50":"%.1f"%distance_from_50, "target_at_15c":"%.1f"%target,
        "proximity_to_settle":"%.1f"%proximity,
        "TWP":"%.3f"%TWP, "Sw":"%.3f"%Sw, "Sl":"%.3f"%Sl,
        "decomposed_ROI":"%.1f"%decomp_roi,
        "ci_low":"%.3f"%ci_low, "ci_high":"%.3f"%ci_high,
        "uncalibrated":is_uncal,
        "_decomp_roi_num":decomp_roi, "_dist":distance_from_50,
        "_Sl_num":Sl, "_prox":proximity, "_ci_low_num":ci_low,
        "_Sl_res_num":0, "_Sl_pred_num":0,
    })

filtered_for_fit = [r for r in results if r["_prox"] > 10 and int(r["N_loser"]) >= 30]
if len(filtered_for_fit) > 5:
    n_fit = len(filtered_for_fit)
    sum_x = sum(r["_dist"] for r in filtered_for_fit)
    sum_y = sum(r["_Sl_num"] for r in filtered_for_fit)
    sum_xx = sum(r["_dist"]**2 for r in filtered_for_fit)
    sum_xy = sum(r["_dist"]*r["_Sl_num"] for r in filtered_for_fit)
    b_coef = (n_fit*sum_xy - sum_x*sum_y) / (n_fit*sum_xx - sum_x**2)
    a_coef = (sum_y - b_coef*sum_x) / n_fit
    print("Sl baseline regression (clean cells, N=%d): Sl = %.3f + %.4f * distance_from_50" % (n_fit, a_coef, b_coef))
else:
    a_coef, b_coef = 0.5, 0
    print("Insufficient cells for regression")

for r in results:
    sl_pred = a_coef + b_coef * r["_dist"]
    sl_res = r["_Sl_num"] - sl_pred
    r["Sl_predicted"] = "%.3f" % sl_pred
    r["Sl_residual"] = "%.3f" % sl_res
    r["_Sl_res_num"] = sl_res
    r["_Sl_pred_num"] = sl_pred

    if r["uncalibrated"]:
        r["mechanism"] = "UNCALIBRATED"
    elif r["_prox"] <= 2:
        r["mechanism"] = "SETTLEMENT_RIDE_CONTAMINATED"
    elif r["_prox"] <= 5:
        r["mechanism"] = "SETTLEMENT_RIDE"
    elif r["_prox"] <= 10:
        r["mechanism"] = "MIXED_EDGE" if r["_ci_low_num"] > 0 else "MIXED_BREAK_EVEN"
    else:
        if sl_res > 0.05 and r["_ci_low_num"] > 0:
            r["mechanism"] = "SCALPER_EDGE"
        elif sl_res < -0.05:
            r["mechanism"] = "SCALPER_NEGATIVE"
        else:
            r["mechanism"] = "SCALPER_BREAK_EVEN"

cols = ["cell","N","N_winner","N_loser","avg_entry","bias_correction","distance_from_50",
        "target_at_15c","proximity_to_settle","TWP","Sw","Sl","Sl_predicted","Sl_residual",
        "decomposed_ROI","ci_low","ci_high","mechanism","uncalibrated"]
with open("/tmp/rebuilt_scorecard.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in sorted(results, key=lambda x: -x["_decomp_roi_num"]):
        w.writerow(r)

print("\nTotal cells with N >= 20: %d" % len(results))
from collections import Counter
mech_counts = Counter(r["mechanism"] for r in results)
print("By mechanism:")
for m, c in sorted(mech_counts.items()):
    print("  %s: %d" % (m, c))

print("\nSCALPER_EDGE cells:")
for r in sorted(results, key=lambda x: -x["_decomp_roi_num"]):
    if r["mechanism"] == "SCALPER_EDGE":
        print("  %-30s N=%-4d ROI=%+.1f%% Sl=%.0f%% Sl_res=%+.1fpp CI[%+.2f, %+.2f]" % (
            r["cell"], r["N"], r["_decomp_roi_num"], r["_Sl_num"]*100, r["_Sl_res_num"]*100,
            r["_ci_low_num"], float(r["ci_high"])))

print("\nSETTLEMENT_RIDE cells:")
for r in sorted(results, key=lambda x: -x["_decomp_roi_num"]):
    if r["mechanism"].startswith("SETTLEMENT_RIDE"):
        print("  %-30s N=%-4d ROI=%+.1f%% TWP=%.0f%% prox=%.1fc" % (
            r["cell"], r["N"], r["_decomp_roi_num"], float(r["TWP"])*100, r["_prox"]))

print("\nSCALPER_NEGATIVE cells:")
for r in sorted(results, key=lambda x: x["_decomp_roi_num"]):
    if r["mechanism"] == "SCALPER_NEGATIVE":
        print("  %-30s N=%-4d ROI=%+.1f%% Sl=%.0f%% Sl_res=%+.1fpp" % (
            r["cell"], r["N"], r["_decomp_roi_num"], r["_Sl_num"]*100, r["_Sl_res_num"]*100))

print("\nUNCALIBRATED:")
for r in results:
    if r["mechanism"] == "UNCALIBRATED":
        print("  %-30s N=%-4d ROI=%+.1f%%" % (r["cell"], r["N"], r["_decomp_roi_num"]))

print("\nFile written: /tmp/rebuilt_scorecard.csv")
