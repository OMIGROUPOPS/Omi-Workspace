#!/usr/bin/env python3
"""Fix: Add game state rejection filters to 92+ maker path in both bots.

BUG: 92+ maker entries fetch game state for LOGGING ONLY — never reject.
This allows maker bids on not_started/scheduled matches.
FIX: After fetching game state, call check_*_game_state() and reject.
"""

BOTS = {
    "ncaamb": {
        "path": "/root/Omi-Workspace/arb-executor/ncaamb_stb.py",
        "check_fn": "check_ncaamb_game_state",
    },
    "tennis": {
        "path": "/root/Omi-Workspace/arb-executor/tennis_stb.py",
        "check_fn": "check_tennis_game_state",
    },
}

for name, cfg in BOTS.items():
    path = cfg["path"]
    check_fn = cfg["check_fn"]

    with open(path) as f:
        content = f.read()
    original = content

    if name == "ncaamb":
        # ncaamb: logging-only block to replace
        old = '''        # --- Game state collection for 92c+ entries (logging only, no filters) ---
        _gs_log_92 = ""
        _game_data_92 = await self.fetch_game_state(et)
        if not _game_data_92:
            log(f"[92+_SKIP_NOSTATE] {side} — game state unavailable, skipping 92+ entry")
            return
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
            )'''

        new = '''        # --- Game state check for 92c+ entries (with rejection filters) ---
        _gs_log_92 = ""
        _game_data_92 = await self.fetch_game_state(et)
        if not _game_data_92:
            log(f"[92+_SKIP_NOSTATE] {side} — game state unavailable, skipping 92+ entry")
            return
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
            # Apply same game state filters as STB path
            _reject_92 = self.check_ncaamb_game_state(ticker, _game_data_92)
            if _reject_92:
                log(f"[92+_REJECT_GAMESTATE] {side} — {_reject_92}{_gs_log_92}")
                return'''

    else:  # tennis
        old = '''        # --- Game state collection for 92c+ entries (data only, no filters) ---
        _gs_log_92t = ""
        _game_data_92t = await self.fetch_game_state(et)
        if not _game_data_92t:
            log(f"[92+_SKIP_NOSTATE] {side} — game state unavailable, skipping 92+ entry")
            return
        if _game_data_92t:
            _live92t = _game_data_92t.get("live_data", {})
            _det92t = _live92t.get("details", {})
            _p1_92t = _det92t.get("competitor1_overall_score", "?")
            _p2_92t = _det92t.get("competitor2_overall_score", "?")
            _server_92t = _det92t.get("server", "?")
            _status_92t = _det92t.get("status", "?")
            _gs_log_92t = f" sets={_p1_92t}-{_p2_92t} server={_server_92t} status={_status_92t}"'''

        new = '''        # --- Game state check for 92c+ entries (with rejection filters) ---
        _gs_log_92t = ""
        _game_data_92t = await self.fetch_game_state(et)
        if not _game_data_92t:
            log(f"[92+_SKIP_NOSTATE] {side} — game state unavailable, skipping 92+ entry")
            return
        if _game_data_92t:
            _live92t = _game_data_92t.get("live_data", {})
            _det92t = _live92t.get("details", {})
            _p1_92t = _det92t.get("competitor1_overall_score", "?")
            _p2_92t = _det92t.get("competitor2_overall_score", "?")
            _server_92t = _det92t.get("server", "?")
            _status_92t = _det92t.get("status", "?")
            _gs_log_92t = f" sets={_p1_92t}-{_p2_92t} server={_server_92t} status={_status_92t}"
            # Apply same game state filters as STB path
            _reject_92t = self.check_tennis_game_state(ticker, _game_data_92t)
            if _reject_92t:
                log(f"[92+_REJECT_GAMESTATE] {side} — {_reject_92t}{_gs_log_92t}")
                return'''

    if old in content:
        content = content.replace(old, new)
        with open(path, "w") as f:
            f.write(content)
        print(f"  [{name}] FIXED: 92+ maker path now applies game state rejection filters")
    else:
        print(f"  [{name}] WARN: pattern not found")
        # Debug
        if "data only, no filters" in content:
            print(f"    Found 'data only' variant")
        if "logging only, no filters" in content:
            print(f"    Found 'logging only' variant")

print("\nDone.")
