# Rejected Round-2 PRE-RUN blocker corrections

Controlling audit: `fb17a98fb93ac73668e3ebd731aa0d9c1b99ca43`. Rejected PRE-RUN: `6eecbd1d9adc7c41af28526d0cabe1038f3ae18b`.
Status: **corrected and frozen, not scored**.

## F1 — cohort availability

Below-floor cohort support now returns `NO_CALL_UNAVAILABLE`; it never
sets `feature_censored` and the underlying pair/divot/posture chain
continues. The cohort-aware retained candidates recorded 1,471
per-leg NO_CALLs each. Cohort is unavailable and is not counted as
coverage.

## F2 — positive-size evidence

A single admission gate now requires receipt identity, independently
verified finite size >0, a public source class, and a non-synthetic
row before any fill, divot, flow, orientation, walk, or posture
surface. Zero/null/malformed/synthetic divot and walk fixtures pass.

## F3 — immutable data diet

The data-binding manifest covers D=804 events, 1,608 legs, the V5
start ledger, public print archive, all 804 per-event cache files,
BBO/top-five streams, own-order receipts, feature flags, cohort,
shape/orientation/drift/recut surfaces, close references, source
classes, and censor reasons. The runner refuses any digest, identity,
date, or file-set drift.

## F4 — policy/evaluation clocks

Eligibility is now `policy_anchor_ts + t_deep_p50`, clamped only to
the declared schedule corridor. Realized start is rejected by policy
code and accepted only by the ex-post evaluator. Identical causal
histories remain byte-identical under different future starts while
the evaluator classifies them differently.

## Real capability result

- retained candidates: 4;
- eligible events per candidate: 694; censored: 110;
- pairwise duplicate groups: zero;
- isolated real decision-changing family witnesses: 9;
- D remains 804; target remains PC=603; metrics are unchanged and
  unexecuted;
- July 24-26 remains excluded, unopened, and unqueried.
