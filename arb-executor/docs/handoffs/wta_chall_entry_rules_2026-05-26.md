# WTA_CHALL optimal entry rule per cell band — 2026-05-26

Read-only, local. Step-1 bands × discount {0,1,2,3,4,5,6,8,10,12,15}c × post_start {B1..B4} (rests to T-20m). Fill if band ticker min_bid in any bucket ≥ post_start ≤ post price; **fill price = our bid (anchor−discount)**; exit at fill+R via **raw_max** else settle. Unfilled → **skip** ($0) or **taker fallback** (cross at anchor at T-20m, exit R).

## ⚠️ Caveats (uplifts are upper bounds)
- **`raw_max` exit-hit** = unqualified peak, optimistic vs deployed `size_qual_max_250` (≥250-depth). Captures are an upper bound.
- **Per-band optima are IN-SAMPLE** (best of 44 combos on the same corpus) — overfit ceilings, not out-of-sample.
- **Idealized maker fill** (fills whenever observed min_bid touches our bid; no queue/partial).

## Headline (vs taker baseline)
- **Taker baseline** (enter all at anchor, Step-1 band R): **$222.10**.
- **Skip optimum:** **$419.30** — uplift **+197.20** (+88.8%).
- **Fallback optimum:** **$476.70** — uplift **+254.60** (+114.6%).

## SKIP scenario — per band optimum

| band | N | exit_R | disc | post_start | fill% | avg disc | skip $ | taker $ | uplift |
|---|---|---|---|---|---|---|---|---|---|
| 5-23 | 146 | 15 | 2c | B1 | 77% | 2.0c | 49.9 | 28.0 | +21.9 |
| 24-35 | 132 | 71 | 3c | B2 | 80% | 3.0c | 153.1 | 118.9 | +34.2 |
| 36-45 | 107 | 49 | 15c | B1 | 18% | 15.0c | 64.0 | 32.4 | +31.6 |
| 46-56 | 109 | 32 | 3c | B1 | 83% | 3.0c | 75.8 | 59.2 | +16.6 |
| 57-67 | 161 | 2 | 2c | B1 | 93% | 2.0c | 29.8 | -19.5 | +49.3 |
| 68-77 | 109 | 5 | 5c | B1 | 63% | 5.0c | 34.5 | 8.1 | +26.4 |
| 78-94 | 123 | 1 | 2c | B1 | 99% | 2.0c | 12.2 | -5.0 | +17.2 |
| **TOTAL** | | | | | | | **419.3** | **222.1** | **+197.2** |

## FALLBACK scenario — per band optimum

| band | N | exit_R | disc | post_start | fill% | fallback $ | taker $ | uplift | ROI tot cap |
|---|---|---|---|---|---|---|---|---|---|
| 5-23 | 146 | 15 | 4c | B1 | 45% | 54.5 | 28.0 | +26.5 | 31.214% |
| 24-35 | 132 | 71 | 8c | B1 | 39% | 166.5 | 118.9 | +47.6 | 47.1% |
| 36-45 | 107 | 49 | 12c | B1 | 27% | 55.6 | 32.4 | +23.2 | 13.949% |
| 46-56 | 109 | 32 | 10c | B1 | 35% | 115.7 | 59.2 | +56.5 | 22.195% |
| 57-67 | 161 | 2 | 2c | B1 | 93% | 25.3 | -19.5 | +44.8 | 2.596% |
| 68-77 | 109 | 5 | 5c | B1 | 63% | 46.8 | 8.1 | +38.7 | 6.183% |
| 78-94 | 123 | 1 | 1c | B1 | 99% | 12.3 | -5.0 | +17.3 | 1.174% |
| **TOTAL** | | | | | | **476.7** | **222.1** | **+254.6** | |

## Read of the optima
- **post_start (skip):** {'B1': 6, 'B2': 1} | **(fallback):** {'B1': 7} — vs the drift-timing late-dip skew (B4).
- **discount (skip):** {2: 3, 3: 2, 5: 1, 15: 1} | **(fallback):** {1: 1, 2: 1, 4: 1, 5: 1, 8: 1, 10: 1, 12: 1}.

*Read-only on drift_timing + spike_perN. Per-band-per-combo parquet staged. raw_max + in-sample optima — see caveats.*