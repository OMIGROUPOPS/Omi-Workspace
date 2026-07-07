#!/usr/bin/env python3
"""READ-ONLY conformance referee: count + sample today's jsonl for every
doctrine-relevant event class. Bot untouched."""
import json, sys
from collections import Counter

LOG = "/root/Omi-Workspace/arb-executor/logs/live_v3_20260707.jsonl"
KEYS = ["never_marketable_clamped", "buy_blocked_position_full", "buy_qty_reduced",
        "buy_guard_api_fail", "buy_blocked_conception_halt", "reconcile_exit_topup",
        "reconcile_exit_posted", "exit_skip_no_open_shares", "v4_exit_posted",
        "hold_to_settle", "post_boot_audit", "conception_halt_armed",
        "conception_halt_cleared", "expression_clamped", "aim_shadow",
        "leg2_reshuffle_reaim", "reaim_sibling_arrival", "sibling_repost_placed",
        "sibling_repost_skip", "sibling_repost_scan", "match_live_detected",
        "premarket_walk_capped", "completion_no_attempt", "complete_cross",
        "complete_cross_skip", "entry_filled", "order_error", "adoption_true_basis",
        "reconcile_v4_adopted", "window_open_set", "v4_repost_hold_same_price",
        "grace", "latch", "would_skip_walled_post", "paired_basis_skip",
        "cell_not_eligible", "settled", "exit_filled", "reconcile_price_mismatch",
        "v4_resting_restored", "audit_artifact_error", "buy_blocked", "tripwire"]
counts = Counter()
samples = {}
flags_bid_ex_self = 0
grace_events = Counter()
with open(LOG, encoding="utf-8", errors="replace") as fh:
    for line in fh:
        try:
            e = json.loads(line)
        except Exception:
            continue
        ev = e.get("event", "")
        for k in KEYS:
            if ev == k or (k in ("grace", "latch", "buy_blocked", "tripwire", "settled") and k in ev):
                counts[k if ev != k else ev] += 1
                if ev not in samples:
                    samples[ev] = line.strip()[:420]
                if k in ("grace", "latch"):
                    grace_events[ev] += 1
        if ev == "aim_shadow" and e.get("details", {}).get("bid_ex_self") is not None:
            flags_bid_ex_self += 1
out = {"counts": dict(counts), "bid_ex_self_lines": flags_bid_ex_self,
       "grace_latch_breakdown": dict(grace_events)}
print(json.dumps(out, indent=1))
print("\n=== SAMPLES (one per event) ===")
for ev in sorted(samples):
    print(ev, "->", samples[ev])
