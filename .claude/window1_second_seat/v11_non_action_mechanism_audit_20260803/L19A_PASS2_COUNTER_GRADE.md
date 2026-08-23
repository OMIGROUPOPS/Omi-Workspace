# L19a PASS-2 COUNTER-GRADE + RULER ADJUDICATION — @42ebb620 (tip 85c2fa17)

License: LAW_INDEX @ 42ebb620, sha256 c7c72715… · L8 L11 L18 L20 L22 · honest ruler · corrections law · process-first.
Seat: CC verification. Data: L19A_PASS2_COUNTER_GRADE.json · DIVE_QUEUE_V2.json (sha256 cf2d1669…).
Scope: read-only; no 804 run, no sealed read, no retune.

## 1 — The impossibles, adjudicated

| line | what it is | under corrections |
|---|---|---|
| GIUBAR Δ11 (BAR 30 @1783874430, GIU 59 @1783876264) | FOUR_GAME_TRIPWIRE raw `completed` (report_only_inside_tune=true) | both fills POST_BELL (W1TT-C-001 bell 1783874300) → NEITHER |
| DANPRA Δ3 (DAN 57 @1784373323, PRA 40 @1784374172) | raw line | both after span_end 1784372160 → NEITHER; not OFFERED_UNDER_PAR (59+41 = 100, offer 0) |
| URSPAL Δ2 (PAL 33 @1784042264, URS 65 @1784042719) | raw line | both after W1TT-C-002 bell 1784042247 → NEITHER |
| LAJSVA Δ3 (LAJ 49 @1784078830, SVA 48 @1784060451) | raw line | LAJ post-bell → PARTIAL (SVA only) |

Grader: `build_window1_v54_functionable_v6.js` loadGroundTruth (lines 274–304) applies W1TT-C-001/002 to the truth rows before `score()`. Independent recompute: uncorrected spans give 39 / 134¢ / Δ3.436 (GIUBAR in); corrected give **38 / 123¢ / Δ3.237 = the SCORECARD**. Verdict: NOT a grader defect — a REPORT defect: the tripwire prints raw completes with no honest stamp. Four-game honest: 0 completes.

## 2 — Counter-grade

| item | verdict |
|---|---|
| Sealed | 0 sealed/holdout strings in SOURCE_RECEIPTS; same stores as pass 1 plus pass-1 SCORECARD; sealed 171 ∩ Foundation 9,000 = 0; ∩ specialist records = 0; dev 804 ∩ library = 0 |
| Determinism | two clean builds PASS; 9/10 committed artifacts equal the receipt; REPORT.md receipt 603d3f65… vs committed+manifest 189a1e0a… (rewritten after the receipt — pass-1 class) |
| Custody | sentence archive 9e796ab7… present, 75,525,710 B, 61,400 rows |
| Specialist records | 18,000 committed (8.6 MB, under L22); **18,000/18,000 reproduce** from the custodied Foundation library (remaining_depth = observed_low − low; floor_fraction; receipt; category). floor_fraction = (floor−formation_end)/(bell−formation_end) holds 16,126/18,000; 1,874 clamped to 0 where the floor precedes formation end (clamp unstated). The library's own tape (droplet per_minute parquet) is external; F-VS-067's 8-leg check stands, not re-runnable locally |
| Leave-self-out | dev 804 ∩ library = 0 → "leave-self-out on every decision" is vacuous for the dev population; the pass-1 gap (unreceipted fit population) does not repeat — the vote inputs are the committed records |
| Fill census (legs) | valid 335 · **post-bell 980** · none 265 · pre-formation 9 · unknown-span 19 |
| Low rests | 12,023 rows rest ≤2¢ under reason FORMATION_NOT_COMPLETE (1,599 PLACE_REST); 1,735 ≤2¢ under NEIGHBOR_VOTED; 9 entries ≤3¢ |

### Validation decomposition from the sentences

| set | n | basis that priced the rest | touch | gap (ref − rest) | pass-2 fill class |
|---|---:|---|---|---|---|
| LOST recovered | 5 | OWN_TAPE_PRESENCE_AT_TOUCH 10/10 | AT_BID 7 · −1¢ 3 | median 0, 100% at/above | VALID 10 |
| LOST still lost | 253 | DERIVED_TIMING_DEPTH 387 · OWN_TAPE 114 · none 5 | 3¢ 55 · 4¢ 51 · 2¢ 42 · 5¢ 41 · 6¢ 37 · AT 31 · 1¢ 30 · 8¢ 28 | **median 6¢, mean 8.27; 7% at/above** (pass 1: 2¢, 12.6%) | POST_BELL 319 · VALID 93 · NONE 93 |
| GAINED retained | 6 | OWN_TAPE 11 · TIMING 1 | AT_BID 6 | median 0, 100% | VALID 12 |
| GAINED surrendered | 18 | OWN_TAPE 24 · TIMING 12 | AT 7 · 3¢ 6 · 4¢ 5 | median 2¢; 31% at/above | POST_BELL 19 · VALID 13 · NONE 4 |

Reading: every win is OWN_TAPE_PRESENCE_AT_TOUCH at the bid; every loss is DERIVED_TIMING_DEPTH standing 3–8¢ under the prior fill. Pass 2 stands deeper than pass 1 (6¢ vs 2¢ under the reference), hence 980 post-bell legs and 38 < 77.

## 3 — Gates-inside

PASS1_LOST_GAINED_VALIDATION.json: `executed_before_full_804: true`; `pre_stated_direction: {recovered_any_lost: true, surrendered_no_gained: false}` → the pre-stated direction FAILED (18/24 surrendered) and the full 804 executed anyway; TUNE_DISPOSITION carries `pre_stated_direction_pass: false` beside the full-804 numbers. The dispatch wording made the validation a report, not a gate — attribution to the dispatch; the OS build executed as worded. Filed F-VS-090.

## 4 — Dive queue v2

DIVE_QUEUE_V2.json: 642 offered games pass 2 does not validly complete (680 − 38). Per leg: rest standing at the truth floor print, basis, touch, gap = floor − rest, fill class; game mechanism = worst leg. Ranked category → mechanism frequency → offer margin.

| category | games | top mechanisms |
|---|---:|---|
| ATP_CHALL | 307 | TIMING ≥10¢ under floor 149 · TIMING 6¢ 25 · OWN_TAPE ≥10¢ 24 · TIMING 7¢ 18 |
| ATP_MAIN | 114 | TIMING ≥10¢ 53 · OWN_TAPE ≥10¢ 8 · TIMING 4¢ 7 |
| WTA_CHALL | 93 | TIMING ≥10¢ 56 · TIMING 9¢ 8 · TIMING 7¢ 6 |
| WTA_MAIN | 128 | TIMING ≥10¢ 55 · TIMING 8¢ 9 · TIMING 3¢/5¢/6¢ 7 each |
| ALL | 642 | DERIVED_TIMING_DEPTH ≥10¢ under floor **313**; floor reached but not validly held 4 |

Supersedes the pass-1 queue (F-VS-087). Losses weighted: 253 of the 642 are pass-1 LOST games still lost (ATP_CHALL 115 · WTA_MAIN 56 · WTA_CHALL 45 · ATP_MAIN 37).
