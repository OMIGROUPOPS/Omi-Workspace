#!/usr/bin/env python3
"""
DUAL WEBSOCKET ARBITRAGE EXECUTOR
Uses Kalshi WebSocket + PM US WebSocket for real-time orderbook tracking.

Architecture:
  Kalshi WebSocket --> Local Orderbook --+
                                          +--> Spread Check --> Execute (PM first)
  PM US WebSocket --> PM Orderbook ------+

Both sides are event-driven. When either side updates, we check for spreads.
No REST polling delay. Sub-100ms latency on both sides.
"""
import asyncio
import aiohttp
import websockets
import time
import base64
import json
import os
import sys
import signal
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set, Tuple
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

import httpx  # available from PM SDK dependency
from dashboard_push import DashboardPusher
from espn_scores import ESPNScores
import orderbook_db

# Shared configuration - single source of truth
from config import Config, ExecutionMode

# Import from v7 - reuse as much as possible
from arb_executor_v7 import (
    # API Classes
    KalshiAPI,
    PolymarketUSAPI,

    # Core data structures
    ArbOpportunity,
    Position,

    # Profit/fee calculations
    estimate_net_profit_cents,
    calculate_actual_pnl,

    # Logging
    log_trade,
    log_skipped_arb,
    print_pnl_summary,
    TRADE_LOG,

    # Position tracking
    check_kill_switch,
    activate_kill_switch,
    save_unhedged_position,

    # Utilities
    normalize_team_abbrev,

    # Lock for sequential execution
    EXECUTION_LOCK,
)

# Clean execution engine - single source of truth for order placement
from executor_core import (
    execute_arb,
    calculate_optimal_size,
    TradeResult,
    TRADE_PARAMS,           # For computing settlement fields
    traded_games,           # Shared state - games traded this session
    blacklisted_games,      # Shared state - games blacklisted after crashes
    load_traded_games,      # Load persisted traded games on startup
    save_traded_game,       # Save traded game after successful trade
    refresh_position_cache, # Background position refresh (not on hot path)
    load_directional_positions,  # Load OMI directional positions on startup
    MIN_K_DEPTH_L1,         # Depth gate threshold for walk-based check
)

from pregame_mapper import load_verified_mappings, TEAM_FULL_NAMES
from verify_all_mappings import run_startup_verification, run_trade_verification

# ============================================================================
# WINDOWS UTF-8 FIX
# ============================================================================
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# WEBSOCKET CONFIG
# ============================================================================
KALSHI_WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
KALSHI_WS_PATH = "/trade-api/ws/v2"

PM_WS_URL = "wss://api.polymarket.us/v1/ws/markets"
PM_WS_PATH = "/v1/ws/markets"

PM_PRICE_MAX_AGE_MS = 2000  # Skip if PM price is older than 2 seconds (for safety)
K_PRICE_MAX_AGE_MS = 2000   # Skip if Kalshi price is older than 2 seconds

WS_RECONNECT_DELAY_INITIAL = 1  # Initial reconnect delay in seconds
WS_RECONNECT_DELAY_MAX = 60     # Max reconnect delay
WS_PING_INTERVAL = 30           # Send ping every 30 seconds

STATUS_LOG_INTERVAL = 30  # Log status every 30 seconds

# ============================================================================
# GLOBAL STATE
# ============================================================================

# Local orderbook state - updated by WebSocket
# Structure: ticker -> {yes_bids: {price: size}, yes_asks: {price: size}, best_bid, best_ask, ...}
local_books: Dict[str, Dict] = {}

# Latest PM prices - updated by WebSocket
# Structure: "{cache_key}_{team}" -> {bid, ask, bid_size, ask_size, timestamp_ms, pm_slug, outcome_index}
pm_prices: Dict[str, Dict] = {}

# Full PM orderbook depth - updated by WebSocket
# Structure: pm_slug -> {bids: [{price_cents, size}, ...], asks: [{price_cents, size}, ...], timestamp_ms}
pm_books: Dict[str, Dict] = {}

# Mapping from Kalshi ticker -> cache_key (for spread detection)
ticker_to_cache_key: Dict[str, str] = {}
# Mapping from cache_key -> list of kalshi tickers
cache_key_to_tickers: Dict[str, List[str]] = {}
# Mapping from PM slug -> list of cache_keys (for PM WS spread triggers)
pm_slug_to_cache_keys: Dict[str, List[str]] = {}

# Verified mappings
VERIFIED_MAPS: Dict = {}

# Games flagged for pm_long_team price mismatch — skip trading until manually verified
# Set of cache_keys where PM WS prices diverge from Kalshi by >15c on first arrival
price_mismatch_games: set = set()
# Track which cache_keys have already been sanity-checked (only check once per session)
_pm_price_checked: set = set()

# Signal file for hot-reload (written by auto_mapper.py)
MAPPINGS_SIGNAL_FILE = os.path.join(os.path.dirname(__file__) or '.', 'mappings_updated.flag')
_last_signal_check: float = 0
SIGNAL_CHECK_INTERVAL = 60  # Check every 60 seconds

# Per-game execution guard — prevents concurrent execution on the same game
# A cache_key is added before execution starts and removed in a finally block
executing_games: set = set()

# Tickers whose orderbook changed since last snapshot recording (drained by background task)
dirty_tickers: set = set()

# Per-team cooldown after SUCCESS — prevents re-trading same team too quickly
game_success_cooldown: Dict[str, float] = {}

# Per-team no-fill cooldown — exponential backoff on repeated PM no-fills
nofill_cooldown: Dict[str, float] = {}   # cooldown_key -> timestamp of last no-fill
nofill_count: Dict[str, int] = {}        # cooldown_key -> consecutive no-fill count
NOFILL_COOLDOWN_BASE = 30                # seconds (doubles per consecutive no-fill)
NOFILL_COOLDOWN_MAX = 300                # 5 minutes max cooldown
NOFILL_BLACKLIST_THRESHOLD = 10          # stop trading game after this many consecutive no-fills

# Live balances (refreshed periodically, read by dashboard pusher)
live_balances: Dict = {
    "kalshi_balance": 0, "pm_balance": 0,  # backwards-compat (used by sizing)
    "k_cash": 0, "k_portfolio": 0,
    "pm_cash": 0, "pm_portfolio": 0,
    "updated_at": "",
}
# Live positions fetched from platform APIs (list of Position dicts for dashboard)
live_positions: list = []
_last_balance_refresh: float = 0
BALANCE_REFRESH_INTERVAL = 60  # seconds

# Statistics
stats = {
    'k_ws_connected': False,
    'k_ws_messages': 0,
    'pm_ws_connected': False,
    'pm_ws_messages': 0,
    'spreads_detected': 0,
    'spreads_executed': 0,
    'last_status_log': 0,
}

# Spread watch tracking (for data collection)
spread_watch_stats = {
    '2-3c': 0,  # Spreads 2c to <3c
    '3-4c': 0,  # Spreads 3c to <4c
    '4c+': 0,   # Spreads 4c+ (execution threshold)
}

# CSV file for spread watching
SPREAD_WATCH_FILE = os.path.join(os.path.dirname(__file__) or '.', 'spread_watch.csv')
_spread_watch_file_initialized = False

# Deduplication: track last logged spread per game/team to avoid spam
# Key: (game, team), Value: (last_spread_cents, last_log_time)
_last_logged_spreads: Dict[Tuple[str, str], Tuple[float, float]] = {}
SPREAD_LOG_COOLDOWN_SECONDS = 30  # Only log same game/team once per 30 seconds


def log_spread_watch(game: str, team: str, direction: str, spread_cents: float,
                     k_price: int, pm_price: float, pm_size: int, is_long_team: bool):
    """Log a watched spread to CSV for later analysis (with deduplication)."""
    global _spread_watch_file_initialized

    # Deduplication check - only log if spread changed significantly or enough time passed
    now = time.time()
    key = (game, team)
    if key in _last_logged_spreads:
        last_spread, last_time = _last_logged_spreads[key]
        # Skip if same spread level (within 0.5c) and logged within cooldown
        if abs(spread_cents - last_spread) < 0.5 and (now - last_time) < SPREAD_LOG_COOLDOWN_SECONDS:
            return  # Skip duplicate

    # Update dedup tracking
    _last_logged_spreads[key] = (spread_cents, now)

    # Initialize CSV with header if needed
    if not _spread_watch_file_initialized:
        if not os.path.exists(SPREAD_WATCH_FILE):
            with open(SPREAD_WATCH_FILE, 'w') as f:
                f.write('timestamp,game,team,direction,spread_cents,k_price,pm_price,pm_size,is_long_team\n')
        _spread_watch_file_initialized = True

    # Append row
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(SPREAD_WATCH_FILE, 'a') as f:
        f.write(f'{timestamp},{game},{team},{direction},{spread_cents:.1f},{k_price},{pm_price:.1f},{pm_size},{is_long_team}\n')

# Cooldown tracking
last_trade_time = 0
# Note: traded_games and blacklisted_games are imported from executor_core

# Execution mode is now controlled via Config (from config.py)
# All functions should use Config.is_live(), Config.is_paper(), etc.

# Shutdown flag
shutdown_requested = False

# One-trade test mode flag
ONE_TRADE_TEST_MODE = False

# Max trades limit (0 = unlimited)
MAX_TRADES_LIMIT = 0


# ============================================================================
# OMI EDGE SIGNAL CACHE
# ============================================================================

class OmiSignalCache:
    """Pre-cached OMI Edge signals. All lookups are local dict reads (0ms)."""

    def __init__(self):
        self.signals = {}           # keyed by lowercase team name → signal dict
        self.last_refresh = 0
        self.refresh_interval_idle = 900   # 15 min when no live games
        self.refresh_interval_live = 30    # 30s when games are live
        self.api_url = "https://omi-workspace-production.up.railway.app/api/v1/edge-signal/bulk?sport=NCAAB"
        self.api_key = os.environ.get("OMI_API_KEY", "SkvEI04AmE0lOsOuHsSNmLwsUkDh_6Q_n1wyQBZK8rU")
        self._refreshing = False    # Guard against concurrent refreshes
        # Build abbreviation → full name reverse lookup from TEAM_FULL_NAMES
        self._abbrev_to_full: dict[str, str] = {}
        for abbrev, full in TEAM_FULL_NAMES.items():
            self._abbrev_to_full[abbrev.lower()] = full.lower()

    async def refresh(self) -> bool:
        """Fetch all signals from OMI Edge API and rebuild local cache."""
        if self._refreshing:
            return False
        self._refreshing = True
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
            signals_list = data.get("signals", data.get("games", data if isinstance(data, list) else []))
            new_cache = {}
            for s in signals_list:
                home = s.get("home_team", "").lower().strip()
                away = s.get("away_team", "").lower().strip()
                if home:
                    new_cache[home] = s
                if away:
                    new_cache[away] = s
            self.signals = new_cache
            self.last_refresh = time.time()
            live_count = data.get("live_count", 0)
            print(f"[OMI] Cache refreshed: {len(signals_list)} games, {live_count} live")
            return any(s.get("game_status") == "live" for s in signals_list)
        except Exception as e:
            print(f"[OMI] Cache refresh failed: {e}")
            return False
        finally:
            self._refreshing = False

    def get_signal(self, team_name: str) -> dict | None:
        """Look up signal by team name. Tries exact, abbreviation, then substring."""
        key = team_name.lower().strip()
        if key in self.signals:
            return self.signals[key]
        # Try abbreviation → full name lookup (e.g. "uk" → "kentucky wildcats")
        full = self._abbrev_to_full.get(key)
        if full and full in self.signals:
            return self.signals[full]
        # Substring match (existing fallback)
        for cached_key, signal in self.signals.items():
            if key in cached_key or cached_key in key:
                return signal
        return None

    def get_effective_ceq(self, signal: dict) -> float:
        """Return best_edge_pct (0-15 scale). Used for pregame thresholds and position sizing."""
        edge = signal.get("best_edge_pct", 0) or 0
        return float(edge)

    def get_live_ceq(self, signal: dict) -> float | None:
        """Return live_ceq (0-100 scale) or None if not live."""
        if signal.get("game_status") == "live" and signal.get("live"):
            live_ceq = signal["live"].get("live_ceq")
            if live_ceq is not None:
                return float(live_ceq)
        return None

    def get_hold_signal(self, signal: dict) -> str | None:
        """Return live hold_signal (STRONG_HOLD/HOLD/UNWIND/URGENT_UNWIND) or None."""
        if signal.get("game_status") == "live" and signal.get("live"):
            return signal["live"].get("hold_signal")
        return None

    @property
    def has_live_games(self) -> bool:
        """Check if any cached signal has game_status == 'live'."""
        seen = set()
        for s in self.signals.values():
            sid = id(s)
            if sid in seen:
                continue
            seen.add(sid)
            if isinstance(s, dict) and s.get("game_status") == "live":
                return True
        return False

    def get_flow_gated(self, signal: dict) -> bool:
        """Return True if sharp money flow doesn't confirm the edge."""
        return bool(signal.get("flow_gated", False))

    def get_favored_team(self, signal: dict) -> str:
        """Derive favored team from favored_side field."""
        side = signal.get("favored_side", "")
        if side == "home":
            return signal.get("home_team", "")
        elif side == "away":
            return signal.get("away_team", "")
        return ""

    def is_stale(self) -> bool:
        if self.last_refresh == 0:
            return True
        interval = self.refresh_interval_live if self.has_live_games else self.refresh_interval_idle
        return time.time() - self.last_refresh > interval


# Module-level OMI cache instance
omi_cache = OmiSignalCache()


# ============================================================================
# LOCAL ORDERBOOK MANAGEMENT
# ============================================================================

def init_orderbook(ticker: str) -> Dict:
    """Initialize empty orderbook structure for a ticker"""
    return {
        'yes_bids': {},  # price (cents) -> size
        'yes_asks': {},  # price (cents) -> size
        'best_bid': None,
        'best_bid_size': 0,
        'best_ask': None,
        'best_ask_size': 0,
        'last_update_ms': 0,
    }


def apply_orderbook_snapshot(ticker: str, snapshot: Dict):
    """Apply full orderbook snapshot from WebSocket

    Kalshi WS format:
    - 'yes': [[price, depth], ...] - YES side bids (buy YES orders)
    - 'no': [[price, depth], ...] - NO side bids (buy NO = sell YES orders)

    To get YES orderbook:
    - best_bid = max price in 'yes' array (highest someone will pay for YES)
    - best_ask = 100 - max price in 'no' array (lowest someone will sell YES)
    """
    book = init_orderbook(ticker)

    # Parse YES side bids - format: [[price, depth], ...]
    yes_data = snapshot.get('yes', [])
    for level in yes_data:
        if isinstance(level, list) and len(level) >= 2:
            price, size = int(level[0]), int(level[1])
            if size > 0:
                book['yes_bids'][price] = size

    # Parse NO side bids - these imply YES asks
    # If someone bids 40c for NO, that implies a 60c ask for YES
    no_data = snapshot.get('no', [])
    for level in no_data:
        if isinstance(level, list) and len(level) >= 2:
            no_price, size = int(level[0]), int(level[1])
            yes_ask_price = 100 - no_price  # Invert to get YES ask price
            if size > 0:
                book['yes_asks'][yes_ask_price] = size

    recalculate_best_prices(book)
    book['last_update_ms'] = int(time.time() * 1000)
    local_books[ticker] = book

    return book


def apply_orderbook_delta(ticker: str, delta: Dict):
    """Apply incremental orderbook update from WebSocket

    Kalshi delta format:
    - 'price': price in cents
    - 'delta': change in size (can be negative)
    - 'side': 'yes' or 'no'

    YES side deltas affect yes_bids
    NO side deltas affect yes_asks (inverted price: 100 - no_price)
    """
    if ticker not in local_books:
        local_books[ticker] = init_orderbook(ticker)

    book = local_books[ticker]

    price = delta.get('price')
    size_delta = delta.get('delta', 0)  # Can be negative
    side = delta.get('side', 'yes').lower()

    if price is None:
        return book

    price = int(price)

    # YES side updates affect yes_bids
    # NO side updates affect yes_asks (with price inversion)
    if side == 'yes':
        target = book['yes_bids']
        target_price = price
    elif side == 'no':
        target = book['yes_asks']
        target_price = 100 - price  # Invert: NO at 40 = YES ask at 60
    else:
        return book

    # Apply delta
    if size_delta != 0:
        current = target.get(target_price, 0)
        new_val = current + int(size_delta)
        if new_val <= 0:
            target.pop(target_price, None)
        else:
            target[target_price] = new_val

    recalculate_best_prices(book)
    book['last_update_ms'] = int(time.time() * 1000)

    return book


def recalculate_best_prices(book: Dict):
    """Recalculate best bid/ask from orderbook"""
    # Best bid = highest price someone is willing to buy at
    if book['yes_bids']:
        best_bid = max(book['yes_bids'].keys())
        book['best_bid'] = best_bid
        book['best_bid_size'] = book['yes_bids'][best_bid]
    else:
        book['best_bid'] = None
        book['best_bid_size'] = 0

    # Best ask = lowest price someone is willing to sell at
    if book['yes_asks']:
        best_ask = min(book['yes_asks'].keys())
        book['best_ask'] = best_ask
        book['best_ask_size'] = book['yes_asks'][best_ask]
    else:
        book['best_ask'] = None
        book['best_ask_size'] = 0


# ============================================================================
# ORDERBOOK SNAPSHOT RECORDING
# ============================================================================

def _record_kalshi_snapshot(ticker: str):
    """Record a Kalshi orderbook snapshot to SQLite (throttled by orderbook_db)."""
    book = local_books.get(ticker)
    if not book:
        return
    best_bid = book.get('best_bid') or 0
    best_ask = book.get('best_ask') or 0
    if best_bid == 0 or best_ask == 0:
        return

    parts = ticker.split("-")
    game_id = parts[1] if len(parts) >= 2 else ticker

    bids = book.get('yes_bids', {})
    bid_levels = sorted(bids.items(), key=lambda x: -x[0])[:5]
    bid_depth = sum(bids.values())

    asks = book.get('yes_asks', {})
    ask_levels = sorted(asks.items(), key=lambda x: x[0])[:5]
    ask_depth = sum(asks.values())

    orderbook_db.record_snapshot(
        game_id=game_id,
        platform='kalshi',
        best_bid=best_bid,
        best_ask=best_ask,
        bid_depth=bid_depth,
        ask_depth=ask_depth,
        bid_levels_json=json.dumps([{"price": p, "size": s} for p, s in bid_levels]),
        ask_levels_json=json.dumps([{"price": p, "size": s} for p, s in ask_levels]),
        spread=best_ask - best_bid,
    )


def _record_pm_snapshot(pm_slug: str, market_data: Dict):
    """Record a PM orderbook snapshot to SQLite (throttled by orderbook_db)."""
    bids = market_data.get("bids", [])
    offers = market_data.get("offers", [])
    if not bids or not offers:
        return

    sorted_bids = sorted(bids, key=lambda x: float(x["px"]["value"]), reverse=True)
    sorted_offers = sorted(offers, key=lambda x: float(x["px"]["value"]))

    best_bid = round(float(sorted_bids[0]["px"]["value"]) * 100)
    best_ask = round(float(sorted_offers[0]["px"]["value"]) * 100)

    bid_depth = sum(int(float(b["qty"])) for b in sorted_bids)
    ask_depth = sum(int(float(o["qty"])) for o in sorted_offers)

    bid_levels = [{"price": round(float(b["px"]["value"]) * 100), "size": int(float(b["qty"]))} for b in sorted_bids[:5]]
    ask_levels = [{"price": round(float(o["px"]["value"]) * 100), "size": int(float(o["qty"]))} for o in sorted_offers[:5]]

    orderbook_db.record_snapshot(
        game_id=pm_slug,
        platform='pm',
        best_bid=best_bid,
        best_ask=best_ask,
        bid_depth=bid_depth,
        ask_depth=ask_depth,
        bid_levels_json=json.dumps(bid_levels),
        ask_levels_json=json.dumps(ask_levels),
        spread=best_ask - best_bid,
    )


async def periodic_snapshot_recorder():
    """Background task: drain dirty_tickers and record Kalshi snapshots every 5s.

    Keeps snapshot recording off the WS hot path — the WS handler just does
    dirty_tickers.add(ticker) (O(1) set op) instead of building JSON + writing SQLite.
    """
    while not shutdown_requested:
        await asyncio.sleep(5)
        # Atomically swap the dirty set
        batch = dirty_tickers.copy()
        dirty_tickers.clear()
        for ticker in batch:
            try:
                _record_kalshi_snapshot(ticker)
            except Exception:
                pass  # Best-effort — don't crash background task


# ============================================================================
# PM PRICE MANAGEMENT
# ============================================================================

def update_pm_price(cache_key: str, team: str, bid: float, ask: float,
                    bid_size: int, ask_size: int, pm_slug: str, outcome_index: int,
                    pm_long_team: str = ""):
    """Update PM price for a team"""
    key = f"{cache_key}_{team}"
    pm_prices[key] = {
        'bid': bid,  # cents
        'ask': ask,  # cents
        'bid_size': bid_size,
        'ask_size': ask_size,
        'timestamp_ms': int(time.time() * 1000),
        'pm_slug': pm_slug,
        'outcome_index': outcome_index,
        'cache_key': cache_key,
        'team': team,
        'pm_long_team': pm_long_team,  # Team with long=true in PM marketSides
    }


def get_pm_price(cache_key: str, team: str) -> Optional[Dict]:
    """Get latest PM price for a team, checking staleness"""
    key = f"{cache_key}_{team}"
    price_data = pm_prices.get(key)

    if not price_data:
        return None

    age_ms = int(time.time() * 1000) - price_data['timestamp_ms']
    if age_ms > PM_PRICE_MAX_AGE_MS:
        return None  # Too stale

    return price_data


async def confirm_pm_price_fresh(
    session: aiohttp.ClientSession,
    pm_api,
    arb: 'ArbOpportunity'
) -> Tuple[Optional[Dict], float]:
    """
    Fetch fresh PM orderbook for a single market to confirm spread is real.

    Returns:
        (fresh_pm_data, confirm_time_ms) where fresh_pm_data contains:
        - bid, ask, bid_size, ask_size (in cents)
        - or None if fetch failed
    """
    start = time.time()

    try:
        # Fetch orderbook for just this one slug
        orderbooks = await pm_api.get_orderbooks_batch(session, [arb.pm_slug], debug=False)

        ob = orderbooks.get(arb.pm_slug)
        if not ob or ob.get('best_bid') is None or ob.get('best_ask') is None:
            return None, (time.time() - start) * 1000

        # Convert prices to cents
        best_bid = int(ob['best_bid'] * 100) if ob['best_bid'] < 1 else int(ob['best_bid'])
        best_ask = int(ob['best_ask'] * 100) if ob['best_ask'] < 1 else int(ob['best_ask'])
        bid_size = ob.get('bid_size', 0)
        ask_size = ob.get('ask_size', 0)

        # Determine if this team is the PM long team (team with long=true in marketSides)
        # PM API always returns prices for pm_long_team, so we invert if trading the other team
        # CRITICAL: Use pm_long_team, NOT slug position! pm_long_team can be either team.
        is_long_team = (arb.team == arb.pm_long_team)

        # Apply price inversion if trading the non-long team
        if is_long_team:
            fresh_bid = best_bid
            fresh_ask = best_ask
            fresh_bid_size = bid_size
            fresh_ask_size = ask_size
        else:
            fresh_bid = 100 - best_ask
            fresh_ask = 100 - best_bid
            fresh_bid_size = ask_size
            fresh_ask_size = bid_size

        confirm_time = (time.time() - start) * 1000

        return {
            'bid': fresh_bid,
            'ask': fresh_ask,
            'bid_size': fresh_bid_size,
            'ask_size': fresh_ask_size,
        }, confirm_time

    except Exception as e:
        return None, (time.time() - start) * 1000


def recalculate_spread_with_fresh_pm(arb: 'ArbOpportunity', fresh_pm: Dict) -> Tuple[int, str]:
    """
    Recalculate spread using fresh PM prices.

    CRITICAL: Spread depends on whether team == pm_long_team!
    - BUY_YES on PM: cost = price paid
    - SELL_YES on PM: cost = 100 - price received (the risk)

    Returns:
        (new_spread_cents, direction) - the best spread and its direction
    """
    k_bid = arb.k_bid
    k_ask = arb.k_ask
    pm_bid = fresh_pm['bid']
    pm_ask = fresh_pm['ask']

    is_long_team = (arb.team == arb.pm_long_team)

    # Calculate spreads for both directions using correct formulas
    if is_long_team:
        spread_buy_pm = k_bid - pm_ask        # Case 1: BUY_LONG on PM
        spread_buy_k = pm_bid - k_ask         # Case 3: BUY_SHORT on PM
    else:
        spread_buy_pm = k_bid - pm_ask        # Case 2: BUY_SHORT on PM (pm_ask already inverted)
        spread_buy_k = pm_bid - k_ask         # Case 4: BUY_LONG on PM

    # Return spread for the specified direction
    if arb.direction == 'BUY_PM_SELL_K':
        return spread_buy_pm, 'BUY_PM_SELL_K'
    else:
        return spread_buy_k, 'BUY_K_SELL_PM'


# ============================================================================
# SPREAD DETECTION (EVENT-DRIVEN)
# ============================================================================

def quick_spread_possible(ticker: str) -> bool:
    """
    Lightweight pre-check: can this ticker possibly produce a spread >= exec_min?

    Avoids the full check_spread_for_ticker overhead (mapping lookup, PM price fetch,
    sport detection, ArbOpportunity construction) for ~95% of WS messages where
    no spread is possible.

    Only uses in-memory dicts — no allocations, no I/O.
    """
    book = local_books.get(ticker)
    if not book:
        return False

    k_bid = book.get('best_bid') or 0
    k_ask = book.get('best_ask') or 0
    if k_bid == 0 and k_ask == 0:
        return False

    # Skip stale Kalshi books
    k_age_ms = int(time.time() * 1000) - book.get('last_update_ms', 0)
    if k_age_ms > K_PRICE_MAX_AGE_MS:
        return False

    cache_key = ticker_to_cache_key.get(ticker)
    if not cache_key:
        return False

    # Extract team from ticker (e.g., KXNBAGAME-26FEB05PHILAL-PHI -> PHI)
    parts = ticker.split('-')
    if len(parts) < 3:
        return False
    team = parts[-1]

    pm_data = pm_prices.get(f"{cache_key}_{team}")
    if not pm_data:
        return False

    pm_bid = pm_data.get('bid') or 0
    pm_ask = pm_data.get('ask') or 0

    threshold = Config.spread_log_min_cents  # 2c — same as check_spread_for_ticker uses

    # BUY_PM_SELL_K: spread = k_bid - pm_ask
    if k_bid > 0 and pm_ask > 0 and (k_bid - pm_ask) >= threshold:
        return True
    # BUY_K_SELL_PM: spread = pm_bid - k_ask
    if pm_bid > 0 and k_ask > 0 and (pm_bid - k_ask) >= threshold:
        return True

    return False


def check_spread_for_ticker(ticker: str) -> Optional[ArbOpportunity]:
    """
    Check for arbitrage opportunity on a specific ticker.
    Called immediately after receiving a Kalshi orderbook update.

    Returns ArbOpportunity if spread >= threshold and liquidity exists, else None.
    """
    global stats

    # Get local book
    book = local_books.get(ticker)
    if not book or book['best_bid'] is None or book['best_ask'] is None:
        return None

    # Skip stale Kalshi books
    k_age_ms = int(time.time() * 1000) - book.get('last_update_ms', 0)
    if k_age_ms > K_PRICE_MAX_AGE_MS:
        return None

    # Find the cache_key for this ticker
    cache_key = ticker_to_cache_key.get(ticker)
    if not cache_key:
        return None

    # Get the mapping
    mapping = VERIFIED_MAPS.get(cache_key)
    if not mapping or not mapping.get('verified'):
        return None

    # Extract team from ticker (e.g., KXNBAGAME-26FEB05PHILAL-PHI -> PHI)
    ticker_parts = ticker.split('-')
    if len(ticker_parts) < 3:
        return None
    team = ticker_parts[-1]

    # Get PM price for this team
    pm_data = get_pm_price(cache_key, team)
    if not pm_data:
        return None

    k_bid = book['best_bid']
    k_ask = book['best_ask']
    k_bid_size = book['best_bid_size']
    k_ask_size = book['best_ask_size']

    pm_bid = pm_data['bid']  # cents
    pm_ask = pm_data['ask']  # cents
    pm_bid_size = pm_data['bid_size']
    pm_ask_size = pm_data['ask_size']
    pm_slug = pm_data['pm_slug']
    pm_outcome_index = pm_data['outcome_index']
    pm_long_team = pm_data.get('pm_long_team', '')  # Team with long=true in PM

    # Calculate spreads for both directions
    # CRITICAL: Spread depends on whether team == pm_long_team!
    # - BUY_YES on PM: cost = price paid
    # - SELL_YES on PM: cost = 100 - price received (the risk if counterparty wins)

    is_long_team = (team == pm_long_team)

    # BUY_PM_SELL_K: Go LONG team on PM, SHORT team on Kalshi
    # Kalshi: SELL YES at k_bid (receive k_bid)
    # PM: depends on is_long_team
    if is_long_team:
        # Case 1: PM BUY_LONG (intent=1) at pm_ask
        # Profit = k_bid - pm_ask
        spread_buy_pm = k_bid - pm_ask
    else:
        # Case 2: PM BUY_SHORT (intent=3) to short favorite = long underdog; cost from pm_ask
        # Profit = k_bid - pm_ask
        spread_buy_pm = k_bid - pm_ask

    # BUY_K_SELL_PM: Go LONG team on Kalshi, SHORT team on PM
    # Kalshi: BUY YES at k_ask (pay k_ask)
    # PM: depends on is_long_team
    if is_long_team:
        # Case 3: PM BUY_SHORT (intent=3) to short long_team
        # Pay underdog_ask = 100 - pm_bid
        # Profit = pm_bid - k_ask
        spread_buy_k = pm_bid - k_ask
    else:
        # Case 4: PM BUY_LONG (intent=1) at long_team_ask = 100 - pm_bid
        # pm_bid is our team's (underdog's) bid
        # Profit = 100 - k_ask - (100 - pm_bid) = pm_bid - k_ask
        spread_buy_k = pm_bid - k_ask

    # Get configured thresholds
    log_min = Config.spread_log_min_cents   # Watch threshold (2c)
    exec_min = Config.spread_min_cents      # Execute threshold (4c)

    # Find best EXECUTABLE spread (all 4 cases now executable with BUY_SHORT)
    best_spread = None
    best_direction = None

    # Check BUY_PM_SELL_K (Case 1: BUY_LONG favorite, Case 2: BUY_SHORT favorite = long underdog)
    if spread_buy_pm >= log_min and k_bid_size >= 1:
        best_spread = spread_buy_pm
        best_direction = 'BUY_PM_SELL_K'

    # Check BUY_K_SELL_PM (Case 3: is_long_team uses BUY_SHORT, Case 4: uses BUY_LONG)
    if spread_buy_k >= log_min and k_ask_size >= 1:
        if best_spread is None or spread_buy_k > best_spread:
            best_spread = spread_buy_k
            best_direction = 'BUY_K_SELL_PM'

    if best_spread is None:
        return None

    # Skip thin PM liquidity - price will move before we can execute
    MIN_PM_SIZE = 50  # minimum contracts at the price we'd trade
    if best_direction == 'BUY_PM_SELL_K':
        if pm_ask_size < MIN_PM_SIZE:
            return None  # PM ask too thin
        pm_size_for_watch = pm_ask_size
        pm_price_for_watch = pm_ask
        k_price_for_watch = k_bid
    else:  # BUY_K_SELL_PM
        if pm_bid_size < MIN_PM_SIZE:
            return None  # PM bid too thin
        pm_size_for_watch = pm_bid_size
        pm_price_for_watch = pm_bid
        k_price_for_watch = k_ask

    # Track spread in watch stats and log to CSV
    if best_spread >= 2 and best_spread < 3:
        spread_watch_stats['2-3c'] += 1
    elif best_spread >= 3 and best_spread < 4:
        spread_watch_stats['3-4c'] += 1
    elif best_spread >= 4:
        spread_watch_stats['4c+'] += 1

    # Only proceed to execution if spread >= exec_min
    if best_spread < exec_min:
        log_spread_watch(ticker_parts[1] if len(ticker_parts) >= 2 else ticker,
                        team, best_direction, best_spread, k_price_for_watch,
                        pm_price_for_watch, pm_size_for_watch, is_long_team)
        print(f"[SPREAD-WATCH] {ticker_parts[1] if len(ticker_parts) >= 2 else ticker} {team}: {best_spread:.1f}c {best_direction} (below {exec_min}c threshold)", flush=True)
        return None

    stats['spreads_detected'] += 1

    # Determine which PM price to use based on direction
    if best_direction == 'BUY_PM_SELL_K':
        pm_price_for_arb = pm_ask
        k_price_for_arb = k_bid
        k_size = k_bid_size
        pm_size = pm_ask_size
    else:
        pm_price_for_arb = pm_bid
        k_price_for_arb = k_ask
        k_size = k_ask_size
        pm_size = pm_bid_size

    # Build ArbOpportunity
    # Extract game ID from ticker
    game_id = ticker_parts[1] if len(ticker_parts) >= 2 else ticker

    # Determine sport from series
    sport = 'NBA'
    if 'NHL' in ticker:
        sport = 'NHL'
    elif 'NCAAMB' in ticker:
        sport = 'CBB'

    arb = ArbOpportunity(
        timestamp=datetime.now(),
        game=game_id,
        team=team,
        sport=sport,
        direction=best_direction,
        k_bid=k_bid,
        k_ask=k_ask,
        pm_bid=pm_bid,
        pm_ask=pm_ask,
        gross_spread=best_spread,
        fees=0,  # Will be calculated in profit estimation
        net_spread=best_spread,
        size=min(k_size, pm_size, Config.max_contracts),
        kalshi_ticker=ticker,
        pm_slug=pm_slug,
        pm_outcome_index=pm_outcome_index,
        price_timestamp=time.time(),
        k_bid_size=k_bid_size,
        k_ask_size=k_ask_size,
        pm_bid_size=pm_bid_size,
        pm_ask_size=pm_ask_size,
        pm_long_team=pm_long_team,  # Team with long=true - determines BUY_YES vs SELL_YES
        cache_key=cache_key,  # For verified mappings lookup
    )

    return arb


# ============================================================================
# KALSHI WEBSOCKET CONNECTION
# ============================================================================

class KalshiWebSocket:
    """Manages Kalshi WebSocket connection with auto-reconnect"""

    def __init__(self, api_key: str, private_key_pem: str):
        self.api_key = api_key
        self.private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )
        self.ws = None
        self.connected = False
        self.subscribed_tickers: Set[str] = set()
        self.reconnect_delay = WS_RECONNECT_DELAY_INITIAL
        self.message_id = 0
        self.on_spread_detected = None  # Callback for spread detection
        self._last_resub = time.time()  # Track periodic re-subscribe for book freshness

    def _sign(self, ts: str, method: str, path: str) -> str:
        """Generate RSA-PSS signature"""
        msg = f'{ts}{method}{path}'.encode('utf-8')
        sig = self.private_key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')

    def _get_auth_headers(self) -> Dict:
        """Generate WebSocket authentication headers"""
        ts = str(int(time.time() * 1000))
        return {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-SIGNATURE': self._sign(ts, 'GET', KALSHI_WS_PATH),
            'KALSHI-ACCESS-TIMESTAMP': ts,
        }

    async def connect(self):
        """Connect to Kalshi WebSocket"""
        global stats

        headers = self._get_auth_headers()

        try:
            print(f"[WS] Connecting to {KALSHI_WS_URL}...")
            self.ws = await websockets.connect(
                KALSHI_WS_URL,
                additional_headers=headers,
                ping_interval=WS_PING_INTERVAL,
                ping_timeout=10,
            )
            self.connected = True
            self.reconnect_delay = WS_RECONNECT_DELAY_INITIAL
            stats['k_ws_connected'] = True
            stats['ws_connect_time'] = time.time()
            print(f"[WS] Connected to Kalshi WebSocket")
            return True
        except Exception as e:
            print(f"[WS] Connection failed: {e}")
            self.connected = False
            stats['k_ws_connected'] = False
            return False

    async def subscribe(self, tickers: List[str]):
        """Subscribe to orderbook_delta for given tickers"""
        if not self.connected or not self.ws:
            return False

        # Clear local books for fresh subscriptions
        for ticker in tickers:
            local_books[ticker] = init_orderbook(ticker)

        self.message_id += 1
        subscribe_msg = {
            "id": self.message_id,
            "cmd": "subscribe",
            "params": {
                "channels": ["orderbook_delta"],
                "market_tickers": tickers
            }
        }

        try:
            await self.ws.send(json.dumps(subscribe_msg))
            self.subscribed_tickers.update(tickers)
            print(f"[WS] Subscribed to {len(tickers)} tickers")
            return True
        except Exception as e:
            print(f"[WS] Subscribe failed: {e}")
            return False

    async def listen(self):
        """Listen for WebSocket messages"""
        global stats, shutdown_requested

        while not shutdown_requested:
            if not self.connected or not self.ws:
                # Try to reconnect
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, WS_RECONNECT_DELAY_MAX)

                if await self.connect():
                    # Resubscribe
                    if self.subscribed_tickers:
                        await self.subscribe(list(self.subscribed_tickers))
                continue

            # Periodic re-subscribe to force fresh orderbook snapshots
            now = time.time()
            if now - self._last_resub >= 60 and self.subscribed_tickers:
                active = [t for t in self.subscribed_tickers
                          if (local_books.get(t, {}).get('best_bid') or 0) > 0]
                if active:
                    resub_batch = active[:50]
                    try:
                        await self.subscribe(resub_batch)
                        print(f"[WS] Periodic re-subscribe: {len(resub_batch)}/{len(self.subscribed_tickers)} active tickers (book refresh)")
                    except Exception as e:
                        print(f"[WS] Periodic re-subscribe failed: {e}")
                self._last_resub = now

            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=60)
                stats['k_ws_messages'] += 1

                data = json.loads(msg)
                msg_type = data.get('type', '')
                msg_data = data.get('msg', {})

                if msg_type == 'orderbook_snapshot':
                    ticker = msg_data.get('market_ticker')
                    if ticker:
                        apply_orderbook_snapshot(ticker, msg_data)
                        dirty_tickers.add(ticker)
                        # Check for spread after snapshot
                        if quick_spread_possible(ticker):
                            arb = check_spread_for_ticker(ticker)
                            if arb and self.on_spread_detected:
                                asyncio.create_task(self.on_spread_detected(arb))

                elif msg_type == 'orderbook_delta':
                    ticker = msg_data.get('market_ticker')
                    if ticker:
                        apply_orderbook_delta(ticker, msg_data)
                        dirty_tickers.add(ticker)
                        # Check for spread after every delta - this is the key!
                        if quick_spread_possible(ticker):
                            arb = check_spread_for_ticker(ticker)
                            if arb and self.on_spread_detected:
                                asyncio.create_task(self.on_spread_detected(arb))

                elif msg_type == 'subscribed':
                    print(f"[WS] Subscription confirmed: {msg_data}")

                elif msg_type == 'error':
                    print(f"[WS] Error: {msg_data}")

            except asyncio.TimeoutError:
                # No message received, connection might be stale
                continue
            except websockets.exceptions.ConnectionClosed as e:
                print(f"[WS] Connection closed: {e}")
                self.connected = False
                stats['k_ws_connected'] = False
            except Exception as e:
                print(f"[WS] Error processing message: {e}")

    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
        self.connected = False
        stats['k_ws_connected'] = False


# ============================================================================
# PM US WEBSOCKET
# ============================================================================

# Import Ed25519 for PM WebSocket auth
from cryptography.hazmat.primitives.asymmetric import ed25519

class PMWebSocket:
    """Manages PM US WebSocket connection for real-time orderbook data"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        # Parse Ed25519 private key from base64 secret
        secret_bytes = base64.b64decode(secret_key)
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_bytes[:32])
        self.ws = None
        self.connected = False
        self.reconnect_delay = WS_RECONNECT_DELAY_INITIAL
        self.on_spread_detected = None  # Callback for spread detection
        # Subscription health tracking
        self._subscribed_slugs: set = set()
        self._slug_last_data: Dict[str, float] = {}  # slug -> last data timestamp

    def _sign(self, ts: str, method: str, path: str) -> str:
        """Sign message with Ed25519"""
        message = f'{ts}{method}{path}'.encode('utf-8')
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode('utf-8')

    def _get_auth_headers(self) -> Dict:
        """Generate WebSocket authentication headers"""
        ts = str(int(time.time() * 1000))
        return {
            'X-PM-Access-Key': self.api_key,
            'X-PM-Timestamp': ts,
            'X-PM-Signature': self._sign(ts, 'GET', PM_WS_PATH),
        }

    async def connect(self):
        """Connect to PM US WebSocket"""
        global stats

        headers = self._get_auth_headers()

        try:
            print(f"[PM WS] Connecting to {PM_WS_URL}...")
            self.ws = await websockets.connect(
                PM_WS_URL,
                additional_headers=headers,
                ping_interval=WS_PING_INTERVAL,
                ping_timeout=10,
            )
            self.connected = True
            self.reconnect_delay = WS_RECONNECT_DELAY_INITIAL
            stats['pm_ws_connected'] = True
            print(f"[PM WS] Connected!")
            return True
        except Exception as e:
            print(f"[PM WS] Connection failed: {e}")
            self.connected = False
            stats['pm_ws_connected'] = False
            return False

    async def subscribe(self, slugs: List[str]):
        """Subscribe to market data in batches of 10 to avoid server limits"""
        if not self.connected or not self.ws:
            return False

        BATCH_SIZE = 10
        total = len(slugs)
        ok = 0

        for i in range(0, total, BATCH_SIZE):
            batch = slugs[i:i + BATCH_SIZE]
            subscribe_msg = {
                "subscribe": {
                    "request_id": f"arb-sub-{i // BATCH_SIZE}",
                    "subscription_type": 1,  # MARKET_DATA (full orderbook)
                    "market_slugs": batch
                }
            }
            try:
                await self.ws.send(json.dumps(subscribe_msg))
                ok += len(batch)
                self._subscribed_slugs.update(batch)
                if i + BATCH_SIZE < total:
                    await asyncio.sleep(0.3)  # 300ms between batches
            except Exception as e:
                print(f"[PM WS] Subscribe batch {i // BATCH_SIZE} failed: {e}")
                return False

        print(f"[PM WS] Subscribed to {ok}/{total} markets in {(total + BATCH_SIZE - 1) // BATCH_SIZE} batches")
        return True

    async def log_subscription_health(self, delay: float = 5.0):
        """After subscribing, wait and report which markets responded"""
        await asyncio.sleep(delay)
        responding = set()
        silent = set()
        for slug in self._subscribed_slugs:
            if slug in self._slug_last_data:
                responding.add(slug)
            else:
                silent.add(slug)
        print(f"[PM WS HEALTH] {len(responding)}/{len(self._subscribed_slugs)} markets responding after {delay}s")
        if silent:
            print(f"[PM WS HEALTH] SILENT markets ({len(silent)}): {sorted(silent)}", flush=True)
        if responding:
            print(f"[PM WS HEALTH] Responding ({len(responding)}): {sorted(responding)}", flush=True)

    def get_silent_slugs(self, threshold_s: float = 30.0) -> List[str]:
        """Return slugs that haven't sent data within threshold_s seconds"""
        now = time.time()
        silent = []
        for slug in self._subscribed_slugs:
            last = self._slug_last_data.get(slug, 0)
            if now - last > threshold_s:
                silent.append(slug)
        return silent

    async def resubscribe_silent(self, threshold_s: float = 60.0):
        """Re-subscribe slugs that have been silent for threshold_s seconds"""
        silent = self.get_silent_slugs(threshold_s)
        if not silent:
            return 0
        print(f"[PM WS] Resubscribing {len(silent)} silent markets: {sorted(silent)}", flush=True)
        if self.connected and self.ws:
            try:
                subscribe_msg = {
                    "subscribe": {
                        "request_id": "arb-resub",
                        "subscription_type": 1,
                        "market_slugs": silent
                    }
                }
                await self.ws.send(json.dumps(subscribe_msg))
            except Exception as e:
                print(f"[PM WS] Resubscribe failed: {e}")
        return len(silent)

    def _handle_market_data(self, data: Dict):
        """Parse PM WS orderbook update and update local PM book cache"""
        global stats

        if "marketData" not in data:
            return

        md = data["marketData"]
        pm_slug = md.get("marketSlug", "")

        if not pm_slug:
            return

        # Track subscription health
        self._slug_last_data[pm_slug] = time.time()

        # Parse best bid/ask from orderbook
        bids = md.get("bids", [])
        offers = md.get("offers", [])

        if not bids or not offers:
            return

        # Sort bids descending by price (highest = best bid)
        # Sort offers ascending by price (lowest = best ask)
        sorted_bids = sorted(bids, key=lambda x: float(x["px"]["value"]), reverse=True)
        sorted_offers = sorted(offers, key=lambda x: float(x["px"]["value"]))

        # Store full depth for sizing algorithm (raw long-team frame)
        pm_books[pm_slug] = {
            'bids': [{'price_cents': round(float(b["px"]["value"]) * 100),
                      'size': int(float(b["qty"]))} for b in sorted_bids],
            'asks': [{'price_cents': round(float(o["px"]["value"]) * 100),
                      'size': int(float(o["qty"]))} for o in sorted_offers],
            'timestamp_ms': int(time.time() * 1000),
        }

        best_bid = float(sorted_bids[0]["px"]["value"]) * 100  # Convert to cents
        best_bid_size = int(float(sorted_bids[0]["qty"]))
        best_ask = float(sorted_offers[0]["px"]["value"]) * 100  # Convert to cents
        best_ask_size = int(float(sorted_offers[0]["qty"]))

        # Skip stale/crossed PM books (bid >= ask means corrupted data)
        if best_bid >= best_ask:
            return

        # Find all cache_keys mapped to this PM slug
        cache_keys = pm_slug_to_cache_keys.get(pm_slug, [])

        for cache_key in cache_keys:
            mapping = VERIFIED_MAPS.get(cache_key)
            if not mapping:
                continue

            pm_outcomes = mapping.get('pm_outcomes', {})
            pm_long_team = mapping.get('pm_long_team', '')

            # ── Runtime pm_long_team sanity check (once per game per session) ──
            if cache_key not in _pm_price_checked and pm_long_team:
                _pm_price_checked.add(cache_key)
                pm_mid = (best_bid + best_ask) / 2  # PM WS price in long-team frame
                # Find Kalshi price for pm_long_team
                kalshi_tickers = mapping.get('kalshi_tickers', {})
                k_ticker = kalshi_tickers.get(pm_long_team)
                if k_ticker and k_ticker in local_books:
                    k_book = local_books[k_ticker]
                    k_bid = k_book.get('best_bid')
                    k_ask = k_book.get('best_ask')
                    if k_bid is not None and k_ask is not None:
                        k_mid = (k_bid + k_ask) / 2
                        diff = abs(k_mid - pm_mid)
                        # Also check if the OTHER team's price matches better
                        inv_pm_mid = 100 - pm_mid  # inverted = other team's price
                        inv_diff = abs(k_mid - inv_pm_mid)
                        if diff > 15 and inv_diff < diff:
                            price_mismatch_games.add(cache_key)
                            print(
                                f"[WARN] Price mismatch on {cache_key}: "
                                f"PM long team {pm_long_team} WS mid={pm_mid:.0f}c "
                                f"vs Kalshi {pm_long_team} mid={k_mid:.0f}c "
                                f"(diff={diff:.0f}c, inverted diff={inv_diff:.0f}c) "
                                f"— skipping trades on this game",
                                flush=True,
                            )

            for idx_str, outcome_data in pm_outcomes.items():
                team = outcome_data.get('team')
                outcome_idx = outcome_data.get('outcome_index')
                if not team:
                    continue

                team_normalized = normalize_team_abbrev(team)

                # PM WS prices are for pm_long_team - apply inversion for other team
                is_long_team = (team_normalized == pm_long_team)

                if is_long_team:
                    update_pm_price(cache_key, team, best_bid, best_ask,
                                  best_bid_size, best_ask_size, pm_slug, outcome_idx, pm_long_team)
                else:
                    update_pm_price(cache_key, team, 100 - best_ask, 100 - best_bid,
                                  best_ask_size, best_bid_size, pm_slug, outcome_idx, pm_long_team)

        stats['pm_ws_messages'] += 1

    async def _check_spreads_for_slug(self, pm_slug: str):
        """Check spreads for all tickers mapped to this PM slug"""
        cache_keys = pm_slug_to_cache_keys.get(pm_slug, [])

        for cache_key in cache_keys:
            tickers = cache_key_to_tickers.get(cache_key, [])
            for ticker in tickers:
                if not quick_spread_possible(ticker):
                    continue
                arb = check_spread_for_ticker(ticker)
                if arb and self.on_spread_detected:
                    asyncio.create_task(self.on_spread_detected(arb))

    async def listen(self):
        """Listen for PM WebSocket messages"""
        global stats, shutdown_requested

        while not shutdown_requested:
            if not self.connected or not self.ws:
                # Try to reconnect
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, WS_RECONNECT_DELAY_MAX)

                if await self.connect():
                    # Resubscribe to all slugs
                    slugs = list(pm_slug_to_cache_keys.keys())
                    if slugs:
                        await self.subscribe(slugs)
                continue

            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=60)
                data = json.loads(msg)

                # Handle heartbeat
                if "heartbeat" in data:
                    continue

                # Handle market data update
                if "marketData" in data:
                    pm_slug = data["marketData"].get("marketSlug", "")
                    self._handle_market_data(data)
                    _record_pm_snapshot(pm_slug, data["marketData"])
                    # Check spreads for all tickers mapped to this PM slug
                    await self._check_spreads_for_slug(pm_slug)

            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed as e:
                print(f"[PM WS] Connection closed: {e}")
                self.connected = False
                stats['pm_ws_connected'] = False
            except Exception as e:
                print(f"[PM WS] Error: {e}")

    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
        self.connected = False
        stats['pm_ws_connected'] = False


# ============================================================================
# PM WS HEALTH MONITOR & REST FALLBACK
# ============================================================================

async def pm_resub_monitor(pm_ws: PMWebSocket):
    """Every 60s, resubscribe any markets that haven't sent data"""
    global shutdown_requested
    await asyncio.sleep(15)  # Initial grace period after startup
    while not shutdown_requested:
        try:
            count = await pm_ws.resubscribe_silent(threshold_s=60.0)
            if count == 0:
                # All markets responding — check less frequently
                await asyncio.sleep(60)
            else:
                # Gave resub, check again sooner to see if it helped
                await asyncio.sleep(20)
        except Exception as e:
            print(f"[PM RESUB] Error: {e}", flush=True)
            await asyncio.sleep(30)


async def pm_rest_fallback_poller(
    pm_ws: PMWebSocket,
    pm_api: 'PolymarketUSAPI',
    session: aiohttp.ClientSession,
):
    """
    Poll REST BBO for PM markets that have been silent on WS for >30s.
    Updates pm_prices so spread detection works even without WS data.
    Polls every 5s per silent market, staggered to avoid bursts.
    """
    global shutdown_requested, stats

    SILENCE_THRESHOLD_S = 30.0
    POLL_INTERVAL_S = 5.0

    await asyncio.sleep(20)  # Let WS settle before starting fallback
    print("[PM REST FALLBACK] Poller started (silence threshold=30s, poll=5s)", flush=True)

    while not shutdown_requested:
        try:
            silent_slugs = pm_ws.get_silent_slugs(SILENCE_THRESHOLD_S)
            if not silent_slugs:
                await asyncio.sleep(POLL_INTERVAL_S)
                continue

            stats_key = 'pm_rest_fallback_polls'
            if stats_key not in stats:
                stats[stats_key] = 0

            for slug in silent_slugs:
                if shutdown_requested:
                    break
                try:
                    ob = await pm_api.get_orderbook(session, slug, debug=False)
                    if not ob or ob.get('best_bid') is None or ob.get('best_ask') is None:
                        continue

                    # Convert to cents (REST returns decimal like 0.55)
                    best_bid = ob['best_bid'] * 100 if ob['best_bid'] < 1 else ob['best_bid']
                    best_ask = ob['best_ask'] * 100 if ob['best_ask'] < 1 else ob['best_ask']
                    bid_size = ob.get('bid_size', 0)
                    ask_size = ob.get('ask_size', 0)

                    if best_bid >= best_ask:
                        continue  # Crossed book

                    # Store full depth
                    pm_books[slug] = {
                        'bids': [{'price_cents': round(b['price'] * 100), 'size': b['size']}
                                 for b in ob.get('bids', [])],
                        'asks': [{'price_cents': round(a['price'] * 100), 'size': a['size']}
                                 for a in ob.get('asks', [])],
                        'timestamp_ms': int(time.time() * 1000),
                    }

                    # Update pm_prices for all cache_keys mapped to this slug
                    cache_keys = pm_slug_to_cache_keys.get(slug, [])
                    for cache_key in cache_keys:
                        mapping = VERIFIED_MAPS.get(cache_key)
                        if not mapping:
                            continue
                        pm_outcomes = mapping.get('pm_outcomes', {})
                        pm_long_team = mapping.get('pm_long_team', '')

                        for idx_str, outcome_data in pm_outcomes.items():
                            team = outcome_data.get('team')
                            outcome_idx = outcome_data.get('outcome_index')
                            if not team:
                                continue

                            team_normalized = normalize_team_abbrev(team)
                            is_long_team = (team_normalized == pm_long_team)

                            if is_long_team:
                                update_pm_price(cache_key, team, best_bid, best_ask,
                                              bid_size, ask_size, slug, outcome_idx, pm_long_team)
                            else:
                                update_pm_price(cache_key, team, 100 - best_ask, 100 - best_bid,
                                              ask_size, bid_size, slug, outcome_idx, pm_long_team)

                    stats[stats_key] += 1

                    # Check spreads after REST update
                    for cache_key in cache_keys:
                        tickers = cache_key_to_tickers.get(cache_key, [])
                        for ticker in tickers:
                            if not quick_spread_possible(ticker):
                                continue
                            arb = check_spread_for_ticker(ticker)
                            if arb and pm_ws.on_spread_detected:
                                asyncio.create_task(pm_ws.on_spread_detected(arb))

                except Exception as e:
                    print(f"[PM REST FALLBACK] Error polling {slug}: {e}", flush=True)

                # Stagger requests — 200ms between slugs
                await asyncio.sleep(0.2)

            # Log periodically
            if stats.get(stats_key, 0) % 50 == 1:
                print(f"[PM REST FALLBACK] Polling {len(silent_slugs)} silent markets "
                      f"(total polls: {stats.get(stats_key, 0)})", flush=True)

            await asyncio.sleep(POLL_INTERVAL_S)

        except Exception as e:
            print(f"[PM REST FALLBACK] Loop error: {e}", flush=True)
            await asyncio.sleep(10)


# ============================================================================
# EXECUTION HANDLER
# ============================================================================

async def handle_spread_detected(arb: ArbOpportunity, session: aiohttp.ClientSession,
                                  kalshi_api: KalshiAPI, pm_api: PolymarketUSAPI):
    """
    Handle detected arbitrage opportunity.

    This function handles:
    - Pre-execution checks (cooldown, kill switch, mapping verification)
    - Profit estimation (using WS prices directly - no REST confirmation)

    NO REST confirmation - trusts WS prices + PM buffer for speed.
    PM-first execution means bad price = PM order expires = no harm.

    Actual order execution is delegated to executor_core.execute_arb()
    """
    global last_trade_time, stats, shutdown_requested

    # -------------------------------------------------------------------------
    # Pre-execution checks (stay in WS executor)
    # -------------------------------------------------------------------------

    # Check cooldown
    time_since_last = time.time() - last_trade_time
    if time_since_last < Config.cooldown_seconds:
        return

    # Check if already traded (uses shared state from executor_core)
    if arb.game in traded_games or arb.pm_slug in traded_games:
        return

    # Check blacklist (uses shared state from executor_core)
    if arb.game in blacklisted_games or arb.cache_key in blacklisted_games:
        return

    # Check price mismatch (pm_long_team sanity check failed at runtime)
    if arb.cache_key in price_mismatch_games:
        return

    # Check kill switch
    if check_kill_switch():
        print(f"[EXEC] Kill switch active - skipping")
        return

    # Team-level cooldown key (ILST no-fill shouldn't block UNI on same game)
    cd_key = f"{arb.cache_key}:{arb.team}"

    # Per-team cooldown after SUCCESS — prevent stacking losses
    if cd_key in game_success_cooldown:
        elapsed = time.time() - game_success_cooldown[cd_key]
        if elapsed < 30:  # 30 second cooldown after success
            return

    # Per-team no-fill blacklist — stop after too many consecutive no-fills
    if nofill_count.get(cd_key, 0) >= NOFILL_BLACKLIST_THRESHOLD:
        return

    # Per-team no-fill cooldown — exponential backoff on repeated PM no-fills
    if cd_key in nofill_cooldown:
        elapsed = time.time() - nofill_cooldown[cd_key]
        count = nofill_count.get(cd_key, 1)
        cooldown = min(NOFILL_COOLDOWN_BASE * count, NOFILL_COOLDOWN_MAX)
        if elapsed < cooldown:
            remaining = cooldown - elapsed
            if arb.spread_cents >= 7:
                print(f"[COOLDOWN] {arb.team} {arb.spread_cents:.1f}c spread blocked by nofill cooldown ({remaining:.0f}s left, {count} consecutive no-fills)")
            return

    # Per-game execution guard — prevent concurrent execution on same game
    if arb.cache_key in executing_games:
        return
    executing_games.add(arb.cache_key)

    try:
        # Get mapping for trade verification
        mapping = VERIFIED_MAPS.get(arb.cache_key)
        if not mapping:
            print(f"[EXEC] No mapping for {arb.cache_key} - skipping")
            return

        # Verify this trade would create a proper hedge
        if not run_trade_verification(mapping, arb.team, arb.direction):
            print(f"[FATAL] Trade verification failed for {arb.game} {arb.team}")
            print(f"[FATAL] This trade would NOT create a hedge. Aborting.")
            log_skipped_arb(arb, 'hedge_verification_failed', 'Trade would not create proper hedge')
            return

        print(f"\n[SPREAD] {arb.game} {arb.team}: {arb.net_spread}c ({arb.direction})")
        print(f"  Kalshi: bid={arb.k_bid}c x{arb.k_bid_size} / ask={arb.k_ask}c x{arb.k_ask_size}")
        print(f"  PM (WS): bid={arb.pm_bid}c x{arb.pm_bid_size} / ask={arb.pm_ask}c x{arb.pm_ask_size}")

        # ---------------------------------------------------------------------
        # NO REST CONFIRMATION - Trust WS prices + PM buffer
        # PM-first execution means bad price = PM order expires = no harm
        # Saves 50-100ms latency where competitors steal spreads
        # ---------------------------------------------------------------------
        stats['spreads_detected'] += 1

        # Estimate profit
        net_profit, breakdown = estimate_net_profit_cents(arb)
        if net_profit < Config.min_profit_cents:
            print(f"[EXEC] Net profit {net_profit:.1f}c < min {Config.min_profit_cents}c - skipping")
            log_skipped_arb(arb, 'low_profit', f'Net {net_profit:.1f}c < min {Config.min_profit_cents}c')
            return

        print(f"[EXEC] Est. net profit: {net_profit:.1f}c/contract")

        # -----------------------------------------------------------------
        # Depth-aware sizing
        # -----------------------------------------------------------------
        is_long_team = (arb.team == arb.pm_long_team)
        kalshi_book = local_books.get(arb.kalshi_ticker, {})
        pm_depth = pm_books.get(arb.pm_slug, {})

        if pm_depth and pm_depth.get('bids') and pm_depth.get('asks'):
            # Juicy spreads get higher contract cap
            effective_max = Config.max_contracts_juicy if arb.net_spread >= Config.juicy_spread_threshold else Config.max_contracts
            sizing = calculate_optimal_size(
                kalshi_book=kalshi_book, pm_depth=pm_depth,
                direction=arb.direction, is_long_team=is_long_team,
                pm_balance_cents=int(live_balances.get('pm_balance', 0) * 100),
                k_balance_cents=int(live_balances.get('kalshi_balance', 0) * 100),
                max_contracts=effective_max,
            )
            optimal_size = sizing['size']
        else:
            optimal_size = 1  # Fallback: no depth data
            sizing = {'expected_profit_cents': net_profit, 'avg_spread_cents': arb.net_spread,
                      'avg_pm_price': 0, 'avg_k_price': 0, 'k_depth': 0, 'pm_depth': 0, 'limit_reason': 'no_depth_data'}

        if optimal_size == 0:
            log_skipped_arb(arb, 'depth_zero', 'No profitable contracts after depth walk')
            return

        arb.size = optimal_size  # Update for log_trade's contracts_intended field

        print(f"[EXEC] Sized: {optimal_size} contracts (limit: {sizing.get('limit_reason', '?')}), "
              f"est ${sizing['expected_profit_cents']/100:.2f} profit")

        # Print depth walk summary
        dwl = sizing.get('depth_walk_log', [])
        if dwl:
            profitable = [l for l in dwl if not l.get('stopped')]
            stopped = [l for l in dwl if l.get('stopped')]
            parts = []
            for l in dwl:
                avail = l.get('contracts_at_level', l.get('k_remaining', '?'))
                tag = " STOP" if l.get('stopped') else ""
                parts.append(f"L{l['level']}: K{l['k_price']}+PM{l['pm_cost']}={l['k_price']+l['pm_cost']}c "
                             f"({l['spread']}c spread, {l['marginal_profit']}c net{tag})")
            print(f"[DEPTH] {arb.team}: {len(profitable)} profitable levels | {' | '.join(parts)}", flush=True)

        # Walk-based depth gate — authoritative check using actual depth at arb price
        if dwl:
            walk_k_depth = dwl[0].get('k_remaining', 0)
            if walk_k_depth < MIN_K_DEPTH_L1:
                print(f"[DEPTH_GATE] SKIP {arb.team}: walk K L1 depth {walk_k_depth} < {MIN_K_DEPTH_L1} at arb price", flush=True)
                log_skipped_arb(arb, 'walk_depth_gate', f'K depth {walk_k_depth} < {MIN_K_DEPTH_L1} at arb price')
                stats['depth_gate_skips'] = stats.get('depth_gate_skips', 0) + 1
                return

        # Sizing decision log
        _dcap = sizing.get('depth_cap_used', 0)
        _spread_l1 = sizing.get('spread_at_sizing', 0)
        _commit_cap = sizing.get('commitment_cap', '?')
        print(f"[SIZING] {arb.team}: {optimal_size} contracts | spread={_spread_l1:.1f}c cap={_dcap:.0%} | "
              f"walk={sizing.get('max_profitable_contracts', '?')} depth={sizing.get('size', '?')} "
              f"commit={_commit_cap} max={Config.max_contracts} | limit={sizing.get('limit_reason', '?')}", flush=True)

        # Build sizing_details dict for trade log
        _sizing_details = {
            'avg_spread_cents': sizing.get('avg_spread_cents', 0),
            'expected_profit_cents': sizing.get('expected_profit_cents', 0),
            'k_depth': sizing.get('k_depth', 0),
            'pm_depth': sizing.get('pm_depth', 0),
            'limit_reason': sizing.get('limit_reason', ''),
            'depth_walk_log': dwl,
            'depth_cap_used': sizing.get('depth_cap_used', 0),
            'spread_at_sizing': sizing.get('spread_at_sizing', 0),
            'commitment_cap': sizing.get('commitment_cap', 0),
        }

        # -----------------------------------------------------------------
        # Compute opposite-side hedge info (for Tier 3 cross-platform arb)
        # -----------------------------------------------------------------
        opposite_info = None
        mapping = VERIFIED_MAPS.get(arb.cache_key)
        if not mapping:
            print(f"[OPP-HEDGE] No VERIFIED_MAP for {arb.cache_key} — opposite hedge unavailable")
        else:
            all_tickers = mapping.get('kalshi_tickers', {})
            other_teams = [t for t in all_tickers if t != arb.team]
            if not other_teams:
                print(f"[OPP-HEDGE] No other team in mapping for {arb.cache_key} — opposite hedge unavailable")
            else:
                ot = other_teams[0]
                ot_ticker = all_tickers[ot]
                ot_book = local_books.get(ot_ticker)
                if not ot_book or not ot_book.get('best_ask'):
                    print(f"[OPP-HEDGE] No orderbook/ask for {ot} ({ot_ticker}) — opposite hedge unavailable")
                else:
                    opposite_info = {
                        'team': ot,
                        'ticker': ot_ticker,
                        'ask': ot_book['best_ask'],
                        'ask_size': ot_book.get('best_ask_size', 0),
                    }

        # -----------------------------------------------------------------
        # Execute via executor_core (clean execution engine)
        # -----------------------------------------------------------------
        async with EXECUTION_LOCK:
            # ── Pre-execution: fetch FRESH PM BBO via REST ──
            fresh_pm, bbo_ms = await confirm_pm_price_fresh(session, pm_api, arb)

            if fresh_pm is None:
                print(f"[EXEC] PM REST BBO fetch failed ({bbo_ms:.0f}ms) — aborting")
                executing_games.discard(arb.cache_key)
                return

            # Log cache vs fresh divergence for diagnostics
            _cache_bid_diff = fresh_pm['bid'] - arb.pm_bid
            _cache_ask_diff = fresh_pm['ask'] - arb.pm_ask
            if abs(_cache_bid_diff) > 1 or abs(_cache_ask_diff) > 1:
                print(f"[EXEC] PM cache divergence: bid {arb.pm_bid:.0f}→{fresh_pm['bid']:.0f} ({_cache_bid_diff:+.0f}c), "
                      f"ask {arb.pm_ask:.0f}→{fresh_pm['ask']:.0f} ({_cache_ask_diff:+.0f}c)")

            # Update arb with fresh PM prices (executor_core reads these)
            arb.pm_bid = fresh_pm['bid']
            arb.pm_ask = fresh_pm['ask']
            arb.pm_bid_size = fresh_pm.get('bid_size', 0)
            arb.pm_ask_size = fresh_pm.get('ask_size', 0)

            # Recalculate spread with fresh prices — abort if gone
            fresh_spread, _ = recalculate_spread_with_fresh_pm(arb, fresh_pm)
            if fresh_spread < Config.spread_min_cents:
                print(f"[EXEC] Spread gone after fresh BBO: {fresh_spread:.1f}c < {Config.spread_min_cents}c min — aborting ({bbo_ms:.0f}ms)")
                executing_games.discard(arb.cache_key)
                return

            # Update arb spread fields for executor_core
            arb.gross_spread = fresh_spread
            arb.net_spread = fresh_spread  # Will be recalculated by executor_core with fees

            print(f"[EXEC] Fresh BBO confirmed ({bbo_ms:.0f}ms): "
                  f"pm_bid={fresh_pm['bid']:.0f}c pm_ask={fresh_pm['ask']:.0f}c spread={fresh_spread:.1f}c")

            # ── Pre-execution freshness check: Kalshi book ──
            _fresh_k = local_books.get(arb.kalshi_ticker)
            if _fresh_k:
                _k_age = int(time.time() * 1000) - _fresh_k.get('last_update_ms', 0)
                if _k_age > K_PRICE_MAX_AGE_MS:
                    executing_games.discard(arb.cache_key)
                    return
                if arb.direction == 'BUY_PM_SELL_K':
                    _fresh_k_bid = _fresh_k.get('best_bid') or 0
                    _k_drift = arb.k_bid - _fresh_k_bid
                    if _k_drift > 2:
                        print(f"[EXEC] K bid drifted -{_k_drift:.0f}c since detection — aborting")
                        executing_games.discard(arb.cache_key)
                        return
                else:
                    _fresh_k_ask = _fresh_k.get('best_ask') or 0
                    _k_drift = _fresh_k_ask - arb.k_ask
                    if _k_drift > 2:
                        print(f"[EXEC] K ask drifted +{_k_drift:.0f}c since detection — aborting")
                        executing_games.discard(arb.cache_key)
                        return

            print(f"[EXEC] Executing {optimal_size} contract(s) via executor_core...")

            # Compute PM data age for no-fill diagnostics
            _pm_key = f"{arb.cache_key}_{arb.team}"
            _pm_data_age_ms = 0
            if _pm_key in pm_prices and 'timestamp_ms' in pm_prices[_pm_key]:
                _pm_data_age_ms = int(time.time() * 1000) - pm_prices[_pm_key]['timestamp_ms']

            result = await execute_arb(
                arb=arb,
                session=session,
                kalshi_api=kalshi_api,
                pm_api=pm_api,
                pm_slug=arb.pm_slug,
                pm_outcome_idx=arb.pm_outcome_index,
                size=optimal_size,
                k_book_ref=local_books.get(arb.kalshi_ticker),
                omi_cache=omi_cache,
                opposite_info=opposite_info,
                pm_data_age_ms=_pm_data_age_ms,
            )

            # Compute PM position details for settlement tracking
            # Replicates executor_core.py logic: actual traded outcome + long/short
            _is_long = (arb.team == arb.pm_long_team)
            _params = TRADE_PARAMS.get((arb.direction, _is_long), {})
            _actual_pm_oi = (1 - arb.pm_outcome_index) if _params.get('pm_switch_outcome', False) else arb.pm_outcome_index
            _is_buy_short = _params.get('pm_is_buy_short', False)

            # Handle result — only apply cooldown when PM order was actually sent
            pm_was_sent = result.pm_order_ms > 0 or result.success or result.unhedged
            if pm_was_sent:
                last_trade_time = time.time()

            if result.tier in ("TIER3_OPPOSITE_HEDGE", "TIER3_OPPOSITE_OVERWEIGHT"):
                # Opposite-side hedge: cross-platform arb (PM team A + K team B)
                timing = f"pm={result.pm_order_ms}ms → k={result.k_order_ms}ms → TOTAL={result.execution_time_ms}ms"
                print(f"[EXEC] [{result.tier}]: {result.abort_reason} | {timing}")
                k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price}
                pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}
                log_trade(arb, k_result, pm_result, result.tier,
                          execution_time_ms=result.execution_time_ms,
                          pm_order_ms=result.pm_order_ms,
                          sizing_details=_sizing_details,
                          execution_phase=result.execution_phase,
                          is_maker=result.is_maker,
                          gtc_rest_time_ms=result.gtc_rest_time_ms,
                          gtc_spread_checks=result.gtc_spread_checks,
                          gtc_cancel_reason=result.gtc_cancel_reason,
                          tier=result.tier)
                # Patch opposite hedge fields into trade record
                from arb_executor_v7 import TRADE_LOG
                if TRADE_LOG:
                    TRADE_LOG[-1].update({
                        'opposite_hedge_ticker': result.opposite_hedge_ticker,
                        'opposite_hedge_team': result.opposite_hedge_team,
                        'opposite_hedge_price': result.opposite_hedge_price,
                        'combined_cost_cents': result.combined_cost_cents,
                        'guaranteed_profit_cents': result.guaranteed_profit_cents,
                    })
                    with open('trades.json', 'w', encoding='utf-8') as f:
                        json.dump(TRADE_LOG, f, indent=2)

                game_success_cooldown[cd_key] = time.time()
                nofill_count.pop(cd_key, None)
                nofill_cooldown.pop(cd_key, None)
                save_traded_game(arb.game, pm_slug=arb.pm_slug, team=arb.team)
                stats['spreads_executed'] += 1

            elif result.success:
                # Show timing breakdown: PM first (unreliable) → K second (reliable)
                phase = " [GTC]" if result.execution_phase == "gtc" else ""
                maker = " (MAKER)" if result.is_maker else ""
                timing = f"pm={result.pm_order_ms}ms → k={result.k_order_ms}ms → TOTAL={result.execution_time_ms}ms"
                if result.gtc_rest_time_ms > 0:
                    timing += f" (GTC: {result.gtc_rest_time_ms}ms, {result.gtc_spread_checks} checks)"
                print(f"[EXEC]{phase} SUCCESS{maker}: PM={result.pm_filled}@{result.pm_price:.2f}, K={result.kalshi_filled}@{result.kalshi_price}c | {timing}")
                # Build result dicts for log_trade compatibility
                k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price}
                pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}
                log_trade(arb, k_result, pm_result, 'SUCCESS',
                          execution_time_ms=result.execution_time_ms,
                          pm_order_ms=result.pm_order_ms,
                          sizing_details=_sizing_details,
                          execution_phase=result.execution_phase,
                          is_maker=result.is_maker,
                          gtc_rest_time_ms=result.gtc_rest_time_ms,
                          gtc_spread_checks=result.gtc_spread_checks,
                          gtc_cancel_reason=result.gtc_cancel_reason,
                          tier=result.tier)

                # Cooldown: prevent re-trading same team too quickly
                game_success_cooldown[cd_key] = time.time()
                nofill_count.pop(cd_key, None)
                nofill_cooldown.pop(cd_key, None)

                # Persist traded game to prevent duplicates across restarts
                save_traded_game(arb.game, pm_slug=arb.pm_slug, team=arb.team)

                stats['spreads_executed'] += 1

                # Check max trades limit
                if MAX_TRADES_LIMIT > 0 and stats['spreads_executed'] >= MAX_TRADES_LIMIT:
                    print("\n" + "=" * 70)
                    print(f"MAX TRADES REACHED ({MAX_TRADES_LIMIT}) — STOPPING")
                    print("=" * 70)
                    shutdown_requested = True

            elif result.unhedged:
                # PM filled but Kalshi didn't - this is now rare (Kalshi is reliable)
                timing = f"pm={result.pm_order_ms}ms → k={result.k_order_ms}ms"
                print(f"[EXEC] UNHEDGED! PM={result.pm_filled} filled, K={result.kalshi_filled} failed | {timing}")
                print(f"[EXEC] Reason: {result.abort_reason}")
                k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price,
                            'k_response_details': result.k_response_details}
                pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}
                log_trade(arb, k_result, pm_result, 'UNHEDGED',
                          execution_time_ms=result.execution_time_ms,
                          pm_order_ms=result.pm_order_ms,
                          sizing_details=_sizing_details,
                          execution_phase=result.execution_phase,
                          is_maker=result.is_maker,
                          gtc_rest_time_ms=result.gtc_rest_time_ms,
                          gtc_spread_checks=result.gtc_spread_checks,
                          gtc_cancel_reason=result.gtc_cancel_reason,
                          tier=result.tier)
                # Save unhedged position for recovery
                try:
                    from arb_executor_v7 import HedgeState
                    hedge_state = HedgeState(
                        kalshi_ticker=arb.kalshi_ticker,
                        pm_slug=arb.pm_slug,
                        target_qty=optimal_size,
                        kalshi_filled=result.kalshi_filled,
                        pm_filled=result.pm_filled,
                        kalshi_price=result.kalshi_price,
                        pm_price=int(result.pm_price * 100),
                    )
                    save_unhedged_position(hedge_state, result.abort_reason)
                except Exception as e:
                    print(f"[ERROR] Failed to save unhedged position: {e}")
                nofill_count.pop(cd_key, None)
                nofill_cooldown.pop(cd_key, None)

            elif result.tier == "TIER3A":
                # OMI directional hold — not a full unwind
                timing = f"pm={result.pm_order_ms}ms → k={result.k_order_ms}ms → TOTAL={result.execution_time_ms}ms"
                print(f"[EXEC] [{result.tier}]: {result.abort_reason} | {timing}")
                k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price,
                            'k_response_details': result.k_response_details}
                pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}
                log_trade(arb, k_result, pm_result, result.tier,
                          execution_time_ms=result.execution_time_ms,
                          pm_order_ms=result.pm_order_ms,
                          sizing_details=_sizing_details,
                          execution_phase=result.execution_phase,
                          is_maker=result.is_maker,
                          gtc_rest_time_ms=result.gtc_rest_time_ms,
                          gtc_spread_checks=result.gtc_spread_checks,
                          gtc_cancel_reason=result.gtc_cancel_reason,
                          tier=result.tier)
                nofill_count.pop(cd_key, None)
                nofill_cooldown.pop(cd_key, None)

            elif result.exited:
                # PM filled, K failed, PM successfully unwound — position is flat
                timing = f"pm={result.pm_order_ms}ms → k={result.k_order_ms}ms → TOTAL={result.execution_time_ms}ms"
                tier_info = f" [{result.tier}]" if result.tier else ""
                print(f"[EXEC] EXITED{tier_info}: {result.abort_reason} | {timing}")
                k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price,
                            'k_response_details': result.k_response_details}
                pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}
                log_trade(arb, k_result, pm_result, 'EXITED',
                          execution_time_ms=result.execution_time_ms,
                          pm_order_ms=result.pm_order_ms,
                          unwind_loss_cents=result.unwind_loss_cents,
                          unwind_pnl_cents=result.unwind_pnl_cents,
                          sizing_details=_sizing_details,
                          execution_phase=result.execution_phase,
                          is_maker=result.is_maker,
                          gtc_rest_time_ms=result.gtc_rest_time_ms,
                          gtc_spread_checks=result.gtc_spread_checks,
                          gtc_cancel_reason=result.gtc_cancel_reason,
                          tier=result.tier,
                          unwind_fill_price=result.unwind_fill_price,
                          unwind_qty=result.unwind_qty)
                nofill_count.pop(cd_key, None)
                nofill_cooldown.pop(cd_key, None)

            elif result.pm_filled == 0 and result.pm_order_ms > 0:
                # Real PM no-fill: order was sent to PM API but IOC expired
                gtc_info = ""
                if result.execution_phase == "gtc":
                    gtc_info = f" | GTC: {result.gtc_cancel_reason} ({result.gtc_rest_time_ms}ms)"
                _diag = result.nofill_diagnosis
                _diag_reason = _diag.get('reason', '?') if _diag else '?'
                print(f"[EXEC] PM NO FILL: {_diag_reason} — {result.abort_reason} | pm={result.pm_order_ms}ms{gtc_info}")
                k_result = {'fill_count': 0, 'fill_price': result.kalshi_price}
                pm_result = {'fill_count': 0, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}
                log_trade(arb, k_result, pm_result, 'PM_NO_FILL',
                          execution_time_ms=result.execution_time_ms,
                          pm_order_ms=result.pm_order_ms,
                          sizing_details=_sizing_details,
                          execution_phase=result.execution_phase,
                          is_maker=result.is_maker,
                          gtc_rest_time_ms=result.gtc_rest_time_ms,
                          gtc_spread_checks=result.gtc_spread_checks,
                          gtc_cancel_reason=result.gtc_cancel_reason,
                          tier=result.tier,
                          nofill_diagnosis=_diag)
                # No-fill cooldown: exponential backoff on repeated failures
                nofill_cooldown[cd_key] = time.time()
                nofill_count[cd_key] = nofill_count.get(cd_key, 0) + 1
                count = nofill_count[cd_key]
                if count >= NOFILL_BLACKLIST_THRESHOLD:
                    print(f"[NOFILL] {arb.team}: {count} consecutive no-fills — BLACKLISTED")
                elif count > 1:
                    print(f"[NOFILL] {arb.team}: {count} consecutive no-fills — cooldown {min(NOFILL_COOLDOWN_BASE * count, NOFILL_COOLDOWN_MAX)}s")

            else:
                # Early abort — never reached PM API (safety, phantom, pm_long_team, etc.)
                print(f"[EXEC] SKIPPED: {result.abort_reason}")

            # One-trade test mode: stop after first trade attempt
            if ONE_TRADE_TEST_MODE:
                print("\n" + "=" * 70)
                print("ONE-TRADE TEST COMPLETE - STOPPING")
                print("=" * 70)
                shutdown_requested = True

    finally:
        executing_games.discard(arb.cache_key)


# ============================================================================
# STATUS LOGGING
# ============================================================================

def log_status():
    """Log periodic status"""
    global stats

    now = time.time()
    if now - stats['last_status_log'] < STATUS_LOG_INTERVAL:
        return

    stats['last_status_log'] = now

    k_ws_status = "OK" if stats['k_ws_connected'] else "DOWN"
    pm_ws_status = "OK" if stats['pm_ws_connected'] else "DOWN"

    fresh_pm = sum(1 for p in pm_prices.values()
                   if now * 1000 - p['timestamp_ms'] < PM_PRICE_MAX_AGE_MS)

    books_with_data = sum(1 for b in local_books.values()
                          if b.get('best_bid') is not None and b.get('best_ask') is not None)

    print(f"\n[STATUS] K_WS: {k_ws_status} | PM_WS: {pm_ws_status} | Books: {books_with_data} K, {fresh_pm} PM")
    print(f"[STATUS] K_msgs: {stats['k_ws_messages']} | PM_msgs: {stats['pm_ws_messages']}")
    print(f"[STATUS] Spreads detected: {stats['spreads_detected']} | Executed: {stats['spreads_executed']}")


# Flag to print snapshot once
_snapshot_printed = False
_snapshot_start_time = None

def print_spread_snapshot():
    """Print one-time snapshot of spreads for all tracked games"""
    global _snapshot_printed, _snapshot_start_time

    if _snapshot_printed:
        return

    # Initialize start time on first call
    if _snapshot_start_time is None:
        _snapshot_start_time = time.time()

    # Wait at least 15 seconds after startup for data to stabilize
    if time.time() - _snapshot_start_time < 15:
        return

    # Need both Kalshi and PM data - wait for at least 10 PM WS messages
    if stats['pm_ws_messages'] < 10:
        return

    # Count books with actual price data
    books_with_prices = sum(1 for b in local_books.values()
                            if b.get('best_bid') is not None and b.get('best_ask') is not None)
    if books_with_prices < 20:
        return  # Wait for Kalshi orderbook data

    now_ms = int(time.time() * 1000)
    fresh_pm_count = sum(1 for p in pm_prices.values()
                         if now_ms - p['timestamp_ms'] < PM_PRICE_MAX_AGE_MS)

    if fresh_pm_count < 15:
        return  # Wait until we have enough fresh data

    _snapshot_printed = True

    from datetime import datetime
    time_str = datetime.now().strftime('%I:%M %p')

    # Collect spread data for each game/team
    spreads = []

    for ticker, book in local_books.items():
        if book['best_bid'] is None or book['best_ask'] is None:
            continue

        # Get cache_key and team
        cache_key = ticker_to_cache_key.get(ticker)
        if not cache_key:
            continue

        ticker_parts = ticker.split('-')
        if len(ticker_parts) < 3:
            continue
        team = ticker_parts[-1]
        game_id = ticker_parts[1] if len(ticker_parts) >= 2 else ticker

        # Get PM price - directly access without staleness check for snapshot
        pm_key = f"{cache_key}_{team}"
        pm_data = pm_prices.get(pm_key)
        if not pm_data:
            continue

        k_bid = book['best_bid']
        k_ask = book['best_ask']
        pm_bid = pm_data['bid']
        pm_ask = pm_data['ask']
        pm_long_team = pm_data.get('pm_long_team', '')

        # Calculate spreads - MUST account for is_long_team!
        is_long_team = (team == pm_long_team)

        # All 4 cases now executable with BUY_SHORT (intent=3)
        if is_long_team:
            spread_buy_pm = k_bid - pm_ask        # Case 1: BUY_LONG on PM
            spread_buy_k = pm_bid - k_ask         # Case 3: BUY_SHORT on PM
        else:
            spread_buy_pm = k_bid - pm_ask        # Case 2: BUY_SHORT on PM (pm_ask already inverted)
            spread_buy_k = pm_bid - k_ask         # Case 4: BUY_LONG on PM

        # All cases are now executable
        exec_buy_pm = True
        exec_buy_k = True

        # Find best spread
        best_spread = None
        best_dir = None
        if spread_buy_pm > 0:
            best_spread = spread_buy_pm
            best_dir = 'BUY_PM'
        if spread_buy_k > 0:
            if best_spread is None or spread_buy_k > best_spread:
                best_spread = spread_buy_k
                best_dir = 'BUY_K'

        spreads.append({
            'game': game_id,
            'team': team,
            'k_bid': k_bid,
            'k_ask': k_ask,
            'pm_bid': pm_bid,
            'pm_ask': pm_ask,
            'spread_buy_pm': spread_buy_pm,
            'spread_buy_k': spread_buy_k,
            'exec_buy_pm': exec_buy_pm,
            'exec_buy_k': exec_buy_k,
            'best_spread': best_spread or 0,
            'best_dir': best_dir,
            'is_long_team': is_long_team,
        })

    # Sort by best spread descending (highest first)
    spreads.sort(key=lambda x: x['best_spread'], reverse=True)

    print(f"\n{'='*70}")
    print(f"SPREAD SNAPSHOT ({time_str}) - {len(spreads)} markets")
    print(f"{'='*70}")

    # Group by game
    seen_games = set()
    for s in spreads:
        game_key = s['game']
        if game_key in seen_games:
            continue
        seen_games.add(game_key)

        # Find both teams for this game
        game_spreads = [x for x in spreads if x['game'] == game_key]

        for gs in game_spreads:
            # Mark with * if there's a spread >= 3c
            marker = '*' if gs['best_spread'] and gs['best_spread'] >= 3 else ' '
            print(f"{marker}{gs['game']}/{gs['team']}: K={gs['k_bid']}/{gs['k_ask']} PM={int(gs['pm_bid'])}/{int(gs['pm_ask'])} "
                  f"-> BUY_PM:{int(gs['spread_buy_pm']):+d}c | BUY_K:{int(gs['spread_buy_k']):+d}c")

    print(f"{'='*70}")
    print(f"* = 3c+ spread | Current min: {Config.spread_min_cents}c")
    print(f"[WATCH] 2-3c: {spread_watch_stats['2-3c']} | 3-4c: {spread_watch_stats['3-4c']} | 4c+: {spread_watch_stats['4c+']} (executed: {stats['spreads_executed']})")
    print(f"{'='*70}\n", flush=True)


# ============================================================================
# BALANCE REFRESH
# ============================================================================

async def refresh_balances(session, kalshi_api, pm_api):
    """Periodically fetch balances and positions from both platforms."""
    global _last_balance_refresh

    now = time.time()
    if now - _last_balance_refresh < BALANCE_REFRESH_INTERVAL:
        return
    _last_balance_refresh = now

    try:
        # Kalshi: fetch cash and portfolio_value separately
        k_cash = 0.0
        k_portfolio = 0.0
        k_path = '/trade-api/v2/portfolio/balance'
        async with session.get(
            f'{kalshi_api.BASE_URL}{k_path}',
            headers=kalshi_api._headers('GET', k_path),
            timeout=aiohttp.ClientTimeout(total=5)
        ) as r:
            if r.status == 200:
                data = await r.json()
                k_cash = round((data.get('balance', 0)) / 100, 2)
                k_positions_value = round((data.get('portfolio_value', 0)) / 100, 2)
                k_portfolio = round(k_cash + k_positions_value, 2)

        # PM: fetch buyingPower (cash)
        pm_cash = 0.0
        pm_positions_value = 0.0
        pm_positions_source = "margin"
        pm_path = '/v1/account/balances'
        async with session.get(
            f'{pm_api.BASE_URL}{pm_path}',
            headers=pm_api._headers('GET', pm_path),
            timeout=aiohttp.ClientTimeout(total=5)
        ) as r:
            if r.status == 200:
                data = await r.json()
                for b in data.get('balances', []):
                    if b.get('currency') == 'USD':
                        pm_cash = round(float(b.get('buyingPower', 0)), 2)
                        # Default: margin-based (currentBalance - buyingPower)
                        pm_positions_value = round(
                            float(b.get('currentBalance', 0)) - float(b.get('buyingPower', 0)), 2)
                        break

        # Fetch actual PM positions for mark-to-market
        try:
            pos_path = '/v1/portfolio/positions'
            async with session.get(
                f'{pm_api.BASE_URL}{pos_path}',
                headers=pm_api._headers('GET', pos_path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    pos_data = await r.json()
                    positions_dict = pos_data.get('positions', {})
                    if isinstance(positions_dict, dict):
                        mkt_value = 0.0
                        for slug, pos in positions_dict.items():
                            if not isinstance(pos, dict):
                                continue
                            net = int(pos.get('netPosition', 0) or 0)
                            if net != 0:
                                cv = pos.get('cashValue')
                                if isinstance(cv, dict):
                                    mkt_value += float(cv.get('value', 0))
                                elif cv is not None:
                                    mkt_value += float(cv)
                        pm_positions_value = round(mkt_value, 2)
                        pm_positions_source = "market"
        except Exception as e:
            print(f"[BALANCE] PM positions fetch failed, using margin: {e}")

        pm_portfolio = round(pm_cash + pm_positions_value, 2)

        live_balances["k_cash"] = k_cash
        live_balances["k_portfolio"] = k_portfolio
        live_balances["pm_cash"] = pm_cash
        live_balances["pm_portfolio"] = pm_portfolio
        live_balances["pm_positions_value"] = pm_positions_value
        live_balances["pm_positions_source"] = pm_positions_source
        # Backwards-compat: sizing uses these
        live_balances["kalshi_balance"] = k_portfolio
        live_balances["pm_balance"] = pm_cash
        live_balances["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Persist snapshot for daily_recap.py
        try:
            bal_path = os.path.join(os.path.dirname(__file__) or ".", "balances.json")
            with open(bal_path, "w") as bf:
                json.dump(live_balances, bf)
        except Exception:
            pass
    except Exception as e:
        print(f"[BALANCE] Refresh failed: {e}", flush=True)

    # Fetch real positions from both APIs
    try:
        positions = []

        # ── Load trades.json for hedge cross-reference ──
        # trades.json is the SOURCE OF TRUTH for hedge status
        hedged_by_slug: Dict[str, dict] = {}   # pm_slug -> trade
        hedged_by_ticker: Dict[str, dict] = {}  # kalshi_ticker -> trade
        trades_file = os.path.join(os.path.dirname(__file__) or ".", "trades.json")
        try:
            if os.path.exists(trades_file):
                with open(trades_file, "r") as f:
                    all_trades = json.load(f)
                for t in all_trades:
                    if (t.get("hedged") and t.get("status") == "SUCCESS"
                            and t.get("contracts_filled", 0) > 0):
                        if t.get("pm_slug"):
                            hedged_by_slug[t["pm_slug"]] = t
                        if t.get("kalshi_ticker"):
                            hedged_by_ticker[t["kalshi_ticker"]] = t
        except Exception as e:
            print(f"[POSITIONS] Error loading trades.json for hedge check: {e}", flush=True)

        # Kalshi positions (skip settled: market_exposure == 0 means resolved)
        # Also refresh executor_core's position cache (background, not on hot path)
        settled_kalshi_games: set = set()  # Track settled game_ids to filter PM side too
        k_positions = await kalshi_api.get_positions(session)
        await refresh_position_cache(session, kalshi_api, prefetched=k_positions)
        for ticker, pos in (k_positions or {}).items():
            qty = pos.position if hasattr(pos, 'position') else pos.get('position', 0)
            if qty == 0:
                continue
            exposure = pos.market_exposure if hasattr(pos, 'market_exposure') else pos.get('market_exposure', 0)
            if exposure == 0:
                parts = ticker.split("-")
                settled_gid = parts[1] if len(parts) >= 2 else ticker
                settled_kalshi_games.add(settled_gid)
                continue  # Settled market — position pending payout
            cache_key = ticker_to_cache_key.get(ticker, "")
            parts = ticker.split("-")
            team = parts[-1] if len(parts) >= 3 else ""
            game_id = parts[1] if len(parts) >= 2 else ticker
            sport = cache_key.split(":")[0].upper() if cache_key else ""
            positions.append({
                "platform": "Kalshi",
                "game_id": game_id,
                "team": team,
                "sport": sport,
                "side": "LONG" if qty > 0 else "SHORT",
                "quantity": abs(qty),
                "avg_price": 0,
                "current_value": 0,
                "hedged_with": None,
                "_ticker": ticker,
            })

        # PM US positions
        pm_positions = await pm_api.get_positions(session)
        if isinstance(pm_positions, dict):
            for slug, pos_data in pm_positions.items():
                qty = 0
                side = ""
                if isinstance(pos_data, dict):
                    qty = pos_data.get("quantity", 0) or pos_data.get("size", 0)
                    side = pos_data.get("side", "")
                elif isinstance(pos_data, list):
                    for p in pos_data:
                        qty += p.get("quantity", 0) or p.get("size", 0)
                        side = p.get("side", side)
                if qty == 0:
                    continue
                cache_keys = pm_slug_to_cache_keys.get(slug, [])
                sport = ""
                game_id = slug
                team = ""
                if cache_keys:
                    ck = cache_keys[0]
                    sport = ck.split(":")[0].upper()
                    game_id = ck.split(":")[1] if ":" in ck else slug

                # ── Remap PM game_id to Kalshi format using trades.json ──
                # PM game_id (e.g. "SILL-INDST") != Kalshi game_id ("26FEB09SIUINST")
                # Use trades.json to find the Kalshi game_id for this PM slug
                trade = hedged_by_slug.get(slug)
                if trade:
                    game_id = trade["game_id"]
                    team = trade.get("team", team)
                    sport = trade.get("sport", sport) or sport

                # Skip PM positions whose Kalshi counterpart already settled
                if game_id in settled_kalshi_games:
                    continue

                positions.append({
                    "platform": "PM",
                    "game_id": game_id,
                    "team": team,
                    "sport": sport,
                    "side": side.upper() if side else "LONG",
                    "quantity": abs(qty) if isinstance(qty, (int, float)) else 0,
                    "avg_price": 0,
                    "current_value": 0,
                    "hedged_with": None,
                    "_pm_slug": slug,
                })

        # ── Helper: check if a Kalshi position looks settled ──
        def _is_settled_kalshi(p: dict) -> bool:
            """Return True if this Kalshi position is likely settled/expired."""
            ticker = p.get("_ticker", "")
            if not ticker:
                return False
            book = local_books.get(ticker)
            if book is None:
                # Not in our active books at all — likely settled
                return True
            bid = book.get("best_bid") or 0
            ask = book.get("best_ask") or 0
            # Settled: no book, or resolved prices
            if bid == 0 and ask == 0:
                return True
            if bid >= 99 or (ask > 0 and ask <= 1):
                return True
            return False

        # ── Match hedged pairs by game_id (now aligned via trades.json) ──
        by_game: Dict[str, list] = {}
        for p in positions:
            gkey = p["game_id"]
            if gkey not in by_game:
                by_game[gkey] = []
            by_game[gkey].append(p)

        matched = []
        for gkey, group in by_game.items():
            platforms = {p["platform"] for p in group}

            # Skip settled games — check all Kalshi positions in group
            settled = any(
                _is_settled_kalshi(p) for p in group if p["platform"] == "Kalshi"
            )
            if settled:
                continue

            if "PM" in platforms and "Kalshi" in platforms:
                # Hedged pair — both APIs show positions
                pm_pos = next(p for p in group if p["platform"] == "PM")
                k_pos = next(p for p in group if p["platform"] == "Kalshi")
                matched.append({
                    "platform": "PM+Kalshi",
                    "game_id": gkey,
                    "team": k_pos["team"] or pm_pos["team"],
                    "sport": k_pos["sport"] or pm_pos["sport"],
                    "side": f"PM {pm_pos['side']} / K {k_pos['side']}",
                    "quantity": min(pm_pos["quantity"], k_pos["quantity"]),
                    "avg_price": pm_pos["avg_price"],
                    "current_value": k_pos["avg_price"],
                    "hedged_with": "HEDGED",
                    "hedge_source": "API_MATCHED",
                })
            else:
                # Only one platform visible — check trades.json before calling it UNHEDGED
                confirmed_hedged = False

                for p in group:
                    if p["platform"] == "Kalshi" and p.get("_ticker"):
                        if p["_ticker"] in hedged_by_ticker:
                            confirmed_hedged = True

                    if p["platform"] == "PM" and p.get("_pm_slug"):
                        if p["_pm_slug"] in hedged_by_slug:
                            confirmed_hedged = True

                if confirmed_hedged:
                    # trades.json says HEDGED — trust it over API mismatch
                    rep = group[0]
                    matched.append({
                        "platform": rep["platform"],
                        "game_id": gkey,
                        "team": rep["team"],
                        "sport": rep["sport"],
                        "side": rep["side"],
                        "quantity": rep["quantity"],
                        "avg_price": rep["avg_price"],
                        "current_value": rep["current_value"],
                        "hedged_with": "HEDGED",
                        "hedge_source": "CONFIRMED",
                    })
                else:
                    # Truly unhedged — no trades.json confirmation
                    for p in group:
                        p.pop("_ticker", None)
                        p.pop("_pm_slug", None)
                        p["hedge_source"] = "UNHEDGED"
                    matched.extend(group)

        # Strip remaining internal fields
        for p in matched:
            p.pop("_ticker", None)
            p.pop("_pm_slug", None)

        # Update global live_positions in-place
        live_positions.clear()
        live_positions.extend(matched)

    except Exception as e:
        print(f"[POSITIONS] Refresh failed: {e}", flush=True)


# ============================================================================
# HOT-RELOAD
# ============================================================================

async def check_and_reload_mappings(k_ws, pm_ws, pusher=None) -> bool:
    """Check for signal file from auto_mapper.py and hot-reload mappings.
    Returns True if mappings were reloaded."""
    global VERIFIED_MAPS, _last_signal_check

    now = time.time()
    if now - _last_signal_check < SIGNAL_CHECK_INTERVAL:
        return False
    _last_signal_check = now

    if not os.path.exists(MAPPINGS_SIGNAL_FILE):
        return False

    # Read and remove signal file
    try:
        with open(MAPPINGS_SIGNAL_FILE, "r") as f:
            signal = json.load(f)
        os.remove(MAPPINGS_SIGNAL_FILE)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[RELOAD] Bad signal file: {e}", flush=True)
        try:
            os.remove(MAPPINGS_SIGNAL_FILE)
        except OSError:
            pass
        return False

    prev_count = signal.get("prev_count", "?")
    new_count = signal.get("new_count", "?")
    added = signal.get("added_games", [])
    print(f"\n[RELOAD] Signal detected: {prev_count} -> {new_count} mappings", flush=True)
    if added:
        for g in added:
            print(f"[RELOAD]   + {g}", flush=True)

    # Reload mappings from disk
    old_keys = set(VERIFIED_MAPS.keys())
    new_maps = load_verified_mappings()
    if not new_maps:
        print("[RELOAD] Failed to load new mappings, keeping old ones", flush=True)
        return False

    VERIFIED_MAPS = new_maps

    # Clear runtime sanity-check caches so reloaded games get re-checked
    price_mismatch_games.clear()
    _pm_price_checked.clear()

    # Update pusher's reference to the new VERIFIED_MAPS (it was reassigned above)
    if pusher:
        pusher.verified_maps = VERIFIED_MAPS

    # Rebuild ticker lookup tables
    old_tickers = set(ticker_to_cache_key.keys())
    old_slugs = set(pm_slug_to_cache_keys.keys())
    build_ticker_mappings()
    new_tickers = set(ticker_to_cache_key.keys())
    new_slugs = set(pm_slug_to_cache_keys.keys())

    print(f"[RELOAD] Mappings reloaded: {len(VERIFIED_MAPS)} games, {len(new_tickers)} tickers", flush=True)

    # Subscribe to new tickers/slugs that weren't there before
    added_tickers = sorted(new_tickers - old_tickers)
    added_slugs = sorted(new_slugs - old_slugs)

    if added_tickers:
        print(f"[RELOAD] Subscribing to {len(added_tickers)} new Kalshi tickers", flush=True)
        await k_ws.subscribe(added_tickers)

    if added_slugs:
        print(f"[RELOAD] Subscribing to {len(added_slugs)} new PM slugs", flush=True)
        await pm_ws.subscribe(added_slugs)

    return True


# ============================================================================
# INITIALIZATION
# ============================================================================

def build_ticker_mappings():
    """Build mapping from Kalshi tickers to cache keys and PM slugs to cache keys"""
    global ticker_to_cache_key, cache_key_to_tickers, pm_slug_to_cache_keys

    # Clear old mappings so reloads don't accumulate stale entries
    # Use .clear() to preserve dict identity (pusher thread holds references)
    ticker_to_cache_key.clear()
    cache_key_to_tickers.clear()
    pm_slug_to_cache_keys.clear()

    # Use local time for date filtering (games are stored with local dates)
    # Include yesterday, today, and tomorrow to handle timezone edge cases
    now_local = datetime.now()
    yesterday = (now_local - timedelta(days=1)).strftime('%Y-%m-%d')
    today = now_local.strftime('%Y-%m-%d')
    tomorrow = (now_local + timedelta(days=1)).strftime('%Y-%m-%d')
    valid_dates = {yesterday, today, tomorrow}

    for cache_key, mapping in VERIFIED_MAPS.items():
        if not mapping.get('verified'):
            continue
        game_date = mapping.get('date', '')
        if game_date not in valid_dates:
            continue

        # Map Kalshi tickers to cache keys
        kalshi_tickers = mapping.get('kalshi_tickers', {})
        for team, ticker in kalshi_tickers.items():
            if ticker:
                ticker_to_cache_key[ticker] = cache_key
                if cache_key not in cache_key_to_tickers:
                    cache_key_to_tickers[cache_key] = []
                cache_key_to_tickers[cache_key].append(ticker)

        # Map PM slugs to cache keys (for PM WS spread triggers)
        pm_slug = mapping.get('pm_slug')
        if pm_slug:
            if pm_slug not in pm_slug_to_cache_keys:
                pm_slug_to_cache_keys[pm_slug] = []
            pm_slug_to_cache_keys[pm_slug].append(cache_key)

    print(f"[INIT] Mapped {len(ticker_to_cache_key)} Kalshi tickers to {len(cache_key_to_tickers)} games")


async def run_self_test(kalshi_api: KalshiAPI, pm_api: PolymarketUSAPI):
    """Test WebSocket connection and REST auth"""
    print("\n[SELF-TEST] Testing connections...")

    async with aiohttp.ClientSession() as session:
        # Test Kalshi REST
        print("[TEST] Kalshi REST API...")
        k_bal = await kalshi_api.get_balance(session)
        if k_bal is not None:
            print(f"  [PASS] Kalshi balance: ${k_bal:.2f}")
        else:
            print("  [FAIL] Kalshi balance fetch failed")
            return False

        # Test PM REST
        print("[TEST] PM US REST API...")
        pm_bal = await pm_api.get_balance(session)
        if pm_bal is not None:
            print(f"  [PASS] PM US balance: ${pm_bal:.2f}")
        else:
            print("  [FAIL] PM US balance fetch failed")
            return False

        # Test Kalshi WebSocket
        print("[TEST] Kalshi WebSocket...")
        try:
            with open(os.path.join(os.path.dirname(__file__) or '.', 'kalshi.pem')) as f:
                kalshi_pk_pem = f.read()
        except:
            print("  [FAIL] Could not load kalshi.pem")
            return False
        ws = KalshiWebSocket(kalshi_api.api_key, kalshi_pk_pem)
        if await ws.connect():
            print("  [PASS] WebSocket connected")

            # Try subscribing to one ticker
            if ticker_to_cache_key:
                test_ticker = list(ticker_to_cache_key.keys())[0]
                if await ws.subscribe([test_ticker]):
                    print(f"  [PASS] Subscribed to {test_ticker}")

                    # Wait for snapshot
                    try:
                        msg = await asyncio.wait_for(ws.ws.recv(), timeout=5)
                        data = json.loads(msg)
                        if data.get('type') == 'orderbook_snapshot':
                            print(f"  [PASS] Received orderbook snapshot")
                        else:
                            print(f"  [INFO] Received: {data.get('type')}")
                    except asyncio.TimeoutError:
                        print("  [WARN] No snapshot received in 5s")

            await ws.close()
        else:
            print("  [FAIL] WebSocket connection failed")
            return False

    print("\n[SELF-TEST] All tests passed!")
    return True


# ============================================================================
# PM SDK CONNECTION KEEPALIVE
# ============================================================================

async def pm_sdk_keepalive(pm_api: 'PolymarketUSAPI'):
    """Ping PM API every 30s to keep httpx connection pool warm.

    The SDK uses httpx with connection pooling.  Warm requests take ~22ms
    vs 200ms+ cold (TLS handshake).  Connections die after ~60s idle, so
    we ping every 30s to keep them alive.
    """
    while not shutdown_requested:
        try:
            await asyncio.sleep(30)
            if pm_api._sdk_client is None:
                continue
            # Pick any active slug from current mappings
            slug = next(iter(pm_slug_to_cache_keys), None)
            if slug is None:
                continue
            await pm_api._sdk_client.markets.bbo(slug)
        except Exception:
            pass  # Silent — this is just keepalive


# ============================================================================
# MAIN
# ============================================================================

async def main_loop(kalshi_api: KalshiAPI, pm_api: PolymarketUSAPI, pm_secret: str, args):
    """Main execution loop"""
    global VERIFIED_MAPS, shutdown_requested

    # Initialize orderbook snapshot database
    orderbook_db.init_db()

    # Load verified mappings
    VERIFIED_MAPS = load_verified_mappings()
    if not VERIFIED_MAPS:
        print("[ERROR] No verified mappings found. Run pregame_mapper.py first.", flush=True)
        return

    print(f"[INIT] Loaded {len(VERIFIED_MAPS)} verified mappings", flush=True)

    # CRITICAL: Verify all mappings before trading
    print("[VERIFY] Running startup verification...", flush=True)
    if not run_startup_verification(VERIFIED_MAPS):
        print("[FATAL] Mapping verification failed. REFUSING TO TRADE.", flush=True)
        print("[FATAL] Fix the mappings and regenerate with pregame_mapper.py", flush=True)
        return

    print("[VERIFY] All mappings passed structural verification", flush=True)

    # Build ticker mappings
    build_ticker_mappings()

    # Initialize OMI signal cache
    try:
        await omi_cache.refresh()
    except Exception as e:
        print(f"[OMI] Initial cache load failed: {e}")

    if not ticker_to_cache_key:
        print("[ERROR] No active tickers for today/tomorrow")
        return

    # Warm up PM SDK connection pool (first call is always cold ~200ms+)
    if pm_api._sdk_client is not None:
        warmup_slug = next(iter(pm_slug_to_cache_keys), None)
        if warmup_slug:
            try:
                await pm_api._sdk_client.markets.bbo(warmup_slug)
                print("[PM-SDK] Connection pool warmed up")
            except Exception:
                print("[PM-SDK] Warmup ping failed (non-fatal)")

    async with aiohttp.ClientSession() as session:
        # Get balances (detailed: cash + portfolio for each platform)
        k_cash, k_portfolio, pm_cash, pm_portfolio = 0.0, 0.0, 0.0, 0.0
        try:
            k_path = '/trade-api/v2/portfolio/balance'
            async with session.get(
                f'{kalshi_api.BASE_URL}{k_path}',
                headers=kalshi_api._headers('GET', k_path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    k_cash = round(data.get('balance', 0) / 100, 2)
                    k_positions_value = round(data.get('portfolio_value', 0) / 100, 2)
                    k_portfolio = round(k_cash + k_positions_value, 2)
        except Exception as e:
            print(f"[CAPITAL] Kalshi balance error: {e}")
        pm_positions_value = 0.0
        pm_positions_source = "margin"
        try:
            pm_path = '/v1/account/balances'
            async with session.get(
                f'{pm_api.BASE_URL}{pm_path}',
                headers=pm_api._headers('GET', pm_path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    for b in data.get('balances', []):
                        if b.get('currency') == 'USD':
                            pm_cash = round(float(b.get('buyingPower', 0)), 2)
                            # Default: margin-based (currentBalance - buyingPower)
                            pm_positions_value = round(
                                float(b.get('currentBalance', 0)) - float(b.get('buyingPower', 0)), 2)
                            break
        except Exception as e:
            print(f"[CAPITAL] PM balance error: {e}")

        # Fetch actual PM positions for mark-to-market
        try:
            pos_path = '/v1/portfolio/positions'
            async with session.get(
                f'{pm_api.BASE_URL}{pos_path}',
                headers=pm_api._headers('GET', pos_path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    pos_data = await r.json()
                    positions_dict = pos_data.get('positions', {})
                    if isinstance(positions_dict, dict):
                        mkt_value = 0.0
                        for slug, pos in positions_dict.items():
                            if not isinstance(pos, dict):
                                continue
                            net = int(pos.get('netPosition', 0) or 0)
                            if net != 0:
                                cv = pos.get('cashValue')
                                if isinstance(cv, dict):
                                    mkt_value += float(cv.get('value', 0))
                                elif cv is not None:
                                    mkt_value += float(cv)
                        pm_positions_value = round(mkt_value, 2)
                        pm_positions_source = "market"
        except Exception as e:
            print(f"[CAPITAL] PM positions fetch failed, using margin: {e}")

        pm_portfolio = round(pm_cash + pm_positions_value, 2)
        print(f"\n[CAPITAL] Kalshi: cash=${k_cash:.2f} portfolio=${k_portfolio:.2f} | "
              f"PM: cash=${pm_cash:.2f} positions=${pm_positions_value:.2f} ({pm_positions_source}) portfolio=${pm_portfolio:.2f}")

        # Seed live_balances for dashboard
        live_balances["k_cash"] = k_cash
        live_balances["k_portfolio"] = k_portfolio
        live_balances["pm_cash"] = pm_cash
        live_balances["pm_portfolio"] = pm_portfolio
        live_balances["pm_positions_value"] = pm_positions_value
        live_balances["pm_positions_source"] = pm_positions_source
        live_balances["kalshi_balance"] = k_portfolio
        live_balances["pm_balance"] = pm_cash
        live_balances["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Create Kalshi WebSocket connection
        kalshi_pk_pem = None
        try:
            with open(os.path.join(os.path.dirname(__file__) or '.', 'kalshi.pem')) as f:
                kalshi_pk_pem = f.read()
        except:
            pass
        if not kalshi_pk_pem:
            print("[ERROR] Could not load kalshi.pem for WebSocket")
            return

        k_ws = KalshiWebSocket(kalshi_api.api_key, kalshi_pk_pem)

        # Create PM WebSocket connection
        pm_ws = PMWebSocket(pm_api.api_key, pm_secret)

        # Set up spread handler (shared by both WebSockets)
        async def on_spread(arb):
            await handle_spread_detected(arb, session, kalshi_api, pm_api)

        k_ws.on_spread_detected = on_spread
        pm_ws.on_spread_detected = on_spread

        # Connect Kalshi WebSocket
        if not await k_ws.connect():
            print("[ERROR] Failed to connect to Kalshi WebSocket")
            return

        tickers = list(ticker_to_cache_key.keys())
        if not await k_ws.subscribe(tickers):
            print("[ERROR] Failed to subscribe to Kalshi tickers")
            return

        # Connect PM WebSocket
        if not await pm_ws.connect():
            print("[ERROR] Failed to connect to PM WebSocket")
            return

        pm_slugs = list(pm_slug_to_cache_keys.keys())
        if not await pm_ws.subscribe(pm_slugs):
            print("[ERROR] Failed to subscribe to PM markets")
            return

        gtc_status = f"ON (timeout={Config.gtc_timeout_seconds}s, recheck={Config.gtc_recheck_interval_ms}ms)" if Config.enable_gtc else "OFF"
        print(f"\n{'='*70}")
        print(f"DUAL WS EXECUTOR: K={len(tickers)} tickers, PM={len(pm_slugs)} markets")
        print(f"Mode: {'LIVE' if Config.is_live() else 'PAPER'}")
        print(f"Min spread: {Config.spread_min_cents}c | Max contracts: {Config.max_contracts}")
        print(f"GTC (maker): {gtc_status}")
        print(f"{'='*70}\n")

        # Start WebSocket listener tasks
        k_ws_task = asyncio.create_task(k_ws.listen())
        pm_ws_task = asyncio.create_task(pm_ws.listen())

        # PM subscription health: log which markets respond within 5s
        asyncio.create_task(pm_ws.log_subscription_health(delay=5.0))

        # PM resubscription monitor: resub silent markets every 60s
        resub_task = asyncio.create_task(pm_resub_monitor(pm_ws))

        # PM REST fallback: poll BBO for markets missing WS data >30s
        rest_fallback_task = asyncio.create_task(
            pm_rest_fallback_poller(pm_ws, pm_api, session)
        )

        # Keep PM SDK httpx connection pool warm (prevents 200ms+ cold starts)
        keepalive_task = asyncio.create_task(pm_sdk_keepalive(pm_api))

        # Background snapshot recorder (drains dirty_tickers every 5s)
        snapshot_task = asyncio.create_task(periodic_snapshot_recorder())

        # ESPN live scores (polls every 45s, no auth needed)
        espn = ESPNScores()

        # Start dashboard push (if DASHBOARD_URL is set in .env)
        pusher = DashboardPusher()
        pusher.set_state_sources(
            local_books=local_books,
            pm_prices=pm_prices,
            pm_books=pm_books,
            ticker_to_cache_key=ticker_to_cache_key,
            cache_key_to_tickers=cache_key_to_tickers,
            stats=stats,
            balances=live_balances,
            live_positions=live_positions,
            verified_maps=VERIFIED_MAPS,
            executor_version="ws-v8",
            omi_cache=omi_cache,
            espn_scores=espn,
        )
        pusher.start(interval=5)

        # Status logging loop
        try:
            while not shutdown_requested:
                log_status()
                print_spread_snapshot()  # One-time snapshot after data loads
                await refresh_balances(session, kalshi_api, pm_api)
                await check_and_reload_mappings(k_ws, pm_ws, pusher=pusher)
                if omi_cache.is_stale():
                    asyncio.create_task(omi_cache.refresh())  # Non-blocking
                await espn.poll(session, VERIFIED_MAPS)  # Self-throttles to every 45s
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received interrupt, stopping...")
            shutdown_requested = True

        # Cleanup
        pusher.stop()
        try:
            await pm_api.close()
        except Exception:
            pass
        k_ws_task.cancel()
        pm_ws_task.cancel()
        keepalive_task.cancel()
        resub_task.cancel()
        rest_fallback_task.cancel()
        await k_ws.close()
        await pm_ws.close()

        print("[SHUTDOWN] Complete")


def main():
    global shutdown_requested

    import argparse

    parser = argparse.ArgumentParser(description='WebSocket-based Arbitrage Executor')
    parser.add_argument('--live', action='store_true', help='Live trading mode')
    parser.add_argument('--paper', action='store_true', help='Paper trading mode (default)')
    parser.add_argument('--spread-min', type=int, default=4, help='Minimum spread in cents')
    parser.add_argument('--contracts', type=int, default=20, help='Max contracts per trade (depth algo governs actual size)')
    parser.add_argument('--self-test', action='store_true', dest='self_test',
                       help='Test connections and exit')
    parser.add_argument('--pnl', action='store_true', help='Show P&L summary and exit')
    parser.add_argument('--one-trade', action='store_true', dest='one_trade',
                       help='Stop after first trade attempt (for testing)')
    parser.add_argument('--max-trades', type=int, default=0, dest='max_trades',
                       help='Stop after N successful trades (0 = unlimited)')
    parser.add_argument('--clear-traded', action='store_true', dest='clear_traded',
                       help='Clear traded_games.json (use for new trading day)')
    parser.add_argument('--max-positions', type=int, default=None, dest='max_positions',
                       help='Max concurrent positions (default: 15)')
    parser.add_argument('--min-profit', type=float, default=1.0, dest='min_profit',
                       help='Min expected net profit in cents per marginal contract (default 1.0)')
    parser.add_argument('--depth-factor', type=float, default=0.70, dest='depth_factor',
                       help='Fraction of available depth to use (default 0.70)')
    parser.add_argument('--gtc-timeout', type=float, default=None, dest='gtc_timeout',
                       help='GTC order timeout in seconds (default: 3)')
    parser.add_argument('--spread-recheck-interval', type=int, default=None,
                       dest='spread_recheck_interval',
                       help='GTC spread recheck interval in ms (default: 200)')
    parser.add_argument('--enable-gtc', action='store_true', default=None,
                       dest='enable_gtc', help='Enable IOC-then-GTC (default)')
    parser.add_argument('--no-gtc', action='store_false', dest='enable_gtc',
                       help='Disable GTC, use IOC only')

    args = parser.parse_args()

    # Handle --pnl
    if args.pnl:
        print_pnl_summary()
        return

    # Load previously traded games (prevents duplicate trades across restarts)
    traded_count = load_traded_games(clear=args.clear_traded)
    if traded_count > 0:
        print(f"[INIT] Loaded {traded_count} previously traded games from traded_games.json")

    # Load directional positions (OMI Tier 3a/3b exposure tracking)
    dir_exposure, dir_loss = load_directional_positions()
    if dir_exposure > 0 or dir_loss > 0:
        print(f"[INIT] Directional positions: exposure=${dir_exposure:.2f}, daily_loss=${dir_loss:.2f}")

    # Configure shared Config object - this is the single source of truth
    # All imported v7 functions will read from Config automatically
    Config.configure_from_args(args)

    # Set one-trade test mode
    global ONE_TRADE_TEST_MODE
    if args.one_trade:
        ONE_TRADE_TEST_MODE = True
        print("[ONE-TRADE TEST MODE] Will stop after first trade attempt")

    # Set max trades limit
    global MAX_TRADES_LIMIT
    if args.max_trades > 0:
        MAX_TRADES_LIMIT = args.max_trades
        print(f"[MAX TRADES] Will stop after {MAX_TRADES_LIMIT} successful trades")

    # Load API credentials - same as v7
    # Kalshi credentials
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    try:
        with open(os.path.join(os.path.dirname(__file__), 'kalshi.pem')) as f:
            kalshi_pk = f.read()
    except FileNotFoundError:
        print("[ERROR] kalshi.pem not found")
        return

    # PM US credentials from .env or environment
    from dotenv import load_dotenv
    load_dotenv()
    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')

    if not pm_key or not pm_secret:
        print("[ERROR] Missing PM US credentials. Set PM_US_API_KEY and PM_US_SECRET_KEY in .env")
        return

    # Initialize APIs
    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)
    pm_api = PolymarketUSAPI(pm_key, pm_secret)

    # Load verified mappings for self-test
    global VERIFIED_MAPS
    VERIFIED_MAPS = load_verified_mappings()
    build_ticker_mappings()

    # Handle --self-test
    if args.self_test:
        asyncio.run(run_self_test(kalshi_api, pm_api))
        return

    # Set up signal handlers
    def handle_signal(sig, frame):
        global shutdown_requested
        print(f"\n[SIGNAL] Received {sig}, shutting down...")
        shutdown_requested = True

    signal.signal(signal.SIGINT, handle_signal)
    try:
        signal.signal(signal.SIGTERM, handle_signal)
    except (ValueError, OSError):
        pass  # SIGTERM not available on Windows

    # Run main loop
    print(f"\n{'='*70}")
    print("WEBSOCKET ARBITRAGE EXECUTOR")
    print(f"{'='*70}")

    asyncio.run(main_loop(kalshi_api, pm_api, pm_secret, args))


if __name__ == "__main__":
    main()
