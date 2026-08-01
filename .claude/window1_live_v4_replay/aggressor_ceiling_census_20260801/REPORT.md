# Window-1 ask-side aggressor and ceiling census

Score-free descriptive census over the frozen July 12-20 D=804. Holdout is not read.

## Law

- BUY means `taker_side=yes`: an aggressor lifted the ask.
- SELL means `taker_side=no`: an aggressor hit the bid.
- Maker-reachable is ex-post only: at least one positive-size SELL print exists on the leg. Its floor is the lowest such print. It does not prove queue priority or five-lot capacity.
- The controlling take ceiling uses the frozen raw-tick ask floor: a same-price ask episode with dwell >=10s and displayed ask capacity >=5 at or below X. The stricter requirement that the capacity receipt itself arrive >=10s later is disclosed separately and does not rewrite the frozen 516.
- Pair ceiling requires both legs reachable, both independent Window-1 closes available, and combined floor-minus-close delta <0.
- Exact time-to-bell partitions use only V5 `exact_start_utc`. Proxy clocks are not promoted to actual bells. Scheduled-clock partitions are separate.

## Conservation

- Events: 804; legs: 1608.
- Lawful admitted prints: 126917; BUY 113892; SELL 13025; UNKNOWN 0.
- Spread bound: 125923; no prior BBO: 994; exact equal-timestamp ambiguity: 0.

## Ex-post opportunity ceilings

| Measure | Events |
|---|---:|
| Controlling take ceiling | 516 |
| Reproduced take ceiling | 516 |
| Both legs take-reachable | 786 |
| Maker pair combined-negative | 253 |
| Both legs maker-reachable | 318 |
| Missing independent close blocks comparison | 182 |

The maker pair count 253 is the subset of the frozen 516 pair-floor events where both targets have a SELL print at or below X. The broader 318 count spans D=804 and is not itself a combined-negative ceiling.

Raw-tick 516 reconciliation: guarded-cache same-law reconstruction 515; stricter later-capacity-receipt variant 512. Exact identities and source-grain explanation are frozen in `CEILING_CENSUS.json`.

All headline totals have mandatory category and starting-price-split partitions in `CEILING_CENSUS.json`. All flow results are partitioned in `AGGRESSOR_SPLIT.json`; no pooled median is emitted.
