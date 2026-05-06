"""
Cat 7: Per-minute Open Interest reconstruction.

For each market, walk g9_trades chronologically, compute signed cumulative count_fp by taker_side
direction, bin to per-minute. Per LESSONS F31 + B24.

Notes on OI semantics:
- A 'yes' taker side trade means a taker bought yes; the maker sold yes.
  Net new yes_oi = +count_fp (one new yes contract held by taker).
  But if the maker was closing a yes-long, OI doesn't increase — just transfers.
  We CANNOT distinguish open vs close from trade tape alone.
  However: cumulative net buys gives a *bound* on OI.

Per the lesson framing, we compute "cumulative signed count_fp by taker_side" as the proxy.
At session-9 we'll evaluate whether this proxy correlates with the live OI we saw on Kalshi
(2,070 for Dzumhur YES, 8,594 for Mannarino YES).

Output:
- Per-tier OI growth shapes (linear vs hockey-stick)
- Anchor reproduction: pick 5 large markets (with known volume), compute final-cumulative-yes-trades
- Persist /tmp/diagnostics_session_8/oi_per_minute_cat7.parquet for Cat 10

Streams row-groups; does NOT materialize 33.7M rows in memory.
"""
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import numpy as np
from collections import defaultdict
import time
import os

print('=' * 100)
print('Cat 7: PER-MINUTE OPEN INTEREST RECONSTRUCTION')
print('Per LESSONS F31 + B24. Foundation: g9_trades.parquet (T28 ea84e74).')
print('Computation: signed cumulative count_fp by taker_side per market per minute.')
print('=' * 100)
print()

start = time.time()

# Load metadata
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', 'category']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
ticker_to_category = dict(zip(md['ticker'], md['category']))

pf = pq.ParquetFile('data/durable/g9_trades.parquet')
print(f'g9_trades: {pf.metadata.num_rows:,} rows in {pf.metadata.num_row_groups} row groups.')
print()

# Per-(ticker, minute) accumulator: yes-side trades, no-side trades counts (signed proxy for OI delta)
# Using dict-of-dict structure; streaming row groups to keep memory bounded
ticker_minute_yes_trades = defaultdict(lambda: defaultdict(int))
ticker_minute_no_trades = defaultdict(lambda: defaultdict(int))

rows_processed = 0
for rg_idx in range(pf.metadata.num_row_groups):
    rg = pf.read_row_group(rg_idx, columns=['ticker', 'created_time', 'count_fp', 'taker_side'])
    df = rg.to_pandas()
    df['ticker'] = df['ticker'].astype(str)
    df['ts_minute'] = df['created_time'].astype(str).str[:16]
    df['count_fp'] = pd.to_numeric(df['count_fp'], errors='coerce').fillna(0).astype(int)

    for ticker, ts_min, count, side in zip(df['ticker'], df['ts_minute'], df['count_fp'], df['taker_side']):
        if side == 'yes':
            ticker_minute_yes_trades[ticker][ts_min] += count
        elif side == 'no':
            ticker_minute_no_trades[ticker][ts_min] += count

    rows_processed += len(df)
    if rg_idx % 10 == 0 or rg_idx == pf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        n_markets = len(set(list(ticker_minute_yes_trades.keys()) + list(ticker_minute_no_trades.keys())))
        print(f'  RG {rg_idx+1}/{pf.metadata.num_row_groups}, {rows_processed:,} rows, {n_markets:,} markets, {elapsed:.0f}s')

print()
print(f'Streaming pass complete in {time.time() - start:.0f}s. Building per-minute OI series...')
print()

# Build per-(ticker, minute) cumulative OI series, then summarize per market and per tier
all_tickers = set(list(ticker_minute_yes_trades.keys()) + list(ticker_minute_no_trades.keys()))

per_market_summary = []  # ticker, category, n_minutes, final_yes_cum, final_no_cum, max_yes_cum, max_no_cum
oi_rows_for_parquet = []  # ticker, ts_minute, yes_cum, no_cum

for ticker in all_tickers:
    cat = ticker_to_category.get(ticker, 'UNKNOWN')
    yes_minutes = ticker_minute_yes_trades.get(ticker, {})
    no_minutes = ticker_minute_no_trades.get(ticker, {})
    all_minutes = sorted(set(list(yes_minutes.keys()) + list(no_minutes.keys())))

    yes_cum = 0
    no_cum = 0
    max_yes = 0
    max_no = 0
    for ts_min in all_minutes:
        yes_cum += yes_minutes.get(ts_min, 0)
        no_cum += no_minutes.get(ts_min, 0)
        max_yes = max(max_yes, yes_cum)
        max_no = max(max_no, no_cum)
        oi_rows_for_parquet.append((ticker, ts_min, yes_cum, no_cum))

    per_market_summary.append({
        'ticker': ticker, 'category': cat, 'n_minutes': len(all_minutes),
        'final_yes_cum': yes_cum, 'final_no_cum': no_cum,
        'max_yes_cum': max_yes, 'max_no_cum': max_no,
    })

summary_df = pd.DataFrame(per_market_summary)

# === Section 1: Per-tier OI shape summary ===
print('-' * 100)
print('1. PER-TIER FINAL CUMULATIVE OI PROXY (signed cumulative count_fp by taker_side)')
print('-' * 100)
for cat in sorted(summary_df['category'].dropna().unique()):
    sub = summary_df[summary_df['category'] == cat]
    print(f'\n{cat} ({len(sub):,} markets):')
    print(f'  final_yes_cum: median={sub["final_yes_cum"].median():.0f}, p75={sub["final_yes_cum"].quantile(0.75):.0f}, p95={sub["final_yes_cum"].quantile(0.95):.0f}, max={sub["final_yes_cum"].max():.0f}')
    print(f'  final_no_cum:  median={sub["final_no_cum"].median():.0f}, p75={sub["final_no_cum"].quantile(0.75):.0f}, p95={sub["final_no_cum"].quantile(0.95):.0f}, max={sub["final_no_cum"].max():.0f}')
    print(f'  n_minutes:     median={sub["n_minutes"].median():.0f}, max={sub["n_minutes"].max():.0f}')

# === Section 2: Anchor reproduction — search for Dzumhur + Mannarino tickers ===
print()
print('-' * 100)
print('2. ANCHOR REPRODUCTION (per LESSONS B24 evidence: Dzumhur YES OI=2,070, Mannarino YES OI=8,594)')
print('-' * 100)
dzumhur_matches = summary_df[summary_df['ticker'].str.contains('DZU', case=False, na=False)]
mannarino_matches = summary_df[summary_df['ticker'].str.contains('MAN', case=False, na=False)]
print(f'\nTickers containing "DZU" (n={len(dzumhur_matches)}):')
if len(dzumhur_matches) > 0:
    print(dzumhur_matches.head(10).to_string(index=False))
print(f'\nTickers containing "MAN" (n={len(mannarino_matches)}):')
if len(mannarino_matches) > 0:
    print(mannarino_matches.head(10).to_string(index=False))

# === Section 3: Top 20 markets by max_yes_cum ===
print()
print('-' * 100)
print('3. TOP 20 MARKETS BY MAX CUMULATIVE YES OI PROXY')
print('-' * 100)
top_yes = summary_df.nlargest(20, 'max_yes_cum')[['ticker', 'category', 'n_minutes', 'max_yes_cum', 'max_no_cum', 'final_yes_cum', 'final_no_cum']]
print(top_yes.to_string(index=False))

# === Persist preview parquet for Cat 10 ===
print()
os.makedirs('/tmp/diagnostics_session_8', exist_ok=True)
oi_df = pd.DataFrame(oi_rows_for_parquet, columns=['ticker', 'ts_minute', 'yes_cum_proxy', 'no_cum_proxy'])
oi_df.to_parquet('/tmp/diagnostics_session_8/oi_per_minute_cat7.parquet')
print(f'Persisted /tmp/diagnostics_session_8/oi_per_minute_cat7.parquet ({len(oi_df):,} rows)')

print()
print('=' * 100)
print(f'END Cat 7 in {time.time() - start:.0f}s — OI proxy reconstructed.')
print('=' * 100)
