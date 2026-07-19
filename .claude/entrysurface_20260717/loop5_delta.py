#!/usr/bin/env python3
# LOOP 5 (AMENDMENT v2) - THE DELTA IS THE SCORE. Pair-level own-frame
# replay: per game, both legs; fill = any W1 print <= level (two-phase:
# conception park at anchor-default band, T-6h recognition re-call).
# Metrics (the operator's, nothing else): dual-fill rate / per-leg delta
# (fill - W1 close) / combined pair delta. HOLDOUT-PASS = dual positions
# at negative combined delta, repeatably, on unseen days (n>=10 duals,
# median pair delta < 0). P1 fold-in: flat depths capped at own dip_p90.
# No settlement, no exits, anywhere.
import json
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / 'state/band_map_v1.json').read_text())
TAB = json.loads((ROOT / 'state/entry_tables_v1.json').read_text())['tables']
DIVOT = json.loads((ROOT / 'state/divot_tables_v1.json').read_text())
RECOG = json.loads((ROOT / 'state/drift_surfaces_v1.json').read_text()).get('recognition', {})
def dband(cat, a):
    c = BMAP['cats'].get(cat)
    if not c or c.get('thin'): return None
    fl = [b for b in c['bands'] if b['direction'] == 'flat'] or c['bands']
    return min(fl, key=lambda b: abs(b['anchor_med'] - a))['band']
def pb(a, n, d):
    ab = 'a25' if a<=25 else 'a50' if a<=50 else 'a75' if a<=75 else 'a95'
    nb = 'dn10' if n<=-10 else 'dn3' if n<=-3 else 'flat' if n<3 else 'up3' if n<10 else 'up10'
    return ab+'|'+nb+'|'+('d0' if d<=2 else 'd3' if d<=9 else 'd10')
def call(cat, a, n, d):
    cell = (RECOG.get(cat+'|h6') or {}).get(pb(a, n, d))
    if cell and cell.get('purity', 0) >= 0.5: return cell['top']
    return dband(cat, a)
G = []
for line in open(ROOT / 'state/range_spectrum_v1.jsonl'):
    r = json.loads(line)
    legs = {k: v for k, v in r['legs'].items() if v.get('shape')}
    if len(legs) != 2: continue
    t8 = r['sched'] - 8*3600; cut = t8 + 2*3600
    day = r['event'].split('-')[1][:7]
    gl = []
    for leg, v in legs.items():
        tk = [(ts, lc) for ts, b, a, lc in (v.get('ticks') or []) if lc]
        p1 = [(ts, lc) for ts, lc in tk if ts <= cut]
        gl.append({'anchor': v['anchor'], 'close': v['close'],
                   'lows': (min(x[1] for x in tk) if tk else None),
                   'net_h': (p1[-1][1]-p1[0][1]) if p1 else 0,
                   'dip_h': (v['anchor']-min(x[1] for x in p1)) if p1 else 0})
    G.append({'cat': r['cat'], 'legs': gl, 'day': day,
              'hold': day >= '26JUL14' and day.startswith('26JUL')})
print('games:', len(G), flush=True)
CAP = {}
for band, row in TAB.items():
    dv = (DIVOT.get('bands') or {}).get(band) or {}
    if row.get('kind') == 'flat' and dv.get('depth_p90'):
        CAP[band] = int(dv['depth_p90'])
def replay(depths, cohort):
    duals = 0; pdl = []; per = defaultdict(lambda: [0, 0, []])
    for g in cohort:
        fl = []
        for x in g['legs']:
            band = call(g['cat'], x['anchor'], x['net_h'], x['dip_h'])
            if not band or band not in depths: fl.append(None); continue
            lvl = x['anchor'] - depths[band]
            if lvl < 5 or x['lows'] is None or x['lows'] > lvl:
                fl.append(None); continue
            fl.append((band, lvl, lvl - x['close']))
        if all(f is not None for f in fl):
            duals += 1
            pd = sum(f[2] for f in fl)
            pdl.append(pd)
            for f in fl:
                per[f[0]][0] += 1; per[f[0]][2].append(f[2])
    med = sorted(pdl)[len(pdl)//2] if pdl else None
    neg = (sum(1 for x in pdl if x < 0)/len(pdl)) if pdl else 0
    return duals/max(len(cohort),1), med, neg, len(pdl), per
train = [g for g in G if not g['hold']]; hold = [g for g in G if g['hold']]
depths = {}
for b, r in TAB.items():
    if r.get('thin') or r.get('depth') is None: continue
    if r['kind'] == 'faller' and (r.get('roc') or 0) <= 0: continue
    depths[b] = min(r['depth'], CAP.get(b, 99))
L = ['# LOOP 5 - THE DELTA (dual-fill / per-leg / pair; no exits anywhere)', '']
for it in range(1, 11):
    dr, med, neg, nd, _ = replay(depths, train)
    dh, medh, negh, ndh, perh = replay(depths, hold)
    L.append('- iter %d: TRAIN dual %.3f medPairD %s negShare %.2f (n=%d) | HOLDOUT dual %.3f medPairD %s negShare %.2f (n=%d)' % (it, dr, med, neg, nd, dh, medh, negh, ndh))
    acc = []
    base = neg * dr
    for band in sorted(depths):
        bd, bs = depths[band], base
        for st in (-3, -2, -1, 1, 2, 3):
            ndp = depths[band] + st
            if ndp < 1 or ndp > 30 or (band in CAP and ndp > CAP[band]): continue
            c2 = dict(depths); c2[band] = ndp
            d2, m2, n2, _, _ = replay(c2, train)
            s = n2 * d2
            if s > bs: bs, bd = s, ndp
        if bd != depths[band]:
            acc.append((band, depths[band], bd)); depths[band] = bd; base = bs
    if acc: L.append('    adjusted: ' + ' - '.join('%s %d->%d' % a for a in acc[:8]))
    else: L.append('- STOP: CONVERGED.'); break
dh, medh, negh, ndh, perh = replay(depths, hold)
L.append('')
L.append('## HOLDOUT VERDICT: dual-rate %.3f - median pair delta %s - negative-delta share %.2f - duals n=%d' % (dh, medh, negh, ndh))
L.append('PASS = duals>=10 AND median pair delta < 0: **%s**' % ('HOLDOUT-PASS' if (ndh >= 10 and medh is not None and medh < 0) else 'FAIL/THIN'))
for band, (n, _, ds) in sorted(perh.items()):
    if ds:
        d2 = sorted(ds)
        L.append('- %s: legs %d - leg-delta med %+d p25 %+d p75 %+d' % (band, n, d2[len(d2)//2], d2[len(d2)//4], d2[3*len(d2)//4]))
(ROOT / 'state/delta_tables_v1.json').write_text(json.dumps({'depths': depths, 'holdout': {'dual': dh, 'med_pair_delta': medh, 'neg_share': negh, 'n': ndh}}))
Path('/tmp/LOOP5_CAMPAIGN.md').write_text(chr(10).join(L) + chr(10))
print('LOOP5-DONE', 'dual', round(dh, 3), 'medD', medh, 'n', ndh)
