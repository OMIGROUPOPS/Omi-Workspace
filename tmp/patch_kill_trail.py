#!/usr/bin/env python3
"""Kill trailing stop on tennis. Deploy fixed +12c maker exit.

Changes:
1. EXIT_BOUNCE = 12 (was 7)
2. Remove TRAIL_CONFIGS_TENNIS, TRAIL_CEILING constants
3. Remove trail_active, trail_sell_price from Position dataclass
4. Simplify place_exit_sell: always post at sell_price with post_only=True
5. Remove _update_trailing_sell method entirely
6. Remove trail logic block from on_bbo_update
"""

def patch_file(filepath, patches):
    with open(filepath) as f:
        content = f.read()
    for old, new, desc in patches:
        if old not in content:
            print(f"  [WARN] Patch '{desc}' - not found in {filepath}")
            continue
        count = content.count(old)
        if count > 1:
            print(f"  [WARN] Patch '{desc}' - found {count} times, replacing first")
            content = content.replace(old, new, 1)
        else:
            content = content.replace(old, new)
        print(f"  [OK] {desc}")
    with open(filepath, "w") as f:
        f.write(content)


print("=" * 60)
print("Patching tennis_stb.py — kill trail, deploy fixed +12c")
print("=" * 60)

patches = []

# 1. EXIT_BOUNCE = 12
patches.append((
    'EXIT_BOUNCE = 7               # sell at entry_ask + 7c',
    'EXIT_BOUNCE = 12              # sell at entry_ask + 12c (fixed maker exit)',
    "EXIT_BOUNCE 7 -> 12"
))

# 2. Remove TRAIL_CONFIGS and TRAIL_CEILING
patches.append((
    '''
# Trailing stop config (per series)
TRAIL_CONFIGS_TENNIS = {
    "KXATPMATCH":          {"trigger": 7, "trail_width": 4},   # ATP Main: 4c trail
    "KXWTAMATCH":          {"trigger": 7, "trail_width": 4},   # WTA Main: 4c trail
    "KXATPCHALLENGERMATCH": {"trigger": 7, "trail_width": 3},  # ATP Chall: 3c trail
    "KXWTACHALLENGERMATCH": {"trigger": 7, "trail_width": 3},  # WTA Chall: 3c trail
}
TRAIL_CEILING = 99  # if bid >= 99c, sell at 99c immediately''',
    '',
    "Remove TRAIL_CONFIGS_TENNIS and TRAIL_CEILING"
))

# 3. Remove trail fields from Position dataclass
patches.append((
    '''
    # Trailing stop state
    trail_active: bool = False        # True once bid >= entry + trigger
    trail_sell_price: int = 0         # current trailing sell target''',
    '',
    "Remove trail fields from Position dataclass"
))

# 4. Simplify place_exit_sell — no safety net, no trail logic, always post_only=True
patches.append((
    '''    async def place_exit_sell(self, ticker: str):
        """Place resting sell order. STB: 99c safety net until trail activates. Maker: static."""
        pos = self.positions.get(ticker)
        if not pos:
            return

        sell_price = pos.sell_price
        # STB trades: post at 99c safety net until trail activates and sets real price
        if not pos.trail_active and "92plus" not in (pos.entry_mode or ""):
            sell_price = TRAIL_CEILING  # 99c safety net — trail will ratchet down on activation
        if sell_price > 99:
            sell_price = 99  # cap at 99c

        # Trail sells are below current bid by design — post_only would reject them.
        # Only use post_only for 99c safety net and 92+ static sells.
        use_post_only = not pos.trail_active

        path = "/trade-api/v2/portfolio/orders"
        payload = {
            "ticker": ticker,
            "action": "sell",
            "side": "yes",
            "count": pos.contracts,
            "type": "limit",
            "yes_price": sell_price,
            "client_order_id": str(uuid.uuid4()),
            "post_only": use_post_only,
        }''',
    '''    async def place_exit_sell(self, ticker: str):
        """Place resting sell order at entry+12c (STB) or static price (92+ maker)."""
        pos = self.positions.get(ticker)
        if not pos:
            return

        sell_price = min(pos.sell_price, 99)

        path = "/trade-api/v2/portfolio/orders"
        payload = {
            "ticker": ticker,
            "action": "sell",
            "side": "yes",
            "count": pos.contracts,
            "type": "limit",
            "yes_price": sell_price,
            "client_order_id": str(uuid.uuid4()),
            "post_only": True,
        }''',
    "Simplify place_exit_sell — fixed price, always post_only"
))

# 5. Remove _update_trailing_sell method entirely
patches.append((
    '''    # ------------------------------------------------------------------
    # Trailing stop sell update
    # ------------------------------------------------------------------
    async def _update_trailing_sell(self, ticker: str):
        """Cancel current resting sell and post new one at updated trail price."""
        pos = self.positions.get(ticker)
        if not pos or pos.filled or pos.settled or pos.time_stopped:
            return

        # Cancel existing sell
        if pos.sell_order_id:
            # First check if it already filled
            chk_path = f"/trade-api/v2/portfolio/orders/{pos.sell_order_id}"
            chk = await api_get(self.session, self.api_key, self.private_key, chk_path, self.rl)
            if chk:
                order = chk.get("order", {})
                status = order.get("status", "")
                if status == "executed":
                    log(f"  [TRAIL_FILLED] {pos.side} sell already filled at {pos.sell_price}c while updating trail")
                    return
                if status == "resting":
                    del_path = f"/trade-api/v2/portfolio/orders/{pos.sell_order_id}"
                    await api_delete(self.session, self.api_key, self.private_key, del_path, self.rl)
                    self.resting_sells.pop(ticker, None)
                    pos.sell_order_id = None

        # Post new sell at updated price
        await self.place_exit_sell(ticker)''',
    '',
    "Remove _update_trailing_sell method"
))

# 6. Remove trail logic block from on_bbo_update
patches.append((
    '''                # --- Trailing stop logic (STB trades only, not maker module) ---
                if pos.entry_mode == "" or "92plus" not in pos.entry_mode:
                    _tcfg_series = next((s for s in TRAIL_CONFIGS_TENNIS if ticker.startswith(s)), None)
                    if _tcfg_series:
                        tcfg = TRAIL_CONFIGS_TENNIS[_tcfg_series]
                        trigger = tcfg["trigger"]
                        trail_w = tcfg["trail_width"]
                        floor_price = pos.entry_ask + EXIT_BOUNCE

                        # CEILING: if bid >= 99c, sell at 99c immediately
                        if bid >= TRAIL_CEILING:
                            if pos.sell_price < TRAIL_CEILING:
                                log(f"[TRAIL_CEILING] {pos.side} bid={bid}c >= {TRAIL_CEILING}c "
                                    f"entry={pos.entry_ask}c — upgrading sell to {TRAIL_CEILING}c")
                                pos.trail_active = True
                                pos.trail_sell_price = TRAIL_CEILING
                                pos.sell_price = TRAIL_CEILING
                                asyncio.ensure_future(self._update_trailing_sell(ticker))
                        # Trail activation + update
                        elif bid >= pos.entry_ask + trigger:
                            new_trail = bid - trail_w
                            new_trail = max(new_trail, floor_price)
                            new_trail = min(new_trail, TRAIL_CEILING)
                            if not pos.trail_active:
                                pos.trail_active = True
                                pos.trail_sell_price = new_trail
                                # Always update on first activation: replace 99c safety net with trail price
                                log(f"[TRAIL_ON] {pos.side} bid={bid}c >= entry+{trigger}c "
                                    f"entry={pos.entry_ask}c — trail activated, sell 99c -> {new_trail}c")
                                pos.sell_price = new_trail
                                asyncio.ensure_future(self._update_trailing_sell(ticker))
                            elif new_trail > pos.trail_sell_price:
                                pos.trail_sell_price = new_trail
                                if new_trail > pos.sell_price:
                                    log(f"[TRAIL_UP] {pos.side} bid={bid}c peak={pos.max_bid_after_entry}c "
                                        f"entry={pos.entry_ask}c — sell {pos.sell_price}c -> {new_trail}c")
                                    pos.sell_price = new_trail
                                    asyncio.ensure_future(self._update_trailing_sell(ticker))''',
    '',
    "Remove trail logic from on_bbo_update"
))

patch_file("/root/Omi-Workspace/arb-executor/tennis_stb.py", patches)

print()
print("Done. Trail removed, fixed +12c maker exit deployed.")
