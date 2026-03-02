#!/usr/bin/env python3
"""
reconciliation.py — Post-trade reconciliation loop.

Every 60 seconds:
1. Query Kalshi positions API for all open positions
2. Query PM positions API for all open positions
3. Compare against trades.json open positions
4. Flag and log any discrepancy to reconciliation_log.json

Start in executor event loop:
    asyncio.create_task(run_reconciliation_loop(session, kalshi_api, pm_api))
"""
import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

TRADES_FILE = os.path.join(os.path.dirname(__file__), "trades.json")
RECON_LOG = os.path.join(os.path.dirname(__file__), "reconciliation_log.json")
INTERVAL_SECONDS = 60


def _load_trades() -> List[Dict]:
    try:
        with open(TRADES_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _get_open_positions_from_trades(trades: List[Dict]) -> Dict[str, Dict]:
    """Extract open positions from trades.json.
    Returns dict keyed by game_id with expected position info."""
    open_positions = {}
    for i, t in enumerate(trades):
        status = t.get("status", "")
        if status == "SUCCESS" and t.get("hedged"):
            game_id = t.get("game_id", "")
            if not game_id:
                continue
            if t.get("settlement_pnl") is not None or t.get("reconciled_pnl") is not None:
                continue
            open_positions[game_id] = {
                "trade_index": i,
                "team": t.get("team"),
                "direction": t.get("direction"),
                "kalshi_ticker": t.get("kalshi_ticker"),
                "pm_slug": t.get("pm_slug"),
                "k_fill": t.get("kalshi_fill", 0),
                "pm_fill": t.get("pm_fill", 0),
                "k_price": t.get("k_price"),
                "pm_price": t.get("pm_price"),
                "pm_is_buy_short": t.get("pm_is_buy_short", False),
            }
    return open_positions


async def _get_kalshi_positions(session, kalshi_api) -> Dict[str, int]:
    """Get all Kalshi positions. Returns {ticker: position_count}."""
    try:
        positions = await kalshi_api.get_positions(session)
        return {ticker: pos.position for ticker, pos in positions.items()}
    except Exception as e:
        print(f"[RECON] Kalshi positions error: {e}")
        return {}


async def _get_pm_positions(session, pm_api) -> Dict[str, Dict]:
    """Get all PM positions. Returns {slug: {netPosition, ...}}."""
    try:
        positions = await pm_api.get_positions(session)
        result = {}
        if isinstance(positions, dict):
            for key, val in positions.items():
                net = val.get("netPosition", 0)
                if isinstance(net, str):
                    net = int(net) if net else 0
                if net != 0:
                    slug = val.get("marketSlug", key)
                    result[slug] = {"netPosition": net, "raw": val}
        elif isinstance(positions, list):
            for pos in positions:
                net = pos.get("netPosition", 0)
                if isinstance(net, str):
                    net = int(net) if net else 0
                if net != 0:
                    slug = pos.get("marketSlug", pos.get("slug", ""))
                    result[slug] = {"netPosition": net, "raw": pos}
        return result
    except Exception as e:
        print(f"[RECON] PM positions error: {e}")
        return {}


def _log_discrepancy(discrepancies: List[Dict]):
    """Append discrepancies to reconciliation_log.json."""
    if not discrepancies:
        return
    existing = []
    if os.path.exists(RECON_LOG):
        try:
            with open(RECON_LOG) as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.extend(discrepancies)
    if len(existing) > 1000:
        existing = existing[-1000:]
    with open(RECON_LOG, 'w') as f:
        json.dump(existing, f, indent=2)


async def reconcile_once(session, kalshi_api, pm_api) -> List[Dict]:
    """Run one reconciliation pass. Returns list of discrepancies."""
    trades = _load_trades()
    expected = _get_open_positions_from_trades(trades)

    k_actual = await _get_kalshi_positions(session, kalshi_api)
    pm_actual = await _get_pm_positions(session, pm_api)

    discrepancies = []
    ts = datetime.now(timezone.utc).isoformat()

    for game_id, exp in expected.items():
        ticker = exp.get("kalshi_ticker", "")
        slug = exp.get("pm_slug", "")

        # Kalshi check
        k_pos = k_actual.get(ticker, 0)
        if k_pos == 0 and exp["k_fill"] > 0:
            discrepancies.append({
                "timestamp": ts, "type": "KALSHI_MISSING",
                "game_id": game_id, "ticker": ticker,
                "expected_fill": exp["k_fill"], "actual_position": k_pos,
                "trade_index": exp["trade_index"],
            })
        elif k_pos != 0 and exp["k_fill"] != abs(k_pos):
            discrepancies.append({
                "timestamp": ts, "type": "KALSHI_QTY_MISMATCH",
                "game_id": game_id, "ticker": ticker,
                "expected_fill": exp["k_fill"], "actual_position": k_pos,
                "trade_index": exp["trade_index"],
            })

        # PM check
        pm_pos = pm_actual.get(slug, {}).get("netPosition", 0)
        expected_pm_net = exp["pm_fill"] if not exp["pm_is_buy_short"] else -exp["pm_fill"]
        if pm_pos == 0 and exp["pm_fill"] > 0:
            discrepancies.append({
                "timestamp": ts, "type": "PM_MISSING",
                "game_id": game_id, "slug": slug,
                "expected_fill": exp["pm_fill"], "expected_net": expected_pm_net,
                "actual_position": pm_pos, "trade_index": exp["trade_index"],
            })
        elif pm_pos != 0 and pm_pos != expected_pm_net:
            discrepancies.append({
                "timestamp": ts, "type": "PM_QTY_MISMATCH",
                "game_id": game_id, "slug": slug,
                "expected_net": expected_pm_net, "actual_position": pm_pos,
                "trade_index": exp["trade_index"],
            })

    # Check for phantom positions
    expected_tickers = {exp["kalshi_ticker"] for exp in expected.values()}
    expected_slugs = {exp["pm_slug"] for exp in expected.values()}

    for ticker, pos in k_actual.items():
        if ticker not in expected_tickers and pos != 0:
            discrepancies.append({
                "timestamp": ts, "type": "KALSHI_PHANTOM",
                "ticker": ticker, "position": pos,
                "note": "Position on Kalshi with no matching open trade",
            })

    for slug, pos_data in pm_actual.items():
        if slug not in expected_slugs:
            discrepancies.append({
                "timestamp": ts, "type": "PM_PHANTOM",
                "slug": slug, "position": pos_data.get("netPosition", 0),
                "note": "Position on PM with no matching open trade",
            })

    return discrepancies


async def run_reconciliation_loop(session, kalshi_api, pm_api):
    """Background task: reconcile every 60 seconds."""
    print("[RECON] Reconciliation loop started (interval=60s)")
    while True:
        try:
            await asyncio.sleep(INTERVAL_SECONDS)
            discrepancies = await reconcile_once(session, kalshi_api, pm_api)
            if discrepancies:
                print(f"[!!!RECON!!!] {len(discrepancies)} discrepancies found:")
                for d in discrepancies:
                    dtype = d.get('type', '?')
                    print(f"  [{dtype}] {json.dumps(d)}")
                _log_discrepancy(discrepancies)
            else:
                now = time.strftime('%H:%M:%S')
                print(f"[RECON] All positions reconciled OK ({now})")
        except asyncio.CancelledError:
            print("[RECON] Reconciliation loop cancelled")
            break
        except Exception as e:
            print(f"[RECON] Reconciliation error: {e}")
            await asyncio.sleep(10)
