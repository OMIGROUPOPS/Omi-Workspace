#!/usr/bin/env python3
"""Apply the schedule date mismatch fix to live_v3.py"""

with open('/root/Omi-Workspace/arb-executor/live_v3.py', 'r') as f:
    content = f.read()

# Block 1: Insert date guard helper and add _date_ok check to direct_6char block
old_block1 = """        # Try direct match first
        result = match_kalshi_event(event_ticker, self.schedule)
        if result:
            self._log("schedule_match", {"""

new_block1 = '''        # Extract ticker date for cross-day mismatch guard
        import re as _re
        _dm = _re.search(r"-(\\d{2})([A-Z]{3})(\\d{2})", event_ticker)
        _month_map = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
                      "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

        def _date_ok(sched_result):
            """Reject schedule match if start_time date differs from ticker date by >12h."""
            if not _dm:
                return True
            try:
                tk_date = datetime(2000+int(_dm.group(1)), _month_map[_dm.group(2)],
                                   int(_dm.group(3)), 16, 0, tzinfo=timezone.utc)
                sched_dt = datetime.fromisoformat(sched_result.get("start_time","").replace("Z","+00:00"))
                if abs((sched_dt - tk_date).total_seconds()) > 43200:
                    self._log("schedule_date_mismatch", {
                        "event": event_ticker,
                        "ticker_date": tk_date.strftime("%Y-%m-%d"),
                        "schedule_date": sched_dt.strftime("%Y-%m-%dT%H:%M"),
                    })
                    return False
            except Exception:
                pass
            return True

        # Try direct match first
        result = match_kalshi_event(event_ticker, self.schedule)
        if result and _date_ok(result):
            self._log("schedule_match", {'''

assert old_block1 in content, "Block 1 not found in live_v3.py!"
content = content.replace(old_block1, new_block1, 1)

# Block 2: Add _date_ok check to fuzzy_name block
old_block2 = """            result = match_kalshi_event(event_ticker, self.schedule, kalshi_player_names=player_names)
            if result:
                self._log("schedule_match", {
                    "event": event_ticker,
                    "method": "fuzzy_name","""

new_block2 = """            result = match_kalshi_event(event_ticker, self.schedule, kalshi_player_names=player_names)
            if result and _date_ok(result):
                self._log("schedule_match", {
                    "event": event_ticker,
                    "method": "fuzzy_name","""

assert old_block2 in content, "Block 2 not found in live_v3.py!"
content = content.replace(old_block2, new_block2, 1)

with open('/root/Omi-Workspace/arb-executor/live_v3.py', 'w') as f:
    f.write(content)

print("Both patches applied successfully.")
