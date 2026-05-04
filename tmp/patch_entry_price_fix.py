#!/usr/bin/env python3
"""Fix entry_ask to use actual avg fill price instead of limit order price.

BUG: entry_ask stores the limit order price (e.g., 59c), but the actual fill
can be higher due to retries at higher asks (e.g., 60.72c avg → rounds to 61c).
All exit floor calculations use entry_ask, so the floor is wrong.

FIX: After buy confirmation, fetch all buy fills from fills API, compute
volume-weighted average, and update entry_ask + sell_price.
"""

def patch_file(filepath, patches):
    with open(filepath) as f:
        content = f.read()
    for old, new, desc in patches:
        if old not in content:
            print(f"  [WARN] Patch '{desc}' - not found in {filepath}")
            continue
        if content.count(old) > 1:
            print(f"  [WARN] Patch '{desc}' - found {content.count(old)} times, replacing first")
            content = content.replace(old, new, 1)
        else:
            content = content.replace(old, new)
        print(f"  [OK] {desc}")
    with open(filepath, "w") as f:
        f.write(content)


# ============================================================
# TENNIS_STB.PY
# ============================================================
print("=" * 60)
print("Patching tennis_stb.py")
print("=" * 60)

tennis_patches = []

# PATCH 1: Replace _get_actual_entry_price with volume-weighted average version
tennis_patches.append((
    '''    async def _get_actual_entry_price(self, ticker: str) -> Optional[int]:
        """Get the actual buy price from fills history (not avg_price)."""
        path = f"/trade-api/v2/portfolio/fills?ticker={ticker}&limit=50"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return None
        # Find the most recent buy fill
        for f in result.get("fills", []):
            if f.get("action") == "buy" and f.get("side") == "yes":
                return _parse_price(f.get("yes_price_dollars", f.get("yes_price")))
        return None''',
    '''    async def _get_actual_entry_price(self, ticker: str) -> Optional[int]:
        """Get volume-weighted avg buy price from fills history."""
        path = f"/trade-api/v2/portfolio/fills?ticker={ticker}&limit=50"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return None
        total_cost = 0
        total_ct = 0
        for f in result.get("fills", []):
            if f.get("action") == "buy" and f.get("side") == "yes":
                price = _parse_price(f.get("yes_price_dollars", f.get("yes_price")))
                count = f.get("count", 1)
                if price and price > 0:
                    total_cost += price * count
                    total_ct += count
        if total_ct == 0:
            return None
        return round(total_cost / total_ct)''',
    "Replace _get_actual_entry_price with volume-weighted average"
))

# PATCH 2: After BUY_CONFIRMED, fetch actual fill price and update entry_ask
tennis_patches.append((
    '''                    if status == "executed":
                        pos.buy_confirmed = True
                        pos.buy_fill_ts = time.time()
                        expected_ct_cf = CONTRACTS_92PLUS if pos.entry_mode and "92plus" in pos.entry_mode else CONTRACTS
                        pos.contracts = fill_count or expected_ct_cf
                        is_chall = self._is_challenger(ticker)
                        stop_info = " (hold to settle)"
                        log(f"  [BUY_CONFIRMED] {pos.side} buy filled {pos.contracts}ct at "
                            f"{pos.entry_ask}c — posting sell at {pos.sell_price}c{stop_info}")
                        await self.place_exit_sell(ticker)''',
    '''                    if status == "executed":
                        pos.buy_confirmed = True
                        pos.buy_fill_ts = time.time()
                        expected_ct_cf = CONTRACTS_92PLUS if pos.entry_mode and "92plus" in pos.entry_mode else CONTRACTS
                        pos.contracts = fill_count or expected_ct_cf
                        # Fix entry_ask to actual fill price (not limit price)
                        actual_fill = await self._get_actual_entry_price(ticker)
                        if actual_fill and actual_fill > 0 and actual_fill != pos.entry_ask:
                            log(f"  [FILL_PRICE] {pos.side} limit={pos.entry_ask}c "
                                f"actual_fill={actual_fill}c — correcting entry_ask")
                            pos.entry_ask = actual_fill
                            pos.sell_price = min(actual_fill + EXIT_BOUNCE, 99)
                        is_chall = self._is_challenger(ticker)
                        stop_info = " (hold to settle)"
                        log(f"  [BUY_CONFIRMED] {pos.side} buy filled {pos.contracts}ct at "
                            f"{pos.entry_ask}c — posting sell at {pos.sell_price}c{stop_info}")
                        await self.place_exit_sell(ticker)''',
    "Update entry_ask to actual fill price after buy confirmation"
))

# PATCH 3: Fix _finalize_retry to update entry_ask with avg fill price
tennis_patches.append((
    '''    async def _finalize_retry(self, ticker: str, pos):''',
    '''    async def _finalize_retry(self, ticker: str, pos):
        # Fix entry_ask to actual volume-weighted avg fill price
        actual_fill = await self._get_actual_entry_price(ticker)
        if actual_fill and actual_fill > 0 and actual_fill != pos.entry_ask:
            log(f"  [FILL_PRICE] {pos.side} limit={pos.entry_ask}c "
                f"actual_fill={actual_fill}c — correcting entry_ask (retry)")
            pos.entry_ask = actual_fill
            pos.sell_price = min(actual_fill + EXIT_BOUNCE, 99)''',
    "Update entry_ask in _finalize_retry path"
))

patch_file("/root/Omi-Workspace/arb-executor/tennis_stb.py", tennis_patches)


# ============================================================
# NCAAMB_STB.PY
# ============================================================
print()
print("=" * 60)
print("Patching ncaamb_stb.py")
print("=" * 60)

ncaamb_patches = []

# PATCH 1: Replace _get_actual_entry_price with volume-weighted average version
ncaamb_patches.append((
    '''    async def _get_actual_entry_price(self, ticker: str) -> Optional[int]:
        """Get the actual buy price from fills history (not avg_price)."""
        path = f"/trade-api/v2/portfolio/fills?ticker={ticker}&limit=50"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return None
        # Find the most recent buy fill
        for f in result.get("fills", []):
            if f.get("action") == "buy" and f.get("side") == "yes":
                return _parse_price(f.get("yes_price_dollars", f.get("yes_price")))
        return None''',
    '''    async def _get_actual_entry_price(self, ticker: str) -> Optional[int]:
        """Get volume-weighted avg buy price from fills history."""
        path = f"/trade-api/v2/portfolio/fills?ticker={ticker}&limit=50"
        result = await api_get(self.session, self.api_key, self.private_key, path, self.rl)
        if not result:
            return None
        total_cost = 0
        total_ct = 0
        for f in result.get("fills", []):
            if f.get("action") == "buy" and f.get("side") == "yes":
                price = _parse_price(f.get("yes_price_dollars", f.get("yes_price")))
                count = f.get("count", 1)
                if price and price > 0:
                    total_cost += price * count
                    total_ct += count
        if total_ct == 0:
            return None
        return round(total_cost / total_ct)''',
    "Replace _get_actual_entry_price with volume-weighted average"
))

# PATCH 2: After BUY_CONFIRMED, fetch actual fill price and update entry_ask
ncaamb_patches.append((
    '''                    if status == "executed":
                        pos.buy_confirmed = True
                        pos.buy_fill_ts = time.time()
                        pos.contracts = fill_count or CONTRACTS
                        log(f"  [BUY_CONFIRMED] {pos.side} buy filled {pos.contracts}ct at "
                            f"{pos.entry_ask}c — posting sell at {pos.sell_price}c "
                            f"(hold to settle)")
                        await self.place_exit_sell(ticker)''',
    '''                    if status == "executed":
                        pos.buy_confirmed = True
                        pos.buy_fill_ts = time.time()
                        pos.contracts = fill_count or CONTRACTS
                        # Fix entry_ask to actual fill price (not limit price)
                        actual_fill = await self._get_actual_entry_price(ticker)
                        if actual_fill and actual_fill > 0 and actual_fill != pos.entry_ask:
                            log(f"  [FILL_PRICE] {pos.side} limit={pos.entry_ask}c "
                                f"actual_fill={actual_fill}c — correcting entry_ask")
                            pos.entry_ask = actual_fill
                            pos.sell_price = min(actual_fill + EXIT_BOUNCE, 99)
                        log(f"  [BUY_CONFIRMED] {pos.side} buy filled {pos.contracts}ct at "
                            f"{pos.entry_ask}c — posting sell at {pos.sell_price}c "
                            f"(hold to settle)")
                        await self.place_exit_sell(ticker)''',
    "Update entry_ask to actual fill price after buy confirmation"
))

# PATCH 3: Fix _finalize_retry to update entry_ask with avg fill price
ncaamb_patches.append((
    '''    async def _finalize_retry(self, ticker: str, pos):''',
    '''    async def _finalize_retry(self, ticker: str, pos):
        # Fix entry_ask to actual volume-weighted avg fill price
        actual_fill = await self._get_actual_entry_price(ticker)
        if actual_fill and actual_fill > 0 and actual_fill != pos.entry_ask:
            log(f"  [FILL_PRICE] {pos.side} limit={pos.entry_ask}c "
                f"actual_fill={actual_fill}c — correcting entry_ask (retry)")
            pos.entry_ask = actual_fill
            pos.sell_price = min(actual_fill + EXIT_BOUNCE, 99)''',
    "Update entry_ask in _finalize_retry path"
))

patch_file("/root/Omi-Workspace/arb-executor/ncaamb_stb.py", ncaamb_patches)

print()
print("Done. Both files patched — entry_ask now uses actual avg fill price.")
print()
print("Changes:")
print("  1. _get_actual_entry_price() now computes volume-weighted average across ALL buy fills")
print("  2. BUY_CONFIRMED path updates entry_ask from fills API before posting sell")
print("  3. _finalize_retry path updates entry_ask from fills API before posting sell")
print("  4. sell_price recalculated as actual_fill + EXIT_BOUNCE (capped at 99)")
