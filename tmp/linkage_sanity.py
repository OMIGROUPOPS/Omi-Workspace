import sqlite3, json, csv, os, glob
from collections import defaultdict

BASE_DIR = "/root/Omi-Workspace/arb-executor"
OUT_DIR = "/tmp/per_cell_verification"

def classify_cell(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

conn = sqlite3.connect(os.path.join(BASE_DIR, "tennis.db"))
cur = conn.cursor()

# Part 1: From matches table (361 unambiguous links)
# Join and classify each into cells, then pick one per target cell
target_cells = [
    "ATP_CHALL_leader_70-74",
    "ATP_CHALL_leader_60-64",
    "ATP_CHALL_underdog_45-49",
    "ATP_MAIN_leader_70-74",
    "WTA_MAIN_leader_50-54",
]

cur.execute("""
    SELECT m.id, m.date, m.category, m.our_side, m.entry_price, m.result,
           m.settlement_time, m.pnl_cents,
           h.event_ticker, h.winner, h.loser,
           h.first_price_winner, h.first_price_loser,
           h.first_ts
    FROM matches m, historical_events h
    WHERE m.date >= '2026-03-20' AND m.entry_price > 0
    AND m.category = h.category
    AND (m.our_side = h.winner OR m.our_side = h.loser)
    AND substr(h.first_ts, 1, 10) = m.date
""")

# Group by match id
match_links = defaultdict(list)
for row in cur.fetchall():
    match_links[row[0]].append(row)

# Filter to unambiguous only, classify into cells
matches_by_cell = defaultdict(list)
for mid, links in match_links.items():
    if len(links) != 1: continue
    row = links[0]
    cat = row[2]
    our_side = row[3]
    bot_entry = row[4]
    winner = row[9]
    loser = row[10]
    fp_w = row[11]
    fp_l = row[12]

    if our_side == winner:
        first_price = fp_w
        side = "winner"
    elif our_side == loser:
        first_price = fp_l
        side = "loser"
    else:
        continue

    if not first_price or first_price <= 0: continue

    tier_map = {"ATP_CHALL":"ATP_CHALL","ATP_MAIN":"ATP_MAIN",
                "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}
    tier = tier_map.get(cat)
    if not tier: continue

    # Classify by first_price (as analyses do)
    cell_fp = classify_cell(tier, first_price)
    # Classify by bot_entry (what the bot actually experienced)
    cell_bot = classify_cell(tier, bot_entry)

    evt_ticker = row[8]
    # Construct market ticker
    mkt_ticker = evt_ticker + "-" + our_side

    matches_by_cell[cell_fp].append({
        "source": "matches_table",
        "ticker": mkt_ticker, "event_ticker": evt_ticker,
        "our_side": our_side, "date": row[1],
        "bot_entry": bot_entry, "first_price": first_price,
        "bias": bot_entry - first_price,
        "side": side, "result": row[5],
        "cell_by_first_price": cell_fp, "cell_by_bot_entry": cell_bot,
        "cell_mismatch": cell_fp != cell_bot,
        "settlement_time": row[6],
    })

# Pick one per target cell
selected = []
for target in target_cells:
    candidates = matches_by_cell.get(target, [])
    if candidates:
        # Pick one with non-zero bias for interesting example
        pick = sorted(candidates, key=lambda x: abs(x["bias"]), reverse=True)[0]
        selected.append(pick)
    else:
        # Try bot-entry classification
        for cell, entries in matches_by_cell.items():
            for e in entries:
                if e["cell_by_bot_entry"] == target:
                    selected.append(e)
                    break
            if len(selected) > len([s for s in selected if s not in selected]):
                break

print("Part 1: Selected %d matches from matches table" % len(selected))
for s in selected:
    print("  %s | side=%s bot=%dc fp=%dc bias=%+dc cell_fp=%s cell_bot=%s %s" % (
        s["ticker"][-25:], s["side"], s["bot_entry"], s["first_price"],
        s["bias"], s["cell_by_first_price"], s["cell_by_bot_entry"],
        "MISMATCH" if s["cell_mismatch"] else ""))

# Part 2: From live logs (129 entry_filled events)
print("\nPart 2: Live log fills")
log_files = sorted(glob.glob(os.path.join(BASE_DIR, "logs/live_v3_*.jsonl")))

live_fills = []
for lf in log_files:
    with open(lf) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                if d.get("event") == "entry_filled":
                    det = d.get("details", {})
                    live_fills.append({
                        "ticker": d.get("ticker", ""),
                        "cell": det.get("cell", ""),
                        "fill_price": det.get("fill_price", 0),
                        "ts": d.get("ts", ""),
                    })
            except:
                continue

print("Total live fills: %d" % len(live_fills))

# For each live fill, look up first_price from historical_events
live_selected = []
live_by_cell = defaultdict(list)

for lf in live_fills:
    tk = lf["ticker"]
    # Extract event_ticker: remove last -XXX
    parts = tk.rsplit("-", 1)
    if len(parts) != 2: continue
    evt_tk = parts[0]
    side_code = parts[1]

    cur.execute("SELECT first_price_winner, first_price_loser, winner, loser FROM historical_events WHERE event_ticker = ?",
                (evt_tk,))
    row = cur.fetchone()
    if not row: continue

    fp_w, fp_l, winner, loser = row
    if side_code.upper() == (winner or "").upper():
        first_price = fp_w
        side = "winner"
    elif side_code.upper() == (loser or "").upper():
        first_price = fp_l
        side = "loser"
    else:
        continue

    if not first_price or first_price <= 0: continue

    cell = lf["cell"]
    bias = lf["fill_price"] - first_price

    entry = {
        "source": "live_log",
        "ticker": tk, "event_ticker": evt_tk,
        "our_side": side_code, "date": lf["ts"][:10] if lf["ts"] else "",
        "bot_entry": lf["fill_price"], "first_price": first_price,
        "bias": bias, "side": side, "result": "",
        "cell_by_first_price": cell,  # live log already has cell
        "cell_by_bot_entry": cell,
        "cell_mismatch": False,
        "settlement_time": "",
    }
    live_by_cell[cell].append(entry)

# Pick one per target cell from live fills
for target in target_cells:
    candidates = live_by_cell.get(target, [])
    if candidates:
        live_selected.append(candidates[0])

print("Selected %d live fills for target cells" % len(live_selected))
for s in live_selected:
    print("  %s | side=%s fill=%dc fp=%dc bias=%+dc cell=%s" % (
        s["ticker"][-25:], s["side"], s["bot_entry"], s["first_price"],
        s["bias"], s["cell_by_first_price"]))

# Also: per-cell bias from all 361 unambiguous matches
print("\n=== Per-cell bias from matches table (all 361) ===")
print("| Cell | N | Mean bias | Median | StdDev | Pct within 5c |")
print("|---|---|---|---|---|---|")
all_biases_by_cell = defaultdict(list)
for cell, entries in matches_by_cell.items():
    for e in entries:
        all_biases_by_cell[cell].append(e["bias"])

for cell in sorted(all_biases_by_cell.keys()):
    bs = all_biases_by_cell[cell]
    n = len(bs)
    if n < 3: continue
    avg = sum(bs)/n
    std = (sum((x-avg)**2 for x in bs)/n)**0.5
    med = sorted(bs)[n//2]
    w5 = sum(1 for x in bs if abs(x) <= 5)/n*100
    print("| %s | %d | %+.1f | %+.1f | %.1f | %.0f%% |" % (cell, n, avg, med, std, w5))

# Write combined CSV
all_selected = selected + live_selected
with open(os.path.join(OUT_DIR, "linkage_sanity_check.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source","ticker","event_ticker","our_side","date",
                "bot_entry_price","first_price_historical","bias_cents",
                "side","result","cell_by_first_price","cell_by_bot_entry","cell_mismatch"])
    for s in all_selected:
        w.writerow([s["source"], s["ticker"], s["event_ticker"], s["our_side"],
                     s["date"], s["bot_entry"], s["first_price"], s["bias"],
                     s["side"], s["result"], s["cell_by_first_price"],
                     s["cell_by_bot_entry"], s["cell_mismatch"]])

# Also write full per-cell bias summary
with open(os.path.join(OUT_DIR, "bias_by_cell_from_matches.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N","mean_bias","median_bias","stddev","pct_within_3c","pct_within_5c",
                "pct_bot_higher","pct_cell_mismatch"])
    for cell in sorted(all_biases_by_cell.keys()):
        bs = all_biases_by_cell[cell]
        n = len(bs)
        if n < 3: continue
        avg = sum(bs)/n
        std = (sum((x-avg)**2 for x in bs)/n)**0.5
        med = sorted(bs)[n//2]
        w3 = sum(1 for x in bs if abs(x) <= 3)/n*100
        w5 = sum(1 for x in bs if abs(x) <= 5)/n*100
        higher = sum(1 for x in bs if x > 0)/n*100
        # Cell mismatch rate
        entries = matches_by_cell[cell]
        mm = sum(1 for e in entries if e["cell_mismatch"])/len(entries)*100
        w.writerow([cell, n, "%.1f"%avg, "%.1f"%med, "%.1f"%std,
                     "%.0f"%w3, "%.0f"%w5, "%.0f"%higher, "%.0f"%mm])

print("\nWritten: linkage_sanity_check.csv, bias_by_cell_from_matches.csv")
conn.close()
