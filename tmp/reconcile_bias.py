#!/usr/bin/env python3
"""
Q1: Per-cell real economics in % of cost basis
Q2: Reconcile bias contradiction — per-fill first_price lookup
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

# Load fills + outcomes (same as real_economics.py)
fills = []
exits = []
settlements = []
for lf in sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl"))):
    with open(lf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except: continue
            ev = d.get("event","")
            det = d.get("details",{})
            tk = d.get("ticker","")
            if ev == "entry_filled":
                fills.append({"ticker":tk,"fill_price":det.get("fill_price",0),
                    "cell":det.get("cell",""),"ts":d.get("ts","")})
            elif ev in ("exit_filled","scalp_filled"):
                exits.append({"ticker":tk,"pnl_cents":det.get("pnl_cents",det.get("profit_cents",0)),"type":ev})
            elif ev == "settled":
                settlements.append({"ticker":tk,"result":det.get("settle",""),
                    "pnl_cents":det.get("pnl_cents",0)})

seen = set()
exit_map = {}
for e in exits:
    if e["ticker"] not in seen:
        seen.add(e["ticker"])
        exit_map[e["ticker"]] = e

seen = set()
settle_map = {}
for s in settlements:
    if s["ticker"] not in seen:
        seen.add(s["ticker"])
        settle_map[s["ticker"]] = s

conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()

# Check historical_events date range
cur.execute("SELECT min(first_ts), max(first_ts), count(*) FROM historical_events")
he_range = cur.fetchone()
print("historical_events range: %s to %s (%d rows)" % he_range)

# Q2: For each of 130 fills, look up first_price
print("\n=== Q2: PER-FILL FIRST_PRICE LOOKUP ===\n")

q2_rows = []
found_count = 0
not_found_count = 0
mismatch_count = 0

for f in fills:
    tk = f["ticker"]
    fill_price = f["fill_price"]
    tier = get_tier(tk)
    if not tier: continue

    parts = tk.rsplit("-", 1)
    if len(parts) != 2: continue
    evt_tk = parts[0]
    side_code = parts[1]

    cur.execute("SELECT first_price_winner, first_price_loser, winner, loser, first_ts FROM historical_events WHERE event_ticker = ?",
                (evt_tk,))
    row = cur.fetchone()

    first_price = None
    he_exists = False
    he_first_ts = ""
    if row:
        he_exists = True
        fp_w, fp_l, winner, loser, first_ts = row
        he_first_ts = first_ts or ""
        if side_code.upper() == (winner or "").upper():
            first_price = fp_w
        elif side_code.upper() == (loser or "").upper():
            first_price = fp_l

    cell_by_fill = classify_cell(tier, fill_price)
    cell_by_fp = classify_cell(tier, first_price) if first_price and first_price > 0 else ""
    match = cell_by_fill == cell_by_fp if cell_by_fp else None
    bias = fill_price - first_price if first_price and first_price > 0 else None

    if he_exists and first_price and first_price > 0:
        found_count += 1
        if not match:
            mismatch_count += 1
    else:
        not_found_count += 1

    q2_rows.append({
        "ticker": tk, "fill_price": fill_price, "first_price": first_price,
        "bias": bias, "he_exists": he_exists, "he_first_ts": he_first_ts,
        "cell_by_fill": cell_by_fill, "cell_by_fp": cell_by_fp,
        "match": match, "cell_at_fill_time": f["cell"],
    })

print("Total fills: %d" % len(q2_rows))
print("Found in historical_events: %d" % found_count)
print("NOT found in historical_events: %d" % not_found_count)
print("Cell mismatches (where found): %d" % mismatch_count)

# Write Q2 CSV
with open(os.path.join(OUT_DIR, "per_fill_first_price_lookup.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker","fill_price","first_price","bias","in_historical_events",
                "he_first_ts","cell_by_fill_price","cell_by_first_price",
                "cell_match","cell_at_fill_time_from_bot"])
    for r in q2_rows:
        w.writerow([r["ticker"], r["fill_price"],
                     r["first_price"] if r["first_price"] else "",
                     "%.0f" % r["bias"] if r["bias"] is not None else "",
                     "YES" if r["he_exists"] else "NO",
                     r["he_first_ts"][:10] if r["he_first_ts"] else "",
                     r["cell_by_fill"], r["cell_by_fp"],
                     "YES" if r["match"] == True else ("NO" if r["match"] == False else "N/A"),
                     r["cell_at_fill_time"]])

# Show mismatches explicitly
if mismatch_count > 0:
    print("\n=== MISMATCHES ===")
    for r in q2_rows:
        if r["match"] == False:
            print("  %s: fill=%dc fp=%dc bias=%+dc cell_fill=%s cell_fp=%s" % (
                r["ticker"][-25:], r["fill_price"], r["first_price"], r["bias"],
                r["cell_by_fill"], r["cell_by_fp"]))

# Show the found ones with bias
if found_count > 0:
    biases = [r["bias"] for r in q2_rows if r["bias"] is not None]
    avg_b = sum(biases)/len(biases)
    abs_b = sorted([abs(b) for b in biases])
    print("\n=== BIAS ON %d FOUND FILLS ===" % found_count)
    print("Mean bias: %+.1fc" % avg_b)
    print("Median abs: %.1fc" % abs_b[len(abs_b)//2])
    print("Pct within 3c: %.0f%%" % (sum(1 for b in biases if abs(b) <= 3)/len(biases)*100))

# Why are fills not in historical_events?
print("\n=== WHY FILLS NOT FOUND ===")
for r in q2_rows:
    if not r["he_exists"]:
        # Extract date from ticker
        parts = r["ticker"].split("-")
        if len(parts) >= 2:
            date_part = parts[1]  # e.g. 26APR24ERESTE
            print("  %s (date_code=%s, fill=%dc)" % (r["ticker"][-30:], date_part[:7], r["fill_price"]))
        break  # just show first one

# Check: what's the latest date in historical_events?
cur.execute("SELECT max(first_ts) FROM historical_events")
print("\nLatest historical_events first_ts: %s" % cur.fetchone()[0])
print("Live fills start at: %s" % fills[0]["ts"] if fills else "?")

conn.close()

# Q1: Real economics in % of cost basis
print("\n=== Q1: REAL ECONOMICS IN % OF COST BASIS ===\n")

# Load analysis corrected scorecard for comparison
analysis = {}
scorecard = "/tmp/corrected_analysis/corrected_scorecard.csv"
if os.path.exists(scorecard):
    with open(scorecard) as f:
        for row in csv.DictReader(f):
            analysis[row["cell"]] = {
                "ev": float(row["EV_per_event"]),
                "avg_e": float(row["avg_entry"]),
                "cost": float(row["cost_basis"]),
            }

# Build per-cell from fills
cell_data = defaultdict(lambda: {"fills":0,"pnl_total":0,"fill_prices":[],"pnl_list":[]})
DAYS = 10
QTY = 10

for f in fills:
    tk = f["ticker"]
    fp = f["fill_price"]
    tier = get_tier(tk)
    if not tier: continue
    cell = classify_cell(tier, fp)

    pnl_cents = 0
    if tk in exit_map:
        pnl_cents = exit_map[tk]["pnl_cents"]
    elif tk in settle_map:
        pnl_cents = settle_map[tk]["pnl_cents"]

    pnl_dollars = pnl_cents * QTY / 100
    cell_data[cell]["fills"] += 1
    cell_data[cell]["fill_prices"].append(fp)
    cell_data[cell]["pnl_total"] += pnl_dollars
    cell_data[cell]["pnl_list"].append(pnl_dollars)

with open(os.path.join(OUT_DIR, "real_economics_pct.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N","avg_fill_price","cost_basis","real_pnl_per_fill_pct",
                "real_daily_pct_return","analysis_pnl_per_fill_pct","delta_pct"])

    for cell in sorted(cell_data.keys()):
        d = cell_data[cell]
        n = d["fills"]
        avg_fp = sum(d["fill_prices"])/n
        cost = avg_fp * QTY / 100
        avg_pnl = d["pnl_total"]/n
        real_pct = avg_pnl / cost * 100 if cost else 0
        daily_pct = real_pct * (n/DAYS) / 100

        an = analysis.get(cell)
        if an and an["cost"] > 0:
            an_pct = an["ev"] / an["cost"] * 100
        else:
            an_pct = None

        delta = real_pct - an_pct if an_pct is not None else None

        w.writerow([cell, n, "%.1f"%avg_fp, "%.2f"%cost,
                     "%.1f"%real_pct,
                     "%.4f"%daily_pct,
                     "%.1f"%an_pct if an_pct is not None else "",
                     "%.1f"%delta if delta is not None else ""])

print("Written: real_economics_pct.csv, per_fill_first_price_lookup.csv")
