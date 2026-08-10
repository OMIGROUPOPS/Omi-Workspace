# Window-1 V47 Same-Tick Arm Addendum — 2026-08-10

## Ruling

V47 is **PASS / OPERATIVE** as the replay baseline. It adds one pipeline
correctness invariant to operative V45: when a deep-join level qualifies on a
receipt, that join-state update and the placement decision execute in the same
receipt-local call. Persistence, targets, the deep-gap guard, sibling-credit
release, pair cap, sanity bound, fill rulers, and the hard pre-bell edge are
unchanged. Aggregate gain is not required for this latency correctness fix;
zero bound regression is required and passed.

The executable whole-population footprint contains 1,380,318 qualification
receipts conserved into 3,180 mode-by-leg rows. V47 has zero positive scheduler
latency rows. It has 33,125 positive qualification-to-post rows, exactly equal
to V45; these are delays imposed by unchanged guards or laws and are expressly
not scheduler latency. All 1,608 market action streams are byte-identical and
no outcome changes.

V45 reproduces at 396 market-grade completed/under-par pairs, 1,936 cents
locked, -162 cents naked, +1,774 cents true book, and frontier
52/71/142/396. V47 is identical. Strict print-cross verification is also
identical at 331 completed pairs and frontier 36/50/99/331.

SURECH remains unfilled, as ordered. The `8877c2d5` SURECH render is an older
L4 archetype and not a frozen V45 decision trace. In the executable V45 trace,
the qualifying join updates already reach the placement decision on the same
receipt; V47 makes that invariant explicit rather than manufacturing a replay
gain. ARNROM, KIRSEK, KRUFER, BOSCOP, and PANFAL are unchanged and pass the
named zero-regression checks.

Two clean builds match byte-for-byte across all 35 regenerable artifacts.
Forbidden access is zero for holdout, live, network runtime, orders, positions,
exits, settlement, DCA, and deployment. This ruling authorizes no deployment
or live cutover.

## Frozen evidence

Report:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/REPORT.md

Attribution scorecard:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/ATTRIBUTION_SCORECARD.json

SEG_C receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/SEG_C_SAME_TICK_RECEIPT.json

Per-leg SEG_C footprint:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/SEG_C_SAME_TICK_FOOTPRINT.jsonl.gz

Named regressions:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/NAMED_V47_RECEIPT.json

Determinism:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/DETERMINISM_RECEIPT.json

Forbidden access:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34/.claude/window1_live_v4_replay/v47_same_tick_arm_20260810/FORBIDDEN_ACCESS_RECEIPT.json

Controlling SURECH evidence:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/8877c2d519c26b4e54f283ebebcee4933113d100/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/l4_archetype/SURECH_DECISION_MARKS.json

