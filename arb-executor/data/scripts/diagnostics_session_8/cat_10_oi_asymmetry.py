"""
Cat 10: Per-side OI asymmetry analysis.

Reads /tmp/diagnostics_session_8/oi_per_minute_cat7.parquet from Cat 7.
For each market, compute final yes_cum_proxy / no_cum_proxy ratio.
Resolve event_ticker via rsplit so we can also look at cross-side asymmetry within the same MATCH
(YES on player A vs YES on player B).

Per LESSONS B24: same-match opposite-side OI asymmetry seen at 4× in Dzumhur/Mannarino anchor.

Output:
- Per-tier intra-ticker yes/no asymmetry distribution
- Per-event (match) cross-ticker yes-on-A vs yes-on-B asymmetry
- Top 20 most asymmetric markets
- Anchor reproduction: Dzumhur vs Mannarino if tickers found
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from collections import defaultdict
import time

print('=' * 100)
print('Cat 10: PER-SIDE OI ASYMMETRY')
print('Per LESSONS B24. Reads Cat 7 output /tmp/diagnostics_session_8/oi_per_minute_cat7.parquet.')
print('=' * 100)
print()

start = time.time()

oi_df = pd.read_parquet('/tmp/diagnostics_session_8/oi_per_minute_cat7.parquet')
print(f'OI rows loaded: {len(oi_df):,}')

# Final per-market values
final_oi = oi_df.groupby('ticker').agg(
    yes_final=('yes_cum_proxy', 'last'),
    no_final=('no_cum_proxy', 'last'),
    n_minutes=('ts_minute', 'count'),
).reset_index()
print(f'Per-market summary rows: {len(final_oi):,}')
print()

# Load category metadata
md = pq.read_table('data/durable/g9_metadata.parquet', columns=['ticker', 'category']).to_pandas()
md['ticker'] = md['ticker'].astype(str)
final_oi = final_oi.merge(md, on='ticker', how='left')

# Compute intra-ticker asymmetry (yes-side trades / no-side trades within same ticker)
final_oi['intra_ratio'] = np.where(
    (final_oi['no_final'] > 0) & (final_oi['yes_final'] > 0),
    final_oi['yes_final'] / final_oi['no_final'],
    np.nan
)

# === Section 1: Per-tier intra-ticker yes-vs-no asymmetry ===
print('-' * 100)
print('1. PER-TIER INTRA-TICKER YES vs NO TRADE-SIDE ASYMMETRY')
print('   Ratio = (yes-side trades) / (no-side trades) per market')
print('   1.0 = balanced; >1.0 = yes-side-dominant; <1.0 = no-side-dominant')
print('-' * 100)
for cat in sorted(final_oi['category'].dropna().unique()):
    sub = final_oi[final_oi['category'] == cat].dropna(subset=['intra_ratio'])
    if len(sub) == 0:
        continue
    print(f'\n{cat} ({len(sub):,} markets):')
    print(f'  intra_ratio: median={sub["intra_ratio"].median():.3f}, p25={sub["intra_ratio"].quantile(0.25):.3f}, p75={sub["intra_ratio"].quantile(0.75):.3f}, max={sub["intra_ratio"].max():.2f}')
    n_extreme = (sub['intra_ratio'] >= 4.0).sum() + (sub['intra_ratio'] <= 0.25).sum()
    print(f'  Markets with >=4x asymmetry (either direction): {n_extreme} ({n_extreme/len(sub)*100:.1f}%)')

# === Section 2: Cross-ticker (paired-side) asymmetry within same event ===
print()
print('-' * 100)
print('2. CROSS-TICKER ASYMMETRY (YES on player A vs YES on player B in same match)')
print('   Per LESSONS B24 anchor: Dzumhur YES OI 2,070 vs Mannarino YES OI 8,594 = 4.15x')
print('-' * 100)

# Resolve event_ticker via rsplit('-', 1)[0]
final_oi['event_ticker'] = final_oi['ticker'].str.rsplit('-', n=1).str[0]
event_groups = final_oi.groupby('event_ticker').filter(lambda g: len(g) == 2)  # paired markets only
print(f'Paired (2-side) events: {len(event_groups) // 2:,} matches')
print()

# Compute per-pair YES-side asymmetry
paired_asymmetry = []
for ev_ticker, group in event_groups.groupby('event_ticker'):
    if len(group) != 2:
        continue
    sides = group.sort_values('ticker').to_dict('records')
    a, b = sides[0], sides[1]
    if a['yes_final'] <= 0 or b['yes_final'] <= 0:
        continue
    ratio = max(a['yes_final'], b['yes_final']) / min(a['yes_final'], b['yes_final'])
    paired_asymmetry.append({
        'event_ticker': ev_ticker,
        'category': a.get('category', 'UNKNOWN'),
        'side_a_ticker': a['ticker'],
        'side_b_ticker': b['ticker'],
        'side_a_yes': a['yes_final'],
        'side_b_yes': b['yes_final'],
        'asymmetry_ratio': ratio,
    })

paired_df = pd.DataFrame(paired_asymmetry)
print(f'Paired matches with non-zero YES on both sides: {len(paired_df):,}')
print()

if len(paired_df) > 0:
    print('Per-tier paired YES asymmetry distribution:')
    for cat in sorted(paired_df['category'].dropna().unique()):
        sub = paired_df[paired_df['category'] == cat]
        if len(sub) == 0:
            continue
        print(f'\n{cat} ({len(sub):,} matches):')
        print(f'  asymmetry_ratio: median={sub["asymmetry_ratio"].median():.2f}x, p75={sub["asymmetry_ratio"].quantile(0.75):.2f}x, p95={sub["asymmetry_ratio"].quantile(0.95):.2f}x, max={sub["asymmetry_ratio"].max():.2f}x')
        n_extreme = (sub['asymmetry_ratio'] >= 4.0).sum()
        print(f'  Matches with >=4x cross-side asymmetry (B24-anchor-or-beyond): {n_extreme} ({n_extreme/len(sub)*100:.1f}%)')

    # === Section 3: Top 20 most asymmetric paired matches ===
    print()
    print('-' * 100)
    print('3. TOP 20 MOST ASYMMETRIC PAIRED MATCHES (cross-side YES OI ratio)')
    print('-' * 100)
    top_pair = paired_df.nlargest(20, 'asymmetry_ratio')[
        ['event_ticker', 'category', 'side_a_ticker', 'side_a_yes', 'side_b_ticker', 'side_b_yes', 'asymmetry_ratio']
    ]
    print(top_pair.to_string(index=False))

# === Section 4: Anchor reproduction ===
print()
print('-' * 100)
print('4. ANCHOR REPRODUCTION (Dzumhur/Mannarino paired-match search)')
print('-' * 100)
dzu_man = paired_df[paired_df['side_a_ticker'].str.contains('DZU|MAN', case=False, na=False) | paired_df['side_b_ticker'].str.contains('DZU|MAN', case=False, na=False)] if len(paired_df) > 0 else pd.DataFrame()
if len(dzu_man) > 0:
    print(dzu_man.to_string(index=False))
else:
    print('(No Dzumhur/Mannarino paired matches found in current g9_trades corpus.)')
    print('(May indicate the anchor screenshot was taken on a market that was newer than the g9 collection cutoff.)')

print()
print('=' * 100)
print(f'END Cat 10 in {time.time() - start:.0f}s — OI asymmetry catalogued.')
print('=' * 100)
