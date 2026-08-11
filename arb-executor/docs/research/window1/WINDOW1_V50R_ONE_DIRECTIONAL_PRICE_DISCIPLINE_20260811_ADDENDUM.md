# V50-R one-directional price discipline — blocked

V50-R preserves frozen V47 (`fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34`) and narrows V50's observed-flow price bound to the prospective unhedged first fill. Before either expression is credited, a live level is bounded by `99 - sibling lowest causal true-trade price observed so far`. Once the sibling is credited, that observed-flow authority terminates immediately; only V47's fixed pair cap remains and the second expression seeks its own lawful causal floor. The law adds no timing gate or clock.

## Executable result

- V47 reproduction: 396 completed/under-par pairs, 1,936c locked, -162c naked, +1,774c true book; frontier 52/71/142/396; strict 331.
- V50-R: 385 completed/under-par pairs, 1,869c locked, -79c naked, +1,790c true book; frontier 54/65/136/385; strict 311.
- Delta: -11 completed, -67c locked, +83c naked, +16c true book.
- Development CAP_UNFEASIBLE recovery: 35 of 192 events; 184 incumbent entries delayed and 116 lost.
- Named: ARNROM regresses 89 -> 97; PUTJEA remains completed at 73 rather than withheld; KREZHE 97, KRUFER 96, and BOSCOP 80 are unchanged; ROCBUE remains incomplete.

The trace corrects the proposed diagnosis. In V47, ARN fills first at 50 and ROM later at 39 (89). Under V50-R, the pre-credit bound delays ARN's original opportunity; ROM then fills first at 39 and ARN later fills second at 58 (97). Lifting the bound after ROM credit cannot restore ARN's earlier 50 opportunity. ROM was not forced to 49 in the executable trace.

PUTJEA also contradicts the requested outcome under this exact law. PUT fills first at 9; JEA is therefore the unbounded second expression and fills at 64 (73). Withholding PUTJEA would require a different gate or a future-sequence oracle, neither authorized by this respecification.

The one-directional implementation has zero bound violations and its conservation checks pass, but both named checks fail. V50-R is `BLOCKED_V47_REMAINS_OPERATIVE`. The true-book gain cannot override the mechanism-bound failures or eleven lost completions. No deployment or live-cutover authority is created.

Two clean builds produced 36 byte-identical artifacts. Ten focused/inherited test programs passed. Forbidden access is zero for holdout, live, network-runtime, order, position, exit, settlement, DCA, and deployment surfaces.

Frozen report:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8e4191f40f1c38d43cb897ae10d6cc385f1012de/.claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811/REPORT.md

Attribution scorecard:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8e4191f40f1c38d43cb897ae10d6cc385f1012de/.claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811/ATTRIBUTION_SCORECARD.json

Named receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8e4191f40f1c38d43cb897ae10d6cc385f1012de/.claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811/NAMED_V50_RECEIPT.json

Recovery/cost receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8e4191f40f1c38d43cb897ae10d6cc385f1012de/.claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811/CAP_BOUND_RECOVERY_AND_COST_RECEIPT.json

Determinism receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8e4191f40f1c38d43cb897ae10d6cc385f1012de/.claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811/DETERMINISM_RECEIPT.json
