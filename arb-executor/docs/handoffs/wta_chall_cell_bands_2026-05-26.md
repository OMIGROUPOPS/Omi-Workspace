# WTA_CHALL cell-band map — DP partition (MIN_N=100, raw_max exit, 10ct) — 2026-05-26

Read-only, local. Cells 5–94c partitioned into contiguous bands maximizing total $ (best single-R per band, exit-hit via **raw_max**, entered at anchor), each band **N≥100**; bands with negative max-R total are **DISABLE**.

> **Caveat:** `raw_max` is the unqualified peak (more optimistic than the deployed `size_qual_max_250` ≥250-depth realizable model). In-sample best-R per band.

- bands: **7** | tradeable total $ (positive bands): **$246.60** | disabled: 2

| band | N | wr% | best R | hit% | $/N | total $ | ROI% | action |
|---|---|---|---|---|---|---|---|---|
| 5-23 | 146 | 11.6 | 15 | 52.7 | 0.192 | 28.0 | 13.96 | R15 |
| 24-35 | 132 | 38.6 | 71 | 12.9 | 0.901 | 118.9 | 30.09 | R71 |
| 36-45 | 107 | 41.1 | 49 | 48.6 | 0.303 | 32.4 | 7.48 | R49 |
| 46-56 | 109 | 47.7 | 32 | 67.0 | 0.543 | 59.2 | 10.58 | R32 |
| 57-67 | 161 | 54.7 | 2 | 95.0 | -0.121 | -19.5 | -1.94 | DISABLE |
| 68-77 | 109 | 67.0 | 5 | 94.5 | 0.074 | 8.1 | 1.02 | R5 |
| 78-94 | 123 | 83.7 | 1 | 98.4 | -0.041 | -5.0 | -0.47 | DISABLE |

*Read-only on spike_perN. raw_max exit, in-sample best-R — see caveat. Bands feed Step 3 entry-rule optimization.*