#!/usr/bin/env python3
"""Add missing _check_bid_stability and _log_sizing_tier helpers to ncaamb_stb.py."""

path = "/root/Omi-Workspace/arb-executor/ncaamb_stb.py"

with open(path) as f:
    content = f.read()
original = content

marker = '''    # ------------------------------------------------------------------
    # 92c+ Settlement Mode -- sustained filter
    # ------------------------------------------------------------------'''

helper = '''    def _check_bid_stability(self, ticker: str) -> tuple:
        """Check rolling 2-min bid stddev. Returns (stddev, n_points) or (None, 0)."""
        import math
        hist = self.bid_stability_history.get(ticker, [])
        if len(hist) < 5:
            return None, len(hist)
        bids = [b for _, b in hist]
        mean = sum(bids) / len(bids)
        variance = sum((b - mean) ** 2 for b in bids) / len(bids)
        return math.sqrt(variance), len(bids)

    def _log_sizing_tier(self, side: str, depth_ratio: float, stddev: float):
        """Log sizing tier classification for data collection."""
        if depth_ratio > 1.0 and stddev < 1.0:
            log(f"[TIER_A] {side} depth_ratio={depth_ratio:.3f} stddev={stddev:.1f}c — high confidence")
        elif depth_ratio >= 0.15 and stddev <= 3.0:
            log(f"[TIER_B] {side} depth_ratio={depth_ratio:.3f} stddev={stddev:.1f}c — standard")
        else:
            log(f"[TIER_C] {side} depth_ratio={depth_ratio:.3f} stddev={stddev:.1f}c — low confidence")

    # ------------------------------------------------------------------
    # 92c+ Settlement Mode -- sustained filter
    # ------------------------------------------------------------------'''

if marker in content:
    content = content.replace(marker, helper)
    with open(path, 'w') as f:
        f.write(content)
    print("Added _check_bid_stability and _log_sizing_tier to ncaamb_stb.py")
else:
    print("WARN: marker not found")
