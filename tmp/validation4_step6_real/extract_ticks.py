"""Stream BBO log, extract raw ticks for 1628 trajectory tickers, write to per-ticker pickles."""
import os
import pickle
import time
import sys
from collections import defaultdict

TICKERS_PATH = '/tmp/validation4/step6_real/tickers.txt'
OUT_DIR = '/tmp/validation4/step6_real/ticks'
os.makedirs(OUT_DIR, exist_ok=True)

# Sources to stream
SOURCES = [
    ('/tmp/bbo_log_v4.csv',       'v4',      dict(ts_col=0, ticker_col=1, bid_col=2, ask_col=3, has_header=True)),
    ('/tmp/bbo_log_v3.csv',       'v3',      dict(ts_col=0, ticker_col=1, bid_col=3, ask_col=4, has_header=True)),
    ('/tmp/tennis_bbo_all.csv',   'tbba',    dict(ts_col=0, ticker_col=1, bid_col=3, ask_col=4, has_header=True)),
]
for d in [5, 6, 7, 8]:
    SOURCES.append((f'/root/Omi-Workspace/arb-executor/intra_kalshi/data/bbo_log_202603{d:02d}.csv',
                    f'ik{d}', dict(ts_col=0, ticker_col=1, bid_col=3, ask_col=4, has_header=True)))

with open(TICKERS_PATH) as f:
    target = set(line.strip() for line in f if line.strip())
print(f'Target tickers: {len(target)}')

import datetime
import calendar


def parse_ts(s):
    s = s.strip()
    if s.startswith('2026') or s.startswith('2025'):
        try:
            dt = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            return calendar.timegm(dt.timetuple()) + 4 * 3600  # ET->UTC approx
        except ValueError:
            return None
    try:
        return int(float(s))
    except ValueError:
        return None


per_ticker = defaultdict(list)

for path, tag, cfg in SOURCES:
    if not os.path.exists(path):
        print(f'[skip] {path} not found')
        continue
    t0 = time.time()
    rows = 0
    matched = 0
    ts_col, tk_col = cfg['ts_col'], cfg['ticker_col']
    bid_col, ask_col = cfg['bid_col'], cfg['ask_col']
    has_hdr = cfg['has_header']
    with open(path, 'r', errors='replace') as f:
        if has_hdr:
            next(f, None)
        for line in f:
            rows += 1
            if rows % 20_000_000 == 0:
                dt = time.time() - t0
                print(f'  [{tag}] {rows/1e6:.0f}M rows in {dt:.0f}s ({rows/dt/1e6:.1f}M/s) — {matched} matched, {len(per_ticker)} tickers so far')
            parts = line.rstrip('\n').split(',')
            if len(parts) <= tk_col:
                continue
            tk = parts[tk_col]
            if tk not in target:
                continue
            ts = parse_ts(parts[ts_col])
            if ts is None:
                continue
            try:
                bid = int(parts[bid_col])
                ask = int(parts[ask_col])
            except (ValueError, IndexError):
                continue
            per_ticker[tk].append((ts, bid, ask))
            matched += 1
    dt = time.time() - t0
    print(f'[{tag}] done: {rows/1e6:.0f}M rows, {matched} matched, {dt:.0f}s ({rows/dt/1e6:.1f}M rows/s)')

print(f'\nTotal tickers with any tick: {len(per_ticker)}')
print(f'Total ticks extracted: {sum(len(v) for v in per_ticker.values())}')

# Sort and pickle per ticker
t0 = time.time()
n = 0
for tk, ticks in per_ticker.items():
    ticks.sort(key=lambda x: x[0])
    out_path = f'{OUT_DIR}/{tk.replace("/", "_")}.pkl'
    with open(out_path, 'wb') as f:
        pickle.dump(ticks, f)
    n += 1
    if n % 500 == 0:
        print(f'  wrote {n}/{len(per_ticker)} in {time.time()-t0:.0f}s')
print(f'Wrote {n} per-ticker pickles in {time.time()-t0:.0f}s')

# Summary
with open('/tmp/validation4/step6_real/extract_summary.txt', 'w') as f:
    f.write(f'Tickers target: {len(target)}\n')
    f.write(f'Tickers matched: {len(per_ticker)}\n')
    f.write(f'Total ticks: {sum(len(v) for v in per_ticker.values())}\n')
    missed = target - set(per_ticker.keys())
    f.write(f'Missed tickers ({len(missed)}):\n')
    for m in sorted(missed)[:50]:
        f.write(f'  {m}\n')
