#!/usr/bin/env python3
"""Strip period 2+ and diff>=10 from NCAAMB and NBA maker entries.
Keep game state LOGGING but remove the reject gates."""


def patch_ncaamb(path):
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # Replace the game state filter block: keep fetch + logging, remove rejects
    old = """        # --- Game state check for 92c+ entries ---
        _gs_log_92 = ""
        _game_data_92 = await self.fetch_game_state(et)
        if _game_data_92:
            _live92 = _game_data_92.get("live_data", {})
            _det92 = _live92.get("details", {})
            _status92 = _det92.get("status", "?")
            _away92 = _det92.get("away_points", "?")
            _home92 = _det92.get("home_points", "?")
            _period92 = _det92.get("period", "?")
            _remaining92 = _det92.get("period_remaining_time", "?")
            _gs_log_92 = (
                f" score={_away92}-{_home92} period={_period92}"
                f" clock={_remaining92} status={_status92}"
            )
            # Reject period 1 (first half) for 92c+ entries
            try:
                _pnum92 = int(_period92) if _period92 and _period92 != "?" else 0
            except (ValueError, TypeError):
                _pnum92 = 0
            if _pnum92 == 1:
                log(f"[92+_REJECT_PERIOD1] {side} first half — skipping 92c+ entry{_gs_log_92}")
                return
            # Reject if score diff < 10
            try:
                _diff92 = abs(int(_away92) - int(_home92))
            except (ValueError, TypeError):
                _diff92 = 999  # unknown score — allow entry
            if _diff92 < 10:
                log(f"[92+_REJECT_CLOSE_GAME] {side} diff={_diff92}pts < 10{_gs_log_92}")
                return"""

    new = """        # --- Game state collection for 92c+ entries (logging only, no filters) ---
        _gs_log_92 = ""
        _game_data_92 = await self.fetch_game_state(et)
        if _game_data_92:
            _live92 = _game_data_92.get("live_data", {})
            _det92 = _live92.get("details", {})
            _status92 = _det92.get("status", "?")
            _away92 = _det92.get("away_points", "?")
            _home92 = _det92.get("home_points", "?")
            _period92 = _det92.get("period", "?")
            _remaining92 = _det92.get("period_remaining_time", "?")
            _gs_log_92 = (
                f" score={_away92}-{_home92} period={_period92}"
                f" clock={_remaining92} status={_status92}"
            )"""

    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print('  [ncaamb] Stripped period 2+ and diff>=10 rejects (kept logging)')

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f'  ncaamb: {changes} changes applied')
    else:
        print('  ncaamb: NO CHANGES — pattern not found')
    return changes


def patch_tennis(path):
    """Tennis maker has no game state filters to strip — verify."""
    with open(path, 'r') as f:
        content = f.read()

    if 'REJECT_PERIOD1' in content or 'REJECT_CLOSE_GAME' in content:
        print('  [tennis] WARNING: found game state reject — needs manual review')
        return 0
    else:
        print('  [tennis] Confirmed: no game state filters on maker entries')
        return 0


print('=' * 60)
print('STRIP GAME STATE FILTERS FROM MAKER')
print('=' * 60)
print()
c1 = patch_ncaamb('/root/Omi-Workspace/arb-executor/ncaamb_stb.py')
print()
c2 = patch_tennis('/root/Omi-Workspace/arb-executor/tennis_stb.py')
print(f'\nTOTAL: {c1 + c2} changes')
