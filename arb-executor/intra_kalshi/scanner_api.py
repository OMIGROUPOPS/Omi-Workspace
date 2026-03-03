"""
Scanner API — FastAPI endpoints exposing live scanner data.

Embedded inside the scanner process. The scanner sets _scanner_ref on startup,
and uvicorn serves this app as an additional asyncio task.

Endpoints:
  GET /api/scanner/status     — uptime, stats, connection info
  GET /api/scanner/signals    — recent signals/alerts
  GET /api/scanner/trades     — open + closed paper trades
  GET /api/scanner/orderbook/{ticker} — BBO + depth
  GET /api/scanner/categories — category-grouped ticker summaries
"""

import os
import time
from collections import defaultdict
from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

api_app = FastAPI(title="Intra-Kalshi Scanner API", docs_url=None, redoc_url=None)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Set by scanner on startup
_scanner_ref = None


def set_scanner(scanner):
    global _scanner_ref
    _scanner_ref = scanner


# ---------------------------------------------------------------------------
# GET /api/scanner/status
# ---------------------------------------------------------------------------

@api_app.get("/api/scanner/status")
async def scanner_status():
    s = _scanner_ref
    if s is None:
        return {"error": "scanner not initialized"}

    now = time.time()
    uptime = now - s.stats.get("started", now)

    # Memory via resource module (Linux only)
    mem_mb = 0
    try:
        import resource
        mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except Exception:
        pass

    # Total PnL from closed trades
    total_pnl = sum(t.pnl_cents or 0 for t in s.closed_trades)
    winners = sum(1 for t in s.closed_trades if (t.pnl_cents or 0) > 0)
    losers = sum(1 for t in s.closed_trades if (t.pnl_cents or 0) < 0)

    # Strategy stats from _recent_signals
    strategy_stats = defaultdict(lambda: {"signals": 0, "trades": 0})
    for sig in getattr(s, "_recent_signals", []):
        stype = sig.get("scan_type", "unknown")
        strategy_stats[stype]["signals"] += 1
        if not sig.get("is_alert", True):
            strategy_stats[stype]["trades"] += 1

    return {
        "uptime": round(uptime),
        "pid": os.getpid(),
        "memory_mb": round(mem_mb, 1),
        "tickers_count": len(s.subscribed_tickers),
        "events_count": s.stats.get("events_discovered", 0),
        "ws_messages": s.stats.get("ws_messages", 0),
        "ws_reconnects": s.stats.get("ws_reconnects", 0),
        "ws_connected": s.ws_connected,
        "bbo_updates": s.stats.get("bbo_updates", 0),
        "scan_signals": s.stats.get("scan_signals", 0),
        "open_trades": len(s.open_trades),
        "closed_trades": len(s.closed_trades),
        "total_pnl": total_pnl,
        "winners": winners,
        "losers": losers,
        "whale_fills": getattr(s, "_whale_fills_total", 0),
        "strategy_stats": dict(strategy_stats),
    }


# ---------------------------------------------------------------------------
# GET /api/scanner/signals?limit=50
# ---------------------------------------------------------------------------

@api_app.get("/api/scanner/signals")
async def scanner_signals(limit: int = Query(default=50, ge=1, le=200)):
    s = _scanner_ref
    if s is None:
        return {"error": "scanner not initialized"}

    signals = list(getattr(s, "_recent_signals", []))
    # Return most recent first
    return signals[-limit:][::-1]


# ---------------------------------------------------------------------------
# GET /api/scanner/trades
# ---------------------------------------------------------------------------

@api_app.get("/api/scanner/trades")
async def scanner_trades():
    s = _scanner_ref
    if s is None:
        return {"error": "scanner not initialized"}

    open_trades = [asdict(t) for t in s.open_trades]
    closed_recent = [asdict(t) for t in s.closed_trades[-50:]]

    # Summary
    total_pnl = sum(t.pnl_cents or 0 for t in s.closed_trades)
    winners = sum(1 for t in s.closed_trades if (t.pnl_cents or 0) > 0)
    losers = sum(1 for t in s.closed_trades if (t.pnl_cents or 0) < 0)

    # By strategy
    by_strategy = defaultdict(lambda: {
        "total_pnl": 0, "trade_count": 0, "winners": 0, "losers": 0,
        "total_hold_time": 0, "total_edge": 0,
    })
    for t in s.closed_trades:
        bs = by_strategy[t.scan_type]
        bs["trade_count"] += 1
        bs["total_pnl"] += t.pnl_cents or 0
        if (t.pnl_cents or 0) > 0:
            bs["winners"] += 1
        elif (t.pnl_cents or 0) < 0:
            bs["losers"] += 1
        bs["total_hold_time"] += t.hold_time or 0
        # Edge: target - entry as rough proxy
        if t.target and t.entry_price:
            bs["total_edge"] += abs(t.target - t.entry_price)

    # Compute averages
    by_strategy_out = {}
    for stype, bs in by_strategy.items():
        n = bs["trade_count"] or 1
        by_strategy_out[stype] = {
            "scan_type": stype,
            "total_pnl": bs["total_pnl"],
            "trade_count": bs["trade_count"],
            "winners": bs["winners"],
            "losers": bs["losers"],
            "avg_hold_time": round(bs["total_hold_time"] / n, 1),
            "avg_edge": round(bs["total_edge"] / n / 100, 4) if bs["total_edge"] else 0,
        }

    return {
        "open": open_trades,
        "closed_recent": closed_recent,
        "summary": {
            "total_pnl": total_pnl,
            "open_count": len(s.open_trades),
            "closed_count": len(s.closed_trades),
            "winners": winners,
            "losers": losers,
            "by_strategy": by_strategy_out,
        },
    }


# ---------------------------------------------------------------------------
# GET /api/scanner/orderbook/{ticker}
# ---------------------------------------------------------------------------

@api_app.get("/api/scanner/orderbook/{ticker}")
async def scanner_orderbook(ticker: str):
    s = _scanner_ref
    if s is None:
        return {"error": "scanner not initialized"}

    book = s.books.get(ticker)
    if not book:
        return {"error": f"no book for {ticker}"}

    # Build depth levels
    bids = [{"price": p, "size": sz} for p, sz in sorted(book.yes_bids.items(), reverse=True)]
    asks = [{"price": p, "size": sz} for p, sz in sorted(book.yes_asks.items())]

    spread = None
    if book.best_bid is not None and book.best_ask is not None:
        spread = book.best_ask - book.best_bid

    return {
        "ticker": ticker,
        "best_bid": book.best_bid,
        "best_ask": book.best_ask,
        "spread": spread,
        "bid_size": book.best_bid_size,
        "ask_size": book.best_ask_size,
        "bids": bids,
        "asks": asks,
    }


# ---------------------------------------------------------------------------
# GET /api/scanner/categories
# ---------------------------------------------------------------------------

@api_app.get("/api/scanner/categories")
async def scanner_categories():
    s = _scanner_ref
    if s is None:
        return {"error": "scanner not initialized"}

    now = time.time()
    recent_signals = list(getattr(s, "_recent_signals", []))

    # Index signals by category for last_signal_time
    signals_by_cat = defaultdict(list)
    for sig in recent_signals:
        cat = sig.get("category", "")
        signals_by_cat[cat].append(sig)

    categories = []
    for cat, cdata in s._category_stats.items():
        cat_label = cat if cat else "Unknown"

        # Collect tickers for this category
        cat_tickers = []
        for ticker, info in s.market_info.items():
            if info.category != cat:
                continue
            book = s.books.get(ticker)
            if not book or book.best_bid is None or book.best_ask is None:
                continue

            spread = book.best_ask - book.best_bid
            mid = (book.best_bid + book.best_ask) / 2

            # 30s price move from bbo_history
            move_30s = None
            hist = s.bbo_history.get(ticker)
            if hist and len(hist) >= 2:
                cutoff = now - 30.0
                oldest_in_window = None
                for entry in hist:
                    if entry.ts >= cutoff:
                        oldest_in_window = entry
                        break
                if oldest_in_window:
                    old_mid = (oldest_in_window.bid + oldest_in_window.ask) / 2
                    move_30s = round(mid - old_mid)

            cat_tickers.append({
                "ticker": ticker,
                "team": info.team,
                "event_ticker": info.event_ticker,
                "market_type": info.market_type,
                "category": cat_label,
                "best_bid": book.best_bid,
                "best_ask": book.best_ask,
                "mid": round(mid, 1),
                "spread": spread,
                "bid_size": book.best_bid_size,
                "ask_size": book.best_ask_size,
                "kyle_lambda": s._ticker_lambda.get(ticker),
                "vpin": s._ticker_vpin.get(ticker),
                "move_30s": move_30s,
            })

        # Sort by tightest spread, then highest lambda desc. Take top 10.
        cat_tickers.sort(key=lambda t: (t["spread"], -(t["kyle_lambda"] or 999)))
        top_tickers = cat_tickers[:10]

        # Last signal time for this category
        cat_sigs = signals_by_cat.get(cat, [])
        last_signal_time = None
        if cat_sigs:
            last_ts = max(sig.get("timestamp", 0) for sig in cat_sigs)
            if last_ts > 0:
                last_signal_time = last_ts

        categories.append({
            "category": cat_label,
            "active_tickers": len(cat_tickers),
            "active_events": len(cdata.get("events", set())),
            "signals_count": cdata.get("signals", 0),
            "last_signal_time": last_signal_time,
            "top_tickers": top_tickers,
        })

    # Sort categories by active_tickers desc
    categories.sort(key=lambda c: -c["active_tickers"])

    return {
        "categories": categories,
        "total_tickers": len(s.subscribed_tickers),
        "total_events": s.stats.get("events_discovered", 0),
    }
