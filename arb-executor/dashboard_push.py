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
import sqlite3
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable

import requests

logger = logging.getLogger("dashboard_push")

TRADES_FILE = os.path.join(os.path.dirname(__file__) or ".", "trades.json")
VERIFIED_MAPPINGS_FILE = os.path.join(os.path.dirname(__file__) or ".", "verified_mappings.json")
ORDERBOOK_DB_PATH = os.path.join(os.path.dirname(__file__) or ".", "orderbook_data.db")
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
        liquidity_stats = self._build_liquidity_stats()

        mappings_refreshed = self._get_mappings_last_refreshed()

        payload = {
            "spreads": spreads,
            "trades": trades,
            "positions": positions,
            "balances": balances,
            "system": system,
            "pnl_summary": pnl_summary,
            "mapped_games": mapped_games,
            "mappings_last_refreshed": mappings_refreshed,
            "liquidity_stats": liquidity_stats,
        }

        # Size check: drop liquidity_stats if payload too large (Vercel 4.5MB limit)
        payload_json = json.dumps(payload)
        payload_size = len(payload_json)
        if payload_size > 4_000_000:
            liq_size = len(json.dumps(liquidity_stats))
            print(
                f"[DASH] WARNING: Payload {payload_size/1e6:.1f}MB exceeds 4MB limit "
                f"(liquidity_stats={liq_size/1e6:.1f}MB), dropping liquidity_stats",
                flush=True,
            )
            payload.pop("liquidity_stats", None)
            payload_json = json.dumps(payload)
            payload_size = len(payload_json)

        # Debug: log payload summary every push
        bal_k = balances.get("kalshi_balance", 0)
        bal_p = balances.get("pm_balance", 0)
        liq_games = len(liquidity_stats.get("per_game", []))
        liq_hist = len(liquidity_stats.get("spread_history", []))
        print(
            f"[DASH] Push: {len(spreads)} spreads, {len(trades)} trades, "
            f"{len(positions)} positions, bal K=${bal_k} PM=${bal_p}, "
            f"{system.get('games_monitored', 0)} games, "
            f"liq={liq_games}g/{liq_hist}pts, "
            f"size={payload_size/1e3:.0f}KB",
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
                # Keep ALL trades that affect P&L (SUCCESS, EXITED, UNHEDGED,
                # TIER3A_HOLD, TIER3B_FLIP, TIER3_UNWIND).  Only limit
                # PM_NO_FILL / SKIPPED which are high-volume, zero-P&L noise.
                pnl_statuses = {"SUCCESS", "EXITED", "UNHEDGED"}
                pnl_tiers = {"TIER1_HEDGE", "TIER2_EXIT", "TIER3_UNWIND",
                             "TIER3A_HOLD", "TIER3B_FLIP"}
                pnl_trades = [
                    t for t in trades
                    if t.get("status") in pnl_statuses
                    or t.get("tier") in pnl_tiers
                    or t.get("settlement_pnl") is not None
                ]
                noise_trades = [
                    t for t in trades
                    if t.get("status") not in pnl_statuses
                    and t.get("tier", "") not in pnl_tiers
                    and t.get("settlement_pnl") is None
                ]
                # Keep last 100 noise trades for recent activity display
                recent_noise = noise_trades[-100:] if len(noise_trades) > 100 else noise_trades
                recent = sorted(
                    pnl_trades + recent_noise,
                    key=lambda t: t.get("timestamp", ""),
                )
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
                        "contracts_intended": t.get("contracts_intended", 1),
                        "actual_pnl": t.get("actual_pnl"),
                        "paper_mode": t.get("paper_mode", False),
                        "sizing_details": t.get("sizing_details"),
                        "execution_phase": t.get("execution_phase", "ioc"),
                        "is_maker": t.get("is_maker", False),
                        "gtc_rest_time_ms": t.get("gtc_rest_time_ms", 0),
                        "gtc_spread_checks": t.get("gtc_spread_checks", 0),
                        "gtc_cancel_reason": t.get("gtc_cancel_reason", ""),
                        "unwind_loss_cents": t.get("unwind_loss_cents"),
                        "execution_time_ms": t.get("execution_time_ms", 0),
                        "pm_order_ms": t.get("pm_order_ms", 0),
                        "tier": t.get("tier", ""),
                        "settlement_pnl": t.get("settlement_pnl"),
                        "settlement_time": t.get("settlement_time"),
                        "settlement_winner_index": t.get("settlement_winner_index"),
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

        games = self.verified_maps  # already the games dict (load_verified_mappings extracts it)
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

    # ── Liquidity Stats ────────────────────────────────────────────────────

    def _build_liquidity_stats(self) -> dict:
        """Query orderbook_data.db for per-game liquidity aggregates.

        Optimized to stay under Vercel's 4.5MB payload limit:
        - Per-game table: only games active in last 2h
        - Spread history: top 10 games by snapshot count, 10-min downsample
        - All floats rounded to 1 decimal place
        """
        empty = {"per_game": [], "spread_history": [], "aggregate": {}}

        if not os.path.exists(ORDERBOOK_DB_PATH):
            return empty

        try:
            conn = sqlite3.connect(ORDERBOOK_DB_PATH, timeout=3)
            conn.row_factory = sqlite3.Row

            now = datetime.now(timezone.utc)
            cutoff_24h = (now - timedelta(hours=24)).isoformat()
            cutoff_2h = (now - timedelta(hours=2)).isoformat()

            # Per-game aggregates — only games active in last 2h
            per_game_rows = conn.execute("""
                SELECT
                    game_id,
                    platform,
                    COUNT(*) as snapshots,
                    ROUND(AVG(bid_depth), 1) as avg_bid_depth,
                    ROUND(AVG(ask_depth), 1) as avg_ask_depth,
                    ROUND(AVG(spread), 1) as avg_spread,
                    ROUND(MIN(spread), 1) as min_spread,
                    ROUND(MAX(spread), 1) as max_spread,
                    MAX(best_bid) as best_bid_seen,
                    MIN(best_ask) as best_ask_seen,
                    MAX(timestamp) as last_snapshot
                FROM orderbook_snapshots
                WHERE timestamp > ?
                GROUP BY game_id, platform
                HAVING MAX(timestamp) > ?
                ORDER BY snapshots DESC
            """, (cutoff_24h, cutoff_2h)).fetchall()

            per_game = []
            for r in per_game_rows:
                per_game.append({
                    "game_id": r["game_id"],
                    "platform": r["platform"],
                    "snapshots": r["snapshots"],
                    "avg_bid_depth": round(r["avg_bid_depth"] or 0, 1),
                    "avg_ask_depth": round(r["avg_ask_depth"] or 0, 1),
                    "avg_spread": round(r["avg_spread"] or 0, 1),
                    "min_spread": round(r["min_spread"] or 0, 1),
                    "max_spread": round(r["max_spread"] or 0, 1),
                    "best_bid_seen": r["best_bid_seen"] or 0,
                    "best_ask_seen": r["best_ask_seen"] or 0,
                    "last_snapshot": r["last_snapshot"] or "",
                })

            # Top 10 games by snapshot count for spread history
            top_games_rows = conn.execute("""
                SELECT game_id, COUNT(*) as cnt
                FROM orderbook_snapshots
                WHERE timestamp > ?
                GROUP BY game_id
                ORDER BY cnt DESC
                LIMIT 10
            """, (cutoff_2h,)).fetchall()
            top_game_ids = [r["game_id"] for r in top_games_rows]

            # Spread history — last 6h, only top 10 games, 10-min downsample
            spread_history: list = []
            if top_game_ids:
                placeholders = ",".join("?" for _ in top_game_ids)
                spread_cutoff = (now - timedelta(hours=6)).isoformat()
                spread_rows = conn.execute(f"""
                    SELECT
                        game_id, platform, timestamp,
                        best_bid, best_ask, bid_depth, ask_depth, spread
                    FROM orderbook_snapshots
                    WHERE timestamp > ? AND game_id IN ({placeholders})
                    ORDER BY timestamp ASC
                """, (spread_cutoff, *top_game_ids)).fetchall()

                # Downsample to 10-min intervals per game+platform
                last_ts: Dict[str, str] = {}
                for r in spread_rows:
                    key = f"{r['game_id']}_{r['platform']}"
                    ts = r["timestamp"]
                    if key in last_ts:
                        try:
                            prev = datetime.fromisoformat(last_ts[key])
                            curr = datetime.fromisoformat(ts)
                            if (curr - prev).total_seconds() < 600:
                                continue
                        except (ValueError, TypeError):
                            pass
                    last_ts[key] = ts
                    spread_history.append({
                        "game_id": r["game_id"],
                        "platform": r["platform"],
                        "timestamp": ts,
                        "best_bid": r["best_bid"] or 0,
                        "best_ask": r["best_ask"] or 0,
                        "bid_depth": r["bid_depth"] or 0,
                        "ask_depth": r["ask_depth"] or 0,
                        "spread": r["spread"] or 0,
                    })

            # Aggregate stats across all games (24h)
            agg_row = conn.execute("""
                SELECT
                    COUNT(*) as total_snapshots,
                    COUNT(DISTINCT game_id) as unique_games,
                    ROUND(AVG(bid_depth), 1) as overall_avg_bid_depth,
                    ROUND(AVG(ask_depth), 1) as overall_avg_ask_depth,
                    ROUND(AVG(spread), 1) as overall_avg_spread
                FROM orderbook_snapshots
                WHERE timestamp > ?
            """, (cutoff_24h,)).fetchone()

            aggregate = {
                "total_snapshots": agg_row["total_snapshots"] if agg_row else 0,
                "unique_games": agg_row["unique_games"] if agg_row else 0,
                "overall_avg_bid_depth": round(agg_row["overall_avg_bid_depth"] or 0, 1) if agg_row else 0,
                "overall_avg_ask_depth": round(agg_row["overall_avg_ask_depth"] or 0, 1) if agg_row else 0,
                "overall_avg_spread": round(agg_row["overall_avg_spread"] or 0, 1) if agg_row else 0,
            }

            conn.close()
            return {
                "per_game": per_game,
                "spread_history": spread_history,
                "aggregate": aggregate,
            }

        except Exception as e:
            logger.debug(f"Error building liquidity stats: {e}")
            return empty

    # ── Mappings Health ─────────────────────────────────────────────────────

    def _get_mappings_last_refreshed(self) -> str:
        """Return ISO timestamp of verified_mappings.json last modification."""
        try:
            if os.path.exists(VERIFIED_MAPPINGS_FILE):
                mtime = os.path.getmtime(VERIFIED_MAPPINGS_FILE)
                return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        except Exception:
            pass
        return ""

    # ── Balances ───────────────────────────────────────────────────────────

    def _build_balances(self) -> dict:
        """Return current balance snapshot."""
        k_cash = self.balances.get("k_cash", 0)
        k_portfolio = self.balances.get("k_portfolio", 0)
        pm_cash = self.balances.get("pm_cash", 0)
        pm_portfolio = self.balances.get("pm_portfolio", 0)
        return {
            "k_cash": round(k_cash, 2),
            "k_portfolio": round(k_portfolio, 2),
            "pm_cash": round(pm_cash, 2),
            "pm_portfolio": round(pm_portfolio, 2),
            "total_portfolio": round(k_portfolio + pm_portfolio, 2),
            # Backwards-compat
            "kalshi_balance": round(k_portfolio, 2),
            "pm_balance": round(pm_cash, 2),
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
