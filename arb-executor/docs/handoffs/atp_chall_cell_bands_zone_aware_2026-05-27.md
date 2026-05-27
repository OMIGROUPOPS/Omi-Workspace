# ATP_CHALL zone-aware risk-adjusted exit R — 2026-05-27

Read-only, local. Same DP band boundaries as `atp_chall_cell_bands_2026-05-26.md`; R re-selected per zone. **raw_max** exit, 10ct (caveat: raw_max optimistic vs deployed size_qual; in-sample).

**Zone rule (by avg cell price in band):** underdog `<26` → keep max-EV · mid `26–74` → R≥3 ∧ hit≥60% ∧ total≥75%·maxEV, pick **highest hit** (relax 75% if none; else max-EV) · favorite `≥75` → keep max-EV. DISABLE (maxEV total ≤0) stays DISABLE.

## Headline
- **Total $ max-EV: $2,200.20** → **zone-aware: $1,805.50** — retention **82.1%**.
- Bands where R changed (zone-aware ≠ max-EV): **19** / 33.
- zones: underdog:7, mid:22, favorite:4 | DISABLE:2

| band | N | wr% | maxEV R | maxEV hit% | maxEV $ | ZA R | ZA hit% | ZA $ | zone | action |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-8 | 160 | 5.0 | 9 | 66.2 | 59.0 | R9 | 66.2 | 59.0 | underdog | R9 |
| 9-12 | 161 | 14.3 | 64 | 23.6 | 113.4 | R64 | 23.6 | 113.4 | underdog | R64 |
| 13-14 | 105 | 16.2 | 49 | 38.1 | 108.7 | R49 | 38.1 | 108.7 | underdog | R49 |
| 15-17 | 144 | 20.8 | 43 | 44.4 | 147.5 | R43 | 44.4 | 147.5 | underdog | R43 |
| 18-19 | 107 | 24.3 | 57 | 35.5 | 89.1 | R57 | 35.5 | 89.1 | underdog | R57 |
| 20-22 | 139 | 16.5 | 22 | 65.5 | 99.0 | R22 | 65.5 | 99.0 | underdog | R22 |
| 23-25 | 163 | 20.2 | 47 | 39.3 | 63.1 | R47 | 39.3 | 63.1 | underdog | R47 |
| 26-27 | 101 | 26.7 | 61 | 36.6 | 56.4 | R3 | 94.1 | 12.6 | mid | R3 (relaxed) |
| 28-29 | 103 | 23.3 | 30 | 54.4 | 34.5 | R13 | 75.7 | 30.3 | mid | R13 |
| 30-31 | 149 | 26.8 | 15 | 76.5 | 64.0 | R13 | 77.9 | 50.0 | mid | R13 |
| 32-33 | 147 | 25.2 | 6 | 85.0 | 3.6 | R6 | 85.0 | 3.6 | mid | R6 |
| 34-35 | 144 | 32.6 | 52 | 45.1 | 64.5 | R22 | 67.4 | 50.8 | mid | R22 |
| 36-37 | 123 | 36.6 | 44 | 50.4 | 50.0 | R3 | 91.1 | -6.7 | mid | R3 (relaxed) |
| 38-39 | 151 | 33.1 | 10 | 84.8 | 39.5 | R8 | 87.4 | 32.5 | mid | R8 |
| 40-41 | 147 | 44.9 | 37 | 60.5 | 94.5 | R31 | 63.9 | 76.7 | mid | R31 |
| 42-44 | 179 | 47.5 | 53 | 50.8 | 104.0 | R4 | 92.7 | 10.1 | mid | R4 (relaxed) |
| 45-46 | 134 | 50.7 | 27 | 71.6 | 86.4 | R19 | 78.4 | 67.7 | mid | R19 |
| 47-48 | 134 | 53.7 | 24 | 77.6 | 107.0 | R19 | 80.6 | 81.5 | mid | R19 |
| 49-50 | 112 | 48.2 | 19 | 75.9 | 27.9 | R18 | 76.8 | 26.2 | mid | R18 |
| 51-52 | 105 | 47.6 | 24 | 76.2 | 63.3 | R22 | 77.1 | 54.6 | mid | R22 |
| 53-55 | 197 | 48.7 | 7 | 90.9 | 28.3 | R7 | 90.9 | 28.3 | mid | R7 |
| 56-57 | 146 | 49.3 | 13 | 86.3 | 50.8 | R11 | 88.4 | 45.9 | mid | R11 |
| 58-59 | 148 | 51.4 | 16 | 85.8 | 80.2 | R11 | 90.5 | 65.3 | mid | R11 |
| 60-61 | 159 | 55.3 | 1 | 98.7 | 3.6 | R3 | 94.3 | -9.6 | mid | R3 (relaxed) |
| 62-63 | 172 | 62.8 | 10 | 93.0 | 85.0 | R8 | 94.2 | 67.0 | mid | R8 |
| 64-65 | 157 | 58.0 | 4 | 94.9 | 7.9 | R4 | 94.9 | 7.9 | mid | R4 |
| 66-67 | 173 | 69.4 | 17 | 86.7 | 101.7 | R13 | 90.2 | 89.5 | mid | R13 |
| 68-71 | 310 | 72.9 | 27 | 76.8 | 153.8 | R25 | 77.1 | 115.6 | mid | R25 |
| 72-73 | 140 | 72.9 | 13 | 87.9 | 37.2 | R12 | 88.6 | 33.3 | mid | R12 |
| 74-78 | 301 | 81.7 | HOLD | — | 171.8 | HOLD | — | 171.8 | favorite | HOLD |
| 79-80 | 100 | 75.0 | 3 | 96.0 | -3.1 | DISABLE | — | -3.1 | favorite | DISABLE |
| 81-83 | 148 | 73.6 | 2 | 98.0 | 4.5 | R2 | 98.0 | 4.5 | favorite | R2 |
| 84-94 | 467 | 83.3 | 1 | 97.2 | -69.3 | DISABLE | — | -69.3 | favorite | DISABLE |

*Read-only. Zone-aware R is the input for the v6 parquet build (replaces max-EV picks). raw_max + in-sample caveat.*