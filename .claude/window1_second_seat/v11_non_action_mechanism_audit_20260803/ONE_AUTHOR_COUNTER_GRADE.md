# ONE-AUTHOR VERIFICATION + THE BRAIN'S FIRST HONEST GRADE — @34d43755

License: LAW_INDEX read @34d43755, sha256 41784e6a… (verified this seat).
Build: `window1: enforce one-author veto-only pricing`.
Package: `stage1_store/v54_one_author_cap_veto_no_vacuum_20260825_rerun4/`.
Method: four independent verification lanes, each recomputing from the custodied trace,
raw prints/tick tapes, CORPUS_INDEX, the V3 map @ac68e3bc, and `git show 34d43755:` code.
Filed findings: F-VS-215 … F-VS-218.

---

## 0 — LEDGER ADJUDICATION (F-VS-215)

My ledger (`FINDINGS_VERIFICATION_SEAT.md`) is untouched at 34d43755; true next-free was **F-VS-215**.
The builder's `FINDINGS_V53.md` runs a **parallel F-VS sequence**: 37 numbered rows, of which
**33 collide** with filed vault numbers (171–174, 179–203, 207–210 — all with different content),
and 215–218 pre-number my next-free block. F-VS-117's collision class, second appearance, now
systemic. The collisions sit on law-bearing numbers: their "F-VS-188" is rest-tenure trivia where
the vault's F-VS-188 is the governing ceiling table (the bed spec); their "193"/"199" overwrite the
TECHNIQUE FRAME and ZERO CONTRADICTIONS operator rulings. One content conflict is material: their
parallel "F-VS-209" asserts DANPRA "floor-rest proof at DAN 59 **and PRA 41**" at d837b992 — false;
the vault's F-VS-213 proved PRA never rested at 41 there (the proof was DAN-only).

**Ruling filed:** F-VS numbers are assigned only by this seat, at filing time, in the vault ledger.
The builder's numbers are void as vault citations; their four new texts are re-designated build
claims BC-A…BC-D and adjudicated below; numbers 215–218 are reclaimed by this seat's filings.

---

## 1 — VERIFICATION: every build claim survives adversarial recount (F-VS-216)

- **The brain's number is the emitted number — 47/47, zero divergences.** The sole price author is
  `mappedFloorTarget` = lower weighted median (os:522-533) of per-vote
  `licensed_floor = max(1, v3_price_cell − edge_p50)` (os:720), author bound at os:745.
  All 47 PLACE/REPRICE targets recomputed from each row's `authority_recompute_inputs`: 0 divergences.
  Deeper, 12 sampled orders (80 votes): every vote's cell verified against the member's bounded close
  in CORPUS_INDEX, every edge_p50 against the V3 map FILE @ac68e3bc (sha 72751efe… matches), every
  weight against the law score × coverage × 1/(1+|memberDip−ownDip|) to 1e-9. **Conditioning is
  weights-only** — the observed traded low never touches a vote value or the target.
- **Ask−1 is dead.** 0/47 orders at ask−1 (d837b992: 41/47). The clamp code is deleted;
  `post_only_cap_cents: null` on 3,042/3,042. Traded-low authorship: 0/47.
- **1,042 vetoes — count EXACT, set-identical to my recount; blocked and rewrote nothing.** Caveat:
  1,041 of them are passive (the predicate evaluating false over an already-standing rest at/above
  the ask); exactly **one** row genuinely blocked a proposed new target (ln223 PAL 39 vs ask 39,
  existing 37 held). 96 rows sit on genuinely ask-only book receipts (re-verified at raw-tape
  granularity); zero orders fired on any.
- **162 vacuum rows — EXACT; all emitted nothing.** All 162 are pre-formation
  (`formation_complete: false`); post-formation the authority was never silent in any game.
  The census measures formation gating, not mid-game authority failure.
- **Fills: three, all lawful.** URS entry 60 on the 58 print @1784028256.439 (af7cc4fa…) ·
  PAL entry 39 on its floor print @1784042066.596 (11b32855…) · LAJ entry 52 on the 51 floor print
  @1784060123.219 (7fb0df36…). Entry == prior standing rest on all three (F-VS-107); no resting leg
  was ever crossed by an in-span print (min prints: BAR 27 vs rest 25 · GIU 66 vs 62 · SVA 41 vs 36 ·
  DAN 59 vs 57 · PRA 41 vs 40). GIUBAR's lawful 0-fill stands ONLY on the W1TT-C-001 corrected bell
  1783874300 — under the stale c0056976 span both GIUBAR rests would have been crossed post-bell.
- **Custody: the "four attempts" reconcile as 3 + 1.** Three mechanical failures in custody
  (field-miswire · veto-check/ask-only-rearm · cap-veto-cancelled-lawful-plan), manifest/disk/hashes
  all verified; rerun4 is the fourth run and the decisive package — itself failing on outcome
  (tripwire + third DANPRA proof failure), not mechanics.
- **Determinism X2 byte-identical on all four games**; stage/fill counts reconcile to the trace
  exactly. **Gate: 23/24; sole failure CURRENT_BED_TRIPWIRE — on all four games**
  (GIUBAR incomplete · URSPAL Δ1 < 4 · LAJSVA incomplete · DANPRA UNSTAMPED ≠ LAWFUL);
  `self_stop: true`.

**Adjudication of BC-A…BC-D (the builder's "215–218" texts): substantially TRUE**, with the two
characterization corrections above (passive veto population; vacuum = formation gating).

---

## 2 — PARITY: which banked wins survived, and what broke each (F-VS-217)

| banked win | this build | verdict | what broke / preserved it |
|---|---|---|---|
| URS 57 held (d837b992 filled 58) | **FILLED 60** | **BROKE −2¢/−3¢** | q50 authored 60 at ln216 @1784004782 (SINKAL 60¢ crossing vote; zero own prints). First print @1784005897 armed C02 floor tenure; it then vetoed **457 recomputes at 58** (from ts 1784006318, 21,938 s before the fill) and 413 at 55. The rest stood crossed (60 > ask 58) at the fill. Caveat: un-frozen tracking was a 58-or-55 coin flip — 55 never fills (span min 57). |
| BAR 27 exact | rest 25, **no fill** | **BROKE** | Two mechanisms: (i) the same-receipt traded-low capture that banked 27 is retired by design (C07 RETIRED_BY_ONE_AUTHOR — "the print never authors the order price"); (ii) pure panel churn repriced 30→25 at ln44 @1783841772, **29.3 s before the floor print**, on a joint leave-one-out recomposition (DOSHIJ out, CHIWON in, SAMHUA's weight halved) with zero market input. C02 then locked the underwater 25, vetoing the 27 later recomputes (all at 29¢, ln48–71). 27¢ itself was derived only on pre-book stand-down rows and one ask-tick-vetoed row — never rested. |
| SVA 41 exact | rest 36, **no fill** | **BROKE** | Capture retired + the neighbor library's licensed floors for this cell sit ~5¢ under the realized floor (q50 36 even without the 16¢ outlier). 41 derived once, pre-book. No print ≤36 exists. |
| PAL 40 | **FILLED 39 — exact floor, first time ever** | **IMPROVED +1¢** | q50 luck + the freeze: the crossing sat in the 39 vote block at ln246, 0.6 s before PAL's first print armed C02; the freeze then preserved 39 against 745+ lower recomputes (mode of drift: 38/37/34/32) and skipped the 40 print the prior build ate. The same veto that broke URS. |
| LAJ completed (54; crown 53) | **FILLED 52** | **IMPROVED +2¢/+1¢** | SMISMI2's dominant 52¢ vote (47% of mass) pinned q50 at ln1417; C02 held it against 58-drift; filled on the floor print, 1¢ above floor. |

GIU (never banked): rest 62, unfillable under this authority — max proposal ever 65, span min print
66. DAN/PRA: see §4. **The churn class:** panel membership changes move resting levels up to 5¢
between adjacent receipts with no market input; whichever level happens to stand when the first
print arms C02 becomes the level for the rest of the window.

---

## 3 — THE GRADE: the brain's own math at every floor moment (F-VS-218)

At 7 of 8 governing rows the **fresh** authority recompute diverged from the standing rest
(GIU 59 v 62 · URS 64 v 60 · PAL 32 v 39 · SVA 50 v 36 · LAJ 63 v 52 · DAN 53 v 57 · PRA 36 v 40)
and the C02/pair vetoes held the older, better number. The brain drifts both directions; the vetoes
— which consume exactly the evidence the author is forbidden — produced the census's accuracy.

| leg | floor | brain | gap | its inputs at the governing row | street, per cent |
|---|---|---|---|---|---|
| BAR | 27 | 25 | −2 | authored ln44: cell 30 − edge 5; obs low **27** on the floor-print row, spread-eye clearing **27**, `below_low` flag TRUE — all unread | **2¢ RIGHT DATA UNCONSUMED** |
| GIU | 66 | 62 | −4 | authored ln38: cell 68 − edge 6 (ILABRO 62¢, 43% of mass); at ln80 bid 65, obs low 67, clearing 70 all above 66, unread | **3¢ UNCONSUMED** + 1¢ at-ask (66 = ask; unpostable under their own post-only law, though 66 printed twice more) |
| URS | 57 | 60 | +3 | authored ln216 from neighbor close cells 63–83; timed remaining-dip q50 = 0 while 7¢ of dip remained; no channel ever carried 57 (bid/ask bracketed it) | **3¢ WRONG DATA CONSUMED** (2 of them recoverable at 58 via the vetoed recomputes) |
| PAL | 39 | 39 | 0 | exact — but the floor-moment fresh author said **32**; the hit is the ln246 state frozen by C02 + obs-low-40 tenure licensing | 0¢ (credit belongs to the veto, not the author) |
| SVA | 41 | 36 | −5 | cell 40 − library edge 4, subtracted straight through a live 40 bid; zero own prints ever (conditioning channel empty); bid 40/ask 41 on the row, unread | **4¢ UNCONSUMED** + 1¢ at-ask (41 = ask) |
| LAJ | 51 | 52 | +1 | stale early map product (cell 58 − 6); at the governing row the live bid was **51 — the floor exactly** — unread | **1¢ UNCONSUMED** |
| DAN | 59 | 57 | −2 | votes top out at 57 (GIRDAV crossing); obs low **59 = the floor** on the floor-print row, flagged, unread | **1¢ UNCONSUMED** (bid 58 join lawful) + 1¢ at-ask (59 = ask) |
| PRA | 41 | 40 | −1 | q50 40 (PRIHEI 0.646); obs low 43 pointed high; 40 = live bid = the maximal postable level | 1¢ at-ask — with the ln1546 exception below |

**Totals over the 18¢ of gap: WRONG DATA CONSUMED 3¢ · RIGHT DATA UNCONSUMED 11¢ ·
AT-ASK (unpostable under the build's own post-only law) 4¢ · DATA THAT NEVER EXISTED 0¢.**
The brain never lacked the data — it lacked the license to read it: the observed traded low never
adds a cent (no `max(target, low)` exists; five governing rows carried `below_bounded_trade_low:
true` and did nothing), the remaining-dip machinery is pure telemetry, and the spread eye is
recorded-never-consumed on every row. The undershoot mechanism is the formula itself: a
category-median historical edge (4–9¢) subtracted from neighbor closes, straight through live bids,
at window fractions 0.04–0.23, then frozen.

---

## 4 — DANPRA: the third abstention failure is structural — and the build's own veto blocked the fix (F-VS-218)

Receipt honest this time: stamp UNSTAMPED_INCOMPLETE, `rest_at_floor_rows` EMPTY,
`rest_at_floor_proven: false`. Conduct: DAN flapped 44↔56, repriced 57 @1784336963 (q50 of a panel
whose values never support 59 — max authority ever 57), held 57 to span end. PRA placed 40
@1784332553 and held. Neither leg ever rested at its floor.

**The sharpest row of the run: ln1546 @1784359766 — PRA's authority independently recomputed to
41, the exact floor** (obs low 41, the real floor print, in the panel's conditioning) —
`authority_target_divergence {authority 41, final 40, diverged: true, senior_authority_reason:
C02_FLOOR_TENURE_OVER_BELIEF_DRIFT}`. The one moment the proof-by-conduct was within reach, the
build's title mechanism vetoed the lift; PRA printed 41 four more times afterwards. DAN's failure
is a vote-panel limitation; PRA's is a veto artifact.

Clean this time: zero post-span orders (the trace ends exactly at governing span_end 1784372160 —
the d837b992 bell pathology is gone), zero cancels anywhere. Residue: the URSPAL LAWFUL receipt
still stamps `rest_at_floor_proven: true` on 1,149 rows that are all PAL — the F-VS-213
field-definition defect persists; and PAL's rows cite a URS-named book file (pair-stage receipt
naming, minor).

---

**The one-line grade:** the build honestly did what was ordered — one author, vetoes that only
veto, custody, determinism, and its first honest self-stop on all four games. The honest grade it
earns is the first clean measurement of the brain itself: ±5¢ of drift, 14 of 18 lost cents sitting
in evidence the author is forbidden to consume, and both banked improvements owed to the freeze,
not the forecast.
