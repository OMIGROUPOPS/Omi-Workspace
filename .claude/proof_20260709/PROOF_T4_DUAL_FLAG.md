# OUTCOME PROOF (C46, two-lane) — C-T4-DUAL-FLAG (Plex ratification's binding condition; shadow/logging only)

**Candidate SHA: `12a523f3`** (live_v4.py shadow hook + ws volume accumulator, oslayer/holdgate.py comment+echo upgrade, analysis/os_shadow_rollup.py fence, PLEX_T3_T4_RATIFICATION.md — zero order-path or decision-core behavior change; os_active untouched, dormant).

## Prior art (C45)
- **PLEX_T3_T4_RATIFICATION.md (recorded first, this push)** — the ruling being executed; T4's binding condition in its exact shape; verbatim body still owed by the relay (paste dropped it — flagged, slot reserved).
- **OS BUILD vault entry 07-09 + STEP1.md §P4** — holdgate.py was BUILT dual-flag ("TWO separate readings, never merged"); tonight's finding: the live CALLER starved it (`expected_share_by_now=None` → floor_miss_flag constant False; baseline = running median of all samples, not the T−8h→T−4h span). The pure module was right; the wiring wasn't.
- **STEP1.md §P1b** — the volume floor has no enforcement point except the hold-gate; hence the ruling's two-jobs law.
- **CLIMBSIDE_SPEC.md arm-path paragraph** — arm prerequisites unchanged (four bars, joint-shadow n≥30, shadow-first).
- **HOURLY_APPENDIX 07-07** — the source of the shadow-default expected-share curve's shape (ITF/CHALL volume entirely T−2h→bell); numbers are placeholders the threshold pass refits, never a ruling.

## LANE 1 — MECHANISM
- **Unit checks 4/4** (pure module, run pre-deploy): diverging case quiet=True ∧ floor_qual=on_pace both named separately · below_pace fires on pace-miss with realized+projected logged · qualified_now short-circuits on realized ≥ staged floor · missing curve → `unevaluable`, named, never silent.
- **The live proof line (tonight's first real dual-flag hold_review):** rendered in the close-out — both flags named and separate, baseline value + `cum_vol` (ws contracts) + `floor_target` + `floor_qual` + `t4: dual_flag_v1` on the line.
- **Fence:** rollup now splits `pre_instrument` (no t4 stamp — 300 lines today pre-deploy) from the threshold dataset; the T4 accumulation clock = first stamped line after boot.
- **Byte-identity for trading:** the ws accumulator is a dict-add consumed only by the shadow hook; `_os_shadow` remains log-only (never raises, dedup unchanged); decision_core untouched; no config change.

## LANE 2 — SETTLEMENT P&L
$0 claimed. Shadow/logging only.

## Regression watches
Every post-deploy hold_review line carries `t4: dual_flag_v1` + `floor_qual` ≠ silent · rollup `pre_instrument` counter stops growing after tonight · quiet/floor divergence count visible nightly · os-import-boundary line in the gate (holdgate stays pure).
