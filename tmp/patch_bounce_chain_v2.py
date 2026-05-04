#!/usr/bin/env python3
"""Restructure bounce chain: 5 signals → 3 signals.
Remove decel + drop. Keep stable + tight + wall.
Update tier boundaries. Loosen EARLY_GAME filter.
"""

def patch_file(path, label):
    with open(path) as f:
        content = f.read()
    original = content
    changes = 0

    # ============================================================
    # 1. REPLACE compute_bounce_chain: 5 steps → 3 steps
    # ============================================================
    old_chain = '''    def compute_bounce_chain(self, ticker: str) -> tuple:
        """Score pre-entry microstructure: 5-step bounce chain.
        Returns (score 0-5, detail_string).

        Chain steps:
        1. STABLE baseline: bid stddev < 1c in 5-3 min before now
        2. SUDDEN DROP: price fell >= 5c in last 3 min (dislocation)
        3. DECELERATION: rate of drop slowing in last 90s vs prior 90s
        4. SPREAD TIGHTENING: spread now <= spread 2 min ago
        5. BID WALL: bid_size at best_bid > ask_size at best_ask (depth ratio > 1.0)

        A 5/5 chain = maximum conviction entry.
        """
        history = self.bid_history.get(ticker, [])
        book = self.books.get(ticker)
        now = time.time()
        score = 0
        details = []

        # Need at least 3 minutes of history
        if len(history) < 10:
            return 0, "insufficient_data"

        # Step 1: STABLE baseline (5-3 min ago)
        baseline_ticks = [b for t, b in history if now - 300 <= t <= now - 180]
        if len(baseline_ticks) >= 3:
            import statistics as _st
            baseline_std = _st.stdev(baseline_ticks)
            stable = baseline_std < 1.5
        else:
            baseline_std = 0
            stable = False
        if stable:
            score += 1
            details.append("stable=Y")
        else:
            details.append("stable=N")

        # Step 2: SUDDEN DROP (price fell >= 5c in last 3 min)
        recent_ticks = [b for t, b in history if t >= now - 180]
        old_ticks = [b for t, b in history if now - 300 <= t <= now - 180]
        if recent_ticks and old_ticks:
            baseline_level = max(old_ticks)  # highest point before drop
            current_level = recent_ticks[-1]
            drop = baseline_level - current_level
            sudden_drop = drop >= 5
        else:
            drop = 0
            sudden_drop = False
        if sudden_drop:
            score += 1
            details.append("drop=Y")
        else:
            details.append("drop=N")

        # Step 3: DECELERATION (rate of drop slowing)
        # Compare change rate: 90-180s ago vs last 90s
        mid_ticks = [(t, b) for t, b in history if now - 180 <= t <= now - 90]
        late_ticks = [(t, b) for t, b in history if t >= now - 90]
        if len(mid_ticks) >= 2 and len(late_ticks) >= 2:
            mid_change = mid_ticks[-1][1] - mid_ticks[0][1]   # negative if dropping
            late_change = late_ticks[-1][1] - late_ticks[0][1]
            # Deceleration = late_change > mid_change (less negative or positive)
            decel = late_change > mid_change
        else:
            decel = False
        if decel:
            score += 1
            details.append("decel=Y")
        else:
            details.append("decel=N")

        # Step 4: SPREAD TIGHTENING
        # We track bid_history but not spread history directly.
        # Use current spread vs inferred spread from 2 min ago.
        if book and book.best_ask is not None and book.best_bid is not None:
            current_spread = book.best_ask - book.best_bid
            # Estimate old spread from bid history + assumption ask tracks similarly
            old_bids = [b for t, b in history if now - 150 <= t <= now - 90]
            if old_bids:
                old_bid_avg = sum(old_bids) / len(old_bids)
                # If current bid is closer to current ask than old bid was,
                # spread has tightened. Proxy: spread_tight if current_spread <= 3
                spread_tight = current_spread <= 3
            else:
                spread_tight = current_spread <= 2
        else:
            spread_tight = False
            current_spread = 99
        if spread_tight:
            score += 1
            details.append("tight=Y")
        else:
            details.append("tight=N")

        # Step 5: BID WALL (depth ratio > 1.0)
        if book and book.best_bid_size > 0 and book.best_ask_size > 0:
            depth_ratio = book.best_bid_size / book.best_ask_size
            wall = depth_ratio > 1.0
        else:
            depth_ratio = 0
            wall = False
        if wall:
            score += 1
            details.append("wall=Y")
        else:
            details.append("wall=N")

        detail_str = " ".join(details)
        return score, detail_str'''

    new_chain = '''    def compute_bounce_chain(self, ticker: str) -> tuple:
        """Score pre-entry microstructure: 3-signal bounce chain.
        Returns (score 0-3, detail_string).

        Signals (backed by 11,814-bounce BBO discovery):
        1. STABLE baseline: bid stddev < 1.5c in 5-3 min before now (88% of bounces)
        2. SPREAD TIGHT: current spread <= 3c (84% of bounces at bottom)
        3. BID WALL: bid_size > ask_size at best levels (88% of bounces)

        Removed (v2):
        - DROP: redundant — we know it dropped, that's the entry condition
        - DECEL: penalizes 81% of V-bottom bounces (only 19% show deceleration)

        3/3 = A-tier, 2/3 = B-tier, 0-1/3 = C-tier
        """
        history = self.bid_history.get(ticker, [])
        book = self.books.get(ticker)
        now = time.time()
        score = 0
        details = []

        # Need at least 3 minutes of history
        if len(history) < 10:
            return 0, "insufficient_data"

        # Signal 1: STABLE baseline (bid stddev < 1.5c in 5-3 min ago)
        baseline_ticks = [b for t, b in history if now - 300 <= t <= now - 180]
        if len(baseline_ticks) >= 3:
            import statistics as _st
            baseline_std = _st.stdev(baseline_ticks)
            stable = baseline_std < 1.5
        else:
            stable = False
        if stable:
            score += 1
            details.append("stable=Y")
        else:
            details.append("stable=N")

        # Signal 2: SPREAD TIGHT (current spread <= 3c)
        if book and book.best_ask is not None and book.best_bid is not None:
            current_spread = book.best_ask - book.best_bid
            spread_tight = current_spread <= 3
        else:
            spread_tight = False
        if spread_tight:
            score += 1
            details.append("tight=Y")
        else:
            details.append("tight=N")

        # Signal 3: BID WALL (bid_size > ask_size at best levels)
        if book and book.best_bid_size > 0 and book.best_ask_size > 0:
            depth_ratio = book.best_bid_size / book.best_ask_size
            wall = depth_ratio > 1.0
        else:
            wall = False
        if wall:
            score += 1
            details.append("wall=Y")
        else:
            details.append("wall=N")

        detail_str = " ".join(details)
        return score, detail_str'''

    if old_chain in content:
        content = content.replace(old_chain, new_chain)
        changes += 1
        print(f"  [{label}] Replaced compute_bounce_chain: 5 signals → 3 signals")
    else:
        print(f"  [{label}] WARN: Could not find compute_bounce_chain to replace")

    # ============================================================
    # 2. UPDATE score_entry_tier: chain * 5 → chain * 8 (so 3/3 = 24, 2/3 = 16)
    #    Also update tier docstring
    # ============================================================
    old_tier_doc = '''        A-tier (high conviction): chain 4-5, depth > 1.0, safe game clock
        B-tier (standard):        chain 3, depth 0.15-1.0, moderate game clock
        C-tier (marginal):        chain 0-2, depth < 0.15, late game close score'''
    new_tier_doc = '''        A-tier (high conviction): chain 3/3, depth > 1.0, safe game clock
        B-tier (standard):        chain 2/3, depth 0.15-1.0, moderate game clock
        C-tier (marginal):        chain 0-1/3, depth < 0.15, late game close score'''
    if old_tier_doc in content:
        content = content.replace(old_tier_doc, new_tier_doc)
        changes += 1
        print(f"  [{label}] Updated tier docstring")

    # Change chain multiplier: 5 → 8 (so 3*8=24 hits A-tier threshold of 20)
    old_mult = '        # Bounce chain (0-5 mapped to 0-25 points)\n        score += bounce_chain * 5'
    new_mult = '        # Bounce chain (0-3 mapped to 0-24 points)\n        score += bounce_chain * 8'
    if old_mult in content:
        content = content.replace(old_mult, new_mult)
        changes += 1
        print(f"  [{label}] Updated chain multiplier: 5 → 8")

    # ============================================================
    # 3. UPDATE all /5 log references → /3
    # ============================================================
    # BOUNCE_CHAIN log in WS handler
    old_bc_log = 'log(f"[BOUNCE_CHAIN] {_side} steps={_chain_score}/5 ({_chain_detail})")'
    new_bc_log = 'log(f"[BOUNCE_CHAIN] {_side} steps={_chain_score}/3 ({_chain_detail})")'
    c = content.count(old_bc_log)
    if c > 0:
        content = content.replace(old_bc_log, new_bc_log)
        changes += 1
        print(f"  [{label}] Updated BOUNCE_CHAIN log /5 → /3 ({c} occurrences)")

    # TIER log
    old_tier_log = 'log(f"[TIER] {pos.side} score={bounce_chain}/5 tier={pos.entry_tier} "'
    new_tier_log = 'log(f"[TIER] {pos.side} score={bounce_chain}/3 tier={pos.entry_tier} "'
    c = content.count(old_tier_log)
    if c > 0:
        content = content.replace(old_tier_log, new_tier_log)
        changes += 1
        print(f"  [{label}] Updated TIER log /5 → /3 ({c} occurrences)")

    # C-tier pre-check logs
    old_pre = '_pre_sc = _chain_score * 5'
    new_pre = '_pre_sc = _chain_score * 8'
    c = content.count(old_pre)
    if c > 0:
        content = content.replace(old_pre, new_pre)
        changes += 1
        print(f"  [{label}] Updated pre-score multiplier ({c} occurrences)")

    # REJECT_CTIER_SPIKE logs
    old_ctier = 'chain={_chain_score}/5'
    new_ctier = 'chain={_chain_score}/3'
    c = content.count(old_ctier)
    if c > 0:
        content = content.replace(old_ctier, new_ctier)
        changes += 1
        print(f"  [{label}] Updated chain log references ({c} occurrences)")

    # Reentry chain logs
    old_re_log = 'log(f"[REENTRY_CHAIN] {side} steps={_re_chain}/5 ({_re_detail})")'
    new_re_log = 'log(f"[REENTRY_CHAIN] {side} steps={_re_chain}/3 ({_re_detail})")'
    if old_re_log in content:
        content = content.replace(old_re_log, new_re_log)
        changes += 1
        print(f"  [{label}] Updated REENTRY_CHAIN log /5 → /3")

    old_re_pre = '_re_score = _re_chain * 5'
    new_re_pre = '_re_score = _re_chain * 8'
    if old_re_pre in content:
        content = content.replace(old_re_pre, new_re_pre)
        changes += 1
        print(f"  [{label}] Updated reentry pre-score multiplier")

    old_re_ctier = 'chain={_re_chain}/5'
    new_re_ctier = 'chain={_re_chain}/3'
    c = content.count(old_re_ctier)
    if c > 0:
        content = content.replace(old_re_ctier, new_re_ctier)
        changes += 1
        print(f"  [{label}] Updated reentry chain log refs ({c} occurrences)")

    # ============================================================
    # 4. LOOSEN EARLY_GAME FILTER (ncaamb only)
    #    Only reject period 1 if chain_score < 2
    # ============================================================
    if label == 'ncaamb':
        old_early = '''        # Reject period 1 entries UNLESS score differential >= 5
        # First-half dips in tight games are noise, not dislocations
        if period_num == 1:
            diff = abs(away_pts - home_pts)
            if diff < 5:
                side_tag = ticker.split("-")[-1] if "-" in ticker else ticker
                log(f"[REJECT_EARLY_GAME] {side_tag} period=1 diff={diff} "
                    f"score={away_pts}-{home_pts} clock={remaining} "
                    f"— insufficient lead for first half entry")
                return f"first half diff={diff} < 5: {away_pts}-{home_pts}"

        return None  # passed all filters'''

        new_early = '''        # Reject period 1 entries UNLESS score diff >= 5 OR strong bounce chain
        # V2: allow period-1 if chain_score >= 2/3 (strong microstructure overrides)
        # This is checked at the caller level, not here — caller passes chain_score
        # to check_ncaamb_game_state. For backwards compat, reject if chain unknown.
        if period_num == 1:
            diff = abs(away_pts - home_pts)
            if diff < 5:
                side_tag = ticker.split("-")[-1] if "-" in ticker else ticker
                log(f"[REJECT_EARLY_GAME] {side_tag} period=1 diff={diff} "
                    f"score={away_pts}-{home_pts} clock={remaining} "
                    f"— first half, checking chain override")
                return f"early_game_pending:{diff}"  # special marker for chain override

        return None  # passed all filters'''

        if old_early in content:
            content = content.replace(old_early, new_early)
            changes += 1
            print(f"  [{label}] Updated EARLY_GAME to return pending marker for chain override")

        # Now modify the caller to handle the "early_game_pending" marker
        old_reject_handler = '''            reject = self.check_ncaamb_game_state(ticker, game_data) if sport in ("ncaamb", "nba") else None
            if reject:
                self.game_state_rejects += 1
                log(f"[REJECT_GAMESTATE] {et} {side} ask={ask}c "
                    f"combined_mid={combined_mid:.1f}c — {reject}"
                    f"{game_state_log}")
                return'''

        new_reject_handler = '''            reject = self.check_ncaamb_game_state(ticker, game_data) if sport in ("ncaamb", "nba") else None
            if reject:
                # Chain override: allow period-1 entries if bounce chain >= 2/3
                if isinstance(reject, str) and reject.startswith("early_game_pending:"):
                    _eg_diff = reject.split(":")[1]
                    if bounce_chain >= 2:
                        log(f"[EARLY_GAME_OVERRIDE] {et} {side} ask={ask}c "
                            f"diff={_eg_diff} chain={bounce_chain}/3 — allowed by chain")
                    else:
                        self.game_state_rejects += 1
                        log(f"[REJECT_EARLY_GAME] {et} {side} ask={ask}c "
                            f"diff={_eg_diff} chain={bounce_chain}/3 — chain too weak"
                            f"{game_state_log}")
                        return
                else:
                    self.game_state_rejects += 1
                    log(f"[REJECT_GAMESTATE] {et} {side} ask={ask}c "
                        f"combined_mid={combined_mid:.1f}c — {reject}"
                        f"{game_state_log}")
                    return'''

        if old_reject_handler in content:
            content = content.replace(old_reject_handler, new_reject_handler)
            changes += 1
            print(f"  [{label}] Added chain override for EARLY_GAME rejects")
        else:
            print(f"  [{label}] WARN: Could not find reject handler to patch")

    # ============================================================
    # Write
    # ============================================================
    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f"\n  {label}: {changes} changes applied")
    else:
        print(f"\n  {label}: NO CHANGES")
    return changes


if __name__ == "__main__":
    print("=" * 80)
    print("BOUNCE CHAIN V2 — March Madness Deploy")
    print("=" * 80)
    print()
    print("--- ncaamb_stb.py ---")
    c1 = patch_file("/root/Omi-Workspace/arb-executor/ncaamb_stb.py", "ncaamb")
    print()
    print("--- tennis_stb.py ---")
    c2 = patch_file("/root/Omi-Workspace/arb-executor/tennis_stb.py", "tennis")
    print()
    print(f"TOTAL: {c1 + c2} changes")
