# Exit config diff — OLD (deployed) vs NEW (proposed v6) — 2026-05-27

Read-only. Decision-gate audit before any swap. **OLD** = deployed `{cat}_adaptive_exit_bands.parquet` (per-cell `band_x`). **NEW (v6)** = `{cat}_cell_bands_2026-05-26.md` DP map (best-R per band + DISABLE).

## ⚠️ Model-mismatch caveat (read before judging better/worse)
- **OLD R was built on the deployed `size_qual_max_250` (≥250-depth realizable) + 99c settle-haircut model.**
- **NEW R was built on `raw_max` (unqualified peak) + 100/0 settle, in-sample best-R.** raw_max is structurally more optimistic (more/deeper captures look hittable than are realizable at depth).
- ⇒ OLD vs NEW R are **not apples-to-apples**; a 'deeper' NEW R partly reflects model optimism, not pure edge. Treat NEW as a candidate, not ground truth.

## PART A — open positions, line by line

6 legs across 4 events, all in **active (in-play)** matches; exits already resting at the OLD entry-time R. Current live bid/ask not returned by the public endpoint for in-play markets.

| leg | ticker | cat | entry (fill) | OLD R | OLD resting sell | NEW band | NEW R / action | NEW would-be sell | verdict |
|---|---|---|---|---|---|---|---|---|---|
| Duckworth | …DUCJOD-DUC | ATP_MAIN | 6c | 32 | 38 | 5-9 | R63 | 69 | BETTER (deeper, +EV*) |
| Jodar | …DUCJOD-JOD | ATP_MAIN | 95c | 4 | 98 | 90-94 | R2 | 97 | SHALLOWER |
| Swiatek | …BEJSWI-SWI | WTA_MAIN | 95c | 5 | 98 | 90-94 | DISABLE | — (no entry) | DISABLE |
| Svitolina | …SVIQUE-SVI | WTA_MAIN | 93c | 1 | 94 | 90-94 | DISABLE | — (no entry) | DISABLE |
| Rakhimova | …RAKMUC-RAK | WTA_MAIN | 11c | 7 | 18 | 10-14 | R46 | 57 | BETTER (deeper, +EV*) |
| Muchova | …RAKMUC-MUC | WTA_MAIN | 90c | 7 | 97 | 90-94 | DISABLE | — (no entry) | DISABLE |

\* *“+EV” per the raw_max model only — see caveat. For these already-open positions the exit is already resting at OLD R; a swap would NOT move it (see Part C).*

### Per-position note + DISABLE handling
- **Duckworth** (cell 6): OLD R32→NEW R63 (deeper). Underdog entered 6c; resting sell @38. New rule would target +63 (@69). Open-position impact: none (sell stays @38).
- **Jodar** (cell 94): OLD R4→NEW R2 (shallower). Sell @98 (capped). Minor.
- **Rakhimova** (cell 11): OLD R7→NEW R46 (much deeper). Sell @18 stays.
- **Swiatek / Svitolina / Muchova** (WTA_MAIN cells 94/93/90): **NEW = DISABLE** — the v6 map would not *enter* these high-favorite WTA cells (negative best-R EV). They are already open (sells @98/@94/@97).
  - **Cleanest behavior for an already-open DISABLE-cell position:** DISABLE governs *entry*, not exit. **Keep the existing resting sell live** — it's already an above-entry target and the position is sunk. Do **not** force a market exit (crystallizes loss/spread) and do **not** cancel-to-ride-settle unless the sell is clearly stale. (These are 90–95c favorites; the resting sell @94–98 is a fine exit; if unfilled, Bug-4 settlement closes it. No action needed.)

## PART B — full per-band diff, all 4 categories

### Change-category summary

| category | +1c_trap_removed | disabled_now | exit->hold | exit_deepened | exit_shallowed | rescued(hold->exit) | unchanged |
|---|---|---|---|---|---|---|---|
| ATP_MAIN | 9 | 8 | 3 | 35 | 27 | 4 | 4 |
| WTA_MAIN | 2 | 10 | 2 | 26 | 32 | 5 | 13 |
| ATP_CHALL | 4 | 13 | 2 | 29 | 30 | 3 | 9 |
| WTA_CHALL | 3 | 28 | 0 | 19 | 23 | 14 | 3 |

### ATP_MAIN — per-cell (5–94)

| cell | OLD band_x | NEW band | NEW R/action | change |
|---|---|---|---|---|
| 5 | 32 | 5-9 | R63 | exit_deepened **«** |
| 6 | 32 | 5-9 | R63 | exit_deepened **«** |
| 7 | 65 | 5-9 | R63 | exit_shallowed **«** |
| 8 | HOLD | 5-9 | R63 | rescued(hold->exit) **«** |
| 9 | HOLD | 5-9 | R63 | rescued(hold->exit) **«** |
| 10 | 1 | 10-16 | R6 | +1c_trap_removed **«** |
| 11 | 17 | 10-16 | R6 | exit_shallowed **«** |
| 12 | 17 | 10-16 | R6 | exit_shallowed **«** |
| 13 | 42 | 10-16 | R6 | exit_shallowed **«** |
| 14 | 42 | 10-16 | R6 | exit_shallowed **«** |
| 15 | 42 | 10-16 | R6 | exit_shallowed **«** |
| 16 | 4 | 10-16 | R6 | exit_deepened **«** |
| 17 | HOLD | 17-19 | R54 | rescued(hold->exit) **«** |
| 18 | 52 | 17-19 | R54 | exit_deepened **«** |
| 19 | 52 | 17-19 | R54 | exit_deepened **«** |
| 20 | 52 | 20-22 | R52 | unchanged |
| 21 | 8 | 20-22 | R52 | exit_deepened **«** |
| 22 | 45 | 20-22 | R52 | exit_deepened **«** |
| 23 | 23 | 23-25 | R22 | exit_shallowed **«** |
| 24 | 38 | 23-25 | R22 | exit_shallowed **«** |
| 25 | 24 | 23-25 | R22 | exit_shallowed **«** |
| 26 | 70 | 26-28 | R71 | exit_deepened **«** |
| 27 | 70 | 26-28 | R71 | exit_deepened **«** |
| 28 | 70 | 26-28 | R71 | exit_deepened **«** |
| 29 | 30 | 29-30 | R31 | exit_deepened **«** |
| 30 | 30 | 29-30 | R31 | exit_deepened **«** |
| 31 | 4 | 31-32 | R14 | exit_deepened **«** |
| 32 | 30 | 31-32 | R14 | exit_shallowed **«** |
| 33 | 42 | 33-35 | R29 | exit_shallowed **«** |
| 34 | 42 | 33-35 | R29 | exit_shallowed **«** |
| 35 | 28 | 33-35 | R29 | exit_deepened **«** |
| 36 | 37 | 36-37 | R39 | exit_deepened **«** |
| 37 | 37 | 36-37 | R39 | exit_deepened **«** |
| 38 | 1 | 38-40 | DISABLE | disabled_now **«** |
| 39 | 1 | 38-40 | DISABLE | disabled_now **«** |
| 40 | 1 | 38-40 | DISABLE | disabled_now **«** |
| 41 | 31 | 41-42 | R32 | exit_deepened **«** |
| 42 | 6 | 41-42 | R32 | exit_deepened **«** |
| 43 | 53 | 43-44 | R54 | exit_deepened **«** |
| 44 | 53 | 43-44 | R54 | exit_deepened **«** |
| 45 | 45 | 45-46 | R48 | exit_deepened **«** |
| 46 | 45 | 45-46 | R48 | exit_deepened **«** |
| 47 | 17 | 47-48 | R11 | exit_shallowed **«** |
| 48 | 8 | 47-48 | R11 | exit_deepened **«** |
| 49 | 8 | 49-51 | R50 | exit_deepened **«** |
| 50 | HOLD | 49-51 | R50 | rescued(hold->exit) **«** |
| 51 | 38 | 49-51 | R50 | exit_deepened **«** |
| 52 | 38 | 52-54 | R11 | exit_shallowed **«** |
| 53 | 1 | 52-54 | R11 | +1c_trap_removed **«** |
| 54 | 1 | 52-54 | R11 | +1c_trap_removed **«** |
| 55 | HOLD | 55-56 | HOLD | unchanged |
| 56 | HOLD | 55-56 | HOLD | unchanged |
| 57 | 1 | 57-58 | R18 | +1c_trap_removed **«** |
| 58 | 19 | 57-58 | R18 | exit_shallowed **«** |
| 59 | 40 | 59-61 | R35 | exit_shallowed **«** |
| 60 | 34 | 59-61 | R35 | exit_deepened **«** |
| 61 | 34 | 59-61 | R35 | exit_deepened **«** |
| 62 | 9 | 62-64 | R12 | exit_deepened **«** |
| 63 | 36 | 62-64 | R12 | exit_shallowed **«** |
| 64 | 36 | 62-64 | R12 | exit_shallowed **«** |
| 65 | 1 | 65-66 | R33 | +1c_trap_removed **«** |
| 66 | 32 | 65-66 | R33 | exit_deepened **«** |
| 67 | 3 | 67-68 | DISABLE | disabled_now **«** |
| 68 | 3 | 67-68 | DISABLE | disabled_now **«** |
| 69 | 29 | 69-71 | HOLD | exit->hold **«** |
| 70 | 17 | 69-71 | HOLD | exit->hold **«** |
| 71 | 26 | 69-71 | HOLD | exit->hold **«** |
| 72 | 1 | 72-74 | R2 | +1c_trap_removed **«** |
| 73 | 4 | 72-74 | R2 | exit_shallowed **«** |
| 74 | 14 | 72-74 | R2 | exit_shallowed **«** |
| 75 | 1 | 75-76 | R8 | +1c_trap_removed **«** |
| 76 | 1 | 75-76 | R8 | +1c_trap_removed **«** |
| 77 | 1 | 77-79 | R14 | +1c_trap_removed **«** |
| 78 | 14 | 77-79 | R14 | unchanged |
| 79 | 19 | 77-79 | R14 | exit_shallowed **«** |
| 80 | 1 | 80-82 | DISABLE | disabled_now **«** |
| 81 | 1 | 80-82 | DISABLE | disabled_now **«** |
| 82 | 6 | 80-82 | DISABLE | disabled_now **«** |
| 83 | 13 | 83-85 | R15 | exit_deepened **«** |
| 84 | 13 | 83-85 | R15 | exit_deepened **«** |
| 85 | 13 | 83-85 | R15 | exit_deepened **«** |
| 86 | 13 | 86-89 | R11 | exit_shallowed **«** |
| 87 | 10 | 86-89 | R11 | exit_deepened **«** |
| 88 | 10 | 86-89 | R11 | exit_deepened **«** |
| 89 | 10 | 86-89 | R11 | exit_deepened **«** |
| 90 | 10 | 90-94 | R2 | exit_shallowed **«** |
| 91 | 4 | 90-94 | R2 | exit_shallowed **«** |
| 92 | 4 | 90-94 | R2 | exit_shallowed **«** |
| 93 | 4 | 90-94 | R2 | exit_shallowed **«** |
| 94 | 4 | 90-94 | R2 | exit_shallowed **«** |

### WTA_MAIN — per-cell (5–94)

| cell | OLD band_x | NEW band | NEW R/action | change |
|---|---|---|---|---|
| 5 | 74 | 5-9 | R25 | exit_shallowed **«** |
| 6 | 74 | 5-9 | R25 | exit_shallowed **«** |
| 7 | 29 | 5-9 | R25 | exit_shallowed **«** |
| 8 | 29 | 5-9 | R25 | exit_shallowed **«** |
| 9 | 15 | 5-9 | R25 | exit_deepened **«** |
| 10 | 79 | 10-14 | R46 | exit_shallowed **«** |
| 11 | 7 | 10-14 | R46 | exit_deepened **«** |
| 12 | HOLD | 10-14 | R46 | rescued(hold->exit) **«** |
| 13 | HOLD | 10-14 | R46 | rescued(hold->exit) **«** |
| 14 | 46 | 10-14 | R46 | unchanged |
| 15 | 46 | 15-18 | R79 | exit_deepened **«** |
| 16 | 46 | 15-18 | R79 | exit_deepened **«** |
| 17 | 81 | 15-18 | R79 | exit_shallowed **«** |
| 18 | 81 | 15-18 | R79 | exit_shallowed **«** |
| 19 | 81 | 19-21 | R33 | exit_shallowed **«** |
| 20 | 32 | 19-21 | R33 | exit_deepened **«** |
| 21 | 43 | 19-21 | R33 | exit_shallowed **«** |
| 22 | 43 | 22-24 | R45 | exit_deepened **«** |
| 23 | 35 | 22-24 | R45 | exit_deepened **«** |
| 24 | 54 | 22-24 | R45 | exit_shallowed **«** |
| 25 | 16 | 25-27 | R31 | exit_deepened **«** |
| 26 | HOLD | 25-27 | R31 | rescued(hold->exit) **«** |
| 27 | HOLD | 25-27 | R31 | rescued(hold->exit) **«** |
| 28 | 45 | 28-30 | R39 | exit_shallowed **«** |
| 29 | 53 | 28-30 | R39 | exit_shallowed **«** |
| 30 | 69 | 28-30 | R39 | exit_shallowed **«** |
| 31 | 17 | 31-32 | R34 | exit_deepened **«** |
| 32 | 32 | 31-32 | R34 | exit_deepened **«** |
| 33 | HOLD | 33-35 | HOLD | unchanged |
| 34 | HOLD | 33-35 | HOLD | unchanged |
| 35 | HOLD | 33-35 | HOLD | unchanged |
| 36 | 1 | 36-38 | R7 | +1c_trap_removed **«** |
| 37 | 1 | 36-38 | R7 | +1c_trap_removed **«** |
| 38 | 37 | 36-38 | R7 | exit_shallowed **«** |
| 39 | 37 | 39-41 | R35 | exit_shallowed **«** |
| 40 | 59 | 39-41 | R35 | exit_shallowed **«** |
| 41 | 36 | 39-41 | R35 | exit_shallowed **«** |
| 42 | 57 | 42-44 | R56 | exit_shallowed **«** |
| 43 | 53 | 42-44 | R56 | exit_deepened **«** |
| 44 | 53 | 42-44 | R56 | exit_deepened **«** |
| 45 | 43 | 45-47 | R44 | exit_deepened **«** |
| 46 | HOLD | 45-47 | R44 | rescued(hold->exit) **«** |
| 47 | 49 | 45-47 | R44 | exit_shallowed **«** |
| 48 | 49 | 48-49 | R45 | exit_shallowed **«** |
| 49 | 49 | 48-49 | R45 | exit_shallowed **«** |
| 50 | 45 | 50-52 | R6 | exit_shallowed **«** |
| 51 | 45 | 50-52 | R6 | exit_shallowed **«** |
| 52 | 32 | 50-52 | R6 | exit_shallowed **«** |
| 53 | 32 | 53-54 | DISABLE | disabled_now **«** |
| 54 | 11 | 53-54 | DISABLE | disabled_now **«** |
| 55 | 29 | 55-57 | R10 | exit_shallowed **«** |
| 56 | 4 | 55-57 | R10 | exit_deepened **«** |
| 57 | 31 | 55-57 | R10 | exit_shallowed **«** |
| 58 | 37 | 58-59 | R8 | exit_shallowed **«** |
| 59 | 4 | 58-59 | R8 | exit_deepened **«** |
| 60 | 38 | 60-61 | HOLD | exit->hold **«** |
| 61 | 38 | 60-61 | HOLD | exit->hold **«** |
| 62 | 35 | 62-65 | R36 | exit_deepened **«** |
| 63 | 35 | 62-65 | R36 | exit_deepened **«** |
| 64 | 35 | 62-65 | R36 | exit_deepened **«** |
| 65 | 35 | 62-65 | R36 | exit_deepened **«** |
| 66 | 19 | 66-69 | R20 | exit_deepened **«** |
| 67 | 11 | 66-69 | R20 | exit_deepened **«** |
| 68 | 3 | 66-69 | R20 | exit_deepened **«** |
| 69 | 3 | 66-69 | R20 | exit_deepened **«** |
| 70 | 22 | 70-71 | R22 | unchanged |
| 71 | 22 | 70-71 | R22 | unchanged |
| 72 | 1 | 72-75 | R1 | unchanged |
| 73 | 1 | 72-75 | R1 | unchanged |
| 74 | 23 | 72-75 | R1 | exit_shallowed **«** |
| 75 | 1 | 72-75 | R1 | unchanged |
| 76 | 15 | 76-78 | R10 | exit_shallowed **«** |
| 77 | 22 | 76-78 | R10 | exit_shallowed **«** |
| 78 | 18 | 76-78 | R10 | exit_shallowed **«** |
| 79 | 7 | 79-82 | R11 | exit_deepened **«** |
| 80 | 7 | 79-82 | R11 | exit_deepened **«** |
| 81 | 7 | 79-82 | R11 | exit_deepened **«** |
| 82 | 17 | 79-82 | R11 | exit_shallowed **«** |
| 83 | 6 | 83-85 | DISABLE | disabled_now **«** |
| 84 | 6 | 83-85 | DISABLE | disabled_now **«** |
| 85 | 13 | 83-85 | DISABLE | disabled_now **«** |
| 86 | 3 | 86-89 | R3 | unchanged |
| 87 | 3 | 86-89 | R3 | unchanged |
| 88 | 3 | 86-89 | R3 | unchanged |
| 89 | 3 | 86-89 | R3 | unchanged |
| 90 | 7 | 90-94 | DISABLE | disabled_now **«** |
| 91 | 7 | 90-94 | DISABLE | disabled_now **«** |
| 92 | 1 | 90-94 | DISABLE | disabled_now **«** |
| 93 | 1 | 90-94 | DISABLE | disabled_now **«** |
| 94 | 5 | 90-94 | DISABLE | disabled_now **«** |

### ATP_CHALL — per-cell (5–94)

| cell | OLD band_x | NEW band | NEW R/action | change |
|---|---|---|---|---|
| 5 | 7 | 5-8 | R9 | exit_deepened **«** |
| 6 | 7 | 5-8 | R9 | exit_deepened **«** |
| 7 | 7 | 5-8 | R9 | exit_deepened **«** |
| 8 | 7 | 5-8 | R9 | exit_deepened **«** |
| 9 | 64 | 9-12 | R64 | unchanged |
| 10 | 27 | 9-12 | R64 | exit_deepened **«** |
| 11 | 27 | 9-12 | R64 | exit_deepened **«** |
| 12 | 78 | 9-12 | R64 | exit_shallowed **«** |
| 13 | 49 | 13-14 | R49 | unchanged |
| 14 | 49 | 13-14 | R49 | unchanged |
| 15 | 41 | 15-17 | R43 | exit_deepened **«** |
| 16 | 14 | 15-17 | R43 | exit_deepened **«** |
| 17 | 37 | 15-17 | R43 | exit_deepened **«** |
| 18 | 72 | 18-19 | R57 | exit_shallowed **«** |
| 19 | HOLD | 18-19 | R57 | rescued(hold->exit) **«** |
| 20 | 32 | 20-22 | R22 | exit_shallowed **«** |
| 21 | 21 | 20-22 | R22 | exit_deepened **«** |
| 22 | 21 | 20-22 | R22 | exit_deepened **«** |
| 23 | 46 | 23-25 | R47 | exit_deepened **«** |
| 24 | 50 | 23-25 | R47 | exit_shallowed **«** |
| 25 | 24 | 23-25 | R47 | exit_deepened **«** |
| 26 | 21 | 26-27 | R61 | exit_deepened **«** |
| 27 | 59 | 26-27 | R61 | exit_deepened **«** |
| 28 | 18 | 28-29 | R30 | exit_deepened **«** |
| 29 | 66 | 28-29 | R30 | exit_shallowed **«** |
| 30 | 66 | 30-31 | R15 | exit_shallowed **«** |
| 31 | 17 | 30-31 | R15 | exit_shallowed **«** |
| 32 | 8 | 32-33 | R6 | exit_shallowed **«** |
| 33 | 8 | 32-33 | R6 | exit_shallowed **«** |
| 34 | 49 | 34-35 | R52 | exit_deepened **«** |
| 35 | 8 | 34-35 | R52 | exit_deepened **«** |
| 36 | 43 | 36-37 | R44 | exit_deepened **«** |
| 37 | 43 | 36-37 | R44 | exit_deepened **«** |
| 38 | 10 | 38-39 | R10 | unchanged |
| 39 | 10 | 38-39 | R10 | unchanged |
| 40 | 59 | 40-41 | R37 | exit_shallowed **«** |
| 41 | 35 | 40-41 | R37 | exit_deepened **«** |
| 42 | 52 | 42-44 | R53 | exit_deepened **«** |
| 43 | 55 | 42-44 | R53 | exit_shallowed **«** |
| 44 | 55 | 42-44 | R53 | exit_shallowed **«** |
| 45 | 55 | 45-46 | R27 | exit_shallowed **«** |
| 46 | 55 | 45-46 | R27 | exit_shallowed **«** |
| 47 | 55 | 47-48 | R24 | exit_shallowed **«** |
| 48 | 47 | 47-48 | R24 | exit_shallowed **«** |
| 49 | 18 | 49-50 | R19 | exit_deepened **«** |
| 50 | 15 | 49-50 | R19 | exit_deepened **«** |
| 51 | 33 | 51-52 | R24 | exit_shallowed **«** |
| 52 | 33 | 51-52 | R24 | exit_shallowed **«** |
| 53 | HOLD | 53-55 | R7 | rescued(hold->exit) **«** |
| 54 | 1 | 53-55 | R7 | +1c_trap_removed **«** |
| 55 | 12 | 53-55 | R7 | exit_shallowed **«** |
| 56 | 12 | 56-57 | R13 | exit_deepened **«** |
| 57 | 12 | 56-57 | R13 | exit_deepened **«** |
| 58 | 23 | 58-59 | R16 | exit_shallowed **«** |
| 59 | 18 | 58-59 | R16 | exit_shallowed **«** |
| 60 | 3 | 60-61 | R1 | exit_shallowed **«** |
| 61 | 3 | 60-61 | R1 | exit_shallowed **«** |
| 62 | 29 | 62-63 | R10 | exit_shallowed **«** |
| 63 | 12 | 62-63 | R10 | exit_shallowed **«** |
| 64 | 1 | 64-65 | R4 | +1c_trap_removed **«** |
| 65 | 1 | 64-65 | R4 | +1c_trap_removed **«** |
| 66 | 33 | 66-67 | R17 | exit_shallowed **«** |
| 67 | 12 | 66-67 | R17 | exit_deepened **«** |
| 68 | 30 | 68-71 | R27 | exit_shallowed **«** |
| 69 | 25 | 68-71 | R27 | exit_deepened **«** |
| 70 | HOLD | 68-71 | R27 | rescued(hold->exit) **«** |
| 71 | 27 | 68-71 | R27 | unchanged |
| 72 | 1 | 72-73 | R13 | +1c_trap_removed **«** |
| 73 | 12 | 72-73 | R13 | exit_deepened **«** |
| 74 | HOLD | 74-78 | HOLD | unchanged |
| 75 | 14 | 74-78 | HOLD | exit->hold **«** |
| 76 | HOLD | 74-78 | HOLD | unchanged |
| 77 | HOLD | 74-78 | HOLD | unchanged |
| 78 | 19 | 74-78 | HOLD | exit->hold **«** |
| 79 | 5 | 79-80 | DISABLE | disabled_now **«** |
| 80 | 16 | 79-80 | DISABLE | disabled_now **«** |
| 81 | 5 | 81-83 | R2 | exit_shallowed **«** |
| 82 | 5 | 81-83 | R2 | exit_shallowed **«** |
| 83 | 5 | 81-83 | R2 | exit_shallowed **«** |
| 84 | 5 | 84-94 | DISABLE | disabled_now **«** |
| 85 | HOLD | 84-94 | DISABLE | disabled_now **«** |
| 86 | 4 | 84-94 | DISABLE | disabled_now **«** |
| 87 | 12 | 84-94 | DISABLE | disabled_now **«** |
| 88 | 1 | 84-94 | DISABLE | disabled_now **«** |
| 89 | 1 | 84-94 | DISABLE | disabled_now **«** |
| 90 | 1 | 84-94 | DISABLE | disabled_now **«** |
| 91 | 1 | 84-94 | DISABLE | disabled_now **«** |
| 92 | 1 | 84-94 | DISABLE | disabled_now **«** |
| 93 | 1 | 84-94 | DISABLE | disabled_now **«** |
| 94 | 1 | 84-94 | DISABLE | disabled_now **«** |

### WTA_CHALL — per-cell (5–94)

| cell | OLD band_x | NEW band | NEW R/action | change |
|---|---|---|---|---|
| 5 | 62 | 5-23 | R15 | exit_shallowed **«** |
| 6 | 62 | 5-23 | R15 | exit_shallowed **«** |
| 7 | 18 | 5-23 | R15 | exit_shallowed **«** |
| 8 | 7 | 5-23 | R15 | exit_deepened **«** |
| 9 | HOLD | 5-23 | R15 | rescued(hold->exit) **«** |
| 10 | HOLD | 5-23 | R15 | rescued(hold->exit) **«** |
| 11 | HOLD | 5-23 | R15 | rescued(hold->exit) **«** |
| 12 | 67 | 5-23 | R15 | exit_shallowed **«** |
| 13 | 6 | 5-23 | R15 | exit_deepened **«** |
| 14 | 83 | 5-23 | R15 | exit_shallowed **«** |
| 15 | 83 | 5-23 | R15 | exit_shallowed **«** |
| 16 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 17 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 18 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 19 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 20 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 21 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 22 | 16 | 5-23 | R15 | exit_shallowed **«** |
| 23 | 5 | 5-23 | R15 | exit_deepened **«** |
| 24 | HOLD | 24-35 | R71 | rescued(hold->exit) **«** |
| 25 | HOLD | 24-35 | R71 | rescued(hold->exit) **«** |
| 26 | 1 | 24-35 | R71 | +1c_trap_removed **«** |
| 27 | 27 | 24-35 | R71 | exit_deepened **«** |
| 28 | HOLD | 24-35 | R71 | rescued(hold->exit) **«** |
| 29 | HOLD | 24-35 | R71 | rescued(hold->exit) **«** |
| 30 | HOLD | 24-35 | R71 | rescued(hold->exit) **«** |
| 31 | 12 | 24-35 | R71 | exit_deepened **«** |
| 32 | HOLD | 24-35 | R71 | rescued(hold->exit) **«** |
| 33 | 42 | 24-35 | R71 | exit_deepened **«** |
| 34 | 1 | 24-35 | R71 | +1c_trap_removed **«** |
| 35 | 63 | 24-35 | R71 | exit_deepened **«** |
| 36 | 63 | 36-45 | R49 | exit_shallowed **«** |
| 37 | 63 | 36-45 | R49 | exit_shallowed **«** |
| 38 | 3 | 36-45 | R49 | exit_deepened **«** |
| 39 | 20 | 36-45 | R49 | exit_deepened **«** |
| 40 | 48 | 36-45 | R49 | exit_deepened **«** |
| 41 | 48 | 36-45 | R49 | exit_deepened **«** |
| 42 | 57 | 36-45 | R49 | exit_shallowed **«** |
| 43 | 2 | 36-45 | R49 | exit_deepened **«** |
| 44 | 2 | 36-45 | R49 | exit_deepened **«** |
| 45 | HOLD | 36-45 | R49 | rescued(hold->exit) **«** |
| 46 | 19 | 46-56 | R32 | exit_deepened **«** |
| 47 | 1 | 46-56 | R32 | +1c_trap_removed **«** |
| 48 | HOLD | 46-56 | R32 | rescued(hold->exit) **«** |
| 49 | HOLD | 46-56 | R32 | rescued(hold->exit) **«** |
| 50 | 20 | 46-56 | R32 | exit_deepened **«** |
| 51 | 3 | 46-56 | R32 | exit_deepened **«** |
| 52 | 20 | 46-56 | R32 | exit_deepened **«** |
| 53 | 41 | 46-56 | R32 | exit_shallowed **«** |
| 54 | 41 | 46-56 | R32 | exit_shallowed **«** |
| 55 | 20 | 46-56 | R32 | exit_deepened **«** |
| 56 | 38 | 46-56 | R32 | exit_shallowed **«** |
| 57 | 11 | 57-67 | DISABLE | disabled_now **«** |
| 58 | 22 | 57-67 | DISABLE | disabled_now **«** |
| 59 | 1 | 57-67 | DISABLE | disabled_now **«** |
| 60 | 8 | 57-67 | DISABLE | disabled_now **«** |
| 61 | 4 | 57-67 | DISABLE | disabled_now **«** |
| 62 | HOLD | 57-67 | DISABLE | disabled_now **«** |
| 63 | 12 | 57-67 | DISABLE | disabled_now **«** |
| 64 | HOLD | 57-67 | DISABLE | disabled_now **«** |
| 65 | 8 | 57-67 | DISABLE | disabled_now **«** |
| 66 | 31 | 57-67 | DISABLE | disabled_now **«** |
| 67 | 4 | 57-67 | DISABLE | disabled_now **«** |
| 68 | 4 | 68-77 | R5 | exit_deepened **«** |
| 69 | HOLD | 68-77 | R5 | rescued(hold->exit) **«** |
| 70 | HOLD | 68-77 | R5 | rescued(hold->exit) **«** |
| 71 | 5 | 68-77 | R5 | unchanged |
| 72 | 5 | 68-77 | R5 | unchanged |
| 73 | 5 | 68-77 | R5 | unchanged |
| 74 | 10 | 68-77 | R5 | exit_shallowed **«** |
| 75 | 20 | 68-77 | R5 | exit_shallowed **«** |
| 76 | 20 | 68-77 | R5 | exit_shallowed **«** |
| 77 | 20 | 68-77 | R5 | exit_shallowed **«** |
| 78 | 20 | 78-94 | DISABLE | disabled_now **«** |
| 79 | 20 | 78-94 | DISABLE | disabled_now **«** |
| 80 | 13 | 78-94 | DISABLE | disabled_now **«** |
| 81 | 13 | 78-94 | DISABLE | disabled_now **«** |
| 82 | 1 | 78-94 | DISABLE | disabled_now **«** |
| 83 | 1 | 78-94 | DISABLE | disabled_now **«** |
| 84 | 1 | 78-94 | DISABLE | disabled_now **«** |
| 85 | 1 | 78-94 | DISABLE | disabled_now **«** |
| 86 | 11 | 78-94 | DISABLE | disabled_now **«** |
| 87 | 11 | 78-94 | DISABLE | disabled_now **«** |
| 88 | 11 | 78-94 | DISABLE | disabled_now **«** |
| 89 | 2 | 78-94 | DISABLE | disabled_now **«** |
| 90 | 2 | 78-94 | DISABLE | disabled_now **«** |
| 91 | HOLD | 78-94 | DISABLE | disabled_now **«** |
| 92 | HOLD | 78-94 | DISABLE | disabled_now **«** |
| 93 | 1 | 78-94 | DISABLE | disabled_now **«** |
| 94 | 5 | 78-94 | DISABLE | disabled_now **«** |

## PART C — swap mechanics (code-traced)

- **Hot-swap mid-session: NO live effect.** `_load_exit_table()` is called **only once at init** (line 955); the table is cached in `self.exit_table`. There is no file-watch and no reload on tick. Replacing the parquet does nothing until the process restarts.
- **Existing open positions keep their entry-time R.** Exits are resolved at **fill time** (`_v4_apply_exit` → `exit_rule_for(category, fill_price)`, ~line 2043) and posted immediately. On **restart**, `_v4_reconcile_naked` (~3463–3469) **adopts an existing resting sell** as-is (reads it from the book; does not re-resolve). Only **naked** positions (hold cells, or exits that were cancelled) get re-resolved against the new table. ⇒ a swap+restart does **not** move the 6 open legs' exits.
- **DISABLE while a position is open:** the running bot has **no DISABLE concept** — `exit_rule_for` returns only `exit`/`hold`. Worse, **`_load_exit_table` parses `band_exit_X` as `HOLD` or `int(float(raw))`** — a literal `"DISABLE"` value would raise `ValueError` and **crash the bot on the next restart**. A v6 parquet must encode DISABLE bands as **`HOLD`** (ride-to-settle) — or it needs a code change to add a disable rule. For an already-open position on a (newly) DISABLE cell, nothing changes live (cached table); on restart it either keeps its resting sell (adopted) or, if naked + DISABLE→HOLD, rides to settle.
- **Safest swap sequence (no code change, exit_R-only):**
  1. Build the v6 `{cat}_adaptive_exit_bands.parquet` in the **deployed schema** (`price_low, price_high, band_exit_X`), encoding **DISABLE→HOLD** (so the loader can't crash and disabled cells ride to settle).
  2. Swap can happen anytime (no live effect until restart); existing resting exits are preserved on restart. To apply v6 to **new** entries, **restart during a no-placement window** (no event within its placement_minute), so no entry is mid-flight.
  3. Because existing exits are adopted on restart, **no need to drain positions first** — only new fills pick up v6. Verify post-restart: `EXIT_TABLE_LOADED` band counts match v6, 0 tracebacks, reconcile shows 0 orphans.
  - If you want DISABLE to actually **block entries** (not just ride-to-settle on exit), that requires the entry-path change from `live_v4_gaps_2026-05-27.md` (the exit parquet only governs the exit side; entry still uses `per_regime_offsets_v2.csv`).

*Read-only. No parquet writes, no swap, no restart. Operator reviews, then decides swap timing.*