# ATP_MAIN exit reanalysis (raw peak_trade, no depth filter) — 2026-05-27 10:48 PM ET

**Single concern. Read-only on inputs. In-sample. No commit; candidate staged only if gated criteria pass.**

## Methodology
- **Universe:** atlas 4,137 N (ATP_MAIN), no F35 / no tier filter / no ROI floor / no imposed objective.
- **Per-N peak (corrected):** `max(price_high)*100` over `[match_start_ts, settlement_ts-300s]` from `per_minute_features.parquet` (sha 9fde4b5d). **Raw trade prints, NO `size_qual_max_250` depth filter** (the prior-prompt blocker). 6 of 4,137 N had no in-match trade (null peak → settlement-only); excluded from the R-sweep, noted.
- **Pair peak:** `legX_peak_trade_inmatch_cents` from the paired primitive (already `price_high`-derived) used as-is.
- **Cost basis (B):** `drift_envelope` has no explicit fill-price field. Used `cost_basis = anchor_cents - clip(drift_low_vs_anchor, 0, 5)` — the per-ticker premarket dip below anchor, **capped at 5c (conservative)**, floored at 0. Mean discount 3.3c (p25 2 / p50 3 / p75 5).
- **Hit rule:** `peak_trade >= anchor + R`. Exit (recovery) = `anchor + R`; else ride to settlement (`settle_value*100`). Per-contract PnL (cents) = recovery − cost_basis. `$` figures: `sum(pnl_cents)/100 * contracts`.
- **R selection per band:** sweep R=1..(99−band_high) + HOLD; pick max total-$ subject to `hit≥50% AND bootstrap-CI-upper>0 AND Sortino>0`; if none qualify → DISABLE (ride to settle). Bootstrap = 1000 resamples on mean PnL.

## Inputs verified
| input | sha (12) | rows |
|---|---|---|
| per_minute_features.parquet | 9fde4b5d30e5 | 9,330,878 |
| atp_main_spike_perN.parquet | 621c86340b90 | 4,137 |
| paired_primitive_v1/atp_main/primitive.parquet | 564c19382ad6 | 1,881 |
| atp_main_drift_envelope.parquet | fb61d47ee52a | 4,137 |
| atp_main_adaptive_exit_bands_v6.parquet | a9aee4ec1849 | 31 |

## C — v6 baseline (the honest floor)
- **Stated atlas baseline:** $1235.40 (in-sample; built on `size_qual_max_250` peak + anchor cost). **Not the right comparator here** — different peak/cost methodology.
- **v6 on 4,137 atoms, SAME method (raw peak + actual cost):** **$1830.9 @10ct** — this is the apples-to-apples single-leg floor.
- **v6 on 1,881 paired events (actual cost basis):**
  - per-leg total \$ (both legs) @10ct: **$1384.80**
  - pair total \$: **$1384.80 @10ct** / **$692.40 @5ct**
  - pair PnL (cents): mean 7.36, pctiles {10: -38.0, 25: -14.0, 50: 12.0, 75: 31.0, 90: 46.0}
  - pair ROI: mean 0.0789, pctiles {10: -0.38, 25: -0.14, 50: 0.12, 75: 0.32, 90: 0.48}

## D — band-partition strategies (single-leg, 4,137 atoms)
| strategy | bands | total \$ @10ct | total \$ @5ct | DISABLE bands | vs v6 same-method ($1831) | vs stated ($1235) |
|---|---|---|---|---|---|---|
| D1_fixed5c | 18 | $1857.6 | $928.8 | 0 | +26.7 | +622.2 |
| D2_fixed10c | 9 | $1696.1 | $848.1 | 0 | -134.8 | +460.7 |
| D3_dp_min300 | 12 | $1819.2 | $909.6 | 0 | -11.7 | +583.8 |
| D4_dp_min500 | 7 | $1646.3 | $823.1 | 0 | -184.6 | +410.9 |

**Best single-leg strategy: `D1_fixed5c` ($1857.6 @10ct, +$26.7 vs v6 same-method = +1.5%).**

### D1_fixed5c — per-band R picks
| band | N | anchor̄ | action | hit% | total \$@10ct | Sortino | CI95 lo | CI95 hi |
|---|---|---|---|---|---|---|---|---|
| 5-9 | 112 | 7.0 | 9 | 54% | $47.6 | 1.38 | 2.77 | 5.71 |
| 10-14 | 127 | 11.9 | 15 | 50% | $59.8 | 0.74 | 2.49 | 6.96 |
| 15-19 | 170 | 17.1 | 12 | 69% | $107.7 | 0.83 | 4.13 | 8.29 |
| 20-24 | 177 | 22.0 | 23 | 55% | $100.1 | 0.44 | 2.10 | 8.84 |
| 25-29 | 239 | 27.0 | 31 | 51% | $137.9 | 0.34 | 2.18 | 9.37 |
| 30-34 | 253 | 31.9 | 30 | 55% | $145.5 | 0.30 | 1.87 | 9.61 |
| 35-39 | 315 | 37.0 | 29 | 54% | $66.2 | 0.09 | -1.63 | 5.73 |
| 40-44 | 296 | 41.9 | 34 | 57% | $128.4 | 0.17 | -0.03 | 8.42 |
| 45-49 | 277 | 46.8 | 48 | 50% | $134.2 | 0.16 | -0.55 | 10.37 |
| 50-54 | 234 | 52.0 | 45 | 54% | $102.1 | 0.13 | -1.88 | 10.75 |
| 55-59 | 318 | 57.1 | 40 | 59% | $198.4 | 0.19 | 0.44 | 11.18 |
| 60-64 | 335 | 62.1 | 34 | 64% | $179.2 | 0.16 | 0.93 | 10.21 |
| 65-69 | 307 | 66.8 | 30 | 67% | $91.5 | 0.08 | -2.00 | 8.09 |
| 70-74 | 272 | 72.1 | 24 | 74% | $85.4 | 0.09 | -1.65 | 8.15 |
| 75-79 | 238 | 76.8 | 14 | 86% | $122.8 | 0.19 | 1.02 | 9.01 |
| 80-84 | 205 | 82.0 | 15 | 81% | $32.5 | 0.05 | -3.66 | 6.28 |
| 85-89 | 140 | 86.8 | 9 | 91% | $84.4 | 0.27 | 1.95 | 9.57 |
| 90-94 | 116 | 92.0 | 5 | 94% | $33.9 | 0.13 | -1.44 | 7.03 |

### D2_fixed10c — per-band R picks
| band | N | anchor̄ | action | hit% | total \$@10ct | Sortino | CI95 lo | CI95 hi |
|---|---|---|---|---|---|---|---|---|
| 5-14 | 239 | 9.6 | 12 | 51% | $104.8 | 0.89 | 3.03 | 5.80 |
| 15-24 | 347 | 19.6 | 12 | 70% | $192.6 | 0.61 | 4.08 | 7.03 |
| 25-34 | 492 | 29.6 | 30 | 54% | $276.9 | 0.31 | 2.86 | 8.22 |
| 35-44 | 611 | 39.4 | 31 | 55% | $181.3 | 0.12 | 0.13 | 5.75 |
| 45-54 | 511 | 49.2 | 45 | 52% | $222.1 | 0.14 | 0.14 | 8.27 |
| 55-64 | 653 | 59.7 | 34 | 64% | $353.1 | 0.16 | 1.74 | 8.95 |
| 65-74 | 579 | 69.3 | 24 | 72% | $124.5 | 0.06 | -1.00 | 5.75 |
| 75-84 | 443 | 79.2 | 14 | 84% | $147.6 | 0.11 | -0.01 | 6.25 |
| 85-94 | 256 | 89.2 | 5 | 94% | $93.2 | 0.18 | 0.74 | 6.18 |

### D3_dp_min300 — per-band R picks
| band | N | anchor̄ | action | hit% | total \$@10ct | Sortino | CI95 lo | CI95 hi |
|---|---|---|---|---|---|---|---|---|
| 5-18 | 379 | 12.2 | 12 | 58% | $195.5 | 0.86 | 3.94 | 6.31 |
| 19-27 | 343 | 23.3 | 23 | 55% | $182.1 | 0.39 | 2.90 | 7.72 |
| 28-35 | 425 | 31.6 | 30 | 57% | $281.5 | 0.35 | 3.87 | 9.62 |
| 36-40 | 309 | 38.0 | 3 | 87% | $23.3 | 0.06 | -0.83 | 2.19 |
| 41-46 | 359 | 43.5 | 48 | 52% | $265.5 | 0.27 | 2.81 | 11.95 |
| 47-54 | 385 | 50.4 | 11 | 81% | $113.5 | 0.15 | 0.36 | 5.10 |
| 55-59 | 318 | 57.1 | 40 | 59% | $198.4 | 0.19 | 1.20 | 11.18 |
| 60-64 | 335 | 62.1 | 34 | 64% | $179.2 | 0.16 | -0.00 | 10.01 |
| 65-69 | 307 | 66.8 | 30 | 67% | $91.5 | 0.08 | -1.88 | 8.05 |
| 70-75 | 324 | 72.6 | 24 | 73% | $100.9 | 0.09 | -1.66 | 7.64 |
| 76-82 | 306 | 78.7 | 14 | 84% | $83.3 | 0.09 | -1.36 | 6.32 |
| 83-94 | 341 | 87.8 | 5 | 94% | $104.5 | 0.15 | 0.62 | 5.52 |

### D4_dp_min500 — per-band R picks
| band | N | anchor̄ | action | hit% | total \$@10ct | Sortino | CI95 lo | CI95 hi |
|---|---|---|---|---|---|---|---|---|
| 5-25 | 635 | 16.2 | 12 | 63% | $323.8 | 0.64 | 3.97 | 6.12 |
| 26-35 | 512 | 30.7 | 30 | 55% | $313.5 | 0.33 | 3.65 | 8.76 |
| 36-44 | 542 | 39.9 | 34 | 53% | $147.7 | 0.11 | -0.50 | 5.80 |
| 45-54 | 511 | 49.2 | 45 | 52% | $222.1 | 0.14 | 0.43 | 8.32 |
| 55-62 | 509 | 58.6 | 37 | 61% | $261.9 | 0.15 | 1.46 | 9.27 |
| 63-71 | 555 | 66.6 | 28 | 70% | $219.5 | 0.12 | 0.41 | 7.56 |
| 72-94 | 867 | 81.0 | 4 | 93% | $157.8 | 0.09 | 0.32 | 3.13 |

## E — best single-leg strategy applied to the 1,881 paired events
- pair total \$: **$1356.50 @10ct** / **$678.25 @5ct**  (v6: $1384.80 / $692.40)
- pair PnL (cents): mean 7.21, pctiles {10: -32.0, 25: -5.0, 50: 0.0, 75: 25.0, 90: 63.0}
- pair ROI: mean 0.0776, pctiles {10: -0.33, 25: -0.05, 50: 0.0, 75: 0.26, 90: 0.64}

### E — deltas vs v6 baseline (C)
| metric | v6 | best | delta |
|---|---|---|---|
| pair median PnL (c) | 12.0 | 0.0 | **-12.0** |
| pair median ROI | 0.1224 | 0.0000 | **-0.1224** |
| pair p10 PnL (c) | -38.0 | -32.0 | +6.0 |
| pair mean PnL (c) | 7.36 | 7.21 | -0.15 |
| aggregate \$ @10ct | 1384.8 | 1356.5 | **-28.3** |
| aggregate \$ @5ct | 692.4 | 678.2 | -14.1 |
| pairs improved / degraded | — | — | 1104 / 696 |

## F — pair-aware diagnostic (descriptive only)
Band-pair buckets using `D1_fixed5c` partition. Top 20 by N:
| legA band | legB band | N | P(both) | P(Aonly) | P(Bonly) | P(none) | pair PnL med | pair ROI med |
|---|---|---|---|---|---|---|---|---|
| 55-59 | 45-49 | 171 | 0.09 | 0.52 | 0.37 | 0.01 | 0.0 | 0.000 |
| 65-69 | 35-39 | 167 | 0.26 | 0.43 | 0.31 | 0.00 | 0.0 | 0.000 |
| 60-64 | 40-44 | 157 | 0.18 | 0.46 | 0.34 | 0.02 | -2.0 | -0.020 |
| 75-79 | 25-29 | 128 | 0.34 | 0.48 | 0.17 | 0.00 | -5.0 | -0.052 |
| 70-74 | 30-34 | 125 | 0.31 | 0.49 | 0.20 | 0.00 | 0.0 | 0.000 |
| 60-64 | 35-39 | 114 | 0.22 | 0.49 | 0.28 | 0.01 | 1.0 | 0.010 |
| 55-59 | 40-44 | 106 | 0.20 | 0.38 | 0.42 | 0.01 | 1.0 | 0.010 |
| 65-69 | 30-34 | 95 | 0.19 | 0.42 | 0.39 | 0.00 | 1.0 | 0.010 |
| 70-74 | 25-29 | 94 | 0.24 | 0.44 | 0.30 | 0.02 | 1.0 | 0.010 |
| 80-84 | 20-24 | 88 | 0.38 | 0.48 | 0.15 | 0.00 | 2.0 | 0.021 |
| 85-89 | 15-19 | 85 | 0.52 | 0.39 | 0.09 | 0.00 | 24.0 | 0.245 |
| 50-54 | 45-49 | 80 | 0.05 | 0.45 | 0.49 | 0.01 | 1.5 | 0.016 |
| 80-84 | 15-19 | 68 | 0.54 | 0.25 | 0.21 | 0.00 | 29.5 | 0.301 |
| 75-79 | 20-24 | 63 | 0.49 | 0.41 | 0.10 | 0.00 | 1.0 | 0.011 |
| 90-94 | 10-14 | 60 | 0.48 | 0.47 | 0.05 | 0.00 | 14.5 | 0.150 |
| 50-54 | 50-54 | 51 | 0.04 | 0.33 | 0.61 | 0.02 | 1.0 | 0.010 |
| 85-89 | 10-14 | 48 | 0.42 | 0.48 | 0.10 | 0.00 | 5.5 | 0.060 |
| 90-94 | 5-9 | 42 | 0.38 | 0.48 | 0.14 | 0.00 | 4.0 | 0.042 |
| 65-69 | 40-44 | 10 | 0.00 | 0.70 | 0.30 | 0.00 | -4.0 | -0.040 |
| 55-59 | 50-54 | 10 | 0.00 | 0.30 | 0.70 | 0.00 | -1.0 | -0.010 |

### F — band-pair buckets with NEGATIVE median pair PnL (N≥10): 4
| legA band | legB band | N | pair PnL med | P(both) | P(none) |
|---|---|---|---|---|---|
| 60-64 | 40-44 | 157 | -2.0 | 0.18 | 0.02 |
| 75-79 | 25-29 | 128 | -5.0 | 0.34 | 0.00 |
| 65-69 | 40-44 | 10 | -4.0 | 0.00 | 0.00 |
| 55-59 | 50-54 | 10 | -1.0 | 0.00 | 0.00 |

### F — band-level R inversions (higher-anchor band carries a larger R than a lower-anchor band): **69**
Sample (lower band @R  vs  higher band @R):
- 5-9 @R9  <  10-14 @R15
- 5-9 @R9  <  15-19 @R12
- 5-9 @R9  <  20-24 @R23
- 10-14 @R15  <  20-24 @R23
- 15-19 @R12  <  20-24 @R23
- 5-9 @R9  <  25-29 @R31
- 10-14 @R15  <  25-29 @R31
- 15-19 @R12  <  25-29 @R31
- 20-24 @R23  <  25-29 @R31
- 5-9 @R9  <  30-34 @R30
- 10-14 @R15  <  30-34 @R30
- 15-19 @R12  <  30-34 @R30

## G — staging decision
- single-leg total \$ improves vs v6 (same method): **True** ($1857.6 vs $1830.9)
- pair median PnL improves vs v6: **False** (0.0 vs 12.0)
- catastrophic negative pair-bucket(s): **True** (4 buckets N≥10 with negative median)
- **DECISION: DO NOT STAGE the v7 candidate.**

### Gap (why not staged)
- Wider single-leg bands lift single-leg total \$ only marginally (+$26.7, +1.5%), and **only D1** beats v6; D2/D3/D4 are below v6 same-method.
- That single-leg gain **does not translate to pairs**: pair median PnL **-12.0c**, pair aggregate **$-28.3 @10ct** — both worse than v6.
- Per-band independent R optimization yields **69 R-inversions** and **4 negative-median pair buckets** — incoherent pair structure. v6's zone-aware R remains better at the pair level.

## Caveats (flagged)
- **In-sample.** Entire analysis is on the same atlas v6 was built on. Out-of-sample validation is a separate, required step before any deploy.
- **Raw-peak realism (Axis 1/2/3):** hit uses `peak_trade = max(price_high)` with NO depth qualification — assumes a resting sell fills if ANY trade prints at/above it. Real fills depend on size at that print; thin prints may not fill the full 10ct. This inflates hit rates/total-$ uniformly across v6 and candidate (cancels in deltas, but absolute $ are optimistic).
- **Drift-discount cost basis:** `anchor − clip(dip,0,5)`. The 5c cap is a conservative bound on premarket entry improvement; the true maker fill depends on the bot's posted bid offset, not the observed envelope minimum. Applied identically to v6 and candidate.
- **Bootstrap CI overlaps:** for many bands, adjacent R picks have overlapping 95% CIs on mean PnL — the chosen R is often statistically indeterminate vs neighbors (the per-band tables show the bounds; treat single-cent R picks as soft).
- **Single-leg vs pair divergence is the headline:** optimizing per-band single-leg total-\$ is not equivalent to optimizing pair-level outcome; this analysis demonstrates they diverge for ATP_MAIN.
