"""
Cat 8: Formation gate distribution per LESSONS F34 + E12.

For each market: formation_gate_minutes = first_trade_ts - market_open_ts
where market_open_ts comes from g9_metadata.open_time
and first_trade_ts comes from min(g9_trades.created_time) per ticker.

Output:
- Per-tier distribution
- Validates whether bot's uniform 4-hour gate is appropriate per tier
- Anomaly flagging (e.g., negative gates, multi-day gates)
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from collections import defaultdict
import time

print('=' * 100)
print('Cat 8: FORMATION GATE DISTRIBUTION (line release -> first trade gap per market)')
print('Per LESSONS F34 + E12. Bot uses uniform 4-hour gate; this checks whether that fits the data.')
print('=' * 100)
print()

start = time.time()

# Load metadata
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', '_tier', 'open_time']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
md['open_time'] = pd.to_datetime(md['open_time'], errors='coerce', utc=True)
print(f'Metadata loaded: {len(md):,} markets')
print(f'  with open_time: {md["open_time"].notna().sum():,}')
print()

# Stream g9_trades, find min created_time per ticker
pf = pq.ParquetFile('data/durable/g9_trades.parquet')
print(f'g9_trades: {pf.metadata.num_rows:,} rows. Computing min(created_time) per ticker...')
print()

ticker_first_trade = {}  # ticker -> earliest created_time string

rows_processed = 0
for rg_idx in range(pf.metadata.num_row_groups):
    rg = pf.read_row_group(rg_idx, columns=['ticker', 'created_time'])
    df = rg.to_pandas()
    df['ticker'] = df['ticker'].astype(str)
    df['created_time'] = df['created_time'].astype(str)

    # Per-ticker min in this row group
    rg_min = df.groupby('ticker')['created_time'].min()
    for ticker, min_ts in rg_min.items():
        if ticker not in ticker_first_trade or min_ts < ticker_first_trade[ticker]:
            ticker_first_trade[ticker] = min_ts

    rows_processed += len(df)
    if rg_idx % 10 == 0 or rg_idx == pf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        print(f'  RG {rg_idx+1}/{pf.metadata.num_row_groups}, {rows_processed:,} rows, {len(ticker_first_trade):,} tickers, {elapsed:.0f}s')

print()
print(f'Streaming complete in {time.time() - start:.0f}s.')
print()

# Build per-market formation gate
md['first_trade_ts'] = md['ticker'].map(lambda t: ticker_first_trade.get(t))
md['first_trade_ts'] = pd.to_datetime(md['first_trade_ts'], errors='coerce', utc=True)
md['gate_seconds'] = (md['first_trade_ts'] - md['open_time']).dt.total_seconds()
md['gate_minutes'] = md['gate_seconds'] / 60.0
md['gate_hours'] = md['gate_minutes'] / 60.0

valid = md.dropna(subset=['gate_minutes']).copy()
print(f'Markets with both open_time and first_trade_ts: {len(valid):,} of {len(md):,}')
print()

# === Section 1: Overall distribution ===
print('-' * 100)
print('1. OVERALL FORMATION GATE DISTRIBUTION')
print('-' * 100)
print(f'Median: {valid["gate_minutes"].median():.1f} min ({valid["gate_hours"].median():.2f} hr)')
print(f'Mean:   {valid["gate_minutes"].mean():.1f} min')
print(f'p25:    {valid["gate_minutes"].quantile(0.25):.1f} min')
print(f'p75:    {valid["gate_minutes"].quantile(0.75):.1f} min')
print(f'p95:    {valid["gate_minutes"].quantile(0.95):.1f} min')
print(f'Min:    {valid["gate_minutes"].min():.1f} min')
print(f'Max:    {valid["gate_minutes"].max():.1f} min')
n_negative = (valid['gate_minutes'] < 0).sum()
print(f'Negative gates (anomalous): {n_negative}')
n_4hr = (valid['gate_minutes'] <= 240).sum()
print(f'Gates <= 4 hours (bot uniform threshold): {n_4hr} ({n_4hr/len(valid)*100:.1f}%)')

# === Section 2: Per-tier distribution ===
print()
print('-' * 100)
print('2. PER-TIER FORMATION GATE DISTRIBUTION')
print('-' * 100)
for cat in sorted(valid['_tier'].dropna().unique()):
    sub = valid[valid['_tier'] == cat]
    print(f'\n{cat} ({len(sub):,} markets):')
    print(f'  median: {sub["gate_minutes"].median():.1f} min ({sub["gate_hours"].median():.2f} hr)')
    print(f'  p25: {sub["gate_minutes"].quantile(0.25):.1f} min, p75: {sub["gate_minutes"].quantile(0.75):.1f} min, p95: {sub["gate_minutes"].quantile(0.95):.1f} min')
    n_4hr = (sub['gate_minutes'] <= 240).sum()
    print(f'  gates <= 4hr (bot threshold): {n_4hr} ({n_4hr/len(sub)*100:.1f}%)')

# === Section 3: Bucketed distribution ===
print()
print('-' * 100)
print('3. BUCKETED DISTRIBUTION')
print('-' * 100)
buckets = [(0, 5), (5, 30), (30, 60), (60, 120), (120, 240), (240, 480), (480, 1440), (1440, 999999)]
labels = ['<5min', '5-30min', '30-60min', '1-2hr', '2-4hr', '4-8hr', '8-24hr', '>24hr']
print(f'\n{"Bucket":<10} {"Count":>10} {"% of total":>12}')
for (lo, hi), lbl in zip(buckets, labels):
    n = ((valid['gate_minutes'] >= lo) & (valid['gate_minutes'] < hi)).sum()
    print(f'{lbl:<10} {n:>10,} {n/len(valid)*100:>11.1f}%')

# === Section 4: Anomalies (negative gates, multi-day gates) ===
print()
print('-' * 100)
print('4. ANOMALIES')
print('-' * 100)
neg = valid[valid['gate_minutes'] < 0].nsmallest(10, 'gate_minutes')
print(f'\nMost-negative gates (n={len(neg)} of {n_negative} total negatives shown):')
if len(neg) > 0:
    print(neg[['ticker', '_tier', 'open_time', 'first_trade_ts', 'gate_minutes']].to_string(index=False))

multi_day = valid[valid['gate_hours'] > 24]
print(f'\nMulti-day gates (>24hr): {len(multi_day):,}')
if len(multi_day) > 0:
    print(multi_day.nlargest(10, 'gate_hours')[['ticker', '_tier', 'gate_hours']].to_string(index=False))

print()
print('=' * 100)
print(f'END Cat 8 in {time.time() - start:.0f}s — formation gate distribution catalogued.')
print('=' * 100)
