# Per-Cell Exit Optimization v2 — Winning-Side Implication Fix
Generated: 2026-04-22 09:26:16 PM ET

## Methodology

- Same pregame-close detection as v1
- **FIX: Winning-side logical implication**
  - If side settled at 100 (winner) AND target <= 100: HIT (price path from entry to 100 must cross target)
  - If target > 100: MISS (scalp impossible)
  - If side settled at 0 (loser): check tick data max_bounce for target crossing
- Price field: mid = (bid + ask) / 2 for tick-based checks. Winning-side uses logical implication, not tick data.

## Data Coverage

- Total trades: 1574
- Distinct trading days: 34
- Excluded: {'no_settlement': 596, 'no_ticks': 193, 'bad_entry': 1, 'no_category': 0}

## v1 vs v2 Diff — Material Changes

Criteria: HR change >10%, mean_pnl change >3c, or optimal_X change >5

| Cell | v1 opt | v2 opt | v1 HR | v2 HR | v1 pnl | v2 pnl | Flag |
|------|--------|--------|-------|-------|--------|--------|------|
| WTA_CHALL 85-89 | +14c | +14c | 0.0% | 100.0% | 14.0c | 14.0c | HR |
| WTA_CHALL 90-94 | +10c | +10c | 0.0% | 25.0% | 8.5c | 8.5c | HR |

Material changes: 2 cells

## ATP_MAIN

| Bucket | Status | N | Cur Exit | Opt Exit | HR | Avg Entry | Mean PnL | ROI% | EV/day | Delta |
|--------|--------|---|----------|----------|-----|-----------|----------|------|--------|-------|
| 0-4 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 5-9 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 10-14 | MISSING | 3 | - | +35c | 100% | 14.0c | +35.0c | 250.0% | 3.1 |  |
| 15-19 | MISSING | 11 | - | +32c | 100% | 16.8c | +32.0c | 190.3% | 10.3 |  |
| 20-24 | ACTIVE | 24 | 25c | +25c | 96% | 22.2c | +23.0c | 103.2% | 16.2 | +0.0 |
| 25-29 | ACTIVE | 13 | 23c | +22c | 85% | 26.5c | +14.7c | 55.4% | 5.6 | +3.1 |
| 30-34 | ACTIVE | 33 | 15c | +15c | 97% | 32.6c | +13.6c | 41.6% | 13.2 | +0.0 |
| 35-39 | ACTIVE | 34 | 12c | +12c | 94% | 37.5c | +9.1c | 24.2% | 9.1 | +0.0 |
| 40-44 | ACTIVE | 38 | 7c | +9c | 89% | 41.8c | +3.5c | 8.4% | 3.9 | +0.5 |
| 45-49 | MISSING | 13 | - | +4c | 92% | 46.8c | -0.1c | -0.2% | -0.0 |  |
| 50-54 | MISSING | 6 | - | +12c | 100% | 53.2c | +12.0c | 22.6% | 2.1 |  |
| 55-59 | DISABLED | 15 | - | +9c | 67% | 57.0c | -12.9c | -22.7% | -5.7 |  |
| 60-64 | ACTIVE | 54 | 13c | +8c | 85% | 62.5c | -2.5c | -4.1% | -4.0 | -0.1 |
| 65-69 | ACTIVE | 29 | 5c | +3c | 93% | 67.2c | -1.8c | -2.7% | -1.6 | +3.2 |
| 70-74 | ACTIVE | 30 | 10c | +25c | 80% | 71.8c | +5.7c | 8.0% | 5.1 | +3.9 |
| 75-79 | ACTIVE | 20 | 17c | +14c | 85% | 77.0c | +0.5c | 0.6% | 0.3 | +7.0 |
| 80-84 | MISSING | 10 | - | +15c | 90% | 81.8c | +5.1c | 6.2% | 1.5 |  |
| 85-89 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 90-94 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 95-99 | MISSING | 0 | - | - | - | - | - | - | - | - |

## ATP_CHALL

| Bucket | Status | N | Cur Exit | Opt Exit | HR | Avg Entry | Mean PnL | ROI% | EV/day | Delta |
|--------|--------|---|----------|----------|-----|-----------|----------|------|--------|-------|
| 0-4 | MISSING | 1 | - | +4c | 100% | 2.0c | +4.0c | 200.0% | 0.1 |  |
| 5-9 | MISSING | 3 | - | +35c | 100% | 7.3c | +35.0c | 477.3% | 3.1 |  |
| 10-14 | MISSING | 19 | - | +35c | 89% | 12.5c | +29.9c | 240.1% | 16.7 |  |
| 15-19 | ACTIVE | 36 | 31c | +31c | 94% | 17.4c | +28.4c | 163.3% | 30.1 | +0.0 |
| 20-24 | ACTIVE | 69 | 25c | +25c | 99% | 22.3c | +24.3c | 109.1% | 49.4 | +0.0 |
| 25-29 | ACTIVE | 54 | 21c | +21c | 100% | 26.8c | +21.0c | 78.3% | 33.4 | +0.0 |
| 30-34 | ACTIVE | 73 | 16c | +15c | 100% | 32.1c | +15.0c | 46.7% | 32.2 | +0.4 |
| 35-39 | ACTIVE | 56 | 12c | +11c | 100% | 37.1c | +11.0c | 29.6% | 18.1 | +0.8 |
| 40-44 | ACTIVE | 86 | 10c | +8c | 93% | 41.9c | +4.4c | 10.6% | 11.2 | +1.2 |
| 45-49 | ACTIVE | 58 | 6c | +13c | 86% | 46.2c | +4.8c | 10.5% | 8.3 | +3.4 |
| 50-54 | MISSING | 30 | - | +33c | 67% | 51.0c | +5.2c | 10.1% | 4.6 |  |
| 55-59 | ACTIVE | 38 | 6c | +3c | 97% | 57.9c | +1.4c | 2.4% | 1.5 | +0.5 |
| 60-64 | ACTIVE | 98 | 10c | +6c | 96% | 62.1c | +3.2c | 5.2% | 9.3 | +1.3 |
| 65-69 | ACTIVE | 34 | 10c | +6c | 97% | 67.0c | +3.8c | 5.7% | 3.8 | +2.8 |
| 70-74 | ACTIVE | 82 | 11c | +6c | 95% | 71.7c | +2.2c | 3.1% | 5.3 | +2.3 |
| 75-79 | ACTIVE | 47 | 19c | +19c | 91% | 76.8c | +10.8c | 14.1% | 15.0 | +0.0 |
| 80-84 | ACTIVE | 63 | 15c | +15c | 89% | 81.6c | +4.3c | 5.3% | 8.1 | +0.0 |
| 85-89 | ACTIVE | 15 | 11c | +7c | 93% | 86.4c | +0.6c | 0.7% | 0.3 | +2.7 |
| 90-94 | MISSING | 1 | - | +3c | 0% | 90.0c | -90.0c | -100.0% | -2.6 |  |
| 95-99 | MISSING | 1 | - | +4c | 0% | 96.0c | +4.0c | 4.2% | 0.1 |  |

## WTA_MAIN

| Bucket | Status | N | Cur Exit | Opt Exit | HR | Avg Entry | Mean PnL | ROI% | EV/day | Delta |
|--------|--------|---|----------|----------|-----|-----------|----------|------|--------|-------|
| 0-4 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 5-9 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 10-14 | MISSING | 10 | - | +32c | 90% | 12.5c | +27.8c | 222.4% | 8.2 |  |
| 15-19 | ACTIVE | 12 | 31c | +31c | 75% | 17.3c | +19.2c | 110.6% | 6.8 | +0.0 |
| 20-24 | ACTIVE | 15 | 25c | +22c | 87% | 22.1c | +16.3c | 73.5% | 7.2 | +0.4 |
| 25-29 | ACTIVE | 24 | 21c | +21c | 92% | 26.9c | +17.1c | 63.6% | 12.1 | +0.0 |
| 30-34 | ACTIVE | 23 | 16c | +16c | 96% | 31.7c | +13.9c | 43.8% | 9.4 | +0.0 |
| 35-39 | ACTIVE | 20 | 12c | +11c | 90% | 36.7c | +6.2c | 16.9% | 3.6 | +1.6 |
| 40-44 | ACTIVE | 34 | 5c | +5c | 94% | 42.2c | +2.2c | 5.2% | 2.2 | +0.0 |
| 45-49 | ACTIVE | 26 | 14c | +13c | 85% | 46.7c | +3.9c | 8.3% | 3.0 | +1.5 |
| 50-54 | ACTIVE | 25 | 26c | +3c | 96% | 50.9c | +0.7c | 1.4% | 0.5 | +5.4 |
| 55-59 | DISABLED | 13 | - | +4c | 85% | 57.2c | -5.5c | -9.6% | -2.1 |  |
| 60-64 | ACTIVE | 20 | 8c | +34c | 65% | 62.0c | +0.4c | 0.7% | 0.2 | +10.0 |
| 65-69 | DISABLED | 24 | - | +23c | 75% | 67.1c | +0.4c | 0.6% | 0.3 |  |
| 70-74 | ACTIVE | 28 | 15c | +26c | 75% | 72.1c | +5.0c | 6.9% | 4.1 | +5.5 |
| 75-79 | MISSING | 9 | - | +3c | 100% | 76.9c | +3.0c | 3.9% | 0.8 |  |
| 80-84 | ACTIVE | 18 | 15c | +17c | 67% | 81.3c | +0.6c | 0.7% | 0.3 | +1.5 |
| 85-89 | DISABLED | 16 | - | +14c | 19% | 87.3c | +6.4c | 7.4% | 3.0 |  |
| 90-94 | MISSING | 2 | - | +10c | 0% | 91.0c | +9.0c | 9.9% | 0.5 |  |
| 95-99 | MISSING | 0 | - | - | - | - | - | - | - | - |

## WTA_CHALL

| Bucket | Status | N | Cur Exit | Opt Exit | HR | Avg Entry | Mean PnL | ROI% | EV/day | Delta |
|--------|--------|---|----------|----------|-----|-----------|----------|------|--------|-------|
| 0-4 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 5-9 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 10-14 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 15-19 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 20-24 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 25-29 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 30-34 | MISSING | 1 | - | +20c | 100% | 34.0c | +20.0c | 58.8% | 0.6 |  |
| 35-39 | MISSING | 5 | - | +11c | 100% | 38.2c | +11.0c | 28.8% | 1.6 |  |
| 40-44 | MISSING | 24 | - | +35c | 71% | 42.3c | +12.3c | 29.1% | 8.7 |  |
| 45-49 | MISSING | 6 | - | +25c | 83% | 46.8c | +12.7c | 27.1% | 2.2 |  |
| 50-54 | MISSING | 10 | - | +15c | 80% | 50.2c | +2.0c | 4.0% | 0.6 |  |
| 55-59 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 60-64 | MISSING | 5 | - | +9c | 80% | 62.6c | -5.6c | -8.9% | -0.8 |  |
| 65-69 | MISSING | 2 | - | +9c | 100% | 66.0c | +9.0c | 13.6% | 0.5 |  |
| 70-74 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 75-79 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 80-84 | MISSING | 0 | - | - | - | - | - | - | - | - |
| 85-89 | MISSING | 1 | - | +14c | 100% | 86.0c | +14.0c | 16.3% | 0.4 |  |
| 90-94 | MISSING | 4 | - | +10c | 25% | 91.5c | +8.5c | 9.3% | 1.0 |  |
| 95-99 | MISSING | 0 | - | - | - | - | - | - | - | - |

## Validation

- Total trades: 1574
- Winning-side trades (implication applied): 609
- Losing-side trades (tick-checked): 965
- Sum of N across cells: 1574

### Symmetry
- ATP_MAIN: N(0-49)=169, N(50-99)=164, ratio=1.03
- ATP_CHALL: N(0-49)=455, N(50-99)=409, ratio=1.11
- WTA_MAIN: N(0-49)=164, N(50-99)=155, ratio=1.06
- WTA_CHALL: N(0-49)=36, N(50-99)=22, ratio=1.64

Full sweep: per_cell_exit_sweep_full_v2.csv (2013 rows)

