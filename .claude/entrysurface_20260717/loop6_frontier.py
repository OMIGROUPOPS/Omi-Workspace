#!/usr/bin/env python3
# LOOP 6 - THE DYNAMIC FRONTIER. Metric (all three must clear, holdout,
# viable games only): (a) EACH leg fills below its own W1 close; (b) pair
# sum negative; (c) THE BAR: >=75% of duals with BOTH legs negative.
# Policies not constants: per-band depth SCHEDULES (d_early/d_mid/d_late,
# seeded from the band's own reach quartiles), role-aware (risers park,
# fallers carry depth), recognition re-call at T-6h re-selects the
# schedule, realism = the band's own reach curve must support the level
# (>=8 touches), dead-band games = refusals counted separately.
import json
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / 'state/band_map_v1.json').read_text())
DRIFT = json.loads((ROOT / 'state/drift_surfaces_v1.json').read_text())
RECOG = DRIFT.get('recognition', {})
SURF = DRIFT['bands']

def dband(cat, a):
    c = BMAP['cats'].get(cat)
    if not c or c.get('thin'):
        return None
    fl = [b for b in c['bands'] if b['direction'] == 'flat'] or c['bands']
    return min(fl, key=lambda b: abs(b['anchor_med'] - a))['band']

def meta(band):
    for b in BMAP['cats'][band.split('-')[0]]['bands']:
        if b['band'] == band:
            return b

def pbk(a, n, d):
    ab = 'a25' if a <= 25 else 'a50' if a <= 50 else 'a75' if a <= 75 else 'a95'
    nb = ('dn10' if n <= -10 else 'dn3' if n <= -3 else
          'flat' if n < 3 else 'up3' if n < 10 else 'up10')
    return ab + '|' + nb + '|' + ('d0' if d <= 2 else 'd3' if d <= 9 else 'd10')

def call(cat, a, n, d):
    cell = (RECOG.get(cat + '|h6') or {}).get(pbk(a, n, d))
    if cell and cell.get('purity', 0) >= 0.5:
        return cell['top']
    return dband(cat, a)

def reach_ok(band, d):
    rc = (SURF.get(band) or {}).get('reach') or {}
    n = (SURF.get(band) or {}).get('n', 0)
    p = float(rc.get(str(d), 0) or 0)
    return d <= 1 or p * n >= 8

G = []
for line in open(ROOT / 'state/range_spectrum_v1.jsonl'):
    r = json.loads(line)
    legs = {k: v for k, v in r['legs'].items() if v.get('shape')}
    if len(legs) != 2:
        continue
    t8 = r['sched'] - 8 * 3600
    RE = r['right_edge']
    cut = t8 + 2 * 3600
    day = r['event'].split('-')[1][:7]
    gl = []
    for leg, v in legs.items():
        tk = [(ts, lc) for ts, b, a, lc in (v.get('ticks') or []) if lc]
        p1 = [(ts, lc) for ts, lc in tk if ts <= cut]
        gl.append({'anchor': v['anchor'], 'close': v['close'], 'ticks': tk,
                   'net_h': (p1[-1][1] - p1[0][1]) if p1 else 0,
                   'dip_h': (v['anchor'] - min(x[1] for x in p1)) if p1 else 0})
    G.append({'cat': r['cat'], 'legs': gl, 't8': t8, 're': RE, 'cut': cut,
              'day': day, 'hold': day >= '26JUL14' and day.startswith('26JUL'),
              'viable': all(len(x['ticks']) >= 3 for x in gl)})
print('games:', len(G), 'viable:', sum(1 for g in G if g['viable']), flush=True)

POL = {}
for band, s in SURF.items():
    m = meta(band)
    if not m or s['n'] < 30:
        continue
    rc = s.get('reach') or {}
    def deep(q):
        best = 1
        for d in range(1, 31):
            if float(rc.get(str(d), 0) or 0) >= q:
                best = d
        return best
    if m['direction'] == 'riser':
        POL[band] = [1, 1, 0]
    else:
        POL[band] = [deep(0.25), deep(0.5), 1]

def lvl_at(band, pol, anchor, frac):
    d = pol[0] if frac < 0.4 else pol[1] if frac < 0.8 else pol[2]
    while d > 0 and not reach_ok(band, d):
        d -= 1
    return anchor - d

def sim_leg(g, x):
    b1 = dband(g['cat'], x['anchor'])
    b2 = call(g['cat'], x['anchor'], x['net_h'], x['dip_h']) or b1
    span = max(g['re'] - g['t8'], 1.0)
    for ts, lc in x['ticks']:
        frac = (ts - g['t8']) / span
        band = b1 if ts <= g['cut'] else b2
        if band not in POL:
            return None
        lv = lvl_at(band, POL[band], x['anchor'], frac)
        if lv >= 5 and lc <= lv:
            return (band, lv, lv - x['close'])
    return (b2 if b2 in POL else b1, None, None)

def replay(cohort):
    viable = duals = both_neg = refus = 0
    legd = defaultdict(list)
    pair = []
    for g in cohort:
        if not g['viable']:
            refus += 1
            continue
        viable += 1
        f = [sim_leg(g, x) for x in g['legs']]
        if any(r is None for r in f):
            continue
        if all(r[1] is not None for r in f):
            duals += 1
            if all(r[2] < 0 for r in f):
                both_neg += 1
            pair.append(sum(r[2] for r in f))
            for r in f:
                legd[r[0]].append(r[2])
    return viable, refus, duals, both_neg, pair, legd

def score(cohort):
    v, rf, du, bn, pr, _ = replay(cohort)
    return (bn / du if du else 0) * (du / v if v else 0)

train = [g for g in G if not g['hold']]
hold = [g for g in G if g['hold']]
L = ['# LOOP 6 - THE DYNAMIC FRONTIER (policies; 75% both-negative bar)', '']
for it in range(1, 9):
    v, rf, du, bn, pr, _ = replay(train)
    vh, rfh, duh, bnh, prh, legdh = replay(hold)
    L.append('- iter %d: TRAIN viable %d dual %.3f bothneg %.2f | HOLDOUT '
             'viable %d refus %d dual %.3f bothneg %s medPair %s'
             % (it, v, du / max(v, 1), bn / max(du, 1), vh, rfh,
                duh / max(vh, 1), round(bnh / max(duh, 1), 2),
                sorted(prh)[len(prh) // 2] if prh else None))
    acc = []
    base = score(train)
    for band in sorted(POL):
        for slot in (0, 1, 2):
            b0 = POL[band][slot]
            best = (b0, base)
            for st in (-2, -1, 1, 2):
                nd = b0 + st
                if nd < 0 or nd > 30:
                    continue
                POL[band][slot] = nd
                s = score(train)
                if s > best[1]:
                    best = (nd, s)
                POL[band][slot] = b0
            if best[0] != b0:
                POL[band][slot] = best[0]
                base = best[1]
                acc.append('%s[%d]%d>%d' % (band, slot, b0, best[0]))
    if acc:
        L.append('    adj: ' + ' '.join(acc[:10]))
    else:
        L.append('- STOP: CONVERGED.')
        break
vh, rfh, duh, bnh, prh, legdh = replay(hold)
bar = bnh / max(duh, 1)
L.append('')
L.append('## HOLDOUT: viable %d - refusals %d - dual %.3f - duals n=%d - '
         'BOTH-NEG %.1f%% vs BAR 75%% -> **%s** - med pair %s'
         % (vh, rfh, duh / max(vh, 1), duh, 100 * bar,
            'CLEARS' if bar >= 0.75 else 'BELOW',
            sorted(prh)[len(prh) // 2] if prh else None))
for band, ds in sorted(legdh.items()):
    d2 = sorted(ds)
    L.append('- %s: legs %d - delta med %+d p25 %+d p75 %+d - neg%% %.0f'
             % (band, len(ds), d2[len(d2) // 2], d2[len(d2) // 4],
                d2[3 * len(d2) // 4],
                100 * sum(1 for x in ds if x < 0) / len(ds)))
(ROOT / 'state/policy_tables_v1.json').write_text(json.dumps(
    {'policies': POL, 'holdout': {'viable': vh, 'dual': duh,
                                  'both_neg_pct': round(100 * bar, 1)}}))
Path('/tmp/LOOP6_CAMPAIGN.md').write_text(chr(10).join(L) + chr(10))
print('LOOP6-DONE bothneg %.1f%% dual %d viable %d'
      % (100 * bar, duh, vh))
