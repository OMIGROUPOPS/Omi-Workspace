# Corrected Window-1 OS-family development result

Authoritative PRE-RUN commit:
`bb7f994305334fcc95a57ce261f5e90385458798`.

This is a deterministic July 12-20 development result. D remains 804.
The July 24-26 holdout was not queried or opened.

## Primary result

Raw integers are stated before percentages.

| Metric | Raw | Required ratio |
|---|---:|---:|
| D | 804 | immutable |
| C | 10 | C/D = 1.24% |
| PC | 9 | PC/D = 1.12%; PC/C = 90.00% |
| S | 9 | S/C = 90.00% |
| IC | 4 | IC/D = 0.50%; IC/C = 40.00% |

The leading lawful policy is
`drift_cohort_orientation__walk__reaim`. It uses the
`drift_cohort_orientation` family, walk posture, and re-aim response to the
first sibling fill. PC is 9, versus the fixed target of 603. The raw shortfall
is 594; the target was not reached.

Classification conservation:

| Classification | Count |
|---|---:|
| exact-five | 10 |
| partial | 0 |
| other-quantity | 0 |
| nonfill | 678 |
| contradictory | 14 |
| censored | 102 |
| total | 804 |

The PC-failure census is 795 events: 678 nonfills, 102 censored, 14
contradictory, and 1 exact-five completion whose combined close delta was not
negative. Missing data remains in D.

## Completed-event economics and guards

Across the 10 completed events, combined entry cost was 94-101 cents
(mean 97.4; median 97.5; p25 96; p75 98). Combined Window-1-close delta was
-7 to 0 cents (mean -4.2; median -4; p25 -6; p75 -3). The 20 individual-leg
deltas were -10 to +3 cents (mean -2.1; median -2; p25 -3; p75 +1).

`official-point-strict-60s-v1` means an official exact start minus the frozen
60-second positive guard. `te-calibration-central-93pct-asymmetric-v1` means
the five-minute-quantized late-detection proxy minus 900 seconds for a strict
Window-1 verdict; the complementary post-start edge is proxy plus 600
seconds, and the interior remains censored.

| Event | Guard | Strict cutoff UTC | Cost | Pair delta | Leg deltas | PC/S/IC |
|---|---|---|---:|---:|---:|---|
| KXATPMATCH-26JUL12CERKOL | asymmetric proxy -900/+600 | 2026-07-14 08:25 | 94 | -7 | -10, +3 | 1/1/0 |
| KXATPMATCH-26JUL12JACTRU | official strict 60s | 2026-07-13 16:29 | 101 | 0 | +3, -3 | 0/0/0 |
| KXATPMATCH-26JUL12SONSCH | asymmetric proxy -900/+600 | 2026-07-13 08:20 | 96 | -6 | +1, -7 | 1/1/0 |
| KXATPMATCH-26JUL12TSIBUS | official strict 60s | 2026-07-14 13:49 | 97 | -5 | -3, -2 | 1/1/1 |
| KXATPMATCH-26JUL15BUBHAL | official strict 60s | 2026-07-16 14:29 | 98 | -3 | +1, -4 | 1/1/0 |
| KXATPMATCH-26JUL19GAUCAR | asymmetric proxy -900/+600 | 2026-07-21 10:55 | 99 | -2 | -3, +1 | 1/1/0 |
| KXATPMATCH-26JUL19KOPBUS | official strict 60s | 2026-07-20 14:24 | 98 | -4 | -3, -1 | 1/1/1 |
| KXATPMATCH-26JUL19STRSHE | asymmetric proxy -900/+600 | 2026-07-21 08:55 | 98 | -4 | -2, -2 | 1/1/1 |
| KXATPMATCH-26JUL19TORBAS | asymmetric proxy -900/+600 | 2026-07-20 10:55 | 97 | -4 | -3, -1 | 1/1/1 |
| KXATPMATCH-26JUL19VANFAR | asymmetric proxy -900/+600 | 2026-07-21 17:05 | 96 | -7 | -10, +3 | 1/1/0 |

The selected event ledger carries the full guard object, cutoff, cost,
combined delta, and both individual deltas for all 804 verdicts.

## Results by development date

| Date | D | C | PC | S | IC |
|---|---:|---:|---:|---:|---:|
| July 12 | 156 | 4 | 3 | 3 | 1 |
| July 13 | 114 | 0 | 0 | 0 | 0 |
| July 14 | 99 | 0 | 0 | 0 | 0 |
| July 15 | 64 | 1 | 1 | 1 | 0 |
| July 16 | 42 | 0 | 0 | 0 | 0 |
| July 17 | 50 | 0 | 0 | 0 | 0 |
| July 18 | 62 | 0 | 0 | 0 | 0 |
| July 19 | 121 | 5 | 5 | 5 | 3 |
| July 20 | 96 | 0 | 0 | 0 | 0 |

## Results by tournament class

| Class | D | C | PC | S | IC |
|---|---:|---:|---:|---:|---:|
| ATP_CHALL | 369 | 0 | 0 | 0 | 0 |
| ATP_MAIN | 147 | 10 | 9 | 9 | 4 |
| WTA_CHALL | 136 | 0 | 0 | 0 | 0 |
| WTA_MAIN | 152 | 0 | 0 | 0 | 0 |

## Results by start-source class

| Start source | D | C | PC | S | IC |
|---|---:|---:|---:|---:|---:|
| official exact | 234 | 4 | 3 | 3 | 2 |
| quantized late-detection proxy | 453 | 6 | 6 | 6 | 2 |
| clean causal interval | 31 | 0 | 0 | 0 | 0 |
| contradictory | 14 | 0 | 0 | 0 | 0 |
| schedule-only | 20 | 0 | 0 | 0 | 0 |
| live-by-only | 52 | 0 | 0 | 0 | 0 |

The 453 proxy clocks are not exact starts and were never promoted to exact
starts.

## Best result by frozen policy family

Every family searched four declared posture/response combinations. D is 804
for every row.

| Family | Best policy | C | PC | S | IC | Partial | Nonfill | Censored |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| causal_micro_pressure | causal_micro_pressure__park__reaim | 7 | 7 | 6 | 2 | 1 | 693 | 89 |
| drift_cohort_orientation | drift_cohort_orientation__walk__reaim | 10 | 9 | 9 | 4 | 0 | 678 | 102 |
| dynamic_recut_atlas | dynamic_recut_atlas__park__reaim | 2 | 2 | 2 | 1 | 2 | 699 | 87 |
| full_chronological_stack | full_chronological_stack__park__reaim | 2 | 2 | 2 | 1 | 0 | 692 | 96 |
| mirror_deceleration | mirror_deceleration__walk__reaim | 10 | 9 | 9 | 4 | 0 | 678 | 102 |
| pair_divot_core | pair_divot_core__park__reaim | 10 | 9 | 8 | 3 | 2 | 684 | 94 |

The complete result artifact contains all 24 candidates, not only each family
leader.

## Results by feature-coverage class

| Coverage class | D | C | PC | S | IC |
|---|---:|---:|---:|---:|---:|
| available 6 of 16 | 3 | 0 | 0 | 0 | 0 |
| available 7 of 16 | 24 | 2 | 2 | 2 | 1 |
| available 8 of 16 | 215 | 7 | 6 | 6 | 2 |
| available 9 of 16 | 50 | 1 | 1 | 1 | 1 |
| available 10 of 16 | 339 | 0 | 0 | 0 | 0 |
| available 11 of 16 | 61 | 0 | 0 | 0 | 0 |
| no causal birth book | 1 | 0 | 0 | 0 | 0 |
| start-boundary censored | 99 | 0 | 0 | 0 | 0 |
| window left after guarded start | 12 | 0 | 0 | 0 | 0 |

No event had all 16 feature families. Full depth was unavailable and unused.
Shape-corpus cells were unavailable per event because there was no
independent non-AIM causal cell mapping; they were not imputed. Top-five
pressure, FV/bookmaker voice, and all other optional families were active
only on the legs where their causal coverage was present.

## Frozen ablations

All 13 predeclared ablations ran. Eleven retained C=10, PC=9, S=9, IC=4;
`without_true_print_walk` fell to C=9, PC=8, S=7, IC=3; and
`without_first_fill_sibling_response` fell to C=6, PC=6, S=6, IC=2.
The ablation artifact preserves the full classification census for every
ablation.

## Data ceiling versus feature ceiling

These are separate and neither is called a market ceiling:

- Data/start ceiling: 705 events have a strict positive boundary after the
  13 named evidence censors. Only 26 events complete under the optimistic
  same-price queue bound.
- Feature ceiling: 0 events have all 16 allowed feature families. Missing
  feature components were disabled individually, never proxy-substituted or
  imputed.

A development miss is not automatically a market ceiling.

## Start-ledger corrections and historical witnesses

The frozen conservation is 687 start-clock rows + 31 clean causal intervals
+ 14 contradictory + 20 schedule-only + 52 live-by-only = 804. Start-clock
means 234 official exact clocks plus 453 five-minute-quantized late-detection
proxies. Calibration used the 234 official-start population: 222 unique
comparisons, median proxy lateness +300 seconds, and 207/222 (93.24%) within
15 minutes, with a longer 15-event tail.

The seven historical witnesses were recomputed under both stated laws:

- strict 60-second witness guard: 5 strict duals, 3 under par;
- frozen asymmetric development guard (-900/+600): 1 strict dual, 0 under
  par.

Every witness has per-leg guard IDs, cutoffs, margins, and verdicts in
`HISTORICAL_WITNESSES_GUARDED.json`. The correction record also discloses
the four prior post-to-strict reversals (TOPUGO, COLVAC, GRABER, YEVCAM), the
permanently unavailable shrink from 106 to 82, and the W1-leg expansion from
45 to 146.

## Frozen invariants

All frozen invariants held: D and source conservation; adapter, metric,
candidate allowlist, source and cache hashes; start-boundary law; no
schedule-as-start; no future information; no narrow proxy substitution; no
feature-gap imputation; no unproved full depth; no AIM_V2 or Pinnacle use;
and no holdout access.

This report is ready for independent audit. No live, production, order,
position, settlement, exit, DCA, Window 2, configuration, or deployment
surface was modified.
