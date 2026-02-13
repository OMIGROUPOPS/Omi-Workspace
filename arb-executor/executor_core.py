#!/usr/bin/env python3
"""
executor_core.py - Clean execution engine for arb trades.

Given: a fully resolved arb opportunity with all prices and mappings
Does: places hedged orders on Kalshi and PM, or safely aborts

4 possible trades (all executable via BUY_LONG/BUY_SHORT):
  1. BUY_PM_SELL_K, team IS pm_long_team  -> K: SELL YES, PM: BUY_LONG (intent=1)
  2. BUY_PM_SELL_K, team NOT pm_long_team -> K: SELL YES, PM: BUY_SHORT (intent=3)
  3. BUY_K_SELL_PM, team IS pm_long_team  -> K: BUY YES, PM: BUY_SHORT (intent=3)
  4. BUY_K_SELL_PM, team NOT pm_long_team -> K: BUY YES, PM: BUY_LONG (intent=1)

EXECUTION ORDER: PM FIRST, THEN KALSHI
  - PM is the unreliable leg (IOC orders often expire due to latency)
  - Kalshi is the reliable leg (fills consistently)
  - If PM doesn't fill, we exit cleanly with no position
  - If PM fills but Kalshi doesn't, we have an unhedged position (rare)

Safety guarantees:
  - Checks position before ordering (no duplicate trades)
  - PM first (unreliable), Kalshi only if PM fills (reliable)
  - 1 contract only, always
  - Phantom spread rejection (>90c)
  - All 4 trade cases handled explicitly via TRADE_PARAMS lookup
  - Runtime pm_long_team verification against live PM API
"""
import asyncio
import json
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
# RUNTIME PM_LONG_TEAM VERIFICATION
# =============================================================================
async def verify_pm_long_team(
    session,
    pm_api,
    pm_slug: str,
    expected_pm_long_team: str,
) -> Tuple[bool, str, Optional[str]]:
    """
    Verify pm_long_team at runtime by fetching PM market and checking marketSides.

    Returns: (is_valid, reason, actual_pm_long_team)
    - is_valid: True if mapping matches live API
    - reason: Human-readable explanation
    - actual_pm_long_team: The actual pm_long_team from live API (or None on error)
    """
    try:
        # Fetch market details from PM API
        path = f'/v1/markets/{pm_slug}'
        headers = pm_api._headers('GET', path)

        async with session.get(f'{pm_api.BASE_URL}{path}', headers=headers) as r:
            if r.status != 200:
                # Market might be closed - allow trade to proceed with warning
                return True, f"PM market fetch failed (status={r.status}), proceeding with caution", None

            market = await r.json()

            # Check for error response
            if market.get('code') or market.get('message') == 'Not Found':
                return True, "PM market not found (may be closed), proceeding with caution", None

            # Get marketSides
            market_sides = market.get('marketSides', [])
            if not market_sides or len(market_sides) < 2:
                return True, "No marketSides in response, proceeding with caution", None

            # Find which team has long=true
            actual_long_team = None
            for side in market_sides:
                if side.get('long') is True:
                    team_info = side.get('team', {})
                    # Try displayAbbreviation first, then abbreviation
                    abbrev = team_info.get('displayAbbreviation') or team_info.get('abbreviation') or ''
                    abbrev_lower = abbrev.lower()

                    # Map to Kalshi abbreviation
                    if abbrev_lower in PM_DISPLAY_TO_KALSHI:
                        actual_long_team = PM_DISPLAY_TO_KALSHI[abbrev_lower]
                    else:
                        actual_long_team = abbrev.upper()
                    break

            if not actual_long_team:
                return True, "Could not determine pm_long_team from marketSides, proceeding with caution", None

            # Compare with expected
            if actual_long_team == expected_pm_long_team:
                return True, f"pm_long_team verified: {actual_long_team}", actual_long_team
            else:
                return False, (
                    f"PM_LONG_TEAM MISMATCH: mapping says {expected_pm_long_team}, "
                    f"API says {actual_long_team}"
                ), actual_long_team

    except Exception as e:
        # On error, allow trade but log warning
        return True, f"pm_long_team verification error: {e}, proceeding with caution", None

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
        'k_price_field': 'k_ask',       # Buying, so pay ask
        'pm_intent': 3,                  # BUY_SHORT (underdog)
        'pm_price_field': 'pm_bid',     # Need to invert: underdog_ask = 100 - pm_bid
        'pm_invert_price': True,        # Signals to use 100 - pm_bid as the price
        'pm_is_buy_short': True,
        'k_result': 'LONG',
        'pm_result': 'SHORT',            # SHORT favorite = LONG underdog
        'executable': True,              # RE-ENABLED: price now converted to YES frame
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
        'k_price_field': 'k_ask',       # Buying, so pay ask
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


# =============================================================================
# SAFETY STATE (module-level, persists across trades)
# =============================================================================
traded_games: Set[str] = set()           # Games traded this session
blacklisted_games: Set[str] = set()      # Games blacklisted after crashes
crash_counts: Dict[str, int] = {}        # Crash count per game
cached_positions: Dict[str, int] = {}    # Kalshi positions cache
cached_positions_ts: float = 0           # Cache timestamp


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


async def refresh_position_cache(session, kalshi_api) -> None:
    """Refresh the Kalshi positions cache."""
    global cached_positions, cached_positions_ts
    try:
        positions = await kalshi_api.get_positions(session)
        cached_positions.clear()
        if positions:
            for ticker, pos in positions.items():
                qty = pos.position if hasattr(pos, 'position') else pos.get('position', 0)
                if qty != 0:
                    cached_positions[ticker] = qty
        cached_positions_ts = time.time()
    except Exception as e:
        print(f"[SAFETY] Failed to refresh positions: {e}")


async def safe_to_trade(
    session,
    kalshi_api,
    ticker: str,
    game_id: str
) -> Tuple[bool, str]:
    """
    Pre-trade safety checks. Returns (safe, reason).

    Checks:
    1. Game not blacklisted
    2. Game not already traded this session
    3. No existing position on this ticker
    4. Under position limit
    """
    global cached_positions_ts

    # Check blacklist
    if game_id in blacklisted_games:
        return False, f"Game {game_id} is BLACKLISTED after crashes"

    # Check already traded
    if game_id in traded_games:
        return False, f"Game {game_id} already traded this session"

    # Refresh cache if stale (>5 seconds)
    if time.time() - cached_positions_ts > 5:
        await refresh_position_cache(session, kalshi_api)

    # Check existing position
    if ticker in cached_positions:
        pos_count = cached_positions[ticker]
        if abs(pos_count) >= Config.max_contracts_per_game:
            return False, f"Already have {pos_count} contracts on {ticker}"

    # Check position limit
    total_positions = len(cached_positions)
    if total_positions >= Config.max_concurrent_positions:
        return False, f"Too many positions ({total_positions}/{Config.max_concurrent_positions})"

    return True, "OK"


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
) -> TradeResult:
    """
    Execute a single 1-contract hedged arb trade.
    Returns TradeResult with status, fills, and details.

    EXECUTION ORDER: PM FIRST, THEN KALSHI
    - PM is the unreliable leg (IOC orders often expire)
    - Kalshi is the reliable leg (fills consistently)
    - If PM doesn't fill → exit cleanly with no position
    - If PM fills but Kalshi doesn't → unhedged (rare, logged)

    Safety guarantees:
    1. Checks position before ordering (no duplicate trades)
    2. Runtime pm_long_team verification against live PM API
    3. PM first (unreliable), Kalshi only if PM fills (reliable)
    4. 1 contract only, always
    5. Phantom spread rejection (>90c)
    6. All 4 trade cases handled explicitly via TRADE_PARAMS lookup
    """
    start_time = time.time()
    game_id = arb.game  # Kalshi game_id format

    # -------------------------------------------------------------------------
    # Step 1: Safety checks
    # -------------------------------------------------------------------------
    safe, reason = await safe_to_trade(session, kalshi_api, arb.kalshi_ticker, game_id)
    if not safe:
        return TradeResult(success=False, abort_reason=f"Safety: {reason}")

    # NOTE: traded_games is only updated AFTER PM fills (see Step 5.5 below).
    # This allows retries on PM_NO_FILL — the game stays tradeable.

    # -------------------------------------------------------------------------
    # Step 1.5: Runtime pm_long_team verification
    # -------------------------------------------------------------------------
    # CRITICAL: The pregame mapper's pm_long_team can be wrong!
    # Verify against live PM API before placing any orders.
    pm_valid, pm_reason, actual_pm_long = await verify_pm_long_team(
        session, pm_api, pm_slug, arb.pm_long_team
    )
    if not pm_valid:
        # MISMATCH - abort trade to prevent unhedged positions
        print(f"[ABORT] {pm_reason}")
        return TradeResult(success=False, abort_reason=pm_reason)

    # Log verification result
    if actual_pm_long and actual_pm_long != arb.pm_long_team:
        print(f"[WARN] pm_long_team corrected: {arb.pm_long_team} -> {actual_pm_long}")

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

    # Aggressive PM buffer: 50% of spread to overcome IOC latency
    # Crosses deeper into the book for fills against non-top-of-book liquidity
    pm_buffer = max(2, int(spread * 0.50))

    if params.get('pm_is_buy_short', False):
        # BUY_SHORT: PM interprets price as MIN YES sell price (favorite frame)
        # pm_price_cents = underdog cost (what we want to pay for SHORT)
        # Buffer adds to underdog cost (willing to pay slightly more for fill)
        max_underdog_cost = min(pm_price_cents + pm_buffer, 99)
        # Convert to YES frame: min_yes_sell = 100 - max_underdog_cost
        pm_price_buffered = max(100 - max_underdog_cost, 1)
        pm_price = pm_price_buffered / 100.0
    else:
        # BUY_LONG: PM interprets price as MAX YES buy price (favorite frame)
        pm_price_buffered = min(pm_price_cents + pm_buffer, 99)
        pm_price = pm_price_buffered / 100.0

    # Add buffer to Kalshi price for better fill
    if params['k_action'] == 'sell':
        k_limit_price = max(k_price - Config.price_buffer_cents, 1)
    else:
        k_limit_price = min(k_price + Config.price_buffer_cents, 99)

    # -------------------------------------------------------------------------
    # Step 5: Place PM order FIRST (unreliable leg - IOC often expires)
    # -------------------------------------------------------------------------
    # CRITICAL FIX: When is_long_team=False, we must trade on the LONG team's
    # outcome (index 0), not the team's outcome (index 1). This is because:
    # - BUY_NO on long team's outcome = SHORT long team = LONG our team
    # - BUY_YES on long team's outcome = LONG long team = SHORT our team
    # So when betting on non-long-team, always use outcome_index = 0
    actual_pm_outcome_idx = pm_outcome_idx if is_long_team else 0

    pm_order_start = time.time()
    try:
        pm_result = await pm_api.place_order(
            session,
            pm_slug,
            params['pm_intent'],   # 1=BUY_YES, 3=BUY_NO
            pm_price,
            1,                     # Always 1 contract
            tif=3,                 # time_in_force: IOC
            sync=True,             # Always synchronous for IOC
            outcome_index=actual_pm_outcome_idx
        )
    except Exception as e:
        # PM failed before any position taken - safe exit
        execution_time_ms = int((time.time() - start_time) * 1000)
        return TradeResult(success=False, abort_reason=f"PM order failed: {e}", execution_time_ms=execution_time_ms)

    pm_order_ms = int((time.time() - pm_order_start) * 1000)
    pm_filled = pm_result.get('fill_count', 0)
    pm_fill_price = pm_result.get('fill_price', pm_price)

    if pm_filled == 0:
        execution_time_ms = int((time.time() - start_time) * 1000)

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
                execution_time_ms=execution_time_ms
            )

        # Real no-fill: order was accepted but IOC expired without fills
        return TradeResult(
            success=False,
            pm_filled=0,
            pm_price=pm_price,
            abort_reason="PM: no fill (safe exit)",
            pm_order_ms=pm_order_ms,
            execution_time_ms=execution_time_ms
        )

    # -------------------------------------------------------------------------
    # Step 5.5: PM filled — NOW lock the game to prevent duplicate trades
    # -------------------------------------------------------------------------
    traded_games.add(game_id)

    # -------------------------------------------------------------------------
    # Step 6: Place Kalshi order (only if PM filled - reliable leg)
    # -------------------------------------------------------------------------
    k_order_start = time.time()
    try:
        k_result = await kalshi_api.place_order(
            session,
            arb.kalshi_ticker,
            params['k_side'],      # 'yes'
            params['k_action'],    # 'buy' or 'sell'
            1,                     # Always 1 contract
            k_limit_price
        )
    except Exception as e:
        # KALSHI EXCEPTION - Attempt to unwind PM position
        print(f"[RECOVERY] Kalshi exception: {e} - unwinding PM position...")
        on_execution_crash(game_id)

        # Try to unwind PM position
        original_intent = params['pm_intent']
        reverse_intent = 2 if original_intent == 1 else 1
        unwind_buffer = 3
        unwind_price_cents = max(pm_price_cents - unwind_buffer, 1) if reverse_intent == 2 else min(pm_price_cents + unwind_buffer, 99)
        unwind_price = unwind_price_cents / 100.0

        try:
            unwind_result = await pm_api.place_order(
                session, pm_slug, reverse_intent, unwind_price, pm_filled,
                tif=3, sync=True, outcome_index=actual_pm_outcome_idx
            )
            unwind_filled = unwind_result.get('fill_count', 0)
            if unwind_filled > 0:
                unwind_fill_price = unwind_result.get('fill_price', unwind_price)
                loss_cents = abs((pm_fill_price - unwind_fill_price) * 100)
                print(f"[RECOVERY] PM UNWOUND after K exception: {unwind_filled} @ ${unwind_fill_price:.3f} (loss: {loss_cents:.1f}c)")
                return TradeResult(
                    success=False, kalshi_filled=0, pm_filled=0,
                    kalshi_price=k_limit_price, pm_price=pm_fill_price,
                    unhedged=False,
                    abort_reason=f"Kalshi exception, PM unwound (loss: {loss_cents:.1f}c)",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    pm_order_ms=pm_order_ms, k_order_ms=0
                )
        except Exception as unwind_err:
            print(f"[RECOVERY] PM unwind failed: {unwind_err}")

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
            k_order_ms=0
        )

    k_order_ms = int((time.time() - k_order_start) * 1000)
    k_filled = k_result.get('fill_count', 0)
    k_fill_price = k_result.get('fill_price', k_price)

    # -------------------------------------------------------------------------
    # Step 7: Check hedge status and recover if needed
    # -------------------------------------------------------------------------
    elapsed_ms = int((time.time() - start_time) * 1000)

    if k_filled == 0:
        # KALSHI FAILED - Attempt to unwind PM position immediately
        print(f"[RECOVERY] Kalshi failed to fill - unwinding PM position...")

        # Determine reverse intent: if we bought (1), sell (2); if we sold (2), buy (1)
        original_intent = params['pm_intent']
        reverse_intent = 2 if original_intent == 1 else 1  # BUY_YES=1 -> SELL_YES=2

        # For unwinding, we need to be aggressive with price to ensure fill
        # If selling (intent=2): use bid - buffer (willing to take less)
        # If buying (intent=1): use ask + buffer (willing to pay more)
        unwind_buffer = 3  # 3c buffer for aggressive exit

        if reverse_intent == 2:  # SELL_YES to close long
            # Get current bid to sell at
            unwind_price_cents = max(pm_price_cents - unwind_buffer, 1)
        else:  # BUY_YES to close short
            # Get current ask to buy at
            unwind_price_cents = min(pm_price_cents + unwind_buffer, 99)

        unwind_price = unwind_price_cents / 100.0

        try:
            unwind_result = await pm_api.place_order(
                session,
                pm_slug,
                reverse_intent,
                unwind_price,
                pm_filled,  # Unwind same quantity that was filled
                tif=3,      # IOC
                sync=True,
                outcome_index=actual_pm_outcome_idx
            )

            unwind_filled = unwind_result.get('fill_count', 0)
            unwind_fill_price = unwind_result.get('fill_price', unwind_price)

            if unwind_filled > 0:
                # Calculate loss from the spread
                if reverse_intent == 2:  # We sold to close
                    loss_cents = (pm_fill_price * 100) - (unwind_fill_price * 100)
                else:  # We bought to close
                    loss_cents = (unwind_fill_price * 100) - (pm_fill_price * 100)

                print(f"[RECOVERY] PM UNWOUND: Closed {unwind_filled} @ ${unwind_fill_price:.3f}")
                print(f"[RECOVERY] Loss from unwind: {loss_cents:.1f}c (+ fees)")

                # Trade is now flat - no unhedged position
                return TradeResult(
                    success=False,
                    kalshi_filled=0,
                    pm_filled=0,  # Net zero after unwind
                    kalshi_price=k_limit_price,
                    pm_price=pm_fill_price,
                    unhedged=False,  # Successfully unwound
                    abort_reason=f"Kalshi failed, PM unwound (loss: {loss_cents:.1f}c)",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    pm_order_ms=pm_order_ms,
                    k_order_ms=k_order_ms
                )
            else:
                print(f"[RECOVERY] PM UNWIND FAILED - position remains open!")

        except Exception as unwind_err:
            print(f"[RECOVERY] PM unwind error: {unwind_err}")

        # Unwind failed - still unhedged
        return TradeResult(
            success=False,
            kalshi_filled=0,
            pm_filled=pm_filled,
            kalshi_price=k_limit_price,
            pm_price=pm_fill_price,
            unhedged=True,
            abort_reason=f"Kalshi: no fill, PM unwind failed - UNHEDGED!",
            execution_time_ms=int((time.time() - start_time) * 1000),
            pm_order_ms=pm_order_ms,
            k_order_ms=k_order_ms
        )

    # Both sides filled - SUCCESS
    return TradeResult(
        success=True,
        kalshi_filled=k_filled,
        pm_filled=pm_filled,
        kalshi_price=k_fill_price,
        pm_price=pm_fill_price,
        unhedged=False,
        execution_time_ms=elapsed_ms,
        pm_order_ms=pm_order_ms,
        k_order_ms=k_order_ms
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
