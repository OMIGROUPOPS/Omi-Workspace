# THREE-NAMED-STEPS COUNTER-GRADE + RESIDUAL FORENSICS — @ae2137b6

License: LAW_INDEX @ ae2137b6, sha256 41784e6a… · L8 L11 L18 L20 L22 · corrections · F-VS-108 · welds.
Citation note: the dispatch's "F-VS-117..120" does not resolve in the CC ledger (next-free at receipt was F-VS-116); read as the @ae2137b6 F-V53 repair bank.
Seat: CC verification.

## 1 — Counter-grade

| item | verdict |
|---|---|
| URSPAL mind-only completion | VERIFIED: URS entry 58 == rest 58 (set @1784031271 at a COHERENT stage) filled by the 57-print a4575e0c… — rest-priced honest, pays 58; PAL entry 40 == rest 40 (set @1784038360.853, DISAGREES stage, prior coherence @1784016225) filled by the 40-print b24bd093…; both prints already trade-id-verified; **98/Δ2, first mind-only completion** |
| Coherence at placements | prior-coherence law holds on all three fills (GIU 66 set @1783867224 after GIUBAR's 1783833752.027) |
| Bias table | re-graded in full: 2,680 rows, my 1,544 graded / 65 hits vs receipt 1,546/66 (2 boundary ties); **median signed error −8 confirmed** (was −11) |
| Deep-edge zero | VERIFIED: 0 deeper-candidate rows in 2,571 envelope rows; rule is CONDITIONED_REMAINING_DIP_Q50_FLOOR_SIDE_ONLY, with ZERO_REMAINING_DIP_USES_EVIDENCED_BID |
| The 22 rest resolutions | behaviorally corroborated: 685 migration rows banked; 16 leg-cancels / 15 distinct FAIL_LOUD_CANCEL_INCONSISTENT_RESTS events (URS 13, DAN 2, PRA 1) vs gate's 14 (±1 counting drift); the exact 22 active-inconsistent rows are not independently derivable from the receipt's fields — granularity note, not a fault |
| Stories · determinism | dual-belief format throughout (28 belief sentences, no predicted number beside a fill price); determinism PASS_BYTE_IDENTICAL_X2 |

## 2 — Residual forensics (rows only)

**(a) URSPAL's Δ2 anatomy** (lawful floors 39+57 = 96/Δ4; paid 40+58 = 98/Δ2):
- URS +1: at the COHERENT placement @1784031271 the envelope was [58,58] with live bid/ask 57/59 and remaining-dip q50 = 0 → ZERO_REMAINING_DIP_USES_EVIDENCED_BID projected the bid **up into the envelope**: 57 → 58. The conditioned input that paid the cent: **the belief envelope low 58 sitting 1¢ above the live bid**, clamping the projection. The 57 floor print filled the 58 rest one stage later.
- PAL +1: placement @1784038360.853, remaining-dip q50 = 0 → stand at the evidenced bid 40 (envelope [37,44]). The 39 floor printed @1784042066.596 — 69 s AFTER the 40-fill @1784041997.986. Input: the repaired clamp correctly says ~0 remaining at frac ≈0.9; the cent is the residual of standing at the touch one tick above a floor that arrived later. No defect row.

**(b) The −8 bias, by input**: with the repaired remaining = total − arrived (term medians: total 16 / arrived 9 / remaining 6), signed error by remaining-dip bucket: rem 1–5 → −7, rem 6–12 → −9, rem 13+ → −20, rem=0 → 0; **adding the remaining-dip q50 back re-centers every bucket (−3/−3/+3)** — the term that still drags deep is the remaining-dip subtraction itself, overstated roughly by its own size; a ~−3¢ residual remains from the ask-side base (ask − q50 starts above the bid). By leg the drag concentrates where totals are travel-scale: LAJ −20, DAN −20, GIU −18, SVA −17, vs URS −2, PRA 0, BAR −4.

**(c) LAJSVA and DANPRA silence, step-named**:
- LAJSVA (both legs, 77 stages each, all HOLD_REST/None, ENVELOPE=null at both floor moments): **NO PLACEMENT TRIGGER — coherence never formed in this build (ever_coherent=false)**, and the mind-only fence lawfully leaves nothing standing. This is a REGRESSION vs @8be7dfd8, where LAJSVA cohered @1784007604 (3 stages): the F-VS-114(b) remaining-dip repair moved the predictions and un-cohered LAJSVA (URSPAL's first coherence also moved 1784004251 → 1784016225). The repair traded LAJSVA's coherence for URSPAL's completion.
- DANPRA: DAN's floor 59 @1784339306.8 passed at a DISAGREES stage with ENVELOPE=null (coherence only arrived @1784341326, after the floor) — no rest could stand: no-trigger, lawful for the offer-0 game. PRA's floor 41 @1784342554 passed with target None although PRA was COHERENT with envelope [43,43] from @1784341326 — **placement did not fire at the first coherent stage** (PLACE came only @1784359388 at 40); that rest and DAN's two 59-rests were then killed by FAIL_LOUD_CANCEL_INCONSISTENT_RESTS (@1784360967, @1784373056). Steps: late trigger → fail-loud cancel; abstain remains lawful (59+41 = 100).

Functionable-standard state: URSPAL is the first completion with the machine on (coherent belief priced the winning rests); bed = 1 complete + DANPRA lawful abstain + GIUBAR partial (BAR rest 30 vs floor 27) + LAJSVA silent = still short of 4/4; no 804.
