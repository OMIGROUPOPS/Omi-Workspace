#!/usr/bin/env python3
"""Plot Kalshi last-traded vs Pinnacle consensus FV for a given event."""
import csv, json, sqlite3, sys, os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

ET = ZoneInfo("America/New_York")
TRADE_DIR = Path(__file__).resolve().parent / "trades"
DB_PATH = Path(__file__).resolve().parent.parent / "tennis.db"

def load_trades(ticker):
    """Load trade tape from CSV."""
    f = TRADE_DIR / ("%s.csv" % ticker)
    if not f.exists():
        return []
    trades = []
    with open(f) as fh:
        reader = csv.reader(fh)
        try:
            next(reader)
        except StopIteration:
            return []
        for row in reader:
            if len(row) < 3:
                continue
            try:
                ts = datetime.strptime(row[0].strip(), "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET)
                price = int(row[2])
                count = int(row[3]) if len(row) > 3 else 1
            except:
                continue
            if price <= 0 or price >= 100:
                continue
            trades.append({"ts": ts, "price": price, "count": count})
    trades.sort(key=lambda t: t["ts"])
    return trades

def load_consensus(event_ticker):
    """Load consensus FV history from tennis.db edge_scores."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH), timeout=5)
    try:
        cur = conn.cursor()
        cur.execute("SELECT pinnacle_p1, pinnacle_p2, kalshi_p1, kalshi_p2, "
                     "edge_p1, edge_p2, grade, updated_at, player1_name, player2_name "
                     "FROM edge_scores WHERE event_ticker = ?", (event_ticker,))
        rows = cur.fetchall()
        if not rows:
            return []
        # edge_scores has one row per event (latest snapshot)
        # For historical series, we'd need a separate history table
        # Return the single snapshot for overlay
        r = rows[0]
        return [{
            "p1_fv": r[0], "p2_fv": r[1],
            "p1_kalshi": r[2], "p2_kalshi": r[3],
            "p1_edge": r[4], "p2_edge": r[5],
            "grade": r[6], "updated_at": r[7],
            "p1_name": r[8], "p2_name": r[9],
        }]
    except:
        return []
    finally:
        conn.close()

def plot_text(ticker, trades, consensus):
    """ASCII text chart — works in terminal without matplotlib."""
    if not trades:
        print("No trades for %s" % ticker)
        return

    player = ticker.split("-")[-1]
    event = "-".join(ticker.split("-")[:2])

    print("=" * 70)
    print("PRICE CHART: %s (%s)" % (player, ticker[:45]))
    print("=" * 70)

    # Time buckets: 30-min intervals
    start = trades[0]["ts"]
    end = trades[-1]["ts"]
    duration_min = (end - start).total_seconds() / 60

    if duration_min < 60:
        bucket_min = 5
    elif duration_min < 360:
        bucket_min = 15
    else:
        bucket_min = 30

    from datetime import timedelta
    buckets = []
    t = start
    while t <= end:
        bucket_trades = [tr for tr in trades if t <= tr["ts"] < t + timedelta(minutes=bucket_min)]
        if bucket_trades:
            prices = [tr["price"] for tr in bucket_trades]
            vol = sum(tr["count"] for tr in bucket_trades)
            buckets.append({
                "ts": t, "low": min(prices), "high": max(prices),
                "last": prices[-1], "vol": vol, "count": len(prices),
            })
        t += timedelta(minutes=bucket_min)

    if not buckets:
        print("No valid buckets")
        return

    # Price range
    all_prices = [b["last"] for b in buckets]
    min_p = min(all_prices) - 5
    max_p = max(all_prices) + 5
    chart_height = 20
    price_range = max_p - min_p
    if price_range == 0:
        price_range = 1

    def price_to_row(p):
        return int((p - min_p) / price_range * (chart_height - 1))

    # Consensus FV overlay
    fv_price = None
    fv_label = ""
    if consensus:
        c = consensus[0]
        # Determine which side this ticker is
        if ticker.endswith("-" + ticker.split("-")[-1]):
            # Try matching player name to p1 or p2
            code = ticker.split("-")[-1]
            if c["p1_name"] and code.upper()[:3] in c["p1_name"].upper()[:5]:
                fv_price = c["p1_fv"]
                fv_label = "Pinnacle FV: %.0fc" % fv_price
            else:
                fv_price = c["p2_fv"]
                fv_label = "Pinnacle FV: %.0fc" % fv_price

    # Print chart
    print()
    print("Time range: %s to %s" % (
        start.strftime("%m/%d %I:%M %p"), end.strftime("%m/%d %I:%M %p")))
    print("Duration: %.1f hours  |  Trades: %d  |  Buckets: %d (%dm each)" % (
        duration_min / 60, len(trades), len(buckets), bucket_min))
    if fv_label:
        print("Consensus: %s (from tennis.db)" % fv_label)
    print()

    # ASCII chart
    for row in range(chart_height - 1, -1, -1):
        price_at_row = min_p + (row / (chart_height - 1)) * price_range
        label = "%3dc" % round(price_at_row)

        line = ""
        for b in buckets:
            p_row = price_to_row(b["last"])
            if p_row == row:
                line += "#"
            elif fv_price and price_to_row(fv_price) == row:
                line += "-"
            else:
                line += " "

        # FV marker on right side
        fv_mark = ""
        if fv_price and abs(price_at_row - fv_price) < price_range / chart_height:
            fv_mark = " <-- FV %.0fc" % fv_price

        print("%s |%s|%s" % (label, line, fv_mark))

    # Time axis
    print("     +" + "-" * len(buckets) + "+")
    print("      %s" % start.strftime("%I:%M %p"))
    print("      " + " " * (len(buckets) - 10) + end.strftime("%I:%M %p"))

    # Summary stats
    print()
    first_price = trades[0]["price"]
    last_price = trades[-1]["price"]
    print("First trade: %dc  Last trade: %dc  Change: %+dc" % (
        first_price, last_price, last_price - first_price))
    print("Low: %dc  High: %dc  Range: %dc" % (
        min(all_prices), max(all_prices), max(all_prices) - min(all_prices)))
    if fv_price:
        print("Entry vs FV: first=%dc vs FV=%.0fc = %+.0fc gap" % (
            first_price, fv_price, first_price - fv_price))
        print("Final vs FV: last=%dc vs FV=%.0fc = %+.0fc gap" % (
            last_price, fv_price, last_price - fv_price))

    # Trade volume distribution
    print()
    print("Volume by time bucket:")
    for b in buckets[:10]:
        bar = "#" * min(b["vol"] // 5, 40)
        print("  %s  %3dc  vol=%4d  %s" % (
            b["ts"].strftime("%I:%M %p"), b["last"], b["vol"], bar))
    if len(buckets) > 10:
        print("  ... (%d more buckets)" % (len(buckets) - 10))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_kalshi_vs_consensus.py <TICKER>")
        print("       python3 plot_kalshi_vs_consensus.py <EVENT_TICKER>  (plots both sides)")
        print()
        print("Examples:")
        print("  python3 plot_kalshi_vs_consensus.py KXATPMATCH-26APR19RUBFIL-RUB")
        print("  python3 plot_kalshi_vs_consensus.py KXATPMATCH-26APR19RUBFIL")
        print()
        # List available trade files
        if TRADE_DIR.exists():
            files = sorted(TRADE_DIR.glob("*.csv"))
            print("Available tickers (%d):" % len(files))
            for f in files[-10:]:
                print("  %s" % f.stem)
        return

    arg = sys.argv[1]

    # If event ticker (no player code), plot both sides
    if arg.count("-") <= 1 or (arg.count("-") == 1 and len(arg.split("-")[-1]) > 3):
        # Try as event ticker
        event_ticker = arg
        trade_files = list(TRADE_DIR.glob("%s-*.csv" % event_ticker))
        if not trade_files:
            print("No trade files matching %s" % event_ticker)
            return
        for tf in sorted(trade_files):
            ticker = tf.stem
            trades = load_trades(ticker)
            consensus = load_consensus(event_ticker)
            plot_text(ticker, trades, consensus)
            print()
    else:
        # Single ticker
        ticker = arg
        event_ticker = "-".join(ticker.split("-")[:2])
        trades = load_trades(ticker)
        consensus = load_consensus(event_ticker)
        plot_text(ticker, trades, consensus)


if __name__ == "__main__":
    main()
