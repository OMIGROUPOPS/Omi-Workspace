"""
Cat 2: Empirical fee table from kalshi_fills_history.json.
Validates layer_c_spec.md Decision 1: empirical maker + taker fees per (is_taker, yes_price_bucket).
Computes:
- Per (is_taker, price-bucket) median + mean + count
- Confirms parabolic shape vs |P-0.50|
- Surface any anomalous rows (e.g., maker fee > $1, very high taker fees)
Output: ASCII tables.
"""
import json
import pandas as pd
import numpy as np
from collections import defaultdict

print('=' * 100)
print('Cat 2: EMPIRICAL FEE TABLE from kalshi_fills_history.json')
print('Validates layer_c_spec.md Decision 1 (empirical fees per (is_taker, yes_price_bucket); NOT maker-zero).')
print('=' * 100)
print()

with open('data/durable/kalshi_fills_history.json') as f:
    raw = json.load(f)

fills = raw if isinstance(raw, list) else (raw.get('fills') or list(raw.values())[0])
print(f'Total fills: {len(fills):,}')

df = pd.DataFrame(fills)
print(f'Columns: {sorted(df.columns.tolist())}')
print()

# Fee field probe + price field probe
fee_col = 'fee_cost' if 'fee_cost' in df.columns else None
taker_col = 'is_taker' if 'is_taker' in df.columns else None
# Probe yes_price field — could be yes_price_dollars, yes_price, price_dollars, price
yes_price_col = None
for candidate in ['yes_price_dollars', 'yes_price', 'price_dollars', 'price']:
    if candidate in df.columns:
        yes_price_col = candidate
        break

if not fee_col or not taker_col or not yes_price_col:
    print(f'ABORT: missing required columns. Have fee={fee_col}, taker={taker_col}, yes_price={yes_price_col}')
    print(f'Available: {sorted(df.columns.tolist())}')
    raise SystemExit(1)

print(f'Using fee_col={fee_col}, taker_col={taker_col}, yes_price_col={yes_price_col}')
print()

# Coerce numeric
df[fee_col] = pd.to_numeric(df[fee_col], errors='coerce')
df[yes_price_col] = pd.to_numeric(df[yes_price_col], errors='coerce')
df = df.dropna(subset=[fee_col, taker_col, yes_price_col]).copy()
print(f'After dropna on key cols: {len(df):,}')
print()

# Buckets: 5c-wide, [0,5), [5,10), ..., [95,100), [100, 100+]
df['price_cents'] = (df[yes_price_col] * 100).round().astype(int)
df['price_bucket'] = pd.cut(
    df['price_cents'],
    bins=[-1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 200],
    labels=['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50',
            '50-55', '55-60', '60-65', '65-70', '70-75', '75-80', '80-85', '85-90', '90-95', '95+']
)
df['distance_from_50'] = (df['price_cents'] - 50).abs()

# === Section 1: Overall fee distribution ===
print('-' * 100)
print('1. OVERALL FEE DISTRIBUTION')
print('-' * 100)
for is_taker, label in [(True, 'TAKER'), (False, 'MAKER')]:
    sub = df[df[taker_col] == is_taker]
    print(f'\n{label} ({len(sub):,} fills):')
    print(f'  fee_cost: median=${sub[fee_col].median():.4f}, mean=${sub[fee_col].mean():.4f}, max=${sub[fee_col].max():.4f}')
    print(f'  Non-zero fees: {(sub[fee_col] > 0).sum()} ({(sub[fee_col] > 0).mean()*100:.1f}%)')

# === Section 2: Per-bucket median fee table (validates parabolic shape) ===
print()
print('-' * 100)
print('2. PER-BUCKET MEDIAN FEE — TAKER (validates parabolic vs |P-0.50|)')
print('-' * 100)
taker_table = df[df[taker_col] == True].groupby('price_bucket').agg(
    n=(fee_col, 'count'),
    median_fee=(fee_col, 'median'),
    mean_fee=(fee_col, 'mean'),
    max_fee=(fee_col, 'max'),
).round(4)
print(taker_table.to_string())
print()

print('-' * 100)
print('3. PER-BUCKET MEDIAN FEE — MAKER (validates parabolic vs |P-0.50|; NOT zero)')
print('-' * 100)
maker_table = df[df[taker_col] == False].groupby('price_bucket').agg(
    n=(fee_col, 'count'),
    median_fee=(fee_col, 'median'),
    mean_fee=(fee_col, 'mean'),
    max_fee=(fee_col, 'max'),
).round(4)
print(maker_table.to_string())
print()

# === Section 4: Taker:maker ratio at 50c peak (Decision 1 Check) ===
print('-' * 100)
print('4. TAKER:MAKER RATIO AT 50¢ PEAK (validates Check 2 of layer_c_spec.md: ratio >= 3)')
print('-' * 100)
peak_taker = df[(df[taker_col] == True) & (df['distance_from_50'] <= 5)]
peak_maker = df[(df[taker_col] == False) & (df['distance_from_50'] <= 5)]
if len(peak_taker) > 0 and len(peak_maker) > 0:
    t_med = peak_taker[fee_col].median()
    m_med = peak_maker[fee_col].median()
    ratio = t_med / m_med if m_med > 0 else float('inf')
    print(f'Taker median at distance<=5c: ${t_med:.4f} (n={len(peak_taker)})')
    print(f'Maker median at distance<=5c: ${m_med:.4f} (n={len(peak_maker)})')
    print(f'Ratio: {ratio:.2f}x (Check 2 expects >= 3)')

# === Section 5: Anomalies ===
print()
print('-' * 100)
print('5. ANOMALOUS FEES (worth flagging)')
print('-' * 100)
high_maker = df[(df[taker_col] == False) & (df[fee_col] > 0.5)]
print(f'\nMaker fills with fee > $0.50: {len(high_maker)}')
if len(high_maker) > 0:
    print(high_maker[['price_cents', fee_col]].head(10).to_string(index=False))

print()
print('=' * 100)
print('END Cat 2 — empirical fee table validated for Decision 1.')
print('=' * 100)
