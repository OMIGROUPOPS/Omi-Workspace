# WTA_MAIN zone-aware risk-adjusted exit R — 2026-05-27

Read-only, local. Same DP band boundaries as `wta_main_cell_bands_2026-05-26.md`; R re-selected per zone. **raw_max** exit, 10ct (caveat: raw_max optimistic vs deployed size_qual; in-sample).

**Zone rule (by avg cell price in band):** underdog `<26` → keep max-EV · mid `26–74` → R≥3 ∧ hit≥60% ∧ total≥75%·maxEV, pick **highest hit** (relax 75% if none; else max-EV) · favorite `≥75` → keep max-EV. DISABLE (maxEV total ≤0) stays DISABLE.

## Headline
- **Total $ max-EV: $1,507.50** → **zone-aware: $1,227.40** — retention **81.4%**.
- Bands where R changed (zone-aware ≠ max-EV): **12** / 28.
- zones: underdog:5, mid:18, favorite:5 | DISABLE:3

| band | N | wr% | maxEV R | maxEV hit% | maxEV $ | ZA R | ZA hit% | ZA $ | zone | action |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-9 | 113 | 8.0 | 25 | 39.8 | 63.9 | R25 | 39.8 | 63.9 | underdog | R25 |
| 10-14 | 142 | 14.8 | 46 | 28.9 | 65.4 | R46 | 28.9 | 65.4 | underdog | R46 |
| 15-18 | 113 | 19.5 | 79 | 23.9 | 73.8 | R79 | 23.9 | 73.8 | underdog | R79 |
| 19-21 | 118 | 17.8 | 33 | 54.2 | 102.8 | R33 | 54.2 | 102.8 | underdog | R33 |
| 22-24 | 127 | 19.7 | 45 | 40.9 | 60.9 | R45 | 40.9 | 60.9 | underdog | R45 |
| 25-27 | 122 | 32.0 | 31 | 58.2 | 87.4 | R23 | 64.8 | 69.6 | mid | R23 |
| 28-30 | 116 | 36.2 | 39 | 56.9 | 112.2 | R23 | 69.8 | 84.7 | mid | R23 |
| 31-32 | 108 | 34.3 | 34 | 58.3 | 72.6 | R14 | 80.6 | 55.6 | mid | R14 |
| 33-35 | 113 | 44.2 | HOLD | — | 115.6 | R30 | 65.5 | 89.8 | mid | R30 |
| 36-38 | 151 | 29.1 | 7 | 86.8 | 27.6 | R7 | 86.8 | 27.6 | mid | R7 |
| 39-41 | 147 | 36.1 | 35 | 58.5 | 57.1 | R31 | 60.5 | 43.9 | mid | R31 |
| 42-44 | 141 | 45.4 | 56 | 33.3 | 57.2 | R4 | 92.2 | 5.0 | mid | R4 (relaxed) |
| 45-47 | 145 | 46.2 | 44 | 55.2 | 53.0 | R3 | 91.7 | -15.2 | mid | R3 (relaxed) |
| 48-49 | 109 | 54.1 | 45 | 63.3 | 116.7 | R24 | 78.0 | 87.9 | mid | R24 |
| 50-52 | 147 | 49.0 | 6 | 93.2 | 31.5 | R6 | 93.2 | 31.5 | mid | R6 |
| 53-54 | 101 | 39.6 | 11 | 81.2 | -11.4 | DISABLE | — | -11.4 | mid | DISABLE |
| 55-57 | 152 | 50.0 | 10 | 87.5 | 26.3 | R7 | 91.4 | 24.2 | mid | R7 |
| 58-59 | 111 | 54.1 | 8 | 90.1 | 15.6 | R8 | 90.1 | 15.6 | mid | R8 |
| 60-61 | 107 | 66.4 | HOLD | — | 63.4 | R31 | 72.0 | 57.4 | mid | R31 |
| 62-65 | 229 | 69.0 | 36 | 30.6 | 143.2 | R33 | 70.3 | 109.4 | mid | R33 |
| 66-69 | 191 | 60.7 | 20 | 78.0 | 13.6 | R20 | 78.0 | 13.6 | mid | R20 |
| 70-71 | 101 | 72.3 | 22 | 82.2 | 55.6 | R22 | 82.2 | 55.6 | mid | R22 |
| 72-75 | 177 | 65.0 | 1 | 98.9 | 2.9 | R3 | 93.8 | -31.2 | mid | R3 (relaxed) |
| 76-78 | 128 | 78.1 | 10 | 93.0 | 49.5 | R10 | 93.0 | 49.5 | favorite | R10 |
| 79-82 | 136 | 79.4 | 11 | 90.4 | 31.0 | R11 | 90.4 | 31.0 | favorite | R11 |
| 83-85 | 105 | 81.0 | 9 | 89.5 | -7.6 | DISABLE | — | -7.6 | favorite | DISABLE |
| 86-89 | 120 | 82.5 | 3 | 97.5 | 8.7 | R3 | 97.5 | 8.7 | favorite | R3 |
| 90-94 | 113 | 88.5 | 5 | 93.8 | -11.2 | DISABLE | — | -11.2 | favorite | DISABLE |

*Read-only. Zone-aware R is the input for the v6 parquet build (replaces max-EV picks). raw_max + in-sample caveat.*