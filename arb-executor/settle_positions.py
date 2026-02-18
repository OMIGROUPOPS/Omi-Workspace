#!/usr/bin/env python3
"""
settle_positions.py - Check settlement status of open PM positions and update trades.json.

Reads UNHEDGED / TIER3A_HOLD / TIER3B_FLIP trades from trades.json, queries
the PM US API for market settlement, and writes back the realized P&L as
`settlement_pnl` (in dollars).

Run manually:   python settle_positions.py
Run on cron:     */30 * * * * cd /path/to/arb-executor && python settle_positions.py >> logs/settle.log 2>&1

P&L logic (all amounts in cents, converted to dollars at the end):

  BUY_PM_SELL_K  (long PM — we bought YES or SHORT on PM, sold YES on Kalshi):
    Our PM leg is a long position on the traded team.
    If team won:  payout = 100c per contract, cost = pm_price_cents  → profit = (100 - pm_price_cents) * qty
    If team lost: payout = 0,   cost = pm_price_cents                → loss   = -pm_price_cents * qty

  BUY_K_SELL_PM  (short PM — we sold YES or LONG on PM, bought YES on Kalshi):
    Our PM leg is a short position on the traded team.
    If team lost: we keep the premium                                → profit = pm_price_cents * qty
    If team won:  we owe (100 - premium)                             → loss   = -(100 - pm_price_cents) * qty

NOTE: This only calculates the PM leg P&L.  The Kalshi leg settled separately
(Kalshi auto-settles).  For UNHEDGED trades, there IS no Kalshi hedge — the
entire P&L is the PM leg.
"""
import asyncio
import aiohttp
import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519

# ── Load .env ────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

PM_US_API_KEY = os.getenv('PM_US_API_KEY')
PM_US_SECRET_KEY = os.getenv('PM_US_SECRET_KEY')
BASE_URL = 'https://api.polymarket.us'
TRADES_FILE = os.path.join(os.path.dirname(__file__), 'trades.json')

# Statuses that represent open (unsettled) positions on the PM side
OPEN_STATUSES = {'UNHEDGED'}
OPEN_TIERS = {'TIER3A_HOLD', 'TIER3B_FLIP'}


# ── Auth helpers ─────────────────────────────────────────────────────────

def _make_private_key(secret_b64: str):
    secret_bytes = base64.b64decode(secret_b64)
    return ed25519.Ed25519PrivateKey.from_private_bytes(secret_bytes[:32])


def _sign(private_key, ts: str, method: str, path: str) -> str:
    message = f'{ts}{method}{path}'.encode('utf-8')
    signature = private_key.sign(message)
    return base64.b64encode(signature).decode('utf-8')


def _headers(private_key, api_key: str, method: str, path: str) -> dict:
    ts = str(int(time.time() * 1000))
    return {
        'X-PM-Access-Key': api_key,
        'X-PM-Timestamp': ts,
        'X-PM-Signature': _sign(private_key, ts, method, path),
        'Content-Type': 'application/json',
    }


# ── PM market fetch ─────────────────────────────────────────────────────

async def fetch_market(session, private_key, api_key: str, slug: str) -> dict | None:
    """Fetch a single market by slug.  Returns the market dict or None."""
    # Try the individual market endpoint first
    path = f'/v1/markets/{slug}'
    try:
        async with session.get(
            f'{BASE_URL}{path}',
            headers=_headers(private_key, api_key, 'GET', path),
            timeout=aiohttp.ClientTimeout(total=10),
        ) as r:
            if r.status == 200:
                data = await r.json()
                # Individual endpoint may return the market directly or nested
                if 'slug' in data:
                    return data
                if 'market' in data:
                    return data['market']
                return data
    except Exception:
        pass

    # Fallback: fetch the book endpoint which has marketData.state
    path = f'/v1/markets/{slug}/book'
    try:
        async with session.get(
            f'{BASE_URL}{path}',
            headers=_headers(private_key, api_key, 'GET', path),
            timeout=aiohttp.ClientTimeout(total=10),
        ) as r:
            if r.status == 200:
                data = await r.json()
                md = data.get('marketData', {})
                # Construct a pseudo-market dict from book response
                return {
                    'slug': slug,
                    'state': md.get('state', ''),
                    'status': md.get('status', ''),
                    'outcomes': md.get('outcomes', []),
                    'outcomePrices': md.get('outcomePrices', []),
                    'winningOutcome': md.get('winningOutcome'),
                    'resolvedOutcome': md.get('resolvedOutcome'),
                    '_source': 'book',
                }
    except Exception:
        pass

    return None


def is_settled(market: dict) -> bool:
    """Return True if the market is settled/resolved."""
    state = (market.get('state') or '').lower()
    status = (market.get('status') or '').lower()
    closed = market.get('closed', False)

    if any(s in state for s in ('settled', 'resolved', 'closed')):
        return True
    if any(s in status for s in ('settled', 'resolved')):
        return True
    if closed and state != 'market_state_active':
        return True
    return False


def get_winning_outcome_index(market: dict) -> int | None:
    """
    Determine which outcome index won (0 or 1).

    PM US binary markets have two outcomes. On settlement, one pays out 100c
    and the other pays 0.  We look at outcomePrices: the winning side goes
    to 1.0 (or 100) and the losing side goes to 0.

    Returns 0, 1, or None if we can't determine.
    """
    # Direct winning outcome field (if PM provides it)
    wo = market.get('winningOutcome')
    if wo is not None:
        try:
            return int(wo)
        except (ValueError, TypeError):
            pass

    ro = market.get('resolvedOutcome')
    if ro is not None:
        try:
            return int(ro)
        except (ValueError, TypeError):
            pass

    # Infer from outcomePrices — the winner is the one at 1.0 (or near it)
    prices = market.get('outcomePrices', [])
    if len(prices) >= 2:
        try:
            p0 = float(prices[0])
            p1 = float(prices[1])
            if p0 > 0.9 and p1 < 0.1:
                return 0
            if p1 > 0.9 and p0 < 0.1:
                return 1
        except (ValueError, TypeError):
            pass

    return None


# ── P&L calculation ──────────────────────────────────────────────────────

def calculate_settlement_pnl(trade: dict, winning_outcome_index: int) -> float:
    """
    Calculate the realized P&L in dollars for the PM leg of an unhedged trade.

    Parameters
    ----------
    trade : dict
        A trade entry from trades.json.
    winning_outcome_index : int
        0 or 1 — which outcome won on PM.

    Returns
    -------
    float  P&L in dollars (positive = profit, negative = loss).
    """
    direction = trade['direction']
    pm_price_raw = trade['pm_price']
    qty = trade.get('contracts_filled', 0) or trade.get('contracts_intended', 0) or 1
    pm_outcome_index = trade.get('pm_outcome_index', 0)

    # pm_price is stored as a decimal (e.g., 0.694 = 69.4 cents)
    # or sometimes as cents already (> 1).  Normalise to cents.
    if pm_price_raw < 1:
        pm_price_cents = pm_price_raw * 100
    else:
        pm_price_cents = pm_price_raw

    # Did our team's outcome win?
    team_won = (winning_outcome_index == pm_outcome_index)

    if direction == 'BUY_PM_SELL_K':
        # Long PM on our team
        if team_won:
            pnl_cents = (100 - pm_price_cents) * qty
        else:
            pnl_cents = -pm_price_cents * qty
    elif direction == 'BUY_K_SELL_PM':
        # Short PM on our team
        if team_won:
            # Team won → our short loses
            pnl_cents = -(100 - pm_price_cents) * qty
        else:
            # Team lost → our short profits
            pnl_cents = pm_price_cents * qty
    else:
        return 0.0

    return round(pnl_cents / 100, 4)


# ── Main ─────────────────────────────────────────────────────────────────

async def main():
    if not PM_US_API_KEY or not PM_US_SECRET_KEY:
        print('[ERROR] Missing PM_US_API_KEY / PM_US_SECRET_KEY in environment')
        sys.exit(1)

    private_key = _make_private_key(PM_US_SECRET_KEY)

    # Load trades
    if not os.path.exists(TRADES_FILE):
        print(f'[ERROR] {TRADES_FILE} not found')
        sys.exit(1)

    with open(TRADES_FILE, 'r') as f:
        trades = json.load(f)

    # Find open positions that need settlement checking
    open_trades = []
    for i, t in enumerate(trades):
        # Skip trades that already have settlement_pnl
        if t.get('settlement_pnl') is not None:
            continue
        # Skip trades with no PM fill
        if (t.get('contracts_filled') or 0) == 0:
            continue
        # Check if this is an open position
        status = t.get('status', '')
        tier = t.get('tier', '')
        if status in OPEN_STATUSES or tier in OPEN_TIERS:
            open_trades.append((i, t))

    if not open_trades:
        print(f'[{datetime.now().isoformat()}] No open positions to check')
        return

    print(f'[{datetime.now().isoformat()}] Checking {len(open_trades)} open position(s)...')

    # De-duplicate slugs (multiple trades may share a market)
    slugs_to_check = list({t['pm_slug'] for _, t in open_trades if t.get('pm_slug')})
    print(f'  Unique markets: {len(slugs_to_check)}')

    # Fetch market data
    settled_markets: dict[str, int] = {}  # slug → winning_outcome_index
    async with aiohttp.ClientSession() as session:
        for slug in slugs_to_check:
            market = await fetch_market(session, private_key, PM_US_API_KEY, slug)
            if market is None:
                print(f'  [{slug}] Could not fetch market data — skipping')
                continue

            if not is_settled(market):
                print(f'  [{slug}] Not settled yet — skipping')
                continue

            winner = get_winning_outcome_index(market)
            if winner is None:
                print(f'  [{slug}] Settled but cannot determine winner — skipping')
                # Dump what we got for debugging
                print(f'    Raw: state={market.get("state")} status={market.get("status")} '
                      f'prices={market.get("outcomePrices")} '
                      f'winner={market.get("winningOutcome")} '
                      f'resolved={market.get("resolvedOutcome")}')
                continue

            settled_markets[slug] = winner
            outcomes = market.get('outcomes', ['outcome0', 'outcome1'])
            winner_name = outcomes[winner] if winner < len(outcomes) else f'outcome[{winner}]'
            print(f'  [{slug}] SETTLED — winner: {winner_name} (index {winner})')

    if not settled_markets:
        print('  No newly settled markets found')
        return

    # Update trades
    updated_count = 0
    for idx, trade in open_trades:
        slug = trade.get('pm_slug', '')
        if slug not in settled_markets:
            continue

        winning_outcome = settled_markets[slug]
        pnl = calculate_settlement_pnl(trade, winning_outcome)

        trades[idx]['settlement_pnl'] = pnl
        trades[idx]['settlement_time'] = datetime.now(timezone.utc).isoformat()
        trades[idx]['settlement_winner_index'] = winning_outcome

        team = trade.get('team', '?')
        direction = trade.get('direction', '?')
        qty = trade.get('contracts_filled', 0)
        pm_price = trade.get('pm_price', 0)
        pm_oi = trade.get('pm_outcome_index', 0)
        team_won = (winning_outcome == pm_oi)

        print(f'  SETTLED: {team} ({direction}) {qty}x @ {pm_price} | '
              f'team {"WON" if team_won else "LOST"} | P&L: ${pnl:+.4f}')
        updated_count += 1

    if updated_count > 0:
        # Write back
        with open(TRADES_FILE, 'w') as f:
            json.dump(trades, f, indent=2)
        print(f'\n  Updated {updated_count} trade(s) in {TRADES_FILE}')
    else:
        print('  No trades updated')


if __name__ == '__main__':
    asyncio.run(main())
