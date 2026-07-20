#!/usr/bin/env python3
# LOOP 7 — THE DESTINATION FRAME (operator's correction). Aims price
# against the PROJECTED W1 CLOSE (band net-travel quantiles, conditioned
# on the recognition call, re-projected at re-calls) — not the anchor.
# Risers park at touch from birth · flats fish divots below anchor
# (dip_p90-capped) · fallers bid below the projected terminal (net
# quantile sets the level; violent-faller REFUSE stands). Pair-aware;
# dead bands refused; realism = the band's own reach support at the
# implied depth. Metric: >=75% duals both-legs-below-their-own-closes +
# combined tiers. Holdout law; stop by evidence.
import json
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / 'state/band_map_v1.json').read_text())
DRIFT = json.loads((ROOT / 'state/drift_surfaces_v1.json').read_text())
DIVOT = json.loads((ROOT / 'state/divot_tables_v1.json').read_text())
RECOG = DRIFT.get('recognition', {})
SURF = DRIFT['bands']

def mmeta(band):
    for b in BMAP['cats'][band.split('-')[0]]['bands']:
        if b['band'] == band:
            return b

def dband(cat, a):
    c = BMAP['cats'].get(cat)
    if not c or c.get('thin'):
        return None
    fl = [b for b in c['bands'] if b['direction'] == 'flat'] or c['bands']
    return min(fl, key=lambda b: abs(b['anchor_med'] - a))['band']

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

# net-travel quantiles per band (one pass), + games
NETS = defaultdict(list)
G = []
for line in open(ROOT / 'state/range_spectrum_v1.jsonl'):
    r = json.loads(line)
    legs = {k: v for k, v in r['legs'].items() if v.get('shape')}
    if len(legs) != 2:
        continue
    t8 = r['sched'] - 8 * 3600
    cut = t8 + 2 * 3600
    day = r['event'].split('-')[1][:7]
    gl = []
    for leg, v in legs.items():
        tk = [(ts, lc) for ts, b, a, lc in (v.get('ticks') or []) if lc]
        p1 = [(ts, lc) for ts, lc in tk if ts <= cut]
        gl.append({'anchor': v['anchor'], 'close': v['close'], 'ticks': tk,
                   'net_h': (p1[-1][1] - p1[0][1]) if p1 else 0,
                   'dip_h': (v['anchor'] - min(x[1] for x in p1)) if p1 else 0})
        # band for NETS: hindsight assign (population stat, fit-era only)
        if not (day >= '26JUL14' and day.startswith('26JUL')):
            c = BMAP['cats'].get(r['cat'])
            if c and not c.get('thin'):
                mus, sds = c['feature_mus'], c['feature_sds']
                z = tuple((x - m) / s for x, m, s in zip(
                    (v['anchor'], v['net'], v['anchor'] - v['low']), mus, sds))
                j = min(range(len(c['centroids_z'])), key=lambda i: sum(
                    (a - b) ** 2 for a, b in zip(z, c['centroids_z'][i])))
                am = c['centroids_z'][j][0] * sds[0] + mus[0]
                bb = min(c['bands'], key=lambda b: abs(b['anchor_med'] - am))
                NETS[bb['band']].append(v['net'])
    G.append({'cat': r['cat'], 'legs': gl, 'cut': cut, 'day': day,
              'hold': day >= '26JUL14' and day.startswith('26JUL'),
              'viable': all(len(x['ticks']) >= 3 for x in gl)})
NQ = {}
for band, v in NETS.items():
    v.sort()
    NQ[band] = [v[int(q * len(v))] for q in (0.10, 0.25, 0.40)]
print('games:', len(G), 'bands w/ net-q:', len(NQ), flush=True)

def reach_ok(band, d):
    rc = (SURF.get(band) or {}).get('reach') or {}
    n = (SURF.get(band) or {}).get('n', 0)
    return d <= 1 or float(rc.get(str(d), 0) or 0) * n >= 8

CAPF = {}
for band, row in DIVOT.get('bands', {}).items():
    if row.get('depth_p90'):
        CAPF[band] = int(row['depth_p90'])

# policy knob per band: fallers -> net-quantile index 0/1/2; flats ->
# divot depth 1..cap; risers -> 0/1 below touch. REFUSE: violent fallers.
POL = {}
for band, s in SURF.items():
    m = mmeta(band)
    if not m or s['n'] < 30:
        continue
    if m['direction'] == 'riser':
        POL[band] = ('riser', 0)
    elif m['direction'] == 'flat':
        POL[band] = ('flat', min(3, CAPF.get(band, 3)))
    else:
        if m['net_med'] <= -30:
            POL[band] = ('refuse', None)     # the violent-faller law
        else:
            POL[band] = ('faller', 1)        # start at q25

def level_for(band, anchor):
    kind, k = POL[band]
    if kind == 'refuse':
        return None
    if kind == 'riser':
        lv = anchor - k
    elif kind == 'flat':
        lv = anchor - k
    else:
        nq = NQ.get(band)
        if not nq:
            return None
        lv = anchor + nq[k]                  # below the projected terminal
    d = anchor - lv
    if d > 0 and not reach_ok(band, min(d, 30)):
        return None
    return lv if lv >= 5 else None

def sim_leg(g, x):
    b1 = dband(g['cat'], x['anchor'])
    b2 = call(g['cat'], x['anchor'], x['net_h'], x['dip_h']) or b1
    for ts, lc in x['ticks']:
        band = b1 if ts <= g['cut'] else b2
        if band not in POL:
            return None
        lv = level_for(band, x['anchor'])
        if lv is not None and lc <= lv:
            return (band, lv, lv - x['close'])
    return (b2 if b2 in POL else b1, None, None)

def replay(cohort):
    viable = duals = bothneg = 0
    tiers = {'le93': 0, 'le95': 0, 'le97': 0, 'gt97': 0}
    legd = defaultdict(list)
    for g in cohort:
        if not g['viable']:
            continue
        viable += 1
        f = [sim_leg(g, x) for x in g['legs']]
        if any(r is None for r in f):
            continue
        if all(r[1] is not None for r in f):
            duals += 1
            comb = sum(r[1] for r in f)
            tiers['le93' if comb <= 93 else 'le95' if comb <= 95 else
                  'le97' if comb <= 97 else 'gt97'] += 1
            if all(r[2] < 0 for r in f):
                bothneg += 1
            for r in f:
                legd[r[0]].append(r[2])
    return viable, duals, bothneg, tiers, legd

def score(cohort):
    v, du, bn, t, _ = replay(cohort)
    return (bn / du if du else 0) * min(1.0, du / max(0.15 * v, 1))

train = [g for g in G if not g['hold']]
hold = [g for g in G if g['hold']]
L = ['# LOOP 7 — THE DESTINATION FRAME (aims vs projected close)', '']
for it in range(1, 8):
    v, du, bn, t, _ = replay(train)
    vh, duh, bnh, th, legdh = replay(hold)
    L.append('- iter %d: TRAIN viable %d dual %.3f bothneg %s | HOLDOUT '
             'viable %d dual %.3f bothneg %s gt97 %s'
             % (it, v, du / max(v, 1), round(bn / max(du, 1), 2), vh,
                duh / max(vh, 1), round(bnh / max(duh, 1), 2),
                round(th['gt97'] / max(duh, 1), 2)))
    acc = []
    base = score(train)
    for band in sorted(POL):
        kind, k = POL[band]
        if kind == 'refuse':
            continue
        cands = ([0, 1] if kind == 'riser' else
                 range(1, CAPF.get(band, 4) + 1) if kind == 'flat' else
                 [0, 1, 2])
        best = (k, base)
        for nk in cands:
            if nk == k:
                continue
            POL[band] = (kind, nk)
            s = score(train)
            if s > best[1]:
                best = (nk, s)
            POL[band] = (kind, k)
        if best[0] != k:
            POL[band] = (kind, best[0])
            base = best[1]
            acc.append('%s %s>%s' % (band, k, best[0]))
    if acc:
        L.append('    adj: ' + ' '.join(acc[:10]))
    else:
        L.append('- STOP: CONVERGED.')
        break
vh, duh, bnh, th, legdh = replay(hold)
bar = bnh / max(duh, 1)
L.append('')
L.append('## HOLDOUT: viable %d · duals %d (%.3f) · BOTH-NEG %.1f%% vs 75%% '
         '-> **%s** · tiers <=93 %.0f%% <=95 %.0f%% <=97 %.0f%% >97 %.0f%%'
         % (vh, duh, duh / max(vh, 1), 100 * bar,
            'CLEARS' if bar >= 0.75 else 'BELOW',
            *(100 * th[k] / max(duh, 1)
              for k in ('le93', 'le95', 'le97', 'gt97'))))
for band, ds in sorted(legdh.items()):
    d2 = sorted(ds)
    L.append('- %s %s: legs %d · delta med %+d · neg%% %.0f'
             % (band, POL.get(band), len(ds), d2[len(d2) // 2],
                100 * sum(1 for x in ds if x < 0) / len(ds)))
(ROOT / 'state/destination_tables_v1.json').write_text(json.dumps(
    {'policies': {k: list(v) for k, v in POL.items()}, 'net_q': NQ,
     'holdout': {'viable': vh, 'duals': duh,
                 'both_neg_pct': round(100 * bar, 1),
                 'tiers': th}}))
Path('/tmp/LOOP7_CAMPAIGN.md').write_text(chr(10).join(L) + chr(10))
print('LOOP7-DONE bothneg %.1f%% dual %d/%d gt97 %.1f%%'
      % (100 * bar, duh, vh, 100 * th['gt97'] / max(duh, 1)))
