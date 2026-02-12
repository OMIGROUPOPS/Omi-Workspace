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

from dashboard_push import DashboardPusher

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
    TradeResult,
    traded_games,           # Shared state - games traded this session
    blacklisted_games,      # Shared state - games blacklisted after crashes
    load_traded_games,      # Load persisted traded games on startup
    save_traded_game,       # Save traded game after successful trade
)

from pregame_mapper import load_verified_mappings
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

# Mapping from Kalshi ticker -> cache_key (for spread detection)
ticker_to_cache_key: Dict[str, str] = {}
# Mapping from cache_key -> list of kalshi tickers
cache_key_to_tickers: Dict[str, List[str]] = {}
# Mapping from PM slug -> list of cache_keys (for PM WS spread triggers)
pm_slug_to_cache_keys: Dict[str, List[str]] = {}

# Verified mappings
VERIFIED_MAPS: Dict = {}

# Signal file for hot-reload (written by auto_mapper.py)
MAPPINGS_SIGNAL_FILE = os.path.join(os.path.dirname(__file__) or '.', 'mappings_updated.flag')
_last_signal_check: float = 0
SIGNAL_CHECK_INTERVAL = 60  # Check every 60 seconds

# Live balances (refreshed periodically, read by dashboard pusher)
live_balances: Dict = {"kalshi_balance": 0, "pm_balance": 0, "updated_at": ""}
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
        # Case 2: PM BUY_SHORT (intent=3) at pm_ask (underdog's ask, already inverted in cache)
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

    # Check BUY_PM_SELL_K (Case 1: is_long_team uses BUY_LONG, Case 2: uses BUY_SHORT)
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
                        # Check for spread after snapshot
                        arb = check_spread_for_ticker(ticker)
                        if arb and self.on_spread_detected:
                            await self.on_spread_detected(arb)

                elif msg_type == 'orderbook_delta':
                    ticker = msg_data.get('market_ticker')
                    if ticker:
                        apply_orderbook_delta(ticker, msg_data)
                        # Check for spread after every delta - this is the key!
                        arb = check_spread_for_ticker(ticker)
                        if arb and self.on_spread_detected:
                            await self.on_spread_detected(arb)

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
        """Subscribe to market data for given slugs"""
        if not self.connected or not self.ws:
            return False

        subscribe_msg = {
            "subscribe": {
                "request_id": "arb-executor-sub",
                "subscription_type": 1,  # MARKET_DATA (full orderbook)
                "market_slugs": slugs
            }
        }

        try:
            await self.ws.send(json.dumps(subscribe_msg))
            print(f"[PM WS] Subscribed to {len(slugs)} markets")
            return True
        except Exception as e:
            print(f"[PM WS] Subscribe failed: {e}")
            return False

    def _handle_market_data(self, data: Dict):
        """Parse PM WS orderbook update and update local PM book cache"""
        global stats

        if "marketData" not in data:
            return

        md = data["marketData"]
        pm_slug = md.get("marketSlug", "")

        if not pm_slug:
            return

        # Parse best bid/ask from orderbook
        bids = md.get("bids", [])
        offers = md.get("offers", [])

        if not bids or not offers:
            return

        # Sort bids descending by price (highest = best bid)
        # Sort offers ascending by price (lowest = best ask)
        sorted_bids = sorted(bids, key=lambda x: float(x["px"]["value"]), reverse=True)
        sorted_offers = sorted(offers, key=lambda x: float(x["px"]["value"]))

        best_bid = float(sorted_bids[0]["px"]["value"]) * 100  # Convert to cents
        best_bid_size = int(float(sorted_bids[0]["qty"]))
        best_ask = float(sorted_offers[0]["px"]["value"]) * 100  # Convert to cents
        best_ask_size = int(float(sorted_offers[0]["qty"]))

        # Find all cache_keys mapped to this PM slug
        cache_keys = pm_slug_to_cache_keys.get(pm_slug, [])

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
                arb = check_spread_for_ticker(ticker)
                if arb and self.on_spread_detected:
                    await self.on_spread_detected(arb)

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

    # Check kill switch
    if check_kill_switch():
        print(f"[EXEC] Kill switch active - skipping")
        return

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

    # -------------------------------------------------------------------------
    # NO REST CONFIRMATION - Trust WS prices + PM buffer
    # PM-first execution means bad price = PM order expires = no harm
    # Saves 50-100ms latency where competitors steal spreads
    # -------------------------------------------------------------------------
    stats['spreads_detected'] += 1

    # Estimate profit
    net_profit, breakdown = estimate_net_profit_cents(arb)
    if net_profit < Config.min_profit_cents:
        print(f"[EXEC] Net profit {net_profit:.1f}c < min {Config.min_profit_cents}c - skipping")
        log_skipped_arb(arb, 'low_profit', f'Net {net_profit:.1f}c < min {Config.min_profit_cents}c')
        return

    print(f"[EXEC] Est. net profit: {net_profit:.1f}c/contract")

    # -------------------------------------------------------------------------
    # Execute via executor_core (clean execution engine)
    # -------------------------------------------------------------------------
    async with EXECUTION_LOCK:
        last_trade_time = time.time()
        print(f"[EXEC] Executing 1 contract via executor_core...")

        result = await execute_arb(
            arb=arb,
            session=session,
            kalshi_api=kalshi_api,
            pm_api=pm_api,
            pm_slug=arb.pm_slug,
            pm_outcome_idx=arb.pm_outcome_index,
        )

        # Handle result
        if result.success:
            # Show timing breakdown: PM first (unreliable) → K second (reliable)
            timing = f"pm={result.pm_order_ms}ms → k={result.k_order_ms}ms → TOTAL={result.execution_time_ms}ms"
            print(f"[EXEC] SUCCESS: PM={result.pm_filled}@{result.pm_price:.2f}, K={result.kalshi_filled}@{result.kalshi_price}c | {timing}")
            # Build result dicts for log_trade compatibility
            k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price}
            pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price}
            log_trade(arb, k_result, pm_result, 'SUCCESS', execution_time_ms=result.execution_time_ms)

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
            k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price}
            pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price}
            log_trade(arb, k_result, pm_result, 'UNHEDGED', execution_time_ms=result.execution_time_ms)
            # Save unhedged position for recovery
            try:
                from arb_executor_v7 import HedgeState
                hedge_state = HedgeState(
                    kalshi_ticker=arb.kalshi_ticker,
                    pm_slug=arb.pm_slug,
                    target_qty=1,
                    kalshi_filled=result.kalshi_filled,
                    pm_filled=result.pm_filled,
                    kalshi_price=result.kalshi_price,
                    pm_price=int(result.pm_price * 100),
                )
                save_unhedged_position(hedge_state, result.abort_reason)
            except Exception as e:
                print(f"[ERROR] Failed to save unhedged position: {e}")

        elif result.pm_filled == 0:
            # PM didn't fill - safe exit, no position taken
            print(f"[EXEC] PM NO FILL (safe): {result.abort_reason} | pm={result.pm_order_ms}ms")
            k_result = {'fill_count': 0, 'fill_price': result.kalshi_price}
            pm_result = {'fill_count': 0, 'fill_price': result.pm_price}
            log_trade(arb, k_result, pm_result, 'PM_NO_FILL', execution_time_ms=result.execution_time_ms)

        else:
            print(f"[EXEC] ABORTED: {result.abort_reason}")

        # One-trade test mode: stop after first trade attempt
        if ONE_TRADE_TEST_MODE:
            print("\n" + "=" * 70)
            print("ONE-TRADE TEST COMPLETE - STOPPING")
            print("=" * 70)
            shutdown_requested = True


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
    """Periodically fetch balances from both platforms."""
    global _last_balance_refresh

    now = time.time()
    if now - _last_balance_refresh < BALANCE_REFRESH_INTERVAL:
        return
    _last_balance_refresh = now

    try:
        k_bal = await kalshi_api.get_balance(session)
        pm_bal = await pm_api.get_balance(session)
        live_balances["kalshi_balance"] = round(k_bal or 0, 2)
        live_balances["pm_balance"] = round(pm_bal or 0, 2)
        live_balances["updated_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        print(f"[BALANCE] Refresh failed: {e}", flush=True)


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
# MAIN
# ============================================================================

async def main_loop(kalshi_api: KalshiAPI, pm_api: PolymarketUSAPI, pm_secret: str, args):
    """Main execution loop"""
    global VERIFIED_MAPS, shutdown_requested

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

    if not ticker_to_cache_key:
        print("[ERROR] No active tickers for today/tomorrow")
        return

    async with aiohttp.ClientSession() as session:
        # Get balances
        k_bal = await kalshi_api.get_balance(session)
        pm_bal = await pm_api.get_balance(session)
        k_bal = k_bal or 0
        pm_bal = pm_bal or 0
        print(f"\n[CAPITAL] Kalshi: ${k_bal:.2f} | PM US: ${pm_bal:.2f}")

        # Seed live_balances for dashboard
        live_balances["kalshi_balance"] = round(k_bal, 2)
        live_balances["pm_balance"] = round(pm_bal, 2)
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

        print(f"\n{'='*70}")
        print(f"DUAL WS EXECUTOR: K={len(tickers)} tickers, PM={len(pm_slugs)} markets")
        print(f"Mode: {'LIVE' if Config.is_live() else 'PAPER'}")
        print(f"Min spread: {Config.spread_min_cents}c | Max contracts: {Config.max_contracts}")
        print(f"{'='*70}\n")

        # Start WebSocket listener tasks
        k_ws_task = asyncio.create_task(k_ws.listen())
        pm_ws_task = asyncio.create_task(pm_ws.listen())

        # Start dashboard push (if DASHBOARD_URL is set in .env)
        pusher = DashboardPusher()
        pusher.set_state_sources(
            local_books=local_books,
            pm_prices=pm_prices,
            ticker_to_cache_key=ticker_to_cache_key,
            cache_key_to_tickers=cache_key_to_tickers,
            stats=stats,
            balances=live_balances,
            verified_maps=VERIFIED_MAPS,
            executor_version="ws-v8",
        )
        pusher.start(interval=5)

        # Status logging loop
        try:
            while not shutdown_requested:
                log_status()
                print_spread_snapshot()  # One-time snapshot after data loads
                await refresh_balances(session, kalshi_api, pm_api)
                await check_and_reload_mappings(k_ws, pm_ws, pusher=pusher)
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received interrupt, stopping...")
            shutdown_requested = True

        # Cleanup
        pusher.stop()
        k_ws_task.cancel()
        pm_ws_task.cancel()
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
    parser.add_argument('--contracts', type=int, default=1, help='Max contracts per trade')
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

    args = parser.parse_args()

    # Handle --pnl
    if args.pnl:
        print_pnl_summary()
        return

    # Load previously traded games (prevents duplicate trades across restarts)
    traded_count = load_traded_games(clear=args.clear_traded)
    if traded_count > 0:
        print(f"[INIT] Loaded {traded_count} previously traded games from traded_games.json")

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
