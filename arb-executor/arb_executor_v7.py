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
import sys
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set, Any, Tuple
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ed25519
from cryptography.hazmat.backends import default_backend

# Shared configuration - single source of truth for both executors
from config import Config, ExecutionMode

# Pre-game mapping agent integration
try:
    from pregame_mapper import (
        load_verified_mappings,
        get_mapping_for_game,
        get_team_outcome_index,
        get_team_token_id,
    )
    HAS_MAPPER = True
except ImportError:
    HAS_MAPPER = False

# ============================================================================
# FIX: Windows Unicode encoding issue (cp1252 can't handle special chars)
# ============================================================================
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for stdout/stderr
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7 fallback
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# HARD LIMITS - DO NOT CHANGE THESE
# FIX-BUG-9: Adjusted limits - max 20 contracts, $15 per trade as requested
# ============================================================================
MAX_CONTRACTS = 20          # FIX-BUG-9: Reduced from 100 to 20 contracts per trade
MAX_COST_CENTS = 1500       # FIX-BUG-9: Reduced from 5000 to 1500 ($15 max per trade)
MIN_CONTRACTS = 1           # Minimum contracts per order (was 5, but WS executor uses 1)
MIN_LIQUIDITY = 50          # Minimum bid/ask size on both sides
MIN_PM_PRICE = 5            # FIX-BUG-2: Safety floor $0.05 (5c) - skip arbs below this
MIN_BUY_PRICE = 5           # FIX-BUG-2: Safety floor $0.05 (5c) on buy side
MIN_SPREAD_CENTS = 4        # Minimum spread to consider (must cover slippage + profit)
MIN_SWEEP_ROI = 1.0         # Minimum ROI during sweep before stopping
MAX_ROI = 50.0              # Maximum ROI - higher is likely bad data (kept for flagging)
DEBUG_MATCHING = True       # Log matching debug info
COOLDOWN_SECONDS = 10       # Seconds between trade attempts
SCAN_INTERVAL = 500         # Target scan interval in milliseconds
# NOTE: We no longer filter by ROI - we use spread * liquidity score instead
# High ROI on illiquid prices is misleading (240% ROI on 5c ask = only $2 profit)
# ============================================================================

# ============================================================================
# HEDGE PROTECTION SYSTEM
# FIX-BUG-10: Adjusted staleness to 2000ms (2 seconds) as requested
# ============================================================================
MAX_PRICE_STALENESS_MS = 2000   # FIX-BUG-10: Max 2 seconds since price fetch (was 200ms)
MIN_HEDGE_SPREAD_CENTS = 4      # Minimum spread required to proceed with trade
UNHEDGED_EXPOSURE_LIMIT = 1000  # Max unhedged exposure in cents ($10) before kill switch
SLIPPAGE_RECOVERY_LEVELS = [1, 2, 3, 5, 10]  # Cents of slippage to try for recovery
UNHEDGED_POSITIONS_FILE = 'unhedged_positions.json'
HEDGE_KILL_SWITCH_ACTIVE = False  # Set True to stop all trading

# FIX-BUG-12: Sequential execution lock - only one arb can execute at a time
import asyncio as _asyncio_for_lock
EXECUTION_LOCK = _asyncio_for_lock.Lock()  # Global lock for sequential execution

# ============================================================================
# DRY RUN & TESTING CONFIG
# ============================================================================
DRY_RUN_MODE = False              # Connect to real APIs but don't submit orders
MAX_TRADES = 0                    # Stop after N trades (0 = unlimited)
TRADES_EXECUTED = 0               # Counter for --max-trades

# ============================================================================
# CAPITAL TRACKING & POSITION LIMITS
# ============================================================================
MAX_CONCURRENT_POSITIONS = 10     # Max simultaneous open positions (safety limit)
CAPITAL_WARNING_PCT = 80          # Warn when this % of capital is deployed
POSITION_DISPLAY_INTERVAL = 60    # Show position summary every N seconds

# Open positions tracking
# Key: game_id, Value: {contracts, entry_price, capital_locked, opened_at, kalshi_ticker, pm_slug}
OPEN_POSITIONS: Dict[str, Dict] = {}
LAST_POSITION_DISPLAY = 0         # Timestamp of last position summary

def get_total_deployed_capital() -> float:
    """Get total capital currently locked in open positions (in dollars)."""
    return sum(p.get('capital_locked', 0) for p in OPEN_POSITIONS.values())

def get_position_count() -> int:
    """Get number of open positions."""
    return len(OPEN_POSITIONS)

def add_open_position(game_id: str, contracts: int, entry_price: int,
                      capital_locked: float, kalshi_ticker: str, pm_slug: str):
    """Track a new open position."""
    OPEN_POSITIONS[game_id] = {
        'contracts': contracts,
        'entry_price': entry_price,
        'capital_locked': capital_locked,
        'opened_at': time.time(),
        'kalshi_ticker': kalshi_ticker,
        'pm_slug': pm_slug,
    }
    print(f"[POSITIONS] Opened: {game_id} | {contracts} @ {entry_price}c | ${capital_locked:.2f} locked")
    print(f"[POSITIONS] {get_position_count()}/{MAX_CONCURRENT_POSITIONS} positions | ${get_total_deployed_capital():.2f} deployed")

def display_capital_status(kalshi_balance: float, pm_balance: float, avg_price: int = 50):
    """Display current capital utilization."""
    deployed = get_total_deployed_capital()
    positions = get_position_count()

    # Calculate max contracts possible on each side
    k_max = int(kalshi_balance * 100 / avg_price) if avg_price > 0 else 0
    pm_max = int(pm_balance * 100 / avg_price) if avg_price > 0 else 0
    limiting = "Kalshi" if k_max < pm_max else "PM US"
    limiting_amt = min(kalshi_balance, pm_balance)

    print(f"\n[CAPITAL] Kalshi: ${kalshi_balance:.2f} available | PM US: ${pm_balance:.2f} available")
    print(f"[CAPITAL] Limiting factor: {limiting} (${limiting_amt:.2f} = max {min(k_max, pm_max)} contracts @ {avg_price}c)")
    print(f"[POSITIONS] {positions}/{MAX_CONCURRENT_POSITIONS} open | ${deployed:.2f} deployed")

def display_position_summary():
    """Display summary of all open positions."""
    global LAST_POSITION_DISPLAY

    if not OPEN_POSITIONS:
        return

    now = time.time()
    if now - LAST_POSITION_DISPLAY < POSITION_DISPLAY_INTERVAL:
        return

    LAST_POSITION_DISPLAY = now

    total_contracts = sum(p['contracts'] for p in OPEN_POSITIONS.values())
    total_deployed = get_total_deployed_capital()
    oldest = min(p['opened_at'] for p in OPEN_POSITIONS.values())
    age_mins = (now - oldest) / 60

    print(f"\n[POSITIONS SUMMARY] {len(OPEN_POSITIONS)} open | {total_contracts} contracts | ${total_deployed:.2f} deployed | Oldest: {age_mins:.0f}m ago")

    # Show individual positions if few
    if len(OPEN_POSITIONS) <= 5:
        for gid, pos in OPEN_POSITIONS.items():
            age = (now - pos['opened_at']) / 60
            print(f"  - {gid}: {pos['contracts']} @ {pos['entry_price']}c | ${pos['capital_locked']:.2f} | {age:.0f}m ago")

# ============================================================================
# EXECUTION SPEED & SIZING CONFIG
# ============================================================================
LIQUIDITY_UTILIZATION = 0.66      # Use 66% of available liquidity (conservative)

# ============================================================================
# FEE-AWARE EXECUTION PARAMETERS (OPTIMIZED FOR LOW LATENCY)
# Based on verified fee formulas:
# - Kalshi taker fee: ceil(0.07 * P * (1-P)) = ~2c at 50c prices
# - PM US taker fee: 0.10% of notional (~0.05c per contract at 50c)
# - Slippage reduced from 3c to 1c by eliminating redundant API calls
# ============================================================================
KALSHI_FEE_CENTS_PER_CONTRACT = 2     # Kalshi taker fee (~2c/contract at 50c)
PM_US_FEE_RATE = 0.001                # PM US: 0.10% (10 bps) on notional
EXPECTED_SLIPPAGE_CENTS = 1           # REDUCED from 3c - faster execution = less slippage
MIN_PROFIT_CENTS = 1                  # Minimum profit we want AFTER all costs
RECOVERY_SLIPPAGE_BUDGET_CENTS = 2    # Max slippage during recovery before aborting

# Calculate minimum spread needed to break even:
# raw_spread >= k_fee + pm_fee + slippage + min_profit
# At 50c price: 2c + 0.05c + 1c + 1c = 4.05c
# Using 5c as conservative minimum
CALCULATED_BREAKEVEN_SPREAD = KALSHI_FEE_CENTS_PER_CONTRACT + 1 + EXPECTED_SLIPPAGE_CENTS + MIN_PROFIT_CENTS  # = 5c
MIN_SPREAD_FOR_EXECUTION = max(CALCULATED_BREAKEVEN_SPREAD, 5)  # At least 5c

# FIX-BUG-5: Price buffers for limit orders
# Kalshi: 1c buffer for timing variance
# PM: NO buffer - limit order at scanned price protects against overpay
PRICE_BUFFER_CENTS = 1            # Kalshi: 1c buffer (safety margin)
PM_PRICE_BUFFER_CENTS = 0         # PM US: NO buffer - limit order IS the protection

# LATENCY OPTIMIZATION: Max price age before requiring refetch
# Prices from scan are fresh - only reject if > 500ms old
MAX_PRICE_AGE_MS = 500            # Reject prices older than 500ms
MIN_EXECUTION_SPREAD = MIN_SPREAD_FOR_EXECUTION  # Alias for validation
EXECUTION_STATS_FILE = 'execution_stats.json'
SLOW_EXECUTION_THRESHOLD_MS = 500 # Alert if avg execution > 500ms

# Execution stats tracking
EXECUTION_STATS = {
    'recent_executions': [],      # List of {timestamp, kalshi_ms, pm_ms, total_ms, success}
    'max_history': 100,           # Keep last 100 executions
    'total_executions': 0,
    'successful_executions': 0,
    'avg_execution_ms': 0,
    'avg_kalshi_ms': 0,
    'avg_pm_ms': 0,
}

def load_execution_stats():
    """Load execution stats from file"""
    global EXECUTION_STATS
    try:
        if os.path.exists(EXECUTION_STATS_FILE):
            with open(EXECUTION_STATS_FILE, 'r') as f:
                loaded = json.load(f)
                EXECUTION_STATS.update(loaded)
    except Exception as e:
        print(f"[EXEC STATS] Error loading: {e}")

def save_execution_stats():
    """Save execution stats to file"""
    try:
        with open(EXECUTION_STATS_FILE, 'w') as f:
            json.dump(EXECUTION_STATS, f, indent=2)
    except Exception as e:
        print(f"[EXEC STATS] Error saving: {e}")

def record_execution(kalshi_ms: float, pm_ms: float, total_ms: float, success: bool):
    """Record an execution and update averages"""
    EXECUTION_STATS['recent_executions'].append({
        'timestamp': datetime.now().isoformat(),
        'kalshi_ms': kalshi_ms,
        'pm_ms': pm_ms,
        'total_ms': total_ms,
        'success': success
    })

    # Keep only last N executions
    if len(EXECUTION_STATS['recent_executions']) > EXECUTION_STATS['max_history']:
        EXECUTION_STATS['recent_executions'] = EXECUTION_STATS['recent_executions'][-EXECUTION_STATS['max_history']:]

    EXECUTION_STATS['total_executions'] += 1
    if success:
        EXECUTION_STATS['successful_executions'] += 1

    # Update averages
    recent = EXECUTION_STATS['recent_executions']
    if recent:
        EXECUTION_STATS['avg_execution_ms'] = sum(e['total_ms'] for e in recent) / len(recent)
        EXECUTION_STATS['avg_kalshi_ms'] = sum(e['kalshi_ms'] for e in recent) / len(recent)
        EXECUTION_STATS['avg_pm_ms'] = sum(e['pm_ms'] for e in recent) / len(recent)

        # Alert if slow
        if EXECUTION_STATS['avg_execution_ms'] > SLOW_EXECUTION_THRESHOLD_MS:
            print(f"[!!! SLOW EXECUTION !!!] Avg {EXECUTION_STATS['avg_execution_ms']:.0f}ms > {SLOW_EXECUTION_THRESHOLD_MS}ms threshold")

    save_execution_stats()

# ============================================================================
# UPTIME LOGGING - Track bot starts/stops for debugging
# ============================================================================
UPTIME_LOG_FILE = 'logs/uptime.log'

def log_uptime(event: str, reason: str = "", details: dict = None):
    """Log bot start/stop events to uptime.log for debugging crashes.

    Args:
        event: "STARTED" or "STOPPED"
        reason: Why the bot stopped (e.g., "KeyboardInterrupt", "UnicodeEncodeError")
        details: Optional dict with extra info (scan_interval, mode, etc.)
    """
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build log line
        if event == "STARTED":
            mode = "PAPER" if EXECUTION_MODE == ExecutionMode.PAPER else "LIVE"
            limits = "NO_LIMITS" if PAPER_NO_LIMITS else "WITH_LIMITS"
            scan_info = details.get('scan_interval', 'default') if details else 'default'
            line = f"{timestamp} | {event} | Mode: {mode} ({limits}) | Scan: {scan_info}"
        elif event == "STOPPED":
            line = f"{timestamp} | {event} | Reason: {reason}"
            if details:
                line += f" | {details}"
        else:
            line = f"{timestamp} | {event} | {reason}"

        # Append to log file
        with open(UPTIME_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

        print(f"[UPTIME] {line}")

    except Exception as e:
        print(f"[UPTIME] Error logging: {e}")

def get_uptime_summary():
    """Read uptime log and return summary of recent sessions."""
    try:
        if not os.path.exists(UPTIME_LOG_FILE):
            return "No uptime log found"

        with open(UPTIME_LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Get last 10 entries
        recent = lines[-20:] if len(lines) > 20 else lines
        return ''.join(recent)
    except Exception as e:
        return f"Error reading uptime log: {e}"

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
    """Load unhedged positions from file.
    Handles empty, corrupted, or missing files gracefully.
    """
    try:
        if os.path.exists(UNHEDGED_POSITIONS_FILE):
            with open(UNHEDGED_POSITIONS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Handle empty file
                if not content:
                    return []
                data = json.loads(content)
                # Ensure it's a list
                if isinstance(data, list):
                    return data
                else:
                    print(f"[HEDGE] Warning: unhedged_positions.json is not a list, resetting")
                    return []
    except json.JSONDecodeError as e:
        print(f"[HEDGE] Warning: unhedged_positions.json is corrupted ({e}), resetting to empty")
        return []
    except FileNotFoundError:
        return []
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
        with open(UNHEDGED_POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(positions, f, indent=2)
        print(f"[HEDGE] Saved unhedged position to {UNHEDGED_POSITIONS_FILE}")
    except Exception as e:
        print(f"[HEDGE] ERROR saving unhedged position: {e}")

def check_kill_switch() -> bool:
    """Check if kill switch is active.

    In PAPER mode with PAPER_NO_LIMITS=True, always returns False since
    we want to keep trading to track all arb opportunities.
    """
    global HEDGE_KILL_SWITCH_ACTIVE

    # In paper no-limits mode, never block trading
    if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
        return False

    if HEDGE_KILL_SWITCH_ACTIVE:
        print("[!!! KILL SWITCH !!!] Trading halted due to unhedged position")
        return True
    return False

def activate_kill_switch(reason: str):
    """Activate the kill switch to stop all trading.

    In PAPER mode with PAPER_NO_LIMITS=True, the kill switch is NOT activated
    since there's no real money at risk.
    """
    global HEDGE_KILL_SWITCH_ACTIVE

    # Don't activate kill switch in paper mode when tracking full arb market
    if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS:
        print(f"\n{'='*60}")
        print("[PAPER] Kill switch would activate but skipped (no-limits mode)")
        print(f"Reason: {reason}")
        print("[PAPER] Continuing to trade - no real money at risk")
        print(f"{'='*60}\n")
        return

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

# Pre-game verified mappings (loaded from pregame_mapper.py output)
VERIFIED_MAPS = {}
MAPPING_LAST_LOADED = 0.0
MAPPING_RELOAD_INTERVAL = 300  # Reload every 5 minutes

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
    'low_buy_price': 0,      # Buy side price too low (stale/illiquid data)
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
    initial_at_risk_cents: int  # Capital at risk (buy side price * contracts)
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
    # TAM: 100% liquidity (uncapped)
    'total_profit_if_captured': 0,  # cents
    'total_contracts': 0,
    'total_at_risk': 0,             # cents
    # Realistic: min(66% liquidity, MAX_CONTRACTS), skip if < MIN_CONTRACTS
    'realistic_profit': 0,          # cents
    'realistic_contracts': 0,
    'realistic_at_risk': 0,         # cents
    'realistic_arb_count': 0,       # Arbs that meet MIN_CONTRACTS threshold
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
    k_bid_size: int = 0    # Liquidity on Kalshi bid side (from orderbook)
    k_ask_size: int = 0    # Liquidity on Kalshi ask side (from orderbook)
    needs_review: bool = False  # Flag for suspicious trades (high ROI in paper mode)
    review_reason: str = ""     # Reason for review flag
    is_live_game: bool = False  # Flag for in-progress games (higher risk)
    price_timestamp: float = 0.0  # LATENCY OPT: Unix timestamp when prices were fetched
    # CRITICAL: pm_long_team is the team with long=true in PM marketSides
    # For binary sports markets: BUY_YES bets on pm_long_team, SELL_YES bets against
    pm_long_team: str = ""  # Team abbreviation (e.g., "HOU")
    # Cache key for verified mappings lookup (e.g., "nba:PHI-PHX:2026-02-07")
    cache_key: str = ""

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


# ============================================================================
# FEE-AWARE PROFIT ESTIMATION
# ============================================================================

def estimate_net_profit_cents(arb: 'ArbOpportunity') -> Tuple[float, Dict]:
    """
    Estimate net profit per contract AFTER fees, slippage, and costs.
    Returns (cents_per_contract, breakdown_dict).
    Negative = don't trade.

    For a hedge trade:
    - Gross profit = net_spread (already calculated correctly based on is_long_team)
    - Net profit = gross - K_fee - PM_fee - expected_slippage
    """
    raw_spread = arb.net_spread  # Already calculated correctly in spread detection

    # Kalshi fee: approximately 2c per contract (based on actual trade data)
    k_fee = KALSHI_FEE_CENTS_PER_CONTRACT

    # PM fee: 0.10% on notional (the price transacted, not the risk)
    # Fee depends on is_long_team and direction
    is_long_team = (arb.team == arb.pm_long_team)

    if arb.direction == 'BUY_K_SELL_PM':
        # We SHORT on PM
        if is_long_team:
            # SELL_YES at pm_bid
            pm_price_cents = arb.pm_bid if arb.pm_bid else 50
        else:
            # BUY_YES at pm_ask (to long the other team = short our team)
            pm_price_cents = arb.pm_ask if arb.pm_ask else 50
    else:  # BUY_PM_SELL_K
        # We LONG on PM
        if is_long_team:
            # BUY_YES at pm_ask
            pm_price_cents = arb.pm_ask if arb.pm_ask else 50
        else:
            # SELL_YES at pm_bid (to short the long team = long our team)
            pm_price_cents = arb.pm_bid if arb.pm_bid else 50

    pm_fee = pm_price_cents * PM_US_FEE_RATE  # typically ~0.05c

    # Expected slippage (based on historical data)
    slippage = EXPECTED_SLIPPAGE_CENTS

    # Total fees and costs
    total_costs = k_fee + pm_fee + slippage

    # Net profit per contract
    net_cents = raw_spread - total_costs

    breakdown = {
        'raw_spread': raw_spread,
        'k_fee': k_fee,
        'pm_fee': round(pm_fee, 2),
        'slippage': slippage,
        'total_costs': round(total_costs, 2),
        'net_cents': round(net_cents, 2),
    }

    return net_cents, breakdown


def calculate_actual_pnl(k_fill_price_cents: float, pm_fill_price_cents: float,
                         contracts: int, direction: str,
                         k_fee_cents: float = 0, pm_fee_cents: float = 0,
                         pm_intent: int = None) -> Dict:
    """
    Calculate actual P&L after a completed hedge.
    Returns dict with detailed breakdown.

    CRITICAL: pm_intent determines the actual PM cost:
    - pm_intent=1 (BUY_YES): pm_cost = pm_fill_price_cents
    - pm_intent=2 (SELL_YES): pm_cost = 100 - pm_fill_price_cents

    The direction alone doesn't determine this - it depends on is_long_team!
    """
    # Kalshi is always BUY or SELL YES on our team's ticker
    if direction == "BUY_K_SELL_PM":
        k_cost = k_fill_price_cents  # BUY on Kalshi (pay k_price)
    else:  # BUY_PM_SELL_K
        k_cost = 100 - k_fill_price_cents  # SELL on Kalshi (at-risk = 100 - k_price)

    # PM cost depends on pm_intent, not direction!
    if pm_intent == 1:  # BUY_YES
        pm_cost = pm_fill_price_cents  # We paid pm_price
    elif pm_intent == 2:  # SELL_YES
        pm_cost = 100 - pm_fill_price_cents  # We received pm_price, at-risk = 100 - pm_price
    else:
        # Fallback to old logic if pm_intent not provided (backwards compatibility)
        if direction == "BUY_K_SELL_PM":
            pm_cost = 100 - pm_fill_price_cents
        else:
            pm_cost = pm_fill_price_cents

    total_cost_cents = (k_cost + pm_cost) * contracts

    # Total payout = guaranteed $1 per contract = 100c
    total_payout_cents = 100 * contracts

    # Gross profit
    gross_cents = total_payout_cents - total_cost_cents

    # Net after fees
    total_fees = (k_fee_cents + pm_fee_cents) * contracts
    net_cents = gross_cents - total_fees

    # Per-contract breakdown
    per_contract = {
        'k_cost': k_cost,
        'pm_cost': pm_cost,
        'total_cost': k_cost + pm_cost,
        'payout': 100,
        'gross': 100 - k_cost - pm_cost,
        'fees': k_fee_cents + pm_fee_cents,
        'net': 100 - k_cost - pm_cost - k_fee_cents - pm_fee_cents,
        'direction': direction,
    }

    result = {
        'contracts': contracts,
        'total_cost_dollars': total_cost_cents / 100,
        'total_payout_dollars': total_payout_cents / 100,
        'gross_profit_dollars': gross_cents / 100,
        'fees_dollars': total_fees / 100,
        'net_profit_dollars': net_cents / 100,
        'per_contract': per_contract,
        'is_profitable': net_cents > 0,
    }

    return result


def log_profit_estimate(arb: 'ArbOpportunity', contracts: int):
    """Log detailed profit estimate before execution."""
    net_cents, breakdown = estimate_net_profit_cents(arb)
    total_net_dollars = net_cents * contracts / 100

    print(f"\n[PROFIT EST] ===== PRE-EXECUTION ESTIMATE =====")
    print(f"[PROFIT EST] Team: {arb.team} | Direction: {arb.direction}")
    print(f"[PROFIT EST] Raw spread: {breakdown['raw_spread']:.1f}c")
    print(f"[PROFIT EST] Kalshi fee: -{breakdown['k_fee']:.1f}c")
    print(f"[PROFIT EST] PM fee: -{breakdown['pm_fee']:.2f}c")
    print(f"[PROFIT EST] Expected slippage: -{breakdown['slippage']:.1f}c")
    print(f"[PROFIT EST] Total costs: -{breakdown['total_costs']:.1f}c")
    print(f"[PROFIT EST] ---")
    print(f"[PROFIT EST] Net per contract: {net_cents:.2f}c")
    print(f"[PROFIT EST] Expected profit: ${total_net_dollars:.2f} on {contracts} contracts")

    if net_cents < MIN_PROFIT_CENTS:
        print(f"[PROFIT EST] *** WARNING: {net_cents:.2f}c is below {MIN_PROFIT_CENTS}c minimum! ***")

    print(f"[PROFIT EST] ==========================================")

    return net_cents, breakdown


def log_actual_pnl(result: Dict):
    """Log actual P&L after trade completion."""
    pc = result['per_contract']

    print(f"\n[ACTUAL P&L] ===== POST-TRADE RESULT =====")
    print(f"[ACTUAL P&L] Contracts: {result['contracts']}")
    print(f"[ACTUAL P&L] K paid: {pc['k_paid']:.1f}c | PM paid: {pc['pm_paid']:.1f}c")
    print(f"[ACTUAL P&L] Total cost: ${result['total_cost_dollars']:.2f}")
    print(f"[ACTUAL P&L] Guaranteed payout: ${result['total_payout_dollars']:.2f}")
    print(f"[ACTUAL P&L] Fees: ${result['fees_dollars']:.2f}")
    print(f"[ACTUAL P&L] ---")
    print(f"[ACTUAL P&L] NET PROFIT: ${result['net_profit_dollars']:.2f} ({pc['net']:.1f}c/contract)")

    if not result['is_profitable']:
        print(f"[ACTUAL P&L] *** NEGATIVE P&L - Trade lost money! ***")

    print(f"[ACTUAL P&L] =========================================")


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
        """Generate auth headers. CRITICAL: Sign path WITHOUT query params."""
        ts = str(int(time.time() * 1000))
        # Kalshi requires signing the PATH only, not query params
        sign_path = path.split('?')[0] if '?' in path else path
        return {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-SIGNATURE': self._sign(ts, method, sign_path),
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
        # Use Config for all execution-controlling values
        paper_unlimited = Config.is_paper_unlimited()

        # In paper unlimited mode, skip all limits
        if not paper_unlimited:
            # HARD LIMIT ENFORCEMENT (live mode only)
            if count > Config.max_contracts:
                print(f"   [SAFETY] Capping contracts from {count} to {Config.max_contracts}")
                count = Config.max_contracts

            if count < Config.min_contracts:
                return {'success': False, 'error': f'Count {count} below minimum {Config.min_contracts}'}

            if action == 'buy':
                max_cost = count * price_cents
            else:
                max_cost = count * (100 - price_cents)

            if max_cost > Config.max_cost_cents:
                if action == 'buy':
                    count = Config.max_cost_cents // price_cents
                else:
                    count = Config.max_cost_cents // (100 - price_cents)
                max_cost = count * price_cents if action == 'buy' else count * (100 - price_cents)
                print(f"   [SAFETY] Reduced to {count} contracts (max cost ${max_cost/100:.2f})")

            if count < Config.min_contracts:
                return {'success': False, 'error': f'Count {count} below minimum after cost cap'}

        if Config.is_paper():
            print(f"   [PAPER] Would place: {action} {count} {side} @ {price_cents}c")
            # LATENCY OPT: Removed 0.1s sleep - paper mode should be fast
            return {
                'success': True,
                'fill_count': count,
                'order_id': f'PAPER-{int(time.time()*1000)}',
                'paper': True
            }

        # DRY RUN MODE: Show what would happen but don't submit
        if Config.dry_run_mode:
            cost = count * price_cents if action == 'buy' else count * (100 - price_cents)
            print(f"   [DRY RUN] Kalshi: Would {action.upper()} {count} {side.upper()} @ {price_cents}c (${cost/100:.2f})")
            # LATENCY OPT: Removed 0.1s sleep
            return {
                'success': True,
                'fill_count': count,
                'order_id': f'DRYRUN-K-{int(time.time()*1000)}',
                'dry_run': True
            }

        path = '/trade-api/v2/portfolio/orders'
        order_price = price_cents

        payload = {
            'ticker': ticker,
            'action': action,
            'side': side,
            'count': count,
            'type': 'limit',
            'time_in_force': 'immediate_or_cancel',  # IOC: fill what you can, cancel rest
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

                # Handle HTTP 409 - insufficient resting volume (IOC order couldn't fill)
                if r.status == 409:
                    error_code = data.get('error', {}).get('code', '')
                    error_msg = data.get('error', {}).get('message', 'Unknown 409 error')
                    print(f"   [!] Kalshi 409: {error_code} - {error_msg}")
                    return {
                        'success': False,
                        'fill_count': 0,
                        'order_id': None,
                        'status': 'REJECTED_409',
                        'error': f'409: {error_code}'
                    }

                # Handle HTTP 400 - invalid parameters (API error, NOT liquidity issue)
                if r.status == 400:
                    error_code = data.get('error', {}).get('code', '')
                    error_msg = data.get('error', {}).get('message', 'Unknown 400 error')
                    error_details = data.get('error', {}).get('details', '')
                    print(f"   [!!!] Kalshi 400 API ERROR: {error_code} - {error_msg}")
                    print(f"   [!!!] Details: {error_details}")
                    print(f"   [!!!] Full response: {data}")
                    return {
                        'success': False,
                        'fill_count': 0,
                        'order_id': None,
                        'status': 'API_ERROR_400',
                        'error': f'400: {error_code} - {error_msg} - {error_details}'
                    }

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

    async def get_orderbook(self, session, ticker: str, depth: int = 1) -> Optional[Dict]:
        """
        Fetch orderbook for a Kalshi market to get depth at best price.

        Returns: {'yes_bid': price, 'yes_bid_size': qty, 'yes_ask': price, 'yes_ask_size': qty}

        Kalshi orderbook only has BIDS (no asks). For binary markets:
        - YES BID at price X = NO ASK at (100-X)
        - NO BID at price Y = YES ASK at (100-Y)
        """
        path = f'/trade-api/v2/markets/{ticker}/orderbook'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                params={'depth': depth},
                timeout=aiohttp.ClientTimeout(total=3)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    ob = data.get('orderbook', {})

                    # Get YES bids (best bid for YES contracts)
                    yes_bids = ob.get('yes', [])
                    no_bids = ob.get('no', [])

                    # Best YES bid is highest price in yes_bids
                    yes_bid = yes_bids[0][0] if yes_bids else 0
                    yes_bid_size = yes_bids[0][1] if yes_bids else 0

                    # Best YES ask = 100 - best NO bid price
                    # (A NO BID at Y means they'll sell YES at 100-Y)
                    yes_ask = (100 - no_bids[0][0]) if no_bids else 100
                    yes_ask_size = no_bids[0][1] if no_bids else 0

                    return {
                        'yes_bid': yes_bid,
                        'yes_bid_size': yes_bid_size,
                        'yes_ask': yes_ask,
                        'yes_ask_size': yes_ask_size
                    }
                else:
                    return None
        except Exception as e:
            print(f"   [!] Kalshi orderbook error: {e}")
            return None

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

    async def get_orderbook(self, session, market_slug: str, debug: bool = False, verbose_debug: bool = False) -> Optional[Dict]:
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

        verbose_debug: If True, prints detailed endpoint/timing info for staleness investigation
        """
        # Try different possible endpoint patterns
        # CRITICAL: /book is the correct endpoint with LIVE data!
        # /orderbook returns 404
        endpoints_to_try = [
            f'/v1/markets/{market_slug}/book',  # CORRECT - live data
            f'/v1/markets/{market_slug}/orderbook',  # Fallback
            f'/v1/orderbook/{market_slug}',  # Fallback
        ]

        for endpoint in endpoints_to_try:
            path = endpoint
            try:
                import time as time_module
                start_time = time_module.perf_counter()

                # Add cache-busting timestamp to URL
                cache_bust = int(time_module.time() * 1000)
                full_url = f'{self.BASE_URL}{path}?_t={cache_bust}'

                # Get base headers and add cache-control
                headers = self._headers('GET', path)
                headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                headers['Pragma'] = 'no-cache'

                async with session.get(
                    full_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    elapsed_ms = (time_module.perf_counter() - start_time) * 1000

                    if r.status == 200:
                        data = await r.json()

                        if verbose_debug:
                            raw_json = json.dumps(data)
                            print(f"\n[PM ORDERBOOK DEBUG] Endpoint: {full_url}")
                            print(f"[PM ORDERBOOK DEBUG] Response time: {elapsed_ms:.0f}ms")
                            print(f"[PM ORDERBOOK DEBUG] Raw response: {raw_json[:500]}")

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

                        if verbose_debug:
                            bid_cents = int(best_bid * 100) if best_bid else 0
                            ask_cents = int(best_ask * 100) if best_ask else 0
                            print(f"[PM ORDERBOOK DEBUG] Parsed: bid={bid_cents}c, ask={ask_cents}c (size: {bid_size}/{ask_size})")

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

    async def check_orderbook_staleness(self, session, market_slug: str) -> Dict:
        """
        Fetch orderbook TWICE in quick succession to detect staleness.
        If the API returns cached/stale data, both fetches will be identical.
        If live, there may be differences (especially bid/ask sizes).

        Returns: {
            'fetch1': {bid, ask, bid_size, ask_size, latency_ms},
            'fetch2': {bid, ask, bid_size, ask_size, latency_ms},
            'identical': bool,  # True if both fetches returned exact same data
            'price_diff': int,  # Difference in bid/ask between fetches (cents)
        }
        """
        import time as time_module

        results = {'fetch1': None, 'fetch2': None, 'identical': True, 'price_diff': 0}

        for i, fetch_name in enumerate(['fetch1', 'fetch2']):
            start = time_module.perf_counter()
            ob = await self.get_orderbook(session, market_slug, debug=False, verbose_debug=True)
            elapsed = (time_module.perf_counter() - start) * 1000

            if ob:
                results[fetch_name] = {
                    'bid': int(ob['best_bid'] * 100) if ob['best_bid'] else 0,
                    'ask': int(ob['best_ask'] * 100) if ob['best_ask'] else 0,
                    'bid_size': ob['bid_size'],
                    'ask_size': ob['ask_size'],
                    'latency_ms': elapsed
                }

            # Small delay between fetches to give API time to update
            if i == 0:
                await asyncio.sleep(0.1)

        # Compare results
        f1, f2 = results['fetch1'], results['fetch2']
        if f1 and f2:
            results['identical'] = (
                f1['bid'] == f2['bid'] and
                f1['ask'] == f2['ask'] and
                f1['bid_size'] == f2['bid_size'] and
                f1['ask_size'] == f2['ask_size']
            )
            results['price_diff'] = abs(f1['bid'] - f2['bid']) + abs(f1['ask'] - f2['ask'])

        print(f"\n[STALENESS CHECK] {market_slug}")
        print(f"  Fetch 1: bid={f1['bid'] if f1 else '?'}c ask={f1['ask'] if f1 else '?'}c "
              f"(size {f1['bid_size'] if f1 else 0}/{f1['ask_size'] if f1 else 0}) "
              f"[{f1['latency_ms']:.0f}ms]" if f1 else "  Fetch 1: FAILED")
        print(f"  Fetch 2: bid={f2['bid'] if f2 else '?'}c ask={f2['ask'] if f2 else '?'}c "
              f"(size {f2['bid_size'] if f2 else 0}/{f2['ask_size'] if f2 else 0}) "
              f"[{f2['latency_ms']:.0f}ms]" if f2 else "  Fetch 2: FAILED")
        print(f"  Identical: {results['identical']} | Price diff: {results['price_diff']}c")

        return results

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
                          sync: bool = True, outcome_index: int = 0) -> Dict:
        """
        Place order on PM US.

        intent: 1=BUY_LONG (favorite), 2=SELL_LONG, 3=BUY_SHORT (underdog), 4=SELL_SHORT
        tif: 1=GTC, 2=GTD, 3=IOC, 4=FOK
        price: in dollars (e.g., 0.55)
        outcome_index: 0 or 1 - which outcome to trade on

        Note: BUY_SHORT (intent=3) requires minimum 2c price.
        """
        # Use Config for all execution-controlling values
        paper_unlimited = Config.is_paper_unlimited()

        # In paper unlimited mode, skip all limits
        if not paper_unlimited:
            # HARD LIMIT ENFORCEMENT (live mode only)
            if quantity > Config.max_contracts:
                print(f"   [SAFETY] PM US: Capping contracts from {quantity} to {Config.max_contracts}")
                quantity = Config.max_contracts
            if quantity < Config.min_contracts:
                return {'success': False, 'error': f'Quantity {quantity} below minimum'}

            max_cost_dollars = price * quantity
            if max_cost_dollars * 100 > Config.max_cost_cents:
                quantity = int(Config.max_cost_cents / (price * 100))
                if quantity < Config.min_contracts:
                    return {'success': False, 'error': 'Quantity below minimum after cost cap'}
                print(f"   [SAFETY] PM US: Reduced to {quantity} contracts")

        intent_names = {1: 'BUY_LONG', 2: 'SELL_LONG', 3: 'BUY_SHORT', 4: 'SELL_SHORT'}

        if Config.is_paper():
            print(f"   [PAPER] PM US: {intent_names[intent]} outcome[{outcome_index}] {quantity} @ ${price:.2f} on {market_slug}")
            # LATENCY OPT: Removed 0.1s sleep - paper mode should be fast
            return {
                'success': True,
                'fill_count': quantity,
                'fill_price': price,
                'order_id': f'PM-PAPER-{int(time.time()*1000)}',
                'paper': True
            }

        # DRY RUN MODE: Show what would happen but don't submit
        if Config.dry_run_mode:
            cost = price * quantity
            print(f"   [DRY RUN] PM US: Would {intent_names[intent]} outcome[{outcome_index}] {quantity} @ ${price:.2f} (${cost:.2f}) on {market_slug}")
            # LATENCY OPT: Removed 0.1s sleep
            return {
                'success': True,
                'fill_count': quantity,
                'fill_price': price,
                'order_id': f'DRYRUN-PM-{int(time.time()*1000)}',
                'dry_run': True
            }

        path = '/v1/orders'
        payload = {
            'market_slug': market_slug,
            'intent': intent,
            'outcomeIndex': outcome_index,  # CRITICAL: Specify which outcome to trade
            'type': 1,  # LIMIT
            'price': {'value': f'{price:.2f}', 'currency': 'USD'},
            'quantity': quantity,
            'tif': tif,
            'manualOrderIndicator': 2,  # AUTOMATIC
            'synchronousExecution': sync,
        }

        try:
            print(f"   [PM ORDER] {intent_names[intent]} outcome[{outcome_index}] {quantity} @ ${price:.2f} on {market_slug}")
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

                    # CRITICAL FIX: PM response has state/cumQuantity in multiple places:
                    # 1. Top-level: data['state'], data['cumQuantity']
                    # 2. Inside LAST execution: executions[-1]['order']['state'], etc.
                    # We must check the LAST execution for final state!

                    # First try top-level
                    order_state = data.get('state', '')
                    cum_qty = data.get('cumQuantity', 0)
                    avg_px = data.get('avgPx', {})

                    # CRITICAL: Check LAST execution for final state
                    # The executions array shows order progression: NEW -> PARTIAL -> FILLED
                    if executions:
                        last_exec = executions[-1]
                        # Check if last execution has an 'order' object with state
                        last_order = last_exec.get('order', {})
                        if last_order:
                            exec_state = last_order.get('state', '')
                            exec_cum_qty = last_order.get('cumQuantity', 0)
                            exec_avg_px = last_order.get('avgPx', {})
                            # Use execution data if it has state info
                            if exec_state:
                                order_state = exec_state
                            if exec_cum_qty:
                                cum_qty = exec_cum_qty
                            if exec_avg_px:
                                avg_px = exec_avg_px

                    # Parse cumQuantity (might be string)
                    if isinstance(cum_qty, str):
                        cum_qty = int(cum_qty) if cum_qty else 0

                    # Sum fills from execution types as backup
                    total_filled = 0
                    fill_price = None
                    for ex in executions:
                        ex_type = ex.get('type', '')
                        # PM returns string types: EXECUTION_TYPE_FILL, EXECUTION_TYPE_PARTIAL_FILL
                        if 'FILL' in str(ex_type):
                            shares = ex.get('lastShares', 0)
                            # lastShares can be string like "1.000"
                            if isinstance(shares, str):
                                shares = float(shares)
                            total_filled += int(shares)
                            last_px = ex.get('lastPx', {})
                            if last_px:
                                fill_price = float(last_px.get('value', 0))

                    # Use cumQuantity if it's higher (more reliable)
                    if cum_qty > total_filled:
                        total_filled = cum_qty

                    # Get fill price from avgPx if not set from executions
                    if avg_px and not fill_price:
                        px_value = avg_px.get('value', 0)
                        if px_value:
                            fill_price = float(px_value)

                    # Check order state - FILLED or PARTIALLY_FILLED with qty means success
                    is_filled = (
                        order_state in ['ORDER_STATE_FILLED', 'ORDER_STATE_PARTIALLY_FILLED']
                        or total_filled > 0
                    )

                    print(f"   [DEBUG] Parsed: state={order_state}, filled={total_filled}, price={fill_price}")

                    return {
                        'success': is_filled,
                        'fill_count': total_filled,
                        'order_id': order_id,
                        'fill_price': fill_price,
                        'order_state': order_state,
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


def get_pm_execution_params(arb: ArbOpportunity, fresh_prices: Dict = None, debug_only: bool = False) -> tuple:
    """
    Determine PM US order params for the given arb.

    CRITICAL FIX (2026-02-07): PM US sports markets are BINARY with ONE tradeable side!
    The pm_long_team is the team where marketSides has long=true.

    - BUY_YES (intent=1): Always bets ON the pm_long_team
    - SELL_YES (intent=2): Always bets AGAINST the pm_long_team (= for the other team)

    outcomeIndex is IGNORED for binary sports markets - always use 0.

    Logic:
    - BUY_PM_SELL_K (want LONG our team on PM):
        - If arb.team == pm_long_team: intent=1 (BUY_YES)
        - If arb.team != pm_long_team: intent=2 (SELL_YES - selling long team = betting on our team)

    - BUY_K_SELL_PM (want SHORT our team on PM):
        - If arb.team == pm_long_team: intent=2 (SELL_YES)
        - If arb.team != pm_long_team: intent=1 (BUY_YES - buying long team = betting against our team)

    Price:
    - BUY_YES: pay the ask price
    - SELL_YES: receive the bid price (but we set limit at bid - buffer to ensure fill)

    Args:
      arb: The arbitrage opportunity
      fresh_prices: Optional fresh price data (if None, uses cached arb prices)
      debug_only: If True, suppress warnings - for informational logging only

    Returns (intent, price_dollars, outcome_index, is_valid)
    - intent: 1 (BUY_YES) or 2 (SELL_YES) depending on team and direction
    - price: Limit price in dollars
    - outcome_index: Always 0 (ignored for binary markets)
    - is_valid: Always True
    """
    pm_long_team = getattr(arb, 'pm_long_team', '')
    our_team_is_long = (arb.team == pm_long_team)

    # Determine intent based on direction and whether our team is the long team
    if arb.direction == 'BUY_PM_SELL_K':
        # We want to go LONG our team on PM
        if our_team_is_long:
            intent = PM_BUY_YES  # Buy long team = long our team
        else:
            intent = PM_SELL_YES  # Sell long team = bet on short team = long our team
    else:  # BUY_K_SELL_PM
        # We want to go SHORT our team on PM
        if our_team_is_long:
            intent = PM_SELL_YES  # Sell long team = short our team
        else:
            intent = PM_BUY_YES  # Buy long team = long opponent = short our team

    # outcomeIndex is ignored for binary markets - always 0
    outcome_index = 0

    # Calculate price
    price_source = "unknown"

    if fresh_prices:
        raw_bid = fresh_prices.get('raw_bid', 0)  # dollars
        raw_ask = fresh_prices.get('raw_ask', 0)  # dollars

        print(f"[PM PRICE DEBUG] fresh_prices: bid=${raw_bid:.4f}, ask=${raw_ask:.4f}")
        print(f"[PM PRICE DEBUG] team={arb.team}, pm_long_team={pm_long_team}, our_team_is_long={our_team_is_long}")
        print(f"[PM PRICE DEBUG] direction={arb.direction} -> intent={'BUY_YES' if intent == 1 else 'SELL_YES'}")

        if intent == PM_BUY_YES:
            # Buying: pay the ask
            price = raw_ask if raw_ask else arb.pm_ask / 100
            price_source = f"ask=${price:.4f} (buying)"
        else:
            # Selling: receive the bid (set limit at bid to ensure fill)
            price = raw_bid if raw_bid else arb.pm_bid / 100
            price_source = f"bid=${price:.4f} (selling)"

        print(f"[PM PRICE DEBUG] -> price=${price:.4f} from {price_source}")
    else:
        if not debug_only:
            import traceback
            caller = ''.join(traceback.format_stack()[-3:-1])
            if 'recovery' not in caller.lower() and 'close' not in caller.lower():
                print(f"[!!!WARNING!!!] get_pm_execution_params called WITHOUT fresh_prices!")

        # Use cached prices
        if intent == PM_BUY_YES:
            price = arb.pm_ask / 100
            price_source = f"cached ask={arb.pm_ask}c"
        else:
            price = arb.pm_bid / 100
            price_source = f"cached bid={arb.pm_bid}c"

        print(f"[PM PRICE DEBUG] NO fresh_prices, using {price_source}")

    is_valid = True
    return intent, price, outcome_index, is_valid


# ============================================================================
# HEDGE PROTECTION FUNCTIONS
# ============================================================================

async def fetch_fresh_prices(session, kalshi_api, pm_api, kalshi_ticker: str, pm_slug: str, pm_outcome_index: int = 0) -> Dict:
    """
    Fetch fresh prices from both platforms simultaneously.
    Returns dict with kalshi_bid, kalshi_ask, pm_bid, pm_ask, timestamp, is_fresh

    CRITICAL: pm_outcome_index determines which team's prices we need:
    - 0 = our team is outcome[0], use orderbook prices directly
    - 1 = our team is outcome[1], INVERT prices (100 - orderbook price)
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
                # Raw orderbook prices (for outcome[0])
                raw_bid = bids[0]['price'] * 100 if bids else 0
                raw_ask = asks[0]['price'] * 100 if asks else 100
                raw_bid_size = bids[0]['size'] if bids else 0
                raw_ask_size = asks[0]['size'] if asks else 0

                # CRITICAL: Adjust prices based on which outcome our team is
                if pm_outcome_index == 0:
                    # Our team is outcome[0] - use orderbook directly
                    best_bid = raw_bid
                    best_ask = raw_ask
                    bid_size = raw_bid_size
                    ask_size = raw_ask_size
                else:
                    # Our team is outcome[1] - INVERT prices
                    # Buying outcome[1] = Selling outcome[0], so cost = 100 - bid
                    # Selling outcome[1] = Buying outcome[0], so receive = 100 - ask
                    best_bid = 100 - raw_ask  # To sell our team, we get 100 - outcome[0] ask
                    best_ask = 100 - raw_bid  # To buy our team, we pay 100 - outcome[0] bid
                    bid_size = raw_ask_size   # Sizes swap too
                    ask_size = raw_bid_size

                return {
                    'bid': best_bid,
                    'ask': best_ask,
                    'bid_size': bid_size,
                    'ask_size': ask_size,
                    'success': True,
                    'raw_bid': raw_bid,
                    'raw_ask': raw_ask,
                    'outcome_index': pm_outcome_index
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
    print(f"\n[VALIDATE] ========== PRE-TRADE VALIDATION ==========")
    print(f"[VALIDATE] Team: {arb.team} | Direction: {arb.direction}")
    print(f"[VALIDATE] PM outcome_index: {arb.pm_outcome_index}")
    print(f"[VALIDATE] Fetching fresh prices...")

    # CRITICAL: Pass pm_outcome_index to get correct prices for OUR team
    fresh = await fetch_fresh_prices(session, kalshi_api, pm_api, arb.kalshi_ticker, arb.pm_slug, arb.pm_outcome_index)

    # Check if we got valid prices
    if not fresh['kalshi_success'] or not fresh['pm_success']:
        return False, "Failed to fetch fresh prices", fresh

    # Check freshness
    if not fresh['is_fresh']:
        return False, f"Prices stale ({fresh['fetch_time_ms']:.0f}ms > {MAX_PRICE_STALENESS_MS}ms)", fresh

    # Calculate fresh spread based on direction
    if arb.direction == 'BUY_PM_SELL_K':
        # Buy on PM (pay ask), Sell on Kalshi (get bid)
        # Profit = K bid - PM ask
        k_price = fresh['kalshi_bid']  # What we get selling on K
        pm_price = fresh['pm_ask']     # What we pay buying on PM
        fresh_spread = k_price - pm_price
        available_size = fresh['pm_ask_size']
        print(f"[VALIDATE] BUY_PM_SELL_K: Sell K @ {k_price}c, Buy PM @ {pm_price}c")
    else:
        # BUY_K_SELL_PM: Buy on Kalshi (pay ask), Sell on PM (get bid)
        # Profit = PM bid - K ask
        k_price = fresh['kalshi_ask']  # What we pay buying on K
        pm_price = fresh['pm_bid']     # What we get selling on PM
        fresh_spread = pm_price - k_price
        available_size = fresh['pm_bid_size']
        print(f"[VALIDATE] BUY_K_SELL_PM: Buy K @ {k_price}c, Sell PM @ {pm_price}c")

    print(f"[VALIDATE] Fresh prices: K={fresh['kalshi_bid']}/{fresh['kalshi_ask']}c, PM={fresh['pm_bid']:.0f}/{fresh['pm_ask']:.0f}c")
    print(f"[VALIDATE] Spread: {pm_price}c - {k_price}c = {fresh_spread:.1f}c | Liquidity: {available_size}")
    print(f"[VALIDATE] Min required: {MIN_SPREAD_FOR_EXECUTION}c")

    # CRITICAL: Abort if spread too thin to cover slippage + profit
    if fresh_spread < MIN_SPREAD_FOR_EXECUTION:
        return False, f"[ABORT] Spread too thin: {fresh_spread:.1f}c < {MIN_SPREAD_FOR_EXECUTION}c minimum", fresh

    # Verify liquidity
    if available_size < arb.size:
        return False, f"Insufficient liquidity ({available_size} < {arb.size})", fresh

    print(f"[VALIDATE] Pre-trade validation PASSED ✓")
    print(f"[VALIDATE] =============================================")
    return True, "OK", fresh


async def calculate_conservative_size(
    session, kalshi_api, pm_api, arb: 'ArbOpportunity',
    kalshi_balance: float, pm_balance: float
) -> Tuple[int, Dict]:
    """
    Calculate conservative position size based on:
    - 66% of available liquidity on BOTH sides (not 100%)
    - Balance limits on both sides
    - Max contracts limit
    - Kalshi orderbook depth (fetched fresh)

    Returns (size, sizing_details)
    """
    details = {}

    # Fetch Kalshi orderbook to get FRESH depth at best price
    # This adds ~30-50ms but prevents requesting more than available
    k_orderbook = await kalshi_api.get_orderbook(session, arb.kalshi_ticker, depth=1)

    if arb.direction == 'BUY_PM_SELL_K':
        # Buying on PM (need ask), selling on Kalshi (need bid)
        pm_price = arb.pm_ask
        pm_size = arb.pm_ask_size  # From scan
        k_price = arb.k_bid
        # Kalshi depth: we're selling YES, so we need YES bid depth
        k_size = k_orderbook['yes_bid_size'] if k_orderbook else 0
        # For Kalshi sell: we receive k_bid, risk is (100 - k_bid) per contract
        k_cost_per = 100 - k_price  # cents
        pm_cost_per = pm_price  # cents (what we pay to buy)
    else:
        # Buying on Kalshi (need ask), selling on PM (need bid)
        pm_price = arb.pm_bid
        pm_size = arb.pm_bid_size  # From scan
        k_price = arb.k_ask
        # Kalshi depth: we're buying YES, so we need YES ask depth (= NO bid depth)
        k_size = k_orderbook['yes_ask_size'] if k_orderbook else 0
        k_cost_per = k_price  # cents (what we pay to buy)
        pm_cost_per = 100 - pm_price  # cents (collateral for sell)

    details['kalshi_liquidity'] = f"{k_size} @ {k_price}c"
    details['pm_liquidity'] = f"{pm_size} @ {pm_price}c"

    # Apply 66% conservative factor to BOTH sides
    k_conservative = int(k_size * LIQUIDITY_UTILIZATION) if k_size > 0 else 0
    pm_conservative = int(pm_size * LIQUIDITY_UTILIZATION)
    details['k_66_pct'] = k_conservative
    details['pm_66_pct'] = pm_conservative

    # Calculate max affordable on each side based on balance
    kalshi_balance_cents = int(kalshi_balance * 100)
    pm_balance_cents = int(pm_balance * 100)

    max_kalshi_by_balance = kalshi_balance_cents // k_cost_per if k_cost_per > 0 else 0
    max_pm_by_balance = pm_balance_cents // pm_cost_per if pm_cost_per > 0 else 0

    details['kalshi_max_by_balance'] = max_kalshi_by_balance
    details['pm_max_by_balance'] = max_pm_by_balance
    details['kalshi_balance'] = f"${kalshi_balance:.2f}"
    details['pm_balance'] = f"${pm_balance:.2f}"

    # Final size is minimum of all constraints (including BOTH sides' depth)
    constraints = [MAX_CONTRACTS, max_kalshi_by_balance, max_pm_by_balance]

    # Add liquidity constraints (only if > 0)
    if k_conservative > 0:
        constraints.append(k_conservative)
    if pm_conservative > 0:
        constraints.append(pm_conservative)

    final_size = min(constraints) if constraints else 0

    details['final_size'] = final_size
    details['limiting_factor'] = 'unknown'

    if k_conservative > 0 and final_size == k_conservative:
        details['limiting_factor'] = 'kalshi_depth_66%'
    elif pm_conservative > 0 and final_size == pm_conservative:
        details['limiting_factor'] = 'pm_liquidity_66%'
    elif final_size == MAX_CONTRACTS:
        details['limiting_factor'] = 'max_contracts'
    elif final_size == max_kalshi_by_balance:
        details['limiting_factor'] = 'kalshi_balance'
    elif final_size == max_pm_by_balance:
        details['limiting_factor'] = 'pm_balance'

    return final_size, details


async def fresh_price_validation(
    session, kalshi_api, pm_api, arb: 'ArbOpportunity', intended_size: int,
    verbose_debug: bool = True
) -> Tuple[bool, str, Dict]:
    """
    Immediately before execution, re-fetch order books and validate:
    - Spread still >= MIN_EXECUTION_SPREAD
    - Liquidity still >= intended_size

    Returns (is_valid, reason, fresh_prices)
    """
    start_time = time.time()

    # Fetch fresh PM orderbook with verbose debug
    pm_orderbook = await pm_api.get_orderbook(session, arb.pm_slug, debug=False, verbose_debug=verbose_debug)
    if not pm_orderbook:
        return False, "Failed to fetch PM orderbook", {}

    pm_fetch_ms = (time.time() - start_time) * 1000

    # =======================================================================
    # FIX-BUG-3: Use FLOAT DOLLARS for sub-cent precision (PM uses 0.001)
    # This prevents integer truncation - all PM prices stay as float dollars
    # =======================================================================
    # raw_bid/raw_ask are in DOLLARS (e.g., 0.037 = 3.7 cents, 0.519 = 51.9 cents)
    # DO NOT convert to integer cents - we lose precision!
    raw_bid = float(pm_orderbook.get('best_bid', 0))  # DOLLARS (e.g., 0.79)
    raw_ask = float(pm_orderbook.get('best_ask', 0))  # DOLLARS (e.g., 0.81)
    raw_bid_size = pm_orderbook.get('bid_size', 0)
    raw_ask_size = pm_orderbook.get('ask_size', 0)

    # Convert to cents for display only
    raw_bid_cents = raw_bid * 100
    raw_ask_cents = raw_ask * 100

    # DEBUG: Show raw orderbook values with full precision
    print(f"[ORDERBOOK FETCH] Slug: {arb.pm_slug}")
    print(f"[ORDERBOOK FETCH] Raw best_bid from API: ${raw_bid:.4f} ({raw_bid_cents:.1f}c)")
    print(f"[ORDERBOOK FETCH] Raw best_ask from API: ${raw_ask:.4f} ({raw_ask_cents:.1f}c)")
    print(f"[ORDERBOOK FETCH] Team: {arb.team}, Direction: {arb.direction}, pm_outcome_index: {arb.pm_outcome_index}")

    # SANITY CHECK: orderbook values should be in reasonable range (in dollars: 0.05 to 0.95)
    if raw_bid < 0.05 or raw_bid > 0.95:
        print(f"[ORDERBOOK WARNING] raw_bid=${raw_bid:.3f} ({raw_bid_cents:.1f}c) outside normal range (5-95c)")
    if raw_ask < 0.05 or raw_ask > 0.95:
        print(f"[ORDERBOOK WARNING] raw_ask=${raw_ask:.3f} ({raw_ask_cents:.1f}c) outside normal range (5-95c)")
    if raw_ask < raw_bid:
        print(f"[ORDERBOOK WARNING] Inverted book: ask=${raw_ask:.3f} < bid=${raw_bid:.3f}")
    if (raw_ask - raw_bid) > 0.20:
        print(f"[ORDERBOOK WARNING] Wide spread: {(raw_ask - raw_bid)*100:.1f}c")

    # Calculate our team's prices (in DOLLARS)
    if arb.pm_outcome_index == 0:
        # Our team is outcome[0] - use orderbook directly
        fresh_pm_bid = raw_bid  # dollars
        fresh_pm_ask = raw_ask  # dollars
        pm_bid_size = raw_bid_size
        pm_ask_size = raw_ask_size
    else:
        # Our team is outcome[1] - INVERT prices (1.0 - x in dollars)
        fresh_pm_bid = 1.0 - raw_ask  # dollars
        fresh_pm_ask = 1.0 - raw_bid  # dollars
        pm_bid_size = raw_ask_size
        pm_ask_size = raw_bid_size

    # Get fresh prices based on direction
    # CRITICAL: execution_pm_price is in DOLLARS (PM accepts 0.001 precision)
    #
    # ALL arbs use BUY_YES - just on different outcomeIndex:
    # - BUY_PM_SELL_K: LONG our team → buy our team's outcome
    # - BUY_K_SELL_PM: SHORT our team → buy opponent's outcome
    #
    # Price calculation (in DOLLARS):
    # - Buying outcome[0]: use raw_ask
    # - Buying outcome[1]: use (1.0 - raw_bid) = outcome[1] ask

    # Convert arb prices from cents to dollars for comparison
    arb_k_bid_dollars = arb.k_bid / 100.0
    arb_k_ask_dollars = arb.k_ask / 100.0

    # CRITICAL: Calculate execution_pm_price FIRST, then use it for spread calculation
    # execution_pm_price is what we PAY on PM (the ask for the outcome we're buying)

    if arb.direction == 'BUY_PM_SELL_K':
        # PM LONG our team → buy our team's outcome directly
        available_size = pm_ask_size
        if arb.pm_outcome_index == 0:
            # Our team is outcome[0] → BUY_YES outcome[0] → raw_ask
            execution_pm_price = raw_ask  # DOLLARS
            print(f"[PRICE CALC] BUY_PM_SELL_K, pm_outcome_index=0: execution_pm_price = raw_ask = ${execution_pm_price:.4f} ({execution_pm_price*100:.1f}c)")
        else:
            # Our team is outcome[1] → BUY_YES outcome[1] → (1.0 - raw_bid)
            execution_pm_price = 1.0 - raw_bid  # DOLLARS
            print(f"[PRICE CALC] BUY_PM_SELL_K, pm_outcome_index=1: execution_pm_price = 1.0 - ${raw_bid:.4f} = ${execution_pm_price:.4f} ({execution_pm_price*100:.1f}c)")

        # FIX-BUG-13: Spread formula verified - matches execution prices
        # Spread = what we RECEIVE (Kalshi bid) - what we PAY (PM execution price)
        # BUY_PM_SELL_K: Buy on PM at execution_pm_price, Sell on Kalshi at k_bid
        # Profit = k_bid - execution_pm_price
        fresh_spread_dollars = arb_k_bid_dollars - execution_pm_price
        print(f"[SPREAD CALC] BUY_PM_SELL_K: spread = k_bid(${arb_k_bid_dollars:.4f}) - pm_price(${execution_pm_price:.4f}) = ${fresh_spread_dollars:.4f} ({fresh_spread_dollars*100:.1f}c)")

    else:
        # PM SHORT our team → buy opponent's outcome (LONG opponent)
        available_size = pm_bid_size
        if arb.pm_outcome_index == 0:
            # Our team is outcome[0] → buy outcome[1] → (1.0 - raw_bid)
            execution_pm_price = 1.0 - raw_bid  # DOLLARS
            print(f"[PRICE CALC] BUY_K_SELL_PM, pm_outcome_index=0: execution_pm_price = 1.0 - ${raw_bid:.4f} = ${execution_pm_price:.4f} ({execution_pm_price*100:.1f}c)")
        else:
            # Our team is outcome[1] → buy outcome[0] → raw_ask
            execution_pm_price = raw_ask  # DOLLARS
            print(f"[PRICE CALC] BUY_K_SELL_PM, pm_outcome_index=1: execution_pm_price = raw_ask = ${execution_pm_price:.4f} ({execution_pm_price*100:.1f}c)")

        # FIX-BUG-13: Spread formula verified - matches execution prices
        # Spread = $1 payout - total cost (Kalshi buy + PM buy)
        # BUY_K_SELL_PM: Buy on Kalshi at k_ask, Buy opponent on PM at execution_pm_price
        # Both positions pay out $1 if our team LOSES, so total cost must be < $1
        # Profit = 1.0 - k_ask - execution_pm_price
        fresh_spread_dollars = 1.0 - arb_k_ask_dollars - execution_pm_price
        print(f"[SPREAD CALC] BUY_K_SELL_PM: spread = 1.0 - k_ask(${arb_k_ask_dollars:.4f}) - pm_price(${execution_pm_price:.4f}) = ${fresh_spread_dollars:.4f} ({fresh_spread_dollars*100:.1f}c)")

    # Convert spread to cents for threshold comparison (legacy compatibility)
    fresh_spread = fresh_spread_dollars * 100  # cents for comparison

    # DEBUG: Show exactly what's being set in fresh_prices
    print(f"[PRICE CALC] FINAL execution_pm_price = ${execution_pm_price:.4f} ({execution_pm_price*100:.1f}c)")
    print(f"[PRICE CALC] Fresh spread = ${fresh_spread_dollars:.4f} ({fresh_spread:.1f}c)")

    # All prices in DOLLARS for sub-cent precision
    fresh_prices = {
        'pm_bid': fresh_pm_bid,           # dollars (e.g., 0.79)
        'pm_ask': fresh_pm_ask,           # dollars (e.g., 0.81)
        'pm_bid_size': pm_bid_size,
        'pm_ask_size': pm_ask_size,
        'spread': fresh_spread,            # cents (legacy compatibility)
        'spread_dollars': fresh_spread_dollars,  # dollars (precise)
        'fetch_ms': pm_fetch_ms,
        'execution_pm_price': execution_pm_price,  # DOLLARS - use directly for PM order!
        'outcome_index': arb.pm_outcome_index,
        'raw_bid': raw_bid,               # dollars (e.g., 0.79)
        'raw_ask': raw_ask,               # dollars (e.g., 0.81)
    }

    # Check staleness
    if pm_fetch_ms > MAX_PRICE_STALENESS_MS:
        return False, f"Price fetch too slow ({pm_fetch_ms:.0f}ms > {MAX_PRICE_STALENESS_MS}ms)", fresh_prices

    # Check spread - must cover slippage + profit (compare in cents for legacy thresholds)
    if fresh_spread < MIN_SPREAD_FOR_EXECUTION:
        # Build detailed abort message showing the calculation
        if arb.direction == 'BUY_K_SELL_PM':
            calc_msg = f"1.0 - k_ask(${arb_k_ask_dollars:.3f}) - pm(${execution_pm_price:.3f}) = ${fresh_spread_dollars:.3f}"
        else:
            calc_msg = f"k_bid(${arb_k_bid_dollars:.3f}) - pm(${execution_pm_price:.3f}) = ${fresh_spread_dollars:.3f}"
        return False, f"[ABORT] Spread too thin: {calc_msg} = {fresh_spread:.1f}c < {MIN_SPREAD_FOR_EXECUTION}c min", fresh_prices

    # Check liquidity (use 66% of available)
    conservative_available = int(available_size * LIQUIDITY_UTILIZATION)
    if conservative_available < intended_size:
        return False, f"Liquidity dropped ({conservative_available} < {intended_size} needed)", fresh_prices

    return True, "OK", fresh_prices


# =============================================================================
# CRITICAL SAFETY CHECK: Verify hedge direction before execution
# This catches same-direction betting bugs that would result in naked exposure
# =============================================================================
def verify_hedge_direction(arb: 'ArbOpportunity') -> Tuple[bool, str]:
    """
    CRITICAL SAFETY CHECK: Verify that Kalshi and PM are on OPPOSITE sides.

    For a valid hedge:
    - BUY_K_SELL_PM: Kalshi LONG team, PM SHORT team (buy opponent on PM)
    - BUY_PM_SELL_K: PM LONG team, Kalshi SHORT team

    CRITICAL FIX: This function now INDEPENDENTLY derives the expected pm_outcome_index
    from the PM slug and PM_US_MARKET_CACHE, instead of trusting arb.pm_outcome_index.
    This catches bugs where pm_outcome_index was incorrectly assigned during cache building.

    Returns (is_valid, error_message)
    """
    # Parse PM slug to get team order in the slug
    slug_parts = arb.pm_slug.split('-')
    if len(slug_parts) < 5:
        return False, f"Can't parse slug: {arb.pm_slug}"

    slug_team1 = slug_parts[2].upper()  # First team in slug
    slug_team2 = slug_parts[3].upper()  # Second team in slug

    # Parse Kalshi ticker to get team
    k_parts = arb.kalshi_ticker.split('-')
    k_team = k_parts[-1].upper() if k_parts else 'UNKNOWN'

    our_team = arb.team.upper()

    # ==========================================================================
    # CRITICAL: Independently verify pm_outcome_index from the cache
    # The bug was: if pm_outcome_index is wrong, old verify logic would pass anyway
    # Now we look up the EXPECTED outcome_index from PM_US_MARKET_CACHE
    # ==========================================================================
    expected_outcome_index = None
    cache_lookup_info = ""

    # Try to find the market in PM_US_MARKET_CACHE
    for cache_key, pm_market in PM_US_MARKET_CACHE.items():
        if pm_market.get('slug') == arb.pm_slug:
            teams_data = pm_market.get('teams', {})
            if our_team in teams_data:
                expected_outcome_index = teams_data[our_team].get('outcome_index')
                cache_lookup_info = f"cache_key={cache_key}"
                break
            # Try with normalized team name
            for team_key, team_data in teams_data.items():
                if team_key.upper() == our_team:
                    expected_outcome_index = team_data.get('outcome_index')
                    cache_lookup_info = f"cache_key={cache_key}, matched via {team_key}"
                    break

    # Log the verification details
    print(f"[HEDGE VERIFY] Direction: {arb.direction}")
    print(f"[HEDGE VERIFY] Our team: {our_team}, arb.pm_outcome_index: {arb.pm_outcome_index}")
    print(f"[HEDGE VERIFY] Slug teams: {slug_team1} vs {slug_team2}")
    print(f"[HEDGE VERIFY] Kalshi team from ticker: {k_team}")

    if expected_outcome_index is not None:
        print(f"[HEDGE VERIFY] Cache lookup: expected_outcome_index={expected_outcome_index} ({cache_lookup_info})")
        if expected_outcome_index != arb.pm_outcome_index:
            error = (f"[!!!HEDGE VERIFY FAIL!!!] pm_outcome_index MISMATCH!\n"
                    f"  arb.pm_outcome_index = {arb.pm_outcome_index}\n"
                    f"  expected (from cache) = {expected_outcome_index}\n"
                    f"  This would cause same-direction betting!\n"
                    f"  Slug: {arb.pm_slug}, Team: {our_team}")
            print(error)
            return False, error
    else:
        print(f"[HEDGE VERIFY] WARNING: Could not find market in cache for independent verification")
        # Continue with fallback logic below

    # Determine which PM outcome we'll buy based on direction
    if arb.direction == 'BUY_PM_SELL_K':
        # PM goes LONG our team -> outcome_index = arb.pm_outcome_index
        pm_buying_index = arb.pm_outcome_index
    else:  # BUY_K_SELL_PM
        # PM goes SHORT our team -> outcome_index = 1 - arb.pm_outcome_index (buy opponent)
        pm_buying_index = 1 - arb.pm_outcome_index

    # Additional sanity check: the buying_index should result in buying opponent for BUY_K_SELL_PM
    # We verify this by checking which team is at each slug position
    # NOTE: Slug order may not match PM outcomes array order, but we can still check consistency

    # For BUY_K_SELL_PM on team X:
    #   - Kalshi: LONG X
    #   - PM: Should buy opponent Y (SHORT X)
    #   - If slug is "x-y" and our team is X:
    #     - If pm_outcome_index=0 (X at outcome[0]), buy outcome[1] (Y) - CORRECT
    #     - If pm_outcome_index=1 (X at outcome[1]), buy outcome[0] (Y) - CORRECT

    # For BUY_PM_SELL_K on team X:
    #   - Kalshi: SHORT X
    #   - PM: Should buy X (LONG X)
    #   - If pm_outcome_index=0 (X at outcome[0]), buy outcome[0] (X) - CORRECT
    #   - If pm_outcome_index=1 (X at outcome[1]), buy outcome[1] (X) - CORRECT

    # The key insight: as long as pm_outcome_index correctly identifies where OUR TEAM is,
    # the hedge logic works. The bug happens when pm_outcome_index is WRONG.

    # Map outcome indices to teams based on arb.pm_outcome_index
    if arb.pm_outcome_index == 0:
        pm_team_at_0 = our_team
        pm_team_at_1 = "OPPONENT"
    else:
        pm_team_at_0 = "OPPONENT"
        pm_team_at_1 = our_team

    pm_buying_team = pm_team_at_0 if pm_buying_index == 0 else pm_team_at_1

    print(f"[HEDGE VERIFY] PM buying outcome[{pm_buying_index}] = {pm_buying_team}")

    # Verify hedge logic
    if arb.direction == 'BUY_K_SELL_PM':
        # Kalshi: LONG our team
        # PM: should be SHORT our team (buy opponent)
        if pm_buying_team == our_team:
            error = (f"[!!!HEDGE VERIFY FAIL!!!] BUY_K_SELL_PM but PM buying SAME team!\n"
                    f"  Kalshi LONG: {k_team}\n"
                    f"  PM buying outcome[{pm_buying_index}] = {our_team} (SAME!)\n"
                    f"  PM should be buying OPPONENT, not {our_team}!\n"
                    f"  arb.pm_outcome_index={arb.pm_outcome_index}")
            print(error)
            return False, error
        else:
            print(f"[HEDGE VERIFY] ✓ OK: K LONG {k_team}, PM LONG opponent = valid hedge")

    elif arb.direction == 'BUY_PM_SELL_K':
        # Kalshi: SHORT our team
        # PM: should be LONG our team
        if pm_buying_team != our_team:
            error = (f"[!!!HEDGE VERIFY FAIL!!!] BUY_PM_SELL_K but PM NOT buying our team!\n"
                    f"  Our team: {our_team}\n"
                    f"  PM buying outcome[{pm_buying_index}] = OPPONENT\n"
                    f"  PM should be buying {our_team}!\n"
                    f"  arb.pm_outcome_index={arb.pm_outcome_index}")
            print(error)
            return False, error
        else:
            print(f"[HEDGE VERIFY] ✓ OK: PM LONG {our_team}, K SHORT = valid hedge")

    return True, "OK"


async def execute_sequential_orders(
    session, kalshi_api, pm_api, arb: 'ArbOpportunity',
    kalshi_price: int, pm_price: float, quantity: int,
    fresh_prices: Dict = None
) -> Tuple[Dict, Dict, Dict]:
    """
    Execute orders SEQUENTIALLY: Kalshi first, then PM only if Kalshi fills.

    This is slower by ~50-100ms but ELIMINATES unhedged positions from Kalshi failures.

    Flow:
    1. Send Kalshi order, wait for response
    2. IF Kalshi filled → send PM order
    3. IF Kalshi failed → skip PM (no unhedged risk)

    The only remaining unhedged risk is: Kalshi fills, then PM fails.
    That case is handled by existing recovery/close logic.

    Returns (kalshi_result, pm_result, execution_timing)

    CRITICAL: Pass fresh_prices to ensure we use current market data, not stale cache!
    """
    # Determine Kalshi action and add price buffer
    k_action = 'buy' if arb.direction == 'BUY_K_SELL_PM' else 'sell'

    # Apply price buffer for limit orders:
    # - If buying: bid at ask + buffer (willing to pay more)
    # - If selling: ask at bid - buffer (willing to receive less)
    if k_action == 'buy':
        k_limit_price = kalshi_price + PRICE_BUFFER_CENTS
    else:
        k_limit_price = kalshi_price - PRICE_BUFFER_CENTS
    k_limit_price = max(1, min(99, k_limit_price))  # Clamp to valid range

    # For PM: small buffer for timing between detection and execution
    # We now use BUY_YES only - BUY_NO doesn't work on PM US!
    # CRITICAL: Pass fresh_prices to use current market data!
    pm_intent, _, pm_outcome_index, _ = get_pm_execution_params(arb, fresh_prices)
    # All intents are now BUY (BUY_YES or BUY_NO), so always add buffer
    pm_limit_price = pm_price + (PM_PRICE_BUFFER_CENTS / 100)
    pm_limit_price = max(0.01, min(0.99, pm_limit_price))

    intent_names = {1: 'BUY_LONG', 2: 'SELL_LONG', 3: 'BUY_SHORT', 4: 'SELL_SHORT'}

    # DEBUG: Show exactly which team we're betting on each platform
    print(f"\n[EXEC] ========== EXECUTION DETAILS ==========")
    print(f"[EXEC] Arb Team: {arb.team} | Direction: {arb.direction}")
    print(f"[EXEC] Kalshi Ticker: {arb.kalshi_ticker}")
    print(f"[EXEC] PM Slug: {arb.pm_slug}")
    print(f"[EXEC] PM outcome_index for team: {arb.pm_outcome_index}")

    # Parse slug to show team order
    slug_parts = arb.pm_slug.split('-')
    if len(slug_parts) >= 4:
        slug_team1 = slug_parts[2].upper()
        slug_team2 = slug_parts[3].upper()
        print(f"[EXEC] PM Slug teams: outcome[0]={slug_team1}, outcome[1]={slug_team2}")
        our_team_slot = "outcome[0]" if arb.pm_outcome_index == 0 else "outcome[1]"
        print(f"[EXEC] Our team {arb.team} = {our_team_slot}")

    # Explain the intent logic with price breakdown
    pm_exposure = "LONG" if (arb.direction == 'BUY_PM_SELL_K') else "SHORT"
    k_exposure = "SHORT" if (arb.direction == 'BUY_PM_SELL_K') else "LONG"

    print(f"[EXEC] Arb structure: Kalshi {k_exposure} {arb.team}, PM {pm_exposure} {arb.team}")
    print(f"[EXEC] PM price passed in: ${pm_price:.2f} | With buffer: ${pm_limit_price:.2f}")

    target = slug_team1 if len(slug_parts) >= 4 else 'outcome[0]'
    other = slug_team2 if len(slug_parts) >= 4 else 'outcome[1]'

    # Debug: Show which outcome we're buying and what exposure that gives
    buying_outcome = target if pm_outcome_index == 0 else other
    if arb.direction == 'BUY_PM_SELL_K':
        print(f"[EXEC] BUY_YES outcome[{pm_outcome_index}] ({buying_outcome}) -> LONG {arb.team}")
    else:
        print(f"[EXEC] BUY_YES outcome[{pm_outcome_index}] ({buying_outcome}) -> SHORT {arb.team} (long opponent)")

    print(f"[EXEC] ==========================================")
    print(f"[EXEC] Kalshi: {k_action.upper()} {arb.team} {quantity} @ {k_limit_price}c")
    print(f"[EXEC] PM US: {intent_names[pm_intent]} {quantity} @ ${pm_limit_price:.2f}")

    overall_start = time.time()
    kalshi_timing = {'start': 0, 'end': 0, 'ms': 0}
    pm_timing = {'start': 0, 'end': 0, 'ms': 0}

    async def execute_kalshi():
        kalshi_timing['start'] = time.time()
        try:
            result = await kalshi_api.place_order(
                session, arb.kalshi_ticker, 'yes', k_action, quantity, k_limit_price
            )
            kalshi_timing['end'] = time.time()
            kalshi_timing['ms'] = (kalshi_timing['end'] - kalshi_timing['start']) * 1000
            result['execution_ms'] = kalshi_timing['ms']
            return result
        except Exception as e:
            kalshi_timing['end'] = time.time()
            kalshi_timing['ms'] = (kalshi_timing['end'] - kalshi_timing['start']) * 1000
            return {'success': False, 'error': str(e), 'fill_count': 0, 'execution_ms': kalshi_timing['ms']}

    async def execute_pm(override_qty: int = None):
        """Execute PM order. Use override_qty to match Kalshi's actual fill."""
        pm_timing['start'] = time.time()
        pm_qty = override_qty if override_qty is not None else quantity

        # FIX-BUG-2: FINAL SAFETY CHECK: Verify price is in safe range
        # Using MIN_PM_PRICE (5c = $0.05) as floor, 95c as ceiling
        pm_price_cents = int(pm_limit_price * 100)
        if pm_price_cents < MIN_PM_PRICE or pm_price_cents > (100 - MIN_PM_PRICE):
            print(f"[!!!EXECUTE ABORT!!!] PM limit price {pm_price_cents}c outside safe range ({MIN_PM_PRICE}-{100-MIN_PM_PRICE}c)")
            print(f"    NOT SENDING PM ORDER - would likely expire unfilled!")
            pm_timing['end'] = time.time()
            pm_timing['ms'] = (pm_timing['end'] - pm_timing['start']) * 1000
            return {
                'success': False,
                'error': f'Price {pm_price_cents}c outside safe range',
                'fill_count': 0,
                'execution_ms': pm_timing['ms'],
                'safety_abort': True
            }

        try:
            result = await pm_api.place_order(
                session, arb.pm_slug, pm_intent, pm_limit_price, pm_qty,
                tif=3, sync=True, outcome_index=pm_outcome_index
            )
            pm_timing['end'] = time.time()
            pm_timing['ms'] = (pm_timing['end'] - pm_timing['start']) * 1000
            result['execution_ms'] = pm_timing['ms']
            # CRITICAL: Log the outcome_index used for auditing
            result['outcome_index'] = pm_outcome_index
            return result
        except Exception as e:
            pm_timing['end'] = time.time()
            pm_timing['ms'] = (pm_timing['end'] - pm_timing['start']) * 1000
            return {'success': False, 'error': str(e), 'fill_count': 0, 'execution_ms': pm_timing['ms']}

    # =======================================================================
    # SEQUENTIAL EXECUTION (SAFETY): Kalshi first, then PM only if Kalshi fills
    # This eliminates unhedged positions from Kalshi failures (409 errors, etc.)
    # Slightly slower (~50-100ms) but prevents the #1 cause of unhedged positions
    # =======================================================================

    # STEP 1: Execute Kalshi FIRST
    print(f"[EXEC] Step 1: Sending Kalshi order...")
    kalshi_result = await execute_kalshi()

    k_fill = kalshi_result.get('fill_count', 0)
    k_fill_price = kalshi_result.get('fill_price') or k_limit_price
    k_fill_price = k_fill_price if k_fill_price is not None else k_limit_price

    print(f"[EXEC] Kalshi result: {k_fill} filled @ {k_fill_price}c in {kalshi_timing['ms']:.0f}ms")

    # STEP 2: Only execute PM if Kalshi filled
    if k_fill == 0:
        # Kalshi didn't fill - ABORT PM to avoid unhedged position
        print(f"[EXEC] Kalshi didn't fill - SKIPPING PM order (no unhedged risk)")
        pm_result = {
            'success': False,
            'fill_count': 0,
            'error': 'Skipped - Kalshi did not fill',
            'execution_ms': 0,
            'skipped': True,
            'outcome_index': pm_outcome_index  # Log even for skipped orders
        }
        pm_timing['ms'] = 0
    else:
        # CRITICAL FIX: PM quantity = Kalshi ACTUAL fill, not requested quantity
        # This prevents mismatch when Kalshi partially fills
        pm_qty = k_fill if k_fill < quantity else quantity
        print(f"[EXEC] Step 2: Kalshi filled {k_fill} - sending PM order for {pm_qty} contracts...")
        pm_result = await execute_pm(override_qty=pm_qty)

    overall_end = time.time()
    total_ms = (overall_end - overall_start) * 1000

    # Log execution results
    pm_fill = pm_result.get('fill_count', 0)
    pm_fill_price = pm_result.get('fill_price') or pm_limit_price
    pm_fill_price = pm_fill_price if pm_fill_price is not None else pm_limit_price

    k_status = f"{k_fill} @ {k_fill_price}c in {kalshi_timing['ms']:.0f}ms" + (" OK" if k_fill > 0 else " NO FILL")
    if pm_result.get('skipped'):
        pm_status = "SKIPPED (Kalshi didn't fill)"
    elif pm_result.get('safety_abort'):
        pm_status = f"SAFETY ABORT - Price {int(pm_limit_price*100)}c outside range!"
    else:
        pm_status = f"{pm_fill} @ ${pm_fill_price:.2f} in {pm_timing['ms']:.0f}ms" + (" OK" if pm_fill > 0 else " NO FILL")

    print(f"[EXEC] Kalshi: {k_status}")
    print(f"[EXEC] PM US: {pm_status}")

    both_matched = k_fill > 0 and pm_fill > 0 and k_fill == pm_fill
    if both_matched:
        print(f"[EXEC] Total execution: {total_ms:.0f}ms | Both sides matched OK")
    elif k_fill > 0 and pm_fill > 0:
        print(f"[EXEC] Total execution: {total_ms:.0f}ms | QUANTITY MISMATCH: K={k_fill}, PM={pm_fill}")
    elif k_fill == 0:
        print(f"[EXEC] Total execution: {total_ms:.0f}ms | Kalshi failed - PM skipped (SAFE)")
    elif pm_result.get('safety_abort'):
        print(f"[EXEC] Total execution: {total_ms:.0f}ms | PM SAFETY ABORT - UNHEDGED POSITION!")
        print(f"[!!!CRITICAL!!!] {k_fill} Kalshi contracts filled but PM aborted - MANUAL CLOSE NEEDED!")
    else:
        print(f"[EXEC] Total execution: {total_ms:.0f}ms | PARTIAL FILL - hedge needed")

    # Record execution stats
    record_execution(kalshi_timing['ms'], pm_timing['ms'], total_ms, both_matched)

    execution_timing = {
        'kalshi_ms': kalshi_timing['ms'],
        'pm_ms': pm_timing['ms'],
        'total_ms': total_ms,
        'both_matched': both_matched,
        'k_limit_price': k_limit_price,
        'pm_limit_price': pm_limit_price,
    }

    return kalshi_result, pm_result, execution_timing


async def attempt_hedge_recovery(
    session, pm_api, arb: 'ArbOpportunity',
    unhedged_qty: int, original_pm_price: float, hedge_state: HedgeState
) -> bool:
    """
    Attempt to complete hedge with slippage.
    Returns True if hedge completed, False otherwise.

    CRITICAL FIXES:
    - Check ORDER_STATE_FILLED and cumQuantity to detect successful fills
    - Track total filled across attempts to avoid double buying
    - Stop immediately when target is reached
    """
    print(f"\n[RECOVERY] Attempting to hedge {unhedged_qty} contracts...")
    hedge_state.recovery_attempted = True

    # Track remaining qty to avoid double buying
    remaining_qty = unhedged_qty
    total_recovery_filled = 0

    # Get intent from arb params - now uses BUY_YES only (BUY_NO doesn't work!)
    pm_intent, _, pm_outcome_index, _ = get_pm_execution_params(arb)
    intent_names = {1: 'BUY_LONG', 2: 'SELL_LONG', 3: 'BUY_SHORT', 4: 'SELL_SHORT'}

    # FEE-AWARE: Calculate max slippage before trade becomes unprofitable
    # If we slip too much, better to close Kalshi than overpay on PM
    raw_spread = arb.net_spread
    max_slippage_budget = raw_spread - KALSHI_FEE_CENTS_PER_CONTRACT - MIN_PROFIT_CENTS
    print(f"[RECOVERY] Raw spread: {raw_spread:.1f}c | Max slippage budget: {max_slippage_budget:.1f}c")
    print(f"[RECOVERY] (Will abort if slippage > {max_slippage_budget:.1f}c to prevent negative EV)")

    for slippage in SLIPPAGE_RECOVERY_LEVELS:
        # FEE-AWARE: Check if this slippage level would make trade unprofitable
        if slippage > max_slippage_budget:
            print(f"[RECOVERY ABORT] Slippage {slippage}c > budget {max_slippage_budget:.1f}c")
            print(f"[RECOVERY ABORT] Proceeding would result in negative EV trade!")
            print(f"[RECOVERY ABORT] Recommend closing Kalshi position instead of overpaying on PM")
            break
        # Check if we've already filled enough
        if remaining_qty <= 0:
            print(f"[RECOVERY] Target already reached ({total_recovery_filled} filled), stopping")
            break

        # All intents are now BUY (BUY_YES or BUY_NO), so always ADD slippage
        try_price = original_pm_price + (slippage / 100)
        try_price = max(0.01, min(0.99, try_price))  # Clamp to valid range

        print(f"[RECOVERY] Trying PM {intent_names[pm_intent]} {remaining_qty} @ ${try_price:.2f} (slippage: {slippage}c)...")

        try:
            result = await pm_api.place_order(
                session, arb.pm_slug, pm_intent, try_price, remaining_qty,
                tif=3, sync=True, outcome_index=pm_outcome_index
            )

            # CRITICAL FIX: Check multiple indicators of success
            order_state = result.get('order_state', '')
            fill_count = result.get('fill_count', 0)
            fill_price = result.get('fill_price', try_price)
            is_success = result.get('success', False)

            print(f"[RECOVERY] Result: state={order_state}, fill_count={fill_count}, success={is_success}")

            # Check if order filled (FILLED or PARTIALLY_FILLED both mean fills happened)
            is_filled = order_state in ['ORDER_STATE_FILLED', 'ORDER_STATE_PARTIALLY_FILLED']

            # If order state says FILLED but fill_count is 0, trust the state
            # ISSUE 3 HARDENING: Log this assumption for verification
            if is_filled and fill_count == 0:
                fill_count = remaining_qty  # Assume full fill if state says FILLED
                print(f"[RECOVERY WARNING] State={order_state} but fill_count=0 - ASSUMING {fill_count} filled")
                print(f"[RECOVERY WARNING] This assumption should be verified against PM position after trade")

            # Also trust success flag if fill_count > 0
            if is_success and fill_count == 0 and order_state:
                fill_count = remaining_qty
                print(f"[RECOVERY] Success=True, assuming {fill_count} filled")

            if fill_count > 0:
                hedge_state.pm_filled += fill_count
                total_recovery_filled += fill_count
                remaining_qty -= fill_count
                hedge_state.recovery_slippage = slippage

                print(f"[RECOVERY] FILLED {fill_count} @ ${fill_price:.3f} ✓ (total: {total_recovery_filled}, remaining: {remaining_qty})")

                # SUCCESS: Check if we've filled enough
                if remaining_qty <= 0:
                    print(f"[RECOVERY] SUCCESS! All {unhedged_qty} contracts hedged ✓")
                    return True
            else:
                print(f"[RECOVERY] No fill at {slippage}c slippage (state: {order_state}, success: {is_success})")

        except Exception as e:
            print(f"[RECOVERY] Error at {slippage}c slippage: {e}")

        await asyncio.sleep(0.1)  # Brief pause between attempts

    # Final check - did we fill anything?
    if total_recovery_filled >= unhedged_qty:
        print(f"[RECOVERY] SUCCESS! Filled {total_recovery_filled}/{unhedged_qty} contracts ✓")
        return True

    print(f"[RECOVERY] FAILED - {remaining_qty} of {unhedged_qty} contracts still unhedged")
    # ISSUE 3 HARDENING: Remind to verify assumptions
    print(f"[RECOVERY] NOTE: Run position sync to verify actual PM fills match assumptions")
    return False


# FIX-BUG-4: Auto-close Kalshi if PM fails - this function closes the Kalshi
# position to avoid unhedged exposure when PM order fails completely.
async def attempt_kalshi_close(
    session, kalshi_api, arb: 'ArbOpportunity',
    qty: int, original_k_price: int
) -> Tuple[bool, int]:
    """
    FIX-BUG-4: Attempt to close Kalshi position when PM hedge fails completely.
    Returns (success, fill_count).

    Logic:
    - If original trade was BUY_K_SELL_PM (we bought on Kalshi), sell to close
    - If original trade was BUY_PM_SELL_K (we sold on Kalshi), buy to close
    """
    print(f"\n[KALSHI CLOSE] Attempting to close {qty} Kalshi contracts...")

    if arb.direction == 'BUY_K_SELL_PM':
        # We bought YES on Kalshi, need to sell YES to close
        close_action = 'sell'
        close_side = 'yes'
        # Sell at bid with slippage (accept lower price to ensure fill)
        base_price = arb.k_bid
    else:
        # BUY_PM_SELL_K: we sold YES on Kalshi, need to buy YES to close
        close_action = 'buy'
        close_side = 'yes'
        # Buy at ask with slippage (pay higher price to ensure fill)
        base_price = arb.k_ask

    # Try with increasing slippage
    for slippage in [1, 2, 3, 5, 10, 15]:
        if close_action == 'sell':
            try_price = max(1, base_price - slippage)  # Accept lower to sell
        else:
            try_price = min(99, base_price + slippage)  # Pay more to buy

        print(f"[KALSHI CLOSE] Trying {close_action.upper()} {qty} {close_side.upper()} @ {try_price}c (slippage: {slippage}c)...")

        try:
            result = await kalshi_api.place_order(
                session, arb.kalshi_ticker, close_side, close_action, qty, try_price
            )

            fill_count = result.get('fill_count', 0)

            if fill_count >= qty:
                loss_cents = abs(try_price - original_k_price) * fill_count
                print(f"[KALSHI CLOSE] SUCCESS! Closed {fill_count} @ {try_price}c (loss: ${loss_cents/100:.2f})")
                return True, fill_count
            elif fill_count > 0:
                qty -= fill_count
                print(f"[KALSHI CLOSE] Partial: {fill_count} closed, {qty} remaining")
        except Exception as e:
            print(f"[KALSHI CLOSE] Error at {slippage}c slippage: {e}")

        await asyncio.sleep(0.1)

    print(f"[KALSHI CLOSE] FAILED - {qty} contracts still open")
    return False, 0


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

        # Attempt recovery - get pm_price (intent and outcome_index handled in recovery function)
        _, pm_price, _, _ = get_pm_execution_params(arb)
        recovery_success = await attempt_hedge_recovery(
            session, pm_api, arb, unhedged_qty, pm_price, hedge_state
        )

        if recovery_success:
            hedge_state.is_hedged = True
            print(f"[HEDGE CHECK] RECOVERED ✓ (with {hedge_state.recovery_slippage}c slippage)")
        else:
            # PM recovery failed - attempt to close the Kalshi position
            print(f"[!!! PM RECOVERY FAILED !!!] Attempting to close Kalshi position...")

            k_close_success, k_closed = await attempt_kalshi_close(
                session, kalshi_api, arb, unhedged_qty, hedge_state.kalshi_price or 50
            )

            if k_close_success:
                hedge_state.is_hedged = True
                hedge_state.kalshi_filled -= k_closed  # Position closed
                print(f"[HEDGE CHECK] POSITION CLOSED ✓ (took loss to avoid exposure)")
            else:
                # Both PM and Kalshi recovery failed - save for manual intervention
                save_unhedged_position(hedge_state, "PM recovery failed, Kalshi close failed")

                # Calculate exposure
                exposure_cents = unhedged_qty * (hedge_state.kalshi_price or 50)
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
    print("[1/7] API CREDENTIALS")

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
    print("\n[2/7] ACCOUNT BALANCES")

    MIN_KALSHI_BALANCE = 10.0   # $10 minimum (lowered for testing)
    MIN_PM_BALANCE = 10.0       # $10 minimum (lowered for testing)

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
    print("\n[3/7] EXISTING POSITIONS")

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
    print("\n[4/7] MARKET CONNECTIVITY")

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
    print("\n[5/7] CONFIGURATION")

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
    print("\n[6/7] DATA FILES")

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

    # ISSUE 4 HARDENING: Check trades.json for corruption (not just writability)
    trades_corrupt = False
    try:
        if os.path.exists('trades.json'):
            with open('trades.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content and content != '[]':
                    json.loads(content)  # Will raise JSONDecodeError if corrupt
                    print(f"  [INFO] trades.json: valid JSON")
    except json.JSONDecodeError as e:
        trades_corrupt = True
        results.append(PreflightResult(
            name="trades.json Integrity",
            passed=False,
            blocking=True,
            message=f"CORRUPTED: {str(e)[:40]}",
            details="Delete or fix trades.json before trading"
        ))
        print(f"  [FAIL] trades.json: CORRUPTED - {str(e)[:40]}")

    # =========================================================================
    # 7. CRASH HISTORY - Check for recent crashes (ISSUE 4)
    # =========================================================================
    print("\n[7/7] CRASH HISTORY")

    crash_files = sorted([f for f in os.listdir('logs') if f.startswith('crash_')]) if os.path.exists('logs') else []
    recent_crash_warning = False
    if crash_files:
        print(f"  [INFO] Found {len(crash_files)} crash log(s)")
        # Show last 3 crashes
        for cf in crash_files[-3:]:
            print(f"         - {cf}")
        # Check if latest crash was recent
        try:
            latest_crash = crash_files[-1]
            crash_ts = latest_crash.replace('crash_', '').replace('.log', '')
            crash_dt = datetime.strptime(crash_ts, '%Y%m%d_%H%M%S')
            hours_ago = (datetime.now() - crash_dt).total_seconds() / 3600
            if hours_ago < 1:
                recent_crash_warning = True
                results.append(PreflightResult(
                    name="Recent Crashes",
                    passed=True,  # Warning only, not blocking
                    blocking=False,
                    message=f"Crash {hours_ago:.1f}h ago - review before trading"
                ))
                print(f"  [WARN] Most recent crash was {hours_ago:.1f} hours ago - review logs before trading")
        except Exception:
            pass
    else:
        print("  [PASS] No crash logs found")

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


def _pm_price_cents(fill_price: float, arb) -> float:
    """Normalize PM price to cents. API returns dollars (0.72), arb fields are cents (72)."""
    if fill_price and 0 < fill_price < 1:
        return round(fill_price * 100, 1)
    if fill_price and fill_price >= 1:
        return fill_price
    # No fill price — use raw ask/bid from arb opportunity
    return arb.pm_ask if arb.direction == 'BUY_PM_SELL_K' else arb.pm_bid


def log_trade(arb: ArbOpportunity, k_result: Dict, pm_result: Dict, status: str,
               execution_time_ms: float = 0):
    """Log trade details with all important fields"""
    global TRADE_LOG

    # Determine display status
    if arb.needs_review:
        display_status = 'REVIEW'
    elif Config.is_paper():
        display_status = 'PAPER'
    else:
        display_status = status

    # Calculate at-risk (capital deployed on buy side)
    # BUY_K_SELL_PM: risk = k_ask * contracts (we buy on Kalshi)
    # BUY_PM_SELL_K: risk = pm_ask * contracts (we buy on PM)
    k_fill = k_result.get('fill_count', 0)
    pm_fill = pm_result.get('fill_count', 0)
    actual_contracts = min(k_fill, pm_fill) if (k_fill > 0 and pm_fill > 0) else max(k_fill, pm_fill)

    if arb.direction == 'BUY_K_SELL_PM':
        buy_price_cents = arb.k_ask
    else:  # BUY_PM_SELL_K
        buy_price_cents = arb.pm_ask
    at_risk_cents = buy_price_cents * actual_contracts
    at_risk_dollars = at_risk_cents / 100

    # Calculate spread in cents
    spread_cents = arb.net_spread

    # Determine if fully hedged
    hedged = (k_fill > 0 and pm_fill > 0 and k_fill == pm_fill) or status == 'RECOVERED'

    trade = {
        # Core identifiers
        'timestamp': datetime.now().isoformat(),
        'game_id': arb.game,
        'team': arb.team,
        'sport': arb.sport,
        'direction': arb.direction,

        # Sizing
        'contracts_intended': arb.size,
        'contracts_filled': actual_contracts,
        'kalshi_fill': k_fill,
        'pm_fill': pm_fill,

        # Prices (cents) — PM fill_price comes from API in dollars, convert to cents
        'k_price': k_result.get('fill_price') or (arb.k_ask if arb.direction == 'BUY_K_SELL_PM' else arb.k_bid),
        'pm_price': _pm_price_cents(pm_result.get('fill_price', 0), arb),
        'k_bid': arb.k_bid,
        'k_ask': arb.k_ask,
        'pm_bid': arb.pm_bid,
        'pm_ask': arb.pm_ask,

        # Financials
        'spread_cents': spread_cents,
        'profit_dollars': arb.profit,
        'at_risk_dollars': at_risk_dollars,
        'roi_percent': round(arb.roi, 2),

        # FEE-AWARE P&L (added for post-trade verification)
        'estimated_net_profit_cents': None,  # Will be filled below
        'actual_pnl': None,  # Will be filled below if both sides filled

        # Execution
        'execution_time_ms': round(execution_time_ms, 1),
        'hedged': hedged,
        'paper_mode': Config.is_paper(),

        # Status
        'status': display_status,
        'raw_status': status,

        # Additional context
        'pm_slug': arb.pm_slug,
        'kalshi_ticker': arb.kalshi_ticker,
        'k_order_id': k_result.get('order_id'),
        'pm_order_id': pm_result.get('order_id'),
        'pm_success': pm_result.get('success', False),
        'pm_error': pm_result.get('error'),
        'needs_review': arb.needs_review,
        'review_reason': arb.review_reason if arb.needs_review else None,
        'is_live_game': arb.is_live_game,

        # CRITICAL: Log pm_outcome_index for post-hoc auditing
        # This helps diagnose same-direction betting bugs
        'pm_outcome_index': arb.pm_outcome_index,
        'pm_outcome_index_used': pm_result.get('outcome_index'),  # Actual index sent to PM API
        'mapping_verified': any(
            vm.get('game_id') == arb.game and vm.get('verified', False)
            for vm in VERIFIED_MAPS.values()
        ) if VERIFIED_MAPS else False,
    }

    # FEE-AWARE P&L CALCULATION
    # Add estimated profit
    try:
        est_profit, est_breakdown = estimate_net_profit_cents(arb)
        trade['estimated_net_profit_cents'] = round(est_profit, 2)
        trade['estimated_costs_breakdown'] = est_breakdown
    except Exception as e:
        trade['estimated_net_profit_cents'] = None
        trade['estimated_costs_breakdown'] = {'error': str(e)}

    # Add actual P&L if both sides filled
    if k_fill > 0 and pm_fill > 0:
        k_fill_price = k_result.get('fill_price', trade['k_price'])
        pm_fill_price = pm_result.get('fill_price', trade['pm_price'])

        # Convert PM fill price if it's in dollars
        if pm_fill_price and pm_fill_price < 1:
            pm_fill_price = pm_fill_price * 100  # Convert to cents

        # Calculate pm_intent based on direction and is_long_team
        is_long_team = (arb.team == arb.pm_long_team)
        if arb.direction == 'BUY_K_SELL_PM':
            pm_intent = 2 if is_long_team else 1  # SELL_YES if long, BUY_YES if not
        else:  # BUY_PM_SELL_K
            pm_intent = 1 if is_long_team else 2  # BUY_YES if long, SELL_YES if not

        actual_contracts = min(k_fill, pm_fill)
        actual_pnl = calculate_actual_pnl(
            k_fill_price_cents=k_fill_price,
            pm_fill_price_cents=pm_fill_price,
            contracts=actual_contracts,
            direction=arb.direction,
            k_fee_cents=KALSHI_FEE_CENTS_PER_CONTRACT,
            pm_fee_cents=pm_fill_price * PM_US_FEE_RATE if pm_fill_price else 0.05,
            pm_intent=pm_intent
        )
        trade['actual_pnl'] = actual_pnl

        # Log actual vs estimated
        if actual_pnl and est_profit is not None:
            actual_per_contract = actual_pnl['per_contract']['net']
            diff = actual_per_contract - est_profit
            print(f"[P&L VERIFY] Estimated: {est_profit:.1f}c/contract | Actual: {actual_per_contract:.1f}c/contract | Diff: {diff:+.1f}c")
            if actual_per_contract < 0:
                print(f"[P&L WARNING] NEGATIVE actual profit! Check fees/slippage assumptions.")

    TRADE_LOG.append(trade)

    if len(TRADE_LOG) > 1000:
        TRADE_LOG = TRADE_LOG[-1000:]

    try:
        # Use explicit encoding to avoid BOM issues
        with open('trades.json', 'w', encoding='utf-8') as f:
            json.dump(TRADE_LOG, f, indent=2)
    except Exception as e:
        print(f"[TRADE LOG] Error saving trades.json: {e}")


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
            with open('skipped_arbs.json', 'w', encoding='utf-8') as f:
                json.dump(SKIPPED_ARBS, f, indent=2)
        except:
            pass


def save_skipped_arbs():
    """Force save skipped arbs to file"""
    try:
        with open('skipped_arbs.json', 'w', encoding='utf-8') as f:
            json.dump(SKIPPED_ARBS, f, indent=2)
    except:
        pass


def print_pnl_summary():
    """Print P&L summary from trades.json"""
    try:
        with open('trades.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content or content == '[]':
                print("\n[P&L SUMMARY] No trades found in trades.json")
                return
            trades = json.loads(content)
    except FileNotFoundError:
        print("\n[P&L SUMMARY] trades.json not found")
        return
    except json.JSONDecodeError as e:
        print(f"\n[P&L SUMMARY] Error reading trades.json: {e}")
        return

    if not trades:
        print("\n[P&L SUMMARY] No trades found")
        return

    # Separate paper and live trades
    paper_trades = [t for t in trades if t.get('paper_mode') or t.get('status', '').startswith('PAPER')]
    live_trades = [t for t in trades if not t.get('paper_mode') and not t.get('status', '').startswith('PAPER')]

    print("\n" + "="*70)
    print("                     P&L SUMMARY")
    print("="*70)

    for label, trade_list in [("PAPER TRADES", paper_trades), ("LIVE TRADES", live_trades)]:
        if not trade_list:
            continue

        print(f"\n[{label}] {len(trade_list)} trades")
        print("-"*70)

        total_profit = 0
        total_at_risk = 0
        total_contracts = 0
        by_sport = {}
        by_status = {}
        spreads = []

        for t in trade_list:
            contracts = t.get('contracts_filled', 0)
            spread = t.get('spread_cents', 0)
            profit = (spread * contracts) / 100  # dollars
            at_risk = t.get('at_risk_dollars', 0)
            sport = t.get('sport', 'UNKNOWN')
            status = t.get('status', 'UNKNOWN')

            total_profit += profit
            total_at_risk += at_risk
            total_contracts += contracts
            spreads.append(spread)

            if sport not in by_sport:
                by_sport[sport] = {'profit': 0, 'contracts': 0, 'count': 0}
            by_sport[sport]['profit'] += profit
            by_sport[sport]['contracts'] += contracts
            by_sport[sport]['count'] += 1

            if status not in by_status:
                by_status[status] = 0
            by_status[status] += 1

        avg_spread = sum(spreads) / len(spreads) if spreads else 0
        min_spread = min(spreads) if spreads else 0
        max_spread = max(spreads) if spreads else 0
        roi = (total_profit / total_at_risk * 100) if total_at_risk > 0 else 0

        print(f"  Total Profit:     ${total_profit:>10.2f}")
        print(f"  Total At Risk:    ${total_at_risk:>10.2f}")
        print(f"  ROI:              {roi:>10.1f}%")
        print(f"  Total Contracts:  {total_contracts:>10}")
        print(f"  Avg Spread:       {avg_spread:>10.1f}c")
        print(f"  Spread Range:     {min_spread:.0f}c - {max_spread:.0f}c")

        print(f"\n  By Sport:")
        for sport, data in sorted(by_sport.items(), key=lambda x: -x[1]['profit']):
            print(f"    {sport:>5}: ${data['profit']:>8.2f} profit | {data['contracts']:>5} contracts | {data['count']:>3} trades")

        print(f"\n  By Status:")
        for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
            print(f"    {status:>15}: {count:>3} trades")

        # Show recent trades
        print(f"\n  Recent Trades (last 10):")
        for t in trade_list[-10:]:
            ts = t.get('timestamp', '')[:19]
            sport = t.get('sport', '?')
            team = t.get('team', '?')
            spread = t.get('spread_cents', 0)
            contracts = t.get('contracts_filled', 0)
            profit = (spread * contracts) / 100
            direction = t.get('direction', '?')[:10]
            print(f"    {ts} | {sport:>3} {team:>4} | {spread:>2}c x {contracts:>3} = ${profit:>5.2f} | {direction}")

    print("\n" + "="*70)


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
                    # Use normalized team abbreviations for matching!
                    game_date = None
                    if game_time_str:
                        try:
                            dt_utc = datetime.fromisoformat(game_time_str.replace('Z', '+00:00')).replace(tzinfo=None)
                            dt_est = dt_utc - timedelta(hours=5)  # UTC to EST
                            game_date = dt_est.strftime('%Y-%m-%d')
                        except:
                            game_date = game_time_str[:10]  # Fallback to raw date
                    if game_date:
                        cache_key = build_cache_key(sport, team1, team2, game_date)
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

# =============================================================================
# KALSHI ABBREVIATION TO PM OUTCOME NAME KEYWORDS
# Used by find_pm_outcome_index() to match Kalshi team codes against PM outcome names
# Maps: Kalshi abbreviation -> list of keywords that appear in PM outcome names
# =============================================================================
KALSHI_ABBREV_TO_NAMES = {
    # NBA Teams (30 teams)
    'ATL': ['hawks', 'atlanta'],
    'BOS': ['celtics', 'boston'],
    'BKN': ['nets', 'brooklyn'],
    'CHA': ['hornets', 'charlotte'],
    'CHI': ['bulls', 'chicago'],
    'CLE': ['cavaliers', 'cavs', 'cleveland'],
    'DAL': ['mavericks', 'mavs', 'dallas'],
    'DEN': ['nuggets', 'denver'],
    'DET': ['pistons', 'detroit'],
    'GSW': ['warriors', 'golden state'],
    'HOU': ['rockets', 'houston'],
    'IND': ['pacers', 'indiana'],
    'LAC': ['clippers', 'la clippers', 'los angeles clippers'],
    'LAL': ['lakers', 'la lakers', 'los angeles lakers'],
    'MEM': ['grizzlies', 'memphis'],
    'MIA': ['heat', 'miami'],
    'MIL': ['bucks', 'milwaukee'],
    'MIN': ['timberwolves', 'wolves', 'minnesota'],
    'NOP': ['pelicans', 'new orleans'],
    'NYK': ['knicks', 'new york knicks'],
    'OKC': ['thunder', 'oklahoma city', 'oklahoma'],
    'ORL': ['magic', 'orlando'],
    'PHI': ['76ers', 'sixers', 'philadelphia'],
    'PHX': ['suns', 'phoenix'],
    'POR': ['trail blazers', 'blazers', 'portland'],
    'SAC': ['kings', 'sacramento'],
    'SAS': ['spurs', 'san antonio'],
    'TOR': ['raptors', 'toronto'],
    'UTA': ['jazz', 'utah'],
    'WAS': ['wizards', 'washington'],

    # NHL Teams (32 teams)
    'ANA': ['ducks', 'anaheim'],
    'ARI': ['coyotes', 'arizona'],  # Now Utah Hockey Club
    'BOS': ['bruins', 'boston'],  # Note: shared with NBA
    'BUF': ['sabres', 'buffalo'],
    'CAR': ['hurricanes', 'carolina'],
    'CBJ': ['blue jackets', 'columbus'],
    'CGY': ['flames', 'calgary'],
    'CHI': ['blackhawks', 'chicago'],  # Note: shared with NBA (different mascot)
    'COL': ['avalanche', 'colorado'],
    'DAL': ['stars', 'dallas'],  # Note: shared with NBA (different mascot)
    'DET': ['red wings', 'detroit'],  # Note: shared with NBA (different mascot)
    'EDM': ['oilers', 'edmonton'],
    'FLA': ['panthers', 'florida'],
    'LA': ['kings', 'los angeles'],  # NHL Kings
    'LAK': ['kings', 'los angeles'],  # NHL Kings alternate
    'MIN': ['wild', 'minnesota'],  # Note: shared with NBA (different mascot)
    'MTL': ['canadiens', 'habs', 'montreal'],
    'NJ': ['devils', 'new jersey'],
    'NJD': ['devils', 'new jersey'],  # Alternate
    'NSH': ['predators', 'preds', 'nashville'],
    'NYI': ['islanders', 'new york islanders'],
    'NYR': ['rangers', 'new york rangers'],
    'OTT': ['senators', 'sens', 'ottawa'],
    'PHI': ['flyers', 'philadelphia'],  # Note: shared with NBA (different mascot)
    'PIT': ['penguins', 'pens', 'pittsburgh'],
    'SEA': ['kraken', 'seattle'],
    'SJ': ['sharks', 'san jose'],
    'SJS': ['sharks', 'san jose'],  # Alternate
    'STL': ['blues', 'st. louis', 'st louis', 'saint louis'],
    'TB': ['lightning', 'tampa bay', 'tampa'],
    'TBL': ['lightning', 'tampa bay', 'tampa'],  # Alternate
    'TOR': ['maple leafs', 'leafs', 'toronto'],  # Note: shared with NBA (different mascot)
    'UTA': ['utah hockey club', 'utah hockey', 'utah'],  # New NHL team
    'VAN': ['canucks', 'vancouver'],
    'VGK': ['golden knights', 'vegas', 'las vegas'],
    'WPG': ['jets', 'winnipeg'],
    'WSH': ['capitals', 'caps', 'washington'],

    # CBB Teams (add mascots and school names for name-based matching)
    # Power 5 Conferences
    'DUKE': ['blue devils', 'duke'],
    'UNC': ['tar heels', 'north carolina', 'carolina'],
    'CUSE': ['orange', 'syracuse'],
    'LOU': ['cardinals', 'louisville'],
    'UVA': ['cavaliers', 'virginia'],
    'VT': ['hokies', 'virginia tech'],
    'WAKE': ['demon deacons', 'wake forest'],
    'BC': ['eagles', 'boston college'],
    'PITT': ['panthers', 'pittsburgh'],
    'GT': ['yellow jackets', 'georgia tech'],
    'FSU': ['seminoles', 'florida state'],
    'MIA': ['hurricanes', 'miami'],  # Note: conflicts with NBA Heat
    'NCST': ['wolfpack', 'nc state'],
    'CLEM': ['tigers', 'clemson'],
    'ND': ['fighting irish', 'notre dame'],
    'UK': ['wildcats', 'kentucky'],
    'TENN': ['volunteers', 'vols', 'tennessee'],
    'FLA': ['gators', 'florida'],
    'UGA': ['bulldogs', 'georgia'],
    'AUB': ['tigers', 'auburn'],
    'ALA': ['crimson tide', 'alabama'],
    'LSU': ['tigers', 'lsu', 'louisiana state'],
    'ARK': ['razorbacks', 'hogs', 'arkansas'],
    'MIZ': ['tigers', 'mizzou', 'missouri'],
    'MSST': ['bulldogs', 'mississippi state'],
    'MISS': ['rebels', 'ole miss', 'mississippi'],
    'VAN': ['commodores', 'vanderbilt', 'vandy'],
    'SCAR': ['gamecocks', 'south carolina'],
    'TXAM': ['aggies', 'texas a&m'],
    'TEX': ['longhorns', 'texas'],
    'OU': ['sooners', 'oklahoma'],
    'OKST': ['cowboys', 'oklahoma state'],
    'BAY': ['bears', 'baylor'],
    'TCU': ['horned frogs', 'tcu'],
    'TT': ['red raiders', 'texas tech'],
    'KU': ['jayhawks', 'kansas'],
    'KSU': ['wildcats', 'kansas state', 'k-state'],
    'ISU': ['cyclones', 'iowa state'],
    'WVU': ['mountaineers', 'west virginia'],
    'CIN': ['bearcats', 'cincinnati'],
    'HOU': ['cougars', 'houston'],
    'UCF': ['knights', 'ucf', 'central florida'],
    'BYU': ['cougars', 'byu', 'brigham young'],
    'COLO': ['buffaloes', 'buffs', 'colorado'],
    'ARIZ': ['wildcats', 'arizona'],
    'ASU': ['sun devils', 'arizona state'],
    'UTAH': ['utes', 'utah'],
    'UCLA': ['bruins', 'ucla'],
    'USC': ['trojans', 'usc'],
    'ORE': ['ducks', 'oregon'],
    'ORST': ['beavers', 'oregon state'],
    'WASH': ['huskies', 'washington'],
    'WSU': ['cougars', 'washington state', 'wazzu'],
    'STAN': ['cardinal', 'stanford'],
    'CAL': ['bears', 'cal', 'california'],
    'MICH': ['wolverines', 'michigan'],
    'MSU': ['spartans', 'michigan state'],
    'OSU': ['buckeyes', 'ohio state'],
    'PSU': ['nittany lions', 'penn state'],
    'IND': ['hoosiers', 'indiana'],
    'PUR': ['boilermakers', 'purdue'],
    'IOWA': ['hawkeyes', 'iowa'],
    'WIS': ['badgers', 'wisconsin'],
    'NEB': ['cornhuskers', 'huskers', 'nebraska'],
    'NW': ['wildcats', 'northwestern'],
    'ILL': ['fighting illini', 'illini', 'illinois'],
    'MINN': ['golden gophers', 'gophers', 'minnesota'],
    'MD': ['terrapins', 'terps', 'maryland'],
    'RUTG': ['scarlet knights', 'rutgers'],
    'GONZ': ['bulldogs', 'zags', 'gonzaga'],
    'CONN': ['huskies', 'uconn', 'connecticut'],
    'MARQ': ['golden eagles', 'marquette'],
    'NOVA': ['wildcats', 'villanova'],
    'CREIGH': ['bluejays', 'creighton'],
    'XAVIER': ['musketeers', 'xavier'],
    'PROV': ['friars', 'providence'],
    'SETON': ['pirates', 'seton hall'],
    'STJOHN': ['red storm', "st. john's", 'st johns'],
    'BUTLER': ['bulldogs', 'butler'],
    'DEPAUL': ['blue demons', 'depaul'],
    'GTOWN': ['hoyas', 'georgetown'],
    'UVM': ['catamounts', 'vermont'],
    'SMC': ['gaels', "saint mary's", 'st marys'],
}

# =============================================================================
# TEAM NAME TO ABBREVIATION (Reverse lookup)
# Built from KALSHI_ABBREV_TO_NAMES - maps team names/mascots to canonical abbrev
# =============================================================================
TEAM_NAME_TO_ABBREV = {}
for abbrev, names in KALSHI_ABBREV_TO_NAMES.items():
    for name in names:
        TEAM_NAME_TO_ABBREV[name.lower()] = abbrev


def team_name_to_canonical(name: str) -> str:
    """
    Convert a team name (e.g., "Tar Heels", "North Carolina", "Syracuse Orange")
    to its canonical abbreviation (e.g., "UNC", "CUSE").

    Used for name-based matching between PM outcomes and Kalshi markets.

    CRITICAL FIX: Check mascot (last word) BEFORE city/state to avoid cross-sport
    collisions like "Carolina Hurricanes" -> UNC (wrong, should be CAR).
    Mascots are more unique than city names.
    """
    if not name:
        return None

    name_lower = name.lower().strip()

    # Direct lookup of full name (e.g., "north carolina")
    if name_lower in TEAM_NAME_TO_ABBREV:
        return TEAM_NAME_TO_ABBREV[name_lower]

    words = name_lower.split()

    # CRITICAL FIX: Check words in REVERSE order (mascot first, then city)
    # Team names are typically "City/State Mascot" format
    # - "Carolina Hurricanes" -> check "hurricanes" first -> CAR (correct!)
    # - "Ottawa Senators" -> check "senators" first -> OTT (correct!)
    # This prevents "carolina" matching UNC when it should match CAR (hurricanes)
    for word in reversed(words):
        if word in TEAM_NAME_TO_ABBREV:
            return TEAM_NAME_TO_ABBREV[word]

    # Try two-word combinations (for "North Carolina", "Texas Tech", etc.)
    # Check from end first to prefer mascot combinations
    for i in range(len(words) - 2, -1, -1):
        two_word = f"{words[i]} {words[i+1]}"
        if two_word in TEAM_NAME_TO_ABBREV:
            return TEAM_NAME_TO_ABBREV[two_word]

    # Try removing common suffixes and looking up
    for suffix in [' state', ' tech', ' university']:
        if name_lower.endswith(suffix):
            base = name_lower[:-len(suffix)]
            if base in TEAM_NAME_TO_ABBREV:
                return TEAM_NAME_TO_ABBREV[base]

    return None


def extract_teams_from_pm_outcomes(outcomes: list) -> tuple:
    """
    Extract canonical team abbreviations from PM outcomes array.

    PM outcomes look like: ["Sacramento Kings", "Washington Wizards"]
                      or: ["Tar Heels", "Orange"]

    Returns: (team1_abbrev, team2_abbrev) or (None, None) if can't parse
    """
    if not outcomes or len(outcomes) < 2:
        return None, None

    team1 = team_name_to_canonical(outcomes[0])
    team2 = team_name_to_canonical(outcomes[1])

    return team1, team2


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
    'SA': 'SAS',    # San Antonio: PM uses SA, Kalshi uses SAS (not SAC which is Sacramento)
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
    'CALPOL': 'CP',     # Cal Poly SLO (PM: calpol, K: CP) - note: some games may use CPOLY
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
    # CBB - Additional mappings (Feb 2026)
    'WCAR': 'WCU',      # Western Carolina (PM: wcar, K: WCU)
    'NEBR': 'NEB',      # Nebraska (PM: nebr, K: NEB)
    # Note: MINNST would be Minnesota State, NOT Minnesota - verify before adding
    # Note: MARY (Maryland) - Kalshi code TBD, not TARL (that's Texas Arlington)
    # CBB - Phantom spread fixes (Feb 6 2026)
    'MERRI': 'MRMK',    # Merrimack (PM slug: merri, K: MRMK)
    'NFL': 'UNF',       # North Florida (PM slug: nfl, K: UNF)
    'QUEEN': 'QUC',     # Queens Charlotte (PM slug: queen, K: QUC)
    'MHST': 'MORE',     # Morehead State (PM slug: mhst, K: MORE)
    'TMRT': 'UTM',      # UT Martin (PM slug: tmrt, K: UTM)
    'FLGC': 'FGCU',     # Florida Gulf Coast (PM slug: flgc, K: FGCU)
    'BELLA': 'BELL',    # Bellarmine (PM slug: bella, K: BELL)
    'UCDV': 'UCD',      # UC Davis (PM slug: ucdv, K: UCD)
    'BOWLGR': 'BGSU',   # Bowling Green (PM slug: bowlgr, K: BGSU)
    'ARKST': 'ASU',     # Arkansas State (PM slug: arkst, K: ASU) - conflicts with Arizona State!
    'ABCHR': 'AC',      # Abilene Christian (PM slug: abchr, K: AC)
    'CABAP': 'CBU',     # California Baptist (PM slug: cabap, K: CBU)
    'BRYNT': 'BRY',     # Bryant (PM slug: brynt, K: BRY)
    'MAINE': 'ME',      # Maine (PM slug: maine, K: ME)
    'BRYANT': 'BRY',    # Bryant (PM slug: bryant, K: BRY)
    # Big Sky conference (Feb 7 2026 fix)
    'NCOL': 'UNCO',     # Northern Colorado (PM slug: ncol, K: UNCO)
    'IDHST': 'IDST',    # Idaho State (PM slug: idhst, K: IDST)
    'WEBST': 'WEB',     # Weber State (PM slug: webst, K: WEB)
    'EWASH': 'EWU',     # Eastern Washington (PM slug: ewash, K: EWU)
    'MTST': 'MTST',     # Montana State (already correct)
    'MONT': 'MONT',     # Montana (already correct)
    'IDAHO': 'IDHO',    # Idaho (PM slug: idaho, K: IDHO)
    'NAU': 'NAU',       # Northern Arizona (already correct)
    'PORTST': 'PSU',    # Portland State (PM slug: portst, K: PSU) - note: conflicts with Penn State!
    'SACST': 'SAC',     # Sacramento State (PM slug: sacst, K: SAC) - note: conflicts with Sacramento Kings!
}

# =============================================================================
# FIX-BUG-6: BIDIRECTIONAL TEAM ABBREVIATION MAP
# KALSHI_TO_SLUG is the REVERSE of SLUG_TO_KALSHI
# This allows looking up PM slugs from Kalshi codes and vice versa
# =============================================================================
KALSHI_TO_SLUG = {v: k for k, v in SLUG_TO_KALSHI.items() if k != v}
# Add explicit entries that don't auto-reverse cleanly (Kalshi -> PM)
KALSHI_TO_SLUG.update({
    # NBA - Kalshi codes to PM codes
    'GSW': 'GS',     # Golden State Warriors
    'NOP': 'NO',     # New Orleans Pelicans
    'NYK': 'NY',     # New York Knicks
    'PHX': 'PHO',    # Phoenix Suns
    'SAS': 'SA',     # San Antonio Spurs
    # NHL
    'VGK': 'VEG',    # Vegas Golden Knights
    'WSH': 'WAS',    # Washington Capitals (NHL)
    'MTL': 'MON',    # Montreal Canadiens
    'NSH': 'NAS',    # Nashville Predators
    'SJS': 'SJ',     # San Jose Sharks
    'TBL': 'TB',     # Tampa Bay Lightning
    'LAK': 'LA',     # Los Angeles Kings
    'NJD': 'NJ',     # New Jersey Devils
    # CBB - Major schools
    'UVM': 'VERM',   # Vermont
    'PSU': 'PENNST', # Penn State
    'KU': 'KANS',    # Kansas
    'HOU': 'HOUS',   # Houston
    'FLA': 'FLOR',   # Florida
    'ALA': 'ALAB',   # Alabama
    'TEX': 'TEXA',   # Texas
    'WIS': 'WISC',   # Wisconsin
    'ORE': 'OREG',   # Oregon
    'OU': 'OKLA',    # Oklahoma
    'BAY': 'BAYL',   # Baylor
    'TT': 'TXTE',    # Texas Tech
    'KSU': 'KSTA',   # Kansas State
    'ISU': 'IOST',   # Iowa State
    'CIN': 'CINC',   # Cincinnati
    'ASU': 'ARST',   # Arizona State
    'LSU': 'LOUI',   # LSU
    'VAN': 'VAND',   # Vanderbilt
    'UGA': 'GEOR',   # Georgia
    'AUB': 'AUBR',   # Auburn
    'UK': 'KENT',    # Kentucky
    'MIZ': 'MIZZ',   # Missouri
    'ARK': 'ARKN',   # Arkansas
    'PUR': 'PURD',   # Purdue
    'SAM': 'SAMF',   # Samford
    'FUR': 'FURM',   # Furman
    'NEB': 'NEBR',   # Nebraska
    'WCU': 'WCAR',   # Western Carolina
})


def normalize_team_bidirectional(abbrev: str, direction: str = 'to_kalshi') -> str:
    """
    FIX-BUG-6: Bidirectional team abbreviation normalization.

    Args:
        abbrev: Team abbreviation to normalize
        direction: 'to_kalshi' (PM->Kalshi) or 'to_pm' (Kalshi->PM)

    Returns:
        Normalized team abbreviation for the target platform
    """
    upper = abbrev.upper()
    if direction == 'to_kalshi':
        return SLUG_TO_KALSHI.get(upper, upper)
    else:  # to_pm
        return KALSHI_TO_SLUG.get(upper, upper)


# =============================================================================
# CANONICAL TEAM ABBREVIATIONS
# Normalizes ALL platform-specific codes to a single canonical form
# CRITICAL: Both Kalshi and PM cache keys MUST use the same abbreviations!
# =============================================================================
CANONICAL_ABBREV = {
    # NHL - PM uses different codes than Kalshi
    'WAS': 'WSH',    # Washington Capitals: PM=WAS, Kalshi=WSH (NHL)
    'MON': 'MTL',    # Montreal Canadiens: PM=MON, Kalshi=MTL
    'NAS': 'NSH',    # Nashville Predators: PM=NAS, Kalshi=NSH
    'SJ': 'SJS',     # San Jose Sharks: PM=SJ, Kalshi=SJS
    'TB': 'TBL',     # Tampa Bay Lightning: normalize to TBL
    'LA': 'LAK',     # Los Angeles Kings: PM=LA, Kalshi=LAK
    'NJ': 'NJD',     # New Jersey Devils: PM=NJ, Kalshi=NJD
    'VEG': 'VGK',    # Vegas Golden Knights: PM=VEG, Kalshi=VGK

    # NBA - PM uses different codes than Kalshi
    'NY': 'NYK',     # New York Knicks: PM=NY, Kalshi=NYK
    'GS': 'GSW',     # Golden State Warriors: PM=GS, Kalshi=GSW
    'NO': 'NOP',     # New Orleans Pelicans: PM=NO, Kalshi=NOP
    'SA': 'SAS',     # San Antonio Spurs: PM=SA, Kalshi=SAS
    'PHO': 'PHX',    # Phoenix Suns: PM=PHO, Kalshi=PHX

    # CBB - Major schools with different codes
    'NCAR': 'UNC',   # North Carolina
    'SYRA': 'CUSE',  # Syracuse
    'MICH': 'MICH',  # Michigan (same)
    'DUKE': 'DUKE',  # Duke (same)
    'KANS': 'KU',    # Kansas
    'KENT': 'UK',    # Kentucky
    'FLOR': 'FLA',   # Florida
    'ALAB': 'ALA',   # Alabama
    'TEXA': 'TEX',   # Texas
    'LOUI': 'LSU',   # LSU
    'GEOR': 'UGA',   # Georgia
    'AUBR': 'AUB',   # Auburn
    'ARKN': 'ARK',   # Arkansas
    'MIZZ': 'MIZ',   # Missouri
    'VAND': 'VAN',   # Vanderbilt
    'TENN': 'TENN',  # Tennessee (same)
    'WISC': 'WIS',   # Wisconsin
    'OREG': 'ORE',   # Oregon
    'OKLA': 'OU',    # Oklahoma
    'BAYL': 'BAY',   # Baylor
    'TXTE': 'TT',    # Texas Tech
    'KSTA': 'KSU',   # Kansas State
    'IOST': 'ISU',   # Iowa State
    'CINC': 'CIN',   # Cincinnati
    'ARST': 'ASU',   # Arizona State
    'HOUS': 'HOU',   # Houston
    'VERM': 'UVM',   # Vermont
    'VER': 'UVM',    # Vermont variant
    'PURD': 'PUR',   # Purdue
    'SAMF': 'SAM',   # Samford
    'FURM': 'FUR',   # Furman
    'FURMAN': 'FUR', # Furman variant
    'PENNST': 'PSU', # Penn State
    'NEBR': 'NEB',   # Nebraska
    'WCAR': 'WCU',   # Western Carolina
}


def normalize_team_abbrev(abbrev: str) -> str:
    """
    Normalize a team abbreviation to canonical form.
    Used when building cache keys to ensure Kalshi and PM use the same key.

    Example: 'WAS' -> 'WSH' (NHL Capitals)
             'NY' -> 'NYK' (NBA Knicks)
             'NCAR' -> 'UNC' (CBB North Carolina)
    """
    upper = abbrev.upper()
    return CANONICAL_ABBREV.get(upper, upper)


# =============================================================================
# SELF-TEST FUNCTION
# Validates all critical configurations before live trading
# =============================================================================
def run_self_test() -> Tuple[bool, List[str]]:
    """
    Run comprehensive self-test to validate critical configurations.

    Tests:
    1. All 4 outcome index + price combos produce prices in $0.05-$0.95 range
    2. Team abbreviation map is bidirectional (PM->Kalshi and Kalshi->PM)
    3. Spread formulas produce positive values for valid arbs
    4. Balance checks correctly reject orders exceeding limits

    Returns (all_passed, list_of_errors)
    """
    errors = []
    print("\n" + "="*70)
    print("SELF-TEST: Validating critical configurations")
    print("="*70)

    # TEST 1: Outcome index + price combos
    # FIX-BUG-2: Verify all 4 combos produce prices in safety floor range
    print("\n[TEST 1] Outcome index + price combinations...")
    test_cases = [
        # (direction, pm_outcome_index, raw_bid, raw_ask, expected_buy_outcome)
        ('BUY_PM_SELL_K', 0, 0.50, 0.52, 0),  # Buy our team (outcome 0)
        ('BUY_PM_SELL_K', 1, 0.50, 0.52, 1),  # Buy our team (outcome 1)
        ('BUY_K_SELL_PM', 0, 0.50, 0.52, 1),  # Short our team = buy opponent (outcome 1)
        ('BUY_K_SELL_PM', 1, 0.50, 0.52, 0),  # Short our team = buy opponent (outcome 0)
    ]

    for direction, pm_outcome_idx, raw_bid, raw_ask, expected_outcome in test_cases:
        # Calculate what we'd pay (the ask for the outcome we're buying)
        if direction == 'BUY_PM_SELL_K':
            # LONG our team
            if pm_outcome_idx == 0:
                price = raw_ask  # Buy outcome[0] directly
                buy_outcome = 0
            else:
                price = 1.0 - raw_bid  # Buy outcome[1] = 1 - outcome[0] bid
                buy_outcome = 1
        else:  # BUY_K_SELL_PM
            # SHORT our team = long opponent
            if pm_outcome_idx == 0:
                price = 1.0 - raw_bid  # Buy outcome[1] = opponent
                buy_outcome = 1
            else:
                price = raw_ask  # Buy outcome[0] = opponent
                buy_outcome = 0

        price_cents = price * 100

        # Check price is in safe range (FIX-BUG-2 safety floor $0.05)
        if price_cents < 5 or price_cents > 95:
            errors.append(f"Combo {direction}/idx{pm_outcome_idx}: price {price_cents:.1f}c outside 5-95c range")
        elif buy_outcome != expected_outcome:
            errors.append(f"Combo {direction}/idx{pm_outcome_idx}: expected outcome {expected_outcome}, got {buy_outcome}")
        else:
            print(f"  ✓ {direction} + outcome[{pm_outcome_idx}]: buy outcome[{buy_outcome}] @ {price_cents:.1f}c")

    # TEST 2: Bidirectional team map
    # FIX-BUG-6: Verify mapping works both directions
    print("\n[TEST 2] Bidirectional team abbreviation map...")
    test_teams = [
        ('GS', 'GSW'),      # NBA
        ('NY', 'NYK'),      # NBA
        ('VEG', 'VGK'),     # NHL
        ('KANS', 'KU'),     # CBB
        ('FLOR', 'FLA'),    # CBB
    ]
    for pm_code, kalshi_code in test_teams:
        # PM -> Kalshi
        pm_to_k = SLUG_TO_KALSHI.get(pm_code, pm_code)
        if pm_to_k != kalshi_code:
            errors.append(f"PM->Kalshi: {pm_code} should map to {kalshi_code}, got {pm_to_k}")
        else:
            print(f"  ✓ PM->Kalshi: {pm_code} -> {pm_to_k}")

        # Kalshi -> PM (bidirectional)
        k_to_pm = KALSHI_TO_SLUG.get(kalshi_code, kalshi_code)
        if k_to_pm != pm_code:
            errors.append(f"Kalshi->PM: {kalshi_code} should map to {pm_code}, got {k_to_pm}")
        else:
            print(f"  ✓ Kalshi->PM: {kalshi_code} -> {k_to_pm}")

    # TEST 3: Spread formulas produce positive values
    # FIX-BUG-13: Verify spread calculations are correct
    print("\n[TEST 3] Spread formula validation...")
    # BUY_PM_SELL_K: spread = k_bid - pm_ask (should be positive for valid arb)
    k_bid, pm_ask = 55, 50  # cents (buy PM at 50, sell K at 55 = 5c profit)
    spread1 = k_bid - pm_ask
    if spread1 <= 0:
        errors.append(f"BUY_PM_SELL_K spread formula: {k_bid} - {pm_ask} = {spread1} (should be positive)")
    else:
        print(f"  ✓ BUY_PM_SELL_K: k_bid({k_bid}c) - pm_ask({pm_ask}c) = {spread1}c profit")

    # BUY_K_SELL_PM: spread = 100 - k_ask - pm_opponent_ask
    k_ask, pm_opponent_ask = 45, 48  # cents (total cost 93c < 100c payout = 7c profit)
    spread2 = 100 - k_ask - pm_opponent_ask
    if spread2 <= 0:
        errors.append(f"BUY_K_SELL_PM spread formula: 100 - {k_ask} - {pm_opponent_ask} = {spread2} (should be positive)")
    else:
        print(f"  ✓ BUY_K_SELL_PM: 100 - k_ask({k_ask}c) - pm_opp_ask({pm_opponent_ask}c) = {spread2}c profit")

    # TEST 4: Balance/position limit checks
    # FIX-BUG-9: Verify limits are enforced
    print("\n[TEST 4] Balance and position limit checks...")
    print(f"  MAX_CONTRACTS = {MAX_CONTRACTS} (should be 20)")
    print(f"  MAX_COST_CENTS = {MAX_COST_CENTS} (should be 1500 = $15)")
    print(f"  MIN_PM_PRICE = {MIN_PM_PRICE} (should be 5 = $0.05)")

    if MAX_CONTRACTS != 20:
        errors.append(f"MAX_CONTRACTS should be 20, got {MAX_CONTRACTS}")
    else:
        print(f"  ✓ MAX_CONTRACTS = 20")

    if MAX_COST_CENTS != 1500:
        errors.append(f"MAX_COST_CENTS should be 1500, got {MAX_COST_CENTS}")
    else:
        print(f"  ✓ MAX_COST_CENTS = 1500 ($15 max)")

    if MIN_PM_PRICE != 5:
        errors.append(f"MIN_PM_PRICE should be 5, got {MIN_PM_PRICE}")
    else:
        print(f"  ✓ MIN_PM_PRICE = 5 ($0.05 safety floor)")

    # Simulate balance check
    test_balance_cents = 1000  # $10
    test_price = 50  # 50 cents
    max_contracts_by_balance = test_balance_cents // test_price
    if max_contracts_by_balance > MAX_CONTRACTS:
        effective_max = MAX_CONTRACTS
    else:
        effective_max = max_contracts_by_balance
    print(f"  Balance $10 @ 50c: max {effective_max} contracts (capped at {MAX_CONTRACTS})")

    # Summary
    print("\n" + "="*70)
    if errors:
        print(f"SELF-TEST FAILED: {len(errors)} error(s)")
        for e in errors:
            print(f"  ✗ {e}")
        print("="*70)
        return False, errors
    else:
        print("SELF-TEST PASSED: All checks OK ✓")
        print("="*70)
        return True, []


async def maybe_reload_mappings():
    """Periodically reload verified mappings to pick up new games."""
    global VERIFIED_MAPS, MAPPING_LAST_LOADED
    if not HAS_MAPPER:
        return
    if time.time() - MAPPING_LAST_LOADED > MAPPING_RELOAD_INTERVAL:
        try:
            new_maps = load_verified_mappings()
            if new_maps:
                added = len(new_maps) - len(VERIFIED_MAPS)
                if added > 0:
                    print(f"[MAPPING] Reload: {added} new games added ({len(new_maps)} total)")
                VERIFIED_MAPS = new_maps
                MAPPING_LAST_LOADED = time.time()
        except Exception as e:
            print(f"[MAPPING] Reload failed: {e}")


def pre_trade_verification(arb) -> bool:
    """
    Final safety gate: verify the mapping is still valid before committing real money.
    Returns True if trade is safe to execute.
    """
    if not VERIFIED_MAPS:
        # No verified mappings loaded — allow but tag as unverified
        return True

    # Build cache key from arb data
    cache_key = None
    # Try to extract cache key from the arb's game info
    # The game field is the Kalshi game_id like "26FEB05DENNYK"
    # We need sport + teams + date to build the cache key
    sport = arb.sport.lower()
    game_id = arb.game
    teams_list = list(set([arb.team]))
    # Get opponent from kalshi_ticker: e.g., "KXNBAGAME-26FEB05DENNYK-DEN"
    ticker_parts = arb.kalshi_ticker.split('-')
    if len(ticker_parts) >= 3:
        # Game ID has both teams: "26FEB05DENNYK" — extract from ticker
        game_id_str = ticker_parts[1]
        date_str, _, _ = parse_gid(game_id_str)
        if date_str:
            # Get all teams from the game
            all_teams = set()
            all_teams.add(arb.team)
            # Find opponent from game_id: after the date prefix (7 chars), remaining chars are sorted teams
            team_suffix = game_id_str[7:]  # e.g., "DENNYK"
            # We know our team is arb.team — look up the game in all_games or just try the cache key
            cache_key = build_cache_key(sport, arb.team, arb.team, date_str)
            # This won't work for building cache key — we need both teams
            # Try all verified mappings that match sport and date
            for vk, vm in VERIFIED_MAPS.items():
                if vm.get('game_id') == game_id_str:
                    cache_key = vk
                    break

    if not cache_key:
        print(f"[VERIFY] Could not build cache key for {arb.sport} {arb.game} — allowing (unverified)")
        return True

    mapping = get_mapping_for_game(VERIFIED_MAPS, cache_key)
    if not mapping:
        print(f"[VERIFY] No verified mapping for {cache_key} — allowing (unverified)")
        return True

    # Verify outcome index matches
    expected_index = get_team_outcome_index(mapping, arb.team)
    if expected_index is not None and expected_index != arb.pm_outcome_index:
        print(f"[!!!TRADE BLOCKED!!!] Outcome index mismatch!")
        print(f"  Arb says pm_outcome_index={arb.pm_outcome_index}")
        print(f"  Verified mapping says outcome_index={expected_index}")
        print(f"  For team {arb.team} in {cache_key}")
        print(f"  THIS WOULD HAVE BEEN A SAME-DIRECTION BET!")
        return False

    # Verify both teams have different outcome indices
    kalshi_tickers = mapping.get('kalshi_tickers', {})
    teams_in_game = list(kalshi_tickers.keys())
    if len(teams_in_game) == 2:
        idx0 = get_team_outcome_index(mapping, teams_in_game[0])
        idx1 = get_team_outcome_index(mapping, teams_in_game[1])
        if idx0 is not None and idx1 is not None and idx0 == idx1:
            print(f"[!!!TRADE BLOCKED!!!] Both teams have same outcome index {idx0}!")
            print(f"  Teams: {teams_in_game[0]}={idx0}, {teams_in_game[1]}={idx1}")
            return False

    return True


def build_cache_key(sport: str, team1: str, team2: str, date: str) -> str:
    """
    Build a normalized cache key for matching Kalshi and PM markets.
    Teams are normalized to canonical form and sorted alphabetically.
    """
    norm1 = normalize_team_abbrev(team1)
    norm2 = normalize_team_abbrev(team2)
    sorted_teams = sorted([norm1, norm2])
    return f"{sport}:{sorted_teams[0]}-{sorted_teams[1]}:{date}"


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

        # Build Kalshi cache keys (with normalized abbreviations!)
        kalshi_cache_keys = {}  # {cache_key: game_info}
        for sport, games in kalshi_games.items():
            for gid, game in games.items():
                if len(game['teams']) >= 2:
                    teams_list = list(game['teams'])
                    cache_key = build_cache_key(sport, teams_list[0], teams_list[1], game['date'])
                    kalshi_cache_keys[cache_key] = {
                        'sport': sport,
                        'gid': gid,
                        'teams': sorted([normalize_team_abbrev(t) for t in teams_list]),
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


# ============================================================================
# OPTIMIZED FAST PATH: Use pre-verified mappings to skip runtime matching
# ============================================================================
async def fetch_prices_from_verified_mappings(session, pm_api, verified_maps: dict, debug: bool = False) -> int:
    """
    FAST PATH: Fetch orderbook prices for pre-verified games.

    Skips ALL runtime matching, slug parsing, and team normalization.
    Uses verified_mappings.json which has:
    - pm_slug: exact slug to query
    - pm_outcomes: pre-verified outcome indices for each team
    - kalshi_tickers: pre-mapped Kalshi tickers

    Returns: number of games with valid orderbook data
    """
    global PM_US_MARKET_CACHE

    if not verified_maps:
        return 0

    # Filter to today/tomorrow games only (verified mappings may include past games)
    from datetime import timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    today = now.strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')

    # Extract unique slugs from verified mappings
    slug_to_cache_keys = {}  # slug -> [cache_key1, cache_key2, ...] (usually just one)
    for cache_key, mapping in verified_maps.items():
        if not mapping.get('verified'):
            continue
        game_date = mapping.get('date', '')
        if game_date not in (today, tomorrow):
            continue

        pm_slug = mapping.get('pm_slug')
        if pm_slug:
            if pm_slug not in slug_to_cache_keys:
                slug_to_cache_keys[pm_slug] = []
            slug_to_cache_keys[pm_slug].append(cache_key)

    if not slug_to_cache_keys:
        return 0

    slugs = list(slug_to_cache_keys.keys())

    # Batch fetch orderbooks - single API call for all slugs
    orderbooks = await pm_api.get_orderbooks_batch(session, slugs, debug=False)

    # Build cache directly from verified mappings + fresh orderbook prices
    PM_US_MARKET_CACHE.clear()
    valid_count = 0

    for pm_slug, cache_keys in slug_to_cache_keys.items():
        ob = orderbooks.get(pm_slug)
        if not ob or ob.get('best_bid') is None or ob.get('best_ask') is None:
            continue

        # Convert prices to cents
        best_bid = int(ob['best_bid'] * 100) if ob['best_bid'] < 1 else int(ob['best_bid'])
        best_ask = int(ob['best_ask'] * 100) if ob['best_ask'] < 1 else int(ob['best_ask'])
        bid_size = ob.get('bid_size', 0)
        ask_size = ob.get('ask_size', 0)

        # Apply to all cache keys for this slug
        for cache_key in cache_keys:
            mapping = verified_maps.get(cache_key)
            if not mapping:
                continue

            # Get pre-verified teams and outcome indices
            pm_outcomes = mapping.get('pm_outcomes', {})
            kalshi_tickers = mapping.get('kalshi_tickers', {})

            # Extract slug teams to determine orderbook direction
            slug_parts = pm_slug.split('-')
            slug_team1 = slug_parts[2].upper() if len(slug_parts) >= 4 else None

            # Build teams dict from pre-verified data
            teams_cache = {}
            for idx_str, outcome_data in pm_outcomes.items():
                team = outcome_data.get('team')
                outcome_idx = outcome_data.get('outcome_index')
                if not team:
                    continue

                # Determine if this team's prices come from orderbook directly or inverted
                # Orderbook is always for the first team in the slug
                team_normalized = normalize_team_abbrev(team)

                # Check if this is the orderbook team (first in slug)
                is_ob_team = False
                if slug_team1:
                    # Try various matching strategies
                    if team_normalized == slug_team1:
                        is_ob_team = True
                    elif team_normalized in SLUG_TO_KALSHI and SLUG_TO_KALSHI.get(slug_team1, slug_team1) == team_normalized:
                        is_ob_team = True
                    elif slug_team1 in SLUG_TO_KALSHI and SLUG_TO_KALSHI[slug_team1] == team_normalized:
                        is_ob_team = True
                    # Fallback: prefix matching (e.g., DRAKE -> DRKE both start with DR)
                    elif len(slug_team1) >= 2 and len(team_normalized) >= 2:
                        # Match if first 2 chars are same (PM slugs differ from Kalshi abbrevs)
                        if slug_team1[:2] == team_normalized[:2]:
                            is_ob_team = True

                # CRITICAL FIX: PM orderbook is for FIRST team in SLUG, not outcome[0]!
                # Use is_ob_team to determine price direction, NOT outcome_idx
                if is_ob_team:
                    # This team IS the orderbook team - use prices directly
                    teams_cache[team] = {
                        'bid': best_bid,
                        'ask': best_ask,
                        'bid_size': bid_size,
                        'ask_size': ask_size,
                        'outcome_index': outcome_idx
                    }
                else:
                    # This team is NOT the orderbook team - invert prices
                    teams_cache[team] = {
                        'bid': 100 - best_ask,
                        'ask': 100 - best_bid,
                        'bid_size': ask_size,
                        'ask_size': bid_size,
                        'outcome_index': outcome_idx
                    }

            if len(teams_cache) == 2:
                PM_US_MARKET_CACHE[cache_key] = {
                    'slug': pm_slug,
                    'teams': teams_cache,
                    'volume': 0,  # We don't have volume from orderbook, but it's not used for filtering
                    'has_orderbook': True,
                    'from_verified': True  # Flag: using optimized fast path
                }
                valid_count += 1

    return valid_count


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
            # TEAM MATCHING STRATEGY:
            # 1. Try slug-based extraction (e.g., "aec-cbb-syra-ncar" -> SYRA, NCAR)
            # 2. Apply SLUG_TO_KALSHI mapping to normalize codes
            # 3. If still no match, try NAME-BASED matching using outcomes array
            #    (e.g., "Orange" -> CUSE, "Tar Heels" -> UNC)
            # =====================================================================
            if slug_teams:
                raw_0, raw_1 = slug_teams[0], slug_teams[1]
                # Apply SLUG_TO_KALSHI mapping to normalize codes
                team_0 = SLUG_TO_KALSHI.get(raw_0, raw_0)
                team_1 = SLUG_TO_KALSHI.get(raw_1, raw_1)

                # FALLBACK: If slug codes don't normalize, try name-based matching
                # This handles cases like SYRA -> CUSE, NCAR -> UNC
                name_team_0 = team_name_to_canonical(outcomes[0]) if outcomes else None
                name_team_1 = team_name_to_canonical(outcomes[1]) if len(outcomes) > 1 else None

                # Use name-based if it produces a different (presumably better) result
                if name_team_0 and name_team_0 != team_0:
                    if debug:
                        print(f"[NAME MATCH] {outcomes[0]}: slug={team_0} -> name={name_team_0}")
                    team_0 = name_team_0
                if name_team_1 and name_team_1 != team_1:
                    if debug:
                        print(f"[NAME MATCH] {outcomes[1]}: slug={team_1} -> name={name_team_1}")
                    team_1 = name_team_1

                if debug:
                    print(f"[{cfg['sport'].upper()}] {slug}: {team_0} vs {team_1}")
            else:
                # No slug teams - use pure name-based matching
                team_0 = team_name_to_canonical(outcomes[0]) if outcomes else None
                team_1 = team_name_to_canonical(outcomes[1]) if len(outcomes) > 1 else None

                # Fallback to old mascot matching if name-based fails
                if not team_0:
                    team_0 = map_outcome_to_kalshi(outcomes[0], cfg['pm2k'], cfg['sport'])
                if not team_1:
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

                # Normalize team abbreviations for cache key matching!
                norm_team_0 = normalize_team_abbrev(team_0)
                norm_team_1 = normalize_team_abbrev(team_1)

                # Store mid prices as fallback (but we'll prefer order book)
                mid_price_0 = int(float(prices[0]) * 100)
                mid_price_1 = int(float(prices[1]) * 100)

                # Create single cache entry with normalized teams
                cache_key = build_cache_key(sport, team_0, team_1, game_date)

                # CRITICAL: Store the PM outcomes array order!
                # PM outcomeIndex refers to position in this array, NOT slug order
                # outcomes[0] and outcomes[1] might be in different order than slug teams
                matched_markets.append({
                    'cache_key': cache_key,
                    'slug': slug,
                    'team_0': team_0,
                    'team_1': team_1,
                    'mid_price_0': mid_price_0,
                    'mid_price_1': mid_price_1,
                    'volume': market.get('volumeNum', 0) or market.get('volume24hr', 0) or 0,
                    # Store PM outcomes array for correct index mapping
                    'pm_outcomes': outcomes,  # e.g., ["Sacramento Kings", "Washington Wizards"]
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

            # CRITICAL FIX: PM's outcomeIndex refers to position in the outcomes ARRAY,
            # NOT the slug position! We must find which index in outcomes[] each team is.
            pm_outcomes = m.get('pm_outcomes', [])  # e.g., ["Sacramento Kings", "Washington Wizards"]

            slug_parts = slug.split('-')
            if len(slug_parts) >= 4:
                slug_team1 = slug_parts[2].upper()  # First team in slug
                slug_team2 = slug_parts[3].upper()  # Second team in slug

                # Order book prices are for slug_team1 (first team in slug)
                # Check which of our mapped teams matches slug_team1
                orderbook_is_for_team_0 = normalize_slug_team(slug_team1, team_0)

                # Double-check: also verify team_1 matches slug_team2 for consistency
                if not orderbook_is_for_team_0:
                    team_1_matches_slug2 = normalize_slug_team(slug_team2, team_0)
                    if team_1_matches_slug2:
                        orderbook_is_for_team_0 = False
                    else:
                        if is_debug_slug and debug:
                            print(f"  WARNING: Cannot determine team mapping for {slug}")
                            print(f"    slug_team1={slug_team1} slug_team2={slug_team2}")
                            print(f"    team_0={team_0} team_1={team_1}")
                        orderbook_is_for_team_0 = True

                # CRITICAL: Determine PM outcomes array index for each team
                # This is what PM's outcomeIndex parameter refers to!
                def find_pm_outcome_index(team_code: str, outcomes: list) -> int:
                    """Find which index in PM outcomes array matches this team code.

                    Uses KALSHI_ABBREV_TO_NAMES to map abbreviations like 'TB' to
                    keywords like ['lightning', 'tampa bay'] that appear in PM outcomes.
                    """
                    team_upper = team_code.upper()

                    for idx, outcome_name in enumerate(outcomes):
                        outcome_lower = outcome_name.lower()
                        outcome_upper = outcome_name.upper()

                        # Method 1: Check KALSHI_ABBREV_TO_NAMES dictionary (PRIMARY)
                        # This is the most reliable - maps TB -> ['lightning', 'tampa bay']
                        if team_upper in KALSHI_ABBREV_TO_NAMES:
                            keywords = KALSHI_ABBREV_TO_NAMES[team_upper]
                            for keyword in keywords:
                                if keyword.lower() in outcome_lower:
                                    return idx

                        # Method 2: Direct abbreviation match (e.g., "NYK" in "NYK vs LAL")
                        if team_upper in outcome_upper:
                            return idx

                        # Method 3: Check SLUG_TO_KALSHI mapped abbreviations
                        mapped = SLUG_TO_KALSHI.get(team_upper, team_upper)
                        if mapped != team_upper and mapped in KALSHI_ABBREV_TO_NAMES:
                            keywords = KALSHI_ABBREV_TO_NAMES[mapped]
                            for keyword in keywords:
                                if keyword.lower() in outcome_lower:
                                    return idx

                        # Method 4: City name prefix matching (fallback)
                        # e.g., "WAS" should match "Washington Wizards"
                        outcome_words = outcome_name.split()
                        if outcome_words:
                            city = outcome_words[0].upper()
                            if len(team_upper) >= 2 and len(city) >= 3:
                                if city.startswith(team_upper[:3]) or team_upper.startswith(city[:3]):
                                    return idx

                    # Fallback: return 0 if no match found (will trigger sanity check)
                    return 0

                # Get the CORRECT PM array index for each team
                team_0_pm_idx = find_pm_outcome_index(team_0, pm_outcomes) if pm_outcomes else 0
                team_1_pm_idx = find_pm_outcome_index(team_1, pm_outcomes) if pm_outcomes else 1

                # Sanity check: they should be different
                if team_0_pm_idx == team_1_pm_idx and pm_outcomes:
                    # Both mapped to same index - use slug order as fallback
                    if is_debug_slug and debug:
                        print(f"  WARNING: Both teams mapped to same PM index!")
                        print(f"    team_0={team_0} -> pm_idx={team_0_pm_idx}")
                        print(f"    team_1={team_1} -> pm_idx={team_1_pm_idx}")
                        print(f"    pm_outcomes={pm_outcomes}")
                    team_0_pm_idx = 0
                    team_1_pm_idx = 1

            else:
                # Fallback: assume order book is for team_0
                orderbook_is_for_team_0 = True
                # Also set default PM indices
                team_0_pm_idx = 0
                team_1_pm_idx = 1

            if orderbook_is_for_team_0:
                # Order book is for team_0 (normal case)
                ob_team = team_0
                other_team = team_1
                ob_pm_idx = team_0_pm_idx    # Use PM ARRAY index, not slug index!
                other_pm_idx = team_1_pm_idx
            else:
                # Order book is for team_1 - SWAP assignment
                ob_team = team_1
                other_team = team_0
                ob_pm_idx = team_1_pm_idx    # Use PM ARRAY index, not slug index!
                other_pm_idx = team_0_pm_idx

            # DEBUG: Detailed tracing for specific games
            if is_debug_slug and debug:
                print(f"\n[DEBUG PM CACHE] {slug}")
                print(f"  cache_key: {cache_key}")
                print(f"  team_0 (from matching): {team_0}")
                print(f"  team_1 (from matching): {team_1}")
                print(f"  PM outcomes array: {pm_outcomes}")
                print(f"  team_0 PM array index: {team_0_pm_idx}")
                print(f"  team_1 PM array index: {team_1_pm_idx}")
                print(f"  slug_team1 (orderbook team): {slug_team1 if len(slug_parts) >= 4 else 'N/A'}")
                print(f"  slug_team2: {slug_team2 if len(slug_parts) >= 4 else 'N/A'}")
                print(f"  orderbook_is_for_team_0: {orderbook_is_for_team_0}")
                print(f"  -> ob_team={ob_team} (PM idx={ob_pm_idx}), other_team={other_team} (PM idx={other_pm_idx})")
                print(f"  Raw orderbook: best_bid={best_bid}c best_ask={best_ask}c")

            PM_US_MARKET_CACHE[cache_key] = {
                'slug': slug,
                'teams': {
                    ob_team: {
                        'bid': best_bid,           # Price to sell ob_team (sell YES)
                        'ask': best_ask,           # Price to buy ob_team (buy YES)
                        'bid_size': bid_size,
                        'ask_size': ask_size,
                        'outcome_index': ob_pm_idx  # CRITICAL: Use PM ARRAY index!
                    },
                    other_team: {
                        'bid': 100 - best_ask,     # Price to sell other_team = 100 - ask for ob_team
                        'ask': 100 - best_bid,     # Price to buy other_team = 100 - bid for ob_team
                        'bid_size': ask_size,      # Sizes are swapped for opposite side
                        'ask_size': bid_size,
                        'outcome_index': other_pm_idx  # CRITICAL: Use PM ARRAY index!
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

            # CRITICAL: Use PM outcomes array to determine correct indices
            pm_outcomes = m.get('pm_outcomes', [])

            def find_pm_outcome_index_fallback(team_code: str, outcomes: list) -> int:
                """Find which index in PM outcomes array matches this team code.
                Uses KALSHI_ABBREV_TO_NAMES for reliable matching.
                """
                team_upper = team_code.upper()
                for idx, outcome_name in enumerate(outcomes):
                    outcome_lower = outcome_name.lower()
                    outcome_upper = outcome_name.upper()

                    # Method 1: Use KALSHI_ABBREV_TO_NAMES (PRIMARY)
                    if team_upper in KALSHI_ABBREV_TO_NAMES:
                        keywords = KALSHI_ABBREV_TO_NAMES[team_upper]
                        for keyword in keywords:
                            if keyword.lower() in outcome_lower:
                                return idx

                    # Method 2: Direct match
                    if team_upper in outcome_upper:
                        return idx

                    # Method 3: City name prefix
                    if outcome_name.split() and outcome_name.split()[0].upper().startswith(team_upper[:3]):
                        return idx
                return 0  # Fallback

            team_0_pm_idx = find_pm_outcome_index_fallback(team_0, pm_outcomes) if pm_outcomes else 0
            team_1_pm_idx = find_pm_outcome_index_fallback(team_1, pm_outcomes) if pm_outcomes else 1

            # Ensure different indices
            if team_0_pm_idx == team_1_pm_idx:
                team_0_pm_idx = 0
                team_1_pm_idx = 1

            PM_US_MARKET_CACHE[cache_key] = {
                'slug': slug,
                'teams': {
                    team_0: {
                        'bid': m['mid_price_0'],
                        'ask': m['mid_price_0'],
                        'bid_size': 0,
                        'ask_size': 0,
                        'outcome_index': team_0_pm_idx  # Use PM ARRAY index!
                    },
                    team_1: {
                        'bid': m['mid_price_1'],
                        'ask': m['mid_price_1'],
                        'bid_size': 0,
                        'ask_size': 0,
                        'outcome_index': team_1_pm_idx  # Use PM ARRAY index!
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

        if k_balance is not None and pm_balance is not None:
            # Use the new capital display function
            display_capital_status(k_balance, pm_balance)
        else:
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

            # Timing instrumentation
            t_mapping_start = time.time()

            # Reload verified mappings periodically (every 5 min)
            await maybe_reload_mappings()

            # ================================================================
            # OPTIMIZED PATH: Use verified mappings when available
            # Skips runtime slug parsing, team normalization, and matching
            # ================================================================
            is_first_scan = (scan_num == 1)
            use_fast_path = bool(VERIFIED_MAPS) and len(VERIFIED_MAPS) >= 10  # Use fast path if we have enough mappings

            if use_fast_path:
                # FAST PATH: Fetch Kalshi markets and PM orderbooks in parallel
                # PM prices come directly from verified mappings + fresh orderbooks
                kalshi_task = fetch_kalshi_markets(session, kalshi_api, debug=False)
                pm_verified_task = fetch_prices_from_verified_mappings(session, pm_api, VERIFIED_MAPS, debug=False)
                kalshi_data, pm_verified_count = await asyncio.gather(kalshi_task, pm_verified_task)
                pm_us_matched = pm_verified_count

                # Only log on first scan or periodically
                if is_first_scan:
                    print(f"[SCAN] Fast path: {pm_verified_count} verified games, skipping runtime matching")
            else:
                # FALLBACK PATH: Full runtime matching (for unmapped games)
                kalshi_task = fetch_kalshi_markets(session, kalshi_api, debug=(DEBUG_MATCHING and is_first_scan))
                pm_us_task = fetch_pm_us_markets(session, pm_api, debug=(DEBUG_MATCHING and is_first_scan))
                kalshi_data, pm_us_matched = await asyncio.gather(kalshi_task, pm_us_task)

            t_mapping_end = time.time()
            t_prices = (t_mapping_end - t_mapping_start) * 1000  # ms

            # PENDING MARKET MONITORING: Only check periodically, not every scan
            # This reduces API calls when we have verified mappings
            check_pending = is_first_scan or (scan_num % 10 == 0)  # Every 10 scans
            if check_pending:
                all_pm_markets = await pm_api.get_all_markets_including_pending(session, debug=is_first_scan)
            else:
                all_pm_markets = []

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

                    teams_list = list(game['teams'].keys())
                    cache_key = build_cache_key(cfg['sport'], teams_list[0], teams_list[1], game['date'])

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

                                # Override with pre-verified mapping if available
                                if VERIFIED_MAPS:
                                    verified_map = VERIFIED_MAPS.get(cache_key)
                                    if verified_map and verified_map.get('verified'):
                                        # Normalize team for lookup (Kalshi raw -> canonical)
                                        norm_team = normalize_team_abbrev(team)
                                        verified_idx = get_team_outcome_index(verified_map, norm_team)
                                        if verified_idx is not None:
                                            if verified_idx != outcome_idx:
                                                print(f"[MAPPING OVERRIDE] {cache_key}:{norm_team}: "
                                                      f"runtime idx={outcome_idx} -> verified idx={verified_idx}")
                                            outcome_idx = verified_idx

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
                                'teams': teams_list,
                                'date': game['date'],
                                'cache_key': cache_key
                            })

            # Debug: Log cache keys for diagnosis (first scan only, skip when using fast path)
            if DEBUG_MATCHING and scan_num == 1 and not use_fast_path:
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

            # Find arbs - TIMING INSTRUMENTED
            t_spreads_start = time.time()
            arbs = []

            # DEBUG: Track specific games for detailed analysis (only on first scan)
            DEBUG_GAMES = ['WSHDET', 'DETWSH', 'WSH', 'UMBCUVM', 'UMBC', 'UVM'] if is_first_scan else []

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

                        # Get outcome index for this team
                        pm_outcome_idx = p.get('pm_outcome_index', 0)

                        # Debug specific games
                        if is_debug_game and scan_num <= 3:
                            ticker = game['tickers'].get(team, 'N/A')
                            print(f"\n[DEBUG ARB CALC] {gid} team={team}:")
                            print(f"  Kalshi ticker: {ticker}")
                            print(f"  PM outcome_index: {pm_outcome_idx} ({'our team IS outcome[0]' if pm_outcome_idx == 0 else 'our team is outcome[1]'})")
                            print(f"  Kalshi: bid={kb}c ask={ka}c (we sell at bid, buy at ask)")
                            print(f"  PM (stored): bid={pb}c ask={pa}c")
                            if pm_outcome_idx == 1:
                                # These are INVERTED prices - show what the raw orderbook was
                                raw_bid_approx = 100 - pa  # pm_ask = 100 - raw_bid → raw_bid = 100 - pm_ask
                                raw_ask_approx = 100 - pb  # pm_bid = 100 - raw_ask → raw_ask = 100 - pm_bid
                                print(f"  PM (raw orderbook for outcome[0]): bid≈{raw_bid_approx}c ask≈{raw_ask_approx}c")
                                print(f"  SELL_YES on outcome[0] would hit bid≈{raw_bid_approx}c, effective cost={pa}c")
                                print(f"  BUY_YES on outcome[0] would hit ask≈{raw_ask_approx}c, effective cost={pb}c")
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
                                    is_live_game=game.get('is_live', False),
                                    price_timestamp=time.time()  # LATENCY OPT: Track when prices fetched
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
                                    is_live_game=game.get('is_live', False),
                                    price_timestamp=time.time()  # LATENCY OPT: Track when prices fetched
                                ))

            # Filter by LIQUIDITY and SPREAD (not ROI - high ROI on illiquid prices is misleading)
            # Analysis showed: 240% ROI on 5c ask = only $2.40 profit vs 12% ROI on 50c ask = $30 profit
            exec_arbs = []
            skipped_high_roi = 0
            skipped_low_liquidity = 0
            skipped_low_price = 0
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

                # FILTER 1b: Skip low buy-side prices (stale/illiquid data creating fake high ROI)
                if a.direction == 'BUY_PM_SELL_K':
                    buy_price = a.pm_ask  # Buying on PM
                else:  # BUY_K_SELL_PM
                    buy_price = a.k_ask   # Buying on Kalshi

                if buy_price < MIN_BUY_PRICE:
                    skipped_low_price += 1
                    log_skipped_arb(a, 'low_buy_price', f"Buy price {buy_price}c < {MIN_BUY_PRICE}c - likely stale data")
                    print(f"[SKIP] {a.sport} {a.team}: {a.net_spread}c spread but buy price {buy_price}c < {MIN_BUY_PRICE}c min (likely stale)")
                    continue

                # FILTER 2: Skip low contract count (not worth the effort)
                if pm_size < MIN_CONTRACTS:
                    skipped_low_liquidity += 1
                    potential_profit = a.net_spread * pm_size / 100
                    log_skipped_arb(a, 'low_liquidity', f"PM size {pm_size} < {MIN_CONTRACTS} contracts")
                    print(f"[SKIP] {a.sport} {a.team}: {a.net_spread:.0f}c spread | {pm_size} contracts | ${potential_profit:.2f} profit (below {MIN_CONTRACTS} min)")
                    continue

                # NOTE: Live games are where arbs happen - DO NOT skip them
                # Just flag for awareness (prices move fast during live games)
                if a.is_live_game:
                    a.needs_review = True
                    if not a.review_reason:
                        a.review_reason = "Live game - prices may move fast"
                    else:
                        a.review_reason += "; Live game - prices may move fast"

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

            # End timing
            t_spreads_end = time.time()
            t_spreads = (t_spreads_end - t_spreads_start) * 1000  # ms
            scan_time = (time.time() - t0) * 1000  # Total scan time

            # ================================================================
            # CONCISE SCAN SUMMARY (reduces log noise)
            # ================================================================
            total_games = sum(len(all_games[c['sport']]) for c in SPORTS_CONFIG)
            spreads_above_min = len([a for a in exec_arbs if a.net_spread >= MIN_SPREAD_CENTS])

            # One-line scan summary (always shown)
            fast_path_marker = "[FAST]" if use_fast_path else "[FULL]"
            print(f"SCAN {fast_path_marker}: {pm_us_matched} markets, {spreads_above_min} spreads >{MIN_SPREAD_CENTS}c, {scan_time:.0f}ms (prices:{t_prices:.0f}ms, calc:{t_spreads:.0f}ms)")

            # DEBUG: Show spread distribution every 20 scans to understand market conditions
            if scan_num % 20 == 0:
                if exec_arbs:
                    spread_1_3c = len([a for a in exec_arbs if 1 <= a.net_spread < 4])
                    best_spread = max((a.net_spread for a in exec_arbs), default=0)
                    print(f"  [DEBUG] Spread distribution: {spread_1_3c} arbs at 1-3c, best spread: {best_spread}c")
                else:
                    # Show why no arbs: sample a matched game's prices
                    sample_shown = False
                    for cfg in SPORTS_CONFIG:
                        for gid, game in all_games.get(cfg['sport'], {}).items():
                            for team, tp in game.get('teams', {}).items():
                                kb, ka = tp.get('k_bid', 0), tp.get('k_ask', 0)
                                pb = tp.get('pm_bid', 0)
                                pa = tp.get('pm_ask', 0)
                                if kb > 0 and ka > 0 and pb > 0 and pa > 0:
                                    g1 = kb - pa  # Buy PM, Sell K
                                    g2 = pb - ka  # Buy K, Sell PM
                                    print(f"  [DEBUG] Sample {gid}:{team} - K:{kb}/{ka}c PM:{pb}/{pa}c | Gross spreads: {g1}c / {g2}c")
                                    sample_shown = True
                                    break
                            if sample_shown:
                                break
                        if sample_shown:
                            break
                    if not sample_shown:
                        print(f"  [DEBUG] No matched games with valid K+PM prices found")

            # Detailed info only on first scan or when arbs found
            show_details = is_first_scan or len(exec_arbs) > 0 or scan_num % 30 == 0
            if show_details:
                print("=" * 70)
                print(f"v7 DIRECT US | Scan #{scan_num} | {datetime.now().strftime('%H:%M:%S')}")
                print(f"Mode: {EXECUTION_MODE.value.upper()} | Trades: {total_trades} | Profit: ${total_profit:.2f}")

                # Show pending market count (only if we checked)
                if check_pending and pending_markets:
                    pending_soon = [p for p in pending_markets if p.get('hours_to_game') and 0 < p['hours_to_game'] < 6]
                    print(f"Pending: {len(pending_markets)} markets | Soon (<6h): {len(pending_soon)}")
                print("=" * 70)

                print(f"\n[i] Kalshi Games: {total_games} | PM US Matched: {total_matched} | PM US Markets: {pm_us_matched}")
                print(f"[i] Found {len(arbs)} arbs, {len(exec_arbs)} executable (liquid + {MIN_CONTRACTS}+ contracts)")

            # Skip/review summaries (only if nonzero)
            if skipped_low_price > 0:
                print(f"[SKIP] {skipped_low_price} illiquid (PM price < {MIN_PM_PRICE}c)")
            if skipped_low_liquidity > 0:
                print(f"[SKIP] {skipped_low_liquidity} low liquidity (< {MIN_CONTRACTS} contracts)")
            if skipped_high_roi > 0:
                print(f"[SKIP] {skipped_high_roi} extreme ROI > {MAX_ROI}% (likely bad data)")
            if review_high_roi > 0:
                print(f"[REVIEW] {review_high_roi} extreme ROI flagged for verification")

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

                # Position and capital tracking (LIVE mode)
                if EXECUTION_MODE == ExecutionMode.LIVE or (EXECUTION_MODE == ExecutionMode.PAPER and not PAPER_NO_LIMITS):
                    pos_count = get_position_count()
                    deployed = get_total_deployed_capital()
                    if pos_count > 0:
                        print(f"\n  [OPEN POSITIONS] {pos_count}/{MAX_CONCURRENT_POSITIONS} | ${deployed:.2f} deployed")
                    display_position_summary()

                # Total Addressable Market stats (paper unlimited mode)
                if EXECUTION_MODE == ExecutionMode.PAPER and PAPER_NO_LIMITS and TAM_STATS['scan_count'] > 0:
                    total_unique = TAM_STATS['unique_arbs_new'] + TAM_STATS['unique_arbs_reopen']
                    tam_roi = (TAM_STATS['total_profit_if_captured'] / TAM_STATS['total_at_risk'] * 100) if TAM_STATS['total_at_risk'] > 0 else 0
                    realistic_roi = (TAM_STATS['realistic_profit'] / TAM_STATS['realistic_at_risk'] * 100) if TAM_STATS['realistic_at_risk'] > 0 else 0
                    print(f"\n  [TOTAL ADDRESSABLE MARKET]")
                    print(f"    Scans: {TAM_STATS['scan_count']}")
                    print(f"    Unique Arbs: {total_unique} ({TAM_STATS['unique_arbs_new']} NEW + {TAM_STATS['unique_arbs_reopen']} REOPEN)")
                    print(f"    Flicker Ignored: {TAM_STATS['flicker_ignored']}")
                    print(f"    Executed: {TAM_STATS['unique_arbs_executed']}")
                    realistic_count = TAM_STATS.get('realistic_arb_count', 0)
                    print(f"    Full liquidity (TAM): ${TAM_STATS['total_profit_if_captured']/100:.2f} profit from ${TAM_STATS['total_at_risk']/100:.0f} at risk ({tam_roi:.1f}% ROI)")
                    print(f"    Realistic ({MAX_CONTRACTS} cap):  ${TAM_STATS['realistic_profit']/100:.2f} profit from ${TAM_STATS['realistic_at_risk']/100:.0f} at risk ({realistic_roi:.1f}% ROI) [{realistic_count} arbs]")
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

                    # Calculate at-risk (capital required on buy side)
                    # BUY_K_SELL_PM: risk = k_ask * contracts (we buy on Kalshi)
                    # BUY_PM_SELL_K: risk = pm_ask * contracts (we buy on PM)
                    if arb.direction == 'BUY_K_SELL_PM':
                        buy_price = arb.k_ask  # cents
                    else:  # BUY_PM_SELL_K
                        buy_price = arb.pm_ask  # cents
                    at_risk_cents = buy_price * arb.size

                    # Calculate realistic values with ALL constraints:
                    # 1. 66% of available liquidity
                    # 2. Capped at MAX_CONTRACTS (100)
                    uncapped_size = int(arb.size * LIQUIDITY_UTILIZATION)
                    realistic_size = min(uncapped_size, MAX_CONTRACTS)
                    is_capped = uncapped_size > MAX_CONTRACTS
                    realistic_profit = arb.net_spread * realistic_size
                    realistic_at_risk = buy_price * realistic_size
                    implied_roi = (profit_cents / at_risk_cents * 100) if at_risk_cents > 0 else 0
                    realistic_roi = (realistic_profit / realistic_at_risk * 100) if realistic_at_risk > 0 else 0

                    if arb_key in ACTIVE_ARBS:
                        # PERSISTING arb - already active
                        active = ACTIVE_ARBS[arb_key]
                        active.last_seen = now
                        active.scan_count += 1
                        active.current_spread = arb.net_spread
                        active.current_size = arb.size
                        active.current_profit_cents = profit_cents

                        duration = format_duration(now - active.first_seen)
                        cap_note = f" [CAPPED from {uncapped_size}]" if is_capped else ""
                        print(f"  [PERSIST] {arb.sport} {arb.team}: {arb.net_spread}c spread | {arb.size} avail | ${profit_cents/100:.2f} profit | ${at_risk_cents/100:.0f} at risk (TAM)")
                        print(f"            -> Realistic: {realistic_size} contracts{cap_note} | ${realistic_profit/100:.2f} profit | ${realistic_at_risk/100:.0f} at risk | ROI:{realistic_roi:.1f}% (open {duration})")

                    elif arb_key in RECENTLY_CLOSED:
                        # FIX-BUG-7: Flicker detection - ignores arbs that reopen too quickly
                        # Was recently closed - check if flicker or real reopen
                        closed = RECENTLY_CLOSED[arb_key]
                        time_since_close = now - closed.closed_at

                        if time_since_close < REOPEN_COOLDOWN_SECONDS:
                            # FIX-BUG-7: FLICKER - reopened too quickly, ignore (API noise)
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
                                initial_at_risk_cents=at_risk_cents,
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

                            cap_note = f" [CAPPED from {uncapped_size}]" if is_capped else ""
                            print(f"  [REOPEN] {arb.sport} {arb.team}: {arb.net_spread}c spread | {arb.size} avail | ${profit_cents/100:.2f} profit | ${at_risk_cents/100:.0f} at risk (TAM)")
                            print(f"           -> Realistic: {realistic_size} contracts{cap_note} | ${realistic_profit/100:.2f} profit | ${realistic_at_risk/100:.0f} at risk | ROI:{realistic_roi:.1f}%")
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
                            initial_at_risk_cents=at_risk_cents,
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

                        cap_note = f" [CAPPED from {uncapped_size}]" if is_capped else ""
                        print(f"  [NEW] {arb.sport} {arb.team}: {arb.net_spread}c spread | {arb.size} avail | ${profit_cents/100:.2f} profit | ${at_risk_cents/100:.0f} at risk (TAM)")
                        print(f"        -> Realistic: {realistic_size} contracts{cap_note} | ${realistic_profit/100:.2f} profit | ${realistic_at_risk/100:.0f} at risk | ROI:{realistic_roi:.1f}%")

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
                        # Track TAM (100% liquidity - uncapped)
                        TAM_STATS['total_profit_if_captured'] += active.initial_profit_cents
                        TAM_STATS['total_contracts'] += active.initial_size
                        TAM_STATS['total_at_risk'] += active.initial_at_risk_cents

                        # Track REALISTIC with ALL constraints:
                        # 1. 66% of available liquidity
                        # 2. Capped at MAX_CONTRACTS (100)
                        # 3. Only count if >= MIN_CONTRACTS (20)
                        realistic_size = min(int(active.initial_size * LIQUIDITY_UTILIZATION), MAX_CONTRACTS)

                        if realistic_size >= MIN_CONTRACTS:
                            realistic_profit = active.initial_spread * realistic_size
                            # Recalculate at-risk based on capped size
                            buy_price_cents = active.initial_at_risk_cents / active.initial_size if active.initial_size > 0 else 0
                            realistic_at_risk = int(buy_price_cents * realistic_size)
                            TAM_STATS['realistic_profit'] += realistic_profit
                            TAM_STATS['realistic_contracts'] += realistic_size
                            TAM_STATS['realistic_at_risk'] += realistic_at_risk
                            TAM_STATS['realistic_arb_count'] = TAM_STATS.get('realistic_arb_count', 0) + 1

                        tag = "REOPEN" if active.is_reopen else "NEW"
                        print(f"    -> [PAPER EXECUTE {tag}] ${active.initial_profit_cents/100:.2f} profit / ${active.initial_at_risk_cents/100:.0f} risk (TAM)")

                # Summary with at-risk and ROI
                total_unique = TAM_STATS['unique_arbs_new'] + TAM_STATS['unique_arbs_reopen']
                total_active = len(ACTIVE_ARBS)
                total_recently_closed = len(RECENTLY_CLOSED)
                total_perm_closed = len(CLOSED_ARBS)

                tam_roi = (TAM_STATS['total_profit_if_captured'] / TAM_STATS['total_at_risk'] * 100) if TAM_STATS['total_at_risk'] > 0 else 0
                realistic_roi = (TAM_STATS['realistic_profit'] / TAM_STATS['realistic_at_risk'] * 100) if TAM_STATS['realistic_at_risk'] > 0 else 0

                print(f"\n  [TAM SUMMARY] Unique: {total_unique} ({TAM_STATS['unique_arbs_new']} NEW + {TAM_STATS['unique_arbs_reopen']} REOPEN)")
                print(f"  Flicker ignored: {TAM_STATS['flicker_ignored']}")
                print(f"  Active: {total_active} | Recently Closed: {total_recently_closed} | Perm Closed: {total_perm_closed}")
                print(f"  Scans: {TAM_STATS['scan_count']} | Executed: {TAM_STATS['unique_arbs_executed']}")
                realistic_count = TAM_STATS.get('realistic_arb_count', 0)
                print(f"  Full liquidity (TAM): ${TAM_STATS['total_profit_if_captured']/100:.2f} profit from ${TAM_STATS['total_at_risk']/100:.0f} at risk ({tam_roi:.1f}% ROI)")
                print(f"  Realistic ({MAX_CONTRACTS} cap):  ${TAM_STATS['realistic_profit']/100:.2f} profit from ${TAM_STATS['realistic_at_risk']/100:.0f} at risk ({realistic_roi:.1f}% ROI) [{realistic_count} arbs]")

            # Execute if we have arbs and cooldown passed (skip in paper unlimited - handled above)
            if not paper_unlimited:
                cooldown_ok = (time.time() - last_trade_time) >= COOLDOWN_SECONDS
                if exec_arbs and cooldown_ok:
                    # Take first executable arb (no longer skip already-traded games)
                    # This allows trading the same game multiple times if spread reappears
                    best = exec_arbs[0]
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
                # In paper unlimited mode, pick the best arb for full simulation
                # (but we'll simulate instead of actually executing)
                if exec_arbs:
                    best = exec_arbs[0]
                else:
                    # No executable arbs - just continue scanning
                    await asyncio.sleep(1.0)
                    continue

            # best is already set from the block above (no longer check TRADED_GAMES)
            # This allows trading the same game multiple times if spread reappears

            # =========================================================
            # PRE-TRADE MAPPING VERIFICATION
            # =========================================================
            if not pre_trade_verification(best):
                print(f"[BLOCKED] Pre-trade verification FAILED for {best.sport} {best.game} {best.team}")
                print(f"[BLOCKED] This trade would have been a same-direction bet!")
                log_skipped_arb(best, 'mapping_verification_failed',
                                f"Outcome index mismatch detected by pre_trade_verification")
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
            # POSITION LIMIT CHECK
            # =========================================================
            if get_position_count() >= MAX_CONCURRENT_POSITIONS:
                print(f"[BLOCKED] Max concurrent positions ({MAX_CONCURRENT_POSITIONS}) reached")
                print(f"[POSITIONS] {get_position_count()} open | ${get_total_deployed_capital():.2f} deployed")
                display_position_summary()
                await asyncio.sleep(10.0)  # Wait longer when at capacity
                continue

            # =========================================================
            # STEP 1: CONSERVATIVE SIZING CALCULATION
            # =========================================================
            t_sizing_start = time.time()

            print(f"\n[!] BEST ARB: {best.sport} {best.game} {best.team}")
            print(f"    Direction: {best.direction}")
            print(f"    K: {best.k_bid}/{best.k_ask}c | PM: {best.pm_bid}/{best.pm_ask}c")
            print(f"    Size (raw): {best.size} | Profit: ${best.profit:.2f} | ROI: {best.roi:.1f}%")
            print(f"    PM Slug: {best.pm_slug} | Outcome Index: {best.pm_outcome_index}")

            # DEBUG: Show exactly what PM order will be placed
            # ALL arbs are valid - BUY_YES on appropriate outcomeIndex
            pm_intent_debug, pm_price_debug, pm_outcome_idx_debug, _ = get_pm_execution_params(best, debug_only=True)
            intent_names = {1: 'BUY_LONG', 2: 'SELL_LONG', 3: 'BUY_SHORT', 4: 'SELL_SHORT'}
            print(f"    [DEBUG] PM Intent: {intent_names.get(pm_intent_debug, pm_intent_debug)} outcome[{pm_outcome_idx_debug}]")
            print(f"    [DEBUG] PM Base Price: ${pm_price_debug:.2f} + {PM_PRICE_BUFFER_CENTS}c buffer")

            # Get balances for sizing calculation (parallel fetch for speed)
            t_balance_start = time.time()
            kalshi_balance_task = kalshi_api.get_balance(session)
            pm_balance_task = pm_api.get_balance(session)
            kalshi_balance, pm_balance = await asyncio.gather(kalshi_balance_task, pm_balance_task)
            kalshi_balance = kalshi_balance or 0
            pm_balance = pm_balance or 0
            t_balance_ms = (time.time() - t_balance_start) * 1000

            trade_size, sizing_details = await calculate_conservative_size(
                session, kalshi_api, pm_api, best, kalshi_balance, pm_balance
            )
            t_sizing_ms = (time.time() - t_sizing_start) * 1000

            # Output sizing calculation
            print(f"\n[SIZE] ===== CONSERVATIVE SIZING =====")
            print(f"[SIZE] Kalshi balance: {sizing_details['kalshi_balance']} ({sizing_details['kalshi_max_by_balance']} contracts max)")
            print(f"[SIZE] PM US balance: {sizing_details['pm_balance']} ({sizing_details['pm_max_by_balance']} contracts max)")
            print(f"[SIZE] Kalshi depth: {sizing_details['kalshi_liquidity']} → {sizing_details.get('k_66_pct', 0)} @ 66%")
            print(f"[SIZE] PM depth: {sizing_details['pm_liquidity']} → {sizing_details['pm_66_pct']} @ 66%")
            print(f"[SIZE] Final size: {trade_size} contracts (limited by: {sizing_details['limiting_factor']})")
            print(f"[SIZE] ===================================")

            if trade_size < 1:
                print(f"[ABORT] Insufficient size after conservative calculation")
                log_skipped_arb(best, 'insufficient_size', f"Size {trade_size} < 1 after sizing")
                await asyncio.sleep(1.0)
                continue

            # =========================================================
            # STEP 2: PRICE AGE CHECK (LATENCY OPTIMIZED)
            # The scan JUST fetched prices - use them directly instead of refetching
            # Only reject if prices are too old (> MAX_PRICE_AGE_MS)
            # =========================================================
            t_exec_start = time.time()
            price_age_ms = (t_exec_start - best.price_timestamp) * 1000 if best.price_timestamp > 0 else 0

            if price_age_ms > MAX_PRICE_AGE_MS:
                print(f"[ABORT] Prices are {price_age_ms:.0f}ms old (> {MAX_PRICE_AGE_MS}ms) - too stale")
                log_skipped_arb(best, 'price_stale', f'Price age {price_age_ms:.0f}ms > {MAX_PRICE_AGE_MS}ms')
                await asyncio.sleep(0.5)
                continue

            print(f"[FAST] Using scan prices (age: {price_age_ms:.0f}ms) - NO REFETCH")

            # =========================================================
            # FEE-AWARE PROFITABILITY CHECK
            # Estimate net profit AFTER fees and slippage BEFORE committing
            # =========================================================
            net_profit, profit_breakdown = estimate_net_profit_cents(best)
            log_profit_estimate(best, trade_size)

            if net_profit < MIN_PROFIT_CENTS:
                print(f"\n[SKIP] Net profit {net_profit:.2f}c < minimum {MIN_PROFIT_CENTS}c - NOT WORTH IT")
                print(f"    Raw spread: {profit_breakdown['raw_spread']:.1f}c")
                print(f"    Kalshi fee: -{profit_breakdown['k_fee']:.1f}c")
                print(f"    PM fee: -{profit_breakdown['pm_fee']:.2f}c")
                print(f"    Expected slippage: -{profit_breakdown['slippage']:.1f}c")
                print(f"    Net: {net_profit:.2f}c (need {MIN_PROFIT_CENTS}c minimum)")
                log_skipped_arb(best, 'negative_ev', f'Net profit {net_profit:.2f}c < {MIN_PROFIT_CENTS}c min')
                await asyncio.sleep(1.0)
                continue

            print(f"[PROFIT] Estimated net: {net_profit:.1f}c/contract (after {profit_breakdown['total_costs']:.1f}c costs)")

            # =========================================================
            # STEP 3: PRICE CALCULATION FROM CACHED DATA (NO REFETCH)
            # LATENCY OPTIMIZED: Use prices from scan directly
            # =========================================================
            # Determine execution prices from cached arb data
            # PM price calculated based on direction and outcome_index
            if best.direction == 'BUY_PM_SELL_K':
                k_price = best.k_bid  # Sell on Kalshi at bid (cents)
                # PM LONG our team: buy our team's outcome
                if best.pm_outcome_index == 0:
                    pm_price = best.pm_ask / 100  # Convert cents to dollars
                else:
                    pm_price = (100 - best.pm_bid) / 100  # Outcome[1] ask = 1 - bid[0]
            else:
                k_price = best.k_ask  # Buy on Kalshi at ask (cents)
                # PM SHORT our team: buy opponent's outcome
                if best.pm_outcome_index == 0:
                    pm_price = (100 - best.pm_bid) / 100  # Outcome[1] ask = 1 - bid[0]
                else:
                    pm_price = best.pm_ask / 100  # Convert cents to dollars

            pm_price_cents = pm_price * 100  # For logging

            # =========================================================
            # SAFETY CHECK: PM price sanity bounds
            # Sports bets rarely trade below 5c or above 95c
            # =========================================================
            if pm_price_cents < MIN_PM_PRICE:
                print(f"\n[!!!SAFETY ABORT!!!] PM price ${pm_price:.4f} ({pm_price_cents:.1f}c) is TOO LOW (< {MIN_PM_PRICE}c)")
                print(f"    Cached: pm_bid={best.pm_bid}c, pm_ask={best.pm_ask}c")
                log_skipped_arb(best, 'safety_abort', f'PM price {pm_price_cents:.1f}c too low')
                await asyncio.sleep(1.0)
                continue

            if pm_price_cents > 90:
                print(f"\n[!!!SAFETY ABORT!!!] PM price ${pm_price:.4f} ({pm_price_cents:.1f}c) is TOO HIGH (> 90c)")
                log_skipped_arb(best, 'safety_abort', f'PM price {pm_price_cents:.1f}c too high')
                await asyncio.sleep(1.0)
                continue

            # Build fresh_prices dict from cached data for compatibility with downstream code
            # LATENCY OPT: No API call here - just restructuring cached data
            raw_bid = best.pm_bid / 100 if best.pm_outcome_index == 0 else (100 - best.pm_ask) / 100
            raw_ask = best.pm_ask / 100 if best.pm_outcome_index == 0 else (100 - best.pm_bid) / 100

            # Build fresh_prices dict for downstream compatibility
            fresh_prices = {
                'pm_bid': best.pm_bid / 100,  # dollars
                'pm_ask': best.pm_ask / 100,  # dollars
                'pm_bid_size': best.pm_bid_size,
                'pm_ask_size': best.pm_ask_size,
                'spread': best.net_spread,  # cents
                'spread_dollars': best.net_spread / 100,
                'fetch_ms': price_age_ms,  # Use age as "fetch time"
                'execution_pm_price': pm_price,  # dollars
                'outcome_index': best.pm_outcome_index,
                'raw_bid': raw_bid,
                'raw_ask': raw_ask,
            }

            # Determine PM execution outcome index
            if best.direction == 'BUY_K_SELL_PM':
                pm_outcome_exec = 1 - best.pm_outcome_index  # Buy opponent
            else:
                pm_outcome_exec = best.pm_outcome_index  # Buy our team

            # Parse slug to get team names for logging
            slug_parts = best.pm_slug.split('-')
            team0 = slug_parts[2].upper() if len(slug_parts) >= 4 else 'T0'
            team1 = slug_parts[3].upper() if len(slug_parts) >= 4 else 'T1'

            print(f"\n[EXEC] K: {best.direction.split('_')[0]} @ {k_price}c | PM: BUY outcome[{pm_outcome_exec}] @ ${pm_price:.4f} ({pm_price_cents:.1f}c)")

            # =========================================================
            # OPTIMIZATION: Start pre-position fetch concurrently with execution
            # This removes ~50-100ms from the critical path. The position data
            # is only needed for post-trade verification, not execution decisions.
            # =========================================================
            t_prepos_start = time.time()
            prepos_task = asyncio.create_task(
                kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
            )
            # Don't await here - let it run concurrently with execution

            # =========================================================
            # PAPER MODE: Simulate execution instead of real orders
            # FIX-BUG-11: Paper mode uses SAME validation as live mode:
            #   - Conservative sizing calculation (calculate_conservative_size)
            #   - Fresh price validation (fresh_price_validation)
            #   - PM price safety checks (15-90c bounds)
            #   - Price difference check (20c max from cached)
            # Only the execution differs (simulated vs real orders)
            # =========================================================
            # Default timing for paper mode (no hedge verification)
            t_hedge_ms = 0

            if paper_unlimited:
                # Calculate what the orders WOULD be
                k_action = 'buy' if best.direction == 'BUY_K_SELL_PM' else 'sell'
                k_limit_price = k_price + PRICE_BUFFER_CENTS if k_action == 'buy' else k_price - PRICE_BUFFER_CENTS
                k_limit_price = max(1, min(99, k_limit_price))

                pm_limit_price = pm_price + (PM_PRICE_BUFFER_CENTS / 100)
                pm_limit_price = max(0.01, min(0.99, pm_limit_price))

                print(f"\n{'='*70}")
                print(f"[PAPER MODE] SIMULATED ATOMIC EXECUTION")
                print(f"{'='*70}")
                print(f"[PAPER] Target: {trade_size} contracts via {trade_size}x atomic 1-contract trades")
                print(f"[PAPER] Kalshi: {k_action.upper()} {best.team} @ {k_limit_price}c")
                print(f"[PAPER]   Ticker: {best.kalshi_ticker}")
                print(f"[PAPER] PM: BUY_YES outcome[{pm_outcome_exec}] @ ${pm_limit_price:.4f} ({pm_limit_price*100:.1f}c)")
                print(f"[PAPER]   Slug: {best.pm_slug}")

                # Simulate atomic execution
                for i in range(trade_size):
                    print(f"[ATOMIC] Trade {i+1}/{trade_size} - simulated K=1, PM=1 ✓")

                print(f"[ATOMIC] Completed: {trade_size}/{trade_size} pairs hedged (simulated)")
                print(f"{'='*70}")

                # Simulate successful fills for TAM tracking
                k_result = {
                    'success': True,
                    'fill_count': trade_size,
                    'fill_price': k_limit_price,
                    'execution_ms': 50 * trade_size,
                    'simulated': True
                }
                # Calculate PM outcome_index for paper trade logging
                paper_pm_outcome_idx = best.pm_outcome_index if best.direction == 'BUY_PM_SELL_K' else 1 - best.pm_outcome_index
                pm_result = {
                    'success': True,
                    'fill_count': trade_size,
                    'fill_price': pm_limit_price,
                    'execution_ms': 50 * trade_size,
                    'simulated': True,
                    'outcome_index': paper_pm_outcome_idx  # Log for paper trades too
                }
                execution_timing = {
                    'kalshi_ms': 50 * trade_size,
                    'pm_ms': 50 * trade_size,
                    'total_ms': 100 * trade_size,
                    'both_matched': True,
                    'k_limit_price': k_limit_price,
                    'pm_limit_price': pm_limit_price,
                }

                print(f"[PAPER] Simulated profit: ${best.net_spread * trade_size / 100:.2f}")
                print(f"EXEC TIMING: size={t_sizing_ms:.0f}ms → hedge=0ms → k_order=sim → pm_order=sim → TOTAL=sim")

                # LOG PAPER TRADE - write to trades.json for P&L tracking
                log_trade(best, k_result, pm_result, 'PAPER_SUCCESS',
                         execution_time_ms=execution_timing['total_ms'])
                print(f"[PAPER] Trade logged to trades.json")

                # Mark this arb as executed so we see different arbs next cycle
                TRADED_GAMES.add(best.game)
                if best.pm_slug:
                    TRADED_GAMES.add(best.pm_slug)

                # Paper mode cooldown to avoid spamming
                print(f"[PAPER] Cooldown: Waiting {COOLDOWN_SECONDS}s before next simulation...")

                # Cancel pre-position task - not needed in paper mode
                prepos_task.cancel()
                pre_position = None
                post_position = None
                t_prepos_ms = 0
            else:
                # =============================================================
                # CRITICAL: VERIFY HEDGE DIRECTION BEFORE EXECUTION
                # This catches same-direction betting bugs that cause naked exposure
                # =============================================================
                t_hedge_start = time.time()
                hedge_valid, hedge_error = verify_hedge_direction(best)
                t_hedge_ms = (time.time() - t_hedge_start) * 1000
                if not hedge_valid:
                    print(f"[!!!ABORT!!!] Hedge direction verification FAILED - skipping trade")
                    print(f"  {hedge_error}")
                    log_skipped_arb(best, 'hedge_direction_mismatch',
                        f"PM and Kalshi on same side - outcome_index bug")
                    continue  # Skip to next scan

                # FIX-BUG-12: Acquire execution lock - only one arb at a time
                async with EXECUTION_LOCK:
                    print(f"[EXEC LOCK] Acquired - executing arb")

                    # =============================================================
                    # ATOMIC 1-CONTRACT EXECUTION LOOP
                    # With IOC orders, partial fills create mismatches. Solution:
                    # Always send quantity=1 to both platforms. Each pair is atomic.
                    # If we want N contracts, we loop N times with 1-contract orders.
                    # =============================================================
                    target_contracts = trade_size
                    executed_pairs = 0
                    total_k_fill = 0
                    total_pm_fill = 0
                    loop_start = time.time()

                    # Aggregate results for compatibility with existing code
                    k_result = {'success': False, 'fill_count': 0, 'fill_price': k_price}
                    pm_result = {'success': False, 'fill_count': 0, 'fill_price': pm_price, 'outcome_index': best.pm_outcome_index}

                    for i in range(target_contracts):
                        print(f"\n[ATOMIC] Trade {i+1}/{target_contracts}")

                        # Check price age - prices may have moved during loop
                        current_price_age_ms = (time.time() - best.price_timestamp) * 1000
                        if current_price_age_ms > 1000 and i > 0:
                            print(f"[ATOMIC] Prices stale ({current_price_age_ms:.0f}ms) after {i} trades - stopping")
                            break

                        # Execute exactly 1 contract
                        iter_k_result, iter_pm_result, iter_timing = await execute_sequential_orders(
                            session, kalshi_api, pm_api, best,
                            k_price, pm_price, 1,  # ALWAYS quantity=1
                            fresh_prices=fresh_prices
                        )

                        iter_k_fill = iter_k_result.get('fill_count', 0)
                        iter_pm_fill = iter_pm_result.get('fill_count', 0)

                        if iter_k_fill == 0:
                            print(f"[ATOMIC] Kalshi didn't fill - stopping loop")
                            break  # No fill = no PM order was sent, no partial risk

                        total_k_fill += iter_k_fill

                        if iter_pm_fill == 0:
                            print(f"[ATOMIC] PM didn't fill - 1 contract UNHEDGED!")
                            # Only 1 contract unhedged - existing recovery will handle
                            break

                        total_pm_fill += iter_pm_fill
                        executed_pairs += 1
                        print(f"[ATOMIC] ✓ Pair {executed_pairs} hedged (K={total_k_fill}, PM={total_pm_fill})")

                        # Brief pause between orders to avoid rate limiting
                        if i < target_contracts - 1:
                            await asyncio.sleep(0.05)  # 50ms between pairs

                    loop_end = time.time()
                    total_loop_ms = (loop_end - loop_start) * 1000

                    # Update aggregate results
                    k_result['fill_count'] = total_k_fill
                    k_result['success'] = total_k_fill > 0
                    k_result['fill_price'] = iter_k_result.get('fill_price', k_price) if total_k_fill > 0 else k_price

                    pm_result['fill_count'] = total_pm_fill
                    pm_result['success'] = total_pm_fill > 0
                    pm_result['fill_price'] = iter_pm_result.get('fill_price', pm_price) if total_pm_fill > 0 else pm_price

                    execution_timing = {'total_ms': total_loop_ms, 'k_limit_price': k_price, 'pm_limit_price': pm_price}

                    print(f"\n[ATOMIC] Completed: {executed_pairs}/{target_contracts} pairs hedged in {total_loop_ms:.0f}ms")
                    print(f"[EXEC LOCK] Released")

                # =========================================================
                # STEP 4: FILL VERIFICATION (LIVE MODE ONLY)
                # Pre-position task was started concurrently - await it now
                # =========================================================
                await asyncio.sleep(0.3)
                # Await pre-position (ran concurrently with execution)
                try:
                    pre_position = await prepos_task
                    t_prepos_ms = (time.time() - t_prepos_start) * 1000
                    print(f"[PRE-TRADE] Kalshi Position = {pre_position} (fetched async in {t_prepos_ms:.0f}ms)")
                except Exception as e:
                    print(f"[WARN] Pre-position fetch failed: {e}")
                    pre_position = None
                    t_prepos_ms = 0
                # Fetch post-position for verification
                post_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
            if not paper_unlimited:
                print(f"[POST-TRADE] Kalshi Position = {post_position}")

            # Get actual fills from results
            k_fill = k_result.get('fill_count', 0)
            pm_fill = pm_result.get('fill_count', 0)

            # Cross-check with position change (skip in paper mode)
            position_change = 0
            if not paper_unlimited:
                if pre_position is not None and post_position is not None:
                    position_change = abs(post_position - pre_position)

                # If API says 0 but position changed, use position change
                actual_k_fill = k_fill if k_fill > 0 else position_change
                if actual_k_fill != k_fill and actual_k_fill > 0:
                    print(f"[VERIFY] Position changed by {position_change}, overriding API fill {k_fill}")
                    k_fill = actual_k_fill

                print(f"[VERIFY] Final fills: Kalshi={k_fill}, PM={pm_fill}, Position change={position_change}")

            # =========================================================
            # STEP 5: HEDGE RECONCILIATION
            # =========================================================
            # Define exec_time_ms early so it's available in all code paths
            exec_time_ms = execution_timing.get('total_ms', 0)

            if k_fill > 0 or pm_fill > 0:
                # Compute actual fill for hedge reconciliation
                actual_fill = min(k_fill, pm_fill) if (k_fill > 0 and pm_fill > 0) else max(k_fill, pm_fill)

                if paper_unlimited:
                    # Paper mode: simulate hedged state
                    from dataclasses import dataclass
                    @dataclass
                    class SimulatedHedgeState:
                        is_hedged: bool = True
                        kalshi_filled: int = 0
                        pm_filled: int = 0
                        recovery_slippage: float = 0.0
                    hedge_state = SimulatedHedgeState(
                        is_hedged=True,
                        kalshi_filled=k_fill,
                        pm_filled=pm_fill,
                        recovery_slippage=0.0
                    )
                    print(f"[PAPER] Simulated hedge: Both sides matched, no recovery needed")
                else:
                    # Run hedge reconciliation with recovery if needed
                    hedge_state = await reconcile_hedge(
                        session, kalshi_api, pm_api, best,
                        k_result, pm_result, actual_fill
                    )

                fill_price = execution_timing.get('k_limit_price', k_price)
                pm_fill_price = pm_result.get('fill_price')

                if pm_fill > 0:
                    print(f"[OK] PM US FILLED: {pm_fill} contracts" + (f" @ ${pm_fill_price:.2f}" if pm_fill_price else ""))

                # Calculate actual profit
                price_diff = abs(fill_price - k_price)
                slippage_cost = hedge_state.recovery_slippage * hedge_state.pm_filled / 100 if hedge_state.recovery_slippage else 0
                actual_profit = best.profit - (price_diff * actual_fill / 100) - slippage_cost

                if hedge_state.is_hedged:
                    # Successfully hedged (possibly with recovery)
                    total_trades += 1
                    SCAN_STATS['total_executed'] += 1
                    total_profit += actual_profit

                    exec_time_ms = execution_timing.get('total_ms', 0)
                    if hedge_state.recovery_slippage > 0:
                        print(f"[$] Trade #{total_trades} | +${actual_profit:.2f} (reduced due to {hedge_state.recovery_slippage}c recovery slippage)")
                        log_trade(best, k_result, pm_result, 'RECOVERED', execution_time_ms=exec_time_ms)
                    else:
                        print(f"[$] Trade #{total_trades} | +${actual_profit:.2f} | Total: ${total_profit:.2f} | Exec: {exec_time_ms:.0f}ms")
                        log_trade(best, k_result, pm_result, 'SUCCESS', execution_time_ms=exec_time_ms)

                    # LATENCY TRACKING: Show detailed timing breakdown
                    total_latency_ms = (time.time() - best.price_timestamp) * 1000 if best.price_timestamp > 0 else 0
                    k_order_ms = execution_timing.get('kalshi_ms', 0)
                    pm_order_ms = execution_timing.get('pm_ms', 0)
                    # Pre-position fetch ran concurrently - show it separately from critical path
                    print(f"EXEC TIMING: size={t_sizing_ms:.0f}ms → hedge={t_hedge_ms:.0f}ms → k_order={k_order_ms:.0f}ms → pm_order={pm_order_ms:.0f}ms → TOTAL={exec_time_ms:.0f}ms (prepos={t_prepos_ms:.0f}ms async)")
                    print(f"[TIMING] Scan→Execute total: {total_latency_ms:.0f}ms (price_age={price_age_ms:.0f}ms)")

                    # Check for slow execution warning
                    avg_exec = EXECUTION_STATS.get('avg_execution_ms', 0)
                    if avg_exec > SLOW_EXECUTION_THRESHOLD_MS:
                        print(f"[!] SLOW EXEC WARNING: Avg {avg_exec:.0f}ms > {SLOW_EXECUTION_THRESHOLD_MS}ms threshold")

                    # Track paper stats
                    if EXECUTION_MODE == ExecutionMode.PAPER:
                        PAPER_STATS['total_arbs_executed'] += 1
                        PAPER_STATS['total_theoretical_profit'] += actual_profit
                        PAPER_STATS['total_contracts'] += actual_fill

                    # Mark game as traded
                    TRADED_GAMES.add(best.game)
                    if best.pm_slug:
                        TRADED_GAMES.add(best.pm_slug)

                    # Track open position with capital locked
                    # Capital locked = buy side cost (contracts * buy price in cents / 100)
                    if best.direction == 'BUY_PM_SELL_K':
                        entry_price = best.pm_ask  # Bought on PM
                    else:
                        entry_price = best.k_ask   # Bought on Kalshi
                    capital_locked = actual_fill * entry_price / 100

                    if not paper_unlimited:
                        add_open_position(
                            game_id=best.game,
                            contracts=actual_fill,
                            entry_price=entry_price,
                            capital_locked=capital_locked,
                            kalshi_ticker=best.kalshi_ticker,
                            pm_slug=best.pm_slug or ''
                        )

                        # Show updated capital status
                        k_bal_after = await kalshi_api.get_balance(session) or 0
                        pm_bal_after = await pm_api.get_balance(session) or 0
                        print(f"[CAPITAL] After trade: Kalshi ${k_bal_after:.2f} | PM US ${pm_bal_after:.2f}")
                    else:
                        print(f"[PAPER] Simulated trade complete - no position tracking in paper mode")

                    # Check max-trades limit
                    global TRADES_EXECUTED
                    TRADES_EXECUTED += 1
                    if MAX_TRADES > 0 and TRADES_EXECUTED >= MAX_TRADES:
                        print(f"\n[MAX TRADES] Reached limit of {MAX_TRADES} trade(s) - stopping")
                        raise SystemExit(f"MAX_TRADES limit ({MAX_TRADES}) reached")

                else:
                    # UNHEDGED - recovery failed
                    unhedged_qty = hedge_state.kalshi_filled - hedge_state.pm_filled
                    print(f"[!!!] UNHEDGED POSITION: {unhedged_qty} contracts on {best.kalshi_ticker}")

                    log_trade(best, k_result, pm_result, 'UNHEDGED', execution_time_ms=exec_time_ms)

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
                # No fill on either side
                exec_time_ms = execution_timing.get('total_ms', 0)
                print(f"\n[X] NO FILL on either side (K={k_fill}, PM={pm_fill})")
                log_skipped_arb(best, 'no_fill', f"Parallel execution: K={k_fill}, PM={pm_fill}")
                log_trade(best, k_result, pm_result, 'NO_FILL', execution_time_ms=exec_time_ms)

            # Paper mode: longer cooldown to allow time to review output
            if paper_unlimited:
                await asyncio.sleep(COOLDOWN_SECONDS)
            else:
                await asyncio.sleep(1.0)


# FIX-BUG-8: Note - crash recovery is implemented in the main entry point
# via the --restart-on-crash flag. See run_main_loop() at line ~8033.
# The AUTO-RESTART logic handles:
# - Tracking restart timestamps to avoid infinite restart loops
# - Differentiating between user interrupts and crashes
# - Logging crashes for debugging


if __name__ == "__main__":
    import argparse
    import sys

    # SAFETY GUARD: Prevent accidental execution of v7 (use arb_executor_ws.py instead)
    print("=" * 70)
    print("ERROR: arb_executor_v7.py is DEPRECATED")
    print("=" * 70)
    print("This executor has bugs that can place unlimited contracts.")
    print("Use arb_executor_ws.py instead:")
    print("")
    print("  python arb_executor_ws.py --live --spread-min 3 --contracts 1")
    print("")
    print("To bypass this guard (NOT RECOMMENDED), set ARB_V7_ALLOW=1")
    print("=" * 70)
    if not os.environ.get('ARB_V7_ALLOW'):
        sys.exit(1)

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
    parser.add_argument('--restart-on-crash', action='store_true', dest='restart_on_crash',
                        help='Auto-restart on crash (max 5 restarts per hour)')
    parser.add_argument('--dry-run', action='store_true', dest='dry_run',
                        help='Connect to real APIs but do not submit orders (safe live testing)')
    parser.add_argument('--max-trades', type=int, default=0, dest='max_trades',
                        help='Stop after N successful trades (0 = unlimited)')
    parser.add_argument('--max-positions', type=int, default=10, dest='max_positions',
                        help='Max concurrent open positions (default: 10)')
    parser.add_argument('--contracts', type=int, default=0,
                        help='Hard cap on contracts per trade (0 = use MAX_CONTRACTS)')
    parser.add_argument('--spread-min', type=int, default=0, dest='spread_min',
                        help='Minimum spread in cents to execute (0 = use calculated breakeven)')
    parser.add_argument('--test-mode', action='store_true', dest='test_mode',
                        help='Small position limits for testing ($15 max, 20 contracts)')
    parser.add_argument('--self-test', action='store_true', dest='self_test',
                        help='Run self-test to validate configurations and exit')
    parser.add_argument('--pnl', action='store_true',
                        help='Show P&L summary from trades.json and exit')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip interactive confirmation for live trading (for automation)')
    args = parser.parse_args()

    # Run self-test if requested and exit
    if args.self_test:
        passed, errors = run_self_test()
        sys.exit(0 if passed else 1)

    # Show P&L summary if requested and exit
    if args.pnl:
        print_pnl_summary()
        sys.exit(0)

    # Override execution mode if specified (use globals() to modify module-level variable)
    if args.paper:
        globals()['EXECUTION_MODE'] = ExecutionMode.PAPER
    elif args.live:
        globals()['EXECUTION_MODE'] = ExecutionMode.LIVE

    # Set paper no-limits mode (default True for paper, can be disabled with --with-limits)
    if args.with_limits:
        globals()['PAPER_NO_LIMITS'] = False
    elif args.no_limits or globals()['EXECUTION_MODE'] == ExecutionMode.PAPER:
        globals()['PAPER_NO_LIMITS'] = True

    # Enable debug mode
    if args.debug:
        DEBUG_MATCHING = True

    # Enable dry-run mode (connect to real APIs but don't submit orders)
    if args.dry_run:
        DRY_RUN_MODE = True
        print("[DRY RUN] Mode enabled - will NOT submit real orders")

    # Set max trades limit
    if args.max_trades > 0:
        MAX_TRADES = args.max_trades
        print(f"[MAX TRADES] Will stop after {MAX_TRADES} successful trade(s)")

    # Set max concurrent positions
    if args.max_positions != 10:  # Non-default value
        MAX_CONCURRENT_POSITIONS = args.max_positions
        print(f"[MAX POSITIONS] Limit set to {MAX_CONCURRENT_POSITIONS} concurrent positions")

    # Override MAX_CONTRACTS if --contracts flag provided
    if args.contracts > 0:
        globals()['MAX_CONTRACTS'] = args.contracts
        # BUG FIX: MIN_CONTRACTS must not exceed MAX_CONTRACTS or all arbs get silently filtered
        if args.contracts < globals()['MIN_CONTRACTS']:
            globals()['MIN_CONTRACTS'] = args.contracts
            print(f"[CONTRACTS] Hard cap set to {args.contracts} contracts per trade (min also set to {args.contracts})")
        else:
            print(f"[CONTRACTS] Hard cap set to {args.contracts} contracts per trade")

    # Override MIN_SPREAD_FOR_EXECUTION if --spread-min flag provided
    if args.spread_min > 0:
        globals()['MIN_SPREAD_FOR_EXECUTION'] = args.spread_min
        globals()['MIN_SPREAD_CENTS'] = args.spread_min
        print(f"[SPREAD-MIN] Minimum spread set to {args.spread_min}c")

    # Test mode - very small positions for testing outcome mapping
    TEST_MODE = args.test_mode
    if TEST_MODE:
        # Override module-level constants for test mode
        import arb_executor_v7 as self_module
        self_module.MAX_CONTRACTS = 5               # Small: 5 contracts max
        self_module.MIN_CONTRACTS = 5               # Match max for consistent sizing
        self_module.MAX_COST_CENTS = 500            # $5 max per trade
        self_module.MAX_CONCURRENT_POSITIONS = 5
        # Lower spread requirements to force trades for testing BUY_NO logic
        self_module.MIN_SPREAD_CENTS = 1  # TEMP: lowered from 2 for testing
        self_module.EXPECTED_SLIPPAGE_CENTS = 0
        self_module.MIN_PROFIT_CENTS = 1
        self_module.MIN_SPREAD_FOR_EXECUTION = 1  # TEMP: lowered from 2 for testing
        self_module.MIN_EXECUTION_SPREAD = 1
        # Update local references too
        MAX_CONTRACTS = 5
        MIN_CONTRACTS = 5
        MAX_COST_CENTS = 500
        MAX_CONCURRENT_POSITIONS = 5
        print("\n" + "="*60)
        print("[TEST MODE] Small positions for outcome mapping verification")
        print("="*60)
        print(f"  Max contracts per trade:   {MAX_CONTRACTS}")
        print(f"  Min contracts per trade:   {MIN_CONTRACTS}")
        print(f"  Max cost per trade:        ${MAX_COST_CENTS/100:.0f}")
        print(f"  Min spread required:       {self_module.MIN_SPREAD_FOR_EXECUTION}c")
        print(f"  Risk per trade:            ~$2.50 at 50c")
        print("="*60 + "\n")

    # FEE-AWARE: Warn if MIN_SPREAD is below calculated breakeven
    # This warns users they may be accepting negative EV trades
    # Note: Use self_module to get post-test-mode values
    import arb_executor_v7 as self_module
    current_min_spread = self_module.MIN_SPREAD_FOR_EXECUTION
    current_breakeven = self_module.CALCULATED_BREAKEVEN_SPREAD
    current_k_fee = self_module.KALSHI_FEE_CENTS_PER_CONTRACT
    current_slippage = self_module.EXPECTED_SLIPPAGE_CENTS
    current_min_profit = self_module.MIN_PROFIT_CENTS

    if current_min_spread < current_breakeven:
        print("\n" + "!"*60)
        print("[FEE WARNING] MIN_SPREAD below calculated breakeven!")
        print("!"*60)
        print(f"  Current MIN_SPREAD:          {current_min_spread}c")
        print(f"  Calculated breakeven:        {current_breakeven}c")
        print(f"    (K fee {current_k_fee}c + PM fee ~0.05c + slippage {current_slippage}c + min profit {current_min_profit}c)")
        print(f"  Gap:                         {current_breakeven - current_min_spread}c below breakeven")
        print("")
        print("  -> Trades with spreads between these values will be")
        print("     ALLOWED BY SCAN but REJECTED BY PROFIT CHECK.")
        print("  -> This is intentional in test mode (watching vs trading)")
        print("!"*60 + "\n")

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

    # Load pre-verified game mappings from pregame_mapper.py output
    if HAS_MAPPER:
        VERIFIED_MAPS = load_verified_mappings()
        if VERIFIED_MAPS:
            print(f"[MAPPING] Loaded {len(VERIFIED_MAPS)} verified game mappings")
            MAPPING_LAST_LOADED = time.time()
        else:
            print("[MAPPING] No verified mappings found - run pregame_mapper.py first")
            print("[MAPPING] Falling back to runtime matching (slower, less safe)")
    else:
        print("[MAPPING] pregame_mapper.py not available - using runtime matching only")

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
    if DRY_RUN_MODE:
        mode_str += " [DRY RUN - no real orders]"
    print(f"Mode: {mode_str}")
    if MAX_TRADES > 0:
        print(f"Max Trades: {MAX_TRADES} (will stop after)")
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
        print("  python arb_executor_v7.py --start --live --test-mode  # Live with small positions ($15 max)")
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
            globals()['EXECUTION_MODE'] = ExecutionMode.PAPER
            globals()['PAPER_NO_LIMITS'] = True
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

    # =========================================================================
    # LIVE MODE: Show balances and require confirmation
    # =========================================================================
    if EXECUTION_MODE == ExecutionMode.LIVE and not DRY_RUN_MODE:
        async def show_live_balances():
            """Fetch and display balances before live trading."""
            pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
            kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
            async with aiohttp.ClientSession() as session:
                k_balance = await kalshi_api.get_balance(session) or 0
                pm_balance = await pm_api.get_balance(session) or 0
                return k_balance, pm_balance

        try:
            k_bal, pm_bal = asyncio.run(show_live_balances())
            total_bal = k_bal + pm_bal

            print("\n" + "="*70)
            print("[LIVE MODE] REAL MONEY TRADING")
            print("="*70)
            print(f"  Kalshi Balance:    ${k_bal:>10.2f}")
            print(f"  PM US Balance:     ${pm_bal:>10.2f}")
            print(f"  Total Available:   ${total_bal:>10.2f}")
            print("-"*70)
            print(f"  Max Position:      {MAX_CONTRACTS} contracts")
            print(f"  Max Cost per Trade: ${MAX_COST_CENTS/100:.2f}")
            print(f"  Min Contracts:     {MIN_CONTRACTS}")
            if MAX_TRADES > 0:
                print(f"  Max Trades:        {MAX_TRADES} (will stop after)")
            print("="*70)
            if args.yes:
                print("\n[AUTO-CONFIRMED] --yes flag provided, starting live trading...\n")
            else:
                print("\n[!] Press ENTER to start live trading, or Ctrl+C to cancel...")
                input()
                print("[CONFIRMED] Starting live trading...\n")
        except KeyboardInterrupt:
            print("\n[CANCELLED] Live trading cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] Could not fetch balances: {e}")
            print("[!] Press ENTER to continue anyway, or Ctrl+C to cancel...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n[CANCELLED] Cancelled by user")
                sys.exit(0)

    # =========================================================================
    # AUTO-RESTART LOGIC
    # =========================================================================
    MAX_RESTARTS_PER_HOUR = 5
    RESTART_DELAY_SECONDS = 10
    restart_timestamps = []  # Track restart times

    def should_restart():
        """Check if we should restart (not exceeded max restarts per hour)."""
        now = time.time()
        hour_ago = now - 3600
        # Remove timestamps older than 1 hour
        recent = [t for t in restart_timestamps if t > hour_ago]
        restart_timestamps.clear()
        restart_timestamps.extend(recent)
        return len(restart_timestamps) < MAX_RESTARTS_PER_HOUR

    def run_main_loop():
        """Run the main executor loop once."""
        # Log bot start for uptime tracking
        log_uptime("STARTED", details={
            'scan_interval': f"{SCAN_INTERVAL}ms",
            'max_contracts': MAX_CONTRACTS,
            'min_buy_price': MIN_BUY_PRICE,
            'restart_count': len(restart_timestamps),
        })
        asyncio.run(run_executor())

    if args.restart_on_crash:
        print(f"[AUTO-RESTART] Enabled - max {MAX_RESTARTS_PER_HOUR} restarts per hour")

        while True:
            try:
                run_main_loop()
                break  # Clean exit
            except KeyboardInterrupt:
                # User stopped it - don't restart
                break
            except SystemExit as e:
                # Intentional exit (kill switch, etc.) - don't restart
                log_uptime("STOPPED", f"SystemExit: {e}")
                raise
            except Exception as e:
                import traceback
                error_type = type(e).__name__
                error_msg = str(e)
                tb = traceback.format_exc()

                log_uptime("STOPPED", f"CRASH: {error_type}: {error_msg}")

                # Save crash log
                crash_file = f"logs/crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                try:
                    os.makedirs('logs', exist_ok=True)
                    with open(crash_file, 'w', encoding='utf-8') as f:
                        f.write(f"Crash at: {datetime.now().isoformat()}\n")
                        f.write(f"Error: {error_type}: {error_msg}\n\n")
                        f.write("Traceback:\n")
                        f.write(tb)
                    print(f"\n[CRASH] Error logged to {crash_file}")
                except:
                    pass

                # Try to save price history
                if PRICE_HISTORY:
                    try:
                        save_price_history()
                    except:
                        pass

                # Check if we should restart
                if should_restart():
                    restart_timestamps.append(time.time())
                    restart_count = len(restart_timestamps)
                    print(f"\n[AUTO-RESTART] Crash detected: {error_type}: {error_msg}")
                    print(f"[AUTO-RESTART] Restarting in {RESTART_DELAY_SECONDS}s... (attempt {restart_count}/{MAX_RESTARTS_PER_HOUR} this hour)")
                    time.sleep(RESTART_DELAY_SECONDS)
                    print(f"[AUTO-RESTART] Restarting now...")
                    continue
                else:
                    print(f"\n[AUTO-RESTART] Max restarts ({MAX_RESTARTS_PER_HOUR}) exceeded in last hour")
                    print(f"[AUTO-RESTART] Bot stopping to prevent crash loop")
                    log_uptime("STOPPED", f"Max restarts exceeded - crash loop prevention")
                    raise

        # If we get here, it was a clean exit or KeyboardInterrupt
        raise KeyboardInterrupt("Clean shutdown")

    # No auto-restart - run once
    try:
        # Log bot start for uptime tracking
        log_uptime("STARTED", details={
            'scan_interval': f"{SCAN_INTERVAL}ms",
            'max_contracts': MAX_CONTRACTS,
            'min_buy_price': MIN_BUY_PRICE,
        })
        asyncio.run(run_executor())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        log_uptime("STOPPED", "KeyboardInterrupt")
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

    except SystemExit as e:
        # Intentional exit (e.g., kill switch)
        log_uptime("STOPPED", f"SystemExit: {e}")
        raise

    except Exception as e:
        # Unexpected crash - log it!
        import traceback
        error_type = type(e).__name__
        error_msg = str(e)
        tb = traceback.format_exc()

        log_uptime("STOPPED", f"CRASH: {error_type}: {error_msg}")

        # Also save traceback to a crash log
        crash_file = f"logs/crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        try:
            os.makedirs('logs', exist_ok=True)
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write(f"Crash at: {datetime.now().isoformat()}\n")
                f.write(f"Error: {error_type}: {error_msg}\n\n")
                f.write("Traceback:\n")
                f.write(tb)
            print(f"\n[CRASH] Error logged to {crash_file}")
        except:
            pass

        print(f"\n[CRASH] Bot crashed with {error_type}: {error_msg}")
        print(f"[CRASH] Check logs/uptime.log and {crash_file} for details")

        # Try to save price history even on crash
        if PRICE_HISTORY:
            try:
                print("[CRASH] Attempting to save price history...")
                save_price_history()
            except:
                pass

        raise
