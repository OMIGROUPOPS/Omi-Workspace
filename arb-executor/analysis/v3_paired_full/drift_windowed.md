# Windowed Drift Analysis

**Window A**: market_open → T-60min (pregame migration, bot does NOT enter)
**Window B**: T-60min → T-0 (bot entry window, ENTRY_BEFORE_START=3600s)

**Match start estimated as**: last_ts - category_duration (same proxy as prior analyses).
**Window B start**: match_start - 3600s. Matches bot gate_open = est_start - ENTRY_BEFORE_START.

## Task 1 - Drift in Each Window

| Cell | N_A | Med_A | Mean_A | SNR_A | N_B | Med_B | Mean_B | SNR_B |
|---|---|---|---|---|---|---|---|---|
| ATP_CHALL_leader_55-59 | 66 | +0.0c | -0.2c | 0.25 | 50 | +0.0c | -0.1c | 0.13 |
| ATP_CHALL_leader_60-64 | 55 | +0.0c | +0.0c | 0.02 | 42 | +0.0c | +0.1c | 0.12 |
| ATP_CHALL_leader_65-69 | 48 | +0.0c | +0.1c | 0.16 | 39 | +0.0c | -0.3c | 0.24 |
| ATP_CHALL_leader_70-74 | 38 | +0.0c | -0.1c | 0.09 | 28 | +0.0c | -0.4c | 0.34 |
| ATP_CHALL_leader_75-79 | 39 | +0.0c | -0.0c | 0.02 | 28 | +0.0c | -0.3c | 0.25 |
| ATP_CHALL_leader_80-84 | 25 | +0.0c | +0.1c | 0.11 | 18 | +0.0c | -0.1c | 0.15 |
| ATP_CHALL_underdog_10-14 | 24 | -0.5c | -0.4c | 0.37 | 16 | +0.0c | -0.2c | 0.22 |
| ATP_CHALL_underdog_15-19 | 34 | -1.0c | -0.9c | 0.99 | 32 | +0.0c | -0.1c | 0.06 |
| ATP_CHALL_underdog_20-24 | 43 | -0.5c | -0.7c | 0.79 | 36 | -0.5c | -0.4c | 0.29 |
| ATP_CHALL_underdog_25-29 | 42 | -0.5c | -0.6c | 0.77 | 29 | +0.0c | -0.1c | 0.11 |
| ATP_CHALL_underdog_30-34 | 58 | -0.5c | -0.8c | 0.83 | 46 | +0.0c | -0.3c | 0.30 |
| ATP_CHALL_underdog_35-39 | 70 | -0.5c | -0.5c | 0.61 | 58 | -0.5c | -0.5c | 0.50 |
| ATP_CHALL_underdog_40-44 | 66 | -0.2c | -0.4c | 0.49 | 47 | +0.0c | -0.2c | 0.19 |
| ATP_MAIN_leader_55-59 | 28 | +0.2c | +0.0c | 0.04 | 18 | +0.0c | -0.3c | 0.34 |
| ATP_MAIN_leader_60-64 | 40 | +0.2c | -0.1c | 0.08 | 24 | +0.0c | +0.3c | 0.20 |
| ATP_MAIN_leader_65-69 | 28 | +0.0c | -0.1c | 0.14 | 16 | +0.0c | -0.2c | 0.15 |
| ATP_MAIN_leader_70-74 | 22 | +0.2c | +0.2c | 0.18 | 11 | +0.0c | -0.4c | 0.66 |
| ATP_MAIN_leader_75-79 | 12 | +0.0c | +0.4c | 0.51 | 7 | +0.0c | -0.1c | 0.07 |
| ATP_MAIN_underdog_15-19 | 15 | -2.0c | -1.7c | 0.84 | 9 | +0.0c | -0.1c | 0.04 |
| ATP_MAIN_underdog_20-24 | 14 | -0.8c | -0.8c | 0.84 | 11 | +0.0c | -0.3c | 0.53 |
| ATP_MAIN_underdog_25-29 | 17 | -0.5c | -0.6c | 0.85 | 9 | -0.5c | -0.4c | 0.47 |
| ATP_MAIN_underdog_30-34 | 22 | -0.5c | -0.8c | 0.83 | 12 | +0.0c | -0.2c | 0.20 |
| ATP_MAIN_underdog_35-39 | 35 | -0.5c | -0.5c | 0.46 | 20 | +0.0c | +0.0c | 0.00 |
| ATP_MAIN_underdog_40-44 | 31 | -0.5c | -0.7c | 0.87 | 20 | +0.0c | -0.1c | 0.16 |
| WTA_CHALL_leader_60-64 | 5 | +0.0c | -0.3c | 0.31 | 4 | +0.0c | -0.1c | 0.09 |
| WTA_CHALL_leader_85-89 | 4 | +0.0c | -0.6c | 0.50 | 3 | +0.0c | -0.2c | 0.58 |
| WTA_CHALL_underdog_35-39 | 7 | +0.0c | -0.2c | 0.19 | 9 | +0.0c | -0.7c | 0.37 |
| WTA_CHALL_underdog_40-44 | 19 | -0.5c | -0.7c | 0.59 | 17 | +0.0c | +0.2c | 0.11 |
| WTA_MAIN_leader_55-59 | 24 | +0.0c | -0.2c | 0.35 | 8 | -0.8c | -0.4c | 0.24 |
| WTA_MAIN_leader_60-64 | 16 | +0.0c | -0.1c | 0.10 | 13 | -1.5c | -1.0c | 0.99 |
| WTA_MAIN_leader_65-69 | 19 | -0.5c | -0.3c | 0.30 | 12 | -0.2c | -0.3c | 0.24 |
| WTA_MAIN_leader_70-74 | 19 | +0.0c | -0.1c | 0.11 | 12 | -0.2c | -0.5c | 0.43 |
| WTA_MAIN_leader_75-79 | 14 | +0.0c | +0.2c | 0.37 | 9 | +0.0c | -0.2c | 0.21 |
| WTA_MAIN_leader_80-84 | 11 | +0.0c | -0.2c | 0.30 | 6 | +0.0c | -0.4c | 0.52 |
| WTA_MAIN_leader_85-89 | 9 | +0.0c | +0.1c | 0.07 | 5 | +0.5c | +0.8c | 0.88 |
| WTA_MAIN_underdog_15-19 | 23 | +0.0c | -0.4c | 0.18 | 16 | +0.0c | +0.3c | 0.13 |
| WTA_MAIN_underdog_20-24 | 10 | -0.2c | -0.3c | 0.33 | 8 | +0.0c | -0.2c | 0.33 |
| WTA_MAIN_underdog_25-29 | 21 | +0.0c | -0.6c | 0.63 | 13 | +0.0c | +0.1c | 0.13 |
| WTA_MAIN_underdog_30-34 | 18 | -0.2c | -0.4c | 0.48 | 13 | +0.0c | -0.1c | 0.13 |
| WTA_MAIN_underdog_35-39 | 16 | +0.0c | +0.1c | 0.09 | 10 | +0.0c | +0.2c | 0.22 |
| WTA_MAIN_underdog_40-44 | 37 | -0.5c | -0.7c | 0.38 | 19 | +0.0c | -0.3c | 0.14 |

## Task 2 - Fill Rate by Window

| Cell | Fill_A(%) | Fill_B(%) | Dwell_A(min) | Dwell_B(min) |
|---|---|---|---|---|
| ATP_CHALL_leader_55-59 | 67% | 52% | 159min | 6min |
| ATP_CHALL_leader_60-64 | 64% | 54% | 168min | 8min |
| ATP_CHALL_leader_65-69 | 50% | 49% | 129min | 6min |
| ATP_CHALL_leader_70-74 | 44% | 42% | 88min | 5min |
| ATP_CHALL_leader_75-79 | 58% | 50% | 94min | 6min |
| ATP_CHALL_leader_80-84 | 55% | 48% | 116min | 9min |
| ATP_CHALL_underdog_10-14 | 64% | 43% | 241min | 31min |
| ATP_CHALL_underdog_15-19 | 43% | 43% | 114min | 15min |
| ATP_CHALL_underdog_20-24 | 55% | 45% | 99min | 4min |
| ATP_CHALL_underdog_25-29 | 62% | 31% | 163min | 9min |
| ATP_CHALL_underdog_30-34 | 71% | 56% | 128min | 13min |
| ATP_CHALL_underdog_35-39 | 70% | 52% | 137min | 7min |
| ATP_CHALL_underdog_40-44 | 63% | 54% | 154min | 5min |
| ATP_MAIN_leader_55-59 | 69% | 44% | 309min | 8min |
| ATP_MAIN_leader_60-64 | 80% | 43% | 470min | 33min |
| ATP_MAIN_leader_65-69 | 79% | 39% | 368min | 7min |
| ATP_MAIN_leader_70-74 | 68% | 36% | 276min | 19min |
| ATP_MAIN_leader_75-79 | 85% | 46% | 219min | 7min |
| ATP_MAIN_underdog_15-19 | 63% | 26% | 692min | 46min |
| ATP_MAIN_underdog_20-24 | 81% | 44% | 298min | 14min |
| ATP_MAIN_underdog_25-29 | 79% | 42% | 255min | 4min |
| ATP_MAIN_underdog_30-34 | 85% | 31% | 217min | 12min |
| ATP_MAIN_underdog_35-39 | 81% | 30% | 330min | 12min |
| ATP_MAIN_underdog_40-44 | 85% | 50% | 387min | 5min |
| WTA_CHALL_leader_60-64 | 57% | 57% | 506min | 13min |
| WTA_CHALL_leader_85-89 | 25% | 50% | 16min | 3min |
| WTA_CHALL_underdog_35-39 | 20% | 50% | 179min | 14min |
| WTA_CHALL_underdog_40-44 | 50% | 60% | 318min | 25min |
| WTA_MAIN_leader_55-59 | 79% | 29% | 117min | 20min |
| WTA_MAIN_leader_60-64 | 64% | 55% | 241min | 5min |
| WTA_MAIN_leader_65-69 | 89% | 53% | 338min | 20min |
| WTA_MAIN_leader_70-74 | 54% | 46% | 290min | 14min |
| WTA_MAIN_leader_75-79 | 75% | 44% | 312min | 26min |
| WTA_MAIN_leader_80-84 | 69% | 46% | 117min | 6min |
| WTA_MAIN_leader_85-89 | 73% | 45% | 215min | 18min |
| WTA_MAIN_underdog_15-19 | 69% | 54% | 490min | 16min |
| WTA_MAIN_underdog_20-24 | 54% | 54% | 187min | 21min |
| WTA_MAIN_underdog_25-29 | 73% | 41% | 196min | 10min |
| WTA_MAIN_underdog_30-34 | 76% | 48% | 340min | 3min |
| WTA_MAIN_underdog_35-39 | 78% | 44% | 436min | 26min |
| WTA_MAIN_underdog_40-44 | 76% | 32% | 443min | 11min |

## Task 3 - Transit vs Sticky by Window

Transit = dwell < 15 min in cell during that window.

| Cell | Dwell_A(med) | Dwell_B(med) | Transit%_A | Transit%_B | Classification |
|---|---|---|---|---|---|
| ATP_CHALL_leader_55-59 | 159min | 6min | 20% | 74% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_leader_60-64 | 168min | 8min | 11% | 67% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_leader_65-69 | 129min | 6min | 17% | 69% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_leader_70-74 | 88min | 5min | 16% | 79% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_leader_75-79 | 94min | 6min | 23% | 64% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_leader_80-84 | 116min | 9min | 20% | 61% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_underdog_10-14 | 241min | 31min | 17% | 38% | STICKY_BOTH |
| ATP_CHALL_underdog_15-19 | 114min | 15min | 32% | 50% | STICKY_BOTH |
| ATP_CHALL_underdog_20-24 | 99min | 4min | 19% | 78% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_underdog_25-29 | 163min | 9min | 14% | 62% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_underdog_30-34 | 128min | 13min | 19% | 52% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_underdog_35-39 | 137min | 7min | 17% | 59% | MIGRATE_OUT (sticky A, transit B) |
| ATP_CHALL_underdog_40-44 | 154min | 5min | 6% | 66% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_leader_55-59 | 309min | 8min | 7% | 67% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_leader_60-64 | 470min | 33min | 5% | 33% | STICKY_BOTH |
| ATP_MAIN_leader_65-69 | 368min | 7min | 11% | 75% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_leader_70-74 | 276min | 19min | 5% | 45% | STICKY_BOTH |
| ATP_MAIN_leader_75-79 | 219min | 7min | 0% | 71% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_underdog_15-19 | 692min | 46min | 13% | 33% | STICKY_BOTH |
| ATP_MAIN_underdog_20-24 | 298min | 14min | 7% | 55% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_underdog_25-29 | 255min | 4min | 18% | 56% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_underdog_30-34 | 217min | 12min | 18% | 50% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_underdog_35-39 | 330min | 12min | 6% | 50% | MIGRATE_OUT (sticky A, transit B) |
| ATP_MAIN_underdog_40-44 | 387min | 5min | 0% | 65% | MIGRATE_OUT (sticky A, transit B) |
| WTA_CHALL_leader_60-64 | 506min | 13min | 0% | 50% | MIGRATE_OUT (sticky A, transit B) |
| WTA_CHALL_leader_85-89 | 16min | 3min | 50% | 67% | MIGRATE_OUT (sticky A, transit B) |
| WTA_CHALL_underdog_35-39 | 179min | 14min | 14% | 56% | MIGRATE_OUT (sticky A, transit B) |
| WTA_CHALL_underdog_40-44 | 318min | 25min | 0% | 35% | STICKY_BOTH |
| WTA_MAIN_leader_55-59 | 117min | 20min | 12% | 38% | STICKY_BOTH |
| WTA_MAIN_leader_60-64 | 241min | 5min | 19% | 62% | MIGRATE_OUT (sticky A, transit B) |
| WTA_MAIN_leader_65-69 | 338min | 20min | 5% | 42% | STICKY_BOTH |
| WTA_MAIN_leader_70-74 | 290min | 14min | 16% | 50% | MIGRATE_OUT (sticky A, transit B) |
| WTA_MAIN_leader_75-79 | 312min | 26min | 14% | 44% | STICKY_BOTH |
| WTA_MAIN_leader_80-84 | 117min | 6min | 9% | 67% | MIGRATE_OUT (sticky A, transit B) |
| WTA_MAIN_leader_85-89 | 215min | 18min | 0% | 40% | STICKY_BOTH |
| WTA_MAIN_underdog_15-19 | 490min | 16min | 0% | 50% | STICKY_BOTH |
| WTA_MAIN_underdog_20-24 | 187min | 21min | 10% | 38% | STICKY_BOTH |
| WTA_MAIN_underdog_25-29 | 196min | 10min | 14% | 69% | MIGRATE_OUT (sticky A, transit B) |
| WTA_MAIN_underdog_30-34 | 340min | 3min | 6% | 69% | MIGRATE_OUT (sticky A, transit B) |
| WTA_MAIN_underdog_35-39 | 436min | 26min | 0% | 30% | STICKY_BOTH |
| WTA_MAIN_underdog_40-44 | 443min | 11min | 3% | 58% | MIGRATE_OUT (sticky A, transit B) |