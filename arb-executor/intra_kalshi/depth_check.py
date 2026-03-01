"""
Monotonicity Inversion Depth Checker
Fetches live orderbooks for all monotonicity inversions and ranks by
executable profit × fillable depth.

Trade logic for an inversion where hi_ask > lo_ask (higher strike overpriced):
  - BUY YES on LOWER strike @ lo_ask  (underpriced — should cost MORE)
  - BUY NO on HIGHER strike @ hi_no_ask = (100 - hi_bid)  (overpriced — short it)
  - Combined cost = lo_ask + (100 - hi_bid)

Payoff matrix:
  1. Both settle YES (team covers hi): lo YES=100, hi NO=0   → payout 100
  2. lo YES, hi NO (covers lo not hi): lo YES=100, hi NO=100 → payout 200
  3. Both settle NO (doesn't cover lo): lo YES=0,   hi NO=100 → payout 100
  Minimum payout = 100c ALWAYS.
  Guaranteed profit = 100 - cost = hi_bid - lo_ask

Usage:
    cd arb-executor
    python -m intra_kalshi.depth_check [--top 20]
"""

import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict

import aiohttp

from .discovery import (
    load_credentials, auth_headers, RateLimiter, api_get,
    BASE_URL, MAX_CONCURRENCY,
)
from .scanner import load_surface, scan_monotonicity, extract_team

# ---------------------------------------------------------------------------
# Orderbook parsing
# ---------------------------------------------------------------------------

def parse_ob_price(v):
    """Handle both cent ints and FixedPointDollar strings."""
    if isinstance(v, str):
        return round(float(v) * 100)
    return int(v)


def compute_depth(orderbook, side, price_threshold):
    """Compute total fillable qty at price >= threshold on given side.

    For BUY YES: side='no' (match against NO bids), threshold = 100 - yes_ask
    For BUY NO:  side='yes' (match against YES bids), threshold = yes_bid
    """
    if not orderbook or side not in orderbook:
        return 0
    total = 0
    for entry in orderbook[side]:
        if len(entry) < 2:
            continue
        price = parse_ob_price(entry[0])
        qty = int(entry[1])
        if price >= price_threshold:
            total += qty
    return total

# ---------------------------------------------------------------------------
# Fetch orderbooks
# ---------------------------------------------------------------------------

async def fetch_orderbooks(tickers, api_key, private_key):
    """Fetch orderbooks for a list of tickers. Returns {ticker: orderbook}."""
    rate_limiter = RateLimiter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results = {}

    async def fetch_one(session, ticker):
        path = f'/trade-api/v2/markets/{ticker}/orderbook?depth=0'
        data = await api_get(session, api_key, private_key, path, rate_limiter, semaphore)
        if data:
            results[ticker] = data.get('orderbook', {})

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, t) for t in tickers]
        await asyncio.gather(*tasks)

    return results

# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

async def run(top_n=20):
    # Load surface and run scan
    events, markets = load_surface('market_surface.json')
    inversions = scan_monotonicity(events, markets)
    print(f'\n{len(inversions)} monotonicity inversions found')

    if not inversions:
        print('No inversions to check.')
        return

    # Collect unique tickers
    tickers = set()
    for inv in inversions:
        for m in inv['markets']:
            tickers.add(m['ticker'])
    print(f'Fetching orderbooks for {len(tickers)} unique tickers...')

    # Fetch
    api_key, private_key = load_credentials()
    orderbooks = await fetch_orderbooks(tickers, api_key, private_key)
    print(f'Got {len(orderbooks)} orderbooks\n')

    # Analyze each inversion
    ranked = []
    for inv in inversions:
        lo_m = inv['markets'][0]  # lower strike
        hi_m = inv['markets'][1]  # higher strike

        lo_ticker = lo_m['ticker']
        hi_ticker = hi_m['ticker']
        lo_ask = lo_m['yes_ask']
        hi_ask = hi_m['yes_ask']
        lo_bid = lo_m.get('yes_bid', 0)
        hi_bid = hi_m.get('yes_bid', 0)
        lo_strike = lo_m['floor_strike']
        hi_strike = hi_m['floor_strike']

        # Correct trade: BUY YES lower + BUY NO higher
        # Cost = lo_ask + (100 - hi_bid)
        # Profit = hi_bid - lo_ask
        hi_no_ask = 100 - hi_bid
        combined_cost = lo_ask + hi_no_ask
        exec_profit = hi_bid - lo_ask

        if exec_profit <= 0:
            continue  # not executable at current bid/ask

        lo_ob = orderbooks.get(lo_ticker, {})
        hi_ob = orderbooks.get(hi_ticker, {})

        # Depth for BUY YES on lower: match against NO bids at >= (100 - lo_ask)
        lo_depth = compute_depth(lo_ob, 'no', 100 - lo_ask)

        # Depth for BUY NO on higher: match against YES bids at >= hi_bid
        hi_depth = compute_depth(hi_ob, 'yes', hi_bid)

        min_depth = min(lo_depth, hi_depth)
        score = exec_profit * min_depth

        # Get close time from surface data
        lo_close = markets.get(lo_ticker, {}).get('close_time', '?')
        hi_close = markets.get(hi_ticker, {}).get('close_time', '?')
        lo_vol = markets.get(lo_ticker, {}).get('volume_24h', 0)
        hi_vol = markets.get(hi_ticker, {}).get('volume_24h', 0)
        category = markets.get(lo_ticker, {}).get('category', '')

        ranked.append({
            'score': score,
            'exec_profit': exec_profit,
            'min_depth': min_depth,
            'lo_depth': lo_depth,
            'hi_depth': hi_depth,
            'lo_ticker': lo_ticker,
            'hi_ticker': hi_ticker,
            'lo_strike': lo_strike,
            'hi_strike': hi_strike,
            'lo_ask': lo_ask,
            'hi_ask': hi_ask,
            'lo_bid': lo_bid,
            'hi_bid': hi_bid,
            'hi_no_ask': hi_no_ask,
            'combined_cost': combined_cost,
            'lo_vol': lo_vol,
            'hi_vol': hi_vol,
            'lo_close': lo_close,
            'hi_close': hi_close,
            'team': inv.get('team', ''),
            'event_ticker': inv.get('event_ticker', ''),
            'category': category,
            'ask_inversion': hi_ask - lo_ask,
        })

    ranked.sort(key=lambda x: -x['score'])

    # Print report
    print('=' * 90)
    print('  MONOTONICITY INVERSIONS — RANKED BY (profit × depth)')
    print('=' * 90)
    print(f'\n  {len(ranked)} executable inversions (hi_bid > lo_ask)')
    print(f'  {sum(1 for r in ranked if r["min_depth"] > 0)} with depth on both sides\n')

    for i, r in enumerate(ranked[:top_n]):
        print(f'  #{i+1}  score={r["score"]:,}  profit={r["exec_profit"]}c × depth={r["min_depth"]}')
        print(f'      Event: {r["event_ticker"]}  Team: {r["team"]}  Category: {r["category"]}')
        print(f'      ┌ LOWER strike={r["lo_strike"]}')
        print(f'      │   {r["lo_ticker"]}')
        print(f'      │   yes_ask={r["lo_ask"]}c  yes_bid={r["lo_bid"]}c  '
              f'vol={r["lo_vol"]:,}  depth@ask={r["lo_depth"]}')
        print(f'      │   close: {r["lo_close"]}')
        print(f'      ├ HIGHER strike={r["hi_strike"]}')
        print(f'      │   {r["hi_ticker"]}')
        print(f'      │   yes_ask={r["hi_ask"]}c  yes_bid={r["hi_bid"]}c  '
              f'vol={r["hi_vol"]:,}  depth@bid={r["hi_depth"]}')
        print(f'      │   close: {r["hi_close"]}')
        print(f'      └ TRADE:')
        print(f'          BUY YES {r["lo_ticker"]} @ {r["lo_ask"]}c')
        print(f'        + BUY NO  {r["hi_ticker"]} @ {r["hi_no_ask"]}c')
        print(f'        = Cost {r["combined_cost"]}c → payout ≥100c → PROFIT {r["exec_profit"]}c guaranteed')
        print(f'          Ask inversion: {r["ask_inversion"]}c  (hi_ask={r["hi_ask"]}c > lo_ask={r["lo_ask"]}c)')
        print()

    if len(ranked) > top_n:
        rest = ranked[top_n:]
        print(f'  ... +{len(rest)} more inversions '
              f'(total score={sum(r["score"] for r in rest):,})')

    # Summary stats
    with_depth = [r for r in ranked if r['min_depth'] > 0]
    print(f'\n  SUMMARY:')
    print(f'    Executable inversions: {len(ranked)}')
    print(f'    With depth both sides: {len(with_depth)}')
    if with_depth:
        total_profit = sum(r['exec_profit'] * r['min_depth'] for r in with_depth)
        print(f'    Total profit×depth:    {total_profit:,}c')
        print(f'    Best single trade:     {with_depth[0]["exec_profit"]}c × {with_depth[0]["min_depth"]} contracts')
    print('=' * 90)


def main():
    parser = argparse.ArgumentParser(description='Monotonicity Depth Check')
    parser.add_argument('--top', type=int, default=20, help='Show top N results')
    args = parser.parse_args()
    asyncio.run(run(top_n=args.top))


if __name__ == '__main__':
    main()
