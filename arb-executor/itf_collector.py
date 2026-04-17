#!/usr/bin/env python3
"""
itf_collector.py - Research-only ITF men's tick collector.

Subscribes to KXITFMATCH markets via Kalshi WebSocket.
Writes per-ticker CSV tick files to analysis/itf_ticks/.
Writes match_facts rows to analysis/itf_facts.csv.

Does NOT trade. Read-only data collection for offline analysis.
"""

import asyncio
import aiohttp
import base64
import csv
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Set

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE_URL = "https://api.elections.kalshi.com"
WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"
WS_PATH = "/trade-api/ws/v2"
MAX_RPS = 8
WS_PING_INTERVAL = 15
WS_SUBSCRIBE_BATCH = 50
DISCOVERY_INTERVAL = 300

SERIES = "KXITFMATCH"
OUT_DIR = Path(__file__).resolve().parent / "analysis" / "itf_ticks"
FACTS_PATH = Path(__file__).resolve().parent / "analysis" / "itf_facts.csv"

FACTS_FIELDS = [
    "ticker_id", "tour", "event_ticker", "side", "match_result",
    "settlement_price", "open_time_ts", "entry_mid", "entry_bid", "entry_ask",
    "match_low_bid", "match_high_bid", "match_low_mid", "match_high_mid",
    "max_dip_from_entry", "max_bounce_from_entry", "tick_count_live",
]


def load_credentials():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass
    api_key = os.getenv("KALSHI_API_KEY")
    pem_path = Path(__file__).resolve().parent / "kalshi.pem"
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


from collections import deque
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


@dataclass
class TickerState:
    ticker: str
    event_ticker: str
    open_time_ts: float
    csv_file: object = None
    csv_writer: object = None
    tick_count: int = 0
    first_bid: int = 0
    first_ask: int = 0
    first_mid: float = 0.0
    low_bid: int = 999
    high_bid: int = 0
    low_mid: float = 999.0
    high_mid: float = 0.0
    settled: bool = False


class ITFCollector:
    def __init__(self):
        self.ak, self.pk = load_credentials()
        self.rl = RateLimiter()
        self.session = None
        self.ws = None
        self.ws_connected = False

        self.books: Dict[str, Book] = {}
        self.subscribed: Set[str] = set()
        self.msg_id = 0
        self.ticker_to_event: Dict[str, str] = {}
        self.event_tickers: Dict[str, Set[str]] = defaultdict(set)
        self.ticker_states: Dict[str, TickerState] = {}
        self.event_open_times: Dict[str, float] = {}

        OUT_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, msg):
        print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg), flush=True)

    # WS
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
            self.log("WS connected")
            return True
        except Exception as e:
            self.log("WS connect failed: %s" % e)
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
                self.log("WS subscribe error: %s" % e)
        self.log("Subscribed %d new tickers (total %d)" % (len(new), len(self.subscribed)))

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
        self._on_tick(ticker, book)

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
        self._on_tick(ticker, book)

    def _on_tick(self, ticker, book):
        if ticker not in self.ticker_states:
            return
        st = self.ticker_states[ticker]
        if st.settled:
            return
        bid, ask = book.best_bid, book.best_ask
        if bid <= 0 or ask >= 100:
            return
        mid = (bid + ask) / 2.0
        now = time.time()
        ts_offset = int(now - st.open_time_ts)

        # First tick: record entry
        if st.tick_count == 0:
            st.first_bid = bid
            st.first_ask = ask
            st.first_mid = mid

        # Track extremes
        if bid < st.low_bid:
            st.low_bid = bid
        if bid > st.high_bid:
            st.high_bid = bid
        if mid < st.low_mid:
            st.low_mid = mid
        if mid > st.high_mid:
            st.high_mid = mid

        # Write tick to CSV (flush every write — ITF is low-volume)
        if st.csv_writer:
            st.csv_writer.writerow([ts_offset, bid, ask, "%.1f" % mid])
            st.csv_file.flush()
            st.tick_count += 1

        # Detect settlement
        if bid >= 98 or ask <= 2:
            settle = 99 if bid >= 98 else 1
            self._finalize(ticker, settle)

    def _finalize(self, ticker, settle_price):
        st = self.ticker_states.get(ticker)
        if not st or st.settled:
            return
        st.settled = True
        if st.csv_file:
            st.csv_file.flush()
            st.csv_file.close()
            st.csv_file = None

        # Determine side
        et = st.event_ticker
        tickers = sorted(self.event_tickers.get(et, set()))
        if len(tickers) == 2:
            bids = []
            for t in tickers:
                s = self.ticker_states.get(t)
                if s:
                    bids.append((t, s.first_bid))
            bids.sort(key=lambda x: -x[1])
            side = "leader" if bids[0][0] == ticker else "underdog"
        else:
            side = "unknown"

        result = "win" if settle_price > 50 else "loss"
        entry_mid = st.first_mid
        dip = entry_mid - st.low_mid if entry_mid > 0 else 0
        bounce = st.high_mid - entry_mid if entry_mid > 0 else 0

        row = {
            "ticker_id": ticker,
            "tour": "ITF",
            "event_ticker": et,
            "side": side,
            "match_result": result,
            "settlement_price": settle_price,
            "open_time_ts": int(st.open_time_ts),
            "entry_mid": "%.1f" % entry_mid,
            "entry_bid": st.first_bid,
            "entry_ask": st.first_ask,
            "match_low_bid": st.low_bid,
            "match_high_bid": st.high_bid,
            "match_low_mid": "%.1f" % st.low_mid,
            "match_high_mid": "%.1f" % st.high_mid,
            "max_dip_from_entry": "%.1f" % dip,
            "max_bounce_from_entry": "%.1f" % bounce,
            "tick_count_live": st.tick_count,
        }
        write_header = not FACTS_PATH.exists()
        with open(FACTS_PATH, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FACTS_FIELDS)
            if write_header:
                w.writeheader()
            w.writerow(row)

        self.log("SETTLED %s %s entry=%.0fc settle=%d ticks=%d dip=%.0f bounce=%.0f" % (
            ticker, result, entry_mid, settle_price, st.tick_count, dip, bounce))

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
                    self.apply_snapshot(msg.get("msg", {}).get("market_ticker", ""),
                                       msg.get("msg", {}))
                elif typ == "orderbook_delta":
                    self.apply_delta(msg.get("msg", {}).get("market_ticker", ""),
                                    msg.get("msg", {}))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.log("WS error: %s" % e)
                self.ws_connected = False
                await asyncio.sleep(2)
                await self.ws_connect()
                if self.ws_connected and self.subscribed:
                    old = list(self.subscribed)
                    self.subscribed.clear()
                    await self.ws_subscribe(old)

    async def discover_markets(self):
        all_tickers = []
        cursor = ""
        for _ in range(10):
            path = "/trade-api/v2/markets?limit=200&status=open&series_ticker=%s" % SERIES
            if cursor:
                path += "&cursor=%s" % cursor
            data = await api_get(self.session, self.ak, self.pk, path, self.rl)
            if not data:
                break
            for m in data.get("markets", []):
                ticker = m["ticker"]
                et = m["event_ticker"]
                self.ticker_to_event[ticker] = et
                self.event_tickers[et].add(ticker)
                ot_str = m.get("open_time", "")
                if ot_str and et not in self.event_open_times:
                    try:
                        self.event_open_times[et] = datetime.fromisoformat(
                            ot_str.replace("Z", "+00:00")).timestamp()
                    except Exception:
                        pass
                # Initialize ticker state and CSV file
                if ticker not in self.ticker_states:
                    ot = self.event_open_times.get(et, time.time())
                    csv_path = OUT_DIR / ("%s.csv" % ticker)
                    is_new = not csv_path.exists() or csv_path.stat().st_size == 0
                    fh = open(csv_path, "a", newline="")
                    w = csv.writer(fh)
                    if is_new:
                        w.writerow(["ts_offset_sec", "bid", "ask", "mid"])
                        fh.flush()
                    self.ticker_states[ticker] = TickerState(
                        ticker=ticker, event_ticker=et,
                        open_time_ts=ot, csv_file=fh, csv_writer=w,
                    )
                    vol = m.get("volume_fp", "0")
                    bid_str = m.get("yes_bid_dollars", "0")
                    ask_str = m.get("yes_ask_dollars", "0")
                    self.log("  NEW: %s bid=%s ask=%s vol=%s" % (ticker[:45], bid_str, ask_str, vol))
                all_tickers.append(ticker)
            cursor = data.get("cursor", "")
            if not cursor:
                break
        self.log("Discovery: %d ITF tickers across %d events" % (
            len(all_tickers), len(self.event_tickers)))
        return all_tickers

    async def run(self):
        print("=" * 60, flush=True)
        print("ITF TICK COLLECTOR - RESEARCH ONLY - NO TRADING", flush=True)
        print("Series: %s" % SERIES, flush=True)
        print("Ticks: %s" % OUT_DIR, flush=True)
        print("Facts: %s" % FACTS_PATH, flush=True)
        print("=" * 60, flush=True)

        self.session = aiohttp.ClientSession()
        if not await self.ws_connect():
            print("[FATAL] WS connect failed", flush=True)
            return

        tickers = await self.discover_markets()
        if tickers:
            await self.ws_subscribe(tickers)

        asyncio.create_task(self.ws_reader())

        last_discovery = time.time()
        last_status = time.time()

        while True:
            try:
                now = time.time()
                if now - last_discovery > DISCOVERY_INTERVAL:
                    new = await self.discover_markets()
                    if new:
                        await self.ws_subscribe(new)
                    last_discovery = now

                if now - last_status > 600:
                    active = sum(1 for s in self.ticker_states.values() if not s.settled)
                    settled = sum(1 for s in self.ticker_states.values() if s.settled)
                    total_ticks = sum(s.tick_count for s in self.ticker_states.values())
                    self.log("STATUS: %d active, %d settled, %d total ticks" % (
                        active, settled, total_ticks))
                    last_status = now

                await asyncio.sleep(1)
            except KeyboardInterrupt:
                self.log("Shutting down...")
                for st in self.ticker_states.values():
                    if st.csv_file:
                        st.csv_file.flush()
                        st.csv_file.close()
                break
            except Exception as e:
                self.log("ERROR: %s" % e)
                await asyncio.sleep(5)

        if self.session:
            await self.session.close()


if __name__ == "__main__":
    asyncio.run(ITFCollector().run())
