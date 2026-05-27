# ATP_MAIN paired primitive — handoff (2026-05-27 17:00:56 ET = 2026-05-27 21:00:56 UTC)

**Path A** — F35 tier-1/2 live-era cohort, thresholds calibrated to this universe.

**Final N in primitive:** 651 paired events  |  **producer commit:** `ec7cdae44bf6`  |  **output sha256:** `5442e313306f0319`

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

## 5 random sample rows

```json
[
  {
    "event_ticker": "KXATPMATCH-26MAR18HALDRA",
    "legA_ticker": "KXATPMATCH-26MAR18HALDRA-HAL",
    "legB_ticker": "KXATPMATCH-26MAR18HALDRA-DRA",
    "match_start_ts": 1773960960,
    "settlement_ts": 1773968700,
    "settlement_winner_side": "A",
    "match_duration_min": 129.0,
    "legA_anchor_cents": 67,
    "legA_anchor_dollars": 0.67,
    "legA_T20m_ttms_min": 21,
    "legA_peak_bid_inmatch_cents": 99,
    "legA_peak_bid_inmatch_ts": 1773967740,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 35,
    "legB_anchor_dollars": 0.35,
    "legB_T20m_ttms_min": 20,
    "legB_peak_bid_inmatch_cents": 62,
    "legB_peak_bid_inmatch_ts": 1773964260,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 102,
    "pair_skew_cents": 32,
    "pair_anchor_sum_off_100c": 2
  },
  {
    "event_ticker": "KXATPMATCH-26APR03TIEBUR",
    "legA_ticker": "KXATPMATCH-26APR03TIEBUR-TIE",
    "legB_ticker": "KXATPMATCH-26APR03TIEBUR-BUR",
    "match_start_ts": 1775236200,
    "settlement_ts": 1775242093,
    "settlement_winner_side": "B",
    "match_duration_min": 98.217,
    "legA_anchor_cents": 60,
    "legA_anchor_dollars": 0.6,
    "legA_T20m_ttms_min": 20,
    "legA_peak_bid_inmatch_cents": 79,
    "legA_peak_bid_inmatch_ts": 1775236680,
    "legA_settle_value": 0.0,
    "legA_realized_at_settlement_cents": 0,
    "legB_anchor_cents": 43,
    "legB_anchor_dollars": 0.43,
    "legB_T20m_ttms_min": 20,
    "legB_peak_bid_inmatch_cents": 99,
    "legB_peak_bid_inmatch_ts": 1775241720,
    "legB_settle_value": 1.0,
    "legB_realized_at_settlement_cents": 100,
    "pair_combined_anchor_cents": 103,
    "pair_skew_cents": 17,
    "pair_anchor_sum_off_100c": 3
  },
  {
    "event_ticker": "KXATPMATCH-26APR05FONDIA",
    "legA_ticker": "KXATPMATCH-26APR05FONDIA-FON",
    "legB_ticker": "KXATPMATCH-26APR05FONDIA-DIA",
    "match_start_ts": 1775485680,
    "settlement_ts": 1775491073,
    "settlement_winner_side": "A",
    "match_duration_min": 89.883,
    "legA_anchor_cents": 80,
    "legA_anchor_dollars": 0.8,
    "legA_T20m_ttms_min": 20,
    "legA_peak_bid_inmatch_cents": 99,
    "legA_peak_bid_inmatch_ts": 1775490660,
    "legA_settle_value": 1.0,
    "legA_realized_at_settlement_cents": 100,
    "legB_anchor_cents": 22,
    "legB_anchor_dollars": 0.22,
    "legB_T20m_ttms_min": 21,
    "legB_peak_bid_inmatch_cents": 22,
    "legB_peak_bid_inmatch_ts": 1775485680,
    "legB_settle_value": 0.0,
    "legB_realized_at_settlement_cents": 0,
    "pair_combined_anchor_cents": 102,
    "pair_skew_cents": 58,
    "pair_anchor_sum_off_100c": 2
  },
  {
    "event_ticker": "KXATPMATCH-26APR04BONBAU",
    "legA_ticker": "KXATPMATCH-26APR04BONBAU-BON",
    "legB_ticker": "KXATPMATCH-26APR04BONBAU-BAU",
    "match_start_ts": 1775299980,
    "settlement_ts": 1775306673,
    "settlement_winner_side": "B",
    "match_duration_min": 111.55,
    "legA_anchor_cents": 53,
    "legA_anchor_dollars": 0.53,
    "legA_T20m_ttms_min": 22,
    "legA_peak_bid_inmatch_cents": 55,
    "legA_peak_bid_inmatch_ts": 1775300160,
    "legA_settle_value": 0.0,
    "legA_realized_at_settlement_cents": 0,
    "legB_anchor_cents": 50,
    "legB_anchor_dollars": 0.5,
    "legB_T20m_ttms_min": 20,
    "legB_peak_bid_inmatch_cents": 99,
    "legB_peak_bid_inmatch_ts": 1775306220,
    "legB_settle_value": 1.0,
    "legB_realized_at_settlement_cents": 100,
    "pair_combined_anchor_cents": 103,
    "pair_skew_cents": 3,
    "pair_anchor_sum_off_100c": 3
  },
  {
    "event_ticker": "KXATPMATCH-26APR22BERCIL",
    "legA_ticker": "KXATPMATCH-26APR22BERCIL-BER",
    "legB_ticker": "KXATPMATCH-26APR22BERCIL-CIL",
    "match_start_ts": 1776849180,
    "settlement_ts": 1776857142,
    "settlement_winner_side": "B",
    "match_duration_min": 132.7,
    "legA_anchor_cents": 53,
    "legA_anchor_dollars": 0.53,
    "legA_T20m_ttms_min": 20,
    "legA_peak_bid_inmatch_cents": 78,
    "legA_peak_bid_inmatch_ts": 1776851820,
    "legA_settle_value": 0.0,
    "legA_realized_at_settlement_cents": 0,
    "legB_anchor_cents": 49,
    "legB_anchor_dollars": 0.49,
    "legB_T20m_ttms_min": 20,
    "legB_peak_bid_inmatch_cents": 99,
    "legB_peak_bid_inmatch_ts": 1776856680,
    "legB_settle_value": 1.0,
    "legB_realized_at_settlement_cents": 100,
    "pair_combined_anchor_cents": 102,
    "pair_skew_cents": 4,
    "pair_anchor_sum_off_100c": 2
  }
]
```

## Honest unknowns / calibration context (G23)

- **Why the floor numbers differ from PAIRING_DIAGNOSTIC.md:** the prior halted run (ec7cdae) used a [80, 92]% pairing band and a 1500-event floor. Those were calibrated against the **spike per-N universe** (`atp_main_spike_perN.parquet`, N=4,137 → 2,230 events → 1,907 paired = 85.52%), a broader set than the cohort this producer actually uses. The **F35 tier-1/2 live-era cohort** (`tier==live` & `both_sides_*` & `total_volume_in_match>0`) is event-symmetric — if one leg passes the screen its partner almost always does too — so it pairs at ~100%, not ~85.5%. Path A re-calibrates to the cohort itself: PROBE 1 floor-only ≥ 95%, PROBE 2 floor 500. These are not a relaxation of quality gates; they match the gate shape to the universe being gated.

- **descriptive_1c dropped from inputs:** `atp_main_descriptive_1c.parquet` is cell-level (90 rows, no ticker column), so it carries no per-ticker settlement. `settlement_value` is read directly from `per_minute_features` (the answer-key terminal value, E32(d)). Only two inputs are recorded in run_summary.json.

- **settlement_winner_side = NONE** would indicate a paired event where neither leg settled 1.0 (data anomaly). This run: 0.

- **Premarket excluded by construction:** the forward walk is match_start → settlement-300s only. R hits in premarket (the +1c/+2c/+3c trap) are out of scope here and handled separately downstream.
