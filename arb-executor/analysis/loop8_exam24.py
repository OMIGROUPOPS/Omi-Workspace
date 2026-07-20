#!/usr/bin/env python3
# LOOP 8 — THE 24-HOUR EXAM, lap 1. The operator's model, three branches:
#   RISER bands  -> divot bids DURING CLIMBS (walking level = rolling
#                   30-min median - dip_p50, armed only while med >= anchor)
#   FALLER bands -> destination casts NOT-TOO-DEEP (static level =
#                   anchor + net_med + 2c shallow-of-destination)
#   FLAT bands   -> dual divot bids (walking level = med - dip_p50)
# Two gauges, the operator's: (a) both-legs-negative rate (fill < own W1
# close, both legs of a dual) vs the 75% bar; (b) combined price tiers.
# Frame: W1 only (T-8h -> sched). Band call = loop5 two-phase convention
# (recognition at T-6h cut, purity >= 0.5, else default flat band); all
# entries placed at the cut (conception parks out of scope this lap,
# declared). Tape = analysis/trades REST CSVs (the store lacks JUL19/20
# -> the divot-v2 tables are OUT-OF-SAMPLE vs this window, verified).
# Clocks = kalshi_schedule_primary (session-clock class named; W1 edges
# carry that error where no honest source exists).
import csv, json, glob, statistics, sys, time
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = '/root/Omi-Workspace/arb-executor'
ET = ZoneInfo('America/New_York')
BMAP = json.load(open(ROOT + '/state/band_map_v1.json'))['cats']
DV2 = json.load(open(ROOT + '/state/divot_tables_v2.json'))['bands']
RECOG = json.load(open(ROOT + '/state/drift_surfaces_v1.json')).get(
    'recognition', {})
BIG4 = {'KXATPMATCH': 'ATP_MAIN', 'KXWTAMATCH': 'WTA_MAIN',
        'KXATPCHALLENGERMATCH': 'ATP_CHALL',
        'KXWTACHALLENGERMATCH': 'WTA_CHALL'}
NOW = time.time()
LOGS = [ROOT + '/logs/live_v3_20260718_part2_recovered.jsonl',
        ROOT + '/logs/live_v3_20260720.jsonl']

def cat_of(event):
    for pfx, cat in BIG4.items():
        if event.startswith(pfx + '-'):
            return cat
    return None

# ---- schedules: LAST schedule_match line per event wins ----------------
sched = {}
for path in LOGS:
    try:
        fh = open(path, encoding='utf-8', errors='replace')
    except OSError:
        continue
    for line in fh:
        if '"schedule_match"' not in line:
            continue
        try:
            j = json.loads(line)
        except ValueError:
            continue
        d = j.get('details') or {}
        ev, st = d.get('event'), d.get('start_time')
        if not ev or not st or not cat_of(ev):
            continue
        try:
            sched[ev] = datetime.fromisoformat(st).timestamp()
        except ValueError:
            continue

exam = {ev: s for ev, s in sched.items() if NOW - 24 * 3600 <= s <= NOW}

# ---- tape ---------------------------------------------------------------
def load_tape(tk):
    rows = []
    try:
        fh = open(ROOT + '/analysis/trades/' + tk + '.csv')
    except OSError:
        return rows
    for r in csv.DictReader(fh):
        try:
            if not r.get('ts_et') or not r.get('price'):
                continue
            ts = datetime.strptime(r['ts_et'], '%Y-%m-%d %I:%M:%S %p'
                                   ).replace(tzinfo=ET).timestamp()
            rows.append((ts, int(r['price'])))
        except (ValueError, KeyError, TypeError):
            continue
    rows.sort()
    return rows

def pb(a, n, d):
    ab = 'a25' if a <= 25 else 'a50' if a <= 50 else 'a75' if a <= 75 else 'a95'
    nb = ('dn10' if n <= -10 else 'dn3' if n <= -3 else 'flat' if n < 3
          else 'up3' if n < 10 else 'up10')
    return ab + '|' + nb + '|' + ('d0' if d <= 2 else 'd3' if d <= 9 else 'd10')

def dband(cat, a):
    c = BMAP.get(cat)
    if not c or c.get('thin'):
        return None
    fl = [b for b in c['bands'] if b['direction'] == 'flat'] or c['bands']
    return min(fl, key=lambda b: abs(b['anchor_med'] - a))['band']

def band_row(cat, name):
    for b in BMAP[cat]['bands']:
        if b['band'] == name:
            return b
    return None

def simulate(cat, tk, t8, redge):
    tape = load_tape(tk)
    win = [(t, p) for t, p in tape if t8 <= t <= redge]
    if len(win) < 5:
        return None
    pre = [p for t, p in tape if t <= t8]
    anchor = pre[-1] if pre else win[0][1]
    cut = t8 + 2 * 3600
    upto = [(t, p) for t, p in win if t <= cut] or win[:1]
    n_sofar = upto[-1][1] - win[0][1]
    d_sofar = max(0, anchor - min(p for _, p in upto))
    cell = (RECOG.get(cat + '|h6') or {}).get(pb(anchor, n_sofar, d_sofar))
    recog = bool(cell and cell.get('purity', 0) >= 0.5)
    band = cell['top'] if recog else dband(cat, anchor)
    if not band:
        return None
    br = band_row(cat, band)
    dv = DV2.get(band, {})
    dip = dv.get("dip_p90") or dv.get("dip_p50") or br.get("dip_med") or 3
    direction = br['direction']
    close = win[-1][1]
    fill = None
    refused = False
    window = []
    meds = []
    for t, p_ in win:
        window = [(x, q) for x, q in window if x >= t - 1800]
        med = statistics.median([q for _, q in window]) if window else p_
        meds.append((t, med))
        window.append((t, p_))
        if t < max(cut, redge - 2 * 3600):
            continue
        net_now = med - anchor
        if net_now <= -5:
            refused = True          # FALLER regime: refuse the falling leg
            continue
        old_m = [m for x, m in meds if x <= t - 1800]
        med_stable = (med >= old_m[-1] - 1) if old_m else True
        level = max(1, int(round(med)) - int(round(dip)))
        if med_stable and p_ <= level:
            fill = level
            direction = 'riser_regime' if net_now >= 5 else 'flat_regime'
            break
    return {'band': band, 'dir': direction, 'anchor': anchor, 'recog': recog,
            'fill': fill, 'close': close, 'n_prints': len(win), 'refused': refused}

# ---- pairs --------------------------------------------------------------
pairs = []
skip = {'thin_tape': 0, 'one_leg_file': 0, 'no_band': 0}
for ev, s in sorted(exam.items()):
    cat = cat_of(ev)
    legs = sorted({f.rsplit('/', 1)[-1][:-4]
                   for f in glob.glob(ROOT + '/analysis/trades/' + ev + '-*.csv')})
    if len(legs) != 2:
        skip['one_leg_file'] += 1
        continue
    t8 = s - 8 * 3600
    sims = [simulate(cat, tk, t8, s) for tk in legs]
    if any(x is None for x in sims):
        skip['thin_tape'] += 1
        continue
    pairs.append({'event': ev, 'cat': cat, 'legs': dict(zip(legs, sims))})

# ---- gauges -------------------------------------------------------------
def tier(c):
    return '<=93' if c <= 93 else '94-97' if c <= 97 else '98-100' \
        if c <= 100 else '>100'

overall = {'pairs': len(pairs), 'duals': 0, 'both_neg': 0,
           'tiers': defaultdict(int)}
percat = defaultdict(lambda: {'pairs': 0, 'duals': 0, 'both_neg': 0})
perband = defaultdict(lambda: {'legs': 0, 'fills': 0, 'neg': 0, 'deltas': []})
perdir = defaultdict(lambda: {'legs': 0, 'fills': 0, 'neg': 0, 'deltas': []})
percombo = defaultdict(lambda: {'pairs': 0, 'duals': 0, 'both_neg': 0,
                                'gt100': 0})
n_recog = n_default = 0
for pr in pairs:
    cat = pr['cat']
    percat[cat]['pairs'] += 1
    sims = list(pr['legs'].values())
    combo = '+'.join(sorted(sm['dir'] for sm in sims))
    percombo[combo]['pairs'] += 1
    for sm in sims:
        n_recog += 1 if sm['recog'] else 0
        n_default += 0 if sm['recog'] else 1
        for st in (perband[sm['band']], perdir[sm['dir']]):
            st['legs'] += 1
            if sm['fill'] is not None:
                st['fills'] += 1
                dl = sm['fill'] - sm['close']
                st['deltas'].append(dl)
                if dl < 0:
                    st['neg'] += 1
    if all(sm['fill'] is not None for sm in sims):
        overall['duals'] += 1
        percat[cat]['duals'] += 1
        percombo[combo]['duals'] += 1
        combined = sum(sm['fill'] for sm in sims)
        overall['tiers'][tier(combined)] += 1
        if combined > 100:
            percombo[combo]['gt100'] += 1
        if all(sm['fill'] < sm['close'] for sm in sims):
            overall['both_neg'] += 1
            percat[cat]['both_neg'] += 1
            percombo[combo]['both_neg'] += 1

L = ['# LOOP 8 — 24-HOUR EXAM, LAP 5 (dynamic regimes: riser-divot / faller-REFUSE / flat-divot; p90; final-2h) (window %s -> %s ET)'
     % (datetime.fromtimestamp(NOW - 86400, ET).strftime('%m-%d %I:%M %p'),
        datetime.fromtimestamp(NOW, ET).strftime('%m-%d %I:%M %p')),
     'model: riser=divot-during-climb · faller=dest cast net_med+2 shallow'
     ' · flat=dual divot (med-dip_p50, 30min rolling) · entries at T-6h cut',
     'events sched-in-window %d · scored pairs %d · skipped %s'
     % (len(exam), len(pairs), dict(skip)), '']
d = overall
if d['duals']:
    L.append('OVERALL: duals %d/%d (%.1f%%) · BOTH-NEG %d/%d (%.1f%% vs 75'
             '%% bar) · tiers %s'
             % (d['duals'], d['pairs'], 100 * d['duals'] / max(1, d['pairs']),
                d['both_neg'], d['duals'], 100 * d['both_neg'] / d['duals'],
                dict(sorted(d['tiers'].items()))))
else:
    L.append('OVERALL: ZERO duals of %d pairs' % d['pairs'])
for cat, st in sorted(percat.items()):
    bn = 100 * st['both_neg'] / st['duals'] if st['duals'] else 0.0
    L.append('- %s: pairs %d duals %d both_neg %.0f%%'
             % (cat, st['pairs'], st['duals'], bn))
L.append('band calls: recognition %d / default-flat %d' % (n_recog, n_default))
L.append('')
L.append('per-BRANCH (the model\'s three arms):')
for dr, st in sorted(perdir.items()):
    md = statistics.median(st['deltas']) if st['deltas'] else None
    L.append('- %s: legs %d fills %d neg %.0f%% medD %s'
             % (dr, st['legs'], st['fills'],
                100 * st['neg'] / st['fills'] if st['fills'] else 0.0, md))
L.append('per-PAIR-COMBO (duals/both_neg/comb>100):')
for cb, st in sorted(percombo.items(), key=lambda kv: -kv[1]['pairs']):
    L.append('- %s: pairs %d duals %d both_neg %d gt100 %d'
             % (cb, st['pairs'], st['duals'], st['both_neg'], st['gt100']))
L.append('')
L.append('per-band (legs/fills/neg-share/med-delta):')
for band, st in sorted(perband.items(), key=lambda kv: -kv[1]['legs']):
    md = statistics.median(st['deltas']) if st['deltas'] else None
    L.append('- %s: legs %d fills %d neg %.0f%% medD %s'
             % (band, st['legs'], st['fills'],
                100 * st['neg'] / st['fills'] if st['fills'] else 0.0, md))
out = '\n'.join(L) + '\n'
open('/tmp/LOOP8_EXAM24.md', 'w').write(out)
json.dump({'pairs': pairs}, open('/tmp/loop8_exam24_pairs.json', 'w'))
print(out)
