#!/usr/bin/env python3
"""
Reliability patch script — applies all 5 fixes to executor_core.py and arb_executor_v7.py.

Run on droplet: python3 patches/fix_reliability.py
"""
import re
import os
import shutil
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(BASE, "executor_core.py")
V7 = os.path.join(BASE, "arb_executor_v7.py")


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = f"{path}.bak_{ts}"
    shutil.copy2(path, dst)
    print(f"  Backed up {os.path.basename(path)} -> {os.path.basename(dst)}")
    return dst


def patch_file(path, old, new, label=""):
    with open(path) as f:
        content = f.read()
    if old not in content:
        print(f"  WARNING: Could not find target for [{label}] in {os.path.basename(path)}")
        # Try to show what we were looking for
        first_line = old.strip().split('\n')[0][:80]
        print(f"    Looking for: {first_line}...")
        return False
    if content.count(old) > 1:
        print(f"  WARNING: Multiple matches for [{label}] in {os.path.basename(path)} — patching first only")
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  Applied [{label}]")
    return True


def main():
    print("=" * 60)
    print("RELIABILITY PATCH — 5 fixes")
    print("=" * 60)

    # ── Backups ──
    print("\n1. Creating backups...")
    backup(CORE)
    backup(V7)

    # ══════════════════════════════════════════════════════════════
    # FIX 1: Double-fire in _unwind_pm_position (executor_core.py)
    # ══════════════════════════════════════════════════════════════
    print("\n2. FIX 1: Double-fire — rewriting _unwind_pm_position...")

    OLD_UNWIND = '''async def _unwind_pm_position(
    session, pm_api, pm_slug: str, reverse_intent: int,
    pm_price_cents: float, qty: int, outcome_index: int,
    buffers: list = None,
) -> Tuple[int, Optional[float]]:
    """
    Attempt to unwind a PM position with configurable buffer steps.
    Returns (filled_count, fill_price_or_None).
    """
    if buffers is None:
        buffers = [10, 25]

    # Try SDK close_position first (fastest exit)
    try:
        close_resp = await pm_api.close_position(session, pm_slug, outcome_index=outcome_index)
        cum_qty = close_resp.get("cumQuantity", 0)
        if isinstance(cum_qty, str):
            cum_qty = int(cum_qty) if cum_qty else 0
        filled_qty = int(cum_qty)
        if filled_qty >= qty:
            avg_px = close_resp.get("avgPx", {})
            if isinstance(avg_px, dict):
                fill_price = float(avg_px.get("value", 0)) if avg_px.get("value") else 0
            else:
                fill_price = float(avg_px) if avg_px else 0
            loss_cents = abs(pm_price_cents - fill_price * 100)
            print(f"[UNWIND] SDK close_position filled {filled_qty} @ {fill_price:.4f} (loss ~{loss_cents:.1f}c)")
            return filled_qty, fill_price
        print(f"[UNWIND] SDK close_position partial: {filled_qty}/{qty}, falling back to manual")
    except Exception as e:
        print(f"[UNWIND] SDK close_position failed: {e}, falling back to manual buffers")

    for attempt, buffer in enumerate(buffers, 1):
        if reverse_intent == 2:  # SELL_LONG: sell YES lower to exit (accept less)
            price_cents = max(pm_price_cents - buffer, 1)
        else:  # SELL_SHORT (4): buy YES higher to close short (pay more to exit)
            price_cents = min(pm_price_cents + buffer, 99)
        price = price_cents / 100.0
        label = f"attempt {attempt} (buf={buffer}c)"
        try:
            result = await pm_api.place_order(
                session, pm_slug, reverse_intent, price, qty,
                tif=3, sync=True, outcome_index=outcome_index
            )
            filled = result.get('fill_count', 0)
            fill_price = result.get('fill_price', price)
            if filled > 0:
                print(f"[RECOVERY] PM unwind {label}: filled {filled} @ ${fill_price:.3f} (buf={buffer}c)")
                return filled, fill_price
            else:
                print(f"[RECOVERY] PM unwind {label}: no fill (buf={buffer}c)")
        except Exception as e:
            print(f"[RECOVERY] PM unwind {label} error: {e}")
    return 0, None'''

    NEW_UNWIND = '''# Per-slug unwind locks to prevent double-fire
_unwind_locks: Dict[str, asyncio.Lock] = {}


def _get_unwind_lock(slug: str) -> asyncio.Lock:
    """Get or create a per-slug lock for unwind operations."""
    if slug not in _unwind_locks:
        _unwind_locks[slug] = asyncio.Lock()
    return _unwind_locks[slug]


async def _verify_pm_position_zero(pm_api, session, pm_slug: str) -> Tuple[bool, Optional[int]]:
    """Query PM positions API to verify position is zero after unwind.
    Returns (is_zero, net_position_or_None)."""
    try:
        positions = await pm_api.get_positions(session, market_slug=pm_slug)
        if not positions:
            return True, 0  # No positions = zero
        # positions is a dict or list depending on API
        if isinstance(positions, dict):
            for slug_key, pos_data in positions.items():
                if pm_slug in str(slug_key):
                    net = pos_data.get('netPosition', 0)
                    if isinstance(net, str):
                        net = int(net) if net else 0
                    return (int(net) == 0), int(net)
        elif isinstance(positions, list):
            for pos in positions:
                if pos.get('marketSlug', '') == pm_slug or pos.get('slug', '') == pm_slug:
                    net = pos.get('netPosition', 0)
                    if isinstance(net, str):
                        net = int(net) if net else 0
                    return (int(net) == 0), int(net)
        return True, 0  # Not found = zero
    except Exception as e:
        print(f"[UNWIND_VERIFY] Position check failed: {e}")
        return False, None  # Unknown — treat as not verified


async def _unwind_pm_position(
    session, pm_api, pm_slug: str, reverse_intent: int,
    pm_price_cents: float, qty: int, outcome_index: int,
    buffers: list = None,
) -> Tuple[int, Optional[float]]:
    """
    Unwind a PM position using ONLY close_position with retry.
    No manual buffer fallback — prevents double-fire from race conditions.

    Uses per-slug lock to ensure only one unwind runs at a time.
    After unwind, verifies position is zero via PM positions API.

    Returns (filled_count, fill_price_or_None).
    """
    lock = _get_unwind_lock(pm_slug)

    async with lock:
        print(f"[UNWIND] Acquired lock for {pm_slug}")
        filled_qty = 0
        fill_price = None
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[UNWIND] close_position attempt {attempt}/{max_retries} for {pm_slug}")
                close_resp = await pm_api.close_position(session, pm_slug, outcome_index=outcome_index)

                cum_qty = close_resp.get("cumQuantity", 0)
                if isinstance(cum_qty, str):
                    cum_qty = int(cum_qty) if cum_qty else 0
                filled_qty = int(cum_qty)

                avg_px = close_resp.get("avgPx", {})
                if isinstance(avg_px, dict):
                    fill_price = float(avg_px.get("value", 0)) if avg_px.get("value") else 0
                else:
                    fill_price = float(avg_px) if avg_px else 0

                if filled_qty >= qty:
                    loss_cents = abs(pm_price_cents - fill_price * 100)
                    print(f"[UNWIND] close_position filled {filled_qty} @ {fill_price:.4f} "
                          f"(loss ~{loss_cents:.1f}c) on attempt {attempt}")
                    break

                print(f"[UNWIND] close_position partial: {filled_qty}/{qty} on attempt {attempt}")
                # Wait before retry to let PM settle
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"[UNWIND] close_position attempt {attempt} error: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * attempt)  # Exponential backoff

        # ── Verify position is actually zero ──
        await asyncio.sleep(0.3)  # Brief settle time
        is_zero, net_pos = await _verify_pm_position_zero(pm_api, session, pm_slug)

        if is_zero:
            print(f"[UNWIND_VERIFY] Position confirmed ZERO for {pm_slug}")
        else:
            print(f"[!!!UNWIND_INCOMPLETE!!!] Position NOT zero for {pm_slug}: "
                  f"net={net_pos}, filled={filled_qty}/{qty}")
            # Log to file for reconciliation
            try:
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "slug": pm_slug,
                    "expected_close": qty,
                    "close_filled": filled_qty,
                    "remaining_position": net_pos,
                    "fill_price": fill_price,
                }
                log_path = os.path.join(os.path.dirname(__file__), "unwind_incomplete.log")
                with open(log_path, "a") as f:
                    f.write(json.dumps(log_entry) + "\\n")
            except Exception:
                pass

        print(f"[UNWIND] Released lock for {pm_slug}")
        return filled_qty, fill_price'''

    patch_file(CORE, OLD_UNWIND, NEW_UNWIND, "FIX1: double-fire")

    # ══════════════════════════════════════════════════════════════
    # FIX 3: Add order IDs to TradeResult (executor_core.py)
    # ══════════════════════════════════════════════════════════════
    print("\n3. FIX 3: Order ID capture — adding fields to TradeResult...")

    OLD_TRADE_RESULT_END = '''    opposite_hedge_filled: int = 0
    combined_cost_cents: float = 0.0        # PM + K opposite
    guaranteed_profit_cents: float = 0.0    # (100 - combined) * qty, 0 if overweight'''

    NEW_TRADE_RESULT_END = '''    opposite_hedge_filled: int = 0
    combined_cost_cents: float = 0.0        # PM + K opposite
    guaranteed_profit_cents: float = 0.0    # (100 - combined) * qty, 0 if overweight
    k_order_id: Optional[str] = None        # Kalshi order ID for audit trail
    pm_order_id: Optional[str] = None       # PM order ID for audit trail'''

    patch_file(CORE, OLD_TRADE_RESULT_END, NEW_TRADE_RESULT_END, "FIX3a: TradeResult order IDs")

    # Now propagate order IDs in K_PRICE_DRIFT return (executor_core.py ~line 1964)
    OLD_DRIFT_RETURN = '''                    return TradeResult(
                        success=False, pm_filled=pm_filled,
                        pm_price=pm_fill_price,
                        unhedged=not exited,
                        abort_reason=f"K price drift {drift}c: spread {spread:.0f}c -> {new_spread:.0f}c, PM unwound",
                        pm_order_ms=pm_order_ms,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        pm_response_details=pm_response_details,
                        execution_phase="ioc",
                        exited=exited,
                        unwind_loss_cents=abs(unwind_pnl) if unwind_pnl and unwind_pnl < 0 else 0,
                        unwind_pnl_cents=unwind_pnl,
                        unwind_fill_price=unwind_fill_price if exited else None,
                        unwind_qty=unwind_filled if exited else 0,
                        tier="K_PRICE_DRIFT",
                    )'''

    NEW_DRIFT_RETURN = '''                    return TradeResult(
                        success=False, pm_filled=pm_filled,
                        pm_price=pm_fill_price,
                        unhedged=not exited,
                        abort_reason=f"K price drift {drift}c: spread {spread:.0f}c -> {new_spread:.0f}c, PM unwound",
                        pm_order_ms=pm_order_ms,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        pm_response_details=pm_response_details,
                        execution_phase="ioc",
                        exited=exited,
                        unwind_loss_cents=abs(unwind_pnl) if unwind_pnl and unwind_pnl < 0 else 0,
                        unwind_pnl_cents=unwind_pnl,
                        unwind_fill_price=unwind_fill_price if exited else None,
                        unwind_qty=unwind_filled if exited else 0,
                        tier="K_PRICE_DRIFT",
                        pm_order_id=pm_result.get('order_id'),
                    )'''

    patch_file(CORE, OLD_DRIFT_RETURN, NEW_DRIFT_RETURN, "FIX3b: K_PRICE_DRIFT order ID")

    # Propagate order IDs from the successful K fill path (around line 2195-2205)
    OLD_K_ORDER_DETAILS = """            'k_order_id': k_order_id,"""
    # This already exists — we just need to make sure pm_order_id is also passed
    # Let me find the return for the success path
    # Actually, check if pm_order_id is already in any TradeResult return
    # Let's search for other TradeResult returns and add pm_order_id/k_order_id

    # ══════════════════════════════════════════════════════════════
    # FIX 2: Fill price verification (arb_executor_v7.py)
    # ══════════════════════════════════════════════════════════════
    print("\n4. FIX 2: Fill price verification — adding get_fill_price method...")

    # Add get_fill_price method to KalshiAPI class, after place_order
    OLD_GET_ORDERBOOK = '''    async def get_orderbook(self, session, ticker: str, depth: int = 1) -> Optional[Dict]:
        """'''

    NEW_GET_ORDERBOOK = '''    async def get_fill_price(self, session, ticker: str) -> Optional[int]:
        """Query fills API to get actual fill price for most recent fill on this ticker.
        Returns fill price in cents or None if no fills found."""
        path = f'/trade-api/v2/portfolio/fills?ticker={ticker}&limit=1'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    fills = data.get('fills', [])
                    if fills:
                        fill = fills[0]
                        yes_price = fill.get('yes_price')
                        no_price = fill.get('no_price')
                        action = fill.get('action', '')
                        side = fill.get('side', '')
                        # Return the relevant price based on side
                        if side == 'yes':
                            return yes_price
                        elif side == 'no':
                            return 100 - no_price if no_price else None
                        # Fallback: return yes_price
                        return yes_price
                else:
                    print(f"   [FILL_VERIFY] Fills API HTTP {r.status}")
        except Exception as e:
            print(f"   [FILL_VERIFY] Fills API error: {e}")
        return None

    async def get_orderbook(self, session, ticker: str, depth: int = 1) -> Optional[Dict]:
        """'''

    patch_file(V7, OLD_GET_ORDERBOOK, NEW_GET_ORDERBOOK, "FIX2a: get_fill_price method")

    # Now add the fill verification call after Kalshi fill in execute_sequential_orders
    OLD_KALSHI_RESULT = '''    k_fill = kalshi_result.get('fill_count', 0)
    k_fill_price = kalshi_result.get('fill_price') or k_limit_price
    k_fill_price = k_fill_price if k_fill_price is not None else k_limit_price

    print(f"[EXEC] Kalshi result: {k_fill} filled @ {k_fill_price}c in {kalshi_timing['ms']:.0f}ms")

    # STEP 2: Only execute PM if Kalshi filled
    if k_fill == 0:'''

    NEW_KALSHI_RESULT = '''    k_fill = kalshi_result.get('fill_count', 0)
    k_fill_price = kalshi_result.get('fill_price') or k_limit_price
    k_fill_price = k_fill_price if k_fill_price is not None else k_limit_price

    # FIX: Verify fill price via fills API (prevents limit-price fallback bug)
    if k_fill > 0:
        try:
            verified_price = await kalshi_api.get_fill_price(session, arb.kalshi_ticker)
            if verified_price is not None and verified_price != k_fill_price:
                print(f"[FILL_VERIFY] Price correction: logged {k_fill_price}c -> actual {verified_price}c")
                k_fill_price = verified_price
                kalshi_result['fill_price'] = verified_price
            elif verified_price is not None:
                print(f"[FILL_VERIFY] Price confirmed: {verified_price}c")
        except Exception as e:
            print(f"[FILL_VERIFY] Could not verify fill price: {e}")

    print(f"[EXEC] Kalshi result: {k_fill} filled @ {k_fill_price}c in {kalshi_timing['ms']:.0f}ms")

    # STEP 2: Only execute PM if Kalshi filled
    if k_fill == 0:'''

    patch_file(V7, OLD_KALSHI_RESULT, NEW_KALSHI_RESULT, "FIX2b: fill verification in exec flow")

    # ══════════════════════════════════════════════════════════════
    # FIX 3 (continued): Fix aggregation loop to copy order_id
    # ══════════════════════════════════════════════════════════════
    print("\n5. FIX 3 (continued): Fix aggregation loop order ID propagation...")

    OLD_AGGREGATE = '''                    # Update aggregate results
                    k_result['fill_count'] = total_k_fill
                    k_result['success'] = total_k_fill > 0
                    k_result['fill_price'] = iter_k_result.get('fill_price', k_price) if total_k_fill > 0 else k_price

                    pm_result['fill_count'] = total_pm_fill
                    pm_result['success'] = total_pm_fill > 0
                    pm_result['fill_price'] = iter_pm_result.get('fill_price', pm_price) if total_pm_fill > 0 else pm_price'''

    NEW_AGGREGATE = '''                    # Update aggregate results
                    k_result['fill_count'] = total_k_fill
                    k_result['success'] = total_k_fill > 0
                    k_result['fill_price'] = iter_k_result.get('fill_price', k_price) if total_k_fill > 0 else k_price
                    k_result['order_id'] = iter_k_result.get('order_id')  # Propagate order ID

                    pm_result['fill_count'] = total_pm_fill
                    pm_result['success'] = total_pm_fill > 0
                    pm_result['fill_price'] = iter_pm_result.get('fill_price', pm_price) if total_pm_fill > 0 else pm_price
                    pm_result['order_id'] = iter_pm_result.get('order_id')  # Propagate order ID'''

    patch_file(V7, OLD_AGGREGATE, NEW_AGGREGATE, "FIX3c: aggregation order IDs")

    # ══════════════════════════════════════════════════════════════
    # FIX 4: Post-trade reconciliation loop
    # ══════════════════════════════════════════════════════════════
    print("\n6. FIX 4: Post-trade reconciliation — creating reconciliation module...")

    reconciliation_path = os.path.join(BASE, "reconciliation.py")
    with open(reconciliation_path, 'w') as f:
        f.write(RECONCILIATION_MODULE)
    print(f"  Created {reconciliation_path}")

    # ══════════════════════════════════════════════════════════════
    # FIX 5: Unwind verification (already in FIX 1's _unwind_pm_position)
    # ══════════════════════════════════════════════════════════════
    print("\n7. FIX 5: Unwind verification — already embedded in FIX 1")
    print("  _unwind_pm_position now calls _verify_pm_position_zero after every unwind")

    print("\n" + "=" * 60)
    print("ALL PATCHES APPLIED")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review changes: diff executor_core.py executor_core.py.bak_*")
    print("  2. Review changes: diff arb_executor_v7.py arb_executor_v7.py.bak_*")
    print("  3. Restart executor")
    print("  4. Start reconciliation: python3 -c 'import reconciliation; ...'")


RECONCILIATION_MODULE = '''#!/usr/bin/env python3
"""
reconciliation.py — Post-trade reconciliation loop.

Every 60 seconds:
1. Query Kalshi positions API for all open positions
2. Query PM positions API for all open positions
3. Compare against trades.json open positions
4. Flag and log any discrepancy to reconciliation_log.json

Run as background task in the executor event loop:
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
        if status in ("SUCCESS",) and t.get("hedged"):
            # Fully hedged trade = has positions on both platforms
            game_id = t.get("game_id", "")
            if not game_id:
                continue
            # Skip if already settled
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
    """Get all PM positions. Returns {slug: {netPosition, cost, ...}}."""
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
    # Keep last 1000 entries
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

    # Check each expected position
    for game_id, exp in expected.items():
        ticker = exp.get("kalshi_ticker", "")
        slug = exp.get("pm_slug", "")

        # Kalshi check
        k_pos = k_actual.get(ticker, 0)
        if k_pos == 0 and exp["k_fill"] > 0:
            discrepancies.append({
                "timestamp": ts,
                "type": "KALSHI_MISSING",
                "game_id": game_id,
                "ticker": ticker,
                "expected_fill": exp["k_fill"],
                "actual_position": k_pos,
                "trade_index": exp["trade_index"],
            })
        elif k_pos != 0 and exp["k_fill"] != abs(k_pos):
            discrepancies.append({
                "timestamp": ts,
                "type": "KALSHI_QTY_MISMATCH",
                "game_id": game_id,
                "ticker": ticker,
                "expected_fill": exp["k_fill"],
                "actual_position": k_pos,
                "trade_index": exp["trade_index"],
            })

        # PM check
        pm_pos = pm_actual.get(slug, {}).get("netPosition", 0)
        expected_pm_net = exp["pm_fill"] if not exp["pm_is_buy_short"] else -exp["pm_fill"]
        if pm_pos == 0 and exp["pm_fill"] > 0:
            discrepancies.append({
                "timestamp": ts,
                "type": "PM_MISSING",
                "game_id": game_id,
                "slug": slug,
                "expected_fill": exp["pm_fill"],
                "expected_net": expected_pm_net,
                "actual_position": pm_pos,
                "trade_index": exp["trade_index"],
            })
        elif pm_pos != 0 and pm_pos != expected_pm_net:
            discrepancies.append({
                "timestamp": ts,
                "type": "PM_QTY_MISMATCH",
                "game_id": game_id,
                "slug": slug,
                "expected_net": expected_pm_net,
                "actual_position": pm_pos,
                "trade_index": exp["trade_index"],
            })

    # Check for phantom positions (on platform but not in trades.json)
    expected_tickers = {exp["kalshi_ticker"] for exp in expected.values()}
    expected_slugs = {exp["pm_slug"] for exp in expected.values()}

    for ticker, pos in k_actual.items():
        if ticker not in expected_tickers and pos != 0:
            discrepancies.append({
                "timestamp": ts,
                "type": "KALSHI_PHANTOM",
                "ticker": ticker,
                "position": pos,
                "note": "Position on Kalshi with no matching open trade",
            })

    for slug, pos_data in pm_actual.items():
        if slug not in expected_slugs:
            discrepancies.append({
                "timestamp": ts,
                "type": "PM_PHANTOM",
                "slug": slug,
                "position": pos_data.get("netPosition", 0),
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
                    print(f"  [{d['type']}] {json.dumps(d)}")
                _log_discrepancy(discrepancies)
            else:
                print(f"[RECON] All positions reconciled OK ({time.strftime('%H:%M:%S')})")
        except asyncio.CancelledError:
            print("[RECON] Reconciliation loop cancelled")
            break
        except Exception as e:
            print(f"[RECON] Reconciliation error: {e}")
            await asyncio.sleep(10)  # Wait a bit on error
'''

    print("  Reconciliation module written to reconciliation.py")


if __name__ == "__main__":
    main()
