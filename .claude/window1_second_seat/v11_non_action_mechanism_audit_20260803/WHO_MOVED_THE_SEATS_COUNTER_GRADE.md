# WHO MOVED THE SEATS · STORY STANDARD — @8e8f7149 · @27fc702f · @801a62f6

License: LAW_INDEX read @801a62f6, sha256 41784e6a… (verified this seat).
Builds: `bank conviction-seated bid self-stop` (B1 @8e8f7149) · `preserve prediction seats through
four-game bed` (B2 @27fc702f) · `let convictions reseat their own rests` (B3 @801a62f6).
Method: four lanes recomputing from all three custodied traces (B3 decompresses to 7.14 GB —
streamed), prints, tapes, code, and every cited git blob. Filed: F-VS-242 … F-VS-246.
Ledger discipline holds a sixth time: BC-063..076 append-only, every cited hash recomputes, and
`FINDINGS_VERIFICATION_SEAT.md` is blob-identical (`41ca8bd9…`) across all four commits.

---

## 1 — VERIFICATION (F-VS-242)

**GIU's 66 credit — CONFIRMED, the campaign's first GIU floor capture.** FILL_EVENT B3 ln251:
entry 66 == prior standing rest 66, triggering print 66, trade `924208a2` resolved in
prints.jsonl (ticker …GIUBAR-GIU, 66¢, size 3.0, 2026-07-12T15:16:15.227061Z, true_print). Paid by
the **first** of the three 66 prints; seat at 1783833752.027, lead **35,623.20 s**; F-VS-107
satisfied; the rest was never repriced or cancelled between seat and fill.

Two corrections to the build's account of it:
- **The 67→66 move is not new at B3.** B1 ln50/51 are byte-for-byte identical (same instant, same
  two receipts, same targets). B1 lost the 66 because ln100 `CONTINUOUS_POST_ONLY_CANCEL_CROSSED_
  STANDING_REST` cancelled the at-floor rest 1,589 s before the first 66 print — a standing rest at
  66 with ask 66 does not cross; it *is* the book — and all three 66 prints then read
  `POST_ONLY_BLOCKED_NO_EXISTING_POSTABLE_REST`. B2 fixed the precedence but froze the seat at 67.
  **The capture required BOTH changes; BC-073/074 credit only the reseat.**
- **The receipt's `first_target_print` resolves to the largest-size print, not the earliest** —
  it names the third 66 print and overstates GIU's lead by 3,236.27 s. Same defect on URS 62 and
  PAL 40 rows.

**The 11 reseats — count CONFIRMED.** Receipt row-set == independent full-trace recount (11 on 11
distinct lines; 0 at B1 and B2 — the mover is genuinely new). All 11 carry same-receipt movement,
a welded per-row `sentence_sha256`, and `independent_recompute_cents == target_cents`. Three
failures inside the rows: BC-073's narrative names only **8 of 11** (omitting PAL 34→35, URS
62→63, and **PAL 39→40 — the one that cost PAL its floor**); **2 rows carry null decisive
evidence** (both PAL); **3 rows move while `authority_conditioning_changed: false`** and labelled
`CONFIRMED`, contradicting the receipt's own law text while it asserts `evidence_changed: true`
on all 11. Two rows carry a direction label opposite to the move.

**The three self-reported violations.**
- *One double-order receipt* — CONFIRMED, 1 row: the seat and its same-instant reseat, two orders
  at one microsecond. A **regression** (identical key/count at B1, absent at B2), structurally
  inseparable from the reseat. Unrealised here; a genuine double-fill hazard live.
- *11 uncovered post-only rows* — CONFIRMED, and **they map 1:1 onto the 11 reseats**: the feature
  is 100% outside the shared guard, by design (`post_only_role: NO_AUTHORITY_OVER_SEATED_REST`,
  with a private duplicate predicate in the reseat lane). Every row has target < ask, so
  **receipt-coverage-only in this bed** — but two of the eleven are the standing-license receipts
  of the PAL and URS fills, so credited entries rest on unaudited emissions. This is the C04 class
  (F-VS-225/230) reintroduced one commit after C04 reached zero failures.
- *BAR live-conviction lag* — CONFIRMED as a gate failure, **mislabelled**: the conviction is
  `CONFIRMED_OWN_CONVICTION` 30→30 refreshed on that very receipt; it is the **rest** that lags.
  **Value-inert** — zero BAR prints exist after that instant and BAR has no fill in any build to
  destroy. The unflagged defect underneath: the at-floor immunity is protecting a **dead level** —
  BAR's 27 rest became permanently unfillable when its prints passed 30,810 s earlier.

**Also refuted:** BC-074's "DAN's wired borrow moves 46→57" — the decisive source on that row is
`CAUSAL_LIVE_BOOK_BID` (58), and **all 8 borrow consumptions yield null targets**. The borrow is
receipted and grade-stamped but changed no emitted level anywhere (BC-065's zero rows and BC-070's
eight consumptions both verify).

**Determinism, custody, cache recovery.** X2 internally consistent on all three; row counts
reconcile exactly in all 12 game-rows — **but the hashed byte totals are 33–50 % larger than the
shipped artifacts** (B3's URSPAL stream alone exceeds the whole shipped trace), so the attestation
is not recomputable from anything in custody. Custody itself is strong: **19/19 local entries
hash- and byte-verified** (beyond the spot-check), plus 98/102/98 in-git manifest entries, with one
Linux-path artifact unverifiable from this host. BC-068's cache recovery: inputs verify, but the
"recovery" is a **re-derivation to a different byte image** (418,510 B vs the asserted 1,041,339 B),
its binding field is self-referential (F-VS-238 class) — though the underlying byte-identity claim
is independently true via git blob identity. `RECEIPT_ONLY_REBUILD_IDENTITY.json` is self-refuting
(label says "did not change score artifacts"; body says `false`) and at B3 **all three** score
artifacts drift with no BC entry mentioning it.

**A modelling caveat that qualifies every "capture" in the campaign:** fills are modelled from any
true_print at/below the rest regardless of aggressor direction. GIU's paying 66 print is
`taker_book_side: bid` — an aggressive buyer, which would not lift a resting bid on a real book.
Same for LAJ 54/55, URS 58, PRA 41; URS 57 and PAL 40 are correctly ask-side. **Floor capture here
is a simulation property, not a verified execution.**

---

## 2 — THE RESEAT LINEAGE, AND THE INVARIANT (F-VS-243)

**Verdict: the repricer class wearing the conviction's license — proven in the predicate's own
text.** `predictionSeatEvidenceChanged` (os:235-241) is a five-way disjunction whose first clause
compares `belief_book_receipt` — a tape-row cursor — and whose last is
`authority_conditioning_changed`, flipped by any bid/ask change. And the level it moves *to* comes
from a posterior that the live bid is enrolled into as a first-class evidence channel (os:472-496)
with a likelihood kernel centred on the bid (os:517-561). **Door 4 reads door 1's output and calls
it a conviction.**

| reseat | licensing receipt | what actually changed | the tell |
|---|---|---|---|
| **URS 57→58** | `URSPAL-PAL.csv.gz#row-30468` — the **sibling's book row** | floor receipt, floor value, shapes, survivor movement **all identical**; only the cursor and quote | 57 = prior ask−1; 58 = current ask−1 |
| **PAL 39→40** | `URSPAL-PAL.csv.gz#row-29931` — the adjacent book row | sole changed input **ask 47→48**, which flipped the gate from `PURE_PANEL_RECOMPOSITION_SUPPRESSED` to `MOVED_ON_NEW_MARKET_INPUT` | leg's own proposal that row was **31** (down 8) while the seat went up 1, labelled `SHIFTED_OWN_CONVICTION_UP` |
| **PRA 41→40** | the 42¢ print | `decisive_evidence.source = CAUSAL_LIVE_BOOK_BID, value 40` **is** the emitted level; the true-print channel sits at decisiveness 0, excluded | destroyed the leg — B2 credited PRA at 41 |
| **DAN 46→57** | DAN's own first 59 print | evidence genuinely new — but the level is bid 58−1; the 59 print excluded at decisiveness 0 | mixed: real trigger, book-derived number |

Census of all 11: **11/11 move toward a live touch, 0/11 away**; 6/11 land exactly on bid, bid−1 or
ask−1; 6/11 had no new print; **7/11 had byte-identical quotes**, two of which had no evidence
change of any kind (only the cursor advanced); **0/11 licensed by a shape or criterion overturn**;
proposal ≠ emission on 10/11. Across four different licensing lanes the credited numbers are
identical — URS 58, PAL 40 — because **the number is a function of the book, and every door reads
the book.**

**THE INVARIANT: THE BOOK IS VETO-ONLY.** No live-book quantity — bid, ask, book-row receipt or
cursor, or any boolean derived from their change — may **(i)** determine an emitted level,
**(ii)** transform an emitted level, or **(iii)** license, gate or unlock a change to a standing
level. The book's only lawful role is to **refuse** an emission. A level is a function of receipted
trade prints and the survivor/criterion set alone.

Per-door coverage: door 1 (bid-follow) closed by (i) — delete the `CAUSAL_LIVE_BOOK_BID` channel
and its kernel; door 2 (ask−1 clamp) closed by (ii) — the ask may veto, never re-price; door 3
(`ownEvidenceCentral ?? engineTarget`) closed by (i)+(iii); door 4 closed by (iii) — strike the two
book disjuncts, leaving the print- and criterion-derived ones. Rejected candidates, each with row
evidence: the *ratchet* and *monotone-descent* rules both block PAL 35→39, the one upward reseat on
a path to a fill, and monotone additionally **blesses the PRA row that destroyed a credit**;
*graded-HIT* is vacuous (every reseat is pre-fill).

**Measured cost of the invariant on this campaign: zero lost fills, three gains** — URS holds 57
and fills at 57; PAL holds 39 and fills at 39 (68.6 s later, inside the late-bell edge); PRA holds
41 and fills at 41, restoring B2's credit — while PAL 35→39 survives because its changed input was
the print-derived envelope high. **URSPAL would have been 57+39 = 96 = Δ4, exactly the required
spec**, lost to two reseats of 1¢ each.

One point in the build's favour, stated plainly: the five retired movers stayed dead. What the
build did was mint a **sixth** mover with a better name and grant it the one privilege the other
five were denied — moving a *seated* rest — then define its admission test to accept a book cursor.

---

## 3 — STORY STANDARD RULING (F-VS-244)

**All four stories FAIL as an unassisted-reader deliverable. 0/4. Four malformed confirms.**

FOUR_STORIES.md is **22,232,700 bytes of which 10,092 (0.045 %) is prose**; 99.573 % is VERBATIM
JSON, median ~130 KB *per physical line*, some lines 1.88 MB with premise and conclusion at
opposite ends. Concretely:

- **The campaign's first GIU floor capture is not narrated.** At that instant the transition line
  reads "Coherence=DISAGREES; BAR: HOLD_REST at 27 cents"; GIU is not named, and its credit exists
  only as `CREDITED_SIBLING_ENTRY=66` at char 142,074 of the following line. `"filled"` appears
  **zero times** in 22 MB.
- **4 of 11 reseats rendered.** The DAN 46→57 move — the largest in the build — is rendered as
  `HOLD_REST`, as are two other level changes.
- **20 of 47 belief blocks argue one number and act at another** (one argues 40 and seats 59; one
  argues 57 and seats 39 — opposite direction).
- **The ruler is never applied**: "floor" appears once in readable prose, "opportunity" zero times;
  two rendered reseats moved their leg a cent worse than the floor and neither cost is stated.
- **The build's own failure is suppressed** — `safety_floor_pass:false`, `self_stop_triggered:true`
  and three law violations appear nowhere in the story.
- Two stories end hours before their own fills; the only outcome table sits under a heading that
  disclaims it ("context, not verdict"); outcome rows contradict each other unreconciled.
- **F-VS-108: one hard violation** — a fill price with a live fill receipt and two predicted
  numbers ~60 chars away. Down from 5 at the prior corpus (where the values *diverged*); the
  emitter was never fixed.
- **F-VS-224 converse: LAJ's @59 fill scores ZERO** — no block in its story ever argues 59.
- The same package's TRADE_REPORT_FOUR.md carries exactly the missing sections in short lines.
  **The artifact named "story" is strictly less legible than the artifact named "report."**

**THE STORY-QUALITY BAR — filed as a standing requirement on every future confirm.** Twenty
mechanically checkable rules in four groups: *Legibility* (no line > 4,000 chars; prose ≥ 20 % of
bytes; no raw JSON in table cells; a Terms block). *Conviction before action* (every fill line
preceded in-story by its conviction block naming target, deadline and evidence receipt — a fill
without one scores **zero**; every seated level preceded within 2,000 chars by a sentence arguing
**that** level; every action names its reason in prose; `ACTIVE_TARGET_BEFORE_CENTS=N` lawful only
if N was rendered earlier; a rendered level change must carry a rendered action). *Selection* (the
decisive set is not optional: first placement, every reseat, the fill or terminal non-fill, and the
market's last transition, per leg; every reseat renders its movement evidence as prose once).
*Outcome and ruler* (a terminal prose exhibit per leg: final rest, fill and price, truth-table
floor, signed distance, pair delta; no outcome under a disclaiming heading; the authoritative row
named where rows disagree; self-stop and law violations stated in the first ten lines; the F-VS-224
grade stated before the appendix). *Floor* (no predicted number within 200 chars of a fill price;
every rendered fill price traceable to an in-story conviction). **A story needing narration is a
malformed confirm.** Requirements 1, 5, 6, 10, 12 and 16 alone would have caught every gap here.

---

## 4 — THE 19¢ LEDGER, REFRESHED (F-VS-245)

| leg | floor | B1 @8e8f7149 | B2 @27fc702f | B3 @801a62f6 | what ended the best seat |
|---|---|---|---|---|---|
| BAR | 27 | rest 27 | rest 27 | rest 27 | **byte-identical in all three**: a *fillable* 28 rest moved to an unfillable 25 by the prediction seat 2.24 h before the only 27 prints; the later 27 arrives 2.64 h after them |
| GIU | 66 | seat **66**, cancelled | fill 67 (+1) | **FILL 66 = FLOOR** | B1: post-only cancel of an at-floor rest; B3: `PREDICTION_SEAT_IMMUNITY_PRECEDES_EVERY_ROUTINE_MOVER` at the identical receipt — **the whole capture is one precedence flip** |
| URS | 57 | fill 58 | fill 63 (+6) | fill 58 | pre-seated at **57 with 8.67 h of runway in all three**; vacated by reprice 1,603.6 s before the only 57 print |
| PAL | 39 | fill 40 | rest 34 | fill 40 | seated 39; reseated to 40 on a book row 3.28 h early; the 40 fill lands 68.6 s *before* the 39 print |
| SVA | 41 | rest **41** (16 h late) | rest 35 | rest 39 | B1/B3 both reprice to 38 **on the receipt of the 41 print itself** |
| LAJ | 51 | fill 54 | fill 59 | fill 59 | the 52 seat — the winning ticket — walked up to 59 at bid-follow, 13.24 h before the first 51 print |
| DAN | 59 | rest 53 | rest 53 | rest 53 | library cell ends at 58 (F-VS-241, thrice-confirmed) |
| PRA | 41 | rest 40 | **FILL 41 = FLOOR** | rest 40 | perfect controlled experiment — same seat, same instant: B2's immunity pins the posterior at 41 and fills; B1 and B3 both re-round to 40, **B3 punching through its own immunity** |

**Banked: B1 = 2¢ · B2 = 0¢ · B3 = 2¢ of 19.** Only URSPAL ever completes (98/Δ2). Against the
campaign's best on record — **11¢ at @7889d9e1** — these three are a **9¢ regression**.

**Two claims corrected, both mine.** (i) **F-VS-239's width-zero table was wrong about LAJ**: each
trace's own floor-print stream carries **two** in-span 51 prints (@1784060123.219071 and
@1784077990.967, the latter 409 s inside `window_end` 1784078400) — a **4.96-hour** capture window,
not width zero. A LAJ rest left standing at 51 or 52 converts, and standing rests fill while the
machine sleeps (B2's PRA and B3's GIU both filled after their leg's last derivation). URS 57 and
PAL 39 remain genuinely single-print. (ii) **The width-zero class did not bind URS or PAL here** —
all three builds *achieved* the pre-seat F-VS-240 called for and discarded it by repricer. **The
binding constraint on those cents is tenure, not admission.** The one-beat-late law survives only
where the pre-seat was never built: SVA (7.65 s window, no store aims at 41) and DAN (library cell).

**Best-ever simultaneous bed: 15¢ of 19 (78.9 %)** — GIUBAR's Δ7 is now *component-proven*, both
halves converted in different builds and never together. The untouched 4¢ is **URS 1¢ + LAJ 3¢**,
and both live in one class: a floor that was seated, or nearly seated, and vacated hours early.

**And the trade nobody stated.** B3 is not an advance: **it buys GIU 66 by paying away PRA 41**,
which B2 had already banked. Net floor captures per build: B1 = 0, B2 = 1, B3 = 1. The order's own
framing — that the reseats cost URS 57→58 and PAL 39→40 as the price of GIU 66 — is refuted:
**B1 and B3 have byte-identical URS and PAL conduct.** GIU 66 was free; the reseat lane's actual
price was PRA. And B3's reseat rule **vacated three of the four floor seats its own receipt names**.

---

**One line:** the seats were moved by the book, wearing four different licenses; the story that
should have said so is 99.6 % JSON and never uses the word "filled."
