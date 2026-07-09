# OUTCOME PROOF (C46, two-lane) — C-VOL-LEDGER forward field + CONFIG HYGIENE (DRIFT-1/2/6)

**Candidate SHA: `c6979d1a`**.

## Prior art (C45)
- **VOLUME LEDGER dispatch (operator, 07-08 night)** — "one logging field forward"; the backfill + hypotheses run read-only alongside (`/root/volume_ledger.py`, detached).
- **CONFORMANCE_20260708 drift list** — DRIFT-1 (orphaned `exit_band_resolution`), DRIFT-2 (`conception_horizon_hours` living as a code default — a LAW without a config line), DRIFT-6 (retire archaic-ARMED `per_match_clock_shadow`; remove dead `fv_anchor_scenarios_enabled`/`round5_detector_enabled`). This deploy is the "one config-hygiene deploy takes DRIFT-1/2/6" named there.
- **Flow gauge (provisional thresholds) + GRANULARITY LAW** — the vol-at-fire field is micro-instrument telemetry; thresholds refit macro-side (the running corpus job), and any gauge change ships as its OWN gated deploy after operator read (per the dispatch).

## LANE 1 — MECHANISM
- `vol_prints_30m` computed in `_gun_stamp` from the existing `_trade_times` deques (read-only loop, no new state, wrapped in the stamp that already fires once per event): pure logging addition — no decision path reads it.
- Config deltas, key-by-key: `exit_band_resolution` REMOVED (grep: zero code consumers — orphaned) · `fv_anchor_scenarios_enabled`/`round5_detector_enabled` REMOVED (dead legacy, already False; code defaults False — byte-identical) · `per_match_clock_shadow` true→**false** (shadow logging for a flag armed since 07-06 — output-only change: the shadow log lines stop; no decision consumed them) · `conception_horizon_hours: 8` ADDED explicit (code default was 8 — byte-identical by value, the law now visible in config).
- **Every delta is logging/visibility-only or value-identical: the replay of today's session under this build differs by log lines only.**

## LANE 2 — SETTLEMENT P&L
$0 claimed. No price/size/exit/refusal logic touched.

## Regression watches
`gun_fired.vol_prints_30m` present on every fire from this boot · `pm_clock_shadow` line count → 0 (the retire visible) · boot audit PASS with `conception_horizon_hours` read from config.
