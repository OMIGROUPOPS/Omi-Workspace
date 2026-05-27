# ATP_MAIN zone-aware risk-adjusted exit R — 2026-05-27

Read-only, local. Same DP band boundaries as `atp_main_cell_bands_2026-05-26.md`; R re-selected per zone. **raw_max** exit, 10ct (caveat: raw_max optimistic vs deployed size_qual; in-sample).

**Zone rule (by avg cell price in band):** underdog `<26` → keep max-EV · mid `26–74` → R≥3 ∧ hit≥60% ∧ total≥75%·maxEV, pick **highest hit** (relax 75% if none; else max-EV) · favorite `≥75` → keep max-EV. DISABLE (maxEV total ≤0) stays DISABLE.

## Headline
- **Total $ max-EV: $1,626.80** → **zone-aware: $1,235.40** — retention **75.9%**.
- Bands where R changed (zone-aware ≠ max-EV): **14** / 31.
- zones: underdog:5, mid:20, favorite:6 | DISABLE:3

| band | N | wr% | maxEV R | maxEV hit% | maxEV $ | ZA R | ZA hit% | ZA $ | zone | action |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-9 | 113 | 11.5 | 63 | 21.2 | 90.5 | R63 | 21.2 | 90.5 | underdog | R63 |
| 10-16 | 193 | 6.7 | 6 | 80.3 | 44.8 | R6 | 80.3 | 44.8 | underdog | R6 |
| 17-19 | 107 | 24.3 | 54 | 37.4 | 96.1 | R54 | 37.4 | 96.1 | underdog | R54 |
| 20-22 | 106 | 24.5 | 52 | 40.6 | 91.3 | R52 | 40.6 | 91.3 | underdog | R52 |
| 23-25 | 120 | 20.0 | 22 | 63.3 | 60.9 | R22 | 63.3 | 60.9 | underdog | R22 |
| 26-28 | 138 | 34.8 | 71 | 36.2 | 117.8 | R3 | 92.8 | 11.5 | mid | R3 (relaxed) |
| 29-30 | 111 | 29.7 | 31 | 56.8 | 63.6 | R26 | 60.4 | 54.3 | mid | R26 |
| 31-32 | 100 | 24.0 | 14 | 75.0 | 26.3 | R12 | 77.0 | 19.9 | mid | R12 |
| 33-35 | 163 | 30.1 | 29 | 60.7 | 68.9 | R24 | 64.4 | 54.2 | mid | R24 |
| 36-37 | 117 | 36.8 | 39 | 57.3 | 79.0 | R3 | 99.1 | 31.2 | mid | R3 (relaxed) |
| 38-40 | 192 | 29.7 | 1 | 96.9 | -4.7 | DISABLE | — | -4.7 | mid | DISABLE |
| 41-42 | 126 | 40.5 | 32 | 64.3 | 72.2 | R26 | 68.3 | 57.4 | mid | R26 |
| 43-44 | 107 | 43.0 | 54 | 48.6 | 41.3 | R3 | 94.4 | 4.2 | mid | R3 (relaxed) |
| 45-46 | 126 | 50.8 | 48 | 58.7 | 118.6 | R39 | 63.5 | 102.6 | mid | R39 |
| 47-48 | 110 | 34.5 | 11 | 82.7 | 9.9 | R11 | 82.7 | 9.9 | mid | R11 |
| 49-51 | 129 | 55.0 | 50 | 17.8 | 93.3 | R3 | 97.7 | 22.8 | mid | R3 (relaxed) |
| 52-54 | 146 | 50.0 | 11 | 84.9 | 19.9 | R11 | 84.9 | 19.9 | mid | R11 |
| 55-56 | 126 | 61.1 | HOLD | — | 69.2 | R33 | 67.5 | 52.5 | mid | R33 |
| 57-58 | 126 | 54.0 | 18 | 77.0 | 8.0 | R18 | 77.0 | 8.0 | mid | R18 |
| 59-61 | 191 | 64.9 | 35 | 69.6 | 117.2 | R24 | 77.0 | 88.4 | mid | R24 |
| 62-64 | 210 | 62.4 | 12 | 88.6 | 71.8 | R8 | 92.9 | 61.1 | mid | R8 |
| 65-66 | 136 | 66.2 | 33 | 67.6 | 16.2 | R33 | 67.6 | 16.2 | mid | R33 |
| 67-68 | 123 | 61.8 | 2 | 96.7 | -3.2 | DISABLE | — | -3.2 | mid | DISABLE |
| 69-71 | 152 | 73.7 | HOLD | — | 55.2 | R17 | 84.2 | 49.1 | mid | R17 |
| 72-74 | 168 | 69.6 | 2 | 98.8 | 18.6 | R3 | 97.0 | 12.4 | mid | R3 (relaxed) |
| 75-76 | 104 | 73.1 | 8 | 94.2 | 33.1 | R8 | 94.2 | 33.1 | favorite | R8 |
| 77-79 | 134 | 76.9 | 14 | 88.1 | 40.9 | R14 | 88.1 | 40.9 | favorite | R14 |
| 80-82 | 120 | 70.8 | 1 | 98.3 | -4.6 | DISABLE | — | -4.6 | favorite | DISABLE |
| 83-85 | 117 | 86.3 | 15 | 64.1 | 56.9 | R15 | 64.1 | 56.9 | favorite | R15 |
| 86-89 | 109 | 88.1 | 11 | 71.6 | 31.4 | R11 | 71.6 | 31.4 | favorite | R11 |
| 90-94 | 117 | 90.6 | 2 | 99.1 | 13.9 | R2 | 99.1 | 13.9 | favorite | R2 |

*Read-only. Zone-aware R is the input for the v6 parquet build (replaces max-EV picks). raw_max + in-sample caveat.*