#!/usr/bin/env python3
"""[READ-ONLY] Hourly buckets of placement/fill/hold/stale events for one log.
Usage: python3 hourly_regress.py LOG"""
import json, sys
from collections import defaultdict, Counter

LOG = sys.argv[1]
WATCH = ('order_placed', 'entry_filled', 'v4_place', 'staircase_hold_place',
         'event_skip_stale_book', 'error', 'on_bbo_update_error', 'window_open_set')
by_hour = defaultdict(Counter)
hold_reasons = Counter()
stale_events = Counter()
for line in open(LOG, encoding='utf-8', errors='replace'):
    if '"event"' not in line:
        continue
    try:
        o = json.loads(line)
    except Exception:
        continue
    e = o.get('event')
    if e not in WATCH:
        continue
    ts = o.get('ts', '')            # '2026-07-04 05:00:39 AM ET'
    d = o.get('details', {})
    if e == 'order_placed' and d.get('action') != 'buy':
        continue
    # hour bucket like '07-04 05AM'
    try:
        day = ts.split(' ')[0][5:]
        hh = ts.split(' ')[1].split(':')[0]
        ap = ts.split(' ')[2]
        by_hour[f'{day} {hh}{ap}'][e] += 1
    except Exception:
        pass
    if e == 'staircase_hold_place':
        hold_reasons[json.dumps({k: d.get(k) for k in ('reason', 'cat', 'why', 'hold') if k in d})] += 1
    if e == 'event_skip_stale_book':
        stale_events[d.get('event', '?')] += 1

cols = ['order_placed', 'v4_place', 'entry_filled', 'staircase_hold_place', 'error', 'on_bbo_update_error', 'event_skip_stale_book']
hdr = ['buy_placed', 'v4_place', 'filled', 'stair_hold', 'error', 'bbo_err', 'stale_skip']
print(f"{'hour':12s} " + ' '.join(f'{h:>10}' for h in hdr))
def key(h):
    day, rest = h.split(' ')
    hh = int(rest[:-2]) % 12 + (12 if rest[-2:] == 'PM' else 0)
    return (day, hh)
for h in sorted(by_hour, key=key):
    print(f"{h:12s} " + ' '.join(f'{by_hour[h].get(c,0):>10}' for c in cols))

print("\nstaircase_hold_place reason breakdown:")
for k, v in hold_reasons.most_common(10):
    print(f"  {v:>5}  {k}")
print("\ntop stale-book events:")
for k, v in stale_events.most_common(12):
    print(f"  {v:>6}  {k}")
