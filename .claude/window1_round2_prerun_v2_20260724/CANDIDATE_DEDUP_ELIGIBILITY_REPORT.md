# Round-2 candidate deduplication and eligibility

The retained allowlist is pairwise distinct over complete D=804
decision-hash bundles. No candidate exists only on synthetic fixtures.

| candidate | eligible | censored | cohort NO_CALL | distinct events vs base | place | reprice | cancel | positive prints consumed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| r2_async_pair__park_join__hold | 694 | 110 | 0 | 0 | 590 | 9531 | 9734 | 2249391 |
| r2_async_pair__touch_park__hold | 694 | 110 | 0 | 486 | 592 | 5416 | 5545 | 2249391 |
| r2_causal_steer__park_join__hold | 694 | 110 | 1471 | 324 | 590 | 10388 | 10598 | 2249391 |
| r2_full_os__walk_park__hold | 694 | 110 | 1471 | 415 | 418 | 8278 | 8375 | 2249391 |

Named retained-candidate censor reasons are `causal_role` (10 leg
occurrences), `dynamic_recut_cell_unavailable` (127), and, where
required, `top5` (10). Missing features remain censored, never
nonfills.

| candidate | async events | posture events | recut events | sibling events | walk events | BBO-covered events | top5-covered events |
|---|---:|---:|---:|---:|---:|---:|---:|
| r2_async_pair__park_join__hold | 671 | 415 | 771 | 265 | 0 | 799 | 799 |
| r2_async_pair__touch_park__hold | 671 | 439 | 771 | 321 | 0 | 799 | 799 |
| r2_causal_steer__park_join__hold | 671 | 415 | 771 | 258 | 0 | 799 | 799 |
| r2_full_os__walk_park__hold | 671 | 299 | 771 | 223 | 187 | 799 | 799 |

The JSON capability receipt names every exercising event, every
cohort class/zone/event/leg call, every full-ticker per-leg
placement/reprice/cancel count, and every missing-feature count.

Removed before freeze:

- `r2_async_pair__park_join__reaim` — non-minimal response variant; hold retains executable first-fill sibling response.
- `r2_async_pair__touch_park__reaim` — non-minimal response variant; hold retains executable first-fill sibling response.
- `r2_causal_steer__park_join__reaim` — non-minimal response variant; hold retains executable first-fill sibling response.
- `r2_full_os__walk_park__reaim` — non-minimal response variant; hold retains executable first-fill sibling response.
- `r2_full_os__park_join__hold` — walk actuator is unreachable under park_join; structurally duplicates causal-steer posture.
- `r2_full_os__park_join__reaim` — walk actuator is unreachable under park_join; structurally duplicates causal-steer posture and uses removed response variant.

The two full-stack park/join variants were structurally redundant
because that posture cannot call the walk actuator. The reaim variants
were removed as non-minimal response variants; the retained hold
policies exercise real first-fill sibling decisions.
