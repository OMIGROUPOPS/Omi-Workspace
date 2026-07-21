#!/usr/bin/env python3
# THE CAPTURE STANDARD — BOOK/MID FRAME + THREE FRAME GUARDS
# (operator frame-defect ruling + guards, 07-20 late; absorbed BEFORE
# any verdict prints).
# THE LAW OF THIS FRAME:
#   ANCHORS = book MID from the 5-level REST tick series; never
#     trade-print medians.
#   WINDOWS (guard 1) run T-8h -> OFFICIAL START or the honest corridor
#     estimate — NEVER truncated at sched; the final-20-min + corridor
#     stretch is in every window; edge tier named per event
#     (official / corpus-right-edge / corridor-est(+30m declared)).
#   FILLS (guard 2) are SIZE-AWARE: a level fills only when cumulative
#     printed volume at/below it AFTER placement >= our lot (5).
#   THE ARM MENU (guard 3) includes the plain WALK-LAW PARK (rest at
#     touch at placement, both classes) as a first-class candidate
#     judged under par tiers beside the divot arms — the operator's
#     original mechanic, scored on the honest yardstick.
#   COMBINED = fillA + fillB vs 100; tiers <=93/<=95/<=97/<100.
# VALIDATION GATE mandatory and FIRST (size-aware): reproduce the
# machine's realized duals or be DISCARDED — no verdicts on FAIL.
# Ground = the book series' span (JUL 12 -> yesterday); whole market;
# violent REFUSE apart; joint number first; mirror law; two exits only.
import csv, glob, gzip, json, os, sqlite3, statistics, sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    os.nice(12)
except Exception:
    pass
ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo('America/New_York')
BMAP = json.loads((ROOT / 'state/band_map_v1.json').read_text())['cats']
RECOG = json.loads((ROOT / 'state/drift_surfaces_v1.json').read_text()
                   ).get('recognition', {})
DB = ROOT / 'state/subsecond_store.db'
TICKS = ROOT / 'analysis/premarket_ticks'
OUT = ROOT.parent / '.claude/capture_20260720'
BIG4 = {'KXATPMATCH': 'ATP_MAIN', 'KXWTAMATCH': 'WTA_MAIN',
        'KXATPCHALLENGERMATCH': 'ATP_CHALL',
        'KXWTACHALLENGERMATCH': 'WTA_CHALL'}
YEST = (datetime.now(ET) - timedelta(days=1)).replace(
    hour=23, minute=59, second=59).timestamp()
LOT = 5
CORRIDOR_EST = 1800          # declared corridor stretch when no official
con = sqlite3.connect('file:%s?mode=ro' % DB, uri=True, timeout=30)

def cat_of(ev):
    for p, c in BIG4.items():
        if ev.startswith(p + '-'):
            return c
    return None

def pb(a, n, d):
    ab = 'a25' if a <= 25 else 'a50' if a <= 50 else 'a75' if a <= 75 else 'a95'
    nb = ('dn10' if n <= -10 else 'dn3' if n <= -3 else 'flat' if n < 3
          else 'up3' if n < 10 else 'up10')
    return ab + '|' + nb + '|' + ('d0' if d <= 2 else 'd3' if d <= 9 else 'd10')

def band_call(cat, a, n, d):
    cell = (RECOG.get(cat + '|h6') or {}).get(pb(a, n, d))
    if cell and cell.get('purity', 0) >= 0.5:
        return cell['top']
    c = BMAP.get(cat)
    if not c or c.get('thin'):
        return None
    fl = [b for b in c['bands'] if b['direction'] == 'flat'] or c['bands']
    return min(fl, key=lambda b: abs(b['anchor_med'] - a))['band']

def right_edge(ev, sched, corpus, bells):
    """Guard 1: official start > corpus honest right edge > sched +
    declared corridor estimate. Returns (edge_ts, tier)."""
    r = corpus.get(ev)
    if r:
        if r.get('official_ts'):
            return float(r['official_ts']), 'official'
        if r.get('right_edge'):
            return float(r['right_edge']), 'corpus-edge(%s)' % (
                r.get('right_edge_src') or '?')
    b = bells.get(ev)
    if b:
        return float(b), 'official-bell'
    return sched + CORRIDOR_EST, 'corridor-est(+30m)'

def mid_series(tk, t0, t1):
    out = []
    bid1 = []
    for f in glob.glob(str(TICKS / (tk + '.csv*'))):
        op = gzip.open if f.endswith('.gz') else open
        with op(f, 'rt', encoding='utf-8', errors='replace') as fh:
            for r in csv.DictReader(fh):
                try:
                    ts = datetime.strptime(
                        r['ts_et'], '%Y-%m-%d %I:%M:%S %p'
                    ).replace(tzinfo=ET).timestamp()
                    if t0 <= ts <= t1 and r.get('mid'):
                        out.append((ts, float(r['mid'])))
                        bid1.append((ts, int(float(r.get('bid_1') or 0))))
                except Exception:
                    continue
    out.sort()
    bid1.sort()
    return out, bid1

def prints_sized(tk, t0, t1):
    rows = con.execute(
        'SELECT ts, price, size FROM prints WHERE ticker=? AND ts>=? '
        'AND ts<=? ORDER BY ts', (tk, t0, t1)).fetchall()
    merged = {}
    for t, p, sz in rows:
        if not p:
            continue
        k = (int(t // 60), int(p))
        if k not in merged:
            merged[k] = [t, int(p), 0.0]
        merged[k][2] += float(sz or 1)
    return sorted(merged.values())

def vol_at_or_below(pr, tp):
    """Guard 2: cum printed volume at/below each cent AFTER tp."""
    v = [0.0] * 101
    for t, p, sz in pr:
        if t >= tp and 0 < p <= 100:
            v[p] += sz
    for i in range(1, 101):
        v[i] += v[i - 1]
    return [round(x, 1) for x in v]

SUB = OUT / 'substrate_book.jsonl'

def build():
    corpus = {}
    try:
        for line in open(ROOT / 'state/corpus_events_v2.jsonl',
                         encoding='utf-8', errors='replace'):
            try:
                r = json.loads(line)
                corpus[r['event']] = r
            except Exception:
                continue
    except OSError:
        pass
    try:
        bells = json.loads((ROOT / 'state/daysheet_bells_official.json'
                            ).read_text())
    except Exception:
        bells = {}
    have = set()
    if SUB.exists():
        for line in open(SUB):
            try:
                have.add(json.loads(line)['event'])
            except Exception:
                pass
    evs = defaultdict(set)
    for f in os.listdir(TICKS):
        tk = f.split('.csv')[0]
        ev = tk.rsplit('-', 1)[0]
        if cat_of(ev):
            evs[ev].add(tk)
    sched = {}
    for path in sorted(glob.glob(str(ROOT / 'logs/live_v3_2026071*.jsonl*'))
                       ) + [str(ROOT / 'logs/live_v3_20260720.jsonl')]:
        op = gzip.open if path.endswith('.gz') else open
        try:
            fh = op(path, 'rt', encoding='utf-8', errors='replace')
        except OSError:
            continue
        for line in fh:
            if '"schedule_match"' not in line:
                continue
            try:
                j = json.loads(line)
                d = j['details']
                if d.get('event') in evs and d.get('start_time'):
                    sched[d['event']] = datetime.fromisoformat(
                        d['start_time']).timestamp()
            except Exception:
                continue
    sf = open(SUB, 'a')
    n9 = 0
    for ev, tks in sorted(evs.items()):
        if ev in have or len(tks) != 2 or ev not in sched:
            continue
        s = sched[ev]
        if s > YEST:
            continue
        edge, tier9 = right_edge(ev, s, corpus, bells)
        edge = max(edge, s)          # never earlier than sched
        t8 = s - 8 * 3600
        legs = {}
        ok = True
        for tk in sorted(tks):
            ms, bid1 = mid_series(tk, t8, edge)
            pr = prints_sized(tk, t8, edge)
            if len(ms) < 10 or len(pr) < 3:
                ok = False
                break
            anchor = ms[0][1]
            mids = [m for _, m in ms]
            dur = edge - t8
            frames = {'open': 0.0, 'f4h': max(0.0, dur - 14400),
                      'f2h': max(0.0, dur - 7200)}
            floor_t = min((p, t) for t, p, _ in pr)[1] - t8
            volL = {k: vol_at_or_below(pr, t8 + off)
                    for k, off in frames.items()}
            volL['floor'] = vol_at_or_below(pr, t8 + floor_t)
            park = {}
            for k, off in frames.items():
                b = next((b_ for ts_, b_ in bid1 if ts_ >= t8 + off),
                         None)
                park[k] = b
            legs[tk] = {'anchor': round(anchor, 1),
                        'close_print': pr[-1][1],
                        'path_up': any(m - anchor >= 5 for m in mids),
                        'path_dn': any(m - anchor <= -5 for m in mids),
                        'band': band_call(cat_of(ev), anchor,
                                          mids[-1] - anchor,
                                          max(0, anchor - min(mids))),
                        'floor_t': round(floor_t),
                        'volL': volL, 'park': park,
                        'reach_open': round(anchor - min(
                            p for _, p, _ in pr), 1),
                        'n_ticks': len(ms), 'n_prints': len(pr)}
        if not ok or len(legs) != 2:
            continue
        ups = [v['path_up'] for v in legs.values()]
        dns = [v['path_dn'] for v in legs.values()]
        kl = ('flat_flat' if not (any(ups) or any(dns)) else
              'mirror' if (any(ups) and any(dns)) else 'neither')
        sf.write(json.dumps({'event': ev, 'cat': cat_of(ev), 'sched': s,
                             'edge_tier': tier9,
                             'day': datetime.fromtimestamp(
                                 s, ET).strftime('%Y%m%d'),
                             'path_class': kl, 'legs': legs}) + '\n')
        n9 += 1
        if n9 % 100 == 0:
            sf.flush()
            print('book substrate +%d' % n9, flush=True)
    sf.close()
    print('book substrate done: +%d' % n9, flush=True)

def load():
    G = []
    for line in open(SUB):
        try:
            G.append(json.loads(line))
        except Exception:
            continue
    return G

def filled(v, level, frame):
    if level is None or level < 1:
        return False
    lv = min(100, max(1, int(level)))
    return v['volL'][frame][lv] >= LOT

# ---- THE VALIDATION GATE (size-aware, mandatory, first) ----------------
def gate():
    fills_real = defaultdict(dict)
    placed = defaultdict(dict)
    for path in sorted(glob.glob(str(ROOT / 'logs/live_v3_2026071*.jsonl*'))
                       ) + [str(ROOT / 'logs/live_v3_20260720.jsonl')]:
        op = gzip.open if path.endswith('.gz') else open
        try:
            fh = op(path, 'rt', encoding='utf-8', errors='replace')
        except OSError:
            continue
        for line in fh:
            if '"entry_filled"' in line:
                try:
                    j = json.loads(line)
                    fills_real[j['ticker'].rsplit('-', 1)[0]][
                        j['ticker']] = int(j['details']['fill_price'])
                except Exception:
                    continue
            elif '"order_placed"' in line and '"buy"' in line:
                try:
                    j = json.loads(line)
                    d = j['details']
                    placed[j['ticker']][int(d['price'])] = j['ts_epoch']
                except Exception:
                    continue
    ok = n = 0
    misses = []
    for ev, legs in fills_real.items():
        if len(legs) != 2 or not cat_of(ev):
            continue
        good = True
        cover = True
        for tk, lvl in legs.items():
            tp = placed.get(tk, {}).get(lvl)
            if tp is None:
                cover = False
                break
            pr = prints_sized(tk, tp, tp + 12 * 3600)
            vol = sum(sz for t, p, sz in pr if p <= lvl)
            if vol < LOT:
                good = False
        if not cover:
            continue
        n += 1
        if good:
            ok += 1
        else:
            misses.append(ev)
    pct = 100 * ok / max(1, n)
    verdict = pct >= 90
    L = ['## THE VALIDATION GATE (size-aware, lot=%d): reproduced '
         '%d/%d realized big-4 duals = %.0f%% -> **%s**'
         % (LOT, ok, n, pct,
            'GATE PASS' if verdict else
            'GATE FAIL — simulator DISCARDED, no verdicts print')]
    if misses:
        L.append('- missed: %s' % ', '.join(misses[:6]))
    print('\n'.join(L), flush=True)
    (OUT / 'VALIDATION_GATE.md').write_text('\n'.join(L) + '\n')
    return verdict

# ---- arms ---------------------------------------------------------------
def leg_arm(g, v):
    if v['path_dn'] and not v['path_up']:
        nm = next((b.get('net_med', 0)
                   for b in (BMAP.get(g['cat']) or {}).get('bands', [])
                   if b['band'] == v['band']), 0)
        if nm <= -30:
            return 'faller', True
        return 'decel_cast', False
    if v['path_up'] and not v['path_dn']:
        return 'riser_divot', False
    if v['path_up'] and v['path_dn']:
        return 'decel_cast', False
    return 'flat_divot', False

def tier(c):
    return '<=93' if c <= 93 else '<=95' if c <= 95 else '<=97' \
        if c <= 97 else '<100' if c < 100 else '>=100'

def run(pool, QD, pol, qf, qr, qd, frame):
    comp = du = n = ref = mast = 0
    tiers = defaultdict(int)
    for g in pool:
        rows = []
        skip = refuse = False
        for v in g['legs'].values():
            arm, rf = leg_arm(g, v)
            if rf:
                refuse = True
                break
            if pol == 'park':
                lvl = v['park'].get(frame)
                fkey = frame
            else:
                qt = QD.get(v['band'])
                if not qt:
                    skip = True
                    break
                q = qf if arm == 'flat_divot' else \
                    qr if arm == 'riser_divot' else qd
                lvl = int(round(v['anchor'] - qt[q]))
                fkey = 'floor' if arm == 'decel_cast' else frame
            if lvl is None:
                skip = True
                break
            rows.append((v, lvl, fkey))
        if refuse:
            ref += 1
            continue
        if skip:
            continue
        n += 1
        f9 = [(v, lvl if filled(v, lvl, fk) else None)
              for v, lvl, fk in rows]
        if all(px is not None for _, px in f9):
            du += 1
            cmb = sum(px for _, px in f9)
            tiers[tier(cmb)] += 1
            if cmb < 100:
                comp += 1
                if all(px < v['close_print'] for v, px in f9):
                    mast += 1
    return n, du, comp, ref, mast, dict(tiers)

def census_and_drill():
    G = load()
    days = sorted({g['day'] for g in G})
    cutd = days[len(days) // 2]
    fit_g = [g for g in G if g['day'] < cutd]
    judge_g = [g for g in G if g['day'] >= cutd]
    arr = defaultdict(list)
    for g in fit_g:
        for v in g['legs'].values():
            arr[v['band']].append(v['reach_open'])
    QD = {}
    for band, ds in arr.items():
        if len(ds) < 20:
            continue
        ds = sorted(ds)
        QD[band] = {q: max(1, ds[max(0, min(len(ds) - 1,
                                            int((1 - q / 100)
                                                * len(ds))))])
                    for q in (50, 60, 70, 80, 90)}
    tiers9 = defaultdict(int)
    for g in G:
        tiers9[g['edge_tier'].split('(')[0]] += 1
    L = ['# CAPTURE STANDARD — BOOK/MID FRAME, THREE GUARDS IN '
         '(size-aware lot=%d; windows to official/corridor edge; the '
         'walk-law PARK on the menu). Ground %s->%s. Whole market. '
         'Generated %s ET.' % (LOT, days[0], days[-1],
                               datetime.now(ET).strftime(
                                   '%m-%d %I:%M %p')),
         'games %d (fit %d < %s <= judge %d) · class mix %s · window '
         'edge tiers %s · arrival tables (reach-below-mid-anchor, fit '
         'days) bands %d'
         % (len(G), len(fit_g), cutd, len(judge_g),
            {k: sum(1 for g in G if g['path_class'] == k)
             for k in ('flat_flat', 'mirror', 'neither')},
            dict(tiers9), len(QD)), '']
    best = None
    # THE PARK (guard 3): the operator's original mechanic, first-class
    for fr in ('open', 'f4h', 'f2h'):
        n, du, comp, ref, mast, t9 = run(fit_g, QD, 'park',
                                         0, 0, 0, fr)
        cr = 100 * comp / max(1, n)
        sr = 100 * comp / max(1, du)
        L.append('- FIT PARK/%s: **%.0f%% x %.0f%%** (subpar %d / '
                 'games %d · duals %d · mastery %.0f%% · tiers %s)'
                 % (fr, cr, sr, comp, n, du,
                    100 * mast / max(1, du), t9))
        if best is None or cr > best[0]:
            best = (cr, 'park', 0, 0, 0, fr)
    for qf in (50, 60, 70, 80, 90):
        for qr in (50, 70, 90):
            for qd in (50, 70, 90):
                for fr in ('open', 'f4h', 'f2h'):
                    n, du, comp, ref, mast, t9 = run(
                        fit_g, QD, 'divot', qf, qr, qd, fr)
                    cr = 100 * comp / max(1, n)
                    sr = 100 * comp / max(1, du)
                    if cr >= 55:
                        L.append('- FIT f%d/r%d/d%d/%s: **%.0f%% x '
                                 '%.0f%%** (subpar %d / games %d · '
                                 'duals %d · mastery %.0f%% · tiers %s)'
                                 % (qf, qr, qd, fr, cr, sr, comp, n,
                                    du, 100 * mast / max(1, du), t9))
                    if best is None or cr > best[0]:
                        best = (cr, 'divot', qf, qr, qd, fr)
    _, pol, qf, qr, qd, fr = best
    n, du, comp, ref, mast, t9 = run(judge_g, QD, pol, qf, qr, qd, fr)
    cr = 100 * comp / max(1, n)
    sr = 100 * comp / max(1, du)
    L.append('')
    L.append('## HOLDOUT (unseen) %s f%d/r%d/d%d/%s: **%.0f%% x '
             '%.0f%%** (subpar %d / games %d · duals %d · refused %d '
             'apart · mastery %.0f%% · tiers %s) -> %s'
             % (pol, qf, qr, qd, fr, cr, sr, comp, n, du, ref,
                100 * mast / max(1, du), t9,
                'EXIT (a): JOINT BAR MET — re-seal by ceremony'
                if cr >= 70 and sr >= 70 else
                'below bar — the ceiling decides'))
    # CEILING: size-aware deepest reach per class
    L.append('')
    L.append('## THE CEILINGS (size-aware deepest capture, judge pool):')
    days_j = max(1, len({g['day'] for g in judge_g}))
    tot_a = tot_n = 0
    for kl in ('flat_flat', 'mirror', 'neither'):
        pool = [g for g in judge_g if g['path_class'] == kl]
        avail = cn = rf9 = 0
        for g in pool:
            deep = []
            refuse = False
            for v in g['legs'].values():
                arm, rf = leg_arm(g, v)
                if rf:
                    refuse = True
                    break
                fk = 'floor' if arm == 'decel_cast' else 'open'
                vv = v['volL'][fk]
                lo = next((i for i in range(1, 101)
                           if vv[i] >= LOT), None)
                deep.append(lo)
            if refuse:
                rf9 += 1
                continue
            cn += 1
            if all(x is not None for x in deep) and sum(deep) < 100:
                avail += 1
        tot_a += avail
        tot_n += cn
        L.append('- %s: ceiling %.0f%% (%d/%d; refused %d) · '
                 'games/day %.1f'
                 % (kl, 100 * avail / max(1, cn), avail, cn, rf9,
                    avail / days_j))
    tv = 100 * tot_a / max(1, tot_n)
    L.append('## THE SUM vs 70: **%.0f%%** (%d/%d; %.1f games/day). %s'
             % (tv, tot_a, tot_n, tot_a / days_j,
                'Completion >= 70 PHYSICALLY AVAILABLE — iterate.'
                if tv >= 70 else
                '**EXIT (b) EVIDENCE: gap %.0fpp / %.1f games/day = '
                'the widening work.**'
                % (70 - tv, (0.7 * tot_n - tot_a) / days_j)))
    # MIRROR LAW
    mp = [g for g in judge_g if g['path_class'] == 'mirror']
    clean = unclean = linked = 0
    prow = []
    xs, ys = [], []
    for g in mp:
        legs = list(g['legs'].items())
        upl = [(t, v) for t, v in legs
               if v['path_up'] and not v['path_dn']]
        dnl = [(t, v) for t, v in legs
               if v['path_dn'] and not v['path_up']]
        if len(upl) != 1 or len(dnl) != 1:
            unclean += 1
            continue
        clean += 1
        (rtk, rv), (ftk, fv) = upl[0], dnl[0]
        if pol == 'park':
            rl, fl = rv['park'].get(fr), fv['park'].get(fr)
            rfill = rl if filled(rv, rl, fr) else None
            ffill = fl if filled(fv, fl, fr) else None
        else:
            rqt, fqt = QD.get(rv['band']), QD.get(fv['band'])
            rl = int(round(rv['anchor'] - rqt[qr])) if rqt else None
            fl = int(round(fv['anchor'] - fqt[qd])) if fqt else None
            rfill = rl if (rl and filled(rv, rl, fr)) else None
            ffill = fl if (fl and filled(fv, fl, 'floor')) else None
        if rfill is not None and ffill is not None:
            linked += 1
        prow.append({'event': g['event'],
                     'riser': {'leg': rtk.rsplit('-', 1)[1],
                               'fill': rfill},
                     'fader': {'leg': ftk.rsplit('-', 1)[1],
                               'floor_t_min': round(fv['floor_t'] / 60),
                               'cast_fill': ffill,
                               'miss': None if ffill is not None
                               else 'size-aware-reach-short'},
                     'pair_combined': (rfill + ffill)
                     if (rfill is not None and ffill is not None)
                     else None})
        xs.append(rv['floor_t'])
        ys.append(fv['floor_t'])
    corr = None
    if len(xs) >= 8:
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        den = (sum((a - mx) ** 2 for a in xs)
               * sum((b - my) ** 2 for b in ys)) ** 0.5
        corr = (sum((a - mx) * (b - my)
                    for a, b in zip(xs, ys)) / den if den else None)
    L.append('')
    L.append('## MIRROR LAW: games %d · clean %d (unclean %d apart) · '
             '**LINK-RATE %d/%d = %.0f%%** · inverse receipt r=%s n=%d'
             % (len(mp), clean, unclean, linked, max(1, clean),
                100 * linked / max(1, clean),
                ('%.2f' % corr) if corr is not None else 'insuff-n',
                len(xs)))
    for r in prow[:5]:
        L.append('- %s' % json.dumps(r))
    (OUT / 'mirror_pairs_book.jsonl').write_text(
        '\n'.join(json.dumps(r) for r in prow) + '\n')
    out = '\n'.join(L) + '\n'
    (OUT / 'CAPTURE_BOOKFRAME.md').write_text(out)
    print(out)

if __name__ == '__main__':
    if '--build' in sys.argv or not SUB.exists():
        build()
    if not gate():
        sys.exit(1)
    census_and_drill()
