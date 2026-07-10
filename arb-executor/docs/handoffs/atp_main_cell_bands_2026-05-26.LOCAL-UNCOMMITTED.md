# ATP_MAIN cell-band map — DP partition (MIN_N=100, raw_max exit, 10ct) — 2026-05-26

Read-only, local. Cells 5–94c partitioned into contiguous bands maximizing total $ (best single-R per band, exit-hit via **raw_max**, entered at anchor), each band **N≥100**; bands with negative max-R total are **DISABLE**.

> **Caveat:** `raw_max` is the unqualified peak (more optimistic than the deployed `size_qual_max_250` ≥250-depth realizable model). In-sample best-R per band.

> **Reconstruction note (2026-05-27):** This doc was regenerated from `atp_main_spike_perN.parquet` — the original 2026-05-26 run was never committed. The generalized script reproduces the other 3 categories' cell-band docs **exactly** (every band boundary, N, R, hit%, and $) and reproduces the deployed `adaptive_exit_bands.parquet` **to the penny** ($1,536.70). One methodology drift was found in the original ATP_MAIN run — see the reconciliation note at the bottom. The **30-band structure below is the original** (kept for consistency with the already-committed downstream `atp_main_entry_rules` / `drift_*` docs); all 30 band totals match the entry-rule taker baseline to the penny.

- bands: **30** | tradeable total $ (positive bands): **$1,620.40** | disabled: 3

| band | N | wr% | best R | hit% | $/N | total $ | ROI% | action |
|---|---|---|---|---|---|---|---|---|
| 5-9 | 113 | 11.5 | 63 | 21.2 | 0.801 | 90.5 | 114.85 | R63 |
| 10-16 | 193 | 6.7 | 6 | 80.3 | 0.232 | 44.8 | 17.69 | R6 |
| 17-19 | 107 | 24.3 | 54 | 37.4 | 0.898 | 96.1 | 50.16 | R54 |
| 20-22 | 106 | 24.5 | 52 | 40.6 | 0.861 | 91.3 | 40.96 | R52 |
| 23-25 | 120 | 20.0 | 22 | 63.3 | 0.508 | 60.9 | 21.06 | R22 |
| 26-28 | 138 | 34.8 | 71 | 36.2 | 0.854 | 117.8 | 31.62 | R71 |
| 29-30 | 111 | 29.7 | 31 | 56.8 | 0.573 | 63.6 | 19.40 | R31 |
| 31-32 | 100 | 24.0 | 14 | 75.0 | 0.263 | 26.3 | 8.33 | R14 |
| 33-35 | 163 | 30.1 | 29 | 60.7 | 0.423 | 68.9 | 12.37 | R29 |
| 36-37 | 117 | 36.8 | 39 | 57.3 | 0.675 | 79.0 | 18.51 | R39 |
| 38-40 | 192 | 29.7 | 1 | 96.9 | -0.024 | -4.7 | -0.63 | DISABLE |
| 41-42 | 126 | 40.5 | 32 | 64.3 | 0.573 | 72.2 | 13.81 | R32 |
| 43-44 | 107 | 43.0 | 54 | 48.6 | 0.386 | 41.3 | 8.87 | R54 |
| 45-46 | 126 | 50.8 | 48 | 58.7 | 0.941 | 118.6 | 20.68 | R48 |
| 47-48 | 110 | 34.5 | 11 | 82.7 | 0.090 | 9.9 | 1.90 | R11 |
| 49-51 | 129 | 55.0 | 50 | 17.8 | 0.723 | 93.3 | 14.48 | R50 |
| 52-54 | 146 | 50.0 | 11 | 84.9 | 0.136 | 19.9 | 2.57 | R11 |
| 55-56 | 126 | 61.1 | HOLD | — | 0.549 | 69.2 | 9.87 | HOLD |
| 57-58 | 126 | 54.0 | 18 | 77.0 | 0.063 | 8.0 | 1.10 | R18 |
| 59-61 | 191 | 64.9 | 35 | 69.6 | 0.614 | 117.2 | 10.23 | R35 |
| 62-64 | 210 | 62.4 | 12 | 88.6 | 0.342 | 71.8 | 5.43 | R12 |
| 65-66 | 136 | 66.2 | 33 | 67.6 | 0.119 | 16.2 | 1.82 | R33 |
| 67-68 | 123 | 61.8 | 2 | 96.7 | -0.026 | -3.2 | -0.39 | DISABLE |
| 69-71 | 152 | 73.7 | HOLD | — | 0.363 | 55.2 | 5.18 | HOLD |
| 72-74 | 168 | 69.6 | 2 | 98.8 | 0.111 | 18.6 | 1.52 | R2 |
| 75-76 | 104 | 73.1 | 8 | 94.2 | 0.318 | 33.1 | 4.22 | R8 |
| 77-79 | 134 | 76.9 | 14 | 88.1 | 0.305 | 40.9 | 3.92 | R14 |
| 80-82 | 120 | 70.8 | 1 | 98.3 | -0.038 | -4.6 | -0.47 | DISABLE |
| 83-86 | 153 | 86.9 | 15 | 49.0 | 0.440 | 67.3 | 5.21 | R15 |
| 87-94 | 190 | 89.5 | 2 | 99.5 | 0.150 | 28.5 | 1.66 | R2 |

*Read-only on spike_perN. raw_max exit, in-sample best-R — see caveat. Bands feed Step 3 entry-rule optimization.*

---

## Reconciliation (reconstruction validation, 2026-05-27)

**Cross-checks (all pass):**
- **All-band sum = $1,607.90**, identical to the `atp_main_entry_rules` doc's **taker baseline** ($1,607.90; operator ref ~$1,595, within 0.8%). Every one of the 30 bands matches that doc's per-band taker $ to the penny.
- Tradeable (positive bands) = **$1,620.40**; disabled = 3 (`38-40` −$4.7, `67-68` −$3.2, `80-82` −$4.6 → −$12.5; $1,620.40 − $12.5 = $1,607.90).
- The generalized script reproduces `wta_main` (28 bands/$1,507.50), `atp_chall` (33/$2,200.20), and `wta_chall` (7/$246.60) cell-band docs **exactly**, row-for-row, and the deployed `adaptive_exit_bands.parquet` to the penny ($1,536.70).

**PnL model (validated):** per ticker, if `raw_max ≥ cell + R` → capture **R**c (sell-at-target); else ride to settle — **win → 100−cell, loss → −cell** (raw settlement, no fee). ×10ct (SIZE 0.1). Note this differs from the *deployed* exit table's settlement (99−cell / −(cell−1), 1c-fee-adjusted); the cell-band docs use the raw convention. DP maximizes Σ max(band $, 0) (disabled bands contribute 0 → losses isolated, not pooled), tie-break = fewest bands.

**Methodology drift found (top of range, cells 83–94):** the original ATP_MAIN run's partition `83-86`($67.3) + `87-94`($28.5) = **$95.8** is **suboptimal**. Full enumeration of the 83–94 region (all N≥100 partitions) gives a strictly better split **`83-85`($56.9) + `86-89`($31.4) + `90-94`($13.9) = $102.2** (+$6.40, 31 bands total). The other 3 categories had no such gap. The **original 30-band structure is published above** for consistency with the already-committed downstream docs; the optimal alternative (31 bands / tradeable $1,626.80 / all-band $1,614.30) is noted here only. If the chain is ever rebuilt end-to-end, the 83–94 region should be re-partitioned and entry-rules re-run.
