# Spike volatility map -- cross-category

**DEPRECATED 2026-05-21 ET (Stage 0 Commit 7).** This file is the early-arc 2-of-4-category cross-comparison generated 2026-05-19 when only ATP_MAIN + WTA_MAIN had landed. The "Pending (not yet computed)" line below is stale — ATP_CHALL landed at commit `ec1f593` (2026-05-20) and WTA_CHALL at commit `d038cb3` (same day), completing the four-category atlas at HEAD `d99c6e9`.

**Canonical replacements:**
- Per-category methodology and headline numbers: the four LOCKED_DOWN.md files in this directory (ATP_MAIN_LOCKED_DOWN.md, WTA_MAIN_LOCKED_DOWN.md, ATP_CHALL_LOCKED_DOWN.md, WTA_CHALL_LOCKED_DOWN.md).
- Cross-category and pairing analysis: PAIRING_DIAGNOSTIC.md in this directory (event-level pairing rate 79.3%, per-category breakdown).
- Catalog-style cross-reference: SESSION_HANDOFF.md "Atlas headline" section (four-category headline table); ANALYSIS_LIBRARY.md Section 2 atlas entry (deliverable catalog) + Section 4 atlas finding entry (corpus-wide findings).
- Reproducibility: data/scripts/build_spike_perN.py at commit `c5e377f` reproduces all four spike per-N parquets byte-identical.

The body below is preserved as a 2-category historical snapshot from 2026-05-19. Do not consume it as the current cross-category reference.

---

# Spike volatility map -- cross-category

Generated: 2026-05-19T22:06:36.215107+00:00 (UTC), fresh from parquets in this directory.

## Completeness

- Present (this commit): ATP_MAIN, WTA_MAIN
- Pending (not yet computed): ATP_CHALL, WTA_CHALL

## Method (identical per category)

Per N, fresh tape-walk of `data/durable/g9_trades.parquet` over `[t20m_trade_ts, settlement_ts]` (no first_extreme_touch cutoff, no peak-walk). `size_qual_max_250` = highest price P at which cumulative `count_fp` at-that-price-or-higher >= 250. `spike_cents = (P - anchor_price) * 100`. `spike_pct = (P - anchor_price) / anchor_price * 100` (A39 descriptive scale, NOT a return). `truncation_delta_cents = spike_cents - old_metric_cents` where `old_metric_cents = peak_bid_bounce_pre_resolution * 100` (the stored, truncated metric). `settlement_value` is carried as the answer-key label only -- never a P&L input. No exit logic, no ROI-on-a-trade, no EV.

## ATP_MAIN

### ATP_MAIN -- Blast radius (n=4137)

| Δ category | count | share |
|---|---|---|
| truncation_delta_cents > 0 (old undercounted) | **3654** | **88.32%** |
| truncation_delta_cents == 0 | 307 | 7.42% |
| truncation_delta_cents < 0  | 176 | 4.25% |

truncation_delta_cents (cents): min=-24.000  p25=+1.000  p50=+2.000  p75=+4.000  p90=+10.000  max=+94.000  mean=+4.363

spike_cents (cents): min=-24.000  p25=+10.000  p50=+24.000  p75=+42.000  p90=+59.000  max=+94.000  mean=+27.950

### ATP_MAIN -- Volatility map by anchor-price band (size-qualified >=250ct)

| band | N | mean spike_cents | median spike_cents | mean spike_pct | median spike_pct |
|---|---|---|---|---|---|
| 0.05-0.10 | 113 | +23.204 | +8.000 | +322.820 | +125.000 |
| 0.10-0.15 | 129 | +23.992 | +13.000 | +198.181 | +108.333 |
| 0.15-0.20 | 171 | +31.246 | +18.000 | +181.718 | +110.526 |
| 0.20-0.25 | 177 | +35.158 | +25.000 | +160.366 | +108.696 |
| 0.25-0.30 | 239 | +35.841 | +28.000 | +132.747 | +106.897 |
| 0.30-0.35 | 253 | +34.451 | +31.000 | +108.070 | +100.000 |
| 0.35-0.40 | 315 | +33.451 | +32.000 | +90.903 | +89.744 |
| 0.40-0.45 | 296 | +34.986 | +40.000 | +83.521 | +96.477 |
| 0.45-0.50 | 277 | +34.217 | +45.000 | +73.268 | +97.917 |
| 0.50-0.55 | 234 | +32.380 | +45.000 | +62.429 | +83.333 |
| 0.55-0.60 | 318 | +31.528 | +40.000 | +55.285 | +67.797 |
| 0.60-0.65 | 335 | +28.445 | +36.000 | +45.853 | +57.143 |
| 0.65-0.70 | 307 | +24.805 | +31.000 | +37.159 | +45.588 |
| 0.70-0.75 | 272 | +21.893 | +26.000 | +30.414 | +35.616 |
| 0.75-0.80 | 238 | +19.445 | +22.000 | +25.335 | +28.571 |
| 0.80-0.85 | 205 | +14.590 | +16.000 | +17.819 | +19.277 |
| 0.85-0.90 | 141 | +11.340 | +12.000 | +13.093 | +13.793 |
| 0.90-0.95 | 117 | +6.598 | +7.000 | +7.193 | +7.609 |

(anchors outside 0.05-0.95: N=0)

## WTA_MAIN

### WTA_MAIN -- Blast radius (n=3683)

| Δ category | count | share |
|---|---|---|
| truncation_delta_cents > 0 (old undercounted) | **3212** | **87.21%** |
| truncation_delta_cents == 0 | 286 | 7.77% |
| truncation_delta_cents < 0  | 185 | 5.02% |

truncation_delta_cents (cents): min=-41.000  p25=+1.000  p50=+2.000  p75=+5.000  p90=+9.000  max=+91.000  mean=+4.362

spike_cents (cents): min=-41.000  p25=+10.000  p50=+25.000  p75=+42.000  p90=+60.000  max=+94.000  mean=+28.189

### WTA_MAIN -- Volatility map by anchor-price band (size-qualified >=250ct)

| band | N | mean spike_cents | median spike_cents | mean spike_pct | median spike_pct |
|---|---|---|---|---|---|
| 0.05-0.10 | 113 | +26.496 | +14.000 | +389.979 | +180.000 |
| 0.10-0.15 | 142 | +28.310 | +15.000 | +236.446 | +116.783 |
| 0.15-0.20 | 151 | +33.265 | +20.000 | +195.105 | +110.526 |
| 0.20-0.25 | 207 | +32.739 | +27.000 | +149.580 | +116.667 |
| 0.25-0.30 | 204 | +38.132 | +33.500 | +141.406 | +121.456 |
| 0.30-0.35 | 217 | +38.825 | +38.000 | +121.725 | +118.750 |
| 0.35-0.40 | 234 | +33.594 | +31.500 | +90.989 | +84.947 |
| 0.40-0.45 | 243 | +34.444 | +41.000 | +82.273 | +97.500 |
| 0.45-0.50 | 254 | +35.240 | +50.000 | +74.832 | +102.041 |
| 0.50-0.55 | 248 | +30.343 | +39.000 | +58.420 | +73.829 |
| 0.55-0.60 | 263 | +29.738 | +40.000 | +52.184 | +67.797 |
| 0.60-0.65 | 272 | +29.213 | +36.000 | +47.174 | +57.143 |
| 0.65-0.70 | 255 | +24.878 | +31.000 | +37.224 | +45.588 |
| 0.70-0.75 | 234 | +21.940 | +26.000 | +30.510 | +35.616 |
| 0.75-0.80 | 211 | +18.531 | +21.000 | +24.072 | +26.923 |
| 0.80-0.85 | 158 | +15.013 | +16.500 | +18.369 | +20.004 |
| 0.85-0.90 | 164 | +11.073 | +12.000 | +12.788 | +13.793 |
| 0.90-0.95 | 113 | +6.646 | +7.000 | +7.260 | +7.609 |

(anchors outside 0.05-0.95: N=0)

## Cross-category comparison -- median spike per band

| band | ATP_MAIN N | WTA_MAIN N | ATP_MAIN med spike_cents | WTA_MAIN med spike_cents | ATP_MAIN med spike_pct | WTA_MAIN med spike_pct |
|---|---|---|---|---|---|---|
| 0.05-0.10 | 113 | 113 | +8.000 | +14.000 | +125.000 | +180.000 |
| 0.10-0.15 | 129 | 142 | +13.000 | +15.000 | +108.333 | +116.783 |
| 0.15-0.20 | 171 | 151 | +18.000 | +20.000 | +110.526 | +110.526 |
| 0.20-0.25 | 177 | 207 | +25.000 | +27.000 | +108.696 | +116.667 |
| 0.25-0.30 | 239 | 204 | +28.000 | +33.500 | +106.897 | +121.456 |
| 0.30-0.35 | 253 | 217 | +31.000 | +38.000 | +100.000 | +118.750 |
| 0.35-0.40 | 315 | 234 | +32.000 | +31.500 | +89.744 | +84.947 |
| 0.40-0.45 | 296 | 243 | +40.000 | +41.000 | +96.477 | +97.500 |
| 0.45-0.50 | 277 | 254 | +45.000 | +50.000 | +97.917 | +102.041 |
| 0.50-0.55 | 234 | 248 | +45.000 | +39.000 | +83.333 | +73.829 |
| 0.55-0.60 | 318 | 263 | +40.000 | +40.000 | +67.797 | +67.797 |
| 0.60-0.65 | 335 | 272 | +36.000 | +36.000 | +57.143 | +57.143 |
| 0.65-0.70 | 307 | 255 | +31.000 | +31.000 | +45.588 | +45.588 |
| 0.70-0.75 | 272 | 234 | +26.000 | +26.000 | +35.616 | +35.616 |
| 0.75-0.80 | 238 | 211 | +22.000 | +21.000 | +28.571 | +26.923 |
| 0.80-0.85 | 205 | 158 | +16.000 | +16.500 | +19.277 | +20.004 |
| 0.85-0.90 | 141 | 164 | +12.000 | +12.000 | +13.793 | +13.793 |
| 0.90-0.95 | 117 | 113 | +7.000 | +7.000 | +7.609 | +7.609 |

(Per-N parquets in this directory carry every individual row -- 4137 ATP_MAIN, 3683 WTA_MAIN; see `*_spike_perN.parquet`.)

