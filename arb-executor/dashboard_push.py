"""
Push arb executor state to the Vercel dashboard API.

Usage:
    from dashboard_push import DashboardPusher

    pusher = DashboardPusher("https://your-app.vercel.app/api/arb")
    pusher.start(interval=5)  # push every 5 seconds in background

    # Set data sources (call these to update what gets pushed):
    pusher.set_state_sources(
        local_books=local_books,
        pm_prices=pm_prices,
        ticker_to_cache_key=ticker_to_cache_key,
        cache_key_to_tickers=cache_key_to_tickers,
        stats=stats,
        balances=live_balances,
        verified_maps=VERIFIED_MAPS,
    )
"""

import json
import os
import time
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable

import requests

logger = logging.getLogger("dashboard_push")

TRADES_FILE = os.path.join(os.path.dirname(__file__) or ".", "trades.json")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "")
DASHBOARD_TOKEN = os.environ.get("DASHBOARD_TOKEN", "")


class DashboardPusher:
    """Pushes executor state to the Next.js /api/arb endpoint."""

    def __init__(
        self,
        url: str = "",
        token: str = "",
    ):
        self.url = url or DASHBOARD_URL
        self.token = token or DASHBOARD_TOKEN
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._start_time = time.time()

        # References to executor state (set these after init)
        self.local_books: Dict = {}
        self.pm_prices: Dict = {}
        self.ticker_to_cache_key: Dict = {}
        self.cache_key_to_tickers: Dict = {}
        self.stats: Dict = {}
        self.balances: Dict = {}
        self.live_positions: list = []
        self.verified_maps: Dict = {}
        self.executor_version: str = ""

    def set_state_sources(self, **kwargs: Any) -> None:
        """Set references to live executor state dicts."""
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def start(self, interval: float = 5.0) -> None:
        """Start background push thread."""
        if not self.url:
            logger.warning("DASHBOARD_URL not set, dashboard push disabled")
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, args=(interval,), daemon=True
        )
        self._thread.start()
        logger.info(f"Dashboard push started -> {self.url} every {interval}s")

    def stop(self) -> None:
        """Stop background push."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _loop(self, interval: float) -> None:
        while not self._stop.is_set():
            try:
                self.push()
            except Exception as e:
                logger.debug(f"Dashboard push error: {e}")
            self._stop.wait(interval)

    def push(self) -> bool:
        """Build and send current state. Returns True on success."""
        if not self.url:
            return False

        spreads = self._build_spreads()
        trades = self._build_trades()
        positions = self._build_positions()
        balances = self._build_balances()
        system = self._build_system()

        payload = {
            "spreads": spreads,
            "trades": trades,
            "positions": positions,
            "balances": balances,
            "system": system,
        }

        # Debug: log payload summary every push
        bal_k = balances.get("kalshi_balance", 0)
        bal_p = balances.get("pm_balance", 0)
        print(
            f"[DASH] Push: {len(spreads)} spreads, {len(trades)} trades, "
            f"{len(positions)} positions, bal K=${bal_k} PM=${bal_p}, "
            f"{system.get('games_monitored', 0)} games, "
            f"tickers_ref={len(self.ticker_to_cache_key)} books_ref={len(self.local_books)}",
            flush=True,
        )

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            resp = requests.post(
                self.url, json=payload, headers=headers, timeout=5
            )
            if resp.status_code != 200:
                print(f"[DASH] Push failed: {resp.status_code} {resp.text[:200]}", flush=True)
            return resp.status_code == 200
        except requests.RequestException as e:
            print(f"[DASH] Push error: {e}", flush=True)
            return False

    # ── Spreads ────────────────────────────────────────────────────────────

    def _build_spreads(self) -> list:
        """Build spread rows from live orderbook state."""
        rows = []

        for ticker, cache_key in self.ticker_to_cache_key.items():
            # Extract team from ticker (e.g. KXNBAGAME-26FEB09ATLMIN-ATL -> ATL)
            ticker_parts = ticker.split("-")
            if len(ticker_parts) < 3:
                continue
            team = ticker_parts[-1]
            game_id = ticker_parts[1] if len(ticker_parts) >= 2 else ticker

            # Kalshi orderbook
            book = self.local_books.get(ticker)
            if not book:
                continue
            k_bid = book.get("best_bid") or 0
            k_ask = book.get("best_ask") or 0

            # Skip empty/settled orderbooks
            if k_bid == 0 or k_ask == 0:
                continue

            # PM price (keyed by cache_key_team)
            pm_key = f"{cache_key}_{team}"
            pm = self.pm_prices.get(pm_key)
            if not pm:
                continue
            pm_bid = pm.get("bid") or 0
            pm_ask = pm.get("ask") or 0
            pm_ask_size = pm.get("ask_size") or 0
            pm_bid_size = pm.get("bid_size") or 0
            pm_long_team = pm.get("pm_long_team", "")

            # Spread calculation (prices already inverted for non-long team in pm_prices)
            spread_buy_pm = k_bid - pm_ask
            spread_buy_k = pm_bid - k_ask

            # Parse sport and date from cache_key (format: sport:TEAM1-TEAM2:YYYY-MM-DD)
            ck_parts = cache_key.split(":")
            sport = ck_parts[0].upper() if ck_parts else "?"
            if sport == "CBB":
                sport = "CBB"
            game_date = ck_parts[2] if len(ck_parts) >= 3 else ""

            best = max(spread_buy_pm, spread_buy_k)
            is_exec = best >= 4

            rows.append(
                {
                    "game_id": game_id,
                    "game_name": game_id,
                    "sport": sport,
                    "team": team,
                    "k_bid": k_bid,
                    "k_ask": k_ask,
                    "pm_bid": round(pm_bid, 1),
                    "pm_ask": round(pm_ask, 1),
                    "spread_buy_pm": round(spread_buy_pm, 1),
                    "spread_buy_k": round(spread_buy_k, 1),
                    "pm_size": max(pm_ask_size, pm_bid_size),
                    "is_executable": is_exec,
                    "game_date": game_date,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        return rows

    # ── Trades ─────────────────────────────────────────────────────────────

    def _build_trades(self) -> list:
        """Load recent trades from trades.json."""
        try:
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, "r") as f:
                    trades = json.load(f)
                recent = trades[-50:] if len(trades) > 50 else trades
                return [
                    {
                        "timestamp": t.get("timestamp", ""),
                        "game_id": t.get("game_id", ""),
                        "team": t.get("team", ""),
                        "sport": t.get("sport", ""),
                        "direction": t.get("direction", ""),
                        "spread_cents": t.get("spread_cents", 0),
                        "estimated_net_profit_cents": t.get(
                            "estimated_net_profit_cents"
                        ),
                        "hedged": t.get("hedged", False),
                        "status": t.get("status", ""),
                        "k_price": t.get("k_price", 0),
                        "pm_price": t.get("pm_price", 0),
                        "contracts_filled": t.get("contracts_filled", 0),
                        "actual_pnl": t.get("actual_pnl"),
                        "paper_mode": t.get("paper_mode", False),
                    }
                    for t in recent
                ]
        except Exception as e:
            logger.debug(f"Error loading trades: {e}")
        return []

    # ── Positions ──────────────────────────────────────────────────────────

    def _build_positions(self) -> list:
        """Return live positions fetched from platform APIs by the executor."""
        return list(self.live_positions)

    # ── Balances ───────────────────────────────────────────────────────────

    def _build_balances(self) -> dict:
        """Return current balance snapshot."""
        k = self.balances.get("kalshi_balance", 0)
        p = self.balances.get("pm_balance", 0)
        return {
            "kalshi_balance": k,
            "pm_balance": p,
            "total_portfolio": round(k + p, 2),
            "updated_at": self.balances.get("updated_at", ""),
        }

    # ── System ─────────────────────────────────────────────────────────────

    def _build_system(self) -> dict:
        """Build system status from stats dict."""
        return {
            "ws_connected": bool(
                self.stats.get("k_ws_connected")
                and self.stats.get("pm_ws_connected")
            ),
            "ws_messages_processed": (
                self.stats.get("k_ws_messages", 0)
                + self.stats.get("pm_ws_messages", 0)
            ),
            "uptime_seconds": round(time.time() - self._start_time),
            "last_scan_at": datetime.now(timezone.utc).isoformat(),
            "games_monitored": len(
                set(self.ticker_to_cache_key.values())
            ),
            "executor_version": self.executor_version,
            "error_count": self.stats.get("errors", 0),
            "last_error": self.stats.get("last_error"),
        }


# ── Convenience: standalone push from CLI ───────────────────────────────────

if __name__ == "__main__":
    """Quick test / one-shot push of trades.json to dashboard."""
    import argparse

    parser = argparse.ArgumentParser(description="Push arb state to dashboard")
    parser.add_argument(
        "--url",
        default=DASHBOARD_URL or "http://localhost:3000/api/arb",
        help="Dashboard API URL",
    )
    parser.add_argument("--token", default=DASHBOARD_TOKEN, help="API token")
    args = parser.parse_args()

    pusher = DashboardPusher(url=args.url, token=args.token)

    # Load trades for a one-shot push
    trades = pusher._build_trades()
    print(f"Pushing {len(trades)} trades to {args.url}")

    headers = {"Content-Type": "application/json"}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    resp = requests.post(
        args.url,
        json={"trades": trades},
        headers=headers,
        timeout=5,
    )
    print(f"Response: {resp.status_code} {resp.text}")
