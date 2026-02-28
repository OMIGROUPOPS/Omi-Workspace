#!/usr/bin/env python3
"""
Kalshi API client for fills/settlements reconciliation.

Provides ground-truth P&L data from Kalshi exchange.
Used by settle_positions.py, daily_recap.py, and dashboard_push.py.

Usage as standalone:
    python kalshi_reconciler.py              # pull + cache + print summary
    python kalshi_reconciler.py --refresh    # force refresh from API
"""

import asyncio
import aiohttp
import base64
import json
import os
import sys
import time
from collections import defaultdict
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KALSHI_API_KEY = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
KALSHI_PEM_PATH = os.path.join(SCRIPT_DIR, 'kalshi.pem')
KALSHI_BASE_URL = 'https://api.elections.kalshi.com'

FILLS_CACHE = os.path.join(SCRIPT_DIR, 'kalshi_fills_cache.json')
SETTLEMENTS_CACHE = os.path.join(SCRIPT_DIR, 'kalshi_settlements_cache.json')

# Cache is stale after 5 minutes
CACHE_TTL_SECONDS = 300


# ── Auth ──────────────────────────────────────────────────────────────────

def _load_private_key():
    with open(KALSHI_PEM_PATH, 'r') as f:
        key_data = f.read()
    return serialization.load_pem_private_key(
        key_data.encode(), password=None, backend=default_backend()
    )


def _sign(private_key, ts: str, method: str, path: str) -> str:
    msg = f'{ts}{method}{path}'.encode('utf-8')
    sig = private_key.sign(
        msg,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(sig).decode('utf-8')


def _headers(private_key, method: str, path: str) -> dict:
    """Generate auth headers. Sign base path only (no query params)."""
    ts = str(int(time.time() * 1000))
    base_path = path.split('?')[0] if '?' in path else path
    return {
        'KALSHI-ACCESS-KEY': KALSHI_API_KEY,
        'KALSHI-ACCESS-SIGNATURE': _sign(private_key, ts, method, base_path),
        'KALSHI-ACCESS-TIMESTAMP': ts,
        'Content-Type': 'application/json'
    }


# ── API pulls ─────────────────────────────────────────────────────────────

async def _pull_paginated(session, private_key, base_path: str, key: str,
                          since_date: Optional[str] = None) -> list:
    """Pull all records from a paginated Kalshi endpoint."""
    all_records = []
    cursor = None
    while True:
        path = f'{base_path}?limit=1000'
        if cursor:
            path += f'&cursor={cursor}'
        if since_date:
            path += f'&min_ts={since_date}T00:00:00Z'

        headers = _headers(private_key, 'GET', path)
        async with session.get(
            f'{KALSHI_BASE_URL}{path}',
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as r:
            if r.status != 200:
                text = await r.text()
                print(f'  [WARN] {base_path}: HTTP {r.status}: {text[:200]}')
                break
            data = await r.json()
            records = data.get(key, [])
            all_records.extend(records)
            cursor = data.get('cursor')
            if not cursor or not records:
                break
    return all_records


async def pull_fills(session, private_key, since_date: Optional[str] = None) -> list:
    return await _pull_paginated(
        session, private_key,
        '/trade-api/v2/portfolio/fills', 'fills',
        since_date=since_date
    )


async def pull_settlements(session, private_key, since_date: Optional[str] = None) -> list:
    return await _pull_paginated(
        session, private_key,
        '/trade-api/v2/portfolio/settlements', 'settlements',
        since_date=since_date
    )


async def pull_balance(session, private_key) -> dict:
    path = '/trade-api/v2/portfolio/balance'
    headers = _headers(private_key, 'GET', path)
    async with session.get(
        f'{KALSHI_BASE_URL}{path}',
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        return await r.json()


# ── Cache management ──────────────────────────────────────────────────────

def _cache_is_fresh(cache_path: str) -> bool:
    if not os.path.exists(cache_path):
        return False
    age = time.time() - os.path.getmtime(cache_path)
    return age < CACHE_TTL_SECONDS


def _read_cache(cache_path: str) -> list:
    with open(cache_path, 'r') as f:
        return json.load(f)


def _write_cache(cache_path: str, data: list):
    with open(cache_path, 'w') as f:
        json.dump(data, f)


# ── High-level API ────────────────────────────────────────────────────────

async def get_all_fills(force_refresh: bool = False, since_date: Optional[str] = None) -> list:
    """Get all Kalshi fills, using cache if fresh."""
    if not force_refresh and since_date is None and _cache_is_fresh(FILLS_CACHE):
        return _read_cache(FILLS_CACHE)

    private_key = _load_private_key()
    async with aiohttp.ClientSession() as session:
        fills = await pull_fills(session, private_key, since_date=since_date)

    if since_date is None:
        _write_cache(FILLS_CACHE, fills)
    return fills


async def get_all_settlements(force_refresh: bool = False, since_date: Optional[str] = None) -> list:
    """Get all Kalshi settlements, using cache if fresh."""
    if not force_refresh and since_date is None and _cache_is_fresh(SETTLEMENTS_CACHE):
        return _read_cache(SETTLEMENTS_CACHE)

    private_key = _load_private_key()
    async with aiohttp.ClientSession() as session:
        settlements = await pull_settlements(session, private_key, since_date=since_date)

    if since_date is None:
        _write_cache(SETTLEMENTS_CACHE, settlements)
    return settlements


async def get_fills_and_settlements(force_refresh: bool = False) -> tuple[list, list]:
    """Pull both fills and settlements (shared session for efficiency)."""
    use_cache = not force_refresh
    if use_cache and _cache_is_fresh(FILLS_CACHE) and _cache_is_fresh(SETTLEMENTS_CACHE):
        return _read_cache(FILLS_CACHE), _read_cache(SETTLEMENTS_CACHE)

    private_key = _load_private_key()
    async with aiohttp.ClientSession() as session:
        fills = await pull_fills(session, private_key)
        settlements = await pull_settlements(session, private_key)

    _write_cache(FILLS_CACHE, fills)
    _write_cache(SETTLEMENTS_CACHE, settlements)
    return fills, settlements


# ── Aggregation helpers ───────────────────────────────────────────────────

def get_fill_cost_by_ticker(fills: list) -> dict:
    """
    Aggregate fill data per ticker.

    Returns: {ticker: {
        cost_cents: int (total spent buying),
        revenue_cents: int (total received selling),
        net_cost_cents: int (cost - revenue),
        count: int (total contracts),
        fee_dollars: float,
        buys: [{side, count, price, fee}...],
        sells: [{side, count, price, fee}...],
    }}
    """
    by_ticker = {}
    for f in fills:
        ticker = f.get('ticker', '')
        if ticker not in by_ticker:
            by_ticker[ticker] = {
                'cost_cents': 0, 'revenue_cents': 0, 'net_cost_cents': 0,
                'count': 0, 'fee_dollars': 0.0,
                'yes_bought': 0, 'yes_sold': 0,
                'no_bought': 0, 'no_sold': 0,
                'yes_cost': 0, 'yes_revenue': 0,
                'no_cost': 0, 'no_revenue': 0,
            }

        rec = by_ticker[ticker]
        action = f.get('action', '')
        side = f.get('side', '')
        count = f.get('count', 0)
        yes_price = f.get('yes_price', 0)
        no_price = f.get('no_price', 0)
        fee = float(f.get('fee_cost', '0') or '0')
        price = yes_price if side == 'yes' else no_price

        rec['fee_dollars'] += fee
        rec['count'] += count

        if action == 'buy':
            rec['cost_cents'] += count * price
            if side == 'yes':
                rec['yes_bought'] += count
                rec['yes_cost'] += count * yes_price
            else:
                rec['no_bought'] += count
                rec['no_cost'] += count * no_price
        elif action == 'sell':
            rec['revenue_cents'] += count * price
            if side == 'yes':
                rec['yes_sold'] += count
                rec['yes_revenue'] += count * yes_price
            else:
                rec['no_sold'] += count
                rec['no_revenue'] += count * no_price

        rec['net_cost_cents'] = rec['cost_cents'] - rec['revenue_cents']

    # Add net position fields
    for rec in by_ticker.values():
        rec['net_yes'] = rec['yes_bought'] - rec['yes_sold']
        rec['net_no'] = rec['no_bought'] - rec['no_sold']

    return by_ticker


def get_settlement_by_ticker(settlements: list) -> dict:
    """
    Map settlements by ticker.

    Returns: {ticker: {
        revenue_cents: int,
        result: str ('yes'/'no'),
        yes_total_cost: int,
        no_total_cost: int,
        fee_dollars: float,
        settled_time: str,
    }}
    """
    by_ticker = {}
    for s in settlements:
        ticker = s.get('ticker', '')
        by_ticker[ticker] = {
            'revenue_cents': s.get('revenue', 0),
            'result': s.get('market_result', ''),
            'yes_count': s.get('yes_count', 0),
            'no_count': s.get('no_count', 0),
            'yes_total_cost': s.get('yes_total_cost', 0),
            'no_total_cost': s.get('no_total_cost', 0),
            'fee_dollars': float(s.get('fee_cost', '0') or '0'),
            'settled_time': s.get('settled_time', ''),
        }
    return by_ticker


def compute_kalshi_pnl(fill_rec: dict, settle_rec: dict) -> float:
    """
    Compute Kalshi-side P&L for a single ticker in dollars.

    Uses fills' net positions + settlement result (not the API revenue field,
    which doesn't properly account for short positions).

    P&L = (trade_cash_flow + settlement_value) / 100 - fees
    """
    # Cash flow from trading (cents): money received from sells minus money paid for buys
    cash_flow = (fill_rec['yes_revenue'] + fill_rec['no_revenue']
                 - fill_rec['yes_cost'] - fill_rec['no_cost'])

    # Settlement value from net positions (cents)
    settlement_value = 0
    if settle_rec:
        result = settle_rec['result']
        net_yes = fill_rec['net_yes']
        net_no = fill_rec['net_no']
        if result == 'yes':
            settlement_value = net_yes * 100  # each YES contract pays 100c
        elif result == 'no':
            settlement_value = net_no * 100   # each NO contract pays 100c

    gross = (cash_flow + settlement_value) / 100

    # Fees
    fill_fees = fill_rec['fee_dollars']
    settle_fees = settle_rec.get('fee_dollars', 0) if settle_rec else 0
    return gross - fill_fees - settle_fees


# ── Standalone CLI ────────────────────────────────────────────────────────

async def _main():
    import argparse
    parser = argparse.ArgumentParser(description="Kalshi reconciler")
    parser.add_argument("--refresh", action="store_true", help="Force refresh from API")
    args = parser.parse_args()

    print("Pulling Kalshi data...")
    fills, settlements = await get_fills_and_settlements(force_refresh=args.refresh)
    print(f"  Fills: {len(fills)}")
    print(f"  Settlements: {len(settlements)}")

    fill_map = get_fill_cost_by_ticker(fills)
    settle_map = get_settlement_by_ticker(settlements)

    # Summary
    total_gross = 0
    total_fees = 0
    settled_count = 0
    open_count = 0

    for ticker, fill_rec in sorted(fill_map.items()):
        settle_rec = settle_map.get(ticker)
        pnl = compute_kalshi_pnl(fill_rec, settle_rec)
        fees = fill_rec['fee_dollars'] + (settle_rec['fee_dollars'] if settle_rec else 0)
        total_gross += pnl + fees
        total_fees += fees
        if settle_rec:
            settled_count += 1
        else:
            open_count += 1

    print(f"\n  Tickers: {len(fill_map)} ({settled_count} settled, {open_count} open)")
    print(f"  Gross P&L: ${total_gross:+.2f}")
    print(f"  Fees: ${total_fees:.2f}")
    print(f"  Net P&L: ${total_gross - total_fees:+.2f}")

    # Balance check
    private_key = _load_private_key()
    async with aiohttp.ClientSession() as session:
        bal = await pull_balance(session, private_key)
    cash = bal.get('balance', 0) / 100
    port = bal.get('portfolio_value', 0) / 100
    print(f"\n  Kalshi balance: ${cash:.2f} cash + ${port:.2f} positions = ${cash + port:.2f}")


if __name__ == "__main__":
    asyncio.run(_main())
