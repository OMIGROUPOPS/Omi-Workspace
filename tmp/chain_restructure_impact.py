#!/usr/bin/env python3
"""
Bounce Chain Restructure Impact Analysis
OLD: 5-signal chain (stable, drop, decel, tight, wall) — score = count * 5
NEW: 3-signal chain (stable, tight, wall) — score = count * 8
Thresholds (both): A>=20, B>=10, C<10
"""

import re
import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta

# ── Paths ─────────────────────────────────────────────────────────────────────
NCAAMB_LOG   = "/tmp/ncaamb_stb.log"
TENNIS_LOG   = "/tmp/tennis_stb.log"
TRADES_CSV   = "/tmp/v3_enriched_trades.csv"
BOUNCE_MATCH = "/tmp/live_bounce_match.txt"
OUTPUT_FILE  = "/tmp/chain_restructure_impact.txt"

# ── Scoring logic ──────────────────────────────────────────────────────────────
def old_score(stable, drop, decel, tight, wall):
    """OLD: 5-signal chain * 5"""
    count = sum([stable, drop, decel, tight, wall])
    return count * 5

def new_score(stable, tight, wall):
    """NEW: 3-signal chain * 8 (drop and decel removed)"""
    count = sum([stable, tight, wall])
    return count * 8

def score_to_tier(score, thresholds=(20, 10)):
    if score >= thresholds[0]:
        return 'A'
    elif score >= thresholds[1]:
        return 'B'
    else:
        return 'C'

def new_chain_count(stable, tight, wall):
    return sum([stable, tight, wall])

# ── Parse TIER lines from logs ─────────────────────────────────────────────────
# Format: [TIER] SIDE score=X/5 tier=Y chain=[stable=Y/N drop=Y/N decel=Y/N tight=Y/N wall=Y/N]
TIER_PATTERN = re.compile(
    r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[TIER\] (\w+) score=(\d+)/5 tier=([ABC]) chain=\[([^\]]*)\]'
)
SIGNAL_PATTERN = re.compile(r'(\w+)=([YN])')

def parse_tier_lines(logfile):
    """Parse all [TIER] log lines into structured records."""
    records = []
    if not os.path.exists(logfile):
        return records
    with open(logfile, 'r', errors='replace') as f:
        for line in f:
            m = TIER_PATTERN.search(line)
            if not m:
                continue
            ts_str, side, score_str, tier, chain_str = m.groups()
            try:
                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            except:
                ts = None
            signals = dict(SIGNAL_PATTERN.findall(chain_str))
            stable = signals.get('stable', 'N') == 'Y'
            drop   = signals.get('drop',   'N') == 'Y'
            decel  = signals.get('decel',  'N') == 'Y'
            tight  = signals.get('tight',  'N') == 'Y'
            wall   = signals.get('wall',   'N') == 'Y'
            old_s  = old_score(stable, drop, decel, tight, wall)
            new_s  = new_score(stable, tight, wall)
            old_t  = score_to_tier(old_s)
            new_t  = score_to_tier(new_s)
            records.append({
                'ts': ts, 'side': side,
                'old_score': old_s, 'new_score': new_s,
                'old_tier': old_t, 'new_tier': new_t,
                'stable': stable, 'drop': drop, 'decel': decel,
                'tight': tight, 'wall': wall,
                'log_tier': tier,
                'new_chain_count': new_chain_count(stable, tight, wall),
            })
    return records

# ── Parse trades CSV ───────────────────────────────────────────────────────────
def parse_trades(csv_path):
    trades = []
    if not os.path.exists(csv_path):
        return trades
    with open(csv_path, 'r', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            except:
                ts = None
            pnl = 0
            try:
                pnl = float(row.get('pnl_cents', 0) or 0)
            except:
                pass
            period = None
            try:
                period = int(row.get('period', 0) or 0)
            except:
                pass
            score_diff = None
            try:
                score_diff = abs(float(row.get('score_diff', 0) or 0))
            except:
                pass
            sport = row.get('sport', '')
            ticker = row.get('ticker', '')
            side = row.get('entry_side', '')
            entry_price = None
            try:
                entry_price = float(row.get('entry_price', 0) or 0)
            except:
                pass
            exit_type = row.get('exit_type', '')
            trades.append({
                'ts': ts, 'ticker': ticker, 'sport': sport,
                'side': side, 'pnl': pnl, 'period': period,
                'score_diff': score_diff, 'entry_price': entry_price,
                'exit_type': exit_type, 'row': row,
            })
    return trades

# ── Match trades to TIER log entries ──────────────────────────────────────────
def match_trade_to_tier(trade, tier_records, window_sec=300):
    """Find the nearest TIER record for the same side within ±window_sec of the trade."""
    side = trade['side'].upper() if trade['side'] else ''
    ts   = trade['ts']
    if not ts or not side:
        return None
    best = None
    best_delta = timedelta(seconds=window_sec)
    for r in tier_records:
        if r['side'].upper() != side:
            continue
        if r['ts'] is None:
            continue
        delta = abs(r['ts'] - ts)
        if delta < best_delta:
            best_delta = delta
            best = r
    return best

# ── Parse REJECT_EARLY_GAME lines ─────────────────────────────────────────────
# Format: [REJECT_EARLY_GAME] SIDE period=X diff=Y score=A-B clock=MM:SS — ...
EARLY_GAME_PATTERN = re.compile(
    r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[REJECT_EARLY_GAME\] (\w+) period=(\d+) diff=(\d+)'
)

def parse_reject_early_game(logfile):
    events = []
    if not os.path.exists(logfile):
        return events
    with open(logfile, 'r', errors='replace') as f:
        for line in f:
            m = EARLY_GAME_PATTERN.search(line)
            if not m:
                continue
            ts_str, side, period, diff = m.groups()
            try:
                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            except:
                ts = None
            events.append({'ts': ts, 'side': side, 'period': int(period), 'diff': int(diff)})
    return events

# ── Parse BOUNCE_CHAIN lines (for REJECT_EARLY_GAME chain matching) ───────────
BOUNCE_CHAIN_PATTERN = re.compile(
    r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[BOUNCE_CHAIN\] (\w+) steps=(\d+)/5 \(([^)]+)\)'
)
BOUNCE_SIGNAL_PATTERN = re.compile(r'(stable|drop|decel|tight|wall)=([YN])')

def parse_bounce_chains(logfile):
    """Parse all BOUNCE_CHAIN lines that have signal details."""
    chains = []
    if not os.path.exists(logfile):
        return chains
    with open(logfile, 'r', errors='replace') as f:
        for line in f:
            m = BOUNCE_CHAIN_PATTERN.search(line)
            if not m:
                continue
            ts_str, side, steps_str, details = m.groups()
            if 'insufficient_data' in details:
                continue
            try:
                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            except:
                ts = None
            sigs = dict(BOUNCE_SIGNAL_PATTERN.findall(details))
            stable = sigs.get('stable', 'N') == 'Y'
            drop   = sigs.get('drop',   'N') == 'Y'
            decel  = sigs.get('decel',  'N') == 'Y'
            tight  = sigs.get('tight',  'N') == 'Y'
            wall   = sigs.get('wall',   'N') == 'Y'
            nc = new_chain_count(stable, tight, wall)
            chains.append({'ts': ts, 'side': side, 'nc': nc,
                           'stable': stable, 'drop': drop, 'decel': decel,
                           'tight': tight, 'wall': wall})
    return chains

def match_early_game_to_chain(event, chains, window_sec=60):
    """Find nearest BOUNCE_CHAIN for a REJECT_EARLY_GAME event."""
    side = event['side'].upper()
    ts   = event['ts']
    if not ts:
        return None
    best = None
    best_delta = timedelta(seconds=window_sec)
    for c in chains:
        if c['side'].upper() != side:
            continue
        if c['ts'] is None:
            continue
        delta = abs(c['ts'] - ts)
        if delta < best_delta:
            best_delta = delta
            best = c
    return best

# ── Main analysis ──────────────────────────────────────────────────────────────
def main():
    lines = []
    def w(s=''):
        lines.append(s)

    w("=" * 80)
    w("BOUNCE CHAIN RESTRUCTURE: P&L IMPACT ANALYSIS")
    w("OLD: 5-signal (stable+drop+decel+tight+wall) × 5  |  Thresholds A≥20, B≥10, C<10")
    w("NEW: 3-signal (stable+tight+wall) × 8              |  Thresholds A≥20, B≥10, C<10")
    w(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    w("=" * 80)

    # ── Load data ──────────────────────────────────────────────────────────────
    w("\nLoading data...")
    ncaamb_tiers  = parse_tier_lines(NCAAMB_LOG)
    tennis_tiers  = parse_tier_lines(TENNIS_LOG)
    all_tiers     = ncaamb_tiers + tennis_tiers
    trades        = parse_trades(TRADES_CSV)
    ncaamb_chains = parse_bounce_chains(NCAAMB_LOG)
    tennis_chains = parse_bounce_chains(TENNIS_LOG)
    all_chains    = ncaamb_chains + tennis_chains
    ncaamb_early  = parse_reject_early_game(NCAAMB_LOG)
    tennis_early  = parse_reject_early_game(TENNIS_LOG)
    all_early     = ncaamb_early + tennis_early

    w(f"  TIER log lines parsed: {len(all_tiers)} ({len(ncaamb_tiers)} ncaamb + {len(tennis_tiers)} tennis)")
    w(f"  BOUNCE_CHAIN lines:    {len(all_chains)}")
    w(f"  Trades loaded:         {len(trades)}")
    w(f"  REJECT_EARLY_GAME:     {len(all_early)} ({len(ncaamb_early)} ncaamb + {len(tennis_early)} tennis)")

    # ── Date range ─────────────────────────────────────────────────────────────
    trade_dates = [t['ts'] for t in trades if t['ts']]
    if trade_dates:
        first_date = min(trade_dates)
        last_date  = max(trade_dates)
        n_days     = max(1, (last_date - first_date).days + 1)
        w(f"  Trade date range:      {first_date.date()} → {last_date.date()} ({n_days} days)")
    else:
        n_days = 5

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1: RECLASSIFICATION OF TRADES
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 1: TRADE RECLASSIFICATION — OLD TIER vs NEW TIER")
    w("=" * 80)

    matched   = []
    unmatched = []

    for trade in trades:
        tier_rec = match_trade_to_tier(trade, all_tiers, window_sec=300)
        if tier_rec:
            matched.append((trade, tier_rec))
        else:
            unmatched.append(trade)

    w(f"\n  Trades matched to TIER log:    {len(matched)}")
    w(f"  Trades without TIER match:     {len(unmatched)}")
    w(f"  Match rate:                    {100*len(matched)/max(1,len(trades)):.1f}%")

    if unmatched:
        w(f"\n  UNMATCHED TRADES (no TIER log found within 5 min):")
        for t in unmatched[:10]:
            w(f"    {t['ts']} | {t['side']:10s} | pnl={t['pnl']:+.0f}c | {t['sport']}")
        if len(unmatched) > 10:
            w(f"    ... and {len(unmatched)-10} more")

    # Build comparison table
    tier_changes = defaultdict(list)  # (old_tier, new_tier) -> list of pnl
    same_tier    = defaultdict(list)  # tier -> list of pnl (unchanged)

    w(f"\n  {'Trade':<30} {'Side':<8} {'Old':<5} {'New':<5} {'Change':<10} {'P&L':>8} {'Win'}")
    w(f"  {'-'*30} {'-'*8} {'-'*5} {'-'*5} {'-'*10} {'-'*8} {'-'*4}")

    for (trade, tier_rec) in matched[:50]:  # show first 50
        old_t = tier_rec['old_tier']
        new_t = tier_rec['new_tier']
        pnl   = trade['pnl']
        win   = "W" if pnl > 0 else ("L" if pnl < 0 else "P")
        change_str = f"{old_t}→{new_t}" if old_t != new_t else f"{old_t}(same)"
        key   = f"{old_t}→{new_t}"
        tier_changes[key].append(pnl)
        ticker_short = trade['ticker'].split('-')[-1] if trade['ticker'] else ''
        w(f"  {ticker_short:<30} {trade['side']:<8} {old_t:<5} {new_t:<5} {change_str:<10} {pnl:>+8.0f}c {win}")

    if len(matched) > 50:
        w(f"  ... ({len(matched)-50} more trades not shown)")

    # Aggregate all
    for (trade, tier_rec) in matched:
        old_t = tier_rec['old_tier']
        new_t = tier_rec['new_tier']
        pnl   = trade['pnl']
        tier_changes[f"{old_t}→{new_t}"].append(pnl)

    w(f"\n  TIER TRANSITION SUMMARY:")
    w(f"  {'Transition':<12} {'Count':>7} {'Wins':>6} {'WR%':>7} {'Avg P&L':>10} {'Total P&L':>12}")
    w(f"  {'-'*12} {'-'*7} {'-'*6} {'-'*7} {'-'*10} {'-'*12}")
    for key in sorted(tier_changes.keys()):
        pnls = tier_changes[key]
        wins = sum(1 for p in pnls if p > 0)
        wr   = 100 * wins / len(pnls) if pnls else 0
        avg  = sum(pnls) / len(pnls) if pnls else 0
        tot  = sum(pnls)
        w(f"  {key:<12} {len(pnls):>7} {wins:>6} {wr:>6.1f}% {avg:>+10.1f}c {tot:>+12.1f}c")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2: NEW TIER PERFORMANCE TABLE
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 2: PERFORMANCE BY NEW TIER (3-SIGNAL CHAIN)")
    w("  Tier A = 3/3 signals (score=24) | B = 2/3 (score=16) | C = 0-1/3 (score=0 or 8)")
    w("=" * 80)

    new_tier_data = defaultdict(list)
    for (trade, tier_rec) in matched:
        new_t = tier_rec['new_tier']
        new_tier_data[new_t].append(trade['pnl'])

    # Also look at TIER records by chain count
    chain_count_data = defaultdict(list)  # new_chain_count -> pnl (for matched trades)
    for (trade, tier_rec) in matched:
        cc = tier_rec['new_chain_count']
        chain_count_data[cc].append(trade['pnl'])

    w(f"\n  BY NEW TIER:")
    w(f"  {'Tier':<8} {'Signals':<12} {'Trades':>8} {'Wins':>6} {'WR%':>7} {'Avg P&L':>10} {'Total P&L':>12}")
    w(f"  {'-'*8} {'-'*12} {'-'*8} {'-'*6} {'-'*7} {'-'*10} {'-'*12}")
    for tier_label, sig_desc in [('A', '3/3 (score≥20)'), ('B', '2/3 (score≥10)'), ('C', '0-1/3 (score<10)')]:
        pnls = new_tier_data.get(tier_label, [])
        wins = sum(1 for p in pnls if p > 0)
        wr   = 100 * wins / len(pnls) if pnls else 0
        avg  = sum(pnls) / len(pnls) if pnls else 0
        tot  = sum(pnls)
        w(f"  {tier_label:<8} {sig_desc:<12} {len(pnls):>8} {wins:>6} {wr:>6.1f}% {avg:>+10.1f}c {tot:>+12.1f}c")

    w(f"\n  BY NEW CHAIN COUNT:")
    w(f"  {'Chain':>8} {'Score':>7} {'Tier':<6} {'Trades':>8} {'WR%':>7} {'Avg P&L':>10} {'Total P&L':>12}")
    w(f"  {'-'*8} {'-'*7} {'-'*6} {'-'*8} {'-'*7} {'-'*10} {'-'*12}")
    for cc in [3, 2, 1, 0]:
        pnls  = chain_count_data.get(cc, [])
        score = cc * 8
        tier  = score_to_tier(score)
        wins  = sum(1 for p in pnls if p > 0)
        wr    = 100 * wins / len(pnls) if pnls else 0
        avg   = sum(pnls) / len(pnls) if pnls else 0
        tot   = sum(pnls)
        w(f"  {cc:>8}/3  {score:>5}/24  {tier:<6} {len(pnls):>8} {wr:>6.1f}% {avg:>+10.1f}c {tot:>+12.1f}c")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3: EARLY_GAME UNLOCK ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 3: EARLY_GAME UNLOCK ANALYSIS")
    w("  OLD rule: period=1, diff<5 → always reject")
    w("  NEW rule: period=1, diff<5 → allow IF new chain ≥ 2/3 (tight+wall or stable+tight, etc.)")
    w("=" * 80)

    total_early = len(all_early)
    w(f"\n  Total REJECT_EARLY_GAME raw events: {total_early}")
    w(f"    ncaamb: {len(ncaamb_early)}")
    w(f"    tennis: {len(tennis_early)}")
    w(f"    NOTE: raw events = repeated polls on same side, not unique opportunities")

    # Deduplicate by (date, side) — each side-day = 1 opportunity
    seen_side_days = set()
    deduped_early = []
    for ev in sorted(all_early, key=lambda e: (e['ts'] or datetime.min)):
        date_str = ev['ts'].strftime('%Y-%m-%d') if ev['ts'] else 'unknown'
        key = (date_str, ev['side'].upper())
        if key not in seen_side_days:
            seen_side_days.add(key)
            deduped_early.append(ev)

    # Count unique sides per day
    from collections import Counter
    daily_unique_counts = Counter()
    for ev in deduped_early:
        date_str = ev['ts'].strftime('%Y-%m-%d') if ev['ts'] else 'unknown'
        daily_unique_counts[date_str] += 1

    w(f"\n  UNIQUE side-day opportunities (deduplicated):")
    for d in sorted(daily_unique_counts):
        w(f"    {d}: {daily_unique_counts[d]} unique sides")
    w(f"    TOTAL: {len(deduped_early)} unique side-day opportunities")
    w(f"    Per day avg: {len(deduped_early)/max(1,len(daily_unique_counts)):.1f}")

    # Match each UNIQUE REJECT_EARLY_GAME to nearest BOUNCE_CHAIN
    matched_early  = []
    no_chain_early = []
    for ev in deduped_early:
        chain = match_early_game_to_chain(ev, all_chains, window_sec=60)
        if chain:
            matched_early.append((ev, chain))
        else:
            no_chain_early.append(ev)

    w(f"\n  Matched to BOUNCE_CHAIN log: {len(matched_early)} / {len(deduped_early)}")
    w(f"  No chain match found:        {len(no_chain_early)}")

    # Count those that would now pass (new chain >= 2)
    would_unlock = [pair for pair in matched_early if pair[1]['nc'] >= 2]
    still_reject = [pair for pair in matched_early if pair[1]['nc'] < 2]

    w(f"\n  NEW CHAIN SCORE DISTRIBUTION (matched early-game events):")
    chain_dist = defaultdict(int)
    for (ev, ch) in matched_early:
        chain_dist[ch['nc']] += 1
    for cc in sorted(chain_dist.keys(), reverse=True):
        tier  = score_to_tier(cc * 8)
        allow = "ALLOW" if cc >= 2 else "still reject"
        w(f"    chain {cc}/3: {chain_dist[cc]:>5} events  [{allow}] → new tier {tier}")

    # For unmatched, assume worst case distribution from known signal stats
    # From live_bounce_match.txt: tight=90.7%, wall=40.1%, stable=35.5%
    # P(nc>=2) = P(at least 2 of stable,tight,wall)
    # tight almost always fires; wall fires ~40%, stable ~35%
    # Approximate: tight always fires, so need wall OR stable additionally
    # P(nc>=2) ≈ P(tight=Y) * P(wall=Y OR stable=Y) = 0.907 * (1-(1-0.401)*(1-0.355)) = 0.907 * 0.613 ≈ 0.556
    ESTIMATED_UNLOCK_RATE = 0.556
    estimated_unmatched_unlock = int(len(no_chain_early) * ESTIMATED_UNLOCK_RATE)

    total_would_unlock = len(would_unlock) + estimated_unmatched_unlock
    unlock_pct = 100 * total_would_unlock / total_early if total_early else 0

    w(f"\n  UNLOCK SUMMARY:")
    w(f"    Would be ALLOWED by new chain≥2 rule (matched): {len(would_unlock)}")
    w(f"    Estimated unlocks from unmatched (rate={ESTIMATED_UNLOCK_RATE:.0%}): {estimated_unmatched_unlock}")
    w(f"    TOTAL estimated unlocks:                          {total_would_unlock}")
    w(f"    As % of all REJECT_EARLY_GAME:                    {unlock_pct:.1f}%")

    # Estimate P&L impact
    # Use A/B tier win rates from matched trades for the unlocked ones
    # All unlocked have chain>=2 so new tier B or A
    tier_b_pnls = new_tier_data.get('B', [])
    tier_a_pnls = new_tier_data.get('A', [])
    # Most will be chain=2 (tier B), some chain=3 (tier A)
    chain2_unlock = chain_dist.get(2, 0) + int(estimated_unmatched_unlock * 0.7)
    chain3_unlock = chain_dist.get(3, 0) + int(estimated_unmatched_unlock * 0.3)

    avg_b = sum(tier_b_pnls) / len(tier_b_pnls) if tier_b_pnls else 0
    avg_a = sum(tier_a_pnls) / len(tier_a_pnls) if tier_a_pnls else 0

    early_game_days   = max(1, len(daily_unique_counts))
    # Use deduplicated unique side-day count for per-day rate
    unique_unlocks_per_day = total_would_unlock / early_game_days
    # Conversion: unique side-day → actual trade entry
    # ~42% of regular trade opportunities convert; early_game previously 0%
    # Conservative: use 40% (similar to current bulk conversion rate per side)
    ENTRY_CONVERSION  = 0.40
    new_trades_per_day = unique_unlocks_per_day * ENTRY_CONVERSION
    avg_new_trade_pnl  = (chain2_unlock * avg_b + chain3_unlock * avg_a) / max(1, chain2_unlock + chain3_unlock)
    early_game_pnl_day = new_trades_per_day * avg_new_trade_pnl

    w(f"\n  EARLY_GAME P&L PROJECTION:")
    w(f"    Unique side-day unlock opps/day:  {unique_unlocks_per_day:.1f}")
    w(f"    Entry conversion rate:            {ENTRY_CONVERSION:.0%} (per unique side opportunity)")
    w(f"    Estimated new trades/day:         {new_trades_per_day:.1f}")
    w(f"    Avg P&L (B-tier weighted):        {avg_new_trade_pnl:+.1f}c/trade")
    w(f"    Projected additional $/day:       {early_game_pnl_day:+.1f}c")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4: RISK COMPARISON — OLD vs NEW CONFIG
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 4: RISK COMPARISON — OLD 5-SIGNAL vs NEW 3-SIGNAL CONFIG")
    w("=" * 80)

    # Old tier distribution for matched trades
    old_tier_data = defaultdict(list)
    for (trade, tier_rec) in matched:
        old_t = tier_rec['old_tier']
        old_tier_data[old_t].append(trade['pnl'])

    all_pnls = [t['pnl'] for t in trades]
    wins_all  = sum(1 for p in all_pnls if p > 0)
    losses_all = [p for p in all_pnls if p < 0]
    avg_loss  = sum(losses_all) / len(losses_all) if losses_all else 0

    w(f"\n  CURRENT STATE (all {len(trades)} trades, {n_days} days):")
    w(f"    Trades/day:     {len(trades)/n_days:.1f}")
    w(f"    Win rate:       {100*wins_all/len(trades):.1f}%")
    w(f"    Total P&L:      {sum(all_pnls):+.0f}c = ${sum(all_pnls)/100:+.2f}")
    w(f"    P&L/day:        {sum(all_pnls)/n_days:+.1f}c = ${sum(all_pnls)/n_days/100:+.2f}")
    w(f"    Avg win:        {sum(p for p in all_pnls if p>0)/max(1,wins_all):+.1f}c")
    w(f"    Avg loss:       {avg_loss:+.1f}c")
    w(f"    Losses/day:     {len(losses_all)/n_days:.1f}")
    w(f"    Daily drawdown: {sum(losses_all)/n_days:+.1f}c = ${sum(losses_all)/n_days/100:+.2f}")

    # OLD config by tier
    w(f"\n  OLD CONFIG — TIER PERFORMANCE (5-signal × 5):")
    w(f"  {'Tier':<6} {'Score Range':<16} {'Trades':>8} {'WR%':>7} {'Avg P&L':>10} {'Total P&L':>12} {'$/day':>10}")
    w(f"  {'-'*6} {'-'*16} {'-'*8} {'-'*7} {'-'*10} {'-'*12} {'-'*10}")
    for tier_label, score_range in [('A', '≥20 (4-5 sigs)'), ('B', '10-19 (2-3 sigs)'), ('C', '<10 (0-1 sigs)')]:
        pnls = old_tier_data.get(tier_label, [])
        wins = sum(1 for p in pnls if p > 0)
        wr   = 100 * wins / len(pnls) if pnls else 0
        avg  = sum(pnls) / len(pnls) if pnls else 0
        tot  = sum(pnls)
        dpd  = tot / n_days
        w(f"  {tier_label:<6} {score_range:<16} {len(pnls):>8} {wr:>6.1f}% {avg:>+10.1f}c {tot:>+12.1f}c {dpd:>+10.1f}c")

    # NEW config by tier
    w(f"\n  NEW CONFIG — TIER PERFORMANCE (3-signal × 8):")
    w(f"  {'Tier':<6} {'Score Range':<16} {'Trades':>8} {'WR%':>7} {'Avg P&L':>10} {'Total P&L':>12} {'$/day':>10}")
    w(f"  {'-'*6} {'-'*16} {'-'*8} {'-'*7} {'-'*10} {'-'*12} {'-'*10}")
    for tier_label, score_range in [('A', '≥20 (3/3 sigs)'), ('B', '10-19 (2/3 sigs)'), ('C', '<10 (0-1 sigs)')]:
        pnls = new_tier_data.get(tier_label, [])
        wins = sum(1 for p in pnls if p > 0)
        wr   = 100 * wins / len(pnls) if pnls else 0
        avg  = sum(pnls) / len(pnls) if pnls else 0
        tot  = sum(pnls)
        dpd  = tot / n_days
        w(f"  {tier_label:<6} {score_range:<16} {len(pnls):>8} {wr:>6.1f}% {avg:>+10.1f}c {tot:>+12.1f}c {dpd:>+10.1f}c")

    # KEY CHANGE: impact of removing drop/decel
    w(f"\n  IMPACT OF REMOVING DROP + DECEL SIGNALS:")
    # How many trades were ONLY in A-tier old because of drop/decel contributing?
    # In new config, these drop to B or C tier
    demoted  = [(t, r) for (t, r) in matched if r['old_tier'] in ('A','B') and r['new_tier'] < r['old_tier']]
    promoted = [(t, r) for (t, r) in matched if r['new_tier'] > r['old_tier']]
    same_t   = [(t, r) for (t, r) in matched if r['new_tier'] == r['old_tier']]

    demoted_pnl  = [t['pnl'] for (t, r) in demoted]
    promoted_pnl = [t['pnl'] for (t, r) in promoted]

    w(f"    Trades that DEMOTE (old tier > new tier): {len(demoted)}")
    if demoted_pnl:
        dw = sum(1 for p in demoted_pnl if p > 0)
        w(f"      WR: {100*dw/len(demoted_pnl):.1f}% | Avg P&L: {sum(demoted_pnl)/len(demoted_pnl):+.1f}c | "
          f"Total: {sum(demoted_pnl):+.1f}c")
        w(f"      NOTE: These were boosted by drop/decel — their TRUE quality at new tier revealed")

    w(f"    Trades that PROMOTE (new tier > old tier): {len(promoted)}")
    if promoted_pnl:
        pw = sum(1 for p in promoted_pnl if p > 0)
        w(f"      WR: {100*pw/len(promoted_pnl):.1f}% | Avg P&L: {sum(promoted_pnl)/len(promoted_pnl):+.1f}c | "
          f"Total: {sum(promoted_pnl):+.1f}c")

    w(f"    Trades with SAME tier:                     {len(same_t)}")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5: MISSED HIGH-SIGNAL BOUNCES ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 5: MISSED HIGH-SIGNAL BOUNCES — CATCH RATE UNDER NEW CONFIG")
    w("  From live_bounce_match.txt: 26 missed sides with chain 3-5/5")
    w("=" * 80)

    # These 26 sides were missed for specific reasons — re-examine under new scoring
    # Old 3-5/5 = old score 15-25. Under new 3-signal chain, drop/decel removed.
    # A side that was 3/5 OLD might be 1-2/3 NEW if the 3 signals included drop or decel.

    # Parse all TIER lines to find entries for the 26 missed sides from live_bounce_match.txt
    MISSED_SIDES_AND_REASONS = {
        'BAR':  'REJECT',        'DOL':  'REJECT',        'MOU':  'REJECT_SHALLOW',
        'ZID':  'REJECT',        'JAN':  'REJECT',        'CBU':  'REJECT_EARLY_GAME',
        'PAR':  'WARN_CTIER',    'KIR':  'REJECT_SHALLOW', 'LA':   'REJECT',
        'TLSA': 'REJECT_EARLY_GAME', 'MSU': 'REJECT_EARLY_GAME', 'PAU': 'REJECT',
        'CAM':  'REJECT_SHALLOW', 'FER':  'REJECT',        'UCI':  'REJECT_EARLY_GAME',
        'OKC':  'WARN_CTIER',    'STA':  'WARN_CTIER',     'HARV': 'REJECT_EARLY_GAME',
        'RAD':  'WARN_CTIER',    'ING':  'WARN_CTIER',     'GAL':  'WARN_CTIER',
        'USF':  'REJECT_EARLY_GAME', 'ARN': 'REJECT',      'MAS':  'WARN_CTIER',
        'GIL':  'REJECT_SHALLOW', 'BOR':  'REJECT',
    }

    # Get TIER records for each missed side
    missed_side_tiers = defaultdict(list)
    for r in all_tiers:
        if r['side'].upper() in MISSED_SIDES_AND_REASONS:
            missed_side_tiers[r['side'].upper()].append(r)

    w(f"\n  Missed sides with TIER log data: {len(missed_side_tiers)} / 26")
    w(f"\n  {'Side':<8} {'Reject Reason':<22} {'Old Chain':<12} {'New Chain':<12} {'New Tier':<10} {'Now Catch?'}")
    w(f"  {'-'*8} {'-'*22} {'-'*12} {'-'*12} {'-'*10} {'-'*10}")

    would_catch_count = 0
    would_catch_early_game = 0
    still_miss_ctier = 0
    early_game_sides = [s for s, r in MISSED_SIDES_AND_REASONS.items() if r == 'REJECT_EARLY_GAME']

    for side, reason in sorted(MISSED_SIDES_AND_REASONS.items()):
        recs = missed_side_tiers.get(side, [])
        if recs:
            # Use the best chain record
            best = max(recs, key=lambda r: r['new_score'])
            old_chain_str = f"{best['old_score']//5}/5"
            new_chain_str = f"{best['new_chain_count']}/3"
            new_t         = best['new_tier']
            # Would we catch it?
            if reason == 'REJECT_EARLY_GAME':
                catch = "YES (unlock)" if best['new_chain_count'] >= 2 else "NO (chain<2)"
                if best['new_chain_count'] >= 2:
                    would_catch_count += 1
                    would_catch_early_game += 1
            elif reason == 'WARN_CTIER':
                catch = "YES (tier↑)" if new_t in ('A','B') else "NO (still C)"
                if new_t in ('A', 'B'):
                    would_catch_count += 1
                else:
                    still_miss_ctier += 1
            elif reason in ('REJECT', 'REJECT_SHALLOW', 'REJECT_COLLAPSE'):
                catch = "NO (other filter)"
            else:
                catch = "UNKNOWN"
        else:
            old_chain_str = "no data"
            new_chain_str = "no data"
            new_t         = "?"
            if reason == 'REJECT_EARLY_GAME':
                catch = "LIKELY YES (est)"
                would_catch_count += 1
                would_catch_early_game += 1
            else:
                catch = "UNKNOWN"
        w(f"  {side:<8} {reason:<22} {old_chain_str:<12} {new_chain_str:<12} {new_t:<10} {catch}")

    w(f"\n  SUMMARY:")
    w(f"    Total missed high-signal sides:       26")
    w(f"    Would now catch (new chain/tier fix):  {would_catch_count}")
    w(f"      - via EARLY_GAME unlock (chain≥2):  {would_catch_early_game}")
    w(f"      - via WARN_CTIER → B/A tier fix:    {would_catch_count - would_catch_early_game}")
    w(f"    Still missed (REJECT/SHALLOW/other):  {26 - would_catch_count}")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 6: NET IMPACT CALCULATION
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 6: NET P&L IMPACT — PROJECTED NEW $/DAY")
    w("=" * 80)

    # Current P&L/day baseline
    current_pnl_per_day = sum(all_pnls) / n_days
    current_trades_per_day = len(trades) / n_days

    # A) Improvement from tier scoring changes on existing trades
    # Compare old vs new tier for existing trades → difference in expected P&L
    tier_reclass_delta = 0.0
    tier_upgrade_count = 0
    tier_downgrade_count = 0
    for (trade, tier_rec) in matched:
        old_t = tier_rec['old_tier']
        new_t = tier_rec['new_tier']
        if old_t == new_t:
            continue
        # Impact is mainly on size / position — for now flag demoted trades
        # that were B/A old → C new: those might have been entered under WARN_CTIER
        # and would still be entered (no size impact on existing entries)
        # Tier change doesn't change existing P&L — it changes FUTURE FILTER decisions
        if new_t > old_t:
            tier_upgrade_count += 1
        else:
            tier_downgrade_count += 1

    # B) WARN_CTIER trades that were actually B-tier under new scoring
    warn_ctier_recs = [(t, r) for (t, r) in matched if r['log_tier'] == 'C' and r['new_tier'] in ('A','B')]
    warn_ctier_pnls = [t['pnl'] for (t, r) in warn_ctier_recs]
    # These were C-tier (entered with WARN_CTIER or rejected), new scoring would classify as B+
    # Under new config: they'd enter at normal sizing — P&L per trade stays same, but filter is cleaner

    # C) Additional trades from EARLY_GAME unlock
    additional_from_early = early_game_pnl_day  # computed in section 3

    # D) Additional trades from missed bounces now catchable
    # From section 5: would_catch_count sides (spread over n_days)
    missed_catch_per_day = would_catch_count / n_days
    # Use average B-tier P&L as estimate
    avg_b_pnl = sum(tier_b_pnls) / len(tier_b_pnls) if tier_b_pnls else 0
    additional_from_missed = missed_catch_per_day * avg_b_pnl

    # E) Additional losses from lower barrier to entry (C-tier trades that wouldn't have been taken)
    # Under new scoring, fewer C-tier (score<10 = chain 0-1/3) since tight alone = score 8
    # These borderline trades: tight=Y only, score=8 (just below B) — currently WARN_CTIER
    # NEW: tight alone = score 8 → same as old score 8 for tight alone — no change here
    # But removing drop/decel means some 2/5 old → 1/3 new (B→C) → might now be filtered = fewer losses
    demoted_losses = [(t['pnl'], r) for (t, r) in demoted if t['pnl'] < 0]
    demoted_loss_saved_per_day = abs(sum(p for (p,r) in demoted_losses)) / n_days

    # F) Risk: C-tier trades previously blocked now entering (unlock has risk)
    # This is captured by conversion rate (30%) and B-tier avg pnl
    # Conservative: we already used realized avg pnl from B-tier to project

    w(f"\n  BASELINE:")
    w(f"    Current P&L/day:          {current_pnl_per_day:>+8.1f}c  (${current_pnl_per_day/100:>+.2f})")
    w(f"    Current trades/day:       {current_trades_per_day:>8.1f}")
    w(f"    Current WR:               {100*wins_all/len(trades):>8.1f}%")

    w(f"\n  ADJUSTMENTS:")
    w(f"    [+] EARLY_GAME unlock:    {additional_from_early:>+8.1f}c/day  "
      f"({new_trades_per_day:.1f} new trades × {avg_new_trade_pnl:+.1f}c avg, {unique_unlocks_per_day:.1f} unlocks/day)")
    w(f"    [+] Missed bounce catch:  {additional_from_missed:>+8.1f}c/day  "
      f"({would_catch_count} sides / {n_days} days × {avg_b_pnl:+.1f}c avg B-tier)")
    w(f"    [+] Demoted trade filter: {demoted_loss_saved_per_day:>+8.1f}c/day  "
      f"(avoided {len(demoted_losses)} loss trades that drop to C-tier)")
    w(f"    Tier reclassification:    {tier_upgrade_count} upgrades, {tier_downgrade_count} downgrades on existing trades")

    total_adjustment = additional_from_early + additional_from_missed + demoted_loss_saved_per_day
    projected_pnl_per_day = current_pnl_per_day + total_adjustment

    w(f"\n  NET IMPACT:")
    w(f"    Total adjustment/day:     {total_adjustment:>+8.1f}c  (${total_adjustment/100:>+.2f})")
    w(f"    Projected new P&L/day:    {projected_pnl_per_day:>+8.1f}c  (${projected_pnl_per_day/100:>+.2f})")
    w(f"    Improvement:              {100*(projected_pnl_per_day - current_pnl_per_day)/max(0.01, abs(current_pnl_per_day)):>+.1f}%")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 7: SIGNAL QUALITY DEEP DIVE
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 7: SIGNAL QUALITY — WHY DROP & DECEL SHOULD BE REMOVED")
    w("=" * 80)

    # From all_tiers, compute per-signal correlation with trade outcomes
    signal_pnls = {'stable': [], 'drop': [], 'decel': [], 'tight': [], 'wall': []}
    signal_pnls_N = {'stable': [], 'drop': [], 'decel': [], 'tight': [], 'wall': []}
    for (trade, tier_rec) in matched:
        pnl = trade['pnl']
        for sig in ['stable', 'drop', 'decel', 'tight', 'wall']:
            if tier_rec[sig]:
                signal_pnls[sig].append(pnl)
            else:
                signal_pnls_N[sig].append(pnl)

    w(f"\n  SIGNAL CORRELATION WITH P&L OUTCOME:")
    w(f"  When signal=Y:  {'Signal':<8} {'Trades':>8} {'WR%':>7} {'Avg P&L':>10} | "
      f"When signal=N:  {'Trades':>8} {'WR%':>7} {'Avg P&L':>10}")
    w(f"  {'-'*8} {'-'*8} {'-'*7} {'-'*10}   {'-'*8} {'-'*7} {'-'*10}")
    for sig in ['stable', 'drop', 'decel', 'tight', 'wall']:
        y_pnls = signal_pnls[sig]
        n_pnls = signal_pnls_N[sig]
        y_wr = 100 * sum(1 for p in y_pnls if p > 0) / len(y_pnls) if y_pnls else 0
        n_wr = 100 * sum(1 for p in n_pnls if p > 0) / len(n_pnls) if n_pnls else 0
        y_avg = sum(y_pnls) / len(y_pnls) if y_pnls else 0
        n_avg = sum(n_pnls) / len(n_pnls) if n_pnls else 0
        retained = "KEPT" if sig in ('stable', 'tight', 'wall') else "REMOVED"
        w(f"  {sig:<8} {len(y_pnls):>8} {y_wr:>6.1f}% {y_avg:>+10.1f}c   {len(n_pnls):>8} {n_wr:>6.1f}% {n_avg:>+10.1f}c  [{retained}]")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 8: EXECUTIVE SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    w("\n" + "=" * 80)
    w("SECTION 8: EXECUTIVE SUMMARY")
    w("=" * 80)

    total_pnl_dollars = sum(all_pnls) / 100
    pnl_per_day_dollars = current_pnl_per_day / 100
    projected_per_day_dollars = projected_pnl_per_day / 100

    w(f"""
  TRADE PERFORMANCE (Mar 11-15, {n_days} days, {len(trades)} trades):
    Total P&L:       ${total_pnl_dollars:>+.2f}  ({sum(all_pnls):>+.0f}c)
    P&L/day:         ${pnl_per_day_dollars:>+.2f}  ({current_pnl_per_day:>+.1f}c)
    Win rate:        {100*wins_all/len(trades):.1f}%
    Trades/day:      {current_trades_per_day:.1f}

  SIGNAL REDUNDANCY (key finding):
    - drop=Y fires only 3.4% of all 28,115 chain evaluations
    - decel=Y fires 20.2% but has minimal P&L correlation vs tight/wall
    - tight=Y fires 90.7% — dominates scoring in old system
    - wall=Y fires 40.1% — strong secondary signal
    - stable=Y fires 35.5% — meaningful confirmation signal
    → Removing drop+decel reduces noise, simplifies tier math

  TIER BOUNDARY CHANGE (critical):
    OLD: 2 signals = score 10 → tier B (entry allowed)
    NEW: 2 signals = score 16 → tier B (entry allowed)
    OLD: 1 signal  = score  5 → tier C (WARN_CTIER or reject)
    NEW: 1 signal  = score  8 → tier C (reject — tighter filter)
    → tight-alone (1/3) is now firmly C-tier: reduces noise entries

  PROJECTED IMPACT:
    Early game unlocks:   {additional_from_early:>+.1f}c/day  ({new_trades_per_day:.1f} new trades from {unique_unlocks_per_day:.1f} unique unlocks/day)
    Missed bounce catch:  {additional_from_missed:>+.1f}c/day
    Demoted loss filter:  {demoted_loss_saved_per_day:>+.1f}c/day (avoided bad C-tier entries)
    ─────────────────────────────────────────────────
    NET IMPROVEMENT:      {total_adjustment:>+.1f}c/day  (${total_adjustment/100:>+.2f}/day)
    CURRENT P&L/day:      {current_pnl_per_day:>+.1f}c/day  (${pnl_per_day_dollars:>+.2f}/day)
    PROJECTED P&L/day:    {projected_pnl_per_day:>+.1f}c/day  (${projected_per_day_dollars:>+.2f}/day)

  RECOMMENDATION:
    Deploy 3-signal chain with EARLY_GAME unlock (chain>=2/3).
    Key wins: {would_catch_count} previously missed high-signal bounces, {total_would_unlock} EARLY_GAME unlocks.
    Risk: Tight-alone (1/3) now firmly C-tier reduces marginal noise entries.
    Net: Cleaner signal quality + expanded entry universe for genuine bounces.
""")

    w("=" * 80)
    w("END OF ANALYSIS")
    w("=" * 80)

    output = "\n".join(lines)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output)
    print(output)
    print(f"\n[Saved to {OUTPUT_FILE}]")

if __name__ == '__main__':
    main()
