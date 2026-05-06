"""
Cat 5: Alpha discovery on Layer B v1 outputs.
Read exit_policy_per_cell.parquet. For each (cell, policy) with sufficient n_simulated, compute:
- expected_value_per_entry = capture_mean × fire_rate
- a Sharpe-like ratio: capture_mean / capture_std (but Layer B has percentiles, not std — use IQR proxy)
- rank top 30 by expected_value_per_entry, separately for premarket vs in_match
- rank top 30 by capture_p90 (tail-edge) for in_match (where 95% of P&L lives per E16)
Output: ASCII tables. Single-pass aggregation, no streaming needed (19,170 rows).
"""
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

print('=' * 100)
print('Cat 5: ALPHA DISCOVERY on Layer B v1 outputs')
print(f'Foundation: Layer B v1 PASSED T31c 2026-05-05 ET (commit 5cf45e0); 19,170 rows; sha256 d94bc56c.')
print('=' * 100)
print()

p = Path('data/durable/layer_b_v1/exit_policy_per_cell.parquet')
df = pq.read_table(p).to_pandas()
print(f'Total rows: {len(df):,}, columns: {list(df.columns)}')
print()

# Identify column names robustly
# (Layer B columns from probe: includes regime, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity, policy_class, policy_param, n_simulated, fire_count, fire_rate, capture_mean, capture_p10, capture_p25, capture_p50, capture_p75, capture_p90)
# Verify
expected_cols = {'regime', 'category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity',
                 'policy_class', 'policy_param', 'n_simulated', 'fire_rate', 'capture_mean', 'capture_p90'}
missing = expected_cols - set(df.columns)
if missing:
    print(f'WARN: missing expected columns: {missing}')
    print(f'Available: {list(df.columns)}')

# Filter substantial cells
substantial = df[df['n_simulated'] >= 50].copy()
print(f'Substantial (n_simulated >= 50): {len(substantial):,} of {len(df):,}')
print()

# Compute alpha metric: expected value per entry = capture_mean × fire_rate
substantial['expected_value'] = substantial['capture_mean'] * substantial['fire_rate']

# IQR proxy for std
if 'capture_p25' in substantial.columns and 'capture_p75' in substantial.columns:
    substantial['capture_iqr'] = substantial['capture_p75'] - substantial['capture_p25']
    substantial['sharpe_proxy'] = np.where(
        substantial['capture_iqr'] > 0,
        substantial['capture_mean'] / substantial['capture_iqr'],
        np.nan
    )

# === Section 1: Top 30 by expected_value, in_match ===
print('-' * 100)
print('1. TOP 30 (cell, policy) BY EXPECTED VALUE (capture_mean × fire_rate) — in_match only')
print('   Per LESSONS E16: 95% of P&L lives in_match. This is the alpha-discovery primary lens.')
print('-' * 100)
inmatch = substantial[substantial['regime'] == 'in_match']
top_inmatch = inmatch.nlargest(30, 'expected_value')[
    ['regime', 'category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity',
     'policy_class', 'policy_param', 'n_simulated', 'fire_rate', 'capture_mean', 'capture_p90', 'expected_value']
]
print(top_inmatch.to_string(index=False))
print()

# === Section 2: Top 30 by expected_value, premarket ===
print('-' * 100)
print('2. TOP 30 (cell, policy) BY EXPECTED VALUE — premarket only')
print('   Per E16: only 5% of P&L; lower priority. But check for any cells with unusually high EV.')
print('-' * 100)
premarket = substantial[substantial['regime'] == 'premarket']
top_premarket = premarket.nlargest(30, 'expected_value')[
    ['regime', 'category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity',
     'policy_class', 'policy_param', 'n_simulated', 'fire_rate', 'capture_mean', 'capture_p90', 'expected_value']
]
print(top_premarket.to_string(index=False))
print()

# === Section 3: Top 30 by capture_p90 (tail-edge) in_match, limit-bearing only ===
print('-' * 100)
print('3. TOP 30 BY capture_p90 (TAIL EDGE) — in_match, limit-bearing policies only')
print('   Per LESSONS B21: time_stop trends opposite to MFE; limit policies capture MFE in mean-reverting markets.')
print('   capture_p90 isolates upper tail of the all-outcome distribution.')
print('-' * 100)
limit_inmatch = inmatch[inmatch['policy_class'].str.contains('limit', case=False, na=False)]
top_p90 = limit_inmatch.nlargest(30, 'capture_p90')[
    ['regime', 'category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity',
     'policy_class', 'policy_param', 'n_simulated', 'fire_rate', 'capture_mean', 'capture_p90', 'expected_value']
]
print(top_p90.to_string(index=False))
print()

# === Section 4: Per-category alpha summary ===
print('-' * 100)
print('4. PER-CATEGORY EXPECTED-VALUE SUMMARY (in_match, substantial cells)')
print('-' * 100)
for cat in sorted(inmatch['category'].unique()):
    sub = inmatch[inmatch['category'] == cat]
    print(f'\n{cat} ({len(sub):,} (cell, policy) rows):')
    print(f'  EV: median={sub["expected_value"].median():+.4f}, p75={sub["expected_value"].quantile(0.75):+.4f}, p95={sub["expected_value"].quantile(0.95):+.4f}, max={sub["expected_value"].max():+.4f}')
    print(f'  capture_mean: median={sub["capture_mean"].median():+.4f}')
    print(f'  fire_rate: median={sub["fire_rate"].median():.3f}')

# === Section 5: Policy-class alpha summary ===
print()
print('-' * 100)
print('5. PER-POLICY-CLASS EXPECTED-VALUE SUMMARY (in_match)')
print('-' * 100)
for pc in sorted(inmatch['policy_class'].unique()):
    sub = inmatch[inmatch['policy_class'] == pc]
    print(f'\n{pc} ({len(sub):,} rows):')
    print(f'  EV median: {sub["expected_value"].median():+.4f}')
    print(f'  EV p95: {sub["expected_value"].quantile(0.95):+.4f}')
    print(f'  capture_p90 median: {sub["capture_p90"].median():+.4f}')

print()
print('=' * 100)
print('END Cat 5 — top alpha-bearing (cell, policy) targets surfaced. Use these to focus T32b producer development.')
print('=' * 100)
