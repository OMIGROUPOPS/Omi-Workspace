#!/usr/bin/env python3
"""
UNWIND OPPORTUNITY MONITOR
Monitors hedged arb positions for profitable unwind opportunities.
"""

import json, time, math, os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class HedgedPosition:
    game_id: str
    team: str
    sport: str
    cache_key: str
    pm_slug: str
    pm_entry_price: float
    pm_side: str
    pm_outcome_index: int
    pm_is_buy_short: bool
    k_ticker: str
    k_entry_price: float
    k_direction: str
    contracts: int
    entry_cost: float
    locked_spread: float
    pm_live_bid: float = 0.0
    pm_live_ask: float = 0.0
    k_live_bid: float = 0.0
    k_live_ask: float = 0.0
    pm_data_age_ms: int = 0
    k_data_age_ms: int = 0
    combined_exit_value: float = 0.0
    exit_fees: float = 0.0
    unwind_pnl: float = 0.0
    unwind_total: float = 0.0
    hold_pnl: float = 0.0
    unwind_is_profitable: bool = False
    unwind_beats_hold: bool = False
    entry_time: str = ""
    last_update: str = ""


def load_hedged_positions(trades_file="trades.json"):
    if not os.path.exists(trades_file):
        return []
    with open(trades_file, "r") as f:
        trades = json.load(f)
    positions = []
    for t in trades:
        if t.get("status") != "SUCCESS": continue
        if not t.get("hedged"): continue
        if t.get("settlement_pnl") is not None: continue
        if t.get("contracts_filled", 0) == 0: continue
        direction = t["direction"]
        pm_fill = t["pm_price"]
        k_fill = t["k_price"]
        if direction == "BUY_PM_SELL_K":
            k_cost = 100 - k_fill
            if t.get("pm_is_buy_short"):
                pm_cost = 100 - pm_fill
            else:
                pm_cost = pm_fill
        else:
            k_cost = k_fill
            pm_cost = 100 - pm_fill
        entry_cost = pm_cost + k_cost
        pos = HedgedPosition(
            game_id=t["game_id"], team=t["team"], sport=t.get("sport",""),
            cache_key=t.get("cache_key",""), pm_slug=t.get("pm_slug",""),
            pm_entry_price=pm_cost,
            pm_side="BUY_LONG" if direction=="BUY_PM_SELL_K" else "BUY_SHORT",
            pm_outcome_index=t.get("pm_outcome_index_used",0),
            pm_is_buy_short=t.get("pm_is_buy_short",False),
            k_ticker=t.get("kalshi_ticker",""), k_entry_price=k_cost,
            k_direction=direction, contracts=t["contracts_filled"],
            entry_cost=entry_cost, locked_spread=100-entry_cost,
            entry_time=t.get("timestamp",""),
        )
        positions.append(pos)
    return positions


def kalshi_taker_fee(price_cents):
    p = price_cents / 100.0
    return math.ceil(0.07 * p * (1 - p) * 100)


def compute_unwind(pos, pm_prices, local_books, ticker_to_cache_key=None):
    now_ms = int(time.time() * 1000)
    pm_key = f"{pos.cache_key}_{pos.team}"
    pm_data = pm_prices.get(pm_key)
    if pm_data:
        pos.pm_live_bid = pm_data.get('bid', 0)
        pos.pm_live_ask = pm_data.get('ask', 0)
        pos.pm_data_age_ms = now_ms - pm_data.get('timestamp_ms', 0)
    k_book = local_books.get(pos.k_ticker)
    if k_book:
        pos.k_live_bid = k_book.get('best_bid', 0) or 0
        pos.k_live_ask = k_book.get('best_ask', 0) or 0
        pos.k_data_age_ms = now_ms - k_book.get('last_update_ms', 0)
    if not pm_data or not k_book:
        pos.last_update = datetime.now(timezone.utc).isoformat()
        return pos
    if pos.k_direction == "BUY_PM_SELL_K":
        if pos.pm_is_buy_short:
            pm_exit_value = 100 - pos.pm_live_ask
        else:
            pm_exit_value = pos.pm_live_bid
        k_exit_value = 100 - pos.k_live_ask
    else:
        k_exit_value = pos.k_live_bid
        pm_exit_value = 100 - pos.pm_live_ask
    pos.combined_exit_value = pm_exit_value + k_exit_value
    pm_exit_fee = 0.05
    if pos.k_direction == "BUY_PM_SELL_K":
        k_exit_fee = kalshi_taker_fee(pos.k_live_ask)
    else:
        k_exit_fee = kalshi_taker_fee(pos.k_live_bid)
    pos.exit_fees = pm_exit_fee + k_exit_fee
    pos.unwind_pnl = pos.combined_exit_value - pos.entry_cost - pos.exit_fees
    pos.unwind_total = pos.unwind_pnl * pos.contracts
    entry_k_fee = kalshi_taker_fee(pos.k_entry_price)
    pos.hold_pnl = pos.locked_spread - entry_k_fee - 0.05
    pos.unwind_is_profitable = pos.unwind_pnl > 0
    pos.unwind_beats_hold = pos.unwind_pnl > pos.hold_pnl
    pos.last_update = datetime.now(timezone.utc).isoformat()
    return pos


def to_json(pos):
    return {
        "game_id": pos.game_id, "team": pos.team, "sport": pos.sport,
        "contracts": pos.contracts, "direction": pos.k_direction,
        "pm_slug": pos.pm_slug, "k_ticker": pos.k_ticker,
        "pm_entry_price": pos.pm_entry_price, "k_entry_price": pos.k_entry_price,
        "entry_cost": pos.entry_cost, "locked_spread": pos.locked_spread,
        "pm_live_bid": pos.pm_live_bid, "pm_live_ask": pos.pm_live_ask,
        "k_live_bid": pos.k_live_bid, "k_live_ask": pos.k_live_ask,
        "combined_exit_value": pos.combined_exit_value,
        "exit_fees": pos.exit_fees,
        "unwind_pnl_per_contract": pos.unwind_pnl,
        "unwind_total": pos.unwind_total,
        "hold_pnl_per_contract": pos.hold_pnl,
        "unwind_is_profitable": pos.unwind_is_profitable,
        "unwind_beats_hold": pos.unwind_beats_hold,
        "entry_time": pos.entry_time, "last_update": pos.last_update,
    }


async def unwind_monitor_loop(pm_prices, local_books, ticker_to_cache_key, interval=5.0):
    import asyncio
    print(f"[UNWIND] Monitor started — checking positions every {interval}s")
    while True:
        try:
            positions = load_hedged_positions()
            if not positions:
                await asyncio.sleep(interval)
                continue
            opportunities = []
            for pos in positions:
                compute_unwind(pos, pm_prices, local_books, ticker_to_cache_key)
                if pos.combined_exit_value > 0:
                    opportunities.append(pos)
                    if pos.unwind_beats_hold:
                        print(f"[UNWIND] ★ {pos.team} {pos.contracts}x: "
                              f"unwind={pos.unwind_pnl:+.1f}c > hold={pos.hold_pnl:+.1f}c "
                              f"(total {pos.unwind_total:+.1f}c)")
            if opportunities:
                out = [to_json(p) for p in opportunities]
                with open("unwind_opportunities.json", "w") as f:
                    json.dump(out, f, indent=2)
        except Exception as e:
            print(f"[UNWIND] Error: {e}")
        await asyncio.sleep(interval)


if __name__ == "__main__":
    positions = load_hedged_positions()
    if not positions:
        print("No open hedged positions found.")
        exit(0)
    print(f"\n{'='*80}")
    print(f"  UNWIND MONITOR — {len(positions)} open hedged positions")
    print(f"{'='*80}\n")
    total_locked = 0
    for pos in positions:
        total_locked += pos.locked_spread * pos.contracts
        entry_k_fee = kalshi_taker_fee(pos.k_entry_price)
        net_locked = pos.locked_spread - entry_k_fee - 0.05
        print(f"  {pos.team:6s} {pos.sport:4s} | {pos.contracts:3d}x | "
              f"PM={pos.pm_entry_price:.0f}c + K={pos.k_entry_price:.0f}c = {pos.entry_cost:.0f}c | "
              f"locked={pos.locked_spread:.0f}c net={net_locked:.1f}c | {pos.k_direction}")
    print(f"\n  Total locked: {total_locked:.0f}c (${total_locked/100:.2f})")
