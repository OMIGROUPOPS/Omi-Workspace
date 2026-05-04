#!/usr/bin/env python3
"""
Build /tmp/live_v3_paper.py from /root/Omi-Workspace/arb-executor/live_v3.py.

Applies all paper-mode transformations per /tmp/paper_mode_spec.md (sha 32f29fda):
- Renames module-level api_get/post/delete -> _real_api_get/post/delete
- Inserts new dispatcher functions and _PAPER_API global
- Inserts paper-mode classes (PaperOrder, PaperPosition, VolumeTracker,
  PaperFillSimulator, PaperApi) between Position class and LiveV3 class
- Hooks: trade ingestion in apply_trade, book updates in apply_snapshot
  and apply_delta, heartbeat in main loop, paper-mode init in LiveV3.__init__
- Startup safety check + load_state in async run-loop preamble

Does NOT modify live_v3.py. Writes /tmp/live_v3_paper.py.
"""

import os
import sys

SOURCE = "/root/Omi-Workspace/arb-executor/live_v3.py"
TARGET = "/tmp/live_v3_paper.py"

# =====================================================================
# PAPER MODE CODE BLOCK (injected after Position class, before LiveV3)
# =====================================================================
PAPER_MODE_BLOCK = '''
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


'''


# =====================================================================
# TRANSFORMATION
# =====================================================================

def transform(content):
    # 1. Rename module-level api_* to _real_api_*
    content = content.replace(
        "async def api_get(s, ak, pk, path, rl):",
        "async def _real_api_get(s, ak, pk, path, rl):", 1)
    content = content.replace(
        "async def api_post(s, ak, pk, path, payload, rl):",
        "async def _real_api_post(s, ak, pk, path, payload, rl):", 1)
    content = content.replace(
        "async def api_delete(s, ak, pk, path, rl):",
        "async def _real_api_delete(s, ak, pk, path, rl):", 1)

    # 2. Insert PAPER_MODE_BLOCK between Position class and LiveV3 class.
    #    Anchor: the comment header before LiveV3 class.
    anchor_2 = (
        "# -------------------------------------------------------------------------\n"
        "# Live V3 Bot\n"
        "# -------------------------------------------------------------------------\n"
        "class LiveV3:"
    )
    if anchor_2 not in content:
        raise SystemExit("ANCHOR 2 (Live V3 Bot header) not found")
    content = content.replace(anchor_2, PAPER_MODE_BLOCK.lstrip("\n") + anchor_2, 1)

    # 3. Trade hook: insert _PAPER_API.on_trade between book.last_trade_side
    #    and self._log_trade in apply_trade.
    anchor_3 = (
        "        book.last_trade_side = side\n"
        "        self._log_trade(ticker, price, count, side)\n"
    )
    new_3 = (
        "        book.last_trade_side = side\n"
        "        if _PAPER_API is not None:\n"
        "            _PAPER_API.on_trade(ticker, book.last_trade_ts, price, count, side)\n"
        "        self._log_trade(ticker, price, count, side)\n"
    )
    if anchor_3 not in content:
        raise SystemExit("ANCHOR 3 (trade hook) not found")
    content = content.replace(anchor_3, new_3, 1)

    # 4. Snapshot hook: after self._log_tick at end of apply_snapshot.
    #    Disambiguate from apply_delta by including the preceding self.books[ticker]=book
    #    line which is unique to apply_snapshot.
    anchor_4 = (
        "        self.books[ticker] = book\n"
        "        self._log_tick(ticker, book)\n"
        "\n"
        "    def apply_delta(self, ticker, msg):\n"
    )
    new_4 = (
        "        self.books[ticker] = book\n"
        "        self._log_tick(ticker, book)\n"
        "        if _PAPER_API is not None:\n"
        "            _PAPER_API.on_book_update(ticker)\n"
        "\n"
        "    def apply_delta(self, ticker, msg):\n"
    )
    if anchor_4 not in content:
        raise SystemExit("ANCHOR 4 (snapshot hook) not found")
    content = content.replace(anchor_4, new_4, 1)

    # 5. Delta hook: after self._log_tick at end of apply_delta.
    #    Disambiguate by anchoring on the preceding _ws_reconnect def.
    anchor_5 = (
        "        self._log_tick(ticker, book)\n"
        "\n"
        "    async def _ws_reconnect(self):\n"
    )
    new_5 = (
        "        self._log_tick(ticker, book)\n"
        "        if _PAPER_API is not None:\n"
        "            _PAPER_API.on_book_update(ticker)\n"
        "\n"
        "    async def _ws_reconnect(self):\n"
    )
    if anchor_5 not in content:
        raise SystemExit("ANCHOR 5 (delta hook) not found")
    content = content.replace(anchor_5, new_5, 1)

    # 6. Bot init wiring: after self._load_schedule() at end of __init__.
    #    Anchor by including the start of next method definition.
    anchor_6 = (
        "        self._load_schedule()\n"
        "\n"
        "    def _log(self, event, details=None, ticker=\"\"):\n"
    )
    new_6 = (
        "        self._load_schedule()\n"
        "\n"
        "        # Paper mode init (spec §2.2)\n"
        "        if self.config.get(\"paper_mode\", False):\n"
        "            global _PAPER_API\n"
        "            _PAPER_API = PaperApi(bot=self)\n"
        "            self._log(\"paper_mode_enabled\", {\n"
        "                \"config_path\": str(CONFIG_PATH),\n"
        "                \"PAPER_MODE_VERSION\": \"1.0\",\n"
        "                \"paper_state_max_age_sec\": self.config.get(\"paper_state_max_age_sec\", 86400),\n"
        "            })\n"
        "\n"
        "    def _log(self, event, details=None, ticker=\"\"):\n"
    )
    if anchor_6 not in content:
        raise SystemExit("ANCHOR 6 (init wiring) not found")
    content = content.replace(anchor_6, new_6, 1)

    # 7. Heartbeat call: after await self.check_fills() in main loop.
    anchor_7 = (
        "                if now - last_fill_check > FILL_CHECK_INTERVAL:\n"
        "                    await self.check_fills()\n"
        "                    last_fill_check = now\n"
    )
    new_7 = (
        "                if now - last_fill_check > FILL_CHECK_INTERVAL:\n"
        "                    await self.check_fills()\n"
        "                    if _PAPER_API is not None:\n"
        "                        _PAPER_API.maybe_heartbeat()\n"
        "                    last_fill_check = now\n"
    )
    if anchor_7 not in content:
        raise SystemExit("ANCHOR 7 (heartbeat) not found")
    content = content.replace(anchor_7, new_7, 1)

    # 8. Startup safety check + load_state: after await asyncio.sleep(10).
    anchor_8 = (
        "        await asyncio.sleep(10)\n"
        "\n"
        "        last_discovery = time.time()\n"
    )
    new_8 = (
        "        await asyncio.sleep(10)\n"
        "\n"
        "        # Paper mode startup: safety check + restore prior state (spec §2.3, §13)\n"
        "        if _PAPER_API is not None:\n"
        "            real_pos = await _real_api_get(self.session, self.ak, self.pk,\n"
        "                \"/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled\",\n"
        "                self.rl)\n"
        "            real_positions_count = len((real_pos or {}).get(\"market_positions\", []))\n"
        "            if real_positions_count > 0:\n"
        "                self._log(\"paper_real_orders_blocked\", {\n"
        "                    \"real_positions_count\": real_positions_count,\n"
        "                    \"action\": \"abort\",\n"
        "                })\n"
        "                raise RuntimeError(\n"
        "                    \"paper_mode=true but %d real Kalshi positions exist; close them first\"\n"
        "                    % real_positions_count)\n"
        "            paper_state_path = \"/root/Omi-Workspace/arb-executor/paper_state.json\"\n"
        "            paper_state_max_age = self.config.get(\"paper_state_max_age_sec\", 86400)\n"
        "            _PAPER_API.load_state(paper_state_path, paper_state_max_age)\n"
        "\n"
        "        last_discovery = time.time()\n"
    )
    if anchor_8 not in content:
        raise SystemExit("ANCHOR 8 (startup safety) not found")
    content = content.replace(anchor_8, new_8, 1)

    return content


def main():
    with open(SOURCE) as f:
        content = f.read()
    new_content = transform(content)
    with open(TARGET, "w") as f:
        f.write(new_content)
    print("WROTE: %s" % TARGET)
    print("SIZE: %d bytes" % os.path.getsize(TARGET))


if __name__ == "__main__":
    main()
