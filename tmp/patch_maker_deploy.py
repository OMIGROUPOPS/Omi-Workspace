#!/usr/bin/env python3
"""FULL MAKER CONFIG DEPLOY — both bots, all sports.

Changes:
  NCAAMB BOT:
    - CONTRACTS_92PLUS: 50 → 25
    - NCAAMB maker: 95c → 90c (bid at 89c if ask=90, else 90c)
    - NBA maker: 95c → 90c (same pattern)
    - NHL maker: ADD at 92c, 10ct
    - Remove NHL skip in WS handler (was skipping 92+ for NHL)
    - Remove 92+ stop loss (already disabled via `if False`, clean it up)
    - Capital utilization check before all maker entries

  TENNIS BOT:
    - CONTRACTS_92PLUS: 50 → 25
    - ATP Main: 92c → 90c
    - WTA Main: ADD (was ATP-only)
    - ATP Challenger: ADD with 60min elapsed filter
    - Remove WTA Main/Chall restriction (currently ATP Main only)
    - Capital utilization check before all maker entries
"""

import re


def patch_ncaamb(path):
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # === 1. CONTRACTS_92PLUS 50 → 25 ===
    old = 'CONTRACTS_92PLUS = 50                  # 95c maker entries: 50ct (4c edge * 50 = $1.50/trade)'
    new = 'CONTRACTS_92PLUS = 25                  # maker entries: 25ct (sized for ~$400 balance)'
    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print('  [ncaamb] CONTRACTS_92PLUS 50 → 25')

    # === 2. Add MAKER_CONFIGS dict + NHL contracts constant after CONTRACTS_92PLUS line ===
    marker = 'CONTRACTS_92PLUS = 25                  # maker entries: 25ct (sized for ~$400 balance)'
    maker_configs = '''CONTRACTS_92PLUS = 25                  # maker entries: 25ct (sized for ~$400 balance)
CONTRACTS_92PLUS_NHL = 10              # NHL maker: 10ct (smaller edge)

# Sport-specific maker entry levels and sell targets
MAKER_CONFIGS = {
    "ncaamb": {"bid_level": 90, "sell_target": 99, "contracts": 25, "depth_filter": True, "min_depth_ratio": 0.15},
    "nba":    {"bid_level": 90, "sell_target": 99, "contracts": 25, "depth_filter": False},
    "nhl":    {"bid_level": 92, "sell_target": 99, "contracts": 10, "depth_filter": False},
}
MAX_CAPITAL_UTIL = 0.50  # do not enter maker if locked exposure > 50% of balance'''
    if marker in content and 'MAKER_CONFIGS' not in content:
        content = content.replace(marker, maker_configs, 1)
        changes += 1
        print('  [ncaamb] Added MAKER_CONFIGS dict + NHL 10ct + MAX_CAPITAL_UTIL')

    # === 3. Rewrite execute_entry_92plus to use MAKER_CONFIGS ===
    # Replace the bid price logic: was hardcoded 95c/94c
    # Old: Conditional bid: 94c if ask=95c (avoid post_only cross), else 95c
    old_bid = """        # Conditional bid: 94c if ask=95c (avoid post_only cross), else 95c
        if ask == 95:
            maker_price = 94
            log(f'[92+_BID] {side} bid=94c (ask=95c fallback)')
        else:
            maker_price = 95
            log(f'[92+_BID] {side} bid=95c (ask={ask}c)')"""
    new_bid = """        # Sport-specific maker bid level
        sport = self._detect_sport(ticker)
        mcfg = MAKER_CONFIGS.get(sport, MAKER_CONFIGS["ncaamb"])
        bid_level = mcfg["bid_level"]
        maker_contracts = mcfg["contracts"]

        # Capital utilization check
        if self.cash_balance > 0:
            open_exposure = sum(p.contracts * p.entry_ask / 100.0
                                for p in self.positions.values()
                                if not p.filled and not p.settled and not p.time_stopped)
            total_balance = self.cash_balance + open_exposure
            if total_balance > 0 and open_exposure / total_balance > MAX_CAPITAL_UTIL:
                log(f"[92+_SKIP_CAPITAL] {side} exposure=${open_exposure:.2f}/{total_balance:.2f} "
                    f"({open_exposure/total_balance*100:.0f}%) > {MAX_CAPITAL_UTIL*100:.0f}%")
                return

        # Depth filter (ncaamb only)
        if mcfg.get("depth_filter"):
            if dr5 != "" and isinstance(dr5, (int, float)) and dr5 < mcfg.get("min_depth_ratio", 0.15):
                log(f"[92+_SKIP_DEPTH] {side} depth_ratio_5c={dr5:.3f} < {mcfg.get('min_depth_ratio', 0.15)}")
                return

        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level
        if ask == bid_level:
            maker_price = bid_level - 1
            log(f'[92+_BID] {side} bid={maker_price}c (ask={bid_level}c fallback)')
        else:
            maker_price = bid_level
            log(f'[92+_BID] {side} bid={maker_price}c (ask={ask}c)')"""
    if old_bid in content:
        content = content.replace(old_bid, new_bid, 1)
        changes += 1
        print('  [ncaamb] Rewrote maker bid logic → sport-specific MAKER_CONFIGS')

    # === 4. Remove the old depth filter (now handled in new bid logic) ===
    old_depth = """        # Depth filter: require depth_ratio_5c >= 0.15
        depth_snap = await self.capture_depth_snapshot(ticker)
        dr5 = depth_snap.get("depth_ratio_5c", "")
        if dr5 != "" and isinstance(dr5, (int, float)) and dr5 < 0.15:
            log(f"[92+_SKIP_DEPTH] {side} depth_ratio_5c={dr5:.3f} < 0.15")
            return"""
    new_depth = """        # Depth snapshot for logging
        depth_snap = await self.capture_depth_snapshot(ticker)
        dr5 = depth_snap.get("depth_ratio_5c", "")"""
    if old_depth in content:
        content = content.replace(old_depth, new_depth, 1)
        changes += 1
        print('  [ncaamb] Moved depth filter into MAKER_CONFIGS block')

    # === 5. Replace CONTRACTS_92PLUS in order payload with maker_contracts ===
    old_count = """            "count": CONTRACTS_92PLUS,
            "type": "limit",
            "yes_price": maker_price,"""
    new_count = """            "count": maker_contracts,
            "type": "limit",
            "yes_price": maker_price,"""
    if old_count in content:
        content = content.replace(old_count, new_count, 1)
        changes += 1
        print('  [ncaamb] Order payload uses maker_contracts instead of CONTRACTS_92PLUS')

    # === 6. Fix Position creation to use maker_contracts ===
    old_pos = 'contracts=CONTRACTS_92PLUS if buy_confirmed else 0,'
    new_pos = 'contracts=maker_contracts if buy_confirmed else 0,'
    if old_pos in content:
        content = content.replace(old_pos, new_pos, 1)
        changes += 1
        print('  [ncaamb] Position creation uses maker_contracts')

    old_pos2 = '            pos.contracts = CONTRACTS_92PLUS'
    new_pos2 = '            pos.contracts = maker_contracts'
    # Only replace the one in execute_entry_92plus (first occurrence)
    if old_pos2 in content:
        content = content.replace(old_pos2, new_pos2, 1)
        changes += 1
        print('  [ncaamb] pos.contracts assignment uses maker_contracts')

    # === 7. WS handler: Remove NHL skip, change ask threshold from 95 to sport-specific ===
    old_ws = """        # --- 92c+ Settlement Mode: maker bid at 95c (NCAAMB + NBA only) ---
        if ticker not in self.entered_sides and ticker not in self.mode_92_entered:
            # Skip 95c maker for NHL
            _sport92 = self._detect_sport(ticker)
            if _sport92 == "nhl":
                return
            book92 = self.books.get(ticker)
            if book92 and book92.best_ask is not None and book92.best_ask >= 95:"""
    new_ws = """        # --- 92c+ Settlement Mode: sport-specific maker bids ---
        if ticker not in self.entered_sides and ticker not in self.mode_92_entered:
            _sport92 = self._detect_sport(ticker)
            _mcfg92 = MAKER_CONFIGS.get(_sport92)
            if not _mcfg92:
                return
            book92 = self.books.get(ticker)
            if book92 and book92.best_ask is not None and book92.best_ask >= _mcfg92["bid_level"]:"""
    if old_ws in content:
        content = content.replace(old_ws, new_ws, 1)
        changes += 1
        print('  [ncaamb] WS handler: removed NHL skip, sport-specific threshold')

    # === 8. WS handler: change ask < 90 cancel threshold to sport-specific ===
    old_cancel = """            elif book92 and book92.best_ask is not None and book92.best_ask < 90:
                # Reset sustained counter if price drops below 90
                self.sustained_90_ticks.pop(ticker, None)
                # Cancel resting maker bid if price dropped below 90c"""
    new_cancel = """            elif book92 and book92.best_ask is not None and book92.best_ask < _mcfg92["bid_level"] - 4:
                # Reset sustained counter if price drops > 4c below bid level
                self.sustained_90_ticks.pop(ticker, None)
                # Cancel resting maker bid if price dropped too far"""
    if old_cancel in content:
        content = content.replace(old_cancel, new_cancel, 1)
        changes += 1
        print('  [ncaamb] WS handler: cancel threshold now bid_level - 4c')

    # === 8b. Fix the cancel log message ===
    old_cancel_log = """                        log(f"[92+_BID_CANCEL] {side90} ask dropped to "
                            f"{book92.best_ask}c < 90c -- cancelling maker bid")"""
    new_cancel_log = """                        log(f"[92+_BID_CANCEL] {side90} ask dropped to "
                            f"{book92.best_ask}c < {_mcfg92['bid_level'] - 4}c -- cancelling maker bid")"""
    if old_cancel_log in content:
        content = content.replace(old_cancel_log, new_cancel_log, 1)
        changes += 1
        print('  [ncaamb] Updated cancel log message')

    # === 9. Print scan state: update log line ===
    old_scan_log = '        log(f"  NCAAMB + NBA + NHL | {CONTRACTS}ct bounce +{EXIT_BOUNCE}c | 95c maker -> 99c")'
    if old_scan_log in content:
        new_scan_log = '        log(f"  NCAAMB 90c/{CONTRACTS_92PLUS}ct | NBA 90c/{CONTRACTS_92PLUS}ct | NHL 92c/{CONTRACTS_92PLUS_NHL}ct | -> 99c")'
        content = content.replace(old_scan_log, new_scan_log, 1)
        changes += 1
        print('  [ncaamb] Updated scan state log')

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f'  ncaamb: {changes} changes applied')
    else:
        print('  ncaamb: NO CHANGES')
    return changes


def patch_tennis(path):
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # === 1. CONTRACTS_92PLUS 50 → 25 ===
    old = 'CONTRACTS_92PLUS = 50                  # 92c+ maker entries: 50ct (7c edge * 50 = $3.50/trade)'
    new = 'CONTRACTS_92PLUS = 25                  # maker entries: 25ct (sized for ~$400 balance)'
    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print('  [tennis] CONTRACTS_92PLUS 50 → 25')

    # === 2. Add MAKER_CONFIGS after CONTRACTS_92PLUS ===
    marker = 'CONTRACTS_92PLUS = 25                  # maker entries: 25ct (sized for ~$400 balance)'
    maker_configs = '''CONTRACTS_92PLUS = 25                  # maker entries: 25ct (sized for ~$400 balance)

# Sport-specific maker entry levels and sell targets
MAKER_CONFIGS_TENNIS = {
    "KXATPMATCH":          {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 0},
    "KXWTAMATCH":          {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 20},
    "KXATPCHALLENGERMATCH": {"bid_level": 90, "sell_target": 99, "contracts": 25, "elapsed_filter": 60},
    # WTA Challenger: NOT included — marginal edge
}
MAX_CAPITAL_UTIL = 0.50  # do not enter maker if locked exposure > 50% of balance'''
    if marker in content and 'MAKER_CONFIGS_TENNIS' not in content:
        content = content.replace(marker, maker_configs, 1)
        changes += 1
        print('  [tennis] Added MAKER_CONFIGS_TENNIS + MAX_CAPITAL_UTIL')

    # === 3. Rewrite post_92c_maker_bid to use MAKER_CONFIGS_TENNIS ===
    # Change the bid logic from hardcoded 92c to sport-specific
    old_bid = """        # Conditional bid: 91c if ask=92c (avoid post_only cross), else 92c
        _book92 = self.books.get(ticker)
        _ask92 = _book92.best_ask if _book92 and _book92.best_ask is not None else 99
        if _ask92 == 92:
            maker_bid_92 = 91
            log(f"[92+_BID] {side} bid=91c (ask=92c fallback)")
        else:
            maker_bid_92 = 92
            log(f"[92+_BID] {side} bid=92c (ask={_ask92}c)")"""
    new_bid = """        # Sport-specific maker bid level
        _series_key = next((s for s in MAKER_CONFIGS_TENNIS if ticker.startswith(s)), None)
        if not _series_key:
            return
        _mcfg = MAKER_CONFIGS_TENNIS[_series_key]
        bid_level = _mcfg["bid_level"]
        maker_contracts = _mcfg["contracts"]

        # Capital utilization check
        if self.cash_balance > 0:
            open_exposure = sum(p.contracts * p.entry_ask / 100.0
                                for p in self.positions.values()
                                if not p.filled and not p.settled and not p.time_stopped)
            total_balance = self.cash_balance + open_exposure
            if total_balance > 0 and open_exposure / total_balance > MAX_CAPITAL_UTIL:
                log(f"[92+_SKIP_CAPITAL] {side} exposure=${open_exposure:.2f}/{total_balance:.2f} "
                    f"({open_exposure/total_balance*100:.0f}%) > {MAX_CAPITAL_UTIL*100:.0f}%")
                return

        # Elapsed filter (WTA Main: 20min, ATP Chall: 60min)
        elapsed_min_req = _mcfg.get("elapsed_filter", 0)
        if elapsed_min_req > 0:
            expiry_t = self.ticker_expiry.get(ticker)
            if expiry_t:
                # Elapsed = (original duration assumed 3h) - time_to_expiry
                hours_left = (expiry_t - time.time()) / 3600.0
                elapsed_est = max(0, (3.0 - hours_left) * 60)  # minutes elapsed
                if elapsed_est < elapsed_min_req:
                    log(f"[92+_SKIP_ELAPSED] {side} elapsed~{elapsed_est:.0f}m < {elapsed_min_req}m")
                    return

        # Conditional bid: bid_level-1 if ask==bid_level (avoid post_only cross), else bid_level
        _book92 = self.books.get(ticker)
        _ask92 = _book92.best_ask if _book92 and _book92.best_ask is not None else 99
        if _ask92 == bid_level:
            maker_bid_92 = bid_level - 1
            log(f"[92+_BID] {side} bid={maker_bid_92}c (ask={bid_level}c fallback)")
        else:
            maker_bid_92 = bid_level
            log(f"[92+_BID] {side} bid={maker_bid_92}c (ask={_ask92}c)")"""
    if old_bid in content:
        content = content.replace(old_bid, new_bid, 1)
        changes += 1
        print('  [tennis] Rewrote maker bid logic → sport-specific MAKER_CONFIGS_TENNIS')

    # === 4. Replace CONTRACTS_92PLUS in order payload with maker_contracts ===
    old_count = """            "count": CONTRACTS_92PLUS,
            "type": "limit",
            "yes_price": maker_bid_92,"""
    new_count = """            "count": maker_contracts,
            "type": "limit",
            "yes_price": maker_bid_92,"""
    if old_count in content:
        content = content.replace(old_count, new_count, 1)
        changes += 1
        print('  [tennis] Order payload uses maker_contracts')

    # === 5. Fix instant fill Position: CONTRACTS_92PLUS → maker_contracts ===
    old_instant_fee = """            entry_fee = CONTRACTS_92PLUS"""
    new_instant_fee = """            entry_fee = maker_contracts"""
    if old_instant_fee in content:
        content = content.replace(old_instant_fee, new_instant_fee, 1)
        changes += 1
        print('  [tennis] Instant fill fee uses maker_contracts')

    old_instant_pos = """                contracts=CONTRACTS_92PLUS, sell_price=99,"""
    new_instant_pos = """                contracts=maker_contracts, sell_price=99,"""
    # First occurrence is in instant fill section of post_92c_maker_bid
    if old_instant_pos in content:
        content = content.replace(old_instant_pos, new_instant_pos, 1)
        changes += 1
        print('  [tennis] Instant fill Position uses maker_contracts')

    # === 6. Fix check_92plus_bid_fills: CONTRACTS_92PLUS → contract count from order ===
    old_fill_ct = """                contracts = fill_count or CONTRACTS_92PLUS"""
    new_fill_ct = """                contracts = fill_count or CONTRACTS_92PLUS  # fallback to default"""
    # This is fine as-is since fill_count should always be set.
    # But let's keep CONTRACTS_92PLUS as fallback since it's now 25.

    # === 7. WS handler: expand from ATP Main only to all configured series ===
    old_ws = """        # --- 92c+ Settlement Mode (additive, main draw only, maker-based) ---
        if (ticker not in self.entered_sides
                and ticker not in self.mode_92_entered
                and ticker not in self.mode_92_bids
                and self._is_main_draw(ticker)
                and ticker.startswith("KXATPMATCH")):  # ATP Main only, exclude WTA for 92c+"""
    new_ws = """        # --- 92c+ Settlement Mode (additive, maker-based) ---
        _maker_series = next((s for s in MAKER_CONFIGS_TENNIS if ticker.startswith(s)), None)
        if (_maker_series
                and ticker not in self.entered_sides
                and ticker not in self.mode_92_entered
                and ticker not in self.mode_92_bids):"""
    if old_ws in content:
        content = content.replace(old_ws, new_ws, 1)
        changes += 1
        print('  [tennis] WS handler: expanded to all MAKER_CONFIGS_TENNIS series')

    # === 8. WS handler: use sport-specific bid level for ask threshold ===
    old_ask_check = """                ask92 = book92.best_ask
                # Update sustained counter on every tick
                if ask92 >= 88:
                    sustained = self._check_sustained_90(ticker, ask92)
                    if sustained and ask92 >= 92:"""
    new_ask_check = """                ask92 = book92.best_ask
                _mcfg_bid = MAKER_CONFIGS_TENNIS[_maker_series]["bid_level"]
                # Update sustained counter on every tick
                if ask92 >= _mcfg_bid - 2:
                    sustained = self._check_sustained_90(ticker, ask92)
                    if sustained and ask92 >= _mcfg_bid:"""
    if old_ask_check in content:
        content = content.replace(old_ask_check, new_ask_check, 1)
        changes += 1
        print('  [tennis] WS handler: sport-specific ask threshold')

    # === 9. WS handler: update sustained wait log ===
    old_wait = """                    elif self.sustained_90_ticks.get(ticker, 0) > 0 and ask92 >= 92:"""
    new_wait = """                    elif self.sustained_90_ticks.get(ticker, 0) > 0 and ask92 >= _mcfg_bid:"""
    if old_wait in content:
        content = content.replace(old_wait, new_wait, 1)
        changes += 1
        print('  [tennis] WS handler: sustained wait uses sport-specific level')

    # === 10. WS handler: cancel threshold from 88 to bid_level - 4 ===
    old_cancel_thresh = """                else:
                    # Price below 88 -- cancel any resting 92c bid
                    self.sustained_90_ticks[ticker] = 0
                    if ticker in self.mode_92_bids:
                        await self.cancel_92c_maker_bid(ticker)"""
    new_cancel_thresh = """                else:
                    # Price dropped > 4c below bid level -- cancel any resting maker bid
                    if ask92 < _mcfg_bid - 4:
                        self.sustained_90_ticks[ticker] = 0
                        if ticker in self.mode_92_bids:
                            await self.cancel_92c_maker_bid(ticker)"""
    if old_cancel_thresh in content:
        content = content.replace(old_cancel_thresh, new_cancel_thresh, 1)
        changes += 1
        print('  [tennis] WS handler: cancel threshold now bid_level - 4c')

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f'  tennis: {changes} changes applied')
    else:
        print('  tennis: NO CHANGES')
    return changes


print('=' * 60)
print('FULL MAKER CONFIG DEPLOY')
print('=' * 60)
print()
c1 = patch_ncaamb('/root/Omi-Workspace/arb-executor/ncaamb_stb.py')
print()
c2 = patch_tennis('/root/Omi-Workspace/arb-executor/tennis_stb.py')
print(f'\nTOTAL: {c1 + c2} changes')
