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
import subprocess
import sys
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


# ── Git info — computed once at module load ────────────────────────────────
def _get_git_info() -> dict:
    info = {"commit_short": "", "commit_sha": "", "branch": "", "commit_date": "", "commit_msg": ""}
    try:
        base = os.path.dirname(__file__) or "."
        info["commit_sha"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=base, timeout=3
        ).stdout.strip()
        info["commit_short"] = info["commit_sha"][:7]
        info["branch"] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=base, timeout=3
        ).stdout.strip()
        info["commit_date"] = subprocess.run(
            ["git", "log", "-1", "--format=%ci"], capture_output=True, text=True, cwd=base, timeout=3
        ).stdout.strip()
        info["commit_msg"] = subprocess.run(
            ["git", "log", "-1", "--format=%s"], capture_output=True, text=True, cwd=base, timeout=3
        ).stdout.strip()[:80]
    except Exception:
        pass
    return info

_GIT_INFO = _get_git_info()
_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


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
        self.pm_books: Dict = {}
        self.ticker_to_cache_key: Dict = {}
        self.cache_key_to_tickers: Dict = {}
        self.stats: Dict = {}
        self.balances: Dict = {}
        self.live_positions: list = []
        self.verified_maps: Dict = {}
        self.executor_version: str = ""
        self.omi_cache = None
        self.espn_scores = None  # ESPNScores instance

        # Rolling spread history buffer (60 min, max 1 point per 30s per game)
        self._spread_history: list = []
        self._spread_history_last: Dict[str, float] = {}  # game_team -> last_ts

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
        spread_history = self._build_spread_history(spreads)
        trades = self._build_trades()
        positions = self._build_positions()
        balances = self._build_balances()
        system = self._build_system()
        pnl_summary = self._build_pnl_summary()
        mapped_games = self._build_mapped_games()
        liquidity_stats = self._build_liquidity_stats()
        specs = self._build_specs()

        mappings_refreshed = self._get_mappings_last_refreshed()

        payload = {
            "spreads": spreads,
            "spread_history": spread_history,
            "trades": trades,
            "positions": positions,
            "balances": balances,
            "system": system,
            "pnl_summary": pnl_summary,
            "mapped_games": mapped_games,
            "mappings_last_refreshed": mappings_refreshed,
            "liquidity_stats": liquidity_stats,
            "specs": specs,
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

    # ── Spread History ───────────────────────────────────────────────────

    def _build_spread_history(self, spreads: list) -> list:
        """Snapshot current spreads into rolling 60-min history buffer.

        Downsamples to max 1 point per 30s per game to keep payload small.
        Returns the full buffer (trimmed to 60 min).
        """
        now = time.time()
        cutoff = now - 3600  # 60 minutes

        # Add current spread snapshot
        for s in spreads:
            key = f"{s['game_id']}_{s['team']}"
            last_ts = self._spread_history_last.get(key, 0)
            if now - last_ts < 30:
                continue  # skip — too soon for this game
            self._spread_history_last[key] = now
            self._spread_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "game_id": s["game_id"],
                "team": s["team"],
                "sport": s["sport"],
                "spread_buy_pm": s["spread_buy_pm"],
                "spread_buy_k": s["spread_buy_k"],
                "best_spread": max(s["spread_buy_pm"], s["spread_buy_k"]),
            })

        # Trim entries older than 60 min
        self._spread_history = [
            p for p in self._spread_history
            if now - datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")).timestamp() < 3600
        ]

        # Also clean up stale keys from last-timestamp tracker
        self._spread_history_last = {
            k: v for k, v in self._spread_history_last.items() if now - v < 3600
        }

        return self._spread_history

    # ── Trades ─────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_opponent(trade: dict) -> str:
        """Extract opponent team from cache_key. Format: 'sport:TEAM1-TEAM2:date'"""
        ck = trade.get("cache_key", "")
        team = trade.get("team", "")
        if not ck or not team:
            return ""
        parts = ck.split(":")
        if len(parts) < 2:
            return ""
        teams_part = parts[1]  # "TEAM1-TEAM2"
        teams = teams_part.split("-")
        for t in teams:
            if t != team:
                return t
        return ""

    def _resolve_full_name(self, cache_key: str, team_abbrev: str) -> str:
        """Look up full team name from verified_maps, fall back to TEAM_FULL_NAMES."""
        if not team_abbrev:
            return ""
        mapping = self.verified_maps.get(cache_key, {})
        team_names = mapping.get("team_names", {})
        if team_abbrev in team_names:
            return team_names[team_abbrev]
        # Fall back to static NBA/NHL names
        try:
            from pregame_mapper import TEAM_FULL_NAMES
            return TEAM_FULL_NAMES.get(team_abbrev, "")
        except ImportError:
            return ""

    def _build_trades(self) -> list:
        """Load recent trades from trades.json."""
        try:
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, "r") as f:
                    trades = json.load(f)
                # Keep ALL trades that affect P&L (SUCCESS, EXITED, UNHEDGED,
                # TIER3A_HOLD, TIER3_OPPOSITE_*, TIER3_UNWIND).  Only limit
                # PM_NO_FILL / SKIPPED which are high-volume, zero-P&L noise.
                pnl_statuses = {"SUCCESS", "EXITED", "UNHEDGED"}
                pnl_tiers = {"TIER1_HEDGE", "TIER2_EXIT", "TIER3_UNWIND",
                             "TIER3A_HOLD", "TIER3_OPPOSITE_HEDGE", "TIER3_OPPOSITE_OVERWEIGHT"}
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
                        "unwind_pnl_cents": t.get("unwind_pnl_cents"),
                        "unwind_fill_price": t.get("unwind_fill_price"),
                        "unwind_qty": t.get("unwind_qty", 0),
                        "pm_fee": t.get("pm_fee", 0),
                        "k_fee": t.get("k_fee", 0),
                        "execution_time_ms": t.get("execution_time_ms", 0),
                        "pm_order_ms": t.get("pm_order_ms", 0),
                        "k_order_ms": t.get("k_order_ms", 0),
                        "tier": t.get("tier", ""),
                        "settlement_pnl": t.get("settlement_pnl"),
                        "reconciled_pnl": t.get("reconciled_pnl"),
                        "settlement_time": t.get("settlement_time"),
                        "settlement_winner_index": t.get("settlement_winner_index"),
                        "opponent": self._extract_opponent(t),
                        "team_full_name": self._resolve_full_name(t.get("cache_key", ""), t.get("team", "")),
                        "opponent_full_name": self._resolve_full_name(t.get("cache_key", ""), self._extract_opponent(t)),
                        "cache_key": t.get("cache_key", ""),
                        "pm_slug": t.get("pm_slug", ""),
                        "kalshi_ticker": t.get("kalshi_ticker", ""),
                    }
                    for t in recent
                ]
        except Exception as e:
            logger.debug(f"Error loading trades: {e}")
        return []

    # ── Positions ──────────────────────────────────────────────────────────

    def _build_positions(self) -> list:
        """Build open positions by scanning trades.json for unsettled fills.

        Open = contracts_filled > 0, no settlement_pnl, not EXITED.
        Enriches each with current WS prices and OMI signal data.
        """
        OPEN_STATUSES = {"SUCCESS", "UNHEDGED"}
        OPEN_TIERS = {"TIER1_HEDGE", "TIER3A_HOLD", "TIER3_OPPOSITE_HEDGE", "TIER3_OPPOSITE_OVERWEIGHT"}

        try:
            if not os.path.exists(TRADES_FILE):
                return []
            with open(TRADES_FILE, "r") as f:
                all_trades = json.load(f)
        except Exception as e:
            logger.debug(f"Error loading trades for positions: {e}")
            return []

        positions = []
        for t in all_trades:
            if t.get("contracts_filled", 0) <= 0:
                continue
            if t.get("settlement_pnl") is not None:
                continue
            status = t.get("status", "")
            tier = t.get("tier", "")
            if status == "EXITED":
                continue
            if status not in OPEN_STATUSES and tier not in OPEN_TIERS:
                continue

            qty = t.get("contracts_filled", 0)
            direction = t.get("direction", "")
            pm_fill = t.get("pm_price", 0)
            k_fill = t.get("k_price", 0)
            team = t.get("team", "")
            hedged = t.get("hedged", False)

            # Normalise PM fill to cents (stored as decimal < 1 or cents)
            pm_fill_c = pm_fill * 100 if pm_fill < 1 else pm_fill

            # Cost in dollars
            pm_cost = pm_fill_c * qty / 100
            k_cost = k_fill * qty / 100 if hedged else 0

            # ── Current market prices from WS cache ──
            k_ticker = t.get("kalshi_ticker", "")
            pm_bid_now = 0.0
            pm_ask_now = 0.0
            k_bid_now = 0.0
            k_ask_now = 0.0

            # Kalshi current
            if k_ticker:
                book = self.local_books.get(k_ticker)
                if book:
                    k_bid_now = book.get("best_bid") or 0
                    k_ask_now = book.get("best_ask") or 0

            # PM current via cache_key lookup
            cache_key = self.ticker_to_cache_key.get(k_ticker, "")
            if cache_key and team:
                pm_key = f"{cache_key}_{team}"
                pm = self.pm_prices.get(pm_key)
                if pm:
                    pm_bid_now = pm.get("bid") or 0
                    pm_ask_now = pm.get("ask") or 0

            # ── Market value (mark-to-market) ──
            # For BUY_PM_SELL_K: long PM YES, short K YES
            #   PM value = pm_bid * qty (could sell at bid)
            #   K value  = (100 - k_ask) * qty (cost to buy back)
            # For BUY_K_SELL_PM: short PM YES, long K YES
            #   PM value = (100 - pm_ask) * qty (cost to buy back)
            #   K value  = k_bid * qty (could sell at bid)
            if direction == "BUY_PM_SELL_K":
                pm_mkt = pm_bid_now * qty / 100 if pm_bid_now else 0
                k_mkt = (100 - k_ask_now) * qty / 100 if hedged and k_ask_now else 0
            elif direction == "BUY_K_SELL_PM":
                pm_mkt = (100 - pm_ask_now) * qty / 100 if pm_ask_now else 0
                k_mkt = k_bid_now * qty / 100 if hedged and k_bid_now else 0
            else:
                pm_mkt = 0
                k_mkt = 0

            # Fees
            pm_fee = t.get("pm_fee", 0) or 0
            k_fee = t.get("k_fee", 0) or 0
            total_fees = pm_fee + k_fee

            # ── Unrealised P&L ──
            if hedged:
                # Locked spread — doesn't change with market
                spread_cents = t.get("spread_cents", 0) or 0
                unrealised = spread_cents * qty / 100 - total_fees
            else:
                # Directional — mark to market
                if direction == "BUY_PM_SELL_K":
                    unrealised = pm_mkt - pm_cost - total_fees
                elif direction == "BUY_K_SELL_PM":
                    unrealised = pm_cost - pm_mkt - total_fees  # short PM
                else:
                    unrealised = 0

            # ── OMI signal ──
            ceq = None
            signal = None
            if self.omi_cache is not None:
                omi_data = self.omi_cache.get_signal(team)
                if omi_data:
                    ceq = round(self.omi_cache.get_effective_ceq(omi_data), 2)
                    signal = omi_data.get("signal", "")

            # Determine display status
            if hedged:
                display_status = "HEDGED"
            elif tier in OPEN_TIERS:
                display_status = tier
            else:
                display_status = "UNHEDGED"

            _ck = t.get("cache_key", "")
            _opp = self._extract_opponent(t)
            positions.append({
                "game_id": t.get("game_id", ""),
                "team": team,
                "team_full_name": self._resolve_full_name(_ck, team),
                "opponent": _opp,
                "opponent_full_name": self._resolve_full_name(_ck, _opp),
                "sport": t.get("sport", ""),
                "direction": direction,
                "status": display_status,
                "tier": tier,
                "hedged": hedged,
                "timestamp": t.get("timestamp", ""),
                "contracts": qty,
                "pm_fill_cents": round(pm_fill_c, 1),
                "k_fill_cents": k_fill,
                "pm_bid_now": round(pm_bid_now, 1),
                "pm_ask_now": round(pm_ask_now, 1),
                "k_bid_now": k_bid_now,
                "k_ask_now": k_ask_now,
                "pm_cost_dollars": round(pm_cost, 4),
                "k_cost_dollars": round(k_cost, 4),
                "pm_mkt_val_dollars": round(pm_mkt, 4),
                "k_mkt_val_dollars": round(k_mkt, 4),
                "pm_fee": round(pm_fee, 4),
                "k_fee": round(k_fee, 4),
                "total_fees": round(total_fees, 4),
                "unrealised_pnl": round(unrealised, 4),
                "spread_cents": t.get("spread_cents", 0) or 0,
                "ceq": ceq,
                "signal": signal,
            })

        return positions

    # ── P&L Summary ───────────────────────────────────────────────────────

    def _build_pnl_summary(self) -> dict:
        """Compute P&L from trades.json using reconciled_pnl as primary source.

        Priority order for each trade's P&L:
          1. reconciled_pnl (set by cash_ledger.py reconcile)
          2. settlement_pnl (set by kalshi_reconciler)
          3. actual_pnl / estimated_net_profit_cents (original executor data)
          4. unwind_pnl_cents / recomputed unwind (EXITED trades)

        Also computes cash_pnl = portfolio_total - starting_balance as headline.
        """
        STARTING_BALANCE_TOTAL = 910.31

        empty = {
            "total_pnl_dollars": 0,
            "profitable_count": 0,
            "losing_count": 0,
            "total_trades": 0,
            "total_attempts": 0,
            "total_filled": 0,
            "hedged_count": 0,
            "unhedged_filled": 0,
            "cash_pnl": 0,
            "portfolio_total": 0,
            "starting_balance": STARTING_BALANCE_TOTAL,
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

                status = t.get("status", "")
                if filled == 0 or status not in ("SUCCESS", "EXITED"):
                    continue

                net = None

                # Priority 1: reconciled_pnl (cash_ledger.py ground truth)
                rp = t.get("reconciled_pnl")
                if rp is not None:
                    net = rp

                # Priority 2: Kalshi-reconciled settlement_pnl
                if net is None and t.get("settlement_source") == "kalshi_reconciled":
                    net = t.get("settlement_pnl", 0) or 0

                # Priority 3: actual_pnl or estimated (SUCCESS trades)
                if net is None and status == "SUCCESS":
                    pnl = t.get("actual_pnl")
                    if pnl and isinstance(pnl, dict):
                        net = pnl.get("net_profit_dollars", 0)
                    else:
                        est = t.get("estimated_net_profit_cents", 0) or 0
                        net = est * filled / 100

                # Priority 4: unwind P&L (EXITED trades)
                if net is None and status == "EXITED":
                    upnl = t.get("unwind_pnl_cents")
                    if upnl is not None:
                        net = upnl / 100.0
                    else:
                        direction = t.get("direction", "")
                        pm_price = t.get("pm_price", 0) or 0
                        ufp = t.get("unwind_fill_price")
                        uqty = t.get("unwind_qty", 0) or filled
                        if ufp is not None and pm_price > 0:
                            if direction == "BUY_PM_SELL_K":
                                net = ((ufp * 100) - pm_price) * uqty / 100.0
                            else:
                                net = (pm_price - (ufp * 100)) * uqty / 100.0
                        else:
                            ulc = t.get("unwind_loss_cents", 0) or 0
                            net = -(abs(ulc) / 100.0)

                if net is not None:
                    total_pnl += net
                    trades_with_pnl += 1
                    if net > 0:
                        profitable += 1
                    else:
                        losing += 1

            # Cash P&L from live balances
            k_portfolio = self.balances.get("k_portfolio", 0)
            pm_portfolio = self.balances.get("pm_portfolio", 0)
            portfolio_total = k_portfolio + pm_portfolio
            cash_pnl = portfolio_total - STARTING_BALANCE_TOTAL

            return {
                "total_pnl_dollars": round(total_pnl, 4),
                "profitable_count": profitable,
                "losing_count": losing,
                "total_trades": trades_with_pnl,
                "total_attempts": len(all_trades),
                "total_filled": total_filled,
                "hedged_count": hedged_count,
                "unhedged_filled": unhedged_filled,
                "cash_pnl": round(cash_pnl, 2),
                "portfolio_total": round(portfolio_total, 2),
                "starting_balance": STARTING_BALANCE_TOTAL,
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

            # Extract team abbreviations from cache_key (format: sport:TEAM1-TEAM2:date)
            ck_parts = cache_key.split(":")
            teams_str = ck_parts[1] if len(ck_parts) >= 2 else ""
            teams = teams_str.split("-") if teams_str else []
            team1 = teams[0] if len(teams) >= 1 else ""
            team2 = teams[1] if len(teams) >= 2 else ""

            # Resolve full names from team_names dict
            tn = g.get("team_names", {})
            team1_full = tn.get(team1, "")
            team2_full = tn.get(team2, "")

            # Kalshi tickers
            kalshi_tickers = g.get("kalshi_tickers", {})
            ticker_list = list(kalshi_tickers.values())

            # Per-team prices and spreads from live orderbooks
            team_order = [team1, team2]
            team_prices_list = []  # [{k_bid, k_ask, pm_bid, pm_ask, spread}, ...]
            best_spread = 0.0
            k_depth_total = 0
            pm_depth_total = 0

            for team_abbr in team_order:
                tp = {"k_bid": 0, "k_ask": 0, "pm_bid": 0, "pm_ask": 0, "spread": 0.0}
                ticker = kalshi_tickers.get(team_abbr, "")
                if ticker:
                    book = self.local_books.get(ticker)
                    if book:
                        tp["k_bid"] = book.get("best_bid") or 0
                        tp["k_ask"] = book.get("best_ask") or 0
                        k_depth_total += sum(book.get("yes_bids", {}).values())

                pm_key = f"{cache_key}_{team_abbr}"
                pm = self.pm_prices.get(pm_key)
                if pm:
                    tp["pm_bid"] = round(pm.get("bid") or 0, 1)
                    tp["pm_ask"] = round(pm.get("ask") or 0, 1)

                # Per-team spread
                if tp["k_bid"] and tp["pm_ask"]:
                    spread_buy_pm = tp["k_bid"] - tp["pm_ask"]
                    spread_buy_k = tp["pm_bid"] - tp["k_ask"]
                    tp["spread"] = round(max(spread_buy_pm, spread_buy_k), 1)
                    if tp["spread"] > best_spread:
                        best_spread = tp["spread"]

                team_prices_list.append(tp)

            # PM full book depth (all levels)
            pm_book = self.pm_books.get(pm_slug, {})
            if pm_book:
                pm_depth_total = sum(l.get("size", 0) for l in pm_book.get("bids", []))
            else:
                for team_abbr in kalshi_tickers:
                    pm = self.pm_prices.get(f"{cache_key}_{team_abbr}")
                    if pm:
                        pm_depth_total += pm.get("bid_size", 0)

            # Determine status
            has_books = any(
                self.local_books.get(t) and
                (self.local_books[t].get("best_bid") or 0) > 0
                for t in ticker_list
            )
            status = "Active" if has_books else "Inactive"

            row = {
                "cache_key": cache_key,
                "game_id": game_id,
                "sport": sport,
                "date": date,
                "team1": team1,
                "team2": team2,
                "team1_full": team1_full,
                "team2_full": team2_full,
                "pm_slug": pm_slug,
                "kalshi_tickers": ticker_list,
                "best_spread": round(best_spread, 1),
                "k_depth": k_depth_total,
                "pm_depth": pm_depth_total,
                "team1_prices": team_prices_list[0] if len(team_prices_list) > 0 else None,
                "team2_prices": team_prices_list[1] if len(team_prices_list) > 1 else None,
                "status": status,
                "traded": game_id in traded_game_ids,
            }

            # Enrich with ESPN live data (scores, clock, period)
            if self.espn_scores:
                espn = self.espn_scores.get(cache_key)
                if espn:
                    row["game_status"] = espn.get("game_status", "")
                    row["game_time"] = espn.get("game_time", "")
                    row["period"] = espn.get("period", "")
                    row["clock"] = espn.get("clock", "")
                    row["team1_score"] = espn.get("team1_score", 0)
                    row["team2_score"] = espn.get("team2_score", 0)

            rows.append(row)

        # Sort: live first, then active, then by date, then by best spread
        def _sort_key(r):
            gs = r.get("game_status", "")
            if gs == "in":
                priority = 0  # live games first
            elif r["status"] == "Active":
                priority = 1
            else:
                priority = 2
            return (priority, r["date"], -r["best_spread"])

        rows.sort(key=_sort_key)
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
        pm_positions_value = self.balances.get("pm_positions_value", pm_portfolio - pm_cash)
        pm_positions_source = self.balances.get("pm_positions_source", "margin")
        return {
            "k_cash": round(k_cash, 2),
            "k_portfolio": round(k_portfolio, 2),
            "pm_cash": round(pm_cash, 2),
            "pm_portfolio": round(pm_portfolio, 2),
            "pm_positions": round(pm_positions_value, 2),
            "k_positions": round(k_portfolio - k_cash, 2),
            "pm_positions_source": pm_positions_source,
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

    # ── Specs ─────────────────────────────────────────────────────────────

    def _build_specs(self) -> dict:
        """Build specs payload for the Specs diagnostics tab."""
        from config import Config

        # ── Load trades for latency + tier stats ──
        all_trades = []
        try:
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, "r") as f:
                    all_trades = json.load(f)
        except Exception:
            pass

        # Filled trades (have actual execution data)
        filled = [t for t in all_trades if t.get("contracts_filled", 0) > 0
                  and t.get("execution_time_ms", 0) > 0]
        # Sort by timestamp descending for recency
        filled.sort(key=lambda t: t.get("timestamp", ""), reverse=True)

        # ── Latency ──
        last_trade = {}
        if filled:
            lt = filled[0]
            last_trade = {
                "pm_ms": lt.get("pm_order_ms", 0),
                "k_ms": lt.get("k_order_ms", 0),
                "total_ms": lt.get("execution_time_ms", 0),
                "sdk_used": lt.get("pm_order_ms", 999) < 100,
                "timestamp": lt.get("timestamp", ""),
                "team": lt.get("team", ""),
            }

        rolling_10 = {}
        r10 = filled[:10]
        if r10:
            rolling_10 = {
                "avg_pm_ms": round(sum(t.get("pm_order_ms", 0) for t in r10) / len(r10)),
                "avg_k_ms": round(sum(t.get("k_order_ms", 0) for t in r10) / len(r10)),
                "avg_total_ms": round(sum(t.get("execution_time_ms", 0) for t in r10) / len(r10)),
                "sdk_hit_rate": round(sum(1 for t in r10 if t.get("pm_order_ms", 999) < 100) / len(r10) * 100),
            }

        all_time = {}
        if filled:
            exec_times = [t["execution_time_ms"] for t in filled]
            sdk_count = sum(1 for t in filled if t.get("pm_order_ms", 999) < 100)
            all_time = {
                "fastest_ms": min(exec_times),
                "slowest_ms": max(exec_times),
                "sdk_success_rate": round(sdk_count / len(filled) * 100),
            }

        # ── Tier stats ──
        tier_filled = [t for t in all_trades if t.get("contracts_filled", 0) > 0]
        total_filled = len(tier_filled)
        success_count = 0
        tier1_count = 0
        tier2_count = 0
        tier3a_count = 0
        opp_hedge_count = 0
        tier3_unwind_count = 0
        unhedged_no_tier = 0
        exited_count = 0
        success_spreads = []
        exit_losses = []
        dir_settled = 0
        dir_wins = 0

        for t in all_trades:
            status = t.get("status", "")
            tier = t.get("tier", "")
            cf = t.get("contracts_filled", 0)

            if status == "SUCCESS" and not tier:
                if cf > 0:
                    success_count += 1
                    if t.get("spread_cents") is not None:
                        success_spreads.append(t["spread_cents"])
            elif tier == "TIER1_HEDGE":
                if cf > 0:
                    tier1_count += 1
                    if t.get("spread_cents") is not None:
                        success_spreads.append(t["spread_cents"])
            elif tier == "TIER2_EXIT":
                if cf > 0:
                    tier2_count += 1
            elif tier in ("TIER3A_HOLD", "TIER3A"):
                if cf > 0:
                    tier3a_count += 1
            elif tier in ("TIER3_OPPOSITE_HEDGE", "TIER3_OPPOSITE_OVERWEIGHT"):
                if cf > 0:
                    opp_hedge_count += 1
            elif tier == "TIER3_UNWIND":
                if cf > 0:
                    tier3_unwind_count += 1
            elif status == "UNHEDGED" and cf > 0:
                unhedged_no_tier += 1

            if status == "EXITED" and t.get("unwind_loss_cents") is not None:
                exit_losses.append(abs(t["unwind_loss_cents"]))
                exited_count += 1

            # Directional win rate
            if (status == "UNHEDGED" or tier in ("TIER3A_HOLD", "TIER3A", "TIER3_OPPOSITE_HEDGE", "TIER3_OPPOSITE_OVERWEIGHT")):
                sp = t.get("settlement_pnl")
                if sp is not None:
                    dir_settled += 1
                    if sp > 0:
                        dir_wins += 1

        hedge_success = success_count + tier1_count
        kalshi_fail_rate = round((total_filled - hedge_success) / total_filled * 100) if total_filled > 0 else 0
        avg_success_spread = round(sum(success_spreads) / len(success_spreads), 1) if success_spreads else 0
        avg_exit_loss = round(sum(exit_losses) / len(exit_losses), 1) if exit_losses else 0
        directional_win_rate = round(dir_wins / dir_settled * 100) if dir_settled > 0 else 0

        # ── OMI cache ──
        omi_signals = 0
        omi_live = 0
        omi_refresh_ago = None
        omi_stale = True
        if self.omi_cache is not None:
            seen = set()
            for v in self.omi_cache.signals.values():
                sid = id(v)
                if sid not in seen:
                    seen.add(sid)
                    omi_signals += 1
                    if v.get("game_status") == "live":
                        omi_live += 1
            if self.omi_cache.last_refresh > 0:
                omi_refresh_ago = round(time.time() - self.omi_cache.last_refresh)
            omi_stale = self.omi_cache.is_stale()

        # ── Connection ──
        connection = {
            "kalshi_ws": bool(self.stats.get("k_ws_connected")),
            "pm_ws": bool(self.stats.get("pm_ws_connected")),
            "k_messages": self.stats.get("k_ws_messages", 0),
            "pm_messages": self.stats.get("pm_ws_messages", 0),
            "omi_signals_cached": omi_signals,
            "omi_live_count": omi_live,
            "omi_last_refresh_ago_s": omi_refresh_ago,
            "omi_is_stale": omi_stale,
        }

        # ── Book coverage ──
        k_total = len(self.ticker_to_cache_key)
        k_active = sum(
            1 for t in self.ticker_to_cache_key
            if self.local_books.get(t) and (self.local_books[t].get("best_bid") or 0) > 0
        )
        pm_keys = set()
        pm_active_count = 0
        for t, ck in self.ticker_to_cache_key.items():
            parts = t.split("-")
            team = parts[-1] if len(parts) >= 3 else ""
            pk = f"{ck}_{team}"
            if pk not in pm_keys:
                pm_keys.add(pk)
                pm = self.pm_prices.get(pk)
                if pm and (pm.get("bid") or 0) > 0:
                    pm_active_count += 1
        # Find cache_keys with Kalshi book but no PM price
        missing_pm = []
        seen_ck = set()
        for t, ck in self.ticker_to_cache_key.items():
            if ck in seen_ck:
                continue
            seen_ck.add(ck)
            parts = t.split("-")
            team = parts[-1] if len(parts) >= 3 else ""
            pk = f"{ck}_{team}"
            book = self.local_books.get(t)
            if book and (book.get("best_bid") or 0) > 0:
                pm = self.pm_prices.get(pk)
                if not pm or (pm.get("bid") or 0) == 0:
                    missing_pm.append(ck)

        book_coverage = {
            "k_total": k_total,
            "k_active": k_active,
            "pm_total": len(pm_keys),
            "pm_active": pm_active_count,
            "missing_pm": missing_pm[:20],  # Cap to avoid payload bloat
        }

        return {
            "latency": {
                "last_trade": last_trade,
                "rolling_10": rolling_10,
                "all_time": all_time,
            },
            "deployment": {
                "git_branch": _GIT_INFO["branch"],
                "git_commit_short": _GIT_INFO["commit_short"],
                "git_commit_date": _GIT_INFO["commit_date"],
                "git_commit_msg": _GIT_INFO["commit_msg"],
                "executor_version": self.executor_version,
                "python_version": _PYTHON_VERSION,
                "server": "DO ubuntu-s-1vcpu-2gb-nyc3-01",
                "execution_mode": "LIVE" if Config.is_live() else "PAPER",
                "dry_run": Config.dry_run_mode,
            },
            "config": {
                "spread_min_cents": Config.spread_min_cents,
                "min_contracts": Config.min_contracts,
                "max_contracts": Config.max_contracts,
                "max_cost_cents": Config.max_cost_cents,
                "enable_gtc": Config.enable_gtc,
                "depth_pre_check": False,
                "max_concurrent_positions": Config.max_concurrent_positions,
                "min_ceq_hold": Config.min_ceq_hold,
                "opposite_hedge_max_cost": Config.opposite_hedge_max_cost,
                "opposite_overweight_max_cost": Config.opposite_overweight_max_cost,
                "opposite_overweight_min_ceq": Config.opposite_overweight_min_ceq,
                "max_directional_exposure_usd": Config.max_directional_exposure_usd,
                "daily_loss_limit": Config.daily_directional_loss_limit,
                "expected_slippage_cents": Config.expected_slippage_cents,
                "price_buffer_cents": Config.price_buffer_cents,
                "pm_price_buffer_cents": Config.pm_price_buffer_cents,
                "cooldown_seconds": Config.cooldown_seconds,
                "depth_cap": Config.depth_cap,
            },
            "tiers": {
                "total_filled": total_filled,
                "success_count": success_count,
                "tier1_count": tier1_count,
                "tier2_count": tier2_count,
                "tier3a_count": tier3a_count,
                "opp_hedge_count": opp_hedge_count,
                "tier3_unwind_count": tier3_unwind_count,
                "unhedged_no_tier": unhedged_no_tier,
                "kalshi_fail_rate": kalshi_fail_rate,
                "avg_success_spread": avg_success_spread,
                "avg_exit_loss": avg_exit_loss,
                "directional_win_rate": directional_win_rate,
            },
            "connection": connection,
            "book_coverage": book_coverage,
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
