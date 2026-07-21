#!/usr/bin/env python3
# THE CAPTURE STANDARD (operator dispatch + two amendments, 07-20 night).
# The sealed class is judged on BOTH axes JOINTLY: >=70% of floor-passing
# FLAT_FLAT games complete DUAL in W1 at combined sub-par, AND >=70% of
# completed duals sub-par. Completion is pass/fail, first number.
#
# GROUND (date-range line, verbatim law): Jul 12 -> yesterday,
# fit-early / judge-unseen, growing nightly. Pre-Jul-12 backfill events
# join the JUDGING pool only where BOTH legs clear the per-event density
# bar (>= 200 prints in-window, the declared decision-grade threshold),
# named per event. Below the bar: EXCLUDED — no simulated divot fills on
# coarse tape, EVER.
#
# EXIT LAW (Loop 9, verbatim): only two exits — (a) >=70/>=70 on unseen
# dense days -> re-seal by ceremony; (b) the arrival distributions prove
# a hard ceiling below 70 -> ceiling named in CENTS and GAMES/DAY, the
# next drill widens the playable class by breadth. No third exit. No
# quality-only progress. Joint number (completion% x sub-par%) FIRST on
# every iteration line.
#
# Modes:
#   --census  P1: the leak funnel (called -> floor -> fish placed ->
#             divots arrived -> eaten/starved, reason per leg), sealed
#             fish (b2f0b670 depths), two placement frames (window-open
#             and final-2h), leak classes ranked by games lost.
#   --drill   P2/Loop 9: knob grid (depth quantile x arming x offset)
#             against BOTH bars, fit-early/judge-unseen, exits per law.
import json, os, sqlite3, statistics, sys
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
SEAL = json.loads((ROOT / 'state/pair_policies_sealed_v1.json'
                   ).read_text())['bands']
DB = ROOT / 'state/subsecond_store.db'
EV = ROOT / 'state/corpus_events_v2.jsonl'
OUT = ROOT.parent / '.claude/capture_20260720'
OUT.mkdir(exist_ok=True)
BIG4 = {'KXATPMATCH': 'ATP_MAIN', 'KXWTAMATCH': 'WTA_MAIN',
        'KXATPCHALLENGERMATCH': 'ATP_CHALL',
        'KXWTACHALLENGERMATCH': 'WTA_CHALL'}
DENSE0 = datetime(2026, 7, 12, 0, 0, tzinfo=ET).timestamp()
YEST = (datetime.now(ET) - timedelta(days=1)).replace(
    hour=23, minute=59, second=59).timestamp()
DENSITY_BAR = 200      # per-event, per-leg, declared decision-grade bar

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

# ---- SUBSTRATE: path-classed flat-flat games on qualifying tape --------
SUB = OUT / 'substrate.jsonl'

def build_substrate():
    have = set()
    if SUB.exists():
        for line in open(SUB):
            try:
                have.add(json.loads(line)['event'])
            except Exception:
                pass
    evs = []
    for line in open(EV, encoding='utf-8', errors='replace'):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        ev = r.get('event'); cat = cat_of(ev or '')
        s = r.get('sched_honest') or r.get('sched')
        if not ev or not cat or not s or s > YEST or ev in have:
            continue
        evs.append((ev, cat, float(s)))
    sf = open(SUB, 'a')
    n9 = 0
    for ev, cat, s in sorted(evs, key=lambda x: x[2]):
        tks = [r[0] for r in con.execute(
            'SELECT DISTINCT ticker FROM prints WHERE event=?', (ev,))]
        if len(tks) != 2:
            continue
        t8 = s - 8 * 3600
        legs = {}
        ok = True
        for tk in sorted(tks):
            rows = con.execute(
                'SELECT ts, price FROM prints WHERE ticker=? AND ts>=? '
                'AND ts<=? ORDER BY ts', (tk, t8 - 86400, s)).fetchall()
            win = [(t, int(p)) for t, p in rows if t8 <= t <= s and p]
            # THE FIDELITY LAW: dense era by date, or pre-JUL-12 patch
            # clearing the per-event bar. Below: excluded, never simmed.
            if s >= DENSE0:
                if len(win) < 50:      # dense-era thin legs still skip
                    ok = False
                    break
            elif len(win) < DENSITY_BAR:
                ok = False
                break
            pre = [int(p) for t, p in rows if t <= t8 and p]
            anchor = pre[-1] if pre else win[0][1]
            # path walk: rolling 30-min median; class crossings; divots
            wnd, meds, divots = [], [], []
            up = dn = False
            cur = None
            for t, p_ in win:
                wnd = [(x, q) for x, q in wnd if x >= t - 1800]
                med = statistics.median([q for _, q in wnd]) if wnd else p_
                wnd.append((t, p_))
                meds.append((t, med))
                nn = med - anchor
                if nn >= 5:
                    up = True
                if nn <= -5:
                    dn = True
                if cur is None and p_ <= med - 2:
                    cur = [med, p_, t]
                elif cur is not None:
                    if p_ < cur[1]:
                        cur[1], cur[2] = p_, t
                    if p_ >= cur[0] - 1:
                        divots.append({'t': round(cur[2] - t8),
                                       'trough': cur[1],
                                       'depth': round(cur[0] - cur[1], 1)})
                        cur = None
            band = recall(cat, anchor,
                          (win[-1][1] - win[0][1]), max(0, anchor - min(
                              p for _, p in win)))
            legs[tk] = {'anchor': anchor, 'close': win[-1][1],
                        'n_prints': len(win), 'band': band,
                        'path_up': up, 'path_dn': dn,
                        'divots': divots[:60],
                        'min_print': min(p for _, p in win),
                        'min_print_t': round(min(
                            (p, t) for t, p in win)[1] - t8),
                        'prints_leq': {}}
            # fill tests at candidate levels get computed on demand in
            # census/drill from divots+min; store a coarse price-time
            # frontier: earliest time each cent level was touched
            frontier = {}
            for t, p_ in win:
                if p_ not in frontier:
                    frontier[p_] = round(t - t8)
            legs[tk]['frontier'] = {str(k): v for k, v in
                                    sorted(frontier.items())}
        if not ok or len(legs) != 2:
            continue
        ups = [v['path_up'] for v in legs.values()]
        dns = [v['path_dn'] for v in legs.values()]
        kl = ('flat_flat' if not (any(ups) or any(dns)) else
              'mirror' if (any(ups) and any(dns)) else 'neither')
        sf.write(json.dumps({
            'event': ev, 'cat': cat, 'sched': s,
            'day': datetime.fromtimestamp(s, ET).strftime('%Y%m%d'),
            'era': 'dense' if s >= DENSE0 else 'patch(pre-JUL12, bar-cleared)',
            'path_class': kl, 'legs': legs}) + '\n')
        n9 += 1
        if n9 % 100 == 0:
            sf.flush()
            print('substrate +%d' % n9, flush=True)
    sf.close()
    print('substrate done: +%d games' % n9, flush=True)

def load_sub():
    G = []
    for line in open(SUB):
        try:
            G.append(json.loads(line))
        except Exception:
            continue
    return G

def earliest_touch(leg, level, after=0):
    """Earliest window-second any print <= level, or None. Frontier is
    per-cent earliest-touch; scan levels <= level."""
    best = None
    for px, t in leg['frontier'].items():
        if int(px) <= level and t >= after:
            best = t if best is None else min(best, t)
    return best

# [SCOPE CORRECTION — operator's word 07-20 night: the 70/70 bar covers
# ALL floor-passing big-4 games, EVERY class, whole-market denominator.
# Arms per class: flats = dual-divots; mirrors = riser-divot-during-
# climb + the TIMING-LED DECELERATION CAST (graduated from proposal to
# drill, mastery-judged in-loop); violent-faller REFUSE = the only
# named exclusion, counted apart. Exit law unchanged: >=70% of ALL
# floor-passing games dual-completed at sub-par, or per-class ceilings
# in cents + games/day — the gap between the ceilings' sum and 70 IS
# the widening work, named. Joint number first, every lap.]

def leg_arm(g, v):
    """Arm assignment per the scope correction. Returns (arm, refuse)."""
    if v['path_dn'] and not v['path_up']:
        row = SEAL.get(v['band'])
        cband = v['band']
        cm = BMAP.get(g['cat']) or {}
        nm = next((b.get('net_med', 0) for b in cm.get('bands', [])
                   if b['band'] == cband), 0)
        if nm <= -30:
            return 'faller', True          # the violent knife — REFUSE
        return 'decel_cast', False         # the timing-led frame, drilled
    if v['path_up'] and not v['path_dn']:
        return 'riser_divot', False
    if v['path_up'] and v['path_dn']:
        return 'decel_cast', False         # round-tripper: post-trough
    return 'flat_divot', False

def catch(v, q_depth, t_after):
    """First divot with depth >= q after t_after -> fill price
    trough + (depth - q) (the walking fish's level at that dip)."""
    for d in v['divots']:
        if d['t'] >= t_after and d['depth'] >= q_depth:
            return int(round(d['trough'] + (d['depth'] - q_depth)))
    return None

# ======================= P1 — THE LEAK CENSUS ===========================
def census():
    G = load_sub()
    L = ['# THE LEAK CENSUS — WHOLE MARKET (scope correction: every '
         'floor-passing big-4 game, every class; violent-faller REFUSE '
         'the only exclusion, counted apart). Sealed depths per arm '
         '(flat/riser p90; decel cast dip_p50, declared). Generated %s ET.'
         % datetime.now(ET).strftime('%m-%d %I:%M %p'),
         'games (qualifying tape): %d (dense %d / patch %d) · class mix: '
         '%s · floor: big-4 carries no 1,500 ITF floor — all pass, named.'
         % (len(G), sum(1 for g in G if g['era'] == 'dense'),
            sum(1 for g in G if g['era'] != 'dense'),
            dict(sorted(((k, sum(1 for g in G if g['path_class'] == k))
                         for k in ('flat_flat', 'mirror', 'neither')),
                        key=lambda x: -x[1]))), '']
    for fname, tp in (('open', 0), ('final2h', 28800 - 7200)):
        funnel = defaultdict(int)
        leak = defaultdict(int)
        starve = defaultdict(int)
        gaps = []
        for g in G:
            funnel['called'] += 1
            rows = []
            refuse = dead = False
            for tk, v in g['legs'].items():
                arm, rf = leg_arm(g, v)
                row = SEAL.get(v['band'])
                if not row:
                    dead = True
                    break
                if rf:
                    refuse = True
                    break
                dep = (row.get('dip_p50') or 3) if arm == 'decel_cast' \
                    else row['depth_p90']
                t_arm = max(tp, v['min_print_t'] if arm == 'decel_cast'
                            else tp)
                rows.append((v, arm, dep, t_arm))
            if dead:
                leak['dead-band(no sealed row)'] += 1
                continue
            if refuse:
                funnel['violent_refused'] += 1
                continue
            funnel['floor_passing'] += 1
            eaten = []
            for v, arm, dep, t_arm in rows:
                px = catch(v, dep, t_arm)
                if px is not None:
                    eaten.append(px)
                    continue
                eaten.append(None)
                dvs = [d for d in v['divots'] if d['t'] >= t_arm]
                if not dvs:
                    starve['divot-never-came(%s)' % arm] += 1
                elif max(d['depth'] for d in dvs) < dep:
                    starve['came-shallower(%s)' % arm] += 1
                    gaps.append(round(dep - max(d['depth']
                                                for d in dvs), 1))
                else:
                    starve['came-pre-placement(%s)' % arm] += 1
            if all(px is not None for px in eaten):
                comb = sum(eaten)
                if comb <= 97:
                    funnel['dual_subpar'] += 1
                else:
                    leak['dual-but-over-par(%dc over)'
                         % (comb - 97)] += 1
            else:
                leak['starved(%s)' % ('both' if not any(
                    px is not None for px in eaten) else 'one-leg')] += 1
        comp = 100 * funnel['dual_subpar'] / max(1, funnel['floor_passing'])
        L.append('## FRAME %s: called %d -> floor-passing %d (violent '
                 'refused %d, apart) -> **DUAL-AT-SUB-PAR %d = '
                 'completion %.0f%% vs the 70 bar (whole market)** · '
                 'queue-lost unobservable in tape, live-only, named'
                 % (fname, funnel['called'], funnel['floor_passing'],
                    funnel['violent_refused'], funnel['dual_subpar'],
                    comp))
        for k, n in sorted(leak.items(), key=lambda x: -x[1])[:8]:
            L.append('- leak: %s — %d games' % (k, n))
        L.append('- starved legs by reason/arm: %s · shallow gap med %sc'
                 % (dict(sorted(starve.items(), key=lambda x: -x[1])),
                    statistics.median(gaps) if gaps else '-'))
        L.append('')
    out = '\n'.join(L) + '\n'
    (OUT / 'LEAK_CENSUS.md').write_text(out)
    print(out)

# ======================= P2 — LOOP 9: THE DRILL =========================
def drill():
    G = load_sub()          # WHOLE MARKET (scope correction)
    days = sorted({g['day'] for g in G if g['era'] == 'dense'})
    if len(days) < 4:
        print('DRILL REFUSED: <4 dense days')
        return
    cutd = days[len(days) // 2]      # fit-early / judge-unseen
    fit_g = [g for g in G if g['era'] == 'dense' and g['day'] < cutd]
    judge_g = [g for g in G if (g['era'] == 'dense' and g['day'] >= cutd)
               or g['era'] != 'dense']   # patches join the JUDGING pool
    # arrival-distribution depth tables from FIT days only
    arr = defaultdict(list)
    for g in fit_g:
        for v in g['legs'].values():
            for d in v['divots']:
                arr[v['band']].append(d['depth'])
    QT = {}
    for band, ds in arr.items():
        if len(ds) < 20:
            continue
        ds = sorted(ds)
        QT[band] = {q: ds[min(len(ds) - 1, int(q / 100 * len(ds)))]
                    for q in (50, 60, 70, 80, 90)}
    def run(pool, qf, qr, qd, frame):
        # whole-market: n = floor-passing games; refusals counted apart
        comp = du = n = ref = mast = 0
        for g in pool:
            tp = 0 if frame == 'open' else (28800 - 14400
                                            if frame == 'f4h'
                                            else 28800 - 7200)
            rows = []
            skip = refuse = False
            for v in g['legs'].values():
                arm, rf = leg_arm(g, v)
                if rf:
                    refuse = True
                    break
                qt = QT.get(v['band'])
                if not qt:
                    skip = True
                    break
                q = qf if arm == 'flat_divot' else \
                    qr if arm == 'riser_divot' else qd
                t_arm = max(tp, v['min_print_t']) if arm == 'decel_cast' \
                    else tp
                rows.append((v, qt[q], t_arm))
            if refuse:
                ref += 1
                continue
            if skip:
                continue
            n += 1
            fills = [(v, catch(v, dep, t_arm))
                     for v, dep, t_arm in rows]
            if all(px is not None for _, px in fills):
                du += 1
                cmb = sum(px for _, px in fills)
                if cmb <= 97:
                    comp += 1
                    if all(px < v['close'] for v, px in fills):
                        mast += 1   # mastery meter, in-loop, never a bar
        return n, du, comp, ref, mast
    L = ['# LOOP 9 — THE COMPLETION DRILL, WHOLE MARKET (joint bar '
         '>=70 completion x >=70 sub-par over ALL floor-passing big-4 '
         'games; ONLY TWO EXITS per the stopping law; violent-faller '
         'REFUSE the only exclusion, counted apart). Arms: flats dual-'
         'divot · mirrors riser-during-climb + DECELERATION CAST '
         '(graduated to drill, mastery in-loop). Ground: dense fit<%s / '
         'judge>=%s + bar-cleared patches. Generated %s ET.'
         % (cutd, cutd, datetime.now(ET).strftime('%m-%d %I:%M %p')),
         'fit games %d · judge games %d (patches %d) · arrival tables '
         'from fit days only (bands %d)'
         % (len(fit_g), len(judge_g),
            sum(1 for g in judge_g if g['era'] != 'dense'), len(QT)), '']
    best = None
    for qf in (50, 70, 90):
        for qr in (50, 70, 90):
            for qd in (50, 70, 90):
                for fr in ('open', 'f4h', 'f2h'):
                    n, du, comp, ref, mast = run(fit_g, qf, qr, qd, fr)
                    cr = 100 * comp / max(1, n)
                    sr = 100 * comp / max(1, du)
                    if cr >= 40 or (best is None):
                        L.append('- FIT f%d/r%d/d%d/%s: **%.0f%% x '
                                 '%.0f%%** (subpar-duals %d / games %d '
                                 '· duals %d · refused %d · mastery '
                                 '%.0f%%)'
                                 % (qf, qr, qd, fr, cr, sr, comp, n,
                                    du, ref,
                                    100 * mast / max(1, du)))
                    if (best is None or cr > best[0]):
                        best = (cr, sr, qf, qr, qd, fr)
    L.append('')
    cr0, sr0, qf, qr, qd, fr = best
    n, du, comp, ref, mast = run(judge_g, qf, qr, qd, fr)
    cr = 100 * comp / max(1, n)
    sr = 100 * comp / max(1, du)
    exit_a = cr >= 70 and sr >= 70
    L.append('## HOLDOUT (unseen) f%d/r%d/d%d/%s: **%.0f%% x %.0f%%** '
             '(subpar-duals %d / games %d · duals %d · refused %d apart '
             '· mastery %.0f%%) -> %s'
             % (qf, qr, qd, fr, cr, sr, comp, n, du, ref,
                100 * mast / max(1, du),
                'EXIT (a): JOINT BAR MET — re-seal by ceremony'
                if exit_a else 'BELOW BAR on unseen — the ceiling '
                'decides (below)'))
    # THE CEILING, PER CLASS (exit-b evidence): deepest-possible joint
    # capture (every divot caught at its trough, arm-lawful timing)
    L.append('')
    L.append('## THE CEILINGS, per class (deepest-possible capture, '
             'judge pool):')
    days_j = max(1, len({g['day'] for g in judge_g}))
    tot_avail = tot_n = 0
    for kl in ('flat_flat', 'mirror', 'neither'):
        pool = [g for g in judge_g if g['path_class'] == kl]
        avail = ceil_n = ref9 = 0
        over = []
        for g in pool:
            deep = []
            refuse = False
            for v in g['legs'].values():
                arm, rf = leg_arm(g, v)
                if rf:
                    refuse = True
                    break
                t_arm = v['min_print_t'] if arm == 'decel_cast' else 0
                dvs = [d for d in v['divots'] if d['t'] >= t_arm]
                deep.append(min((d['trough'] for d in dvs),
                                default=None))
            if refuse:
                ref9 += 1
                continue
            ceil_n += 1
            if all(x is not None for x in deep):
                cb = sum(deep)
                if cb <= 97:
                    avail += 1
                else:
                    over.append(cb - 97)
            # legs with no lawful divot at all: unreachable, counted in n
        av = 100 * avail / max(1, ceil_n)
        tot_avail += avail
        tot_n += ceil_n
        L.append('- %s: ceiling **%.0f%%** (%d/%d; refused %d apart) · '
                 'over-par-at-best med %sc · games/day at sub-par %.1f'
                 % (kl, av, avail, ceil_n, ref9,
                    statistics.median(over) if over else '-',
                    avail / days_j))
    tv = 100 * tot_avail / max(1, tot_n)
    L.append('')
    L.append('## THE SUM vs 70 (whole market): ceilings sum to **%.0f%%'
             '** (%d/%d floor-passing; %.1f games/day at sub-par). %s'
             % (tv, tot_avail, tot_n, tot_avail / days_j,
                ('Completion >= 70 is PHYSICALLY AVAILABLE — the miss '
                 'is knobs; iterate.') if tv >= 70 else
                ('**EXIT (b) EVIDENCE: the ceilings sum BELOW 70 — the '
                 'gap (%.0fpp, %.1f games/day) IS the widening work, '
                 'named per the law.**'
                 % (70 - tv, (0.70 * tot_n - tot_avail) / days_j))))
    out = '\n'.join(L) + '\n'
    (OUT / 'LOOP9_DRILL.md').write_text(out)
    print(out)

if __name__ == '__main__':
    if '--substrate' in sys.argv or not SUB.exists():
        build_substrate()
    if '--census' in sys.argv:
        census()
    if '--drill' in sys.argv:
        drill()
