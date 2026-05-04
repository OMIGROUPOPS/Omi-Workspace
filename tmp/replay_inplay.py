import json, glob, sqlite3, re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

_month_map = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
              "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

def date_ok(event_ticker, sched_start_time):
    _dm = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", event_ticker)
    if not _dm:
        return True, None
    try:
        tk_date = datetime(2000+int(_dm.group(1)), _month_map[_dm.group(2)],
                           int(_dm.group(3)), 16, 0, tzinfo=timezone.utc)
        sched_dt = datetime.fromisoformat(sched_start_time.replace("Z","+00:00"))
        delta = abs((sched_dt - tk_date).total_seconds())
        return delta <= 43200, delta
    except Exception:
        return True, None

# Load commence_times from kalshi_price_snapshots
conn = sqlite3.connect("tennis.db")
cur = conn.cursor()
cur.execute("SELECT ticker, MAX(commence_time) FROM kalshi_price_snapshots WHERE commence_time IS NOT NULL GROUP BY ticker")
commence_map = {ticker: ct for ticker, ct in cur.fetchall()}
conn.close()

# Collect schedule_match events per event_ticker (not per side ticker)
# The schedule_match log uses event_ticker in details.event
schedule_matches = defaultdict(list)  # event_ticker -> [(ts, start_time, method)]

# Collect entry_filled events that fired after commence_time
in_play_fills = []

for path in sorted(glob.glob("logs/live_v3_*.jsonl")):
    with open(path) as f:
        for line in f:
            try:
                ev = json.loads(line)
            except:
                continue
            evt = ev.get("event")

            if evt == "schedule_match":
                details = ev.get("details", {})
                et = details.get("event", "")
                st = details.get("start_time", "")
                method = details.get("method", "?")
                if et and st:
                    schedule_matches[et].append((ev.get("ts",""), st, method))

            if evt == "entry_filled":
                ticker = ev.get("ticker", "")
                ts = ev.get("ts", "")
                if not ticker or not ts:
                    continue
                ct_iso = commence_map.get(ticker)
                if not ct_iso:
                    continue
                try:
                    fill_ts_clean = ts.replace(" ET","").strip()
                    fill_dt = datetime.strptime(fill_ts_clean, "%Y-%m-%d %I:%M:%S %p")
                    fill_utc = fill_dt.replace(tzinfo=timezone.utc) + timedelta(hours=4)
                    commence_utc = datetime.fromisoformat(ct_iso.replace("Z","+00:00"))
                    if fill_utc > commence_utc:
                        # Extract event_ticker from ticker (drop the side suffix)
                        parts = ticker.rsplit("-", 1)
                        event_ticker = parts[0] if len(parts) == 2 else ticker
                        in_play_fills.append({
                            "ticker": ticker,
                            "event_ticker": event_ticker,
                            "fill_ts": ts,
                            "actual_commence_utc": ct_iso,
                            "delta_hr": (fill_utc - commence_utc).total_seconds() / 3600,
                        })
                except Exception:
                    continue

print("Found %d in-play fills in JSONL logs" % len(in_play_fills))
print()

correctly_caught = 0
not_caught = 0
no_schedule_match = 0
detail_caught = []
detail_not_caught = []
detail_no_sched = []

for fill in in_play_fills:
    et = fill["event_ticker"]
    matches = schedule_matches.get(et, [])
    if not matches:
        no_schedule_match += 1
        detail_no_sched.append(fill)
        continue

    # Use the last schedule_match before the fill
    last_match = matches[-1]
    ts, sched_start, method = last_match

    ok, delta = date_ok(et, sched_start)
    delta_h = delta / 3600 if delta else 0

    if not ok:
        correctly_caught += 1
        detail_caught.append((fill["ticker"], sched_start, fill["actual_commence_utc"], delta_h, method))
    else:
        not_caught += 1
        detail_not_caught.append((fill["ticker"], sched_start, fill["actual_commence_utc"], delta_h, method, fill["fill_ts"]))

print("=" * 80)
print("RESULTS")
print("=" * 80)
print("  Patched logic would have CAUGHT (rejected):  %d" % correctly_caught)
print("  Patched logic would NOT have caught:         %d" % not_caught)
print("  No schedule_match event in logs:             %d" % no_schedule_match)
print()

if detail_caught:
    print("CAUGHT cases (sample, first 10):")
    for tk, sched, actual, dh, method in detail_caught[:10]:
        print("  %-45s method=%-12s sched=%s  actual=%s  delta=%.1fh" % (
            tk[-45:], method, sched, actual, dh))

if detail_not_caught:
    print()
    print("NOT CAUGHT (need investigation):")
    for tk, sched, actual, dh, method, fill_ts in detail_not_caught:
        print("  %-45s method=%-12s sched=%s  actual=%s  delta=%.1fh  filled=%s" % (
            tk[-45:], method, sched, actual, dh, fill_ts))

if detail_no_sched:
    print()
    print("NO SCHEDULE_MATCH logged (%d cases):" % len(detail_no_sched))
    for fill in detail_no_sched[:10]:
        print("  %-45s  filled=%s  actual_commence=%s  delta=%.1fh after commence" % (
            fill["ticker"][-45:], fill["fill_ts"][:25], fill["actual_commence_utc"], fill["delta_hr"]))
    if len(detail_no_sched) > 10:
        print("  ... and %d more" % (len(detail_no_sched) - 10))
