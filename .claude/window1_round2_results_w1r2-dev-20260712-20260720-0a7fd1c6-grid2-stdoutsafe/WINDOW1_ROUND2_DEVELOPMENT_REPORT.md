# Window-1 Round-2 development benchmark

Development result for the frozen eight-candidate Round-2 family.
This is not a market ceiling and does not generalize to all OS policies.

| candidate | D | C | PC | S | IC | target | distance | conservation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| r2_async_pair__park_join__hold | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_async_pair__park_join__reaim | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_async_pair__touch_park__hold | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_async_pair__touch_park__reaim | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_causal_steer__park_join__hold | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_causal_steer__park_join__reaim | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_full_os__walk_park__hold | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |
| r2_full_os__walk_park__reaim | 804 | 0 | 0 | 0 | 0 | 603 | 603 | 804 |

No frozen selection or ranking rule exists; candidates remain unranked.
S and IC are reported separately and are not substitutes for PC.

Unavailable machinery remains unavailable: Pinnacle, proved full depth,
and lawful independent shape mapping were not inferred.

Base/reaim comparisons are in `BASE_REAIM_COMPARISON.json`.
The event ledgers and all breakdown tables are machine-readable artifacts.
