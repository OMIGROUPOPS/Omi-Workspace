#!/usr/bin/env python3
"""
settle_positions.py - Check settlement status of open PM positions and update trades.json.

Reads UNHEDGED / TIER3A_HOLD / TIER3B_FLIP trades from trades.json, queries
the PM US SDK for market settlement, and writes back the realized P&L as
`settlement_pnl` (in dollars).

Run manually:   python settle_positions.py
Run on cron:     */30 * * * * cd /path/to/arb-executor && python settle_positions.py >> logs/settle.log 2>&1

Settlement detection (in priority order):
  1. SDK: client.markets.settlement(slug)
     Returns {"slug": "...", "settlement": 1}  (1 = YES won, 0 = NO won)
     If the endpoint errors or returns no data → market not settled yet.

  2. Fallback: client.markets.book(slug)
     If state == "MARKET_STATE_EXPIRED" AND stats.settlementPx exists:
       settlementPx.value == "1.000" → YES won (settlement=1)
       settlementPx.value == "0.000" → NO won  (settlement=0)

P&L logic (settlement value: 1 = YES/long won, 0 = NO/short won):

  settlement == 1 (YES won):
    BUY_PM_SELL_K (we're long PM YES): WIN  → pnl = (100 - pm_price) * qty / 100
    BUY_K_SELL_PM (we're short PM YES): LOSE → pnl = -(100 - pm_price) * qty / 100

  settlement == 0 (NO won):
    BUY_PM_SELL_K (we're long PM YES): LOSE → pnl = -pm_price * qty / 100
    BUY_K_SELL_PM (we're short PM YES): WIN  → pnl = pm_price * qty / 100

NOTE: This only calculates the PM leg P&L.  The Kalshi leg settled separately
(Kalshi auto-settles).  For UNHEDGED trades, there IS no Kalshi hedge — the
entire P&L is the PM leg.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# ── Load .env ────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

PM_US_API_KEY = os.getenv('PM_US_API_KEY')
PM_US_SECRET_KEY = os.getenv('PM_US_SECRET_KEY')
TRADES_FILE = os.path.join(os.path.dirname(__file__), 'trades.json')

# Statuses that represent open (unsettled) positions on the PM side
OPEN_STATUSES = {'UNHEDGED'}
OPEN_TIERS = {'TIER3A_HOLD', 'TIER3B_FLIP'}

# ── SDK import ────────────────────────────────────────────────────────────
try:
    from polymarket_us import AsyncPolymarketUS
    HAS_PM_SDK = True
except ImportError:
    HAS_PM_SDK = False


# ── Settlement check via SDK ──────────────────────────────────────────────

async def check_settlement_sdk(client, slug: str) -> int | None:
    """
    Check settlement via client.markets.settlement(slug).

    Returns 1 (YES won), 0 (NO won), or None (not settled / error).
    """
    try:
        resp = await client.markets.settlement(slug)
        # resp: {"slug": "...", "settlement": 1} or {"slug": "...", "settlement": 0}
        settlement = resp.get('settlement')
        if settlement is not None:
            return int(settlement)
    except Exception as e:
        # Not settled yet, or endpoint doesn't exist for this market
        print(f'    [SDK settlement] {slug}: {type(e).__name__}: {e}')
    return None


async def check_settlement_book(client, slug: str) -> int | None:
    """
    Fallback: check settlement via book endpoint.

    If state == "MARKET_STATE_EXPIRED" and stats.settlementPx exists:
      settlementPx.value == "1.000" → YES won (return 1)
      settlementPx.value == "0.000" → NO won  (return 0)
    """
    try:
        resp = await client.markets.book(slug)
        md = resp.get('marketData', {})
        state = md.get('state', '')

        if state != 'MARKET_STATE_EXPIRED':
            return None

        stats = md.get('stats', {})
        settlement_px = stats.get('settlementPx')
        if settlement_px is None:
            return None

        value = settlement_px.get('value', '')
        if value == '1.000' or value == '1':
            return 1
        if value == '0.000' or value == '0':
            return 0

        # Try float comparison as fallback
        try:
            fval = float(value)
            if fval > 0.9:
                return 1
            if fval < 0.1:
                return 0
        except (ValueError, TypeError):
            pass

        print(f'    [book fallback] {slug}: EXPIRED but settlementPx={value} — cannot determine')
    except Exception as e:
        print(f'    [book fallback] {slug}: {type(e).__name__}: {e}')
    return None


# ── P&L calculation ──────────────────────────────────────────────────────

def calculate_settlement_pnl(trade: dict, settlement: int) -> float:
    """
    Calculate the realized P&L in dollars for the PM leg.

    Parameters
    ----------
    trade : dict
        A trade entry from trades.json.
    settlement : int
        1 = YES/long side won, 0 = NO/short side won.

    Returns
    -------
    float  P&L in dollars (positive = profit, negative = loss).
    """
    direction = trade['direction']
    pm_price_raw = trade['pm_price']
    qty = trade.get('contracts_filled', 0) or trade.get('contracts_intended', 0) or 1

    # pm_price is stored as a decimal (e.g., 0.694 = 69.4 cents)
    # or sometimes as cents already (> 1).  Normalise to cents.
    if pm_price_raw < 1:
        pm_price_cents = pm_price_raw * 100
    else:
        pm_price_cents = pm_price_raw

    if settlement == 1:
        # YES won
        if direction == 'BUY_PM_SELL_K':
            # We're long PM YES → we WIN
            pnl_cents = (100 - pm_price_cents) * qty
        elif direction == 'BUY_K_SELL_PM':
            # We're short PM YES → we LOSE
            pnl_cents = -(100 - pm_price_cents) * qty
        else:
            return 0.0
    elif settlement == 0:
        # NO won
        if direction == 'BUY_PM_SELL_K':
            # We're long PM YES → we LOSE
            pnl_cents = -pm_price_cents * qty
        elif direction == 'BUY_K_SELL_PM':
            # We're short PM YES → we WIN
            pnl_cents = pm_price_cents * qty
        else:
            return 0.0
    else:
        return 0.0

    return round(pnl_cents / 100, 4)


# ── Main ─────────────────────────────────────────────────────────────────

async def main():
    if not PM_US_API_KEY or not PM_US_SECRET_KEY:
        print('[ERROR] Missing PM_US_API_KEY / PM_US_SECRET_KEY in environment')
        sys.exit(1)

    if not HAS_PM_SDK:
        print('[ERROR] polymarket_us SDK not installed — run: pip install polymarket-us')
        sys.exit(1)

    # Initialize SDK client (same pattern as arb_executor_v7.py)
    client = AsyncPolymarketUS(
        key_id=PM_US_API_KEY,
        secret_key=PM_US_SECRET_KEY,
    )

    try:
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

        # Check settlement for each market
        settled_markets: dict[str, int] = {}  # slug → settlement (1=YES won, 0=NO won)

        for slug in slugs_to_check:
            # Primary: SDK settlement endpoint
            result = await check_settlement_sdk(client, slug)

            # Fallback: book endpoint with settlementPx
            if result is None:
                result = await check_settlement_book(client, slug)

            if result is None:
                print(f'  [{slug}] Not settled yet — skipping')
                continue

            settled_markets[slug] = result
            winner_label = 'YES' if result == 1 else 'NO'
            print(f'  [{slug}] SETTLED — winner: {winner_label} (settlement={result})')

        if not settled_markets:
            print('  No newly settled markets found')
            return

        # Update trades
        updated_count = 0
        for idx, trade in open_trades:
            slug = trade.get('pm_slug', '')
            if slug not in settled_markets:
                continue

            settlement = settled_markets[slug]
            pnl = calculate_settlement_pnl(trade, settlement)

            trades[idx]['settlement_pnl'] = pnl
            trades[idx]['settlement_time'] = datetime.now(timezone.utc).isoformat()
            trades[idx]['settlement_winner_index'] = settlement

            team = trade.get('team', '?')
            direction = trade.get('direction', '?')
            qty = trade.get('contracts_filled', 0)
            pm_price = trade.get('pm_price', 0)

            yes_won = (settlement == 1)
            if direction == 'BUY_PM_SELL_K':
                we_won = yes_won
            else:
                we_won = not yes_won

            print(f'  SETTLED: {team} ({direction}) {qty}x @ {pm_price} | '
                  f'YES {"WON" if yes_won else "LOST"} | we {"WIN" if we_won else "LOSE"} | P&L: ${pnl:+.4f}')
            updated_count += 1

        if updated_count > 0:
            # Write back
            with open(TRADES_FILE, 'w') as f:
                json.dump(trades, f, indent=2)
            print(f'\n  Updated {updated_count} trade(s) in {TRADES_FILE}')
        else:
            print('  No trades updated')

    finally:
        await client.close()


if __name__ == '__main__':
    asyncio.run(main())
