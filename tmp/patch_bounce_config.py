#!/usr/bin/env python3
"""Patch ncaamb_stb.py based on bounce analysis:
1. Kill NHL STB — remove KXNHLGAME from SERIES, SPORT_ENTRY_CONFIGS, TRAIL_CONFIGS
2. Score diff <= 9 filter on STB entry (NCAAMB/NBA)
3. Sport-specific exit: fixed +7c sell for basketball (no trail), trail stays for tennis (other file)
"""
import re

PATH = "/root/Omi-Workspace/arb-executor/ncaamb_stb.py"

with open(PATH) as f:
    content = f.read()
original = content
changes = 0

# ============================================================
# 1. Kill NHL STB: remove from SERIES
# ============================================================
old = 'SERIES = ["KXNCAAMBGAME", "KXNBAGAME", "KXNHLGAME"]'
new = 'SERIES = ["KXNCAAMBGAME", "KXNBAGAME"]  # NHL: maker only, no STB'
if old in content:
    content = content.replace(old, new)
    changes += 1
    print("[1] Removed KXNHLGAME from SERIES")

# Remove KXNHLGAME from SPORT_ENTRY_CONFIGS
old_nhl_cfg = '    "KXNHLGAME":    {"gap_min": 8,  "spread_max": 8, "collapse_drop": 10},  # NHL: gap>=8, wide spread, 10c collapse\n'
if old_nhl_cfg in content:
    content = content.replace(old_nhl_cfg, '')
    changes += 1
    print("[1] Removed KXNHLGAME from SPORT_ENTRY_CONFIGS")

# Remove "nhl" from TRAIL_CONFIGS
old_trail = '''TRAIL_CONFIGS = {
    "ncaamb": {"trigger": 7, "trail_width": 3},
    "nba":    {"trigger": 7, "trail_width": 3},
    "nhl":    {"trigger": 7, "trail_width": 3},
}'''
new_trail = '''TRAIL_CONFIGS = {
    # Basketball: no trailing stop (fixed +7c exit is optimal per bounce analysis)
    # Trail only active for tennis (separate file)
}'''
if old_trail in content:
    content = content.replace(old_trail, new_trail)
    changes += 1
    print("[1] Emptied TRAIL_CONFIGS (basketball uses fixed +7c, no trail)")

# ============================================================
# 2. Score diff <= 9 filter on STB entry
# ============================================================
# Insert after the game state reject check, before anti-stack
# We add a score diff check using the already-parsed away_pts/home_pts

old_reject_block = '''            reject = self.check_ncaamb_game_state(ticker, game_data) if sport != "nhl" else None
            if reject:
                self.game_state_rejects += 1
                log(f"[REJECT_GAMESTATE] {et} {side} ask={ask}c "
                    f"combined_mid={combined_mid:.1f}c — {reject}"
                    f"{game_state_log}")
                return'''

new_reject_block = '''            reject = self.check_ncaamb_game_state(ticker, game_data) if sport in ("ncaamb", "nba") else None
            if reject:
                self.game_state_rejects += 1
                log(f"[REJECT_GAMESTATE] {et} {side} ask={ask}c "
                    f"combined_mid={combined_mid:.1f}c — {reject}"
                    f"{game_state_log}")
                return

            # Score diff filter: only enter STB when diff <= 9 (WR drops to 75% above 10)
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

if old_reject_block in content:
    content = content.replace(old_reject_block, new_reject_block)
    changes += 1
    print("[2] Added score diff <= 9 filter on STB entry")
else:
    print("[2] WARN: Could not find reject block to patch")

# ============================================================
# 3. Sport-specific exit: fixed +7c for basketball (no trail)
# ============================================================
# Change place_exit_sell: basketball STB posts at entry+7c directly, not 99c safety net
old_sell = '''        sell_price = pos.sell_price
        # STB trades: post at 99c safety net until trail activates and sets real price
        if not pos.trail_active and "92plus" not in (pos.entry_mode or ""):
            sell_price = TRAIL_CEILING  # 99c safety net — trail will ratchet down on activation'''

new_sell = '''        sell_price = pos.sell_price
        # Maker trades: always post at sell_target (99c)
        # Basketball STB: fixed +7c exit (no trail — bounces are fast pops)
        # Tennis STB: would use 99c safety net + trail (handled in tennis_stb.py)
        if "92plus" not in (pos.entry_mode or ""):
            sell_price = pos.entry_ask + EXIT_BOUNCE  # fixed +7c for basketball'''

if old_sell in content:
    content = content.replace(old_sell, new_sell)
    changes += 1
    print("[3] Changed place_exit_sell to fixed +7c for basketball STB")

# Also disable trailing stop logic in WS handler for this bot (basketball only)
# The trail block runs for all STB trades — now it's a no-op since TRAIL_CONFIGS is empty
# But let's be explicit: guard with "if tcfg:" already exists, so empty dict = no trail. Good.

# ============================================================
# Write and validate
# ============================================================
if content != original:
    with open(PATH, 'w') as f:
        f.write(content)
    print(f"\n{changes} changes written to {PATH}")
else:
    print("\nNO CHANGES")
