# ITERATION-3 REGRESSION FORENSICS — @97547b05

License: LAW_INDEX @ 97547b05, sha256 c7c72715… · L8 L11 L18 L20 L22.
Seat: CC verification. Data: IT3_REGRESSION_FORENSICS.json (same dir).
Scope: four games, read-only. No 804, sealed, live, or retune.

## 1 — Counter-grade

| item | verdict |
|---|---|
| Gate | pins equal (URSPAL Δ3, LAJSVA Δ6); self-stop honest; GIUBAR 0/2 (rests BAR 27 / GIU 63), URSPAL 0/2 (PAL 21 / URS 55), LAJSVA LAJ 53 @1784059613.617 + SVA rest 32 |
| Determinism | two passes byte-identical; 24/25 files match committed bytes; ARTIFACT_HASH_MANIFEST 14a02145… in receipt vs 8d05704c… committed (self-referential write order) |
| Split receipt | 346 rows: 320 CURRENT-BEHAVIOR-BYTE-EQUAL, 26 LIVE-WINDOW-SPLIT; "every split preserves pair budget" TRUE; every sibling yield from==to (26/26) — the split never moved a target |
| Retrieval receipt | every target names TARGET_BASIS; all lost-print movers are NEIGHBORS-GRADED; formula = round(ownLow − q50 remaining dip) (window1_v54_functionable_os.js:431-458, 509-520) |
| Case study v4 | panels A/B/C + both trade reports hash-match; SIDE_BY_SIDE listed 938 B / 9f960578… in CASE_STUDY_RECEIPT, committed 952 B / f933ede5… (manifest correct) |
| Vault of failed candidate | F-V53-087/088 banked same commit; candidate retained as LAJ-only, not accepted |
| Credit rule | 0 uncredited at/below-rest prints inside the corrected windows (residue all post W1TT-C-001 bell / L11 right edge 1784042040) |

## 2 — The lost prints, row-traced

Old rest = the level the prior machine stood at when the print came. it3 rest = it3's standing level at that exact timestamp. Mover = the derivation that set that level.

| print | rcpt | old rest (machine) | it3 rest | mover (stage ts, prev→new) | class | mover sentence, quoted |
|---|---|---|---|---|---|---|
| BAR 27 @1783841801.304 | 2898debe | 29 (it1/it2 → entry 27) | 25 | 1783834104, 29→25 | NEIGHBORS-GRADED | "Lineage target 29, uncapped lawful target 25 … ALLOCATION=CURRENT-BEHAVIOR-BYTE-EQUAL … REASON=no unique live evidenced window exists. ACTION=REPRICE_REST; TARGET_CENTS=25; ACTIVE_TARGET_BEFORE_CENTS=29." |
| GIU 69 @1783865397.812 | 37ebe8ad | 69 (it2) | 51 | 1783863733, 66→51 | NEIGHBORS-GRADED | "own TRUE_TRADE evidence low is 69 … NO_DIP_OBSERVED … remaining-dip q25/q50/q75 3/18/42 … Lineage target 69, uncapped lawful target 51 … ACTION=REPRICE_REST; TARGET_CENTS=51; ACTIVE_TARGET_BEFORE_CENTS=66." |
| GIU 66 @1783869375.227 | 924208a2 | 66 (it1) | 64 | 1783867786, 66→64 | NEIGHBORS-GRADED | "own-evidence target is 67 … Lineage target 69, uncapped lawful target 64 … post-only cap 66 … ACTION=REPRICE_REST; TARGET_CENTS=64; ACTIVE_TARGET_BEFORE_CENTS=66." (it3 had stood 66 for 6.32 h; left it 26 min before the 66 print) |
| URS 57 @1784032697.6 | a4575e0c | 57 (base/it1/it2) | 56 | 1784031347, 47→56 | NEIGHBORS-GRADED | "own-evidence target is 58 … Lineage target 57, uncapped lawful target 56 … ACTION=REPRICE_REST; TARGET_CENTS=56; ACTIVE_TARGET_BEFORE_CENTS=47." (1¢ under the print) |
| PAL 40 @1784041997.986 | b24bd093 | 40 (base/it2) | 22 | 1784031347, 24→22 | NEIGHBORS-GRADED | "own-evidence target is 40 … Lineage target 40, uncapped lawful target 22 … ACTION=REPRICE_REST; TARGET_CENTS=22; ACTIVE_TARGET_BEFORE_CENTS=24." |
| SVA 41 @1784020209.484 | 62c5acca | 41 (baseline) | 30 (6 eight seconds earlier) | 1784020205, 6→30; and 1784020201.83, 11→6 | NEIGHBORS-GRADED | "own TRUE_TRADE evidence low is 41 … NO_DIP_OBSERVED … q25/q50/q75 0/35/35 … own-evidence target is 41 … Lineage target 40, uncapped lawful target 6 … ACTION=REPRICE_REST; TARGET_CENTS=6; ACTIVE_TARGET_BEFORE_CENTS=11." |
| LAJ 54 @1784050973.062 | 16abd619 | 54 (it1/it2) | 44 | 1784039714, 54→44 | NEIGHBORS-GRADED | "own-evidence target is 54 … Lineage target 54, uncapped lawful target 44 … ACTION=REPRICE_REST; TARGET_CENTS=44; ACTIVE_TARGET_BEFORE_CENTS=54." |
| LAJ 53 @1784052830.356 | 8c5eeb51 | 53 (baseline) | 49 | 1784052714, 44→49 | NEIGHBORS-GRADED | "Lineage target 53, uncapped lawful target 49 … ACTION=REPRICE_REST; TARGET_CENTS=49; ACTIVE_TARGET_BEFORE_CENTS=44." |

Reading: 8/8 movers are the graded-neighbor re-derivation. 0/8 are the allocation yielding (no LIVE-WINDOW-SPLIT row ever changed a sibling level: from==to on all 26). 0/8 are churn — each move is one REPRICE_REST to a q50-derived level that then stood 2–10 h. In every row the lineage target (= the old machine's rest) was AT the print and the lower "uncapped lawful target" won.

## 3 — Movement census

Reprices = target changes after first placement; standing hours per level from formation end to fill or bell (truth-table bell; corrected bells for fills). Depth = time-weighted (best bid − rest) using the baseline trace's per-receipt book; "at bid" = share of placed time with rest ≥ best bid.

| leg | machine | stages | reprices | levels | fill | at-bid share | mean bid−rest ¢ | dominant standing (h) |
|---|---|---|---|---|---|---|---|---|
| BAR | baseline | — | 258 | 17 | 21 (print 18 @1783875779; post-bell) | 0.739 | 0.56 | 29:3.45 30:3.06 26:2.75 |
| BAR | it1 | 16 | 1 | 2 | 27 @1783841801 | 1.000 | −0.20 | 29:2.24 |
| BAR | it2 | 16 | 1 | 2 | 27 @1783841801 | 0.810 | 1.13 | 29:2.24 |
| BAR | it3 | 53 | 11 | 7 | — | 0.039 | 4.44 | 21:3.09 27:2.91 25:2.20 |
| GIU | baseline | — | 7 | 8 | 69 @1783841972 | 1.000 | 0.00 | 68:2.28 |
| GIU | it1 | 16 | 4 | 2 | 66 @1783869375 | 0.050 | 2.02 | 67:5.24 66:5.18 |
| GIU | it2 | 16 | 3 | 4 | 69 @1783865397 | 0.702 | 1.08 | 69:6.49 67:2.24 |
| GIU | it3 | 53 | 10 | 9 | — | 0.004 | 7.41 | 66:6.32 52:2.14 64:1.79 |
| URS | baseline | — | 186 | 11 | 57 @1784032697 | 0.998 | 0.00 | 60:3.26 57:1.27 |
| URS | it1 | 16 | 4 | 4 | 57 @1784032697 | 0.787 | −0.92 | 60:6.04 |
| URS | it2 | 16 | 6 | 6 | 57 @1784032697 | 0.328 | 14.92 | 29:4.07 58:1.97 57:1.60 |
| URS | it3 | 29 | 15 | 11 | — | 0.000 | 11.67 | 49:3.04 47:2.84 56:1.95 |
| PAL | baseline | — | 13,110 | 16 | 40 @1784041997 | 0.979 | 0.04 | 35:4.07 40:3.39 |
| PAL | it1 | 16 | 6 | 4 | — | 0.496 | 1.24 | 36:7.98 |
| PAL | it2 | 16 | 4 | 5 | 40 @1784041997 | 0.765 | −0.05 | 37:4.24 40:2.96 |
| PAL | it3 | 29 | 14 | 10 | — | 0.063 | 13.58 | 22:2.99 21:2.19 27:1.97 |
| LAJ | baseline | — | 44 | 9 | 53 @1784052830 | 1.000 | 0.00 | 53:4.99 54:3.98 |
| LAJ | it1 | 21 | 6 | 5 | 54 @1784050973 | 0.716 | −0.42 | 57:4.77 54:3.13 |
| LAJ | it2 | 21 | 5 | 6 | 54 @1784050973 | 0.700 | 2.37 | 54:3.26 53:2.87 |
| LAJ | it3 | 38 | 14 | 11 | 53 @1784059613 | 0.009 | 16.50 | 44:5.92 28:3.27 24:2.44 |
| SVA | baseline | — | 10 | 5 | 41 @1784020209 | 1.000 | 0.00 | 37:2.53 |
| SVA | it1 | 21 | 9 | 4 | — | 0.209 | 0.33 | 40:17.91 |
| SVA | it2 | 21 | 3 | 4 | — | 0.757 | 1.76 | 41:13.75 |
| SVA | it3 | 38 | 15 | 10 | — | 0.037 | 15.29 | 32:10.47 6:4.56 35:1.92 |
| DAN | baseline | — | 6 | 3 | — | 0.688 | 0.39 | 58:7.74 |
| DAN | it1 | 19 | 2 | 3 | — | 0.000 | 2.76 | 56:10.03 |
| DAN | it2 | 20 | 1 | 2 | — | 0.000 | 11.88 | 56:6.57 33:4.68 |
| DAN | it3 | 59 | 7 | 6 | — | 0.000 | 14.46 | 52:4.17 47:2.96 |
| PRA | baseline | — | 104 | 31 | — (40 post-bell) | 1.000 | 0.00 | 40:6.08 |
| PRA | it1 | 19 | 1 | 2 | — | 0.540 | 0.99 | 40:10.03 |
| PRA | it2 | 20 | 0 | 1 | 43 @1784336963 | 1.000 | −1.10 | 43:1.23 |
| PRA | it3 | 59 | 5 | 4 | 42 @1784341326 | 0.503 | 2.86 | 36:1.21 42:1.14 |

Hypothesis measured: MOVEMENT is real but not the mechanism. it3 reprices 2–5× more than it1/it2 (stages 53/29/38/59 vs 16/16/21/20 — the graded read re-fires on every neighbor-weight change), yet the baseline tracking reflex reprices 10–1,000× more still (PAL 13,110) and fills, because it moves WITH the bid (at-bid 0.74–1.00, mean gap ≤0.56¢). it3 moves AWAY from the bid: at-bid share 0.000–0.063 on all six lost legs, mean 4–16¢ under the bid. it1/it2 sit between (0.2–0.8). STANDING is the mechanism: every it3 lost leg stood 2–10 h at a level the tape never reached.

## 4 — Mechanism and defect classes

- REGRESSION MECHANISM — OWN-LOW-MINUS-q50: target = round(ownLow − q50). ownLow is this leg's own running low, so the rest is BELOW its own best print by construction and ratchets down with every new low; it rises only when q50 shrinks. Same class as V52r's STOOD_TOO_DEEP (1c9419a0), now at 4–16¢ instead of 1–3¢. Visible at SVA 1784020201.83: the leg's own TRUE_TRADE low 41 arrives (= the fill) and the rest moves 11→6.
- ALLOCATION DEFECT A — INERT SPLIT: live window = ask === target+1; with target = ownLow − q50 this holds on 13/346 rows, and on all 26 split rows the sibling yield is from==to. The split's stated law ("the sibling plan yields") never executed a yield.
- ALLOCATION DEFECT B — STALE-PRIOR-OVER-FRESH: siblingPlan = siblingPrior ?? derived. At SVA 1784036624.369 the fresh derivation said 38 (q50 3); the split carried the stale prior 6: "uncapped lawful target 38 … SIBLING_YIELD_FROM_CENTS=6; SIBLING_YIELD_TO_CENTS=6 … ACTION=HOLD_REST; TARGET_CENTS=6." SVA stood at 6 for 4.56 h.
- RECEIPT DRIFT (minor, L20/L22 hygiene): two receipts hash pre-final bytes (section 1).

No repair ordered; measurement only.
