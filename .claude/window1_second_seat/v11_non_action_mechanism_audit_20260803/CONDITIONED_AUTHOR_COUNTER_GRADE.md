# CONDITIONED-AUTHOR COUNTER-GRADE — @53863a33 · CONVICTION FIRST

License: LAW_INDEX read @53863a33, sha256 41784e6a… (verified this seat).
Build: `v54: condition prior and bank conviction stop`.
Package: `stage1_store/v54_condition_dont_replace_20260825/`.
Grading order per F-VS-224: the conviction judged first as an argument; the floor is the ruler.
Method: four independent lanes, all recomputing from trace (727 stages + 8,176 rearms + 3 fills;
1,438 derivations), prints, tapes, and code. Filed: F-VS-225 … F-VS-228.
Ledger: builder filed BC-042..045; zero F-VS rows; my ledger untouched.

---

## 0 — THE CONVICTION AUDIT (F-VS-226)

The conditioning arithmetic (dual_belief_os @53863a33): per panel hypothesis f with weight w,
`posterior_w = w × Π (1/(1+|f−v|))^(rank·grade)` over channels TRADED (rank 3) /
TRADE_BACKED_SPREAD_CLEARING (rank 2) / BOOK (rank 1); level = round(posterior mean), half-up.
Recomputed on ALL 1,438 rows: 0 mismatches. The arithmetic is VALID everywhere.

**The structural defect, stated once: the posterior's support is the panel's hypothesis set only.**
Likelihoods reweight panel floors; they cannot create a hypothesis at the evidence value. When the
own-tape floor is absent from the 7-row panel (BAR 27, DAN 59), no grade, rank, or exponent — not
even ×100 — makes the level equal the floor; the posterior converges to the nearest panel vote.
And the panel is resampled per receipt: membership churn, not evidence, authors most movement
(SAMHUA's exit co-authored BAR's fatal drop; JODFIL/BUBDE/OFNETC rotation authored DAN's endgame).

Eight verdicts:

| leg | verdict | the failing / carrying premise |
|---|---|---|
| BAR | **UNSOUND** | at the floor print's own receipt, trade 27 @grade 0.996 vs book 25 @0.598 — 8.3:1 dominance — posts 25.0016. No weighting rescues 27; support excludes it. |
| GIU | **UNSOUND** (game) | the showcased 65.719→66 row is sound; the conviction then wandered 66→64 on churn against a fixed traded-low 69, and no row after ln77 ever read ≥66 again. |
| URS | **SOUND — fill scores** | final chain trade-led (TRADED 58 @0.966); the addendum's 57.526→58 showcase is a different, book-only row (ln223). |
| PAL | **SOUND (closest call)** | placement chain trade-led; but the panel holds no 40 hypothesis (mixture-mean artifact) and conviction had decayed to 38 by fill time — tenure carried the 40. |
| SVA | **SOUND** | 41 derived ON the first floor print's receipt (posterior 40.638→41); the delay to .484 was lawful post-only. F-VS-221b is repaired at the derivation layer. |
| LAJ | **SOUND — fill scores** | trade-led at the deriving receipt; floor printed 3¢ lower, 9,150 s post-fill. |
| DAN | **UNSOUND** | 59 structurally underivable: at its own floor print the posterior stopped at 56.938; the ×100 counterfactual converges to 60, never 59. |
| PRA | **ABSENT at the floor / SOUND later, silenced** | no decision stage exists at the floor print's receipt (rest sat 39); the later 41 argument was sound and twice silenced by continuous post-only. |

None of the three fills zeroes under F-VS-224 — all final chains are traded-channel-led with
verified print receipts. Two more audit facts: the build's two showcase rows are its weakest
arguments (the 57.526 exemplar is a zero-trade book row; the 65.719→66 exemplar is stamped on
BAR's floor-print receipt — the very receipt where BAR's conviction failed); and two governing
floor prints never became decision instants at all (GIU's 66, PRA's first 41). Telemetry defect:
~128 duplicated stage rows at one receipt (BAR row-2813 @1783874300) inflate the 727 count.

---

## 1 — VERIFICATION (F-VS-225)

- **1,438 conditioning chains: recomputed on every row — 0 mismatches** (posterior and level).
  3,262 channel rows, 0 missing receipts. Book-never-authors-alone substantiated independently
  (295 book-only rows, all with non-empty priors). Wording refutation: **the `??` operator is NOT
  gone** — it survives as `trueConditioning.level_cents ?? engineTarget`, a null-fallback TO the
  prior; only the replacement semantics are gone.
- **Same-receipt acts: 52/52 verified**, 0 violations — with the caveat that
  `scheduler_latency_seconds` is hardcoded 0 for orders (a schema guarantee, not a measurement),
  and 58 further target-changing orders are excluded from the census solely by the
  evidence-pinned-to-current-receipt definition.
- **Directional rounding: uniform on 1,438/1,438** — but the named 57.5→58 exemplar is vacuous
  (zero exact-half posteriors exist in the data; the receipt's example is a static constant), and
  "FLOOR_SIDE" mislabels what is round-half-UP toward the more aggressive integer.
- **16 post-credit reads: exactly 16, all live** (URS 5 / PAL 3 / LAJ 8), non-empty beliefs —
  F-VS-221c ("stops reading its own game") is repaired: the LAJ 51 floor print IS consumed
  post-credit (receipt 7fb0df36 pinned verbatim, grade 0.9998). Zero post-credit orders.
- **Fills: three, by trade id, entry == rest** (URS 58 on the 57 floor print · PAL 40 · LAJ 54).
- **The retained LAJ post-only defect, scoped:** one order — ln5273, PLACE 59 vs ask 60, C04
  rearm-restore lane, receipt SVA row-273. Mechanism: the restore writer runs after the post-only
  gate loop and spread-overwrites the placement without a `post_only_test`; 7 of the 8 C04
  restores happened to carry a test, this one restored over a placement with no candidate test.
  **Value-safe** (restoreLawful independently requires restorePrice < ask; sweep: zero of 121
  orders at/above ask) — the gap is receipt-coverage only, honestly flagged
  (POST_ONLY_GUARD_DID_NOT_COVER_EMITTED_ORDER; gate self-stops on it + the tripwire).
- **Determinism X2 byte-identical**; counts reconcile exactly. Rearm jump 6,635→8,176 reconciled
  (new DANPRA post-only cancel +264; longer URS windows); exactly one rearm unresolved at end —
  PRA's, armed at the fatal cancel, DISAGREES-embargoed to span end.

---

## 2 — THE PENDULUM (F-VS-227): replacement @ec23ad2e vs blend @53863a33, same receipts

| leg | floor | replacement | blend | Δ | class |
|---|---|---|---|---|---|
| BAR | 27 | **FILL 27 exact** (25→27 on the floor-print receipt) | **NO COMPLETION** — 27→25 on the same second's book row, held 25 through both 27 prints, 27 restored only after | leg lost | (i) decisive own evidence must dominate |
| GIU | 66 | FILL 69 (+3) | NO COMPLETION — derived exactly 66, wandered to 64 before the only 66 prints | 3¢ "save" never banked | (ii) prior must dominate touch echoes — and then the conduct must stand |
| URS | 57 | FILL 58 | FILL 58 (own posterior 57.526 rounded UP) | 0 | (iii) rounding-direction |
| PAL | 39 | FILL 40 | FILL 40 (conditioned 39; move-away guard held 40) | 0 | (iii) guard/timing |
| SVA | 41 | rest 41 one receipt late | identical — same reprice on the same .484 print receipt | 0 | (iii) one-receipt ordering, both builds |
| LAJ | 51 | FILL 54 | FILL 54 | 0 | (iii) none |
| DAN | 59 | **rest 59 exact, proof banked** | never rested 59 (posterior 56.94 at the floor print; its one 59.478 was post-only-blocked); ends 56 — **proof lost** | ratified proof lost | (i) decisive own evidence must dominate |
| PRA | 41 | 41 derived, pair-vetoed (DAN 59; sum 100) | 41 rested lawfully 9,861 s (DAN 57; sum 98), then post-only cancelled 0.288 s before a 41 print | both nothing; blend 0.288 s from floor-exact | (iii) ordering — plus (i)'s documented cost on the replacement side |

**The weighting law the table settles:** every real divergence was a floor-print-on-the-row moment
(BAR, DAN) — and the replacement won each one. The blend's only analytical win (GIU's exact 66)
was thrown away by its own restlessness. The remaining losses (URS's cent, SVA/PRA ordering) are
direction and order-management classes no weighting fixes. The law both machines need: **at a
floor-print-on-the-row moment, the decisive channel must be allowed to contribute support (a
hypothesis at the print's level, weight scaled by decisiveness per F-VS-066) — replacement in the
limit, exactly where the evidence is maximally decisive; everywhere else, the graded prior blend
should govern and the conduct must then stand at the conditioned level.**

---

## 3 — THE LOSSES, row-traced (F-VS-228)

- **BAR — lost to counter-causal intra-second ordering.** Book rows carry integer-second stamps;
  prints carry fractions; a decision at second S consumes the WHOLE second's book state and
  mutates the rest before S's fractional prints are fill-tested. ln50's reprice 27→25 cited book
  row-444 — the last row of second 1783841801, containing the 27-prints' aftermath — yet executed
  before the .304766 print in replay order. The reprice out-ran evidence that postdates it. The
  27-episode was the window's only floor touch; zero later BAR prints ≤27.
- **GIU — the killing cents are ln80 (66→65) and ln83 (65→64)**, both licensed by the blend while
  the machine priced BELOW its own live bid channel (bid 66–69); no posterior ≥66 after ln77;
  no decision rows at any of the three 66 prints. GIUBAR's receipt proves both floor rests
  existed to the cent (176 rest_at_floor rows) — destroyed by the build's own repricer, not the
  market.
- **DAN — 59 underivable** (§0); its one 59-intent (posterior 59.478 after the second 59 print)
  was post-only-blocked at ask 59.
- **PRA — guard rotation at the floor.** ec23ad2e: pricing fixed → C09 pair veto consumed the leg
  (DAN held 59). Here: pair lawful (DAN 57, sum 98) → **C03 continuous post-only** cancelled the
  9,861 s rest at the integer-second book row where the ask joined 41 — 0.288 s before the 41
  print — and the rearm was DISAGREES-embargoed through four more fillable 41 prints to span end.
  The class: a guard that cancels the rest exactly when the ask joins it structurally forfeits
  the fill it was resting for; fixing the pricing side merely rotated which veto consumed the leg.
- **DANPRA under amended F-VS-121 (F-VS-223):** stamp LAWFUL_INCOMPLETE with 10 PRA@41 conduct
  rows and the arithmetic stated. Both floors were derived from own floor evidence (PRA
  continuously; DAN at ln8621, from the second 59 print — though NOT at the first floor
  receipt, where the posterior read 57). Two readings flagged for the operator: strict
  (derived-at-first-floor-evidence: DAN fails → stamp unearned) vs plain (derived-at-own-floor-
  evidence: satisfied). The allocated leg's conduct is real but was itself destroyed mid-tenure
  by C03. This seat grades the stamp **defensible under the plain reading, with the conduct-leg
  caveat on the record**.

Gate: tripwire fails GIUBAR/URSPAL(Δ2<4)/LAJSVA; DANPRA passes its row; plus the honest
POST_ONLY coverage failure. Self-stop banked.

---

**One line:** the blend is the first build whose paperwork survives full recomputation — and its
losses are now pure structure: a posterior that cannot say what the tape just said (BAR, DAN),
a replay clock that lets integer-second book rows outrun their own second's prints (BAR, PRA),
and a guard that takes the fill it was protecting (PRA). The weighting law is settled by the
table: decisiveness must buy support, not just weight.
