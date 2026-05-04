import sqlite3, csv, os
from collections import defaultdict

conn = sqlite3.connect('/root/Omi-Workspace/arb-executor/tennis.db')
cur = conn.cursor()

# Check matches table coverage
cur.execute("SELECT count(*), count(event_ticker), count(market_ticker) FROM matches WHERE entry_price > 0")
print("matches linkage (total, has_event_ticker, has_market_ticker):", cur.fetchone())

cur.execute("SELECT count(*) FROM matches WHERE date >= '2026-03-20' AND date <= '2026-04-17' AND entry_price > 0")
print("Matches in backtest window:", cur.fetchone())

cur.execute("SELECT count(*) FROM matches WHERE date >= '2026-03-20' AND date <= '2026-04-17' AND entry_price > 0 AND event_ticker IS NOT NULL")
print("With event_ticker:", cur.fetchone())

# Join: bot entry_price vs historical first_price
cur.execute("""
    SELECT m.event_ticker, m.entry_price, m.our_side, m.category,
           h.first_price_winner, h.first_price_loser, h.winner, h.loser
    FROM matches m
    JOIN historical_events h ON m.event_ticker = h.event_ticker
    WHERE m.date >= '2026-03-20' AND m.entry_price > 0
    ORDER BY m.date
""")

rows = cur.fetchall()
print("\nJoined rows: %d" % len(rows))

# For each: determine which side the bot was on, compare to first_price
biases = []
for evt, bot_entry, our_side, cat, fp_w, fp_l, winner, loser in rows:
    # Determine if bot was on winner or loser side
    if our_side and winner and our_side.upper() == winner.upper():
        first_price = fp_w
        side = "winner"
    elif our_side and loser and our_side.upper() == loser.upper():
        first_price = fp_l
        side = "loser"
    else:
        # Try matching by side code
        first_price = None
        side = "unknown"
        # Skip if we can't determine
        continue

    if first_price is None or first_price <= 0:
        continue

    bias = bot_entry - first_price
    biases.append({
        "evt": evt, "bot_entry": bot_entry, "first_price": first_price,
        "bias": bias, "side": side, "cat": cat or ""
    })

print("\nMatched entries with bias: %d" % len(biases))

if biases:
    avg_bias = sum(b["bias"] for b in biases) / len(biases)
    abs_biases = [abs(b["bias"]) for b in biases]
    std_bias = (sum((b["bias"] - avg_bias)**2 for b in biases) / len(biases)) ** 0.5
    print("Mean bias (bot_entry - first_price): %.1fc" % avg_bias)
    print("StdDev bias: %.1fc" % std_bias)
    print("Mean abs bias: %.1fc" % (sum(abs_biases) / len(abs_biases)))
    print("Median abs bias: %.1fc" % sorted(abs_biases)[len(abs_biases)//2])

    # Distribution
    print("\nBias distribution:")
    for threshold in [-20, -10, -5, -3, -1, 0, 1, 3, 5, 10, 20]:
        count = sum(1 for b in biases if b["bias"] <= threshold)
        print("  bias <= %+dc: %d (%.0f%%)" % (threshold, count, count/len(biases)*100))

    # Per-cell classification: classify by first_price (as analyses do)
    # then check if bot_entry falls in same cell
    def classify(tier, price):
        d = "leader" if price >= 50 else "underdog"
        bs = int(price // 5) * 5
        return "%s_%s_%d-%d" % (tier, d, bs, bs + 4)

    cell_mismatch = 0
    direction_mismatch = 0
    for b in biases:
        cat = b["cat"]
        tier = {"ATP_CHALL":"ATP_CHALL","ATP_MAIN":"ATP_MAIN",
                "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}.get(cat)
        if not tier: continue
        cell_fp = classify(tier, b["first_price"])
        cell_bot = classify(tier, b["bot_entry"])
        if cell_fp != cell_bot:
            cell_mismatch += 1
        if ("leader" in cell_fp) != ("leader" in cell_bot):
            direction_mismatch += 1

    print("\nCell classification impact:")
    print("  Entries where first_price cell != bot_entry cell: %d/%d (%.1f%%)" % (
        cell_mismatch, len(biases), cell_mismatch/len(biases)*100))
    print("  Entries where leader/underdog DIRECTION flips: %d/%d (%.1f%%)" % (
        direction_mismatch, len(biases), direction_mismatch/len(biases)*100))

    # Write per-entry CSV
    OUT_DIR = "/tmp/per_cell_verification"
    with open(os.path.join(OUT_DIR, "entry_price_bias.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event_ticker","bot_entry_price","first_price_historical",
                     "bias_cents","side","category"])
        for b in sorted(biases, key=lambda x: x["bias"]):
            w.writerow([b["evt"], b["bot_entry"], b["first_price"],
                         b["bias"], b["side"], b["cat"]])

    # Per-cell summary
    cell_biases = defaultdict(list)
    for b in biases:
        cat = b["cat"]
        tier = {"ATP_CHALL":"ATP_CHALL","ATP_MAIN":"ATP_MAIN",
                "WTA_MAIN":"WTA_MAIN","WTA_CHALL":"WTA_CHALL"}.get(cat)
        if not tier: continue
        cell = classify(tier, b["first_price"])
        cell_biases[cell].append(b["bias"])

    with open(os.path.join(OUT_DIR, "entry_price_bias_by_cell.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell","N","mean_bias","stddev_bias","median_bias",
                     "pct_within_3c","pct_within_5c"])
        for cell in sorted(cell_biases.keys()):
            bs = cell_biases[cell]
            n = len(bs)
            if n < 3: continue
            mean_b = sum(bs) / n
            std_b = (sum((x-mean_b)**2 for x in bs)/n)**0.5
            med_b = sorted(bs)[n//2]
            within_3 = sum(1 for x in bs if abs(x) <= 3) / n * 100
            within_5 = sum(1 for x in bs if abs(x) <= 5) / n * 100
            w.writerow([cell, n, "%.1f"%mean_b, "%.1f"%std_b, "%.1f"%med_b,
                         "%.0f"%within_3, "%.0f"%within_5])

    print("\nWritten: entry_price_bias.csv, entry_price_bias_by_cell.csv")
else:
    print("No matched entries found — matches table may lack event_ticker linkage")

    # Alternative: use kalshi_price_snapshots for Apr 21-28 period
    # Compare first snapshot mid to last_cents (last traded)
    print("\n=== Alternative: snapshot first_mid vs last_cents ===")
    cur.execute("""
        SELECT ticker, min(polled_at),
               (SELECT bid_cents FROM kalshi_price_snapshots k2
                WHERE k2.ticker = k1.ticker ORDER BY k2.polled_at LIMIT 1) as first_bid,
               (SELECT ask_cents FROM kalshi_price_snapshots k2
                WHERE k2.ticker = k1.ticker ORDER BY k2.polled_at LIMIT 1) as first_ask,
               (SELECT last_cents FROM kalshi_price_snapshots k2
                WHERE k2.ticker = k1.ticker ORDER BY k2.polled_at LIMIT 1) as first_last
        FROM kalshi_price_snapshots k1
        WHERE (ticker LIKE 'KXATPCHALL%' OR ticker LIKE 'KXWTACHALL%'
               OR ticker LIKE 'KXATPMATCH%' OR ticker LIKE 'KXWTAMATCH%')
        GROUP BY ticker
        HAVING count(*) >= 20
        LIMIT 20
    """)
    print("ticker | first_bid | first_ask | first_mid | first_last_traded")
    for tk, ts, fb, fa, fl in cur.fetchall():
        mid = (fb+fa)/2.0 if fb and fa else 0
        print("  %s bid=%s ask=%s mid=%.0f last=%s" % (tk[-20:], fb, fa, mid, fl))

conn.close()
