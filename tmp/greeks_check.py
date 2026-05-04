import sqlite3
conn = sqlite3.connect('/root/Omi-Workspace/arb-executor/tennis.db')
cur = conn.cursor()

# What price path data do we actually have?
cur.execute("SELECT min(polled_at), max(polled_at), count(*) FROM kalshi_price_snapshots")
print("kalshi_price_snapshots:", cur.fetchone())

cur.execute("SELECT count(DISTINCT ticker) FROM kalshi_price_snapshots WHERE ticker LIKE 'KXATP%' OR ticker LIKE 'KXWTA%'")
print("Tennis tickers in snapshots:", cur.fetchone())

cur.execute("SELECT ticker, count(*), min(polled_at), max(polled_at) FROM kalshi_price_snapshots WHERE ticker LIKE 'KXATPCHALL%' GROUP BY ticker ORDER BY count(*) DESC LIMIT 5")
print("\nSample snapshot coverage:")
for r in cur.fetchall():
    print("  %s: %d snapshots, %s to %s" % r)

cur.execute("SELECT count(*) FROM historical_events WHERE first_ts > '2026-04-21' AND first_ts < '2026-04-28' AND total_trades >= 10")
print("\nEvents in snapshot window (Apr 21-28):", cur.fetchone())

# Check if snapshots have commence_time for lifecycle normalization
cur.execute("SELECT ticker, polled_at, bid_cents, ask_cents, commence_time FROM kalshi_price_snapshots WHERE ticker LIKE 'KXATPCHALL%' ORDER BY ticker, polled_at LIMIT 10")
print("\nSnapshot sample with commence_time:")
for r in cur.fetchall():
    print("  %s polled=%s bid=%s ask=%s commence=%s" % r)

# Count: for events in Apr 21-28, how many snapshots per event-side?
cur.execute("""SELECT kps.ticker, count(*) as snaps, min(kps.polled_at), max(kps.polled_at), kps.commence_time
    FROM kalshi_price_snapshots kps
    WHERE (kps.ticker LIKE 'KXATPCHALL%' OR kps.ticker LIKE 'KXWTACHALL%'
        OR kps.ticker LIKE 'KXATPMATCH%' OR kps.ticker LIKE 'KXWTAMATCH%')
    GROUP BY kps.ticker
    HAVING snaps >= 20
    ORDER BY snaps DESC LIMIT 10""")
print("\nTickers with most snapshots:")
for r in cur.fetchall():
    print("  %s: %d snaps, %s to %s, commence=%s" % r)

conn.close()
