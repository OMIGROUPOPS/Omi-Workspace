#!/usr/bin/env python3
"""
Intra-Kalshi Live Paper Trading Scanner

Standalone persistent process that connects to Kalshi WS, monitors ALL live/open
events with 3+ markets, detects 4 types of intra-exchange opportunities
(momentum lag, mean reversion, contradiction, resolution farming), and paper
trades them. Category-agnostic — works on sports, crypto, politics, economics.

PAPER MODE ONLY — no real orders.

Usage:
    cd arb-executor
    python -m intra_kalshi.live_scanner

Runs in tmux alongside the cross-platform executor.
"""

import asyncio
import base64
import json
import math
import os
import re
import signal
import sys
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import websockets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"
MAX_RPS = 18
EVENTS_PATH = "/trade-api/v2/events?status=open&with_nested_markets=true&limit=200"

# Scan parameters
MOMENTUM_THRESHOLD = 5       # Min move (cents) to trigger lag scan
MOMENTUM_WINDOW = 30.0       # Lookback (seconds) for price move
MOMENTUM_LAG_RATIO = 0.5     # Flag if related moved < 50% of expected
REVERSION_SPIKE = 15          # Min spike (cents) for mean reversion
REVERSION_WINDOW = 10.0       # Spike must happen within this (seconds)
REVERSION_TARGET = 4          # Expected reversion amount (cents)
REVERSION_STOP = 5            # Stop loss on reversion trades (cents)
REVERSION_MIN_DEPTH = 50      # Both bid+ask need 50+ contracts
REVERSION_CONFIRM_REVERT = 2  # Must see 2c reversion from peak before entry
REVERSION_CONFIRM_WINDOW = 5.0  # Confirmation must happen within 5s
REVERSION_ALLOWED_CATEGORIES = {"Sports"}  # Only sports mean-revert on short TF
REVERSION_MAX_HALF_LIFE = 120.0  # Skip if OU half-life > 120s (price not mean-reverting fast enough)
CONTRADICTION_MIN_DEPTH = 10  # Both sides need 10+ contracts
RESOLUTION_PRICE_RANGE = (95, 99)  # Near-settled price range
RESOLUTION_TIME = 300         # Within 5 min of close_time (seconds)
PAPER_TIMEOUT = 300           # 5-min position timeout (seconds)
BBO_HISTORY_WINDOW = 60.0    # Rolling price history (seconds)
STATS_INTERVAL = 300          # Stats dump frequency (seconds)
REDISCOVERY_INTERVAL = 1800   # Rediscovery every 30 min (seconds)
WS_SUBSCRIBE_BATCH = 100     # Max tickers per subscribe message
WS_PING_INTERVAL = 30
WS_RECONNECT_INITIAL = 1
WS_RECONNECT_MAX = 60
WS_WATCHDOG_TIMEOUT = 30     # Reconnect if no WS message in 30s

PAPER_TRADES_FILE = os.path.join(os.path.dirname(__file__), "intra_paper_trades.json")
STATS_LOG = "/tmp/intra_scanner.log"

# Correlation factors for momentum lag scan
MOMENTUM_CORRELATION = {
    ("moneyline", "spread"): 0.6,   # ML 10c move → expect 6c spread move
    ("spread", "moneyline"): 1.4,   # spread 10c move → expect 14c ML move
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BBOEntry:
    ts: float
    bid: int
    ask: int
    bid_size: int
    ask_size: int


@dataclass
class LocalBook:
    ticker: str
    yes_bids: Dict[int, int] = field(default_factory=dict)
    yes_asks: Dict[int, int] = field(default_factory=dict)
    best_bid: Optional[int] = None
    best_ask: Optional[int] = None
    best_bid_size: int = 0
    best_ask_size: int = 0
    last_update: float = 0.0


@dataclass
class MarketInfo:
    ticker: str
    event_ticker: str
    game_id: str
    market_type: str    # 'moneyline', 'spread', 'total', 'variant'
    team: str
    floor_strike: Optional[float] = None
    close_time: Optional[str] = None
    category: str = ""


@dataclass
class PaperTrade:
    id: str
    scan_type: str
    ticker: str
    game_id: str
    side: str           # 'buy_yes' or 'buy_no'
    entry_price: int
    entry_time: float
    target: int
    stop: int
    exit_price: Optional[int] = None
    exit_time: Optional[float] = None
    pnl_cents: Optional[int] = None
    exit_reason: Optional[str] = None
    description: str = ""
    # Extra detail fields for overnight analysis
    spike_size: Optional[int] = None
    half_life: Optional[float] = None
    entry_depth: int = 0
    hold_time: Optional[float] = None    # seconds held
    bbo_updates_seen: int = 0            # BBO updates since open (skip exit on 0)


@dataclass
class ScanSignal:
    scan_type: str
    severity: str       # 'HIGH', 'MEDIUM', 'LOW'
    ticker: str
    game_id: str
    entry_side: str     # 'buy_yes' or 'buy_no'
    entry_price: int
    target: int
    stop: int
    description: str
    depth: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_team(ticker: str) -> str:
    """KXNBASPREAD-26MAR01DETORL-DET7 → 'DET'"""
    suffix = ticker.rsplit("-", 1)[-1]
    return re.sub(r"\d+$", "", suffix)


def extract_game_id(event_ticker: str) -> Optional[str]:
    """KXNBAGAME-26FEB28NOPUTA → '26FEB28NOPUTA'"""
    parts = event_ticker.split("-")
    return parts[1] if len(parts) >= 2 else None


def extract_series_prefix(event_ticker: str) -> str:
    """KXNBAGAME-26FEB28NOPUTA → 'KXNBAGAME'"""
    return event_ticker.split("-")[0]


def classify_event_market_type(event_ticker: str) -> str:
    """Infer market type from event ticker prefix.
    Sports use GAME/SPREAD/TOTAL suffixes in the prefix; non-sports default to 'variant'."""
    prefix = extract_series_prefix(event_ticker).upper()
    if "SPREAD" in prefix:
        return "spread"
    if "TOTAL" in prefix:
        return "total"
    if "GAME" in prefix:
        return "moneyline"
    return "variant"


def severity(profit_cents: int) -> str:
    if profit_cents >= 5:
        return "HIGH"
    if profit_cents >= 3:
        return "MEDIUM"
    return "LOW"


def fp_to_cents(val) -> Optional[int]:
    """Convert FixedPointDollars string or legacy int to cents."""
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return round(float(val) * 100)
        except ValueError:
            return None
    if isinstance(val, (int, float)):
        return int(val) if val > 1 else round(val * 100)
    return None


# ---------------------------------------------------------------------------
# Auth — RSA-PSS SHA256 signing
# ---------------------------------------------------------------------------

def load_credentials():
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path)
    except ImportError:
        pass

    api_key = os.getenv("KALSHI_API_KEY", "f3b064d1-a02e-42a4-b2b1-132834694d23")

    pem_path = Path(__file__).resolve().parent.parent / "kalshi.pem"
    if not pem_path.exists():
        sys.exit(f"[FATAL] kalshi.pem not found at {pem_path}")
    private_key = serialization.load_pem_private_key(
        pem_path.read_bytes(), password=None, backend=default_backend()
    )
    return api_key, private_key


def sign_request(private_key, ts: str, method: str, path: str) -> str:
    msg = f"{ts}{method}{path}".encode("utf-8")
    sig = private_key.sign(
        msg,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(sig).decode("utf-8")


def auth_headers(api_key: str, private_key, method: str, path: str) -> dict:
    ts = str(int(time.time() * 1000))
    sign_path = path.split("?")[0]
    return {
        "KALSHI-ACCESS-KEY": api_key,
        "KALSHI-ACCESS-SIGNATURE": sign_request(private_key, ts, method, sign_path),
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Rate limiter — sliding window
# ---------------------------------------------------------------------------

class RateLimiter:
    def __init__(self, max_rps: int = MAX_RPS):
        self.max_rps = max_rps
        self.timestamps: deque = deque()

    async def acquire(self):
        now = time.monotonic()
        while self.timestamps and now - self.timestamps[0] >= 1.0:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_rps:
            sleep_for = 1.0 - (now - self.timestamps[0])
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
        self.timestamps.append(time.monotonic())


# ---------------------------------------------------------------------------
# REST Discovery
# ---------------------------------------------------------------------------

async def api_get(session, api_key, private_key, path, rate_limiter) -> Optional[dict]:
    url = f"{BASE_URL}{path}"
    backoffs = [1, 2, 4]
    for attempt, backoff in enumerate(backoffs + [None]):
        await rate_limiter.acquire()
        headers = auth_headers(api_key, private_key, "GET", path)
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    return await r.json()
                if r.status == 429 and backoff is not None:
                    print(f"  [429] Rate limited on {path}, retry in {backoff}s")
                    await asyncio.sleep(backoff)
                    continue
                print(f"  [ERR] {r.status} on {path}")
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if backoff is not None:
                print(f"  [RETRY] {e}, retry in {backoff}s")
                await asyncio.sleep(backoff)
                continue
            print(f"  [FAIL] {e}")
            return None
    return None


async def paginate(session, api_key, private_key, base_path, result_key, rate_limiter) -> list:
    items = []
    cursor = None
    page = 0
    while True:
        path = base_path + (f"&cursor={cursor}" if cursor else "")
        data = await api_get(session, api_key, private_key, path, rate_limiter)
        if data is None:
            break
        batch = data.get(result_key, [])
        items.extend(batch)
        cursor = data.get("cursor")
        page += 1
        if not cursor or not batch:
            break
    return items


# ============================================================================
# LiveScanner
# ============================================================================

class LiveScanner:
    def __init__(self):
        self.api_key: str = ""
        self.private_key = None
        self.rate_limiter = RateLimiter()
        self.ws = None
        self.ws_connected = False
        self.ws_reconnect_delay = WS_RECONNECT_INITIAL
        self.msg_id = 0
        self.shutdown = False

        # Market data
        self.market_info: Dict[str, MarketInfo] = {}          # ticker → MarketInfo
        self.games: Dict[str, Dict[str, List[str]]] = {}      # game_id → {type → [tickers]}
        self.books: Dict[str, LocalBook] = {}                  # ticker → LocalBook
        self.bbo_history: Dict[str, deque] = {}                # ticker → deque[BBOEntry]
        self.subscribed_tickers: Set[str] = set()

        # Sequence tracking
        self._seq_tracker: Dict[int, Dict] = {}
        self._seq_gaps = 0

        # Paper trading
        self.open_trades: List[PaperTrade] = []
        self.closed_trades: List[PaperTrade] = []

        # Stats
        self.stats = {
            "started": time.time(),
            "ws_messages": 0,
            "bbo_updates": 0,
            "snapshots": 0,
            "deltas": 0,
            "scan_signals": 0,
            "paper_trades_opened": 0,
            "paper_trades_closed": 0,
            "events_discovered": 0,
            "tickers_subscribed": 0,
        }
        # Category tracking
        self._category_stats: Dict[str, Dict] = {}  # category → {events, tickers, signals}

        # Warmup tracking: ticker → timestamp of first BBO
        self._ticker_first_bbo: Dict[str, float] = {}

        # Dedup: don't fire same signal repeatedly
        self._recent_signals: Dict[str, float] = {}  # key → timestamp
        self._signal_cooldown = 30.0  # seconds

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def _load_credentials(self):
        self.api_key, self.private_key = load_credentials()
        print(f"[SCAN] Credentials loaded (key={self.api_key[:8]}...)")

    async def discover_events(self, session) -> int:
        """Fetch ALL open events, group by event, qualify those with 3+ markets."""
        print("[SCAN] Discovering all events...")
        events = await paginate(
            session, self.api_key, self.private_key, EVENTS_PATH, "events", self.rate_limiter
        )
        print(f"[SCAN] Fetched {len(events)} events total")

        new_tickers = []
        for ev in events:
            et = ev.get("event_ticker", "")
            if not et:
                continue
            markets = ev.get("markets", [])
            if len(markets) < 3:
                continue  # Skip events with < 3 markets upfront

            # Derive game_id and market_type from event ticker
            game_id = extract_game_id(et)
            if not game_id:
                game_id = et  # Use full event_ticker as grouping key
            mtype = classify_event_market_type(et)
            category = ev.get("category", "") or ""

            for m in markets:
                ticker = m.get("ticker", "")
                if not ticker or ticker in self.market_info:
                    continue

                fs = m.get("floor_strike")
                fs_num = None
                if fs is not None:
                    try:
                        fs_num = float(fs)
                    except (ValueError, TypeError):
                        pass

                info = MarketInfo(
                    ticker=ticker,
                    event_ticker=et,
                    game_id=game_id,
                    market_type=mtype,
                    team=extract_team(ticker),
                    floor_strike=fs_num,
                    close_time=m.get("close_time"),
                    category=category,
                )
                self.market_info[ticker] = info

                # Group by game_id → market_type
                if game_id not in self.games:
                    self.games[game_id] = defaultdict(list)
                self.games[game_id][mtype].append(ticker)
                new_tickers.append(ticker)

                # Track category
                if category not in self._category_stats:
                    self._category_stats[category] = {"events": set(), "tickers": 0, "signals": 0}
                self._category_stats[category]["events"].add(game_id)
                self._category_stats[category]["tickers"] += 1

        # Qualify: events with 3+ markets total
        qualified_tickers = []
        for game_id, types in self.games.items():
            total_markets = sum(len(v) for v in types.values())
            if total_markets >= 3:
                for tlist in types.values():
                    for t in tlist:
                        if t not in self.subscribed_tickers:
                            qualified_tickers.append(t)

        self.stats["events_discovered"] = len(self.games)
        game_qualified = sum(
            1 for g in self.games.values()
            if sum(len(v) for v in g.values()) >= 3
        )
        # Category summary
        cat_summary = []
        for cat, cdata in sorted(self._category_stats.items(), key=lambda x: -x[1]["tickers"]):
            cat_label = cat if cat else "unknown"
            cat_summary.append(f"{cat_label}={len(cdata['events'])}ev/{cdata['tickers']}t")
        print(f"[SCAN] {len(self.games)} events found, {game_qualified} qualified (3+ markets)")
        print(f"[SCAN] Categories: {', '.join(cat_summary[:10])}")
        print(f"[SCAN] {len(qualified_tickers)} new tickers to subscribe")
        return len(qualified_tickers)

    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------

    async def ws_connect(self):
        ts = str(int(time.time() * 1000))
        headers = {
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-SIGNATURE": sign_request(self.private_key, ts, "GET", WS_PATH),
            "KALSHI-ACCESS-TIMESTAMP": ts,
        }
        try:
            print(f"[WS] Connecting to {WS_URL}...")
            self.ws = await websockets.connect(
                WS_URL,
                additional_headers=headers,
                ping_interval=WS_PING_INTERVAL,
                ping_timeout=10,
            )
            self.ws_connected = True
            self.ws_reconnect_delay = WS_RECONNECT_INITIAL
            print("[WS] Connected")
            return True
        except Exception as e:
            print(f"[WS] Connection failed: {e}")
            self.ws_connected = False
            return False

    async def ws_subscribe(self, tickers: List[str]):
        if not self.ws_connected or not self.ws:
            return
        # Batch in groups of WS_SUBSCRIBE_BATCH
        for i in range(0, len(tickers), WS_SUBSCRIBE_BATCH):
            batch = tickers[i:i + WS_SUBSCRIBE_BATCH]
            self.msg_id += 1
            msg = {
                "id": self.msg_id,
                "cmd": "subscribe",
                "params": {
                    "channels": ["orderbook_delta"],
                    "market_tickers": batch,
                },
            }
            try:
                await self.ws.send(json.dumps(msg))
                self.subscribed_tickers.update(batch)
            except Exception as e:
                print(f"[WS] Subscribe batch failed: {e}")
        self.stats["tickers_subscribed"] = len(self.subscribed_tickers)
        print(f"[WS] Subscribed to {len(tickers)} tickers (total: {len(self.subscribed_tickers)})")

    async def ws_subscribe_all(self):
        """Subscribe to all qualified tickers not yet subscribed."""
        to_sub = []
        for game_id, types in self.games.items():
            total_markets = sum(len(v) for v in types.values())
            if total_markets >= 3:
                for tlist in types.values():
                    for t in tlist:
                        if t not in self.subscribed_tickers:
                            to_sub.append(t)
        if to_sub:
            await self.ws_subscribe(to_sub)

    # ------------------------------------------------------------------
    # Orderbook management
    # ------------------------------------------------------------------

    def apply_snapshot(self, ticker: str, msg: dict):
        book = LocalBook(ticker=ticker)

        for level in msg.get("yes", []):
            if isinstance(level, list) and len(level) >= 2:
                price, size = int(level[0]), int(level[1])
                if size > 0:
                    book.yes_bids[price] = size

        for level in msg.get("no", []):
            if isinstance(level, list) and len(level) >= 2:
                no_price, size = int(level[0]), int(level[1])
                ask_price = 100 - no_price
                if size > 0:
                    book.yes_asks[ask_price] = size

        self._recalc_bbo(book)
        book.last_update = time.time()
        self.books[ticker] = book
        self.stats["snapshots"] += 1

    def apply_delta(self, ticker: str, msg: dict):
        if ticker not in self.books:
            self.books[ticker] = LocalBook(ticker=ticker)
        book = self.books[ticker]

        price = msg.get("price")
        size_delta = msg.get("delta", 0)
        side = msg.get("side", "yes").lower()

        if price is None:
            return

        price = int(price)
        if side == "yes":
            target = book.yes_bids
            target_price = price
        elif side == "no":
            target = book.yes_asks
            target_price = 100 - price
        else:
            return

        if size_delta != 0:
            current = target.get(target_price, 0)
            new_val = current + int(size_delta)
            if new_val <= 0:
                target.pop(target_price, None)
            else:
                target[target_price] = new_val

        self._recalc_bbo(book)
        book.last_update = time.time()
        self.stats["deltas"] += 1

    @staticmethod
    def _recalc_bbo(book: LocalBook):
        if book.yes_bids:
            bb = max(book.yes_bids.keys())
            book.best_bid = bb
            book.best_bid_size = book.yes_bids[bb]
        else:
            book.best_bid = None
            book.best_bid_size = 0

        if book.yes_asks:
            ba = min(book.yes_asks.keys())
            book.best_ask = ba
            book.best_ask_size = book.yes_asks[ba]
        else:
            book.best_ask = None
            book.best_ask_size = 0

    def _record_bbo(self, ticker: str):
        """Record current BBO to rolling history."""
        book = self.books.get(ticker)
        if not book or book.best_bid is None or book.best_ask is None:
            return
        now = time.time()
        if ticker not in self.bbo_history:
            self.bbo_history[ticker] = deque()
        if ticker not in self._ticker_first_bbo:
            self._ticker_first_bbo[ticker] = now
        hist = self.bbo_history[ticker]
        hist.append(BBOEntry(
            ts=now,
            bid=book.best_bid,
            ask=book.best_ask,
            bid_size=book.best_bid_size,
            ask_size=book.best_ask_size,
        ))
        # Prune old entries
        cutoff = now - BBO_HISTORY_WINDOW
        while hist and hist[0].ts < cutoff:
            hist.popleft()
        self.stats["bbo_updates"] += 1

    def _is_warmed_up(self, ticker: str) -> bool:
        """Ticker must have 60s+ of continuous BBO history with 3+ data points."""
        first = self._ticker_first_bbo.get(ticker)
        if first is None:
            return False
        if time.time() - first < BBO_HISTORY_WINDOW:
            return False
        hist = self.bbo_history.get(ticker)
        if not hist or len(hist) < 3:
            return False
        return True

    def _estimate_half_life(self, ticker: str) -> Optional[float]:
        """Estimate OU mean-reversion half-life from rolling BBO history.
        Regresses Δp_t on (μ - p_{t-1}) via simple OLS: Δp = λ(μ - p) + ε.
        Returns half_life = ln(2)/λ in seconds, or None if insufficient data."""
        hist = self.bbo_history.get(ticker)
        if not hist or len(hist) < 10:
            return None

        # Build midpoint time series
        mids = []
        times = []
        for entry in hist:
            mid = (entry.bid + entry.ask) // 2
            if mid > 0:
                mids.append(mid)
                times.append(entry.ts)

        if len(mids) < 10:
            return None

        mu = sum(mids) / len(mids)

        # OLS: Δp_t = λ(μ - p_{t-1}) + ε
        # Regress y = Δp on x = (μ - p_{t-1})
        sum_xy = 0.0
        sum_xx = 0.0
        for i in range(1, len(mids)):
            dt = times[i] - times[i - 1]
            if dt <= 0:
                continue
            dp = mids[i] - mids[i - 1]
            x = mu - mids[i - 1]
            # Normalize by dt so lambda is per-second
            y = dp / dt
            sum_xy += x * y
            sum_xx += x * x

        if sum_xx < 1e-9:
            return None  # No variance — flat price

        lam = sum_xy / sum_xx  # λ per second

        if lam <= 0:
            return None  # Not mean-reverting (trending or random walk)

        half_life = math.log(2) / lam
        return half_life

    def _get_midpoint(self, ticker: str) -> Optional[int]:
        book = self.books.get(ticker)
        if not book or book.best_bid is None or book.best_ask is None:
            return None
        return (book.best_bid + book.best_ask) // 2

    def _get_midpoint_at(self, ticker: str, seconds_ago: float) -> Optional[int]:
        """Get midpoint from N seconds ago. Returns None if no valid data exists
        at that time (rejects first-ever BBO as a reference point)."""
        hist = self.bbo_history.get(ticker)
        if not hist:
            return None
        now = time.time()
        target_ts = now - seconds_ago
        first_bbo = self._ticker_first_bbo.get(ticker)

        # Reject if the target timestamp is before or near the first-ever BBO
        # (the "first snapshot" is not a real historical price)
        if first_bbo is not None and target_ts < first_bbo + 5.0:
            return None

        # Find closest entry at or before target_ts
        best = None
        for entry in hist:
            if entry.ts <= target_ts:
                best = entry
            else:
                break
        if best is None:
            return None  # No entry exists at that time — don't fall back to oldest
        if best.bid <= 0 or best.ask <= 0:
            return None
        return (best.bid + best.ask) // 2

    def _price_move(self, ticker: str, window_seconds: float, min_entries: int = 3) -> Optional[int]:
        """Compute price move over window. Positive = price went up.
        Requires min_entries BBO updates in the window to ensure data quality."""
        hist = self.bbo_history.get(ticker)
        if not hist or len(hist) < min_entries:
            return None
        now_mid = self._get_midpoint(ticker)
        past_mid = self._get_midpoint_at(ticker, window_seconds)
        if now_mid is None or past_mid is None:
            return None
        return now_mid - past_mid

    # ------------------------------------------------------------------
    # Scan 1: Momentum Lag
    # ------------------------------------------------------------------

    def scan_momentum_lag(self, ticker: str) -> List[ScanSignal]:
        """Detect when one market moves but related markets haven't caught up."""
        signals = []
        info = self.market_info.get(ticker)
        if not info:
            return signals

        primary_move = self._price_move(ticker, MOMENTUM_WINDOW, min_entries=5)
        if primary_move is None or abs(primary_move) < MOMENTUM_THRESHOLD:
            return signals

        game = self.games.get(info.game_id)
        if not game:
            return signals

        # Check related markets in same game, different type
        for other_type, other_tickers in game.items():
            if other_type == info.market_type:
                continue
            corr_key = (info.market_type, other_type)
            corr = MOMENTUM_CORRELATION.get(corr_key)
            if corr is None:
                continue  # Skip totals

            for ot in other_tickers:
                other_info = self.market_info.get(ot)
                if not other_info or other_info.team != info.team:
                    continue

                other_move = self._price_move(ot, MOMENTUM_WINDOW, min_entries=5)
                if other_move is None:
                    continue

                expected_move = primary_move * corr
                if abs(expected_move) < 2:
                    continue

                # Check if lagging
                if expected_move > 0:
                    # Expected to go up — did it?
                    if other_move < expected_move * MOMENTUM_LAG_RATIO:
                        remaining = int(expected_move - other_move)
                        book = self.books.get(ot)
                        if not book or book.best_ask is None:
                            continue
                        signals.append(ScanSignal(
                            scan_type="momentum_lag",
                            severity=severity(remaining),
                            ticker=ot,
                            game_id=info.game_id,
                            entry_side="buy_yes",
                            entry_price=book.best_ask,
                            target=book.best_ask + remaining,
                            stop=book.best_ask - 3,
                            description=(
                                f"{info.category} {info.team}: {info.market_type} moved {primary_move:+d}c "
                                f"but {other_type} only {other_move:+d}c (expected {expected_move:+.0f}c)"
                            ),
                            depth=book.best_ask_size,
                        ))
                elif expected_move < 0:
                    if other_move > expected_move * MOMENTUM_LAG_RATIO:
                        remaining = int(abs(expected_move) - abs(other_move))
                        book = self.books.get(ot)
                        if not book or book.best_bid is None:
                            continue
                        signals.append(ScanSignal(
                            scan_type="momentum_lag",
                            severity=severity(remaining),
                            ticker=ot,
                            game_id=info.game_id,
                            entry_side="buy_no",
                            entry_price=100 - book.best_bid,
                            target=100 - (book.best_bid - remaining),
                            stop=100 - (book.best_bid + 3),
                            description=(
                                f"{info.category} {info.team}: {info.market_type} moved {primary_move:+d}c "
                                f"but {other_type} only {other_move:+d}c (expected {expected_move:+.0f}c)"
                            ),
                            depth=book.best_bid_size,
                        ))

        return signals

    # ------------------------------------------------------------------
    # Scan 2: Mean Reversion
    # ------------------------------------------------------------------

    def scan_mean_reversion(self, ticker: str) -> List[ScanSignal]:
        """Detect 15c+ spikes within 10s on liquid sports markets — bet on reversion.
        Requires: sports only, 50+ depth, spike already reversing 2c from peak."""
        signals = []
        info = self.market_info.get(ticker)
        if not info:
            return signals

        # Category filter: only sports markets mean-revert on short timeframes
        if info.category not in REVERSION_ALLOWED_CATEGORIES:
            return signals

        now_mid = self._get_midpoint(ticker)
        past_mid = self._get_midpoint_at(ticker, REVERSION_WINDOW)
        if now_mid is None or past_mid is None:
            return signals

        spike = now_mid - past_mid
        if abs(spike) < REVERSION_SPIKE:
            return signals

        # Reject data artifacts: anything > 25c is not a real spike
        if abs(spike) > 25:
            return signals

        book = self.books.get(ticker)
        if not book:
            return signals

        # Depth filter: both sides need 50+ contracts for reliable reversion
        if book.best_bid_size < REVERSION_MIN_DEPTH or book.best_ask_size < REVERSION_MIN_DEPTH:
            return signals

        # OU half-life filter: skip if price isn't mean-reverting fast enough
        half_life = self._estimate_half_life(ticker)
        if half_life is None:
            return signals  # Can't estimate — insufficient data
        if half_life > REVERSION_MAX_HALF_LIFE:
            return signals  # Mean-reversion too slow to trade

        # Confirmation filter: check that the spike has already started reverting.
        # Look at BBO history in the last 5s to find the peak and verify 2c+ pullback.
        hist = self.bbo_history.get(ticker)
        if not hist or len(hist) < 3:
            return signals

        now_ts = time.time()
        confirm_cutoff = now_ts - REVERSION_CONFIRM_WINDOW
        recent_mids = []
        for entry in reversed(hist):
            if entry.ts < confirm_cutoff:
                break
            recent_mids.append((entry.bid + entry.ask) // 2)

        if len(recent_mids) < 2:
            return signals

        hl_str = f"hl={half_life:.1f}s"

        if spike > 0:
            # Spiked up — peak is the max midpoint in the confirm window
            peak = max(recent_mids)
            current = recent_mids[0]  # most recent (reversed order)
            if peak - current < REVERSION_CONFIRM_REVERT:
                return signals  # Not yet reverting

            if book.best_bid is None:
                return signals
            entry = 100 - book.best_bid
            signals.append(ScanSignal(
                scan_type="mean_reversion",
                severity=severity(REVERSION_TARGET),
                ticker=ticker,
                game_id=info.game_id,
                entry_side="buy_no",
                entry_price=entry,
                target=entry - REVERSION_TARGET,
                stop=entry + REVERSION_STOP,
                description=(
                    f"{info.category} {info.team} {info.market_type}: "
                    f"spiked {spike:+d}c, reverting {peak - current}c from peak — "
                    f"depth={book.best_bid_size} {hl_str}"
                ),
                depth=book.best_bid_size,
            ))
        else:
            # Spiked down — trough is the min midpoint in the confirm window
            trough = min(recent_mids)
            current = recent_mids[0]
            if current - trough < REVERSION_CONFIRM_REVERT:
                return signals  # Not yet reverting

            if book.best_ask is None:
                return signals
            entry = book.best_ask
            signals.append(ScanSignal(
                scan_type="mean_reversion",
                severity=severity(REVERSION_TARGET),
                ticker=ticker,
                game_id=info.game_id,
                entry_side="buy_yes",
                entry_price=entry,
                target=entry + REVERSION_TARGET,
                stop=entry - REVERSION_STOP,
                description=(
                    f"{info.category} {info.team} {info.market_type}: "
                    f"dropped {spike:+d}c, reverting {current - trough}c from trough — "
                    f"depth={book.best_ask_size} {hl_str}"
                ),
                depth=book.best_ask_size,
            ))

        return signals

    # ------------------------------------------------------------------
    # Scan 3: Cross-Market Contradiction
    # ------------------------------------------------------------------

    def scan_contradiction(self, ticker: str) -> List[ScanSignal]:
        """
        3A: Monotonicity — same game, same team, same type, higher strike with higher ask.
        3B: Cross-event — spread ask > ML ask for same team.
        """
        signals = []
        info = self.market_info.get(ticker)
        if not info:
            return signals

        game = self.games.get(info.game_id)
        if not game:
            return signals

        # 3A: Monotonicity inversions (spread or total lines)
        if info.market_type in ("spread", "total"):
            same_type_tickers = game.get(info.market_type, [])
            # Group by team
            by_team: Dict[str, List[Tuple[float, str]]] = defaultdict(list)
            for t in same_type_tickers:
                mi = self.market_info.get(t)
                if not mi or mi.floor_strike is None:
                    continue
                by_team[mi.team].append((mi.floor_strike, t))

            team_group = by_team.get(info.team, [])
            if len(team_group) >= 2:
                sorted_group = sorted(team_group, key=lambda x: x[0])
                for i in range(len(sorted_group) - 1):
                    lo_strike, lo_ticker = sorted_group[i]
                    hi_strike, hi_ticker = sorted_group[i + 1]

                    lo_book = self.books.get(lo_ticker)
                    hi_book = self.books.get(hi_ticker)
                    if not lo_book or not hi_book:
                        continue
                    if lo_book.best_ask is None or hi_book.best_ask is None:
                        continue
                    if lo_book.best_bid is None or hi_book.best_bid is None:
                        continue

                    # Inversion: higher strike has higher ask
                    if hi_book.best_ask > lo_book.best_ask:
                        exec_profit = hi_book.best_bid - lo_book.best_ask
                        if exec_profit <= 0:
                            continue
                        depth = min(lo_book.best_ask_size, hi_book.best_bid_size)
                        if depth < CONTRADICTION_MIN_DEPTH:
                            continue
                        signals.append(ScanSignal(
                            scan_type="contradiction_mono",
                            severity=severity(exec_profit),
                            ticker=lo_ticker,
                            game_id=info.game_id,
                            entry_side="buy_yes",
                            entry_price=lo_book.best_ask,
                            target=lo_book.best_ask + exec_profit,
                            stop=lo_book.best_ask - 2,
                            description=(
                                f"{info.category} MONO {info.team}: "
                                f"strike {lo_strike}→{hi_strike}, "
                                f"ask {lo_book.best_ask}c→{hi_book.best_ask}c, "
                                f"exec={exec_profit}c depth={depth}"
                            ),
                            depth=depth,
                        ))

        # 3B: Cross-event — spread ask > ML ask for same team
        if info.market_type in ("moneyline", "spread"):
            ml_tickers = game.get("moneyline", [])
            sp_tickers = game.get("spread", [])

            for ml_t in ml_tickers:
                ml_info = self.market_info.get(ml_t)
                if not ml_info or ml_info.team != info.team:
                    continue
                ml_book = self.books.get(ml_t)
                if not ml_book or ml_book.best_ask is None or ml_book.best_bid is None:
                    continue

                for sp_t in sp_tickers:
                    sp_info = self.market_info.get(sp_t)
                    if not sp_info or sp_info.team != info.team:
                        continue
                    if sp_info.floor_strike is not None and sp_info.floor_strike <= 0:
                        continue  # Negative spreads can exceed ML

                    sp_book = self.books.get(sp_t)
                    if not sp_book or sp_book.best_ask is None or sp_book.best_bid is None:
                        continue

                    # Impossible: spread ask > ML ask
                    if sp_book.best_ask > ml_book.best_ask:
                        exec_profit = sp_book.best_bid - ml_book.best_ask
                        if exec_profit <= 0:
                            continue
                        depth = min(ml_book.best_ask_size, sp_book.best_bid_size)
                        if depth < CONTRADICTION_MIN_DEPTH:
                            continue
                        signals.append(ScanSignal(
                            scan_type="contradiction_cross",
                            severity=severity(exec_profit),
                            ticker=ml_t,
                            game_id=info.game_id,
                            entry_side="buy_yes",
                            entry_price=ml_book.best_ask,
                            target=ml_book.best_ask + exec_profit,
                            stop=ml_book.best_ask - 2,
                            description=(
                                f"{info.category} CROSS {info.team}: "
                                f"spread(>{sp_info.floor_strike}) ask={sp_book.best_ask}c > "
                                f"ML ask={ml_book.best_ask}c, exec={exec_profit}c depth={depth}"
                            ),
                            depth=depth,
                        ))

        return signals

    # ------------------------------------------------------------------
    # Scan 4: Resolution Farming
    # ------------------------------------------------------------------

    def scan_resolution(self, ticker: str) -> List[ScanSignal]:
        """Buy YES near 95-99c when close_time is within 5 min."""
        signals = []
        info = self.market_info.get(ticker)
        if not info or not info.close_time:
            return signals

        try:
            close_dt = datetime.fromisoformat(info.close_time.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return signals

        now = datetime.now(timezone.utc)
        secs_to_close = (close_dt - now).total_seconds()
        if secs_to_close <= 0 or secs_to_close > RESOLUTION_TIME:
            return signals

        book = self.books.get(ticker)
        if not book or book.best_ask is None:
            return signals

        if RESOLUTION_PRICE_RANGE[0] <= book.best_ask <= RESOLUTION_PRICE_RANGE[1]:
            if book.best_ask_size < 5:
                return signals
            signals.append(ScanSignal(
                scan_type="resolution",
                severity="HIGH" if book.best_ask >= 97 else "MEDIUM",
                ticker=ticker,
                game_id=info.game_id,
                entry_side="buy_yes",
                entry_price=book.best_ask,
                target=100,
                stop=book.best_ask - 3,
                description=(
                    f"{info.category} {info.team}: YES@{book.best_ask}c, "
                    f"{secs_to_close:.0f}s to close, settle→100c"
                ),
                depth=book.best_ask_size,
            ))

        return signals

    # ------------------------------------------------------------------
    # Signal dispatch + dedup
    # ------------------------------------------------------------------

    def on_bbo_update(self, ticker: str):
        """Run all scans on BBO change. Dedup signals."""
        self._record_bbo(ticker)

        # Warmup guard: don't scan until 60s of continuous BBO data
        if not self._is_warmed_up(ticker):
            return

        all_signals = []
        all_signals.extend(self.scan_momentum_lag(ticker))
        # BUG 3: mean_reversion DISABLED — 0 wins in 68 trades, sports spikes are real repricing
        # all_signals.extend(self.scan_mean_reversion(ticker))
        all_signals.extend(self.scan_contradiction(ticker))
        all_signals.extend(self.scan_resolution(ticker))

        now = time.time()
        for sig in all_signals:
            # Dedup key: scan_type + ticker + game_id
            key = f"{sig.scan_type}:{sig.ticker}:{sig.game_id}"
            if key in self._recent_signals and now - self._recent_signals[key] < self._signal_cooldown:
                continue
            self._recent_signals[key] = now
            self.stats["scan_signals"] += 1

            # Track signal by category
            info = self.market_info.get(sig.ticker)
            if info and info.category in self._category_stats:
                self._category_stats[info.category]["signals"] += 1

            print(f"[SIGNAL] [{sig.severity}] {sig.scan_type}: {sig.description}")
            self.open_paper_trade(sig)

        # Check existing paper trades
        self.check_paper_trades(ticker)

        # Clean old dedup entries
        if len(self._recent_signals) > 5000:
            cutoff = now - self._signal_cooldown * 2
            self._recent_signals = {k: v for k, v in self._recent_signals.items() if v > cutoff}

    # ------------------------------------------------------------------
    # Paper Trading
    # ------------------------------------------------------------------

    def open_paper_trade(self, signal: ScanSignal):
        """Open a paper trade from a scan signal."""
        # BUG 2 FIX: Don't open duplicate trades on the same ticker
        for existing in self.open_trades:
            if existing.ticker == signal.ticker:
                return  # Already have an open trade on this ticker

        # Extract spike_size and half_life from description for mean_reversion
        spike_size = None
        half_life_val = None
        if signal.scan_type == "mean_reversion":
            # Parse spike from description: "spiked +15c" or "dropped -18c"
            import re as _re
            spike_m = _re.search(r'(?:spiked|dropped)\s+([+-]?\d+)c', signal.description)
            if spike_m:
                spike_size = int(spike_m.group(1))
            hl_m = _re.search(r'hl=([0-9.]+)s', signal.description)
            if hl_m:
                half_life_val = float(hl_m.group(1))

        trade = PaperTrade(
            id=str(uuid.uuid4())[:8],
            scan_type=signal.scan_type,
            ticker=signal.ticker,
            game_id=signal.game_id,
            side=signal.entry_side,
            entry_price=signal.entry_price,
            entry_time=time.time(),
            target=signal.target,
            stop=signal.stop,
            description=signal.description,
            spike_size=spike_size,
            half_life=half_life_val,
            entry_depth=signal.depth,
        )
        self.open_trades.append(trade)
        self.stats["paper_trades_opened"] += 1
        hl_tag = f" hl={half_life_val:.1f}s" if half_life_val else ""
        print(
            f"[PAPER] OPEN {trade.id}: {trade.scan_type} {trade.side} "
            f"{trade.ticker}@{trade.entry_price}c target={trade.target} stop={trade.stop} "
            f"depth={signal.depth}{hl_tag}"
        )

    def check_paper_trades(self, updated_ticker: str):
        """Check open trades for exits on BBO update."""
        now = time.time()
        still_open = []

        for trade in self.open_trades:
            if trade.ticker != updated_ticker:
                still_open.append(trade)
                continue

            # BUG 1 FIX: Skip exit evaluation on the same BBO update that opened
            # the trade. Increment counter first, then only evaluate exits if we've
            # seen at least 1 subsequent BBO update.
            trade.bbo_updates_seen += 1
            if trade.bbo_updates_seen < 2:
                still_open.append(trade)
                continue

            book = self.books.get(trade.ticker)
            if not book:
                still_open.append(trade)
                continue

            exit_price = None
            exit_reason = None

            if trade.side == "buy_yes":
                # Check if bid hit target
                if book.best_bid is not None and book.best_bid >= trade.target:
                    exit_price = book.best_bid
                    exit_reason = "TARGET"
                # Check stop
                elif book.best_bid is not None and book.best_bid <= trade.stop:
                    exit_price = book.best_bid
                    exit_reason = "STOP"
                # Check timeout
                elif now - trade.entry_time > PAPER_TIMEOUT:
                    exit_price = book.best_bid if book.best_bid is not None else trade.entry_price
                    exit_reason = "TIMEOUT"
            elif trade.side == "buy_no":
                # For buy_no, profit when ask drops (underlying drops)
                # Entry = 100 - bid_at_entry. Current value = 100 - current_ask
                if book.best_ask is not None:
                    current_no_value = 100 - book.best_ask
                    if current_no_value >= trade.target:
                        exit_price = current_no_value
                        exit_reason = "TARGET"
                    elif current_no_value <= trade.stop:
                        exit_price = current_no_value
                        exit_reason = "STOP"
                    elif now - trade.entry_time > PAPER_TIMEOUT:
                        exit_price = current_no_value
                        exit_reason = "TIMEOUT"

            if exit_price is not None and exit_reason is not None:
                trade.exit_price = exit_price
                trade.exit_time = now
                trade.exit_reason = exit_reason
                trade.hold_time = now - trade.entry_time
                if trade.side == "buy_yes":
                    trade.pnl_cents = exit_price - trade.entry_price
                else:
                    trade.pnl_cents = exit_price - trade.entry_price
                self.closed_trades.append(trade)
                self.stats["paper_trades_closed"] += 1
                pnl_str = f"{trade.pnl_cents:+d}c" if trade.pnl_cents is not None else "?"
                ht_str = f" hold={trade.hold_time:.0f}s" if trade.hold_time else ""
                print(
                    f"[PAPER] CLOSE {trade.id}: {trade.exit_reason} "
                    f"entry={trade.entry_price}c exit={exit_price}c pnl={pnl_str}{ht_str}"
                )
            else:
                still_open.append(trade)

        self.open_trades = still_open

    def _check_paper_timeouts(self):
        """Check all open trades for timeout (called periodically)."""
        now = time.time()
        still_open = []
        for trade in self.open_trades:
            if now - trade.entry_time > PAPER_TIMEOUT:
                book = self.books.get(trade.ticker)
                if trade.side == "buy_yes":
                    exit_price = book.best_bid if book and book.best_bid is not None else trade.entry_price
                else:
                    exit_price = (100 - book.best_ask) if book and book.best_ask is not None else trade.entry_price
                trade.exit_price = exit_price
                trade.exit_time = now
                trade.exit_reason = "TIMEOUT"
                trade.hold_time = now - trade.entry_time
                trade.pnl_cents = exit_price - trade.entry_price
                self.closed_trades.append(trade)
                self.stats["paper_trades_closed"] += 1
                pnl_str = f"{trade.pnl_cents:+d}c" if trade.pnl_cents is not None else "?"
                print(f"[PAPER] TIMEOUT {trade.id}: pnl={pnl_str} hold={trade.hold_time:.0f}s")
            else:
                still_open.append(trade)
        self.open_trades = still_open

    def save_paper_trades(self):
        """Save all paper trades to JSON."""
        all_trades = [asdict(t) for t in self.closed_trades + self.open_trades]
        try:
            with open(PAPER_TRADES_FILE, "w") as f:
                json.dump(all_trades, f, indent=2)
        except Exception as e:
            print(f"[PAPER] Save error: {e}")

    # ------------------------------------------------------------------
    # Stats output
    # ------------------------------------------------------------------

    def dump_stats(self):
        now = time.time()
        uptime = now - self.stats["started"]
        uptime_str = f"{uptime / 3600:.1f}h" if uptime > 3600 else f"{uptime / 60:.1f}m"

        # Paper trade P&L summary
        total_pnl = sum(t.pnl_cents for t in self.closed_trades if t.pnl_cents is not None)
        winners = sum(1 for t in self.closed_trades if t.pnl_cents is not None and t.pnl_cents > 0)
        losers = sum(1 for t in self.closed_trades if t.pnl_cents is not None and t.pnl_cents < 0)

        # P&L by scan type
        pnl_by_type: Dict[str, List[int]] = defaultdict(list)
        for t in self.closed_trades:
            if t.pnl_cents is not None:
                pnl_by_type[t.scan_type].append(t.pnl_cents)

        lines = [
            f"=== INTRA-KALSHI LIVE SCANNER STATS ({datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}) ===",
            f"Uptime: {uptime_str}",
            f"WS: connected={self.ws_connected} msgs={self.stats['ws_messages']} "
            f"snaps={self.stats['snapshots']} deltas={self.stats['deltas']} "
            f"bbo_updates={self.stats['bbo_updates']}",
            f"Discovery: {self.stats['events_discovered']} games, "
            f"{self.stats['tickers_subscribed']} tickers subscribed",
            f"Signals: {self.stats['scan_signals']} total, "
            f"seq_gaps={self._seq_gaps}, ws_reconnects={self.stats.get('ws_reconnects', 0)}",
            f"Paper: {self.stats['paper_trades_opened']} opened, "
            f"{self.stats['paper_trades_closed']} closed, "
            f"{len(self.open_trades)} open",
            f"P&L: total={total_pnl:+d}c  W={winners} L={losers} "
            f"(win_rate={'N/A' if not self.closed_trades else f'{winners / len(self.closed_trades) * 100:.0f}%'})",
        ]

        for scan_type, pnls in sorted(pnl_by_type.items()):
            total = sum(pnls)
            w = sum(1 for p in pnls if p > 0)
            l = sum(1 for p in pnls if p < 0)
            lines.append(f"  {scan_type}: {total:+d}c ({len(pnls)} trades, W={w} L={l})")

        # Active books summary
        active_books = sum(1 for b in self.books.values() if b.best_bid is not None)
        lines.append(f"Books: {active_books}/{len(self.books)} active")

        # Category breakdown
        if self._category_stats:
            lines.append("Categories:")
            sorted_cats = sorted(
                self._category_stats.items(),
                key=lambda x: -x[1]["signals"]
            )
            for cat, cdata in sorted_cats:
                cat_label = cat if cat else "unknown"
                ev_count = len(cdata["events"]) if isinstance(cdata["events"], set) else cdata["events"]
                lines.append(
                    f"  {cat_label}: {ev_count} events, "
                    f"{cdata['tickers']} tickers, {cdata['signals']} signals"
                )

        output = "\n".join(lines)
        print(f"\n{output}\n")

        # Write to log file
        try:
            with open(STATS_LOG, "a") as f:
                f.write(output + "\n\n")
        except Exception as e:
            print(f"[STATS] Log write error: {e}")

    # ------------------------------------------------------------------
    # WS Listen Loop
    # ------------------------------------------------------------------

    async def ws_listen(self):
        """Main WS message loop with watchdog reconnect."""
        while not self.shutdown:
            if not self.ws_connected or not self.ws:
                await asyncio.sleep(self.ws_reconnect_delay)
                self.ws_reconnect_delay = min(self.ws_reconnect_delay * 2, WS_RECONNECT_MAX)
                if await self.ws_connect():
                    await self.ws_subscribe_all()
                continue

            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=WS_WATCHDOG_TIMEOUT)
                self.stats["ws_messages"] += 1

                data = json.loads(msg)
                msg_type = data.get("type", "")
                msg_data = data.get("msg", {})

                # Sequence gap detection
                _sid = data.get("sid")
                _seq = data.get("seq")
                _ticker = msg_data.get("market_ticker", "")

                if _sid is not None and _seq is not None and _ticker:
                    if msg_type == "orderbook_snapshot":
                        self._seq_tracker[_sid] = {
                            "ticker": _ticker,
                            "last_seq": _seq,
                        }
                    elif msg_type == "orderbook_delta":
                        tracker = self._seq_tracker.get(_sid)
                        if tracker:
                            expected = tracker["last_seq"] + 1
                            if _seq != expected:
                                self._seq_gaps += 1
                                gap = _seq - tracker["last_seq"] - 1
                                print(f"[SEQ-GAP] {_ticker}: expected {expected}, got {_seq} (missed {gap})")
                                try:
                                    await self.ws_subscribe([_ticker])
                                except Exception as e:
                                    print(f"[SEQ-GAP] Re-sub failed: {e}")
                            tracker["last_seq"] = _seq
                        else:
                            self._seq_tracker[_sid] = {
                                "ticker": _ticker,
                                "last_seq": _seq,
                            }

                # Process message
                if msg_type == "orderbook_snapshot":
                    ticker = msg_data.get("market_ticker")
                    if ticker:
                        old_bid = self.books.get(ticker, LocalBook(ticker)).best_bid
                        old_ask = self.books.get(ticker, LocalBook(ticker)).best_ask
                        self.apply_snapshot(ticker, msg_data)
                        book = self.books.get(ticker)
                        if book and (book.best_bid != old_bid or book.best_ask != old_ask):
                            self.on_bbo_update(ticker)

                elif msg_type == "orderbook_delta":
                    ticker = msg_data.get("market_ticker")
                    if ticker:
                        old_bid = self.books.get(ticker, LocalBook(ticker)).best_bid
                        old_ask = self.books.get(ticker, LocalBook(ticker)).best_ask
                        self.apply_delta(ticker, msg_data)
                        book = self.books.get(ticker)
                        if book and (book.best_bid != old_bid or book.best_ask != old_ask):
                            self.on_bbo_update(ticker)

                elif msg_type == "subscribed":
                    print(f"[WS] Subscribed confirmed: {msg_data}")

                elif msg_type == "error":
                    print(f"[WS] Error: {msg_data}")

            except asyncio.TimeoutError:
                # Watchdog: no message in WS_WATCHDOG_TIMEOUT seconds
                print(f"[WS] Watchdog timeout ({WS_WATCHDOG_TIMEOUT}s no messages) — reconnecting")
                self.stats["ws_reconnects"] = self.stats.get("ws_reconnects", 0) + 1
                try:
                    if self.ws:
                        await self.ws.close()
                except Exception:
                    pass
                self.ws_connected = False
                self.ws = None
                # Loop will reconnect and re-subscribe on next iteration
            except websockets.exceptions.ConnectionClosed as e:
                print(f"[WS] Connection closed: {e}")
                self.ws_connected = False
                self.ws = None
            except Exception as e:
                print(f"[WS] Error: {e}")

    # ------------------------------------------------------------------
    # Background tasks
    # ------------------------------------------------------------------

    async def stats_loop(self):
        """Dump stats every STATS_INTERVAL seconds."""
        while not self.shutdown:
            await asyncio.sleep(STATS_INTERVAL)
            self.dump_stats()
            self.save_paper_trades()

    async def paper_trade_monitor(self):
        """Check paper trade timeouts every second."""
        while not self.shutdown:
            await asyncio.sleep(1)
            self._check_paper_timeouts()

    async def rediscovery_loop(self, session):
        """Re-discover events every 30 min to pick up new games."""
        while not self.shutdown:
            await asyncio.sleep(REDISCOVERY_INTERVAL)
            try:
                new_count = await self.discover_events(session)
                if new_count > 0 and self.ws_connected:
                    await self.ws_subscribe_all()
                    print(f"[REDISCOVERY] Subscribed to {new_count} new tickers")
            except Exception as e:
                print(f"[REDISCOVERY] Error: {e}")

    # ------------------------------------------------------------------
    # Main
    # ------------------------------------------------------------------

    async def run(self):
        """Main entry point."""
        self._load_credentials()

        async with aiohttp.ClientSession() as session:
            # Initial discovery
            await self.discover_events(session)

            # Connect WS
            if not await self.ws_connect():
                print("[FATAL] Cannot connect to WS")
                return

            # Subscribe to all qualified tickers
            await self.ws_subscribe_all()

            # Initial stats
            self.dump_stats()

            # Run concurrent tasks
            try:
                await asyncio.gather(
                    self.ws_listen(),
                    self.stats_loop(),
                    self.paper_trade_monitor(),
                    self.rediscovery_loop(session),
                )
            except asyncio.CancelledError:
                print("[SCAN] Shutting down...")
            finally:
                self.save_paper_trades()
                self.dump_stats()
                if self.ws:
                    await self.ws.close()
                print("[SCAN] Shutdown complete")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    scanner = LiveScanner()

    # Graceful shutdown
    def handle_signal(sig, frame):
        print(f"\n[SCAN] Received signal {sig}, shutting down...")
        scanner.shutdown = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print("=" * 60)
    print("  INTRA-KALSHI LIVE PAPER TRADING SCANNER")
    print("  PAPER MODE — NO REAL ORDERS")
    print("=" * 60)

    asyncio.run(scanner.run())


if __name__ == "__main__":
    main()
