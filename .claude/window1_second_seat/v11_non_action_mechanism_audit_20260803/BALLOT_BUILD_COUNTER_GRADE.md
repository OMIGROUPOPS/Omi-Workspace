# BALLOT BUILD COUNTER-GRADE — @f5413a15 · CONVICTION FIRST

License: LAW_INDEX read @cfab4ac5, sha256 41784e6a… (verified this seat).
Build: `v54: join exact evidence and repair causal clock`.
Package: `stage1_store/v54_evidence_ballot_causal_clock_floor_immunity_20260825_r2/`.
Method: three lanes recomputing from the custodied trace (1,586 stages + 83,406 rearms + 5 fills;
2,824 derivations; custody-pinned sha verified), prints, raw tapes, and code.
Filed: F-VS-230 … F-VS-233. Builder ledger discipline holds (BC-046..049; zero F-VS rows).

---

## 0 — CONVICTION AUDIT (F-VS-231)

**The ballot as coded:** panel rows normalized to unit mass; every own-evidence channel ALSO joins
as a candidate at its exact cent with weight rank×grade; all candidates conditioned by all
channels; level = round(posterior mean), half-up. Two operators the receipts never name:
**evidence votes twice** (likelihood and candidate, raw weight up to 2.99 against a panel whose
whole mass is 1.0), and a **LICENSED_STANDING_REST_EVIDENCE self-echo** channel that feeds the
machine's own rest back as evidence.

**The two passes, verified to their evidence rows.**
- **BAR 27 — SOUND, and the ballot is load-bearing.** At ln56 (the first 27 print's own receipt,
  causally ordered before the .417 print): TRADED-27 w 2.988 + CLEARING-27 w 2.0 enter; posterior
  26.99161 → 27; panel-only would have said **25** — without the ballot the blend law would not
  have restored 27. Filled at .417, floor exact. Flags: ln53's 27 was an interpolation artifact
  (no candidate held 27) and ln54's dip to 26 was pure standing-rest self-echo.
- **DAN 59 — SOUND; stands at-floor to span end.** 25 support rows, all pinned to the two real 59
  prints; ln64343 posterior 58.9192 → 59. Structural note: the ballot's 59 evidence was BORN at
  the floor print — **an exact-evidence law can never buy the first floor print, only the second.**

**THE GIU-66 ABSENCE, quantified to six decimals.** At the same receipt with the identical panel,
the panel-only conditioned mean recomputes to **66.207118 — the blend's number exactly**. The
ballot then adds E69 (w 2.99281, volume-graded 0.9976), E68, E70: posterior 68.96 → 69. After
conditioning, the three own-evidence rows hold **99.96 % of posterior mass**; JUSHEI's 66 — still
the largest surviving panel hypothesis — is outvoted ~1300:1. `GIU_66` support = 0 because GIU's
own tape never printed/bid/cleared 66; under a law where only exact own prices become candidates
and candidates dominate, 66 is unreachable. **The fix that saved BAR is arithmetically what killed
GIU's 66: the ballot repaired the class whose floor lies ON its tape (BAR, DAN) at the price of
the class whose floor lies BELOW its entire tape (GIU).** The F-VS-227 decisiveness grade, as
implemented, measures how decisively a price TRADED (volume), not how decisively it is the FLOOR
(elimination of lower hypotheses) — the one number that separates the two classes. GIU's 69 print
eliminated nothing below it; a decisiveness-of-floor grade gives it near-zero point support and
returns 66.

**Verdicts:** BAR SOUND (floor exact) · GIU **UNSOUND** (touch-decisiveness asserted as
floor-decisiveness) · URS fill-chain SOUND, leg-level flaw at ln1008 · PAL SOUND · SVA chain
SOUND, credit ABSENT · LAJ SOUND · DAN SOUND, uncredited by law · PRA **ABSENT** (self-echo
floated 42 above the floor; post-only cascade stripped it; naked at its floor moment). Opening
pathology flagged: on wide unformed books the panel places unmoored orders (SVA PLACE 24 vs bid
36; LAJ PLACE 65 vs bid 54) — the mirror image of a high-grade bid channel crushing a correct
prior (PAL's 39 → 33 at span start).

---

## 1 — VERIFICATION (F-VS-230)

- **All 8 receipt hashes match** their addendum statements (git-blob sha recompute).
- **Causal clock: order-faithful, label overstated.** Interleave rule verified in code and on raw
  tape at 6 sampled seconds (the BAR row-444 inversion IS fixed in order; PAL's matched-print
  recut exact). Overstatements: "true fractional exchange prints" is **millisecond-deep** —
  every print epoch is truncated to ms, so post-print book stamps precede the prints' true
  microsecond times (order-consistent only because all references truncate identically); 5 of the
  "90 changed order rows" are annotation-only; and the µs-offset scheme is safe on these tapes by
  luck, not construction (no guard for sub-ms prints in-window or ≥1000 book rows/second).
  Zero counter-causal residues across all 84,872 tape-citing rows.
- **At-floor immunity: zero-violation conclusion HOLDS over the full 1,226-row at-floor
  population; the receipt's population claim misleads.** The receipt enumerates 63 decision-lane
  rows (URS 58 ×6, SVA 41 ×40, LAJ 54 ×17 — **no BAR, no DAN**); the trace executes the immunity
  reason on 602 rows (539 more in the rearm lane, including all 7 BAR@27 holds). Exactly one
  at-floor mover exists — the sole lawful exit (GIU's 70 rest, C03 cancel) — and its "supporting
  evidence had overturned" is **asserted state, not a traced transition** (no elimination event
  exists; nearby rows read INSUFFICIENT_EVIDENCE). PRA has no immunity row by definition: its 41
  rest sat 1¢ BELOW its (43-then-42) evidenced floor on all 91 rows.
- **C04 coverage: 3/3 fixed** (the 53863a33 defect does not recur). **Fills: 5/5 by trade id,
  entry == rest.** **Determinism X2** receipt-consistent; counts reconcile exactly.
- **The 83,406-rearm flood is the causal clock's own artifact:** attempts now issue per recorder
  book row × both legs (41,728 unique receipts; URSPAL alone 54,776) — receipt multiplication,
  not decision activity. One unresolved rearm at end: PRA's.
- **Custody: verified**, including the preserved r1 preliminary (byte-different trace; r2 was
  specifically an at-floor-immunity receipt repair — CAUSAL_CLOCK and C04 receipts byte-identical
  across r1/r2).

---

## 2 — RESIDUALS, street per cent (F-VS-232)

| leg | cents | street | the row |
|---|---|---|---|
| URS | 1 (58 v 57) | **MISREAD** | Placed AT 57 at span start (ln1004, bid-echo). At ln1008 the ballot's own posterior held 57 as majority, median, AND mode (57 = 0.5977, 58 = 0.3380) — and the MEAN (57.5173), half-up, moved the rest to 58 on a consumed bid tick. 57 was postable throughout; the floor print fills a standing 57. The endgame 58 restore (ln2181) is honestly 58-print-supported; the cent was spent at ln1008. |
| PAL | 1 (40 v 39) | **DATA-GAP** with two chargeable notes | The panel itself carried 39 at span start and a 0.9867-grade bid channel crushed it to 33 (ln1004); at ln1044 the posterior was **39.811** and the operator named "floor-side" — implemented as nearest-half-up — rounded UP to 40. After span start no consumed channel ever named 39; the only 39 evidence is the post-fill floor print. |
| GIU | 3 (69 v 66) | **MISREAD + GAP + MISREAD-class** | 69→68: the bid-68 candidate was consumed and outvoted (posterior 0.0566 vs E69's 0.9661) — a 68 rest fills on the 67 print. 68→67: nothing consumed at 67 — DATA-GAP. 67→66: the panel's second-largest vote sat exactly at 66 (0.2317) and conditioning crushed it to 0.0009. Post-credit GIUBAR rows: none exist — no posterior was ever computed at the 67/66 prints. |
| LAJ | 3 (54 v 51) | MISREAD-class ×2 + GAP | 54→53: bid-53 candidate consumed (0.0368), mean 53.9696 rounded UP. 53→52: panel vote at 52 (0.1648) consumed-and-crushed; 52 never printed. 52→51: floor print is the only 51 evidence, 2.54 h post-fill — DATA-GAP. |
| SVA | whole leg | **DATA-UNCONSUMED — the missed instant named** | The causal clock cut the ask-lift row (SVA row-342, 41→42) to ≈1784020209.000006 — BEFORE the .484 prints — and the build evaluated SVA ≥14 times in those instants (rearm rows .000006–.000020), holding 39 every time: **no lane rederives on a book-only postability change between print receipts.** The reprice fired at .484 ON the second print's own receipt — unpostdatable. Acting at row-342's instant fills SVA at its exact 41 floor and completes LAJSVA at 95. |

**The rounding operator decides three of the cents** (URS 57.5173, PAL 39.811, LAJ 53.9696 — all
rounded UP by an operator named floor-side, implemented nearest-half-up; a genuinely floor-side
direction yields 57/39/53 from the same consumed data).

---

## 3 — DANPRA: the stamp over-credits at this commit (F-VS-233)

DAN's prong holds under F-VS-229 (25 own-evidence rows; 56→59 reprice with the floor's evidence
in-channel; held at-floor to span end). **PRA's prong fails the plain standard here:** its 41 was
never derived at its floor evidence — it was a posterior-mean artifact at a 43-print receipt
(evidenced floor 43, then 42); immunity never attached (rest below evidenced floor on all 91
rows); and the conduct broke twice — the standing-rest self-echo floated the rest to 42 ABOVE the
floor (ln64334), then the 1784341326 post-only cascade cancelled the restored 41 at .393, leaving
PRA naked through its floor moment with an unresolved rearm whose one attempt AT the floor print
was refused. The LAWFUL_INCOMPLETE stamp at f5413a15 rests on arithmetic + DAN-only derivation:
**unearned at this commit** (a regression against ec23ad2e and 53863a33, whose stamps were
ratified). Gate otherwise honest: tripwire fails GIUBAR Δ4<7 · URSPAL Δ2<4 · LAJSVA incomplete;
self-stop banked.

---

**One line:** the ballot enacted F-VS-227 and won back BAR and DAN — the floors that live on
their own tape — while the same three operators it added (volume-graded point ballots, the
standing-rest self-echo, and mean-half-up rounding) spent GIU's 66, URS's 57, PRA's stamp, and
three rounding cents; and the causal clock, order-faithful but millisecond-deep, manufactured the
exact instant that would have saved SVA — which no lane was built to act on.
