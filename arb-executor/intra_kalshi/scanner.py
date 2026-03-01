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

def is_dead(m):
    """Market is dead/resolved: yes_ask=100, yes_bid=0, or no volume."""
    return (
        m.get('yes_ask') in (None, 100) or
        m.get('yes_bid') in (None, 0) or
        m.get('volume_24h', 0) == 0
    )


def scan_binary_complement(markets):
    """Markets where yes_ask + no_ask < 98c — buy both = guaranteed profit."""
    results = []
    for ticker, m in markets.items():
        if is_dead(m):
            continue
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
    """Mutually exclusive events where BID sum deviates from 100c by > 3c."""
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
                asks.append((t, ya, yb or 0, m.get('title', ''), m.get('volume_24h', 0)))
            if yb is not None:
                bids.append((t, yb))

        if len(asks) < 2:
            continue

        ask_sum = sum(a[1] for a in asks)
        bid_sum = sum(b[1] for b in bids) if bids else 0
        total_vol = sum(a[4] for a in asks)

        # Only report if BID sum deviates > 3c — that's what's actually executable
        if bid_sum < 97:
            # Underpriced on bid side: buy all YES at ask
            # Profit is limited by what we actually pay (ask side)
            profit = 100 - ask_sum if ask_sum < 100 else 0
            if profit <= 0:
                continue
            results.append({
                'scan': 'multi_outcome',
                'severity': severity(profit),
                'profit_cents': profit,
                'description': f'BUY ALL: {len(asks)} outcomes ask_sum={ask_sum}c bid_sum={bid_sum}c → {profit}c profit',
                'markets': [{'ticker': t, 'yes_ask': ya, 'yes_bid': yb, 'title': title}
                            for t, ya, yb, title, _ in asks],
                'event_ticker': ev.get('event_ticker', ''),
                'event_title': ev.get('title', ''),
                'category': ev.get('category', ''),
                'ask_sum': ask_sum,
                'bid_sum': bid_sum,
                'market_count': len(asks),
                'volume_24h': total_vol,
            })
        elif bid_sum > 103:
            # Overpriced: sell all YES at bid price
            profit = bid_sum - 100
            results.append({
                'scan': 'multi_outcome',
                'severity': severity(profit),
                'profit_cents': profit,
                'description': f'SELL ALL: {len(asks)} outcomes bid_sum={bid_sum}c ask_sum={ask_sum}c → {profit}c profit',
                'markets': [{'ticker': t, 'yes_ask': ya, 'yes_bid': yb, 'title': title}
                            for t, ya, yb, title, _ in asks],
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
                lo_bid = lo.get('yes_bid')
                hi_bid = hi.get('yes_bid')
                if lo_ask is None or hi_ask is None:
                    continue
                # Filter dead markets: both must have yes_bid > 0 and yes_ask < 99
                if not lo_bid or lo_bid <= 0 or not hi_bid or hi_bid <= 0:
                    continue
                if lo_ask >= 99 or hi_ask >= 99:
                    continue
                # Inversion: higher strike has HIGHER yes_ask
                if hi_ask > lo_ask:
                    profit = hi_ask - lo_ask
                    # Correct trade: BUY YES lower (underpriced) + BUY NO higher (overpriced)
                    # Cost = lo_ask + (100 - hi_bid), profit = hi_bid - lo_ask
                    exec_profit = hi_bid - lo_ask
                    results.append({
                        'scan': 'monotonicity',
                        'severity': severity(profit),
                        'profit_cents': profit,
                        'exec_profit': exec_profit,
                        'description': (
                            f'INVERSION {team}: strike {lo["floor_strike"]}→{hi["floor_strike"]}, '
                            f'ask {lo_ask}c→{hi_ask}c (+{profit}c, exec={exec_profit}c)'
                        ),
                        'markets': [
                            {'ticker': lo['ticker'], 'floor_strike': lo['floor_strike'],
                             'yes_ask': lo_ask, 'yes_bid': lo_bid, 'action': 'BUY YES', 'title': lo['title']},
                            {'ticker': hi['ticker'], 'floor_strike': hi['floor_strike'],
                             'yes_ask': hi_ask, 'yes_bid': hi_bid, 'action': 'BUY NO', 'title': hi['title']},
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


def detect_sport(event_ticker):
    """Detect sport from event ticker prefix."""
    prefix = extract_series_prefix(event_ticker).upper()
    if 'NBA' in prefix:
        return 'NBA'
    if 'NHL' in prefix:
        return 'NHL'
    if 'NCAAMB' in prefix:
        return 'CBB'
    if 'NFL' in prefix:
        return 'NFL'
    if 'MLB' in prefix:
        return 'MLB'
    return 'OTHER'


def scan_cross_event(events, markets):
    """Flag IMPOSSIBLE contradictions only:
    Type A: spread(>X) yes_ask > ML yes_ask — can't cover spread without winning.
            Executable profit = spread_yes_bid - ml_yes_ask (when positive).
    Type B: same-team spread inversion — higher line costs more than lower line.
            e.g., spread(>4.5) yes_ask > spread(>1.5) yes_ask.
    Both markets must have non-zero volume and live books (bid>0, ask<99)."""
    games = defaultdict(dict)
    for ev in events:
        game_id, mtype = classify_sport_event(ev['event_ticker'])
        if game_id and mtype:
            games[game_id][mtype] = ev

    results = []
    for game_id, types in games.items():
        ml_ev = types.get('moneyline')
        sp_ev = types.get('spread')
        if not sp_ev:
            continue

        sport = detect_sport(sp_ev['event_ticker'])

        # Collect ML data per team (if ML event exists)
        ml_data = {}  # team → (yes_ask, yes_bid, ticker, vol)
        if ml_ev:
            for t in ml_ev.get('market_tickers', []):
                m = markets.get(t)
                if not m or m.get('yes_ask') is None:
                    continue
                if m.get('volume_24h', 0) == 0 or m.get('yes_bid', 0) <= 0 or m['yes_ask'] >= 99:
                    continue
                team = extract_team(t)
                ml_data[team] = (m['yes_ask'], m.get('yes_bid', 0), t, m.get('volume_24h', 0))

        # Collect ALL spread lines per team (not just lowest)
        sp_by_team = defaultdict(list)  # team → [(strike, ask, bid, ticker, vol), ...]
        for t in sp_ev.get('market_tickers', []):
            m = markets.get(t)
            if not m or m.get('yes_ask') is None:
                continue
            if m.get('volume_24h', 0) == 0 or m.get('yes_bid', 0) <= 0 or m['yes_ask'] >= 99:
                continue
            fs = m.get('floor_strike')
            if fs is None:
                continue
            try:
                fs_num = float(fs)
            except (ValueError, TypeError):
                continue
            team = extract_team(t)
            sp_by_team[team].append((fs_num, m['yes_ask'], m.get('yes_bid', 0), t, m.get('volume_24h', 0)))

        # Type A: spread_ask > ml_ask (IMPOSSIBLE — covering implies winning)
        for team, spreads in sp_by_team.items():
            if team not in ml_data:
                continue
            ml_ask, ml_bid, ml_ticker, ml_vol = ml_data[team]

            for sp_strike, sp_ask, sp_bid, sp_ticker, sp_vol in spreads:
                if sp_strike <= 0:
                    continue  # negative spreads can exceed ML
                if sp_ask > ml_ask:
                    # Executable arb: buy ML YES (cheap) + buy Spread NO
                    # Spread NO ask = 100 - sp_bid
                    # Min payout = 100c in all outcomes
                    # Profit = sp_bid - ml_ask (if positive)
                    exec_profit = sp_bid - ml_ask
                    if exec_profit <= 0:
                        continue
                    results.append({
                        'scan': 'cross_event',
                        'severity': severity(exec_profit),
                        'profit_cents': exec_profit,
                        'type': 'spread_exceeds_ml',
                        'description': (
                            f'[{sport}] IMPOSSIBLE: {team} Spread(>{sp_strike}) ask={sp_ask}c > ML ask={ml_ask}c'
                        ),
                        'action': (
                            f'BUY ML YES@{ml_ask}c + BUY Spread NO@{100 - sp_bid}c = '
                            f'{ml_ask + 100 - sp_bid}c → min payout 100c → {exec_profit}c profit'
                        ),
                        'markets': [
                            {'ticker': ml_ticker, 'yes_ask': ml_ask, 'yes_bid': ml_bid,
                             'type': 'moneyline', 'volume_24h': ml_vol},
                            {'ticker': sp_ticker, 'yes_ask': sp_ask, 'yes_bid': sp_bid,
                             'floor_strike': sp_strike, 'type': 'spread', 'volume_24h': sp_vol},
                        ],
                        'event_ticker': game_id,
                        'game_id': game_id,
                        'sport': sport,
                        'team': team,
                        'category': 'Sports',
                        'volume_24h': ml_vol + sp_vol,
                    })

        # Type B: same-team spread inversion (higher line costs more)
        for team, spreads in sp_by_team.items():
            if len(spreads) < 2:
                continue
            sorted_sp = sorted(spreads, key=lambda x: x[0])  # sort by strike asc
            for i in range(len(sorted_sp) - 1):
                lo_strike, lo_ask, lo_bid, lo_ticker, lo_vol = sorted_sp[i]
                hi_strike, hi_ask, hi_bid, hi_ticker, hi_vol = sorted_sp[i + 1]
                if hi_ask > lo_ask:
                    # Executable: buy hi YES + buy lo NO
                    # If hi hits → lo MUST hit → hi YES=100, lo NO=0 → payout=100
                    # If lo hits but not hi → hi YES=0, lo NO=0 → payout=0... wait
                    # Actually: buy lo NO @ (100-lo_bid) + buy hi YES @ hi_ask
                    # lo hits, hi doesn't: lo NO=0, hi YES=0 → lose both
                    # So this is NOT a guaranteed arb from buying, it's a mispricing signal
                    # The arb: SELL hi YES @ hi_bid + BUY lo YES @ lo_ask
                    # = you think lo > hi (correct), pocket the difference
                    # Guaranteed: if hi settles YES → lo settles YES too
                    # If lo settles NO → hi settles NO too
                    # Only risk: lo YES, hi NO (team wins by between lo and hi)
                    # Not riskless, but price inversion is still impossible
                    exec_profit = hi_bid - lo_ask
                    if exec_profit <= 0:
                        continue
                    results.append({
                        'scan': 'cross_event',
                        'severity': severity(exec_profit),
                        'profit_cents': exec_profit,
                        'type': 'spread_inversion',
                        'description': (
                            f'[{sport}] INVERSION: {team} Spread(>{hi_strike}) ask={hi_ask}c > '
                            f'Spread(>{lo_strike}) ask={lo_ask}c'
                        ),
                        'action': (
                            f'BUY Spread(>{lo_strike}) YES@{lo_ask}c + SELL Spread(>{hi_strike}) YES@{hi_bid}c → '
                            f'{exec_profit}c edge (hi settles YES → lo MUST too)'
                        ),
                        'markets': [
                            {'ticker': lo_ticker, 'yes_ask': lo_ask, 'yes_bid': lo_bid,
                             'floor_strike': lo_strike, 'type': 'spread', 'volume_24h': lo_vol},
                            {'ticker': hi_ticker, 'yes_ask': hi_ask, 'yes_bid': hi_bid,
                             'floor_strike': hi_strike, 'type': 'spread', 'volume_24h': hi_vol},
                        ],
                        'event_ticker': game_id,
                        'game_id': game_id,
                        'sport': sport,
                        'team': team,
                        'category': 'Sports',
                        'volume_24h': lo_vol + hi_vol,
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
    Filters: no yes_ask=100 (dead), no expired markets.
    """
    now = datetime.now().astimezone()

    # Group crypto events by base ticker
    crypto_bases = defaultdict(list)
    for ev in events:
        if ev.get('category') != 'Crypto':
            continue
        base = extract_crypto_base(ev['event_ticker'])
        crypto_bases[base].append(ev)

    results = []
    for base, base_events in crypto_bases.items():
        if len(base_events) < 2:
            continue

        strike_series = defaultdict(list)
        for ev in base_events:
            for t in ev.get('market_tickers', []):
                m = markets.get(t)
                if not m:
                    continue
                if m.get('strike_type') != 'greater':
                    continue
                ya = m.get('yes_ask')
                # Filter dead markets
                if ya is None or ya >= 100 or ya <= 0:
                    continue
                if m.get('yes_bid', 0) <= 0:
                    continue
                fs = m.get('floor_strike')
                ct = parse_close_time(m.get('close_time'))
                if fs is None or ct is None:
                    continue
                # Filter expired
                if ct <= now:
                    continue
                try:
                    fs_key = float(fs)
                except (ValueError, TypeError):
                    continue
                strike_series[fs_key].append((ct, ya, m.get('yes_bid', 0), t, ev['event_ticker'],
                                              m.get('volume_24h', 0)))

        for fs_key, entries in strike_series.items():
            if len(entries) < 2:
                continue
            sorted_entries = sorted(entries, key=lambda x: x[0])

            for i in range(len(sorted_entries) - 1):
                early_ct, early_ask, early_bid, early_t, early_ev, early_vol = sorted_entries[i]
                late_ct, late_ask, late_bid, late_t, late_ev, late_vol = sorted_entries[i + 1]

                # Later expiry should have >= yes_ask
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
                            {'ticker': early_t, 'yes_ask': early_ask, 'yes_bid': early_bid,
                             'close_time': str(early_ct), 'action': 'SELL (buy NO)',
                             'volume_24h': early_vol},
                            {'ticker': late_t, 'yes_ask': late_ask, 'yes_bid': late_bid,
                             'close_time': str(late_ct), 'action': 'BUY YES',
                             'volume_24h': late_vol},
                        ],
                        'event_ticker': base,
                        'floor_strike': fs_key,
                        'category': 'Crypto',
                        'volume_24h': early_vol + late_vol,
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

        # Show top 25 for cross_event, 15 for others
        show_n = 25 if scan_type == 'cross_event' else 15
        for r in items[:show_n]:
            sev_tag = f'[{r["severity"]:>6s}]'
            profit_tag = f'{r["profit_cents"]:>4d}c'
            vol_tag = f'vol={r.get("volume_24h", 0):>10,}' if r.get('volume_24h') else ''
            print(f'    {sev_tag} {profit_tag}  {r["description"]}  {vol_tag}')
            if r.get('action'):
                print(f'             → {r["action"]}')
        if len(items) > show_n:
            remaining_profit = sum(r['profit_cents'] for r in items[show_n:])
            print(f'    ... +{len(items) - show_n} more ({remaining_profit}c total)')

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
