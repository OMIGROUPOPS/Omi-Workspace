# STRIKE-THREE KNIFE — THE ONE-BEAT-LATE CLASS — @9870a7fa (+ @7889d9e1)

License: LAW_INDEX read @9870a7fa, sha256 41784e6a… (verified this seat).
Builds: `window1: bank classifier floor-print wake self-stop` (@7889d9e1, package
v54_classifier_floor_print_wake_20260826) · `research(window1): bank directional floor admission
self-stop` (@9870a7fa, package v54_directional_floor_admission_20260826).
Method: three lanes recomputing from both traces (hash-bound to their manifests), prints, tapes,
code, and the graded prediction corpus. Filed: F-VS-238 … F-VS-241.
Ledger discipline holds a fifth time (BC-055..062; zero F-VS rows; my ledger blob-identical
across all three commits).

---

## 1 — VERIFICATION (F-VS-238)

Every recomputable builder claim reproduced exactly:
- **Wake @7889d9e1:** 62/62 floor-print decision instants — independently re-derived from the raw
  tape as bell-cut running-low prefixes; GIU's three 66 receipts each fired (terminal credited-pair
  reads). Classifier equality recomputed object-by-object on all 2,584 live derivations: 0
  mismatches (credited-stream equality is true-by-construction; "zero scheduler latency" is a code
  property, not a measurement). **GIU-69 admission was real and FILLED at 69** — the 2¢-descent ==
  2¢-excursion tie admits it; banked honestly in the BC row, though a stale code comment still
  claims the refusal works.
- **Directional @9870a7fa:** the admission census — 5,975 true-trade-low evaluations, 512
  admitted / 5,463 refused — re-executed over the full population from each row's own fields:
  0 predicate violations. GIU 69 refused (path high 68, descent OPEN) on all 43 rows; GIU 66
  admitted with exact path support on all 135. **The gate is genuinely per-leg-state-driven**
  (the leg's own criterion and descent state; no global dial) — the F-VS-236 dispatch, answered.
  Unclaimed fact: all 512 admissions came through exact-path-support; the observed-descent branch
  never decided. The removed one-tick adjacency exception is absent from the decisive run and
  preserved in custody.
- **Fills:** 6 @wake (BAR 27, GIU 69, URS 58, PAL 40, SVA 41, LAJ 54) and 5 @directional (BAR 27,
  URS 58, SVA 41, LAJ 54, **PRA 41**) — all resolved by trade id, entry == prior standing rest.
  Determinism X2 both; gates self-stop on the tripwire alone; the BC-060 conduct residuals all
  reproduce.
- **Custody: the F-VS-234 gap PARTIALLY closed.** Both recovered attempt sets exist with exact
  file counts and bytes (47/1,510,329,877 · 61/1,616,112,281); 10/10 key-file hashes verified;
  the void mechanical attempt and the adjacency-defect output are both preserved. **But the two
  aggregate digests (de5c28e2, 4cd49c0c) are not independently derivable** — ~20 candidate
  serializations tried, no formula or per-file manifest exists anywhere in the tree. The binding
  is self-referential until the builder commits the digest formula.

---

## 2 — THE TIMING TABLE (F-VS-239)

Admission is print-gated: only a true-trade-low print receipt can bind a floor (os:287), the
directional check refuses prints above the open descent path (os:307), and under F-VS-107 the
admission evidence IS the first floor print — **the first print is structurally unseatable; a leg
can only be paid by a later floor print.** Post-only and authority-derivation then eat window
downstream of the wake (which solved detection only — no seat time moved between the two builds
except where the predicate itself changed).

| leg | floor | seat time (rest at floor) | vs floor prints (seat − print) | window | result |
|---|---|---|---|---|---|
| BAR | 27 | 1783841801.305 — inside p1's own decision stage | p1 0.000 (unfillable) · p2 **−0.112** | 0.112 s | **FILLED 27 — converted** |
| SVA | 41 | 1784020209.000006 | p1 +7.170 · p2/p3 **−0.484** | 7.654 s | **FILLED 41 — converted, 0.484 s to spare** (post-only ate 7.170 s) |
| PRA | 41 | 1784359387.000002 | p1..p8 late · p9 **−9,862.288** | 29,561.7 s (12 prints) | **FILLED 41 — converted** |
| GIU | 66 | 1783873822.000001 | +4,446.8 / +2,810.0 / **+1,210.5** | 1,636.8 / 3,236.3 s | **missed** — authority still derived 55 at p2/p3; 66 produced 1,210.5 s after the last print |
| DAN | 59 | never | all three prints REFUSED (path high 58, OPEN) | 1,474.4 / 2,960.3 s | no seat (wake admitted late: +5,007.9 s — miss either way) |
| URS | 57 | never at 57 in-window (last 57-seat ended 9,447.6 s before the print) | single print = the fill trigger | **width 0** | **structurally uncapturable at 57** — filled at 58 |
| PAL | 39 | 1784042066.596 — **seat ts == print ts** | +0.000 exactly | **width 0** | **uncapturable** — the postdating requirement consumed the entire margin |
| LAJ | 51 | never (credited at 54, 9,150.2 s before the 51 print) | — | **width 0** | uncapturable at 51 |

**The one-beat-late law:** under print-gated admission the capturable set is exactly the
multi-print floors with wide-enough windows — and this build converted three of them (BAR, SVA,
PRA). The single-print floors (URS 57, PAL 39, LAJ 51) have window width **zero**: the only print
is simultaneously the admission evidence and the only fill opportunity. PAL realized the bound
literally. No admission predicate, wake, or clock can fix width-zero floors — only pre-seating can.

---

## 3 — THE PRE-SEAT COUNTERFACTUAL (F-VS-240)

The graded drift-prediction corpus (BELIEF_DEADLINE_SCORING_TABLE, 5,609 rows) already licenses
the escape. Per leg, the earliest coherent prediction at/near the floor, checked for postability
and deadline coverage against the tape:

| leg | prediction (emission → target, deadline covers print?) | coherent? | postable? | pre-seats floor? | standing to first print |
|---|---|---|---|---|---|
| GIU | 1783833752.027 → **66**, graded hit err 0 | YES (stamped at that instant) | 66 < ask 71 | **YES — exact** | 35,623 s (9.90 h) |
| URS | 1784028256.439 → **57**, graded hit err 0 | YES | 57 < ask 58 | **YES — exact** | 4,441 s (1.23 h) |
| PAL | 1784022844 → **39**, deadline covers, graded hit | YES | 39 < ask 42 | **YES — exact** | 19,223 s (5.34 h) |
| PRA | 1784339306.774 → **41**, graded hit | YES | 41 < ask 43 | **YES — exact** | 3,247 s (0.90 h) |
| BAR | coherent one targets 25 (−2); the 26 within-1¢ emission is incoherent | — | 27 < ask 33 | NO — target aims wrong | (8,049 s available) |
| SVA | best pre-print target 37 (−4) — worst aim in the corpus | mixed | 41 < ask 46 | NO | (12,599 s available) |
| LAJ | 52 (+1) but its instant is DISAGREES; every coherent window says 59 (+8) | NO | 51 < ask 54 | NO — coherence miss | (23,499 s available) |
| DAN | 57 (−2) emitted 0.001 s before its own first print, deadline CLAMPED to emission, unpostable (59 == ask) | stamped coherent | NO | NO — fails all three axes | 0.001 s |

**The capture set {GIU, URS, PAL, PRA} pre-seats correctly — including two of the three
width-zero floors (URS, PAL).** Aggregate bed arithmetic: only URSPAL two-sides → prediction-
seated rests bank 4¢ of the 19¢ a perfect pre-seater reaches (21%); GIU and PRA pre-seat as
orphaned one-siders (BAR's −2 aim and DAN's structural failure strand them). Two corpus defects
filed: **2,020 rows (36%) carry `stale_modeled_deadline_clamped_to_emission=true` — zero-width
grading windows — while the header claims all deadlines fresh** (the same defect that voided
DAN's only near-floor prediction); and the URS re-emission storm (63¢ × 2,515) dominates the
2,571 ungraded rows.

---

## 4 — DAN's 58-vs-59, attributed (F-VS-241)

**DATA-GAP — a members-missing library cell.** The separation row consumed the tape correctly
(observed_traded_low 59 on the row; all three 59 prints seen, 152.38 contracts consumable; the
lone 58 print is post-span), but among all 68 member-backed termini in ATP_MAIN_51_75, **not one
final traded-low sits above its anchor** — the surviving shapes' path tops at 58, so 59 is
refused as above-path. Negative-depth bins exist in other categories (ATP_CHALL, WTA_MAIN carry
−1..−6) — a members-missing cell, not schema blindness. Two riders: the belief lane's 57 target
sits 1¢ below even the library's 58 (a drift-target central-estimate artifact), and its clamped
deadline made the grade a formality.

**Strike-three verdict:** the knife's third cut is the first whose conduct on the capturable set
is fully correct — three conversions, two refused chases (GIU-69, PAL-40 — swapped for PRA's
exact-floor fill), honest banking throughout. What remains is not conduct: the width-zero floors
demand pre-seating (the prediction corpus already licenses URS 57 and PAL 39), DAN demands the
missing library cell, and BAR/SVA/LAJ's predictions demand better aim than their tape conduct
already achieves.
