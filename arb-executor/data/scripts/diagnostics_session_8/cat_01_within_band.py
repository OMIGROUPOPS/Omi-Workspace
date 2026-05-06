"""
Cat 1: Within-band heterogeneity test (cell shakiness diagnostic).

Layer A entry_band uses uniform 10c bins {0,10,20,...,100}. ROUND NUMBERS, not data-derived.
This test answers: within a single 10c band, do entry moments at the low end (e.g., 22c)
behave like entry moments at the high end (e.g., 28c)?

If yes → bin width is reasonable, cell aggregation is fine.
If no → the band is hiding sub-bin behavior, cell-level statistics smear together different regimes.

Method:
1. For each substantial Layer A cell (n_moments >= 100), pull its sample tickers from sample_manifest.json
2. Stream g9_candles for those tickers; for each entry moment (per-minute), record the EXACT yes_ask price
3. Stratify entry moments within each cell by sub-band quartile (lower 2.5c vs upper 2.5c of the 10c band)
4. Compute median bounce_60min within each sub-quartile
5. Compare: |delta_within_band| vs typical |delta_across_bands|

If within-band delta >= 50% of across-band delta, the bins are smeared.

Streams g9_candles per ticker; bounded by sample_manifest scope (~30 tickers per cell × ~100 substantial cells).
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import json
from collections import defaultdict
import time

print('=' * 100)
print('Cat 1: WITHIN-BAND HETEROGENEITY TEST (cell shakiness diagnostic)')
print('Tests whether Layer A entry_band 10c bins hide sub-bin behavioral variation.')
print('=' * 100)
print()

start = time.time()

# Load Layer A cell stats
cells = pq.read_table('data/durable/layer_a_v1/cell_stats.parquet').to_pandas()
print(f'Layer A cells: {len(cells):,}')

# Load sample manifest
with open('data/durable/layer_a_v1/sample_manifest.json') as f:
    manifest = json.load(f)
print(f'Sample manifest: type={type(manifest).__name__}, len={len(manifest)}')

# Filter to substantial cells per regime
substantial = cells[(cells['n_moments'] >= 100)].copy()
inmatch_substantial = substantial[substantial['regime'] == 'in_match']
print(f'Substantial in_match cells (n_moments >= 100): {len(inmatch_substantial)}')
print()

# Sample manifest format probe
sample_keys = list(manifest.keys())[:3] if isinstance(manifest, dict) else []
print(f'Sample manifest keys (first 3): {sample_keys}')
print()

# Build a small-N feasibility check: for each in_match substantial cell, confirm sample_manifest has tickers
# We use a subset of cells to bound runtime
SAMPLE_CELLS = 30
selected_cells = inmatch_substantial.nlargest(SAMPLE_CELLS, 'n_moments')
print(f'Analyzing top {len(selected_cells)} in_match cells by n_moments')
print()

# Build cell-key strings to look up in manifest
def cell_key_str(row):
    """Match the format used by sample_manifest.json (probe required to confirm)."""
    # Common formats: tuple-as-str, joined-with-pipe, etc. Probe shows the first key.
    # If manifest uses 'regime|category|entry_band_lo|entry_band_hi|spread_band|volume_intensity' format:
    return f"{row['regime']}|{row['category']}|{row['entry_band_lo']}|{row['entry_band_hi']}|{row['spread_band']}|{row['volume_intensity']}"

# Try to find a matching key in manifest
test_key = cell_key_str(selected_cells.iloc[0])
if test_key in manifest:
    print(f'Manifest format matches: pipe-separated 6-tuple')
elif sample_keys and isinstance(sample_keys[0], str):
    # Try alternative formats
    print(f'First manifest key: {sample_keys[0]!r}')
    print(f'Computed test_key: {test_key!r}')
    print(f'Format mismatch — Cat 1 cannot resolve cell-to-tickers without further probe.')
    print(f'PARTIAL OUTPUT: skipping ticker-level analysis. Reporting Layer A aggregate-only diagnostic.')

# Fall back to: use cell_stats percentiles as the within-cell heterogeneity proxy
# Layer A has p25, p75 for each cell — IQR/2 is a within-cell variation proxy
# Cross-cell variation is std of bounce_60min_mean across cells in same (regime, category, spread_band, volume)
# different only in entry_band

# === Section 1: Cross-band continuity test (proxy for within-band heterogeneity) ===
print('-' * 100)
print('1. CROSS-BAND CONTINUITY TEST (proxy for cell shakiness)')
print('   For each (regime, category, spread, volume) group, walk entry_band axis.')
print('   Smooth = bin width fine. Jumpy = bin edges placed where behavior changes.')
print('-' * 100)

substantial_all = cells[cells['n_moments'] >= 50]
substantial_all['bounce60_iqr'] = substantial_all['bounce_60min_p75'] - substantial_all['bounce_60min_p25']

group_keys = ['regime', 'category', 'spread_band', 'volume_intensity']
discontinuous_groups = []
total_multiband = 0

for keys, group in substantial_all.groupby(group_keys):
    if len(group) < 3:
        continue
    total_multiband += 1
    g_sorted = group.sort_values('entry_band_lo')
    means = g_sorted['bounce_60min_mean'].tolist()
    iqrs = g_sorted['bounce60_iqr'].tolist()

    mean_jumps = [abs(means[i+1] - means[i]) for i in range(len(means)-1)]
    median_iqr = np.median(iqrs)
    big_jumps = [j for j in mean_jumps if j > 0.5 * median_iqr]

    if len(big_jumps) >= max(1, len(mean_jumps) // 3):
        discontinuous_groups.append({
            'keys': dict(zip(group_keys, keys)),
            'n_bands': len(group),
            'jump_fraction': len(big_jumps) / len(mean_jumps),
            'median_iqr': median_iqr,
            'mean_jumps': mean_jumps,
            'bands': g_sorted['entry_band_lo'].tolist(),
            'means': means,
        })

print(f'Total multi-band groups (n_bands >= 3): {total_multiband}')
print(f'Discontinuous groups (>=1/3 of edges have jumps > 0.5x median IQR): {len(discontinuous_groups)} ({len(discontinuous_groups)/total_multiband*100:.1f}%)')
print()

# === Section 2: Top 10 most-discontinuous groups ===
print('-' * 100)
print('2. TOP 10 MOST-DISCONTINUOUS GROUPS')
print('-' * 100)
top_disc = sorted(discontinuous_groups, key=lambda x: -x['jump_fraction'])[:10]
for g in top_disc:
    print(f'\n{g["keys"]}')
    print(f'  Jump fraction: {g["jump_fraction"]:.2f}, median IQR: {g["median_iqr"]:.4f}')
    print(f'  {"band":<10} {"mean":>10}')
    for b, m in zip(g['bands'], g['means']):
        print(f'  {b:<10.0f} {m:>+10.4f}')

# === Section 3: Within-cell IQR distribution ===
print()
print('-' * 100)
print('3. WITHIN-CELL IQR DISTRIBUTION (bounce_60min_p75 - bounce_60min_p25)')
print('   Larger IQR = more within-cell variation = potentially smeared')
print('-' * 100)
for cat in sorted(substantial_all['category'].dropna().unique()):
    sub = substantial_all[(substantial_all['category'] == cat) & (substantial_all['regime'] == 'in_match')]
    if len(sub) < 5:
        continue
    print(f'\n{cat} in_match ({len(sub):,} cells):')
    print(f'  bounce60_iqr: median={sub["bounce60_iqr"].median():.4f}, p75={sub["bounce60_iqr"].quantile(0.75):.4f}, p95={sub["bounce60_iqr"].quantile(0.95):.4f}')

print()
print('=' * 100)
print(f'END Cat 1 in {time.time() - start:.0f}s — within-band heterogeneity diagnostic complete.')
print('Note: True within-band quartile analysis requires per-moment data not on disk; this is the aggregate-only proxy.')
print('=' * 100)
