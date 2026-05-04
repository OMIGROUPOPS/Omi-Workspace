"""Compact-binary streaming splitter.

Parses ts via slicing (no strptime), packs each tick as struct '<IBB' (6 bytes).
Buffers per ticker up to a global threshold, flushes to per-ticker .bin files
in append mode. Bounded RAM, ~1.3GB total disk for ~220M ticks.
"""
import sys
import os
import time
import struct
import calendar
from collections import defaultdict

OUT_DIR = '/tmp/validation4/step6_real/ticks'
os.makedirs(OUT_DIR, exist_ok=True)
FLUSH_BYTES = 30_000_000  # ~30MB buffer

per_ticker = defaultdict(list)
buffered = 0
n = 0
matched = 0
flushes = 0
t0 = time.time()
PACK = struct.Struct('<IBB').pack


def flush():
    global per_ticker, buffered, flushes
    flushes += 1
    for tk, packets in per_ticker.items():
        tk_str = tk.decode('ascii', errors='replace')
        path = f'{OUT_DIR}/{tk_str.replace("/","_")}.bin'
        with open(path, 'ab') as f:
            f.write(b''.join(packets))
    per_ticker = defaultdict(list)
    buffered = 0


for line in sys.stdin.buffer:
    n += 1
    if n % 20_000_000 == 0:
        dt = time.time() - t0
        print(f'  {n/1e6:.0f}M lines in {dt:.0f}s ({n/dt/1e6:.1f}M/s) matched={matched} flushes={flushes} tickers_buffered={len(per_ticker)}', flush=True)
    i1 = line.find(b',')
    if i1 < 0:
        continue
    i2 = line.find(b',', i1 + 1)
    if i2 < 0:
        continue
    tk = line[i1 + 1:i2]
    ts_b = line[:i1]
    if len(ts_b) < 19:
        # epoch ts (intra_kalshi uses epoch float)
        try:
            ts = int(float(ts_b))
        except ValueError:
            continue
    else:
        # ISO "2026-04-15 14:00:00"
        try:
            yr = int(ts_b[0:4]); mo = int(ts_b[5:7]); dy = int(ts_b[8:10])
            hr = int(ts_b[11:13]); mn = int(ts_b[14:16]); sc = int(ts_b[17:19])
            ts = calendar.timegm((yr, mo, dy, hr, mn, sc, 0, 0, 0))
        except (ValueError, IndexError):
            continue
    # bid/ask: try cols 3 and 4 (bytes), else 4 and 5 (v3 schema with series col)
    rest = line[i2 + 1:].split(b',')
    try:
        bid = int(rest[0])
        ask = int(rest[1])
        # sanity: if bid > 100, this is probably v3 schema with series in col 3
        if bid > 100 or ask > 100:
            bid = int(rest[1])
            ask = int(rest[2])
    except (ValueError, IndexError):
        continue
    if bid < 0 or bid > 99 or ask < 0 or ask > 100:
        continue
    per_ticker[tk].append(PACK(ts, bid, ask))
    buffered += 6
    matched += 1
    if buffered >= FLUSH_BYTES:
        flush()

if per_ticker:
    flush()

dt = time.time() - t0
print(f'DONE: {n/1e6:.1f}M lines, {matched} matched, {flushes} flushes, {dt:.0f}s ({n/dt/1e6:.2f}M/s)', flush=True)
