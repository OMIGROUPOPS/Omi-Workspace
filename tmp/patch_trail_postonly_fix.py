#!/usr/bin/env python3
"""Fix post_only for trail sells.

BUG: Trail sells are always below current bid (that's how trailing stops work).
With post_only=True, they cross the bid and get REJECTED by Kalshi.
Position left with no resting sell.

FIX: Use post_only=True only for:
  - 99c safety net (always above any realistic bid)
  - 92+ maker static sells (posted at entry+bounce, above bid at time of fill)
Trail sells use post_only=False (accept taker fill if bid hasn't dropped yet).
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

# Replace the post_only logic in place_exit_sell:
# - 99c safety net: post_only=True (well above bid, will rest)
# - 92+ static: post_only=True (static price, should rest)
# - Trail active: post_only=False (trail price is below bid by design)
tennis_patches.append((
    '''        path = "/trade-api/v2/portfolio/orders"
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
    '''        # Trail sells are below current bid by design — post_only would reject them.
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
    "Trail sells: post_only=False (below bid by design)"
))

patch_file("/root/Omi-Workspace/arb-executor/tennis_stb.py", tennis_patches)


# ============================================================
# NCAAMB_STB.PY — basketball uses fixed +7c exit, no trail
# But let's apply same logic for safety (if trail ever added)
# ============================================================
print()
print("=" * 60)
print("Patching ncaamb_stb.py")
print("=" * 60)

ncaamb_patches = []

ncaamb_patches.append((
    '''        path = "/trade-api/v2/portfolio/orders"
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
    '''        # Trail sells are below current bid by design — post_only would reject them.
        # Only use post_only for safety net / static sells.
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
    "Trail sells: post_only=False (below bid by design)"
))

patch_file("/root/Omi-Workspace/arb-executor/ncaamb_stb.py", ncaamb_patches)

print()
print("Done. Trail sells now use post_only=False.")
print("99c safety net and 92+ static sells remain post_only=True.")
