#!/usr/bin/env python3
# CONVICTION DEEPENING (operator dispatch 07-20 PM) — THE ROLLING-ORIGIN
# BACKWALK. Background drill lane; the live seal trades untouched.
#   The fit/judge WALL marches week-by-week across the print-deep store:
#   at each wall W, per-band numbers (dip_p50/p90 · net_med · net_q25 ·
#   net_q10) are fit ONLY from event-days < W; the judge week [W, W+7)
#   is scored UNSEEN — every event judged in exactly one week, once.
#   Band geometry (band_map_v1) and recognition (h6) are HELD FIXED as
#   the frame (re-clustering weekly would churn band identity — named,
#   not hidden). Scoring per the ruling: COMBINED-PRIMARY (sub-par <=97
#   = pass; tiers <=93/<=95/<=97/98-100/>100) + the MASTERY METER
#   (dual-negative, reported never pass/fail).
#   Arms: sealed flat-flat dual-divot (wall-fit dip_p90) · riser
#   divot-during-climb · FADER CANDIDATES on the weakening leg:
#     A shallow  = anchor + net_med + 2      (the too-shallow exhibit)
#     B q25      = anchor + net_q25          (loop-7 family)
#     C q10deep  = anchor + net_q10          (deeper terminal)
#   Deliverables: does the sealed crop's sub-par hold across weeks of
#   unseen days; does ANY fader frame clear combined anywhere in
#   history. Per-wall receipts + tape-fidelity mix (store src column).
#   Usage: --full (all walls) | --wall latest (nightly cron marches the
#   newest wall). Nice-priority lane.
import json, os, sqlite3, statistics, sys, time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    os.nice(15)
except Exception:
    pass
ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo('America/New_York')
BMAP = json.loads((ROOT / 'state/band_map_v1.json').read_text())['cats']
RECOG = json.loads((ROOT / 'state/drift_surfaces_v1.json').read_text()
                   ).get('recognition', {})
DB = ROOT / 'state/subsecond_store.db'
EV = ROOT / 'state/corpus_events_v2.jsonl'
OUT = ROOT.parent / '.claude/backwalk_20260720'
OUT.mkdir(exist_ok=True)
BIG4 = {'KXATPMATCH': 'ATP_MAIN', 'KXWTAMATCH': 'WTA_MAIN',
        'KXATPCHALLENGERMATCH': 'ATP_CHALL',
        'KXWTACHALLENGERMATCH': 'WTA_CHALL'}
WALL0 = datetime(2026, 5, 25, 0, 0, tzinfo=ET)   # first wall: >=11d of tape
LAST = datetime(2026, 7, 20, 0, 0, tzinfo=ET)

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

def dband(cat, a):
    c = BMAP.get(cat)
    if not c or c.get('thin'):
        return None
    fl = [b for b in c['bands'] if b['direction'] == 'flat'] or c['bands']
    return min(fl, key=lambda b: abs(b['anchor_med'] - a))['band']

def recall(cat, a, n, d):
    cell = (RECOG.get(cat + '|h6') or {}).get(pb(a, n, d))
    if cell and cell.get('purity', 0) >= 0.5:
        return cell['top']
    return dband(cat, a)

con = sqlite3.connect('file:%s?mode=ro' % DB, uri=True, timeout=30)

def leg_prints(tk, t0, t1):
    return con.execute('SELECT ts, price, src FROM prints WHERE ticker=? '
                       'AND ts>=? AND ts<=? ORDER BY ts',
                       (tk, t0, t1)).fetchall()

# ---- corpus: big-4 events with honest scheds inside store coverage ----
events = []
for line in open(EV, encoding='utf-8', errors='replace'):
    try:
        r = json.loads(line)
    except ValueError:
        continue
    ev = r.get('event'); cat = cat_of(ev or '')
    s = r.get('sched_honest') or r.get('sched')
    if not ev or not cat or not s:
        continue
    if WALL0.timestamp() <= s <= LAST.timestamp() + 7 * 86400:
        events.append((ev, cat, float(s)))
events.sort(key=lambda x: x[2])
print('backwalk corpus: %d big-4 events %s -> %s' % (
    len(events), WALL0.date(), LAST.date()), flush=True)

# ---- pass 1: per-leg cache (features + dip samples + net), one query --
CACHE = OUT / 'legcache.jsonl'
done = set()
if CACHE.exists():
    for line in open(CACHE):
        try:
            done.add(json.loads(line)['tk'])
        except Exception:
            pass
cf = open(CACHE, 'a')
n_new = 0
LEGS = {}
for ev, cat, s in events:
    t8 = s - 8 * 3600
    tks = [r[0] for r in con.execute(
        'SELECT DISTINCT ticker FROM prints WHERE event=?', (ev,))]
    LEGS[ev] = sorted(tks)
    if len(tks) != 2:
        continue
    for tk in sorted(tks):
        if tk in done:
            continue
        rows = leg_prints(tk, t8 - 86400, s)
        win = [(t, int(p)) for t, p, _ in rows if t8 <= t <= s and p]
        srcs = defaultdict(int)
        for t, _, sr in rows:
            if t8 <= t <= s:
                srcs[sr] += 1
        rec = {'tk': tk, 'event': ev, 'cat': cat, 'sched': s,
               'day': datetime.fromtimestamp(s, ET).strftime('%Y%m%d'),
               'n_prints': len(win), 'srcs': dict(srcs)}
        if len(win) >= 5:
            pre = [int(p) for t, p, _ in rows if t <= t8 and p]
            anchor = pre[-1] if pre else win[0][1]
            lows = min(p for _, p in win)
            rec.update({'anchor': anchor, 'open': win[0][1],
                        'close': win[-1][1], 'low': lows,
                        'net': win[-1][1] - win[0][1],
                        'dip': max(0, anchor - lows)})
            # dip-depth samples vs trailing-30min rolling median
            # (divot-v2 definition: <=med-2 with recovery to med-1)
            dq, wnd, cur = [], [], None
            for t, p_ in win:
                wnd = [(x, q) for x, q in wnd if x >= t - 1800]
                med = statistics.median([q for _, q in wnd]) if wnd else p_
                wnd.append((t, p_))
                if cur is None and p_ <= med - 2:
                    cur = (med, p_)
                elif cur is not None:
                    cur = (cur[0], min(cur[1], p_))
                    if p_ >= cur[0] - 1:
                        dq.append(round(cur[0] - cur[1], 1))
                        cur = None
            rec['dips'] = dq[:40]
        cf.write(json.dumps(rec) + '\n')
        n_new += 1
        if n_new % 200 == 0:
            cf.flush()
            print('cache +%d' % n_new, flush=True)
cf.close()
print('cache pass done: +%d legs' % n_new, flush=True)

# ---- load cache ---------------------------------------------------------
L = {}
for line in open(CACHE):
    try:
        r = json.loads(line)
        L[r['tk']] = r
    except Exception:
        continue

# ---- walls --------------------------------------------------------------
only_latest = '--wall' in sys.argv and 'latest' in sys.argv
walls = []
w = WALL0
while w <= LAST:
    walls.append(w)
    w += timedelta(days=7)
if only_latest:
    walls = walls[-1:]

def fit(day_lt):
    F = defaultdict(lambda: {'dips': [], 'nets': []})
    for r in L.values():
        if r['day'] >= day_lt or 'anchor' not in r:
            continue
        band = recall(r['cat'], r['anchor'], r['net'], r['dip'])
        if not band:
            continue
        F[band]['dips'].extend(r.get('dips') or [])
        F[band]['nets'].append(r['net'])
    T = {}
    for band, v in F.items():
        if len(v['nets']) < 30 or len(v['dips']) < 30:
            continue                      # band silent this wall — named
        d = sorted(v['dips']); n = sorted(v['nets'])
        T[band] = {'dip_p90': d[int(0.9 * len(d))],
                   'net_med': n[len(n) // 2],
                   'net_q25': n[int(0.25 * len(n))],
                   'net_q10': n[int(0.10 * len(n))],
                   'n': len(v['nets'])}
    return T

def sim_leg(r, T, fader):
    # band call at cut features (T-6h approx from tape)
    tape = r['tape']
    if not tape:
        return None
    cutoff = 2 * 3600.0
    upto = [p for dt, p in tape if dt <= cutoff] or [tape[0][1]]
    band = recall(r['cat'], r['anchor'], upto[-1] - tape[0][1],
                  max(0, r['anchor'] - min(upto)))
    row = T.get(band)
    if not row:
        return None
    anchor, close = r['anchor'], r['close']
    fill = arm = cast = None
    up = dn = refuse = False
    wnd, meds = [], []
    for dt, p_ in tape:
        wnd = [(x, q) for x, q in wnd if x >= dt - 1800]
        med = statistics.median([q for _, q in wnd]) if wnd else p_
        meds.append((dt, med))
        wnd.append((dt, p_))
        net_now = med - anchor
        if net_now >= 5:
            up = True
        if net_now <= -5 and not dn:
            dn = True
            cb = recall(r['cat'], anchor, int(net_now),
                        max(0, anchor - min(q for _, q in wnd)))
            cr = T.get(cb)
            if cr:
                if cr['net_med'] <= -30:
                    refuse = True
                else:
                    lv = anchor + (cr['net_med'] + 2 if fader == 'A'
                                   else cr['net_q25'] if fader == 'B'
                                   else cr['net_q10'])
                    if lv >= 5:
                        cast = int(round(lv))
        if cast is not None and fill is None and not refuse and p_ <= cast:
            fill, arm = cast, 'faller'
            break
        dur = tape[-1][0]
        if dt < max(cutoff, dur - 2 * 3600):
            continue
        if refuse or net_now <= -5:
            continue
        old_m = [m for x, m in meds if x <= dt - 1800]
        st = (med >= old_m[-1] - 1) if old_m else True
        lvl = max(1, int(round(med)) - int(round(row['dip_p90'])))
        if st and p_ <= lvl:
            fill = lvl
            arm = 'riser' if net_now >= 5 else 'flat'
            break
    return {'fill': fill, 'arm': arm, 'close': close, 'up': up, 'dn': dn}

def tier(c):
    return '<=93' if c <= 93 else '<=95' if c <= 95 else '<=97' \
        if c <= 97 else '98-100' if c <= 100 else '>100'

REPORT = []
for w in walls:
    wl = w.strftime('%Y%m%d')
    we = (w + timedelta(days=7)).strftime('%Y%m%d')
    T = fit(wl)
    week_ev = [(ev, cat, s) for ev, cat, s in events
               if wl <= datetime.fromtimestamp(s, ET).strftime('%Y%m%d')
               < we and len(LEGS.get(ev) or []) == 2]
    res = {f: defaultdict(lambda: {'pairs': 0, 'duals': 0, 'pass': 0,
                                   'tiers': defaultdict(int),
                                   'dualneg': 0, 'pd': []})
           for f in 'ABC'}
    srcs = defaultdict(int)
    scored = 0
    for ev, cat, s in week_ev:
        rs = [L.get(tk) for tk in LEGS[ev]]
        if any(r is None or 'anchor' not in r for r in rs):
            continue
        t8 = s - 8 * 3600
        for r in rs:
            rows_j = leg_prints(r['tk'], t8, s)
            r['tape'] = [[round(t - t8, 1), int(p)]
                         for t, p, _ in rows_j if p]
        scored += 1
        for r in rs:
            for k, v in (r.get('srcs') or {}).items():
                srcs[k] += v
        for f in 'ABC':
            sims = [sim_leg(r, T, f) for r in rs]
            if any(x is None for x in sims):
                continue
            up = any(x['up'] for x in sims)
            dn = any(x['dn'] for x in sims)
            kl = 'mirror' if (up and dn) else 'flat_flat' \
                if not (up or dn) else 'neither'
            st = res[f][kl]
            st['pairs'] += 1
            if all(x['fill'] is not None for x in sims):
                comb = sum(x['fill'] for x in sims)
                st['duals'] += 1
                st['tiers'][tier(comb)] += 1
                st['pd'].append(sum(x['fill'] - x['close'] for x in sims))
                if comb <= 97:
                    st['pass'] += 1
                if all(x['fill'] < x['close'] for x in sims):
                    st['dualneg'] += 1
    tot = sum(srcs.values()) or 1
    fid = ' '.join('%s %.0f%%' % (k, 100 * v / tot)
                   for k, v in sorted(srcs.items(), key=lambda x: -x[1]))
    lines = ['## WALL %s (judge %s->%s) · events scored %d · bands fit %d'
             ' · tape fidelity: %s'
             % (wl, wl, we, scored, len(T), fid or 'none')]
    for kl in ('flat_flat', 'mirror', 'neither'):
        st = res['A'][kl]     # flat/riser arms identical across A/B/C
        if kl == 'flat_flat':
            du = st['duals']
            ln = ('- FLAT-FLAT (sealed frame): pairs %d duals %d · '
                  'SUB-PAR %d/%d%s · tiers %s · MASTERY dual-neg %s'
                  % (st['pairs'], du, st['pass'], du,
                     (' = %.0f%%' % (100 * st['pass'] / du)) if du else '',
                     dict(sorted(st['tiers'].items())),
                     ('%.0f%%' % (100 * st['dualneg'] / du)) if du else '-'))
            lines.append(ln)
    for f, nm in (('A', 'shallow net_med+2'), ('B', 'q25'),
                  ('C', 'q10-deep')):
        st = res[f]['mirror']
        du = st['duals']
        lines.append('- MIRROR fader-%s (%s): pairs %d duals %d · SUB-PAR '
                     '%d/%d%s · tiers %s · MASTERY %s · medPairD %s'
                     % (f, nm, st['pairs'], du, st['pass'], du,
                        (' = %.0f%%' % (100 * st['pass'] / du)) if du else '',
                        dict(sorted(st['tiers'].items())),
                        ('%.0f%%' % (100 * st['dualneg'] / du)) if du else '-',
                        ('%+d' % statistics.median(st['pd'])) if st['pd']
                        else '-'))
    REPORT.append('\n'.join(lines))
    print(lines[0], flush=True)

hdr = ('# CONVICTION BACKWALK — rolling-origin, wall weekly '
       '(fit < wall; judge week unseen once). Combined-primary + '
       'mastery meter. Band geometry + recognition HELD FIXED as the '
       'frame (named). Generated %s ET.\n'
       % datetime.now(ET).strftime('%m-%d %I:%M %p'))
mode = 'a' if only_latest else 'w'
open(OUT / 'BACKWALK_WALLS.md', mode).write(
    (hdr if mode == 'w' else '') + '\n\n'.join(REPORT) + '\n')
print('BACKWALK DONE: %d walls -> %s' % (len(REPORT),
                                         OUT / 'BACKWALK_WALLS.md'))
