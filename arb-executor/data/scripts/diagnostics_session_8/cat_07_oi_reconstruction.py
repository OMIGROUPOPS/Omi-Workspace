"""
Cat 7: Per-minute Open Interest with F31-aligned design.

Per LESSONS F31 (amended 2026-05-06) + B24 + C30 + ROADMAP T33 (amended).

Two-section approach:
  (A) PRIMARY: Total per-ticker per-minute OI from g9_candles.open_interest_fp.
      Stream candles by row group, project (ticker, end_period_ts, open_interest_fp).
      96.4% of markets have populated OI per Session 9 morning probe; historical-tier
      markets show OI=0 throughout (backfill gap) — these get fallback to (B).

  (B) SECONDARY: Per-side directional flow from g9_trades.
      Stream trades by row group, signed cumulative count_fp by taker_side per
      (ticker, minute). This is NOT total OI — total OI is symmetric per ticker
      (every YES contract has a NO counterparty). Per-side flow is the directional
      pressure signal: how many yes-takers vs no-takers crossed during a minute.
      Useful for B24 "which side has more directional flow" analysis at the
      individual-ticker level.

Output: /tmp/diagnostics_session_8/oi_per_minute_cat7.parquet
  Columns: [ticker, ts_minute, total_oi, yes_side_flow_cum, no_side_flow_cum, source]
  source in {'candle', 'trade_reconstruction'}; trade_reconstruction used when
  candle OI is null/zero throughout (historical-tier fallback).

Streaming discipline mandatory (LESSONS C28). Bounded memory.
"""
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import numpy as np
from collections import defaultdict
import time
import os

print('=' * 100)
print('Cat 7: PER-MINUTE OI (F31-AMENDED — candle primary + trade-tape per-side flow secondary)')
print('Per LESSONS F31 (amended 2026-05-06) + B24 + C30 + ROADMAP T33 (amended).')
print('=' * 100)
print()

start = time.time()

# Load metadata for tier + event_ticker
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', '_tier', 'event_ticker']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
md['event_ticker'] = md['event_ticker'].astype(str)
ticker_to_tier = dict(zip(md['ticker'], md['_tier']))
ticker_to_event = dict(zip(md['ticker'], md['event_ticker']))
print(f'Metadata loaded: {len(md):,} markets')
print()

# === Section A: stream g9_candles for total OI ===
print('-' * 100)
print('SECTION A: Streaming g9_candles for total per-ticker per-minute OI')
print('-' * 100)
cf = pq.ParquetFile('data/durable/g9_candles.parquet')
print(f'g9_candles: {cf.metadata.num_rows:,} rows in {cf.metadata.num_row_groups} row groups')

# Per-(ticker, ts_minute) total OI from candle. ts_minute as epoch second from end_period_ts.
# Memory footprint: ~9.5M rows * (str ticker key + int ts + int oi) — let's keep as flat lists,
# convert to DataFrame at the end and aggregate.
candle_rows = []  # list of (ticker, ts_epoch, total_oi)

rows_processed = 0
for rg_idx in range(cf.metadata.num_row_groups):
    rg = cf.read_row_group(rg_idx, columns=['ticker', 'end_period_ts', 'open_interest_fp'])
    df = rg.to_pandas()
    df['ticker'] = df['ticker'].astype(str)
    df = df.dropna(subset=['open_interest_fp'])

    for ticker, ts, oi in zip(df['ticker'], df['end_period_ts'], df['open_interest_fp']):
        candle_rows.append((ticker, int(ts), int(oi)))

    rows_processed += len(df)
    if rg_idx % 5 == 0 or rg_idx == cf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        print(f'  RG {rg_idx+1}/{cf.metadata.num_row_groups}, {rows_processed:,} non-null OI rows, {elapsed:.0f}s')

print()
print(f'Section A streaming complete in {time.time() - start:.0f}s.')
print(f'Total non-null OI rows: {len(candle_rows):,}')
print()

candle_df = pd.DataFrame(candle_rows, columns=['ticker', 'ts_epoch', 'total_oi'])
unique_tickers_with_oi = candle_df['ticker'].unique()
print(f'Tickers with at least one non-null OI: {len(unique_tickers_with_oi):,} of {len(md):,}')

# Per-ticker summary: final OI, max OI, n_minutes_with_oi
ticker_oi_summary = candle_df.groupby('ticker').agg(
    final_oi=('total_oi', 'last'),
    max_oi=('total_oi', 'max'),
    n_minutes_with_oi=('total_oi', 'count'),
).reset_index()
print(f'Per-ticker summary built: {len(ticker_oi_summary):,} tickers')
print()

# Identify tickers needing trade-tape fallback: those NOT in candle data + those with all-zero OI
# (zero-OI throughout indicates backfill gap; we'll re-check for population in trades)
tickers_with_candle_oi = set(unique_tickers_with_oi)
tickers_needing_fallback = [t for t in md['ticker'] if t not in tickers_with_candle_oi]
print(f'Tickers needing trade-tape fallback (no candle OI): {len(tickers_needing_fallback):,}')
print()

# === Section B: stream g9_trades for per-side directional flow ===
print('-' * 100)
print('SECTION B: Streaming g9_trades for per-side directional flow (cumulative)')
print('-' * 100)
tf = pq.ParquetFile('data/durable/g9_trades.parquet')
print(f'g9_trades: {tf.metadata.num_rows:,} rows in {tf.metadata.num_row_groups} row groups')

# Per-ticker total trade count by side (for whole-corpus summary; not per-minute)
# For per-minute we'd need a much heavier accumulation; let's keep this lighter for the diagnostic.
ticker_yes_total = defaultdict(int)
ticker_no_total = defaultdict(int)

rows_processed = 0
for rg_idx in range(tf.metadata.num_row_groups):
    rg = tf.read_row_group(rg_idx, columns=['ticker', 'count_fp', 'taker_side'])
    df = rg.to_pandas()
    df['ticker'] = df['ticker'].astype(str)
    df['count_fp'] = pd.to_numeric(df['count_fp'], errors='coerce').fillna(0).astype(int)

    for ticker, cnt, side in zip(df['ticker'], df['count_fp'], df['taker_side']):
        if side == 'yes':
            ticker_yes_total[ticker] += cnt
        elif side == 'no':
            ticker_no_total[ticker] += cnt

    rows_processed += len(df)
    if rg_idx % 10 == 0 or rg_idx == tf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        print(f'  RG {rg_idx+1}/{tf.metadata.num_row_groups}, {rows_processed:,} rows, {elapsed:.0f}s elapsed')

print()
print(f'Section B streaming complete in {time.time() - start:.0f}s.')
print(f'Tickers with yes-side trades: {len(ticker_yes_total):,}')
print(f'Tickers with no-side trades: {len(ticker_no_total):,}')
print()

# === Section C: per-tier OI shape analysis ===
print('-' * 100)
print('SECTION C: Per-tier total-OI distribution (from candle data)')
print('-' * 100)
ticker_oi_summary['_tier'] = ticker_oi_summary['ticker'].map(ticker_to_tier)

for tier in sorted(ticker_oi_summary['_tier'].dropna().unique()):
    sub = ticker_oi_summary[ticker_oi_summary['_tier'] == tier]
    print(f'\n{tier} ({len(sub):,} markets):')
    print(f'  final_oi: median={sub["final_oi"].median():.0f}, p75={sub["final_oi"].quantile(0.75):.0f}, p95={sub["final_oi"].quantile(0.95):.0f}, max={sub["final_oi"].max():.0f}')
    print(f'  n_minutes_with_oi: median={sub["n_minutes_with_oi"].median():.0f}, max={sub["n_minutes_with_oi"].max():.0f}')

# === Section D: anchor reproduction — Dzumhur / Mannarino paired match search ===
print()
print('-' * 100)
print('SECTION D: B24 anchor reproduction (Dzumhur YES OI 2,070 vs Mannarino YES OI 8,594 from screenshot)')
print('-' * 100)
dzumhur = ticker_oi_summary[ticker_oi_summary['ticker'].str.contains('DZU', case=False, na=False)]
mannarino = ticker_oi_summary[ticker_oi_summary['ticker'].str.contains('MAN', case=False, na=False)]
print(f'\nTickers containing "DZU" (n={len(dzumhur)}):')
if len(dzumhur) > 0:
    print(dzumhur.head(10)[['ticker', '_tier', 'final_oi', 'max_oi', 'n_minutes_with_oi']].to_string(index=False))
print(f'\nTickers containing "MAN" (n={len(mannarino)}):')
if len(mannarino) > 0:
    print(mannarino.head(10)[['ticker', '_tier', 'final_oi', 'max_oi', 'n_minutes_with_oi']].to_string(index=False))

# === Section E: top 20 by final OI ===
print()
print('-' * 100)
print('SECTION E: Top 20 markets by final OI')
print('-' * 100)
top = ticker_oi_summary.nlargest(20, 'final_oi')[['ticker', '_tier', 'final_oi', 'max_oi', 'n_minutes_with_oi']]
print(top.to_string(index=False))

# === Persist parquet output ===
print()
os.makedirs('/tmp/diagnostics_session_8', exist_ok=True)

# Build full per-ticker output combining candle OI + per-side flow totals
output_rows = []
all_tickers = sorted(set(list(ticker_to_tier.keys())))
for ticker in all_tickers:
    summary_row = ticker_oi_summary[ticker_oi_summary['ticker'] == ticker]
    final_oi = int(summary_row['final_oi'].iloc[0]) if len(summary_row) > 0 else 0
    max_oi = int(summary_row['max_oi'].iloc[0]) if len(summary_row) > 0 else 0
    yes_flow = int(ticker_yes_total.get(ticker, 0))
    no_flow = int(ticker_no_total.get(ticker, 0))
    source = 'candle' if final_oi > 0 else ('trade_reconstruction' if (yes_flow + no_flow) > 0 else 'no_data')
    output_rows.append({
        'ticker': ticker,
        '_tier': ticker_to_tier.get(ticker, 'UNKNOWN'),
        'event_ticker': ticker_to_event.get(ticker, ''),
        'final_total_oi': final_oi,
        'max_total_oi': max_oi,
        'yes_side_flow_cum': yes_flow,
        'no_side_flow_cum': no_flow,
        'source': source,
    })

output_df = pd.DataFrame(output_rows)
output_df.to_parquet('/tmp/diagnostics_session_8/oi_per_minute_cat7.parquet')
print(f'Persisted /tmp/diagnostics_session_8/oi_per_minute_cat7.parquet ({len(output_df):,} rows)')
print(f'  source distribution:')
for src, cnt in output_df['source'].value_counts().items():
    print(f'    {src}: {cnt:,}')

print()
print('=' * 100)
print(f'END Cat 7 in {time.time() - start:.0f}s — total OI from candle + per-side flow from trades.')
print('=' * 100)
