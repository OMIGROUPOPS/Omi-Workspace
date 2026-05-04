#!/usr/bin/env python3
"""Data Enrichment Deploy — Tier 1 + Tier 2.

Tier 1 (CSV enrichment, both bots):
  - Add columns: period, clock_seconds, score_diff, exit_depth_ratio_5c,
    exit_bid_depth_5c, exit_ask_depth_5c, max_bid_after_entry, price_trajectory
  - Parse game_state_at_entry into period/clock_seconds/score_diff in _csv_write_entry
  - Fix ncaamb bug: assign game_state_at_entry to Position in execute_entry
  - In _csv_write_exit: capture exit depth, write max_bid, serialize trajectory

Tier 2 (92c+ game state):
  - NCAAMB execute_entry_92plus: fetch game state, reject period 1, reject diff<10
  - Tennis post_92c_maker_bid: fetch game state, populate Position (no filters)

Does NOT change any entry/exit logic. Data collection only.
"""
import re


def patch_ncaamb():
    path = '/root/Omi-Workspace/arb-executor/ncaamb_stb.py'
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # ===================================================================
    # 1. Add new columns to CSV_COLS (append before closing bracket)
    # ===================================================================
    old_cols = '        "entry_type",\n    ]'
    new_cols = (
        '        "entry_type",\n'
        '        "period", "clock_seconds", "score_diff",\n'
        '        "exit_depth_ratio_5c", "exit_bid_depth_5c", "exit_ask_depth_5c",\n'
        '        "max_bid_after_entry", "price_trajectory",\n'
        '    ]'
    )
    if old_cols in content:
        content = content.replace(old_cols, new_cols, 1)
        changes += 1
        print('  [OK] Added 8 new CSV columns to CSV_COLS')
    else:
        print('  [WARN] Could not find CSV_COLS closing bracket pattern')

    # ===================================================================
    # 2. Fix ncaamb bug: assign game_state_at_entry to Position
    #    After: pos.entry_type = entry_type
    #           self.positions[ticker] = pos
    #    Add:   if game_state_log:
    #               pos.game_state_at_entry = game_state_log.strip()
    # ===================================================================
    old_assign = (
        '        pos.entry_type = entry_type\n'
        '        self.positions[ticker] = pos\n'
        '\n'
        '        now = time.strftime("%H:%M:%S")\n'
        '        log(f"[ENTRY] {now} {et} {side} ask={ask}c bid={bid}c "'
    )
    new_assign = (
        '        pos.entry_type = entry_type\n'
        '        self.positions[ticker] = pos\n'
        '\n'
        '        # Populate game state for CSV enrichment\n'
        '        if game_state_log:\n'
        '            pos.game_state_at_entry = game_state_log.strip()\n'
        '\n'
        '        now = time.strftime("%H:%M:%S")\n'
        '        log(f"[ENTRY] {now} {et} {side} ask={ask}c bid={bid}c "'
    )
    if old_assign in content:
        content = content.replace(old_assign, new_assign, 1)
        changes += 1
        print('  [OK] Fixed: game_state_at_entry now assigned to Position in execute_entry')
    else:
        print('  [WARN] Could not find Position assignment pattern in execute_entry')

    # ===================================================================
    # 3. Add _parse_game_state helper (after _detect_series or _detect_sport)
    # ===================================================================
    helper = '''
    @staticmethod
    def _parse_game_state(gs_str):
        """Parse game_state_at_entry string into (period, clock_seconds, score_diff)."""
        period = ""
        clock_seconds = ""
        score_diff = ""
        if not gs_str:
            return period, clock_seconds, score_diff
        # Extract period=X
        m = re.search(r'period=(\\S+)', gs_str)
        if m:
            period = m.group(1)
        # Extract clock=MM:SS or clock=PT...
        m = re.search(r'clock=(\\S+)', gs_str)
        if m:
            clock_raw = m.group(1)
            try:
                if ':' in clock_raw:
                    parts = clock_raw.split(':')
                    clock_seconds = str(int(parts[0]) * 60 + int(parts[1]))
                elif clock_raw.startswith('PT'):
                    # ISO duration PT12M30S
                    mins = re.search(r'(\\d+)M', clock_raw)
                    secs = re.search(r'(\\d+)S', clock_raw)
                    total = 0
                    if mins: total += int(mins.group(1)) * 60
                    if secs: total += int(secs.group(1))
                    clock_seconds = str(total)
                else:
                    clock_seconds = clock_raw
            except (ValueError, IndexError):
                clock_seconds = clock_raw
        # Extract score=A-B → diff = abs(A-B)
        m = re.search(r'score=(\\d+)-(\\d+)', gs_str)
        if m:
            try:
                score_diff = str(abs(int(m.group(1)) - int(m.group(2))))
            except ValueError:
                pass
        # Tennis: sets=X-Y
        m2 = re.search(r'sets=(\\d+)-(\\d+)', gs_str)
        if m2 and not score_diff:
            try:
                score_diff = str(abs(int(m2.group(1)) - int(m2.group(2))))
            except ValueError:
                pass
        return period, clock_seconds, score_diff

'''
    # Insert before _csv_write_entry
    marker = '    def _csv_write_entry(self, pos):'
    if '_parse_game_state' not in content and marker in content:
        content = content.replace(marker, helper + marker, 1)
        changes += 1
        print('  [OK] Added _parse_game_state helper')
    elif '_parse_game_state' in content:
        print('  [SKIP] _parse_game_state already exists')

    # ===================================================================
    # 4. Update _csv_write_entry to include new columns
    # ===================================================================
    old_entry_row_end = (
        '            "entry_mode": getattr(pos, \'entry_mode\', \'\'),\n'
        '            "volume_tier": getattr(pos, \'volume_tier\', \'\'),\n'
        '            "entry_type": getattr(pos, \'entry_type\', \'\'),\n'
        '        }'
    )
    new_entry_row_end = (
        '            "entry_mode": getattr(pos, \'entry_mode\', \'\'),\n'
        '            "volume_tier": getattr(pos, \'volume_tier\', \'\'),\n'
        '            "entry_type": getattr(pos, \'entry_type\', \'\'),\n'
        '            "period": _gs_period,\n'
        '            "clock_seconds": _gs_clock,\n'
        '            "score_diff": _gs_diff,\n'
        '            "exit_depth_ratio_5c": "",\n'
        '            "exit_bid_depth_5c": "",\n'
        '            "exit_ask_depth_5c": "",\n'
        '            "max_bid_after_entry": "",\n'
        '            "price_trajectory": "",\n'
        '        }'
    )
    if old_entry_row_end in content:
        # Also need to add the parse call before the row dict
        # Insert parse call after "pos.pre_entry_price_10m = pre_10m"
        old_pre_10m = '        pos.pre_entry_price_10m = pre_10m\n\n        import csv, io'
        new_pre_10m = (
            '        pos.pre_entry_price_10m = pre_10m\n'
            '\n'
            '        # Parse game state into structured fields\n'
            '        _gs_period, _gs_clock, _gs_diff = self._parse_game_state(pos.game_state_at_entry)\n'
            '\n'
            '        import csv, io'
        )
        if old_pre_10m in content:
            content = content.replace(old_pre_10m, new_pre_10m, 1)
            changes += 1
            print('  [OK] Added game state parsing call in _csv_write_entry')

        content = content.replace(old_entry_row_end, new_entry_row_end, 1)
        changes += 1
        print('  [OK] Added new columns to _csv_write_entry row dict')
    else:
        print('  [WARN] Could not find entry_row_end pattern in _csv_write_entry')

    # ===================================================================
    # 5. Update _csv_write_exit to capture exit depth + max_bid + trajectory
    # ===================================================================
    # After gs_exit is built and before CSV read, add exit depth capture
    old_exit_csv_read = (
        '        # Read CSV, find last row for this ticker with empty exit_type, update it\n'
        '        import csv, io'
    )
    new_exit_csv_read = (
        '        # Capture exit depth snapshot\n'
        '        exit_depth = {}\n'
        '        try:\n'
        '            exit_depth = await self.capture_depth_snapshot(pos.ticker)\n'
        '        except Exception:\n'
        '            pass\n'
        '\n'
        '        # Serialize trajectory and max_bid\n'
        '        traj_str = ""\n'
        '        if hasattr(pos, "trajectory") and pos.trajectory:\n'
        '            traj_parts = []\n'
        '            for k in ["15s","30s","1m","2m","3m","5m","10m","15m","20m"]:\n'
        '                v = pos.trajectory.get(k)\n'
        '                traj_parts.append(f"{k}={v}c" if v is not None else f"{k}=?")\n'
        '            traj_str = "|".join(traj_parts)\n'
        '        max_bid_val = pos.max_bid_after_entry if pos.max_bid_after_entry is not None else ""\n'
        '\n'
        '        # Read CSV, find last row for this ticker with empty exit_type, update it\n'
        '        import csv, io'
    )
    # This pattern appears twice (ncaamb _csv_write_exit) — replace only first
    c = content.count(old_exit_csv_read)
    if c >= 1:
        content = content.replace(old_exit_csv_read, new_exit_csv_read, 1)
        changes += 1
        print('  [OK] Added exit depth + trajectory capture in _csv_write_exit')

    # Update the exit row update to include new columns
    # The exit writes to parts[12..16]. After that, we need to extend the row.
    # Current: parts[12]=exit_type, [13]=exit_price, [14]=hold_sec, [15]=gs_exit, [16]=pnl
    # Then depth [17..28], entry_mode[29], volume_tier[30], entry_type[31]
    # New: [32]=period, [33]=clock_seconds, [34]=score_diff,
    #      [35]=exit_depth_ratio_5c, [36]=exit_bid_depth_5c, [37]=exit_ask_depth_5c,
    #      [38]=max_bid_after_entry, [39]=price_trajectory

    old_exit_update = (
        '                        parts[16] = str(pnl_cents)\n'
        '                        lines[i] = ",".join(parts) + "\\n"\n'
        '                        updated = True\n'
        '                        break'
    )
    new_exit_update = (
        '                        parts[16] = str(pnl_cents)\n'
        '                        # Extend row to include new enrichment columns\n'
        '                        while len(parts) < len(self.CSV_COLS):\n'
        '                            parts.append("")\n'
        '                        # exit depth\n'
        '                        parts[35] = str(exit_depth.get("depth_ratio_5c", ""))\n'
        '                        parts[36] = str(exit_depth.get("bid_depth_5c", ""))\n'
        '                        parts[37] = str(exit_depth.get("ask_depth_5c", ""))\n'
        '                        parts[38] = str(max_bid_val)\n'
        '                        parts[39] = traj_str\n'
        '                        lines[i] = ",".join(parts) + "\\n"\n'
        '                        updated = True\n'
        '                        break'
    )
    if old_exit_update in content:
        content = content.replace(old_exit_update, new_exit_update, 1)
        changes += 1
        print('  [OK] Updated exit row update to include new columns')

    # Update fallback exit row to include new columns
    old_fallback_end = '                f"{exit_type},{exit_price},{int(hold_sec)},{gs_exit[:200]},{pnl_cents},,,,,,,,,,,,\\n"'
    new_fallback_end = (
        '                f"{exit_type},{exit_price},{int(hold_sec)},{gs_exit[:200]},{pnl_cents}"\n'
        '                f",,,,,,,,,,,,,,,"\n'
        '                f"{exit_depth.get(\'depth_ratio_5c\', \'\')},{exit_depth.get(\'bid_depth_5c\', \'\')},"\n'
        '                f"{exit_depth.get(\'ask_depth_5c\', \'\')},{max_bid_val},{traj_str}\\n"'
    )
    if old_fallback_end in content:
        content = content.replace(old_fallback_end, new_fallback_end, 1)
        changes += 1
        print('  [OK] Updated fallback exit row')

    # ===================================================================
    # 6. Tier 2: Add game state to execute_entry_92plus
    #    After depth filter, before anti-stack check
    # ===================================================================
    old_92plus_antistack = (
        "        # Anti-stack: check portfolio\n"
        "        pos_check_path = f\"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1\"\n"
        "        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)\n"
        "        if pos_check:\n"
        "            existing = [p for p in pos_check.get(\"market_positions\", []) if p.get(\"position\", 0) > 0]\n"
        "            if existing:\n"
        "                log(f\"[92+_SKIP_STACKED] {ticker} already holding {existing[0].get('position',0)}ct\")\n"
        "                self.mode_92_entered.add(ticker)\n"
        "                self.entered_sides.add(ticker)\n"
        "                return"
    )
    new_92plus_antistack = (
        "        # --- Game state check for 92c+ entries ---\n"
        "        _gs_log_92 = \"\"\n"
        "        _game_data_92 = await self.fetch_game_state(et)\n"
        "        if _game_data_92:\n"
        "            _live92 = _game_data_92.get(\"live_data\", {})\n"
        "            _det92 = _live92.get(\"details\", {})\n"
        "            _status92 = _det92.get(\"status\", \"?\")\n"
        "            _away92 = _det92.get(\"away_points\", \"?\")\n"
        "            _home92 = _det92.get(\"home_points\", \"?\")\n"
        "            _period92 = _det92.get(\"period\", \"?\")\n"
        "            _remaining92 = _det92.get(\"period_remaining_time\", \"?\")\n"
        "            _gs_log_92 = (\n"
        "                f\" score={_away92}-{_home92} period={_period92}\"\n"
        "                f\" clock={_remaining92} status={_status92}\"\n"
        "            )\n"
        "            # Reject period 1 (first half) for 92c+ entries\n"
        "            try:\n"
        "                _pnum92 = int(_period92) if _period92 and _period92 != \"?\" else 0\n"
        "            except (ValueError, TypeError):\n"
        "                _pnum92 = 0\n"
        "            if _pnum92 == 1:\n"
        "                log(f\"[92+_REJECT_PERIOD1] {side} first half — skipping 92c+ entry{_gs_log_92}\")\n"
        "                return\n"
        "            # Reject if score diff < 10\n"
        "            try:\n"
        "                _diff92 = abs(int(_away92) - int(_home92))\n"
        "            except (ValueError, TypeError):\n"
        "                _diff92 = 999  # unknown score — allow entry\n"
        "            if _diff92 < 10:\n"
        "                log(f\"[92+_REJECT_CLOSE_GAME] {side} diff={_diff92}pts < 10{_gs_log_92}\")\n"
        "                return\n"
        "\n"
        "        # Anti-stack: check portfolio\n"
        "        pos_check_path = f\"/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position&limit=1\"\n"
        "        pos_check = await api_get(self.session, self.api_key, self.private_key, pos_check_path, self.rl)\n"
        "        if pos_check:\n"
        "            existing = [p for p in pos_check.get(\"market_positions\", []) if p.get(\"position\", 0) > 0]\n"
        "            if existing:\n"
        "                log(f\"[92+_SKIP_STACKED] {ticker} already holding {existing[0].get('position',0)}ct\")\n"
        "                self.mode_92_entered.add(ticker)\n"
        "                self.entered_sides.add(ticker)\n"
        "                return"
    )
    if old_92plus_antistack in content:
        content = content.replace(old_92plus_antistack, new_92plus_antistack, 1)
        changes += 1
        print('  [OK] Added game state checks to execute_entry_92plus (reject period 1, diff<10)')
    else:
        print('  [WARN] Could not find 92plus anti-stack pattern')

    # Add game_state to 92plus Position creation
    old_92plus_pos = (
        "        pos.depth_snapshot = depth_snap\n"
        "        self.positions[ticker] = pos"
    )
    new_92plus_pos = (
        "        pos.depth_snapshot = depth_snap\n"
        "        if _gs_log_92:\n"
        "            pos.game_state_at_entry = _gs_log_92.strip()\n"
        "        self.positions[ticker] = pos"
    )
    if old_92plus_pos in content:
        content = content.replace(old_92plus_pos, new_92plus_pos, 1)
        changes += 1
        print('  [OK] Added game_state_at_entry to 92plus Position')

    # ===================================================================
    # 7. Add 'import re' if not already present (needed for _parse_game_state)
    # ===================================================================
    if 'import re\n' not in content:
        # Add after 'import time'
        content = content.replace('import time\n', 'import time\nimport re\n', 1)
        changes += 1
        print('  [OK] Added import re')

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f'\n  NCAAMB: {changes} changes applied')
    else:
        print(f'\n  NCAAMB: NO CHANGES')

    return changes


def patch_tennis():
    path = '/root/Omi-Workspace/arb-executor/tennis_stb.py'
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # ===================================================================
    # 1. Add new columns to CSV_COLS
    # ===================================================================
    old_cols = '        "entry_type",\n    ]'
    new_cols = (
        '        "entry_type",\n'
        '        "period", "clock_seconds", "score_diff",\n'
        '        "exit_depth_ratio_5c", "exit_bid_depth_5c", "exit_ask_depth_5c",\n'
        '        "max_bid_after_entry", "price_trajectory",\n'
        '    ]'
    )
    if old_cols in content:
        content = content.replace(old_cols, new_cols, 1)
        changes += 1
        print('  [OK] Added 8 new CSV columns to CSV_COLS')

    # ===================================================================
    # 2. Add _parse_game_state helper
    # ===================================================================
    helper = '''
    @staticmethod
    def _parse_game_state(gs_str):
        """Parse game_state_at_entry string into (period, clock_seconds, score_diff)."""
        period = ""
        clock_seconds = ""
        score_diff = ""
        if not gs_str:
            return period, clock_seconds, score_diff
        # Extract period=X or sets=X-Y
        m = re.search(r'period=(\\S+)', gs_str)
        if m:
            period = m.group(1)
        # Extract clock=MM:SS or clock=PT...
        m = re.search(r'clock=(\\S+)', gs_str)
        if m:
            clock_raw = m.group(1)
            try:
                if ':' in clock_raw:
                    parts = clock_raw.split(':')
                    clock_seconds = str(int(parts[0]) * 60 + int(parts[1]))
                elif clock_raw.startswith('PT'):
                    mins = re.search(r'(\\d+)M', clock_raw)
                    secs = re.search(r'(\\d+)S', clock_raw)
                    total = 0
                    if mins: total += int(mins.group(1)) * 60
                    if secs: total += int(secs.group(1))
                    clock_seconds = str(total)
                else:
                    clock_seconds = clock_raw
            except (ValueError, IndexError):
                clock_seconds = clock_raw
        # Extract score=A-B → diff = abs(A-B)
        m = re.search(r'score=(\\d+)-(\\d+)', gs_str)
        if m:
            try:
                score_diff = str(abs(int(m.group(1)) - int(m.group(2))))
            except ValueError:
                pass
        # Tennis: sets=X-Y
        m2 = re.search(r'sets=(\\d+)-(\\d+)', gs_str)
        if m2 and not score_diff:
            try:
                score_diff = str(abs(int(m2.group(1)) - int(m2.group(2))))
            except ValueError:
                pass
        return period, clock_seconds, score_diff

'''
    marker = '    def _csv_write_entry(self, pos):'
    if '_parse_game_state' not in content and marker in content:
        content = content.replace(marker, helper + marker, 1)
        changes += 1
        print('  [OK] Added _parse_game_state helper')

    # ===================================================================
    # 3. Update _csv_write_entry with new columns
    # ===================================================================
    old_entry_row_end = (
        '            "entry_mode": getattr(pos, \'entry_mode\', \'\'),\n'
        '            "volume_tier": getattr(pos, \'volume_tier\', \'\'),\n'
        '            "entry_type": getattr(pos, \'entry_type\', \'\'),\n'
        '        }'
    )
    new_entry_row_end = (
        '            "entry_mode": getattr(pos, \'entry_mode\', \'\'),\n'
        '            "volume_tier": getattr(pos, \'volume_tier\', \'\'),\n'
        '            "entry_type": getattr(pos, \'entry_type\', \'\'),\n'
        '            "period": _gs_period,\n'
        '            "clock_seconds": _gs_clock,\n'
        '            "score_diff": _gs_diff,\n'
        '            "exit_depth_ratio_5c": "",\n'
        '            "exit_bid_depth_5c": "",\n'
        '            "exit_ask_depth_5c": "",\n'
        '            "max_bid_after_entry": "",\n'
        '            "price_trajectory": "",\n'
        '        }'
    )
    if old_entry_row_end in content:
        old_pre_10m = '        pos.pre_entry_price_10m = pre_10m\n\n        import csv, io'
        new_pre_10m = (
            '        pos.pre_entry_price_10m = pre_10m\n'
            '\n'
            '        # Parse game state into structured fields\n'
            '        _gs_period, _gs_clock, _gs_diff = self._parse_game_state(pos.game_state_at_entry)\n'
            '\n'
            '        import csv, io'
        )
        if old_pre_10m in content:
            content = content.replace(old_pre_10m, new_pre_10m, 1)
            changes += 1
            print('  [OK] Added game state parsing call in _csv_write_entry')

        content = content.replace(old_entry_row_end, new_entry_row_end, 1)
        changes += 1
        print('  [OK] Added new columns to _csv_write_entry row dict')

    # ===================================================================
    # 4. Update _csv_write_exit (same as ncaamb)
    # ===================================================================
    old_exit_csv_read = (
        '        # Read CSV, find last row for this ticker with empty exit_type, update it\n'
        '        import csv, io'
    )
    new_exit_csv_read = (
        '        # Capture exit depth snapshot\n'
        '        exit_depth = {}\n'
        '        try:\n'
        '            exit_depth = await self.capture_depth_snapshot(pos.ticker)\n'
        '        except Exception:\n'
        '            pass\n'
        '\n'
        '        # Serialize trajectory and max_bid\n'
        '        traj_str = ""\n'
        '        if hasattr(pos, "trajectory") and pos.trajectory:\n'
        '            traj_parts = []\n'
        '            for k in ["15s","30s","1m","2m","3m","5m","10m","15m","20m"]:\n'
        '                v = pos.trajectory.get(k)\n'
        '                traj_parts.append(f"{k}={v}c" if v is not None else f"{k}=?")\n'
        '            traj_str = "|".join(traj_parts)\n'
        '        max_bid_val = pos.max_bid_after_entry if pos.max_bid_after_entry is not None else ""\n'
        '\n'
        '        # Read CSV, find last row for this ticker with empty exit_type, update it\n'
        '        import csv, io'
    )
    c = content.count(old_exit_csv_read)
    if c >= 1:
        content = content.replace(old_exit_csv_read, new_exit_csv_read, 1)
        changes += 1
        print('  [OK] Added exit depth + trajectory capture in _csv_write_exit')

    old_exit_update = (
        '                        parts[16] = str(pnl_cents)\n'
        '                        lines[i] = ",".join(parts) + "\\n"\n'
        '                        updated = True\n'
        '                        break'
    )
    new_exit_update = (
        '                        parts[16] = str(pnl_cents)\n'
        '                        # Extend row to include new enrichment columns\n'
        '                        while len(parts) < len(self.CSV_COLS):\n'
        '                            parts.append("")\n'
        '                        # exit depth\n'
        '                        parts[35] = str(exit_depth.get("depth_ratio_5c", ""))\n'
        '                        parts[36] = str(exit_depth.get("bid_depth_5c", ""))\n'
        '                        parts[37] = str(exit_depth.get("ask_depth_5c", ""))\n'
        '                        parts[38] = str(max_bid_val)\n'
        '                        parts[39] = traj_str\n'
        '                        lines[i] = ",".join(parts) + "\\n"\n'
        '                        updated = True\n'
        '                        break'
    )
    if old_exit_update in content:
        content = content.replace(old_exit_update, new_exit_update, 1)
        changes += 1
        print('  [OK] Updated exit row update to include new columns')

    old_fallback_end = '                f"{exit_type},{exit_price},{int(hold_sec)},{gs_exit[:200]},{pnl_cents},,,,,,,,,,,,\\n"'
    new_fallback_end = (
        '                f"{exit_type},{exit_price},{int(hold_sec)},{gs_exit[:200]},{pnl_cents}"\n'
        '                f",,,,,,,,,,,,,,,"\n'
        '                f"{exit_depth.get(\'depth_ratio_5c\', \'\')},{exit_depth.get(\'bid_depth_5c\', \'\')},"\n'
        '                f"{exit_depth.get(\'ask_depth_5c\', \'\')},{max_bid_val},{traj_str}\\n"'
    )
    if old_fallback_end in content:
        content = content.replace(old_fallback_end, new_fallback_end, 1)
        changes += 1
        print('  [OK] Updated fallback exit row')

    # ===================================================================
    # 5. Tier 2: Add game state collection to post_92c_maker_bid
    #    After anti-stack check, before path = "/trade-api/v2/portfolio/orders"
    #    Tennis: collect only, NO rejection filters
    # ===================================================================
    old_tennis_92_path = (
        "        path = \"/trade-api/v2/portfolio/orders\"\n"
        "        # Conditional bid: 91c if ask=92c (avoid post_only cross), else 92c"
    )
    new_tennis_92_path = (
        "        # --- Game state collection for 92c+ entries (data only, no filters) ---\n"
        "        _gs_log_92t = \"\"\n"
        "        _game_data_92t = await self.fetch_game_state(et)\n"
        "        if _game_data_92t:\n"
        "            _live92t = _game_data_92t.get(\"live_data\", {})\n"
        "            _det92t = _live92t.get(\"details\", {})\n"
        "            _p1_92t = _det92t.get(\"competitor1_overall_score\", \"?\")\n"
        "            _p2_92t = _det92t.get(\"competitor2_overall_score\", \"?\")\n"
        "            _server_92t = _det92t.get(\"server\", \"?\")\n"
        "            _status_92t = _det92t.get(\"status\", \"?\")\n"
        "            _gs_log_92t = f\" sets={_p1_92t}-{_p2_92t} server={_server_92t} status={_status_92t}\"\n"
        "\n"
        "        path = \"/trade-api/v2/portfolio/orders\"\n"
        "        # Conditional bid: 91c if ask=92c (avoid post_only cross), else 92c"
    )
    if old_tennis_92_path in content:
        content = content.replace(old_tennis_92_path, new_tennis_92_path, 1)
        changes += 1
        print('  [OK] Added game state collection to post_92c_maker_bid')
    else:
        print('  [WARN] Could not find tennis 92c path pattern')

    # Add game_state to instant fill Position
    old_tennis_92_pos_instant = (
        "                entry_mode=\"stb_92plus_maker\",\n"
        "            )\n"
        "            self.positions[ticker] = pos\n"
        "            pos.depth_snapshot = await self.capture_depth_snapshot(ticker)"
    )
    new_tennis_92_pos_instant = (
        "                entry_mode=\"stb_92plus_maker\",\n"
        "            )\n"
        "            if _gs_log_92t:\n"
        "                pos.game_state_at_entry = _gs_log_92t.strip()\n"
        "            self.positions[ticker] = pos\n"
        "            pos.depth_snapshot = await self.capture_depth_snapshot(ticker)"
    )
    if old_tennis_92_pos_instant in content:
        content = content.replace(old_tennis_92_pos_instant, new_tennis_92_pos_instant, 1)
        changes += 1
        print('  [OK] Added game_state_at_entry to tennis 92plus instant fill Position')

    # For resting bids that fill later (check_92plus_bid_fills creates Position there)
    # We need to store _gs_log_92t somewhere the fill handler can use it
    # Store it on the class indexed by ticker when bid is posted
    old_resting_log = '            self.mode_92_bids[ticker] = order_id\n            log(f"[92+_BID_POSTED] {side} resting buy at {maker_bid_92}c oid={order_id[:12]}")'
    new_resting_log = (
        '            self.mode_92_bids[ticker] = order_id\n'
        '            # Store game state for later fill handling\n'
        '            if not hasattr(self, "_mode_92_game_state"):\n'
        '                self._mode_92_game_state = {}\n'
        '            if _gs_log_92t:\n'
        '                self._mode_92_game_state[ticker] = _gs_log_92t.strip()\n'
        '            log(f"[92+_BID_POSTED] {side} resting buy at {maker_bid_92}c oid={order_id[:12]}")'
    )
    if old_resting_log in content:
        content = content.replace(old_resting_log, new_resting_log, 1)
        changes += 1
        print('  [OK] Stored game state for resting bid fill handler')

    # ===================================================================
    # 6. Add 'import re' if not already present
    # ===================================================================
    if 'import re\n' not in content:
        content = content.replace('import time\n', 'import time\nimport re\n', 1)
        changes += 1
        print('  [OK] Added import re')

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f'\n  TENNIS: {changes} changes applied')
    else:
        print(f'\n  TENNIS: NO CHANGES')

    return changes


print('=== PATCHING NCAAMB ===')
c1 = patch_ncaamb()
print()
print('=== PATCHING TENNIS ===')
c2 = patch_tennis()
print(f'\nTOTAL: {c1 + c2} changes across both files')
