#!/usr/bin/env python3
"""
DUAL-PLATFORM ARBITRAGE EXECUTOR v7 - DIRECT US EXECUTION
Kalshi + Polymarket US, both executed directly from US.
No partner webhook. Ed25519 auth for Polymarket US API.

HARD LIMITS:
- MAX 20 contracts per trade
- MAX $10 total cost per trade
- buy_max_cost enforces Fill-or-Kill behavior
- Position check AFTER every order attempt
- Only execute PM US if Kalshi position actually exists
"""
import asyncio
import aiohttp
import time
import base64
import json
import re
import os
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set, Any, Tuple
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ed25519
from cryptography.hazmat.backends import default_backend

# ============================================================================
# HARD LIMITS - DO NOT CHANGE THESE
# ============================================================================
MAX_CONTRACTS = 20          # Absolute max contracts per trade
MAX_COST_CENTS = 1000       # Absolute max cost in cents ($10)
MIN_CONTRACTS = 50          # Minimum contracts for meaningful profit
MIN_LIQUIDITY = 50          # Minimum bid/ask size on both sides
MIN_PM_PRICE = 10           # Skip arbs where PM price < 10c (likely illiquid/thin)
MIN_SPREAD_CENTS = 1        # Minimum spread to consider (after fees)
MIN_SWEEP_ROI = 1.0         # Minimum ROI during sweep before stopping
MAX_ROI = 50.0              # Maximum ROI - higher is likely bad data (kept for flagging)
DEBUG_MATCHING = True       # Log matching debug info
COOLDOWN_SECONDS = 10       # Seconds between trade attempts
# NOTE: We no longer filter by ROI - we use spread * liquidity score instead
# High ROI on illiquid prices is misleading (240% ROI on 5c ask = only $2 profit)
# ============================================================================

# ============================================================================
# HEDGE PROTECTION SYSTEM
# ============================================================================
MAX_PRICE_STALENESS_MS = 200    # Max time since price fetch before refresh required
MIN_HEDGE_SPREAD_CENTS = 1      # Minimum spread required to proceed with trade
UNHEDGED_EXPOSURE_LIMIT = 1000  # Max unhedged exposure in cents ($10) before kill switch
SLIPPAGE_RECOVERY_LEVELS = [1, 2, 3, 5, 10]  # Cents of slippage to try for recovery
UNHEDGED_POSITIONS_FILE = 'unhedged_positions.json'
HEDGE_KILL_SWITCH_ACTIVE = False  # Set True to stop all trading

@dataclass
class HedgeState:
    """Track hedge state for a trade"""
    kalshi_ticker: str
    pm_slug: str
    target_qty: int
    kalshi_filled: int = 0
    pm_filled: int = 0
    kalshi_price: int = 0  # cents
    pm_price: float = 0.0  # dollars
    is_hedged: bool = False
    recovery_attempted: bool = False
    recovery_slippage: int = 0  # cents of slippage used in recovery

@dataclass
class PositionState:
    """Track positions across platforms"""
    kalshi_positions: Dict[str, int] = field(default_factory=dict)  # ticker -> qty
    pm_positions: Dict[str, int] = field(default_factory=dict)      # slug -> qty
    expected_kalshi: Dict[str, int] = field(default_factory=dict)   # what we think we have
    expected_pm: Dict[str, int] = field(default_factory=dict)
    last_sync: float = 0.0

# Global position state
POSITION_STATE = PositionState()

def load_unhedged_positions() -> List[Dict]:
    """Load unhedged positions from file"""
    try:
        if os.path.exists(UNHEDGED_POSITIONS_FILE):
            with open(UNHEDGED_POSITIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"[HEDGE] Error loading unhedged positions: {e}")
    return []

def save_unhedged_position(hedge_state: HedgeState, reason: str):
    """Save unhedged position to file for manual recovery"""
    positions = load_unhedged_positions()
    positions.append({
        'timestamp': datetime.now().isoformat(),
        'kalshi_ticker': hedge_state.kalshi_ticker,
        'pm_slug': hedge_state.pm_slug,
        'kalshi_filled': hedge_state.kalshi_filled,
        'pm_filled': hedge_state.pm_filled,
        'unhedged_qty': hedge_state.kalshi_filled - hedge_state.pm_filled,
        'kalshi_price': hedge_state.kalshi_price,
        'pm_price': hedge_state.pm_price,
        'reason': reason,
        'recovery_attempted': hedge_state.recovery_attempted,
        'recovery_slippage': hedge_state.recovery_slippage
    })
    try:
        with open(UNHEDGED_POSITIONS_FILE, 'w') as f:
            json.dump(positions, f, indent=2)
        print(f"[HEDGE] Saved unhedged position to {UNHEDGED_POSITIONS_FILE}")
    except Exception as e:
        print(f"[HEDGE] ERROR saving unhedged position: {e}")

def check_kill_switch() -> bool:
    """Check if kill switch is active"""
    global HEDGE_KILL_SWITCH_ACTIVE
    if HEDGE_KILL_SWITCH_ACTIVE:
        print("[!!! KILL SWITCH !!!] Trading halted due to unhedged position")
        return True
    return False

def activate_kill_switch(reason: str):
    """Activate the kill switch to stop all trading"""
    global HEDGE_KILL_SWITCH_ACTIVE
    HEDGE_KILL_SWITCH_ACTIVE = True
    print(f"\n{'='*60}")
    print("[!!! KILL SWITCH ACTIVATED !!!]")
    print(f"Reason: {reason}")
    print("All trading has been halted.")
    print("Manual intervention required to restart.")
    print(f"Use --force flag to override (for recovery only)")
    print(f"{'='*60}\n")

# ROI distribution tracking
ROI_BUCKETS = {
    '0-1%': 0,
    '1-2%': 0,
    '2-3%': 0,
    '3-5%': 0,
    '5-10%': 0,
    '10%+': 0
}

class ExecutionMode(Enum):
    PAPER = "paper"
    LIVE = "live"

# START IN PAPER MODE - Change to LIVE only when ready
EXECUTION_MODE = ExecutionMode.PAPER

# Paper trading unlimited mode - ignore capital constraints to see full arb market
PAPER_NO_LIMITS = True  # Default True for paper mode, set via --no-limits flag

# Paper trading stats
PAPER_STATS = {
    'total_arbs_executed': 0,
    'total_theoretical_profit': 0.0,
    'total_contracts': 0,
    'start_time': None,
}

KALSHI_API_KEY = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
KALSHI_PRIVATE_KEY = open('kalshi.pem').read()

# Polymarket US credentials (Ed25519 auth)
PM_US_API_KEY = 'b215c231-f041-4b98-a048-a203acb6573e'
PM_US_SECRET_KEY = 'WL5Q1uEF3vCvESisQ/kLfflRQFNeOOVyZ8uA84l7A0ktsX2NxnB9IYFdGoKWtQq1RygUlFE0KY60r3o6vCSe3w=='

# Fee rates
KALSHI_FEE = 0.01
PM_US_TAKER_FEE_RATE = 0.001  # 0.10% (10 basis points) on notional

# PM US order intents
PM_BUY_YES = 1
PM_SELL_YES = 2
PM_BUY_NO = 3
PM_SELL_NO = 4

# Trade log - load existing trades on startup
def load_trades() -> List[Dict]:
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
            return trades[-1000:] if len(trades) > 1000 else trades
    except (FileNotFoundError, json.JSONDecodeError):
        return []

TRADE_LOG: List[Dict] = load_trades()

# ============================================================================
# POSITION TRACKING - Prevent trading same game twice
# ============================================================================
# Key format: "KALSHI_TICKER" or "PM_SLUG" - we track both to be safe
TRADED_GAMES: Set[str] = set()

def load_traded_games() -> Set[str]:
    """Load traded games from trade log to avoid re-trading on restart"""
    traded = set()
    for trade in TRADE_LOG:
        # Add Kalshi ticker if present
        if trade.get('k_order_id') and not trade['k_order_id'].startswith('PAPER'):
            ticker = trade.get('kalshi_ticker') or ''
            if ticker:
                # Extract game ID from ticker (e.g., KXNHLGAME-25JAN28NYRN-NYR -> 25JAN28NYRN)
                parts = ticker.split('-')
                if len(parts) >= 2:
                    traded.add(parts[1])  # Game ID
        # Add PM slug if present
        pm_slug = trade.get('pm_slug')
        if pm_slug:
            traded.add(pm_slug)
    return traded

# Initialize from trade history (only for LIVE trades, not paper)
if EXECUTION_MODE == ExecutionMode.LIVE:
    TRADED_GAMES = load_traded_games()
    if TRADED_GAMES:
        print(f"[POSITION TRACKING] Loaded {len(TRADED_GAMES)} previously traded games")

# ============================================================================
# SKIPPED ARB TRACKING - Analyze missed opportunities
# ============================================================================
SKIPPED_ARBS: List[Dict] = []
SKIP_STATS: Dict[str, int] = {
    'high_roi': 0,
    'low_liquidity': 0,
    'illiquid_price': 0,
    'live_game': 0,
    'already_traded': 0,
    'cooldown': 0,
    'validation_failed': 0,
    'sweep_roi_too_low': 0,
    'no_fill': 0
}
SCAN_STATS: Dict[str, int] = {
    'total_found': 0,
    'total_executed': 0,
    'total_skipped': 0
}

# ============================================================================
# TOTAL ADDRESSABLE MARKET TRACKING (Paper mode)
# Track unique arb opportunities and their lifecycle
# ============================================================================

# Cooldown before a reopened arb counts as a new opportunity (filters API flicker)
# Reduced from 30s to 15s based on analysis: 89.7% of arbs last <30s, missing 24.7% as flickers
REOPEN_COOLDOWN_SECONDS = 15

@dataclass
class ActiveArb:
    """Track an active arbitrage opportunity"""
    arb_key: str              # Unique key: "{game}_{team}_{direction}"
    game: str
    team: str
    sport: str
    direction: str
    first_seen: float         # timestamp
    last_seen: float          # timestamp
    scan_count: int           # How many scans it's been active
    initial_spread: int       # cents
    initial_size: int
    initial_profit_cents: int
    current_spread: int
    current_size: int
    current_profit_cents: int
    kalshi_ticker: str
    pm_slug: str
    executed: bool = False    # Did we "execute" this in paper mode?
    is_reopen: bool = False   # Was this a reopen (vs first time NEW)?

@dataclass
class ClosedArb:
    """Track a closed arb for reopen detection"""
    arb_key: str
    closed_at: float          # timestamp when it closed
    sport: str
    team: str
    final_spread: int
    total_open_duration: float  # How long it was open
    total_profit_captured: int  # If we executed it

# Active arbs being tracked: {arb_key: ActiveArb}
ACTIVE_ARBS: Dict[str, ActiveArb] = {}

# Recently closed arbs for reopen detection: {arb_key: ClosedArb}
RECENTLY_CLOSED: Dict[str, ClosedArb] = {}

# Permanently closed arbs history
CLOSED_ARBS: List[ClosedArb] = []

TAM_STATS: Dict[str, Any] = {
    'scan_count': 0,
    'unique_arbs_new': 0,        # First time seeing this arb
    'unique_arbs_reopen': 0,     # Reopened after cooldown
    'flicker_ignored': 0,        # Reopened within cooldown (API noise)
    'unique_arbs_executed': 0,   # Paper "executed" once per unique arb
    'total_profit_if_captured': 0,
    'total_contracts': 0,
}

# ============================================================================
# PRICE HISTORY TRACKING
# Track prices over time for each matched game for analysis/visualization
# ============================================================================
@dataclass
class PriceSnapshot:
    """Single point-in-time price snapshot for a game/team"""
    timestamp: float
    scan_num: int
    kalshi_bid: int      # cents
    kalshi_ask: int      # cents
    pm_bid: int          # cents
    pm_ask: int          # cents
    spread_buy_pm: int   # k_bid - pm_ask (cents, can be negative)
    spread_buy_k: int    # pm_bid - k_ask (cents, can be negative)
    has_arb: bool        # True if either spread > 0 after fees

# Price history: {game_key: [PriceSnapshot, ...]}
# game_key = "{sport}:{game_id}:{team}"
PRICE_HISTORY: Dict[str, List[PriceSnapshot]] = {}

# Flag to enable chart generation on shutdown
GENERATE_CHART_ON_EXIT = False

def get_arb_key(arb) -> str:
    """Generate unique key for an arb opportunity"""
    return f"{arb.game}_{arb.team}_{arb.direction}"

def format_duration(seconds: float) -> str:
    """Format duration in human readable form"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"

def cleanup_old_closed_arbs(now: float):
    """Remove closed arbs older than 5 minutes from RECENTLY_CLOSED"""
    old_keys = [k for k, v in RECENTLY_CLOSED.items() if now - v.closed_at > 300]
    for k in old_keys:
        # Move to permanent closed list
        CLOSED_ARBS.append(RECENTLY_CLOSED[k])
        del RECENTLY_CLOSED[k]

def load_skipped_arbs() -> List[Dict]:
    """Load skipped arbs from file"""
    try:
        with open('skipped_arbs.json', 'r') as f:
            arbs = json.load(f)
            return arbs[-500:] if len(arbs) > 500 else arbs  # Keep last 500
    except (FileNotFoundError, json.JSONDecodeError):
        return []

SKIPPED_ARBS = load_skipped_arbs()

@dataclass
class ArbOpportunity:
    timestamp: datetime
    sport: str
    game: str
    team: str
    direction: str
    k_bid: float  # cents
    k_ask: float  # cents
    pm_bid: float  # cents
    pm_ask: float  # cents
    gross_spread: float
    fees: float
    net_spread: float
    size: int  # contracts
    kalshi_ticker: str
    pm_slug: str
    pm_outcome_index: int  # 0 = YES side (outcome[0]), 1 = NO side (outcome[1])
    pm_bid_size: int = 0   # Liquidity on PM bid side
    pm_ask_size: int = 0   # Liquidity on PM ask side
    needs_review: bool = False  # Flag for suspicious trades (high ROI in paper mode)
    review_reason: str = ""     # Reason for review flag
    is_live_game: bool = False  # Flag for in-progress games (higher risk)

    @property
    def profit(self):
        return (self.net_spread / 100) * self.size

    @property
    def capital(self):
        if self.direction == 'BUY_PM_SELL_K':
            return self.size * (self.pm_ask / 100)
        else:
            return self.size * (self.k_ask / 100)

    @property
    def roi(self):
        return (self.profit / self.capital * 100) if self.capital > 0 else 0

@dataclass
class Position:
    ticker: str
    position: int  # positive = YES, negative = NO
    market_exposure: int


class KalshiAPI:
    BASE_URL = 'https://api.elections.kalshi.com'

    def __init__(self, api_key, private_key):
        self.api_key = api_key
        self.private_key = serialization.load_pem_private_key(
            private_key.encode(), password=None, backend=default_backend()
        )

    def _sign(self, ts, method, path):
        msg = f'{ts}{method}{path}'.encode('utf-8')
        sig = self.private_key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')

    def _headers(self, method, path):
        ts = str(int(time.time() * 1000))
        return {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-SIGNATURE': self._sign(ts, method, path),
            'KALSHI-ACCESS-TIMESTAMP': ts,
            'Content-Type': 'application/json'
        }

    async def get_balance(self, session) -> Optional[float]:
        path = '/trade-api/v2/portfolio/balance'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('balance', 0) / 100
        except Exception as e:
            print(f"   [!] Balance fetch error: {e}")
        return None

    async def get_positions(self, session) -> Dict[str, Position]:
        path = '/trade-api/v2/portfolio/positions?count_filter=position'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    positions = {}
                    for mp in data.get('market_positions', []):
                        if mp.get('position', 0) != 0:
                            positions[mp['ticker']] = Position(
                                ticker=mp['ticker'],
                                position=mp['position'],
                                market_exposure=mp.get('market_exposure', 0)
                            )
                    return positions
        except Exception as e:
            print(f"   [!] Positions fetch error: {e}")
        return {}

    async def get_position_for_ticker(self, session, ticker: str) -> Optional[int]:
        path = f'/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    for mp in data.get('market_positions', []):
                        if mp['ticker'] == ticker:
                            return mp.get('position', 0)
                    return 0
        except Exception as e:
            print(f"   [!] Position fetch error: {e}")
        return None

    async def place_order(self, session, ticker: str, side: str, action: str,
                          count: int, price_cents: int) -> Dict:
        paper_unlimited = EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS

        # In paper unlimited mode, skip all limits
        if not paper_unlimited:
            # HARD LIMIT ENFORCEMENT (live mode only)
            if count > MAX_CONTRACTS:
                print(f"   [SAFETY] Capping contracts from {count} to {MAX_CONTRACTS}")
                count = MAX_CONTRACTS

            if count < MIN_CONTRACTS:
                return {'success': False, 'error': f'Count {count} below minimum {MIN_CONTRACTS}'}

            if action == 'buy':
                max_cost = count * price_cents
            else:
                max_cost = count * (100 - price_cents)

            if max_cost > MAX_COST_CENTS:
                if action == 'buy':
                    count = MAX_COST_CENTS // price_cents
                else:
                    count = MAX_COST_CENTS // (100 - price_cents)
                max_cost = count * price_cents if action == 'buy' else count * (100 - price_cents)
                print(f"   [SAFETY] Reduced to {count} contracts (max cost ${max_cost/100:.2f})")

            if count < MIN_CONTRACTS:
                return {'success': False, 'error': f'Count {count} below minimum after cost cap'}

        if EXECUTION_MODE == ExecutionMode.PAPER:
            print(f"   [PAPER] Would place: {action} {count} {side} @ {price_cents}c")
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'fill_count': count,
                'order_id': f'PAPER-{int(time.time()*1000)}',
                'paper': True
            }

        path = '/trade-api/v2/portfolio/orders'
        order_price = price_cents

        payload = {
            'ticker': ticker,
            'action': action,
            'side': side,
            'count': count,
            'type': 'limit',
            'client_order_id': str(uuid.uuid4()),
        }

        if side == 'yes':
            payload['yes_price'] = order_price
        else:
            payload['no_price'] = order_price

        if action == 'buy':
            payload['buy_max_cost'] = count * order_price + (count * 2)

        try:
            print(f"   [ORDER] {action} {count} {side} @ {order_price}c")
            print(f"   [DEBUG] Payload: {payload}")

            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                data = await r.json()
                print(f"   [DEBUG] HTTP Status: {r.status}")
                print(f"   [DEBUG] Response: {data}")

                order = data.get('order', {})
                fill_count = order.get('taker_fill_count', 0) or order.get('fill_count', 0)
                status = order.get('status', '')

                print(f"   [DEBUG] Order status: {status}, fill_count: {fill_count}")

                if r.status in [200, 201] and fill_count > 0:
                    return {
                        'success': True,
                        'fill_count': fill_count,
                        'order_id': order.get('order_id'),
                        'fill_price': order.get('yes_price') if side == 'yes' else order.get('no_price'),
                        'status': status
                    }

                return {
                    'success': False,
                    'fill_count': fill_count,
                    'order_id': order.get('order_id'),
                    'status': status,
                    'error': data.get('error', {}).get('message', f'Status: {status}')
                }

        except Exception as e:
            print(f"   [!] Order error: {e}")
            return {'success': False, 'error': str(e)}

    async def cancel_order(self, session, order_id: str) -> bool:
        if not order_id:
            return False
        path = f'/trade-api/v2/portfolio/orders/{order_id}'
        try:
            async with session.delete(
                f'{self.BASE_URL}{path}',
                headers=self._headers('DELETE', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status in [200, 204]:
                    print(f"   [CANCEL] Order {order_id[:8]}... cancelled")
                    return True
                else:
                    data = await r.json()
                    error_msg = data.get('error', {}).get('message', str(data))
                    if 'not found' in error_msg.lower() or 'already' in error_msg.lower():
                        print(f"   [CANCEL] Order {order_id[:8]}... already gone")
                        return True
                    print(f"   [!] Cancel failed: {error_msg}")
                    return False
        except Exception as e:
            print(f"   [!] Cancel error: {e}")
            return False

    async def get_open_orders(self, session, ticker: str = None) -> List[Dict]:
        path = '/trade-api/v2/portfolio/orders?status=resting'
        if ticker:
            path += f'&ticker={ticker}'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    orders = data.get('orders', [])
                    return [{
                        'order_id': o.get('order_id'),
                        'ticker': o.get('ticker'),
                        'action': o.get('action'),
                        'side': o.get('side'),
                        'count': o.get('remaining_count', o.get('count', 0)),
                        'price': o.get('yes_price') or o.get('no_price'),
                        'created_time': o.get('created_time')
                    } for o in orders]
                else:
                    print(f"   [!] Get orders failed: HTTP {r.status}")
        except Exception as e:
            print(f"   [!] Get orders error: {e}")
        return []

    async def cancel_all_orders_for_ticker(self, session, ticker: str) -> int:
        cancelled = 0
        for attempt in range(3):
            orders = await self.get_open_orders(session, ticker)
            if not orders:
                if attempt == 0:
                    print(f"   [CLEANUP] No open orders for {ticker}")
                break
            print(f"   [CLEANUP] Found {len(orders)} open orders for {ticker}, cancelling...")
            for order in orders:
                order_id = order.get('order_id')
                if order_id:
                    success = await self.cancel_order(session, order_id)
                    if success:
                        cancelled += 1
                    await asyncio.sleep(0.05)
            await asyncio.sleep(0.2)
        if cancelled > 0:
            print(f"   [CLEANUP] Cancelled {cancelled} orders for {ticker}")
        return cancelled

    async def cancel_all_open_orders(self, session) -> int:
        cancelled = 0
        orders = await self.get_open_orders(session)
        if not orders:
            print("[CLEANUP] No open Kalshi orders found")
            return 0
        print(f"[CLEANUP] Found {len(orders)} total open Kalshi orders, cancelling all...")
        for order in orders:
            order_id = order.get('order_id')
            ticker = order.get('ticker', 'unknown')
            if order_id:
                print(f"   [CANCEL] {ticker}: order {order_id[:8]}...")
                success = await self.cancel_order(session, order_id)
                if success:
                    cancelled += 1
                await asyncio.sleep(0.05)
        print(f"[CLEANUP] Cancelled {cancelled} Kalshi orders total")
        return cancelled


class PolymarketUSAPI:
    """Polymarket US API client with Ed25519 authentication"""
    BASE_URL = 'https://api.polymarket.us'

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        secret_bytes = base64.b64decode(secret_key)
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_bytes[:32])

    def _sign(self, ts: str, method: str, path: str) -> str:
        """Sign: message = timestamp + method + path (no query params)"""
        message = f'{ts}{method}{path}'.encode('utf-8')
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode('utf-8')

    def _headers(self, method: str, path: str) -> Dict:
        ts = str(int(time.time() * 1000))
        return {
            'X-PM-Access-Key': self.api_key,
            'X-PM-Timestamp': ts,
            'X-PM-Signature': self._sign(ts, method, path),
            'Content-Type': 'application/json'
        }

    async def get_balance(self, session, debug: bool = False) -> Optional[float]:
        """Get USD balance"""
        path = '/v1/account/balances'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    if debug:
                        print(f"[DEBUG PM US] Raw balance response: {json.dumps(data)[:500]}")
                    for b in data.get('balances', []):
                        if b.get('currency') == 'USD':
                            buying_power = b.get('buyingPower')
                            current_balance = b.get('currentBalance')
                            if debug:
                                print(f"[DEBUG PM US] buyingPower={buying_power}, currentBalance={current_balance}")
                            return float(buying_power if buying_power is not None else current_balance or 0)
                else:
                    body = await r.text()
                    print(f"   [!] PM US balance HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US balance error: {e}")
        return None

    async def get_positions(self, session, market_slug: str = None) -> Dict:
        """Get portfolio positions"""
        path = '/v1/portfolio/positions'
        query = f'?market={market_slug}' if market_slug else ''
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('positions', {})
                else:
                    body = await r.text()
                    print(f"   [!] PM US positions HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US positions error: {e}")
        return {}

    async def get_moneyline_markets(self, session, debug: bool = False) -> List[Dict]:
        """Fetch all active markets (filter for sports in code)"""
        path = '/v1/markets'
        # Note: sportsMarketTypes filter doesn't work, fetch all and filter in code
        query = '?active=true&closed=false&limit=200'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    markets = data.get('markets', [])
                    if debug and markets:
                        print(f"\n[DEBUG PM US] Raw API returned {len(markets)} markets")
                        # Show first 3 markets as sample
                        for i, m in enumerate(markets[:3]):
                            print(f"[DEBUG PM US] Sample {i+1}:")
                            print(f"  slug: {m.get('slug')}")
                            print(f"  outcomes: {m.get('outcomes')}")
                            print(f"  outcomePrices: {m.get('outcomePrices')} (NOTE: this is last/mid price, NOT order book)")
                            print(f"  gameStartTime: {m.get('gameStartTime')}")
                    return markets
                else:
                    body = await r.text()
                    print(f"   [!] PM US markets HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US markets error: {e}")
        return []

    async def get_all_markets_including_pending(self, session, debug: bool = False) -> List[Dict]:
        """Fetch ALL markets including PENDING ones (closed=false only, no active filter)"""
        path = '/v1/markets'
        query = '?closed=false&limit=500'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    markets = data.get('markets', [])
                    if debug:
                        active = [m for m in markets if m.get('active')]
                        pending = [m for m in markets if not m.get('active')]
                        print(f"[DEBUG PM US] All markets: {len(markets)} (active: {len(active)}, pending: {len(pending)})")
                    return markets
                else:
                    body = await r.text()
                    print(f"   [!] PM US all markets HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US all markets error: {e}")
        return []

    async def get_orderbook(self, session, market_slug: str, debug: bool = False) -> Optional[Dict]:
        """
        Fetch order book for a market.
        Returns: {
            'bids': [{'price': float, 'size': int}, ...],  # sorted high to low
            'asks': [{'price': float, 'size': int}, ...],  # sorted low to high
            'best_bid': float or None,
            'best_ask': float or None,
            'bid_size': int,
            'ask_size': int
        }
        """
        # Try different possible endpoint patterns
        endpoints_to_try = [
            f'/v1/markets/{market_slug}/orderbook',
            f'/v1/orderbook/{market_slug}',
            f'/v1/markets/{market_slug}/book',
        ]

        for endpoint in endpoints_to_try:
            path = endpoint
            try:
                async with session.get(
                    f'{self.BASE_URL}{path}',
                    headers=self._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        if debug:
                            print(f"[DEBUG PM US] Orderbook for {market_slug}: {json.dumps(data)[:500]}")

                        # PM US API returns: {"marketData": {"bids": [...], "offers": [...]}}
                        # Each order: {"px": {"value": "0.55", "currency": "USD"}, "qty": "100.000"}
                        market_data = data.get('marketData', data)
                        raw_bids = market_data.get('bids', [])
                        raw_offers = market_data.get('offers', market_data.get('asks', []))

                        def parse_pm_orders(orders):
                            """Parse PM US order format: {px: {value: "0.55"}, qty: "100"}"""
                            result = []
                            for o in orders:
                                if not isinstance(o, dict):
                                    continue
                                try:
                                    # Handle PM US nested format: px.value
                                    px = o.get('px', {})
                                    if isinstance(px, dict):
                                        price = float(px.get('value', 0))
                                    else:
                                        # Fallback: direct price field
                                        price = float(o.get('price', o.get('p', px or 0)))

                                    # Handle qty as string
                                    qty = o.get('qty', o.get('size', o.get('quantity', 0)))
                                    size = int(float(qty)) if qty else 0

                                    if price > 0 and size > 0:
                                        result.append({'price': price, 'size': size})
                                except (ValueError, TypeError, AttributeError):
                                    continue
                            return result

                        bids = parse_pm_orders(raw_bids)
                        asks = parse_pm_orders(raw_offers)

                        # Sort: bids high to low, asks low to high
                        bids.sort(key=lambda x: -x['price'])
                        asks.sort(key=lambda x: x['price'])

                        best_bid = bids[0]['price'] if bids else None
                        best_ask = asks[0]['price'] if asks else None
                        bid_size = bids[0]['size'] if bids else 0
                        ask_size = asks[0]['size'] if asks else 0

                        if debug:
                            print(f"[DEBUG PM US] Parsed: best_bid={best_bid}, best_ask={best_ask}, "
                                  f"bid_size={bid_size}, ask_size={ask_size}")

                        return {
                            'bids': bids,
                            'asks': asks,
                            'best_bid': best_bid,
                            'best_ask': best_ask,
                            'bid_size': bid_size,
                            'ask_size': ask_size
                        }
                    elif r.status == 404:
                        # Try next endpoint
                        continue
                    else:
                        if debug:
                            body = await r.text()
                            print(f"[DEBUG PM US] Orderbook {path} HTTP {r.status}: {body[:200]}")
            except Exception as e:
                if debug:
                    print(f"[DEBUG PM US] Orderbook {path} error: {e}")
                continue

        return None

    async def get_orderbooks_batch(self, session, slugs: List[str], debug: bool = False) -> Dict[str, Dict]:
        """Fetch order books for multiple markets in parallel"""
        if not slugs:
            return {}

        tasks = [self.get_orderbook(session, slug, debug=(debug and i < 2)) for i, slug in enumerate(slugs)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        orderbooks = {}
        for slug, result in zip(slugs, results):
            if isinstance(result, dict):
                orderbooks[slug] = result
            # Skip exceptions silently

        return orderbooks

    async def place_order(self, session, market_slug: str, intent: int,
                          price: float, quantity: int, tif: int = 3,
                          sync: bool = True) -> Dict:
        """
        Place order on PM US.
        intent: 1=BUY_YES, 2=SELL_YES, 3=BUY_NO, 4=SELL_NO
        tif: 1=GTC, 2=GTD, 3=IOC, 4=FOK
        price: in dollars (e.g., 0.55)
        """
        paper_unlimited = EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS

        # In paper unlimited mode, skip all limits
        if not paper_unlimited:
            # HARD LIMIT ENFORCEMENT (live mode only)
            if quantity > MAX_CONTRACTS:
                print(f"   [SAFETY] PM US: Capping contracts from {quantity} to {MAX_CONTRACTS}")
                quantity = MAX_CONTRACTS
            if quantity < MIN_CONTRACTS:
                return {'success': False, 'error': f'Quantity {quantity} below minimum'}

            max_cost_dollars = price * quantity
            if max_cost_dollars * 100 > MAX_COST_CENTS:
                quantity = int(MAX_COST_CENTS / (price * 100))
                if quantity < MIN_CONTRACTS:
                    return {'success': False, 'error': 'Quantity below minimum after cost cap'}
                print(f"   [SAFETY] PM US: Reduced to {quantity} contracts")

        intent_names = {1: 'BUY_YES', 2: 'SELL_YES', 3: 'BUY_NO', 4: 'SELL_NO'}

        if EXECUTION_MODE == ExecutionMode.PAPER:
            print(f"   [PAPER] PM US: {intent_names[intent]} {quantity} @ ${price:.2f} on {market_slug}")
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'fill_count': quantity,
                'fill_price': price,
                'order_id': f'PM-PAPER-{int(time.time()*1000)}',
                'paper': True
            }

        path = '/v1/orders'
        payload = {
            'market_slug': market_slug,
            'intent': intent,
            'type': 1,  # LIMIT
            'price': {'value': f'{price:.2f}', 'currency': 'USD'},
            'quantity': quantity,
            'tif': tif,
            'manualOrderIndicator': 2,  # AUTOMATIC
            'synchronousExecution': sync,
        }

        try:
            print(f"   [PM ORDER] {intent_names[intent]} {quantity} @ ${price:.2f} on {market_slug}")
            print(f"   [DEBUG] PM Payload: {json.dumps(payload)}")

            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json()
                print(f"   [DEBUG] PM HTTP Status: {r.status}")
                print(f"   [DEBUG] PM Response: {data}")

                if r.status == 200:
                    order_id = data.get('id')
                    executions = data.get('executions', [])

                    # Sum fills from executions
                    total_filled = 0
                    fill_price = None
                    for ex in executions:
                        ex_type = ex.get('type')
                        # 1=PARTIAL_FILL, 2=FILL
                        if ex_type in [1, 2]:
                            total_filled += ex.get('lastShares', 0)
                            last_px = ex.get('lastPx', {})
                            if last_px:
                                fill_price = float(last_px.get('value', 0))

                    return {
                        'success': total_filled > 0,
                        'fill_count': total_filled,
                        'order_id': order_id,
                        'fill_price': fill_price,
                        'executions': executions
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {r.status}: {json.dumps(data)[:200]}'
                    }
        except Exception as e:
            print(f"   [!] PM US order error: {e}")
            return {'success': False, 'error': str(e)}

    async def cancel_order(self, session, order_id: str, market_slug: str) -> bool:
        """Cancel a specific order"""
        path = f'/v1/order/{order_id}/cancel'
        try:
            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json={'market_slug': market_slug},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    print(f"   [PM CANCEL] Order {order_id[:12]}... cancelled")
                    return True
                else:
                    body = await r.text()
                    print(f"   [!] PM cancel failed: HTTP {r.status}: {body[:200]}")
                    return False
        except Exception as e:
            print(f"   [!] PM cancel error: {e}")
            return False

    async def cancel_all_orders(self, session, slugs: List[str] = None) -> List[str]:
        """Cancel all open orders, optionally filtered by market slugs"""
        path = '/v1/orders/open/cancel'
        try:
            payload = {'slugs': slugs or []}
            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    cancelled = data.get('canceledOrderIds', [])
                    if cancelled:
                        print(f"[CLEANUP] Cancelled {len(cancelled)} PM US orders")
                    return cancelled
                else:
                    body = await r.text()
                    print(f"   [!] PM cancel all failed: HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US cancel all error: {e}")
        return []

    async def get_open_orders(self, session, slugs: List[str] = None) -> List[Dict]:
        """Get all open orders"""
        path = '/v1/orders/open'
        query = ''
        if slugs:
            query = '?' + '&'.join(f'slugs={s}' for s in slugs)
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('orders', [])
        except Exception as e:
            print(f"   [!] PM US open orders error: {e}")
        return []


def get_pm_execution_params(arb: ArbOpportunity) -> tuple:
    """
    Determine PM US order intent and price for the given arb.

    For BUY_PM_SELL_K: go long on PM for this team.
    For BUY_K_SELL_PM: short this team on PM by buying the opposite outcome.

    Returns (intent, price_dollars)
    """
    if arb.direction == 'BUY_PM_SELL_K':
        # Buy this team on PM
        if arb.pm_outcome_index == 0:
            intent = PM_BUY_YES
        else:
            intent = PM_BUY_NO
        price = arb.pm_ask / 100  # Cost to buy in dollars
    else:
        # BUY_K_SELL_PM: short this team by buying the opposite outcome
        if arb.pm_outcome_index == 0:
            intent = PM_BUY_NO   # Buy opposite (outcome[1])
        else:
            intent = PM_BUY_YES  # Buy opposite (outcome[0])
        # Cost of opposite = (100 - team_price) / 100
        price = (100 - arb.pm_bid) / 100

    return intent, price


# ============================================================================
# HEDGE PROTECTION FUNCTIONS
# ============================================================================

async def fetch_fresh_prices(session, kalshi_api, pm_api, kalshi_ticker: str, pm_slug: str) -> Dict:
    """
    Fetch fresh prices from both platforms simultaneously.
    Returns dict with kalshi_bid, kalshi_ask, pm_bid, pm_ask, timestamp, is_fresh
    """
    start_time = time.time()

    async def get_kalshi_price():
        try:
            path = f'/trade-api/v2/markets/{kalshi_ticker}'
            async with session.get(
                f'{kalshi_api.BASE_URL}{path}',
                headers=kalshi_api._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=2)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    market = data.get('market', {})
                    return {
                        'bid': market.get('yes_bid', 0),
                        'ask': market.get('yes_ask', 100),
                        'success': True
                    }
        except Exception as e:
            print(f"[VALIDATE] Kalshi price fetch failed: {e}")
        return {'bid': 0, 'ask': 100, 'success': False}

    async def get_pm_price():
        try:
            orderbook = await pm_api.get_orderbook(session, pm_slug, debug=False)
            if orderbook:
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                best_bid = bids[0]['price'] * 100 if bids else 0
                best_ask = asks[0]['price'] * 100 if asks else 100
                bid_size = bids[0]['size'] if bids else 0
                ask_size = asks[0]['size'] if asks else 0
                return {
                    'bid': best_bid,
                    'ask': best_ask,
                    'bid_size': bid_size,
                    'ask_size': ask_size,
                    'success': True
                }
        except Exception as e:
            print(f"[VALIDATE] PM price fetch failed: {e}")
        return {'bid': 0, 'ask': 100, 'bid_size': 0, 'ask_size': 0, 'success': False}

    # Fetch both prices in parallel
    k_result, pm_result = await asyncio.gather(get_kalshi_price(), get_pm_price())

    elapsed_ms = (time.time() - start_time) * 1000
    is_fresh = elapsed_ms < MAX_PRICE_STALENESS_MS

    return {
        'kalshi_bid': k_result['bid'],
        'kalshi_ask': k_result['ask'],
        'pm_bid': pm_result['bid'],
        'pm_ask': pm_result['ask'],
        'pm_bid_size': pm_result.get('bid_size', 0),
        'pm_ask_size': pm_result.get('ask_size', 0),
        'timestamp': time.time(),
        'fetch_time_ms': elapsed_ms,
        'is_fresh': is_fresh,
        'kalshi_success': k_result['success'],
        'pm_success': pm_result['success']
    }


async def validate_pre_trade(session, kalshi_api, pm_api, arb: 'ArbOpportunity') -> Tuple[bool, str, Dict]:
    """
    Pre-trade validation: fetch fresh prices and verify spread still exists.
    Returns (is_valid, reason, fresh_prices)
    """
    print(f"\n[VALIDATE] Fetching fresh prices...")

    fresh = await fetch_fresh_prices(session, kalshi_api, pm_api, arb.kalshi_ticker, arb.pm_slug)

    # Check if we got valid prices
    if not fresh['kalshi_success'] or not fresh['pm_success']:
        return False, "Failed to fetch fresh prices", fresh

    # Check freshness
    if not fresh['is_fresh']:
        return False, f"Prices stale ({fresh['fetch_time_ms']:.0f}ms > {MAX_PRICE_STALENESS_MS}ms)", fresh

    # Calculate fresh spread
    if arb.direction == 'BUY_PM_SELL_K':
        # Buy on PM (pay ask), Sell on Kalshi (get bid)
        fresh_spread = fresh['kalshi_bid'] - fresh['pm_ask']
        available_size = fresh['pm_ask_size']
    else:
        # Buy on Kalshi (pay ask), Sell on PM (get bid)
        fresh_spread = fresh['pm_bid'] - fresh['kalshi_ask']
        available_size = fresh['pm_bid_size']

    print(f"[VALIDATE] Fresh prices: K={fresh['kalshi_bid']}/{fresh['kalshi_ask']}c, PM={fresh['pm_bid']:.0f}/{fresh['pm_ask']:.0f}c")
    print(f"[VALIDATE] Fresh spread={fresh_spread}c, liquidity={available_size}")

    # Verify spread still exists
    if fresh_spread < MIN_HEDGE_SPREAD_CENTS:
        return False, f"Spread gone ({fresh_spread}c < {MIN_HEDGE_SPREAD_CENTS}c)", fresh

    # Verify liquidity
    if available_size < arb.size:
        return False, f"Insufficient liquidity ({available_size} < {arb.size})", fresh

    print(f"[VALIDATE] Pre-trade validation PASSED ✓")
    return True, "OK", fresh


async def execute_parallel_orders(
    session, kalshi_api, pm_api, arb: 'ArbOpportunity',
    kalshi_price: int, pm_price: float, quantity: int
) -> Tuple[Dict, Dict]:
    """
    Execute orders on both platforms simultaneously.
    Returns (kalshi_result, pm_result)
    """
    print(f"\n[EXECUTE] Sending parallel orders...")
    start_time = time.time()

    # Determine Kalshi action
    k_action = 'buy' if arb.direction == 'BUY_K_SELL_PM' else 'sell'

    # Determine PM intent
    pm_intent, _ = get_pm_execution_params(arb)

    async def execute_kalshi():
        try:
            result = await kalshi_api.place_order(
                session, arb.kalshi_ticker, 'yes', k_action, quantity, kalshi_price
            )
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'fill_count': 0}

    async def execute_pm():
        try:
            result = await pm_api.place_order(
                session, arb.pm_slug, pm_intent, pm_price, quantity, tif=3, sync=True
            )
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'fill_count': 0}

    # Execute both orders simultaneously
    kalshi_result, pm_result = await asyncio.gather(execute_kalshi(), execute_pm())

    elapsed_ms = (time.time() - start_time) * 1000
    print(f"[EXECUTE] Both orders submitted in {elapsed_ms:.0f}ms")

    return kalshi_result, pm_result


async def attempt_hedge_recovery(
    session, pm_api, arb: 'ArbOpportunity',
    unhedged_qty: int, original_pm_price: float, hedge_state: HedgeState
) -> bool:
    """
    Attempt to complete hedge with slippage.
    Returns True if hedge completed, False otherwise.
    """
    print(f"\n[RECOVERY] Attempting to hedge {unhedged_qty} contracts...")
    hedge_state.recovery_attempted = True

    pm_intent, _ = get_pm_execution_params(arb)

    for slippage in SLIPPAGE_RECOVERY_LEVELS:
        # Adjust price with slippage (pay more to buy, accept less to sell)
        if pm_intent in [1, 3]:  # BUY_YES or BUY_NO
            try_price = original_pm_price + (slippage / 100)
        else:  # SELL
            try_price = original_pm_price - (slippage / 100)

        try_price = max(0.01, min(0.99, try_price))  # Clamp to valid range

        print(f"[RECOVERY] Trying PM at ${try_price:.2f} (slippage: {slippage}c)...")

        try:
            result = await pm_api.place_order(
                session, arb.pm_slug, pm_intent, try_price, unhedged_qty, tif=3, sync=True
            )

            fill_count = result.get('fill_count', 0)

            if fill_count >= unhedged_qty:
                hedge_state.pm_filled += fill_count
                hedge_state.recovery_slippage = slippage
                print(f"[RECOVERY] SUCCESS! Filled {fill_count} @ ${try_price:.2f} ✓")
                return True
            elif fill_count > 0:
                hedge_state.pm_filled += fill_count
                unhedged_qty -= fill_count
                print(f"[RECOVERY] Partial: {fill_count} filled, {unhedged_qty} remaining")
        except Exception as e:
            print(f"[RECOVERY] Error at {slippage}c slippage: {e}")

        await asyncio.sleep(0.1)  # Brief pause between attempts

    print(f"[RECOVERY] FAILED - {unhedged_qty} contracts still unhedged")
    return False


async def reconcile_hedge(
    session, kalshi_api, pm_api, arb: 'ArbOpportunity',
    kalshi_result: Dict, pm_result: Dict, target_qty: int
) -> HedgeState:
    """
    Post-trade reconciliation: verify fills match, attempt recovery if needed.
    """
    hedge_state = HedgeState(
        kalshi_ticker=arb.kalshi_ticker,
        pm_slug=arb.pm_slug,
        target_qty=target_qty,
        kalshi_filled=kalshi_result.get('fill_count', 0),
        pm_filled=pm_result.get('fill_count', 0),
        kalshi_price=kalshi_result.get('fill_price', 0),
        pm_price=pm_result.get('fill_price', 0)
    )

    print(f"\n[HEDGE CHECK] Kalshi={hedge_state.kalshi_filled}, PM={hedge_state.pm_filled}")

    # Check if perfectly hedged
    if hedge_state.kalshi_filled == hedge_state.pm_filled:
        hedge_state.is_hedged = True
        print(f"[HEDGE CHECK] MATCHED ✓")
        return hedge_state

    # Calculate unhedged quantity
    if hedge_state.kalshi_filled > hedge_state.pm_filled:
        unhedged_qty = hedge_state.kalshi_filled - hedge_state.pm_filled
        print(f"[!!! UNHEDGED !!!] {unhedged_qty} contracts on Kalshi")

        # Attempt recovery
        pm_intent, pm_price = get_pm_execution_params(arb)
        recovery_success = await attempt_hedge_recovery(
            session, pm_api, arb, unhedged_qty, pm_price, hedge_state
        )

        if recovery_success:
            hedge_state.is_hedged = True
            print(f"[HEDGE CHECK] RECOVERED ✓ (with {hedge_state.recovery_slippage}c slippage)")
        else:
            # Save unhedged position for manual intervention
            save_unhedged_position(hedge_state, "PM recovery failed")

            # Calculate exposure
            exposure_cents = unhedged_qty * hedge_state.kalshi_price
            print(f"[!!! EXPOSURE !!!] ${exposure_cents/100:.2f} unhedged")

            if exposure_cents > UNHEDGED_EXPOSURE_LIMIT:
                activate_kill_switch(f"Unhedged exposure ${exposure_cents/100:.2f} > ${UNHEDGED_EXPOSURE_LIMIT/100:.2f} limit")

    elif hedge_state.pm_filled > hedge_state.kalshi_filled:
        # PM filled more than Kalshi (unusual but possible)
        unhedged_qty = hedge_state.pm_filled - hedge_state.kalshi_filled
        print(f"[!!! UNHEDGED !!!] {unhedged_qty} contracts on PM (Kalshi underfilled)")
        save_unhedged_position(hedge_state, "Kalshi underfilled")

    return hedge_state


async def sync_positions(session, kalshi_api, pm_api) -> PositionState:
    """
    Sync position state with both platforms.
    """
    global POSITION_STATE

    print("[POSITIONS] Syncing positions with platforms...")

    # Fetch Kalshi positions
    try:
        k_positions = await kalshi_api.get_positions(session)
        POSITION_STATE.kalshi_positions = {
            ticker: pos.position for ticker, pos in k_positions.items()
        } if k_positions else {}
    except Exception as e:
        print(f"[POSITIONS] Kalshi sync error: {e}")

    # Fetch PM positions
    try:
        pm_positions = await pm_api.get_positions(session)
        if pm_positions and 'positions' in pm_positions:
            POSITION_STATE.pm_positions = {
                p.get('market', {}).get('slug', ''): p.get('quantity', 0)
                for p in pm_positions.get('positions', [])
            }
    except Exception as e:
        print(f"[POSITIONS] PM sync error: {e}")

    POSITION_STATE.last_sync = time.time()

    k_count = len(POSITION_STATE.kalshi_positions)
    pm_count = len(POSITION_STATE.pm_positions)
    print(f"[POSITIONS] Synced: Kalshi={k_count}, PM={pm_count}")

    return POSITION_STATE


async def check_position_mismatch(session, kalshi_api, pm_api) -> List[Dict]:
    """
    Check for mismatches between expected and actual positions.
    Returns list of mismatches.
    """
    await sync_positions(session, kalshi_api, pm_api)

    mismatches = []

    # Compare Kalshi expected vs actual
    for ticker, expected in POSITION_STATE.expected_kalshi.items():
        actual = POSITION_STATE.kalshi_positions.get(ticker, 0)
        if expected != actual:
            mismatches.append({
                'platform': 'kalshi',
                'ticker': ticker,
                'expected': expected,
                'actual': actual,
                'diff': actual - expected
            })

    # Compare PM expected vs actual
    for slug, expected in POSITION_STATE.expected_pm.items():
        actual = POSITION_STATE.pm_positions.get(slug, 0)
        if expected != actual:
            mismatches.append({
                'platform': 'pm',
                'slug': slug,
                'expected': expected,
                'actual': actual,
                'diff': actual - expected
            })

    if mismatches:
        print(f"\n[!!! POSITION MISMATCH !!!]")
        for m in mismatches:
            print(f"  {m['platform']}: expected={m['expected']}, actual={m['actual']}, diff={m['diff']}")

    return mismatches


async def run_recovery_mode(session, kalshi_api, pm_api):
    """
    Recovery mode: show positions and offer recovery options.
    """
    print("\n" + "="*60)
    print("[RECOVERY MODE]")
    print("="*60)

    # Sync positions
    await sync_positions(session, kalshi_api, pm_api)

    # Show current positions
    print("\n[KALSHI POSITIONS]")
    if POSITION_STATE.kalshi_positions:
        for ticker, qty in POSITION_STATE.kalshi_positions.items():
            print(f"  {ticker}: {qty} contracts")
    else:
        print("  (none)")

    print("\n[PM US POSITIONS]")
    if POSITION_STATE.pm_positions:
        for slug, qty in POSITION_STATE.pm_positions.items():
            if qty != 0:
                print(f"  {slug}: {qty} contracts")
    else:
        print("  (none)")

    # Show unhedged positions from file
    unhedged = load_unhedged_positions()
    if unhedged:
        print(f"\n[UNHEDGED POSITIONS FROM FILE]")
        for u in unhedged:
            print(f"  {u['timestamp']}: K={u['kalshi_ticker']}, unhedged={u['unhedged_qty']}")
            print(f"    Reason: {u['reason']}")

    print("\n[RECOVERY OPTIONS]")
    print("  1. Close Kalshi positions manually")
    print("  2. Complete hedge on PM at market price")
    print("  3. Exit recovery mode")
    print("\nReview positions above and take manual action if needed.")
    print("Use --force to restart trading after recovery.")
    print("="*60 + "\n")


# ============================================================================
# PREFLIGHT CHECK SYSTEM
# ============================================================================
@dataclass
class PreflightResult:
    """Result of a single preflight check"""
    name: str
    passed: bool
    blocking: bool  # If True, failure blocks live trading
    message: str
    details: Optional[str] = None

async def run_preflight_checks(session, kalshi_api, pm_api) -> Tuple[bool, List[PreflightResult]]:
    """
    Run comprehensive preflight checks before live trading.
    Returns (all_passed, list_of_results)
    """
    results: List[PreflightResult] = []

    print("\n" + "="*70)
    print("PREFLIGHT CHECKS - Validating system readiness")
    print("="*70 + "\n")

    # =========================================================================
    # 1. API CREDENTIALS - Test authentication
    # =========================================================================
    print("[1/6] API CREDENTIALS")

    # Test Kalshi auth
    kalshi_auth_ok = False
    kalshi_auth_msg = ""
    try:
        start_time = time.time()
        balance = await kalshi_api.get_balance(session)
        latency = (time.time() - start_time) * 1000
        if balance is not None:
            kalshi_auth_ok = True
            kalshi_auth_msg = f"Authenticated ({latency:.0f}ms)"
        else:
            kalshi_auth_msg = "Failed to get balance"
    except Exception as e:
        kalshi_auth_msg = f"Auth error: {str(e)[:50]}"

    results.append(PreflightResult(
        name="Kalshi API Auth",
        passed=kalshi_auth_ok,
        blocking=True,
        message=kalshi_auth_msg
    ))
    print(f"  {'[PASS]' if kalshi_auth_ok else '[FAIL]'} Kalshi: {kalshi_auth_msg}")

    # Test PM US auth
    pm_auth_ok = False
    pm_auth_msg = ""
    try:
        start_time = time.time()
        balance = await pm_api.get_balance(session)
        latency = (time.time() - start_time) * 1000
        if balance is not None:
            pm_auth_ok = True
            pm_auth_msg = f"Authenticated ({latency:.0f}ms)"
        else:
            pm_auth_msg = "Failed to get balance"
    except Exception as e:
        pm_auth_msg = f"Auth error: {str(e)[:50]}"

    results.append(PreflightResult(
        name="PM US API Auth",
        passed=pm_auth_ok,
        blocking=True,
        message=pm_auth_msg
    ))
    print(f"  {'[PASS]' if pm_auth_ok else '[FAIL]'} PM US:  {pm_auth_msg}")

    # =========================================================================
    # 2. ACCOUNT BALANCES - Verify sufficient funds
    # =========================================================================
    print("\n[2/6] ACCOUNT BALANCES")

    MIN_KALSHI_BALANCE = 50.0   # $50 minimum
    MIN_PM_BALANCE = 50.0       # $50 minimum

    # Kalshi balance
    kalshi_balance = None
    kalshi_bal_ok = False
    if kalshi_auth_ok:
        try:
            kalshi_balance = await kalshi_api.get_balance(session)
            if kalshi_balance is not None:
                kalshi_bal_ok = kalshi_balance >= MIN_KALSHI_BALANCE
        except:
            pass

    kalshi_bal_msg = f"${kalshi_balance:.2f}" if kalshi_balance is not None else "Unable to fetch"
    if kalshi_balance is not None and kalshi_balance < MIN_KALSHI_BALANCE:
        kalshi_bal_msg += f" (min ${MIN_KALSHI_BALANCE:.0f} required)"

    results.append(PreflightResult(
        name="Kalshi Balance",
        passed=kalshi_bal_ok,
        blocking=True,
        message=kalshi_bal_msg
    ))
    print(f"  {'[PASS]' if kalshi_bal_ok else '[FAIL]'} Kalshi: {kalshi_bal_msg}")

    # PM US balance
    pm_balance = None
    pm_bal_ok = False
    if pm_auth_ok:
        try:
            pm_balance = await pm_api.get_balance(session)
            if pm_balance is not None:
                pm_bal_ok = pm_balance >= MIN_PM_BALANCE
        except:
            pass

    pm_bal_msg = f"${pm_balance:.2f}" if pm_balance is not None else "Unable to fetch"
    if pm_balance is not None and pm_balance < MIN_PM_BALANCE:
        pm_bal_msg += f" (min ${MIN_PM_BALANCE:.0f} required)"

    results.append(PreflightResult(
        name="PM US Balance",
        passed=pm_bal_ok,
        blocking=True,
        message=pm_bal_msg
    ))
    print(f"  {'[PASS]' if pm_bal_ok else '[FAIL]'} PM US:  {pm_bal_msg}")

    # =========================================================================
    # 3. EXISTING POSITIONS - Check for open/unhedged positions
    # =========================================================================
    print("\n[3/6] EXISTING POSITIONS")

    # Check for unhedged positions from file
    unhedged = load_unhedged_positions()
    unhedged_ok = len(unhedged) == 0
    unhedged_msg = "No unhedged positions" if unhedged_ok else f"{len(unhedged)} unhedged position(s) detected!"

    results.append(PreflightResult(
        name="Unhedged Positions",
        passed=unhedged_ok,
        blocking=True,
        message=unhedged_msg,
        details=f"Run --recover to review" if not unhedged_ok else None
    ))
    print(f"  {'[PASS]' if unhedged_ok else '[FAIL]'} Unhedged: {unhedged_msg}")

    # Check for open Kalshi positions
    kalshi_positions = {}
    if kalshi_auth_ok:
        try:
            kalshi_positions = await kalshi_api.get_positions(session)
        except:
            pass

    kalshi_pos_ok = True  # Open positions are OK, just informational
    kalshi_pos_msg = f"{len(kalshi_positions)} open position(s)" if kalshi_positions else "No open positions"

    results.append(PreflightResult(
        name="Kalshi Positions",
        passed=kalshi_pos_ok,
        blocking=False,  # Open positions are not blocking
        message=kalshi_pos_msg
    ))
    print(f"  [INFO] Kalshi: {kalshi_pos_msg}")

    # Check for open PM US positions
    pm_positions = {}
    if pm_auth_ok:
        try:
            pm_positions = await pm_api.get_positions(session)
        except:
            pass

    pm_pos_msg = f"{len([p for p in pm_positions.values() if p])} open position(s)" if pm_positions else "No open positions"

    results.append(PreflightResult(
        name="PM US Positions",
        passed=True,  # Informational only
        blocking=False,
        message=pm_pos_msg
    ))
    print(f"  [INFO] PM US:  {pm_pos_msg}")

    # Check kill switch
    kill_switch_ok = not HEDGE_KILL_SWITCH_ACTIVE
    kill_msg = "Active - trading blocked!" if HEDGE_KILL_SWITCH_ACTIVE else "Inactive"

    results.append(PreflightResult(
        name="Kill Switch",
        passed=kill_switch_ok,
        blocking=True,
        message=kill_msg,
        details="Use --force to override" if not kill_switch_ok else None
    ))
    print(f"  {'[PASS]' if kill_switch_ok else '[FAIL]'} Kill Switch: {kill_msg}")

    # =========================================================================
    # 4. MARKET CONNECTIVITY - Test API latency and data fetching
    # =========================================================================
    print("\n[4/6] MARKET CONNECTIVITY")

    MAX_ACCEPTABLE_LATENCY_MS = 2000

    # Test Kalshi market fetch
    kalshi_latency_ok = False
    kalshi_market_count = 0
    kalshi_latency = 0
    if kalshi_auth_ok:
        try:
            start_time = time.time()
            # Fetch NBA markets as a test
            path = '/trade-api/v2/markets?series_ticker=KXNBAGAME&status=open&limit=10'
            async with session.get(
                f'{kalshi_api.BASE_URL}{path}',
                headers=kalshi_api._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    kalshi_market_count = len(data.get('markets', []))
                    kalshi_latency = (time.time() - start_time) * 1000
                    kalshi_latency_ok = kalshi_latency < MAX_ACCEPTABLE_LATENCY_MS
        except Exception as e:
            pass

    kalshi_conn_msg = f"{kalshi_market_count} markets in {kalshi_latency:.0f}ms" if kalshi_latency > 0 else "Failed to fetch"
    if kalshi_latency >= MAX_ACCEPTABLE_LATENCY_MS:
        kalshi_conn_msg += " (HIGH LATENCY!)"

    results.append(PreflightResult(
        name="Kalshi Markets",
        passed=kalshi_latency_ok and kalshi_market_count > 0,
        blocking=True,
        message=kalshi_conn_msg
    ))
    print(f"  {'[PASS]' if kalshi_latency_ok and kalshi_market_count > 0 else '[FAIL]'} Kalshi: {kalshi_conn_msg}")

    # Test PM US market fetch
    pm_latency_ok = False
    pm_market_count = 0
    pm_latency = 0
    if pm_auth_ok:
        try:
            start_time = time.time()
            markets = await pm_api.get_moneyline_markets(session)
            pm_market_count = len(markets)
            pm_latency = (time.time() - start_time) * 1000
            pm_latency_ok = pm_latency < MAX_ACCEPTABLE_LATENCY_MS
        except:
            pass

    pm_conn_msg = f"{pm_market_count} markets in {pm_latency:.0f}ms" if pm_latency > 0 else "Failed to fetch"
    if pm_latency >= MAX_ACCEPTABLE_LATENCY_MS:
        pm_conn_msg += " (HIGH LATENCY!)"

    results.append(PreflightResult(
        name="PM US Markets",
        passed=pm_latency_ok and pm_market_count >= 0,  # 0 markets OK outside game hours
        blocking=True,
        message=pm_conn_msg
    ))
    print(f"  {'[PASS]' if pm_latency_ok else '[FAIL]'} PM US:  {pm_conn_msg}")

    # Test order book fetch (if markets available)
    orderbook_ok = True
    orderbook_msg = "Skipped (no markets)"
    if pm_market_count > 0 and pm_auth_ok:
        try:
            # Get first market slug and test orderbook
            test_markets = await pm_api.get_moneyline_markets(session)
            if test_markets:
                test_slug = test_markets[0].get('slug')
                if test_slug:
                    start_time = time.time()
                    orderbook = await pm_api.get_orderbook(session, test_slug)
                    ob_latency = (time.time() - start_time) * 1000
                    if orderbook:
                        orderbook_ok = True
                        orderbook_msg = f"OK ({ob_latency:.0f}ms)"
                    else:
                        orderbook_ok = False
                        orderbook_msg = "Failed to fetch order book"
        except Exception as e:
            orderbook_ok = False
            orderbook_msg = f"Error: {str(e)[:30]}"

    results.append(PreflightResult(
        name="Order Book Access",
        passed=orderbook_ok,
        blocking=False,  # Might fail outside market hours
        message=orderbook_msg
    ))
    print(f"  {'[PASS]' if orderbook_ok else '[WARN]'} Orderbook: {orderbook_msg}")

    # =========================================================================
    # 5. CONFIGURATION - Validate all settings are sane
    # =========================================================================
    print("\n[5/6] CONFIGURATION")

    config_issues = []

    # Check trading limits
    if MAX_CONTRACTS <= 0 or MAX_CONTRACTS > 1000:
        config_issues.append(f"MAX_CONTRACTS={MAX_CONTRACTS} out of range")
    if MAX_COST_CENTS <= 0 or MAX_COST_CENTS > 100000:
        config_issues.append(f"MAX_COST_CENTS={MAX_COST_CENTS} out of range")
    if MIN_CONTRACTS < 1:
        config_issues.append(f"MIN_CONTRACTS={MIN_CONTRACTS} must be >= 1")
    if MIN_SPREAD_CENTS < 1 or MIN_SPREAD_CENTS > 50:
        config_issues.append(f"MIN_SPREAD_CENTS={MIN_SPREAD_CENTS} out of range")
    if COOLDOWN_SECONDS < 0 or COOLDOWN_SECONDS > 300:
        config_issues.append(f"COOLDOWN_SECONDS={COOLDOWN_SECONDS} out of range")

    # Check hedge protection settings
    if UNHEDGED_EXPOSURE_LIMIT <= 0:
        config_issues.append(f"UNHEDGED_EXPOSURE_LIMIT={UNHEDGED_EXPOSURE_LIMIT} must be > 0")
    if MAX_PRICE_STALENESS_MS < 50 or MAX_PRICE_STALENESS_MS > 5000:
        config_issues.append(f"MAX_PRICE_STALENESS_MS={MAX_PRICE_STALENESS_MS} out of range")

    config_ok = len(config_issues) == 0
    config_msg = "All settings valid" if config_ok else f"{len(config_issues)} issue(s)"

    results.append(PreflightResult(
        name="Trading Limits",
        passed=config_ok,
        blocking=True,
        message=config_msg,
        details="; ".join(config_issues) if config_issues else None
    ))
    print(f"  {'[PASS]' if config_ok else '[FAIL]'} Limits: {config_msg}")
    if config_issues:
        for issue in config_issues:
            print(f"         - {issue}")

    # Display current config
    print(f"  [INFO] Config: MAX_CONTRACTS={MAX_CONTRACTS}, MAX_COST=${MAX_COST_CENTS/100:.0f}, MIN_SPREAD={MIN_SPREAD_CENTS}c, COOLDOWN={COOLDOWN_SECONDS}s")

    # =========================================================================
    # 6. DATA FILES - Verify trade log, price history are writable
    # =========================================================================
    print("\n[6/6] DATA FILES")

    files_to_check = [
        ('trades.json', True),           # Blocking
        ('skipped_arbs.json', False),    # Non-blocking
        ('price_history.csv', False),    # Non-blocking
        (UNHEDGED_POSITIONS_FILE, True), # Blocking
    ]

    for filename, is_blocking in files_to_check:
        file_ok = False
        file_msg = ""
        try:
            # Try to open file for append (creates if not exists)
            with open(filename, 'a') as f:
                file_ok = True
                file_msg = "Writable"
        except PermissionError:
            file_msg = "Permission denied!"
        except Exception as e:
            file_msg = f"Error: {str(e)[:30]}"

        results.append(PreflightResult(
            name=f"File: {filename}",
            passed=file_ok,
            blocking=is_blocking,
            message=file_msg
        ))
        status = '[PASS]' if file_ok else ('[FAIL]' if is_blocking else '[WARN]')
        print(f"  {status} {filename}: {file_msg}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)

    blocking_failures = [r for r in results if not r.passed and r.blocking]
    warnings = [r for r in results if not r.passed and not r.blocking]

    all_blocking_passed = len(blocking_failures) == 0

    if all_blocking_passed:
        print("[PREFLIGHT PASSED] All critical checks passed")
        if warnings:
            print(f"  ({len(warnings)} non-blocking warning(s))")
    else:
        print("[PREFLIGHT FAILED] Critical issues must be resolved before live trading:")
        for failure in blocking_failures:
            print(f"  [BLOCKING] {failure.name}: {failure.message}")
            if failure.details:
                print(f"             {failure.details}")

    print("="*70 + "\n")

    return all_blocking_passed, results


def log_trade(arb: ArbOpportunity, k_result: Dict, pm_result: Dict, status: str):
    """Log trade details"""
    global TRADE_LOG

    # Determine display status
    if arb.needs_review:
        display_status = 'REVIEW'
    elif EXECUTION_MODE == ExecutionMode.PAPER:
        display_status = 'PAPER'
    else:
        display_status = status

    trade = {
        'timestamp': datetime.now().isoformat(),
        'sport': arb.sport,
        'game': arb.game,
        'team': arb.team,
        'direction': arb.direction,
        'intended_size': arb.size,
        'k_fill_count': k_result.get('fill_count', 0),
        'k_fill_price': k_result.get('fill_price'),
        'k_order_id': k_result.get('order_id'),
        'pm_fill_count': pm_result.get('fill_count', 0),
        'pm_fill_price': pm_result.get('fill_price'),
        'pm_order_id': pm_result.get('order_id'),
        'pm_slug': arb.pm_slug,
        'pm_success': pm_result.get('success', False),
        'pm_error': pm_result.get('error'),
        'status': display_status,
        'raw_status': status,
        'execution_mode': EXECUTION_MODE.value,
        'needs_review': arb.needs_review,
        'review_reason': arb.review_reason if arb.needs_review else None,
        'is_live_game': arb.is_live_game,
        'expected_profit': arb.profit,
        'roi': arb.roi,
        'k_bid': arb.k_bid,
        'k_ask': arb.k_ask,
        'pm_bid': arb.pm_bid,
        'pm_ask': arb.pm_ask
    }
    TRADE_LOG.append(trade)

    if len(TRADE_LOG) > 1000:
        TRADE_LOG = TRADE_LOG[-1000:]

    try:
        with open('trades.json', 'w') as f:
            json.dump(TRADE_LOG, f, indent=2)
    except:
        pass


def log_skipped_arb(arb: ArbOpportunity, reason: str, details: str = ""):
    """Log a skipped arbitrage opportunity for analysis"""
    global SKIPPED_ARBS, SKIP_STATS, SCAN_STATS

    # Update stats
    if reason in SKIP_STATS:
        SKIP_STATS[reason] += 1
    SCAN_STATS['total_skipped'] += 1

    skipped = {
        'timestamp': datetime.now().isoformat(),
        'game': arb.game,
        'team': arb.team,
        'sport': arb.sport,
        'k_bid': arb.k_bid,
        'k_ask': arb.k_ask,
        'pm_bid': arb.pm_bid,
        'pm_ask': arb.pm_ask,
        'initial_roi': round(arb.roi, 2),
        'skip_reason': reason,
        'details': details,
        'pm_slug': arb.pm_slug,
        'is_live_game': arb.is_live_game
    }
    SKIPPED_ARBS.append(skipped)

    # Keep only last 500 entries
    if len(SKIPPED_ARBS) > 500:
        SKIPPED_ARBS = SKIPPED_ARBS[-500:]

    # Save to file periodically (every 10 skipped)
    if len(SKIPPED_ARBS) % 10 == 0:
        try:
            with open('skipped_arbs.json', 'w') as f:
                json.dump(SKIPPED_ARBS, f, indent=2)
        except:
            pass


def save_skipped_arbs():
    """Force save skipped arbs to file"""
    try:
        with open('skipped_arbs.json', 'w') as f:
            json.dump(SKIPPED_ARBS, f, indent=2)
    except:
        pass


def save_price_history():
    """Save price history to CSV file on shutdown"""
    if not PRICE_HISTORY:
        print("[PRICE HISTORY] No data to save")
        return

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'price_history_{timestamp_str}.csv'

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write('game_key,sport,game_id,team,timestamp,scan_num,kalshi_bid,kalshi_ask,pm_bid,pm_ask,spread_buy_pm,spread_buy_k,has_arb\n')

            total_rows = 0
            for game_key, snapshots in PRICE_HISTORY.items():
                # Parse game_key: "{sport}:{game_id}:{team}"
                parts = game_key.split(':')
                if len(parts) >= 3:
                    sport = parts[0]
                    game_id = parts[1]
                    team = parts[2]
                else:
                    sport, game_id, team = 'unknown', 'unknown', 'unknown'

                for snap in snapshots:
                    f.write(f'{game_key},{sport},{game_id},{team},{snap.timestamp},{snap.scan_num},'
                           f'{snap.kalshi_bid},{snap.kalshi_ask},{snap.pm_bid},{snap.pm_ask},'
                           f'{snap.spread_buy_pm},{snap.spread_buy_k},{snap.has_arb}\n')
                    total_rows += 1

        print(f"[PRICE HISTORY] Saved {total_rows} rows across {len(PRICE_HISTORY)} games to {filename}")
        return filename
    except Exception as e:
        print(f"[PRICE HISTORY] Error saving CSV: {e}")
        return None


def generate_price_charts(csv_filename: str = None):
    """Generate visualization charts from price history data"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend for headless
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("[CHART] matplotlib not installed. Run: pip install matplotlib")
        return None

    if not PRICE_HISTORY:
        print("[CHART] No price history data to chart")
        return None

    # Find games with arb opportunities
    games_with_arbs = []
    for game_key, snapshots in PRICE_HISTORY.items():
        arb_count = sum(1 for s in snapshots if s.has_arb)
        if arb_count > 0:
            games_with_arbs.append((game_key, snapshots, arb_count))

    if not games_with_arbs:
        print("[CHART] No games with arb opportunities found")
        return None

    # Sort by number of arb snapshots (most interesting first)
    games_with_arbs.sort(key=lambda x: -x[2])

    # Create figure with subplots for top N games
    max_charts = min(6, len(games_with_arbs))
    fig, axes = plt.subplots(max_charts, 1, figsize=(14, 4 * max_charts))
    if max_charts == 1:
        axes = [axes]

    for idx, (game_key, snapshots, arb_count) in enumerate(games_with_arbs[:max_charts]):
        ax = axes[idx]

        # Extract data
        times = [datetime.fromtimestamp(s.timestamp) for s in snapshots]
        k_bids = [s.kalshi_bid for s in snapshots]
        k_asks = [s.kalshi_ask for s in snapshots]
        pm_bids = [s.pm_bid for s in snapshots]
        pm_asks = [s.pm_ask for s in snapshots]
        has_arbs = [s.has_arb for s in snapshots]

        # Plot prices
        ax.plot(times, k_bids, 'b-', label='Kalshi Bid', linewidth=1)
        ax.plot(times, k_asks, 'b--', label='Kalshi Ask', linewidth=1, alpha=0.7)
        ax.plot(times, pm_bids, 'r-', label='PM Bid', linewidth=1)
        ax.plot(times, pm_asks, 'r--', label='PM Ask', linewidth=1, alpha=0.7)

        # Highlight arb windows
        arb_times = [t for t, has in zip(times, has_arbs) if has]
        arb_prices = [max(k_bids[i], pm_bids[i]) for i, has in enumerate(has_arbs) if has]
        if arb_times:
            ax.scatter(arb_times, arb_prices, color='green', marker='o', s=30,
                      label=f'Arb Window ({arb_count})', zorder=5)

        # Parse game_key for title
        parts = game_key.split(':')
        sport = parts[0].upper() if len(parts) > 0 else ''
        game_id = parts[1] if len(parts) > 1 else ''
        team = parts[2] if len(parts) > 2 else ''

        ax.set_title(f'{sport} {game_id} - {team} ({len(snapshots)} samples, {arb_count} arb windows)')
        ax.set_ylabel('Price (cents)')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    axes[-1].set_xlabel('Time')

    plt.tight_layout()

    # Save chart
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    chart_filename = f'price_chart_{timestamp_str}.png'
    plt.savefig(chart_filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"[CHART] Saved price chart to {chart_filename}")
    return chart_filename


# ============================================================================
# AUTO-SAVE FUNCTIONALITY
# Save data periodically to prevent loss on crash
# ============================================================================
AUTO_SAVE_INTERVAL = 300  # seconds (5 minutes)
AUTO_SAVE_SCAN_INTERVAL = 500  # or every N scans
LAST_AUTO_SAVE_TIME = 0.0
LAST_AUTO_SAVE_SCAN = 0
PRICE_HISTORY_ROWS_SAVED = 0  # Track rows already saved to CSV


def auto_save_price_history() -> int:
    """Append new price history rows to CSV. Returns number of new rows saved."""
    global PRICE_HISTORY_ROWS_SAVED

    if not PRICE_HISTORY:
        return 0

    # Count total rows
    total_rows = sum(len(snapshots) for snapshots in PRICE_HISTORY.values())
    new_rows = total_rows - PRICE_HISTORY_ROWS_SAVED

    if new_rows <= 0:
        return 0

    filename = 'price_history.csv'
    try:
        # Check if file exists (need to write header if not)
        file_exists = os.path.exists(filename)

        with open(filename, 'a', encoding='utf-8') as f:
            # Write header if new file
            if not file_exists:
                f.write('game_key,sport,game_id,team,timestamp,scan_num,kalshi_bid,kalshi_ask,pm_bid,pm_ask,spread_buy_pm,spread_buy_k,has_arb\n')

            # Write only new rows (rows after PRICE_HISTORY_ROWS_SAVED)
            rows_written = 0
            rows_seen = 0
            for game_key, snapshots in PRICE_HISTORY.items():
                parts = game_key.split(':')
                sport = parts[0] if len(parts) > 0 else 'unknown'
                game_id = parts[1] if len(parts) > 1 else 'unknown'
                team = parts[2] if len(parts) > 2 else 'unknown'

                for snap in snapshots:
                    rows_seen += 1
                    if rows_seen <= PRICE_HISTORY_ROWS_SAVED:
                        continue  # Already saved

                    f.write(f'{game_key},{sport},{game_id},{team},{snap.timestamp},{snap.scan_num},'
                           f'{snap.kalshi_bid},{snap.kalshi_ask},{snap.pm_bid},{snap.pm_ask},'
                           f'{snap.spread_buy_pm},{snap.spread_buy_k},{snap.has_arb}\n')
                    rows_written += 1

        PRICE_HISTORY_ROWS_SAVED = total_rows
        return rows_written
    except Exception as e:
        print(f"[AUTO-SAVE] Error saving price history: {e}")
        return 0


def auto_save_tam_snapshot() -> bool:
    """Save current TAM state to JSON."""
    try:
        snapshot = {
            'timestamp': time.time(),
            'timestamp_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tam_stats': dict(TAM_STATS),
            'active_arbs_count': len(ACTIVE_ARBS),
            'recently_closed_count': len(RECENTLY_CLOSED),
            'closed_arbs_count': len(CLOSED_ARBS),
            'active_arbs': [
                {
                    'arb_key': a.arb_key,
                    'sport': a.sport,
                    'team': a.team,
                    'game': a.game,
                    'direction': a.direction,
                    'current_spread': a.current_spread,
                    'current_size': a.current_size,
                    'current_profit_cents': a.current_profit_cents,
                    'scan_count': a.scan_count,
                    'first_seen': a.first_seen,
                    'executed': a.executed,
                    'is_reopen': a.is_reopen,
                }
                for a in ACTIVE_ARBS.values()
            ],
            'price_history_games': len(PRICE_HISTORY),
            'price_history_rows': sum(len(s) for s in PRICE_HISTORY.values()),
        }

        with open('tam_snapshot.json', 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
        return True
    except Exception as e:
        print(f"[AUTO-SAVE] Error saving TAM snapshot: {e}")
        return False


def perform_auto_save(scan_num: int) -> None:
    """Perform auto-save of all data."""
    global LAST_AUTO_SAVE_TIME, LAST_AUTO_SAVE_SCAN

    price_rows = auto_save_price_history()
    tam_saved = auto_save_tam_snapshot()

    total_profit = TAM_STATS.get('total_profit_if_captured', 0) / 100
    unique_arbs = TAM_STATS.get('unique_arbs_new', 0) + TAM_STATS.get('unique_arbs_reopen', 0)

    status = "OK" if tam_saved else "PARTIAL"
    print(f"[AUTO-SAVE] {PRICE_HISTORY_ROWS_SAVED:,} price rows saved, TAM: ${total_profit:.2f} from {unique_arbs} arbs [{status}]")

    LAST_AUTO_SAVE_TIME = time.time()
    LAST_AUTO_SAVE_SCAN = scan_num


# =============================================================================
# PENDING MARKET MONITORING
# =============================================================================

def load_activated_markets() -> Dict[str, Dict]:
    """Load activated markets history from JSON file."""
    try:
        if os.path.exists(ACTIVATED_MARKETS_FILE):
            with open(ACTIVATED_MARKETS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"[PENDING] Error loading activated markets: {e}")
    return {}


def save_activated_markets() -> None:
    """Save activated markets history to JSON file."""
    global ACTIVATED_MARKETS
    try:
        with open(ACTIVATED_MARKETS_FILE, 'w') as f:
            json.dump(ACTIVATED_MARKETS, f, indent=2, default=str)
    except Exception as e:
        print(f"[PENDING] Error saving activated markets: {e}")


def process_pending_markets(all_markets: List[Dict], kalshi_cache: Dict) -> Tuple[List[Dict], List[Dict]]:
    """
    Process all PM US markets to track PENDING ones and detect activations.

    Returns: (pending_markets, newly_activated)
    """
    global PENDING_MARKETS, ACTIVATED_MARKETS

    now = time.time()
    now_dt = datetime.now()

    pending = []
    newly_activated = []

    for m in all_markets:
        slug = m.get('slug', '')

        # Only track sports markets
        if not any(x in slug.lower() for x in ['-nba-', '-nhl-', '-cbb-', '-ncaab-']):
            continue

        is_active = m.get('active', False)
        ep3_status = m.get('ep3Status', '')
        outcome_prices = m.get('outcomePrices', '["0","0"]')
        game_time_str = m.get('gameStartTime', '')

        # Parse game time
        game_time = None
        hours_to_game = None
        if game_time_str:
            try:
                game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                # Convert to EST for display
                game_time_est = game_time - timedelta(hours=5)
                hours_to_game = (game_time - datetime.utcnow()).total_seconds() / 3600
            except:
                pass

        # Determine sport from slug
        sport = None
        if '-nba-' in slug.lower():
            sport = 'nba'
        elif '-nhl-' in slug.lower():
            sport = 'nhl'
        elif '-cbb-' in slug.lower() or '-ncaab-' in slug.lower():
            sport = 'cbb'

        # Extract teams from slug (e.g., aec-nba-lal-was-2026-01-30)
        parts = slug.split('-')
        team1, team2 = None, None
        if len(parts) >= 5 and sport:
            sport_idx = next((i for i, p in enumerate(parts) if p in ['nba', 'nhl', 'cbb', 'ncaab']), -1)
            if sport_idx >= 0 and sport_idx + 2 < len(parts):
                team1 = parts[sport_idx + 1].upper()
                team2 = parts[sport_idx + 2].upper()
                # Apply SLUG_TO_KALSHI mapping
                team1 = SLUG_TO_KALSHI.get(team1, team1)
                team2 = SLUG_TO_KALSHI.get(team2, team2)

        # Check if this is a PENDING market
        if not is_active or ep3_status == 'PENDING':
            # Track as pending
            if slug not in PENDING_MARKETS:
                PENDING_MARKETS[slug] = {
                    'first_seen': now,
                    'game_time': game_time_str,
                    'sport': sport,
                    'team1': team1,
                    'team2': team2,
                    'last_prices': outcome_prices,
                }
            else:
                # Update last seen prices
                PENDING_MARKETS[slug]['last_prices'] = outcome_prices

            # Add to pending list for display
            pending.append({
                'slug': slug,
                'sport': sport,
                'team1': team1,
                'team2': team2,
                'game_time': game_time_str,
                'hours_to_game': hours_to_game,
                'ep3_status': ep3_status,
                'prices': outcome_prices,
            })

        else:
            # Market is ACTIVE - check if it was previously PENDING
            if slug in PENDING_MARKETS:
                # ACTIVATION DETECTED!
                prev_data = PENDING_MARKETS[slug]

                # Calculate hours before game when activated
                hours_before = None
                if game_time:
                    hours_before = (game_time - datetime.utcnow()).total_seconds() / 3600

                # Check for Kalshi match
                kalshi_match = None
                if sport and team1 and team2:
                    # Build cache key format: {sport}:{sorted_teams}:{date}
                    # IMPORTANT: Convert UTC game time to EST date for Kalshi matching
                    sorted_teams = '-'.join(sorted([team1, team2]))
                    game_date = None
                    if game_time_str:
                        try:
                            dt_utc = datetime.fromisoformat(game_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                            dt_est = dt_utc - timedelta(hours=5)  # UTC to EST
                            game_date = dt_est.strftime('%Y-%m-%d')
                        except:
                            game_date = game_time_str[:10]  # Fallback to raw date
                    if game_date:
                        cache_key = f"{sport}:{sorted_teams}:{game_date}"
                        kalshi_match = cache_key if cache_key in kalshi_cache else None

                activation_info = {
                    'game_time': game_time_str,
                    'activated_at': datetime.now().isoformat(),
                    'hours_before_game': round(hours_before, 2) if hours_before else None,
                    'sport': sport,
                    'team1': team1,
                    'team2': team2,
                    'kalshi_match': kalshi_match,
                    'new_prices': outcome_prices,
                    'was_pending_for_hours': round((now - prev_data['first_seen']) / 3600, 2),
                }

                ACTIVATED_MARKETS[slug] = activation_info
                save_activated_markets()  # Persist immediately

                newly_activated.append({
                    'slug': slug,
                    'info': activation_info,
                })

                # Remove from pending tracking
                del PENDING_MARKETS[slug]

    # Sort pending by hours to game
    pending.sort(key=lambda x: x.get('hours_to_game') or 999)

    return pending, newly_activated


def display_pending_markets(pending: List[Dict], limit: int = 10) -> None:
    """Display PENDING markets status."""
    if not pending:
        return

    # Count by sport
    by_sport = {'nba': 0, 'nhl': 0, 'cbb': 0}
    for p in pending:
        sport = p.get('sport')
        if sport in by_sport:
            by_sport[sport] += 1

    print(f"\n[PENDING MARKETS] {len(pending)} games waiting to activate "
          f"(NBA:{by_sport['nba']}, NHL:{by_sport['nhl']}, CBB:{by_sport['cbb']}):")

    for p in pending[:limit]:
        slug = p['slug']
        hours = p.get('hours_to_game')
        sport = p.get('sport', '').upper()
        team1 = p.get('team1', '?')
        team2 = p.get('team2', '?')

        if hours is not None:
            if hours < 0:
                time_str = f"STARTED {-hours:.1f}h ago"
            elif hours < 1:
                time_str = f"{hours*60:.0f}min to game"
            else:
                time_str = f"{hours:.1f}h to game"
        else:
            time_str = "time unknown"

        print(f"  - {sport} {team1} vs {team2}: {time_str}")

    if len(pending) > limit:
        print(f"  ... and {len(pending) - limit} more")


def display_activation_alert(activated: List[Dict], kalshi_cache: Dict) -> None:
    """Display alert when markets activate."""
    for item in activated:
        slug = item['slug']
        info = item['info']

        sport = info.get('sport', '').upper()
        team1 = info.get('team1', '?')
        team2 = info.get('team2', '?')
        hours_before = info.get('hours_before_game')
        kalshi_match = info.get('kalshi_match')

        print(f"\n{'='*60}")
        print(f"[ACTIVATED] {slug} is now tradeable!")
        print(f"  Game: {sport} {team1} vs {team2}")
        if hours_before is not None:
            print(f"  Activated {hours_before:.1f}h before game start")

        if kalshi_match:
            print(f"  Kalshi match: {kalshi_match} [FOUND]")
            print(f"  >>> Checking for arb opportunity...")
        else:
            print(f"  Kalshi match: NOT FOUND")
        print(f"{'='*60}")


def get_activation_stats() -> Dict:
    """Get statistics about market activation timing."""
    if not ACTIVATED_MARKETS:
        return {}

    hours_before_list = [
        v['hours_before_game']
        for v in ACTIVATED_MARKETS.values()
        if v.get('hours_before_game') is not None
    ]

    if not hours_before_list:
        return {'count': len(ACTIVATED_MARKETS)}

    return {
        'count': len(ACTIVATED_MARKETS),
        'avg_hours_before': sum(hours_before_list) / len(hours_before_list),
        'min_hours_before': min(hours_before_list),
        'max_hours_before': max(hours_before_list),
    }


def get_best_skipped_opportunity() -> Optional[Dict]:
    """Get the highest ROI skipped opportunity from current session"""
    if not SKIPPED_ARBS:
        return None
    # Find highest ROI skipped in last 100 entries
    recent = SKIPPED_ARBS[-100:]
    return max(recent, key=lambda x: x.get('initial_roi', 0))


def export_market_data(all_games: Dict, arbs: List[ArbOpportunity]):
    """Export market mapping, spread, and volume data for dashboard"""
    global VOLUME_HISTORY

    kalshi_games = []
    spreads = []
    match_stats = {}
    volume_by_sport = {}

    for cfg in SPORTS_CONFIG:
        sport = cfg['sport'].upper()
        sport_games = all_games.get(cfg['sport'], {})
        matched_count = 0
        sport_k_volume = 0
        sport_pm_volume = 0

        for gid, game in sport_games.items():
            for team, p in game['teams'].items():
                ticker = game['tickers'].get(team, '')
                has_pm = 'pm_ask' in p
                if has_pm:
                    matched_count += 1

                # Aggregate volume
                k_vol = p.get('k_volume', 0) or 0
                pm_vol = p.get('pm_volume', 0) or 0
                sport_k_volume += k_vol
                sport_pm_volume += pm_vol

                kalshi_games.append({
                    'sport': sport, 'game': gid, 'team': team, 'ticker': ticker,
                    'k_bid': p.get('k_bid', 0), 'k_ask': p.get('k_ask', 0),
                    'k_volume': k_vol, 'pm_volume': pm_vol,
                    'pm_slug': p.get('pm_slug'), 'pm_bid': p.get('pm_bid'),
                    'pm_ask': p.get('pm_ask'), 'matched': has_pm, 'date': game.get('date')
                })

                if has_pm:
                    spread = p['k_bid'] - p['pm_ask']
                    roi = (spread / p['pm_ask'] * 100) if p['pm_ask'] > 0 else 0
                    spreads.append({
                        'sport': sport, 'game': gid, 'team': team,
                        'k_bid': p['k_bid'], 'k_ask': p['k_ask'],
                        'pm_bid': p['pm_bid'], 'pm_ask': p['pm_ask'],
                        'spread': spread, 'roi': roi,
                        'status': 'ARB' if roi >= 5 else 'CLOSE' if roi >= 2 else 'NO_EDGE',
                        'pm_slug': p['pm_slug'], 'ticker': ticker
                    })

        total = len(sport_games)
        match_stats[sport] = {'matched': matched_count // 2, 'total': total,
                             'rate': (matched_count // 2 / total * 100) if total else 0}
        volume_by_sport[sport] = {
            'kalshi': sport_k_volume,
            'pm': sport_pm_volume,
            'total': sport_k_volume + sport_pm_volume
        }

    spreads.sort(key=lambda x: -x['roi'])

    # Calculate total volume
    total_k_volume = sum(v['kalshi'] for v in volume_by_sport.values())
    total_pm_volume = sum(v['pm'] for v in volume_by_sport.values())
    total_volume = total_k_volume + total_pm_volume

    # Add to volume history
    now = datetime.now()
    VOLUME_HISTORY.append({
        'timestamp': now.isoformat(),
        'kalshi': total_k_volume,
        'pm': total_pm_volume,
        'total': total_volume
    })

    # Keep only last 24 hours
    if len(VOLUME_HISTORY) > MAX_VOLUME_HISTORY:
        VOLUME_HISTORY = VOLUME_HISTORY[-MAX_VOLUME_HISTORY:]

    data = {
        'timestamp': now.isoformat(),
        'kalshi_games': kalshi_games, 'match_stats': match_stats,
        'spreads': spreads, 'total_kalshi': len(kalshi_games) // 2,
        'total_matched': sum(s['matched'] for s in match_stats.values()),
        'volume_by_sport': volume_by_sport,
        'volume_history': VOLUME_HISTORY[-50:],  # Last 50 data points for chart
        'total_volume': {
            'kalshi': total_k_volume,
            'pm': total_pm_volume,
            'total': total_volume
        }
    }

    try:
        with open('market_data.json', 'w') as f:
            json.dump(data, f)
    except:
        pass


# Market data mappings
MONTH_MAP = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06',
             'JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}

NBA_K2PM = {'ATL':'atl','BOS':'bos','BKN':'bkn','CHA':'cha','CHI':'chi','CLE':'cle',
            'DAL':'dal','DEN':'den','DET':'det','GSW':'gsw','HOU':'hou','IND':'ind',
            'LAC':'lac','LAL':'lal','MEM':'mem','MIA':'mia','MIL':'mil','MIN':'min',
            'NOP':'nop','NYK':'nyk','OKC':'okc','ORL':'orl','PHI':'phi','PHX':'phx',
            'POR':'por','SAC':'sac','SAS':'sas','TOR':'tor','UTA':'uta','WAS':'was'}

NBA_PM2K = {'Hawks':'ATL','Celtics':'BOS','Nets':'BKN','Hornets':'CHA','Bulls':'CHI',
            'Cavaliers':'CLE','Mavericks':'DAL','Nuggets':'DEN','Pistons':'DET',
            'Warriors':'GSW','Rockets':'HOU','Pacers':'IND','Clippers':'LAC',
            'Lakers':'LAL','Grizzlies':'MEM','Heat':'MIA','Bucks':'MIL',
            'Timberwolves':'MIN','Pelicans':'NOP','Knicks':'NYK','Thunder':'OKC',
            'Magic':'ORL','76ers':'PHI','Suns':'PHX','Trail Blazers':'POR',
            'Kings':'SAC','Spurs':'SAS','Raptors':'TOR','Jazz':'UTA','Wizards':'WAS'}

NHL_K2PM = {'ANA':'ana','BOS':'bos','BUF':'buf','CGY':'cgy','CAR':'car','CHI':'chi',
            'COL':'col','CBJ':'cbj','DAL':'dal','DET':'det','EDM':'edm','FLA':'fla',
            'LA':'la','MIN':'min','MTL':'mtl','NSH':'nsh','NJ':'nj','NYI':'nyi',
            'NYR':'nyr','OTT':'ott','PHI':'phi','PIT':'pit','SJ':'sj','SEA':'sea',
            'STL':'stl','TB':'tb','TOR':'tor','UTA':'uta','VAN':'van','VGK':'vgk','WPG':'wpg','WSH':'wsh'}

NHL_PM2K = {'Ducks':'ANA','Bruins':'BOS','Sabres':'BUF','Flames':'CGY','Hurricanes':'CAR',
            'Blackhawks':'CHI','Avalanche':'COL','Blue Jackets':'CBJ','Stars':'DAL',
            'Red Wings':'DET','Oilers':'EDM','Panthers':'FLA','Kings':'LA','Wild':'MIN',
            'Canadiens':'MTL','Predators':'NSH','Devils':'NJ','Islanders':'NYI',
            'Rangers':'NYR','Senators':'OTT','Flyers':'PHI','Penguins':'PIT','Sharks':'SJ',
            'Kraken':'SEA','Blues':'STL','Lightning':'TB','Maple Leafs':'TOR',
            'Canucks':'VAN','Golden Knights':'VGK','Jets':'WPG','Capitals':'WSH',
            'Utah Hockey Club':'UTA','Mammoth':'UTA'}

# Extended mappings for better matching - includes full names, abbreviations, cities
NBA_FULL_NAMES = {
    'atlanta hawks': 'ATL', 'hawks': 'ATL', 'atl': 'ATL',
    'boston celtics': 'BOS', 'celtics': 'BOS', 'bos': 'BOS',
    'brooklyn nets': 'BKN', 'nets': 'BKN', 'bkn': 'BKN',
    'charlotte hornets': 'CHA', 'hornets': 'CHA', 'cha': 'CHA',
    'chicago bulls': 'CHI', 'bulls': 'CHI', 'chi': 'CHI',
    'cleveland cavaliers': 'CLE', 'cavaliers': 'CLE', 'cavs': 'CLE', 'cle': 'CLE',
    'dallas mavericks': 'DAL', 'mavericks': 'DAL', 'mavs': 'DAL', 'dal': 'DAL',
    'denver nuggets': 'DEN', 'nuggets': 'DEN', 'den': 'DEN',
    'detroit pistons': 'DET', 'pistons': 'DET', 'det': 'DET',
    'golden state warriors': 'GSW', 'warriors': 'GSW', 'gsw': 'GSW',
    'houston rockets': 'HOU', 'rockets': 'HOU', 'hou': 'HOU',
    'indiana pacers': 'IND', 'pacers': 'IND', 'ind': 'IND',
    'la clippers': 'LAC', 'los angeles clippers': 'LAC', 'clippers': 'LAC', 'lac': 'LAC',
    'la lakers': 'LAL', 'los angeles lakers': 'LAL', 'lakers': 'LAL', 'lal': 'LAL',
    'memphis grizzlies': 'MEM', 'grizzlies': 'MEM', 'mem': 'MEM',
    'miami heat': 'MIA', 'heat': 'MIA', 'mia': 'MIA',
    'milwaukee bucks': 'MIL', 'bucks': 'MIL', 'mil': 'MIL',
    'minnesota timberwolves': 'MIN', 'timberwolves': 'MIN', 'wolves': 'MIN', 'min': 'MIN',
    'new orleans pelicans': 'NOP', 'pelicans': 'NOP', 'nop': 'NOP',
    'new york knicks': 'NYK', 'knicks': 'NYK', 'nyk': 'NYK',
    'oklahoma city thunder': 'OKC', 'thunder': 'OKC', 'okc': 'OKC',
    'orlando magic': 'ORL', 'magic': 'ORL', 'orl': 'ORL',
    'philadelphia 76ers': 'PHI', '76ers': 'PHI', 'sixers': 'PHI', 'phi': 'PHI',
    'phoenix suns': 'PHX', 'suns': 'PHX', 'phx': 'PHX',
    'portland trail blazers': 'POR', 'trail blazers': 'POR', 'blazers': 'POR', 'por': 'POR',
    'sacramento kings': 'SAC', 'kings': 'SAC', 'sac': 'SAC',
    'san antonio spurs': 'SAS', 'spurs': 'SAS', 'sas': 'SAS',
    'toronto raptors': 'TOR', 'raptors': 'TOR', 'tor': 'TOR',
    'utah jazz': 'UTA', 'jazz': 'UTA', 'uta': 'UTA',
    'washington wizards': 'WAS', 'wizards': 'WAS', 'was': 'WAS',
}

NHL_FULL_NAMES = {
    'anaheim ducks': 'ANA', 'ducks': 'ANA', 'ana': 'ANA',
    'boston bruins': 'BOS', 'bruins': 'BOS', 'bos': 'BOS',
    'buffalo sabres': 'BUF', 'sabres': 'BUF', 'buf': 'BUF',
    'calgary flames': 'CGY', 'flames': 'CGY', 'cgy': 'CGY',
    'carolina hurricanes': 'CAR', 'hurricanes': 'CAR', 'canes': 'CAR', 'car': 'CAR',
    'chicago blackhawks': 'CHI', 'blackhawks': 'CHI', 'hawks': 'CHI', 'chi': 'CHI',
    'colorado avalanche': 'COL', 'avalanche': 'COL', 'avs': 'COL', 'col': 'COL',
    'columbus blue jackets': 'CBJ', 'blue jackets': 'CBJ', 'cbj': 'CBJ',
    'dallas stars': 'DAL', 'stars': 'DAL', 'dal': 'DAL',
    'detroit red wings': 'DET', 'red wings': 'DET', 'det': 'DET',
    'edmonton oilers': 'EDM', 'oilers': 'EDM', 'edm': 'EDM',
    'florida panthers': 'FLA', 'panthers': 'FLA', 'fla': 'FLA',
    'los angeles kings': 'LA', 'la kings': 'LA', 'kings': 'LA', 'la': 'LA',
    'minnesota wild': 'MIN', 'wild': 'MIN', 'min': 'MIN',
    'montreal canadiens': 'MTL', 'canadiens': 'MTL', 'habs': 'MTL', 'mtl': 'MTL',
    'nashville predators': 'NSH', 'predators': 'NSH', 'preds': 'NSH', 'nsh': 'NSH',
    'new jersey devils': 'NJ', 'devils': 'NJ', 'nj': 'NJ', 'njd': 'NJ',
    'new york islanders': 'NYI', 'islanders': 'NYI', 'isles': 'NYI', 'nyi': 'NYI',
    'new york rangers': 'NYR', 'rangers': 'NYR', 'nyr': 'NYR',
    'ottawa senators': 'OTT', 'senators': 'OTT', 'sens': 'OTT', 'ott': 'OTT',
    'philadelphia flyers': 'PHI', 'flyers': 'PHI', 'phi': 'PHI',
    'pittsburgh penguins': 'PIT', 'penguins': 'PIT', 'pens': 'PIT', 'pit': 'PIT',
    'san jose sharks': 'SJ', 'sharks': 'SJ', 'sj': 'SJ', 'sjs': 'SJ',
    'seattle kraken': 'SEA', 'kraken': 'SEA', 'sea': 'SEA',
    'st louis blues': 'STL', 'st. louis blues': 'STL', 'blues': 'STL', 'stl': 'STL',
    'tampa bay lightning': 'TB', 'lightning': 'TB', 'bolts': 'TB', 'tb': 'TB', 'tbl': 'TB',
    'toronto maple leafs': 'TOR', 'maple leafs': 'TOR', 'leafs': 'TOR', 'tor': 'TOR',
    'vancouver canucks': 'VAN', 'canucks': 'VAN', 'nucks': 'VAN', 'van': 'VAN',
    'vegas golden knights': 'VGK', 'golden knights': 'VGK', 'knights': 'VGK', 'vgk': 'VGK',
    'winnipeg jets': 'WPG', 'jets': 'WPG', 'wpg': 'WPG',
    'washington capitals': 'WSH', 'capitals': 'WSH', 'caps': 'WSH', 'wsh': 'WSH',
    'utah hockey club': 'UTA', 'utah': 'UTA', 'mammoth': 'UTA', 'uta': 'UTA',
}

# ============================================================================
# COLLEGE BASKETBALL (CBB) MAPPINGS
# ============================================================================
# CBB is tricky - hundreds of schools, PM US uses mascots, Kalshi uses abbreviations
# Strategy: Map common mascots + use slug-based extraction for others
# Kalshi ticker format: KXCBBGAME-26JAN29SAMFWOFF-SAMF (Samford vs Wofford)

# Basic K2PM mapping (Kalshi abbrev -> PM US lowercase)
CBB_K2PM = {}  # Will be built dynamically from CBB_FULL_NAMES

# PM US mascot/name -> Kalshi abbreviation
CBB_PM2K = {
    # Common mascots - note some mascots are shared by multiple schools!
    'Bulldogs': None,  # Ambiguous: Samford, Bryant, Georgia, etc. - needs context
    'Paladins': 'FURMAN',
    'Terriers': 'WOFF',  # Wofford
    'Mocs': 'CHAT',  # Chattanooga
    'Bearcats': 'BING',  # Binghamton (also Cincinnati)
    'Highlanders': 'NJIT',
    'Great Danes': 'ALBNY',  # Albany
}

# Extended CBB mappings - school names, abbreviations, cities
CBB_FULL_NAMES = {
    # SoCon
    'samford': 'SAMF', 'samford bulldogs': 'SAMF', 'samf': 'SAMF',
    'furman': 'FURMAN', 'furman paladins': 'FURMAN', 'paladins': 'FURMAN',
    'wofford': 'WOFF', 'wofford terriers': 'WOFF', 'terriers': 'WOFF', 'woff': 'WOFF',
    'chattanooga': 'CHAT', 'utc': 'CHAT', 'mocs': 'CHAT', 'chat': 'CHAT',
    'etsu': 'ETSU', 'east tennessee state': 'ETSU', 'buccaneers': 'ETSU',
    'mercer': 'MERCER', 'mercer bears': 'MERCER',
    'uncg': 'UNCG', 'unc greensboro': 'UNCG', 'spartans': 'UNCG',
    'western carolina': 'WCU', 'catamounts': 'WCU', 'wcu': 'WCU',
    'vmi': 'VMI', 'keydets': 'VMI',
    'citadel': 'CIT', 'the citadel': 'CIT',

    # America East
    'bryant': 'BRYANT', 'bryant bulldogs': 'BRYANT',
    'binghamton': 'BING', 'binghamton bearcats': 'BING', 'bearcats': 'BING', 'bing': 'BING',
    'njit': 'NJIT', 'njit highlanders': 'NJIT', 'highlanders': 'NJIT',
    'albany': 'ALBNY', 'ualbany': 'ALBNY', 'great danes': 'ALBNY', 'albny': 'ALBNY',
    'umbc': 'UMBC', 'retrievers': 'UMBC',
    'maine': 'MAINE', 'black bears': 'MAINE',
    'new hampshire': 'UNH', 'unh': 'UNH', 'wildcats': 'UNH',
    'vermont': 'UVM', 'uvm': 'UVM', 'catamounts': 'UVM',
    'umass lowell': 'UML', 'river hawks': 'UML',

    # Big schools (common on betting markets)
    'duke': 'DUKE', 'blue devils': 'DUKE',
    'unc': 'UNC', 'north carolina': 'UNC', 'tar heels': 'UNC',
    'kentucky': 'UK', 'wildcats': 'UK',
    'kansas': 'KU', 'jayhawks': 'KU',
    'gonzaga': 'GONZ', 'zags': 'GONZ', 'bulldogs': 'GONZ',  # Note: Bulldogs is ambiguous
    'ucla': 'UCLA', 'bruins': 'UCLA',
    'oregon': 'ORE', 'oregon ducks': 'ORE', 'ore': 'ORE',
    'arizona': 'ARIZ', 'wildcats': 'ARIZ', 'ariz': 'ARIZ',
    'uconn': 'UCONN', 'connecticut': 'UCONN', 'huskies': 'UCONN',
    'villanova': 'NOVA', 'wildcats': 'NOVA', 'nova': 'NOVA',
    'purdue': 'PUR', 'boilermakers': 'PUR', 'pur': 'PUR',
    'michigan': 'MICH', 'wolverines': 'MICH', 'mich': 'MICH',
    'michigan state': 'MSU', 'spartans': 'MSU', 'msu': 'MSU',
    'ohio state': 'OSU', 'buckeyes': 'OSU', 'osu': 'OSU',
    'indiana': 'IND', 'hoosiers': 'IND',
    'iowa': 'IOWA', 'hawkeyes': 'IOWA',
    'illinois': 'ILL', 'fighting illini': 'ILL', 'illini': 'ILL', 'ill': 'ILL',
    'wisconsin': 'WISC', 'badgers': 'WISC', 'wisc': 'WISC',
    'texas': 'TEX', 'longhorns': 'TEX', 'tex': 'TEX',
    'baylor': 'BAY', 'bears': 'BAY', 'bay': 'BAY',
    'houston': 'HOU', 'cougars': 'HOU',
    'tennessee': 'TENN', 'volunteers': 'TENN', 'vols': 'TENN', 'tenn': 'TENN',
    'auburn': 'AUB', 'tigers': 'AUB', 'aub': 'AUB',
    'alabama': 'BAMA', 'crimson tide': 'BAMA', 'bama': 'BAMA',
    'lsu': 'LSU', 'tigers': 'LSU',
    'florida': 'FLA', 'gators': 'FLA',
    'arkansas': 'ARK', 'razorbacks': 'ARK', 'hogs': 'ARK', 'ark': 'ARK',
}

# Build CBB_K2PM from CBB_FULL_NAMES (reverse lookup for unique abbreviations)
_cbb_abbrevs = set(CBB_FULL_NAMES.values())
for abbrev in _cbb_abbrevs:
    if abbrev:
        CBB_K2PM[abbrev] = abbrev.lower()

SPORTS_CONFIG = [
    {'sport':'nba','series':'KXNBAGAME','k2pm':NBA_K2PM,'pm2k':NBA_PM2K},
    {'sport':'nhl','series':'KXNHLGAME','k2pm':NHL_K2PM,'pm2k':NHL_PM2K},
    {'sport':'cbb','series':'KXNCAAMBGAME','k2pm':CBB_K2PM,'pm2k':CBB_PM2K},
]

# PM US slug team codes differ from Kalshi codes
# This maps PM slug abbreviations to Kalshi abbreviations
SLUG_TO_KALSHI = {
    # NBA - PM vs Kalshi differences (from deep compare Jan 30)
    'GS': 'GSW',    # Golden State: PM uses GS, Kalshi uses GSW
    'NO': 'NOP',    # New Orleans: PM uses NO, Kalshi uses NOP
    'NY': 'NYK',    # New York Knicks: PM uses NY, Kalshi uses NYK
    'PHO': 'PHX',   # Phoenix: PM uses PHO, Kalshi uses PHX
    # NHL
    'VEG': 'VGK',   # Vegas Golden Knights (NHL)
    # NOTE: WAS/WSH - Kalshi NBA uses WAS, NHL uses WSH - don't map
    # CBB - State schools
    'VERM': 'UVM',      # Vermont
    'VER': 'UVM',       # Vermont variant
    'PENNST': 'PSU',    # Penn State
    'IDAHO': 'IDHO',    # Idaho
    # CBB - Name variations
    'UCONN': 'CONN',    # UConn
    'USCB': 'UCSB',     # UC Santa Barbara (typo)
    'CALPOL': 'CPOLY',  # Cal Poly
    'ORAL': 'ORU',      # Oral Roberts
    'BEACH': 'LBSU',    # Long Beach State
    # CBB - PM slug format uses different codes
    'TXAMC': 'ETAM',    # East Texas A&M (PM slug: txamc)
    'SAMF': 'SAM',      # Samford (PM slug: samf)
    'FURM': 'FUR',      # Furman (PM slug: furm)
    'FURMAN': 'FUR',    # Furman variant
    'NWST': 'NWST',     # Northwestern State (already correct)
    'PURD': 'PUR',      # Purdue (PM slug: purd)
    'MICH': 'MICH',     # Michigan (already correct)
    'IND': 'IND',       # Indiana (already correct)
    'DUKE': 'DUKE',     # Duke (already correct)
    'UNC': 'UNC',       # UNC (already correct)
    'KANS': 'KU',       # Kansas (PM slug: kans)
    'ARIZ': 'ARIZ',     # Arizona (already correct)
    'GONZ': 'GONZ',     # Gonzaga (already correct)
    'HOUS': 'HOU',      # Houston (PM: hous, K: HOU)
    'TENN': 'TENN',     # Tennessee (already correct)
    'FLOR': 'FLA',      # Florida (PM: flor, K: FLA)
    'ALAB': 'ALA',      # Alabama (PM: alab, K: ALA)
    'TEXA': 'TEX',      # Texas (PM: texa, K: TEX)
    'IOWA': 'IOWA',     # Iowa (already correct)
    'WISC': 'WIS',      # Wisconsin (PM: wisc, K: WIS)
    'OREG': 'ORE',      # Oregon (PM: oreg, K: ORE)
    'WASH': 'WASH',     # Washington (already correct for CBB)
    'UCLA': 'UCLA',     # UCLA (already correct)
    'USC': 'USC',       # USC (already correct)
    'STAN': 'STAN',     # Stanford (already correct)
    'COLO': 'COLO',     # Colorado (already correct)
    'UTAH': 'UTAH',     # Utah (already correct)
    'OKLA': 'OU',       # Oklahoma (PM: okla, K: OU)
    'OKST': 'OKST',     # Oklahoma State (already correct)
    'BAYL': 'BAY',      # Baylor (PM: bayl, K: BAY)
    'TCU': 'TCU',       # TCU (already correct)
    'TXTE': 'TT',       # Texas Tech (PM: txte, K: TT)
    'KSTA': 'KSU',      # Kansas State (PM: ksta, K: KSU)
    'IOST': 'ISU',      # Iowa State (PM: iost, K: ISU)
    'CINC': 'CIN',      # Cincinnati (PM: cinc, K: CIN)
    'BYU': 'BYU',       # BYU (already correct)
    'ARST': 'ASU',      # Arizona State (PM: arst, K: ASU)
    'MISS': 'MISS',     # Ole Miss (already correct)
    'MSST': 'MSST',     # Mississippi State (already correct)
    'LOUI': 'LSU',      # LSU (PM: loui, K: LSU)
    'VAND': 'VAN',      # Vanderbilt (PM: vand, K: VAN)
    'SCAR': 'SCAR',     # South Carolina (already correct)
    'GEOR': 'UGA',      # Georgia (PM: geor, K: UGA)
    'AUBR': 'AUB',      # Auburn (PM: aubr, K: AUB)
    'KENT': 'UK',       # Kentucky (PM: kent, K: UK)
    'MIZZ': 'MIZ',      # Missouri (PM: mizz, K: MIZ)
    'ARKN': 'ARK',      # Arkansas (PM: arkn, K: ARK)
    # CBB - Small school codes from PM slug analysis
    'STFPA': 'SFP',     # St. Francis PA (PM: stfpa, K: SFP)
    'LIUB': 'LIU',      # LIU Brooklyn (PM: liub, K: LIU)
    'CHIST': 'ACHS',    # Chicago State (PM: chist, K: ACHS)
    'LAMON': 'OULM',    # UL Monroe (PM: lamon, K: OULM)
    'NHVN': 'ANHC',     # New Haven (PM: nhvn, K: ANHC)
    'GAS': 'GAS',       # Georgia State (already correct)
    'WAG': 'WAG',       # Wagner (already correct)
    'MDES': 'UMES',     # Maryland Eastern Shore (PM: mdes, K: UMES)
    'SCARST': 'SCST',   # South Carolina State (PM: scarst, K: SCST)
    'ABCHR': 'ACT',     # Abilene Christian (PM: abchr, K: ACT)
    'TARL': 'ARL',      # Texas Arlington (PM: tarl, K: ARL)
    'ALAAM': 'AAMU',    # Alabama A&M (PM: alaam, K: AAMU)
    'PVAM': 'PVAM',     # Prairie View A&M (already correct)
    # CBB - Mappings from deep compare Jan 30
    'BROWN': 'BRWN',    # Brown
    'HARVRD': 'HARV',   # Harvard
    'KENTST': 'KENT',   # Kent State (Kalshi: KENT in KENTAKR)
    'AKRON': 'AKR',     # Akron (Kalshi: AKR)
    'CHARLT': 'CHAR',   # Charlotte
    'CLVST': 'CLEV',    # Cleveland State (Kalshi: CLEV in CLEVGB)
    'GB': 'GB',         # Green Bay (Kalshi: GB, not VGB)
    'COLMB': 'CLMB',    # Columbia
    'PRNCE': 'PRIN',    # Princeton (Kalshi: PRIN)
    'CORNEL': 'COR',    # Cornell (Kalshi: COR)
    'STLOU': 'SLU',     # Saint Louis
    'NKENT': 'NKU',     # Northern Kentucky
    'YNGST': 'YSU',     # Youngstown State (Kalshi: YSU)
    'IUPUI': 'IUIN',    # IU Indianapolis (Kalshi: IUIN)
    'LOYCH': 'LCHI',    # Loyola Chicago (Kalshi: LCHI)
    'VCU': 'VCU',       # VCU (Kalshi: VCU, not IVCU)
    'MANH': 'MAN',      # Manhattan
    'MST': 'MSU',       # Michigan State (Kalshi: MSU)
    'MICH': 'MICH',     # Michigan (Kalshi: MICH)
    'STPETE': 'SPC',    # Saint Peter's
    'MSTM': 'MSM',      # Mount St. Mary's
    'SACRED': 'SHU',    # Sacred Heart
    'QUIN': 'QUIN',     # Quinnipiac (already correct)
    'BOISE': 'BSU',     # Boise State (Kalshi: BSU)
    'GCAN': 'GC',       # Grand Canyon (Kalshi: GC)
    'SIENA': 'SIE',     # Siena
    'NIAGRA': 'NIAG',   # Niagara
    'WRGHT': 'WRST',    # Wright State (Kalshi: WRST in MILWWRST)
    'WBD': 'MILW',      # Milwaukee (PM uses WBD?)
    'MARIST': 'MRST',   # Marist (Kalshi: MRST)
    'CANS': 'CAN',      # Canisius (Kalshi: CAN)
    'NEVADA': 'NEV',    # Nevada (Kalshi: NEV)
    'UNLV': 'UNLV',     # UNLV (Kalshi: UNLV)
    'RIDER': 'RID',     # Rider
}

# PM US market cache: {cache_key: {slug, teams: {K_ABBR: {price, outcome_index}}, volume}}
PM_US_MARKET_CACHE = {}

# Volume history for trends (stores last 24h of snapshots)
VOLUME_HISTORY: List[Dict] = []
MAX_VOLUME_HISTORY = 288  # 24 hours at 5-minute intervals

# PENDING market tracking - monitors markets waiting to activate
# Key: slug, Value: {game_time, sport, teams, first_seen, last_prices}
PENDING_MARKETS: Dict[str, Dict] = {}

# Activated markets log - tracks when markets transition from PENDING to ACTIVE
# Key: slug, Value: {game_time, activated_at, hours_before_game, sport}
ACTIVATED_MARKETS: Dict[str, Dict] = {}
ACTIVATED_MARKETS_FILE = 'activated_markets.json'


def parse_gid(gid):
    m = re.match(r'(\d{2})([A-Z]{3})(\d{2})([A-Z]+)', gid)
    if m:
        date = f'20{m.group(1)}-{MONTH_MAP.get(m.group(2),"01")}-{m.group(3)}'
        teams = m.group(4)
        return date, teams[:len(teams)//2], teams[len(teams)//2:]
    return None, None, None


def normalize_team_name(name: str) -> str:
    """Normalize team name for matching - remove dates, extra spaces, standardize case"""
    if not name:
        return ''
    # Convert to lowercase
    name = name.lower().strip()
    # Remove common date patterns (e.g., "Jan 28", "1/28", "01-28")
    name = re.sub(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*\d{1,2}\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?\b', '', name)
    # Remove year patterns
    name = re.sub(r'\b20\d{2}\b', '', name)
    # Remove common suffixes
    name = re.sub(r'\s*(win|wins|to win|moneyline|ml)\s*$', '', name, flags=re.IGNORECASE)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def map_outcome_to_kalshi(outcome_name: str, pm2k: Dict, sport: str = None) -> Optional[str]:
    """
    Map a PM US outcome name to a Kalshi team abbreviation.
    Uses multiple matching strategies:
    1. Direct substring match from pm2k dict
    2. Full name lookup from extended mappings
    3. Abbreviation lookup
    """
    normalized = normalize_team_name(outcome_name)

    # Strategy 1: Direct substring match (original logic)
    for pm_name, k_abbr in pm2k.items():
        if pm_name.lower() in normalized:
            return k_abbr

    # Strategy 2: Check extended name mappings based on sport
    if sport == 'nba':
        # Try exact match first
        if normalized in NBA_FULL_NAMES:
            return NBA_FULL_NAMES[normalized]
        # Try each word
        for word in normalized.split():
            if word in NBA_FULL_NAMES:
                return NBA_FULL_NAMES[word]
        # Try substring match on full names
        for full_name, abbr in NBA_FULL_NAMES.items():
            if full_name in normalized or normalized in full_name:
                return abbr
    elif sport == 'nhl':
        # Try exact match first
        if normalized in NHL_FULL_NAMES:
            return NHL_FULL_NAMES[normalized]
        # Try each word
        for word in normalized.split():
            if word in NHL_FULL_NAMES:
                return NHL_FULL_NAMES[word]
        # Try substring match on full names
        for full_name, abbr in NHL_FULL_NAMES.items():
            if full_name in normalized or normalized in full_name:
                return abbr
    elif sport == 'cbb':
        # CBB: Try exact match first
        if normalized in CBB_FULL_NAMES:
            return CBB_FULL_NAMES[normalized]
        # Try each word (school names like "Samford", "Furman")
        for word in normalized.split():
            if word in CBB_FULL_NAMES:
                return CBB_FULL_NAMES[word]
        # Try substring match on full names
        for full_name, abbr in CBB_FULL_NAMES.items():
            if full_name in normalized or normalized in full_name:
                return abbr
        # CBB special: If the outcome looks like an abbreviation (all caps, 2-6 chars), use it directly
        upper_name = outcome_name.upper().strip()
        if 2 <= len(upper_name) <= 6 and upper_name.isalpha():
            return upper_name

    # Strategy 3: Try uppercase version as abbreviation (e.g., "NYR" -> "NYR")
    upper_name = outcome_name.upper().strip()
    if sport == 'nba' and upper_name.lower() in NBA_FULL_NAMES:
        return NBA_FULL_NAMES[upper_name.lower()]
    if sport == 'nhl' and upper_name.lower() in NHL_FULL_NAMES:
        return NHL_FULL_NAMES[upper_name.lower()]
    if sport == 'cbb' and upper_name.lower() in CBB_FULL_NAMES:
        return CBB_FULL_NAMES[upper_name.lower()]

    return None


async def run_match_debug():
    """Run detailed matching analysis and exit - helps diagnose why markets don't match"""
    print("\n" + "=" * 70)
    print("[MATCH DEBUG] Analyzing PM US <-> Kalshi market matching")
    print("=" * 70)

    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        # Fetch all markets from both platforms
        print("\n[1/3] Fetching Kalshi markets...")
        kalshi_data = await fetch_kalshi_markets(session, kalshi_api, debug=False)

        # Build Kalshi game lookup: {cache_key: {teams, tickers, ...}}
        kalshi_games = {}  # {cache_key: game_info}
        kalshi_team_lookup = {}  # {sport:team: [cache_keys]}

        for cfg in SPORTS_CONFIG:
            sport = cfg['sport']
            series = cfg['series']
            markets = kalshi_data.get(series, [])

            for m in markets:
                parts = m.get('ticker', '').split('-')
                if len(parts) < 3:
                    continue
                gid, team = parts[1], parts[2]
                if team == 'TIE':
                    continue

                date, _, _ = parse_gid(gid)
                if not date:
                    continue

                # Build cache key
                if gid not in kalshi_games.get(sport, {}):
                    if sport not in kalshi_games:
                        kalshi_games[sport] = {}
                    kalshi_games[sport][gid] = {
                        'date': date,
                        'teams': set(),
                        'tickers': {}
                    }

                kalshi_games[sport][gid]['teams'].add(team)
                kalshi_games[sport][gid]['tickers'][team] = m.get('ticker')

                # Team lookup
                team_key = f"{sport}:{team}"
                if team_key not in kalshi_team_lookup:
                    kalshi_team_lookup[team_key] = []
                kalshi_team_lookup[team_key].append((gid, date))

        # Build Kalshi cache keys
        kalshi_cache_keys = {}  # {cache_key: game_info}
        for sport, games in kalshi_games.items():
            for gid, game in games.items():
                if len(game['teams']) >= 2:
                    sorted_teams = sorted(list(game['teams']))
                    cache_key = f"{sport}:{sorted_teams[0]}-{sorted_teams[1]}:{game['date']}"
                    kalshi_cache_keys[cache_key] = {
                        'sport': sport,
                        'gid': gid,
                        'teams': sorted_teams,
                        'date': game['date'],
                        'tickers': game['tickers']
                    }

        total_kalshi = len(kalshi_cache_keys)
        print(f"    Found {total_kalshi} Kalshi games (with 2+ teams)")

        print("\n[2/3] Fetching PM US markets...")
        pm_us_matched = await fetch_pm_us_markets(session, pm_api, debug=False)
        print(f"    PM US returned info for {pm_us_matched} markets")

        # Analyze matches
        print("\n[3/3] Analyzing matches...\n")

        matched = []
        unmatched = []

        for cache_key, pm_info in PM_US_MARKET_CACHE.items():
            slug = pm_info.get('slug', '')
            teams = pm_info.get('teams', {})
            team_names = list(teams.keys())

            if cache_key in kalshi_cache_keys:
                # MATCHED
                k_info = kalshi_cache_keys[cache_key]
                matched.append({
                    'pm_slug': slug,
                    'cache_key': cache_key,
                    'pm_teams': team_names,
                    'kalshi_gid': k_info['gid'],
                    'kalshi_teams': k_info['teams'],
                })
            else:
                # UNMATCHED - diagnose why
                parts = cache_key.split(':')
                if len(parts) >= 3:
                    pm_sport = parts[0]
                    pm_teams_str = parts[1]
                    pm_date = parts[2]
                    pm_team_codes = pm_teams_str.split('-')
                else:
                    pm_sport, pm_teams_str, pm_date = 'unknown', 'unknown', 'unknown'
                    pm_team_codes = []

                # Try to find closest Kalshi match
                diagnosis = diagnose_mismatch(
                    cache_key, pm_sport, pm_team_codes, pm_date,
                    kalshi_cache_keys, kalshi_team_lookup
                )

                unmatched.append({
                    'pm_slug': slug,
                    'cache_key': cache_key,
                    'pm_teams': team_names,
                    'pm_team_codes': pm_team_codes,
                    'pm_sport': pm_sport,
                    'pm_date': pm_date,
                    'diagnosis': diagnosis,
                })

        # Print results
        total_pm = len(PM_US_MARKET_CACHE)
        match_rate = (len(matched) / total_pm * 100) if total_pm > 0 else 0

        print("=" * 70)
        print(f"[MATCH DEBUG] PM US: {total_pm} active markets | Kalshi: {total_kalshi} games")
        print("=" * 70)

        # Summary with match rate
        print(f"\n[MATCHED] {len(matched)} markets ({match_rate:.0f}%)")
        if len(unmatched) > 0:
            # Categorize unmatched
            coverage_gaps = [u for u in unmatched if u['diagnosis'].get('reason_type') == 'coverage_gap']
            mapping_issues = [u for u in unmatched if u['diagnosis'].get('reason_type') != 'coverage_gap']
            print(f"[UNMATCHED] {len(unmatched)} markets ({len(coverage_gaps)} coverage gaps, {len(mapping_issues)} mapping issues)")
        else:
            print(f"[UNMATCHED] 0 markets")

        # Show matched markets (first 10 only to reduce noise)
        if matched:
            print(f"\nMatched markets (showing first 10):")
            for m in matched[:10]:
                print(f"  [OK] {m['pm_slug']} -> {m['cache_key']}")
            if len(matched) > 10:
                print(f"  ... and {len(matched) - 10} more")

        # Unmatched markets with diagnosis
        print(f"\n[UNMATCHED DETAILS] {len(unmatched)} markets:")
        for u in unmatched:
            print(f"\n  [X] {u['pm_slug']}")
            print(f"      PM teams: {u['pm_teams']} -> {u['pm_team_codes']}")
            print(f"      PM key: {u['cache_key']}")

            diag = u['diagnosis']
            if diag['closest_key']:
                print(f"      Closest Kalshi: {diag['closest_key']}")
                print(f"      REASON: {diag['reason']}")
                if diag['fix']:
                    print(f"      FIX: {diag['fix']}")
            else:
                print(f"      Closest Kalshi: (none found)")
                print(f"      REASON: {diag['reason']}")

        # Summary of issues
        print("\n" + "=" * 70)
        print("[DIAGNOSIS SUMMARY]")
        reasons = {}
        for u in unmatched:
            reason = u['diagnosis']['reason_type']
            reasons[reason] = reasons.get(reason, 0) + 1

        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

        # Suggested fixes
        fixes_needed = [u for u in unmatched if u['diagnosis'].get('fix')]
        if fixes_needed:
            print("\n[SUGGESTED FIXES]")
            for u in fixes_needed[:10]:
                print(f"  {u['diagnosis']['fix']}")
            if len(fixes_needed) > 10:
                print(f"  ... and {len(fixes_needed) - 10} more")

        print("\n" + "=" * 70)


async def run_verify_games():
    """Search Kalshi by actual team names to find missing mappings"""
    print("\n" + "=" * 70)
    print("[VERIFY GAMES] Searching Kalshi by team names for unmatched PM markets")
    print("=" * 70)

    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        # Step 1: Get all Kalshi markets with their full details
        print("\n[1/4] Fetching all Kalshi CBB markets with team names...")

        # Fetch CBB markets specifically (they have the most mismatches)
        kalshi_markets = []
        for cfg in SPORTS_CONFIG:
            series = cfg['series']
            cursor = None
            while True:
                path = f'/trade-api/v2/markets?series_ticker={series}&status=open&limit=200'
                if cursor:
                    path += f'&cursor={cursor}'

                try:
                    async with session.get(
                        f'{kalshi_api.BASE_URL}{path}',
                        headers=kalshi_api._headers('GET', path),
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as r:
                        if r.status == 200:
                            data = await r.json()
                            markets = data.get('markets', [])
                            kalshi_markets.extend([(cfg['sport'], m) for m in markets])
                            cursor = data.get('cursor')
                            if not cursor or not markets:
                                break
                        else:
                            break
                except Exception as e:
                    print(f"Error fetching {series}: {e}")
                    break

        print(f"    Found {len(kalshi_markets)} total Kalshi markets")

        # Build lookup by team name substrings
        # kalshi_by_name[sport][name_substring] = [(ticker, team_code, full_title)]
        kalshi_by_name = {'nba': {}, 'nhl': {}, 'cbb': {}}
        kalshi_by_code = {'nba': {}, 'nhl': {}, 'cbb': {}}

        for sport, m in kalshi_markets:
            ticker = m.get('ticker', '')
            title = m.get('title', '') or m.get('subtitle', '') or ''
            parts = ticker.split('-')
            if len(parts) >= 3:
                team_code = parts[2]
                if team_code == 'TIE':
                    continue

                # Store by code
                if team_code not in kalshi_by_code[sport]:
                    kalshi_by_code[sport][team_code] = title

                # Extract words from title for name matching
                title_lower = title.lower()
                words = title_lower.replace('-', ' ').replace('/', ' ').split()
                for word in words:
                    if len(word) >= 3:  # Skip short words
                        if word not in kalshi_by_name[sport]:
                            kalshi_by_name[sport][word] = []
                        if (team_code, title) not in kalshi_by_name[sport][word]:
                            kalshi_by_name[sport][word].append((team_code, title))

        # Print Kalshi team codes for reference
        print(f"\n[2/4] Kalshi team codes found:")
        for sport in ['nba', 'nhl', 'cbb']:
            codes = sorted(kalshi_by_code[sport].keys())
            if codes:
                print(f"  {sport.upper()}: {len(codes)} teams")
                if sport == 'cbb':
                    # Show sample of CBB codes
                    print(f"    Sample: {codes[:20]}")

        # Step 2: Fetch PM markets
        print(f"\n[3/4] Fetching PM US markets...")
        await fetch_pm_us_markets(session, pm_api, debug=False)

        # Step 3: For each unmatched PM market, search by team name
        print(f"\n[4/4] Analyzing unmatched markets by team name...\n")

        # Build Kalshi cache keys for matching
        kalshi_cache_keys = set()
        for sport, m in kalshi_markets:
            ticker = m.get('ticker', '')
            parts = ticker.split('-')
            if len(parts) >= 3:
                gid = parts[1]
                team = parts[2]
                if team == 'TIE':
                    continue
                date, _, _ = parse_gid(gid)
                if date:
                    # We need both teams for the cache key, so just store gid info
                    pass

        # Check each PM market
        unmatched_analysis = []
        for cache_key, pm_info in PM_US_MARKET_CACHE.items():
            # Check if matched
            parts = cache_key.split(':')
            if len(parts) < 3:
                continue

            pm_sport = parts[0]
            pm_teams_str = parts[1]
            pm_date = parts[2]
            pm_team_codes = pm_teams_str.split('-')

            # Get the actual team names from PM
            slug = pm_info.get('slug', '')
            teams_dict = pm_info.get('teams', {})
            team_names = list(teams_dict.keys())

            # Check if this is unmatched by looking at the outcomes
            # We'll search Kalshi by team names

            if pm_sport == 'cbb' and len(team_names) >= 2:
                # Search Kalshi for these team names
                found_mappings = []
                for pm_name in team_names:
                    pm_name_lower = pm_name.lower()
                    pm_words = pm_name_lower.replace('-', ' ').split()

                    matches = []
                    for word in pm_words:
                        if len(word) >= 3 and word in kalshi_by_name.get(pm_sport, {}):
                            for k_code, k_title in kalshi_by_name[pm_sport][word]:
                                matches.append((k_code, k_title, word))

                    if matches:
                        found_mappings.append({
                            'pm_name': pm_name,
                            'matches': matches[:3]  # Top 3 matches
                        })

                if found_mappings:
                    unmatched_analysis.append({
                        'slug': slug,
                        'cache_key': cache_key,
                        'pm_teams': team_names,
                        'pm_codes': pm_team_codes,
                        'found_mappings': found_mappings
                    })

        # Print results
        print("=" * 70)
        print("[VERIFY GAMES] Team name search results")
        print("=" * 70)

        # Group by whether we found potential matches
        with_matches = [u for u in unmatched_analysis if u['found_mappings']]
        print(f"\n[FOUND POTENTIAL MAPPINGS] {len(with_matches)} markets:")

        suggested_mappings = {}  # {pm_name: kalshi_code}

        def pick_best_kalshi_code(pm_name: str, matches: list) -> Optional[str]:
            """Pick the Kalshi code that best matches the PM team name"""
            pm_upper = pm_name.upper()
            pm_lower = pm_name.lower()

            # Priority 1: Exact match or very close
            for k_code, k_title, matched_word in matches:
                k_code_upper = k_code.upper()
                # Check if codes are similar
                if pm_upper == k_code_upper:
                    return k_code
                if pm_upper in k_code_upper or k_code_upper in pm_upper:
                    return k_code
                # Check first letters match
                if len(pm_upper) >= 2 and len(k_code_upper) >= 2:
                    if pm_upper[:2] == k_code_upper[:2]:
                        return k_code

            # Priority 2: Team name appears in title near the code
            for k_code, k_title, matched_word in matches:
                title_lower = k_title.lower()
                # Check if PM name appears in the part of title associated with this team
                # e.g., "Oral Roberts at South Dakota St." - if PM is "ORAL", code should be ORU not SDST
                if ' at ' in title_lower:
                    parts = title_lower.split(' at ')
                    # First part is home team, second is away team
                    if len(parts) >= 2:
                        if pm_lower in parts[0] and k_code in k_title.split(' at ')[0]:
                            return k_code
                        if pm_lower in parts[1]:
                            # This team is the away team
                            return k_code

            # Fallback: return None, don't suggest
            return None

        for u in with_matches[:30]:  # Show first 30
            print(f"\n  {u['slug']}")
            print(f"    PM: {u['pm_teams']} -> codes: {u['pm_codes']}")
            for fm in u['found_mappings']:
                pm_name = fm['pm_name']
                print(f"    Searching '{pm_name}'...")
                for k_code, k_title, matched_word in fm['matches'][:2]:
                    print(f"      -> Kalshi '{k_code}' ({k_title[:50]}...) matched on '{matched_word}'")

                # Pick best match for suggestion
                best_code = pick_best_kalshi_code(pm_name, fm['matches'])
                if best_code and pm_name not in suggested_mappings:
                    suggested_mappings[pm_name] = best_code

        # Print suggested CBB_PM2K additions
        if suggested_mappings:
            print("\n" + "=" * 70)
            print("[SUGGESTED CBB_PM2K MAPPINGS]")
            print("Add these to CBB_PM2K dictionary:")
            print("-" * 40)
            for pm_name, k_code in sorted(suggested_mappings.items()):
                print(f"    '{pm_name}': '{k_code}',")

        # Also show Kalshi games that have no PM equivalent
        print("\n" + "=" * 70)
        print("[KALSHI COVERAGE]")
        cbb_codes = sorted(kalshi_by_code.get('cbb', {}).keys())
        print(f"CBB teams on Kalshi: {len(cbb_codes)}")
        if cbb_codes:
            print(f"Sample: {cbb_codes[:30]}")

        print("\n" + "=" * 70)


def diagnose_mismatch(cache_key: str, pm_sport: str, pm_team_codes: List[str],
                      pm_date: str, kalshi_cache_keys: Dict, kalshi_team_lookup: Dict) -> Dict:
    """Diagnose why a PM market doesn't match any Kalshi market"""

    result = {
        'closest_key': None,
        'reason': 'Unknown',
        'reason_type': 'unknown',
        'fix': None
    }

    # Check 1: Is this sport even on Kalshi?
    sport_keys = [k for k in kalshi_cache_keys if k.startswith(pm_sport + ':')]
    if not sport_keys:
        result['reason'] = f"Sport '{pm_sport}' not found on Kalshi"
        result['reason_type'] = 'sport_not_found'
        return result

    # Check 2: Are there games on this date?
    date_keys = [k for k in sport_keys if k.endswith(':' + pm_date)]
    if not date_keys:
        # Check for date mismatch (timezone issue?)
        nearby_dates = set()
        for k in sport_keys:
            k_date = k.split(':')[-1]
            nearby_dates.add(k_date)

        # Check for +/- 1 day
        try:
            pm_dt = datetime.strptime(pm_date, '%Y-%m-%d')
            prev_day = (pm_dt - timedelta(days=1)).strftime('%Y-%m-%d')
            next_day = (pm_dt + timedelta(days=1)).strftime('%Y-%m-%d')

            if prev_day in nearby_dates:
                alt_key = cache_key.replace(pm_date, prev_day)
                if alt_key in kalshi_cache_keys:
                    result['closest_key'] = alt_key
                    result['reason'] = f"Date mismatch: PM has {pm_date}, Kalshi has {prev_day} (timezone?)"
                    result['reason_type'] = 'date_mismatch'
                    result['fix'] = f"Check timezone conversion - game might be on {prev_day}"
                    return result

            if next_day in nearby_dates:
                alt_key = cache_key.replace(pm_date, next_day)
                if alt_key in kalshi_cache_keys:
                    result['closest_key'] = alt_key
                    result['reason'] = f"Date mismatch: PM has {pm_date}, Kalshi has {next_day} (timezone?)"
                    result['reason_type'] = 'date_mismatch'
                    result['fix'] = f"Check timezone conversion - game might be on {next_day}"
                    return result
        except:
            pass

        result['reason'] = f"No Kalshi games on {pm_date} for {pm_sport}"
        result['reason_type'] = 'date_not_found'
        return result

    # Check 3: Team code mismatch
    if len(pm_team_codes) >= 2:
        pm_t1, pm_t2 = pm_team_codes[0], pm_team_codes[1]

        # Look for each team individually
        t1_found = f"{pm_sport}:{pm_t1}" in kalshi_team_lookup
        t2_found = f"{pm_sport}:{pm_t2}" in kalshi_team_lookup

        if not t1_found and not t2_found:
            # Neither team found - check for similar team codes
            similar = find_similar_teams(pm_sport, pm_team_codes, kalshi_team_lookup, date_keys)
            if similar:
                result['closest_key'] = similar['key']
                result['reason'] = f"Team code mismatch: {similar['pm_code']} vs {similar['k_code']}"
                result['reason_type'] = 'team_code_mismatch'
                # Suggest fix based on sport
                mapping_var = f"{pm_sport.upper()}_PM2K"
                result['fix'] = f"Add {mapping_var}['{similar['pm_name']}'] = '{similar['k_code']}'"
                return result

            result['reason'] = f"Teams {pm_t1}/{pm_t2} not found on Kalshi for {pm_date}"
            result['reason_type'] = 'teams_not_found'
            return result

        elif not t1_found:
            # Only t1 missing
            similar = find_similar_team(pm_sport, pm_t1, kalshi_team_lookup)
            if similar:
                result['closest_key'] = f"team {pm_t1} might be {similar}"
                result['reason'] = f"Team code mismatch: PM uses '{pm_t1}', Kalshi might use '{similar}'"
                result['reason_type'] = 'team_code_mismatch'
                mapping_var = f"{pm_sport.upper()}_PM2K"
                result['fix'] = f"Add {mapping_var}['...'] = '{similar}' for team {pm_t1}"
                return result

        elif not t2_found:
            # Only t2 missing
            similar = find_similar_team(pm_sport, pm_t2, kalshi_team_lookup)
            if similar:
                result['closest_key'] = f"team {pm_t2} might be {similar}"
                result['reason'] = f"Team code mismatch: PM uses '{pm_t2}', Kalshi might use '{similar}'"
                result['reason_type'] = 'team_code_mismatch'
                mapping_var = f"{pm_sport.upper()}_PM2K"
                result['fix'] = f"Add {mapping_var}['...'] = '{similar}' for team {pm_t2}"
                return result

    # Check 4: Game exists but with different team combination?
    result['reason'] = "Game not listed on Kalshi (teams exist but not this matchup)"
    result['reason_type'] = 'game_not_on_kalshi'
    return result


def find_similar_teams(pm_sport: str, pm_team_codes: List[str],
                       kalshi_team_lookup: Dict, date_keys: List[str]) -> Optional[Dict]:
    """Find similar team codes that might be mismatched"""
    if len(pm_team_codes) < 2:
        return None

    pm_t1, pm_t2 = pm_team_codes[0].upper(), pm_team_codes[1].upper()

    # Check date_keys for teams that are similar
    for k in date_keys:
        parts = k.split(':')
        if len(parts) >= 2:
            teams_str = parts[1]
            k_teams = teams_str.split('-')
            if len(k_teams) >= 2:
                k_t1, k_t2 = k_teams[0].upper(), k_teams[1].upper()

                # Check if one team matches and another is similar
                if pm_t1 == k_t1 or pm_t1 == k_t2:
                    other_pm = pm_t2
                    other_k = k_t2 if pm_t1 == k_t1 else k_t1
                    if other_pm != other_k and (other_pm in other_k or other_k in other_pm or
                                                 levenshtein_close(other_pm, other_k)):
                        return {
                            'key': k,
                            'pm_code': other_pm,
                            'k_code': other_k,
                            'pm_name': other_pm  # Would need outcome name lookup
                        }

                if pm_t2 == k_t1 or pm_t2 == k_t2:
                    other_pm = pm_t1
                    other_k = k_t1 if pm_t2 == k_t2 else k_t2
                    if other_pm != other_k and (other_pm in other_k or other_k in other_pm or
                                                 levenshtein_close(other_pm, other_k)):
                        return {
                            'key': k,
                            'pm_code': other_pm,
                            'k_code': other_k,
                            'pm_name': other_pm
                        }

    return None


def find_similar_team(pm_sport: str, pm_team: str, kalshi_team_lookup: Dict) -> Optional[str]:
    """Find a similar team code in Kalshi"""
    pm_upper = pm_team.upper()

    # Get all teams for this sport
    sport_teams = [k.split(':')[1] for k in kalshi_team_lookup if k.startswith(pm_sport + ':')]

    for k_team in sport_teams:
        if pm_upper in k_team or k_team in pm_upper:
            return k_team
        if levenshtein_close(pm_upper, k_team):
            return k_team

    return None


def levenshtein_close(s1: str, s2: str, threshold: int = 2) -> bool:
    """Check if two strings are within edit distance threshold"""
    if abs(len(s1) - len(s2)) > threshold:
        return False

    # Simple check: count character differences
    if len(s1) != len(s2):
        return False

    diffs = sum(1 for a, b in zip(s1, s2) if a != b)
    return diffs <= threshold


async def discover_kalshi_series(session, kalshi_api):
    """Discover available Kalshi series - run once to find CBB ticker"""
    print("\n[KALSHI SERIES DISCOVERY]")
    print("=" * 60)

    series_list = []

    # Step 1: List all series and save to file
    try:
        path = '/trade-api/v2/series'
        async with session.get(
            f'{kalshi_api.BASE_URL}{path}',
            headers=kalshi_api._headers('GET', path),
            timeout=aiohttp.ClientTimeout(total=30)
        ) as r:
            if r.status == 200:
                data = await r.json()
                series_list = data.get('series', [])
                print(f"Found {len(series_list)} total series")

                # Save full series list to file for analysis
                with open('kalshi_series.txt', 'w', encoding='utf-8') as f:
                    f.write(f"# Kalshi Series List - {len(series_list)} total\n")
                    f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                    for s in sorted(series_list, key=lambda x: x.get('ticker', '')):
                        ticker = s.get('ticker', '')
                        title = s.get('title', '')
                        category = s.get('category', '')
                        f.write(f"{ticker}\t{title}\t{category}\n")
                print(f"Saved series list to kalshi_series.txt")
            else:
                print(f"Failed to list series: HTTP {r.status}")
                return
    except Exception as e:
        print(f"Error listing series: {e}")
        return

    # Step 2: Search for CBB-related keywords
    print("\n[SEARCHING FOR CBB-RELATED SERIES]")
    cbb_keywords = ['college', 'ncaa', 'basketball', 'cbb', 'mbb', 'march', 'madness']

    matching_series = []
    for s in series_list:
        ticker = s.get('ticker', '').lower()
        title = s.get('title', '').lower()
        category = s.get('category', '').lower()
        searchable = f"{ticker} {title} {category}"

        for keyword in cbb_keywords:
            if keyword in searchable:
                matching_series.append({
                    'ticker': s.get('ticker'),
                    'title': s.get('title'),
                    'category': s.get('category'),
                    'matched_keyword': keyword
                })
                break

    if matching_series:
        print(f"Found {len(matching_series)} series matching CBB keywords:")
        for m in matching_series:
            # Handle Unicode characters safely
            title = m['title'].encode('ascii', 'replace').decode('ascii')
            category = m['category'].encode('ascii', 'replace').decode('ascii')
            print(f"  [{m['matched_keyword']}] {m['ticker']}: {title} ({category})")
    else:
        print("No series found matching CBB keywords")

    # Step 3: Test matching series for actual markets (with delays)
    if matching_series:
        print("\n[TESTING MATCHING SERIES FOR MARKETS]")
        for m in matching_series[:10]:  # Limit to 10 to avoid rate limits
            series = m['ticker']
            try:
                await asyncio.sleep(1)  # 1-second delay between API calls
                path = f'/trade-api/v2/markets?series_ticker={series}&limit=10'
                async with session.get(
                    f'{kalshi_api.BASE_URL}{path}',
                    headers=kalshi_api._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        markets = data.get('markets', [])
                        if markets:
                            print(f"  [OK] {series}: {len(markets)} markets")
                            sample = markets[0]
                            title = sample.get('title', '').encode('ascii', 'replace').decode('ascii')[:50]
                            print(f"    Sample: {sample.get('ticker')} - {title}")
                        else:
                            print(f"  [X] {series}: 0 markets")
                    elif r.status == 429:
                        print(f"  ! Rate limited - waiting 5 seconds...")
                        await asyncio.sleep(5)
                    else:
                        print(f"  [X] {series}: HTTP {r.status}")
            except Exception as e:
                print(f"  [X] {series}: error - {e}")

    # Step 4: Try fetching markets directly and search titles for college basketball
    print("\n[SEARCHING ALL MARKETS FOR COLLEGE BASKETBALL]")
    try:
        await asyncio.sleep(1)
        path = '/trade-api/v2/markets?limit=200&status=open'
        async with session.get(
            f'{kalshi_api.BASE_URL}{path}',
            headers=kalshi_api._headers('GET', path),
            timeout=aiohttp.ClientTimeout(total=30)
        ) as r:
            if r.status == 200:
                data = await r.json()
                all_markets = data.get('markets', [])
                print(f"Fetched {len(all_markets)} open markets")

                # Search for college basketball in titles
                cbb_markets = []
                for m in all_markets:
                    title = m.get('title', '').lower()
                    subtitle = m.get('subtitle', '').lower()
                    ticker = m.get('ticker', '')
                    searchable = f"{title} {subtitle} {ticker}"

                    if any(kw in searchable for kw in ['college', 'ncaa', 'cbb', 'march madness']):
                        cbb_markets.append(m)

                if cbb_markets:
                    print(f"\nFound {len(cbb_markets)} college basketball markets:")
                    # Group by series ticker
                    series_map = {}
                    for m in cbb_markets:
                        series = m.get('series_ticker', 'unknown')
                        if series not in series_map:
                            series_map[series] = []
                        series_map[series].append(m)

                    for series, markets in series_map.items():
                        print(f"\n  Series: {series} ({len(markets)} markets)")
                        for m in markets[:3]:
                            title = m.get('title', '').encode('ascii', 'replace').decode('ascii')[:60]
                            print(f"    - {m.get('ticker')}: {title}")
                else:
                    print("No college basketball markets found in open markets")

                    # Show what sports markets we DO have
                    print("\nSports markets found (by series):")
                    sports_prefixes = ['KXNBA', 'KXNHL', 'KXMLB', 'KXNFL', 'KXCBB', 'KXNCAA']
                    series_counts = {}
                    for m in all_markets:
                        series = m.get('series_ticker', '')
                        for prefix in sports_prefixes:
                            if series.startswith(prefix):
                                series_counts[series] = series_counts.get(series, 0) + 1

                    for series, count in sorted(series_counts.items()):
                        print(f"  {series}: {count} markets")
            else:
                print(f"Failed to fetch markets: HTTP {r.status}")
    except Exception as e:
        print(f"Error fetching markets: {e}")

    print("\n" + "=" * 60 + "\n")


async def fetch_kalshi_markets(session, kalshi_api, debug: bool = False):
    """Fetch all sports markets from Kalshi - FRESH data on every call"""
    async def fetch_series(series):
        # Use status=open to get only tradeable markets (returns status='active' in response)
        # This is more efficient than fetching all and filtering locally
        all_markets = []
        cursor = None

        # Paginate to get all markets (CBB has 176+)
        for page in range(5):  # Max 5 pages = 1000 markets
            path = f'/trade-api/v2/markets?series_ticker={series}&status=open&limit=200'
            if cursor:
                path += f'&cursor={cursor}'

            try:
                async with session.get(
                    f'{kalshi_api.BASE_URL}{path}',
                    headers=kalshi_api._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        markets = data.get('markets', [])
                        all_markets.extend(markets)
                        cursor = data.get('cursor', '')

                        if not cursor or not markets:
                            break  # No more pages
                    else:
                        if debug:
                            text = await r.text()
                            print(f"[DEBUG KALSHI] {series}: HTTP {r.status} - {text[:200]}")
                        break
            except Exception as e:
                if debug:
                    print(f"[DEBUG KALSHI] {series} page {page}: ERROR - {e}")
                break

        if debug:
            print(f"[DEBUG KALSHI] {series}: {len(all_markets)} tradeable markets")
            if all_markets:
                sample = all_markets[0]
                print(f"  Sample: {sample.get('ticker')} status={sample.get('status')}")
                print(f"  yes_bid={sample.get('yes_bid')} yes_ask={sample.get('yes_ask')}")
                print(f"  last_price={sample.get('last_price')} close_time={sample.get('close_time')}")

        return series, all_markets

    results = await asyncio.gather(*[fetch_series(c['series']) for c in SPORTS_CONFIG])
    return {s: m for s, m in results}


async def fetch_pm_us_markets(session, pm_api, debug: bool = False):
    """
    Fetch PM US moneyline markets and build the match cache.
    Now fetches actual order book bid/ask instead of using stale outcomePrices.
    Returns count of matched markets.
    """
    global PM_US_MARKET_CACHE

    # CRITICAL: Clear cache on every scan to avoid stale data
    PM_US_MARKET_CACHE.clear()

    raw_markets = await pm_api.get_moneyline_markets(session, debug=debug)
    if not raw_markets:
        return 0

    # =========================================================================
    # FILTER: Remove old/settled games - we only care about tradeable markets
    # =========================================================================
    # Use timezone-naive comparison - PM US game times are in UTC
    # We convert everything to naive UTC for comparison
    from datetime import timezone
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff_time = now_utc - timedelta(hours=24)  # Games > 24h old are definitely settled

    markets = []
    filtered_count = 0
    filter_reasons = {'old': 0, 'settled': 0, 'closed': 0}

    for m in raw_markets:
        game_time_str = m.get('gameStartTime', '')
        market_status = m.get('status', '').lower()
        is_closed = m.get('closed', False)
        is_active = m.get('active', True)

        # Skip settled or closed markets
        if market_status in ['settled', 'resolved', 'closed']:
            filtered_count += 1
            filter_reasons['settled'] += 1
            continue
        if is_closed:
            filtered_count += 1
            filter_reasons['closed'] += 1
            continue

        # Skip old games (> 24 hours past start time)
        if game_time_str:
            try:
                # Parse ISO format with Z suffix (UTC)
                game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                # Convert to naive UTC for comparison
                if game_time.tzinfo:
                    game_time = game_time.replace(tzinfo=None)
                if game_time < cutoff_time:
                    filtered_count += 1
                    filter_reasons['old'] += 1
                    continue
            except (ValueError, TypeError):
                pass  # Keep markets with unparseable dates

        markets.append(m)

    if debug or filtered_count > 0:
        reasons_str = ', '.join(f"{v} {k}" for k, v in filter_reasons.items() if v > 0)
        print(f"[PM US] Fetched {len(raw_markets)} markets, filtered to {len(markets)} active ({reasons_str})")

    # PHASE 1: Match markets to teams and collect slugs
    matched_markets = []  # List of {cache_key, slug, team_0, team_1, outcome_idx_0, outcome_idx_1, volume}
    unmatched_details = []  # Detailed info about unmatched markets
    all_pm_markets = []  # Track ALL markets for debug report

    for market in markets:
        slug = market.get('slug', '')
        outcomes_raw = market.get('outcomes', '[]')
        prices_raw = market.get('outcomePrices', '[]')  # NOTE: These are mid/last prices, not order book
        game_time = market.get('gameStartTime', '')

        # Parse JSON strings if needed
        try:
            outcomes = json.loads(outcomes_raw) if isinstance(outcomes_raw, str) else outcomes_raw
            prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
        except (json.JSONDecodeError, TypeError):
            continue

        # Only handle 2-outcome moneyline markets
        if not outcomes or not prices or len(outcomes) != 2 or len(prices) != 2:
            if debug:
                all_pm_markets.append({
                    'slug': slug,
                    'outcomes': outcomes if outcomes else [],
                    'status': 'SKIP_NOT_2_OUTCOME',
                    'reason': f"outcomes={len(outcomes) if outcomes else 0}, prices={len(prices) if prices else 0}"
                })
            continue

        # Track this market for debug
        market_info = {
            'slug': slug,
            'outcomes': outcomes,
            'game_time': game_time,
            'status': 'UNMATCHED',
            'reason': 'No team mapping found',
            'tried_sports': []
        }

        # =====================================================================
        # CRITICAL: Extract team codes from SLUG for CBB
        # The slug format is: aec-{sport}-{team1}-{team2}-{date}
        # Slug is the SOURCE OF TRUTH - never trust mascot names for CBB!
        # Mascot matching causes bugs like "Harvard Crimson" -> BAMA (crimson tide)
        # =====================================================================
        slug_teams = None
        slug_sport = None
        slug_parts = slug.lower().split('-')
        if len(slug_parts) >= 4:
            # Check for sport identifier in slug
            if 'cbb' in slug_parts or 'ncaab' in slug_parts:
                slug_sport = 'cbb'
                # Extract team codes from slug positions after sport
                sport_idx = slug_parts.index('cbb') if 'cbb' in slug_parts else slug_parts.index('ncaab')
                if sport_idx + 2 < len(slug_parts):
                    raw_team1 = slug_parts[sport_idx + 1].upper()
                    raw_team2 = slug_parts[sport_idx + 2].upper()
                    # Validate they look like team codes (not dates like "2026")
                    if not raw_team1.isdigit() and not raw_team2.isdigit():
                        slug_teams = (raw_team1, raw_team2)
            elif 'nba' in slug_parts:
                slug_sport = 'nba'
                sport_idx = slug_parts.index('nba')
                if sport_idx + 2 < len(slug_parts):
                    raw_team1 = slug_parts[sport_idx + 1].upper()
                    raw_team2 = slug_parts[sport_idx + 2].upper()
                    if not raw_team1.isdigit() and not raw_team2.isdigit():
                        slug_teams = (raw_team1, raw_team2)
            elif 'nhl' in slug_parts:
                slug_sport = 'nhl'
                sport_idx = slug_parts.index('nhl')
                if sport_idx + 2 < len(slug_parts):
                    raw_team1 = slug_parts[sport_idx + 1].upper()
                    raw_team2 = slug_parts[sport_idx + 2].upper()
                    if not raw_team1.isdigit() and not raw_team2.isdigit():
                        slug_teams = (raw_team1, raw_team2)

        # Try to match outcomes to known teams across all sports
        matched_this_market = False

        # DEBUG: Detailed tracing for specific games
        is_debug_market = any(x in slug.upper() for x in ['WAS', 'DET', 'WSH'])
        if is_debug_market and debug:
            print(f"\n[DEBUG PM OUTCOMES] {slug}")
            print(f"  outcomes array: {outcomes}")
            print(f"  prices array: {prices}")
            print(f"  slug_teams: {slug_teams}")

        # =====================================================================
        # CRITICAL: When slug tells us the sport, ONLY process that sport!
        # Otherwise NHL mascot matching ("Sharks" -> SJ) hijacks CBB markets.
        # =====================================================================
        configs_to_try = SPORTS_CONFIG
        if slug_sport:
            # Filter to only the sport detected from slug
            configs_to_try = [cfg for cfg in SPORTS_CONFIG if cfg['sport'] == slug_sport]
            if not configs_to_try:
                # Fallback if sport not in config (shouldn't happen)
                configs_to_try = SPORTS_CONFIG

        for cfg in configs_to_try:
            team_0 = None
            team_1 = None

            # =====================================================================
            # CBB: ALWAYS use slug extraction - mascot names are unreliable!
            # Mascot matching causes bugs like:
            #   "Harvard Crimson" -> BAMA (because "crimson" matches "crimson tide")
            #   "Brown Bears" -> BAY (because "bears" matches Baylor)
            #   "Sharks" -> SJ (NHL San Jose instead of CBB LIU)
            # =====================================================================
            if cfg['sport'] == 'cbb' and slug_teams:
                raw_0, raw_1 = slug_teams[0], slug_teams[1]
                # Apply SLUG_TO_KALSHI mapping to normalize codes
                team_0 = SLUG_TO_KALSHI.get(raw_0, raw_0)
                team_1 = SLUG_TO_KALSHI.get(raw_1, raw_1)
                if debug:
                    if raw_0 != team_0 or raw_1 != team_1:
                        print(f"[CBB SLUG->KALSHI] {slug}: {raw_0}->{team_0}, {raw_1}->{team_1}")
                    else:
                        print(f"[CBB SLUG] {slug}: {team_0} vs {team_1}")
            elif cfg['sport'] in ['nba', 'nhl'] and slug_teams:
                # NBA/NHL: Also prefer slug extraction when available
                raw_0, raw_1 = slug_teams[0], slug_teams[1]
                team_0 = SLUG_TO_KALSHI.get(raw_0, raw_0)
                team_1 = SLUG_TO_KALSHI.get(raw_1, raw_1)
                if debug:
                    print(f"[{cfg['sport'].upper()} SLUG] {slug}: {team_0} vs {team_1}")
            else:
                # Fallback: Use mascot matching (only when no slug teams)
                team_0 = map_outcome_to_kalshi(outcomes[0], cfg['pm2k'], cfg['sport'])
                team_1 = map_outcome_to_kalshi(outcomes[1], cfg['pm2k'], cfg['sport'])

            if is_debug_market and debug and cfg['sport'] == 'nhl':
                print(f"  [{cfg['sport']}] '{outcomes[0]}' -> '{team_0}'")
                print(f"  [{cfg['sport']}] '{outcomes[1]}' -> '{team_1}'")

            market_info['tried_sports'].append({
                'sport': cfg['sport'],
                'team_0_in': outcomes[0],
                'team_0_out': team_0,
                'team_1_in': outcomes[1],
                'team_1_out': team_1,
                'slug_extracted': slug_teams if cfg['sport'] == 'cbb' and slug_sport == 'cbb' else None
            })

            if team_0 and team_1:
                matched_this_market = True
                # Extract game date from gameStartTime - CONVERT UTC TO EST
                # PM US uses UTC, Kalshi uses EST. A 7pm EST game shows as midnight UTC next day.
                # IMPORTANT: Use EXACT date matching only - no +/- 1 day variants
                # This prevents cross-matching when teams play back-to-back days
                game_date = None
                if game_time:
                    try:
                        dt_str = game_time.replace('Z', '+00:00')
                        if 'T' in dt_str:
                            dt_utc = datetime.fromisoformat(dt_str)
                        else:
                            dt_utc = datetime.strptime(dt_str[:10], '%Y-%m-%d')
                            dt_utc = dt_utc.replace(tzinfo=None)

                        # Convert UTC to EST (UTC - 5 hours)
                        # Note: This is simplified - doesn't handle DST. EST is always UTC-5.
                        if dt_utc.tzinfo:
                            dt_utc = dt_utc.replace(tzinfo=None)  # Remove timezone for arithmetic
                        dt_est = dt_utc - timedelta(hours=5)

                        # Use ONLY the EST date - exact matching
                        game_date = dt_est.strftime('%Y-%m-%d')

                        if debug and len(matched_markets) < 5:
                            print(f"[DEBUG TZ] {slug}: UTC={game_time} -> EST={game_date}")

                    except (ValueError, TypeError) as e:
                        if debug:
                            print(f"[DEBUG TZ] Failed to parse {game_time}: {e}")
                        pass

                if not game_date:
                    market_info['status'] = 'UNMATCHED'
                    market_info['reason'] = 'Could not parse game date'
                    continue

                sport = cfg['sport']
                sorted_teams = sorted([team_0, team_1])

                # Store mid prices as fallback (but we'll prefer order book)
                mid_price_0 = int(float(prices[0]) * 100)
                mid_price_1 = int(float(prices[1]) * 100)

                # Create single cache entry with exact EST date (no date variants)
                cache_key = f"{sport}:{sorted_teams[0]}-{sorted_teams[1]}:{game_date}"

                matched_markets.append({
                    'cache_key': cache_key,
                    'slug': slug,
                    'team_0': team_0,
                    'team_1': team_1,
                    'mid_price_0': mid_price_0,
                    'mid_price_1': mid_price_1,
                    'volume': market.get('volumeNum', 0) or market.get('volume24hr', 0) or 0,
                })

                # Update market info for debug
                market_info['status'] = 'MATCHED'
                market_info['sport'] = sport
                market_info['cache_key'] = cache_key
                market_info['team_0'] = team_0
                market_info['team_1'] = team_1
                market_info['game_date_est'] = game_date
                market_info['reason'] = None
                break

        # Track for debug report
        if debug:
            all_pm_markets.append(market_info)
            if market_info['status'] == 'UNMATCHED':
                unmatched_details.append(market_info)

    # Count unique markets
    unique_slugs = set(m['slug'] for m in matched_markets)

    # Generate detailed matching report
    if debug:
        print(f"\n" + "=" * 70)
        print("[MATCHING REPORT]")
        print("=" * 70)
        total_pm = len(all_pm_markets)
        matched_count = len([m for m in all_pm_markets if m['status'] == 'MATCHED'])
        unmatched_count = len([m for m in all_pm_markets if m['status'] == 'UNMATCHED'])
        skipped_count = len([m for m in all_pm_markets if m['status'].startswith('SKIP')])

        print(f"PM US Markets Total: {total_pm}")
        print(f"  Matched: {matched_count} ({matched_count/total_pm*100:.1f}%)" if total_pm > 0 else "  Matched: 0")
        print(f"  Unmatched: {unmatched_count}")
        print(f"  Skipped (not 2-outcome): {skipped_count}")

        # Show ALL PM US markets
        print(f"\n[ALL PM US MARKETS]")
        for i, m in enumerate(all_pm_markets[:50], 1):  # Limit to 50
            status_icon = "[OK]" if m['status'] == 'MATCHED' else "[X]"
            if m['status'] == 'MATCHED':
                print(f"  {i:2}. {status_icon} {m['slug'][:50]}")
                print(f"       Teams: {m['outcomes']} -> {m.get('team_0', '?')}/{m.get('team_1', '?')}")
                print(f"       Date: {m.get('game_date_est', '?')} | Key: {m.get('cache_key', '?')}")
            else:
                print(f"  {i:2}. {status_icon} {m['slug'][:50]}")
                print(f"       Outcomes: {m['outcomes']}")
                print(f"       Reason: {m['reason']}")
                # Show what teams we tried to map
                if m.get('tried_sports'):
                    for ts in m['tried_sports']:
                        if ts['team_0_out'] or ts['team_1_out']:
                            print(f"       {ts['sport'].upper()}: '{ts['team_0_in']}'->{ts['team_0_out'] or 'NONE'}, '{ts['team_1_in']}'->{ts['team_1_out'] or 'NONE'}")

        # Team mapping issues
        print(f"\n[TEAM MAPPING ISSUES]")
        mapping_issues = []
        for m in unmatched_details:
            for ts in m.get('tried_sports', []):
                if ts['team_0_out'] and not ts['team_1_out']:
                    mapping_issues.append(f"  '{ts['team_1_in']}' not mapped for {ts['sport'].upper()}")
                elif ts['team_1_out'] and not ts['team_0_out']:
                    mapping_issues.append(f"  '{ts['team_0_in']}' not mapped for {ts['sport'].upper()}")
                elif not ts['team_0_out'] and not ts['team_1_out']:
                    # Check if it looks like a sport we support
                    slug = m['slug'].lower()
                    if 'nba' in slug or 'nhl' in slug:
                        mapping_issues.append(f"  '{ts['team_0_in']}' and '{ts['team_1_in']}' not mapped for {ts['sport'].upper()}")

        if mapping_issues:
            for issue in set(mapping_issues):
                print(issue)
        else:
            print("  No obvious mapping issues found")

        print("=" * 70 + "\n")

    if not matched_markets:
        return 0

    # PHASE 2: Fetch order books for all matched markets (deduplicated by slug)
    slugs = list(unique_slugs)
    if debug:
        print(f"[PM US] Phase 2: Fetching order books for {len(slugs)} unique markets...")

    orderbooks = await pm_api.get_orderbooks_batch(session, slugs, debug=debug)

    if debug:
        print(f"[PM US] Phase 2: Got {len(orderbooks)} order books")

    # PHASE 3: Build cache with real bid/ask from order books
    # Multiple cache keys may point to the same slug (date variants for fuzzy matching)
    matched = 0
    no_orderbook = 0
    seen_slugs = set()  # Track unique slugs for counting

    for m in matched_markets:
        slug = m['slug']
        cache_key = m['cache_key']
        team_0, team_1 = m['team_0'], m['team_1']

        ob = orderbooks.get(slug)

        if ob and ob.get('best_bid') is not None and ob.get('best_ask') is not None:
            # Use real order book prices (convert to cents)
            best_bid = int(ob['best_bid'] * 100) if ob['best_bid'] < 1 else int(ob['best_bid'])
            best_ask = int(ob['best_ask'] * 100) if ob['best_ask'] < 1 else int(ob['best_ask'])
            bid_size = ob.get('bid_size', 0)
            ask_size = ob.get('ask_size', 0)

            # CRITICAL: PM US order book is for the FIRST team in the SLUG, not outcomes[0]
            # Slug format: aec-{sport}-{team1}-{team2}-{date}
            # We need to determine if the order book team matches team_0 or team_1

            # DEBUG: Check if this is a slug we want to trace
            is_debug_slug = any(x in slug.upper() for x in ['WAS', 'DET', 'WSH', 'WSHDET', 'DETWSH', 'UMBC', 'VERM', 'UVM'])

            # Use global SLUG_TO_KALSHI mapping for team code normalization
            def normalize_slug_team(slug_code: str, kalshi_team: str) -> bool:
                """Check if PM slug team code matches Kalshi team code"""
                slug_upper = slug_code.upper()
                kalshi_upper = kalshi_team.upper()

                # Direct match
                if slug_upper == kalshi_upper:
                    return True

                # Check via mapping table
                mapped = SLUG_TO_KALSHI.get(slug_upper, slug_upper)
                if mapped == kalshi_upper:
                    return True

                # Substring matching (for partial codes)
                if slug_upper in kalshi_upper or kalshi_upper in slug_upper:
                    return True

                return False

            slug_parts = slug.split('-')
            if len(slug_parts) >= 4:
                slug_team1 = slug_parts[2].upper()  # First team in slug
                slug_team2 = slug_parts[3].upper()  # Second team in slug

                # Order book prices are for slug_team1
                # Check which of our mapped teams matches slug_team1
                orderbook_is_for_team_0 = normalize_slug_team(slug_team1, team_0)

                # Double-check: also verify team_1 matches slug_team2 for consistency
                if not orderbook_is_for_team_0:
                    # Verify the assignment makes sense
                    team_1_matches_slug2 = normalize_slug_team(slug_team2, team_0)
                    if team_1_matches_slug2:
                        # team_0 matches slug_team2, so orderbook (slug_team1) is for team_1
                        orderbook_is_for_team_0 = False
                    else:
                        # Neither mapping is clear - log warning and use fallback
                        if is_debug_slug and debug:
                            print(f"  WARNING: Cannot determine team mapping for {slug}")
                            print(f"    slug_team1={slug_team1} slug_team2={slug_team2}")
                            print(f"    team_0={team_0} team_1={team_1}")
                        orderbook_is_for_team_0 = True  # Fallback

            else:
                # Fallback: assume order book is for team_0
                orderbook_is_for_team_0 = True

            if orderbook_is_for_team_0:
                # Order book is for team_0 (normal case)
                ob_team = team_0
                other_team = team_1
                ob_outcome_idx = 0
                other_outcome_idx = 1
            else:
                # Order book is for team_1 - SWAP assignment
                ob_team = team_1
                other_team = team_0
                ob_outcome_idx = 1
                other_outcome_idx = 0

            # DEBUG: Detailed tracing for specific games
            if is_debug_slug and debug:
                print(f"\n[DEBUG PM CACHE] {slug}")
                print(f"  cache_key: {cache_key}")
                print(f"  team_0 (from matching): {team_0}")
                print(f"  team_1 (from matching): {team_1}")
                print(f"  slug_parts: {slug_parts}")
                print(f"  slug_team1 (orderbook team): {slug_team1 if len(slug_parts) >= 4 else 'N/A'}")
                print(f"  slug_team2: {slug_team2 if len(slug_parts) >= 4 else 'N/A'}")
                print(f"  orderbook_is_for_team_0: {orderbook_is_for_team_0}")
                print(f"  -> ob_team={ob_team}, other_team={other_team}")
                print(f"  Raw orderbook: best_bid={best_bid}c best_ask={best_ask}c")
                print(f"  Assigning to '{ob_team}': bid={best_bid} ask={best_ask}")
                print(f"  Assigning to '{other_team}': bid={100-best_ask} ask={100-best_bid}")

            PM_US_MARKET_CACHE[cache_key] = {
                'slug': slug,
                'teams': {
                    ob_team: {
                        'bid': best_bid,           # Price to sell ob_team (sell YES)
                        'ask': best_ask,           # Price to buy ob_team (buy YES)
                        'bid_size': bid_size,
                        'ask_size': ask_size,
                        'outcome_index': ob_outcome_idx
                    },
                    other_team: {
                        'bid': 100 - best_ask,     # Price to sell other_team = 100 - ask for ob_team
                        'ask': 100 - best_bid,     # Price to buy other_team = 100 - bid for ob_team
                        'bid_size': ask_size,      # Sizes are swapped for opposite side
                        'ask_size': bid_size,
                        'outcome_index': other_outcome_idx
                    }
                },
                'volume': m['volume'],
                'has_orderbook': True
            }

            # Only count unique slugs for the "matched" total
            if slug not in seen_slugs:
                matched += 1
                seen_slugs.add(slug)
                if debug and matched <= 3:
                    print(f"[DEBUG OB] {cache_key}: {team_0} bid/ask={best_bid}/{best_ask}c, "
                          f"{team_1} bid/ask={100-best_ask}/{100-best_bid}c")
        else:
            # No order book - use mid prices as fallback but mark as unreliable
            if slug not in seen_slugs:
                no_orderbook += 1
                seen_slugs.add(slug)

            PM_US_MARKET_CACHE[cache_key] = {
                'slug': slug,
                'teams': {
                    team_0: {
                        'bid': m['mid_price_0'],
                        'ask': m['mid_price_0'],
                        'bid_size': 0,
                        'ask_size': 0,
                        'outcome_index': 0
                    },
                    team_1: {
                        'bid': m['mid_price_1'],
                        'ask': m['mid_price_1'],
                        'bid_size': 0,
                        'ask_size': 0,
                        'outcome_index': 1
                    }
                },
                'volume': m['volume'],
                'has_orderbook': False  # Flag: this uses stale mid prices
            }

    if debug:
        print(f"[PM US] Phase 3: {matched} with order book, {no_orderbook} using mid prices (unreliable)")

    # Log unmatched samples for debugging
    if debug and unmatched_details:
        print(f"\n[DEBUG PM US] {len(unmatched_details)} unmatched market details:")
        for um in unmatched_details[:10]:  # Limit to 10
            print(f"  slug: {um['slug']}")
            print(f"  outcomes: {um['outcomes']}")
            print(f"  reason: {um.get('reason', 'unknown')}")

    return matched


async def run_executor():
    print("=" * 70)
    print("ARB EXECUTOR v7 - DIRECT US EXECUTION")
    print(f"Mode: {EXECUTION_MODE.value.upper()}")
    if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
        print("PAPER UNLIMITED: No limits - tracking Total Addressable Market")
        print("  - Full liquidity sizing (no contract cap)")
        print("  - No cooldown between trades")
        print("  - No already-traded restriction")
        print("  - Measuring maximum theoretical profit")
    else:
        print(f"HARD LIMITS: Max {MAX_CONTRACTS} contracts, Max ${MAX_COST_CENTS/100:.0f} per trade")
        print(f"Cooldown: {COOLDOWN_SECONDS}s between trades")
    print(f"PM US Fee: {PM_US_TAKER_FEE_RATE*100:.2f}% taker | Kalshi Fee: {KALSHI_FEE*100:.0f}%")
    print(f"Sports: {', '.join([c['sport'].upper() + '(' + c['series'] + ')' for c in SPORTS_CONFIG])}")
    print("=" * 70)

    if EXECUTION_MODE == ExecutionMode.PAPER:
        print("\n*** PAPER TRADING MODE - NO REAL ORDERS ***\n")

    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)

    last_trade_time = 0
    total_trades = 0
    total_profit = 0.0

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        # Get initial balances
        k_balance = await kalshi_api.get_balance(session)
        pm_balance = await pm_api.get_balance(session, debug=DEBUG_MATCHING)

        if k_balance is not None:
            print(f"Kalshi Balance: ${k_balance:.2f}")
        else:
            print("WARNING: Could not fetch Kalshi balance")

        if pm_balance is not None:
            print(f"PM US Balance: ${pm_balance:.2f}")
        else:
            print("WARNING: Could not fetch PM US balance (check API key)")

        # Discover available Kalshi series (run once with debug)
        if DEBUG_MATCHING:
            await discover_kalshi_series(session, kalshi_api)

        # Get initial Kalshi positions
        k_positions = await kalshi_api.get_positions(session)
        if k_positions:
            print(f"Kalshi positions: {len(k_positions)}")
            for ticker, pos in k_positions.items():
                print(f"  {ticker}: {pos.position} contracts")

        # Get initial PM US positions
        pm_positions = await pm_api.get_positions(session)
        if pm_positions:
            print(f"PM US positions: {len(pm_positions)}")

        # CRITICAL: Cancel ALL stale orders on startup
        if EXECUTION_MODE == ExecutionMode.LIVE:
            print("\n[STARTUP CLEANUP] Checking for stale orders...")
            k_cancelled = await kalshi_api.cancel_all_open_orders(session)
            pm_cancelled = await pm_api.cancel_all_orders(session)
            if k_cancelled > 0:
                print(f"[STARTUP CLEANUP] Cancelled {k_cancelled} stale Kalshi orders")
            if pm_cancelled:
                print(f"[STARTUP CLEANUP] Cancelled {len(pm_cancelled)} stale PM US orders")
            print("[STARTUP CLEANUP] Done - clean slate\n")

        scan_num = 0
        start_time = time.time()
        PAPER_STATS['start_time'] = start_time  # Track paper session start
        cumulative_arbs_found = 0
        cumulative_matches = 0
        last_summary_time = time.time()
        SUMMARY_INTERVAL = 1800  # Print summary every 30 minutes

        # Auto-save initialization
        global LAST_AUTO_SAVE_TIME, LAST_AUTO_SAVE_SCAN, ACTIVATED_MARKETS
        LAST_AUTO_SAVE_TIME = time.time()
        LAST_AUTO_SAVE_SCAN = 0

        # Load activated markets history
        ACTIVATED_MARKETS = load_activated_markets()
        if ACTIVATED_MARKETS:
            stats = get_activation_stats()
            print(f"[PENDING] Loaded {stats.get('count', 0)} activation records")
            if stats.get('avg_hours_before'):
                print(f"  Avg activation: {stats['avg_hours_before']:.1f}h before game "
                      f"(min: {stats['min_hours_before']:.1f}h, max: {stats['max_hours_before']:.1f}h)")

        # Track when we last displayed pending markets (to avoid spam)
        last_pending_display = 0
        PENDING_DISPLAY_INTERVAL = 60  # Show pending every 60 seconds

        while True:
            scan_num += 1
            t0 = time.time()

            # Fetch markets from both platforms in parallel - FRESH data every scan
            is_first_scan = (scan_num == 1)
            kalshi_task = fetch_kalshi_markets(session, kalshi_api, debug=(DEBUG_MATCHING and is_first_scan))
            pm_us_task = fetch_pm_us_markets(session, pm_api, debug=(DEBUG_MATCHING and is_first_scan))
            kalshi_data, pm_us_matched = await asyncio.gather(kalshi_task, pm_us_task)

            # PENDING MARKET MONITORING: Fetch ALL PM US markets including PENDING
            # This runs every scan to detect activations quickly
            all_pm_markets = await pm_api.get_all_markets_including_pending(session, debug=is_first_scan)

            # Process pending markets and detect activations
            pending_markets, newly_activated = process_pending_markets(all_pm_markets, PM_US_MARKET_CACHE)

            # Alert on new activations - these are high priority!
            if newly_activated:
                display_activation_alert(newly_activated, PM_US_MARKET_CACHE)

            # Display pending market status periodically (not every scan to reduce spam)
            now_time = time.time()
            if now_time - last_pending_display >= PENDING_DISPLAY_INTERVAL:
                if pending_markets:
                    display_pending_markets(pending_markets, limit=8)
                last_pending_display = now_time

            # Build game data from Kalshi markets - FRESH on every scan
            all_games = {}
            live_games = []  # Track games that are in-progress

            for cfg in SPORTS_CONFIG:
                sport = cfg['sport']
                all_games[sport] = {}

                for m in kalshi_data.get(cfg['series'], []):
                    parts = m.get('ticker', '').split('-')
                    if len(parts) >= 3:
                        gid, team = parts[1], parts[2]
                        if team == 'TIE':
                            continue

                        # Detect live/in-progress games (conservative - avoid false positives)
                        market_status = m.get('status', 'open')
                        close_time_str = m.get('close_time', '')
                        is_live = False
                        live_reason = ""

                        # Parse game date from gid - e.g., "26JAN30DETGSW" -> "2026-01-30"
                        game_date_str, _, _ = parse_gid(gid)
                        today_str = datetime.now().strftime('%Y-%m-%d')

                        # CRITICAL: Compare dates first - future games are NEVER live
                        if game_date_str and today_str:
                            if game_date_str > today_str:
                                # Future game - NOT live regardless of market status
                                is_live = False
                                live_reason = "future"
                            elif game_date_str < today_str:
                                # Past game - already over, not live
                                is_live = False
                                live_reason = "past"
                            else:
                                # Game is TODAY - check if currently in progress
                                if market_status == 'active':
                                    is_live = True
                                    live_reason = "active_status"
                                elif close_time_str:
                                    try:
                                        close_time = datetime.fromisoformat(close_time_str.replace('Z', '+00:00'))
                                        now = datetime.now(close_time.tzinfo) if close_time.tzinfo else datetime.now()
                                        # Estimate game start: close_time - 4 hours (typical game duration buffer)
                                        estimated_start = close_time - timedelta(hours=4)
                                        # Game is LIVE if: current time > estimated start AND before close
                                        if estimated_start <= now < close_time:
                                            is_live = True
                                            live_reason = f"time_window ({estimated_start.strftime('%H:%M')}-{close_time.strftime('%H:%M')})"
                                        else:
                                            live_reason = f"today_not_started (now={now.strftime('%H:%M')}, start={estimated_start.strftime('%H:%M')})"
                                    except Exception as e:
                                        live_reason = f"parse_error: {e}"

                        # Debug output for first scan - show first 5 games processed
                        if DEBUG_MATCHING and is_first_scan and sum(len(g) for g in all_games.values()) < 5:
                            print(f"[DEBUG LIVE] {gid}: game_date={game_date_str}, today={today_str}, status={market_status} -> {'LIVE' if is_live else 'NOT LIVE'} ({live_reason})")

                        if gid not in all_games[sport]:
                            date, _, _ = parse_gid(gid)
                            all_games[sport][gid] = {
                                'date': date,
                                'teams': {},
                                'tickers': {},
                                'is_live': is_live
                            }
                        elif is_live:
                            all_games[sport][gid]['is_live'] = True

                        # Store FRESH Kalshi prices
                        k_bid = m.get('yes_bid', 0)
                        k_ask = m.get('yes_ask', 0)

                        all_games[sport][gid]['teams'][team] = {
                            'k_bid': k_bid,
                            'k_ask': k_ask,
                            'k_volume': m.get('volume', 0) or 0,
                            'k_status': market_status,
                            'k_last_price': m.get('last_price', 0)
                        }
                        all_games[sport][gid]['tickers'][team] = m.get('ticker')

                        # Track live games for warning
                        if is_live and gid not in [g[1] for g in live_games]:
                            live_games.append((sport, gid, k_bid, k_ask))

            # Warn about live games
            if live_games:
                print(f"\n[!!! LIVE GAMES !!!] {len(live_games)} games IN PROGRESS - prices changing rapidly!")
                for sport, gid, bid, ask in live_games[:3]:
                    print(f"  {sport.upper()}: {gid} - current bid/ask: {bid}/{ask}c")

            # Match Kalshi games to PM US markets
            total_matched = 0
            unmatched_kalshi = []  # For debug logging

            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    if len(game['teams']) < 2 or not game['date']:
                        continue

                    teams = sorted(list(game['teams'].keys()))
                    cache_key = f"{cfg['sport']}:{teams[0]}-{teams[1]}:{game['date']}"

                    pm_market = PM_US_MARKET_CACHE.get(cache_key)
                    if pm_market:
                        # Skip markets without real order book data
                        if not pm_market.get('has_orderbook', False):
                            continue  # Don't count as matched - no reliable bid/ask

                        total_matched += 1
                        for team in game['teams']:
                            if team in pm_market['teams']:
                                pm_info = pm_market['teams'][team]

                                # Use REAL order book bid/ask
                                pm_bid = pm_info.get('bid', 0)   # Price to SELL this team
                                pm_ask = pm_info.get('ask', 0)   # Price to BUY this team
                                bid_size = pm_info.get('bid_size', 0)
                                ask_size = pm_info.get('ask_size', 0)
                                outcome_idx = pm_info['outcome_index']

                                # Only include if we have valid prices
                                if pm_bid <= 0 or pm_ask <= 0:
                                    continue

                                game['teams'][team]['pm_ask'] = pm_ask      # Cost to buy this team
                                game['teams'][team]['pm_bid'] = pm_bid      # Price to sell this team
                                game['teams'][team]['pm_bid_size'] = bid_size
                                game['teams'][team]['pm_ask_size'] = ask_size
                                game['teams'][team]['pm_slug'] = pm_market['slug']
                                game['teams'][team]['pm_outcome_index'] = outcome_idx
                                game['teams'][team]['pm_volume'] = pm_market.get('volume', 0)

                                # Track price history for matched games
                                k_bid = game['teams'][team].get('k_bid', 0)
                                k_ask = game['teams'][team].get('k_ask', 0)
                                if k_bid > 0 and k_ask > 0 and pm_bid > 0 and pm_ask > 0:
                                    # Calculate spreads (can be negative)
                                    spread_buy_pm = k_bid - pm_ask  # Buy PM, sell Kalshi
                                    spread_buy_k = pm_bid - k_ask   # Buy Kalshi, sell PM
                                    # Rough fee estimate: ~2 cents total
                                    has_arb = (spread_buy_pm > 2) or (spread_buy_k > 2)

                                    price_key = f"{cfg['sport']}:{gid}:{team}"
                                    if price_key not in PRICE_HISTORY:
                                        PRICE_HISTORY[price_key] = []

                                    PRICE_HISTORY[price_key].append(PriceSnapshot(
                                        timestamp=time.time(),
                                        scan_num=scan_num,
                                        kalshi_bid=k_bid,
                                        kalshi_ask=k_ask,
                                        pm_bid=pm_bid,
                                        pm_ask=pm_ask,
                                        spread_buy_pm=spread_buy_pm,
                                        spread_buy_k=spread_buy_k,
                                        has_arb=has_arb
                                    ))
                    else:
                        # Collect unmatched for debugging
                        if len(unmatched_kalshi) < 5:
                            unmatched_kalshi.append({
                                'sport': cfg['sport'],
                                'gid': gid,
                                'teams': teams,
                                'date': game['date'],
                                'cache_key': cache_key
                            })

            # Debug: Log cache keys for diagnosis (first scan only)
            if DEBUG_MATCHING and scan_num == 1:
                # Collect ALL Kalshi cache keys
                kalshi_keys = set()
                for cfg in SPORTS_CONFIG:
                    for gid, game in all_games[cfg['sport']].items():
                        if len(game['teams']) >= 2 and game['date']:
                            teams = sorted(list(game['teams'].keys()))
                            kalshi_keys.add(f"{cfg['sport']}:{teams[0]}-{teams[1]}:{game['date']}")

                pm_keys = set(PM_US_MARKET_CACHE.keys())

                # Find keys that match vs don't match
                matched_keys = kalshi_keys & pm_keys
                kalshi_only = kalshi_keys - pm_keys
                pm_only = pm_keys - kalshi_keys

                print(f"\n[DEBUG CACHE KEYS] Kalshi: {len(kalshi_keys)} | PM US: {len(pm_keys)} | Matched: {len(matched_keys)}")

                if matched_keys:
                    print(f"[DEBUG] MATCHED keys: {list(matched_keys)[:5]}")

                if kalshi_only:
                    print(f"\n[DEBUG] KALSHI ONLY (no PM match) - {len(kalshi_only)} keys:")
                    # Group by date to show the pattern
                    kalshi_dates = {}
                    for k in kalshi_only:
                        parts = k.split(':')
                        if len(parts) >= 3:
                            date = parts[2]
                            if date not in kalshi_dates:
                                kalshi_dates[date] = []
                            kalshi_dates[date].append(k)
                    for date in sorted(kalshi_dates.keys())[:3]:
                        print(f"  {date}: {kalshi_dates[date][:3]}")

                if pm_only:
                    print(f"\n[DEBUG] PM US ONLY (no Kalshi match) - {len(pm_only)} keys:")
                    # Group by date to show the pattern
                    pm_dates = {}
                    for k in pm_only:
                        parts = k.split(':')
                        if len(parts) >= 3:
                            date = parts[2]
                            if date not in pm_dates:
                                pm_dates[date] = []
                            pm_dates[date].append(k)
                    for date in sorted(pm_dates.keys())[:3]:
                        print(f"  {date}: {pm_dates[date][:3]}")

                    # For each PM-only key, try to find closest Kalshi match
                    print(f"\n[DEBUG] CLOSEST KALSHI MATCHES for PM-only keys:")
                    for pm_key in list(pm_only)[:10]:
                        pm_parts = pm_key.split(':')
                        if len(pm_parts) >= 3:
                            pm_sport, pm_teams, pm_date = pm_parts[0], pm_parts[1], pm_parts[2]
                            # Find Kalshi keys with same sport
                            same_sport = [k for k in kalshi_keys if k.startswith(pm_sport + ':')]
                            # Find keys with same teams (different date)
                            same_teams = [k for k in same_sport if pm_teams in k]
                            # Find keys with same date (different teams)
                            same_date = [k for k in same_sport if pm_date in k]

                            print(f"  PM: {pm_key}")
                            if same_teams:
                                print(f"    -> Same teams, diff date: {same_teams[:2]}")
                            if same_date and not same_teams:
                                print(f"    -> Same date, diff teams: {same_date[:2]}")
                            if not same_teams and not same_date:
                                print(f"    -> No similar Kalshi keys (sport={pm_sport})")

                # Check for same-team-different-date matches (potential timezone issue)
                print(f"\n[DEBUG] Checking for team matches with different dates...")
                kalshi_teams = {}  # {sport:team1-team2 -> [dates]}
                pm_teams = {}
                for k in kalshi_keys:
                    parts = k.rsplit(':', 1)  # Split on last colon to get date
                    if len(parts) == 2:
                        teams_part, date = parts
                        if teams_part not in kalshi_teams:
                            kalshi_teams[teams_part] = []
                        kalshi_teams[teams_part].append(date)
                for k in pm_keys:
                    parts = k.rsplit(':', 1)
                    if len(parts) == 2:
                        teams_part, date = parts
                        if teams_part not in pm_teams:
                            pm_teams[teams_part] = []
                        pm_teams[teams_part].append(date)

                # Find teams that exist on both but with different dates
                potential_matches = 0
                for teams_part in kalshi_teams:
                    if teams_part in pm_teams:
                        k_dates = set(kalshi_teams[teams_part])
                        pm_dates_set = set(pm_teams[teams_part])
                        if k_dates != pm_dates_set:
                            potential_matches += 1
                            if potential_matches <= 5:
                                print(f"  {teams_part}: Kalshi={list(k_dates)} vs PM={list(pm_dates_set)}")

                if potential_matches > 0:
                    print(f"[DEBUG] Found {potential_matches} team pairs with DATE MISMATCH - possible timezone issue!")

            # Find arbs
            arbs = []

            # DEBUG: Track specific games for detailed analysis
            DEBUG_GAMES = ['WSHDET', 'DETWSH', 'WSH', 'UMBCUVM', 'UMBC', 'UVM']  # Games to debug

            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    # Check if this is a debug game
                    is_debug_game = any(dg in gid.upper() for dg in DEBUG_GAMES)

                    if is_debug_game and scan_num <= 3:
                        print(f"\n[DEBUG {gid}] Game found in Kalshi data:")
                        print(f"  All teams: {list(game['teams'].keys())}")
                        for t, tp in game['teams'].items():
                            has_pm = 'pm_ask' in tp
                            print(f"  Team '{t}': K bid/ask = {tp.get('k_bid',0)}/{tp.get('k_ask',0)}c | "
                                  f"PM bid/ask = {tp.get('pm_bid','N/A')}/{tp.get('pm_ask','N/A')} | "
                                  f"PM slug = {tp.get('pm_slug', 'N/A')}")

                    for team, p in game['teams'].items():
                        if 'pm_ask' not in p:
                            continue

                        kb = p['k_bid']  # cents
                        ka = p['k_ask']  # cents
                        pb = p['pm_bid']  # cents (implied sell)
                        pa = p['pm_ask']  # cents (cost to buy)

                        # Debug specific games
                        if is_debug_game and scan_num <= 3:
                            ticker = game['tickers'].get(team, 'N/A')
                            print(f"\n[DEBUG ARB CALC] {gid} team={team}:")
                            print(f"  Kalshi ticker: {ticker}")
                            print(f"  Kalshi: bid={kb}c ask={ka}c (we sell at bid, buy at ask)")
                            print(f"  PM: bid={pb}c ask={pa}c (we sell at bid, buy at ask)")
                            print(f"  Direction 1 (Buy PM, Sell K): k_bid - pm_ask = {kb} - {pa} = {kb - pa}c gross")
                            print(f"  Direction 2 (Buy K, Sell PM): pm_bid - k_ask = {pb} - {ka} = {pb - ka}c gross")

                        if kb == 0 or ka == 0:
                            continue

                        # Direction 1: Buy PM, Sell Kalshi
                        # Profit = k_bid - pm_ask - fees
                        gross1 = kb - pa
                        # PM US fee: 0.10% on notional (pm_ask)
                        # Kalshi fee: 1 cent per contract
                        pm_fee1 = PM_US_TAKER_FEE_RATE * pa
                        k_fee1 = KALSHI_FEE * 100
                        fees1 = int(pm_fee1 + k_fee1)
                        net1 = gross1 - fees1

                        if net1 > 0:
                            # Paper mode: use full available liquidity
                            if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
                                sz = p.get('pm_ask_size', 0)  # Full PM liquidity
                            else:
                                sz = min(p.get('pm_ask_size', 0), MAX_CONTRACTS)
                                max_by_cost = MAX_COST_CENTS // pa if pa > 0 else 0
                                sz = min(sz, max_by_cost)

                            min_sz = 1 if (EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS) else MIN_CONTRACTS
                            if sz >= min_sz:
                                arbs.append(ArbOpportunity(
                                    timestamp=datetime.now(),
                                    sport=cfg['sport'].upper(),
                                    game=gid,
                                    team=team,
                                    direction='BUY_PM_SELL_K',
                                    k_bid=kb,
                                    k_ask=ka,
                                    pm_bid=pb,
                                    pm_ask=pa,
                                    gross_spread=gross1,
                                    fees=fees1,
                                    net_spread=net1,
                                    size=sz,
                                    kalshi_ticker=game['tickers'].get(team, ''),
                                    pm_slug=p.get('pm_slug', ''),
                                    pm_outcome_index=p.get('pm_outcome_index', 0),
                                    pm_bid_size=p.get('pm_bid_size', 0),
                                    pm_ask_size=p.get('pm_ask_size', 0),
                                    is_live_game=game.get('is_live', False)
                                ))

                        # Direction 2: Buy Kalshi, Sell PM
                        # Profit = pm_bid - k_ask - fees
                        gross2 = pb - ka
                        # PM US fee: 0.10% on opposite side notional (100 - pm_bid)
                        pm_fee2 = PM_US_TAKER_FEE_RATE * (100 - pb)
                        k_fee2 = KALSHI_FEE * 100
                        fees2 = int(pm_fee2 + k_fee2)
                        net2 = gross2 - fees2

                        if net2 > 0:
                            # Paper mode: use full available liquidity
                            if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
                                sz = p.get('pm_bid_size', 0)  # Full PM liquidity
                            else:
                                sz = min(p.get('pm_bid_size', 0), MAX_CONTRACTS)
                                max_by_cost = MAX_COST_CENTS // ka if ka > 0 else 0
                                sz = min(sz, max_by_cost)

                            min_sz = 1 if (EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS) else MIN_CONTRACTS
                            if sz >= min_sz:
                                arbs.append(ArbOpportunity(
                                    timestamp=datetime.now(),
                                    sport=cfg['sport'].upper(),
                                    game=gid,
                                    team=team,
                                    direction='BUY_K_SELL_PM',
                                    k_bid=kb,
                                    k_ask=ka,
                                    pm_bid=pb,
                                    pm_ask=pa,
                                    gross_spread=gross2,
                                    fees=fees2,
                                    net_spread=net2,
                                    size=sz,
                                    kalshi_ticker=game['tickers'].get(team, ''),
                                    pm_slug=p.get('pm_slug', ''),
                                    pm_outcome_index=p.get('pm_outcome_index', 0),
                                    pm_bid_size=p.get('pm_bid_size', 0),
                                    pm_ask_size=p.get('pm_ask_size', 0),
                                    is_live_game=game.get('is_live', False)
                                ))

            # Filter by LIQUIDITY and SPREAD (not ROI - high ROI on illiquid prices is misleading)
            # Analysis showed: 240% ROI on 5c ask = only $2.40 profit vs 12% ROI on 50c ask = $30 profit
            exec_arbs = []
            skipped_high_roi = 0
            skipped_low_liquidity = 0
            skipped_low_price = 0
            skipped_live_games = 0
            review_high_roi = 0

            for a in arbs:
                # Get the relevant PM price and size based on direction
                if a.direction == 'BUY_PM_SELL_K':
                    pm_price = a.pm_ask
                    pm_size = a.pm_ask_size
                else:
                    pm_price = a.pm_bid
                    pm_size = a.pm_bid_size

                # FILTER 1: Skip illiquid low prices (high ROI but no real profit)
                if pm_price < MIN_PM_PRICE:
                    skipped_low_price += 1
                    log_skipped_arb(a, 'illiquid_price', f"PM price {pm_price}c < {MIN_PM_PRICE}c - likely thin market")
                    if skipped_low_price <= 3:
                        print(f"[SKIP] Illiquid price: {a.game} {a.team} - PM={pm_price}c (ROI={a.roi:.0f}% misleading)")
                    continue

                # FILTER 2: Skip low contract count (not worth the effort)
                if pm_size < MIN_CONTRACTS:
                    skipped_low_liquidity += 1
                    log_skipped_arb(a, 'low_liquidity', f"PM size {pm_size} < {MIN_CONTRACTS} contracts")
                    if skipped_low_liquidity <= 3:
                        print(f"[SKIP] Low liquidity: {a.game} {a.team} - {pm_size} contracts < {MIN_CONTRACTS}")
                    continue

                # FILTER 3: Skip live games in LIVE mode (prices change too fast)
                if a.is_live_game and EXECUTION_MODE == ExecutionMode.LIVE:
                    skipped_live_games += 1
                    log_skipped_arb(a, 'live_game', "Prices changing rapidly, too risky in LIVE mode")
                    if skipped_live_games <= 3:
                        print(f"[SKIP] LIVE GAME: {a.game} {a.team} - prices changing rapidly")
                    continue

                # Flag live games for review in paper mode
                if a.is_live_game and EXECUTION_MODE == ExecutionMode.PAPER:
                    a.needs_review = True
                    if not a.review_reason:
                        a.review_reason = "Live game - prices may be stale"
                    else:
                        a.review_reason += "; Live game - prices may be stale"

                # FILTER 4: Flag (but don't skip) extreme ROI - likely data issue
                if a.roi > MAX_ROI:
                    review_high_roi += 1
                    a.needs_review = True
                    if a.review_reason:
                        a.review_reason += f"; ROI {a.roi:.1f}% exceeds {MAX_ROI}%"
                    else:
                        a.review_reason = f"ROI {a.roi:.1f}% exceeds {MAX_ROI}% threshold"
                    if review_high_roi <= 3:
                        print(f"[REVIEW] High ROI {a.roi:.1f}% - likely data issue, verify manually")
                        print(f"  {a.game} {a.team}: K={a.k_bid}/{a.k_ask}c | PM={a.pm_bid}/{a.pm_ask}c")
                    # In LIVE mode, skip extreme ROI
                    if EXECUTION_MODE == ExecutionMode.LIVE:
                        skipped_high_roi += 1
                        log_skipped_arb(a, 'high_roi', f"ROI {a.roi:.1f}% - likely bad data")
                        continue

                # Calculate LIQUIDITY SCORE = spread * contracts (realistic profit potential)
                liquidity_score = a.net_spread * pm_size
                realistic_profit = (a.net_spread / 100) * pm_size  # In dollars

                # Store for sorting and display
                a._liquidity_score = liquidity_score
                a._realistic_profit = realistic_profit
                a._available_contracts = pm_size

                exec_arbs.append(a)

                # Track ROI distribution (for analysis only, not filtering)
                if a.roi < 1:
                    ROI_BUCKETS['0-1%'] += 1
                elif a.roi < 2:
                    ROI_BUCKETS['1-2%'] += 1
                elif a.roi < 3:
                    ROI_BUCKETS['2-3%'] += 1
                elif a.roi < 5:
                    ROI_BUCKETS['3-5%'] += 1
                elif a.roi < 10:
                    ROI_BUCKETS['5-10%'] += 1
                else:
                    ROI_BUCKETS['10%+'] += 1

            # Sort by LIQUIDITY SCORE (spread * contracts) - realistic profit potential
            # This prioritizes: 6c spread * 500 contracts = 3000 over 12c spread * 20 contracts = 240
            exec_arbs.sort(key=lambda x: -x._liquidity_score)

            if skipped_live_games > 0:
                print(f"[SKIP] {skipped_live_games} LIVE games (too risky)")

            if skipped_low_price > 0:
                print(f"[SKIP] {skipped_low_price} illiquid (PM price < {MIN_PM_PRICE}c)")

            if skipped_low_liquidity > 0:
                print(f"[SKIP] {skipped_low_liquidity} low liquidity (< {MIN_CONTRACTS} contracts)")

            if skipped_high_roi > 0:
                print(f"[SKIP] {skipped_high_roi} extreme ROI > {MAX_ROI}% (likely bad data)")

            if review_high_roi > 0:
                print(f"[REVIEW] {review_high_roi} extreme ROI flagged for verification")

            scan_time = (time.time() - t0) * 1000

            # Display
            print("=" * 70)
            print(f"v7 DIRECT US | Scan #{scan_num} | {datetime.now().strftime('%H:%M:%S')} | {scan_time:.0f}ms")
            print(f"Mode: {EXECUTION_MODE.value.upper()} | Trades: {total_trades} | Profit: ${total_profit:.2f}")

            # Show pending market count
            if pending_markets:
                pending_soon = [p for p in pending_markets if p.get('hours_to_game') and 0 < p['hours_to_game'] < 6]
                print(f"Pending: {len(pending_markets)} markets | Soon (<6h): {len(pending_soon)} | Activated today: {len([a for a in ACTIVATED_MARKETS.values() if a.get('activated_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))])}")
            print("=" * 70)

            total_games = sum(len(all_games[c['sport']]) for c in SPORTS_CONFIG)

            print(f"\n[i] Kalshi Games: {total_games} | PM US Matched: {total_matched} | PM US Markets: {pm_us_matched}")
            print(f"[i] Found {len(arbs)} arbs, {len(exec_arbs)} executable (liquid + {MIN_CONTRACTS}+ contracts)")

            # Scan-level skip summary
            scan_skipped = skipped_high_roi + skipped_low_liquidity + skipped_live_games
            if scan_skipped > 0:
                skip_breakdown = []
                if skipped_high_roi > 0:
                    skip_breakdown.append(f"high_roi:{skipped_high_roi}")
                if skipped_low_liquidity > 0:
                    skip_breakdown.append(f"low_liq:{skipped_low_liquidity}")
                if skipped_live_games > 0:
                    skip_breakdown.append(f"live:{skipped_live_games}")
                print(f"[SCAN #{scan_num}] Found: {len(arbs)} | Exec: {len(exec_arbs)} | Skipped: {scan_skipped} ({', '.join(skip_breakdown)})")

            # Update cumulative stats
            cumulative_arbs_found += len(arbs)
            cumulative_matches += total_matched
            SCAN_STATS['total_found'] += len(arbs)
            # Note: SCAN_STATS['total_skipped'] is updated by log_skipped_arb() calls

            # Periodic status summary for overnight running (every 30 min or every 100 scans)
            if time.time() - last_summary_time >= SUMMARY_INTERVAL or scan_num % 100 == 0:
                uptime_hours = (time.time() - start_time) / 3600
                avg_arbs = cumulative_arbs_found / scan_num if scan_num > 0 else 0
                avg_matches = cumulative_matches / scan_num if scan_num > 0 else 0
                print("\n" + "=" * 70)
                print(f"[PERIODIC SUMMARY] Uptime: {uptime_hours:.1f}h | Scans: {scan_num}")
                print(f"  Total Trades: {total_trades} | Total Profit: ${total_profit:.2f}")
                print(f"  Arbs Found: {SCAN_STATS['total_found']} | Executed: {total_trades} | Skipped: {SCAN_STATS['total_skipped']}")
                print(f"  Avg Arbs/Scan: {avg_arbs:.1f} | Avg Matches/Scan: {avg_matches:.1f}")

                # Skip breakdown
                active_skips = {k: v for k, v in SKIP_STATS.items() if v > 0}
                if active_skips:
                    skip_str = " | ".join([f"{k}:{v}" for k, v in sorted(active_skips.items(), key=lambda x: -x[1])])
                    print(f"  Skip Breakdown: {skip_str}")

                # Best missed opportunity
                best_missed = get_best_skipped_opportunity()
                if best_missed:
                    print(f"  Best Missed: {best_missed['game']} {best_missed['team']} ROI={best_missed['initial_roi']}% ({best_missed['skip_reason']})")

                print(f"  Traded Games: {len(TRADED_GAMES)} | Live Game Warnings: {len(live_games)}")

                # Total Addressable Market stats (paper unlimited mode)
                if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS and TAM_STATS['scan_count'] > 0:
                    total_unique = TAM_STATS['unique_arbs_new'] + TAM_STATS['unique_arbs_reopen']
                    print(f"\n  [TOTAL ADDRESSABLE MARKET]")
                    print(f"    Scans: {TAM_STATS['scan_count']}")
                    print(f"    Unique Arbs: {total_unique} ({TAM_STATS['unique_arbs_new']} NEW + {TAM_STATS['unique_arbs_reopen']} REOPEN)")
                    print(f"    Flicker Ignored: {TAM_STATS['flicker_ignored']}")
                    print(f"    Executed: {TAM_STATS['unique_arbs_executed']}")
                    print(f"    Total Profit (if captured once): ${TAM_STATS['total_profit_if_captured']/100:.2f}")
                    print(f"    Total Contracts: {TAM_STATS['total_contracts']:,}")
                    print(f"    Active: {len(ACTIVE_ARBS)} | Recently Closed: {len(RECENTLY_CLOSED)} | Perm Closed: {len(CLOSED_ARBS)}")

                    # Show arb persistence breakdown
                    if ACTIVE_ARBS:
                        print(f"\n    [ACTIVE ARB DETAILS]")
                        now = time.time()
                        for arb_key, active in sorted(ACTIVE_ARBS.items(), key=lambda x: -x[1].current_profit_cents)[:5]:
                            duration = format_duration(now - active.first_seen)
                            tag = "REOPEN" if active.is_reopen else ""
                            print(f"      {active.sport} {active.team}: ${active.current_profit_cents/100:.2f} (open {duration}, {active.scan_count} scans) {tag}")

                    if RECENTLY_CLOSED:
                        print(f"\n    [RECENTLY CLOSED] (within {REOPEN_COOLDOWN_SECONDS}s cooldown)")
                        for arb_key, closed in list(RECENTLY_CLOSED.items())[-5:]:
                            duration = format_duration(closed.total_open_duration)
                            print(f"      {closed.sport} {closed.team}: was {closed.final_spread}c spread (was open {duration})")

                # ROI distribution
                total_roi_tracked = sum(ROI_BUCKETS.values())
                if total_roi_tracked > 0:
                    print(f"\n  [ROI DISTRIBUTION] (total: {total_roi_tracked} arbs)")
                    for bucket, count in ROI_BUCKETS.items():
                        if count > 0:
                            pct = count / total_roi_tracked * 100
                            bar = '█' * int(pct / 5)  # 20 char max bar
                            print(f"    {bucket:>6}: {count:4} ({pct:5.1f}%) {bar}")

                try:
                    import psutil
                    process = psutil.Process()
                    mem_mb = process.memory_info().rss / 1024 / 1024
                    print(f"\n  Memory Usage: {mem_mb:.1f} MB")
                except ImportError:
                    pass
                print("=" * 70 + "\n")
                last_summary_time = time.time()
                # Save skipped arbs to file at summary time
                save_skipped_arbs()

            # Auto-save: every 5 minutes or 500 scans to prevent data loss
            time_since_save = time.time() - LAST_AUTO_SAVE_TIME
            scans_since_save = scan_num - LAST_AUTO_SAVE_SCAN
            if time_since_save >= AUTO_SAVE_INTERVAL or scans_since_save >= AUTO_SAVE_SCAN_INTERVAL:
                perform_auto_save(scan_num)

            # Export market data for dashboard
            export_market_data(all_games, arbs)

            # Paper mode with no limits: Track Total Addressable Market with lifecycle
            paper_unlimited = EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS

            if paper_unlimited:
                TAM_STATS['scan_count'] += 1
                now = time.time()

                # Cleanup old closed arbs from tracking
                cleanup_old_closed_arbs(now)

                # Track which arbs we see this scan
                seen_this_scan = set()
                new_arbs = []       # First time ever seeing
                reopen_arbs = []    # Reopened after cooldown
                flicker_count = 0   # Reopened within cooldown (ignored)

                print(f"\n[SCAN #{TAM_STATS['scan_count']}] {len(exec_arbs)} arbs available:")

                for arb in exec_arbs:
                    arb_key = get_arb_key(arb)
                    seen_this_scan.add(arb_key)
                    profit_cents = arb.net_spread * arb.size

                    if arb_key in ACTIVE_ARBS:
                        # PERSISTING arb - already active
                        active = ACTIVE_ARBS[arb_key]
                        active.last_seen = now
                        active.scan_count += 1
                        active.current_spread = arb.net_spread
                        active.current_size = arb.size
                        active.current_profit_cents = profit_cents

                        duration = format_duration(now - active.first_seen)
                        roi_info = f" | ROI:{arb.roi:.0f}%" if arb.roi > 20 else ""
                        print(f"  [PERSIST] {arb.sport} {arb.team}: {arb.net_spread}c spread | {arb.size} contracts | ${profit_cents/100:.2f}{roi_info} (open {duration})")

                    elif arb_key in RECENTLY_CLOSED:
                        # Was recently closed - check if flicker or real reopen
                        closed = RECENTLY_CLOSED[arb_key]
                        time_since_close = now - closed.closed_at

                        if time_since_close < REOPEN_COOLDOWN_SECONDS:
                            # FLICKER - reopened too quickly, ignore
                            flicker_count += 1
                            TAM_STATS['flicker_ignored'] += 1
                            print(f"  [FLICKER] {arb.sport} {arb.team}: {arb.net_spread}c spread (closed {int(time_since_close)}s ago, ignoring)")
                        else:
                            # REOPEN - real reopening after cooldown
                            active = ActiveArb(
                                arb_key=arb_key,
                                game=arb.game,
                                team=arb.team,
                                sport=arb.sport,
                                direction=arb.direction,
                                first_seen=now,
                                last_seen=now,
                                scan_count=1,
                                initial_spread=arb.net_spread,
                                initial_size=arb.size,
                                initial_profit_cents=profit_cents,
                                current_spread=arb.net_spread,
                                current_size=arb.size,
                                current_profit_cents=profit_cents,
                                kalshi_ticker=arb.kalshi_ticker,
                                pm_slug=arb.pm_slug,
                                executed=False,
                                is_reopen=True
                            )
                            ACTIVE_ARBS[arb_key] = active
                            reopen_arbs.append(active)
                            TAM_STATS['unique_arbs_reopen'] += 1
                            # Remove from recently closed
                            del RECENTLY_CLOSED[arb_key]

                            roi_info = f" | ROI:{arb.roi:.0f}%" if arb.roi > 20 else ""
                            print(f"  [REOPEN] {arb.sport} {arb.team}: {arb.net_spread}c spread | {arb.size} contracts | ${profit_cents/100:.2f}{roi_info}")
                    else:
                        # NEW arb - first time seeing it ever
                        active = ActiveArb(
                            arb_key=arb_key,
                            game=arb.game,
                            team=arb.team,
                            sport=arb.sport,
                            direction=arb.direction,
                            first_seen=now,
                            last_seen=now,
                            scan_count=1,
                            initial_spread=arb.net_spread,
                            initial_size=arb.size,
                            initial_profit_cents=profit_cents,
                            current_spread=arb.net_spread,
                            current_size=arb.size,
                            current_profit_cents=profit_cents,
                            kalshi_ticker=arb.kalshi_ticker,
                            pm_slug=arb.pm_slug,
                            executed=False,
                            is_reopen=False
                        )
                        ACTIVE_ARBS[arb_key] = active
                        new_arbs.append(active)
                        TAM_STATS['unique_arbs_new'] += 1

                        roi_info = f" | ROI:{arb.roi:.0f}%" if arb.roi > 20 else ""
                        print(f"  [NEW] {arb.sport} {arb.team}: {arb.net_spread}c spread | {arb.size} contracts | ${profit_cents/100:.2f}{roi_info}")

                # Check for CLOSED arbs (were active but not seen this scan)
                closed_keys = []
                for arb_key, active in ACTIVE_ARBS.items():
                    if arb_key not in seen_this_scan:
                        # Arb closed - move to recently closed for reopen detection
                        duration = format_duration(now - active.first_seen)
                        print(f"  [CLOSED] {active.sport} {active.team}: was {active.current_spread}c spread, open for {duration}")

                        closed = ClosedArb(
                            arb_key=arb_key,
                            closed_at=now,
                            sport=active.sport,
                            team=active.team,
                            final_spread=active.current_spread,
                            total_open_duration=now - active.first_seen,
                            total_profit_captured=active.initial_profit_cents if active.executed else 0
                        )
                        RECENTLY_CLOSED[arb_key] = closed
                        closed_keys.append(arb_key)

                for key in closed_keys:
                    del ACTIVE_ARBS[key]

                # "Execute" NEW and REOPEN arbs in paper mode
                for active in new_arbs + reopen_arbs:
                    if not active.executed:
                        active.executed = True
                        TAM_STATS['unique_arbs_executed'] += 1
                        TAM_STATS['total_profit_if_captured'] += active.initial_profit_cents
                        TAM_STATS['total_contracts'] += active.initial_size
                        tag = "REOPEN" if active.is_reopen else "NEW"
                        print(f"    -> [PAPER EXECUTE {tag}] ${active.initial_profit_cents/100:.2f} captured")

                # Summary
                total_unique = TAM_STATS['unique_arbs_new'] + TAM_STATS['unique_arbs_reopen']
                total_active = len(ACTIVE_ARBS)
                total_recently_closed = len(RECENTLY_CLOSED)
                total_perm_closed = len(CLOSED_ARBS)

                print(f"\n  [TAM SUMMARY] Unique: {total_unique} ({TAM_STATS['unique_arbs_new']} NEW + {TAM_STATS['unique_arbs_reopen']} REOPEN)")
                print(f"  Flicker ignored: {TAM_STATS['flicker_ignored']}")
                print(f"  Active: {total_active} | Recently Closed: {total_recently_closed} | Perm Closed: {total_perm_closed}")
                print(f"  Scans: {TAM_STATS['scan_count']} | Executed: {TAM_STATS['unique_arbs_executed']}")
                print(f"  If captured once each: ${TAM_STATS['total_profit_if_captured']/100:.2f} from {TAM_STATS['total_contracts']:,} contracts")

            # Execute if we have arbs and cooldown passed (skip in paper unlimited - handled above)
            if not paper_unlimited:
                cooldown_ok = (time.time() - last_trade_time) >= COOLDOWN_SECONDS
                if exec_arbs and cooldown_ok:
                    # Find first arb we haven't already traded
                    best = None
                    for candidate in exec_arbs:
                        game_key = candidate.game
                        slug_key = candidate.pm_slug

                        if game_key in TRADED_GAMES:
                            log_skipped_arb(candidate, 'already_traded', f"Already have position in game {game_key}")
                            print(f"[SKIP] Already traded game {game_key} - skipping")
                            continue
                        if slug_key and slug_key in TRADED_GAMES:
                            log_skipped_arb(candidate, 'already_traded', f"Already have position in slug {slug_key}")
                            print(f"[SKIP] Already traded slug {slug_key} - skipping")
                            continue

                        best = candidate
                        break

                    if not best:
                        print(f"\n[.] All {len(exec_arbs)} arbs already traded - skipping")
                        await asyncio.sleep(1.0)
                        continue
                elif exec_arbs:
                    # Have arbs but cooldown hasn't passed
                    cooldown_remaining = COOLDOWN_SECONDS - (time.time() - last_trade_time)
                    for a in exec_arbs:
                        log_skipped_arb(a, 'cooldown', f"{cooldown_remaining:.0f}s remaining in cooldown")
                    print(f"\n[.] Cooldown: {cooldown_remaining:.0f}s remaining")
                    await asyncio.sleep(1.0)
                    continue
                else:
                    # No executable arbs
                    print(f"\n[.] No executable arbs")
                    await asyncio.sleep(1.0)
                    continue
            else:
                # In paper unlimited, skip the execution block below
                await asyncio.sleep(1.0)
                continue

            # best is set from the non-paper-unlimited block above
            best = None
            for candidate in exec_arbs:
                game_key = candidate.game
                slug_key = candidate.pm_slug
                if game_key not in TRADED_GAMES and (not slug_key or slug_key not in TRADED_GAMES):
                    best = candidate
                    break

            if not best:
                await asyncio.sleep(1.0)
                continue

            # =========================================================
            # HEDGE PROTECTION: Kill Switch Check
            # =========================================================
            if check_kill_switch():
                print("[BLOCKED] Trading halted by kill switch")
                await asyncio.sleep(5.0)
                continue

            # =========================================================
            # HEDGE PROTECTION: Pre-Trade Validation
            # =========================================================
            is_valid, reason, fresh_prices = await validate_pre_trade(
                session, kalshi_api, pm_api, best
            )

            if not is_valid:
                print(f"[ABORT] Pre-trade validation failed: {reason}")
                log_skipped_arb(best, 'validation_failed', reason)
                await asyncio.sleep(1.0)
                continue

            print(f"\n[!] BEST ARB: {best.sport} {best.game} {best.team}")
            print(f"    Direction: {best.direction}")
            print(f"    K: {best.k_bid}/{best.k_ask}c | PM: {best.pm_bid}/{best.pm_ask}c")
            print(f"    Size: {best.size} | Profit: ${best.profit:.2f} | ROI: {best.roi:.1f}%")
            print(f"    PM Slug: {best.pm_slug} | Outcome Index: {best.pm_outcome_index}")

            # Determine Kalshi order params
            if best.direction == 'BUY_PM_SELL_K':
                k_action = 'sell'
                k_price = best.k_bid
            else:
                k_action = 'buy'
                k_price = best.k_ask

            # Get position BEFORE order
            pre_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
            print(f"\n[>>] PRE-TRADE: Kalshi Position = {pre_position}")

            # =============================================================
            # BULLETPROOF ORDER BOOK SWEEP (Kalshi side - same as v6)
            # =============================================================
            MAX_PRICE_LEVELS = 10
            actual_fill = 0
            fill_price = k_price
            k_result = {}
            placed_order_ids = []
            sweep_break_reason = None  # Track why sweep ended
            final_adjusted_roi = 0

            try:
                for price_offset in range(MAX_PRICE_LEVELS + 1):
                    if k_action == 'buy':
                        try_price = k_price + price_offset
                    else:
                        try_price = k_price - price_offset

                    if try_price < 1 or try_price > 99:
                        print(f"   [X] Price {try_price}c out of bounds, stopping sweep")
                        sweep_break_reason = 'price_bounds'
                        break

                    if k_action == 'buy':
                        adjusted_profit = best.profit - (price_offset * best.size / 100)
                        adjusted_capital = best.size * (try_price / 100)
                    else:
                        adjusted_profit = best.profit - (price_offset * best.size / 100)
                        adjusted_capital = best.size * ((100 - try_price) / 100)

                    adjusted_roi = (adjusted_profit / adjusted_capital * 100) if adjusted_capital > 0 else 0
                    final_adjusted_roi = adjusted_roi

                    if adjusted_roi < MIN_SWEEP_ROI:
                        print(f"   [X] ROI {adjusted_roi:.1f}% < {MIN_SWEEP_ROI}% at {try_price}c, stopping sweep")
                        sweep_break_reason = 'roi_too_low'
                        break

                    print(f"[>>] SWEEP {price_offset}: {k_action} {best.size} YES @ {try_price}c (ROI: {adjusted_roi:.1f}%)")
                    k_result = await kalshi_api.place_order(
                        session, best.kalshi_ticker, 'yes', k_action, best.size, try_price
                    )

                    api_fill_count = k_result.get('fill_count', 0)
                    order_id = k_result.get('order_id')

                    if order_id:
                        placed_order_ids.append(order_id)
                        print(f"   [ORDER PLACED] {order_id[:12]}...")

                    if api_fill_count > 0:
                        actual_fill = api_fill_count
                        fill_price = try_price
                        print(f"   [OK] Got fill at {try_price}c!")
                        break
                    else:
                        if order_id:
                            cancelled = await kalshi_api.cancel_order(session, order_id)
                            if not cancelled:
                                print(f"   [!] WARNING: Cancel may have failed for {order_id[:12]}")
                        print(f"   [.] No fill at {try_price}c, trying next level...")
                        await asyncio.sleep(0.1)

            finally:
                # CRITICAL CLEANUP: Cancel ALL Kalshi orders for this ticker
                print(f"\n[SWEEP CLEANUP] Ensuring no resting Kalshi orders for {best.kalshi_ticker}...")
                cleanup_count = await kalshi_api.cancel_all_orders_for_ticker(session, best.kalshi_ticker)
                if cleanup_count > 0:
                    print(f"[SWEEP CLEANUP] Cancelled {cleanup_count} resting orders")

            # Verify with position check
            await asyncio.sleep(0.3)
            post_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
            print(f"[>>] POST-TRADE: Kalshi Position = {post_position}")

            position_change = 0
            if pre_position is not None and post_position is not None:
                position_change = abs(post_position - pre_position)

            if actual_fill == 0 and position_change > 0:
                actual_fill = position_change
                print(f"[>>] Position changed by {position_change}, using as fill count")

            print(f"[>>] Final: API fill={k_result.get('fill_count', 0)}, Position change={position_change}, Using={actual_fill}")

            # =============================================================
            # EXECUTE PM US SIDE (replaces partner webhook)
            # =============================================================
            if actual_fill > 0:
                print(f"\n[OK] KALSHI FILLED: {actual_fill} contracts @ {fill_price}c")

                # Compute PM US execution parameters
                pm_intent, pm_price = get_pm_execution_params(best)
                intent_names = {1: 'BUY_YES', 2: 'SELL_YES', 3: 'BUY_NO', 4: 'SELL_NO'}

                print(f"[>>] Executing PM US: {intent_names[pm_intent]} {actual_fill} @ ${pm_price:.2f} on {best.pm_slug}")

                pm_result = await pm_api.place_order(
                    session,
                    market_slug=best.pm_slug,
                    intent=pm_intent,
                    price=pm_price,
                    quantity=actual_fill,
                    tif=3,   # IOC
                    sync=True
                )

                # =========================================================
                # HEDGE PROTECTION: Reconciliation with Recovery
                # =========================================================
                hedge_state = await reconcile_hedge(
                    session, kalshi_api, pm_api, best,
                    k_result, pm_result, actual_fill
                )

                pm_fill = hedge_state.pm_filled
                pm_fill_price = pm_result.get('fill_price')

                if pm_fill > 0:
                    print(f"[OK] PM US FILLED: {pm_fill} contracts" + (f" @ ${pm_fill_price:.2f}" if pm_fill_price else ""))

                # Calculate actual profit (accounting for any recovery slippage)
                price_diff = abs(fill_price - k_price)
                slippage_cost = hedge_state.recovery_slippage * hedge_state.pm_filled / 100 if hedge_state.recovery_slippage else 0
                actual_profit = best.profit - (price_diff * actual_fill / 100) - slippage_cost

                if hedge_state.is_hedged:
                    # Successfully hedged (possibly with recovery)
                    total_trades += 1
                    SCAN_STATS['total_executed'] += 1
                    total_profit += actual_profit

                    if hedge_state.recovery_slippage > 0:
                        print(f"[$] Trade #{total_trades} | +${actual_profit:.2f} (reduced due to {hedge_state.recovery_slippage}c recovery slippage)")
                        log_trade(best, k_result, pm_result, 'RECOVERED')
                    else:
                        print(f"[$] Trade #{total_trades} | +${actual_profit:.2f} | Total: ${total_profit:.2f}")
                        log_trade(best, k_result, pm_result, 'SUCCESS')

                    # Track paper stats
                    if EXECUTION_MODE == ExecutionMode.PAPER:
                        PAPER_STATS['total_arbs_executed'] += 1
                        PAPER_STATS['total_theoretical_profit'] += actual_profit
                        PAPER_STATS['total_contracts'] += actual_fill

                    # Mark game as traded
                    TRADED_GAMES.add(best.game)
                    if best.pm_slug:
                        TRADED_GAMES.add(best.pm_slug)
                    print(f"[POSITION TRACKING] Added {best.game} to traded games ({len(TRADED_GAMES)} total)")

                else:
                    # UNHEDGED - recovery failed
                    unhedged_qty = hedge_state.kalshi_filled - hedge_state.pm_filled
                    print(f"[!!!] UNHEDGED POSITION: {unhedged_qty} contracts on {best.kalshi_ticker}")

                    log_trade(best, k_result, pm_result, 'UNHEDGED')

                    # Mark as traded to avoid retrying
                    TRADED_GAMES.add(best.game)
                    if best.pm_slug:
                        TRADED_GAMES.add(best.pm_slug)

                    if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
                        print(f"[PAPER] Continuing despite unhedged position (no-limits mode)")
                    elif check_kill_switch():
                        # Kill switch was activated by reconciliation
                        print(f"[STOP] Bot stopping due to kill switch")
                        raise SystemExit("KILL SWITCH ACTIVATED - Manual intervention required")
                    else:
                        # Exposure under limit, continue with warning
                        exposure = unhedged_qty * hedge_state.kalshi_price
                        print(f"[WARNING] Exposure ${exposure/100:.2f} under limit, continuing...")

                last_trade_time = time.time()

            else:
                # Log the skipped arb with appropriate reason
                if sweep_break_reason == 'roi_too_low':
                    log_skipped_arb(best, 'sweep_roi_too_low', f"ROI dropped to {final_adjusted_roi:.1f}% during sweep")
                    print(f"\n[X] NO FILL - ROI dropped to {final_adjusted_roi:.1f}% during sweep")
                else:
                    log_skipped_arb(best, 'no_fill', f"No fill after sweeping {MAX_PRICE_LEVELS} price levels")
                    print(f"\n[X] NO FILL after sweeping {MAX_PRICE_LEVELS} price levels")
                log_trade(best, k_result, {}, 'NO_FILL')

            await asyncio.sleep(1.0)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='ARB Executor v7 - Direct US Execution')
    parser.add_argument('--start', action='store_true',
                        help='Start scanning immediately (used by bot_server)')
    parser.add_argument('--paper', action='store_true',
                        help='Force paper trading mode')
    parser.add_argument('--live', action='store_true',
                        help='Force live trading mode')
    parser.add_argument('--clear', action='store_true',
                        help='Clear trades.json and traded_games before starting')
    parser.add_argument('--debug', action='store_true',
                        help='Enable extra debug logging')
    parser.add_argument('--no-limits', action='store_true', dest='no_limits',
                        help='Remove capital constraints in paper mode (default: True for paper)')
    parser.add_argument('--with-limits', action='store_true', dest='with_limits',
                        help='Keep capital constraints even in paper mode')
    parser.add_argument('--discover', action='store_true',
                        help='Discover available Kalshi series (find CBB ticker) and exit')
    parser.add_argument('--chart', action='store_true',
                        help='Generate price charts on shutdown (requires matplotlib)')
    parser.add_argument('--match-debug', action='store_true', dest='match_debug',
                        help='Show detailed market matching analysis and exit (no trading)')
    parser.add_argument('--verify-games', action='store_true', dest='verify_games',
                        help='Search Kalshi by team names to find missing mappings and exit')
    parser.add_argument('--recover', action='store_true',
                        help='Enter recovery mode: show positions, check for mismatches')
    parser.add_argument('--force', action='store_true',
                        help='Force override kill switch (for manual recovery only)')
    parser.add_argument('--preflight', action='store_true',
                        help='Run preflight checks and exit (validates system before live trading)')
    parser.add_argument('--skip-preflight', action='store_true', dest='skip_preflight',
                        help='Skip preflight checks in live mode (NOT RECOMMENDED)')
    args = parser.parse_args()

    # Override execution mode if specified
    if args.paper:
        EXECUTION_MODE = ExecutionMode.PAPER
    elif args.live:
        EXECUTION_MODE = ExecutionMode.LIVE

    # Set paper no-limits mode (default True for paper, can be disabled with --with-limits)
    if args.with_limits:
        PAPER_NO_LIMITS = False
    elif args.no_limits or EXECUTION_MODE == ExecutionMode.PAPER:
        PAPER_NO_LIMITS = True

    # Enable debug mode
    if args.debug:
        DEBUG_MATCHING = True

    # Enable chart generation on shutdown
    if args.chart:
        GENERATE_CHART_ON_EXIT = True
        print("[CHART] Chart generation enabled - will create price_chart_*.png on shutdown")

    # Clear old data if requested
    if args.clear:
        print("[CLEAR] Clearing trades.json, skipped_arbs.json, and position tracking...")
        try:
            with open('trades.json', 'w') as f:
                json.dump([], f)
            print("[CLEAR] trades.json cleared")
        except Exception as e:
            print(f"[CLEAR] Warning: Could not clear trades.json: {e}")
        try:
            with open('skipped_arbs.json', 'w') as f:
                json.dump([], f)
            print("[CLEAR] skipped_arbs.json cleared")
        except Exception as e:
            print(f"[CLEAR] Warning: Could not clear skipped_arbs.json: {e}")
        TRADE_LOG.clear()
        TRADED_GAMES.clear()
        SKIPPED_ARBS.clear()
        for k in SKIP_STATS:
            SKIP_STATS[k] = 0
        for k in SCAN_STATS:
            SCAN_STATS[k] = 0
        for k in ROI_BUCKETS:
            ROI_BUCKETS[k] = 0
        for k in PAPER_STATS:
            PAPER_STATS[k] = 0 if k != 'start_time' else None
        print("[CLEAR] In-memory trade log, skipped arbs, ROI buckets, and traded games cleared")

    # Handle --discover flag (runs series discovery and exits)
    if args.discover:
        async def run_discovery():
            kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
            async with aiohttp.ClientSession() as session:
                await discover_kalshi_series(session, kalshi_api)

        print("\n[KALSHI SERIES DISCOVERY MODE]")
        asyncio.run(run_discovery())
        sys.exit(0)

    # Handle --match-debug flag (runs matching analysis and exits)
    if args.match_debug:
        print("\n[MATCH DEBUG MODE]")
        print("Analyzing PM US <-> Kalshi market matching...")
        asyncio.run(run_match_debug())
        sys.exit(0)

    # Handle --verify-games flag (searches by team names and exits)
    if args.verify_games:
        print("\n[VERIFY GAMES MODE]")
        print("Searching Kalshi by team names to find missing mappings...")
        asyncio.run(run_verify_games())
        sys.exit(0)

    # Handle --preflight flag (run checks and exit)
    if args.preflight:
        async def preflight_main():
            pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
            kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
            async with aiohttp.ClientSession() as session:
                passed, results = await run_preflight_checks(session, kalshi_api, pm_api)
                return passed
        passed = asyncio.run(preflight_main())
        sys.exit(0 if passed else 1)

    # Handle --recover flag (recovery mode)
    if args.recover:
        print("\n[ENTERING RECOVERY MODE]")
        async def recovery_main():
            pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
            kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
            async with aiohttp.ClientSession() as session:
                await run_recovery_mode(session, kalshi_api, pm_api)
        asyncio.run(recovery_main())
        sys.exit(0)

    # Handle --force flag (reset kill switch)
    if args.force:
        HEDGE_KILL_SWITCH_ACTIVE = False
        print("[FORCE] Kill switch overridden - trading enabled")
        print("[WARNING] Use only for manual recovery - ensure positions are balanced!")

    # Check for unhedged positions on startup
    unhedged = load_unhedged_positions()
    if unhedged and not args.force:
        print("\n[!!! WARNING !!!] Unhedged positions detected:")
        for u in unhedged[-3:]:  # Show last 3
            print(f"  {u['timestamp']}: {u['kalshi_ticker']} - {u['unhedged_qty']} unhedged")
        print("\nRun with --recover to review positions")
        print("Run with --force to override and continue trading")
        print("Exiting for safety...")
        sys.exit(1)

    print("\n" + "="*70)
    print("ARB EXECUTOR v7 - DIRECT US EXECUTION")
    print("Kalshi + Polymarket US | No partner webhook")
    mode_str = EXECUTION_MODE.value.upper()
    if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
        mode_str += " (NO LIMITS - tracking full arb market)"
    print(f"Mode: {mode_str}")
    print("="*70 + "\n")

    # Require explicit --start flag to begin scanning
    # This prevents accidental auto-start when testing/exploring
    if not args.start:
        print("=" * 60)
        print("EXECUTOR NOT STARTED")
        print("=" * 60)
        print("\nTo run via dashboard (RECOMMENDED):")
        print("  1. Start bot_server: python bot_server.py")
        print("  2. Go to: http://localhost:3000/edge/trading")
        print("  3. Click START button")
        print("\nTo run directly (for testing):")
        print("  python arb_executor_v7.py --start")
        print("  python arb_executor_v7.py --start --paper         # Paper mode, no limits (default)")
        print("  python arb_executor_v7.py --start --paper --with-limits  # Paper with capital limits")
        print("  python arb_executor_v7.py --start --live          # Live mode (requires preflight)")
        print("  python arb_executor_v7.py --start --clear         # Clear old trades first")
        print("  python arb_executor_v7.py --start --debug         # Extra debug logging")
        print("\nValidation & Recovery:")
        print("  python arb_executor_v7.py --preflight             # Run preflight checks")
        print("  python arb_executor_v7.py --recover               # Recovery mode for unhedged positions")
        print("  python arb_executor_v7.py --discover              # Find Kalshi series tickers")
        print("=" * 60)
        sys.exit(0)

    # =========================================================================
    # LIVE MODE: Require preflight checks before trading real money
    # =========================================================================
    if EXECUTION_MODE == ExecutionMode.LIVE and not args.skip_preflight:
        print("\n[LIVE MODE] Running mandatory preflight checks...")
        async def live_preflight():
            pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
            kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
            async with aiohttp.ClientSession() as session:
                passed, results = await run_preflight_checks(session, kalshi_api, pm_api)
                return passed

        preflight_passed = asyncio.run(live_preflight())

        if not preflight_passed:
            print("\n" + "="*70)
            print("[BLOCKED] LIVE TRADING NOT ALLOWED - Preflight checks failed!")
            print("="*70)
            print("\nResolve all blocking issues above before live trading.")
            print("To run preflight checks only:  python arb_executor_v7.py --preflight")
            print("To skip preflight (DANGER):    python arb_executor_v7.py --start --live --skip-preflight")
            print("\nSwitching to PAPER mode for safety...")
            EXECUTION_MODE = ExecutionMode.PAPER
            PAPER_NO_LIMITS = True
            print("[MODE CHANGED] Now running in PAPER mode with no limits")
        else:
            print("\n[LIVE MODE APPROVED] All preflight checks passed - proceeding with live trading")

    if args.skip_preflight and EXECUTION_MODE == ExecutionMode.LIVE:
        print("\n" + "!"*70)
        print("[WARNING] PREFLIGHT CHECKS SKIPPED - LIVE TRADING AT YOUR OWN RISK!")
        print("!"*70 + "\n")

    # Reload traded games now that EXECUTION_MODE may have changed
    if EXECUTION_MODE == ExecutionMode.LIVE:
        TRADED_GAMES.update(load_traded_games())
        if TRADED_GAMES:
            print(f"[POSITION TRACKING] Loaded {len(TRADED_GAMES)} previously traded games")

    try:
        asyncio.run(run_executor())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        save_skipped_arbs()
        print(f"Trade log saved to trades.json")
        print(f"Skipped arbs saved to skipped_arbs.json ({len(SKIPPED_ARBS)} entries)")
        if SKIP_STATS:
            active = {k: v for k, v in SKIP_STATS.items() if v > 0}
            if active:
                print(f"Skip breakdown: {active}")

        # Paper trading summary
        if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_STATS['total_arbs_executed'] > 0:
            print("\n" + "=" * 70)
            print("[PAPER TRADING SUMMARY]")
            print("=" * 70)

            total_arbs = PAPER_STATS['total_arbs_executed']
            total_profit = PAPER_STATS['total_theoretical_profit']
            total_contracts = PAPER_STATS['total_contracts']
            start_time = PAPER_STATS.get('start_time', time.time())
            runtime_hours = (time.time() - start_time) / 3600

            avg_profit = total_profit / total_arbs if total_arbs > 0 else 0
            arbs_per_hour = total_arbs / runtime_hours if runtime_hours > 0 else 0

            print(f"  Total arbs executed: {total_arbs}")
            print(f"  Total theoretical profit: ${total_profit:.2f}")
            print(f"  Total contracts traded: {total_contracts}")
            print(f"  Avg profit per arb: ${avg_profit:.2f}")
            print(f"  Runtime: {runtime_hours:.2f} hours")
            print(f"  Arbs per hour: {arbs_per_hour:.1f}")

            # ROI distribution
            total_roi_tracked = sum(ROI_BUCKETS.values())
            if total_roi_tracked > 0:
                print(f"\n  [ROI DISTRIBUTION] (total: {total_roi_tracked} arbs)")
                for bucket, count in ROI_BUCKETS.items():
                    if count > 0:
                        pct = count / total_roi_tracked * 100
                        bar = '█' * int(pct / 5)
                        print(f"    {bucket:>6}: {count:4} ({pct:5.1f}%) {bar}")

            # Project profit at different capital levels
            print("\n  Projected profit with more capital:")
            for capital in [100, 500, 1000, 5000]:
                # Current $10 limit means ~10x capital would capture 10x arbs (roughly)
                multiplier = capital / 10
                projected = total_profit * min(multiplier, arbs_per_hour * runtime_hours)
                print(f"    ${capital:,} capital -> ~${projected:.2f} profit")

            print("=" * 70)

        # Save price history to CSV
        if PRICE_HISTORY:
            print("\n[PRICE HISTORY] Saving price data...")
            csv_file = save_price_history()

            # Generate charts if requested
            if GENERATE_CHART_ON_EXIT and csv_file:
                print("[CHART] Generating price visualization...")
                generate_price_charts(csv_file)
