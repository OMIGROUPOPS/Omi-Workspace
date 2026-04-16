# Cell-Level Drift Analysis

Drift = last_pregame_mid - cell_entry_mid
Pregame cutoff: 80% of ticker lifetime OR 5min before last tick, whichever is earlier.

## Step 1 — Cell-Level Drift Table

| Category | Side | Cell | N | Med_drift | Mean_drift | Stdev | %UP>+2 | %DN<-2 | %flat |
|---|---|---|---|---|---|---|---|---|---|
| ATP_CHALL | leader | 55-59 | 80 | -2.0c | -2.2c | 15.8c | 30% | 49% | 21% |
| ATP_CHALL | leader | 60-64 | 69 | +0.5c | -0.5c | 13.1c | 36% | 30% | 33% |
| ATP_CHALL | leader | 65-69 | 62 | +0.0c | -2.2c | 16.3c | 31% | 34% | 35% |
| ATP_CHALL | leader | 70-74 | 52 | +0.5c | -5.0c | 16.1c | 37% | 42% | 21% |
| ATP_CHALL | leader | 75-79 | 46 | +0.5c | -2.5c | 14.1c | 39% | 35% | 26% |
| ATP_CHALL | leader | 80-84 | 32 | +1.2c | -3.0c | 17.0c | 38% | 31% | 31% |
| ATP_CHALL | underdog | 10-14 | 27 | +5.0c | +14.3c | 17.9c | 59% | 7% | 33% |
| ATP_CHALL | underdog | 15-19 | 42 | -1.0c | +2.0c | 15.5c | 29% | 38% | 33% |
| ATP_CHALL | underdog | 20-24 | 53 | +1.5c | +6.0c | 17.6c | 45% | 30% | 25% |
| ATP_CHALL | underdog | 25-29 | 50 | -0.8c | +1.1c | 17.2c | 32% | 38% | 30% |
| ATP_CHALL | underdog | 30-34 | 71 | +2.0c | +2.2c | 18.0c | 49% | 37% | 14% |
| ATP_CHALL | underdog | 35-39 | 76 | +2.0c | +3.8c | 15.0c | 50% | 25% | 25% |
| ATP_CHALL | underdog | 40-44 | 76 | +2.8c | +2.3c | 14.8c | 51% | 28% | 21% |
| ATP_MAIN | leader | 55-59 | 30 | +1.2c | +0.6c | 11.2c | 40% | 17% | 43% |
| ATP_MAIN | leader | 60-64 | 44 | +0.2c | -1.7c | 10.5c | 30% | 39% | 32% |
| ATP_MAIN | leader | 65-69 | 30 | +0.0c | -0.5c | 10.3c | 30% | 27% | 43% |
| ATP_MAIN | leader | 70-74 | 23 | +2.0c | +1.6c | 8.8c | 48% | 13% | 39% |
| ATP_MAIN | leader | 75-79 | 14 | +1.2c | -2.9c | 16.6c | 29% | 14% | 57% |
| ATP_MAIN | underdog | 15-19 | 16 | +0.0c | +4.6c | 12.4c | 38% | 25% | 38% |
| ATP_MAIN | underdog | 20-24 | 15 | +0.0c | +1.5c | 7.4c | 13% | 20% | 67% |
| ATP_MAIN | underdog | 25-29 | 16 | +0.2c | -1.1c | 5.1c | 19% | 31% | 50% |
| ATP_MAIN | underdog | 30-34 | 22 | -0.2c | +1.8c | 11.3c | 32% | 32% | 36% |
| ATP_MAIN | underdog | 35-39 | 38 | +0.5c | +0.6c | 10.1c | 34% | 34% | 32% |
| ATP_MAIN | underdog | 40-44 | 32 | -1.0c | -0.6c | 8.9c | 22% | 28% | 50% |
| WTA_CHALL | leader | 60-64 | 7 | +0.5c | -0.9c | 5.2c | 14% | 14% | 71% |
| WTA_CHALL | leader | 85-89 | 4 | +8.8c | +6.1c | 6.1c | 75% | 25% | 0% |
| WTA_CHALL | underdog | 35-39 | 10 | +0.8c | +10.4c | 19.2c | 30% | 10% | 60% |
| WTA_CHALL | underdog | 40-44 | 20 | -0.8c | -1.8c | 12.9c | 20% | 40% | 40% |
| WTA_MAIN | leader | 55-59 | 28 | -0.5c | +0.4c | 9.0c | 32% | 39% | 29% |
| WTA_MAIN | leader | 60-64 | 17 | +0.0c | -1.6c | 5.4c | 18% | 24% | 59% |
| WTA_MAIN | leader | 65-69 | 19 | -0.5c | +0.5c | 10.7c | 26% | 21% | 53% |
| WTA_MAIN | leader | 70-74 | 22 | +0.2c | -3.1c | 9.1c | 27% | 23% | 50% |
| WTA_MAIN | leader | 75-79 | 15 | +0.0c | -3.1c | 13.2c | 20% | 20% | 60% |
| WTA_MAIN | leader | 80-84 | 9 | +0.5c | -2.4c | 11.1c | 33% | 11% | 56% |
| WTA_MAIN | leader | 85-89 | 9 | +1.5c | +1.2c | 3.5c | 44% | 22% | 33% |
| WTA_MAIN | underdog | 15-19 | 23 | +0.0c | +0.3c | 7.4c | 13% | 35% | 52% |
| WTA_MAIN | underdog | 20-24 | 12 | +0.2c | +3.9c | 11.4c | 33% | 25% | 42% |
| WTA_MAIN | underdog | 25-29 | 20 | +0.5c | +5.2c | 11.0c | 30% | 20% | 50% |
| WTA_MAIN | underdog | 30-34 | 19 | -1.0c | -1.6c | 9.5c | 21% | 37% | 42% |
| WTA_MAIN | underdog | 35-39 | 16 | +0.8c | +1.9c | 5.4c | 31% | 12% | 56% |
| WTA_MAIN | underdog | 40-44 | 39 | +0.5c | -0.2c | 9.1c | 38% | 31% | 31% |

## Step 2 — Drift Signal Strength Ranking

| Cell | N | Direction | Med | Mean | SNR(mean/std) | Classification |
|---|---|---|---|---|---|---|
| ATP_CHALL_underdog_10-14 | 27 | UP | +5.0c | +14.3c | 0.80 | STRONG_UP |
| WTA_CHALL_underdog_35-39 | 10 | UP | +0.8c | +10.4c | 0.54 | DIRECTIONAL |
| WTA_MAIN_underdog_25-29 | 20 | UP | +0.5c | +5.2c | 0.48 | DIRECTIONAL |
| ATP_MAIN_underdog_15-19 | 16 | UP | +0.0c | +4.6c | 0.37 | DIRECTIONAL |
| WTA_MAIN_underdog_35-39 | 16 | UP | +0.8c | +1.9c | 0.36 | DIRECTIONAL |
| WTA_MAIN_leader_85-89 | 9 | UP | +1.5c | +1.2c | 0.35 | DIRECTIONAL |
| WTA_MAIN_underdog_20-24 | 12 | UP | +0.2c | +3.9c | 0.34 | DIRECTIONAL |
| WTA_MAIN_leader_70-74 | 22 | DOWN | +0.2c | -3.1c | 0.34 | DIRECTIONAL |
| ATP_CHALL_underdog_20-24 | 53 | UP | +1.5c | +6.0c | 0.34 | DIRECTIONAL |
| ATP_CHALL_leader_70-74 | 52 | DOWN | +0.5c | -5.0c | 0.31 | DIRECTIONAL |
| WTA_MAIN_leader_60-64 | 17 | DOWN | +0.0c | -1.6c | 0.29 | FLAT/NOISY |
| ATP_CHALL_underdog_35-39 | 76 | UP | +2.0c | +3.8c | 0.26 | FLAT/NOISY |
| WTA_MAIN_leader_75-79 | 15 | DOWN | +0.0c | -3.1c | 0.24 | FLAT/NOISY |
| ATP_MAIN_underdog_25-29 | 16 | DOWN | +0.2c | -1.1c | 0.22 | FLAT/NOISY |
| WTA_MAIN_leader_80-84 | 9 | DOWN | +0.5c | -2.4c | 0.21 | FLAT/NOISY |
| ATP_MAIN_underdog_20-24 | 15 | UP | +0.0c | +1.5c | 0.20 | FLAT/NOISY |
| ATP_MAIN_leader_70-74 | 23 | UP | +2.0c | +1.6c | 0.19 | FLAT/NOISY |
| ATP_CHALL_leader_80-84 | 32 | DOWN | +1.2c | -3.0c | 0.18 | FLAT/NOISY |
| WTA_CHALL_leader_60-64 | 7 | DOWN | +0.5c | -0.9c | 0.18 | FLAT/NOISY |
| ATP_MAIN_leader_75-79 | 14 | DOWN | +1.2c | -2.9c | 0.17 | FLAT/NOISY |
| ATP_CHALL_leader_75-79 | 46 | DOWN | +0.5c | -2.5c | 0.17 | FLAT/NOISY |
| WTA_MAIN_underdog_30-34 | 19 | DOWN | -1.0c | -1.6c | 0.17 | FLAT/NOISY |
| ATP_MAIN_leader_60-64 | 44 | DOWN | +0.2c | -1.7c | 0.16 | FLAT/NOISY |
| ATP_MAIN_underdog_30-34 | 22 | UP | -0.2c | +1.8c | 0.16 | FLAT/NOISY |
| ATP_CHALL_underdog_40-44 | 76 | UP | +2.8c | +2.3c | 0.15 | STRONG_UP |
| WTA_CHALL_underdog_40-44 | 20 | DOWN | -0.8c | -1.8c | 0.14 | FLAT/NOISY |
| ATP_CHALL_leader_55-59 | 80 | DOWN | -2.0c | -2.2c | 0.14 | FLAT/NOISY |
| ATP_CHALL_leader_65-69 | 62 | DOWN | +0.0c | -2.2c | 0.13 | FLAT/NOISY |
| ATP_CHALL_underdog_15-19 | 42 | UP | -1.0c | +2.0c | 0.13 | FLAT/NOISY |
| ATP_CHALL_underdog_30-34 | 71 | UP | +2.0c | +2.2c | 0.12 | FLAT/NOISY |
| ATP_MAIN_underdog_40-44 | 32 | DOWN | -1.0c | -0.6c | 0.07 | FLAT/NOISY |
| ATP_CHALL_underdog_25-29 | 50 | UP | -0.8c | +1.1c | 0.06 | FLAT/NOISY |
| ATP_MAIN_underdog_35-39 | 38 | UP | +0.5c | +0.6c | 0.06 | FLAT/NOISY |
| ATP_MAIN_leader_55-59 | 30 | UP | +1.2c | +0.6c | 0.05 | FLAT/NOISY |
| ATP_MAIN_leader_65-69 | 30 | DOWN | +0.0c | -0.5c | 0.05 | FLAT/NOISY |
| WTA_MAIN_leader_55-59 | 28 | UP | -0.5c | +0.4c | 0.05 | FLAT/NOISY |
| WTA_MAIN_leader_65-69 | 19 | UP | -0.5c | +0.5c | 0.05 | FLAT/NOISY |
| WTA_MAIN_underdog_15-19 | 23 | UP | +0.0c | +0.3c | 0.04 | FLAT/NOISY |
| ATP_CHALL_leader_60-64 | 69 | DOWN | +0.5c | -0.5c | 0.04 | FLAT/NOISY |
| WTA_MAIN_underdog_40-44 | 39 | DOWN | +0.5c | -0.2c | 0.02 | FLAT/NOISY |

## Step 3 — Drift by Price Tier

| Tier | N | Median | Mean | Stdev | %UP | %DN | %flat |
|---|---|---|---|---|---|---|---|
| Heavy favorite (85-89 leaders) | 13 | +2.5c | +2.7c | 4.8c | 54% | 23% | 23% |
| Solid favorite (70-84 leaders) | 213 | +0.5c | -2.9c | 14.1c | 36% | 29% | 35% |
| Near-coinflip leader (55-69) | 386 | +0.0c | -1.1c | 12.9c | 31% | 34% | 35% |
| Near-coinflip underdog (35-44) | 307 | +0.5c | +1.8c | 13.0c | 40% | 28% | 32% |
| Solid underdog (20-34) | 278 | +0.0c | +2.5c | 15.2c | 36% | 32% | 31% |
| Deep underdog (10-19) | 108 | +0.0c | +5.1c | 15.2c | 34% | 28% | 38% |

## Step 4 — Cell Transit Analysis

For each ticker, track which cells its mid passes through during pregame.

| Cell | Start_count | End_count | Net_flow | Avg_dwell(min) | Sticky? |
|---|---|---|---|---|---|
| ATP_CHALL_leader_55-59 | 46 | 53 | +7 | 147 | YES |
| ATP_CHALL_leader_60-64 | 92 | 73 | -19 | 189 | YES |
| ATP_CHALL_leader_65-69 | 57 | 50 | -7 | 151 | YES |
| ATP_CHALL_leader_70-74 | 60 | 58 | -2 | 124 | YES |
| ATP_CHALL_leader_75-79 | 50 | 52 | +2 | 95 | YES |
| ATP_CHALL_leader_80-84 | 52 | 71 | +19 | 115 | YES |
| ATP_CHALL_underdog_10-14 | 24 | 37 | +13 | 139 | YES |
| ATP_CHALL_underdog_15-19 | 39 | 32 | -7 | 132 | YES |
| ATP_CHALL_underdog_20-24 | 38 | 20 | -18 | 147 | YES |
| ATP_CHALL_underdog_25-29 | 14 | 13 | -1 | 75 | YES |
| ATP_CHALL_underdog_30-34 | 1 | 5 | +4 | 22 | no |
| ATP_CHALL_underdog_35-39 | 1 | 7 | +6 | 16 | no |
| ATP_CHALL_underdog_40-44 | 2 | 5 | +3 | 13 | no |