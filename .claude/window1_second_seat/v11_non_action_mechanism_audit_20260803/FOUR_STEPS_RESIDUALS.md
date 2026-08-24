# FOUR-NAMED-STEPS COUNTER-GRADE + RESIDUALS — @46b35969

License: LAW_INDEX @ 46b35969, sha256 41784e6a… · L8 L11 L18 L20 L22 · corrections · F-VS-108 · welds.
Seat: CC verification.

## 1 — Counter-grade

| item | verdict |
|---|---|
| URSPAL completion | VERIFIED: **99/Δ1** — URS 58 == rest (COHERENT set @1784031096; 57-print a4575e0c…) · PAL 41 == rest (COHERENT set @1784030408; 40-print b24bd093…); both trade-ids re-verified. NOTE: Δ1 sits BELOW URSPAL's own bed floor Δ3 — the gate's safety_floor_pass=false is honest; the completion worsened 98→99 while the machinery improved |
| BAR fill | NEW trade 4fa381b8… verified in prints.jsonl (27¢, @1783841801.417, 49 lots, true_print): rest 27 placed on the FIRST 27-print receipt (2898debe…, .304) at a COHERENT stage, filled by the second 27 print 113 ms later — gap to floor 0, gold |
| Bias table (−3) | re-graded in full: 1,517 graded / 429 hits vs receipt 1,519/431 (2 boundary ties); median −3 confirmed; hit rate 28% (was 4%) |
| Latency-0 | receipt consistent: BAR/GIU/LAJ/SVA first placement == first lawful current coherence receipt (latency 0); trace shows no stale-envelope-originated rest |
| Atomic replace | 3 atomic same-receipt replacements + 4 fail-loud-no-replacement; DANPRA cancel storm 15 → 1 receipts |
| Stories · determinism | dual-belief format with explicit INSUFFICIENT_EVIDENCE states and the total/arrived/remaining triplet verbatim; determinism 47 artifacts byte-identical ×2 |

## 2 — Residuals (rows only)

**(a) URSPAL Δ1 anatomy** (98→99): **PAL's cent moved** (40→41; URS unchanged at 58). The re-centered input: at the COHERENT placement @1784030408 (bid/ask 41/44, envelope [40,44]) the repaired remaining-dip q50 3 set floor-side = 44 − 3 = **41**, one tick above the prior build's bid-40 placement. Lawful floors offered 39+57 = 96/Δ4; paid 41 (+2) + 58 (+1) = 99/Δ1.

**(b) The −3 residual** is a NEW term, not F-VS-117's ask-side base (that base is gone — the belief target is now the CAUSAL OWN LOW, remaining-q50 not subtracted twice): PAL rows show predicted == the already-seen causal low (38/37…), and future-window lows sit ~3¢ above it — the **own-low-return assumption**. Per leg the error is now centered (−3…+4) except DAN −10.

**(c) LAJSVA under the fix**: coherence **RESTORED** — 30 coherent stages, first @1784007604 (the @8be7dfd8 stamp). Stage arithmetic at the floors:
- SVA floor 41 (prints @1784020201.83 and @1784020209.484): rest 39 stood COHERENT through @1784020196; **CANCEL_REST fired ON the first 41 print** (@1784020201.83, coherent stage, inconsistent-rest law); rest None through the second 41 print; **PLACE 41 @1784020210 — 0.5 s after the last 41 print**; 41 never printed again; SVA held 41 to bell unfilled. The miss = cancel-at-floor + one-receipt replacement gap (this cancel had no same-receipt replacement — a fail-loud case at the exact floor moment).
- LAJ floor 51 @1784060123.2: stage @1784059613 DISAGREES (gap 6 > spread 4), envelope [62,62] far above the floor, rest None — belief off, nothing lawfully stood.

**(d) GIUBAR — BAR vs its 27 floor**: envelope tightened [27,28] → [27,27] on the print receipt; placed 27 at .304, filled at .417 — the first gold-grade floor capture of the bed. **GIU regression**: placed 70 at first coherence @1783833752, **CANCELLED @1783833776 and never re-placed** — restless for the remaining 11 h; its 66 floor passed @1783869375 with rest None. The fail-loud-no-replacement path leaves a leg permanently silent; GIUBAR flipped from GIU-filled/BAR-missed to BAR-filled/GIU-missed.

**(e) DANPRA**: **no lawful-incomplete stamp exists** in the gate or the stories (searched: gate JSON, FOUR_STORIES, TRADE_REPORT_FOUR) — the state is real by arithmetic (offer 0: floors 59+41 = 100; DAN rests AT its floor 59; storm 15→1) but unstamped. Filed as a gap.

## Bed state

URSPAL completes with the machine on but at Δ1 < its Δ3 floor; GIUBAR partial (BAR gold, GIU silent); LAJSVA partial (SVA 0.5 s late at its floor); DANPRA lawful-incomplete, unstamped. Floors passed: 0. No 804.
