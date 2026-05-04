#!/usr/bin/env python3
"""Deploy three filters backed by trade autopsy data.

FILTER 1: Depth ratio floor on ALL maker entries (both bots)
FILTER 2: Game clock gates for NCAAMB/NBA STB (ncaamb_stb.py only)
FILTER 3: Price stability check + sizing tier logging (both bots)
"""
import re

def patch_ncaamb(path):
    with open(path) as f:
        content = f.read()
    original = content
    changes = 0

    # ============================================================
    # FILTER 1: Depth ratio on ALL maker entries
    # Currently only ncaamb has depth_filter: True. Enable for all.
    # ============================================================

    # Change nba config to include depth_filter
    old_nba = '"nba":    {"bid_level": 90, "sell_target": 99, "contracts": 25, "depth_filter": False},'
    new_nba = '"nba":    {"bid_level": 90, "sell_target": 99, "contracts": 25, "depth_filter": True, "min_depth_ratio": 0.15},'
    if old_nba in content:
        content = content.replace(old_nba, new_nba)
        changes += 1
        print("[F1] Enabled depth_filter on NBA maker")

    # Change nhl config to include depth_filter
    old_nhl = '"nhl":    {"bid_level": 92, "sell_target": 99, "contracts": 10, "depth_filter": False},'
    new_nhl = '"nhl":    {"bid_level": 92, "sell_target": 99, "contracts": 10, "depth_filter": True, "min_depth_ratio": 0.15},'
    if old_nhl in content:
        content = content.replace(old_nhl, new_nhl)
        changes += 1
        print("[F1] Enabled depth_filter on NHL maker")

    # The depth filter check in execute_entry_92plus currently guards with:
    #   if mcfg.get("depth_filter"):
    # This will now apply to all sports since we set depth_filter: True on all.
    # No code change needed — the guard already works correctly.

    # ============================================================
    # FILTER 2: Game clock gates (NCAAMB period 2 close game, NBA Q4)
    # Add after the score diff filter in _execute_entry_inner
    # ============================================================

    # Find the score diff filter block and add clock gates after it
    old_diff_block = '''            # Score diff filter: only enter STB when diff <= 9 (WR drops to 75% above 10)
            try:
                _away = int(away_pts) if str(away_pts).isdigit() else 0
                _home = int(home_pts) if str(home_pts).isdigit() else 0
                _diff = abs(_away - _home)
                if _diff >= 10:
                    log(f"[REJECT_DIFF] {et} {side} ask={ask}c diff={_diff} "
                        f"({away_pts}-{home_pts}) — score diff >= 10")
                    return
            except (ValueError, TypeError):
                pass  # proceed if score unavailable'''

    new_diff_block = '''            # Score diff filter: only enter STB when diff <= 9 (WR drops to 75% above 10)
            try:
                _away = int(away_pts) if str(away_pts).isdigit() else 0
                _home = int(home_pts) if str(home_pts).isdigit() else 0
                _diff = abs(_away - _home)
                if _diff >= 10:
                    log(f"[REJECT_DIFF] {et} {side} ask={ask}c diff={_diff} "
                        f"({away_pts}-{home_pts}) — score diff >= 10")
                    return
            except (ValueError, TypeError):
                _away, _home, _diff = 0, 0, 0

            # FILTER 2: Game clock gates (autopsy-backed)
            try:
                _period_str = str(period) if period != "?" else ""
                _period_num = int(_period_str) if _period_str.isdigit() else 0
                _clock_str = str(remaining) if remaining and remaining != "?" else ""
                _clock_secs = 9999
                if _clock_str:
                    _cp = _clock_str.split(":")
                    if len(_cp) == 2:
                        _clock_secs = int(_cp[0]) * 60 + int(_cp[1])
                    elif len(_cp) == 3:
                        _clock_secs = int(_cp[1]) * 60 + int(_cp[2])

                # NCAAMB: skip entry if period 2, score diff <= 6, clock < 5 min
                if sport == "ncaamb" and _period_num >= 2 and _diff <= 6 and _clock_secs < 300:
                    log(f"[REJECT_LATE_CLOSE] {et} {side} ask={ask}c diff={_diff} "
                        f"clock={_clock_secs}s period={_period_num}")
                    return

                # NBA: skip entry if quarter 4, score diff <= 8
                if sport == "nba" and _period_num >= 4 and _diff <= 8:
                    log(f"[REJECT_Q4_CLOSE] {et} {side} ask={ask}c diff={_diff} "
                        f"period={_period_num}")
                    return
            except (ValueError, TypeError):
                pass  # proceed if parse fails'''

    if old_diff_block in content:
        content = content.replace(old_diff_block, new_diff_block)
        changes += 1
        print("[F2] Added game clock gates (NCAAMB late close + NBA Q4)")
    else:
        print("[F2] WARN: Could not find score diff block to patch")

    # ============================================================
    # FILTER 3: Price stability check + sizing tier logging
    # Need: bid_stability dict in __init__, tracking in recalc_bbo/apply_delta,
    # check in both entry paths
    # ============================================================

    # 3a: Add bid_stability_history to __init__
    old_init = "        # Collapse filter state\n        self.bid_history: Dict[str, List] = {}"
    new_init = """        # Price stability tracking (rolling 2-min bid stddev per ticker)
        self.bid_stability_history: Dict[str, list] = {}  # ticker -> [(ts, bid), ...]

        # Collapse filter state
        self.bid_history: Dict[str, List] = {}"""
    if old_init in content:
        content = content.replace(old_init, new_init)
        changes += 1
        print("[F3] Added bid_stability_history to __init__")

    # 3b: Add stability tracking in apply_delta (after recalc_bbo call)
    old_delta_end = '''        recalc_bbo(book)
        book.last_update = time.time()

    # ------------------------------------------------------------------
    # Discovery'''
    new_delta_end = '''        recalc_bbo(book)
        book.last_update = time.time()

        # Track bid for stability analysis (rolling 2-min window)
        if book.best_bid is not None:
            now = time.time()
            hist = self.bid_stability_history.setdefault(ticker, [])
            hist.append((now, book.best_bid))
            # Trim to 2 minutes
            cutoff = now - 120
            while hist and hist[0][0] < cutoff:
                hist.pop(0)

    # ------------------------------------------------------------------
    # Discovery'''
    if old_delta_end in content:
        content = content.replace(old_delta_end, new_delta_end)
        changes += 1
        print("[F3] Added stability tracking in apply_delta")

    # 3c: Add _check_bid_stability helper method after check_collapse
    # Find end of check_collapse
    old_collapse_end = '''        return None  # no collapse detected

    # ------------------------------------------------------------------
    # 92c+ Settlement Mode'''
    new_collapse_end = '''        return None  # no collapse detected

    def _check_bid_stability(self, ticker: str) -> tuple:
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
    # 92c+ Settlement Mode'''
    if old_collapse_end in content:
        content = content.replace(old_collapse_end, new_collapse_end)
        changes += 1
        print("[F3] Added _check_bid_stability and _log_sizing_tier helpers")
    else:
        print("[F3] WARN: Could not find check_collapse end marker")

    # 3d: Add stability check in _execute_entry_inner (STB path)
    # Insert after score diff / clock gate filters, before anti-stack
    old_antistack = '''        # Anti-stack safety: check portfolio for existing position
        pos_check_path = f"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1"
        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)
        if pos_check:
            existing_pos = [p for p in pos_check.get("market_positions", []) if _read_position(p) > 0]'''

    new_antistack = '''        # FILTER 3: Price stability check (stddev of bid over 2-min window)
        _stab_stddev, _stab_n = self._check_bid_stability(ticker)
        if _stab_stddev is not None and _stab_stddev > 3.0:
            log(f"[REJECT_UNSTABLE] {et} {side} ask={ask}c stddev={_stab_stddev:.1f}c "
                f"(n={_stab_n} points over 2min)")
            return

        # Sizing tier logging (data collection — no action yet)
        _depth_snap_tier = await self.capture_depth_snapshot(ticker)
        _dr5_tier = _depth_snap_tier.get("depth_ratio_5c", 0) if _depth_snap_tier else 0
        if isinstance(_dr5_tier, (int, float)) and _stab_stddev is not None:
            self._log_sizing_tier(side, _dr5_tier, _stab_stddev)

        # Anti-stack safety: check portfolio for existing position
        pos_check_path = f"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1"
        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)
        if pos_check:
            existing_pos = [p for p in pos_check.get("market_positions", []) if _read_position(p) > 0]'''

    if old_antistack in content:
        content = content.replace(old_antistack, new_antistack, 1)  # only first occurrence (STB entry)
        changes += 1
        print("[F3] Added stability check + tier logging in STB entry path")
    else:
        print("[F3] WARN: Could not find anti-stack block in STB entry")

    # 3e: Add stability check in execute_entry_92plus (MAKER path)
    # Insert before the conditional bid section
    old_maker_bid = '''        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level
        if ask == bid_level:
            maker_price = bid_level - 1
            log(f\'[92+_BID] {side} bid={maker_price}c (ask={bid_level}c fallback)\')
        else:
            maker_price = bid_level
            log(f\'[92+_BID] {side} bid={maker_price}c (ask={ask}c)\')'''

    new_maker_bid = '''        # FILTER 3: Price stability check on maker entries
        _stab_stddev_92, _stab_n_92 = self._check_bid_stability(ticker)
        if _stab_stddev_92 is not None and _stab_stddev_92 > 3.0:
            log(f"[92+_SKIP_UNSTABLE] {side} stddev={_stab_stddev_92:.1f}c "
                f"(n={_stab_n_92} points over 2min)")
            return

        # Sizing tier logging for maker entries
        if isinstance(dr5, (int, float)) and _stab_stddev_92 is not None:
            self._log_sizing_tier(side, dr5, _stab_stddev_92)

        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level
        if ask == bid_level:
            maker_price = bid_level - 1
            log(f\'[92+_BID] {side} bid={maker_price}c (ask={bid_level}c fallback)\')
        else:
            maker_price = bid_level
            log(f\'[92+_BID] {side} bid={maker_price}c (ask={ask}c)\')'''

    if old_maker_bid in content:
        content = content.replace(old_maker_bid, new_maker_bid)
        changes += 1
        print("[F3] Added stability check + tier logging in MAKER entry path")
    else:
        print("[F3] WARN: Could not find maker bid block")

    # Write
    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f"\nncaamb_stb.py: {changes} changes applied")
    else:
        print("\nncaamb_stb.py: NO CHANGES")
    return changes


def patch_tennis(path):
    with open(path) as f:
        content = f.read()
    original = content
    changes = 0

    # ============================================================
    # FILTER 1: Depth ratio on ALL tennis maker entries
    # Add depth_filter to all MAKER_CONFIGS_TENNIS entries
    # ============================================================

    old_atp = '"KXATPMATCH":          {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 0},'
    new_atp = '"KXATPMATCH":          {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 0, "depth_filter": True, "min_depth_ratio": 0.15},'
    if old_atp in content:
        content = content.replace(old_atp, new_atp)
        changes += 1
        print("[F1] Enabled depth_filter on ATP Main maker")

    old_wta = '"KXWTAMATCH":          {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 20},'
    new_wta = '"KXWTAMATCH":          {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 20, "depth_filter": True, "min_depth_ratio": 0.15},'
    if old_wta in content:
        content = content.replace(old_wta, new_wta)
        changes += 1
        print("[F1] Enabled depth_filter on WTA Main maker")

    old_chall = '"KXATPCHALLENGERMATCH": {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 60},'
    new_chall = '"KXATPCHALLENGERMATCH": {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 60, "depth_filter": True, "min_depth_ratio": 0.15},'
    if old_chall in content:
        content = content.replace(old_chall, new_chall)
        changes += 1
        print("[F1] Enabled depth_filter on ATP Challenger maker")

    # Now add the depth filter check in execute_entry_92plus
    # Tennis doesn't have it yet — need to add it before the conditional bid
    # First, find if there's already a depth snapshot capture in tennis 92plus
    if '92+_SKIP_DEPTH' not in content:
        # Need to add depth check. Find the elapsed filter block end and add after it
        old_elapsed_end = '''                    log(f"[92+_SKIP_ELAPSED] {side} elapsed~{elapsed_est:.0f}m < {elapsed_min_req}m")
                    return

        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level'''
        new_elapsed_end = '''                    log(f"[92+_SKIP_ELAPSED] {side} elapsed~{elapsed_est:.0f}m < {elapsed_min_req}m")
                    return

        # FILTER 1: Depth ratio check for maker entries
        if _mcfg.get("depth_filter"):
            _depth_snap_92t = await self.capture_depth_snapshot(ticker)
            _dr5_92t = _depth_snap_92t.get("depth_ratio_5c", "") if _depth_snap_92t else ""
            if _dr5_92t != "" and isinstance(_dr5_92t, (int, float)) and _dr5_92t < _mcfg.get("min_depth_ratio", 0.15):
                log(f"[92+_SKIP_DEPTH] {side} depth_ratio_5c={_dr5_92t:.3f} < {_mcfg.get('min_depth_ratio', 0.15)}")
                return

        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level'''
        if old_elapsed_end in content:
            content = content.replace(old_elapsed_end, new_elapsed_end)
            changes += 1
            print("[F1] Added depth ratio check in tennis maker entry path")
        else:
            print("[F1] WARN: Could not find elapsed filter end in tennis")

    # ============================================================
    # FILTER 3: Price stability check + sizing tier logging
    # ============================================================

    # 3a: Add bid_stability_history to __init__
    old_init = "        # Collapse filter state\n        self.bid_history: Dict[str, List] = {}"
    new_init = """        # Price stability tracking (rolling 2-min bid stddev per ticker)
        self.bid_stability_history: Dict[str, list] = {}  # ticker -> [(ts, bid), ...]

        # Collapse filter state
        self.bid_history: Dict[str, List] = {}"""
    if old_init in content:
        content = content.replace(old_init, new_init)
        changes += 1
        print("[F3] Added bid_stability_history to __init__")

    # 3b: Add stability tracking in apply_delta
    old_delta_end = '''        recalc_bbo(book)
        book.last_update = time.time()

    # ------------------------------------------------------------------
    # Discovery'''
    new_delta_end = '''        recalc_bbo(book)
        book.last_update = time.time()

        # Track bid for stability analysis (rolling 2-min window)
        if book.best_bid is not None:
            now = time.time()
            hist = self.bid_stability_history.setdefault(ticker, [])
            hist.append((now, book.best_bid))
            # Trim to 2 minutes
            cutoff = now - 120
            while hist and hist[0][0] < cutoff:
                hist.pop(0)

    # ------------------------------------------------------------------
    # Discovery'''
    if old_delta_end in content:
        content = content.replace(old_delta_end, new_delta_end)
        changes += 1
        print("[F3] Added stability tracking in apply_delta")

    # 3c: Add helper methods after check_collapse (tennis version)
    old_collapse_end = '''        return None  # no collapse detected

    # ------------------------------------------------------------------
    # 92c+ Settlement Mode'''
    new_collapse_end = '''        return None  # no collapse detected

    def _check_bid_stability(self, ticker: str) -> tuple:
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
    # 92c+ Settlement Mode'''
    if old_collapse_end in content:
        content = content.replace(old_collapse_end, new_collapse_end)
        changes += 1
        print("[F3] Added _check_bid_stability and _log_sizing_tier helpers")

    # 3d: Add stability check in _execute_entry_inner (STB path)
    old_antistack_t = '''        # Anti-stack safety: check portfolio for existing position
        pos_check_path = f"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1"
        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)
        if pos_check:
            existing_pos = [p for p in pos_check.get("market_positions", []) if _read_position(p) > 0]'''

    new_antistack_t = '''        # FILTER 3: Price stability check (stddev of bid over 2-min window)
        _stab_stddev, _stab_n = self._check_bid_stability(ticker)
        if _stab_stddev is not None and _stab_stddev > 3.0:
            log(f"[REJECT_UNSTABLE] {et} {side} ask={ask}c stddev={_stab_stddev:.1f}c "
                f"(n={_stab_n} points over 2min)")
            return

        # Sizing tier logging (data collection — no action yet)
        _depth_snap_tier = await self.capture_depth_snapshot(ticker)
        _dr5_tier = _depth_snap_tier.get("depth_ratio_5c", 0) if _depth_snap_tier else 0
        if isinstance(_dr5_tier, (int, float)) and _stab_stddev is not None:
            self._log_sizing_tier(side, _dr5_tier, _stab_stddev)

        # Anti-stack safety: check portfolio for existing position
        pos_check_path = f"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1"
        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)
        if pos_check:
            existing_pos = [p for p in pos_check.get("market_positions", []) if _read_position(p) > 0]'''

    if old_antistack_t in content:
        content = content.replace(old_antistack_t, new_antistack_t, 1)
        changes += 1
        print("[F3] Added stability check + tier logging in STB entry path")

    # 3e: Add stability check in execute_entry_92plus (MAKER path) for tennis
    # Find the conditional bid section (after we just added the depth check)
    old_maker_bid_t = '''        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level
        _book92 = self.books.get(ticker)
        _ask92 = _book92.best_ask if _book92 and _book92.best_ask is not None else 99
        if _ask92 == bid_level:
            maker_bid_92 = bid_level - 1
            log(f"[92+_BID] {side} bid={maker_bid_92}c (ask={bid_level}c fallback)")
        else:
            maker_bid_92 = bid_level
            log(f"[92+_BID] {side} bid={maker_bid_92}c (ask={_ask92}c)")'''

    new_maker_bid_t = '''        # FILTER 3: Price stability check on maker entries
        _stab_stddev_92t, _stab_n_92t = self._check_bid_stability(ticker)
        if _stab_stddev_92t is not None and _stab_stddev_92t > 3.0:
            log(f"[92+_SKIP_UNSTABLE] {side} stddev={_stab_stddev_92t:.1f}c "
                f"(n={_stab_n_92t} points over 2min)")
            return

        # Sizing tier logging for maker entries
        _depth_snap_92t_tier = await self.capture_depth_snapshot(ticker) if '_depth_snap_92t' not in dir() else _depth_snap_92t
        _dr5_92t_tier = _depth_snap_92t_tier.get("depth_ratio_5c", 0) if _depth_snap_92t_tier else 0
        if isinstance(_dr5_92t_tier, (int, float)) and _stab_stddev_92t is not None:
            self._log_sizing_tier(side, _dr5_92t_tier, _stab_stddev_92t)

        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level
        _book92 = self.books.get(ticker)
        _ask92 = _book92.best_ask if _book92 and _book92.best_ask is not None else 99
        if _ask92 == bid_level:
            maker_bid_92 = bid_level - 1
            log(f"[92+_BID] {side} bid={maker_bid_92}c (ask={bid_level}c fallback)")
        else:
            maker_bid_92 = bid_level
            log(f"[92+_BID] {side} bid={maker_bid_92}c (ask={_ask92}c)")'''

    if old_maker_bid_t in content:
        content = content.replace(old_maker_bid_t, new_maker_bid_t)
        changes += 1
        print("[F3] Added stability check + tier logging in tennis MAKER entry path")

    # Write
    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f"\ntennis_stb.py: {changes} changes applied")
    else:
        print("\ntennis_stb.py: NO CHANGES")
    return changes


if __name__ == "__main__":
    print("=" * 80)
    print("DEPLOYING THREE FILTERS")
    print("=" * 80)
    print()
    print("--- ncaamb_stb.py ---")
    c1 = patch_ncaamb("/root/Omi-Workspace/arb-executor/ncaamb_stb.py")
    print()
    print("--- tennis_stb.py ---")
    c2 = patch_tennis("/root/Omi-Workspace/arb-executor/tennis_stb.py")
    print()
    print(f"TOTAL: {c1 + c2} changes across both files")
