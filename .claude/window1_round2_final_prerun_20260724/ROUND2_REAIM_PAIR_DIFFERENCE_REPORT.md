# Base/reaim real-order differences

Bookkeeping actions are excluded. Each witness is an actual sibling
placement/reprice at its own later lawful trigger.

| base | reaim | event | first fill ts | sibling trigger ts | base order | reaim order | diff | earlier orders identical | changed D=804 events | eligible/censored | cohort NO_CALL | reaim NO_CALL |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| r2_async_pair__park_join__hold | r2_async_pair__park_join__reaim | `KXATPCHALLENGERMATCH-26JUL12HERALM` | 1783880950.268002 | 1783883421.501633 | 84 | 85 | +1 | yes | 91 | 694/110 | 0 | 185 |
| r2_async_pair__touch_park__hold | r2_async_pair__touch_park__reaim | `KXATPCHALLENGERMATCH-26JUL12BINGIL` | 1783865090.935257 | 1783866540.894188 | 16 | 17 | +1 | yes | 85 | 694/110 | 0 | 251 |
| r2_causal_steer__park_join__hold | r2_causal_steer__park_join__reaim | `KXATPCHALLENGERMATCH-26JUL12BINGIL` | 1783865492.449254 | 1783866060.0 | 18 | 19 | +1 | yes | 87 | 694/110 | 1471 | 182 |
| r2_full_os__walk_park__hold | r2_full_os__walk_park__reaim | `KXATPCHALLENGERMATCH-26JUL12BINGIL` | 1783865492.449254 | 1783866540.894188 | 15 | 16 | +1 | yes | 64 | 694/110 | 1471 | 168 |

Every changed event has a matching exact +1 applied receipt;
there are no order differences caused by an abstained reaim call.
All witnesses pass price, par, band, and maximum-cost guards; no
reaim action precedes sibling eligibility or the first-leg fill.
