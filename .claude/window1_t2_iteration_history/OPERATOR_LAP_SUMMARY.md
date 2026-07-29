# Window-1 T2 operator lap summary — 2026-07-29

Development sample only: 804 events from 2026-07-12 through 2026-07-20,
split 525 fit / 279 post-fit. Holdout remained sealed. Live, exchange, and
trading-system access remained off.

## Frozen arithmetic

- `FEE_CENTS = 0`
- Frozen adapter line:
  `if b2 != math.floor(-d1 - FEE_CENTS - 1):`
- Therefore, on the frozen integer-cent inputs, `b2_max = -d1 - 1`.

## Execution repairs required

1. The V4/V5 execute path referenced `AMBIGUOUS_REASON` without importing it.
   The operator runner bound the existing constant from
   `window1_range_attack_reference_adapter_v2`.
2. The oracle five-contract floor exceeded a credited five-contract fill on
   34 unique event-legs. Candidate duplication produced 229 bindings:
   195 fit and 34 post-fit, totaling 269 cents of 1–2 cent overperformance.
   The credited fill was used as the effective proven floor, making regret
   zero while the overperformance remains separately disclosed here.
3. Final metric conservation read `audited_metric_summary["D"]`, but D is
   stored under `raw_integers_before_percentages`. The operator runner
   populated the expected top-level D for finalization.

## Laps

- Lap 0: frozen overlays. Hold control completed 131; micro control 123.
  Non-control T2 variants completed only 10–11 because parent fills were not
  carried into their scoring inputs.
- Lap 1: preserved parent fills for non-displacing candidates. Completion
  recovered to the controls, with one `<100`/S loss from an overlapping T2
  fill taking precedence.
- Lap 2: applied parent preservation to all T2 variants. Every variant
  recovered to its family control, still with the one overlapping-fill loss.
- Lap 3: parent fills authoritative on overlap; T2 fills admitted only where
  the parent had none. Every T2 variant became exactly equal to its parent
  control. No T2 mechanism added a completion.

## Final aggregate frontier and metrics

| Family | <=93 | <=95 | <=97 | <100 | Any | PC | IC | S |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Macro hold (control and all T2 variants) | 0 | 1 | 7 | 100 | 131 | 115 | 37 | 100 |
| Macro micro (control and all T2 variants) | 0 | 1 | 7 | 94 | 123 | 109 | 34 | 94 |

Best any-price completion is 131/804 = 16.29%. Best PC is 115/804 =
14.30%. Neither family approaches 75%.

Fit/post-fit any-price completion:

- Macro hold: 86/525 fit; 45/279 post-fit.
- Macro micro: 80/525 fit; 43/279 post-fit.

## Regret

Macro hold:

- Leg execution-proof regret: 475 cents across 500 observed legs; median 0,
  p75 1, p90 3; 277 zero-regret legs.
- Pair regret: 102 cents fit + 115 cents post-fit = 217 cents.
- Pair attribution: 208 cents `NEVER_RECOGNIZED`, 9 cents
  `REFERENCE_AMBIGUOUS`.

Macro micro:

- Leg execution-proof regret: 460 cents across 488 observed legs; median 0,
  p75 1, p90 3; 270 zero-regret legs.
- Pair regret: 98 cents fit + 93 cents post-fit = 191 cents.
- Pair attribution: 182 cents `NEVER_RECOGNIZED`, 9 cents
  `REFERENCE_AMBIGUOUS`.

## Stopping ruling

The T2 additions do not improve the parent controls once parent behavior is
preserved honestly. The numbers stopped improving at Lap 3. No holdout result
or live claim follows from this development-sample result.
