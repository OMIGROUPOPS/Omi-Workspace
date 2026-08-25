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

A contradiction = two techniques able to issue conflicting instructions about the same leg on the same receipt, or one technique's output invalidating another's premise. Fired pairs first, each with its state.

### Fired pairs

| pair | the collision | deciding mechanism | state |
|---|---|---|---|
| **P6 × P1** — hold guard vs coherent reprice (**tenure/belief-drift**) | P6 holds URS's postable 57 for 508 s; at ln1372 ts 1784031096 the ask moves to 59, the singleton 58 becomes postable, and **P1 reprices the held rest up to 58** — while 57 is still postable and is the level that prints. Cost: the URSPAL cent (97 vs 96) | none — P6's guard term `crossingSingletonBlocked` goes false and P1 simply wins by branch order | **UNMANAGED.** No stated rule says whether a standing postable rest at a *deeper* price outranks the belief's newly-postable level. This is the exact "gate breaks gate" the frame forbids: the hold was added as an eye, and P1 overrides it without a recorded adjudication |
| **P3 × post-only** — DISAGREES release vs the maker premise (**guard/singleton family**) | P3's guard validates the *book* (`liveBid < liveAsk`) but never the *target*: ln83 GIU `PLACE 67` against ask 66 (above the offer), ln2902 LAJ `PLACE 54` against ask 54 (at the offer). P1 and P6 both carry the target-level test; P3 does not | none — the guard is absent | **UNMANAGED** (F-VS-191). One term (`ownEvidenceTarget < liveAsk`) reconciles it. Until then the OS applies two different definitions of "postable" depending on lane — a Definition-Lock violation on the term *postable* |
| **C4 × P6-economics** — consistency cancel vs postable rest (**cancel/rearm**) | C4 cancels rests the envelope disowns even when they are postable and economically sound: PAL 38 @1784020558 (ask 39), DAN 58 @1784342469 (ask 59). P6 protects exactly this situation but only when a *singleton crosses* — neither row carries a singleton, so the guard is unreachable | C5 re-arms and re-derives (both resolved) | **PARTIALLY MANAGED.** The rearm path always recovers *a* rest, but not the price: DAN's re-placed 58 never fills. The hold law is scoped to one trigger; the general rule ("never cancel a postable rest without an economic reason") is unstated |
| **P3 × P1** — lane vs lane (**lane/lane**) | Both lanes can propose different targets for one leg on one receipt. Order-level: managed since be412a2f — C2 emits one order per instant (22/22 singletons). Level-selection: P3 rests **at** the running low (can never beat the last print); P1 rests **below** it. The structural residue is the 5 achievable cents of F-VS-189 | C2 arbitration (order level); nothing at level-selection | **PARTIALLY MANAGED.** The collision no longer produces thrash; it still produces the wrong level whenever P3 wins on a leg whose next print will be deeper |
| **P7 × all lanes** | The same-receipt floor law overrides any lane's proposal when this receipt's print establishes a postable floor — fired 3 times, cleanly, with `prior_mode`/`prior_target_cents` recorded | explicit seniority written into P7, pair conservation stated as senior above it | **MANAGED** — the model resolution: seniority stated, both sides recorded |
| **C1 × E3** — allocator vs floors | When both floors sum over par the allocator refuses (`OBSERVED_TRADED_FLOORS_CANNOT_SATISFY_PAR`) rather than cutting through a floor | C7 stamps the abstention | **MANAGED** (DANPRA: 100 vs 99 → lawful incomplete) |
| **E1 × truth table** — window vs governing span | DANPRA's window runs to the bell 1784373060 while the governing span ends 1784372160; 900 s of tail in which techniques act outside the scored span | none | **UNMANAGED** (F-VS-166); benign this run, unpriced in general |
| **C8 × P1** — tenure vs below-low rests (measurement contradiction) | Tenure credits only `active == evidencedFloor`; P1's best behaviour — resting *below* the observed low (PAL 39 vs low 40, 18,818.6 s) — scores zero, and GIU's 1,589.2 s at its floor scores zero for want of evaluation instants | none | **UNMANAGED** (F-VS-190). Not a decision conflict, but the measuring eye contradicts the acting eye: what tenure rewards is not what fills |

### Unfired pairs waiting to collide

| pair | the waiting collision | state |
|---|---|---|
| **P5 × P1** — carried conviction vs current belief | P5 fired twice as HOLDs. If a carried envelope ever *proposes a price* while P1 proposes another on the same receipt, branch order decides (`:566` coherent before `:714` carried) with no stated precedence law | UNMANAGED in law, managed by accident of branch order |
| **P6 × C1** — hold vs allocator reduction | P6 checks `pairPlanLawful` at :851 before holding, but if the *sibling* subsequently rises so the held rest violates par, C1's reduction and the hold have no stated winner | UNMANAGED; unexercised |
| **P7 × C1** — same-receipt floor vs pair budget | P7 states "pair conservation remains senior" — the resolution *is* stated; a case where the just-printed floor would breach par has not yet occurred | MANAGED (stated), unfired |
| **P4 × crossed book** | The touch lane nulls the target when `bid ≥ ask` (:750-class); DAN's crossed-book cancel is now armed by C5. The waiting case: a crossed book *while a postable rest stands* — does the null target cancel the rest? The be412a2f DAN row suggests yes | PARTIALLY MANAGED (rearm catches it); the cancel itself unstated |
| **A2 × every gate** — probe twins | The falsifiability probes are hand-written twins of the production predicates (F-VS-187); a drifted production predicate would still show `can_fail: true`. A meta-gate that can bless a broken gate | UNMANAGED |
| **P2 × P3** — singleton vs DISAGREES on one leg | P2 lives inside the coherent branch and P3 in the DISAGREES branch, so they are mutually exclusive by E7's switch — the branch selector is the stated resolution | MANAGED by construction |

### The audit in one sentence

Of the fourteen pairs, **four are managed** (two by explicit stated seniority — P7's law is the model the frame asks for), **four partially managed**, and **six unmanaged** — and the two unmanaged pairs that have already cost cents (P6×P1, P3×post-only) share one root: a technique that exists in one lane and not another, which is precisely the "contradictory environment" the Technique Frame outlaws. The frame's test for any future build: a new notion must either state its seniority against every technique it touches (as P7 does) or change no other technique's output.
