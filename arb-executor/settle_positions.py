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
import aiohttp
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
    Calculate the realized P&L in dollars for the PM leg (directional trades).

    Uses the actual outcome index traded and whether the position was
    BUY_LONG (bought YES) or BUY_SHORT (sold YES) to determine P&L.

    Settlement mapping:
        settlement=1 → outcome index 0 won
        settlement=0 → outcome index 1 won

    Parameters
    ----------
    trade : dict
        A trade entry from trades.json.
    settlement : int
        1 = outcome 0 won, 0 = outcome 1 won.

    Returns
    -------
    float  P&L in dollars (positive = profit, negative = loss).
    """
    pm_price_raw = trade['pm_price']
    qty = trade.get('contracts_filled', 0) or trade.get('contracts_intended', 0) or 1

    # pm_price is stored as cents (e.g., 69.4) or rarely as a decimal (< 1).
    if pm_price_raw < 1:
        pm_price_cents = pm_price_raw * 100
    else:
        pm_price_cents = pm_price_raw

    # Determine which outcome index we traded on
    actual_oi = trade.get('pm_outcome_index_used')
    if actual_oi is None:
        actual_oi = trade.get('pm_outcome_index')
    if actual_oi is None:
        print(f'    [WARN] No pm_outcome_index for trade — cannot compute P&L')
        return 0.0

    is_buy_short = trade.get('pm_is_buy_short', False)

    # Which outcome won?
    winning_outcome = 0 if settlement == 1 else 1
    our_outcome_won = (actual_oi == winning_outcome)

    if not is_buy_short:
        # BUY_LONG: we bought YES on our outcome
        # Won: payout 100c, paid pm_price → profit = (100 - pm_price) per contract
        # Lost: YES = 0, we lose our cost → loss = -pm_price per contract
        if our_outcome_won:
            pnl_cents = (100 - pm_price_cents) * qty
        else:
            pnl_cents = -pm_price_cents * qty
    else:
        # BUY_SHORT: we sold YES on our outcome (received pm_price proceeds)
        # Won: YES = 100c, we owe 100 → loss = -(100 - pm_price) per contract
        # Lost: YES = 0, we owe nothing → profit = pm_price per contract
        if our_outcome_won:
            pnl_cents = -(100 - pm_price_cents) * qty
        else:
            pnl_cents = pm_price_cents * qty

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


def compute_exited_pnl(trade: dict) -> float:
    """
    Compute P&L for an EXITED trade using 3-priority cascade:
      1. unwind_pnl_cents (signed, new field) → divide by 100
      2. Recompute from unwind_fill_price + pm_price + direction
      3. Fall back to -abs(unwind_loss_cents) / 100 (old unsigned field, always loss)
    Returns P&L in dollars.
    """
    qty = trade.get('contracts_filled', 0) or trade.get('contracts_intended', 0) or 0

    # Priority 1: signed unwind_pnl_cents
    upc = trade.get('unwind_pnl_cents')
    if upc is not None:
        return round(upc / 100, 4)

    # Priority 2: recompute from fill price
    ufp = trade.get('unwind_fill_price')
    pm_raw = trade.get('pm_price', 0)
    pm_cents = pm_raw * 100 if (isinstance(pm_raw, (int, float)) and pm_raw < 1 and pm_raw > 0) else pm_raw
    if ufp is not None and pm_cents > 0 and qty > 0:
        direction = trade.get('direction', '')
        if direction == 'BUY_PM_SELL_K':
            # We bought YES, unwind = sell YES. Profit = sell - buy
            pnl_cents = ((ufp * 100) - pm_cents) * qty
        else:
            # We sold YES (BUY_SHORT), unwind = buy back. Profit = original_sell - buyback
            pnl_cents = (pm_cents - (ufp * 100)) * qty
        return round(pnl_cents / 100, 4)

    # Priority 3: old unsigned field (always treated as loss)
    ulc = trade.get('unwind_loss_cents')
    if ulc is not None and ulc != 0:
        return round(-abs(ulc) / 100, 4)

    return 0.0


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
            settlement_pnl = compute_exited_pnl(trade)

            trades[idx]['settlement_pnl'] = settlement_pnl
            trades[idx]['settlement_time'] = trade.get('timestamp', datetime.now(timezone.utc).isoformat())
            trades[idx]['settlement_source'] = 'unwind'

            team = trade.get('team', '?')
            tier = trade.get('tier', '')
            qty = trade.get('contracts_filled', 0) or trade.get('pm_fill', 0)

            upc = trade.get('unwind_pnl_cents')
            ulc = trade.get('unwind_loss_cents')
            src = 'upc' if upc is not None else ('recomp' if trade.get('unwind_fill_price') else 'ulc')
            print(f'  [EXITED] {team} ({tier}) {qty}x | upc={upc} ulc={ulc} | src={src} | P&L: ${settlement_pnl:+.4f}')
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

        # ── Kalshi reconciliation: replace settlement_pnl with ground truth ──
        reconciled_count = 0
        try:
            from kalshi_reconciler import (
                get_fills_and_settlements, get_fill_cost_by_ticker,
                get_settlement_by_ticker, compute_kalshi_pnl,
            )
            print('\n  Running Kalshi reconciliation...')
            fills, settlements = await get_fills_and_settlements()
            fill_map = get_fill_cost_by_ticker(fills)
            settle_map = get_settlement_by_ticker(settlements)

            for idx, t in enumerate(trades):
                # Only reconcile trades with settlement_pnl that haven't been reconciled yet
                if t.get('settlement_pnl') is None:
                    continue
                if t.get('settlement_source') == 'kalshi_reconciled':
                    continue
                # Skip EXITED trades (no Kalshi fill to reconcile against)
                if t.get('status') == 'EXITED' or t.get('settlement_source') == 'unwind':
                    continue

                ticker = t.get('kalshi_ticker', '')
                if not ticker:
                    continue

                k_fill = fill_map.get(ticker)
                k_settle = settle_map.get(ticker)
                if not k_fill or not k_settle:
                    continue

                # Kalshi-side P&L
                k_pnl = compute_kalshi_pnl(k_fill, k_settle)

                # PM-side P&L from settlement outcome
                pm_raw = t.get('pm_price', 0)
                pm_cents = pm_raw * 100 if (isinstance(pm_raw, (int, float)) and pm_raw < 1 and pm_raw > 0) else pm_raw
                is_short = t.get('pm_is_buy_short')
                if is_short is None:
                    # Infer from direction: BUY_K_SELL_PM → PM is sell (short)
                    is_short = 'SELL_PM' in t.get('direction', '')
                qty = t.get('contracts_filled', 0) or 1
                pm_fee = t.get('pm_fee', 0) or 0

                # Use settlement result directly for PM P&L
                # (don't invert k_won — both legs can be same direction)
                result = k_settle['result']  # 'yes' or 'no'

                if not is_short:
                    # Bought YES on PM → wins if result=yes
                    if result == 'yes':
                        pm_pnl = (100 - pm_cents) * qty / 100
                    else:
                        pm_pnl = -pm_cents * qty / 100
                else:
                    # Sold YES on PM (short) → wins if result=no
                    if result == 'no':
                        pm_pnl = pm_cents * qty / 100
                    else:
                        pm_pnl = -(100 - pm_cents) * qty / 100

                pm_pnl -= pm_fee  # subtract PM fee

                old_pnl = t.get('settlement_pnl')
                new_pnl = round(k_pnl + pm_pnl, 4)

                trades[idx]['settlement_pnl'] = new_pnl
                trades[idx]['settlement_source'] = 'kalshi_reconciled'
                trades[idx]['k_actual_cost'] = k_fill['net_cost_cents']
                trades[idx]['k_actual_fee'] = round(k_fill['fee_dollars'] + k_settle['fee_dollars'], 4)

                team = t.get('team', '?')
                if abs((old_pnl or 0) - new_pnl) > 0.0001:
                    print(f'  [RECONCILED] {team}: ${old_pnl:+.4f} → ${new_pnl:+.4f} '
                          f'(K: ${k_pnl:+.4f}, PM: ${pm_pnl:+.4f})')
                reconciled_count += 1

            if reconciled_count:
                print(f'  Reconciled {reconciled_count} trade(s) against Kalshi API')
        except ImportError:
            print('  [WARN] kalshi_reconciler not available — skipping reconciliation')
        except Exception as e:
            print(f'  [WARN] Kalshi reconciliation failed: {e}')

        total_updated += reconciled_count
        if total_updated > 0:
            with open(TRADES_FILE, 'w') as f:
                json.dump(trades, f, indent=2)
            print(f'\n  Updated {total_updated} trade(s) in {TRADES_FILE} '
                  f'({dir_count} directional, {hedged_count} hedged, {exited_count} exited, '
                  f'{opp_count} opposite-hedge, {reconciled_count} reconciled)')
        else:
            print('  No trades updated')

    finally:
        await client.close()


if __name__ == '__main__':
    asyncio.run(main())
