#!/usr/bin/env python3
"""
Tennis V5 — Full VERSION B Deployment (BABY SIZING validation)
================================================================
Refactor of tennis_v4.py to support all 6 features from version_b_blueprint:

  1. AUTO-SELL at entry+exit_target  (38 of 41 cells)
  2. UNDERDOG betting               (21 of 41 cells)
  3. PER-CELL DCA DROPS             (10/15/20/25/30c per cell)
  4. ENTRY SUB-RANGES               (3c sub-tiers within 5c tiers)
  5. PER-CELL SIZING                (already in v4, extended)
  6. DUAL-SIDE MODE                 (leader and underdog on same event)

DEPLOYMENT MODE: BABY SIZING
  Every cell is forced to BABY_ENTRY_SIZE / BABY_DCA_SIZE (10/5) regardless
  of the blueprint's recommended 80/40 or 40/20. This validates all code
  paths on real matches with bounded risk (~$10 max loss per trade).

  After validation, set BABY_SIZING_MODE = False to use full blueprint sizing.

Match state keying:
  Composite key "event_ticker|direction" — each event can have up to 2
  active match states (one per direction). Both leader and underdog can
  trade independently on the same event.
"""

import asyncio, aiohttp, base64, json, os, sys, time, traceback, uuid
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
# H8 fix (2026-04-11): use DST-aware ZoneInfo for ET instead of hardcoded
# `timezone(timedelta(hours=-4))`. The old offset broke in winter (EST=UTC-5)
# and would silently mis-detect ESPN midnight placeholders from Nov–Mar.
try:
    from zoneinfo import ZoneInfo
    _ET_TZ = ZoneInfo("America/New_York")
except Exception:
    # Fallback: best-effort EDT for Python < 3.9 (will drift in winter)
    _ET_TZ = timezone(timedelta(hours=-4))
import sqlite3
from typing import Dict, List, Optional, Set, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Import VERSION B deployment blueprint
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version_b_blueprint import (
    DEPLOYMENT,
    get_strategy as _bp_get_strategy,
    use_blended_target as _bp_use_blended_target,
)

# ===== BABY SIZING MODE =====
# When True, all cells use 10/5 sizing regardless of blueprint.
# This validates the new code paths on real matches with bounded risk.
# Set to False to use full blueprint sizing after validation.
BABY_SIZING_MODE = True
BABY_ENTRY_SIZE = 10
BABY_DCA_SIZE = 5

# All timestamps in Eastern Time
import os as _os
_os.environ['TZ'] = 'America/New_York'
time.tzset()

# ---------------------------------------------------------------------------
# Category configs
# ---------------------------------------------------------------------------
CATEGORIES = {
    'ATP_MAIN': {
        'series': ['KXATPMATCH'],
        'side': 'leader',
        'entry_min': 55, 'entry_max': 90,
        'dca_drop': 15,
        'entry_window_sec': 300,
        'size': 40,
        'dca_size': 20,
        'max_entries': 1,
        'max_dca': 1,
        'enabled': True,
    },
    'WTA_MAIN': {
        'series': ['KXWTAMATCH'],
        'side': 'leader',
        'entry_min': 55, 'entry_max': 90,
        'dca_drop': 15,
        'entry_window_sec': 600,
        'size': 40,
        'dca_size': 20,
        'max_entries': 1,
        'max_dca': 1,
        'enabled': True,
    },
    'ATP_CHALL': {
        'series': ['KXATPCHALLENGERMATCH'],
        'side': 'leader',
        'entry_min': 55, 'entry_max': 90,
        'dca_drop': 15,
        'entry_window_sec': 600,
        'size': 40,
        'dca_size': 20,
        'max_entries': 1,
        'max_dca': 1,
        'enabled': True,
    },
    'WTA_CHALL': {
        'series': ['KXWTACHALLENGERMATCH'],
        'side': 'leader',
        'entry_min': 55, 'entry_max': 90,
        'dca_drop': 15,
        'entry_window_sec': 600,
        'size': 40,
        'dca_size': 20,
        'max_entries': 1,
        'max_dca': 1,
        'enabled': True,
    },
    'ATP_SLAM': {
        'series': ['KXATPGRANDSLAM'],
        'side': 'leader',
        'entry_min': 55, 'entry_max': 90,
        'dca_drop': 15,
        'entry_window_sec': 600,
        'size': 40,
        'dca_size': 20,
        'max_entries': 1,
        'max_dca': 1,
        'enabled': True,
    },
    'WTA_SLAM': {
        'series': ['KXWTAGRANDSLAM'],
        'side': 'leader',
        'entry_min': 55, 'entry_max': 90,
        'dca_drop': 15,
        'entry_window_sec': 600,
        'size': 40,
        'dca_size': 20,
        'max_entries': 1,
        'max_dca': 1,
        'enabled': True,
    },
}

# ---------------------------------------------------------------------------
# Conditional sizing: per-category, per-tier
# Based on 3,744-event backtest (Jan-Apr 2026, 71% leader WR)
# ---------------------------------------------------------------------------
SIZING_CONFIG = {
    # (category, tier_lo, tier_hi): (entry_size, dca_size)
    #
    # OPTION A — deployed 2026-04-10 after 5,889-event Kalshi tape
    # validation showed the prior 14-cell deploy was overfit on
    # poisoned matches-table data. The clean dataset shows 18 of
    # 28 cells are net-negative; only 10 cells have positive EV.
    # Of those 10, only 4 have EV >= $1.50 with N >= 100 — those
    # are doubled. The other 6 are kept at standard. WTA_CHALL
    # 80-84 has small N=44, kept standard despite high EV.
    #
    # All 18 negative-EV cells are SKIPPED. Skipping these cells
    # alone saves ~$60/day vs the prior bleeding deploy.

    # ----- DOUBLED 80/40 (top 3 cells, EV >= $1.50, N >= 100) -----
    ("ATP_CHALL", 65, 69): (80, 40),  # EV=+$3.47 WR=76% N=465
    ("ATP_CHALL", 70, 74): (80, 40),  # EV=+$1.71 WR=77% N=412
    ("WTA_MAIN",  60, 64): (80, 40),  # EV=+$2.98 WR=70% N=154

    # ----- STANDARD 40/20 (positive but smaller EV or smaller N) -----
    ("WTA_CHALL", 80, 84): (40, 20),  # EV=+$2.57 WR=92% N=48 (small N)
    ("ATP_MAIN",  65, 69): (40, 20),  # EV=+$0.86 WR=70% N=152
    ("WTA_CHALL", 85, 89): (40, 20),  # EV=+$0.65 WR=90% N=71
    ("ATP_CHALL", 60, 64): (40, 20),  # EV=+$0.78 WR=65% N=527
    ("ATP_MAIN",  55, 59): (40, 20),  # EV=+$0.38 WR=59% N=169
    ("WTA_MAIN",  65, 69): (40, 20),  # EV=+$0.04 WR=67% N=155 (borderline)

    # ----- STANDARD 40/0 (entry only, no DCA) -----
    ("WTA_CHALL", 75, 79): (40, 0),   # Config A best, EV+$0.42 WR=79% N=42

    # ----- SKIP cells (negative EV, N >= 30) -----
    ("ATP_MAIN",  60, 64): (0, 0),    # EV=-$0.22
    ("ATP_MAIN",  70, 74): (0, 0),    # EV=-$1.10  ← was DOUBLED, bleeding
    ("ATP_MAIN",  75, 79): (0, 0),    # EV=-$1.10  ← was ENTRY-only
    ("ATP_MAIN",  80, 84): (0, 0),    # EV=-$4.47  ← was ENTRY-only
    ("ATP_MAIN",  85, 89): (0, 0),    # EV=-$6.61  ← was ENTRY-only, worst cell
    ("ATP_CHALL", 55, 59): (0, 0),    # EV=-$2.13
    ("ATP_CHALL", 75, 79): (0, 0),    # EV=-$0.57  ← was ENTRY-only
    ("ATP_CHALL", 80, 84): (0, 0),    # EV=-$0.91
    ("ATP_CHALL", 85, 89): (0, 0),    # EV=-$3.21
    ("WTA_MAIN",  55, 59): (0, 0),    # EV=-$0.21  ← was DOUBLED
    ("WTA_MAIN",  70, 74): (0, 0),    # EV=-$3.68
    ("WTA_MAIN",  75, 79): (0, 0),    # EV=-$1.71  ← was ENTRY-only
    ("WTA_MAIN",  80, 84): (0, 0),    # EV=-$2.82
    ("WTA_MAIN",  85, 89): (0, 0),    # EV=-$5.10
    ("WTA_CHALL", 55, 59): (0, 0),    # EV=-$4.84  ← was DOUBLED
    ("WTA_CHALL", 60, 64): (0, 0),    # EV=-$3.87
    ("WTA_CHALL", 65, 69): (0, 0),    # EV=-$2.50  ← was DOUBLED
    ("WTA_CHALL", 70, 74): (0, 0),    # EV=-$4.29
}

def get_sizing(category, bid_price):
    # H14 fix (2026-04-11): honor BABY_SIZING_MODE here so callers don't have
    # to remember to override. Previously the reconcile legacy-fallback path
    # called this and got raw (40, 20), which was the root cause of the MON
    # post-restart over-DCA incident (20ct instead of 5ct baby).
    for (cat, lo, hi), (es, ds) in SIZING_CONFIG.items():
        if cat == category and lo <= bid_price <= hi:
            if BABY_SIZING_MODE:
                return (BABY_ENTRY_SIZE, BABY_DCA_SIZE if ds > 0 else 0)
            return (es, ds)
    if BABY_SIZING_MODE:
        return (BABY_ENTRY_SIZE, BABY_DCA_SIZE)
    return (40, 20)  # default standard


# ---------------------------------------------------------------------------
# VERSION B blueprint helpers
# ---------------------------------------------------------------------------
LEADER_TIERS_V5 = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS_V5 = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]


def get_strategy_v5(category, direction, entry_price):
    """Look up the per-cell strategy from the VERSION B blueprint.

    Returns the strategy dict (with baby-sizing applied if BABY_SIZING_MODE)
    or None if no viable cell exists for this category/direction/price.
    """
    if direction == 'leader':
        tiers = LEADER_TIERS_V5
    else:
        tiers = UNDERDOG_TIERS_V5
    for lo, hi in tiers:
        if not (lo <= entry_price <= hi):
            continue
        cell = DEPLOYMENT.get((category, direction, lo, hi))
        if cell is None:
            return None  # explicit SKIP (key absent from blueprint)
        # SKIP marker: entry_size == 0 in the blueprint (15 of 56 cells)
        if cell.get('entry_size', 0) == 0:
            return None
        # Apply entry sub-range filter
        if not (cell['entry_lo'] <= entry_price <= cell['entry_hi']):
            return None  # outside the optimal sub-range
        # Apply baby-sizing override (AFTER skip check, so we never trade SKIP cells)
        result = dict(cell)
        if BABY_SIZING_MODE:
            result['entry_size'] = BABY_ENTRY_SIZE
            result['dca_size'] = BABY_DCA_SIZE if cell['dca_drop'] is not None else 0
        result['_tier_lo'] = lo
        result['_tier_hi'] = hi
        return result
    return None


def lookup_edge(event_ticker):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT player1_name, player2_name, pinnacle_p1, pinnacle_p2, "
                    "kalshi_p1, kalshi_p2, edge_p1, edge_p2, grade "
                    "FROM edge_scores WHERE event_ticker = ?", (event_ticker,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {"p1": row[0], "p2": row[1], "pin_p1": row[2], "pin_p2": row[3],
                    "kalshi_p1": row[4], "kalshi_p2": row[5],
                    "edge_p1": row[6], "edge_p2": row[7], "grade": row[8]}
    except Exception:
        pass
    return None

ALL_SERIES = []
for cfg in CATEGORIES.values():
    if cfg.get('enabled', True):
        ALL_SERIES.extend(cfg['series'])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"
LOG_FILE = "/tmp/tennis_v4.log"
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")
BBO_LOG_FILE = "/tmp/bbo_log_v4.csv"
DCA_STATE_FILE = "/tmp/dca_cooling_state.json"
MAX_RPS = 8
MAX_HOURS_TO_EXPIRY = 12
MIN_VOLUME = 50
DISCOVERY_INTERVAL = 300
POSITION_POLL_INTERVAL = 30
WS_PING_INTERVAL = 15
WS_SUBSCRIBE_BATCH = 50
# H11 fix: capital-cap poll cadence + max fraction of balance to hold in exposure
CAPITAL_POLL_INTERVAL = 60    # refresh balance every 60s
CAPITAL_CAP_FRACTION = 0.90   # never exceed 90% of balance in active exposure

# Entry execution
# Category-aware fill timeouts (seconds per attempt)
# ATP Main: bid changes every 98s median → need 300s to see 3 changes
# WTA Main: bid changes every 14s → 120s is plenty
# Challengers: bid changes every 4s → 30s is fine
FILL_TIMEOUTS = {
    'ATP_MAIN': 300, 'WTA_MAIN': 120,
    'ATP_CHALL': 30, 'WTA_CHALL': 30,
    'ATP_SLAM': 300, 'WTA_SLAM': 120,
}
MAX_ENTRY_ATTEMPTS = 5       # max placement attempts per match
MATCH_START_TPM = 8          # bid changes per minute threshold for match start (logging only)
DCA_COOL_SEC = 60            # 1 minute cooling
DCA_COOL_RECOVERY = 10      # cancel cooling if price recovers within 10c of entry

# DCA: simple 15c dip trigger, 60s cooling, max 1 per match

# Clock-based entry window (replaces MATCH_START-gated entry)
ENTRY_BEFORE_START = 3600    # enter up to 60 min BEFORE scheduled start
ENTRY_AFTER_START = 3600     # enter up to 60 min AFTER scheduled start
SCHED_DELAY_TIMEOUT = 7200   # 2h past schedule with no play = delayed match
PREGAME_REFRESH_SEC = 60     # refresh resting buy every 60s
TAKER_TRIGGER_BEFORE = 0     # DISABLED 20260415 - maker only, no taker crossing

# ---------------------------------------------------------------------------
_log_file = None
def log(msg):
    global _log_file
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    try:
        if _log_file is None:
            _log_file = open(LOG_FILE, "a", buffering=1)
        _log_file.write(line + "\n")
    except Exception:
        pass

# ---------------------------------------------------------------------------
ALERT_FILE = "/tmp/tennis_alerts.log"
_alert_file = None
def alert(msg):
    global _alert_file
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] [ALERT] %s" % (ts, msg)
    log(msg)  # also goes to main log
    try:
        if _alert_file is None:
            _alert_file = open(ALERT_FILE, "a", buffering=1)
        _alert_file.write(line + "\n")
    except Exception:
        pass

# ---------------------------------------------------------------------------
def db_log_settlement(side, result, pos, avg, category, entry_price=None, dca_price=None, dca_size=None):
    try:
        from datetime import datetime as _dt
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        date = _dt.now().strftime("%Y-%m-%d")
        ts = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
        # Use blended avg for P&L calculation
        # C3 fix (2026-04-11): Kalshi pays 100c on win, not 99c. Using 99 under-reports
        # every winning trade by 1c × position size. Cumulative ledger drift over time.
        pnl = (100 - avg) * pos if result == "won" else -(avg * pos)
        # entry_price = original entry (before DCA), avg_price = blended after DCA
        ep = entry_price if entry_price is not None else avg
        c.execute("""INSERT OR IGNORE INTO matches
            (date, category, our_side, entry_price, result, total_size, avg_price,
             pnl_cents, settlement_time, source, dca_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (date, category, side, ep, result, pos, avg, pnl, ts, "live", dca_price))
        conn.commit()
        conn.close()
    except Exception:
        pass

def db_log_entry(side, price, size, category, event_ticker=""):
    try:
        from datetime import datetime as _dt
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        date = _dt.now().strftime("%Y-%m-%d")
        ts = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""INSERT OR IGNORE INTO active_positions
            (event_ticker, side, size, avg_price, dca_status, entry_time, match_status, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_ticker, side, size, price, "watching", ts, "pregame", ts))
        conn.commit()
        conn.close()
    except Exception:
        pass

# ---------------------------------------------------------------------------
def load_credentials():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass
    api_key = os.getenv("KALSHI_API_KEY")
    pem_path = Path(__file__).resolve().parent / "kalshi.pem"
    if not pem_path.exists():
        sys.exit("[FATAL] kalshi.pem not found")
    pk = serialization.load_pem_private_key(pem_path.read_bytes(), password=None, backend=default_backend())
    return api_key, pk

# DCA cooling state persistence — survives bot restarts
def save_dca_state(match_states):
    state = {}
    for et, ms in match_states.items():
        if ms.dca_phase == "cooling" and ms.dca_cool_start > 0:
            state[ms.our_ticker] = {
                "event_ticker": et,
                "dca_cool_start": ms.dca_cool_start,
                "dca_cool_trigger_bid": ms.dca_cool_trigger_bid,
                "dca_cool_duration": ms.dca_cool_duration,
                "entry_price": ms.entry_price,
            }
    try:
        with open(DCA_STATE_FILE, "w") as fh:
            json.dump(state, fh)
    except Exception:
        pass

def load_dca_state():
    try:
        with open(DCA_STATE_FILE, "r") as fh:
            return json.load(fh)
    except (FileNotFoundError, ValueError):
        return {}

def is_match_live_te(event_ticker):
    """Check TE live_scores DB for actual match status.
    Returns: (is_live, p1_sets, p2_sets) or (None, 0, 0) if no data."""
    try:
        import sqlite3
        db = sqlite3.connect(DB_PATH)
        # Try matching by kalshi_ticker field
        row = db.execute(
            "SELECT status, p1_sets, p2_sets FROM live_scores WHERE kalshi_ticker != '' "
            "AND ? LIKE '%' || kalshi_ticker || '%' ORDER BY last_updated DESC LIMIT 1",
            (event_ticker,)).fetchone()
        db.close()
        if row:
            return (row[0] == 'live', int(row[1] or 0), int(row[2] or 0))
        return (None, 0, 0)
    except Exception:
        return (None, 0, 0)


def sign_request(pk, ts, method, path):
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return base64.b64encode(sig).decode("utf-8")

def auth_headers(ak, pk, method, path):
    ts = str(int(time.time() * 1000))
    return {"KALSHI-ACCESS-KEY": ak,
            "KALSHI-ACCESS-SIGNATURE": sign_request(pk, ts, method, path.split("?")[0]),
            "KALSHI-ACCESS-TIMESTAMP": ts, "Content-Type": "application/json"}

class RateLimiter:
    def __init__(self):
        self.ts = deque()
    async def acquire(self):
        now = time.monotonic()
        while self.ts and now - self.ts[0] >= 1.0:
            self.ts.popleft()
        if len(self.ts) >= MAX_RPS:
            await asyncio.sleep(1.0 - (now - self.ts[0]))
        self.ts.append(time.monotonic())

async def api_get(s, ak, pk, path, rl):
    for bo in [1, 2, 4, None]:
        await rl.acquire()
        try:
            async with s.get("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "GET", path),
                             timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200: return await r.json()
                if r.status == 429 and bo: await asyncio.sleep(bo); continue
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo: await asyncio.sleep(bo); continue
            return None
    return None

async def api_post(s, ak, pk, path, payload, rl):
    for bo in [1, 2, 4, None]:
        await rl.acquire()
        try:
            async with s.post("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "POST", path),
                              json=payload, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status in (200, 201): return await r.json()
                if r.status == 429 and bo: await asyncio.sleep(bo); continue
                body = await r.text()
                # T2-4 fix: detect market-close race BEFORE logging as error.
                # audit_sells races cleanup_settled near match finalization ~8x/day;
                # these are expected, not real errors. Downgrade to info log and
                # skip the alert.
                is_dead_market = ("MARKET_NOT_ACTIVE" in body or
                                  "market_closed" in body or
                                  "market closed" in body)
                if is_dead_market and "orders" in path:
                    log("[SELL_AUDIT_RACE] POST %s raced settlement, market already closed (expected)" %
                        path.split("/")[-1])
                    return {"_dead_market": True}
                # Real error path — log and alert
                log("  [ERR] POST %d %s: %s" % (r.status, path, body[:200]))
                if "orders" in path:
                    alert("[ORDER_REJECT] POST %d %s: %s" % (r.status, path.split("/")[-1], body[:100]))
                if is_dead_market:
                    return {"_dead_market": True}
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo: await asyncio.sleep(bo); continue
            return None
    return None

async def api_delete(s, ak, pk, path, rl):
    for bo in [1, 2, None]:
        await rl.acquire()
        try:
            async with s.delete("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "DELETE", path),
                                timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status in (200, 204): return True
                if r.status == 429 and bo: await asyncio.sleep(bo); continue
                return False
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo: await asyncio.sleep(bo); continue
            return False
    return False

# ---------------------------------------------------------------------------
@dataclass
class Book:
    bids: Dict[int, int] = field(default_factory=dict)
    asks: Dict[int, int] = field(default_factory=dict)
    best_bid: int = 0
    best_ask: int = 100
    updated: float = 0.0

def recalc_bbo(b):
    b.best_bid = max(b.bids.keys()) if b.bids else 0
    b.best_ask = min(b.asks.keys()) if b.asks else 100

# ---------------------------------------------------------------------------
# Per-event match state
# ---------------------------------------------------------------------------
@dataclass
class MatchState:
    event_ticker: str
    category: str
    cfg: dict
    # Tickers (both sides of the match)
    tickers: Set[str] = field(default_factory=set)
    our_ticker: str = ""       # the side we're trading

    # Match detection
    gate_bid: int = 0               # leader bid at gate open — pregame floor check
    gate_ask: int = 0               # ask at gate open
    gate_mid: float = 0.0           # (gate_bid + gate_ask) / 2
    gate_spread: int = 0            # gate_ask - gate_bid
    match_started: bool = False
    match_start_ts: float = 0.0
    tick_count_window: int = 0
    tick_window_start: float = 0.0
    last_bid: int = 0               # last seen bid for change detection
    last_ask: int = 0               # last seen ask
    bid_change_count: int = 0        # bid changes in current window

    # Entry state
    pick_bid: int = 0              # bid price seen at PICK_SIDE time
    pick_ask: int = 0              # ask price seen at PICK_SIDE time
    entry_phase: str = "waiting"  # waiting | pregame | seeking | placed | filled | skipped
    pregame_order_id: str = ""     # resting pregame maker buy
    pregame_placed_ts: float = 0.0
    pregame_price: int = 0
    entry_price: int = 0
    entry_order_id: str = ""
    entry_placed_ts: float = 0.0
    entry_attempts: int = 0
    entry_fill_ts: float = 0.0

    # Timing
    created_ts: float = 0.0        # when this state was created (ignore early ticks)
    earliest_entry_ts: float = 0.0 # don't enter before this time
    scheduled_start_ts: float = 0.0 # V1 API expected_determination_time
    latest_entry_ts: float = 0.0   # don't enter after this time
    schedule_source: str = ""      # "espn", "tennisexplorer", "price_stability"

    # Match play detection (for DCA scenario routing)
    match_play_start_ts: float = 0.0  # when price first moved 3c+ from flat (first ball proxy)

    # Price stability fallback (for SKIP_NO_SCHED tickers)
    price_stability_phase: str = ""   # "" | "monitoring" | "pregame" | "live_detected"
    first_bid: int = 0                # first observed bid on leader side
    first_bid_ts: float = 0.0        # when first_bid was recorded
    first_ask: int = 0               # first observed ask
    first_ask_ts: float = 0.0
    first_mid: float = 0.0           # (first_bid + first_ask) / 2
    first_spread: int = 0            # first_ask - first_bid
    det_time_ts: float = 0.0         # expected_determination_time from Kalshi

    # DCA state
    dca_phase: str = "watching"  # watching | cooling | placed | filled | skipped
    dca_price: int = 0
    dca_order_id: str = ""
    dca_placed_ts: float = 0.0
    dca_cool_start: float = 0.0    # when cooling phase began
    dca_cool_trigger_bid: int = 0  # bid that triggered cooling
    dca_cool_duration: int = 60   # cooling time (scaled by match age)
    dca_cool_extensions: int = 0  # number of 60s stability extensions
    dca_stable_since: float = 0.0 # when bid last became stable
    dca_last_stable_bid: int = 0  # bid when stability check started
    topup_order_id: str = ""     # resting top-up order
    topup_placed_ts: float = 0.0

    # Position
    position_qty: int = 0
    sell_order_id: str = ""
    # Realized portion (tracks contracts sold pre-settlement via auto-sell maker fills)
    realized_sell_qty: int = 0       # how many contracts already closed out at auto_sell_price
    realized_sell_price: int = 0     # approx avg price those closed contracts filled at

    # Per-match sizing (set at PICK_SIDE/SIZING time, immutable thereafter).
    # These exist because the cfg dict is shared across all matches in a
    # category, so mutating cfg['size'] for one match clobbers every other
    # match. Always read entry/DCA size from these fields, never from cfg.
    target_size: int = 0
    target_dca_size: int = 0

    # ===== VERSION B per-cell strategy fields =====
    # Each MatchState represents ONE position (leader OR underdog side of an
    # event). Both can coexist for the same event using composite key
    # "event_ticker|direction" in match_states dict.
    direction: str = 'leader'        # 'leader' or 'underdog'
    dca_drop: int = 15               # per-cell DCA drop (was global 15c)
    exit_target: int = 0             # auto-sell at entry+X (0 = hold to settle 99c)
    entry_lo_filter: int = 0         # entry sub-range floor
    entry_hi_filter: int = 99        # entry sub-range ceiling
    auto_sell_price: int = 99        # actual sell limit price (entry+exit_target or 99)
    strategy_loaded: bool = False    # whether DEPLOYMENT lookup happened
    use_blended_target: bool = False # if True, recompute auto-sell at blended_avg+exit on DCA fill (Strategy B)
    maker_bid_offset: int = 0        # V5 20260415 — offset applied to bid+1/bid+2 maker placement (neg for underdog deflation)

    def __post_init__(self):
        # Initialize per-match sizing from category template defaults.
        # SIZING (live PICK_SIDE) or RECONCILE will overwrite with the
        # tier-specific values once the picked side and price are known.
        if self.cfg:
            if self.target_size == 0:
                self.target_size = self.cfg.get('size', 40)
            if self.target_dca_size == 0:
                self.target_dca_size = self.cfg.get('dca_size', 20)

# ---------------------------------------------------------------------------
class TennisV5:
    def __init__(self):
        self.ak, self.pk = load_credentials()
        self.rl = RateLimiter()
        self.session = None
        self.ws = None
        self.ws_connected = False

        self.books: Dict[str, Book] = {}
        self.subscribed: Set[str] = set()
        self.msg_id = 0

        # External schedule (ESPN + TennisExplorer)
        self.ext_schedule: dict = {}
        self.last_schedule_fetch: float = 0.0

        # H11 fix (2026-04-11): capital cap state. Balance is refreshed every
        # CAPITAL_POLL_INTERVAL seconds in the main loop. `place_buy` rejects
        # new orders if projected_exposure + existing_exposure would exceed
        # CAPITAL_CAP_FRACTION of the refreshed balance. At baby sizing this
        # is dormant (exposure tiny vs balance), but CRITICAL before scaling
        # to full 80/40 where 20+ concurrent cells could exceed available cash.
        self.current_balance: float = 0.0  # dollars
        self.last_balance_fetch: float = 0.0

        # Event tracking
        self.ticker_to_event: Dict[str, str] = {}
        self.event_tickers: Dict[str, Set[str]] = defaultdict(set)
        self.ticker_category: Dict[str, str] = {}

        # Match states — keyed by composite "event_ticker|direction" string.
        # Each event can have up to 2 entries (leader + underdog).
        self.match_states: Dict[str, MatchState] = {}

        # BBO logging
        self._bbo_buf: List[str] = []
        self._bbo_file = None

    def get_category(self, ticker):
        """Determine which category a ticker belongs to."""
        for cat_name, cfg in CATEGORIES.items():
            for series in cfg['series']:
                if ticker.startswith(series):
                    return cat_name, cfg
        return None, None

    # ------------------------------------------------------------------
    # VERSION B match-state lookups (composite keys)
    # ------------------------------------------------------------------
    def ms_key(self, event_ticker, direction):
        """Build composite key 'event_ticker|direction'."""
        return "{}|{}".format(event_ticker, direction)

    def get_event_states(self, event_ticker):
        """Return all MatchState entries for an event (1 or 2)."""
        return [ms for k, ms in self.match_states.items()
                if k.startswith(event_ticker + "|")]

    def find_ms_by_ticker(self, ticker):
        """Find the MatchState whose our_ticker matches the given full ticker.
        Returns None if no match (e.g., ticker not yet picked, or skipped)."""
        for ms in self.match_states.values():
            if ms.our_ticker == ticker:
                return ms
        return None

    def find_ms_by_event_and_direction(self, event_ticker, direction):
        """Direct composite key lookup."""
        return self.match_states.get(self.ms_key(event_ticker, direction))

    def _sell_price_for(self, ms):
        """V5: compute the auto-sell price for a match state.

        If ms.exit_target > 0 and ms.entry_price is set, sell at
        entry_price + exit_target (capped at 99). Otherwise sell at 99
        (hold-to-settlement strategies and reconciled positions w/o entry).
        """
        if getattr(ms, 'exit_target', 0) > 0 and ms.entry_price > 0:
            return min(99, ms.entry_price + ms.exit_target)
        return 99

    # ------------------------------------------------------------------
    # H11 fix (2026-04-11): capital-cap helpers
    # ------------------------------------------------------------------
    async def refresh_balance(self):
        """Refresh cached balance from Kalshi. Called from main loop every
        CAPITAL_POLL_INTERVAL. Stores dollars in self.current_balance.

        CRITICAL FIX (2026-04-12): Kalshi V2 API /portfolio/balance returns
        the `balance` field in CENTS (integer). Previous code stored the raw
        value as dollars, inflating the balance by 100× and making the H11
        capital cap non-functional ($251k cap vs real $2.5k). Now divides by
        100 to convert cents → dollars correctly.
        """
        bal_data = await api_get(self.session, self.ak, self.pk,
                                 "/trade-api/v2/portfolio/balance", self.rl)
        if bal_data:
            raw = bal_data.get("balance", 0)
            if isinstance(raw, (int, float)) and raw > 0:
                self.current_balance = raw / 100.0  # CENTS → dollars
                self.last_balance_fetch = time.time()

    def _estimate_current_exposure(self):
        """Sum of (position_qty × entry_price) across all active match_states,
        in dollars. This is the *cost basis* of held positions — what we've
        committed to Kalshi. Doesn't include resting DCA buy orders (those
        add potential future exposure but aren't yet committed)."""
        total_cents = 0
        for ms in self.match_states.values():
            if ms.position_qty > 0 and ms.entry_price > 0:
                total_cents += ms.position_qty * ms.entry_price
        return total_cents / 100.0  # cents → dollars

    def _check_capital_cap(self, new_cost_dollars, label=""):
        """H11: return True if placing a new order of `new_cost_dollars` would
        keep projected exposure under CAPITAL_CAP_FRACTION × balance.
        Returns False and emits [CAPITAL_CAP_REJECT] otherwise.

        Dormant if balance hasn't been refreshed yet (returns True to avoid
        blocking startup — main loop refreshes balance on first iteration).
        """
        if self.current_balance <= 0:
            return True  # unknown balance, don't block
        existing = self._estimate_current_exposure()
        projected = existing + new_cost_dollars
        cap = self.current_balance * CAPITAL_CAP_FRACTION
        if projected > cap:
            log("[CAPITAL_CAP_REJECT] %s would push exposure $%.2f + $%.2f = $%.2f > cap $%.2f (bal=$%.2f × %.0f%%)" % (
                label or "order", existing, new_cost_dollars, projected, cap,
                self.current_balance, CAPITAL_CAP_FRACTION * 100))
            return False
        return True

    # ------------------------------------------------------------------
    # BBO logging
    # ------------------------------------------------------------------
    def _bbo_log(self, ticker, bid, ask):
        row = "%s,%s,%d,%d,%d\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), ticker, bid, ask, ask - bid)
        self._bbo_buf.append(row)
        if len(self._bbo_buf) >= 200:
            self._flush_bbo()

    def _flush_bbo(self):
        if not self._bbo_buf: return
        try:
            if self._bbo_file is None:
                self._bbo_file = open(BBO_LOG_FILE, "a", buffering=8192)
                if self._bbo_file.tell() == 0:
                    self._bbo_file.write("timestamp,ticker,bid,ask,spread\n")
            self._bbo_file.writelines(self._bbo_buf)
            self._bbo_file.flush()
        except Exception:
            pass
        self._bbo_buf.clear()

    # ------------------------------------------------------------------
    # Market discovery
    # ------------------------------------------------------------------
    async def discover_markets(self):
        all_tickers = []
        now = time.time()
        counts = defaultdict(int)

        for series in ALL_SERIES:
            cursor = ""
            for _ in range(10):
                path = "/trade-api/v2/markets?limit=100&status=open&series_ticker=%s" % series
                if cursor: path += "&cursor=%s" % cursor
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data: break
                for m in data.get("markets", []):
                    ticker = m["ticker"]
                    vol = int(float(m.get("volume_fp", "0") or "0"))
                    if vol < MIN_VOLUME: continue
                    expiry_str = m.get("expected_expiration_time", "")
                    if expiry_str and not expiry_str.startswith("0001"):
                        try:
                            exp = datetime.fromisoformat(expiry_str.replace("Z", "+00:00")).timestamp()
                            if (exp - now) / 3600 > MAX_HOURS_TO_EXPIRY: continue
                        except: pass
                    et = m["event_ticker"]
                    self.ticker_to_event[ticker] = et
                    self.event_tickers[et].add(ticker)

                    cat_name, cfg = self.get_category(ticker)
                    if cat_name and CATEGORIES[cat_name].get('enabled', True):
                        self.ticker_category[ticker] = cat_name
                        counts[cat_name] += 1

                        # Initialize match state if needed
                        if et not in self.match_states:
                            # Collect full player names from all markets in this event
                            kalshi_names = []
                            for evt_tk in self.event_tickers.get(et, set()):
                                # Market titles are like "Will Frederico Ferreira Silva win..."
                                # The V2 markets list has a "name" field via V1 or we can
                                # parse from the ticker's market data if available
                                pass
                            # Fetch player names from V1 API for fuzzy matching
                            # C1 fix (2026-04-11): was sync `requests.get(...)` which
                            # blocked the event loop for up to 5s per new event. Replaced
                            # with async api_get using the existing aiohttp session.
                            v1_data = None
                            try:
                                v1_data = await api_get(self.session, self.ak, self.pk,
                                                        "/v1/events/" + et, self.rl)
                                if v1_data:
                                    for vm in v1_data.get("event", {}).get("markets", []):
                                        pname = vm.get("name", "")
                                        if pname:
                                            kalshi_names.append(pname)
                            except Exception:
                                pass

                            # Look up start time from ESPN/TennisExplorer schedule
                            from tennis_schedule import match_kalshi_event
                            match_info = match_kalshi_event(et, self.ext_schedule,
                                                            kalshi_player_names=kalshi_names)

                            if not match_info:
                                # No schedule — set up price-stability monitoring
                                # Get det_time from V1 for estimated start fallback
                                det_ts = 0.0
                                try:
                                    if v1_data:
                                        for vm in v1_data.get("event", {}).get("markets", []):
                                            edt = vm.get("rulebook_variables", {}).get("expected_determination_time", "")
                                            if edt:
                                                # H9 partial fix: handle Z suffix for tz-aware parse
                                                det_ts = datetime.fromisoformat(edt.replace("Z", "+00:00")).timestamp()
                                                break
                                except Exception:
                                    pass
                                # Smart schedule fallback chain
                                # Priority 3: exp_exp - 2.5h (if exp_exp within 12h)
                                exp_exp_str = m.get("expected_expiration_time", "")
                                exp_exp_ts = 0
                                if exp_exp_str and not exp_exp_str.startswith("0001"):
                                    try:
                                        exp_exp_ts = datetime.fromisoformat(
                                            exp_exp_str.replace("Z", "+00:00")).timestamp()
                                    except Exception:
                                        pass

                                # Priority 4: open_time + 2h
                                open_time_str = m.get("open_time", "")
                                open_ts = 0
                                if open_time_str:
                                    try:
                                        open_ts = datetime.fromisoformat(
                                            open_time_str.replace("Z", "+00:00")).timestamp()
                                    except Exception:
                                        pass

                                now_ts = time.time()
                                est_start = 0
                                sched_src = "none"

                                if exp_exp_ts and 0 < (exp_exp_ts - now_ts) < 43200:
                                    # exp_exp within 12h — use it as match end proxy
                                    est_start = exp_exp_ts - 9000  # minus 2.5h
                                    sched_src = "exp_exp-2.5h"
                                elif open_ts and (now_ts - open_ts) < 86400:
                                    # Same-day market: open_time + 2h
                                    est_start = open_ts + 7200
                                    sched_src = "open_time+2h"
                                elif det_ts:
                                    # Last resort: det_time - 3h
                                    est_start = det_ts - 10800
                                    sched_src = "det_time-3h"

                                if not est_start:
                                    log("[SKIP_NO_SCHED] %s — no schedule and no time fields" % et)
                                    self.match_states[et] = MatchState(
                                        event_ticker=et, category=cat_name, cfg=cfg,
                                        created_ts=time.time())
                                    self.match_states[et].entry_phase = "skipped"
                                    self.match_states[et].tickers.add(ticker)
                                    continue

                                gate_open = est_start - ENTRY_BEFORE_START
                                gate_close = est_start + ENTRY_AFTER_START
                                self.match_states[et] = MatchState(
                                    event_ticker=et, category=cat_name, cfg=cfg,
                                    created_ts=time.time(),
                                    earliest_entry_ts=gate_open,
                                    scheduled_start_ts=est_start,
                                    latest_entry_ts=gate_close,
                                    schedule_source="price_stability",
                                    price_stability_phase="monitoring",
                                    det_time_ts=det_ts,
                                    first_bid_ts=time.time())
                                log("[PRICE_MONITOR] %s — no schedule, source=%s (est_start=%s)" % (
                                    et, sched_src,
                                    datetime.fromtimestamp(est_start).strftime("%H:%M")))
                                self.match_states[et].tickers.add(ticker)
                                continue

                            ext_status = match_info.get("status", "")
                            if ext_status in ("live", "in", "completed", "post"):
                                log("[SKIP_LIVE] %s — %s per %s" % (et, ext_status, match_info.get("source", "?")))
                                self.match_states[et] = MatchState(
                                    event_ticker=et, category=cat_name, cfg=cfg,
                                    created_ts=time.time())
                                self.match_states[et].entry_phase = "skipped"
                                self.match_states[et].tickers.add(ticker)
                                continue

                            start_str = match_info.get("start_time", "")
                            try:
                                sched_ts = datetime.fromisoformat(
                                    start_str.replace("Z", "+00:00")).timestamp()
                            except Exception:
                                sched_ts = 0.0

                            # ESPN midnight placeholder: 00:00 ET = "after prev match"
                            # H8 fix: use module-level _ET_TZ (ZoneInfo-based,
                            # DST-aware) instead of the broken hardcoded EDT offset.
                            if sched_ts and match_info.get("source") == "espn":
                                _local = datetime.fromtimestamp(sched_ts, tz=_ET_TZ)
                                if _local.hour == 0 and _local.minute == 0:
                                    log("[ESPN_PLACEHOLDER] %s — ESPN 00:00, falling back" % et)
                                    sched_ts = 0.0

                            # Also reject espn_midnight flag from schedule layer
                            if match_info.get("espn_midnight"):
                                log("[ESPN_PLACEHOLDER] %s — flagged midnight, falling back" % et)
                                sched_ts = 0.0

                            if not sched_ts:
                                # Fall through to time-field fallback chain
                                det_ts_fb = 0.0
                                try:
                                    if v1_data:
                                        for vm in v1_data.get("event", {}).get("markets", []):
                                            edt = vm.get("rulebook_variables", {}).get(
                                                "expected_determination_time", "")
                                            if edt:
                                                # H9 partial fix: handle Z suffix for tz-aware parse
                                                det_ts_fb = datetime.fromisoformat(edt.replace("Z", "+00:00")).timestamp()
                                                break
                                except Exception:
                                    pass

                                exp_exp_str_fb = m.get("expected_expiration_time", "")
                                exp_exp_ts_fb = 0
                                if exp_exp_str_fb and not exp_exp_str_fb.startswith("0001"):
                                    try:
                                        exp_exp_ts_fb = datetime.fromisoformat(
                                            exp_exp_str_fb.replace("Z", "+00:00")).timestamp()
                                    except Exception:
                                        pass

                                open_time_str_fb = m.get("open_time", "")
                                open_ts_fb = 0
                                if open_time_str_fb:
                                    try:
                                        open_ts_fb = datetime.fromisoformat(
                                            open_time_str_fb.replace("Z", "+00:00")).timestamp()
                                    except Exception:
                                        pass

                                now_ts_fb = time.time()
                                est_start_fb = 0
                                sched_src_fb = "none"

                                if exp_exp_ts_fb and 0 < (exp_exp_ts_fb - now_ts_fb) < 43200:
                                    est_start_fb = exp_exp_ts_fb - 9000
                                    sched_src_fb = "exp_exp-2.5h"
                                elif open_ts_fb and (now_ts_fb - open_ts_fb) < 86400:
                                    est_start_fb = open_ts_fb + 7200
                                    sched_src_fb = "open_time+2h"
                                elif det_ts_fb:
                                    est_start_fb = det_ts_fb - 10800
                                    sched_src_fb = "det_time-3h"

                                if not est_start_fb:
                                    log("[SKIP_NO_SCHED] %s — no schedule and no fallback times" % et)
                                    self.match_states[et] = MatchState(
                                        event_ticker=et, category=cat_name, cfg=cfg,
                                        created_ts=time.time())
                                    self.match_states[et].entry_phase = "skipped"
                                    self.match_states[et].tickers.add(ticker)
                                    continue

                                gate_open_fb = est_start_fb - ENTRY_BEFORE_START
                                gate_close_fb = est_start_fb + ENTRY_AFTER_START
                                p1_fb = match_info.get("p1", "?")[:15] if match_info else "?"
                                p2_fb = match_info.get("p2", "?")[:15] if match_info else "?"
                                self.match_states[et] = MatchState(
                                    event_ticker=et, category=cat_name, cfg=cfg,
                                    created_ts=time.time(),
                                    earliest_entry_ts=gate_open_fb,
                                    scheduled_start_ts=est_start_fb,
                                    latest_entry_ts=gate_close_fb,
                                    schedule_source=sched_src_fb)
                                log("[SCHED] %s | %s vs %s | start=%s | window=%s-%s | %s (ESPN midnight fallback)" % (
                                    et, p1_fb, p2_fb,
                                    datetime.fromtimestamp(est_start_fb).strftime("%H:%M"),
                                    datetime.fromtimestamp(gate_open_fb).strftime("%H:%M"),
                                    datetime.fromtimestamp(gate_close_fb).strftime("%H:%M"),
                                    sched_src_fb))
                                self.match_states[et].tickers.add(ticker)
                                continue

                            gate_open = sched_ts - ENTRY_BEFORE_START
                            gate_close = sched_ts + ENTRY_AFTER_START
                            src = match_info.get("source", "?")
                            self.match_states[et] = MatchState(
                                event_ticker=et, category=cat_name, cfg=cfg,
                                created_ts=time.time(),
                                earliest_entry_ts=gate_open,
                                scheduled_start_ts=sched_ts,
                                latest_entry_ts=gate_close,
                                schedule_source=src)
                            p1 = match_info.get("p1", "?")[:15]
                            p2 = match_info.get("p2", "?")[:15]
                            log("[SCHED] %s | %s vs %s | start=%s | window=%s-%s | %s" % (
                                et, p1, p2,
                                datetime.fromtimestamp(sched_ts).strftime("%H:%M"),
                                datetime.fromtimestamp(gate_open).strftime("%H:%M"),
                                datetime.fromtimestamp(gate_close).strftime("%H:%M"),
                                src))
                        self.match_states[et].tickers.add(ticker)

                    all_tickers.append(ticker)
                cursor = data.get("cursor", "")
                if not cursor: break

        log("[DISCOVERY] %d tickers: %s" % (
            len(all_tickers),
            " | ".join("%s=%d" % (k, v) for k, v in sorted(counts.items()))))
        return all_tickers

    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------
    async def ws_connect(self):
        ts = str(int(time.time() * 1000))
        headers = {"KALSHI-ACCESS-KEY": self.ak,
                    "KALSHI-ACCESS-SIGNATURE": sign_request(self.pk, ts, "GET", WS_PATH),
                    "KALSHI-ACCESS-TIMESTAMP": ts}
        try:
            import websockets
            self.ws = await websockets.connect(WS_URL, additional_headers=headers,
                ping_interval=WS_PING_INTERVAL, ping_timeout=10, max_size=10_000_000)
            self.ws_connected = True
            log("[WS] Connected")
            return True
        except Exception as e:
            log("[WS] Connect failed: %s" % e)
            self.ws_connected = False
            return False

    async def ws_subscribe(self, tickers):
        if not self.ws_connected or not self.ws: return
        new = [t for t in tickers if t not in self.subscribed]
        if not new: return
        for i in range(0, len(new), WS_SUBSCRIBE_BATCH):
            batch = new[i:i + WS_SUBSCRIBE_BATCH]
            self.msg_id += 1
            try:
                await self.ws.send(json.dumps({"id": self.msg_id, "cmd": "subscribe",
                    "params": {"channels": ["orderbook_delta"], "market_tickers": batch}}))
                self.subscribed.update(batch)
                await asyncio.sleep(0.05)
            except Exception as e:
                log("[WS] Subscribe error: %s" % e)
        log("[WS] Subscribed %d new (total=%d)" % (len(new), len(self.subscribed)))

    def apply_snapshot(self, ticker, msg):
        book = Book()
        for level in msg.get("yes_dollars_fp", msg.get("yes", [])):
            if isinstance(level, list) and len(level) >= 2:
                price, size = round(float(level[0]) * 100), int(float(level[1]))
                if size > 0: book.bids[price] = size
        for level in msg.get("no_dollars_fp", msg.get("no", [])):
            if isinstance(level, list) and len(level) >= 2:
                no_price, size = round(float(level[0]) * 100), int(float(level[1]))
                if size > 0: book.asks[100 - no_price] = size
        recalc_bbo(book)
        book.updated = time.time()
        self.books[ticker] = book
        self._on_tick(ticker, book.best_bid, book.best_ask)

    def apply_delta(self, ticker, msg):
        if ticker not in self.books:
            self.books[ticker] = Book()
        book = self.books[ticker]
        price_raw = msg.get("price_dollars", msg.get("price"))
        delta = msg.get("delta_fp", msg.get("delta", 0))
        side = msg.get("side", "yes").lower()
        if price_raw is None: return
        price = round(float(price_raw) * 100)
        if side == "yes":
            book.bids[price] = book.bids.get(price, 0) + int(float(delta))
            if book.bids[price] <= 0: book.bids.pop(price, None)
        else:
            ap = 100 - price
            book.asks[ap] = book.asks.get(ap, 0) + int(float(delta))
            if book.asks[ap] <= 0: book.asks.pop(ap, None)
        recalc_bbo(book)
        book.updated = time.time()
        self._on_tick(ticker, book.best_bid, book.best_ask)

    async def ws_reader(self):
        while True:
            try:
                if not self.ws_connected or not self.ws:
                    await asyncio.sleep(1); continue
                raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
                msg = json.loads(raw)
                typ = msg.get("type", "")
                if typ == "orderbook_snapshot":
                    self.apply_snapshot(msg.get("msg", {}).get("market_ticker", ""), msg.get("msg", {}))
                elif typ == "orderbook_delta":
                    self.apply_delta(msg.get("msg", {}).get("market_ticker", ""), msg.get("msg", {}))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                log("[WS_ERR] %s" % e)
                self.ws_connected = False
                await asyncio.sleep(2)
                await self.ws_connect()
                if self.ws_connected and self.subscribed:
                    old = list(self.subscribed)
                    self.subscribed.clear()
                    await self.ws_subscribe(old)

    # ------------------------------------------------------------------
    # On every BBO tick
    # ------------------------------------------------------------------
    def _on_tick(self, ticker, bid, ask):
        """C2 fix (2026-04-11): this handler is now write-free on ms state.

        Previously mutated ~10 ms fields (match_started, match_play_start_ts,
        entry_phase, first_bid, etc.). Those writes raced with strategy_tick
        mutations across await boundaries: whenever strategy_tick awaited an
        API call, ws_reader could resume and run apply_delta → _on_tick →
        mutate the same ms dict fields. Hard-to-reproduce state corruption.

        All state transitions now live in strategy_tick._process_tick_events(),
        which reads book.best_bid/book.updated for each ms and makes the same
        decisions, but serialized with the rest of the strategy state machine.

        This handler only:
          1) writes to the BBO CSV log buffer
          2) is a no-op for tickers we aren't tracking
        """
        self._bbo_log(ticker, bid, ask)

    def _process_tick_events(self, event, ms, now):
        """C2 fix: state mutations formerly in _on_tick, now serialized inside
        strategy_tick iteration. Reads book.best_bid and ms fields, writes ms
        fields. Called once per ms per strategy_tick iteration."""
        # Pick the ticker to read book from: our_ticker if set, else any ticker
        # from the event (for pregame/match-start detection before PICK_SIDE).
        det_ticker = ms.our_ticker if ms.our_ticker else next(iter(ms.tickers), None)
        if not det_ticker:
            return
        book = self.books.get(det_ticker)
        if not book or book.updated <= 0:
            return
        bid = book.best_bid
        if bid <= 0:
            return

        # Match start detection — LOGGING ONLY, does not gate entry
        if not ms.match_started:
            if ms.created_ts and now - ms.created_ts < 30:
                return
            # Suppress false MATCH_START if >2h before estimated start
            if ms.scheduled_start_ts and now < ms.scheduled_start_ts - 7200:
                ms.last_bid = bid
                ms.last_ask = book.best_ask if book else 0
                return  # too early — bid changes are pregame noise
            if bid != ms.last_bid and ms.last_bid > 0:
                if now - ms.tick_window_start > 60:
                    ms.tick_window_start = now
                    ms.bid_change_count = 0
                ms.bid_change_count += 1
            ms.last_bid = bid
            ms.last_ask = book.best_ask if book else 0
            if ms.bid_change_count >= MATCH_START_TPM:
                ms.match_started = True
                ms.match_start_ts = now
                log("[MATCH_START] %s | %s | %d bid changes/min" % (
                    event, ms.category, ms.bid_change_count))

        # Match play detection: when price first moves 3c+ from entry
        if (ms.entry_phase in ("filled", "filled_unverified")
                and ms.match_play_start_ts == 0 and ms.entry_price > 0):
            if abs(bid - ms.entry_price) >= 3:
                ms.match_play_start_ts = now
                side = det_ticker.split("-")[-1]
                log("[PLAY_START] %s bid=%dc moved %+dc from entry=%dc" % (
                    side, bid, bid - ms.entry_price, ms.entry_price))

        # Alert: price dropped 15c+ from entry but DCA hasn't triggered
        if (ms.entry_phase in ("filled", "filled_unverified")
                and ms.dca_phase == "watching" and ms.entry_price > 0):
            drop = ms.entry_price - bid
            if drop >= 15 and not getattr(ms, '_drop_alert_logged', False):
                ms._drop_alert_logged = True
                side = det_ticker.split("-")[-1]
                alert("[DROP_NO_DCA] %s bid=%dc entry=%dc drop=%dc — DCA watching but not triggered" % (
                    side, bid, ms.entry_price, drop))

        # Price stability monitoring for SKIP_NO_SCHED fallback
        if ms.price_stability_phase == "monitoring" and bid > 0:
            if ms.first_bid == 0:
                ms.first_bid = bid
                ms.first_bid_ts = now
                _ask = book.best_ask if book else 0
                ms.first_ask = _ask
                ms.first_ask_ts = now
                ms.first_mid = (bid + _ask) / 2.0 if _ask > 0 else float(bid)
                ms.first_spread = _ask - bid if _ask > 0 else 0
            elif abs(bid - ms.first_bid) >= 5:
                is_fallback_sched = ms.schedule_source in (
                    "price_stability", "exp_exp-2.5h", "open_time+2h", "det_time-3h")
                if is_fallback_sched and ms.scheduled_start_ts and now < ms.scheduled_start_ts - 3600:
                    pass  # fallback: suppress until 1h before est_start
                elif not is_fallback_sched and ms.scheduled_start_ts and now < ms.scheduled_start_ts - 7200:
                    pass  # TE/ESPN: suppress until 2h before
                elif abs(bid - ms.first_bid) >= 10:
                    ms.price_stability_phase = "live_detected"
                    ms.entry_phase = "skipped"
                    side = det_ticker.split("-")[-1]
                    log("[LIVE_DETECTED] %s bid=%dc moved %+dc from first=%dc — blocking entry" % (
                        side, bid, bid - ms.first_bid, ms.first_bid))
                else:
                    side = det_ticker.split("-")[-1]
                    log("[LIVE_DRIFT] %s bid=%dc moved %+dc from first=%dc — monitoring (not blocking)" % (
                        side, bid, bid - ms.first_bid, ms.first_bid))
            elif now - ms.first_bid_ts >= 600 and ms.price_stability_phase == "monitoring":
                ms.price_stability_phase = "pregame"
                log("[PREGAME_STABLE] %s bid=%dc stable for %dm (first=%dc) — entry gate armed" % (
                    event, bid, int((now - ms.first_bid_ts) / 60), ms.first_bid))


    def _pick_side(self, ms):
        """Choose which ticker to trade based on category config.
        For 'leader' mode: compare BOTH sides, pick the one with HIGHER bid.
        Only enter if the leader's bid is within entry_min..entry_max."""
        cfg = ms.cfg
        # Collect bids for all sides
        sides = []
        for ticker in ms.tickers:
            book = self.books.get(ticker)
            if not book or book.updated < time.time() - 120:
                continue
            sides.append((ticker, book.best_bid))

        if not sides:
            return None, 0

        if cfg['side'] == 'leader':
            # Sort by bid descending — highest bid is the leader
            sides.sort(key=lambda x: -x[1])
            leader_ticker, leader_bid = sides[0]
            other_bid = sides[1][1] if len(sides) > 1 else (100 - leader_bid)
            # Leader must be >50c (actually the favorite) and within entry range
            if leader_bid > 50 and cfg['entry_min'] <= leader_bid <= cfg['entry_max']:
                side = leader_ticker.split("-")[-1]
                other = sides[1][0].split("-")[-1] if len(sides) > 1 else "?"
                log("[PICK_SIDE] %s=%dc (leader) vs %s=%dc | entry range %d-%dc" % (
                    side, leader_bid, other, other_bid, cfg['entry_min'], cfg['entry_max']))
                return leader_ticker, leader_bid
            return None, 0
        elif cfg['side'] == 'underdog':
            # Sort by bid ascending — lowest bid is the underdog
            sides.sort(key=lambda x: x[1])
            dog_ticker, dog_bid = sides[0]
            if dog_bid < 50 and cfg['entry_min'] <= dog_bid <= cfg['entry_max']:
                return dog_ticker, dog_bid
            return None, 0

        return None, 0

    # ------------------------------------------------------------------
    # Order placement
    # ------------------------------------------------------------------
    async def place_buy(self, ticker, price, size, label="BUY", post_only=True):
        side_name = ticker.split("-")[-1]

        # H11 fix: capital-cap check before placing. Estimate this order's cost
        # at the limit price × size. Skip the check for the race-guard-recovery
        # path (ENTRY_FULL / PARTIAL_FILL) since those don't actually place a
        # new order — they just close out an already-filled position.
        if self.current_balance > 0:
            _new_cost = (price * size) / 100.0  # cents → dollars
            if not self._check_capital_cap(_new_cost, label="%s %s %dct@%dc" % (label, side_name, size, price)):
                return ""

        # RACE GUARD: check position on EVERY buy (including DCA)
        # Read sizing from MatchState (per-match), NOT cfg (shared dict).
        # VERSION B DUAL MODE (2026-04-12): use find_ms_by_ticker which matches
        # by ms.our_ticker instead of the ticker_to_event → match_states[et]
        # path. The old path returned the PRIMARY ms for an event, which is
        # wrong when the ticker being bought belongs to the SECONDARY (dual)
        # ms — that ms has a composite key (event|direction) and the old lookup
        # couldn't find it.
        race_ms = self.find_ms_by_ticker(ticker)
        pos_path = "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&limit=1" % ticker
        pos_data = await api_get(self.session, self.ak, self.pk, pos_path, self.rl)
        if pos_data:
            pos_list = pos_data.get("market_positions", [])
            if pos_list:
                existing_qty = int(float(pos_list[0].get("position_fp", "0")))
                # Use per-match target sizing if available, else safe upper bound
                if race_ms and race_ms.target_size > 0:
                    max_allowed = race_ms.target_size + race_ms.target_dca_size
                else:
                    max_allowed = 120  # safe upper bound for doubled + DCA
                if existing_qty >= max_allowed:
                    log("[RACE_GUARD] %s pos=%d >= max %d — blocking" % (side_name, existing_qty, max_allowed))
                    return ""
                if existing_qty > 0 and label not in ("DCA",):
                    # VERSION B DUAL MODE: use find_ms_by_ticker for the same
                    # reason as above — the ms we want might be secondary.
                    ms = self.find_ms_by_ticker(ticker)
                    if ms is not None:
                        if ms.entry_phase in ("pregame", "seeking", "placed"):
                            if existing_qty >= size:
                                # Full entry achieved — mark filled, place sell
                                ms.entry_phase = "filled"
                                ms.entry_fill_ts = time.time()
                                ms.position_qty = existing_qty
                                ms.our_ticker = ticker
                                if ms.entry_price <= 0:
                                    ms.entry_price = price
                                _sp = self._sell_price_for(ms)
                                log("[ENTRY_FULL] %s pos=%d >= target %d — filled (sell@%dc)" % (
                                    side_name, existing_qty, size, _sp))
                                await self.place_sell(ticker, _sp, existing_qty, "SELL_AUTO")
                                return ""
                            else:
                                # Partial fill — place sell on what we have, keep buying remainder
                                ms.position_qty = existing_qty
                                ms.our_ticker = ticker
                                if ms.entry_price <= 0:
                                    ms.entry_price = price
                                _sp = self._sell_price_for(ms)
                                remaining = size - existing_qty
                                log("[PARTIAL_FILL] %s has %d of %d, buying remaining %d (sell@%dc)" % (
                                    side_name, existing_qty, size, remaining, _sp))
                                await self.place_sell(ticker, _sp, existing_qty, "SELL_AUTO")
                                size = remaining  # continue below to place buy for remainder
                    else:
                        return ""

        # Collect existing buys — cancel AFTER new order placed (no gap)
        orders_path = "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % ticker
        existing = await api_get(self.session, self.ak, self.pk, orders_path, self.rl)
        _old_buy_oids = []
        if existing:
            for o in existing.get("orders", []):
                if o.get("action") == "buy":
                    _old_buy_oids.append(o["order_id"])

        payload = {"ticker": ticker, "action": "buy", "side": "yes",
                   "count": size, "type": "limit",
                   "yes_price": price, "post_only": post_only,
                   "client_order_id": str(uuid.uuid4())}
        result = await api_post(self.session, self.ak, self.pk,
                                "/trade-api/v2/portfolio/orders", payload, self.rl)
        if result and result.get("_dead_market"):
            # VERSION B DUAL MODE: use find_ms_by_ticker so we update the
            # correct ms (primary OR secondary) for the dead ticker.
            ms = self.find_ms_by_ticker(ticker)
            if ms is not None:
                ms.entry_phase = "skipped"
                ms.dca_phase = "filled"  # block all further activity
                alert("[DEAD_MARKET] %s — market closed, stopping all activity" % side_name)
            return ""
        if not result or result.get("error"):
            log("  [%s_FAIL] %s at %dc" % (label, side_name, price))
            return ""
        oid = result.get("order", {}).get("order_id", "")
        log("[%s] %s at %dc %dct oid=%s" % (label, side_name, price, size, oid[:15]))
        # Cancel old buys AFTER new order confirmed — no gap
        for _ooid in _old_buy_oids:
            await api_delete(self.session, self.ak, self.pk,
                           "/trade-api/v2/portfolio/orders/%s" % _ooid, self.rl)
        return oid

    async def place_sell(self, ticker, price, size, label="SELL"):
        side_name = ticker.split("-")[-1]

        # Check for existing resting sells — never double-sell
        orders_path = "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % ticker
        existing_orders = await api_get(self.session, self.ak, self.pk, orders_path, self.rl)
        if existing_orders:
            existing_sell_qty = 0
            for o in existing_orders.get("orders", []):
                if o.get("action") == "sell":
                    existing_sell_qty += int(float(o.get("remaining_count_fp", "0") or "0"))
            if existing_sell_qty >= size:
                log("[SELL_EXISTS] %s already has %dct sell resting, skipping %s" % (
                    side_name, existing_sell_qty, label))
                return ""

        # Verify position
        pos_path = "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&limit=1" % ticker
        pos_data = await api_get(self.session, self.ak, self.pk, pos_path, self.rl)
        if pos_data:
            pos_list = pos_data.get("market_positions", [])
            if pos_list:
                actual = int(float(pos_list[0].get("position_fp", "0")))
                if actual > 0 and actual != size:
                    log("  [SELL_FIX] %s requested %d but actual=%d" % (side_name, size, actual))
                    size = actual
                elif actual <= 0:
                    log("[SELL_BLOCK] %s pos=%d, not placing %s" % (side_name, actual, label))
                    return ""

        payload = {"ticker": ticker, "action": "sell", "side": "yes",
                   "count": size, "type": "limit",
                   "yes_price": price, "post_only": True,
                   "client_order_id": str(uuid.uuid4())}
        result = await api_post(self.session, self.ak, self.pk,
                                "/trade-api/v2/portfolio/orders", payload, self.rl)
        # H4 fix (2026-04-11): mirror place_buy's dead-market handling. Previously
        # `place_sell` fell through the `{"_dead_market": True}` signal because
        # the dict is truthy and has no "error" key, so the bot silently dropped
        # dead-market sells. Position was left unhedged until audit_sells retried
        # (also failing). Now we detect and skip.
        if result and result.get("_dead_market"):
            log("[DEAD_MARKET_SELL] %s market closed, sell at %dc %dct not placed" % (
                side_name, price, size))
            ms = self.find_ms_by_ticker(ticker)
            if ms is not None and ms.dca_phase != "skipped":
                ms.dca_phase = "skipped"  # block DCA state machine on dead markets
            return ""
        if not result or result.get("error"):
            log("  [%s_FAIL] %s %dc %dct" % (label, side_name, price, size))
            return ""
        oid = result.get("order", {}).get("order_id", "")
        log("[%s] %s at %dc %dct oid=%s" % (label, side_name, price, size, oid[:15]))
        return oid

    # ------------------------------------------------------------------
    # Strategy tick — runs every loop iteration
    # ------------------------------------------------------------------
    async def strategy_tick(self):
        now = time.time()

        # VERSION B DUAL MODE fix (2026-04-12): snapshot keys at loop start.
        # The pick_side dual branch can add a secondary ms to match_states
        # mid-iteration (self.match_states[secondary_key] = ms2), which
        # triggers RuntimeError: dictionary changed size during iteration.
        # list() snapshots the (key, ms) pairs so new keys added during the
        # loop are processed on the NEXT strategy_tick iteration, not this one.
        for event, ms in list(self.match_states.items()):
            cfg = ms.cfg

            # C2 fix: process tick-driven state transitions (match_start,
            # play_start, drop alerts, price stability) serialized with the
            # rest of the state machine. Was previously in _on_tick where it
            # raced strategy_tick across await boundaries.
            self._process_tick_events(event, ms, now)

            # --- STALE BBO CHECK ---
            if ms.entry_phase in ("filled", "filled_unverified") and ms.our_ticker:
                book = self.books.get(ms.our_ticker)
                if book and book.updated > 0:
                    stale_sec = now - book.updated
                    if stale_sec > 300 and not getattr(ms, '_stale_bbo_alerted', False):
                        ms._stale_bbo_alerted = True
                        side = ms.our_ticker.split("-")[-1]
                        alert("[STALE_BBO] %s — no tick for %dm, DCA blind — resubscribing" % (side, int(stale_sec / 60)))
                        # Force resubscribe to recover stale ticker
                        if ms.our_ticker in self.subscribed:
                            self.subscribed.discard(ms.our_ticker)
                        # Also discard the other side (use tickers from current
                        # ms — in dual mode both ms share the same tickers set).
                        for t in ms.tickers:
                            self.subscribed.discard(t)
                    elif stale_sec <= 60:
                        ms._stale_bbo_alerted = False  # reset if ticks resume

            # --- AUTO TOP-UP: size up underfilled pregame positions ---
            # H7 fix: include filled_unverified so taker-race positions aren't excluded
            if ms.entry_phase in ("filled", "filled_unverified") and ms.our_ticker and ms.match_play_start_ts == 0:
                # TOP_UP overshoot fix (2026-04-12): belt-and-suspenders guard.
                # If audit_sells hasn't run yet but ms.position_qty has reached
                # target (via a completed prior TOP_UP fill), skip. The primary
                # fix is in audit_sells' POSITION_SYNC but this prevents a
                # narrow race where TOP_UP runs before audit_sells catches up.
                if ms.position_qty >= ms.target_size:
                    # Also clean up any stale topup order that's no longer needed
                    if ms.topup_order_id:
                        try:
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % ms.topup_order_id, self.rl)
                        except Exception:
                            pass
                        ms.topup_order_id = ""
                        log("[TOP_UP_DONE] %s pos=%d >= target=%d, cancelled lingering topup" % (
                            ms.our_ticker.split("-")[-1], ms.position_qty, ms.target_size))
                # Position filled but under target size, match still pregame
                elif ms.position_qty < ms.target_size and ms.position_qty > 0:
                    book = self.books.get(ms.our_ticker)
                    if book and book.best_bid > 0:
                        bid = book.best_bid
                        if abs(bid - ms.entry_price) <= 5:
                            need = ms.target_size - ms.position_qty
                            # Place or refresh top-up order every 60s
                            if not ms.topup_order_id or (now - ms.topup_placed_ts > PREGAME_REFRESH_SEC):
                                if ms.topup_order_id:
                                    await api_delete(self.session, self.ak, self.pk,
                                                   "/trade-api/v2/portfolio/orders/%s" % ms.topup_order_id, self.rl)
                                oid = await self.place_buy(ms.our_ticker, bid, need, "TOP_UP")
                                if oid:
                                    ms.topup_order_id = oid
                                    ms.topup_placed_ts = now
                                    side = ms.our_ticker.split("-")[-1]
                                    log("[TOP_UP] %s at %dc %dct (pos=%d target=%d)" % (
                                        side, bid, need, ms.position_qty, ms.target_size))

            # --- SCHEDULE DELAY SAFEGUARD ---
            # H7 fix: include filled_unverified
            if ms.scheduled_start_ts and ms.entry_phase in ("pregame", "filled", "filled_unverified"):
                hrs_past = (now - ms.scheduled_start_ts) / 3600
                if hrs_past >= 2 and ms.match_play_start_ts == 0:
                    if not getattr(ms, '_sched_delay_logged', False):
                        ms._sched_delay_logged = True
                        side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                        log("[SCHED_DELAY] %s — %.1fh past schedule, no play detected" % (side, hrs_past))
                        if ms.pregame_order_id:
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % ms.pregame_order_id, self.rl)
                            ms.pregame_order_id = ""
                        if ms.entry_phase == "pregame":
                            ms.entry_phase = "skipped"
                    if ms.entry_phase == "pregame":
                        continue

            # --- ENTRY LOGIC: Clock-based window ---
            # Window: scheduled_start - 30min to scheduled_start + 60min
            # Resting maker buy throughout window, refresh every 60s
            # No dependency on MATCH_START detection

            if ms.entry_phase == "waiting":
                if not ms.scheduled_start_ts:
                    continue
                # Price-stability tickers: require confirmed pregame before opening gate
                if ms.schedule_source == "price_stability":
                    if ms.price_stability_phase == "live_detected":
                        ms.entry_phase = "skipped"
                        continue
                    if ms.price_stability_phase != "pregame":
                        continue  # still monitoring, wait for 10 min stability
                if now > ms.latest_entry_ts:
                    ms.entry_phase = "skipped"
                    side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                    mins_past = int((now - ms.scheduled_start_ts) / 60)
                    log("[SKIP_LATE] %s | %dm past scheduled start, window closed" % (side or event, mins_past))
                    continue

                if now >= ms.earliest_entry_ts:
                    ms.entry_phase = "pregame"
                    mins_to = int((ms.scheduled_start_ts - now) / 60)
                    # Snapshot leader bid at gate open for pregame floor check
                    best_gate_bid = 0
                    for t in ms.tickers:
                        bk = self.books.get(t)
                        if bk and bk.best_bid > best_gate_bid:
                            best_gate_bid = bk.best_bid
                    ms.gate_bid = best_gate_bid
                    best_gate_ask = 100
                    for t in ms.tickers:
                        bk = self.books.get(t)
                        if bk and bk.best_ask < best_gate_ask:
                            best_gate_ask = bk.best_ask
                    ms.gate_ask = best_gate_ask
                    ms.gate_mid = (best_gate_bid + best_gate_ask) / 2.0
                    ms.gate_spread = best_gate_ask - best_gate_bid
                    log("[GATE_OPEN] %s | %dm before start | gate_bid=%dc gate_ask=%dc spread=%dc" % (event, max(mins_to, 0), best_gate_bid, best_gate_ask, ms.gate_spread))

            if ms.entry_phase == "pregame":
                # Short-circuit: if position already filled, skip pregame
                if ms.target_size > 0 and ms.position_qty >= ms.target_size:
                    ms.entry_phase = "filled"
                    ms.entry_fill_ts = time.time()
                    side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                    log("[ENTRY_FULL] %s pos=%d >= target %d — filled" % (side, ms.position_qty, ms.target_size))
                    db_log_entry(side, ms.entry_price, ms.position_qty, ms.category, event)
                    if ms.gate_bid >= 10 and ms.entry_price - ms.gate_bid >= 3:
                        alert("[PRICE_CHASE] %s fill=%dc gate_bid=%dc chased=%+dc" % (
                            side, ms.entry_price, ms.gate_bid, ms.entry_price - ms.gate_bid))
                    continue
                # Close window if past latest_entry_ts
                if now > ms.latest_entry_ts:
                    if ms.pregame_order_id:
                        await api_delete(self.session, self.ak, self.pk,
                                       "/trade-api/v2/portfolio/orders/%s" % ms.pregame_order_id, self.rl)
                    ms.entry_phase = "skipped"
                    side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                    log("[WINDOW_CLOSED] %s | entry window expired, no fill" % (side or event))
                    continue

                # Pick side if not chosen yet
                if not ms.our_ticker:
                    # ===== VERSION B DUAL MODE (2026-04-12) =====
                    # When BOTH directions have viable cells, open both positions.
                    # Primary side (higher in_sample_daily_pnl) keeps the simple
                    # event_ticker key; secondary side gets composite key
                    # f"{event_ticker}|{other_direction}". Each ms then runs the
                    # standard pregame → taker → DCA → settle pipeline independently.
                    # Capital cap (H11) naturally rate-limits the second side if
                    # balance is low — higher-EV side is always primary so it wins.
                    side_bids = []
                    for t in ms.tickers:
                        bk = self.books.get(t)
                        if bk and bk.best_bid > 0:
                            side_bids.append((t, bk.best_bid))
                    if len(side_bids) < 2:
                        continue
                    side_bids.sort(key=lambda x: -x[1])
                    leader_t, leader_bid = side_bids[0]
                    underdog_t, underdog_bid = side_bids[1]

                    # Look up both directions in the blueprint
                    leader_strat = get_strategy_v5(ms.category, 'leader', leader_bid)
                    underdog_strat = get_strategy_v5(ms.category, 'underdog', underdog_bid)

                    chosen_strat = None
                    chosen_ticker = None
                    chosen_bid = 0
                    chosen_direction = None
                    secondary_strat = None  # for DUAL mode
                    secondary_ticker = None
                    secondary_bid = 0
                    secondary_direction = None
                    if leader_strat and underdog_strat:
                        # DUAL: higher-EV becomes primary, other becomes secondary
                        if leader_strat['in_sample_daily_pnl'] >= underdog_strat['in_sample_daily_pnl']:
                            chosen_strat, chosen_ticker, chosen_bid, chosen_direction = (
                                leader_strat, leader_t, leader_bid, 'leader')
                            secondary_strat, secondary_ticker, secondary_bid, secondary_direction = (
                                underdog_strat, underdog_t, underdog_bid, 'underdog')
                        else:
                            chosen_strat, chosen_ticker, chosen_bid, chosen_direction = (
                                underdog_strat, underdog_t, underdog_bid, 'underdog')
                            secondary_strat, secondary_ticker, secondary_bid, secondary_direction = (
                                leader_strat, leader_t, leader_bid, 'leader')
                        log("[DUAL_MODE_ENTRY] %s both sides viable: L=%s(%dc,$%.2f/day) U=%s(%dc,$%.2f/day), primary=%s" % (
                            event, leader_t.split("-")[-1], leader_bid,
                            leader_strat['in_sample_daily_pnl'],
                            underdog_t.split("-")[-1], underdog_bid,
                            underdog_strat['in_sample_daily_pnl'],
                            chosen_direction))
                    elif leader_strat:
                        chosen_strat, chosen_ticker, chosen_bid, chosen_direction = (
                            leader_strat, leader_t, leader_bid, 'leader')
                        log("[SINGLE_MODE_ENTRY] %s only leader viable" % event)
                    elif underdog_strat:
                        chosen_strat, chosen_ticker, chosen_bid, chosen_direction = (
                            underdog_strat, underdog_t, underdog_bid, 'underdog')
                        log("[SINGLE_MODE_ENTRY] %s only underdog viable" % event)

                    if not chosen_strat:
                        log("[SKIP_NO_CELL] %s leader=%dc under=%dc — no viable cell in DEPLOYMENT" % (
                            event, leader_bid, underdog_bid))
                        ms.entry_phase = "skipped"
                        continue

                    # DUAL_MODE_ENTRY: create secondary ms for the other direction.
                    # Use composite key f"{event}|{secondary_direction}". Copy
                    # timing fields from primary ms so both enter in sync.
                    if secondary_strat is not None:
                        secondary_key = self.ms_key(event, secondary_direction)
                        if secondary_key not in self.match_states:
                            ms2 = MatchState(
                                event_ticker=event, category=ms.category, cfg=ms.cfg,
                                created_ts=time.time())
                            ms2.tickers = set(ms.tickers)
                            ms2.gate_bid = ms.gate_bid
                            ms2.gate_ask = ms.gate_ask
                            ms2.gate_mid = ms.gate_mid
                            ms2.gate_spread = ms.gate_spread
                            ms2.earliest_entry_ts = ms.earliest_entry_ts
                            ms2.scheduled_start_ts = ms.scheduled_start_ts
                            ms2.latest_entry_ts = ms.latest_entry_ts
                            ms2.schedule_source = ms.schedule_source
                            ms2.target_size = secondary_strat['entry_size']
                            ms2.target_dca_size = secondary_strat['dca_size']
                            ms2.dca_drop = secondary_strat['dca_drop'] if secondary_strat['dca_drop'] is not None else 15
                            ms2.exit_target = secondary_strat['exit_target'] if secondary_strat['exit_target'] is not None else 0
                            ms2.entry_lo_filter = secondary_strat['entry_lo']
                            ms2.entry_hi_filter = secondary_strat['entry_hi']
                            ms2.maker_bid_offset = secondary_strat.get('maker_bid_offset', 0)
                            ms2.direction = secondary_direction
                            ms2.strategy_loaded = True
                            ms2.use_blended_target = _bp_use_blended_target(
                                ms.category, secondary_direction,
                                secondary_strat['_tier_lo'], secondary_strat['_tier_hi'])
                            if secondary_strat['dca_drop'] is None:
                                ms2.dca_phase = "skipped"
                            ms2.our_ticker = secondary_ticker
                            ms2.pick_bid = secondary_bid
                            ms2.entry_phase = "pregame"
                            self.match_states[secondary_key] = ms2
                            _side2 = secondary_ticker.split("-")[-1]
                            log("[PICK_SIDE] %s=%dc (%s) [DUAL_SECONDARY] | strategy: cell %d-%d, sub %d-%d" % (
                                _side2, secondary_bid, secondary_direction,
                                secondary_strat['_tier_lo'], secondary_strat['_tier_hi'],
                                ms2.entry_lo_filter, ms2.entry_hi_filter))
                            log("[V5_SIZING] %s %dc | size=%dct dca=%dct drop=%dc exit_target=%s | sample_n=%d hit=%.0f%% [SECONDARY]" % (
                                _side2, secondary_bid, ms2.target_size, ms2.target_dca_size,
                                ms2.dca_drop, ('+%dc' % ms2.exit_target) if ms2.exit_target else 'hold99',
                                secondary_strat['in_sample_n'], secondary_strat['in_sample_hit_rate'] * 100))
                        # Gate-time dual succeeded → no further drift re-check needed
                        ms._dual_evaluated_final = True

                    # Apply the strategy to ms
                    ms.target_size = chosen_strat['entry_size']
                    ms.target_dca_size = chosen_strat['dca_size']
                    ms.dca_drop = chosen_strat['dca_drop'] if chosen_strat['dca_drop'] is not None else 15
                    ms.exit_target = chosen_strat['exit_target'] if chosen_strat['exit_target'] is not None else 0
                    ms.entry_lo_filter = chosen_strat['entry_lo']
                    ms.entry_hi_filter = chosen_strat['entry_hi']
                    ms.maker_bid_offset = chosen_strat.get('maker_bid_offset', 0)
                    ms.direction = chosen_direction
                    ms.strategy_loaded = True
                    # Strategy B per-cell flag — recompute target against blended_avg after DCA
                    ms.use_blended_target = _bp_use_blended_target(
                        ms.category, chosen_direction,
                        chosen_strat['_tier_lo'], chosen_strat['_tier_hi'])

                    # If no DCA in this cell, mark dca_phase=skipped to bypass cooling/placement
                    if chosen_strat['dca_drop'] is None:
                        ms.dca_phase = "skipped"

                    ms.our_ticker = chosen_ticker
                    ms.pick_bid = chosen_bid
                    _pick_bk = self.books.get(chosen_ticker)
                    ms.pick_ask = _pick_bk.best_ask if _pick_bk else 0
                    side_code = chosen_ticker.split("-")[-1]
                    other_code = (underdog_t if chosen_direction == 'leader' else leader_t).split("-")[-1]
                    other_bid = underdog_bid if chosen_direction == 'leader' else leader_bid
                    log("[PICK_SIDE] %s=%dc (%s) vs %s=%dc | strategy: cell %d-%d, sub %d-%d" % (
                        side_code, chosen_bid, chosen_direction, other_code, other_bid,
                        chosen_strat['_tier_lo'], chosen_strat['_tier_hi'],
                        ms.entry_lo_filter, ms.entry_hi_filter))
                    log("[V5_SIZING] %s %dc | size=%dct dca=%dct drop=%dc exit_target=%s | sample_n=%d hit=%.0f%%" % (
                        side_code, chosen_bid, ms.target_size, ms.target_dca_size,
                        ms.dca_drop, ('+%dc' % ms.exit_target) if ms.exit_target else 'hold99',
                        chosen_strat['in_sample_n'], chosen_strat['in_sample_hit_rate'] * 100))
                    edge_info = lookup_edge(event)
                    if edge_info:
                        side_code = chosen_ticker.split("-")[-1]
                        log("[EDGE] %s grade=%s edge_p1=%+.1fc edge_p2=%+.1fc pin=%.0f%%/%.0f%% | %s vs %s" % (
                            side_code, edge_info["grade"],
                            edge_info["edge_p1"], edge_info["edge_p2"],
                            edge_info["pin_p1"], edge_info["pin_p2"],
                            edge_info["p1"][:15], edge_info["p2"][:15]))

                # ===== DUAL-MODE DRIFT RE-CHECK (2026-04-13) =====
                # At gate_open, if only ONE side was viable (opposing side's
                # bid outside its sub-range by 1-2c), we end up SINGLE. But
                # pregame bids drift — the opposing side often enters its
                # sub-range over the next 30-60 min. This block re-evaluates
                # once per tick until the pregame window closes or the match
                # starts. If the opposing side drifts INTO its cell, create
                # the secondary ms on-the-fly.
                #
                # CRITICAL BUG FIX (OSTKIK incident, 00:14 UTC): this block
                # was using `event` (dict key) to build the secondary composite
                # key. For a SECONDARY ms (already composite-keyed), that
                # produced nested keys like "et|leader|underdog" and created
                # yet-another duplicate on every iteration — infinite cascade
                # → double-filled OST/KIK positions.
                #
                # Two fixes:
                #   1. Gate on PRIMARY ms only (skip if "|" already in event key)
                #   2. Use ms.event_ticker (never `event` loop var) for key building
                _is_primary = "|" not in event  # primary ms uses raw event_ticker key
                if (_is_primary and ms.our_ticker and ms.direction
                        and not getattr(ms, '_dual_evaluated_final', False)
                        and ms.match_play_start_ts == 0):
                    _ms_event = ms.event_ticker  # ALWAYS the raw event_ticker
                    # Hard cutoff on window close or match start
                    if now > ms.latest_entry_ts:
                        ms._dual_evaluated_final = True
                    else:
                        other_dir = 'underdog' if ms.direction == 'leader' else 'leader'
                        secondary_key = self.ms_key(_ms_event, other_dir)
                        if secondary_key in self.match_states:
                            ms._dual_evaluated_final = True
                        else:
                            # Find opposing ticker's current bid
                            other_ticker = None
                            other_bid = 0
                            for t in ms.tickers:
                                if t == ms.our_ticker:
                                    continue
                                bk = self.books.get(t)
                                if bk and bk.best_bid > 0:
                                    other_ticker = t
                                    other_bid = bk.best_bid
                                    break
                            if other_ticker and other_bid > 0:
                                other_strat = get_strategy_v5(ms.category, other_dir, other_bid)
                                if other_strat:
                                    # Drift-in detected — create secondary ms
                                    ms2 = MatchState(
                                        event_ticker=_ms_event, category=ms.category, cfg=ms.cfg,
                                        created_ts=time.time())
                                    ms2.tickers = set(ms.tickers)
                                    ms2.gate_bid = ms.gate_bid
                                    ms2.gate_ask = ms.gate_ask
                                    ms2.gate_mid = ms.gate_mid
                                    ms2.gate_spread = ms.gate_spread
                                    ms2.earliest_entry_ts = ms.earliest_entry_ts
                                    ms2.scheduled_start_ts = ms.scheduled_start_ts
                                    ms2.latest_entry_ts = ms.latest_entry_ts
                                    ms2.schedule_source = ms.schedule_source
                                    ms2.target_size = other_strat['entry_size']
                                    ms2.target_dca_size = other_strat['dca_size']
                                    ms2.dca_drop = other_strat['dca_drop'] if other_strat['dca_drop'] is not None else 15
                                    ms2.exit_target = other_strat['exit_target'] if other_strat['exit_target'] is not None else 0
                                    ms2.entry_lo_filter = other_strat['entry_lo']
                                    ms2.entry_hi_filter = other_strat['entry_hi']
                                    ms2.maker_bid_offset = other_strat.get('maker_bid_offset', 0)
                                    ms2.direction = other_dir
                                    ms2.strategy_loaded = True
                                    ms2.use_blended_target = _bp_use_blended_target(
                                        ms.category, other_dir,
                                        other_strat['_tier_lo'], other_strat['_tier_hi'])
                                    if other_strat['dca_drop'] is None:
                                        ms2.dca_phase = "skipped"
                                    ms2.our_ticker = other_ticker
                                    ms2.pick_bid = other_bid
                                    ms2.entry_phase = "pregame"
                                    # Secondary is also "final" — no further drift checks
                                    ms2._dual_evaluated_final = True
                                    self.match_states[secondary_key] = ms2
                                    _side_d = other_ticker.split("-")[-1]
                                    log("[DUAL_DRIFT_ENTRY] %s opposing side drifted into sub-range: %s=%dc (%s), $%.2f/day — creating secondary" % (
                                        _ms_event, _side_d, other_bid, other_dir,
                                        other_strat['in_sample_daily_pnl']))
                                    log("[PICK_SIDE] %s=%dc (%s) [DUAL_DRIFT] | strategy: cell %d-%d, sub %d-%d" % (
                                        _side_d, other_bid, other_dir,
                                        other_strat['_tier_lo'], other_strat['_tier_hi'],
                                        ms2.entry_lo_filter, ms2.entry_hi_filter))
                                    log("[V5_SIZING] %s %dc | size=%dct dca=%dct drop=%dc exit_target=%s | sample_n=%d hit=%.0f%% [DRIFT]" % (
                                        _side_d, other_bid, ms2.target_size, ms2.target_dca_size,
                                        ms2.dca_drop, ('+%dc' % ms2.exit_target) if ms2.exit_target else 'hold99',
                                        other_strat['in_sample_n'], other_strat['in_sample_hit_rate'] * 100))
                                    ms._dual_evaluated_final = True

                book = self.books.get(ms.our_ticker)
                if not book:
                    continue
                bid = book.best_bid

                # Track pick_bid for logging (no re-pick — too dangerous)
                if ms.pick_bid > 0 and abs(bid - ms.pick_bid) > 5:
                    ms.pick_bid = bid  # update silently, continue with current side
                spread = book.best_ask - bid

                # V5: legacy entry_min/entry_max (55-90) check removed — replaced
                # by direction-aware bid sanity (>50 leader, <50 underdog) and the
                # per-cell sub-range filter below.

                if spread > 5:
                    continue

                # Update pick_bid to track current valid bid
                ms.pick_bid = bid
                # V5: direction-aware safety check using ms.direction (not cfg['side'])
                if ms.direction == 'leader' and bid <= 50:
                    side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                    log("[SIDE_FLIP] %s bid=%dc dropped below 50c (leader) — skipping tick" % (side, bid))
                    continue
                if ms.direction == 'underdog' and bid >= 50:
                    side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                    log("[SIDE_FLIP] %s bid=%dc rose above 50c (underdog) — skipping tick" % (side, bid))
                    continue
                # V5 (Bug D fix 2026-04-11): sub-range filter check is deferred
                # until AFTER buy_price is computed (was: bid-based here). The
                # old check allowed a +1/+2c drift past the sub-range high because
                # the order is placed at bid+1 (or bid+2 after 30min gate_age),
                # not at bid. See the post-restart AND (57-59) case that filled
                # at 61c.  Keep only a direction sanity guard here.

                # Early start detection: if price moved 5c+ from first_bid, match started early
                if ms.first_bid > 0 and abs(bid - ms.first_bid) >= 5 and not hasattr(ms, '_early_start_logged'):
                    ms._early_start_logged = True
                    log("[EARLY_START] %s bid=%dc first_bid=%dc delta=%+dc — match started before schedule" % (
                        ms.our_ticker.split("-")[-1] if ms.our_ticker else event,
                        bid, ms.first_bid, bid - ms.first_bid))

                # Pregame fill strategy:
                # T-60 to T-30: bid+1c maker (free, might fill)
                # T-30 to T-10: bid+2c maker (more aggressive, still free)
                # T-10 to T-0:  cross ask as TAKER (guaranteed fill, ~1.4c/ct fee)
                # After start:  STOP — let check_fills handle position detection
                # Cap: never above gate_bid + 5c
                ask = book.best_ask
                max_price = (ms.gate_bid + 5) if ms.gate_bid >= 10 else cfg['entry_max']
                # Check actual match status: TE live data > schedule estimate
                te_live, _, _ = is_match_live_te(event)
                if te_live is True:
                    match_started = True
                elif te_live is False and ms.scheduled_start_ts and now < ms.scheduled_start_ts + 1800:
                    match_started = False  # TE says not live, trust it within 30min of schedule
                else:
                    match_started = ms.scheduled_start_ts and now >= ms.scheduled_start_ts

                if match_started:
                    # Match has started — don't place new orders or refresh
                    # Cancel resting order if price ran away (cap exceeded)
                    if ms.pregame_order_id and bid > max_price:
                        await api_delete(self.session, self.ak, self.pk,
                                       "/trade-api/v2/portfolio/orders/%s" % ms.pregame_order_id, self.rl)
                        ms.pregame_order_id = ""
                        side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                        log("[FREEZE_CANCEL] %s bid=%dc > max=%dc — cancelled post-start" % (side, bid, max_price))
                    continue  # skip order placement but check_fills still runs separately

                gate_age = now - ms.earliest_entry_ts if ms.earliest_entry_ts else 0
                time_to_start = ms.scheduled_start_ts - now if ms.scheduled_start_ts else 9999

                # --- TAKER PHASE: T-10min, cross the ask for guaranteed fill ---
                if 0 < time_to_start <= TAKER_TRIGGER_BEFORE and ask > 0 and ask <= cfg["entry_max"]:
                    if not getattr(ms, '_taker_attempted', False):
                        ms._taker_attempted = True
                        # Cancel any resting maker order first
                        if ms.pregame_order_id:
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % ms.pregame_order_id, self.rl)
                            ms.pregame_order_id = ""
                        taker_price = min(ask, max_price, cfg['entry_max'])
                        side = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                        log("[TAKER_CROSS] %s at %dc (ask) %dct | T-%.0fm | maker was %dc" % (
                            side, taker_price, ms.target_size,
                            time_to_start / 60, ms.pregame_price or 0))
                        oid = await self.place_buy(ms.our_ticker, taker_price, ms.target_size,
                                                   "TAKER", post_only=False)
                        if oid:
                            ms.pregame_order_id = oid
                            ms.pregame_price = taker_price
                            ms.pregame_placed_ts = now
                            ms.entry_price = taker_price
                            # Bug B fix: compute and cache the auto-sell price
                            # immediately (was defaulting to 99c dataclass value,
                            # causing DCA_FILL logs to show wrong prev_sell_price
                            # and the sell-fill detector to log wrong realized px).
                            ms.auto_sell_price = self._sell_price_for(ms)
                            # Taker fills immediately — transition to filled for DCA
                            ms.entry_phase = "filled"
                            ms.entry_fill_ts = now
                            # Bug A fix: retry position poll up to 3x with 500ms
                            # backoff. Kalshi sometimes returns pos=0 for a brief
                            # window right after a taker submit, which used to
                            # leave ms.position_qty=0 permanently and break PnL.
                            ms.position_qty = 0
                            retries_used = 0
                            for _attempt in range(3):
                                try:
                                    _pos_path = "/trade-api/v2/portfolio/positions?ticker=%s&limit=1" % ms.our_ticker
                                    _pos_data = await api_get(self.session, self.ak, self.pk, _pos_path, self.rl)
                                    _pos_list = (_pos_data or {}).get("market_positions", []) or []
                                    if _pos_list:
                                        _qty_raw = int(float(_pos_list[0].get("position_fp", "0")))
                                        if _qty_raw > 0:
                                            ms.position_qty = _qty_raw
                                            break
                                except Exception:
                                    pass
                                retries_used = _attempt + 1
                                await asyncio.sleep(0.5)
                            if ms.position_qty == 0:
                                # Still no position after retries — assume the
                                # taker filled (we crossed the ask) and flag for
                                # audit verification on the next cycle.
                                ms.position_qty = ms.target_size
                                ms.entry_phase = "filled_unverified"
                                log("[TAKER_RACE_RECOVERY] %s no position after %d retries, assuming %dct filled, flagged for verify" % (
                                    side, retries_used, ms.target_size))
                            elif retries_used > 0:
                                log("[TAKER_RACE_RECOVERY] %s position=%dct confirmed after %d retries" % (
                                    side, ms.position_qty, retries_used))
                            log("[TAKER_FILLED] %s entry_phase=%s pos=%d, DCA armed" % (
                                side, ms.entry_phase, ms.position_qty))
                            # Bug B fix: place the auto-sell here instead of
                            # waiting for audit_sells to notice the gap. Cancel
                            # any stray sell order first, then place fresh.
                            if ms.position_qty > 0:
                                try:
                                    _orders_path = "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % ms.our_ticker
                                    _existing = await api_get(self.session, self.ak, self.pk, _orders_path, self.rl)
                                    if _existing:
                                        for _o in _existing.get("orders", []):
                                            if _o.get("action") == "sell":
                                                await api_delete(self.session, self.ak, self.pk,
                                                               "/trade-api/v2/portfolio/orders/%s" % _o["order_id"], self.rl)
                                except Exception:
                                    pass
                                _sell_tag = "AUTO_SELL" if ms.auto_sell_price < 99 else "SELL_99"
                                _sell_oid = await self.place_sell(
                                    ms.our_ticker, ms.auto_sell_price, ms.position_qty, _sell_tag)
                                ms.sell_order_id = _sell_oid
                                log("[TAKER_AUTOSELL] %s at %dc %dct (%s)" % (
                                    side, ms.auto_sell_price, ms.position_qty, _sell_tag))
                    continue

                # --- MAKER PHASE: direction-aware placement ---
                # Leaders: ask-1 for fast fill (ride upward drift)
                # Underdogs: bid+1 (+2 after 30min) + per-cell offset (patient fill)
                offset = getattr(ms, 'maker_bid_offset', 0)
                if ms.direction == 'leader':
                    buy_price = min(ask - 1, max_price, cfg['entry_max'])
                else:
                    if gate_age > 1800:
                        buy_price = min(bid + 2 + offset, ask - 1, max_price, cfg['entry_max'])
                    else:
                        buy_price = min(bid + 1 + offset, ask - 1, max_price, cfg['entry_max'])
                buy_price = max(1, buy_price)

                # Ensure post_only: buy_price must be < ask
                if buy_price >= ask:
                    buy_price = ask - 1 if ask > 1 else 1

                # Bug D fix: sub-range filter applied to buy_price (not bid).
                # This is the actual price we'd place at — if it drifts above
                # the cell's entry_hi, skip the placement for this tick.
                if ms.entry_lo_filter > 0 and not (ms.entry_lo_filter <= buy_price <= ms.entry_hi_filter):
                    if not getattr(ms, '_drift_logged', False):
                        side_d = ms.our_ticker.split("-")[-1] if ms.our_ticker else event
                        log("[SKIP_DRIFT] %s buy_price=%dc outside sub %d-%d (bid=%dc)" % (
                            side_d, buy_price, ms.entry_lo_filter, ms.entry_hi_filter, bid))
                        ms._drift_logged = True
                    continue

                # If we got back within range after previously drifting, reset the log flag
                if getattr(ms, '_drift_logged', False):
                    ms._drift_logged = False

                # Refresh every PREGAME_REFRESH_SEC
                # Place-first, cancel-after: new order rests before old is removed
                if not ms.pregame_order_id or (now - ms.pregame_placed_ts > PREGAME_REFRESH_SEC):
                    if buy_price != ms.pregame_price or not ms.pregame_order_id:
                        old_oid = ms.pregame_order_id
                        oid = await self.place_buy(ms.our_ticker, buy_price, ms.target_size, "PREGAME",
                                                   post_only=True)
                        if oid:
                            ms.pregame_order_id = oid
                            ms.pregame_price = buy_price
                            ms.pregame_placed_ts = now
                            ms.entry_price = buy_price
                            # Cancel old order AFTER new one is confirmed
                            if old_oid:
                                await api_delete(self.session, self.ak, self.pk,
                                               "/trade-api/v2/portfolio/orders/%s" % old_oid, self.rl)
                        else:
                            # New order failed — keep old order alive
                            ms.pregame_placed_ts = now
                    elif ms.pregame_order_id:
                        # Same price, just reset refresh timer
                        ms.pregame_placed_ts = now

            # --- DCA LOGIC: 3-phase (watching → cooling → placing) ---
            # Phase 1: WATCHING — wait for price to drop dca_drop below entry
            elif ms.entry_phase in ("filled", "filled_unverified") and ms.dca_phase == "watching":
                # Defensive guard: don't DCA a position that's already been closed
                # (auto-sell fill detection can race the watcher; if we missed the
                # Kalshi bulk update, position_qty might still be stale here, but
                # once audit_sells catches the closure and zeros the qty, this
                # guard blocks any further DCA attempts).
                if ms.position_qty <= 0:
                    ms.dca_phase = "skipped"
                    continue
                book = self.books.get(ms.our_ticker)
                if not book: continue
                bid = book.best_bid
                # Skip DCA on settled matches (bid=0 or 1c = match over)
                if bid <= 1:
                    continue
                drop = ms.entry_price - bid
                if drop > 35:
                    if not getattr(ms, '_deep_skip_logged', False):
                        side = ms.our_ticker.split("-")[-1]
                        log("[DCA_SKIP_DEEP] %s drop=%dc > 35c cap, skipping DCA" % (side, drop))
                        ms._deep_skip_logged = True
                    continue
                # V5: per-cell DCA drop (was global cfg['dca_drop'])
                cell_dca_drop = ms.dca_drop if ms.dca_drop > 0 else cfg.get('dca_drop', 15)
                if drop >= cell_dca_drop:
                    ms.dca_phase = "cooling"
                    ms.dca_cool_start = now
                    ms.dca_cool_trigger_bid = bid
                    ms.dca_cool_extensions = 0
                    ms.dca_stable_since = 0.0
                    ms.dca_last_stable_bid = 0
                    side = ms.our_ticker.split("-")[-1]
                    cool_time = DCA_COOL_SEC
                    ms.dca_cool_duration = cool_time
                    mins_since = (now - ms.entry_fill_ts) / 60 if ms.entry_fill_ts else 999
                    log("[DCA_COOL] %s triggered at %dc (entry=%dc drop=%dc thresh=%dc), waiting %ds (%dm into match)" % (
                        side, bid, ms.entry_price, drop, cell_dca_drop, cool_time, int(mins_since)))
                    save_dca_state(self.match_states)

            # Phase 2: COOLING — 5-min wait, cancel if price recovers
            elif ms.dca_phase == "cooling":
                book = self.books.get(ms.our_ticker)
                if not book: continue
                bid = book.best_bid
                # Skip on settled matches
                if bid <= 1:
                    ms.dca_phase = "skipped"
                    continue
                side = ms.our_ticker.split("-")[-1]

                # Cancel cooling if price recovers above entry - DCA_COOL_RECOVERY
                recovery_threshold = ms.entry_price - DCA_COOL_RECOVERY
                if bid > recovery_threshold:
                    ms.dca_phase = "watching"
                    log("[DCA_COOL_CANCEL] %s recovered to %dc (threshold=%dc) during wait" % (
                        side, bid, recovery_threshold))
                    save_dca_state(self.match_states)
                elif now - ms.dca_cool_start >= getattr(ms, 'dca_cool_duration', DCA_COOL_SEC):
                    cool_used = getattr(ms, 'dca_cool_duration', DCA_COOL_SEC)
                    drop = ms.entry_price - bid
                    # V5: per-cell DCA drop
                    cell_dca_drop = ms.dca_drop if ms.dca_drop > 0 else cfg.get('dca_drop', 15)
                    if drop < cell_dca_drop:
                        ms.dca_phase = "watching"
                        ms.dca_cool_extensions = 0
                        log("[DCA_COOL_CANCEL] %s drop=%dc < %dc after wait, back to watching" % (
                            side, drop, cell_dca_drop))
                    else:
                        # Defensive guard: if the position was closed via auto-sell
                        # during the 60s cooldown, don't place a phantom DCA buy.
                        if ms.position_qty <= 0:
                            ms.dca_phase = "skipped"
                            log("[DCA_COOL_ABORT] %s position_qty=0 — auto-sell closed during cool, skipping DCA" % side)
                            continue
                        # 60s elapsed, still below threshold — place at bid
                        dca_target = max(1, bid)
                        oid = await self.place_buy(ms.our_ticker, dca_target, ms.target_dca_size, "DCA")
                        if oid:
                            ms.dca_order_id = oid
                            ms.dca_price = dca_target
                            ms.dca_placed_ts = now
                            ms.dca_phase = "placed"
                            log("[DCA] %s resting at %dc (bid=%dc entry=%dc drop=%dc) after %ds cool" % (
                                side, dca_target, bid, ms.entry_price, drop, cool_used))
                        else:
                            ms.dca_phase = "watching"

            # Phase 3: PLACED — resting buy with 5-min window, follow dip down
            elif ms.dca_phase == "placed":
                # ----- 5-min expiry path: cancel and re-cool or reset -----
                if now - ms.dca_placed_ts > 300:
                    await api_delete(self.session, self.ak, self.pk,
                                   "/trade-api/v2/portfolio/orders/%s" % ms.dca_order_id, self.rl)
                    ms.dca_order_id = ""
                    book = self.books.get(ms.our_ticker)
                    current_bid = book.best_bid if book else 0
                    side = ms.our_ticker.split("-")[-1]
                    cell_dca_drop_retry = ms.dca_drop if ms.dca_drop > 0 else cfg.get('dca_drop', 15)
                    if current_bid > 0 and (ms.entry_price - current_bid) >= cell_dca_drop_retry:
                        ms.dca_phase = "cooling"
                        ms.dca_cool_start = now
                        ms.dca_cool_trigger_bid = current_bid
                        ms.dca_cool_duration = DCA_COOL_SEC
                        log("[DCA_RETRY] %s 5min expired, bid=%dc still %dc below entry — re-cooling" % (
                            side, current_bid, ms.entry_price - current_bid))
                        save_dca_state(self.match_states)
                    else:
                        ms.dca_phase = "watching"
                        log("[DCA_RESET] %s 5min expired, bid=%dc recovered — back to watching" % (
                            side, current_bid))
                    continue  # expired path fully handles this tick, skip refresh/alert below

                # ----- H6 fix (2026-04-11): DCA price refresh — UNCONDITIONAL -----
                # Previously nested inside `else: # stall-alerted` branch, so this
                # dead-code never ran. Grep [DCA_REFRESH] tennis_v5.log prior to this
                # fix → 0 matches. The refresh should follow the dip on every tick
                # while dca_phase=="placed", not only after the 10-min stall alert.
                book = self.books.get(ms.our_ticker)
                if book and ms.dca_order_id:
                    new_target = max(1, book.best_bid)
                    if new_target < ms.dca_price - 2:
                        old_oid = ms.dca_order_id
                        old_price = ms.dca_price
                        await api_delete(self.session, self.ak, self.pk,
                                       "/trade-api/v2/portfolio/orders/%s" % old_oid, self.rl)
                        oid = await self.place_buy(ms.our_ticker, new_target, ms.target_dca_size, "DCA")
                        if oid:
                            ms.dca_order_id = oid
                            ms.dca_price = new_target
                            ms.dca_placed_ts = now  # reset 5-min window to the new order
                            log("[DCA_REFRESH] %s %dc->%dc (bid=%dc)" % (
                                ms.our_ticker.split("-")[-1], old_price, new_target, book.best_bid))

                # ----- Stall alert: DCA placed for >10min without fill -----
                # Independent of refresh (refresh resets dca_placed_ts so this
                # effectively only fires if the refresh hasn't moved the order
                # for 10+ minutes, which is rare but possible on flat markets).
                if not getattr(ms, '_dca_stall_alerted', False):
                    if ms.dca_placed_ts and now - ms.dca_placed_ts > 600:
                        ms._dca_stall_alerted = True
                        side = ms.our_ticker.split("-")[-1]
                        book = self.books.get(ms.our_ticker)
                        current = book.best_bid if book else 0
                        alert("[DCA_STALL] %s placed=%dc current=%dc — 10min without fill" % (
                            side, ms.dca_price, current))

    # ------------------------------------------------------------------
    # Fill detection
    # ------------------------------------------------------------------
    async def check_fills(self):
        for event, ms in self.match_states.items():
            if not ms.our_ticker:
                continue

            # Check position
            if ms.entry_phase in ("pregame", "placed") or ms.dca_phase == "placed":
                path = "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&limit=1" % ms.our_ticker
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data: continue
                positions = data.get("market_positions", [])
                if not positions: continue
                qty = int(float(positions[0].get("position_fp", "0")))

                if qty > 0 and ms.entry_phase == "pregame":
                    side = ms.our_ticker.split("-")[-1]
                    # DAN-19ct fix (2026-04-12): cancel any lingering pregame
                    # maker buy remainder BEFORE clearing pregame_order_id.
                    # Previously the code cleared the ID without cancelling,
                    # leaving the remaining buy-side quantity resting on
                    # Kalshi. When the market swept aggressively, that stale
                    # order filled in addition to whatever TOP_UP placed —
                    # DAN ended up with 19ct (1 pregame + 9 orphaned pregame
                    # remainder + 9 topup) vs 10ct target. Mirrors the H5
                    # DCA_PARTIAL_CANCEL logic.
                    _pregame_target = getattr(ms, 'target_size', 0)
                    if ms.pregame_order_id and qty < _pregame_target:
                        try:
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % ms.pregame_order_id, self.rl)
                            log("[PREGAME_PARTIAL_CANCEL] %s filled %dct of %dct, cancelling %dct remainder | %s" % (
                                side, qty, _pregame_target, _pregame_target - qty, ms.category))
                        except Exception as _e:
                            log("[PREGAME_CANCEL_FAIL] %s err=%s" % (side, str(_e)[:80]))
                    ms.entry_phase = "filled"
                    ms.entry_fill_ts = time.time()
                    ms.position_qty = qty
                    ms.pregame_order_id = ""
                    sell_price = self._sell_price_for(ms)
                    ms.auto_sell_price = sell_price
                    log("[PREGAME_FILL] %s %dct at %dc → sell at %dc | %s" % (
                        side, qty, ms.entry_price, sell_price, ms.category))

                    # Place auto-sell (entry+exit_target or 99 if hold-to-settle)
                    orders_path = "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % ms.our_ticker
                    existing = await api_get(self.session, self.ak, self.pk, orders_path, self.rl)
                    if existing:
                        for o in existing.get("orders", []):
                            if o.get("action") == "sell":
                                await api_delete(self.session, self.ak, self.pk,
                                               "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                    oid = await self.place_sell(ms.our_ticker, sell_price, qty,
                                                "AUTO_SELL" if sell_price < 99 else "SELL_99")
                    ms.sell_order_id = oid

                if qty > 0 and ms.entry_phase == "placed":
                    side = ms.our_ticker.split("-")[-1]
                    # DAN-19ct fix (2026-04-12): cancel lingering placed-phase
                    # entry remainder before clearing entry_order_id. Same
                    # rationale as the PREGAME_FILL path above — orphaned
                    # buy orders can fill in bulk when the market sweeps.
                    _entry_target = getattr(ms, 'target_size', 0)
                    if ms.entry_order_id and qty < _entry_target:
                        try:
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % ms.entry_order_id, self.rl)
                            log("[ENTRY_PARTIAL_CANCEL] %s filled %dct of %dct, cancelling %dct remainder | %s" % (
                                side, qty, _entry_target, _entry_target - qty, ms.category))
                        except Exception as _e:
                            log("[ENTRY_CANCEL_FAIL] %s err=%s" % (side, str(_e)[:80]))
                    ms.entry_phase = "filled"
                    ms.entry_fill_ts = time.time()
                    ms.position_qty = qty
                    ms.entry_order_id = ""
                    sell_price = self._sell_price_for(ms)
                    ms.auto_sell_price = sell_price
                    log("[ENTRY_FILL] %s %dct at %dc → sell at %dc | %s" % (
                        side, qty, ms.entry_price, sell_price, ms.category))

                    # Place auto-sell
                    orders_path = "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % ms.our_ticker
                    existing = await api_get(self.session, self.ak, self.pk, orders_path, self.rl)
                    if existing:
                        for o in existing.get("orders", []):
                            if o.get("action") == "sell":
                                await api_delete(self.session, self.ak, self.pk,
                                               "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                    oid = await self.place_sell(ms.our_ticker, sell_price, qty,
                                                "AUTO_SELL" if sell_price < 99 else "SELL_99")
                    ms.sell_order_id = oid

                if qty > ms.position_qty and ms.dca_phase == "placed":
                    # H5 fix (2026-04-11): cancel the DCA order remainder when
                    # marking phase=filled. Previously, a partial DCA fill would
                    # flip dca_phase → "filled" and the gate at line 2060 would
                    # stop polling, so any further fills on the still-resting
                    # remainder went undetected. ms.position_qty would become
                    # stale and the sell order would be undersized.
                    if ms.dca_order_id:
                        _dca_size_expected = getattr(ms, 'target_dca_size', 0)
                        _dca_qty_filled = qty - ms.position_qty
                        if _dca_size_expected > 0 and _dca_qty_filled < _dca_size_expected:
                            try:
                                await api_delete(self.session, self.ak, self.pk,
                                               "/trade-api/v2/portfolio/orders/%s" % ms.dca_order_id, self.rl)
                                log("[DCA_PARTIAL_CANCEL] %s filled %d of %d, cancelling remainder" % (
                                    ms.our_ticker.split("-")[-1], _dca_qty_filled, _dca_size_expected))
                            except Exception:
                                pass
                        ms.dca_order_id = ""
                    ms.dca_phase = "filled"
                    dca_qty = qty - ms.position_qty
                    old_qty = ms.position_qty
                    ms.position_qty = qty
                    if old_qty > 0 and ms.entry_price > 0 and ms.dca_price > 0:
                        ms.dca_fill_price = ms.dca_price
                        ms.dca_fill_size = dca_qty
                        blended = (old_qty * ms.entry_price + dca_qty * ms.dca_price) / qty
                        ms.blended_avg = int(round(blended))
                    else:
                        ms.blended_avg = ms.entry_price
                        ms.dca_fill_price = ms.dca_price
                        ms.dca_fill_size = dca_qty
                    side = ms.our_ticker.split("-")[-1]
                    # V5 Strategy B (per-cell flag): if use_blended_target, recompute the
                    # auto-sell at blended_avg + exit_target (lower target, easier to hit).
                    # Otherwise keep original entry+exit_target (Strategy A, deployed default).
                    prev_sell_price = ms.auto_sell_price if ms.auto_sell_price > 0 else self._sell_price_for(ms)
                    if (ms.use_blended_target and ms.exit_target > 0
                            and ms.blended_avg > 0):
                        sell_price = min(99, ms.blended_avg + ms.exit_target)
                        ms.auto_sell_price = sell_price  # cache new target
                        target_mode = "BLENDED_B"
                    else:
                        sell_price = prev_sell_price
                        target_mode = "ORIG_A"
                    log("[DCA_FILL] %s %dct at %dc (entry=%dc, blended=%dc) → sell at %dc [%s, was %dc] | %s" % (
                        side, qty, ms.dca_price, ms.entry_price, ms.blended_avg,
                        sell_price, target_mode, prev_sell_price, ms.category))

                    # Update sell limit to cover full position at the SAME price
                    orders_path = "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % ms.our_ticker
                    existing = await api_get(self.session, self.ak, self.pk, orders_path, self.rl)
                    if existing:
                        for o in existing.get("orders", []):
                            if o.get("action") == "sell":
                                await api_delete(self.session, self.ak, self.pk,
                                               "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                    oid = await self.place_sell(ms.our_ticker, sell_price, qty,
                                                "AUTO_SELL_DCA" if sell_price < 99 else "SELL_99_DCA")
                    ms.sell_order_id = oid

    # ------------------------------------------------------------------
    # Sell audit
    # ------------------------------------------------------------------
    async def audit_sells(self):
        pos_data = await api_get(self.session, self.ak, self.pk,
                                "/trade-api/v2/portfolio/positions", self.rl)
        if not pos_data: return

        orders_data = await api_get(self.session, self.ak, self.pk,
                                   "/trade-api/v2/portfolio/orders?status=resting", self.rl)
        if not orders_data: return

        positions = {}
        # Full map including zeroed positions — used for sell-fill detection below.
        # Kalshi sometimes omits positions with qty=0 from the response; we treat
        # any match_state ticker missing from this map as qty=0.
        all_positions_qty = {}
        for p in pos_data.get("market_positions", []):
            ticker = p.get("ticker", "")
            qty = int(float(p.get("position_fp", "0")))
            all_positions_qty[ticker] = qty
            if qty > 0 and self.get_category(ticker)[0]:
                positions[ticker] = qty

        # ------------------------------------------------------------------
        # SELL-FILL DETECTION (2026-04-11 fix) — sync ms.position_qty with
        # Kalshi whenever a resting auto-sell/SELL_99 maker has filled. Without
        # this the DCA state machine keeps firing against a phantom position.
        # See tennis_v5.log 2026-04-11 GAU/BEL incidents.
        # ------------------------------------------------------------------
        for et, ms in list(self.match_states.items()):
            if not ms.our_ticker:
                continue
            if ms.entry_phase not in ("filled", "filled_unverified"):
                continue
            # Bug A fix: promote filled_unverified → filled once Kalshi shows
            # a real position (the taker race resolved). If Kalshi still shows
            # 0, leave unverified and let the audit try again next cycle.
            if ms.entry_phase == "filled_unverified":
                _live = all_positions_qty.get(ms.our_ticker, 0)
                if _live > 0:
                    ms.position_qty = _live
                    ms.entry_phase = "filled"
                    side_u = ms.our_ticker.split("-")[-1]
                    log("[TAKER_VERIFIED] %s filled_unverified → filled, pos=%d | %s" % (
                        side_u, _live, ms.category))
                else:
                    continue  # still no visible position, wait another cycle
            if ms.dca_phase not in ("watching", "cooling"):
                continue
            if ms.position_qty <= 0:
                continue
            live_qty = all_positions_qty.get(ms.our_ticker, 0)
            if live_qty == ms.position_qty:
                continue  # no change, nothing to sync
            if live_qty > ms.position_qty:
                # TOP_UP overshoot fix (2026-04-12): sync ms.position_qty on
                # INCREASES too, not just decreases. Root cause of MAG 13ct
                # over-fill: pregame partial-fill left ms.position_qty=7 while
                # Kalshi pos climbed to 10 then 13 via repeated TOP_UPs. Without
                # this sync, TOP_UP kept recalculating `need = target - 7 = 3`
                # and placing another 3ct buy. audit_sells now becomes source
                # of truth for ms.position_qty on both directions.
                _side = ms.our_ticker.split("-")[-1]
                _old = ms.position_qty
                ms.position_qty = live_qty
                log("[POSITION_SYNC] %s pos %d→%d (detected external fill) | %s" % (
                    _side, _old, live_qty, ms.category))
                continue
            # Position shrank on Kalshi — auto-sell maker filled (partially or fully)
            sold_qty = ms.position_qty - live_qty
            side = ms.our_ticker.split("-")[-1]
            sell_px = ms.auto_sell_price if ms.auto_sell_price > 0 else self._sell_price_for(ms)
            # Weighted avg in case of multiple partial fills across audits
            if ms.realized_sell_qty > 0:
                total = ms.realized_sell_qty + sold_qty
                ms.realized_sell_price = int(round(
                    (ms.realized_sell_qty * ms.realized_sell_price + sold_qty * sell_px) / total))
                ms.realized_sell_qty = total
            else:
                ms.realized_sell_qty = sold_qty
                ms.realized_sell_price = sell_px
            log("[SELL_FILL_DETECTED] %s pos %d→%d (sold %dct at ~%dc) | %s" % (
                side, ms.position_qty, live_qty, sold_qty, sell_px, ms.category))
            ms.position_qty = live_qty
            if live_qty == 0:
                # Full closeout — kill DCA state machine. entry_phase stays
                # "filled" so cleanup_settled still runs at market finalization
                # and records the realized PnL.
                ms.dca_phase = "skipped"
                if ms.dca_order_id:
                    try:
                        await api_delete(self.session, self.ak, self.pk,
                                       "/trade-api/v2/portfolio/orders/%s" % ms.dca_order_id, self.rl)
                    except Exception:
                        pass
                    ms.dca_order_id = ""
                log("[SELL_FILL_CLOSED] %s fully closed via auto-sell, dca_phase=skipped | %s" % (
                    side, ms.category))

        sells = defaultdict(int)
        for o in orders_data.get("orders", []):
            if o.get("action") == "sell":
                sells[o.get("ticker", "")] += int(float(o.get("remaining_count_fp", "0")))

        for ticker, pos_qty in positions.items():
            _sell_qty = sells.get(ticker, 0)
            if _sell_qty < pos_qty:
                cat, cfg = self.get_category(ticker)
                if not cat: continue
                side = ticker.split("-")[-1]
                log("[SELL_AUDIT] %s pos=%d sell=%d — fixing" % (side, pos_qty, _sell_qty))
                for o in orders_data.get("orders", []):
                    if o.get("ticker") == ticker and o.get("action") == "sell":
                        await api_delete(self.session, self.ak, self.pk,
                                       "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                # V5: use auto-sell price if we have an ms with exit_target, else 99
                ms_for_audit = self.find_ms_by_ticker(ticker)
                audit_price = self._sell_price_for(ms_for_audit) if ms_for_audit else 99
                await self.place_sell(ticker, audit_price, pos_qty, "AUDIT_SELL")
            elif _sell_qty > pos_qty:
                # H15 fix (2026-04-11): shrink oversized resting sells. Previously
                # only the `sell < pos` branch ran, so an orphaned over-sized sell
                # (leftover from a prior restart or race) sat forever consuming
                # Kalshi's reserved qty and potentially causing insufficient-balance
                # rejections on new orders.
                cat, cfg = self.get_category(ticker)
                if not cat: continue
                side = ticker.split("-")[-1]
                log("[SELL_AUDIT_OVERSIZE] %s pos=%d sell=%d — shrinking" % (side, pos_qty, _sell_qty))
                for o in orders_data.get("orders", []):
                    if o.get("ticker") == ticker and o.get("action") == "sell":
                        await api_delete(self.session, self.ak, self.pk,
                                       "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                ms_for_audit = self.find_ms_by_ticker(ticker)
                audit_price = self._sell_price_for(ms_for_audit) if ms_for_audit else 99
                await self.place_sell(ticker, audit_price, pos_qty, "AUDIT_SELL_SHRINK")


    # ------------------------------------------------------------------
    # Startup reconciliation — sync with existing Kalshi positions
    # ------------------------------------------------------------------
    async def get_first_entry_price(self, ticker):
        """Fetch the ORIGINAL entry price (first chronological buy fill) for a ticker.
        Returns price in cents, or 0 if no fills found.

        Why this exists: reconcile cannot use blended avg price to determine
        the sizing tier — if a position has been DCA'd, the blended avg drops
        below the original entry and may fall into a different (often DOUBLED)
        tier. See DE Minaur incident 2026-04-10: standard 40+20 position at
        blended 59c was misclassified as ATP_MAIN doubled tier (55-59), causing
        an over-DCA to 100ct. The first buy fill gives us the true entry tier.
        """
        fills_path = "/trade-api/v2/portfolio/fills?ticker=%s&limit=200" % ticker
        fills_data = await api_get(self.session, self.ak, self.pk, fills_path, self.rl)
        if not fills_data:
            return 0
        fills = fills_data.get("fills", [])
        buy_fills = [f for f in fills if f.get("action") == "buy"]
        if not buy_fills:
            return 0
        # Kalshi returns newest-first; sort ascending by ts to find the first buy
        buy_fills.sort(key=lambda x: x.get("ts", 0))
        first = buy_fills[0]
        yes_dollars = float(first.get("yes_price_dollars", "0") or "0")
        return int(round(yes_dollars * 100))

    async def reconcile_positions(self):
        """On startup, check existing positions and mark events as entered."""
        pos_data = await api_get(self.session, self.ak, self.pk,
                                "/trade-api/v2/portfolio/positions", self.rl)
        if not pos_data:
            log("[RECONCILE] Could not fetch positions")
            return

        orders_data = await api_get(self.session, self.ak, self.pk,
                                   "/trade-api/v2/portfolio/orders?status=resting", self.rl)

        # Build sell order map
        sells = defaultdict(int)
        if orders_data:
            for o in orders_data.get("orders", []):
                if o.get("action") == "sell":
                    sells[o.get("ticker", "")] += int(float(o.get("remaining_count_fp", "0") or "0"))

        reconciled = 0
        for p in pos_data.get("market_positions", []):
            ticker = p.get("ticker", "")
            qty = int(float(p.get("position_fp", "0") or "0"))
            if qty <= 0:
                continue

            cat_name, cfg = self.get_category(ticker)
            if not cat_name:
                continue

            # Find event ticker — try discovery map first, then derive from ticker
            et = self.ticker_to_event.get(ticker)
            if not et:
                # Derive: KXWTAMATCH-26MAR19SONBEN-BEN -> KXWTAMATCH-26MAR19SONBEN
                parts = ticker.rsplit("-", 1)
                if len(parts) == 2:
                    et = parts[0]
                else:
                    continue

            # Compute avg price from total_traded / position.
            # CAVEAT (MON bug 2026-04-12): Kalshi's total_traded_dollars is the
            # cumulative GROSS notional across all fills (both buys and sells).
            # For positions that had partial auto-sell fills, this avg_price is
            # inflated — dollars-per-remaining-contract, not cost basis. Example:
            # MON-2 had 8ct buy @33c + 1ct buy @33c + 8ct sell @43c + 2ct buy @34c,
            # leaving 2ct with total_traded≈$7.88 → avg_price = 788/2 = 394c.
            # Fix: prefer get_first_entry_price (first chronological buy fill).
            total_traded = float(p.get("total_traded_dollars", "0") or "0")
            avg_price = int(total_traded / qty * 100) if qty > 0 else 0

            # MON fix (2026-04-12): fetch first-buy-fill price and use it as
            # ms.entry_price (cost basis proxy). Fall back to avg_price only
            # if fill history is missing. Also reused for sizing tier lookup.
            original_entry = await self.get_first_entry_price(ticker)
            if original_entry > 0:
                entry_price_to_use = original_entry
                log("[RECONCILE_ENTRY] %s first_buy=%dc (avg_formula=%dc) — using first_buy" % (
                    ticker.split("-")[-1], original_entry, avg_price))
            else:
                entry_price_to_use = avg_price
                log("[RECONCILE_ENTRY_FALLBACK] %s no fill history, using avg=%dc" % (
                    ticker.split("-")[-1], avg_price))

            # VERSION B DUAL MODE (2026-04-12): determine which match_states
            # key to use for this reconciled position. If NO ms exists for this
            # event yet, this position becomes the PRIMARY (keyed by `et`).
            # If a primary already exists (this is the 2nd Kalshi position for
            # the same event — i.e. dual mode was running pre-restart), we
            # create a SECONDARY ms with composite key `{et}|<direction>`.
            # Direction is inferred from the position's first-buy price:
            # >50c → leader, <=50c → underdog.
            inferred_direction = 'leader' if entry_price_to_use > 50 else 'underdog'
            primary_exists = et in self.match_states
            if primary_exists:
                primary_ms = self.match_states[et]
                # If the primary handles the OTHER direction, this pos is secondary
                if primary_ms.our_ticker and primary_ms.our_ticker != ticker:
                    use_key = self.ms_key(et, inferred_direction)
                    log("[DUAL_RECONCILE] %s 2nd position on event (primary=%s, this=%s %s) — composite key %s" % (
                        ticker.split("-")[-1],
                        primary_ms.our_ticker.split("-")[-1],
                        ticker.split("-")[-1], inferred_direction, use_key))
                else:
                    use_key = et  # same ticker as primary, no dual
            else:
                use_key = et  # first ms for this event

            if use_key not in self.match_states:
                self.match_states[use_key] = MatchState(
                    event_ticker=et, category=cat_name, cfg=cfg,
                    created_ts=time.time())

            ms = self.match_states[use_key]
            ms.our_ticker = ticker
            # H10 fix (2026-04-11): populate ms.tickers with both sides so the
            # main-loop stale-resub and _process_tick_events work correctly.
            # If the ticker was derived from the position string (not in
            # ticker_to_event), we also try to fetch the opposing side via a
            # markets-by-event query so the binary market has both sides
            # subscribed. Previously ms.tickers was left empty, breaking
            # stale-resub detection.
            ms.tickers.add(ticker)
            if len(ms.tickers) < 2:
                try:
                    _evt_path = "/trade-api/v2/markets?event_ticker=%s&status=open&limit=10" % et
                    _evt_data = await api_get(self.session, self.ak, self.pk, _evt_path, self.rl)
                    if _evt_data:
                        _added_tickers = []
                        for _m in _evt_data.get("markets", []):
                            _mt = _m.get("ticker", "")
                            if _mt and _mt not in ms.tickers:
                                ms.tickers.add(_mt)
                                _added_tickers.append(_mt.split("-")[-1])
                                # Also populate the discovery map so later
                                # code paths can look up event_ticker by full
                                # ticker string.
                                self.ticker_to_event[_mt] = et
                                self.event_tickers[et].add(_mt)
                        if _added_tickers:
                            log("[RECONCILE_TICKERS] %s added opposing side(s): %s" % (
                                ticker.split("-")[-1], ", ".join(_added_tickers)))
                except Exception as _e:
                    log("[RECONCILE_TICKERS_ERR] %s" % str(_e)[:100])
            ms.match_started = True
            ms.match_start_ts = time.time()
            ms.entry_phase = "filled"
            ms.entry_price = entry_price_to_use  # MON fix: first_buy if available
            ms.entry_fill_ts = time.time()
            ms.position_qty = qty

            # Sizing tier lookup also uses the ORIGINAL entry price (not the
            # blended avg). Blended avg drops after DCA and can land in a
            # doubled-tier band — see DE Minaur incident (2026-04-10): standard
            # 40+20=60ct position at blended 59c was misread as ATP_MAIN doubled
            # tier (55-59) and over-DCA'd to 100ct. Reuses original_entry fetched
            # above (no second API call).
            sizing_lookup_price = original_entry if original_entry > 0 else avg_price

            # V5: try to look up the per-cell strategy from DEPLOYMENT first.
            # If we find a matching cell, use its parameters. If not, fall back
            # to the legacy SIZING_CONFIG (handles existing positions in cells
            # that were skipped or didn't make it into the V5 blueprint).
            v5_strat = None
            for direction in ('leader', 'underdog'):
                v5_strat = get_strategy_v5(cat_name, direction, sizing_lookup_price)
                if v5_strat:
                    ms.direction = direction
                    ms.dca_drop = v5_strat['dca_drop'] if v5_strat['dca_drop'] is not None else 15
                    ms.exit_target = v5_strat['exit_target'] if v5_strat['exit_target'] is not None else 0
                    ms.entry_lo_filter = v5_strat['entry_lo']
                    ms.entry_hi_filter = v5_strat['entry_hi']
                    ms.maker_bid_offset = v5_strat.get('maker_bid_offset', 0)
                    ms.strategy_loaded = True
                    ms.use_blended_target = _bp_use_blended_target(
                        cat_name, direction, v5_strat['_tier_lo'], v5_strat['_tier_hi'])
                    intended_entry = v5_strat['entry_size']
                    intended_dca = v5_strat['dca_size']
                    log("[RECONCILE_V5] %s matched cell direction=%s sub=%d-%d dca=%dc exit=%s blendedB=%s" % (
                        ticker.split("-")[-1], direction, ms.entry_lo_filter, ms.entry_hi_filter,
                        ms.dca_drop, ('+%dc' % ms.exit_target) if ms.exit_target else 'hold99',
                        ms.use_blended_target))
                    break

            # Bug C fix: tier-only fallback. If get_strategy_v5 returned None
            # because the entry price drifted outside the cell's sub-range (very
            # common — sub is a subset of the tier), still try to grab the
            # cell's full params from DEPLOYMENT directly using just the tier
            # lookup. This preserves dca_drop / exit_target / use_blended_target
            # for grandfathered positions instead of falling through to the
            # legacy (40,20) path which bypassed BABY_SIZING_MODE and left
            # exit_target=0 → auto_sell_price=99c.
            if not v5_strat:
                for direction in ('leader', 'underdog'):
                    tiers = LEADER_TIERS_V5 if direction == 'leader' else UNDERDOG_TIERS_V5
                    for lo, hi in tiers:
                        if not (lo <= sizing_lookup_price <= hi):
                            continue
                        cell = DEPLOYMENT.get((cat_name, direction, lo, hi))
                        if not cell or cell.get('entry_size', 0) == 0:
                            continue
                        ms.direction = direction
                        ms.dca_drop = cell['dca_drop'] if cell['dca_drop'] is not None else 15
                        ms.exit_target = cell['exit_target'] if cell['exit_target'] is not None else 0
                        ms.entry_lo_filter = cell['entry_lo']
                        ms.entry_hi_filter = cell['entry_hi']
                        ms.maker_bid_offset = cell.get('maker_bid_offset', 0)
                        ms.strategy_loaded = True
                        ms.use_blended_target = _bp_use_blended_target(
                            cat_name, direction, lo, hi)
                        if BABY_SIZING_MODE:
                            intended_entry = BABY_ENTRY_SIZE
                            intended_dca = BABY_DCA_SIZE if cell['dca_drop'] is not None else 0
                        else:
                            intended_entry = cell['entry_size']
                            intended_dca = cell['dca_size']
                        log("[RECONCILE_V5_TIER] %s tier-matched direction=%s tier=%d-%d (price=%dc drifted from sub %d-%d) dca=%dc exit=%s blendedB=%s entry=%d/%d" % (
                            ticker.split("-")[-1], direction, lo, hi, sizing_lookup_price,
                            cell['entry_lo'], cell['entry_hi'],
                            ms.dca_drop, ('+%dc' % ms.exit_target) if ms.exit_target else 'hold99',
                            ms.use_blended_target, intended_entry, intended_dca))
                        v5_strat = cell  # signal a match
                        break
                    if v5_strat:
                        break

            if not v5_strat:
                # Still nothing — grandfathered position outside every V5 tier
                # (e.g. entry price < 10 or > 89). Legacy sizing, but respect
                # BABY_SIZING_MODE and log explicitly so we can track these.
                intended_entry, intended_dca = get_sizing(cat_name, sizing_lookup_price)
                if intended_entry == 0:
                    intended_entry, intended_dca = 40, 20  # legacy fallback
                if BABY_SIZING_MODE:
                    intended_entry = BABY_ENTRY_SIZE
                    intended_dca = BABY_DCA_SIZE
                log("[RECONCILE_LEGACY] %s no V5 cell match, legacy sizing=%d/%d entry_price=%dc" % (
                    ticker.split("-")[-1], intended_entry, intended_dca, sizing_lookup_price))

            ms.target_size = intended_entry
            ms.target_dca_size = intended_dca
            ms.auto_sell_price = self._sell_price_for(ms)

            # Determine dca_phase by comparing actual position to expected sizes.
            # If the position already exceeds the entry size, ANY excess is
            # interpreted as a (partial or full) DCA fill — mark dca filled to
            # prevent another DCA from firing. This is the safe direction: a
            # missed DCA (rare partial-doubled-entry case) is preferable to an
            # over-DCA (DE Minaur bug case).
            #
            # Heavy-favorite cells (intended_dca == 0) are entry-only — no DCA
            # ever fires for these, mark dca_phase=skipped.
            if intended_dca == 0:
                ms.dca_phase = "skipped"
                log("[RECONCILE] %s dca_phase=skipped (pos=%d, entry=%d, no DCA — heavy fav, entry=%dc)" % (
                    ticker.split("-")[-1], qty, intended_entry, sizing_lookup_price))
            else:
                full_size = intended_entry + intended_dca
                if qty >= full_size:
                    ms.dca_phase = "filled"
                    log("[RECONCILE] %s dca_phase=filled (pos=%d >= full %d = %d+%d, entry=%dc)" % (
                        ticker.split("-")[-1], qty, full_size, intended_entry, intended_dca, sizing_lookup_price))
                elif qty > intended_entry:
                    # Entry done + partial DCA already filled — do not DCA again
                    ms.dca_phase = "filled"
                    log("[RECONCILE] %s dca_phase=filled (pos=%d > entry %d, partial DCA detected, entry=%dc)" % (
                        ticker.split("-")[-1], qty, intended_entry, sizing_lookup_price))
                else:
                    # qty <= intended_entry — entry-only or partial entry; DCA still pending
                    ms.dca_phase = "watching"
                    log("[RECONCILE] %s dca_phase=watching (pos=%d, entry=%d, will DCA %d more, entry=%dc)" % (
                        ticker.split("-")[-1], qty, intended_entry, intended_dca, sizing_lookup_price))

            # Check if correct 99c sell exists
            sell_qty = sells.get(ticker, 0)
            sell_status = "exists"

            sell_px = self._sell_price_for(ms)

            if sell_qty < qty:
                # Cancel any existing undersized sells
                if orders_data:
                    for o in orders_data.get("orders", []):
                        if o.get("ticker") == ticker and o.get("action") == "sell":
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                # Place correct sell at auto-sell target (or 99c if no target)
                oid = await self.place_sell(ticker, sell_px, qty, "RECONCILE_SELL")
                ms.sell_order_id = oid
                sell_status = "placed %dct@%dc" % (qty, sell_px)
            elif sell_qty > qty:
                # Oversized sell — fix
                if orders_data:
                    for o in orders_data.get("orders", []):
                        if o.get("ticker") == ticker and o.get("action") == "sell":
                            await api_delete(self.session, self.ak, self.pk,
                                           "/trade-api/v2/portfolio/orders/%s" % o["order_id"], self.rl)
                oid = await self.place_sell(ticker, sell_px, qty, "RECONCILE_SELL")
                ms.sell_order_id = oid
                sell_status = "fixed %d->%dct@%dc" % (sell_qty, qty, sell_px)

            side = ticker.split("-")[-1]
            log("[RECONCILE] %s | pos=%d | avg=%dc | sell=%s | %s" % (
                side, qty, avg_price, sell_status, cat_name))
            reconciled += 1

        if reconciled:
            log("[RECONCILE] %d existing positions synced" % reconciled)

        # Restore persisted DCA cooling states
        saved = load_dca_state()
        now_r = time.time()
        # T2-3 fix: also prune any stale entries whose event is no longer in
        # match_states (accumulated from pre-T2-3 sessions where cleanup_settled
        # didn't touch the cooling file). Rewrite the file at the end.
        stale_entries = []
        for ticker, sdata in saved.items():
            # VERSION B DUAL MODE: use find_ms_by_ticker so we match the
            # correct ms (primary or secondary) by its our_ticker field.
            # The old et-keyed lookup would fail for secondary ms in dual mode.
            ms = self.find_ms_by_ticker(ticker)
            if ms is not None:
                if ms.dca_phase == "watching":
                    elapsed = now_r - sdata["dca_cool_start"]
                    remaining = sdata.get("dca_cool_duration", DCA_COOL_SEC) - elapsed
                    ms.dca_phase = "cooling"
                    ms.dca_cool_start = sdata["dca_cool_start"]
                    ms.dca_cool_trigger_bid = sdata["dca_cool_trigger_bid"]
                    ms.dca_cool_duration = sdata.get("dca_cool_duration", DCA_COOL_SEC)
                    if remaining > 0:
                        log("[DCA_RESTORE] %s cooling resumed — %ds remaining" % (
                            ticker.split("-")[-1], int(remaining)))
                    else:
                        log("[DCA_RESTORE] %s cooling expired during restart — will evaluate now" % (
                            ticker.split("-")[-1]))
            else:
                stale_entries.append(ticker)
        if stale_entries:
            pruned_state = {k: v for k, v in saved.items() if k not in stale_entries}
            try:
                with open(DCA_STATE_FILE, "w") as _fh:
                    json.dump(pruned_state, _fh)
                log("[COOLING_STARTUP_PRUNE] dropped %d stale entries: %s" % (
                    len(stale_entries),
                    ", ".join(tk.split("-")[-1] for tk in stale_entries)))
            except Exception as _e:
                log("[COOLING_STARTUP_PRUNE_ERR] %s" % str(_e)[:100])
        else:
            log("[RECONCILE] No existing positions — clean start")

    # ------------------------------------------------------------------
    # Settled event cleanup
    # ------------------------------------------------------------------
    async def cleanup_settled(self):
        to_remove = []
        for event, ms in list(self.match_states.items()):
            if ms.entry_phase not in ("filled", "filled_unverified"):
                continue
            ticker = ms.our_ticker
            if not ticker:
                continue
            data = await api_get(self.session, self.ak, self.pk,
                                "/trade-api/v2/markets/%s" % ticker, self.rl)
            if not data:
                continue
            market = data.get("market", data)
            status = market.get("status", "")
            result_val = market.get("result", "")
            if status == "finalized" or result_val:
                side = ticker.split("-")[-1]
                label = "WON" if result_val == "yes" else "LOST" if result_val == "no" else "SETTLED"
                # Use blended avg if DCA filled, else entry_price
                settle_avg = getattr(ms, 'blended_avg', ms.entry_price) or ms.entry_price
                settle_dca_price = getattr(ms, 'dca_fill_price', None)
                settle_dca_size = getattr(ms, 'dca_fill_size', None)
                # ms.position_qty is now accurate (audit_sells updates it when
                # auto-sell makers fill). Log both the realized (pre-settle
                # sold) portion and the remaining-at-settlement portion so the
                # PnL sheet reflects partial auto-sell fills.
                realized_qty = getattr(ms, 'realized_sell_qty', 0)
                realized_px = getattr(ms, 'realized_sell_price', 0)
                remaining_qty = ms.position_qty
                db_log_settlement(side, label.lower(), remaining_qty, settle_avg, ms.category,
                                  entry_price=ms.entry_price, dca_price=settle_dca_price,
                                  dca_size=settle_dca_size)
                if realized_qty > 0:
                    log("[SETTLED] %s %s | remaining=%d entry=%dc avg=%dc dca=%s | sold_pre=%dct@%dc | %s" % (
                        side, label, remaining_qty, ms.entry_price, settle_avg,
                        "%dc" % settle_dca_price if settle_dca_price else "n/a",
                        realized_qty, realized_px, ms.category))
                else:
                    log("[SETTLED] %s %s | pos=%d entry=%dc avg=%dc dca=%s | %s" % (
                        side, label, remaining_qty, ms.entry_price, settle_avg,
                        "%dc" % settle_dca_price if settle_dca_price else "n/a", ms.category))
                to_remove.append(event)
        # T2-3 fix: prune the dca_cooling_state.json file of settled matches.
        # Read the current file, drop any keys whose event_ticker matches a
        # just-removed event, and write it back. This prevents stale entries
        # from lingering across restarts (observed KOZ 33min after settlement).
        pruned_tickers = []
        if to_remove:
            try:
                current_state = load_dca_state()
                removed_events_set = set(to_remove)
                new_state = {}
                for _tk, _data in current_state.items():
                    if _data.get("event_ticker") in removed_events_set:
                        pruned_tickers.append(_tk.split("-")[-1])
                    else:
                        new_state[_tk] = _data
                if pruned_tickers:
                    with open(DCA_STATE_FILE, "w") as _fh:
                        json.dump(new_state, _fh)
                    log("[COOLING_PRUNED] %s removed from dca_cooling_state.json" %
                        ", ".join(pruned_tickers))
            except Exception as _e:
                log("[COOLING_PRUNE_ERR] %s" % str(_e)[:100])
        for event in to_remove:
            del self.match_states[event]
        if to_remove:
            log("[CLEANUP] Removed %d settled events" % len(to_remove))

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------
    async def run(self):
        log("=" * 70)
        log("  Tennis V5 — VERSION B (auto-sell + underdog + per-cell params)")
        if BABY_SIZING_MODE:
            log("  *** BABY SIZING MODE: entry=%dct dca=%dct (validation run) ***" % (
                BABY_ENTRY_SIZE, BABY_DCA_SIZE))
        # Summarize V5 deployment cells
        n_leader = sum(1 for k in DEPLOYMENT.keys() if k[1] == 'leader')
        n_under  = sum(1 for k in DEPLOYMENT.keys() if k[1] == 'underdog')
        log("  Deployment: %d leader cells + %d underdog cells across 4 categories" % (
            n_leader, n_under))
        for cat_name, cfg in CATEGORIES.items():
            series_str = ",".join(cfg['series'])
            cells_for_cat = sum(1 for k in DEPLOYMENT.keys() if k[0] == cat_name)
            log("  %s: %s (%d V5 cells)" % (cat_name, series_str, cells_for_cat))
        log("  Entry: clock-based, sched-%dm to sched+%dm, resting maker buy" % (
            ENTRY_BEFORE_START // 60, ENTRY_AFTER_START // 60))
        log("  DCA: per-cell drop + %ds cooling + 300s resting window" % DCA_COOL_SEC)
        log("  BBO log: %s" % BBO_LOG_FILE)
        log("=" * 70)

        self.session = aiohttp.ClientSession()

        # H11 fix: prime the capital-cap cache via refresh_balance so place_buy
        # calls during startup reconcile / first strategy_tick have a valid
        # self.current_balance to check against.
        await self.refresh_balance()
        if self.current_balance > 0:
            log("[INIT] Balance: $%.2f (cap=$%.2f at %.0f%%)" % (
                self.current_balance,
                self.current_balance * CAPITAL_CAP_FRACTION,
                CAPITAL_CAP_FRACTION * 100))

        await self.audit_sells()

        # H13 fix: wrap blocking get_match_schedule in asyncio.to_thread so
        # ESPN/TennisExplorer HTTP fetches don't freeze the event loop.
        from tennis_schedule import get_match_schedule
        self.ext_schedule = await asyncio.to_thread(get_match_schedule)
        self.last_schedule_fetch = time.time()

        # Reconcile BEFORE discovery so SKIP_LIVE doesn't orphan positions
        await self.reconcile_positions()

        tickers = await self.discover_markets()
        if not tickers:
            log("[FATAL] No tickers found"); return

        await self.ws_connect()
        await self.ws_subscribe(tickers)
        asyncio.create_task(self.ws_reader())

        last_discovery = time.time()
        last_fill_check = time.time()
        last_audit = time.time()
        last_bbo_flush = time.time()
        last_balance_check = 0.0  # H11: force immediate balance fetch on first iteration

        log("[RUNNING] Main loop started — %d events tracked" % len(self.match_states))

        while True:
            try:
                now = time.time()
                # H12 fix: wrap each sub-call in its own try/except so one failure
                # doesn't abort the rest of the iteration. Full traceback on each.
                try:
                    await self.strategy_tick()
                except Exception as e:
                    log("[ERROR_STRATEGY_TICK] %s" % e)
                    log("[TRACEBACK] %s" % traceback.format_exc())

                if now - last_fill_check >= POSITION_POLL_INTERVAL:
                    try:
                        await self.check_fills()
                    except Exception as e:
                        log("[ERROR_CHECK_FILLS] %s" % e)
                        log("[TRACEBACK] %s" % traceback.format_exc())
                    last_fill_check = now

                if now - last_audit >= 120:
                    try:
                        await self.audit_sells()
                    except Exception as e:
                        log("[ERROR_AUDIT_SELLS] %s" % e)
                        log("[TRACEBACK] %s" % traceback.format_exc())
                    last_audit = now

                # H11: refresh balance cap every 60s
                if now - last_balance_check >= CAPITAL_POLL_INTERVAL:
                    try:
                        _prev_bal = self.current_balance
                        await self.refresh_balance()
                        if self.current_balance > 0 and abs(self.current_balance - _prev_bal) > 1:
                            log("[BALANCE] $%.2f (exposure=$%.2f, cap=$%.2f)" % (
                                self.current_balance,
                                self._estimate_current_exposure(),
                                self.current_balance * CAPITAL_CAP_FRACTION))
                    except Exception as e:
                        log("[ERROR_BALANCE] %s" % e)
                        log("[TRACEBACK] %s" % traceback.format_exc())
                    last_balance_check = now

                # Resubscribe any stale tickers immediately
                stale_resub = []
                for event, ms in self.match_states.items():
                    if ms.entry_phase in ("filled", "filled_unverified") and ms.our_ticker:
                        for t in ms.tickers:
                            if t not in self.subscribed:
                                stale_resub.append(t)
                if stale_resub:
                    try:
                        await self.ws_subscribe(stale_resub)
                        log("[WS_RESUB] Resubscribed %d stale tickers" % len(stale_resub))
                    except Exception as e:
                        log("[ERROR_WS_RESUB] %s" % e)
                        log("[TRACEBACK] %s" % traceback.format_exc())

                if now - last_discovery >= DISCOVERY_INTERVAL:
                    # Refresh external schedule every 30 min
                    if now - self.last_schedule_fetch >= 1800:
                        from tennis_schedule import get_match_schedule, match_kalshi_event
                        # H13 fix: async wrapper around blocking HTTP fetch
                        self.ext_schedule = await asyncio.to_thread(get_match_schedule)
                        self.last_schedule_fetch = now
                        # Update existing MatchStates if schedule changed
                        for evt, ms in self.match_states.items():
                            # H7 fix: include filled_unverified in skip-live gate
                            if ms.entry_phase in ("filled", "filled_unverified", "skipped") and ms.match_play_start_ts > 0:
                                continue  # match is live or done, don't touch
                            if not ms.scheduled_start_ts or ms.schedule_source == "price_stability":
                                continue  # no clock-based schedule to update
                            info = match_kalshi_event(evt, self.ext_schedule)
                            if not info:
                                continue
                            start_str = info.get("start_time", "")
                            try:
                                new_ts = datetime.fromisoformat(
                                    start_str.replace("Z", "+00:00")).timestamp()
                            except Exception:
                                continue
                            if abs(new_ts - ms.scheduled_start_ts) >= 300:  # 5+ min diff
                                old_str = datetime.fromtimestamp(ms.scheduled_start_ts).strftime("%H:%M")
                                new_str = datetime.fromtimestamp(new_ts).strftime("%H:%M")
                                ms.scheduled_start_ts = new_ts
                                ms.earliest_entry_ts = new_ts - ENTRY_BEFORE_START
                                ms.latest_entry_ts = new_ts + ENTRY_AFTER_START
                                src = info.get("source", "?")
                                side = ms.our_ticker.split("-")[-1] if ms.our_ticker else evt
                                log("[SCHED_UPDATE] %s %s -> %s | window %s-%s | %s" % (
                                    side, old_str, new_str,
                                    datetime.fromtimestamp(ms.earliest_entry_ts).strftime("%H:%M"),
                                    datetime.fromtimestamp(ms.latest_entry_ts).strftime("%H:%M"),
                                    src))
                                # Reopen window if it was skipped due to stale time
                                if ms.entry_phase == "skipped" and now < ms.latest_entry_ts:
                                    ms.entry_phase = "waiting"
                                    log("[SCHED_REOPEN] %s window reopened, was skipped on stale schedule" % side)
                    try:
                        tickers = await self.discover_markets()
                        if tickers: await self.ws_subscribe(tickers)
                    except Exception as e:
                        log("[ERROR_DISCOVER] %s" % e)
                        log("[TRACEBACK] %s" % traceback.format_exc())
                    try:
                        await self.cleanup_settled()
                    except Exception as e:
                        log("[ERROR_CLEANUP] %s" % e)
                        log("[TRACEBACK] %s" % traceback.format_exc())
                    last_discovery = now

                if now - last_bbo_flush >= 60:
                    self._flush_bbo()
                    last_bbo_flush = now

                await asyncio.sleep(1)
            except KeyboardInterrupt:
                log("[SHUTDOWN] Ctrl+C"); break
            except Exception as e:
                log("[ERROR] %s" % e)
                log("[TRACEBACK] %s" % traceback.format_exc())
                await asyncio.sleep(5)

        self._flush_bbo()
        await self.session.close()

if __name__ == "__main__":
    asyncio.run(TennisV5().run())
