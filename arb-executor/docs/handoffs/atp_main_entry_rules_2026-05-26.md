# ATP_MAIN optimal entry rule per cell band — 2026-05-26

Read-only, local. For each of 30 cell bands, swept entry **discount** ∈ {0,1,2,3,4,5,6,8,10,12,15}c below anchor × **post_start** ∈ {B1,B2,B3,B4} (bid rests to T-20m). Fill if the band ticker's min_bid in any bucket ≥ post_start ≤ post price; **fill price = our bid (anchor−discount)**. Exit = band's max-EV single-R at fill_price+R (hit via **raw_max**) else settle. Unfilled → **skip** ($0) or **taker fallback** (cross at anchor at T-20m, then exit at R).

## ⚠️ Read these caveats before using the uplift numbers
- **`raw_max` used for exit-hit (per task spec)** — this is the *unqualified* peak, more optimistic than the deployed `size_qual_max_250` (≥250-depth realizable) model. Real fills need depth; treat captures as an upper bound.
- **Per-band optima are IN-SAMPLE** (best of 44 combos chosen on the same 4137-ticker corpus) — overfit ceilings, not out-of-sample expectations.
- **Idealized maker fill** — assumes our resting bid fills whenever the observed min_bid touches it (no queue position, no partial fill).

## Headline (vs taker baseline)
- **Taker baseline** (enter all at anchor, apply band max-EV R): **$1,607.90** (operator ref ~$1,595; reconstructed within 0.8%).
- **Skip-scenario optimum:** **$2,182.90** — uplift **+575.00** (+35.8%). Only filled (discounted) names traded; rest skipped.
- **Fallback-scenario optimum:** **$2,465.40** — uplift **+857.50** (+53.3%). Filled at discount + unfilled crossed at anchor (full deployment).

## SKIP scenario — per band optimum

| band | N | exit_R | best discount | post_start | fill_rate | avg disc | skip $ | taker $ | uplift |
|---|---|---|---|---|---|---|---|---|---|
| 5-9 | 113 | 63 | 1c | B4 | 93% | 1.0c | 96.6 | 90.5 | +6.1 |
| 10-16 | 193 | 6 | 2c | B1 | 77% | 2.0c | 58.6 | 44.8 | +13.8 |
| 17-19 | 107 | 54 | 1c | B1 | 98% | 1.0c | 92.0 | 96.1 | -4.1 |
| 20-22 | 106 | 52 | 0c | B4 | 99% | 0.0c | 93.3 | 91.3 | +2.0 |
| 23-25 | 120 | 22 | 1c | B3 | 97% | 1.0c | 65.5 | 60.9 | +4.6 |
| 26-28 | 138 | 71 | 1c | B4 | 93% | 1.0c | 123.3 | 117.8 | +5.5 |
| 29-30 | 111 | 31 | 1c | B1 | 96% | 1.0c | 70.8 | 63.6 | +7.2 |
| 31-32 | 100 | 14 | 2c | B1 | 80% | 2.0c | 46.8 | 26.3 | +20.5 |
| 33-35 | 163 | 29 | 2c | B1 | 83% | 2.0c | 70.6 | 68.9 | +1.7 |
| 36-37 | 117 | 39 | 2c | B2 | 85% | 2.0c | 92.4 | 79.0 | +13.4 |
| 38-40 | 192 | 1 | 1c | B1 | 94% | 1.0c | 18.1 | -4.7 | +22.8 |
| 41-42 | 126 | 32 | 2c | B3 | 81% | 2.0c | 97.3 | 72.2 | +25.1 |
| 43-44 | 107 | 54 | 2c | B4 | 84% | 2.0c | 46.5 | 41.3 | +5.2 |
| 45-46 | 126 | 48 | 0c | B4 | 98% | 0.0c | 118.3 | 118.6 | -0.3 |
| 47-48 | 110 | 11 | 12c | B1 | 29% | 12.0c | 35.2 | 9.9 | +25.3 |
| 49-51 | 129 | 50 | 3c | B3 | 65% | 3.0c | 119.7 | 93.3 | +26.4 |
| 52-54 | 146 | 11 | 12c | B1 | 25% | 12.0c | 40.7 | 19.9 | +20.8 |
| 55-56 | 126 | HOLD | 2c | B2 | 86% | 2.0c | 110.9 | 69.2 | +41.7 |
| 57-58 | 126 | 18 | 15c | B1 | 18% | 15.0c | 35.4 | 8.0 | +27.4 |
| 59-61 | 191 | 35 | 2c | B1 | 85% | 2.0c | 157.6 | 117.2 | +40.4 |
| 62-64 | 210 | 12 | 2c | B1 | 86% | 2.0c | 91.5 | 71.8 | +19.7 |
| 65-66 | 136 | 33 | 3c | B3 | 61% | 3.0c | 92.9 | 16.2 | +76.7 |
| 67-68 | 123 | 2 | 2c | B1 | 88% | 2.0c | 21.6 | -3.2 | +24.8 |
| 69-71 | 152 | HOLD | 3c | B1 | 70% | 3.0c | 89.5 | 55.2 | +34.3 |
| 72-74 | 168 | 2 | 2c | B2 | 90% | 2.0c | 30.4 | 18.6 | +11.8 |
| 75-76 | 104 | 8 | 3c | B1 | 74% | 3.0c | 53.5 | 33.1 | +20.4 |
| 77-79 | 134 | 14 | 15c | B1 | 35% | 15.0c | 65.8 | 40.9 | +24.9 |
| 80-82 | 120 | 1 | 1c | B1 | 99% | 1.0c | 11.9 | -4.6 | +16.5 |
| 83-86 | 153 | 15 | 15c | B1 | 43% | 15.0c | 99.0 | 67.3 | +31.7 |
| 87-94 | 190 | 2 | 1c | B1 | 98% | 1.0c | 37.2 | 28.5 | +8.7 |
| **TOTAL** | | | | | | | **2182.9** | **1607.9** | **+575.0** |

## FALLBACK scenario — per band optimum

| band | N | exit_R | best discount | post_start | fill_rate | fallback $ | taker $ | uplift | ROI on total cap |
|---|---|---|---|---|---|---|---|---|---|
| 5-9 | 113 | 63 | 3c | B1 | 49% | 109.6 | 90.5 | +19.1 | 175.923% |
| 10-16 | 193 | 6 | 4c | B1 | 47% | 66.2 | 44.8 | +21.4 | 30.465% |
| 17-19 | 107 | 54 | 8c | B4 | 30% | 112.1 | 96.1 | +16.0 | 67.53% |
| 20-22 | 106 | 52 | 10c | B1 | 22% | 110.7 | 91.3 | +19.4 | 55.378% |
| 23-25 | 120 | 22 | 3c | B1 | 55% | 77.4 | 60.9 | +16.5 | 28.731% |
| 26-28 | 138 | 71 | 15c | B1 | 12% | 141.0 | 117.8 | +23.2 | 40.634% |
| 29-30 | 111 | 31 | 12c | B3 | 24% | 97.3 | 63.6 | +33.7 | 32.938% |
| 31-32 | 100 | 14 | 8c | B1 | 20% | 40.6 | 26.3 | +14.3 | 13.547% |
| 33-35 | 163 | 29 | 15c | B1 | 17% | 106.5 | 68.9 | +37.6 | 20.68% |
| 36-37 | 117 | 39 | 12c | B1 | 20% | 107.7 | 79.0 | +28.7 | 26.986% |
| 38-40 | 192 | 1 | 2c | B3 | 80% | 19.2 | -4.7 | +23.9 | 2.674% |
| 41-42 | 126 | 32 | 10c | B1 | 22% | 95.0 | 72.2 | +22.8 | 19.2% |
| 43-44 | 107 | 54 | 15c | B4 | 17% | 53.3 | 41.3 | +12.0 | 12.147% |
| 45-46 | 126 | 48 | 15c | B1 | 16% | 155.7 | 118.6 | +37.1 | 28.648% |
| 47-48 | 110 | 11 | 12c | B1 | 29% | 56.6 | 9.9 | +46.7 | 11.701% |
| 49-51 | 129 | 50 | 6c | B1 | 34% | 115.6 | 93.3 | +22.3 | 18.706% |
| 52-54 | 146 | 11 | 4c | B1 | 48% | 49.3 | 19.9 | +29.4 | 6.611% |
| 55-56 | 126 | HOLD | 15c | B1 | 20% | 106.7 | 69.2 | +37.5 | 16.086% |
| 57-58 | 126 | 18 | 6c | B1 | 34% | 21.5 | 8.0 | +13.5 | 3.076% |
| 59-61 | 191 | 35 | 15c | B3 | 16% | 162.6 | 117.2 | +45.4 | 14.786% |
| 62-64 | 210 | 12 | 4c | B2 | 51% | 105.6 | 71.8 | +33.8 | 8.245% |
| 65-66 | 136 | 33 | 15c | B2 | 18% | 46.4 | 16.2 | +30.2 | 5.435% |
| 67-68 | 123 | 2 | 2c | B1 | 88% | 17.6 | -3.2 | +20.8 | 2.177% |
| 69-71 | 152 | HOLD | 15c | B1 | 22% | 104.7 | 55.2 | +49.5 | 10.312% |
| 72-74 | 168 | 2 | 2c | B1 | 90% | 33.6 | 18.6 | +15.0 | 2.807% |
| 75-76 | 104 | 8 | 3c | B1 | 74% | 50.1 | 33.1 | +17.0 | 6.574% |
| 77-79 | 134 | 14 | 15c | B4 | 33% | 114.3 | 40.9 | +73.4 | 11.695% |
| 80-82 | 120 | 1 | 1c | B1 | 99% | 12.0 | -4.6 | +16.6 | 1.251% |
| 83-86 | 153 | 15 | 15c | B1 | 43% | 138.5 | 67.3 | +71.2 | 11.615% |
| 87-94 | 190 | 2 | 1c | B1 | 98% | 38.0 | 28.5 | +9.5 | 2.235% |
| **TOTAL** | | | | | | **2465.4** | **1607.9** | **+857.5** | |

## Read of the optima
- **Best post_start (skip):** {'B4': 5, 'B1': 18, 'B3': 4, 'B2': 3} | **(fallback):** {'B1': 22, 'B4': 3, 'B3': 3, 'B2': 2} — consistent with the drift-timing finding that dips deepen late (B4).
- **Best discount (skip):** {0: 2, 1: 8, 2: 11, 3: 4, 12: 2, 15: 3} | **(fallback):** {1: 2, 2: 3, 3: 3, 4: 3, 6: 2, 8: 2, 10: 2, 12: 3, 15: 10}.

*Read-only on atp_main_drift_timing.parquet + atp_main_spike_perN.parquet. Per-band per-combo parquet staged (atp_main_entry_rules.parquet, uncommitted). raw_max exit model + in-sample optima — see caveats.*