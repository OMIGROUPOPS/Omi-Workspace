# Fee-aware take census — score-free diagnostic

Raw receipt: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/fee_aware_take_census_20260801/FEE_AWARE_TAKE_CENSUS.json

The executable rule is fail-closed: `expected_close=NOT_BOUND`. The 5/516 value below is an ex-post actual-W1-close oracle screen, not a policy result or tradeable-population claim.

| Category | Ask-price-region pair | Frozen 516 denominator | Ex-post clears | Ex-post fails |
|---|---|---:|---:|---:|
| ATP_CHALL | 26_50+26_50 | 10 | 0 | 10 |
| ATP_CHALL | 26_50+51_75 | 162 | 0 | 162 |
| ATP_CHALL | 26_50+le25 | 1 | 1 | 0 |
| ATP_CHALL | 51_75+le25 | 9 | 1 | 8 |
| ATP_CHALL | ge75+le25 | 74 | 2 | 72 |
| ATP_MAIN | 26_50+26_50 | 6 | 1 | 5 |
| ATP_MAIN | 26_50+51_75 | 75 | 0 | 75 |
| ATP_MAIN | 51_75+le25 | 8 | 0 | 8 |
| ATP_MAIN | ge75+le25 | 18 | 0 | 18 |
| WTA_CHALL | 26_50+51_75 | 39 | 0 | 39 |
| WTA_CHALL | 51_75+le25 | 1 | 0 | 1 |
| WTA_CHALL | ge75+le25 | 18 | 0 | 18 |
| WTA_MAIN | 26_50+26_50 | 2 | 0 | 2 |
| WTA_MAIN | 26_50+51_75 | 52 | 0 | 52 |
| WTA_MAIN | 51_75+le25 | 8 | 0 | 8 |
| WTA_MAIN | ge75+le25 | 33 | 0 | 33 |

Fee law: `ceil(7 * 5 * price * (100-price) / 10000)` cents per leg. The comparison follows the operator-specified convention: pair price-edge cents versus total five-lot taker-fee cents.
