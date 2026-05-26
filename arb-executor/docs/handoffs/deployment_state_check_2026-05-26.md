# Deployment state check — live vs staged v5 vs targeted-sweep — 2026-05-26

**Disk evidence only. No analysis, no recommendations.** Read-only on live state; no deployed file modified.

## Sources (on disk)
- **Live exit table (what PID 3191329 reads):** `config/deploy_v5_live.json` → `exit_table_dir: data/durable/spike_volatility_map/`, `exit_band_resolution: adaptive_calibrated_2026-05-24` → `{cat}_adaptive_exit_bands.parquet`. Startup log `EXIT_TABLE_LOADED` bands 55/57/61/55. md5:
  - `atp_main_adaptive_exit_bands.parquet` md5 `342e8f4e4b6bb1093e99148eb26eb214`
  - `wta_main_adaptive_exit_bands.parquet` md5 `e6aefbc24764eba7fd6926bc876cbbb6`
  - `atp_chall_adaptive_exit_bands.parquet` md5 `f2d14c949e0a5481ff3f7ac0f72ed4f6`
  - `wta_chall_adaptive_exit_bands.parquet` md5 `f13ceb421c0544d17c0293b4de971810`
- **Staged v5:** `{cat}_singleR_v5.parquet` (uncommitted).
- **Targeted sweep recs:** `docs/handoffs/exit_sweep_targeted_2026-05-25.md` (Group A rescue/disable, Group B deepen).
- generated: 2026-05-26T16:08:56.290268Z

## ATP_MAIN

| cell_id | currently_live_X | v5_singleR_proposed_X | targeted_sweep_action | mismatch |
|---|---|---|---|---|
| 5 | 32 | 15 | RESCUE_to_15 | TRUE |
| 6 | 32 | 32 | unchanged |  |
| 7 | 65 | 65 | unchanged |  |
| 8 | HOLD | HOLD | unchanged |  |
| 9 | HOLD | HOLD | unchanged |  |
| 10 | 1 | 1 | unchanged |  |
| 11 | 17 | 17 | unchanged |  |
| 12 | 17 | 17 | unchanged |  |
| 13 | 42 | 42 | unchanged |  |
| 14 | 42 | 51 | unchanged | TRUE |
| 15 | 42 | 57 | unchanged | TRUE |
| 16 | 4 | 4 | unchanged |  |
| 17 | HOLD | HOLD | unchanged |  |
| 18 | 52 | 57 | unchanged | TRUE |
| 19 | 52 | 70 | unchanged | TRUE |
| 20 | 52 | 52 | unchanged |  |
| 21 | 8 | 8 | unchanged |  |
| 22 | 45 | 45 | unchanged |  |
| 23 | 23 | 23 | unchanged |  |
| 24 | 38 | 38 | unchanged |  |
| 25 | 24 | 24 | unchanged |  |
| 26 | 70 | HOLD | unchanged | TRUE |
| 27 | 70 | HOLD | unchanged | TRUE |
| 28 | 70 | 70 | unchanged |  |
| 29 | 30 | 30 | unchanged |  |
| 30 | 30 | 30 | unchanged |  |
| 31 | 4 | 4 | unchanged |  |
| 32 | 30 | 30 | unchanged |  |
| 33 | 42 | 42 | unchanged |  |
| 34 | 42 | 24 | RESCUE_to_40 | TRUE |
| 35 | 28 | 28 | unchanged |  |
| 36 | 37 | 37 | unchanged |  |
| 37 | 37 | 39 | unchanged | TRUE |
| 38 | 1 | 1 | DISABLE | TRUE |
| 39 | 1 | 1 | DISABLE | TRUE |
| 40 | 1 | 1 | DISABLE | TRUE |
| 41 | 31 | 31 | unchanged |  |
| 42 | 6 | 6 | DISABLE | TRUE |
| 43 | 53 | 53 | unchanged |  |
| 44 | 53 | 54 | unchanged | TRUE |
| 45 | 45 | 45 | unchanged |  |
| 46 | 45 | 45 | unchanged |  |
| 47 | 17 | 17 | unchanged |  |
| 48 | 8 | 1 | DISABLE | TRUE |
| 49 | 8 | 8 | unchanged |  |
| 50 | HOLD | HOLD | unchanged |  |
| 51 | 38 | 36 | unchanged | TRUE |
| 52 | 38 | 38 | unchanged |  |
| 53 | 1 | 1 | DISABLE | TRUE |
| 54 | 1 | 3 | DEEPEN_to_3 | TRUE |
| 55 | HOLD | HOLD | unchanged |  |
| 56 | HOLD | 33 | unchanged | TRUE |
| 57 | 1 | 1 | unchanged |  |
| 58 | 19 | 19 | unchanged |  |
| 59 | 40 | 40 | unchanged |  |
| 60 | 34 | 20 | RESCUE_to_20 | TRUE |
| 61 | 34 | 34 | unchanged |  |
| 62 | 9 | 9 | unchanged |  |
| 63 | 36 | 36 | unchanged |  |
| 64 | 36 | 10 | unchanged | TRUE |
| 65 | 1 | 1 | DISABLE | TRUE |
| 66 | 32 | 32 | unchanged |  |
| 67 | 3 | 1 | DISABLE | TRUE |
| 68 | 3 | 3 | DISABLE | TRUE |
| 69 | 29 | 29 | unchanged |  |
| 70 | 17 | 17 | unchanged |  |
| 71 | 26 | 26 | unchanged |  |
| 72 | 1 | 1 | unchanged |  |
| 73 | 4 | 4 | DISABLE | TRUE |
| 74 | 14 | 14 | unchanged |  |
| 75 | 1 | 7 | DEEPEN_to_7 | TRUE |
| 76 | 1 | 5 | DEEPEN_to_5 | TRUE |
| 77 | 1 | 1 | DISABLE | TRUE |
| 78 | 14 | 14 | unchanged |  |
| 79 | 19 | 19 | unchanged |  |
| 80 | 1 | 5 | DISABLE | TRUE |
| 81 | 1 | 1 | DISABLE | TRUE |
| 82 | 6 | 6 | DISABLE | TRUE |
| 83 | 13 | 14 | unchanged | TRUE |
| 84 | 13 | 15 | RESCUE_to_15 | TRUE |
| 85 | 13 | 13 | unchanged |  |
| 86 | 13 | 13 | unchanged |  |
| 87 | 10 | 10 | unchanged |  |
| 88 | 10 | 11 | unchanged | TRUE |
| 89 | 10 | 8 | unchanged | TRUE |
| 90 | 10 | HOLD | unchanged | TRUE |
| 91 | 4 | 4 | unchanged |  |
| 92 | 4 | 4 | unchanged |  |
| 93 | 4 | 1 | DISABLE | TRUE |
| 94 | 4 | 5 | DEEPEN_to_5 | TRUE |

**ATP_MAIN counts:** live==v5_proposed: **63** | live≠v5_proposed: **27** | live still trading a DISABLE-flagged cell: **15** | live X = +1c: **14**

## WTA_MAIN

| cell_id | currently_live_X | v5_singleR_proposed_X | targeted_sweep_action | mismatch |
|---|---|---|---|---|
| 5 | 74 | 74 | unchanged |  |
| 6 | 74 | HOLD | unchanged | TRUE |
| 7 | 29 | 27 | unchanged | TRUE |
| 8 | 29 | 29 | unchanged |  |
| 9 | 15 | 15 | unchanged |  |
| 10 | 79 | 79 | unchanged |  |
| 11 | 7 | 7 | unchanged |  |
| 12 | HOLD | HOLD | unchanged |  |
| 13 | HOLD | 12 | unchanged | TRUE |
| 14 | 46 | 46 | unchanged |  |
| 15 | 46 | 84 | RESCUE_to_25 | TRUE |
| 16 | 46 | 47 | unchanged | TRUE |
| 17 | 81 | 81 | unchanged |  |
| 18 | 81 | 81 | unchanged |  |
| 19 | 81 | 37 | unchanged | TRUE |
| 20 | 32 | 32 | unchanged |  |
| 21 | 43 | 43 | unchanged |  |
| 22 | 43 | 46 | unchanged | TRUE |
| 23 | 35 | 35 | DISABLE | TRUE |
| 24 | 54 | 54 | unchanged |  |
| 25 | 16 | 16 | unchanged |  |
| 26 | HOLD | HOLD | unchanged |  |
| 27 | HOLD | HOLD | unchanged |  |
| 28 | 45 | 45 | unchanged |  |
| 29 | 53 | 53 | unchanged |  |
| 30 | 69 | 69 | unchanged |  |
| 31 | 17 | 17 | unchanged |  |
| 32 | 32 | 32 | unchanged |  |
| 33 | HOLD | HOLD | unchanged |  |
| 34 | HOLD | 14 | unchanged | TRUE |
| 35 | HOLD | HOLD | unchanged |  |
| 36 | 1 | 3 | unchanged | TRUE |
| 37 | 1 | 1 | DISABLE | TRUE |
| 38 | 37 | 37 | unchanged |  |
| 39 | 37 | 23 | unchanged | TRUE |
| 40 | 59 | 59 | unchanged |  |
| 41 | 36 | 36 | unchanged |  |
| 42 | 57 | 57 | unchanged |  |
| 43 | 53 | 53 | unchanged |  |
| 44 | 53 | HOLD | unchanged | TRUE |
| 45 | 43 | 43 | unchanged |  |
| 46 | HOLD | HOLD | unchanged |  |
| 47 | 49 | 50 | unchanged | TRUE |
| 48 | 49 | 45 | unchanged | TRUE |
| 49 | 49 | 49 | unchanged |  |
| 50 | 45 | 45 | DISABLE | TRUE |
| 51 | 45 | 46 | unchanged | TRUE |
| 52 | 32 | 34 | unchanged | TRUE |
| 53 | 32 | 32 | DISABLE | TRUE |
| 54 | 11 | 11 | DISABLE | TRUE |
| 55 | 29 | 29 | unchanged |  |
| 56 | 4 | 4 | unchanged |  |
| 57 | 31 | 31 | unchanged |  |
| 58 | 37 | 37 | unchanged |  |
| 59 | 4 | 4 | DISABLE | TRUE |
| 60 | 38 | HOLD | unchanged | TRUE |
| 61 | 38 | 38 | unchanged |  |
| 62 | 35 | 35 | unchanged |  |
| 63 | 35 | 36 | unchanged | TRUE |
| 64 | 35 | 31 | unchanged | TRUE |
| 65 | 35 | HOLD | unchanged | TRUE |
| 66 | 19 | 19 | unchanged |  |
| 67 | 11 | 11 | unchanged |  |
| 68 | 3 | 3 | unchanged |  |
| 69 | 3 | 19 | DISABLE | TRUE |
| 70 | 22 | 22 | unchanged |  |
| 71 | 22 | 28 | unchanged | TRUE |
| 72 | 1 | 6 | DISABLE | TRUE |
| 73 | 1 | 1 | DISABLE | TRUE |
| 74 | 23 | 23 | unchanged |  |
| 75 | 1 | 1 | DISABLE | TRUE |
| 76 | 15 | 15 | unchanged |  |
| 77 | 22 | 22 | unchanged |  |
| 78 | 18 | 18 | unchanged |  |
| 79 | 7 | 3 | DISABLE | TRUE |
| 80 | 7 | 11 | unchanged | TRUE |
| 81 | 7 | 7 | unchanged |  |
| 82 | 17 | 17 | unchanged |  |
| 83 | 6 | 7 | DISABLE | TRUE |
| 84 | 6 | 6 | DISABLE | TRUE |
| 85 | 13 | 13 | unchanged |  |
| 86 | 3 | 3 | unchanged |  |
| 87 | 3 | 2 | unchanged | TRUE |
| 88 | 3 | 10 | DISABLE | TRUE |
| 89 | 3 | 3 | unchanged |  |
| 90 | 7 | 7 | DISABLE | TRUE |
| 91 | 7 | 8 | unchanged | TRUE |
| 92 | 1 | 1 | unchanged |  |
| 93 | 1 | 1 | unchanged |  |
| 94 | 5 | 5 | unchanged |  |

**WTA_MAIN counts:** live==v5_proposed: **62** | live≠v5_proposed: **28** | live still trading a DISABLE-flagged cell: **15** | live X = +1c: **7**

## ATP_CHALL

| cell_id | currently_live_X | v5_singleR_proposed_X | targeted_sweep_action | mismatch |
|---|---|---|---|---|
| 5 | 7 | 10 | unchanged | TRUE |
| 6 | 7 | 58 | unchanged | TRUE |
| 7 | 7 | 25 | unchanged | TRUE |
| 8 | 7 | 7 | unchanged |  |
| 9 | 64 | 64 | unchanged |  |
| 10 | 27 | 27 | unchanged |  |
| 11 | 27 | 29 | unchanged | TRUE |
| 12 | 78 | 78 | unchanged |  |
| 13 | 49 | 67 | unchanged | TRUE |
| 14 | 49 | 49 | unchanged |  |
| 15 | 41 | 41 | unchanged |  |
| 16 | 14 | 14 | unchanged |  |
| 17 | 37 | 37 | unchanged |  |
| 18 | 72 | 72 | unchanged |  |
| 19 | HOLD | HOLD | unchanged |  |
| 20 | 32 | 32 | unchanged |  |
| 21 | 21 | 23 | unchanged | TRUE |
| 22 | 21 | 21 | unchanged |  |
| 23 | 46 | 46 | unchanged |  |
| 24 | 50 | 50 | unchanged |  |
| 25 | 24 | 24 | unchanged |  |
| 26 | 21 | 21 | unchanged |  |
| 27 | 59 | 59 | unchanged |  |
| 28 | 18 | 18 | unchanged |  |
| 29 | 66 | 60 | unchanged | TRUE |
| 30 | 66 | 66 | unchanged |  |
| 31 | 17 | 17 | unchanged |  |
| 32 | 8 | 2 | DISABLE | TRUE |
| 33 | 8 | 8 | DISABLE | TRUE |
| 34 | 49 | 49 | unchanged |  |
| 35 | 8 | 8 | unchanged |  |
| 36 | 43 | 60 | RESCUE_to_65 | TRUE |
| 37 | 43 | 43 | unchanged |  |
| 38 | 10 | 10 | unchanged |  |
| 39 | 10 | 12 | unchanged | TRUE |
| 40 | 59 | 59 | unchanged |  |
| 41 | 35 | 35 | unchanged |  |
| 42 | 52 | 52 | unchanged |  |
| 43 | 55 | HOLD | unchanged | TRUE |
| 44 | 55 | 55 | unchanged |  |
| 45 | 55 | 22 | unchanged | TRUE |
| 46 | 55 | 29 | unchanged | TRUE |
| 47 | 55 | 42 | unchanged | TRUE |
| 48 | 47 | 47 | unchanged |  |
| 49 | 18 | 18 | unchanged |  |
| 50 | 15 | 15 | unchanged |  |
| 51 | 33 | 33 | unchanged |  |
| 52 | 33 | 26 | unchanged | TRUE |
| 53 | HOLD | HOLD | unchanged |  |
| 54 | 1 | 1 | DISABLE | TRUE |
| 55 | 12 | 12 | unchanged |  |
| 56 | 12 | 13 | unchanged | TRUE |
| 57 | 12 | 12 | unchanged |  |
| 58 | 23 | 23 | unchanged |  |
| 59 | 18 | 18 | unchanged |  |
| 60 | 3 | 5 | DISABLE | TRUE |
| 61 | 3 | 3 | DISABLE | TRUE |
| 62 | 29 | 29 | unchanged |  |
| 63 | 12 | 12 | unchanged |  |
| 64 | 1 | 1 | DISABLE | TRUE |
| 65 | 1 | 1 | DISABLE | TRUE |
| 66 | 33 | 33 | unchanged |  |
| 67 | 12 | 12 | unchanged |  |
| 68 | 30 | 30 | unchanged |  |
| 69 | 25 | 25 | unchanged |  |
| 70 | HOLD | HOLD | unchanged |  |
| 71 | 27 | 27 | unchanged |  |
| 72 | 1 | 1 | DISABLE | TRUE |
| 73 | 12 | 12 | unchanged |  |
| 74 | HOLD | HOLD | unchanged |  |
| 75 | 14 | 14 | DISABLE | TRUE |
| 76 | HOLD | HOLD | unchanged |  |
| 77 | HOLD | 21 | unchanged | TRUE |
| 78 | 19 | 19 | unchanged |  |
| 79 | 5 | 5 | DISABLE | TRUE |
| 80 | 16 | 16 | DISABLE | TRUE |
| 81 | 5 | 1 | DISABLE | TRUE |
| 82 | 5 | 12 | DISABLE | TRUE |
| 83 | 5 | 5 | DISABLE | TRUE |
| 84 | 5 | 7 | unchanged | TRUE |
| 85 | HOLD | HOLD | DISABLE | TRUE |
| 86 | 4 | 4 | DISABLE | TRUE |
| 87 | 12 | 12 | DISABLE | TRUE |
| 88 | 1 | 1 | DISABLE | TRUE |
| 89 | 1 | 1 | DISABLE | TRUE |
| 90 | 1 | 1 | DISABLE | TRUE |
| 91 | 1 | 3 | DEEPEN_to_3 | TRUE |
| 92 | 1 | 4 | RESCUE_to_4 | TRUE |
| 93 | 1 | 6 | DISABLE | TRUE |
| 94 | 1 | 1 | DISABLE | TRUE |

**ATP_CHALL counts:** live==v5_proposed: **66** | live≠v5_proposed: **24** | live still trading a DISABLE-flagged cell: **22** | live X = +1c: **11**

## WTA_CHALL

| cell_id | currently_live_X | v5_singleR_proposed_X | targeted_sweep_action | mismatch |
|---|---|---|---|---|
| 5 | 62 | 8 | RESCUE_to_7 | TRUE |
| 6 | 62 | 62 | unchanged |  |
| 7 | 18 | 18 | unchanged |  |
| 8 | 7 | 7 | unchanged |  |
| 9 | HOLD | HOLD | unchanged |  |
| 10 | HOLD | HOLD | unchanged |  |
| 11 | HOLD | HOLD | unchanged |  |
| 12 | 67 | 67 | unchanged |  |
| 13 | 6 | 6 | unchanged |  |
| 14 | 83 | 83 | unchanged |  |
| 15 | 83 | HOLD | unchanged | TRUE |
| 16 | 16 | 17 | unchanged | TRUE |
| 17 | 16 | 4 | RESCUE_to_4 | TRUE |
| 18 | 16 | 11 | unchanged | TRUE |
| 19 | 16 | HOLD | DISABLE | TRUE |
| 20 | 16 | 72 | unchanged | TRUE |
| 21 | 16 | 16 | unchanged |  |
| 22 | 16 | 49 | unchanged | TRUE |
| 23 | 5 | 5 | DISABLE | TRUE |
| 24 | HOLD | HOLD | unchanged |  |
| 25 | HOLD | HOLD | unchanged |  |
| 26 | 1 | 1 | unchanged |  |
| 27 | 27 | 27 | unchanged |  |
| 28 | HOLD | HOLD | unchanged |  |
| 29 | HOLD | 61 | unchanged | TRUE |
| 30 | HOLD | HOLD | unchanged |  |
| 31 | 12 | 12 | unchanged |  |
| 32 | HOLD | HOLD | unchanged |  |
| 33 | 42 | 42 | unchanged |  |
| 34 | 1 | 1 | unchanged |  |
| 35 | 63 | HOLD | unchanged | TRUE |
| 36 | 63 | 63 | unchanged |  |
| 37 | 63 | HOLD | unchanged | TRUE |
| 38 | 3 | 3 | unchanged |  |
| 39 | 20 | 20 | unchanged |  |
| 40 | 48 | 48 | unchanged |  |
| 41 | 48 | 48 | unchanged |  |
| 42 | 57 | 57 | unchanged |  |
| 43 | 2 | 2 | DISABLE | TRUE |
| 44 | 2 | 49 | DISABLE | TRUE |
| 45 | HOLD | HOLD | unchanged |  |
| 46 | 19 | 19 | unchanged |  |
| 47 | 1 | 1 | unchanged |  |
| 48 | HOLD | HOLD | unchanged |  |
| 49 | HOLD | HOLD | unchanged |  |
| 50 | 20 | 20 | unchanged |  |
| 51 | 3 | 3 | unchanged |  |
| 52 | 20 | 20 | unchanged |  |
| 53 | 41 | HOLD | DISABLE | TRUE |
| 54 | 41 | 41 | unchanged |  |
| 55 | 20 | 20 | unchanged |  |
| 56 | 38 | 38 | unchanged |  |
| 57 | 11 | 11 | unchanged |  |
| 58 | 22 | 22 | unchanged |  |
| 59 | 1 | 1 | DISABLE | TRUE |
| 60 | 8 | 8 | unchanged |  |
| 61 | 4 | 4 | DISABLE | TRUE |
| 62 | HOLD | HOLD | DISABLE | TRUE |
| 63 | 12 | 12 | unchanged |  |
| 64 | HOLD | HOLD | unchanged |  |
| 65 | 8 | 8 | unchanged |  |
| 66 | 31 | 31 | unchanged |  |
| 67 | 4 | 5 | DISABLE | TRUE |
| 68 | 4 | 4 | unchanged |  |
| 69 | HOLD | 10 | unchanged | TRUE |
| 70 | HOLD | HOLD | DISABLE | TRUE |
| 71 | 5 | 8 | DEEPEN_to_7 | TRUE |
| 72 | 5 | 5 | DISABLE | TRUE |
| 73 | 5 | 14 | DEEPEN_to_7 | TRUE |
| 74 | 10 | 10 | unchanged |  |
| 75 | 20 | 20 | unchanged |  |
| 76 | 20 | HOLD | unchanged | TRUE |
| 77 | 20 | 21 | DISABLE | TRUE |
| 78 | 20 | 9 | DISABLE | TRUE |
| 79 | 20 | HOLD | unchanged | TRUE |
| 80 | 13 | 13 | unchanged |  |
| 81 | 13 | 18 | DEEPEN_to_15 | TRUE |
| 82 | 1 | 2 | DEEPEN_to_2 | TRUE |
| 83 | 1 | HOLD | DEEPEN_to_15 | TRUE |
| 84 | 1 | 1 | unchanged |  |
| 85 | 1 | 3 | DEEPEN_to_3 | TRUE |
| 86 | 11 | HOLD | unchanged | TRUE |
| 87 | 11 | HOLD | unchanged | TRUE |
| 88 | 11 | 11 | unchanged |  |
| 89 | 2 | 2 | unchanged |  |
| 90 | 2 | 2 | unchanged |  |
| 91 | HOLD | HOLD | DISABLE | TRUE |
| 92 | HOLD | HOLD | unchanged |  |
| 93 | 1 | 1 | DISABLE | TRUE |
| 94 | 5 | 5 | unchanged |  |

**WTA_CHALL counts:** live==v5_proposed: **63** | live≠v5_proposed: **27** | live still trading a DISABLE-flagged cell: **15** | live X = +1c: **9**

## Aggregate (all categories)

| category | cells | live==v5 | live≠v5 | trading-despite-DISABLE | live_X=+1c |
|---|---|---|---|---|---|
| ATP_MAIN | 90 | 63 | 27 | 15 | 14 |
| WTA_MAIN | 90 | 62 | 28 | 15 | 7 |
| ATP_CHALL | 90 | 66 | 24 | 22 | 11 |
| WTA_CHALL | 90 | 63 | 27 | 15 | 9 |
| **TOTAL** | 360 | **254** | **106** | **67** | **41** |

*Disk evidence only. Live bot on `adaptive_exit_bands.parquet` (unmodified). v5 + targeted artifacts staged/committed but not deployed.*