#!/usr/bin/env python3
"""
settle_positions.py - Check settlement status of positions and update trades.json.

Handles THREE trade types:

  1. UNHEDGED / TIER3A_HOLD — directional (PM-only) positions.
     P&L depends on which side won (see calculate_settlement_pnl).

  2. SUCCESS / TIER1_HEDGE — hedged positions (both legs filled).
     Spread was locked at trade time.  Settlement just confirms the market
     resolved and cash returned.  Net P&L = spread_cents * qty / 100 - fees.

  3. EXITED (TIER2_EXIT / TIER3_UNWIND) — position closed via PM unwind.
     No market settlement needed.  P&L = -(unwind_loss_cents / 100).

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
"""
import asyncio
import json
import math
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

# Statuses/tiers that represent DIRECTIONAL (unhedged) positions
DIRECTIONAL_STATUSES = {'UNHEDGED'}
DIRECTIONAL_TIERS = {'TIER3A_HOLD'}

# Statuses/tiers that represent HEDGED positions (both legs filled)
HEDGED_STATUSES = {'SUCCESS'}
HEDGED_TIERS = {'TIER1_HEDGE'}

# Opposite-side hedge tiers (cross-platform: PM team A + K team B)
OPPOSITE_HEDGE_TIERS = {'TIER3_OPPOSITE_HEDGE', 'TIER3_OPPOSITE_OVERWEIGHT'}

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


def calculate_hedged_settlement_pnl(trade: dict) -> float:
    """
    Calculate the realized net P&L for a HEDGED (SUCCESS) trade.

    The spread was locked at execution.  Both legs settle to $1 or $0 each,
    so regardless of outcome the gross profit is spread_cents * qty.
    We subtract fees to get net.

    Returns P&L in dollars.
    """
    spread_cents = trade.get('spread_cents', 0) or 0
    qty = trade.get('contracts_filled', 0) or trade.get('contracts_intended', 0) or 1

    gross_dollars = spread_cents * qty / 100

    # Use recorded fees if available, otherwise estimate
    pm_fee = trade.get('pm_fee', 0) or 0
    k_fee = trade.get('k_fee', 0)
    if k_fee is None:
        # Estimate Kalshi fee: ceil(7% * p * (1-p) * 100) / 100 * qty
        k_price = trade.get('k_price', 50)
        if k_price and k_price > 0:
            p = k_price / 100.0
            k_fee = math.ceil(0.07 * p * (1 - p) * 100) / 100 * qty
        else:
            k_fee = 0

    net_dollars = gross_dollars - pm_fee - k_fee
    return round(net_dollars, 4)


def calculate_opposite_hedge_settlement_pnl(trade: dict) -> float:
    """
    Calculate the realized P&L for an opposite-side hedge trade.

    Cross-platform arb: PM long Team A + K long Team B.
    Exactly one team wins, so one leg always pays 100c.
    P&L = (100 - combined_cost) * qty / 100, same regardless of winner.
    """
    combined = trade.get('combined_cost_cents')
    if combined is None:
        pm_raw = trade.get('pm_price', 0)
        pm_c = pm_raw * 100 if pm_raw < 1 else pm_raw
        combined = pm_c + trade.get('opposite_hedge_price', 0)
    qty = trade.get('contracts_filled', 0) or 1
    pnl_cents = (100 - combined) * qty
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

        # ── Collect unsettled trades ──
        directional_trades = []   # UNHEDGED / TIER3A
        hedged_trades = []        # SUCCESS / TIER1_HEDGE
        exited_trades = []        # EXITED (position closed via unwind)
        opposite_hedge_trades = []  # TIER3_OPPOSITE_HEDGE / TIER3_OPPOSITE_OVERWEIGHT

        for i, t in enumerate(trades):
            if t.get('settlement_pnl') is not None:
                continue
            status = t.get('status', '')
            tier = t.get('tier', '')
            # EXITED trades don't need contracts_filled > 0 (position was unwound)
            if status == 'EXITED':
                exited_trades.append((i, t))
                continue
            if (t.get('contracts_filled') or 0) == 0:
                continue
            if tier in OPPOSITE_HEDGE_TIERS:
                opposite_hedge_trades.append((i, t))
            elif status in DIRECTIONAL_STATUSES or tier in DIRECTIONAL_TIERS:
                directional_trades.append((i, t))
            elif status in HEDGED_STATUSES or tier in HEDGED_TIERS:
                hedged_trades.append((i, t))

        total_unsettled = len(directional_trades) + len(hedged_trades) + len(exited_trades) + len(opposite_hedge_trades)
        if total_unsettled == 0:
            print(f'[{datetime.now().isoformat()}] No unsettled trades to check')
            return

        print(f'[{datetime.now().isoformat()}] Checking {total_unsettled} unsettled trade(s) '
              f'({len(directional_trades)} directional, {len(hedged_trades)} hedged, '
              f'{len(exited_trades)} exited, {len(opposite_hedge_trades)} opposite-hedge)...')

        # ── Settlement check for directional + hedged trades ──
        settled_markets: dict[str, int] = {}
        dir_count = 0
        hedged_count = 0

        if directional_trades or hedged_trades or opposite_hedge_trades:
            all_market_trades = directional_trades + hedged_trades + opposite_hedge_trades
            slugs_to_check = list({t['pm_slug'] for _, t in all_market_trades if t.get('pm_slug')})
            print(f'  Unique markets to check: {len(slugs_to_check)}')

            for slug in slugs_to_check:
                result = await check_settlement_sdk(client, slug)
                if result is None:
                    result = await check_settlement_book(client, slug)
                if result is None:
                    print(f'  [{slug}] Not settled yet — skipping')
                    continue
                settled_markets[slug] = result
                winner_label = 'YES' if result == 1 else 'NO'
                print(f'  [{slug}] SETTLED — winner: {winner_label} (settlement={result})')

            if not settled_markets and not exited_trades:
                print('  No newly settled markets found')
                return

        # ── Update DIRECTIONAL trades (UNHEDGED / TIER3) ──
        for idx, trade in directional_trades:
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
            we_won = yes_won if direction == 'BUY_PM_SELL_K' else not yes_won

            print(f'  [DIR] {team} ({direction}) {qty}x @ {pm_price} | '
                  f'YES {"WON" if yes_won else "LOST"} | we {"WIN" if we_won else "LOSE"} | P&L: ${pnl:+.4f}')
            dir_count += 1

        # ── Update HEDGED trades (SUCCESS / TIER1_HEDGE) ──
        for idx, trade in hedged_trades:
            slug = trade.get('pm_slug', '')
            if slug not in settled_markets:
                continue

            settlement = settled_markets[slug]
            pnl = calculate_hedged_settlement_pnl(trade)

            trades[idx]['settlement_pnl'] = pnl
            trades[idx]['settlement_time'] = datetime.now(timezone.utc).isoformat()
            trades[idx]['settlement_winner_index'] = settlement

            team = trade.get('team', '?')
            qty = trade.get('contracts_filled', 0)
            spread = trade.get('spread_cents', 0)

            print(f'  [HEDGED] {team} {qty}x | spread={spread}c | net P&L: ${pnl:+.4f}')
            hedged_count += 1

        # ── Update EXITED trades (position closed via unwind — no market settlement needed) ──
        exited_count = 0
        for idx, trade in exited_trades:
            ulc = trade.get('unwind_loss_cents')
            if ulc is None:
                ulc = 0
            settlement_pnl = round(-ulc / 100, 4)

            trades[idx]['settlement_pnl'] = settlement_pnl
            trades[idx]['settlement_time'] = trade.get('timestamp', datetime.now(timezone.utc).isoformat())
            trades[idx]['settlement_source'] = 'unwind'

            team = trade.get('team', '?')
            tier = trade.get('tier', '')
            qty = trade.get('contracts_filled', 0) or trade.get('pm_fill', 0)

            print(f'  [EXITED] {team} ({tier}) {qty}x | unwind_loss={ulc}c | P&L: ${settlement_pnl:+.4f}')
            exited_count += 1

        # ── Update OPPOSITE HEDGE trades (cross-platform arb — P&L is deterministic) ──
        opp_count = 0
        for idx, trade in opposite_hedge_trades:
            slug = trade.get('pm_slug', '')
            if slug not in settled_markets:
                continue

            settlement = settled_markets[slug]
            pnl = calculate_opposite_hedge_settlement_pnl(trade)

            trades[idx]['settlement_pnl'] = pnl
            trades[idx]['settlement_time'] = datetime.now(timezone.utc).isoformat()
            trades[idx]['settlement_winner_index'] = settlement

            team = trade.get('team', '?')
            tier = trade.get('tier', '')
            qty = trade.get('contracts_filled', 0)
            combined = trade.get('combined_cost_cents', 0)

            print(f'  [OPP_HEDGE] {team} ({tier}) {qty}x | combined={combined:.0f}c | P&L: ${pnl:+.4f}')
            opp_count += 1

        total_updated = dir_count + hedged_count + exited_count + opp_count
        if total_updated > 0:
            with open(TRADES_FILE, 'w') as f:
                json.dump(trades, f, indent=2)
            print(f'\n  Updated {total_updated} trade(s) in {TRADES_FILE} '
                  f'({dir_count} directional, {hedged_count} hedged, {exited_count} exited, '
                  f'{opp_count} opposite-hedge)')
        else:
            print('  No trades updated')

    finally:
        await client.close()


if __name__ == '__main__':
    asyncio.run(main())
