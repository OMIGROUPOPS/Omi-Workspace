# SEE-SAW COUNTER-GRADE — @209358dd · CONVICTION FIRST

License: LAW_INDEX read @209358dd, sha256 41784e6a… (verified this seat).
Build: `v54: grade floor decisiveness and honest rounding`.
Package: `stage1_store/v54_floor_decisiveness_no_self_echo_postability_rounding_20260826/`.
Method: three lanes recomputing from the trace (10,738 rows: 3,076 stages / 7,657 rearms /
5 fills; custody sha matches), the three prior builds' traces, prints, tapes, and code.
Filed: F-VS-234 … F-VS-237. Ledger discipline holds a fourth time (BC-050..054; zero F-VS rows).

---

## 0 — CONVICTION AUDIT (F-VS-235)

**Certified-sound set this build: {BAR, GIU, URS, SVA, LAJ, PRA} — six of eight, the best
certificate count of the four builds.** The floor-decisiveness reweight is the first operator in
four builds that grades where a cent sits in the leg's descent instead of how loudly it traded.

- **BAR SOUND** — fd 0.290 at the floor-print receipt, mode 27, filled floor-exact.
- **GIU SOUND** — the formula refused the ballot's 69 purchase (fd 0: exact 0 / lower 151) and
  derived 66 = the floor (fd 0.307); immunity held it to span end. Unfilled — see §2.
- **URS SOUND** — fd 0.476 on its own 58 low (the balanced-downside pole); filled 58.
- **SVA SOUND — first fill in four builds, at its exact floor.** Derived 41 ON the first floor
  print's receipt (fd 0.3468, blocked only by postability 41==ask); established at the ask-lift
  receipt 7.17 s later — **0.484 s BEFORE the .484 prints** — and filled by 62c5acca. Mean-half-up
  would have emitted 39; the honest MODE emitted 41. The F-VS-232 instant, effectively acted on.
- **LAJ SOUND** — 54 = evidenced floor at placement; filled; the 51 floor printed 2.5 h post-fill.
- **PRA SOUND — first fill, at its exact floor**, and an addendum correction: PRA does not
  "stand" 41, it **FILLS 41** @1784369249.287 (6a5b1a68) — seated by the sibling's fall (DAN's
  crushed 53 freed the par budget: 53+41=94), re-rested on its own floor-evidence channel
  (fd 0.1846, receipt c7944353), held by 10 immunity rows, filled 9,862 s later. Both F-VS-229
  prongs met.
- **PAL UNSOUND** — failing premise: the downside-mass denominator lets 153 *unprinted*
  hypothesized floors outvote the leg's *printed* 39 (fd 0.0032); the mode settles on panel cent
  32, a level PAL's tape never approached. Stands 32 under a 39 floor — unfilled, −7, worse than
  every prior build's 40 fill.
- **DAN ABSENT** — no 59 chain ever exists to judge: 59 lies at depth −1, above the panel anchor
  (58), so `exact_support = 0` hard-gates fd to 0 and the printed floor **never becomes a
  candidate** — not graded weak; structurally non-candidate. Held 58 through all three 59 prints
  (unfillable at −1), then the mode dropped it 58→49→53. Materiality: the ballot's DAN-59 also
  never filled — what this build lost is the **stamp** (LAWFUL_INCOMPLETE → honest UNSTAMPED;
  PRA both prongs true, DAN neither — receipt verbatim).

---

## 1 — VERIFICATION (F-VS-234)

- **Self-echo removed** — zero occurrences of the channel or its state carrier in code and in all
  10,738 trace rows; no renamed successor; evidence candidates are no longer reweighted by
  themselves. Channel census: BOOK 5,924 · TRADED 5,634 · CLEARING 2,814 — nothing else.
- **1,817 same-receipt transitions exact**, zero latency violations. **The empty book-only
  postability subpopulation holds** under the build's definition — with the nuance that the one
  order carrying `became_lawful_on_current_book_receipt: true` (URS ln2890, the fill's own
  license) is definitionally excluded because the target moved on the same receipt.
- **At-floor immunity: 161 rows = the complete population** (recounted independently; receipt ↔
  trace key-sets identical; zero exits, zero violations; PRA's 10 rows named). The f5413a15
  63-of-602 receipt discrepancy does not recur.
- **Fills 5/5 by trade id, entry == rest** (BAR 27 · URS 58 · SVA 41 · LAJ 54 · PRA 41);
  GIU/PAL/DAN have none. Determinism X2 byte-identical; counts reconcile exactly.
- **Rounding verified with one characterization:** the emitted integer is the weighted floor-side
  MODE, and the "executed production counterexample" is **synthetic** (hardcoded mass in an
  ensure()); but four real production rows exist where mode ≠ mean-half-up in the operator's
  favor — including URS's acting span-start PLACE 57 (continuous 58.017 → mode 57). The fill
  itself landed 58 because the establishing receipt's own mode was 58 — no contradiction.
- **Clock recharacterized:** declared exchange-millisecond precision with ingest-sequence ties;
  the epsilon *encoding* is unchanged from f5413a15 — what changed is the declaration and
  receipts, and epsilons are applied to book rows unconditionally, not only on actual ties.
- **Custody: 7/7 external artifacts hash-match — but the "two pre-score serialization failures
  preserved outside the repository" CANNOT BE LOCATED**: no path, no hash, no receipt binds them,
  and no failure-era artifacts exist on disk. An unbound custody claim (L20/L22 gap) — the one
  claim in the package that fails verification.

---

## 2 — THE SEE-SAW, and the law it settles (F-VS-236)

| leg (floor) | replacement @ec23ad2e | blend @53863a33 | ballot @f5413a15 | decisiveness @209358dd |
|---|---|---|---|---|
| BAR (27) | **FILL 27** | lost — stood 25 | **FILL 27** | **FILL 27** |
| GIU (66) | 69 (+3) | derived 66, wandered 64 | FILL 69 (+3) | **HOLD 66 = floor**, unfilled |
| URS (57) | FILL 58 | FILL 58 | FILL 58 | FILL 58 |
| PAL (39) | 40 | 40 | FILL 40 (+1) | **stands 32 (−7)**, unfilled |
| SVA (41) | rest 41 late | rest 41 late | rest 41 late | **FILL 41 = floor** |
| LAJ (51) | FILL 54 | FILL 54 | FILL 54 | FILL 54 |
| DAN (59) | rest 59, proof | 57 | rest 59, stamp | **stands 53 (−6)**, stamp lost |
| PRA (41) | pair-vetoed | cancelled −0.288 s | naked | **FILL 41 = floor** |

Movers between columns, one input each: BAR lost to the blend's book-grade dilution, regained by
the ballot's exact-cent evidence, kept by fd > 0. GIU bought +3 by the ballot's volume grade,
reseated at its true floor by the descent reweight. DAN reseated by the ballot's exact evidence,
**lost again structurally** by the depth<0 gate. PAL stable on own-tape evidence for three builds,
crushed by hypothesized downside. SVA fixed by honest mode + no-self-echo. PRA seated by the
sibling's fall. URS and LAJ never moved — the class no operator can hurt.

**THE LAW: yes — one shared operator serves all eight legs where per-leg state should govern.**
The four builds are four global settings of one dial, and each setting reseats one class by
unseating another. The classes: floor ON own tape (BAR, DAN, SVA, PRA — need exact-evidence
authority with mode emission); floor BELOW own tape (GIU, LAJ — need exactly this build's
descent/elimination reweight); floor below panel AND tape (PAL — printed own-tape lows must
outvote unprinted hypotheses); floor at own start (URS — indifferent). **The trace already
carries the classifier it refuses to use**: the sign of `observed_traded_low_depth_cents`,
`descent_state`, and `evidenced_floor_source` are computed and serialized on every row. The proof
sits on one line: **DAN ln10712 — the immunity organ stands ready to treat the printed 59 as an
evidenced floor (the same machinery that held GIU's 66, LAJ's 54, PRA's 41) while the pricing
organ assigns that same print fd 0** because the candidate grid lacks the cent. Two organs of one
build disagree about whether a print is evidence of a floor at its own price. The see-saw is that
missing per-leg dispatch.

---

## 3 — The ordered rows (F-VS-237)

- **GIU rest-66 vs its 66 prints — no fill-law defect; a late-derivation class.** The 66 rest was
  established at ln93 @1783873822 — 4,447 / 2,810 / **1,210.5 s AFTER** the three 66 prints, on
  the next book turning point, with the third 66 print itself as the establishing evidence.
  **None of the three 66-print receipts fired a decision instant** (zero GIU decision rows in
  [1783867786, 1783873822]). The rest then stood 478 s to span end over zero ≤66 prints. The 67
  print @1783867479.636 found GIU resting 55.
- **DAN 59→53 — what the reweight took: candidacy, not weight.** At the floor-print receipt the
  sentence records OBSERVED_TRADED_FLOOR=59 while FLOOR_DECISIVENESS_CHANNELS contains only the
  bid-58 (the 59 filtered by the fd>0 gate). Held 58 through all three 59 prints — one cent under
  the floor, unfillable — then the honest MODE (not the mean) produced the 58→49 drop as channels
  emptied. The distinguishing per-leg state is the **sign of the observed-low's depth**: GIU's 66
  at depth ≥0 (in-grid, fd 0.307) vs DAN's 59 at depth −1 (out-of-grid, fd 0). The same predicate
  that correctly refused GIU's 69 wrongly refuses DAN's 59.
- **URS floor-side mode verified at the fill row.** The addendum's counterexample is synthetic,
  but real acting emissions exist (span-start PLACE 57, continuous 58.017 → mode 57). The final
  establishing receipt (ln2890, `became_lawful` postability re-seat) carried mode 58 = the fill.
- **PAL 32 — the bid-crush class, third appearance, unrepaired in effect.** The span-start bid-33
  still enters at its exact cent (fd 0.4091 now, vs grade 0.9867 before) and the mode lands on
  it, crushing the panel's 39. PAL rested 39 sixty times — all inside a printless window; at the
  40 print it stood 35; at the 39 floor print it stood 32 with the floor evidence consumed at
  fd 0.0032. 1,780 order transitions — the worst churn of the four legs.
- **LAJSVA completes 54+41=95/Δ5** — the first LAJSVA completion in the campaign; still fails the
  Δ8 tripwire. **Gate honest**: 26/27, sole failure CURRENT_BED_TRIPWIRE; self-stop banked.

---

**One line:** the see-saw's fourth swing produced the best conviction certificate yet — six sound
legs, two exact-floor first-fills, and the campaign's first LAJSVA completion — and its two
failures are one missing dispatch: the build computes, serializes, and refuses to consult the
very per-leg state (depth sign, descent state, evidenced-floor source) that says which of its own
four operators each leg needs.
