#!/usr/bin/env python3
# THE CAPTURE STANDARD — BOOK/MID FRAME (operator frame-defect ruling,
# 07-20 late). The prior census/drill priced a strategy we don't trade
# (print-median walking fish) and is preserved FRAME-DEFECTIVE. The law:
#   ANCHORS  = book MID from the book series (REST 5-level snapshots,
#              analysis/premarket_ticks), never trade-print medians.
#   DIVOT    = the bid-reachable excursion: price TRADING down to X
#              below mid.
#   FILL     = a resting maker bid at OUR level L: any print at/below L
#              after placement fills us AT L (maker; the validation gate
#              adjudicates at-level vs strictly-below against reality).
#   COMBINED = fillA + fillB vs 100 (par); tiers <=93/<=95/<=97/<100.
# VALIDATION GATE (mandatory, prints first, verdicts refuse to print on
# FAIL): the simulator must reproduce the machine's own realized duals —
# same games, same levels, fills where reality filled. A simulator that
# cannot reproduce known reality is DISCARDED, not argued with.
# Ground: JUL 12 -> yesterday (the book series' own span = the honest
# frame's reach; pre-JUL-12 has no book series -> excluded by
# construction, named). Whole market, every class, violent REFUSE apart.
# Exits: only the operator's two. Joint number first. Mirror law rides.
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

def mid_series(tk, t8, sched):
    """Book mids from the tick file (REST 5-level snapshots)."""
    out = []
    for f in glob.glob(str(TICKS / (tk + '.csv*'))):
        op = gzip.open if f.endswith('.gz') else open
        with op(f, 'rt', encoding='utf-8', errors='replace') as fh:
            rd = csv.DictReader(fh)
            for r in rd:
                try:
                    ts = datetime.strptime(
                        r['ts_et'], '%Y-%m-%d %I:%M:%S %p'
                    ).replace(tzinfo=ET).timestamp()
                    if t8 <= ts <= sched and r.get('mid'):
                        out.append((ts, float(r['mid'])))
                except Exception:
                    continue
    out.sort()
    return out

def prints_series(tk, t8, sched):
    rows = con.execute(
        'SELECT ts, price FROM prints WHERE ticker=? AND ts>=? AND '
        'ts<=? ORDER BY ts', (tk, t8, sched)).fetchall()
    return [(t, int(p)) for t, p in rows if p]

def suffix_min(pr):
    """[(t, min print from t onward)] breakpoints, for O(log) fill tests."""
    out = []
    m = None
    for t, p in reversed(pr):
        if m is None or p < m:
            m = p
            out.append((t, m))
    out.reverse()
    return out

def reach_after(sm, tp):
    """Lowest print at/after tp given suffix-min breakpoints."""
    lo = None
    for t, m in sm:
        if t >= tp:
            return m          # first breakpoint at/after tp has the min
        lo = m                 # breakpoints before tp: min includes later
    # tp beyond last breakpoint: no prints after
    return None

def fills(sm, level, tp, rule='le'):
    r = reach_after(sm, tp)
    if r is None:
        return False
    return (r <= level) if rule == 'le' else (r <= level - 1)

# ---- substrate (BOOK frame) --------------------------------------------
SUB = OUT / 'substrate_book.jsonl'

def build():
    have = set()
    if SUB.exists():
        for line in open(SUB):
            try:
                have.add(json.loads(line)['event'])
            except Exception:
                pass
    # events from the tick dir itself (the honest frame's own census)
    evs = defaultdict(set)
    for f in os.listdir(TICKS):
        tk = f.split('.csv')[0]
        ev = tk.rsplit('-', 1)[0]
        if cat_of(ev):
            evs[ev].add(tk)
    # scheds from engine logs (last schedule_match wins)
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
        t8 = s - 8 * 3600
        legs = {}
        ok = True
        for tk in sorted(tks):
            ms = mid_series(tk, t8, s)
            pr = prints_series(tk, t8, s)
            if len(ms) < 10 or len(pr) < 5:
                ok = False
                break
            anchor = ms[0][1]
            mids = [m for _, m in ms]
            up = any(m - anchor >= 5 for m in mids)
            dn = any(m - anchor <= -5 for m in mids)
            # bid-reachable excursion depths below CONTEMPORANEOUS mid
            depths = []
            mi = 0
            for t, p in pr:
                while mi + 1 < len(ms) and ms[mi + 1][0] <= t:
                    mi += 1
                depths.append(round(ms[mi][1] - p, 1))
            mn = min(p for _, p in pr)
            legs[tk] = {'anchor': round(anchor, 1),
                        'close_mid': round(mids[-1], 1),
                        'close_print': pr[-1][1],
                        'path_up': up, 'path_dn': dn,
                        'n_ticks': len(ms), 'n_prints': len(pr),
                        'band': band_call(cat_of(ev), anchor,
                                          mids[-1] - anchor,
                                          max(0, anchor - min(mids))),
                        'floor_t': round(min(
                            (p, t) for t, p in pr)[1] - t8),
                        'max_depth_below_mid': max(depths) if depths
                        else 0,
                        'sm': [[round(t - t8), p]
                               for t, p in suffix_min(pr)]}
        if not ok or len(legs) != 2:
            continue
        ups = [v['path_up'] for v in legs.values()]
        dns = [v['path_dn'] for v in legs.values()]
        kl = ('flat_flat' if not (any(ups) or any(dns)) else
              'mirror' if (any(ups) and any(dns)) else 'neither')
        sf.write(json.dumps({'event': ev, 'cat': cat_of(ev), 'sched': s,
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
            g = json.loads(line)
            for v in g['legs'].values():
                v['smx'] = [(t, p) for t, p in v['sm']]
            G.append(g)
        except Exception:
            continue
    return G

# ---- THE VALIDATION GATE (mandatory, first) ----------------------------
def gate():
    """Reproduce the machine's realized duals: same games, same levels,
    fill where reality filled. Both rules tested; the one reproducing
    reality is the law; if neither: DISCARD the simulator."""
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
                    d = j['details']
                    fills_real[j['ticker'].rsplit('-', 1)[0]][
                        j['ticker']] = int(d['fill_price'])
                except Exception:
                    continue
            elif '"order_placed"' in line and '"buy"' in line:
                try:
                    j = json.loads(line)
                    d = j['details']
                    placed[j['ticker']][int(d['price'])] = \
                        j['ts_epoch']
                except Exception:
                    continue
    res = {'le': [0, 0], 'lt': [0, 0]}
    rows = []
    tested = 0
    for ev, legs in fills_real.items():
        if len(legs) != 2 or not cat_of(ev):
            continue
        sims = {}
        cover = True
        for tk, lvl in legs.items():
            pr = None
            # coverage: prints for this ticker in the store around fill
            tp = placed.get(tk, {}).get(lvl)
            prs = prints_series(tk, (tp or 0) - 3600 if tp else 0,
                                9e12)
            if not prs or tp is None:
                cover = False
                break
            sm = suffix_min(prs)
            sims[tk] = {'le': fills(sm, lvl, tp, 'le'),
                        'lt': fills(sm, lvl, tp, 'lt')}
        if not cover:
            continue
        tested += 1
        for rule in ('le', 'lt'):
            ok = all(s[rule] for s in sims.values())
            res[rule][0] += 1 if ok else 0
            res[rule][1] += 1
        rows.append((ev, {t.rsplit('-', 1)[1]: legs[t] for t in legs},
                     {t.rsplit('-', 1)[1]:
                      {r: sims[t][r] for r in ('le', 'lt')}
                      for t in sims}))
    L = ['## THE VALIDATION GATE — reproduce the machine\'s realized '
         'duals (big-4, coverage-qualified): tested %d' % tested]
    verdict = None
    for rule, nm in (('le', 'fill at/below our level'),
                     ('lt', 'strictly-below only')):
        ok, n = res[rule]
        pct = 100 * ok / max(1, n)
        L.append('- rule %s (%s): reproduced %d/%d duals = %.0f%%'
                 % (rule, nm, ok, n, pct))
        if pct >= 90 and verdict is None:
            verdict = rule
    if verdict:
        L.append('**GATE PASS — rule "%s" is the law of this frame.**'
                 % verdict)
    else:
        L.append('**GATE FAIL — the simulator cannot reproduce reality '
                 'and is DISCARDED. No verdicts print.**')
        for r in rows[:6]:
            L.append('- %s' % json.dumps(r))
    print('\n'.join(L), flush=True)
    (OUT / 'VALIDATION_GATE.md').write_text('\n'.join(L) + '\n')
    return verdict, '\n'.join(L)

# ---- census + drill under the frame ------------------------------------
def leg_arm(g, v):
    if v['path_dn'] and not v['path_up']:
        cm = BMAP.get(g['cat']) or {}
        nm = next((b.get('net_med', 0) for b in cm.get('bands', [])
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

def run(pool, QD, qf, qr, qd, frame, rule):
    comp = du = n = ref = mast = 0
    linked = clean_n = 0
    for g in pool:
        tp = 0 if frame == 'open' else (28800 - 14400 if frame == 'f4h'
                                        else 28800 - 7200)
        rows = []
        skip = refuse = False
        for v in g['legs'].values():
            arm, rf = leg_arm(g, v)
            if rf:
                refuse = True
                break
            qt = QD.get(v['band'])
            if not qt:
                skip = True
                break
            q = qf if arm == 'flat_divot' else \
                qr if arm == 'riser_divot' else qd
            lvl = int(round(v['anchor'] - qt[q]))
            t_arm = max(tp, v['floor_t']) if arm == 'decel_cast' else tp
            rows.append((v, lvl, t_arm))
        if refuse:
            ref += 1
            continue
        if skip:
            continue
        n += 1
        f9 = [(v, lvl if fills(v['smx'], lvl, t_arm, rule) else None)
              for v, lvl, t_arm in rows]
        if all(px is not None for _, px in f9):
            du += 1
            cmb = sum(px for _, px in f9)
            if cmb < 100:
                comp += 1
                if all(px < v['close_print'] for v, px in f9):
                    mast += 1
    return n, du, comp, ref, mast

def census_and_drill(rule):
    G = load()
    days = sorted({g['day'] for g in G})
    cutd = days[len(days) // 2]
    fit_g = [g for g in G if g['day'] < cutd]
    judge_g = [g for g in G if g['day'] >= cutd]
    # arrival tables: depth of reach below CONCEPTION anchor(mid), fit days
    arr = defaultdict(list)
    for g in fit_g:
        for v in g['legs'].values():
            sm0 = v['smx'][0][1] if v['smx'] else None
            if sm0 is not None:
                arr[v['band']].append(round(v['anchor'] - sm0, 1))
    QD = {}
    for band, ds in arr.items():
        if len(ds) < 20:
            continue
        ds = sorted(ds)
        QD[band] = {q: ds[max(0, min(len(ds) - 1,
                                     int((1 - q / 100) * len(ds))))]
                    for q in (50, 60, 70, 80, 90)}
        # qXX = depth reached in XX% of windows (P(reach>=d)=q/100)
    L = ['# CAPTURE STANDARD — BOOK/MID FRAME (frame-defect re-run; '
         'validation-gated, rule=%s). Ground %s->%s (book-series span; '
         'pre-JUL-12 excluded by construction). Whole market. '
         'Generated %s ET.' % (rule, days[0], days[-1],
                               datetime.now(ET).strftime(
                                   '%m-%d %I:%M %p')),
         'games %d (fit %d < %s <= judge %d) · class mix %s · arrival '
         'tables (reach-below-mid-anchor) bands %d'
         % (len(G), len(fit_g), cutd, len(judge_g),
            {k: sum(1 for g in G if g['path_class'] == k)
             for k in ('flat_flat', 'mirror', 'neither')}, len(QD)), '']
    # THE CENSUS: sealed-analog depths replaced by frame-honest reach
    # funnel at the median-reach depth (q50) as the reference policy
    best = None
    for qf in (50, 60, 70, 80, 90):
        for qr in (50, 70, 90):
            for qd in (50, 70, 90):
                for fr in ('open', 'f4h', 'f2h'):
                    n, du, comp, ref, mast = run(
                        fit_g, QD, qf, qr, qd, fr, rule)
                    cr = 100 * comp / max(1, n)
                    sr = 100 * comp / max(1, du)
                    if cr >= 50:
                        L.append('- FIT f%d/r%d/d%d/%s: **%.0f%% x '
                                 '%.0f%%** (subpar %d / games %d · '
                                 'duals %d · mastery %.0f%%)'
                                 % (qf, qr, qd, fr, cr, sr, comp, n,
                                    du, 100 * mast / max(1, du)))
                    if best is None or cr > best[0]:
                        best = (cr, qf, qr, qd, fr)
    _, qf, qr, qd, fr = best
    n, du, comp, ref, mast = run(judge_g, QD, qf, qr, qd, fr, rule)
    cr = 100 * comp / max(1, n)
    sr = 100 * comp / max(1, du)
    L.append('')
    L.append('## HOLDOUT (unseen) f%d/r%d/d%d/%s: **%.0f%% x %.0f%%** '
             '(subpar-duals %d / games %d · duals %d · refused %d '
             'apart · mastery %.0f%%) -> %s'
             % (qf, qr, qd, fr, cr, sr, comp, n, du, ref,
                100 * mast / max(1, du),
                'EXIT (a): JOINT BAR MET — re-seal by ceremony'
                if cr >= 70 and sr >= 70 else
                'below bar — the ceiling decides'))
    # CEILING per class in the honest frame
    L.append('')
    L.append('## THE CEILINGS (deepest reach, judge pool):')
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
                t0 = v['floor_t'] if arm == 'decel_cast' else 0
                r = reach_after(v['smx'], t0)
                deep.append(r)
            if refuse:
                rf9 += 1
                continue
            cn += 1
            if all(x is not None for x in deep) and sum(deep) < 100:
                avail += 1
        tot_a += avail
        tot_n += cn
        L.append('- %s: ceiling %.0f%% (%d/%d; refused %d apart) · '
                 'games/day %.1f'
                 % (kl, 100 * avail / max(1, cn), avail, cn, rf9,
                    avail / days_j))
    tv = 100 * tot_a / max(1, tot_n)
    L.append('## THE SUM vs 70: **%.0f%%** (%d/%d; %.1f games/day). %s'
             % (tv, tot_a, tot_n, tot_a / days_j,
                'Completion >= 70 PHYSICALLY AVAILABLE — iterate knobs.'
                if tv >= 70 else
                '**EXIT (b) EVIDENCE: gap %.0fpp / %.1f games/day = '
                'the widening work.**'
                % (70 - tv, (0.7 * tot_n - tot_a) / days_j)))
    # MIRROR LAW
    mp = [g for g in judge_g if g['path_class'] == 'mirror']
    clean = unclean = linked = 0
    prow = []
    xs, ys = [], []
    tpb = 0 if fr == 'open' else (28800 - 14400 if fr == 'f4h'
                                  else 28800 - 7200)
    for g in mp:
        legs = list(g['legs'].items())
        upl = [(t, v) for t, v in legs if v['path_up'] and not v['path_dn']]
        dnl = [(t, v) for t, v in legs if v['path_dn'] and not v['path_up']]
        if len(upl) != 1 or len(dnl) != 1:
            unclean += 1
            continue
        clean += 1
        (rtk, rv), (ftk, fv) = upl[0], dnl[0]
        rqt, fqt = QD.get(rv['band']), QD.get(fv['band'])
        rl = int(round(rv['anchor'] - rqt[qr])) if rqt else None
        fl = int(round(fv['anchor'] - fqt[qd])) if fqt else None
        rfill = (rl if rl and fills(rv['smx'], rl, tpb, rule) else None)
        ffill = (fl if fl and fills(fv['smx'], fl,
                                    max(tpb, fv['floor_t']), rule)
                 else None)
        if rfill is not None and ffill is not None:
            linked += 1
        prow.append({'event': g['event'],
                     'riser': {'leg': rtk.rsplit('-', 1)[1],
                               'fill': rfill},
                     'fader': {'leg': ftk.rsplit('-', 1)[1],
                               'floor_t_min': round(fv['floor_t'] / 60),
                               'cast_fill': ffill,
                               'miss': None if ffill is not None else
                               'reach-short-post-floor'},
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
        corr = (sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / den
                if den else None)
    L.append('')
    L.append('## MIRROR LAW: games %d · clean %d (unclean %d apart) · '
             '**LINK-RATE %d/%d = %.0f%%** · inverse receipt (riser-'
             'floor vs fader-floor clocks) r=%s n=%d'
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
    rule, gtxt = gate()
    if not rule:
        sys.exit(1)          # the gate law: no verdicts on FAIL
    census_and_drill(rule)
