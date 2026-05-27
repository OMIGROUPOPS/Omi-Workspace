# WTA_CHALL zone-aware risk-adjusted exit R — 2026-05-27

Read-only, local. Same DP band boundaries as `wta_chall_cell_bands_2026-05-26.md`; R re-selected per zone. **raw_max** exit, 10ct (caveat: raw_max optimistic vs deployed size_qual; in-sample).

**Zone rule (by avg cell price in band):** underdog `<26` → keep max-EV · mid `26–74` → R≥3 ∧ hit≥60% ∧ total≥75%·maxEV, pick **highest hit** (relax 75% if none; else max-EV) · favorite `≥75` → keep max-EV. DISABLE (maxEV total ≤0) stays DISABLE.

## Headline
- **Total $ max-EV: $246.60** → **zone-aware: $93.50** — retention **37.9%**.
- Bands where R changed (zone-aware ≠ max-EV): **3** / 7.
- zones: underdog:1, mid:5, favorite:1 | DISABLE:2

| band | N | wr% | maxEV R | maxEV hit% | maxEV $ | ZA R | ZA hit% | ZA $ | zone | action |
|---|---|---|---|---|---|---|---|---|---|---|
| 5-23 | 146 | 11.6 | 15 | 52.7 | 28.0 | R15 | 52.7 | 28.0 | underdog | R15 |
| 24-35 | 132 | 38.6 | 71 | 12.9 | 118.9 | R3 | 92.4 | 7.6 | mid | R3 (relaxed) |
| 36-45 | 107 | 41.1 | 49 | 48.6 | 32.4 | R3 | 90.7 | -11.1 | mid | R3 (relaxed) |
| 46-56 | 109 | 47.7 | 32 | 67.0 | 59.2 | R21 | 76.1 | 49.8 | mid | R21 |
| 57-67 | 161 | 54.7 | 2 | 95.0 | -19.5 | DISABLE | — | -19.5 | mid | DISABLE |
| 68-77 | 109 | 67.0 | 5 | 94.5 | 8.1 | R5 | 94.5 | 8.1 | mid | R5 |
| 78-94 | 123 | 83.7 | 1 | 98.4 | -5.0 | DISABLE | — | -5.0 | favorite | DISABLE |

*Read-only. Zone-aware R is the input for the v6 parquet build (replaces max-EV picks). raw_max + in-sample caveat.*