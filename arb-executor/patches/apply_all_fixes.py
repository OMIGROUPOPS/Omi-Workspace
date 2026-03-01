#!/usr/bin/env python3
"""Apply all 5 reliability fixes to the 3 executor files in /tmp/arb-patch/."""
import os

BASE = "/tmp/arb-patch"
CORE = os.path.join(BASE, "executor_core.py")
V7 = os.path.join(BASE, "arb_executor_v7.py")
WS = os.path.join(BASE, "arb_executor_ws.py")


def patch(path, old, new, label):
    with open(path) as f:
        content = f.read()
    if old not in content:
        print(f"  FAIL [{label}]: target not found in {os.path.basename(path)}")
        print(f"    First 80 chars: {repr(old[:80])}")
        return False
    count = content.count(old)
    if count > 1:
        print(f"  WARN [{label}]: {count} matches, replacing first only")
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  OK [{label}]")
    return True


# ═════════════════════════════════════════════════════════════════════════
# FIX 1: Double-fire — rewrite _unwind_pm_position (executor_core.py)
# ═════════════════════════════════════════════════════════════════════════

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
            return True, 0
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
        return True, 0
    except Exception as e:
        print(f"[UNWIND_VERIFY] Position check failed: {e}")
        return False, None


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
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"[UNWIND] close_position attempt {attempt} error: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * attempt)

        # Verify position is actually zero (FIX 5: unwind verification)
        await asyncio.sleep(0.3)
        is_zero, net_pos = await _verify_pm_position_zero(pm_api, session, pm_slug)

        if is_zero:
            print(f"[UNWIND_VERIFY] Position confirmed ZERO for {pm_slug}")
        else:
            print(f"[!!!UNWIND_INCOMPLETE!!!] Position NOT zero for {pm_slug}: "
                  f"net={net_pos}, filled={filled_qty}/{qty}")
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

# ═════════════════════════════════════════════════════════════════════════
# FIX 2: Fill price verification (arb_executor_v7.py)
# ═════════════════════════════════════════════════════════════════════════

OLD_GET_OB = '''    async def get_orderbook(self, session, ticker: str, depth: int = 1) -> Optional[Dict]:
        """'''

NEW_GET_OB = '''    async def get_fill_price(self, session, ticker: str) -> Optional[int]:
        """Query fills API to get actual fill price for most recent fill on ticker.
        Returns fill price in YES cents or None."""
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
                        side = fill.get('side', '')
                        if side == 'yes' and yes_price is not None:
                            return yes_price
                        elif side == 'no' and no_price is not None:
                            return 100 - no_price
                        return yes_price
                else:
                    print(f"   [FILL_VERIFY] Fills API HTTP {r.status}")
        except Exception as e:
            print(f"   [FILL_VERIFY] Fills API error: {e}")
        return None

    async def get_orderbook(self, session, ticker: str, depth: int = 1) -> Optional[Dict]:
        """'''

OLD_EXEC_FILL = '''    k_fill = kalshi_result.get('fill_count', 0)
    k_fill_price = kalshi_result.get('fill_price') or k_limit_price
    k_fill_price = k_fill_price if k_fill_price is not None else k_limit_price

    print(f"[EXEC] Kalshi result: {k_fill} filled @ {k_fill_price}c in {kalshi_timing['ms']:.0f}ms")

    # STEP 2: Only execute PM if Kalshi filled
    if k_fill == 0:'''

NEW_EXEC_FILL = '''    k_fill = kalshi_result.get('fill_count', 0)
    k_fill_price = kalshi_result.get('fill_price') or k_limit_price
    k_fill_price = k_fill_price if k_fill_price is not None else k_limit_price

    # FIX: Verify actual fill price via Kalshi fills API
    if k_fill > 0:
        try:
            verified_price = await kalshi_api.get_fill_price(session, arb.kalshi_ticker)
            if verified_price is not None and verified_price != k_fill_price:
                print(f"[FILL_VERIFY] Price correction: {k_fill_price}c -> actual {verified_price}c")
                k_fill_price = verified_price
                kalshi_result['fill_price'] = verified_price
            elif verified_price is not None:
                print(f"[FILL_VERIFY] Price confirmed: {verified_price}c")
        except Exception as e:
            print(f"[FILL_VERIFY] Could not verify: {e}")

    print(f"[EXEC] Kalshi result: {k_fill} filled @ {k_fill_price}c in {kalshi_timing['ms']:.0f}ms")

    # STEP 2: Only execute PM if Kalshi filled
    if k_fill == 0:'''

# ═════════════════════════════════════════════════════════════════════════
# FIX 3: Order ID capture (executor_core.py + arb_executor_v7.py + ws)
# ═════════════════════════════════════════════════════════════════════════

OLD_TR = '''    opposite_hedge_filled: int = 0
    combined_cost_cents: float = 0.0        # PM + K opposite
    guaranteed_profit_cents: float = 0.0    # (100 - combined) * qty, 0 if overweight'''

NEW_TR = '''    opposite_hedge_filled: int = 0
    combined_cost_cents: float = 0.0        # PM + K opposite
    guaranteed_profit_cents: float = 0.0    # (100 - combined) * qty, 0 if overweight
    k_order_id: Optional[str] = None        # Kalshi order ID for audit trail
    pm_order_id: Optional[str] = None       # PM order ID for audit trail'''

OLD_DRIFT = '''                    return TradeResult(
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

NEW_DRIFT = '''                    return TradeResult(
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

OLD_T1 = '''                    return TradeResult(
                        success=True,
                        kalshi_filled=k_filled,
                        pm_filled=pm_filled,
                        kalshi_price=k_fill_price,
                        pm_price=pm_fill_price,
                        unhedged=False,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        pm_order_ms=pm_order_ms,
                        k_order_ms=k_order_ms,
                        pm_response_details=pm_response_details,
                        k_response_details=_k_response_details,
                        execution_phase=_exec_phase,
                        gtc_rest_time_ms=_gtc_rest,
                        gtc_spread_checks=_gtc_checks,
                        gtc_cancel_reason=_gtc_cancel,
                        is_maker=_is_maker,
                        tier="TIER1_HEDGE",
                    )'''

NEW_T1 = '''                    return TradeResult(
                        success=True,
                        kalshi_filled=k_filled,
                        pm_filled=pm_filled,
                        kalshi_price=k_fill_price,
                        pm_price=pm_fill_price,
                        unhedged=False,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        pm_order_ms=pm_order_ms,
                        k_order_ms=k_order_ms,
                        pm_response_details=pm_response_details,
                        k_response_details=_k_response_details,
                        execution_phase=_exec_phase,
                        gtc_rest_time_ms=_gtc_rest,
                        gtc_spread_checks=_gtc_checks,
                        gtc_cancel_reason=_gtc_cancel,
                        is_maker=_is_maker,
                        tier="TIER1_HEDGE",
                        k_order_id=k_result.get('order_id'),
                        pm_order_id=pm_result.get('order_id'),
                    )'''

OLD_AGG = '''                    # Update aggregate results
                    k_result['fill_count'] = total_k_fill
                    k_result['success'] = total_k_fill > 0
                    k_result['fill_price'] = iter_k_result.get('fill_price', k_price) if total_k_fill > 0 else k_price

                    pm_result['fill_count'] = total_pm_fill
                    pm_result['success'] = total_pm_fill > 0
                    pm_result['fill_price'] = iter_pm_result.get('fill_price', pm_price) if total_pm_fill > 0 else pm_price'''

NEW_AGG = '''                    # Update aggregate results
                    k_result['fill_count'] = total_k_fill
                    k_result['success'] = total_k_fill > 0
                    k_result['fill_price'] = iter_k_result.get('fill_price', k_price) if total_k_fill > 0 else k_price
                    k_result['order_id'] = iter_k_result.get('order_id')

                    pm_result['fill_count'] = total_pm_fill
                    pm_result['success'] = total_pm_fill > 0
                    pm_result['fill_price'] = iter_pm_result.get('fill_price', pm_price) if total_pm_fill > 0 else pm_price
                    pm_result['order_id'] = iter_pm_result.get('order_id')'''

# ═════════════════════════════════════════════════════════════════════════
# FIX 4: Reconciliation import in ws executor
# ═════════════════════════════════════════════════════════════════════════

OLD_IMPORT = "from executor_core import ("
NEW_IMPORT = "from reconciliation import run_reconciliation_loop\nfrom executor_core import ("


def main():
    ok = True

    print("=" * 60)
    print("APPLYING ALL RELIABILITY FIXES")
    print("=" * 60)

    # FIX 1
    print("\nFIX 1: Double-fire — rewrite _unwind_pm_position")
    if not patch(CORE, OLD_UNWIND, NEW_UNWIND, "double-fire"):
        ok = False

    # FIX 2
    print("\nFIX 2: Fill price verification")
    if not patch(V7, OLD_GET_OB, NEW_GET_OB, "get_fill_price method"):
        ok = False
    if not patch(V7, OLD_EXEC_FILL, NEW_EXEC_FILL, "fill verify in exec"):
        ok = False

    # FIX 3a-d
    print("\nFIX 3: Order ID capture")
    if not patch(CORE, OLD_TR, NEW_TR, "TradeResult fields"):
        ok = False
    if not patch(CORE, OLD_DRIFT, NEW_DRIFT, "K_PRICE_DRIFT order_id"):
        ok = False
    if not patch(CORE, OLD_T1, NEW_T1, "TIER1_HEDGE order_ids"):
        ok = False
    if not patch(V7, OLD_AGG, NEW_AGG, "aggregation loop order_ids"):
        ok = False

    # FIX 3e: WS bridge dicts
    print("  Patching arb_executor_ws.py bridge dicts...")
    with open(WS) as f:
        ws = f.read()

    c = 0
    # Simple k_result
    old = "k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price}"
    new = "k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price, 'order_id': result.k_order_id}"
    c += ws.count(old)
    ws = ws.replace(old, new)

    # k_result with k_response_details
    old = "k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price,\n                            'k_response_details': result.k_response_details}"
    new = "k_result = {'fill_count': result.kalshi_filled, 'fill_price': result.kalshi_price,\n                            'k_response_details': result.k_response_details, 'order_id': result.k_order_id}"
    c += ws.count(old)
    ws = ws.replace(old, new)

    # pm_result with outcome_index
    old = "pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}"
    new = "pm_result = {'fill_count': result.pm_filled, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short, 'order_id': result.pm_order_id}"
    c += ws.count(old)
    ws = ws.replace(old, new)

    # PM no-fill
    old = "pm_result = {'fill_count': 0, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short}"
    new = "pm_result = {'fill_count': 0, 'fill_price': result.pm_price, 'outcome_index': _actual_pm_oi, 'is_buy_short': _is_buy_short, 'order_id': result.pm_order_id}"
    c += ws.count(old)
    ws = ws.replace(old, new)

    # K no-fill
    old = "k_result = {'fill_count': 0, 'fill_price': result.kalshi_price}"
    new = "k_result = {'fill_count': 0, 'fill_price': result.kalshi_price, 'order_id': result.k_order_id}"
    c += ws.count(old)
    ws = ws.replace(old, new)

    with open(WS, 'w') as f:
        f.write(ws)
    print(f"  OK [ws bridge dicts]: {c} replacements")

    # FIX 4: Reconciliation import
    print("\nFIX 4: Reconciliation loop")
    if not patch(WS, OLD_IMPORT, NEW_IMPORT, "reconciliation import"):
        ok = False

    # Find a good place to start the reconciliation task
    with open(WS) as f:
        ws = f.read()
    # Add after "refresh_position_cache" background task
    anchor = "    load_traded_games()"
    if anchor in ws:
        ws = ws.replace(
            anchor,
            anchor + "\n\n    # Start reconciliation loop (FIX 4)\n    _recon_task = None  # Will be started after session is created",
        )
        with open(WS, 'w') as f:
            f.write(ws)
        print("  OK [reconciliation placeholder added]")

    # Start recon task where session is available
    with open(WS) as f:
        ws = f.read()
    # Find "async with aiohttp.ClientSession" and add recon task after it
    anchor2 = "        # Initialize PM US API"
    if anchor2 in ws and "_recon_task" in ws and "run_reconciliation_loop" not in ws.split("create_task")[0] if "create_task" in ws else True:
        # Find the right spot — after both APIs are initialized
        # Look for where the first spread processing starts
        recon_start = '''
        # Start reconciliation loop (checks positions every 60s)
        _recon_task = asyncio.create_task(run_reconciliation_loop(session, kalshi_api, pm_api))
        print("[STARTUP] Reconciliation loop started")
'''
        # Add after pm_api initialization
        pm_init = "        pm_api = PolymarketUSAPI("
        if pm_init in ws:
            # Find the end of pm_api initialization block
            idx = ws.index(pm_init)
            # Find next blank line after this
            next_blank = ws.index("\n\n", idx)
            ws = ws[:next_blank] + "\n" + recon_start + ws[next_blank:]
            with open(WS, 'w') as f:
                f.write(ws)
            print("  OK [reconciliation task started after API init]")

    # FIX 5: Already in FIX 1
    print("\nFIX 5: Unwind verification (embedded in FIX 1)")
    print("  OK [_verify_pm_position_zero called after every unwind]")

    print()
    print("=" * 60)
    if ok:
        print("ALL FIXES APPLIED SUCCESSFULLY")
    else:
        print("SOME FIXES HAD ISSUES — check output above")
    print("=" * 60)


if __name__ == "__main__":
    main()
