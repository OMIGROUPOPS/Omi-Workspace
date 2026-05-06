"""
Cat 10: Per-side OI asymmetry — F31-aligned design.

Per LESSONS B24 + F31 (amended 2026-05-06).

B24 anchor: same paired event has two separate tickers (one per player binary).
Same screenshot snapshot:
  Dzumhur YES OI: 2,070 (Ticker 1: Dzumhur match-binary)
  Mannarino YES OI: 8,594 (Ticker 2: Mannarino match-binary)
  Cross-ticker asymmetry ratio: 4.15x

This is NOT within-ticker per-side; it IS cross-ticker paired-match. The total OI
on Ticker 1 (Dzumhur) and Ticker 2 (Mannarino) are independent measurements
because they are separate Kalshi binary contracts (one per player), NOT the YES
side and NO side of the same contract.

This Cat 10 (rewritten 2026-05-06) reads g9_candles.open_interest_fp directly,
no longer depends on Cat 7's output parquet (Cat 7 still produces the same
parquet, but Cat 10 doesn't need it).

Output:
- Per-tier paired-match cross-ticker asymmetry distribution
- Top 20 most-asymmetric paired matches
- Anchor reproduction: any DZU/MAN paired matches in our corpus
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from collections import defaultdict
import time

print('=' * 100)
print('Cat 10: PER-SIDE OI ASYMMETRY (F31-AMENDED — cross-ticker paired-match analysis)')
print('Per LESSONS B24 + F31 (amended). Reads g9_candles directly; no Cat 7 dependency.')
print('=' * 100)
print()

start = time.time()

# Load metadata
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', '_tier', 'event_ticker']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
md['event_ticker'] = md['event_ticker'].astype(str)
print(f'Metadata loaded: {len(md):,} markets')
print()

# === Stream g9_candles for per-ticker final/max OI ===
cf = pq.ParquetFile('data/durable/g9_candles.parquet')
print(f'Streaming g9_candles ({cf.metadata.num_rows:,} rows, {cf.metadata.num_row_groups} row groups)...')

# Accumulate per-ticker max OI (since OI is monotonic per probe, max ≈ final for active periods)
ticker_max_oi = defaultdict(int)
ticker_n_minutes = defaultdict(int)

rows_processed = 0
for rg_idx in range(cf.metadata.num_row_groups):
    rg = cf.read_row_group(rg_idx, columns=['ticker', 'open_interest_fp'])
    df = rg.to_pandas()
    df['ticker'] = df['ticker'].astype(str)
    df = df.dropna(subset=['open_interest_fp'])

    rg_max = df.groupby('ticker')['open_interest_fp'].agg(['max', 'count']).reset_index()
    for ticker, mx, cnt in zip(rg_max['ticker'], rg_max['max'], rg_max['count']):
        if mx > ticker_max_oi[ticker]:
            ticker_max_oi[ticker] = int(mx)
        ticker_n_minutes[ticker] += int(cnt)

    rows_processed += len(df)
    if rg_idx % 5 == 0 or rg_idx == cf.metadata.num_row_groups - 1:
        elapsed = time.time() - start
        print(f'  RG {rg_idx+1}/{cf.metadata.num_row_groups}, {rows_processed:,} non-null OI rows, {elapsed:.0f}s')

print()
print(f'Streaming complete in {time.time() - start:.0f}s. Tickers with OI data: {len(ticker_max_oi):,}')
print()

# Build per-ticker dataframe
oi_df = pd.DataFrame([
    {'ticker': t, 'max_oi': ticker_max_oi[t], 'n_minutes': ticker_n_minutes[t]}
    for t in ticker_max_oi
])
oi_df = oi_df.merge(md[['ticker', '_tier', 'event_ticker']], on='ticker', how='left')
print(f'Per-ticker OI dataframe: {len(oi_df):,} rows')
print()

# === Cross-ticker paired-match asymmetry ===
print('-' * 100)
print('1. CROSS-TICKER PAIRED-MATCH ASYMMETRY (B24 anchor framing)')
print('-' * 100)

# Group by event_ticker; only events with exactly 2 tickers having OI data
paired_events = oi_df.groupby('event_ticker').filter(lambda g: len(g) == 2)
print(f'Paired events with both tickers having OI data: {len(paired_events) // 2:,} matches')
print()

paired_records = []
for ev, group in paired_events.groupby('event_ticker'):
    if len(group) != 2:
        continue
    sides = group.sort_values('ticker').to_dict('records')
    a, b = sides[0], sides[1]
    if a['max_oi'] <= 0 or b['max_oi'] <= 0:
        continue
    larger = max(a['max_oi'], b['max_oi'])
    smaller = min(a['max_oi'], b['max_oi'])
    ratio = larger / smaller
    paired_records.append({
        'event_ticker': ev,
        '_tier': a.get('_tier', 'UNKNOWN'),
        'side_a_ticker': a['ticker'],
        'side_a_max_oi': a['max_oi'],
        'side_b_ticker': b['ticker'],
        'side_b_max_oi': b['max_oi'],
        'asymmetry_ratio': ratio,
    })

paired_df = pd.DataFrame(paired_records)
print(f'Paired matches with non-zero OI on both sides: {len(paired_df):,}')
print()

# === Per-tier asymmetry distribution ===
print('-' * 100)
print('2. PER-TIER ASYMMETRY DISTRIBUTION')
print('-' * 100)
for tier in sorted(paired_df['_tier'].dropna().unique()):
    sub = paired_df[paired_df['_tier'] == tier]
    if len(sub) == 0:
        continue
    print(f'\n{tier} ({len(sub):,} paired matches):')
    print(f'  asymmetry_ratio: median={sub["asymmetry_ratio"].median():.2f}x, p75={sub["asymmetry_ratio"].quantile(0.75):.2f}x, p95={sub["asymmetry_ratio"].quantile(0.95):.2f}x, max={sub["asymmetry_ratio"].max():.2f}x')
    n_2x = (sub['asymmetry_ratio'] >= 2.0).sum()
    n_4x = (sub['asymmetry_ratio'] >= 4.0).sum()
    n_10x = (sub['asymmetry_ratio'] >= 10.0).sum()
    print(f'  >= 2x asymmetry: {n_2x:,} ({n_2x/len(sub)*100:.1f}%)')
    print(f'  >= 4x asymmetry: {n_4x:,} ({n_4x/len(sub)*100:.1f}%) <- B24 anchor threshold (Dzumhur/Mannarino was 4.15x)')
    print(f'  >= 10x asymmetry: {n_10x:,} ({n_10x/len(sub)*100:.1f}%)')

# === Top 20 most-asymmetric paired matches ===
print()
print('-' * 100)
print('3. TOP 20 MOST-ASYMMETRIC PAIRED MATCHES (cross-ticker max-OI ratio)')
print('-' * 100)
top = paired_df.nlargest(20, 'asymmetry_ratio')[
    ['event_ticker', '_tier', 'side_a_ticker', 'side_a_max_oi', 'side_b_ticker', 'side_b_max_oi', 'asymmetry_ratio']
]
print(top.to_string(index=False))

# === Anchor reproduction: Dzumhur/Mannarino paired matches ===
print()
print('-' * 100)
print('4. B24 ANCHOR REPRODUCTION (Dzumhur/Mannarino paired-match search)')
print('-' * 100)
dzu_man = paired_df[
    paired_df['side_a_ticker'].str.contains('DZU|MAN', case=False, na=False) |
    paired_df['side_b_ticker'].str.contains('DZU|MAN', case=False, na=False)
]
if len(dzu_man) > 0:
    print(f'\nFound {len(dzu_man)} paired matches with DZU or MAN tickers:')
    print(dzu_man[['event_ticker', '_tier', 'side_a_ticker', 'side_a_max_oi', 'side_b_ticker', 'side_b_max_oi', 'asymmetry_ratio']].to_string(index=False))
else:
    print('\nNo Dzumhur/Mannarino paired matches in current g9 corpus.')
    print('Anchor screenshot was taken on a market newer than the g9 collection cutoff (2026-03-02 per LESSONS).')

print()
print('=' * 100)
print(f'END Cat 10 in {time.time() - start:.0f}s — cross-ticker OI asymmetry catalogued.')
print('=' * 100)
