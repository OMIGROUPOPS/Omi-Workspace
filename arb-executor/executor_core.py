#!/usr/bin/env python3
"""
executor_core.py - Clean execution engine for arb trades.

Given: a fully resolved arb opportunity with all prices and mappings
Does: places hedged orders on Kalshi and PM, or safely aborts

4 possible trades (all executable via BUY_LONG/BUY_SHORT):
  1. BUY_PM_SELL_K, team IS pm_long_team  -> K: SELL YES, PM: BUY_LONG (intent=1)
  2. BUY_PM_SELL_K, team NOT pm_long_team -> K: SELL YES, PM: BUY_SHORT (intent=3)
  3. BUY_K_SELL_PM, team IS pm_long_team  -> K: BUY YES,  PM: BUY_SHORT (intent=3)
  4. BUY_K_SELL_PM, team NOT pm_long_team -> K: BUY YES,  PM: BUY_LONG (intent=1)

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
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, Tuple, Optional, Any

from config import Config

# Path for persisting traded games across restarts
TRADED_GAMES_FILE = os.path.join(os.path.dirname(__file__), "traded_games.json")

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

TRADE_PARAMS = {
    # ==========================================================================
    # Case 1: BUY_PM_SELL_K, team IS pm_long_team
    # K: SELL YES (short our team), PM: BUY_LONG (long our team = favorite)
    # HEDGE: K SHORT + PM LONG = hedged
    # ==========================================================================
    ('BUY_PM_SELL_K', True): {
        'k_action': 'sell',
        'k_side': 'yes',
        'k_price_field': 'k_bid',       # Selling, so use bid
        'pm_intent': 1,                  # BUY_LONG (favorite)
        'pm_price_field': 'pm_ask',     # Pay favorite's ask
        'pm_is_buy_short': False,
        'k_result': 'SHORT',
        'pm_result': 'LONG',
        'executable': True,
    },

    # ==========================================================================
    # Case 2: BUY_PM_SELL_K, team is NOT pm_long_team (underdog)
    # K: SELL YES (short underdog), PM: BUY_SHORT (long underdog)
    # HEDGE: K SHORT + PM LONG = hedged
    # Price: Use underdog's ask directly (pm_ask since team is underdog)
    # ==========================================================================
    ('BUY_PM_SELL_K', False): {
        'k_action': 'sell',
        'k_side': 'yes',
        'k_price_field': 'k_bid',       # Selling, so use bid
        'pm_intent': 3,                  # BUY_SHORT (underdog)
        'pm_price_field': 'pm_ask',     # Pay underdog's ask directly
        'pm_is_buy_short': True,
        'k_result': 'SHORT',
        'pm_result': 'LONG',
        'executable': True,              # RE-ENABLED: price now converted to YES frame
    },

    # ==========================================================================
    # Case 3: BUY_K_SELL_PM, team IS pm_long_team
    # K: BUY YES (long favorite), PM: BUY_SHORT (long underdog = short favorite)
    # HEDGE: K LONG favorite + PM LONG underdog = hedged
    # Price: Underdog ask = 100 - pm_bid (pm_bid is favorite's bid)
    # ==========================================================================
    ('BUY_K_SELL_PM', True): {
        'k_action': 'buy',
        'k_side': 'yes',
        'k_price_field': 'k_ask',       # Buying, so use ask
        'pm_intent': 3,                  # BUY_SHORT (underdog)
        'pm_price_field': 'pm_bid',     # Need to invert: underdog_ask = 100 - pm_bid
        'pm_invert_price': True,        # Signals to use 100 - pm_bid as the price
        'pm_is_buy_short': True,
        'k_result': 'LONG',
        'pm_result': 'SHORT',            # SHORT favorite = LONG underdog
        'executable': True,
    },

    # ==========================================================================
    # Case 4: BUY_K_SELL_PM, team is NOT pm_long_team (underdog)
    # K: BUY YES (long underdog), PM: BUY_LONG (long favorite = short underdog)
    # HEDGE: K LONG underdog + PM LONG favorite = hedged
    # Price: Favorite ask = 100 - pm_bid (pm_bid is underdog's bid)
    # ==========================================================================
    ('BUY_K_SELL_PM', False): {
        'k_action': 'buy',
        'k_side': 'yes',
        'k_price_field': 'k_ask',       # Buying, so use ask
        'pm_intent': 1,                  # BUY_LONG (favorite)
        'pm_price_field': 'pm_bid',     # Need to invert: favorite_ask = 100 - pm_bid
        'pm_invert_price': True,        # Signals to use 100 - pm_bid as the price
        'pm_is_buy_short': False,
        'k_result': 'LONG',
        'pm_result': 'SHORT',            # LONG favorite = SHORT underdog
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
    execution_phase: str = "ioc"       # "ioc" or "gtc"
    gtc_rest_time_ms: int = 0          # how long GTC rested before fill/cancel
    gtc_spread_checks: int = 0         # spread validations during GTC rest
    gtc_cancel_reason: str = ""        # "timeout", "spread_gone", "filled", ""
    is_maker: bool = False             # True if filled via GTC (0% fee)
    exited: bool = False               # True if PM was successfully unwound after K failure
    unwind_loss_cents: Optional[float] = None  # Total loss from PM unwind across all contracts (cents)
    tier: str = ""  # "TIER1_HEDGE", "TIER2_EXIT", "TIER3_UNWIND", or "" for normal/non-recovery


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
        if reverse_intent in (2, 4):  # SELL: accept less
            price_cents = max(pm_price_cents - buffer, 1)
        else:  # BUY: pay more
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
            if not cancel_ok:
                # Race condition: might have filled between check and cancel
                recheck = await pm_api.get_order_status(session, order_id)
                recheck_qty = recheck.get('cum_quantity', 0)
                if recheck_qty > 0:
                    result['filled'] = recheck_qty
                    result['fill_price'] = recheck.get('fill_price', pm_price)
                    result['is_maker'] = True
                    result['cancel_reason'] = 'filled_on_cancel'
                    print(f"[GTC] Cancel race: actually filled {recheck_qty}")

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

# GTC execution state
gtc_cooldowns: Dict[str, float] = {}      # game_id -> timestamp cooldown expires
_resting_gtc_order_id: Optional[str] = None  # max 1 resting GTC globally


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

    while contracts < max_contracts:
        # Get current prices at this depth level
        if k_idx >= len(k_levels) or pm_idx >= len(pm_levels):
            break
        if k_remaining <= 0:
            k_idx += 1
            if k_idx >= len(k_levels):
                break
            k_remaining = k_levels[k_idx][1]
        if pm_remaining <= 0:
            pm_idx += 1
            if pm_idx >= len(pm_levels):
                break
            pm_remaining = pm_levels[pm_idx][1]

        k_price = k_levels[k_idx][0]
        pm_cost = pm_levels[pm_idx][0]

        # Compute marginal spread
        if direction == 'BUY_PM_SELL_K':
            spread = k_price - pm_cost
        else:  # BUY_K_SELL_PM
            spread = (100 - pm_cost) - k_price

        # Compute fees for this contract
        fees = Config.kalshi_fee_cents + (pm_cost * Config.pm_us_fee_rate) + Config.expected_slippage_cents
        marginal_profit = spread - fees

        if marginal_profit < Config.min_profit_per_contract:
            break

        # Take 1 contract from both books
        contracts += 1
        total_profit += marginal_profit
        total_k_price += k_price
        total_pm_cost += pm_cost
        k_remaining -= 1
        pm_remaining -= 1

    if contracts == 0:
        return {
            'size': 0, 'expected_profit_cents': 0, 'avg_spread_cents': 0,
            'avg_pm_price': 0, 'avg_k_price': 0,
            'k_depth': total_k_available, 'pm_depth': total_pm_available,
            'limit_reason': 'no_profitable_contracts',
        }

    # ── Step D: Apply safety caps ──
    depth_limit = min(total_k_available, total_pm_available)
    safe_depth = math.floor(depth_limit * Config.depth_cap)

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

    # Determine limiting factor
    limit_reason = 'depth_walk'
    final_size = contracts
    if safe_depth < final_size:
        final_size = safe_depth
        limit_reason = 'depth_cap'
    if capital_limit < final_size:
        final_size = capital_limit
        limit_reason = 'capital'
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
            fees = Config.kalshi_fee_cents + (pc * Config.pm_us_fee_rate) + Config.expected_slippage_cents
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
    # Check blacklist
    if game_id in blacklisted_games:
        return False, f"Game {game_id} is BLACKLISTED after crashes"

    # Check already traded (skippable via config for multi-trade-per-game strategies)
    if not Config.skip_traded_games_check and game_id in traded_games:
        return False, f"Game {game_id} already traded this session"

    # Check existing position (from local cache — no API call)
    if ticker in cached_positions:
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

    # -------------------------------------------------------------------------
    # Step 1: Safety checks (in-memory only — no API calls on hot path)
    # -------------------------------------------------------------------------
    safe, reason = safe_to_trade(arb.kalshi_ticker, game_id)
    if not safe:
        return TradeResult(success=False, abort_reason=f"Safety: {reason}")

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

    # For Case 4: pm_bid is our team's bid, but we're buying the OTHER team
    # Other team's ask = 100 - our team's bid
    if params.get('pm_invert_price', False):
        pm_price_cents = 100 - pm_price_cents

    # PM buffer: scale with size to control risk on larger orders
    # Use math.ceil so fractional cents always round UP (e.g. 5.5c → 6c)
    # Prevents :.2f truncation from eating the buffer in the PM API payload
    if size <= 3:
        pm_buffer = max(2, math.ceil(spread * 0.50))
    elif size <= 10:
        pm_buffer = max(2, math.ceil(spread * 0.40))
    else:
        pm_buffer = max(2, math.ceil(spread * 0.30))

    print(f"[EXEC] Sized: {size} contracts | buffer: {pm_buffer}c")

    if params.get('pm_is_buy_short', False):
        # BUY_SHORT: PM interprets price as MIN YES sell price (favorite frame)
        # pm_price_cents = underdog cost (what we want to pay for SHORT)
        # Buffer adds to underdog cost (willing to pay slightly more for fill)
        max_underdog_cost = min(math.ceil(pm_price_cents + pm_buffer), 99)
        # Convert to YES frame: min_yes_sell = 100 - max_underdog_cost
        pm_price_buffered = max(100 - max_underdog_cost, 1)
        pm_price = pm_price_buffered / 100.0
    else:
        # BUY_LONG: PM interprets price as MAX YES buy price (favorite frame)
        pm_price_buffered = min(math.ceil(pm_price_cents + pm_buffer), 99)
        pm_price = pm_price_buffered / 100.0

    # Add buffer to Kalshi price for better fill
    if params['k_action'] == 'sell':
        k_limit_price = max(k_price - Config.price_buffer_cents, 1)
    else:  # buy
        k_limit_price = min(k_price + Config.price_buffer_cents, 99)

    # -------------------------------------------------------------------------
    # Step 4.5: Kalshi depth pre-validation (before committing PM order)
    # -------------------------------------------------------------------------
    if k_book_ref:
        if params['k_action'] == 'sell':
            # Selling YES: need YES bids at or above our limit price
            k_depth_available = sum(
                qty for price, qty in k_book_ref.get('yes_bids', {}).items()
                if int(price) >= k_limit_price
            )
        else:  # buy
            # Buying YES: need YES asks at or below our limit price
            k_depth_available = sum(
                qty for price, qty in k_book_ref.get('yes_asks', {}).items()
                if int(price) <= k_limit_price
            )
        # 2x depth requirement — phantom depth mitigation
        if k_depth_available < size * 2:
            book_bids = sorted(k_book_ref.get('yes_bids', {}).items(), key=lambda x: -int(x[0]))[:5]
            book_asks = sorted(k_book_ref.get('yes_asks', {}).items(), key=lambda x: int(x[0]))[:5]
            print(f"[EXEC] K depth insufficient: need {size}x2={size*2} @ limit={k_limit_price}c, have {k_depth_available} "
                  f"| action={params['k_action']} | bids={book_bids} | asks={book_asks}")
            return TradeResult(
                success=False,
                abort_reason=f"Kalshi book depth insufficient ({k_depth_available}/{size*2} @ {k_limit_price}c)",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    # -------------------------------------------------------------------------
    # Step 5: Place PM order FIRST (unreliable leg - IOC often expires)
    # -------------------------------------------------------------------------
    # CRITICAL FIX: When is_long_team=False, we must trade on the LONG team's
    # outcome, not our team's outcome. The long team's index is the complement
    # of our team's index (1 - pm_outcome_idx). This is because:
    # - BUY_NO on long team's outcome = SHORT long team = LONG our team
    # - BUY_YES on long team's outcome = LONG long team = SHORT our team
    actual_pm_outcome_idx = pm_outcome_idx if is_long_team else (1 - pm_outcome_idx)

    pm_order_start = time.time()
    try:
        pm_result = await pm_api.place_order(
            session,
            pm_slug,
            params['pm_intent'],   # 1=BUY_YES, 3=BUY_NO
            pm_price,
            size,                  # Dynamic sizing from depth walk
            tif=3,                 # time_in_force: IOC
            sync=True,             # Always synchronous for IOC
            outcome_index=actual_pm_outcome_idx
        )
    except Exception as e:
        # PM failed before any position taken - safe exit
        execution_time_ms = int((time.time() - start_time) * 1000)
        pm_err_details = _extract_pm_response_details({'error': str(e)})
        return TradeResult(success=False, abort_reason=f"PM order failed: {e}",
                           execution_time_ms=execution_time_ms,
                           pm_response_details=pm_err_details)

    pm_order_ms = int((time.time() - pm_order_start) * 1000)
    pm_filled = pm_result.get('fill_count', 0)
    pm_fill_price = pm_result.get('fill_price', pm_price)
    pm_response_details = _extract_pm_response_details(pm_result)

    if pm_filled == 0:
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Log diagnostic summary for no-fill
        status = pm_response_details.get('pm_response_status', '?')
        order_state = pm_result.get('order_state', 'N/A')
        order_id = pm_result.get('order_id', 'none')
        error_hint = pm_response_details.get('pm_expiry_reason', '') or ''
        print(f"[EXEC] PM NO FILL: status={status} | state={order_state} | order={order_id} | {size}@${pm_price:.2f} | {error_hint}")

        # Distinguish real no-fills from early aborts / API errors:
        # Real no-fill: has 'order_id' (PM accepted the order, IOC expired)
        # Early abort/error: no 'order_id' (validation fail or HTTP error)
        if 'order_id' not in pm_result:
            error_msg = pm_result.get('error', 'unknown')
            return TradeResult(
                success=False,
                pm_filled=0,
                pm_price=pm_price,
                abort_reason=f"PM order rejected: {error_msg}",
                pm_order_ms=0,  # Force 0 so caller routes to SKIPPED
                execution_time_ms=execution_time_ms,
                pm_response_details=pm_response_details,
            )

        # ── Phase 2: GTC attempt ──
        if Config.enable_gtc and k_book_ref is not None:
            print(f"[EXEC] Phase 1: IOC {size}@${pm_price:.2f} -> expired")
            gtc_phase = await _execute_gtc_phase(
                session=session, pm_api=pm_api, pm_slug=pm_slug,
                pm_intent=params['pm_intent'], pm_price=pm_price,
                size=size, outcome_index=actual_pm_outcome_idx,
                k_book_ref=k_book_ref, direction=arb.direction,
                game_id=game_id,
            )
            if gtc_phase['filled'] > 0:
                # GTC got fills — update vars and FALL THROUGH to Kalshi leg
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
                # DON'T RETURN — fall through to Step 5.5 + Step 6
            else:
                # GTC didn't fill — return with GTC metadata
                return TradeResult(
                    success=False, pm_filled=0, pm_price=pm_price,
                    abort_reason=f"PM: GTC no fill ({gtc_phase['cancel_reason']})",
                    pm_order_ms=pm_order_ms,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    pm_response_details=pm_response_details,
                    execution_phase="gtc",
                    gtc_rest_time_ms=gtc_phase['rest_time_ms'],
                    gtc_spread_checks=gtc_phase['spread_checks'],
                    gtc_cancel_reason=gtc_phase['cancel_reason'],
                )
        else:
            # GTC disabled — original IOC-only return
            return TradeResult(
                success=False, pm_filled=0, pm_price=pm_price,
                abort_reason="PM: no fill (safe exit)",
                pm_order_ms=pm_order_ms,
                execution_time_ms=execution_time_ms,
                pm_response_details=pm_response_details,
            )

    # -------------------------------------------------------------------------
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
                pm_price_cents, pm_filled, actual_pm_outcome_idx,
            )
            exited = unwind_filled > 0
            unwind_loss = None
            if exited and unwind_fill_price is not None:
                if reverse_intent in (2, 4):
                    loss_per_contract = (pm_fill_price * 100) - (unwind_fill_price * 100)
                else:
                    loss_per_contract = (unwind_fill_price * 100) - (pm_fill_price * 100)
                unwind_loss = abs(loss_per_contract) * pm_filled
                print(f"[GTC] Loss from unwind: {abs(loss_per_contract):.1f}c x {pm_filled} = {unwind_loss:.1f}c total (+ fees)")
            if not exited:
                print(f"[GTC] PM unwind failed - position remains open!")
            return TradeResult(
                success=False, pm_filled=0 if exited else pm_filled,
                pm_price=pm_fill_price,
                unhedged=not exited,
                abort_reason=f"GTC filled but K spread gone, PM unwound (loss: {unwind_loss:.1f}c)" if exited and unwind_loss is not None else "GTC filled but K spread gone, PM unwind FAILED - UNHEDGED!" if not exited else "GTC filled but K spread gone, PM unwound",
                pm_order_ms=pm_order_ms,
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_response_details=pm_response_details,
                execution_phase="gtc", is_maker=True,
                gtc_rest_time_ms=gtc_phase['rest_time_ms'],
                gtc_spread_checks=gtc_phase['spread_checks'],
                gtc_cancel_reason='spread_gone_pre_kalshi',
                exited=exited,
                unwind_loss_cents=unwind_loss,
            )

    # -------------------------------------------------------------------------
    # Step 6: Place Kalshi order (only if PM filled - reliable leg)
    # -------------------------------------------------------------------------
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
        print(f"[RECOVERY] Kalshi exception: {e} - unwinding PM position...")
        on_execution_crash(game_id)

        # Try to unwind PM position (10c buffer, then 25c desperation)
        original_intent = params['pm_intent']
        reverse_intent = REVERSE_INTENT[original_intent]
        unwind_filled, unwind_fill_price = await _unwind_pm_position(
            session, pm_api, pm_slug, reverse_intent,
            pm_price_cents, pm_filled, actual_pm_outcome_idx,
        )

        if unwind_filled > 0:
            loss_per_contract = abs((pm_fill_price - unwind_fill_price) * 100)
            loss_cents = loss_per_contract * pm_filled
            return TradeResult(
                success=False, kalshi_filled=0, pm_filled=0,
                kalshi_price=k_limit_price, pm_price=pm_fill_price,
                unhedged=False,
                abort_reason=f"Kalshi exception, PM unwound (loss: {loss_per_contract:.1f}c x {pm_filled} = {loss_cents:.1f}c)",
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_order_ms=pm_order_ms, k_order_ms=0,
                pm_response_details=pm_response_details,
                execution_phase="gtc" if (gtc_phase and gtc_phase.get('filled', 0) > 0) else "ioc",
                gtc_rest_time_ms=gtc_phase['rest_time_ms'] if gtc_phase else 0,
                gtc_spread_checks=gtc_phase['spread_checks'] if gtc_phase else 0,
                gtc_cancel_reason=gtc_phase.get('cancel_reason', '') if gtc_phase else '',
                is_maker=bool(gtc_phase and gtc_phase.get('is_maker', False)),
                exited=True,
                unwind_loss_cents=loss_cents,
                tier="TIER3_UNWIND",
            )

        # Unwind failed
        return TradeResult(
            success=False,
            kalshi_filled=0,
            pm_filled=pm_filled,
            kalshi_price=k_limit_price,
            pm_price=pm_fill_price,
            unhedged=True,
            abort_reason=f"Kalshi exception: {e}, PM unwind failed - UNHEDGED!",
            execution_time_ms=int((time.time() - start_time) * 1000),
            pm_order_ms=pm_order_ms,
            k_order_ms=0,
            pm_response_details=pm_response_details,
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
                        close_resp = await pm_api.close_position(session, pm_slug)
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
                                pm_filled=0,
                                kalshi_price=k_limit_price,
                                pm_price=pm_fill_price,
                                unhedged=False,
                                abort_reason=f"Kalshi failed, PM closed via SDK (P&L {total_pnl:+.1f}c)",
                                execution_time_ms=int((time.time() - start_time) * 1000),
                                pm_order_ms=pm_order_ms,
                                k_order_ms=k_order_ms,
                                pm_response_details=pm_response_details,
                                execution_phase=_exec_phase,
                                gtc_rest_time_ms=_gtc_rest,
                                gtc_spread_checks=_gtc_checks,
                                gtc_cancel_reason=_gtc_cancel,
                                is_maker=_is_maker,
                                exited=True,
                                unwind_loss_cents=abs(total_pnl) if total_pnl < 0 else 0,
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

        # ── TIER 3: Fallback to existing PM unwind (SDK close_position + manual) ──
        print(f"[TIER] Tier 2 failed/skipped. Falling through to Tier 3 unwind.")

        t3_filled, t3_fill_price = await _unwind_pm_position(
            session, pm_api, pm_slug, reverse_intent,
            pm_fill_price_cents, pm_filled, actual_pm_outcome_idx,
        )

        if t3_filled > 0:
            if reverse_intent in (2, 4):
                loss_per = pm_fill_price_cents - (t3_fill_price * 100)
            else:
                loss_per = (t3_fill_price * 100) - pm_fill_price_cents
            loss_cents = abs(loss_per) * pm_filled
            print(f"[TIER] Tier 3: exited {t3_filled} (loss: {loss_cents:.1f}c)")

            return TradeResult(
                success=False,
                kalshi_filled=0,
                pm_filled=0,
                kalshi_price=k_limit_price,
                pm_price=pm_fill_price,
                unhedged=False,
                abort_reason=f"Kalshi failed, PM unwound (loss: {loss_cents:.1f}c)",
                execution_time_ms=int((time.time() - start_time) * 1000),
                pm_order_ms=pm_order_ms,
                k_order_ms=k_order_ms,
                pm_response_details=pm_response_details,
                execution_phase=_exec_phase,
                gtc_rest_time_ms=_gtc_rest,
                gtc_spread_checks=_gtc_checks,
                gtc_cancel_reason=_gtc_cancel,
                is_maker=_is_maker,
                exited=True,
                unwind_loss_cents=loss_cents,
                tier="TIER3_UNWIND",
            )

        # All tiers failed - still unhedged
        print(f"[TIER] ALL TIERS FAILED — position remains unhedged!")
        return TradeResult(
            success=False,
            kalshi_filled=0,
            pm_filled=pm_filled,
            kalshi_price=k_limit_price,
            pm_price=pm_fill_price,
            unhedged=True,
            abort_reason=f"Kalshi: no fill, all recovery tiers failed - UNHEDGED!",
            execution_time_ms=int((time.time() - start_time) * 1000),
            pm_order_ms=pm_order_ms,
            k_order_ms=k_order_ms,
            pm_response_details=pm_response_details,
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
            pm_price_cents, excess, actual_pm_outcome_idx,
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
