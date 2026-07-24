# Final eight-candidate eligibility and deduplication

| candidate | eligible | censored | cohort NO_CALL | reaim NO_CALL | place | reprice | cancel | sibling order-change events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| r2_async_pair__park_join__hold | 694 | 110 | 0 | 0 | 590 | 9531 | 9734 | 0 |
| r2_async_pair__park_join__reaim | 694 | 110 | 0 | 185 | 590 | 9387 | 9587 | 91 |
| r2_async_pair__touch_park__hold | 694 | 110 | 0 | 0 | 592 | 5416 | 5545 | 0 |
| r2_async_pair__touch_park__reaim | 694 | 110 | 0 | 251 | 592 | 4989 | 5114 | 85 |
| r2_causal_steer__park_join__hold | 694 | 110 | 1471 | 0 | 590 | 10388 | 10598 | 0 |
| r2_causal_steer__park_join__reaim | 694 | 110 | 1471 | 182 | 590 | 9664 | 9871 | 87 |
| r2_full_os__walk_park__hold | 694 | 110 | 1471 | 0 | 418 | 8278 | 8375 | 0 |
| r2_full_os__walk_park__reaim | 694 | 110 | 1471 | 168 | 418 | 8117 | 8211 | 64 |

Every candidate is eligible on 694 events and censored on 110 with
the previously frozen named reasons. NO_CALL does not alter either
count. Pairwise complete D=804 order-decision bundles are distinct.
