# V50 first-fill price discipline — rejected

V50 was built as one price-only clause on frozen V47 (`fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34`). A leg's live rest/entry target is capped at `99 - sibling lowest causal true-trade price observed so far`. Before the sibling has a true trade, V47 is unchanged. The clause never withholds placement, never adds a clock, and re-evaluates the live price on every sibling print.

The sealed `a20e1a85976aefee6a6f0567957174133b692df6` receipt is retained as mechanism evidence: 45 sealed-exam cases, 31 first-fill-richness and 14 genuinely infeasible. Those event identities are not the development 804 and were not falsely joined. The development CAP_UNFEASIBLE attribution was independently derived from frozen V47 as: exactly one credited leg, with the uncredited sibling's integer union-reach floor strictly above its fixed pair cap. It conserves 192 unique development events.

## Executable result

- V47 reproduction: 396 completed/under-par pairs, 1,936c locked, -162c naked, +1,774c true book; frontier 52/71/142/396.
- V50: 388 completed/under-par pairs, 1,869c locked, -80c naked, +1,789c true book; frontier 54/65/136/388.
- Delta: -8 completed, -67c locked, +82c naked, +15c true book.
- CAP_UNFEASIBLE recovery: 35 of 192 development cases.
- Cost column: 184 V47 entries delayed and 116 lost.
- Strict build-verification completions: 331 -> 311.
- Named: PUTJEA 73 unchanged; ROCBUE incomplete unchanged; KREZHE 97 unchanged; KRUFER 96 unchanged; BOSCOP 80 unchanged; ARNROM regresses 89 -> 97.

The causal bound has zero price-bound violations and its development-class conservation passes, but the named ARNROM non-regression check fails. V50 is therefore `BLOCKED_V47_REMAINS_OPERATIVE`. The true-book gain does not override the mechanism-bound regression or the loss of eight completed pairs. No deployment or live-cutover authority is created.

Two clean builds produced 36 byte-identical pre-determinism artifacts. Focused V50, V50 package, V47 focused/package, and V45 focused/package checks all pass. Forbidden access is zero for holdout, live, network-runtime, order, position, exit, settlement, DCA, and deployment surfaces.

Frozen report:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a60adeb3e8f510c53f02415669208090b47462e9/.claude/window1_live_v4_replay/v50_first_fill_price_discipline_20260811/REPORT.md

Attribution scorecard:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a60adeb3e8f510c53f02415669208090b47462e9/.claude/window1_live_v4_replay/v50_first_fill_price_discipline_20260811/ATTRIBUTION_SCORECARD.json

CAP recovery/cost receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a60adeb3e8f510c53f02415669208090b47462e9/.claude/window1_live_v4_replay/v50_first_fill_price_discipline_20260811/CAP_BOUND_RECOVERY_AND_COST_RECEIPT.json

Named receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a60adeb3e8f510c53f02415669208090b47462e9/.claude/window1_live_v4_replay/v50_first_fill_price_discipline_20260811/NAMED_V50_RECEIPT.json

Determinism receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a60adeb3e8f510c53f02415669208090b47462e9/.claude/window1_live_v4_replay/v50_first_fill_price_discipline_20260811/DETERMINISM_RECEIPT.json
