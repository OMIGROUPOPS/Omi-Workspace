"""Extract raw per-match facts from pregame-close forward. No simulation."""
import os, struct, json, csv, re
from collections import defaultdict
import sys

sys.path.insert(0, '/tmp/validation4')
old_bp = __import__('old_blueprint')
OLD = old_bp.DEPLOYMENT

TICKS_DIR = '/tmp/validation4/step6_real/ticks'
UNPACK = struct.Struct('<IBB').unpack

with open('/tmp/validation4/step6_real/ticker_meta.json') as f:
    ticker_meta = json.load(f)


def load_ticks(path):
    with open(path, 'rb') as f:
        data = f.read()
    n = len(data) // 6
    ticks = [UNPACK(data[i * 6:i * 6 + 6]) for i in range(n)]
    ticks.sort(key=lambda x: x[0])
    out = []
    prev = None
    for t in ticks:
        if t != prev:
            out.append(t)
            prev = t
    return out


def cat_of(tk):
    if 'KXATPCHALLENGERMATCH' in tk: return 'ATP_CHALL'
    if 'KXWTACHALLENGERMATCH' in tk: return 'WTA_CHALL'
    if 'KXATPMATCH' in tk: return 'ATP_MAIN'
    if 'KXWTAMATCH' in tk: return 'WTA_MAIN'
    return None


def get_event(tk):
    return tk.rsplit('-', 1)[0]


def find_cell(cat, direction, price):
    for ck, cfg in OLD.items():
        if cfg is None:
            continue
        if ck[0] != cat or ck[1] != direction:
            continue
        elo = cfg.get('entry_lo', ck[2])
        ehi = cfg.get('entry_hi', ck[3])
        if elo <= price <= ehi:
            return ck
    return None


def find_pregame_close(ticks):
    """Find first tick where volatility regime changes:
    3c mid move within 30s window, sustained for 2+ windows."""
    if len(ticks) < 10:
        return len(ticks) // 2

    # Scan for volatility jump: compare mid at each tick vs 30s ago
    # Track a rolling window
    window_sec = 30
    volatility_count = 0

    for i in range(1, len(ticks)):
        ts_now = ticks[i][0]
        mid_now = (ticks[i][1] + ticks[i][2]) / 2.0

        # Find tick ~30s ago
        j = i - 1
        while j > 0 and (ts_now - ticks[j][0]) < window_sec:
            j -= 1

        if j == i - 1:
            continue

        mid_then = (ticks[j][1] + ticks[j][2]) / 2.0
        delta = abs(mid_now - mid_then)

        if delta >= 3:
            volatility_count += 1
            if volatility_count >= 2:
                # Sustained volatility — this is match start
                return max(0, j)
        else:
            volatility_count = 0

    # Fallback: 80% of lifetime
    return int(len(ticks) * 0.8)


# ================================================================
# Extract
# ================================================================
print('Extracting match facts...', flush=True)

all_bin = set()
for fn in os.listdir(TICKS_DIR):
    if fn.endswith('.bin'):
        all_bin.add(fn[:-4])

# Group by event to determine leader/underdog
event_tickers = defaultdict(list)
for tk in all_bin:
    cat = cat_of(tk)
    if cat:
        event_tickers[get_event(tk)].append(tk)

rows = []
sample_matches = []

for ev, tks in event_tickers.items():
    if len(tks) < 2:
        continue

    # Load all sides
    sides = []
    for tk in tks:
        bp = os.path.join(TICKS_DIR, tk + '.bin')
        ticks = load_ticks(bp)
        if len(ticks) < 10:
            continue
        cat = cat_of(tk)
        sb = ticker_meta.get(tk, {}).get('settle_bid')
        sides.append((tk, cat, ticks, sb))

    if len(sides) < 2:
        continue

    # Find pregame close for each side
    for s_idx, (tk, cat, ticks, sb) in enumerate(sides):
        pc_idx = find_pregame_close(ticks)

        pc_ts = ticks[pc_idx][0]
        pc_bid = ticks[pc_idx][1]
        pc_ask = ticks[pc_idx][2]
        pc_mid = (pc_bid + pc_ask) / 2.0
        entry_mid = int(round(pc_mid))

        # Determine side: sort all sides by pregame-close mid, highest = leader
        all_mids = []
        for tk2, cat2, ticks2, sb2 in sides:
            pc2 = find_pregame_close(ticks2)
            m2 = (ticks2[pc2][1] + ticks2[pc2][2]) / 2.0
            all_mids.append((tk2, m2))
        all_mids.sort(key=lambda x: x[1], reverse=True)
        if all_mids[0][0] == tk:
            side = 'leader'
        else:
            side = 'underdog'

        # Match result
        if sb is not None:
            match_result = 'win' if sb >= 80 else 'loss'
            settlement = 100 if sb >= 80 else 0
        else:
            match_result = 'unknown'
            settlement = -1

        # Cell assignment
        ck = find_cell(cat, side, entry_mid)
        if ck:
            cell_cat, cell_side, cell_lo, cell_hi = ck
        else:
            cell_cat = 'no_cell'
            cell_side = side
            cell_lo = 0
            cell_hi = 0

        # Live window stats: pregame_close → end
        live_ticks = ticks[pc_idx:]
        if len(live_ticks) < 2:
            continue

        min_bid = 999
        min_bid_ts = 0
        max_bid = -1
        max_bid_ts = 0
        min_mid = 999
        max_mid = -1

        for t in live_ticks:
            ts, bid, ask = t
            mid = (bid + ask) / 2.0
            if bid < min_bid:
                min_bid = bid
                min_bid_ts = ts - pc_ts
            if bid > max_bid:
                max_bid = bid
                max_bid_ts = ts - pc_ts
            if mid < min_mid:
                min_mid = mid
            if mid > max_mid:
                max_mid = mid

        max_dip = pc_mid - min_mid
        max_bounce = max_mid - pc_mid

        rows.append({
            'ticker_id': tk,
            'category': cat,
            'side': side,
            'match_result': match_result,
            'settlement_price': settlement,
            'pregame_close_ts': pc_ts,
            'entry_mid': entry_mid,
            'entry_bid': pc_bid,
            'entry_ask': pc_ask,
            'cell_category': cell_cat,
            'cell_side': cell_side,
            'cell_price_lo': cell_lo,
            'cell_price_hi': cell_hi,
            'match_low_bid': min_bid,
            'match_low_bid_ts': min_bid_ts,
            'match_high_bid': max_bid,
            'match_high_bid_ts': max_bid_ts,
            'match_low_mid': min_mid,
            'match_high_mid': max_mid,
            'max_dip_from_entry': max_dip,
            'max_bounce_from_entry': max_bounce,
            'tick_count_live': len(live_ticks),
        })

        # Collect samples
        if len(sample_matches) < 3:
            sample_matches.append((tk, cat, side, entry_mid, pc_bid, pc_ask,
                                   min_bid, max_bid, min_mid, max_mid,
                                   max_dip, max_bounce, match_result, len(live_ticks)))

# Write CSV
fields = ['ticker_id', 'category', 'side', 'match_result', 'settlement_price',
          'pregame_close_ts', 'entry_mid', 'entry_bid', 'entry_ask',
          'cell_category', 'cell_side', 'cell_price_lo', 'cell_price_hi',
          'match_low_bid', 'match_low_bid_ts', 'match_high_bid', 'match_high_bid_ts',
          'match_low_mid', 'match_high_mid',
          'max_dip_from_entry', 'max_bounce_from_entry', 'tick_count_live']

with open('/tmp/match_facts.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# ================================================================
# SANITY CHECKS
# ================================================================
print()
print('=' * 80)
print('SANITY CHECKS')
print('=' * 80)
print()

# 1. Total ticker count
print('1. Total tickers: %d' % len(rows))
leaders = sum(1 for r in rows if r['side'] == 'leader')
underdogs = sum(1 for r in rows if r['side'] == 'underdog')
print('   Leaders: %d  Underdogs: %d' % (leaders, underdogs))
print()

# 2. How many in active cell
in_cell = sum(1 for r in rows if r['cell_category'] != 'no_cell')
no_cell = len(rows) - in_cell
print('2. In active cell: %d (%.0f%%)  No cell: %d (%.0f%%)' % (
    in_cell, 100 * in_cell / len(rows), no_cell, 100 * no_cell / len(rows)))
print()

# 3. Sample matches
print('3. Sample matches:')
for tk, cat, side, em, pb, pa, lb, hb, lm, hm, dip, bounce, result, tc in sample_matches:
    print('   %s (%s %s) entry_mid=%dc bid=%d ask=%d' % (tk[:50], cat, side, em, pb, pa))
    print('     low_bid=%d high_bid=%d low_mid=%.1f high_mid=%.1f' % (lb, hb, lm, hm))
    print('     dip=%.1fc bounce=%.1fc result=%s ticks=%d' % (dip, bounce, result, tc))
    print()

# 4. Distribution of max_bounce
bounces = [r['max_bounce_from_entry'] for r in rows if r['max_bounce_from_entry'] is not None]
bounces.sort()
n = len(bounces)
print('4. max_bounce_from_entry distribution (N=%d):' % n)
print('   min=%.1f p10=%.1f p25=%.1f p50=%.1f p75=%.1f p90=%.1f max=%.1f' % (
    bounces[0], bounces[n // 10], bounces[n // 4], bounces[n // 2],
    bounces[3 * n // 4], bounces[9 * n // 10], bounces[-1]))
print()

# 5. Distribution of max_dip
dips = [r['max_dip_from_entry'] for r in rows if r['max_dip_from_entry'] is not None]
dips.sort()
n = len(dips)
print('5. max_dip_from_entry distribution (N=%d):' % n)
print('   min=%.1f p10=%.1f p25=%.1f p50=%.1f p75=%.1f p90=%.1f max=%.1f' % (
    dips[0], dips[n // 10], dips[n // 4], dips[n // 2],
    dips[3 * n // 4], dips[9 * n // 10], dips[-1]))

print()
print('CSV written: /tmp/match_facts.csv (%d rows)' % len(rows))
print('Done.')
