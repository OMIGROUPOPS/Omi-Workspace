#!/usr/bin/env python3
"""
Per-cell economics from ACTUAL bot fills (129 live log events, Apr 17-28).
Ground truth: real fill prices, real outcomes, real P&L.
"""
import sqlite3, json, csv, os, glob
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

def get_tier(tk):
    if "KXATPMATCH" in tk and "CHALL" not in tk: return "ATP_MAIN"
    if "KXWTAMATCH" in tk and "CHALL" not in tk: return "WTA_MAIN"
    if "KXATPCHALL" in tk: return "ATP_CHALL"
    if "KXWTACHALL" in tk: return "WTA_CHALL"
    return None

# Load ALL live log events
log_files = sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl")))

fills = []        # entry_filled
exits = []        # exit_filled / scalp_filled
settlements = []  # settled

for lf in log_files:
    with open(lf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except:
                continue
            ev = d.get("event", "")
            det = d.get("details", {})
            tk = d.get("ticker", "")
            ts = d.get("ts", "")

            if ev == "entry_filled":
                fills.append({
                    "ticker": tk, "ts": ts,
                    "fill_price": det.get("fill_price", 0),
                    "qty": det.get("qty", 0),
                    "cell_at_fill": det.get("cell", ""),
                    "direction": det.get("direction", ""),
                })
            elif ev in ("exit_filled", "scalp_filled"):
                exits.append({
                    "ticker": tk, "ts": ts,
                    "exit_price": det.get("exit_price", 0),
                    "entry_price": det.get("entry_price", 0),
                    "pnl_cents": det.get("pnl_cents", det.get("profit_cents", 0)),
                    "type": ev,
                })
            elif ev == "settled":
                settlements.append({
                    "ticker": tk, "ts": ts,
                    "result": det.get("settle", ""),
                    "settle_price": det.get("settle_price", 0),
                    "entry_price": det.get("entry_price", 0),
                    "pnl_cents": det.get("pnl_cents", 0),
                    "pnl_dollars": det.get("pnl_dollars", 0),
                })

print("Fills: %d, Exits: %d, Settlements: %d" % (len(fills), len(exits), len(settlements)))

# Deduplicate exits and settlements by ticker (take first occurrence)
seen = set()
deduped_exits = []
for e in exits:
    if e["ticker"] not in seen:
        seen.add(e["ticker"])
        deduped_exits.append(e)

seen = set()
deduped_settlements = []
for s in settlements:
    if s["ticker"] not in seen:
        seen.add(s["ticker"])
        deduped_settlements.append(s)

print("Deduped exits: %d, Deduped settlements: %d" % (len(deduped_exits), len(deduped_settlements)))

# Build outcome map: ticker -> outcome
exit_map = {e["ticker"]: e for e in deduped_exits}
settle_map = {s["ticker"]: s for s in deduped_settlements}

# Load historical_events for first_price comparison
conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()

# For each fill, determine:
# 1. Cell by actual fill price
# 2. Cell by first_price (what analysis used)
# 3. Outcome (scalp, settle win, settle loss)
# 4. Real P&L

results = []
for f in fills:
    tk = f["ticker"]
    fill_price = f["fill_price"]
    tier = get_tier(tk)
    if not tier:
        continue

    cell_actual = classify_cell(tier, fill_price)
    cell_at_fill = f["cell_at_fill"]  # what bot classified at fill time

    # Look up first_price from historical_events
    parts = tk.rsplit("-", 1)
    if len(parts) != 2:
        continue
    evt_tk = parts[0]
    side_code = parts[1]

    cur.execute("SELECT first_price_winner, first_price_loser, winner, loser FROM historical_events WHERE event_ticker = ?",
                (evt_tk,))
    row = cur.fetchone()
    first_price = None
    cell_by_fp = None
    if row:
        fp_w, fp_l, winner, loser = row
        if side_code.upper() == (winner or "").upper():
            first_price = fp_w
        elif side_code.upper() == (loser or "").upper():
            first_price = fp_l
        if first_price and first_price > 0:
            cell_by_fp = classify_cell(tier, first_price)

    # Determine outcome
    outcome = "unknown"
    pnl_cents = 0
    exit_price = 0

    if tk in exit_map:
        e = exit_map[tk]
        outcome = "scalp"
        pnl_cents = e["pnl_cents"]
        exit_price = e["exit_price"]
    elif tk in settle_map:
        s = settle_map[tk]
        outcome = "settle_win" if s["result"] == "WIN" else "settle_loss"
        pnl_cents = s["pnl_cents"]
        exit_price = s["settle_price"]

    # P&L in dollars (for 10ct position)
    if pnl_cents:
        pnl_dollars = pnl_cents * 10 / 100  # pnl_cents is per contract
    else:
        pnl_dollars = 0

    results.append({
        "ticker": tk, "fill_price": fill_price, "qty": f["qty"],
        "cell_actual": cell_actual, "cell_at_fill": cell_at_fill,
        "cell_by_first_price": cell_by_fp or "",
        "first_price": first_price or 0,
        "bias": fill_price - first_price if first_price else None,
        "outcome": outcome, "exit_price": exit_price,
        "pnl_cents": pnl_cents, "pnl_dollars": pnl_dollars,
        "direction": f["direction"], "ts": f["ts"],
    })

conn.close()
print("Results with outcomes: %d" % len(results))

# Write per-fill detail
with open(os.path.join(OUT_DIR, "real_per_fill.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","fill_price","first_price","bias","cell_actual","cell_at_fill",
                "cell_by_first_price","cell_mismatch","outcome","exit_price",
                "pnl_cents","pnl_dollars","direction","ts"])
    for r in results:
        mismatch = r["cell_actual"] != r["cell_by_first_price"] if r["cell_by_first_price"] else ""
        w.writerow([r["ticker"], r["fill_price"], r["first_price"],
                     r["bias"] if r["bias"] is not None else "",
                     r["cell_actual"], r["cell_at_fill"], r["cell_by_first_price"],
                     mismatch, r["outcome"], r["exit_price"],
                     r["pnl_cents"], "%.2f" % r["pnl_dollars"],
                     r["direction"], r["ts"]])

# Aggregate by cell (using ACTUAL fill price classification)
cell_real = defaultdict(lambda: {"fills": 0, "scalps": 0, "settle_w": 0, "settle_l": 0,
    "unknown": 0, "pnl_total": 0, "fill_prices": [], "pnl_list": []})

for r in results:
    c = r["cell_actual"]
    cell_real[c]["fills"] += 1
    cell_real[c]["fill_prices"].append(r["fill_price"])
    cell_real[c]["pnl_total"] += r["pnl_dollars"]
    cell_real[c]["pnl_list"].append(r["pnl_dollars"])
    if r["outcome"] == "scalp": cell_real[c]["scalps"] += 1
    elif r["outcome"] == "settle_win": cell_real[c]["settle_w"] += 1
    elif r["outcome"] == "settle_loss": cell_real[c]["settle_l"] += 1
    else: cell_real[c]["unknown"] += 1

DAYS = 10  # Apr 17-28

with open(os.path.join(OUT_DIR, "per_cell_real_economics.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N_fills","avg_fill_price","scalps","settle_wins","settle_losses",
                "unknown","scalp_WR_pct","settle_WR_pct","total_pnl_dollars","avg_pnl_per_fill",
                "daily_fills","daily_pnl","stddev_per_fill"])
    for cell in sorted(cell_real.keys()):
        d = cell_real[cell]
        n = d["fills"]
        avg_fp = sum(d["fill_prices"]) / n
        resolved = d["scalps"] + d["settle_w"] + d["settle_l"]
        scalp_wr = d["scalps"] / resolved * 100 if resolved else 0
        settle_wr = d["settle_w"] / resolved * 100 if resolved else 0
        avg_pnl = d["pnl_total"] / n
        daily_f = n / DAYS
        daily_pnl = d["pnl_total"] / DAYS
        pnls = d["pnl_list"]
        std = (sum((x - avg_pnl)**2 for x in pnls) / n)**0.5 if n > 1 else 0

        w.writerow([cell, n, "%.1f" % avg_fp, d["scalps"], d["settle_w"], d["settle_l"],
                     d["unknown"], "%.0f" % scalp_wr, "%.0f" % settle_wr,
                     "%.2f" % d["pnl_total"], "%.2f" % avg_pnl,
                     "%.1f" % daily_f, "%.2f" % daily_pnl, "%.2f" % std])

# Comparison: real vs analysis
# Load analysis projections (corrected scorecard)
analysis = {}
scorecard = "/tmp/corrected_analysis/corrected_scorecard.csv"
if os.path.exists(scorecard):
    with open(scorecard) as f:
        for row in csv.DictReader(f):
            analysis[row["cell"]] = {
                "roi": float(row["ROI_pct"]),
                "ev": float(row["EV_per_event"]),
                "Sl": float(row["Sl"]),
                "Sw": float(row["Sw"]),
            }

with open(os.path.join(OUT_DIR, "comparison_real_vs_analysis.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","real_N","real_avg_fill","real_scalp_WR","real_pnl_per_fill",
                "real_daily_pnl","analysis_ROI","analysis_EV_per_fill","analysis_Sl",
                "delta_pnl_per_fill","assessment"])

    all_cells = sorted(set(list(cell_real.keys()) + list(analysis.keys())))
    for cell in all_cells:
        cr = cell_real.get(cell)
        an = analysis.get(cell)

        real_n = cr["fills"] if cr else 0
        real_avg = sum(cr["fill_prices"])/cr["fills"] if cr and cr["fills"] else 0
        real_sr = cr["scalps"]/(cr["scalps"]+cr["settle_w"]+cr["settle_l"])*100 if cr and (cr["scalps"]+cr["settle_w"]+cr["settle_l"]) else 0
        real_pnl_per = cr["pnl_total"]/cr["fills"] if cr and cr["fills"] else 0
        real_daily = cr["pnl_total"]/DAYS if cr else 0
        an_roi = an["roi"] if an else ""
        an_ev = an["ev"] if an else ""
        an_sl = an["Sl"] if an else ""
        delta = real_pnl_per - float(an_ev) if an and cr and cr["fills"] else ""

        if real_n == 0 and not an:
            continue
        if real_n == 0:
            assessment = "NO_LIVE_DATA"
        elif real_n < 3:
            assessment = "TOO_FEW_FILLS"
        elif not an:
            assessment = "NOT_IN_ANALYSIS"
        elif isinstance(delta, float) and delta > 0.5:
            assessment = "REAL_BETTER"
        elif isinstance(delta, float) and delta < -0.5:
            assessment = "REAL_WORSE"
        else:
            assessment = "CONSISTENT"

        w.writerow([cell, real_n, "%.1f" % real_avg if real_n else "",
                     "%.0f" % real_sr if real_n else "", "%.2f" % real_pnl_per if real_n else "",
                     "%.2f" % real_daily if real_n else "",
                     "%.1f" % an_roi if an else "", "%.3f" % an_ev if an else "",
                     "%.3f" % an_sl if an else "",
                     "%.2f" % delta if isinstance(delta, float) else "",
                     assessment])

# Print summary
print("\n=== REAL ECONOMICS SUMMARY ===")
print("| Cell | N | Avg fill | Scalps | SW | SL | PnL$ | $/fill | $/day |")
print("|---|---|---|---|---|---|---|---|---|")
for cell in sorted(cell_real.keys()):
    d = cell_real[cell]
    n = d["fills"]
    avg_fp = sum(d["fill_prices"])/n
    avg_pnl = d["pnl_total"]/n
    daily = d["pnl_total"]/DAYS
    print("| %s | %d | %.0f | %d | %d | %d | $%.2f | $%.2f | $%.2f |" % (
        cell, n, avg_fp, d["scalps"], d["settle_w"], d["settle_l"],
        d["pnl_total"], avg_pnl, daily))

total_pnl = sum(d["pnl_total"] for d in cell_real.values())
total_fills = sum(d["fills"] for d in cell_real.values())
print("\nTotal: %d fills, $%.2f total P&L, $%.2f/day" % (total_fills, total_pnl, total_pnl/DAYS))

# Cell mismatch summary
mismatches = [r for r in results if r["cell_by_first_price"] and r["cell_actual"] != r["cell_by_first_price"]]
print("\nCell mismatches (actual fill cell != first_price cell): %d/%d (%.0f%%)" % (
    len(mismatches), len(results), len(mismatches)/len(results)*100 if results else 0))

print("\nWritten: real_per_fill.csv, per_cell_real_economics.csv, comparison_real_vs_analysis.csv")
