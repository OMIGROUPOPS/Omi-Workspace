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
        pnl_summary = self._build_pnl_summary()
        mapped_games = self._build_mapped_games()

        payload = {
            "spreads": spreads,
            "trades": trades,
            "positions": positions,
            "balances": balances,
            "system": system,
            "pnl_summary": pnl_summary,
            "mapped_games": mapped_games,
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
                recent = trades[-200:] if len(trades) > 200 else trades
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
        """Return live positions enriched with fill prices from trades.json."""
        positions = [dict(p) for p in self.live_positions]  # shallow copy each

        try:
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, "r") as f:
                    all_trades = json.load(f)

                # Build lookup: game_id -> most recent SUCCESS+hedged trade
                trade_by_game: Dict[str, dict] = {}
                for t in all_trades:
                    if (
                        t.get("status") == "SUCCESS"
                        and t.get("hedged")
                        and t.get("contracts_filled", 0) > 0
                    ):
                        trade_by_game[t["game_id"]] = t

                for pos in positions:
                    trade = trade_by_game.get(pos.get("game_id", ""))
                    if not trade:
                        continue

                    pnl = trade.get("actual_pnl")
                    if pnl and isinstance(pnl, dict):
                        pc = pnl.get("per_contract", {})
                        pos["pm_fill_price"] = pc.get("pm_cost", 0)
                        pos["k_fill_price"] = pc.get("k_cost", 0)
                        pos["locked_profit_cents"] = pc.get("gross", 0)
                        pos["net_profit_cents"] = pc.get("net", 0)

                    pos["direction"] = trade.get("direction", "")
                    pos["contracts"] = trade.get("contracts_filled", 0)
                    pos["trade_timestamp"] = trade.get("timestamp", "")
        except Exception as e:
            logger.debug(f"Error enriching positions: {e}")

        return positions

    # ── P&L Summary ───────────────────────────────────────────────────────

    def _build_pnl_summary(self) -> dict:
        """Compute exact P&L from trades.json actual_pnl data."""
        empty = {
            "total_pnl_dollars": 0,
            "profitable_count": 0,
            "losing_count": 0,
            "total_trades": 0,
            "total_attempts": 0,
            "total_filled": 0,
            "hedged_count": 0,
            "unhedged_filled": 0,
        }
        try:
            if not os.path.exists(TRADES_FILE):
                return empty

            with open(TRADES_FILE, "r") as f:
                all_trades = json.load(f)

            total_pnl = 0.0
            profitable = 0
            losing = 0
            trades_with_pnl = 0
            total_filled = 0
            hedged_count = 0
            unhedged_filled = 0

            for t in all_trades:
                filled = t.get("contracts_filled", 0) or 0
                if filled > 0:
                    total_filled += 1
                    if t.get("hedged"):
                        hedged_count += 1
                    else:
                        unhedged_filled += 1

                if t.get("status") != "SUCCESS" or filled == 0:
                    continue

                pnl = t.get("actual_pnl")
                if pnl and isinstance(pnl, dict):
                    net = pnl.get("net_profit_dollars", 0)
                    total_pnl += net
                    trades_with_pnl += 1
                    if pnl.get("is_profitable"):
                        profitable += 1
                    else:
                        losing += 1
                else:
                    # Fallback: use estimated_net_profit_cents
                    est = t.get("estimated_net_profit_cents", 0) or 0
                    contracts = filled
                    net = est * contracts / 100
                    total_pnl += net
                    trades_with_pnl += 1
                    if net > 0:
                        profitable += 1
                    else:
                        losing += 1

            return {
                "total_pnl_dollars": round(total_pnl, 4),
                "profitable_count": profitable,
                "losing_count": losing,
                "total_trades": trades_with_pnl,
                "total_attempts": len(all_trades),
                "total_filled": total_filled,
                "hedged_count": hedged_count,
                "unhedged_filled": unhedged_filled,
            }
        except Exception as e:
            logger.debug(f"Error computing P&L summary: {e}")
            return empty

    # ── Mapped Games ──────────────────────────────────────────────────────

    def _build_mapped_games(self) -> list:
        """Build mapped games list from verified_maps for the Mapped Games tab."""
        if not self.verified_maps:
            return []

        # Load trades.json to check which games have been traded
        traded_game_ids: set = set()
        try:
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, "r") as f:
                    all_trades = json.load(f)
                for t in all_trades:
                    if t.get("contracts_filled", 0) > 0:
                        traded_game_ids.add(t.get("game_id", ""))
        except Exception:
            pass

        games = self.verified_maps.get("games", {})
        rows = []
        for cache_key, g in games.items():
            game_id = g.get("game_id", "")
            sport = g.get("sport_display", g.get("sport", "").upper())
            date = g.get("date", "")
            pm_slug = g.get("pm_slug", "")

            # Extract team names from cache_key (format: sport:TEAM1-TEAM2:date)
            ck_parts = cache_key.split(":")
            teams_str = ck_parts[1] if len(ck_parts) >= 2 else ""
            teams = teams_str.split("-") if teams_str else []
            team1 = teams[0] if len(teams) >= 1 else ""
            team2 = teams[1] if len(teams) >= 2 else ""

            # Kalshi tickers
            kalshi_tickers = g.get("kalshi_tickers", {})
            ticker_list = list(kalshi_tickers.values())

            # Current best spread from live data
            best_spread = 0.0
            for team_abbr, ticker in kalshi_tickers.items():
                book = self.local_books.get(ticker)
                if not book:
                    continue
                k_bid = book.get("best_bid") or 0
                k_ask = book.get("best_ask") or 0
                if k_bid == 0 or k_ask == 0:
                    continue

                pm_key = f"{cache_key}_{team_abbr}"
                pm = self.pm_prices.get(pm_key)
                if not pm:
                    continue
                pm_bid = pm.get("bid") or 0
                pm_ask = pm.get("ask") or 0

                spread_buy_pm = k_bid - pm_ask
                spread_buy_k = pm_bid - k_ask
                best = max(spread_buy_pm, spread_buy_k)
                if best > best_spread:
                    best_spread = best

            # Determine status
            has_books = any(
                self.local_books.get(t) and
                (self.local_books[t].get("best_bid") or 0) > 0
                for t in ticker_list
            )
            status = "Active" if has_books else "Inactive"

            rows.append({
                "cache_key": cache_key,
                "game_id": game_id,
                "sport": sport,
                "date": date,
                "team1": team1,
                "team2": team2,
                "pm_slug": pm_slug,
                "kalshi_tickers": ticker_list,
                "best_spread": round(best_spread, 1),
                "status": status,
                "traded": game_id in traded_game_ids,
            })

        # Sort: active games first, then by date, then by best spread
        rows.sort(key=lambda r: (
            0 if r["status"] == "Active" else 1,
            r["date"],
            -r["best_spread"],
        ))
        return rows

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
