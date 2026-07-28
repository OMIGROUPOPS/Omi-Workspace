# CASUKA live-safety deployment PRE-RUN

Status: **FROZEN FOR INDEPENDENT AUDIT — NOT DEPLOYED**

## Outcome

The narrow deployment source is commit
`d256c491c851999047779827bca73de808b5f650`, based directly on
`bb085ce06db5932049af85f927a7f9316ad76816`, the commit that introduced the
currently running `live_v4.py` Git blob
`f1857199164664037fef41b024e60f27fa373548` on the frozen VPS lineage.

Only the independently audited CASUKA D1-D3 delta was transplanted:

- per-ticker reconcile-cycle exit-intent serialization;
- final sell-side exchange-truth clamp;
- booked-positive plus unsettled-holding pair-classifier truth.

The deployable file set is exactly `arb-executor/live_v4.py`, candidate blob
`ebd29103ff2153f3d6ced83995c3eb8c159fe38d`, SHA-256
`85fdd653ee85dd598388d3cf6f537999decf0f0bdece6b8b3495a19041ee05d4`.

## Running-lineage resolution

The frozen independent receipt records a VPS checkout at `eca101c6` and a
running file blob `f1857199`. Git history proves these are not the same tree
identity: `eca101c6` contains `live_v4.py` blob `035135ea`. Its direct parent
`bb085ce0` changed the file from `2aa371a2` to `f1857199`. Therefore
`bb085ce0`, not a branch-tip inference, is the exact commit that produced the
running bytes. This distinction is why the deployment candidate starts from
the blob producer and why future deployment must use a one-file integration
commit.

## P0 exclusion

The repair parent `a4996dd0` contains undeployed P0 real-start-guard code and
blob `949f6995`. None of those bytes were used as the candidate baseline.
Candidate-versus-running-parent changes contain zero P0 marker hits. Every P0
surface remains AST-identical to the running parent; within
`_place_order_unlocked`, only the two audited D2 blocks differ, and those
blocks are AST-identical to repair `94be4113`.

The complete one-file delta is frozen as `CASUKA_D1_D3.patch`.

## Equivalence and fixtures

- 15 standalone CASUKA/reconcile/classifier methods: AST-identical to audited
  repair `94be4113`.
- D2 clamp and successful-post intent block inside the otherwise P0-divergent
  placement function: AST-identical.
- Five frozen acceptance fixtures: 5/5.
- Named independent adversarial probes: 21/21.
- Both same-cycle organ orderings converge to exactly one five-lot exit.
- Two consecutive cycles remain idempotent.
- FARRIU and VEGKAW zero-booked/settled classifier regressions pass.

## Validation

- focused repair fixtures: 12/12;
- deployment probes/equivalence: 26/26;
- combined focused: 38/38;
- relevant inherited tests: 7/7;
- AST lint: PASS;
- compile: PASS;
- exact offline CASUKA causal replay: PASS.

The complete historical script census conserves the same 38 known failures:
parent 45/83 pass and candidate 47/85 pass. The two added test scripts pass.
Failure identities and terminal causes are unchanged. Two known failing scripts
gain only the expected reconcile-decorator stack frame.

## Deployment and rollback containment

No deployment, restart, service operation, live GET/POST/DELETE, order change,
position change, configuration change, or halt mutation occurred.

The future deployment template requires:

1. independent PASS of this package;
2. separate operator authorization;
3. an exact one-file integration commit on top of the actual VPS checkout;
4. candidate and rollback blob verification;
5. existing lint, smoke, outcome-proof, close-out, and post-boot gates.

Rollback is pinned to exact running blob `f1857199` in immutable Git object
`bb085ce0:arb-executor/live_v4.py`.

## Audit ruling requested

Verify that this package is exact running bytes plus D1-D3 only; independently
rerun the 5 fixtures, 21 probes, both orderings, two-cycle idempotence,
FARRIU/VEGKAW regressions, full historical parity, P0 exclusion, hashes,
rollback materialization, and command fail-closure. A PASS may authorize an
operator-reviewed deployment ceremony only. It must not deploy.
