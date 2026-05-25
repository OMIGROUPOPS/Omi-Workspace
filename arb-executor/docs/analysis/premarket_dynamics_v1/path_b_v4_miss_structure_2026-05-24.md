# Path B v4 tick-replay — structural breakdown of misses (2026-05-24)

Read-only on `path_b_v4_tick_replay_historical_perN.parquet` (N=14033). A 'miss' = `miss_fallback` (no marketable-taker at placement AND no `taker_side=='no'` sell-trade at/below bid by T-20m → fallback taker at the atlas anchor).

## V4 misses — total 5839/14033 (41.6% miss rate)

### 1. By category

| category | N | misses | miss rate |
|---|---|---|---|
| ATP_MAIN | 4137 | 1153 | 27.9% |
| WTA_MAIN | 3683 | 1459 | 39.6% |
| ATP_CHALL | 5326 | 2776 | 52.1% |
| WTA_CHALL | 887 | 451 | 50.8% |

### 2. Miss rate by category × regime (10c band)

| category | r05_14 | r15_24 | r25_34 | r35_44 | r45_54 | r55_64 | r65_74 | r75_84 | r85_94 |
|---|---|---|---|---|---|---|---|---|---|
| ATP_MAIN | 17% | 44% | 19% | 21% | 36% | 30% | 9% | 64% | 8% |
| WTA_MAIN | 43% | 24% | 24% | 40% | 24% | 86% | 26% | 64% | 9% |
| ATP_CHALL | 58% | 39% | 46% | 61% | 79% | 67% | 33% | 41% | 41% |
| WTA_CHALL | 37% | 48% | 83% | 40% | 46% | 47% | 69% | 62% | 13% |

### 3. Misses by placement-mode
- not_marketable_at_placement (waited for a sell-trade, none arrived): **5839/5839 (100.0%)**
- marketable_at_placement but still miss (should be 0 by construction): **0**

### 4. Miss rate by placement_minute

| placement_minute | N | misses | miss rate |
|---|---|---|---|
| T-60 | 1822 | 848 | 46.5% |
| T-90 | 2314 | 1175 | 50.8% |
| T-120 | 2476 | 1015 | 41.0% |
| T-180 | 3778 | 1573 | 41.6% |
| T-240 | 3643 | 1228 | 33.7% |

### 5. Observed miss rate vs (1 − expected_fill_rate from v2.csv)

| category | regime | N | obs_miss% | 1−exp_fill% | divergence_pp |
|---|---|---|---|---|---|
| ATP_MAIN | r05_14 | 242 | 17% | 22% | -5 |
| ATP_MAIN | r15_24 | 348 | 44% | 46% | -1 |
| ATP_MAIN | r25_34 | 492 | 19% | 21% | -1 |
| ATP_MAIN | r35_44 | 611 | 21% | 16% | +5 |
| ATP_MAIN | r45_54 | 511 | 36% | 34% | +2 |
| ATP_MAIN | r55_64 | 653 | 30% | 33% | -3 |
| ATP_MAIN | r65_74 | 579 | 9% | 8% | +2 |
| ATP_MAIN | r75_84 | 443 | 64% | 64% | +0 |
| ATP_MAIN | r85_94 | 258 | 8% | 8% | +0 |
| WTA_MAIN | r05_14 | 255 | 43% | 44% | -2 |
| WTA_MAIN | r15_24 | 358 | 24% | 22% | +2 |
| WTA_MAIN | r25_34 | 421 | 24% | 20% | +4 |
| WTA_MAIN | r35_44 | 477 | 40% | 40% | +1 |
| WTA_MAIN | r45_54 | 502 | 24% | 22% | +3 |
| WTA_MAIN | r55_64 | 535 | 86% | 86% | -0 |
| WTA_MAIN | r65_74 | 489 | 26% | 22% | +4 |
| WTA_MAIN | r75_84 | 369 | 64% | 63% | +1 |
| WTA_MAIN | r85_94 | 277 | 9% | 7% | +2 |
| ATP_CHALL | r05_14 | 426 | 58% | 61% | -4 |
| ATP_CHALL | r15_24 | 501 | 39% | 38% | +1 |
| ATP_CHALL | r25_34 | 614 | 46% | 44% | +2 |
| ATP_CHALL | r35_44 | 682 | 61% | 57% | +3 |
| ATP_CHALL | r45_54 | 607 | 79% | 77% | +2 |
| ATP_CHALL | r55_64 | 772 | 67% | 66% | +1 |
| ATP_CHALL | r65_74 | 769 | 33% | 29% | +4 |
| ATP_CHALL | r75_84 | 525 | 41% | 39% | +2 |
| ATP_CHALL | r85_94 | 430 | 41% | 39% | +2 |
| WTA_CHALL | r05_14 | 82 | 37% | 49% | -12 ⚠ |
| WTA_CHALL | r15_24 | 75 | 48% | 53% | -5 |
| WTA_CHALL | r25_34 | 104 | 83% | 77% | +6 |
| WTA_CHALL | r35_44 | 112 | 40% | 33% | +7 |
| WTA_CHALL | r45_54 | 95 | 46% | 36% | +11 ⚠ |
| WTA_CHALL | r55_64 | 142 | 47% | 42% | +5 |
| WTA_CHALL | r65_74 | 118 | 69% | 68% | +2 |
| WTA_CHALL | r75_84 | 82 | 62% | 59% | +4 |
| WTA_CHALL | r85_94 | 77 | 13% | 9% | +4 |

Mean |divergence| = 3.2pp; cells >10pp off flagged ⚠ (single-cell sampling variance).

## V3 misses — total 10170/14033 (72.5% miss rate)

### 1. By category

| category | N | misses | miss rate |
|---|---|---|---|
| ATP_MAIN | 4137 | 3006 | 72.7% |
| WTA_MAIN | 3683 | 2815 | 76.4% |
| ATP_CHALL | 5326 | 3701 | 69.5% |
| WTA_CHALL | 887 | 648 | 73.1% |

### 2. Miss rate by category × regime (10c band)

| category | r05_14 | r15_24 | r25_34 | r35_44 | r45_54 | r55_64 | r65_74 | r75_84 | r85_94 |
|---|---|---|---|---|---|---|---|---|---|
| ATP_MAIN | 40% | 77% | 85% | 38% | 88% | 90% | 86% | 69% | 60% |
| WTA_MAIN | 43% | 74% | 85% | 87% | 79% | 85% | 80% | 71% | 59% |
| ATP_CHALL | 58% | 70% | 57% | 84% | 87% | 44% | 88% | 72% | 59% |
| WTA_CHALL | 38% | 67% | 84% | 81% | 80% | 87% | 79% | 61% | 60% |

### 3. Misses by placement-mode
- not_marketable_at_placement (waited for a sell-trade, none arrived): **10170/10170 (100.0%)**
- marketable_at_placement but still miss (should be 0 by construction): **0**

### 4. Miss rate by placement_minute

| placement_minute | N | misses | miss rate |
|---|---|---|---|
| T-90 | 826 | 701 | 84.9% |
| T-120 | 511 | 397 | 77.7% |
| T-180 | 4786 | 3747 | 78.3% |
| T-240 | 7910 | 5325 | 67.3% |

### 5. Observed miss rate vs (1 − expected_fill_rate from v1.csv)

| category | regime | N | obs_miss% | 1−exp_fill% | divergence_pp |
|---|---|---|---|---|---|
| ATP_MAIN | r05_14 | 242 | 40% | 47% | -7 |
| ATP_MAIN | r15_24 | 348 | 77% | 76% | +0 |
| ATP_MAIN | r25_34 | 492 | 85% | 85% | -0 |
| ATP_MAIN | r35_44 | 611 | 38% | 37% | +1 |
| ATP_MAIN | r45_54 | 511 | 88% | 88% | +0 |
| ATP_MAIN | r55_64 | 653 | 90% | 88% | +1 |
| ATP_MAIN | r65_74 | 579 | 86% | 85% | +1 |
| ATP_MAIN | r75_84 | 443 | 69% | 68% | +1 |
| ATP_MAIN | r85_94 | 258 | 60% | 58% | +2 |
| WTA_MAIN | r05_14 | 255 | 43% | 44% | -2 |
| WTA_MAIN | r15_24 | 358 | 74% | 73% | +1 |
| WTA_MAIN | r25_34 | 421 | 85% | 85% | +0 |
| WTA_MAIN | r35_44 | 477 | 87% | 86% | +1 |
| WTA_MAIN | r45_54 | 502 | 79% | 78% | +1 |
| WTA_MAIN | r55_64 | 535 | 85% | 84% | +1 |
| WTA_MAIN | r65_74 | 489 | 80% | 78% | +1 |
| WTA_MAIN | r75_84 | 369 | 71% | 71% | +1 |
| WTA_MAIN | r85_94 | 277 | 59% | 57% | +1 |
| ATP_CHALL | r05_14 | 426 | 58% | 61% | -4 |
| ATP_CHALL | r15_24 | 501 | 70% | 71% | -0 |
| ATP_CHALL | r25_34 | 614 | 57% | 55% | +1 |
| ATP_CHALL | r35_44 | 682 | 84% | 82% | +2 |
| ATP_CHALL | r45_54 | 607 | 87% | 86% | +1 |
| ATP_CHALL | r55_64 | 772 | 44% | 43% | +2 |
| ATP_CHALL | r65_74 | 769 | 88% | 86% | +2 |
| ATP_CHALL | r75_84 | 525 | 72% | 71% | +1 |
| ATP_CHALL | r85_94 | 430 | 59% | 53% | +5 |
| WTA_CHALL | r05_14 | 82 | 38% | 49% | -11 ⚠ |
| WTA_CHALL | r15_24 | 75 | 67% | 65% | +1 |
| WTA_CHALL | r25_34 | 104 | 84% | 77% | +7 |
| WTA_CHALL | r35_44 | 112 | 81% | 79% | +2 |
| WTA_CHALL | r45_54 | 95 | 80% | 77% | +3 |
| WTA_CHALL | r55_64 | 142 | 87% | 85% | +3 |
| WTA_CHALL | r65_74 | 118 | 79% | 80% | -1 |
| WTA_CHALL | r75_84 | 82 | 61% | 61% | -0 |
| WTA_CHALL | r85_94 | 77 | 60% | 55% | +5 |

Mean |divergence| = 2.1pp; cells >10pp off flagged ⚠ (single-cell sampling variance).

## 6. Median realized PnL — misses vs fills, per category (v4, per-contract cents ×10ct = the realized_pnl_v4 column already in $-at-10ct/... actually column is dollars)

| category | median PnL (fills) | median PnL (misses) | mean PnL fills | mean PnL misses | N fills | N miss |
|---|---|---|---|---|---|---|
| ATP_MAIN | 0.400 | 0.500 | 0.520 | 0.420 | 2984 | 1153 |
| WTA_MAIN | 0.700 | 1.000 | 0.733 | 0.401 | 2224 | 1459 |
| ATP_CHALL | 0.800 | 0.900 | 0.652 | 0.373 | 2550 | 2776 |
| WTA_CHALL | 0.700 | 0.900 | 0.842 | 0.810 | 436 | 451 |

(realized_pnl_v4 is net $ at 10ct sizing per leg. Misses enter at the atlas anchor and apply the same cell-X exit, so a PnL gap reflects WHICH legs miss — e.g. if low-fill cells are also lower-PnL cells — not a penalty from missing per se.)

## Key reads
- v4 misses 5839 vs v3 misses 10170: v4 converts **4331** v3-misses into fills.
- Legs missed by BOTH v3 and v4: 5624. Missed by v3 but FILLED by v4: 4546. Missed by v4 but filled by v3: 215.
- All v4 misses are not-marketable-at-placement legs (by construction); the miss is purely 'no counterparty sell-trade hit the resting bid by T-20m'.