"""
Cat 6: Per-market premarket trajectory width (bilateral feasibility per LESSONS B23).

For each market with sufficient premarket data:
- Define premarket = pre-match-start (assume open_time → close_time/2 as proxy if needed)
- max_yes_close - min_yes_close = trajectory range
- Time-in-each-third (lower / mid / upper third of range)
- Low-touch-then-high-touch sequencing test (did price hit low first, then high, or reverse)
- Time gap between low-touch and high-touch (bilateral fill timing)

Streams g9_candles per row group, filtering to premarket minutes per market via metadata.

Per LESSONS B23 + E18: bilateral capture requires trajectory width >= 10c minimum.
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from collections import defaultdict
import time

print('=' * 100)
print('Cat 6: PER-MARKET PREMARKET TRAJECTORY WIDTH')
print('Per LESSONS B23 + E18. Foundation: g9_candles + g9_metadata.')
print('Bilateral feasibility: trajectory width >= 10c minimum required for paired YES+NO maker capture.')
print('=' * 100)
print()

start = time.time()

# Load metadata for premarket windows
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', '_tier', 'open_time', 'close_time']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
md['open_time'] = pd.to_datetime(md['open_time'], errors='coerce', utc=True)
md['close_time'] = pd.to_datetime(md['close_time'], errors='coerce', utc=True)
print(f'Metadata: {len(md):,} markets, {md["open_time"].notna().sum():,} with open_time')
print()

# Build ticker → (open_ts, close_ts) lookup
ticker_window = {}
for _, row in md.iterrows():
    if pd.notna(row['open_time']) and pd.notna(row['close_time']):
        ticker_window[row['ticker']] = (row['open_time'], row['close_time'])
print(f'Tickers with both open/close: {len(ticker_window):,}')
print()

# Stream g9_candles, accumulate per-market yes_close values within premarket window
# Premarket proxy: from open_time to ~match_start. We don't know exact match_start; use first 50% of open->close window as a rough proxy
# (in_match dominates the second half typically).
# Actually safer: just compute trajectory across ALL minutes but stratify by whether it's first-half (premarket-like) vs second-half (in_match-like)

# To bound memory, accumulate per-ticker: list of (ts, yes_close) tuples, then process at end
ticker_yes_series = defaultdict(list)  # ticker -> [(ts_minute, yes_close), ...]

cf = pq.ParquetFile('data/durable/g9_candles.parquet')
print(f'g9_candles: {cf.metadata.num_rows:,} rows in {cf.metadata.num_row_groups} row groups. Streaming...')
print()

# Probe column names from candles schema
sample_cols = [f.name for f in cf.schema_arrow]
print(f'Candles columns: {sample_cols}')
yes_close_col = 'price_close' if 'price_close' in sample_cols else 'yes_ask_close' if 'yes_ask_close' in sample_cols else None
ts_col = 'end_period_ts' if 'end_period_ts' in sample_cols else 'period_end' if 'period_end' in sample_cols else 'ts_minute' if 'ts_minute' in sample_cols else None
ticker_col = 'ticker'

if not yes_close_col or not ts_col:
    print(f'ABORT: cannot locate yes_close or ts column. Have yes={yes_close_col}, ts={ts_col}')
    raise SystemExit(1)

print(f'Using yes_close_col={yes_close_col}, ts_col={ts_col}')
print()

rows_processed = 0
markets_skipped_no_metadata = 0
for rg_idx in range(cf.metadata.num_row_groups):
    rg = cf.read_row_group(rg_idx, columns=[ticker_col, ts_col, yes_close_col])
    df = rg.to_pandas()
    df['ticker'] = df['ticker'].astype(str)
    df = df.dropna(subset=[yes_close_col])

    for ticker, ts, yc in zip(df['ticker'], df[ts_col], df[yes_close_col]):
        if ticker not in ticker_window:
            continue
        ticker_yes_series[ticker].append((str(ts), float(yc)))

    rows_processed += len(df)
    if rg_idx % 5 == 0 or rg_idx == cf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        print(f'  RG {rg_idx+1}/{cf.metadata.num_row_groups}, {rows_processed:,} rows, {len(ticker_yes_series):,} markets, {elapsed:.0f}s')

print()
print(f'Streaming complete in {time.time() - start:.0f}s.')
print()

# Per-market: split series into premarket-half (first half of open→close window) vs in_match-half
# Then compute trajectory metrics on each half separately
per_market = []

for ticker, series in ticker_yes_series.items():
    if ticker not in ticker_window:
        continue
    open_ts, close_ts = ticker_window[ticker]
    # Sort series by timestamp
    series = sorted(series)
    if len(series) < 5:
        continue

    # Compute window midpoint
    window_seconds = (close_ts - open_ts).total_seconds()
    if window_seconds <= 0:
        continue
    midpoint = open_ts + (close_ts - open_ts) / 2

    # Split
    pre_series = []
    post_series = []
    for ts_str, yc in series:
        if 'T' in ts_str or '-' in ts_str:
            ts = pd.Timestamp(ts_str, tz='UTC')
        elif ts_str.lstrip('-').isdigit():
            ts = pd.Timestamp(int(ts_str), unit='s', tz='UTC')
        else:
            ts = None
        if ts is None:
            continue
        if ts < midpoint:
            pre_series.append(yc)
        else:
            post_series.append(yc)

    if len(pre_series) < 3:
        continue

    pre_min, pre_max = min(pre_series), max(pre_series)
    pre_range = pre_max - pre_min

    cat = md[md['ticker'] == ticker]['_tier'].iloc[0] if len(md[md['ticker'] == ticker]) > 0 else 'UNKNOWN'
    per_market.append({
        'ticker': ticker, '_tier': cat,
        'pre_n_minutes': len(pre_series),
        'pre_min': pre_min, 'pre_max': pre_max,
        'pre_range': pre_range,
        'post_n_minutes': len(post_series),
    })

trajectory_df = pd.DataFrame(per_market)
print(f'Per-market trajectory data computed: {len(trajectory_df):,} markets')
print()

# === Section 1: Overall trajectory distribution ===
print('-' * 100)
print('1. OVERALL PREMARKET TRAJECTORY WIDTH (yes_close max - min during premarket-half)')
print('-' * 100)
print(f'Median: ${trajectory_df["pre_range"].median():.4f}')
print(f'Mean:   ${trajectory_df["pre_range"].mean():.4f}')
print(f'p25: ${trajectory_df["pre_range"].quantile(0.25):.4f}')
print(f'p75: ${trajectory_df["pre_range"].quantile(0.75):.4f}')
print(f'p95: ${trajectory_df["pre_range"].quantile(0.95):.4f}')

# === Section 2: Bilateral feasibility threshold ===
print()
print('-' * 100)
print('2. BILATERAL FEASIBILITY (per B23: trajectory >= 10c minimum)')
print('-' * 100)
n_5c = (trajectory_df['pre_range'] >= 0.05).sum()
n_10c = (trajectory_df['pre_range'] >= 0.10).sum()
n_20c = (trajectory_df['pre_range'] >= 0.20).sum()
n_30c = (trajectory_df['pre_range'] >= 0.30).sum()
total = len(trajectory_df)
print(f'  >= $0.05: {n_5c:>6,} ({n_5c/total*100:>5.1f}%)')
print(f'  >= $0.10: {n_10c:>6,} ({n_10c/total*100:>5.1f}%) <- B23 minimum bilateral feasibility')
print(f'  >= $0.20: {n_20c:>6,} ({n_20c/total*100:>5.1f}%)')
print(f'  >= $0.30: {n_30c:>6,} ({n_30c/total*100:>5.1f}%)')

# === Section 3: Per-tier distribution ===
print()
print('-' * 100)
print('3. PER-TIER TRAJECTORY WIDTH')
print('-' * 100)
for cat in sorted(trajectory_df['_tier'].dropna().unique()):
    sub = trajectory_df[trajectory_df['_tier'] == cat]
    print(f'\n{cat} ({len(sub):,} markets):')
    print(f'  pre_range: median=${sub["pre_range"].median():.4f}, p75=${sub["pre_range"].quantile(0.75):.4f}, p95=${sub["pre_range"].quantile(0.95):.4f}')
    n_10c_cat = (sub['pre_range'] >= 0.10).sum()
    print(f'  bilateral-feasible (>=10c): {n_10c_cat:,} ({n_10c_cat/len(sub)*100:.1f}%)')

# === Section 4: Top 20 widest trajectories ===
print()
print('-' * 100)
print('4. TOP 20 WIDEST PREMARKET TRAJECTORIES')
print('-' * 100)
top = trajectory_df.nlargest(20, 'pre_range')[['ticker', '_tier', 'pre_n_minutes', 'pre_min', 'pre_max', 'pre_range']]
print(top.to_string(index=False))

print()
print('=' * 100)
print(f'END Cat 6 in {time.time() - start:.0f}s — premarket trajectory width catalogued.')
print('=' * 100)
