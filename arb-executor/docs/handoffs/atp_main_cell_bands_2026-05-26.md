# ATP_MAIN cell-band map — DP partition (MIN_N=100, raw_max exit, 10ct) — 2026-05-26

Read-only, local. Cells 5–94c partitioned into contiguous bands maximizing total $ (best single-R per band, exit-hit via **raw_max**, entered at anchor), each band **N≥100**; bands with negative max-R total are **DISABLE**.

> **Caveat:** `raw_max` is the unqualified peak (more optimistic than the deployed `size_qual_max_250` ≥250-depth realizable model). In-sample best-R per band.

- bands: **31** | tradeable total $ (positive bands): **$1,626.80** | disabled: 3

## 31-band reconciliation (methodology-drift note for future rebuilds)
This DP partition (MIN_N=100) produces **31 bands** with an **all-bands total of $1,614.30** (positive-only "tradeable" = $1,626.80; the 3 disabled bands 38–40, 67–68, 80–82 net −$12.50). The earlier ATP_MAIN **entry-rules** task (`atp_main_entry_rules_2026-05-26.md`) used a **hand-given 30-band list** whose all-bands taker baseline was **$1,607.90**.

**The DP-optimal 31-band partition is strictly better: $1,614.30 vs $1,607.90 → +$6.40** on the same all-bands (best-R-at-anchor) basis. The drift is purely the band boundaries — the 30-band list was supplied externally; the DP (this doc's method) is the reproducible, optimal partition. **Future rebuilds and the entry-rule layer should key off this 31-band DP map, not the legacy 30-band list.** (Both use raw_max + in-sample best-R; see caveat.)

| band | N | wr% | best R | hit% | $/N | total $ | ROI% | action |
|---|---|---|---|---|---|---|---|---|
| 5-9 | 113 | 11.5 | 63 | 21.2 | 0.801 | 90.5 | 114.85 | R63 |
| 10-16 | 193 | 6.7 | 6 | 80.3 | 0.232 | 44.8 | 17.69 | R6 |
| 17-19 | 107 | 24.3 | 54 | 37.4 | 0.898 | 96.1 | 50.16 | R54 |
| 20-22 | 106 | 24.5 | 52 | 40.6 | 0.861 | 91.3 | 40.96 | R52 |
| 23-25 | 120 | 20.0 | 22 | 63.3 | 0.508 | 60.9 | 21.06 | R22 |
| 26-28 | 138 | 34.8 | 71 | 36.2 | 0.854 | 117.8 | 31.62 | R71 |
| 29-30 | 111 | 29.7 | 31 | 56.8 | 0.573 | 63.6 | 19.4 | R31 |
| 31-32 | 100 | 24.0 | 14 | 75.0 | 0.263 | 26.3 | 8.33 | R14 |
| 33-35 | 163 | 30.1 | 29 | 60.7 | 0.423 | 68.9 | 12.37 | R29 |
| 36-37 | 117 | 36.8 | 39 | 57.3 | 0.675 | 79.0 | 18.51 | R39 |
| 38-40 | 192 | 29.7 | 1 | 96.9 | -0.024 | -4.7 | -0.63 | DISABLE |
| 41-42 | 126 | 40.5 | 32 | 64.3 | 0.573 | 72.2 | 13.81 | R32 |
| 43-44 | 107 | 43.0 | 54 | 48.6 | 0.386 | 41.3 | 8.87 | R54 |
| 45-46 | 126 | 50.8 | 48 | 58.7 | 0.941 | 118.6 | 20.68 | R48 |
| 47-48 | 110 | 34.5 | 11 | 82.7 | 0.09 | 9.9 | 1.9 | R11 |
| 49-51 | 129 | 55.0 | 50 | 17.8 | 0.723 | 93.3 | 14.48 | R50 |
| 52-54 | 146 | 50.0 | 11 | 84.9 | 0.136 | 19.9 | 2.57 | R11 |
| 55-56 | 126 | 61.1 | HOLD | — | 0.549 | 69.2 | 9.87 | HOLD |
| 57-58 | 126 | 54.0 | 18 | 77.0 | 0.063 | 8.0 | 1.1 | R18 |
| 59-61 | 191 | 64.9 | 35 | 69.6 | 0.614 | 117.2 | 10.23 | R35 |
| 62-64 | 210 | 62.4 | 12 | 88.6 | 0.342 | 71.8 | 5.43 | R12 |
| 65-66 | 136 | 66.2 | 33 | 67.6 | 0.119 | 16.2 | 1.82 | R33 |
| 67-68 | 123 | 61.8 | 2 | 96.7 | -0.026 | -3.2 | -0.39 | DISABLE |
| 69-71 | 152 | 73.7 | HOLD | — | 0.363 | 55.2 | 5.18 | HOLD |
| 72-74 | 168 | 69.6 | 2 | 98.8 | 0.111 | 18.6 | 1.52 | R2 |
| 75-76 | 104 | 73.1 | 8 | 94.2 | 0.318 | 33.1 | 4.22 | R8 |
| 77-79 | 134 | 76.9 | 14 | 88.1 | 0.305 | 40.9 | 3.92 | R14 |
| 80-82 | 120 | 70.8 | 1 | 98.3 | -0.038 | -4.6 | -0.47 | DISABLE |
| 83-85 | 117 | 86.3 | 15 | 64.1 | 0.486 | 56.9 | 5.8 | R15 |
| 86-89 | 109 | 88.1 | 11 | 71.6 | 0.288 | 31.4 | 3.3 | R11 |
| 90-94 | 117 | 90.6 | 2 | 99.1 | 0.119 | 13.9 | 1.29 | R2 |

*Read-only on spike_perN. raw_max exit, in-sample best-R — see caveat. Bands feed Step 3 entry-rule optimization.*