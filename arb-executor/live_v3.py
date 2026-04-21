#!/usr/bin/env python3
"""
live_v3.py - LIVE Deploy V3, baby sizing (10ct entry / 5ct DCA).

Places REAL orders on Kalshi. Maker-only, post_only=true.
Exit price capped at min(fill_price + exit_cents, 98).
Cell assignment at order-post time. Fill price drives exit/DCA offsets.
"""

import asyncio
import aiohttp
import base64
import json
import os
import sys
import time
import traceback
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Set, List, Optional
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from fv import get_consensus_fv, check_fv_stability

try:
    from intelligence import recommended_window_seconds, kalshi_price_anchor
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False

def _parse_ticker_date(event_ticker: str):
    """Parse YYMMMDD from ticker like KXATPMATCH-26APR21GEAGAU -> datetime(2026,4,21,11,0 UTC)."""
    import re as _re
    m = _re.search(r'-(\d{2})([A-Z]{3})(\d{2})', event_ticker)
    if not m:
        return None
    yy, mmm, dd = m.groups()
    _month_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                  "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    if mmm not in _month_map:
        return None
    try:
        return datetime(2000 + int(yy), _month_map[mmm], int(dd), 11, 0, tzinfo=timezone.utc)
    except ValueError:
        return None

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------
BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"
MAX_RPS = 8
MIN_VOLUME = 0
MAX_HOURS_TO_EXPIRY = 36
WS_PING_INTERVAL = 15
WS_SUBSCRIBE_BATCH = 50
DISCOVERY_INTERVAL = 300
# ENTRY_CANCEL_TIMEOUT removed in V4.2 -- replaced by match-start-aware expiry
FILL_CHECK_INTERVAL = 5      # poll fills every 5s
EXIT_PRICE_CAP = 98           # never post exit above 98c
ENTRY_BUFFER_SEC = 900        # stop entering 15 min before scheduled start
ENTRY_MAX_LEAD_SEC = 14400    # don't enter more than 4h before start
UNMATCHED_SKIP_CYCLES = 3     # skip unmatched events after this many discovery cycles
UNMATCHED_SKIP_AGE = 3600     # ...only if open_time is > 1h old
DEAD_SPREAD_THRESHOLD = 20    # don't post if spread > 20c
STALE_BUY_DELTA = 5           # cancel resting buy if our price > mid + 5c
PENDING_TIMEOUT_SEC = 7200    # cancel pending entry after 2h with no tight spread
STALE_CHECK_INTERVAL = 120    # validate resting buys every 2 min

STATE_DIR = Path(__file__).resolve().parent / "state"
PROCESSED_FILE = STATE_DIR / "live_v3_processed.json"
SCHEDULE_FILE = STATE_DIR / "schedule.json"
TICK_DIR = Path(__file__).resolve().parent / "analysis" / "premarket_ticks"
TRADE_DIR = Path(__file__).resolve().parent / "analysis" / "trades"

SERIES_MAP = {
    'ATP_MAIN': ['KXATPMATCH'],
    'WTA_MAIN': ['KXWTAMATCH'],
    'ATP_CHALL': ['KXATPCHALLENGERMATCH'],
    'WTA_CHALL': ['KXWTACHALLENGERMATCH'],
    'ATP_SLAM': ['KXATPGRANDSLAM'],
    'WTA_SLAM': ['KXWTAGRANDSLAM'],
}
ALL_SERIES = []
for prefixes in SERIES_MAP.values():
    ALL_SERIES.extend(prefixes)

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "deploy_v4.json"
LOG_DIR = Path(__file__).resolve().parent / "logs"

# -------------------------------------------------------------------------
# Credentials
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# Rate limiter
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# Async HTTP helpers
# -------------------------------------------------------------------------
async def api_get(s, ak, pk, path, rl):
    for bo in [1, 2, 4, None]:
        await rl.acquire()
        try:
            async with s.get("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "GET", path),
                             timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    return await r.json()
                if r.status == 429 and bo:
                    await asyncio.sleep(bo)
                    continue
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo:
                await asyncio.sleep(bo)
                continue
            return None
    return None

async def api_post(s, ak, pk, path, payload, rl):
    for bo in [2, None]:
        await rl.acquire()
        try:
            async with s.post("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "POST", path),
                              json=payload, timeout=aiohttp.ClientTimeout(total=15)) as r:
                body = await r.text()
                if r.status in (200, 201):
                    return json.loads(body)
                if r.status == 429 and bo:
                    await asyncio.sleep(bo)
                    continue
                return {"_error": True, "_status": r.status, "_body": body[:500]}
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if bo:
                await asyncio.sleep(bo)
                continue
            return {"_error": True, "_status": 0, "_body": str(e)}
    return {"_error": True, "_status": 0, "_body": "exhausted retries"}

async def api_delete(s, ak, pk, path, rl):
    for bo in [2, None]:
        await rl.acquire()
        try:
            async with s.delete("%s%s" % (BASE_URL, path), headers=auth_headers(ak, pk, "DELETE", path),
                                timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status in (200, 204):
                    return True
                if r.status == 429 and bo:
                    await asyncio.sleep(bo)
                    continue
                return False
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if bo:
                await asyncio.sleep(bo)
                continue
            return False
    return False

# -------------------------------------------------------------------------
# Book
# -------------------------------------------------------------------------
@dataclass
class Book:
    bids: Dict[int, int] = field(default_factory=dict)
    asks: Dict[int, int] = field(default_factory=dict)
    best_bid: int = 0
    best_ask: int = 100
    updated: float = 0.0
    last_trade_price: int = 0
    last_trade_ts: float = 0.0
    last_trade_side: str = ""

def recalc_bbo(b):
    b.best_bid = max(b.bids.keys()) if b.bids else 0
    b.best_ask = min(b.asks.keys()) if b.asks else 100

# -------------------------------------------------------------------------
# Position state per ticker
# -------------------------------------------------------------------------
@dataclass
class Position:
    ticker: str
    event_ticker: str
    category: str
    direction: str
    cell_name: str
    cell_cfg: dict

    # Entry
    entry_price: int = 0
    entry_qty: int = 0
    entry_order_id: str = ""
    entry_posted_ts: float = 0.0
    match_start_ts: float = 0.0
    entry_filled_ts: float = 0.0

    # Exit
    exit_price: int = 0
    exit_order_id: str = ""
    exit_filled: bool = False

    # DCA
    dca_price: int = 0
    dca_order_id: str = ""
    dca_qty: int = 0
    dca_filled: bool = False

    # Play type (Piece 2A)
    play_type: str = "A_tight"
    layered_exit_price: int = 0
    cell_exit_order_id: str = ""
    cell_exit_price: int = 0
    legacy: bool = False

    # State
    phase: str = "entry_pending"
    settled: bool = False
    pnl_cents: float = 0.0

# -------------------------------------------------------------------------
# Live V3 Bot
# -------------------------------------------------------------------------
class LiveV3:
    def __init__(self):
        self.ak, self.pk = load_credentials()
        self.rl = RateLimiter()
        self.session = None
        self.ws = None
        self.ws_connected = False

        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        self.entry_size = self.config["sizing"]["entry_contracts"]
        self.dca_size = self.config["sizing"]["dca_contracts"]
        self.dca_fill_floor = self.config["dca_fill_floor_cents"]

        self.books: Dict[str, Book] = {}
        self.subscribed: Set[str] = set()
        self.msg_id = 0
        self.ticker_to_event: Dict[str, str] = {}
        self.event_tickers: Dict[str, Set[str]] = defaultdict(set)
        self.ticker_category: Dict[str, str] = {}
        self.event_open_time: Dict[str, float] = {}   # Kalshi open_time (for unmatched-skip logic)
        self.event_start_time: Dict[str, float] = {}   # scheduled start from TE/ESPN
        self.event_player_names: Dict[str, List[str]] = {}  # player names per event
        self.event_unmatched_cycles: Dict[str, int] = {}  # discovery cycles without schedule match

        self.positions: Dict[str, Position] = {}
        self.pending_entries: Dict[str, dict] = {}  # ticker -> {event, direction, cat, cell_name, cell_cfg, discovered_ts}
        self.inflight_orders: Set[str] = set()  # tickers with orders being placed (race guard)

        # Persistent processed-tickers set (survives restarts)
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.processed_events: Set[str] = self._load_processed()

        # Schedule loaded after log_file init (below)
        self.schedule: dict = {}

        # Tick logging
        TICK_DIR.mkdir(parents=True, exist_ok=True)
        TRADE_DIR.mkdir(parents=True, exist_ok=True)
        self._tick_files: Dict[str, object] = {}
        self._tick_writers: Dict[str, object] = {}
        self._tick_last_bbo: Dict[str, tuple] = {}  # dedup unchanged ticks
        self._trade_files: Dict[str, object] = {}
        self._trade_writers: Dict[str, object] = {}

        self.n_matches_seen = 0
        self.n_entries = 0
        self.n_skips = 0
        self.n_exits = 0
        self.n_dcas = 0
        self.n_settlements = 0
        self.start_ts = time.time()

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(ET).strftime("%Y%m%d")
        self.log_path = LOG_DIR / ("live_v3_%s.jsonl" % date_str)
        self.log_file = open(self.log_path, "a")
        self._log("system_start", {"mode": "LIVE", "config_path": str(CONFIG_PATH),
                                    "active_cells": len(self.config["active_cells"]),
                                    "disabled_cells": len(self.config["disabled_cells"]),
                                    "entry_size": self.entry_size,
                                    "dca_size": self.dca_size,
                                    "exit_cap": EXIT_PRICE_CAP})
        self._load_schedule()

    def _log(self, event, details=None, ticker=""):
        entry = {
            "ts": datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET"),
            "ts_epoch": time.time(),
            "event": event,
            "ticker": ticker,
            "details": details or {},
        }
        self.log_file.write(json.dumps(entry) + "\n")
        self.log_file.flush()
        print("[%s] %s %s %s" % (
            datetime.now(ET).strftime("%I:%M:%S %p"),
            event.upper().ljust(20),
            ticker[:40] if ticker else "",
            json.dumps(details)[:120] if details else ""
        ), flush=True)

    def _load_processed(self):
        try:
            with open(PROCESSED_FILE) as f:
                return set(json.load(f))
        except (FileNotFoundError, ValueError):
            return set()

    def _save_processed(self):
        with open(PROCESSED_FILE, "w") as f:
            json.dump(sorted(self.processed_events), f)

    def _load_schedule(self):
        """Load schedule from cron-refreshed state/schedule.json."""
        try:
            with open(SCHEDULE_FILE) as f:
                data = json.load(f)
            self.schedule = data.get("schedule", {})
            age = time.time() - data.get("fetched_epoch", time.time())
            self._log("schedule_loaded", {
                "count": len(self.schedule),
                "fetched": data.get("fetched_et", "?"),
                "age_min": round(age / 60),
            })
        except FileNotFoundError:
            self._log("schedule_missing", {"path": str(SCHEDULE_FILE)})
            self.schedule = {}
        except Exception as e:
            self._log("schedule_error", {"error": str(e)})
            self.schedule = {}

    def _match_event_to_schedule(self, event_ticker):
        """Match Kalshi event to schedule. Returns (entry, method) or (None, None).
        Logs every attempt for 7-day audit trail."""
        from tennis_schedule import match_kalshi_event

        player_names = self.event_player_names.get(event_ticker, [])

        # Try direct match first
        result = match_kalshi_event(event_ticker, self.schedule)
        if result:
            self._log("schedule_match", {
                "event": event_ticker,
                "method": "direct_6char",
                "start_time": result.get("start_time", "?"),
                "p1": result.get("p1", "?"),
                "p2": result.get("p2", "?"),
                "category": result.get("category", "?"),
                "kalshi_players": player_names,
            })
            return result, "direct_6char"

        # Try fuzzy with player names
        if player_names:
            result = match_kalshi_event(event_ticker, self.schedule, kalshi_player_names=player_names)
            if result:
                self._log("schedule_match", {
                    "event": event_ticker,
                    "method": "fuzzy_name",
                    "start_time": result.get("start_time", "?"),
                    "p1": result.get("p1", "?"),
                    "p2": result.get("p2", "?"),
                    "category": result.get("category", "?"),
                    "kalshi_players": player_names,
                })
                return result, "fuzzy_name"

        # No match — log with closest candidate for debugging
        import re
        parts = event_ticker.split("-")
        raw = parts[-1] if len(parts) >= 2 else ""
        m = re.match(r"\d{2}[A-Z]{3}\d{2}(.+)", raw)
        pair_code = m.group(1) if m else raw

        closest = ""
        if pair_code and self.schedule:
            candidates = sorted(self.schedule.keys())
            # Simple prefix match for closest
            matches = [k for k in candidates if k[:3] == pair_code[:3] or k[3:] == pair_code[3:]]
            closest = ", ".join(matches[:3]) if matches else "(none with shared prefix)"

        self._log("schedule_unmatched", {
            "event": event_ticker,
            "pair_code": pair_code,
            "kalshi_players": player_names,
            "closest_schedule_keys": closest,
            "schedule_size": len(self.schedule),
        })
        return None, None

    def get_category(self, ticker):
        for cat_name, prefixes in SERIES_MAP.items():
            for prefix in prefixes:
                if ticker.startswith(prefix):
                    return cat_name
        return None

    def cell_lookup(self, category, direction, entry_mid):
        bucket = int(entry_mid / 5) * 5
        cell_name = "%s_%s_%d-%d" % (category, direction, bucket, bucket + 4)
        if cell_name in self.config["disabled_cells"]:
            return cell_name, None
        if cell_name in self.config["active_cells"]:
            return cell_name, self.config["active_cells"][cell_name]
        return cell_name, None

    def _extract_depth(self, book, side="bid", levels=5):
        """Extract top N price levels with sizes. Returns list of (price, size) tuples."""
        if side == "bid":
            items = sorted(book.bids.items(), reverse=True)[:levels]
        else:
            items = sorted(book.asks.items())[:levels]
        result = list(items)
        while len(result) < levels:
            result.append(("", ""))
        return result

    def _depth_signature(self, book):
        """Hashable snapshot of top-5 depth on both sides for dedup."""
        bids = tuple(sorted(book.bids.items(), reverse=True)[:5])
        asks = tuple(sorted(book.asks.items())[:5])
        return (bids, asks)

    def _log_tick(self, ticker, book):
        """Write depth tick to per-ticker CSV. Dedup on top-5 depth change."""
        bid, ask = book.best_bid, book.best_ask
        if bid <= 0 or ask >= 100:
            return
        sig = self._depth_signature(book)
        last = self._tick_last_bbo.get(ticker)
        if last and last == sig:
            return
        self._tick_last_bbo[ticker] = sig
        mid = (bid + ask) / 2.0

        bid_levels = self._extract_depth(book, "bid")
        ask_levels = self._extract_depth(book, "ask")

        if ticker not in self._tick_writers:
            import csv as _csv
            path = TICK_DIR / ("%s.csv" % ticker)
            is_new = not path.exists() or path.stat().st_size == 0
            fh = open(path, "a", newline="")
            w = _csv.writer(fh)
            if is_new:
                header = ["ts_et", "ticker"]
                for i in range(1, 6):
                    header += ["bid_%d" % i, "bid_%d_sz" % i]
                for i in range(1, 6):
                    header += ["ask_%d" % i, "ask_%d_sz" % i]
                header += ["mid", "bid_depth_5", "ask_depth_5", "depth_ratio", "last_trade"]
                w.writerow(header)
                fh.flush()
            self._tick_files[ticker] = fh
            self._tick_writers[ticker] = w

        ts_str = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p")
        row = [ts_str, ticker]
        total_bid_sz = 0
        total_ask_sz = 0
        for price, size in bid_levels:
            row += [price, size]
            if isinstance(size, (int, float)) and size > 0:
                total_bid_sz += size
        for price, size in ask_levels:
            row += [price, size]
            if isinstance(size, (int, float)) and size > 0:
                total_ask_sz += size
        total = total_bid_sz + total_ask_sz
        depth_ratio = total_bid_sz / total if total > 0 else 0.5
        row += ["%.1f" % mid, total_bid_sz, total_ask_sz, "%.3f" % depth_ratio, book.last_trade_price]
        self._tick_writers[ticker].writerow(row)
        self._tick_files[ticker].flush()

    def apply_trade(self, ticker, msg):
        """Process a trade event from WebSocket."""
        if ticker not in self.books:
            self.books[ticker] = Book()
        book = self.books[ticker]
        price_raw = msg.get("yes_price", msg.get("yes_price_dollars", 0))
        if isinstance(price_raw, str):
            price_raw = float(price_raw)
        price = round(price_raw * 100) if price_raw < 2 else int(price_raw)
        count = msg.get("count", msg.get("count_fp", 0))
        if isinstance(count, str):
            count = int(float(count))
        side = msg.get("taker_side", "?")
        book.last_trade_price = price
        book.last_trade_ts = time.time()
        book.last_trade_side = side
        self._log_trade(ticker, price, count, side)

    def _log_trade(self, ticker, price, count, taker_side):
        """Write trade to per-ticker CSV."""
        if ticker not in self._trade_writers:
            import csv as _csv
            path = TRADE_DIR / ("%s.csv" % ticker)
            is_new = not path.exists() or path.stat().st_size == 0
            fh = open(path, "a", newline="")
            w = _csv.writer(fh)
            if is_new:
                w.writerow(["ts_et", "ticker", "price", "count", "taker_side"])
                fh.flush()
            self._trade_files[ticker] = fh
            self._trade_writers[ticker] = w
        ts_str = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p")
        self._trade_writers[ticker].writerow([ts_str, ticker, price, count, taker_side])
        self._trade_files[ticker].flush()

    # ------------------------------------------------------------------
    # Order placement — REAL Kalshi API calls
    # ------------------------------------------------------------------
    async def place_order(self, ticker, action, side, price, count, post_only=True):
        """Place a real order on Kalshi. Returns (order_id, response_dict) or ("", error_dict)."""
        path = "/trade-api/v2/portfolio/orders"
        coid = str(uuid.uuid4())
        payload = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "type": "limit",
            "count": count,
            "yes_price": price,
            "post_only": post_only,
            "client_order_id": coid,
        }
        resp = await api_post(self.session, self.ak, self.pk, path, payload, self.rl)
        if resp and not resp.get("_error"):
            oid = resp.get("order", {}).get("order_id", "")
            self._log("order_placed", {
                "action": action, "side": side, "price": price, "count": count,
                "order_id": oid, "client_order_id": coid,
                "response_status": resp.get("order", {}).get("status", "?"),
            }, ticker=ticker)
            return oid, resp
        else:
            self._log("order_error", {
                "action": action, "side": side, "price": price, "count": count,
                "error_status": resp.get("_status") if resp else "null",
                "error_body": resp.get("_body", "")[:300] if resp else "null response",
            }, ticker=ticker)
            return "", resp

    async def cancel_order(self, ticker, order_id, label=""):
        """Cancel a resting order. Returns True on success."""
        if not order_id:
            return False
        path = "/trade-api/v2/portfolio/orders/%s" % order_id
        ok = await api_delete(self.session, self.ak, self.pk, path, self.rl)
        self._log("order_cancelled", {
            "order_id": order_id, "label": label, "success": ok,
        }, ticker=ticker)
        return ok

    # ------------------------------------------------------------------
    # WebSocket (identical to paper_v3)
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
            self._log("ws_connected")
            return True
        except Exception as e:
            self._log("ws_connect_failed", {"error": str(e)})
            self.ws_connected = False
            return False

    async def ws_subscribe(self, tickers):
        if not self.ws_connected or not self.ws:
            return
        new = [t for t in tickers if t not in self.subscribed]
        if not new:
            return
        for i in range(0, len(new), WS_SUBSCRIBE_BATCH):
            batch = new[i:i + WS_SUBSCRIBE_BATCH]
            self.msg_id += 1
            try:
                await self.ws.send(json.dumps({"id": self.msg_id, "cmd": "subscribe",
                    "params": {"channels": ["orderbook_delta", "trade"], "market_tickers": batch}}))
                self.subscribed.update(batch)
                await asyncio.sleep(0.05)
            except Exception as e:
                self._log("ws_subscribe_error", {"error": str(e)})
        self._log("ws_subscribed", {"new": len(new), "total": len(self.subscribed)})

    def apply_snapshot(self, ticker, msg):
        book = Book()
        for level in msg.get("yes_dollars_fp", msg.get("yes", [])):
            if isinstance(level, list) and len(level) >= 2:
                price, size = round(float(level[0]) * 100), int(float(level[1]))
                if size > 0:
                    book.bids[price] = size
        for level in msg.get("no_dollars_fp", msg.get("no", [])):
            if isinstance(level, list) and len(level) >= 2:
                no_price, size = round(float(level[0]) * 100), int(float(level[1]))
                if size > 0:
                    book.asks[100 - no_price] = size
        recalc_bbo(book)
        book.updated = time.time()
        self.books[ticker] = book
        self._log_tick(ticker, book)

    def apply_delta(self, ticker, msg):
        if ticker not in self.books:
            self.books[ticker] = Book()
        book = self.books[ticker]
        price_raw = msg.get("price_dollars", msg.get("price"))
        delta = msg.get("delta_fp", msg.get("delta", 0))
        side = msg.get("side", "yes").lower()
        if price_raw is None:
            return
        price = round(float(price_raw) * 100)
        if side == "yes":
            book.bids[price] = book.bids.get(price, 0) + int(float(delta))
            if book.bids[price] <= 0:
                book.bids.pop(price, None)
        else:
            ap = 100 - price
            book.asks[ap] = book.asks.get(ap, 0) + int(float(delta))
            if book.asks[ap] <= 0:
                book.asks.pop(ap, None)
        recalc_bbo(book)
        book.updated = time.time()
        self._log_tick(ticker, book)

    async def _ws_reconnect(self):
        """Reconnect WebSocket with exponential backoff. Never gives up."""
        delays = [5, 10, 30, 60]
        attempt = 0
        while True:
            delay = delays[min(attempt, len(delays) - 1)]
            self._log("ws_reconnecting", {"attempt": attempt + 1, "delay_sec": delay})
            await asyncio.sleep(delay)
            if await self.ws_connect():
                if self.subscribed:
                    old = list(self.subscribed)
                    self.subscribed.clear()
                    await self.ws_subscribe(old)
                self._log("ws_reconnected", {"attempt": attempt + 1})
                return
            attempt += 1

    async def ws_reader(self):
        while True:
            try:
                if not self.ws_connected or not self.ws:
                    await self._ws_reconnect()
                    continue
                raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
                msg = json.loads(raw)
                typ = msg.get("type", "")
                if typ == "orderbook_snapshot":
                    self.apply_snapshot(msg.get("msg", {}).get("market_ticker", ""), msg.get("msg", {}))
                elif typ == "orderbook_delta":
                    self.apply_delta(msg.get("msg", {}).get("market_ticker", ""), msg.get("msg", {}))
                elif typ == "trade":
                    self.apply_trade(msg.get("msg", {}).get("market_ticker", msg.get("msg", {}).get("ticker", "")),
                                    msg.get("msg", {}))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._log("ws_error", {"error": str(e)})
                self.ws_connected = False
                await self._ws_reconnect()

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
                if cursor:
                    path += "&cursor=%s" % cursor
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data:
                    break
                for m in data.get("markets", []):
                    ticker = m["ticker"]
                    vol = int(float(m.get("volume_fp", "0") or "0"))
                    if vol < MIN_VOLUME:
                        continue
                    expiry_str = m.get("expected_expiration_time", "")
                    if expiry_str and not expiry_str.startswith("0001"):
                        try:
                            exp = datetime.fromisoformat(expiry_str.replace("Z", "+00:00")).timestamp()
                            if (exp - now) / 3600 > MAX_HOURS_TO_EXPIRY:
                                continue
                        except:
                            pass
                    et = m["event_ticker"]
                    self.ticker_to_event[ticker] = et
                    self.event_tickers[et].add(ticker)
                    # Capture open_time (for unmatched-skip age check)
                    if et not in self.event_open_time:
                        ot_str = m.get("open_time", "")
                        if ot_str:
                            try:
                                self.event_open_time[et] = datetime.fromisoformat(
                                    ot_str.replace("Z", "+00:00")).timestamp()
                            except Exception:
                                pass
                    # Capture player names for schedule matching
                    if et not in self.event_player_names:
                        names = []
                        yes_name = m.get("yes_sub_title", "")
                        no_name = m.get("no_sub_title", "")
                        if yes_name:
                            names.append(yes_name)
                        if no_name and no_name != yes_name:
                            names.append(no_name)
                        if names:
                            self.event_player_names[et] = names
                    # Schedule match (if not already matched and not processed)
                    if et not in self.event_start_time and et not in self.processed_events:
                        sched_entry, method = self._match_event_to_schedule(et)
                        if sched_entry:
                            st_str = sched_entry.get("start_time", "")
                            if st_str:
                                try:
                                    self.event_start_time[et] = datetime.fromisoformat(
                                        st_str.replace("Z", "+00:00")).timestamp()
                                except Exception:
                                    pass
                        else:
                            # Fallback 1: Odds API commence_time from book_prices
                            ct = self._commence_time_from_book_prices(et)
                            if ct is not None:
                                self.event_start_time[et] = ct.timestamp()
                                self._log("schedule_match", {
                                    "event": et, "method": "odds_api_commence_time",
                                    "start_time": ct.isoformat(),
                                })
                            else:
                                # Fallback 2: Kalshi's own commence_time from price snapshots
                                kct = self._kalshi_commence_time(et)
                                if kct is not None:
                                    self.event_start_time[et] = kct.timestamp()
                                    self._log("schedule_match", {
                                        "event": et, "method": "kalshi_commence_time",
                                        "start_time": kct.isoformat(),
                                    })
                                else:
                                    self.event_unmatched_cycles[et] = self.event_unmatched_cycles.get(et, 0) + 1
                    cat = self.get_category(ticker)
                    if cat:
                        self.ticker_category[ticker] = cat
                        counts[cat] += 1
                        all_tickers.append(ticker)
                cursor = data.get("cursor", "")
                if not cursor:
                    break
        self._log("discovery", {"total_tickers": len(all_tickers), "by_category": dict(counts)})
        return all_tickers

    # ------------------------------------------------------------------
    # Side identification
    # ------------------------------------------------------------------
    def identify_sides(self, event_ticker):
        tickers = list(self.event_tickers.get(event_ticker, set()))
        if len(tickers) < 2:
            return []
        sides = []
        for tk in tickers:
            book = self.books.get(tk)
            if not book or book.updated < time.time() - 120:
                continue
            sides.append((tk, book.best_bid, book.best_ask))
        if len(sides) < 2:
            return []
        sides.sort(key=lambda x: -x[1])
        leader_tk, leader_bid, _ = sides[0]
        underdog_tk, underdog_bid, _ = sides[1]
        cat = self.get_category(leader_tk)
        if not cat:
            return []
        results = []
        if leader_bid > 50:
            results.append((leader_tk, "leader", cat))
        if underdog_bid < 50 and underdog_bid > 0:
            results.append((underdog_tk, "underdog", cat))
        return results

    # ------------------------------------------------------------------
    # Check fills via REST API
    # ------------------------------------------------------------------
    def _untombstone_entry(self, tk, pos):
        """Handle entry cancellation. If unfilled, remove from processed_events
        to allow re-entry. If partially filled, keep position managed."""
        if pos.entry_qty > 0:
            # Partially filled — position is real, keep it managed
            pos.entry_order_id = ""
            pos.phase = "active"
            self._log("entry_cancel_partial", {
                "filled_qty": pos.entry_qty, "kept_position": True,
            }, ticker=tk)
            return
        # Unfilled — remove tombstone, allow re-entry
        et = pos.event_ticker
        if et and et in self.processed_events:
            self.processed_events.discard(et)
            self._save_processed()
        if tk in self.positions:
            del self.positions[tk]

    SIDECAR_INTERVALS = {
        "tennis_odds": 600,
        "betexplorer": 700,
        "fv_monitor": 400,
        "kalshi_price": 400,
    }

    def _check_sidecar_heartbeats(self):
        now = int(time.time())
        for name, expected in self.SIDECAR_INTERVALS.items():
            path = "/tmp/heartbeat_%s.json" % name
            try:
                with open(path) as f:
                    hb = json.load(f)
                age = now - hb.get("ts", 0)
                if age > expected * 2:
                    self._log("sidecar_stale", {
                        "name": name, "age_sec": age,
                        "expected_max_age": expected * 2,
                        "last_extra": {k: v for k, v in hb.items() if k not in ("ts", "name", "status")},
                    })
            except FileNotFoundError:
                self._log("sidecar_missing", {"name": name, "path": path})
            except Exception as e:
                self._log("sidecar_heartbeat_error", {"name": name, "error": str(e)})

    def _commence_time_from_book_prices(self, event_ticker):
        """Query book_prices for most recent commence_time for this event."""
        import sqlite3 as _sql
        try:
            conn = _sql.connect(str(Path(__file__).resolve().parent / "tennis.db"), timeout=5)
            cur = conn.cursor()
            cur.execute(
                "SELECT commence_time FROM book_prices WHERE event_ticker=? "
                "AND commence_time IS NOT NULL AND commence_time != '' "
                "ORDER BY polled_at DESC LIMIT 1",
                (event_ticker,))
            row = cur.fetchone()
            conn.close()
            if not row or not row[0]:
                return None
            ct = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if timedelta(hours=-6) < (ct - now) < timedelta(hours=120):
                return ct
            return None
        except Exception:
            return None

    def _kalshi_commence_time(self, event_ticker):
        """Query kalshi_price_snapshots for commence_time."""
        import sqlite3 as _sql
        try:
            conn = _sql.connect(str(Path(__file__).resolve().parent / "tennis.db"), timeout=5)
            cur = conn.cursor()
            cur.execute(
                "SELECT commence_time FROM kalshi_price_snapshots WHERE event_ticker=? "
                "AND commence_time IS NOT NULL AND commence_time != '' "
                "ORDER BY polled_at DESC LIMIT 1",
                (event_ticker,))
            row = cur.fetchone()
            conn.close()
            if not row or not row[0]:
                return None
            ct = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if timedelta(hours=-2) < (ct - now) < timedelta(hours=120):
                return ct
            return None
        except Exception:
            return None

    def _get_side_fv(self, ticker, event_ticker):
        """Return get_consensus_fv result for the side corresponding to this Kalshi ticker."""
        import sqlite3
        conn = sqlite3.connect(str(Path(__file__).resolve().parent / "tennis.db"), timeout=5)
        cur = conn.cursor()
        cur.execute(
            "SELECT player1_name, player2_name FROM book_prices WHERE event_ticker = ? ORDER BY polled_at DESC LIMIT 1",
            (event_ticker,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        p1_name, p2_name = row
        ticker_side = ticker.split("-")[-1].upper()
        p1_last3 = p1_name.split()[-1].upper()[:3]
        p2_last3 = p2_name.split()[-1].upper()[:3]
        resolved_side = None
        if ticker_side[:3] == p1_last3:
            resolved_side = "p1"
        elif ticker_side[:3] == p2_last3:
            resolved_side = "p2"
        else:
            p1_full = p1_name.split()[-1].upper()
            p2_full = p2_name.split()[-1].upper()
            if ticker_side in p1_full or p1_full.startswith(ticker_side):
                resolved_side = "p1"
            elif ticker_side in p2_full or p2_full.startswith(ticker_side):
                resolved_side = "p2"
        if resolved_side is None:
            return None
        result = get_consensus_fv(event_ticker, resolved_side)
        if result:
            result["_side"] = resolved_side
        return result

    async def check_fills(self):
        """Poll Kalshi for fill status on all active orders."""
        for tk, pos in list(self.positions.items()):
            if pos.settled:
                continue

            # V4.2 migration: backfill match_start_ts from schedule
            if pos.match_start_ts == 0 and pos.event_ticker:
                st = self.event_start_time.get(pos.event_ticker, 0)
                if st > 0:
                    pos.match_start_ts = st

            # Check entry order fill
            if pos.phase == "entry_resting" and pos.entry_order_id:
                now = time.time()
                if pos.match_start_ts > 0 and now > pos.match_start_ts - ENTRY_BUFFER_SEC:
                    await self.cancel_order(tk, pos.entry_order_id, "match_start_buffer")
                    self._log("entry_cancelled", {
                        "reason": "match_start_buffer",
                        "match_start": pos.match_start_ts,
                        "waited_min": round((now - pos.entry_posted_ts) / 60),
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    continue

                path = "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data:
                    continue
                order = data.get("order", data)
                status = order.get("status", "")
                filled = int(order.get("count_filled_fp", order.get("count_filled", 0)) or 0)

                if filled > 0 and filled > pos.entry_qty:
                    new_fills = filled - pos.entry_qty
                    fill_price_raw = order.get("average_fill_price_fp",
                                               order.get("yes_price", pos.entry_price / 100.0))
                    if isinstance(fill_price_raw, str):
                        fill_price_raw = float(fill_price_raw)
                    fill_price = round(fill_price_raw * 100) if fill_price_raw < 1.5 else int(fill_price_raw)
                    if fill_price <= 0:
                        fill_price = pos.entry_price

                    first_fill = pos.entry_qty == 0
                    pos.entry_qty = filled
                    pos.entry_filled_ts = time.time()
                    pos.phase = "active"
                    if first_fill:
                        self.n_entries += 1

                    self._log("entry_filled", {
                        "fill_price": fill_price,
                        "posted_price": pos.entry_price,
                        "qty": filled,
                        "new_fills": new_fills,
                        "cell": pos.cell_name,
                        "direction": pos.direction,
                        "play_type": pos.play_type,
                        "kalshi_status": status,
                    }, ticker=tk)

                    # Cancel ALL existing exit sells before posting new ones
                    if pos.exit_order_id:
                        await self.cancel_order(tk, pos.exit_order_id, "exit_consolidate")
                    if pos.cell_exit_order_id:
                        await self.cancel_order(tk, pos.cell_exit_order_id, "exit_consolidate_cell")
                    existing_orders = await api_get(self.session, self.ak, self.pk,
                        "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                    if existing_orders:
                        for old_sell in existing_orders.get("orders", []):
                            if old_sell.get("action") == "sell":
                                old_oid = old_sell.get("order_id", "")
                                if old_oid and old_oid not in (pos.exit_order_id, pos.cell_exit_order_id):
                                    await self.cancel_order(tk, old_oid, "exit_consolidate_extra")

                    if pos.play_type == "B_convergence" and pos.layered_exit_price > 0:
                        # Play 4: layered exits — 9ct at convergence, rest at cell scalp
                        conv_exit_price = pos.layered_exit_price
                        cell_exit_price = min(fill_price + pos.cell_cfg["exit_cents"], EXIT_PRICE_CAP)

                        conv_qty = min(9, filled)
                        cell_qty = filled - conv_qty

                        if conv_qty > 0:
                            oid_conv, _ = await self.place_order(tk, "sell", "yes", conv_exit_price, conv_qty)
                            pos.exit_order_id = oid_conv
                            pos.exit_price = conv_exit_price
                            self._log("exit_posted_convergence", {
                                "exit_price": conv_exit_price, "qty": conv_qty,
                                "order_id": oid_conv,
                            }, ticker=tk)

                        if cell_qty > 0:
                            oid_cell, _ = await self.place_order(tk, "sell", "yes", cell_exit_price, cell_qty)
                            pos.cell_exit_order_id = oid_cell
                            pos.cell_exit_price = cell_exit_price
                            self._log("exit_posted_cell_scalp", {
                                "exit_price": cell_exit_price, "qty": cell_qty,
                                "order_id": oid_cell,
                            }, ticker=tk)

                    else:
                        # Play 3 / Play 1: standard single exit
                        exit_price = min(fill_price + pos.cell_cfg["exit_cents"], EXIT_PRICE_CAP)
                        pos.exit_price = exit_price

                        sell_qty = filled
                        oid, resp = await self.place_order(tk, "sell", "yes", exit_price, sell_qty)
                        if not oid:
                            self._log("exit_retry", {"reason": "first attempt failed"}, ticker=tk)
                            await asyncio.sleep(1)
                            oid, resp = await self.place_order(tk, "sell", "yes", exit_price, sell_qty)
                        if not oid:
                            self._log("exit_fatal", {
                                "error": "exit sell failed after retry",
                                "exit_price": exit_price, "qty": sell_qty,
                            }, ticker=tk)
                        pos.exit_order_id = oid
                        self._log("exit_posted", {
                            "exit_price": exit_price,
                            "qty": sell_qty, "total_position": filled,
                            "based_on_fill": fill_price,
                            "play_type": pos.play_type,
                            "order_id": oid,
                            "consolidated": True,
                        }, ticker=tk)

                    # Place DCA if applicable (only on first fill, guard against double-post)
                    if first_fill and not pos.dca_order_id and pos.cell_cfg.get("strategy") == "DCA-A":
                        dca_trigger = pos.cell_cfg.get("dca_trigger_cents", 0)
                        dca_price = fill_price - dca_trigger
                        if dca_price >= self.dca_fill_floor:
                            pos.dca_price = dca_price
                            # FIX 2: DCA qty = min(5, filled_qty)
                            dca_qty = min(self.dca_size, filled)
                            dca_oid, dresp = await self.place_order(tk, "buy", "yes", dca_price, dca_qty)
                            if not dca_oid:
                                self._log("dca_retry", {"reason": "first attempt failed"}, ticker=tk)
                                await asyncio.sleep(1)
                                dca_oid, dresp = await self.place_order(tk, "buy", "yes", dca_price, dca_qty)
                            if not dca_oid:
                                self._log("dca_fatal", {
                                    "error": "DCA buy failed after retry",
                                    "dca_price": dca_price, "qty": dca_qty,
                                }, ticker=tk)
                            pos.dca_order_id = dca_oid
                            self._log("dca_posted", {
                                "dca_price": dca_price,
                                "qty": dca_qty, "position_qty": filled,
                                "trigger_cents": dca_trigger,
                                "based_on_fill": fill_price,
                                "order_id": dca_oid,
                            }, ticker=tk)
                        else:
                            self._log("dca_skipped", {
                                "reason": "below_floor",
                                "would_be": dca_price,
                                "floor": self.dca_fill_floor,
                            }, ticker=tk)

            # Check exit order fill
            if pos.phase == "active" and pos.exit_order_id and not pos.exit_filled:
                path = "/trade-api/v2/portfolio/orders/%s" % pos.exit_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if data:
                    order = data.get("order", data)
                    filled = int(order.get("count_filled_fp", order.get("count_filled", 0)) or 0)
                    if filled >= pos.entry_qty:
                        pos.exit_filled = True
                        pos.settled = True
                        pos.phase = "settled"
                        self.n_exits += 1
                        pnl = (pos.exit_price - pos.entry_price) * pos.entry_qty
                        if pos.dca_qty > 0:
                            pnl += (pos.exit_price - pos.dca_price) * pos.dca_qty
                        pos.pnl_cents = pnl
                        self._log("exit_filled", {
                            "exit_price": pos.exit_price,
                            "entry_price": pos.entry_price,
                            "pnl_cents": pnl,
                            "pnl_dollars": pnl / 100.0,
                            "had_dca": pos.dca_qty > 0,
                        }, ticker=tk)
                        # Classify: scalp (pregame exit) vs settlement-adjacent
                        if pos.match_start_ts > 0 and time.time() < pos.match_start_ts:
                            hrs_before = (pos.match_start_ts - time.time()) / 3600
                            self._log("scalp_filled", {
                                "entry_price": pos.entry_price,
                                "exit_price": pos.exit_price,
                                "profit_cents": pos.exit_price - pos.entry_price,
                                "hours_before_commence": round(hrs_before, 2),
                                "play_type": pos.play_type,
                            }, ticker=tk)
                        # FIX 3: Cancel ALL resting buys on this ticker (DCA + any extras)
                        cleanup = await api_get(self.session, self.ak, self.pk,
                            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                        for co in (cleanup or {}).get("orders", []):
                            if co.get("action") == "buy":
                                await self.cancel_order(tk, co.get("order_id", ""), "exit_cleanup_dca")

            # Check DCA order fill
            if pos.phase == "active" and pos.dca_order_id and not pos.dca_filled and not pos.exit_filled:
                path = "/trade-api/v2/portfolio/orders/%s" % pos.dca_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if data:
                    order = data.get("order", data)
                    filled = int(order.get("count_filled_fp", order.get("count_filled", 0)) or 0)
                    if filled > 0 and not pos.dca_filled:
                        pos.dca_filled = True
                        pos.dca_qty = filled
                        self.n_dcas += 1
                        self._log("dca_filled", {
                            "dca_price": pos.dca_price,
                            "qty": filled,
                            "entry_price": pos.entry_price,
                            "exit_stays_at": pos.exit_price,
                        }, ticker=tk)

    # ------------------------------------------------------------------
    # Detect settlement via BBO
    # ------------------------------------------------------------------
    def check_settlements(self):
        for tk, pos in list(self.positions.items()):
            if pos.settled or pos.phase != "active":
                continue
            book = self.books.get(tk)
            if not book:
                continue
            if book.best_bid >= 98 or book.best_ask <= 2:
                settle_val = 99 if book.best_bid >= 98 else 1
                label = "WIN" if settle_val == 99 else "LOSS"
                pnl = (settle_val - pos.entry_price) * pos.entry_qty
                if pos.dca_qty > 0:
                    pnl += (settle_val - pos.dca_price) * pos.dca_qty
                pos.pnl_cents = pnl
                pos.settled = True
                pos.phase = "settled"
                self.n_settlements += 1
                self._log("settled", {
                    "settle": label, "settle_price": settle_val,
                    "pnl_cents": pnl, "pnl_dollars": pnl / 100.0,
                    "entry_price": pos.entry_price,
                }, ticker=tk)

    # ------------------------------------------------------------------
    # Routing: SCHEDULE-BASED entry trigger + cell assignment at post time
    # ------------------------------------------------------------------
    def get_market_price(self, ticker, max_last_trade_age_sec=1800):
        book = self.books.get(ticker)
        if not book:
            return None, 'none'
        now = time.time()
        mid = (book.best_bid + book.best_ask) / 2.0 if book.best_bid > 0 and book.best_ask < 100 else 0
        if book.last_trade_price > 0 and book.last_trade_ts > 0:
            age = now - book.last_trade_ts
            if age < max_last_trade_age_sec:
                if mid > 0 and abs(book.last_trade_price - mid) > 2:
                    self._log('price_signal', {
                        'source': 'last_traded', 'price': book.last_trade_price,
                        'mid': round(mid, 1), 'last_traded_age_sec': round(age),
                        'divergence_cents': round(abs(book.last_trade_price - mid), 1),
                    }, ticker=ticker)
                return book.last_trade_price, 'last_traded'
            else:
                if mid > 0:
                    self._log('price_signal', {
                        'source': 'mid_fallback', 'reason': 'last_traded_stale',
                        'stale_price': book.last_trade_price,
                        'stale_age_sec': round(age), 'mid': round(mid, 1),
                    }, ticker=ticker)
        if mid > 0:
            return mid, 'mid'
        return None, 'none'

    async def routing_tick(self):
        """Enter any time from discovery up to 15 min before scheduled start.
        Once inside the 15-min buffer or past start: permanent skip.
        One attempt per event, never retry."""
        now = time.time()

        for et, tickers in self.event_tickers.items():
            if et in self.processed_events:
                continue

            start_ts = self.event_start_time.get(et)

            # No schedule match yet — check unmatched skip logic
            if start_ts is None:
                cycles = self.event_unmatched_cycles.get(et, 0)
                open_ts = self.event_open_time.get(et, now)
                open_age = now - open_ts
                if cycles >= UNMATCHED_SKIP_CYCLES and open_age > UNMATCHED_SKIP_AGE:
                    self._log("skipped", {
                        "reason": "schedule_gap",
                        "event": et,
                        "unmatched_cycles": cycles,
                        "open_age_sec": round(open_age),
                    })
                continue

            time_to_start = start_ts - now

            # More than 24h away — wait, revisit later (outer bound before intelligence runs)
            if time_to_start > 86400:
                continue

            # Past commence — match already started per our data
            if time_to_start <= 0:
                self.processed_events.add(et)
                self._save_processed()
                self._log("skipped", {
                    "reason": "match_already_started",
                    "event": et,
                    "time_to_start_sec": round(time_to_start),
                    "start_time": datetime.fromtimestamp(start_ts, tz=ET).strftime("%b %d %I:%M %p ET"),
                })
                continue

            # Inside 15-min buffer — too close to start
            if time_to_start <= ENTRY_BUFFER_SEC:
                self.processed_events.add(et)
                self._save_processed()
                self._log("skipped", {
                    "reason": "inside_buffer",
                    "event": et,
                    "time_to_start_sec": round(time_to_start),
                    "start_time": datetime.fromtimestamp(start_ts, tz=ET).strftime("%b %d %I:%M %p ET"),
                })
                continue

            # ENTER: start_ts - 14400 < now < start_ts - 900 (4h to 15min before start)
            tk_list = list(tickers)
            if len(tk_list) < 2:
                continue
            all_have_bbo = all(
                tk in self.books and self.books[tk].updated > now - 120
                for tk in tk_list
            )
            if not all_have_bbo:
                continue  # wait for BBO, will retry next tick (still within window)

            self.n_matches_seen += 1

            sides = self.identify_sides(et)
            if not sides:
                self.n_skips += 1
                self._log("skipped", {"reason": "no_valid_sides", "event": et})
                continue

            for (tk, direction, cat) in sides:
                if tk in self.positions:
                    continue
                if tk in self.inflight_orders:
                    continue
                # Claim pending entry to prevent race with check_pending_entries
                if tk in self.pending_entries:
                    del self.pending_entries[tk]

                book = self.books.get(tk)
                if not book or book.updated < now - 120:
                    continue
                current_price, price_source = self.get_market_price(tk)
                if current_price is None:
                    continue

                # ── Intelligence gate ──
                intel_rec = None
                intel_anchor_mode = "fv"
                intel_size = self.config["sizing"]["entry_contracts"]  # default 10
                intel_window = ENTRY_MAX_LEAD_SEC  # fallback 4h

                if INTELLIGENCE_AVAILABLE:
                    try:
                        intel_rec = recommended_window_seconds(et, tk)
                        intel_window = intel_rec["window_seconds"]
                        intel_anchor_mode = intel_rec.get("anchor_mode", "fv")
                        intel_size = intel_rec["recommended_size"]
                    except Exception as e:
                        self._log("intelligence_error", {"error": str(e)[:200]}, ticker=tk)

                if intel_window == 0:
                    self.n_skips += 1
                    self._log("skipped", {
                        "reason": "intelligence_skip",
                        "event": et,
                        "rationale": intel_rec["rationale"] if intel_rec else "module_error",
                        "confidence_score": intel_rec.get("confidence_score") if intel_rec else None,
                    }, ticker=tk)
                    continue

                if time_to_start > intel_window:
                    continue  # outside tier window — revisit next tick

                # ── Anchor resolution: FV-anchored vs Kalshi-anchored ──
                anchor_source = "fv_consensus"
                fv_cents = None
                fv_source = None
                fv_tier = None
                stability = {"range_pct": 0, "samples": 0}

                if intel_anchor_mode == "kalshi" and intel_rec and intel_rec.get("anchor_source") == "kalshi_price":
                    # Kalshi-anchored path: use Kalshi price median as anchor
                    try:
                        kpa = kalshi_price_anchor(et, tk, hours=1)
                    except Exception:
                        kpa = {}
                    if kpa.get("median_price_cents") and kpa["median_price_cents"] > 0:
                        fv_cents = kpa["median_price_cents"]
                        fv_source = "kalshi_anchor"
                        fv_tier = 9  # synthetic tier for Kalshi-anchored
                        anchor_source = "kalshi_price"
                    else:
                        self.n_skips += 1
                        self._log("skipped", {
                            "reason": "kalshi_anchor_no_data", "event": et,
                        }, ticker=tk)
                        continue
                else:
                    # FV-anchored path: existing logic
                    side_fv = self._get_side_fv(tk, et)
                    if side_fv is None or side_fv.get("fv_cents") is None:
                        self.n_skips += 1
                        fv_reason = side_fv.get("reason", "no_data") if side_fv else "no_data"
                        skip_info = {"reason": "fv_stale" if fv_reason == "stale" else "no_fv_available", "event": et}
                        if fv_reason == "stale":
                            skip_info["stale_source"] = side_fv.get("source")
                            skip_info["age_sec"] = side_fv.get("age_sec")
                        self._log("skipped", skip_info, ticker=tk)
                        continue

                    fv_cents = side_fv["fv_cents"]
                    fv_source = side_fv["source"]
                    fv_tier = side_fv["tier"]

                    # FV stability check — only skip on extreme volatility (>20% range)
                    stability = check_fv_stability(et, side_fv.get("_side", "p1"))
                    if stability["range_pct"] > 20:
                        self.n_skips += 1
                        self._log("skipped", {
                            "reason": "fv_unstable",
                            "event": et, "fv_now": stability["fv_now"],
                            "fv_oldest": stability["fv_oldest"],
                            "range_c": stability["range_c"],
                            "range_pct": stability["range_pct"],
                            "samples": stability["samples"],
                        }, ticker=tk)
                        continue

                kalshi_cell, _ = self.cell_lookup(cat, direction, current_price)
                fv_cell, fv_cell_cfg = self.cell_lookup(cat, direction, fv_cents)
                gap_cents = current_price - fv_cents
                cell_low = int(fv_cents / 5) * 5
                cell_high = cell_low + 4

                # FV cell must have active config
                if fv_cell_cfg is None or fv_cell in self.config.get("disabled_cells", []):
                    self.n_skips += 1
                    self._log("skipped", {
                        "reason": "fv_cell_not_active",
                        "fv_cell": fv_cell, "fv_cents": round(fv_cents, 1), "event": et,
                        "anchor_source": anchor_source,
                    }, ticker=tk)
                    continue

                # Determine play — exhaustive, no fall-through
                play_type = None
                entry_price = None
                entry_size = None
                layered_exit_price = 0

                if kalshi_cell == fv_cell:
                    play_type = "A_tight"
                    entry_price = max(cell_low, int(current_price) - 1)
                    entry_size = intel_size
                elif current_price < fv_cents:
                    play_type = "B_convergence"
                    entry_price = int(current_price) + 1
                    entry_size = intel_size
                    layered_exit_price = int(fv_cents) - 2
                else:
                    play_type = "A_patient"
                    entry_price = cell_high
                    entry_size = intel_size

                # Dead-spread guard
                spread = book.best_ask - book.best_bid
                if spread > DEAD_SPREAD_THRESHOLD:
                    if tk not in self.pending_entries:
                        self.pending_entries[tk] = {
                            "event": et, "direction": direction, "cat": cat,
                            "cell_name": fv_cell, "cell_cfg": fv_cell_cfg,
                            "discovered_ts": now,
                            "play_type": play_type,
                            "entry_size": entry_size,
                            "layered_exit_price": layered_exit_price,
                            "anchor_source": anchor_source,
                        }
                        self._log("entry_deferred", {
                            "reason": "dead_spread", "spread": spread,
                            "bid": book.best_bid, "ask": book.best_ask,
                            "cell": fv_cell, "play": play_type,
                        }, ticker=tk)
                    continue

                # Pre-post guard: check for existing resting orders or position
                existing = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                if existing and existing.get("orders"):
                    self._log("skipped", {
                        "reason": "resting_order_exists",
                        "ticker": tk, "existing_count": len(existing["orders"]),
                    }, ticker=tk)
                    continue
                existing_pos = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&settlement_status=unsettled" % tk, self.rl)
                if existing_pos:
                    pos_list = existing_pos.get("market_positions", [])
                    if any(int(float(p.get("position_fp", 0))) > 0 for p in pos_list):
                        self._log("skipped", {"reason": "position_exists", "ticker": tk}, ticker=tk)
                        continue

                self._log("cell_match", {
                    "event": et, "direction": direction, "cell": fv_cell,
                    "play_type": play_type,
                    "fv_cents": round(fv_cents, 1), "fv_source": fv_source, "fv_tier": fv_tier,
                    "anchor_source": anchor_source,
                    "kalshi_price": current_price,
                    "gap_cents": round(gap_cents, 1),
                    "entry_price": entry_price, "entry_size": entry_size,
                    "layered_exit_price": layered_exit_price,
                    "strategy": fv_cell_cfg["strategy"],
                    "exit_cents": fv_cell_cfg["exit_cents"],
                    "min_before_start": round(time_to_start / 60),
                    "fv_stability_range_pct": stability["range_pct"],
                    "intel_score": intel_rec.get("confidence_score") if intel_rec else None,
                    "intel_grade": intel_rec.get("confidence_grade") if intel_rec else None,
                    "intel_window_sec": intel_window,
                    "intel_anchor": intel_anchor_mode,
                }, ticker=tk)

                self.inflight_orders.add(tk)
                try:
                    oid, resp = await self.place_order(tk, "buy", "yes", entry_price, entry_size)
                finally:
                    self.inflight_orders.discard(tk)

                pos = Position(
                    ticker=tk, event_ticker=et,
                    category=self.ticker_category.get(tk, "?"),
                    direction=direction, cell_name=fv_cell, cell_cfg=fv_cell_cfg,
                    entry_price=entry_price, entry_order_id=oid,
                    entry_posted_ts=now, phase="entry_resting",
                    match_start_ts=start_ts,
                    play_type=play_type,
                    layered_exit_price=layered_exit_price,
                )
                self.positions[tk] = pos

    # ------------------------------------------------------------------
    # Check pending entries: post when spread tightens
    # ------------------------------------------------------------------
    async def check_pending_entries(self):
        now = time.time()
        for tk in list(self.pending_entries.keys()):
            # Race guard: skip if routing_tick already handling or position exists
            if tk in self.positions or tk in self.inflight_orders:
                del self.pending_entries[tk]
                continue

            pe = self.pending_entries[tk]

            # Timeout: 2h with no tight spread → skip permanently
            if now - pe["discovered_ts"] > PENDING_TIMEOUT_SEC:
                del self.pending_entries[tk]
                self._log("pending_timeout", {"ticker": tk, "cell": pe["cell_name"]}, ticker=tk)
                continue

            book = self.books.get(tk)
            if not book or book.updated < now - 120:
                continue

            spread = book.best_ask - book.best_bid
            if spread > DEAD_SPREAD_THRESHOLD:
                continue  # still dead, wait

            current_price, price_source = self.get_market_price(tk)
            if current_price is None:
                continue

            # Re-evaluate play with current FV
            et = pe["event"]
            side_fv = self._get_side_fv(tk, et)
            if side_fv is None or side_fv.get("fv_cents") is None:
                del self.pending_entries[tk]
                self._log("pending_no_fv", {"ticker": tk}, ticker=tk)
                continue

            fv_cents = side_fv["fv_cents"]
            direction = "leader" if current_price > 50 else "underdog"
            kalshi_cell, _ = self.cell_lookup(pe["cat"], direction, current_price)
            fv_cell, fv_cell_cfg = self.cell_lookup(pe["cat"], direction, fv_cents)
            gap = current_price - fv_cents
            cell_low = int(fv_cents / 5) * 5
            cell_high = cell_low + 4

            if fv_cell_cfg is None or fv_cell in self.config.get("disabled_cells", []):
                del self.pending_entries[tk]
                continue

            # Intelligence re-query at resolve time (conditions may have changed)
            pending_intel_size = self.config["sizing"]["entry_contracts"]
            if INTELLIGENCE_AVAILABLE:
                try:
                    p_rec = recommended_window_seconds(et, tk)
                    if p_rec["window_seconds"] == 0:
                        del self.pending_entries[tk]
                        self._log("pending_intel_skip", {
                            "ticker": tk, "rationale": p_rec.get("rationale", ""),
                            "confidence_score": p_rec.get("confidence_score"),
                        }, ticker=tk)
                        continue
                    if p_rec["recommended_size"] > 0:
                        pending_intel_size = p_rec["recommended_size"]
                except Exception:
                    pass

            # Determine play — exhaustive, no fall-through
            play_type = None
            entry_price = None
            entry_size = None
            layered_exit_price = 0

            if kalshi_cell == fv_cell:
                play_type = "A_tight"
                entry_price = max(cell_low, int(current_price) - 1)
                entry_size = pending_intel_size
            elif current_price < fv_cents:
                play_type = "B_convergence"
                entry_price = int(current_price) + 1
                entry_size = pending_intel_size
                layered_exit_price = int(fv_cents) - 2
            else:
                play_type = "A_patient"
                entry_price = cell_high
                entry_size = pending_intel_size

            del self.pending_entries[tk]

            self._log("pending_resolved", {
                "spread": spread, "entry_price": entry_price, "cell": fv_cell,
                "play_type": play_type,
                "fv_cents": round(fv_cents, 1), "gap": round(gap, 1),
                "waited_sec": round(now - pe["discovered_ts"]),
            }, ticker=tk)

            self.inflight_orders.add(tk)
            try:
                oid, resp = await self.place_order(tk, "buy", "yes", entry_price, entry_size)
            finally:
                self.inflight_orders.discard(tk)
            pos = Position(
                ticker=tk, event_ticker=et,
                category=self.ticker_category.get(tk, "?"),
                direction=direction, cell_name=fv_cell, cell_cfg=fv_cell_cfg,
                entry_price=entry_price, entry_order_id=oid,
                entry_posted_ts=now, phase="entry_resting",
                match_start_ts=self.event_start_time.get(et, 0),
                play_type=play_type,
                layered_exit_price=layered_exit_price,
            )
            self.positions[tk] = pos

    # ------------------------------------------------------------------
    # Validate resting buys: cancel stale orders
    # ------------------------------------------------------------------
    async def validate_resting_buys(self):
        now = time.time()
        for tk, pos in list(self.positions.items()):
            if pos.phase != "entry_resting" or not pos.entry_order_id:
                continue

            book = self.books.get(tk)
            if not book or book.updated < now - 120:
                continue

            current_price, price_source = self.get_market_price(tk)
            if current_price is None:
                continue

            # Legacy positions skip new-rule validation
            if pos.legacy:
                continue

            # FV-aware validation per play type
            side_fv = self._get_side_fv(tk, pos.event_ticker)
            if side_fv is None or side_fv.get("fv_cents") is None:
                await self.cancel_order(tk, pos.entry_order_id, "fv_disappeared")
                self._log("stale_buy_cancel", {"reason": "fv_disappeared"}, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            fv_cents = side_fv["fv_cents"]
            cat = self.get_category(tk)
            if not cat:
                continue

            direction = "leader" if current_price > 50 else "underdog"
            kalshi_cell, _ = self.cell_lookup(cat, direction, current_price)
            fv_cell, _ = self.cell_lookup(cat, direction, fv_cents)
            gap = current_price - fv_cents
            cell_low = int(fv_cents / 5) * 5

            play = pos.play_type

            if play == "A_tight":
                # Cancel if Kalshi drifted out of FV cell
                if kalshi_cell != fv_cell:
                    await self.cancel_order(tk, pos.entry_order_id, "A_tight_cell_drift")
                    self._log("stale_buy_cancel", {
                        "reason": "A_tight_cell_drift",
                        "kalshi_cell": kalshi_cell, "fv_cell": fv_cell, "gap": round(gap, 1),
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    continue

                # Asymmetric tape follow: reprice down if tape dropped
                target = max(cell_low, int(current_price) - 1)
                if target < pos.entry_price:
                    await self.cancel_order(tk, pos.entry_order_id, "tape_follow_down")
                    oid, _ = await self.place_order(tk, "buy", "yes", target, 10)
                    old = pos.entry_price
                    pos.entry_price = target
                    pos.entry_order_id = oid
                    self._log("reprice_down", {
                        "old_price": old, "new_price": target,
                        "kalshi": current_price, "fv": round(fv_cents, 1), "play": "A_tight",
                    }, ticker=tk)

            elif play == "B_convergence":
                # Cancel if Kalshi converged into FV cell (opportunity gone)
                if kalshi_cell == fv_cell:
                    await self.cancel_order(tk, pos.entry_order_id, "B_convergence_gap_closed")
                    self._log("stale_buy_cancel", {
                        "reason": "B_convergence_gap_closed",
                        "kalshi_cell": kalshi_cell, "fv_cell": fv_cell, "gap": round(gap, 1),
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    continue

                # Cancel if tape crossed above FV (overshoot — thesis invalid)
                if current_price >= fv_cents:
                    await self.cancel_order(tk, pos.entry_order_id, "B_convergence_overshot")
                    self._log("stale_buy_cancel", {
                        "reason": "B_convergence_overshot",
                        "kalshi": current_price, "fv": round(fv_cents, 1),
                        "original_entry": pos.entry_price,
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    continue

                # Tape follow: update entry to tape + 1c (only if still below FV)
                target = int(current_price) + 1
                if target >= int(fv_cents):
                    await self.cancel_order(tk, pos.entry_order_id, "B_convergence_would_overshoot")
                    self._log("stale_buy_cancel", {
                        "reason": "B_convergence_would_overshoot",
                        "target": target, "fv": round(fv_cents, 1),
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    continue

                if target != pos.entry_price:
                    repost_size = pos.entry_qty if pos.entry_qty > 0 else 19
                    await self.cancel_order(tk, pos.entry_order_id, "B_tape_update")
                    self.inflight_orders.add(tk)
                    try:
                        oid, _ = await self.place_order(tk, "buy", "yes", target, repost_size)
                    finally:
                        self.inflight_orders.discard(tk)
                    old = pos.entry_price
                    pos.entry_price = target
                    pos.entry_order_id = oid
                    self._log("reprice_b_tape", {
                        "old_price": old, "new_price": target,
                        "kalshi": current_price, "fv": round(fv_cents, 1),
                        "size": repost_size,
                    }, ticker=tk)

            elif play == "A_patient":
                # Kalshi drifted INTO FV cell — leave rest, may fill
                if kalshi_cell == fv_cell:
                    continue
                # Kalshi dropped below FV — no longer premium, cancel
                if current_price < fv_cents:
                    await self.cancel_order(tk, pos.entry_order_id, "A_patient_conditions_changed")
                    self._log("stale_buy_cancel", {
                        "reason": "A_patient_now_discount",
                        "kalshi": current_price, "fv": round(fv_cents, 1), "gap": round(gap, 1),
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)
                    continue

            else:
                # Legacy positions: fall back to original stale check
                delta = pos.entry_price - current_price
                if delta > STALE_BUY_DELTA:
                    await self.cancel_order(tk, pos.entry_order_id, "stale_above_fv")
                    self._log("stale_buy_cancel", {
                        "reason": "above_fair_value_legacy", "our_price": pos.entry_price,
                        "current_mid": current_price, "delta": round(delta),
                    }, ticker=tk)
                    self._untombstone_entry(tk, pos)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    def print_summary(self):
        elapsed_hr = (time.time() - self.start_ts) / 3600
        settled = [p for p in self.positions.values() if p.settled]
        total_pnl = sum(p.pnl_cents for p in settled)
        active = [p for p in self.positions.values() if not p.settled]

        print("\n" + "=" * 70, flush=True)
        print("LIVE V3 SUMMARY  (%.1f hours)" % elapsed_hr, flush=True)
        print("=" * 70, flush=True)
        print("  Matches seen:     %d" % self.n_matches_seen, flush=True)
        print("  Entries posted:   %d" % len(self.positions), flush=True)
        print("  Entries filled:   %d" % self.n_entries, flush=True)
        print("  Exits filled:     %d" % self.n_exits, flush=True)
        print("  DCAs filled:      %d" % self.n_dcas, flush=True)
        print("  Settlements:      %d" % self.n_settlements, flush=True)
        print("  Active positions: %d" % len(active), flush=True)
        print("  Total P&L:        %.1fc = $%.2f" % (total_pnl, total_pnl / 100.0), flush=True)
        print("  Skipped:          %d" % self.n_skips, flush=True)

        cell_pnl = defaultdict(lambda: {"n": 0, "pnl": 0})
        for p in settled:
            c = cell_pnl[p.cell_name]
            c["n"] += 1
            c["pnl"] += p.pnl_cents
        if cell_pnl:
            print("\n  Per-cell:", flush=True)
            for cell in sorted(cell_pnl.keys()):
                c = cell_pnl[cell]
                print("    %-35s N=%d  P&L=%.1fc" % (cell, c["n"], c["pnl"]), flush=True)

        if active:
            print("\n  Active:", flush=True)
            for p in active:
                book = self.books.get(p.ticker)
                cur_mid = (book.best_bid + book.best_ask) / 2.0 if book else 0
                print("    %-40s entry=%dc exit=%dc mid=%.0fc %s" % (
                    p.ticker[:40], p.entry_price, p.exit_price, cur_mid, p.phase), flush=True)
        print("=" * 70, flush=True)
        self._log("summary", {
            "elapsed_hr": round(elapsed_hr, 1),
            "matches_seen": self.n_matches_seen, "entries": self.n_entries,
            "exits": self.n_exits, "dcas": self.n_dcas,
            "settlements": self.n_settlements, "active": len(active),
            "total_pnl_cents": total_pnl, "skips": self.n_skips,
        })

    # ------------------------------------------------------------------
    # Startup reconciliation: sync in-memory state with Kalshi account
    # ------------------------------------------------------------------
    async def reconcile(self, quiet=False):
        """Load existing positions and resting orders from Kalshi.
        Populate in-memory state so the bot doesn't re-enter or orphan orders.
        quiet=True suppresses the full report (for periodic 60s runs)."""
        if not quiet:
            print("\n[RECONCILE] Loading account state from Kalshi...", flush=True)

        # 1. Fetch positions
        pos_path = "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled"
        pos_data = await api_get(self.session, self.ak, self.pk, pos_path, self.rl)
        positions = (pos_data or {}).get("market_positions", [])

        pos_map = {}  # ticker -> {qty, avg_price, event_ticker}
        for p in positions:
            tk = p.get("ticker", "")
            qty = int(float(p.get("position_fp", 0)))
            total = float(p.get("market_exposure_dollars", p.get("total_traded_dollars", 0))) * 100  # cents
            avg_price = int(total / qty) if qty > 0 else 0
            et = self.ticker_to_event.get(tk, "")
            if not et:
                parts = tk.rsplit("-", 1)
                et = parts[0] if len(parts) == 2 else ""
            pos_map[tk] = {"qty": qty, "avg_price": avg_price, "event_ticker": et}

        # 2. Fetch resting orders
        ord_path = "/trade-api/v2/portfolio/orders?status=resting"
        ord_data = await api_get(self.session, self.ak, self.pk, ord_path, self.rl)
        resting = (ord_data or {}).get("orders", [])

        ord_map = {}  # ticker -> list of orders
        for o in resting:
            tk = o.get("ticker", "")
            price_raw = o.get("yes_price_dollars", o.get("yes_price", "0"))
            price_cents = round(float(price_raw) * 100) if float(price_raw) < 2 else int(price_raw)
            qty_raw = o.get("remaining_count_fp", o.get("remaining_count", o.get("initial_count_fp", 0)))
            entry = {
                "order_id": o.get("order_id", ""),
                "action": o.get("action", ""),
                "side": o.get("side", ""),
                "price": price_cents,
                "qty": int(float(qty_raw or 0)),
            }
            ord_map.setdefault(tk, []).append(entry)

        # 3. Link positions to exits and populate bot state
        linked = []
        unmanaged = []
        reconcile_exits = []
        orphan_orders = []

        for tk, pinfo in pos_map.items():
            et = pinfo["event_ticker"]
            sells = [o for o in ord_map.get(tk, []) if o["action"] == "sell"]


            if sells:
                sell = sells[0]
                total_sell_qty = sum(s["qty"] for s in sells)
                cat = self.get_category(tk) or "?"
                pos = Position(
                    ticker=tk, event_ticker=et, category=cat,
                    direction="reconciled", cell_name="reconciled",
                    cell_cfg={}, entry_price=pinfo["avg_price"],
                    entry_qty=pinfo["qty"], phase="active",
                    exit_price=sell["price"], exit_order_id=sell["order_id"],
                    entry_filled_ts=time.time(),
                    legacy=True, play_type="A_legacy",
                )
                self.positions[tk] = pos
                linked.append((tk, pinfo, sell))
                # Check qty gap — position may have more contracts than sell covers
                naked_qty = pinfo["qty"] - total_sell_qty
                if naked_qty > 0:
                    exit_price = sell["price"]  # same price as existing sell
                    fresh = await api_get(self.session, self.ak, self.pk,
                        "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                    fresh_sell_qty = sum(int(float(o.get("remaining_count_fp", 0) or 0))
                        for o in (fresh or {}).get("orders", []) if o.get("action") == "sell")
                    actual_naked = pinfo["qty"] - fresh_sell_qty
                    if actual_naked > 0:
                        # Cancel existing sells and repost consolidated
                        for old_sell in (fresh or {}).get("orders", []):
                            if old_sell.get("action") == "sell":
                                await self.cancel_order(tk, old_sell.get("order_id", ""), "reconcile_consolidate")
                        oid, resp = await self.place_order(tk, "sell", "yes", exit_price, pinfo["qty"])
                        reconcile_exits.append((tk, pinfo, exit_price, "qty_gap_consolidated", oid))
                        self._log("reconcile_exit_posted", {
                            "reason": "qty_gap_consolidated", "exit_price": exit_price,
                            "position_qty": pinfo["qty"],
                            "order_id": oid,
                        }, ticker=tk)
                # Check DCA coverage for DCA-A cells
                avg = pinfo["avg_price"]
                direction = "leader" if avg > 50 else "underdog"
                if cat and cat != "?":
                    dca_cell_name, dca_cell_cfg = self.cell_lookup(cat, direction, avg)
                    if dca_cell_cfg and dca_cell_cfg.get("strategy") == "DCA-A":
                        dca_trigger = dca_cell_cfg.get("dca_trigger_cents", 0)
                        dca_price = avg - dca_trigger
                        if dca_price >= self.dca_fill_floor:
                            # FIX 1: strict any-resting-buy guard (no price proximity check)
                            fresh_buys = await api_get(self.session, self.ak, self.pk,
                                "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                            any_resting_buy = any(o.get("action") == "buy"
                                for o in (fresh_buys or {}).get("orders", []))
                            if not any_resting_buy:
                                # FIX 2: DCA qty = min(5, position_qty)
                                dca_qty = min(self.dca_size, pinfo["qty"])
                                dca_oid, _ = await self.place_order(tk, "buy", "yes", dca_price, dca_qty)
                                reconcile_exits.append((tk, pinfo, dca_price, "dca_missing", dca_oid))
                                self._log("reconcile_dca_posted", {
                                    "dca_price": dca_price, "qty": dca_qty,
                                    "position_qty": pinfo["qty"],
                                    "cell": dca_cell_name, "order_id": dca_oid,
                                }, ticker=tk)
            else:
                # No exit sell — try to auto-post one
                cat = self.get_category(tk)
                avg = pinfo["avg_price"]
                direction = "leader" if avg > 50 else "underdog"
                if cat:
                    cell_name, cell_cfg = self.cell_lookup(cat, direction, avg)
                else:
                    cell_name, cell_cfg = None, None

                if cell_cfg:
                    exit_price = min(avg + cell_cfg["exit_cents"], EXIT_PRICE_CAP)
                    # Fresh Kalshi check: verify no resting sell already exists
                    fresh = await api_get(self.session, self.ak, self.pk,
                        "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                    fresh_sells = [o for o in (fresh or {}).get("orders", []) if o.get("action") == "sell"]
                    if fresh_sells:
                        sell = {"order_id": fresh_sells[0].get("order_id", ""),
                                "price": round(float(fresh_sells[0].get("yes_price_dollars", "0")) * 100)}
                        pos = Position(
                            ticker=tk, event_ticker=et, category=cat or "?",
                            direction=direction, cell_name=cell_name, cell_cfg=cell_cfg,
                            entry_price=avg, entry_qty=pinfo["qty"], phase="active",
                            exit_price=sell["price"], exit_order_id=sell["order_id"],
                            entry_filled_ts=time.time(),
                            legacy=True, play_type="A_legacy",
                        )
                        self.positions[tk] = pos
                        linked.append((tk, pinfo, sell))
                        self._log("reconcile_exit_found_fresh", {
                            "ticker": tk, "exit_price": sell["price"],
                        }, ticker=tk)
                    else:
                        oid, resp = await self.place_order(tk, "sell", "yes", exit_price, pinfo["qty"])
                        pos = Position(
                            ticker=tk, event_ticker=et, category=cat or "?",
                            direction=direction, cell_name=cell_name, cell_cfg=cell_cfg,
                            entry_price=avg, entry_qty=pinfo["qty"], phase="active",
                            exit_price=exit_price, exit_order_id=oid,
                            entry_filled_ts=time.time(),
                            legacy=True, play_type="A_legacy",
                        )
                        self.positions[tk] = pos
                        reconcile_exits.append((tk, pinfo, exit_price, cell_name, oid))
                        self._log("reconcile_exit_posted", {
                            "exit_price": exit_price, "qty": pinfo["qty"],
                            "avg_price": avg, "cell": cell_name,
                            "exit_cents": cell_cfg["exit_cents"],
                            "order_id": oid,
                        }, ticker=tk)
                else:
                    unmanaged.append((tk, pinfo))
                    reason = "cell disabled" if cell_name and cell_name in self.config["disabled_cells"] else "no cell config"
                    self._log("reconcile_orphan_no_cell", {
                        "ticker": tk, "avg_price": avg, "cell": cell_name or "?",
                        "reason": reason,
                    }, ticker=tk)

        # Check for orphan resting orders (not matched to any position)
        for tk, orders in ord_map.items():
            if tk not in pos_map:
                for o in orders:
                    orphan_orders.append((tk, o))

        self._save_processed()

        # 4. Print reconciliation report
        if not quiet:
            print("\n" + "=" * 70, flush=True)
            print("RECONCILIATION REPORT", flush=True)
            print("=" * 70, flush=True)

            print("\nPositions found: %d" % len(pos_map), flush=True)
            for tk, p in sorted(pos_map.items()):
                print("  %-45s qty=%d  avg=%dc" % (tk[:45], p["qty"], p["avg_price"]), flush=True)

            print("\nResting orders found: %d" % len(resting), flush=True)
            for o in resting:
                pr = o.get("yes_price_dollars", o.get("yes_price", "0"))
                pc = round(float(pr) * 100) if float(pr) < 2 else int(pr)
                qr = o.get("remaining_count_fp", o.get("remaining_count", o.get("initial_count_fp", 0)))
                print("  %-45s %s %s price=%dc qty=%d oid=%s" % (
                    o.get("ticker","")[:45], o.get("action",""), o.get("side",""),
                    pc, int(float(qr or 0)),
                    o.get("order_id","")[:12]), flush=True)

            print("\nLinked (position + exit): %d" % len(linked), flush=True)
            for tk, p, s in linked:
                print("  %-45s qty=%d entry=%dc exit=%dc oid=%s" % (
                    tk[:45], p["qty"], p["avg_price"], s["price"], s["order_id"][:12]), flush=True)

        # Always print reconcile exits (even in quiet mode — these are actions)
        if reconcile_exits:
            print("\n[RECONCILE] Exits auto-posted: %d" % len(reconcile_exits), flush=True)
            for tk, p, ep, cell, oid in reconcile_exits:
                print("  [EXIT_POSTED] %-35s avg=%dc exit=%dc cell=%s oid=%s" % (
                    tk[:35], p["avg_price"], ep, cell, oid[:12]), flush=True)

        if not quiet:
            print("\nUnmanaged (position, NO exit, no cell): %d" % len(unmanaged), flush=True)
            for tk, p in unmanaged:
                print("  [ORPHAN_NO_CELL] %-35s qty=%d avg=%dc" % (tk[:35], p["qty"], p["avg_price"]), flush=True)

            print("\nOrphan orders (no position): %d" % len(orphan_orders), flush=True)
            for tk, o in orphan_orders:
                print("  [ORPHAN] %-39s %s price=%s oid=%s" % (
                    tk[:39], o["action"], o["price"], o["order_id"][:12]), flush=True)

            print("\nProcessed events: %d" % len(self.processed_events), flush=True)
            print("=" * 70, flush=True)

        self._log("reconcile", {
            "positions": len(pos_map),
            "resting_orders": len(resting),
            "linked": len(linked),
            "reconcile_exits_posted": len(reconcile_exits),
            "unmanaged": len(unmanaged),
            "orphans": len(orphan_orders),
            "processed_events": len(self.processed_events),
        })

        return len(pos_map), len(linked), len(unmanaged), len(orphan_orders)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    async def run(self, reconcile_only=False):
        print("=" * 70, flush=True)
        print("LIVE V3 - REAL ORDERS - BABY SIZING 10/5", flush=True)
        print("=" * 70, flush=True)
        print("Config: %s" % CONFIG_PATH, flush=True)
        print("Active cells: %d  Disabled: %d" % (
            len(self.config["active_cells"]), len(self.config["disabled_cells"])), flush=True)
        print("Entry: %d contracts  DCA: %d contracts" % (self.entry_size, self.dca_size), flush=True)
        print("Exit cap: %dc" % EXIT_PRICE_CAP, flush=True)
        print("Log: %s" % self.log_path, flush=True)
        print("=" * 70, flush=True)

        self.session = aiohttp.ClientSession()

        if not await self.ws_connect():
            print("[FATAL] Cannot connect WebSocket", flush=True)
            return

        tickers = await self.discover_markets()
        if tickers:
            await self.ws_subscribe(tickers)

        # Reconcile: load existing positions and resting orders
        await self.reconcile()

        # Startup skip: events inside the 15-min buffer or past start
        now = time.time()
        startup_skipped = 0
        for evt, start_ts in self.event_start_time.items():
            if evt not in self.processed_events and (start_ts - now) <= ENTRY_BUFFER_SEC:
                self.processed_events.add(evt)
                startup_skipped += 1

        # Expire old tombstones: remove events with dates >24h in the past
        import re as _tomb_re
        _month_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                      "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
        expired = set()
        for evt in list(self.processed_events):
            m = _tomb_re.search(r"-(\d{2})([A-Z]{3})(\d{2})", evt)
            if not m:
                continue
            try:
                evt_date = datetime(2000 + int(m.group(1)), _month_map[m.group(2)], int(m.group(3)),
                                    tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - evt_date).total_seconds() > 86400:
                    expired.add(evt)
            except Exception:
                pass
        if expired:
            self.processed_events -= expired
            startup_skipped -= len(expired)  # net out

        if startup_skipped > 0:
            self._save_processed()

        # Startup validation
        now_et = datetime.fromtimestamp(now, tz=ET)
        print("\n[TIME] %s" % now_et.strftime("%Y-%m-%d %I:%M:%S %p ET"), flush=True)

        total_events = len(self.event_tickers)
        matched = len(self.event_start_time)
        unmatched = sum(1 for et in self.event_tickers if et not in self.event_start_time and et not in self.processed_events)
        print("[SCHED] Kalshi events: %d  Schedule-matched: %d  Unmatched: %d  Already-processed: %d" % (
            total_events, matched, unmatched, len(self.processed_events)), flush=True)
        print("[INIT] Skipped %d stale events at startup" % startup_skipped, flush=True)

        # Next 5 matches bot is waiting on
        # Event status report
        all_events_status = []
        for evt in sorted(self.event_tickers.keys()):
            players = ", ".join(self.event_player_names.get(evt, ["?"]))
            if evt in self.processed_events:
                all_events_status.append((evt, "PROCESSED", 0, "", players))
                continue
            start_ts = self.event_start_time.get(evt)
            if start_ts is None:
                all_events_status.append((evt, "UNMATCHED", 0, "", players))
                continue
            time_to_start = start_ts - now
            start_str = datetime.fromtimestamp(start_ts, tz=ET).strftime("%I:%M %p ET")
            cutoff = datetime.fromtimestamp(start_ts - ENTRY_BUFFER_SEC, tz=ET).strftime("%I:%M %p ET")
            if time_to_start > ENTRY_MAX_LEAD_SEC:
                all_events_status.append((evt, "WAIT (>24h)", time_to_start, start_str, players))
            elif time_to_start > ENTRY_BUFFER_SEC:
                all_events_status.append((evt, "ENTER", time_to_start, "eligible until %s, start=%s" % (cutoff, start_str), players))
            else:
                all_events_status.append((evt, "SKIP (buffer)", time_to_start, start_str, players))

        print("\n[EVENTS] All discovered events:", flush=True)
        for evt, status, secs, detail, players in all_events_status:
            if status == "PROCESSED":
                print("  %-40s  PROCESSED  [%s]" % (evt[:40], players[:30]), flush=True)
            elif status == "ENTER":
                print("  %-40s  ENTER  %s  [%s]" % (evt[:40], detail, players[:30]), flush=True)
            elif status == "WAIT (>24h)":
                print("  %-40s  WAIT  >24h to start=%s  [%s]" % (evt[:40], detail, players[:30]), flush=True)
            elif status == "UNMATCHED":
                print("  %-40s  UNMATCHED  no schedule  [%s]" % (evt[:40], players[:30]), flush=True)
            else:
                print("  %-40s  SKIP  %.0f min to start=%s  [%s]" % (evt[:40], secs/60, detail, players[:30]), flush=True)

        eligible = [e for e, st, s, d, p in all_events_status if st == "ENTER"]
        waiting = [(e, s, d) for e, st, s, d, p in all_events_status if st == "WAIT (>24h)"]
        if eligible:
            print("\n[ALERT] %d events ELIGIBLE for immediate entry!" % len(eligible), flush=True)
        if not eligible and not waiting:
            print("\n[NEXT] No upcoming entries — all events processed or unmatched", flush=True)

        # Log FOMSUN schedule match verification (if present)
        for evt in self.event_tickers:
            if "FOMSUN" in evt:
                st = self.event_start_time.get(evt)
                is_processed = evt in self.processed_events
                if st:
                    print("\n[VERIFY] %s schedule matched: start=%s, processed=%s" % (
                        evt, datetime.fromtimestamp(st, tz=ET).strftime("%I:%M %p ET"), is_processed), flush=True)
                else:
                    print("\n[VERIFY] %s schedule: NO MATCH, processed=%s" % (evt, is_processed), flush=True)

        # Unmatched events with recent open_time (coverage gaps)
        recent_unmatched = []
        for evt in self.event_tickers:
            if evt in self.processed_events or evt in self.event_start_time:
                continue
            open_ts = self.event_open_time.get(evt, 0)
            if now - open_ts < 86400:
                recent_unmatched.append((evt, now - open_ts))
        if recent_unmatched:
            print("\n[WARN] Unmatched events with open_time < 24h:", flush=True)
            for evt, age in recent_unmatched:
                players = self.event_player_names.get(evt, ["?"])
                print("  %-40s  open_age=%.0fh  players=%s" % (evt[:40], age/3600, ", ".join(players)), flush=True)

        self._log("startup_validation", {
            "time_et": now_et.strftime("%Y-%m-%d %I:%M:%S %p ET"),
            "total_events": total_events,
            "schedule_matched": matched,
            "unmatched": unmatched,
            "processed": len(self.processed_events),
            "startup_skipped": startup_skipped,
            "waiting": len(waiting),
            "eligible": len(eligible),
        })

        if reconcile_only:
            print("\n[RECONCILE-ONLY] Exiting after validation.", flush=True)
            await self.session.close()
            self.log_file.close()
            return

        asyncio.create_task(self.ws_reader())

        print("\n[INIT] Waiting 10s for BBO snapshots...", flush=True)
        await asyncio.sleep(10)

        last_discovery = time.time()
        last_fill_check = 0  # force immediate first check_fills
        last_reconcile = time.time()
        last_stale_check = time.time()
        last_summary = time.time()

        print("[RUNNING] Main loop started.", flush=True)

        while True:
            try:
                now = time.time()

                # Check settlements via BBO
                self.check_settlements()

                # Route new events (places real orders)
                await self.routing_tick()

                # Poll fills every 30s
                if now - last_fill_check > FILL_CHECK_INTERVAL:
                    await self.check_fills()
                    last_fill_check = now

                # Check sidecar heartbeats every 5 min
                if now - last_discovery > DISCOVERY_INTERVAL:
                    self._check_sidecar_heartbeats()

                # Re-discover every 5 min + refresh schedule
                if now - last_discovery > DISCOVERY_INTERVAL:
                    self._load_schedule()
                    new_tickers = await self.discover_markets()
                    if new_tickers:
                        await self.ws_subscribe(new_tickers)
                    last_discovery = now

                # Check pending entries every loop (lightweight — just reads books)
                await self.check_pending_entries()

                # Validate resting buys every 2 min
                if now - last_stale_check > STALE_CHECK_INTERVAL:
                    await self.validate_resting_buys()
                    last_stale_check = now

                # Reconcile every 60s — auto-post exits for naked positions
                if now - last_reconcile > 60:
                    await self.reconcile(quiet=True)
                    last_reconcile = now

                # Write own heartbeat
                try:
                    ws_age = int(now - max((b.updated for b in self.books.values()), default=0)) if self.books else 999
                    with open("/tmp/heartbeat_live_v3.json", "w") as _hf:
                        json.dump({"ts": int(now), "name": "live_v3", "status": "ok",
                                       "positions": len(self.positions), "resting_orders": len(self.pending_entries),
                                       "ws_connected": self.ws_connected, "bbo_age_sec": ws_age}, _hf)
                except Exception:
                    pass

                # Summary every 30 min
                if now - last_summary > 1800:
                    self.print_summary()
                    last_summary = now

                await asyncio.sleep(1)

            except KeyboardInterrupt:
                print("\n[STOP] Shutting down...", flush=True)
                self.print_summary()
                break
            except Exception as e:
                self._log("error", {"error": str(e), "traceback": traceback.format_exc()})
                await asyncio.sleep(5)

        if self.session:
            await self.session.close()
        self.log_file.close()


async def main():
    reconcile_only = "--reconcile-only" in sys.argv
    bot = LiveV3()
    await bot.run(reconcile_only=reconcile_only)

if __name__ == "__main__":
    asyncio.run(main())
