#!/usr/bin/env python3
"""
refresh_schedule.py - Cron job to refresh tennis schedule.

Fetches today + tomorrow from TennisExplorer + ESPN.
Writes combined schedule to state/schedule.json.
Run via cron every 30 minutes.

  */30 * * * * cd /root/Omi-Workspace/arb-executor && python3 refresh_schedule.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tennis_schedule import get_match_schedule

OUT_PATH = Path(__file__).resolve().parent / "state" / "schedule.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

now = datetime.now(ET)
today = (now.year, now.month, now.day)

# Tomorrow
from datetime import timedelta
tomorrow_dt = now + timedelta(days=1)
tomorrow = (tomorrow_dt.year, tomorrow_dt.month, tomorrow_dt.day)

combined = get_match_schedule(*today)
sched_tomorrow = get_match_schedule(*tomorrow)
for k, v in sched_tomorrow.items():
    if k not in combined:
        combined[k] = v

output = {
    "fetched_et": now.strftime("%Y-%m-%d %I:%M:%S %p ET"),
    "fetched_epoch": time.time(),
    "today": "%04d-%02d-%02d" % today,
    "tomorrow": "%04d-%02d-%02d" % tomorrow,
    "count": len(combined),
    "schedule": combined,
}

with open(OUT_PATH, "w") as f:
    json.dump(output, f)

print("[%s] Schedule refreshed: %d matches -> %s" % (
    now.strftime("%I:%M:%S %p ET"), len(combined), OUT_PATH))
