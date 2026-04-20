#!/usr/bin/env python3
"""One-time cleanup: remove future-date tombstones from processed_events.json."""
import json, re, datetime

PROCESSED_FILE = "/root/Omi-Workspace/arb-executor/state/live_v3_processed.json"

with open(PROCESSED_FILE) as f:
    data = json.load(f)

if isinstance(data, list):
    events = set(data)
else:
    events = set(data.get("processed_events", data.get("events", [])))

today = datetime.date.today()
month_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
             "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}

to_remove = []
for evt in events:
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", evt)
    if not m:
        continue
    try:
        evt_date = datetime.date(2000 + int(m.group(1)), month_map[m.group(2)], int(m.group(3)))
        if evt_date >= today:
            to_remove.append(evt)
    except Exception:
        pass

print("Current tombstones: %d" % len(events))
print("Future-date tombstones to remove: %d" % len(to_remove))
for evt in sorted(to_remove):
    print("  %s" % evt)

events -= set(to_remove)

with open(PROCESSED_FILE, "w") as f:
    json.dump(sorted(events), f)

print("\nRemaining tombstones: %d" % len(events))
print("Saved to %s" % PROCESSED_FILE)
