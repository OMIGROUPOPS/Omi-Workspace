# Drift timing — full discount-curve distributions (all 4 categories) — 2026-05-26

Read-only on staged `{cat}_drift_timing.parquet`. Per bucket, % of **all** category tickers whose bid dipped ≥Nc below anchor in that bucket (a ticker with no book in a bucket counts as no-dip). `dip = anchor − min_bid_in_bucket`. **Overall** = dipped ≥Nc in *any* bucket.

## ATP_MAIN  (N=4137 tickers)

| bucket | window | ≥1c | ≥2c | ≥3c | ≥4c | ≥5c | ≥6c | ≥8c | ≥10c | ≥15c | median dip |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | T-4h20m→T-3h20m | 67.7% | 52.7% | 37.6% | 27.6% | 21.3% | 17.8% | 13.9% | 12.1% | 9.4% | 2c |
| B2 | T-3h20m→T-2h20m | 71.3% | 54.6% | 38.4% | 28.1% | 21.5% | 18.2% | 14.9% | 13.2% | 10.5% | 2c |
| B3 | T-2h20m→T-1h20m | 76.7% | 59.1% | 40.9% | 30.0% | 23.7% | 20.6% | 17.3% | 15.5% | 12.7% | 2c |
| B4 | T-1h20m→T-20m | 96.2% | 77.3% | 53.6% | 39.5% | 33.5% | 29.6% | 25.7% | 22.9% | 18.6% | 3c |
| **ANY** | full window | **97.1%** | **84.0%** | **62.8%** | **47.4%** | **38.3%** | **33.2%** | **27.8%** | **24.8%** | **20.2%** | **3c** |

## WTA_MAIN  (N=3683 tickers)

| bucket | window | ≥1c | ≥2c | ≥3c | ≥4c | ≥5c | ≥6c | ≥8c | ≥10c | ≥15c | median dip |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | T-4h20m→T-3h20m | 67.8% | 53.8% | 39.6% | 29.9% | 24.1% | 20.9% | 17.1% | 14.9% | 10.9% | 2c |
| B2 | T-3h20m→T-2h20m | 70.4% | 55.5% | 40.8% | 30.8% | 24.7% | 21.5% | 17.9% | 15.5% | 11.9% | 2c |
| B3 | T-2h20m→T-1h20m | 75.7% | 60.2% | 43.6% | 33.0% | 27.5% | 24.5% | 21.1% | 18.7% | 15.2% | 2c |
| B4 | T-1h20m→T-20m | 95.8% | 78.5% | 57.9% | 45.2% | 39.1% | 35.5% | 31.3% | 28.0% | 22.5% | 3c |
| **ANY** | full window | **96.6%** | **84.8%** | **67.1%** | **52.3%** | **43.4%** | **38.4%** | **33.0%** | **29.6%** | **24.0%** | **4c** |

## ATP_CHALL  (N=5326 tickers)

| bucket | window | ≥1c | ≥2c | ≥3c | ≥4c | ≥5c | ≥6c | ≥8c | ≥10c | ≥15c | median dip |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | T-4h20m→T-3h20m | 67.2% | 58.1% | 48.1% | 37.2% | 29.5% | 24.4% | 18.2% | 14.4% | 10.1% | 3c |
| B2 | T-3h20m→T-2h20m | 69.3% | 59.6% | 48.2% | 36.6% | 28.3% | 23.8% | 18.1% | 14.5% | 9.9% | 2c |
| B3 | T-2h20m→T-1h20m | 73.0% | 62.4% | 49.9% | 37.9% | 29.4% | 24.5% | 19.1% | 15.7% | 11.3% | 3c |
| B4 | T-1h20m→T-20m | 94.0% | 83.9% | 68.9% | 53.2% | 42.8% | 37.6% | 30.4% | 25.6% | 18.7% | 4c |
| **ANY** | full window | **95.3%** | **88.0%** | **76.0%** | **61.7%** | **49.8%** | **42.8%** | **33.6%** | **27.7%** | **20.5%** | **4c** |

## WTA_CHALL  (N=887 tickers)

| bucket | window | ≥1c | ≥2c | ≥3c | ≥4c | ≥5c | ≥6c | ≥8c | ≥10c | ≥15c | median dip |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | T-4h20m→T-3h20m | 65.2% | 57.8% | 50.3% | 40.8% | 33.0% | 27.8% | 22.0% | 17.8% | 11.2% | 3c |
| B2 | T-3h20m→T-2h20m | 66.4% | 58.9% | 49.4% | 40.0% | 31.6% | 26.5% | 20.7% | 17.4% | 10.7% | 3c |
| B3 | T-2h20m→T-1h20m | 69.6% | 63.0% | 53.1% | 42.8% | 32.6% | 28.0% | 22.4% | 19.2% | 13.1% | 3c |
| B4 | T-1h20m→T-20m | 94.6% | 86.8% | 74.0% | 57.7% | 47.8% | 43.3% | 36.9% | 32.2% | 22.2% | 4c |
| **ANY** | full window | **95.5%** | **89.9%** | **80.2%** | **66.2%** | **55.9%** | **49.0%** | **39.9%** | **33.0%** | **23.0%** | **5c** |

## Cross-category comparison — shallower vs deeper dip profiles

Overall (any-bucket) % dipped ≥Nc, by category:

| category | N | ≥1c | ≥3c | ≥5c | ≥10c | ≥15c | median deepest dip |
|---|---|---|---|---|---|---|---|
| ATP_MAIN | 4137 | 97% | 63% | 38% | 25% | 20% | 3c |
| WTA_MAIN | 3683 | 97% | 67% | 43% | 30% | 24% | 4c |
| ATP_CHALL | 5326 | 95% | 76% | 50% | 28% | 20% | 4c |
| WTA_CHALL | 887 | 95% | 80% | 56% | 33% | 23% | 5c |

### Structural differences
- **Deeper dip profiles: challengers.** Ranked by overall %≥5c: WTA_CHALL(56%) > ATP_CHALL(50%) > WTA_MAIN(43%) > ATP_MAIN(38%).
- **Deepest: WTA_CHALL** (median deepest dip 5c, 33% dip ≥10c); **shallowest: ATP_MAIN** (25% dip ≥10c).
- **Main draws (ATP_MAIN, WTA_MAIN)** are tighter/more liquid premarket — smaller dips; **challengers (ATP_CHALL, WTA_CHALL)** dip deeper and more often (thinner books, wider premarket swings). This means discount-entry capture is structurally larger in challengers.
- The late-bucket (B4) skew holds in all four: dips concentrate in the final hour before T-20m (see per-bucket tables).

*Read-only on staged drift_timing parquets. No new parquet produced.*