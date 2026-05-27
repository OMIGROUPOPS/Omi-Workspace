# ATP_MAIN paired primitive — handoff (2026-05-27 17:35:27 ET = 2026-05-27 21:35:27 UTC)

**Path A** — F35 tier-1/2 live-era cohort, thresholds calibrated to this universe.

**Final N in primitive:** 651 paired events  |  **producer commit:** `a18b5be6e3f4`  |  **output sha256:** `cedbf559ec5f123f`

## Probe results (verbatim)

```json
{
  "probe1_pairing": {
    "cohort_tickers": 1326,
    "total_events": 663,
    "paired_events": 663,
    "singleton_events": 0,
    "over_paired_events": 0,
    "pairing_rate_pct": 100.0,
    "halt_floor_pct": 95.0,
    "spike_perN_reference_pct": 85.52,
    "halt_triggered": false
  },
  "probe2_t20": {
    "paired_events_in": 663,
    "both_legs_t20_observable": 651,
    "one_leg_only": 7,
    "neither_leg": 5,
    "t20_window": [
      18.0,
      22.0
    ],
    "halt_min_events": 500,
    "halt_triggered": false
  },
  "probe3_inmatch": {
    "both_t20_in": 651,
    "both_legs_inmatch_tape_ok": 651,
    "dropped": 0,
    "drop_pct_from_probe2": 0.0,
    "severe_loss_flag": false
  },
  "probe4_inversion": {
    "n": 651,
    "mean": 101.99,
    "median": 102,
    "std": 2.48,
    "p10": 101.0,
    "p25": 101.0,
    "p75": 102.0,
    "p90": 103.0,
    "count_off_gt_3c": 23,
    "pct_within_3c": 96.47
  }
}
```

## Anchor sum distribution (diagonal check)

- min 99, p10 101.0, p25 101.0, median 102, p75 102.0, p90 103.0, max 142, mean 101.99 (cents)

- count |sum-100c| > 3c: 23 (96.47% within 3c)

## Per-leg anchor distribution (leg-labeling sanity — A must be >= B)

- legA (higher): min 51, p10 56.0, p25 60.0, median 68, p75 78.0, p90 88.0, max 100, mean 69.65

- legB (lower):  min 1, p10 14.0, p25 24.0, median 35, p75 42.0, p90 46.0, max 69, mean 32.35

- A>=B holds on all rows: True

## T-20m ttms distribution (anchor tightness)

- legA: min 18, p10 20.0, p25 20.0, median 20, p75 20.0, p90 20.0, max 22, mean 20.05

- legB: min 19, p10 20.0, p25 20.0, median 20, p75 20.0, p90 20.0, max 22, mean 20.06

## match_duration_min distribution

- min 6.333, p10 64.48, p25 77.32, median 97.483, p75 128.5, p90 155.0, max 1388.283, mean 111.15

## settlement winner side

- A: 443, B: 208, NONE: 0

## peak-trade exit-fill coverage (price_high null edge case)

- legs with zero non-null price_high in [match_start, settlement-300s]: legA 0, legB 0 (of 651 each)

- None — every in-match leg traded, as expected on the F35 cohort.

## 5 random sample rows

```json
[
  {
    "event_ticker": "KXATPMATCH-26APR13TRUMED",
    "legA_ticker": "KXATPMATCH-26APR13TRUMED-MED",
    "legB_ticker": "KXATPMATCH-26APR13TRUMED-TRU",
    "match_start_ts": 1776090300,
    "settlement_ts": 1776096262,
    "settlement_winner_side": "A",
    "match_duration_min": 99.367,
    "legA_anchor_cents": 71,
    "legA_anchor_dollars": 0.71,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1776095400,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 32,
    "legB_anchor_dollars": 0.32,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 65,
    "legB_peak_trade_inmatch_ts": 1776091680,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 103,
    "pair_skew_cents": 39,
    "pair_anchor_sum_off_100c": 3
  },
  {
    "event_ticker": "KXATPMATCH-26APR28MEDCOB",
    "legA_ticker": "KXATPMATCH-26APR28MEDCOB-MED",
    "legB_ticker": "KXATPMATCH-26APR28MEDCOB-COB",
    "match_start_ts": 1777403580,
    "settlement_ts": 1777412248,
    "settlement_winner_side": "B",
    "match_duration_min": 144.467,
    "legA_anchor_cents": 52,
    "legA_anchor_dollars": 0.52,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 90,
    "legA_peak_trade_inmatch_ts": 1777408800,
    "legA_settle_value": 0.0,
    "legA_realized_at_settlement_cents": 0,
    "legB_anchor_cents": 50,
    "legB_anchor_dollars": 0.5,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 99,
    "legB_peak_trade_inmatch_ts": 1777411860,
    "legB_settle_value": 1.0,
    "legB_realized_at_settlement_cents": 100,
    "pair_combined_anchor_cents": 102,
    "pair_skew_cents": 2,
    "pair_anchor_sum_off_100c": 2
  },
  {
    "event_ticker": "KXATPMATCH-26MAR17OPEBOR",
    "legA_ticker": "KXATPMATCH-26MAR17OPEBOR-OPE",
    "legB_ticker": "KXATPMATCH-26MAR17OPEBOR-BOR",
    "match_start_ts": 1773945720,
    "settlement_ts": 1773952760,
    "settlement_winner_side": "A",
    "match_duration_min": 117.333,
    "legA_anchor_cents": 55,
    "legA_anchor_dollars": 0.55,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1773952320,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 47,
    "legB_anchor_dollars": 0.47,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 73,
    "legB_peak_trade_inmatch_ts": 1773947880,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 102,
    "pair_skew_cents": 8,
    "pair_anchor_sum_off_100c": 2
  },
  {
    "event_ticker": "KXATPMATCH-26MAR05ZHEKOP",
    "legA_ticker": "KXATPMATCH-26MAR05ZHEKOP-ZHE",
    "legB_ticker": "KXATPMATCH-26MAR05ZHEKOP-KOP",
    "match_start_ts": 1772771460,
    "settlement_ts": 1772779458,
    "settlement_winner_side": "B",
    "match_duration_min": 133.3,
    "legA_anchor_cents": 55,
    "legA_anchor_dollars": 0.55,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 62,
    "legA_peak_trade_inmatch_ts": 1772773500,
    "legA_settle_value": 0.0,
    "legA_realized_at_settlement_cents": 0,
    "legB_anchor_cents": 47,
    "legB_anchor_dollars": 0.47,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 99,
    "legB_peak_trade_inmatch_ts": 1772777520,
    "legB_settle_value": 1.0,
    "legB_realized_at_settlement_cents": 100,
    "pair_combined_anchor_cents": 102,
    "pair_skew_cents": 8,
    "pair_anchor_sum_off_100c": 2
  },
  {
    "event_ticker": "KXATPMATCH-26MAR29DEJHAN",
    "legA_ticker": "KXATPMATCH-26MAR29DEJHAN-HAN",
    "legB_ticker": "KXATPMATCH-26MAR29DEJHAN-DEJ",
    "match_start_ts": 1774891380,
    "settlement_ts": 1774898058,
    "settlement_winner_side": "A",
    "match_duration_min": 111.3,
    "legA_anchor_cents": 61,
    "legA_anchor_dollars": 0.61,
    "legA_T20m_ttms_min": 20,
    "legA_peak_trade_inmatch_cents": 99,
    "legA_peak_trade_inmatch_ts": 1774897440,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 40,
    "legB_anchor_dollars": 0.4,
    "legB_T20m_ttms_min": 20,
    "legB_peak_trade_inmatch_cents": 44,
    "legB_peak_trade_inmatch_ts": 1774891500,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 101,
    "pair_skew_cents": 21,
    "pair_anchor_sum_off_100c": 1
  }
]
```

## Honest unknowns / calibration context (G23)

- **Why the floor numbers differ from PAIRING_DIAGNOSTIC.md:** the prior halted run (ec7cdae) used a [80, 92]% pairing band and a 1500-event floor. Those were calibrated against the **spike per-N universe** (`atp_main_spike_perN.parquet`, N=4,137 → 2,230 events → 1,907 paired = 85.52%), a broader set than the cohort this producer actually uses. The **F35 tier-1/2 live-era cohort** (`tier==live` & `both_sides_*` & `total_volume_in_match>0`) is event-symmetric — if one leg passes the screen its partner almost always does too — so it pairs at ~100%, not ~85.5%. Path A re-calibrates to the cohort itself: PROBE 1 floor-only ≥ 95%, PROBE 2 floor 500. These are not a relaxation of quality gates; they match the gate shape to the universe being gated.

- **descriptive_1c dropped from inputs:** `atp_main_descriptive_1c.parquet` is cell-level (90 rows, no ticker column), so it carries no per-ticker settlement. `settlement_value` is read directly from `per_minute_features` (the answer-key terminal value, E32(d)). Only two inputs are recorded in run_summary.json.

- **settlement_winner_side = NONE** would indicate a paired event where neither leg settled 1.0 (data anomaly). This run: 0.

- **Premarket excluded by construction:** the forward walk is match_start → settlement-300s only. R hits in premarket (the +1c/+2c/+3c trap) are out of scope here and handled separately downstream.

- **Exit-fill threshold = price_high (max trade print/min), not yes_bid_close** (corrected from a18b5be). A resting sell fills when a trade prints at/above the sell price, so `legX_peak_trade_inmatch_cents = max(price_high*100)` over non-null price_high in [match_start, settlement-300s]. No depth qualification — we trade 5-10ct, not 250. Downstream: `legX_hit_R(R) = peak_trade_inmatch_cents >= anchor + R`; realized = (anchor+R) if hit else realized_at_settlement_cents. Null peak_trade (no in-match trade) surfaced above.
