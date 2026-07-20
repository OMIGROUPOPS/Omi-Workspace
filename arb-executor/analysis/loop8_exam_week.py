#!/usr/bin/env python3
# LOOP 8 — THE WEEK WIDEN under the SPLIT GAUGES (operator ruling 07-20:
# "split the gauges" — each pair class judged on ITS OWN bar):
#   FLAT-FLAT pairs -> dual-divot entries off the catch tables, both legs
#       fished below their anchors; gauge = BOTH-LEGS-NEGATIVE rate vs
#       the 75% bar (the Vukic/Gea crop).
#   MIRROR pairs (one leg risen, sibling weakened — the seesaw crop) ->
#       the COMBINED gauge: pair combined-delta <= 0 share + sub-par
#       combined cost; PASS law = duals >= 10 AND median pair delta < 0
#       (loop-5 frame; loop-5 holdout ran 73% on this gauge).
# Model = lap-5 converged arms with the ruling's mirror amendment:
#   riser (med-anchor >= +5): divot-during-climb, level = med - dip_p90,
#       median-not-falling guard, armed final 2h (the proven arm).
#   weakening (med-anchor <= -5): CALLED EARLY at first crossing —
#       recognition re-call names the destination band; STATIC cast at
#       anchor + net_med(called band) + 2c (shallow-of-destination,
#       explicitly not-too-deep). VIOLENT-FALLER REFUSE HOLDS
#       (net_med <= -30). Cast placed at the crossing (early), not
#       final-2h gated — that is its point.
#   flat: dual-divot, level = med - dip_p90, guard + final-2h.
# Dead bands (thin cat / no band / no divot row) refused and counted
# apart. Honest denominators BY ERA:
#   sched < JUL18 00:00 ET = FIT-ERA (band map + recognition fit through
#       JUL17; counted, NEVER scored — seen games).
#   JUL18+ = UNSEEN by every fitted object (divot v2 read spring
#       spectrum events only; store CONTAINS live-cron prints post-JUL17
#       but no fit consumed them — contained-in != trained-on, named).
#   Unseen splits VIRGIN (sched < 07-19 12:15 ET) vs SELECTION-WINDOW
#       (the 24h exam window laps 1-5 tuned on — model selection tape).
# Missing REST tape for unseen events is fetched from the public
# /markets/trades endpoint into analysis/trades/ (same CSV format),
# 429-disciplined; fetches counted.
import csv, glob, gzip, json, statistics, time, urllib.request
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
UNSEEN_EDGE = datetime(2026, 7, 18, 0, 0, tzinfo=ET).timestamp()
SELECT_EDGE = datetime(2026, 7, 19, 12, 15, tzinfo=ET).timestamp()
LOGS = sorted(glob.glob(ROOT + '/logs/live_v3_202607*.jsonl') +
              glob.glob(ROOT + '/logs/live_v3_202607*.jsonl.gz'))

def cat_of(event):
    for pfx, cat in BIG4.items():
        if event.startswith(pfx + '-'):
            return cat
    return None

# ---- schedules: LAST schedule_match line per event wins ----------------
sched = {}
for path in LOGS:
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

week = {ev: s for ev, s in sched.items() if NOW - 7 * 86400 <= s <= NOW}
seen_era = {ev: s for ev, s in week.items() if s < UNSEEN_EDGE}
exam = {ev: s for ev, s in week.items() if s >= UNSEEN_EDGE}

# ---- tape (fetch-if-missing for unseen events) --------------------------
FETCHED = {'tickers': 0, 'rows': 0, 'errors': 0}
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
            FETCHED['errors'] += 1
            return False
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
    with open(ROOT + '/analysis/trades/' + tk + '.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ts_et', 'ticker', 'price', 'count', 'taker_side'])
        for _, ts_et, px, ct, side in sorted(rows):
            w.writerow([ts_et, tk, px, ct, side])
    FETCHED['tickers'] += 1
    FETCHED['rows'] += len(rows)
    return True

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
    n_sofar = upto[-1][1] - win[0][1]
    d_sofar = max(0, anchor - min(p for _, p in upto))
    band, recog = recall(cat, anchor, n_sofar, d_sofar)
    if not band:
        return None
    dv = DV2.get(band, {})
    br = band_row(cat, band)
    if not dv or not br:
        return {'band': band, 'dead': True, 'anchor': anchor, 'recog': recog}
    dip = dv.get('dip_p90') or dv.get('dip_p50') or br.get('dip_med') or 3
    close = win[-1][1]
    fill = arm = None
    crossed_up = crossed_dn = False
    cast = None            # (level,) once the weakening call is made
    refused_violent = False
    window, meds = [], []
    for t, p_ in win:
        window = [(x, q) for x, q in window if x >= t - 1800]
        med = statistics.median([q for _, q in window]) if window else p_
        meds.append((t, med))
        window.append((t, p_))
        net_now = med - anchor
        if net_now >= 5:
            crossed_up = True
        # ---- weakening: the EARLY CALL fires at first -5 crossing ----
        if net_now <= -5 and not crossed_dn:
            crossed_dn = True
            d_now = max(0, anchor - min(q for _, q in window))
            cb, _ = recall(cat, anchor, int(net_now), d_now)
            cbr = band_row(cat, cb) if cb else None
            if not cbr:
                pass                       # dead call: leg keeps flat arm
            elif cbr['net_med'] <= -30:
                refused_violent = True     # the violent-faller law holds
            else:
                lv = anchor + cbr['net_med'] + 2
                if lv >= 5:
                    cast = int(round(lv))
        if cast is not None and fill is None and not refused_violent \
                and p_ <= cast:
            fill, arm = cast, 'faller_cast'
            break
        # ---- divot arms (riser / flat): final 2h + stability guard ----
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
    return {'band': band, 'anchor': anchor, 'recog': recog, 'dead': False,
            'fill': fill, 'arm': arm, 'close': close,
            'crossed_up': crossed_up, 'crossed_dn': crossed_dn,
            'refused_violent': refused_violent, 'n_prints': len(win)}

# ---- walk the unseen crop ------------------------------------------------
pairs = []
skip = {'thin_tape': 0, 'one_leg_file': 0, 'no_band': 0, 'dead_band': 0,
        'no_tape_unfetchable': 0}
for ev, s in sorted(exam.items()):
    cat = cat_of(ev)
    legs = sorted({f.rsplit('/', 1)[-1][:-4]
                   for f in glob.glob(ROOT + '/analysis/trades/' + ev + '-*.csv')})
    if len(legs) < 2:
        # try the public tape for both legs via event markets naming:
        # we only know leg tickers from files; without either file we
        # cannot name the legs -> counted, not guessed.
        if len(legs) == 1:
            skip['one_leg_file'] += 1
        else:
            skip['no_tape_unfetchable'] += 1
        continue
    t8 = s - 8 * 3600
    for tk in legs:
        tape_rows = load_tape(tk)
        if len([1 for t, _ in tape_rows if t8 <= t <= s]) < 5:
            fetch_csv(tk, t8 - 86400)
    sims = [simulate(cat, tk, t8, s) for tk in legs]
    if any(x is None for x in sims):
        skip['thin_tape'] += 1
        continue
    if any(x.get('dead') for x in sims):
        skip['dead_band'] += 1
        continue
    pairs.append({'event': ev, 'cat': cat, 'sched': s,
                  'era': 'selection' if s >= SELECT_EDGE else 'virgin',
                  'legs': dict(zip(legs, sims))})

# ---- classing + the two gauges ------------------------------------------
def tier(c):
    return '<=93' if c <= 93 else '94-97' if c <= 97 else '98-100' \
        if c <= 100 else '>100'

def pair_class(sims):
    up = any(sm['crossed_up'] for sm in sims)
    dn = any(sm['crossed_dn'] for sm in sims)
    if not up and not dn:
        return 'flat_flat'
    if up and dn:
        return 'mirror'
    return 'neither'

CL = lambda: {'pairs': 0, 'duals': 0, 'both_neg': 0, 'comb_le0': 0,
              'pair_deltas': [], 'tiers': defaultdict(int), 'subpar': 0,
              'refused_violent': 0}
overall = defaultdict(CL)        # class -> stats
percat = defaultdict(CL)         # class|cat
perband = defaultdict(lambda: {'legs': 0, 'fills': 0, 'neg': 0,
                               'deltas': []})
perarm = defaultdict(lambda: {'legs': 0, 'fills': 0, 'neg': 0, 'deltas': []})
perera = defaultdict(CL)         # class|era
n_recog = n_default = 0
for pr in pairs:
    sims = list(pr['legs'].values())
    kl = pair_class(sims)
    buckets = [overall[kl], percat[kl + '|' + pr['cat']],
               perera[kl + '|' + pr['era']]]
    for b in buckets:
        b['pairs'] += 1
        b['refused_violent'] += sum(1 for sm in sims
                                    if sm['refused_violent'])
    for sm in sims:
        n_recog += 1 if sm['recog'] else 0
        n_default += 0 if sm['recog'] else 1
        st = perband[sm['band']]
        st['legs'] += 1
        ar = perarm[sm['arm'] or ('refused_violent'
                                  if sm['refused_violent'] else 'no_fill')]
        ar['legs'] += 1
        if sm['fill'] is not None:
            st['fills'] += 1
            ar['fills'] += 1
            dl = sm['fill'] - sm['close']
            st['deltas'].append(dl)
            ar['deltas'].append(dl)
            if dl < 0:
                st['neg'] += 1
                ar['neg'] += 1
    if all(sm['fill'] is not None for sm in sims):
        combined = sum(sm['fill'] for sm in sims)
        pdelta = sum(sm['fill'] - sm['close'] for sm in sims)
        for b in buckets:
            b['duals'] += 1
            b['tiers'][tier(combined)] += 1
            b['pair_deltas'].append(pdelta)
            if combined < 100:
                b['subpar'] += 1
            if pdelta <= 0:
                b['comb_le0'] += 1
            if all(sm['fill'] < sm['close'] for sm in sims):
                b['both_neg'] += 1

# ---- report --------------------------------------------------------------
def clsline(name, st, bar):
    du = st['duals']
    if not du:
        return '- %s: pairs %d duals 0 — NO DUALS' % (name, st['pairs'])
    bn = 100 * st['both_neg'] / du
    c0 = 100 * st['comb_le0'] / du
    sp = 100 * st['subpar'] / du
    md = statistics.median(st['pair_deltas'])
    if bar == 'flat':
        v = 'CLEARS 75%' if bn >= 75 else 'BELOW 75%'
        g = 'both-neg %.0f%% -> **%s**' % (bn, v)
    else:
        v = ('PASS' if du >= 10 and md < 0 else 'FAIL'
             ) + ' (duals>=10 & medPairD<0)'
        g = ('combD<=0 %.0f%% (loop-5 ref 73%%) · medPairD %+d · '
             'sub-par %.0f%% -> **%s**' % (c0, md, sp, v))
    return ('- %s: pairs %d duals %d (%.0f%%) · %s · tiers %s · '
            'violent-refused legs %d'
            % (name, st['pairs'], du, 100 * du / max(1, st['pairs']), g,
               dict(sorted(st['tiers'].items())), st['refused_violent']))

L = ['# LOOP 8 — THE WEEK WIDEN under the SPLIT GAUGES '
     '(window %s -> %s ET; UNSEEN = JUL18+ only)'
     % (datetime.fromtimestamp(NOW - 7 * 86400, ET).strftime('%m-%d %I:%M %p'),
        datetime.fromtimestamp(NOW, ET).strftime('%m-%d %I:%M %p')),
     'model: riser=divot-during-climb (p90, final-2h, guard) · weakening='
     'EARLY CALL -> dest cast anchor+net_med+2 (violent net_med<=-30 '
     'REFUSED) · flat=dual divot p90 · W1 only · floor/W1/holdout laws '
     'stand',
     'era census: week events %d = FIT-ERA (seen, JUL13-17, EXCLUDED) %d '
     '+ UNSEEN (JUL18+) %d; scored pairs %d; skips %s; tape fetched %d '
     'tickers / %d rows / %d errors; store contains post-JUL17 live-cron '
     'prints but NO fit consumed them (contained-in != trained-on)'
     % (len(week), len(seen_era), len(exam), len(pairs), dict(skip),
        FETCHED['tickers'], FETCHED['rows'], FETCHED['errors']),
     'band calls: recognition %d / default-flat %d' % (n_recog, n_default),
     '', '## THE TWO GAUGES, per class']
L.append(clsline('FLAT-FLAT (75%% both-neg bar)', overall['flat_flat'],
                 'flat'))
L.append(clsline('MIRROR (combined gauge)', overall['mirror'], 'comb'))
L.append(clsline('NEITHER (counted apart, no seal claim)',
                 overall['neither'], 'comb'))
L.append('')
L.append('## per class x era (virgin = pre-07/19-12:15, never touched by '
         'lap selection; selection = the 24h-exam window laps tuned on)')
for k in sorted(perera):
    L.append(clsline(k, perera[k], 'flat' if k.startswith('flat') else 'comb'))
L.append('')
L.append('## per class x cat')
for k in sorted(percat):
    L.append(clsline(k, percat[k], 'flat' if k.startswith('flat') else 'comb'))
L.append('')
L.append('## per ARM (legs/fills/neg-share/med-delta)')
for a, st in sorted(perarm.items(), key=lambda kv: -kv[1]['legs']):
    md = statistics.median(st['deltas']) if st['deltas'] else None
    L.append('- %s: legs %d fills %d neg %.0f%% medD %s'
             % (a, st['legs'], st['fills'],
                100 * st['neg'] / st['fills'] if st['fills'] else 0.0, md))
L.append('')
L.append('## per band (legs/fills/neg-share/med-delta)')
for band, st in sorted(perband.items(), key=lambda kv: -kv[1]['legs']):
    md = statistics.median(st['deltas']) if st['deltas'] else None
    L.append('- %s: legs %d fills %d neg %.0f%% medD %s'
             % (band, st['legs'], st['fills'],
                100 * st['neg'] / st['fills'] if st['fills'] else 0.0, md))
L.append('')
L.append('Instrument residue, named: level-fill (no queue/FIFO realism); '
         'kalshi_schedule_primary right edges carry the session-clock '
         'class on unblessed events; recognition h6 table consulted '
         'mid-window for the early call (fit horizon was T-6h — declared '
         'stretch); dest casts carry no reach-support filter (floor 5c '
         'only); ITF excluded (big-4 tables).')
out = '\n'.join(L) + '\n'
open('/tmp/WEEK_WIDEN.md', 'w').write(out)
json.dump({'pairs': pairs}, open('/tmp/week_widen_pairs.json', 'w'),
          default=str)
print(out)
