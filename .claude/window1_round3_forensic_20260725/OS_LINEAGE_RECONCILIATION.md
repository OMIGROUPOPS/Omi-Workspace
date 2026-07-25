# Round-2 grid reconciliation to the Living Vault and OS lineage

The chronological Living Vault and official OS lineage govern this
reconciliation. Newer pair-law entries require one pair authority,
independent leg clocks, evidence-only reposts, and preservation of queue
when no new causal evidence exists.

| OS family/mechanic | Round-2 actual behavior | Adjudication |
|---|---|---|
| Pair law / one authority | one instrument owned both legs and enforced pair guards | present |
| Independent asynchronous timing | each leg had its own fitted `t_deep`, but the fit became a hard existence gate | present but mechanically defective |
| Pair presence at discovery | park/walk legs waited for a recent divot | missing |
| Touch / join / park / walk | touch existed; park/walk were depth-based; `join` was also depth-subtracted | join was nominal/miswired |
| First-fill sibling response | hold logged bookkeeping; reaim waited for a later trigger and changed +1 | reaim real; hold non-order-changing |
| Partial first-fill response | sibling chain waited for full five-contract completion | missing |
| Dual-divot / catch | per-leg divot recognition existed | partial; deployed dual seal not bound |
| Dynamic floor / recut | dynamic cells repriced on book changes | wired, but violated evidence-only queue preservation |
| Drift / recognition | causal T6 history-through-decision could reprice | real, but its two candidates produced no guarded W1 fills |
| Orientation | causal checkpoint could reprice | real |
| Cohort steering | all bound cells were below n=30 | named NO_CALL; not decision coverage |
| True-print flow | receipt-identified positive-size public prints only | present |
| BBO / top-five pressure | causal where present; top-five was not full depth | present within bound coverage |
| Own fingerprints | used only to subtract attributable volume | safety invariant; no self-confirmation |
| Shape corpus | no lawful independent causal mapping | unavailable |
| Bookmaker/FV/Pinnacle | no source-proved causal Pinnacle surface in the instrument | unavailable |
| Proved full depth | no snapshot ancestry plus continuous sequence reconstruction | unavailable |
| Schedule revision chain | only the bound exchange schedule observation was available | unavailable beyond bound anchor |

## Candidate decision proof

All eight Round-2 candidates produced different aggregate order-decision
hashes. Raw action counts:

| Candidate | Places | Reprices | Cancels | Hold records | Reaim applied | Guarded W1 fill receipts |
|---|---:|---:|---:|---:|---:|---:|
| `r2_async_pair__park_join__hold` | 590 | 9,531 | 9,734 | 265 | 0 | 1 |
| `r2_async_pair__park_join__reaim` | 590 | 9,387 | 9,587 | 0 | 91 | 1 |
| `r2_async_pair__touch_park__hold` | 592 | 5,416 | 5,545 | 321 | 0 | 40 |
| `r2_async_pair__touch_park__reaim` | 592 | 4,989 | 5,114 | 0 | 85 | 40 |
| `r2_causal_steer__park_join__hold` | 590 | 10,388 | 10,598 | 258 | 0 | 0 |
| `r2_causal_steer__park_join__reaim` | 590 | 9,664 | 9,871 | 0 | 87 | 0 |
| `r2_full_os__walk_park__hold` | 418 | 8,278 | 8,375 | 223 | 0 | 0 |
| `r2_full_os__walk_park__reaim` | 418 | 8,117 | 8,211 | 0 | 64 | 0 |

Changed order streams therefore existed, but none connected two lawful
five-contract fills. The causal-steer and full-OS names did not turn their
additional actions into any guarded Window-1 fill. Cohort was wholly
NO_CALL, hold was bookkeeping, and own-volume subtraction had no
attributable own volume; those names are not credited as decision coverage.

Round 3 does not substitute a walk-law replay. It keeps the bound causal
divot, walk, orientation, drift, BBO/top-five, flow, pair-cost, and
own-volume machinery, while repairing only the partner-starvation action
chain identified by the admitted result.
