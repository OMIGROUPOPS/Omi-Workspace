import sqlite3, csv, os
from collections import defaultdict

conn = sqlite3.connect('/root/Omi-Workspace/arb-executor/tennis.db')
cur = conn.cursor()

# matches has market_ticker (e.g. KXATPCHALLENGERMATCH-26APR01ALUMEJ-ALU)
# historical_events has event_ticker (e.g. KXATPCHALLENGERMATCH-26APR01ALUMEJ)
# We can join by stripping the side suffix from market_ticker

cur.execute("""SELECT market_ticker, entry_price, category, our_side, result, date
    FROM matches
    WHERE date >= '2026-03-20' AND date <= '2026-04-17'
    AND entry_price > 0 AND market_ticker IS NOT NULL""")

match_rows = cur.fetchall()
print("matches with market_ticker in window: %d" % len(match_rows))

# Extract event_ticker from market_ticker by removing last -XXX suffix
join_results = []
for mkt_tk, bot_entry, cat, our_side, result, date in match_rows:
    # market_ticker format: KXATPCHALLENGERMATCH-26APR01ALUMEJ-ALU
    # event_ticker format: KXATPCHALLENGERMATCH-26APR01ALUMEJ
    parts = mkt_tk.rsplit("-", 1)
    if len(parts) != 2:
        continue
    evt_tk = parts[0]
    side_code = parts[1]

    cur.execute("""SELECT first_price_winner, first_price_loser, winner, loser
        FROM historical_events WHERE event_ticker = ?""", (evt_tk,))
    row = cur.fetchone()
    if not row:
        continue

    fp_w, fp_l, winner_code, loser_code = row

    # Determine which side bot was on
    if side_code.upper() == (winner_code or "").upper():
        first_price = fp_w
        side = "winner"
    elif side_code.upper() == (loser_code or "").upper():
        first_price = fp_l
        side = "loser"
    else:
        continue

    if first_price is None or first_price <= 0:
        continue

    bias = bot_entry - first_price
    join_results.append({
        "evt": evt_tk, "mkt": mkt_tk, "bot_entry": bot_entry,
        "first_price": first_price, "bias": bias, "side": side,
        "cat": cat or "", "result": result, "side_code": side_code
    })

print("Matched with bias: %d" % len(join_results))

if not join_results:
    print("No matches found")
    conn.close()
    exit()

# Overall stats
biases = [r["bias"] for r in join_results]
avg_b = sum(biases) / len(biases)
std_b = (sum((x-avg_b)**2 for x in biases)/len(biases))**0.5
abs_b = sorted([abs(x) for x in biases])
print("\n=== OVERALL BIAS: bot_entry - first_price ===")
print("N: %d" % len(biases))
print("Mean: %+.1fc" % avg_b)
print("StdDev: %.1fc" % std_b)
print("Median abs: %.1fc" % abs_b[len(abs_b)//2])
print("P25 abs: %.1fc" % abs_b[len(abs_b)//4])
print("P75 abs: %.1fc" % abs_b[3*len(abs_b)//4])
print("P90 abs: %.1fc" % abs_b[int(len(abs_b)*0.9)])

# Distribution
print("\nBias distribution (bot_entry - first_price):")
for t in [-20, -10, -5, -3, -1, 0, 1, 3, 5, 10, 20]:
    c = sum(1 for b in biases if b <= t)
    print("  <= %+dc: %d (%.0f%%)" % (t, c, c/len(biases)*100))

# Cell classification impact
def classify(tier, price):
    d = "leader" if price >= 50 else "underdog"
    bs = int(price // 5) * 5
    return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

cell_mismatch = 0
dir_mismatch = 0
tier_map = {"ATP_CHALL":"ATP_CHALL","ATP_MAIN":"ATP_MAIN",
            "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}
for r in join_results:
    tier = tier_map.get(r["cat"])
    if not tier: continue
    c1 = classify(tier, r["first_price"])
    c2 = classify(tier, r["bot_entry"])
    if c1 != c2: cell_mismatch += 1
    if ("leader" in c1) != ("leader" in c2): dir_mismatch += 1

print("\nCell classification impact:")
print("  Cell mismatch: %d/%d (%.1f%%)" % (cell_mismatch, len(join_results), cell_mismatch/len(join_results)*100))
print("  Direction flip: %d/%d (%.1f%%)" % (dir_mismatch, len(join_results), dir_mismatch/len(join_results)*100))

# Per-cell bias
cell_biases = defaultdict(list)
for r in join_results:
    tier = tier_map.get(r["cat"])
    if not tier: continue
    cell = classify(tier, r["first_price"])
    cell_biases[cell].append(r["bias"])

OUT_DIR = "/tmp/per_cell_verification"

with open(os.path.join(OUT_DIR, "entry_price_bias_by_cell.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cell","N","mean_bias","stddev_bias","median_bias",
                 "pct_within_3c","pct_within_5c"])
    for cell in sorted(cell_biases.keys()):
        bs = cell_biases[cell]
        n = len(bs)
        if n < 3: continue
        mean_b = sum(bs)/n
        std_b = (sum((x-mean_b)**2 for x in bs)/n)**0.5
        med_b = sorted(bs)[n//2]
        w3 = sum(1 for x in bs if abs(x) <= 3)/n*100
        w5 = sum(1 for x in bs if abs(x) <= 5)/n*100
        w.writerow([cell, n, "%.1f"%mean_b, "%.1f"%std_b, "%.1f"%med_b,
                     "%.0f"%w3, "%.0f"%w5])

# Per-entry detail
with open(os.path.join(OUT_DIR, "entry_price_bias.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["event_ticker","market_ticker","side_code","bot_entry_price",
                "first_price_historical","bias_cents","side","category","result"])
    for r in sorted(join_results, key=lambda x: x["bias"]):
        w.writerow([r["evt"], r["mkt"], r["side_code"], r["bot_entry"],
                     r["first_price"], r["bias"], r["side"], r["cat"], r["result"]])

print("\nWritten: entry_price_bias.csv (%d rows)" % len(join_results))
print("Written: entry_price_bias_by_cell.csv")

conn.close()
