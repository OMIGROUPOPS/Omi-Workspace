# ATP_MAIN paired-N — max joint hit rate under price-aware ROI floor — 2026-05-27

Read-only, local. 1,907 paired ATP_MAIN events. **Objective per (fav_band,dog_band): R_fav/anchor_fav ≥ X AND R_dog/anchor_dog ≥ X (price-aware ROI floor); maximize joint hit rate P(both reach anchor+R); tie-break max(R_fav+R_dog).** Floor uses each band's mean leg anchor (e.g. X=0.20 → 90c entry needs R≥18, 10c needs R≥2). Per `docs/rung1_strategy_evaluation_spec.md` A39: ROI floors, not absolute-cent floors, are the comparable framing across cells.

## Sensitivity to ROI floor X

| X (ROI floor) | mean joint-hit | mean (R_f+R_d) | both-cash $ @10ct (new) | v6 baseline | infeasible pairs* |
|---|---|---|---|---|---|
| 0.20 | 56.7% | 24.4 | $2,185 | $2,551 | 5 |
| 0.30 | 39.1% | 34.3 | $2,208 | $2,551 | 10 |
| 0.40 | 24.8% | 44.4 | $1,814 | $2,551 | 14 |

\*infeasible = band-pair where the floor forces a target the leg can't reach (joint-hit 0).

## ⚠️ Structural limit: ROI floors are infeasible for high favorites
A favorite entered at anchor `a` can appreciate at most to 100, so its **maximum possible price-ROI = (100−a)/a**. For a=83c that's 20%; **above ~83c a 20% ROI floor is impossible** (e.g. 90c → max 11%; the floor demands R≥18 → target 108 > 100). Those favorite legs can only earn their return via **settlement (win→100), not price capture** — the ROI-on-price floor doesn't apply to them, and they show joint-hit 0 here. ROI floors are the right framing for mid/underdog cells but break down as the favorite approaches 100.

## Per band-pair at X=0.20 (primary)

| fav band | dog band | N | floor (R_f,R_d) | v6 (R_f,R_d) | v6 joint-hit | new (R_f,R_d) | new joint-hit | new cap/game | new $/game | v6 $/game |
|---|---|---|---|---|---|---|---|---|---|---|
| 62-64 | 38-40 | 111 | (13,8) | (8,1) | 89% | (13,8) | 59% | 12.49c | 1.249 | 0.803 |
| 86-89 | 10-16 | 89 | (18,3) | (11,6) | 57% | (18,3) | 0% | 0.00c | 0.000 | 0.974 |
| 59-61 | 41-42 | 83 | (13,9) | (24,26) | 42% | (14,9) | 66% | 15.24c | 1.524 | 2.108 |
| 67-68 | 33-35 | 75 | (14,7) | (2,24) | 69% | (14,7) | 56% | 11.76c | 1.176 | 1.803 |
| 77-79 | 23-25 | 72 | (16,5) | (14,22) | 50% | (16,5) | 74% | 15.46c | 1.546 | 1.800 |
| 72-74 | 26-28 | 66 | (15,6) | (3,3) | 86% | (18,6) | 64% | 15.27c | 1.527 | 0.518 |
| 69-71 | 31-32 | 64 | (15,7) | (17,12) | 64% | (17,7) | 67% | 16.12c | 1.613 | 1.858 |
| 55-56 | 45-46 | 63 | (12,10) | (33,39) | 22% | (13,13) | 67% | 17.33c | 1.733 | 1.600 |
| 80-82 | 20-22 | 63 | (17,5) | (1,52) | 38% | (17,6) | 63% | 14.60c | 1.460 | 2.019 |
| 72-74 | 29-30 | 62 | (15,6) | (3,26) | 50% | (15,8) | 61% | 14.10c | 1.410 | 1.450 |
| 52-54 | 49-51 | 61 | (11,10) | (11,3) | 79% | (11,11) | 74% | 16.23c | 1.623 | 1.102 |
| 83-85 | 17-19 | 61 | (17,4) | (15,54) | 21% | (17,4) | 0% | 0.00c | 0.000 | 1.470 |
| 65-66 | 36-37 | 59 | (14,8) | (33,3) | 58% | (14,9) | 64% | 14.81c | 1.481 | 2.075 |
| 90-94 | 5-9 | 54 | (19,2) | (2,63) | 24% | (19,2) | 0% | 0.00c | 0.000 | 1.565 |
| 90-94 | 10-16 | 53 | (19,3) | (2,6) | 81% | (19,3) | 0% | 0.00c | 0.000 | 0.649 |
| 52-54 | 47-48 | 47 | (11,10) | (11,11) | 77% | (12,11) | 77% | 17.62c | 1.762 | 1.685 |
| 57-58 | 43-44 | 47 | (12,9) | (18,3) | 77% | (13,10) | 70% | 16.15c | 1.615 | 1.609 |
| 75-76 | 26-28 | 45 | (16,6) | (8,3) | 82% | (16,6) | 62% | 13.69c | 1.369 | 0.904 |
| 57-58 | 45-46 | 43 | (12,10) | (18,39) | 42% | (12,10) | 67% | 14.84c | 1.484 | 2.386 |
| 59-61 | 43-44 | 39 | (12,9) | (24,3) | 69% | (30,11) | 56% | 23.13c | 2.313 | 1.869 |
| 59-61 | 38-40 | 38 | (13,8) | (24,1) | 82% | (23,8) | 74% | 22.84c | 2.284 | 2.039 |
| 55-56 | 47-48 | 34 | (12,10) | (33,11) | 50% | (21,13) | 62% | 21.00c | 2.100 | 2.200 |
| 62-64 | 36-37 | 33 | (13,8) | (8,3) | 91% | (13,8) | 67% | 14.00c | 1.400 | 1.000 |
| 65-66 | 33-35 | 30 | (14,7) | (33,24) | 27% | (16,7) | 67% | 15.33c | 1.533 | 1.520 |
| 69-71 | 33-35 | 30 | (14,7) | (17,24) | 60% | (18,7) | 80% | 20.00c | 2.000 | 2.460 |
| 75-76 | 23-25 | 30 | (16,5) | (8,22) | 60% | (23,6) | 77% | 22.23c | 2.223 | 1.800 |
| 83-85 | 10-16 | 30 | (17,4) | (15,6) | 23% | (17,4) | 0% | 0.00c | 0.000 | 0.490 |
| 69-71 | 29-30 | 27 | (15,6) | (17,26) | 41% | (15,9) | 63% | 15.11c | 1.511 | 1.752 |
| 65-66 | 38-40 | 26 | (14,8) | (33,1) | 81% | (33,9) | 62% | 25.85c | 2.585 | 2.746 |
| 80-82 | 17-19 | 26 | (17,4) | (1,54) | 46% | (17,5) | 50% | 11.00c | 1.100 | 2.538 |
| 77-79 | 20-22 | 24 | (16,5) | (14,52) | 29% | (19,7) | 62% | 16.25c | 1.625 | 1.925 |
| 62-64 | 41-42 | 22 | (13,9) | (8,26) | 64% | (13,9) | 68% | 15.00c | 1.500 | 2.164 |
| 49-51 | 49-51 | 19 | (11,11) | (3,3) | 95% | (11,12) | 58% | 13.32c | 1.332 | 0.568 |
| 77-79 | 26-28 | 19 | (16,6) | (14,3) | 79% | (17,6) | 74% | 16.95c | 1.695 | 1.342 |
| 67-68 | 36-37 | 15 | (14,8) | (2,3) | 93% | (14,8) | 73% | 16.13c | 1.613 | 0.467 |
| **TOTAL** | | | | | | | | | **$2,185** | **$2,551** |

## Reading it
- **The ROI floor is the balanced lever the prior two objectives lacked.** At X=0.20 the both-cash capture ($2,185) recovers ~86% of v6's ($2,551) while lifting price-ROI per cashing leg to ≥20% — vs the flat-R≥2 objective which hit 93% joint-fire but only ~⅓ the capture, and the deep E[A+B]/P(both)×sum objectives which over-deepened.
- **Both-cash capture is flat-to-slightly-higher from X=0.20→0.30 ($2,185→$2,208) then falls at 0.40 ($1,814)** — the sweet spot is ~0.20–0.30; beyond that the deeper floor kills too much joint-fire.
- **Joint hit rate falls monotonically with X** (56.7%→39.1%→24.8%) as the floor deepens — the reliability/ROI tradeoff is explicit.
- High-favorite pairings drop out (joint-hit 0) as X rises — the infeasibility above.

**Metric caveat:** $ counts both-cash capture only (excludes single-leg + ride-to-settle). v6 remains deployed; this quantifies the ROI-floor design space, no change made.

*Read-only, local, in-sample.*