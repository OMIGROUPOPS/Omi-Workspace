#!/usr/bin/env python3
"""
live_v4.py - Path B v4 bid-laying executor (forked from live_v3.py).

Strategy: docs/bid_laying_policy_v1.md Sections 2-7 + Section 12 (v4 net-PnL
offsets). For each atlas-qualifying paired leg, post a maker bid at
T-(placement_minute) per the leg's anchor regime; marketable-taker if the
target bid is already at/through the ask, else resting maker; T-20m taker
fallback (= atlas baseline). Exit per the adaptive exit band table: "exit at
+X" with >=250ct depth, or "hold to settlement" (no exit posted; Bug 4 closes).

Entry table : docs/policy/per_regime_offsets_v2.csv
Exit table  : data/durable/spike_volatility_map/{category}_adaptive_exit_bands.parquet
Config      : config/deploy_v5.json (live_v3.py keeps deploy_v4.json -- rollback)

Bug 4 settlement detection (WS market_lifecycle_v2 + REST safety-net + BBO
backstop + idempotent process_settlement chokepoint) is inherited VERBATIM from
live_v3.py @366d8aa -- DO NOT modify those paths.
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
WS_PING_INTERVAL = 30
WS_SUBSCRIBE_BATCH = 50
WS_QUEUE_MAXSIZE = 5000       # WS recv->worker queue cap; lossless backpressure when worker is behind
DISCOVERY_INTERVAL = 300
# ENTRY_CANCEL_TIMEOUT removed in V4.2 -- replaced by match-start-aware expiry
FILL_CHECK_INTERVAL = 5      # poll fills every 5s
EXIT_PRICE_CAP = 98           # never post exit above 98c
ENTRY_BUFFER_SEC = 900        # stop entering 15 min before scheduled start
ENTRY_MAX_LEAD_SEC_BY_SERIES = {
    "KXATPMATCH": 43200,         # ATP Main Draw: 12h (books stable at T-12h, 1c spread)
    "KXWTAMATCH": 43200,         # WTA Main Draw: 12h (books stable at T-12h, 1c spread)
    "KXATPCHALLENGERMATCH": 14400,  # ATP Challenger: 4h (books not formed until T-4h)
    "KXWTACHALLENGERMATCH": 14400,  # WTA Challenger: 4h (books not formed until T-4h)
}
DEFAULT_ENTRY_MAX_LEAD_SEC = 14400

def _entry_lead_cap(event_ticker):
    series = event_ticker.split("-")[0] if event_ticker else ""
    return ENTRY_MAX_LEAD_SEC_BY_SERIES.get(series, DEFAULT_ENTRY_MAX_LEAD_SEC)
UNMATCHED_SKIP_CYCLES = 3     # skip unmatched events after this many discovery cycles
UNMATCHED_SKIP_AGE = 3600     # ...only if open_time is > 1h old
BOOK_STALENESS_SEC = 900      # 15 min — quiet pregame books may not update for 5-15 min
DEAD_SPREAD_THRESHOLD = 20    # don't post if spread > 20c
STALE_BUY_DELTA = 5           # cancel resting buy if our price > mid + 5c
PENDING_TIMEOUT_SEC = 7200    # cancel pending entry after 2h with no tight spread
STALE_CHECK_INTERVAL = 120    # validate resting buys every 2 min
SETTLEMENT_POLL_INTERVAL = 300  # Bug 4 §6.3: REST settlements safety-net poll every 5 min (LIVE only)
ROUTING_SWEEP_INTERVAL = 60     # backstop full-universe routing sweep cadence (placement is event-driven via on_bbo_update)

# v4 bid-laying timing (all ET-relative to scheduled match start)
V4_MAX_PLACEMENT_SEC = 240 * 60   # earliest placement in per_regime_offsets_v2 (T-4h)
V4_T20M_SEC = 20 * 60             # T-20m taker fallback = atlas baseline entry
V4_REPRICE_MOVE_CENTS = 5         # resting bid re-post threshold (1 cell width); STEP 5 heuristic

STATE_DIR = Path(__file__).resolve().parent / "state"
PROCESSED_FILE = STATE_DIR / "live_v3_processed.json"
V4_RESTING_FILE = STATE_DIR / "live_v4_resting.json"  # v4 resting-bid recovery (STEP 5)
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

# v4: own config file (deploy_v5.json). deploy_v4.json stays as live_v3.py's
# rollback config -- zero coupling. Env override var also renamed so the two
# executors cannot accidentally share one config.
CONFIG_PATH = Path(__file__).resolve().parent / "config" / "deploy_v5.json"
_cfg_override = os.environ.get("LIVE_V4_CONFIG")
if _cfg_override:
    CONFIG_PATH = Path(__file__).resolve().parent / _cfg_override
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
async def _real_api_get(s, ak, pk, path, rl):
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

async def _real_api_post(s, ak, pk, path, payload, rl):
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

async def _real_api_delete(s, ak, pk, path, rl):
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

    # Play type
    play_type: str = "A_tight"
    layered_exit_price: int = 0
    cell_exit_order_id: str = ""
    cell_exit_price: int = 0
    legacy: bool = False
    anchor_source: str = "fv_consensus"
    routed_cell: str = ""
    last_cancel_repost_ts: float = 0.0

    # State
    phase: str = "entry_pending"
    settled: bool = False
    pnl_cents: float = 0.0

    # ---- v4 bid-laying fields ----
    is_v4: bool = False
    regime_at_posting: str = ""        # e.g. "r85_94" at the minute the bid was placed
    target_price: int = 0             # the regime-offset target bid (resting maker)
    placement_minute: int = 0         # minutes-before-start this leg's bid was scheduled
    entry_mode: str = ""              # marketable_taker | resting_maker | miss_fallback
    paid_taker_fee: bool = False      # 1c/ct fee applies to marketable + fallback entries
    # P0 #5 decision (operator, 2026-05-25): fee is NOT modeled in computed
    # pnl_cents -- this flag only records the mode. The Bug-4 / paper try_fill
    # PnL math is left untouched (highest-risk surface; no edits near the
    # idempotent chokepoint before the live window). Computed PnL is ~1c/ct
    # optimistic on taker entries in BOTH paper and live; the Kalshi account
    # reconciliation reflects true fees. Paper findings report raw + fee-haircut
    # PnL; live cash is fee-accurate via exchange-side deduction.
    strategy: str = ""                # "exit" | "hold" (set at fill from exit table)
    exit_band_x: Optional[int] = None  # +X cents for exit cells; None for hold cells
    exit_cell_id: int = 0             # 1c cell used for the exit-table lookup (entry-priced)

# -------------------------------------------------------------------------
# Paper Mode (spec sha 32f29fda)
# -------------------------------------------------------------------------

_PAPER_API = None  # module-level; set at LiveV3 init when paper_mode=true


@dataclass
class PaperOrder:
    order_id: str
    ticker: str
    action: str
    side: str
    yes_price: int          # cents (internal storage)
    count: int
    remaining_count: int
    filled_count: int = 0
    status: str = "resting"
    post_ts: float = 0.0
    last_event_ts: float = 0.0
    client_order_id: str = ""
    book_depth_at_price_post: int = 0
    best_bid_at_post: int = 0
    best_ask_at_post: int = 100
    last_trade_price_at_post: int = 0
    last_trade_age_at_post: float = 0.0
    fv_anchor_at_post: Optional[float] = None
    spread_at_post: int = 0

    def to_kalshi_dict(self):
        return {
            "order_id": self.order_id,
            "ticker": self.ticker,
            "action": self.action,
            "side": self.side,
            "yes_price_dollars": self.yes_price / 100.0,
            "remaining_count_fp": float(self.remaining_count),
            "fill_count_fp": float(self.filled_count),
            "average_fill_price_fp": (self.yes_price / 100.0) if self.filled_count > 0 else 0.0,
            "yes_price": self.yes_price,
            "remaining_count": self.remaining_count,
            "count_filled": self.filled_count,
            "count": self.count,
            "status": self.status,
            "client_order_id": self.client_order_id,
        }


@dataclass
class PaperPosition:
    ticker: str
    event_ticker: str = ""
    qty: int = 0
    sold_qty: int = 0
    total_cost_cents: int = 0
    total_revenue_cents: int = 0
    realized_pnl_cents: int = 0
    open_buy_orders: List[str] = field(default_factory=list)
    open_sell_orders: List[str] = field(default_factory=list)
    first_entry_ts: float = 0.0
    last_event_ts: float = 0.0
    settled: bool = False
    settlement_price: Optional[int] = None

    @property
    def net_qty(self):
        return self.qty - self.sold_qty

    @property
    def avg_price(self):
        if self.qty == 0:
            return 0
        return self.total_cost_cents // self.qty

    def to_kalshi_dict(self):
        net = self.net_qty
        exposure_dollars = (self.avg_price * net) / 100.0 if net > 0 else 0.0
        traded_dollars = (self.avg_price * self.qty) / 100.0
        return {
            "ticker": self.ticker,
            "event_ticker": self.event_ticker,
            "position_fp": float(net),
            "market_exposure_dollars": exposure_dollars,
            "total_traded_dollars": traded_dollars,
            "settlement_status": "settled" if self.settled else "unsettled",
        }


class VolumeTracker:
    """Per-ticker rolling tracker of trade prints. Normalizes Kalshi WS
    taker_side ("yes"/"no") to internal aggressor side ("buy"/"sell") at
    record-time per spec §4."""

    def __init__(self, api=None, retention_sec=21600.0):
        self.api = api
        self.trades = {}  # ticker -> deque[(ts, price, qty, side)]
        self.retention_sec = retention_sec
        self.unsided_count = 0
        self.sample_count = 0

    def record(self, ticker, ts, price, qty, taker_side):
        if taker_side == "yes":
            side = "buy"
        elif taker_side == "no":
            side = "sell"
        else:
            side = ""
            self.unsided_count += 1
        self.sample_count += 1
        if ticker not in self.trades:
            self.trades[ticker] = deque()
        dq = self.trades[ticker]
        dq.append((ts, int(price), int(qty), side))
        cutoff = ts - self.retention_sec
        while dq and dq[0][0] < cutoff:
            dq.popleft()

    def volume_at_or_through(self, ticker, side, target_price, since_ts):
        """side here is internal ("buy" or "sell")."""
        dq = self.trades.get(ticker)
        if not dq:
            return 0
        total = 0
        if side == "buy":
            for ts, price, qty, s in dq:
                if ts >= since_ts and price <= target_price and s == "sell":
                    total += qty
        else:
            for ts, price, qty, s in dq:
                if ts >= since_ts and price >= target_price and s == "buy":
                    total += qty
        return total

    def depth_for_side(self, ticker, side, price):
        if not self.api or not self.api.bot:
            return 0
        book = self.api.bot.books.get(ticker)
        if not book:
            return 0
        if side == "ask":
            return book.asks.get(price, 0)
        return book.bids.get(price, 0)


class PaperFillSimulator:
    def __init__(self, api):
        self.api = api

    def evaluate_book_cross(self, ticker):
        bot = self.api.bot
        book = bot.books.get(ticker)
        if not book:
            return
        for order in list(self.api.paper_orders.values()):
            if order.ticker != ticker or order.status != "resting":
                continue
            if order.action == "buy" and book.best_ask <= order.yes_price and book.best_ask > 0:
                self.try_fill(order, order.yes_price, time.time(), "book_cross")
            elif order.action == "sell" and book.best_bid >= order.yes_price and book.best_bid < 100:
                self.try_fill(order, order.yes_price, time.time(), "book_cross")

    def evaluate_trade_print(self, ticker, ts, price):
        for order in list(self.api.paper_orders.values()):
            if order.ticker != ticker or order.status != "resting":
                continue
            if order.action == "buy" and price <= order.yes_price:
                self.try_fill(order, order.yes_price, ts, "trade_print")
            elif order.action == "sell" and price >= order.yes_price:
                self.try_fill(order, order.yes_price, ts, "trade_print")

    def try_fill(self, order, fill_price, fill_ts, trigger):
        if order.status != "resting":
            return  # Idempotency — see spec §7
        order.status = "executed"
        order.filled_count = order.count
        order.remaining_count = 0
        order.last_event_ts = fill_ts

        bot = self.api.bot
        pos = self.api.paper_positions.get(order.ticker)
        if pos is None:
            event_ticker = bot.ticker_to_event.get(order.ticker, "")
            pos = PaperPosition(ticker=order.ticker, event_ticker=event_ticker)
            self.api.paper_positions[order.ticker] = pos

        if order.action == "buy":
            pos.qty += order.count
            pos.total_cost_cents += order.count * fill_price
            if not pos.first_entry_ts:
                pos.first_entry_ts = fill_ts
            if order.order_id in pos.open_buy_orders:
                pos.open_buy_orders.remove(order.order_id)
        else:
            pos.sold_qty += order.count
            pos.total_revenue_cents += order.count * fill_price
            if order.order_id in pos.open_sell_orders:
                pos.open_sell_orders.remove(order.order_id)
            if pos.net_qty == 0:
                pos.realized_pnl_cents = pos.total_revenue_cents - pos.total_cost_cents
        pos.last_event_ts = fill_ts

        time_to_fill_sec = fill_ts - order.post_ts
        internal_side = order.action
        vol_lifetime = self.api.volume_tracker.volume_at_or_through(
            order.ticker, internal_side, order.yes_price, order.post_ts)
        depth_side = "ask" if order.action == "buy" else "bid"
        depth_at_fill = self.api.volume_tracker.depth_for_side(
            order.ticker, depth_side, order.yes_price)
        book_now = bot.books.get(order.ticker)
        best_bid = book_now.best_bid if book_now else 0
        best_ask = book_now.best_ask if book_now else 100
        last_trade_price = book_now.last_trade_price if book_now else 0

        event = "paper_fill" if order.action == "buy" else "paper_exit_fill"
        self.api._emit(event, {
            "order_id": order.order_id,
            "fill_price": fill_price,
            "qty": order.count,
            "time_to_fill_sec": round(time_to_fill_sec, 2),
            "volume_at_or_through_lifetime": vol_lifetime,
            "depth_at_fill": depth_at_fill,
            "fill_trigger": trigger,
            "best_bid_at_fill": best_bid,
            "best_ask_at_fill": best_ask,
            "last_trade_price_at_fill": last_trade_price,
            "post_telemetry": {
                "best_bid": order.best_bid_at_post,
                "best_ask": order.best_ask_at_post,
                "depth_at_price": order.book_depth_at_price_post,
                "fv_anchor": order.fv_anchor_at_post,
                "last_trade_price": order.last_trade_price_at_post,
            },
            "entry_avg_price_after_fill": pos.avg_price,
            "net_qty_after_fill": pos.net_qty,
            "realized_pnl_cents": pos.realized_pnl_cents if order.action == "sell" else None,
        }, ticker=order.ticker)


class PaperApi:
    PAPER_STATE_VERSION = "1.0"

    def __init__(self, bot):
        self.bot = bot
        self.paper_orders = {}
        self.paper_positions = {}
        self.volume_tracker = VolumeTracker(api=self)
        self.fill_simulator = PaperFillSimulator(self)
        self.next_seq = 0
        self.last_heartbeat_ts = 0.0
        self.fills_last_hour = deque()
        self.event_counts_last_hour = deque()

    def _new_order_id(self, ticker, ts):
        self.next_seq += 1
        return "PAPER-%s-%d-%06d" % (ticker, int(ts), self.next_seq)

    def _emit(self, event, details=None, ticker=""):
        self.bot._log(event, details or {}, ticker=ticker)
        now = time.time()
        self.event_counts_last_hour.append((now, event))
        if event in ("paper_fill", "paper_exit_fill"):
            self.fills_last_hour.append(now)
        cutoff = now - 3600
        while self.event_counts_last_hour and self.event_counts_last_hour[0][0] < cutoff:
            self.event_counts_last_hour.popleft()
        while self.fills_last_hour and self.fills_last_hour[0] < cutoff:
            self.fills_last_hour.popleft()

    async def handle_get(self, s, ak, pk, path, rl):
        if not path.startswith("/trade-api/v2/portfolio/"):
            return await _real_api_get(s, ak, pk, path, rl)
        from urllib.parse import urlsplit, parse_qs
        parts = urlsplit(path)
        path_only = parts.path
        query = parse_qs(parts.query)

        # Single order: /trade-api/v2/portfolio/orders/<id>
        if path_only.startswith("/trade-api/v2/portfolio/orders/"):
            oid = path_only.split("/")[-1]
            order = self.paper_orders.get(oid)
            if not order:
                return {"order": None, "_error": "not_found"}
            return {"order": order.to_kalshi_dict()}

        # List orders
        if path_only == "/trade-api/v2/portfolio/orders":
            ticker_filter = query.get("ticker", [None])[0]
            status_filter = query.get("status", [None])[0]
            orders = []
            for o in self.paper_orders.values():
                if ticker_filter and o.ticker != ticker_filter:
                    continue
                if status_filter and o.status != status_filter:
                    continue
                orders.append(o.to_kalshi_dict())
            return {"orders": orders}

        # Positions
        if path_only == "/trade-api/v2/portfolio/positions":
            ticker_filter = query.get("ticker", [None])[0]
            settlement_filter = query.get("settlement_status", [None])[0]
            positions = []
            for p in self.paper_positions.values():
                if p.net_qty == 0:
                    continue
                if ticker_filter and p.ticker != ticker_filter:
                    continue
                if settlement_filter == "unsettled" and p.settled:
                    continue
                if settlement_filter == "settled" and not p.settled:
                    continue
                positions.append(p.to_kalshi_dict())
            return {"market_positions": positions}

        return await _real_api_get(s, ak, pk, path, rl)

    async def handle_post(self, s, ak, pk, path, payload, rl):
        if path != "/trade-api/v2/portfolio/orders":
            return await _real_api_post(s, ak, pk, path, payload, rl)
        ticker = payload.get("ticker", "")
        action = payload.get("action", "")
        side = payload.get("side", "yes")
        count = int(payload.get("count", 0))
        yes_price = int(payload.get("yes_price", 0))
        client_order_id = payload.get("client_order_id", "")
        post_ts = time.time()
        order_id = self._new_order_id(ticker, post_ts)

        book = self.bot.books.get(ticker)
        best_bid = book.best_bid if book else 0
        best_ask = book.best_ask if book else 100
        spread = (best_ask - best_bid) if (best_ask < 100 and best_bid > 0) else 0
        last_trade_price = book.last_trade_price if book else 0
        last_trade_ts = book.last_trade_ts if book else 0.0
        last_trade_age = (post_ts - last_trade_ts) if last_trade_ts else 0.0
        if action == "buy":
            depth_at_price = book.bids.get(yes_price, 0) if book else 0
            depth_opposite = book.asks.get(yes_price, 0) if book else 0
        else:
            depth_at_price = book.asks.get(yes_price, 0) if book else 0
            depth_opposite = book.bids.get(yes_price, 0) if book else 0

        fv_anchor = None
        try:
            event_ticker = self.bot.ticker_to_event.get(ticker, "")
            if event_ticker and hasattr(self.bot, "_get_side_fv"):
                side_fv = self.bot._get_side_fv(ticker, event_ticker)
                if side_fv and side_fv.get("fv_cents") is not None:
                    fv_anchor = float(side_fv["fv_cents"])
        except Exception:
            fv_anchor = None
        fv_minus_price = (fv_anchor - yes_price) if fv_anchor is not None else None

        order = PaperOrder(
            order_id=order_id, ticker=ticker, action=action, side=side,
            yes_price=yes_price, count=count, remaining_count=count,
            post_ts=post_ts, last_event_ts=post_ts, client_order_id=client_order_id,
            book_depth_at_price_post=depth_at_price,
            best_bid_at_post=best_bid, best_ask_at_post=best_ask,
            last_trade_price_at_post=last_trade_price,
            last_trade_age_at_post=last_trade_age,
            fv_anchor_at_post=fv_anchor, spread_at_post=spread,
        )
        self.paper_orders[order_id] = order

        pos = self.paper_positions.get(ticker)
        if pos is None:
            event_ticker = self.bot.ticker_to_event.get(ticker, "")
            pos = PaperPosition(ticker=ticker, event_ticker=event_ticker)
            self.paper_positions[ticker] = pos
        if action == "buy":
            pos.open_buy_orders.append(order_id)
        else:
            pos.open_sell_orders.append(order_id)

        self._emit("paper_order_posted", {
            "order_id": order_id,
            "client_order_id": client_order_id,
            "action": action, "side": side,
            "yes_price": yes_price, "count": count,
            "best_bid": best_bid, "best_ask": best_ask,
            "spread": spread,
            "depth_at_price": depth_at_price,
            "depth_opposite_side": depth_opposite,
            "last_trade_price": last_trade_price,
            "last_trade_age_sec": round(last_trade_age, 1),
            "fv_anchor": fv_anchor,
            "fv_minus_price_cents": fv_minus_price,
            "post_ts": post_ts,
        }, ticker=ticker)

        return {"order": {"order_id": order_id, "ticker": ticker, "status": "resting",
                          "yes_price": yes_price, "count": count}}

    async def handle_delete(self, s, ak, pk, path, rl):
        if not path.startswith("/trade-api/v2/portfolio/orders/"):
            return await _real_api_delete(s, ak, pk, path, rl)
        oid = path.split("/")[-1]
        order = self.paper_orders.get(oid)
        if not order or order.status != "resting":
            return False
        order.status = "canceled"
        cancel_ts = time.time()
        order.last_event_ts = cancel_ts
        pos = self.paper_positions.get(order.ticker)
        if pos:
            if oid in pos.open_buy_orders:
                pos.open_buy_orders.remove(oid)
            if oid in pos.open_sell_orders:
                pos.open_sell_orders.remove(oid)
        lifetime = cancel_ts - order.post_ts
        internal_side = order.action
        vol = self.volume_tracker.volume_at_or_through(
            order.ticker, internal_side, order.yes_price, order.post_ts)
        book = self.bot.books.get(order.ticker)
        best_bid = book.best_bid if book else 0
        best_ask = book.best_ask if book else 100
        self._emit("paper_order_cancelled", {
            "order_id": oid,
            "post_ts": order.post_ts,
            "lifetime_sec": round(lifetime, 2),
            "fills_during_lifetime": 0,
            "volume_at_or_through_lifetime": vol,
            "best_bid_at_cancel": best_bid,
            "best_ask_at_cancel": best_ask,
        }, ticker=order.ticker)
        return True

    def on_book_update(self, ticker):
        try:
            self.fill_simulator.evaluate_book_cross(ticker)
        except Exception as e:
            self.bot._log("paper_error", {"where": "on_book_update",
                                          "error": str(e)}, ticker=ticker)

    def on_trade(self, ticker, ts, price, qty, taker_side):
        try:
            self.volume_tracker.record(ticker, ts, price, qty, taker_side)
            self.fill_simulator.evaluate_trade_print(ticker, ts, price)
        except Exception as e:
            self.bot._log("paper_error", {"where": "on_trade",
                                          "error": str(e)}, ticker=ticker)

    def maybe_heartbeat(self):
        now = time.time()
        if now - self.last_heartbeat_ts < 60:
            return
        self.last_heartbeat_ts = now
        try:
            active_pos = sum(1 for p in self.paper_positions.values()
                             if p.net_qty > 0 and not p.settled)
            active_orders = sum(1 for o in self.paper_orders.values()
                                if o.status == "resting")
            mtm = self._compute_mark_to_market_cents()
            realized = sum(p.realized_pnl_cents for p in self.paper_positions.values())
            counts = {}
            cutoff = now - 3600
            for ts, event in self.event_counts_last_hour:
                if ts >= cutoff:
                    counts[event] = counts.get(event, 0) + 1
            fills_last_hour = sum(1 for ts in self.fills_last_hour if ts >= cutoff)
            self._emit("paper_heartbeat", {
                "active_paper_positions": active_pos,
                "active_paper_orders_resting": active_orders,
                "paper_pnl_mtm_cents": mtm,
                "paper_pnl_realized_cents": realized,
                "fills_in_last_hour": fills_last_hour,
                "telemetry_event_counts_last_hour": counts,
            })
            try:
                self.dump_state("/root/Omi-Workspace/arb-executor/paper_state.json")
            except Exception as e:
                self.bot._log("paper_error", {"where": "dump_state", "error": str(e)})
        except Exception as e:
            self.bot._log("paper_error", {"where": "maybe_heartbeat", "error": str(e)})

    def _compute_mark_to_market_cents(self):
        total = 0
        for pos in self.paper_positions.values():
            if pos.settled or pos.net_qty <= 0:
                continue
            book = self.bot.books.get(pos.ticker)
            best_bid = book.best_bid if book else 0
            net = pos.net_qty
            value_now = net * best_bid
            cost_basis_remaining = (pos.total_cost_cents // pos.qty) * net if pos.qty > 0 else 0
            total += value_now - cost_basis_remaining
        return total

    def dump_state(self, path):
        data = {
            "PAPER_STATE_VERSION": self.PAPER_STATE_VERSION,
            "next_seq": self.next_seq,
            "ts": time.time(),
            "orders": [o.__dict__ for o in self.paper_orders.values()],
            "positions": [p.__dict__ for p in self.paper_positions.values()],
        }
        tmp_path = path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, default=str)
        os.replace(tmp_path, path)

    def load_state(self, path, max_age_sec):
        if not os.path.exists(path):
            self._emit("paper_state_skipped", {"reason": "file_not_found"})
            return False
        mtime = os.path.getmtime(path)
        age = time.time() - mtime
        if age > max_age_sec:
            self._emit("paper_state_skipped", {"reason": "file_stale",
                                               "age_sec": round(age, 1)})
            return False
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            self._emit("paper_state_skipped", {"reason": "parse_error",
                                               "error": str(e)})
            return False
        if data.get("PAPER_STATE_VERSION") != self.PAPER_STATE_VERSION:
            self._emit("paper_state_skipped", {"reason": "version_mismatch"})
            return False
        try:
            self.next_seq = int(data.get("next_seq", 0))
            for od in data.get("orders", []):
                o = PaperOrder(
                    order_id=od["order_id"], ticker=od["ticker"],
                    action=od["action"], side=od["side"],
                    yes_price=int(od["yes_price"]), count=int(od["count"]),
                    remaining_count=int(od["remaining_count"]),
                    filled_count=int(od.get("filled_count", 0)),
                    status=od.get("status", "resting"),
                    post_ts=float(od.get("post_ts", 0.0)),
                    last_event_ts=float(od.get("last_event_ts", 0.0)),
                    client_order_id=od.get("client_order_id", ""),
                    book_depth_at_price_post=int(od.get("book_depth_at_price_post", 0)),
                    best_bid_at_post=int(od.get("best_bid_at_post", 0)),
                    best_ask_at_post=int(od.get("best_ask_at_post", 100)),
                    last_trade_price_at_post=int(od.get("last_trade_price_at_post", 0)),
                    last_trade_age_at_post=float(od.get("last_trade_age_at_post", 0.0)),
                    fv_anchor_at_post=od.get("fv_anchor_at_post"),
                    spread_at_post=int(od.get("spread_at_post", 0)),
                )
                self.paper_orders[o.order_id] = o
            for pd in data.get("positions", []):
                p = PaperPosition(
                    ticker=pd["ticker"],
                    event_ticker=pd.get("event_ticker", ""),
                    qty=int(pd.get("qty", 0)),
                    sold_qty=int(pd.get("sold_qty", 0)),
                    total_cost_cents=int(pd.get("total_cost_cents", 0)),
                    total_revenue_cents=int(pd.get("total_revenue_cents", 0)),
                    realized_pnl_cents=int(pd.get("realized_pnl_cents", 0)),
                    open_buy_orders=list(pd.get("open_buy_orders", [])),
                    open_sell_orders=list(pd.get("open_sell_orders", [])),
                    first_entry_ts=float(pd.get("first_entry_ts", 0.0)),
                    last_event_ts=float(pd.get("last_event_ts", 0.0)),
                    settled=bool(pd.get("settled", False)),
                    settlement_price=pd.get("settlement_price"),
                )
                self.paper_positions[p.ticker] = p
            self._emit("paper_state_restored", {
                "orders_loaded": len(self.paper_orders),
                "positions_loaded": len(self.paper_positions),
                "state_age_sec": round(age, 1),
                "schema_version": self.PAPER_STATE_VERSION,
            })
            return True
        except Exception as e:
            self._emit("paper_state_skipped", {"reason": "parse_error",
                                               "error": str(e)})
            return False


# -------------------------------------------------------------------------
# Module-level dispatchers (replace the original api_get/post/delete)
# -------------------------------------------------------------------------

async def api_get(s, ak, pk, path, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_get(s, ak, pk, path, rl)
    return await _real_api_get(s, ak, pk, path, rl)


async def api_post(s, ak, pk, path, payload, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_post(s, ak, pk, path, payload, rl)
    return await _real_api_post(s, ak, pk, path, payload, rl)


async def api_delete(s, ak, pk, path, rl):
    if _PAPER_API is not None:
        return await _PAPER_API.handle_delete(s, ak, pk, path, rl)
    return await _real_api_delete(s, ak, pk, path, rl)


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
        # v4 has no DCA. deploy_v5.json omits these keys; default safely so the
        # FV/legacy DCA paths (gated off) don't KeyError at init.
        self.dca_size = self.config["sizing"].get("dca_contracts", 0)
        self.dca_fill_floor = self.config.get("dca_fill_floor_cents", 10)
        self.exit_size = self.config["sizing"].get("exit_contracts", self.entry_size)
        # v4 toggles
        self.fv_scenarios_enabled = self.config.get("fv_anchor_scenarios_enabled", False)
        self.round5_enabled = self.config.get("round5_detector_enabled", False)
        self.exit_depth_floor = self.config.get("min_depth_for_exit_realization", 250)
        self.categories_enabled = set(self.config.get("categories_enabled",
            ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]))
        # Open the log file BEFORE anything that calls _log() (the table
        # loaders below log their results). _log needs self.log_file.
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(ET).strftime("%Y%m%d")
        self.log_path = LOG_DIR / ("live_v3_%s.jsonl" % date_str)
        self.log_file = open(self.log_path, "a")

        # v4 deployable tables (loaded once into plain dicts; no hot-path I/O)
        self.entry_table = {}   # (category, regime) -> (placement_min, offset_cents, fill_rate, net_roi_pct)
        self.exit_table = {}    # category -> {cell_id(int) -> (band_x|None, "exit"|"hold")}
        self._load_entry_table()
        self._load_exit_table()

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
        self._event_routing: Set[str] = set()   # events currently being routed (on_bbo_update vs backstop sweep)
        self._mgmt_inflight: Set[str] = set()    # tickers whose v4 resting bid is being managed (serialize callers)
        self._ws_queue = None                    # asyncio.Queue: WS recv (producer) -> worker (consumer); created in run()
        self._loop_lag_samples = 0               # loop-lag monitor sample counter

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

        # log_file already opened above (before the table loaders).
        self._log("system_start", {"mode": "LIVE", "config_path": str(CONFIG_PATH),
                                    "executor": "v4_bid_laying",
                                    "fv_scenarios_enabled": self.fv_scenarios_enabled,
                                    "active_cells": len(self.config.get("active_cells", {})),
                                    "disabled_cells": len(self.config.get("disabled_cells", [])),
                                    "entry_table_rows": len(self.entry_table),
                                    "exit_table_categories": list(self.exit_table.keys()),
                                    "entry_size": self.entry_size,
                                    "exit_size": self.exit_size,
                                    "exit_cap": EXIT_PRICE_CAP})
        self._load_schedule()

        # Paper mode init (spec §2.2)
        if self.config.get("paper_mode", False):
            global _PAPER_API
            _PAPER_API = PaperApi(bot=self)
            self._log("paper_mode_enabled", {
                "config_path": str(CONFIG_PATH),
                "PAPER_MODE_VERSION": "1.0",
                "paper_state_max_age_sec": self.config.get("paper_state_max_age_sec", 86400),
            })

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

        # Extract ticker date for cross-day mismatch guard
        import re as _re
        _dm = _re.search(r"-(\d{2})([A-Z]{3})(\d{2})", event_ticker)
        _month_map = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                      "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

        def _date_ok(sched_result):
            """Reject schedule match if start_time date differs from ticker date by >12h."""
            if not _dm:
                return True
            try:
                tk_date = datetime(2000+int(_dm.group(1)), _month_map[_dm.group(2)],
                                   int(_dm.group(3)), 16, 0, tzinfo=timezone.utc)
                sched_dt = datetime.fromisoformat(sched_result.get("start_time","").replace("Z","+00:00"))
                if abs((sched_dt - tk_date).total_seconds()) > 43200:
                    self._log("schedule_date_mismatch", {
                        "event": event_ticker,
                        "ticker_date": tk_date.strftime("%Y-%m-%d"),
                        "schedule_date": sched_dt.strftime("%Y-%m-%dT%H:%M"),
                    })
                    return False
            except Exception:
                pass
            return True

        # Try direct match first
        result = match_kalshi_event(event_ticker, self.schedule)
        if result and _date_ok(result):
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
            if result and _date_ok(result):
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

    # ------------------------------------------------------------------
    # v4 deployable table loaders (STEP 3) -- run once at init
    # ------------------------------------------------------------------
    def _load_entry_table(self):
        """Load per_regime_offsets_v2.csv into self.entry_table keyed
        (category, anchor_regime) -> (placement_minute, bid_offset_cents,
        expected_fill_rate, expected_net_roi_pct). 36 rows = 4 cat x 9 regime."""
        import csv as _csv
        rel = self.config.get("entry_table_path", "docs/policy/per_regime_offsets_v2.csv")
        path = Path(__file__).resolve().parent / rel
        n = 0
        with open(path, newline="") as f:
            for row in _csv.DictReader(f):
                key = (row["category"].strip(), row["anchor_regime"].strip())
                self.entry_table[key] = (
                    int(float(row["placement_minute"])),
                    int(float(row["bid_offset_cents"])),
                    float(row["expected_fill_rate"]),
                    float(row["expected_net_roi_pct"]),
                )
                n += 1
        self._log("entry_table_loaded", {"rows": n, "path": str(rel)})

    def _load_exit_table(self):
        """Load the 4 {category}_adaptive_exit_bands.parquet into
        self.exit_table[category] = {cell_id -> (band_x|None, "exit"|"hold")}.
        Each band's [price_low, price_high] is expanded to its constituent 1c
        cell_ids; band_exit_X == "HOLD" -> ("hold", band_x=None), else
        ("exit", band_x=int). pyarrow read happens here only; the hot path
        reads the cached dict."""
        import pyarrow.parquet as _pq
        rel_dir = self.config.get("exit_table_dir", "data/durable/spike_volatility_map/")
        base = Path(__file__).resolve().parent / rel_dir
        loaded = {}
        for cat in ("ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"):
            fp = base / ("%s_adaptive_exit_bands.parquet" % cat.lower())
            tbl = _pq.read_table(fp).to_pandas()
            cell_map = {}
            n_hold = 0
            for _, r in tbl.iterrows():
                lo, hi = int(r["price_low"]), int(r["price_high"])
                raw = str(r["band_exit_X"]).strip()
                if raw.upper() == "HOLD":
                    rule, band_x = "hold", None
                    n_hold += (hi - lo + 1)
                else:
                    rule, band_x = "exit", int(round(float(raw)))
                for cid in range(lo, hi + 1):
                    cell_map[cid] = (band_x, rule)
            loaded[cat] = cell_map
            self._log("exit_table_loaded", {
                "category": cat, "bands": len(tbl),
                "cells_mapped": len(cell_map), "hold_cells": n_hold,
            })
        self.exit_table = loaded

    def exit_rule_for(self, category, price_cents):
        """v4 exit lookup: returns (band_x|None, rule) for the 1c cell of
        price_cents. rule in {"exit","hold"}. Falls back to ("exit", default)
        if the category/cell is somehow absent (never expected for the 4
        enabled categories)."""
        cid = self.cell_lookup(category, price_cents)
        cmap = self.exit_table.get(category)
        if cmap and cid in cmap:
            return cmap[cid]
        return (15, "exit")  # defensive default; logged by caller if hit

    def get_category(self, ticker):
        for cat_name, prefixes in SERIES_MAP.items():
            for prefix in prefixes:
                if ticker.startswith(prefix):
                    return cat_name
        return None

    def cell_lookup(self, category, current_kalshi_price_cents):
        """v4 direction-free 1c cell classification from the current Kalshi
        yes-price. Returns an int cell_id in [5, 94] (the exit-band table's
        domain). No direction, no 5c bucket -- the exit band table is keyed on
        the 1c cell of the *current* price (entry-priced cell at exit lookup)."""
        cell_id = int(round(current_kalshi_price_cents))
        if cell_id < 5:
            cell_id = 5
        if cell_id > 94:
            cell_id = 94
        return cell_id

    def regime_lookup(self, category, current_kalshi_price_cents):
        """Map the current Kalshi yes-price to its 10c regime band for the v4
        entry-offset table (per_regime_offsets_v2.csv). Band low boundaries:
        5,15,25,...,85 -> r05_14 ... r85_94."""
        p = current_kalshi_price_cents
        if p < 15: return "r05_14"
        if p < 25: return "r15_24"
        if p < 35: return "r25_34"
        if p < 45: return "r35_44"
        if p < 55: return "r45_54"
        if p < 65: return "r55_64"
        if p < 75: return "r65_74"
        if p < 85: return "r75_84"
        return "r85_94"

    def _legacy_cell_lookup(self, category, direction, entry_mid):
        """LEGACY FV-anchor cell lookup (5c bucket + direction). Used only by the
        FV-scenario routing path, which v4 gates off by default
        (config fv_anchor_scenarios_enabled). Retained for emergency rollback."""
        bucket = int(entry_mid / 5) * 5
        cell_name = "%s_%s_%d-%d" % (category, direction, bucket, bucket + 4)
        active = self.config.get("active_cells", {})
        if cell_name in self.config.get("disabled_cells", []):
            return cell_name, None
        if cell_name in active:
            return cell_name, active[cell_name]
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
        if _PAPER_API is not None:
            _PAPER_API.on_trade(ticker, book.last_trade_ts, price, count, side)
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
        # Position accumulation guard: cap total buy exposure per ticker
        if action == "buy":
            target_max = self.config["sizing"]["entry_contracts"]
            existing_pos = self.positions.get(ticker)
            current_qty = existing_pos.entry_qty if existing_pos and existing_pos.phase == "active" else 0
            if current_qty >= target_max:
                self._log("buy_blocked_position_full", {
                    "current_qty": current_qty, "target_max": target_max,
                    "attempted_count": count, "price": price,
                }, ticker=ticker)
                return "", {"_error": "position_full"}
            if current_qty + count > target_max:
                count = target_max - current_qty
                self._log("buy_qty_reduced", {
                    "current_qty": current_qty, "reduced_to": count,
                    "target_max": target_max, "price": price,
                }, ticker=ticker)

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
                    "params": {"channels": ["orderbook_delta", "trade", "market_lifecycle_v2"], "market_tickers": batch}}))
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
        if _PAPER_API is not None:
            _PAPER_API.on_book_update(ticker)

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
        if _PAPER_API is not None:
            _PAPER_API.on_book_update(ticker)

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
        """PRODUCER: read frames off the WebSocket and enqueue them -- nothing
        else. Kept deliberately trivial so the recv loop yields to the event
        loop (and thus the websockets keepalive ping coroutine) on every frame,
        regardless of routing load. ALL heavy processing -- parse, book apply,
        on_bbo_update routing, lifecycle settlement -- happens in _ws_worker
        draining the queue.

        Why this matters: in paper mode the api_get/place_order calls inside
        on_bbo_update route through PaperApi coroutines that complete WITHOUT
        awaiting any real I/O, so awaiting them does NOT yield to the loop.
        Processing a resubscribe snapshot flood inline here therefore blocked
        the loop past ping_timeout (1011) -> reconnect -> flood -> repeat. The
        queue + per-message worker yield breaks that self-sustaining loop."""
        while True:
            try:
                if not self.ws_connected or not self.ws:
                    await self._ws_reconnect()
                    continue
                raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
                # Lossless backpressure: await put applies backpressure when the
                # worker is behind (bounds memory) without dropping frames -- a
                # dropped frame could be a market_lifecycle settlement (Bug 4) or
                # a trade-tape print. The await itself yields, keeping recv (and
                # the keepalive) responsive.
                await self._ws_queue.put(raw)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._log("ws_error", {"error": str(e)})
                self.ws_connected = False
                await self._ws_reconnect()

    async def _ws_worker(self):
        """CONSUMER: drain the WS queue and dispatch each frame. Yields to the
        event loop after EVERY message (await asyncio.sleep(0)) so a burst (e.g.
        a 134-ticker resubscribe snapshot flood) can never block the keepalive
        ping -- synchronous work is bounded to one message between yields.
        Processing errors are logged and never propagate (no reconnect)."""
        while True:
            raw = await self._ws_queue.get()
            try:
                await self._dispatch_ws_message(raw)
            except Exception as e:
                self._log("ws_worker_error",
                          {"error": str(e), "traceback": traceback.format_exc()})
            finally:
                self._ws_queue.task_done()
                # Yield -- bounds synchronous work to a single message so the
                # loop (recv + keepalive) is serviced between every dispatch.
                await asyncio.sleep(0)

    async def _dispatch_ws_message(self, raw):
        """Dispatch one raw WS frame. Identical processing to the pre-split
        ws_reader body -- only the invocation moved off the recv coroutine onto
        the worker. Preserves Bug 4 lifecycle handling and trade-tape capture."""
        msg = json.loads(raw)
        typ = msg.get("type", "")
        if typ == "orderbook_snapshot":
            tk = msg.get("msg", {}).get("market_ticker", "")
            self.apply_snapshot(tk, msg.get("msg", {}))
            if tk:
                await self.on_bbo_update(tk)
        elif typ == "orderbook_delta":
            tk = msg.get("msg", {}).get("market_ticker", "")
            bk_before = self.books.get(tk)
            old_bbo = (bk_before.best_bid, bk_before.best_ask) if bk_before else None
            self.apply_delta(tk, msg.get("msg", {}))
            bk_after = self.books.get(tk)
            new_bbo = (bk_after.best_bid, bk_after.best_ask) if bk_after else None
            # Only route on an actual BBO change (matches tennis_stb): a delta
            # that doesn't move best_bid/best_ask can't change any placement
            # decision, so skip the routing work.
            if tk and new_bbo != old_bbo:
                await self.on_bbo_update(tk)
        elif typ == "trade":
            self.apply_trade(msg.get("msg", {}).get("market_ticker", msg.get("msg", {}).get("ticker", "")),
                            msg.get("msg", {}))
        elif typ == "market_lifecycle_v2":
            # Bug 4 §6.2: settled payload is minimal (no value) -> async REST hop.
            sub = msg.get("msg", {})
            if sub.get("event_type") == "settled":
                tk = sub.get("market_ticker", "")
                settled_ts = sub.get("settled_ts", time.time())
                if tk:
                    # Don't block the worker on a REST call -- fire and forget.
                    asyncio.create_task(self._handle_ws_settlement(tk, settled_ts))
            # determination / deactivated: ignored in v1 (§13 deferred caching)

    async def _loop_lag_monitor(self):
        """Instrument event-loop scheduling lag (verification for the keepalive
        starvation fix). Sleeps 1.0s and measures the actual elapsed time; a
        delta >1.5s means the loop was starved by synchronous work. Emits a
        loop_lag event on any starvation spike and a periodic loop_lag_sample
        baseline every 30s. App greps loop_lag* to confirm starvation is gone
        before the cutover gate (healthy steady-state ~1.000s, zero spikes)."""
        while True:
            t0 = time.monotonic()
            await asyncio.sleep(1.0)
            delta = time.monotonic() - t0
            self._loop_lag_samples += 1
            qd = self._ws_queue.qsize() if self._ws_queue is not None else 0
            if delta > 1.5:
                self._log("loop_lag", {"expected_sec": 1.0, "actual_sec": round(delta, 3),
                                       "lag_sec": round(delta - 1.0, 3), "ws_queue_depth": qd})
            elif self._loop_lag_samples % 30 == 0:
                self._log("loop_lag_sample", {"actual_sec": round(delta, 3),
                                              "ws_queue_depth": qd})

    async def _handle_ws_settlement(self, ticker, settled_ts):
        """Bug 4 §6.2: WS settled events carry no settlement value (§4.1). Fetch
        it from the public /markets/{ticker} endpoint (paper-safe -- passes
        through to real Kalshi via PaperApi.handle_get). Decoupled into its own
        coroutine so the WS reader loop is not blocked by the REST call."""
        path = "/trade-api/v2/markets/%s" % ticker
        data = await api_get(self.session, self.ak, self.pk, path, self.rl)
        market = (data or {}).get("market", data) or {}

        if market.get("status") != "finalized":
            # Pre-finalized race: determination not yet complete. Do NOT settle.
            # The 5-min REST poll (live) or a later BBO cross will catch it.
            self._log("ws_settled_pre_finalized",
                      {"market_status": market.get("status")}, ticker=ticker)
            return

        # Void guard (decision b): never auto-settle a voided market.
        result = market.get("result") or market.get("market_result")
        if result == "void":
            self._log("settlement_void_manual",
                      {"source": "ws_lifecycle"}, ticker=ticker)
            return

        # Normalize dollars -> integer cents at the call site (decision c).
        sv_dollars = market.get("settlement_value_dollars",
                                market.get("settlement_value", "0"))
        try:
            settle_val_cents = max(0, min(100, round(float(sv_dollars) * 100)))
        except (TypeError, ValueError):
            self._log("ws_settle_value_unparseable", {"raw": sv_dollars}, ticker=ticker)
            return

        self.process_settlement(ticker, settle_val_cents, settled_ts, source="ws_lifecycle")

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
                                # No reliable commence source — skip rather than use Kalshi expiration
                                self.event_unmatched_cycles[et] = self.event_unmatched_cycles.get(et, 0) + 1
                                self._log("no_reliable_commence_source", {"event": et})
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
            if not book or book.updated < time.time() - BOOK_STALENESS_SEC:
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

    async def _v4_apply_exit(self, tk, pos, fill_price, filled):
        """STEP 7. Apply the atlas exit rule for a freshly-filled v4 position
        from its entry-priced 1c cell. Two outcomes:

          rule == "hold"  -> post NO exit. Set strategy="hold"; the position is
            left net-open so Bug 4's settlement chokepoint (WS lifecycle / REST
            safety-net / BBO backstop -> process_settlement) closes it at
            settlement. (P0 #1, #4.)
          rule == "exit"  -> post a resting sell at min(fill+band_x, cap),
            sized to the filled qty, after clearing any stray sells. (P0 #4.)

        Highest-risk surface (inventory #8c, checklist P0). Bug 4 paths are NOT
        touched here -- a hold position simply never gets an exit order, and
        arrives at the same chokepoint it would have via an exit-fill."""
        pos.phase = "active"
        cell_id = self.cell_lookup(pos.category, fill_price)
        band_x, rule = self.exit_rule_for(pos.category, fill_price)
        pos.exit_cell_id = cell_id

        # Clear any stray resting sells (idempotent; fresh fill normally has none)
        if pos.exit_order_id:
            await self.cancel_order(tk, pos.exit_order_id, "v4_exit_reset")
            pos.exit_order_id = ""
        existing = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
        for o in (existing or {}).get("orders", []):
            if o.get("action") == "sell":
                await self.cancel_order(tk, o.get("order_id", ""), "v4_exit_reset_stray")

        if rule == "hold":
            pos.strategy = "hold"
            pos.exit_band_x = None
            self._log("hold_to_settle", {
                "cell_id": cell_id, "entry_price": fill_price,
                "regime": pos.regime_at_posting, "category": pos.category,
                "entry_mode": pos.entry_mode, "qty": filled,
                "expected_settle_note": "Bug4 chokepoint closes at settlement",
            }, ticker=tk)
            return

        # exit at +X
        pos.strategy = "exit"
        pos.exit_band_x = band_x
        exit_target = min(fill_price + band_x, EXIT_PRICE_CAP)
        pos.exit_price = exit_target
        book = self.books.get(tk)
        depth_at_target = book.asks.get(exit_target, 0) if book else 0

        oid, resp = await self.place_order(tk, "sell", "yes", exit_target, filled)
        if not oid:
            await asyncio.sleep(1)
            oid, resp = await self.place_order(tk, "sell", "yes", exit_target, filled)
        if not oid:
            self._log("v4_exit_fatal", {
                "exit_price": exit_target, "qty": filled,
            }, ticker=tk)
        pos.exit_order_id = oid
        self._log("v4_exit_posted", {
            "exit_price": exit_target, "band_x": band_x, "cell_id": cell_id,
            "entry_price": fill_price, "qty": filled,
            "depth_at_exit": depth_at_target, "depth_floor": self.exit_depth_floor,
            "depth_ok": depth_at_target >= self.exit_depth_floor,
            "order_id": oid,
        }, ticker=tk)

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
                filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))

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

                    # v4 exit application (STEP 7): hold-skip or exit-at-+X from
                    # the adaptive exit band table. Bypasses the legacy
                    # re-classify / exit_cents / DCA block entirely.
                    if pos.is_v4:
                        await self._v4_apply_exit(tk, pos, fill_price, filled)
                        self._save_v4_resting()
                        continue

                    # Re-classify cell based on fill_price (may differ from anchor)
                    old_cell = pos.cell_name
                    old_exit_cents = pos.cell_cfg.get("exit_cents", 0) if pos.cell_cfg else 0
                    fill_cell, fill_cell_cfg = self._legacy_cell_lookup(pos.category, pos.direction, fill_price)
                    if fill_cell != old_cell:
                        if fill_cell_cfg is None:
                            fill_cell_cfg = {"exit_cents": 15, "strategy": pos.cell_cfg.get("strategy", "noDCA")}
                            self._log("cell_drift_to_inactive", {
                                "old_cell": old_cell, "new_cell": fill_cell,
                                "anchor_price": pos.entry_price, "fill_price": fill_price,
                                "drift_cents": pos.entry_price - fill_price,
                                "old_exit_cents": old_exit_cents, "new_exit_cents": 15,
                                "direction": pos.direction,
                            }, ticker=tk)
                        else:
                            self._log("cell_reclassified", {
                                "old_cell": old_cell, "new_cell": fill_cell,
                                "anchor_price": pos.entry_price, "fill_price": fill_price,
                                "drift_cents": pos.entry_price - fill_price,
                                "old_exit_cents": old_exit_cents,
                                "new_exit_cents": fill_cell_cfg["exit_cents"],
                                "direction": pos.direction,
                            }, ticker=tk)
                        pos.cell_name = fill_cell
                        pos.cell_cfg = fill_cell_cfg

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
                    filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))
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
                    filled = int(float(order.get("fill_count_fp", order.get("count_filled", 0)) or 0))
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
    async def poll_settlements_rest(self):
        """Bug 4 §6.3: catch any settlements missed via WS. Idempotent --
        process_settlement short-circuits on pos.settled. LIVE MODE ONLY --
        never called when _PAPER_API is set (defensive guard at top in case a
        caller forgets the cadence gate; the real-account settlement history
        would otherwise falsely settle paper positions)."""
        if _PAPER_API is not None:
            return  # paper mode: WS lifecycle is the only settlement source
        min_ts = getattr(self, "_last_settlement_min_ts", 0) or (time.time() - 86400)
        path = "/trade-api/v2/portfolio/settlements?min_ts=%d&limit=100" % int(min_ts)
        data = await api_get(self.session, self.ak, self.pk, path, self.rl)
        for s in (data or {}).get("settlements", []):
            # market_result -> integer cents, normalized at the call site (decision c).
            result = s.get("market_result", "")
            if result == "yes":
                settle_val_cents = 100
            elif result == "no":
                settle_val_cents = 0
            elif result == "scalar":
                settle_val_cents = max(0, min(100, int(s.get("value") or 0)))
            elif result == "void":
                # decision b: skip + log, manual reconciliation. No auto-settle.
                self._log("settlement_void_manual",
                          {"source": "rest_poll"}, ticker=s.get("ticker"))
                continue
            else:
                self._log("rest_settlement_unknown_result",
                          {"result": result, "ticker": s.get("ticker")})
                continue
            # settled_time is RFC3339, not epoch -> parse.
            settled_time_str = s.get("settled_time", "")
            try:
                settled_ts = datetime.fromisoformat(
                    settled_time_str.replace("Z", "+00:00")).timestamp()
            except (TypeError, ValueError, AttributeError):
                settled_ts = time.time()
            self.process_settlement(
                ticker=s.get("ticker", ""),
                settle_val_cents=settle_val_cents,
                settled_ts=settled_ts,
                source="rest_poll",
            )
        self._last_settlement_min_ts = time.time() - 60  # 60s overlap to avoid edge gaps

    def process_settlement(self, ticker, settle_val_cents, settled_ts, source):
        """Bug 4 §6.4: single chokepoint for all three settlement sources
        (WS, REST, BBO). Routes paper vs live based on module-level _PAPER_API.
        settle_val_cents is integer cents 0-100, already normalized at the call
        site (decision c removed the central _normalize_settle_value)."""
        settle_val = max(0, min(100, int(settle_val_cents)))  # defensive clamp only

        if _PAPER_API is not None:
            # Paper mode: mutate PaperPosition, emit paper_settled
            ppos = _PAPER_API.paper_positions.get(ticker)
            if not ppos or ppos.settled:
                return  # idempotent
            ppos.settled = True
            ppos.settlement_price = settle_val
            ppos.last_event_ts = settled_ts

            # Realized P&L at settlement -- full double-entry form (v3 fix).
            # ASSIGNMENT (not +=) because try_fill only books realized_pnl_cents
            # when net_qty hits zero; a partial-exit position reaching settlement
            # with net_qty > 0 still has realized_pnl_cents == 0 here, so the
            # final P&L must be derived from the totals:
            #   total_revenue_cents already accounts for all prior partial sells
            #   settle_val * net_qty is the payout on remaining unsold contracts
            #   total_cost_cents is everything paid in
            ppos.realized_pnl_cents = (
                ppos.total_revenue_cents
                - ppos.total_cost_cents
                + settle_val * ppos.net_qty
            )

            # Silent short-circuit: mark self.positions mirror as settled so
            # check_settlements stops re-iterating on subsequent cycles.
            # No event emitted -- paper_settled (below) is the source of truth.
            if ticker in self.positions:
                self.positions[ticker].settled = True
                self.positions[ticker].phase = "settled"

            _PAPER_API._emit("paper_settled", {
                "settle_price": settle_val,
                "settle_source": source,
                "settled_ts": settled_ts,
                "qty": ppos.qty,
                "sold_qty": ppos.sold_qty,
                "net_qty_at_settlement": ppos.net_qty,
                "avg_entry_price": ppos.avg_price,
                "realized_pnl_cents": ppos.realized_pnl_cents,
            }, ticker=ticker)

            # Cleanup: cancel resting paper orders via dispatch (handle_delete -> paper)
            for oid in list(ppos.open_buy_orders) + list(ppos.open_sell_orders):
                asyncio.create_task(self.cancel_order(ticker, oid, "settlement_cleanup"))
            return

        # ---- Live mode ----
        pos = self.positions.get(ticker)
        if not pos or pos.settled:
            return  # idempotent
        if pos.phase not in ("active", "entry_pending"):
            self._log("settlement_unexpected_phase", {
                "phase": pos.phase, "source": source,
            }, ticker=ticker)

        pnl = (settle_val - pos.entry_price) * pos.entry_qty
        if pos.dca_qty > 0:
            pnl += (settle_val - pos.dca_price) * pos.dca_qty
        pos.pnl_cents = pnl
        pos.settled = True
        pos.phase = "settled"
        self.n_settlements += 1

        self._log("settled", {
            "settle": "WIN" if settle_val >= 50 else "LOSS",
            "settle_price": settle_val,
            "settle_source": source,             # ws_lifecycle | rest_poll | bbo_threshold_*
            "settled_ts": settled_ts,
            "pnl_cents": pnl,
            "pnl_dollars": pnl / 100.0,
            "entry_price": pos.entry_price,
            "had_dca": pos.dca_qty > 0,
        }, ticker=ticker)

        # Cleanup: cancel any resting orders for this ticker
        if pos.exit_order_id:
            asyncio.create_task(self.cancel_order(ticker, pos.exit_order_id, "settlement_cleanup"))
        if pos.dca_order_id:
            asyncio.create_task(self.cancel_order(ticker, pos.dca_order_id, "settlement_cleanup"))
        if pos.cell_exit_order_id:
            asyncio.create_task(self.cancel_order(ticker, pos.cell_exit_order_id, "settlement_cleanup"))

    def check_settlements(self):
        """Bug 4 §6.5: BBO threshold backstop. Iterates the appropriate position
        dict based on _PAPER_API and routes via process_settlement (which
        dispatches paper/live). Passes literal cents (yes=100, no=0)."""
        if _PAPER_API is not None:
            # Paper mode: iterate paper_positions
            for tk, ppos in list(_PAPER_API.paper_positions.items()):
                if ppos.settled or ppos.net_qty <= 0:
                    continue
                book = self.books.get(tk)
                if not book:
                    continue
                if book.best_bid >= 98:
                    self.process_settlement(tk, 100, time.time(), source="bbo_threshold_yes")
                elif book.best_ask <= 2:
                    self.process_settlement(tk, 0, time.time(), source="bbo_threshold_no")
            return

        # Live mode: iterate self.positions (current behavior)
        for tk, pos in list(self.positions.items()):
            if pos.settled or pos.phase != "active":
                continue
            book = self.books.get(tk)
            if not book:
                continue
            if book.best_bid >= 98:
                self.process_settlement(tk, 100, time.time(), source="bbo_threshold_yes")
            elif book.best_ask <= 2:
                self.process_settlement(tk, 0, time.time(), source="bbo_threshold_no")

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

    def _resolve_anchor(self, tk, et):
        """Resolve anchor price via priority chain: FV aggregate > Kalshi mid > Kalshi last-traded."""
        book = self.books.get(tk)

        # Priority A: FV aggregate (>=2 sources, age < 600s)
        side_fv = self._get_side_fv(tk, et)
        if side_fv and side_fv.get("fv_cents") and side_fv.get("num_books", 0) >= 2:
            age = side_fv.get("age_sec", 9999)
            if age < 600:
                return side_fv["fv_cents"], "fv_aggregate", side_fv

        # Priority B: Kalshi mid (spread <= 1c, valid bids)
        if book and book.best_bid > 0 and book.best_ask < 100:
            spread = book.best_ask - book.best_bid
            if spread <= 1:
                mid = (book.best_bid + book.best_ask) / 2.0
                return mid, "kalshi_mid", None

        # Priority C: Kalshi last-traded (age < 900s, spread <= 2c)
        if book and book.last_trade_price > 0 and book.last_trade_ts > 0:
            trade_age = time.time() - book.last_trade_ts
            if trade_age < 900 and book.best_bid > 0 and book.best_ask < 100:
                spread = book.best_ask - book.best_bid
                if spread <= 2:
                    return book.last_trade_price, "kalshi_last_traded", None

        # Priority D: FV with single source (spread <= 2c gate)
        if side_fv and side_fv.get("fv_cents") and side_fv.get("age_sec", 9999) < 1800:
            if book and book.best_bid > 0 and book.best_ask < 100:
                spread_d = book.best_ask - book.best_bid
                if spread_d <= 2:
                    return side_fv["fv_cents"], "fv_single", side_fv
                else:
                    self._log("fv_single_spread_gate", {"spread": spread_d, "fv_cents": side_fv["fv_cents"]}, ticker=tk)
            # No book or degenerate → skip fv_single

        return None, "no_anchor", None

    def round5_detector_fire(self, ticker, current_ask, target_bid):
        # TODO: Implement the 2-of-4 composite per bid_laying_policy_v1.md Section 5
        # (volume burst + bilateral taker flow + BBO velocity + distortion spike).
        # When it fires AND current_ask <= target_bid + 5c, cross immediately
        # (Round-6 Stage-3 velocity override); when it fires AND ask > target+5c,
        # the spread is pathological -> hold (do NOT cross).
        # Currently stubbed False -- the static placement is never overridden.
        # Reusable components for the real build (per live_v3_v4_inventory #6b):
        #   volume-burst    -> VolumeTracker rolling counts
        #   bilateral taker -> taker_side mix (book.last_trade_side)
        #   BBO velocity    -> tennis_stb.py capture_depth_snapshot deltas
        #   distortion      -> arb_executor_ws.py ~628 combined yes+no > $1
        # Follow-up patch (production week 1).
        return False

    async def routing_tick(self):
        """Periodic backstop sweep over all events. Placement is now primarily
        event-driven (on_bbo_update, one event per BBO message); this slow sweep
        runs on a 60s main-loop cadence -- OFF the 1s hot path -- only to catch
        legs whose placement_minute opens while their book is quiet (no BBO
        update to trigger on_bbo_update). Per-event reentrancy is guarded inside
        _route_event so the sweep and on_bbo_update never double-place."""
        now = time.time()
        for et, tickers in list(self.event_tickers.items()):
            # Yield after every event so a long sweep never blocks the loop /
            # WS keepalive. No delay -- sleep(0) yields control only.
            await asyncio.sleep(0)
            await self._route_event(et, tickers, now)

    async def _route_event(self, et, tickers, now):
        """Route ONE event (both legs) to v4 bid-laying placement. Invoked from
        on_bbo_update (per-ticker hot path) and routing_tick (periodic backstop).
        Bounded to a single event so the loop is never blocked across the full
        ticker universe. Logic is byte-identical to the pre-restructure per-event
        body -- only the invocation pattern changed. The reentrancy guard
        serializes the two callers so they cannot double-place the same event."""
        if et in self._event_routing:
            return
        self._event_routing.add(et)
        try:
            if et in self.processed_events:
                return

            start_ts = self.event_start_time.get(et)

            # No schedule match yet
            if start_ts is None:
                cycles = self.event_unmatched_cycles.get(et, 0)
                open_ts = self.event_open_time.get(et, now)
                open_age = now - open_ts
                if cycles >= UNMATCHED_SKIP_CYCLES and open_age > UNMATCHED_SKIP_AGE:
                    self._log("skipped", {"reason": "schedule_gap", "event": et,
                        "unmatched_cycles": cycles, "open_age_sec": round(open_age)})
                return

            time_to_start = start_ts - now

            if time_to_start > 86400:
                return

            if time_to_start <= 0:
                self.processed_events.add(et)
                self._save_processed()
                self._log("skipped", {"reason": "match_already_started", "event": et,
                    "time_to_start_sec": round(time_to_start),
                    "start_time": datetime.fromtimestamp(start_ts, tz=ET).strftime("%b %d %I:%M %p ET")})
                return

            if time_to_start <= ENTRY_BUFFER_SEC:
                self.processed_events.add(et)
                self._save_processed()
                self._log("skipped", {"reason": "inside_buffer", "event": et,
                    "time_to_start_sec": round(time_to_start),
                    "start_time": datetime.fromtimestamp(start_ts, tz=ET).strftime("%b %d %I:%M %p ET")})
                return

            # v4: coarse event-level gate only. The fine-grained per-leg
            # placement timing (post at T-placement_minute for that leg's
            # regime) lives in the side loop below. Earliest placement in the
            # v2 table is T-240m, so don't even evaluate sides before T-4h.
            # (Legacy FV path keeps its intel-window gate when enabled.)
            if self.fv_scenarios_enabled:
                intel_window = _entry_lead_cap(et)
                if INTELLIGENCE_AVAILABLE:
                    try:
                        tk0 = list(tickers)[0] if tickers else ""
                        if tk0:
                            intel_rec = recommended_window_seconds(et, tk0)
                            intel_window = intel_rec["window_seconds"]
                            if intel_window == 0:
                                return
                    except Exception:
                        pass
                if time_to_start > intel_window:
                    return
            else:
                if time_to_start > V4_MAX_PLACEMENT_SEC:
                    return

            tk_list = list(tickers)
            if len(tk_list) < 2:
                return
            all_have_bbo = all(tk in self.books and self.books[tk].updated > now - BOOK_STALENESS_SEC for tk in tk_list)
            if not all_have_bbo:
                self._log("event_skip_stale_book", {
                    "event": et,
                    "book_ages_sec": [int(now - self.books[tk].updated) for tk in tk_list if tk in self.books],
                    "missing_books": [tk[-20:] for tk in tk_list if tk not in self.books],
                })
                return

            self.n_matches_seen += 1

            sides = self.identify_sides(et)
            if not sides:
                self.n_skips += 1
                self._log("skipped", {"reason": "no_valid_sides", "event": et})
                return

            for (tk, direction, cat) in sides:
                if tk in self.positions:
                    continue
                if tk in self.inflight_orders:
                    continue

                book = self.books.get(tk)
                if not book or book.updated < now - BOOK_STALENESS_SEC:
                    self._log("side_skip_stale_book", {
                        "book_age_sec": int(now - book.updated) if book else "missing",
                    }, ticker=tk)
                    continue

                # Universal anti-degenerate guard
                if book.best_bid <= 0 or book.best_ask >= 100 or book.best_bid >= book.best_ask:
                    self._log("skipped", {"reason": "degenerate_book_skip", "event": et,
                        "bid": book.best_bid, "ask": book.best_ask}, ticker=tk)
                    continue

                # ---- Dispatch: legacy FV A/B/C scenarios (gated) vs v4 ----
                if self.fv_scenarios_enabled:
                    await self._legacy_route_side(tk, et, direction, cat,
                                                  book, time_to_start, start_ts, now)
                    continue

                # ===== v4 bid-laying placement (STEP 4) =====
                if cat not in self.categories_enabled:
                    continue

                # Marshall the current Kalshi yes-price from the book at decision
                # time (v4 cell = current price, NOT FV).
                cur_mid = (book.best_bid + book.best_ask) / 2.0
                current_price = int(round(cur_mid))
                regime = self.regime_lookup(cat, current_price)
                ekey = (cat, regime)
                if ekey not in self.entry_table:
                    self.n_skips += 1
                    self._log("skipped", {"reason": "no_entry_table_row",
                        "cat": cat, "regime": regime, "price": current_price}, ticker=tk)
                    continue
                placement_min, offset, exp_fill, exp_roi = self.entry_table[ekey]

                # Per-leg placement timing: wait until this leg's regime window
                # opens (post at T-placement_minute). Event is NOT marked
                # processed, so the next tick re-evaluates this leg.
                if time_to_start > placement_min * 60:
                    continue

                current_ask = book.best_ask
                target_bid = max(1, current_price - offset)
                force_cross = self.round5_enabled and self.round5_detector_fire(
                    tk, current_ask, target_bid)

                # Execution branch (Section 4) with late-discovery / T-20m
                # fallback folded in.
                if time_to_start <= V4_T20M_SEC:
                    # At/after T-20m -> atlas baseline taker (the +8.70% floor).
                    entry_price, post_only, entry_mode = current_ask, False, "miss_fallback"
                elif target_bid >= current_ask or force_cross:
                    # MARKETABLE TAKER: lift the ask, pay the 1c taker fee.
                    entry_price, post_only, entry_mode = current_ask, False, "marketable_taker"
                else:
                    # RESTING MAKER limit buy at target_bid; manage to T-20m.
                    entry_price, post_only, entry_mode = target_bid, True, "resting_maker"

                if entry_price <= 0 or entry_price >= 100:
                    continue

                # Pre-post guards: existing resting order / open position.
                existing = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
                if existing and existing.get("orders"):
                    self._log("skipped", {"reason": "resting_order_exists",
                        "ticker": tk, "existing_count": len(existing["orders"])}, ticker=tk)
                    continue
                existing_pos = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&settlement_status=unsettled" % tk, self.rl)
                if existing_pos:
                    if any(int(float(p.get("position_fp", 0))) > 0
                           for p in existing_pos.get("market_positions", [])):
                        self._log("skipped", {"reason": "position_exists", "ticker": tk}, ticker=tk)
                        continue

                self._log("v4_place", {
                    "event": et, "direction": direction, "cat": cat,
                    "regime": regime, "current_price": current_price,
                    "offset": offset, "target_bid": target_bid,
                    "current_ask": current_ask, "entry_price": entry_price,
                    "entry_mode": entry_mode, "post_only": post_only,
                    "placement_minute": placement_min,
                    "min_before_start": round(time_to_start / 60),
                    "exp_fill_rate": round(exp_fill, 3), "exp_net_roi_pct": round(exp_roi, 2),
                }, ticker=tk)

                self.inflight_orders.add(tk)
                try:
                    oid, resp = await self.place_order(tk, "buy", "yes", entry_price,
                                                       self.entry_size, post_only=post_only)
                finally:
                    self.inflight_orders.discard(tk)

                pos = Position(
                    ticker=tk, event_ticker=et, category=cat,
                    direction=direction, cell_name="", cell_cfg={},
                    entry_price=entry_price, entry_order_id=oid,
                    entry_posted_ts=now, phase="entry_resting",
                    match_start_ts=start_ts,
                    play_type="v4_" + entry_mode,
                    is_v4=True, regime_at_posting=regime, target_price=target_bid,
                    placement_minute=placement_min, entry_mode=entry_mode,
                    paid_taker_fee=(post_only is False),
                )
                self.positions[tk] = pos
                if entry_mode == "resting_maker":
                    self._save_v4_resting()
        finally:
            self._event_routing.discard(et)

    async def on_bbo_update(self, ticker):
        """Event-driven hot path (tennis_stb pattern): a single ticker's BBO
        changed. Route its event for placement and manage its own resting bid --
        both bounded to one ticker/event so the WS reader (which awaits this
        inline) never blocks long enough to starve the keepalive ping. Wrapped
        so any routing error is logged, never bubbling into ws_reader's
        reconnect path (a routing bug must NOT trigger a WS reconnect)."""
        et = self.ticker_to_event.get(ticker)
        if not et:
            return
        tickers = self.event_tickers.get(et)
        if not tickers:
            return
        try:
            now = time.time()
            # Placement for this ticker's event (bounded to one event; the
            # reentrancy guard makes this safe against the periodic sweep).
            await self._route_event(et, tickers, now)
            # Manage this ticker's own resting bid (move-repost, T-20m fallback)
            # on its own BBO update. validate_resting_buys remains the backstop
            # for quiet books; the per-ticker mgmt guard serializes the two.
            pos = self.positions.get(ticker)
            if (pos and pos.is_v4 and pos.phase == "entry_resting"
                    and pos.entry_order_id):
                book = self.books.get(ticker)
                if book and book.updated >= now - BOOK_STALENESS_SEC:
                    await self._v4_manage_resting(ticker, pos, book, now)
        except Exception as e:
            self._log("on_bbo_update_error",
                      {"error": str(e), "traceback": traceback.format_exc()},
                      ticker=ticker)

    async def _legacy_route_side(self, tk, et, direction, cat, book, time_to_start, start_ts, now):
        """LEGACY FV-anchor A/B/C scenario routing for one side. Fires only when
        config fv_anchor_scenarios_enabled is true (default false). Preserved
        verbatim for emergency rollback. `continue` semantics become `return`."""
        # Resolve anchor
        anchor_value, anchor_source, side_fv = self._resolve_anchor(tk, et)
        if anchor_value is None:
            self.n_skips += 1
            self._log("skipped", {"reason": "no_anchor_available", "event": et}, ticker=tk)
            return

        # Cell assignment from anchor
        anchor_cell, anchor_cell_cfg = self._legacy_cell_lookup(cat, direction, anchor_value)
        if anchor_cell_cfg is None or anchor_cell in self.config.get("disabled_cells", []):
            self.n_skips += 1
            self._log("skipped", {"reason": "fv_cell_not_active",
                "fv_cell": anchor_cell, "fv_cents": round(anchor_value, 1),
                "event": et, "anchor_source": anchor_source}, ticker=tk)
            return

        # Scenario classification
        kalshi_mid = (book.best_bid + book.best_ask) / 2.0
        delta = kalshi_mid - anchor_value
        spread = book.best_ask - book.best_bid
        entry_size = self.config["sizing"]["entry_contracts"]

        if not self.config.get("b_convergence_enabled", True) and delta <= -8:
            delta = 0  # B disabled -> force Scenario C path

        if delta <= -8:
            scenario = "B_take"
            if spread <= 2 and book.best_bid > 0 and book.best_ask < 100 and anchor_source.startswith("fv"):
                entry_price = book.best_ask
                post_only = False
            else:
                scenario = "C_discount"
                entry_price = book.best_bid
                post_only = True
        elif delta > 0:
            scenario = "A_premium"
            if time_to_start > 3600:
                return  # too early for premium entries
            entry_price = book.best_bid
            post_only = True
        else:
            scenario = "C_discount"
            entry_price = book.best_bid
            post_only = True

        if entry_price <= 0 or entry_price >= 100:
            return

        existing = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
        if existing and existing.get("orders"):
            self._log("skipped", {"reason": "resting_order_exists",
                "ticker": tk, "existing_count": len(existing["orders"])}, ticker=tk)
            return
        existing_pos = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/positions?ticker=%s&count_filter=position&settlement_status=unsettled" % tk, self.rl)
        if existing_pos:
            pos_list = existing_pos.get("market_positions", [])
            if any(int(float(p.get("position_fp", 0))) > 0 for p in pos_list):
                self._log("skipped", {"reason": "position_exists", "ticker": tk}, ticker=tk)
                return

        self._log("cell_match", {
            "event": et, "direction": direction, "cell": anchor_cell,
            "scenario": scenario, "anchor_value": round(anchor_value, 1),
            "anchor_source": anchor_source, "kalshi_mid": round(kalshi_mid, 1),
            "delta": round(delta, 1), "spread": spread,
            "entry_price": entry_price, "entry_size": entry_size,
            "post_only": post_only,
            "strategy": anchor_cell_cfg["strategy"],
            "exit_cents": anchor_cell_cfg["exit_cents"],
            "min_before_start": round(time_to_start / 60),
        }, ticker=tk)

        self.inflight_orders.add(tk)
        try:
            oid, resp = await self.place_order(tk, "buy", "yes", entry_price, entry_size, post_only=post_only)
        finally:
            self.inflight_orders.discard(tk)

        pos = Position(
            ticker=tk, event_ticker=et,
            category=self.ticker_category.get(tk, "?"),
            direction=direction, cell_name=anchor_cell, cell_cfg=anchor_cell_cfg,
            entry_price=entry_price, entry_order_id=oid,
            entry_posted_ts=now, phase="entry_resting",
            match_start_ts=start_ts,
            play_type=scenario,
            anchor_source=anchor_source,
            routed_cell=anchor_cell,
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
            kalshi_cell, _ = self._legacy_cell_lookup(pe["cat"], direction, current_price)
            fv_cell, fv_cell_cfg = self._legacy_cell_lookup(pe["cat"], direction, fv_cents)
            gap = current_price - fv_cents
            cell_low = int(fv_cents / 5) * 5
            cell_high = cell_low + 4

            if fv_cell_cfg is None or fv_cell in self.config.get("disabled_cells", []):
                del self.pending_entries[tk]
                continue

            # Intelligence re-query at resolve time — gate only, no size override
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
                entry_size = self.config["sizing"]["entry_contracts"]
            elif current_price < fv_cents:
                play_type = "B_convergence"
                entry_price = int(current_price) + 1
                entry_size = 19
                layered_exit_price = int(fv_cents) - 2
            else:
                play_type = "A_patient"
                entry_price = cell_high
                entry_size = self.config["sizing"]["entry_contracts"]

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
    # ------------------------------------------------------------------
    # v4 resting-bid management + state persistence (STEP 5)
    # ------------------------------------------------------------------
    def _save_v4_resting(self):
        """Persist live v4 resting bids for restart recovery (STEP 5). Holds
        order_id, posted_at, posted_price, target_price, regime_at_posting and
        the fields needed to rebuild the Position. Live mode only; paper mode
        recovers via PaperApi.load_state."""
        if _PAPER_API is not None:
            return
        out = {}
        for tk, pos in self.positions.items():
            if pos.is_v4 and pos.phase == "entry_resting" and pos.entry_order_id:
                out[tk] = {
                    "order_id": pos.entry_order_id,
                    "event_ticker": pos.event_ticker,
                    "category": pos.category,
                    "direction": pos.direction,
                    "posted_at": pos.entry_posted_ts,
                    "posted_price": pos.entry_price,
                    "target_price": pos.target_price,
                    "regime_at_posting": pos.regime_at_posting,
                    "placement_minute": pos.placement_minute,
                    "entry_mode": pos.entry_mode,
                    "match_start_ts": pos.match_start_ts,
                }
        tmp = str(V4_RESTING_FILE) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(out, f)
        os.replace(tmp, str(V4_RESTING_FILE))

    def _load_v4_resting(self):
        """Rebuild v4 resting-bid Positions from the state file on startup.
        Skips tickers already present (reconcile may have linked them)."""
        if _PAPER_API is not None:
            return
        try:
            with open(V4_RESTING_FILE) as f:
                data = json.load(f)
        except (FileNotFoundError, ValueError):
            return
        restored = 0
        for tk, d in data.items():
            if tk in self.positions:
                continue
            self.positions[tk] = Position(
                ticker=tk, event_ticker=d.get("event_ticker", ""),
                category=d.get("category", "?"), direction=d.get("direction", ""),
                cell_name="", cell_cfg={},
                entry_price=int(d.get("posted_price", 0)),
                entry_order_id=d.get("order_id", ""),
                entry_posted_ts=float(d.get("posted_at", 0.0)),
                phase="entry_resting", match_start_ts=float(d.get("match_start_ts", 0.0)),
                play_type="v4_" + d.get("entry_mode", "resting_maker"),
                is_v4=True, regime_at_posting=d.get("regime_at_posting", ""),
                target_price=int(d.get("target_price", 0)),
                placement_minute=int(d.get("placement_minute", 0)),
                entry_mode=d.get("entry_mode", "resting_maker"),
            )
            restored += 1
        if restored:
            self._log("v4_resting_restored", {"count": restored})

    async def _v4_manage_resting(self, tk, pos, book, now):
        """Serialized entry point for v4 resting-bid management. Both
        on_bbo_update (per BBO tick) and validate_resting_buys (120s backstop)
        can call this; the per-ticker guard ensures only one manager runs at a
        time so they cannot race a double cancel/repost or double T-20m take."""
        if tk in self._mgmt_inflight:
            return
        self._mgmt_inflight.add(tk)
        try:
            await self._v4_manage_resting_inner(tk, pos, book, now)
        finally:
            self._mgmt_inflight.discard(tk)

    async def _v4_manage_resting_inner(self, tk, pos, book, now):
        """Manage one v4 resting bid from placement -> T-20m. Maintains
        target_bid (re-classifies regime and re-posts when the current Kalshi
        price moves > 1 cell width from the last placement basis), cancels on a
        degenerate/wide-spread book, and crosses as taker if a re-evaluated
        target becomes marketable. T-20m fallback is handled below (STEP 6)."""
        spread = book.best_ask - book.best_bid
        # Degenerate / wide-spread book: cancel and free the leg for re-entry.
        if spread > 2 or book.best_bid <= 0 or book.best_ask >= 100:
            await self.cancel_order(tk, pos.entry_order_id, "v4_degenerate_cancel")
            self._log("v4_resting_cancel", {"reason": "degenerate_or_wide_spread",
                "spread": spread, "bid": book.best_bid, "ask": book.best_ask}, ticker=tk)
            self._untombstone_entry(tk, pos)
            self._save_v4_resting()
            return

        time_to_start = pos.match_start_ts - now if pos.match_start_ts > 0 else 99999

        # T-20m taker fallback (STEP 6): if the bid is still unfilled at T-20m,
        # cross as a taker at the current ask. This IS the atlas baseline entry
        # -- the +8.70% floor -- so the strategy can never underperform it. Pay
        # the 1c taker fee (by design). Fires once; after crossing, entry_mode is
        # miss_fallback and we just wait for the taker fill.
        if time_to_start <= V4_T20M_SEC and pos.entry_mode != "miss_fallback":
            old = await api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
            if old:
                old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
                if old_filled > 0:
                    return  # filled as maker before the deadline -- let check_fills book it
            await self.cancel_order(tk, pos.entry_order_id, "v4_t20m_fallback")
            self.inflight_orders.add(tk)
            try:
                oid, _ = await self.place_order(tk, "buy", "yes", book.best_ask,
                                                self.entry_size, post_only=False)
            finally:
                self.inflight_orders.discard(tk)
            pos.entry_price = book.best_ask
            pos.entry_order_id = oid
            pos.entry_mode = "miss_fallback"
            pos.play_type = "v4_miss_fallback"
            pos.paid_taker_fee = True
            self._log("v4_t20m_fallback", {
                "take_price": book.best_ask, "target_was": pos.target_price,
                "regime": pos.regime_at_posting,
                "time_to_start_min": round(time_to_start / 60, 1),
            }, ticker=tk)
            self._save_v4_resting()
            return

        # Significant-move re-post (cadence-gated 60s). "Significant" = the
        # current Kalshi price has moved > V4_REPRICE_MOVE_CENTS (5c = 1 cell
        # width) from the price basis at the last placement. Heuristic --
        # surfaced for operator review.
        if now - pos.last_cancel_repost_ts < 60:
            return
        offset_at_post = self.entry_table.get((pos.category, pos.regime_at_posting), (0, 0, 0, 0))[1]
        price_basis = pos.target_price + offset_at_post  # current price when last placed
        current_price = int(round((book.best_bid + book.best_ask) / 2.0))
        if abs(current_price - price_basis) <= V4_REPRICE_MOVE_CENTS:
            return

        # Re-classify regime and recompute the target at the new price.
        new_regime = self.regime_lookup(pos.category, current_price)
        row = self.entry_table.get((pos.category, new_regime))
        if row is None:
            return
        _, new_offset, _, _ = row
        new_target = max(1, current_price - new_offset)
        current_ask = book.best_ask

        # Cancel the old bid, but first check it didn't just fill.
        old = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
        if old:
            old_filled = int(float((old.get("order", old).get("fill_count_fp", 0)) or 0))
            if old_filled > 0:
                # Fill happened -- let check_fills book it on its next pass.
                return
        await self.cancel_order(tk, pos.entry_order_id, "v4_move_repost")

        if new_target >= current_ask:
            # Re-evaluated target is now marketable -> cross as taker.
            self.inflight_orders.add(tk)
            try:
                oid, _ = await self.place_order(tk, "buy", "yes", current_ask,
                                                self.entry_size, post_only=False)
            finally:
                self.inflight_orders.discard(tk)
            pos.entry_price = current_ask
            pos.entry_order_id = oid
            pos.entry_mode = "marketable_taker"
            pos.play_type = "v4_marketable_taker"
            pos.paid_taker_fee = True
            mode = "cross_on_move"
        else:
            self.inflight_orders.add(tk)
            try:
                oid, _ = await self.place_order(tk, "buy", "yes", new_target,
                                                self.entry_size, post_only=True)
            finally:
                self.inflight_orders.discard(tk)
            pos.entry_price = new_target
            pos.entry_order_id = oid
            pos.entry_mode = "resting_maker"
            pos.play_type = "v4_resting_maker"
            mode = "repost_resting"
        pos.target_price = new_target
        pos.regime_at_posting = new_regime
        pos.last_cancel_repost_ts = now
        self._log("v4_move_repost", {
            "mode": mode, "old_basis": price_basis, "current_price": current_price,
            "new_regime": new_regime, "new_offset": new_offset,
            "new_target": new_target, "current_ask": current_ask,
            "move_cents": current_price - price_basis,
        }, ticker=tk)
        self._save_v4_resting()

    async def validate_resting_buys(self):
        """Cadence-gated cancel/repost for resting entry orders + deadline force-take."""
        now = time.time()
        for tk, pos in list(self.positions.items()):
            if pos.phase != "entry_resting" or not pos.entry_order_id:
                continue

            book = self.books.get(tk)
            if not book or book.updated < now - BOOK_STALENESS_SEC:
                self._log("validate_skip_stale_book", {
                    "book_age_sec": int(now - book.updated) if book else "missing",
                }, ticker=tk)
                continue

            # v4 resting bids are managed by the v4 manager (target-bid based,
            # not best-bid reprice / FV-anchor freshness).
            if pos.is_v4:
                await self._v4_manage_resting(tk, pos, book, now)
                continue

            # Legacy positions skip validation
            if pos.legacy:
                continue

            time_to_start = pos.match_start_ts - now if pos.match_start_ts > 0 else 99999
            spread = book.best_ask - book.best_bid

            # Immediate cancel conditions (no cadence gate)
            if spread > 2 or book.best_bid <= 0 or book.best_ask >= 100:
                await self.cancel_order(tk, pos.entry_order_id, "degenerate_cancel")
                self._log("stale_buy_cancel", {"reason": "degenerate_or_wide_spread",
                    "spread": spread, "bid": book.best_bid, "ask": book.best_ask}, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            # Cancel if our price is far above current mid (falling knife protection)
            mid = (book.best_bid + book.best_ask) / 2.0
            if pos.entry_price > mid + STALE_BUY_DELTA:
                await self.cancel_order(tk, pos.entry_order_id, 'stale_buy_price_too_high')
                self._log('stale_buy_cancel', {
                    'reason': 'price_above_mid',
                    'our_price': pos.entry_price,
                    'current_mid': round(mid, 1),
                    'delta': round(pos.entry_price - mid, 1),
                }, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            # Check anchor freshness — cancel if expired
            anchor_value, anchor_source, _ = self._resolve_anchor(tk, pos.event_ticker)
            if anchor_value is None:
                await self.cancel_order(tk, pos.entry_order_id, "anchor_expired")
                self._log("stale_buy_cancel", {"reason": "anchor_expired"}, ticker=tk)
                self._untombstone_entry(tk, pos)
                continue

            # Deadline force-take at T-16 min
            if 955 <= time_to_start <= 965:
                kalshi_mid = (book.best_bid + book.best_ask) / 2.0
                if kalshi_mid < anchor_value and spread <= 2 and book.best_bid > 0 and book.best_ask < 100:
                    await self.cancel_order(tk, pos.entry_order_id, "deadline_force_take")
                    self.inflight_orders.add(tk)
                    try:
                        oid, _ = await self.place_order(tk, "buy", "yes", book.best_ask,
                            self.config["sizing"]["entry_contracts"], post_only=False)
                    finally:
                        self.inflight_orders.discard(tk)
                    pos.entry_price = book.best_ask
                    pos.entry_order_id = oid
                    pos.play_type = "deadline_force_take"
                    self._log("deadline_force_take", {
                        "old_price": pos.entry_price, "take_price": book.best_ask,
                        "anchor": round(anchor_value, 1), "kalshi_mid": round(kalshi_mid, 1),
                        "time_to_start": round(time_to_start),
                    }, ticker=tk)
                    continue

            # Cadence-gated cancel/repost
            cadence = 60
            if now - pos.last_cancel_repost_ts < cadence:
                continue

            # Reprice to current best_bid if different
            target = book.best_bid
            if target != pos.entry_price and target > 0 and target < 100:
                await self.cancel_order(tk, pos.entry_order_id, "cadence_repost")
                # Check if old order filled before placing replacement
                old_order = await api_get(self.session, self.ak, self.pk,
                    "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id, self.rl)
                if old_order:
                    old_filled = int(float((old_order.get("order", old_order).get("fill_count_fp", 0)) or 0))
                    if old_filled > 0:
                        pos.entry_qty = old_filled
                        pos.phase = "active"
                        pos.entry_filled_ts = time.time()
                        # Re-classify cell based on fill price
                        old_cell = pos.cell_name
                        old_exit_cents = pos.cell_cfg.get("exit_cents", 0) if pos.cell_cfg else 0
                        fill_cell, fill_cell_cfg = self._legacy_cell_lookup(pos.category, pos.direction, pos.entry_price)
                        if fill_cell != old_cell:
                            if fill_cell_cfg is None:
                                fill_cell_cfg = {"exit_cents": 15, "strategy": pos.cell_cfg.get("strategy", "noDCA")}
                                self._log("cell_drift_to_inactive", {
                                    "old_cell": old_cell, "new_cell": fill_cell,
                                    "anchor_price": pos.entry_price, "fill_price": pos.entry_price,
                                    "drift_cents": 0,
                                    "old_exit_cents": old_exit_cents, "new_exit_cents": 15,
                                    "direction": pos.direction,
                                }, ticker=tk)
                            else:
                                self._log("cell_reclassified", {
                                    "old_cell": old_cell, "new_cell": fill_cell,
                                    "anchor_price": pos.entry_price, "fill_price": pos.entry_price,
                                    "drift_cents": 0,
                                    "old_exit_cents": old_exit_cents,
                                    "new_exit_cents": fill_cell_cfg["exit_cents"],
                                    "direction": pos.direction,
                                }, ticker=tk)
                            pos.cell_name = fill_cell
                            pos.cell_cfg = fill_cell_cfg
                        self._log("cadence_repost_fill_detected", {
                            "filled_qty": old_filled, "price": pos.entry_price,
                        }, ticker=tk)
                        continue
                self.inflight_orders.add(tk)
                try:
                    oid, _ = await self.place_order(tk, "buy", "yes", target,
                        self.config["sizing"]["entry_contracts"])
                finally:
                    self.inflight_orders.discard(tk)
                old = pos.entry_price
                pos.entry_price = target
                pos.entry_order_id = oid
                pos.last_cancel_repost_ts = now
                self._log("cadence_repost", {
                    "old_price": old, "new_price": target,
                    "anchor": round(anchor_value, 1), "cadence_sec": cadence,
                    "time_to_start_min": round(time_to_start / 60),
                }, ticker=tk)

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
    async def _v4_reconcile_naked(self, tk, et, cat, avg, pinfo):
        """v4 restart recovery for a naked open position (no resting sell):
        re-post the exit-band sell, or -- for a hold cell -- leave it naked and
        tracked so Bug 4 closes it at settlement (STEP 7 / P0 #4)."""
        qty = pinfo["qty"]
        cell_id = self.cell_lookup(cat, avg)
        band_x, rule = self.exit_rule_for(cat, avg)
        base = dict(
            ticker=tk, event_ticker=et, category=cat, direction="",
            cell_name="", cell_cfg={}, entry_price=avg, entry_qty=qty,
            phase="active", entry_filled_ts=time.time(),
            is_v4=True, exit_cell_id=cell_id, play_type="v4_reconciled",
        )
        if rule == "hold":
            self.positions[tk] = Position(**base, strategy="hold", exit_band_x=None)
            self._log("reconcile_v4_hold", {
                "cell_id": cell_id, "avg": avg, "qty": qty}, ticker=tk)
            return
        exit_target = min(avg + band_x, EXIT_PRICE_CAP)
        fresh = await api_get(self.session, self.ak, self.pk,
            "/trade-api/v2/portfolio/orders?ticker=%s&status=resting" % tk, self.rl)
        fresh_sells = [o for o in (fresh or {}).get("orders", []) if o.get("action") == "sell"]
        if fresh_sells:
            sp = round(float(fresh_sells[0].get("yes_price_dollars", "0")) * 100)
            self.positions[tk] = Position(**base, strategy="exit", exit_band_x=band_x,
                exit_price=sp, exit_order_id=fresh_sells[0].get("order_id", ""))
            self._log("reconcile_v4_exit_found", {
                "exit_price": sp, "cell_id": cell_id}, ticker=tk)
            return
        oid, _ = await self.place_order(tk, "sell", "yes", exit_target, qty)
        self.positions[tk] = Position(**base, strategy="exit", exit_band_x=band_x,
            exit_price=exit_target, exit_order_id=oid)
        self._log("reconcile_v4_exit_posted", {
            "exit_price": exit_target, "band_x": band_x, "cell_id": cell_id,
            "qty": qty, "order_id": oid}, ticker=tk)

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

            existing = self.positions.get(tk)
            if existing and existing.entry_price > 0:
                kalshi_avg = pinfo["avg_price"]
                if abs(kalshi_avg - existing.entry_price) > 1:
                    self._log("reconcile_price_mismatch", {
                        "bot_entry_price": existing.entry_price,
                        "kalshi_avg_price": kalshi_avg,
                        "delta": kalshi_avg - existing.entry_price,
                        "entry_qty": existing.entry_qty,
                        "kalshi_qty": pinfo["qty"],
                    }, ticker=tk)
                if pinfo["qty"] > existing.entry_qty:
                    existing.entry_qty = pinfo["qty"]
                if sells and not existing.exit_order_id:
                    existing.exit_order_id = sells[0]["order_id"]
                    existing.exit_price = sells[0]["price"]
                continue

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
                    dca_cell_name, dca_cell_cfg = self._legacy_cell_lookup(cat, direction, avg)
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
                # v4: use the adaptive exit band table (hold-skip aware). Avoids
                # posting an unwanted exit on a hold-cell position after restart.
                if not self.fv_scenarios_enabled and cat in self.categories_enabled:
                    await self._v4_reconcile_naked(tk, et, cat, avg, pinfo)
                    continue
                direction = "leader" if avg > 50 else "underdog"
                if cat:
                    cell_name, cell_cfg = self._legacy_cell_lookup(cat, direction, avg)
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
                    reason = "cell disabled" if cell_name and cell_name in self.config.get("disabled_cells", []) else "no cell config"
                    self._log("reconcile_orphan_no_cell", {
                        "ticker": tk, "avg_price": avg, "cell": cell_name or "?",
                        "reason": reason,
                    }, ticker=tk)

        # Check for orphan resting orders (not matched to any position)
        for tk, orders in ord_map.items():
            if tk not in pos_map:
                # Skip tickers the bot is actively managing in entry_resting phase
                in_memory_pos = self.positions.get(tk)
                if in_memory_pos and in_memory_pos.phase == "entry_resting":
                    continue
                for o in orders:
                    orphan_orders.append((tk, o))

        # Cancel orphan resting buys so bot can re-discover cleanly
        for tk, o in orphan_orders:
            if o["action"] == "buy":
                await self.cancel_order(tk, o["order_id"], "orphan_buy_reconcile_cleanup")
                self._log("orphan_buy_cancelled", {
                    "price": o["price"], "qty": o["qty"],
                }, ticker=tk)

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
        mode = "PAPER" if _PAPER_API is not None else "LIVE - REAL ORDERS"
        print("=" * 70, flush=True)
        print("LIVE V4 - BID-LAYING EXECUTOR - %s" % mode, flush=True)
        print("=" * 70, flush=True)
        print("Config: %s" % CONFIG_PATH, flush=True)
        if self.fv_scenarios_enabled:
            print("Mode: LEGACY FV-anchor scenarios (active=%d disabled=%d)" % (
                len(self.config.get("active_cells", {})),
                len(self.config.get("disabled_cells", []))), flush=True)
        else:
            print("Mode: v4 bid-laying  |  entry rows: %d  |  categories: %s" % (
                len(self.entry_table), ",".join(sorted(self.categories_enabled))), flush=True)
            print("Exit bands/cat: %s" % {c: len(self.exit_table.get(c, {}))
                for c in sorted(self.categories_enabled)}, flush=True)
        print("Entry: %d contracts  Exit: %d contracts" % (self.entry_size, self.exit_size), flush=True)
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

        # v4: rebuild any persisted resting bids reconcile didn't link (STEP 5)
        self._load_v4_resting()

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
            if time_to_start > _entry_lead_cap(evt):
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

        # WS producer/consumer split: ws_reader only enqueues frames; _ws_worker
        # drains + dispatches (parse, book apply, on_bbo_update routing) yielding
        # per message so a snapshot flood can't starve the keepalive ping.
        # _loop_lag_monitor instruments scheduling lag for the cutover gate.
        self._ws_queue = asyncio.Queue(maxsize=WS_QUEUE_MAXSIZE)
        asyncio.create_task(self.ws_reader())
        asyncio.create_task(self._ws_worker())
        asyncio.create_task(self._loop_lag_monitor())

        print("\n[INIT] Waiting 10s for BBO snapshots...", flush=True)
        await asyncio.sleep(10)

        # Paper mode startup: safety check + restore prior state (spec §2.3, §13)
        if _PAPER_API is not None:
            real_pos = await _real_api_get(self.session, self.ak, self.pk,
                "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled",
                self.rl)
            real_positions_count = len((real_pos or {}).get("market_positions", []))
            if real_positions_count > 0:
                self._log("paper_real_orders_blocked", {
                    "real_positions_count": real_positions_count,
                    "action": "abort",
                })
                raise RuntimeError(
                    "paper_mode=true but %d real Kalshi positions exist; close them first"
                    % real_positions_count)
            paper_state_path = "/root/Omi-Workspace/arb-executor/paper_state.json"
            paper_state_max_age = self.config.get("paper_state_max_age_sec", 86400)
            _PAPER_API.load_state(paper_state_path, paper_state_max_age)

        last_discovery = time.time()
        last_fill_check = 0  # force immediate first check_fills
        last_reconcile = time.time()
        last_stale_check = time.time()
        last_summary = time.time()
        last_settlement_poll = 0  # Bug 4 §6.3: force first REST settlements poll early (live only)
        last_routing_sweep = 0    # force first backstop routing sweep immediately at startup

        print("[RUNNING] Main loop started.", flush=True)

        while True:
            try:
                now = time.time()

                # Check settlements via BBO (tier-3 backstop)
                self.check_settlements()

                # Bug 4 §6.3: REST settlements safety-net poll (LIVE ONLY; 5-min cadence).
                # Gated on _PAPER_API is None -- paper mode must NOT poll real-account
                # settlement history (would falsely close paper positions).
                if _PAPER_API is None and now - last_settlement_poll > SETTLEMENT_POLL_INTERVAL:
                    await self.poll_settlements_rest()
                    last_settlement_poll = now

                # Backstop routing sweep (placement is primarily event-driven
                # via on_bbo_update per BBO message). Runs on a slow cadence,
                # OFF the 1s hot path, only to catch legs whose placement window
                # opens while their book is quiet (no BBO update to trigger
                # on_bbo_update). This is what keeps the full-universe iteration
                # from starving the WS keepalive.
                if now - last_routing_sweep > ROUTING_SWEEP_INTERVAL:
                    await self.routing_tick()
                    last_routing_sweep = now

                # Poll fills every 30s
                if now - last_fill_check > FILL_CHECK_INTERVAL:
                    await self.check_fills()
                    if _PAPER_API is not None:
                        _PAPER_API.maybe_heartbeat()
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

                # check_pending_entries disabled — new routing_tick re-evaluates every tick
                # await self.check_pending_entries()

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
