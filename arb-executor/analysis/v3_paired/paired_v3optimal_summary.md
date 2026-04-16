# V3 Paired Optimal Analysis

## Category Rollup

| Category | Scenario | N | Both_clip% | Combined_EV(c) | Combined_ROI% | Sharpe(EV/std) |
|---|---|---|---|---|---|---|
| ATP_CHALL | V3_OPTIMAL | 124 | 62.1% | +196.8 | +15.63% | 0.435 |
| ATP_CHALL | BASELINE_10C | 124 | 75.8% | +92.2 | +7.74% | 0.304 |
| ATP_CHALL | WORST_CASE | 124 | 3.2% | +68.0 | +4.88% | 0.359 |
| ATP_MAIN | V3_OPTIMAL | 53 | 69.8% | +192.8 | +16.15% | 0.551 |
| ATP_MAIN | BASELINE_10C | 53 | 69.8% | +51.8 | +5.27% | 0.140 |
| ATP_MAIN | WORST_CASE | 53 | 5.7% | +56.4 | +4.02% | 0.294 |
| WTA_MAIN | V3_OPTIMAL | 53 | 69.8% | +282.8 | +22.14% | 0.692 |
| WTA_MAIN | BASELINE_10C | 53 | 58.5% | +15.2 | +0.74% | 0.045 |
| WTA_MAIN | WORST_CASE | 53 | 3.8% | +85.6 | +6.07% | 0.424 |
| WTA_CHALL | V3_OPTIMAL | 3 | 33.3% | -26.7 | -0.11% | -0.050 |
| WTA_CHALL | BASELINE_10C | 3 | 66.7% | +30.0 | +2.28% | 0.079 |
| WTA_CHALL | WORST_CASE | 3 | 0.0% | +48.3 | +2.97% | 0.294 |

## Winners per Category

- **ATP_CHALL**: V3_OPTIMAL
- **ATP_MAIN**: V3_OPTIMAL
- **WTA_MAIN**: V3_OPTIMAL
- **WTA_CHALL**: WORST_CASE

## Marginal Contribution Ranking
Effect of reverting EACH cell from V3-optimal to +10c while keeping all others at V3-optimal.

| Cell | Cat | V3_exit | N | V3_EV(c) | Revert_EV(c) | Delta(c) | Verdict |
|---|---|---|---|---|---|---|---|
| WTA_MAIN_leader_55-59 | WTA_MAIN | +7c | 20 | +187.0 | -576.8 | +763.8 | KEEP |
| WTA_MAIN_underdog_40-44 | WTA_MAIN | +30c | 20 | +187.5 | -559.0 | +746.5 | KEEP |
| WTA_MAIN_leader_65-69 | WTA_MAIN | hold99 | 10 | +312.5 | -302.5 | +615.0 | KEEP |
| WTA_MAIN_leader_60-64 | WTA_MAIN | +7c | 8 | +372.5 | -189.4 | +561.9 | KEEP |
| ATP_CHALL_underdog_40-44 | ATP_CHALL | hold99 | 11 | -129.1 | -675.9 | +546.8 | KEEP |
| ATP_MAIN_leader_70-74 | ATP_MAIN | +19c | 7 | +177.9 | -295.7 | +473.6 | KEEP |
| ATP_MAIN_underdog_25-29 | ATP_MAIN | +21c | 7 | +327.9 | -81.4 | +409.3 | KEEP |
| ATP_MAIN_leader_65-69 | ATP_MAIN | +4c | 13 | +270.8 | -130.4 | +401.2 | KEEP |
| WTA_MAIN_underdog_30-34 | WTA_MAIN | +8c | 12 | +288.3 | -103.3 | +391.7 | KEEP |
| ATP_CHALL_underdog_25-29 | ATP_CHALL | +11c | 19 | +313.9 | -27.9 | +341.8 | KEEP |
| ATP_CHALL_leader_70-74 | ATP_CHALL | hold99 | 23 | +307.2 | +29.1 | +278.0 | KEEP |
| WTA_MAIN_leader_70-74 | WTA_MAIN | hold99 | 4 | +562.5 | +302.5 | +260.0 | KEEP |
| WTA_MAIN_underdog_35-39 | WTA_MAIN | +29c | 6 | +439.2 | +225.8 | +213.3 | KEEP |
| ATP_CHALL_leader_55-59 | ATP_CHALL | +21c | 28 | +159.1 | -43.4 | +202.5 | KEEP |
| ATP_MAIN_underdog_30-34 | ATP_MAIN | +26c | 15 | +164.3 | -23.7 | +188.0 | KEEP |
| WTA_MAIN_leader_75-79 | WTA_MAIN | +22c | 5 | +290.0 | +131.0 | +159.0 | KEEP |
| ATP_CHALL_leader_65-69 | ATP_CHALL | hold99 | 23 | +120.7 | -18.7 | +139.3 | KEEP |
| ATP_MAIN_leader_60-64 | ATP_MAIN | +5c | 18 | +81.1 | -56.9 | +138.1 | KEEP |
| ATP_MAIN_underdog_35-39 | ATP_MAIN | +24c | 17 | +129.7 | -4.1 | +133.8 | KEEP |
| ATP_CHALL_leader_80-84 | ATP_CHALL | +23c | 12 | +358.8 | +252.5 | +106.2 | KEEP |
| ATP_CHALL_underdog_10-14 | ATP_CHALL | +21c | 1 | +405.0 | +340.0 | +65.0 | KEEP |
| WTA_MAIN_leader_85-89 | WTA_MAIN | +14c | 1 | +510.0 | +450.0 | +60.0 | KEEP |
| WTA_MAIN_underdog_25-29 | WTA_MAIN | +21c | 4 | +562.5 | +510.0 | +52.5 | KEEP |
| WTA_MAIN_underdog_15-19 | WTA_MAIN | +20c | 6 | +240.8 | +199.2 | +41.7 | KEEP |
| ATP_MAIN_leader_55-59 | ATP_MAIN | +9c | 8 | +291.9 | +253.8 | +38.1 | KEEP |
| ATP_MAIN_underdog_40-44 | ATP_MAIN | +12c | 8 | +253.8 | +226.2 | +27.5 | KEEP |
| WTA_MAIN_leader_80-84 | WTA_MAIN | +28c | 5 | +187.0 | +176.0 | +11.0 | KEEP |
| ATP_MAIN_leader_75-79 | ATP_MAIN | +12c | 7 | +237.1 | +243.6 | -6.4 | CONSIDER_10C |
| ATP_MAIN_underdog_20-24 | ATP_MAIN | +21c | 6 | +204.2 | +229.2 | -25.0 | CONSIDER_10C |
| ATP_CHALL_leader_60-64 | ATP_CHALL | +27c | 25 | +115.6 | +142.6 | -27.0 | CONSIDER_10C |
| ATP_CHALL_underdog_15-19 | ATP_CHALL | +13c | 17 | +315.3 | +348.8 | -33.5 | CONSIDER_10C |
| ATP_CHALL_underdog_35-39 | ATP_CHALL | +11c | 39 | +197.4 | +245.0 | -47.6 | CONSIDER_10C |
| WTA_MAIN_underdog_20-24 | WTA_MAIN | +4c | 5 | +290.0 | +344.0 | -54.0 | CONSIDER_10C |
| ATP_CHALL_underdog_30-34 | ATP_CHALL | +7c | 24 | +130.8 | +229.2 | -98.3 | CONSIDER_10C |
| ATP_CHALL_leader_75-79 | ATP_CHALL | +13c | 13 | +224.2 | +361.5 | -137.3 | CONSIDER_10C |
| ATP_CHALL_underdog_20-24 | ATP_CHALL | +27c | 13 | +250.4 | +406.5 | -156.2 | CONSIDER_10C |
| WTA_CHALL_underdog_35-39 | WTA_CHALL | +30c | 3 | -26.7 | +313.3 | -340.0 | CONSIDER_10C |
| WTA_CHALL_leader_60-64 | WTA_CHALL | +14c | 3 | -26.7 | +566.7 | -593.3 | CONSIDER_10C |