# LAYERED BUILD CERTIFICATION — @8ac76488

License: LAW_INDEX @ 8ac76488, sha256 41784e6a… · L8 L11 L18 L20 L22 · corrections · formation law · welds · F-VS-101/102/103.
Seat: CC verification. Verdict: **CERTIFIED WITH TWO FAULTS — the bed-pass claim does not survive fill-price pricing on GIUBAR.**

## 1 — Gate, recomputed under corrections

| game | fills (trade-id verified vs fit-local prints.jsonl) | timing vs corrected span | line |
|---|---|---|---|
| GIUBAR | BAR 27 @1783841801.304 (2898debe…, 242 lots) · GIU 66 @1783869375.227 (924208a2…) | both < W1TT-C-001 bell 1783874300 | recorded 93/Δ7 — see fault A |
| URSPAL | URS 57 @1784032697.601 (a4575e0c…) · PAL 40 @1784041997.986 (b24bd093…) | both < W1TT-C-002 bell 1784042247 | **97/Δ3 PASS** (= floor Δ3) |
| LAJSVA | SVA 41 @1784020209.484 (d97f0682…) · LAJ 53 @1784052830.356 (8c5eeb51…) | both < bell 1784078400 | **94/Δ6 PASS** (= floor Δ6) |
| DANPRA | none (rests DAN 55 / PRA 38) | offer 0 game | NEITHER — no floor required |

All six fills verified by trade_id: price, timestamp (±10 ms), true_print=true, kalshi_public_trade. Entry == standing rest on **five of six** legs.

**FAULT A — GIUBAR fill pricing.** BAR's only lifecycle is HOLD → PLACE_REST **29** @1783831858 (LAYERED_COHERENT_ENVELOPE); the rest stood at 29 at the fill moment, and the build credits entry **27** = the print price. A resting 29 bid cannot execute at 27; the truth table's own us_fill convention prices the fill at the rest (W1TT-C-001 before-block: BAR us_fill 21 = rest, print 18). Rest-priced, GIUBAR = 29+66 = **95/Δ5 < required Δ7** → safety-floor break → the gate's `safety_floor_pass: true` and F-V53-120's "bed passes" depend on print-pricing a maker fill 2¢ through its own limit. (Same convention existed in it1/it2 fills; here it is decisive for the first time.)

## 2 — The independent lane (the pointed question)

Row-traced all four URSPAL/LAJSVA fill lifecycles (1,070 change-points): every one carries `target_basis: INDEPENDENT_LINEAGE_V3_OWN_TAPE`, `reflex_rung_used: false` everywhere, `lineage_depth_fallback_used: false` everywhere — no legacy rung fired under a license label. Against the raw tape, 733/1,075 change-point targets equal the tape bid at that second (the off-by-ones are the stage firing on the bid change; the cited `live_bid_cents` is the pre-change row). The rests track the **evidenced touch at the touch, not bid−1**.

**PAL's PLACE_REST 33 @1784001495 (COHERENCE=DISAGREES):** licensed by (i) the live bid 33 on `URSPAL-PAL.csv.gz#row-6` (`joint_depth_license: EVIDENCED_TOUCH`, receipts to that row), (ii) V3 cell ATP_CHALL|33 consulted and **refusing** depth (`map_depth_license: false`, chosen_depth 0), (iii) MACRO prior INTERIM_UP_TRAVEL informing, not gating; allocation `JOINT_TARGET_ALREADY_UNDER_PAR` (33+57=90). DISAGREES blocks belief-priced rests only — the independent lane lawfully places at the touch. Residue: 16 transient PAL moments (≈1784024309–24499) where the evidenced touch lagged a fast-rising bid by 2–5¢ under the EVIDENCED_TOUCH label — conservative direction, noted.

## 3 — Sentence provenance (30 drawn)

30/30 sentence==action. Store citations, map cells, and neighbor receipts resolve. **FAULT B — the belief `<price>` field:** it is `drift.current` (the evidenced reader level), not the book at that timestamp. On the draw it deviates from the contemporaneous mid by median 0.75¢ but **>1¢ on 42%, max 3.5¢**; the flagged early values are worse: "believes PAL at 64¢" at formation end is the pre-settle wide mid (row-6: 33/95) while the settled tape at that second reads 33/43 (mid 38); URS "64" persists across 1784024368–26436 while the true mid runs 53.5–56.5; PRA "60" vs true 42. Values resolve to real cited rows, but an unformed-era book value poses as the formation-end price — F-VS-101's `<price>` X is not "from actual rows at that timestamp" on these rows. Placement is unaffected (targets use the live bid); the fault is the belief sentence's price field.

## 4 — Coherence timelines

Verified from the trace sentences themselves (COHERENCE/MIRROR_GAP/SPREAD_BOUND): GIUBAR first COHERENT @1783833752.027 (gap 13 = spread 13, exactly at the bound; 2 coherent stages) — matches COHERENCE_TIMELINES and F-VS-103. DANPRA first @1784332592 (gap 7 ≤ spread 12; 11 stages). URSPAL: 0 coherent in 1,183 stages, best gap 17 vs spread 12; LAJSVA: 0 in 33, best gap 24. **Not a tolerance artifact**: under the as-filed bound (gap ≤ spread ≤ 20) nothing passes; even a flat-20 tolerance would admit only 2 URSPAL stages and 0 LAJSVA stages. Never-coherence is honest.

## Verdict

CERTIFIED: the independent lane (real licenses, no legacy rung), the URSPAL 97/Δ3 and LAJSVA 94/Δ6 lines, all six fills as true prints, the coherence machinery and its negative results, formation/crossed-book law (0 violations in trace).
FAULTED as the bed-passing version: (A) GIUBAR's Δ7 exists only under print-priced maker fills — rest-priced it is 95/Δ5 and the gate should have self-stopped; (B) the belief-sentence price field carries evidenced-reader values that deviate from the book at the stamp, including a pre-settle mid at formation. The version stands as the best line yet (2 valid completes + the first honest GIUBAR pair since the corrections) but is NOT certified as bed-passing until fill pricing is adjudicated rest-priced or the operator rules print-pricing lawful.
