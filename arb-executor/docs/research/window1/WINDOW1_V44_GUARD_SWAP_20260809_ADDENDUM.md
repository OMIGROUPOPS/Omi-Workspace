# V44 Guard Swap — Blocked / Not Operative — 2026-08-09

V44 was built on operative V43 (`01a58334e90acffd4bb0fb17b6ceed17c4f51bbd`) with exactly the ordered swap: the T=10 deep-gap feasibility guard was removed, and a three-cent dry-sibling withhold was added. Arm-at-first-evidence, one-cent loosening, maker-only fills, sanity bound, lazy-leg-1 coupling, pair cap, no-clock law, and the hard pre-bell edge remain inherited.

The controlling recalibration (`b503e4edc2184e8958c97980c2e1769a077bfdd9`) described deleting a fill while the sibling was dry. That post-hoc operation is not exchange-executable: a resting order cannot refuse an opposing fill. V44 therefore implements the only lawful form of the order: the rest is withheld or cancelled before it can fill and is placed on the first receipt that establishes sibling union flow within three cents of a causally observed lawful sibling rest level. No missed receipt is retro-credited. A hard invariant stops the build if a live rest reaches a fill while its sibling is still dry.

The executable four-row attribution is:

| row | completed / under par | locked cents | naked cents | true book cents | frontier <=93 / <=95 / <=97 / <100 | strict |
|---|---:|---:|---:|---:|---:|---:|
| V43 baseline | 395 | 1,910 | -162 | 1,748 | 51 / 70 / 141 / 395 | 331 |
| guard removed only | 393 | 1,905 | -315 | 1,590 | 53 / 72 / 142 / 393 | 330 |
| dry sibling only | 375 | 1,146 | -191 | 955 | 28 / 43 / 101 / 375 | 319 |
| V44 combined | 375 | 1,077 | -206 | 871 | 27 / 41 / 98 / 375 | 319 |

V43 reproduces exactly. The analysis-seat projection of 415 completed and +2,165 cents is retained as `ANALYTICAL_ESTIMATE` and is not emitted as executable truth. The causal dry-sibling rest withhold touches 1,603 legs, starts 1,603 withholding episodes, and later lifts 1,585 of them. Delaying placement removes lawful early fills and does not repair the naked book.

V44 fails every numeric bar: 375 is below the 395 completion floor, -206 is below the zero naked-book floor, and +871 is below the strict +1,748 true-book floor. PENTHA and SHEOLI remain incomplete; PUTJEA becomes naked on JEA rather than the required dry skip; KIRSEK is 31 rather than <=24; ARNROM is 97 rather than <=89. KRUFER 96 and BOSCOP 80 pass their at-or-better checks. No value was forced.

Two clean builds compared 37 pre-receipt artifacts byte-for-byte with zero mismatches. The focused V44 source test and package test pass, the artifact manifest verifies, and forbidden access is zero for holdout, live, network-runtime, orders, positions, exits, settlement, DCA, and deployment.

Ruling: `V44_GUARD_SWAP = BLOCKED_NOT_OPERATIVE`. V43 remains operative at 395 completed / +1,748 cents true book. The standalone T=10 calibration is `COMPOSITION_STALE`, but removing it without a different executable naked-book mechanism is not ratified. The dry-sibling analytical deletion is also not ratified as machine behavior because it cannot be realized without changing order residency.

Controlling analytical receipts:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/b503e4edc2184e8958c97980c2e1769a077bfdd9/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V43_COMPOSITION_RECALIBRATION.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/639e8b19e9e6699f6c99bcd48a9557273234cd93/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V43_RESIDUAL_MISS_GEOMETRY.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/645e035bce12a4dcaf4cb7f10a3767fa898652a0/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAP_UNFEASIBLE_CENSUS.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a30f5ccdf0c4233b30bf4017af48707f0db8ff1f/.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V41_FULL_BOOK_PNL.json
