# Drift envelope analysis — ATP_MAIN premarket [T-4h20m, T-20m] — 2026-05-26

Read-only. For each ATP_MAIN ticker in `atp_main_spike_perN.parquet`, g9_candles in the window **[anchor_ts − 4h, anchor_ts]** (anchor_ts = T-20m). Bid/ask from g9 (dollars → cents). mid = (yes_bid_close + yes_ask_close)/2.

- **Coverage: 4137/4137 tickers** have candle data in the window (100%).
- Output: `data/durable/spike_volatility_map/atp_main_drift_envelope.parquet` (per-ticker).

## 1. Drift envelope width (max_bid − min_bid)

| width | tickers |
|---|---|
| ≤1c | 701 (16.9%) |
| 2–3c | 1331 (32.2%) |
| 4–5c | 474 (11.5%) |
| 6+c | 1631 (39.4%) |

median **4c**, mean 13.4c, p90 42c, max 98c.

## 2. drift_low_vs_anchor = anchor − min_bid (how far below anchor the bid traded — where we could have filled cheaper)

| dip below anchor | tickers |
|---|---|
| ≤0c (never below anchor) | 121 (2.9%) |
| 1–2c | 1418 (34.3%) |
| 3–5c | 1225 (29.6%) |
| 6–10c | 399 (9.6%) |
| 11+c | 974 (23.5%) |

median dip **3c** below anchor; mean 10.1c. (Positive = the resting bid could have filled below anchor during premarket.)

## 3. Time-weighted avg mid vs anchor (tw_avg_mid − anchor)

| tw_avg vs anchor | tickers |
|---|---|
| below anchor (< −1c) | 1830 (44.2%) |
| ≈ anchor (−1..+1c) | 1397 (33.8%) |
| above anchor (> +1c) | 910 (22.0%) |

median tw_avg − anchor = **-0.7c**, mean -1.0c. (Negative ⇒ premarket time-weighted price sat below the T-20m anchor on average.)

## 4. Per anchor cell — price range actually visited in premarket

For each anchor cell (entry price), across its tickers: median envelope, the aggregate bid range visited [min of min_bid, max of max_bid], and median dip/rise vs anchor.

| anchor_cell | n | med envelope | visited bid range | med dip (anchor−minbid) | med rise (maxbid−anchor) |
|---|---|---|---|---|---|
| 5 | 21 | 13c | [0, 56] | 2c | 10c |
| 6 | 25 | 4c | [1, 82] | 2c | 1c |
| 7 | 26 | 4c | [0, 80] | 2c | 2c |
| 8 | 18 | 3c | [0, 44] | 3c | 0c |
| 9 | 23 | 10c | [0, 42] | 3c | 7c |
| 10 | 31 | 14c | [1, 56] | 3c | 9c |
| 11 | 28 | 20c | [0, 85] | 2c | 16c |
| 12 | 21 | 13c | [3, 71] | 5c | 4c |
| 13 | 23 | 18c | [2, 66] | 2c | 11c |
| 14 | 26 | 10c | [0, 51] | 2c | 6c |
| 15 | 24 | 18c | [0, 44] | 5c | 10c |
| 16 | 40 | 13c | [0, 56] | 3c | 2c |
| 17 | 40 | 18c | [0, 46] | 6c | 6c |
| 18 | 37 | 3c | [0, 68] | 2c | 1c |
| 19 | 30 | 2c | [1, 54] | 3c | 0c |
| 20 | 35 | 12c | [0, 67] | 3c | 5c |
| 21 | 33 | 3c | [2, 70] | 3c | 1c |
| 22 | 38 | 3c | [0, 60] | 2c | 1c |
| 23 | 37 | 3c | [8, 56] | 2c | 1c |
| 24 | 34 | 6c | [0, 90] | 4c | 0c |
| 25 | 49 | 3c | [1, 67] | 3c | 1c |
| 26 | 52 | 3c | [0, 64] | 2c | 1c |
| 27 | 35 | 3c | [0, 56] | 3c | 1c |
| 28 | 51 | 2c | [0, 70] | 2c | 0c |
| 29 | 52 | 4c | [5, 82] | 3c | 1c |
| 30 | 59 | 3c | [3, 80] | 3c | 0c |
| 31 | 43 | 5c | [0, 78] | 3c | 2c |
| 32 | 57 | 3c | [1, 63] | 2c | 0c |
| 33 | 41 | 3c | [7, 87] | 2c | 0c |
| 34 | 53 | 6c | [0, 80] | 3c | 1c |
| 35 | 69 | 3c | [4, 80] | 2c | 0c |
| 36 | 62 | 4c | [0, 81] | 3c | 0c |
| 37 | 55 | 3c | [5, 82] | 2c | 0c |
| 38 | 64 | 3c | [0, 68] | 3c | 0c |
| 39 | 65 | 5c | [7, 83] | 3c | 0c |
| 40 | 63 | 4c | [6, 79] | 3c | 1c |
| 41 | 64 | 3c | [0, 80] | 3c | 0c |
| 42 | 62 | 4c | [0, 86] | 3c | 0c |
| 43 | 50 | 3c | [4, 72] | 3c | 0c |
| 44 | 57 | 3c | [0, 85] | 3c | 0c |
| 45 | 61 | 3c | [1, 73] | 3c | 1c |
| 46 | 65 | 3c | [4, 87] | 3c | 0c |
| 47 | 59 | 4c | [0, 87] | 4c | 0c |
| 48 | 51 | 4c | [0, 76] | 4c | 0c |
| 49 | 41 | 3c | [1, 79] | 3c | 0c |
| 50 | 53 | 6c | [0, 82] | 4c | 1c |
| 51 | 35 | 4c | [2, 88] | 4c | 0c |
| 52 | 49 | 4c | [2, 90] | 4c | 1c |
| 53 | 49 | 3c | [0, 90] | 3c | 1c |
| 54 | 48 | 4c | [2, 85] | 3c | 1c |
| 55 | 48 | 3c | [1, 81] | 3c | 0c |
| 56 | 78 | 4c | [0, 97] | 4c | 0c |
| 57 | 61 | 3c | [5, 90] | 4c | 0c |
| 58 | 65 | 4c | [0, 87] | 3c | 0c |
| 59 | 66 | 3c | [4, 87] | 3c | 0c |
| 60 | 57 | 3c | [0, 68] | 3c | 0c |
| 61 | 68 | 4c | [1, 82] | 3c | 0c |
| 62 | 66 | 3c | [0, 98] | 4c | -1c |
| 63 | 73 | 4c | [4, 96] | 4c | 0c |
| 64 | 71 | 3c | [0, 83] | 3c | -1c |
| 65 | 79 | 4c | [0, 93] | 4c | 0c |
| 66 | 57 | 3c | [0, 74] | 3c | 0c |
| 67 | 64 | 4c | [6, 96] | 4c | -0c |
| 68 | 59 | 3c | [5, 78] | 4c | 0c |
| 69 | 48 | 3c | [2, 95] | 4c | -1c |
| 70 | 48 | 6c | [0, 92] | 4c | -1c |
| 71 | 56 | 3c | [14, 90] | 3c | -1c |
| 72 | 50 | 3c | [6, 96] | 4c | 0c |
| 73 | 59 | 3c | [6, 92] | 3c | -1c |
| 74 | 59 | 3c | [0, 98] | 4c | 0c |
| 75 | 52 | 4c | [0, 89] | 4c | 0c |
| 76 | 52 | 4c | [6, 94] | 4c | 0c |
| 77 | 54 | 6c | [1, 97] | 6c | -1c |
| 78 | 45 | 4c | [6, 91] | 4c | -1c |
| 79 | 35 | 3c | [6, 93] | 3c | -1c |
| 80 | 47 | 3c | [4, 94] | 3c | 0c |
| 81 | 36 | 5c | [6, 93] | 5c | -0c |
| 82 | 37 | 8c | [0, 97] | 5c | 0c |
| 83 | 42 | 4c | [6, 98] | 4c | 0c |
| 84 | 43 | 11c | [1, 99] | 5c | -1c |
| 85 | 32 | 22c | [0, 97] | 20c | 0c |
| 86 | 36 | 4c | [12, 93] | 4c | 0c |
| 87 | 25 | 16c | [2, 96] | 11c | 0c |
| 88 | 24 | 12c | [0, 98] | 8c | -0c |
| 89 | 24 | 22c | [24, 94] | 21c | 0c |
| 90 | 19 | 11c | [5, 96] | 11c | -1c |
| 91 | 29 | 16c | [6, 93] | 14c | -1c |
| 92 | 20 | 23c | [0, 99] | 22c | 0c |
| 93 | 28 | 12c | [0, 97] | 13c | -1c |
| 94 | 21 | 9c | [7, 95] | 9c | 0c |

*Read-only on g9_candles + spike_perN. Per-ticker parquet staged in spike_volatility_map/.*