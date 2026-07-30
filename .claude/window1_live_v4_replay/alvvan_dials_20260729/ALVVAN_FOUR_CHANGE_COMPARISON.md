# ALVVAN — repaired baseline and three isolated dials

**No version completed the pair.** The field repair successfully activated sealed authority, but sealed chose prices the tape never reached. The three requested dials did not solve that price-selection problem.

| Run | VAN | ALV | Pair | What changed |
|---|---|---|---|---|
| Before field repair | 22 filled | 74 missed | No | Authority misread its own order fields, so legacy stayed in control |
| Repaired baseline | 16 resting, no fill | 70 resting, no fill | No | Sweep canceled legacy 22/74 and re-anchored both at sealed 16/70 |
| Contention DROP enforced | 22 filled | No order | No | ALV's 2.4% DROP became a veto; without ALV band state, sealed never took the pair |
| Wait for drift/band | 16 resting, no fill | 70 resting, no fill | No | Orders waited for recognition and were born directly at sealed 16/70 |
| Cohort steering on riser | 16 resting, no fill | 70 resting, no fill | No | No trace or output divergence |

Tape lows: VAN 22, ALV 78.

The pre-repair row comes from the immediately preceding ALVVAN trace. That trace lacked the transaction-consistent `tennis.db` snapshot. In the repaired replay the database was present but its historical quotes still returned the same `NO-READ: stale_sources`, and every decision through the original 22/74 posts matched; the first behavioral change was the repaired ownership sweep.

## 1. Field contract repair

This repair did what it was supposed to do. The sweep read `order_id` and `price`, found both bot-owned orders, flagged the legacy/authority mismatch twice, canceled 22/74, and reposted 16/70 under `SEAL`.

Outcome effect on this game:

- Before: one filled VAN leg at 22; ALV missed; no pair.
- After: zero fills; no pair.

It removed a naked-leg outcome, but it also proved that the sealed B4/B6 depths were too deep for this tape: six cents below the VAN low and eight cents below the ALV low.

## 2. Contention DROP honored

The first split occurred at 1:05:21 AM, when ALV's atlas selector returned DROP with a best fitted completion probability of 2.4%.

- Baseline: posted ALV 74, later re-anchored it to 70.
- Dial: refused ALV completely.
- Downstream: VAN never gained a two-band flat-flat pair state, so its legacy 22 remained live and filled at 1:19:15 AM.
- Final: VAN filled at 22, ALV had no order, no pair.

This dial is actively dangerous as a standalone change because it turns a pair decision into one-sided exposure.

## 3. Placement waits for drift/band

The first split occurred at 12:47:02 AM, when baseline would post VAN 22.

- Dial: held VAN because neither its leg band nor the pair class was ready.
- After VAN B4 and ALV B6 existed, both orders were born under sealed authority at 16/70.
- It eliminated the temporary legacy bids, two cancels, and two reposts.
- Final fills and pair outcome were identical to the repaired baseline: none.

This is the cleanest operational change. It fixes the 43–44 second placement race and removes churn, but it cannot repair an unreachable sealed aim.

## 4. Cohort steering allowed on the riser

The trace diff found no divergence.

ALV's cohort opinion was visible, but enabling riser steering did not change the computed aim that survived downstream. The PATH atlas still selected 74, and sealed authority still replaced it with 70. Orders, timing, fills, and final state were byte-for-field identical at the decision surface.

## Which is worth the most?

By completed pairs, **none**: all scored 0/1.

By correctness and safety:

1. **Keep the field-contract repair.** It restores the authority mechanism and prevents own orders from being misclassified as foreign.
2. **The recognition wait is the only useful dial here.** It produces the same final policy cleanly, without posting and canceling legacy orders first.
3. **Do not enable contention DROP alone.** On this game it creates a naked VAN fill.
4. **The riser-cohort dial is worth zero on ALVVAN.** It changed nothing.

The next causal question is not another one of these three toggles. It is why the flat-flat sealed table demands 16/70 when the observed lows are 22/78, and whether that depth policy is calibrated to a later window than the evaluator is grading.

Machine-readable diffs live under:

- `contention_drop/counterfactual/KXATPCHALLENGERMATCH-26JUL12ALVVAN/`
- `recognition_wait/counterfactual/KXATPCHALLENGERMATCH-26JUL12ALVVAN/`
- `cohort_riser/counterfactual/KXATPCHALLENGERMATCH-26JUL12ALVVAN/`
