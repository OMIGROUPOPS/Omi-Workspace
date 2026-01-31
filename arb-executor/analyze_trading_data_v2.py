#!/usr/bin/env python3
"""
Enhanced Trading Data Analysis with ROI and Capital-Constrained Optimization.
"""

import csv
import glob
import os
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import statistics
import math

# Capital assumptions - ACTUAL SETTINGS
ACCOUNT_BALANCE = 10000  # $10K per account (Kalshi or PM)
TOTAL_CAPITAL = 20000    # $20K total (Kalshi + PM)
POSITION_SIZE_PCT = 0.66  # 66% of available liquidity
EXECUTION_TIME_SECONDS = 5

# Position size limits - ACTUAL SETTINGS
MIN_CONTRACTS = 20       # Skip arbs with fewer contracts available
MAX_CONTRACTS = 100      # Risk limit per trade
TYPICAL_LIQUIDITY = 200  # Typical available contracts on order book

# Fee model: For arb trading (not holding to settlement), fees are minimal
FEE_PER_CONTRACT = 0.002  # 0.2 cents per contract (execution cost estimate)
FEE_PCT_OF_PROFIT = 0.05  # 5% of gross profit for safety margin


@dataclass
class ArbOpportunity:
    game_key: str
    sport: str
    game_id: str
    team: str
    timestamp: float
    kalshi_bid: float
    kalshi_ask: float
    pm_bid: float
    pm_ask: float
    spread: float
    direction: str  # "sell_k" or "sell_pm"

    @property
    def buy_price(self) -> float:
        """Price to buy (lower of the two sides we're buying)."""
        if self.direction == "sell_k":
            return self.pm_ask  # Buy PM
        else:
            return self.kalshi_ask  # Buy Kalshi

    @property
    def roi(self) -> float:
        """ROI as percentage."""
        if self.buy_price <= 0:
            return 0
        return (self.spread / self.buy_price) * 100

    @property
    def max_contracts_by_capital(self) -> int:
        """Max contracts affordable with $10K at this price."""
        if self.buy_price <= 0:
            return 0
        return int(ACCOUNT_BALANCE / (self.buy_price / 100))

    @property
    def realistic_contracts(self) -> int:
        """Realistic contracts considering liquidity, capital, and position limits."""
        # Calculate based on 66% of typical liquidity
        liquidity_based = int(TYPICAL_LIQUIDITY * POSITION_SIZE_PCT)
        # Cap by capital affordability
        capital_based = int(self.max_contracts_by_capital * POSITION_SIZE_PCT)
        # Apply MAX_CONTRACTS limit
        return min(liquidity_based, capital_based, MAX_CONTRACTS)

    @property
    def meets_min_size(self) -> bool:
        """Check if this arb meets minimum contract requirement."""
        return self.realistic_contracts >= MIN_CONTRACTS

    @property
    def realistic_profit(self) -> float:
        """Realistic profit in dollars after fees."""
        gross_profit = self.realistic_contracts * self.spread / 100
        # Execution costs: small per-contract fee for slippage
        execution_fee = self.realistic_contracts * FEE_PER_CONTRACT
        # Safety margin: percentage of gross profit
        safety_margin = gross_profit * FEE_PCT_OF_PROFIT
        return gross_profit - execution_fee - safety_margin


@dataclass
class ArbEvent:
    game_key: str
    sport: str
    game_id: str
    team: str
    start_time: float
    end_time: float
    max_spread: float
    direction: str
    opportunities: List[ArbOpportunity] = field(default_factory=list)

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
        return statistics.mean([o.spread for o in self.opportunities]) if self.opportunities else 0

    @property
    def avg_roi(self) -> float:
        rois = [o.roi for o in self.opportunities if o.roi > 0]
        return statistics.mean(rois) if rois else 0

    @property
    def max_roi(self) -> float:
        rois = [o.roi for o in self.opportunities if o.roi > 0]
        return max(rois) if rois else 0

    @property
    def total_realistic_profit(self) -> float:
        return sum(o.realistic_profit for o in self.opportunities)


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
    """Analyze the price history data and return comprehensive statistics."""

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

        if game_key:
            games.add(game_key)
            sports_games[sport].add(game_key)
            sports_rows[sport].append(row)

    # Arb analysis with ROI
    all_opportunities = []
    arb_events = []
    current_arb = None

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

            sell_k_spread = k_bid - pm_ask
            sell_pm_spread = pm_bid - k_ask

            has_arb = sell_k_spread > 0 or sell_pm_spread > 0

            if has_arb:
                spread = max(sell_k_spread, sell_pm_spread)
                direction = "sell_k" if sell_k_spread > sell_pm_spread else "sell_pm"

                opp = ArbOpportunity(
                    game_key=game_key,
                    sport=sport,
                    game_id=game_id,
                    team=team,
                    timestamp=ts,
                    kalshi_bid=k_bid,
                    kalshi_ask=k_ask,
                    pm_bid=pm_bid,
                    pm_ask=pm_ask,
                    spread=spread,
                    direction=direction
                )
                all_opportunities.append(opp)

                if current_arb is None or current_arb.game_key != game_key:
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
                        opportunities=[opp]
                    )
                else:
                    current_arb.end_time = ts
                    current_arb.max_spread = max(current_arb.max_spread, spread)
                    current_arb.opportunities.append(opp)
            else:
                if current_arb:
                    arb_events.append(current_arb)
                    current_arb = None

        except Exception as e:
            continue

    if current_arb:
        arb_events.append(current_arb)

    # ROI distribution
    roi_buckets = {
        '0-2%': 0, '2-5%': 0, '5-10%': 0, '10-15%': 0,
        '15-20%': 0, '20-30%': 0, '30%+': 0
    }

    for opp in all_opportunities:
        roi = opp.roi
        if roi < 2:
            roi_buckets['0-2%'] += 1
        elif roi < 5:
            roi_buckets['2-5%'] += 1
        elif roi < 10:
            roi_buckets['5-10%'] += 1
        elif roi < 15:
            roi_buckets['10-15%'] += 1
        elif roi < 20:
            roi_buckets['15-20%'] += 1
        elif roi < 30:
            roi_buckets['20-30%'] += 1
        else:
            roi_buckets['30%+'] += 1

    # ROI by sport
    sport_rois = defaultdict(list)
    for opp in all_opportunities:
        if opp.roi > 0:
            sport_rois[opp.sport].append(opp.roi)

    sport_avg_roi = {sport: statistics.mean(rois) for sport, rois in sport_rois.items() if rois}

    # ROI by hour
    hourly_rois = defaultdict(list)
    hourly_arbs = defaultdict(int)
    hourly_total = defaultdict(int)
    hourly_profits = defaultdict(float)

    for row in sorted_rows:
        try:
            ts = float(row.get('timestamp', 0))
            if ts > 0:
                dt = datetime.fromtimestamp(ts)
                hour = dt.hour
                hourly_total[hour] += 1
        except:
            pass

    for opp in all_opportunities:
        try:
            dt = datetime.fromtimestamp(opp.timestamp)
            hour = dt.hour
            hourly_arbs[hour] += 1
            hourly_rois[hour].append(opp.roi)
            hourly_profits[hour] += opp.realistic_profit
        except:
            pass

    hourly_avg_roi = {h: statistics.mean(rois) for h, rois in hourly_rois.items() if rois}

    # Sport-specific stats
    sport_stats = {}
    for sport, sport_rows_list in sports_rows.items():
        sport_opps = [o for o in all_opportunities if o.sport == sport]
        spreads = [o.spread for o in sport_opps]
        rois = [o.roi for o in sport_opps if o.roi > 0]
        profits = [o.realistic_profit for o in sport_opps]

        sport_stats[sport] = {
            'games': len(sports_games[sport]),
            'rows': len(sport_rows_list),
            'arb_count': len(sport_opps),
            'arb_pct': (len(sport_opps) / len(sport_rows_list) * 100) if sport_rows_list else 0,
            'avg_spread': statistics.mean(spreads) if spreads else 0,
            'max_spread': max(spreads) if spreads else 0,
            'avg_roi': statistics.mean(rois) if rois else 0,
            'max_roi': max(rois) if rois else 0,
            'total_profit': sum(profits),
            'avg_profit': statistics.mean(profits) if profits else 0,
        }

    # Spread threshold analysis
    spread_thresholds = {}
    for threshold in [1, 2, 3, 5]:
        filtered = [o for o in all_opportunities if o.spread >= threshold]
        profits = [o.realistic_profit for o in filtered]
        spread_thresholds[threshold] = {
            'count': len(filtered),
            'total_profit': sum(profits),
            'avg_profit': statistics.mean(profits) if profits else 0,
            'avg_roi': statistics.mean([o.roi for o in filtered if o.roi > 0]) if filtered else 0,
        }

    # Top arbs by ROI
    top_by_roi = sorted(all_opportunities, key=lambda o: o.roi, reverse=True)[:50]

    # Top arbs by spread
    top_by_spread = sorted(all_opportunities, key=lambda o: o.spread, reverse=True)[:20]

    # Top games by arb count
    game_arb_counts = defaultdict(int)
    game_profits = defaultdict(float)
    for opp in all_opportunities:
        game_arb_counts[opp.game_key] += 1
        game_profits[opp.game_key] += opp.realistic_profit

    top_games = sorted(game_arb_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_games_profit = sorted(game_profits.items(), key=lambda x: x[1], reverse=True)[:10]

    # Capital utilization analysis
    total_realistic_profit = sum(o.realistic_profit for o in all_opportunities)
    avg_position_size = statistics.mean([o.realistic_contracts for o in all_opportunities]) if all_opportunities else 0
    avg_position_value = statistics.mean([o.realistic_contracts * o.buy_price / 100 for o in all_opportunities if o.buy_price > 0]) if all_opportunities else 0

    # Estimate arbs per hour (executable, not overlapping)
    arbs_per_hour = len(all_opportunities) / time_span_hours if time_span_hours > 0 else 0
    executable_per_hour = min(arbs_per_hour, 3600 / EXECUTION_TIME_SECONDS)  # Max possible executions

    # REALISTIC execution model: Only count FIRST occurrence of each arb event
    # Constraint 1: 5-second cooldown per game
    # Constraint 2: Global 5-second cooldown (one trade at a time)
    executed_arbs = []
    last_execution_by_game = {}  # game_key -> last execution timestamp
    last_global_execution = 0     # global cooldown

    for opp in sorted(all_opportunities, key=lambda o: o.timestamp):
        game = opp.game_key
        last_game_exec = last_execution_by_game.get(game, 0)

        # Must wait 5+ seconds since last execution on this game AND globally
        if (opp.timestamp - last_game_exec >= EXECUTION_TIME_SECONDS and
            opp.timestamp - last_global_execution >= EXECUTION_TIME_SECONDS):
            executed_arbs.append(opp)
            last_execution_by_game[game] = opp.timestamp
            last_global_execution = opp.timestamp

    # Executed profit is from discrete, non-overlapping executions
    executed_profit = sum(o.realistic_profit for o in executed_arbs)
    executed_per_hour = len(executed_arbs) / time_span_hours if time_span_hours > 0 else 0

    # Daily profit projections
    prime_hours = [19, 20, 21, 22]  # 7-10 PM
    prime_opps = [o for o in all_opportunities if datetime.fromtimestamp(o.timestamp).hour in prime_hours]
    prime_profit = sum(o.realistic_profit for o in prime_opps)
    prime_hours_in_data = sum(1 for h in prime_hours if h in hourly_total)

    # Prime hours executed
    prime_executed = [o for o in executed_arbs if datetime.fromtimestamp(o.timestamp).hour in prime_hours]
    prime_executed_profit = sum(o.realistic_profit for o in prime_executed)

    # Filter to arbs meeting MIN_CONTRACTS requirement
    valid_executed = [o for o in executed_arbs if o.meets_min_size]
    valid_executed_profit = sum(o.realistic_profit for o in valid_executed)

    # Prime hours with valid size
    prime_valid = [o for o in valid_executed if datetime.fromtimestamp(o.timestamp).hour in prime_hours]
    prime_valid_profit = sum(o.realistic_profit for o in prime_valid)

    # Calculate prime hours stats
    prime_hours_data = sum(1 for h in prime_hours if hourly_total.get(h, 0) > 0)
    prime_arbs_per_hour = len(prime_valid) / prime_hours_data if prime_hours_data > 0 else 0

    # CONTRACT CAP COMPARISON - Calculate profits at different max contract levels
    def calc_profit_at_cap(arbs, max_cap):
        """Calculate profit with a specific contract cap."""
        total = 0
        for opp in arbs:
            contracts = min(opp.realistic_contracts, max_cap)
            if contracts >= MIN_CONTRACTS:
                gross = contracts * opp.spread / 100
                fees = contracts * FEE_PER_CONTRACT + gross * FEE_PCT_OF_PROFIT
                total += gross - fees
        return total

    contract_cap_comparison = {}
    for cap in [50, 100, 200]:
        # Calculate for all executed arbs
        total_profit = calc_profit_at_cap(executed_arbs, cap)
        prime_profit_cap = calc_profit_at_cap(prime_executed, cap)

        # Count valid arbs at this cap
        valid_count = sum(1 for o in executed_arbs if min(o.realistic_contracts, cap) >= MIN_CONTRACTS)
        prime_valid_count = sum(1 for o in prime_executed if min(o.realistic_contracts, cap) >= MIN_CONTRACTS)

        # Daily estimates (3 prime hours, 70% success rate)
        if prime_hours_data > 0:
            hourly_profit = prime_profit_cap / prime_hours_data
            daily_profit = hourly_profit * 3 * 0.70  # 3 hours, 70% success
        else:
            daily_profit = 0

        contract_cap_comparison[cap] = {
            'total_profit': total_profit,
            'prime_profit': prime_profit_cap,
            'valid_count': valid_count,
            'prime_valid_count': prime_valid_count,
            'daily_profit': daily_profit,
            'monthly_profit': daily_profit * 30,
            'annual_profit': daily_profit * 365,
            'annual_roi': (daily_profit * 365 / TOTAL_CAPITAL * 100) if TOTAL_CAPITAL > 0 else 0,
        }

    return {
        'total_rows': total_rows,
        'time_span_hours': time_span_hours,
        'start_time': datetime.fromtimestamp(min_ts) if min_ts > 0 else None,
        'end_time': datetime.fromtimestamp(max_ts) if max_ts > 0 else None,
        'unique_games': len(games),
        'sports_games': {k: len(v) for k, v in sports_games.items()},
        'all_opportunities': all_opportunities,
        'arb_events': arb_events,
        'arb_rows': len(all_opportunities),
        'arb_pct': (len(all_opportunities) / total_rows * 100) if total_rows > 0 else 0,
        'avg_arb_spread': statistics.mean([o.spread for o in all_opportunities]) if all_opportunities else 0,
        'max_arb_spread': max([o.spread for o in all_opportunities]) if all_opportunities else 0,
        'avg_arb_duration': statistics.mean([e.duration_seconds for e in arb_events]) if arb_events else 0,
        'roi_buckets': roi_buckets,
        'sport_avg_roi': sport_avg_roi,
        'hourly_arbs': dict(hourly_arbs),
        'hourly_total': dict(hourly_total),
        'hourly_avg_roi': hourly_avg_roi,
        'hourly_profits': dict(hourly_profits),
        'sport_stats': sport_stats,
        'spread_thresholds': spread_thresholds,
        'top_by_roi': top_by_roi,
        'top_by_spread': top_by_spread,
        'top_games': top_games,
        'top_games_profit': top_games_profit,
        'total_realistic_profit': total_realistic_profit,
        'avg_position_size': avg_position_size,
        'avg_position_value': avg_position_value,
        'arbs_per_hour': arbs_per_hour,
        'executable_per_hour': executable_per_hour,
        'prime_profit': prime_profit,
        'prime_hours_in_data': prime_hours_in_data,
        # Realistic execution model
        'executed_arbs': executed_arbs,
        'executed_count': len(executed_arbs),
        'executed_profit': executed_profit,
        'executed_per_hour': executed_per_hour,
        'prime_executed_profit': prime_executed_profit,
        'prime_executed_count': len(prime_executed),
        # Filtered by MIN_CONTRACTS
        'valid_executed': valid_executed,
        'valid_executed_count': len(valid_executed),
        'valid_executed_profit': valid_executed_profit,
        'prime_valid_count': len(prime_valid),
        'prime_valid_profit': prime_valid_profit,
        'prime_arbs_per_hour': prime_arbs_per_hour,
        'prime_hours_data': prime_hours_data,
        # Contract cap comparison
        'contract_cap_comparison': contract_cap_comparison,
    }


def generate_report(stats: dict) -> str:
    """Generate comprehensive markdown report."""

    lines = []
    lines.append("# Trading Data Analysis Report v2")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n**Capital Assumptions:** ${ACCOUNT_BALANCE:,} per account, ${TOTAL_CAPITAL:,} total")
    lines.append("")

    # Section 1: Overview
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

    # Section 2: Arb Opportunities
    lines.append("## 2. ARB OPPORTUNITIES")
    lines.append("")
    lines.append(f"- **Total arb data points:** {stats['arb_rows']:,}")
    lines.append(f"- **Arb frequency:** {stats['arb_pct']:.2f}% of all data points")
    lines.append(f"- **Total arb events:** {len(stats['arb_events']):,}")
    lines.append(f"- **Average spread:** {stats['avg_arb_spread']:.1f}c")
    lines.append(f"- **Maximum spread:** {stats['max_arb_spread']:.0f}c")
    lines.append("")

    lines.append("### Games with Most Arb Events")
    lines.append("| Game | Arb Count |")
    lines.append("|------|-----------|")
    for game, count in stats['top_games'][:10]:
        lines.append(f"| {game} | {count:,} |")
    lines.append("")

    # Section 3: By Sport
    lines.append("## 3. BY SPORT")
    lines.append("")
    for sport, ss in sorted(stats['sport_stats'].items()):
        lines.append(f"### {sport}")
        lines.append(f"- Games tracked: {ss['games']}")
        lines.append(f"- Data points: {ss['rows']:,}")
        lines.append(f"- Arb frequency: {ss['arb_pct']:.2f}%")
        lines.append(f"- Average spread: {ss['avg_spread']:.1f}c")
        lines.append(f"- Max spread: {ss['max_spread']:.0f}c")
        lines.append(f"- Average ROI: {ss['avg_roi']:.1f}%")
        lines.append(f"- Max ROI: {ss['max_roi']:.1f}%")
        lines.append(f"- Total realistic profit: ${ss['total_profit']:.2f}")
        lines.append("")

    # Section 4: Time Analysis
    lines.append("## 4. TIME ANALYSIS")
    lines.append("")
    lines.append("### Arb Frequency by Hour")
    lines.append("| Hour | Arbs | Total | Arb % | Avg ROI | Est. Profit |")
    lines.append("|------|------|-------|-------|---------|-------------|")

    for hour in sorted(stats['hourly_total'].keys()):
        arbs = stats['hourly_arbs'].get(hour, 0)
        total = stats['hourly_total'][hour]
        pct = (arbs / total * 100) if total > 0 else 0
        avg_roi = stats['hourly_avg_roi'].get(hour, 0)
        profit = stats['hourly_profits'].get(hour, 0)
        lines.append(f"| {hour:02d}:00 | {arbs:,} | {total:,} | {pct:.1f}% | {avg_roi:.1f}% | ${profit:.2f} |")
    lines.append("")

    # Section 5: Top 10 by Spread
    lines.append("## 5. TOP 10 ARB OPPORTUNITIES (by Spread)")
    lines.append("")
    lines.append("| Rank | Game | Time | Spread | ROI | Direction | Est. Profit |")
    lines.append("|------|------|------|--------|-----|-----------|-------------|")

    for i, opp in enumerate(stats['top_by_spread'][:10], 1):
        try:
            time_str = datetime.fromtimestamp(opp.timestamp).strftime('%m/%d %H:%M')
        except:
            time_str = "N/A"
        direction = "Sell K" if opp.direction == "sell_k" else "Sell PM"
        lines.append(f"| {i} | {opp.game_key} | {time_str} | {opp.spread:.0f}c | {opp.roi:.1f}% | {direction} | ${opp.realistic_profit:.2f} |")
    lines.append("")

    # Section 6: Recommendations (basic)
    lines.append("## 6. BASIC RECOMMENDATIONS")
    lines.append("")

    best_hours = sorted(
        [(h, stats['hourly_arbs'].get(h, 0) / stats['hourly_total'][h] * 100)
         for h in stats['hourly_total'] if stats['hourly_total'][h] > 1000],
        key=lambda x: x[1],
        reverse=True
    )[:3]

    if best_hours:
        hours_str = ", ".join([f"{h:02d}:00" for h, _ in best_hours])
        lines.append(f"### Best Hours: {hours_str}")
        lines.append("")

    best_sports = sorted(
        [(s, ss['arb_pct']) for s, ss in stats['sport_stats'].items() if ss['rows'] > 1000],
        key=lambda x: x[1],
        reverse=True
    )
    if best_sports:
        lines.append("### Sports Priority")
        for sport, pct in best_sports[:3]:
            lines.append(f"- **{sport}**: {pct:.2f}% arb frequency")
        lines.append("")

    # =========================================================================
    # NEW SECTIONS
    # =========================================================================

    # Section 8: ROI Analysis
    lines.append("## 8. ROI ANALYSIS")
    lines.append("")
    lines.append("ROI = spread / buy_price * 100")
    lines.append("")

    lines.append("### ROI Distribution")
    lines.append("| ROI Range | Count | Percentage |")
    lines.append("|-----------|-------|------------|")
    total_opps = sum(stats['roi_buckets'].values())
    for bucket, count in stats['roi_buckets'].items():
        pct = (count / total_opps * 100) if total_opps > 0 else 0
        lines.append(f"| {bucket} | {count:,} | {pct:.1f}% |")
    lines.append("")

    lines.append("### Average ROI by Sport")
    lines.append("| Sport | Avg ROI | Max ROI |")
    lines.append("|-------|---------|---------|")
    for sport, ss in sorted(stats['sport_stats'].items(), key=lambda x: x[1]['avg_roi'], reverse=True):
        lines.append(f"| {sport} | {ss['avg_roi']:.1f}% | {ss['max_roi']:.1f}% |")
    lines.append("")

    lines.append("### Average ROI by Hour")
    lines.append("| Hour | Avg ROI | Arb Count |")
    lines.append("|------|---------|-----------|")
    for hour in sorted(stats['hourly_avg_roi'].keys()):
        roi = stats['hourly_avg_roi'][hour]
        count = stats['hourly_arbs'].get(hour, 0)
        if count > 100:
            lines.append(f"| {hour:02d}:00 | {roi:.1f}% | {count:,} |")
    lines.append("")

    lines.append("### Top 20 Arbs by ROI")
    lines.append("| Rank | Game | Spread | Buy Price | ROI | Profit |")
    lines.append("|------|------|--------|-----------|-----|--------|")
    for i, opp in enumerate(stats['top_by_roi'][:20], 1):
        lines.append(f"| {i} | {opp.game_key} | {opp.spread:.0f}c | {opp.buy_price:.0f}c | {opp.roi:.1f}% | ${opp.realistic_profit:.2f} |")
    lines.append("")

    # Section 9: Capital-Constrained Analysis
    lines.append("## 9. CAPITAL-CONSTRAINED ANALYSIS")
    lines.append("")
    lines.append(f"**Assumptions:** ${ACCOUNT_BALANCE:,} per account, {POSITION_SIZE_PCT*100:.0f}% position sizing, {TYPICAL_LIQUIDITY} typical liquidity")
    lines.append("")

    lines.append("### Position Sizing Examples")
    lines.append("| Buy Price | Max Contracts | With 66% | With Liquidity Cap |")
    lines.append("|-----------|---------------|----------|-------------------|")
    for price in [20, 30, 40, 50, 60, 70, 80]:
        max_c = int(ACCOUNT_BALANCE / (price / 100))
        with_66 = int(max_c * POSITION_SIZE_PCT)
        with_liq = min(with_66, int(TYPICAL_LIQUIDITY * POSITION_SIZE_PCT))
        lines.append(f"| {price}c | {max_c:,} | {with_66:,} | {with_liq:,} |")
    lines.append("")

    lines.append("### Raw Data (All Arb Data Points)")
    lines.append(f"- **Total arb data points:** {stats['arb_rows']:,}")
    lines.append(f"- **Sum of all arb profits (theoretical max):** ${stats['total_realistic_profit']:,.2f}")
    lines.append(f"- **Arbs per hour (raw data):** {stats['arbs_per_hour']:.1f}")
    lines.append("")

    lines.append("### Realistic Execution Model")
    lines.append("*Constraints: 5-second cooldown per game, one trade at a time*")
    lines.append("")
    lines.append(f"- **Executable arbs (5s cooldown):** {stats['executed_count']:,}")
    lines.append(f"- **REALISTIC TOTAL PROFIT:** ${stats['executed_profit']:,.2f}")
    lines.append(f"- **Arbs per hour (executable):** {stats['executed_per_hour']:.1f}")
    lines.append(f"- **Average position size:** {stats['avg_position_size']:.0f} contracts")
    lines.append(f"- **Average profit per executed arb:** ${stats['executed_profit']/stats['executed_count']:.2f}" if stats['executed_count'] > 0 else "")
    lines.append("")

    # Estimate daily profit using executed arbs
    daily_profit_estimate = stats['executed_profit'] / (stats['time_span_hours'] / 24) if stats['time_span_hours'] > 0 else 0
    prime_daily = stats['prime_executed_profit'] / (stats['prime_hours_in_data'] / 4) if stats['prime_hours_in_data'] > 0 else 0

    lines.append("### Daily Profit Potential (Realistic)")
    lines.append(f"- **Extrapolated daily profit (24h):** ${daily_profit_estimate:,.2f}")
    lines.append(f"- **Prime hours profit in data (7-10 PM):** ${stats['prime_executed_profit']:,.2f}")
    lines.append(f"- **Prime hours extrapolated (4h/day):** ${prime_daily:,.2f}")
    lines.append("")

    # Section 10: Optimal Trading Rules
    lines.append("## 10. OPTIMAL TRADING RULES FOR $10K ACCOUNTS")
    lines.append("")

    lines.append("### 1. MIN_SPREAD Threshold Analysis")
    lines.append("| Threshold | Arb Count | Total Profit | Avg Profit | Avg ROI |")
    lines.append("|-----------|-----------|--------------|------------|---------|")
    for thresh, data in sorted(stats['spread_thresholds'].items()):
        lines.append(f"| {thresh}c | {data['count']:,} | ${data['total_profit']:,.2f} | ${data['avg_profit']:.2f} | {data['avg_roi']:.1f}% |")
    lines.append("")

    # Find optimal threshold
    best_thresh = max(stats['spread_thresholds'].items(), key=lambda x: x[1]['total_profit'])
    lines.append(f"**Recommendation:** MIN_SPREAD = **{best_thresh[0]}c** (highest total profit)")
    lines.append("")

    lines.append("### 2. MAX_POSITION_SIZE")
    lines.append(f"- At typical 50c price: {int(ACCOUNT_BALANCE / 0.5):,} contracts max")
    lines.append(f"- With 66% sizing: {int(ACCOUNT_BALANCE / 0.5 * POSITION_SIZE_PCT):,} contracts")
    lines.append(f"- **Recommendation:** MAX_POSITION_SIZE = **{int(TYPICAL_LIQUIDITY * POSITION_SIZE_PCT)}** (liquidity-limited)")
    lines.append("")

    lines.append("### 3. POSITION_SIZING_PERCENT")
    lines.append("- Current: 66%")
    lines.append("- Analysis: Liquidity is the limiting factor, not capital")
    lines.append("- **Recommendation:** Keep at **66%** for safety margin")
    lines.append("")

    lines.append("### 4. CONCURRENT_POSITIONS")
    lines.append("- Execution time: ~5 seconds per trade")
    lines.append("- Arb duration: Often < 10 seconds")
    lines.append("- **Recommendation:** Focus on **one position at a time** to avoid stale fills")
    lines.append("")

    lines.append("### 5. TIME_FILTERS")
    prime_pct = (stats['prime_profit'] / stats['total_realistic_profit'] * 100) if stats['total_realistic_profit'] > 0 else 0
    lines.append(f"- Prime hours (7-10 PM) captured {prime_pct:.1f}% of total profit")
    lines.append("- **Recommendation:** Run **6 PM - midnight** for best ROI on effort")
    lines.append("")

    lines.append("### 6. SPORT_PRIORITY")
    sport_profit_rank = sorted(stats['sport_stats'].items(), key=lambda x: x[1]['total_profit'], reverse=True)
    lines.append("By total profit potential:")
    for i, (sport, ss) in enumerate(sport_profit_rank, 1):
        lines.append(f"{i}. **{sport}**: ${ss['total_profit']:.2f} ({ss['arb_pct']:.1f}% frequency)")
    lines.append("")

    # Section 11: Projected Returns with Contract Caps
    lines.append("## 11. PROJECTED RETURNS BY CONTRACT CAP")
    lines.append("")
    lines.append(f"*Settings: MIN_CONTRACTS={MIN_CONTRACTS}, 5-second cooldown, 70% success rate*")
    lines.append(f"*Prime hours: 7-10 PM (3 hours/day)*")
    lines.append("")

    # Contract cap comparison table
    lines.append("### Contract Cap Comparison")
    lines.append("")
    lines.append("| Scenario | Max Contracts | Valid Arbs | Daily Profit | Monthly | Annual | ROI on $20K |")
    lines.append("|----------|---------------|------------|--------------|---------|--------|-------------|")

    cap_comparison = stats['contract_cap_comparison']
    scenarios = [
        ("Conservative", 50),
        ("Moderate", 100),
        ("Aggressive", 200),
    ]

    for name, cap in scenarios:
        data = cap_comparison[cap]
        lines.append(f"| {name} | {cap} | {data['prime_valid_count']:,} | ${data['daily_profit']:.2f} | ${data['monthly_profit']:,.2f} | ${data['annual_profit']:,.2f} | {data['annual_roi']:.0f}% |")
    lines.append("")

    # Detailed breakdown for 100 contract cap (moderate)
    mod_data = cap_comparison[100]
    lines.append("### Moderate Scenario Details (100 Contract Cap)")
    lines.append("")
    lines.append(f"- **Prime hours in data:** {stats['prime_hours_data']} hours")
    lines.append(f"- **Arbs per hour (prime, 20+ contracts):** {stats['prime_arbs_per_hour']:.1f}")
    lines.append(f"- **Total profit in data (prime hours):** ${mod_data['prime_profit']:.2f}")
    lines.append(f"- **Avg profit per valid arb:** ${mod_data['prime_profit']/mod_data['prime_valid_count']:.2f}" if mod_data['prime_valid_count'] > 0 else "")
    lines.append("")

    lines.append("### Daily Profit Calculation")
    lines.append("```")
    hourly_profit = mod_data['prime_profit'] / stats['prime_hours_data'] if stats['prime_hours_data'] > 0 else 0
    lines.append(f"Hourly profit (from data):     ${hourly_profit:.2f}")
    lines.append(f"Prime hours per day:           3 hours (7-10 PM)")
    lines.append(f"Gross daily:                   ${hourly_profit * 3:.2f}")
    lines.append(f"Success rate adjustment:       70%")
    lines.append(f"Net daily profit:              ${mod_data['daily_profit']:.2f}")
    lines.append("```")
    lines.append("")

    # Capital at risk
    lines.append("### Capital at Risk per Trade")
    lines.append("")
    lines.append("| Max Contracts | Avg Price | Capital/Trade | Max Daily Trades | Max Capital Exposure |")
    lines.append("|---------------|-----------|---------------|------------------|---------------------|")
    for cap in [50, 100, 200]:
        capital_per = cap * 0.50  # 50¢ avg price
        max_trades = int(ACCOUNT_BALANCE / capital_per)
        max_exposure = min(capital_per * 10, ACCOUNT_BALANCE)  # ~10 concurrent max
        lines.append(f"| {cap} | 50¢ | ${capital_per:.0f} | {max_trades} | ${max_exposure:.0f} |")
    lines.append("")

    # Break-even analysis
    mod_data = stats['contract_cap_comparison'][100]
    mod_daily = mod_data['daily_profit']

    lines.append("### Break-Even Analysis")
    lines.append("")
    if mod_daily > 0:
        breakeven_days = TOTAL_CAPITAL / mod_daily
        lines.append(f"- Days to recover $20K capital (moderate): **{breakeven_days:.0f} days**")
        lines.append(f"- Days to recover $10K (one side fails): **{breakeven_days/2:.0f} days**")
    lines.append("")

    lines.append("## 12. SUMMARY STATISTICS")
    lines.append("")
    lines.append("```")
    lines.append(f"Total Data Points:        {stats['total_rows']:>12,}")
    lines.append(f"Unique Games:             {stats['unique_games']:>12,}")
    lines.append(f"Time Span:                {stats['time_span_hours']:>11.1f}h")
    lines.append(f"Arb Data Points:          {stats['arb_rows']:>12,}")
    lines.append(f"Executable Arbs (5s):     {stats['executed_count']:>12,}")
    lines.append(f"Valid Arbs (20+ size):    {stats['valid_executed_count']:>12,}")
    lines.append(f"Arb Frequency:            {stats['arb_pct']:>11.2f}%")
    lines.append(f"Avg Arb Spread:           {stats['avg_arb_spread']:>11.1f}c")
    lines.append(f"Max Arb Spread:           {stats['max_arb_spread']:>11.0f}c")
    lines.append("```")
    lines.append("")
    lines.append("### Realistic Profit (100 Contract Cap, 70% Success)")
    lines.append("```")
    lines.append(f"Prime Hours Valid Arbs:   {mod_data['prime_valid_count']:>12,}")
    lines.append(f"Prime Hours Profit:       ${mod_data['prime_profit']:>10,.2f}")
    lines.append(f"Est. Daily Profit:        ${mod_data['daily_profit']:>10,.2f}")
    lines.append(f"Est. Monthly Profit:      ${mod_data['monthly_profit']:>10,.2f}")
    lines.append(f"Est. Annual Profit:       ${mod_data['annual_profit']:>10,.2f}")
    lines.append(f"Est. Annual ROI:          {mod_data['annual_roi']:>10.0f}%")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Enhanced Trading Data Analysis v2")
    print("=" * 60)
    print()

    pattern = "price_history*.csv"
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Loading CSV files...")
    rows = load_all_csvs(pattern)

    if not rows:
        print("No data found!")
        return

    print(f"\nTotal rows loaded: {len(rows):,}")
    print("\nAnalyzing data (this may take a minute)...")

    stats = analyze_data(rows)

    print("\nGenerating report...")
    report = generate_report(stats)

    report_path = "data_analysis_report_v2.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")
    print("\n" + "=" * 60)
    print("QUICK SUMMARY (100 Contract Cap, MIN_CONTRACTS=20)")
    print("=" * 60)
    print(f"Total data points: {stats['total_rows']:,}")
    print(f"Arb data points: {stats['arb_rows']:,}")
    print(f"Executable arbs (5s cooldown): {stats['executed_count']:,}")
    print(f"Valid arbs (20+ contracts): {stats['valid_executed_count']:,}")
    print(f"Prime hours valid arbs: {stats['prime_valid_count']:,}")
    print(f"Avg spread: {stats['avg_arb_spread']:.1f}c")

    # Contract cap comparison
    print("\n" + "-" * 60)
    print("CONTRACT CAP COMPARISON (Prime Hours, 70% Success Rate)")
    print("-" * 60)
    print(f"{'Scenario':<15} {'Cap':>5} {'Daily':>12} {'Monthly':>12} {'Annual ROI':>12}")
    print("-" * 60)
    for name, cap in [("Conservative", 50), ("Moderate", 100), ("Aggressive", 200)]:
        data = stats['contract_cap_comparison'][cap]
        print(f"{name:<15} {cap:>5} ${data['daily_profit']:>10,.2f} ${data['monthly_profit']:>10,.2f} {data['annual_roi']:>10.0f}%")
    print("-" * 60)

    mod = stats['contract_cap_comparison'][100]
    print(f"\nMODERATE (100 cap): ${mod['daily_profit']:.2f}/day, ${mod['monthly_profit']:,.2f}/month, {mod['annual_roi']:.0f}% annual ROI")


if __name__ == "__main__":
    main()
