"""
Cat 9: Combined-trade-price distortion events.
Walk g9_trades per market (streaming row-groups), bin to per-minute, compute (yes_close + no_close)
per minute, flag minutes where combined > $1.00 + $0.01 tolerance.

Output: ASCII report:
  - Per-tier distortion event count + rate (events / total minutes)
  - Per-stage (premarket vs in_match vs settlement_zone) breakdown if metadata available
  - Magnitude distribution
  - Top 20 markets with most distortion events
  - Anchor: any specific minute where combined far exceeded $1.00

Per LESSONS F32 + B23. C28 streaming discipline mandatory (33.7M trade rows).
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from collections import defaultdict
import time

print('=' * 100)
print('Cat 9: COMBINED-TRADE-PRICE DISTORTION EVENTS')
print('Per LESSONS F32 + B23. Foundation: g9_trades.parquet (T28 ea84e74, 33.7M rows).')
print('Definition: per-market per-minute, flag minutes where (last_yes_price + last_no_price) > $1.01.')
print('=' * 100)
print()

start = time.time()

# Load metadata for tier classification (small file)
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', 'category', 'open_time']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
ticker_to_category = dict(zip(md['ticker'], md['category']))
print(f'Metadata loaded: {len(md):,} markets')
print()

# Stream g9_trades by row-group; for each market, build per-minute close series for yes and no
pf = pq.ParquetFile('data/durable/g9_trades.parquet')
print(f'g9_trades: {pf.metadata.num_rows:,} rows in {pf.metadata.num_row_groups} row groups. Streaming...')
print()

# Accumulate per-(ticker, minute) the latest yes_price and no_price observation, separately
# A trade with taker_side='yes' tells us a yes contract changed hands at yes_price_dollars
# but the relationship to no_price is also given via no_price_dollars per row
# We use yes_price_dollars and no_price_dollars from the trade row directly (every row has both)

# Per-(ticker, minute) accumulators: latest yes_price and no_price observed
# Using nested dict to manage memory; flush to per-ticker minute-series only after each row group
minute_yes = defaultdict(dict)  # {ticker: {minute_ts_str: latest_yes_price}}
minute_no = defaultdict(dict)   # {ticker: {minute_ts_str: latest_no_price}}

rows_processed = 0
for rg_idx in range(pf.metadata.num_row_groups):
    rg = pf.read_row_group(rg_idx, columns=['ticker', 'created_time', 'yes_price_dollars', 'no_price_dollars'])
    df = rg.to_pandas()
    # Convert created_time to minute bucket as string
    df['ticker'] = df['ticker'].astype(str)
    df['ts_minute'] = df['created_time'].astype(str).str[:16]  # 'YYYY-MM-DDTHH:MM' truncation

    # For each row, update the per-(ticker, minute) latest price
    for ticker, ts_min, yp, np_ in zip(df['ticker'], df['ts_minute'], df['yes_price_dollars'], df['no_price_dollars']):
        minute_yes[ticker][ts_min] = float(yp) if pd.notna(yp) else minute_yes[ticker].get(ts_min)
        minute_no[ticker][ts_min] = float(np_) if pd.notna(np_) else minute_no[ticker].get(ts_min)

    rows_processed += len(df)
    if rg_idx % 10 == 0 or rg_idx == pf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        print(f'  RG {rg_idx+1}/{pf.metadata.num_row_groups}, processed {rows_processed:,} rows, {len(minute_yes):,} markets seen, {elapsed:.0f}s elapsed')

print()
print(f'Streaming pass complete in {time.time() - start:.0f}s. Now scanning for distortions...')
print()

# For each market, identify minutes where both yes and no prices are present and sum > $1.01
distortion_events = []  # list of (ticker, ts_minute, yes_price, no_price, combined, magnitude)
distortion_count_per_ticker = defaultdict(int)
total_minutes_per_ticker = defaultdict(int)

for ticker in minute_yes:
    for ts_min in minute_yes[ticker]:
        yp = minute_yes[ticker][ts_min]
        np_ = minute_no[ticker].get(ts_min)
        if yp is None or np_ is None:
            continue
        total_minutes_per_ticker[ticker] += 1
        combined = yp + np_
        if combined > 1.01:
            magnitude = combined - 1.0
            distortion_events.append((ticker, ts_min, yp, np_, combined, magnitude))
            distortion_count_per_ticker[ticker] += 1

print(f'Total distortion events: {len(distortion_events):,}')
print(f'Markets with at least 1 distortion: {len(distortion_count_per_ticker):,} of {len(minute_yes):,}')
print()

# === Section 1: Per-tier summary ===
print('-' * 100)
print('1. PER-TIER DISTORTION SUMMARY')
print('-' * 100)
tier_events = defaultdict(int)
tier_minutes = defaultdict(int)
for ticker, count in distortion_count_per_ticker.items():
    cat = ticker_to_category.get(ticker, 'UNKNOWN')
    tier_events[cat] += count
for ticker, count in total_minutes_per_ticker.items():
    cat = ticker_to_category.get(ticker, 'UNKNOWN')
    tier_minutes[cat] += count

print(f'\n{"Tier":<20} {"Distortions":>12} {"Total min":>12} {"Rate (per 1k min)":>20}')
for cat in sorted(set(list(tier_events.keys()) + list(tier_minutes.keys()))):
    n_dist = tier_events[cat]
    n_min = tier_minutes[cat]
    rate = (n_dist / n_min * 1000) if n_min > 0 else 0
    print(f'{cat:<20} {n_dist:>12,} {n_min:>12,} {rate:>20.3f}')

# === Section 2: Magnitude distribution ===
print()
print('-' * 100)
print('2. MAGNITUDE DISTRIBUTION (how much combined exceeds $1.00)')
print('-' * 100)
if distortion_events:
    magnitudes = [e[5] for e in distortion_events]
    mag_arr = np.array(magnitudes)
    print(f'  Count: {len(mag_arr):,}')
    print(f'  Min:   ${mag_arr.min():.4f}')
    print(f'  p25:   ${np.percentile(mag_arr, 25):.4f}')
    print(f'  Median: ${np.percentile(mag_arr, 50):.4f}')
    print(f'  p75:   ${np.percentile(mag_arr, 75):.4f}')
    print(f'  p95:   ${np.percentile(mag_arr, 95):.4f}')
    print(f'  Max:   ${mag_arr.max():.4f}')
    print()
    print(f'  Buckets:')
    for lo, hi in [(0.01, 0.02), (0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 1.0)]:
        n = ((mag_arr >= lo) & (mag_arr < hi)).sum()
        print(f'    ${lo:.2f}-${hi:.2f}: {n:>8,} ({n/len(mag_arr)*100:.1f}%)')

# === Section 3: Top 20 markets by distortion count ===
print()
print('-' * 100)
print('3. TOP 20 MARKETS BY DISTORTION EVENT COUNT')
print('-' * 100)
top_markets = sorted(distortion_count_per_ticker.items(), key=lambda x: -x[1])[:20]
print(f'\n{"Ticker":<60} {"Tier":<15} {"Distortions":>12} {"Total min":>12} {"Rate":>10}')
for ticker, count in top_markets:
    cat = ticker_to_category.get(ticker, 'UNKNOWN')
    n_min = total_minutes_per_ticker[ticker]
    rate = (count / n_min * 1000) if n_min > 0 else 0
    print(f'{ticker:<60} {cat:<15} {count:>12,} {n_min:>12,} {rate:>10.2f}')

# === Section 4: Top 20 single-event extreme distortions ===
print()
print('-' * 100)
print('4. TOP 20 SINGLE-MINUTE EXTREME DISTORTIONS (largest combined price)')
print('-' * 100)
top_events = sorted(distortion_events, key=lambda e: -e[4])[:20]
print(f'\n{"Ticker":<55} {"Minute (UTC)":<18} {"yes":>8} {"no":>8} {"combined":>10} {"magnitude":>10}')
for ticker, ts_min, yp, np_, combined, mag in top_events:
    print(f'{ticker:<55} {ts_min:<18} ${yp:>7.4f} ${np_:>7.4f} ${combined:>9.4f} ${mag:>9.4f}')

# === Persist preview parquet for Cat 10 (and any future analysis) ===
import os
os.makedirs('/tmp/diagnostics_session_8', exist_ok=True)
ev_df = pd.DataFrame(distortion_events, columns=['ticker', 'ts_minute', 'yes_price', 'no_price', 'combined', 'magnitude'])
ev_df.to_parquet('/tmp/diagnostics_session_8/distortion_events_cat9_preview.parquet')
print()
print(f'Persisted /tmp/diagnostics_session_8/distortion_events_cat9_preview.parquet ({len(ev_df):,} rows)')

print()
print('=' * 100)
print(f'END Cat 9 in {time.time() - start:.0f}s — distortion events catalogued.')
print('=' * 100)
