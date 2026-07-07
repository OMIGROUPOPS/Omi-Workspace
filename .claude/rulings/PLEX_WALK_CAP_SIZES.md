# PLEX WALK-CAP RULING — per-cat honest-anchor cap sizes (relayed 2026-07-07, evening)

**Provenance:** text as relayed by the operator with the execution dispatch, 2026-07-07. If a
fuller verbatim Plex body exists beyond this relay, this file reserves its slot (REANCHOR
precedent); the operative constraints are in force as relayed either way.

**LINEAGE CORRECTION (honest, per the dispatch):** the staging cite supplied with the relay —
`e1505e92` — was WRONG (that hash is the AIM_V2 OPERATIONAL commit). The correct staging cite
is **`7def47e2`** (2026-07-06 day-queue close-out: "walk-cap honest census harvested (ITF_W p75
+20c) + C-WALKCAP-HONEST-ANCHOR staged gated-OFF"). The ruled sizes below are exactly that
census's per-cat p75 conception→fill drift; the whole staged design (C45: never arm a source
without its envelope) is `walk_cap_honest_anchor` + `walk_cap_honest_by_cat` +
`pos.honest_anchor` set-once at first target (live_v4.py:1627-1628, :7022, :8077-8092).

## THE RULED PARAMETERS (as relayed)

- **Per-cat cap sizes (cents above the honest anchor = the position's FIRST placed target):**
  **ITF_W 20 · ITF_M 14 · ATP_CHALL 2 · WTA_CHALL 2 · MAIN 1** (both mains).
- Sizes land in the STAGED config (`walk_cap_honest_by_cat`); **`walk_cap_honest_anchor`
  stays default-OFF** — nothing arms from this ruling alone.
- **ARM CONDITION = THE JOINT SHADOW:** every placement/repost decision logs, alongside the
  actual level: (a) the level the walk cap ALONE would have permitted, (b) the level the
  expression invariant ALONE would express (join/improve-1 vs the non-self chain), (c) the
  level under BOTH combined; per line the would-fill read vs the tape where computable
  (book/last at decision time; the full would-fill is the nightly offline replay). Nightly
  rollup: conversion/starvation delta of combined-vs-each-alone, and ≤97 held on every
  constrained pair. Runs on the live slate from tonight forward.

## Implementation (this push)
- Config: `walk_cap_honest_by_cat` = ruled sizes; `walk_cap_honest_anchor: false` (explicit).
- `_aim_shadow_log` extended with `walkcap_level` / `walkcap_anchor_src` / `walkcap_cap` /
  `exself_level` / `joint_level` / `tape_last` / `constrained` on every shadow line (both
  call sites: v4_place + walk/repost). Log-only; no order-path change.
- Nightly rollup: `analysis/joint_shadow_rollup.py` → `.claude/live_20260705/JOINT_SHADOW_<date>.md`
  (wired into NIGHTLY_PASS).
- Arm of `walk_cap_honest_anchor` (and the invariant flag, its sibling) waits on the joint
  shadow's nights + the standing four-bar gate. Invariant = step law, cap = journey bound.
