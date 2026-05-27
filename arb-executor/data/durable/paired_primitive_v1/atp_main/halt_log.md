# HALT — ATP_MAIN paired primitive (pre-flight probe gate)

_Generated 2026-05-27 16:41:35 ET (= 2026-05-27 20:41:35 UTC)._

## Why halted

- **PROBE 1 pairing rate = 100.0%** is outside the [80.0, 92.0]% halt band (expected ~85.52%).
- **PROBE 2 fully T-20m-observable events = 651** is below the 1500-event floor.

## Root cause (G23 honest provenance)

The spec's expected ~85.52% pairing and ~1,500–1,990 events are derived from `PAIRING_DIAGNOSTIC.md`, which was computed on the **spike per-N universe** (`atp_main_spike_perN.parquet`, N=4,137 → 2,230 events → 1,907 paired). That is a different, broader universe than the **F35 tier-1/2 live-era cohort** the spec names as the cohort (`tier==live` & `both_sides_*` & `total_volume_in_match>0`), which yields only **N=1,326 → 663 events**. The F35 screen is event-symmetric (both legs share match_start_method/tier and in-match volume), so it pairs at ~100%, not 85.52%. The two halt triggers are the same fact seen twice: the named cohort is ~2.9x smaller than the universe the expectations came from.

## Decision required

Operator must choose the cohort definition before primitive emission:

- **(A)** F35 tier-1/2 live-era cohort *as literally specified* → 663 paired events, 100% pairing. (Probes as designed would still flag the <1500 floor.)
- **(B)** The spike per-N universe (`atp_main_spike_perN.parquet`, 4,137 N) that the ~85.5% / ~1,907 expectations and probe thresholds were calibrated for.

No primitive emitted. No bands, no R sweep, no analysis performed.

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
    "expected_pct": 85.52,
    "halt_band": [
      80.0,
      92.0
    ],
    "halt_triggered": true
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
    "halt_min_events": 1500,
    "halt_triggered": true
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