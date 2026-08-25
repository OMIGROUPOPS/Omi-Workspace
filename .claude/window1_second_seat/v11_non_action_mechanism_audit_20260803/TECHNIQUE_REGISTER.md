# THE TECHNIQUE REGISTER — decision path @4a96ded9

License: LAW_INDEX read this turn @ 2941cd15, sha256 `41784e6ab62d6341…` — verified against the order's `41784e6a…`. Laws: L8 L11 L18 L20 L22 · ONE OS · pattern law · welds.
Seat: CC verification. The findings branch and the build line are divergent (merge base 0591792d); the current decision-path tip is the latest build, **4a96ded9**. Every row below is pinned to that commit's code and measured on its custodied trace (2,781 leg-derivations, 22 orders, 7 fills).

## 1 — THE TECHNIQUE FRAME (operator ruling, 2026-08-25, filed verbatim)

> Everything the OS does individually is a **TECHNIQUE**; the objective is that all techniques hum together, never creating a contradictory environment; a new notion enters as an **added eye that strengthens the ultimate conclusion per side**, never as a gate that breaks another gate.

Applied to this history: the retired floor lock (F-VS-145), the upward-only violation metric, the supervisor that admitted the chase (F-VS-154), and the singleton fallback that cancelled a postable rest (F-VS-156/181) were all gates that broke other gates. The repairs that worked — the one-producer floor (F-VS-171), the named par bound, the one-decision arbitration (F-VS-179), the postable-rest hold — are added eyes.

---

## 2 — THE REGISTER

One row per technique. **Feeds** names the evidence store; **contributes** is what it adds to the per-side conclusion; **touches** names the techniques that read its output. Rows marked ● act in the decision path; ○ are receipt-only. Line references are `window1_v54_dual_belief_os.js` unless prefixed (`fos` = functionable_os, `sse` = survivor_shape_elimination, `build` = build_window1_v54_dual_belief).

### Evidence techniques (what the machine knows)

| # | technique | job, in operator language | domain | feeds on | contributes | touches |
|---|---|---|---|---|---|---|
| E1 ● | **Window binding** (`window_source`, `window_end_epoch`; fos) | fix the lawful clock — when the game starts, when the bell ends it | every receipt | truth table / operator rulings (L11) | the span every other technique is confined to | all phase math, deadlines, tenure, rearm windows |
| E2 ● | **Book reference series** (`referenceOf`, running low/high; fos:177-211 class) | keep a running picture of where the market *quotes* | every book row | ticks tape (bid/ask/last) | the live bid/ask each lane prices against; the conditioning low when no trade exists | every placement lane, post-only guards, E4 |
| E3 ● | **Running true-trade floor** (`running_true_trade_low_cents`; written on PRINT rows only; read at :667, :751, :837, :981) | the floor is what has actually traded — one producer, with the print receipt that set it | every print | prints tape | `evidenced_floor_cents` + receipt — the Definition-Lock floor | DISAGREES release, par bound, tenure, hold guard, same-receipt law, gate floor check |
| E4 ● | **Non-traded-low disclosure** (`conditioning_low_cents`, `book_path_low_source`, `non_traded_low_disclosure`) | when no trade exists yet, say so out loud and name the substitute | 279 rows this run | E2's mid-series minimum | a *conditioning* input to prediction, never a floor | belief (B1); the sentence; gate `NON_TRADED_LOW_DISCLOSED` |
| E5 ● | **Survivor-shape elimination** (sse; V18/V19 libraries @189eaa20; `candidate_final_floor_levels_cents`, overturn tests) | which final-low shapes are still possible, on the traded-low axis; eliminations permanent unless overturned | every receipt with prints | shape libraries + E3 | the admissible level ladder and shape support; the license `criterionSupportsLevel` (:91) | DISAGREES release, envelope snap (`supportedFloorLevel` :85), carried conviction, hold guard support |
| E6 ● | **Neighbor-conditioned belief** (`predicted_cents` = own low + library offset; `phase_central_estimate` q75; fos conditioning family) | what the future low *should* be, learned from similar games | every resolved receipt | E2/E4 low + foundation library + phase surface | the predicted cent and the q75 offset that price the coherent lane | envelope construction, Q75 lane, deadlines (E8) |
| E7 ● | **Micro-micro tick resolution + coherence test** (`coherentNow` :452-456; mirror gap ≤ spread ≤ `SPREAD_SETTLE_COHERENCE_MAX_CENTS` = 20 :11) | do the two legs' beliefs add up against the contract — if yes the belief may price; if no it may not | every receipt | both legs' beliefs + book | the COHERENT / DISAGREES / INSUFFICIENT_EVIDENCE switch that selects the placement lane | all placement lanes (the branch selector) |
| E8 ○ | **Fresh deadline** (`freshDeadline` :258; `SHOULD drift to X¢ by Y`) | say when the predicted move should have happened | every belief row | E6 + window | a stated expectation with an epoch — scoreable, not acting | sentences; deadline scoring table |

### Placement techniques (what the machine does, per side)

| # | technique | job | domain (this run) | feeds on | contributes | touches |
|---|---|---|---|---|---|---|
| P1 ● | **Coherent Q75 placement** (`CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE` :613; clamp + `supportedFloorLevel` snap; post-only `lawfulEnvelopeHigh = min(high, ask−1)`) | when the pair-read coheres, rest where the conditioned distribution says the low will be — **the only lane that rests below the observed low** | 2,304 rows; produced PAL 39 (the run's one below-low floor capture) | E5 + E6 + E7 + E2 ask | a belief-priced target inside the envelope, post-only guarded | allocator, arbitration, singleton (P2), hold guard (P6) |
| P2 ● | **Singleton consumption** (`chooseEnvelopePlacementTarget` :95) | when the belief narrows to one cent, stand on it — if the book will post it | 14 singleton rows; 8 unconsumed (all URS, 58 ≥ ask 58) | P1's envelope + E2 ask | consume-at-level or refuse with `ENVELOPE_POINT_AT_OR_ABOVE_LIVE_ASK` | P1, hold guard P6 |
| P3 ● | **DISAGREES own-evidence release** (`OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED` :667-671) | when the pair-read disagrees, the leg may still rest on its own *traded* evidence, if the survivor ladder licenses the level | 22 rows, 3 orders (BAR 27, GIU 67, LAJ 54) | E3 (runningTradeLow) + E5 license + E2 book-validity | a tape-priced target at the running low | arbitration; **lacks the post-only test P1/P6 have — F-VS-191** |
| P4 ● | **Live-touch lane** (`CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL` :747) | before any envelope exists, the live bid is the only evidence in sight | 243 rows; 0 orders this run | E2 bid/ask | a provisional bid-priced target (or hold) | arbitration; crossed-book cancel path |
| P5 ● | **Carried conviction** (`CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED` :714; F-VS-134/135) | a belief formed on evidence persists — carried while its eliminations hold and its basis is restated | 2 rows this run | prior envelope + E5 survivors | continuity of the prior conclusion where the current receipt is thin | P1 geometry; arbitration |
| P6 ● | **Postable-floor-rest hold** (`crossingSingletonBlocked && activeIsPostableFloor` :845-857; `POSTABLE_FLOOR_REST_HELD_WHILE_SINGLETON_CROSSES`) | never abandon a standing, postable rest just because the narrowed belief's own cent is un-postable | 8 rows (URS 57) | P2's refusal + E2 ask + captured-floor license + pair plan | a hold that outranks the null-target fallback | P1 (which may still reprice it away — C1), allocator |
| P7 ● | **Same-receipt established floor governs** (`SAME_RECEIPT_ESTABLISHED_FLOOR_GOVERNS` :768; the F-VS-185 repair) | when *this* receipt's print sets a new postable floor, no lane may price away from it on this receipt | 3 rows | E3 print on the current receipt + E2 ask | overrides the lane's proposal with the just-printed floor | all lanes (a senior pricing veto); pair conservation stays senior |
| P8 ● | **Hold previously licensed target** (`HOLD_PREVIOUSLY_LICENSED_ENVELOPE_TARGET` :659) | when coherent but nothing better is lawful, keep the standing licensed rest | 0 rows this run | P1's prior license | continuity of the last lawful price | arbitration |

### Conservation, execution, and repair techniques

| # | technique | job | domain | feeds on | contributes | touches |
|---|---|---|---|---|---|---|
| C1 ● | **Pair-par allocator + named floor bound** (`allocateUnderPar` :380; `PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND` = min(evidencedFloor, target); `PAR_BUDGET_CENTS` 99) | the two legs may never promise more than 99 together, and no reduction may cut through a traded floor | every 2-open-leg receipt | both lanes' targets + E3 bounds | the lawful joint plan, or `OBSERVED_TRADED_FLOORS_CANNOT_SATISFY_PAR` | every placement; fill handoff C3 |
| C2 ● | **One-decision arbitration** (one order per (leg, instant); `ONE_DECISION_PER_RECEIPT`) | one machine decision per instant per side — lanes propose, one wins, the loser is recorded | all 22 orders; multi-order set empty | all lanes' proposals | the single emitted order with winner/loser record | everything that acts |
| C3 ● | **Fill handoff pair cap** (:825, cap = 99 − sibling entry) | once one side is credited, the open side's budget is what remains | post-fill receipts | fill events + C1 | a hard cap on the surviving leg | P1-P3 targets post-fill |
| C4 ● | **Envelope-consistency check + atomic cancel/replace** (`activeInconsistent`; `FAIL_LOUD_NO_LAWFUL_ATOMIC_REPLACEMENT`) | a rest outside the current lawful envelope must be replaced this receipt or cancelled loudly | 4 cancels this run | active rest vs current envelope + ask | removal of unlawful rests, never silent | rearm C5 |
| C5 ● | **Rearm state machine** (F-VS-120; `REARM_PENDING` → re-derive every receipt → `REARM_RESOLVED_WITH_LAWFUL_REST`) | a cancelled side does not go silent — it re-derives until a lawful rest stands or the window ends | 4,438 attempt rows; all cancels armed and resolved | C4's cancels + all lanes | the way back after any cancel | all lanes on subsequent receipts |
| C6 ● | **Rest-priced crediting** (F-VS-107; `entry == prior_standing_target`, `print_at_or_below_rest`) | a maker fills at the price of its own resting bid — the only reportable price | all 7 fills | prints tape + standing rest | the credited entry per side | pair sums, bed verdicts, C3 |
| C7 ● | **Lawful-incomplete stamp** (F-VS-121) | when the floors themselves cannot satisfy par, abstention is the correct trade | DANPRA (59+41=100) | E3 both legs + C1 | a scored abstention instead of a forced completion | bed verdict |
| C8 ● | **Floor-rest tenure** (`AT_OBSERVED_TRADED_FLOOR_HOLDING`; episodes) | measure how long a rest stood at the traded floor | 3 episodes / 33 rows | E3 + active rest at evaluation instants | the tenure record (still half-blind — F-VS-190) | gate `AT_FLOOR_TENURE` |

### Accounting techniques (receipt-side; ○ = never act)

| # | technique | job |
|---|---|---|
| A1 ○ | **Sentence serialization + assertions** — every derivation states its full basis; `sentence_action_assertion` hard-asserts ACTION/TARGET agreement |
| A2 ○ | **Gate of 14 checks + executed counterexample probes** — pass computed from failures; `can_fail` from an executed probe (probes are twins — F-VS-187) |
| A3 ○ | **Determinism ×2** — byte-identical replay before any score is emitted |
| A4 ○ | **Custody / literal / producer audits** — L22 custody with sha256; 136 raw literals 0 named; 61/61 receipts have writers |
| A5 ○ | **Two-way street attribution** (F-VS-122) and the **honest-baseline pins** with `run_source` (F-VS-170 repair) |

---

## 3 — CONTRADICTION AUDIT

A contradiction = two internal rules wanting opposite things: two techniques able to issue conflicting instructions about the same leg on the same receipt, or one technique's output invalidating another's premise. Fired contradictions first, each with its state. (The word PAIR is reserved for its one meaning — both legs of a game owned/completed — and is not used for these entries.)

### Fired contradictions

| contradiction | the collision | deciding mechanism | state |
|---|---|---|---|
| **P6 × P1** — hold guard vs coherent reprice (**tenure/belief-drift**) | P6 holds URS's postable 57 for 508 s; at ln1372 ts 1784031096 the ask moves to 59, the singleton 58 becomes postable, and **P1 reprices the held rest up to 58** — while 57 is still postable and is the level that prints. Cost: the URSPAL cent (97 vs 96) | none — P6's guard term `crossingSingletonBlocked` goes false and P1 simply wins by branch order | **UNMANAGED.** No stated rule says whether a standing postable rest at a *deeper* price outranks the belief's newly-postable level. This is the exact "gate breaks gate" the frame forbids: the hold was added as an eye, and P1 overrides it without a recorded adjudication |
| **P3 × post-only** — DISAGREES release vs the maker premise (**guard/singleton family**) | P3's guard validates the *book* (`liveBid < liveAsk`) but never the *target*: ln83 GIU `PLACE 67` against ask 66 (above the offer), ln2902 LAJ `PLACE 54` against ask 54 (at the offer). P1 and P6 both carry the target-level test; P3 does not | none — the guard is absent | **UNMANAGED** (F-VS-191). One term (`ownEvidenceTarget < liveAsk`) reconciles it. Until then the OS applies two different definitions of "postable" depending on lane — a Definition-Lock violation on the term *postable* |
| **C4 × P6-economics** — consistency cancel vs postable rest (**cancel/rearm**) | C4 cancels rests the envelope disowns even when they are postable and economically sound: PAL 38 @1784020558 (ask 39), DAN 58 @1784342469 (ask 59). P6 protects exactly this situation but only when a *singleton crosses* — neither row carries a singleton, so the guard is unreachable | C5 re-arms and re-derives (both resolved) | **PARTIALLY MANAGED.** The rearm path always recovers *a* rest, but not the price: DAN's re-placed 58 never fills. The hold law is scoped to one trigger; the general rule ("never cancel a postable rest without an economic reason") is unstated |
| **P3 × P1** — lane vs lane (**lane/lane**) | Both lanes can propose different targets for one leg on one receipt. Order-level: managed since be412a2f — C2 emits one order per instant (22/22 singletons). Level-selection: P3 rests **at** the running low (can never beat the last print); P1 rests **below** it. The structural residue is the 5 achievable cents of F-VS-189 | C2 arbitration (order level); nothing at level-selection | **PARTIALLY MANAGED.** The collision no longer produces thrash; it still produces the wrong level whenever P3 wins on a leg whose next print will be deeper |
| **P7 × all lanes** | The same-receipt floor law overrides any lane's proposal when this receipt's print establishes a postable floor — fired 3 times, cleanly, with `prior_mode`/`prior_target_cents` recorded | explicit seniority written into P7, pair conservation stated as senior above it | **MANAGED** — the model resolution: seniority stated, both sides recorded |
| **C1 × E3** — allocator vs floors | When both floors sum over par the allocator refuses (`OBSERVED_TRADED_FLOORS_CANNOT_SATISFY_PAR`) rather than cutting through a floor | C7 stamps the abstention | **MANAGED** (DANPRA: 100 vs 99 → lawful incomplete) |
| **E1 × truth table** — window vs governing span | DANPRA's window runs to the bell 1784373060 while the governing span ends 1784372160; 900 s of tail in which techniques act outside the scored span | none | **UNMANAGED** (F-VS-166); benign this run, unpriced in general |
| **C8 × P1** — tenure vs below-low rests (measurement contradiction) | Tenure credits only `active == evidencedFloor`; P1's best behaviour — resting *below* the observed low (PAL 39 vs low 40, 18,818.6 s) — scores zero, and GIU's 1,589.2 s at its floor scores zero for want of evaluation instants | none | **UNMANAGED** (F-VS-190). Not a decision conflict, but the measuring eye contradicts the acting eye: what tenure rewards is not what fills |

### Unfired contradictions waiting to fire

| contradiction | the waiting collision | state |
|---|---|---|
| **P5 × P1** — carried conviction vs current belief | P5 fired twice as HOLDs. If a carried envelope ever *proposes a price* while P1 proposes another on the same receipt, branch order decides (`:566` coherent before `:714` carried) with no stated precedence law | UNMANAGED in law, managed by accident of branch order |
| **P6 × C1** — hold vs allocator reduction | P6 checks `pairPlanLawful` at :851 before holding, but if the *sibling* subsequently rises so the held rest violates par, C1's reduction and the hold have no stated winner | UNMANAGED; unexercised |
| **P7 × C1** — same-receipt floor vs pair budget | P7 states "pair conservation remains senior" — the resolution *is* stated; a case where the just-printed floor would breach par has not yet occurred | MANAGED (stated), unfired |
| **P4 × crossed book** | The touch lane nulls the target when `bid ≥ ask` (:750-class); DAN's crossed-book cancel is now armed by C5. The waiting case: a crossed book *while a postable rest stands* — does the null target cancel the rest? The be412a2f DAN row suggests yes | PARTIALLY MANAGED (rearm catches it); the cancel itself unstated |
| **A2 × every gate** — probe twins | The falsifiability probes are hand-written twins of the production predicates (F-VS-187); a drifted production predicate would still show `can_fail: true`. A meta-gate that can bless a broken gate | UNMANAGED |
| **P2 × P3** — singleton vs DISAGREES on one leg | P2 lives inside the coherent branch and P3 in the DISAGREES branch, so they are mutually exclusive by E7's switch — the branch selector is the stated resolution | MANAGED by construction |

### The audit in one sentence

Under the ZERO CONTRADICTIONS ruling (§4): every entry above is a CONTRADICTION and every one is OPEN. Seniority contracts — P7's stated seniority, the one-decision arbitration, the lawful-incomplete stamp, the carried/coherent branch precedence — are TRIAGE: they stop the bleeding at a fired contradiction but do not close it. A contradiction closes only when the overlap that created it is dissolved by design, as the coherence switch dissolves singleton×DISAGREES (the two can never be live together). The two open contradictions that have already cost cents (P6×P1, P3×post-only) share one root: a technique that exists in one lane and not another — the contradictory environment the Technique Frame outlaws.

---

# ADDENDUM — 4-lane sweep returned; register extended, one misattribution corrected, one lane claim rejected under the corrections law

Filed as F-VS-196 … F-VS-198. Every row re-checked before filing.

## A — Corrections to the register and audit

**(a) The DAN cancel was misattributed.** F-VS-195(iii) charged it to the consistency check. The actual writer is the **locked-book nullifier — `os.js:750`**: `if (!formationComplete || (liveBid && liveAsk && liveBid >= liveAsk)) targets[legId] = null` — which on a locked book (DAN ln4526, bid 59 / ask 59, `crossed_book: true`) nulls the target regardless of the standing rest, turning a placement law silently into a cancellation law, under an emitted reason that misattributes it (`OWN_EVIDENCED_LIVE_TOUCH_ENVELOPE_NULL`). Narrowing that matters: the same-receipt floor law (:763) and floor-rest protection (:802) both run *after* :750 and re-impose a target — so an active rest standing **at** the supported evidenced floor survives a locked book; the unmanaged blast radius is **below-floor rests specifically**, exactly the population the hold-guard commit was written to protect. W5 joins the register as a technique in its own right.

**(b) Register additions** (all verified at 4a96ded9):
- **Neighborhood retrieval engine** — `SIMILARITY_DECLARATION` (fos:52-92, 14 hand-authored weights/scales, 7 neighbors, leave-self-out asserted at build:944). The engine every conditioned quantity descends from, previously catalogued only via its consumers.
- **Evidence-match conditioning weights** — `weight = score × coverage × 1/(1+|ownDip−memberDip|)` (fos:549-551) → `conditioning_weight` (os:156). The weights behind every conditioned quantile.
- **Formation/crossed-book veto (W5)** — os:750, above.
- **Standing-rest captured-floor license** — build:966-981 writes `standing_governing_floor_cents/receipt`; os:841 reads it as the hold's first authority. Stamped only on PLACE/REPRICE and only for the SAME_RECEIPT/EVIDENCED_FLOOR modes — **a DISAGREES placement at the traded low is never captured**, so its future holds ride the `?? floor` fallback at :844.
- **Decision cadence machinery** — turning epochs + FILL_HANDOFF/ATOMIC_REARM triggers (build:784-812): determines when decisions can exist at all.
- **Named-subset execution guard** — `window1_named_subset_guard.js`, FAIL_LOUD on unrequested/duplicate/incomplete games.
- **Atomic pair-sum nulling** — os:896-900: when both held actives survive individually but sum > 99, **both are nulled** — the branch that turns one unlawful allocation into a two-leg cancel.
- **Envelope-high provenance** — the coherent envelope's ceiling is the **drift reader's current reference level** (os:288, 337), which by `referenceOf`'s ladder can be a print, a book last-trade, **or a floored mid** — a "high" with a non-book source, Definition-Lock adjacent.

**(c) Re-labelled:** the entire base pricing chain — touch pricing, mind-window vote, **V3 map re-keying, joint depth license**, base post-only/pair caps — is **displaced to telemetry**: `deriveJointActions` overwrites `row.action` on every emitted derivation (os:1163-1183). Dead at tip: `lineageTarget` (os:371-378), `supportingShapeIdsForLevel` (os:103-109), the full `similarity` variant, and — dormant with a **contradicting reduction rule** — `allocatePairActions` (fos:844-933, grade-proportional, exported, zero call sites) beside the live headroom-greedy `allocateUnderPar`. Floor-rest protection (os:802-819) fired **0 times** this run.

**(d) C2 qualified:** one order per instant holds **per leg**. The 22 orders occupy **18 instants** — four instants carried sibling pairs (both legs of one game); pair-level simultaneity is governed only by the joint allocation sum. My F-VS-179/186 measurements were per (leg, instant) and stand.

**(e) One lane claim REJECTED under the corrections law.** The audit's P11 claimed URSPAL's PAL fill landed 26.6 s past the span edge, citing c0056976's `span_end 1784042040`. **W1TT-C-002 governs and sets URSPAL's span_end to 1784042247** — the PAL fill at 1784042066.596 is *inside* the governing span by 180.4 s. Both the lane and its verifier read the uncorrected table — the seat's oldest named failure mode. The DANPRA half (bell 1784373060 consumed vs governing span_end 1784372160, 900 s tail) stands, as filed in F-VS-166.

## B — A fifteenth contradiction, fired and open (P12)

**The same-receipt floor law's violation detector fires where no writer can act.** Its writer is guarded on `Number.isInteger(active)` (:763); its detector is not (:990-995). Trace **ln41, ts 1783833752.027, GIU**: floor 70 established at this epoch, postable (< ask 71), **no active rest**, the DISAGREES lane lawfully refuses origination — and the row is stamped `floor_rest_protection.violation: true`, **the only violation=true row in the bed**. One technique's measurement brands unlawful an outcome the writers' guards make inevitable. Nothing routes it. Also noted: the law is **epoch-grain**, not receipt-grain (`timestamp_epoch === state.current_epoch`, :756) — a floor print at the same epoch under a different receipt still triggers it; and the arbitration serializes `winningLane: "SAME_RECEIPT_ESTABLISHED_FLOOR"`, a lane name absent from `laneEligibility` (:953-959), on 3 receipts that list all five named lanes as losers — a consumer keying winners to lane names drops those decisions.

## C — Tenure now has three instruments giving three answers (extends F-VS-190)

1. The **in-OS recorder** (:1077, requires `active === evidencedFloor`) says `NO_ACTIVE_EVIDENCED_FLOOR_TENURE` on **all 8 hold rows** (active 57, evidenced floor 58).
2. The **harness table** (`EVIDENCED_FLOOR_TENURE_TABLE.json`) counts the identical URS episode as governing-floor tenure — `BELOW_RUNNING_TRADED_LOW, runlow 58, 2,827 s`.
3. And the table **over-counts on a third axis**: DAN lv 52 (1784332553→1784339622) is `counted_as_governing_floor_tenure: true` for 315.2 s with `running_traded_low_at_stand: null` — build:1637-1643 falls back to *any print at or above the rest* to start "governing floor tenure", including when **no traded floor exists at all**.

## D — Latent contradictions added to the audit

- **U1 — post-allocation writers vs the axis.** The par reduction (never fired — the reconciliation branch appears in 0 of 2,781 rows, so **the named floor bound has never actually reduced a target**) and the fill-handoff cap (never bound) both emit cents that are **never re-snapped to `candidate_final_floor_levels_cents`**. The first real squeeze breaks the traded-low-axis premise silently.
- **U2** — floor protection (W7) zeroes headroom; if the pair then goes par-infeasible while DISAGREES, the atomic fallback's hold test requires a decision envelope DISAGREES never has → the "protected" rest is cancelled by machinery ranked junior to it.
- **U3** — the carried lane's `: active` fallback (:706/:708) can hold a rest outside the carried envelope while the mode sits in the authoritative list → `VIOLATION_STALE_REST_SURVIVED` with no repair path.
- **U4** — asymmetric consistency coverage: `HOLD_PREVIOUSLY_LICENSED_ENVELOPE_TARGET` and `SAME_RECEIPT_ESTABLISHED_FLOOR_GOVERNS` escape `activeInconsistent` entirely.
- **U5** — a DISAGREES running-low above `99 − siblingEntry` would be capped into an unsupported level after licensing (GIU came within 5¢: target 67, cap 72).
- **U6** — the dormant second allocator: two par arithmetics for one pair the day anything wires it.

**And the P5 contradiction sharpened into a sentence the frame was written for:** LAJ's rearm — opened by the coherent lane's lawful cancel — was resolved 4.5 hours later **by the DISAGREES lane's crossing 54-at-the-ask order (F-VS-191)**. The repair machinery delivered its repair through the one unguarded lane. Techniques not humming together is not an abstraction; it is the LAJ fill.

---

## 4 — ZERO CONTRADICTIONS (operator ruling, 2026-08-25, filed verbatim)

> **ZERO CONTRADICTIONS** — "2 internal rules wanting opposite things" is a CONTRADICTION; there should be **0 contradictions anywhere**; the OS synergizes, never disagrees with itself. Vocabulary corrected throughout the register: these entries are renamed **CONTRADICTIONS** (the word **PAIR** keeps its one meaning — both legs of a game owned/completed). **Seniority contracts are TRIAGE, not the standard** — each contracted contradiction stays open on the register until the overlap that created it is dissolved by design. No other change.

### The register scoreboard under the ruling

| state | count | entries |
|---|---:|---|
| **DISSOLVED BY DESIGN** (the overlap cannot exist) | **1** | singleton×DISAGREES — mutually exclusive branches of the coherence switch. (The verified non-collisions — W6-then-W10, W10 double-reinsertion, live-touch×crossed-book closure — were never contradictions.) |
| **CONTRACTED — OPEN** (triage in place: a stated seniority, arbitration, or stamp) | **6** | P7×lanes (stated seniority) · allocator×floors (lawful-incomplete stamp) · carried×coherent (branch precedence + arbitration record) · lane×lane order-thrash (one-decision arbitration; level-selection overlap remains) · singleton×post-only (the min() chooser) · per-leg arbitration (pair-level simultaneity governed only by the joint sum) |
| **UNCONTRACTED — OPEN** | **13** | hold×coherent-reprice (the URS surrender) · DISAGREES×post-only (crossing bids) · locked-book nullifier×below-floor rests · cancel-economics×consistency · rearm-resolution-lane unspecified · tenure×below-low rests (three instruments, three answers) · window-bell×governing-span (DANPRA) · same-receipt-detector×writer-guards (P12) · U1 post-allocation×axis · U2 protection×atomic-fallback-in-DISAGREES · U3 carried-fallback×consistency · U4 modes escaping activeInconsistent · U5 DISAGREES×fill-cap · U6 dormant second allocator |

**Zero is the standard. Nineteen contradictions are catalogued; one is dissolved; eighteen are open** — six with triage, thirteen without (the level-selection overlap inside the arbitrated lane×lane entry keeps that entry open despite its contract). Every triaged entry remains on this register until a build removes the overlap itself: one post-only definition for every lane, one cancellation law, one tenure instrument, one allocator, one clock.

---

## 5 — THE FUNCTION AUDIT (standing; operator ruling, 2026-08-25, filed verbatim)

> **EVERY SINGLE FUNCTION HAS A FUNCTION** — everything that has an effect on OS opinion and sentiment is **validated** (source proven, provenance stated, consumed by a named decision); anything in the decision path that **affects nothing or duplicates another's job is a defect** (dormant allocator class), and anything **unvalidated that shapes sentiment is a contamination** (midpoint-low class). Standing audit: the register gains a column — each technique's inputs **VALIDATED yes/no**, and each technique's output **CONSUMED BY** whom; blanks are findings. No other change.

The column, normalized as one audit table keyed to the register's row numbers. **VALIDATED** = every input has a proven source and stated provenance. **CONSUMED BY** = the named decision that reads the output. Anything not YES / not a named decision is a finding, cited.

| # | inputs VALIDATED? | output CONSUMED BY | finding |
|---|---|---|---|
| E1 window | **partial** — 3 of 4 games operator-ruled/machine; DANPRA is `TAPE_INFERENCE` and the consumption edge runs 900 s past the governing span | phase math, deadlines, rearm window, the tape-consumption filter (build:1344) | F-VS-166 open |
| E2 reference series | **partial** — the tape is receipt-proven, but the third branch of `referenceOf` is a **computed midpoint**, and via the drift reader it becomes the **coherent envelope's HIGH** (os:288/337) with no disclosure — the same class E4 discloses on the low side | drift reader, lows_travel, DISAGREES book-validity, **envelope high** | **NEW — the envelope-high midpoint channel is an undisclosed sibling of the midpoint-low contamination** |
| E3 traded floor | **YES** — print receipt on the same object; the gate recomputes it from the raw tape prefix | P3 target, par bound (C1), tenure (C8), hold (P6), same-receipt law (P7), gate | — (the model row) |
| E4 non-traded-low disclosure | **YES** — basis, producing branch and source receipt stated; sentence carries it | E6 conditioning | — (the remediated contamination the ruling names) |
| E5 survivor shapes | **mostly** — libraries sha256-bound @189eaa20, custody verified; **but** high/low orientation is frozen at the first book bid (sse:225), an input with no stated validation | P3 license, envelope snap, P6 support, P5 | orientation input unvalidated |
| E6 conditioned belief | **partial** — foundation library and phase surface are sha-bound; the conditioning low is disclosed; **but the 14 similarity weights/scales (fos:52-92) and the evidence-match formula `1/(1+|dipΔ|)` (fos:549-551) are hand-authored values with stated provenance and NO source proof** — unvalidated numbers shaping every conditioned quantile | envelope construction, P1 pricing, E8 | **NEW — contamination class: hand-authored weights shape sentiment unvalidated** |
| E7 coherence switch | **partial** — beliefs and book are proven; `SPREAD_SETTLE_COHERENCE_MAX_CENTS = 20` (os:11) is a numeric constant with no operational derivation (the literal audit covers booleans only) | the lane selector — every placement | the 20 is an unvalidated sentiment-shaping constant |
| E8 freshDeadline | YES (E6 + window) | deadline scoring table, sentences | — (scoreable, consumed) |
| P1 coherent Q75 | YES (E5/E6/E7 + ask) | arbitration → orders; produced the run's only below-low floor capture | — |
| P2 singleton | YES | P1 target / refusal reason; P6 trigger | — |
| P3 DISAGREES release | **partial** — its inputs are proven (E3 + E5) but its own postability premise is unvalidated: no `target < ask` test | arbitration → 3 orders | F-VS-191 open |
| P4 live-touch | YES (bid/ask + receipt) | arbitration; 0 orders this run | — |
| P5 carried conviction | YES (prior envelope + survivors, basis restated) | arbitration; 2 HOLDs | — |
| P6 postable hold | YES (ask + captured-floor license + pair plan) | allocation re-insert → held orders | license never stamped on DISAGREES placements (F-VS-196b) |
| P7 same-receipt floor | YES (print on the current epoch + ask) | overrides every lane's proposal; 3 rows | detector/writer guard mismatch (F-VS-197) |
| P8 hold-previously-licensed | YES | arbitration; **0 rows** — live branch, unfired this bed | watch: unfired ≠ dead |
| C1 allocator + bound | YES (targets + E3 bound) | the joint plan; every order | **the reduction branch has fired 0 times — the bound has never reduced a target, and its output is not re-snapped to the axis (U1)** |
| C2 arbitration | YES (all lanes' proposals) | the emitted order; winner/loser record | per-leg only (F-VS-196d) |
| C3 fill-handoff cap | YES (fill events) | post-fill targets | cap never bound; if it binds, output un-snapped (U1) |
| C4 consistency + atomic | YES (rest vs envelope + ask) | cancels/replacements | two modes escape the check (U4) |
| C5 rearm | YES (cancels + lanes) | the next lawful rest | resolution lane unspecified (F-VS-198) |
| C6 rest-priced crediting | **YES** — trade_id resolved in the print store, entry == rest asserted | pair sums, bed verdict | — |
| C7 lawful-incomplete | YES (E3 both legs + par) | bed verdict | — |
| C8 tenure | **NO** — three instruments give three answers on one episode, one counts tenure where no traded floor exists | gate `AT_FLOOR_TENURE` | F-VS-190/198 open — an unvalidated measurement shaping the gate |
| A1 sentences | YES (hard asserts vs the row) | operator reading; gate substring checks | — |
| A2 gate + probes | **partial** — `passed` computed from failures; **the probes are hand-written twins, one a constant** | the bed verdict | F-VS-187 open |
| A3 determinism | YES | score emission license | one-host limit stated |
| A4 custody/literal/producer audits | YES (sha256 / scan / writer search) | L20/L22 compliance | classifier-by-line-shape caveat (F-VS-183) |
| A5 attribution + pins | YES (`run_source` on both objects) | bed comparison | — |

### Defects under the ruling, by its two named classes

**Dormant-allocator class (in the decision path, affecting nothing or duplicating another's job)** — all verified at 4a96ded9:
1. **`allocatePairActions` + `rewriteAllocatedAction`** (fos:828-933) — a second, dormant allocator with a grade-proportional reduction rule that **contradicts** the live headroom-greedy `allocateUnderPar`; exported, zero call sites (U6).
2. **`lineageTarget`** (os:371-378) and **`supportingShapeIdsForLevel`** (os:103-109) — defined, never called.
3. **The full `similarity` variant** (fos:385-407) — dead; nothing consumes even a hash of it.
4. **The displaced base pricing chain** — touch pricing, mind-window vote, V3 map re-keying, joint depth license, base post-only/pair caps: every emitted action overwrites their work (os:1163-1183). They duplicate the dual layer's job and affect no order.
5. **Floor-rest protection's writer** (os:802-819) — fired 0 times while its **detector** fired once where no writer could act (F-VS-197): a function whose only output this run was an unroutable violation.

**Midpoint-low contamination class (unvalidated, shaping sentiment)**:
1. **The envelope-high midpoint channel** — the coherent envelope's ceiling is the drift reader's reference level, whose third source is `floor((bid+ask)/2)`; unlike the low side (E4), **nothing discloses when the high is mid-derived**. New finding.
2. **The 14 hand-authored similarity weights and the evidence-match formula** — stated, never validated against any store; they shape every neighborhood and therefore every conditioned belief. New finding.
3. **`SPREAD_SETTLE_COHERENCE_MAX_CENTS = 20`** — the constant that decides which lane may price, with no operational derivation on record.
4. *(Remediated exemplar)* the midpoint low itself — now disclosed per-row with its producing branch and receipt (E4); the class's name survives as the standard.

**Blanks-are-findings summary: 0 blank cells; 11 rows carry a finding.** Three are new to this audit — the envelope-high midpoint channel, the unvalidated similarity weights, and the unvalidated coherence constant — filed under F-VS-200.

