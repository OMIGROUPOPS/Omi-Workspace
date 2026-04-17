#!/usr/bin/env python3
"""Clear processed_events for upcoming matches. Keep past/live matches."""
import os, time, base64, json, requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
ak = os.getenv("KALSHI_API_KEY")
pk = serialization.load_pem_private_key(
    (Path(__file__).resolve().parent / "kalshi.pem").read_bytes(),
    password=None, backend=default_backend())
BASE = "https://api.elections.kalshi.com"
ET = ZoneInfo("America/New_York")
BUFFER = 900

def auth(method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": ts}

PROCESSED_FILE = Path(__file__).resolve().parent / "state" / "live_v3_processed.json"
SCHEDULE_FILE = Path(__file__).resolve().parent / "state" / "schedule.json"

now = time.time()
now_et = datetime.fromtimestamp(now, tz=ET)
print("Current time: %s" % now_et.strftime("%I:%M:%S %p ET"))

# Load schedule
sched = json.load(open(SCHEDULE_FILE)).get("schedule", {})
print("Schedule entries: %d" % len(sched))

# Load current processed
with open(PROCESSED_FILE) as f:
    processed = set(json.load(f))
print("\nBEFORE: %d processed events" % len(processed))
for e in sorted(processed):
    print("  %s" % e)

# Step 2: Get positions to force-keep their events
pos_path = "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled"
r = requests.get(BASE + pos_path, headers=auth("GET", pos_path.split("?")[0]), timeout=15)
positions = r.json().get("market_positions", [])
position_events = set()
for p in positions:
    tk = p.get("ticker", "")
    parts = tk.rsplit("-", 1)
    if len(parts) == 2:
        position_events.add(parts[0])
print("\nPositions held (force-keep): %s" % sorted(position_events))

# Step 1: Evaluate each processed event
from tennis_schedule import match_kalshi_event

removed = []
kept = []
new_processed = set()

for evt in sorted(processed):
    # Force-keep if we hold a position
    if evt in position_events:
        new_processed.add(evt)
        kept.append((evt, "has_position"))
        continue

    # Schedule lookup
    entry = match_kalshi_event(evt, sched)
    if entry is None:
        # No schedule match — keep (can't verify)
        new_processed.add(evt)
        kept.append((evt, "no_schedule_match"))
        continue

    st_str = entry.get("start_time", "")
    if not st_str:
        new_processed.add(evt)
        kept.append((evt, "no_start_time"))
        continue

    start_ts = datetime.fromisoformat(st_str.replace("Z", "+00:00")).timestamp()
    time_to_start = start_ts - now
    start_et = datetime.fromtimestamp(start_ts, tz=ET).strftime("%I:%M %p ET")

    if time_to_start > BUFFER:
        # Upcoming — remove so bot can enter
        removed.append((evt, start_et, "%.0f min away" % (time_to_start / 60)))
    else:
        # Inside buffer or live — keep
        new_processed.add(evt)
        if time_to_start > 0:
            kept.append((evt, "inside_buffer (%.0f min to start %s)" % (time_to_start / 60, start_et)))
        else:
            kept.append((evt, "already_started (start was %s)" % start_et))

# Save
with open(PROCESSED_FILE, "w") as f:
    json.dump(sorted(new_processed), f, indent=1)

print("\n" + "=" * 60)
print("REMOVED (%d) — bot will enter these:" % len(removed))
for evt, start_et, detail in removed:
    print("  %-45s  start=%s  (%s)" % (evt, start_et, detail))

print("\nKEPT (%d):" % len(kept))
for evt, reason in kept:
    print("  %-45s  %s" % (evt, reason))

print("\nAFTER: %d processed events" % len(new_processed))
for e in sorted(new_processed):
    print("  %s" % e)
