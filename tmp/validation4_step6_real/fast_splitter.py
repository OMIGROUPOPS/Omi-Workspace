"""Fast stdin splitter: minimal string work, bucket raw lines by ticker.

Designed for throughput — no datetime parsing, no int conversion. Just find the
ticker substring and append full line to per-ticker list. Parsing happens at
simulation time.
"""
import sys
import os
import pickle
import time
from collections import defaultdict

OUT_DIR = '/tmp/validation4/step6_real/ticks'
os.makedirs(OUT_DIR, exist_ok=True)

per_ticker = defaultdict(list)
t0 = time.time()
n = 0
# Format: ts,ticker,bid,ask,spread (v4, tbba)
# or:    ts,ticker,series,bid,ask,spread (v3)
# We keep the entire line — parse later.

# Use buffered read for speed
for line in sys.stdin.buffer:
    n += 1
    # Find first 2 commas for ticker extraction
    i1 = line.find(b',')
    if i1 < 0:
        continue
    i2 = line.find(b',', i1 + 1)
    if i2 < 0:
        continue
    tk = line[i1 + 1:i2]  # bytes
    per_ticker[tk].append(line)
    if n % 20_000_000 == 0:
        dt_ = time.time() - t0
        print(f'  {n/1e6:.0f}M rows bucketed in {dt_:.0f}s ({n/dt_/1e6:.1f}M/s), tickers={len(per_ticker)}', flush=True)

dt = time.time() - t0
print(f'DONE bucketing: {n/1e6:.1f}M rows in {dt:.0f}s, {len(per_ticker)} tickers, mem rows total={sum(len(v) for v in per_ticker.values())}', flush=True)

# Write raw lines per ticker (append-safe via mode='ab')
t0 = time.time()
for i, (tk, lines) in enumerate(per_ticker.items()):
    tk_str = tk.decode('ascii', errors='replace')
    out_path = f'{OUT_DIR}/{tk_str.replace("/","_")}.raw'
    with open(out_path, 'ab') as f:
        for ln in lines:
            f.write(ln)
    if (i + 1) % 500 == 0:
        print(f'  wrote {i+1}/{len(per_ticker)} in {time.time()-t0:.0f}s', flush=True)
print(f'Wrote {len(per_ticker)} .raw files in {time.time()-t0:.0f}s', flush=True)
