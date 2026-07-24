# Round-2 Window-1 policy and family specification

Status: **PRE-RUN construction only. No Round-2 candidate has been scored.**

This instrument repairs the under-expression established by the independent
cross-audit at commit `024f03bb5b1944bae39ad5afef6ee019ef5dc06d`.
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
2. The recut cell's `t_deep_p50` produces that leg's own eligibility timestamp,
   clamped to the guarded Window-1 interval. The sibling may have a different
   timestamp.
3. Macro values never trigger an order. Public non-self true prints and a
   contemporaneous BBO/ask-hold state provide the micro confirmation.
4. Orientation is first callable at the first-hour checkpoint and uses only
   non-self prints observed through that checkpoint.
5. Drift recognition is first callable at T6. It computes net and dip from
   BBO history observed through T6 and can change only T6-or-later actions.
6. A causal book-cell change may recut and reprice only that leg.
7. A full five-contract fill on one leg may create a timestamped hold or
   one-cent sibling reaim on the still-independent other leg.
8. Remaining orders cancel independently at the guarded right edge.

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
- **First-fill sibling response:** hold or reaim occurs only after the first
  leg's causal full fill.
- **Pair/divot recut:** the current leg alone reacts to its current book-cell
  change; no identical pair timestamp is imposed.
- **Orientation:** the frozen orientation table may deepen/reprice the called
  role only after the first-hour observation checkpoint.
- **Drift recognition:** the frozen h6 table may change an order only at/after
  T6.
- **Cohort steering:** the frozen pre-development cohort is callable only at
  n>=30 and only when its depth differs by at least two cents.
- **True-print flow:** zero-size, synthetic, or fingerprinted-own activity
  never confirms flow, divot, walk, or fill.
- **BBO/top-five pressure:** the causal top-five ask/external-bid ratio may add
  the frozen one-cent pressure depth where the feature is present.
- **Own-order subtraction:** exact fingerprints subtract contributed book and
  print volume. They can remove false evidence but can never add confirmation.
- **Start boundary:** schedule-only, live-by-only, and contradictory rows cannot
  create a positive Window-1 stream; every positive-capable stream carries the
  frozen guard object.

Each family above changes at least one eligible decision in the synthetic
causal-fixture campaign. Names that cannot pass that test are not advertised.

## Frozen grid

The allowlist contains ten candidate IDs:

- async pair: park/join or touch/park, each with hold or reaim;
- causal steer: park/join, with hold or reaim;
- full OS: park/join or walk/park, each with hold or reaim.

There are nine predeclared selected-candidate ablations and no free numeric
parameter. True-print flow and own-volume subtraction are invariant evidence
laws, not ablatable shortcuts. The exact IDs and values live in
`WINDOW1_ROUND2_CANDIDATES_V1.json`.

## Missingness and terminal law

A missing required feature produces `censored_feature`, not nonfill. A
zero-length guarded interval produces `zero_length_window1_opportunity`. A
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
