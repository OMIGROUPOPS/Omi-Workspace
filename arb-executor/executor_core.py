#!/usr/bin/env python3
"""
executor_core.py - Clean execution engine for arb trades.

Given: a fully resolved arb opportunity with all prices and mappings
Does: places hedged orders on Kalshi and PM, or safely aborts

4 possible trades (K and PM always YES opposite teams):
  1. BUY_PM_SELL_K, team IS pm_long_team  -> K: YES opponent, PM: YES team (intent=1)
  2. BUY_PM_SELL_K, team NOT pm_long_team -> K: YES opponent, PM: YES team (intent=3)
  3. BUY_K_SELL_PM, team IS pm_long_team  -> K: YES team,     PM: YES opponent (intent=3)
  4. BUY_K_SELL_PM, team NOT pm_long_team -> K: YES team,     PM: YES opponent (intent=1)

EXECUTION ORDER: PM FIRST, THEN KALSHI
  - PM is the unreliable leg (IOC orders often expire due to latency)
  - Kalshi is the reliable leg (fills consistently)
  - If PM doesn't fill, we exit cleanly with no position
  - If PM fills but Kalshi doesn't, we have an unhedged position (rare)

Safety guarantees:
  - In-memory position check before ordering (no API calls on hot path)
  - PM first (unreliable), Kalshi only if PM fills (reliable)
  - Dynamic sizing via depth-aware algorithm (defaults to 1 if no depth data)
  - Phantom spread rejection (>90c)
  - All 4 trade cases handled explicitly via TRADE_PARAMS lookup
  - pm_long_team verified at WS level (price mismatch check on first update)
  - Partial hedge handling (unwinds excess PM if K partially fills)
"""
import asyncio
import json
import math
import os
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Set, Tuple, Optional, Any

from config import Config
from pregame_mapper import TEAM_FULL_NAMES  # Kalshi abbrev → full name for OMI lookups

# Path for persisting traded games across restarts
TRADED_GAMES_FILE = os.path.join(os.path.dirname(__file__), "traded_games.json")
DIRECTIONAL_POSITIONS_FILE = os.path.join(os.path.dirname(__file__), "directional_positions.json")
KALSHI_ERRORS_LOG = os.path.join(os.path.dirname(__file__), "kalshi_errors.log")

# =============================================================================
# PM_LONG_TEAM ABBREVIATION MAPPINGS
# =============================================================================
# Map PM displayAbbreviation to Kalshi abbreviation for pm_long_team verification
PM_DISPLAY_TO_KALSHI = {
    # NBA
    "atl": "ATL", "bos": "BOS", "bkn": "BKN", "cha": "CHA", "chi": "CHI",
    "cle": "CLE", "dal": "DAL", "den": "DEN", "det": "DET", "gsw": "GSW",
    "hou": "HOU", "ind": "IND", "lac": "LAC", "lal": "LAL", "mem": "MEM",
    "mia": "MIA", "mil": "MIL", "min": "MIN", "nop": "NOP", "nyk": "NYK",
    "okc": "OKC", "orl": "ORL", "phi": "PHI", "phx": "PHX", "por": "POR",
    "sac": "SAC", "sas": "SAS", "tor": "TOR", "uta": "UTA", "was": "WAS",
    # CBB common
    "unco": "UNCO", "ncol": "UNCO",  # Northern Colorado
    "idst": "IDST", "idhst": "IDST",  # Idaho State
    "chat": "CHAT", "cita": "CIT",  # Chattanooga, Citadel
}


# =============================================================================
# PM_LONG_TEAM VERIFICATION — now handled at two earlier stages:
#   1. pregame_mapper.py: price sanity check during mapping (Kalshi vs PM bestBid)
#   2. arb_executor_ws.py: runtime check in _handle_market_data() on first WS update
# No per-trade API verification needed — eliminated for latency.

# =============================================================================
# TRADE PARAMETERS - EXPLICIT MAPPING FOR ALL 4 CASES
# =============================================================================
# Key: (direction, is_long_team)
# - direction: 'BUY_PM_SELL_K' or 'BUY_K_SELL_PM'
# - is_long_team: True if our team == pm_long_team
#
# PM US API intents:
# - intent=1 (BUY_LONG): Buy the pm_long_team (favorite)
# - intent=3 (BUY_SHORT): Buy the underdog (non-long team)
#
# IMPORTANT: intent=3 price uses direct underdog price (not inverted)
# Underdog ask = 100 - pm_long_team_bid

# Reverse intent mapping for unwinding PM positions:
# BUY_LONG(1) ↔ SELL_LONG(2), BUY_SHORT(3) ↔ SELL_SHORT(4)
REVERSE_INTENT = {1: 2, 2: 1, 3: 4, 4: 3}

# Minimum K depth gate - skip trades when Kalshi L1 depth is too thin
# Data: 57% unwind rate when K_L1 < 50, vs 0% when >= 50
MIN_K_DEPTH_L1 = 50


def get_depth_cap(spread_cents: float) -> float:
    """Higher spread = more confidence = take more depth."""
    if spread_cents >= 20: return 0.85
    if spread_cents >= 10: return 0.75
    if spread_cents >= 7:  return 0.65
    if spread_cents >= 5:  return 0.50
    return 0.35  # 4c spreads, just skim


def _get_opposing_team(cache_key: str, team: str) -> str:
    """From cache_key 'sport:TEAMA-TEAMB:date', return the other team."""
    try:
        teams = cache_key.split(':')[1].split('-')
        return teams[1] if teams[0] == team else teams[0]
    except Exception:
        return '?'


def _yes_teams(team: str, k_action: str, cache_key: str):
    """Return (k_yes_team, pm_yes_team) — which team each platform bet YES on.
    In a hedged arb, K and PM always back opposite teams."""
    opp = _get_opposing_team(cache_key, team)
    if k_action == 'buy':
        return team, opp    # K bought YES team, PM bought YES opponent
    else:
        return opp, team    # K sold YES team (=YES opponent), PM bought YES team


def _check_hedge_coherence(team: str, k_fill_price: int, pm_fill_price_dollars: float,
                           k_action: str, is_buy_short: bool, direction: str,
                           pm_long_team: str, is_long_team: bool,
                           cache_key: str = '') -> bool:
    """
    Post-fill sanity check: verify K + PM positions form a valid hedge.

    For a valid arb (opposite sides of same event), combined cost should be
    close to 100c (the guaranteed payout). If combined < 80c or > 110c,
    the positions may be same-side (not a hedge).

    Returns True if coherent (likely valid hedge), False if suspicious.
    """
    pm_fill_cents = pm_fill_price_dollars * 100

    # K cost: buy = fill_price, sell = 100 - fill_price (risk)
    k_cost = k_fill_price if k_action == 'buy' else (100 - k_fill_price)
    # PM cost: BUY_LONG = fill_price, BUY_SHORT = 100 - fill_price (collateral)
    pm_cost = (100 - pm_fill_cents) if is_buy_short else pm_fill_cents

    combined = k_cost + pm_cost

    k_yes, pm_yes = _yes_teams(team, k_action, cache_key) if cache_key else ('?', '?')

    if combined < 80 or combined > 110:
        print(f"[HEDGE_CHECK] WARNING: {team} combined={combined:.0f}c "
              f"(K YES {k_yes} @{k_cost:.0f}c + PM YES {pm_yes} @{pm_cost:.0f}c) | "
              f"Expected ~96-100c for valid arb | dir={direction}",
              flush=True)
        if combined < 80:
            print(f"[HEDGE_CHECK] CRITICAL: combined={combined:.0f}c < 80c — "
                  f"likely SAME-SIDE bet (not a hedge)!", flush=True)
        return False

    # Post-fill combined cost gate: tighter than pre-trade check
    if combined > 102:
        print(f"[COST_GATE] CRITICAL POST-FILL: {team} combined={combined:.0f}c > 102c "
              f"(K YES {k_yes} @{k_cost:.0f}c + PM YES {pm_yes} @{pm_cost:.0f}c) | "
              f"NEGATIVE ARB — will lose {combined - 100:.0f}c at settlement", flush=True)
        return False

    return True

async def _verify_both_legs(session, kalshi_api, pm_api, ticker: str, pm_slug: str,
                            team: str, k_filled: int, pm_filled: int) -> bool:
    """
    Post-fill verification: confirm both legs exist on their platforms via API.
    Pauses executor if either leg is missing. Exception-safe — API errors don't pause.
    Returns True if both legs confirmed, False if verification failed.
    """
    global executor_paused
    try:
        k_pos = await kalshi_api.get_position_for_ticker(session, ticker)
        # get_position_for_ticker returns an int (position count), not an object
        k_exists = k_pos is not None and abs(k_pos) > 0

        pm_positions = await pm_api.get_positions(session, market_slug=pm_slug)
        pm_exists = pm_positions is not None and len(pm_positions) > 0

        if not k_exists or not pm_exists:
            # WARNING ONLY — do NOT pause. Both fills were already confirmed by order
            # responses. Position API may lag behind (especially K SELL YES = short).
            # False positives from API latency are common and were pausing the executor
            # unnecessarily (e.g., LCHI trade: K confirmed fill_count=1 but position
            # API returned 0 within 50ms of fill).
            print(f"[HEDGE_VERIFY] WARN: {team} | "
                  f"K={ticker} {'EXISTS' if k_exists else 'MISSING'} (expected {k_filled}) | "
                  f"PM={pm_slug[:35]} {'EXISTS' if pm_exists else 'MISSING'} (expected {pm_filled}) | "
                  f"NOTE: both fills confirmed by order response — likely API latency",
                  flush=True)
            return False

        print(f"[HEDGE_VERIFY] OK: {team} K={ticker[-15:]} PM={pm_slug[:25]} — both legs confirmed",
              flush=True)
        return True
    except Exception as e:
        print(f"[HEDGE_VERIFY] ERROR checking legs for {team}: {e} — skipping (trade already done)",
              flush=True)
        return True  # Don't pause on API errors


async def post_trade_audit(session, kalshi_api, pm_api, ticker: str, pm_slug: str,
                           team: str, k_filled: int, pm_filled: int,
                           k_price: int, pm_price: float,
                           k_action: str, is_buy_short: bool,
                           cache_key: str = ''):
    """
    Lightweight post-trade audit: verify the new trade's two legs exist on both
    platforms with correct quantities and hedged cost. Runs after every successful
    trade. Exception-safe — API errors log but don't crash or pause.

    Logs [POST_TRADE_AUDIT] CONFIRMED or MISMATCH.
    """
    try:
        # Small delay to let position APIs settle (K SELL can lag ~100ms)
        await asyncio.sleep(1.0)

        # --- Kalshi leg ---
        k_pos = await kalshi_api.get_position_for_ticker(session, ticker)
        k_qty = abs(k_pos) if k_pos else 0
        k_exists = k_qty > 0

        # --- PM leg ---
        pm_positions = await pm_api.get_positions(session, market_slug=pm_slug)
        pm_exists = pm_positions is not None and len(pm_positions) > 0
        pm_qty = 0
        if pm_exists:
            for p in pm_positions:
                net = p.get('netPosition', p.get('net_position', 0))
                if net != 0:
                    pm_qty = abs(net)
                    break

        # --- Combined cost (hedge check) ---
        k_cost = k_price if k_action == 'buy' else (100 - k_price)
        pm_cost = (100 - int(pm_price * 100)) if is_buy_short else int(pm_price * 100)
        combined = k_cost + pm_cost
        hedged = 90 <= combined <= 102

        # --- Build verdict ---
        issues = []
        if not k_exists:
            issues.append(f"K MISSING (expected {k_filled})")
        elif k_qty < k_filled:
            issues.append(f"K QTY {k_qty} < expected {k_filled}")
        if not pm_exists:
            issues.append(f"PM MISSING (expected {pm_filled})")
        elif pm_qty < pm_filled:
            issues.append(f"PM QTY {pm_qty} < expected {pm_filled}")
        if not hedged:
            issues.append(f"COMBINED {combined}c outside 90-102c")

        k_yes, pm_yes = _yes_teams(team, k_action, cache_key) if cache_key else ('?', '?')

        if issues:
            print(f"[POST_TRADE_AUDIT] MISMATCH: {team} | " + " | ".join(issues) +
                  f" | K YES {k_yes} @{k_cost}c PM YES {pm_yes} @{pm_cost}c combined={combined}c",
                  flush=True)
        else:
            print(f"[POST_TRADE_AUDIT] CONFIRMED: {team} | "
                  f"K={k_qty}x YES {k_yes} @{k_price}c | PM={pm_qty}x YES {pm_yes} @{int(pm_price*100)}c | "
                  f"combined={combined}c",
                  flush=True)
    except Exception as e:
        print(f"[POST_TRADE_AUDIT] ERROR: {team} — {e} (trade already done, skipping)",
              flush=True)


TRADE_PARAMS = {
    # ==========================================================================
    # Case 1: BUY_PM_SELL_K, team IS pm_long_team
    # K: SELL YES team (= YES opponent), PM: BUY YES team (favorite)
    # HEDGE: K YES opp + PM YES team = hedged
    # Price: pm_ask = favorite's ask from cache (direct, no inversion)
    # ==========================================================================
    ('BUY_PM_SELL_K', True): {
        'k_action': 'sell',
        'k_side': 'yes',
        'k_price_field': 'k_bid',       # Selling, so use bid
        'pm_intent': 1,                  # BUY_LONG (favorite)
        'pm_price_field': 'pm_ask',     # Pay favorite's ask
        'pm_is_buy_short': False,
        'pm_switch_outcome': False,      # Trade on own outcome (long team)
        'k_result': 'YES_OPP',
        'pm_result': 'YES_TEAM',
        'executable': True,
    },

    # ==========================================================================
    # Case 2: BUY_PM_SELL_K, team is NOT pm_long_team (underdog)
    # K: SELL YES team (= YES opponent), PM: BUY YES team (underdog via BUY_SHORT)
    # HEDGE: K YES opp + PM YES team = hedged
    #
    # BINARY MARKET: PM US SDK DOES accept outcomeIndex (0 or 1).
    # Intent controls direction, outcomeIndex selects which outcome to trade:
    #   BUY_LONG (1) + outcomeIndex = LONG on that outcome
    #   BUY_SHORT (3) + outcomeIndex = SHORT on that outcome
    # For underdog (not pm_long_team), we BUY_SHORT with pm_switch_outcome
    # to target the correct outcome index.
    #
    # Price: pm_ask = underdog's ask from cache (already inverted: 100 - long_bid)
    #        Converted to YES-frame via pm_is_buy_short path:
    #        min_YES_sell = (100 - max_underdog_cost) / 100
    # ==========================================================================
    ('BUY_PM_SELL_K', False): {
        'k_action': 'sell',
        'k_side': 'yes',
        'k_price_field': 'k_bid',       # Selling, so use bid
        'pm_intent': 3,                  # BUY_SHORT (short pm_long_team = long underdog)
        'pm_price_field': 'pm_ask',     # Underdog's ask (cache inverted: 100 - long_bid)
        'pm_is_buy_short': True,
        'pm_switch_outcome': True,       # Settlement: actual_oi = 0 (all binary trades are outcome 0)
        'k_result': 'YES_OPP',
        'pm_result': 'YES_TEAM',
        'executable': True,
    },

    # ==========================================================================
    # Case 3: BUY_K_SELL_PM, team IS pm_long_team
    # K: BUY YES team (favorite), PM: BUY YES opponent (via BUY_SHORT favorite)
    # HEDGE: K YES team + PM YES opp = hedged
    # Price: pm_bid (long team bid) → invert to underdog cost → YES-frame
    # ==========================================================================
    ('BUY_K_SELL_PM', True): {
        'k_action': 'buy',
        'k_side': 'yes',
        'k_price_field': 'k_ask',       # Buying, so use ask
        'pm_intent': 3,                  # BUY_SHORT (short favorite)
        'pm_price_field': 'pm_bid',     # Need to invert: underdog_cost = 100 - pm_bid
        'pm_invert_price': True,        # Signals to use 100 - pm_bid as underdog cost
        'pm_is_buy_short': True,
        'pm_switch_outcome': False,      # Trade on own outcome (long team)
        'k_result': 'YES_TEAM',
        'pm_result': 'YES_OPP',
        'executable': True,
    },

    # ==========================================================================
    # Case 4: BUY_K_SELL_PM, team is NOT pm_long_team (underdog)
    # K: BUY YES team (underdog), PM: BUY YES opponent (via BUY_LONG favorite)
    # HEDGE: K YES team + PM YES opp = hedged
    # Price: pm_bid (underdog bid) → invert to favorite ask = 100 - pm_bid
    # ==========================================================================
    ('BUY_K_SELL_PM', False): {
        'k_action': 'buy',
        'k_side': 'yes',
        'k_price_field': 'k_ask',       # Buying, so use ask
        'pm_intent': 1,                  # BUY_LONG (favorite)
        'pm_price_field': 'pm_bid',     # Need to invert: favorite_ask = 100 - pm_bid
        'pm_invert_price': True,        # Signals to use 100 - pm_bid as the price
        'pm_is_buy_short': False,
        'pm_switch_outcome': True,       # Must switch to long team's outcome for BUY_LONG
        'k_result': 'YES_TEAM',
        'pm_result': 'YES_OPP',
        'executable': True,
    },
}


# =============================================================================
# TRADE RESULT
# =============================================================================
@dataclass
class TradeResult:
    """Result of an execution attempt."""
    success: bool
    kalshi_filled: int = 0
    pm_filled: int = 0
    kalshi_price: int = 0      # cents
    pm_price: float = 0.0      # dollars
    unhedged: bool = False
    abort_reason: str = ""
    execution_time_ms: int = 0
    pm_order_ms: int = 0       # PM order latency
    k_order_ms: int = 0        # Kalshi order latency
    pm_response_details: Optional[Dict] = None  # PM API response diagnostics
    k_response_details: Optional[Dict] = None   # Kalshi API response diagnostics
    execution_phase: str = "ioc"       # "ioc" or "gtc"
    gtc_rest_time_ms: int = 0          # how long GTC rested before fill/cancel
    gtc_spread_checks: int = 0         # spread validations during GTC rest
    gtc_cancel_reason: str = ""        # "timeout", "spread_gone", "filled", ""
    is_maker: bool = False             # True if filled via GTC (0% fee)
    exited: bool = False               # True if PM was successfully unwound after K failure
    unwind_loss_cents: Optional[float] = None  # Unsigned loss from PM unwind (always positive, backward compat)
    unwind_pnl_cents: Optional[float] = None   # Signed P&L from PM unwind (positive=profit, negative=loss)
    unwind_fill_price: Optional[float] = None  # Price PM unwind filled at (dollars)
    unwind_qty: int = 0                         # Contracts actually unwound
    tier: str = ""  # "TIER1_HEDGE", "TIER2_EXIT", "TIER3_UNWIND", "TIER3A", "TIER3_OPPOSITE_HEDGE", etc.
    naked_contracts: int = 0           # Contracts held directional (no hedge)
    omi_ceq: float = 0.0              # CEQ used for decision
    omi_signal: str = ""               # Signal tier (e.g. "HIGH EDGE")
    omi_favored_team: str = ""         # Team OMI favors
    omi_pillar_scores: Optional[Dict] = None  # Full pillar scores dict
    # No-fill diagnostic (only present on PM_NO_FILL trades)
    nofill_diagnosis: Optional[Dict] = None     # Full diagnosis from diagnose_nofill()
    # Opposite-side hedge fields
    opposite_hedge_ticker: str = ""
    opposite_hedge_team: str = ""
    opposite_hedge_price: int = 0           # Kalshi fill price on opposite side (cents)
    opposite_hedge_filled: int = 0
    combined_cost_cents: float = 0.0        # PM + K opposite
    guaranteed_profit_cents: float = 0.0    # (100 - combined) * qty, 0 if overweight


def _log_kalshi_error(ticker: str, price_cents: int, action: str, side: str,
                      count: int, error_str: str, tb: str) -> None:
    """Append Kalshi error to persistent log file for post-hoc diagnosis."""
    try:
        ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        with open(KALSHI_ERRORS_LOG, 'a') as f:
            f.write(f"[{ts}] {ticker} | {action} {count} {side} @ {price_cents}c\n")
            f.write(f"  Error: {error_str}\n")
            f.write(f"  Traceback:\n")
            for line in tb.strip().splitlines():
                f.write(f"    {line}\n")
            f.write("\n")
    except Exception:
        pass  # Never let logging crash execution


# =============================================================================
# NO-FILL DIAGNOSTIC ENGINE
# =============================================================================
# Every PM_NO_FILL must have a verifiable root cause. This system captures:
# 1. Pre-order state: PM BBO, book depth, data age, Kalshi prices
# 2. Order details: exact price sent, intent, outcome_index, buffer used
# 3. PM response: order_id, state, any error message
# 4. Post-order state: PM BBO after the no-fill (was liquidity still there?)
# 5. Verdict: structured classification of WHY it didn't fill

NOFILL_REASONS = {
    'BOOK_EMPTY':       'PM book had no resting orders on our side at order time',
    'PRICE_UNCROSSED':  'Our limit price did not cross the best resting order',
    'DEPTH_EATEN':      'Liquidity was there pre-order but gone post-order (race)',
    'LATENCY_STALE':    'PM data was >500ms old when order hit the exchange',
    'API_REJECTED':     'PM API rejected the order (no order_id returned)',
    'TIMEOUT':          'PM order timed out (>2s) before response received',
    'PARTIAL_ONLY':     'Order partially filled but not enough for hedge',
    'UNKNOWN':          'Could not determine root cause — needs manual review',
}


def diagnose_nofill(
    pm_result: Dict,
    pm_price_sent: float,          # dollars, the limit price we sent
    pm_intent: int,                # 1=BUY_LONG, 3=BUY_SHORT
    is_buy_short: bool,
    pre_order_bbo: Optional[Dict], # {bid_cents, ask_cents, bid_size, ask_size} or None
    post_order_bbo: Optional[Dict],# same shape, fetched AFTER the no-fill
    pm_data_age_ms: int,           # how old the PM WS data was at order time
    pm_order_ms: int,              # round-trip latency of the PM order call
    spread_cents: float,           # spread that triggered the trade
    buffer_cents: int,             # buffer applied to price
) -> Dict:
    """
    Classify a PM no-fill into a verifiable root cause.
    
    Returns dict with:
      reason: str          - key from NOFILL_REASONS
      explanation: str     - human-readable one-liner
      details: dict        - full diagnostic data for logging
    """
    diag: Dict[str, Any] = {
        'reason': 'UNKNOWN',
        'explanation': '',
        'pm_price_sent': pm_price_sent,
        'pm_price_sent_cents': round(pm_price_sent * 100, 1),
        'pm_intent': pm_intent,
        'is_buy_short': is_buy_short,
        'spread_cents': spread_cents,
        'buffer_cents': buffer_cents,
        'pm_data_age_ms': pm_data_age_ms,
        'pm_order_ms': pm_order_ms,
        'pre_bbo': pre_order_bbo,
        'post_bbo': post_order_bbo,
        'pm_order_id': pm_result.get('order_id'),
        'pm_order_state': pm_result.get('order_state', ''),
        'pm_error': pm_result.get('error'),
    }

    # ── Check 1: API rejection (no order_id) ──
    if not pm_result.get('order_id'):
        diag['reason'] = 'API_REJECTED'
        diag['explanation'] = f"PM API rejected: {pm_result.get('error', 'unknown')}"
        return diag

    # ── Check 2: Timeout ──
    if pm_order_ms >= 1900:  # close to 2s timeout
        diag['reason'] = 'TIMEOUT'
        diag['explanation'] = f"PM order took {pm_order_ms}ms (timeout=2000ms)"
        return diag

    # ── Check 3: Pre-order book analysis ──
    if pre_order_bbo:
        pre_bid = pre_order_bbo.get('bid_cents', 0) or 0
        pre_ask = pre_order_bbo.get('ask_cents', 0) or 0
        pre_bid_size = pre_order_bbo.get('bid_size', 0) or 0
        pre_ask_size = pre_order_bbo.get('ask_size', 0) or 0
        price_sent_cents = round(pm_price_sent * 100, 1)

        if is_buy_short:
            # BUY_SHORT: we sell YES. Need a YES bid to match against.
            # Our min sell price = pm_price_sent (YES-frame).
            # We need pre_bid >= our min sell.
            resting_price = pre_bid
            resting_size = pre_bid_size
            crosses = pre_bid >= price_sent_cents if pre_bid else False
            side_label = f"YES bids (best={pre_bid}c x{pre_bid_size})"
            cross_label = f"our min_sell={price_sent_cents:.0f}c vs best_bid={pre_bid}c"
        else:
            # BUY_LONG: we buy YES. Need a YES ask to match against.
            # Our max buy price = pm_price_sent (YES-frame).
            # We need pre_ask <= our max buy.
            resting_price = pre_ask
            resting_size = pre_ask_size
            crosses = pre_ask <= price_sent_cents if pre_ask else False
            side_label = f"YES asks (best={pre_ask}c x{pre_ask_size})"
            cross_label = f"our max_buy={price_sent_cents:.0f}c vs best_ask={pre_ask}c"

        diag['resting_price'] = resting_price
        diag['resting_size'] = resting_size
        diag['price_crosses'] = crosses
        diag['cross_detail'] = cross_label

        if not resting_price or resting_size == 0:
            diag['reason'] = 'BOOK_EMPTY'
            diag['explanation'] = f"No resting {side_label} at order time"
            return diag

        if not crosses:
            diag['reason'] = 'PRICE_UNCROSSED'
            diag['explanation'] = f"Price didn't cross: {cross_label}"
            return diag

    # ── Check 4: Post-order book comparison ──
    if pre_order_bbo and post_order_bbo:
        if is_buy_short:
            post_bid = post_order_bbo.get('bid_cents', 0) or 0
            post_bid_size = post_order_bbo.get('bid_size', 0) or 0
            pre_liq = pre_order_bbo.get('bid_size', 0) or 0
            if pre_liq > 0 and post_bid_size == 0:
                diag['reason'] = 'DEPTH_EATEN'
                diag['explanation'] = (f"Liquidity race: pre={pre_liq} bids @ "
                                       f"{pre_order_bbo.get('bid_cents', 0)}c → "
                                       f"post={post_bid_size} bids @ {post_bid}c")
                return diag
        else:
            post_ask = post_order_bbo.get('ask_cents', 0) or 0
            post_ask_size = post_order_bbo.get('ask_size', 0) or 0
            pre_liq = pre_order_bbo.get('ask_size', 0) or 0
            if pre_liq > 0 and post_ask_size == 0:
                diag['reason'] = 'DEPTH_EATEN'
                diag['explanation'] = (f"Liquidity race: pre={pre_liq} asks @ "
                                       f"{pre_order_bbo.get('ask_cents', 0)}c → "
                                       f"post={post_ask_size} asks @ {post_ask}c")
                return diag

    # ── Check 5: Stale data ──
    if pm_data_age_ms > 500:
        diag['reason'] = 'LATENCY_STALE'
        diag['explanation'] = f"PM data was {pm_data_age_ms}ms old at order time"
        return diag

    # ── Check 6: price crossed pre-order but still no fill → likely race condition ──
    if pre_order_bbo and diag.get('price_crosses'):
        # Price should have crossed, but didn't fill.
        # Most likely: between BBO fetch and order arrival, someone else took the liquidity.
        diag['reason'] = 'DEPTH_EATEN'
        diag['explanation'] = (f"Price crossed ({diag.get('cross_detail', '')}) but IOC expired — "
                               f"liquidity consumed between BBO fetch and order arrival "
                               f"(order latency: {pm_order_ms}ms)")
        return diag

    # ── Fallback ──
    diag['reason'] = 'UNKNOWN'
    diag['explanation'] = (f"No clear root cause. order_state={pm_result.get('order_state', '?')}, "
                           f"pm_latency={pm_order_ms}ms, data_age={pm_data_age_ms}ms")
    return diag


def _extract_pm_response_details(pm_result: Dict) -> Dict:
    """Extract PM API response details for trade record diagnostics."""
    details: Dict[str, Any] = {}

    # HTTP status: infer from response shape
    if 'order_id' in pm_result:
        details['pm_response_status'] = 200
    elif 'error' in pm_result:
        err = pm_result['error']
        if isinstance(err, str) and err.startswith('HTTP '):
            try:
                details['pm_response_status'] = int(err.split(':')[0].split(' ')[1])
            except (ValueError, IndexError):
                details['pm_response_status'] = None
        else:
            details['pm_response_status'] = None
    else:
        details['pm_response_status'] = None

    # Response body (truncated to 500 chars)
    body_str = json.dumps(pm_result, default=str)
    details['pm_response_body'] = body_str[:500]

    # Fill details
    details['pm_fill_price'] = pm_result.get('fill_price')
    details['pm_fill_qty'] = pm_result.get('fill_count', 0)
    details['pm_order_id'] = pm_result.get('order_id')

    # Expiry / failure reason
    order_state = pm_result.get('order_state', '')
    if order_state == 'ORDER_STATE_EXPIRED':
        details['pm_expiry_reason'] = 'IOC expired (no matching liquidity at limit price)'
    elif order_state == 'ORDER_STATE_CANCELED':
        details['pm_expiry_reason'] = 'Order canceled'
    elif 'error' in pm_result:
        details['pm_expiry_reason'] = str(pm_result['error'])[:200]
    elif pm_result.get('fill_count', 0) == 0 and order_state:
        details['pm_expiry_reason'] = f'No fill (state: {order_state})'
    else:
        details['pm_expiry_reason'] = None

    return details


def _kalshi_fee_cents(price_cents: int) -> int:
    """Kalshi fee per contract: ceil(0.07 * P * (1-P) * 100) where P = price/100."""
    p = price_cents / 100.0
    return math.ceil(0.07 * p * (1 - p) * 100)


async def _unwind_pm_position(
    session, pm_api, pm_slug: str, reverse_intent: int,
    pm_price_cents: float, qty: int, outcome_index: int,
    buffers: list = None,
) -> Tuple[int, Optional[float]]:
    """
    Attempt to unwind a PM position with configurable buffer steps.
    Returns (filled_count, fill_price_or_None).
    """
    if buffers is None:
        buffers = [10, 25]

    # Try SDK close_position first (fastest exit)
    try:
        close_resp = await pm_api.close_position(session, pm_slug, outcome_index=outcome_index)
        cum_qty = close_resp.get("cumQuantity", 0)
        if isinstance(cum_qty, str):
            cum_qty = int(cum_qty) if cum_qty else 0
        filled_qty = int(cum_qty)
        if filled_qty >= qty:
            avg_px = close_resp.get("avgPx", {})
            if isinstance(avg_px, dict):
                fill_price = float(avg_px.get("value", 0)) if avg_px.get("value") else 0
            else:
                fill_price = float(avg_px) if avg_px else 0
            loss_cents = abs(pm_price_cents - fill_price * 100)
            print(f"[UNWIND] SDK close_position filled {filled_qty} @ {fill_price:.4f} (loss ~{loss_cents:.1f}c)")
            return filled_qty, fill_price
        print(f"[UNWIND] SDK close_position partial: {filled_qty}/{qty}, falling back to manual")
    except Exception as e:
        print(f"[UNWIND] SDK close_position failed: {e}, falling back to manual buffers")

    for attempt, buffer in enumerate(buffers, 1):
        if reverse_intent == 2:  # SELL_LONG: sell YES lower to exit (accept less)
            price_cents = max(pm_price_cents - buffer, 1)
        else:  # SELL_SHORT (4): buy YES higher to close short (pay more to exit)
            price_cents = min(pm_price_cents + buffer, 99)
        price = price_cents / 100.0
        label = f"attempt {attempt} (buf={buffer}c)"
        try:
            result = await pm_api.place_order(
                session, pm_slug, reverse_intent, price, qty,
                tif=3, sync=True, outcome_index=outcome_index
            )
            filled = result.get('fill_count', 0)
            fill_price = result.get('fill_price', price)
            if filled > 0:
                print(f"[RECOVERY] PM unwind {label}: filled {filled} @ ${fill_price:.3f} (buf={buffer}c)")
                return filled, fill_price
            else:
                print(f"[RECOVERY] PM unwind {label}: no fill (buf={buffer}c)")
        except Exception as e:
            print(f"[RECOVERY] PM unwind {label} error: {e}")
    return 0, None


def _find_kalshi_wider_price(
    k_book_ref: Optional[Dict],
    action: str,
    original_price: int,
    count: int,
    pm_fill_price_cents: float,
    direction: str,
) -> Optional[int]:
    """
    Walk the WS orderbook to find the nearest price level with sufficient depth
    where an arb still exists net of fees.

    Returns the price in cents, or None if no profitable wider price exists.
    Does NOT place any orders — pure price discovery from local WS data.
    """
    if not k_book_ref:
        return None

    if action == 'buy':
        # Buying YES: walk YES asks upward from original+1
        asks = k_book_ref.get('yes_asks', {})
        for price_str in sorted(asks.keys(), key=lambda x: int(x)):
            price = int(price_str)
            if price <= original_price:
                continue
            if price > 95:
                break
            depth = int(asks[price_str])
            if depth < count:
                continue
            # Check if arb still exists at this wider price
            # BUY_K_SELL_PM: spread = (100 - pm_cost) - k_price
            if direction == 'BUY_K_SELL_PM':
                wider_spread = (100 - pm_fill_price_cents) - price
            else:
                wider_spread = price - pm_fill_price_cents
            k_fee = _kalshi_fee_cents(price)
            pm_fee = math.ceil(pm_fill_price_cents * 0.001)
            net_profit = wider_spread - k_fee - pm_fee
            if net_profit >= 1:  # At least 1 cent profit
                return price
    else:
        # Selling YES: walk YES bids downward from original-1
        bids = k_book_ref.get('yes_bids', {})
        for price_str in sorted(bids.keys(), key=lambda x: -int(x)):
            price = int(price_str)
            if price >= original_price:
                continue
            if price < 5:
                break
            depth = int(bids[price_str])
            if depth < count:
                continue
            # BUY_PM_SELL_K: spread = k_price - pm_cost
            if direction == 'BUY_PM_SELL_K':
                wider_spread = price - pm_fill_price_cents
            else:
                wider_spread = pm_fill_price_cents - price
            k_fee = _kalshi_fee_cents(price)
            pm_fee = math.ceil(pm_fill_price_cents * 0.001)
            net_profit = wider_spread - k_fee - pm_fee
            if net_profit >= 1:
                return price

    return None


def check_kalshi_spread_live(
    k_book: Dict,
    direction: str,
    pm_price_cents: float,
) -> Tuple[bool, int]:
    """Check if Kalshi spread still exceeds Config.spread_min_cents.

    Uses pm_price_cents (our PM limit price) because during GTC rest
    we don't have a fill price yet.
    """
    if not k_book:
        return False, 0
    best_bid = k_book.get('best_bid')
    best_ask = k_book.get('best_ask')
    if best_bid is None or best_ask is None:
        return False, 0
    if direction == 'BUY_PM_SELL_K':
        current_spread = best_bid - pm_price_cents
    else:
        current_spread = pm_price_cents - best_ask
    return current_spread >= Config.spread_min_cents, int(current_spread)


async def _execute_gtc_phase(
    session, pm_api, pm_slug: str, pm_intent: int,
    pm_price: float, size: int, outcome_index: int,
    k_book_ref: Dict, direction: str, game_id: str,
) -> Dict:
    """
    Phase 2: Place GTC, monitor spread, return fill info.
    Returns: {filled, fill_price, order_id, cancel_reason, rest_time_ms, spread_checks, is_maker}
    """
    global _resting_gtc_order_id

    result = {
        'filled': 0, 'fill_price': None, 'order_id': '',
        'cancel_reason': '', 'rest_time_ms': 0, 'spread_checks': 0, 'is_maker': False,
    }

    # Safety gate: only 1 GTC at a time
    if _resting_gtc_order_id is not None:
        result['cancel_reason'] = 'concurrent_gtc'
        return result

    # Per-game cooldown check
    now = time.time()
    if game_id in gtc_cooldowns and now < gtc_cooldowns[game_id]:
        remaining = gtc_cooldowns[game_id] - now
        result['cancel_reason'] = f'cooldown ({remaining:.0f}s left)'
        return result

    # Place GTC order (tif=1 = GTC, sync=False for async placement)
    gtc_start = time.time()
    try:
        pm_result = await pm_api.place_order(
            session, pm_slug, pm_intent, pm_price, size,
            tif=1,       # GTC
            sync=False,  # Async - we'll poll status
            outcome_index=outcome_index
        )
    except Exception as e:
        result['cancel_reason'] = f'place_error: {e}'
        return result

    order_id = pm_result.get('order_id', '')
    if not order_id:
        result['cancel_reason'] = f"no_order_id: {pm_result.get('error', 'unknown')}"
        return result

    result['order_id'] = order_id

    # Handle paper/dry_run → instant fill
    if Config.is_paper() or Config.dry_run_mode:
        fill_count = pm_result.get('fill_count', 0)
        result['filled'] = fill_count if fill_count > 0 else size
        result['fill_price'] = pm_result.get('fill_price', pm_price)
        result['is_maker'] = True
        result['cancel_reason'] = 'filled'
        return result

    # Handle instant fill from place_order response
    instant_fills = pm_result.get('fill_count', 0)
    if instant_fills >= size:
        result['filled'] = instant_fills
        result['fill_price'] = pm_result.get('fill_price', pm_price)
        result['is_maker'] = True
        result['cancel_reason'] = 'filled'
        return result

    # Set global gate
    _resting_gtc_order_id = order_id
    print(f"[GTC] Resting order {order_id[:12]}... {size}@${pm_price:.2f} (timeout={Config.gtc_timeout_seconds}s)")

    # Monitoring loop
    loop_start = time.time()
    spread_checks = 0
    cancel_reason = ''

    try:
        while (time.time() - loop_start) < Config.gtc_timeout_seconds:
            await asyncio.sleep(Config.gtc_recheck_interval_ms / 1000)
            elapsed_ms = int((time.time() - loop_start) * 1000)

            # Check order status
            status = await pm_api.get_order_status(session, order_id)

            cum_qty = status.get('cum_quantity', 0)
            state = status.get('state', '')

            if cum_qty >= size or state in ('ORDER_STATE_FILLED',):
                result['filled'] = cum_qty
                result['fill_price'] = status.get('fill_price', pm_price)
                result['is_maker'] = True
                cancel_reason = 'filled'
                print(f"[GTC] FILLED {cum_qty}/{size} @ {elapsed_ms}ms")
                break

            if state in ('ORDER_STATE_CANCELED', 'ORDER_STATE_EXPIRED'):
                cancel_reason = f'state_{state}'
                break

            # Check spread
            spread_checks += 1
            spread_ok, current_spread = check_kalshi_spread_live(
                k_book_ref, direction, pm_price * 100
            )
            status_str = 'ok' if spread_ok else 'GONE'
            print(f"[GTC] {elapsed_ms}ms spread={current_spread}c {status_str} (fills={cum_qty})")

            if not spread_ok:
                cancel_reason = 'spread_gone'
                break

        # Timeout
        if not cancel_reason:
            cancel_reason = 'timeout'

    finally:
        result['rest_time_ms'] = int((time.time() - loop_start) * 1000)
        result['spread_checks'] = spread_checks
        result['cancel_reason'] = cancel_reason

        # Cancel if not fully filled
        if cancel_reason != 'filled':
            # Try to cancel
            cancel_ok = await pm_api.cancel_order(session, order_id, pm_slug)
            # ALWAYS recheck fill status after cancel — even if cancel "succeeded"
            recheck = await pm_api.get_order_status(session, order_id)
            recheck_qty = recheck.get('cum_quantity', 0)
            if recheck_qty > 0:
                result['filled'] = recheck_qty
                result['fill_price'] = recheck.get('fill_price', pm_price)
                result['is_maker'] = True
                result['cancel_reason'] = 'filled_on_cancel'
                print(f"[GTC] Post-cancel recheck: FILLED {recheck_qty} (cancel_ok={cancel_ok})")

            # Set cooldown on timeout/spread_gone
            if cancel_reason in ('timeout', 'spread_gone'):
                gtc_cooldowns[game_id] = time.time() + Config.gtc_cooldown_seconds

        # Clear global gate
        _resting_gtc_order_id = None

    return result


# =============================================================================
# SAFETY STATE (module-level, persists across trades)
# =============================================================================
traded_games: Set[str] = set()           # Games traded this session
blacklisted_games: Set[str] = set()      # Games blacklisted after crashes
crash_counts: Dict[str, int] = {}        # Crash count per game
cached_positions: Dict[str, int] = {}    # Kalshi positions cache
cached_positions_ts: float = 0           # Cache timestamp

# Unhedged exposure tracking
unhedged_positions: Dict[str, int] = {}  # ticker → cost_cents of unhedged leg
executor_paused: bool = False
MAX_UNHEDGED_EXPOSURE_CENTS = 5000       # $50 — pause executor if exceeded

# GTC execution state
gtc_cooldowns: Dict[str, float] = {}      # game_id -> timestamp cooldown expires
_resting_gtc_order_id: Optional[str] = None  # max 1 resting GTC globally


def register_unhedged(ticker: str, cost_cents: int):
    """Track an unhedged position. Pauses executor if total exceeds limit."""
    global executor_paused
    unhedged_positions[ticker] = cost_cents
    total = sum(unhedged_positions.values())
    print(f"[EXPOSURE] Unhedged: {ticker} +{cost_cents}c | total=${total/100:.2f} "
          f"(limit=${MAX_UNHEDGED_EXPOSURE_CENTS/100:.2f})", flush=True)
    if total > MAX_UNHEDGED_EXPOSURE_CENTS:
        executor_paused = True
        print(f"[EXPOSURE_LIMIT] EXECUTOR PAUSED: unhedged exposure ${total/100:.2f} > "
              f"${MAX_UNHEDGED_EXPOSURE_CENTS/100:.2f} limit. Manual review required.", flush=True)


def clear_unhedged(ticker: str):
    """Remove from unhedged tracker (e.g., after manual close or settlement)."""
    unhedged_positions.pop(ticker, None)


# =============================================================================
# TRADED GAMES PERSISTENCE
# =============================================================================
def load_traded_games(clear: bool = False) -> int:
    """
    Load previously traded games from traded_games.json.

    Args:
        clear: If True, delete the file and start fresh

    Returns:
        Number of games loaded
    """
    global traded_games

    if clear:
        if os.path.exists(TRADED_GAMES_FILE):
            os.remove(TRADED_GAMES_FILE)
            print(f"[INIT] Cleared traded_games.json")
        traded_games.clear()
        return 0

    if not os.path.exists(TRADED_GAMES_FILE):
        return 0

    try:
        with open(TRADED_GAMES_FILE, 'r') as f:
            data = json.load(f)

        # data is a list of {game_id, timestamp, ...} entries
        for entry in data:
            game_id = entry.get('game_id')
            if game_id:
                traded_games.add(game_id)

        return len(traded_games)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[WARN] Failed to load traded_games.json: {e}")
        return 0


def save_traded_game(game_id: str, pm_slug: str = "", team: str = "") -> None:
    """
    Append a traded game to traded_games.json.

    Args:
        game_id: The game identifier (e.g., "26FEB09NAVYBUCK")
        pm_slug: The PM market slug
        team: The team that was traded
    """
    # Load existing data
    data = []
    if os.path.exists(TRADED_GAMES_FILE):
        try:
            with open(TRADED_GAMES_FILE, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []

    # Append new entry
    entry = {
        "game_id": game_id,
        "pm_slug": pm_slug,
        "team": team,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    data.append(entry)

    # Write back
    try:
        with open(TRADED_GAMES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"[WARN] Failed to save traded_games.json: {e}")


def get_traded_games_count() -> int:
    """Get the number of traded games in the current session."""
    return len(traded_games)


# =============================================================================
# DIRECTIONAL POSITION TRACKING (OMI Edge Tier 3a/3b)
# =============================================================================
# In-memory directional positions for exposure tracking
# Key: game_id → {contracts, entry_price_cents, side, tier, ceq, timestamp, ...}
directional_positions: Dict[str, Dict] = {}


def load_directional_positions() -> Tuple[float, float]:
    """Load directional_positions.json. Return (current_exposure_usd, daily_loss_usd)."""
    global directional_positions
    if not os.path.exists(DIRECTIONAL_POSITIONS_FILE):
        return 0.0, 0.0
    try:
        with open(DIRECTIONAL_POSITIONS_FILE, 'r') as f:
            data = json.load(f)
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        exposure = 0.0
        daily_loss = 0.0
        for entry in data:
            gid = entry.get('game_id', '')
            if not entry.get('settled', False):
                # Active position → count toward exposure
                cost = entry.get('entry_price_cents', 0) * entry.get('naked_contracts', 0) / 100.0
                exposure += cost
                directional_positions[gid] = entry
            else:
                # Settled → count toward daily loss if today
                ts = entry.get('timestamp', '')
                if ts.startswith(today):
                    pnl = entry.get('settlement_pnl', 0)
                    if pnl < 0:
                        daily_loss += abs(pnl)
        return exposure, daily_loss
    except Exception as e:
        print(f"[WARN] Failed to load directional_positions.json: {e}")
        return 0.0, 0.0


def save_directional_position(entry: dict) -> None:
    """Append a directional position entry to directional_positions.json."""
    data = []
    if os.path.exists(DIRECTIONAL_POSITIONS_FILE):
        try:
            with open(DIRECTIONAL_POSITIONS_FILE, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []
    data.append(entry)
    with open(DIRECTIONAL_POSITIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    # Also track in memory
    gid = entry.get('game_id', '')
    if gid and not entry.get('settled', False):
        directional_positions[gid] = entry


# =============================================================================
# SAFETY FUNCTIONS
# =============================================================================
def on_execution_crash(game_id: str) -> None:
    """Record an execution crash. Blacklist after max crashes."""
    crash_counts[game_id] = crash_counts.get(game_id, 0) + 1
    if crash_counts[game_id] >= Config.max_crashes_per_game:
        blacklisted_games.add(game_id)
        print(f"[SAFETY] Game {game_id} BLACKLISTED after {crash_counts[game_id]} crashes")


async def refresh_position_cache(session, kalshi_api, prefetched=None) -> None:
    """Refresh the Kalshi positions cache.

    Called in the background (every 60s via refresh_balances), NOT on the hot path.
    If prefetched positions are provided, use those to avoid a duplicate API call.
    """
    global cached_positions, cached_positions_ts
    try:
        positions = prefetched if prefetched is not None else await kalshi_api.get_positions(session)
        cached_positions.clear()
        if positions:
            for ticker, pos in positions.items():
                qty = pos.position if hasattr(pos, 'position') else pos.get('position', 0)
                if qty != 0:
                    cached_positions[ticker] = qty
        cached_positions_ts = time.time()
    except Exception as e:
        print(f"[SAFETY] Failed to refresh positions: {e}")


def calculate_optimal_size(
    kalshi_book: Dict,       # {yes_bids: {price: size}, yes_asks: {price: size}}
    pm_depth: Dict,          # {bids: [{price_cents, size}], asks: [{price_cents, size}], timestamp_ms}
    direction: str,          # 'BUY_PM_SELL_K' or 'BUY_K_SELL_PM'
    is_long_team: bool,
    pm_balance_cents: int,
    k_balance_cents: int,
    max_contracts: int,
) -> Dict:
    """
    Walk both orderbooks to find optimal contract count.

    Returns: {size, expected_profit_cents, avg_spread_cents, avg_pm_price,
              avg_k_price, k_depth, pm_depth, limit_reason}
    """
    default = {
        'size': 1, 'expected_profit_cents': 0, 'avg_spread_cents': 0,
        'avg_pm_price': 0, 'avg_k_price': 0, 'k_depth': 0, 'pm_depth': 0,
        'limit_reason': 'default',
    }

    # Validate PM depth freshness (>2s stale -> fallback to 1)
    if not pm_depth or not pm_depth.get('bids') or not pm_depth.get('asks'):
        default['limit_reason'] = 'no_pm_depth'
        return default

    now_ms = int(time.time() * 1000)
    if now_ms - pm_depth.get('timestamp_ms', 0) > 2000:
        default['limit_reason'] = 'pm_depth_stale'
        return default

    # ── Step A: Build Kalshi levels ──
    # BUY_PM_SELL_K → SELL YES on Kalshi → walk yes_bids descending (highest first)
    # BUY_K_SELL_PM → BUY YES on Kalshi → walk yes_asks ascending (lowest first)
    k_levels = []
    if direction == 'BUY_PM_SELL_K':
        raw = kalshi_book.get('yes_bids', {})
        for price in sorted(raw.keys(), reverse=True):
            k_levels.append((int(price), int(raw[price])))
    else:  # BUY_K_SELL_PM
        raw = kalshi_book.get('yes_asks', {})
        for price in sorted(raw.keys()):
            k_levels.append((int(price), int(raw[price])))

    if not k_levels:
        default['limit_reason'] = 'no_k_depth'
        return default

    # ── Step B: Build PM levels (raw long-team frame from pm_books) ──
    # Cases 1,4: walk PM asks ascending, cost = ask_price
    # Cases 2,3: walk PM bids descending, cost = 100 - bid_price
    pm_levels = []  # [(effective_cost_cents, available_size)]
    walk_asks = (direction == 'BUY_PM_SELL_K' and is_long_team) or \
                (direction == 'BUY_K_SELL_PM' and not is_long_team)

    if walk_asks:
        for level in pm_depth['asks']:  # already sorted ascending
            pm_levels.append((level['price_cents'], level['size']))
    else:
        for level in pm_depth['bids']:  # already sorted descending
            pm_levels.append((100 - level['price_cents'], level['size']))

    if not pm_levels:
        default['limit_reason'] = 'no_pm_levels'
        return default

    # ── Step C: Walk both books, compute marginal profit per contract ──
    k_idx = 0
    k_remaining = k_levels[0][1] if k_levels else 0
    pm_idx = 0
    pm_remaining = pm_levels[0][1] if pm_levels else 0

    contracts = 0
    total_profit = 0.0
    total_k_price = 0
    total_pm_cost = 0
    total_k_available = sum(s for _, s in k_levels)
    total_pm_available = sum(s for _, s in pm_levels)

    # Depth walk log: track each price-level transition
    depth_walk_log = []
    _prev_k_idx = -1
    _prev_pm_idx = -1
    _level_contracts = 0
    _walk_stopped_reason = None

    while contracts < max_contracts:
        # Get current prices at this depth level
        if k_idx >= len(k_levels) or pm_idx >= len(pm_levels):
            _walk_stopped_reason = 'book_exhausted'
            break
        if k_remaining <= 0:
            k_idx += 1
            if k_idx >= len(k_levels):
                _walk_stopped_reason = 'k_book_exhausted'
                break
            k_remaining = k_levels[k_idx][1]
        if pm_remaining <= 0:
            pm_idx += 1
            if pm_idx >= len(pm_levels):
                _walk_stopped_reason = 'pm_book_exhausted'
                break
            pm_remaining = pm_levels[pm_idx][1]

        k_price = k_levels[k_idx][0]
        pm_cost = pm_levels[pm_idx][0]

        # Compute marginal spread
        if direction == 'BUY_PM_SELL_K':
            spread = k_price - pm_cost
        else:  # BUY_K_SELL_PM
            spread = (100 - pm_cost) - k_price

        # Compute fees for this contract (including Kalshi buffer cost)
        fees = Config.kalshi_fee_cents + (pm_cost * Config.pm_us_fee_rate) + Config.expected_slippage_cents + Config.price_buffer_cents
        marginal_profit = spread - fees

        if marginal_profit < Config.min_profit_per_contract:
            # Log the unprofitable level that stopped the walk
            depth_walk_log.append({
                'level': len(depth_walk_log) + 1,
                'k_price': k_price,
                'pm_cost': pm_cost,
                'spread': round(spread, 2),
                'fees': round(fees, 2),
                'marginal_profit': round(marginal_profit, 2),
                'k_remaining': k_remaining,
                'pm_remaining': pm_remaining,
                'cumulative_contracts': contracts,
                'stopped': True,
            })
            _walk_stopped_reason = 'unprofitable'
            break

        # Log new price-level transition
        if k_idx != _prev_k_idx or pm_idx != _prev_pm_idx:
            # Close out previous level
            if _prev_k_idx >= 0 and _level_contracts > 0:
                depth_walk_log[-1]['contracts_at_level'] = _level_contracts
            _prev_k_idx = k_idx
            _prev_pm_idx = pm_idx
            _level_contracts = 0
            depth_walk_log.append({
                'level': len(depth_walk_log) + 1,
                'k_price': k_price,
                'pm_cost': pm_cost,
                'spread': round(spread, 2),
                'fees': round(fees, 2),
                'marginal_profit': round(marginal_profit, 2),
                'k_remaining': k_remaining,
                'pm_remaining': pm_remaining,
                'cumulative_contracts': contracts + 1,
                'stopped': False,
            })

        # Take 1 contract from both books
        contracts += 1
        _level_contracts += 1
        total_profit += marginal_profit
        total_k_price += k_price
        total_pm_cost += pm_cost
        k_remaining -= 1
        pm_remaining -= 1

    # Finalize last profitable level's contract count
    if depth_walk_log and not depth_walk_log[-1].get('stopped') and _level_contracts > 0:
        depth_walk_log[-1]['contracts_at_level'] = _level_contracts

    # ── Depth profile: continue walk past cap for analysis ──
    depth_profile = []
    if _walk_stopped_reason is None and contracts > 0:
        # Walk stopped at max_contracts — continue to find full profitable depth
        dp_k_idx, dp_pm_idx = k_idx, pm_idx
        dp_k_rem, dp_pm_rem = k_remaining, pm_remaining
        dp_contracts = contracts
        dp_total_profit = total_profit
        dp_prev_k = -1
        dp_prev_pm = -1

        while True:
            if dp_k_idx >= len(k_levels) or dp_pm_idx >= len(pm_levels):
                break
            if dp_k_rem <= 0:
                dp_k_idx += 1
                if dp_k_idx >= len(k_levels):
                    break
                dp_k_rem = k_levels[dp_k_idx][1]
            if dp_pm_rem <= 0:
                dp_pm_idx += 1
                if dp_pm_idx >= len(pm_levels):
                    break
                dp_pm_rem = pm_levels[dp_pm_idx][1]

            kp = k_levels[dp_k_idx][0]
            pc = pm_levels[dp_pm_idx][0]
            if direction == 'BUY_PM_SELL_K':
                sp = kp - pc
            else:
                sp = (100 - pc) - kp
            f = Config.kalshi_fee_cents + (pc * Config.pm_us_fee_rate) + Config.expected_slippage_cents + Config.price_buffer_cents
            net = sp - f

            if net < Config.min_profit_per_contract:
                break

            # New level transition → start new profile entry
            if dp_k_idx != dp_prev_k or dp_pm_idx != dp_prev_pm:
                dp_prev_k = dp_k_idx
                dp_prev_pm = dp_pm_idx
                depth_profile.append({
                    'level': len(depth_profile) + 1,
                    'k_price': kp,
                    'pm_cost': pc,
                    'spread': round(sp, 2),
                    'net': round(net, 2),
                    'available': 0,
                    'cumulative': dp_contracts,
                })

            dp_contracts += 1
            dp_total_profit += net
            dp_k_rem -= 1
            dp_pm_rem -= 1
            depth_profile[-1]['available'] += 1
            depth_profile[-1]['cumulative'] = dp_contracts

        max_profitable = dp_contracts
        max_profit = dp_total_profit
    else:
        # Walk ended naturally (unprofitable or exhausted) — full depth already captured
        max_profitable = contracts
        max_profit = total_profit

    if contracts == 0:
        return {
            'size': 0, 'expected_profit_cents': 0, 'avg_spread_cents': 0,
            'avg_pm_price': 0, 'avg_k_price': 0,
            'k_depth': total_k_available, 'pm_depth': total_pm_available,
            'limit_reason': 'no_profitable_contracts',
            'depth_walk_log': depth_walk_log,
            'depth_profile': depth_profile,
            'max_profitable_contracts': max_profitable,
            'max_theoretical_profit_cents': round(max_profit, 2),
            'traded_contracts': 0,
            'captured_profit_cents': 0,
        }

    # ── Step D: Apply safety caps ──
    depth_limit = min(total_k_available, total_pm_available)
    spread_at_l1 = depth_walk_log[0]['spread'] if depth_walk_log else 0
    depth_cap_used = get_depth_cap(spread_at_l1)
    safe_depth = math.floor(depth_limit * depth_cap_used)

    # Capital limits (approximate using best-level cost)
    best_pm_cost = pm_levels[0][0] if pm_levels else 50
    best_k_cost = k_levels[0][0] if k_levels else 50
    if direction == 'BUY_PM_SELL_K':
        # K cost = 100 - k_bid (risk on short side)
        k_cost_per = 100 - best_k_cost
    else:
        k_cost_per = best_k_cost
    capital_limit_pm = math.floor(pm_balance_cents / max(best_pm_cost, 1))
    capital_limit_k = math.floor(k_balance_cents / max(k_cost_per, 1))
    capital_limit = min(capital_limit_pm, capital_limit_k)

    # Max 12% of smaller account balance committed per trade
    max_commitment_pct = 0.12
    smaller_balance = min(k_balance_cents, pm_balance_cents)
    max_cost_per_contract = max(k_cost_per, best_pm_cost)
    commitment_cap = math.floor((smaller_balance * max_commitment_pct) / max(max_cost_per_contract, 1))

    # Determine limiting factor
    limit_reason = 'depth_walk'
    final_size = contracts
    if safe_depth < final_size:
        final_size = safe_depth
        limit_reason = 'depth_cap'
    if capital_limit < final_size:
        final_size = capital_limit
        limit_reason = 'capital'
    if commitment_cap < final_size:
        final_size = commitment_cap
        limit_reason = 'commitment_cap'
    if max_contracts < final_size:
        final_size = max_contracts
        limit_reason = 'max_contracts'

    # Always at least 1 if any spread was profitable
    final_size = max(final_size, 1)

    # Recalculate expected profit at final_size (may be less than full walk)
    if final_size < contracts:
        # Re-walk for exact final_size
        k_idx2 = 0
        k_rem2 = k_levels[0][1]
        pm_idx2 = 0
        pm_rem2 = pm_levels[0][1]
        total_profit = 0.0
        total_k_price = 0
        total_pm_cost = 0
        for _ in range(final_size):
            if k_rem2 <= 0:
                k_idx2 += 1
                k_rem2 = k_levels[k_idx2][1]
            if pm_rem2 <= 0:
                pm_idx2 += 1
                pm_rem2 = pm_levels[pm_idx2][1]
            kp = k_levels[k_idx2][0]
            pc = pm_levels[pm_idx2][0]
            if direction == 'BUY_PM_SELL_K':
                sp = kp - pc
            else:
                sp = (100 - pc) - kp
            fees = Config.kalshi_fee_cents + (pc * Config.pm_us_fee_rate) + Config.expected_slippage_cents + Config.price_buffer_cents
            total_profit += sp - fees
            total_k_price += kp
            total_pm_cost += pc
            k_rem2 -= 1
            pm_rem2 -= 1

    if total_profit <= 0:
        return {
            'size': 0, 'expected_profit_cents': 0, 'avg_spread_cents': 0,
            'avg_pm_price': 0, 'avg_k_price': 0,
            'k_depth': total_k_available, 'pm_depth': total_pm_available,
            'limit_reason': 'negative_total_profit',
            'depth_walk_log': depth_walk_log,
            'depth_profile': depth_profile,
            'max_profitable_contracts': max_profitable,
            'max_theoretical_profit_cents': round(max_profit, 2),
            'traded_contracts': 0,
            'captured_profit_cents': 0,
        }

    avg_k = total_k_price / final_size if final_size > 0 else 0
    avg_pm = total_pm_cost / final_size if final_size > 0 else 0
    avg_spread = (total_k_price - total_pm_cost) / final_size if direction == 'BUY_PM_SELL_K' and final_size > 0 else \
                 ((100 * final_size - total_pm_cost - total_k_price) / final_size if final_size > 0 else 0)

    return {
        'size': final_size,
        'expected_profit_cents': round(total_profit, 2),
        'avg_spread_cents': round(avg_spread, 2),
        'avg_pm_price': round(avg_pm, 2),
        'avg_k_price': round(avg_k, 2),
        'k_depth': total_k_available,
        'pm_depth': total_pm_available,
        'limit_reason': limit_reason,
        'depth_walk_log': depth_walk_log,
        'depth_profile': depth_profile,
        'max_profitable_contracts': max_profitable,
        'max_theoretical_profit_cents': round(max_profit, 2),
        'traded_contracts': final_size,
        'captured_profit_cents': round(total_profit, 2),
        'depth_cap_used': depth_cap_used,
        'spread_at_sizing': spread_at_l1,
        'commitment_cap': commitment_cap,
    }


def safe_to_trade(
    ticker: str,
    game_id: str
) -> Tuple[bool, str]:
    """
    Pre-trade safety checks using IN-MEMORY state only (no API calls).

    Checks:
    1. Game not blacklisted
    2. Game not already traded this session
    3. No existing position on this ticker (from local cache)
    4. Under position limit (from local cache)

    Position cache is refreshed in the background by the WS executor,
    NOT on the hot execution path.
    """
    # Check if executor is paused (unhedged exposure limit)
    if executor_paused:
        return False, "Executor PAUSED: unhedged exposure limit exceeded — manual review required"

    # Check blacklist
    if game_id in blacklisted_games:
        return False, f"Game {game_id} is BLACKLISTED after crashes"

    # Check already traded (skippable via config for multi-trade-per-game strategies)
    if not Config.skip_traded_games_check and game_id in traded_games:
        return False, f"Game {game_id} already traded this session"

    # Check existing position (from local cache — no API call)
    if False and ticker in cached_positions:  # DISABLED: K-first testing
        pos_count = cached_positions[ticker]
        if abs(pos_count) >= Config.max_contracts_per_game:
            return False, f"Already have {pos_count} contracts on {ticker}"

    # Check position limit
    total_positions = len(cached_positions)
    if total_positions >= Config.max_concurrent_positions:
        return False, f"Too many positions ({total_positions}/{Config.max_concurrent_positions})"

    return True, "OK"


def update_position_cache_after_trade(ticker: str, qty_delta: int):
    """
    Update the local position cache after a successful Kalshi fill.
    Called from execute_arb() so the cache stays current without API calls.
    """
    current = cached_positions.get(ticker, 0)
    new_qty = current + qty_delta
    if new_qty == 0:
        cached_positions.pop(ticker, None)
    else:
        cached_positions[ticker] = new_qty


# =============================================================================
# CORE EXECUTION
# =============================================================================
async def execute_arb(
    arb,              # ArbOpportunity with all fields populated
    session,          # aiohttp session
    kalshi_api,       # KalshiAPI instance
    pm_api,           # PolymarketUSAPI instance
    pm_slug: str,     # PM market slug
    pm_outcome_idx: int,  # PM outcome index (usually 0)
    size: int = 1,    # Number of contracts (from depth-aware sizing)
    k_book_ref: Optional[Dict] = None,  # Live Kalshi book ref for GTC spread monitoring
    omi_cache=None,   # OmiSignalCache instance for Tier 3 directional decisions
    opposite_info: Optional[Dict] = None,  # {team, ticker, ask, ask_size} for cross-hedge
    pm_data_age_ms: int = 0,  # Age of PM WS data at detection time (for no-fill diagnostics)
    pm_prices: Optional[Dict] = None,  # WS-updated PM price dict for BBO refresh
) -> TradeResult:
    """
    Execute a hedged arb trade with dynamic sizing.
    Returns TradeResult with status, fills, and details.

    EXECUTION ORDER: PM FIRST, THEN KALSHI
    - PM is the unreliable leg (IOC orders often expire)
    - Kalshi is the reliable leg (fills consistently)
    - Cases 1/2: SELL YES, Cases 3/4: BUY YES
    - If PM doesn't fill → exit cleanly with no position
    - If PM fills but Kalshi doesn't → unhedged (rare, logged)

    Safety guarantees:
    1. In-memory position/blacklist check (no API calls)
    2. pm_long_team verified at WS level (price mismatch check in _handle_market_data)
    3. PM first (unreliable), Kalshi only if PM fills (reliable)
    4. Size governed by depth-aware sizing algorithm
    5. Phantom spread rejection (>90c)
    6. All 4 trade cases handled explicitly via TRADE_PARAMS lookup
    """
    start_time = time.time()
    game_id = arb.game  # Kalshi game_id format
    gtc_phase = None  # Set in Phase 2 if GTC is attempted

    # Hard cap: prevent sizing bugs from sending oversized orders
    if size > Config.max_contracts:
        print(f"[EXEC] SIZE CAP: {size} -> {Config.max_contracts} (max_contracts)")
        size = Config.max_contracts

    # -------------------------------------------------------------------------
    # Step 1: Safety checks (in-memory only — no API calls on hot path)
    # -------------------------------------------------------------------------
    safe, reason = safe_to_trade(arb.kalshi_ticker, game_id)
    if not safe:
        return TradeResult(success=False, abort_reason=f"Safety: {reason}")

    # -------------------------------------------------------------------------
    # Step 1b: pm_long_team guard — REFUSE to trade if mapping is missing
    # -------------------------------------------------------------------------
    # Root cause of Feb 27 wrong-side trades: stale verified_mappings.json had
    # no UFC entries, so pm_long_team was empty string. This caused is_long_team
    # to always be False, routing BUY_K_SELL_PM to Case 4 (BUY_LONG intent=1)
    # instead of Case 3 (BUY_SHORT intent=3), buying SAME side on both exchanges.
    if not arb.pm_long_team:
        print(
            f"[GUARD] REFUSING to trade {arb.game} {arb.team}: "
            f"pm_long_team is empty/None! Mapping is missing or stale. "
            f"Cannot determine correct PM trade direction.",
            flush=True
        )
        return TradeResult(
            success=False,
            abort_reason=f"pm_long_team is empty for {arb.game} — mapping missing or stale, cannot determine PM trade side"
        )

    # NOTE: traded_games is only updated AFTER PM fills (see Step 5.5 below).
    # This allows retries on PM_NO_FILL — the game stays tradeable.

    # -------------------------------------------------------------------------
    # Step 2: Phantom spread check
    # -------------------------------------------------------------------------
    # Recalculate spread from current prices using CORRECT formula
    # For underdog, pm_bid/pm_ask are already inverted in cache
    is_long_team = (arb.team == arb.pm_long_team)

    if arb.direction == 'BUY_PM_SELL_K':
        # K: SELL YES at k_bid, PM: buy at pm_ask
        # Both cases use k_bid - pm_ask (pm_ask is already correct for the team)
        spread = arb.k_bid - arb.pm_ask
    else:  # BUY_K_SELL_PM
        # K: BUY YES at k_ask, PM: sell via BUY_SHORT or BUY_LONG
        # Both cases use pm_bid - k_ask
        spread = arb.pm_bid - arb.k_ask

    # For low-priced markets, high spreads can be legitimate
    # e.g., K ask=8c + PM ask=11c = 19c total, 81c profit is real
    if spread > 90:  # Only reject clearly impossible spreads
        return TradeResult(success=False, abort_reason=f"Phantom spread: {spread}c > 90c max")

    # ── SPREAD CEILING: reject spreads that indicate pm_long_team mapping errors ──
    # Real arbs: 2-7c. Anything > 20c is almost certainly a price frame inversion
    # where PM prices are stored in the wrong team's frame (e.g., ALA-TENN bug:
    # spread=33c because pm_bid was TENN's raw price, not ALA's inverted price).
    MAX_CREDIBLE_SPREAD = 20
    if spread > MAX_CREDIBLE_SPREAD:
        print(f"[SPREAD_GATE] REJECT {arb.team}: spread={spread:.0f}c > {MAX_CREDIBLE_SPREAD}c ceiling. "
              f"Likely pm_long_team inversion | "
              f"pm_bid={arb.pm_bid}c pm_ask={arb.pm_ask}c "
              f"k_bid={arb.k_bid}c k_ask={arb.k_ask}c | "
              f"pm_long_team={arb.pm_long_team} is_long_team={is_long_team} "
              f"dir={arb.direction} | slug={arb.pm_slug}", flush=True)
        return TradeResult(success=False, abort_reason=f"Spread {spread:.0f}c > {MAX_CREDIBLE_SPREAD}c ceiling — likely mapping error")

    # ── COMBINED COST GATE: tighter check on expected entry cost ──
    # For a valid arb, combined cost = 100 - spread (e.g., 4c spread → 96c combined).
    # Block if outside 90-102c range (spread > 10c or negative arb).
    expected_combined = 100 - spread
    if expected_combined < 90 or expected_combined > 102:
        print(f"[COST_GATE] REJECT {arb.team}: expected combined={expected_combined:.0f}c "
              f"(outside 90-102c range) | spread={spread:.0f}c | "
              f"k_bid={arb.k_bid}c k_ask={arb.k_ask}c pm_bid={arb.pm_bid}c pm_ask={arb.pm_ask}c | "
              f"dir={arb.direction}", flush=True)
        return TradeResult(success=False,
            abort_reason=f"Combined cost {expected_combined:.0f}c outside 90-102c range")

    # -------------------------------------------------------------------------
    # Step 3: Look up trade params
    # -------------------------------------------------------------------------
    # is_long_team already calculated above in phantom spread check
    key = (arb.direction, is_long_team)

    if key not in TRADE_PARAMS:
        return TradeResult(success=False, abort_reason=f"Unknown trade key: {key}")

    params = TRADE_PARAMS[key]

    # Check if this case is executable on PM
    if not params.get('executable', True):
        return TradeResult(
            success=False,
            abort_reason=f"Non-executable: {arb.direction} with is_long_team={is_long_team} requires shorting PM (no liquidity)"
        )

    # -------------------------------------------------------------------------
    # Step 4: Calculate prices
    # -------------------------------------------------------------------------
    # Kalshi price (in cents)
    k_price = getattr(arb, params['k_price_field'])

    # PM price (in dollars) with buffer for slippage protection
    pm_price_cents = getattr(arb, params['pm_price_field'])

    # pm_invert_price: convert from our team's bid to the other team's ask
    # Case 3: 100 - long_bid = underdog cost, Case 4: 100 - underdog_bid = favorite ask
    if params.get('pm_invert_price', False):
        pm_price_cents = 100 - pm_price_cents

    # PM buffer: controls how far past BBO we're willing to pay for PM IOC fill.
    # Buffer eats directly into profit — every cent of buffer = 1c less net P&L.
    # K fee is 2c, so spread must cover: buffer + 2c K fee + profit target.
    # Example: 4c spread, 1c buffer → gross=3c, -2c K fee → 1c net profit.
    # Old 3c min buffer made 4-5c spreads breakeven ($0 net after fees).
    if spread >= 10:
        pm_buffer = max(3, math.ceil(spread * 0.40))
    elif spread >= 6:
        pm_buffer = max(2, math.ceil(spread * 0.30))
    else:
        # Tight spreads (4-5c): 1c buffer preserves profit margin
        # PM IOC fills at or near L1 — 1c is enough to cross the spread
        pm_buffer = 1

    print(f"[EXEC] Sized: {size} contracts | buffer: {pm_buffer}c")

    if params.get('pm_is_buy_short', False):
        # BUY_SHORT: PM interprets price as MINIMUM YES SELL price (always YES-frame)
        # pm_price_cents = underdog cost (after pm_invert_price conversion)
        # Buffer adds to underdog cost (willing to pay slightly more for fill)
        # Convert to YES frame: min_sell = 100 - max_cost (lower sell = more aggressive)
        max_underdog_cost = min(math.ceil(pm_price_cents + pm_buffer), 99)
        pm_price = max(100 - max_underdog_cost, 1) / 100.0  # YES-frame price
    else:
        # BUY_LONG: PM interprets price as MAX YES buy price (favorite frame)
        pm_price_buffered = min(math.ceil(pm_price_cents + pm_buffer), 99)
        pm_price = pm_price_buffered / 100.0

    # Add buffer to Kalshi price for better fill
    if params['k_action'] == 'sell':
        k_limit_price = max(k_price - Config.price_buffer_cents, 1)
    else:  # buy
        k_limit_price = min(k_price + Config.price_buffer_cents, 99)

    # Depth pre-check removed — tier system handles Kalshi failures cheaply

    # -------------------------------------------------------------------------
    # Step 4.5: Pre-flight Kalshi validation (zero-cost, prevents PM risk)
    # -------------------------------------------------------------------------
    if k_book_ref is not None:
        k_best_bid = k_book_ref.get('best_bid', 0)
        k_best_ask = k_book_ref.get('best_ask', 0)
        # Check book has valid prices (ticker is active and tradeable)
        if not k_best_bid and not k_best_ask:
            return TradeResult(
                success=False,
                abort_reason=f"Pre-flight: Kalshi book empty for {arb.kalshi_ticker} (inactive/untradeable)",
            )
        # Check our limit price isn't wildly out of range
        if params['k_action'] == 'sell' and k_best_bid:
            if k_limit_price > k_best_bid + 5:
                return TradeResult(
                    success=False,
                    abort_reason=f"Pre-flight: K sell price {k_limit_price}c > best_bid {k_best_bid}c + 5c buffer",
                )
        elif params['k_action'] == 'buy' and k_best_ask:
            if k_limit_price < k_best_ask - 5:
                return TradeResult(
                    success=False,
                    abort_reason=f"Pre-flight: K buy price {k_limit_price}c < best_ask {k_best_ask}c - 5c buffer",
                )
    else:
        # No book reference at all — cannot validate Kalshi side
        return TradeResult(
            success=False,
            abort_reason=f"Pre-flight: No Kalshi book data for {arb.kalshi_ticker}",
        )

    # -------------------------------------------------------------------------
    # Step 4b: K depth gate — skip if Kalshi L1 too thin for reliable fill
    # -------------------------------------------------------------------------
    if params['k_action'] == 'sell':
        k_l1_depth = k_book_ref.get('best_bid_size', 0) if k_book_ref else 0
    else:
        k_l1_depth = k_book_ref.get('best_ask_size', 0) if k_book_ref else 0

    if k_l1_depth < MIN_K_DEPTH_L1:
        print(f"[DEPTH_GATE] SKIP {arb.team}: K L1 depth {k_l1_depth} < {MIN_K_DEPTH_L1}", flush=True)
        on_execution_crash(game_id)
        return TradeResult(
            success=False,
            abort_reason=f"k_depth_gate: K L1 depth {k_l1_depth} < {MIN_K_DEPTH_L1}",
        )

    # -------------------------------------------------------------------------
    # Step 5: Place PM order FIRST (unreliable leg - IOC often expires)
    # -------------------------------------------------------------------------
    # Snapshot pre-order BBO for no-fill diagnostics
    # arb.pm_bid/pm_ask were refreshed by the WS handler's confirm_pm_price_fresh()
    # These are in the team's own frame (already inverted for underdog)
    _pre_order_bbo = {
        'bid_cents': arb.pm_bid,
        'ask_cents': arb.pm_ask,
        'bid_size': arb.pm_bid_size,
        'ask_size': arb.pm_ask_size,
    }

    # Outcome index: most cases trade on their own team's outcome.
    # Only Case 4 (BUY_K_SELL_PM, underdog) switches to the long team's outcome
    # because we BUY_LONG on the long team to SHORT our underdog.
    actual_pm_outcome_idx = (1 - pm_outcome_idx) if params.get('pm_switch_outcome', False) else pm_outcome_idx

    # ── PRE-ORDER DEBUG LOG ──
    _, _pm_yes = _yes_teams(arb.team, params['k_action'], arb.cache_key)
    _intent_label = f"YES {_pm_yes}"
    _case_num = '3' if (arb.direction == 'BUY_K_SELL_PM' and is_long_team) else \
                '4' if (arb.direction == 'BUY_K_SELL_PM' and not is_long_team) else \
                '1' if (arb.direction == 'BUY_PM_SELL_K' and is_long_team) else '2'
    print(f"[PM_ORDER] Case {_case_num}: {_intent_label} {size}@${pm_price:.4f} "
          f"outcome[{actual_pm_outcome_idx}] | "
          f"team={arb.team} is_long={is_long_team} dir={arb.direction} | "
          f"pm_bid={arb.pm_bid}c pm_ask={arb.pm_ask}c | "
          f"spread={spread:.1f}c buf={pm_buffer}c | slug={pm_slug[:50]}")

    pm_order_start = time.time()

    # ── GTC-ONLY MODE: Skip IOC entirely, go straight to maker order ──
    # When enable_gtc=True, IOC taker fills eat the margin on thin spreads.
    # GTC maker at 0% PM fee is the only path that's profitable for 2-4c spreads.
    _gtc_only_filled = False
    if Config.enable_gtc and k_book_ref is not None:
        print(f"[EXEC] GTC-ONLY: Skipping IOC, placing maker order {size}@${pm_price:.2f}")
        gtc_phase = await _execute_gtc_phase(
            session=session, pm_api=pm_api, pm_slug=pm_slug,
            pm_intent=params['pm_intent'], pm_price=pm_price,
            size=size, outcome_index=actual_pm_outcome_idx,
            k_book_ref=k_book_ref, direction=arb.direction,
            game_id=game_id,
        )
        if gtc_phase['filled'] > 0:
            # GTC got fills — set vars and skip IOC, fall through to Step 5.5 + Step 6
            pm_filled = gtc_phase['filled']
            pm_fill_price = gtc_phase['fill_price'] or pm_price
            pm_order_ms = int((time.time() - pm_order_start) * 1000)
            pm_response_details = {
                'pm_response_status': 200,
                'pm_response_body': f"GTC filled {pm_filled}/{size}",
                'pm_fill_price': pm_fill_price,
                'pm_fill_qty': pm_filled,
                'pm_order_id': gtc_phase['order_id'],
                'pm_expiry_reason': None,
            }
            _gtc_only_filled = True
            print(f"[EXEC] GTC MAKER FILL: {pm_filled}x @${pm_fill_price:.2f} (0% PM fee)")
        else:
            # GTC didn't fill — return immediately
            execution_time_ms = int((time.time() - start_time) * 1000)
            return TradeResult(
                success=False, pm_filled=0, pm_price=pm_price,
                abort_reason=f"PM: GTC no fill ({gtc_phase['cancel_reason']})",
                pm_order_ms=int((time.time() - pm_order_start) * 1000),
                execution_time_ms=execution_time_ms,
                pm_response_details={},
                execution_phase="gtc",
                gtc_rest_time_ms=gtc_phase['rest_time_ms'],
                gtc_spread_checks=gtc_phase['spread_checks'],
                gtc_cancel_reason=gtc_phase['cancel_reason'],
            )

    # Initialize variables
    k_filled = 0
    k_fill_price = k_price
    k_order_ms = 0

    # ── PM-FIRST IOC: Send PM (unreliable leg) then K (reliable leg) ──
    # Monte Carlo: PM-first Sharpe 1.80 vs K-first 0.07. PM no-fill = $0 clean abort.
    # K no-fill after PM fills → Tier 1/2/3 recovery (PM unwind capped at spread).
    if not _gtc_only_filled:
        pm_order_start = time.time()
        try:
            pm_result = await asyncio.wait_for(
                pm_api.place_order(session, pm_slug, params['pm_intent'], pm_price,
                    size, tif=3, sync=True, outcome_index=actual_pm_outcome_idx),
                timeout=5.0)
        except asyncio.TimeoutError:
            pm_order_ms = int((time.time() - pm_order_start) * 1000)
            print(f"[PM_FIRST] PM IOC timeout ({pm_order_ms}ms) — clean abort, $0 cost")
            pm_result = {'fill_count': 0, 'error': 'timeout'}
        except Exception as e:
            pm_order_ms = int((time.time() - pm_order_start) * 1000)
            print(f"[PM_FIRST] PM IOC error: {e} — clean abort, $0 cost")
            pm_result = {'fill_count': 0, 'error': str(e)}

        pm_filled = pm_result.get('fill_count', 0)
        pm_fill_price = pm_result.get('fill_price', pm_price)
        pm_order_ms = int((time.time() - pm_order_start) * 1000)
        pm_response_details = _extract_pm_response_details(pm_result)

        if pm_filled == 0:
            # PM didn't fill — CLEAN ABORT. No position, no risk, $0 cost.
            print(f"[PM_FIRST] PM no-fill ({pm_order_ms}ms) — clean abort, no position taken")
            return TradeResult(
                success=False, pm_filled=0,
                abort_reason=f"PM no-fill (PM-first): clean abort, $0 cost",
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_order_ms=pm_order_ms,
                pm_response_details=pm_response_details,
                execution_phase="ioc",
                nofill_diagnosis={
                    'sequence': 'PM_FIRST',
                    'pm_latency_ms': pm_order_ms,
                    'pm_price_sent': pm_price,
                    'pm_intent': params['pm_intent'],
                    'pre_order_bbo': _pre_order_bbo,
                    'pm_data_age_ms': pm_data_age_ms,
                },
            )

        print(f"[PM_FIRST] PM filled {pm_filled}x @${pm_fill_price:.4f} in {pm_order_ms}ms — placing K...")

        # Refresh K limit price after PM latency (150-250ms K book may shift)
        if k_book_ref:
            live_bid = k_book_ref.get('best_bid')
            live_ask = k_book_ref.get('best_ask')
            if live_bid and live_ask:
                old_k_limit = k_limit_price
                if params['k_action'] == 'sell':
                    k_limit_price = max(live_bid - Config.price_buffer_cents, 1)
                else:
                    k_limit_price = min(live_ask + Config.price_buffer_cents, 99)
                if k_limit_price != old_k_limit:
                    print(f"[PM_FIRST] K price refreshed: {old_k_limit}c -> {k_limit_price}c "
                          f"(live bid={live_bid} ask={live_ask})")

        # k_filled stays 0 — falls through to Step 6 (K order placement)

    # Step 5.5: PM filled — NOW lock the game to prevent duplicate trades
    # -------------------------------------------------------------------------
    traded_games.add(game_id)

    # -------------------------------------------------------------------------
    # Step 5.75: Final spread recheck after GTC fill (before Kalshi order)
    # -------------------------------------------------------------------------
    if gtc_phase is not None and gtc_phase['filled'] > 0 and k_book_ref:
        spread_ok, current_spread = check_kalshi_spread_live(
            k_book_ref, arb.direction, pm_fill_price * 100
        )
        if not spread_ok:
            print(f"[GTC] Spread gone before K order ({current_spread}c), unwinding PM...")
            original_intent = params['pm_intent']
            reverse_intent = REVERSE_INTENT[original_intent]
            unwind_filled, unwind_fill_price = await _unwind_pm_position(
                session, pm_api, pm_slug, reverse_intent,
                pm_fill_price * 100, pm_filled, actual_pm_outcome_idx,
            )
            exited = unwind_filled > 0
            unwind_loss = None
            unwind_pnl = None
            if exited and unwind_fill_price is not None:
                if reverse_intent == 2:  # Selling long: profit = sell - buy
                    pnl_per = (unwind_fill_price * 100) - (pm_fill_price * 100)
                else:  # reverse_intent == 4: Closing short: profit = original_sell - buyback
                    pnl_per = (pm_fill_price * 100) - (unwind_fill_price * 100)
                unwind_pnl = pnl_per * unwind_filled
                unwind_loss = abs(unwind_pnl)
                pnl_label = "gain" if unwind_pnl > 0 else "loss"
                print(f"[GTC] Unwind {pnl_label}: {abs(pnl_per):.1f}c x {unwind_filled} = {abs(unwind_pnl):.1f}c total (+ fees)")
            if not exited:
                print(f"[GTC] PM unwind failed - position remains open!")
            return TradeResult(
                success=False, pm_filled=pm_filled,
                pm_price=pm_fill_price,
                unhedged=not exited,
                abort_reason=f"GTC filled but K spread gone, PM unwound ({pnl_label}: {abs(unwind_pnl):.1f}c)" if exited and unwind_pnl is not None else "GTC filled but K spread gone, PM unwind FAILED - UNHEDGED!" if not exited else "GTC filled but K spread gone, PM unwound",
                pm_order_ms=pm_order_ms,
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_response_details=pm_response_details,
                execution_phase="gtc", is_maker=True,
                gtc_rest_time_ms=gtc_phase['rest_time_ms'],
                gtc_spread_checks=gtc_phase['spread_checks'],
                gtc_cancel_reason='spread_gone_pre_kalshi',
                exited=exited,
                unwind_loss_cents=unwind_loss,
                unwind_pnl_cents=unwind_pnl,
                unwind_fill_price=unwind_fill_price if exited else None,
                unwind_qty=unwind_filled if exited else 0,
            )

    # -------------------------------------------------------------------------
    # Step 5.9: Refresh K limit price from LIVE book (critical for GTC)
    # -------------------------------------------------------------------------
    # After GTC rest (up to 3s), the original k_limit_price is stale.
    # Read current K best bid/ask and recompute limit price.
    if gtc_phase is not None and gtc_phase['filled'] > 0 and k_book_ref:
        live_bid = k_book_ref.get('best_bid')
        live_ask = k_book_ref.get('best_ask')
        if live_bid and live_ask:
            old_k_limit = k_limit_price
            if params['k_action'] == 'sell':
                k_limit_price = max(live_bid - Config.price_buffer_cents, 1)
            else:  # buy
                k_limit_price = min(live_ask + Config.price_buffer_cents, 99)
            if k_limit_price != old_k_limit:
                print(f"[GTC] K price refreshed: {old_k_limit}c → {k_limit_price}c (live bid={live_bid} ask={live_ask})")

    # -------------------------------------------------------------------------
    # Step 6: Kalshi order (already filled in K-first mode, placed here in PM-first/GTC)
    # -------------------------------------------------------------------------
    if k_filled > 0:
        traded_games.add(game_id)
        execution_time_ms = int((time.time() - start_time) * 1000)
        _check_hedge_coherence(
            arb.team, k_fill_price, pm_fill_price,
            params['k_action'], params.get('pm_is_buy_short', False),
            arb.direction, arb.pm_long_team, is_long_team,
            cache_key=arb.cache_key)
        await _verify_both_legs(session, kalshi_api, pm_api,
                                arb.kalshi_ticker, pm_slug, arb.team, k_filled, pm_filled)
        print(f"[PM_FIRST] SUCCESS: K={k_filled}x@{k_fill_price}c PM={pm_filled}x@${pm_fill_price:.4f} "
              f"total={execution_time_ms}ms (k={k_order_ms}ms pm={pm_order_ms}ms)")
        return TradeResult(
            success=True,
            kalshi_filled=k_filled,
            pm_filled=pm_filled,
            kalshi_price=k_fill_price,
            pm_price=pm_fill_price,
            execution_time_ms=execution_time_ms,
            pm_order_ms=pm_order_ms,
            k_order_ms=k_order_ms,
            pm_response_details=pm_response_details,
            execution_phase="ioc",
            tier="PM_FIRST_SUCCESS",
        )
    k_order_start = time.time()
    try:
        k_result = await kalshi_api.place_order(
            session,
            arb.kalshi_ticker,
            params['k_side'],      # 'yes' or 'no'
            params['k_action'],    # 'sell'
            pm_filled,             # Match PM's actual fill count
            k_limit_price
        )
    except Exception as e:
        # KALSHI EXCEPTION - Attempt to unwind PM position
        k_exception_str = str(e)
        k_traceback = traceback.format_exc()
        print(f"[RECOVERY] Kalshi exception: {k_exception_str} - unwinding PM position...")
        on_execution_crash(game_id)

        # Log to persistent file
        _log_kalshi_error(arb.kalshi_ticker, k_limit_price, params['k_action'],
                          params['k_side'], pm_filled, k_exception_str, k_traceback)

        k_err_details = {
            'k_exception': k_exception_str,
            'k_traceback': k_traceback,
            'k_limit_price_sent': k_limit_price,
            'k_original_price': k_price,
            'k_action': params['k_action'],
            'k_side': params['k_side'],
            'k_count': pm_filled,
        }

        # Try to unwind PM position (10c buffer, then 25c desperation)
        original_intent = params['pm_intent']
        reverse_intent = REVERSE_INTENT[original_intent]
        unwind_filled, unwind_fill_price = await _unwind_pm_position(
            session, pm_api, pm_slug, reverse_intent,
            pm_fill_price * 100, pm_filled, actual_pm_outcome_idx,
        )

        if unwind_filled > 0:
            if reverse_intent == 2:  # Selling long: profit = sell - buy
                pnl_per = (unwind_fill_price - pm_fill_price) * 100
            else:  # reverse_intent == 4: Closing short: profit = original_sell - buyback
                pnl_per = (pm_fill_price - unwind_fill_price) * 100
            unwind_pnl = pnl_per * unwind_filled
            loss_cents = abs(unwind_pnl)
            pnl_label = "gain" if unwind_pnl > 0 else "loss"
            return TradeResult(
                success=False, kalshi_filled=0, pm_filled=pm_filled,
                kalshi_price=k_limit_price, pm_price=pm_fill_price,
                unhedged=False,
                abort_reason=f"Kalshi exception: {k_exception_str} | PM unwound ({pnl_label}: {abs(pnl_per):.1f}c x {unwind_filled} = {loss_cents:.1f}c)",
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_order_ms=pm_order_ms, k_order_ms=0,
                pm_response_details=pm_response_details,
                k_response_details=k_err_details,
                execution_phase="gtc" if (gtc_phase and gtc_phase.get('filled', 0) > 0) else "ioc",
                gtc_rest_time_ms=gtc_phase['rest_time_ms'] if gtc_phase else 0,
                gtc_spread_checks=gtc_phase['spread_checks'] if gtc_phase else 0,
                gtc_cancel_reason=gtc_phase.get('cancel_reason', '') if gtc_phase else '',
                is_maker=bool(gtc_phase and gtc_phase.get('is_maker', False)),
                exited=True,
                unwind_loss_cents=loss_cents,
                unwind_pnl_cents=unwind_pnl,
                unwind_fill_price=unwind_fill_price,
                unwind_qty=unwind_filled,
                tier="TIER3_UNWIND",
            )

        # Unwind failed — register unhedged exposure
        pm_cost_cents = int(pm_fill_price * 100) * pm_filled
        register_unhedged(arb.kalshi_ticker, pm_cost_cents)
        return TradeResult(
            success=False,
            kalshi_filled=0,
            pm_filled=pm_filled,
            kalshi_price=k_limit_price,
            pm_price=pm_fill_price,
            unhedged=True,
            abort_reason=f"Kalshi exception: {k_exception_str} | PM unwind failed - UNHEDGED!",
            execution_time_ms=int((time.time() - start_time) * 1000),
            pm_order_ms=pm_order_ms,
            k_order_ms=0,
            pm_response_details=pm_response_details,
            k_response_details=k_err_details,
            execution_phase="gtc" if (gtc_phase and gtc_phase.get('filled', 0) > 0) else "ioc",
            gtc_rest_time_ms=gtc_phase['rest_time_ms'] if gtc_phase else 0,
            gtc_spread_checks=gtc_phase['spread_checks'] if gtc_phase else 0,
            gtc_cancel_reason=gtc_phase.get('cancel_reason', '') if gtc_phase else '',
            is_maker=bool(gtc_phase and gtc_phase.get('is_maker', False)),
            tier="TIER3_UNWIND",
        )

    k_order_ms = int((time.time() - k_order_start) * 1000)
    k_filled = k_result.get('fill_count', 0)
    k_fill_price = k_result.get('fill_price', k_price)

    # Update local position cache (no API call needed)
    if k_filled > 0:
        qty_delta = -k_filled if params['k_action'] == 'sell' else k_filled
        update_position_cache_after_trade(arb.kalshi_ticker, qty_delta)

    # -------------------------------------------------------------------------
    # Step 7: Kalshi IOC failed — tiered recovery (all IOC, no GTC/polling)
    # Tier 1: Hedge at wider Kalshi price if arb still exists
    # Tier 2: Close PM via SDK if position is in the money
    # Tier 3: Fallback to existing PM unwind (SDK close_position + manual)
    # -------------------------------------------------------------------------
    if k_filled == 0:
        # ── Diagnostic: log Kalshi failure context ──
        k_status = k_result.get('status', '?')
        k_error = k_result.get('error', '')
        k_order_id = k_result.get('order_id', 'none')
        # Check price staleness: current book vs sent price
        k_stale_info = ""
        if k_book_ref:
            if params['k_action'] == 'sell':
                cur_bid = k_book_ref.get('best_bid', 0)
                if cur_bid and cur_bid < k_limit_price:
                    k_stale_info = f" STALE: bid moved {cur_bid}c < sent {k_limit_price}c"
            else:
                cur_ask = k_book_ref.get('best_ask', 0)
                if cur_ask and cur_ask > k_limit_price:
                    k_stale_info = f" STALE: ask moved {cur_ask}c > sent {k_limit_price}c"
        print(f"[KALSHI FAIL] {arb.kalshi_ticker}: {params['k_action']} {params['k_side']} "
              f"{pm_filled}x @ {k_limit_price}c | status={k_status} | order={k_order_id} | "
              f"pm_latency={pm_order_ms}ms k_latency={k_order_ms}ms | "
              f"original_k_price={k_price}c{k_stale_info}")
        if k_error:
            print(f"[KALSHI FAIL] Error: {k_error}")

        _k_response_details = {
            'k_status': k_status,
            'k_error': k_error,
            'k_order_id': k_order_id,
            'k_limit_price_sent': k_limit_price,
            'k_original_price': k_price,
            'k_stale_info': k_stale_info.strip() if k_stale_info else None,
            'pm_latency_ms': pm_order_ms,
            'k_latency_ms': k_order_ms,
            'k_full_response': k_result,
        }

        # Compute values used across all tiers
        pm_fill_price_cents = pm_fill_price * 100
        original_intent = params['pm_intent']
        reverse_intent = REVERSE_INTENT[original_intent]
        # Normalize to effective PM cost: BUY_LONG cost = fill price,
        # BUY_SHORT cost = 100 - fill price (underdog cost)
        is_buy_short = params.get('pm_is_buy_short', False)
        pm_cost_cents = (100 - pm_fill_price_cents) if is_buy_short else pm_fill_price_cents
        _exec_phase = "gtc" if (gtc_phase and gtc_phase.get('filled', 0) > 0) else "ioc"
        _gtc_rest = gtc_phase['rest_time_ms'] if gtc_phase else 0
        _gtc_checks = gtc_phase['spread_checks'] if gtc_phase else 0
        _gtc_cancel = gtc_phase.get('cancel_reason', '') if gtc_phase else ''
        _is_maker = bool(gtc_phase and gtc_phase.get('is_maker', False))

        # ── TIER 1: Kalshi IOC at wider price if arb still exists ──
        wider_price = _find_kalshi_wider_price(
            k_book_ref, params['k_action'], k_limit_price,
            pm_filled, pm_cost_cents, arb.direction,
        )
        if wider_price is not None:
            k_fee = _kalshi_fee_cents(wider_price)
            pm_fee = math.ceil(pm_cost_cents * 0.001)
            if arb.direction == 'BUY_PM_SELL_K':
                wider_spread = wider_price - pm_cost_cents
            else:
                wider_spread = (100 - pm_cost_cents) - wider_price
            net_spread = wider_spread - k_fee - pm_fee
            concession = abs(wider_price - k_limit_price)
            print(f"[TIER] Kalshi IOC failed. Checking Tier 1: wider arb at {wider_price}c "
                  f"(spread {net_spread:.0f}c net of fees, concession {concession}c) -> placing IOC")

            try:
                t1_result = await kalshi_api.place_order(
                    session, arb.kalshi_ticker,
                    params['k_side'], params['k_action'],
                    pm_filled, wider_price,
                    time_in_force='immediate_or_cancel'
                )
                t1_filled = t1_result.get('fill_count', 0)
                t1_fill_price = t1_result.get('fill_price', wider_price)
            except Exception as e:
                print(f"[TIER] Tier 1 Kalshi IOC exception: {e}")
                t1_filled = 0
                t1_fill_price = wider_price

            if t1_filled > 0:
                k_filled = t1_filled
                k_fill_price = t1_fill_price
                k_order_ms = int((time.time() - k_order_start) * 1000)

                # Update position cache for Tier 1 fills
                qty_delta = -k_filled if params['k_action'] == 'sell' else k_filled
                update_position_cache_after_trade(arb.kalshi_ticker, qty_delta)

                if t1_filled >= pm_filled:
                    actual_cost = abs(t1_fill_price - k_limit_price)
                    _check_hedge_coherence(
                        arb.team, t1_fill_price, pm_fill_price,
                        params['k_action'], params.get('pm_is_buy_short', False),
                        arb.direction, arb.pm_long_team, is_long_team,
                        cache_key=arb.cache_key)
                    await _verify_both_legs(session, kalshi_api, pm_api,
                                            arb.kalshi_ticker, pm_slug, arb.team, k_filled, pm_filled)
                    print(f"[TIER] Tier 1 SUCCESS: hedged {t1_filled}/{pm_filled} @ {t1_fill_price}c "
                          f"(concession {actual_cost}c, net spread {net_spread:.0f}c)")
                    return TradeResult(
                        success=True,
                        kalshi_filled=k_filled,
                        pm_filled=pm_filled,
                        kalshi_price=k_fill_price,
                        pm_price=pm_fill_price,
                        unhedged=False,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        pm_order_ms=pm_order_ms,
                        k_order_ms=k_order_ms,
                        pm_response_details=pm_response_details,
                        k_response_details=_k_response_details,
                        execution_phase=_exec_phase,
                        gtc_rest_time_ms=_gtc_rest,
                        gtc_spread_checks=_gtc_checks,
                        gtc_cancel_reason=_gtc_cancel,
                        is_maker=_is_maker,
                        tier="TIER1_HEDGE",
                    )
                # Partial Tier 1 fill — fall through to Step 7.5
                print(f"[TIER] Tier 1 partial: {t1_filled}/{pm_filled}, falling through to partial handler")
            else:
                print(f"[TIER] Tier 1 failed: Kalshi IOC at {wider_price}c got no fill")
        else:
            print(f"[TIER] Kalshi IOC failed. Tier 1 skipped: no wider arb exists in book")

    # Recompute elapsed after potential Tier 1
    elapsed_ms = int((time.time() - start_time) * 1000)

    if k_filled == 0:
        # Tier 1 failed or skipped — try Tier 2 (PM SDK close)
        # ── TIER 2: Close PM via SDK if position is in the money ──
        t2_attempted = False
        try:
            bbo = await pm_api.get_bbo(pm_slug)
            bbo_bid = bbo.get('bid')
            bbo_ask = bbo.get('ask')
            if bbo_bid is not None and bbo_ask is not None:
                # BBO is in long-team frame (outcome 0). If our position is on
                # outcome 1 (underdog), invert to get underdog's BBO.
                if actual_pm_outcome_idx != 0:
                    bbo_bid, bbo_ask = 100 - bbo_ask, 100 - bbo_bid
                # Determine if PM position is closeable near breakeven.
                # Intent 1/4 (long YES): close by selling at bid. P&L = bid - fill_price.
                # Intent 2/3 (short YES): close by buying at ask. P&L = fill_price - ask.
                if original_intent in (1, 4):
                    pm_close_pnl_cents = bbo_bid - pm_fill_price_cents
                    close_price_label = f"BBO bid {bbo_bid}c"
                else:
                    pm_close_pnl_cents = pm_fill_price_cents - bbo_ask
                    close_price_label = f"BBO ask {bbo_ask}c"

                if pm_close_pnl_cents >= -1:  # Allow up to 1c loss per contract
                    print(f"[TIER] Tier 1 failed. Checking Tier 2: PM position closeable "
                          f"(fill {pm_fill_price_cents:.0f}c, {close_price_label}, "
                          f"P&L {pm_close_pnl_cents:+.0f}c/contract) -> closing via SDK")
                    t2_attempted = True
                    try:
                        close_resp = await pm_api.close_position(session, pm_slug, outcome_index=actual_pm_outcome_idx)
                        # Parse close_position response
                        t2_cum_qty = close_resp.get('cumQuantity', 0)
                        if isinstance(t2_cum_qty, str):
                            t2_cum_qty = int(t2_cum_qty) if t2_cum_qty else 0
                        t2_avg_px = close_resp.get('avgPx')
                        if isinstance(t2_avg_px, dict):
                            t2_fill_price = float(t2_avg_px.get('value', 0)) if t2_avg_px.get('value') else None
                        elif t2_avg_px is not None:
                            t2_fill_price = float(t2_avg_px) if t2_avg_px else None
                        else:
                            t2_fill_price = None

                        if t2_cum_qty >= pm_filled and t2_fill_price is not None:
                            if original_intent in (1, 4):
                                pnl_per = (t2_fill_price * 100) - pm_fill_price_cents
                            else:
                                pnl_per = pm_fill_price_cents - (t2_fill_price * 100)
                            total_pnl = pnl_per * pm_filled
                            print(f"[TIER] Tier 2 SUCCESS: closed {t2_cum_qty} @ ${t2_fill_price:.4f} "
                                  f"(P&L {pnl_per:+.1f}c/contract, total {total_pnl:+.1f}c)")
                            return TradeResult(
                                success=False,
                                kalshi_filled=0,
                                pm_filled=pm_filled,
                                kalshi_price=k_limit_price,
                                pm_price=pm_fill_price,
                                unhedged=False,
                                abort_reason=f"Kalshi failed, PM closed via SDK (P&L {total_pnl:+.1f}c)",
                                execution_time_ms=int((time.time() - start_time) * 1000),
                                pm_order_ms=pm_order_ms,
                                k_order_ms=k_order_ms,
                                pm_response_details=pm_response_details,
                                k_response_details=_k_response_details,
                                execution_phase=_exec_phase,
                                gtc_rest_time_ms=_gtc_rest,
                                gtc_spread_checks=_gtc_checks,
                                gtc_cancel_reason=_gtc_cancel,
                                is_maker=_is_maker,
                                exited=True,
                                unwind_loss_cents=abs(total_pnl) if total_pnl < 0 else 0,
                                unwind_fill_price=t2_fill_price,
                                unwind_qty=t2_cum_qty,
                                tier="TIER2_EXIT",
                            )
                        else:
                            print(f"[TIER] Tier 2 partial/failed: close_position filled {t2_cum_qty}/{pm_filled}")
                    except Exception as e:
                        print(f"[TIER] Tier 2 SDK close_position failed: {e}")
                else:
                    print(f"[TIER] Tier 1 failed. Tier 2 skipped: PM underwater "
                          f"(fill {pm_fill_price_cents:.0f}c, {close_price_label}, "
                          f"P&L {pm_close_pnl_cents:+.0f}c/contract)")
            else:
                print(f"[TIER] Tier 2 skipped: BBO unavailable (bid={bbo_bid}, ask={bbo_ask})")
        except Exception as e:
            if not t2_attempted:
                print(f"[TIER] Tier 2 skipped: BBO fetch failed: {e}")

        # ── TIER 3: OMI DIRECTIONAL RISK ──
        # Master kill switch: if enable_tier3_directional is False, skip ALL
        # directional risk (TIER3A hold, OPPOSITE_HEDGE, OPPOSITE_OVERWEIGHT)
        # and go straight to unwind. User wants risk-free arb only.
        if not Config.enable_tier3_directional:
            print(f"[TIER] Tier 3 DISABLED (enable_tier3_directional=False). Skipping directional, unwinding PM.")
            _tier3_fell_through = True
        else:
            print(f"[TIER] Tier 2 failed/skipped. Entering Tier 3 directional decision.")
            _tier3_fell_through = True  # Flag: did we skip to fallback?

        if Config.enable_tier3_directional and omi_cache is not None:
            # Step 1: Look up OMI signal
            team_full_name = TEAM_FULL_NAMES.get(arb.team, arb.team)
            omi_signal_data = omi_cache.get_signal(team_full_name)

            if omi_signal_data is not None:
                ceq = omi_cache.get_effective_ceq(omi_signal_data)        # edge % (0-15), used for sizing
                live_ceq = omi_cache.get_live_ceq(omi_signal_data)        # 0-100 scale, for logging only
                favored_team = omi_cache.get_favored_team(omi_signal_data)
                signal_tier = omi_signal_data.get("signal", "")
                game_status = omi_signal_data.get("game_status", "")
                live_data = omi_signal_data.get("live") or {}
                live_confidence = live_data.get("live_confidence", "") if live_data else ""
                pillar_scores = omi_signal_data.get("pillar_scores", {})

                flow_gated = omi_cache.get_flow_gated(omi_signal_data)
                print(f"[TIER3] OMI signal: edge={ceq:.1f}%, "
                      f"live_ceq={live_ceq}, favored={favored_team}, "
                      f"signal={signal_tier}, game_status={game_status}, "
                      f"flow_gated={flow_gated}")

                # Flow-gated: sharp money doesn't confirm edge — skip directional
                if flow_gated:
                    print(f"[OMI] Flow-gated signal: {arb.team} — skipping directional")

                # Step 2: Game status check
                elif game_status != "final":

                    # Step 3: Exposure limits
                    current_exposure, daily_loss = load_directional_positions()
                    new_cost = pm_cost_cents * pm_filled / 100.0
                    print(f"[TIER3] Exposure: current=${current_exposure:.2f}, "
                          f"limit=${Config.max_directional_exposure_usd:.2f} | "
                          f"Daily loss: ${daily_loss:.2f}, "
                          f"limit=${Config.daily_directional_loss_limit:.2f}")

                    if (current_exposure + new_cost <= Config.max_directional_exposure_usd
                            and daily_loss < Config.daily_directional_loss_limit):

                        # Step 4: Direction match
                        # BUY_PM_SELL_K → we're LONG arb.team
                        # BUY_K_SELL_PM → we're SHORT arb.team (PM is opposite side)
                        pm_bet_long = (arb.direction == 'BUY_PM_SELL_K')

                        # Check if OMI favored_team matches arb.team
                        arb_team_full = team_full_name.lower()
                        favored_full = favored_team.lower()
                        omi_favors_our_team = (
                            arb_team_full in favored_full or favored_full in arb_team_full
                        ) if favored_full else False

                        omi_agrees = (pm_bet_long and omi_favors_our_team) or \
                                     (not pm_bet_long and not omi_favors_our_team)

                        # ── OPPOSITE-SIDE HEDGE CHECK ──
                        # Buy the OTHER team's YES on Kalshi. Since exactly one team wins,
                        # one leg always pays 100c. P&L = (100 - combined_cost) * qty / 100.
                        if opposite_info and opposite_info.get('ask'):
                            other_ask = opposite_info['ask']
                            combined = pm_cost_cents + other_ask
                            print(f"[TIER3] Opposite hedge: {opposite_info['team']} ask={other_ask}c, "
                                  f"combined={combined:.0f}c (PM {pm_cost_cents:.0f}c + K {other_ask}c)")

                            execute_opposite = False
                            opp_tier_name = ""

                            # Guaranteed profit path: combined < 100c
                            if combined < Config.opposite_hedge_max_cost:
                                execute_opposite = True
                                opp_tier_name = "TIER3_OPPOSITE_HEDGE"
                                print(f"[TIER3] Guaranteed profit path: combined {combined:.0f}c < {Config.opposite_hedge_max_cost}c")

                            # Conviction overweight path: 100-103c with strong signal
                            elif combined <= Config.opposite_overweight_max_cost:
                                hold_sig = omi_cache.get_hold_signal(omi_signal_data)
                                if hold_sig == "STRONG_HOLD":
                                    execute_opposite = True
                                    opp_tier_name = "TIER3_OPPOSITE_OVERWEIGHT"
                                    print(f"[TIER3] Overweight path: STRONG_HOLD + combined {combined:.0f}c")
                                elif hold_sig is None and ceq >= Config.opposite_overweight_min_ceq \
                                        and signal_tier == "HIGH EDGE":
                                    execute_opposite = True
                                    opp_tier_name = "TIER3_OPPOSITE_OVERWEIGHT"
                                    print(f"[TIER3] Overweight path: pregame CEQ {ceq:.1f} + {signal_tier} + combined {combined:.0f}c")
                                else:
                                    print(f"[TIER3] Overweight conditions not met (hold_sig={hold_sig}, ceq={ceq:.1f}, signal={signal_tier})")

                            if execute_opposite:
                                # Place BUY YES on other team's ticker
                                try:
                                    opp_result = await kalshi_api.place_order(
                                        session, opposite_info['ticker'],
                                        'yes', 'buy',
                                        pm_filled, other_ask,
                                        time_in_force='immediate_or_cancel'
                                    )
                                    opp_filled = opp_result.get('fill_count', 0)
                                    opp_price = opp_result.get('fill_price', other_ask)

                                    if opp_filled > 0:
                                        update_position_cache_after_trade(opposite_info['ticker'], opp_filled)

                                    if opp_filled == pm_filled:
                                        actual_combined = pm_cost_cents + opp_price
                                        profit_per = 100 - actual_combined
                                        print(f"[TIER3] {opp_tier_name}: {opp_filled}x filled @ {opp_price}c, "
                                              f"combined={actual_combined:.0f}c, profit={profit_per:.1f}c/contract")

                                        # Save directional position for overweight (need settlement tracking)
                                        if opp_tier_name == "TIER3_OPPOSITE_OVERWEIGHT":
                                            dir_entry = {
                                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                                "game_id": arb.game, "team": arb.team,
                                                "side": "long" if pm_bet_long else "short",
                                                "naked_contracts": 0,
                                                "hedged_contracts": opp_filled,
                                                "entry_price_cents": int(pm_cost_cents),
                                                "opposite_hedge_price": opp_price,
                                                "combined_cost_cents": actual_combined,
                                                "tier": opp_tier_name, "ceq": round(ceq, 1),
                                                "live_ceq": live_ceq, "signal": signal_tier,
                                                "game_status": game_status,
                                                "live_confidence": live_confidence,
                                                "pillar_scores": pillar_scores,
                                                "settled": False, "settlement_pnl": None,
                                            }
                                            save_directional_position(dir_entry)

                                        _tier3_fell_through = False
                                        return TradeResult(
                                            success=True,
                                            kalshi_filled=opp_filled,
                                            pm_filled=pm_filled,
                                            kalshi_price=opp_price,
                                            pm_price=pm_fill_price,
                                            unhedged=False,
                                            abort_reason=f"{opp_tier_name}: {opposite_info['team']} {opp_filled}x @ {opp_price}c, combined={actual_combined:.0f}c",
                                            execution_time_ms=int((time.time() - start_time) * 1000),
                                            pm_order_ms=pm_order_ms, k_order_ms=k_order_ms,
                                            pm_response_details=pm_response_details,
                                            k_response_details=_k_response_details,
                                            execution_phase=_exec_phase,
                                            gtc_rest_time_ms=_gtc_rest, gtc_spread_checks=_gtc_checks,
                                            gtc_cancel_reason=_gtc_cancel, is_maker=_is_maker,
                                            tier=opp_tier_name,
                                            omi_ceq=ceq, omi_signal=signal_tier,
                                            omi_favored_team=favored_team, omi_pillar_scores=pillar_scores,
                                            opposite_hedge_ticker=opposite_info['ticker'],
                                            opposite_hedge_team=opposite_info['team'],
                                            opposite_hedge_price=opp_price,
                                            opposite_hedge_filled=opp_filled,
                                            combined_cost_cents=actual_combined,
                                            guaranteed_profit_cents=max(profit_per * pm_filled, 0),
                                        )
                                    else:
                                        print(f"[TIER3] Opposite hedge partial: {opp_filled}/{pm_filled} filled — falling through")
                                except Exception as e:
                                    print(f"[TIER3] Opposite hedge order failed: {e} — falling through")

                        # ── LIVE GAME: hold_signal-based decisions ──
                        hold_signal = omi_cache.get_hold_signal(omi_signal_data)
                        if hold_signal is not None:
                            print(f"[TIER3] Live hold_signal={hold_signal}, omi_agrees={omi_agrees}, ceq={ceq:.1f}")

                            if hold_signal == "URGENT_UNWIND":
                                print(f"[TIER3] URGENT_UNWIND — unwinding immediately")
                                # Fall through to fallback unwind

                            elif hold_signal == "UNWIND":
                                print(f"[TIER3] UNWIND — unwinding")
                                # Fall through to fallback unwind

                            elif hold_signal in ("HOLD", "STRONG_HOLD"):
                                do_hold = False
                                if omi_agrees:
                                    do_hold = True
                                    print(f"[TIER3] {hold_signal} + omi_agrees → TIER3A hold")
                                elif hold_signal == "STRONG_HOLD":
                                    do_hold = True
                                    print(f"[TIER3] STRONG_HOLD overrides direction disagreement → TIER3A hold")
                                else:
                                    print(f"[TIER3] HOLD but omi disagrees — unwinding")

                                if do_hold:
                                    naked_count = Config.get_naked_contracts(ceq)
                                    naked_count = min(naked_count, pm_filled)
                                    hedge_count = pm_filled - naked_count
                                    k_hedge_filled = 0
                                    k_hedge_price = k_limit_price

                                    if hedge_count > 0:
                                        print(f"[TIER3] TIER3A: {hold_signal} (CEQ {ceq:.1f}). "
                                              f"Holding {naked_count} naked, hedging {hedge_count} via Kalshi IOC")
                                        try:
                                            t3a_result = await kalshi_api.place_order(
                                                session, arb.kalshi_ticker,
                                                params['k_side'], params['k_action'],
                                                hedge_count, k_limit_price,
                                                time_in_force='immediate_or_cancel'
                                            )
                                            k_hedge_filled = t3a_result.get('fill_count', 0)
                                            k_hedge_price = t3a_result.get('fill_price', k_limit_price)
                                            if k_hedge_filled > 0:
                                                qty_delta = -k_hedge_filled if params['k_action'] == 'sell' else k_hedge_filled
                                                update_position_cache_after_trade(arb.kalshi_ticker, qty_delta)
                                        except Exception as e:
                                            print(f"[TIER3] TIER3A Kalshi hedge IOC failed: {e}")
                                    else:
                                        print(f"[TIER3] TIER3A: {hold_signal} (CEQ {ceq:.1f}). "
                                              f"Holding all {naked_count} contracts naked")

                                    actual_naked = pm_filled - k_hedge_filled

                                    dir_entry = {
                                        "timestamp": datetime.now(timezone.utc).isoformat(),
                                        "game_id": arb.game, "team": arb.team,
                                        "side": "long" if pm_bet_long else "short",
                                        "naked_contracts": actual_naked,
                                        "hedged_contracts": k_hedge_filled,
                                        "entry_price_cents": int(pm_cost_cents),
                                        "tier": "TIER3A", "ceq": round(ceq, 1),
                                        "live_ceq": live_ceq, "signal": signal_tier,
                                        "game_status": game_status,
                                        "live_confidence": live_confidence,
                                        "hold_signal": hold_signal,
                                        "pillar_scores": pillar_scores,
                                        "settled": False, "settlement_pnl": None,
                                    }
                                    save_directional_position(dir_entry)

                                    print(f"[TIER3] TIER3A result: {actual_naked} naked + {k_hedge_filled} hedged")

                                    _tier3_fell_through = False
                                    return TradeResult(
                                        success=k_hedge_filled > 0,
                                        kalshi_filled=k_hedge_filled,
                                        pm_filled=pm_filled,
                                        kalshi_price=k_hedge_price,
                                        pm_price=pm_fill_price,
                                        unhedged=actual_naked > 0,
                                        abort_reason=f"TIER3A: {hold_signal}, holding {actual_naked} naked (CEQ {ceq:.1f}, {signal_tier})",
                                        execution_time_ms=int((time.time() - start_time) * 1000),
                                        pm_order_ms=pm_order_ms, k_order_ms=k_order_ms,
                                        pm_response_details=pm_response_details,
                                        k_response_details=_k_response_details,
                                        execution_phase=_exec_phase,
                                        gtc_rest_time_ms=_gtc_rest, gtc_spread_checks=_gtc_checks,
                                        gtc_cancel_reason=_gtc_cancel, is_maker=_is_maker,
                                        tier="TIER3A",
                                        naked_contracts=actual_naked,
                                        omi_ceq=ceq, omi_signal=signal_tier,
                                        omi_favored_team=favored_team, omi_pillar_scores=pillar_scores,
                                    )
                            else:
                                print(f"[TIER3] Unknown hold_signal '{hold_signal}' — unwinding")

                        # ── PREGAME: CEQ threshold-based decisions ──
                        else:
                            # Step 5a: TIER3A — OMI agrees, hold some naked
                            if omi_agrees and ceq >= Config.min_ceq_hold:
                                naked_count = Config.get_naked_contracts(ceq)
                                naked_count = min(naked_count, pm_filled)
                                hedge_count = pm_filled - naked_count
                                k_hedge_filled = 0
                                k_hedge_price = k_limit_price

                                if hedge_count > 0:
                                    print(f"[TIER3] TIER3A: OMI agrees (CEQ {ceq:.1f}). "
                                          f"Holding {naked_count} naked, hedging {hedge_count} via Kalshi IOC")
                                    try:
                                        t3a_result = await kalshi_api.place_order(
                                            session, arb.kalshi_ticker,
                                            params['k_side'], params['k_action'],
                                            hedge_count, k_limit_price,
                                            time_in_force='immediate_or_cancel'
                                        )
                                        k_hedge_filled = t3a_result.get('fill_count', 0)
                                        k_hedge_price = t3a_result.get('fill_price', k_limit_price)
                                        if k_hedge_filled > 0:
                                            qty_delta = -k_hedge_filled if params['k_action'] == 'sell' else k_hedge_filled
                                            update_position_cache_after_trade(arb.kalshi_ticker, qty_delta)
                                    except Exception as e:
                                        print(f"[TIER3] TIER3A Kalshi hedge IOC failed: {e}")
                                else:
                                    print(f"[TIER3] TIER3A: OMI agrees (CEQ {ceq:.1f}). "
                                          f"Holding all {naked_count} contracts naked")

                                actual_naked = pm_filled - k_hedge_filled

                                dir_entry = {
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "game_id": arb.game, "team": arb.team,
                                    "side": "long" if pm_bet_long else "short",
                                    "naked_contracts": actual_naked,
                                    "hedged_contracts": k_hedge_filled,
                                    "entry_price_cents": int(pm_cost_cents),
                                    "tier": "TIER3A", "ceq": round(ceq, 1),
                                    "live_ceq": live_ceq, "signal": signal_tier,
                                    "game_status": game_status,
                                    "live_confidence": live_confidence,
                                    "pillar_scores": pillar_scores,
                                    "settled": False, "settlement_pnl": None,
                                }
                                save_directional_position(dir_entry)

                                print(f"[TIER3] TIER3A result: {actual_naked} naked + {k_hedge_filled} hedged")

                                _tier3_fell_through = False
                                return TradeResult(
                                    success=k_hedge_filled > 0,
                                    kalshi_filled=k_hedge_filled,
                                    pm_filled=pm_filled,
                                    kalshi_price=k_hedge_price,
                                    pm_price=pm_fill_price,
                                    unhedged=actual_naked > 0,
                                    abort_reason=f"TIER3A: OMI agrees, holding {actual_naked} naked (CEQ {ceq:.1f}, {signal_tier})",
                                    execution_time_ms=int((time.time() - start_time) * 1000),
                                    pm_order_ms=pm_order_ms, k_order_ms=k_order_ms,
                                    pm_response_details=pm_response_details,
                                    k_response_details=_k_response_details,
                                    execution_phase=_exec_phase,
                                    gtc_rest_time_ms=_gtc_rest, gtc_spread_checks=_gtc_checks,
                                    gtc_cancel_reason=_gtc_cancel, is_maker=_is_maker,
                                    tier="TIER3A",
                                    naked_contracts=actual_naked,
                                    omi_ceq=ceq, omi_signal=signal_tier,
                                    omi_favored_team=favored_team, omi_pillar_scores=pillar_scores,
                                )

                            else:
                                print(f"[TIER3] OMI signal present but conditions not met "
                                      f"(agrees={omi_agrees}, ceq={ceq:.1f}, signal={signal_tier})")
                    else:
                        print(f"[TIER3] Exposure/loss limits exceeded, skipping directional")
                else:
                    print(f"[TIER3] Game status is 'final', skipping directional")
            else:
                print(f"[TIER3] No OMI signal for {team_full_name}")
        else:
            print(f"[TIER3] OMI cache not available")

        # ── TIER 3 FALLBACK: Existing PM unwind (SDK close_position + manual) ──
        if _tier3_fell_through:
            print(f"[TIER] Tier 3 directional skipped. Falling through to unwind.")

            t3_filled, t3_fill_price = await _unwind_pm_position(
                session, pm_api, pm_slug, reverse_intent,
                pm_fill_price_cents, pm_filled, actual_pm_outcome_idx,
            )

            if t3_filled > 0:
                if reverse_intent == 2:  # Selling long: profit = sell - buy
                    pnl_per = (t3_fill_price * 100) - pm_fill_price_cents
                else:  # reverse_intent == 4: Closing short: profit = original_sell - buyback
                    pnl_per = pm_fill_price_cents - (t3_fill_price * 100)
                unwind_pnl = pnl_per * t3_filled
                loss_cents = abs(unwind_pnl)
                pnl_label = "gain" if unwind_pnl > 0 else "loss"
                print(f"[TIER] Tier 3 unwind: exited {t3_filled} ({pnl_label}: {loss_cents:.1f}c)")

                return TradeResult(
                    success=False,
                    kalshi_filled=0,
                    pm_filled=pm_filled,
                    kalshi_price=k_limit_price,
                    pm_price=pm_fill_price,
                    unhedged=False,
                    abort_reason=f"Kalshi failed, PM unwound ({pnl_label}: {loss_cents:.1f}c)",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    pm_order_ms=pm_order_ms,
                    k_order_ms=k_order_ms,
                    pm_response_details=pm_response_details,
                    k_response_details=_k_response_details,
                    execution_phase=_exec_phase,
                    gtc_rest_time_ms=_gtc_rest,
                    gtc_spread_checks=_gtc_checks,
                    gtc_cancel_reason=_gtc_cancel,
                    is_maker=_is_maker,
                    exited=True,
                    unwind_loss_cents=loss_cents,
                    unwind_pnl_cents=unwind_pnl,
                    unwind_fill_price=t3_fill_price,
                    unwind_qty=t3_filled,
                    tier="TIER3_UNWIND",
                )

            # ── EMERGENCY UNWIND: Aggressive market-crossing exit ──
            # All normal tiers failed. Rather than leaving a naked position,
            # retry with much wider buffers. A 15-20c loss on forced exit is
            # better than potential 60-70c loss at settlement.
            print(f"[EMERGENCY] All tiers failed — attempting aggressive market-crossing exit")

            emg_filled, emg_fill_price = await _unwind_pm_position(
                session, pm_api, pm_slug, reverse_intent,
                pm_fill_price_cents, pm_filled, actual_pm_outcome_idx,
                buffers=[35, 50, 65],
            )

            if emg_filled > 0:
                if reverse_intent == 2:  # Selling long: profit = sell - buy
                    pnl_per = (emg_fill_price * 100) - pm_fill_price_cents
                else:  # reverse_intent == 4: Closing short: profit = original_sell - buyback
                    pnl_per = pm_fill_price_cents - (emg_fill_price * 100)
                unwind_pnl = pnl_per * emg_filled
                loss_cents = abs(unwind_pnl)
                pnl_label = "gain" if unwind_pnl > 0 else "loss"
                print(f"[EMERGENCY] Exited {emg_filled} @ {emg_fill_price:.4f} ({pnl_label} ~{loss_cents:.1f}c)")

                return TradeResult(
                    success=False,
                    kalshi_filled=0,
                    pm_filled=pm_filled,
                    kalshi_price=k_limit_price,
                    pm_price=pm_fill_price,
                    unhedged=False,
                    exited=True,
                    unwind_loss_cents=loss_cents,
                    unwind_pnl_cents=unwind_pnl,
                    unwind_fill_price=emg_fill_price,
                    unwind_qty=emg_filled,
                    abort_reason=f"Emergency exit: {emg_filled} @ {emg_fill_price:.4f} ({pnl_label} ~{loss_cents:.1f}c)",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    pm_order_ms=pm_order_ms,
                    k_order_ms=k_order_ms,
                    pm_response_details=pm_response_details,
                    k_response_details=_k_response_details,
                    execution_phase="emergency",
                    gtc_rest_time_ms=_gtc_rest,
                    gtc_spread_checks=_gtc_checks,
                    gtc_cancel_reason=_gtc_cancel,
                    is_maker=_is_maker,
                    tier="TIER3_EMERGENCY",
                )

            # Even emergency exit failed — flag for manual review + register exposure
            print(f"[EMERGENCY] ALL EXIT ATTEMPTS FAILED — position remains unhedged, needs manual review")
            pm_cost_cents = int(pm_fill_price * 100) * pm_filled
            register_unhedged(arb.kalshi_ticker, pm_cost_cents)
            return TradeResult(
                success=False,
                kalshi_filled=0,
                pm_filled=pm_filled,
                kalshi_price=k_limit_price,
                pm_price=pm_fill_price,
                unhedged=True,
                abort_reason=f"Kalshi: no fill, all recovery tiers AND emergency exit failed - UNHEDGED! NEEDS MANUAL REVIEW",
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_order_ms=pm_order_ms,
                k_order_ms=k_order_ms,
                pm_response_details=pm_response_details,
                k_response_details=_k_response_details,
                execution_phase=_exec_phase,
                gtc_rest_time_ms=_gtc_rest,
                gtc_spread_checks=_gtc_checks,
                gtc_cancel_reason=_gtc_cancel,
                is_maker=_is_maker,
                tier="TIER3_UNWIND",
            )

    # -------------------------------------------------------------------------
    # Step 7.5: Partial hedge — unwind excess PM if K filled fewer than PM
    # -------------------------------------------------------------------------
    if 0 < k_filled < pm_filled:
        excess = pm_filled - k_filled
        print(f"[RECOVERY] Kalshi partial fill: {k_filled}/{pm_filled} — unwinding {excess} excess PM contracts")

        original_intent = params['pm_intent']
        reverse_intent = REVERSE_INTENT[original_intent]
        unwind_filled, _ = await _unwind_pm_position(
            session, pm_api, pm_slug, reverse_intent,
            pm_fill_price * 100, excess, actual_pm_outcome_idx,
        )
        if unwind_filled > 0:
            pm_filled = pm_filled - unwind_filled
            print(f"[RECOVERY] Unwound {unwind_filled}/{excess} excess PM. Net PM={pm_filled}")
        else:
            print(f"[RECOVERY] Excess PM unwind failed — {excess} contracts remain unhedged")

        # Still count as success for the hedged portion
        return TradeResult(
            success=k_filled > 0,
            kalshi_filled=k_filled,
            pm_filled=pm_filled,
            kalshi_price=k_fill_price,
            pm_price=pm_fill_price,
            unhedged=(pm_filled != k_filled),
            execution_time_ms=elapsed_ms,
            pm_order_ms=pm_order_ms,
            k_order_ms=k_order_ms,
            pm_response_details=pm_response_details,
            execution_phase="gtc" if (gtc_phase and gtc_phase.get('filled', 0) > 0) else "ioc",
            gtc_rest_time_ms=gtc_phase['rest_time_ms'] if gtc_phase else 0,
            gtc_spread_checks=gtc_phase['spread_checks'] if gtc_phase else 0,
            gtc_cancel_reason=gtc_phase.get('cancel_reason', '') if gtc_phase else '',
            is_maker=bool(gtc_phase and gtc_phase.get('is_maker', False)),
        )

    # Both sides filled (fully matched) - SUCCESS
    _check_hedge_coherence(
        arb.team, k_fill_price, pm_fill_price,
        params['k_action'], params.get('pm_is_buy_short', False),
        arb.direction, arb.pm_long_team, is_long_team,
        cache_key=arb.cache_key)
    await _verify_both_legs(session, kalshi_api, pm_api,
                            arb.kalshi_ticker, pm_slug, arb.team, k_filled, pm_filled)
    return TradeResult(
        success=True,
        kalshi_filled=k_filled,
        pm_filled=pm_filled,
        kalshi_price=k_fill_price,
        pm_price=pm_fill_price,
        unhedged=False,
        execution_time_ms=elapsed_ms,
        pm_order_ms=pm_order_ms,
        k_order_ms=k_order_ms,
        pm_response_details=pm_response_details,
        execution_phase="gtc" if (gtc_phase and gtc_phase.get('filled', 0) > 0) else "ioc",
        gtc_rest_time_ms=gtc_phase['rest_time_ms'] if gtc_phase else 0,
        gtc_spread_checks=gtc_phase['spread_checks'] if gtc_phase else 0,
        gtc_cancel_reason=gtc_phase.get('cancel_reason', '') if gtc_phase else '',
        is_maker=bool(gtc_phase and gtc_phase.get('is_maker', False)),
    )


# =============================================================================
# SELF-TEST
# =============================================================================
def run_self_test():
    """
    Verify all 4 TRADE_PARAMS cases with human-readable descriptions.
    For a sample game (ARK vs MSST, pm_long_team=ARK).
    """
    print("=" * 70)
    print("EXECUTOR_CORE SELF-TEST")
    print("=" * 70)
    print()
    print("Sample game: ARK vs MSST, pm_long_team = ARK")
    print("-" * 70)
    print()

    test_cases = [
        # (direction, team, pm_long_team, expected_description)
        ('BUY_PM_SELL_K', 'ARK', 'ARK',
         "K SELL YES @ k_bid, PM BUY_YES @ pm_ask -> K SHORT ARK, PM LONG ARK"),
        ('BUY_PM_SELL_K', 'MSST', 'ARK',
         "K SELL YES @ k_bid, PM BUY_NO @ (100-pm_bid) -> K SHORT MSST, PM LONG MSST"),
        ('BUY_K_SELL_PM', 'ARK', 'ARK',
         "K BUY YES @ k_ask, PM BUY_NO @ (100-pm_bid) -> K LONG ARK, PM SHORT ARK"),
        ('BUY_K_SELL_PM', 'MSST', 'ARK',
         "K BUY YES @ k_ask, PM BUY_YES @ pm_ask -> K LONG MSST, PM SHORT MSST"),
    ]

    all_passed = True

    for direction, team, pm_long_team, expected_desc in test_cases:
        is_long_team = (team == pm_long_team)
        key = (direction, is_long_team)
        params = TRADE_PARAMS[key]

        # Build description from params
        intent_names = {1: 'BUY_LONG', 2: 'SELL_LONG', 3: 'BUY_SHORT', 4: 'SELL_SHORT'}
        pm_intent_str = intent_names.get(params['pm_intent'], f"INTENT_{params['pm_intent']}")

        # For BUY_SHORT with inverted price, show the price conversion
        if params.get('pm_invert_price', False):
            price_str = f"(100-{params['pm_price_field']})"
        else:
            price_str = params['pm_price_field']

        actual_desc = (
            f"K {params['k_action'].upper()} {params['k_side'].upper()} @ {params['k_price_field']}, "
            f"PM {pm_intent_str} @ {price_str} -> "
            f"K {params['k_result']} {team}, PM {params['pm_result']} {team}"
        )

        # Check if opposite positions (hedged)
        is_hedged = (params['k_result'] != params['pm_result'])
        is_executable = params.get('executable', True)
        status = "HEDGE" if is_hedged else "FAIL"
        exec_status = "EXECUTABLE" if is_executable else "SKIP (no PM short liquidity)"

        print(f"{direction} for {team}:")
        print(f"  {actual_desc} {status}")
        print(f"  {exec_status}")

        if not is_hedged:
            print(f"  ERROR: Not a hedge!")
            all_passed = False
        else:
            print(f"  OK")
        print()

    print("-" * 70)
    if all_passed:
        print("ALL 4 CASES: PASSED - Every case results in opposite positions")
    else:
        print("FAILED - Some cases are not properly hedged!")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = run_self_test()
    exit(0 if success else 1)
