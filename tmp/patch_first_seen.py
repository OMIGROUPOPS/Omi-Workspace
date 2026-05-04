#!/usr/bin/env python3
"""Fix: Move first_seen_prices assignment BEFORE volume gate in both bots."""

FIXES = {
    "tennis": "/root/Omi-Workspace/arb-executor/tennis_stb.py",
    "ncaamb": "/root/Omi-Workspace/arb-executor/ncaamb_stb.py",
}

for name, path in FIXES.items():
    with open(path) as f:
        content = f.read()
    original = content

    # The pattern: volume gate comes BEFORE first_seen_prices
    # We need to move first_seen_prices ABOVE the volume gate
    old = """                    self.ticker_volume[ticker] = vol
                    if ticker not in self.first_seen_prices:
                        lp_raw = m.get("last_price_fp", "0") or "0"
                        self.first_seen_prices[ticker] = int(round(float(lp_raw) * 100))"""

    new = """                    self.ticker_volume[ticker] = vol"""

    # First, find the volume gate + continue block to insert first_seen before it
    # Look for the pattern with the skip/continue
    if "if vol < min_vol:" in content and old in content:
        # Strategy: remove first_seen from after ticker_volume, add it before vol check
        # Step 1: Remove first_seen from its current location (keep ticker_volume)
        content = content.replace(old, new)

        # Step 2: Insert first_seen BEFORE the volume gate
        vol_gate = """                    if vol < min_vol:"""
        first_seen_block = """                    if ticker not in self.first_seen_prices:
                        lp_raw = m.get("last_price_fp", "0") or "0"
                        self.first_seen_prices[ticker] = int(round(float(lp_raw) * 100))
                    if vol < min_vol:"""

        content = content.replace(vol_gate, first_seen_block, 1)

        if content != original:
            with open(path, "w") as f:
                f.write(content)
            print(f"  [{name}] Fixed: first_seen_prices now set BEFORE volume gate")
        else:
            print(f"  [{name}] NO CHANGE")
    else:
        print(f"  [{name}] WARN: pattern not found")
        # Debug
        if old not in content:
            print(f"    old block not found")
        if "if vol < min_vol:" not in content:
            print(f"    vol gate not found")

print("Done.")
