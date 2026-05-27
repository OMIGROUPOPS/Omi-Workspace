# ATP_MAIN paired-N R analysis — joint both-cash optimization — 2026-05-27

Read-only, local. 1,907 paired events (both legs in corpus), joined by `event_ticker` (fav = higher anchor, dog = lower). raw_max hits, 10ct.

## ⚠️ Headline verdict: paired optimization gives NO real edge — DO NOT switch
Measured in-sample "uplift" is **+$909.60 (+91.7%)** joint EV (v6 $991.80 → paired-opt $1,901.40) across 35 band-pairs — **but this is an overfitting artifact, not realizable edge.** Two independent reasons:

1. **Joint EV is mathematically separable.** `E[fav_pnl(R_f) + dog_pnl(R_d)] = E[fav_pnl(R_f)] + E[dog_pnl(R_d)]` — expectation is linear, so the joint optimum is just the per-leg optimum on each leg's population. **No "paired interaction" exists for joint optimization to exploit that per-leg optimization cannot.** The legs are anti-correlated in *settlement* (one wins), which affects only the both-cash *hit rate*, not the EV being maximized.
2. **The apparent uplift = small-sample conditioning + free-parameter overfit.** Paired-opt re-fits R_fav and R_dog *within each (fav_band,dog_band) subset* — N median 45 (range 15–111) — sweeping ~2,116 combos and keeping the in-sample max, vs v6's R chosen on the **full band** with zone-aware robustness. Overfit evidence:
   - Paired-opt picks **more deep/lottery R (≥25c): 21 leg-picks vs v6's 16** — the fragile tails zone-aware was designed to reject (e.g. R_dog 39/41/43 on small underdog subsets riding a few spikes).
   - 34% of the uplift is in the smallest pairings (N<40); the rest still overfit ~2k free combos per subset.
   - A genuine +91.7% would mean v6 leaves half the EV on the table — implausible, since v6 R is already per-leg-optimal (zone-aware) on the full bands.

**Recommendation: keep v6 per-leg (zone-aware) R. Do not adopt paired-optimal R** — it won't generalize out-of-sample and re-introduces the lottery-tail fragility v6 removed.

## Genuine paired insight (diagnostic, not optimization)
- **Both-cash joint hit rate at paired-opt averages 44.2%** (range 0–89%). The legs' price paths are anti-correlated (favorite up ⇒ underdog down), so both legs cashing an up-R in the same match is rarer than independent rates imply. Useful for combined-position cash-flow understanding — but it creates **no** R-selection interaction (EV stays separable).
- `combined_anchor_cost` (fav+dog anchor) sits just under 100 — the structural maker edge; the dual-settle outcome nets `100 − combined_cost` per match regardless of R.

## Per band-pair (N≥15, sorted by in-sample Δ — illustrative of overfit, NOT a deploy table)

| fav band | dog band | N | v6 R_f | v6 R_d | opt R_f | opt R_d | joint-hit(opt) | v6 EV | opt EV | Δ in-sample |
|---|---|---|---|---|---|---|---|---|---|---|
| 65-66 | 36-37 | 59 | 33 | 3 | 1 | 39 | 63% | -27.3 | 70.2 | +97.5 |
| 52-54 | 49-51 | 61 | 11 | 3 | 2 | HOLD | — | 4.9 | 83.7 | +78.8 |
| 72-74 | 26-28 | 66 | 3 | 3 | 4 | 41 | 47% | -1.5 | 54.8 | +56.3 |
| 75-76 | 26-28 | 45 | 8 | 3 | 1 | HOLD | — | -1.0 | 54.6 | +55.6 |
| 55-56 | 47-48 | 34 | 33 | 11 | 45 | 1 | 0% | 29.4 | 80.0 | +50.6 |
| 52-54 | 47-48 | 47 | 11 | 11 | HOLD | 11 | — | 35.2 | 81.4 | +46.2 |
| 57-58 | 43-44 | 47 | 18 | 3 | 4 | 43 | 60% | 15.5 | 61.4 | +45.9 |
| 69-71 | 31-32 | 64 | 17 | 12 | 29 | 14 | 39% | 46.4 | 88.4 | +42.0 |
| 59-61 | 41-42 | 83 | 24 | 26 | 38 | 31 | 33% | 54.3 | 94.9 | +40.6 |
| 90-94 | 10-16 | 53 | 2 | 6 | 10 | 18 | 0% | 26.3 | 60.8 | +34.5 |
| 69-71 | 29-30 | 27 | 17 | 26 | 1 | 41 | 59% | 1.8 | 35.8 | +34.0 |
| 55-56 | 45-46 | 63 | 33 | 39 | 6 | 41 | 56% | 29.1 | 61.0 | +31.9 |
| 67-68 | 36-37 | 15 | 2 | 3 | 9 | 44 | 60% | 0.6 | 32.2 | +31.6 |
| 59-61 | 43-44 | 39 | 24 | 3 | 30 | 1 | 79% | 23.4 | 53.6 | +30.2 |
| 77-79 | 26-28 | 19 | 14 | 3 | 6 | HOLD | — | 2.0 | 31.4 | +29.4 |
| 62-64 | 38-40 | 111 | 8 | 1 | 36 | 1 | 48% | 24.1 | 53.1 | +29.0 |
| 65-66 | 33-35 | 30 | 33 | 24 | 35 | 1 | 0% | 13.8 | 35.9 | +22.1 |
| 72-74 | 29-30 | 62 | 3 | 26 | 24 | 31 | 31% | 13.7 | 34.5 | +20.8 |
| 62-64 | 41-42 | 22 | 8 | 26 | 12 | HOLD | — | 20.1 | 40.5 | +20.4 |
| 80-82 | 17-19 | 26 | 1 | 54 | 5 | HOLD | — | 39.5 | 59.7 | +20.2 |
| 67-68 | 33-35 | 75 | 2 | 24 | 3 | 41 | 55% | 59.2 | 75.6 | +16.4 |
| 59-61 | 38-40 | 38 | 24 | 1 | 41 | 8 | 0% | 35.7 | 51.3 | +15.6 |
| 83-85 | 10-16 | 30 | 15 | 6 | 7 | 10 | 80% | 24.4 | 35.6 | +11.2 |
| 75-76 | 23-25 | 30 | 8 | 22 | 8 | 16 | 77% | 34.0 | 43.6 | +9.6 |
| 49-51 | 49-51 | 19 | 3 | 3 | 8 | 6 | 89% | 6.1 | 15.1 | +9.0 |
| 65-66 | 38-40 | 26 | 33 | 1 | 35 | 19 | 0% | 51.0 | 58.6 | +7.6 |
| 77-79 | 23-25 | 72 | 14 | 22 | 14 | 12 | 69% | 61.5 | 69.0 | +7.5 |
| 77-79 | 20-22 | 24 | 14 | 52 | 10 | 45 | 42% | 30.1 | 37.3 | +7.2 |
| 83-85 | 17-19 | 61 | 15 | 54 | 15 | 16 | 52% | 57.5 | 62.7 | +5.2 |
| 62-64 | 36-37 | 33 | 8 | 3 | 37 | 3 | 0% | 14.7 | 19.7 | +5.0 |
| 57-58 | 45-46 | 43 | 18 | 39 | 11 | 39 | 51% | 44.1 | 49.0 | +4.9 |
| 69-71 | 33-35 | 30 | 17 | 24 | 18 | 24 | 60% | 51.0 | 53.9 | +2.9 |
| 86-89 | 10-16 | 89 | 11 | 6 | 11 | 6 | 57% | 63.2 | 63.2 | +0.0 |
| 80-82 | 20-22 | 63 | 1 | 52 | 1 | HOLD | — | 50.0 | 45.3 | -4.7 |
| 90-94 | 5-9 | 54 | 2 | 63 | 1 | 45 | 31% | 59.0 | 53.6 | -5.4 |

*Read-only, local. The Δ column is in-sample (overfit) and is NOT deployable gain — see headline. v6 zone-aware per-leg R stands; paired optimization adds no structural edge (EV is separable).*