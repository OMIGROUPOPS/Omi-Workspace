# Round-2 Window-1 PRE-RUN freeze

Status: **FROZEN, NOT SCORED. Stop for independent CC review.**

## Immutable scope

- development: July 12-20, 2026 UTC only;
- unopened holdout: July 24-26, 2026 UTC;
- D=804; primary target PC=603;
- exact lot: five contracts per leg;
- no production, live_v4, configuration, orders, positions, Window 2,
  exits, settlement, or DCA interface.

## Start boundary

- guard: `te-calibration-central-93pct-asymmetric-v1`;
- proxy interval: [proxy_clock-900s, proxy_clock+600s];
- TennisExplorer clocks remain quantized late-detection proxies, never
  exact starts;
- schedule-only, live-by-only, and contradictory rows cannot produce a
  positive stream;
- the one-sided stronger-causal-bound precedence law remains frozen.

## Grid and capability

- candidate IDs: 10;
- predeclared selected-candidate ablations: 9;
- free numeric parameters: zero;
- every advertised family changed at least one eligible order decision
  in a causal fixture;
- no family is actually selected because Round-2 scoring has not run.

## T8/T6 defect proof

Two fixture runs differed only in the future T6 recognition mapping.
Their complete pre-T6 decision hashes are identical; their post-T6
decision hashes differ. No T8 price accepts a recognition band.

## Missing and unavailable

- missing required features are censored, never nonfills;
- full depth unavailable (ancestry + continuous sequence unproved);
- Pinnacle unavailable; shape unavailable without non-AIM mapping;
- bookmaker/FV conditional but unused by the v1 candidate grid;
- own fingerprints subtract contributed volume only and never confirm
  a market signal.

Round-2 scoring, tuning, ablation evaluation, and holdout access have not
occurred.
