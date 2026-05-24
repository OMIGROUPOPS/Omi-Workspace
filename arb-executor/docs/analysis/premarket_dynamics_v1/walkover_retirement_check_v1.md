> **SUPERSEDE NOTE (2026-05-23):** This analysis used a duration-proxy (settlement_ts − match_start_ts) to classify walkover/retirement events. The duration proxy conflates true walkovers (3-5% of corpus) with fast straight-set wins and Kalshi settlement-lag noise, producing an inflated 17-25% "reversal-prone" classification. Per operator pushback: the atlas (T42) already accounts for reversal events by construction — its +8.70% measured return IS net of reversal-driven losses. Recomputing T4 drift gradient excluding "reversal-prone" events answers the wrong question; the gradient including all events is the operating reality the strategy trades against. **The methodology conclusion of this doc (T4 gradient is "not robust") is invalid.** The corpus T4 gradient is robust as the strategy operates net of reversals.

# Walkover / retirement frequency sanity check (Round 5 Failure Mode 1 quantification)

**Date:** 2026-05-23
**Concern:** Is the Scope A T4 mid-drift gradient (±~11c across anchor regimes) robust to
walkover/retirement (reversal) events, or do reversal events materially distort the corpus
aggregate? Quick duration-based sanity check, not a per-event classifier.

## Sources (read-only)

| Artifact | sha256 | role |
|----------|--------|------|
| `premarket_tape_v1.parquet` | `ff2a63d9951d1a3d6b80044106c96ca9fdfd8d3951590e73eec1b46209c5a214` | mid_close at window endpoints for the T4 recompute |
| `{atp_main,wta_main,atp_chall,wta_chall}_spike_perN.parquet` | (4 atlas files) | anchor_ts, settlement_ts (durations), anchor_price (banding) |

**Methodology.** Per atlas ticker, `est_match_duration_min = (settlement_ts − anchor_ts)/60 − 20`
(subtracting the 20-min T-20m→start window). Duration bins: `short_match` <30 min (walkover /
first-set retirement), `truncated_match` 30–60 min (likely mid-match retirement), `normal_match`
60–300 min (typical completion), `outlier_long` >300 min (suspended/resumed; data-quality flag).
"Reversal-prone" = short + truncated. T4 mid_drift = (mid at the leg's latest window minute, ≈T-20m)
− (mid at its earliest, ≈T-4h), in cents, mean per (category × 10c anchor_regime) cell — identical
methodology to Scope A T4 (the full-corpus recompute below reproduces the published gradient
exactly, validating the method).

## Section 1 — Walkover/retirement frequency by category

| Category | total N | short (<30m) | truncated (30–60m) | normal (60–300m) | outlier (>300m) | reversal-prone (short+trunc) |
|----------|--------:|-------------:|-------------------:|-----------------:|----------------:|-----------------------------:|
| ATP_MAIN | 4,137 | 232 (5.6%) | 502 (12.1%) | 3,308 (80.0%) | 95 (2.3%) | **734 (17.7%)** |
| WTA_MAIN | 3,683 | 251 (6.8%) | 538 (14.6%) | 2,811 (76.3%) | 83 (2.3%) | **789 (21.4%)** |
| ATP_CHALL | 5,326 | 361 (6.8%) | 892 (16.7%) | 4,012 (75.3%) | 61 (1.1%) | **1,253 (23.5%)** |
| WTA_CHALL | 887 | 60 (6.8%) | 162 (18.3%) | 642 (72.4%) | 23 (2.6%) | **222 (25.0%)** |

Reversal-prone share rises Main→Challenger and ATP→WTA, from 17.7% (ATP_MAIN) to 25.0% (WTA_CHALL).
No null-timestamp tickers. (Per the disclosure, this duration proxy over-counts retirements — some
short matches are genuine quick straight-set wins.)

## Section 2 — T4 mid-drift gradient (cents), completed-matches-only (normal_match)

| Category | r05_14 | r15_24 | r25_34 | r35_44 | r45_54 | r55_64 | r65_74 | r75_84 | r85_94 |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| ATP_MAIN | -5.05 | -3.91 | -1.97 | -1.18 | -0.15 | 1.04 | 1.73 | 3.45 | 6.31 |
| WTA_MAIN | -5.04 | -4.00 | -2.65 | -1.74 | -0.01 | 1.37 | 1.98 | 3.83 | 5.74 |
| ATP_CHALL | -6.37 | -5.54 | -3.04 | -2.09 | -0.88 | 1.46 | 2.38 | 3.89 | 6.58 |
| WTA_CHALL | -9.42 | -7.93 | -1.97 | -2.22 | 0.35 | 0.56 | 2.27 | 5.25 | 8.32 |

For reference, the **full-corpus** values (reproducing Scope A T4 exactly): ATP_MAIN ranges
−10.56 → +10.81; WTA_MAIN −10.79 → +10.94; ATP_CHALL −10.69 → +10.41; WTA_CHALL −12.60 → +13.08.

## Section 3 — Per-cell delta (completed-only − full corpus); flagged where |Δ| > 1.0c

| Category | r05_14 | r15_24 | r25_34 | r35_44 | r45_54 | r55_64 | r65_74 | r75_84 | r85_94 |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| ATP_MAIN | **+5.51** | **+2.70** | **+1.87** | +0.80 | +0.22 | -0.58 | **-1.36** | **-3.06** | **-4.50** |
| WTA_MAIN | **+5.76** | **+3.03** | **+1.55** | +0.09 | +0.03 | -0.40 | -0.74 | **-2.87** | **-5.19** |
| ATP_CHALL | **+4.32** | **+2.81** | **+1.38** | +0.61 | +0.23 | -0.29 | -0.60 | **-2.34** | **-3.82** |
| WTA_CHALL | **+3.18** | **+4.04** | **+1.94** | +0.84 | +0.51 | -0.79 | **-1.01** | **-3.62** | **-4.76** |

22 of 36 cells exceed ±1.0c (bold). The distortion is **systematic and concentrated at the
extremes**: large positive deltas in the underdog bands (r05_14, r15_24) and large negative deltas
in the favorite bands (r75_84, r85_94), shrinking the gradient inward; the coin-flip band (r45_54)
is essentially unchanged (|Δ| ≤ 0.51c). Max |Δ| = 5.76c. (Smallest normal-only cells are WTA_CHALL
extremes — r05_14 n=36, r85_94 n=37 — so those magnitudes are indicative.)

## Section 4 — Observational summary

**The T4 gradient is NOT robust in magnitude to walkover/retirement removal.** Excluding
reversal-prone matches roughly **halves** the extreme-band drift — ATP_MAIN's r05_14/r85_94 goes
from −10.6c/+10.8c to −5.1c/+6.3c, and the same ~2× attenuation holds across all four categories.
The *shape* survives — drift is still monotonic in anchor regime, still crosses zero at the
coin-flip band — but roughly half of the headline ±11c magnitude at the extremes was contributed by
reversal-prone events. The pattern is mechanistically coherent: injury/withdrawal-bound matches
tend to show large premarket favorite-strengthening drift (the market pricing the developing
withdrawal) *and* then settle as a walkover/retirement, so they pile into exactly the extreme
anchor bands where the corpus gradient looked largest. The distortion is concentrated entirely in
the extreme bands (r05_14, r15_24, r75_84, r85_94); the mid-board is barely affected.

## Disclosure

This is a coarse **duration-based proxy** for walkover/retirement, not a definitive classifier.
Some `short_match` cases are genuinely quick straight-set wins, not retirements, so the proxy
over-counts reversals (conservative on the upside). The correct reading is therefore the
**corpus-level robustness conclusion** — the headline gradient's magnitude is materially
reversal-dependent at the extremes — not any per-event classification claim. A definitive analysis
would require settlement-reason / scoreline data rather than duration alone.
