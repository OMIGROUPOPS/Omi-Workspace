#!/usr/bin/env python3
"""Deep dive analysis of high ROI arbs from overnight trading data"""
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def analyze_high_roi():
    report = []
    report.append("# High ROI Arb Analysis - January 29-30, 2026")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    print("Loading price history...")
    df = pd.read_csv('price_history_20260130_081111.csv')
    print(f"  Loaded {len(df):,} rows")

    # Convert timestamp
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['time_str'] = df['datetime'].dt.strftime('%H:%M:%S')

    # Calculate spread and ROI for each row
    # spread_buy_pm = k_bid - pm_ask (buy on PM, sell on Kalshi)
    # spread_buy_k = pm_bid - k_ask (buy on Kalshi, sell on PM)
    df['best_spread'] = df[['spread_buy_pm', 'spread_buy_k']].max(axis=1)
    df['direction'] = df.apply(lambda r: 'BUY_PM' if r['spread_buy_pm'] >= r['spread_buy_k'] else 'BUY_K', axis=1)

    # ROI calculation: spread / cost
    # For BUY_PM: cost = pm_ask, ROI = spread / pm_ask * 100
    # For BUY_K: cost = k_ask, ROI = spread / k_ask * 100
    def calc_roi(row):
        if row['best_spread'] <= 0:
            return 0
        if row['direction'] == 'BUY_PM':
            cost = row['pm_ask']
        else:
            cost = row['kalshi_ask']
        if cost <= 0:
            return 0
        return (row['best_spread'] / cost) * 100

    df['roi'] = df.apply(calc_roi, axis=1)

    # Filter to arb rows only
    arb_rows = df[df['has_arb'] == True].copy()
    print(f"  Arb rows: {len(arb_rows):,}")

    # ================================================================
    # 1. HIGH ROI ARBS (>5%)
    # ================================================================
    report.append("---\n## 1. High ROI Arbs (>5%)\n")

    high_roi = arb_rows[arb_rows['roi'] > 5].copy()
    report.append(f"**Total high ROI snapshots (>5%):** {len(high_roi):,}\n")

    if len(high_roi) > 0:
        report.append("### All High ROI Occurrences\n")
        report.append("| Time (UTC) | Game | Team | Spread | ROI | K Bid/Ask | PM Bid/Ask | Direction |")
        report.append("|------------|------|------|--------|-----|-----------|------------|-----------|")

        for _, row in high_roi.sort_values('roi', ascending=False).head(50).iterrows():
            game_parts = row['game_key'].split(':')
            game_id = game_parts[1] if len(game_parts) > 1 else row['game_key']
            team = game_parts[2] if len(game_parts) > 2 else ''
            report.append(f"| {row['time_str']} | {game_id} | {team} | {row['best_spread']:.0f}c | {row['roi']:.1f}% | {row['kalshi_bid']:.0f}/{row['kalshi_ask']:.0f} | {row['pm_bid']:.0f}/{row['pm_ask']:.0f} | {row['direction']} |")

        if len(high_roi) > 50:
            report.append(f"\n*...showing top 50 of {len(high_roi)} high ROI snapshots*\n")

    # ================================================================
    # 2. ARB WINDOW DURATION BY ROI TIER
    # ================================================================
    report.append("\n---\n## 2. Arb Window Duration by ROI Tier\n")

    # Group consecutive arb periods by game_key and calculate ROI tier
    arb_periods = []

    for game_key in df['game_key'].unique():
        game_df = df[df['game_key'] == game_key].sort_values('timestamp')

        in_arb = False
        arb_start = None
        arb_start_time = None
        period_rows = []

        for _, row in game_df.iterrows():
            if row['has_arb'] and not in_arb:
                # Arb opens
                in_arb = True
                arb_start = row['timestamp']
                arb_start_time = row['time_str']
                period_rows = [row]
            elif row['has_arb'] and in_arb:
                # Arb continues
                period_rows.append(row)
            elif not row['has_arb'] and in_arb:
                # Arb closes
                in_arb = False
                duration = row['timestamp'] - arb_start

                if period_rows:
                    max_roi = max(r['roi'] for r in period_rows)
                    max_spread = max(r['best_spread'] for r in period_rows)
                    avg_roi = statistics.mean(r['roi'] for r in period_rows)

                    arb_periods.append({
                        'game_key': game_key,
                        'start_time': arb_start_time,
                        'duration': duration,
                        'max_roi': max_roi,
                        'max_spread': max_spread,
                        'avg_roi': avg_roi,
                        'snapshots': len(period_rows),
                        'rows': period_rows
                    })
                period_rows = []

    # Categorize by ROI tier
    roi_tiers = {
        '1-2%': {'min': 1, 'max': 2, 'periods': []},
        '2-3%': {'min': 2, 'max': 3, 'periods': []},
        '3-5%': {'min': 3, 'max': 5, 'periods': []},
        '5-10%': {'min': 5, 'max': 10, 'periods': []},
        '10%+': {'min': 10, 'max': 999, 'periods': []},
    }

    for period in arb_periods:
        for tier_name, tier in roi_tiers.items():
            if tier['min'] <= period['max_roi'] < tier['max']:
                tier['periods'].append(period)
                break
        else:
            if period['max_roi'] >= 10:
                roi_tiers['10%+']['periods'].append(period)

    report.append("| ROI Tier | Count | Avg Duration | Max Duration | Avg Spread |")
    report.append("|----------|-------|--------------|--------------|------------|")

    for tier_name, tier in roi_tiers.items():
        periods = tier['periods']
        if periods:
            durations = [p['duration'] for p in periods]
            spreads = [p['max_spread'] for p in periods]
            avg_dur = statistics.mean(durations)
            max_dur = max(durations)
            avg_spread = statistics.mean(spreads)
            report.append(f"| {tier_name} | {len(periods)} | {avg_dur:.1f}s | {max_dur:.1f}s | {avg_spread:.1f}c |")
        else:
            report.append(f"| {tier_name} | 0 | - | - | - |")

    report.append(f"\n**Total arb periods:** {len(arb_periods)}")

    # ================================================================
    # 3. FULL LIFECYCLE FOR HIGH ROI ARBS (>5%)
    # ================================================================
    report.append("\n---\n## 3. High ROI Arb Lifecycles (>5%)\n")

    high_roi_periods = roi_tiers['5-10%']['periods'] + roi_tiers['10%+']['periods']
    high_roi_periods.sort(key=lambda x: -x['max_roi'])

    report.append(f"**Found {len(high_roi_periods)} arb periods with >5% ROI**\n")

    for i, period in enumerate(high_roi_periods[:20], 1):
        game_parts = period['game_key'].split(':')
        sport = game_parts[0].upper() if len(game_parts) > 0 else ''
        game_id = game_parts[1] if len(game_parts) > 1 else ''
        team = game_parts[2] if len(game_parts) > 2 else ''

        report.append(f"### [{i}] {sport} {game_id} - {team}")
        report.append(f"**Max ROI:** {period['max_roi']:.1f}% | **Max Spread:** {period['max_spread']:.0f}c | **Duration:** {period['duration']:.1f}s\n")

        report.append("```")
        report.append("Time     | K Bid/Ask | PM Bid/Ask | Spread | ROI   | Status")
        report.append("-" * 65)

        rows = period['rows']
        for j, row in enumerate(rows):
            status = "OPEN" if j == 0 else "continuing..."
            if j == len(rows) - 1 and len(rows) > 1:
                status = "LAST SNAPSHOT"
            report.append(f"{row['time_str']} | {row['kalshi_bid']:>3.0f}/{row['kalshi_ask']:<3.0f}  | {row['pm_bid']:>3.0f}/{row['pm_ask']:<3.0f}   | {row['best_spread']:>4.0f}c  | {row['roi']:>4.1f}% | {status}")

        report.append("```")

        # Executable assessment
        if period['duration'] >= 2:
            exec_status = "YES - sufficient time for execution (~1s needed)"
        elif period['duration'] >= 1:
            exec_status = "MARGINAL - just enough time, may miss"
        else:
            exec_status = "NO - too fast, likely to miss"

        report.append(f"**Executable?** {exec_status}\n")

    if len(high_roi_periods) > 20:
        report.append(f"\n*...showing 20 of {len(high_roi_periods)} high ROI periods*\n")

    # ================================================================
    # 4. EXECUTION FEASIBILITY
    # ================================================================
    report.append("\n---\n## 4. Execution Feasibility Analysis\n")

    report.append("**Assumptions:**")
    report.append("- API call latency: ~250ms per call")
    report.append("- Two calls needed: one to each exchange")
    report.append("- Total execution time: ~500ms-1000ms")
    report.append("- Safe buffer: 2 seconds minimum\n")

    # Duration analysis for all arb periods
    total_periods = len(arb_periods)
    if total_periods > 0:
        over_1s = len([p for p in arb_periods if p['duration'] >= 1])
        over_2s = len([p for p in arb_periods if p['duration'] >= 2])
        over_5s = len([p for p in arb_periods if p['duration'] >= 5])
        over_10s = len([p for p in arb_periods if p['duration'] >= 10])

        report.append("### All Arb Periods\n")
        report.append(f"| Duration Threshold | Count | Percentage |")
        report.append(f"|-------------------|-------|------------|")
        report.append(f"| ≥1 second | {over_1s} | {100*over_1s/total_periods:.1f}% |")
        report.append(f"| ≥2 seconds | {over_2s} | {100*over_2s/total_periods:.1f}% |")
        report.append(f"| ≥5 seconds | {over_5s} | {100*over_5s/total_periods:.1f}% |")
        report.append(f"| ≥10 seconds | {over_10s} | {100*over_10s/total_periods:.1f}% |")

    # Duration analysis for HIGH ROI periods only
    if high_roi_periods:
        report.append("\n### High ROI Periods Only (>5%)\n")
        total_high = len(high_roi_periods)
        high_over_1s = len([p for p in high_roi_periods if p['duration'] >= 1])
        high_over_2s = len([p for p in high_roi_periods if p['duration'] >= 2])
        high_over_5s = len([p for p in high_roi_periods if p['duration'] >= 5])

        report.append(f"| Duration Threshold | Count | Percentage |")
        report.append(f"|-------------------|-------|------------|")
        report.append(f"| ≥1 second | {high_over_1s} | {100*high_over_1s/total_high:.1f}% |")
        report.append(f"| ≥2 seconds | {high_over_2s} | {100*high_over_2s/total_high:.1f}% |")
        report.append(f"| ≥5 seconds | {high_over_5s} | {100*high_over_5s/total_high:.1f}% |")

    # ================================================================
    # 5. RECOMMENDATIONS
    # ================================================================
    report.append("\n---\n## 5. Recommendations\n")

    # Calculate optimal threshold
    executable_periods = [p for p in arb_periods if p['duration'] >= 2]
    if executable_periods:
        avg_roi_executable = statistics.mean(p['max_roi'] for p in executable_periods)
        avg_spread_executable = statistics.mean(p['max_spread'] for p in executable_periods)

        report.append("### Optimal ROI Threshold\n")
        report.append(f"- Executable arb periods (≥2s duration): {len(executable_periods)}")
        report.append(f"- Average max ROI of executable arbs: {avg_roi_executable:.1f}%")
        report.append(f"- Average max spread of executable arbs: {avg_spread_executable:.1f}c")

        # Count by ROI
        roi_1_plus = len([p for p in executable_periods if p['max_roi'] >= 1])
        roi_2_plus = len([p for p in executable_periods if p['max_roi'] >= 2])
        roi_3_plus = len([p for p in executable_periods if p['max_roi'] >= 3])
        roi_5_plus = len([p for p in executable_periods if p['max_roi'] >= 5])

        report.append(f"\n**Executable arbs by ROI threshold:**")
        report.append(f"- ROI ≥1%: {roi_1_plus} arbs")
        report.append(f"- ROI ≥2%: {roi_2_plus} arbs")
        report.append(f"- ROI ≥3%: {roi_3_plus} arbs")
        report.append(f"- ROI ≥5%: {roi_5_plus} arbs")

    report.append("\n### Order Type Recommendation\n")

    # Analyze price stability during arb periods
    price_changes = []
    for period in arb_periods:
        if len(period['rows']) >= 2:
            first = period['rows'][0]
            last = period['rows'][-1]
            k_bid_change = abs(last['kalshi_bid'] - first['kalshi_bid'])
            pm_ask_change = abs(last['pm_ask'] - first['pm_ask'])
            price_changes.append(max(k_bid_change, pm_ask_change))

    if price_changes:
        avg_change = statistics.mean(price_changes)
        max_change = max(price_changes)
        report.append(f"- Average price movement during arb: {avg_change:.1f}c")
        report.append(f"- Max price movement during arb: {max_change:.0f}c")

        if avg_change < 2:
            report.append(f"- **Recommendation:** LIMIT ORDERS at current prices")
            report.append(f"  - Prices are stable enough during arb windows")
            report.append(f"  - Limit orders avoid slippage")
        else:
            report.append(f"- **Recommendation:** MARKET ORDERS for speed")
            report.append(f"  - Prices move {avg_change:.1f}c on average - need speed over precision")

    report.append("\n### Summary Recommendations\n")

    if executable_periods:
        # Find the "sweet spot"
        good_arbs = [p for p in executable_periods if p['max_roi'] >= 2 and p['duration'] >= 3]

        report.append(f"1. **Minimum ROI threshold:** 2% (captures most executable opportunities)")
        report.append(f"2. **High ROI (>5%) arbs:** {'Executable' if high_over_2s > 0 else 'Too fast'} - {high_over_2s}/{len(high_roi_periods)} last ≥2s")
        report.append(f"3. **Sweet spot:** ROI 2-5% with duration ≥3s ({len(good_arbs)} opportunities)")
        report.append(f"4. **Execution strategy:** Submit both orders simultaneously, not sequentially")
        report.append(f"5. **Risk management:** Set 1-2c buffer on limit prices to ensure fills")

    # ================================================================
    # WRITE REPORT
    # ================================================================
    report_text = '\n'.join(report)
    with open('high_roi_analysis.md', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\nReport written to: high_roi_analysis.md")
    print(f"Report length: {len(report_text):,} characters")

    # Print summary to console
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total arb periods: {len(arb_periods)}")
    print(f"High ROI periods (>5%): {len(high_roi_periods)}")
    if high_roi_periods:
        print(f"High ROI executable (≥2s): {high_over_2s} ({100*high_over_2s/len(high_roi_periods):.0f}%)")
    print(f"All arbs executable (≥2s): {over_2s} ({100*over_2s/len(arb_periods):.0f}%)")

if __name__ == '__main__':
    analyze_high_roi()
