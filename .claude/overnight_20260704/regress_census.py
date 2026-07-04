#!/usr/bin/env python3
"""[READ-ONLY] Regression sweep: event-type census for two nights side by side,
plus new-flag interaction extracts. Usage: python3 regress_census.py OLDLOG NEWLOG"""
import json, sys
from collections import Counter, defaultdict

OLD, NEW = sys.argv[1], sys.argv[2]

def census(path):
    c = Counter()
    err = Counter()
    inter = defaultdict(list)   # interaction extracts
    for line in open(path, encoding='utf-8', errors='replace'):
        if '"event"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        e = o.get('event')
        c[e] += 1
        d = o.get('details', {})
        if e in ('error', 'on_bbo_update_error'):
            err[str(d.get('error'))[:90]] += 1
        # flag-interaction extracts (keep small)
        if e in ('leg2_reshuffle_reaim', 'premarket_walk_capped', 'freeze_at_gun_hold',
                 'liquid_repost_at_touch', 'completion_ceiling_capped', 'match_live_grace_armed',
                 'match_live_resting_cancel'):
            if len(inter[e]) < 400:
                inter[e].append({'ts': o.get('ts'), 'tk': o.get('ticker'), **{k: d.get(k) for k in
                    ('event', 'from', 'to', 'leg1_basis', 'goal', 'proposed_target', 'walk_ceiling',
                     'conception_cell', 'cap', 'graced', 'grace_sec', 'depth_target', 'touch',
                     'target_price') if k in d}})
    return c, err, inter

co, eo, _ = census(OLD)
cn, en, inter = census(NEW)

print("==== EVENT-TYPE CENSUS DIFF (new vs old night; sorted by |delta|) ====")
keys = set(co) | set(cn)
rows = sorted(keys, key=lambda k: -abs(cn.get(k, 0) - co.get(k, 0)))
print(f"{'event':42s} {'old':>8} {'new':>8} {'delta':>8}")
for k in rows:
    a, b = co.get(k, 0), cn.get(k, 0)
    if a == 0 and b == 0:
        continue
    tag = ' NEW' if a == 0 else (' GONE' if b == 0 else '')
    print(f"{str(k):42s} {a:>8} {b:>8} {b-a:>+8}{tag}")

print("\n==== ERROR CLASSES old night ====")
for k, v in eo.most_common(10):
    print(f"  {v:>6}  {k}")
print("==== ERROR CLASSES new night ====")
for k, v in en.most_common(10):
    print(f"  {v:>6}  {k}")

print("\n==== FLAG-INTERACTION EXTRACTS (new night) ====")
for e, rows in inter.items():
    print(f"-- {e} ({len(rows)} shown-capped)")
    for r in rows[:25]:
        print("   ", json.dumps(r))
