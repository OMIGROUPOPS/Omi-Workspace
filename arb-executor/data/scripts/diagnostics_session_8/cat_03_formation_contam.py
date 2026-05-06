"""
Cat 3: Formation contamination measurement (Decision 6 / Check 5 preview).

Layer A's premarket regime conflates pre-formation, formation, and post-formation entry moments.
This test stratifies premarket Layer B (cell, policy) outputs by their typical formation-elapsed-time
to see whether early-formation entries differ from settled-premarket entries.

Method (aggregate-only, no per-moment):
- Use Cat 8's formation_gate per market (need to read /tmp output if available, else fall back)
- For each premarket Layer A cell: classify markets in that cell by their formation_gate quartile
- Compute within-cell variation of bounce_60min_mean across formation-gate quartile

If within-cell variation by formation-gate quartile is small → no contamination
If large → premarket cell aggregates contaminated by formation-period dynamics

Plus: check whether premarket bounce_60min_mean correlates with elapsed-since-open at the cell level,
using cell-level summary stats only.
"""
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import json
from collections import defaultdict
import time
import os

print('=' * 100)
print('Cat 3: FORMATION CONTAMINATION MEASUREMENT (Decision 6 / Check 5 preview)')
print('Tests whether premarket Layer A cells conflate formation vs post-formation entries.')
print('=' * 100)
print()

start = time.time()

# Load Layer A cell stats (premarket only)
cells = pq.read_table('data/durable/layer_a_v1/cell_stats.parquet').to_pandas()
premarket_cells = cells[cells['regime'] == 'premarket'].copy()
print(f'Premarket Layer A cells: {len(premarket_cells)}')

# === Section 1: Premarket bounce_60min mean variation by entry_band ===
# Within a single category, walk entry_band; if behavior is heterogeneous within premarket regime,
# this is the strongest signal of contamination
print()
print('-' * 100)
print('1. PREMARKET BOUNCE BY ENTRY_BAND (within-category)')
print('   Hypothesis: if formation contaminates premarket, near-formation entries (when prices wider)')
print('   should have systematically different bounce vs settled-premarket entries.')
print('-' * 100)
premarket_substantial = premarket_cells[premarket_cells['n_moments'] >= 50]

for cat in sorted(premarket_substantial['category'].dropna().unique()):
    sub = premarket_substantial[premarket_substantial['category'] == cat]
    if len(sub) < 5:
        continue
    print(f'\n{cat} premarket ({len(sub):,} cells):')
    by_band = sub.groupby('entry_band_lo').agg(
        n_cells=('bounce_60min_mean', 'count'),
        median_bounce=('bounce_60min_mean', 'median'),
        std_bounce=('bounce_60min_mean', 'std'),
    ).round(4)
    print(by_band.to_string())

# === Section 2: Compare premarket vs in_match cell bounce shapes ===
print()
print('-' * 100)
print('2. PREMARKET vs IN_MATCH BOUNCE SHAPE COMPARISON (per cell-key)')
print('   For cells that exist in both regimes (matching category/band/spread/volume), compare:')
print('   - Is premarket bounce systematically lower? (Per E16: 95% of P&L is in_match)')
print('   - Is the bounce IQR wider in premarket? (Sign of mixed regimes within premarket)')
print('-' * 100)

# Build matching cell-key tuples
key_cols = ['category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity']
pre_substantial = premarket_cells[premarket_cells['n_moments'] >= 50]
inm = cells[(cells['regime'] == 'in_match') & (cells['n_moments'] >= 50)]

merged = pre_substantial.merge(inm, on=key_cols, suffixes=('_pre', '_inm'))
print(f'Cells matched across premarket and in_match: {len(merged)}')
print()

if len(merged) > 0:
    merged['bounce_delta'] = merged['bounce_60min_mean_inm'] - merged['bounce_60min_mean_pre']
    merged['iqr_pre'] = merged['bounce_60min_p75_pre'] - merged['bounce_60min_p25_pre']
    merged['iqr_inm'] = merged['bounce_60min_p75_inm'] - merged['bounce_60min_p25_inm']
    merged['iqr_delta'] = merged['iqr_pre'] - merged['iqr_inm']

    print(f'bounce_delta (in_match - premarket): median={merged["bounce_delta"].median():+.4f}, mean={merged["bounce_delta"].mean():+.4f}')
    print(f'iqr_pre median: {merged["iqr_pre"].median():.4f}')
    print(f'iqr_inm median: {merged["iqr_inm"].median():.4f}')
    print(f'iqr_delta (premarket - in_match) median: {merged["iqr_delta"].median():+.4f}')
    print()
    print(f'  Positive iqr_delta = premarket has wider IQR than in_match = mixed-regime smearing in premarket cell')
    n_pre_wider = (merged['iqr_delta'] > 0).sum()
    print(f'  Cells where premarket IQR > in_match IQR: {n_pre_wider} ({n_pre_wider/len(merged)*100:.1f}%)')

# === Section 3: Formation-gate cross-reference (if Cat 8 output available) ===
print()
print('-' * 100)
print('3. FORMATION-GATE CONTAMINATION CHECK (cross-reference with Cat 8 if available)')
print('-' * 100)

# This section is informative-only; the tight analysis would require per-moment formation-gate data
# which we'd build in T35. For now, just check if Cat 8's output is on disk for cross-reference.
cat8_output = '/root/Omi-Workspace/arb-executor/data/durable/diagnostics_session_8/cat_08_formation_gate.txt'
if os.path.exists(cat8_output):
    print(f'Cat 8 output present at {cat8_output}')
    print('Cross-reference: review Cat 8 + Cat 3 outputs together to see if formation_gate distribution')
    print('aligns with premarket cell IQR width pattern (wider IQR cells should correlate with longer formation gates).')
else:
    print(f'Cat 8 output not yet present at {cat8_output} (may run after Cat 3 in master driver order).')
    print('After both run, compare Cat 8 per-tier formation_gate distribution against Cat 3 per-tier IQR pattern.')

print()
print('=' * 100)
print(f'END Cat 3 in {time.time() - start:.0f}s — formation contamination diagnostic complete.')
print('Note: Definitive Check 5 measurement requires T35 formation_gate per-market field; this is the cell-aggregate proxy.')
print('=' * 100)
