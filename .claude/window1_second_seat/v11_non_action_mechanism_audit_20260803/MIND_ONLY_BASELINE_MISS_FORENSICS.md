# MIND-ONLY BASELINE COUNTER-GRADE + MISS FORENSICS — @8be7dfd8

License: LAW_INDEX @ 8be7dfd8, sha256 41784e6a… · L8 L11 L18 L20 L22 · corrections · F-VS-108 standard · F-VS-111/112 repairs · welds.
Seat: CC verification.

## 1 — Counter-grade

| item | verdict |
|---|---|
| Coherence, all four | REPRODUCED from the trace sentences: GIUBAR @1783833752.027 (2 coherent stages) · **URSPAL @1784004251 (16)** · **LAJSVA @1784007604 (3)** · DANPRA @1784332553 (14) — the F-VS-111 phase conditioning unlocked coherence on the two never-coherent games; all four stamps equal COHERENCE_TIMELINES |
| Zero-bypass fence | VERIFIED: 3 fills (GIU 70, URS 57, PRA 42), each entry == the rest standing at the fill, each rest LAYERED_COHERENT_ENVELOPE; independent-lane fills 0; gate may_complete=false holds; safety_floor_pass=false honest (no completes) |
| Deadline scoring table | RE-GRADED IN FULL (2,623 rows vs TARGET_PRINTS_5): **73/73 hits reproduce**; graded 1,488 vs receipt 1,491 (3 deadline-boundary ties); no-trade field shape (false vs null) only; **0 deadlines before emission** — F-VS-112's stale-deadline defect is repaired; every deadline derives fresh at its emission receipt |
| Four stories | Operator format holds: dual belief sentences with named bid/ask/book-receipt prices, fresh deadline receipts inline; TRADE_REPORT_FOUR carries no predicted/diagnostic number beside a fill price |
| Determinism | Two clean builds, 36 files, 0 differing, pre-receipt manifests equal (4a5d3fd0…); dual-belief OS unit test PASS |

## 2 — Miss forensics, row-traced (uncompleted legs)

Floors corrected (W1TT-C-001/002); envelope and rest read at the last stage at/before the floor print.

| leg | floor | envelope at floor moment | rest | verdict | the diverging input, row-cited |
|---|---|---|---|---|---|
| BAR | 27 @1783841801.305 | [25,31] COHERENT era, stage @1783841801.304 (DISAGREES at that stamp) | 25 | **envelope CONTAINED the floor; placement missed by 2¢** | deeper-candidate rule: ask − placement q50 4 → 25; the 27 print passed 2¢ above the rest |
| PAL | 39 @1784042066.596 | [32,37] | 32 | **envelope EXCLUDED the floor (top 37 < 39)** | phase-conditioned dip q50 18 at window_fraction 0.985 — the clamp (own_frac ÷ member_floor_frac, capped 1) serves the ARRIVED share of full travel as the REMAINING dip, so remaining dip GROWS toward window end instead of shrinking; at frac 0.985 remaining ≈ 0 would put the envelope top at own_low 40 and contain 39 |
| LAJ | 51 @1784060123.2 | [55,62] | 49 | **envelope migrated ABOVE the floor; the held rest sat below both** | prior q50 0 vs placement q50 33 at frac 0.735 (inconsistent conditioning inputs on one row); hold discipline froze 49 while the envelope moved up |
| SVA | 41 @1784020209.484 | [39,41] | 39 | **envelope CONTAINED the floor; placement missed by 2¢** | deeper-candidate: ask − q50 6 → 39; a 41 rest fills on the 41 print (d97f0682) |
| DAN | 59 @1784339306.8 | [56,59] COHERENT | 53 | contained; rest held 6¢ under | offer-0 game — the abstain is lawful (59+41=100); hold discipline kept an earlier deeper rest |

The exact step where cents were lost, by class: **(a) deeper-candidate placement under a contained floor** (BAR −2¢, SVA −2¢ — both pairs died on it); **(b) the inverted phase clamp** (PAL — arrived-travel served as remaining dip, envelope excluded the floor); **(c) envelope/hold divergence** (LAJ — rest below a migrated envelope). GIU filled 70 vs floor 66 (+4, gold boundary) but its pair died on (a).

## 3 — Prediction skill: 73/1,491 decomposed

- 95.1% of graded predictions sit BELOW the realized low by their own deadline (signed error median −11¢): the drift model predicts unreachably deep almost always.
- Conditioned rows (q50>0): 47/1,426 = 3.3% hit, median −11¢. Own-low rows (q50=0): 26/65 = **40.0%**, median −3¢ — the only systematic skill is own-low anchoring.
- By phase (emitted min-to-bell): ≥600: 55/159 = 34.6% · 300–599: 17/168 = 10.1% · 120–299: **1/1,160 = 0.1%** (1,156 of these are PAL churn emissions, all ~12¢ deep) · <120: 0/4.
- By leg: PRA 21/21 = 100% but signed error +19 — predictions ABOVE the realized low, trivially hit (not skill); LAJ 28/68 = 41%; URS 13/100; BAR 8/42; SVA 1/57; PAL 0/1,180; DAN 0/17.
- Statement: skill exists only where the prediction is anchored to the leg's own observed low, early in the window; the conditioned drift model is guessing everywhere else — mid-window it is wrong 999 times in 1,000, and its one perfect leg (PRA) is shallow-prediction auto-hit.

Functionable-standard state unchanged: 0 completes on this build (mind-only, fence on) — bed 0/4 this run; no 804.
