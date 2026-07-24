# Round-2 Window-1 policy and family specification

Status: **PRE-RUN construction only. No Round-2 candidate has been scored.**

This final superseding instrument preserves the passed gates and repairs R1
and R2 established by the independent audit at commit
`7851204a2f1ffac1d6af61670b67bc0bf6794f9e`.
The immutable development population remains D=804 for July 12-20 UTC, the
primary target remains PC=603, and July 24-26 remains sealed and unqueried.

## Counterfactual object

Every candidate creates a new causal order stream for both required legs. A
stream begins with `leg_open` and ends with one terminal record. Placements,
reprices, cancellations, public-print fill observations, and sibling decisions
carry their own exchange/causal timestamp and leg identity. No candidate may
reuse a historical placement as its decision.

The two legs are one pair for completeness but two independent state machines:
each binds its own birth cell, divot depth, recut timing prior, micro signal,
book, queue, posture, active order, fill state, and cancellation clock.

## Chronological law

1. The first causal BBO binds the leg's birth cell and the frozen pre-development
   recut/divot surfaces.
2. `policy_anchor_ts` is the timestamped exchange schedule known to the policy.
   The recut cell's `t_deep_p50` produces that leg's own eligibility timestamp
   relative to that policy anchor and declared corridor. The sibling may have
   a different timestamp. `evaluation_real_start_ts` is never passed to this
   code.
3. Macro values never trigger an order. Public non-self true prints and a
   contemporaneous BBO/ask-hold state provide the micro confirmation.
4. Orientation is first callable at the first-hour checkpoint and uses only
   non-self prints observed through that checkpoint.
5. Drift recognition is first callable at T6. It computes net and dip from
   BBO history observed through T6 and can change only T6-or-later actions.
6. A causal book-cell change may recut and reprice only that leg.
7. A full five-contract fill on one leg may create a timestamped hold or arm
   reaim on the still-independent other leg. Arming never changes an order.
   Reaim may apply only when that sibling reaches its own strictly later
   lawful causal trigger after its own eligibility. The changed sibling order
   must be exactly one cent above the otherwise-lawful guarded order.
8. Remaining orders cancel independently at the declared policy horizon.
   A separate ex-post evaluator may then use independently reconstructed start
   truth to classify actions; it cannot create or time an order.

The four Round-1 `pair_divot_core` rows failed item 5 by reading a T6
`called_band` in a T8 price. Round 2 has no T8 pricing function that accepts a
recognition band. The mechanical fixture varies only the future recognition
mapping: every pre-T6 decision hash remains identical and the post-T6 hashes
differ.

## Executable families

- **Asynchronous divot timing:** each leg derives eligibility from its own
  frozen recut cell.
- **Leg posture:** touch, join, park, and walk are selected per leg role.
- **Exact walk:** a walk requires a verified non-self print chain and advances
  exactly one cent, never marketably.
- **First-fill sibling response:** hold is bookkeeping only. Reaim arms after
  the first causal full fill and becomes order-affecting only at the sibling's
  later lawful trigger. Missing trigger evidence returns
  `NO_CALL_UNAVAILABLE`; it never creates an action or censor.
- **Pair/divot recut:** the current leg alone reacts to its current book-cell
  change; no identical pair timestamp is imposed.
- **Orientation:** the frozen orientation table may deepen/reprice the called
  role only after the first-hour observation checkpoint.
- **Drift recognition:** the frozen h6 table may change an order only at/after
  T6.
- **Cohort steering:** the frozen pre-development cohort is callable only at
  n>=30 and only when its depth differs by at least two cents. Below-floor
  support returns `NO_CALL_UNAVAILABLE`; it never censors the leg, erases the
  underlying posture/divot decision, or changes the event to nonfill.
- **True-print flow:** only receipt-identified, independently size-verified
  positive public prints are admitted. Zero, null, malformed, synthetic, or
  fingerprinted-own activity contributes zero and never confirms divot, flow,
  pressure, posture, walk, join, touch, park, recut, replenishment, or fill.
- **BBO/top-five pressure:** the causal top-five ask/external-bid ratio may add
  the frozen one-cent pressure depth where the feature is present.
- **Own-order subtraction:** exact fingerprints subtract contributed book and
  print volume. They can remove false evidence but can never add confirmation.
- **Start boundary:** a timestamped schedule may lawfully anchor policy time,
  but schedule-only, live-by-only, and contradictory truth can never prove a
  positive Window-1 result. The guarded actual start is evaluation-only.

Nine policy families change at least one decision in isolated contrasts on
the bound real D=804 development population. Cohort is loaded and evaluated
but unavailable at n=30, own-order subtraction is a mandatory safety law but
inert because all 1,608 T8 receipts show zero attributable own volume, and the
start boundary is evaluation-only. None of those three is counted as policy
coverage.

## Frozen grid

The final superseding allowlist contains eight real-eligible, pairwise-distinct
candidate IDs:

- async pair: park/join hold/reaim and touch/park hold/reaim;
- causal steer: park/join hold/reaim;
- full OS: walk/park hold/reaim.

The four lawful reaim variants are restored. The two full-stack park/join
variants remain removed because the walk actuator is unreachable under that
posture and the remaining policies are structurally the corresponding
causal-steer park/join chains.

There are nine predeclared selected-candidate ablations and no free numeric
parameter. True-print flow and own-volume subtraction are invariant evidence
laws, not ablatable shortcuts. The exact IDs and values live in
`WINDOW1_ROUND2_CANDIDATES_V1.json`.

## Frozen scorer

The deterministic scorer is complete and hash-bound in this PRE-RUN but has
not been executed on any candidate. It consumes only the frozen event ledger,
candidate streams, admitted public fill receipts, V5 start ledger, close
references, feature/censor classifications, and immutable binding receipts.
It derives the strict positive cutoff as official start minus 60 seconds,
proxy clock minus 900 seconds, or clean interval lower bound minus 60 seconds.
Schedule-only and live-by-only rows are censored and contradictory rows remain
separate. Raw realized start is never a cutoff.

The scorer preserves D=804 and the frozen C/PC/S/IC definitions, reports every
event exactly once into the corrected census, and keeps cohort/reaim NO_CALL
and feature unavailability separate. Only minimal synthetic contract fixtures
were executed to test it.

## Missingness and terminal law

A missing required feature produces `censored_feature`, not nonfill. Cohort
abstention is not missingness and does not censor. A
feature-complete leg that had a lawful order and zero fills produces
`genuine_zero_fill`; a feature-complete leg whose micro trigger never appeared
produces `no_eligible_micro_trigger`. Missingness never changes D and never
becomes success.

## Unavailable or excluded

- Pinnacle has zero causal rows and is unavailable.
- Full depth is unavailable: no snapshot-ancestry plus gap-free
  sequence-continuous reconstruction is proved. The adapter is top-five only.
- Shape is unavailable without an independent non-AIM causal mapping.
- AIM_V2 remains excluded.
- The uncommitted sealed pair-policy object is unavailable and is not recreated.
- Riser is not an actuator; its disarm remains controlling.
- Bookmaker/FV is allowed only when causal and source-proven, but no v1 candidate
  requires it.

No production, live_v4, configuration, live order, position, Window 2, exit,
settlement, or DCA surface is imported or callable.
