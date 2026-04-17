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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------
BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"
MAX_RPS = 8
MIN_VOLUME = 50
MAX_HOURS_TO_EXPIRY = 12
WS_PING_INTERVAL = 15
WS_SUBSCRIBE_BATCH = 50
DISCOVERY_INTERVAL = 300
ENTRY_CANCEL_TIMEOUT = 1800  # 30 min
FILL_CHECK_INTERVAL = 30     # poll fills every 30s
EXIT_PRICE_CAP = 98           # never post exit above 98c

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

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "deploy_v3.json"
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

        self.positions: Dict[str, Position] = {}
        self.seen_events: Set[str] = set()

        self.n_matches_seen = 0
        self.n_entries = 0
        self.n_skips = 0
        self.n_exits = 0
        self.n_dcas = 0
        self.n_settlements = 0
        self.start_ts = time.time()

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        self.log_path = LOG_DIR / ("live_v3_%s.jsonl" % date_str)
        self.log_file = open(self.log_path, "a")
        self._log("system_start", {"mode": "LIVE", "config_path": str(CONFIG_PATH),
                                    "active_cells": len(self.config["active_cells"]),
                                    "disabled_cells": len(self.config["disabled_cells"]),
                                    "entry_size": self.entry_size,
                                    "dca_size": self.dca_size,
                                    "exit_cap": EXIT_PRICE_CAP})

    def _log(self, event, details=None, ticker=""):
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "ts_epoch": time.time(),
            "event": event,
            "ticker": ticker,
            "details": details or {},
        }
        self.log_file.write(json.dumps(entry) + "\n")
        self.log_file.flush()
        print("[%s] %s %s %s" % (
            datetime.now().strftime("%H:%M:%S"),
            event.upper().ljust(20),
            ticker[:40] if ticker else "",
            json.dumps(details)[:120] if details else ""
        ), flush=True)

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
                    "params": {"channels": ["orderbook_delta"], "market_tickers": batch}}))
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

    async def ws_reader(self):
        while True:
            try:
                if not self.ws_connected or not self.ws:
                    await asyncio.sleep(1)
                    continue
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
                self._log("ws_error", {"error": str(e)})
                self.ws_connected = False
                await asyncio.sleep(2)
                await self.ws_connect()
                if self.ws_connected and self.subscribed:
                    old = list(self.subscribed)
                    self.subscribed.clear()
                    await self.ws_subscribe(old)

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
    async def check_fills(self):
        """Poll Kalshi for fill status on all active orders."""
        for tk, pos in list(self.positions.items()):
            if pos.settled:
                continue

            # Check entry order fill
            if pos.phase == "entry_resting" and pos.entry_order_id:
                now = time.time()
                if now - pos.entry_posted_ts > ENTRY_CANCEL_TIMEOUT:
                    await self.cancel_order(tk, pos.entry_order_id, "entry_timeout_30min")
                    pos.phase = "settled"
                    pos.settled = True
                    self._log("entry_cancelled", {"reason": "timeout_30min"}, ticker=tk)
                    continue

                path = "/trade-api/v2/portfolio/orders/%s" % pos.entry_order_id
                data = await api_get(self.session, self.ak, self.pk, path, self.rl)
                if not data:
                    continue
                order = data.get("order", data)
                status = order.get("status", "")
                filled = int(order.get("count_filled_fp", order.get("count_filled", 0)) or 0)

                if filled > 0 and pos.entry_qty == 0:
                    fill_price_raw = order.get("average_fill_price_fp",
                                               order.get("yes_price", pos.entry_price / 100.0))
                    if isinstance(fill_price_raw, str):
                        fill_price_raw = float(fill_price_raw)
                    fill_price = round(fill_price_raw * 100) if fill_price_raw < 1.5 else int(fill_price_raw)
                    if fill_price <= 0:
                        fill_price = pos.entry_price

                    pos.entry_qty = filled
                    pos.entry_filled_ts = time.time()
                    pos.phase = "active"
                    self.n_entries += 1

                    exit_price = min(fill_price + pos.cell_cfg["exit_cents"], EXIT_PRICE_CAP)
                    pos.exit_price = exit_price

                    self._log("entry_filled", {
                        "fill_price": fill_price,
                        "posted_price": pos.entry_price,
                        "qty": filled,
                        "cell": pos.cell_name,
                        "direction": pos.direction,
                        "kalshi_status": status,
                    }, ticker=tk)

                    # Place exit sell
                    oid, resp = await self.place_order(tk, "sell", "yes", exit_price, filled)
                    pos.exit_order_id = oid
                    self._log("exit_posted", {
                        "exit_price": exit_price,
                        "qty": filled,
                        "based_on_fill": fill_price,
                        "order_id": oid,
                    }, ticker=tk)

                    # Place DCA if applicable
                    if pos.cell_cfg["strategy"] == "DCA-A":
                        dca_trigger = pos.cell_cfg.get("dca_trigger_cents", 0)
                        dca_price = fill_price - dca_trigger
                        if dca_price >= self.dca_fill_floor:
                            pos.dca_price = dca_price
                            dca_oid, dresp = await self.place_order(tk, "buy", "yes", dca_price, self.dca_size)
                            pos.dca_order_id = dca_oid
                            self._log("dca_posted", {
                                "dca_price": dca_price,
                                "qty": self.dca_size,
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
                        # Cancel DCA if still resting
                        if pos.dca_order_id and not pos.dca_filled:
                            await self.cancel_order(tk, pos.dca_order_id, "exit_filled_cancel_dca")

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
    # Routing: cell assignment at post time + real order placement
    # ------------------------------------------------------------------
    async def routing_tick(self):
        now = time.time()
        for et, tickers in self.event_tickers.items():
            if et in self.seen_events:
                continue
            tk_list = list(tickers)
            if len(tk_list) < 2:
                continue
            all_have_bbo = all(
                tk in self.books and self.books[tk].updated > now - 120
                for tk in tk_list
            )
            if not all_have_bbo:
                continue

            self.seen_events.add(et)
            self.n_matches_seen += 1

            sides = self.identify_sides(et)
            if not sides:
                self.n_skips += 1
                self._log("skipped", {"reason": "no_valid_sides", "event": et})
                continue

            for (tk, direction, cat) in sides:
                if tk in self.positions:
                    continue

                book = self.books.get(tk)
                if not book or book.updated < now - 120:
                    continue
                current_mid = (book.best_bid + book.best_ask) / 2.0

                cell_name, cell_cfg = self.cell_lookup(cat, direction, current_mid)

                if cell_name in self.config["disabled_cells"]:
                    self.n_skips += 1
                    self._log("skipped", {
                        "reason": "cell_disabled_at_post_time",
                        "cell": cell_name, "mid_at_post": current_mid, "event": et,
                    }, ticker=tk)
                    continue

                if cell_cfg is None:
                    self.n_skips += 1
                    self._log("skipped", {
                        "reason": "no_cell_config_at_post_time",
                        "cell": cell_name, "mid_at_post": current_mid, "event": et,
                    }, ticker=tk)
                    continue

                entry_price = int(current_mid)

                self._log("cell_match", {
                    "event": et, "direction": direction, "cell": cell_name,
                    "mid_at_post": current_mid, "entry_price": entry_price,
                    "strategy": cell_cfg["strategy"],
                    "exit_cents": cell_cfg["exit_cents"],
                }, ticker=tk)

                # Place REAL entry buy
                oid, resp = await self.place_order(tk, "buy", "yes", entry_price, self.entry_size)

                pos = Position(
                    ticker=tk, event_ticker=et,
                    category=self.ticker_category.get(tk, "?"),
                    direction=direction, cell_name=cell_name, cell_cfg=cell_cfg,
                    entry_price=entry_price, entry_order_id=oid,
                    entry_posted_ts=now, phase="entry_resting",
                )
                self.positions[tk] = pos

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
    # Main loop
    # ------------------------------------------------------------------
    async def run(self):
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

        asyncio.create_task(self.ws_reader())

        print("[INIT] Waiting 10s for BBO snapshots...", flush=True)
        await asyncio.sleep(10)

        last_discovery = time.time()
        last_fill_check = time.time()
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

                # Re-discover every 5 min
                if now - last_discovery > DISCOVERY_INTERVAL:
                    new_tickers = await self.discover_markets()
                    if new_tickers:
                        await self.ws_subscribe(new_tickers)
                    last_discovery = now

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
    bot = LiveV3()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
