# OUTCOME PROOF (C46, two-lane) — C-BAND-CLAMP (preflight, [5,95) maker-buy bound)

**Candidate SHA: `31c0f69f`** (one chokepoint guard: maker buys refused at price <5 or >=95).

## Prior art (C45)
The audit's `bid_outside_5_95` FLAG (pre-wired detection, C49 build — this is its enforcement half, exactly as the flag's docstring anticipated); tonight's live counters (COXBRA @4, NAKZHA @2, and the preflight sweep's 11: ADAIMA@1, CAVPLO@2/3, HARMAI@3, KUBSHK@2/95, MANKAV@3/95, VAJKAR@3/95, BOSBOY@2 — all cancelled 200); the `goal_level<=2` noise-skip (:3978, the same principle one tier down); operator sweep list (95 named as out).

## LANE 1 — MECHANISM (deterministic)
- Replay the cohort: tonight's 11 out-of-band resting bids could not have been placed under the clamp — every one arrived via maker paths that flow through `place_order(post_only=True)`. Zero effect on in-band placements (guard is a pure price-range check before any API call). Deliberate taker paths (complete_cross) keep their own `cross_bounds_ok` [5,95] leg-range — unchanged.
- Economics of the refused class: sub-5¢ bids are noise-level goal bids the tape cannot pay (the ≤2¢ skip's own rationale, extended to the operator's 5¢ line); ≥95¢ bids are one tick from par — a pair completed there is structurally ≥ par-adjacent (0A: >100 = total failure regardless of fills). Refusal = participation loss only on legs whose EV was already declared noise by standing law.
- Reconcile re-post loop closed: the sweep cancelled the 11; without the clamp the next `_repost_missing_siblings`/reaim pass re-derives the same levels (goal −basis arithmetic) and re-posts them — the clamp is what makes the cancel stick.

## LANE 2 — SETTLEMENT P&L
Not applicable (refusal-only guard); pro forma per C46.

**Verdict: enforcement half of an already-flagged class; deploys through the full gate, then the OVERNIGHT FREEZE holds (no deploys/restarts until the morning checkpoint).**
