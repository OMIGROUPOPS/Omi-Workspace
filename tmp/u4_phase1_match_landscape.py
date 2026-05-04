"""
U4 Phase 1: Match landscape characterization.

No pre-defined cells. One row per match, every relevant variable as a column.
Lets us slice the data any way post-hoc rather than locking a partition.

Variables included per match:
- Identity: event_ticker, category, winner, loser
- Kalshi C-tier prices: first/min/max/last for both sides; total_trades; first_ts; last_ts
- Derived: bounce magnitudes, skew, spread, match duration
- Pinnacle (if available in book_prices): per-event sharp FV per side
- Volume: kalshi_price_snapshots.volume_24h (if available, joined by ticker)
- Time: hour-of-day from first_ts, day-of-week

Metrics computed per match (continuous, not thresholded):
- winner_max_bounce, loser_max_bounce
- winner_max_dip, loser_max_dip (using min_price)
- winner_settlement_convergence (last - 99 if winner; for symmetry compute both signs)
- skew_magnitude = abs(50 - first_price_winner)
- spread = first_price_winner - first_price_loser (~ -1 to 1 in cents-100, but C-tier prices are 0-99)
- pinnacle_kalshi_skew_winner = pinnacle_p1_fv - first_price_winner (if pinnacle joined)

Output: /tmp/u4_phase1_match_landscape.csv
        /tmp/u4_phase1_summary.txt (basic distributions per category)
"""

import sqlite3
import csv
from datetime import datetime
from collections import defaultdict

DB = '/root/Omi-Workspace/arb-executor/tennis.db'

def parse_iso(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except:
        return None

def main():
    conn = sqlite3.connect(DB)

    rows = list(conn.execute("""
        SELECT event_ticker, category, winner, loser,
               first_price_winner, min_price_winner, max_price_winner, last_price_winner,
               first_price_loser, min_price_loser, max_price_loser,
               total_trades, first_ts, last_ts
        FROM historical_events
        WHERE total_trades >= 10
          AND first_price_winner IS NOT NULL
          AND max_price_winner IS NOT NULL
          AND first_price_loser IS NOT NULL
          AND max_price_loser IS NOT NULL
          AND category IN ('ATP_MAIN', 'ATP_CHALL', 'WTA_MAIN', 'WTA_CHALL')
    """))
    print(f"Loaded {len(rows)} matches")

    pinnacle = {}
    for r in conn.execute("""
        SELECT event_ticker, book_p1_fv_cents, book_p2_fv_cents, player1_name, player2_name
        FROM book_prices
        WHERE book_key = 'pinnacle'
        ORDER BY polled_at DESC
    """):
        et = r[0]
        if et not in pinnacle:
            pinnacle[et] = (r[1], r[2], r[3], r[4])
    print(f"Pinnacle FVs available for {len(pinnacle)} events")

    volume = {}
    for r in conn.execute("""
        SELECT event_ticker, MAX(volume_24h)
        FROM kalshi_price_snapshots
        GROUP BY event_ticker
    """):
        volume[r[0]] = r[1]
    print(f"volume_24h available for {len(volume)} events")

    conn.close()

    output_rows = []
    for row in rows:
        (et, cat, winner, loser,
         fpw, minpw, mpw, lpw,
         fpl, minpl, mpl,
         ntrades, first_ts, last_ts) = row

        winner_max_bounce = mpw - fpw
        loser_max_bounce = mpl - fpl
        winner_max_dip = (fpw - minpw) if minpw is not None else None
        loser_max_dip = (fpl - minpl) if minpl is not None else None

        skew_magnitude = abs(50 - fpw)
        spread_check = fpw + fpl

        winner_settlement_conv = (lpw - 99) if lpw is not None else None

        pin_p1, pin_p2, pin_n1, pin_n2 = pinnacle.get(et, (None, None, None, None))

        vol_24h = volume.get(et)

        ft_dt = parse_iso(first_ts)
        hour_of_day = ft_dt.hour if ft_dt else None
        day_of_week = ft_dt.weekday() if ft_dt else None

        lt_dt = parse_iso(last_ts)
        if ft_dt and lt_dt:
            duration_hours = (lt_dt - ft_dt).total_seconds() / 3600
        else:
            duration_hours = None

        output_rows.append({
            'event_ticker': et,
            'category': cat,
            'winner': winner,
            'loser': loser,
            'first_price_winner': fpw,
            'first_price_loser': fpl,
            'min_price_winner': minpw,
            'min_price_loser': minpl,
            'max_price_winner': mpw,
            'max_price_loser': mpl,
            'last_price_winner': lpw,
            'total_trades': ntrades,
            'winner_max_bounce': winner_max_bounce,
            'loser_max_bounce': loser_max_bounce,
            'winner_max_dip': winner_max_dip,
            'loser_max_dip': loser_max_dip,
            'skew_magnitude': skew_magnitude,
            'spread_check_sum': spread_check,
            'winner_settle_conv': winner_settlement_conv,
            'pinnacle_p1_fv': pin_p1,
            'pinnacle_p2_fv': pin_p2,
            'pinnacle_p1_name': pin_n1,
            'pinnacle_p2_name': pin_n2,
            'volume_24h_max': vol_24h,
            'hour_of_day_utc': hour_of_day,
            'day_of_week': day_of_week,
            'duration_hours': duration_hours,
            'first_ts': first_ts,
        })

    cols = list(output_rows[0].keys())
    with open('/tmp/u4_phase1_match_landscape.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in output_rows:
            w.writerow(r)
    print(f"Wrote {len(output_rows)} rows to /tmp/u4_phase1_match_landscape.csv")

    with open('/tmp/u4_phase1_summary.txt', 'w') as f:
        f.write("U4 PHASE 1 MATCH LANDSCAPE SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total matches: {len(output_rows)}\n")
        f.write(f"With Pinnacle FV available: {sum(1 for r in output_rows if r['pinnacle_p1_fv'] is not None)}\n")
        f.write(f"With volume_24h available: {sum(1 for r in output_rows if r['volume_24h_max'] is not None)}\n")
        f.write(f"With min_price both sides: {sum(1 for r in output_rows if r['winner_max_dip'] is not None and r['loser_max_dip'] is not None)}\n")
        f.write("\n")

        f.write("=== Per-category counts ===\n")
        cat_counts = defaultdict(int)
        for r in output_rows:
            cat_counts[r['category']] += 1
        for cat in sorted(cat_counts):
            f.write(f"  {cat}: {cat_counts[cat]}\n")
        f.write("\n")

        from statistics import median, quantiles
        f.write("=== Bounce distributions per category (winner side max_bounce) ===\n")
        by_cat_bounce = defaultdict(list)
        for r in output_rows:
            by_cat_bounce[r['category']].append(r['winner_max_bounce'])
        for cat in sorted(by_cat_bounce):
            data = sorted(by_cat_bounce[cat])
            n = len(data)
            if n >= 4:
                q = quantiles(data, n=4)
                f.write(f"  {cat}: n={n}, p25={q[0]:.0f}, p50={q[1]:.0f}, p75={q[2]:.0f}, max={max(data)}\n")
        f.write("\n")

        f.write("=== Loser side max_bounce ===\n")
        by_cat_bounce_l = defaultdict(list)
        for r in output_rows:
            by_cat_bounce_l[r['category']].append(r['loser_max_bounce'])
        for cat in sorted(by_cat_bounce_l):
            data = sorted(by_cat_bounce_l[cat])
            n = len(data)
            if n >= 4:
                q = quantiles(data, n=4)
                f.write(f"  {cat}: n={n}, p25={q[0]:.0f}, p50={q[1]:.0f}, p75={q[2]:.0f}, max={max(data)}\n")
        f.write("\n")

        f.write("=== Skew magnitude distribution (abs(50 - first_price_winner)) ===\n")
        for cat in sorted(cat_counts):
            skews = sorted([r['skew_magnitude'] for r in output_rows if r['category'] == cat])
            n = len(skews)
            if n >= 4:
                q = quantiles(skews, n=4)
                f.write(f"  {cat}: n={n}, p25={q[0]}, p50={q[1]}, p75={q[2]}, max={max(skews)}\n")
        f.write("\n")

        f.write("=== spread_check_sum (fpw + fpl) — should be ~100 for valid binary ===\n")
        sums = [r['spread_check_sum'] for r in output_rows]
        n = len(sums)
        if n >= 4:
            q = quantiles(sorted(sums), n=4)
            f.write(f"  n={n}, p25={q[0]}, p50={q[1]}, p75={q[2]}\n")
            outliers = [r for r in output_rows if abs(r['spread_check_sum'] - 100) > 5]
            f.write(f"  Outliers (>5c off 100): {len(outliers)}\n")

    print()
    print("=== Summary ===")
    with open('/tmp/u4_phase1_summary.txt') as f:
        print(f.read())

if __name__ == '__main__':
    main()
