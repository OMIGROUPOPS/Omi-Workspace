"""
Intra-Kalshi Contradiction Scanner — Phase 2
Loads market_surface.json from Phase 1 discovery and scans ALL markets
for pricing contradictions across 5 scan types.

Usage:
    cd arb-executor
    python -m intra_kalshi.scanner [--input market_surface.json] [--output contradictions.json]
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Severity thresholds (cents)
# ---------------------------------------------------------------------------
HIGH_THRESHOLD = 5
MEDIUM_THRESHOLD = 3

def severity(profit_cents):
    if profit_cents >= HIGH_THRESHOLD:
        return 'HIGH'
    if profit_cents >= MEDIUM_THRESHOLD:
        return 'MEDIUM'
    return 'LOW'

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_surface(path):
    if not os.path.exists(path):
        sys.exit(f'[FATAL] {path} not found. Run discovery first.')
    with open(path) as f:
        data = json.load(f)
    events = data.get('events', [])
    markets = data.get('markets', {})
    print(f'Loaded {len(events)} events, {len(markets)} markets from {path}')
    print(f'Generated: {data.get("generated_at", "unknown")}')
    return events, markets

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_team(ticker):
    """KXNBASPREAD-26MAR01DETORL-DET7 → 'DET'"""
    suffix = ticker.rsplit('-', 1)[-1]
    return re.sub(r'\d+$', '', suffix)


def extract_game_id(event_ticker):
    """KXNBAGAME-26FEB28NOPUTA → '26FEB28NOPUTA'"""
    parts = event_ticker.split('-')
    return parts[1] if len(parts) >= 2 else None


def extract_series_prefix(event_ticker):
    """KXNBAGAME-26FEB28NOPUTA → 'KXNBAGAME'"""
    return event_ticker.split('-')[0]


def extract_crypto_base(event_ticker):
    """KXBTCD-26MAR0617 → 'KXBTCD'"""
    return event_ticker.split('-')[0]


def parse_close_time(ct):
    """Parse ISO close_time string to datetime for ordering."""
    if not ct:
        return None
    try:
        return datetime.fromisoformat(ct.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None

# ---------------------------------------------------------------------------
# Scan 1: Binary Complement
# ---------------------------------------------------------------------------

def scan_binary_complement(markets):
    """Markets where yes_ask + no_ask < 98c — buy both = guaranteed profit."""
    results = []
    for ticker, m in markets.items():
        ya = m.get('yes_ask')
        na = m.get('no_ask')
        if ya is None or na is None:
            continue
        total = ya + na
        if total < 98:
            profit = 100 - total
            results.append({
                'scan': 'binary_complement',
                'severity': severity(profit),
                'profit_cents': profit,
                'description': f'Buy YES@{ya}c + NO@{na}c = {total}c → {profit}c guaranteed profit',
                'markets': [{'ticker': ticker, 'yes_ask': ya, 'no_ask': na, 'title': m.get('title', '')}],
                'event_ticker': m.get('event_ticker', ''),
                'category': m.get('category', ''),
                'volume_24h': m.get('volume_24h', 0),
            })
    results.sort(key=lambda x: -x['profit_cents'])
    return results

# ---------------------------------------------------------------------------
# Scan 2: Multi-Outcome Sum
# ---------------------------------------------------------------------------

def scan_multi_outcome(events, markets):
    """Mutually exclusive events where sum of yes_asks deviates from 100c."""
    results = []
    for ev in events:
        if not ev.get('mutually_exclusive'):
            continue
        tickers = ev.get('market_tickers', [])
        if len(tickers) < 2:
            continue

        asks = []
        bids = []
        for t in tickers:
            m = markets.get(t)
            if not m:
                continue
            ya = m.get('yes_ask')
            yb = m.get('yes_bid')
            if ya is not None:
                asks.append((t, ya, m.get('title', '')))
            if yb is not None:
                bids.append((t, yb))

        if len(asks) < 2:
            continue

        ask_sum = sum(a[1] for a in asks)
        bid_sum = sum(b[1] for b in bids) if bids else None
        total_vol = sum(markets[t].get('volume_24h', 0) for t in tickers if t in markets)

        if ask_sum < 97:
            # Underpriced: buy all YES outcomes
            profit = 100 - ask_sum
            results.append({
                'scan': 'multi_outcome',
                'severity': severity(profit),
                'profit_cents': profit,
                'description': f'BUY ALL: {len(asks)} outcomes sum_yes_ask={ask_sum}c → {profit}c profit (buy all YES)',
                'markets': [{'ticker': t, 'yes_ask': ya, 'title': title} for t, ya, title in asks],
                'event_ticker': ev.get('event_ticker', ''),
                'event_title': ev.get('title', ''),
                'category': ev.get('category', ''),
                'ask_sum': ask_sum,
                'bid_sum': bid_sum,
                'market_count': len(asks),
                'volume_24h': total_vol,
            })
        elif ask_sum > 103:
            # Overpriced: sell all YES (= buy NO on each)
            # Actual profit depends on bid side — you sell at yes_bid
            sell_profit = (bid_sum - 100) if bid_sum and bid_sum > 100 else None
            profit = ask_sum - 100
            results.append({
                'scan': 'multi_outcome',
                'severity': severity(sell_profit if sell_profit else profit),
                'profit_cents': sell_profit if sell_profit else profit,
                'description': f'SELL ALL: {len(asks)} outcomes sum_yes_ask={ask_sum}c (sum_yes_bid={bid_sum}) → ~{sell_profit or profit}c profit (sell YES)',
                'markets': [{'ticker': t, 'yes_ask': ya, 'title': title} for t, ya, title in asks],
                'event_ticker': ev.get('event_ticker', ''),
                'event_title': ev.get('title', ''),
                'category': ev.get('category', ''),
                'ask_sum': ask_sum,
                'bid_sum': bid_sum,
                'market_count': len(asks),
                'volume_24h': total_vol,
            })
    results.sort(key=lambda x: -abs(x['profit_cents']))
    return results

# ---------------------------------------------------------------------------
# Scan 3: Alt-Line Monotonicity
# ---------------------------------------------------------------------------

def scan_monotonicity(events, markets):
    """
    For 'greater' strike_type markets in the same event:
    higher floor_strike → yes_ask MUST be <= lower floor_strike's yes_ask.
    Inversions = guaranteed profit.
    """
    # Group markets by event_ticker, filter to greater + numeric floor_strike
    event_groups = defaultdict(list)
    for ticker, m in markets.items():
        if m.get('strike_type') != 'greater':
            continue
        fs = m.get('floor_strike')
        if fs is None:
            continue
        try:
            fs_num = float(fs)
        except (ValueError, TypeError):
            continue
        event_groups[m['event_ticker']].append({
            'ticker': ticker,
            'floor_strike': fs_num,
            'yes_ask': m.get('yes_ask'),
            'yes_bid': m.get('yes_bid'),
            'title': m.get('title', ''),
            'team': extract_team(ticker),
            'volume_24h': m.get('volume_24h', 0),
        })

    results = []
    for et, group_markets in event_groups.items():
        # Sub-group by team
        by_team = defaultdict(list)
        for gm in group_markets:
            by_team[gm['team']].append(gm)

        for team, team_markets in by_team.items():
            if len(team_markets) < 2:
                continue
            # Sort by floor_strike ascending
            sorted_mkts = sorted(team_markets, key=lambda x: x['floor_strike'])

            for i in range(len(sorted_mkts) - 1):
                lo = sorted_mkts[i]
                hi = sorted_mkts[i + 1]
                lo_ask = lo['yes_ask']
                hi_ask = hi['yes_ask']
                if lo_ask is None or hi_ask is None:
                    continue
                # Inversion: higher strike has HIGHER yes_ask
                if hi_ask > lo_ask:
                    # Buy YES on higher strike (cheaper should be, but isn't)
                    # Buy NO on lower strike (= sell YES at lower strike)
                    # If higher strike hits → lower MUST hit too → collect on both
                    profit = hi_ask - lo_ask
                    results.append({
                        'scan': 'monotonicity',
                        'severity': severity(profit),
                        'profit_cents': profit,
                        'description': (
                            f'INVERSION {team}: strike {lo["floor_strike"]}→{hi["floor_strike"]}, '
                            f'ask {lo_ask}c→{hi_ask}c (+{profit}c)'
                        ),
                        'markets': [
                            {'ticker': lo['ticker'], 'floor_strike': lo['floor_strike'],
                             'yes_ask': lo_ask, 'action': 'BUY NO', 'title': lo['title']},
                            {'ticker': hi['ticker'], 'floor_strike': hi['floor_strike'],
                             'yes_ask': hi_ask, 'action': 'BUY YES', 'title': hi['title']},
                        ],
                        'event_ticker': et,
                        'team': team,
                        'category': markets.get(lo['ticker'], {}).get('category', ''),
                        'volume_24h': lo['volume_24h'] + hi['volume_24h'],
                    })

    results.sort(key=lambda x: -x['profit_cents'])
    return results

# ---------------------------------------------------------------------------
# Scan 4: Cross-Event Implied Probability
# ---------------------------------------------------------------------------

SPORT_PREFIXES = {
    'KXNBAGAME', 'KXNBASPREAD', 'KXNBATOTAL',
    'KXNHLGAME', 'KXNHLSPREAD', 'KXNHLTOTAL',
    'KXNCAAMBGAME', 'KXNCAAMBSPREAD', 'KXNCAAMBTOTAL',
    'KXNFLGAME', 'KXNFLSPREAD', 'KXNFLTOTAL',
    'KXMLBGAME', 'KXMLBSPREAD', 'KXMLBTOTAL',
}

def classify_sport_event(event_ticker):
    """Returns (game_id, market_type) or (None, None)."""
    prefix = extract_series_prefix(event_ticker)
    if prefix not in SPORT_PREFIXES:
        return None, None
    game_id = extract_game_id(event_ticker)
    if 'SPREAD' in prefix:
        mtype = 'spread'
    elif 'TOTAL' in prefix:
        mtype = 'total'
    else:
        mtype = 'moneyline'
    return game_id, mtype


def scan_cross_event(events, markets):
    """Compare implied probabilities across moneyline vs spread for same game."""
    # Group events by game_id
    games = defaultdict(dict)  # game_id → {moneyline: event, spread: event, total: event}
    for ev in events:
        game_id, mtype = classify_sport_event(ev['event_ticker'])
        if game_id and mtype:
            games[game_id][mtype] = ev

    results = []
    for game_id, types in games.items():
        ml_ev = types.get('moneyline')
        sp_ev = types.get('spread')
        if not ml_ev or not sp_ev:
            continue

        # Get moneyline prices (team YES = win prob)
        ml_prices = {}  # team → yes_ask
        for t in ml_ev.get('market_tickers', []):
            m = markets.get(t)
            if m and m.get('yes_ask') is not None:
                team = extract_team(t)
                ml_prices[team] = m['yes_ask']

        # Get spread-implied probabilities from the lowest strike
        # At spread floor_strike=1.5, yes_ask ≈ implied prob of winning by >1.5
        # We want the ~0.5 strike (closest to moneyline) or lowest available
        sp_prices = {}
        for t in sp_ev.get('market_tickers', []):
            m = markets.get(t)
            if not m or m.get('yes_ask') is None:
                continue
            fs = m.get('floor_strike')
            if fs is None:
                continue
            try:
                fs_num = float(fs)
            except (ValueError, TypeError):
                continue
            team = extract_team(t)
            # Keep the lowest floor_strike per team (closest to moneyline)
            if team not in sp_prices or fs_num < sp_prices[team][0]:
                sp_prices[team] = (fs_num, m['yes_ask'], t)

        # Compare ML vs lowest-spread implied probs
        for team in ml_prices:
            if team not in sp_prices:
                continue
            ml_prob = ml_prices[team]
            sp_strike, sp_prob, sp_ticker = sp_prices[team]
            gap = abs(ml_prob - sp_prob)
            if gap > 5:
                profit = gap
                ml_ticker = None
                for t in ml_ev.get('market_tickers', []):
                    if extract_team(t) == team:
                        ml_ticker = t
                        break
                results.append({
                    'scan': 'cross_event',
                    'severity': severity(profit),
                    'profit_cents': profit,
                    'description': (
                        f'{team} ML={ml_prob}c vs Spread({sp_strike})={sp_prob}c → {gap}c gap'
                    ),
                    'markets': [
                        {'ticker': ml_ticker or f'{team}_ML', 'yes_ask': ml_prob,
                         'type': 'moneyline', 'title': f'{team} moneyline'},
                        {'ticker': sp_ticker, 'yes_ask': sp_prob, 'floor_strike': sp_strike,
                         'type': 'spread', 'title': f'{team} spread >{sp_strike}'},
                    ],
                    'event_ticker': game_id,
                    'game_id': game_id,
                    'team': team,
                    'category': 'Sports',
                    'volume_24h': 0,
                })

    results.sort(key=lambda x: -x['profit_cents'])
    return results

# ---------------------------------------------------------------------------
# Scan 5: Crypto Time-Consistency
# ---------------------------------------------------------------------------

def scan_crypto_time(events, markets):
    """
    Same crypto underlying + same strike at different expiry dates.
    For 'greater' type: later expiry → yes_ask should be >= earlier expiry.
    """
    # Group crypto events by base ticker
    crypto_bases = defaultdict(list)
    for ev in events:
        if ev.get('category') != 'Crypto':
            continue
        base = extract_crypto_base(ev['event_ticker'])
        # Only include 'directional' bases (KXBTCD, KXETHD, KXSOLD, etc.)
        # Skip 'range' bases (KXBTC, KXETH — these are "between" range markets)
        crypto_bases[base].append(ev)

    results = []
    for base, base_events in crypto_bases.items():
        if len(base_events) < 2:
            continue

        # For each event, collect 'greater' markets keyed by floor_strike
        # Structure: {floor_strike: [(close_time, yes_ask, ticker, event_ticker), ...]}
        strike_series = defaultdict(list)
        for ev in base_events:
            for t in ev.get('market_tickers', []):
                m = markets.get(t)
                if not m:
                    continue
                if m.get('strike_type') != 'greater':
                    continue
                fs = m.get('floor_strike')
                ct = parse_close_time(m.get('close_time'))
                ya = m.get('yes_ask')
                if fs is None or ct is None or ya is None:
                    continue
                try:
                    fs_key = float(fs)
                except (ValueError, TypeError):
                    continue
                strike_series[fs_key].append((ct, ya, t, ev['event_ticker']))

        # Check monotonicity within each strike
        for fs_key, entries in strike_series.items():
            if len(entries) < 2:
                continue
            sorted_entries = sorted(entries, key=lambda x: x[0])  # sort by close_time

            for i in range(len(sorted_entries) - 1):
                early_ct, early_ask, early_t, early_ev = sorted_entries[i]
                late_ct, late_ask, late_t, late_ev = sorted_entries[i + 1]

                # Later expiry should have >= yes_ask (more time to hit target)
                # Inversion: later expiry has LOWER yes_ask
                if late_ask < early_ask:
                    profit = early_ask - late_ask
                    results.append({
                        'scan': 'crypto_time',
                        'severity': severity(profit),
                        'profit_cents': profit,
                        'description': (
                            f'{base} strike={fs_key}: '
                            f'early({early_ct.strftime("%m/%d")})={early_ask}c > '
                            f'late({late_ct.strftime("%m/%d")})={late_ask}c → {profit}c inversion'
                        ),
                        'markets': [
                            {'ticker': early_t, 'yes_ask': early_ask,
                             'close_time': str(early_ct), 'action': 'SELL (buy NO)',
                             'title': f'{base} >{fs_key} expires {early_ct.strftime("%m/%d")}'},
                            {'ticker': late_t, 'yes_ask': late_ask,
                             'close_time': str(late_ct), 'action': 'BUY YES',
                             'title': f'{base} >{fs_key} expires {late_ct.strftime("%m/%d")}'},
                        ],
                        'event_ticker': base,
                        'floor_strike': fs_key,
                        'category': 'Crypto',
                        'volume_24h': 0,
                    })

    results.sort(key=lambda x: -x['profit_cents'])
    return results

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

SCAN_LABELS = {
    'binary_complement': 'Binary Complement (buy YES + NO < $1)',
    'multi_outcome': 'Multi-Outcome Sum (mutually exclusive)',
    'monotonicity': 'Alt-Line Monotonicity Inversion',
    'cross_event': 'Cross-Event Implied Probability Gap',
    'crypto_time': 'Crypto Time-Consistency Inversion',
}

def print_report(all_results):
    print('\n' + '=' * 70)
    print('  INTRA-KALSHI CONTRADICTION SCANNER')
    print('=' * 70)

    # Summary counts
    by_scan = defaultdict(list)
    for r in all_results:
        by_scan[r['scan']].append(r)

    total_profit = sum(r['profit_cents'] for r in all_results)
    high_count = sum(1 for r in all_results if r['severity'] == 'HIGH')
    med_count = sum(1 for r in all_results if r['severity'] == 'MEDIUM')

    print(f'\n  Total contradictions: {len(all_results)}')
    print(f'  HIGH severity (>={HIGH_THRESHOLD}c): {high_count}')
    print(f'  MEDIUM severity (>={MEDIUM_THRESHOLD}c): {med_count}')
    print(f'  Total profit potential: {total_profit}c across all signals')

    for scan_type in ['binary_complement', 'multi_outcome', 'monotonicity', 'cross_event', 'crypto_time']:
        items = by_scan.get(scan_type, [])
        label = SCAN_LABELS.get(scan_type, scan_type)
        print(f'\n  --- {label} ({len(items)}) ---')
        if not items:
            print('    None found')
            continue

        # Show top 15 per scan type
        for r in items[:15]:
            sev_tag = f'[{r["severity"]:>6s}]'
            profit_tag = f'{r["profit_cents"]:>4d}c'
            print(f'    {sev_tag} {profit_tag}  {r["description"]}')
        if len(items) > 15:
            remaining_profit = sum(r['profit_cents'] for r in items[15:])
            print(f'    ... +{len(items) - 15} more ({remaining_profit}c total)')

    print('\n' + '=' * 70)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(input_path='market_surface.json', output_path='contradictions.json'):
    events, markets = load_surface(input_path)

    print('\nRunning 5 scans on ALL markets...')

    r1 = scan_binary_complement(markets)
    print(f'  [1/5] Binary complement: {len(r1)} contradictions')

    r2 = scan_multi_outcome(events, markets)
    print(f'  [2/5] Multi-outcome sum: {len(r2)} contradictions')

    r3 = scan_monotonicity(events, markets)
    print(f'  [3/5] Monotonicity: {len(r3)} contradictions')

    r4 = scan_cross_event(events, markets)
    print(f'  [4/5] Cross-event: {len(r4)} contradictions')

    r5 = scan_crypto_time(events, markets)
    print(f'  [5/5] Crypto time: {len(r5)} contradictions')

    all_results = r1 + r2 + r3 + r4 + r5
    print_report(all_results)

    # Save
    with open(output_path, 'w') as f:
        json.dump({
            'generated_at': __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime()),
            'scan_counts': {
                'binary_complement': len(r1),
                'multi_outcome': len(r2),
                'monotonicity': len(r3),
                'cross_event': len(r4),
                'crypto_time': len(r5),
                'total': len(all_results),
            },
            'contradictions': all_results,
        }, f, indent=2, default=str)
    print(f'\n  Saved {len(all_results)} contradictions to {output_path} ({os.path.getsize(output_path) / 1024:.0f} KB)')


def main():
    parser = argparse.ArgumentParser(description='Intra-Kalshi Contradiction Scanner')
    parser.add_argument('--input', type=str, default='market_surface.json', help='Input surface JSON')
    parser.add_argument('--output', type=str, default='contradictions.json', help='Output contradictions JSON')
    args = parser.parse_args()
    run(input_path=args.input, output_path=args.output)


if __name__ == '__main__':
    main()
