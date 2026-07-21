#!/usr/bin/env python3
# P4 of the SPLIT-GAUGE dispatch (2026-07-20) — THE PER-CLASS NIGHTLY.
# The operator's two gauges as STANDING NIGHTLY LINES, one edition per
# night over yesterday's big-4 slate:
#   FLAT-FLAT pairs -> both-legs-negative rate vs the 75% bar
#   MIRROR pairs    -> the combined gauge (combD<=0 share · medPairD ·
#                      sub-par cost · tiers; loop-5 PASS law cited)
#   NEITHER         -> counted apart, no seal claim
# Model = the week-widen instrument verbatim (riser divot-during-climb
# p90/final-2h/guard · weakening EARLY CALL -> dest cast net_med+2,
# violent net_med<=-30 REFUSED · flat dual-divot p90). READ-SIDE
# measurement only — the gauges judge; nothing steers until a class
# clears its bar and a ceremony with members is held. Era stamp on
# every line: fits are frozen at the 07-20 ceremony (post-seal era);
# a re-fit founds a new era label — eras never mix.
# Cron: nightly post-midnight ET; appends NIGHTLY_PASS + dated artifact
# (.claude/perclass_meter/), commit+push per the milestone-shadow pattern.
import csv, glob, gzip, json, statistics, sys, time, urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = '/root/Omi-Workspace/arb-executor'
ET = ZoneInfo('America/New_York')
ERA = 'post-seal-20260720'
BMAP = json.load(open(ROOT + '/state/band_map_v1.json'))['cats']
DV2 = json.load(open(ROOT + '/state/divot_tables_v2.json'))['bands']
RECOG = json.load(open(ROOT + '/state/drift_surfaces_v1.json')).get(
    'recognition', {})
BIG4 = {'KXATPMATCH': 'ATP_MAIN', 'KXWTAMATCH': 'WTA_MAIN',
        'KXATPCHALLENGERMATCH': 'ATP_CHALL',
        'KXWTACHALLENGERMATCH': 'WTA_CHALL'}

_day = None
for i, a in enumerate(sys.argv):
    if a == '--date':
        _day = sys.argv[i + 1]
if _day:
    D0 = datetime.strptime(_day, '%Y%m%d').replace(tzinfo=ET)
else:
    D0 = (datetime.now(ET) - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0)
D1 = D0 + timedelta(days=1)
DAYTAG = D0.strftime('%Y%m%d')

def cat_of(event):
    for pfx, cat in BIG4.items():
        if event.startswith(pfx + '-'):
            return cat
    return None

sched = {}
for path in sorted(glob.glob(ROOT + '/logs/live_v3_*.jsonl') +
                   glob.glob(ROOT + '/logs/live_v3_*.jsonl.gz')):
    # only logs that can carry the day's schedule lines (day-3 .. day+1)
    try:
        dstr = path.rsplit('live_v3_', 1)[1][:8]
        if not (DAYTAG >= (datetime.strptime(dstr, '%Y%m%d') -
                           timedelta(days=1)).strftime('%Y%m%d')
                and dstr <= D1.strftime('%Y%m%d')):
            continue
    except ValueError:
        continue
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

exam = {ev: s for ev, s in sched.items()
        if D0.timestamp() <= s < D1.timestamp()}

API = ('https://api.elections.kalshi.com/trade-api/v2/markets/trades'
       '?ticker=%s&limit=1000')

def fetch_csv(tk, t_floor):
    rows, cursor = [], None
    for _ in range(60):
        url = API % tk + (('&cursor=%s' % cursor) if cursor else '')
        try:
            r = json.load(urllib.request.urlopen(url, timeout=20))
        except Exception:
            time.sleep(3)
            return
        for t in r.get('trades', []):
            try:
                ts = datetime.fromisoformat(
                    t['created_time'].replace('Z', '+00:00'))
                rows.append((ts.timestamp(),
                             ts.astimezone(ET).strftime(
                                 '%Y-%m-%d %I:%M:%S %p'),
                             int(t['yes_price']), int(t.get('count') or 0),
                             t.get('taker_side') or ''))
            except (KeyError, ValueError, TypeError):
                continue
        cursor = r.get('cursor')
        if not cursor or (rows and rows[-1][0] < t_floor):
            break
        time.sleep(0.3)
    with open(ROOT + '/analysis/trades/' + tk + '.csv', 'w',
              newline='') as f:
        w = csv.writer(f)
        w.writerow(['ts_et', 'ticker', 'price', 'count', 'taker_side'])
        for _, ts_et, px, ct, side in sorted(rows):
            w.writerow([ts_et, tk, px, ct, side])

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

def recall(cat, a, n, d):
    cell = (RECOG.get(cat + '|h6') or {}).get(pb(a, n, d))
    if cell and cell.get('purity', 0) >= 0.5:
        return cell['top'], True
    return dband(cat, a), False

def simulate(cat, tk, t8, redge):
    tape = load_tape(tk)
    win = [(t, p) for t, p in tape if t8 <= t <= redge]
    if len(win) < 5:
        return None
    pre = [p for t, p in tape if t <= t8]
    anchor = pre[-1] if pre else win[0][1]
    cut = t8 + 2 * 3600
    upto = [(t, p) for t, p in win if t <= cut] or win[:1]
    band, recog = recall(cat, anchor, upto[-1][1] - win[0][1],
                         max(0, anchor - min(p for _, p in upto)))
    if not band:
        return None
    dv = DV2.get(band, {})
    br = band_row(cat, band)
    if not dv or not br:
        return {'band': band, 'dead': True}
    dip = dv.get('dip_p90') or dv.get('dip_p50') or br.get('dip_med') or 3
    close = win[-1][1]
    fill = arm = cast = None
    crossed_up = crossed_dn = refused_violent = False
    window, meds = [], []
    for t, p_ in win:
        window = [(x, q) for x, q in window if x >= t - 1800]
        med = statistics.median([q for _, q in window]) if window else p_
        meds.append((t, med))
        window.append((t, p_))
        net_now = med - anchor
        if net_now >= 5:
            crossed_up = True
        if net_now <= -5 and not crossed_dn:
            crossed_dn = True
            cb, _ = recall(cat, anchor, int(net_now),
                           max(0, anchor - min(q for _, q in window)))
            cbr = band_row(cat, cb) if cb else None
            if cbr and cbr['net_med'] <= -30:
                refused_violent = True
            elif cbr:
                lv = anchor + cbr['net_med'] + 2
                if lv >= 5:
                    cast = int(round(lv))
        if cast is not None and fill is None and not refused_violent \
                and p_ <= cast:
            fill, arm = cast, 'faller_cast'
            break
        if t < max(cut, redge - 2 * 3600):
            continue
        if refused_violent or net_now <= -5:
            continue
        old_m = [m for x, m in meds if x <= t - 1800]
        med_stable = (med >= old_m[-1] - 1) if old_m else True
        level = max(1, int(round(med)) - int(round(dip)))
        if med_stable and p_ <= level:
            fill = level
            arm = 'riser_divot' if net_now >= 5 else 'flat_divot'
            break
    return {'band': band, 'dead': False, 'fill': fill, 'arm': arm,
            'close': close, 'crossed_up': crossed_up,
            'crossed_dn': crossed_dn, 'refused_violent': refused_violent}

pairs = []
skip = {'thin_tape': 0, 'one_leg_file': 0, 'dead_band': 0, 'no_tape': 0}
for ev, s in sorted(exam.items()):
    cat = cat_of(ev)
    legs = sorted({f.rsplit('/', 1)[-1][:-4]
                   for f in glob.glob(ROOT + '/analysis/trades/'
                                      + ev + '-*.csv')})
    if len(legs) < 2:
        skip['one_leg_file' if len(legs) == 1 else 'no_tape'] += 1
        continue
    t8 = s - 8 * 3600
    for tk in legs:
        if len([1 for t, _ in load_tape(tk) if t8 <= t <= s]) < 5:
            fetch_csv(tk, t8 - 86400)
    sims = [simulate(cat, tk, t8, s) for tk in legs]
    if any(x is None for x in sims):
        skip['thin_tape'] += 1
        continue
    if any(x.get('dead') for x in sims):
        skip['dead_band'] += 1
        continue
    pairs.append({'event': ev, 'cat': cat,
                  'legs': dict(zip(legs, sims))})

# [COMBINED-PRIMARY ruling 07-20 PM] pass/fail = combined vs par
# (sub-par <=97 = pass); dual-negative = MASTERY meter, never pass/fail.
def tier(c):
    return '<=93' if c <= 93 else '<=95' if c <= 95 else '<=97' \
        if c <= 97 else '98-100' if c <= 100 else '>100'

CL = lambda: {'pairs': 0, 'duals': 0, 'both_neg': 0, 'comb_le0': 0,
              'pair_deltas': [], 'tiers': defaultdict(int), 'subpar': 0}
overall = defaultdict(CL)
percat = defaultdict(CL)
for pr in pairs:
    sims = list(pr['legs'].values())
    up = any(sm['crossed_up'] for sm in sims)
    dn = any(sm['crossed_dn'] for sm in sims)
    kl = 'mirror' if (up and dn) else 'flat_flat' if not (up or dn) \
        else 'neither'
    for b in (overall[kl], percat[kl + '|' + pr['cat']]):
        b['pairs'] += 1
        if all(sm['fill'] is not None for sm in sims):
            b['duals'] += 1
            comb = sum(sm['fill'] for sm in sims)
            pd = sum(sm['fill'] - sm['close'] for sm in sims)
            b['tiers'][tier(comb)] += 1
            b['pair_deltas'].append(pd)
            if comb < 100:
                b['subpar'] += 1
            if pd <= 0:
                b['comb_le0'] += 1
            if all(sm['fill'] < sm['close'] for sm in sims):
                b['both_neg'] += 1

def line(name, st, bar='comb', joint=False):
    # [CAPTURE STANDARD 07-20 night] the sealed class is judged JOINTLY:
    # COMPLETION (sub-par duals / class games) >= 70 AND QUALITY
    # (sub-par / duals) >= 70 — completion FIRST, the operator's order.
    du = st['duals']
    sp = sum(v for k, v in st['tiers'].items()
             if k in ('<=93', '<=95', '<=97'))
    if joint:
        cr = 100 * sp / max(1, st['pairs'])
        qr = 100 * sp / du if du else 0.0
        v = ('JOINT PASS' if (cr >= 70 and qr >= 70 and du)
             else 'JOINT FAIL (bar 70/70)')
        mast = (100 * st['both_neg'] / du) if du else 0.0
        md = statistics.median(st['pair_deltas']) if du else 0
        return ('- %s: **COMPLETION %d/%d = %.0f%% x QUALITY %d/%d = '
                '%.0f%% -> %s** · tiers %s · MASTERY dual-neg %.0f%% · '
                'medPairD %+d'
                % (name, sp, st['pairs'], cr, sp, du, qr, v,
                   dict(sorted(st['tiers'].items())), mast, md))
    if not du:
        return '- %s: pairs %d duals 0 — NO DUALS' % (name, st['pairs'])
    md = statistics.median(st['pair_deltas'])
    ps = 100 * sp / du
    v = 'PASS' if ps >= 50 else 'FAIL'
    mast = 100 * st['both_neg'] / du
    return ('- %s: pairs %d duals %d (completion %.0f%%) · SUB-PAR(<=97) '
            '%d/%d = %.0f%% -> %s · tiers %s · MASTERY dual-neg %.0f%% '
            '(meter, never pass/fail) · medPairD %+d'
            % (name, st['pairs'], du, 100 * du / max(1, st['pairs']),
               sp, du, ps, v, dict(sorted(st['tiers'].items())), mast, md))

L = ['## PERCLASS %s (era %s) — COMBINED PRIMARY (ruling 07-20 PM): '
     'sub-par(<=97)=pass; dual-negative=mastery meter'
     % (DAYTAG, ERA),
     'slate: %d big-4 events · %d scored pairs · skips %s'
     % (len(exam), len(pairs), dict(skip)),
     line('FLAT-FLAT (SEALED b2f0b670; capture standard)',
          overall['flat_flat'], joint=True),
     line('MIRROR (REFUSE; fader drill on the mastery meter)',
          overall['mirror']),
     line('NEITHER (counted apart)', overall['neither'])]
_spall = sum(sum(v for k2, v in s['tiers'].items()
                 if k2 in ('<=93', '<=95', '<=97'))
             for s in overall.values())
L.append('- COMPLETION (volume drill): sub-par duals %d / %d slate pairs '
         '= %.1f%%' % (_spall, max(1, len(pairs)),
                       100 * _spall / max(1, len(pairs))))
for k in sorted(percat):
    L.append('  ' + line(k, percat[k]))
# [DECAY TRIPWIRE — operator one-liner 07-20 PM; SIMONS rule 6 with a
# bell on it. NEVER silent (the line prints every night: OK / DECAY /
# insufficient-n), NEVER auto-disarm (the flag demands the operator's
# ruling; no config is touched here).]
SEAL_FLOOR = 0.70   # named from the seal's own receipts: sealed at
                    # 100% (7/7 week + 2/2 founding day); the operator's
                    # own example names <70% as the bell. Ruling moves it.
try:
    import sqlite3
    roll_p = art_dir = Path(ROOT).parent / '.claude/perclass_meter'
    art_dir.mkdir(exist_ok=True)
    roll_f = roll_p / 'rolling.json'
    try:
        roll = json.loads(roll_f.read_text())
    except Exception:
        roll = {}
    # [CAPTURE STANDARD 07-20 night] the tripwire covers BOTH axes:
    # rolling-7 COMPLETION (sub-par duals / class games) and QUALITY
    # (sub-par / duals), each vs the 70 floor.
    ffs = overall['flat_flat']
    sp_today = sum(v for k, v in ffs['tiers'].items()
                   if k in ('<=93', '<=95', '<=97'))
    roll[DAYTAG] = {'duals': ffs['duals'], 'subpar': sp_today,
                    'pairs': ffs['pairs']}
    roll = {k: roll[k] for k in sorted(roll)[-14:]}
    roll_f.write_text(json.dumps(roll))
    last7 = [roll[k] for k in sorted(roll)[-7:]]
    du7 = sum(r['duals'] for r in last7)
    sp7 = sum(r['subpar'] for r in last7)
    pr7 = sum(r.get('pairs', 0) for r in last7)
    decay = []
    tws = []
    if pr7 >= 10:
        comp7 = sp7 / pr7
        tws.append('completion7 %d/%d=%.0f%%' % (sp7, pr7, 100 * comp7))
        if comp7 < SEAL_FLOOR:
            decay.append('rolling7 COMPLETION %d/%d = %.0f%% < %.0f%%'
                         % (sp7, pr7, 100 * comp7, 100 * SEAL_FLOOR))
    else:
        tws.append('completion: insufficient n (games %d < 10), said'
                   % pr7)
    if du7 >= 5:
        rate7 = sp7 / du7
        tws.append('quality7 %d/%d=%.0f%%' % (sp7, du7, 100 * rate7))
        if rate7 < SEAL_FLOOR:
            decay.append('rolling7 QUALITY %d/%d = %.0f%% < %.0f%%'
                         % (sp7, du7, 100 * rate7, 100 * SEAL_FLOOR))
    else:
        tws.append('quality: insufficient n (duals %d < 5), said' % du7)
    tw = ' · '.join(tws) + (' (floor %.0f%% both axes)'
                            % (100 * SEAL_FLOOR))
    # backwalk regression: newest wall fails where history passed
    try:
        bw = (Path(ROOT).parent
              / '.claude/backwalk_20260720/BACKWALK_WALLS.md'
              ).read_text()
        import re as _re
        rows = _re.findall(r'## WALL (\d+).*?FLAT-FLAT[^\n]*?SUB-PAR '
                           r'(\d+)/(\d+)', bw, _re.S)
        rows = [(d, int(a), int(b)) for d, a, b in rows if int(b) > 0]
        if len(rows) >= 3:
            prior = rows[:-1]
            newest = rows[-1]
            prior_pass = sum(1 for _, a, b in prior
                             if a / b >= SEAL_FLOOR)
            if (newest[1] / newest[2] < SEAL_FLOOR
                    and prior_pass * 2 >= len(prior)):
                decay.append('backwalk wall %s %d/%d fails where '
                             '%d/%d prior walls passed'
                             % (newest[0], newest[1], newest[2],
                                prior_pass, len(prior)))
    except Exception:
        pass
    L.append('- SEAL-DECAY TRIPWIRE: ' + (('**SEAL-DECAY — RED; '
             'operator ruling required; never auto-disarm** [' +
             ' · '.join(decay) + ']') if decay else tw))
    if decay:
        try:
            con9 = sqlite3.connect(str(Path(ROOT)
                                       / 'state/fund_equity.db'))
            con9.execute('INSERT INTO flags VALUES (?,?,?,?,?)',
                         (time.time(),
                          datetime.now(ET).strftime('%Y%m%d'),
                          'SEAL_DECAY', 'flat_flat_dual_divot',
                          '; '.join(decay)[:200] +
                          ' — operator ruling required'))
            con9.commit()
        except Exception:
            pass
except Exception as _twe:
    L.append('- SEAL-DECAY TRIPWIRE: tripwire error (%s) — never '
             'silent, said plainly' % str(_twe)[:80])

out = '\n'.join(L) + '\n'
art = Path(ROOT).parent / '.claude/perclass_meter'
art.mkdir(exist_ok=True)
(art / ('PERCLASS_%s.md' % DAYTAG)).write_text(out)
np = Path(ROOT).parent / '.claude/live_20260705/NIGHTLY_PASS.md'
try:
    np.write_text(np.read_text() + '\n' + out)
except OSError:
    pass
print(out)
