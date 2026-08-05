# Window-1 V29-R3 standing-floor release — 2026-08-05

V29-R3 is one additive overlay correction on frozen V29-R2. The arm-time
current own-book snapshot is evaluated before the preserved post-arm R2 path.
An ordinary ask at or below aim releases when spread is at most one cent, ask
dwell is at least ten seconds, and displayed ask size is at least five. Under
the explicit crossed-book ruling, `bid >= ask` at/below aim is maximal urgency:
dwell remains mandatory, while the ordinary spread and displayed-ask-size
gates are bypassed and the action releases at the standing ask. Aim remains
`min(99 - first_fill, own lawful live-book floor)`. No clock or audited close
is a policy input.

The R2 `OWN_ASK_NEVER_AT_OR_BELOW_AIM` defect cohort conserves exactly 128
legs. Three had a standing qualifying arm floor under R3; 125 were genuinely
not offered at/below aim at arm. Across all 371 target legs, disposition is 33
RELEASED_AND_FILLED, 200 INCUMBENT_FIRST, 138 NEVER_RELEASED, and zero
RELEASED_UNFILLED.

The required ARNROM|ARN regression flips. R2 recorded NEVER_RELEASED at aim
56. The frozen arm snapshot is `57/56`, ask dwell 519 seconds, displayed ask
size 2, at the arm timestamp 1783896551. R3 releases at 56 under crossed-book
maximal urgency and explicitly receipts the ordinary five-contract displayed
ask bypass. The earlier operator shorthand of four-hour dwell/five displayed
contracts is not reproduced by the frozen row and is not silently copied.

R3 changes 11 of 1,608 R2 leg streams; 1,597 remain semantic-hash identical.
It adds six completed and under-par pairs, but no new JOINT pair: JOINT remains
68. Strict carried pairs rise 148 to 152. Independent ceiling conversion moves
FN 7/29 to 8/29 and leaves carried 0/119.

Two clean builds produced 20 byte-identical payload artifacts with manifest
SHA-256 `a608379788aeb35254aeda774ca1ee799ed25ebf75e3665ef2fccbadc4801048`.
No holdout, live, network-runtime, order, position, exit, settlement, DCA,
Window-2, deployment, future floor, or clock input was accessed.

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/REPORT.md

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/SCORECARD.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/STANDING_ARM_CENSUS.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/ARNROM_ARN_REGRESSION_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/ARMED_LEG_DISPOSITION.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/DIFFERENTIAL_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/49f6501561c5d99a7f36c68ec41e0ea7250680e5/.claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/DETERMINISM_RECEIPT.json
