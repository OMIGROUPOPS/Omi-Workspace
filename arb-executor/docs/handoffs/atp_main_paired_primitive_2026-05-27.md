# ATP_MAIN paired primitive — handoff (2026-05-27 17:55:00 ET = 2026-05-27 21:55:00 UTC)

**Cohort = atlas N universe** — ticker list from `atp_main_spike_perN.parquet` (4,137 N), no tier/F35 screen. PROBE 1 band [80,92]%, PROBE 2 floor 1500.

**Final N in primitive:** 1881 paired events  |  **producer commit:** `49c88bea2e8a`  |  **output sha256:** `564c19382ad6464e`

## Probe results (verbatim)

```json
{
  "probe1_pairing": {
    "cohort_tickers": 4137,
    "total_events": 2230,
    "paired_events": 1907,
    "singleton_events": 323,
    "over_paired_events": 0,
    "pairing_rate_pct": 85.52,
    "halt_band": [
      80.0,
      92.0
    ],
    "expected_pct": 85.52,
    "halt_triggered": false
  },
  "probe2_t20": {
    "paired_events_in": 1907,
    "both_legs_t20_observable": 1907,
    "one_leg_only": 0,
    "neither_leg": 0,
    "t20_window": [
      18.0,
      22.0
    ],
    "halt_min_events": 1500,
    "halt_triggered": false
  },
  "probe3_inmatch": {
    "both_t20_in": 1907,
    "both_legs_inmatch_tape_ok": 1881,
    "dropped": 26,
    "drop_pct_from_probe2": 1.36,
    "severe_loss_flag": false
  },
  "probe4_inversion": {
    "n": 1881,
    "mean": 103.11,
    "median": 102,
    "std": 5.24,
    "p10": 101.0,
    "p25": 101.0,
    "p75": 103.0,
    "p90": 104.0,
    "count_off_gt_3c": 275,
    "pct_within_3c": 85.38
  }
}
```

## Anchor sum distribution (diagonal check)

- min 99, p10 101.0, p25 101.0, median 102, p75 103.0, p90 104.0, max 158, mean 103.11 (cents)

- count |sum-100c| > 3c: 275 (85.38% within 3c)

## Per-leg anchor distribution (leg-labeling sanity — A must be >= B)

- legA (higher): min 51, p10 56.0, p25 61.0, median 69, p75 79.0, p90 87.0, max 98, mean 70.17

- legB (lower):  min 6, p10 16.0, p25 24.0, median 34, p75 42.0, p90 47.0, max 76, mean 32.94

- A>=B holds on all rows: True

## T-20m ttms distribution (anchor tightness)

- legA: min 19, p10 20.0, p25 20.0, median 20, p75 20.0, p90 20.0, max 22, mean 20.03

- legB: min 18, p10 20.0, p25 20.0, median 20, p75 20.0, p90 20.0, max 22, mean 20.01

## match_duration_min distribution

- min 6.333, p10 41.23, p25 69.9, median 95.5, p75 130.52, p90 162.65, max 1388.283, mean 106.06

## settlement winner side

- A: 1302, B: 579, NONE: 0

## peak-trade exit-fill coverage (price_high null edge case)

- legs with zero non-null price_high in [match_start, settlement-300s]: legA 1, legB 1 (of 1881 each; 0.053% of legs)

- Near-zero / within tolerance — these legs never traded in-match, so peak_trade is null and R can only resolve at settlement.

## 5 random sample rows

```json
[
  {
    "event_ticker": "KXATPMATCH-25AUG25HARAUG",
    "legA_ticker": "KXATPMATCH-25AUG25HARAUG-AUG",
    "legB_ticker": "KXATPMATCH-25AUG25HARAUG-HAR",
    "match_start_ts": 1756240680,
    "settlement_ts": 1756246536,
    "settlement_winner_side": "A",
    "match_duration_min": 97.6,
    "legA_anchor_cents": 80,
    "legA_anchor_dollars": 0.8,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1756243980,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 21,
    "legB_anchor_dollars": 0.21,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 22,
    "legB_peak_trade_inmatch_ts": 1756240680,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 101,
    "pair_skew_cents": 59,
    "pair_anchor_sum_off_100c": 1
  },
  {
    "event_ticker": "KXATPMATCH-26FEB10BARSEY",
    "legA_ticker": "KXATPMATCH-26FEB10BARSEY-BAR",
    "legB_ticker": "KXATPMATCH-26FEB10BARSEY-SEY",
    "match_start_ts": 1770740520,
    "settlement_ts": 1770747489,
    "settlement_winner_side": "A",
    "match_duration_min": 116.15,
    "legA_anchor_cents": 59,
    "legA_anchor_dollars": 0.59,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1770747120,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 44,
    "legB_anchor_dollars": 0.44,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 99,
    "legB_peak_trade_inmatch_ts": 1770745320,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 103,
    "pair_skew_cents": 15,
    "pair_anchor_sum_off_100c": 3
  },
  {
    "event_ticker": "KXATPMATCH-26APR24HURMUS",
    "legA_ticker": "KXATPMATCH-26APR24HURMUS-MUS",
    "legB_ticker": "KXATPMATCH-26APR24HURMUS-HUR",
    "match_start_ts": 1777021920,
    "settlement_ts": 1777028934,
    "settlement_winner_side": "A",
    "match_duration_min": 116.9,
    "legA_anchor_cents": 63,
    "legA_anchor_dollars": 0.63,
    "legA_T20m_ttms_min": 21,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1777028400,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 38,
    "legB_anchor_dollars": 0.38,
    "legB_T20m_ttms_min": 21,
    "legB_peak_trade_inmatch_cents": 45,
    "legB_peak_trade_inmatch_ts": 1777027680,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 101,
    "pair_skew_cents": 25,
    "pair_anchor_sum_off_100c": 1
  },
  {
    "event_ticker": "KXATPMATCH-26JAN20BUBFUC",
    "legA_ticker": "KXATPMATCH-26JAN20BUBFUC-BUB",
    "legB_ticker": "KXATPMATCH-26JAN20BUBFUC-FUC",
    "match_start_ts": 1768978560,
    "settlement_ts": 1768987134,
    "settlement_winner_side": "A",
    "match_duration_min": 142.9,
    "legA_anchor_cents": 85,
    "legA_anchor_dollars": 0.85,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1768986240,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 18,
    "legB_anchor_dollars": 0.18,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 34,
    "legB_peak_trade_inmatch_ts": 1768980000,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 103,
    "pair_skew_cents": 67,
    "pair_anchor_sum_off_100c": 3
  },
  {
    "event_ticker": "KXATPMATCH-26MAR26CERZVE",
    "legA_ticker": "KXATPMATCH-26MAR26CERZVE-ZVE",
    "legB_ticker": "KXATPMATCH-26MAR26CERZVE-CER",
    "match_start_ts": 1774566780,
    "settlement_ts": 1774570967,
    "settlement_winner_side": "A",
    "match_duration_min": 69.783,
    "legA_anchor_cents": 73,
    "legA_anchor_dollars": 0.73,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1774569600,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 28,
    "legB_anchor_dollars": 0.28,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 32,
    "legB_peak_trade_inmatch_ts": 1774566780,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 101,
    "pair_skew_cents": 45,
    "pair_anchor_sum_off_100c": 1
  }
]
```

## Honest unknowns / calibration context (G23)

- **Cohort universe reverted to the atlas N set (corrects 49c88be):** the cohort is now the ticker list from `atp_main_spike_perN.parquet` (4,137 N) directly — the same N universe the atlas/spike-volatility map was built on — with NO tier filter and NO F35 screen. The F35 `tier==live` & `both_sides_*` & `total_volume_in_match>0` screen used in path A was inappropriately inherited; it produced a 663-event event-symmetric cohort (~100% pairing). This universe pairs at ~85.52% (PAIRING_DIAGNOSTIC.md), the expected non-symmetric rate.

- **PROBE 1/2 thresholds restored to the universe-appropriate values from ec7cdae:** PROBE 1 band [80, 92]% (admits the ~85.5% atlas pairing), PROBE 2 floor 1500. The path-A PROBE 1 floor-only ≥95% was specific to the event-symmetric F35 cohort and does NOT apply here — leaving it would have false-halted this universe at ~85.5%. PROBE 3/4 unchanged.

- **Inputs:** `per_minute_features` (tape/anchor/settlement, sha-verified 9fde4b5d) and `atp_main_spike_perN.parquet` (cohort source). `n_profile_v1` is no longer used. `settlement_value` is read from `per_minute_features` (answer-key terminal value, E32(d)), not from the spike per-N file. Both inputs' sha256 recorded in run_summary.

- **settlement_winner_side = NONE** would indicate a paired event where neither leg settled 1.0 (data anomaly). This run: 0.

- **Premarket excluded by construction:** the forward walk is match_start → settlement-300s only. R hits in premarket (the +1c/+2c/+3c trap) are out of scope here and handled separately downstream.

- **Exit-fill threshold = price_high (max trade print/min), not yes_bid_close** (corrected from a18b5be). A resting sell fills when a trade prints at/above the sell price, so `legX_peak_trade_inmatch_cents = max(price_high*100)` over non-null price_high in [match_start, settlement-300s]. No depth qualification — we trade 5-10ct, not 250. Downstream: `legX_hit_R(R) = peak_trade_inmatch_cents >= anchor + R`; realized = (anchor+R) if hit else realized_at_settlement_cents. Null peak_trade (no in-match trade) surfaced above.
