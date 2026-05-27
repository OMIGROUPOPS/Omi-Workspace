# ATP_MAIN paired-N — maximize JOINT HIT RATE (reliable double-cash) — 2026-05-27

Read-only, local. 1,907 paired ATP_MAIN events, joined by `event_ticker` (fav=higher anchor). raw_max. **Objective per (fav_band,dog_band): sweep R_fav,R_dog ∈ [2,99]; maximize P(both legs reach anchor+R within match); tie-break max (R_fav+R_dog).**

## Result — intent achieved (shallow R, high joint-fire), but at a large capture cost
- **Joint hit rate: 59.9% (v6) → 92.7% (new)** — far more games double-cash.
- **Mean (R_fav+R_dog): 32.7 (v6) → 5.8 (new)** — much shallower (picks cluster at R=2–3 per leg).
- **But both-cash capture $ @10ct: v6 $2,551 → new $805 (Δ -1,746).** Tiny captures × high rate ≪ deep captures × moderate rate.

**The tradeoff is the headline:** maximizing joint hit rate makes double-cash reliable (~93%) but each cash is only ~2–3c, so total both-cash capture collapses to ~⅓ of v6's. "Reliable" and "profitable" pull in opposite directions here; this objective sits at the reliable-but-thin extreme, the prior E[A+B]/deep objective at the profitable-but-rare extreme.

**⚠️ Metric scope:** the $ column counts **both-cash capture only** — it ignores single-leg captures *and* ride-to-settle value, both of which v6's deeper R also earns. So neither this nor the joint-hit number is full strategy EV; this is the specific "both legs fire" lens requested.

## Per band-pair

| fav band | dog band | N | v6 (R_f,R_d) | v6 joint-hit | new (R_f,R_d) | new joint-hit | new capture/game | new $/game @10ct | v6 $/game @10ct |
|---|---|---|---|---|---|---|---|---|---|
| 62-64 | 38-40 | 111 | (8,1) | 89% | (2,2) | 90% | 3.60c | 0.360 | 0.803 |
| 86-89 | 10-16 | 89 | (11,6) | 57% | (2,2) | 93% | 3.73c | 0.373 | 0.974 |
| 59-61 | 41-42 | 83 | (24,26) | 42% | (2,2) | 95% | 3.81c | 0.381 | 2.108 |
| 67-68 | 33-35 | 75 | (2,24) | 69% | (2,2) | 88% | 3.52c | 0.352 | 1.803 |
| 77-79 | 23-25 | 72 | (14,22) | 50% | (3,2) | 96% | 4.79c | 0.479 | 1.800 |
| 72-74 | 26-28 | 66 | (3,3) | 86% | (2,2) | 92% | 3.70c | 0.370 | 0.518 |
| 69-71 | 31-32 | 64 | (17,12) | 64% | (3,2) | 98% | 4.92c | 0.492 | 1.858 |
| 55-56 | 45-46 | 63 | (33,39) | 22% | (2,2) | 100% | 4.00c | 0.400 | 1.600 |
| 80-82 | 20-22 | 63 | (1,52) | 38% | (2,2) | 89% | 3.56c | 0.356 | 2.019 |
| 72-74 | 29-30 | 62 | (3,26) | 50% | (2,2) | 87% | 3.48c | 0.348 | 1.450 |
| 52-54 | 49-51 | 61 | (11,3) | 79% | (2,2) | 97% | 3.87c | 0.387 | 1.102 |
| 83-85 | 17-19 | 61 | (15,54) | 21% | (2,3) | 92% | 4.59c | 0.459 | 1.470 |
| 65-66 | 36-37 | 59 | (33,3) | 58% | (3,3) | 93% | 5.59c | 0.559 | 2.075 |
| 90-94 | 5-9 | 54 | (2,63) | 24% | (2,2) | 93% | 3.70c | 0.370 | 1.565 |
| 90-94 | 10-16 | 53 | (2,6) | 81% | (2,2) | 91% | 3.62c | 0.362 | 0.649 |
| 52-54 | 47-48 | 47 | (11,11) | 77% | (2,2) | 98% | 3.91c | 0.391 | 1.685 |
| 57-58 | 43-44 | 47 | (18,3) | 77% | (4,3) | 96% | 6.70c | 0.670 | 1.609 |
| 75-76 | 26-28 | 45 | (8,3) | 82% | (2,4) | 89% | 5.33c | 0.533 | 0.904 |
| 57-58 | 45-46 | 43 | (18,39) | 42% | (2,8) | 88% | 8.84c | 0.884 | 2.386 |
| 59-61 | 43-44 | 39 | (24,3) | 69% | (3,2) | 92% | 4.62c | 0.462 | 1.869 |
| 59-61 | 38-40 | 38 | (24,1) | 82% | (4,3) | 92% | 6.45c | 0.645 | 2.039 |
| 55-56 | 47-48 | 34 | (33,11) | 50% | (2,2) | 94% | 3.76c | 0.376 | 2.200 |
| 62-64 | 36-37 | 33 | (8,3) | 91% | (3,3) | 97% | 5.82c | 0.582 | 1.000 |
| 65-66 | 33-35 | 30 | (33,24) | 27% | (6,2) | 97% | 7.73c | 0.773 | 1.520 |
| 69-71 | 33-35 | 30 | (17,24) | 60% | (2,2) | 90% | 3.60c | 0.360 | 2.460 |
| 75-76 | 23-25 | 30 | (8,22) | 60% | (8,2) | 97% | 9.67c | 0.967 | 1.800 |
| 83-85 | 10-16 | 30 | (15,6) | 23% | (7,2) | 93% | 8.40c | 0.840 | 0.490 |
| 69-71 | 29-30 | 27 | (17,26) | 41% | (2,4) | 96% | 5.78c | 0.578 | 1.752 |
| 65-66 | 38-40 | 26 | (33,1) | 81% | (2,2) | 81% | 3.23c | 0.323 | 2.746 |
| 80-82 | 17-19 | 26 | (1,54) | 46% | (5,5) | 85% | 8.46c | 0.846 | 2.538 |
| 77-79 | 20-22 | 24 | (14,52) | 29% | (4,2) | 100% | 6.00c | 0.600 | 1.925 |
| 62-64 | 41-42 | 22 | (8,26) | 64% | (2,3) | 82% | 4.09c | 0.409 | 2.164 |
| 49-51 | 49-51 | 19 | (3,3) | 95% | (3,6) | 95% | 8.53c | 0.853 | 0.568 |
| 77-79 | 26-28 | 19 | (14,3) | 79% | (6,3) | 95% | 8.53c | 0.853 | 1.342 |
| 67-68 | 36-37 | 15 | (2,3) | 93% | (2,8) | 93% | 9.33c | 0.933 | 0.467 |
| **TOTAL** | | | | 59.9% avg | | 92.7% avg | | **$805** | **$2,551** |

## Reading it
- New R picks are almost all **(2,2) or (3,2)** — the shallowest allowed — confirming the objective drives to the floor (joint hit is monotone in R, so the max is at the shallowest R; the tie-break only pushes deeper where doing so drops no double-cash game).
- Joint-fire reliability jumps to ~93%, but the per-game both-cash capture falls from ~19.6c (v6) to ~5.4c (new).
- **If the goal is to actually make money, neither pure extreme wins** — v6's per-leg zone-aware R (chosen on full EV incl. single-leg + settle) remains the deployed, balanced choice. This analysis quantifies what pure joint-hit maximization costs (~$1.7k of both-cash capture) to buy reliability.

*Read-only, local, in-sample. Both-cash-capture metric only (excludes single-leg + settle). v6 remains deployed; no change made.*