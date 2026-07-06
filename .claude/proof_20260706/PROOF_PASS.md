# OUTCOME PROOF (C46 two-lane) — C-TRUE-BASIS + C-BOUND-LAW-COMPLETION

**Candidate/proven SHA: `b8a73a55`; proven state also carried at `996dcadc`** (branch blend/kalshi-occ-fallback; the b8a73a55→996dcadc delta is this proof + autopsy evidence only — analysis scripts under `.claude/autopsy_20260706/`, zero bot code/config/table change). Replay tape: the 2026-07-06 post-flip session itself (boot 07-05 23:50:39 ET → 11:2x ET, 174 games, 306 log fills, 707 exchange fill rows, 36 zero-tolerance violations). Replay machinery: `.claude/autopsy_20260706/outcome_replay.py` + forensic joins (`stale_order_forensics.json`, `bound_coverage.json`, `vio_contexts.json`). Deep-cut + triple cross-check: `.claude/autopsy_20260706/VIOLATIONS_DEEPCUT_20260706.md`.

## Prior art (C45)
C-BOUND-RULING 21eaad4 (07-05) — the law these fixes complete · §0A PRIORITY-1=PAIR (07-02, "walk constraint, never a participation filter") · C42 3691ff5 (07-04, same gap-class at three other sites) · A54 in-code (mark-to-market ≠ cost; `_repost_missing_siblings` already fetches true basis) · pair_governor grave f4a766d (06-29 SUMTAK: unserialized writers; P2b/P4 are the placement-side serialization steps; no cancel rework per §4H lock) · paired_cap BANNED (06-12; nothing here vetoes participation).

## LANE 1 — MECHANISM (deterministic replay vs the tape)
- **P1 (true-basis adoption):** 43/144 adoptions booked ≥1c off cost on this tape; the 7 fabricated combined>goal violations dissolve at the source (TODSAG 98→95.5, VAJRAM 101→97.0, HERNAG 98→85.8, POTFEL 101→97.0, TEUHAS 105→97.0, PACLOV 106→97.0, KULVOG 102→95.5 — all bound-compliant on exchange truth), plus the LENTHE avg=0 adoption-churn pathology (18 re-adoptions) books correctly. Exit-cell selection for every adopted fill now keys off cost. **Order flow altered: ZERO — every clean fill survives by construction.**
- **P2 (post-await bound recheck):** TSIAND 77c→73c (blocks the only real walk-race over, +4). VULCOU-class rescues unchanged.
- **P3 (fresh-place bound):** SILDIG 98c→88c (blocks +10, the worst over of the night; the 88c bound bid had already been the standing quote — participation retained). TEXCAR 37→30 (rescue no longer needed).
- **P2/P3 blast radius, full independent scan: exactly 5 of 2,340 buy orders altered** — all five are the violation/near-miss set (VULCOU, TEXCAR, TSIAND, SILDIG, LAPCIO −1c rounding). 2,335 buys byte-identical.
- **P2b (ownership abort):** prophylactic for the reaim×walk interleave (mechanism A); zero legitimate walk placements altered (fires only when the oid was re-keyed mid-flight).
- **P4 (dup guard):** blocks the 12 same-pass duplicate sibling-reposts on this tape (POTFEL double-fill to 10 shares; **KEYNOS — the orphan that filled 54c 23min past the live latch, the night's only grace_breach**). All 102 legitimate WATSHI-heal reposts unaffected (no in-flight twin).
- **Grade construction:** ≤97 completion rate rises (the 7 fabricated overs re-book at/below bound); naked-single count unchanged (no participation touched); violation classes 2(C-a), 2(C-c), 3 eliminated at source; class C-b (6 same-tick pre-basis races, +1..+5c) remains — NAMED UNSOLVED by doctrine choice (only closer = banned pre-fill veto).

## LANE 2 — SETTLEMENT P&L (secondary, sanity)
Violation-carrying games settled **−$16.96 (n=26)** vs clean games **+$7.63 (n=116)** on exchange truth. Fix-attributable deltas on this tape: POTFEL/TEUHAS/HERNAG/PACLOV double-fill exposure halved (≈$8–10 basis), SILDIG +10c×5 and TSIAND +4c×5 overs blocked, KEYNOS in-play fill avoided. Estimated ≈ +$8–12 of the violation damage removed. **n=26 settled violation games — LUCK-POLLUTED below n≈30; Lane 1 is the verdict, Lane 2 is consistent with it.**

## Gate status at proof time
- Lint: PASS (`deploy/lint_gate.py`, AST core) at b8a73a55.
- Tests: 80 standalone files, **zero new failures vs pre-patch baseline** (43 pre-existing stale-harness failures, list at `.claude/autopsy_20260706/baseline_fails.txt`; `test_bound_ruling.py`: ALL BARS HOLD).
- Smoke replay: runs on the VPS inside `deploy/deploy_live_v4.sh` (gate step 2) before restart.
- Not shipped (triple-check verdicts): S1 walk-cap honest-window fallback (STAGED — cap sizes have only card-clock calibration; needs honest-window census); S2 full order-ownership serialization (§4H cancel-rework lock); R1 riser disarm (pre-registered rule FIRED — deferred to Plex with the population caveat); M1/M2 monitor grading fixes (tooling, separate).
