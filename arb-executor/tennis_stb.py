#!/usr/bin/env python3
"""
Tennis Sell-The-Bounce (STB) — Live Trading Module
===================================================
Buy dislocation dips on ATP/WTA match markets, exit +7c via resting sell.
Standalone module — does NOT touch swing_ladder.py or live_scanner.py.
"""

import asyncio
import aiohttp
import base64
import json
import os
import sys
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"

SERIES = ["KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH"]
CONTRACTS = 25
CONTRACTS_92PLUS = 50                  # 92c+ maker entries: 50ct (7c edge * 50 = $3.50/trade)
EXIT_BOUNCE = 7               # sell at entry_ask + 7c

# Entry filters
MAX_COMBINED_MID = 97          # combined MID of both sides ≤ 97c (dislocation)
MIN_ENTRY_ASK = 55             # entry side ask >= 55c
MAX_ENTRY_ASK = 90             # skip entries > 90c (backtest: 0% win rate above 94c)
MAX_SPREAD = 4                 # ask - bid ≤ 4c
MIN_MARKET_VOLUME_MAIN = 1000       # main draw volume threshold
MIN_MARKET_VOLUME_CHALLENGER = 500  # challenger: lower threshold (thinner books)
MAX_HOURS_TO_EXPIRY = 6        # skip if expected_expiration > 6h away (match not started)

# Conditional time stop — CHALLENGER series only
# At COND_STOP_MINUTES: if bid >= entry, hold and re-check every COND_STOP_RECHECK seconds
# If bid < entry at any check, cancel resting sell and market exit at bid-2c
COND_STOP_MINUTES = 7
COND_STOP_RECHECK = 60         # re-check every 60s after initial checkpoint
ENABLE_COND_STOP = False       # DISABLED — backtest shows no-stop optimal for all tennis
CHALLENGER_SERIES = ["KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH"]
MAIN_DRAW_SERIES = ["KXATPMATCH", "KXWTAMATCH"]
MAIN_DRAW_CONTRACTS = 25       # main draw: 10ct (collapse filter active)

# Collapse filter — reject entry if bid dropped in lookback window, re-enter later
COLLAPSE_DROP_THRESHOLD = 6    # reject if bid dropped >= 6c
COLLAPSE_LOOKBACK_SEC = 600    # 10 minute lookback window
COLLAPSE_REENTRY_DELAY = 600   # re-enter after 10 minutes

MAX_RPS = 10
WS_SUBSCRIBE_BATCH = 100
WS_PING_INTERVAL = 30
DISCOVERY_INTERVAL = 300       # 5 min
RESUB_INTERVAL = 60            # re-subscribe BBO every 60s
STATS_INTERVAL = 1800          # P&L summary every 30 min
BALANCE_CHECK_INTERVAL = 120   # check balance every 2 min
STALE_BUY_TIMEOUT = 30         # cancel unfilled buy after 30 seconds
RETRY_WINDOW = 60              # max seconds to retry after first partial fill
RETRY_INTERVAL = 30            # seconds between retry attempts
GAME_STATE_TIMEOUT = 0.5       # 500ms max for live_data call

LOG_FILE = "/tmp/tennis_stb.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_log_file = None

def log(msg: str):
    """Print to stdout and append to log file."""
    print(msg, flush=True)
    global _log_file
    try:
        if _log_file is None:
            _log_file = open(LOG_FILE, "a", buffering=1)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        _log_file.write(f"[{ts}] {msg}\n")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def load_credentials():
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(env_path)
    except ImportError:
        pass
    api_key = os.getenv("KALSHI_API_KEY", "f3b064d1-a02e-42a4-b2b1-132834694d23")
    pem_path = Path(__file__).resolve().parent / "kalshi.pem"
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
# Rate limiter
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
# REST helpers
# ---------------------------------------------------------------------------
async def api_get(session, api_key, private_key, path, rl) -> Optional[dict]:
    url = f"{BASE_URL}{path}"
    for backoff in [1, 2, 4, None]:
        await rl.acquire()
        headers = auth_headers(api_key, private_key, "GET", path)
        try:
            async with session.get(url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    return await r.json()
                if r.status == 429 and backoff is not None:
                    await asyncio.sleep(backoff)
                    continue
                body = await r.text()
                log(f"  [ERR] GET {r.status} {path}: {body[:200]}")
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if backoff is not None:
                await asyncio.sleep(backoff)
                continue
            log(f"  [FAIL] GET {e}")
            return None
    return None


async def api_post(session, api_key, private_key, path, payload, rl) -> Optional[dict]:
    url = f"{BASE_URL}{path}"
    for backoff in [1, 2, 4, None]:
        await rl.acquire()
        headers = auth_headers(api_key, private_key, "POST", path)
        try:
            async with session.post(url, headers=headers, json=payload,
                                    timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status in (200, 201):
                    return await r.json()
                if r.status == 429 and backoff is not None:
                    log(f"  [429] POST {path}, retry {backoff}s")
                    await asyncio.sleep(backoff)
                    continue
                body = await r.text()
                log(f"  [ERR] POST {r.status} {path}: {body[:200]}")
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if backoff is not None:
                await asyncio.sleep(backoff)
                continue
            log(f"  [FAIL] POST {e}")
            return None
    return None


async def api_delete(session, api_key, private_key, path, rl) -> Optional[dict]:
    url = f"{BASE_URL}{path}"
    for backoff in [1, 2, 4, None]:
        await rl.acquire()
        headers = auth_headers(api_key, private_key, "DELETE", path)
        try:
            async with session.delete(url, headers=headers,
                                      timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status in (200, 204):
                    try:
                        return await r.json()
                    except Exception:
                        return {}
                if r.status == 429 and backoff is not None:
                    await asyncio.sleep(backoff)
                    continue
                body = await r.text()
                log(f"  [ERR] DELETE {r.status} {path}: {body[:200]}")
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if backoff is not None:
                await asyncio.sleep(backoff)
                continue
            log(f"  [FAIL] DELETE {e}")
            return None
    return None


# ---------------------------------------------------------------------------
# Local orderbook
# ---------------------------------------------------------------------------
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


def recalc_bbo(book: LocalBook):
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


# ---------------------------------------------------------------------------
# Position tracking
# ---------------------------------------------------------------------------
@dataclass
class Position:
    ticker: str
    event_ticker: str
    side: str               # e.g. "HUR" or "KOV"
    entry_ask: int          # price paid (ask at time of entry)
    entry_bid: int
    entry_spread: int
    combined_ask: int
    entry_ts: float
    contracts: int
    buy_order_id: Optional[str] = None
    buy_confirmed: bool = False   # True only after buy fill is confirmed
    buy_fill_ts: Optional[float] = None  # timestamp of buy fill confirmation
    sell_order_id: Optional[str] = None
    sell_price: int = 0     # target exit price = entry_ask + 7
    filled: bool = False
    settled: bool = False
    time_stopped: bool = False   # True if exited via conditional time stop
    exit_price: Optional[int] = None
    exit_ts: Optional[float] = None
    # Observation: trajectory tracking (bid at fixed intervals after entry)
    trajectory: Dict[str, Optional[int]] = field(default_factory=lambda: {
        "15s": None, "30s": None, "1m": None, "2m": None, "3m": None,
        "5m": None, "10m": None, "15m": None, "20m": None,
    })
    trajectory_logged: bool = False
    # Observation: overshoot tracking (max bid seen after entry)
    max_bid_after_entry: Optional[int] = None
    # Enriched trade logging (v3)
    game_state_at_entry: str = ""       # raw game state string
    who_winning_at_entry: str = ""      # leading/trailing/tied
    collapse_triggered: bool = False     # was collapse filter triggered?
    pre_entry_price_10m: Optional[int] = None  # bid 10 min before entry
    depth_snapshot: Optional[dict] = None  # orderbook depth at entry
    csv_entry_logged: bool = False
    csv_exit_logged: bool = False
    entry_mode: str = ""  # "" = standard STB, "stb_92plus_maker" = 92c+ maker
    volume_tier: str = ""  # "thin" (500-999) or "standard" (1000+)

    # Partial fill retry tracking
    retry_remaining: int = 0          # contracts still needed
    retry_start_ts: float = 0.0       # when retry window started
    retry_attempts: int = 0           # number of retry buys placed
    retry_active: bool = False        # currently in retry mode
    highest_fill_price: int = 0       # track max fill price across retries



# ---------------------------------------------------------------------------
# Main bot
# ---------------------------------------------------------------------------
class TennisSTB:
    def __init__(self):
        self.api_key, self.private_key = load_credentials()
        self.rl = RateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws = None
        self.ws_connected = False
        self.msg_id = 0
        self.ws_msg_count = 0
        self._first_scan_printed = False

        # Market state
        self.books: Dict[str, LocalBook] = {}
        self.ticker_to_event: Dict[str, str] = {}   # ticker -> event_ticker
        self.event_tickers: Dict[str, Set[str]] = {} # event_ticker -> {ticker_a, ticker_b}
        self.subscribed: Set[str] = set()
        self.known_events: Set[str] = set()
        self.min_combined: Dict[str, int] = {}   # event_ticker -> lowest combined ask seen
        self.global_min_combined: int = 999
        self.ticker_expiry: Dict[str, float] = {}  # ticker -> expected_expiration epoch

        # Game state (milestone) cache
        self.event_milestones: Dict[str, str] = {}  # event_ticker -> milestone_id
        self.game_state_rejects: int = 0
        self.game_state_fails: int = 0

        # Collapse filter state
        self.bid_history: Dict[str, List] = {}         # ticker -> [(ts, bid), ...]
        self.ticker_volume: Dict[str, int] = {}        # market volume at discovery
        self.collapse_rejected: Set[str] = set()       # tickers pending re-entry
        self.pending_reentries: Dict[str, tuple] = {}  # ticker -> (reentry_time, orig_bid, attempt)
        self._reentry_attempt: Dict[str, int] = {}     # collapse re-entry attempt counter
        self.total_collapse_rejects: int = 0
        self.total_reentries: int = 0
        self.spread_confirmed: Dict[str, bool] = {}  # 2-tick spread confirmation
        self.entered_events: Set[str] = set()         # event-level dedup
        self.total_reentry_skips: int = 0

        # Position tracking
        self.positions: Dict[str, Position] = {}     # ticker -> Position
        self.entered_sides: Set[str] = set()         # tickers we've entered (never re-enter)
        self.resting_sells: Dict[str, str] = {}      # ticker -> sell_order_id

        # P&L
        self.cash_balance: float = 0.0
        self.total_pnl_cents: int = 0
        self.total_entries: int = 0
        self.total_wins: int = 0
        self.total_losses: int = 0
        self.total_time_stops: int = 0
        self.total_fees_cents: int = 0
        self.start_time = time.time()

        # 92c+ settlement mode state (maker-based, main draw only)
        self.sustained_90_ticks: Dict[str, int] = {}   # ticker -> consecutive ticks >= 90c
        self.mode_92_entered: Set[str] = set()          # tickers entered via 92c+ mode
        self.mode_92_bids: Dict[str, str] = {}          # ticker -> resting buy order_id at 92c

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
            import websockets
            self.ws = await websockets.connect(
                WS_URL, additional_headers=headers,
                ping_interval=WS_PING_INTERVAL, ping_timeout=10,
                max_size=10_000_000,
            )
            self.ws_connected = True
            log("[WS] Connected")
            return True
        except Exception as e:
            log(f"[WS] Connect failed: {e}")
            self.ws_connected = False
            return False

    async def ws_subscribe(self, tickers: List[str]):
        if not self.ws_connected or not self.ws:
            return
        new_tickers = [t for t in tickers if t not in self.subscribed]
        if not new_tickers:
            return
        for i in range(0, len(new_tickers), WS_SUBSCRIBE_BATCH):
            batch = new_tickers[i:i + WS_SUBSCRIBE_BATCH]
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
                self.subscribed.update(batch)
                await asyncio.sleep(0.05)
            except Exception as e:
                log(f"[WS] Subscribe failed: {e}")
        log(f"[WS] Subscribed {len(new_tickers)} tickers (total: {len(self.subscribed)})")

    async def ws_resubscribe_all(self):
        """Periodic full re-subscribe to avoid phantom depth."""
        if not self.ws_connected or not self.ws or not self.subscribed:
            return
        all_tickers = list(self.subscribed)
        for i in range(0, len(all_tickers), WS_SUBSCRIBE_BATCH):
            batch = all_tickers[i:i + WS_SUBSCRIBE_BATCH]
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
                await asyncio.sleep(0.05)
            except Exception as e:
                log(f"[WS] Resub failed: {e}")

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
        recalc_bbo(book)
        book.last_update = time.time()
        self.books[ticker] = book

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
        recalc_bbo(book)
        book.last_update = time.time()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_expiry(ts_str: str) -> Optional[float]:
        """Parse ISO timestamp to epoch seconds."""
        if not ts_str or ts_str.startswith("0001"):
            return None
        try:
            ts_clean = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(ts_clean).timestamp()
        except Exception:
            return None

    async def fetch_milestones(self):
        """Fetch milestone IDs for all active events and cache them."""
        fetched = 0
        for series in SERIES:
            path = (f"/trade-api/v2/events?status=open&series_ticker={series}"
                    f"&limit=50&with_milestones=true")
            data = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
            if not data:
                continue
            for m in data.get("milestones", []):
                mid = m.get("id", "")
                if not mid:
                    continue
                for et in m.get("primary_event_tickers", []):
                    if et not in self.event_milestones:
                        self.event_milestones[et] = mid
                        fetched += 1
        if fetched:
            log(f"[MILESTONES] Cached {fetched} new milestone IDs "
                f"(total: {len(self.event_milestones)})")

    async def fetch_game_state(self, event_ticker: str) -> Optional[dict]:
        """Fetch live game state for an event via milestone API. Returns None on failure."""
        mid = self.event_milestones.get(event_ticker)
        if not mid:
            return None
        path = f"/trade-api/v2/live_data/scores/milestone/{mid}"
        url = f"{BASE_URL}{path}"
        ts = str(int(time.time() * 1000))
        sign_path = path.split("?")[0]
        headers = {
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-SIGNATURE": sign_request(self.private_key, ts, "GET", sign_path),
            "KALSHI-ACCESS-TIMESTAMP": ts,
            "Content-Type": "application/json",
        }
        try:
            async with self.session.get(
                url, headers=headers,
                timeout=aiohttp.ClientTimeout(total=GAME_STATE_TIMEOUT)
            ) as r:
                if r.status == 200:
                    return await r.json()
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    def check_tennis_game_state(self, ticker: str, game_data: dict) -> Optional[str]:
        """Check tennis game state filters. Returns rejection reason or None if OK."""
        live = game_data.get("live_data", {})
        details = live.get("details", {})
        status = details.get("status", "").lower()

        # Reject ended/completed matches
        if status in ("ended", "completed", "closed", "finished", "retired"):
            return f"match {status}"

        # Reject scheduled/not started (backup for pre-game filter)
        if status in ("scheduled", "not_started", "created"):
            return f"match {status}"

        # Check set scores: reject if player is down 0-2 sets
        # Determine which side we're buying from ticker
        side = ticker.split("-")[-1]
        p1_score = details.get("competitor1_overall_score", 0)
        p2_score = details.get("competitor2_overall_score", 0)

        # Try to map ticker side to competitor
        # competitor1/2 names aren't in live_data, but we can use round_scores
        # For rejection: if EITHER player is down 0-2, we reject buying the down player
        # Since we don't know which competitor maps to which ticker side,
        # reject if ANY player is down 0-2 (conservative)
        try:
            p1_sets = int(p1_score) if p1_score else 0
            p2_sets = int(p2_score) if p2_score else 0
        except (ValueError, TypeError):
            p1_sets = 0
            p2_sets = 0

        if p1_sets == 0 and p2_sets >= 2:
            return f"player down 0-{p2_sets} sets"
        if p2_sets == 0 and p1_sets >= 2:
            return f"player down 0-{p1_sets} sets"

        # Deciding set filter REMOVED (Phase 1)

        # Fix 1: Reject if match just started (set 1, <3 games played)
        # Early-match entries have no game state edge — just thin book noise
        p1_rounds = details.get("competitor1_round_scores", [])
        p2_rounds = details.get("competitor2_round_scores", [])
        completed_sets = max(p1_sets, p2_sets)
        if completed_sets == 0 and p1_rounds and p2_rounds:
            # In set 1 — check game count
            try:
                g1 = int(p1_rounds[0].get("score", 0)) if p1_rounds else 0
                g2 = int(p2_rounds[0].get("score", 0)) if p2_rounds else 0
            except (ValueError, TypeError, IndexError):
                g1, g2 = 0, 0
            if max(g1, g2) < 3:
                return f"match too early: {g1}-{g2} in set 1 (need 3+ games)"

        return None  # passed all filters

    def check_collapse(self, ticker: str):
        """Check if bid dropped >= COLLAPSE_DROP_THRESHOLD in lookback window.
        Returns (drop, max_bid, current_bid) or None."""
        book = self.books.get(ticker)
        if not book or book.best_bid is None:
            return None
        current_bid = book.best_bid
        history = self.bid_history.get(ticker, [])
        if not history:
            return None
        cutoff = time.time() - COLLAPSE_LOOKBACK_SEC
        max_bid = current_bid
        for ts, bid in history:
            if ts >= cutoff and bid > max_bid:
                max_bid = bid
        drop = max_bid - current_bid
        if drop >= COLLAPSE_DROP_THRESHOLD:
            return (drop, max_bid, current_bid)
        return None

    async def discover_markets(self):
        """Find all open tennis match markets. Filters ghost/illiquid and pre-match."""
        all_tickers = []
        now = time.time()
        skipped_pregame = 0
        for series in SERIES:
            cursor = ""
            pages = 0
            while pages < 10:
                path = f"/trade-api/v2/markets?limit=100&status=open&series_ticker={series}"
                if cursor:
                    path += f"&cursor={cursor}"
                data = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
                if not data:
                    break
                markets = data.get("markets", [])
                if not markets:
                    break
                for m in markets:
                    ticker = m["ticker"]
                    vol = m.get("volume", 0) or 0
                    lp = m.get("last_price", 0) or 0
                    is_chall_market = any(ticker.startswith(s) for s in CHALLENGER_SERIES)
                    min_vol = MIN_MARKET_VOLUME_CHALLENGER if is_chall_market else MIN_MARKET_VOLUME_MAIN
                    if vol < min_vol and lp == 0:
                        print(f"  [SKIP] {ticker} volume={vol} last_price={lp} — ghost market")
                        continue
                    if vol < min_vol:
                        print(f"  [SKIP] {ticker} volume={vol} \u2014 below minimum (threshold={min_vol})")
                        continue
                    self.ticker_volume[ticker] = vol

                    # Store/update expiry for pre-match filter
                    expiry_str = m.get("expected_expiration_time", "")
                    expiry_epoch = self._parse_expiry(expiry_str)
                    if expiry_epoch:
                        self.ticker_expiry[ticker] = expiry_epoch

                    # Pre-match filter: skip if expiry > MAX_HOURS_TO_EXPIRY from now
                    if expiry_epoch:
                        hours_until = (expiry_epoch - now) / 3600.0
                        if hours_until > MAX_HOURS_TO_EXPIRY:
                            event_ticker = m.get("event_ticker", "")
                            if event_ticker not in self.known_events:
                                side = ticker.split("-")[-1]
                                print(f"  [SKIP_PREGAME] {side} expires={expiry_str[:16]} "
                                      f"hours_until={hours_until:.1f} — match not started")
                            skipped_pregame += 1
                            continue

                    event_ticker = m["event_ticker"]
                    self.ticker_to_event[ticker] = event_ticker
                    if event_ticker not in self.event_tickers:
                        self.event_tickers[event_ticker] = set()
                    self.event_tickers[event_ticker].add(ticker)
                    all_tickers.append(ticker)
                    if event_ticker not in self.known_events:
                        self.known_events.add(event_ticker)
                cursor = data.get("cursor", "")
                pages += 1
                if not cursor:
                    break
        if skipped_pregame:
            log(f"[DISCOVERY] Skipped {skipped_pregame} pre-match tickers "
                  f"(expiry > {MAX_HOURS_TO_EXPIRY}h away)")

        # Fetch milestone IDs for game state integration
        await self.fetch_milestones()

        return all_tickers

    # ------------------------------------------------------------------
    # Entry logic
    # ------------------------------------------------------------------
    def get_partner_ticker(self, ticker: str) -> Optional[str]:
        """Get the other side of the same match."""
        et = self.ticker_to_event.get(ticker)
        if not et:
            return None
        tickers = self.event_tickers.get(et, set())
        for t in tickers:
            if t != ticker:
                return t
        return None

    # ------------------------------------------------------------------
    # 92c+ Settlement Mode -- sustained filter + maker entry
    # ------------------------------------------------------------------
    def _check_sustained_90(self, ticker: str, price: int) -> bool:
        """Track consecutive ticks >= 90c. Returns True when 5+ sustained."""
        if price >= 90:
            self.sustained_90_ticks[ticker] = self.sustained_90_ticks.get(ticker, 0) + 1
        else:
            self.sustained_90_ticks[ticker] = 0
        return True  # sustained filter disabled (0-tick)

    def _is_main_draw(self, ticker: str) -> bool:
        """Returns True if ticker is ATP/WTA main draw (not challenger)."""
        return any(ticker.startswith(s) for s in MAIN_DRAW_SERIES)

    async def post_92c_maker_bid(self, ticker: str):
        """Post resting buy bid at 92c for 25ct (maker entry)."""
        side = ticker.split("-")[-1]
        et = self.ticker_to_event.get(ticker, "?")

        # Anti-stack: check portfolio
        pos_check_path = f"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1"
        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)
        if pos_check:
            existing = [p for p in pos_check.get("market_positions", []) if p.get("position", 0) > 0]
            if existing:
                log(f"[92+_SKIP_STACKED] {ticker} already holding {existing[0].get('position',0)}ct")
                self.mode_92_entered.add(ticker)
                self.entered_sides.add(ticker)
                return

        path = "/trade-api/v2/portfolio/orders"
        payload = {
            "ticker": ticker,
            "action": "buy",
            "side": "yes",
            "count": CONTRACTS_92PLUS,
            "type": "limit",
            "yes_price": 92,
            "post_only": True,  # maker -- must rest
            "client_order_id": str(uuid.uuid4()),
        }

        result = await api_post(self.session, self.api_key, self.private_key,
                                path, payload, self.rl)
        if not result or result.get("error"):
            err = result.get("error", {}) if result else {}
            log(f"[92+_BID_FAIL] {side} err={err}")
            return

        order = result.get("order", {})
        order_id = order.get("order_id", "")
        status = order.get("status", "")

        if status == "executed":
            # Filled immediately (crossed the spread) -- treat as taker fill
            log(f"[92+_BID_INSTANT_FILL] {side} 92c bid filled immediately")
            self.mode_92_entered.add(ticker)
            self.entered_sides.add(ticker)
            self.entered_events.add(et)
            self.total_entries += 1
            entry_fee = CONTRACTS_92PLUS
            self.total_fees_cents += entry_fee

            book = self.books.get(ticker)
            bid = book.best_bid if book and book.best_bid is not None else 92
            spread = 0
            partner = self.get_partner_ticker(ticker)
            partner_book = self.books.get(partner)
            combined_mid = ((92 + bid) / 2.0 +
                            ((partner_book.best_ask + partner_book.best_bid) / 2.0
                             if partner_book and partner_book.best_ask and partner_book.best_bid else 0))

            pos = Position(
                ticker=ticker, event_ticker=et, side=side,
                entry_ask=92, entry_bid=bid, entry_spread=spread,
                combined_ask=int(combined_mid), entry_ts=time.time(),
                contracts=CONTRACTS_92PLUS, sell_price=99,
                buy_order_id=order_id, buy_confirmed=True,
                buy_fill_ts=time.time(),
                entry_mode="stb_92plus_maker",
            )
            self.positions[ticker] = pos
            pos.depth_snapshot = await self.capture_depth_snapshot(ticker)
            self._csv_write_entry(pos)
            await self.place_exit_sell(ticker)
            log(f"[92+_ENTRY] {time.strftime('%H:%M:%S')} {et} {side} entry=92c "
                f"target_sell=99c mode=92plus_maker (instant fill)")
        elif status == "resting":
            self.mode_92_bids[ticker] = order_id
            log(f"[92+_BID_POSTED] {side} resting buy at 92c oid={order_id[:12]}")
        else:
            log(f"[92+_BID_UNKNOWN] {side} status={status} oid={order_id[:12]}")

    async def cancel_92c_maker_bid(self, ticker: str):
        """Cancel a resting 92c maker bid."""
        oid = self.mode_92_bids.pop(ticker, None)
        if not oid:
            return
        side = ticker.split("-")[-1]
        del_path = f"/trade-api/v2/portfolio/orders/{oid}"
        await api_delete(self.session, self.api_key, self.private_key, del_path, self.rl)
        log(f"[92+_BID_CANCELLED] {side} sustained broke -- cancelled 92c bid")

    async def check_92plus_bid_fills(self):
        """Check if any resting 92c maker bids have filled."""
        for ticker in list(self.mode_92_bids.keys()):
            oid = self.mode_92_bids[ticker]
            path = f"/trade-api/v2/portfolio/orders/{oid}"
            result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
            if not result:
                continue

            order = result.get("order", result)
            status = order.get("status", "")
            fill_count = order.get("fill_count", 0)
            side = ticker.split("-")[-1]
            et = self.ticker_to_event.get(ticker, "?")

            if status == "executed":
                # Bid filled! Create position and post 99c sell
                self.mode_92_bids.pop(ticker, None)
                self.mode_92_entered.add(ticker)
                self.entered_sides.add(ticker)
                self.entered_events.add(et)
                self.total_entries += 1
                # Note: maker fills have 0 fee on Kalshi

                book = self.books.get(ticker)
                bid = book.best_bid if book and book.best_bid is not None else 92
                spread = 0
                partner = self.get_partner_ticker(ticker)
                partner_book = self.books.get(partner)
                combined_mid = ((92 + bid) / 2.0 +
                                ((partner_book.best_ask + partner_book.best_bid) / 2.0
                                 if partner_book and partner_book.best_ask and partner_book.best_bid else 0))

                contracts = fill_count or CONTRACTS_92PLUS
                pos = Position(
                    ticker=ticker, event_ticker=et, side=side,
                    entry_ask=92, entry_bid=bid, entry_spread=spread,
                    combined_ask=int(combined_mid), entry_ts=time.time(),
                    contracts=contracts, sell_price=99,
                    buy_order_id=oid, buy_confirmed=True,
                    buy_fill_ts=time.time(),
                    entry_mode="stb_92plus_maker",
                )
                self.positions[ticker] = pos
                pos.depth_snapshot = await self.capture_depth_snapshot(ticker)
                self._csv_write_entry(pos)
                await self.place_exit_sell(ticker)
                log(f"[92+_ENTRY] {time.strftime('%H:%M:%S')} {et} {side} "
                    f"entry=92c target_sell=99c {contracts}ct mode=92plus_maker")

            elif status == "cancelled":
                self.mode_92_bids.pop(ticker, None)
                if fill_count and fill_count > 0:
                    # Partial fill
                    self.mode_92_entered.add(ticker)
                    self.entered_sides.add(ticker)
                    self.entered_events.add(et)
                    self.total_entries += 1

                    book = self.books.get(ticker)
                    bid = book.best_bid if book and book.best_bid is not None else 92
                    partner = self.get_partner_ticker(ticker)
                    partner_book = self.books.get(partner)
                    combined_mid = ((92 + bid) / 2.0 +
                                    ((partner_book.best_ask + partner_book.best_bid) / 2.0
                                     if partner_book and partner_book.best_ask and partner_book.best_bid else 0))

                    pos = Position(
                        ticker=ticker, event_ticker=et, side=side,
                        entry_ask=92, entry_bid=bid, entry_spread=0,
                        combined_ask=int(combined_mid), entry_ts=time.time(),
                        contracts=fill_count, sell_price=99,
                        buy_order_id=oid, buy_confirmed=True,
                        buy_fill_ts=time.time(),
                        entry_mode="stb_92plus_maker",
                    )
                    self.positions[ticker] = pos
                    pos.depth_snapshot = await self.capture_depth_snapshot(ticker)
                    self._csv_write_entry(pos)
                    await self.place_exit_sell(ticker)
                    log(f"[92+_PARTIAL] {side} {fill_count}ct filled at 92c, posting sell at 99c")
                else:
                    log(f"[92+_BID_EXPIRED] {side} 92c bid cancelled with 0 fills")

    def check_entry(self, ticker: str) -> bool:
        """Check if this ticker passes all entry filters."""
        if ticker in self.entered_sides:
            return False
        if ticker in self.collapse_rejected:
            return False

        # Fix 3: Event-level dedup — block if we already traded any side of this match
        event_ticker = self.ticker_to_event.get(ticker, "")
        if event_ticker and event_ticker in self.entered_events:
            return False

        # Pre-match guard: block entry if expiry still > MAX_HOURS_TO_EXPIRY away
        expiry = self.ticker_expiry.get(ticker)
        if expiry:
            hours_until = (expiry - time.time()) / 3600.0
            if hours_until > MAX_HOURS_TO_EXPIRY:
                return False

        book = self.books.get(ticker)
        if not book or book.best_ask is None or book.best_bid is None:
            return False

        ask = book.best_ask
        bid = book.best_bid
        spread = ask - bid

        # Compute combined mid early for rejection logging
        partner = self.get_partner_ticker(ticker)
        partner_book = self.books.get(partner) if partner else None
        combined_mid = None
        if partner_book and partner_book.best_ask is not None and partner_book.best_bid is not None:
            combined_mid = (ask + bid) / 2.0 + (partner_book.best_ask + partner_book.best_bid) / 2.0

        # Only log rejections when combined mid is in dislocation zone (≤ 98c)
        log_reject = combined_mid is not None and combined_mid <= 98

        # Filter: entry side ask >= 55c
        if ask < MIN_ENTRY_ASK:
            if log_reject:
                side = ticker.split("-")[-1]
                log(f"[REJECT] {side} ask={ask}c < {MIN_ENTRY_ASK}c "
                      f"(spread={spread}c combined_mid={combined_mid:.1f}c)")
            return False

        # Filter: entry side ask <= 90c (skip shallow dislocations)
        if ask > MAX_ENTRY_ASK:
            if log_reject:
                side = ticker.split("-")[-1]
                log(f"[REJECT_SHALLOW] {side} ask={ask}c > {MAX_ENTRY_ASK}c "
                      f"(spread={spread}c combined_mid={combined_mid:.1f}c)")
            return False

        # Filter: spread <= 4c
        if spread > MAX_SPREAD:
            if log_reject:
                side = ticker.split("-")[-1]
                log(f"[REJECT] {side} spread={spread}c > {MAX_SPREAD}c "
                      f"(ask={ask}c combined_mid={combined_mid:.1f}c)")
            self.spread_confirmed.pop(ticker, None)  # reset on wide spread
            return False

        # 2-tick spread confirmation REMOVED (Phase 1)
        # Filter: combined MID <= 97c (dislocation signal)
        if not partner or not partner_book:
            return False
        if combined_mid is None:
            return False
        if combined_mid > MAX_COMBINED_MID:
            return False

        return True

    async def execute_entry(self, ticker: str, is_reentry: bool = False, original_price: int = 0):
        """Buy at ASK via taker order."""
        book = self.books[ticker]
        ask = book.best_ask
        bid = book.best_bid
        spread = ask - bid
        partner = self.get_partner_ticker(ticker)
        partner_book = self.books.get(partner)
        combined_mid = ((ask + bid) / 2.0 +
                        ((partner_book.best_ask + partner_book.best_bid) / 2.0
                         if partner_book and partner_book.best_ask and partner_book.best_bid else 0))

        # Extract side name from ticker (last segment after -)
        side = ticker.split("-")[-1]
        et = self.ticker_to_event.get(ticker, "?")

        # --- Collapse filter ---
        collapse = self.check_collapse(ticker)
        if collapse:
            drop, max_bid, current_bid = collapse
            if not is_reentry:
                log(f"[REJECT_COLLAPSE] {side} bid dropped {drop}c in 10m "
                    f"(max={max_bid}c now={current_bid}c) — re-entry in 10m")
                self.collapse_rejected.add(ticker)
                self.pending_reentries[ticker] = (
                    time.time() + COLLAPSE_REENTRY_DELAY, current_bid, 1)
                self.total_collapse_rejects += 1
                return
            else:
                # Re-entry but still collapsing: re-queue if attempts remain
                attempt = self._reentry_attempt.get(ticker, 1)
                if attempt < 3:
                    next_attempt = attempt + 1
                    self.pending_reentries[ticker] = (
                        time.time() + COLLAPSE_REENTRY_DELAY, current_bid, next_attempt)
                    self._reentry_attempt[ticker] = next_attempt
                    log(f"[REENTRY_REQUEUE] {side} still collapsing attempt {attempt}/3 "
                        f"dropped {drop}c (max={max_bid}c now={current_bid}c) next in 10m")
                    return
                log(f"[REENTRY_EXHAUSTED] {side} still collapsing after 3 attempts "
                    f"dropped {drop}c (max={max_bid}c now={current_bid}c)")
                self.collapse_rejected.discard(ticker)
                self._reentry_attempt.pop(ticker, None)
                self.entered_sides.add(ticker)
                self.total_reentry_skips += 1
                return

        if is_reentry:
            savings = original_price - ask if original_price else 0
            self.total_reentries += 1
            log(f"[REENTRY] {side} original_price={original_price}c "
                f"new_price={ask}c savings={savings}c")

        # --- Game state check (v2 filter) ---
        game_state_log = ""
        game_data = await self.fetch_game_state(et)
        if game_data:
            live = game_data.get("live_data", {})
            details = live.get("details", {})
            status = details.get("status", "?")
            p1_score = details.get("competitor1_overall_score", "?")
            p2_score = details.get("competitor2_overall_score", "?")
            p1_rounds = details.get("competitor1_round_scores", [])
            p2_rounds = details.get("competitor2_round_scores", [])
            server = details.get("server", "?")
            # Build set score string
            set_scores = "-".join(
                f"{r.get('score','?')}" for r in p1_rounds
            ) + " vs " + "-".join(
                f"{r.get('score','?')}" for r in p2_rounds
            ) if p1_rounds or p2_rounds else f"{p1_score}-{p2_score}"
            game_state_log = (
                f" sets={p1_score}-{p2_score} games={set_scores}"
                f" server={server} status={status}"
            )

            # Apply rejection filters
            reject = self.check_tennis_game_state(ticker, game_data)
            if reject:
                self.game_state_rejects += 1
                log(f"[REJECT_GAMESTATE] {et} {side} ask={ask}c "
                    f"combined_mid={combined_mid:.1f}c — {reject}"
                    f"{game_state_log}")
                return
        else:
            mid = self.event_milestones.get(et)
            if mid:
                self.game_state_fails += 1
                log(f"[GAME_STATE_FAIL] {et} {side} — proceeding without game state")
            # No milestone or fetch failed — proceed on price alone

        # Flat 25ct sizing (dynamic sizing disabled until clean week)
        order_contracts = CONTRACTS
        # Anti-stack safety: check portfolio for existing position
        pos_check_path = f"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1"
        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)
        if pos_check:
            existing_pos = [p for p in pos_check.get("market_positions", []) if p.get("position", 0) > 0]
            if existing_pos:
                held = existing_pos[0].get("position", 0)
                log(f"[SKIP_STACKED] {ticker} already holding {held}ct — skipping entry")
                self.entered_sides.add(ticker)
                return

        # Place taker buy at ask
        path = "/trade-api/v2/portfolio/orders"
        payload = {
            "ticker": ticker,
            "action": "buy",
            "side": "yes",
            "count": order_contracts,
            "type": "limit",
            "yes_price": ask,
            "post_only": False,  # taker
            "client_order_id": str(uuid.uuid4()),
        }

        result = await api_post(self.session, self.api_key, self.private_key,
                                path, payload, self.rl)
        if not result or result.get("error"):
            err = result.get("error", {}) if result else {}
            log(f"[ENTRY_FAIL] {ticker} ask={ask}c err={err}")
            return

        order = result.get("order", {})
        order_id = order.get("order_id", "")
        status = order.get("status", "")

        # Mark entered regardless of fill status — never re-enter
        self.entered_sides.add(ticker)
        self.entered_events.add(et)  # Fix 3: event-level dedup
        self.total_entries += 1

        # Fee: 1c per contract on taker entry
        entry_fee = order_contracts  # 1c per contract on taker entry
        self.total_fees_cents += entry_fee

        buy_confirmed = (status == "executed")
        buy_fill_ts = time.time() if buy_confirmed else None

        is_chall = any(ticker.startswith(s) for s in CHALLENGER_SERIES)

        pos = Position(
            ticker=ticker, event_ticker=et, side=side,
            entry_ask=ask, entry_bid=bid, entry_spread=spread,
            combined_ask=int(combined_mid), entry_ts=time.time(),
            contracts=order_contracts, sell_price=ask + EXIT_BOUNCE,
            buy_order_id=order_id, buy_confirmed=buy_confirmed,
            buy_fill_ts=buy_fill_ts,
        )
        self.positions[ticker] = pos

        # Populate game state for CSV enrichment
        if game_state_log:
            pos.game_state_at_entry = game_state_log.strip()

        # Volume tier tagging
        vol = self.ticker_volume.get(ticker, 0)
        pos.volume_tier = "thin" if 0 < vol < 1000 else "standard"

        stop_info = " hold-to-settle"  # no conditional stop for any tennis
        now = time.strftime("%H:%M:%S")
        log(f"[ENTRY] {now} {et} {side} ask={ask}c bid={bid}c "
            f"spread={spread}c combined_mid={combined_mid:.1f}c "
            f"target_sell={ask + EXIT_BOUNCE}c oid={order_id[:12]} "
            f"buy_status={status}{stop_info} volume_tier={pos.volume_tier}")

        # Game state log for every entry (builds dataset for analysis)
        log(f"[GAME_STATE] {et} side={side} entry={ask}c"
            f"{game_state_log} combined_mid={combined_mid:.1f}c")

        if buy_confirmed:
            # Buy filled immediately — safe to post resting sell
            # Capture orderbook depth at entry
            pos.depth_snapshot = await self.capture_depth_snapshot(ticker)
            self._csv_write_entry(pos)
            await self.place_exit_sell(ticker)
        else:
            # Buy is resting — DO NOT post sell yet, fill_check_loop will handle it
            log(f"  [DEFERRED_SELL] Buy not yet filled (status={status}), "
                f"sell will post after buy confirms")

    async def place_exit_sell(self, ticker: str):
        """Place resting sell order at entry_ask + EXIT_BOUNCE."""
        pos = self.positions.get(ticker)
        if not pos:
            return

        sell_price = pos.sell_price
        if sell_price > 99:
            sell_price = 99  # cap at 99c

        path = "/trade-api/v2/portfolio/orders"
        payload = {
            "ticker": ticker,
            "action": "sell",
            "side": "yes",
            "count": pos.contracts,
            "type": "limit",
            "yes_price": sell_price,
            "client_order_id": str(uuid.uuid4()),
        }

        result = await api_post(self.session, self.api_key, self.private_key,
                                path, payload, self.rl)
        if result and not result.get("error"):
            order = result.get("order", {})
            oid = order.get("order_id", "")
            pos.sell_order_id = oid
            self.resting_sells[ticker] = oid
            log(f"  [SELL_POSTED] {ticker.split('-')[-1]} sell={sell_price}c oid={oid[:12]}")
        else:
            err = result.get("error", {}) if result else {}
            log(f"  [SELL_FAIL] {ticker} price={sell_price}c err={err}")

    # ------------------------------------------------------------------
    # Conditional time stop (CHALLENGER series only)
    # ------------------------------------------------------------------
    def _is_challenger(self, ticker: str) -> bool:
        return any(ticker.startswith(s) for s in CHALLENGER_SERIES)

    async def check_time_stops(self):
        """Conditional time stop for challenger positions only.
        At COND_STOP_MINUTES after buy fill:
          - If bid >= entry_price → hold, re-check every COND_STOP_RECHECK seconds
          - If bid < entry_price → cancel resting sell, market exit at bid-2c
        Main draw positions are never time-stopped (hold to settlement).
        """
        now = time.time()
        for ticker in list(self.positions.keys()):
            pos = self.positions[ticker]

            if pos.filled or pos.settled or pos.time_stopped:
                continue
            if not pos.buy_confirmed or pos.buy_fill_ts is None:
                continue
            if not self._is_challenger(ticker):
                continue  # main draw — hold to settlement

            elapsed_min = (now - pos.buy_fill_ts) / 60.0
            if elapsed_min < COND_STOP_MINUTES:
                continue

            # Get current bid
            book = self.books.get(ticker)
            current_bid = book.best_bid if book and book.best_bid is not None else None

            if current_bid is None:
                # No WS bid — try REST fallback
                mkt_path = f"/trade-api/v2/markets/{ticker}/orderbook"
                ob_data = await api_get(self.session, self.api_key, self.private_key,
                                        mkt_path, self.rl)
                if ob_data and ob_data.get("orderbook", {}).get("yes"):
                    bids = ob_data["orderbook"]["yes"]
                    if bids:
                        current_bid = max(int(b[0]) for b in bids if len(b) >= 2)

            if current_bid is not None and current_bid >= pos.entry_ask:
                # Bid at or above entry — hold, let resting sell stay active
                # Only log once per minute to avoid spam
                if not hasattr(pos, '_last_hold_log') or now - pos._last_hold_log > 60:
                    log(f"[COND_HOLD] {pos.side} entry={pos.entry_ask}c bid={current_bid}c "
                        f"hold={elapsed_min:.1f}m — bid >= entry, holding")
                    pos._last_hold_log = now
                continue

            # Bid < entry (or no bid) — EXIT
            pos.time_stopped = True

            if current_bid is None:
                log(f"[COND_STOP] {pos.side} entry={pos.entry_ask}c — no bid, selling at 1c")
                current_bid = 1

            log(f"[COND_STOP] {pos.side} entry={pos.entry_ask}c bid={current_bid}c "
                f"hold={elapsed_min:.1f}m — bid < entry, exiting")

            # Step 1: Cancel resting sell and CHECK if it already filled
            if pos.sell_order_id:
                chk_path = f"/trade-api/v2/portfolio/orders/{pos.sell_order_id}"
                chk_result = await api_get(self.session, self.api_key, self.private_key,
                                           chk_path, self.rl)
                if chk_result:
                    order = chk_result.get("order", chk_result)
                    status = order.get("status", "")
                    if status == "executed":
                        pos.time_stopped = False
                        pos.filled = True
                        pos.exit_price = pos.sell_price
                        pos.exit_ts = time.time()
                        profit = (pos.sell_price - pos.entry_ask) * pos.contracts
                        self.total_pnl_cents += profit - pos.contracts
                        self.total_wins += 1
                        hold_sec = pos.exit_ts - pos.entry_ts
                        now_str = time.strftime("%H:%M:%S")
                        log(f"[FILL_BEAT_STOP] {now_str} {pos.event_ticker} {pos.side} "
                            f"entry={pos.entry_ask}c sold={pos.sell_price}c "
                            f"profit={profit - pos.contracts}c — sell filled just before cond stop")
                        self.log_trajectory(pos, "WIN")
                        await self._csv_write_exit(pos, "fill_7c", pos.sell_price, profit - pos.contracts)
                        self.resting_sells.pop(ticker, None)
                        await self.print_balance()
                        continue

                del_path = f"/trade-api/v2/portfolio/orders/{pos.sell_order_id}"
                await api_delete(self.session, self.api_key, self.private_key,
                                 del_path, self.rl)
                self.resting_sells.pop(ticker, None)

            # Step 2: Aggressive taker sell at bid-2c
            aggressive_price = max(1, current_bid - 2)
            sell_path = "/trade-api/v2/portfolio/orders"
            sell_payload = {
                "ticker": ticker,
                "action": "sell",
                "side": "yes",
                "count": pos.contracts,
                "type": "limit",
                "yes_price": aggressive_price,
                "post_only": False,
                "client_order_id": str(uuid.uuid4()),
            }

            result = await api_post(self.session, self.api_key, self.private_key,
                                    sell_path, sell_payload, self.rl)

            if result and not result.get("error"):
                order = result.get("order", {})
                sell_status = order.get("status", "")
                pos.exit_ts = time.time()
                pos.exit_price = current_bid

                pnl_cents = (current_bid - pos.entry_ask) * pos.contracts
                exit_fee = pos.contracts  # 1c taker exit
                net_pnl = pnl_cents - pos.contracts - exit_fee
                self.total_pnl_cents += net_pnl
                self.total_fees_cents += exit_fee
                self.total_time_stops += 1

                if net_pnl >= 0:
                    self.total_wins += 1
                else:
                    self.total_losses += 1

                pos.filled = True
                hold_sec = pos.exit_ts - pos.buy_fill_ts
                now_str = time.strftime("%H:%M:%S")
                log(f"[COND_STOP] {now_str} {pos.event_ticker} {pos.side} "
                    f"entry={pos.entry_ask}c exit={current_bid}c (limit={aggressive_price}c) "
                    f"pnl={net_pnl}c net hold={hold_sec:.0f}s ({hold_sec/60:.1f}m) "
                    f"sell_status={sell_status}")
                self.log_trajectory(pos, "COND_STOP")
                await self._csv_write_exit(pos, "cond_stop", current_bid, net_pnl)
                await self.print_balance()
            else:
                err = result.get("error", {}) if result else {}
                log(f"  [COND_STOP_SELL_FAIL] {ticker} bid={current_bid}c "
                    f"limit={aggressive_price}c err={err}")
                pos.time_stopped = False  # allow retry

    # ------------------------------------------------------------------
    # Exit monitoring
    # ------------------------------------------------------------------
    async def _cancel_stale_buy(self, ticker: str, pos, elapsed: float):
        """Cancel a stale/early-cancel buy and handle partial fills."""
        # First check order status to get fill_count
        chk_path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
        chk_result = await api_get(self.session, self.api_key, self.private_key,
                                    chk_path, self.rl)
        fill_count = 0
        if chk_result:
            order = chk_result.get("order", chk_result)
            status = order.get("status", "")
            fill_count = order.get("fill_count", 0) or 0
            if status == "executed":
                # Fully filled between our check — treat as normal buy confirm
                pos.buy_confirmed = True
                pos.buy_fill_ts = time.time()
                expected_ct = CONTRACTS_92PLUS if pos.entry_mode and "92plus" in pos.entry_mode else CONTRACTS
                pos.contracts = fill_count or expected_ct
                log(f"  [BUY_FILLED_LATE] {pos.side} fully filled {pos.contracts}ct "
                    f"while cancelling — posting sell at {pos.sell_price}c")
                await self.place_exit_sell(ticker)
                if pos.depth_snapshot is None:
                    pos.depth_snapshot = await self.capture_depth_snapshot(pos.ticker)
                self._csv_write_entry(pos)
                return

        # Cancel the remaining unfilled portion
        del_path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
        await api_delete(self.session, self.api_key, self.private_key,
                         del_path, self.rl)

        if fill_count > 0:
            # Partial fill — enter retry mode to get remaining contracts
            pos.buy_confirmed = True
            pos.buy_fill_ts = time.time()
            pos.contracts = fill_count
            expected_ct_r = CONTRACTS_92PLUS if pos.entry_mode and "92plus" in pos.entry_mode else CONTRACTS
            remaining = expected_ct_r - fill_count

            # Check if signal still valid for retry
            book = self.books.get(ticker)
            if book and remaining > 0:
                current_ask = book.best_ask
                current_bid = book.best_bid
                current_spread = (current_ask - current_bid) if (current_ask is not None and current_bid is not None) else 99

                # Signal still valid: price in range, spread OK
                price_ok = (current_ask is not None
                           and current_ask >= MIN_ENTRY_ASK
                           and current_ask <= MAX_ENTRY_ASK
                           and current_spread <= MAX_SPREAD)

                if price_ok:
                    pos.retry_remaining = remaining
                    pos.retry_start_ts = time.time()
                    pos.retry_attempts = 0
                    pos.retry_active = True
                    pos.highest_fill_price = pos.entry_ask  # initial fill price
                    log(f"  [PARTIAL_FILL] {pos.side} — {fill_count}ct filled of {expected_ct_r} "
                        f"at {pos.entry_ask}c, {remaining}ct remaining — entering retry mode "
                        f"(ask={current_ask}c spread={current_spread}c)")
                    # Place first retry immediately
                    await self._place_retry_buy(ticker, pos)
                    return

            # Signal no longer valid or no book — accept partial, post sell
            log(f"  [PARTIAL_FILL] {pos.side} — {fill_count}ct filled of {expected_ct_r} "
                f"at {pos.entry_ask}c, cancelled rest after {elapsed:.0f}s, "
                f"signal expired — posting sell for {fill_count}ct at {pos.sell_price}c")
            if pos.depth_snapshot is None:
                pos.depth_snapshot = await self.capture_depth_snapshot(pos.ticker)
            self._csv_write_entry(pos)
            await self.place_exit_sell(ticker)
        else:
            # Nothing filled — clean exit, allow retry
            log(f"  [STALE_BUY] {pos.side} — 0ct filled, cancelled after {elapsed:.0f}s — unlocking ticker")
            self.entered_sides.discard(ticker)
            et = self.ticker_to_event.get(ticker, "")
            if et:
                self.entered_events.discard(et)
            self.spread_confirmed.pop(ticker, None)
            del self.positions[ticker]

    async def _place_retry_buy(self, ticker: str, pos):
        """Place a retry buy order for remaining contracts at current ask."""
        book = self.books.get(ticker)
        if not book or book.best_ask is None:
            log(f"  [RETRY_SKIP] {pos.side} — no book data, finalizing with {pos.contracts}ct")
            await self._finalize_retry(ticker, pos)
            return

        current_ask = book.best_ask
        current_bid = book.best_bid
        current_spread = (current_ask - current_bid) if (current_ask is not None and current_bid is not None) else 99

        # Validate signal still active
        if (current_ask < MIN_ENTRY_ASK or current_ask > MAX_ENTRY_ASK
                or current_spread > MAX_SPREAD):
            log(f"  [RETRY_STOP] {pos.side} — signal expired "
                f"(ask={current_ask}c spread={current_spread}c), "
                f"finalizing with {pos.contracts}ct")
            await self._finalize_retry(ticker, pos)
            return

        pos.retry_attempts += 1
        remaining = pos.retry_remaining

        path = "/trade-api/v2/portfolio/orders"
        payload = {
            "ticker": ticker,
            "action": "buy",
            "side": "yes",
            "count": remaining,
            "type": "limit",
            "yes_price": current_ask,
            "post_only": False,
            "client_order_id": str(uuid.uuid4()),
        }

        result = await api_post(self.session, self.api_key, self.private_key,
                                path, payload, self.rl)
        if result and not result.get("error"):
            order = result.get("order", {})
            oid = order.get("order_id", "")
            status = order.get("status", "")
            fill_count = order.get("fill_count", 0) or 0

            pos.buy_order_id = oid  # track new order for stale checks

            if status == "executed":
                # Retry fully filled
                pos.contracts += fill_count or remaining
                pos.retry_remaining = 0
                pos.retry_active = False
                pos.highest_fill_price = max(pos.highest_fill_price, current_ask)
                log(f"  [RETRY_FILLED] {pos.side} — retry #{pos.retry_attempts} "
                    f"filled {fill_count or remaining}ct at {current_ask}c, "
                    f"total={pos.contracts}ct — posting sell")
                await self._finalize_retry(ticker, pos)
            else:
                # Retry order is resting — will be checked in check_fills
                log(f"  [RETRY] {pos.side} remaining={remaining} "
                    f"attempt={pos.retry_attempts} ask={current_ask}c "
                    f"oid={oid[:12]}")
        else:
            err = result.get("error", {}) if result else {}
            log(f"  [RETRY_FAIL] {pos.side} — order failed: {err}, "
                f"finalizing with {pos.contracts}ct")
            await self._finalize_retry(ticker, pos)

    async def _finalize_retry(self, ticker: str, pos):
        """End retry mode and post resting sell for accumulated contracts."""
        pos.retry_active = False
        pos.retry_remaining = 0
        if pos.contracts > 0:
            # Set sell price from highest fill across all retries
            if pos.highest_fill_price > 0:
                if pos.entry_mode and "92plus" in pos.entry_mode:
                    pos.sell_price = 99  # 92c+ always sells at 99c
                else:
                    pos.sell_price = min(pos.highest_fill_price + EXIT_BOUNCE, 99)
            log(f"  [RETRY_DONE] {pos.side} — final fill={pos.contracts}ct, "
                f"highest_fill={pos.highest_fill_price}c, "
                f"posting sell at {pos.sell_price}c")
            if pos.depth_snapshot is None:
                pos.depth_snapshot = await self.capture_depth_snapshot(pos.ticker)
            self._csv_write_entry(pos)
            await self.place_exit_sell(ticker)
        else:
            # Nothing filled at all — safety net
            log(f"  [RETRY_EMPTY] {pos.side} — 0ct total, cleaning up")
            self.entered_sides.discard(ticker)
            et = self.ticker_to_event.get(ticker, "")
            if et:
                self.entered_events.discard(et)
            self.spread_confirmed.pop(ticker, None)
            del self.positions[ticker]

    async def check_fills(self):
        """Poll buy and sell orders for fills. Post sell only after buy confirms."""
        for ticker in list(self.positions.keys()):
            pos = self.positions[ticker]
            if pos.filled or pos.settled or pos.time_stopped:
                continue

            # Handle retry mode for partial fills
            if pos.retry_active:
                retry_elapsed = time.time() - pos.retry_start_ts

                # Retry window expired
                if retry_elapsed > RETRY_WINDOW:
                    # Cancel any outstanding retry order
                    if pos.buy_order_id:
                        chk_path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
                        chk_result = await api_get(self.session, self.api_key, self.private_key,
                                                    chk_path, self.rl)
                        if chk_result:
                            order = chk_result.get("order", chk_result)
                            status = order.get("status", "")
                            fill_count = order.get("fill_count", 0) or 0
                            if status == "executed":
                                pos.contracts += fill_count
                                pos.retry_remaining = 0
                            elif status == "resting":
                                if fill_count > 0:
                                    pos.contracts += fill_count
                                    pos.retry_remaining -= fill_count
                                # Cancel remainder
                                del_path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
                                await api_delete(self.session, self.api_key, self.private_key,
                                                 del_path, self.rl)
                    log(f"  [RETRY_TIMEOUT] {pos.side} — {retry_elapsed:.0f}s elapsed, "
                        f"finalizing with {pos.contracts}ct")
                    await self._finalize_retry(ticker, pos)
                    continue

                # Check if current retry order filled or partially filled
                if pos.buy_order_id:
                    chk_path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
                    chk_result = await api_get(self.session, self.api_key, self.private_key,
                                                chk_path, self.rl)
                    if chk_result:
                        order = chk_result.get("order", chk_result)
                        status = order.get("status", "")
                        fill_count = order.get("fill_count", 0) or 0

                        if status == "executed":
                            # Retry order fully filled
                            new_fills = fill_count or pos.retry_remaining
                            pos.contracts += new_fills
                            pos.retry_remaining -= new_fills
                            # Track highest fill price
                            order_price = order.get("yes_price", 0) or 0
                            if order_price > 0:
                                pos.highest_fill_price = max(pos.highest_fill_price, order_price)
                            if pos.retry_remaining <= 0:
                                pos.retry_remaining = 0
                                log(f"  [RETRY_COMPLETE] {pos.side} — all {pos.contracts}ct filled")
                                await self._finalize_retry(ticker, pos)
                            else:
                                # Still more needed, place another retry
                                log(f"  [RETRY_PARTIAL] {pos.side} — +{new_fills}ct, "
                                    f"total={pos.contracts}ct, still need {pos.retry_remaining}ct")
                                await self._place_retry_buy(ticker, pos)
                            continue

                        elif status == "resting":
                            # Check if this retry order is stale (>RETRY_INTERVAL)
                            time_since_retry_start = time.time() - pos.retry_start_ts
                            expected_checks = pos.retry_attempts
                            next_retry_at = expected_checks * RETRY_INTERVAL

                            if time_since_retry_start > next_retry_at:
                                # Cancel this retry order, collect any fills, retry again
                                if fill_count > 0:
                                    pos.contracts += fill_count
                                    pos.retry_remaining -= fill_count
                                del_path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
                                await api_delete(self.session, self.api_key, self.private_key,
                                                 del_path, self.rl)
                                if pos.retry_remaining > 0:
                                    order_price = order.get("yes_price", 0) or 0
                                    if order_price > 0 and fill_count > 0:
                                        pos.highest_fill_price = max(pos.highest_fill_price, order_price)
                                    log(f"  [RETRY_CYCLE] {pos.side} — cancelling stale retry, "
                                        f"+{fill_count}ct, total={pos.contracts}ct, "
                                        f"remaining={pos.retry_remaining}ct")
                                    await self._place_retry_buy(ticker, pos)
                                else:
                                    await self._finalize_retry(ticker, pos)
                            continue

                        elif status == "cancelled":
                            if fill_count > 0:
                                pos.contracts += fill_count
                                pos.retry_remaining -= fill_count
                            if pos.retry_remaining > 0:
                                await self._place_retry_buy(ticker, pos)
                            else:
                                await self._finalize_retry(ticker, pos)
                            continue
                continue  # don't process normal flow while in retry mode

            # Step 1: If buy not yet confirmed, check buy order status
            if not pos.buy_confirmed and pos.buy_order_id:
                elapsed = time.time() - pos.entry_ts

                # Early cancel: if bid drops below entry - 2c, cancel immediately
                book = self.books.get(ticker)
                if book and book.best_bid is not None:
                    if book.best_bid < pos.entry_ask - 2 and elapsed > 2:
                        log(f"  [EARLY_CANCEL] {pos.side} bid={book.best_bid}c < "
                            f"entry-2={pos.entry_ask - 2}c after {elapsed:.0f}s")
                        await self._cancel_stale_buy(ticker, pos, elapsed)
                        continue

                # Stale buy check: cancel if unfilled after STALE_BUY_TIMEOUT
                if elapsed > STALE_BUY_TIMEOUT:
                    log(f"  [STALE_BUY] {pos.side} — cancelling unfilled buy at "
                        f"{pos.entry_ask}c after {elapsed:.0f}s")
                    await self._cancel_stale_buy(ticker, pos, elapsed)
                    continue

                path = f"/trade-api/v2/portfolio/orders/{pos.buy_order_id}"
                result = await api_get(self.session, self.api_key, self.private_key,
                                       path, self.rl)
                if result:
                    order = result.get("order", result)
                    status = order.get("status", "")
                    fill_count = order.get("fill_count", 0)
                    if status == "executed":
                        pos.buy_confirmed = True
                        pos.buy_fill_ts = time.time()
                        expected_ct_cf = CONTRACTS_92PLUS if pos.entry_mode and "92plus" in pos.entry_mode else CONTRACTS
                        pos.contracts = fill_count or expected_ct_cf
                        is_chall = self._is_challenger(ticker)
                        stop_info = " (hold to settle)"
                        log(f"  [BUY_CONFIRMED] {pos.side} buy filled {pos.contracts}ct at "
                            f"{pos.entry_ask}c — posting sell at {pos.sell_price}c{stop_info}")
                        await self.place_exit_sell(ticker)
                        if pos.depth_snapshot is None:
                            pos.depth_snapshot = await self.capture_depth_snapshot(pos.ticker)
                        self._csv_write_entry(pos)
                    elif status == "resting" and fill_count and fill_count > 0:
                        # Partial fill while still resting — stale timeout will
                        # trigger retry logic. Don't cancel early.
                        pass
                    elif status == "cancelled":
                        if fill_count and fill_count > 0:
                            log(f"  [PARTIAL_CANCELLED] {pos.side} — {fill_count}ct filled "
                                f"before cancel, posting sell")
                            pos.buy_confirmed = True
                            pos.buy_fill_ts = time.time()
                            pos.contracts = fill_count
                            await self.place_exit_sell(ticker)
                            if pos.depth_snapshot is None:
                                pos.depth_snapshot = await self.capture_depth_snapshot(pos.ticker)
                            self._csv_write_entry(pos)
                        else:
                            log(f"  [BUY_CANCELLED] {pos.side} — removing from tracking")
                            pos.filled = True
                        continue
                continue

            # Step 2: Check if sell order filled
            if pos.sell_order_id:
                path = f"/trade-api/v2/portfolio/orders/{pos.sell_order_id}"
                result = await api_get(self.session, self.api_key, self.private_key,
                                       path, self.rl)
                if result:
                    order = result.get("order", result)
                    status = order.get("status", "")
                    if status == "executed":
                        pos.filled = True
                        pos.exit_price = pos.sell_price
                        pos.exit_ts = time.time()
                        profit = (pos.sell_price - pos.entry_ask) * pos.contracts
                        self.total_pnl_cents += profit - (pos.contracts)
                        self.total_wins += 1
                        hold_sec = pos.exit_ts - pos.entry_ts
                        now = time.strftime("%H:%M:%S")
                        log(f"[FILL] {now} {pos.event_ticker} {pos.side} "
                            f"entry={pos.entry_ask}c sold={pos.sell_price}c "
                            f"profit={profit - pos.contracts}c net "
                            f"time={hold_sec:.0f}s ({hold_sec/60:.1f}m)")
                        self.log_trajectory(pos, "WIN")
                        await self._csv_write_exit(pos, "fill_7c", pos.sell_price, profit - pos.contracts)
                        await self.print_balance()
                        continue

            # Step 3: Check if market settled/closed
            await self.check_settlement(ticker)

    async def check_settlement(self, ticker: str):
        """Check if market has settled — if so, record loss."""
        pos = self.positions[ticker]
        if pos.filled or pos.settled or pos.time_stopped:
            return

        path = f"/trade-api/v2/markets/{ticker}"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return

        status = result.get("status", "")
        if status not in ("settled", "closed", "finalized"):
            return

        # Market settled — position exits at settlement
        pos.settled = True
        pos.exit_ts = time.time()

        result_str = result.get("result", "")
        if result_str == "yes":
            # We held YES, it settled YES = 100c
            exit_price = 100
        elif result_str == "no":
            exit_price = 0
        else:
            exit_price = 0  # unknown = assume loss

        pos.exit_price = exit_price
        pnl = (exit_price - pos.entry_ask) * pos.contracts
        # Settlement fee: 1c per contract on win, 0 on loss
        settle_fee = pos.contracts if exit_price > pos.entry_ask else 0
        self.total_fees_cents += settle_fee
        net_pnl = pnl - pos.contracts - settle_fee  # entry fee + settlement fee
        self.total_pnl_cents += net_pnl

        # Cancel resting sell if still open
        if pos.sell_order_id and pos.sell_order_id in self.resting_sells.values():
            await api_delete(self.session, self.api_key, self.private_key,
                             f"/trade-api/v2/portfolio/orders/{pos.sell_order_id}", self.rl)

        hold_sec = pos.exit_ts - pos.entry_ts
        now = time.strftime("%H:%M:%S")

        if exit_price >= pos.entry_ask:
            self.total_wins += 1
            log(f"[SETTLE_WIN] {now} {pos.event_ticker} {pos.side} "
                f"entry={pos.entry_ask}c settled={exit_price}c "
                f"net={net_pnl}c time={hold_sec/60:.1f}m")
            self.log_trajectory(pos, "SETTLE_WIN")
            await self._csv_write_exit(pos, "settlement_win", exit_price, net_pnl)
        else:
            self.total_losses += 1
            log(f"[LOSS] {now} {pos.event_ticker} {pos.side} "
                f"entry={pos.entry_ask}c exit={exit_price}c "
                f"loss={net_pnl}c time={hold_sec/60:.1f}m")
            self.log_trajectory(pos, "LOSS")
            await self._csv_write_exit(pos, "settlement_loss", exit_price, net_pnl)
        await self.print_balance()


    def _detect_series(self, ticker: str) -> str:
        if "CHALLENGERMATCH" in ticker.upper():
            return "challenger"
        return "main_draw"


    # ------------------------------------------------------------------
    # Enriched CSV logging (v3)
    # ------------------------------------------------------------------
    CSV_PATH = "/tmp/v3_enriched_trades.csv"
    CSV_COLS = [
        "timestamp", "ticker", "series", "sport", "entry_price", "entry_side",
        "combined_mid", "spread", "collapse_triggered",
        "game_state_at_entry", "who_winning_at_entry", "pre_entry_price_10m",
        "exit_type", "exit_price", "hold_time_seconds",
        "game_state_at_exit", "pnl_cents",
        "bid_depth_5c", "bid_depth_10c", "bid_depth_15c",
        "ask_depth_5c", "ask_depth_10c", "ask_depth_15c",
        "depth_ratio_5c", "depth_ratio_10c", "depth_ratio_15c",
        "book_spread", "book_mid", "total_depth",
        "entry_mode",
        "volume_tier",
    ]


    async def capture_depth_snapshot(self, ticker: str) -> dict:
        """Fetch orderbook and compute depth metrics at entry time."""
        snap = {
            "bid_depth_5c": 0, "bid_depth_10c": 0, "bid_depth_15c": 0,
            "ask_depth_5c": 0, "ask_depth_10c": 0, "ask_depth_15c": 0,
            "depth_ratio_5c": "", "depth_ratio_10c": "", "depth_ratio_15c": "",
            "book_spread": "", "book_mid": "", "total_depth": 0,
        }
        try:
            path = f"/trade-api/v2/markets/{ticker}/orderbook"
            data = await api_get(self.session, self.api_key, self.private_key,
                                 path, self.rl)
            if not data or "orderbook" not in data:
                return snap
            ob = data["orderbook"]
            yes_bids = ob.get("yes", [])
            no_bids = ob.get("no", [])
            if not yes_bids and not no_bids:
                return snap

            # YES bids sorted descending by price
            bids = sorted([(int(b[0]), int(b[1])) for b in yes_bids if len(b) >= 2],
                          key=lambda x: -x[0])
            # YES asks derived from NO side: ask_price = 100 - no_price
            asks = sorted([(100 - int(a[0]), int(a[1])) for a in no_bids if len(a) >= 2],
                          key=lambda x: x[0])

            best_bid = bids[0][0] if bids else None
            best_ask = asks[0][0] if asks else None

            if best_bid is not None and best_ask is not None:
                snap["book_spread"] = best_ask - best_bid
                snap["book_mid"] = (best_ask + best_bid) / 2

            # Compute depth within N cents of BBO
            for window in [5, 10, 15]:
                bd = 0
                if best_bid is not None:
                    for price, qty in bids:
                        if best_bid - price <= window:
                            bd += qty
                ad = 0
                if best_ask is not None:
                    for price, qty in asks:
                        if price - best_ask <= window:
                            ad += qty
                snap[f"bid_depth_{window}c"] = bd
                snap[f"ask_depth_{window}c"] = ad
                if ad > 0:
                    snap[f"depth_ratio_{window}c"] = round(bd / ad, 3)
                else:
                    snap[f"depth_ratio_{window}c"] = ""

            snap["total_depth"] = sum(q for _, q in bids) + sum(q for _, q in asks)
        except Exception as e:
            log(f"[DEPTH_ERR] {ticker}: {e}")
        return snap

    def _csv_ensure_header(self):
        import os
        if not os.path.exists(self.CSV_PATH):
            with open(self.CSV_PATH, "w") as f:
                f.write(",".join(self.CSV_COLS) + "\n")

    def _csv_write_entry(self, pos):
        """Write entry row to CSV when buy is confirmed."""
        if pos.csv_entry_logged:
            return
        pos.csv_entry_logged = True
        self._csv_ensure_header()

        series = self._detect_series(pos.ticker)

        # Pre-entry price from bid_history
        history = self.bid_history.get(pos.ticker, [])
        pre_10m = None
        if history:
            cutoff = pos.entry_ts - 600
            for ts, bid in reversed(history):
                if ts <= cutoff:
                    pre_10m = bid
                    break
        pos.pre_entry_price_10m = pre_10m

        import csv, io
        ds = pos.depth_snapshot
        row = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(pos.entry_ts)),
            "ticker": pos.ticker,
            "series": series,
            "sport": "tennis",
            "entry_price": pos.entry_ask,
            "entry_side": pos.side,
            "combined_mid": pos.combined_ask,
            "spread": pos.entry_spread,
            "collapse_triggered": "T" if pos.collapse_triggered else "F",
            "game_state_at_entry": pos.game_state_at_entry.replace(",", ";"),
            "who_winning_at_entry": pos.who_winning_at_entry,
            "pre_entry_price_10m": pre_10m if pre_10m is not None else "",
            "exit_type": "",
            "exit_price": "",
            "hold_time_seconds": "",
            "game_state_at_exit": "",
            "pnl_cents": "",
            "bid_depth_5c": ds.get("bid_depth_5c", "") if ds else "",
            "bid_depth_10c": ds.get("bid_depth_10c", "") if ds else "",
            "bid_depth_15c": ds.get("bid_depth_15c", "") if ds else "",
            "ask_depth_5c": ds.get("ask_depth_5c", "") if ds else "",
            "ask_depth_10c": ds.get("ask_depth_10c", "") if ds else "",
            "ask_depth_15c": ds.get("ask_depth_15c", "") if ds else "",
            "depth_ratio_5c": ds.get("depth_ratio_5c", "") if ds else "",
            "depth_ratio_10c": ds.get("depth_ratio_10c", "") if ds else "",
            "depth_ratio_15c": ds.get("depth_ratio_15c", "") if ds else "",
            "book_spread": ds.get("book_spread", "") if ds else "",
            "book_mid": ds.get("book_mid", "") if ds else "",
            "total_depth": ds.get("total_depth", "") if ds else "",
            "entry_mode": getattr(pos, 'entry_mode', ''),
            "volume_tier": getattr(pos, 'volume_tier', ''),
        }

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=self.CSV_COLS)
        writer.writerow(row)
        with open(self.CSV_PATH, "a") as f:
            f.write(buf.getvalue())

    async def _csv_write_exit(self, pos, exit_type, exit_price, pnl_cents):
        """Append exit data by rewriting the last matching entry row."""
        if pos.csv_exit_logged:
            return
        pos.csv_exit_logged = True

        hold_sec = (pos.exit_ts or time.time()) - pos.entry_ts

        # Fetch game state at exit
        et = pos.event_ticker
        gs_exit = ""
        try:
            game_data = await self.fetch_game_state(et)
            if game_data:
                live = game_data.get("live_data", {})
                details = live.get("details", {})
                gs_exit = str(details).replace(",", ";")[:200]
        except Exception:
            pass

        # Read CSV, find last row for this ticker with empty exit_type, update it
        import csv, io
        try:
            with open(self.CSV_PATH, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return

        updated = False
        for i in range(len(lines) - 1, 0, -1):
            if pos.ticker in lines[i]:
                parts = lines[i].strip().split(",")
                if len(parts) >= 17:  # min columns (pre-depth rows have 17)
                    # exit_type is at index 12
                    if parts[12] == "":
                        parts[12] = exit_type
                        parts[13] = str(exit_price)
                        parts[14] = str(int(hold_sec))
                        parts[15] = gs_exit.replace(",", ";")[:200]
                        parts[16] = str(pnl_cents)
                        lines[i] = ",".join(parts) + "\n"
                        updated = True
                        break

        if updated:
            with open(self.CSV_PATH, "w") as f:
                f.writelines(lines)
        else:
            # Fallback: append a standalone exit row
            self._csv_ensure_header()
            row_str = (
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())},{pos.ticker},"
                f"{self._detect_series(pos.ticker)},tennis,{pos.entry_ask},{pos.side},"
                f"{pos.combined_ask},{pos.entry_spread},"
                f"{'T' if pos.collapse_triggered else 'F'},"
                f"{pos.game_state_at_entry.replace(chr(44), chr(59))},"
                f"{pos.who_winning_at_entry},{pos.pre_entry_price_10m or ''},"
                f"{exit_type},{exit_price},{int(hold_sec)},{gs_exit[:200]},{pnl_cents},,,,,,,,,,,,\n"
            )
            with open(self.CSV_PATH, "a") as f:
                f.write(row_str)

    def log_trajectory(self, pos: "Position", outcome: str):
        """Log trajectory + overshoot data for a closed position."""
        if pos.trajectory_logged:
            return
        pos.trajectory_logged = True
        t = pos.trajectory
        def fmt(v):
            return f"{v}c" if v is not None else "?"
        overshoot = ""
        if pos.max_bid_after_entry is not None:
            over = pos.max_bid_after_entry - pos.entry_ask
            overshoot = f" max_bid={pos.max_bid_after_entry}c overshoot={over:+d}c"
        log(f"[TRAJECTORY] {pos.side} entry={pos.entry_ask}c "
            f"t15s={fmt(t['15s'])} t30s={fmt(t['30s'])} "
            f"t1m={fmt(t['1m'])} t2m={fmt(t['2m'])} "
            f"t3m={fmt(t['3m'])} t5m={fmt(t['5m'])} "
            f"t10m={fmt(t['10m'])} t15m={fmt(t['15m'])} t20m={fmt(t['20m'])} "
            f"outcome={outcome}{overshoot}")

    # ------------------------------------------------------------------
    # Balance & stats
    # ------------------------------------------------------------------
    async def fetch_balance(self) -> Optional[float]:
        result = await api_get(self.session, self.api_key, self.private_key,
                               "/trade-api/v2/portfolio/balance", self.rl)
        if result:
            # Balance is in cents
            bal = result.get("balance", 0)
            self.cash_balance = bal / 100.0
            return self.cash_balance
        return None

    async def print_balance(self):
        bal = await self.fetch_balance()
        if bal is not None:
            pnl_dollars = self.total_pnl_cents / 100.0
            open_count = sum(1 for p in self.positions.values()
                             if not p.filled and not p.settled and not p.time_stopped)
            log(f"  [BAL] ${bal:.2f}  P&L: ${pnl_dollars:+.2f}  "
                f"open={open_count} wins={self.total_wins} losses={self.total_losses} "
                f"cond_stops={self.total_time_stops} entries={self.total_entries}")

    def print_stats(self):
        elapsed = (time.time() - self.start_time) / 3600
        pnl = self.total_pnl_cents / 100.0
        open_positions = sum(1 for p in self.positions.values()
                             if not p.filled and not p.settled and not p.time_stopped)
        closed = self.total_wins + self.total_losses
        win_rate = (self.total_wins / closed * 100) if closed > 0 else 0
        now = time.strftime("%H:%M:%S")
        log(f"\n[STATS] {now} — {elapsed:.1f}h elapsed")
        log(f"  Entries: {self.total_entries}  Wins: {self.total_wins}  "
            f"Losses: {self.total_losses}  Win%: {win_rate:.1f}%")
        log(f"  Collapse: rejects={self.total_collapse_rejects} "
            f"reentries={self.total_reentries} skips={self.total_reentry_skips} "
            f"pending={len(self.pending_reentries)}")
        log(f"  P&L: ${pnl:+.2f}  Fees: ${self.total_fees_cents/100:.2f}  "
            f"Balance: ${self.cash_balance:.2f}")
        log(f"  Open positions: {open_positions}  "
            f"Tickers tracked: {len(self.subscribed)}  "
            f"Events: {len(self.known_events)}")
        log(f"  Game state: milestones={len(self.event_milestones)} "
            f"rejects={self.game_state_rejects} fails={self.game_state_fails}")
        if open_positions > 0:
            for t, pos in self.positions.items():
                if not pos.filled and not pos.settled and not pos.time_stopped:
                    hold = (time.time() - pos.entry_ts) / 60
                    is_chall = self._is_challenger(t)
                    stop_info = " (hold to settle)"
                    book = self.books.get(t)
                    bid_now = book.best_bid if book and book.best_bid else "?"
                    log(f"    {pos.side} entry={pos.entry_ask}c bid_now={bid_now}c "
                        f"target={pos.sell_price}c hold={hold:.0f}m{stop_info}")
        log("")

    # ------------------------------------------------------------------
    # BBO update handler
    # ------------------------------------------------------------------
    async def on_bbo_update(self, ticker: str):
        """Called whenever BBO changes for a ticker. Check entry conditions."""
        self.ws_msg_count += 1

        # Record bid to collapse filter history
        _bk = self.books.get(ticker)
        if _bk and _bk.best_bid is not None:
            _now = time.time()
            if ticker not in self.bid_history:
                self.bid_history[ticker] = []
            self.bid_history[ticker].append((_now, _bk.best_bid))
            if len(self.bid_history[ticker]) > 200:
                cutoff = _now - 900
                self.bid_history[ticker] = [
                    (t, b) for t, b in self.bid_history[ticker] if t >= cutoff]

        # Track min combined MID per event (tick-by-tick)
        et = self.ticker_to_event.get(ticker)
        if et:
            partner = self.get_partner_ticker(ticker)
            if partner:
                book = self.books.get(ticker)
                pbook = self.books.get(partner)
                if (book and pbook and book.best_ask is not None
                        and pbook.best_ask is not None
                        and book.best_bid is not None
                        and pbook.best_bid is not None):
                    combined_mid = ((book.best_ask + book.best_bid) / 2.0 +
                                    (pbook.best_ask + pbook.best_bid) / 2.0)
                    combined_int = int(combined_mid)
                    prev_min = self.min_combined.get(et, 999)
                    if combined_int < prev_min:
                        self.min_combined[et] = combined_int
                        if combined_int < self.global_min_combined:
                            self.global_min_combined = combined_int
                        # Log when we see a new low at or below 98c
                        if combined_int <= 98:
                            side = ticker.split("-")[-1]
                            print(f"[LOW_COMBINED] {et[-25:]} combined_mid={combined_mid:.1f}c "
                                  f"({side} ask={book.best_ask}c) "
                                  f"global_min={self.global_min_combined}c")

        # Trajectory + overshoot tracking for open positions
        pos = self.positions.get(ticker)
        if pos and pos.buy_confirmed and not pos.filled and not pos.settled and not pos.time_stopped:
            book = self.books.get(ticker)
            if book and book.best_bid is not None:
                bid = book.best_bid
                elapsed = time.time() - pos.entry_ts
                # Overshoot: track max bid seen
                if pos.max_bid_after_entry is None or bid > pos.max_bid_after_entry:
                    pos.max_bid_after_entry = bid
                # Trajectory: sample bid at fixed intervals
                TRAJ_INTERVALS = {
                    "15s": 15, "30s": 30, "1m": 60, "2m": 120, "3m": 180,
                    "5m": 300, "10m": 600, "15m": 900, "20m": 1200,
                }
                for label, secs in TRAJ_INTERVALS.items():
                    if pos.trajectory[label] is None and elapsed >= secs:
                        pos.trajectory[label] = bid

        # After first batch of snapshots, print diagnostic once
        if not self._first_scan_printed and self.ws_msg_count >= 20:
            self._first_scan_printed = True
            self._print_scan_state()

        # Only enter if not already in this ticker
        if ticker not in self.entered_sides and self.check_entry(ticker):
            await self.execute_entry(ticker)

        # --- 92c+ Settlement Mode (additive, main draw only, maker-based) ---
        if (ticker not in self.entered_sides
                and ticker not in self.mode_92_entered
                and ticker not in self.mode_92_bids
                and self._is_main_draw(ticker)
                and ticker.startswith("KXATPMATCH")):  # ATP Main only, exclude WTA for 92c+
            book92 = self.books.get(ticker)
            if book92 and book92.best_ask is not None:
                ask92 = book92.best_ask
                # Update sustained counter on every tick
                if ask92 >= 88:
                    sustained = self._check_sustained_90(ticker, ask92)
                    if sustained and ask92 >= 92:
                        # Event-level dedup
                        et92 = self.ticker_to_event.get(ticker, "")
                        if not (et92 and et92 in self.entered_events):
                            # Deciding set guard REMOVED (Phase 1)
                            if True:
                                # Pre-match guard
                                expiry92 = self.ticker_expiry.get(ticker)
                                skip_expiry = False
                                if expiry92:
                                    hours92 = (expiry92 - time.time()) / 3600.0
                                    if hours92 > MAX_HOURS_TO_EXPIRY:
                                        skip_expiry = True
                                if not skip_expiry:
                                    await self.post_92c_maker_bid(ticker)
                    elif self.sustained_90_ticks.get(ticker, 0) > 0 and ask92 >= 92:
                        side92 = ticker.split("-")[-1]
                        log(f"[92+_WAIT] {side92} ask={ask92}c "
                            f"sustained={self.sustained_90_ticks[ticker]}/5")
                else:
                    # Price below 88 -- cancel any resting 92c bid
                    self.sustained_90_ticks[ticker] = 0
                    if ticker in self.mode_92_bids:
                        await self.cancel_92c_maker_bid(ticker)

    def _print_scan_state(self):
        """Print current filter state for all tracked tickers."""
        log(f"\n[SCAN] BBO received for {len(self.books)} tickers "
              f"({self.ws_msg_count} msgs) global_min_combined={self.global_min_combined}c")
        # Show combined asks for all events
        for et, tickers in sorted(self.event_tickers.items()):
            ticker_list = sorted(tickers)
            if len(ticker_list) != 2:
                continue
            t_a, t_b = ticker_list
            b_a = self.books.get(t_a)
            b_b = self.books.get(t_b)
            if not b_a or not b_b or b_a.best_ask is None or b_b.best_ask is None:
                continue
            mid_a = (b_a.best_ask + b_a.best_bid) / 2.0 if b_a.best_bid is not None else b_a.best_ask
            mid_b = (b_b.best_ask + b_b.best_bid) / 2.0 if b_b.best_bid is not None else b_b.best_ask
            combined_mid = mid_a + mid_b
            s_a = t_a.split("-")[-1]
            s_b = t_b.split("-")[-1]
            min_c = self.min_combined.get(et, int(combined_mid))
            flag = " << DISLOCATION" if combined_mid <= MAX_COMBINED_MID else ""
            log(f"  {et[-20:]}: {s_a}={b_a.best_bid}/{b_a.best_ask} "
                  f"{s_b}={b_b.best_bid}/{b_b.best_ask} "
                  f"combined_mid={combined_mid:.0f}c min={min_c}c{flag}")
        log("")

    # ------------------------------------------------------------------
    # Main loops
    # ------------------------------------------------------------------
    async def discovery_loop(self):
        """Periodically discover new tennis markets and subscribe."""
        while True:
            try:
                tickers = await self.discover_markets()
                if tickers:
                    await self.ws_subscribe(tickers)
                # Print scan state every discovery cycle
                if self._first_scan_printed:
                    self._print_scan_state()
            except Exception as e:
                log(f"[DISCOVERY_ERR] {e}")
            await asyncio.sleep(DISCOVERY_INTERVAL)

    async def resub_loop(self):
        """Periodic re-subscribe to avoid phantom depth."""
        while True:
            await asyncio.sleep(RESUB_INTERVAL)
            try:
                await self.ws_resubscribe_all()
            except Exception as e:
                log(f"[RESUB_ERR] {e}")

    async def fill_check_loop(self):
        """Poll for sell fills and settlements."""
        while True:
            await asyncio.sleep(5)
            try:
                if self.positions:
                    await self.check_fills()
                # Check 92c+ maker bid fills
                if self.mode_92_bids:
                    await self.check_92plus_bid_fills()
            except Exception as e:
                log(f"[FILL_CHECK_ERR] {e}")

    async def reentry_loop(self):
        """Check pending collapse re-entries every 10 seconds."""
        while True:
            await asyncio.sleep(10)
            try:
                now = time.time()
                for ticker in list(self.pending_reentries.keys()):
                    entry = self.pending_reentries[ticker]
                    reentry_time = entry[0]
                    orig_bid = entry[1]
                    attempt = entry[2] if len(entry) > 2 else 1
                    if now < reentry_time:
                        continue
                    self.pending_reentries.pop(ticker)
                    self.collapse_rejected.discard(ticker)
                    self._reentry_attempt[ticker] = attempt
                    side = ticker.split("-")[-1]
                    if not self.check_entry(ticker):
                        if attempt < 3:
                            next_attempt = attempt + 1
                            self.pending_reentries[ticker] = (
                                time.time() + COLLAPSE_REENTRY_DELAY, orig_bid, next_attempt)
                            self.collapse_rejected.add(ticker)
                            log(f"[REENTRY_NOFILTER] {side} filters fail attempt {attempt}/3 â retry in 10m")
                            continue
                        log(f"[REENTRY_SKIP] {side} dislocation resolved after {attempt} attempts")
                        self._reentry_attempt.pop(ticker, None)
                        self.entered_sides.add(ticker)
                        self.total_reentry_skips += 1
                        continue
                    self._reentry_attempt.pop(ticker, None)
                    await self.execute_entry(
                        ticker, is_reentry=True, original_price=orig_bid)
            except Exception as e:
                log(f"[REENTRY_ERR] {e}")

    async def stats_loop(self):
        """Print P&L stats periodically."""
        while True:
            await asyncio.sleep(STATS_INTERVAL)
            try:
                await self.fetch_balance()
                self.print_stats()
            except Exception as e:
                log(f"[STATS_ERR] {e}")

    async def ws_loop(self):
        """Main websocket message loop with reconnection."""
        import websockets
        reconnect_delay = 1

        while True:
            try:
                if not self.ws_connected:
                    success = await self.ws_connect()
                    if not success:
                        await asyncio.sleep(reconnect_delay)
                        reconnect_delay = min(reconnect_delay * 2, 60)
                        continue
                    reconnect_delay = 1
                    # Re-subscribe all tickers after reconnect
                    if self.subscribed:
                        old = list(self.subscribed)
                        self.subscribed.clear()
                        await self.ws_subscribe(old)

                try:
                    msg = await asyncio.wait_for(self.ws.recv(), timeout=45)
                except asyncio.TimeoutError:
                    # Send ping
                    continue

                data = json.loads(msg)
                msg_type = data.get("type", "")
                msg_data = data.get("msg", {})

                if msg_type == "orderbook_snapshot":
                    ticker = msg_data.get("market_ticker")
                    if ticker:
                        self.apply_snapshot(ticker, msg_data)
                        await self.on_bbo_update(ticker)

                elif msg_type == "orderbook_delta":
                    ticker = msg_data.get("market_ticker")
                    if ticker:
                        old_bid = self.books.get(ticker, LocalBook(ticker)).best_bid
                        old_ask = self.books.get(ticker, LocalBook(ticker)).best_ask
                        self.apply_delta(ticker, msg_data)
                        book = self.books.get(ticker)
                        if book and (book.best_bid != old_bid or book.best_ask != old_ask):
                            await self.on_bbo_update(ticker)

            except (websockets.ConnectionClosed, ConnectionError) as e:
                log(f"[WS] Disconnected: {e}")
                self.ws_connected = False
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60)
            except Exception as e:
                log(f"[WS_ERR] {e}")
                await asyncio.sleep(1)

    async def run(self):
        """Main entry point."""
        log("=" * 60)
        log("  Tennis STB v2 — Sell The Bounce + Game State")
        log(f"  ATP + WTA | Challengers: {CONTRACTS}ct, Main: {MAIN_DRAW_CONTRACTS}ct | +{EXIT_BOUNCE}c exit target")
        log(f"  Combined MID <= {MAX_COMBINED_MID}c | Entry ask >= {MIN_ENTRY_ASK}c | Spread <= {MAX_SPREAD}c")
        log(f"  All tennis: hold to settlement (no stop)")
        log(f"  Collapse filter: {COLLAPSE_DROP_THRESHOLD}c drop in "
            f"{COLLAPSE_LOOKBACK_SEC//60}m -> re-enter after {COLLAPSE_REENTRY_DELAY//60}m")
        log(f"  Game state: reject down 0-2 sets, ended/scheduled matches")
        log("=" * 60)

        self.session = aiohttp.ClientSession()
        try:
            # Initial balance
            bal = await self.fetch_balance()
            log(f"[INIT] Balance: ${bal:.2f}" if bal else "[INIT] Balance check failed")

            # Initial discovery
            tickers = await self.discover_markets()
            log(f"[INIT] Found {len(tickers)} tennis tickers across {len(self.known_events)} events")

            if not tickers:
                log("[INIT] No open tennis markets found. Waiting for new markets...")

            # Cancel ALL resting tennis orders before anything else
            await self.cancel_all_resting_orders()

            # Rebuild entered_sides from fill history (survives restarts)
            await self.rebuild_entered_sides()

            # Connect WS and subscribe
            await self.ws_connect()
            if tickers:
                await self.ws_subscribe(tickers)

            # Check for existing positions that might need sell orders
            await self.reconcile_existing_positions()

            # Launch all loops (includes cond stop loop for challengers)
            await asyncio.gather(
                self.ws_loop(),
                self.discovery_loop(),
                self.resub_loop(),
                self.fill_check_loop(),
                self.reentry_loop(),
                self.stats_loop(),
            )
        finally:
            await self.session.close()

    async def cancel_all_resting_orders(self):
        """Cancel ALL resting orders on tennis tickers. Called once at startup."""
        cancelled = 0
        cursor = ""
        pages = 0
        while pages < 10:
            path = "/trade-api/v2/portfolio/orders?status=resting&limit=100"
            if cursor:
                path += f"&cursor={cursor}"
            result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
            if not result:
                break
            orders = result.get("orders", [])
            if not orders:
                break
            for o in orders:
                oid = o.get("order_id", "")
                ticker = o.get("ticker", "")
                is_tennis = any(ticker.startswith(s) for s in SERIES)
                if not is_tennis:
                    continue
                del_path = f"/trade-api/v2/portfolio/orders/{oid}"
                await api_delete(self.session, self.api_key, self.private_key, del_path, self.rl)
                price = o.get("yes_price", "?")
                action = o.get("action", "?")
                log(f"[CANCEL_RESTING] {ticker.split('-')[-1]} {action} yes@{price}c oid={oid[:12]}")
                cancelled += 1
            cursor = result.get("cursor", "")
            pages += 1
            if not cursor:
                break
        if cancelled:
            log(f"[INIT] Cancelled {cancelled} stale resting orders")
        else:
            log("[INIT] No resting tennis orders to cancel")

    async def rebuild_entered_sides(self):
        """Rebuild entered_sides from today's fill history so restarts don't re-enter."""
        cursor = ""
        pages = 0
        recovered = 0
        while pages < 10:
            path = "/trade-api/v2/portfolio/fills?limit=100"
            if cursor:
                path += f"&cursor={cursor}"
            result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
            if not result:
                break
            fills = result.get("fills", [])
            if not fills:
                break
            for f in fills:
                ticker = f.get("ticker", "")
                action = f.get("action", "")
                is_tennis = any(ticker.startswith(s) for s in SERIES)
                if not is_tennis:
                    continue
                # Any ticker we've ever bought = entered, never re-enter
                if action == "buy" and ticker not in self.entered_sides:
                    self.entered_sides.add(ticker)
                    recovered += 1
            cursor = result.get("cursor", "")
            pages += 1
            if not cursor:
                break
        if recovered:
            log(f"[INIT] Recovered {recovered} entered sides from fill history: "
                  f"{', '.join(t.split('-')[-1] for t in self.entered_sides)}")
        else:
            log("[INIT] No previous tennis entries found in fill history")

    async def _get_actual_entry_price(self, ticker: str) -> Optional[int]:
        """Get the actual buy price from fills history (not avg_price)."""
        path = f"/trade-api/v2/portfolio/fills?ticker={ticker}&limit=50"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return None
        # Find the most recent buy fill
        for f in result.get("fills", []):
            if f.get("action") == "buy" and f.get("side") == "yes":
                return f.get("yes_price")
        return None

    async def reconcile_existing_positions(self):
        """Check for existing Kalshi positions in tennis markets at startup.
        All resting orders have already been cancelled by cancel_all_resting_orders().
        """
        path = "/trade-api/v2/portfolio/positions?count_filter=position&limit=200"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return

        for p in result.get("market_positions", []):
            ticker = p.get("ticker", "")
            position = p.get("position", 0)
            if position <= 0:
                continue

            # Check if this is a tennis ticker
            is_tennis = any(ticker.startswith(s) for s in SERIES)
            if not is_tennis:
                continue

            # Get ACTUAL entry price from fills, not the unreliable avg_price
            actual_price = await self._get_actual_entry_price(ticker)
            if actual_price is None:
                # Fallback to API avg_price only if fills unavailable
                actual_price = p.get("market_average_price", 0)
                if actual_price == 0:
                    book = self.books.get(ticker)
                    actual_price = book.best_ask if book and book.best_ask else 60
                log(f"[RECONCILE] {ticker} {position}ct — fills unavailable, "
                      f"using fallback avg_price={actual_price}c")
            else:
                api_avg = p.get("market_average_price", 0)
                if api_avg != actual_price:
                    log(f"[RECONCILE] {ticker} {position}ct — "
                        f"actual_entry={actual_price}c (API avg_price={api_avg}c was WRONG)")
                else:
                    log(f"[RECONCILE] {ticker} {position}ct — entry={actual_price}c")

            et = self.ticker_to_event.get(ticker, "")
            side = ticker.split("-")[-1]
            sell_price = actual_price + EXIT_BOUNCE

            pos = Position(
                ticker=ticker, event_ticker=et, side=side,
                entry_ask=actual_price, entry_bid=0, entry_spread=0,
                combined_ask=0, entry_ts=time.time(),
                contracts=position, sell_price=sell_price,
                buy_confirmed=True,  # reconciled = already own shares
                buy_fill_ts=time.time(),
            )
            pos.depth_snapshot = None
            self.positions[ticker] = pos
            self.entered_sides.add(ticker)
            if et:
                self.entered_events.add(et)  # Fix 3: event-level dedup

            # Fix: restore entry_mode for 92c+ positions so stop loss works
            if actual_price >= 92:
                pos.entry_mode = "stb_92plus"

            # Place exit sell (safe — all resting were already cancelled)
            log(f"  [RECONCILE_SELL] Placing sell at {sell_price}c "
                  f"(entry={actual_price}c + {EXIT_BOUNCE}c bounce)")
            await self.place_exit_sell(ticker)


def main():
    bot = TennisSTB()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        log("\n[SHUTDOWN] Ctrl+C — positions and resting sells remain on Kalshi")
        bot.print_stats()


if __name__ == "__main__":
    main()
