# DEFINITION-REPAIR COUNTER-GRADE — @453296b7

License: LAW_INDEX read this turn @ 453296b7, sha256 `41784e6ab62d6341…` — verified against the order's `41784e6a…`. Laws: L8 L11 L18 L20 L22 · DEFINITION LOCK (F-VS-163) · TWO-WAY STREET F-VS-122 · welds.
Seat: CC verification. Every number measured by me from the custodied trace (112,805,539 B / 1,796 DECISION_STAGE / 62,570 REARM_ATTEMPT / 5 FILL_EVENT / **3,509 leg-derivations**), the raw print store, and the code at 453296b7. Governing floors: W1TT-C-001 GIUBAR, W1TT-C-002 URSPAL; LAJSVA and DANPRA from c0056976. `PAR_BUDGET_CENTS = 99`.

## Headline

**The definition repair is real and it bought a fill.** "Floor" now has one producer — the observed traded low, with the print receipt that set it — and the belief fallback is gone from every row. The par bound is named, emitted on all 3,509 rows, and never above the traded floor. SVA captured its 41 at 1784020209.484, the fill my F-VS-154 measured as lost by 2.516 s. **Against that: the two lanes now fight inside a single receipt — orders went 60 → 309, with up to 10 on one leg at one timestamp — and `can_fail` is decided by comparing two typed labels.**

---

## 1 — Verification

### The floor definition at the repaired site — REPAIRED

`window1_v54_dual_belief_os.js:745` and `:865`, both sites identical:
```js
const evidencedFloor = cent(state.legs[legId].running_true_trade_low_cents);
const evidencedFloorReceipt = evidencedFloor === null ? null
  : [...state.legs[legId].prints].reverse().find((row) => cent(row.price_cents) === evidencedFloor)?.receipt ?? null;
```
The `floorEvidenceCandidates` array and its `?? candidates[0]` fallback are **gone**. One definition, and the source is a **print receipt** carried on the same object.

Census over all 3,509 derivations: `evidenced_floor_source` = `OBSERVED_TRUE_TRADE_PRINT` **3,223**, `null` **286**. **`CURRENT_SURVIVOR_ENVELOPE_LOW` appears zero times.** F-VS-159 is closed. Cross-check: the evidenced floor is at or above the envelope low on every row it coexists with one (2,392 above, 283 equal, **0 below**) — the belief is now the conservative number and the tape is the floor.

### The 286 disclosures and the 201 / 151 changes — REPRODUCED

`own_evidence.basis` is `BOOK_PATH` on **286** rows, `TRUE_TRADE` on 3,223 — exactly matching the 286 rows with no traded floor. Every one of the 286 carries
`non_traded_low_disclosure: "BOOK_PATH_REFERENCE_NOT_A_TRADE:BOOK_BID_ASK_MID_SERIES_FLOORED_NON_TRADE"`,
and it is **in the sentence** (`os.js:1032`, `NON_TRADED_LOW_DISCLOSURE=`). The disclosure names the mid-quote branch I filed in F-VS-169 verbatim.

`LOW_SOURCE_REPRICE_RECEIPT.json`: `changed_order_count` **201** (I count 201 rows in `changed_orders`), and `DEFINITION_REPAIR_SUMMARY.json` gives `changed_target_rows` **151** — PAL 70 · URS 46 · LAJ 28 · SVA 1 · DAN 5 · PRA 1. The summary also reconciles against my own count: `cc_expected_non_trade_rows: 283`, `executable_non_trade_rows: 286`, `executable_difference_vs_cc_count: 3` — my 283 was measured on 3,198 derivations at 3c56730a; this run has 3,509.

**DAN 52 → 57**, at `KXATPMATCH-26JUL18DANPRA-PRA.csv.gz#row-966`, ts **1784332873**, confirmed in the trace (ln64345, `REPRICE_REST → 57`, `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`). The repaired evidence object is the model the lock asks for:
```
conditioning_low_cents: 49          (was: observed_low_cents: 49)
observed_traded_low_cents: null
observed_book_path_low_cents: 49
book_path_low_source: { source: "BOOK_BID_ASK_MID_SERIES_FLOORED_NON_TRADE",
                        receipt: "…DANPRA-DAN.csv.gz#row-3", timestamp_epoch: 1784317958 }
```
The field that falsely claimed to be an observed low is **renamed**, the traded low is **explicitly null**, and the substitute names its own producing branch and receipt. That is F-VS-164/168 closed at the write site.

### The named bound at all six write sites — REPAIRED

`par_allocation_floor_bound` is emitted on **3,509 of 3,509** derivations:
```
name: "PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND"
value_cents · evidenced_floor_cents · source · source_receipt
never_above_evidenced_floor · role: "MAXIMUM_LAWFUL_REDUCTION_FLOOR_FOR_PAIR_PAR_ALLOCATION"
provenance: "F-VS-160/F-VS-169@a2a6a25d/44559ebc"
```
`source` = `OBSERVED_TRUE_TRADE_PRINT` 3,223 · `NO_TRADED_FLOOR_NO_REDUCTION_AUTHORITY` 286. `never_above_evidenced_floor` **true on 3,509/3,509, zero exceptions**. It is in the sentence (`PAR_ALLOCATION_FLOOR_BOUND=`, `PAR_ALLOCATION_HEADROOM_CENTS=`) and in the allocator's own result object (`os.js:381/392/393`). F-VS-169's nameless bound is closed.

And the bound is now the right number: `os.js:750 boundValue = Math.min(evidencedFloor, targetBeforeAllocation)` — headroom is measured against a **traded** floor, not an envelope low. That is the direct cause of the SVA capture in §3.

### The tenure table's zero-violation claim over ALL rows — TRUE, AND I CHECKED IT THE HARD WAY

The gate's population is filtered exactly as it was at 3c56730a (`build.js:1437`, rows where `active_was_at_evidenced_floor || protected_from_conflicting_belief_or_cancel`), which is the filter I refuted in F-VS-161 — the flag goes false at the moment a rest is abandoned. **So I did not accept it.** I recomputed over **all** 3,509 derivations: for every leg, every row whose *previous* row was at the evidenced floor and which then repriced or cancelled.

**Result: 0 such rows.** The population is 307 (matching `at_floor_receipts: 307`; my per-leg count BAR 161 + GIU 130 + URS 6 + PRA 10 = 307) and the wider test finds nothing either. **The claim holds on the merits, not by the filter.**

**But the metric is capture-blind, and that is the finding:**

| leg | level | rows | tenure start | qualifying floor print | prints ≤ level after tenure began |
|---|---:|---:|---:|---:|---:|
| BAR | 27 | 161 | 1783851325 | 1783841801.305 | **0** |
| GIU | 66 | 130 | 1783873944 | 1783869375.227 | **0** |
| URS | 58 | 6 | 1784031096 | 1784032697.601 | 1 → **filled** |
| PRA | 41 | 10 | 1784359766 | 1784342554.0 | 4 → **filled** |

**Two of the four episodes begin after the last qualifying print** — BAR by 9,523.7 s, GIU by 4,568.8 s. `AT_FLOOR_TENURE` scores BAR as holding its exact floor for **22,975 s** on a rest that could never fill. Tenure measures *whether* a rest sat at the floor, never *whether it sat there in time*.

### The 10 fail-capable gates — the claim is decided by a string comparison

`build.js:2226`:
```js
].map((check) => ({ ...check, can_fail: check.producer_store !== check.check_store,
                    passed: check.failures.length === 0 }));
```
`passed` **is** computed from `failures` — the contract's second half holds, and every typed pass-literal from F-VS-167 is gone. But **`can_fail` is `producer_store !== check_store`: a comparison of two strings typed in by the author at `:2216-2225`.** Any two distinct labels yield `can_fail: true`. `gate_fields_that_can_fail: 10` counts ten non-identical labels, not ten falsifiable checks.

My own adjudication, each against its predicate:

| check | verdict | why |
|---|---|---|
| `FLOOR_IS_OBSERVED_TRADE_LOW` | **GENUINELY INDEPENDENT** | `:2196-2203` recomputes the floor as `Math.min` over the materialized tape's PRINT prefix and compares to the emitted value. Different store, real arithmetic. The strongest check in the gate |
| `DETERMINISM_X2` | **GENUINELY INDEPENDENT** | two replays compared byte-for-byte |
| `CURRENT_BED_TRIPWIRE` | **PROVEN FAIL-CAPABLE** | it fired — GIUBAR and LAJSVA |
| `AT_FLOOR_TENURE` | holds, but see above | filtered population; I verified it independently and it survives |
| `NON_TRADED_LOW_DISCLOSED` | **SERIALIZATION ONLY** | selects rows by `non_traded_low_consumed === true`, then checks the sentence contains the disclosure substring. It verifies the template, not the value |
| `PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR` | **CANNOT FAIL** | tests `name !== "PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND"` (a literal the producer writes) **or** `value_cents > evidenced_floor_cents` — impossible, because `os.js:750` sets `value_cents = Math.min(evidencedFloor, target)` |
| `TARGET_AUTHORITY_ACTUAL` | **CANNOT FAIL** | `build.js:2204-2211` re-derives authority from `envelope_placement.mode`; `os.js:1044` **sets** authority from the same mode by the same mapping. The check recomputes the producer's own function |
| `RUN_SOURCE_EXPLICIT` | **CANNOT FAIL** | compares `run_source` against the same constants the producer wrote |
| `BASELINE_PINS` | **CANNOT FAIL** | compares a frozen lineage against expected deltas (3 and 6) typed into the predicate |
| `LAW_VIOLATIONS` | **PASSTHROUGH** | `observed: lawViolations, failures: lawViolations` — the same array in both fields. It fired, so it reports; it does not check |

**Four genuinely falsifiable, five that cannot fail as written, one passthrough.**

### Fills and determinism — CONFIRMED

**Five fills** (was four). All verified by `trade_id` in `fit-local/prints.jsonl`, all `true_print: true`, F-VS-107 holds on every one:

| leg | trade_id | entry | rest | print | epoch |
|---|---|---:|---:|---:|---|
| URS | `a4575e0c…` | 58 | 58 | 57 | 1784032697.600949 |
| PAL | `11b32855…` | 39 | 39 | 39 | 1784042066.596112 |
| **SVA** | `62c5acca…` | **41** | 41 | 41 | **1784020209.484174** |
| LAJ | `25f578e2…` | 54 | 54 | 54 | 1784036624.369515 |
| PRA | `6a5b1a68…` | 41 | 41 | 41 | 1784369249.287716 |

Determinism `V54_DEFINITION_REPAIR_DETERMINISM_X2`, `runs_per_game: 2`, `all_byte_identical: true` on all four games. Replay stability on one tape and one host — not cross-machine.

---

## 2 — Residual blockers, rows

### (a) `SINGLETON_SURVIVOR_ENVELOPE_NOT_CONSUMED` — 8 rows, one leg, the same condition as before

146 singleton rows, 138 consumed, **8 unconsumed — all URS, all level 58, ts 1784030027 → 1784030535, ask 58, `lawful_envelope_high` 57.**

**The condition that refuses a rest at a single-level conviction is unchanged: the post-only guard.** `singleton ≤ min(envelope.high, liveAsk − 1)`; with the singleton at 58 and the ask at 58 the bound is 57, so 58 is not postable as a maker bid and the target falls to null. That is lawful (F-VS-156) — a bid at the ask is a taker.

What changed is *when*: the cancel now lands at **ln1579 ts 1784030027**, the receipt at which 3c56730a still held 57 and only cancelled 261 s later. URS re-places 58 at ln1587 ts 1784031046 and fills at 58; its at-floor tenure is recorded from 1784031096. The lost cent is the envelope narrowing [57,58] → [58,58], not the bound — as corrected in F-VS-160(c). One new honest field: the cancel now carries `no_lawful_replacement_reason: ENVELOPE_POINT_AT_OR_ABOVE_LIVE_ASK`, which names the condition instead of hiding it.

### (b) `FAIL_LOUD_CANCEL_WITHOUT_REARM_STATE` — the crossed-book route is gone; a new one opened

20 cancels, **18 armed, 2 un-armed**:

| ln | leg | ts | book | `no_lawful_replacement_reason` | action reason |
|---|---|---:|---|---|---|
| 64202 | LAJ | 1784020205 | bid 56 / ask 58 — **uncrossed** | **null** | `LAYERED_COHERENT_ENVELOPE_Q75_INSIDE_SPREAD_REACH` |
| 64350 | PRA | 1784341326 | bid 40 / ask 41 — **uncrossed** | **null** | `LAYERED_COHERENT_ENVELOPE_Q75_INSIDE_SPREAD_REACH` |

**The permitting predicate is `os.js` arming branch `if (action.action === "CANCEL_REST" && noLawfulReplacement)`.** Both rows miss it because `noLawfulReplacement` is **false**: these are not fail-loud cancels at all. The coherent Q75 lane nulled the target for its own reasons and the cancel executed outside the arming path entirely. At 3c56730a the single un-armed cancel was a crossed book (DAN, bid 60 / ask 59); that route is closed and **a wider one is open — an ordinary coherent-lane cancel on a normal book.**

**And it cost the early fill.** PRA cancelled 41 at **1784341326**, **1,227.97 s before** the first 41 print at 1784342553.971, with no rearm state, and did not re-place until 1784347255 (at 40). It reached 41 again only at 1784359388 and filled at **1784369249.287** — the same price **26,695 s later than the prior build's PRA fill**. Two qualifying prints (1784342553.971 and 1784342806.09) passed while PRA had no rest.

---

## 3 — The remaining cents, two-way attributed

### LAJSVA — Δ5 achieved, Δ6 was 16,206 s away

LAJ 54 + SVA 41 = **95 → Δ5**. The frozen lineage pin is Δ6 (sum 94).

**SVA is a genuine capture and the repair caused it.** SVA reaches 41 at ln64203 **ts 1784020209** on the coherent lane and fills at **1784020209.484174** — 0.484 s later. At 3c56730a SVA reached 41 at 1784020212, **2.516 s after** the last 41 print, because `allocateUnderPar` had capped it at 40: LAJ's headroom was `59 − 59 = 0` measured against LAJ's **envelope low**. With the bound now `min(observed traded floor, target)`, LAJ has headroom and SVA is not forced to absorb the cent. **F-VS-160(b) is closed by the named bound.**

**The missing cent is LAJ, and it is a speed/price trade, not a defect.** LAJ filled at 54 on the first ≤54 print, 1784036624.370. Its first ≤53 print is **1784052830.356 — 16,206 s later**. A 53 rest scores Δ6 and waits 4.5 hours longer into the bell. LAJ never rested below 54 (it alternated 54/55 eight times on the DISAGREES lane); its floor is 51.
**Attribution: DATA-UNCONSUMED, weakly.** LAJ's own criterion admitted 53 and no row proposed it — but the input that would license waiting (the distribution of remaining time to a ≤53 print) is not in any store. The cent is real; calling it a miss would require evidence the build does not hold.

### GIUBAR — both legs unchanged, both attributed MISREAD

| leg | lifecycle | the decisive row |
|---|---|---|
| **BAR** | 29 → 26 → 25 → 26 → **27 @1783851291**, then 22,975 s at 27 | **ln46 @1783841772, REPRICE 29 → 26**, live bid 26, `OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED`, **29.305 s before** the only 27 print. Identical to 3c56730a and to 680e995c |
| **GIU** | 63 → 64 → 67 → 68 → 67 → **66 @1783867224** → **65 @1783867786** → 66 @1783873872 | **ln82 @1783867786, REPRICE 66 → 65**, live bid 65, same lane, **1,589.2 s before** the first 66 print. All three 66 prints land while GIU rests at 65; it returns to 66 **1,261.2 s after the last one** |

**The floor repair does not reach either leg**, because on both decisive rows `evidenced_floor_cents` is **null** — no true trade had printed yet, so there is no observed traded floor to bound anything. The DISAGREES bid-follower is unsupervised in exactly that window, as I filed in F-VS-154(ii).
**Attribution: MISREAD on both.** Nothing was missing — the leg's own standing rest was fillable and its own rule moved it to the live bid. BAR's is the sharper case: it left a fillable 29 twenty-nine seconds before the print and then held the exact floor, unfillable, for six and a half hours.

### DANPRA — the second leg, and the axis still cannot name 59

DAN: 52 → **57 @1784332873** → **58 @1784336963.017**. 58 is the shallowest level the ATP_MAIN survivor library can express (`anchor 58 − depth 0`); **DAN's floor is 59, above its anchor, and no shape carries a negative depth bin.** The repair moved DAN 6¢ closer and stopped exactly where the library ends.
**Attribution: DATA-GAP, unchanged.** The evidence that would license 59 exists in no store the machine holds.

And it would not have mattered: **DAN 59 + PRA 41 = 100 against par 99 — `strictly_under_par_offer_cents: 0`.** No under-par completion existed on DANPRA at any price. The 57 does not help and could not.
PRA is the leg with a real loss, and it is §2(b): an un-armed cancel 1,227.97 s before its floor print, costing 26,695 s of exposure at the same entry. **Attribution: MISREAD** — the rest was standing at the right price and the coherent lane cancelled it outside the arming path.

---

## 4 — Collision re-sweep

**(a) No value stamped as observed still originates from a belief on the decision path — CONFIRMED, with one carve-out.**
`evidenced_floor_source` is `OBSERVED_TRUE_TRADE_PRINT` or null; the envelope-low source is gone. `own_evidence` no longer calls a book-path number an observed low — it is `conditioning_low_cents`, with `observed_traded_low_cents: null` and a named `book_path_low_source`. `target_authority` now varies with the lane (`CONDITIONED_Q75_RECONCILED_TO_SURVIVOR_TRADED_LOW_SUPPORT` 2,724 · `LIVE_TOUCH` 441 · `OWN_EVIDENCE_WITH_SURVIVOR_SUPPORT` 332 · `OBSERVED_TRUE_TRADE_FLOOR_TENURE` 12) instead of the constant `EVIDENCED_TOUCH` on 3,198/3,198 — F-VS-165 closed. `par_allocation_floor_bound` is bounded by the traded floor on every row.
**The carve-out:** `predicted_cents` is still `conditioning_low_cents + library offset`, and on the 286 non-trade rows that low is a mid-quote. It is now *disclosed*, and it no longer names itself observed — but it still prices `envelope.low_cents` through `supportedFloorLevel`. Disclosed, not removed.

**(b) New self-agreeing checks WERE introduced — three of them.**
- **`can_fail = producer_store !== check_store`** (`build.js:2226`) — a string comparison standing in for a proof of falsifiability, and it is the field that certifies the honesty of the other nine.
- **`TARGET_AUTHORITY_ACTUAL`** — the check re-derives the producer's own mode→authority mapping (`build.js:2204-2211` vs `os.js:1044`).
- **`PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR`** — its inequality is made impossible by the `Math.min` at `os.js:750`.

Against that, the build genuinely removed all 17 typed pass-literals, and `FLOOR_IS_OBSERVED_TRADE_LOW` is the first check in this system's history that recomputes a policy number from a separate store and compares. That is the pattern the lock asked for, and it should be the template for the other nine.

---

## 5 — The new defect this build introduced: order thrash

Orders went **60 → 309** (PLACE 28 · REPRICE **261** · CANCEL 20). PAL alone accounts for **224**.

**Two lanes now fight inside a single receipt.** At ts 1784024516 PAL takes three orders (REPRICE 31, REPRICE 32, REPRICE 39); the pattern — DISAGREES drags the rest down to the live bid, the coherent lane pulls it back to 39 — repeats through 1784025000–1784025300 dozens of times. **62 (leg, timestamp) pairs carry more than one order, and the maximum at a single instant is 10.** PAL's direction census is 143 up / 76 down.

No prior build did this: 3c56730a had 60 orders and no repeated same-timestamp actions. The floor and bound repairs are sound; the oscillation is a consequence of both lanes now being able to act on the same receipt without a precedence rule between them.

---

## Verdict

CERTIFIED: floor has one producer and a print receipt on every row; the belief fallback is gone (0 of 3,509); the 286 non-trade rows are disclosed in the field and in the sentence; 201 changed orders and 151 changed targets reproduce, DAN 52→57 confirmed at `…PRA.csv.gz#row-966`; the named bound is emitted on 3,509/3,509 and never above the traded floor; the tenure claim holds over ALL rows, not just its filtered 307; five fills verified by trade_id with F-VS-107 clean; determinism byte-identical ×2; all typed pass-literals removed; **SVA's 41 captured, closing F-VS-160(b)**.

FAULTED: (i) `can_fail` is a string comparison, and on the predicates themselves only four of ten checks are falsifiable; (ii) `TARGET_AUTHORITY_ACTUAL` and `PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR` are new self-agreeing checks; (iii) tenure is capture-blind — BAR scores 22,975 s at its exact floor on a rest that could never fill; (iv) the un-armed-cancel route widened from a crossed book to an ordinary coherent-lane cancel, and it cost PRA 26,695 s; (v) GIUBAR is unchanged on both legs because the repaired floor is null on the rows that matter; (vi) orders went 60 → 309 with up to 10 at one instant.
