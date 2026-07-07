# OUTCOME PROOF (C46, two-lane) — C-JOINT-SHADOW (Plex walk-cap ruling, shadow-first)

**Candidate SHA: `bf678a7c`** (ruling file + staged `walk_cap_honest_by_cat` sizes + joint-shadow logger fields + nightly rollup; `walk_cap_honest_anchor: false` explicit).

## Prior art (C45)
C-WALKCAP-HONEST-ANCHOR staged gated-OFF @`7def47e2` (the whole envelope: flag + by-cat dict + `pos.honest_anchor` set-once — this push arms NOTHING, it fills the dict and lights the shadow); PLEX_EXPRESSION_INVARIANT (the sibling constraint, carry live/clamp off); AIM_SHADOW_PROOF + EX_SELF_PROOF (the logger-only proof precedents); B3 conservative would-fill convention (the rollup's fill test).

## LANE 1 — MECHANISM (deterministic, code-scoped)
- The ONLY consumers of the new config values: (i) the gated enforcement branch `live_v4.py:8077` — guarded by `walk_cap_honest_anchor`, which this push sets **explicitly false**; (ii) the new `_aim_shadow_log` block — which computes and WRITES LOG FIELDS ONLY (`walkcap_level`/`exself_level`/`joint_level`/`constrained`/`tape_last`), inside the existing `aim_shadow` try/except, after every price/size/cancel decision has already been made. No placement, walk, exit, completion, or reconcile path reads any new field.
- Replay claim vs the prior slate: today's 1,988 `aim_shadow` lines re-emitted under this code differ ONLY by the added keys; zero order-path delta by construction. Lint PASS (duplicate-def AST); smoke exercises both shadow call sites (v4_place + walk).
- The ruling's arm condition (joint shadow nights + four bars) is what this push CREATES, not consumes.

## LANE 2 — SETTLEMENT P&L
Not applicable (no order-path delta); flagged pro forma per C46.

**Verdict: logger + staged-values only; deploys through the full gate with the C47 boot audit live and C50's first STRICT window (BOARD + LIVING_VAULT both touched since last_deploy_sha).**
