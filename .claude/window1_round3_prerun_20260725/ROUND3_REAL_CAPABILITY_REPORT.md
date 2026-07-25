# Round-3 real-input capability and distinctness report

This campaign generated order streams only. It did not import or invoke the
scorer, calculate C/PC/S/IC, rank candidates, run ablations, or access the
holdout.

## Hard gates

- D = 804 and candidate-event streams = 6,432.
- Exactly eight candidates, in frozen order.
- Every candidate is eligible on 694 real events and censored on 110:
  105 `dynamic_recut_cell_unavailable`, 5 `causal_role`.
- Every candidate has a unique aggregate decision hash.
- Every candidate differs from its declared reference on real development
  events.
- Every reaim candidate makes an actual later sibling order change on real
  events; bookkeeping does not count.
- Metrics are null and `scored=false` for every stream.

## Candidate capability

| Candidate | Eligible | Censored | Place | Reprice | Cancel | Events distinct from reference | Reaim applied | Reaim NO_CALL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `r3_pair_presence__park_join__hold` | 694 | 110 | 1,471 | 785 | 1,253 | 777 | 0 | 0 |
| `r3_pair_presence__park_join__reaim` | 694 | 110 | 1,471 | 977 | 1,437 | 322 | 325 | 324 |
| `r3_pair_presence__touch_park__hold` | 694 | 110 | 1,471 | 811 | 1,265 | 777 | 0 | 0 |
| `r3_pair_presence__touch_park__reaim` | 694 | 110 | 1,471 | 951 | 1,396 | 269 | 271 | 347 |
| `r3_causal_steer__park_join__hold` | 694 | 110 | 1,471 | 1,720 | 2,185 | 692 | 0 | 0 |
| `r3_causal_steer__park_join__reaim` | 694 | 110 | 1,471 | 1,879 | 2,338 | 291 | 292 | 354 |
| `r3_full_os__walk_park__hold` | 694 | 110 | 1,471 | 3,401 | 3,949 | 777 | 0 | 0 |
| `r3_full_os__walk_park__reaim` | 694 | 110 | 1,471 | 3,557 | 4,095 | 278 | 287 | 288 |

The 1,471 placements per candidate reflect independent leg presence across
eligible events; they are not fills or performance results.

## Real base/reaim order proof

| Base / reaim | Real changed-order events | Witness event | First fill ts | Later sibling trigger ts | Base | Reaim |
|---|---:|---|---:|---:|---:|---:|
| pair-presence park/join | 322 | `KXATPCHALLENGERMATCH-26JUL12AZKLEO` | 1783890888.057660 | 1783891204.598156 | 49 | 50 |
| pair-presence touch/park | 269 | `KXATPCHALLENGERMATCH-26JUL12BINGIL` | 1783864852.466626 | 1783864964.354738 | 88 | 89 |
| causal-steer park/join | 291 | `KXATPCHALLENGERMATCH-26JUL12AZKLEO` | 1783890888.057660 | 1783891204.598156 | 48 | 49 |
| full-OS walk/park | 278 | `KXATPCHALLENGERMATCH-26JUL12AVEFOR` | 1783880265.028795 | 1783880846.987768 | 50 | 51 |

All 1,160 real reaim witnesses have exact +1, the emitted repost equals the
reaim price, and all earlier decisions are byte-identical to the hold base.
The full ledger is `ROUND3_REAIM_ORDER_DIFFERENCES.jsonl`.

## Family capability

| Family | Loaded | Available | Evaluated | Decision-changing | Selected/active |
|---|---|---|---|---|---|
| independent pair presence | yes | yes | yes | yes | yes |
| leg-specific touch/join/park | yes | yes | yes | yes | yes |
| positive-print divot recut | yes | yes | yes | yes | yes |
| first-fill sibling response | yes | yes | yes | yes | yes |
| nonself one-cent walk | yes | yes | yes | yes | yes |
| causal orientation | yes | yes | yes | yes | yes |
| causal drift/recognition | yes | yes | yes | yes | yes |
| BBO/top-five pressure | yes | where present | yes | yes | yes |
| cohort steering | yes | no | yes | no | no |
| advisory fitted `t_deep` | yes | yes | yes | no; inert diagnostic | no |
| own-order subtraction | yes | yes | yes | no attributable volume | safety only |
| deployed pair-policy seal | no | no | no | no | no |
| shape mapping | no | no | no | no | no |
| Pinnacle | no | no | no | no | no |
| proved full depth | no | no | no | no | no |

The score-free streams consumed 2,249,391 receipt-identified positive-size
prints per candidate. Both-leg BBO and top-five coverage exists on 799
events; five events lack complete coverage and remain named rather than
imputed.

Per-event differences for all retained candidates are in
`ROUND3_CANDIDATE_ORDER_DIFFERENCES.jsonl`. Aggregate details and hashes are
in `ROUND3_REAL_CAPABILITY.json`.
