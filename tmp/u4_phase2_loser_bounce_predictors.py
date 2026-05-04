"""
U4 Phase 2: Loser-side bounce predictors.

Phase 1 found:
- Loser median bounce is ~12-16c, half of losers don't reach +10c.
- 33% of matches have first_price_winner + first_price_loser >5c off 100 (A19: first_price unsynchronized).
- Bilateral capture is rate-limited by loser-side bounce.

Strategic question reframed: which match characteristics predict loser-side max_bounce?

Method:
- Filter to synchronized subset: abs(first_price_winner + first_price_loser - 100) <= 5
- Compute loser_max_bounce per match
- Stratify by: skew_magnitude bins, total_trades bins, category, match duration, hour-of-day
- For each stratum: report N, p25/p50/p75/p90 of loser_max_bounce, and bilateral-capture rate
  at +5c / +10c / +15c / +20c (using the bilateral question as a derived metric)

Output: /tmp/u4_phase2_loser_bounce_by_strata.csv
        /tmp/u4_phase2_loser_bounce_summary.txt
"""

import csv
from collections import defaultdict
from statistics import quantiles, mean, stdev

INPUT = '/tmp/u4_phase1_match_landscape.csv'
OUTPUT_CSV = '/tmp/u4_phase2_loser_bounce_by_strata.csv'
OUTPUT_TXT = '/tmp/u4_phase2_loser_bounce_summary.txt'

THRESHOLDS = [5, 10, 15, 20]

def safe_quartiles(data):
    if len(data) < 4:
        return None
    q = quantiles(sorted(data), n=10)
    return {'p10': q[0], 'p25': q[1], 'p50': q[4], 'p75': q[6], 'p90': q[8], 'max': max(data), 'mean': mean(data), 'n': len(data)}

def stratum_stats(matches, key_fn, name):
    groups = defaultdict(list)
    for m in matches:
        k = key_fn(m)
        if k is None:
            continue
        groups[k].append(m)

    results = []
    for k in sorted(groups.keys(), key=lambda x: (str(type(x)), x)):
        group = groups[k]
        loser_bounces = [m['loser_max_bounce'] for m in group]
        winner_bounces = [m['winner_max_bounce'] for m in group]
        n = len(group)
        if n < 30:
            low_n = 'YES'
        else:
            low_n = 'NO'

        loser_q = safe_quartiles(loser_bounces) if n >= 4 else None
        winner_q = safe_quartiles(winner_bounces) if n >= 4 else None

        bilateral = {}
        for x in THRESHOLDS:
            both = sum(1 for m in group if m['winner_max_bounce'] >= x and m['loser_max_bounce'] >= x)
            bilateral[x] = 100.0 * both / n if n else 0

        results.append({
            'stratum': name,
            'value': str(k),
            'n': n,
            'low_n_flag': low_n,
            'loser_p10': loser_q['p10'] if loser_q else None,
            'loser_p25': loser_q['p25'] if loser_q else None,
            'loser_p50': loser_q['p50'] if loser_q else None,
            'loser_p75': loser_q['p75'] if loser_q else None,
            'loser_p90': loser_q['p90'] if loser_q else None,
            'loser_max': loser_q['max'] if loser_q else None,
            'loser_mean': round(loser_q['mean'], 2) if loser_q else None,
            'winner_p50': winner_q['p50'] if winner_q else None,
            'bilateral_5c_pct': round(bilateral[5], 1),
            'bilateral_10c_pct': round(bilateral[10], 1),
            'bilateral_15c_pct': round(bilateral[15], 1),
            'bilateral_20c_pct': round(bilateral[20], 1),
        })
    return results

def main():
    matches = []
    with open(INPUT) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['first_price_winner'] = int(float(row['first_price_winner']))
                row['first_price_loser'] = int(float(row['first_price_loser']))
                row['winner_max_bounce'] = int(float(row['winner_max_bounce']))
                row['loser_max_bounce'] = int(float(row['loser_max_bounce']))
                row['skew_magnitude'] = int(float(row['skew_magnitude']))
                row['spread_check_sum'] = int(float(row['spread_check_sum']))
                row['total_trades'] = int(row['total_trades'])
                row['hour_of_day_utc'] = int(row['hour_of_day_utc']) if row['hour_of_day_utc'] else None
                row['duration_hours'] = float(row['duration_hours']) if row['duration_hours'] else None
                matches.append(row)
            except (ValueError, KeyError):
                continue
    print(f"Loaded {len(matches)} matches from Phase 1 CSV")

    synced = [m for m in matches if abs(m['spread_check_sum'] - 100) <= 5]
    print(f"Synchronized subset (|fpw+fpl-100| <= 5): {len(synced)} matches ({100.0*len(synced)/len(matches):.1f}%)")

    all_results = []

    all_results.extend(stratum_stats(synced, lambda m: m['category'], 'category'))

    def skew_bin(m):
        s = m['skew_magnitude']
        if s < 5: return '00-04'
        if s < 10: return '05-09'
        if s < 15: return '10-14'
        if s < 20: return '15-19'
        if s < 25: return '20-24'
        if s < 30: return '25-29'
        if s < 35: return '30-34'
        if s < 40: return '35-39'
        if s < 45: return '40-44'
        return '45+'
    all_results.extend(stratum_stats(synced, skew_bin, 'skew_magnitude'))

    def volume_bin(m):
        t = m['total_trades']
        if t < 25: return '0010-0024'
        if t < 50: return '0025-0049'
        if t < 100: return '0050-0099'
        if t < 250: return '0100-0249'
        if t < 500: return '0250-0499'
        if t < 1000: return '0500-0999'
        return '1000+'
    all_results.extend(stratum_stats(synced, volume_bin, 'total_trades'))

    def cat_skew(m):
        return f"{m['category']}|{skew_bin(m)}"
    all_results.extend(stratum_stats(synced, cat_skew, 'category_x_skew'))

    all_results.extend(stratum_stats(synced, lambda m: m['hour_of_day_utc'], 'hour_utc'))

    def duration_bin(m):
        d = m['duration_hours']
        if d is None: return None
        if d < 2: return '0_under_2h'
        if d < 4: return '1_2-4h'
        if d < 6: return '2_4-6h'
        if d < 12: return '3_6-12h'
        return '4_12h+'
    all_results.extend(stratum_stats(synced, duration_bin, 'duration_bin'))

    def spread_dev(m):
        d = m['spread_check_sum'] - 100
        if d == 0: return 'exactly_100'
        if abs(d) <= 2: return 'within_2c'
        return '3-5c_off'
    all_results.extend(stratum_stats(synced, spread_dev, 'spread_dev'))

    with open(OUTPUT_CSV, 'w', newline='') as f:
        cols = ['stratum', 'value', 'n', 'low_n_flag',
                'loser_p10', 'loser_p25', 'loser_p50', 'loser_p75', 'loser_p90', 'loser_max', 'loser_mean',
                'winner_p50',
                'bilateral_5c_pct', 'bilateral_10c_pct', 'bilateral_15c_pct', 'bilateral_20c_pct']
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in all_results:
            w.writerow(r)

    with open(OUTPUT_TXT, 'w') as f:
        f.write("U4 PHASE 2: LOSER-SIDE BOUNCE PREDICTORS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total matches loaded: {len(matches)}\n")
        f.write(f"Synchronized subset (|fpw+fpl-100| <= 5): {len(synced)}\n\n")

        all_loser = [m['loser_max_bounce'] for m in synced]
        all_winner = [m['winner_max_bounce'] for m in synced]
        f.write("=== AGGREGATE on synchronized subset ===\n")
        q = safe_quartiles(all_loser)
        f.write(f"  Loser bounce: n={q['n']}, p10={q['p10']}, p25={q['p25']}, p50={q['p50']}, p75={q['p75']}, p90={q['p90']}, mean={q['mean']:.1f}\n")
        q = safe_quartiles(all_winner)
        f.write(f"  Winner bounce: n={q['n']}, p10={q['p10']}, p25={q['p25']}, p50={q['p50']}, p75={q['p75']}, p90={q['p90']}, mean={q['mean']:.1f}\n")
        f.write("\n")
        for x in THRESHOLDS:
            both = sum(1 for m in synced if m['winner_max_bounce'] >= x and m['loser_max_bounce'] >= x)
            pct = 100.0 * both / len(synced)
            f.write(f"  Bilateral capture at +{x}c: {both}/{len(synced)} = {pct:.2f}%\n")
        f.write("\n")

        for stratum_name in ['category', 'skew_magnitude', 'total_trades', 'duration_bin', 'spread_dev']:
            f.write(f"=== Stratum: {stratum_name} ===\n")
            f.write(f"  {'value':<25} {'n':>5} {'l_p50':>6} {'l_p75':>6} {'bi_10':>7} {'bi_15':>7}\n")
            for r in all_results:
                if r['stratum'] != stratum_name:
                    continue
                if r['n'] < 30:
                    flag = ' [LOW N]'
                else:
                    flag = ''
                f.write(f"  {str(r['value']):<25} {r['n']:>5} {str(r['loser_p50']):>6} {str(r['loser_p75']):>6} {r['bilateral_10c_pct']:>7.1f} {r['bilateral_15c_pct']:>7.1f}{flag}\n")
            f.write("\n")

    print()
    with open(OUTPUT_TXT) as f:
        print(f.read())
    print()
    print(f"Detailed CSV: {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
