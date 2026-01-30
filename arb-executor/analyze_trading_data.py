#!/usr/bin/env python3
"""
Comprehensive analysis of trading data to find optimization opportunities.
Analyzes price history, trades, skipped arbs, and TAM data.
"""
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def analyze_trading_data():
    report = []
    report.append("# Trading Data Analysis Report - January 29-30, 2026")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ================================================================
    # LOAD DATA
    # ================================================================
    print("Loading data...")

    # Load price history
    df = pd.read_csv('price_history_20260130_081111.csv')
    print(f"  Price history: {len(df):,} rows")

    # Load TAM snapshot
    with open('tam_snapshot.json', 'r') as f:
        tam = json.load(f)
    print(f"  TAM snapshot loaded")

    # Load trades
    with open('trades.json', 'r') as f:
        trades = json.load(f)
    print(f"  Trades: {len(trades):,} records")

    # Load skipped arbs
    with open('skipped_arbs.json', 'r') as f:
        skipped = json.load(f)
    print(f"  Skipped arbs: {len(skipped):,} records")

    # ================================================================
    # EXECUTIVE SUMMARY
    # ================================================================
    report.append("## Executive Summary\n")

    tam_stats = tam['tam_stats']
    report.append(f"- **Total Scans:** {tam_stats['scan_count']:,}")
    report.append(f"- **Unique Arbs Found:** {tam_stats['unique_arbs_new']} new + {tam_stats['unique_arbs_reopen']} reopened = {tam_stats['unique_arbs_executed']} total")
    report.append(f"- **Flickers Ignored:** {tam_stats['flicker_ignored']}")
    report.append(f"- **TAM (Total Addressable Market):** ${tam_stats['total_profit_if_captured']/100:,.2f}")
    report.append(f"- **Total Contracts Available:** {tam_stats['total_contracts']:,}")
    report.append(f"- **Games Tracked:** {tam['price_history_games']}")
    report.append(f"- **Price Data Points:** {tam['price_history_rows']:,}\n")

    # ================================================================
    # 1. ARB TIMING PATTERNS
    # ================================================================
    report.append("---\n## 1. Arb Timing Patterns\n")

    # Convert timestamp to datetime and calculate EST hour
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['hour'] = (df['datetime'].dt.hour - 5) % 24  # Convert UTC to EST
    df['minute'] = df['datetime'].dt.minute

    # Calculate spread early (needed for arb analysis)
    df['spread'] = df[['spread_buy_pm', 'spread_buy_k']].max(axis=1)

    # Find rows with arbs
    arb_rows = df[df['has_arb'] == True].copy()
    non_arb_rows = df[df['has_arb'] == False].copy()

    report.append(f"### Arb Frequency\n")
    report.append(f"- **Total price snapshots:** {len(df):,}")
    report.append(f"- **Snapshots with arb:** {len(arb_rows):,} ({100*len(arb_rows)/len(df):.2f}%)")
    report.append(f"- **Snapshots without arb:** {len(non_arb_rows):,}\n")

    # Arbs by hour
    report.append("### Arbs by Hour (EST)\n")
    report.append("| Hour | Arb Snapshots | Total Snapshots | Arb Rate |")
    report.append("|------|---------------|-----------------|----------|")

    hourly_arbs = arb_rows.groupby('hour').size()
    hourly_total = df.groupby('hour').size()

    for hour in sorted(hourly_total.index):
        arb_count = hourly_arbs.get(hour, 0)
        total = hourly_total[hour]
        rate = 100 * arb_count / total if total > 0 else 0
        report.append(f"| {hour:02d}:00 | {arb_count:,} | {total:,} | {rate:.2f}% |")

    # Arb duration analysis
    report.append("\n### Arb Duration Analysis\n")

    # Group consecutive arb periods by game_key
    arb_durations = []
    for game_key in df['game_key'].unique():
        game_df = df[df['game_key'] == game_key].sort_values('timestamp')

        in_arb = False
        arb_start = None

        for _, row in game_df.iterrows():
            if row['has_arb'] and not in_arb:
                in_arb = True
                arb_start = row['timestamp']
            elif not row['has_arb'] and in_arb:
                in_arb = False
                duration = row['timestamp'] - arb_start
                arb_durations.append(duration)

    if arb_durations:
        report.append(f"- **Number of arb periods:** {len(arb_durations)}")
        report.append(f"- **Average duration:** {statistics.mean(arb_durations):.1f} seconds")
        report.append(f"- **Median duration:** {statistics.median(arb_durations):.1f} seconds")
        report.append(f"- **Min duration:** {min(arb_durations):.1f} seconds")
        report.append(f"- **Max duration:** {max(arb_durations):.1f} seconds")

        # Duration distribution
        dur_buckets = {'<10s': 0, '10-30s': 0, '30-60s': 0, '1-5min': 0, '5-30min': 0, '>30min': 0}
        for d in arb_durations:
            if d < 10:
                dur_buckets['<10s'] += 1
            elif d < 30:
                dur_buckets['10-30s'] += 1
            elif d < 60:
                dur_buckets['30-60s'] += 1
            elif d < 300:
                dur_buckets['1-5min'] += 1
            elif d < 1800:
                dur_buckets['5-30min'] += 1
            else:
                dur_buckets['>30min'] += 1

        report.append("\n**Duration Distribution:**")
        report.append("| Duration | Count | Percentage |")
        report.append("|----------|-------|------------|")
        for bucket, count in dur_buckets.items():
            pct = 100 * count / len(arb_durations) if arb_durations else 0
            report.append(f"| {bucket} | {count} | {pct:.1f}% |")

    # ================================================================
    # 2. SPREAD ANALYSIS
    # ================================================================
    report.append("\n---\n## 2. Spread Analysis\n")

    # Overall spread distribution
    report.append("### Spread Distribution (All Snapshots)\n")

    spread_buckets = {
        'Negative (no arb)': len(df[df['spread'] <= 0]),
        '1-2c': len(df[(df['spread'] > 0) & (df['spread'] <= 2)]),
        '2-3c': len(df[(df['spread'] > 2) & (df['spread'] <= 3)]),
        '3-5c': len(df[(df['spread'] > 3) & (df['spread'] <= 5)]),
        '5-10c': len(df[(df['spread'] > 5) & (df['spread'] <= 10)]),
        '10c+': len(df[df['spread'] > 10]),
    }

    report.append("| Spread | Count | Percentage |")
    report.append("|--------|-------|------------|")
    for bucket, count in spread_buckets.items():
        pct = 100 * count / len(df)
        report.append(f"| {bucket} | {count:,} | {pct:.2f}% |")

    # Spreads by sport
    report.append("\n### Spreads by Sport (Arb Snapshots Only)\n")

    for sport in ['nba', 'nhl', 'cbb']:
        sport_arbs = arb_rows[arb_rows['sport'] == sport]
        if len(sport_arbs) > 0:
            avg_spread = sport_arbs['spread'].mean()
            max_spread = sport_arbs['spread'].max()
            report.append(f"- **{sport.upper()}:** {len(sport_arbs):,} arb snapshots, avg spread: {avg_spread:.1f}c, max: {max_spread:.0f}c")

    # Top games by arb frequency
    report.append("\n### Top 10 Games by Arb Frequency\n")

    game_arb_counts = arb_rows.groupby(['game_key', 'sport']).agg({
        'spread': ['count', 'mean', 'max']
    }).reset_index()
    game_arb_counts.columns = ['game_key', 'sport', 'arb_count', 'avg_spread', 'max_spread']
    game_arb_counts = game_arb_counts.sort_values('arb_count', ascending=False).head(10)

    report.append("| Game | Sport | Arb Snapshots | Avg Spread | Max Spread |")
    report.append("|------|-------|---------------|------------|------------|")
    for _, row in game_arb_counts.iterrows():
        game_id = row['game_key'].split(':')[1] if ':' in row['game_key'] else row['game_key']
        report.append(f"| {game_id} | {row['sport'].upper()} | {row['arb_count']:,} | {row['avg_spread']:.1f}c | {row['max_spread']:.0f}c |")

    # ================================================================
    # 3. LIQUIDITY ANALYSIS
    # ================================================================
    report.append("\n---\n## 3. Liquidity Analysis\n")

    # Analyze skipped arbs
    skip_reasons = defaultdict(int)
    skip_by_game = defaultdict(list)
    low_liq_sizes = []

    for arb in skipped:
        reason = arb.get('reason', 'unknown')
        skip_reasons[reason] += 1

        game_key = arb.get('game_key', 'unknown')
        skip_by_game[game_key].append(arb)

        if reason == 'low_liquidity':
            # Extract contract size
            size = arb.get('contracts', 0)
            if size > 0:
                low_liq_sizes.append(size)

    report.append("### Skip Reasons\n")
    report.append("| Reason | Count | Percentage |")
    report.append("|--------|-------|------------|")
    for reason, count in sorted(skip_reasons.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(skipped) if skipped else 0
        report.append(f"| {reason} | {count:,} | {pct:.1f}% |")

    if low_liq_sizes:
        report.append(f"\n### Low Liquidity Skip Analysis\n")
        report.append(f"- **Low liquidity skips:** {len(low_liq_sizes):,}")
        report.append(f"- **Average contract size when skipped:** {statistics.mean(low_liq_sizes):.0f}")
        report.append(f"- **Median contract size when skipped:** {statistics.median(low_liq_sizes):.0f}")

    # Analyze trades for execution sizes
    report.append("\n### Trade Execution Sizes\n")

    trade_sizes = []
    for trade in trades:
        size = trade.get('contracts', 0)
        if size > 0:
            trade_sizes.append(size)

    if trade_sizes:
        report.append(f"- **Trades executed:** {len(trade_sizes):,}")
        report.append(f"- **Average trade size:** {statistics.mean(trade_sizes):.0f} contracts")
        report.append(f"- **Median trade size:** {statistics.median(trade_sizes):.0f} contracts")
        report.append(f"- **Max trade size:** {max(trade_sizes):,} contracts")
        report.append(f"- **Total contracts traded:** {sum(trade_sizes):,}")

    # ================================================================
    # 4. EXECUTION OPTIMIZATION
    # ================================================================
    report.append("\n---\n## 4. Execution Optimization\n")

    # Total profit potential
    total_profit = tam_stats['total_profit_if_captured'] / 100
    total_contracts = tam_stats['total_contracts']

    report.append(f"### TAM Analysis\n")
    report.append(f"- **Total Addressable Market:** ${total_profit:,.2f}")
    report.append(f"- **Total contracts available:** {total_contracts:,}")
    report.append(f"- **Average profit per contract:** ${total_profit/total_contracts:.4f}" if total_contracts > 0 else "")
    report.append(f"- **Unique arbs found:** {tam_stats['unique_arbs_executed']}")
    report.append(f"- **Average profit per arb:** ${total_profit/tam_stats['unique_arbs_executed']:.2f}" if tam_stats['unique_arbs_executed'] > 0 else "")

    # ROI analysis from trades
    report.append("\n### Executed Trades Analysis\n")

    roi_values = []
    spreads_executed = []
    for trade in trades:
        spread = trade.get('spread_cents', 0)
        if spread > 0:
            spreads_executed.append(spread)
            # ROI = spread / cost, assuming cost ~50c average
            roi = spread  # In cents
            roi_values.append(roi)

    if spreads_executed:
        report.append(f"- **Trades with positive spread:** {len(spreads_executed):,}")
        report.append(f"- **Average spread captured:** {statistics.mean(spreads_executed):.1f}c")
        report.append(f"- **Median spread captured:** {statistics.median(spreads_executed):.1f}c")

        # Spread buckets for executed trades
        report.append("\n**Spread Distribution of Executed Trades:**")
        report.append("| Spread | Count | Percentage |")
        report.append("|--------|-------|------------|")

        spread_exec_buckets = {'1-2c': 0, '2-3c': 0, '3-5c': 0, '5-10c': 0, '10c+': 0}
        for s in spreads_executed:
            if s <= 2:
                spread_exec_buckets['1-2c'] += 1
            elif s <= 3:
                spread_exec_buckets['2-3c'] += 1
            elif s <= 5:
                spread_exec_buckets['3-5c'] += 1
            elif s <= 10:
                spread_exec_buckets['5-10c'] += 1
            else:
                spread_exec_buckets['10c+'] += 1

        for bucket, count in spread_exec_buckets.items():
            pct = 100 * count / len(spreads_executed)
            report.append(f"| {bucket} | {count:,} | {pct:.1f}% |")

    # Live games analysis
    report.append("\n### Live Games Analysis\n")

    live_skips = skip_reasons.get('live_game', 0)
    report.append(f"- **Arbs skipped due to live game:** {live_skips:,}")
    report.append(f"- **Percentage of skips:** {100*live_skips/len(skipped):.1f}%" if skipped else "N/A")

    # ================================================================
    # 5. FLICKER ANALYSIS
    # ================================================================
    report.append("\n---\n## 5. Flicker Analysis\n")

    flicker_count = tam_stats.get('flicker_ignored', 0)
    total_arbs = tam_stats.get('unique_arbs_executed', 0)

    report.append(f"- **Flickers ignored:** {flicker_count}")
    report.append(f"- **Unique arbs captured:** {total_arbs}")
    report.append(f"- **Flicker rate:** {100*flicker_count/(flicker_count+total_arbs):.1f}%" if (flicker_count+total_arbs) > 0 else "N/A")

    # Analyze arb durations for flicker patterns
    if arb_durations:
        short_arbs = len([d for d in arb_durations if d < 30])
        report.append(f"\n### Short-lived Arbs (<30 seconds)\n")
        report.append(f"- **Count:** {short_arbs}")
        report.append(f"- **Percentage of all arb periods:** {100*short_arbs/len(arb_durations):.1f}%")
        report.append(f"\nThese short-lived arbs may be API noise or genuine fleeting opportunities.")
        report.append(f"The 30-second cooldown helps avoid chasing these.")

    # ================================================================
    # 6. RECOMMENDATIONS
    # ================================================================
    report.append("\n---\n## 6. Recommendations\n")

    report.append("### Optimal Trading Hours\n")

    # Find hours with highest arb rates
    best_hours = []
    for hour in sorted(hourly_total.index):
        if hourly_total[hour] > 100:  # Enough data
            rate = hourly_arbs.get(hour, 0) / hourly_total[hour]
            best_hours.append((hour, rate))

    best_hours.sort(key=lambda x: -x[1])
    if best_hours:
        report.append(f"Based on arb frequency, the best trading hours are:")
        for hour, rate in best_hours[:5]:
            report.append(f"- **{hour:02d}:00 EST:** {100*rate:.2f}% arb rate")

    report.append("\n### Optimal ROI Threshold\n")

    if spreads_executed:
        avg_spread = statistics.mean(spreads_executed)
        median_spread = statistics.median(spreads_executed)
        report.append(f"- Average spread captured: {avg_spread:.1f}c ({avg_spread/50*100:.1f}% ROI on 50c position)")
        report.append(f"- Median spread captured: {median_spread:.1f}c ({median_spread/50*100:.1f}% ROI)")
        report.append(f"- **Recommendation:** Set minimum spread to 2c (4% ROI) to filter noise while capturing most opportunities")

    report.append("\n### Optimal Position Sizing\n")

    if trade_sizes:
        report.append(f"- Current average position: {statistics.mean(trade_sizes):.0f} contracts")
        report.append(f"- Consider dynamic sizing based on spread: larger positions for wider spreads")
        report.append(f"- **Recommendation:** 50-100 contracts for 2-3c spreads, 100-200 for 3-5c, 200+ for 5c+")

    report.append("\n### Sport Prioritization\n")

    for sport in ['nba', 'nhl', 'cbb']:
        sport_arbs = arb_rows[arb_rows['sport'] == sport]
        sport_total = df[df['sport'] == sport]
        if len(sport_total) > 0:
            arb_rate = 100 * len(sport_arbs) / len(sport_total)
            avg_spread = sport_arbs['spread'].mean() if len(sport_arbs) > 0 else 0
            report.append(f"- **{sport.upper()}:** {arb_rate:.2f}% arb rate, {avg_spread:.1f}c avg spread")

    report.append("\n### Live Games\n")

    report.append(f"- {live_skips:,} arbs skipped due to live game status")
    report.append(f"- Live games often have wider spreads but faster price movement")
    report.append(f"- **Recommendation:** Continue avoiding live games for safety, but consider monitoring for large spreads (>5c)")

    report.append("\n### Flicker Cooldown\n")

    report.append(f"- Current cooldown: 15 seconds (reduced from 30s)")
    if (flicker_count + total_arbs) > 0:
        report.append(f"- {flicker_count} flickers ignored ({100*flicker_count/(flicker_count+total_arbs):.1f}% of potential arbs)")
    else:
        report.append(f"- {flicker_count} flickers ignored")
    if arb_durations:
        median_dur = statistics.median(arb_durations)
        report.append(f"- Median arb duration: {median_dur:.1f}s")
        if median_dur > 60:
            report.append(f"- **Recommendation:** 30s cooldown is appropriate - most arbs last longer")
        else:
            report.append(f"- **Recommendation:** Consider reducing cooldown to 15-20s to capture more short-lived opportunities")

    # ================================================================
    # SUMMARY TABLE
    # ================================================================
    report.append("\n---\n## Summary: Key Metrics\n")

    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Total Scans | {tam_stats['scan_count']:,} |")
    report.append(f"| Runtime | ~{tam_stats['scan_count']/60:.0f} minutes |")
    report.append(f"| Unique Arbs | {tam_stats['unique_arbs_executed']} |")
    report.append(f"| TAM | ${total_profit:,.2f} |")
    report.append(f"| Avg Profit/Arb | ${total_profit/tam_stats['unique_arbs_executed']:.2f} |" if tam_stats['unique_arbs_executed'] > 0 else "| Avg Profit/Arb | N/A |")
    report.append(f"| Total Contracts | {total_contracts:,} |")
    report.append(f"| Flickers Ignored | {flicker_count} |")
    report.append(f"| Low Liquidity Skips | {skip_reasons.get('low_liquidity', 0):,} |")
    report.append(f"| Live Game Skips | {live_skips:,} |")

    # Write report
    report_text = '\n'.join(report)
    with open('analysis_report_20260130.md', 'w') as f:
        f.write(report_text)

    print(f"\nReport written to: analysis_report_20260130.md")
    print(f"Report length: {len(report_text):,} characters")

    return report_text

if __name__ == '__main__':
    analyze_trading_data()
