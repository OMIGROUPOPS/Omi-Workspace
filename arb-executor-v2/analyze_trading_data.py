#!/usr/bin/env python3
"""
Analyze price history data from CSV files to generate trading insights report.
"""

import csv
import glob
import os
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import statistics

@dataclass
class ArbEvent:
    game_key: str
    sport: str
    game_id: str
    team: str
    start_time: float
    end_time: float
    max_spread: float
    direction: str  # "sell_k" or "sell_pm"
    spreads: List[float] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time

    @property
    def duration_str(self) -> str:
        secs = int(self.duration_seconds)
        if secs < 60:
            return f"{secs}s"
        elif secs < 3600:
            return f"{secs // 60}m {secs % 60}s"
        else:
            return f"{secs // 3600}h {(secs % 3600) // 60}m"

    @property
    def avg_spread(self) -> float:
        return statistics.mean(self.spreads) if self.spreads else 0


def load_all_csvs(pattern: str) -> List[dict]:
    """Load all CSV files matching pattern and return combined rows."""
    all_rows = []
    files = sorted(glob.glob(pattern))

    print(f"Found {len(files)} CSV files to analyze")

    for filepath in files:
        try:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  Loading {os.path.basename(filepath)} ({size_mb:.1f} MB)...")

            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    all_rows.append(row)
                    count += 1
                print(f"    -> {count:,} rows")
        except Exception as e:
            print(f"  Error loading {filepath}: {e}")

    return all_rows


def analyze_data(rows: List[dict]) -> dict:
    """Analyze the price history data and return statistics."""

    # Basic stats
    total_rows = len(rows)
    if total_rows == 0:
        return {"error": "No data found"}

    # Parse timestamps
    timestamps = []
    for row in rows:
        try:
            ts = float(row.get('timestamp', 0))
            if ts > 0:
                timestamps.append(ts)
        except:
            pass

    min_ts = min(timestamps) if timestamps else 0
    max_ts = max(timestamps) if timestamps else 0
    time_span_hours = (max_ts - min_ts) / 3600 if max_ts > min_ts else 0

    # Unique games and sports
    games = set()
    sports_games = defaultdict(set)
    sports_rows = defaultdict(list)

    for row in rows:
        game_key = row.get('game_key', '')
        sport = row.get('sport', '').upper()
        game_id = row.get('game_id', '')

        if game_key:
            games.add(game_key)
            sports_games[sport].add(game_key)
            sports_rows[sport].append(row)

    # Arb analysis
    arb_rows = []
    arb_events = []
    current_arb = None

    # Sort rows by timestamp for proper arb duration analysis
    sorted_rows = sorted(rows, key=lambda r: float(r.get('timestamp', 0)))

    for row in sorted_rows:
        try:
            k_bid = float(row.get('kalshi_bid', 0))
            k_ask = float(row.get('kalshi_ask', 0))
            pm_bid = float(row.get('pm_bid', 0))
            pm_ask = float(row.get('pm_ask', 0))
            ts = float(row.get('timestamp', 0))
            game_key = row.get('game_key', '')
            sport = row.get('sport', '').upper()
            game_id = row.get('game_id', '')
            team = row.get('team', '')

            # Check for arb
            sell_k_spread = k_bid - pm_ask  # Sell Kalshi, Buy PM
            sell_pm_spread = pm_bid - k_ask  # Sell PM, Buy Kalshi

            has_arb = sell_k_spread > 0 or sell_pm_spread > 0

            if has_arb:
                spread = max(sell_k_spread, sell_pm_spread)
                direction = "sell_k" if sell_k_spread > sell_pm_spread else "sell_pm"
                arb_rows.append(row)

                # Track arb event
                if current_arb is None or current_arb.game_key != game_key:
                    # New arb event
                    if current_arb:
                        arb_events.append(current_arb)
                    current_arb = ArbEvent(
                        game_key=game_key,
                        sport=sport,
                        game_id=game_id,
                        team=team,
                        start_time=ts,
                        end_time=ts,
                        max_spread=spread,
                        direction=direction,
                        spreads=[spread]
                    )
                else:
                    # Continue existing arb
                    current_arb.end_time = ts
                    current_arb.max_spread = max(current_arb.max_spread, spread)
                    current_arb.spreads.append(spread)
            else:
                if current_arb:
                    arb_events.append(current_arb)
                    current_arb = None

        except Exception as e:
            continue

    if current_arb:
        arb_events.append(current_arb)

    # Time of day analysis
    hourly_arbs = defaultdict(int)
    hourly_total = defaultdict(int)

    for row in sorted_rows:
        try:
            ts = float(row.get('timestamp', 0))
            if ts > 0:
                dt = datetime.fromtimestamp(ts)
                hour = dt.hour
                hourly_total[hour] += 1

                k_bid = float(row.get('kalshi_bid', 0))
                pm_ask = float(row.get('pm_ask', 0))
                pm_bid = float(row.get('pm_bid', 0))
                k_ask = float(row.get('kalshi_ask', 0))

                if k_bid > pm_ask or pm_bid > k_ask:
                    hourly_arbs[hour] += 1
        except:
            pass

    # Sport-specific analysis
    sport_stats = {}
    for sport, sport_rows_list in sports_rows.items():
        arb_count = 0
        spreads = []

        for row in sport_rows_list:
            try:
                k_bid = float(row.get('kalshi_bid', 0))
                pm_ask = float(row.get('pm_ask', 0))
                pm_bid = float(row.get('pm_bid', 0))
                k_ask = float(row.get('kalshi_ask', 0))

                sell_k = k_bid - pm_ask
                sell_pm = pm_bid - k_ask

                if sell_k > 0 or sell_pm > 0:
                    arb_count += 1
                    spreads.append(max(sell_k, sell_pm))
            except:
                pass

        sport_stats[sport] = {
            'games': len(sports_games[sport]),
            'rows': len(sport_rows_list),
            'arb_count': arb_count,
            'arb_pct': (arb_count / len(sport_rows_list) * 100) if sport_rows_list else 0,
            'avg_spread': statistics.mean(spreads) if spreads else 0,
            'max_spread': max(spreads) if spreads else 0,
        }

    # Top arb events
    top_arbs = sorted(arb_events, key=lambda e: e.max_spread, reverse=True)[:20]

    # Games with most arbs
    game_arb_counts = defaultdict(int)
    for event in arb_events:
        game_arb_counts[event.game_key] += 1
    top_games = sorted(game_arb_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        'total_rows': total_rows,
        'time_span_hours': time_span_hours,
        'start_time': datetime.fromtimestamp(min_ts) if min_ts > 0 else None,
        'end_time': datetime.fromtimestamp(max_ts) if max_ts > 0 else None,
        'unique_games': len(games),
        'sports_games': {k: len(v) for k, v in sports_games.items()},
        'arb_rows': len(arb_rows),
        'arb_events': arb_events,
        'arb_pct': (len(arb_rows) / total_rows * 100) if total_rows > 0 else 0,
        'avg_arb_spread': statistics.mean([e.avg_spread for e in arb_events]) if arb_events else 0,
        'max_arb_spread': max([e.max_spread for e in arb_events]) if arb_events else 0,
        'avg_arb_duration': statistics.mean([e.duration_seconds for e in arb_events]) if arb_events else 0,
        'hourly_arbs': dict(hourly_arbs),
        'hourly_total': dict(hourly_total),
        'sport_stats': sport_stats,
        'top_arbs': top_arbs,
        'top_games': top_games,
    }


def generate_report(stats: dict) -> str:
    """Generate markdown report from stats."""

    lines = []
    lines.append("# Trading Data Analysis Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Overview
    lines.append("## 1. OVERVIEW")
    lines.append("")
    lines.append(f"- **Total data points collected:** {stats['total_rows']:,}")
    lines.append(f"- **Time span covered:** {stats['time_span_hours']:.1f} hours")
    if stats.get('start_time'):
        lines.append(f"- **Start time:** {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if stats.get('end_time'):
        lines.append(f"- **End time:** {stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- **Number of games tracked:** {stats['unique_games']}")
    lines.append("")
    lines.append("### Sports Breakdown")
    lines.append("| Sport | Games |")
    lines.append("|-------|-------|")
    for sport, count in sorted(stats['sports_games'].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"| {sport} | {count} |")
    lines.append("")

    # Arb Opportunities
    lines.append("## 2. ARB OPPORTUNITIES")
    lines.append("")
    lines.append(f"- **Total arb data points:** {stats['arb_rows']:,}")
    lines.append(f"- **Arb frequency:** {stats['arb_pct']:.2f}% of all data points")
    lines.append(f"- **Total arb events:** {len(stats['arb_events']):,}")
    lines.append(f"- **Average spread when arb existed:** {stats['avg_arb_spread']:.1f}¢")
    lines.append(f"- **Maximum spread seen:** {stats['max_arb_spread']:.0f}¢")

    if stats['avg_arb_duration'] > 0:
        avg_dur = int(stats['avg_arb_duration'])
        if avg_dur < 60:
            dur_str = f"{avg_dur}s"
        elif avg_dur < 3600:
            dur_str = f"{avg_dur // 60}m {avg_dur % 60}s"
        else:
            dur_str = f"{avg_dur // 3600}h {(avg_dur % 3600) // 60}m"
        lines.append(f"- **Average arb duration:** {dur_str}")
    lines.append("")

    # Games with most arbs
    lines.append("### Games with Most Arb Events")
    lines.append("| Game | Arb Events |")
    lines.append("|------|------------|")
    for game, count in stats['top_games'][:10]:
        lines.append(f"| {game} | {count} |")
    lines.append("")

    # By Sport
    lines.append("## 3. BY SPORT")
    lines.append("")
    for sport, ss in sorted(stats['sport_stats'].items()):
        lines.append(f"### {sport}")
        lines.append(f"- Games tracked: {ss['games']}")
        lines.append(f"- Data points: {ss['rows']:,}")
        lines.append(f"- Arb frequency: {ss['arb_pct']:.2f}%")
        lines.append(f"- Average spread: {ss['avg_spread']:.1f}¢")
        lines.append(f"- Max spread: {ss['max_spread']:.0f}¢")
        lines.append("")

    # Time Analysis
    lines.append("## 4. TIME ANALYSIS")
    lines.append("")
    lines.append("### Arb Frequency by Hour")
    lines.append("| Hour | Arb Points | Total Points | Arb % |")
    lines.append("|------|------------|--------------|-------|")

    for hour in sorted(stats['hourly_total'].keys()):
        arbs = stats['hourly_arbs'].get(hour, 0)
        total = stats['hourly_total'][hour]
        pct = (arbs / total * 100) if total > 0 else 0
        hour_str = f"{hour:02d}:00"
        lines.append(f"| {hour_str} | {arbs:,} | {total:,} | {pct:.2f}% |")
    lines.append("")

    # Best hours
    if stats['hourly_arbs']:
        best_hours = sorted(
            [(h, stats['hourly_arbs'].get(h, 0) / stats['hourly_total'][h] * 100)
             for h in stats['hourly_total'] if stats['hourly_total'][h] > 100],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        if best_hours:
            lines.append("### Best Hours for Arbs")
            for hour, pct in best_hours:
                lines.append(f"- **{hour:02d}:00**: {pct:.2f}% arb frequency")
            lines.append("")

    # Top 10 Arb Opportunities
    lines.append("## 5. TOP 10 ARB OPPORTUNITIES")
    lines.append("")
    lines.append("| Rank | Game | Time | Max Spread | Avg Spread | Duration | Direction |")
    lines.append("|------|------|------|------------|------------|----------|-----------|")

    for i, arb in enumerate(stats['top_arbs'][:10], 1):
        try:
            time_str = datetime.fromtimestamp(arb.start_time).strftime('%m/%d %H:%M')
        except:
            time_str = "N/A"
        direction = "Sell K / Buy PM" if arb.direction == "sell_k" else "Sell PM / Buy K"
        lines.append(f"| {i} | {arb.game_key} | {time_str} | {arb.max_spread:.0f}¢ | {arb.avg_spread:.1f}¢ | {arb.duration_str} | {direction} |")
    lines.append("")

    # Recommendations
    lines.append("## 6. RECOMMENDATIONS")
    lines.append("")

    # Best times
    if stats['hourly_arbs']:
        best_hours = sorted(
            [(h, stats['hourly_arbs'].get(h, 0) / stats['hourly_total'][h] * 100)
             for h in stats['hourly_total'] if stats['hourly_total'][h] > 1000],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        if best_hours:
            hours_str = ", ".join([f"{h:02d}:00" for h, _ in best_hours])
            lines.append(f"### Best Times to Run Bot")
            lines.append(f"Based on arb frequency, prioritize: **{hours_str}**")
            lines.append("")

    # Best sports
    if stats['sport_stats']:
        best_sports = sorted(
            [(s, ss['arb_pct']) for s, ss in stats['sport_stats'].items() if ss['rows'] > 1000],
            key=lambda x: x[1],
            reverse=True
        )
        if best_sports:
            lines.append("### Sports to Prioritize")
            for sport, pct in best_sports[:3]:
                lines.append(f"- **{sport}**: {pct:.2f}% arb frequency")
            lines.append("")

    # Spread threshold
    if stats['top_arbs']:
        profitable_arbs = [a for a in stats['arb_events'] if a.max_spread >= 2]
        if profitable_arbs:
            avg_profitable = statistics.mean([a.max_spread for a in profitable_arbs])
            lines.append("### Optimal Spread Threshold")
            lines.append(f"- Arbs with 2¢+ spread: {len(profitable_arbs):,}")
            lines.append(f"- Average spread of profitable arbs: {avg_profitable:.1f}¢")
            lines.append(f"- **Recommendation:** Set MIN_SPREAD to 2¢ for consistent profits")
            lines.append("")

    # Summary stats
    lines.append("## 7. SUMMARY STATISTICS")
    lines.append("")
    lines.append("```")
    lines.append(f"Total Data Points:     {stats['total_rows']:>12,}")
    lines.append(f"Unique Games:          {stats['unique_games']:>12,}")
    lines.append(f"Time Span:             {stats['time_span_hours']:>11.1f}h")
    lines.append(f"Arb Data Points:       {stats['arb_rows']:>12,}")
    lines.append(f"Arb Events:            {len(stats['arb_events']):>12,}")
    lines.append(f"Arb Frequency:         {stats['arb_pct']:>11.2f}%")
    lines.append(f"Avg Arb Spread:        {stats['avg_arb_spread']:>11.1f}¢")
    lines.append(f"Max Arb Spread:        {stats['max_arb_spread']:>11.0f}¢")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Trading Data Analysis")
    print("=" * 60)
    print()

    # Load all CSV files
    pattern = "price_history*.csv"
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Loading CSV files...")
    rows = load_all_csvs(pattern)

    if not rows:
        print("No data found!")
        return

    print(f"\nTotal rows loaded: {len(rows):,}")
    print("\nAnalyzing data...")

    stats = analyze_data(rows)

    print("\nGenerating report...")
    report = generate_report(stats)

    # Save report
    report_path = "data_analysis_report.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    print(f"Total data points: {stats['total_rows']:,}")
    print(f"Unique games: {stats['unique_games']}")
    print(f"Arb events: {len(stats['arb_events']):,}")
    print(f"Arb frequency: {stats['arb_pct']:.2f}%")
    print(f"Max spread: {stats['max_arb_spread']:.0f}¢")
    print(f"Avg arb spread: {stats['avg_arb_spread']:.1f}¢")


if __name__ == "__main__":
    main()
